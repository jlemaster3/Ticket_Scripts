#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, threading, copy
from datetime import datetime
from typing import Optional, Literal, Callable, Any

from .ToolBox_Logger import OutputLogger
from .scr.ToolBox_Data_Silo import ToolBox_Data_Silo_Manager
from .scr.shared_utils.ToolBox_Filters import *
from .scr.shared_utils.ToolBox_Utils import *
from .scr.shared_utils.ToolBox_Enums import (
    ToolBox_Amount_Options,
    ToolBox_Entity_Types,
    ToolBox_REGEX_Patterns
)
from .scr.decoders.ToolBox_base_text_file import ToolBox_text_file_manager
from .scr.decoders.ToolBox_CSV_file import ToolBox_CSV_File_Manager
from .scr.decoders.ToolBox_IWS_Config_file import ToolBox_IWS_Config_File_Manager
from .scr.decoders.ToolBox_IWS_JIL_file import ToolBox_IWS_JIL_File_Manager
from .scr.decoders.ToolBox_IWS_TEXT_file import ToolBox_IWS_text_file_manager
from .scr.ToolBox_Action_Manager import ToolBox_Action_Manager

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

    Entity_Types = ToolBox_Entity_Types
    Amount_Options = ToolBox_Amount_Options
    Regex_Patterns = ToolBox_REGEX_Patterns    

    #------- private properties -------#
    _instance = None
    _lock = threading.Lock()

    Text_File_Manager:ToolBox_text_file_manager = ToolBox_text_file_manager.get_instance()
    CSV_File_Manager:ToolBox_CSV_File_Manager = ToolBox_CSV_File_Manager.get_instance()
    IWS_JIL_File_Manager:ToolBox_IWS_JIL_File_Manager = ToolBox_IWS_JIL_File_Manager.get_instance()
    IWS_CONFIG_File_Manager:ToolBox_IWS_Config_File_Manager = ToolBox_IWS_Config_File_Manager.get_instance()
    IWS_TEXT_File_Manager:ToolBox_IWS_text_file_manager = ToolBox_IWS_text_file_manager.get_instance()
    
    Action_Manager:ToolBox_Action_Manager = ToolBox_Action_Manager.get_instance()
    #------- Initialize class -------#
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> "ToolBox_Manager":
        """Returns the singleton instance of ToolBox_Manager, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    #-------public Getter & Setter methods -------#    
    
    @ToolBox_Decorator
    def collect_files (self,
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
    ) -> list [Any]:
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
        _results:list[Any] = []
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
                _file_name, _file_extension = os.path.splitext(os.path.basename(_filePath))
                _file_metadata:dict[str,Any] = {
                    'full_path' : _filePath,
                    'root_path' : _source,
                    'file_path' : os.path.relpath(_root, _source),
                    'file_name' : _file_name,
                    'file_format' : _file_extension.lower(),
                    'created_datatime' : datetime.fromtimestamp(os.path.getctime(_filePath)),
                    'modified_datatime' : datetime.fromtimestamp(os.path.getmtime(_filePath)),
                }
                match _file_extension.lower():
                    case '.txt':
                        if 'JobDefinitions' in _filePath:
                            _file_metadata['object_type'] = ToolBox_Entity_Types.FILE_JIL
                        else:
                            _file_metadata['object_type'] = ToolBox_Entity_Types.FILE_TXT
                    case '.json':
                        _file_metadata['object_type'] = ToolBox_Entity_Types.FILE_JSON
                    case '.job':
                        _file_metadata['object_type'] = ToolBox_Entity_Types.FILE_JIL
                    case '.jil':
                        _file_metadata['object_type'] = ToolBox_Entity_Types.FILE_JIL
                    case '.csv':
                        _file_metadata['object_type'] = ToolBox_Entity_Types.FILE_CSV
                    case '.yaml':
                        _file_metadata['object_type'] = ToolBox_Entity_Types.FILE_YAML
                    case '.ps1':
                        pass
                    case '.xlsx':
                        if 'runbook' in _filePath.lower():
                            _file_metadata['object_type'] = ToolBox_Entity_Types.IWS_XLS_RUNBOOK
                        else:
                            _file_metadata['object_type'] = ToolBox_Entity_Types.FILE_XLSX
                    case _:
                        self.log.warning(f"Unknown registered file format, skipping file : '{_filePath}'")
                if 'object_type' in _file_metadata.keys() and _file_metadata['object_type'] is not None:
                    _new_entitiy_key = self.dataSilo.create_entity(
                        key_id=gen_uuid_key(f"{_filePath}"), 
                        components=_file_metadata
                    )
                    _results.append(_new_entitiy_key)
        if len(_results) >= 1:
            _relFilePaths = [f"'{os.path.relpath(self.dataSilo.get_entity(key).get('full_path', ''), _source)}'" for key in _results]
            self.log.info (f"Found [{len(_results)}] files within root path '{_source}' : ", data = _relFilePaths, list_data_as_table = True)
            self.log.blank('-'*100)
            return _results
        else:
            return []
    
    @ToolBox_Decorator
    def Foramt_list_of_dictionaries_to_multiline_str (self, source_row_list:list[dict[str,Any]]) -> str:
        """Takes a list of rows represented by a dictionary of key : value pairs that are the column name and value for that row."""
        #exposes the Formatting option through Toolbox caller
        return ToolBox_list_of_dictionaries_to_table(source_row_list)
    



ToolBox:ToolBox_Manager = ToolBox_Manager().get_instance()