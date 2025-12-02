#-------------------------------------------------
#   Imports
#-------------------------------------------------
from ast import pattern
import threading, re, copy
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
    ToolBox_identify_date_parts,
    ToolBox_REGEX_score_evaluator
)
from .ToolBox_CSV_file import ToolBox_CSV_File_Manager

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

class ToolBox_IWS_text_file_manager :
    """Object class that handles *.josn Config files."""   
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    datasilo: ToolBox_Data_Silo_Manager = ToolBox_Data_Silo_Manager.get_instance()
    csv_manager: ToolBox_CSV_File_Manager = ToolBox_CSV_File_Manager.get_instance()
    
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
    def get_instance(cls) -> "ToolBox_IWS_text_file_manager":
        """Returns the singleton instance of ToolBox_IWS_text_file_manager, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    #-------public Getter & Setter methods -------#

    @property
    def file_keys(self) -> list[str]:
        return self.datasilo.get_entity_keys_by_component_value('object_type', ToolBox_Entity_Types.FILE_TXT)
    
    #------- Methods / Functions -------#
    
    @ToolBox_Decorator
    def load_files(self, quite_logging:bool=True, enable_post_porcesses:bool=True, **component_filters):
        """Loads file entities into their respective objects based on entity type."""
        if len(self.file_keys) == 0:
            self.log.info("No text files found in collection to load.")
            return
        _key_list = self.datasilo.get_entity_keys_by_component_value('object_type', ToolBox_Entity_Types.FILE_TXT, **component_filters) if component_filters is not None and len(component_filters) > 0 else self.file_keys
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
            pass
    
    @ToolBox_Decorator
    def decode_IWS_calendar_text(self, **component_filters):
        _key_list = self.datasilo.get_entity_keys_by_component_value('object_type', ToolBox_Entity_Types.FILE_TXT, **component_filters) if component_filters is not None and len(component_filters) > 0 else self.file_keys

        _calendar_name_pattern = r'^(?P<folder>[^\s]*(?:[^\s]*)*\/)*(?P<calendar>[^\s.*?\.]*)\b'

        for _e_counter, _e_key in enumerate(_key_list):
            _e_str = self.datasilo.get_component(_e_key, 'file_text', '')
            _calendar_match = re.match(ToolBox_REGEX_Patterns.IWS_CALENDAR_DECORATOR_LINE, _e_str)
            if _calendar_match is not None and isinstance(_e_str, str):
                _e_str_rows = _e_str.splitlines()
                _curr_calendar_key:str|None = None
                for _line_coutner, _line_str in enumerate(_e_str_rows):
                    if _line_coutner == 0 : continue
                    _cal_path_names = re.search(_calendar_name_pattern, _line_str)
                    if _cal_path_names is not None:
                        _cal_component = {
                            "source_file_key" : _e_key,
                            "folder" : _cal_path_names.group('folder'),
                            "name": _cal_path_names.group('calendar'),
                            "object_type": ToolBox_Entity_Types.IWS_CALENDAR,
                            'dates' : []
                        }
                        _curr_calendar_key = self.datasilo.create_entity(gen_uuid_key(f"{_cal_component['folder']}{_cal_component['name']}"), _cal_component)
                        continue
                    _cal_description = re.search(ToolBox_REGEX_Patterns.IWS_DESCRIPTION_LINE, _line_str)
                    if _cal_description is not None and _curr_calendar_key is not None:
                        self.datasilo.add_component(_curr_calendar_key, 'description', _cal_description.group('description'))
                        continue
                    _cal_dates = re.finditer(ToolBox_REGEX_Patterns.MONTH_DAY_YEAR_PART, _line_str)
                    if _cal_dates is not None and _curr_calendar_key is not None:
                        _curr_cal_dates:list[Any] = self.datasilo.get_component(_curr_calendar_key, 'dates', None)
                        for _line_date_coutner, _line_date_match in enumerate(_cal_dates):
                            try:
                                _date = datetime(
                                    year=int(_line_date_match.group('year')), 
                                    month=int(_line_date_match.group('month')), 
                                    day=int(_line_date_match.group('day')),
                                    hour=0,
                                    minute=0,
                                    second=0
                                ).strftime('%Y-%m-%d')
                                if _date not in _curr_cal_dates:
                                    _curr_cal_dates.append(_date)
                            except Exception as e:
                                self.log.error(f"Error parsing date: {e}", data=_line_str)
                        self.datasilo.update_component(_curr_calendar_key, 'dates', _curr_cal_dates)
                        continue
    
    @ToolBox_Decorator
    def decode_IWS_RCG_text(self, **component_filters):
        """Decodes IWS RCG text files into RCG entities."""
        _key_list = self.datasilo.get_entity_keys_by_component_value('object_type', ToolBox_Entity_Types.IWS_RUNCYCLEGROUP, **component_filters) if component_filters is not None and len(component_filters) > 0 else self.file_keys
        for _f_counter, _f_key in enumerate(_key_list):
            _f_text = self.datasilo.get_component(_f_key, 'file_text', '')
            _search_complie = re.compile(pattern=ToolBox_REGEX_Patterns.IWS_RUNCYCLEGROUP_PART,flags=re.IGNORECASE|re.MULTILINE)
            _searh_results = re.finditer(_search_complie, _f_text)
            if _searh_results is not None:
                _last_rcg_key:str|None = None
                _curr_rcg_key:str|None = None
                _curr_rcg_data:dict|None = None
                _new_line_coutner:int = 0
                _rcg_in_file:int = 0
                for _rslt_cnt, _result in enumerate(_searh_results):
                    _new_line_coutner += _f_text[:_result.start()].count('\n')
                    if _curr_rcg_key is not None:
                        _last_rcg_key = _curr_rcg_key
                        _curr_rcg_key = None
                        _curr_rcg_data = None
                    _rcg_in_file += 1
                    _curr_rcg_data = {
                        'source_file_key':_f_key,
                        'object_type': ToolBox_Entity_Types.IWS_RUNCYCLEGROUP,
                        'folder':_result.group('rcg_folder'),
                        'name':_result.group('rcg_name'),
                        'rcg_in_file': _rcg_in_file,
                        'span_in_file': _result.span(),
                        'span_in_line': (_result.start() - _f_text.rfind('\n', 0, _result.start()), _result.end() - _f_text.rfind('\n', 0, _result.start()))
                    }
                    _rcg_key_string = f"{self.datasilo.get_component(_f_key, 'full_path')}|{_rcg_in_file}|{_curr_rcg_data['folder']}{_curr_rcg_data['name']}"
                    _curr_rcg_key = self.datasilo.create_entity(key_id=gen_uuid_key(_rcg_key_string), components=_curr_rcg_data)
                    if _last_rcg_key is not None:
                        _text_block = _f_text[self.datasilo.get_component(key=_last_rcg_key, component_name='span_in_file')[0]:self.datasilo.get_component(key=_curr_rcg_key, component_name='span_in_file')[0]].strip()
                        self.datasilo.add_component(_last_rcg_key, 'text_block', _text_block)                        
                    
                if _curr_rcg_key is not None and _last_rcg_key is not None:
                    _text_block = _f_text[self.datasilo.get_component(key=_curr_rcg_key, component_name='span_in_file')[0]:].strip()
                    self.datasilo.add_component(_curr_rcg_key, 'text_block', _text_block)
            
            _rcg_keys = self.datasilo.get_entity_keys_by_component_value(
                component='object_type',   
                value=ToolBox_Entity_Types.IWS_RUNCYCLEGROUP,
                source_file_key=_f_key
            )

            def finditer_exclude_by_span (text:str, include_pattern:str , exclude_spans:list[str]) ->list[re.Match]:
                _include_rslt = re.compile(pattern=include_pattern, flags=re.MULTILINE)
                _exclude_results = [re.compile(pattern=ex_pattern, flags=re.MULTILINE) for ex_pattern in exclude_spans]
                _exclude_spans:list[tuple[int,int]] = []
                for ex in _exclude_results:
                    _ex_rslt = ex.finditer(text)
                    if _ex_rslt is not None:
                        for _ex in _ex_rslt:
                            _exclude_spans.append(_ex.span())
                _found_list = []
                for m in _include_rslt.finditer(text):
                    if any(ex_span[0] >= m.start() <= ex_span[1] or ex_span[0] >= m.end() <= ex_span[1] for ex_span in _exclude_spans): 
                        continue
                    else:
                        _found_list.append(m)
                return _found_list


            if _rcg_keys is not None and len(_rcg_keys) > 0:
                for _rcg_key in _rcg_keys:
                    _rcg_text_block = self.datasilo.get_component(_rcg_key, 'text_block', '')
                    if isinstance(_rcg_text_block, str) and len(_rcg_text_block) > 0:                        
                        _description_match = re.search(ToolBox_REGEX_Patterns.IWS_DESCRIPTION_PART, _rcg_text_block)
                        if _description_match is not None:
                            self.datasilo.add_component(_rcg_key, 'description', _description_match.groupdict().get('description', None))

                        _valid_to_match = re.search(ToolBox_REGEX_Patterns.IWS_VALIDTO_PART, _rcg_text_block)
                        if _valid_to_match is not None:
                            _temp = ToolBox_identify_date_parts(
                                val_a = _valid_to_match.groupdict().get('date_v1') or _valid_to_match.group(1),
                                val_b = _valid_to_match.groupdict().get('date_v2') or _valid_to_match.group(2),
                                val_c = _valid_to_match.groupdict().get('date_v3') or _valid_to_match.group(3)
                            )
                            if isinstance(_temp, datetime):
                                self.datasilo.add_component(_rcg_key, 'validto', _temp)

                        _valid_from_match = re.search(ToolBox_REGEX_Patterns.IWS_VALIDFROM_PART, _rcg_text_block)
                        if _valid_from_match is not None:
                            _temp = ToolBox_identify_date_parts(
                                val_a = _valid_from_match.groupdict().get('date_v1') or _valid_from_match.group(1),
                                val_b = _valid_from_match.groupdict().get('date_v2') or _valid_from_match.group(2),
                                val_c = _valid_from_match.groupdict().get('date_v3') or _valid_from_match.group(3)
                            )
                            if isinstance(_temp, datetime):
                                self.datasilo.add_component(_rcg_key, 'validfrom', _temp)
                            

                        _include_pattern = ToolBox_REGEX_Patterns.UNKNOWN_DATE_PART.value
                        _exclude_pattern_list = [
                            ToolBox_REGEX_Patterns.IWS_VALIDFROM_PART.value,
                            ToolBox_REGEX_Patterns.IWS_VALIDTO_PART.value
                        ]
                        _date_values:list[datetime] = []
                        _found_matches = finditer_exclude_by_span(_rcg_text_block, _include_pattern, _exclude_pattern_list)
                        if len(_found_matches) >= 1:
                            for _dv_result in _found_matches:
                                if len (_dv_result.groups()) >= 3:
                                    _temp = ToolBox_identify_date_parts(
                                        val_a = _dv_result.groupdict().get('date_v1') or _dv_result.group(1),
                                        val_b = _dv_result.groupdict().get('date_v2') or _dv_result.group(2),
                                        val_c = _dv_result.groupdict().get('date_v3') or _dv_result.group(3)
                                    )
                                    if isinstance(_temp, datetime):
                                        _date_values.append(_temp)
                                    else:
                                        raise ValueError(f"Unable to parse date from RCG '{self.datasilo.get_component(_rcg_key, 'name','unknown')}' in file '{self.datasilo.get_component(_f_key, 'full_path','unknown')}'")
                        if len(_date_values) > 0:
                            _date_values_sorted = sorted(_date_values)
                            self.datasilo.add_component(_rcg_key, 'date_values', _date_values_sorted)

                        
                        