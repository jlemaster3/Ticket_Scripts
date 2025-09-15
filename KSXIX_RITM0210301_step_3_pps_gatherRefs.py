#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM0210301

Created by: Jim Lemaster
Date: 06/26/2024

Purpose: This script is designed to gather all refrences to RCG, Calendars, and NEEDS found in source path.
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0210301\\PPS_copy"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0210301\\KSXIX_PRD-PPS_step3_reffrences_log.txt"

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
def process_files (file_path_list:list):
    _rcg_names = []
    _needs_names = []
    _streamlogon_names = []

    for counter, filePath in enumerate(file_path_list):
        _output_log_holder.append(f" [{counter+1}] - Processing File : '{os.path.basename(filePath)}'")

        _source_file = open(filePath, "r")
        _rawText = _source_file.read()
        _rawLines = str(_rawText).split('\n')    
        
        for _line_id, _line in enumerate(_rawLines):
            if '$RCG' in _line:
                _lineparts = _line.split(' ')
                _idx = _lineparts.index('$RCG')
                _rcgtarget = str(_lineparts[_idx+1]).split('/')[-1]
                if _rcgtarget not in _rcg_names:
                    _rcg_names.append(_rcgtarget)

            if 'NEEDS' in _line[0:10]:
                _lineparts = _line.split(' ')
                _needstarget = str(_lineparts[-1]).split('/')[-1]
                if _needstarget not in _needs_names:
                    _needs_names.append(_needstarget)

            if 'STREAMLOGON' in _line:
                _streamLogon = _line.split(' ')[-1].replace('\"','')
                if _streamLogon not in _streamlogon_names:
                    _streamlogon_names.append(_streamLogon)
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Found the following RCG refrences [{len(_rcg_names)}]: ")
    for _refCount, _ref in enumerate(_rcg_names):
        _output_log_holder.append(f" - [{_refCount+1}] : {_ref}")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Found the following Resource refrences [{len(_needs_names)}]: ")
    for _refCount, _ref in enumerate(_needs_names):
        _output_log_holder.append(f" - [{_refCount+1}] : {_ref}")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Found the following Stream Logon refrences [{len(_streamlogon_names)}]: ")
    for _refCount, _ref in enumerate(_streamlogon_names):
        _output_log_holder.append(f" - [{_refCount+1}] : {_ref}")
                
    
#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # get all jil files in path and all subdirectories
    jil_files_dictionary = get_jil_files(source_directory)

    _output_log_holder.append(f"Running Search and Replace process")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Soruce directory : '{source_directory}'")
    _output_log_holder.append('-'*100)
    
    # create new files that contains a copy of the edited contents
    process_files(
        file_path_list=jil_files_dictionary
    )   

    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")