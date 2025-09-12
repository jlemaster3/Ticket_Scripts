#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM0195686 
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, copy

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0195686\\Script_1_output"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0195686\\KYXIX_script5_addingNote_log.txt"

note_to_add = "### REMOVE THIS NOTE ###"


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


#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # get all jil files in path and all subdirectories
    jil_files_dictionary = get_jil_files(source_directory)
    #filter list of files down to those that contian the sarch terms

    _output_log_holder.append(f"Running File Copy process")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Soruce directory : '{source_directory}'")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of files found in source Directory: [{len(jil_files_dictionary)}]")
    _output_log_holder.append(f"Note being added or removed at end of file: '{note_to_add}'")
    _output_log_holder.append('-'*100)

    for _pathCounter, _fullFilePath in enumerate(jil_files_dictionary) :
        _output_log_holder.append(f" [{_pathCounter+1}] - Processing File : '{os.path.basename(_fullFilePath)}'")
        if os.path.isfile(_fullFilePath):
            _source_file = open(_fullFilePath, "r")
            _source_string = _source_file.read()
            if (note_to_add in _source_string):
                _output_log_holder.append(f"Removing Note form file")
                _source_string = str(copy.deepcopy(_source_string)).strip().replace(note_to_add,"")
            else:
                _output_log_holder.append(f"Adding Note to end of file")
                _source_string = str(copy.deepcopy(_source_string)).strip() + f"\n\n{note_to_add}"
            with open(os.path.join(_fullFilePath), "w") as output_file:
                output_file.write(_source_string)
        _output_log_holder.append('-'*100)
    
    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")