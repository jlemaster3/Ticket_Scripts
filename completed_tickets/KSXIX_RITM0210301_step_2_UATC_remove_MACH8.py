#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM0210301
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
source_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0210301\\UATC_copy"

output_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0210301\\UATC_copy"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0210301\\KSXIX_UATC_step2_remove_MACH8_log.txt"

target_workstation = ['MACH8']

# contains output Log strings.
_output_log_holder = []


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


def removeJobStreams (source_string:str, target_workstation:list[str]) -> str:
    _source_lines = str(source_string).split('\n')    
    _stream_start_ids:list[int] = []
    _stream_edge_ids:list[int] = []
    _job_line_ids:list[int] = []
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

    _new_line_list = []
    for _i in range(len(_stream_start_ids)):
        _start_id = _stream_start_ids[_i]
        _end_id = _stream_end_ids[_i]
        if all(_tw.upper() not in _source_lines[_start_id].upper() for _tw in target_workstation):
            _new_line_list.extend(_source_lines[_start_id:_end_id+1])
    
    updatedString = '\n'.join(_new_line_list)
    return updatedString


# output files will be saved in the provided output_path with the same file name as the source
# output file will contain both the orriginal contents and the duplicated/edited contents in the same file.
def remove_JobStream_By_Workstaions (path_list:list, targetWorkstation:list[str], output_path:str):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for counter, filePath in enumerate(path_list):
        file_name = os.path.basename(filePath)
        _rel_path = os.path.relpath(filePath, source_directory)
        _output_log_holder.append(f" [{counter+1}] - Processing File : '{_rel_path}'")
        try:    
            _target_path = os.path.join(output_path, os.path.dirname(_rel_path))
            if not (os.path.exists(_target_path)):
                os.makedirs(_target_path)
            output_filePath = os.path.join(_target_path, file_name)    
            if os.path.isfile(filePath):
                source_file = open(filePath, "r")
                source_string = source_file.read()
                _updatedText = removeJobStreams (source_string, targetWorkstation)            
                with open(output_filePath, "w") as output_file:
                    output_file.write(_updatedText)
                    _output_log_holder.append(f" [{counter+1}] - Updated File")
        except Exception as e:
            _output_log_holder.append(f" [{counter+1}] - Error processing file : {os.path.basename(filePath)} - {e}")
        
        _output_log_holder.append('-'*100)


#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # get all jil files in path and all subdirectories
    jil_files_dictionary = get_jil_files(source_directory)
    #filter list of files down to those that contian the sarch terms
    fitlered_files = files_with_search_terms (jil_files_dictionary, target_workstation)

    _output_log_holder.append(f"Running Search and Replace process")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Soruce directory : '{source_directory}'")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of Search Terms: [{len(target_workstation)}]")
    for _term_count, _term in enumerate(target_workstation):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term}")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of files found in source Directory: [{len(jil_files_dictionary)}]")
    _output_log_holder.append(f"Number of files found with Search Terms: [{len(fitlered_files)}]")
    _output_log_holder.append('-'*100)


    # create new files that contains a copy of the edited contents
    remove_JobStream_By_Workstaions(
        path_list=fitlered_files, 
        targetWorkstation = target_workstation,
        output_path=output_directory, 
    )

    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")