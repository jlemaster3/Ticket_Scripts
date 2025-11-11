#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, threading, copy
from datetime import datetime
from typing import Optional, Literal, Callable, Any

from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Data_Silo import *
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Filters import *
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import (
    ToolBox_Amount_Options,
    ToolBox_File_Types, 
    ToolBox_Entity_Types, 
    ToolBox_REGEX_Patterns,
    ToolBox_Struct_Entity_Relationships,
    ToolBox_Struct_IWS_Stream,
    ToolBox_Struct_IWS_Job  
)
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Timezones import ToolBox_Timezone_Patterns
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Formatters import ToolBox_list_of_dictionaries_to_table as _list_of_rows_to_Strings
from ToolBox_ECS_V1.Nodes import *

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

class ToolBox_Manager :
    """Main Entry point for ToolBox scripts."""
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    dataSilo:ToolBox_Data_Silo_Manager = ToolBox_Data_Silo_Manager.get_instance()

    # Using imported types from ToolBox_Types
    File_Types = ToolBox_File_Types
    Entity_Types = ToolBox_Entity_Types
    Amount_Options = ToolBox_Amount_Options
    REGEX_Patterns = ToolBox_REGEX_Patterns
    TimeZone_Patterns = ToolBox_Timezone_Patterns
    IWS_struct_relationships = ToolBox_Struct_Entity_Relationships
    IWS_struct_Stream = ToolBox_Struct_IWS_Stream
    IWS_struct_Job = ToolBox_Struct_IWS_Job

    #------- private properties -------#
    _instance = None
    _lock = threading.Lock()

    _nodes:dict[str, ToolBox_ECS_Node] = {}

    _IWS_nodes:dict[str,dict[str, ToolBox_IWS_Obj_Node]] = {
        "unsorted":{},
        "Job_Streams":{},
        "Jobs":{},
        
    }

    #------- Initialize class -------#

    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __setitem__(self, key:str, value:ToolBox_ECS_Node):
        if isinstance(value, str):
            self.dataSilo[key] = value
        else:
            self.dataSilo[key] = value

    def __getitem__(self, key:str):
        if isinstance(key, str):
            key = key
        return self.dataSilo[key]
    
    def __len__(self):
        """Returns the total number of nodes contained."""
        return len(self.dataSilo)
    
    def __contains__(self, item:str|ToolBox_ECS_Node):
        """
        Implements the 'in' operator, if string is provided, will check stored id_keys and names of nodes,
        if a ToolBox_ECS_Node class is provided, will check stored node list
        """
        if isinstance(item, str):
            for _k, _v in self._nodes.items():
                if item.upper() in _k.upper():
                    return True
                if item.upper() in _v.name.upper():
                    return True
        elif isinstance(item, ToolBox_ECS_Node):
            return item in self._nodes.values()
        return False
    
    @classmethod
    def get_instance(cls) -> "ToolBox_Manager":
        """Returns the singleton instance of ToolBox_Manager, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    #-------public Getter & Setter methods -------#

    @property
    def nodes (self) -> list[ToolBox_ECS_Node]:
        """Returns this a list of all Nodes"""
        return self.dataSilo.nodes
        #return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_ECS_Node)]
    
    @property
    def node_keys (self) -> list[str]:
        """Returns this a list of all key string stored in Nodes collection"""
        return [_n.id_key for _n in self._nodes.values() if isinstance(_n, ToolBox_ECS_Node)]

    @property
    def file_nodes (self) -> list[ToolBox_ECS_File_Node]:
        """Returns this a list of all File Nodes"""
        return self.dataSilo.file_nodes
        #return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_ECS_File_Node)]
    
    @property
    def file_node_keys (self) -> list[str]:
        """Returns this a list of all key string for all File Nodes in collection"""
        return [_n.id_key for _n in self._nodes.values() if isinstance(_n, ToolBox_ECS_File_Node)]
    
    @property
    def JIL_file_nodes (self) -> list[ToolBox_IWS_JIL_File_Node]:
        """Returns this a list of all *.jil or *.job File Nodes"""
        return self.dataSilo.JIL_file_nodes
        #return [_n for _n in self._nodes.values() if (isinstance(_n, ToolBox_IWS_JIL_File_Node) and (_n.node_type == ToolBox_Entity_Types.FILE_JIL or _n.node_type == ToolBox_Entity_Types.FILE_JOB))]

    @property
    def JIL_file_node_keys (self) -> list[str]:
        """Returns this a list of all *.jil or *.job key strings for all File Nodes in collection."""
        return [_n.id_key for _n in self._nodes.values() if (isinstance(_n, ToolBox_IWS_JIL_File_Node) and (_n.node_type == ToolBox_Entity_Types.FILE_JIL or _n.node_type == ToolBox_Entity_Types.FILE_JOB))]
    
    @property
    def CSV_file_nodes (self) -> list[ToolBox_CSV_File_Node]:
        """Returns this a list of all *.csv Nodes"""
        return self.dataSilo.CSV_file_nodes
        #return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_CSV_File_Node) and (_n.node_type == ToolBox_Entity_Types.FILE_CSV)]
    
    @property
    def XLSX_file_nodes (self) -> list[ToolBox_XLSX_File_Node]:
        """Returns this a list of all *.xlsx Nodes"""
        return self.dataSilo.XLSX_file_nodes
        #return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_XLSX_File_Node) and (_n.node_type == ToolBox_Entity_Types.FILE_XLSX)]

    @property
    def IWS_Runbook_file_nodes (self) -> list[ToolBox_IWS_XLSX_Runbook_File_Node]:
        """Returns this a list of all *.xlsx Runbook Nodes"""
        return self.dataSilo.IWS_Runbook_file_nodes
        #return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_IWS_XLSX_Runbook_File_Node) and (_n.node_type == ToolBox_Entity_Types.IWS_XLS_RUNBOOK)]

    @property
    def CSV_file_node_keys (self) -> list[str]:
        """Returns this a list of all *.csv key strings for all File Nodes in collection."""
        return [_n.id_key for _n in self._nodes.values() if isinstance(_n, ToolBox_CSV_File_Node) and (_n.node_type == ToolBox_Entity_Types.FILE_CSV)]

    @property
    def IWS_object_nodes (self) -> list[ToolBox_IWS_Obj_Node]:
        """Returns this a list of all IWS Object Nodes"""
        return self.dataSilo.IWS_object_nodes
        #return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_IWS_Obj_Node)]
    
    @property
    def IWS_Job_Stream_nodes (self) -> list[ToolBox_IWS_Obj_Node]:
        """Returns this a list of all IWS Job Stream Nodes"""
        return self.dataSilo.IWS_Job_Stream_nodes
        #return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_IWS_Obj_Node) and (_n.node_type == ToolBox_Entity_Types.IWS_JOB_STREAM)]

    @property
    def IWS_Job_nodes (self) -> list[ToolBox_IWS_Obj_Node]:
        """Returns this a list of all IWS Job Stream Nodes"""
        return self.dataSilo.IWS_Job_nodes
        #return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_IWS_Obj_Node) and (_n.node_type == ToolBox_Entity_Types.IWS_JOB)]
    
    @property
    def node_stats (self) -> str:
        return self.dataSilo.statistics

    #------- Methods / Functions -------#

    @ToolBox_Decorator
    def append_node_object (self, node:ToolBox_ECS_Node, overwrite_node:bool = False):
        """Adds a premade node to the ESC node list"""
        if isinstance(node, ToolBox_ECS_Node):
            if (overwrite_node == False) and (node.id_key in self._nodes.keys()):
                self.log.warning(f" Unable to add Node to system, Node Key : [{node.id_key}] - '{node.name}' already exists.")
                return
            self.dataSilo.append_node(node)
            #self._nodes[node.id_key] = node


    @ToolBox_Decorator
    def collect_files_as_nodes (self,
        source_dir: str,
        isolate_directory_names: Optional[list[str]] = None,
        exclude_directory_name: Optional[list[str]] = None,
        directory_AnyOrAll:Literal[ToolBox_Amount_Options.ANY, ToolBox_Amount_Options.ALL] = ToolBox_Amount_Options.ANY,
        isolate_fileName_names: Optional[list[str]] = None,
        exclude_fileName_names: Optional[list[str]] = None,
        fileName_AnyOrAll:Literal[ToolBox_Amount_Options.ANY, ToolBox_Amount_Options.ALL] = ToolBox_Amount_Options.ANY,
        isolate_formats: Optional[list[str]] = ['jil','job'],
        containing_terms: Optional[list[str]] = None,
        last_modified: Optional[datetime] = None,
        quite_logging:bool = True,
        list_as_tables:bool = True
    ) -> list [ToolBox_ECS_File_Node]:
        """
        Scans a directory for files matching criteria and returns a list of ToolBox_ECS_File_Node objects that represent a found file.
        """
        if isolate_directory_names is not None : 
            self.log.info (f"Directory names to Isolate : ", data= isolate_directory_names, list_data_as_table = list_as_tables)
        if exclude_directory_name is not None : 
            self.log.info (f"Directory names to Exclude : ", data= exclude_directory_name, list_data_as_table = list_as_tables)
        if isolate_fileName_names is not None : 
            self.log.info (f"File Names to Isolate : ", data= isolate_fileName_names, list_data_as_table = list_as_tables)
        if exclude_fileName_names is not None : 
            self.log.info (f"File Names to Exclude : ", data= exclude_fileName_names, list_data_as_table = list_as_tables)
        if isolate_formats is not None : 
            self.log.info (f"Allowed File Formats : ", data= isolate_formats, list_data_as_table = list_as_tables)
        if last_modified is not None:
            self.log.info (f"Date to check fi file was modified after : ", data= last_modified)
        if containing_terms is not None:
            self.log.info (f"Strings / Terms in files to search for : ", data= containing_terms, list_data_as_table = list_as_tables)
        _source = os.path.abspath(source_dir)
        _results:list[ToolBox_ECS_File_Node] = []
        for _root, _dirs, _files in os.walk(_source):
            for _file in _files:
                _filePath = os.path.join(_root, _file)
                if not os.path.isfile(_filePath):
                    continue
                if not filter_directory_included(_filePath, isolate_directory_names, exclude_directory_name, isolate_any = (True if directory_AnyOrAll == ToolBox_Amount_Options.ANY else False)):
                    if (quite_logging != True) : self.log.debug (f"Skipping File '{_filePath}' - does not contains any of the terms found in either or both 'isolate_directory_names' or 'exclude_directory_name' lists.")
                    continue
                if not filter_format_included(_filePath, isolate_formats):
                    if (quite_logging != True) : self.log.debug (f"Skipping File '{_filePath}' - does not match any of the approved formates in 'isolate_foramts' lists.")
                    continue
                if not filter_filename_included(_filePath, isolate_fileName_names, exclude_fileName_names, isolate_any = (True if fileName_AnyOrAll == ToolBox_Amount_Options.ANY else False)):
                    if (quite_logging != True) : self.log.debug (f"Skipping File '{_filePath}' - does not contains any of the terms found in either or both 'isolate_fileName_names' or 'exclude_fileName_names' lists.")
                    continue
                if not filter_file_modified_after(_filePath, last_modified):
                    if (quite_logging != True) : self.log.debug (f"Skipping File '{_filePath}' - was not modified after date {last_modified.strftime('%Y-%m-%d') if last_modified is not None else ''}.")
                    continue
                if not filter_text_content_contains(_filePath, containing_terms):
                    if (quite_logging != True) : self.log.debug (f"Skipping File '{_filePath}' - does not contains any of teh terms listed in 'containing_terms'.")
                    continue
                _, _extension = os.path.splitext(_filePath)
                _file_node = None
                match _extension.lower():
                    case '.json':
                        pass
                    case '.job':
                        _file_node = ToolBox_IWS_JIL_File_Node(source_file_path=_filePath, root_path=_source)
                    case '.jil':
                        _file_node = ToolBox_IWS_JIL_File_Node(source_file_path=_filePath, root_path=_source)
                    case '.csv':
                        _file_node = ToolBox_CSV_File_Node(source_file_path=_filePath, root_path=_source)
                    case '.yaml':
                        pass
                    case '.ps1':
                        pass
                    case '.xlsx':
                        if 'runbook' in _filePath.lower():
                            _file_node = ToolBox_IWS_XLSX_Runbook_File_Node(source_file_path=_filePath, root_path=_source)
                        else:
                            _file_node = ToolBox_XLSX_File_Node(source_file_path=_filePath, root_path=_source)
                    case _:
                        self.log.warning(f"Unknown registered file format, skipping file : '{_filePath}'")
                if (isinstance(_file_node, ToolBox_ECS_File_Node)) and (_file_node.id_key not in self._nodes.keys()):
                    _results.append(_file_node)
                    self.dataSilo.append_node(_file_node)
                    #self._nodes[_file_node.id_key] = _file_node
                    if (quite_logging != True) : self.log.debug (f"Adding Node : [{_file_node.id_key}] - '{_file_node.node_type}' defined in file '{_file_node.sourceFilePath}'")
        if len(_results) >= 1:
            relFilePaths = [_f.relFilePath for _f in _results]
            self.log.info (f"Found [{len(_results)}] files within root path '{_source}' : ", data = relFilePaths, list_data_as_table = True)
            self.log.blank('-'*100)
            return _results
        else:
            return []

    @ToolBox_Decorator
    def load_file_nodes (self, 
            node_file_types:Optional[list[ToolBox_File_Types]] = None,
            isolate_directory_names: Optional[list[str]] = None,
            exclude_directory_name: Optional[list[str]] = None,
            directory_AnyOrAll:Literal[ToolBox_Amount_Options.ANY, ToolBox_Amount_Options.ALL] = ToolBox_Amount_Options.ANY,
            isolate_fileName_names: Optional[list[str]] = None,
            exclude_fileName_names: Optional[list[str]] = None,
            fileName_AnyOrAll:Literal[ToolBox_Amount_Options.ANY, ToolBox_Amount_Options.ALL] = ToolBox_Amount_Options.ANY,
            isolate_formats: Optional[list[str]] = None,
            last_modified: Optional[datetime] = None,
            skip_duplicates:bool = False,
            quite_logging:bool = True,
            enable_post_porcesses:bool = True,
            contents_as_entities:bool = False
        ) -> list[ToolBox_ECS_File_Node]:
        """Loads any tracked File Nodes, if the file type is able to produce ToolBox_ECS_Nodes, they will be laoded into ToolBox."""
        _files = [_n for _n in self.dataSilo.file_nodes]
        #_files = [_n for _n in self.file_nodes]
        for _node in _files:
            if isinstance(_node,ToolBox_ECS_File_Node):
                _filePath = _node.sourceFilePath
                if not os.path.isfile(_filePath):
                    continue
                if not filter_directory_included(_filePath, isolate_directory_names, exclude_directory_name, isolate_any = (True if directory_AnyOrAll == ToolBox_Amount_Options.ANY else False)):
                    continue
                if not filter_format_included(_filePath, isolate_formats):
                    continue
                if not filter_filename_included(_filePath, isolate_fileName_names, exclude_fileName_names, isolate_any = (True if fileName_AnyOrAll == ToolBox_Amount_Options.ANY else False)):
                    continue
                if not filter_file_modified_after(_filePath, last_modified):
                    continue                
                if (node_file_types is not None) and (not any(_node.node_type == _nt for _nt in node_file_types)):
                    continue
                if hasattr(_node, 'open_file') and contents_as_entities == False:
                    #try:
                        # Try calling with skip_duplicates if supported
                        _node.open_file(quite_logging=quite_logging, skip_duplicates=skip_duplicates, enable_post_porcesses=enable_post_porcesses) # type: ignore
                    #except TypeError:
                    #    # Fallback for implementations that don't accept skip_duplicates
                    #    try:
                    #        _node.open_file(quite_logging=False)
                    #    except Exception as _ex:
                    #        self.log.warning(f"Failed to open node ({type(_node)}) [{_node.id_key}] : {_node.name} - {_ex}")
                    #except Exception as _ex:
                    #    self.log.warning(f"Failed to open node ({type(_node)}) [{_node.id_key}] : {_node.name} - {_ex}")
                elif contents_as_entities == True and isinstance(_node, ToolBox_IWS_JIL_File_Node) and hasattr(_node, 'load_contents_as_entities'):
                    _node.load_contents_as_entities()
                else:
                    self.log.warning(f"Node ({type(_node)}) [{_node.id_key}] : {_node.name} is missing 'open_file()' method.")
                    continue
            else:
                continue
        return _files
    
    @ToolBox_Decorator
    def action_duplicate_node(self,
        source_key:str,
        filter_func:Callable[[ToolBox_ECS_Node], bool],
        search_replace_terms:dict[str,str|int|float|bool|datetime|None]
        ) : 
        """W.I.P. - Not completed or working - Copy the source node and assigns it a new ID key, keeping all other settings of the node"""
        _source_node = self._nodes.get(source_key)
        if _source_node is None:
            self.log.warning(f"Source key not found in node list : ", data=source_key)
            return None
        if not filter_func(_source_node):
            return None
        
    @ToolBox_Decorator
    def Foramt_list_of_dictionaries_to_multiline_str (self, source_row_list:list[dict[str,Any]]) -> str:
        """Takes a list of rows represented by a dictionary of key : value pairs that are the column name and value for that row."""
        #exposes the Formatting option through Toolbox caller
        return _list_of_rows_to_Strings(source_row_list)
    
    @ToolBox_Decorator
    def Action_IWS_nodes_Duplicate_to_New_Agent (self,
            source_IWS_file_nodes:list[ToolBox_IWS_JIL_File_Node],
            Output_Folder_path:str ,
            Search_Replace_Terms:dict[str,str],
            quite_logging:bool = True
        ) -> list[ToolBox_IWS_JIL_File_Node] | None:
        """For each file in source path, find all IWS assets, and duplicate them, then preform a search and replace on teh duplicated assest's text.
        Append the duplcated and udpated text to the current file, and save a copy of the file to a new location for review.
        Returns a list of pointers to the nodes that have been changed.

        !!! - This action does not save the changed or modified node. - !!!
        """
        _changed_list:list[ToolBox_IWS_JIL_File_Node]|None = None
        for _file_index, _file_node in enumerate(source_IWS_file_nodes):
            if isinstance(_file_node,ToolBox_IWS_JIL_File_Node):
                _has_been_updated:bool = False
                self.log.info (f"[{_file_index+1}] Processing file '{_file_node.relFilePath}'")
                _file_node.open_file(
                    enable_post_porcesses=False
                )
                _copy_of_text:str|None = copy.deepcopy(_file_node._source_file_text) or None
                
                if isinstance(_copy_of_text, str):
                    for _search, _replace in Search_Replace_Terms.items():
                        _replaced = _copy_of_text.replace(_search,_replace)
                        if _replaced != _copy_of_text:
                            if (quite_logging != True) :self.log.debug (f"Found search term '{_search}' and repalcing with '{_replace}'")
                            _copy_of_text = _replaced
                            _has_been_updated = True
                if _has_been_updated == True and isinstance(_copy_of_text, str):
                    if _changed_list is None:
                        _changed_list = []
                    _changed_list.append(_file_node)
        return _changed_list

ToolBox:ToolBox_Manager = ToolBox_Manager().get_instance()