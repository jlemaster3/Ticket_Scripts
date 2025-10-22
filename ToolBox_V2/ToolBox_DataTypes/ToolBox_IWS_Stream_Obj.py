#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, re
from datetime import datetime
from collections import UserDict
from typing import Any
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_Job_Obj import ToolBox_IWS_Job_Obj
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_Follows_Obj import ToolBox_IWS_Follows_Obj, ToolBox_IWS_Join_Obj
from ToolBox_V2.ToolBox_logger import OutputLogger
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

class ToolBox_IWS_Stream_Obj (UserDict):
    """Data Class representing and handing IWS Job Stream actions"""
    log:OutputLogger = OutputLogger().get_instance()
    _source_file:str = None
    _source_text:str = None
    _source_end_text:str = None
    _modified_text:str = None
    _modified_end_text:str = None
    _defined_path:str = None
    _name:str = None
    _workstaion:str = None
    _folder:str = None

    _job_collection:list[ToolBox_IWS_Job_Obj] = []
    _follows_collection:list[ToolBox_IWS_Follows_Obj|ToolBox_IWS_Join_Obj] = []

    def __init__(self, definition_text:str, end_text:str=None, sourceFile:str=None, initial_data:dict[str,Any]=None):
        super().__init__(initial_data)
        self._source_file = sourceFile
        self._source_text = definition_text
        self._source_end_text = end_text
        self._modified_text = self._source_text
        self._modified_end_text = self._source_end_text
        self._job_collection = []
        self._reset_values_from_modified_text()

    
    def __setitem__(self, key, value):
        if isinstance(value, str):
            self.data[key] = value
        else:
            self.data[key] = value

    
    def __getitem__(self, key):
        if isinstance(key, str):
            key = key
        return self.data[key] 

    #------- private methods -------#

    @ToolBox_Decorator
    def _reset_values_from_modified_text (self):
        """collects values from the current state of the Job Stream Modified text."""
        _lines = str(self._modified_text).splitlines()
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
            self._defined_path = str(_line.split(' ')[1])
            _js_parts = self._defined_path.split('/')
            self._workstaion = _js_parts.pop(0)
            self._name = _js_parts.pop(-1)
            self._folder = f"/{'/'.join(_js_parts)}/"
        self._reset_dependancies_from_modified_text()
    
    @ToolBox_Decorator
    def _reset_dependancies_from_modified_text (self):
        """Collects dependancies from the current state of the Job Stream Modified text."""
        self._follows_collection = []
        _lines = str(self._modified_text).splitlines()
        _follows_ids:list[int] = []
        _join_ids:list[int] = []
        _endjoin_ids:list[int] = []
        for _line_id, _line in enumerate(_lines):
            if ('JOIN' in _line[0:10]) and ('ENDJOIN' not in _line[0:10]):
                _join_ids.append(_line_id)
            if 'FOLLOWS' in _line[0:14]:
                _follows_ids.append(_line_id)
            if 'ENDJOIN' in _line[0:10]:
                _endjoin_ids.append(_line_id)
        if (len(_join_ids) >= 1) and (len(_join_ids) == (len(_endjoin_ids))):
            for _join_idx in range(len(_join_ids)):    
                _join_line = _lines[_join_ids[_join_idx]]
                _endjoin_line = _lines[_endjoin_ids[_join_idx]]
                _new_join_obj = ToolBox_IWS_Join_Obj (
                    definition_text= _join_line, 
                    end_text= _endjoin_line, 
                    sourceFile= self._source_file, 
                    parent_path= self.full_path
                )
                _join_follow_ids = []
                for _f_line_idx in _follows_ids:
                    if _join_ids[_join_idx] < _f_line_idx < _endjoin_ids[_join_idx]:
                        _join_follow_ids.append(_f_line_idx)
                for _jf_line_id in _join_follow_ids:
                    _jf_line = _lines[_jf_line_id]
                    _new_join_obj.add_follows_by_text(
                        definition_text=_jf_line,
                        sourceFile=self._source_file
                    )
                self._follows_collection.append(_new_join_obj)
                _follows_ids = [item for item in _follows_ids if item not in _join_follow_ids]
        if (len(_follows_ids) >= 1):
            for _follow_line_id in range(len(_follows_ids)):    
                _line = _lines[_follows_ids[_follow_line_id]]
                _new_follow = ToolBox_IWS_Follows_Obj(
                    definition_text= _line,
                    sourceFile= self._source_file,
                    parent_path= self.full_path 
                )
                self._follows_collection.append(_new_follow)

        
    @ToolBox_Decorator
    def _update_follows_in_modified_text (self):
        """Collects dependancies from the current state of the Job Stream Modified text."""
        if len(self._follows_collection) != 0:
            _lines = str(self._modified_text).splitlines()
            _follows_ids:list[int] = []
            _join_ids:list[int] = []
            _endjoin_ids:list[int] = []
            for _line_id, _line in enumerate(_lines):
                if ('JOIN' in _line[0:10]) and ('ENDJOIN' not in _line[0:10]):
                    _join_ids.append(_line_id)
                if 'FOLLOWS' in _line[0:14]:
                    _follows_ids.append(_line_id)
                if 'ENDJOIN' in _line[0:10]:
                    _endjoin_ids.append(_line_id)
            _remove_list:list[int] = _follows_ids + _join_ids +_endjoin_ids
            if len (_remove_list) != 0 :
                _prev_id = min(_remove_list)
                _cleaned_lines = [_line for _idx, _line in enumerate(_lines) if _idx not in _remove_list]
                _follows_text = [_f_obj.get_current_text() for _f_obj in self._follows_collection]
                for _i, _new_line in enumerate(_follows_text):
                    _cleaned_lines.insert(_prev_id + _i, _new_line)
                _new_text = '\n'.join(_cleaned_lines)
                self._modified_text = _new_text

    #------- properties -------#

    @property
    def workstaion (self) -> str:
        """Returns assigned Job Stream Name as stored in IWS."""
        return self._name
    
    @workstaion.setter
    def workstaion (self, value:str) :
        """Sets the value of the assigned Workstaion."""
        self._workstaion = value

    @property
    def folder (self) -> str:
        """Returns assigned folder Path in IWS."""
        return self._folder
    
    @folder.setter
    def folder (self, value:str) :
        """Sets the value of the folder Path in IWS."""
        self._folder = value

    @property
    def name (self) -> str:
        """Returns assigned Job Stream Name as stored in IWS."""
        return self._name
    
    @name.setter
    def name (self, value:str) :
        """Sets the value of the Job Stream Name."""
        self._name = value
    
    @property
    def full_path (self) -> str:
        """Returns the full path of the Job Stream as shown in IWS when viewed in a schedule.
        format: {workstation}/{folderPath}/{jobStreamName}.@
        """
        return f"{self._workstaion}{self._folder}{self._name}.@"
    
    @property
    def job_objects (self) -> list[ToolBox_IWS_Job_Obj]:
        """Returns a list of Job Objects contained in this Job Stream Object"""
        return self._job_collection
    
    @property
    def job_paths (self) -> list[str]:
        """Returns a list of Job paths found in this Job Stream Object."""
        return [_j.full_path for _j in self._job_collection]
    
    @property
    def job_data (self) -> dict[str, ToolBox_IWS_Job_Obj]:
        """Returns a dictionary of Job Paths and Job Objects as key value pairs."""
        _holder = {}
        for _job in self._job_collection:
            _holder[_job.full_path] = _job
        return _holder

    @property
    def follows_list (self) -> list[ToolBox_IWS_Follows_Obj|ToolBox_IWS_Join_Obj]:
        """Returns the list of follows and join objects found in this Job Stream"""
        return self._follows_collection
    
    @property
    def notes (self) -> str:
        _lines = str(self._modified_text).splitlines()
        _note_line_ids:list[int] = []
        _stream_start_ids:list[int] = []
        for _line_id, _line in enumerate(_lines):
            if "SCHEDULE" in str(_line).strip()[0:9]:
                _stream_start_ids.append(_line_id)
            if '#' in str(_line).strip()[0:4]:
                _note_line_ids.append(_line_id)
        _holder = []
        for _id_index in range(len(_stream_start_ids)):
            for _id in range(len(_note_line_ids)):
                if _note_line_ids[_id] < _stream_start_ids[_id_index]:
                    _holder.append(_lines[_note_line_ids[_id]])
        if len(_holder) >= 1:
            return '\n'.join (_holder)
        else:
            return None
        
    @notes.setter
    def notes (self, value:str) :
        """Sets or adds notes to end of current notes found above Job Stream definition"""
        _lines = str(self._modified_text).splitlines()
        _stream_start_ids:list[int] = []
        for _line_id, _line in enumerate(_lines):
            if "SCHEDULE" in str(_line).strip()[0:9]:
                _stream_start_ids.append(_line_id)
        if (self.notes is None) or (self.notes.strip() == ''):
            _holder = [line.strip() for line in value.splitlines() if line.strip()]
            _holder.extend(_lines)
            self._modified_text = '\n'.join([_l for _l in _holder])
        else:
            _cur_notes:list[str] = self.notes.splitlines()
            _new_notes:list[str] = [_l for _l in str(value).splitlines()]
            _overlap_count = 0
            _max_overlap = min(len(_cur_notes), len(_new_notes))
            for _i in range(1, _max_overlap + 1):
                _a_val = _cur_notes[-_i].strip().lower() # last to first
                _b_val = _new_notes[_i-1].strip().lower() # first to last
                if _a_val == _b_val:
                    overlap_count += 1
                else:
                    break  # stop at the first mismatch
            if _overlap_count >= 1:
                _to_add = _new_notes[_overlap_count:]
                _cur_notes.extend(_to_add)
            _new_text = '\n'.join(_cur_notes) + '\n\n'
            _new_text += '\n '.join(_lines[min(_stream_start_ids):])
            self._modified_text = _new_text

            #if _overlap_count >= 1:
            #    _to_add = _new_notes[_overlap_count:]
            #else:
            #    _to_add = _new_notes
            #_cur_notes.extend(_to_add)
            #_new_lines = _cur_notes + _line[min(_stream_start_ids):]
            #self._modified_text = '\n'.join([_l for _l in _new_lines])
    
    #------- Public Methods -------#
    
    @ToolBox_Decorator
    def clear_all_stream_notes (self) :
        _lines = str(self._modified_text).splitlines()
        _stream_start_ids:list[int] = []
        for _line_id, _line in enumerate(_lines):
            if "SCHEDULE" in str(_line).strip()[0:9]:
                _stream_start_ids.append(_line_id)
        self._modified_text = '\n'.join(_line[min(_stream_start_ids):])

    @ToolBox_Decorator
    def get_current_text(self) -> str:
        """Returns the current Job Stream text including sub job definitions."""
        self._update_follows_in_modified_text()
        _textHolder = self._modified_text + '\n'
        _textHolder += "\n\n\n".join([_job.get_current_text() for _job in self._job_collection])
        _textHolder += ("\n\n") 
        _textHolder += self._modified_end_text
        _textHolder += ("\n\n")
        return _textHolder

    @ToolBox_Decorator
    def add_job_by_text (self, definition_text:str, sourceFile:str=None, initial_data:dict[str,Any]=None) :
        """adds a job to the end of the stream based off the given definition text."""
        _new_jobObject = ToolBox_IWS_Job_Obj(
            definition_text = definition_text,
            sourceFile = sourceFile,
            parent_path = self.full_path,
            initial_data = initial_data
        )
        if all([_new_jobObject.full_path != _j.full_path for _j in self._job_collection]):
            self._job_collection.append(_new_jobObject)
        return self
    
    @ToolBox_Decorator
    def get_Job_by_name (self, name:str):
        """Returns the target Job by Name if found, returns None if none can be found."""
        for _job in self._job_collection:
            if (name.upper() in _job.full_path.upper()):
                return _job
        return None
    
    @ToolBox_Decorator
    def search_replace_text (self, searchString:str, replaceString:str, updated_source:bool=False) :
        if (searchString in self._modified_text):
            self.log.debug(f"Replaceing text in '{self.full_path}' from '{searchString}' to '{replaceString}'")
            self._modified_text = re.sub(searchString, replaceString, self._modified_text, flags=re.IGNORECASE)
            if updated_source == True:
                self._source_text = re.sub(searchString, replaceString, self._source_text, flags=re.IGNORECASE)
            self._reset_values_from_modified_text()
        return self

    @ToolBox_Decorator
    def get_resources (self) -> list[str]:
        """Returns a list of Resource used by this Job Stream"""
        _results = []
        _pattern = re.compile(r"^(?=.{0,7}\bneeds\b).*?(\S+\s+){2}(\S+)", re.IGNORECASE | re.MULTILINE)
        for _match in _pattern.finditer(self._modified_text):
            _resource_path = _match.group(2) 
            _results.append(_resource_path)
        return _results
    
    @ToolBox_Decorator
    def set_ON_REQUEST(self, value:bool):
        """Adds or Removes the 'ON REQUEST' line from the stream definition."""
        _lines = self._modified_text.splitlines()
        _DESCRIPTION_id = next((_idx for _idx, _line in enumerate(_lines) if 'DESCRIPTION' in _line[0:14]), -1)
        _REQUEST_id = next((_idx for _idx, _line in enumerate(_lines) if 'ON REQUEST' in _line[0:16]), -1)
        if (value == True) and (_REQUEST_id == -1):
            self.log.debug (f"Adding 'ON REQUEST' to Stream : '{self.full_path}'.")
            _lines.insert(_DESCRIPTION_id+1, 'ON REQUEST')
        elif (value == True) and (_REQUEST_id != -1):
            self.log.debug (f"Stream : '{self.full_path}' is already 'ON REQUEST'.")
        if (value == False) and (_REQUEST_id != -1):
            self.log.debug (f"Removing 'ON REQUEST' from Stream : '{self.full_path}'.")
            _lines.pop(_REQUEST_id)
        self._modified_text = "\n".join(_lines)
        return self
    
    @ToolBox_Decorator
    def set_DRAFT (self, value:bool):
        """Adds or Removes the 'DRAFT' line from the stream definition."""
        _lines = self._modified_text.splitlines()
        _DESCRIPTION_id = next((_idx for _idx, _line in enumerate(_lines) if 'DESCRIPTION' in _line[0:14]), -1)
        _REQUEST_id = next((_idx for _idx, _line in enumerate(_lines) if 'ON REQUEST' in _line[0:16]), -1)
        _DRAFT_id = next((_idx for _idx, _line in enumerate(_lines) if 'DRAFT' in _line), -1)
        print (_DESCRIPTION_id, _REQUEST_id, _DRAFT_id)
        if (_DRAFT_id != -1) and (value == True):
            self.log.debug (f"Stream : '{self.full_path}' is already set to DRAFT.")
        elif (_DRAFT_id != -1) and (value == False):
            self.log.debug (f"Removing 'DRAFT' from Stream : '{self.full_path}'.")
            _lines.pop(_DRAFT_id)
        elif (_DRAFT_id == -1) and (value == True):
            self.log.debug (f"Adding 'DRAFT' to Stream : '{self.full_path}'.")
            _index = max([_DESCRIPTION_id, _REQUEST_id])
            _lines.insert(_index+1, 'DRAFT')
        self._modified_text = "\n".join(_lines)
        return self
    
    @ToolBox_Decorator
    def set_all_Jobs_NOP (self, value:bool):
        """Sets the state of 'On Request' for all Job Streams in this file."""
        for _job in self._job_collection:
            _job.set_NOP(value)
        return self