#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, re
from enum import Enum
from datetime import datetime

#-------------------------------------------------
#   Filter Enums
#-------------------------------------------------

class ToolBox_Enum_AnyAll (Enum):
    ANY = 'any'
    ALL = 'all'

#-------------------------------------------------
#   Filter Functions
#-------------------------------------------------


def directory_included(path:str, isolate_terms:list[str]=None, exclude_terms:list[str]=None, isolate_any:bool=True, exclude_any:bool=True) -> bool:
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


def filename_included(path:str, isolate_terms:list[str]=None, exclude_terms:list[str]=None, isolate_any:bool=True, exclude_any:bool=True) -> bool:
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


def format_included(path:str, isolate_formats:list[str]=None) -> bool:
    if os.path.isfile(path) == False:
        return False
    if isolate_formats:
        ext = path.split(".")[-1].lower()
        return ext in [fmt.lower() for fmt in isolate_formats]
    return True


def content_contains(path:str, containing_terms:list[str]=None,  isolate_any:bool=True,) -> bool:
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


def modified_after(path:str, last_modified: datetime = None) -> bool:
    if not last_modified:
        return True
    _modified = datetime.fromtimestamp(os.path.getmtime(path))
    return _modified >= last_modified


def string_contains_no_whiteSpace (text:str) -> bool:
    return bool(re.fullmatch(r"^\S+$", text))


def is_IWS_asset (path:str) -> bool:
    pattern = r".*#[\/|\\\\]+.*\.(@|\w)"
    if re.search(pattern, path) and (string_contains_no_whiteSpace(path)):
        return True
    else:
        return False
    