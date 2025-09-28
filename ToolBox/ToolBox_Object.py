#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, re, copy, uuid
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


class ToolBox_FileData (UserDict):
    _id:str = None
    _logger:OutputLogger = OutputLogger().get_instance()
    _sourceFile:str = None
    _rootPath:str = None
    _relPath:str = None
    _fileName:str = None
    _rawLines:list[str] = []
    _modLines:list[str] = []
    _idCollections:dict[str,list[int]] = {}
    
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
        self._idCollections = {}
        

    def __setitem__(self, key, value):
        # take custom action when setting a keyword, if keyword is X do Y then add to data
        if isinstance(value, str):
            self.data[key] = value
        else:
            self.data[key] = value
    

    def __getitem__(self, key):
        if isinstance(key, str):
            key = key
        if key in self._idCollections.keys():
            return self._idCollections[key]
        return self.data[key] 
    

    @ToolBox_Decorator
    def openFile (self):
        if (len(self._rawLines) == 0):
            _holder = None
            with open(self._sourceFile, "r") as f:
                _holder = copy.deepcopy(f.read()).split('\n')
            if (_holder != None):
                #clean lines and remove retuirns and next line charecters
                self._rawLines = [s.replace('\n', '').replace('\r', '') for s in _holder]
            self.reset_mod_lines()
            self.update_mod_lineIDs()
        return self

    @ToolBox_Decorator
    def closeFile (self):
        del self._rawLines
        self._rawLines = []
        del self._modLines
        self._modLines = []
        del self._idCollections
        self._idCollections = {}
        self.init_default_collections()

    @ToolBox_Decorator
    def reset_mod_lines (self) :
        self._modLines = copy.deepcopy(self._rawLines)
        self.update_mod_lineIDs()
        return self

    @ToolBox_Decorator
    def list_collectionNames (self) -> list[str]:
        """Returns the list of avalible collection names, this does not include user defiend data or keys"""
        return [_k for _k in self._idCollections.keys()]
    
    @ToolBox_Decorator
    def add_collection (self, name:str, initialList:list[Any]=None) :
        """Add a named list[] used to store a collections of refrences or values"""
        if name not in self._idCollections.keys():
            self._idCollections[name] = [] if initialList is None else initialList

    @ToolBox_Decorator
    def get_collection_by_Name (self, name:str) ->list[int]|list[Any] :
        """returns the collection if found."""
        if name not in self._idCollections.keys():
            return self._idCollections[name]

    @ToolBox_Decorator
    def reset_collection_by_name (self, name:str, auto_Create:bool=False) :
        """Resets the named collection to a blank list if found."""
        if name in self._idCollections.keys():
            self._idCollections[name] = []
        if auto_Create == True:
            self.add_collection(name)

    @ToolBox_Decorator
    def reset_default_collections (self):
        """Resets teh default lists of connections, user defiend collections will remain unaffected."""
        self.init_default_collections()

    @ToolBox_Decorator
    def init_default_collections (self):
        default_collection_list:list[str] = [
            '_STREAM_START_ids',
            '_STREAM_EDGE_ids',
            '_STREAM_END_ids',
            '_JOB_START_ids',
            '_DOCOMMAND_ids',
            '_RUNCYCLE_ids',
            '_EXCEPT_ids',
            '_STREAMLOGON_ids',
            '_DESCRIPTION_ids',
            '_DRAFT_ids',
            '_REQUEST_ids',
            '_FOLLOWS_ids',
            '_TASKTYPE_ids',
            '_OUTPUTCOND_ids',
            '_RECOVERY_ids',
            '_NOP_ids',
            '_NEEDS_ids'
        ]
        for _name in default_collection_list:
            self.reset_collection_by_name(_name, auto_Create=True)
                

    @ToolBox_Decorator
    def update_mod_lineIDs (self):
        #find way to convers id list to dynicly names colelction by keyword and pre-difiend filter/labmda action
        self.reset_default_collections()
        for _line_id, _line in enumerate(self._modLines):
            if "SCHEDULE" in str(_line).strip()[0:9]:
                self._idCollections['_STREAM_START_ids'].append(_line_id)
            if 'DRAFT' in _line:
                self._idCollections['_DRAFT_ids'].append(_line_id)
            if 'REQUEST' in _line[0:20].upper():
                self._idCollections['_REQUEST_ids'].append(_line_id)
            if ':' in _line[0:2]:
                self._idCollections['_STREAM_EDGE_ids'].append(_line_id)
            if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) :#or (any(_s in str(_line).strip()[0:5] for _s in ['PRD#', 'NPR#'])) and ('#' in str(_line[2:]).strip()):
                self._idCollections['_JOB_START_ids'].append(_line_id)
            if 'DESCRIPTION' in _line:
                self._idCollections['_DESCRIPTION_ids'].append(_line_id)
            if 'RUNCYCLE' in _line:
                self._idCollections['_RUNCYCLE_ids'].append(_line_id)
            if 'FOLLOWS' in _line:
                self._idCollections['_FOLLOWS_ids'].append(_line_id)
            if 'EXCEPT' in _line:
                self._idCollections['_EXCEPT_ids'].append(_line_id)
            if 'DOCOMMAND' in _line:
                self._idCollections['_DOCOMMAND_ids'].append(_line_id)
            if 'STREAMLOGON' in _line:
                self._idCollections['_STREAMLOGON_ids'].append(_line_id)
            if 'OUTPUTCOND' in _line:
                self._idCollections['_OUTPUTCOND_ids'].append(_line_id)
            if 'TASKTYPE' in _line:
                self._idCollections['_TASKTYPE_ids'].append(_line_id)
            if 'RECOVERY' in _line:
                self._idCollections['_RECOVERY_ids'].append(_line_id)
            if 'NOP' in _line:
                self._idCollections['_NOP_ids'].append(_line_id)   
            if 'NEEDS' in _line[0:8]:
                self._idCollections['_NEEDS_ids'].append(_line_id)
            if "END" in str(_line).strip()[0:4] and 'ENDJOIN' not in str(_line).strip():
                self._idCollections['_STREAM_END_ids'].append(_line_id)
        return self

    
    @property
    def id (self) -> str:
        """Returns randomly generated ID value."""
        return self._id
    
    @property
    def text_raw (self) -> str:
        """Returns the raw text from the source file un-edited."""
        return str(' \n'.join(self._rawLines))
    
    @property
    def text_modified (self) -> str:
        """Returns the modified text after modifications have been made."""
        return str(' \n'.join(self._modLines))
    
    @property
    def has_changed (self) -> bool:
        """Returns a true falce value if the modified value is diffrent from the orriginal contents of the files when opened."""
        is_same = True
        if (len(self._rawLines) != len(self._modLines)):
            is_same = False
        else:
            for _i in range(len(self._rawLines)):
                if self._rawLines[_i] != self._modLines[_i]:
                    is_same = False
                    break
        return is_same

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
        self._logger.debug(f"Number of Job Streams : [{len(self._idCollections['_STREAM_START_ids'])}]")
        self._logger.debug(f"Number of Jobs : [{len(self._idCollections['_JOB_START_ids'])}]")
        return self
    
    @ToolBox_Decorator
    def search_for_terms (self, searchTerms:list[str]) -> dict[int, list[str]] :
        _found_lineID_terms:dict[int, list[str]] = {}
        for _line_id, _line in enumerate(self._modLines):
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
    def search_replace_terms (self, searchReplaceTerms:dict[str,str]) -> bool:
        """Searches for a substring and replaces it with a given substring in file.  Returns True of change was made, false if no change was made."""    
        _changed = False
        for _line_id, _line in enumerate(self._modLines):
            for _search, _replace in searchReplaceTerms.items():
                if _search.lower() in _line.lower():
                    _newline, _changes = re.subn(_search, _replace, _line, flags=re.IGNORECASE)
                    if _changes >= 1:
                        _changed = True
                        self._modLines[_line_id] = _newline
                        self._logger.debug (f"Found term '{_search}' and reaplced with '{_replace}' on line [{_line_id}] in file '{os.path.join(self.sourceFileDirRelPath, self.sourceFileName)}'")
        
        return _changed
    
    @ToolBox_Decorator
    def saveTo (self, outputfolder:str, rename:str=None, useRelPath:bool=False) -> str:
        #needs to be reworked, not saving some files in the correct path.
        _outputPath = os.path.join(outputfolder,self._relPath) if useRelPath == False else outputfolder
        os.makedirs(_outputPath, exist_ok=True)
        _filename = rename if rename != None else self._fileName
        _outputFilePath = os.path.join (_outputPath, _filename)
        if os.path.exists (_outputFilePath):
            os.remove(_outputFilePath)
        with open(_outputFilePath, "w") as output_file:
            output_file.write(self.text_modified)
        return _outputFilePath
    

    @ToolBox_Decorator
    def insert_Moddified_Line (self, index:int, lines_to_add:list[str]):
        _insert_id = index
        for _line in lines_to_add:
            _insert_id += 1
            self._modLines.insert(int(_insert_id), _line)
        self.update_mod_lineIDs()

    @ToolBox_Decorator
    def remove_Line_at (self, index:int, count:int):
        if len(self._modLines) >= (index + count):
            del self._modLines[index: index + count]
        self.update_mod_lineIDs()


    @ToolBox_Decorator
    def get_consecutive_int_from_list_at (self, index:int, targetList:list[int], valueClampStart:int=None, valueClampStop:int=None) -> list[int]:
        if index < 0 or index >= len(targetList):
            return []
        start = index
        end = index
        # expand backwards
        while start > 0 and targetList[start] - targetList[start - 1] == 1:
            start -= 1
        # expand forwards
        while end < len(targetList) - 1 and targetList[end + 1] - targetList[end] == 1:
            end += 1
        _results = targetList[start:end+1]
        # returns calmpped values if provided
        if (valueClampStart is not None) and (valueClampStop is not None):
            _results = [x for x in _results if valueClampStart <= x <= valueClampStop]
        return _results
    

    @ToolBox_Decorator
    def set_Streams_ONREQUEST (self, value:bool=True, filter_worksataiton:list[str]=None, filter_folder:list[str]=None, filer_streamName:list[str]=None, remove_RUNCYCLE_lines:bool = False):
        for _stream_id in range(len(self._idCollections['_STREAM_START_ids'])):
            _stream_start = self._idCollections['_STREAM_START_ids'][_stream_id]
            _stream_edge = self._idCollections['_STREAM_EDGE_ids'][_stream_id]
            _skip:bool = False
            _criteria = {}
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
            if _skip == True:                 
                self._logger.debug (f"Skipping stream : '{str(self._modLines[_stream_start].split(' ')[1])}', does not match search criteria : ")
                continue
            if (len(self._idCollections['_REQUEST_ids']) >= 1):
                # if settign value to true, and ON REQUEST is already set, skip changes.
                _has_onrequest = False
                for _req_id in self._idCollections['_REQUEST_ids']:
                    if (_stream_start <= _req_id <= _stream_edge):
                        _has_onrequest = True
                        _target_name = str(self._modLines[_stream_start].split(' ')[1])
                        self._logger.debug (f"Stream : '{_target_name}' is already ON REQUEST")
                if (_has_onrequest == True) and (value == True): 
                    _skip = True
                elif (_has_onrequest == True) and (value == False): 
                    _skip = False
            if _skip == True: continue
            if (value == True):
                # add onrequest if missing
                _target_line = _stream_start
                _target_name = str(self._modLines[_stream_start].split(' ')[1])
                for _desc in self._idCollections['_DESCRIPTION_ids']:
                    if (_stream_start < _desc < _stream_edge) and _desc > _target_line:
                        _target_line = _desc
                self.insert_Moddified_Line(int(_target_line), ['ON REQUEST'])
                self._logger.debug (f"Added 'ON REQUEST' to stream : '{_target_name}'")
                if (remove_RUNCYCLE_lines == True):                   
                    _rc_ids = [_id for _id in self._idCollections['_RUNCYCLE_ids'] if _stream_start <= _id <= _stream_edge]
                    self.remove_Line_at(min(_rc_ids),len(_rc_ids))
                    self._logger.debug (f"Removed 'ON RUNCYCLE ...' lines from stream : '{_target_name}'")
            else:
                # if value is 'False' remove 'ON REQUEST' if found.
                _request_ids = [_id for _id in self._idCollections['_REQUEST_ids'] if _stream_start <= _id <= _stream_edge]
                self.remove_Line_at(min(_request_ids),len(_request_ids))
                self._logger.debug (f"Removed 'ON REQUEST' from stream : '{_target_name}'")
                
        return self
    


    @ToolBox_Decorator
    def set_Streams_DRAFT (self, value:bool=True, filter_worksataiton:list[str]=None, filter_folder:list[str]=None, filer_streamName:list[str]=None):
        for _stream_id in range(len(self._idCollections['_STREAM_START_ids'])):
            _stream_start = self._idCollections['_STREAM_START_ids'][_stream_id]
            _stream_edge = self._idCollections['_STREAM_EDGE_ids'][_stream_id]
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
            if _skip == True:                 
                self._logger.debug (f"Skipping stream : '{str(self._modLines[_stream_start].split(' ')[1])}', does not match search criteria : ")
                continue
            _has_draft = False
            if (len(self._idCollections['_DRAFT_ids']) >= 1):
                for _draft_id in self._idCollections['_DRAFT_ids']:
                    if _stream_start < _draft_id < _stream_edge :
                        _has_draft = True
                if (_has_draft == True) and (value == True): 
                    _skip = True
                elif (_has_draft == True) and (value == False): 
                    _skip = False
            if _skip == True: continue
            _target_name = str(self._modLines[_stream_start].split(' ')[1])
            if (value == True):
                #add draft is missing
                _desc_ids = [_id for _id in self._idCollections['_DESCRIPTION_ids'] if _stream_start <= _id <= _stream_edge]
                _req_ids = [_id for _id in self._idCollections['_REQUEST_ids'] if _stream_start <= _id <= _stream_edge]
                _target = max(list(set(_desc_ids + _req_ids)))
                self.insert_Moddified_Line(int(_target), ['DRAFT'])
                self._logger.debug (f"Added 'DRAFT' to stream : '{_target_name}'")
            elif (_has_draft == True) and (value == False):
                _draft_ids = [_id for _id in self._idCollections['_DRAFT_ids'] if _stream_start <= _id <= _stream_edge]
                self.remove_Line_at(min(_draft_ids),len(_draft_ids))
                self._logger.debug (f"Removed 'DRAFT' from stream : '{_target_name}'")
        return self
    

    @ToolBox_Decorator
    def set_Jobs_NOP (self, value:bool=True, filter_worksataiton:list[str]=None, filter_folder:list[str]=None, filer_streamName:list[str]=None, filter_jobNames:list[str]=None):
        for _stream_id in range(len(self._idCollections['_STREAM_START_ids'])):
            _stream_start = self._idCollections['_STREAM_START_ids'][_stream_id]
            _stream_end = self._idCollections['_STREAM_END_ids'][_stream_id]+1
            _skip:bool = False
            _job_ids = [_id for _id in self._idCollections['_JOB_START_ids'] if _stream_start < _id < _stream_end]
            _lines_toRemove:dict[str,list[int]] = {}
            for _i in range(len([_id for _id in self._idCollections['_JOB_START_ids'] if _stream_start < _id < _stream_end])):
                _job_line_start = _job_ids[_i]
                _job_line_stop = int(_job_ids[_i+1])-1 if _i < (len(_job_ids)-1) else int(_stream_end -1)
                if (filter_worksataiton != None) and (len(filter_worksataiton) >= 1) :
                    for _ws_term in filter_worksataiton:
                        if (_ws_term.upper() not in self._modLines[_job_line_start].upper()):
                            _skip = True
                if (filter_folder != None) and (len(filter_folder) >= 1) :

                    for _fl_term in filter_folder:
                        if (_fl_term.upper() not in self._modLines[_job_line_start].upper()):
                            _skip = True
                if (filer_streamName != None) and (len(filer_streamName) >= 1) :

                    for _name_term in filer_streamName:
                        if (_name_term.upper() not in self._modLines[_job_line_start].upper()):
                            _skip = True
                if _skip == True:                 
                    self._logger.debug (f"Skipping job : '{str(self._modLines[_job_line_start].split(' ')[1])}', does not match search criteria : ")
                    continue
                _has_nop = False
                if (len(self._idCollections['_NOP_ids']) >= 1):
                    for _nop_id in self._idCollections['_NOP_ids']:
                        if _job_line_start < _nop_id < _job_line_stop :
                            _has_nop = True
                    if (_has_nop == True) and (value == True): 
                        _skip = True
                    elif (_has_nop == True) and (value == False): 
                        _skip = False
                
                if _skip == True: continue
                
                _target_name = f"{self._modLines[_stream_start].split(' ')[1]}.{self._modLines[_job_line_start].strip().split('/')[-1]}"
                if (value == True):
                    _rec_ids = [_rec_idx for _rec_idx in self._idCollections['_RECOVERY_ids'] if _job_line_start < _rec_idx < _job_line_stop]
                    self.insert_Moddified_Line(int(max(_rec_ids)-1), ' NOP')
                    self._logger.debug (f"Added 'NOP' to job : '{_target_name}'")
                elif (_has_nop == True) and (value == False):    
                    _nop_ids = [_nop_idx for _nop_idx in self._idCollections['_NOP_ids'] if _job_line_start < _nop_idx < _job_line_stop]
                    _lines_toRemove[_target_name] = _nop_ids

            if len(_lines_toRemove.keys()) >= 1:
                _remove_target_order = sorted(_lines_toRemove.keys(), key=lambda k: _lines_toRemove[k][0], reverse=True)
                for _targetName in _remove_target_order:
                    self.remove_Line_at(min(_lines_toRemove[_targetName]),len(_lines_toRemove[_targetName]))
                    self._logger.debug (f"Removed 'NOP' from job : '{_targetName}'")
        return self
    
    @ToolBox_Decorator
    def copy_Streams_By_Workstation (self, sourceWorkstation:str, targetWorkstation:str) -> bool:
        self.update_mod_lineIDs()
        _found_source_items : list[dict[str,int|str]] = []
        _found_target_items : list[dict[str,int|str]] = []
        for _stream_id in range(len(self._idCollections['_STREAM_START_ids'])):
            _stream_start = self._idCollections['_STREAM_START_ids'][_stream_id]
            _stream_end = self._idCollections['_STREAM_END_ids'][_stream_id]+1
            if (sourceWorkstation.upper() in self._modLines[_stream_start].upper()):
                _found_source = {
                    "start" : _stream_start,
                    "stop" : _stream_end,
                    "name" : self._modLines[_stream_start].split(' ')[1]
                }
                if _found_source not in _found_source_items:
                    _found_source_items.append(_found_source)
            if (targetWorkstation.upper() in self._modLines[_stream_start].upper()):
                _found_target = {
                    "start" : _stream_start,
                    "stop" : _stream_end,
                    "name" : self._modLines[_stream_start].split(' ')[1]
                }
                if _found_target not in _found_target_items:
                    _found_target_items.append(_found_target)
        _has_changed = False
        for _found_item in _found_source_items:
            _source_stream_name = str(_found_item['name']).strip().split('/')[-1]
            _already_exists = False
            for _target_item in _found_target_items:
                _target_stream_name = str(_target_item['name'])
                if (targetWorkstation.upper() in _target_stream_name) and (_source_stream_name.upper() in _target_stream_name):
                    _already_exists = True
            if _already_exists == True:
                continue
            self._logger.debug(f"Duplicating Stream '{_found_item['name']}' replacing all Workstation references '{sourceWorkstation}' with: '{targetWorkstation}'")  
            _duplicate_lines = copy.deepcopy(self._modLines[_found_item['start']:_found_item['stop']])
            for _i in range(len(_duplicate_lines)):
                _duplicate_lines[_i] = _duplicate_lines[_i].replace(sourceWorkstation, targetWorkstation)
            _duplicate_lines.insert(0,'')
            self._modLines.extend(_duplicate_lines)
            _has_changed = True
        self.update_mod_lineIDs()
        return _has_changed
    
    @ToolBox_Decorator
    def get_NEEDS_reference (self) ->list[str]:
        """Returns the list of named NEEDS resources found in file."""
        self.update_mod_lineIDs()
        _found_needs:list[str] = []
        for _i in range(len(self._idCollections['_NEEDS_ids'])):
            _needs_line = self._modLines[self._idCollections['_NEEDS_ids'][_i]]
            _needs_name = _needs_line.split(' ')[2].split('/')[-1]
            if (_needs_name not in _found_needs):
                _found_needs.append(_needs_name)
        return _found_needs
    
    @ToolBox_Decorator
    def get_RCG_reference (self) ->list[str]:
        """Returns the list of named RCG resources found in file."""
        self.update_mod_lineIDs()
        _found_needs:list[str] = []
        for _i in range(len(self._idCollections['_RUNCYCLE_ids'])):
            _line = self._modLines[self._idCollections['_RUNCYCLE_ids'][_i]]
            _parts = _line.split(' ')
            for _idx, elem in enumerate(_parts):
                if ('$RCG' in elem) and (_idx + 1 < len(_parts)):
                    _rcgName = _parts[_idx+1].split('/')[-1]
                    if _rcgName not in _found_needs:
                        _found_needs.append(_rcgName)
        return _found_needs
    
    @ToolBox_Decorator
    def get_Stream_names (self) -> list[str] :
        self.update_mod_lineIDs()
        _names = []
        for _stream_id in range(len(self._idCollections['_STREAM_START_ids'])):
            _stream_start = self._idCollections['_STREAM_START_ids'][_stream_id]
            _streamName = str(self._modLines[_stream_start].split(' ')[1])
            if _streamName not in _names:
                _names.append(_streamName)
        return _names
    
    @ToolBox_Decorator
    def get_Job_names (self) -> list[str] :
        self.update_mod_lineIDs()
        _names = []
        for _stream_id in range(len(self._idCollections['_STREAM_START_ids'])):
            _stream_start = self._idCollections['_STREAM_START_ids'][_stream_id]
            _stream_end = self._idCollections['_STREAM_END_ids'][_stream_id]+1
            _streamName = str(self._modLines[_stream_start].split(' ')[1])
            _job_ids = [_id for _id in self._idCollections['_JOB_START_ids'] if _stream_start< _id < _stream_end]
            for _job_id in _job_ids:
                _job_line = self._modLines[_job_id].split('/')[-1]
                _fullName = f"{_streamName}.{_job_line}"
                if _fullName not in _names:
                    _names.append(_fullName)
        return _names

    @ToolBox_Decorator
    def get_StreamText (self, streamName:str) -> str:
        """Returns the string value of the trarget Stream name in this file"""
        _holder_string = ''
        for _stream_id in range(len(self._idCollections['_STREAM_START_ids'])):
            _stream_start = self._idCollections['_STREAM_START_ids'][_stream_id]
            _stream_end = self._idCollections['_STREAM_END_ids'][_stream_id]+1
            if (streamName.upper() in self._modLines[_stream_id].upper()):
                _holder_string += '\n'.join(self._modLines[_stream_start:_stream_end])
                _holder_string += '\n'
        return _holder_string
    
    @ToolBox_Decorator
    def get_JobText (self, streamName:str, jobName:str) -> str:
        """Returns the string value of the trarget Stream name in this file"""
        _holder_string = ''
        for _stream_id in range(len(self._idCollections['_STREAM_START_ids'])):
            if (streamName.upper() in self._modLines[_stream_id].upper()):
                _stream_start = self._idCollections['_STREAM_START_ids'][_stream_id]
                _stream_end = self._idCollections['_STREAM_END_ids'][_stream_id]+1
                _job_ids = [_id for _id in self._idCollections['_JOB_START_ids'] if _stream_start < _id < _stream_end]
                for _i in range(len([_id for _id in self._idCollections['_JOB_START_ids'] if _stream_start < _id < _stream_end])):
                    _job_line_start = _job_ids[_i]
                    _job_line_stop = int(_job_ids[_i+1])-1 if _i < (len(_job_ids)-1) else int(_stream_end -1)
                    if (jobName.upper() in self._modLines[_job_line_start].upper()):
                        _holder_string += '\n'
                        _holder_string += '\n'.join(self._modLines[_job_line_start:_job_line_stop])
        return _holder_string

    @ToolBox_Decorator
    def add_streamText_to_File (self, text:str) :
        """Add Stream to end of file."""
        _textLines = text.split('\n')
        _textLines.insert(0,'')
        self.openFile()
        self._modLines.extend(_textLines)
        self.update_mod_lineIDs()

    @ToolBox_Decorator
    def add_Job_to_Stream (self, streamName:str, jobText:str):
        """Add Job to end of target Stream in file."""
        self.openFile()
        _textLines = jobText.split('\n')
        for _stream_id in range(len(self._idCollections['_STREAM_START_ids'])):
            if (streamName.upper() in self._modLines[_stream_id].upper()):
                _stream_end = self._idCollections['_STREAM_END_ids'][_stream_id]
                self._modLines[_stream_end:_stream_end] = _textLines
        self.update_mod_lineIDs()
