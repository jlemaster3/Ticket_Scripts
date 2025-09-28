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

import os, shutil, copy

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\VS_Managed_Accounts\\WIXIX\\SETE"

# where the output files shold go, dont use source location
output_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0214643\\SETE_install_2"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0214643\\WVXIX_RITM0214643_install_2_log.txt"

exclude_dir = []

exclusive_fileNames = [
    "D5CLM_DCCI_ADJ",
    "D5CLM_EMAIL_RPT",
    "D5CLM_FLUSH_FIX",
    "D5CLM_SCHD_CLK",
    "D5FIN_AUTO_PYRL",
    "D5FIN_A_FSH_RPT",
    "D5TPL_INS_DISC",
    "D6CLM_205",
    "D7AIM_CDATE",
    "D7AIM_PARMDTVAL",
    "D7BNX_FTP_FILES",
    "D7CLE_2060_ENC",
    "D7CLE_300E",
    "D7CLE_350E",
    "D7CLE_900E",
    "D7CLE_ENCS",
    "D7CLE_MASS_GEN",
    "D7CLE_NDYE",
    "D7CLE_UNDUPE",
    "D7CLM_2060",
    "D7CLM_2061",
    "D7CLM_2062",
    "D7CLM_2064E",
    "D7CLM_300",
    "D7CLM_350",
    "D7CLM_900",
    "D7CLM_BNX_RPT",
    "D7CLM_BNX_RPTS",
    "D7CLM_MSS_PY_VD",
    "D7CLM_NDY",
    "D7CLM_PM_FX_BNX",
    "D7CLM_SCRTS",
    "D7CLM_SUM_CLK_P",
    "D7ENC_DASHBOARD",
    "D7ENC_REPORT",
    "D7ENC_RESPONSE",
    "D7PRV_BIONIX",
    "D7TPL_HR_BIONIX",
    "MREF_0400",
    "MREF_W00",
    "WCLM_EOW",
    "WCLM_EOW",
    "WCLM_FLUSH",
    "WCLM_MASS_SUN",
    "WEDI_M270",
    "WEDI_M276",
    "WEDI_M278",
    "WEDI_MINB270",
    "WEDI_MINBNO270",
    "WEDI_MOUTB",
    "WREF_FW155"
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


def copy_files (sourceFileList:list[str], output_path:str, exclusive_terms:list[str]) -> list[str]:
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    _outputPathList = []
    for counter, filePath in enumerate(sourceFileList):
        try:
            file_name = os.path.basename(filePath)
            _rel_path = os.path.relpath(filePath, source_directory)
            _output_log_holder.append(f" [{counter+1}] - Processing File : '{_rel_path}'")
            _target_path = os.path.join(output_path, os.path.dirname(_rel_path))
            _shouldCopy = False
            os.makedirs(_target_path, exist_ok=True)
            output_filePath = os.path.join(_target_path, file_name)    
            if exclusive_terms != None and len(exclusive_terms) >= 1:
                for _nameTerm in exclusive_terms:
                    if _nameTerm.lower() in filePath.lower():
                        _output_log_holder.append(f" [{counter+1}] - Adding {filePath} to list, found '{_nameTerm}' in file name")
                        _shouldCopy = True
            if (_shouldCopy == True) :
                shutil.copy (filePath, output_filePath)
                _outputPathList.append(output_filePath)
                _output_log_holder.append(f" [{counter+1}] - Copied file to new location: {output_filePath}")
        except Exception as e:
            _output_log_holder.append(f" [{counter+1}] - Error processing file : {os.path.basename(filePath)} - {e}")
        _output_log_holder.append('-'*100)

    return _outputPathList


def toggle_EOF_commnet (fullFilePath:str, commnet:str="REMOVE THIS LINE"):
    #try:
        _comment = commnet if commnet.startswith('#') else f"### {commnet} ###"
        with open(fullFilePath, 'r') as f:
            lines = f.readlines()

        if not lines:  # Handle empty file
            _output_log_holder.append(f"File '{fullFilePath}' is empty. No line to toggle.")
            return

        # Find the last non-empty line
        last_non_empty_line_index = -1
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip():  # Check if the line is not just whitespace
                last_non_empty_line_index = i
                break

        if last_non_empty_line_index == -1:  # Only empty lines in the file
            _output_log_holder.append(f"File '{fullFilePath}' contains only empty lines. No line to toggle.")
            return

        last_line = lines[last_non_empty_line_index].strip()

        if _comment in last_line:
            # Remove last line if it is a Commented line
            lines = [item for item in lines if _comment not in item]
            _output_log_holder.append(f"Comment Removed to end of file : '{fullFilePath}'")
        else:
            # Add Commented line to end of file
            lines.append(f"\n{_comment}")
            _output_log_holder.append(f"Comment Added to end of file : '{fullFilePath}'")

        with open(fullFilePath, 'w') as f:
            f.writelines(lines)

    #except FileNotFoundError:
    #    _output_log_holder.append(f"Error: File '{fullFilePath}' not found.")
    #except Exception as e:
    #    _output_log_holder.append(f"An error occurred: {e}")

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
    _output_log_holder.append(f"Number of exclusive File Names terms: [{len(exclusive_fileNames)}]")
    for _term_count, _term in enumerate(exclusive_fileNames):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term}")
    _output_log_holder.append(f"Number of excluded terms: [{len(exclude_text)}]")
    for _term_count, _term in enumerate(exclude_text):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term}")
    _output_log_holder.append('-'*100)
    
    #copiedPathList = copy_files(
    #    sourceFileList = jil_files_dictionary,
    #    output_path= output_directory,
    #    exclusive_terms = exclusive_fileNames,
    #)
    #_output_log_holder.append('-'*100)
    #_output_log_holder.append(f"Total number of files copied: [{len(copiedPathList)}]")

    _toggle_files_dictionary = get_jil_files(output_directory)
    for _pathCounter, _fullFilePath in enumerate(_toggle_files_dictionary) :
        toggle_EOF_commnet (_fullFilePath)

    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")

