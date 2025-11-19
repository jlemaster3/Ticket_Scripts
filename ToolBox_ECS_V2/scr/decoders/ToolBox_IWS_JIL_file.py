#-------------------------------------------------
#   Imports
#-------------------------------------------------
import threading, copy, re
import numpy as np
from typing import Any, Dict, List, Optional, Union, Hashable

from ...ToolBox_Logger import OutputLogger
from ..ToolBox_Data_Silo import ToolBox_Data_Silo_Manager
from ..shared_utils.ToolBox_Filters import *
from ..shared_utils.ToolBox_Enums import (
    ToolBox_Amount_Options,
    ToolBox_Entity_Types,
    ToolBox_REGEX_Patterns
)
from ..shared_utils.ToolBox_Utils import (
    gen_uuid_key
)

#-------------------------------------------------
#   Decorator Functions / Wrappers
#-------------------------------------------------

def ToolBox_Decorator(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        return result
    return wrapper

#-------------------------------------------------
#   classes
#-------------------------------------------------

class text_score_evaluator:

    #------- public properties -------#
    log:OutputLogger = OutputLogger().get_instance()
    
    #------- private properties -------#
    _line_index:int
    _text:str
    _flags:list[re.RegexFlag]
    _results:dict[str,list[tuple[int, re.Match]]]
    _filter_AnyOrAll:ToolBox_Amount_Options|str|None
    _filter_patterns:list[str]|None
    _bonus_score:int|None

    #------- Initialize class -------#

    def __init__ (self, 
        text:str, 
        line_index:int,
        filter_patterns:list[str]|None = None,
        filter_AnyOrAll:ToolBox_Amount_Options|str|None = None,
        flags:list[re.RegexFlag]|None = None,
        bonus_score:int|None = None
    ):
        self._text = text
        self._line_index = line_index
        self._flags = flags or [re.IGNORECASE]
        if any(_p in text for _p in ['\n', '\r']) and re.MULTILINE not in self._flags:
            self._flags.append(re.MULTILINE)
        self._filter_patterns = filter_patterns
        try:
            self._filter_AnyOrAll = filter_AnyOrAll if (
                (filter_AnyOrAll is not None) and 
                    (isinstance(filter_AnyOrAll, ToolBox_Amount_Options) or 
                        (isinstance(filter_AnyOrAll,str) and 
                            filter_AnyOrAll in ToolBox_Amount_Options
                        )
                    )
                ) else ToolBox_Amount_Options.ANY
        except:
            self._filter_AnyOrAll = ToolBox_Amount_Options.ANY
        self._bonus_score = bonus_score
        self.evaluate_text()

    #-------public Getter & Setter methods -------#

    @property
    def line_index(self) -> int:
        return self._line_index
    
    @property
    def text(self) -> str:
        return self._text
    
    @text.setter
    def text(self, value: str):
        self._text = value


    @property
    def found_pattern_names (self) -> list[str]:
        """Returns the list of all found pattern names in line score"""
        return [_n for _n in self._results.keys()] if self._results is not None else []
    
    @property
    def get_highest_scoreing_pattern_names (self) -> list[str]:
        """Returns the list of highest scoring pattern names in line score"""
        _highest_score:int = 0
        _highest_names:list[str] = []
        for _p_name, _p_results in self._results.items():
            _max_score = max([_r[0] for _r in _p_results]) if len(_p_results) > 0 else 0
            if _max_score > _highest_score:
                _highest_score = _max_score
                _highest_names = [_p_name]
            elif _max_score == _highest_score:
                _highest_names.append(_p_name)
        return _highest_names
    
    @property
    def all_results(self) -> dict[str,list[tuple[int, dict[str,Any]]]]:
        """Returns a collection of all results with their scores and match details."""
        _results:dict[str,list[tuple[int, dict[str,Any]]]] = {}
        for _pattern_name, _pattern_results in self._results.items():
            _results[_pattern_name] = [(_score, _match.groupdict()) for _score, _match in _pattern_results]
        return _results
    
    #------- Methods / Functions -------#

    @ToolBox_Decorator
    def evaluate_text (self):
        """Evaluates the text against all regex patterns and scores them."""
        _flag_val = sum(self._flags)
        self._results = {}
        for _pattern_name, _pattern in ToolBox_REGEX_Patterns.__members__.items():
            _results = re.finditer(_pattern, self._text, _flag_val)
            if _results is not None:
                _score:int = 0 if (self._bonus_score is None) else self._bonus_score
                _pattern_name_parts = _pattern_name.split('_')
                if ((self._filter_patterns is not None) and 
                    (self._filter_AnyOrAll == ToolBox_Amount_Options.ALL) and 
                    not (all([_f.upper() in _pattern_name.upper() for _f in self._filter_patterns]))
                ):
                    for _f in self._filter_patterns:
                        if re.search(rf"(?:\b|_){_f}(?:\b|_)", _pattern_name, re.IGNORECASE):
                            _score += 20
                elif ((self._filter_patterns is not None) and 
                    (self._filter_AnyOrAll == ToolBox_Amount_Options.ANY)
                ):
                    for _f in self._filter_patterns:
                        if re.search(rf"(?:\b|_){_f}(?:\b|_)", _pattern_name, re.IGNORECASE):
                            _score += 15
                if(self._filter_patterns is not None):
                    _score -= 5 *len([_pn_w for _pn_w in _pattern_name_parts if all([_pn_w.upper() != _f for _f in self._filter_patterns])])
                if 'note' in _pattern_name.lower():
                    _score += 20
                for _r in _results:
                    if isinstance(_r, re.Match):
                        _nonNone_groups = [_grp_v for _grp_v in _r.groupdict().values() if _grp_v is not None and _grp_v.strip() != '']
                        _None_groups = [_grp_v for _grp_v in _r.groupdict().values() if _grp_v is None or _grp_v.strip() == '']
                        _reults_len:int = len(_r.groupdict().keys())
                        if len(_nonNone_groups) >= 1:
                            _score += 5 * abs(_reults_len-len(_nonNone_groups))
                        if len(_None_groups) >= 1:
                            _score -= 5 * abs(len(_None_groups) - _reults_len)
                        _score += 5 * _reults_len
                        if _pattern_name not in self._results.keys():
                            self._results[_pattern_name] = []
                        self._results[_pattern_name].append((_score, _r))

    @ToolBox_Decorator
    def get_results_for_pattern(self, pattern_name: str) -> list[dict[str,Any]]:
        """Returns a list of dictionaries containing the match details for a given pattern name."""
        _results = [_r[1].groupdict() for _r in self._results.get(pattern_name, [])]
        return _results

        



class ToolBox_IWS_JIL_File_Manager :
    """Object class that handles Jil files."""   
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    datasilo: ToolBox_Data_Silo_Manager = ToolBox_Data_Silo_Manager.get_instance()

    #------- private properties -------#
    _lock = threading.Lock()
    _instance = None

    #------- Initialize class -------#
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> "ToolBox_IWS_JIL_File_Manager":
        """Returns the singleton instance of ToolBox_IWS_JIL_File_Manager, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    #-------public Getter & Setter methods -------#
    
    @property
    def file_keys(self) -> list[str]:
        return self.datasilo.get_entity_keys_by_component_value('object_type', ToolBox_Entity_Types.FILE_JIL)
    
    #------- Methods / Functions -------#

    @ToolBox_Decorator
    def load_files(self, quite_logging:bool=True, enable_post_porcesses:bool=True, **component_filters):
        """Loads file entities into their respective objects based on entity type."""
        if len(self.file_keys) == 0:
            self.log.info("No JIL files found in collection to load.")
            return
        _key_list = self.datasilo.get_entity_keys_by_component_value('object_type', ToolBox_Entity_Types.FILE_JIL, **component_filters) if component_filters is not None and len(component_filters) > 0 else self.file_keys
        _e_counter_size = len(str(len(_key_list)))
        for _e_counter, _e_key in enumerate(_key_list):
            _e_data:dict[str,Any] = self.datasilo.get_entity(_e_key)
            _file_full_path = _e_data.get('full_path','')
            try:
                _holder = None
                with open(_file_full_path, "r", encoding="utf-8") as f:
                    _holder = copy.deepcopy(f.read())
                if (_holder is not None):
                    if (quite_logging != True) : self.log.info(f"[{str(_e_counter+1).rjust(_e_counter_size, '0')}] Loaded IWS JIL file : '{_file_full_path}'")
                    self.datasilo.add_component(_e_key, 'file_text', _holder)
                else:
                    self.log.error (f"Unable to read file contents : '{_file_full_path}'")
            except BufferError as errmsg:
                self.log.error (f"Unable to open file : '{_file_full_path}'", data = errmsg)
            except FileNotFoundError as errmsg:
                self.log.error (f"File not found : '{_file_full_path}'", data = errmsg)
            except Exception as e:
                self.log.error(f"An unexpected error occurred while reading '{_file_full_path}'", data = e)
        if (enable_post_porcesses == True):
            self.extract_IWS_streams()

    @ToolBox_Decorator
    def extract_IWS_streams(self, **component_filters):
        """Extracts the Job Stream entities from the loaded JIL File data"""
        _key_list = self.datasilo.get_entity_keys_by_component_value('object_type', ToolBox_Entity_Types.FILE_JIL, **component_filters) if component_filters is not None and len(component_filters) > 0 else self.file_keys
        _curr_file_e_key:str|None = None
        _curr_stream_key:str|None = None
        _last_stream_key:str|None = None
        _curr_job_key:str|None = None
        _last_job_key:str|None = None
        _note_line_holder:list[str]|None = None
        
        def _clean_data(data: dict[str, Any]) -> dict[str, Any]:
            _cleaded_data:dict[str, Any] = {}
            for _k, _v in data.items():
                match _v:
                    case list():
                        if len(_v) >= 1:
                            _cleaded_data[_k] = _v
                    case dict():
                        if len(_v.keys()) >= 1:
                            _cleaded_data[_k] = _v
                    case str():
                        if _v.strip() != '':
                            _cleaded_data[_k] = _v
                    case _:
                        if _v is not None and (not (isinstance(_v, float) and np.isnan(_v))):
                            _cleaded_data[_k] = _v
            return _cleaded_data
        
        def _create_entity_from_line (key_id:str, data:dict[str,Any]) -> str:
            nonlocal _curr_file_e_key
            if _curr_file_e_key is not None and 'source_file_key' not in data.keys():
                data['source_file_key'] = _curr_file_e_key
            _data = _clean_data(data)
            if self.datasilo.entity_exists(key_id):
                self.datasilo.update_entity_components(key_id, _data)
                return key_id
            else:
                _entity_key = self.datasilo.create_entity(
                    key_id=key_id,
                    components=_data
                )
            return _entity_key
        
        _stream_in_file = 0
        _job_in_file = 0
        _job_in_stream = 0
        for _e_counter, _e_key in enumerate(_key_list):
            _e_str_rows = self.datasilo.get_component(_e_key, 'file_text', '').splitlines()
            if len(_e_str_rows) > 0:
                _update_substep:float = 1.0
                _udpate_percent:float = max(1.0, int(len(_e_str_rows) * (_update_substep/100)))
                _max_percent:float = 2.0
                _show_steps:bool = True if len(_e_str_rows) >= 10000 else False
                _curr_file_e_key = _e_key
                if _show_steps == True:
                    self.log.info(f"sub step debug enabled for upto [{int((_max_percent*len(_e_str_rows))/100)}] lines out of a total of [{len(_e_str_rows)}] lines, debug steps every [{_update_substep}%] stopping after [{_max_percent}%]")
                for _line_idx, _line_str in enumerate(_e_str_rows):
                    if _show_steps == True and _line_idx % _udpate_percent == 0:
                        if (_line_idx/len(_e_str_rows))*100 >= _max_percent:
                            break
                        self.log.debug(f"Line : [{_line_idx}] {round((_line_idx/len(_e_str_rows))*100, 2)}% | Job Stream Count: [{len(self.datasilo.get_entity_keys_by_component_value(component='object_type', value=ToolBox_Entity_Types.IWS_JOB_STREAM))}] |  Job Count: [{len(self.datasilo.get_entity_keys_by_component_value(component='object_type', value=ToolBox_Entity_Types.IWS_JOB))}]")
                    _evaluator = text_score_evaluator(
                        text=_line_str,
                        line_index=_line_idx,
                        filter_patterns=['IWS', 'JOB', 'STREAM', 'LINE'],
                        filter_AnyOrAll=ToolBox_Amount_Options.ANY,
                        bonus_score=0
                    )
                    if ToolBox_REGEX_Patterns.NOTE_LINE.name.upper() in _evaluator.get_highest_scoreing_pattern_names:
                        if _note_line_holder is None:
                            _note_line_holder = []
                        _note_line_holder.append(_line_str)
                        continue
                    if ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE.name.upper() in _evaluator.get_highest_scoreing_pattern_names:
                        if _curr_stream_key is not None and _curr_stream_key != _last_stream_key:
                            _last_stream_key = _curr_stream_key
                        _stream_results = _evaluator.get_results_for_pattern(ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE.name.upper())[0]
                        _stream_results['object_type'] = ToolBox_Entity_Types.IWS_JOB_STREAM
                        _uuid_string = f"{self.datasilo.get_component(_e_key, 'full_path','')}|{_stream_results.get('workstation','')}{_stream_results.get('folder','')}{_stream_results.get('stream', '')}.@"
                        _stream_results['name'] = _stream_results['stream']
                        del _stream_results['stream']
                        _stream_in_file += 1
                        _stream_results['stream_index_in_file'] = _stream_in_file
                        if _note_line_holder is not None:
                            _stream_results['pre_notes'] = '\n'.join(_note_line_holder)
                            _note_line_holder = None
                        _curr_stream_key = _create_entity_from_line(key_id=gen_uuid_key(_uuid_string), data = _stream_results)
                        self.datasilo.add_component(_curr_stream_key, 'job_keys', [])
                        continue
                    if ToolBox_REGEX_Patterns.IWS_ONOVERLAP_LINE.name.upper() in _evaluator.get_highest_scoreing_pattern_names:
                        if _curr_stream_key is not None:
                            _onoverlap_data = _evaluator.get_results_for_pattern(ToolBox_REGEX_Patterns.IWS_ONOVERLAP_LINE.name.upper())[0]
                            if _onoverlap_data is not None and len(_onoverlap_data) >= 1:
                                self.datasilo.add_component(_curr_stream_key, 'onoverlap', _onoverlap_data['onoverlap'])
                        continue
                    if ToolBox_REGEX_Patterns.IWS_MATCHING_LINE.name.upper() in _evaluator.get_highest_scoreing_pattern_names:
                        if _curr_stream_key is not None:
                            _matching_data = _evaluator.get_results_for_pattern(ToolBox_REGEX_Patterns.IWS_MATCHING_LINE.name.upper())[0]
                            if _matching_data is not None and len(_matching_data) >= 1:
                                self.datasilo.add_component(_curr_stream_key, 'matching', _matching_data['matching'])
                        continue
                    if ToolBox_REGEX_Patterns.IWS_STREAM_EDGE_LINE.name.upper() in _evaluator.get_highest_scoreing_pattern_names:
                        if _curr_stream_key is not None and _note_line_holder is not None and len(_note_line_holder)>=1:
                            self.datasilo.add_component(_curr_stream_key, 'post_notes', '\n'.join(_note_line_holder))
                            _note_line_holder = None
                        continue
                    if ToolBox_REGEX_Patterns.IWS_JOB_START_LINE.name.upper() in _evaluator.get_highest_scoreing_pattern_names:
                        if _curr_job_key is not None and _curr_job_key != _last_job_key:
                            _last_job_key = _curr_job_key
                        _job_results = _evaluator.get_results_for_pattern(ToolBox_REGEX_Patterns.IWS_JOB_START_LINE.name.upper())[0]
                        _job_results['object_type'] = ToolBox_Entity_Types.IWS_JOB
                        
                        _uuid_string = f"{self.datasilo.get_component(_e_key, 'full_path','')}|{_job_results.get('workstation','')}{_job_results.get('folder','')}"
                        if _curr_stream_key is not None:
                            _parent_job_name = self.datasilo.get_component(_curr_stream_key, 'name', None)
                            if _parent_job_name is not None:
                                _uuid_string += f"{_parent_job_name}."
                        if 'alias' in _job_results.keys() and _job_results['alias'] is not None and _job_results['alias'].strip() != '':
                            _job_results['is_instance'] = True
                            #_job_results['instance_source_key'] = gen_uuid_key(f"{_job_results.get('job','')}")
                            _uuid_string += f"{_job_results['alias']}"
                        else:
                            _uuid_string += f"{_job_results.get('job','')}"
                        _job_results['name'] = _job_results['job']
                        del _job_results['job']
                        _job_in_file += 1
                        _job_results['job_index_in_file'] = _job_in_file
                        if _note_line_holder is not None:
                            _job_results['pre_notes'] = '\n'.join(_note_line_holder)
                            _note_line_holder = None
                        _curr_job_key = _create_entity_from_line(key_id=gen_uuid_key(_uuid_string), data = _job_results)
                        if _curr_stream_key is not None:
                            self.datasilo.add_component(_curr_job_key, 'parent_stream_key', _curr_stream_key)
                            _job_in_stream += 1
                            self.datasilo.add_component(_curr_job_key, 'job_index_in_stream', _job_in_stream)
                            if (self.datasilo.entity_has_component(_curr_stream_key, 'job_keys')):
                                _stream_job_keys_raw = self.datasilo.get_component(_curr_stream_key, 'job_keys', [])
                                _stream_job_keys: list[str] = _stream_job_keys_raw if isinstance(_stream_job_keys_raw, list) else [str(_stream_job_keys_raw)]
                                if _curr_job_key not in _stream_job_keys:
                                    _stream_job_keys.append(_curr_job_key)
                                    self.datasilo.add_component(_curr_stream_key, 'job_keys', _stream_job_keys)
                            else:
                                self.datasilo.add_component(_curr_stream_key, 'job_keys', [_curr_job_key])
                        continue
                    if ToolBox_REGEX_Patterns.IWS_DESCRIPTION_LINE.name.upper() in _evaluator.get_highest_scoreing_pattern_names:
                        _description_data = _evaluator.get_results_for_pattern(ToolBox_REGEX_Patterns.IWS_DESCRIPTION_LINE.name.upper())[0]
                        if _curr_job_key is not None:
                            self.datasilo.add_component(_curr_job_key, 'description', _description_data['description'])
                        elif _curr_stream_key is not None:
                            self.datasilo.add_component(_curr_stream_key, 'description', _description_data['description'])
                        continue
                    if ToolBox_REGEX_Patterns.IWS_PRIORITY_LINE.name.upper() in _evaluator.get_highest_scoreing_pattern_names:
                        _priority_data = _evaluator.get_results_for_pattern(ToolBox_REGEX_Patterns.IWS_PRIORITY_LINE.name.upper())[0]
                        if _curr_job_key is not None:
                            self.datasilo.add_component(_curr_job_key, 'priority', int(_priority_data['priority']))
                        elif _curr_stream_key is not None:
                            self.datasilo.add_component(_curr_stream_key, 'priority', int(_priority_data['priority']))
                        continue
                    if ToolBox_REGEX_Patterns.BLANK_LINE.name.upper() in _evaluator.get_highest_scoreing_pattern_names:
                        if _curr_job_key is not None:
                            _last_job_key = _curr_job_key
                            _curr_job_key = None
                        continue    
                    if ToolBox_REGEX_Patterns.IWS_STREAM_END_LINE.name.upper() in _evaluator.get_highest_scoreing_pattern_names:
                        _last_stream_key = _curr_stream_key
                        _curr_stream_key = None
                        if _last_job_key is not None and _note_line_holder is not None and len(_note_line_holder) >= 1:
                            self.datasilo.add_component(_last_job_key, 'post_notes', '\n'.join(_note_line_holder))
                            _note_line_holder = None
                        _job_in_stream = 0
                        continue
                if _note_line_holder is not None and len(_note_line_holder) >= 1:
                    if _last_stream_key is not None:
                        self.datasilo.add_component(_last_stream_key, 'post_notes', '\n'.join(_note_line_holder))
                        _note_line_holder = None
            else:
                self.log.warning(f"No lines found in JIL file: '{_e_key}'")