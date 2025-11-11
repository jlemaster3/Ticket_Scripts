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
    _source_file_path:str
    _source_root_path:str|None
    _source_extension:str
    _source_file_text:str|None
    _modified_file_text:str|None
    _has_changed:bool
    _size_bytes:int
    _last_modified:datetime

    #------- Initialize class -------#

    def __init__(
        self,
        source_file_path:str,
        root_path:str|None = None,
        parent_entitity:ToolBox_ECS_Node|None=None, 
        initial_data:dict[str,Any]|None=None
    ) :
        self._is_open = False
        _file_key = str(uuid.uuid5(uuid.NAMESPACE_DNS, source_file_path))
        self._file_name = os.path.basename(source_file_path).split('.')[0]
        self._source_extension = os.path.basename(source_file_path).split('.')[-1]
        super().__init__(
            id_key = _file_key,
            name = self._file_name,
            node_type = ToolBox_Entity_Types.FILE,
            parent_entitity = parent_entitity,
            initial_data = initial_data
        )
        self._source_file_path = source_file_path
        self._source_root_path = root_path
        self._source_file_text = None
        self._modified_file_text = None
        self._has_changed = False
        self._size_bytes = os.path.getsize(source_file_path)
        self._last_modified = datetime.fromtimestamp(os.path.getmtime(source_file_path))
    
    def __contains__(self, item):
        """
        Defines how membership is checked for MyContainer instances.
        """
        return item in self._modified_file_text
    
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
    def rootPath (self) -> str|None:
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
        return os.path.relpath(self.sourcePath,self._source_root_path)
    
    @property
    def relFilePath (self) -> str:
        """Returns Relative Path with file name and extention."""
        return os.path.join(self.relPath, f"{self.name}.{self.foramt}")
    
    @property
    def has_changed (self) ->bool:
        return self._modified_file_text == self._source_file_text

    #------- Methods -------#

    @ToolBox_Decorator
    def open_file (self, quite_logging:bool=False, enable_post_porcesses:bool=True):
        try:
            with open(self._source_file_path, 'r', encoding='utf-8') as file:
                content:str = file.read()
                self._source_file_text = content
                self._modified_file_text = content
            self._is_open = True
            self._has_changed = False
        except FileNotFoundError:
            self.log.error(f"Error: The file '{self._source_file_path}' was not found.")
            self._is_open = False
            self._has_changed = False
        except IOError as e:
            self.log.error(f"Error reading file '{self._source_file_path}': {e}")
            self._is_open = False
            self._has_changed = False
        if (enable_post_porcesses == True) and (self._is_open == True):
            # no post processes to run for basic text files.
            pass

    @ToolBox_Decorator
    def close_file (self):
        """Closes current instance of the file, clearing all changes."""
        self._source_file_text = None
        self._modified_file_text = None
        self._is_open = False
        self._has_changed = False
    
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
            _file_text = rf"""{self._modified_file_text}""" if self._modified_file_text is not None else None
            if _file_text is not None:
                with open(_outputFilePath, "w", encoding='utf-8') as output_file:
                    output_file.write(_file_text)
                self.log.info (f"Saved file : '{self.relFilePath}' as file : '{_outputFilePath}'")
            else:
                self.log.error (f"Unable to save file expecting'node._source_file_text' to be tpye of literal string, got : ", data=_file_text)
        except SystemError as se :
            self.log.error (f"Unable to save file : 'SystemError' : ", data = se)
        except IOError as ioe:
            self.log.error (f"Error saving file : 'IOError' :", data = ioe)

    @ToolBox_Decorator
    def reset_modified_text (self):
        """Resets the current state of teh modified text to the stored state of the text when the file was last opened."""
        if self._is_open != True:
            self.open_file(quite_logging=True, enable_post_porcesses=False)
        if self._is_open == True and self._modified_file_text is not None and self._source_file_text is not None:
            self._modified_file_text = self._source_file_text

    @ToolBox_Decorator
    def search_for_terms (self, search_terms:list[str]) -> dict[str,bool]:
        """Returns a collection of terms and boolean values if found in text."""
        if self._is_open != True:
            self.open_file(quite_logging=True, enable_post_porcesses=False)
        _terms:dict[str,bool] = {}
        for _term in search_terms:
            if self._modified_file_text is not None:
                _terms[_term] = _term in self._modified_file_text
        return _terms
    
    @ToolBox_Decorator
    def search_replace_terms (self, search_repalce_strings:dict[str,str]):
        if self._is_open != True:
            self.open_file(quite_logging=True, enable_post_porcesses=False)
        """Preforms a basic search and replace string operation on the current state of the file text."""
        for _search, _replace in search_repalce_strings.items():
            if self._modified_file_text is not None:
                self._modified_file_text = self._modified_file_text.replace(_search, _replace)

