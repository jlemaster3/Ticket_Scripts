#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os
from datetime import datetime
from collections import UserDict
from typing import Any
from ToolBox_V2.ToolBox_logger import OutputLogger
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

class ToolBox_FileData(UserDict):
    """
    Base class for file metadata.
    Acts as a dictionary-like object for ECS node storage.
    """
    log:OutputLogger = OutputLogger().get_instance()
    _isOpen:bool = None
    _source_path:str = None
    _root_path:str = None
    _name:str = None
    _extension:str = None
    _size_bytes:str = None
    _last_modified:str = None

    def __init__(self, path:str, rootPath:str=None, initial_data:dict[str,Any]=None):
        super().__init__(initial_data)
        self._source_path = os.path.dirname(path) if os.path.isfile(path) else path
        self._rootPath = rootPath
        self._name = os.path.basename(os.path.splitext(path)[0]) if os.path.isfile(path) else None
        self._extension = os.path.splitext(path)[1] if os.path.isfile(path) else None
        self._size_bytes = os.path.getsize(path) if os.path.isfile(path) else None
        self._last_modified = datetime.fromtimestamp(os.path.getmtime(path)) if os.path.isfile(path) else None
    
    def __repr__(self):
        return f"<{self.__class__.__name__} name={self._name} size={self._size_bytes}B>"
    
    #------- Getter / Setters -------#

    def __setitem__(self, key, value):
        if isinstance(value, str):
            self.data[key] = value
        else:
            self.data[key] = value

    def __getitem__(self, key):
        if isinstance(key, str):
            key = key
        return self.data[key] 

    @property
    def is_Open (self) -> bool:
        """Returns if teh file is in an open and editable status."""
        return self._isOpen

    @property
    def name (self) -> str:
        """Returns file name without file extention."""
        return self._name
    
    @name.setter
    def name (self, value:str) :
        """Sets files name."""
        self._name = value
    
    @property
    def foramt (self) -> str:
        """Returns file extention."""
        return self._extension
    
    @property
    def rootPath (self) -> str:
        """Returns Root Path."""
        return self._rootPath
    
    @property
    def sourcePath (self) -> str:
        """Returns Source Path without file name or file extention."""
        return self._source_path
    
    @property
    def sourceFilePath (self) -> str:
        """Returns Source Path with file name and extention."""
        return os.path.abspath(os.path.join(self._source_path, f"{self._name}{self._extension}"))
    
    @property
    def relPath (self) -> str:
        """Returns Relative Path without file name or file extention."""
        return os.path.relpath(self._source_path,self._rootPath)
    
    @property
    def relFilePath (self) -> str:
        """Returns Relative Path with file name and extention."""
        return os.path.join(self.relPath, f"{self._name}{self._extension}")

    #------- Methods -------#