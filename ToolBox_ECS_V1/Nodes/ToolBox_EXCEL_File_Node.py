#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import os, csv
import openpyxl, openpyxl.cell, openpyxl.utils
from typing import TYPE_CHECKING, Any, Optional, TypedDict
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Nodes.ToolBox_Base_File_Node import ToolBox_ECS_File_Node
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import ToolBox_Entity_Types

if TYPE_CHECKING:
    from ToolBox_ECS_V1.Nodes.ToolBox_Base_Node import ToolBox_ECS_Node
    from ToolBox_ECS_V1.Nodes.ToolBox_IWS_OBJ_Nodes import ToolBox_IWS_IWS_Obj_Node
    from openpyxl import Workbook
    from openpyxl.worksheet.worksheet import Worksheet
    from openpyxl.workbook.workbook import _WorksheetOrChartsheetLike
    from openpyxl.workbook.defined_name import DefinedName, DefinedNameDict, DefinedNameList
    from openpyxl.worksheet.dimensions import DimensionHolder, Dimension

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

class ToolBox_XLSX_File_Node (ToolBox_ECS_File_Node):
    """Extends from ToolBox_ECS_File_Node.

    Node that represents a *.csv file.
    """
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    
    #------- private properties -------#
    
    _workbook:Workbook|None
    _active_sheet:Worksheet|None
    _sheets_as_tables:dict[str,list[dict[str,Any]]]
    _defined_names:DefinedNameDict|None
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
        self._node_type = ToolBox_Entity_Types.FILE_XLSX
        self._workbook = None
        self._active_sheet = None
        self._sheets_as_tables = {}
        self._defined_names = None
    
    #-------public Getter & Setter methods -------#

    @property
    def active_sheet (self) -> Worksheet|None:
        """Returns the active sheet in the document."""
        return self._active_sheet
    
    @property
    def sheet_names (self) -> list[str]:
        return self._workbook.sheetnames if self._workbook is not None else []

    @property
    def workbook_defined_names (self) -> list[str]:
        """Returns a list of DefinedName objects in Workbook"""
        _name_holder = []
        if (self._defined_names is not None) and len(self._defined_names.keys()) >= 1:
            for _dfn_name, _location in self._defined_names:
                if _dfn_name not in _name_holder:
                    _name_holder.append(_dfn_name)
        return _name_holder

    #------- Public Methods -------#

    @ToolBox_Decorator
    def open_file (self, quite_logging:bool=True, enable_post_porcesses:bool=True):
        """Opens source Jil file and converts to IWS objects."""
        if self.is_Open != True:
            try:
                self._workbook = openpyxl.load_workbook(filename=self.sourceFilePath, data_only=True, read_only=True, keep_vba=False)
                self._active_sheet = self._workbook.active if self._workbook is not None else None
                self._is_open = True
                if (quite_logging != True) : self.log.info (f"Opening source file : '{self.relFilePath}'")
            except BufferError as errmsg:
                self.log.warning (f"Unable to open file : '{self.relFilePath}'", data = errmsg)
                self._is_open = False
            except FileNotFoundError as errmsg:
                self.log.error (f"File not found : '{self.relFilePath}'")
                self._is_open = False
        if (enable_post_porcesses == True) and (self._is_open == True) and self._workbook is not None:
            self._defined_names = self._workbook.defined_names
            self.convert_all_sheets_to_tables(first_row_header=True, quite_logging = quite_logging)
    
    @ToolBox_Decorator
    def close_file (self, quite_logging:bool=False):
        """Closes current instance of the file, clearing all temporary changes if not saved."""
        if self.is_Open == True:
            if (quite_logging != True): self.log.debug (f"Closing source file : '{self.relFilePath}'")
            self._isOpen = False
            self._source_file_text = None

    @ToolBox_Decorator
    def save_File (self, outputFolder:str, rename:str|None=None, useRelPath:bool=False):
        """Saves teh current modifications of teh file to the target location."""
        _outputPath = os.path.join(outputFolder,self.relPath) if useRelPath == True else outputFolder
        os.makedirs(_outputPath, exist_ok=True)
        _filename = rename if rename != None else self.name
        _outputFilePath = os.path.join (_outputPath, f"{_filename}{self.foramt}")
        if os.path.exists (_outputFilePath):
            os.remove(_outputFilePath)
        try:
            if self._is_open == True and self._workbook is not None:
                self._workbook.save(_outputFilePath)
            else:
                # add copy file to new location if not already exsts.
                pass
        except SystemError as se :
            self.log.error (f"Unable to save file : 'SystemError' : ", data = se)
        except IOError as ioe:
            self.log.error (f"Error saving file : 'IOError' :", data = ioe)
    
    @ToolBox_Decorator
    def get_sheet_by_name (self, sheet_name:str) -> _WorksheetOrChartsheetLike|None:
        """Returns the index of the sheet by name, returns -1 if not found."""
        return self._workbook[sheet_name] if self._workbook is not None else None
    
    @ToolBox_Decorator
    def get_sheets_with_defined_name (self, defiend_name:str) -> list[str]:
        """Returns teh worksheet name where the defiend name can be found."""
        _sheets_using_dfn:list[str] = []
        if self._defined_names is not None and defiend_name in self._defined_names.keys():
            for _sheetName, _location in self._defined_names:
                if (_sheetName.upper() == defiend_name.upper()):
                    _sheets_using_dfn.append(_sheetName)            
        return _sheets_using_dfn

    @ToolBox_Decorator
    def convert_all_sheets_to_tables (self, first_row_header:bool=True, quite_logging:bool=True) -> dict[str,list[dict[str,Any]]]:
        """Returns a dictionary of named sheet as tables, represented by a dictionary of sheet names as keys whom's values are a list of rows for each table.
        Each row is a key value pair of column names and values."""
        for _sh_name in self.sheet_names:
            if _sh_name not in self._sheets_as_tables.keys():
                self._sheets_as_tables[_sh_name] = self.sheet_to_table_obj(
                    sheet_name = _sh_name, 
                    header_row_index = 1 if first_row_header else None,
                    quite_logging=quite_logging
                )
        return self._sheets_as_tables

    @ToolBox_Decorator
    def sheet_to_table_obj (self, sheet_name:str, header_row_index:int|None=None, quite_logging:bool=True) -> list[dict[str,Any]]:
        """Returns the active sheet as a list of dictionary where the keys are the cell column names and the values are the cell values. for the row."""        
        _target_sheet = self.get_sheet_by_name (sheet_name)
        _header_row_idx = header_row_index-1 if header_row_index is not None and header_row_index >= 1 else None
        _row_holder:list[dict[str,Any]] = []
        if (_target_sheet is not None):
            _column_names:list[str] = []
            _is_header_row:bool = False
            for _row_idx, _row in enumerate(_target_sheet.rows):
                if (_header_row_idx is not None) and ((_row_idx) == _header_row_idx):
                    _is_header_row = True
                elif _is_header_row == True:
                    _is_header_row = False
                _new_row:dict[str, Any]|None = None
                for _cell_idx, _cell in enumerate(_row):
                    _cell_val = _cell.value if _cell.value is not None and all(f"{_cell.value}".strip() != _n for _n in ['', 'None']) else None
                    if _is_header_row == True and _cell_val is not None and (f"{_cell.value}" not in _column_names):
                        _column_names.append(f"{_cell.value}")
                    elif(_header_row_idx is not None and _row_idx > _header_row_idx):
                        if _new_row is None:
                            _new_row = {}
                        _col_name = _column_names[_cell_idx] if (len(_column_names) >= 1 and _cell_idx <= len(_column_names)) else f"cell_{_cell_idx}"
                        if (_col_name not in _new_row.keys()):
                            _new_row[_col_name] = _cell.value
                if (_new_row is not None) and (len(_new_row.keys()) >= 1):
                    _all_cells_are_None:bool = True
                    for _c in _new_row.values():
                        if _c is not None:
                            _all_cells_are_None = False
                            break
                    if _all_cells_are_None != True:
                        _row_holder.append(_new_row)
            if (quite_logging != True) : self.log.debug (f"Converted [{len(_row_holder)}] rows from Excel Workbook: '{self.relFilePath}' on Sheet: '{sheet_name}'")
        return _row_holder