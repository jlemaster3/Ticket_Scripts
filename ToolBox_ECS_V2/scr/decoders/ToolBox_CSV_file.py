#-------------------------------------------------
#   Imports
#-------------------------------------------------
import threading, csv, copy
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

class ToolBox_CSV_File_Manager :
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
    def get_instance(cls) -> "ToolBox_CSV_File_Manager":
        """Returns the singleton instance of ToolBox_CSV_File_Manager, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    #-------public Getter & Setter methods -------#

    @property
    def file_keys(self) -> list[str]:
        return self.datasilo.get_entity_keys_by_component_value('object_type', ToolBox_Entity_Types.FILE_CSV)
    
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
            self.log.info("No CSV files found in collection to load.")
            return
        _key_list = self.datasilo.get_entity_keys_by_component_value('object_type', ToolBox_Entity_Types.FILE_CSV, **component_filters) if component_filters is not None and len(component_filters) > 0 else self.file_keys
        _e_counter_size = len(str(len(_key_list)))
        for _e_counter, _e_key in enumerate(_key_list):
            _e_data:dict[str,Any] = self.datasilo.get_entity(_e_key)
            _file_full_path = _e_data.get('full_path','')
            try:
                _field_names = None
                _row_values = None
                _holder = None
                with open(_file_full_path, mode="r", newline='') as f:
                    _reader = csv.DictReader(f)
                    if _reader is not None:
                        _holder = []
                        _field_names = []
                        _row_values = []
                        for _row in _reader:
                            _holder.append(_row)
                            _row_data = []
                            for _col, _val in _row.items():
                                if _col not in _field_names:
                                    _field_names.append(_col)
                                _row_data.append(_val)
                            _row_values.append(_row_data)
                if (_holder is not None and _field_names is not None):
                    if (quite_logging != True) : self.log.info(f"[{str(_e_counter+1).rjust(_e_counter_size, '0')}] Loaded CSV file : '{_file_full_path}'")
                    self.datasilo.add_component(_e_key, 'raw_data', _holder)
                    self.datasilo.add_component(_e_key, 'column_names', _field_names)
                    self.datasilo.add_component(_e_key, 'row_values', _row_values)
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
    def new_csv_file (self, file_name:str, output_path:str|None=None) -> str:
        _new_csv_data = {
            "full_path": os.path.join(output_path, f"{file_name}.csv") if output_path is not None else f"{file_name}.csv",
            "file_path": output_path if output_path is not None else None,
            "file_name": file_name,
            "file_format": "csv",
            "created_datatime" : None,
            "modified_datatime" : None,
            "object_type": ToolBox_Entity_Types.FILE_CSV,
            "column_names": [],
            "row_values": []
        }
        _new_cvs_key = gen_uuid_key(_new_csv_data['full_path'])
        if self.datasilo.entity_exists(_new_cvs_key):
            return _new_cvs_key
        else:
            _new_csv_entity = self.datasilo.create_entity(key_id=_new_cvs_key, components=_new_csv_data)
            return _new_csv_entity
        
    @ToolBox_Decorator
    def save_csv_entity_to_file (self, target_entity:str, file_name:str|None=None, output_folder:str|None=None) -> bool:
        _e_data:dict[str,Any] = self.datasilo.get_entity(target_entity)
        if _e_data is None:
            self.log.error (f"CSV Entity with key '{target_entity}' does not exist in data silo.")
            return False
        _file_full_path = os.path.join(output_folder, f"{file_name}.csv") if file_name is not None and output_folder is not None else _e_data.get('full_path',None)
        _column_names:list[str] = _e_data.get('column_names', [])
        _row_values:list[list[Any]] = _e_data.get('row_values', [])
        if _file_full_path is not None and _column_names is not None and _row_values is not None:
            try:
                with open(_file_full_path, mode="w", newline='') as f:
                    _writer = csv.writer(f)
                    if len(_column_names) > 0:
                        _writer.writerow(_column_names)
                    for _row in _row_values:
                        _writer.writerow(_row)
                self.log.info (f"CSV file saved successfully : '{_file_full_path}'")
                return True
            except BufferError as errmsg:
                self.log.error (f"Unable to open file for writing : '{_file_full_path}'", data = errmsg)
            except Exception as e:
                self.log.error(f"An unexpected error occurred while writing '{_file_full_path}'", data = e)
        return False