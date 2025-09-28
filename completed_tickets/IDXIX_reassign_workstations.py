#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Searches a given directory for all jil files that contain a search values found in find_replace_strings dictionary object.

The Keys are strings to search for, and the values are what replaces those strings in the duplciate text.
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, copy

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\VS_Code_Repo\IDXIX\Jobs"

# where the output files shold go, dont use source location
output_directory = "C:\Projects\scripts\jil_File_tools\output_path\duplicate_items_to_workstation"

# Key - Value piar, key string is the source string to saerch for, and the value is what to replace it with.
find_replace_strings = {
    "/IDXIX/MIS/DEV/IDSSIS#" :"@ETL#",
    "/IDXIX/MIS/DEV/IDSSRS#" :"@SRS#",
    "/IDXIX/MIS/DEV/IDCYPRESS#" :"@CYPRS#"
}

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
    string_with_draft = '\n'.join(_lines)
    return string_with_draft

# output files will be saved in the provided output_path with the same file name as the source
# output file will contain both the orriginal contents and the duplicated/edited contents in the same file.
def process_files (path_list:list, seach_replace_dictionary:dict, output_path:str, overwrite_original:bool=True, keep_original:bool=False, original_to_DRAFT:bool=False):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for counter, filePath in enumerate(path_list):
        file_name = os.path.basename(filePath)
        if overwrite_original == False:
            output_filePath = os.path.join(output_path, file_name)    
        else:
            output_filePath = filePath
        if os.path.isfile(filePath):
            source_file = open(filePath, "r")
            source_string = source_file.read()
            duplicate_str = str(copy.deepcopy(source_string))
            for search_key, repalce_val in seach_replace_dictionary.items():
                duplicate_str = duplicate_str.replace(str(search_key).upper(), str(repalce_val).upper())
            with open(output_filePath, "w") as output_file:
                if keep_original == True:
                    if original_to_DRAFT == True:
                        output_file.write(add_Draft_to_String(source_string))
                    else:
                        output_file.write(source_string)
                    output_file.write("\n\n")
                output_file.write(duplicate_str)
            print (f"{counter+1} - {output_filePath}")
        

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
    # create new files that contains a copy of the edited contents
    process_files(fitlered_files, find_replace_strings, output_directory)

#-------------------------------------------------
#   Updates / Notes
#-------------------------------------------------

# 2024/08/30 - Scipt created by James Lemaster
# script is used to create duplicate Job Streams and all Jobs within for workstation migration.
