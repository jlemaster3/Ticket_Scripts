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
source_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0150789\\new_workstation\\UATB"

# where the output files shold go, dont use source location
output_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0150789\\new_workstation\\UATB"

# file types to search for and use
file_types = [".jil"]


note_to_add = "### REMOVE THIS NOTE ###"


# Key - Value piar, key string is the source string to saerch for, and the value is what to replace it with.
find_replace_strings = {
    note_to_add :"",
}


#-------------------------------------------------
#   Functions
#-------------------------------------------------

# collects all files in source folder path that end with items found in file_types list
def get_jil_files (folder_path:str):
    path = os.path.abspath(folder_path)
    if not os.path.exists(path):
        print (f"Path not found : {folder_path}")
    file_list = []
    for dir_path, dirs, files in os.walk(path):
        file_list = list(set(file_list + [os.path.join(dir_path, f) for f in files for e in file_types if f.endswith(e)]))
    return file_list

def add_note (_fullFilePath:list, not_to_add:dict, output_path:str):
    if os.path.isfile(_fullFilePath):
        _file_name = os.path.basename(_fullFilePath)
        _source_file = open(_fullFilePath, "r")
        _changed_string = str(copy.deepcopy(_source_file.read())).strip() + f"\n\n{note_to_add}"
        
        with open(os.path.join(_output_folderPath, _file_name), "w") as output_file:
            output_file.write(_changed_string)


def Remove_note (_fullFilePath:list, seach_replace_dictionary:dict, output_path:str):
    if os.path.isfile(_fullFilePath):
        _file_name = os.path.basename(_fullFilePath)

        source_file = open(_fullFilePath, "r")
        source_string = source_file.read()
        duplicate_str = ""
        for search_key, repalce_val in seach_replace_dictionary.items():
            duplicate_str = str(copy.deepcopy(source_string)).strip().replace(str(search_key), str(repalce_val))
        with open(os.path.join (output_path, _file_name), "w") as output_file:
            output_file.write(duplicate_str)

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    # get all jil files in path and all subdirectories
    jil_files_dictionary = get_jil_files(source_directory)
    # collects saerchtersm as a list form source dictionary
    
    for _pathCounter, _fullFilePath in enumerate(jil_files_dictionary) :
        if os.path.isfile(_fullFilePath):
            _file_name = os.path.basename(_fullFilePath)
            _sub_path = os.path.relpath(os.path.dirname(_fullFilePath), source_directory)
            _output_folderPath = os.path.join(output_directory, _sub_path)

            if not os.path.exists(_output_folderPath):
                os.makedirs(_output_folderPath)
            
            
            #add_note (_fullFilePath, note_to_add, _output_folderPath)
            Remove_note (_fullFilePath, find_replace_strings, _output_folderPath)

            print (_pathCounter, os.path.join(_output_folderPath, _file_name))

#-------------------------------------------------
#   Updates / Notes
#-------------------------------------------------

# 2024/08/30 - Scipt created by James Lemaster
# script is used to create duplicate Job Streams and all Jobs within for workstation migration.