#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, copy
from datetime import datetime
from collections import UserDict
from typing import Any
from ToolBox_V2.ToolBox_logger import OutputLogger
from ToolBox_V2.ToolBox_DataTypes.ToolBox_File_Base import ToolBox_FileData
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_Stream_Obj import ToolBox_IWS_Stream_Obj
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_Job_Obj import ToolBox_IWS_Job_Obj

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


class ToolBox_IWS_JIL_File(ToolBox_FileData):
    """JIL file metadata for ECS node system."""
    log:OutputLogger = OutputLogger().get_instance()
    _source_file_text:str = None

    _jobStream_collection:list[ToolBox_IWS_Stream_Obj] = []
    
    def __init__(self, path:str, rootPath:str=None, initial_data:dict[str,Any]=None):
        super().__init__(path, rootPath, initial_data)
        self["type"] = "IWS JIL"
        self._isOpen = False
        self._source_file_text = None
        self._jobStream_collection = []
    
    #------- private methods -------#

    #------- properties -------#
    @property
    def job_stream_paths (self) -> list[str]:
        """Returns a list of Job Stream paths found in file."""
        return [_js.full_path for _js in self._jobStream_collection]
    
    @property
    def job_paths (self) -> list[str]:
        """Returns a list of Job Stream paths found in file."""
        return [_j.full_path for _js in self._jobStream_collection for _j in _js.job_objects]
    
    @property
    def job_stream_objects (self) -> list[ToolBox_IWS_Stream_Obj]:
        """Returns a list of Job Stream Objects contained in file"""
        return self._jobStream_collection
    
    @property
    def job_objects (self) -> list[ToolBox_IWS_Stream_Obj]:
        """Returns a list of Job Objects contained in file"""
        return [_j for _js in self._jobStream_collection for _j in _js.job_objects]
    
    #------- Public Methods -------#

    @ToolBox_Decorator
    def open_file (self, quite_logging:bool=True):
        """Opens source Jil file and converts to IWS objects."""
        if self.is_Open != True:
            try:
                _holder = None
                with open(self.sourceFilePath, "r", encoding="utf-8") as f:
                    _holder = copy.deepcopy(f.read())
                if (_holder is not None):
                    if (quite_logging != True): self.log.debug (f"Opening source file : '{self.relFilePath}'")
                    self._source_file_text = _holder
                    self._isOpen = True
                    self.load_jobStreams_from_text ()
                else:
                    self.log.debug (f"Unable to read file contents : '{self.relFilePath}'")
                    self._source_file_text = None
                    self._isOpen = False
            except BufferError as errmsg:
                self.log.warning (f"Unable to open file : '{self.relFilePath}'", data = errmsg)
            except FileNotFoundError as errmsg:
                self.log.error (f"File not found : '{self.relFilePath}'")
        return self
    
    @ToolBox_Decorator
    def close_file (self, quite_logging:bool=True):
        """Closes current instance of the file, clearing all temporary changes if not saved."""
        if self.is_Open == True:
            if (quite_logging != True): self.log.debug (f"Closing source file : '{self.relFilePath}'")
            self._isOpen = False
            self._source_file_text = None
            self._jobStream_collection = []
        return self
    
    @ToolBox_Decorator
    def save_File (self, outputFolder:str, rename:str=None, useRelPath:bool=False):
        """Saves teh current modifications of teh file to the target location."""
        _outputPath = os.path.join(outputFolder,self.relPath) if useRelPath == True else outputFolder
        os.makedirs(_outputPath, exist_ok=True)
        _filename = rename if rename != None else self.name
        _outputFilePath = os.path.join (_outputPath, f"{_filename}{self.foramt}")
        if os.path.exists (_outputFilePath):
            os.remove(_outputFilePath)
        try:
            _filetext = "\n".join([_stream.get_current_text() for _stream in self._jobStream_collection])
            with open(_outputFilePath, "w") as output_file:
                output_file.write(_filetext)
            self.log.info (f"Saved file : '{self.relFilePath}' as file : '{_outputFilePath}'")
        except SystemError as se :
            raise (se)
        return self
    
    @ToolBox_Decorator
    def _clear_ (self):
        """Clears out Job Stream collection"""
        self._jobStream_collection = []
        return self

    @ToolBox_Decorator
    def load_jobStreams_from_text (self, text:str=None) :
        """Take source File text and breaks it down into seprate object classes for editing."""
        if self.is_Open != True:
            self.open_file()
        _note_line_ids:list[int] = []
        _stream_start_ids:list[int] = []
        _stream_edge_ids:list[int] = []
        _job_start_ids:list[int] = []
        _stream_end_ids:list[int] = []
        _lines = self._source_file_text.splitlines() if text is None else text
        for _line_id, _line in enumerate(_lines):
            if "SCHEDULE" in str(_line).strip()[0:9]:
                _stream_start_ids.append(_line_id)
            if ':' in _line[0:2]:
                _stream_edge_ids.append(_line_id)
            if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) :#or (any(_s in str(_line).strip()[0:5] for _s in ['PRD#', 'NPR#'])) and ('#' in str(_line[2:]).strip()):
                _job_start_ids.append(_line_id)
            if "END" in str(_line).strip()[0:4] and 'ENDJOIN' not in str(_line).strip():
                _stream_end_ids.append(_line_id)
            if '#' in str(_line).strip()[0:4]:
                _note_line_ids.append(_line_id)
        #self._clear_()
        _stream_last_end = 0
        for _id_index in range(len(_stream_start_ids)):
            _stream_start = _stream_start_ids[_id_index]
            _stream_edge = _stream_edge_ids[_id_index]
            _stream_end = _stream_end_ids[_id_index]
            _stream_note_ids = [_idx for _idx in _note_line_ids if _stream_last_end <= _idx <= _stream_start]
            _stream_text = ""
            if len(_stream_note_ids) >= 1:
                _stream_text += "\n".join([_line for _line in _lines[min(_stream_note_ids):max(_stream_note_ids)+1]])
                _stream_text += '\n'
            _stream_text += "\n".join([_line for _line in _lines[_stream_start:_stream_edge+1] if _line.strip() != ''])
            _jobStreamObject = ToolBox_IWS_Stream_Obj(
                definition_text =  _stream_text,
                end_text = _lines[_stream_end].strip(),
                sourceFile = self.sourceFilePath
                )
            _job_ids = [_id for _id in _job_start_ids if _stream_start < _id < _stream_end]
            _job_last_end = _stream_edge
            for _job_id_index in range(len(_job_ids)):
                _job_line_start = _job_ids[_job_id_index]
                _job_line_stop = int(_job_ids[_job_id_index+1])-1 if _job_id_index < (len(_job_ids)-1) else int(_stream_end -1)
                for _i in reversed(range(_job_line_start, _job_line_stop)):
                    _a_val = _lines[_i].strip().lower() # last to first
                    if (_a_val is not None) and ((_a_val.strip() == '') or ('#' in _a_val.strip()[0])):
                        _job_line_stop -= 1
                    else:
                        break  # stop at the first mismatch
                _job_note_ids = [_idx for _idx in _note_line_ids if _job_last_end <= _idx <= _job_line_start]
                _job_text = ""
                if len(_job_note_ids) >= 1:
                    _job_text += "\n".join([_line for _line in _lines[min(_job_note_ids):max(_job_note_ids)+1]])
                    _job_text += "\n"
                _job_text += "\n".join([_line for _line in _lines[_job_line_start:_job_line_stop] if _line.strip() != ''])
                _jobStreamObject.add_job_by_text(
                    definition_text = _job_text,
                    sourceFile = self.sourceFilePath
                )
                _job_last_end = _job_line_stop
            self._jobStream_collection.append(_jobStreamObject)
            _stream_last_end = _stream_end
        return self
    
    @ToolBox_Decorator
    def get_Job_Stream_by_name (self, name:str):
        """Returns the target Job Stream by Name if found, returns None if none can be found."""
        for _stream in self._jobStream_collection:
            if (name.upper() in _stream.full_path.upper()):
                return _stream
        return None
    
    @ToolBox_Decorator
    def set_all_Stream_ONREQUEST (self, value:bool) :
        """Sets the state of 'On Request' for all Job Streams in this file."""
        if self.is_Open != True:
            self.open_file()
        for _stream in self._jobStream_collection:
            _stream.set_ON_REQUEST (value)
        return self
    
    @ToolBox_Decorator
    def set_all_Streams_DRAFT (self, value:bool) :
        """Sets the state of 'On Request' for all Job Streams in this file."""
        if self.is_Open != True:
            self.open_file()
        for _stream in self._jobStream_collection:
            _stream.set_DRAFT (value)
        return self
    
    @ToolBox_Decorator
    def set_all_Jobs_NOP (self, value:bool) :
        """Sets the state of 'On Request' for all Job Streams in this file."""
        if self.is_Open != True:
            self.open_file()
        for _stream in self._jobStream_collection:
            _stream.set_all_Jobs_NOP(value)
        return self