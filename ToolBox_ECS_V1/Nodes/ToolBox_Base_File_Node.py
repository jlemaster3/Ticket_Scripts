#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import os, copy, uuid, re
from datetime import datetime
from typing import Any, Optional, TYPE_CHECKING
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Nodes.ToolBox_Base_Node import ToolBox_ECS_Node
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import ToolBox_Entity_Types

if TYPE_CHECKING:
    from ToolBox_ECS_V1.Nodes.ToolBox_Base_Node import ToolBox_ECS_Node

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

class ToolBox_ECS_File_Node (ToolBox_ECS_Node):
    """Extends from ToolBox_ECS_Node
    
    This Node tpye is ment to handle unique relationships between otehr nodes that extends outside the
    basic "Parent-Child" hierarchy and relationships that most node trees would impliment.
    """
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    
    #------- private properties -------#

    _is_open:bool = False
    _source_file_path:str = None
    _source_root_path:str = None
    _source_extension:str = None
    _size_bytes:int = None
    _last_modified:str = None

    #------- Initialize class -------#

    def __init__(
        self,
        source_file_path:str,
        root_path:str = None,
        parent_entitity:ToolBox_ECS_Node=None, 
        initial_data:dict[str,Any]=None
    ) :
        self._is_open = False
        _file_key = str(uuid.uuid5(uuid.NAMESPACE_DNS, source_file_path))
        self._file_name = '.'.join(os.path.basename(source_file_path).split('.')[:-1])
        self._source_extension = os.path.basename(source_file_path).split('.')[-1].lower()
        super().__init__(
            id_key = _file_key,
            name = self._file_name,
            node_type = ToolBox_Entity_Types.FILE,
            parent_entitity = parent_entitity,
            initial_data = initial_data
        )
        self._source_file_path = source_file_path
        self._source_root_path = root_path
        self._size_bytes = os.path.getsize(source_file_path)
        self._last_modified = datetime.fromtimestamp(os.path.getmtime(source_file_path))
    
    def __repr__(self):
        return f"{type(self)} (source_file_path:str = {self.sourceFilePath})"
    
    #-------public Getter & Setter methods -------#

    @property
    def is_Open (self) -> bool:
        """Returns if the state of the file is open and has been read."""
        return self._is_open
    
    @property
    def foramt (self) -> str:
        """Returns file extention."""
        return self._source_extension
    
    @property
    def rootPath (self) -> str:
        """Returns Root Path."""
        return self._source_root_path
    
    @property
    def sourcePath (self) -> str:
        """Returns Source Path without file name or file extention."""
        return os.path.abspath(os.path.dirname(self._source_file_path))
    
    @property
    def sourceFilePath (self) -> str:
        """Returns Source Path with file name and extention."""
        return os.path.abspath(self._source_file_path)
    
    @property
    def relPath (self) -> str:
        """Returns Relative Path without file name or file extention."""
        return os.path.relpath(self._source_file_path,self._source_root_path)
    
    @property
    def relFilePath (self) -> str:
        """Returns Relative Path with file name and extention."""
        return os.path.join(self.relPath, f"{self._name}{self._source_extension}")

    #------- Methods -------#