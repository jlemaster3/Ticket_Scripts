#-------------------------------------------------
#   Imports
#-------------------------------------------------

import logging, os, re, json, sys, uuid, copy

import threading

from collections import UserDict
from enum import Enum, StrEnum
from datetime import datetime as dt
from typing import Any, Callable, Dict, Optional

#-------------------------------------------------
#   Enum Classes
#-------------------------------------------------

class LogLevel(Enum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

class ValidIWSFileFormat(StrEnum):
    JIL = 'jil'
    JOB = 'job'
    #YAML = 'yaml'
    #CSV = 'csv'
    #ps1 = 'ps1'

class ValidConfigFileFormat(StrEnum):
    JSON = 'json'

#-------------------------------------------------
#   Logger Classes
#-------------------------------------------------

class OutputLogger(logging.Logger):
    _instance = None
    _lock = threading.Lock()  # Ensures thread-safe singleton creation

    def __new__(cls, log_folder:str=None, log_file:str=f"log_{str(dt.now().date()).replace('-','')}.log"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(OutputLogger, cls).__new__(cls)
            return cls._instance

    def __init__ (self, log_folder:str=None, log_file: str=f"log_{str(dt.now().date()).replace('-','')}.log", level: int = logging.DEBUG):
        if getattr(self, "_initialized", False):
            return
        _folder_path = None
        if (log_folder != None and os.path.exists(log_folder) and os.path.isdir(log_folder)):
            _folder_path = log_folder  
        elif getattr(sys, 'frozen', False):
            _folder_path = os.path.dirname(sys.executable)
        elif __file__:
            _folder_path = os.path.dirname(os.path.abspath(__file__))
        logging.Logger.__init__(self, name="App", level=level)
        os.makedirs(_folder_path, exist_ok=True)
        log_path = os.path.join(_folder_path, log_file)
        # File handler
        fh = logging.FileHandler(log_path, encoding="utf-8", mode='w')
        fh.setLevel(level)
        file_format = logging.Formatter('{asctime} | {levelname:<8s} | {funcName} | {message}',datefmt="%Y-%m-%d %H:%M:%S", style='{')
        fh.setFormatter(file_format)
        self.addHandler(fh)
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        console_format = logging.Formatter("[%(levelname)s]: %(message)s")
        ch.setFormatter(console_format)
        self.addHandler(ch)
        self._initialized = True

    def get_logger(self):
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

#-------------------------------------------------
#   Data container Classes
#-------------------------------------------------

class Found_File_Path:
    """Contains data about file locations, does not contain file data or refrences to internal file values."""
    _name:str
    _foramt:str
    _rootPath:str
    _fullPath:str
    _relPath:str
    _logger:OutputLogger = OutputLogger().get_logger()
    _delimiter = "."

    def __init__ (self, sourcePath:str, rootPath:str|None=None) :
        if (not os.path.exists (sourcePath) or (not os.path.isfile(sourcePath))):
            self._logger.log(LogLevel.WARNING, f"Source file does not exist : '{sourcePath}'")
            return
        self._fullPath = sourcePath
        _base_split = os.path.basename(self._fullPath).split('.')
        self._name = _base_split[0].strip()
        self._foramt = _base_split[1].strip().lower()
        if (rootPath is not None and os.path.exists(rootPath)): 
            self._rootPath = rootPath
            self.set_relPath_from_rootPath(rootPath)

    @property
    def name(self):
        """Getter method for 'name' attribute."""
        return self._name
    @property
    def format(self):
        """Getter method for 'foramt' attribute."""
        return self._foramt
    @property
    def fullPath(self):
        """Getter method for 'fullPath' attribute."""
        return self._fullPath
    
    @property
    def rootPath(self):
        """Getter method for 'rootPath' attribute."""
        return self._rootPath
    
    @property
    def relPath(self):
        """Getter method for 'relPath' attribute."""
        return self._relPath

    def set_relPath_from_rootPath (self, rootPath:str) -> str:
        """Determins relitave path from provided root path"""
        if (not os.path.exists (rootPath) or (not os.path.isdir(rootPath))):
            self._logger.warning(f"Provided root path does not exist : '{rootPath}'")
            return
        elif (rootPath.lower() not in self._fullPath.lower()):            
            self._logger.warning(f"Provided rootPath can not be found in file's source path.\n   filePath: '{self._fullPath}'\n   rootPath: '{rootPath}'")
        self._relPath = os.path.relpath(os.path.dirname(self.fullPath), self._rootPath)
        return self._relPath


class Loaded_Config_File (Found_File_Path):
    """Loads and stores data found in designated Config files."""
    _data:dict[str,Any] = {}
    _delimiter = "."

    def __init__ (self, sourcePath:str, rootPath:str|None=None):
        super(sourcePath, rootPath)

    def loadFile (self) :
        """Loads data found in target config file in self._fullPath"""
        if self._fullPath.strip().lower().endswith('.json'):
            self._data = json.loads(self._fullPath)
        if self._fullPath.strip().lower().endswith('.yaml'):
            self._data = json.loads(self._fullPath)

    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Retrieves a value from the settings dictionary using a delimiter-separated key."""
        keys = key.split(cls._delimiter)
        value = cls._data
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
        
    @classmethod
    def __getitem__(cls, key: str) -> Any:
        return cls.get(key)


class Loaded_File_Data (UserDict):
    """Loads and stores data found in target source file"""
    _logger:OutputLogger = OutputLogger().get_logger()
    _sourceFile:str = None
    _foundFilePath:Found_File_Path = None
    _format:str = None
    _rawLines:list[str] = []
    _modifiedLines:list[str] = []
    _canSearch:bool = False
    _searchTerm_ids:dict[int, list[int]] = {}
    _stream_start_ids:list[int] = []
    _stream_edge_ids:list[int] = []
    _stream_END_ids:list[int] = []
    _job_start_ids:list[int] = []
    _DOCOMMAND_ids:list[int] = []
    _RUNCYCLE_ids:list[int] = []
    _EXCEPT_ids:list[int] = []
    _STREAMLOGON_ids:list[int] = []
    _DESCRIPTION_ids:list[int] = []
    _DRAFT_ids:list[int] = []
    _FOLLOWS_ids:list[int] = []
    _TASKTYPE_ids:list = []
    _OUTPUTCOND_ids:list = []
    _RECOVERY_ids:list[int] = []
    _NOP_ids:list[int] = []
    
    def __init__(self, sourceFile:str|Found_File_Path):
        try:
            _path = sourceFile if isinstance(sourceFile, str) else sourceFile.fullPath
            if not(os.path.isfile(_path)):
                self._logger.error(f"Target source path is not a valid file : '{_path}'")
                return
            super().__init__()
            self._sourceFile = _path
            self._foundFilePath = sourceFile if isinstance(sourceFile, Found_File_Path) else None
            self._format = str(os.path.basename(_path)).split('.')[-1]
            source_file = open(_path, "r")
            _rawText = source_file.read()
            self._rawLines = str(_rawText).split('\n')
            self._copy_rawText()
            self._sort_line_ids()

        except FileExistsError as fxe:
            self._logger.error(f"Invalid file path : '{sourceFile}' - {fxe}")

    def __setItem__ (self, key:str, value:Any):
        if not isinstance(key,str):
            raise TypeError("Keys must be string values.")
        self.data[key] = value

    def _copy_rawText (self):
        self._modifiedLines = copy.deepcopy(self._rawLines)
        self._canSearch = True if (len(self._rawLines) >= 1 and len(self._modifiedLines) >= 1) else False
    
    def _clear_line_ids (self):
        self._searchTerm_ids = {}
        self._stream_start_ids = []
        self._stream_edge_ids = []
        self._stream_END_ids = []
        self._job_start_ids = []
        self._DOCOMMAND_ids = []
        self._RUNCYCLE_ids = []
        self._EXCEPT_ids = []
        self._STREAMLOGON_ids = []
        self._DESCRIPTION_ids = []
        self._DRAFT_ids = []
        self._FOLLOWS_ids = []
        self._TASKTYP = []
        self._OUTPUTCON = []
        self._RECOVERY_ids = []
        self._NOP_ids = []

    def _sort_line_ids (self):
        if len(self._rawLines) == 0:
            self._logger.warning (f"No lines loaded form source file : '{self._sourceFile}'")
        for _line_id, _line in enumerate(self._rawLines):
            if "SCHEDULE" in str(_line).strip()[0:9]:
                self._stream_start_ids.append(_line_id)
            if 'DRAFT' in _line:
                self._DRAFT_ids.append(_line_id)
            if ':' in _line[0:2]:
                self._stream_edge_ids.append(_line_id)
            if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) or (any(_s in str(_line).strip()[0:5] for _s in ['PRD#', 'NPR#'])) and ('#' in str(_line[2:]).strip()):
                self._job_start_ids.append(_line_id)
            if 'DESCRIPTION' in _line:
                self._DESCRIPTION_ids.append(_line_id)
            if 'RUNCYCLE' in _line:
                self._RUNCYCLE_ids.append(_line_id)
            if 'FOLLOWS' in _line:
                self._FOLLOWS_ids.append(_line_id)
            if 'EXCEPT' in _line:
                self._EXCEPT_ids.append(_line_id)
            if 'DOCOMMAND' in _line:
                self._DOCOMMAND_ids.append(_line_id)
            if 'STREAMLOGON' in _line:
                self._STREAMLOGON_ids.append(_line_id)
            if 'OUTPUTCOND' in _line:
                self._OUTPUTCOND_ids.append(_line_id)
            if 'TASKTYPE' in _line:
                self._TASKTYPE_ids.append(_line_id)
            if 'RECOVERY' in _line:
                self._RECOVERY_ids.append(_line_id)
            if 'NOP' in _line:
                self._NOP_ids.append(_line_id)   
            if "END" in str(_line).strip()[0:4] and 'ENDJOIN' not in str(_line).strip():
                self._stream_END_ids.append(_line_id)

    @property
    def is_searchable (self) -> bool:
        self._canSearch = True if (len(self._rawLines) >= 1 and len(self._modifiedLines) >= 1) else False
        return self._canSearch
    
    @property
    def sourceFile(self) -> str:
        """Getter method for 'relPath' attribute."""
        return self._sourceFile
    
    @property
    def jobStreamStartIndicies(self) -> list[int]:
        """Getter method for 'relPath' attribute."""
        return self._stream_start_ids
    
    @property
    def raw_text (self) -> str:
        """Returns the raw text from the source file un-edited."""
        return str('\n'.join(self._rawLines))
    
    @property
    def modified_text (self) -> str:
        """returns the modified text as stored in memory."""
        return str('\n'.join(self._modifiedLines))
    

    def search (self, terms:list[str], useRegExpess:bool=False) -> dict[str,list[tuple]]:
        if (len(terms) == 0) or all(len(_str) == 0 for _str in terms):
            self._logger.error(f"Invalid terms list, espected list of strings, received : ", terms)
            return None
        if (self.is_searchable == False or len(self._modifiedLines) == 0):
            self._logger.error(f"Unable to search file, may ned to resync text.")
            return None
        _found_terms:dict[str,list[tuple]] = {}
        for _lineid, _line in enumerate(self._modifiedLines):
            for _term in terms:
                if useRegExpess == True:
                    _pattern = re.escape(_term)
                    _found = [(m.start(0), m.end(0)) for m in re.finditer(_pattern, _line)]
                    if len(_found) >= 1:
                        if _term not in _found_terms.keys():
                            _found_terms[_term] = []
                        _found_terms[_term].append((_lineid, _found[0]))
                else:
                    _start_index = 0
                    while True:
                        _index = _line.find(_term, _start_index)
                        if _index == -1:
                            break
                        if _term not in _found_terms.keys():
                            _found_terms[_term] = []
                        _found_terms[_term].append((_lineid, _index))
                        _start_index = _index + len(_term)
        for _t, _idList in _found_terms.items():
            if _t not in self._searchTerm_ids.keys():
                self._searchTerm_ids[_t] = _idList
                continue
            self._searchTerm_ids[_t].extend(_idList)
        return _found_terms


    def get_foundSearchTerms (self) -> dict[str,list[tuple]]:
        """Returns collection of found terms, the lines they are found on and the index on the line for each instance of the term found."""
        return self._searchTerm_ids

        

        
        
    

#-------------------------------------------------
#   IWS_ToolBox Class
#-------------------------------------------------

class IWS_ToolBox:
    logger:OutputLogger
    logStreamHandler:logging.StreamHandler = None
    logFileHandler:logging.FileHandler = None
    logFileName:str = None
    targetWorkingDir:str = None
    targetOutputDir:str = None

    sourceFileFormats:list[str] = [fmt.value for fmt in ValidIWSFileFormat]
    configFileFormats:list[str] = [fmt.value for fmt in ValidConfigFileFormat]

    sourcePaths:list[str] = []
    sourceFilePaths:list[Found_File_Path] = []
    loadedConfigFiles:list[Loaded_Config_File] = []
    loadedFileData:dict[str,Loaded_File_Data] = {}

    # folder path and file terms to isolate or exclude from processing
    excludeDirNames:list[str] = []
    excludeFileNames:list[str] = []
    excludeFileFormats:list[str] = []
    includeDirNames:list[str] = []
    includeFileNames:list[str] = []
    includeFileFormats:list[str] = []
    
    # File content search terms to isolate or exclude from processing
    excludeTerms:list[str] = []
    searchReplaceTerms:dict[str,str] = {}
    searchTerms:list[str] = []


    def __init__ (self, workingDirectoryPath:str=None, logFileName:str|None=None):
        if (workingDirectoryPath != None and os.path.exists(workingDirectoryPath) and os.path.isdir(workingDirectoryPath)):
            self.targetWorkingDir = workingDirectoryPath  
        elif getattr(sys, 'frozen', False):
            self.targetWorkingDir = os.path.dirname(sys.executable)
        elif __file__:
            self.targetWorkingDir = os.path.dirname(os.path.abspath(__file__))
          
        self.logFileName = logFileName if (logFileName is not None) else f"log_{str(dt.now().date()).replace('-','')}.log"
        self.logger = OutputLogger(self.targetWorkingDir, self.logFileName)


    def add_sourcePath (self, sourcePath:str) -> list[str]:
        """Adds Directory or Folder path to source path list, used when collecting and filtering files."""
        if os.path.exists(sourcePath) and os.path.isdir(sourcePath):
            if sourcePath not in self.sourcePaths:
                self.logger.debug(f"Added to sourcePath list : '{sourcePath}'")
                self.sourcePaths.append(sourcePath)
            else:
                self.logger.debug(f"Skipping source Path '{sourcePath}' - alredy loaded or not a valid folder path.")
        return self.sourcePaths


    def collectSourceFiles (self) -> list[dict[str,str]]:
        """Gathers refferences to all files in each provided source path, filtering for file formats, directory paths, and file names"""
        if len(self.sourcePaths) == 0 :
            self.logger.warning("Unable to collect source files, no source paths have been loaded, use IWS_ToolBox.add_sourcePath() first to add a path")
        _known_file_formats = set([fmt.lower() for fmt in self.sourceFileFormats])# + [e for e in self.configFileFormats])
        self.logger.info(f"Valid File Formats", data=self.sourceFileFormats)
        self.logger.info(f"Valid Config File Formats", data=self.configFileFormats)
        if len(self.includeDirNames) >= 1 : self.logger.info(f"Including Directory Paths containeing terms : ", data=self.includeDirNames)
        if len(self.includeFileNames) >= 1 : self.logger.info(f"Including File Names containing Terms : ", data=self.includeFileNames)
        if len(self.excludeDirNames) >= 1 : self.logger.info(f"Exclude Directory Paths containing Terms : ", data=self.excludeDirNames)
        if len(self.excludeFileNames) >= 1 : self.logger.info(f"Exclude Files Names containing Terms : ", data=self.excludeFileNames)
        if len(self.excludeTerms) >= 1 : self.logger.info(f"Exclude Terms : ", data=self.excludeTerms)
        
        _totalCounter = 0
        _collectedCounter = 0
        _relPaths = {}
        for _path in self.sourcePaths:
            if not(os.path.exists(_path)):
                self.logger.warning(f"Unable to find path in sourcePaths List. target Path: '{_path}'")
                continue
            for dir_path, dirs, files in os.walk(_path):
                for file in files:
                    _totalCounter +=1
                    _should_add:bool = True
                    _excludeText = []
                    _filePath = os.path.join(dir_path,file)
                    if (len(self.includeDirNames) >= 1):
                        for _dir in self.includeDirNames:
                            if _dir.lower() not in dir_path.lower():
                                _excludeText.append(f"Directory path does not contain any include terms: '{_dir}'")
                                _should_add = False
                    
                    if (len(self.includeFileNames) >= 1):
                        for _incdflnm in self.includeFileNames:
                            if _incdflnm.lower() not in os.path.basename(dir_path).lower():
                                _excludeText.append(f"Directory path does not contain any include terms: '{_incdflnm}'")
                                _should_add = False
                    
                    #Checks if directory path contains excluded directory term
                    for _excludeDir in self.excludeDirNames:
                        if (_excludeDir.lower() in dir_path.lower()) or (_excludeDir.lower() == dir_path.lower()):
                            _excludeText.append(f"File path contains excluded directory term : '{_excludeDir}'")
                            _should_add = False
                    #Checks if file foramt ends with and of the known formats.
                    if not any([file.lower().endswith(fmt) for fmt in _known_file_formats]):
                        _excludeText.append(f"File is not correct File Format : '*.{str(os.path.basename(file)).split('.')[-1]}'")
                        _should_add = False
                    
                    #Checks is file should be added to data set:
                    if (_should_add == False):
                        _reasons = ', '.join([f'"{_sc+1}":"{_str}"' for _sc, _str in enumerate(_excludeText)])
                        self.logger.debug(f"Excluding File from collection : '{_filePath}' | {_reasons}")
                    else:
                        self.logger.debug(f"Adding File to collection : '{_filePath}'")
                        _new_file = Found_File_Path(_filePath, _path)
                        if _new_file.relPath not in _relPaths.keys():
                            _relPaths[_new_file.relPath] = []
                        
                        _relPaths[_new_file.relPath].append(file)
                        self.sourceFilePaths.append(_new_file)
                        _collectedCounter += 1
        self.logger.info(f"Found [{_collectedCounter}] Files out of [{_totalCounter}] files.")
        self.logger.info(f"from [{len(_relPaths)}] directories:",data = _relPaths)
        return [_p.fullPath for _p in self.sourceFilePaths]

    
    def loadCollectedFiles(self, filePathList:list[str]=None):
        """Loads each file in provided path list."""
        if filePathList == None:
            _pathlist = self.sourcePaths
        else:
            _pathlist = filePathList
        self.logger.info(f"Loading [{len(filePathList)}] files in collection")
        _loaded_counter = 0
        for _fp in _pathlist:
            _did_load = self.loadFile(_fp)
            if (_did_load == True):
                _loaded_counter += 1
        self.logger.info(f"Loaded [{len(filePathList)}] files into memory")


    def loadFile (self, sourcePath:str) -> bool:
        """Loads provided file"""
        def _find_sourcePath (targetPath:str) -> int:
            for _idx, _pth in enumerate(self.sourceFilePaths):
                if isinstance(_pth, Found_File_Path) and (targetPath.lower() == _pth.fullPath.lower()):
                    return _idx
            return -1
        
        if isinstance(sourcePath, str):
            if not(os.path.exists(sourcePath)):
                self.logger.error(f"Target source path does nto exists : ", sourcePath)
                return False
            _foramt = os.path.basename(sourcePath).split('.')[-1]
            if not(os.path.isfile(sourcePath)) or (_foramt.lower() not in [_fmt.lower() for _fmt in self.sourceFileFormats]):
                self.logger.error(f"Target source path is not a valid file : ", sourcePath)
                return False
        try:
            _collected_id = _find_sourcePath(sourcePath)
            if (_collected_id != -1):
                _loaded_file = Loaded_File_Data(self.sourceFilePaths[_collected_id])
            else:
                _loaded_file = Loaded_File_Data(sourcePath)

            if (_loaded_file is not None) and (isinstance(_loaded_file, Loaded_File_Data)):
                self.loadedFileData[os.path.basename(_loaded_file.sourceFile)] = _loaded_file
            return True
        except PermissionError as err:
            self.logger.error(f"Not enough permissions to load file from path: '{sourcePath}' - {err}")
            return False
        except FileExistsError as err:
            self.logger.error(f"Unable to load file from path: '{sourcePath}' - {err}")
            return False
    

    def files_by_terms (self, searchTermList:list[str]=None) -> dict[str,list[str]]:
        """Returns a collection of found terms ans the file that contain them"""
        _searchList = searchTermList if isinstance(searchTermList, list) else self.searchTerms
        if (len(_searchList) == 0) or (_searchList is None):
            self.logger.warning(f"No search terms provided or found in toolbox.")
            return None
        _foundterms = {}
        for _file, _data in self.loadedFileData.items():
            _found = _data.search(_searchList)
            if len(_found.keys()) != 0:
                for _k in _found.keys():
                    if _k not in _foundterms.keys():
                        _foundterms[_k] = []
                    _foundterms[_k].append(_file)
        if len(_foundterms.keys()) >=1 :
            _counts = {}
            for _k, _v in _foundterms.items():
                if _k not in _counts.keys():
                        _counts[_k] = (len(_v), _v)
            _sum = sum([_v[1][0] for _v in _counts.items()])
            self.logger.info(f"Found [{_sum}] results when searching for [{len(_foundterms.keys())}] terms : ", data=_counts)
        return _foundterms
    
#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    # Capture current date and time when script begins
    _startTime = dt.now()

    _outputPath = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\IDXIX_sitALT_to_uatALT"

    # Create new instance of the IWS_ToolBox class
    toolbox = IWS_ToolBox(workingDirectoryPath=_outputPath)
    toolbox.logger.info(f"Process started at : {_startTime}")
    # Add a source paths to the the toolbox.
    toolbox.add_sourcePath("C:\\VS_Code_Repo\\IDXIX\\")
    # Sets trems to search for and use to exclude a file form processing if found in the file's full filepath
    toolbox.excludeDirNames = ["ObsoleteJobs"]
    toolbox.excludeFileNames = []
    toolbox.excludeFileFormats = []
    # Sets trems to search for and use to isolate and process only files found in this file's full filepath
    toolbox.includeDirNames = ["Jobs"]
    toolbox.includeFileNames = []
    toolbox.includeFileFormats = []

    # Initials the Toolbox's file colelction process, gathering refrences to all files in each provided source path.
    colelctedFileList = toolbox.collectSourceFiles()

    # Load and Filter Colelcted Source Files
    toolbox.excludeTerms = []
    toolbox.searchReplaceTerms = {}
    toolbox.searchTerms = []

    toolbox.loadCollectedFiles(colelctedFileList) 
    
    toolbox.files_by_terms()

    # Capture current date and time when script ends
    _stopTime = dt.now()
    toolbox.logger.info(f"Process completed at :  at {_stopTime} elapsed time {format(_stopTime-_startTime)}")
    