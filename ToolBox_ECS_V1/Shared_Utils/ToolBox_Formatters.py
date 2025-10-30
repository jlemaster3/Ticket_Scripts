#-------------------------------------------------
#   Imports
#-------------------------------------------------
import re, uuid
from enum import StrEnum
from typing import Literal, Any
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


def ToolBox_string_find_REGEX_patterns (
        source_text:str, 
        filter_patterns:list[str]|None=None, 
        filter_AnyOrAll:Literal[ToolBox_Amount_Options.ANY, ToolBox_Amount_Options.ALL] = ToolBox_Amount_Options.ANY,
        flags_list:list[re.RegexFlag] = [re.IGNORECASE|re.MULTILINE],
        quite_logging:bool = False,
    ) -> dict[str,list[dict[str,Any]]]:
    """tries to format the privided text based off the IWS REGEX patterns"""
    _line_pattern_list:list[list[ToolBox_REGEX_Patterns]] = ToolBox_REGEX_identify_patterns(source_text)
    # No patterns matched source string, return empty list.
    if (_line_pattern_list is None) and (len(_line_pattern_list) == 0): 
        return []
    # Mulitple patterns were found, find score value os patterns
    _source_lines = source_text.splitlines()
    _score_holder:dict[str,list[dict[str,Any]]] = {}
    _score_data = {
        'line_index' : -1,
        'patern_index' : 0,
        'pattern' : ToolBox_REGEX_Patterns.BLANK_LINE,
        'groups' : None,
        'score' : 0,
    }
    for _line_idx in range(len(_line_pattern_list)):
        if ((filter_patterns is not None) and (len(filter_patterns) >= 1)) and (filter_AnyOrAll == ToolBox_Amount_Options.ALL):
            _patternList = [_p for _p in _line_pattern_list[_line_idx] if all([_f.upper() in _p.upper() for _f in filter_patterns])]
        elif ((filter_patterns is not None) and (len(filter_patterns) >= 1)) and (filter_AnyOrAll == ToolBox_Amount_Options.ANY):
            _patternList = [_p for _p in _line_pattern_list[_line_idx] if any([_f.upper() in _p.upper() for _f in filter_patterns])]
        else:
            _patternList = _line_pattern_list[_line_idx]
        _source_line:str = _source_lines[_line_idx]
        if _source_line not in _score_holder.keys():
                _score_holder[_source_line] = []
        if _source_line is None or _source_line.strip() == '':
            _score_data = {
                'line_index' : _line_idx,
                'patern_index' : 0,
                'pattern' : ToolBox_REGEX_Patterns.BLANK_LINE,
                'groups' : None,
                'score' : 0,
            }
            log.debug (f"line : '{_source_line}' - High Score: [0] - Pattern(s) : ", data=[ToolBox_REGEX_Patterns.BLANK_LINE])    
            
            continue
        _flag_val:int = sum(flags_list)
        _high_score_val = None
        _high_score_pattern_list = []
        for _pattern_idx, _pattern in enumerate(_patternList):
            _score_val:int = 0
            _results = re.search(ToolBox_REGEX_Patterns[_pattern], _source_line, _flag_val)
            if _results:
                if (filter_patterns is not None):
                    _score_val += 10 * len([_s for _s in filter_patterns if _s.upper() in _pattern.upper()])
                _nonNone_group_ids = [_id for _id, _grp in enumerate(_results.groups()) if _grp is not None and _grp.strip() != '']
                _score_val -= 5 * abs(len(_results.groups())-len(_nonNone_group_ids))
                _score_val += 5 * len(_results.groups())
                _score_data = {
                    'line_index' : _line_idx,
                    'patern_index' : _pattern_idx,
                    'pattern' : _pattern,
                    'groups' : _results.groups(),
                    'score' : _score_val,
                }                    
                if (_high_score_val is None) or (_score_val > _high_score_val):
                    _high_score_val = _score_val
                    _high_score_pattern_list = [_pattern]
                elif (_score_val == _high_score_val):
                    _high_score_pattern_list.append(_pattern)
            _score_holder[_source_line].append(_score_data)        
        if (quite_logging != True) :
            log.debug (f"High Score: [{_high_score_val}] - line : '{_source_line}' - Pattern(s) [{len(_high_score_pattern_list)}]: {_high_score_pattern_list}")
            for _sd_idx, _s_data in enumerate(_score_holder[_source_line]):
                _score_groups = ', '.join([_p for _p in _s_data['groups'] if _p is not None]) if _s_data['groups'] is not None else 'None'
                log.blank(f"[{_sd_idx}] - Score : [{_s_data['score']}] - pattern : '{_s_data['pattern']} - found : [{_score_groups}]'")
    return _score_holder


def ToolBox_list_of_dictionaries_to_string (source_row_list:list[dict[str,Any]], include_row_idx:bool=True) -> str:
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

class ToolBox_REGEX_text_score_evaluator (UserDict):
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
     
    #------- private properties -------#

    _source_text:str
    _source_lines:list[str]
    _line_meta_data:dict[int,list[dict[str,Any]]]
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
        self._line_meta_data = {}    
        self._flag_val:int = sum(self._flag_list)
        for _line_index, _line_str in enumerate(self._source_lines):
            if _line_index not in self._line_meta_data.keys():
                self._line_meta_data[_line_index] = []
            for _pattern_name, _pattern in ToolBox_REGEX_Patterns._member_map_.items():
                _results = re.finditer(_pattern.value, _line_str, self._flag_val)
                _score_val:int = 0
                if _results is not None:
                    for _r_idx, _r in enumerate(_results):
                        if ((self._filter_patterns is not None) and 
                            (self._filter_AnyOrAll == ToolBox_Amount_Options.ALL) and 
                            not (all([_f.upper() in _pattern_name.upper() for _f in self._filter_patterns]))
                        ):
                            _score_val += 20
                        elif ((self._filter_patterns is not None) and 
                              (self._filter_AnyOrAll == ToolBox_Amount_Options.ANY) and 
                              not (any([_f.upper() in _pattern_name.upper() for _f in self._filter_patterns]))
                        ):
                            _score_val += 10
                        if isinstance(_r, re.Match):
                            _nonNone_groups = [_grp for _grp in _r.groups() if _grp is not None and _grp.strip() != '']
                            _reults_len:int = len(_r.groups())
                            if len(_nonNone_groups) >= 1:
                                _score_val += 5 * abs(_reults_len-len(_nonNone_groups))
                            else:
                                _score_val -= 10 *_reults_len
                            _score_val += 5 * _reults_len
                            if (self._filter_patterns is not None):
                                _score_val += 10 * len([_s for _s in self._filter_patterns if _s.upper() in _pattern_name.upper()])

                            _line_word_match_list = [_w for _w in re.finditer(r'\b\w+\b', _line_str)]
                            _start_word_idx = [_w_idx for _w_idx, _w in enumerate(_line_word_match_list) if _w.start() <= _r.start() <= _w.end()]
                            if len(_start_word_idx) >= 1:
                                _score_val += 5 * (len(_line_word_match_list) -_start_word_idx[0])
                            self._line_meta_data[_line_index].append({
                                "line_index":_line_index,
                                "pattern":_pattern,
                                "pattern_name": _pattern_name,
                                "groups": _r,
                                "score":_score_val
                            })
            if len(self._line_meta_data[_line_index]) == 0:
                self._line_meta_data[_line_index].append({
                    "line_index":_line_index,
                    "pattern": None,
                    "pattern_name": None,
                    "groups": None,
                    "score": None
                })

    
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
    def statistics (self) -> str:
        """Returns a string of statistics and results as a multiline string."""
        _stats_text_holder:list[str] = []
        for _idx in range(len(self._source_lines)):
            _lind_data =self.get_line_meta_data_by_index(_idx) or []
            _highest_score:int|None = None
            _high_score_pattern_list:list[ToolBox_REGEX_Patterns] = []
            _sub_debug_str:list[str] = []
            for _md_idx, _md in enumerate(_lind_data):
                if ('score' in _md.keys() and 'pattern_name' in _md.keys() and 'groups' in _md.keys()):
                    if (_highest_score is None) or (_md['score'] is not None and _md['score'] > _highest_score):
                        _highest_score = _md['score']
                        _high_score_pattern_list = [_md['pattern_name']]
                    elif (_highest_score is None and _md['score'] is not None and _md['score'] == _highest_score):
                        _high_score_pattern_list.append(_md['pattern_name'])
                    _sub_debug_str.append(rf"       {''*len(str(_idx))} [{_md_idx}] Score : [{_md['score']}] - Pattern : '{_md['pattern_name']}' - Group : [{_md['groups'].groups() if _md['groups'] is not None else None}]")
            _stats_text_holder.append(rf"line [{_idx}] text : '{self._source_lines[_idx]}' | High Score : [{_highest_score}] | Pattern(s) [{len(_high_score_pattern_list)}] : {_high_score_pattern_list}")
            _stats_text_holder.extend(_sub_debug_str)
            _stats_text_holder.append('')
        if len(_stats_text_holder) >= 1:
            return f"\n".join(_stats_text_holder)
        else:
            return ''
    
    @property
    def line_pattern_highest_score_list (self) -> list[tuple[str,int]]:
        """Returns the a list of patterns and score values of the highest scoring result(s) per line.
        Multiple patterns may be returned if they have teh same score value."""
        _pattern_score_list:list[tuple[str,int]] = []
        for _md_list in self._line_meta_data.values():
            for _md in _md_list:
                if ('score' in _md.keys()) and ('pattern' in _md.keys()):
                    _pattern_score_list.append((_md['pattern'], _md['score']))
        return _pattern_score_list
    
    #------- Methods / Functions -------#

    @ToolBox_Decorator
    def get_line_by_index (self, line_index:int = 0, clamp_index:bool = True) -> str|None:
        """Returns the line of text coresponding to the privided index.

        If clamp_index is set to True, then line_index will be set to 0 if below 0 or the last index if above the total number of lines.
        If clamp_index is set to False, any index outside of 0 to amx number of lines in source text will return None.
        """
        if clamp_index == True:
            _line_index = 0 if (line_index < 0) else line_index if (line_index < len(self._source_lines)) else len(self._source_lines)
        else:
            _line_index = None if (line_index < 0) else line_index if (line_index < len(self._source_lines)) else None
        return self._source_lines[_line_index] if _line_index is not None else None
    
    def get_line_pattern_names_by_index (self, line_index:int = 0, clamp_index:bool = True) -> list[ToolBox_REGEX_Patterns]|None:
        """Returns the line of text coresponding to the privided index.

        If clamp_index is set to True, then line_index will be set to 0 if below 0 or the last index if above the total number of lines.
        If clamp_index is set to False, any index outside of 0 to amx number of lines in source text will return None.
        """
        if clamp_index == True:
            _line_index = 0 if (line_index < 0) else line_index if (line_index < len(self._source_lines)) else len(self._source_lines)
        else:
            _line_index = None if (line_index < 0) else line_index if (line_index < len(self._source_lines)) else None
        return self.get_line_patterns()[_line_index] if _line_index is not None else None

    @ToolBox_Decorator
    def get_line_meta_data_by_index (self, line_index:int, clamp_index:bool = True) -> list[dict[str,Any]]|None:
        """Returns the patterns found for the coresponding index.

        If clamp_index is set to True, then line_index will be set to 0 if below 0 or the last index if above the total number of lines.
        If clamp_index is set to False, any index outside of 0 to amx number of lines in source text will return None.
        """
        if clamp_index == True:
            _line_index = 0 if (line_index < 0) else line_index if (line_index < len(self._source_lines)) else len(self._source_lines)
        else:
            _line_index = None if (line_index < 0) else line_index if (line_index < len(self._source_lines)) else None
        return self._line_meta_data[_line_index] if _line_index is not None else None
    
    def get_line_patterns (self) -> list[list[ToolBox_REGEX_Patterns]]:
        """Returns a list of patterns for each line in source text."""
        return [_md['pattern'].name for _mdlist in self._line_meta_data.values() for _md in _mdlist]
    
    def get_line_pattern_scores (self) -> list[list[int]]:
        """Returns a list of patterns for the coresponding line index."""
        return [_md['score'] for _mdlist in self._line_meta_data.values() for _md in _mdlist]
    
    def get_line_pattern_results (self) -> list[list[re.Match]]:
        """Returns a list of Matches from the patthern aginst the coresponding line index."""
        return [_md['groups'] for _mdlist in self._line_meta_data.values() for _md in _mdlist]
    