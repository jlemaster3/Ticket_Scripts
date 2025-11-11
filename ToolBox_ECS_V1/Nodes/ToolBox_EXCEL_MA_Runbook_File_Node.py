#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import os, csv
import openpyxl, openpyxl.cell, openpyxl.utils
from typing import TYPE_CHECKING, Any
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Nodes.ToolBox_EXCEL_File_Node import ToolBox_XLSX_File_Node
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import ToolBox_Entity_Types
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Formatters import (
    ToolBox_list_of_dictionaries_to_table
)

if TYPE_CHECKING:
    from ToolBox_ECS_V1.Nodes.ToolBox_Base_Node import ToolBox_ECS_Node
    from ToolBox_ECS_V1.Nodes.ToolBox_IWS_OBJ_Nodes import ToolBox_IWS_Obj_Node
#from ToolBox_ECS_V1.ToolBox_Manager import ToolBox_Manager

#-------------------------------------------------
#   Decorator Functions / Wrappers
#-------------------------------------------------

def ToolBox_Decorator(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        return result
    return wrapper

#-------------------------------------------------
#   Defined Node Classes
#-------------------------------------------------

class ToolBox_IWS_XLSX_Runbook_File_Node (ToolBox_XLSX_File_Node):
    """Extends from ToolBox_ECS_File_Node.

    Node that represents a *.csv file.
    """
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    
    #------- private properties -------#

    _runbook_data_table_tab_name:str = 'Data Table'
    _runbook_data_table_obj:list[dict[str, Any]]
    _runbook_hidden_data_table_tab_name:str = 'Hidden_Data_Table'
    _runbook_hidden_data_table_obj:list[dict[str, Any]]
    _runbook_info_tab_name:str = 'Runbook Info'
    _runbook_info_table_obj:list[dict[str, Any]]
    
    
    
    #------- Initialize class -------#

    def __init__(
        self,
        source_file_path:str,
        root_path:str|None = None,
        parent_entitity:ToolBox_ECS_Node|None = None,
        initial_data:dict[str,Any]|None=None
    ) :
        super().__init__(
            source_file_path = source_file_path,
            root_path = root_path,
            parent_entitity = parent_entitity,
            initial_data = initial_data
        )
        self._node_type = ToolBox_Entity_Types.IWS_XLS_RUNBOOK
        self._runbook_data_table_obj = []
        self._runbook_hidden_data_table_obj = []
        self._runbook_info_table_obj = []
    
    #-------public Getter & Setter methods -------#
    @property
    def environments (self) -> list[str]:
        """Returns a list of IWS 'environments' refrenced in this Runbook"""
        if self._is_open == False:
            self.open_file(enable_post_porcesses=True)
        _holder:list[str] = []
        if len(self._runbook_data_table_obj) >= 1:
            for _row in self._runbook_data_table_obj:
                if (('Env.' in _row.keys()) and 
                    (_row['Env.'] not in _holder)
                ):
                    _holder.append(_row['Env.'])
        return _holder
    
    @property
    def job_stream_full_paths (self) -> list[str]:
        """Returns a list of IWS 'full path' for each Job Stream Object defined in this Runbook"""
        if self._is_open == False:
            self.open_file(enable_post_porcesses=True)
        _holder:list[str] = []
        if len(self._runbook_data_table_obj) >= 1:
            for _row in self._runbook_data_table_obj:
                if (('Full Path' in _row.keys()) and 
                    (_row['Full Path'] not in _holder) and 
                    ('.@' in _row['Full Path'])
                ):
                    _holder.append(_row['Full Path'])
        return _holder
    
    @property
    def job_full_paths (self) -> list[str]:
        """Returns a list of IWS 'full path' for each Job Object defined in this Runbook"""
        if self._is_open == False:
            self.open_file(enable_post_porcesses=True)
        _holder:list[str] = []
        if len(self._runbook_data_table_obj) >= 1:
            for _row in self._runbook_data_table_obj:
                if (('Full Path' in _row.keys()) and 
                    (_row['Full Path'] not in _holder) and 
                    ('.@' not in _row['Full Path'])
                ):
                    _holder.append(_row['Full Path'])
        return _holder

    #------- Public Methods -------#

    @ToolBox_Decorator
    def open_file(self, quite_logging: bool = True, enable_post_porcesses: bool = True):
        super().open_file(quite_logging = quite_logging, enable_post_porcesses=False)
        if enable_post_porcesses == True and self._workbook is not None:
            
            self._runbook_info_table_obj = self.sheet_to_table_obj(self._runbook_info_tab_name, header_row_index=12)
            self._runbook_data_table_obj = self.sheet_to_table_obj(self._runbook_data_table_tab_name, header_row_index=2)
            self._runbook_hidden_data_table_obj = self.sheet_to_table_obj(self._runbook_hidden_data_table_tab_name, header_row_index=2)
            #self.log.blank (ToolBox_list_of_dictionaries_to_table(self._runbook_info_table_obj))
            #self.log.blank (ToolBox_list_of_dictionaries_to_table(self._runbook_data_table_obj))
    