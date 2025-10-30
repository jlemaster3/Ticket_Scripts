#-------------------------------------------------
#   Imports
#-------------------------------------------------
import uuid
from datetime import datetime
from typing import Any

#-------------------------------------------------
#   Shared Methods / Functions.
#-------------------------------------------------

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


