#-------------------------------------------------
#   Imports
#-------------------------------------------------
import re, uuid
from enum import StrEnum
from typing import Literal, Any, TypedDict, NotRequired, Required, Dict, Type
from collections import UserDict
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import (
    ToolBox_Amount_Options,
    ToolBox_Entity_Types,
    ToolBox_REGEX_Patterns
)

#-------------------------------------------------
#   Enums
#-------------------------------------------------

log:OutputLogger = OutputLogger().get_instance()

#-------------------------------------------------
#   Shared Methods / Functions.
#-------------------------------------------------

def ToolBox_REGEX_identify_patterns (source_text:str) -> list[list[ToolBox_REGEX_Patterns]]:
    """Returns a collection of patterns found per line of source text provided."""
    _container:list[list[ToolBox_REGEX_Patterns]] = []
    if source_text is None:
        log.warning(f"Unable to identiy Patterns of 'source_text', privided type is 'NoneType'.")
    else:
        for _line_str in source_text.splitlines():
            _matched_patterns:list[ToolBox_REGEX_Patterns] = []
            for _name, _pattern in ToolBox_REGEX_Patterns._member_map_.items():
                if re.search(_pattern.value, _line_str, re.IGNORECASE.value):
                    _matched_patterns.append(ToolBox_REGEX_Patterns[_name])
            if len(_matched_patterns) >= 1:
                _container.append(_matched_patterns)
    return _container


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

class ToolBox_line_score_data (UserDict):
    
    _source_index:int
    _source_text:str
    
    _flag_list:list[re.RegexFlag]
    _flag_val:int
    _filter_AnyOrAll:ToolBox_Amount_Options|str|None
    _filter_patterns:list[str]|None
    _results: dict[str,list[tuple[int,re.Match]]]|None
    _bonus_score:int|None
    _score: int|None

    #------- Initialize class -------#
    
    def __init__ (self,
            source_index:int,
            source_text:str,
            filter_patterns:list[str]|None = None,
            filter_AnyOrAll:ToolBox_Amount_Options|str|None = None,
            flags:list[re.RegexFlag]|None = None,
            bonus_score:int|None = None,
            initial_data: Dict[str, Any] | None = None, 
            **kwargs: Any | None
        ):
        super().__init__(initial_data, kwargs = kwargs)
        self._source_index = source_index
        self._source_text = source_text
        self._flag_list = flags or [re.IGNORECASE]
        if any(_p in source_text for _p in ['\n', '\r']) and re.MULTILINE not in self._flag_list:
            self._flag_list.append(re.MULTILINE)
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
        self._flag_val:int = sum(self._flag_list)
        self._bonus_score = bonus_score
        self._results = None
        self._score = None
        self.evaluate_pattern()

    def __setitem__(self, key, value):
        if isinstance(value, str):
            self.data[key] = value
        else:
            self.data[key] = value
    
    def __getitem__(self, key:str):
        if isinstance(key, str):
            if self._results is not None and key in self._results.keys():
                return self._results.get(key)
            return self.get(key)

    #-------public Getter & Setter methods -------#

    @property
    def source_line_index (self) -> int:
        return self._source_index
    
    @property
    def source_line_text (self) -> str:
        return self._source_text

    @property
    def high_score_value (self) -> int:
        """Returns the high score value."""
        _high_score = None
        if self._results is not None:
            for _rl in self._results.values():
                for _r in _rl:
                    if _high_score is None:
                        _high_score = _r[0]
                    elif _r[0] > _high_score:
                        _high_score = _r[0]
        return _high_score if _high_score is not None else -1
        
    
    @property
    def high_score_pattern_names (self) -> list[str]:
        """Returns the list of results if found, returns None if none are found"""
        _high_score_results:list[str] = []
        if self._results is not None:
            for _pn, _rl in self._results.items():
                for _r in _rl:
                    if _r[0] == self.high_score_value and _pn not in _high_score_results:
                            _high_score_results.append(_pn)
        return _high_score_results
    
    @property
    def highest_scoring_results (self) -> dict[str,Any]:
        """Retunrs teh reuslts of teh highest scoring pattern"""
        if self._results is not None:
            for _pn, _rl in self._results.items():
                for _r in _rl:
                    if _r[0] == self.high_score_value:
                        return _r[1].groupdict()
        return {}

    @property
    def all_results (self) -> dict[str,list[tuple[int,re.Match]]]:
        """Returns the collection of found patterns by name, that coresponds to a list of score values and Match objects pairs"""
        return self._results if self._results is not None else {}

    @property
    def found_pattern_names (self) -> list[str]:
        """Returns the list of all found pattern names in line score"""
        return [_n for _n in self._results.keys()] if self._results is not None else []
    

    #------- Methods / Functions -------#

    @ToolBox_Decorator
    def reset_pattern (self):
        self._results = None
        self._score = None

    @ToolBox_Decorator
    def evaluate_pattern (self):
        """Will evaluate the assign or provided pattern aginst the stored string."""
        if self._results is None:
            self._results = {}
        for _pattern_name, _pattern in ToolBox_REGEX_Patterns.__members__.items():
            _results = re.finditer(_pattern, self._source_text, self._flag_val)
            if _results is not None:
                if _pattern_name not in self._results.keys():
                    self._results[_pattern_name] = []
                _score:int = 0 if (self._bonus_score is None) else self._bonus_score
                _pattern_name_parts = _pattern_name.split('_')
                if ((self._filter_patterns is not None) and 
                    (self._filter_AnyOrAll == ToolBox_Amount_Options.ALL) and 
                    not (all([_f.upper() in _pattern_name.upper() for _f in self._filter_patterns]))
                ):
                    for _f in self._filter_patterns:
                        if re.search(rf"(?:\b|_){_f}(?:\b|_)", _pattern_name, re.IGNORECASE):
                            _score += 20
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
                        self._results[_pattern_name].append((_score, _r))

    @ToolBox_Decorator
    def get_all_Match_results (self) -> list[tuple[str,int,list[tuple[str,Any,tuple[int, int]]]]]:
        _holder:list[tuple[str,int,list[tuple[str,Any,tuple[int, int]]]]] = []
        if self._results is not None:
            for _result_name, _score_data in self._results.items():
                for _score, _match in _score_data:
                    _values = []
                    for _m_id, (_k, _v) in enumerate(_match.groupdict().items()):
                        _values.append((_k, _v, _match.span(_m_id+1)))
                    _holder.append((_result_name, _score, _values))
        return _holder

class ToolBox_REGEX_text_score_evaluator (UserDict):
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
     
    #------- private properties -------#

    _source_text:str
    _source_lines:list[str]
    _score_holder: dict[int,ToolBox_line_score_data]
    _filter_AnyOrAll:ToolBox_Amount_Options|str|None
    _filter_patterns:list[str]|None
    _flag_list:list[re.RegexFlag]|None
    _flag_val:int

    #------- Initialize class -------#
    
    def __init__ (self, 
            source_text:str,
            filter_patterns:list[str]|None = None,
            filter_AnyOrAll:ToolBox_Amount_Options|str|None = None,
            flag_list:list[re.RegexFlag]|None = None,
            initial_data:dict[str,Any]|None = None
        ):
        super().__init__(initial_data)
        self._source_text = source_text if (source_text is None) or (source_text.strip()!='') else ''
        self._source_lines = self._source_text.splitlines()
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
        self._flag_list = flag_list or [re.IGNORECASE]
        if any(_p in source_text for _p in ['\n', '\r']) and re.MULTILINE not in self._flag_list:
            self._flag_list.append(re.MULTILINE)
        self._flag_val:int = sum(self._flag_list)
        self._score_holder = {}
        for _line_index, _line_str in enumerate(self._source_lines):
            _pattern_score_obj = ToolBox_line_score_data(
                source_index= _line_index,
                source_text= _line_str,
                filter_patterns=self._filter_patterns,
                filter_AnyOrAll=self._filter_AnyOrAll,
                flags=self._flag_list
            )
            if _pattern_score_obj.all_results is not None:
                self._score_holder[_line_index] = _pattern_score_obj
    
    def __setitem__(self, key, value):
        if isinstance(value, str):
            self.data[key] = value
        else:
            self.data[key] = value

    def __getitem__(self, key):
        if isinstance(key, str):
            key = key
        return self.data[key]
    
    def __repr__(self):
        return f"{type(self)} (source_text = {self._source_text})"
    
    #-------public Getter & Setter methods -------#

    @property
    def source_text (self) -> str:
        """Returns full source text of evaluator."""
        return self._source_text
    
    @property
    def statistics (self) -> str|None:
        """Returns a string of statistics and results as a multiline string."""
        _stats_text_holder:list[str] = []
        for _line_idx, _ToolBox_line_score_data in self._score_holder.items():
            _stats_text_holder.append(rf"line [{_line_idx}] | Score : [{_ToolBox_line_score_data.high_score_value}] | Pattern : {_ToolBox_line_score_data.high_score_pattern_names} | Text : '{_ToolBox_line_score_data.source_line_text}'")
            if _ToolBox_line_score_data.all_results is not None:
                for _pn, _pn_d in _ToolBox_line_score_data.all_results.items():
                    for _score, _match in _pn_d:
                        _stats_text_holder.append(f"    - '{_pn}' [{_score}] : {_match.groupdict()}")
                _stats_text_holder.append('')
        if len(_stats_text_holder) >= 1:
            return f"\n".join(_stats_text_holder)
        else:
            return None
        
    @property
    def all_results (self) -> list[ToolBox_line_score_data]:
        """Returns a list of ToolBox_line_score_data objects"""
        return [_sd for _sd in self._score_holder.values()]
    
    #------- Methods / Functions -------#

    @ToolBox_Decorator
    def get_scores_by_line_index (self, index:int, enable_clamp:bool=True) -> list[ToolBox_line_score_data]:
        """Returns the score data object that coresponds to the provided index.
        'enable_clamp' will return the first or last ToolBox_line_score_data object if the value is outside the range of index's found.
        """
        _index = max(0, min(index, len(self._score_holder.keys()))) if (enable_clamp == True) else index
        return [_sd for _sd in self._score_holder.values() if _sd._source_index == _index]
    
    @ToolBox_Decorator
    def get_scores_by_REGEX_Pattern_name (self, name:str) -> list[ToolBox_line_score_data]:
        """Returns the score data object that coresponds to the provided index."""
        _name = name if name in ToolBox_REGEX_Patterns._member_names_ else None
        return [_sd for _sd in self._score_holder.values() if (
            (_sd.high_score_pattern_names is not None) and 
            (_name in _sd.high_score_pattern_names)
        )] if _name is not None else []
    
    @ToolBox_Decorator
    def get_closest_to_pattern_and_index (self, name:str, index:int) -> ToolBox_line_score_data|None:
        """Returns the clostest ToolBox_line_score_data objects to the named REGEX pattern"""
        _name = name if name in ToolBox_REGEX_Patterns._member_names_ else None
        return min([_sd for _sd in self._score_holder.values() if (
            (_sd.high_score_pattern_names is not None) and 
            (_name in _sd.high_score_pattern_names)
        )], key=lambda x: abs(index - x.source_line_index)) if _name is not None else None
    
    @ToolBox_Decorator
    def get_patterns_between_indices (self, name:str, start_index:int, end_index:int) -> list[ToolBox_line_score_data]:
        """Returns the clostest ToolBox_line_score_data objects to the named REGEX pattern between the given line indicies"""
        _name = name if name in ToolBox_REGEX_Patterns._member_names_ else None
        return [_sd for _sd in self._score_holder.values() if (
            (start_index <= _sd.source_line_index <= end_index) and 
            (_sd.high_score_pattern_names is not None) and 
            (_name in _sd.high_score_pattern_names)
        )] if _name is not None else []
        