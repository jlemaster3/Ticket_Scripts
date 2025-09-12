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

# location of source repository to refrence:
source_directory = "C:\VS_Managed_Accounts\MSXIX\TPI\MIS"
source_root_remove = "C:\VS_Managed_Accounts"

# output directory where modicied copies will be stored
output_directory = "C:\Projects\scripts\jil_File_tools\output_path\duplicate_jil_with_note"

# Contains the search string and note to add at the end of each file that contains the matching search string
#
# Key   : String - Source string to search for, case sensitive and can include special characters.
#   - If key is 'NoneType' without the quotes, then note will be added to all files found
#   - Numbers should be encapsulated in double quotes to convert to string.
#   - Does not support compund searching, each key is its own serpate search and add.
#
# Value : String - Target string to replace the source string, can include special characters.
#   -                        - 
find_string_add_note_filter = {
    None : '### - REMOVE THIS LINE - ###'
}

#-------------------------------------------------
#   Functions
#-------------------------------------------------

# collects all files in source folder path that end with items found in file_types list
def get_jil_files (folder_path:str, file_types:list=[".jil"]) ->list:
    """
        Collects all files in source folder_path that end with formates found in file_types list
            folder_path : String - top level directory to search trough
            file_types  : List of Strings - contains teh file formate of file types to search for and use.
                Default : [".jil"]
    """
    path = os.path.abspath(folder_path)
    if not os.path.exists(path):
        print (f"Path not found : {folder_path}")
    file_list = []
    for dir_path, dirs, files in os.walk(path):
        _list = [os.path.join(dir_path, f) for f in files for e in file_types if f.endswith(e)]
        file_list = list(set(file_list + _list))
    return file_list

# loops over each file and removes any file that does not contain atleast one of the provided terms in search_terms list, terms must be string values
def files_with_search_terms (file_path_list:list, search_terms:list=None):
    file_holder = []
    for file in file_path_list:
        if not os.path.exists(file):
            print (f"Can not filter file {os.path.basename}, Unable to find file : {file}")
            continue
        if os.path.isfile(file):
            with open(file, 'r') as f:
                if (search_terms is not None) and (len(search_terms) >= 1):
                    for term in search_terms:
                        if (term is not None) and (term not in f.read()): continue
                        file_holder.append(file)
                else:
                    file_holder.append(file)
    return file_holder

# output files will be saved in the provided output_path with the same file name as the source
# output file will contain both the orriginal contents and the duplicated/edited contents in the same file.
def process_files_add_note_to_end (filePath_list:list, seach_dictionary:dict, output_path:str, source_path_overlap:str = None):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for counter, filePath in enumerate(filePath_list):
        file_name = os.path.basename(filePath)
        source_file_path = os.path.dirname(filePath)
        source_path_minus_overlap = os.path.relpath(source_file_path, source_path_overlap) if source_path_overlap is not None else None
        if (source_path_minus_overlap is not None) and (str(source_path_overlap) != str(source_file_path)):
            output_filePath = os.path.join (output_path, source_path_minus_overlap)
            if not os.path.exists(output_filePath):
                os.mkdir(output_filePath)
        else:
            output_filePath = os.path.join(output_path)
        if os.path.isfile(filePath):
            source_file = open(filePath, "r")
            source_string = source_file.read()
            duplicate_str = str(copy.deepcopy(source_string))
            write_new_file = False
            for search_key, _val in seach_dictionary.items():
                if (search_key is None) or (search_key in source_string):
                    duplicate_str += f"{str(_val)}\n"
                    write_new_file = True
            if write_new_file == True:
                with open(os.path.join(output_filePath, file_name), "w") as output_file:
                    output_file.write(duplicate_str)
            print (f"{counter+1} : {str(write_new_file).ljust(5)} - {os.path.join(output_filePath, file_name)}")
        

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    
    # get all jil files in path and all subdirectories
    jil_files_dictionary = get_jil_files(source_directory)
    #collects saerchtersm as a list form source dictionary
    search_terms = list(find_string_add_note_filter.keys())
    #filter list of files down to those that contian the sarch terms
    fitlered_files = files_with_search_terms (jil_files_dictionary, search_terms)
    # create new files that contains a copy of the edited contents
    process_files_add_note_to_end(fitlered_files, find_string_add_note_filter, output_directory, source_directory)

#-------------------------------------------------
#   Updates / Notes
#-------------------------------------------------

# 2024/10/19 - Scipt created by James Lemaster
# script is used to create duplicate jil file and adds a note to teh end of the file based off the search terms provided.
