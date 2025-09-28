#-------------------------------------------------
#   Imports
#-------------------------------------------------

import logging, os, json, sys, shutil, copy, uuid

import threading

from enum import Enum, StrEnum
from datetime import datetime as dt
from typing import Any

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


class IWS_OBJ_TYPE(StrEnum):
    UNDEFINED = 'undefined'
    WORKSTATION = 'workstation'
    FOLDER = 'folder'
    JOBSTREAM = 'jobstream'
    JOB = 'job'
    RUNCYCLE = 'runcycle'
    FOLLOWS = 'follows'

class IWS_LINK_TYPE (StrEnum):
    UNDEFINED = 'undefined'
    STREAM_TO_JOB = 'stream_to_job'
    FOLLOWS = 'follows'
    NEEDS = 'needs'

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
        _log_folder = self._log_folder
        _log_file = self._log_fileName if self._log_fileName is not None else log_file if log_file is not None else f"{self._log_name}_{str(dt.now().date()).replace('-','')}.log"  
        _level = self._log_level if self._log_level is not None else level
        if log_folder is None and _log_folder is None and getattr(sys, 'frozen', False):
            _log_folder = os.path.dirname(sys.executable)
        elif log_folder is None  and _log_folder is None and __file__:
            _log_folder = os.path.dirname(os.path.abspath(__file__))
        elif log_folder is not None and os.path.exists(log_folder) and os.path.isfile(log_folder):
            _log_folder = os.path.basename(log_folder)
        elif log_folder is not None and os.path.exists(log_folder) and os.path.isdir(log_folder):
            _log_folder = log_folder
        elif log_folder is not None and not os.path.exists(log_folder) and os.path.isdir(log_folder):
            os.makedirs(log_folder, exist_ok=True)
            _log_folder = log_folder
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

#-------------------------------------------------
#   Data container Classes
#-------------------------------------------------

class IWS_TEXT_obj :
    _logger:OutputLogger = OutputLogger().get_instance()
    _idKey:str|int
    _name:str
    _type:IWS_OBJ_TYPE
    _sourceFilePath:str
    _sourceRawText:dict[int,str]
    _connectionKeys:list[str]

    def __init__ (self, name:str, objType:str|IWS_OBJ_TYPE, lineData:dict[int,str], sourceFilePath:str, idKey:str|int=None) :
        self._idKey = uuid.uuid4() if idKey == None else idKey
        self._name = name
        self._type = IWS_OBJ_TYPE[objType] if objType in IWS_OBJ_TYPE.__members__ else IWS_OBJ_TYPE.UNDEFINED
        self._sourceFilePath = sourceFilePath

        for _k, _v in lineData:
            if _k not in self._sourceRawText.keys():
                self._sourceRawText[_k] = _v

    @property
    def idKey(self) -> str:
        """Retrieves object IdKey."""
        return self._idKey
    
    @property
    def name(self) -> str:
        """Retrieves object name."""
        return self._name.strip()
    
    @name.setter
    def name (self, new_value:str):
        if not isinstance(new_value, (str)):
            self._logger.error(f"Value of 'name' must be of type 'string' was provided as type : '{type(new_value)}'")
            raise TypeError(f"Value of 'name' must be of type 'string' was provided as type : '{type(new_value)}'")
        if new_value.strip() == '':
            self._logger.error(f"Value of 'name' was provided as a blank string, new_value : '{new_value}'")
        self._name = new_value.strip()

    @property
    def type(self) -> str:
        """Retrieves object type."""
        return self._type

    @classmethod
    def add_line (self, lineIndex:str, lineContent:str, overwrite:bool=False) -> bool :
        if (overwrite == True):
            self._sourceRawText[lineIndex] = lineContent
            return True
        else:
            if lineIndex not in self._sourceRawText.keys():
                self._sourceRawText[lineIndex] = lineContent
                return True
            else:
                self._logger.warning(f"Source line key [{lineIndex}] is already defined in IWS Object {self._name}")
        return False


class IWS_OBJ_LINK:
    _logger:OutputLogger = OutputLogger().get_instance()
    _idKey:str|int
    _type:IWS_LINK_TYPE
    _fromKey:str|int
    _toKey:str|int

    def __init__ (self, fromKey:str|int, toKey:str|int, type:str|IWS_LINK_TYPE,  sourceFilePath:str, idKey:str|int=None) :
        self._idKey = uuid.uuid4() if idKey == None else idKey
        self._type = IWS_LINK_TYPE[type] if type in IWS_LINK_TYPE.__members__ else IWS_LINK_TYPE.UNDEFINED
        self._sourceFilePath = sourceFilePath
        self._fromKey = fromKey
        self._toKey = toKey

    @property
    def idKey(self) -> str:
        """Retrieves object IdKey."""
        return self._idKey
    
    @property
    def type(self) -> IWS_LINK_TYPE:
        """Retrieves IWS Connection Type."""
        return self._type
    
    @type.setter
    def type (self, new_value:str|IWS_LINK_TYPE):
        if not isinstance(new_value, (str, IWS_LINK_TYPE)):
            self._logger.error(f"Value of 'type' must be of type 'string' or predefined in was provided as one f the following [{', '.join(_mem.name for _mem in IWS_LINK_TYPE)}] : '{type(new_value)}'")
            raise TypeError(f"Value of 'type' must be of type 'string' or predefined in was provided as one f the following [{', '.join(_mem.name for _mem in IWS_LINK_TYPE)}] : '{type(new_value)}'")
        if new_value.strip() == '':
            self._logger.error(f"Value of 'type' was provided as a blank string")
        self.type = IWS_LINK_TYPE[new_value] if new_value in IWS_LINK_TYPE.__members__ else IWS_LINK_TYPE.UNDEFINED


class ToolBox_Step:
    _logger:OutputLogger = OutputLogger().get_instance()
    _name:str

    _sourcePaths:list[str] = []
    _sourceFileFormats:list[str] = [fmt.value for fmt in ValidIWSFileFormat]
    _configFileFormats:list[str] = [fmt.value for fmt in ValidConfigFileFormat]

    # folder path and file terms to isolate or exclude from processing
    _excludeDirNames:list[str] = []
    _excludeFileNames:list[str] = []
    _excludeFileFormats:list[str] = []
    _found_files:list[dict[str,str]] = []
        
    def __init__ (self, name:str) :
        self._name = name
        self._sourcePaths = []
        self._sourceFileFormats = [fmt.value for fmt in ValidIWSFileFormat]
        self._configFileFormats = [fmt.value for fmt in ValidConfigFileFormat]
        self._excludeDirNames = []
        self._excludeFileNames = []
        self._excludeFileFormats = []
        self._found_files = []

    @property
    def name(self) -> str:
        """Retrieves step name."""
        return self._name.strip()
    
    @property
    def fileCount(self) -> int:
        """Retrieves step name."""
        return len(self._found_files)
    
    @property
    def fileList_FullPath(self) -> list[str]:
        """Retrieves returns list of found file paths."""
        return ([os.path.join(_f['rootPath'], _f['relPath'], _f['fileName']) for _f in self._found_files])
    
    @property
    def fileList_RelPath(self) -> list[str]:
        """Retrieves returns list of found file paths."""
        return (set([os.path.join(_f['relPath'], _f['fileName']) for _f in self._found_files]))
    
    @property
    def fileList_fileName(self) -> list[str]:
        """Retrieves returns list of found file paths."""
        return (set([_f['fileName'] for _f in self._found_files]))
    
    @classmethod
    def add_sourcePath (self, sourcePath:str):
        """Adds Directory or Folder path to source path list, used when collecting and filtering files."""
        if os.path.exists(sourcePath) and os.path.isdir(sourcePath):
            if sourcePath not in self._sourcePaths:
                self._logger.debug(f"Added to sourcePath list : '{sourcePath}'")
                self._sourcePaths.append(sourcePath)
            else:
                self._logger.debug(f"Skipping source Path '{sourcePath}' - alredy loaded or not a valid folder path.")
        return self
    
    @classmethod
    def gather_files (self, excludedDirectories:list[str] = None, excludedFileNames:list[str]=None, excludeFileFormats:list[str]=None):
        """Gathers refferences to all files in each provided source path, filtering for file formats, directory paths, and file names"""
        if len(self._sourcePaths) == 0 :
            self._logger.warning("Unable to collect source files, no source paths have been loaded, use IWS_ToolBox.add_sourcePath() first to add a path")
        _known_file_formats = set([fmt.lower() for fmt in self._sourceFileFormats])# + [e for e in self.configFileFormats])
        self._logger.info(f"Valid File Formats", data=self._sourceFileFormats)
        self._logger.info(f"Valid Config File Formats", data=self._configFileFormats)
        self._excludeFileNames = excludedFileNames if excludedFileNames != None else []
        self._excludeDirNames = excludedDirectories if excludedDirectories != None else []
        self._excludeFileFormats = excludeFileFormats if excludeFileFormats != None else []
        if len(self._excludeDirNames) >= 1 : self._logger.info(f"Exclude Directory Paths containing Terms : ", data=self._excludeDirNames)
        if len(self._excludeFileNames) >= 1 : self._logger.info(f"Exclude Files Names containing Terms : ", data=self._excludeFileNames)
        if len(self._excludeFileFormats) >= 1 : self._logger.info(f"Exclude Foramts: : ", data=self._excludeFileFormats)
        _totalCounter = 0
        _collectedCounter = 0
        _relPaths = {}
        for _path in self._sourcePaths:
            if not(os.path.exists(_path)):
                self._logger.warning(f"Unable to find path in sourcePaths List. target Path: '{_path}'")
                continue
            for dir_path, dirs, files in os.walk(_path):
                for file in files:
                    _totalCounter +=1
                    _should_add:bool = True
                    _excludeText = []
                    _filePath = os.path.join(dir_path,file)
                    
                    #Checks if directory path contains excluded directory term
                    if len(self._excludeDirNames) >= 1:
                        for _excludeDir in self._excludeDirNames:
                            if (_excludeDir.lower() in dir_path.lower()) or (_excludeDir.lower() == dir_path.lower()):
                                _excludeText.append(f"File path contains excluded directory term : '{_excludeDir}'")
                                _should_add = False

                    #Checks if file name contains an excluded file name term.
                    if len(self._excludeFileNames) >= 1:
                        for _excludeFileName in self._excludeFileNames:
                            if (_excludeFileName.lower() in file.lower()):
                                _excludeText.append(f"File path contains excluded file name : '{_excludeFileName}'")
                                _should_add = False

                    #Checks if file foramt ends with and of the known formats.
                    if excludeFileFormats is not None and len(excludeFileFormats) >= 1:
                        if not any([file.lower().endswith(fmt) for fmt in _known_file_formats]):
                            _excludeText.append(f"File is not correct File Format : '*.{str(os.path.basename(file)).split('.')[-1]}'")
                            _should_add = False
                    
                    #Checks is file should be added to data set:
                    if (_should_add == False):
                        _reasons = ', '.join([f'"{_sc+1}":"{_str}"' for _sc, _str in enumerate(_excludeText)])
                        self._logger.debug(f"Excluding File from collection : '{_filePath}' | {_reasons}")
                    else:
                        self._logger.debug(f"Adding File to collection : '{_filePath}'")
                        _relPath = os.path.relpath(dir_path,_path)
                        if _relPath not in _relPaths.keys():
                            _relPaths[_relPath] = []
                        
                        _relPaths[_relPath].append(file)
                        self._found_files.append({
                            "rootPath":_path,
                            "relPath":_relPath,
                            "fileName":file
                        })
                        _collectedCounter += 1
        self._logger.info(f"Found [{_collectedCounter}] Files out of [{_totalCounter}] files.")
        self._logger.info(f"from [{len(_relPaths)}] directories:",data = _relPaths)
        return self
    
    @classmethod
    def copyFilesTo (self, outputDir:str) :
        _copyCounter = 0
        for _file in self._found_files:
            _source_path = os.path.join(_file['rootPath'], _file['relPath'], _file['fileName'])
            _output_path = os.path.join(outputDir, _file['relPath'])
            os.makedirs(_output_path, exist_ok=True)
            try:
                shutil.copy(_source_path, os.path.join(_output_path,_file['fileName']))
                self._logger.debug (f"Copied File : '{os.path.join(_file['relPath'],_file['fileName'])}' output : '{os.path.join(_output_path,_file['fileName'])}'")
                _copyCounter += 1
            except PermissionError:
                self._logger.error (f"Error: Permission denied when copying to '{_file}'.")
            except Exception as e:
                self._logger.info (f"An unexpected error occurred: {e}")
        self._logger.info(f"Found [{_copyCounter}] Files out of [{len(self._found_files)}] files.")
        return self
    

class ToolBox_loadedFileData:
    _logger:OutputLogger = OutputLogger().get_instance()
    _sourceFile:str = None
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
    _TASKTYPE_ids:list[int] = []
    _OUTPUTCOND_ids:list[int] = []
    _RECOVERY_ids:list[int] = []
    _NOP_ids:list[int] = []

    _iws_objects:dict[str,IWS_TEXT_obj] = {}
    _iws_obj_links:dict[str,IWS_OBJ_LINK]

    def __init__(self, sourceFilePath:str):
        if not(os.path.isfile(sourceFilePath)):
            self._logger.error(f"Target source path is not a valid file : '{sourceFilePath}'")
            return
        self._sourceFile = sourceFilePath
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
        self._TASKTYPE_ids = []
        self._OUTPUTCOND_ids = []
        self._RECOVERY_ids = []
        self._NOP_ids = []
        self._openFile()

    
    def _openFile (self):
        with open(self._sourceFile, "r") as f:
            self._rawLines = copy.deepcopy(f.readlines())
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

        
        for _i in range(len(self._job_start_ids)):
            _iws_js_obj = IWS_TEXT_obj(
                sourceFilePath = self._sourceFile,
                name= self._rawLines[self._stream_start_ids[_i]].split(' ')[-1].split('/')[-1],
                objType=IWS_OBJ_TYPE.JOBSTREAM,
                lineData=self._rawLines[self._stream_start_ids[_i]:self._stream_edge_ids[_i] + 1],
                idKey = uuid.uuid4()
            )
            _iws_js_obj.add_line(self._rawLines[self._stream_END_ids[_i]])
            for _j in range(len(self._job_start_ids)):
                job_start_id = self._job_start_ids[_j]
                job_end_id = self._job_start_ids[_j+1]-1 if _j < len(self._job_start_ids) else self._stream_edge_ids[_i]
                
                if (self._stream_edge_ids[_i] <= self._job_start_ids[_j] <= self._stream_END_ids[_i]):
                    _iws_job_obj = IWS_TEXT_obj(
                        sourceFilePath = self._sourceFile,
                        name= self._rawLines[job_start_id].split(' ')[-1].split('/')[-1],
                        objType=IWS_OBJ_TYPE.JOB,
                        lineData=self._rawLines[job_start_id:job_end_id],
                        idKey = uuid.uuid4()
                    )
                    _new_link = IWS_OBJ_LINK(
                        fromKey= _iws_js_obj.idKey,
                        toKey= _iws_job_obj.idKey,
                        type= IWS_LINK_TYPE.STREAM_TO_JOB,
                        idKey= uuid.uuid4()
                    )

                    if _iws_job_obj.idKey not in self._iws_objects.keys():
                        self._iws_objects[_iws_job_obj.idKey] = _iws_job_obj
                    if _new_link.idKey not in self._iws_obj_links.keys():
                        self._iws_obj_links[_new_link.idKey] = _new_link
                        
            if _iws_js_obj.idKey not in self._iws_objects.keys():
                self._iws_objects[_iws_js_obj.idKey] = _iws_js_obj
        return self
    
    
    @property
    def raw_text (self) -> str:
        """Returns the raw text from the source file un-edited."""
        return str('\n'.join(self._rawLines))
    

    def get_file_stats (self):
        self._logger.debug(f"Number of Job Streams : [{len(self._stream_start_ids)}]")
        self._logger.debug(f"Number of Jobs : [{len(self._job_start_ids)}]")
        return self    
 

    def get_JOBSTREAM_definition (self, filter:dict[str,any]=None) -> list[IWS_TEXT_obj] :
        _holder_list = []

        
        
        return _holder_list



#-------------------------------------------------
#   IWS_ToolBox Class
#-------------------------------------------------

class IWS_ToolBox:
    logger:OutputLogger = OutputLogger().get_instance()
    logFileName:str = None
    _targetWorkingDir:str = None
    
    sourcePaths:list[str] = []
    _steps:list[ToolBox_Step] = []
    _fileData:list[ToolBox_loadedFileData] = []

    def __init__ (self, workingDirectoryPath:str=None, logFileName:str|None=None):
        if (workingDirectoryPath != None and os.path.exists(workingDirectoryPath) and os.path.isdir(workingDirectoryPath)):
            self.targetWorkingDir = workingDirectoryPath  
        elif getattr(sys, 'frozen', False):
            self.targetWorkingDir = os.path.dirname(sys.executable)
        elif __file__:
            self.targetWorkingDir = os.path.dirname(os.path.abspath(__file__))
          
        self.logFileName = logFileName if (logFileName is not None) else f"log_{str(dt.now().date()).replace('-','')}.log"
        self._logger = OutputLogger.get_instance()
        self._logger.init_logger(log_folder=self.targetWorkingDir, log_file=self.logFileName, level=logging.DEBUG)


    def add_step (self, step_name:str) -> ToolBox_Step :
        _newStep = ToolBox_Step(step_name)
        self._steps.append(_newStep)
        self.logger.info(f"Added added step : '{_newStep.name}'")
        return _newStep


    def readFile (self, sourceFilePath:str) -> ToolBox_loadedFileData:
        _fileData = ToolBox_loadedFileData(sourceFilePath)
        
        if _fileData != None :
            self._fileData.append(_fileData)
            self.logger.info(f"Loaded Data from File: '{os.path.basename(sourceFilePath)}'")
            return _fileData
            