#-------------------------------------------------
#   Imports
#-------------------------------------------------
import uuid, re
from datetime import datetime
from typing import Any

from ...ToolBox_Logger import OutputLogger
from ..shared_utils.ToolBox_Enums import (
    ToolBox_Amount_Options,
    ToolBox_Entity_Types,
    ToolBox_REGEX_Patterns
)

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


def ToolBox_list_of_dictionaries_to_table (source_row_list:list[dict[str,Any]], include_row_idx:bool=True) -> str:
    """Takes a list of rows represented by a dictionary of key : value pairs that are the column name and value for that row."""
    _headers = list(source_row_list[0].keys())
    if include_row_idx == True:
        _headers.insert(0,'Row Index')
    _col_width:dict[str,int] = {_h: len(_h) for _h in _headers}
    for _indx, _row in enumerate(source_row_list):
        _row['Row Index'] = _indx + 1
        for _header, _value in _row.items():
            _col_width[_header] = max(_col_width[_header], len(str(_value)))
    _header_row = " | ".join(f"{_h:^{_col_width[_h]}}" for _h in _headers)
    _separator = '-+-'.join("-" * _w for _w in _col_width.values())
    _data_rows = []
    for _row in source_row_list:
        _parts = []
        for _h in _headers:
            _target_val = _row.get(_h, None)
            if isinstance(_target_val,str):
                _parts.append(f"{str(_target_val):<{_col_width[_h]}}")
            else:
                _parts.append(f"{str(_target_val):^{_col_width[_h]}}")
        _row_str = " | ".join(_parts)
        _data_rows.append(_row_str)
    _table_parts = [_header_row, _separator]+_data_rows
    return '\n'.join(_table_parts)

def ToolBox_identify_date_parts (val_a:str|int|float, val_b:str|int|float, val_c:str|int|float) -> datetime|None:
    """Identifies the date parts (year, month, day) from three string/int/float values."""
    _identified:dict[str,int] = {
}
    _curr_year = datetime.now().year
    def expand_year(part:str|int|float) -> int|None:
        """Expands a 2-digit year to 4-digit based on common conventions."""
        if isinstance(part, float):
            part = int(round(part))
        if isinstance(part, str):
            part = int(part)
        year_int = part
        if len(str(year_int)) == 4:
            return year_int
        elif 0 <= len(str(year_int)) <= 3:
            if 100 <= year_int <= 999:
                return 1900 + year_int
            if 0 <= year_int <= _curr_year % 100:
                return 2000 + year_int
            elif _curr_year % 100 < year_int <= 99:
                return 1900 + year_int
        return None

    def is_possible_year(part:str|int|float) -> bool:
        """Checks if the part can be a year (2 or 4 digits)."""
        try:
            _part = int(part)
            if len(str(_part)) <= 2:
                return (0 <= _part <= 99)
            year_int = expand_year(part)
            if year_int is not None:
                return (1000 <= year_int <= 9999)
            return False
        except:
            return False
        
    def is_possible_month(part:str|int|float) -> bool:
        """Checks if the part can be a month (1-12)."""
        try:
            month_int = int(part)
            return 1 <= month_int <= 12
        except:
            return False
    def is_possible_day(part:str|int|float) -> bool:
        """Checks if the part can be a day (1-31)."""
        try:
            day_int = int(part)
            return 1 <= day_int <= 31
        except:
            return False
        
    _parts = [val_a, val_b, val_c]
    _int_parts = [int(p) for p in _parts if isinstance(p,(str,int,float)) and str(p).isdigit()]
    _part_scores:dict[str, dict[str,int]] = {}
    for _idx, _part in enumerate(_int_parts):
        _tag = f"idx_{_idx}"
        _part_scores[_tag] = {'source': _part, 'year':0, 'month':0, 'day':0}
        if is_possible_year(_part):
            _part_scores[_tag]['year'] += 1
        if is_possible_month(_part):
            _part_scores[_tag]['month'] += 1
        if is_possible_day(_part):
            _part_scores[_tag]['day'] += 1
        if len(str(int(_part))) >= 3:
            _part_scores[_tag]['year'] += 3
            _part_scores[_tag]['month'] -= 2
            _part_scores[_tag]['day'] -= 2
        if 1 <= _part <= 12:
            _part_scores[_tag]['month'] += 2
            _part_scores[_tag]['day'] += 1
        elif 12 < _part <= 31:
            _part_scores[_tag]['day'] += 3
        elif 31 < _part <= 99:
            _part_scores[_tag]['year'] += 3
        if _part == 0 :
            _part_scores[_tag]['month'] -= 5
            _part_scores[_tag]['day'] -= 5
        
    assigned_parts = set()
    for _role in ['year', 'month', 'day']:
        _best_tag = None
        _best_score = -9999
        for _tag, _scores in _part_scores.items():
            if _tag in assigned_parts:
                continue
            if _scores[_role] > _best_score:
                _best_score = _scores[_role]
                _best_tag = _tag
        if _best_tag is not None and _best_score > 0:
            assigned_parts.add(_best_tag)
            _identified[_role] = int(_part_scores[_best_tag]['source'])
    
    if len(_identified) < 3:
        while all(_k not in _identified for _k in ['year', 'month', 'day']):
            for _tag, _scores in _part_scores.items():
                if _tag in assigned_parts:
                    continue
                for _role in ['year', 'month', 'day']:
                    if _role not in _identified:
                        _identified[_role] = int(_scores['source'])
                        assigned_parts.add(_tag)
                        break
    
    _final_year = expand_year(_identified['year']) if 'year' in _identified.keys() else None
    _final_month = _identified.get('month') if 'month' in _identified.keys() else None
    _final_day = _identified.get('day') if 'day' in _identified.keys() else None

    if _final_year is not None and _final_month is not None and _final_day is not None:
        return datetime(year=_final_year, month=_final_month, day=_final_day)
    else:
        print (f"Could not definitively identify date parts from values: {val_a}, {val_b}, {val_c}\nIdentified parts: {_identified}\nPart Scores: {_part_scores}")
        return None
        

#-------------------------------------------------
#   Decorator Functions / Wrappers
#-------------------------------------------------

def ToolBox_Decorator(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        return result
    return wrapper

#-------------------------------------------------
#   classes
#-------------------------------------------------

class ToolBox_REGEX_score_evaluator:

    #------- public properties -------#
    log:OutputLogger = OutputLogger().get_instance()
    
    #------- private properties -------#
    _line_index:int
    _text:str
    _flags:list[re.RegexFlag]
    _results:dict[str,list[tuple[int, re.Match]]]
    _filter_AnyOrAll:ToolBox_Amount_Options|str|None
    _filter_patterns:list[str]|None
    _bonus_score:int|None

    #------- Initialize class -------#

    def __init__ (self, 
        text:str, 
        line_index:int,
        filter_patterns:list[str]|None = None,
        filter_AnyOrAll:ToolBox_Amount_Options|str|None = None,
        flags:list[re.RegexFlag]|None = None,
        bonus_score:int|None = None
    ):
        self._text = text
        self._line_index = line_index
        self._flags = flags or [re.IGNORECASE]
        if any(_p in text for _p in ['\n', '\r']) and re.MULTILINE not in self._flags:
            self._flags.append(re.MULTILINE)
        self._filter_patterns = filter_patterns
        try:
            self._filter_AnyOrAll = filter_AnyOrAll if (
                (filter_AnyOrAll is not None) and 
                    (isinstance(filter_AnyOrAll, ToolBox_Amount_Options) or 
                        (isinstance(filter_AnyOrAll,str) and 
                            filter_AnyOrAll in ToolBox_Amount_Options
                        )
                    )
                ) else ToolBox_Amount_Options.ANY
        except:
            self._filter_AnyOrAll = ToolBox_Amount_Options.ANY
        self._bonus_score = bonus_score
        self.evaluate_text()

    #-------public Getter & Setter methods -------#

    @property
    def line_index(self) -> int:
        return self._line_index
    
    @property
    def text(self) -> str:
        return self._text
    
    @text.setter
    def text(self, value: str):
        self._text = value


    @property
    def found_pattern_names (self) -> list[str]:
        """Returns the list of all found pattern names in line score"""
        return [_n for _n in self._results.keys()] if self._results is not None else []
    
    @property
    def get_highest_scoreing_pattern_names (self) -> list[str]:
        """Returns the list of highest scoring pattern names in line score"""
        _highest_score:int = 0
        _highest_names:list[str] = []
        for _p_name, _p_results in self._results.items():
            _max_score = max([_r[0] for _r in _p_results]) if len(_p_results) > 0 else 0
            if _max_score > _highest_score:
                _highest_score = _max_score
                _highest_names = [_p_name]
            elif _max_score == _highest_score:
                _highest_names.append(_p_name)
        return _highest_names
    
    @property
    def all_results(self) -> dict[str,list[tuple[int, dict[str,Any]]]]:
        """Returns a collection of all results with their scores and match details."""
        _results:dict[str,list[tuple[int, dict[str,Any]]]] = {}
        for _pattern_name, _pattern_results in self._results.items():
            _results[_pattern_name] = [(_score, _match.groupdict()) for _score, _match in _pattern_results]
        return _results
    
    @property
    def all_non_overlapping_results(self) -> dict[str, list[tuple[int, dict[str, Any]]]]:
        """Return non-overlapping matches across all patterns.
        Overlap resolution: keep match with lowest start index; if equal starts, keep longest span.
        """
        if not hasattr(self, "_results") or self._results is None:
            return {}
        # Flatten all matches
        _flat: list[tuple[int, int, int, str, int, re.Match]] = []
        for _p_name, _p_results in self._results.items():
            for _score, _m in _p_results:
                _s, _e = _m.span()
                _flat.append((_s, _e - _s, _e, _p_name, _score, _m))
        # Sort: start asc, length desc (so longest first when same start)
        _flat.sort(key=lambda x: (-x[1]))
        _selected_spans: list[tuple[int, int]] = []
        _non_overlapping: dict[str, list[tuple[int, dict[str, Any]]]] = {}
        for _start, _length, _end, _p_name, _score, _match in _flat:
            _span = (_start, _end)
            # Check overlap
            _overlaps = any((_start < _occ_end and _end > _occ_start) for _occ_start, _occ_end in _selected_spans)
            if _overlaps:
                continue
            _selected_spans.append(_span)
            if _p_name not in _non_overlapping:
                _non_overlapping[_p_name] = []
            _non_overlapping[_p_name].append((_score, _match.groupdict()))
        _orig_count = sum(len(v) for v in self._results.values())
        _filtered_count = sum(len(v) for v in _non_overlapping.values())
        if _filtered_count != _orig_count:
            self.log.info(f"[{self._line_index}] '{self.text}'")
            self.log.debug(f"Filtered overlapping matches: original [{_orig_count}] vs kept [{_filtered_count}]")
            self.log.debug(f"Original Results: {self.all_results}")
            self.log.debug(f"Non-overlapping Results: {_non_overlapping}")
            self.log.blank('-'*100)
        return _non_overlapping
    
    #------- Methods / Functions -------#

    @ToolBox_Decorator
    def evaluate_text (self):
        """Evaluates the text against all regex patterns and scores them."""
        _flag_val = sum(self._flags)
        self._results = {}        
        for _pattern_name, _pattern in ToolBox_REGEX_Patterns.__members__.items():
            _results = re.finditer(_pattern, self._text, _flag_val)
            if _results is not None:
                _score:int = 0 if (self._bonus_score is None) else self._bonus_score
                _pattern_name_parts = _pattern_name.split('_')
                if ((self._filter_patterns is not None) and 
                    (self._filter_AnyOrAll == ToolBox_Amount_Options.ALL) and 
                    not (all([_f.upper() in _pattern_name.upper() for _f in self._filter_patterns]))
                ):
                    _skip_pattern:bool = False
                    for _f in self._filter_patterns:
                        if re.search(rf"(?:\b|_){_f}(?:\b|_)", _pattern_name, re.IGNORECASE):
                            _score += 20
                        else:
                            _skip_pattern = True
                            break
                    if _skip_pattern:
                        continue
                elif ((self._filter_patterns is not None) and 
                    (self._filter_AnyOrAll == ToolBox_Amount_Options.ANY)
                ):
                    for _f in self._filter_patterns:
                        if re.search(rf"(?:\b|_){_f}(?:\b|_)", _pattern_name, re.IGNORECASE):
                            _score += 15
                if(self._filter_patterns is not None):
                    _score -= 5 *len([_pn_w for _pn_w in _pattern_name_parts if all([_pn_w.upper() != _f for _f in self._filter_patterns])])
                if 'note' in _pattern_name.lower():
                    _score += 20
                for _r in _results:
                    if isinstance(_r, re.Match):
                        _nonNone_groups = [_grp_v for _grp_v in _r.groupdict().values() if _grp_v is not None and _grp_v.strip() != '']
                        _None_groups = [_grp_v for _grp_v in _r.groupdict().values() if _grp_v is None or _grp_v.strip() == '']
                        _reults_len:int = len(_r.groupdict().keys())
                        if len(_nonNone_groups) >= 1:
                            _score += 5 * abs(_reults_len-len(_nonNone_groups))
                        if len(_None_groups) >= 1:
                            _score -= 5 * abs(len(_None_groups) - _reults_len)
                        _score += 5 * _reults_len
                        if _pattern_name not in self._results.keys():
                            self._results[_pattern_name] = []
                        self._results[_pattern_name].append((_score, _r))
    
    @ToolBox_Decorator
    def get_results_for_pattern(self, pattern_name: str) -> list[dict[str,Any]]:
        """Returns a list of dictionaries containing the match details for a given pattern name."""
        _results = [_r[1].groupdict() for _r in self._results.get(pattern_name, [])]
        return _results