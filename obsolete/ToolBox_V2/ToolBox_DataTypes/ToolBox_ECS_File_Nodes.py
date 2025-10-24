#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import os, copy, uuid, re
from datetime import datetime
from typing import Any, Optional

from ToolBox_V2.ToolBox_logger import OutputLogger
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_JIL_File import ToolBox_IWS_JIL_File
from ToolBox_V2.ToolBox_DataTypes.ToolBox_ECS_Data_Nodes import (
    ToolBox_ECS_Node,
    ToolBox_Entity_types,
    ToolBox_REGEX_Patterns,
    ToolBox_ECS_Node_IWS_Obj
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
    ) :
        self._is_open = False
        _file_key = str(uuid.uuid5(uuid.NAMESPACE_DNS, source_file_path))
        self._file_name = '.'.join(os.path.basename(source_file_path).split('.')[0:-1])
        self._source_extension = os.path.basename(source_file_path).split('.')[-1].lower()
        super().__init__(
            id_key = _file_key,
            name = self._file_name,
            node_type = ToolBox_Entity_types.FILE,
            parent_entitity = None,
            initial_data = None
        )
        self._source_file_path = source_file_path
        self._source_root_path = root_path
        self._size_bytes = os.path.getsize(source_file_path)
        self._last_modified = datetime.fromtimestamp(os.path.getmtime(source_file_path))
    
    def __repr__(self):
        return f"{type(self)}(source_file_path:str={self.sourceFilePath}, roor_path={self.rootPath})"
    
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
        return self._source_file_path
    
    @property
    def sourceFilePath (self) -> str:
        """Returns Source Path with file name and extention."""
        return os.path.abspath(os.path.join(self._source_file_path, f"{self._name}{self._source_extension}"))
    
    @property
    def relPath (self) -> str:
        """Returns Relative Path without file name or file extention."""
        return os.path.relpath(self._source_file_path,self._source_root_path)
    
    @property
    def relFilePath (self) -> str:
        """Returns Relative Path with file name and extention."""
        return os.path.join(self.relPath, f"{self._name}{self._source_extension}")

    #------- Methods -------#


#-------------------------------------------------
#   Defined Node Classes
#-------------------------------------------------

class ToolBox_ECS_JIL_File (ToolBox_ECS_File_Node):
    """Extends from ToolBox_ECS_File_Node.

    Generic IWS Object node, handles all information about standard IWS objects.
    Handles basic Parent-Child relasionships like:
    
    All children foudn under this node would represent ownership of all shild nodes,
    and only represents half the hyerarchy and structure of the Node Tree.
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
    ) :
        super().__init__(
            source_file_path= source_file_path,
            root_path= root_path,
        )

        self._source_file_text = None
        self._modified_file_text = None

    #-------public Getter & Setter methods -------#


    #------- Public Methods -------#

    @ToolBox_Decorator
    def open_file (self, quite_logging:bool=False):
        """Opens teh Jil file and loads the data as Node objects."""
        if self.is_Open != True:
            try:
                _holder = None
                with open(self.sourceFilePath, "r", encoding="utf-8") as f:
                    _holder = copy.deepcopy(f.read())
                if (_holder is not None):
                    if (quite_logging != True): self.log.debug (f"Opening source file : '{self.relFilePath}'")
                    self._source_file_text = _holder
                    self._modified_file_text = _holder
                    self._isOpen = True
                else:
                    self.log.debug (f"Unable to read file contents : '{self.relFilePath}'")
                    self._source_file_text = None
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
    
    @ToolBox_Decorator
    def save_File (self, outputFolder:str, rename:str=None, useRelPath:bool=False):
        """Saves teh current modifications of teh file to the target location."""
        _outputPath = os.path.join(outputFolder,self.relPath) if useRelPath == True else outputFolder
        os.makedirs(_outputPath, exist_ok=True)
        _filename = rename if rename != None else self.name
        _outputFilePath = os.path.join (_outputPath, f"{_filename}{self.foramt}")
        if os.path.exists (_outputFilePath):
            os.remove(_outputFilePath)
        try:
            _file_text = """"""
            _curr_stream_counter = 0
            for _node in self._children_entities:
                if isinstance(_node, ToolBox_ECS_Node_IWS_Obj) and (_node.node_type == ToolBox_Entity_types.IWS_JOBSTREAM):
                    if _curr_stream_counter >= 1:
                        _file_text += '\n\n'
                    _file_text += _node.format_as_Job_Stream(
                        indent = 0,
                        include_notes = True,
                        include_jobs = True,
                        include_end = True
                    )
                    _file_text += '\n'
                    _curr_stream_counter += 1
            with open(_outputFilePath, "w") as output_file:
                output_file.write(_file_text)
            self.log.info (f"Saved file : '{self.relFilePath}' as file : '{_outputFilePath}'")
        except SystemError as se :
            raise (se)
        return self