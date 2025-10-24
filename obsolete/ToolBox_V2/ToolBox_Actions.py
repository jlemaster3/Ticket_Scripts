#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, copy
from ToolBox_V2.ToolBox_logger import OutputLogger
from ToolBox_V2.ToolBox_DataTypes.ToolBox_File_Base import ToolBox_FileData
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_JIL_File import ToolBox_IWS_JIL_File
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_Stream_Obj import ToolBox_IWS_Stream_Obj
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_Job_Obj import ToolBox_IWS_Job_Obj
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_Follows_Obj import ToolBox_IWS_Follows_Obj, ToolBox_IWS_Join_Obj
from typing import Any, Optional, List

#-------------------------------------------------
#   Actions
#-------------------------------------------------

def Action_IWS_JIL_duplicate_streams (file:ToolBox_IWS_JIL_File, sourceFilter:str, targetFilter:str) :
    """Duplicate any source Job Stream within the same file."""
    log = OutputLogger.get_instance()
    file.open_file()
    _source_stream_paths:list[ToolBox_IWS_Stream_Obj] = []
    _target_stream_paths:list[ToolBox_IWS_Stream_Obj] = []
    for _stream in file.job_stream_objects:
        if sourceFilter.upper() in _stream.full_path.upper():
            _source_stream_paths.append(_stream)
        if targetFilter.upper() in _stream.full_path.upper():
            _target_stream_paths.append(_stream)

    for _stream in _source_stream_paths:
        _new_stream = copy.deepcopy (_stream)
        _new_stream.search_replace_text(sourceFilter, targetFilter, quite_logging=True)
        _new_stream._workstaion = targetFilter
        log.debug (f"Duplicated Stream '{_stream.full_path}' and renamed to '{_new_stream.full_path}'")
        if all ([_new_stream.full_path != _js.full_path for _js in file._jobStream_collection]):
            file._jobStream_collection.append(_new_stream)


def Action_IWS_Assets_merge_dependancies_A_B (
    source_A: ToolBox_IWS_Stream_Obj | ToolBox_IWS_Job_Obj,
    source_B: ToolBox_IWS_Stream_Obj | ToolBox_IWS_Job_Obj,
) :
    """Merges all missing dependancies from Source Job Stream or Job over to target Job Stream or Job, maintaining the order found as much as possible."""
    log = OutputLogger.get_instance()
    _set_A:dict[str, ToolBox_IWS_Follows_Obj | ToolBox_IWS_Join_Obj] = {}
    _set_B:dict[str, ToolBox_IWS_Follows_Obj | ToolBox_IWS_Join_Obj] = {}
    for _obj in source_A.follows_list:
        if isinstance(_obj, ToolBox_IWS_Follows_Obj):
            _path = f"{_obj.parent_path}|{_obj.target_path}"
            if (_obj.matching != None) and (_obj.matching.strip() != ''):
                _path += f"|{_obj.matching}"
            if (_obj.condition != None) and (_obj.condition.strip() != ''):
                _path += f"|{_obj.condition}"
        if isinstance(_obj, ToolBox_IWS_Join_Obj):
            _path = f"{_obj.parent_path}|{_obj.name}"
        if (_obj.parent_path == source_A.full_path) and (_path not in _set_A.keys()):
            _set_A[_path] = _obj
    for _obj in source_B.follows_list:
        if isinstance(_obj, ToolBox_IWS_Follows_Obj):
            _path = f"{_obj.parent_path}|{_obj.target_path}"
            if (_obj.matching != None) and (_obj.matching.strip() != ''):
                _path += f"|{_obj.matching}"
            if (_obj.condition != None) and (_obj.condition.strip() != ''):
                _path += f"|{_obj.condition}"
        if isinstance(_obj, ToolBox_IWS_Join_Obj):
            _path = f"{_obj.parent_path}|{_obj.name}"
        if (_obj.parent_path == source_B.full_path) and (_path not in _set_B.keys()):
            _set_B[_path] = _obj
    
    _merged:dict[str, ToolBox_IWS_Follows_Obj | ToolBox_IWS_Join_Obj] = {}
    for _p_b_idx, _path_b in enumerate(_set_B.keys()):
        if _path_b not in _merged.keys():
            _merged[_path_b] = _set_B[_path_b]
            _key = ' '.join(_path_b.split('|')[1:]).replace("'",'"')
            #log.debug (f"Keeping '{_key}'")
        try:
            _idx_a = list(_set_A.keys()).index(_path_b)
        except ValueError:
            _idx_a = None
        if (_idx_a is not None):
            _insert_idx = _idx_a + 1
            while _insert_idx < len(_set_A.keys()):
                _next_key = list(_set_A.keys())[_idx_a + 1]
                if _next_key not in _merged.keys() and _next_key not in _set_B.keys():
                    _merged[_next_key] = copy.deepcopy(_set_A[_next_key])
                    _merged[_next_key].parent_path = source_B.full_path
                    _key = ' '.join(_next_key.split('|')[1:]).replace("'",'"')
                    log.debug (f"Missing dependancy '{_key}' in : '{source_B.full_path}', merging from '{source_A.full_path}'")
                elif _next_key in _path_b:
                    break
                _insert_idx += 1
    for _p_a_idx, _path_a in enumerate(_set_A.keys()):
        if _path_a not in _merged.keys():
            _merged[_path_a] = copy.deepcopy(_set_A[_path_a])
            _merged[_path_a].parent_path = source_B.full_path
            _key = ' '.join(_path_a.split('|')[1:]).replace("'",'"')
            log.debug (f"Missing dependancy '{_key}' in Steam : '{source_B.full_path}', merging from '{source_A.full_path}'")
    if list(_merged.keys()) != _set_B.keys():
        source_B._follows_collection = list(_merged.values())


def Action_IWS_Assets_merge_Notes_A_B (
    source_A: ToolBox_IWS_Stream_Obj | ToolBox_IWS_Job_Obj,
    source_B: ToolBox_IWS_Stream_Obj | ToolBox_IWS_Job_Obj,
) :
    """Merges all missing dependancies from Source Job Stream or Job over to target Job Stream or Job, maintaining the order found as much as possible."""    
    log = OutputLogger.get_instance()
    if (source_A.notes is not None) and (source_B.notes is not None):
        if source_A.notes.lower() != source_B.notes.lower():
            log.debug (f"Found notes in '{source_A.full_path}' that are not in '{source_B.full_path}', merging missing notes")
            source_B.clear_all_stream_notes()
            source_B.notes = source_A.notes
    elif (source_A.notes is not None) and (source_B.notes is None):
        log.debug (f"Found notes in '{source_A.full_path}' that are not in '{source_B.full_path}', merging missing notes")
        source_B.notes = source_A.notes


def Action_IWS_Stream_merge_Jobs_A_B (
    source_Stream_A:ToolBox_IWS_Stream_Obj, 
    source_Stream_B:ToolBox_IWS_Stream_Obj,
    check_dependancies:bool=True
) :
    """Merges all missing jobs from Source Job Stream over to target Job Stream, maintaining the order found as much as possible."""
    log = OutputLogger.get_instance()
    _path_set_A = list(source_Stream_A.job_paths)
    _path_set_B = list(source_Stream_B.job_paths)
    _merged:dict[str, ToolBox_IWS_Job_Obj] = {}
    for _path_b in _path_set_B:
        if _path_b not in _merged.keys():
            _merged[_path_b] = source_Stream_B.get_Job_by_name(_path_b.split('#')[-1])
            #log.debug (f"Keeping '{_merged[_path_b].full_path}'")
        try:
            _idx_a = _path_set_A.index(_path_b)
        except ValueError:
            _idx_a = None
        if (_idx_a is not None):
            _source_A_job = source_Stream_A.get_Job_by_name(_path_set_A[_idx_a].split('#')[-1])
            _source_B_job = _merged[_path_b]
            Action_IWS_Assets_merge_Notes_A_B(_source_A_job, _source_B_job)
            if check_dependancies == True:
                Action_IWS_Assets_merge_dependancies_A_B(_source_A_job, _source_B_job)
            _insert_idx = _idx_a + 1
            while _insert_idx < len(_path_set_A):
                _next_key = _path_set_A[_idx_a + 1]
                if _next_key not in _merged.keys() and _next_key not in _path_set_B:
                    _source_next_job = source_Stream_A.get_Job_by_name(_next_key.split('#')[-1])
                    _merged[_next_key] = copy.deepcopy(_source_next_job)
                    log.debug (f"Missing Job '{_next_key}' in Job Steam : '{source_Stream_B.full_path}', merging Job from '{source_Stream_A.full_path}'")
                elif _next_key in _path_b:
                    break
                _insert_idx += 1
    for _path_a in _path_set_A:
        if _path_a not in _merged.keys():
            _stream_in_A_only = source_Stream_A.get_Job_by_name(_path_a.split('#')[-1])
            if _stream_in_A_only.notes is not None:
                print (_stream_in_A_only.full_path, _stream_in_A_only.notes)
            _merged[_path_a] = copy.deepcopy(_stream_in_A_only)
            log.debug (f"Missing Job '{_path_a}' in Job Steam : '{source_Stream_B.full_path}', merging Job from '{source_Stream_A.full_path}'")
    if list(_merged.values()) != source_Stream_B._job_collection:
        for _job in _merged.values():
            _job._source_file = source_Stream_B._source_file
            _job.parent_path = source_Stream_B.full_path
        source_Stream_B._job_collection = _merged.values()
    


def Action_IWS_JIL_merge_Streams_A_B (
        file_A:ToolBox_IWS_JIL_File, 
        file_B:ToolBox_IWS_JIL_File,
        check_dependancies:bool=True,
        include_jobs:bool = True
    ) :
    """Merges all missing Job Streams found in files, will also check for jobs if include_jobs is 'True', default (True)"""
    log = OutputLogger.get_instance()
    file_A.open_file()
    file_B.open_file()
    _set_A:set[str] = set(file_A.job_stream_paths)
    _set_B:set[str] = set(file_B.job_stream_paths)
    _A_only_streams = _set_A -_set_B
    _matching_streams = _set_A.intersection(_set_B)
    if len(_A_only_streams) >= 1:
        # found only in file , copy stream to file B
        for _streamPath in _A_only_streams:
            log.debug (f"Stream '{_streamPath}' only found in file : '{file_A.relFilePath}', duplicated Stream to file : '{file_B.relFilePath}'")
            _streamCopy = copy.deepcopy(file_A.get_Job_Stream_by_name(_streamPath))
            _streamCopy._source_file = file_B.sourcePath
            if include_jobs != True:
                log.debug(f"Skipping Jobs due to parameter : include_jobs == {include_jobs}")
                _streamCopy._job_collection = []
            file_B._jobStream_collection.append(_streamCopy)
    if (len(_matching_streams) >=1):
        # found in both files, and include merging missing jobs is true, 
        for _streamPath  in _matching_streams:
            _sourceStreamData = file_A.get_Job_Stream_by_name(_streamPath)
            _targetStreamData = file_B.get_Job_Stream_by_name(_streamPath)
            Action_IWS_Assets_merge_Notes_A_B(_sourceStreamData, _targetStreamData)
            if check_dependancies == True:
                Action_IWS_Assets_merge_dependancies_A_B(_sourceStreamData, _targetStreamData)
            if include_jobs == True:
                log.debug (f"Stream '{_streamPath}' is in both '{file_A.relFilePath}' and '{file_B.relFilePath}' reviewing jobs for changes")
                Action_IWS_Stream_merge_Jobs_A_B(_sourceStreamData, _targetStreamData)
            
    elif include_jobs == False:
        log.debug(f"Skipping Jobs due to parameter : include_jobs == {include_jobs}")


def Action_IWS_JIL_sync_streams_A_B (
    file : ToolBox_IWS_JIL_File,
    source_filter:str,
    target_filter:str,
    check_dependancies:bool=True
) :
    """syncs the Jobs between two Job Streams in the same file nased off source and target criteria."""
    log = OutputLogger.get_instance()
    file.open_file()
    _source_paths:list[str] = []
    _target_paths:list[str] = []
    for _path in file.job_stream_paths:
        if source_filter.upper() in _path.upper():
            _source_paths.append(_path)
        if target_filter.upper() in _path.upper():
            _target_paths.append(_path)
    _matching_pairs:list[tuple[str,str]] = []
    _missed_source_items:list[str] = []
    _missed_target_items:list[str] = []
    for _sp in _source_paths:
        _sp_found:bool = False
        _tp_found:bool = False
        for _tp in _target_paths:
            if _sp.replace(source_filter,'') == _tp.replace(target_filter, ''):
                _matching_pairs.append((_sp,_tp))
                _sp_found = True
                _tp_found == True
        if _sp_found == False and _sp not in _missed_source_items:
            _missed_source_items.append(_sp)
        if _tp_found == False and _sp not in _missed_target_items:
            _missed_target_items.append(_sp)
    for _pair in _matching_pairs:
        _source_stream = file.get_Job_Stream_by_name(_pair[0])
        _target_stream = file.get_Job_Stream_by_name(_pair[1])
        Action_IWS_Assets_merge_Notes_A_B(_source_stream, _target_stream)
        if check_dependancies == True:
            Action_IWS_Assets_merge_dependancies_A_B(_source_stream, _target_stream)
        if (_source_stream is not None) and (_target_stream is not None):
            _path_set_A = list(_source_stream.job_paths)
            _path_set_B = list(_target_stream.job_paths)
            _merged:dict[str, ToolBox_IWS_Job_Obj] = {}
            for _path_b in _path_set_B:
                if _path_b not in _merged.keys():
                    _merged[_path_b] = _target_stream.get_Job_by_name(_path_b.split('#')[-1])
                _path_b_replaced = _path_b.replace(target_filter, source_filter)
                try:
                    _idx_a = _path_set_A.index(_path_b_replaced)
                except Exception:
                    _idx_a = None
                if (_idx_a is not None):
                    Action_IWS_Assets_merge_dependancies_A_B(_source_stream.get_Job_by_name(_path_set_A[_idx_a].split('#')[-1]), _merged[_path_b])
                    _insert_idx = _idx_a + 1
                    while _insert_idx < len(_path_set_A):
                        _next_key = _path_set_A[_insert_idx]
                        if _next_key not in _merged.keys() and (_next_key.replace(source_filter, target_filter) not in _path_set_B):
                            log.debug (f"Missing Job '{_next_key}' in Job Steam : '{_target_stream.full_path}', merging Job from '{_source_stream.full_path}'.")
                            _merged[_next_key] = copy.deepcopy(_source_stream.get_Job_by_name(_next_key.split('#')[-1]))
                            _merged[_next_key].search_replace_text(source_filter, target_filter, updated_source= True)
                        elif _next_key in _path_set_B:
                            break
                        _insert_idx += 1
            if list(_merged.values()) != _target_stream._job_collection:
                _target_stream._job_collection = _merged.values()
    