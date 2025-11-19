#-------------------------------------------------
#   Imports
#-------------------------------------------------
import threading, csv, copy
from typing import Any, Dict, List, Optional, Union, Hashable

from ..ToolBox_Logger import OutputLogger
from .ToolBox_Data_Silo import ToolBox_Data_Silo_Manager
from .shared_utils.ToolBox_Filters import *
from .shared_utils.ToolBox_Enums import (
    ToolBox_Entity_Types
)
from .shared_utils.ToolBox_Utils import (
    gen_uuid_key
)

from .decoders.ToolBox_CSV_file import ToolBox_CSV_File_Manager

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

class ToolBox_Action_Manager :
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
    def get_instance(cls) -> "ToolBox_Action_Manager":
        """Returns the singleton instance of ToolBox_Action_Manager, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    #-------public Getter & Setter methods -------#

    @ToolBox_Decorator
    def calendar_report_to_CSV(self, output_name:str , output_path:str, **component_filters):
        """Returns a list of tuples with the calendar and oldest date value"""
        _cal_keys = self.datasilo.get_entity_keys_by_component_value('object_type', ToolBox_Entity_Types.IWS_CALENDAR, **component_filters)
        if _cal_keys is not None and len(_cal_keys) >= 1:
            _values_holder = []
            for _cal_key in _cal_keys:
                _cal_ent = self.datasilo.get_entity(_cal_key)
                if _cal_ent is not None:
                    _folder = _cal_ent['folder'] if 'folder' in _cal_ent else None
                    _name = _cal_ent['name'] if 'name' in _cal_ent else None
                    _oldest_date = min(_cal_ent.get('dates', [])) if _cal_ent.get('dates') else None
                    _newest_date = max(_cal_ent.get('dates', [])) if _cal_ent.get('dates') else None
                    _path_parts = os.path.normpath(_folder).split(os.sep) if _folder is not None else None
                    _contract = [_pt for _pt in _path_parts if _pt.strip() != ''] if _path_parts is not None else None
                    _values_holder.append({
                        "Contract": _contract[0] if _contract is not None and len(_contract) > 0 else None,
                        "folder": _folder,
                        "Name": _name,
                        "Oldest Date": _oldest_date,
                        "Newest Date": _newest_date
                    })
            _new_csv_entity = self.csv_manager.new_csv_file(
                file_name=output_name,
                output_path=output_path
            )
            if self.datasilo.entity_has_component(_new_csv_entity, 'column_names') == False:
                self.datasilo.add_component(_new_csv_entity, 'column_names', [])
            _stored_columns:list[str] = self.datasilo.get_component(_new_csv_entity, 'column_names', [])
            for _row_data in _values_holder:
                for _col in _row_data.keys():
                    if _col not in _stored_columns:
                        _stored_columns.append(_col)
            self.datasilo.update_component(_new_csv_entity, 'column_names', _stored_columns)
            _stored_values:list[list[str]] = self.datasilo.get_component(_new_csv_entity, 'row_values', [])
            for _row_data in _values_holder:
                _row_values = []
                for _col in _stored_columns:
                    _row_values.append(_row_data.get(_col, ''))
                if _row_values not in _stored_values:
                    _stored_values.append(_row_values)
            self.datasilo.update_component(_new_csv_entity, 'row_values', _stored_values)
            self.csv_manager.save_csv_entity_to_file(
                target_entity=_new_csv_entity, 
                file_name=output_name, 
                output_folder=output_path)
        else:
            self.log.info("No calendars found in collection to report.")

                    