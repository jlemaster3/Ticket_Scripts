#-------------------------------------------------
#   Imports
#-------------------------------------------------
import threading, re, copy
from typing import Any, Dict, List, Optional, Union, Hashable

from ...ToolBox_Logger import OutputLogger
from ..ToolBox_Data_Silo import ToolBox_Data_Silo_Manager
from ..shared_utils.ToolBox_Filters import *
from ..shared_utils.ToolBox_Enums import (
    ToolBox_Entity_Types
)
from ..shared_utils.ToolBox_Utils import (
    gen_uuid_key
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

    _delineator:str = '.'

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
    
    @property
    def delineator(self) -> str:
        return self._delineator
    
    @delineator.setter
    def delineator(self, value:str):
        self._delineator = value
    
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

        _calendar_pattern = r'^ ?\$[Cc][Aa][Ll][Ee][Nn][Dd][Aa][Rr]'
        _calendar_name_pattern = r'^(?P<folder>[^\s]*(?:[^\s]*)*\/)*(?P<calendar>[^\s.*?\.]*)\b'
        _calendar_description_pattern = r'^ *(?:[\"\']{1}?(?P<description>[^\s]+.*)[\"\']{1}?)'
        _date_value_pattern = r'\b(?P<month>\d{2})[-\/\.]?(?P<day>\d{2})[-\/\.]?(?P<year>\d{4})\b'

        for _e_counter, _e_key in enumerate(_key_list):
            _e_str = self.datasilo.get_component(_e_key, 'file_text', '')
            _calendar_match = re.match(_calendar_pattern, _e_str)
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
                    _cal_description = re.search(_calendar_description_pattern, _line_str)
                    if _cal_description is not None and _curr_calendar_key is not None:
                        self.datasilo.add_component(_curr_calendar_key, 'description', _cal_description.group('description'))
                        continue
                    _cal_dates = re.finditer(_date_value_pattern, _line_str)
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
        _key_list = self.datasilo.get_entity_keys_by_component_value('object_type', ToolBox_Entity_Types.FILE_TXT, **component_filters) if component_filters is not None and len(component_filters) > 0 else self.file_keys
        
        pass