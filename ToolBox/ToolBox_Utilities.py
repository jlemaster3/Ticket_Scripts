#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, re, shutil, copy
from typing import Optional, List, Any
from ToolBox.ToolBox_logger import OutputLogger
from ToolBox.ToolBox_Object import ToolBox_IWS_JIL_File

#-------------------------------------------------
#   Global - Functions
#-------------------------------------------------

def gather_files (
    source_path: str,
    exclude_subfolders: Optional[List[str]] = None,
    include_name_terms: Optional[List[str]] = None,
    exclude_name_terms: Optional[List[str]] = None,
    include_formats: Optional[List[str]] = None,
    exclude_formats: Optional[List[str]] = None,
    quite_logging:bool = False
) -> list[ToolBox_IWS_JIL_File] | None:
    """Collects full file paths from a source directory with optional filtering.

    Parameters
    ----------
    source_path : str
        Directory to search.
    exclude_subfolders : list[str], optional
        List of substrings; if a subfolder path contains any, it will be skipped.
    include_name_terms : list[str], optional
        Only include files that contain one of these terms in their name.
    exclude_name_terms : list[str], optional
        Exclude files that contain any of these terms in their name.
    include_formats : list[str], optional
        Only include files with these extensions (e.g., ['.txt', '.csv']).
    exclude_formats : list[str], optional
        Exclude files with these extensions.

    Returns
    -------
    List[ToolBox_File]
        A list object that contains ToolBox fileData objects representing the foudn files.
    """
    log = OutputLogger.get_instance()
    if not(os.path.exists(source_path)):
        log.warning(f"Unable to find path in sourcePaths List. target Path: '{source_path}'")
        return None
    _exclude_subfolders = [_term.lower() for _term in (exclude_subfolders or [])]
    _include_name_terms = [_term.lower() for _term in (include_name_terms or [])]
    _exclude_name_terms = [_term.lower() for _term in (exclude_name_terms or [])]
    _include_formats = [f.lower() for f in (include_formats or [])]
    _exclude_formats = [f.lower() for f in (exclude_formats or [])]
    if len(_exclude_subfolders) >= 1 : log.info(f"Exclude Directory Paths containing Terms : ", data=_exclude_subfolders)
    if len(_exclude_name_terms) >= 1 : log.info(f"Exclude Files Names containing Terms : ", data=_exclude_name_terms)
    if len(_exclude_formats) >= 1 : log.info(f"Exclude Foramts : ", data=_exclude_formats)
    if len(_include_name_terms) >= 1 : log.info(f"Isolating files by terms : ", data=_include_name_terms)
    if len(_include_name_terms) >= 1 : log.info(f"Directory Paths containing Terms : ", data=_include_name_terms)
    _file_collection = []
    for _root, _dirs, _files in os.walk(source_path, topdown=True):
        _dirs[:] = [ d for d in _dirs if not any(excl.lower() in os.path.join(_root, d).lower() for excl in _exclude_subfolders)]
        for _file in _files:
            
            _name = os.path.splitext(_file)[0]
            _ext = os.path.splitext(_file)[1].lower()
            if include_name_terms and not any(term in _name.lower() for term in _include_name_terms) : 
                if (quite_logging != True): log.debug(f"File name does not match any of the include search terms.")
                continue
            if any(term.lower() in _name.lower() for term in _exclude_name_terms) : 
                if (quite_logging != True): log.debug(f"File name contains a matchto one of the excluded search term.")
                continue
            if include_formats and _ext.lower() not in _include_formats : 
                if (quite_logging != True): log.debug(f"File format not listed in the include format list.")
                continue
            if _ext.lower() in _exclude_formats : 
                if (quite_logging != True): log.debug(f"File foramt listed in the exclude foramts list.")
                continue
            
            _full_path = os.path.join(_root, _file)
            if (quite_logging != True): log.debug(f"Adding File to collection : '{_full_path}'")
            
            if _ext == '.jil':
                _fileData = ToolBox_IWS_JIL_File(_full_path, rootPath=source_path)
                _file_collection.append(_fileData)
    return _file_collection        



def gather_files_old (
        source_path:str, 
        file_types:list=['.jil', '.job'], 
        excludedDirectories:list[str] = None, 
        excludedFileNames:list[str]=None, 
        excludeFileFormats:list[str]=None,
        isolateByDirectories:list[str] = None, 
        isolateByFileNames:list[str]=None,
        quite_logging:bool = False
    ) -> dict[str,ToolBox_IWS_JIL_File] | None:
    """Gathers refferences to all files in each provided source path, filtering for file formats, directory paths, and file names"""
    log = OutputLogger.get_instance()
    _known_file_formats = [fmt.lower() for fmt in file_types]
    log.info(f"Valid File Formats", data=_known_file_formats)
    _excludeFileNames = excludedFileNames if excludedFileNames != None else []
    _excludeDirNames = excludedDirectories if excludedDirectories != None else []
    _excludeFileFormats = excludeFileFormats if excludeFileFormats != None else []
    _isolateByFileNames = isolateByFileNames if isolateByFileNames != None else []
    _isolateByDirNames = isolateByDirectories if isolateByDirectories != None else []
    if len(_excludeDirNames) >= 1 : log.info(f"Exclude Directory Paths containing Terms : ", data=_excludeDirNames)
    if len(_excludeFileNames) >= 1 : log.info(f"Exclude Files Names containing Terms : ", data=_excludeFileNames)
    if len(_excludeFileFormats) >= 1 : log.info(f"Exclude Foramts : ", data=_excludeFileFormats)
    if len(_isolateByDirNames) >= 1 : log.info(f"Isolating files by terms : ", data=_isolateByDirNames)
    if len(_isolateByFileNames) >= 1 : log.info(f"Directory Paths containing Terms : ", data=_isolateByFileNames)
    _totalCounter = 0
    _collectedCounter = 0
    _relPaths = {}
    _found_file_list:dict[str,ToolBox_IWS_JIL_File] = {}
    if not(os.path.exists(source_path)):
        log.warning(f"Unable to find path in sourcePaths List. target Path: '{source_path}'")
        return None
        
    for dir_path, dirs, files in os.walk(source_path):
        for file in files:
            _totalCounter +=1
            _should_add:bool = True
            _excludeText = []
            _includeText = []
            _filePath = os.path.join(dir_path,file)
            #Checks if directory path contains excluded directory term
            if len(_excludeDirNames) >= 1:
                for _excludeDir in _excludeDirNames:
                    if (_excludeDir.lower() in dir_path.lower()) or (_excludeDir.lower() == dir_path.lower()):
                        _excludeText.append(f"File path contains excluded directory term : '{_excludeDir}'")
                        _should_add = False
            #Checks if file name contains an excluded file name term.
            if len(_excludeFileNames) >= 1:
                for _excludeFileName in _excludeFileNames:
                    if (_excludeFileName.lower() in file.lower()):
                        _excludeText.append(f"File path contains excluded file name : '{_excludeFileName}'")
                        _should_add = False
            #Checks if file foramt ends with and of the known formats.
            if excludeFileFormats is not None and len(excludeFileFormats) >= 1:
                if not any([file.lower().endswith(fmt) for fmt in _known_file_formats]):
                    _excludeText.append(f"File is not correct File Format : '*.{str(os.path.basename(file)).split('.')[-1]}'")
                    _should_add = False
            elif not any([file.lower().endswith(fmt) for fmt in _known_file_formats]):
                _excludeText.append(f"File is not correct File Format : '*.{str(os.path.basename(file)).split('.')[-1]}'")
                _should_add = False
            #Checks if directory path contains excluded directory term
            if (len(_isolateByDirNames) >= 1) and (_should_add == True):
                _found_dir_terms = []
                for _isolateDir in _isolateByDirNames:
                    if (_isolateDir.lower() in dir_path.lower()) or (_isolateDir.lower() == dir_path.lower()):
                        _found_dir_terms.append(_isolateDir)
                if (len(_found_dir_terms) == 0):
                    _excludeText.append(f"Folder path does not contain any of the Isolation Directory terms")
                    _should_add = False

            #Checks if file name contains excluded directory term
            if (len(_isolateByFileNames) >= 1) and (_should_add == True):
                _found_name_terms = []
                for _isolateName in _isolateByFileNames:
                    if (_isolateName.lower() in file.lower()) or (_isolateName.lower() == file.lower()):
                        _found_name_terms.append(_isolateName)
                if (len(_found_name_terms) == 0):
                    _excludeText.append(f"File name does not contain any of the Isolation File terms")
                    _should_add = False
            #Checks is file should be added to data set:
            if (_should_add == False):
                _reasons = ', '.join([f'"{_sc+1}":"{_str}"' for _sc, _str in enumerate(_excludeText)])
                if (quite_logging != True): log.debug(f"Excluding File from collection : '{_filePath}' | {_reasons}")
            else:
                if (quite_logging != True): log.debug(f"Adding File to collection : '{_filePath}'")
                _relPath = os.path.relpath(dir_path,source_path)
                if _relPath not in _relPaths.keys():
                    _relPaths[_relPath] = []
                _relPaths[_relPath].append(file)
                _fileData = ToolBox_IWS_JIL_File(os.path.join (source_path,_relPath,file), rootPath=source_path)
                _found_file_list[_fileData.id] = _fileData
                _collectedCounter += 1
    log.info(f"Collected [{_collectedCounter}] Files out of [{_totalCounter}] files in [{len(_relPaths)}] diffrent sub-directories : ",data = _relPaths)
    return _found_file_list




def sync_Files_A_to_B (
        file_A:ToolBox_IWS_JIL_File, 
        file_B:ToolBox_IWS_JIL_File, 
        worksataiton_criteria:list[tuple[str,str]] = None,
        folder_criteria:list[tuple[str,str]] = None
    ):
    """Compares Job Streams from File A to File B. 
        - If source Stream from File A is not found in File B, the Stream will be copied to File B.
        - I the Streams are found in Both files, any Job that exists in File A in the found stream will be copied over to File B under the coresponding Stream.

        Source IWS Workstations to target IWS Workstations can be applied as a filter if provided, otherwise exact match is required.
        Source IWS Folder to target IWS Folder can be applied as a filter if provided, otherwise exact match is required.
    """

    log = OutputLogger.get_instance()
    file_A.openFile()
    file_B.openFile()

    _file_A_streams = set(file_A.jobStreamPaths)
    _file_B_streams = set(file_B.jobStreamPaths)

    for _streamPath_A in _file_A_streams:
        _skip = False
        if (worksataiton_criteria is not None) and (len(worksataiton_criteria) >= 1):
            for _ws in [_item[0] for _item in worksataiton_criteria if _item[0].upper() not in _streamPath_A.upper()]:
                _skip = True
        if (folder_criteria is not None) and (len(folder_criteria) >= 1):
            for _fl in [_item[0] for _item in folder_criteria if _item[0].upper() not in _streamPath_A.upper()]:
                _skip = True
        if _skip == True:
            log.debug(f"Skipping source Stream '{_streamPath_A}', did not match filter criteria.")
            continue
        _stream_A_name = _streamPath_A.split('/')[-1]

        for _streamPath_B in _file_B_streams:
            if (worksataiton_criteria is not None) and (len(worksataiton_criteria) >= 1):
                for __ws in [_item[0] for _item in worksataiton_criteria if _item[0].upper() not in _streamPath_A.upper()]:
                    _skip = True

    return None