#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import os, copy, random, re
from datetime import datetime
from typing import Any, Optional, TYPE_CHECKING
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Nodes.ToolBox_Base_File_Node import ToolBox_ECS_File_Node
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import (
    ToolBox_Entity_Types,
    ToolBox_REGEX_Patterns
)
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Utils import(
    gen_uuid_key
)

from ToolBox_ECS_V1.Nodes.ToolBox_IWS_OBJ_Nodes import ToolBox_IWS_IWS_Obj_Node

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
    
    #------- private properties -------#
    
    _source_file_text:str = None
    _modified_file_text:str = None
    
    _blocks:list[dict[str,str]] = None
    _node_dependancies:dict[str,dict[str,str]] = None
    
    #------- Initialize class -------#

    def __init__(
        self,
        source_file_path:str,
        root_path:str = None,
        parent_entitity:ToolBox_ECS_Node = None,
        initial_data:dict[str,Any]=None
    ) :
        super().__init__(
            source_file_path = source_file_path,
            root_path = root_path,
            parent_entitity = parent_entitity,
            initial_data = initial_data
        )
        self._node_type = ToolBox_Entity_Types.FILE_JIL,
        self._source_file_text = None
        self._modified_file_text = None
        self._blocks = []
        self._node_dependancies = {}

    #-------public Getter & Setter methods -------#


    #------- Public Methods -------#

    @ToolBox_Decorator
    def open_file (self, quite_logging:bool=False, skip_duplicates=False) -> str:
        """Opens teh Jil file and loads the data as Node objects."""
        if self._is_open != True:
            try:
                _holder = None
                with open(self.sourceFilePath, "r", encoding="utf-8") as f:
                    _holder = copy.deepcopy(f.read())
                if (_holder is not None):
                    if (quite_logging != True): self.log.debug (f"Opening source file : '{self.relFilePath}'")
                    self._source_file_text = _holder
                    self._is_open = True
                else:
                    self.log.debug (f"Unable to read file contents : '{self.relFilePath}'")
                    self._source_file_text = None
                    self._is_open = False
            except BufferError as errmsg:
                self.log.warning (f"Unable to open file : '{self.relFilePath}'", data = errmsg)
            except FileNotFoundError as errmsg:
                self.log.error (f"File not found : '{self.relFilePath}'")
            except Exception as e:
                self.log.warning(f"An unexpected error occurred while reading '{self.sourceFilePath}': {e}")
        if self._is_open == True:
            self.decode_source_text(skip_duplicates=skip_duplicates)
            self.convert_text_blocks_to_nodes()
        return self
    
    @ToolBox_Decorator
    def close_file (self, quite_logging:bool=True):
        """Closes current instance of the file, clearing all temporary changes if not saved."""
        if self._is_open == True:
            if (quite_logging != True): self.log.debug (f"Closing source file : '{self.relFilePath}'")
            self._is_open = False
            self._source_file_text = None
        return self
    
    @ToolBox_Decorator
    def save_File (self, outputFolder:str, rename:str=None, useRelPath:bool=False):
        """Saves teh current modifications of teh file to the target location."""
        from ToolBox_ECS_V1.Nodes.ToolBox_IWS_OBJ_Nodes import ToolBox_IWS_IWS_Obj_Node
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
                if isinstance(_node, ToolBox_IWS_IWS_Obj_Node) and (_node.node_type == ToolBox_Entity_Types.IWS_JOBSTREAM):
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
    
    @ToolBox_Decorator
    def decode_source_text (self, source_text:str=None, quite_logging:bool=True, skip_duplicates:bool = False):
        """breaks the source text into seprate to blocks for further processing, while capturing links between blocks."""
        from ToolBox_ECS_V1.ToolBox_Manager import ToolBox
        if (quite_logging != True) : self.log.blank("-"*100)
        if (quite_logging != True) : self.log.label(f"Decoding IWS Object contents from source file : '{self.relFilePath}'")
        _source_text = source_text if source_text is not None else self._source_file_text
        _last_text_block:dict[str,Any] = None
        _curr_text_block:dict[str,Any] = None
        _post_note_block:list[str] = []
        _curr_stream_block:dict[str,Any] = None
        _curr_job_block:dict[str,Any] = None
        _curr_stream_workstation:str = None
        _curr_stream_folder:str = None
        _curr_stream_name:str = None
        _curr_stream_id_key:str = None
        _curr_stream_full_path:str = None
        _curr_job_workstation:str = None
        _curr_job_folder:str = None
        _curr_job_name:str = None
        _curr_job_alias:str = None
        _curr_job_id_key:str = None
        _curr_job_full_path:str = None
        _total_stream_counter:int = 0
        _total_job_counter:int = 0
        _curr_stream_index:int = 0
        _curr_job_index:int = 0
        _curr_follows_index:int = 0

        self._blocks.clear()

        def finalize_block ():
            nonlocal _curr_text_block
            if _curr_text_block is not None:
                self._blocks.append(_curr_text_block)
                nonlocal _last_text_block
                _last_text_block = self._blocks[-1]
                _curr_text_block = None

        def create_new_block (blockType:ToolBox_Entity_Types, line:str):
            nonlocal _curr_text_block
            if _curr_text_block is not None:
                finalize_block()
            _curr_text_block ={
                "type":blockType,
                "notes": [],
                "content":[line.rstrip()],
                "data": {}
            }
            nonlocal _post_note_block
            _curr_text_block['notes'].extend(_post_note_block)
            _post_note_block = []

        def add_line_to_content (line:str, autoCreate:bool=False, blockType:ToolBox_Entity_Types=None):
            nonlocal _curr_text_block
            if (_curr_text_block is not None) and (_curr_text_block['content'] is not None):
                _curr_text_block['content'].append(line)
            elif autoCreate == True:
                create_new_block(blockType, line)        
        
        for _line  in _source_text.splitlines():
            # start of job stream definition line, closes current block if open, then starts a new block.
            # saves a pointer to the last stream block if found and sets the current stream block pointer to the current text block.
            if (re.match(ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE, _line, re.IGNORECASE)):
                create_new_block(ToolBox_Entity_Types.IWS_JOBSTREAM, _line)
                _curr_stream_block = _curr_text_block
                stream_parts_results = re.search(ToolBox_REGEX_Patterns.IWS_STREAM_PATH_PARTS, _line, re.IGNORECASE)
                if stream_parts_results:
                    _curr_stream_workstation = stream_parts_results.group(1)
                    _curr_stream_folder = stream_parts_results.group(2)
                    _curr_stream_name = stream_parts_results.group(3)
                    _curr_stream_full_path = f"{_curr_stream_workstation}{_curr_stream_folder}{_curr_stream_name}.@"
                    _curr_stream_key_string = f"{self._source_file_path}|{_curr_stream_full_path}"
                    _curr_stream_id_key = gen_uuid_key(_curr_stream_key_string)
                    if (skip_duplicates == False) and _curr_stream_id_key in ToolBox:
                        _rand_key = str(random.randrange(1000000000))
                        _curr_text_block['data']["random_key"] = _rand_key
                        _curr_stream_key_string = f"{self._source_file_path}|{_curr_stream_full_path}|{_rand_key}"
                        _rand_curr_stream_id_key = gen_uuid_key(_curr_stream_key_string)
                        self.log.warning (f"Key [{_curr_stream_id_key}] was already assigned in ECS system, generating random key: [{_rand_curr_stream_id_key}]")
                        _curr_stream_id_key = _rand_curr_stream_id_key
                    elif skip_duplicates == True:
                        continue
                    _curr_text_block['data']['id_key'] = _curr_stream_id_key
                    _curr_text_block['data']['key_string'] = _curr_stream_key_string
                    _curr_text_block['data']['full_path'] = _curr_stream_full_path
                    _curr_text_block['data']['stream_order_index'] = _curr_stream_index
                    _total_stream_counter += 1
                    _curr_stream_index += 1
                continue
            # Marks a line as a FOLLOWS line and marks it for being created as a seprate node.
            if re.match(ToolBox_REGEX_Patterns.IWS_FOLLOWS_LINE, _line, re.IGNORECASE) and (_curr_text_block is not None) and ((_curr_stream_block is not None) or (_curr_job_block is not None)):
                _owning_block = _curr_text_block
                if (_owning_block is None) or (
                    ('data' not in _owning_block.keys()) or 
                    ('full_path' not in _owning_block['data'].keys()) or
                    ('id_kay' not in _owning_block['data'].keys())
                ): continue
                _follow_target_parts = re.search(ToolBox_REGEX_Patterns.IWS_FOLLOWS_LINE, _line, re.IGNORECASE)
                _follows_target_ws = _follow_target_parts.group(1)
                _follows_target_path = _follow_target_parts.group(2)
                _follows_target_stream = _follow_target_parts.group(3)
                _follows_target_job = _follow_target_parts.group(5) if _follow_target_parts.group(5) else _follow_target_parts.group(4)
                _target_full_path = None
                if _follow_target_parts.group(5) is not None:
                    _target_full_path = f"{_curr_stream_workstation}{_curr_stream_folder}{_curr_stream_name}.{_follows_target_job}"
                else:
                    _target_full_path = f"{_follows_target_ws}{_follows_target_path}{_follows_target_stream}.{_follows_target_job}"
                _follows_key_string = f"{self._source_file_path}|{_target_full_path}|{_owning_block['data']['full_path']}"
                _follows_id_key = gen_uuid_key(_curr_stream_key_string)
                _follows_block = {
                    "type":ToolBox_Entity_Types.IWS_FOLLOW,
                    "notes": [],
                    "content":[_line.rstrip()],
                    "data": {
                        'id_key' : _follows_id_key,
                        'key_string' : _follows_key_string,
                        'soure_key' : _target_full_path,
                        'target_key' : _owning_block['data']['id_key'],
                        'parent_path' : _owning_block['data']['full_path'],
                        'parent_key' : _owning_block['data']['id_key'],
                        'follow_order_index' : _curr_follows_index,
                    }
                }
                _curr_follows_index += 1
                self._blocks.append(_follows_block)
                continue
            # Edge line of the current Stream Block marked by ':' in source text.
            # Adds the line to the current block, then closes current block.
            if (re.match(ToolBox_REGEX_Patterns.IWS_STREAM_EDGE_LINE, _line, re.IGNORECASE)):
                add_line_to_content(_line)
                continue
            # Start of Job definition line, saves pointer to last Job def if found, and sets the current Job pointer
            if re.match(ToolBox_REGEX_Patterns.IWS_JOB_START_LINE, _line, re.IGNORECASE):
                create_new_block(ToolBox_Entity_Types.IWS_JOB, _line)
                _curr_job_block = _curr_text_block
                _job_parts_results = re.search(ToolBox_REGEX_Patterns.IWS_JOB_PATH_PARTS, _line, re.IGNORECASE)
                if _job_parts_results:
                    _curr_job_workstation = _job_parts_results.group(1)
                    _curr_job_folder = _job_parts_results.group(2)
                    _curr_job_name = _job_parts_results.group(3)
                    _curr_job_alias = _job_parts_results.group(5)
                    _curr_job_full_path = ''
                    if (_curr_job_workstation.upper() == _curr_stream_workstation.upper()) and (_curr_job_folder.upper() == _curr_stream_folder.upper()):
                        _curr_job_full_path += f"{_curr_stream_workstation}{_curr_stream_folder}{_curr_stream_name}."
                    else:
                        _curr_job_full_path += f"{_curr_job_workstation}{_curr_job_folder}"
                    _curr_job_full_path += _curr_job_alias if _job_parts_results.group(5) else _curr_job_name
                    _curr_job_key_string = f"{self._source_file_path}|{_curr_job_full_path}"
                    _curr_job_id_key = gen_uuid_key(_curr_job_key_string)
                    if (skip_duplicates == False) and _curr_job_id_key in ToolBox:
                        _rand_key = str(random.randrange(1000000000))
                        _curr_text_block['data']["random_key"] = _rand_key
                        _curr_job_key_string = f"{self._source_file_path}|{_curr_job_full_path}|{_rand_key}"
                        _rand_curr_job_id_key = gen_uuid_key(_curr_job_key_string)
                        self.log.warning (f"Key [{_curr_job_id_key}] was already assigned in ECS system, generating random key: [{_rand_curr_job_id_key}]")
                        _curr_job_id_key = _rand_curr_job_id_key
                    elif skip_duplicates == True:
                        continue
                    _curr_text_block['data']['id_key'] = _curr_job_id_key
                    _curr_text_block['data']['key_string'] = _curr_job_key_string
                    _curr_text_block['data']['full_path'] = _curr_job_full_path
                    _curr_text_block['data']['parent_path'] = _curr_stream_full_path
                    _curr_text_block['data']['parent_key'] = _curr_stream_id_key
                    _curr_text_block['data']['job_order_index'] = _curr_job_index
                    _total_job_counter += 1
                    _curr_job_index += 1
                continue
            # First blank line after the start of a job definition has been found.
            # close current block
            if (re.match(ToolBox_REGEX_Patterns.BLANK_LINE, _line, re.IGNORECASE) and
                (_curr_text_block is not None) and
                ('type' in _curr_text_block.keys()) and
                (_curr_text_block['type'].upper() == ToolBox_Entity_Types.IWS_JOB.value.upper())):
                finalize_block()
                _curr_job_workstation = None
                _curr_job_folder = None
                _curr_job_name = None
                _curr_job_alias = None
                _curr_job_id_key = None
                _curr_job_full_path = None
                _curr_job_index = 0
                continue
            # End of current Job Stream block, will close out current block if the current block is a job or the current job stream.
            # will add current line to last known Strem block.
            if (re.match(ToolBox_REGEX_Patterns.IWS_STREAM_END_LINE, _line, re.IGNORECASE) and
                (_curr_stream_block is not None) and
                (_curr_stream_full_path is not None)):
                if (_curr_job_block is not None) and (_curr_text_block == _curr_job_block):
                    finalize_block()
                if (_curr_stream_block is not None) and (_curr_stream_block['content'] is not None):
                    _curr_stream_block['content'].append(_line)
                _curr_stream_workstation = None
                _curr_stream_folder = None
                _curr_stream_name = None
                _curr_stream_id_key = None
                _curr_stream_full_path = None
                _curr_job_workstation = None
                _curr_job_folder = None
                _curr_job_name = None
                _curr_job_alias = None
                _curr_job_id_key = None
                _curr_job_full_path = None
                _curr_stream_index = 0
                _curr_job_index = 0
                continue
            # Line is a Note line that starts with a '#', will add to current block if one is found.
            # If no block is found, will save for next block in file or appends to the last block if no more are found.
            if re.match(ToolBox_REGEX_Patterns.NOTE_LINE, _line, re.IGNORECASE):
                if (_curr_text_block is None):
                    _post_note_block.append(_line)
                continue
            # all else fails, add line to current block or notes for next block.
            if (_line.strip() != '') and (_curr_text_block is not None):
                add_line_to_content(_line)
            elif (_line.strip() != ''):
                _post_note_block.append(_line)
        # Add any post notes to last block in stack.
        if len(self._blocks) >= 1 and len(_post_note_block) >= 1:
            if '"post_notes"' not in self._blocks[-1].keys():
                self._blocks[-1]["post_notes"] = []
            self._blocks[-1]["post_notes"].extend(_post_note_block)
    
    @ToolBox_Decorator
    def convert_text_blocks_to_nodes (self, quite_logging:bool = True):
        """Adds stored nodes to ECS system"""
        from ToolBox_ECS_V1.ToolBox_Manager import ToolBox
        if len(self._blocks) >= 1:
            _stream_blocks = []
            _job_blocks = []
            _follow_blocks = []
            _other_blocks = []
            # split blocks into Groups for ordered processing
            for _idx in range(len(self._blocks)):
                _curr_block_type:ToolBox_Entity_Types = self._blocks[_idx]['type']
                if _curr_block_type == ToolBox_Entity_Types.IWS_JOBSTREAM:
                    _stream_blocks.append(self._blocks[_idx])
                elif _curr_block_type == ToolBox_Entity_Types.IWS_JOB:
                    _job_blocks.append(self._blocks[_idx])
                elif _curr_block_type == ToolBox_Entity_Types.IWS_FOLLOW:
                    _follow_blocks.append(self._blocks[_idx])
                else:
                    _other_blocks.append(self._blocks[_idx])
            if (quite_logging != True) : self.log.info(f"Total Stream Blocks Found : [{len(_stream_blocks)}]")
            if (quite_logging != True) : self.log.info (f"Total Job Blocks Found : [{len(_job_blocks)}]")
            if (quite_logging != True) : self.log.info (f"Total Follows Blocks Found : [{len(_follow_blocks)}]")
            if len(_other_blocks) >= 1:
                self.log (f"Total Blocks unable to filter : [{len(_other_blocks)}]")

            # Process all Job Stream Blocks
            for _streamBlock in _stream_blocks:
                _curr_stream_type:ToolBox_Entity_Types = _streamBlock['type']
                _curr_stream_notes:str = '\n'.join([_l.rstrip() for _l in _streamBlock['notes']]) if len(_streamBlock['notes']) != 0 else None
                _curr_stream_content:str = '\n'.join(_l.rstrip() for _l in _streamBlock['content'])    
                _curr_stream_data:dict[str,Any] = _streamBlock['data']
                _curr_stream_node = ToolBox_IWS_IWS_Obj_Node(
                    id_key = _curr_stream_data['id_key'] if 'id_key' in _curr_stream_data.keys() else None,
                    object_type = _curr_stream_type,
                    parent_entitity = None,
                    initial_data = _curr_stream_data
                )
                _curr_stream_node.sourceFile_Object = self
                _curr_stream_node.sourceFile_Text = (f"{_curr_stream_notes}\n\n"if _curr_stream_notes is not None else "")+ _curr_stream_content
                _curr_stream_post_notes:str = '\n'.join([_l.rstrip() for _l in _streamBlock['post_notes']]) if 'post_notes' in _streamBlock.keys() else None
                if _curr_stream_post_notes is not None:
                    _curr_stream_node.sourceFile_Text += f'\n\n{_curr_stream_post_notes}'
                _curr_stream_node.sourceFile_Object = self
                _curr_stream_node.sourceFile_Path = self.sourceFilePath    
                if (quite_logging != True) : self.log.debug (f"Adding Node :'{_curr_stream_node.object_type}' defined in file '{_curr_stream_node.sourceFile_Object.relFilePath}' as '{_curr_stream_node.full_path}'")#, data=_curr_stream_node._source_file_text.splitlines(), list_data_as_table=True, column_count=1 )
                ToolBox.insert_node_object(node = _curr_stream_node, overwrite_node = False)
            # Process all Job Stream Blocks
            for _jobBlock in _job_blocks:
                _curr_job_type:ToolBox_Entity_Types = _jobBlock['type']
                _curr_job_notes:str = '\n'.join([_l.rstrip() for _l in _jobBlock['notes']]) if len(_jobBlock['notes']) != 0 else None
                _curr_job_content:str = '\n'.join(_l.rstrip() for _l in _jobBlock['content'])    
                _curr_job_data:dict[str,Any] = _jobBlock['data']
                _curr_job_node = ToolBox_IWS_IWS_Obj_Node(
                    id_key = _curr_job_data['id_key'] if 'id_key' in _curr_job_data.keys() else None,
                    object_type = _curr_job_type,
                    parent_entitity = None,
                    initial_data = _curr_job_data
                )
                _curr_job_node.sourceFile_Object = self
                _curr_job_node.sourceFile_Text = (f"{_curr_job_notes}\n\n"if _curr_job_notes is not None else "")+ _curr_job_content
                _curr_job_post_notes:str = '\n'.join([_l.rstrip() for _l in _jobBlock['post_notes']]) if 'post_notes' in _jobBlock.keys() else None
                if _curr_job_post_notes is not None:
                    _curr_job_node.sourceFile_Text += f'\n\n{_curr_job_post_notes}'
                _curr_job_node.sourceFile_Path = self.sourceFilePath    
                if (quite_logging != True) : self.log.debug (f"Adding Node :'{_curr_job_node.object_type}' defined in file '{_curr_job_node.sourceFile_Object.relFilePath}' as '{_curr_job_node.full_path}'")#, data=_curr_job_node._source_file_text.splitlines(), list_data_as_table=True, column_count=1 )
                ToolBox.insert_node_object(node = _curr_job_node, overwrite_node = False)
                if ('parent_key' in _curr_job_data.keys()) and (_curr_job_data['parent_key'] is not None):
                    _source_key = _curr_job_data['parent_key']
                    if (_source_key is None):
                        self.log.warning (f"Source Key was not provided,  please set 'source_key' key in object.")
                    else:
                        _source_node = ToolBox[_source_key] if _source_key in ToolBox else None
                        if ((_source_node is not None) and (isinstance(_source_node, ToolBox_IWS_IWS_Obj_Node))):
                            _source_node.add_child(_curr_job_node)
                            if (quite_logging != True) : self.log.debug (f"Attaching Job node : '{_curr_job_node.deffined_path}' to its parent Job Stream node : '{_source_node.full_path if hasattr(_source_node, 'full_path') else _source_node.name}'")
                        else:
                            self.log.warning (f"Unable to find node for Source Key : '{_source_key}'")
