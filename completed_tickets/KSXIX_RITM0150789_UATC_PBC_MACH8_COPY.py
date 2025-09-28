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
source_directory = "C:\\VS_Managed_Accounts\\KSXIX\\UATC\\PBC"

# where the output files shold go, dont use source location
output_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0150789\\PBC_from_UATC"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0150789\\UATC_PBC_MACH8_COPY_log.txt"

# Key - Value piar, key string is the source string to saerch for, and the value is what to replace it with.
find_replace_strings = {
    "@MACH8#" :"@MACH8#"
}

exclude_text = ["@MACH2#", "@MACH3#"]

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


def extract_JS_by_workstation (source_string:str, target_workstation:str="MACH8") -> str:
    _source_lines = str(source_string).split('\n')    
    _stream_start_ids:list[int] = []
    _stream_end_ids:list[int] = []
    _result_lines = []
    for _line_id, _line in enumerate(_source_lines):
        if "SCHEDULE" in str(_line).strip()[0:9]:
            _stream_start_ids.append(_line_id)
        if "END" in str(_line).strip()[0:4] and 'ENDJOIN' not in str(_line).strip():
            _stream_end_ids.append(_line_id)
    for _i in range(len(_stream_start_ids)):
        _start_id = _stream_start_ids[_i]
        _end_id = _stream_end_ids[_i]
        if target_workstation.upper() in _source_lines[_start_id].upper():
            for _keep_id in [_id for _id in range(_start_id,_end_id+1)]:
                _result_lines.append(_source_lines[_keep_id])

    _result_string = '\n'.join(_result_lines)
    return _result_string


def process_files (path_list:list, seach_replace_dictionary:dict, output_path:str, overwrite_original_file:bool=False):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for counter, filePath in enumerate(path_list):
        file_name = os.path.basename(filePath)
        _rel_path = os.path.relpath(filePath, source_directory)
        _output_log_holder.append(f" [{counter+1}] - Processing File : '{_rel_path}'")
        #try:    
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
            for _exclude_counter, _s in enumerate(exclude_text):
                if _s in source_string:
                    _output_log_holder.append (f" [{counter+1}] [{_exclude_counter+1}] - Skipping file, excluded text '{_s}' was found in source text.")
                    _skip = True
                    break
            if _skip == True:
                _output_log_holder.append('-'*100)
                continue
            duplicate_str = str(copy.deepcopy(source_string))
            for _replace_counter, (search_key, repalce_val) in enumerate(seach_replace_dictionary.items()):
                duplicate_str = duplicate_str.replace(str(search_key), str(repalce_val))
                _output_log_holder.append (f" [{counter+1}] [{_replace_counter+1}] - Copied and Replaced : '{search_key}' With : '{repalce_val}'")

            _kept_text = extract_JS_by_workstation(source_string, "MACH8")
            with open(output_filePath, "w") as output_file:
                output_file.write(_kept_text)
                _output_log_holder.append(f" [{counter+1}] - Created new file: {output_file}")
        #except Exception as e:
            #_output_log_holder.append(f" [{counter+1}] - Error processing file : {os.path.basename(filePath)} - {e}")
        
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
        overwrite_original_file=False, 
    )

    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")
