#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, re
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
class ToolBox_IWS_Follows_Obj (UserDict):
    """Data Class representing and handing IWS Job Stream actions"""
    log:OutputLogger = OutputLogger().get_instance()
    _source_file:str = None
    _source_text:str = None
    _modified_text:str = None
    _parent_path:str = None
    _target_path:str = None
    _condition_text:str = None

    def __init__(self, definition_text:str, sourceFile:str=None, parent_path:str=None, initial_data:dict[str,Any]=None):
        super().__init__(initial_data)
        self._source_file = sourceFile
        self._source_text = definition_text
        self._modified_text = self._source_text
        self._parent_path = parent_path
    
    def __setitem__(self, key, value):
        if isinstance(value, str):
            self.data[key] = value
        else:
            self.data[key] = value

    
    def __getitem__(self, key):
        if isinstance(key, str):
            key = key
        return self.data[key]

    #------- private methods -------#
    
    #------- properties -------#
    @property
    def parent_path (self) -> str:
        """Returns assigned Target Job Stream or Job Path this dependacy is used by."""
        return self._parent_path

    @parent_path.setter
    def parent_path (self, path:str):
        """Sets the Parent Path"""
        if (path is not None or path.strip() != '') and (self._parent_path.upper() != path.upper()):
            self._parent_path = path

    @property
    def target_path(self) -> str:
        """Returns assigned Target Job Stream or Job Path this dependency is looking for."""
        _match = re.search(r"FOLLOWS\s+(\S+)", self._modified_text)
        return _match.group(1) if _match else None
        
    @target_path.setter
    def target_path (self, path:str):
        """Sets the Parent Path"""
        _match = re.search(re.escape('FOLLOWS') + r'\s+(\w+)', self._modified_text)
        if _match :
            self._modified_text = re.sub('FOLLOWS' + r'\1' + path, self._modified_text, count=1)

    @property
    def matching (self) -> str:
        """Returns the matching value if defined."""
        _is_sameday = True if 'SAMEDAY' in self._modified_text else False
        _is_previous = True if 'PREVIOUS' in self._modified_text else False
        if _is_sameday == True:
            return 'SAMEDAY'
        if _is_previous == True:
            return 'PREVIOUS'
        return None

    @property
    def condition (self) -> str:
        """Returns the matching value if defined."""
        _results = []
        _pattern = re.compile(r'\bIF\b\s+(.*)', re.IGNORECASE)
        for line in self._modified_text.splitlines():
            match = _pattern.search(line)
            if match:
                # Split the captured group into words
                words = re.findall(r'\b\w+\b', match.group(1))
                # Filter out 'SAMEDAY' and 'PREVIOUS' (case-insensitive)
                filtered = [w for w in words if w.upper() not in ['SAMEDAY', 'PREVIOUS']]
                _results.extend(''.join(filtered))
        return ' '.join(_results)

    #------- Public Methods -------#

    @ToolBox_Decorator
    def get_current_text(self) -> str:
        """Returns the current text of this Job."""
        return self._modified_text.strip()
    
    @ToolBox_Decorator
    def reset_modfied_text (self):
        if self._modified_text != self._source_text:
            self._modified_text = self._source_text
        return self
    
    
    @ToolBox_Decorator
    def search_replace_text (self, searchString:str, replaceString:str, updated_source:bool=False) :
        if (searchString in self._modified_text):
            self._modified_text = re.sub(searchString, replaceString, self._modified_text, flags=re.IGNORECASE)
            if updated_source == True:
                self._source_text = re.sub(searchString, replaceString, self._source_text, flags=re.IGNORECASE)
        return self
    
    


class ToolBox_IWS_Join_Obj (UserDict):
    log:OutputLogger = OutputLogger().get_instance()
    _source_file:str = None
    _source_text:str = None
    _source_end_text:str = None
    _modified_text:str = None
    _modified_end_text:str = None
    _parent_path:str = None
    _name:str = None
    _number:int = None

    _follows_collection:list[ToolBox_IWS_Follows_Obj] = []

    def __init__(self, definition_text:str, end_text:str=None, sourceFile:str=None, parent_path:str=None, initial_data:dict[str,Any]=None):
        super().__init__(initial_data)
        self._source_file = sourceFile
        self._source_text = definition_text
        self._source_end_text = end_text
        self._modified_text = self._source_text        
        self._modified_end_text = self._source_end_text
        self._parent_path = parent_path
        self._follows_collection = []
    
    def __setitem__(self, key, value):
        if isinstance(value, str):
            self.data[key] = value
        else:
            self.data[key] = value
    
    def __getitem__(self, key):
        if isinstance(key, str):
            key = key
        return self.data[key]
    
    #------- private methods -------#

    #------- properties -------#

    @property
    def parent_path (self) -> str:
        """Returns assigned Target Job Stream or Job Path this dependacy is used by."""
        return self._parent_path

    @parent_path.setter
    def parent_path (self, path:str):
        """Sets the Parent Path"""
        if (path is not None or path.strip() != '') and (self._parent_path.upper() != path.upper()):
            self._parent_path = path

    @property
    def name (self) -> str:
        """Returns assigned Join Name as stored in IWS."""
        _match = re.search(r"JOIN\s+(\S+)", self._modified_text)
        return _match.group(1) if _match else None
    
    @name.setter
    def name (self, value:str) :
        """Sets the value of the Join Name."""
        _match = re.compile(r"^(?=.{0,12}\bjoin\b)\s+(\w+)\s+(\w+)", re.IGNORECASE | re.MULTILINE)
        if _match :
            self._modified_text = re.sub('JOIN' + r'\1' + value, self._modified_text, count=1)

    @property
    def number (self) -> int|str:
        """Returns assigned Join amount as stored in IWS."""
        _match = re.search(r'\bJOIN\b\s+\S+\s+(\S+)', self._modified_text, re.IGNORECASE)
        return _match.group(1) if _match else None
    
    @number.setter
    def number (self, value:int|str) :
        """Sets the value of the Join amount(0 | 1 | 2 | 3 | ...ect) or ('ALL', 0 == 'ALL')."""
        _match = re.compile(r"^(?=.{0,12}\bjoin\b)\s+(\w+)\s+(\w+)", re.IGNORECASE | re.MULTILINE)
        if _match :
            self._modified_text = re.sub('JOIN' + r'\2' + value, self._modified_text, count=1)

    @property
    def full_path (self) -> str:
        """Returns the full path of the Job Stream as shown in IWS when viewed in a schedule.
        Job        : {workstation}/{folderPath}/{jobStreamName}.{JobName}.{JoinName}
        Job Stream : {workstation}/{folderPath}/{jobStreamName}.@.{JoinName}
        """
        return f"{self._parent_path}.{self._name}"
    
    @property
    def follows_list (self) -> list[ToolBox_IWS_Follows_Obj]:
        """Returns the list of follows and join objects found in this Job Strem"""
        return self._follows_collection
    
    @property
    def follows_targets (self) -> list[ToolBox_IWS_Follows_Obj]:
        """Returns the list of follows and join objects found in this Job Strem"""
        _results = []
        for _f_obj in self._follows_collection:
            _results.append(_f_obj.target_path)
        return _results

    #------- Public Methods -------#

    @ToolBox_Decorator
    def add_follows_by_text (self, definition_text:str, sourceFile:str=None, initial_data:dict[str,Any]=None) :
        _new_follow = ToolBox_IWS_Follows_Obj(
            definition_text = definition_text,
            sourceFile = sourceFile,
            parent_path = self._parent_path,
            initial_data = initial_data 
        )
        self._follows_collection.append(_new_follow)

    @ToolBox_Decorator
    def get_current_text(self) -> str:
        """Returns the current text of this Join and included follows objects."""
        _text = f"JOIN {self.name} {self.number} OF\n"
        _text += f"\n".join ([f" {_f_obj.get_current_text()}" for _f_obj in self._follows_collection])
        _text += f"\n{self._modified_end_text}"
        return _text
    
    @ToolBox_Decorator
    def reset_modfied_text (self):
        if self._modified_text != self._source_text:
            self._modified_text = self._source_text
        return self
    
    @ToolBox_Decorator
    def search_replace_text (self, searchString:str, replaceString:str, updated_source:bool=False) :
        if (searchString in self._modified_text):
            self._modified_text = re.sub(searchString, replaceString, self._modified_text, flags=re.IGNORECASE)
            if updated_source == True:
                self._source_text = re.sub(searchString, replaceString, self._source_text, flags=re.IGNORECASE)
        return self