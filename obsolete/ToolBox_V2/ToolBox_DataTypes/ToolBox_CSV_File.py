#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, csv, copy
from datetime import datetime
from collections import UserDict
from typing import Any
from ToolBox_V2.ToolBox_logger import OutputLogger
from ToolBox_V2.ToolBox_DataTypes.ToolBox_File_Base import ToolBox_FileData

#-------------------------------------------------
#   Decorator Functions / Wrappers
#-------------------------------------------------

def ToolBox_Decorator(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        return result
    return wrapper

#-------------------------------------------------
#   Classes
#-------------------------------------------------


class ToolBox_CSV_File(ToolBox_FileData):
    """JIL file metadata for ECS node system."""
    log:OutputLogger = OutputLogger().get_instance()
    _source_file_data:list[dict[str,dict[str,str|int|float|bool|None]]] = None
    
    def __init__(self, path:str, rootPath:str=None, initial_data:dict[str,Any]=None):
        super().__init__(path, rootPath, initial_data)
        self["type"] = "CSV"
        self._source_file_data = []

    #------- properties -------#
    @property
    def rows (self) -> list[dict[str,dict[str,str|int|float|bool|None]]]:
        """Returns a list of rows as dict[column_name:value]."""
        return self._source_file_data
    
    @property
    def columns (self) -> list[str]:
        """Returns a list of columns"""
        return list({key for d in self._source_file_data for key in d.keys()})
    #------- Public Methods -------#

    @ToolBox_Decorator
    def open_file (self, quite_logging:bool=True):
        """Opens source Jil file and converts to IWS objects."""
        if self.is_Open != True:
            try:
                _holder = []
                with open(self.sourceFilePath, mode="r", newline='') as f:
                    _reader = csv.DictReader(f)
                    for row in _reader:
                        _holder.append(row)
                if (_holder is not None):
                    if (quite_logging != True): self.log.debug (f"Opening source file : '{self.relFilePath}'")
                    self._source_file_data = _holder
                    self._isOpen = True
                else:
                    self.log.debug (f"Unable to read file contents : '{self.relFilePath}'")
                    self._source_file_data = None
                    self._isOpen = False
            except BufferError as errmsg:
                self.log.warning (f"Unable to open file : '{self.relFilePath}'", data = errmsg)
            except FileNotFoundError as errmsg:
                self.log.error (f"File not found : '{self.relFilePath}'")
        return self

    @ToolBox_Decorator
    def close_file (self, quite_logging:bool=True):
        """Closes current instance of the file, clearing all temporary changes if not saved."""
        if self.is_Open == True:
            if (quite_logging != True): self.log.debug (f"Closing source file : '{self.relFilePath}'")
            self._isOpen = False
            self._source_file_data = None
        return self