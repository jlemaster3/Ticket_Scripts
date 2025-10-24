#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, re, copy, uuid, warnings, difflib
from collections import UserDict
from typing import Any, Match, Optional
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
    _sourceFile:str = None
    _parentPath:str = None
    _jobPath:str = None
    _jobWorkstation:str = None
    _jobFolder:str = None
    _jobName:str = None
    _jobAlias:str = None
    _source_job_def_text:str = None
    _modified_job_def_text:str = None
    
    def __init__(self, path:str, definition_text:str, parent_path:str=None, alias_name:str=None, initial_data:dict[str,Any]=None, sourceFile:str=None):
        super().__init__(initial_data)
        _id = str(uuid.uuid5(uuid.NAMESPACE_DNS, path))
        self._id = str(_id)
        self._jobPath = path
        _j_parts = path.split('/')
        self._jobWorkstation = _j_parts.pop(0)
        self._jobName = _j_parts.pop(-1)
        self._jobFolder = '/'.join(_j_parts)
        self._jobAlias = alias_name
        self._parentPath = parent_path        
        self._source_job_def_text = definition_text
        self._modified_job_def_text = definition_text
        self._sourceFile = sourceFile

    @ToolBox_Decorator
    def _reset_values_from_modified_text (self):
        _job_start_ids:list[int] = []
        _lines = self._modified_job_def_text.splitlines()
        for _line_id, _line in enumerate(_lines):
            if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) :#or (any(_s in str(_line).strip()[0:5] for _s in ['PRD#', 'NPR#'])) and ('#' in str(_line[2:]).strip()):
                _job_start_ids.append(_line_id)
        for _i in range(len(_job_start_ids)):
            _line = _lines[_job_start_ids[_i]]
            self._jobPath = _line.strip().split(' ')[0]
            _j_parts = self._jobPath.split('/')
            self._jobWorkstation = _j_parts.pop(0)
            self._jobName = _j_parts.pop(-1)
            self._jobFolder = f"/{'/'.join(_j_parts)}/"
            _alias_index = _line.find(" AS ")
            self._jobAlias = _line[_alias_index+3:].strip().split(' ')[0] if _alias_index != -1 else None
        return self

    def __str__(self) -> str:
        return self._modified_job_def_text
    
    @property
    def id (self) -> str:
        """Returns randomly generated ID value."""
        return self._id
    
    @property
    def sourceFile (self) -> str:
        return self._sourceFile
    
    @property
    def name (self) -> str:
        """Returns assigned Job Name as stored in IWS."""
        return self._jobName
    
    @property
    def name_fullPath (self) -> str:
        """Returns path of the Job Stream, {jobName} will be the alias if used, formatted : {workstation}/{folderPath}/{jobStreamName}.{jobName} or {workstation}/{folderPath}/{jobName}"""
        _ouput = None
        if (self._parentPath is None):
            _ouput = self._jobPath
        else:
            _js_parts = list(self._parentPath.split('/'))
            _js_ws = _js_parts.pop(0)
            _js_name = _js_parts.pop(-1).replace('.@','').strip()
            _js_folder = '/'.join(_js_parts)
            _j_name = self._jobName if (self._jobAlias is None) or (self._jobAlias.strip() == '') else self._jobAlias
            if (_js_ws.upper() in self._jobWorkstation.upper()) and (_js_folder.upper() in self._jobFolder.upper()):
                _ouput = f"{_js_ws}/{_js_folder}/{_js_name}.{_j_name}"
            else:
                _ouput = f"{self._jobWorkstation}{self._jobFolder}{_j_name}"
            
        return _ouput
    
    @property
    def alias (self) -> str:
        """Returns assigned Alias for Job Name as stored in IWS."""
        return self._jobAlias
    
    @property
    def path (self) -> str:
        """Returns assigned Path for Job Name as stored in IWS. formatted : {workstation}/{folderPath}/{jobName}"""
        return self._jobPath

    @ToolBox_Decorator
    def change_parent_path (self, path:str):
        if (path is not None or path.strip() != '') and (self._parentPath.upper() != path.upper()):
            self._parentPath = path
        return self
    
    @ToolBox_Decorator
    def reset_modfied_text (self):
        if self._modified_job_def_text != self._source_job_def_text:
            self._modified_job_def_text = self._source_job_def_text
        return self
    
    @ToolBox_Decorator
    def search_replace_text (self, searchString:str, replaceString:str, updated_source:bool=False) :
        self._modified_job_def_text = re.sub(searchString, replaceString, self._modified_job_def_text, flags=re.IGNORECASE)
        if updated_source == True:
            self._source_job_def_text = re.sub(searchString, replaceString, self._source_job_def_text, flags=re.IGNORECASE)
        self._reset_values_from_modified_text()
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
    _sourceFile:str = None
    _streamPath:str = None
    _streamWorkstation:str = None
    _streamFolder:str = None
    _streamName:str = None
    _source_stream_def_text:str = None
    _source_stream_end_text:str = None
    _modified_stream_def_text:str = None
    _modified_stream_end_text:str = None
    _job_collection:dict[str, ToolBox_IWS_JobObj] = None
    
    def __init__(self, path:str, definition_text:str, end_text:str, initial_data:dict[str,Any]=None, sourceFile:str=None):
        super().__init__(initial_data)
        _id = str(uuid.uuid5(uuid.NAMESPACE_DNS, path))
        self._id = str(_id)
        self._streamPath = path
        _js_parts = path.split('/')
        self._streamWorkstation = _js_parts.pop(0)
        self._streamName = _js_parts.pop(-1)
        self._streamFolder = '/'.join(_js_parts)
        self._source_stream_def_text = definition_text
        self._source_stream_end_text = end_text
        self._modified_stream_def_text = definition_text
        self._modified_stream_end_text = end_text
        self._sourceFile = sourceFile
        self._job_collection = {}
        self.reset_modfied_text()

    @ToolBox_Decorator
    def _reset_values_from_modified_text (self):
        _lines = str(self._modified_stream_def_text).splitlines()
        _stream_start_ids:list[int] = []
        _stream_edge_ids:list[int] = []
        _stream_end_ids:list[int] = []
        for _line_id, _line in enumerate(_lines):
            if "SCHEDULE" in str(_line).strip()[0:9]:
                _stream_start_ids.append(_line_id)
            if ':' in _line[0:2]:
                _stream_edge_ids.append(_line_id)
            if "END" in str(_line).strip()[0:4] and 'ENDJOIN' not in str(_line).strip():
                _stream_end_ids.append(_line_id)
        for _id_index in range(len(_stream_start_ids)):
            _line = _lines[_stream_start_ids[_id_index]]
            self._streamPath = str(_line.split(' ')[1])
            _js_parts = self._streamPath.split('/')
            self._streamWorkstation = _js_parts.pop(0)
            self._streamName = _js_parts.pop(-1)
            self._streamFolder = f"/{'/'.join(_js_parts)}/"
            
        return self
    
    def __str__(self) -> str:
        _textHolder = self._modified_stream_def_text + '\n'
        _textHolder += "\n\n\n".join([str(_job.__str__()) for _job in self._job_collection.values()])
        _textHolder += ("\n\n") 
        _textHolder += self._modified_stream_end_text
        _textHolder += ("\n\n")
        return _textHolder

    @property
    def id (self) -> str:
        """Returns randomly generated ID value."""
        return self._id
    
    @property
    def sourceFile (self) -> str:
        return self._sourceFile

    @property
    def name (self) -> str:
        """Returns assigned Job Stream Name as stored in IWS."""
        return self._streamName
    
    @property
    def name_path (self) -> str:
        """Returns path of the Job Stream, formatted : {workstation}/{folderPath}/{jobStreamName}"""
        return self._streamPath
    
    @property
    def name_fullPath (self) -> str:
        """Returns full path of the Job Stream, formatted : {workstation}/{folderPath}/{jobStreamName}.@"""
        return f"{self._streamPath}.@"

    @ToolBox_Decorator
    def job_list (self) -> list[str]:
        """Returns a list of the full paths for each job in this Job Stream, {workstation}/{folderPath}/{jobStreamName}.{jobName} AS {aliasName}"""
        _list = []
        for _job in self._job_collection.values():
            if _job.name_fullPath not in _list:
                _list.append(_job.name_fullPath)
        return _list
    
    @ToolBox_Decorator
    def jobObjects (self) -> dict[str,ToolBox_IWS_JobObj]:
        _data:dict[str,ToolBox_IWS_JobObj] = {}
        for _job in self._job_collection.values():
            if _job.name_fullPath not in _data.keys():
                _data[_job.name_fullPath] = _job
        return _data

    
    @ToolBox_Decorator
    def add_Job_definition (self, path:str, definition_text:str, parent_path:str=None, alias_name:str=None, initial_data:dict[str,Any]=None, sourceFile:str=None):
        _parent_path = parent_path if parent_path is not None else self.name_fullPath
        _source_file = sourceFile if sourceFile is not None else self._sourceFile

        # create new job if missing
        _new_obj = ToolBox_IWS_JobObj(
            path = path,
            definition_text = definition_text,
            parent_path = _parent_path,
            alias_name = alias_name,
            initial_data = initial_data,
            sourceFile = _source_file
        )
        self._job_collection[_new_obj.name_fullPath] = _new_obj
        return self
    
    @ToolBox_Decorator
    def insert_jobObject (self, index:int, jobObj:ToolBox_IWS_JobObj):
        _items = list(self._job_collection.items())
        _items.insert(index, (jobObj.path, jobObj))
        self._job_collection = dict(_items)
        return self
    
    @ToolBox_Decorator
    def get_job_by_name (self, name:str) -> ToolBox_IWS_JobObj | None:
        """Returns the 1st Job Data block for the given job name, will return None if one can't be found."""
        for _jobPath, _jobdata in self._job_collection.items():
            if (name.upper() in _jobPath.upper()):
                return _jobdata
        return None
    
    @ToolBox_Decorator
    def get_job_index_by_name (self, name:str) -> int :
        """Returns the 1st index of the Job for the name, will return -1 if match can't be found."""
        return list(self._job_collection.keys()).index(name)
    
    @ToolBox_Decorator
    def get_job_name_by_index (self, index:int) -> str:
        """Returns the 1st index of the Job for the name, will return None if match can't be found."""
        for _i, key in enumerate(self._job_collection.keys()):
            if _i == index:
                return key
        return None

    @ToolBox_Decorator
    def reset_modfied_text (self):
        if (self._modified_stream_def_text is None) or (self._modified_stream_def_text != self._source_stream_def_text):
            self._modified_stream_def_text = self._source_stream_def_text
        if (self._modified_stream_end_text is None) or (self._modified_stream_end_text != self._source_stream_end_text):
            self._modified_stream_end_text = self._source_stream_end_text
        return self
    
    @ToolBox_Decorator
    def search_replace_text (self, searchString:str, replaceString:str) :
        self._modified_stream_def_text = re.sub(searchString, replaceString, self._modified_stream_def_text, flags=re.IGNORECASE)
        for _job in self._job_collection.values():
            _job.search_replace_text(searchString, replaceString)
        self._reset_values_from_modified_text()
        return self
    
    @ToolBox_Decorator
    def set_ONREQUEST (self, value:bool = True):
        _lines = self._modified_stream_def_text.splitlines()
        _DESCRIPTION_id = next((_idx for _idx, _line in enumerate(_lines) if 'DESCRIPTION' in _line[0:14]), -1)
        _REQUEST_id = next((_idx for _idx, _line in enumerate(_lines) if 'REQUEST' in _line[0:20]), -1)
        if (_REQUEST_id != -1) and (value == True):
            self._logger.debug (f"Stream : '{self._streamPath}' is already 'ON REQUEST'.")
        elif (_REQUEST_id != -1) and (value == False):
            self._logger.debug (f"Removing 'ON REQUEST' from Stream : '{self._streamPath}'.")
            _lines.pop(_REQUEST_id)
        elif (_REQUEST_id == -1) and (value == False):
            self._logger.debug (f"Stream : '{self._streamPath}' is already not using 'ON REQUEST'.")
        elif (_REQUEST_id == -1) and (value == True):
            self._logger.debug (f"Adding 'ON REQUEST' to Stream : '{self._streamPath}'.")
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
            self._logger.debug (f"Stream : '{self._streamPath}' is already set to DRAFT.")
        elif (_DRAFT_id != -1) and (value == False):
            self._logger.debug (f"Removing 'DRAFT' from Stream : '{self._streamPath}'.")
            _lines.pop(_DRAFT_id)
        elif (_DRAFT_id == -1) and (value == False):
            self._logger.debug (f"Stream : '{self._streamPath}' is already not using DRAFT.")
        elif (_DRAFT_id == -1) and (value == True):
            self._logger.debug (f"Adding 'DRAFT' to Stream : '{self._streamPath}'.")
            _index = max([_DESCRIPTION_id, _REQUEST_id])
            _lines.insert(_index, 'DRAFT')
        
        self._modified_stream_def_text = "\n".join(_lines)
        return self
    
    def remove_RUNCYCLE_lines (self):

        return self
    
    @ToolBox_Decorator
    def set_Jobs_NOP (self, value:bool = True, filter_worksataiton:list[str]=None, filter_folder:list[str]=None, filer_streamName:list[str]=None, filer_jobName:list[str]=None):
        for _job in self._job_collection.values():
            _skip = False
            if (filter_worksataiton is not None) and all( _ws.upper() not in _job.name_fullPath.upper() for _ws in filter_worksataiton): 
                _skip = True
            if (filter_folder is not None) and all( _f.upper() not in _job.name_fullPath.upper() for _f in filter_folder): 
                _skip = True
            if (filer_jobName is not None) and all( _jn.upper() not in _job.name.upper() for _jn in filer_jobName): 
                _skip = True
            if _skip == True : continue
            _job.set_NOP(value=value)
        return self

class ToolBox_IWS_JIL_File (UserDict):
    _id:str = None
    _logger:OutputLogger = OutputLogger().get_instance()
    _sourceFile:str = None
    _rootPath:str = None
    _relPath:str = None
    _fileName:str = None

    _sourceFileLines:list[str] = None
    _jobStream_collection:dict[str, ToolBox_IWS_JobStreamObj] = None

    def __init__(self, sourceFilePath:str, rootPath:str=None, initial_data:dict[str,Any]=None):
        super().__init__(initial_data)
        self._sourceFile = sourceFilePath
        self._fileName = os.path.basename(sourceFilePath)
        self._sourceFileLines = []
        self._jobStream_collection = {}
        _id = str(uuid.uuid5(uuid.NAMESPACE_DNS, sourceFilePath))
        self._id = str(_id)
        if rootPath != None : 
            self._rootPath = rootPath
            self._relPath = os.path.relpath(os.path.dirname(sourceFilePath),self._rootPath)
        else:
            self._rootPath = None
            self._relPath = None
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

    @ToolBox_Decorator
    def jobStreamObjects (self) -> dict[str,ToolBox_IWS_JobStreamObj]:
        """Returns a list of Job Steram objects in file."""
        return self._jobStream_collection.items()

    @ToolBox_Decorator
    def jobStreamPaths (self) -> list[str]:
        """Returns a list of Job Stream paths found in file, formatted: {workstation}/{folderPath}/{jobStreamName}.@]"""
        return [_js.name_fullPath for _js in self._jobStream_collection.values()]
    
    @ToolBox_Decorator
    def jobObjects (self) -> dict[str,ToolBox_IWS_JobObj]:
        """Returns a list of Job objects in file."""
        _data:dict[str,ToolBox_IWS_JobObj] = {}
        for _streamObj in self._jobStream_collection.values():
            for _j_path, _j_obj in _streamObj.jobObjects().items():
                if _j_path not in _data.keys():
                    _data[_j_path] = _j_obj
        return _data
    
    @ToolBox_Decorator
    def jobPaths (self) -> list[str]:
        """Returns a list of Job paths found in file, formatted: {workstation}/{folderPath}/{jobStreamName}.{jobName}]"""
        _list = []
        for _js in self._jobStream_collection.values():
            for _jpath in _js.job_list():
                if _jpath not in _list:
                    _list.append(_jpath)
        return _list

    @ToolBox_Decorator
    def openFile (self):
        # ensure instance owns its storage (avoid shared class-level defaults)
        if not getattr(self, "_sourceFileLines", None):
            _holder = None
            with open(self._sourceFile, "r") as f:
                _holder = copy.deepcopy(f.read()).split('\n')
            if (_holder is not None):
                # clean lines and remove returns and next line characters
                self._sourceFileLines = [s.replace('\n', '').replace('\r', '') for s in _holder]
            else:
                self._sourceFileLines = []
            # ensure jobStream_collection is an instance dict (not a shared class dict)
            self._jobStream_collection = {}
            self._logger.debug (f"Opening source file : '{os.path.join(self.sourceFileDirRelPath, self.sourceFileName)}'")
            self._reload_streams_and_jobs()
        return self
    
    @ToolBox_Decorator
    def closeFile(self):
        self._logger.debug (f"Closing source file : '{os.path.join(self.sourceFileDirRelPath, self.sourceFileName)}'")
        # clear lines and ensure a new list is assigned to the instance
        self._sourceFileLines = []
        # clear nested job collections on each stream to break any shared references
        if getattr(self, "_jobStream_collection", None):
            for _stream in list(self._jobStream_collection.values()):
                try:
                    if getattr(_stream, "_job_collection", None):
                        _stream._job_collection.clear()
                except Exception:
                    pass
        # assign a fresh dict to the instance to avoid retaining class-level state
        self._jobStream_collection = {}
        return self
    
    
    @ToolBox_Decorator
    def _clear_ (self):
        # clear nested job collections on each stream first
        if getattr(self, "_jobStream_collection", None):
            for _stream in list(self._jobStream_collection.values()):
                try:
                    if getattr(_stream, "_job_collection", None):
                        _stream._job_collection.clear()
                except Exception:
                    pass
        # assign a new empty dict to the instance (avoids modifying class-level dict)
        self._jobStream_collection = {}
        return self

    @ToolBox_Decorator
    def _reload_streams_and_jobs (self):
        if self._sourceFileLines is None or len(self._sourceFileLines) == 0:
            self.openFile()
            return self
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
        _source_file = os.path.join(self._rootPath, self._relPath, self._fileName)
        for _id_index in range(len(_stream_start_ids)):
            _stream_start = _stream_start_ids[_id_index]
            _stream_path = str(self._sourceFileLines[_stream_start].split(' ')[1])
            if _stream_path not in self._jobStream_collection.keys():
                _stream_edge = _stream_edge_ids[_id_index]
                _stream_end = _stream_end_ids[_id_index]
                _stream_definition_text = "\n".join([_line for _line in self._sourceFileLines[_stream_start:_stream_edge+1] if _line.strip() != ''])
                _stream_end_text = self._sourceFileLines[_stream_end].strip()
                _jobStreamObj = ToolBox_IWS_JobStreamObj(
                    path=_stream_path,
                    definition_text=_stream_definition_text, 
                    end_text=_stream_end_text, 
                    initial_data=None, 
                    sourceFile=_source_file)
                self._jobStream_collection[_stream_path] = _jobStreamObj

            _job_ids = [_id for _id in _job_start_ids if _stream_start < _id < _stream_end]
            for _job_id_index in range(len(_job_ids)):
                _job_line_start = _job_ids[_job_id_index]
                _job_line_stop = int(_job_ids[_job_id_index+1])-1 if _job_id_index < (len(_job_ids)-1) else int(_stream_end -1)
                _job_definition_text = "\n".join([_line for _line in self._sourceFileLines[_job_line_start:_job_line_stop] if _line.strip() != ''])
                _source_job_line = str(self._sourceFileLines[_job_line_start])
                _job_path = _source_job_line.strip().split(' ')[0]
                _alias_index = _source_job_line.find(" AS ")
                _alias_name = _source_job_line[_alias_index+3:].strip().split(' ')[0] if _alias_index != -1 else None
                self._jobStream_collection[_stream_path].add_Job_definition(
                    path= _job_path, 
                    definition_text=_job_definition_text,
                    parent_path=f"{_stream_path}.@",
                    alias_name=_alias_name,
                    initial_data=None, 
                    sourceFile=_source_file
                )   
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
    def search_file_for_terms (self, filterList:list[str]) -> dict[str,list[Match[str]]]:
        _found_terms:dict[str,list[Match[str]]]
        _filetext = "\n".join([str(_stream.__str__()) for _stream in self._jobStream_collection.values()])
        for _term in filterList:
            _match = re.search(_term, _filetext.__str__(), re.IGNORECASE)
            if _match:
                if _term not in _found_terms:
                    _found_terms[_term] = []
                _found_terms[_term].append(_match)
        return _found_terms

    @ToolBox_Decorator
    def get_jobStreamObjects (self) ->list[ToolBox_IWS_JobStreamObj]:
        return [_js for _js in self._jobStream_collection.values()]

    @ToolBox_Decorator
    def get_stream_by_name (self, name:str) -> ToolBox_IWS_JobStreamObj | None:
        """Returns the 1st Job Stream Data block for the given job name, will return None if one can't be found."""
        for _streamPath, _streamData in self._jobStream_collection.items():
            if (name.upper() in _streamPath.upper()):
                return _streamData
        return None
    
    @ToolBox_Decorator
    def get_job_stream (self, workstation:Optional[str]=None, folder:Optional[str]=None, name:Optional[str]=None) -> Optional[ToolBox_IWS_JobStreamObj]:
        """Returns the 1st Job Stream Data block for the search terms.
            - workstation - string
            - folder - string
            - name - string
        One or more search terms will be required or results will be none.
        """
        _search_terms = []
        if workstation is not None or workstation.strip() == '': _search_terms.append(workstation)
        if folder is not None or folder.strip() == '': _search_terms.append(folder)
        if name is not None or name.strip() == '': _search_terms.append(name)
        if (len(_search_terms) == 0):
            warnings.warn(f"Returning None, no search criteria has been provided, all search terms provided are 'NoneType' or blank")
            return None
        _best_match = None
        _highest_score = -1
        for _jobStreamObj in self.get_jobStreamObjects():
            _streamPath = _jobStreamObj.name_fullPath.split('.')[0]
            _parts = _streamPath.split('/')
            _js_ws = _parts.pop(0)
            _js_name = _parts.pop(-1)
            _js_folder = '/'.join(_parts)
            _score = 0
            if workstation is not None or workstation.strip() == '':
                if workstation.upper() in _js_ws.upper(): _score += 10
                if workstation.upper() == _js_ws.upper(): _score += 5
            if folder is not None or folder.strip() == '':
                if folder.upper() in _js_folder.upper(): _score += 10
                if folder.upper() == _js_folder.upper(): _score += 5
            if name is not None or name.strip() == '':
                if name.upper() in _js_name.upper(): _score += 10
                if name.upper() == _js_name.upper(): _score += 5
            if _score != 0 and _score > _highest_score:
                _best_match = _jobStreamObj
                _highest_score = _score
        return _best_match

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
        return self

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
        return self

    @ToolBox_Decorator
    def set_Jobs_NOP (self, value:bool = True, filter_worksataiton:list[str]=None, filter_folder:list[str]=None, filer_streamName:list[str]=None, filer_jobName:list[str]=None):
        _stream_keys = [_path for _path in self._jobStream_collection.keys()]
        if filer_streamName is not None:        
            _stream_keys = [_path for _jsn in filer_streamName for _path in _stream_keys if _jsn.upper() in _path.upper()]
        for _key in _stream_keys:
            _stream = self._jobStream_collection[_key]
            for _jobPath in _stream.job_list():
                _skip = False
                if (filter_worksataiton is not None) and all( _ws.upper() not in _jobPath.upper() for _ws in filter_worksataiton): 
                    _skip = True
                if (filter_folder is not None) and all( _f.upper() not in _jobPath.upper() for _f in filter_folder): 
                    _skip = True
                if (filer_jobName is not None) and all( _jn.upper() not in _jobPath.upper() for _jn in filer_jobName): 
                    _skip = True
                if _skip == True : continue
                _jobData = _stream.get_job_by_name(_jobPath.split('.')[-1])
                _jobData.set_NOP(value=value)
        return self
                
    @ToolBox_Decorator
    def duplciate_jobStream_by_workstaion (self, jobStreamName:str, sourceWorkstaion:str, targetWorkstation:str) -> ToolBox_IWS_JobStreamObj :
        _target_stream = self.get_stream_by_name(jobStreamName)
        if (_target_stream is not None) and (sourceWorkstaion.upper() in _target_stream.name_path):
            _duplcaite_stream = copy.deepcopy(_target_stream) if _target_stream is not None else None
            if (_duplcaite_stream is not None) and (sourceWorkstaion is not None) and (targetWorkstation is not None):
                _duplcaite_stream.search_replace_text(sourceWorkstaion, targetWorkstation)
                _duplcaite_stream._streamPath = _duplcaite_stream._streamPath.replace(sourceWorkstaion, targetWorkstation)
                _duplcaite_stream._streamName = _duplcaite_stream.name_path.replace(sourceWorkstaion, targetWorkstation)
                if _duplcaite_stream.name_fullPath not in self._jobStream_collection.keys():
                    self._logger.debug(f"Duplicating Stream : '{_target_stream.name_path}' to '{_duplcaite_stream.name_path}'")
                    self._jobStream_collection[_duplcaite_stream.name_fullPath] = _duplcaite_stream

                    return self._jobStream_collection[_duplcaite_stream.name_fullPath]
        return None
    