#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, sys, logging, threading, json
from typing import Any, List, Optional, Union
from datetime import datetime as dt
from enum import Enum

#-------------------------------------------------
#   Enumerations
#-------------------------------------------------

class OutputLoggingLevel (Enum):
    LABEL = logging.INFO + 1
    BLANK = logging.WARNING - 1

#-------------------------------------------------
#   Formating Classes and Functions
#-------------------------------------------------

class BlankLineFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == OutputLoggingLevel.BLANK:
            return "\n"
        return super().format(record)
    
def format_list_as_table (
        source_list: List[str|int|float|bool],
        deliniator: str = ',',
        column_padding: int = 0,
        max_row_characters: Optional[int] = None,
        max_items_per_row: Optional[int] = 8
    ) -> str:
    """Converts the provided list of string, integers, flaots, and boolean values into a string that dispalys as table."""
    # If both max_row_characters and max_items_per_row are set to 0
    if (max_row_characters in (0, None)) and (max_items_per_row in (0, None)):
        return '\n'.join([str(_e) for _e in source_list])
    _str_list = [f"{item}" for item in source_list]
    if max_row_characters not in (-1, None):
        _widths = [len(s) for s in _str_list]
        _rows = []
        _current_row = []
        _current_len = 0
        for s, w in zip(_str_list, _widths):
            _padded_width = w + (column_padding * 2) + len(deliniator)
            if _current_len + _padded_width > max_row_characters and _current_row:
                _rows.append(_current_row)
                _current_row = [s]
                _current_len = w + (column_padding * 2) + len(deliniator)
            else:
                _current_row.append(s)
                _current_len += _padded_width
        if _current_row:
            _rows.append(_current_row)
    elif max_items_per_row not in (-1, None):
        _rows = [ _str_list[_i:_i + max_items_per_row] for _i in range(0, len(_str_list), max_items_per_row)]
    else:
        return '\n'.join([str(_e) for _e in source_list])
    # Compute column widths (based on longest string in each column)
    _max_cols = max(len(_row) for _row in _rows)
    _col_widths = [0] * _max_cols
    for _row in _rows:
        for _i, _item in enumerate(_row):
            _col_widths[_i] = max(_col_widths[_i], len(_item))
    _formatted_rows = []
    for _row in _rows:
        padded_items = [f"{item:<{_col_widths[i] + column_padding}}" for i, item in enumerate(_row)]
        _formatted_rows.append(f" {deliniator} ".join(padded_items).rstrip())
    return '\n'.join(_formatted_rows)
        
#-------------------------------------------------
#   Logger Classes
#-------------------------------------------------

class OutputLogger(logging.Logger):
    _instance = None
    _lock = threading.Lock()  # Ensures thread-safe singleton creation
    _log_name:str
    _log_folder:str|None
    _log_fileName:str|None
    _log_level:int
    _formatter:logging.Formatter
    _blankformatter:BlankLineFormatter

    def __new__(cls, log_folder=None, log_file=None, level=logging.DEBUG, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
                cls._log_folder = log_folder
                cls._log_fileName = log_file
                cls._log_level = level
            return cls._instance

    def __init__ (self, log_folder=None, log_file=None, level=logging.DEBUG):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

    def init_logger(self, log_folder:str|None=None, log_file:str|None=None, level=logging.DEBUG):        
        # Use instance variables set in __new__
        _log_folder = log_folder
        _log_file = self._log_fileName if self._log_fileName is not None else log_file if log_file is not None else f"{self._log_name}_{str(dt.now().date()).replace('-','')}.log"  
        _level = self._log_level if self._log_level is not None else level
        
        if log_folder == None and getattr(sys, 'frozen', False):
            _log_folder = os.path.dirname(sys.executable)
        elif log_folder == None and __file__:
            _log_folder = os.path.dirname(os.path.abspath(__file__))
        if _log_folder is not None:
            os.makedirs(_log_folder, exist_ok=True)
            super().__init__(name = _log_file, level = _level)

            _log_path = os.path.join(_log_folder, _log_file)
            _fileHandler = logging.FileHandler(_log_path, mode='w', encoding='utf-8')
            _fileHandler.setLevel(_level)
            self._formatter = logging.Formatter('{asctime} | {levelname:<8s} | {funcName:<40} | {message}', datefmt="%Y-%m-%d %H:%M:%S", style='{')
            self._blankformatter = BlankLineFormatter()
            _fileHandler.setFormatter(self._formatter)
            self.addHandler(_fileHandler)
            _streamHandler = logging.StreamHandler()
            _streamHandler.setLevel(logging.WARNING)
            _streamHandler.setFormatter(self._formatter)
            self.addHandler(_streamHandler)
            self.propagate = True 

    @classmethod
    def get_instance(cls) -> "OutputLogger":
        """Returns the singleton instance of OutputLogger."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


    def _log_with_data(self, level, message:str|None, data=None, list_data_as_table:bool=False, column_count:int|None=None, *args, **kwargs):
        """
        Overrides the default log method to provide custom behavior if needed.
        This method delegates to the underlying logging.Logger's log method.
        """
        def format_val (val:Any, indent:int=0) -> str:
            _indent = indent + 2
            match val:
                case str():
                   return (f'"{val}"')
                case dict():
                    _str = ' ' * indent+"{"
                    for _c, (_k,_v) in enumerate(val.items()):
                        _str += '\n'+' ' * _indent + f"{format_val(_k, _indent)} = {format_val(_v, _indent)}"
                    _str += '\n'+' ' * indent+'}'
                    return _str
                case list():
                    if (list_data_as_table == True):
                        _str = "[" +('\n' if column_count == 1 else '')+ format_list_as_table(val, max_items_per_row=column_count) + ('\n' if column_count == 1 else '') +"]"
                    else:
                        _str = "[" + ', '.join ([format_val(_s) for _s in val]) + "]"
                    return _str
                case _:
                    return (str(val))

        if data is None and args:
            data, *args = args
        if data is not None:
            data_str:str = ''
            try:
                # Normalize callables
                if callable(data):
                    data = str(data)  # or data() if you want to execute it!
                # Normalize primitive types (int/float/bool) by wrapping
                # so they become valid JSON root types
                if isinstance(data, (str, dict, list, int, float, bool)):
                    if (list_data_as_table == True and isinstance(data, list)):
                        data_str = "\n" + format_list_as_table(data, max_items_per_row=column_count)
                    else:
                        data_str = format_val (data)
                else:
                    # fallback for anything else
                    data_str = json.dumps(str(data), ensure_ascii=False)
            except Exception:
                # If serialization fails, just coerce to string
                data_str = str(data)
            message = rf"{message} | {type(data)} - {data_str}"
        self.log(level, message, *(), stacklevel=3, **kwargs)
        
    def debug(self, message:str|None, data=None, list_data_as_table:bool = False, column_count:int = 8, *args, **kwargs):
        self._log_with_data(logging.DEBUG, message, data, list_data_as_table, column_count, *args, **kwargs)

    def info(self, message:str|None, data=None, list_data_as_table:bool = False, column_count:int = 8, *args, **kwargs):
        self._log_with_data(logging.INFO, message, data, list_data_as_table, column_count, *args, **kwargs)

    def label(self, message:str|None, data=None, list_data_as_table:bool = False, column_count:int = 8, *args, **kwargs):
        self._log_with_data(OutputLoggingLevel.LABEL.value, message, data, list_data_as_table, column_count, *args, **kwargs)
    
    def blank(self, message:str|None=None, data=None, list_data_as_table:bool = False, column_count:int = 8, *args, **kwargs):
        for h in self.handlers:
            h.setFormatter( self._blankformatter)
        self._log_with_data(OutputLoggingLevel.BLANK.value, message, data, list_data_as_table, column_count, *args, **kwargs)
        for h in self.handlers:
            h.setFormatter( self._formatter)

    def warning(self, message:str|None, data=None, list_data_as_table:bool = False, column_count:int = 8, *args, **kwargs):
        self._log_with_data(logging.WARNING, message, data, list_data_as_table, column_count, *args, **kwargs)

    def error(self, message:str|None, data=None, list_data_as_table:bool = False, column_count:int = 8, *args, **kwargs):
        self._log_with_data(logging.ERROR, message, data, list_data_as_table, column_count, *args, **kwargs)

    def critical(self, message:str|None, data=None, list_data_as_table:bool = False, column_count:int = 8, *args, **kwargs):
        self._log_with_data(logging.CRITICAL, message, data, list_data_as_table, column_count, *args, **kwargs)


for level in OutputLoggingLevel:
    logging.addLevelName(level.value, level.name)
    setattr(logging, level.name, level.value)
    _arget_method = getattr(OutputLogger, level.name.lower())
    setattr(logging.getLoggerClass(), level.name.lower(), _arget_method)