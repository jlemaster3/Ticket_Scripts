#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, shutil, copy
from typing import Any
from ToolBox.ToolBox_logger import OutputLogger

class ToolBox_FileData:
    _logger:OutputLogger = OutputLogger().get_instance()
    _sourceFile:str = None
    _rootPath:str = None
    _relPath:str = None
    _fileName:str = None
    _rawLines:list[str] = []
    _modLines:list[str] = []
    _stream_START_ids:list[int] = []
    _stream_EDGE_ids:list[int] = []
    _stream_END_ids:list[int] = []
    _job_START_ids:list[int] = []
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


    _mod_stream_START_ids:list[int] = []
    _mod_stream_EDGE_ids:list[int] = []
    _mod_stream_END_ids:list[int] = []
    _mod_job_START_ids:list[int] = []
    _mod_DOCOMMAND_ids:list[int] = []
    _mod_RUNCYCLE_ids:list[int] = []
    _mod_EXCEPT_ids:list[int] = []
    _mod_STREAMLOGON_ids:list[int] = []
    _mod_DESCRIPTION_ids:list[int] = []
    _mod_DRAFT_ids:list[int] = []
    _mod_REQUEST_ids:list[int] = []
    _mod_FOLLOWS_ids:list[int] = []
    _mod_TASKTYPE_ids:list[int] = []
    _mod_OUTPUTCOND_ids:list[int] = []
    _mod_RECOVERY_ids:list[int] = []
    _mod_NOP_ids:list[int] = []

    def __init__(self, sourceFilePath:str, rootPath:str=None):
        if not(os.path.isfile(sourceFilePath)):
            self._logger.error(f"Target source path is not a valid file : '{sourceFilePath}'")
            return
        self._sourceFile = sourceFilePath
        self._fileName = os.path.basename(sourceFilePath)
        if rootPath != None : self.rootPath = rootPath
        self._stream_START_ids = []
        self._stream_EDGE_ids = []
        self._stream_END_ids = []
        self._job_START_ids = []
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

        self._openFile()

    
    def _openFile (self):
        with open(self._sourceFile, "r") as f:
            self._rawLines = copy.deepcopy(f.readlines())
        if len(self._rawLines) == 0:
            self._logger.warning (f"No lines loaded form source file : '{self._sourceFile}'")
        for _line_id, _line in enumerate(self._rawLines):
            if "SCHEDULE" in str(_line).strip()[0:9]:
                self._stream_START_ids.append(_line_id)
            if 'DRAFT' in _line:
                self._DRAFT_ids.append(_line_id)
            if 'REQUEST' in _line[0:20].upper():
                self._REQUEST_ids.append(_line_id)
            if ':' in _line[0:2]:
                self._stream_EDGE_ids.append(_line_id)
            if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) or (any(_s in str(_line).strip()[0:5] for _s in ['PRD#', 'NPR#'])) and ('#' in str(_line[2:]).strip()):
                self._job_START_ids.append(_line_id)
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
        self.reset_mod_lines()
        self.update_moded_lineIDs()
        return self
    
    def update_moded_lineIDs (self):
        self._mod_stream_START_ids = []
        self._mod_stream_EDGE_ids = []
        self._mod_stream_END_ids = []
        self._mod_job_START_ids = []
        self._mod_DOCOMMAND_ids = []
        self._mod_RUNCYCLE_ids = []
        self._mod_EXCEPT_ids = []
        self._mod_STREAMLOGON_ids = []
        self._mod_DESCRIPTION_ids = []
        self._mod_DRAFT_ids = []
        self._mod_REQUEST_ids = []
        self._mod_FOLLOWS_ids = []
        self._mod_TASKTYPE_ids = []
        self._mod_OUTPUTCOND_ids = []
        self._mod_RECOVERY_ids = []
        self._mod_NOP_ids = []
        for _line_id, _line in enumerate(self._modLines):
            if "SCHEDULE" in str(_line).strip()[0:9]:
                self._mod_stream_START_ids.append(_line_id)
            if 'DRAFT' in _line:
                self._mod_DRAFT_ids.append(_line_id)
            if 'REQUEST' in _line[0:20].upper():
                self._mod_REQUEST_ids.append(_line_id)
            if ':' in _line[0:2]:
                self._mod_stream_EDGE_ids.append(_line_id)
            if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) or (any(_s in str(_line).strip()[0:5] for _s in ['PRD#', 'NPR#'])) and ('#' in str(_line[2:]).strip()):
                self._mod_job_START_ids.append(_line_id)
            if 'DESCRIPTION' in _line:
                self._mod_DESCRIPTION_ids.append(_line_id)
            if 'RUNCYCLE' in _line:
                self._mod_RUNCYCLE_ids.append(_line_id)
            if 'FOLLOWS' in _line:
                self._mod_FOLLOWS_ids.append(_line_id)
            if 'EXCEPT' in _line:
                self._mod_EXCEPT_ids.append(_line_id)
            if 'DOCOMMAND' in _line:
                self._mod_DOCOMMAND_ids.append(_line_id)
            if 'STREAMLOGON' in _line:
                self._mod_STREAMLOGON_ids.append(_line_id)
            if 'OUTPUTCOND' in _line:
                self._mod_OUTPUTCOND_ids.append(_line_id)
            if 'TASKTYPE' in _line:
                self._mod_TASKTYPE_ids.append(_line_id)
            if 'RECOVERY' in _line:
                self._mod_RECOVERY_ids.append(_line_id)
            if 'NOP' in _line:
                self._mod_NOP_ids.append(_line_id)   
            if "END" in str(_line).strip()[0:4] and 'ENDJOIN' not in str(_line).strip():
                self._mod_stream_END_ids.append(_line_id)

    def reset_mod_lines (self) :
        self._modLines = copy.deepcopy(self._rawLines)
    
    @property
    def raw_text (self) -> str:
        """Returns the raw text from the source file un-edited."""
        return str(''.join(self._rawLines))
    
    @property
    def modified_text (self) -> str:
        """Returns the modified text after modifications have been made."""
        return str(''.join(self._modLines))
    
    @property
    def sourcePath_full(self) -> str:
        return os.path.join (self.rootPath, self.relPath, self._fileName)
    
    @property
    def sourcePath_rel(self) -> str:
        return os.path.join (self.relPath, self._fileName)
    
    @property
    def rootPath(self) -> str:
        return self._rootPath
    
    @rootPath.setter
    def rootPath (self, rootPath:str) :
        self._rootPath = rootPath
        self._relPath = os.path.relpath(os.path.dirname(self._sourceFile),rootPath)

    @property
    def relPath(self) -> str:
        return self._relPath
    

    def get_file_stats (self):
        self._logger.debug(f"Number of Job Streams : [{len(self._stream_START_ids)}]")
        self._logger.debug(f"Number of Jobs : [{len(self._job_START_ids)}]")
        return self
    
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
        
    def saveTo (self, outputfolder:str, rename:str=None, useRelPath:bool=False) -> str:
        _outputPath = outputfolder if useRelPath == False else os.path.join(outputfolder,self._relPath)
        os.makedirs(_outputPath, exist_ok=True)
        _filename = rename if rename != None else self._fileName
        _outputFilePath = os.path.join (_outputPath, _filename)
        with open(_outputFilePath, "w") as output_file:
            output_file.write(self.modified_text)
        return _outputFilePath
    
    def set_Streams_onRequest (self, filter_worksataiton:list[str]=None, filter_folder:list[str]=None, filer_streamName:list[str]=None):
        self.update_moded_lineIDs()
        for _stream_id in range(len(self._mod_stream_START_ids)):
            _stream_start = self._mod_stream_START_ids[_stream_id]
            _stream_edge = self._mod_stream_EDGE_ids[_stream_id]
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
            if (len(self._mod_REQUEST_ids) >= 1):
                _has_onrequest = False
                for _req_id in self._mod_REQUEST_ids:
                    if (_stream_start <= _req_id <= _stream_edge):
                        _has_onrequest = True
                        _target_name = str(self._modLines[_stream_start].split(' ')[1]).rstrip(' \r\n')
                        self._logger.debug (f"Stream : {_target_name} is already ON REQUEST")
                if _has_onrequest == True : _skip = True
            if _skip == True: continue
            _target_line = _stream_start
            for _desc in self._mod_DESCRIPTION_ids:
                if (_stream_start < _desc < _stream_edge) and _desc > _target_line:
                    print (_stream_start, _desc, _stream_edge)
                    _target_line = _desc

            self._modLines.insert(int(_target_line+1), 'ON REQUEST\n')
            _target_name = str(self._modLines[_stream_start].split(' ')[1]).rstrip(' \r\n')
            self._logger.debug (f"Added On-Request to stream : {_target_name}")
            

