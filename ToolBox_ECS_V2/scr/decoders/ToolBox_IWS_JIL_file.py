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
    gen_uuid_key,
    ToolBox_REGEX_score_evaluator
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
    def save_files(self, outputFolder:str|None=None, useRelPath:bool=False, quite_logging:bool=True, **component_filters):
        """Saves file entities from their respective objects based on entity type."""
        if len(self.file_keys) == 0:
            self.log.info("No JIL files found in collection to save.")
            return
        _key_list = self.datasilo.get_entity_keys_by_component_value('object_type', ToolBox_Entity_Types.FILE_JIL, **component_filters) if component_filters is not None and len(component_filters) > 0 else self.file_keys
        print (f"Saving {len(_key_list)} JIL files...")
        _e_counter_size = len(str(len(_key_list)))

        for _e_counter, _e_key in enumerate(_key_list):
            _e_data:dict[str,Any] = self.datasilo.get_entity(_e_key)
            _outputPath:str|None = outputFolder if outputFolder is not None else _e_data.get('full_path',None)
            if useRelPath == True and isinstance(_outputPath, str):
                _rel_path = _e_data.get('file_path',None)
                if isinstance(_rel_path, str):
                    _outputPath = os.path.join(_outputPath, _rel_path)
                os.makedirs(_outputPath, exist_ok=True)
            _file_name = f"{_e_data.get('file_name', None)}{_e_data.get('file_format', None)}"
            if isinstance(_outputPath, str) and isinstance(_file_name, str):
                _file_full_path = os.path.join(_outputPath, _file_name)
                try:
                    _file_text = self.datasilo.get_component(_e_key, 'file_text', '')
                    with open(_file_full_path, "w", encoding="utf-8") as f:
                        f.write(_file_text)
                    if (quite_logging != True) : self.log.info(f"[{str(_e_counter+1).rjust(_e_counter_size, '0')}] Saved IWS JIL file : '{_file_full_path}'")
                except Exception as e:
                    self.log.error(f"An unexpected error occurred while saving '{_file_full_path}'", data = e)

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
                    _evaluator = ToolBox_REGEX_score_evaluator(
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