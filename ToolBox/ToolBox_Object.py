#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, re, copy, uuid, warnings
from collections import UserDict
from typing import Any
from ToolBox.ToolBox_logger import OutputLogger

#-------------------------------------------------
#   Decorator Functions / Wrappers
#-------------------------------------------------

def ToolBox_Decorator(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        return result
    return wrapper


class ToolBox_IWS_JobObj (UserDict):
    _id:str = None
    _logger:OutputLogger = OutputLogger().get_instance()
    _jobPath:str
    _jobName:str
    _jobAlias:str
    _source_job_def_text:str
    _modified_job_def_text:str
    
    def __init__(self, path:str, definition_text:str, alias_name:str=None, initial_data:dict[str,Any]=None):
        super().__init__(initial_data)
        _id = str(uuid.uuid5(uuid.NAMESPACE_DNS, path))
        self._id = str(_id)
        self._jobPath = path
        self._jobName = path.split('/')[-1]
        self._jobAlias = alias_name if alias_name != None and len(alias_name) >= 1 else None
        self._source_job_def_text = definition_text
        self._modified_job_def_text = definition_text

    def __str__(self) -> str:
        return self._modified_job_def_text
    
    @property
    def id (self) -> str:
        """Returns randomly generated ID value."""
        return self._id
    
    @property
    def name (self) -> str:
        """Returns assigned Job Name as stored in IWS."""
        return self._jobName
    
    @property
    def alias (self) -> str:
        """Returns assigned Alias for Job Name as stored in IWS."""
        return self._jobAlias

    @ToolBox_Decorator
    def reset_modfied_text (self):
        if self._modified_job_def_text != self._source_job_def_text:
            self._modified_job_def_text = self._source_job_def_text
        return self
    
    @ToolBox_Decorator
    def set_NOP (self, value:bool=True):
        _lines = self._modified_job_def_text.splitlines()
        _RECOVERY_id = next((_idx for _idx, _line in enumerate(_lines) if 'RECOVERY' in _line[0:10]), -1)
        _NOP_id = next((_idx for _idx, _line in enumerate(_lines) if 'NOP' in _line[0:6]), -1)
        
        if (_NOP_id != -1) and (value == True):
            self._logger.debug (f"Job : '{self._jobPath}' is already set to NOP")
        elif (_NOP_id != -1) and (value == False):
            self._logger.debug (f"Removing 'NOP' from Job : '{self._jobPath}'")
            _lines.pop(_NOP_id)
        elif (_NOP_id == -1) and (value == True):
            self._logger.debug (f"Adding 'NOP' to job : '{self._jobPath}'")
            _lines.insert(_RECOVERY_id+1, 'ON REQUEST')
        self._modified_job_def_text = "\n".join(_lines)
        
        return self
    


class ToolBox_IWS_JobStreamObj (UserDict):
    _id:str = None
    _logger:OutputLogger = OutputLogger().get_instance()
    _streamPath:str
    _streamName:str
    _source_stream_def_text:str
    _source_stream_end_text:str
    _modified_stream_def_text:str
    _modified_stream_end_text:str
    _job_collection:dict[str, ToolBox_IWS_JobObj] = {}
    
    def __init__(self, path:str, definition_text:str, end_text:str, initial_data:dict[str,Any]=None):
        super().__init__(initial_data)
        _id = str(uuid.uuid5(uuid.NAMESPACE_DNS, path))
        self._id = str(_id)
        self._streamPath = path
        self._streamName = path.split('/')[-1]
        self._source_stream_def_text = definition_text
        self._source_stream_end_text = end_text
        self._modified_stream_def_text = definition_text
        self._modified_stream_end_text = end_text
        self.reset_modfied_text()

    def __str__(self) -> str:
        _textHolder = self._modified_stream_def_text + '\n'
        _textHolder += "\n\n\n".join([str(_job.__str__()) for _job in self._job_collection.values()])
        _textHolder += ("\n\n") 
        _textHolder += self._modified_stream_end_text
        return _textHolder

    @property
    def id (self) -> str:
        """Returns randomly generated ID value."""
        return self._id
    
    @property
    def name (self) -> str:
        """Returns assigned Job Stream Name as stored in IWS."""
        return self._streamName
    
    @property
    def name_fullPath (self) -> str:
        """Returns full path of the Job Stream, formatted : {workstation}/{folderPath}/{jobStreamName}.@"""
        return f"{self._streamPath}.@"

    @property
    def job_list (self) -> list[ToolBox_IWS_JobObj]:
        """Returns a list of the full paths for each job in this Job Stream, {workstation}/{folderPath}/{jobStreamName}.{jobName} AS {aliasName}"""
        return [f"{self.name_fullPath.upper()[0:-2]}.{_job.name.upper()}" for _job in self._job_collection.values()]

    
    @ToolBox_Decorator
    def add_Job_definition (self, name:str, definition_text:str, alias_name:str=None, initial_data:dict[str,Any]=None):
        if name not in self._job_collection.keys():
            self._job_collection[name] = ToolBox_IWS_JobObj(name, definition_text, alias_name=alias_name, initial_data=initial_data)
        return self
    
    def get_job_by_name (self, name:str) -> ToolBox_IWS_JobObj | None:
        """Returns the 1st Job Data block for the given job name, will return None if one can't be found."""
        for _jobPath, _jobdata in self._job_collection.items():
            if (name.upper() in _jobPath.upper()):
                return _jobdata
        return None

    @ToolBox_Decorator
    def reset_modfied_text (self):
        if (self._modified_stream_def_text is None) or (self._modified_stream_def_text != self._source_stream_def_text):
            self._modified_stream_def_text = self._source_stream_def_text
        if (self._modified_stream_end_text is None) or (self._modified_stream_end_text != self._source_stream_end_text):
            self._modified_stream_end_text = self._source_stream_end_text
        return self
    
    @ToolBox_Decorator
    def set_ONREQUEST (self, value:bool = True):
        _lines = self._modified_stream_def_text.splitlines()
        _DESCRIPTION_id = next((_idx for _idx, _line in enumerate(_lines) if 'DESCRIPTION' in _line[0:14]), -1)
        _REQUEST_id = next((_idx for _idx, _line in enumerate(_lines) if 'REQUEST' in _line[0:20]), -1)
        if (_REQUEST_id != -1) and (value == True):
            self._logger.debug (f"Stream : '{self._streamPath}' is already ON REQUEST")
        elif (_REQUEST_id != -1) and (value == False):
            self._logger.debug (f"Removing 'ON REQUEST' from Stream : '{self._streamPath}'")
            _lines.pop(_REQUEST_id)
        elif (_REQUEST_id == -1) and (value == True):
            self._logger.debug (f"Adding 'ON REQUEST' to Stream : '{self._streamPath}'")
            _lines.insert(_DESCRIPTION_id, 'ON REQUEST')
        self._modified_stream_def_text = "\n".join(_lines)
        return self
    
    @ToolBox_Decorator
    def set_DRAFT (self, value:bool = True):
        _lines = self._modified_stream_def_text.splitlines()
        _DESCRIPTION_id = next((_idx for _idx, _line in enumerate(_lines) if 'DESCRIPTION' in _line[0:14]), -1)
        _REQUEST_id = next((_idx for _idx, _line in enumerate(_lines) if 'REQUEST' in _line[0:20]), -1)
        _DRAFT_id = next((_idx for _idx, _line in enumerate(_lines) if 'DRAFT' in _line), -1)

        if (_DRAFT_id != -1) and (value == True):
            self._logger.debug (f"Stream : '{self._streamPath}' is already set to DRAFT")
        elif (_DRAFT_id != -1) and (value == False):
            self._logger.debug (f"Removing 'DRAFT' from Stream : '{self._streamPath}'")
            _lines.pop(_DRAFT_id)
        elif (_DRAFT_id == -1) and (value == True):
            self._logger.debug (f"Adding 'DRAFT' to Stream : '{self._streamPath}'")
            _index = max([_DESCRIPTION_id, _REQUEST_id])
            _lines.insert(_index, 'DRAFT')
        self._modified_stream_def_text = "\n".join(_lines)
        return self
    
    def remove_RUNCYCLE_lines (self):

        return self

class ToolBox_IWS_JIL_File (UserDict):
    _id:str = None
    _logger:OutputLogger = OutputLogger().get_instance()
    _sourceFile:str = None
    _rootPath:str = None
    _relPath:str = None
    _fileName:str = None

    _sourceFileLines:list[str] = []
    _jobStream_collection:dict[str, ToolBox_IWS_JobStreamObj] = {}

    def __init__(self, sourceFilePath:str, rootPath:str=None, initial_data:dict[str,Any]=None):
        super().__init__(initial_data)
        self._sourceFile = sourceFilePath
        self._fileName = os.path.basename(sourceFilePath)
        _id = str(uuid.uuid5(uuid.NAMESPACE_DNS, sourceFilePath))
        self._id = str(_id)
        if rootPath != None : 
            self._rootPath = rootPath
            self._relPath = os.path.relpath(os.path.dirname(self._sourceFile),self._rootPath)
        #self.openFile() # disabled line in __init__ for faster gathering and filtering of files by path and file name, no need to open the file till required to.

    @property
    def id (self) -> str:
        """Returns randomly generated ID value."""
        return self._id
    
    @property
    def log (self) -> OutputLogger:
        """Returns assigned log for debugging and logging of actions"""
        return self._logger
    
    @property
    def sourceFilePath(self) -> str:
        """Returns whole source file path"""
        return self._sourceFile
    
    @property
    def sourceFileName(self) -> str:
        """Returns file name with format"""
        return os.path.basename(self._sourceFile)
    
    @property
    def sourceFileBaseName(self) -> str:
        """Returns file name without the file format at the end"""
        return '.'.join(os.path.basename(self._sourceFile).split('.')[0:-1])
    
    @property
    def sourceFileFormat(self) -> str:
        """Returns file format"""
        return os.path.basename(self._sourceFile).split('.')[-1]
    
    @property
    def sourceFileDir(self) -> str:
        """Returns directory path where file is stored"""
        return os.path.dirname(self._sourceFile)
    
    @property
    def sourceFileDirRoot(self) -> str:
        """Returns assigned root path for file"""
        return os.path.dirname(self._rootPath)
    
    @property
    def sourceFileDirRelPath(self) -> str:
        """Returns the relative path of the file (sourceFileDir minus the sourceFileDirRoot)"""
        return os.path.relpath(os.path.dirname(self._sourceFile), self._rootPath)
    
    @property
    def rootPath(self) -> str:
        """Returns rootPath"""
        return self._rootPath
    
    @rootPath.setter
    def rootPath (self, value:str) :
        self._rootPath = value
        self._relPath = os.path.relpath(os.path.dirname(self._sourceFile),self._rootPath)

    @property
    def jobStreamPaths (self) -> list[str]:
        """Returns a list of Job Streams found in file, formatted: {workstation}/{folderPath}/{jobStreamName}.@]"""
        return [_js.name_fullPath for _js in self._jobStream_collection.values()]
    
    @property
    def jobPaths (self) -> list[str]:
        """Returns a list of Jobs found in file, formatted: {workstation}/{folderPath}/{jobStreamName}.{jobName}]"""
        
        return [_js.name_fullPath for _js in self._jobStream_collection.values()]

    @ToolBox_Decorator
    def openFile (self):
        if (len(self._sourceFileLines) == 0):
            _holder = None
            with open(self._sourceFile, "r") as f:
                _holder = copy.deepcopy(f.read()).split('\n')
            if (_holder != None):
                #clean lines and remove returns and next line charecters
                self._sourceFileLines = [s.replace('\n', '').replace('\r', '') for s in _holder]
            self._logger.debug (f"Opening source file : '{os.path.join(self.sourceFileDirRelPath, self.sourceFileName)}'")
            self._reload_streams_and_jobs()
        return self
    
    @ToolBox_Decorator
    def closeFile(self):
        self._sourceFileLines = []
        self._jobStream_collection.clear()


    @ToolBox_Decorator
    def _clear_ (self):
        self._jobStream_collection.clear()
        return self

    @ToolBox_Decorator
    def _reload_streams_and_jobs (self):
        _stream_start_ids:list[int] = []
        _stream_edge_ids:list[int] = []
        _job_start_ids:list[int] = []
        _stream_end_ids:list[int] = []
        for _line_id, _line in enumerate(self._sourceFileLines):
            if "SCHEDULE" in str(_line).strip()[0:9]:
                _stream_start_ids.append(_line_id)
            if ':' in _line[0:2]:
                _stream_edge_ids.append(_line_id)
            if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) :#or (any(_s in str(_line).strip()[0:5] for _s in ['PRD#', 'NPR#'])) and ('#' in str(_line[2:]).strip()):
                _job_start_ids.append(_line_id)
            if "END" in str(_line).strip()[0:4] and 'ENDJOIN' not in str(_line).strip():
                _stream_end_ids.append(_line_id)
        self._clear_()
        for _id_index in range(len(_stream_start_ids)):
            _stream_start = _stream_start_ids[_id_index]
            _stream_path = str(self._sourceFileLines[_stream_start].split(' ')[1])
            if _stream_path not in self._jobStream_collection.keys():
                _stream_edge = _stream_edge_ids[_id_index]
                _stream_end = _stream_end_ids[_id_index]
                _stream_definition_text = "\n".join([_line for _line in self._sourceFileLines[_stream_start:_stream_edge+1] if _line.strip() != ''])
                _stream_end_text = self._sourceFileLines[_stream_end].strip()
                self._jobStream_collection[_stream_path] = ToolBox_IWS_JobStreamObj(_stream_path, _stream_definition_text, _stream_end_text)
            _job_ids = [_id for _id in _job_start_ids if _stream_start < _id < _stream_end]
            for _job_id_index in range(len(_job_ids)):
                _job_line_start = _job_ids[_job_id_index]
                _job_line_stop = int(_job_ids[_job_id_index+1])-1 if _job_id_index < (len(_job_ids)-1) else int(_stream_end -1)
                _job_definition_text = "\n".join([_line for _line in self._sourceFileLines[_job_line_start:_job_line_stop] if _line.strip() != ''])
                _job_name = self._sourceFileLines[_job_line_start].strip().split('/')[-1].split('/')[-1]
                _alias_pattern = r"(\w+)\s+" + re.escape(" AS ") + r"\s+(\w+)"
                _alias_matches = re.findall(_alias_pattern, self._sourceFileLines[_job_line_start], flags=re.IGNORECASE)
                _job_path = f"{_stream_path}.{_job_name}"
                if len(_alias_matches) >= 1:
                    print (_job_path, "alias matchs : ", _alias_matches)
                else:
                    _alias_matches = None
                self._jobStream_collection[_stream_path].add_Job_definition(_job_path, _alias_matches, _job_definition_text)        
        return self
    
    @ToolBox_Decorator
    def saveTo(self, outputfolder:str, rename:str=None, useRelPath:bool=False) -> str:
        warnings.warn(
            "'saveTo' is deprecated and will be removed in a future versions. Use 'saveFileTo' instead.",
            DeprecationWarning,
            stacklevel=2 # This ensures the warning points to the caller's code
        )
        return self.saveFileTo(outputfolder, rename, useRelPath)
    
    @ToolBox_Decorator
    def saveFileTo (self, outputfolder:str, rename:str=None, useRelPath:bool=False) -> str:
        _outputPath = os.path.join(outputfolder,self._relPath) if useRelPath == True else outputfolder
        os.makedirs(_outputPath, exist_ok=True)
        _filename = rename if rename != None else self._fileName
        _outputFilePath = os.path.join (_outputPath, _filename)
        if os.path.exists (_outputFilePath):
            os.remove(_outputFilePath)
        try:
            _filetext = "\n".join([str(_stream.__str__()) for _stream in self._jobStream_collection.values()])
            with open(_outputFilePath, "w") as output_file:
                output_file.write(_filetext)
            self._logger.debug (f"Saved source file : '{os.path.join(self.sourceFileDirRelPath, self.sourceFileName)}' as file : '{_outputFilePath}'")
        except SystemError as se :
            raise (se)
        return _outputFilePath

    @ToolBox_Decorator
    def set_Streams_ONREQUEST (self, value:bool = True, filter_worksataiton:list[str]=None, filter_folder:list[str]=None, filer_streamName:list[str]=None):
        _stream_keys = [_path for _path in self._jobStream_collection.keys()]
        if filter_worksataiton is not None: 
            _stream_keys = [_path for _ws in filter_worksataiton for _path in _stream_keys if _ws.upper() in _path.upper()]
        if filter_folder is not None: 
            _stream_keys = [_path for _f in filter_folder for _path in _stream_keys if _f.upper() in _path.upper()]
        if filer_streamName is not None: 
            _stream_keys = [_path for _jsn in filer_streamName for _path in _stream_keys if _jsn.upper() in _path.upper()]
        for _key in _stream_keys:
            _stream = self._jobStream_collection[_key]
            _stream.set_ONREQUEST(value)

    @ToolBox_Decorator
    def set_Streams_DRAFT (self, value:bool = True, filter_worksataiton:list[str]=None, filter_folder:list[str]=None, filer_streamName:list[str]=None):
        _stream_keys = [_path for _path in self._jobStream_collection.keys()]
        if filter_worksataiton is not None: 
            _stream_keys = [_path for _ws in filter_worksataiton for _path in _stream_keys if _ws.upper() in _path.upper()]
        if filter_folder is not None: 
            _stream_keys = [_path for _f in filter_folder for _path in _stream_keys if _f.upper() in _path.upper()]
        if filer_streamName is not None: 
            _stream_keys = [_path for _jsn in filer_streamName for _path in _stream_keys if _jsn.upper() in _path.upper()]
        for _key in _stream_keys:
            _stream = self._jobStream_collection[_key]
            _stream.set_DRAFT(value)

    @ToolBox_Decorator
    def set_Jobs_NOP (self, value:bool = True, filter_worksataiton:list[str]=None, filter_folder:list[str]=None, filer_streamName:list[str]=None, filer_jobName:list[str]=None):
        _stream_keys = [_path for _path in self._jobStream_collection.keys()]
        if filer_streamName is not None:        
            _stream_keys = [_path for _jsn in filer_streamName for _path in _stream_keys if _jsn.upper() in _path.upper()]
        for _key in _stream_keys:
            _stream = self._jobStream_collection[_key]
            for _job in _stream.job_list:
                _skip = False
                if (filter_worksataiton is not None) and all( _ws.upper() not in _job._jobPath.upper() for _ws in filter_worksataiton): 
                    _skip = True
                if (filter_folder is not None) and all( _f.upper() not in _job._jobPath.upper() for _f in filter_folder): 
                    _skip = True
                if (filer_jobName is not None) and all( _jn.upper() not in _job._jobPath.upper() for _jn in filer_jobName): 
                    _skip = True
                if _skip == True : continue
                _jobData = _stream.get_job_by_name(_job.split('/')[-1])
                _jobData.set_NOP(value)