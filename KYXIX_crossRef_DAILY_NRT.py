#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''

'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, copy

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\VS_Managed_Accounts\\KYXIX\\PROD"

# where the output files shold go, dont use source location
output_directory = "C:\\Projects\\scripts\\jil_File_tools\\output_path\\KYXIX_temp"

output_log_file = "C:\\Projects\\scripts\\jil_File_tools\\output_path\\KYXIX_temp\\kyxix_temp_log.txt"


# contains output Log strings.
_output_log_holder = []


#-------------------------------------------------
#   Functions
#-------------------------------------------------

# collects all files in source folder path that end with items found in file_types list
def get_jil_files (source_path:str, file_types:list=['.jil', '.job'])->list[str]|None:
    path = os.path.abspath(source_path)
    if not os.path.exists(path):
        _output_log_holder.append(f"WARNING - Path not found : {source_path}")
        return None
    file_list = []
    for root, _, files in os.walk(path):
        for file in files:
            if any(file.lower().endswith(ft) for ft in file_types):
                file_list.append(os.path.join(root, file))
    return file_list


# loops over each file and removes any file that does not contain at least one of the provided terms in search_terms list, terms must be string values
def files_with_filter_terms (file_path_list:list, search_terms:list):
    file_holder = []
    for file in file_path_list:
        if not os.path.exists(file):
            _output_log_holder.append(f"WARNING - Can not filter file {os.path.basename}, Unable to find file : {file}")
            continue
        if os.path.isfile(file):
            with open(file, 'r') as f:
                for line in f:
                    if any(_t in line for _t in search_terms) and (file not in file_holder):
                        file_holder.append(file)
    return file_holder


def get_paths_by_filter_terms (file_path_list:list, search_terms:list):
    path_holder = []
    for _path in file_path_list:
        if any(_t in os.path.basename(_path) for _t in search_terms):
            path_holder.append(_path)
    return path_holder

def get_diff_filePaths_A_B (source_list_A:list[str], source_list_B:list[str]) ->list[str]:
    _diff_list = []
    for _filePath_A in source_list_A:
        _fileName_A = os.path.basename(_filePath_A)
        if all(_fileName_A.upper() != os.path.basename(_filePath_B).upper() for _filePath_B in source_list_B):
            _diff_list.append(_filePath_A)
    return _diff_list


def get_same_fileNames_A_B (source_list_A:list[str], source_list_B:list[str])->list[str]:
    _same_list = []
    for _filePath_A in source_list_A:
        _fileName_A = os.path.basename(_filePath_A)
        if any(_fileName_A.upper() == os.path.basename(_filePath_B).upper() for _filePath_B in source_list_B):
            _same_list.append(_fileName_A)
    return _same_list


def get_merged_unique_list (source_list_A:list[str], source_list_B:list[str])->list[str]:
    _merged_list = []
    for _path in source_list_A + source_list_B:  
        if _path not in _merged_list:  
            _merged_list.append(_path)
    return _merged_list

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    filter_pass_1 = [
        "{E}BUYTBQR",
        "{E}ELGKHBE",
        "{E}ELGRTRO",
        "RCNFLMON",
        "{E}ELGDNRT"
    ]

    filter_pass_2 = [
        "ELG_DAILY_NRT"
    ]

    filter_pass_3 = [
        "recon",
        "RECON"
    ]

    # get all jil files in path and all subdirectories
    jil_files_dictionary = get_jil_files(source_directory)

    fitlered_files_1 = files_with_filter_terms (jil_files_dictionary, filter_pass_1)
    fitlered_files_2 = files_with_filter_terms (fitlered_files_1, filter_pass_2)
    fitlered_files_3 = files_with_filter_terms (fitlered_files_1, filter_pass_3)
    
    filesNames_filter_2 = get_paths_by_filter_terms (jil_files_dictionary, filter_pass_2)
    filesNames_filter_3 = get_paths_by_filter_terms (jil_files_dictionary, filter_pass_3)

    _merged_listsd_2_3 = get_merged_unique_list(fitlered_files_2, fitlered_files_3)
    _filter_1_minus_2_3 = get_diff_filePaths_A_B (fitlered_files_1, _merged_listsd_2_3)

    

    _output_log_holder.append(f"Running Search")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Soruce directory : '{source_directory}'")
    _output_log_holder.append(f"Output directory : '{output_directory}'")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of Filter 1 Terms: [{len(filter_pass_1)}]")
    for _term_count, _term in enumerate(filter_pass_1):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term}")
    _output_log_holder.append(f"Number of Filter 2 Terms: [{len(filter_pass_2)}]")
    for _exclude_count, _exclude in enumerate(filter_pass_2):
        _output_log_holder.append(f"  [{_exclude_count+1}] - {_exclude}")
    _output_log_holder.append(f"Number of Filter 3 Terms: [{len(filter_pass_3)}]")
    for _exclude_count, _exclude in enumerate(filter_pass_3):
        _output_log_holder.append(f"  [{_exclude_count+1}] - {_exclude}")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of files found in source Directory: [{len(jil_files_dictionary)}]")
    _output_log_holder.append(f"Number of files found with Filter 1 Terms: [{len(fitlered_files_1)}]")
    _output_log_holder.append(f"Number of files found with Filter 1 and Filter 2 Terms: [{len(fitlered_files_2)}]")
    _output_log_holder.append(f"Number of files found with Filter 1 and Filter 3 Terms: [{len(fitlered_files_3)}]")
    _output_log_holder.append(f"Number of files found with Filter 1 minus Filters 2 and 3 Terms: [{len(_filter_1_minus_2_3)}]")
    _output_log_holder.append(f"Number of files found with Filter 2 terms in file name: [{len(filesNames_filter_2)}]")
    _output_log_holder.append(f"Number of files found with Filter 3 terms in file name: [{len(filesNames_filter_3)}]")
    _output_log_holder.append('-'*100)
    _output_log_holder.append('')
    _output_log_holder.append(f"Files found with Filter 1 Terms: [ {', '.join([_s for _s in filter_pass_1])} ]")
    _output_log_holder.append('')
    for _filteredPath_count, _filteredPath in enumerate(fitlered_files_1):
        _output_log_holder.append(f"  [{_filteredPath_count+1}] - {_filteredPath}")
    _output_log_holder.append('')
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Files found with Filter 2 Terms: [ {', '.join([_s for _s in filter_pass_2])} ]")
    _output_log_holder.append('')
    for _filteredPath_count, _filteredPath in enumerate(fitlered_files_2):
        _output_log_holder.append(f"  [{_filteredPath_count+1}] - {_filteredPath}")
    _output_log_holder.append('')
    _output_log_holder.append('-'*100)
    _output_log_holder.append('')
    _output_log_holder.append(f"Files found with Filter 3 Terms: [ {', '.join([_s for _s in filter_pass_3])} ]")
    _output_log_holder.append('')
    for _filteredPath_count, _filteredPath in enumerate(fitlered_files_3):
        _output_log_holder.append(f"  [{_filteredPath_count+1}] - {_filteredPath}")
    _output_log_holder.append('')
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Files found with 1 terms minus those found with Filters 2 and 3 Terms:")
    _output_log_holder.append('')
    for _filteredPath_count, _filteredPath in enumerate(_filter_1_minus_2_3):
        _output_log_holder.append(f"  [{_filteredPath_count+1}] - {_filteredPath}")
    _output_log_holder.append('')
    _output_log_holder.append('-'*100)
    _output_log_holder.append('')
    _output_log_holder.append(f"Files found with Filter 2 Terms in file path or file name: [ {', '.join([_s for _s in filter_pass_2])} ]")
    _output_log_holder.append('')
    for _filteredPath_count, _filteredPath in enumerate(filesNames_filter_2):
        _output_log_holder.append(f"  [{_filteredPath_count+1}] - {_filteredPath}")
    _output_log_holder.append('')
    _output_log_holder.append('-'*100)
    _output_log_holder.append('')
    _output_log_holder.append(f"Files found with Filter 3 Terms in file path or file name: [ {', '.join([_s for _s in filter_pass_3])} ]")
    _output_log_holder.append('')
    for _filteredPath_count, _filteredPath in enumerate(filesNames_filter_3):
        _output_log_holder.append(f"  [{_filteredPath_count+1}] - {_filteredPath}")
    _output_log_holder.append('')


    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")
