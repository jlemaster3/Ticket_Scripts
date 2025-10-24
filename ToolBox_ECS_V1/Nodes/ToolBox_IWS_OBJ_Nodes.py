#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import random, uuid, re
from typing import Any, Optional, TYPE_CHECKING
from enum import StrEnum
from collections import UserDict
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Nodes.ToolBox_Base_Node import ToolBox_ECS_Node
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import ToolBox_Entity_Types, ToolBox_REGEX_Patterns

if TYPE_CHECKING:
    from ToolBox_ECS_V1.Nodes.ToolBox_IWS_File_Nodes import ToolBox_IWS_JIL_File_Node
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
#-------------------------------------------------
#   Defined Node Classes
#-------------------------------------------------

class ToolBox_IWS_IWS_Obj_Node (ToolBox_ECS_Node):
    """Extends from ToolBox_ECS_Node.

    Generic IWS Object node, handles all information about standard IWS objects.
    Handles basic Parent-Child relasionships like:
    
    All children foudn under this node would represent ownership of all shild nodes,
    and only represents half the hyerarchy and structure of the Node Tree.
    """
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    
    #------- private properties -------#
    _iws_object_type:ToolBox_Entity_Types = None
    _source_file_path:str = None
    _source_file_obj:ToolBox_IWS_JIL_File_Node = None
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
    
    _timing_objects:list[ToolBox_IWS_IWS_Obj_Node] = None
    _runcycle_objects:list[ToolBox_IWS_IWS_Obj_Node] = None
    _follows_objects:list[ToolBox_IWS_IWS_Obj_Node] = None
    _job_objects:list[ToolBox_IWS_IWS_Obj_Node] = None
    _resource_objects:list[ToolBox_IWS_IWS_Obj_Node] = None
    _open_objects:list[ToolBox_IWS_IWS_Obj_Node] = None
    _prompt_objects:list[ToolBox_IWS_IWS_Obj_Node] = None
    
    #------- Initialize class -------#

    def __init__(
        self,
        id_key:str,
        object_type:ToolBox_Entity_Types,
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

    def __repr__(self):
        return f"{type(self)} (id_key:str = {self.id_key}, object_type:ToolBox_Entity_Types = {self.node_type},)"
    
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
    def object_type (self) -> ToolBox_Entity_Types:
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
    def sourceFile_Object (self) -> ToolBox_IWS_JIL_File_Node:
        """Returns the object class for the source file if still in memory, returns none if not found"""
        return self._source_file_obj
    
    @sourceFile_Object.setter
    def sourceFile_Object (self, value:ToolBox_IWS_JIL_File_Node) :
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
            if self.node_type == ToolBox_Entity_Types.IWS_JOBSTREAM:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_STREAM_PATH_PARTS, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                if isinstance(_IWS_path_parts, re.Match):
                    return _IWS_path_parts.group(1)
                if isinstance(_IWS_path_parts, str):
                    return _IWS_path_parts
            if self.node_type == ToolBox_Entity_Types.IWS_JOB:
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
            if self.node_type == ToolBox_Entity_Types.IWS_JOBSTREAM:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_STREAM_PATH_PARTS, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                if isinstance(_IWS_path_parts, re.Match):
                    return _IWS_path_parts.group(2)
                if isinstance(_IWS_path_parts, str):
                    return _IWS_path_parts
            if self.node_type == ToolBox_Entity_Types.IWS_JOB:
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
            if self.node_type == ToolBox_Entity_Types.IWS_JOBSTREAM:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_STREAM_PATH_PARTS, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                return _IWS_path_parts.group(3)
            if self.node_type == ToolBox_Entity_Types.IWS_JOB:
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
            if self.node_type == ToolBox_Entity_Types.IWS_JOB:
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
        if self.object_type == ToolBox_Entity_Types.IWS_JOBSTREAM:
            return f"{self.workstation}{self.folder}{self.name}"
        if self.object_type == ToolBox_Entity_Types.IWS_JOB:
            return f"{self.workstation}{self.folder}{self.name}"
        return self.name
    
    @property
    def full_path (self) -> str:
        """Returns the full path of the Object, may differ from Deffined Path.
        This will be the extended path shows in the scheduled execution.
        
        Job Streams will end with '.@'
            Ex: {workstation}#/{folder}/{stream name}.@'
        Job Straems will show their chind Jobs' name or alias in place of the '@' symbol to define a child Job."""
        if self.object_type == ToolBox_Entity_Types.IWS_JOBSTREAM:
            return f"{self.workstation}{self.folder}{self.name}.@"
        if self.object_type == ToolBox_Entity_Types.IWS_JOB:
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
    def format_as_Job_Stream (self, indent:int = 0, include_notes:bool = True, include_jobs:bool = True, include_end:bool=True) -> str:
        """Returns the Node text formated as an IWS Job Stream definition."""
        _temp_string = """"""
        _contains_pre_note:bool = False
        _is_in_stream:bool = False
        _is_in_join_area:bool = False
        for _line in self._modified_file_text.split('\n'):
            if _line.strip() == '' : continue
            _indent_space:int = ' '*(indent)
            if (re.match(ToolBox_REGEX_Patterns.NOTE_LINE, _line, re.IGNORECASE) and (_is_in_stream == False)):
                if include_notes == True:
                    _contains_pre_note = True
                    _temp_string += f"{_indent_space}{_line.strip()}\n"
                continue
            if (re.match(ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE, _line, re.IGNORECASE) and (_is_in_stream == False)):
                if (include_notes == True) and (_contains_pre_note == True):
                    _temp_string += '\n'
                _is_in_stream = True
                _temp_string += f"{_indent_space}{_line.strip()}\n"
                continue
            if (re.search(ToolBox_REGEX_Patterns.IWS_JOIN_LINE, _line, re.IGNORECASE) and (_is_in_stream == True)):
                _temp_string += f"{_indent_space}{_line.strip()}\n"
                _is_in_join_area = True
                continue
            if (re.search(ToolBox_REGEX_Patterns.IWS_FOLLOWS_LINE, _line, re.IGNORECASE) and (_is_in_stream == True)):
                _temp_string += _indent_space+(' ' if _is_in_join_area == True else '')+f"{_line.strip()}\n"
                continue
            if (re.search(ToolBox_REGEX_Patterns.IWS_ENDJOIN_LINE, _line, re.IGNORECASE) and (_is_in_stream == True)):
                _temp_string += f"{_indent_space}{_line.strip()}\n"
                _is_in_join_area = False
                continue
            if (re.match(ToolBox_REGEX_Patterns.IWS_STREAM_EDGE_LINE, _line, re.IGNORECASE) and (_is_in_stream == True)):
                _temp_string += f"{_indent_space}{_line.strip()}\n"
                if (include_jobs == True):
                    _job_nodes = [_c for _c in self.children if _c.node_type == ToolBox_Entity_Types.IWS_JOB]
                    if (len(_job_nodes) >= 1):
                        for _child_node in self.children:
                            print (_child_node.name)
                            if ((isinstance(_child_node, ToolBox_IWS_IWS_Obj_Node)) and(_child_node.node_type == ToolBox_Entity_Types.IWS_JOB)):
                                _temp_string += _child_node.format_as_Job(indent = indent)
                                _temp_string += "\n\n"
                continue
            if (re.match(ToolBox_REGEX_Patterns.IWS_STREAM_END_LINE, _line, re.IGNORECASE) and (_is_in_stream == True)):
                if include_end == True:
                    _temp_string += f"{_indent_space}{_line.strip()}\n"
                _is_in_stream = False
                continue
            # All else fails, add the line.
            _temp_string += f"{_indent_space}{_line.strip()}\n"
        return _temp_string
            

    def format_as_Job (self, indent:int = 0, include_notes:bool = True) -> str:
        """Returns the Node text formated as an IWS Job definition."""
        _temp_string = """"""
        _is_in_job_area:bool = False
        _is_in_join_area:bool = False
        for _line in self._modified_file_text.split('\n'):
            _indent_space:int = ' '*(indent+(1 if _is_in_job_area else 0))
            if (re.match(ToolBox_REGEX_Patterns.NOTE_LINE, _line, re.IGNORECASE) and (_is_in_job_area == False)):
                _temp_string += f"{_indent_space}{_line.strip()}\n"
                continue
            if (re.match(ToolBox_REGEX_Patterns.IWS_JOB_START_LINE, _line, re.IGNORECASE) and (_is_in_job_area == False)):
                _is_in_job_area = True
                _temp_string += f"{_indent_space}{_line.strip()}\n"
                continue
            if (re.search(ToolBox_REGEX_Patterns.IWS_JOIN_LINE, _line, re.IGNORECASE) and (_is_in_job_area == True)):
                _temp_string += f"{_indent_space}{_line.strip()}\n"
                _is_in_join_area = True
                continue
            if (re.search(ToolBox_REGEX_Patterns.IWS_FOLLOWS_LINE, _line, re.IGNORECASE) and (_is_in_job_area == True)):
                _temp_string += _indent_space+(' ' if _is_in_join_area == True else '')+f"{_line.strip()}\n"
                continue
            if (re.search(ToolBox_REGEX_Patterns.IWS_ENDJOIN_LINE, _line, re.IGNORECASE) and (_is_in_job_area == True)):
                _temp_string += f"{_indent_space}{_line.strip()}\n"
                _is_in_join_area = False
                continue
            if (re.search(ToolBox_REGEX_Patterns.BLANK_LINE, _line, re.IGNORECASE) and (_is_in_job_area == True)):
                _is_in_job_area = False
            #All else fails, add the line.
            _temp_string += f"{_indent_space}{_line.strip()}\n"
        return _temp_string
    
    @ToolBox_Decorator
    def format_as_Follows(self, indent:int = 0):
        _temp_string = """"""
        _is_in_job_area:bool = False
        _is_in_join_area:bool = False
        for _line in self._modified_file_text.split('\n'):
            _indent_space:int = ' '*(indent+(1 if _is_in_job_area else 0))
            if (re.search(ToolBox_REGEX_Patterns.IWS_FOLLOWS_LINE, _line, re.IGNORECASE) and (_is_in_job_area == True)):
                _temp_string += _indent_space+(' ' if _is_in_join_area == True else '')+f"{_line.strip()}\n"
                #All else fails, add the line.
            _temp_string += f"{_indent_space}{_line.strip()}\n"
        return _temp_string

