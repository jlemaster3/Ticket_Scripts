#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM0195686 
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, re, datetime

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0195686\\Script_1_output"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0195686\\KYXIX_script4_VALIDTO010125_log.txt"

validTo_date = '01/01/2025'

exclude_list = [
"CLD300_MON",
"CLD300_TUE",
"CLD300_WED",
"CLD300_THU",
"CLD300_FRI",
"CLD300_SAT",
"CLD300_SUN",
"CLD350",
"CLD350_SATURDAY",
"CLD350_SUNDAY",
"EDI_DAILY",
"CYCDPSTSOAPREF",
"CLDNDY",
"CYCDCLMENCCLNUP",
"END350_SUN_THU",
"END350_TUE_THU",
"END350_SAT_WED",
"END350_MON_THU",
"FIN_SCHED",
"FIN_INTERFACE",
"FIN_DAILY",
"FIN_HISTORY",
"FIN_RA_HISTORY",
"DLY_ENC_277_AM",
"ND RDLY_ENC_277",
"CTD205",
"CLM_RCYCLEMO2TH",
"CLEANDIR",
"CLMDATE",
"CYCDATE",
"CYCWDATE",
"CYCQDATE",
"MRM_PARM_DATES",
"CYCMDATE",
"PAU_DAILY_PARM",
]

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

def filter_fileNames_exclude (file_path_list:list[str], excludeList:list[str]) -> list[str]:
    file_holder = []
    for counter, filePath in enumerate(file_path_list):
        if not os.path.exists(filePath):
            _output_log_holder.append (f"Can not filter file {os.path.basename}, Unable to find file : {filePath}")
            continue
        _fileName = str(os.path.basename(filePath)).split('.')[0]
        _should_add = True
        for _exclude_coutner, _ex in enumerate(excludeList):
            if _ex.lower() in _fileName.lower():
                _output_log_holder.append (f" [{counter+1}] [{_exclude_coutner+1}] - Skipping file {filePath}, excluded text '{_ex}'")
                _should_add = False
        if _should_add == True:
            file_holder.append(filePath)
    return file_holder

def add_validTo_stream (source_string:str, validToDate:str) -> str:
    _source_lines = str(source_string).split('\n')    
    _stream_start_ids:list[int] = []
    _stream_ON_ids:list[int] = []
    _stream_edge_ids:list[int] = []
    _job_line_ids:list[int] = []
    _stream_end_ids:list[int] = []
    for _line_id, _line in enumerate(_source_lines):
        if "SCHEDULE" in str(_line).strip()[0:9]:
            _stream_start_ids.append(_line_id)
        if 'ON ' in str(_line)[0:9]:
            _stream_ON_ids.append(_line_id)
        if ':' in _line[0:2]:
            _stream_edge_ids.append(_line_id)
        if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) or (any(_s in str(_line).strip()[0:5] for _s in ['PRD#', 'NPR#'])) and ('#' in str(_line[2:]).strip()):
            _job_line_ids.append(_line_id)
        if "END" in str(_line).strip()[0:4] and 'ENDJOIN' not in str(_line).strip():
            _stream_end_ids.append(_line_id)
    for _i in range(len(_stream_start_ids)):
        _start_id = _stream_start_ids[_i]
        _end_id = _stream_end_ids[_i]
        for _on_id in [_id for _id in _stream_ON_ids if _start_id < _id < _end_id]:
            if ('request' in str(_source_lines[_on_id]).lower()) or ("validto" in str(_source_lines[_on_id]).lower()):
                _output_log_holder.append(f"  - skipping file, either assigned 'ON REQUEST' or already assigned earlier VALIDTO date.")
                continue
            else:
                _wordList = _source_lines[_on_id].split()
                _temp = f"  - Changing line [{_on_id}]: {_source_lines[_on_id]} -> "

                if ('ON'.lower() == _wordList[0].lower() and 'RUNCYCLE' in _wordList[1] and len(_wordList) >= 4):
                    _wordList.insert(3, f'VALIDTO {validToDate}')
                    _source_lines[_on_id] = ' '.join(_wordList)
                
                _temp += f"{_source_lines[_on_id]}"
                _output_log_holder.append(_temp)
        _output_log_holder.append('-'*100)
    return_string = '\n'.join(_source_lines)
    return return_string

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
    _output_log_holder.append(f"Terms to Exclude: [{len(exclude_list)}]")
    for _term_count, _term in enumerate(exclude_list):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term}")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of files found in source Directory: [{len(jil_files_dictionary)}]")
    _output_log_holder.append('-'*100)
    
    #collects saerchtersm as a list form source dictionary
    fitlered_files = filter_fileNames_exclude (jil_files_dictionary, exclude_list)
    _output_log_holder.append(f"Number of files found after exclution: [{len(fitlered_files)}]")
    _output_log_holder.append('-'*100)

    overwrite_original_file = True
    for counter, filePath in enumerate(fitlered_files):
        file_name = os.path.basename(filePath)
        _rel_path = os.path.relpath(filePath, source_directory)
        _output_log_holder.append(f" [{counter+1}] - Processing File : '{_rel_path}'")
        
        if os.path.isfile(filePath):
            source_file = open(filePath, "r")
            source_string = source_file.read()
            source_string = add_validTo_stream(source_string, validTo_date)
            
            with open(filePath, "w") as output_file:    
                output_file.write(source_string)

    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")