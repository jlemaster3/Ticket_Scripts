#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import re
from typing import Any, Optional, TYPE_CHECKING, Literal
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Nodes.ToolBox_Base_Node import ToolBox_ECS_Node
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import ToolBox_Entity_Types, ToolBox_REGEX_Patterns
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Timezones import ToolBox_Timezone_Patterns
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Formatters import (
    ToolBox_line_score_data,
    ToolBox_REGEX_text_score_evaluator,
    ToolBox_REGEX_identify_patterns
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

class ToolBox_IWS_Obj_Node (ToolBox_ECS_Node):
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
    _modified_line_scores:list[ToolBox_line_score_data]
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
    _follows_source_node:ToolBox_IWS_Obj_Node|None
    _follows_type: Literal [ToolBox_Entity_Types.IWS_FOLLOW, ToolBox_Entity_Types.IWS_JOIN]|None
    
    #------- Initialize class -------#

    def __init__(
        self,
        id_key:str,
        object_type:ToolBox_Entity_Types,
        name:str|None = None,
        parent_entitity:ToolBox_ECS_Node|str|None=None, 
        initial_data:dict[str,Any]|None=None
    ) :
        super().__init__(
            id_key = id_key,
            name = name if isinstance(name,str) else 'N/A',
            node_type = object_type,
            parent_entitity = parent_entitity.id_key if isinstance(parent_entitity,ToolBox_ECS_Node) else parent_entitity if isinstance(parent_entitity,str) else None,
            initial_data = initial_data
        )
        self._iws_object_type = object_type
        self._source_file_text = None
        self._modified_file_text = None
        self._modified_line_scores = []
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
        self._modified_line_scores = []

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
        if (self._name is None) and (self._modified_file_text is not None):
            for _line in self._modified_file_text.splitlines():
                if self.node_type == ToolBox_Entity_Types.IWS_JOB_STREAM:
                    _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE, _line, re.IGNORECASE)
                    return f"{_IWS_path_parts.groupdict()['stream']}" if _IWS_path_parts is not None else 'None'
                if self.node_type == ToolBox_Entity_Types.IWS_JOB:
                    _IWS_path_parts = re.search(ToolBox_REGEX_Patterns.IWS_JOB_START_LINE, _line, re.IGNORECASE)
                    return f"{_IWS_path_parts.groupdict()['job']}" if _IWS_path_parts is not None else 'None'
            return 'None'
        else:
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
                return _IWS_path_parts.group(5) if isinstance(_IWS_path_parts, re.Match) and len(_IWS_path_parts.groups())>= 5 and (_IWS_path_parts.group(5).strip() != '')else None
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
            if self.parent_IWS_obj is not None:
                _path = f'{self.parent_IWS_obj.workstation}{self.parent_IWS_obj.folder}{self.parent_IWS_obj.name}.'
            else:
                _path = f"{self.workstation}{self.folder}"
            _path += self.alias if self.alias is not None else self.name
            return _path
        return ''
    
    @property
    def parent_IWS_obj (self) -> ToolBox_IWS_Obj_Node|None:
        """Returns the IWS_parent Object node if set."""
        return self.dataSilo.get(self._parent_key,None) if self._parent_key is not None else None
        
    #------- Methods / Functions -------#
        
    @ToolBox_Decorator
    def get_pattern_first_match (self, pattern:ToolBox_REGEX_Patterns) -> str|re.Match|None:
        """returns first matching results of from the current state of the object's text."""
        if  self._modified_file_text is not None:
            _results = re.search(pattern, self._modified_file_text, re.IGNORECASE | re.MULTILINE)
            if isinstance(_results, re.Match):
                return _results
            if isinstance(_results, str):
                return _results
        return None

    @ToolBox_Decorator
    def evaluate_modified_text (self):
        """Resets and evaluates the score values of from the current state of the object's text."""
        if self._modified_file_text is None:
            self._modified_line_scores = []
        else:
            self._modified_line_scores = []
            for _line_idx, _line_str in enumerate(self._modified_file_text.splitlines()):
                _line_score = ToolBox_line_score_data(
                    source_index= _line_idx,
                    source_text= _line_str,
                    filter_patterns=['IWS', 'LINE'],
                    filter_AnyOrAll= 'Any',
                    flags=[re.IGNORECASE]
                )
                self._modified_line_scores.append(_line_score)
    
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
        for _line_idx, _line in enumerate(self._modified_file_text.splitlines()):
            if _line.strip() == '' : continue
            _indent_space:str = ' '*(indent)
            if (re.search(ToolBox_REGEX_Patterns.NOTE_LINE, _line, re.IGNORECASE) and (_is_in_stream == False)):
                if include_notes == True:
                    if (_contains_pre_note == True):
                        _temp_string += '\n'
                    _temp_string += f"{_indent_space}{_line.strip()}"
                    _contains_pre_note = True
                continue
            if (re.search(ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE, _line, re.IGNORECASE) and (_is_in_stream == False)):
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
            if (re.search(ToolBox_REGEX_Patterns.IWS_STREAM_EDGE_LINE, _line, re.IGNORECASE) and (_is_in_stream == True)):
                _temp_string += f"\n{_indent_space}{_line.strip()}"
                if (include_jobs == True):
                    _job_nodes = [_c for _c in self.children if isinstance(_c, ToolBox_IWS_Obj_Node) and _c.node_type == ToolBox_Entity_Types.IWS_JOB]
                    if (len(_job_nodes) >= 1):
                        for _child_node in _job_nodes:
                            _job_text = _child_node.format_as_Job(indent = indent, include_notes=include_notes)
                            if _job_text is not None:
                                if _job_counter >= 1:
                                    _temp_string += ''    
                                _temp_string += f"{_job_text}"
                                _job_counter += 1
                continue
            if (re.search(ToolBox_REGEX_Patterns.IWS_STREAM_END_LINE, _line, re.IGNORECASE) and (_is_in_stream == True)):
                if include_end == True:
                    if _job_counter >= 1:
                        _temp_string += '\n'
                    _temp_string += f"\n{_indent_space}{_line.strip()}"
                _is_in_stream = False
                _job_counter = 0
                continue
            # All else fails, add the line.
            _temp_string += f"\n{_indent_space}{_line.strip()}"
        #_text_evaluator = ToolBox_REGEX_text_score_evaluator(_temp_string, filter_patterns=['IWS', 'LINE'], filter_AnyOrAll='any', flag_list=[re.IGNORECASE, re.MULTILINE])
        #self.log.blank(_text_evaluator.statistics)
        return _temp_string.strip()
            

    def format_as_Job (self, indent:int = 0, include_notes:bool = True) -> str|None:
        """Returns the Node text formated as an IWS Job definition."""
        _temp_string = """"""
        _is_in_job_area:bool = False
        _is_in_join_area:bool = False
        _contains_pre_note:bool = False
        if  self._modified_file_text is None:
            return None
        for _line in self._modified_file_text.splitlines():
            _indent_space:str = ' '*(indent+(1 if _is_in_job_area else 0))
            if (re.match(ToolBox_REGEX_Patterns.NOTE_LINE, _line, re.IGNORECASE) and (_is_in_job_area == False)):
                if include_notes == True:
                    if (_contains_pre_note == True):
                        _temp_string += '\n'
                    _temp_string += f"\n{_indent_space}{_line.strip()}"
                    _contains_pre_note = True
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
                continue
            #All else fails, add the line.
            _temp_string += f"\n{_indent_space}{_line.strip()}"
        return _temp_string

    
    @ToolBox_Decorator
    def get_line_by_pattern_name (self, pattern:ToolBox_REGEX_Patterns|list[ToolBox_REGEX_Patterns],
             auto_refresh_scores:bool=False
        ) -> list[tuple[int,tuple[int,int],int, str, str,Any]]:
        """Returns a list of Tuples : [ line index , sub string span , score , pattern name, parameter , value]"""
        if (self._modified_line_scores is None) or (auto_refresh_scores == True) or (
            len(self._modified_line_scores) == 0 and
            self._modified_file_text is not None and
            self._modified_file_text.strip() != ''
        ):
            self.evaluate_modified_text()
        _holder:list[tuple[int,tuple[int,int],int, str, str,Any]] = []
        for _score_data in self._modified_line_scores:
            if (_score_data.high_score_pattern_names is not None and 
                (pattern.name in _score_data.high_score_pattern_names if isinstance(pattern, ToolBox_REGEX_Patterns) else 
                any([_p.name in _score_data.high_score_pattern_names for _p in pattern]))
            ):
                _results = _score_data.get_all_Match_results()
                if _results is not None:
                    for  _pattern_name, _score , _groups in _results:
                        for _k, _v, _span in _groups:
                            _holder.append((_score_data.source_line_index, _span, _score, _pattern_name, _k, _v))
        
        def _sort_key(item: tuple[int,tuple[int,int],int, str, str,Any]):
            return (item[0], item[1][0])
        _sorted_holder = sorted(_holder, key = _sort_key)
        return _sorted_holder
    
    @ToolBox_Decorator
    def set_DEADLINE (self, 
            time_hhmm:int|str,
            time_zone:ToolBox_Timezone_Patterns|None = None,
            day_offset:int|str|None = None,
            auto_offse_days:bool = True
        ):
        """Adds, Edits or Removes teh Deadline settgin on the current Node.
        Default is to remove Deadline 'active = False'
        If 'target_line_index' is set to anything but 'None', the change will only occure on the line index that is set if it can be set on that line.
        """
        
        if (self._modified_line_scores is None):
            self.evaluate_modified_text()
        _mod_lines:list[str] = self._modified_file_text.splitlines() if self._modified_file_text is not None else []
        if len(_mod_lines) >= 1 and self._node_type == ToolBox_Entity_Types.IWS_JOB_STREAM:
            # if this node is a Job Stream Node:    
            _on_runcycle_lines = self.get_line_by_pattern_name([
                    ToolBox_REGEX_Patterns.IWS_ON_RUNCYCLE_GROUP_LINE,
                    ToolBox_REGEX_Patterns.IWS_ON_RUNCYCLE_FREQ_LINE,
                    ToolBox_REGEX_Patterns.IWS_ON_DATE_LINE,
                    ToolBox_REGEX_Patterns.IWS_ON_DAY_LINE,
                    ToolBox_REGEX_Patterns.IWS_DEADLINE
                ])
            self.log.debug (f"checking for deadline on Job Stream : '{self.full_path}', checking [{len(_on_runcycle_lines)}] lines.")
            _idx_checked:list[int] = []
            _line:str = _mod_lines[0]
            for _idx, _span, _score, _pattern_name, _key, _val in _on_runcycle_lines:
                if _mod_lines[_idx] != _line:
                    _line = _mod_lines[_idx]
                if _idx not in _idx_checked:
                    _idx_checked.append(_idx)
                    self.log.debug (f"Checking line [{_idx}] : '{_line}'")
                self.log.debug (f"Span: [{_span[0]}] - [{_span[1]}] | Score: [{_score}] | Pattern: {_pattern_name}| Key : '{_key}' | Value : '{_val}'")
                _parentheses_search = re.search(r'(\(.*\))', _line)
                _span_start = _parentheses_search.span()[0] if _parentheses_search is not None else 0
                _span_stop = _parentheses_search.span()[1] if _parentheses_search is not None else len(_line)
                if 'deadline' in _line.lower():
                    # line contains deadline values
                    pass
                else:
                    _first_time_match = re.search(r'(\d{4})',_line[_span_start:_span_stop], re.IGNORECASE|re.MULTILINE)
                    if _first_time_match is not None:
                        _search = _first_time_match.group(0)
                        _replace = f"{_search} DEADLINE {time_hhmm}"
                        if time_zone is not None:
                            _replace += f" TZ {time_zone}"
                        if day_offset is not None:
                            _day_val = int(str(day_offset).replace('+','').replace('-',''))
                            _replace += f" {'+' if int(_day_val) >= 0 else '-'}{_day_val} DAY{'S' if int(_day_val) >= 2 else''}"
                        _mod_lines[_idx] = _line.replace(_search, _replace)

        elif len(_mod_lines) >= 1 and self._node_type == ToolBox_Entity_Types.IWS_JOB:
            # if this node is a Job Stream Node:
            self.log.debug (f"Adding deadline to Job : '{self.full_path}'")
            _job_lines = self.get_line_by_pattern_name([
                ToolBox_REGEX_Patterns.IWS_RECOVERY_LINE,
                ToolBox_REGEX_Patterns.IWS_AT_SCHEDTIME,
                ToolBox_REGEX_Patterns.IWS_PLUS_MINUS_DAYS,
                ToolBox_REGEX_Patterns.IWS_UNTIL,
                ToolBox_REGEX_Patterns.IWS_JSUNTIL,
                ToolBox_REGEX_Patterns.IWS_EVERY,
                ToolBox_REGEX_Patterns.IWS_DEADLINE
            ])            
            _idx_checked:list[int] = []
            _line:str = _mod_lines[0]
            for _idx, _span, _score, _pattern_name, _key, _val in _job_lines:
                if _mod_lines[_idx] != _line:
                    _line = _mod_lines[_idx]
                if _idx not in _idx_checked:
                    _idx_checked.append(_idx)
                    self.log.debug (f"Checking line [{_idx}] : '{_line}'")
                self.log.debug (f"Span: [{_span[0]}] - [{_span[1]}] | Score: [{_score}] | Pattern: {_pattern_name}| Key : '{_key}' | Value : '{_val}'")

            _contains_deadline = [_p for _p in _job_lines if 'deadline' in _p[3].lower()]
            _contains_every = [_p for _p in _job_lines if 'every' in _p[3].lower()]
            _contains_until = [_p for _p in _job_lines if 'until' in _p[3].lower()]
            _contains_schedtime = [_p for _p in _job_lines if 'schedtime' in _p[3].lower()]
            
            if len(_contains_deadline) >= 1:
                #contains a deadline value, check and compare if shoudl be changed.
                self.log.warning (f"DEADLINE responce for foudn Deadline values mising and needs to be built")
                pass
            elif len(_contains_until) >= 1 :
                # contains 'until' values, add deadline infron of until
                self.log.warning (f"UNTIL and JSUNTIL responce is missing and needs to be built")
                pass
            elif len(_contains_every) >= 1:
                # contains 'every' values
                self.log.warning (f"EVERY and EVERYENDTIME responce is missing and needs to be built")
                pass
            elif len(_contains_schedtime) >= 1:
                # add after At time values line
                _edit_line_index = max([_ps[0] for _ps in _job_lines if _ps[3].upper() == ToolBox_REGEX_Patterns.IWS_AT_SCHEDTIME.name.upper()])
                _line = _mod_lines[_edit_line_index]
                _first_time_match = re.search(ToolBox_REGEX_Patterns.IWS_AT_SCHEDTIME,_line, re.IGNORECASE|re.MULTILINE)
                _date_match = re.search(ToolBox_REGEX_Patterns.IWS_PLUS_MINUS_DAYS,_line, re.IGNORECASE|re.MULTILINE)
                if _first_time_match is not None:
                    _job_time_hhmm = int(f"{_first_time_match.groupdict()['hh']}{_first_time_match.groupdict()['mm']}")
                    _day_offset:int = 0
                    _search = _line[_first_time_match.span()[0]:_first_time_match.span()[1]]
                    if _date_match is not None:
                        _search = _line[_first_time_match.span()[0]:_date_match.span()[1]]
                        _day_offset = int(_date_match.groupdict()['days']) if _date_match.groupdict()['days'] is not None and _date_match.groupdict()['days'].isdigit() else 0
                    _replace = f"{_search} DEADLINE {time_hhmm}"
                    if time_zone is not None:
                        _replace += f" TZ {time_zone}"
                    if _day_offset >= 1:
                        if day_offset is None:
                            day_offset = _day_offset
                    if _job_time_hhmm > int(time_hhmm):
                        if day_offset is None:
                            day_offset = 1
                        elif isinstance(day_offset,int):
                            day_offset += 1
                    if day_offset is not None:
                        _day_val = int(str(day_offset).replace('+','').replace('-',''))
                        _replace += f" {'+' if int(_day_val) >= 0 else '-'}{_day_val} DAY{'S' if int(_day_val) >= 2 else''}"    
                    _mod_lines[_edit_line_index] = _line.replace(_search, _replace)
            else:
                # add after recovery line
                _inster_index = max([_ps[0] for _ps in _job_lines if _ps[3].upper() == ToolBox_REGEX_Patterns.IWS_RECOVERY_LINE.name.upper()]) + 1
                _deadline_text = f"DEADLINE {time_hhmm}"
                if time_zone is not None:
                    _deadline_text += f" TZ {time_zone}"
                if day_offset is not None:
                    _day_val = int(str(day_offset).replace('+','').replace('-',''))
                    _deadline_text += f" {'+' if int(_day_val) >= 0 else '-'}{_day_val} DAY{'S' if int(_day_val) >= 2 else''}"
                _mod_lines.insert(_inster_index, _deadline_text)
        
        self._modified_file_text = '\n'.join (_mod_lines)
        if self._modified_file_text != self._source_file_text:
            self.sourceFile_Object._has_changed = True

            