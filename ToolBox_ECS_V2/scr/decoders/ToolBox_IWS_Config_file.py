#-------------------------------------------------
#   Imports
#-------------------------------------------------
import threading, json, copy
from typing import Any, Dict, List, Optional, Union, Hashable

from ...ToolBox_Logger import OutputLogger
from ..ToolBox_Data_Silo import ToolBox_Data_Silo_Manager
from ..shared_utils.ToolBox_Filters import *
from ..shared_utils.ToolBox_Enums import (
    ToolBox_Entity_Types
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

class ToolBox_IWS_Config_File_Manager :
    """Object class that handles *.josn Config files."""   
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    datasilo: ToolBox_Data_Silo_Manager = ToolBox_Data_Silo_Manager.get_instance()

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
    def get_instance(cls) -> "ToolBox_IWS_Config_File_Manager":
        """Returns the singleton instance of ToolBox_IWS_Config_File_Manager, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    #-------public Getter & Setter methods -------#

    @property
    def file_keys(self) -> list[str]:
        return self.datasilo.get_entity_keys_by_component_value('object_type', ToolBox_Entity_Types.FILE_JSON)
    
    @property
    def delineator(self) -> str:
        return self._delineator
    
    @delineator.setter
    def delineator(self, value:str):
        self._delineator = value
    
    #------- Methods / Functions -------#
    @ToolBox_Decorator
    def flatten_json_to_dict(self, nested_json, parent_key:str='', sep:str='.') -> dict[str, Any]:
        """Flatten a nested JSON object into a single-level dictionary."""
        items = {}
        for k, v in nested_json.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(self.flatten_json_to_dict(v, new_key, sep=sep))
            else:
                items[new_key] = v
        return items
    
    @ToolBox_Decorator
    def load_files(self, quite_logging:bool=True, enable_post_porcesses:bool=True, **component_filters):
        """Loads file entities into their respective objects based on entity type."""
        if len(self.file_keys) == 0:
            self.log.info("No JSON files found in collection to load.")
            return
        _key_list = self.datasilo.get_entity_keys_by_component_value('object_type', ToolBox_Entity_Types.FILE_JSON, **component_filters) if component_filters is not None and len(component_filters) > 0 else self.file_keys
        _e_counter_size = len(str(len(_key_list)))
        for _e_counter, _e_key in enumerate(_key_list):
            _e_data:dict[str,Any] = self.datasilo.get_entity(_e_key)
            _file_full_path = _e_data.get('full_path','')
            try:
                _holder = None
                with open(_file_full_path, 'r') as _file:
                    _holder = copy.deepcopy(json.load(_file))
                if (_holder is not None):
                    _holder = self.flatten_json_to_dict(_holder, sep=self.delineator)
                    if (quite_logging != True) : self.log.info(f"[{str(_e_counter+1).rjust(_e_counter_size, '0')}] Loaded Configuration file : '{_file_full_path}'")
                    self.datasilo.add_component(_e_key, 'config_data', _holder)
                else:
                    self.log.error (f"Unable to read file contents : '{_file_full_path}'")
            except BufferError as errmsg:
                self.log.error (f"Unable to open file : '{_file_full_path}'", data = errmsg)
            except FileNotFoundError as errmsg:
                self.log.error (f"File not found : '{_file_full_path}'", data = errmsg)
            except json.JSONDecodeError as errmsg:
                self.log.error (f"JSON decoding error in file : '{_file_full_path}'", data = errmsg)
            except Exception as e:
                self.log.error (f"An unexpected error occurred while reading '{_file_full_path}'", data = e)
        if (enable_post_porcesses == True):
            pass
    
    @ToolBox_Decorator
    def get (self, target_entitiy:str, key:str, default=None) -> Any:
        """Retrieve the value of the 'config_data' component for a given entity key."""
        _results = self.datasilo.get_component(target_entitiy, 'config_data', default)
        if isinstance(_results, dict):
            return _results.get(key, default)
        return default
    
    @ToolBox_Decorator
    def set (self, target_entitiy:str,key:str, value:Any):
        """Set the value of a specific component for a given entity key."""
        _results = self.datasilo.get_component(target_entitiy, 'config_data', {})
        if isinstance(_results, dict):
            _results[key] = value
            self.datasilo.update_component(target_entitiy, 'config_data', _results)
        else:
            self.datasilo.add_component(target_entitiy, 'config_data',{key: value})