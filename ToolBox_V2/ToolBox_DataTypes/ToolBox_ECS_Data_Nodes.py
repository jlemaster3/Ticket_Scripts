#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import random, uuid, re
from typing import Any, Optional
from enum import StrEnum
from collections import UserDict
from ToolBox_V2.ToolBox_logger import OutputLogger
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_JIL_File import ToolBox_IWS_JIL_File

#-------------------------------------------------
#   Variables 
#-------------------------------------------------

IWS_Object_Parts = r'([^ #]+)#(/([^/]*)/([^/]*)/([^/]*)/([^ ]*))'

#-------------------------------------------------
#   Enumerations
#-------------------------------------------------

class ToolBox_Entity_types (StrEnum):
    NONE = 'not_assigned'
    OTHER = 'other'
    DEPENDENCY = 'dependency'
    IWS_JOBSTREAM = 'iws_jobstream'
    IWS_JOB = 'iws_job'
    IWS_TIMING = 'iws_timing'
    IWS_RUNCYCLE = 'iws_runcycle'
    IWS_FOLLOW = 'iws_follow'
    IWS_JOIN = 'iws_join'
    IWS_RESOURCE = 'iws_resource'
    IWS_OPENS = 'iws_opens'
    IWS_PROMPT = 'iws_prompt'

class ToolBox_REGEX_Patterns (StrEnum):
    BLANK_LINE = r'^\s*$'
    NOTE_LINE = r'^\s*#(?!\s*:)'
    IWS_OBJECT_PATH_PARTS = r'([/@][A-Za-z0-9_-]+#)(/[^/\s]*(?:/[^/\s]*)*/)*([^\s.*?\.]*).*?[^\s]?([^\s@]*)?'
    IWS_STREAM_START_LINE = r"^\s*SCHEDULE\s*([/@][A-Za-z0-9_-]+#)(/[^/\s]*(?:/[^/\s]*)*/)*([^\s.*?\.]*).*?[^\s]?([^\s@]*)?"
    IWS_STREAM_EDGE_LINE = r"^\s*:"
    IWS_STREAM_END_LINE = r'^\s*END(?!JOIN)'
    IWS_STREAM_PATH_PARTS = r'^\s*SCHEDULE\s*([/@][A-Za-z0-9_]+#)(/[^/\s]*(?:/[^/\s]*)*/)[.\b]?([^\s]*)'
    IWS_STREAM_DRAFT = r'^\s*DRAFT\s'
    IWS_STREAM_RUNCYCLE_LINE = r'ON\sRUNCYCLE'
    IWS_STREAM_ONREQUEST_LINE = r'ON\sREQUEST'
    IWS_JOB_START_LINE = r'^\s*([/@][A-Za-z0-9_-]+#)(/[^/\s]*(?:/[^/\s]*)*/)*([^\s.*?\.]*).*?[^\s]?([^\s@]*)?'
    IWS_JOB_PATH_PARTS = r'([/@][A-Za-z0-9_-]+#)(/[^/\s]*(?:/[^/\s]*)*/)*([^\s.*?\.]*).*?[^\s]?([^\s@]*)?(?: [Aa][Ss] )?([^\s@]*)?'
    IWS_FOLLOWS_LINE = r'^\s*FOLLOWS\s*(([/@][A-Za-z0-9_-]+#)(/[^/\s]*(?:/[^/\s]*)*/)*([^\s.*?\.]*).*?[^\s@]?([^\s@]*))?([^\s@]*)?(?:\s*[Ii][Ff]\s*([^\s]*))?\s*(PREVIOUS|SAMEDAY)?$'
    IWS_JOIN_LINE = r'^\s*JOIN\s+(\S+)\s* (\d|[Aa]+[Ll]+)\s*OF$'
    IWS_ENDJOIN_LINE = r'^\s*ENDJOIN$'
    IWS_DESCRIPTION_LINE = r'^\s*DESCRIPTION\s'

#-------------------------------------------------
#   Decorator Functions / Wrappers
#-------------------------------------------------

def ToolBox_Decorator(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        return result
    return wrapper

#-------------------------------------------------
#   Base Classes
#-------------------------------------------------    

# Generic Node Class for storing data as a Tree of Dictionary objects with additional functionality.
class ToolBox_ECS_Node (UserDict):
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    
    #------- private properties -------#
    
    _key:str = None
    _name:str = None
    _node_type:ToolBox_Entity_types = None
    _parent_entity:ToolBox_ECS_Node = None
    _children_entities:list[ToolBox_ECS_Node] = None

    #------- Initialize class -------#

    def __init__(
            self,
            name:str,
            node_type:str|ToolBox_Entity_types,
            id_key:str|None=None,
            parent_entitity:Optional[ToolBox_ECS_Node]=None, 
            initial_data:dict[str,Any]=None
            
        ):
        """Initial Entitiy Base Class"""
        super().__init__(initial_data)
        self._name = name
        self._key = id_key if id_key is not None else str(uuid.uuid5(uuid.NAMESPACE_DNS, str(random.randrange(1000000000))))
        self._node_type = node_type or ToolBox_Entity_types.NONE
        self._parent_entity = parent_entitity
        self._children_entities = []

    def __setitem__(self, key, value):
        if isinstance(value, str):
            self.data[key] = value
        else:
            self.data[key] = value

    def __getitem__(self, key):
        if isinstance(key, str):
            key = key
        return self.data[key]
    
    def __repr__(self):
        return f"{type(self)}(node_type='{self._node_type}')"

    #-------public Getter & Setter methods -------#

    @property
    def id_key (self) -> str:
        """Returns assigned id / Key at time of creation."""
        return self._key

    @property
    def name (self) -> str:
        """Returns assigned Node name."""
        return self._name
        
    @name.setter
    def name (self, value:str) :
        """Sets the Name of the Node."""
        self._name = value

    @property
    def children (self) -> list[ToolBox_ECS_Node]:
        return self._children_entities
    

    @property
    def siblings(self) -> list[ToolBox_ECS_Node]:
        """Return a list of sibling entities (excluding self)."""
        if not self._parent_entity:
            return []
        return [sib for sib in self._parent_entity.children if sib is not self]
    
    @property
    def parent(self) -> list[ToolBox_ECS_Node]:
        """Return a list of sibling entities (excluding self)."""
        if not self._parent_entity:
            return None
        return self._parent_entity
    
    @parent.setter
    def parent (self, value:ToolBox_ECS_Node):
        self._parent_entity = value
    
    @property
    def node_type (self) -> str:
        return self._node_type
    
    #------- Methods / Functions -------#

    @ToolBox_Decorator
    def add_child(self, child: ToolBox_ECS_Node):
        """Attach a child entity while maintaining order."""
        if child in self._children_entities:
            return  # avoid duplicates
        self._children_entities.append(child)
        child._parent_entity = self

    @ToolBox_Decorator
    def remove_child(self, child: ToolBox_ECS_Node):
        """Removed child link if found"""
        if child in self._children_entities:
            self._children_entities.remove(child)
            child._parent_entity = None


#-------------------------------------------------
#   Defined Node Classes
#-------------------------------------------------

# IWS Generic Object node, handles all IWS node types by the node_type value defined.
# Extends from ToolBox_ECS_Node.
class ToolBox_ECS_Node_IWS_Obj (ToolBox_ECS_Node):
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    
    #------- private properties -------#
    _iws_object_type:ToolBox_Entity_types = None
    _source_file_path:str = None
    _source_file_obj:ToolBox_IWS_JIL_File = None
    _source_file_text:str = None
    _modified_file_text:str = None
    _notes:str = None
    _workstation:str = None
    _folder:str = None
    _alias: str = None
    _decription:str = None
    _draft:str = None
    _nop:str = None
    _priority:str = None
    _on_overlap:str = None
    _matching: str = None
    _freedays: str = None
    _valid_from:str = None
    _valid_to:str = None
    _time_zone:str = None
    
    _timing_objects:list[ToolBox_ECS_Node_IWS_Obj] = None
    _runcycle_objects:list[ToolBox_ECS_Node_IWS_Obj] = None
    _follows_objects:list[ToolBox_ECS_Node_IWS_Obj] = None
    _job_objects:list[ToolBox_ECS_Node_IWS_Obj] = None
    _resource_objects:list[ToolBox_ECS_Node_IWS_Obj] = None
    _open_objects:list[ToolBox_ECS_Node_IWS_Obj] = None
    _prompt_objects:list[ToolBox_ECS_Node_IWS_Obj] = None
    
    #------- Initialize class -------#

    def __init__(
        self,
        id_key:str,
        object_type:ToolBox_Entity_types,
        name:str = None,
        parent_entitity:Optional[ToolBox_ECS_Node]=None, 
        initial_data:dict[str,Any]=None
    ) :
        super().__init__(
            id_key = id_key,
            name = initial_data['name'] if initial_data is not None and 'name' in initial_data else None,
            node_type = object_type,
            parent_entitity = parent_entitity, 
            initial_data = initial_data
        )
        self._iws_object_type = object_type
        self._notes = initial_data['notes'] if initial_data is not None and 'notes' in initial_data else None
        #self._workstation = initial_data['workstation'] if initial_data is not None and 'workstation' in initial_data else None
        #self._folder = initial_data['folder'] if initial_data is not None and 'folder' in initial_data else None
        #self._alias = initial_data['alias'] if initial_data is not None and 'alias' in initial_data else None
        self._decription = initial_data['description'] if initial_data is not None and 'description' in initial_data else None
        self._draft = initial_data['draft'] if initial_data is not None and 'draft' in initial_data else None
        self._nop = initial_data['nop'] if initial_data is not None and 'nop' in initial_data else None
        self._priority = initial_data['priority'] if initial_data is not None and 'priority' in initial_data else None
        self._on_overlap = initial_data['on_overlap'] if initial_data is not None and 'on_overlap' in initial_data else None
        self._matching = initial_data['matching'] if initial_data is not None and 'matching' in initial_data else None
        self._freedays = initial_data['freedays'] if initial_data is not None and 'freedays' in initial_data else None
        self._valid_from = initial_data['valid_from'] if initial_data is not None and 'valid_from' in initial_data else None
        self._valid_to = initial_data['valid_to'] if initial_data is not None and 'valid_to' in initial_data else None
        self._time_zone = initial_data['time_zone'] if initial_data is not None and 'time_zone' in initial_data else None

        self._timing_objects = []
        self._runcycle_objects = []
        self._follows_objects = []
        self._job_objects = []
        self._resource_objects = []
        self._open_objects = []
        self._prompt_objects = []


    def __str__ (self):
        return str(self.full_path)


    #-------public Getter & Setter methods -------#
    @property
    def id_key (self) -> str:
        """Returns assigned Job Name as stored in IWS."""
        return self._key
    
    @id_key.setter
    def id_key (self, value:str) :
        """Sets the value of the Job Name."""
        self._key = value

    @property
    def object_type (self) -> ToolBox_Entity_types:
        """Returns assigned folder Path in IWS."""
        return self._iws_object_type

    @property
    def sourceFile_Path (self) -> str:
        """Returns assigned folder Path in IWS."""
        return self._source_file_path
    
    @sourceFile_Path.setter
    def sourceFile_Path (self, value:str) :
        """Sets the value of the folder Path in IWS."""
        self._source_file_path = value

    @property
    def sourceFile_Object (self) -> ToolBox_IWS_JIL_File:
        """Returns the object class for the source file if still in memory, returns none if not found"""
        return self._source_file_obj
    
    @sourceFile_Object.setter
    def sourceFile_Object (self, value:ToolBox_IWS_JIL_File) :
        """Sets the object for teh source file."""
        self._source_file_obj = value

    @property
    def sourceFile_Text (self) -> str:
        """Returns assigned folder Path in IWS."""
        return self._source_file_text
    
    @sourceFile_Text.setter
    def sourceFile_Text (self, value:str) :
        """Sets the value of the folder Path in IWS."""
        self._source_file_text = value
        self._modified_file_text = self._source_file_text

    @property
    def workstation (self) -> str:
        """Returns assigned Job Stream Name as stored in IWS."""
        if self._workstation is None:
            if self.node_type == ToolBox_Entity_types.IWS_JOBSTREAM:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_STREAM_PATH_PARTS, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                if isinstance(_IWS_path_parts, re.Match):
                    return _IWS_path_parts.group(1)
                if isinstance(_IWS_path_parts, str):
                    return _IWS_path_parts
            if self.node_type == ToolBox_Entity_types.IWS_JOB:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_JOB_PATH_PARTS, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                if isinstance(_IWS_path_parts, re.Match):
                    return _IWS_path_parts.group(1)
                if isinstance(_IWS_path_parts, str):
                    return _IWS_path_parts
        return self._workstation
    
    @workstation.setter
    def workstation (self, value:str) :
        """Sets the value of the assigned Workstaion."""
        self._workstation = value

    @property
    def folder (self) -> str:
        """Returns assigned folder Path in IWS."""
        if self._folder is None:
            if self.node_type == ToolBox_Entity_types.IWS_JOBSTREAM:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_STREAM_PATH_PARTS, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                if isinstance(_IWS_path_parts, re.Match):
                    return _IWS_path_parts.group(2)
                if isinstance(_IWS_path_parts, str):
                    return _IWS_path_parts
            if self.node_type == ToolBox_Entity_types.IWS_JOB:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_JOB_PATH_PARTS, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                if isinstance(_IWS_path_parts, re.Match):
                    return _IWS_path_parts.group(2)
                if isinstance(_IWS_path_parts, str):
                    return _IWS_path_parts
        return self._folder
    
    @folder.setter
    def folder (self, value:str) :
        """Sets the value of the folder Path in IWS."""
        self._folder = value

    @property
    def name (self) -> str:
        """Returns assigned Job Name as stored in IWS."""
        if self._name is None:
            if self.node_type == ToolBox_Entity_types.IWS_JOBSTREAM:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_STREAM_PATH_PARTS, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                return _IWS_path_parts.group(3)
            if self.node_type == ToolBox_Entity_types.IWS_JOB:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_JOB_PATH_PARTS, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                return _IWS_path_parts.group(3)
        return self._name
        
    @name.setter
    def name (self, value:str) :
        """Sets the value of the Object."""
        self._name = value
    
    @property
    def alias (self) -> str:
        """Returns assigned Object alias as stored in IWS."""
        if self._alias is None:
            if self.node_type == ToolBox_Entity_types.IWS_JOB:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_JOB_PATH_PARTS, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                return _IWS_path_parts.group(5) if _IWS_path_parts.group(5) else None
        return self._alias
        
    @alias.setter
    def alias (self, value:str) :
        """Sets the value of the Object Alias."""
        self._alias = value

    @property
    def deffined_path (self) -> str:
        """Returns the Deffined path as set in source file, might differ from the Full Path seen in executed schedules."""
        if self.object_type == ToolBox_Entity_types.IWS_JOBSTREAM:
            return f"{self.workstation}{self.folder}{self.name}"
        if self.object_type == ToolBox_Entity_types.IWS_JOB:
            return f"{self.workstation}{self.folder}{self.name}"
        return self.name
    
    @property
    def full_path (self) -> str:
        """Returns the full path of the Object, may differ from Deffined Path.
        This will be the extended path shows in the scheduled execution.
        
        Job Streams will end with '.@'
            Ex: {workstation}#/{folder}/{stream name}.@'
        Job Straems will show their chind Jobs' name or alias in place of the '@' symbol to define a child Job."""
        if self.object_type == ToolBox_Entity_types.IWS_JOBSTREAM:
            return f"{self.workstation}{self.folder}{self.name}.@"
        if self.object_type == ToolBox_Entity_types.IWS_JOB:
            _path = f"{self.workstation}{self.folder}"
            if self.parent is not None:
                _path += f'{self._parent_entity.name}.'                
            _path += self.alias if self.alias is not None else self.name
            return _path
        
    #------- Methods / Functions -------#
        
    @ToolBox_Decorator
    def get_pattern_first_match (self, pattern:ToolBox_REGEX_Patterns) -> str|re.Match:
        """returns first matching results of from the current state of object text."""
        _results = re.search(pattern, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
        if isinstance(_results, re.Match):
            return _results
        if isinstance(_results, str):
            return _results
        return None

    @ToolBox_Decorator
    def format_as_Job_Stream (self, indent:int = 0) -> str:
        """Returns teh object formated as an IWS Job Stream definition with Jobs."""
        _indent_space:int = indent
        _temp_string = """"""
        _is_in_stream:bool = False
        _is_in_job_area:bool = False
        _is_in_join_area:bool = False
        for _line in self._modified_file_text.split('\n'):
            if (re.match(ToolBox_REGEX_Patterns.NOTE_LINE, _line, re.IGNORECASE) and 
                (_is_in_stream == False) and
                (_is_in_job_area == False)
                ):
                _temp_string += ' '*_indent_space + f"{_line.strip()}\n"
                continue
            if (re.match(ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE, _line, re.IGNORECASE) and 
                (_is_in_stream == False) and 
                (_is_in_job_area == False)
                ):
                _is_in_stream = True
                _is_in_job_area = False
                _temp_string += ' '*_indent_space + f"{_line.strip()}\n"
                continue
            if re.search(ToolBox_REGEX_Patterns.IWS_JOIN_LINE, _line, re.IGNORECASE):
                _temp_string += ' '*_indent_space + f"{_line}\n"
                _is_in_join_area = True
                continue
            if re.search(ToolBox_REGEX_Patterns.IWS_FOLLOWS_LINE, _line, re.IGNORECASE):
                if(_is_in_join_area == True):
                    _temp_string += ' '*_indent_space + f" {_line}\n"
                else:
                    _temp_string += ' '*_indent_space + f"{_line}\n"
                continue
            if re.search(ToolBox_REGEX_Patterns.IWS_ENDJOIN_LINE, _line, re.IGNORECASE):
                _temp_string += ' '*_indent_space + f"{_line}\n"
                _is_in_join_area = False
                continue
            if (re.match(ToolBox_REGEX_Patterns.IWS_STREAM_EDGE_LINE, _line, re.IGNORECASE) and 
                (_is_in_stream == True) and
                (_is_in_job_area == False)
                ):
                _is_in_job_area = True
                _temp_string += ' '*_indent_space + f"{_line.strip()}\n"
                _job_nodes = [_c for _c in self.children if _c.node_type == ToolBox_Entity_types.IWS_JOB]
                if len(_job_nodes) >= 1 :
                    for _child_node in self.children:
                        if ((isinstance(_child_node, ToolBox_ECS_Node_IWS_Obj)) and(_child_node.node_type == ToolBox_Entity_types.IWS_JOB)):
                            _temp_string += ' '*_indent_space + f"{_child_node.format_as_Job()}\n"
                            _temp_string += "\n\n"
                continue
            if (re.match(ToolBox_REGEX_Patterns.IWS_STREAM_END_LINE, _line, re.IGNORECASE) and
                (_is_in_stream == True)
            ):
                _temp_string += ' '*_indent_space + f"{_line.strip()}\n"
                _is_in_stream = False
                _is_in_job_area = False
                continue
            #All else fails, add the line.
            _temp_string += ' '*_indent_space + f"{_line.strip()}\n"
        return _temp_string
            

    def format_as_Job (self) -> str:
        """Returns teh object formated as an IWS Job definition."""
        return "temp line for a job object"