#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM0210301

Created by: Jim Lemaster
Date: 06/26/2024

Purpose: This script is designed to copy files from PROD into PPS.
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------


from datetime import datetime as dt

import os, copy

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\VS_Managed_Accounts\\KSXIX\\PROD"

# where the output files shold go, dont use source location
output_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0210301\\PPS_copy"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0210301\\KSXIX_PPS_step1_copy_log.txt"

# Key - Value piar, key string is the source string to saerch for, and the value is what to replace it with.
find_replace_strings = {
    "@MACH1#" :"@MACH8#",
}

exclude_text = ["@MACH7#"]

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

# adds draft to job stream text in source stream
def add_Draft_to_String (source_string:str):
    _lines = str(source_string).split('\n')
    _js_list = []
    _description_lines = []
    _has_draft = []
    for _id, _line in enumerate(_lines):
        if 'SCHEDULE' in _line:
            _js_list.append(_id)
        if ':' in _line[0:2]:
            _js_list.append(_id)
        if 'DESCRIPTION' in _line:
            _description_lines.append(_id)
        if 'DRAFT' in _line:
            _has_draft.append(_id)
    _id_sets = list(zip(_js_list[::2], _js_list[1::2]))
    for _disc_line in _description_lines:
        for _set in _id_sets:
            already_draft = False
            if (len(_has_draft) >= 1):
                for _draft_id in _has_draft:
                    if _set[0] < _draft_id < _set[1] :
                        already_draft = True
            if (_set[0] < _disc_line < _set[1]) and (already_draft == False):
                _lines.insert(int(_disc_line+1), 'DRAFT')
                _output_log_holder.append(f"    - Adding 'DRAFT' to Job Stream : '{_lines[_set[0]].split('/')[-1]}'")
    string_with_draft = '\n'.join(_lines)
    return string_with_draft

# adds NOP to job text in source string
def add_NOP_to_String (source_string:str):
    _source_lines = str(source_string).split('\n')    
    _stream_start_ids:list[int] = []
    _stream_edge_ids:list[int] = []
    _job_line_ids:list[int] = []
    _recovery_lines:list[int] = []
    _nop_lines:list[int] = []
    _stream_end_ids:list[int] = []
    for _line_id, _line in enumerate(_source_lines):
        if "SCHEDULE" in str(_line).strip()[0:9]:
            _stream_start_ids.append(_line_id)
        if ':' in _line[0:2]:
            _stream_edge_ids.append(_line_id)
        if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) or (any(_s in str(_line).strip()[0:5] for _s in ['PRD#', 'NPR#'])) and ('#' in str(_line[2:]).strip()):
            _job_line_ids.append(_line_id)
        if 'RECOVERY' in _line:
            _recovery_lines.append(_line_id)
        if 'NOP' in _line:
            _nop_lines.append(_line_id)
        if "END" in str(_line).strip()[0:4] and 'ENDJOIN' not in str(_line).strip():
            _stream_end_ids.append(_line_id)
    _insert_line:dict[int, str] = {}
    for _stream_id in range(len(_stream_start_ids)):
        _stream_idx = _stream_start_ids[_stream_id]
        _stream_end = _stream_end_ids[_stream_id]
        _job_ids = [_j_idx+1 for _j_idx in _job_line_ids if _stream_idx < _j_idx < _stream_end]
        _job_sets = list((_job_line_ids[_i]+1, _job_line_ids[_i+1]) for _i in range(len(_job_ids)-1))
        _job_sets.append((_job_ids[-1], _stream_end))
        for _job_line_set in _job_sets:
            _rec_ids = [_rec_idx+1 for _rec_idx in _recovery_lines if _job_line_set[0] < _rec_idx < _job_line_set[1]]
            _nop_ids = [_nop_idx+1 for _nop_idx in _nop_lines if _job_line_set[0] < _nop_idx < _job_line_set[1]]    
            if (len(_rec_ids) >= 1) and (len(_nop_ids) == 0):
                _insert_line[int(_rec_ids[-1])] = ' NOP'
                _output_log_holder.append(f"    - Adding 'NOP' to Job Stream : '{_source_lines[_job_line_set[0]].split('/')[-1]}'")
    _insert_line = dict(reversed(_insert_line.items()))
    for _line_idx, _insert_str in _insert_line.items():
        _source_lines.insert(_line_idx, _insert_str)
    string_with_NOP = '\n'.join(_source_lines)
    return string_with_NOP



# output files will be saved in the provided output_path with the same file name as the source
# output file will contain both the orriginal contents and the duplicated/edited contents in the same file.
def process_files (path_list:list, seach_replace_dictionary:dict, output_path:str, overwrite_original_file:bool=False, keep_original_Stream:bool=False, original_to_DRAFT:bool=False, original_to_NOP:bool=False, changed_to_DRAFT:bool=False, changed_to_NOP:bool=True,):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for counter, filePath in enumerate(path_list):
        file_name = os.path.basename(filePath)
        _rel_path = os.path.relpath(filePath, source_directory)
        _output_log_holder.append(f" [{counter+1}] - Processing File : '{_rel_path}'")
        try:    
            if overwrite_original_file == False:
                _target_path = os.path.join(output_path, os.path.dirname(_rel_path))
                if not (os.path.exists(_target_path)):
                    os.makedirs(_target_path)
                output_filePath = os.path.join(_target_path, file_name)    
            else:
                output_filePath = filePath
            if os.path.isfile(filePath):
                source_file = open(filePath, "r")
                source_string = source_file.read()
                _skip = False
                for _s in exclude_text:
                    if _s in source_string:
                        _output_log_holder.append (f" [{counter+1}] [{_replace_counter+1}] - Skipping file, excluded text '{_s}' was found in source text.")
                        _skip = True
                        break
                if _skip == True:
                    _output_log_holder.append('-'*100)
                    continue
                duplicate_str = str(copy.deepcopy(source_string))
                for _replace_counter, (search_key, repalce_val) in enumerate(seach_replace_dictionary.items()):
                    duplicate_str = duplicate_str.replace(str(search_key), str(repalce_val))
                    _output_log_holder.append (f" [{counter+1}] [{_replace_counter+1}] - Copied and Replaced : '{search_key}' With : '{repalce_val}'")
                if original_to_DRAFT == True:
                    source_string = add_Draft_to_String(source_string)
                if original_to_NOP == True:
                    source_string = add_NOP_to_String(source_string)
                if changed_to_DRAFT == True:
                    duplicate_str = add_Draft_to_String(duplicate_str)
                if changed_to_NOP == True:
                    duplicate_str = add_NOP_to_String(duplicate_str)
                with open(output_filePath, "w") as output_file:
                    if keep_original_Stream == True:
                        output_file.write(source_string)
                        output_file.write("\n\n")
                    output_file.write(duplicate_str)
                    _output_log_holder.append(f" [{counter+1}] - Created new file")
        except Exception as e:
            _output_log_holder.append(f" [{counter+1}] - Error processing file : {os.path.basename(filePath)} - {e}")
        
        _output_log_holder.append('-'*100)

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    

    # get all jil files in path and all subdirectories
    jil_files_dictionary = get_jil_files(source_directory)
    #collects saerchtersm as a list form source dictionary
    search_terms = list(find_replace_strings.keys())
    #filter list of files down to those that contian the sarch terms
    fitlered_files = files_with_search_terms (jil_files_dictionary, search_terms)

    _output_log_holder.append(f"Running Search and Replace process")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Soruce directory : '{source_directory}'")
    _output_log_holder.append(f"Output directory : '{output_directory}'")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of Search and Replace Terms: [{len(search_terms)}]")
    for _term_count, (_term,_replace) in enumerate(find_replace_strings.items()):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term} -> {_replace}")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of files found in source Directory: [{len(jil_files_dictionary)}]")
    _output_log_holder.append(f"Number of files found with Search Terms: [{len(fitlered_files)}]")

    # create new files that contains a copy of the edited contents
    process_files(
        path_list=jil_files_dictionary, 
        seach_replace_dictionary=find_replace_strings, 
        output_path=output_directory, 
        overwrite_original_file=False, 
        keep_original_Stream=False, 
        original_to_DRAFT=False,
        original_to_NOP=False,
        changed_to_DRAFT=False,
        changed_to_NOP=False,
    )

    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")
