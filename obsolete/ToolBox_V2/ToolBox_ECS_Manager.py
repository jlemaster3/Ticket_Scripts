#-------------------------------------------------
#   Imports
#-------------------------------------------------
import random, os, re, copy

from ToolBox_V2.ToolBox_logger import OutputLogger
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_JIL_File import ToolBox_IWS_JIL_File
from ToolBox_V2.ToolBox_DataTypes.ToolBox_ECS_Data_Nodes import (
    ToolBox_Entity_types, 
    ToolBox_REGEX_Patterns,
    ToolBox_ECS_Node,
    ToolBox_ECS_Node_IWS_Obj
)
from ToolBox_V2.ToolBox_DataTypes.ToolBox_ECS_Dependancy_Nodes import (
    ToolBox_ECS_Node_IWS_Dependancy
)
from ToolBox_V2.ToolBox_Utilities import (
    gen_uuid_key
)
from typing import Any, Optional, Dict

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

class ToolBox_Data_ECS_Manager:
    log = OutputLogger.get_instance()
    _instance = None
    _fileObjects:dict[str,object] = {}
    _nodeItems:dict[str, ToolBox_ECS_Node] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolBox_Data_ECS_Manager, cls).__new__(cls)
            cls._instance._nodeItems = {}
        return cls._instance
    
    @classmethod
    def get_instance(self) -> "ToolBox_Data_ECS_Manager":
        """Returns the singleton instance of OutputLogger."""
        return self._instance

    @ToolBox_Decorator
    def insert_node_object (self, node:ToolBox_ECS_Node, overwrite_node:bool = False):
        """Adds a premade node to the ESC node list"""
        if isinstance(node, ToolBox_ECS_Node):
            if (overwrite_node == False) and (node.id_key in self._nodeItems.keys()):
                self.log.warning(f" Unable to add Node to system, Node Key : [{node.id_key}] - '{node.name}' already exists.")
                return
            self._nodeItems[node.id_key] = node

    @ToolBox_Decorator
    def get_node_by_key(self, id_key: str) -> Optional[ToolBox_ECS_Node]:
        """Return entity by id_key if found, will return None if entity not found."""
        return self._nodeItems.get(id_key)    

    @ToolBox_Decorator
    def clear(self):
        """Clear all entities (useful for resetting tests)."""
        self._nodeItems.clear()

    @ToolBox_Decorator
    def import_file_list (self, file_list:list[Any]) :
        """Opens and imports *.Jil files from provided list"""
        for _file in file_list: 
            if isinstance(_file, ToolBox_IWS_JIL_File):
                _jil_file_obj = ToolBox_ECS_IWS_JIL_Parser(_file)
                if _jil_file_obj._source_file.relFilePath not in self._fileObjects.keys():
                    self._fileObjects[_jil_file_obj._source_file.relFilePath] = _jil_file_obj

    @ToolBox_Decorator
    def get_all_entities(self) -> list[ToolBox_ECS_Node]:
        """Return all entities in creation order."""
        return [_n for _n in self._nodeItems.values()]
    
    @ToolBox_Decorator
    def get_entities_by_name (self, name: str) -> Optional[list[ToolBox_ECS_Node]]:
        """Return a list of nodes found with names containing search term."""
        return [_n for _n in self._nodeItems if isinstance(_n, ToolBox_ECS_Node) and name.upper() in _n.name.upper()]    
    
    @ToolBox_Decorator
    def get_IWS_nodes_by_file (self) -> dict[str,list[ToolBox_ECS_Node]]:
        """Return all nodes seprate by importing file."""
        _holder:dict[str,list[ToolBox_ECS_Node]] = {}
        for _filePath in self._fileObjects.keys():
            if _filePath not in _holder.keys():
                _holder[_filePath] = [_n for _n in self._nodeItems.values() if isinstance(_n, ToolBox_ECS_Node_IWS_Obj) and (_filePath.upper() in _n.sourceFile_Path.upper())]
        return _holder
    
    @ToolBox_Decorator
    def get_IWS_Job_Stream_nodes (self) -> list[ToolBox_ECS_Node_IWS_Obj]:
        """Returns all loaded IWS Job Stream nodes as a list"""
        return [_n for _n in self._nodeItems if isinstance(_n, ToolBox_ECS_Node_IWS_Obj) and _n.node_type == ToolBox_Entity_types.IWS_JOBSTREAM]
    
    @ToolBox_Decorator
    def get_IWS_Job_nodes (self) -> list[ToolBox_ECS_Node_IWS_Obj]:
        """Returns all loaded IWS Job Stream nodes as a list"""
        return [_n for _n in self._nodeItems if isinstance(_n, ToolBox_ECS_Node_IWS_Obj) and _n.node_type == ToolBox_Entity_types.IWS_JOB]




#-------------------------------------------------
#   Parser Classes
#-------------------------------------------------

class ToolBox_ECS_IWS_JIL_Parser:
    log:OutputLogger = OutputLogger.get_instance()
    dataECS:ToolBox_Data_ECS_Manager = None
    #------- private properties -------#
    _source_file_path: str = None
    _source_file: ToolBox_IWS_JIL_File = None
    _source_text: str = None
    _blocks:list[dict[str,str]] = None
    _node_dependancies:dict[str,dict[str,str]] = None

    def __init__ (self, source_file:ToolBox_IWS_JIL_File):
        self.dataECS = ToolBox_Data_ECS_Manager.get_instance()
        self._source_file = source_file
        self._source_text = None
        self._blocks = []
        self._node_dependancies = {}    
        self.open_file()
        self.decode_source_text()
        self.convert_text_blocks_to_nodes()
    
    @ToolBox_Decorator
    def open_file (self):
        try:
            with open(self._source_file.sourceFilePath, 'r', encoding='utf8') as _file:
                self._source_text = _file.read()
        except FileNotFoundError:
            self.log.warning (f"Error: File not found at '{self._source_file.sourceFilePath}'")
        except UnicodeDecodeError:
            self.log.warning (f"Error: Could not decode file '{self._source_file.sourceFilePath}'. Try a different encoding.")
        except Exception as e:
            self.log.warning(f"An unexpected error occurred while reading '{self._source_file.sourceFilePath}': {e}")

    @ToolBox_Decorator
    def decode_source_text (self, source_text:str=None):
        """breaks the source text into seprate to blocks for further processing, while capturing links between blocks."""
        self.log.blank("-"*100)
        self.log.label(f"Decoding IWS Object contents from source file : '{self._source_file.relFilePath}'")
        _source_text = source_text if source_text is not None else self._source_text
        _last_text_block:dict[str,str] = None
        _curr_text_block:dict[str,str] = None
        _post_note_block:list[str] = []
        _curr_stream_block:dict[str,str] = None
        _curr_job_block:dict[str,str] = None
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

        def create_new_block (blockType:ToolBox_Entity_types, line:str):
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

        def add_line_to_content (line:str, autoCreate:bool=False, blockType:ToolBox_Entity_types=None):
            nonlocal _curr_text_block
            if (_curr_text_block is not None) and (_curr_text_block['content'] is not None):
                _curr_text_block['content'].append(line)
            elif autoCreate == True:
                create_new_block(blockType, line)        
        
        for _line  in _source_text.splitlines():
            # start of job stream definition line, closes current block if open, then starts a new block.
            # saves a pointer to the last stream block if found and sets the current stream block pointer to the current text block.
            if (re.match(ToolBox_REGEX_Patterns.IWS_STREAM_START_LINE, _line, re.IGNORECASE)):
                create_new_block(ToolBox_Entity_types.IWS_JOBSTREAM, _line)
                _curr_stream_block = _curr_text_block
                stream_parts_results = re.search(ToolBox_REGEX_Patterns.IWS_STREAM_PATH_PARTS, _line, re.IGNORECASE)
                if stream_parts_results:
                    _curr_stream_workstation = stream_parts_results.group(1)
                    _curr_stream_folder = stream_parts_results.group(2)
                    _curr_stream_name = stream_parts_results.group(3)
                    _curr_stream_full_path = f"{_curr_stream_workstation}{_curr_stream_folder}{_curr_stream_name}.@"
                    _curr_stream_key_string = f"{self._source_file._source_path}|{_curr_stream_full_path}"
                    _curr_stream_id_key = gen_uuid_key(_curr_stream_key_string)
                    if _curr_stream_id_key in self.dataECS._nodeItems.keys():
                        _rand_key = str(random.randrange(1000000000))
                        _curr_text_block['data']["random_key"] = _rand_key
                        _curr_stream_key_string = f"{self._source_file._source_path}|{_curr_stream_full_path}|{_rand_key}"
                        _rand_curr_stream_id_key = gen_uuid_key(_curr_stream_key_string)
                        self.log.warning (f"Key [{_curr_stream_id_key}] was already assigned in ECS system, generating random key: [{_rand_curr_stream_id_key}]")
                        _curr_stream_id_key = _rand_curr_stream_id_key
                    _curr_text_block['data']['id_key'] = _curr_stream_id_key
                    _curr_text_block['data']['key_string'] = _curr_stream_key_string
                    _curr_text_block['data']['full_path'] = _curr_stream_full_path
                    _curr_text_block['data']['stream_order_index'] = _curr_stream_index
                    _total_stream_counter += 1
                    _curr_stream_index += 1
                continue
            # Marks a line as a FOLLOWS line and marks it for being created as a seprate node.
            if re.match(ToolBox_REGEX_Patterns.IWS_FOLLOWS_LINE, _line, re.IGNORECASE):
                _owning_block = _curr_stream_block if _curr_job_block is None else _curr_job_block
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
                _follows_key_string = f"{self._source_file._source_path}|{_target_full_path}|{_owning_block['data']['full_path']}"
                _follows_id_key = gen_uuid_key(_curr_stream_key_string)
                _follows_block = {
                    "type":ToolBox_Entity_types.IWS_FOLLOW,
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
                create_new_block(ToolBox_Entity_types.IWS_JOB, _line)
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
                    _curr_job_key_string = f"{self._source_file._source_path}|{_curr_job_full_path}"
                    _curr_job_id_key = gen_uuid_key(_curr_job_key_string)
                    if _curr_job_id_key in self.dataECS._nodeItems.keys():
                        _rand_key = str(random.randrange(1000000000))
                        _curr_text_block['data']["random_key"] = _rand_key
                        _curr_job_key_string = f"{self._source_file._source_path}|{_curr_job_full_path}|{_rand_key}"
                        _rand_curr_job_id_key = gen_uuid_key(_curr_job_key_string)
                        self.log.warning (f"Key [{_curr_job_id_key}] was already assigned in ECS system, generating random key: [{_rand_curr_job_id_key}]")
                        _curr_job_id_key = _rand_curr_job_id_key
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
                (_curr_text_block['type'].upper() == ToolBox_Entity_types.IWS_JOB.value.upper())):
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
        if len(_post_note_block) >= 1:
            if '"post_notes"' not in self._blocks[-1].keys():
                self._blocks[-1]["post_notes"] = []
            self._blocks[-1]["post_notes"].extend(_post_note_block)
        
    @ToolBox_Decorator
    def convert_text_blocks_to_nodes (self):
        """Adds stored nodes to ECS system"""
        if len(self._blocks) >= 1:
            _stream_blocks = []
            _job_blocks = []
            _follow_blocks = []
            _other_blocks = []
            # split blocks into Groups for ordered processing
            for _idx in range(len(self._blocks)):
                _curr_block_type:ToolBox_Entity_types = self._blocks[_idx]['type']
                if _curr_block_type == ToolBox_Entity_types.IWS_JOBSTREAM:
                    _stream_blocks.append(self._blocks[_idx])
                elif _curr_block_type == ToolBox_Entity_types.IWS_JOB:
                    _job_blocks.append(self._blocks[_idx])
                elif _curr_block_type == ToolBox_Entity_types.IWS_FOLLOW:
                    _follow_blocks.append(self._blocks[_idx])
                else:
                    _other_blocks.append(self._blocks[_idx])
            self.log.info(f"Total Stream Blocks Found : [{len(_stream_blocks)}]")
            self.log.info (f"Total Job Blocks Found : [{len(_job_blocks)}]")
            self.log.info (f"Total Follows Blocks Found : [{len(_follow_blocks)}]")
            if len(_other_blocks) >= 1:
                self.log (f"Total Blocks unable to filter : [{len(_other_blocks)}]")

            # Process all Job Stream Blocks
            for _streamBlock in _stream_blocks:
                _curr_stream_type:ToolBox_Entity_types = _streamBlock['type']
                _curr_stream_notes:str = '\n'.join([_l.rstrip() for _l in _streamBlock['notes']]) if len(_streamBlock['notes']) != 0 else None
                _curr_stream_content:str = '\n'.join(_l.rstrip() for _l in _streamBlock['content'])    
                _curr_stream_data:dict[str,Any] = _streamBlock['data']
                _curr_stream_node = ToolBox_ECS_Node_IWS_Obj(
                    id_key = _curr_stream_data['id_key'] if 'id_key' in _curr_stream_data.keys() else None,
                    object_type = _curr_stream_type,
                    parent_entitity = None,
                    initial_data = _curr_stream_data
                )
                _curr_stream_node.sourceFile_Object = self._source_file
                _curr_stream_node.sourceFile_Text = (f"{_curr_stream_notes}\n\n"if _curr_stream_notes is not None else "")+ _curr_stream_content
                _curr_stream_post_notes:str = '\n'.join([_l.rstrip() for _l in _streamBlock['post_notes']]) if 'post_notes' in _streamBlock.keys() else None
                if _curr_stream_post_notes is not None:
                    _curr_stream_node.sourceFile_Text += f'\n\n{_curr_stream_post_notes}'
                _curr_stream_node.sourceFile_Object = self._source_file
                _curr_stream_node.sourceFile_Path = self._source_file.sourceFilePath    
                self.log.debug (f"Adding Node :'{_curr_stream_node.object_type}' defined in file '{_curr_stream_node.sourceFile_Object.relFilePath}' as '{_curr_stream_node.full_path}'")#, data=_curr_stream_node._source_file_text.splitlines(), list_data_as_table=True, column_count=1 )
                self.dataECS.insert_node_object(node = _curr_stream_node, overwrite_node = False)
            # Process all Job Stream Blocks
            for _jobBlock in _job_blocks:
                _curr_job_type:ToolBox_Entity_types = _jobBlock['type']
                _curr_job_notes:str = '\n'.join([_l.rstrip() for _l in _jobBlock['notes']]) if len(_jobBlock['notes']) != 0 else None
                _curr_job_content:str = '\n'.join(_l.rstrip() for _l in _jobBlock['content'])    
                _curr_job_data:dict[str,Any] = _jobBlock['data']
                _curr_job_node = ToolBox_ECS_Node_IWS_Obj(
                    id_key = _curr_job_data['id_key'] if 'id_key' in _curr_job_data.keys() else None,
                    object_type = _curr_job_type,
                    parent_entitity = None,
                    initial_data = _curr_job_data
                )
                _curr_job_node.sourceFile_Object = self._source_file
                _curr_job_node.sourceFile_Text = (f"{_curr_job_notes}\n\n"if _curr_job_notes is not None else "")+ _curr_job_content
                _curr_job_post_notes:str = '\n'.join([_l.rstrip() for _l in _jobBlock['post_notes']]) if 'post_notes' in _jobBlock.keys() else None
                if _curr_job_post_notes is not None:
                    _curr_job_node.sourceFile_Text += f'\n\n{_curr_job_post_notes}'
                _curr_job_node.sourceFile_Object = self._source_file
                _curr_job_node.sourceFile_Path = self._source_file.sourceFilePath    
                self.log.debug (f"Adding Node :'{_curr_job_node.object_type}' defined in file '{_curr_job_node.sourceFile_Object.relFilePath}' as '{_curr_job_node.full_path}'")#, data=_curr_job_node._source_file_text.splitlines(), list_data_as_table=True, column_count=1 )
                self.dataECS.insert_node_object(node = _curr_job_node, overwrite_node = False)
                if ('parent_key' in _curr_job_data.keys()) and (_curr_job_data['parent_key'] is not None):
                    _source_key = _curr_job_data['parent_key']
                    if (_source_key is None):
                        self.log.warning (f"Source Key was not provided,  please set 'source_key' key in object.")
                    else:
                        _source_node = self.dataECS._nodeItems[_source_key] if _source_key in self.dataECS._nodeItems.keys() else None
                        if ((_source_node is not None) and (isinstance(_source_node, ToolBox_ECS_Node_IWS_Obj))):
                            _source_node.add_child(_curr_job_node)
                            self.log.debug (f"Attaching Job node : '{_curr_job_node.deffined_path}' to its parent Job Stream node : '{_source_node.full_path if hasattr(_source_node, 'full_path') else _source_node.name}'")
                        else:
                            self.log.warning (f"Unable to find node for Source Key : '{_source_key}'")