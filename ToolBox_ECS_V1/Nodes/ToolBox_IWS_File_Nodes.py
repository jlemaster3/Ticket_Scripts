#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import os, copy, re
from datetime import datetime
from typing import Any, Optional, TYPE_CHECKING
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Data_Silo import ToolBox_Data_Silo_Manager
from ToolBox_ECS_V1.Nodes.ToolBox_Base_File_Node import ToolBox_ECS_File_Node
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import (
    ToolBox_Entity_Types,
    ToolBox_REGEX_Patterns, 
    ToolBox_Struct_IWS_Stream,
    ToolBox_Struct_IWS_Job,
    ToolBox_Struct_Entity_Relationships
)
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Utils import(
    gen_uuid_key
)
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Formatters import (
    ToolBox_line_score_data,
    ToolBox_REGEX_text_score_evaluator
)
from ToolBox_ECS_V1.Nodes.ToolBox_IWS_OBJ_Nodes import ToolBox_IWS_Obj_Node

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

class ToolBox_IWS_JIL_File_Node (ToolBox_ECS_File_Node):
    """Extends from ToolBox_ECS_File_Node.

    Generic IWS Object node, handles all information about standard IWS objects.
    Handles basic Parent-Child relasionships like:
    
    All children foudn under this node would represent ownership of all shild nodes,
    and only represents half the hyerarchy and structure of the Node Tree.
    """
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    dataSilo:ToolBox_Data_Silo_Manager
    
    #------- private properties -------#
    
    _source_file_text:str|None
    _modified_file_text:str|None
    _modified_line_scores:list[ToolBox_line_score_data]
    _job_stream_keys:list[str]
    _job_keys:list[str]

    #------- Initialize class -------#

    def __init__(
        self,
        source_file_path:str,
        root_path:str|None = None,
        parent_entitity:ToolBox_ECS_Node|None = None,
        initial_data:dict[str,Any]|None=None
    ) :
        super().__init__(
            source_file_path = source_file_path,
            root_path = root_path,
            parent_entitity = parent_entitity,
            initial_data = initial_data
        )
        self.dataSilo = ToolBox_Data_Silo_Manager().get_instance()
        self._node_type = ToolBox_Entity_Types.FILE_JIL
        self._source_file_text = None
        self._modified_file_text = None
        self._modified_line_scores = []
        self._job_stream_keys = []
        self._job_keys = []

    #-------public Getter & Setter methods -------#

    @property
    def job_stream_nodes (self) -> list[ToolBox_IWS_Obj_Node]:
        """Returns a list of Job Stream nodes linked to this file."""
        _holder = []
        for _k in self._job_stream_keys:
            _node = self.dataSilo.get(_k)
            if ((_node is not None) and 
                isinstance(_node, ToolBox_IWS_Obj_Node) and
                _node.node_type == ToolBox_Entity_Types.IWS_JOB_STREAM
            ):
                _holder.append(_node)
        return _holder
    
    @property
    def job_nodes (self) -> list[ToolBox_IWS_Obj_Node]:
        """Returns a list of Job nodes linked to this file."""
        _holder = []
        for _k in self._job_keys:
            _node = self.dataSilo.get(_k)
            if ((_node is not None) and 
                isinstance(_node, ToolBox_IWS_Obj_Node) and
                _node.node_type == ToolBox_Entity_Types.IWS_JOB
            ):
                _holder.append(_node)
        return _holder
    
    @property
    def children (self) -> list[ToolBox_ECS_Node]:
        """Returns the current list of Children Nodes."""
        _holder:list[ToolBox_ECS_Node] = []
        for _key in self._children_keys + self._job_stream_keys + self._job_keys:
            if self.dataSilo[_key] not in _holder:
                _holder.append(self.dataSilo[_key])
        return _holder
    

    #------- Public Methods -------#
    @ToolBox_Decorator
    def add_child(self, child: ToolBox_ECS_Node|str):
        _child:ToolBox_ECS_Node|None = child if isinstance(child, ToolBox_ECS_Node) else self.dataSilo.get(child) if isinstance(child, str) else None
        if _child is not None:
            if isinstance(_child, ToolBox_IWS_Obj_Node) and _child.node_type == ToolBox_Entity_Types.IWS_JOB_STREAM:
                self.add_job_stream_node(_child)
            elif isinstance(_child, ToolBox_IWS_Obj_Node) and  _child.node_type == ToolBox_Entity_Types.IWS_JOB:
                self.add_job_node(_child)
            else:
                super().add_child(child = child)

    @ToolBox_Decorator
    def add_job_stream_node (self, node:ToolBox_IWS_Obj_Node):
        """Add a Job Stream node to list of links"""
        if (node.node_type == ToolBox_Entity_Types.IWS_JOB_STREAM and 
            node.id_key not in self._job_stream_keys
        ):
            self._job_stream_keys.append(node.id_key)

    @ToolBox_Decorator
    def add_job_node (self, node:ToolBox_IWS_Obj_Node):
        """Add a Job node to list of links"""
        if (node.node_type == ToolBox_Entity_Types.IWS_JOB and 
            node.id_key not in self._job_keys
        ):
            self._job_keys.append(node.id_key)
            

    @ToolBox_Decorator
    def open_file (self, quite_logging:bool=True, enable_post_porcesses:bool=True, skip_duplicates=False):
        """Opens teh Jil file and loads the data as Node objects."""
        if self._is_open != True:
            try:
                _holder = None
                with open(self.sourceFilePath, "r", encoding="utf-8") as f:
                    _holder = copy.deepcopy(f.read())
                if (_holder is not None):
                    if (quite_logging != True) : self.log.info (f"Opening source file : '{self.relFilePath}'")
                    self._source_file_text = _holder
                    self._modified_file_text = _holder
                    self._is_open = True
                    self._has_changed = False
                else:
                    self.log.warning (f"Unable to read file contents : '{self.relFilePath}'")
                    self._source_file_text = None
                    self._modified_file_text = None
                    self._is_open = False
                    self._has_changed = False
            except BufferError as errmsg:
                self.log.warning (f"Unable to open file : '{self.relFilePath}'", data = errmsg)
                self._source_file_text = None
                self._modified_file_text = None
                self._is_open = False
                self._has_changed = False
            except FileNotFoundError as errmsg:
                self.log.error (f"File not found : '{self.relFilePath}'")
                self._source_file_text = None
                self._modified_file_text = None
                self._is_open = False
                self._has_changed = False
            except Exception as e:
                self.log.warning(f"An unexpected error occurred while reading '{self.sourceFilePath}': {e}")
                self._source_file_text = None
                self._modified_file_text = None
                self._is_open = False
                self._has_changed = False
        if (enable_post_porcesses == True) and (self._is_open == True):
            self.split_source_text_to_nodes(
                source_text= self._source_file_text,
                quite_logging=quite_logging
                )
    
    @ToolBox_Decorator
    def close_file (self, quite_logging:bool=True):
        """Closes current instance of the file, clearing all temporary changes if not saved."""
        if self._is_open == True:
            if (quite_logging != True) : self.log.info (f"Closing source file : '{self.relFilePath}'")
            self._is_open = False
            self._source_file_text = None
            self._modified_file_text = None
            self._modified_line_scores = []
            self._has_changed = False
    
    @ToolBox_Decorator
    def save_File (self, outputFolder:str, rename:str|None=None, useRelPath:bool=False,  quite_logging:bool=True, skip_unchanged:bool=False):
        """Saves teh current modifications of teh file to the target location."""
        if self._has_changed != True and skip_unchanged == True:
            if (quite_logging != True) : self.log.info (f"File : '{self.relFilePath}' has not been edited, skipping save.")
            return
        from ToolBox_ECS_V1.Nodes.ToolBox_IWS_OBJ_Nodes import ToolBox_IWS_Obj_Node
        _outputPath = os.path.join(outputFolder,self.relPath) if useRelPath == True else outputFolder
        os.makedirs(_outputPath, exist_ok=True)
        _filename = rename if rename != None else self.name
        _outputFilePath = os.path.join (_outputPath, f"{_filename}.{self.foramt}")
        if os.path.exists (_outputFilePath):
            os.remove(_outputFilePath)
        #try:
        _file_text:str|None = None
        if len(self.job_stream_nodes) >= 1:
            _file_text = ""
            _curr_stream_counter = 0
            for _node in self.job_stream_nodes:
                if _curr_stream_counter >= 1:
                    _file_text += '\n\n'
                _stream_text = _node.format_as_Job_Stream(
                    indent = 0,
                    include_notes = True,
                    include_jobs = True,
                    include_end = True
                )
                if _stream_text:
                    _file_text += f'{_stream_text}\n'
                _curr_stream_counter += 1
        else:
            _file_text = self._modified_file_text if self._modified_file_text is not None else None
        if isinstance(_file_text, str) and _file_text != "":
            with open(_outputFilePath, "w") as output_file:
                output_file.write(_file_text)
            if (quite_logging != True) : self.log.info (f"Saved file : '{self.relFilePath}' as file : '{_outputFilePath}'")
        else:
            self.log.error (f"Unable to save file expecting '{self.relFilePath}' to be tpye of literal string, got : ", data=_file_text)
        #except SystemError as se :
        #    self.log.error (f"Unable to save file : 'SystemError' : ", data = se)
        #except IOError as ioe:
        #    self.log.error (f"Error saving file : 'IOError' :", data = ioe)
    
    @ToolBox_Decorator
    def split_source_text_to_nodes (self, source_text:str|None=None, quite_logging:bool=True):
        if (quite_logging != True) : self.log.debug(f"Decoding IWS configuration text from source file : '{self.relFilePath}' to Node Objects")
        if self._is_open == True and isinstance(self._modified_file_text,str):
            _source_text = source_text if source_text is not None else self._modified_file_text
            _lines:list[str] = self._modified_file_text.splitlines()
            _score_evals = ToolBox_REGEX_text_score_evaluator ( 
                source_text = _source_text,
                filter_patterns = ['IWS', 'LINE'],
                filter_AnyOrAll = 'ANY'
                )
            _stream_start_scores = _score_evals.get_scores_by_REGEX_Pattern_name(ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE.name)
            _last_end_index:int = -1
            _stream_counter:int = 0
            _job_counter:int = 0
            _total_counter:int = 0
            for _js_idx in range (len(_stream_start_scores)):
                _js_line_data = _stream_start_scores[_js_idx]
                _js_ws = _js_line_data.highest_scoring_results['workstation'] or None
                _js_f = _js_line_data.highest_scoring_results['folder'] or None
                _js_name = _js_line_data.highest_scoring_results['stream'] or None
                _js_key_string = f"{self._source_file_path}|{_js_ws}{_js_f}{_js_name}.@"
                _js_key_id = gen_uuid_key(_js_key_string)
                _js_new_node = ToolBox_IWS_Obj_Node(
                    id_key = _js_key_id,
                    name= _js_name,
                    object_type = ToolBox_Entity_Types.IWS_JOB_STREAM,
                    parent_entitity= None,
                    initial_data = None
                )
                _js_new_node.sourceFile_Path = self.sourceFilePath
                _js_new_node.sourceFile_Object = self
                
                if _js_idx != 0:
                    _start_index = _js_line_data.source_line_index if _last_end_index == -1 else _last_end_index
                else:
                    _start_index = 0
                _last_line_index:int = _stream_start_scores[_js_idx+1].source_line_index if _js_idx < len(_stream_start_scores)-1 else len(_lines)
                _closest_edge = _score_evals.get_closest_to_pattern_and_index(ToolBox_REGEX_Patterns.IWS_STREAM_EDGE_LINE.name, _js_line_data.source_line_index)
                _closest_end = _score_evals.get_closest_to_pattern_and_index(ToolBox_REGEX_Patterns.IWS_STREAM_END_LINE.name, _last_line_index)
                _stream_text_block:list[str] = copy.deepcopy(_lines[_start_index : _closest_edge.source_line_index+1]) if _closest_edge is not None else _lines[_start_index : _closest_end.source_line_index+1] if _closest_end is not None else _lines[_start_index: ]
                if _closest_end is not None and _closest_end.source_line_index > _js_line_data.source_line_index:
                    _last_end_index = max(_last_end_index, _closest_end.source_line_index+1)
                    _stream_text_block.append(_closest_end.source_line_text)
                else:
                    _last_end_index = max(_last_end_index, len(_lines))
                _js_new_node.sourceFile_Text = '\n'.join(_stream_text_block)
                self.dataSilo.append_node(_js_new_node)
                self._job_stream_keys.append(_js_new_node.id_key)
                _stream_counter += 1
                if (quite_logging != True) : self.log.debug (f"[{_stream_counter}|0] Adding node [{_js_new_node.id_key}] [{_js_new_node.node_type}] - '{_js_new_node.full_path}'")

                if (_closest_edge is not None and
                    _js_line_data.source_line_index <_closest_edge.source_line_index < _last_line_index - 1
                ):
                    _job_start_scores = _score_evals.get_patterns_between_indices(ToolBox_REGEX_Patterns.IWS_JOB_START_LINE.name, _closest_edge.source_line_index, _last_end_index)
                    _last_job_stop_line_index:int|None = None
                    for _j_idx in range(len(_job_start_scores)):
                        _j_line_data = _job_start_scores[_j_idx]
                        _j_start_line_index = _last_job_stop_line_index if _last_job_stop_line_index is not None else _j_line_data.source_line_index 
                        _j_end_line_index = _job_start_scores[_j_idx+1].source_line_index if _j_idx < len(_job_start_scores)-1 else _last_end_index - 1
                        _blank_line_scores = _score_evals.get_patterns_between_indices(ToolBox_REGEX_Patterns.BLANK_LINE.name, _j_start_line_index, _j_end_line_index)
                        _first_blank_line_ids = min([_idx.source_line_index for _idx in _blank_line_scores if _idx.source_line_index > _j_line_data.source_line_index ])
                        _job_text_block = copy.deepcopy(_lines[_j_start_line_index:_first_blank_line_ids])
                        if (_last_job_stop_line_index is None) or (_first_blank_line_ids > _last_job_stop_line_index):
                            _last_job_stop_line_index = _first_blank_line_ids
                        _j_ws = _j_line_data.highest_scoring_results['workstation'] or None
                        _j_f = _j_line_data.highest_scoring_results['folder'] or None
                        _j_name = _j_line_data.highest_scoring_results['job'] or None
                        _j_alias = _j_line_data.highest_scoring_results['alias'] or None
                        if _j_alias is not None:
                            _j_key_string = f"{self._source_file_path}|{_j_ws}{_j_f}{_js_name}.{_j_alias}"
                        else:
                            _j_key_string = f"{self._source_file_path}|{_j_ws}{_j_f}{_js_name}.{_j_name}"
                        _j_key_id = gen_uuid_key(_j_key_string)
                        _j_new_node = ToolBox_IWS_Obj_Node(
                            id_key = _j_key_id,
                            name=_j_name,
                            object_type = ToolBox_Entity_Types.IWS_JOB,
                            parent_entitity= _js_new_node,
                            initial_data = None
                        )
                        _j_new_node._node_type = ToolBox_Entity_Types.IWS_JOB
                        _j_new_node.sourceFile_Path = self.sourceFilePath
                        _j_new_node.sourceFile_Object = self
                        _j_new_node.sourceFile_Text = '\n'.join(_job_text_block)
                        self.dataSilo.append_node(_j_new_node)
                        self._job_keys.append(_j_new_node.id_key)
                        _js_new_node.add_child(_j_new_node)
                        _total_counter +=1
                        if (quite_logging != True) : self.log.debug (f"[{_stream_counter}|{_job_counter}] Adding node [{_j_new_node.id_key}] [{_j_new_node.node_type}] - '{_j_new_node.full_path}'")
            if (quite_logging != True) : self.log.info (f"Added [{_total_counter}] Nodes | [{_stream_counter}] Streams | [{_job_counter}] Jobs")
        if (quite_logging != True) : self.log.blank("-"*100)

    @ToolBox_Decorator
    def get_Job_Stream_Start_lines (self) -> list[tuple[int,str]]:
        _line_holder:list[tuple[int,str]] = []
        if self._modified_file_text is not None:
            for _line_idx, _line in enumerate(self._modified_file_text.splitlines()):
                if re.match(ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE, _line):
                    _line_holder.append((_line_idx,_line))
        return _line_holder
    
    @ToolBox_Decorator
    def get_Job_Stream_Edge_lines (self) -> list[tuple[int,str]]:
        _line_holder:list[tuple[int,str]] = []
        if self._modified_file_text is not None:
            for _line_idx, _line in enumerate(self._modified_file_text.splitlines()):
                if re.match(ToolBox_REGEX_Patterns.IWS_STREAM_EDGE_LINE, _line):
                    _line_holder.append((_line_idx,_line))
        return _line_holder
    
    @ToolBox_Decorator
    def get_Job_Stream_End_lines (self) -> list[tuple[int,str]]:
        _line_holder:list[tuple[int,str]] = []
        if self._modified_file_text is not None:
            for _line_idx, _line in enumerate(self._modified_file_text.splitlines()):
                if re.match(ToolBox_REGEX_Patterns.IWS_STREAM_END_LINE, _line):
                    _line_holder.append((_line_idx,_line))
        return _line_holder
    
    @ToolBox_Decorator
    def get_ON_RUNCYCLE_lines (self) -> list[tuple[int,str]]:
        _line_holder:list[tuple[int,str]] = []
        if self._modified_file_text is not None:
            for _line_idx, _line in enumerate(self._modified_file_text.splitlines()):
                if re.match(ToolBox_REGEX_Patterns.IWS_ON_RUNCYCLE_GROUP_LINE, _line):
                    _line_holder.append((_line_idx,_line))
                if re.match(ToolBox_REGEX_Patterns.IWS_ON_RUNCYCLE_FREQ_LINE, _line):
                    _line_holder.append((_line_idx,_line))
        return _line_holder
    
    @ToolBox_Decorator
    def get_Job_Start_lines (self) -> list[tuple[int,str]]:
        _line_holder:list[tuple[int,str]] = []
        if self._modified_file_text is not None:
            for _line_idx, _line in enumerate(self._modified_file_text.splitlines()):
                if re.match(ToolBox_REGEX_Patterns.IWS_JOB_START_LINE, _line):
                    _line_holder.append((_line_idx,_line))
        return _line_holder
    

    @ToolBox_Decorator
    def load_contents_as_entities (self, quite_logging:bool=True, enable_post_porcesses:bool=True, skip_duplicates=False):
        """Opens teh Jil file and loads the data as Node objects."""
        if self._is_open != True:
            try:
                _holder = None
                with open(self.sourceFilePath, "r", encoding="utf-8") as f:
                    _holder = copy.deepcopy(f.read())
                if (_holder is not None):
                    if (quite_logging != True) : self.log.info (f"Opening source file : '{self.relFilePath}'")
                    self._source_file_text = _holder
                    self._modified_file_text = _holder
                    self._is_open = True
                    self._has_changed = False
                else:
                    self.log.warning (f"Unable to read file contents : '{self.relFilePath}'")
                    self._source_file_text = None
                    self._modified_file_text = None
                    self._is_open = False
                    self._has_changed = False
            except BufferError as errmsg:
                self.log.warning (f"Unable to open file : '{self.relFilePath}'", data = errmsg)
                self._source_file_text = None
                self._modified_file_text = None
                self._is_open = False
                self._has_changed = False
            except FileNotFoundError as errmsg:
                self.log.error (f"File not found : '{self.relFilePath}'")
                self._source_file_text = None
                self._modified_file_text = None
                self._is_open = False
                self._has_changed = False
            except Exception as e:
                self.log.warning(f"An unexpected error occurred while reading '{self.sourceFilePath}': {e}")
                self._source_file_text = None
                self._modified_file_text = None
                self._is_open = False
                self._has_changed = False
        if (enable_post_porcesses == True) and (self._is_open == True):
            self.convert_text_to_entities ()


    @ToolBox_Decorator
    def convert_text_to_entities (self,
        quite_logging:bool=True
    ):        
        if (quite_logging != True) : self.log.debug(f"Decoding IWS configuration text from source file : '{self.relFilePath}' to Entities")  
        if self._is_open == True and self._modified_file_text is not None:
            self._modified_line_scores = []
            _curr_stream_entity:str|None = None
            _curr_job_entity:str|None = None
            _last_stream_entity:str|None = None
            _last_job_entity:str|None = None
            _curr_stream_data:dict[str,Any]|None = None
            _curr_job_data:dict[str,Any]|None = None
            _curr_stream_notes:list[str]|None = None
            _curr_stream_idx:int = 0
            _curr_job_idx:int = 0
            for _line_idx, _line_str in enumerate(self._modified_file_text.splitlines()):
                _line_score = ToolBox_line_score_data(
                    source_index= _line_idx,
                    source_text= _line_str,
                    filter_patterns=['IWS', 'LINE'],
                    filter_AnyOrAll= 'Any',
                    flags=[re.IGNORECASE]
                )
                self._modified_line_scores.append(_line_score)
                if (ToolBox_REGEX_Patterns.NOTE_LINE.name in _line_score.high_score_pattern_names):
                    if _curr_stream_notes is None:
                        _curr_stream_notes = []
                    _curr_stream_notes.append(_line_str)
                if (ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE.name in _line_score.high_score_pattern_names):
                    if _curr_stream_data is not None:
                        _last_stream_entity = _curr_stream_entity
                        _curr_stream_entity = self.dataSilo.create_entity(
                            key_id = _curr_stream_data['_hash'] or None,
                            components = _curr_stream_data
                        )
                        _curr_stream_data = None
                    if _curr_stream_data is None:
                        _curr_stream_data = {}
                        _curr_stream_idx += 1
                        _curr_job_idx = 0
                    for _result_list in _line_score.all_results.values():
                        for _score, _match in _result_list:
                            _found_results = _match.groupdict()
                            if all (_k in _found_results.keys() for _k in ['workstation', 'folder', 'stream']):
                                
                                _curr_stream_data['source_file'] = self.sourceFilePath
                                _curr_stream_data['stream_index_in_file'] = _curr_stream_idx
                                _curr_stream_data['obj_type'] = ToolBox_Entity_Types.IWS_JOB_STREAM
                                _curr_stream_data['workstation'] = _found_results['workstation'] or None
                                _curr_stream_data['folder'] = _found_results['folder'] or None
                                _curr_stream_data['name'] = _found_results['stream'] or None
                                _uuid_string = f"{self.sourceFilePath}|{_curr_stream_data['workstation']}{_curr_stream_data['folder']}{_curr_stream_data['name']}.@"
                                _curr_stream_data['_hash'] = gen_uuid_key(_uuid_string)
                                if _curr_stream_notes is not None:
                                    _curr_stream_data['pre_notes'] = '\n'.join(_curr_stream_notes)
                                    _curr_stream_notes = None
                if (ToolBox_REGEX_Patterns.IWS_JOB_START_LINE.name in _line_score.high_score_pattern_names):
                    if _curr_job_data is not None:
                        _last_job_entity = _curr_job_entity
                        _curr_job_entity = self.dataSilo.create_entity(
                            key_id = _curr_job_data['_hash'] or None,
                            components = _curr_job_data)
                        _curr_job_data = None
                    if _curr_job_data is None:
                        _curr_job_data = {}
                        _curr_job_idx += 1
                    for _result_list in _line_score.all_results.values():
                        for _score, _match in _result_list:
                            _found_results = _match.groupdict()
                            if all (_k in _found_results.keys() for _k in ['workstation', 'folder', 'job', 'alias']):
                                _curr_job_data['source_file'] = self.sourceFilePath
                                _curr_job_data['obj_type'] = ToolBox_Entity_Types.IWS_JOB
                                _curr_job_data['workstation'] = _found_results['workstation'] or None
                                _curr_job_data['folder'] = _found_results['folder'] or None
                                _curr_job_data['name'] = _found_results['job'] or None
                                _curr_job_data['alias'] = _found_results['alias'] or None
                                if (_curr_stream_data is not None and 
                                    'workstation' in _curr_stream_data.keys() and 
                                    'folder' in _curr_stream_data.keys() and
                                    'name' in _curr_stream_data.keys()
                                    ):
                                    _uuid_string = f"{self.sourceFilePath}|{_curr_job_data['workstation']}{_curr_job_data['folder']}{_curr_stream_data['name']}."
                                    _curr_job_data['parent_stream_key'] = _curr_stream_data['_hash']
                                    _curr_job_data['job_index_in_stream'] = _curr_job_idx
                                    if 'job_keys' not in _curr_stream_data.keys():
                                        _curr_stream_data['job_keys'] = []
                                else:
                                    _uuid_string = f"{self.sourceFilePath}|{_curr_job_data['workstation']}{_curr_job_data['folder']}"
                                _uuid_string += f"{_curr_job_data['alias']}" if _curr_job_data['alias'] is not None else f"{_curr_job_data['name']}"
                                
                                _curr_job_data['_hash'] = gen_uuid_key(_uuid_string)
                                if _curr_stream_data is not None and 'job_keys' in _curr_stream_data.keys():
                                    _curr_stream_data['job_keys'].append(_curr_job_data['_hash'])
                                if _curr_stream_notes is not None:
                                    _curr_job_data['pre_notes'] = '\n'.join(_curr_stream_notes)
                                    _curr_stream_notes = None
                if (ToolBox_REGEX_Patterns.BLANK_LINE.name in _line_score.high_score_pattern_names):
                    if _curr_job_data is not None:
                        _last_job_entity = _curr_job_entity
                        self.dataSilo.create_entity(
                            key_id = _curr_job_data['_hash'] or None,
                            components = _curr_job_data)
                        _curr_job_entity = None
                        _curr_job_data = None
                        

                if (ToolBox_REGEX_Patterns.IWS_STREAM_END_LINE.name in _line_score.high_score_pattern_names):
                    if _curr_stream_data is not None:
                        _last_stream_entity = _curr_stream_entity
                        self.dataSilo.create_entity(
                            key_id = _curr_stream_data['_hash'] or None,
                            components = _curr_stream_data
                        )
                        _curr_stream_entity = None
                        _curr_stream_data = None
                    if _curr_job_data is not None:
                        _last_job_entity = _curr_job_entity
                        self.dataSilo.create_entity(
                            key_id = _curr_job_data['_hash'] or None,
                            components = _curr_job_data)
                        _curr_job_entity = None
                        _curr_job_data = None
                        _curr_job_idx = 0
                
                        
    