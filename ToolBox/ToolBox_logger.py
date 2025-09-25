#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, sys, logging, threading, json
from typing import Any
from datetime import datetime as dt

#-------------------------------------------------
#   Logger Classes
#-------------------------------------------------

class OutputLogger(logging.Logger):
    _instance = None
    _lock = threading.Lock()  # Ensures thread-safe singleton creation
    _log_name:str = "IWS_ToolBox"
    _log_folder:str = None
    _log_fileName:str = None
    _log_level:int = None

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

    def init_logger(self, log_folder=None, log_file=None, level=logging.DEBUG):        
        # Use instance variables set in __new__
        _log_folder = log_folder
        _log_file = self._log_fileName if self._log_fileName is not None else log_file if log_file is not None else f"{self._log_name}_{str(dt.now().date()).replace('-','')}.log"  
        _level = self._log_level if self._log_level is not None else level
        
        if log_folder == None and getattr(sys, 'frozen', False):
            _log_folder = os.path.dirname(sys.executable)
        elif log_folder == None and __file__:
            _log_folder = os.path.dirname(os.path.abspath(__file__))

        os.makedirs(_log_folder, exist_ok=True)
        super().__init__(self._log_name, _level)
        _log_path = os.path.join(_log_folder, _log_file)
        _fileHandler = logging.FileHandler(_log_path, mode='w', encoding='utf-8')
        _fileHandler.setLevel(_level)
        _formatter = logging.Formatter('{asctime} | {levelname:<8s} | {funcName} | {message}', datefmt="%Y-%m-%d %H:%M:%S", style='{')
        _fileHandler.setFormatter(_formatter)
        self.addHandler(_fileHandler)
        _streamHandler = logging.StreamHandler()
        _streamHandler.setLevel(logging.WARNING)
        _streamHandler.setFormatter(_formatter)
        self.addHandler(_streamHandler)
        self.propagate = True 

    @classmethod
    def get_instance(self) -> "OutputLogger":
        """Returns the singleton instance of OutputLogger."""
        return self._instance

    def _log_with_data(self, level, message, data=None, *args, **kwargs):
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
                    _str = "[" + ', '.join ([format_val(_s) for _s in val]) + "]"
                    return _str
                case _:
                    return (str(val))
                
        if data is None and args:
            data, *args = args
        if data is not None:
            try:
                # Normalize callables
                if callable(data):
                    data = str(data)  # or data() if you want to execute it!
                # Normalize primitive types (int/float/bool) by wrapping
                # so they become valid JSON root types
                if isinstance(data, (str, dict, list, int, float, bool)):
                    data_str = format_val (data)
                else:
                    # fallback for anything else
                    json_str = json.dumps(str(data), ensure_ascii=False)
            except Exception:
                # If serialization fails, just coerce to string
                data_str = str(data)
            message = f"{message} | {type(data)} - {data_str}"
        self.log(level, message, *(), stacklevel=3, **kwargs)
        
    def debug(self, message, data=None, *args, **kwargs):
        self._log_with_data(logging.DEBUG, message, data, *args, **kwargs)

    def info(self, message, data=None, *args, **kwargs):
        self._log_with_data(logging.INFO, message, data, *args, **kwargs)

    def warning(self, message, data=None, *args, **kwargs):
        self._log_with_data(logging.WARNING, message, data, *args, **kwargs)

    def error(self, message, data=None, *args, **kwargs):
        self._log_with_data(logging.ERROR, message, data, *args, **kwargs)

    def critical(self, message, data=None, *args, **kwargs):
        self._log_with_data(logging.CRITICAL, message, data, *args, **kwargs)