#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, shutil, copy
from typing import Any
from ToolBox.ToolBox_logger import OutputLogger
from ToolBox.ToolBox_Object import ToolBox_FileData

#-------------------------------------------------
#   Functions
#-------------------------------------------------

def gather_files (
        source_path:str, 
        file_types:list=['.jil', '.job'], 
        excludedDirectories:list[str] = None, 
        excludedFileNames:list[str]=None, 
        excludeFileFormats:list[str]=None,
        isolateByDirectories:list[str] = None, 
        isolateByFileNames:list[str]=None,
    ) -> list[ToolBox_FileData] | None:
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
    _found_file_list:list[ToolBox_FileData] = []
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
                log.debug(f"Excluding File from collection : '{_filePath}' | {_reasons}")
            else:
                log.debug(f"Adding File to collection : '{_filePath}'")
                _relPath = os.path.relpath(dir_path,source_path)
                if _relPath not in _relPaths.keys():
                    _relPaths[_relPath] = []
                
                _relPaths[_relPath].append(file)
                _fileData = ToolBox_FileData(os.path.join (source_path,_relPath,file), rootPath=source_path)
                _found_file_list.append(_fileData)
                _collectedCounter += 1
    log.info(f"Found [{_collectedCounter}] Files out of [{_totalCounter}] files.")
    log.info(f"from [{len(_relPaths)}] directories:",data = _relPaths)
    return _found_file_list


def filter_fileList_by_terms (file_list:list[ToolBox_FileData], search_terms:list[str]):
    """Loops over the list of filePaths provided, and returns a list of file paths with files that containe the defiend search_terms"""
    log = OutputLogger.get_instance()
    file_holder = []
    for file in file_list:
        _lineid_terms = file.search_for_terms (search_terms)
        if len(_lineid_terms) >= 1:
            file_holder.append(file)            
    return file_holder

