#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os
from datetime import datetime
from ToolBox_V2.ToolBox_logger import OutputLogger
from ToolBox_V2.ToolBox_DataTypes.ToolBox_File_Base import ToolBox_FileData
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_JIL_File import ToolBox_IWS_JIL_File
from ToolBox_V2.ToolBox_DataTypes.ToolBox_CSV_File import ToolBox_CSV_File
from ToolBox_V2.ToolBox_Filters import (
    ToolBox_Enum_AnyAll,
    directory_included,
    filename_included,
    format_included,
    content_contains,
    modified_after
)
from typing import Any, Optional, List

#-------------------------------------------------
#   variables
#-------------------------------------------------



#-------------------------------------------------
#   FileData Factory
#-------------------------------------------------

def ToolBox_FileData_Sorter (filePath:str, rootPath:str=None) -> ToolBox_FileData|ToolBox_CSV_File:
    log = OutputLogger.get_instance()
    if os.path.isfile(filePath):
        _, _extension = os.path.splitext(filePath)
        match _extension.lower():
            case '.json':
                pass
            case '.job':
                pass
            case '.jil':
                return ToolBox_IWS_JIL_File(path=filePath, rootPath=rootPath)
            case '.csv':
                return ToolBox_CSV_File(path=filePath, rootPath=rootPath)
            case '.yaml':
                pass
            case '.ps1':
                pass
            case _:
                log.warning(f"Unknown registered file format, skipping file : '{filePath}'")
                pass
    return None

#-------------------------------------------------
#   Functions
#-------------------------------------------------

def ToolBox_Gather_Directories (
    source_dir:str
) -> list[str]:
    """Returns a list of sub directories found in provided root directory."""
    log = OutputLogger.get_instance()
    _sourcePath = os.path.abspath(source_dir)
    _results:list[str] = []
    for _root, _dirs, _files in os.walk(_sourcePath):
         if not _dirs:
            relative_path = os.path.relpath(_root, _sourcePath)
            if relative_path not in _results:
                _results.append(relative_path)
    log.info (f"Found [{len(_results)}] directories in source path '{_sourcePath}' : ", data = _results, list_data_as_table = True)
    return _results

def ToolBox_Gather_Files(
    source_dir: str,
    isolate_directory_names: Optional[List[str]] = None,
    exclude_directory_name: Optional[List[str]] = None,
    directory_AnyOrAll:ToolBox_Enum_AnyAll = ToolBox_Enum_AnyAll.ANY,
    isolate_fileName_names: Optional[List[str]] = None,
    exclude_fileName_names: Optional[List[str]] = None,
    fileName_AnyOrAll:ToolBox_Enum_AnyAll = ToolBox_Enum_AnyAll.ANY,
    isolate_formats: Optional[List[str]] = ['jil','job'],
    containing_terms: Optional[List[str]] = None,
    last_modified: Optional[datetime] = None,
    quite_logging:bool = True,
    list_as_tables:bool = False
) -> list [ToolBox_IWS_JIL_File|ToolBox_CSV_File]:
    """
    Scans a directory for files matching criteria and returns FileData objects.
    """
    log = OutputLogger.get_instance()

    if isolate_directory_names is not None : 
        log.info (f"Directory names to Isolate : ", data= isolate_directory_names, list_data_as_table = list_as_tables)
    if exclude_directory_name is not None : 
        log.info (f"Directory names to Exclude : ", data= exclude_directory_name, list_data_as_table = list_as_tables)
    if isolate_fileName_names is not None : 
        log.info (f"File Names to Isolate : ", data= isolate_fileName_names, list_data_as_table = list_as_tables)
    if exclude_fileName_names is not None : 
        log.info (f"File Names to Exclude : ", data= exclude_fileName_names, list_data_as_table = list_as_tables)
    if isolate_formats is not None : 
        log.info (f"Allowed File Formats : ", data= isolate_formats, list_data_as_table = list_as_tables)
    if last_modified is not None:
        log.info (f"Date to check fi file was modified after : ", data= last_modified)
    if containing_terms is not None:
        log.info (f"Strings / Terms in files to search for : ", data= containing_terms, list_data_as_table = list_as_tables)
    _source = os.path.abspath(source_dir)
    _results:list[ToolBox_FileData|ToolBox_CSV_File] = []
    for _root, _dirs, _files in os.walk(_source):
        for _file in _files:
            _filePath = os.path.join(_root, _file)
            if not os.path.isfile(_filePath):
                continue
            if not directory_included(_filePath, isolate_directory_names, exclude_directory_name, isolate_any = (True if directory_AnyOrAll == ToolBox_Enum_AnyAll.ANY else False)):
                if (quite_logging != True) : log.debug (f"Skipping File '{_filePath}' - does not contains any of the terms found in either or both 'isolate_directory_names' or 'exclude_directory_name' lists.")
                continue
            if not format_included(_filePath, isolate_formats):
                if (quite_logging != True) : log.debug (f"Skipping File '{_filePath}' - does not match any of the approved formates in 'isolate_foramts' lists.")
                continue
            if not filename_included(_filePath, isolate_fileName_names, exclude_fileName_names, isolate_any = (True if fileName_AnyOrAll == ToolBox_Enum_AnyAll.ANY else False)):
                if (quite_logging != True) : log.debug (f"Skipping File '{_filePath}' - does not contains any of the terms found in either or both 'isolate_fileName_names' or 'exclude_fileName_names' lists.")
                continue
            if not modified_after(_filePath, last_modified):
                if (quite_logging != True) : log.debug (f"Skipping File '{_filePath}' - was not modified after date {last_modified.strftime('%Y-%m-%d')}.")
                continue
            if not content_contains(_filePath, containing_terms):
                if (quite_logging != True) : log.debug (f"Skipping File '{_filePath}' - does not contains any of teh terms listed in 'containing_terms'.")
                continue
            if (quite_logging != True) : log.debug (f"Adding file '{_filePath}' to selection.")
            _found_file = ToolBox_FileData_Sorter(_filePath, _source)
            _results.append(_found_file)
    relFilePaths = [_f.relFilePath for _f in _results]
    log.info (f"Found [{len(_results)}] files within root path '{_source}' : ", data = relFilePaths, list_data_as_table = True)
    return _results
