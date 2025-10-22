#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, re
from datetime import datetime
from collections import UserDict
from typing import Any
from ToolBox_V2.ToolBox_logger import OutputLogger
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_Follows_Obj import ToolBox_IWS_Follows_Obj, ToolBox_IWS_Join_Obj
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

class ToolBox_IWS_Job_Obj (UserDict):
    """Data Class representing and handing IWS Job Stream actions"""
    log:OutputLogger = OutputLogger().get_instance()
    _source_file:str = None
    _source_text:str = None
    _modified_text:str = None
    _parent_path:str = None
    _defined_path:str = None
    _name:str = None
    _alias:str = None
    _workstation:str = None
    _folder:str = None    

    _follows_collection:list[ToolBox_IWS_Follows_Obj | ToolBox_IWS_Join_Obj] = []

    def __init__(self, definition_text:str, sourceFile:str=None, parent_path:str=None, initial_data:dict[str,Any]=None):
        super().__init__(initial_data)
        self._source_file = sourceFile
        self._source_text = definition_text
        self._modified_text = self._source_text
        self._parent_path = parent_path
        self._follows_collection = []
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
        """collects instal values form teh current state of teh job stream definition text."""
        _job_start_ids:list[int] = []
        _lines = self._modified_text.splitlines()
        for _line_id, _line in enumerate(_lines):
            if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) :
                _job_start_ids.append(_line_id)
        for _i in range(len(_job_start_ids)):
            _line = _lines[_job_start_ids[_i]]
            self._jobPath = _line.strip().split(' ')[0]
            _j_parts = self._jobPath.split('/')
            self._workstation = _j_parts.pop(0)
            self._name = _j_parts.pop(-1)
            self._folder = f"/{'/'.join(_j_parts)}/"
            _alias_index = _line.find(" AS ")
            self._alias = _line[_alias_index+3:].strip().split(' ')[0] if _alias_index != -1 else None
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
        """Collects dependancies from the current state of the Job Modified text."""
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
                _cleaned_lines = [_line.strip() for _idx, _line in enumerate(_lines) if _idx not in _remove_list]
                _follows_text = [_f_obj.get_current_text() for _f_obj in self._follows_collection]
                for _i, _new_line in enumerate(_follows_text):
                    _cleaned_lines.insert(_prev_id + _i,_new_line)
                _new_text = '\n'.join([_l.strip() for _l in _cleaned_lines])
                self._modified_text = _new_text

    #------- properties -------#

    @property
    def workstaion (self) -> str:
        """Returns assigned Job Stream Name as stored in IWS."""
        return self._workstation
    
    @workstaion.setter
    def workstaion (self, value:str) :
        """Sets the value of the assigned Workstaion."""
        self._workstation = value

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
        """Returns assigned Job Name as stored in IWS."""
        return self._name
    
    @name.setter
    def name (self, value:str) :
        """Sets the value of the Job Name."""
        self._name = value

    @property
    def alias (self) -> str:
        """Returns assigned Job Stream as stored in IWS."""
        return self._alias
    
    @alias.setter
    def alias (self, value:str|None) :
        """Sets the value of the Job Alias."""
        self._alias = value
    
    @property
    def parent_path (self) -> str:
        """Returns assigned Job Stream Parent Path as stored in IWS."""
        return self._parent_path

    @parent_path.setter
    def parent_path (self, path:str):
        """Sets the Parent Path"""
        if (path is not None or path.strip() != '') and (self._parent_path.upper() != path.upper()):
            self._parent_path = path

    @property
    def full_path (self) -> str:
        """Returns the full path of the Job as shown in IWS when viewed in a schedule.
        If the Job Alias has been set, the Alias will be used in place of the Name.
        format: {workstation}/{folderPath}/{jobStreamName}.{jobName}
        """
        _ouput = None
        if (self.parent_path is None):
            _ouput = f"{self._workstation}{self._folder}{self._name}"
        else:
            _js_parts = list(self.parent_path.split('/'))
            _js_ws = _js_parts.pop(0)
            _js_name = _js_parts.pop(-1).replace('.@','').strip()
            _js_folder = '/'.join(_js_parts)
            _j_name = self._name if (self._alias is None) or (self._alias.strip() == '') else self._alias
            if (_js_ws.upper() in self._workstation.upper()) and (_js_folder.upper() in self._folder.upper()):
                _ouput = f"{_js_ws}/{_js_folder}/{_js_name}.{_j_name}"
            else:
                _ouput = f"{self._workstation}{self._folder}{_j_name}"
        return _ouput
    
    @property
    def follows_list (self) -> list[ToolBox_IWS_Follows_Obj|ToolBox_IWS_Join_Obj]:
        """Returns the list of follows and join objects found in this Job"""
        return self._follows_collection
    
    @property
    def DOCOMMAND(self) -> str:
        """Returns assigned Target Job Stream or Job Path this dependency is looking for."""
        _pattern = r"^.*?DOCOMMAND(.*)$"
        _match = re.search(_pattern, self._modified_text, re.MULTILINE|re.IGNORECASE)
        if _match:
            return _match.group(1)
        return None
    
    @DOCOMMAND.setter
    def DOCOMMAND(self, value:str):
        """Sets the DOCOMMAND quoted value in the Job text."""
        _pattern = re.compile(r'(DOCOMMAND\s+)("(?:(?:\\.|[^"\\])*)")', re.IGNORECASE | re.MULTILINE)
        _replace = value.replace('"','\\"')
        # Use a lambda so replace_value is inserted literally
        self._modified_text = _pattern.sub(lambda m: m.group(1) + rf'"{_replace}"', self._modified_text)
    
    @property
    def notes (self) -> str:
        _lines = str(self._modified_text).splitlines()
        _note_line_ids:list[int] = []
        _job_start_ids:list[int] = []
        for _line_id, _line in enumerate(_lines):
            if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) :
                _job_start_ids.append(_line_id)
            if '#' in str(_line).strip()[0:4]:
                _note_line_ids.append(_line_id)
        _holder = []
        for _id_index in range(len(_job_start_ids)):
            for _id in range(len(_note_line_ids)):
                if _note_line_ids[_id] < _job_start_ids[_id_index]:
                    _holder.append(_lines[_note_line_ids[_id]])
        if len(_holder) >= 1:
            return '\n'.join (_holder)
        else:
            return None
    
    @notes.setter
    def notes (self, value:str) :
        """Sets or adds notes to end of current notes found above Job definition"""
        _lines = str(self._modified_text).splitlines()
        _job_start_ids:list[int] = []
        for _line_id, _line in enumerate(_lines):
            if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) :
                _job_start_ids.append(_line_id)
        if (self.notes is None) or (self.notes.strip() == ''):
            _holder = [f'{line}\n' for line in value.splitlines() if line.strip() != '']
            _holder.extend(_lines)
            self._modified_text = '\n'.join(_holder)
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
            _new_text += '\n'.join([_l.strip() for _l in _lines[min(_job_start_ids):]])
            self._modified_text = _new_text
            #_new_lines = _cur_notes + [f" {_l}" for _l in _lines[min(_job_start_ids):]]
            #self._modified_text = '\n'.join([_l for _l in _new_lines])

            
    #------- Public Methods -------#

    @ToolBox_Decorator
    def clear_all_stream_notes (self) :
        _lines = str(self._modified_text).splitlines()
        _job_start_ids:list[int] = []
        for _line_id, _line in enumerate(_lines):
            if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) :
                _job_start_ids.append(_line_id)
        self._modified_text = '\n'.join(_line[min(_job_start_ids):])
    
    @ToolBox_Decorator
    def get_current_text(self) -> str:
        """Returns the current text of this Job."""
        self._update_follows_in_modified_text()
        _new_lines = []
        _job_start_id = -1
        for _line_idx, _line in enumerate(self._modified_text.splitlines()):
            if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) :
                _job_start_id = _line_idx
            _new_lines.append(f"{_line.strip()}")
        for _new_line_idx, _line in enumerate(_new_lines):
            if _new_line_idx > _job_start_id and (_line[0] != ' '):
                _new_lines[_new_line_idx] = f" {_line}"
        return '\n'.join(_new_lines)

    @ToolBox_Decorator
    def reset_modfied_text (self):
        if self._modified_text != self._source_text:
            self._modified_text = self._source_text
        return self
    
    @ToolBox_Decorator
    def search_replace_text (self, searchString:str, replaceString:str, updated_source:bool=False) :
        if (searchString in self._modified_text):
            self.log.debug(f"Replaceing text in '{self._jobPath}' from '{searchString}' to '{replaceString}'")
            self._modified_text = re.sub(searchString, replaceString, self._modified_text, flags=re.IGNORECASE)
            if updated_source == True:
                self._source_text = re.sub(searchString, replaceString, self._source_text, flags=re.IGNORECASE)
            self._reset_values_from_modified_text()
        return self
    
    @ToolBox_Decorator
    def get_resources (self) -> list[str]:
        """Returns a list of Resource used by this Job"""
        _results = []
        _pattern = re.compile(r"^(?=.{0,7}\bneeds\b).*?(\S+\s+){2}(\S+)", re.IGNORECASE | re.MULTILINE)
        for _match in _pattern.finditer(self._modified_text):
            _resource_path = _match.group(2) 
            _results.append(_resource_path)
        return _results
    
    @ToolBox_Decorator
    def set_NOP (self, value:bool=True):
        """Adds or Removes the 'NOP' line from the Job definition."""
        _lines = self._modified_text.splitlines()
        _RECOVERY_id = next((_idx for _idx, _line in enumerate(_lines) if 'RECOVERY' in _line[0:10]), -1)
        _NOP_id = next((_idx for _idx, _line in enumerate(_lines) if 'NOP' in _line[0:6]), -1)
        if (_NOP_id != -1) and (value == True):
            self.log.debug (f"Job : '{self._jobPath}' is already set to NOP")
        elif (_NOP_id != -1) and (value == False):
            self.log.debug (f"Removing 'NOP' from Job : '{self._jobPath}'")
            _lines.pop(_NOP_id)
        elif (_NOP_id == -1) and (value == True):
            self.log.debug (f"Adding 'NOP' to job : '{self._jobPath}'")
            _lines.insert(_RECOVERY_id+1, 'ON REQUEST')
        self._modified_text = "\n".join(_lines)
        return self