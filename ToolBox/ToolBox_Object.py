#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, shutil, copy, uuid
from collections import UserDict
from typing import Any
from ToolBox.ToolBox_logger import OutputLogger
#from ToolBox.ToolBox_Utilities import ToolBox_Decorator

#-------------------------------------------------
#   Decorator Functions / Wrappers
#-------------------------------------------------

def ToolBox_Decorator(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        return result
    return wrapper


class ToolBox_FileData (UserDict):
    _id:str = None
    _logger:OutputLogger = OutputLogger().get_instance()
    _sourceFile:str = None
    _rootPath:str = None
    _relPath:str = None
    _fileName:str = None
    _rawLines:list[str] = []
    _modLines:list[str] = []

    #find way to convers id list to dynicly names colelction by keyword and pre-difiend filter/labmda action
    _STREAM_START_ids:list[int] = []
    _STREAM_EDGE_ids:list[int] = []
    _STREAM_END_ids:list[int] = []
    _JOB_START_ids:list[int] = []
    _DOCOMMAND_ids:list[int] = []
    _RUNCYCLE_ids:list[int] = []
    _EXCEPT_ids:list[int] = []
    _STREAMLOGON_ids:list[int] = []
    _DESCRIPTION_ids:list[int] = []
    _DRAFT_ids:list[int] = []
    _REQUEST_ids:list[int] = []
    _FOLLOWS_ids:list[int] = []
    _TASKTYPE_ids:list[int] = []
    _OUTPUTCOND_ids:list[int] = []
    _RECOVERY_ids:list[int] = []
    _NOP_ids:list[int] = []

    def __init__(self, sourceFilePath:str, rootPath:str=None, initial_data:dict[str,Any]=None):
        super().__init__(initial_data)
        if not(os.path.isfile(sourceFilePath)):
            self._logger.error(f"Target source path is not a valid file : '{sourceFilePath}'")
            return
        self._sourceFile = sourceFilePath
        self._fileName = os.path.basename(sourceFilePath)
        _id = str(uuid.uuid5(uuid.NAMESPACE_DNS, sourceFilePath))
        self._id = str(_id)
        if rootPath != None : self.rootPath = rootPath
    

    def __setitem__(self, key, value):
        # take custom action when setting a keyword, if keyword is X do Y then add to data
        if isinstance(value, str):
            self.data[key] = value
        else:
            self.data[key] = value
    

    def __getitem__(self, key):
        if isinstance(key, str):
            key = key
        return self.data[key] 

    @ToolBox_Decorator
    def openFile (self):
        with open(self._sourceFile, "r") as f:
            self._rawLines = copy.deepcopy(f.readlines())
            
        if len(self._rawLines) == 0:
            self._logger.warning (f"No lines loaded form source file : '{self._sourceFile}'")
        self.reset_mod_lines()
        self.update_mod_lineIDs()
        return self

    @ToolBox_Decorator
    def reset_mod_lines (self) :
        self._modLines = copy.deepcopy(self._rawLines)
        return self

    @ToolBox_Decorator
    def update_mod_lineIDs (self):
        #find way to convers id list to dynicly names colelction by keyword and pre-difiend filter/labmda action
        self._STREAM_START_ids = []
        self._STREAM_EDGE_ids = []
        self._STREAM_END_ids = []
        self._JOB_START_ids = []
        self._DOCOMMAND_ids = []
        self._RUNCYCLE_ids = []
        self._EXCEPT_ids = []
        self._STREAMLOGON_ids = []
        self._DESCRIPTION_ids = []
        self._DRAFT_ids = []
        self._REQUEST_ids = []
        self._FOLLOWS_ids = []
        self._TASKTYPE_ids = []
        self._OUTPUTCOND_ids = []
        self._RECOVERY_ids = []
        self._NOP_ids = []
        for _line_id, _line in enumerate(self._modLines):
            if "SCHEDULE" in str(_line).strip()[0:9]:
                self._STREAM_START_ids.append(_line_id)
            if 'DRAFT' in _line:
                self._DRAFT_ids.append(_line_id)
            if 'REQUEST' in _line[0:20].upper():
                self._REQUEST_ids.append(_line_id)
            if ':' in _line[0:2]:
                self._STREAM_EDGE_ids.append(_line_id)
            if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) or (any(_s in str(_line).strip()[0:5] for _s in ['PRD#', 'NPR#'])) and ('#' in str(_line[2:]).strip()):
                self._JOB_START_ids.append(_line_id)
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
                self._STREAM_END_ids.append(_line_id)
        return self

    
    @property
    def id (self) -> str:
        """Returns randomly generated ID value."""
        return self._id
    
    @property
    def text_raw (self) -> str:
        """Returns the raw text from the source file un-edited."""
        return str(''.join(self._rawLines))
    
    @property
    def text_modified (self) -> str:
        """Returns the modified text after modifications have been made."""
        return str(''.join(self._modLines))
    
    @property
    def has_changed (self) -> bool:
        """Returns a true falce value if the modified value is diffrent from the orriginal contents of the files when opened."""
        if len(self._rawLines >= 1) and (len(self._rawLines) == len(self._modLines)):
            for _i in range(len(self._rawLines)):
               if (self._rawLines[_i] != self._modLines[_i]) :
                   return False
            return True
        return False

    @property
    def sourceFilePath(self) -> str:
        return self._sourceFile
    
    @property
    def sourceFileName(self) -> str:
        return os.path.basename(self._sourceFile)
    
    @property
    def sourceFileBaseName(self) -> str:
        return '.'.join(os.path.basename(self._sourceFile).split('.')[0:-1])
    
    @property
    def sourceFileFormat(self) -> str:
        return os.path.basename(self._sourceFile).split('.')[-1]
    
    @property
    def sourceFileDir(self) -> str:
        return os.path.dirname(self._sourceFile)
    
    @property
    def sourceFileDirRoot(self) -> str:
        return os.path.dirname(self._rootPath)
    
    @property
    def sourceFileDirRelPath(self) -> str:
        return os.path.relpath(os.path.dirname(self._sourceFile), self._rootPath)
    
    @property
    def rootPath(self) -> str:
        return self._rootPath
    
    @rootPath.setter
    def rootPath (self, value:str) :
        self._rootPath = value
        self._relPath = os.path.relpath(os.path.dirname(self._sourceFile),self._rootPath)
    
    @ToolBox_Decorator
    def get_file_stats (self):
        self._logger.debug(f"Number of Job Streams : [{len(self._STREAM_START_ids)}]")
        self._logger.debug(f"Number of Jobs : [{len(self._JOB_START_ids)}]")
        return self
    
    @ToolBox_Decorator
    def search_for_terms (self, searchTerms:list[str]) -> dict[int, list[str]] :
        _found_lineID_terms:dict[int, list[str]] = {}
        for _line_id, _line in enumerate(self._rawLines):
            for _term in searchTerms:
                if _term.lower() in _line.lower():
                    if _line_id not in _found_lineID_terms.keys():
                        _found_lineID_terms[_line_id] = []
                    _found_lineID_terms[_line_id].append(_line_id)
        if len(_found_lineID_terms.keys()) == 0:
            return None
        else:
            return _found_lineID_terms
        
    
    @ToolBox_Decorator
    def saveTo (self, outputfolder:str, rename:str=None, useRelPath:bool=False) -> str:
        #needs to be reworked, not saving some files in the correct path.
        _outputPath = outputfolder if useRelPath == False else os.path.join(outputfolder,self._relPath)
        os.makedirs(_outputPath, exist_ok=True)
        _filename = rename if rename != None else self._fileName
        _outputFilePath = os.path.join (_outputPath, _filename)
        if os.path.exists (_outputFilePath):
            os.remove(_outputFilePath)
        with open(_outputFilePath, "w") as output_file:
            output_file.write(self.text_modified)
        return _outputFilePath
    

    @ToolBox_Decorator
    def set_Streams_onRequest (self, filter_worksataiton:list[str]=None, filter_folder:list[str]=None, filer_streamName:list[str]=None):
        # add option to remove or toggle OnRequest
        # refactor for use by other keywords and ids.
        self.update_mod_lineIDs()
        for _stream_id in range(len(self._STREAM_START_ids)):
            _stream_start = self._STREAM_START_ids[_stream_id]
            _stream_edge = self._STREAM_EDGE_ids[_stream_id]
            _skip:bool = False
            if (filter_worksataiton != None) and (len(filter_worksataiton) >= 1) :
                for _ws_term in filter_worksataiton:
                    if (_ws_term.upper() not in self._modLines[_stream_start].upper()):
                        _skip = True

            if (filter_folder != None) and (len(filter_folder) >= 1) :
                for _fl_term in filter_folder:
                    if (_fl_term.upper() not in self._modLines[_stream_start].upper()):
                        _skip = True

            if (filer_streamName != None) and (len(filer_streamName) >= 1) :
                for _name_term in filer_streamName:
                    if (_name_term.upper() not in self._modLines[_stream_start].upper()):
                        _skip = True
            if (len(self._REQUEST_ids) >= 1):
                _has_onrequest = False
                for _req_id in self._REQUEST_ids:
                    if (_stream_start <= _req_id <= _stream_edge):
                        _has_onrequest = True
                        _target_name = str(self._modLines[_stream_start].split(' ')[1]).rstrip(' \r\n')
                        self._logger.debug (f"Stream : '{_target_name}' is already ON REQUEST")
                if _has_onrequest == True : _skip = True
            if _skip == True: continue

            _target_line = _stream_start
            for _desc in self._DESCRIPTION_ids:
                if (_stream_start < _desc < _stream_edge) and _desc > _target_line:
                    
                    _target_line = _desc

            self._modLines.insert(int(_target_line+1), 'ON REQUEST\n')
            _target_name = str(self._modLines[_stream_start].split(' ')[1]).rstrip(' \r\n')
            self._logger.debug (f"Added On-Request to stream : '{_target_name}'")
        return self
            

