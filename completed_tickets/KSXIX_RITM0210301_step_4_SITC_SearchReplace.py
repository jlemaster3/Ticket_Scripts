#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM0210301

Created by: Jim Lemaster
Date: 06/26/2024

Purpose: This script is designed to Search and Replace values only if the Job or Job Stream is assigned to MACH8.
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------


from datetime import datetime as dt

import os, re

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0210301\\SITC_copy"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0210301\\KSXIX_SITC_step4_replace_log.txt"

# Key - Value piar, key string is the source string to saerch for, and the value is what to replace it with.
find_replace_strings = {
    "/export/customer/kscmnc/mod/job/autojob.sh":"/dsks/{APP_CMN}/{ENV_DIR}/autojob.sh",
    "/export/ftp/kscmnc/mod":"/dsks/ftp/{APP_CMN}/{ENV_DIR}",
    "/export/home/kscmnc":"/dsks/home/{APP_CMN}/{ENV_DIR}",
    "{JOBDIR}": "/dsks/{APP_CMN}/{ENV_DIR}",
    "DEVB" :"{ENV}",
    "SITB" :"{ENV}",
    "UATB" :"{ENV}",
    "DEVC" :"{ENV}",
    "SITC" :"{ENV}",
    "UATC" :"{ENV}",
    "PPS" :"{ENV}",
    "PROD" :"{ENV}"
}

target_workstation = 'MACH8'

commentLinesWith_term = []

exclude_dir = []

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
        print (f"Path not found : {source_path}")
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
            print (f"Can not filter file {os.path.basename}, Unable to find file : {file}")
            continue
        if os.path.isfile(file):
            with open(file, 'r') as f:
                for line in f:
                    if any(_t in line for _t in search_terms) and (file not in file_holder):
                        file_holder.append(file)
    return file_holder


def find_first_nonWhiteSpace (sourceString:str) -> int :
    for i, char in enumerate(sourceString):
        if not char.isspace():
            return i
    return -1


def commentoutLineByTerms (source_string:str, search_term:str, fileindex:int) -> str:
    _source_lines = str(source_string).split('\n')    
    _stream_start_ids:list[int] = []
    _stream_edge_ids:list[int] = []
    _job_line_ids:list[int] = []
    _comment_term_ids:dict[int, list[str]] = {}
    _stream_end_ids:list[int] = []
    for _line_id, _line in enumerate(_source_lines):
        if "SCHEDULE" in str(_line).strip()[0:9]:
            _stream_start_ids.append(_line_id)
        if ':' in _line[0:2]:
            _stream_edge_ids.append(_line_id)
        if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) or (any(_s in str(_line).strip()[0:5] for _s in ['PRD#', 'NPR#'])) and ('#' in str(_line[2:]).strip()):
            _job_line_ids.append(_line_id)        
        if "END" in str(_line).strip()[0:4] and 'ENDJOIN' not in str(_line).strip():
            _stream_end_ids.append(_line_id)
        for _term in search_term:
            if _term.upper() in _line.upper():
                if _line_id not in _comment_term_ids.keys():
                    _comment_term_ids[_line_id] = []
                _comment_term_ids[_line_id].append(_term)
    
    for _foundCount, (_lineIdx, _foundList) in enumerate(_comment_term_ids.items()):
        if (_lineIdx in _stream_start_ids) or (_lineIdx in _job_line_ids):
            _output_log_holder.append(f" [{fileindex+1}] [{_lineIdx}] - Stream or Job definition line contains term : {_term}")
            return "REMOVE"
        _terms = f"{', '.join(_foundList)}"
        _new_line = re.sub(r'(\S)', r'##\1', _source_lines[_lineIdx], 1)
        _source_lines[_lineIdx] = _new_line
        
        _output_log_holder.append(f" [{fileindex+1}] [{_lineIdx}] - Commenting out line containing term : {_terms}")
    
    return_string = '\n'.join(_source_lines)
    return return_string
    
def update_MACH_NUM_DOCOMMAND (source_string:str, search_term:str, replace_val:str, target_workstation:str) -> str:
    _source_lines = str(source_string).split('\n')    
    _stream_start_ids:list[int] = []
    _stream_edge_ids:list[int] = []
    _job_line_ids:list[int] = []
    _DOCOMMAND_lines:list[int] = []
    _stream_end_ids:list[int] = []
    for _line_id, _line in enumerate(_source_lines):
        if "SCHEDULE" in str(_line).strip()[0:9]:
            _stream_start_ids.append(_line_id)
        if ':' in _line[0:2]:
            _stream_edge_ids.append(_line_id)
        if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) or (any(_s in str(_line).strip()[0:5] for _s in ['PRD#', 'NPR#'])) and ('#' in str(_line[2:]).strip()):
            _job_line_ids.append(_line_id)
        if 'DOCOMMAND' in _line:
            _DOCOMMAND_lines.append(_line_id)
        if "END" in str(_line).strip()[0:4] and 'ENDJOIN' not in str(_line).strip():
            _stream_end_ids.append(_line_id)
    for _i in range(len(_stream_start_ids)):
        _start_id = _stream_start_ids[_i]
        _end_id = _stream_end_ids[_i]
        if target_workstation.upper() in _source_lines[_start_id].upper():
            for _dcmd_id in [_id for _id in _DOCOMMAND_lines if _start_id < _id < _end_id]:
                _temp = f"  - Changing line [{_dcmd_id}]: {_source_lines[_dcmd_id]}"
                _newline = _source_lines[_dcmd_id].replace(search_term, replace_val,-1)
                if _newline != _source_lines[_dcmd_id]:
                    _source_lines[_dcmd_id] = _newline
                    _temp += f" to  {_source_lines[_dcmd_id]}"
                    _output_log_holder.append(_temp)
    updated_string = '\n'.join(_source_lines)
    return updated_string


# output files will be saved in the provided output_path with the same file name as the source
# output file will contain both the orriginal contents and the duplicated/edited contents in the same file.
def process_files (path_list:list, seach_replace_dictionary:dict, targetWorkstation:str):
    file_remove_list = []
    
    for counter, filePath in enumerate(path_list):
        file_name = os.path.basename(filePath)
        _rel_path = os.path.relpath(filePath, source_directory)
        try:    
            output_filePath = filePath
            if os.path.isfile(filePath):
                source_file = open(filePath, "r")
                source_string = source_file.read()
                _skip = False
                for _s in exclude_text:
                    if _s in source_string:
                        _output_log_holder.append (f" [{counter+1}] - Skipping file {file_name}, excluded text '{_s}' was found in source text.")
                        _skip = True
                        break
                _output_log_holder.append(f" [{counter+1}] - Processing File : '{_rel_path}'")
                if len(commentLinesWith_term) >= 1:
                    source_string = commentoutLineByTerms(source_string, commentLinesWith_term, counter)
                    if "REMOVE" in source_string[0:8].upper():
                        _output_log_holder.append (f" [{counter+1}] - Removing File from collection.")
                        _skip = True
                        file_remove_list.append(filePath)
                if _skip == True:
                    _output_log_holder.append('-'*100)
                    continue
                
                for _replace_counter, (search_key, repalce_val) in enumerate(seach_replace_dictionary.items()):
                    source_string = update_MACH_NUM_DOCOMMAND(source_string, search_key, repalce_val, target_workstation=targetWorkstation)


                with open(output_filePath, "w") as output_file:
                    output_file.write(source_string)
                    _output_log_holder.append(f" [{counter+1}] - Updated file")
        except Exception as e:
            _output_log_holder.append(f" [{counter+1}] - Error processing file : {os.path.basename(filePath)} - {e}")
        
        _output_log_holder.append('-'*100)

    for _fp in file_remove_list:
        os.remove(_fp)
        print (f"removed {_fp}")
                

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    
    # get all jil files in path and all subdirectories
    jil_files_dictionary = get_jil_files(source_directory)

    _output_log_holder.append(f"Running Search and Replace process")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Soruce directory : '{source_directory}'")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of Terms to search and Comment out: [{len(commentLinesWith_term)}]")
    for _term_count, _term in enumerate(commentLinesWith_term):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term}")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of files found in source Directory: [{len(jil_files_dictionary)}]")
    _output_log_holder.append('-'*100)
    _output_log_holder.append('')
    _output_log_holder.append('-'*100)

    # create new files that contains a copy of the edited contents
    process_files(
        path_list=jil_files_dictionary, 
        seach_replace_dictionary=find_replace_strings,
        targetWorkstation = target_workstation
    )   

    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")