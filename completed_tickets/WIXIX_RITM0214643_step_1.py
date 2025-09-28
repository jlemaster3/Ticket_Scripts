#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM0214643

Copy working files from source WIXIX\\SETE to working directory if the file does not containe any of the following:

    "D5SYS_SMON", "D7SYS_AM", "D7SYS_NDY", "D7SYS_SMND", "MSYS_PATCH", "WSYS_SPCE"
    
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, shutil

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\VS_Managed_Accounts\\WIXIX\\SETE"

# where the output files shold go, dont use source location
output_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0214643\\SETE_Copy"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0214643\\WVXIX_RITM0214643_step1_copy_log.txt"

exclude_dir = []

exclude_fileNames_with = [
    "D5SYS_SMON", 
    "D7SYS_AM", 
    "D7SYS_NDY", 
    "D7SYS_SMND", 
    "MSYS_PATCH", 
    "WSYS_SPCE"
]

exclude_text = ['#MACH3@', 'WIXODCLPAPP267']

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


def copy_files (sourceFileList:list[str], output_path:str, exclude_dir:list[str], exclude_filenames:list[str], exclude_terms:list[str]) -> list[str]:
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    _outputPathList = []
    for counter, filePath in enumerate(sourceFileList):
        file_name = os.path.basename(filePath)
        _rel_path = os.path.relpath(filePath, source_directory)
        _output_log_holder.append(f" [{counter+1}] - Processing File : '{_rel_path}'")
        _target_path = os.path.join(output_path, os.path.dirname(_rel_path))
        _shouldCopy = True
        try:  
            if not (os.path.exists(_target_path)):
                os.makedirs(_target_path)
            output_filePath = os.path.join(_target_path, file_name)    
            for _term in exclude_dir:
                if _term in filePath:
                    _output_log_holder.append(f" [{counter+1}] - Removing {filePath} from list, found directory : '{_term}' in folder path")
                    _shouldCopy = False
            if exclude_filenames != None and len(exclude_filenames) >= 1:
                for _nameTerm in exclude_filenames:
                    if _nameTerm.lower() in filePath.lower():
                        _output_log_holder.append(f" [{counter+1}] - Removing {filePath} from list, found '{_nameTerm}' in file name")
                        _shouldCopy = False
            if (_shouldCopy == True) :
                with open(filePath, 'r') as f:
                    for _lineCounter, _line in enumerate (f):
                        for _term in exclude_terms:
                            if _term in _line:
                                _output_log_holder.append(f" [{counter+1}] - Removing {filePath} from list, found : '{_term}' on line [{_lineCounter}]")
                                _shouldCopy = False
            if (_shouldCopy == True) :
                shutil.copy (filePath, output_filePath)
                _outputPathList.append(output_filePath)
                _output_log_holder.append(f" [{counter+1}] - Copied file to new location: {output_filePath}")
        except Exception as e:
            _output_log_holder.append(f" [{counter+1}] - Error processing file : {os.path.basename(filePath)} - {e}")
        _output_log_holder.append('-'*100)

    return _outputPathList

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
    _output_log_holder.append(f"Output directory : '{output_directory}'")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of files found in source Directory: [{len(jil_files_dictionary)}]")
    _output_log_holder.append(f"Number of excluded directories: [{len(exclude_dir)}]")
    for _term_count, _term in enumerate(exclude_dir):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term}")
    _output_log_holder.append(f"Number of excluded File Names terms: [{len(exclude_fileNames_with)}]")
    for _term_count, _term in enumerate(exclude_fileNames_with):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term}")
    _output_log_holder.append(f"Number of excluded terms: [{len(exclude_text)}]")
    for _term_count, _term in enumerate(exclude_text):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term}")
    _output_log_holder.append('-'*100)
    

    
    copiedPathList = copy_files(
        sourceFileList = jil_files_dictionary,
        output_path= output_directory,
        exclude_dir= exclude_dir,
        exclude_filenames = exclude_fileNames_with,
        exclude_terms=exclude_text
    )
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Total number of files copied: [{len(copiedPathList)}]")

    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")