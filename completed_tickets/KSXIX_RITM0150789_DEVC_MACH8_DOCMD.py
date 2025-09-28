#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM00150789
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, copy

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0150789\\new_workstation\\DEVC"

# where the output files shold go, dont use source location
output_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0150789\\docommand\\DEVC"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0150789\\DEVC_MACH8_DOCOMMAND_log.txt"

# Key - Value piar, key string is the source string to saerch for, and the value is what to replace it with.
find_replace_strings = {
    "/export/customer/kscmnc/test/job" :"{JOBDIR}"
}

exclude_text = ["@MACH2#", "@MACH3#" ]

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


def update_MACH_NUM_DOCOMMAND (source_string:str, search_term:str, replace_val:str, target_workstation:str="MACH8") -> str:
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
                _source_lines[_dcmd_id] = _source_lines[_dcmd_id].replace(search_term, replace_val)
                _temp += f" to  {_source_lines[_dcmd_id]}"
                _output_log_holder.append(_temp)
    string_with_NOP = '\n'.join(_source_lines)
    return string_with_NOP


def process_files (path_list:list, seach_replace_dictionary:dict, output_path:str, overwrite_original_file:bool=False, keep_original_Stream:bool=False):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for counter, filePath in enumerate(path_list):
        #if counter >= 6: break  ## line is used for limiting fwhile developing script, comment out when running full.
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
                    
                    #update DOCOMMAND for MACH8 machines only
                    duplicate_str = update_MACH_NUM_DOCOMMAND(duplicate_str, search_key, repalce_val, target_workstation= 'MACH8')
                    
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
    _output_log_holder.append(f"Number of Sarch Terms: [{len(search_terms)}]")
    for _term_count, _term in enumerate(search_terms):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term}")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of files found in source Directory: [{len(jil_files_dictionary)}]")
    _output_log_holder.append(f"Number of files found with Search Terms: [{len(fitlered_files)}]")

    # create new files that contains a copy of the edited contents
    process_files(
        path_list=fitlered_files, 
        seach_replace_dictionary=find_replace_strings, 
        output_path=output_directory, 
        overwrite_original_file=True, 
        keep_original_Stream=False
    )

    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")
