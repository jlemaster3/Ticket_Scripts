#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import os, csv
from typing import TYPE_CHECKING, Any
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Nodes.ToolBox_Base_File_Node import ToolBox_ECS_File_Node
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import ToolBox_Entity_Types

if TYPE_CHECKING:
    from ToolBox_ECS_V1.Nodes.ToolBox_Base_Node import ToolBox_ECS_Node
    from ToolBox_ECS_V1.Nodes.ToolBox_IWS_OBJ_Nodes import ToolBox_IWS_IWS_Obj_Node
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

class ToolBox_CSV_File_Node (ToolBox_ECS_File_Node):
    """Extends from ToolBox_ECS_File_Node.

    Node that represents a *.csv file.
    """
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    
    #------- private properties -------#
    
    _source_file_text:str = None
    _modified_file_text:str = None
    
    #------- Initialize class -------#

    def __init__(
        self,
        source_file_path:str,
        root_path:str = None,
        parent_entitity:ToolBox_ECS_Node = None,
        initial_data:dict[str,Any]=None
    ) :
        super().__init__(
            source_file_path = source_file_path,
            root_path = root_path,
            parent_entitity = parent_entitity,
            initial_data = initial_data
        )
        self.node_type = ToolBox_Entity_Types.FILE_CSV,
        self._source_file_text = None
        self._modified_file_text = None

    
    #-------public Getter & Setter methods -------#
    
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
    def open_file (self, quite_logging:bool=False):
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
            self._source_file_text = None
        return self