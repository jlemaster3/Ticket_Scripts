#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, copy, difflib, shutil

#-------------------------------------------------
#   Variables
#-------------------------------------------------


# location of local repository directory:
source_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\IDXIX_SITALT_to_UATALT\\"

# where the output files shold go, dont use source location
output_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\IDXIX_SITALT_to_UATALT\\"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\IDXIX_SITALT_to_UATALT\\_step_3_diffrences_log.txt"
# Key - Value piar, key string is the source string to saerch for, and the value is what to replace it with.
find_replace_strings_A = {}

find_replace_strings_B = {}

exclude_text = []

# contains output Log strings.
_output_log_holder = []

#-------------------------------------------------
#   Functions
#-------------------------------------------------

# collects all files in source folder path that end with items found in file_types list
def get_jil_files (source_path:str, file_types:list=['.jil', '.job'])->list[str]:
    path = os.path.abspath(source_path)
    if not os.path.exists(path):
        _output_log_holder.append(f"Path not found : {source_path}")
    file_list = []
    for dir_path, dirs, files in os.walk(path):
        for file in files:
            if any([file.lower().endswith(e) for e in file_types]):
                file_list.append(os.path.join(dir_path,file))
    return file_list

# loops over each file and removes any file that does not contain at least one of the provided terms in search_terms list, terms must be string values
def files_with_search_terms (file_path_list:list, search_terms:list):
    file_holder = []
    for file in file_path_list:
        if not os.path.exists(file):
            _output_log_holder.append(f"Can not filter file {os.path.basename}, Unable to find file : {file}")
            continue
        if os.path.isfile(file):
            with open(file, 'r') as f:
                for line in f:
                    if any(_t in line for _t in search_terms) and (file not in file_holder):
                        file_holder.append(file)
    return file_holder


def get_files_by_name (path_list:list[str], term:str) ->list[str]:
    _holder:list[str] = []
    for _path in path_list:
        if term.upper() in os.path.basename(_path).upper():
            _holder.append(_path)
    return _holder


def get_diff_filePaths_A_B (source_list_A:list[str], source_list_B:list[str], delineatorList:list[str]=[]) ->list[str]:
    _diff_list:list[str] = []
    _match_list:list[tuple] = []
    _foundlist_A:dict[str:list[str]] = {}    
    for _filePath_A in source_list_A:
        _fileName_A = os.path.basename(_filePath_A)
        for _rem in delineatorList:
            if _rem.upper() in _fileName_A.upper():
                _fileName_A = _fileName_A.replace(_rem,'')
        if _fileName_A not in _foundlist_A.keys():
            _foundlist_A[_fileName_A] = []
        if _filePath_A not in _foundlist_A[_fileName_A]:
            _foundlist_A[_fileName_A].append(_filePath_A)

    for _filePath_B in source_list_B:
        _fileName_B = os.path.basename(_filePath_B)
        for _rem in delineatorList:
            if _rem.upper() in _fileName_B.upper():
                _fileName_B = _fileName_B.replace(_rem,'')
        if _fileName_B in _foundlist_A.keys():
            for _i in range(len(_foundlist_A[_fileName_B])):
                _match = (_foundlist_A[_fileName_B][_i], _filePath_B)
                _match_list.append(_match)
        else:
            _diff_list.append(_filePath_B)
    return (_diff_list)


def get_same_fileNames_A_B (source_list_A:list[str], source_list_B:list[str], delineatorList:list[str]=[])->list[tuple[str,str]]:
    _same_list:list[tuple[str,str]] = [] 
    for _filePath_A in source_list_A:
        _fileName_A = os.path.basename(_filePath_A)
        for _filePath_B in source_list_B:
            _fileName_B = os.path.basename(_filePath_B)
            for _rem in delineatorList:
                if _rem.upper() in _fileName_A.upper():
                    _fileName_A = _fileName_A.replace(_rem,'')
                if _rem.upper() in _fileName_B.upper():
                    _fileName_B = _fileName_B.replace(_rem,'')
            if _fileName_A.upper() == _fileName_B.upper():
                _same_list.append((_filePath_A, _filePath_B))
    return (_same_list)


def compare_dirPaths (source_A:str, source_B:str) -> tuple[str|None,str|None]:
    components1 = source_A.split(os.sep)
    components2 = source_B.split(os.sep)
    if os.name == 'nt' and len(components1) > 0 and len(components2) > 0:
        if components1[0].endswith(':') and components2[0].endswith(':'):
            if components1[0].lower() != components2[0].lower():
                return (components1[0], components2[0])
            else:
                components1 = components1[1:]
                components2 = components2[1:]
    min_len = min(len(components1), len(components2))
    for i in range(min_len):
        if components1[i] != components2[i]:
            return ('\\'.join(components1[i:]), '\\'.join(components2[i:]))
    # If one path is a prefix of the other (e.g., /a/b and /a/b/c)
    if len(components1) != len(components2):
        if len(components1) > len(components2):
            return ('\\'.join(components1[min_len:]), None)
        else:
            return (None, '\\'.join(components2[min_len:]))
    return (None, None) # Paths are identical

def check_filePathPairsList_diffrences (filePathPairList:list[tuple[str,str]], target_output_path:str, excludeTerms:list[str]=[]) :
    _output_log_holder.append(f"Checking [{len(filePathPairList)}] files for differences, placing updated files in : {target_output_path}")
    _output_log_holder.append(f"-"*100)
    _diff_file_count = 0
    _file_cntr_str_len = len(str(len(filePathPairList)))
    for _pairCounter, _pair in enumerate(filePathPairList):
        _relPathA, _relPathB = compare_dirPaths(_pair[0], _pair[1])
        _relPartsA = _relPathA.split(os.sep)
        _relPartsB = _relPathB.split(os.sep)
        _outpathA = os.path.join (target_output_path, os.sep.join(_relPartsA[1:]))
        _outpathB = os.path.join (target_output_path, os.sep.join(_relPartsB[1:]))
        if not os.path.exists(os.path.dirname(_outpathA)):
                os.makedirs(os.path.dirname(_outpathA))
        _should_replace_A_with_B:bool = False
        with open (_pair[0], 'r') as _file_A, open(_pair[1], 'r') as _file_B:
            _file_A_lines = _file_A.readlines()
            _file_B_lines = _file_B.readlines()
            if not any(any(_s in _l for _l in _file_A_lines) for _s in excludeTerms):
                _diff_list = list(difflib.unified_diff(_file_A_lines, _file_B_lines, fromfile=_pair[0], tofile=_pair[1], lineterm=''))
                if len(_diff_list) != 0:
                    _should_replace_A_with_B = True
                    _diff_cntr_len = len(str(len(_diff_list)))
                    for _diff_line_cnt, _diff_line in enumerate(_diff_list):
                        _temp = _diff_line.strip()
                        if (_temp != '') and (any(_s in _temp[0:2] for _s in ['+','-','@@'])):
                            _output_log_holder.append(f"[{str(_pairCounter+1).zfill(_file_cntr_str_len)}] [{str(_diff_line_cnt+1).zfill(_diff_cntr_len)}] {_temp}")
                    _diff_file_count += 1
        if _should_replace_A_with_B == True:
            shutil.copy(_pair[1], _outpathA)
            _output_log_holder.append(f"[{str(_pairCounter+1).zfill(_file_cntr_str_len)}] - Replaced with second file '{_relPathB}' renaming to '{_outpathA}'")
        else:
            shutil.copy(_pair[0], _outpathA)
            _output_log_holder.append(f"[{str(_pairCounter+1).zfill(_file_cntr_str_len)}] [01] --- {_pair[0]}")
            _output_log_holder.append(f"[{str(_pairCounter+1).zfill(_file_cntr_str_len)}] [02] +++ {_pair[0]}")
            _output_log_holder.append(f"[{str(_pairCounter+1).zfill(_file_cntr_str_len)}] [00] @@ No difference Found.")
            _output_log_holder.append(f"[{str(_pairCounter+1).zfill(_file_cntr_str_len)}] - Copying first file '{_relPathA}' to : '{_outpathA}'")
        _output_log_holder.append(f"-"*100)    
    _output_log_holder.append(f"Completed Check and found [{_diff_file_count}] file with differences.")


def copy_rename_files (sourceFileList:list[str], output_path:str, sourceRelPath:str=None, rename_prefix:str=None, rename_sufix:str=None):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for counter, filePath in enumerate(sourceFileList):
        _newFileName = os.path.basename(filePath).split('.')[0]
        _fileForamt = os.path.basename(filePath).split('.')[-1]
        _relPath = os.path.relpath(os.path.dirname(filePath), sourceRelPath) if sourceRelPath is not None else ''
        _relParts = _relPath.split(os.sep)
        _outpath = os.path.join (output_path, os.sep.join(_relParts[2:]))
        if rename_prefix is not None:
            _newFileName = f"{rename_prefix}{_newFileName}"
        if rename_sufix is not None:
            _newFileName = f"{_newFileName}{rename_sufix}"
        _newFileName = f"{_newFileName}.{_fileForamt}"
        if not(os.path.exists(_outpath)):
            os.makedirs(_outpath)
        _outputPath = os.path.join(_outpath, _newFileName)
        _output_log_holder.append(f" [{counter+1}] - Copied file '{filePath}' to new location: {_outputPath}")
        shutil.copy (filePath, _outputPath)
    



#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # get all jil files in path and all subdirectories
    _source_jobs_A = os.path.join(source_directory, 'jobs')
    _source_jobs_B = os.path.join(source_directory, 'jobs_alt')
    jil_files_dictionary_A = get_jil_files(_source_jobs_A)
    jil_files_dictionary_B = get_jil_files(_source_jobs_B)

    _output_path = os.path.join(output_directory, 'output')
    _output_log_holder.append(f"Soruce directory A : '{_source_jobs_A}'")
    _output_log_holder.append(f"Soruce directory B : '{_source_jobs_B}'")
    _output_log_holder.append(f"  Files in A : [{len(jil_files_dictionary_A)}]")
    _output_log_holder.append(f"  Files in B : [{len(jil_files_dictionary_B)}]")
    _output_log_holder.append('-'*100)
    _missing_from_A = get_diff_filePaths_A_B (jil_files_dictionary_A, jil_files_dictionary_B, delineatorList=["_ALT"])
    _output_log_holder.append(f"  File in Missing from A that are found in B: [{len(_missing_from_A)}]")
    copy_rename_files (_missing_from_A, _output_path, _source_jobs_A)
    _output_log_holder.append('-'*100)
    _missing_from_B = get_diff_filePaths_A_B (jil_files_dictionary_B, jil_files_dictionary_A, delineatorList=["_ALT"])
    _output_log_holder.append(f"  File in Missing from B that are found in A: [{len(_missing_from_B)}]")
    copy_rename_files (_missing_from_B, _output_path, _source_jobs_B, rename_sufix='_ALT')
    _output_log_holder.append('-'*100)
    _fileNames_in_both = get_same_fileNames_A_B(jil_files_dictionary_B, jil_files_dictionary_A, delineatorList=["_ALT"]) 
    _output_log_holder.append(f"  Overlap to Check: [{len(_fileNames_in_both)}]")
    check_filePathPairsList_diffrences(_fileNames_in_both,_output_path)
    
    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")
