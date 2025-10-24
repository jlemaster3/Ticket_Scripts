#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, threading
from datetime import datetime
from typing import Optional, Type

from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Filters import *
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import (
    ToolBox_File_Types, 
    ToolBox_Entity_Types, 
    ToolBox_Options, 
    ToolBox_REGEX_Patterns
)
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

    # Using imported types from ToolBox_Types
    File_Types = ToolBox_File_Types
    Entity_Types = ToolBox_Entity_Types
    Options = ToolBox_Options
    REGEX_Patterns = ToolBox_REGEX_Patterns

    #------- private properties -------#
    _instance = None
    _lock = threading.Lock()

    _nodes:dict[str, ToolBox_ECS_Node] = {}

    #------- Initialize class -------#

    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __setitem__(self, key, value):
        if isinstance(value, str):
            self._nodes[key] = value
        else:
            self._nodes[key] = value

    def __getitem__(self, key):
        if isinstance(key, str):
            key = key
        return self._nodes[key]
    
    def __len__(self):
        """Returns the total number of nodes contained."""
        return len(self._nodes.keys())
    
    def __contains__(self, item):
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
    def get_instance(self) -> "ToolBox_Manager":
        """Returns the singleton instance of OutputLogger."""
        return self._instance
    
    #-------public Getter & Setter methods -------#

    @property
    def nodes (self) -> list[ToolBox_ECS_File_Node]:
        """Returns this a list of all Nodes"""
        return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_ECS_Node)]
    
    @property
    def file_nodes (self) -> list[ToolBox_ECS_File_Node]:
        """Returns this a list of all File Nodes"""
        return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_ECS_File_Node)]
    
    @property
    def JIL_file_nodes (self) -> list[ToolBox_IWS_JIL_File_Node]:
        """Returns this a list of all *.jil or *.job File Nodes"""
        return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_ECS_File_Node) and (_n.node_type == ToolBox_Entity_Types.FILE_JIL or _n.node_type == ToolBox_Entity_Types.FILE_JOB)]

    @property
    def CSV_file_nodes (self) -> list[ToolBox_CSV_File_Node]:
        """Returns this a list of all *.csv Nodes"""
        return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_ECS_File_Node) and (_n.node_type == ToolBox_Entity_Types.FILE_CSV)]

    @property
    def IWS_object_nodes (self) -> list[ToolBox_IWS_IWS_Obj_Node]:
        """Returns this a list of all IWS Object Nodes"""
        return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_IWS_IWS_Obj_Node)]
    
    @property
    def IWS_Job_Stream_nodes (self) -> list[ToolBox_IWS_IWS_Obj_Node]:
        """Returns this a list of all IWS Job Stream Nodes"""
        return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_IWS_IWS_Obj_Node) and (_n.node_type == ToolBox_Entity_Types.IWS_JOBSTREAM)]

    @property
    def IWS_Job_nodes (self) -> list[ToolBox_IWS_IWS_Obj_Node]:
        """Returns this a list of all IWS Job Stream Nodes"""
        return [_n for _n in self._nodes.values() if isinstance(_n, ToolBox_IWS_IWS_Obj_Node) and (_n.node_type == ToolBox_Entity_Types.IWS_JOB)]
        

    #------- Methods / Functions -------#

    @ToolBox_Decorator
    def insert_node_object (self, node:ToolBox_ECS_Node, overwrite_node:bool = False):
        """Adds a premade node to the ESC node list"""
        if isinstance(node, ToolBox_ECS_Node):
            if (overwrite_node == False) and (node.id_key in self._nodes.keys()):
                self.log.warning(f" Unable to add Node to system, Node Key : [{node.id_key}] - '{node.name}' already exists.")
                return
            self._nodes[node.id_key] = node


    @ToolBox_Decorator
    def collect_files_as_nodes (self,
        source_dir: str,
        isolate_directory_names: Optional[list[str]] = None,
        exclude_directory_name: Optional[list[str]] = None,
        directory_AnyOrAll:ToolBox_Options = ToolBox_Options.ANY,
        isolate_fileName_names: Optional[list[str]] = None,
        exclude_fileName_names: Optional[list[str]] = None,
        fileName_AnyOrAll:ToolBox_Options = ToolBox_Options.ANY,
        isolate_formats: Optional[list[str]] = ['jil','job'],
        containing_terms: Optional[list[str]] = None,
        last_modified: Optional[datetime] = None,
        quite_logging:bool = True,
        list_as_tables:bool = False
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
                if not filter_directory_included(_filePath, isolate_directory_names, exclude_directory_name, isolate_any = (True if directory_AnyOrAll == self.Options.ANY else False)):
                    if (quite_logging != True) : self.log.debug (f"Skipping File '{_filePath}' - does not contains any of the terms found in either or both 'isolate_directory_names' or 'exclude_directory_name' lists.")
                    continue
                if not filter_format_included(_filePath, isolate_formats):
                    if (quite_logging != True) : self.log.debug (f"Skipping File '{_filePath}' - does not match any of the approved formates in 'isolate_foramts' lists.")
                    continue
                if not filter_filename_included(_filePath, isolate_fileName_names, exclude_fileName_names, isolate_any = (True if fileName_AnyOrAll == self.Options.ANY else False)):
                    if (quite_logging != True) : self.log.debug (f"Skipping File '{_filePath}' - does not contains any of the terms found in either or both 'isolate_fileName_names' or 'exclude_fileName_names' lists.")
                    continue
                if not filter_file_modified_after(_filePath, last_modified):
                    if (quite_logging != True) : self.log.debug (f"Skipping File '{_filePath}' - was not modified after date {last_modified.strftime('%Y-%m-%d')}.")
                    continue
                if not filter_text_content_contains(_filePath, containing_terms):
                    if (quite_logging != True) : self.log.debug (f"Skipping File '{_filePath}' - does not contains any of teh terms listed in 'containing_terms'.")
                    continue
                if (quite_logging != True) : self.log.debug (f"Adding file '{_filePath}' to selection.")
                _, _extension = os.path.splitext(_filePath)
                _file_node = None
                match _extension.lower():
                    case '.json':
                        pass
                    case '.job':
                        pass
                    case '.jil':
                        _file_node = ToolBox_IWS_JIL_File_Node(source_file_path=_filePath, root_path=_source)
                    case '.csv':
                        pass
                        _file_node = ToolBox_CSV_File_Node(source_file_path=_filePath, root_path=_source)
                    case '.yaml':
                        pass
                    case '.ps1':
                        pass
                    case _:
                        self.log.warning(f"Unknown registered file format, skipping file : '{_filePath}'")
                        pass                    
                if (isinstance(_file_node, ToolBox_ECS_File_Node)) and (_file_node.id_key not in self._nodes.keys()):
                    self._nodes[_file_node.id_key] = _file_node
                    _results.append(self._nodes[_file_node.id_key])
        if len(_results) >= 1:
            relFilePaths = [_f.relFilePath for _f in _results]
            self.log.info (f"Found [{len(_results)}] files within root path '{_source}' : ", data = relFilePaths, list_data_as_table = True)
            return _results
        else:
            return None

    @ToolBox_Decorator
    def load_file_nodes (self, 
            node_file_types:list[ToolBox_File_Types] = None,
            isolate_directory_names: Optional[list[str]] = None,
            exclude_directory_name: Optional[list[str]] = None,
            directory_AnyOrAll:ToolBox_Options = ToolBox_Options.ANY,
            isolate_fileName_names: Optional[list[str]] = None,
            exclude_fileName_names: Optional[list[str]] = None,
            fileName_AnyOrAll:ToolBox_Options = ToolBox_Options.ANY,
            isolate_formats: Optional[list[str]] = None,
            last_modified: Optional[datetime] = None,
            skip_duplicates:bool = False
        ) -> list[ToolBox_ECS_File_Node]:
        """Loads any tracked File Nodes, if the file type is able to produce ToolBox_ECS_Nodes, they will be laoded into ToolBox."""
        _files = [_n for _n in self.file_nodes]
        for _node in _files:
            if isinstance(_node,ToolBox_ECS_File_Node):
                _filePath = _node.sourceFilePath
                if not os.path.isfile(_filePath):
                    continue
                if not filter_directory_included(_filePath, isolate_directory_names, exclude_directory_name, isolate_any = (True if directory_AnyOrAll == self.Options.ANY else False)):
                    continue
                if not filter_format_included(_filePath, isolate_formats):
                    continue
                if not filter_filename_included(_filePath, isolate_fileName_names, exclude_fileName_names, isolate_any = (True if fileName_AnyOrAll == self.Options.ANY else False)):
                    continue
                if not filter_file_modified_after(_filePath, last_modified):
                    continue                
                if (node_file_types is not None) and (not any(_node.node_type == _nt for _nt in node_file_types)):
                    continue
                if hasattr(_node, 'open_file'):
                    _node.open_file(skip_duplicates = skip_duplicates)
                else:
                    self.log.warning(f"Node ({type(_node)}) [{_node.id_key}] : {_node.name} is missing 'open_file()' method.")
                    continue
            else:
                continue

    
ToolBox:ToolBox_Manager = ToolBox_Manager().get_instance()