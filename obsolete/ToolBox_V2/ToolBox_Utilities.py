#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, uuid
from enum import Enum
from datetime import datetime
from ToolBox_V2.ToolBox_logger import OutputLogger
from ToolBox_V2.ToolBox_DataTypes.ToolBox_File_Base import ToolBox_FileData
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_JIL_File import ToolBox_IWS_JIL_File
from ToolBox_V2.ToolBox_DataTypes.ToolBox_CSV_File import ToolBox_CSV_File
from typing import Any, Optional, List

#-------------------------------------------------
#   Enums
#-------------------------------------------------

class ToolBox_Enum_AnyAll (Enum):
    ANY = 'any'
    ALL = 'all'

#-------------------------------------------------
#   Filter Functions
#-------------------------------------------------

def filter_directory_included(
        path:str, 
        isolate_terms:list[str]=None, 
        exclude_terms:list[str]=None, 
        isolate_any:bool=True, 
        exclude_any:bool=True
    ) -> bool:
    """Returns True or False if the direcory path contains any of the provide search terms."""
    dirs = [_d.upper() for _d in path.split(os.sep) if '.' not in _d]
    _status = True
    if isolate_terms and (isolate_any == True) and (not any(term.upper() in d for term in isolate_terms for d in dirs)):
        _status = False
    elif isolate_terms and (isolate_any == False) and (not all(any(_term.upper() in _dir for _dir in dirs) for _term in isolate_terms)):
        _status = False
    if exclude_terms and (exclude_any == True) and (any(term.upper() in d for d in dirs for term in exclude_terms)):
        _status = False
    elif exclude_terms and (exclude_any == False) and (all(any(_term.upper() in _dir for _dir in dirs) for _term in exclude_terms)):
        _status = False
    return _status


def filter_filename_included(
        path:str, 
        isolate_terms:list[str]=None, 
        exclude_terms:list[str]=None, 
        isolate_any:bool=True, 
        exclude_any:bool=True
    ) -> bool:
    """Returns True or False if the file name contains any of the provide search terms."""
    if os.path.isfile(path) == False:
        return False
    _filename  = os.path.basename(path).split('.')[0].lower()
    _status = True
    if isolate_terms and (isolate_any == True) and (not any(term.lower() in _filename for term in isolate_terms)):
        _status = False
    elif isolate_terms and (isolate_any == False) and (not all(_term.lower() in _filename for _term in isolate_terms)):
        _status = False
    if exclude_terms and (exclude_any == True) and (any(term.lower() in _filename for term in exclude_terms)):
        _status = False
    elif exclude_terms and (exclude_any == False) and (all(term.lower() in _filename for term in exclude_terms)):
        _status = False
    return _status


def filter_format_included(path:str, isolate_formats:list[str]=None) -> bool:
    if os.path.isfile(path) == False:
        return False
    if isolate_formats:
        ext = path.split(".")[-1].lower()
        return ext in [fmt.lower() for fmt in isolate_formats]
    return True


def filter_text_content_contains(path:str, containing_terms:list[str]=None,  isolate_any:bool=True,) -> bool:
    if os.path.isfile(path) == False:
        return False
    if not containing_terms:
        return True
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        if  isolate_any ==True :
            return any(term in text for term in containing_terms)
        else:
            return all(term in text for term in containing_terms)
    except Exception:
        return False


def filter_file_modified_after(path:str, last_modified: datetime = None) -> bool:
    if not last_modified:
        return True
    _modified = datetime.fromtimestamp(os.path.getmtime(path))
    return _modified >= last_modified


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
    directory_AnyOrAll:ToolBox_Enum_AnyAll|str = ToolBox_Enum_AnyAll.ANY,
    isolate_fileName_names: Optional[List[str]] = None,
    exclude_fileName_names: Optional[List[str]] = None,
    fileName_AnyOrAll:ToolBox_Enum_AnyAll|str = ToolBox_Enum_AnyAll.ANY,
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
    _dir_any_all = (mem for mem in ToolBox_Enum_AnyAll if directory_AnyOrAll.lower() in mem.value.lower()) if isinstance(directory_AnyOrAll, str) else directory_AnyOrAll if directory_AnyOrAll is not None else ToolBox_Enum_AnyAll.ANY
    _file_any_all = (mem for mem in ToolBox_Enum_AnyAll if fileName_AnyOrAll.lower() in mem.value.lower()) if isinstance(fileName_AnyOrAll, str) else fileName_AnyOrAll if fileName_AnyOrAll is not None else ToolBox_Enum_AnyAll.ANY
    _source = os.path.abspath(source_dir)
    _results:list[ToolBox_FileData|ToolBox_CSV_File] = []
    for _root, _dirs, _files in os.walk(_source):
        for _file in _files:
            _filePath = os.path.join(_root, _file)
            if not os.path.isfile(_filePath):
                continue
            if not filter_directory_included(_filePath, isolate_directory_names, exclude_directory_name, isolate_any = (True if _dir_any_all == ToolBox_Enum_AnyAll.ANY else False)):
                if (quite_logging != True) : log.debug (f"Skipping File '{_filePath}' - does not contains any of the terms found in either or both 'isolate_directory_names' or 'exclude_directory_name' lists.")
                continue
            if not filter_format_included(_filePath, isolate_formats):
                if (quite_logging != True) : log.debug (f"Skipping File '{_filePath}' - does not match any of the approved formates in 'isolate_foramts' lists.")
                continue
            if not filter_filename_included(_filePath, isolate_fileName_names, exclude_fileName_names, isolate_any = (True if _file_any_all == ToolBox_Enum_AnyAll.ANY else False)):
                if (quite_logging != True) : log.debug (f"Skipping File '{_filePath}' - does not contains any of the terms found in either or both 'isolate_fileName_names' or 'exclude_fileName_names' lists.")
                continue
            if not filter_file_modified_after(_filePath, last_modified):
                if (quite_logging != True) : log.debug (f"Skipping File '{_filePath}' - was not modified after date {last_modified.strftime('%Y-%m-%d')}.")
                continue
            if not filter_text_content_contains(_filePath, containing_terms):
                if (quite_logging != True) : log.debug (f"Skipping File '{_filePath}' - does not contains any of teh terms listed in 'containing_terms'.")
                continue
            if (quite_logging != True) : log.debug (f"Adding file '{_filePath}' to selection.")
            _found_file = ToolBox_FileData_Sorter(_filePath, _source)
            _results.append(_found_file)
    relFilePaths = [_f.relFilePath for _f in _results]
    log.info (f"Found [{len(_results)}] files within root path '{_source}' : ", data = relFilePaths, list_data_as_table = True)
    return _results


def gen_uuid_key_old (sourceString:str=None) -> str:
    """Generates and returns a unique uuid (UUID5) string based off the string provided."""
    _tempString = str(sourceString)
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, _tempString))
    

def flatten_str(value: str) -> str:
    """Return string as-is."""
    return value


def flatten_bool(value: bool) -> str:
    """Return boolean as 'True' or 'False'."""
    return "True" if value else "False"


def flatten_int(value: int) -> str:
    """Return integer as string."""
    return str(value)


def flatten_float(value: float) -> str:
    """Return float as string (preserves Python formatting)."""
    return str(value)


def flatten_datetime(value: datetime) -> str:
    """Format datetime as single-line string: %Y-%m-%d %H:%M:%S"""
    return value.strftime("%Y-%m-%d %H:%M:%S")


def flatten_none(value: None) -> str:
    """Represent None as 'None'."""
    return "None"


def flatten_list(value: list, _recurse) -> str:
    """Flatten list recursively, include square brackets and commas with a space."""
    inner = ", ".join(_recurse(item) for item in value)
    return f"[{inner}]"


def flatten_dict(value: dict, _recurse) -> str:
    """Flatten dict recursively, include curly braces and use ': ' between key and value,
    elements separated by ', ' (space after comma)."""
    parts = []
    for k, v in value.items():
        key_s = _recurse(k)
        val_s = _recurse(v)
        parts.append(f"{key_s}: {val_s}")
    return "{%s}" % (", ".join(parts))


def flatten_any(value: Any) -> str:
    """Generic entry point — dispatches to the appropriate flattener recursively."""
    # Note: check bool before int because bool is a subclass of int
    if value is None:
        return flatten_none(value)
    if isinstance(value, bool):
        return flatten_bool(value)
    if isinstance(value, str):
        return flatten_str(value)
    if isinstance(value, int):
        return flatten_int(value)
    if isinstance(value, float):
        return flatten_float(value)
    if isinstance(value, datetime):
        return flatten_datetime(value)
    if isinstance(value, list):
        return flatten_list(value, flatten_any)
    if isinstance(value, dict):
        return flatten_dict(value, flatten_any)
    # Fallback for other iterables/objects: use str()
    return str(value)


def gen_uuid_key (source:str|int|float|list|dict|datetime) -> str:
    """Generates and returns a unique uuid (UUID5) string based off the string provided."""
    if not any([isinstance(source,_t) for _t in [str,int,float,list,dict,datetime]]):
        raise TypeError(f"Source must be of type : [ string, int, float, list, dict, datetime ] , recieved : {type:(source)}")
    _tempString = flatten_any (source)
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, _tempString))