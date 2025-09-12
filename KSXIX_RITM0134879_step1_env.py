#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM0134879
Replace  DEVB/SITB/UATB/DEVC/SITC/UATC/PPS/PROD with {ENV}
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, copy

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\VS_Managed_Accounts\\KSXIX"

# where the output files shold go, dont use source location
output_directory = "C:\\Projects\\scripts\\jil_File_tools\\output_path\\KSXIX_RITM0134879"

output_log_file = os.path.join(output_directory, 'env_change_log.txt')

# Key - Value piar, key string is the source string to saerch for, and the value is what to replace it with.
find_replace_strings = {
    "DEVB" :"{ENV}",
    "SITB" :"{ENV}",
    "UATB" :"{ENV}",
    "DEVC" :"{ENV}",
    "SITC" :"{ENV}",
    "UATC" :"{ENV}",
    "PPS" :"{ENV}",
    "PROD" :"{ENV}"
}

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


def process_files (source_path:str, seach_replace_dictionary:dict, output_path:str, overwrite_original:bool=False, keep_original:bool=False, original_to_DRAFT:bool=False):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    path = os.path.abspath(source_path)
    if not os.path.exists(path):
        print (f"Path not found : {source_path}")
        return None
    _file_list = get_jil_files(source_path)
    _log_holder = [f"Found a total of [{len(_file_list)}] in source root '{source_path}'"]
    _found_data = {}
    for _file_cntr, file_path in enumerate(_file_list):
        file_name = os.path.basename(file_path)
        _repath = os.path.relpath(os.path.abspath(os.path.dirname(file_path)),os.path.abspath(source_directory))
        _output_filePath = os.path.join(output_path, _repath)
        if overwrite_original == False:
            output_filePath = os.path.join(_output_filePath, file_name)    
        else:
            output_filePath = file_path
        if os.path.isfile(file_path):
            source_lines = None
            with open(file_path, 'r') as file:
                source_lines = file.readlines()
            if source_lines is not None:
                _found_change = False
                for _id, _line in enumerate(source_lines):    
                    if (str(_line).upper().find('DOCOMMAND') != -1):
                        _temp_line = copy.deepcopy(_line)
                        for search_key, repalce_val in seach_replace_dictionary.items():
                            _temp_line = str(_temp_line).replace(str(search_key).upper(), str(repalce_val).upper(),-1)
                        if _temp_line.lower().strip() != _line.lower().strip():
                            source_lines[_id] = _temp_line
                            _found_change = True
                if _found_change == True:
                    string_with_changes = ''.join(source_lines)
                    _found_data[output_filePath] = string_with_changes                    
    _changed_file_cntr_len = len(str(len(_found_data.keys())))
    for output_counter, (_output_filepath, _output_string) in enumerate(_found_data.items()):        
        try:
            output_dir = os.path.dirname(_output_filepath)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            with open(_output_filepath, "w") as output_file:
                output_file.write(_output_string)
            _log_holder.append(f"[{str(output_counter+1).zfill(_changed_file_cntr_len)}] -  Updated  {_output_filepath}")
        except Exception as e:
            _log_holder.append(f"[{str(output_counter+1).zfill(_changed_file_cntr_len)}] -  Unable to make change to {_output_filepath} : {e}")
    return "\n".join(_log_holder)

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    
    _update_log = process_files(source_directory, find_replace_strings, output_directory, overwrite_original=True)


    _output_log_holder = []
    _output_log_holder.append(f"Soruce directory : '{source_directory}'")
    _output_log_holder.append(f"Output directory : '{output_directory}'")
    _output_log_holder.append(f"Overwrite Orriginal Files : 'True'")
    _output_log_holder.append(f"Search / Replace Values:")
    for _cntr,(_key,_val) in enumerate(find_replace_strings.items()):
        _output_log_holder.append(f"[{_cntr+1}]{_key} : {_val}")
    _output_log_holder.append('-'*100)
    _output_log_holder.extend(_update_log.split('\n'))

    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")

