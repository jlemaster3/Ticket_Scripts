#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM0195686 
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, re

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0195686\\Script_1_output"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0195686\\KYXIX_script3_DOCOMMANDUpdate_log.txt"

find_replace_strings = {
    '\\\"23.45\\\"':"\\\"23.45\\\" 08"
}


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


def update_DOCOMMAND (source_string:str, search_term:str, replace_val:str) -> str:
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
    _2345SearchTerm = '\\\"23.45\\\"'
    for _i in range(len(_stream_start_ids)):
        _start_id = _stream_start_ids[_i]
        _end_id = _stream_end_ids[_i]
        for _dcmd_id in [_id for _id in _DOCOMMAND_lines if _start_id < _id < _end_id]:
            _temp = f"  - Changing line [{_dcmd_id}]: {_source_lines[_dcmd_id]}"
            
            # Specific search and replace term, this is a custom regular exprection search 
            
            _pattern = rf"{re.escape(_2345SearchTerm)}\s*(\d+(\.\d+)?)"
            _source_pattern = re.search(_pattern, _source_lines[_dcmd_id]).group(0)
            _source_lines[_dcmd_id] = _source_lines[_dcmd_id].replace(_source_pattern, replace_val)

            _temp += f" to  {_source_lines[_dcmd_id]}"
            _output_log_holder.append(_temp)
        _output_log_holder.append('-'*100)
    return_string = '\n'.join(_source_lines)
    return return_string

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # get all jil files in path and all subdirectories
    jil_files_dictionary = get_jil_files(source_directory)
    #collects saerchtersm as a list form source dictionary
    search_terms = list(find_replace_strings.keys())
    #collects saerchtersm as a list form source dictionary
    fitlered_files = files_with_search_terms (jil_files_dictionary, search_terms)

    _output_log_holder.append(f"Running Search and Replace process")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Soruce directory : '{source_directory}'")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of Sarch Terms: [{len(search_terms)}]")
    for _term_count, (_term,_replace) in enumerate(find_replace_strings.items()):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term} -> {_replace}")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of files found in source Directory: [{len(jil_files_dictionary)}]")
    _output_log_holder.append(f"Number of files found with Search Terms: [{len(fitlered_files)}]")
    _output_log_holder.append('-'*100)

    overwrite_original_file = True
    for counter, filePath in enumerate(fitlered_files):
        file_name = os.path.basename(filePath)
        _rel_path = os.path.relpath(filePath, source_directory)
        _output_log_holder.append(f" [{counter+1}] - Processing File : '{_rel_path}'")
        
        if os.path.isfile(filePath):
            source_file = open(filePath, "r")
            source_string = source_file.read()
            for _replace_counter, (search_key, repalce_val) in enumerate(find_replace_strings.items()):
                source_string = update_DOCOMMAND(source_string, search_key, repalce_val)
            with open(filePath, "w") as output_file:    
                output_file.write(source_string)

    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")