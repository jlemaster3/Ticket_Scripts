#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import re
from typing import Any, Optional, TYPE_CHECKING, Literal
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Nodes.ToolBox_Base_Node import ToolBox_ECS_Node
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import ToolBox_Entity_Types, ToolBox_REGEX_Patterns
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Formatters import (
    ToolBox_REGEX_text_score_evaluator
)
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
#   Classes
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
    _iws_object_type:ToolBox_Entity_Types
    _source_file_path:str
    _source_file_obj:ToolBox_IWS_JIL_File_Node
    _source_file_text:str|None
    _modified_file_text:str|None
    _notes:str|None
    _workstation:str|None
    _folder:str|None
    _alias: str|None
    _decription:str|None
    _draft:str|None
    _nop:str|None
    _priority:str|None
    _on_overlap:str|None
    _matching: str|None
    _freedays: str|None
    _valid_from:str|None
    _valid_to:str|None
    _time_zone:str|None
    _follows_source_key:str|None
    _follows_source_node:ToolBox_IWS_IWS_Obj_Node|None
    _follows_type: Literal [ToolBox_Entity_Types.IWS_FOLLOW, ToolBox_Entity_Types.IWS_JOIN]|None
    
    #------- Initialize class -------#

    def __init__(
        self,
        id_key:str,
        object_type:ToolBox_Entity_Types,
        name:str|None = None,
        parent_entitity:ToolBox_ECS_Node|None=None, 
        initial_data:dict[str,Any]|None=None
    ) :
        super().__init__(
            id_key = id_key,
            name = initial_data['name'] if isinstance(initial_data,dict) and 'name' in initial_data.keys() else name if name is not None else 'N/A',
            node_type = object_type,
            parent_entitity = parent_entitity, 
            initial_data = initial_data
        )
        self._iws_object_type = object_type
        self._source_file_text = None
        self._modified_file_text = None
        self._notes = None
        self._workstation = None
        self._folder = None
        self._alias = None
        self._decription = None
        self._draft = None
        self._nop = None
        self._priority = None
        self._on_overlap = None
        self._matching = None
        self._freedays = None
        self._valid_from = None
        self._valid_to = None
        self._time_zone = None
        self._follows_source_key = None
        self._follows_source_node = None
        self._follows_type = None

    def __str__ (self):
        return str(self.full_path)

    def __repr__(self):
        return f"{type(self)} (id_key:str = {self.id_key}, object_type:ToolBox_Entity_Types = {self.node_type},)"
    
    #-------public Getter & Setter methods -------#
    @property
    def id_key (self) -> str:
        """Returns assigned Job Name as stored in IWS."""
        return self._id_key
    
    @id_key.setter
    def id_key (self, value:str) :
        """Sets the value of the Job Name."""
        self._id_key = value

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
    def sourceFile_Text (self) -> str|None:
        """Returns assigned folder Path in IWS."""
        return self._source_file_text
    
    @sourceFile_Text.setter
    def sourceFile_Text (self, value:str) :
        """Sets the value of the folder Path in IWS."""
        self._source_file_text = value
        self._modified_file_text = self._source_file_text

    @property
    def workstation (self) -> str|None:
        """Returns assigned Job Stream Name as stored in IWS."""
        if self._workstation is None:
            if self.node_type == ToolBox_Entity_Types.IWS_JOB_STREAM and self._modified_file_text is not None:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE.value, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                if isinstance(_IWS_path_parts, re.Match):
                    return _IWS_path_parts.group(1)
                if isinstance(_IWS_path_parts, str):
                    return _IWS_path_parts
            if self.node_type == ToolBox_Entity_Types.IWS_JOB and self._modified_file_text is not None:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_JOB_START_LINE.value, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
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
    def folder (self) -> str|None:
        """Returns assigned folder Path in IWS."""
        if self._folder is None:
            if self.node_type == ToolBox_Entity_Types.IWS_JOB_STREAM and self._modified_file_text is not None:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                if isinstance(_IWS_path_parts, re.Match):
                    return _IWS_path_parts.group(2)
                if isinstance(_IWS_path_parts, str):
                    return _IWS_path_parts
            if self.node_type == ToolBox_Entity_Types.IWS_JOB and self._modified_file_text is not None:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_JOB_START_LINE, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
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
            if self.node_type == ToolBox_Entity_Types.IWS_JOB_STREAM and self._modified_file_text is not None:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                return _IWS_path_parts.group(3) if _IWS_path_parts is not None else 'None'
            if self.node_type == ToolBox_Entity_Types.IWS_JOB and self._modified_file_text is not None:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_JOB_START_LINE, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                return _IWS_path_parts.group(3) if _IWS_path_parts is not None else 'None'
        return self._name
        
    @name.setter
    def name (self, value:str) :
        """Sets the value of the Object."""
        self._name = value
    
    @property
    def alias (self) -> str|None:
        """Returns assigned Object alias as stored in IWS."""
        if self._alias is None:
            if self.node_type == ToolBox_Entity_Types.IWS_JOB and self._modified_file_text is not None:
                _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_JOB_START_LINE, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
                return _IWS_path_parts.group(5) if isinstance(_IWS_path_parts, re.Match) and len(_IWS_path_parts.groups())>= 5 else None
        return self._alias
        
    @alias.setter
    def alias (self, value:str) :
        """Sets the value of the Object Alias."""
        self._alias = value

    @property
    def deffined_path (self) -> str:
        """Returns the Deffined path as set in source file, might differ from the Full Path seen in executed schedules."""
        if self.object_type == ToolBox_Entity_Types.IWS_JOB_STREAM:
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
        if self.object_type == ToolBox_Entity_Types.IWS_JOB_STREAM:
            return f"{self.workstation}{self.folder}{self.name}.@"
        if self.object_type == ToolBox_Entity_Types.IWS_JOB:
            _path = f"{self.workstation}{self.folder}"
            if self.parent is not None and isinstance(self._parent_entity, ToolBox_ECS_Node):
                _path += f'{self._parent_entity.name}.'                
            _path += self.alias if self.alias is not None else self.name
            return _path
        return ''
        
    #------- Methods / Functions -------#
        
    @ToolBox_Decorator
    def get_pattern_first_match (self, pattern:ToolBox_REGEX_Patterns) -> str|re.Match|None:
        """returns first matching results of from the current state of object text."""
        if  self._modified_file_text is not None:
            _results = re.search(pattern, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
            if isinstance(_results, re.Match):
                return _results
            if isinstance(_results, str):
                return _results
        return None

    @ToolBox_Decorator
    def format_as_Job_Stream (self, indent:int = 0, include_notes:bool = True, include_jobs:bool = True, include_end:bool=True) -> str|None:
        """Returns the Node text formated as an IWS Job Stream definition."""
        _temp_string = """"""
        _contains_pre_note:bool = False
        _is_in_stream:bool = False
        _is_in_join_area:bool = False
        _job_counter:int = 0
        if  self._modified_file_text is None:
            return None
        for _line in self._modified_file_text.splitlines():
            if _line.strip() == '' : continue
            _indent_space:str = ' '*(indent)
            if (re.match(ToolBox_REGEX_Patterns.NOTE_LINE, _line, re.IGNORECASE) and (_is_in_stream == False)):
                if include_notes == True:
                    if (_contains_pre_note == True):
                        _temp_string += '\n'
                    _temp_string += f"{_indent_space}{_line.strip()}"
                    _contains_pre_note = True
                continue
            if (re.match(ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE, _line, re.IGNORECASE) and (_is_in_stream == False)):
                if (include_notes == True) and (_contains_pre_note == True):
                    _temp_string += '\n'
                _is_in_stream = True
                _temp_string += f"\n{_indent_space}{_line.strip()}"
                continue
            if (re.search(ToolBox_REGEX_Patterns.IWS_JOIN_LINE, _line, re.IGNORECASE) and (_is_in_stream == True)):
                _temp_string += f"\n{_indent_space}{_line.strip()}"
                _is_in_join_area = True
                continue
            if (re.search(ToolBox_REGEX_Patterns.IWS_FOLLOWS_LINE, _line, re.IGNORECASE) and (_is_in_stream == True)):
                _temp_string += '\n'+_indent_space+(' ' if _is_in_join_area == True else '')+f"{_line.strip()}"
                continue
            if (re.search(ToolBox_REGEX_Patterns.IWS_ENDJOIN_LINE, _line, re.IGNORECASE) and (_is_in_stream == True)):
                _temp_string += f"\n{_indent_space}{_line.strip()}"
                _is_in_join_area = False
                continue
            if (re.match(ToolBox_REGEX_Patterns.IWS_STREAM_EDGE_LINE, _line, re.IGNORECASE) and (_is_in_stream == True)):
                _temp_string += f"\n{_indent_space}{_line.strip()}"
                if (include_jobs == True):
                    _job_nodes = [_c for _c in self.children if _c.node_type == ToolBox_Entity_Types.IWS_JOB]
                    if (len(_job_nodes) >= 1):
                        
                        for _child_node in self.children:
                            if ((isinstance(_child_node, ToolBox_IWS_IWS_Obj_Node)) and(_child_node.node_type == ToolBox_Entity_Types.IWS_JOB)):
                                _job_text = _child_node.format_as_Job(indent = indent)
                                if _job_text is not None:
                                    if _job_counter >= 1:
                                        _temp_string += '\n\n'    
                                    _temp_string += f"{_job_text}"
                                    _job_counter += 1

                continue
            if (re.match(ToolBox_REGEX_Patterns.IWS_STREAM_END_LINE, _line, re.IGNORECASE) and (_is_in_stream == True)):
                if include_end == True:
                    if _job_counter >= 1:
                        _temp_string += '\n'
                    _temp_string += f"\n{_indent_space}{_line.strip()}"
                _is_in_stream = False
                _job_counter = 0
                continue
            # All else fails, add the line.
            _temp_string += f"\n{_indent_space}{_line.strip()}"
        _text_evaluator = ToolBox_REGEX_text_score_evaluator(_temp_string, filter_patterns=['IWS', 'stream', 'LINE'], filter_AnyOrAll='any', flag_list=[re.IGNORECASE, re.MULTILINE])
        self.log.blank(_text_evaluator.statistics)
        return _temp_string
            

    def format_as_Job (self, indent:int = 0, include_notes:bool = True) -> str|None:
        """Returns the Node text formated as an IWS Job definition."""
        _temp_string = """"""
        _is_in_job_area:bool = False
        _is_in_join_area:bool = False
        if  self._modified_file_text is None:
            return None
        for _line in self._modified_file_text.splitlines():
            _indent_space:str = ' '*(indent+(1 if _is_in_job_area else 0))
            if (re.match(ToolBox_REGEX_Patterns.NOTE_LINE, _line, re.IGNORECASE) and (_is_in_job_area == False)):
                _temp_string += f"\n{_indent_space}{_line.strip()}"
                continue
            if (re.match(ToolBox_REGEX_Patterns.IWS_JOB_START_LINE, _line, re.IGNORECASE) and (_is_in_job_area == False)):
                _is_in_job_area = True
                _temp_string += f"\n{_indent_space}{_line.strip()}"
                continue
            if (re.search(ToolBox_REGEX_Patterns.IWS_JOIN_LINE, _line, re.IGNORECASE) and (_is_in_job_area == True)):
                _temp_string += f"\n{_indent_space}{_line.strip()}"
                _is_in_join_area = True
                continue
            if (re.search(ToolBox_REGEX_Patterns.IWS_FOLLOWS_LINE, _line, re.IGNORECASE) and (_is_in_job_area == True)):
                _temp_string += '\n'+_indent_space+(' ' if _is_in_join_area == True else '')+f"{_line.strip()}"
                continue
            if (re.search(ToolBox_REGEX_Patterns.IWS_ENDJOIN_LINE, _line, re.IGNORECASE) and (_is_in_job_area == True)):
                _temp_string += f"\n{_indent_space}{_line.strip()}"
                _is_in_join_area = False
                continue
            if (re.search(ToolBox_REGEX_Patterns.BLANK_LINE, _line, re.IGNORECASE) and (_is_in_job_area == True)):
                _is_in_job_area = False
            #All else fails, add the line.
            _temp_string += f"\n{_indent_space}{_line.strip()}"
        return _temp_string