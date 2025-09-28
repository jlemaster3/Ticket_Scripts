#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM00150789
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, shutil, difflib

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_dir_A = "C:\\VS_Managed_Accounts\\KSXIX\\UATC"
source_dir_B = "C:\\VS_Managed_Accounts\\KSXIX\\UATB"

# where the output files shold go, dont use source location
output_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0150789\\Diffrences\\UATB"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0150789\\UATC_2_UATB_log.txt"
exclude_text = ["@MACH2#", "@MACH3#", "@MACH7#"]

#-------------------------------------------------
#   Functions
#-------------------------------------------------

# collects all files in source folder path that end with items found in file_types list
def get_jil_files (source_path:str, file_types:list=['.jil', '.job'])->list[str]|None:
    path = os.path.abspath(source_path)
    if not os.path.exists(path):
        print (f"Path not found : {source_path}")
        return None
    file_list = []
    for root, _, files in os.walk(path):
        for file in files:
            if any(file.lower().endswith(ft) for ft in file_types):
                file_list.append(os.path.join(root, file))
    return file_list

def get_diff_filePaths_A_B (source_list_A:list[str], source_list_B:list[str]) ->list[str]:
    _diff_list = []
    for _filePath_A in source_list_A:
        _fileName_A = os.path.basename(_filePath_A)
        if all(_fileName_A.upper() != os.path.basename(_filePath_B).upper() for _filePath_B in source_list_B):
            _diff_list.append(_filePath_A)
    return (_diff_list)

def get_same_fileNames_A_B (source_list_A:list[str], source_list_B:list[str])->list[str]:
    _same_list = []
    for _filePath_A in source_list_A:
        _fileName_A = os.path.basename(_filePath_A)
        if any(_fileName_A.upper() == os.path.basename(_filePath_B).upper() for _filePath_B in source_list_B):
            _same_list.append(_fileName_A)
    return (_same_list)


def copy_to_path (source_filePath_list:list[str], source_root_path:str, target_output_path:str) ->str:
    _log_holder = [f"Copying [{len(source_filePath_list)}] files from {source_root_path} to {target_output_path}:"]
    _copy_counter = 0
    _file_cntr_str_len = len(str(len(source_filePath_list)))
    for _fp_counter,_filePath in enumerate(source_filePath_list):
        try:
            _copy_ok = True
            with open (_filePath, 'r') as _file:
                _file_A_lines = _file.readlines()
                if any(any(_s in _l for _l in _file_A_lines) for _s in exclude_text):
                    _copy_ok = False
            if _copy_ok == True:
                _file_name = os.path.basename(_filePath)
                _rel_path = os.path.relpath(_filePath, source_root_path)
                _target_path = os.path.join(target_output_path, os.path.dirname(_rel_path))
                if not os.path.exists(_target_path) :
                    os.makedirs(_target_path)
                _output_path = os.path.join(_target_path, _file_name)
                shutil.copy(_filePath, _output_path)
                _copy_counter += 1
                _log_holder.append(f"[{str(_fp_counter+1).zfill(_file_cntr_str_len)}] - Copied source file {_filePath} to target location {_output_path}")
            else:
                _line_count = 1
                _log_holder.append(f"[{str(_fp_counter+1).zfill(_file_cntr_str_len)}] [{_line_count}] --- Skipping file copy : {_filePath}")
                for _lc, _l in enumerate(_file_A_lines):
                    for _s in exclude_text:
                        if _s.lower() in _l.lower():
                            _line_count += 1
                            _log_holder.append(f"[{str(_fp_counter+1).zfill(_file_cntr_str_len)}] [{_line_count}]     Refrence to {_s} on line {_lc+1} not resolvable in target environment.")

            _log_holder.append(f"-"*100)
        except FileNotFoundError as fnfe:
            _log_holder.append(f"[{str(_fp_counter+1).zfill(_file_cntr_str_len)}] - Source file not found: {fnfe}")
        except Exception as e:
            _log_holder.append(f"[{str(_fp_counter+1).zfill(_file_cntr_str_len)}] - Error copying {_filePath}: {e}")
    _log_holder.append(f"Completed with [{_copy_counter}] files copied.")
    return "\n".join(_log_holder)


def check_differences (source_dir_A:str, source_dir_B:str, source_root_A:str, file_name_list:list[str], target_output_path:str|None=None) ->str:
    _log_holder = [f"Checking [{len(file_name_list)}] files for differences, placing updated files in : {target_output_path}"]
    _log_holder.append(f"-"*100)
    _diff_file_count = 0
    _file_cntr_str_len = len(str(len(file_name_list)))
    for _file_coutner, _fileName in enumerate(file_name_list):
        _sourcePaths_A = [_path for _path in source_dir_A if _fileName in _path]
        _sourcePaths_B = [_path for _path in source_dir_B if _fileName in _path]
        if (len(_sourcePaths_A) >= 1) and (len(_sourcePaths_B) >=1):
            _first_path_A = _sourcePaths_A[0]
            _first_path_B = _sourcePaths_B[0]
            _file_name = os.path.basename(_first_path_A)
            _rel_path = os.path.relpath(_first_path_A, source_root_A)
            _target_path = os.path.join(target_output_path, os.path.dirname(_rel_path))
            if not os.path.exists(_target_path):
                os.makedirs(_target_path)
            _output_path = os.path.join(_target_path, _file_name)
            with open (_first_path_A, 'r') as _file_A, open(_first_path_B, 'r') as _file_B:
                _file_A_lines = _file_A.readlines()
                _file_B_lines = _file_B.readlines()
                if not any(any(_s in _l for _l in _file_A_lines) for _s in exclude_text):
                    _diff_list = list(difflib.unified_diff(_file_A_lines, _file_B_lines, fromfile=_first_path_A, tofile=_first_path_B, lineterm=''))
                
                    if len(_diff_list) != 0:
                        _diff_cntr_len = len(str(len(_diff_list)))
                        for _diff_line_cnt, _diff_line in enumerate(_diff_list):
                            _temp = _diff_line.strip()
                            if (_temp != '') and (any(_s in _temp[0:2] for _s in ['+','-','@@'])):
                                _log_holder.append(f"[{str(_file_coutner+1).zfill(_file_cntr_str_len)}] [{str(_diff_line_cnt+1).zfill(_diff_cntr_len)}] {_temp}")
                        shutil.copy(_first_path_A, _output_path)
                        _log_holder.append(f"-"*100)    
                        _diff_file_count += 1
                elif any(any(_s in _l for _l in _file_A_lines) for _s in exclude_text):
                    _line_count = 1
                    _log_holder.append(f"[{str(_file_coutner+1).zfill(_file_cntr_str_len)}] [{_line_count}] --- Skipping file : {_first_path_A}")
                    for _lc, _l in enumerate(_file_A_lines):
                        for _s in exclude_text:
                            if _s.lower() in _l.lower():
                                _line_count += 1
                                _log_holder.append(f"[{str(_file_coutner+1).zfill(_file_cntr_str_len)}] [{_line_count}]     Refrence to {_s} on line {_lc+1} not resolvable in target environment.")
                    _log_holder.append(f"-"*100)
                #else:
                #    _log_holder.append(f"[{str(_file_coutner+1).zfill(_file_cntr_str_len)}] [1] --- {_first_path_A}")
                #    _log_holder.append(f"[{str(_file_coutner+1).zfill(_file_cntr_str_len)}] [2] +++ {_first_path_B}")
                #    _log_holder.append(f"[{str(_file_coutner+1).zfill(_file_cntr_str_len)}] [3]     No Differences Found")
                #    _log_holder.append(f"-"*100)
    _log_holder.append(f"Completed Check and found [{_diff_file_count}] file with differences.")                    
    return ("\n".join(_log_holder), _diff_file_count)
#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    _file_list_A = get_jil_files(source_dir_A)
    _file_list_B = get_jil_files(source_dir_B)

    _missing_from_B = get_diff_filePaths_A_B (_file_list_A, _file_list_B)
    _fileNames_in_both = get_same_fileNames_A_B(_file_list_A, _file_list_B) 
    _copy_log = copy_to_path(_missing_from_B,source_dir_A, output_directory)
    _differences_log, _diff_counter = check_differences(_file_list_A, _file_list_B, source_dir_A, _fileNames_in_both, output_directory)


    _output_log_holder = []
    _output_log_holder.append(f"Soruce directory A : '{source_dir_A}'")
    _output_log_holder.append(f"Soruce directory B : '{source_dir_B}'")
    _output_log_holder.append(f"  Files in A : [{len(_file_list_A)}]")
    _output_log_holder.append(f"  Files in B : [{len(_file_list_B)}]")
    _output_log_holder.append(f"  Missing from B: [{len(_missing_from_B)}]")
    _output_log_holder.append(f"  Overlap to Check: [{len(_fileNames_in_both)}]")
    _output_log_holder.append(f"  Differences : [{_diff_counter}]")
    _output_log_holder.append('-'*100)
    _output_log_holder.extend(_copy_log.split('\n'))
    _output_log_holder.append('-'*100)
    _output_log_holder.extend(_differences_log.split('\n'))

    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")

