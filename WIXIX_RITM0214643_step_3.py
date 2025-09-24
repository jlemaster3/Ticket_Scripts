#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM0214643 

Set the following streasm to DRAFT:

/WIXIX/WIXODCLPAPP267#/WIXIX/MIS/SETE/SWSYS_REFRESH.@
/WIXIX/WIXODCLPAPP267#/WIXIX/MIS/SETE/SWSYS_REFRESH_PS.@
/WIXIX/WIXODCLPAPP267#/WIXIX/DBA/SETE/SWDBA_CHG_PSWDS.@

'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, copy

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0214643\\SETE_duplicated"

# where the output files shold go, dont use source location
output_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0214643\\SETE_duplicated"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0214643\\WVXIX_RITM0214643_step3_set_DRAFT_log.txt"

Streams_to_DRAFT = [
    "{E}WSYS_REFRESH",
    "{E}WSYS_REFRESH_PS",
    "{E}WDBA_CHG_PSWDS"
]

target_workstations = ['@MACH3#']

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
def files_with_search_terms (file_path_list:list, search_terms:list):
    file_holder = []
    for _fileCounter, file in enumerate(file_path_list):
        if not os.path.exists(file):
            print (f"Can not filter file {os.path.basename}, Unable to find file : {file}")
            continue
        if os.path.isfile(file):
            found_terms = []
            with open(file, 'r') as f:
                for line in f:
                    for _t in search_terms:
                        if (_t in line) and (file not in file_holder):
                            if _t not in found_terms:
                                found_terms.append(_t)
                            
            if len(found_terms) >= 1:
                _output_log_holder.append(f" - [{_fileCounter}] - adding file '{file}' to collection, found term: [{', '.join(found_terms)}]")
                file_holder.append(file)
    return file_holder


def Add_Draft_to_Stream (path_list:list, output_path:str, targetWorkstationList:list[str]=None, targetFolderList:list[str]=None, targetStreamNameList:list[str]=None):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for counter, filePath in enumerate(path_list):
        file_name = os.path.basename(filePath)
        _rel_path = os.path.relpath(filePath, source_directory)
        _output_log_holder.append(f" [{counter+1}] - Processing File : '{_rel_path}'")
        try:
            _target_path = os.path.join(output_path, os.path.dirname(_rel_path))
            if not (os.path.exists(_target_path)):
                os.makedirs(_target_path)
            output_filePath = os.path.join(_target_path, file_name)
            if os.path.isfile(filePath):
                source_file = open(filePath, "r")
                source_string = source_file.read()
                _fileChanged = False

                _source_lines = str(source_string).split('\n')    
                _stream_start_ids:list[int] = []
                _stream_edge_ids:list[int] = []
                _job_line_ids:list[int] = []
                _DESCRIPTION_ids:list[int] = []
                _DRAFT_lines:list[int] = []
                _stream_end_ids:list[int] = []
                for _line_id, _line in enumerate(_source_lines):
                    if "SCHEDULE" in str(_line).strip()[0:9]:
                        _stream_start_ids.append(_line_id)
                    if ':' in _line[0:2]:
                        _stream_edge_ids.append(_line_id)
                    if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) or (any(_s in str(_line).strip()[0:5] for _s in ['PRD#', 'NPR#'])) and ('#' in str(_line[2:]).strip()):
                        _job_line_ids.append(_line_id)
                    if 'DESCRIPTION' in _line:
                        _DESCRIPTION_ids.append(_line_id)
                    if 'DRAFT' in _line:
                        _DRAFT_lines.append(_line_id)
                    if "END" in str(_line).strip()[0:4] and 'ENDJOIN' not in str(_line).strip():
                        _stream_end_ids.append(_line_id)

                for _i in range(len(_stream_start_ids)):
                    _start_id = _stream_start_ids[_i]
                    _end_id = _stream_end_ids[_i]
                    _streamName = _source_lines[_start_id].split('/')[-1]
                    _found_WS_terms = [_tw for _tw in targetWorkstationList if _tw.upper() in _source_lines[_start_id].upper()] if targetWorkstationList != None else None
                    _found_FL_terms = [_tf for _tf in targetFolderList if _tf.upper() in _source_lines[_start_id].upper()] if targetFolderList != None else None
                    _found_SN_terms = [_sn for _sn in targetStreamNameList if _sn.upper() in _streamName.upper()] if targetStreamNameList != None else None
                    _desc_ids =  [num for num in _DESCRIPTION_ids if _start_id <= num <= _end_id]
                    _filter_min_count = [targetWorkstationList != None,targetFolderList != None, targetStreamNameList != None].count(True)
                    _should_add_Draft = False
                    _has_Draft = True if any((_start_id <= _dft_id <=_end_id) for _dft_id in _DRAFT_lines) else False

                    _add_reasons:list[str] = []
                    _skip_reasons:list[str] = []


                    # only check if filters are being used, otehrwise auto add DRAFT unless already has it.
                    if _filter_min_count >= 1:
                        _should_add_Draft = False
                        _filter_coutner = 0
                        if _found_WS_terms != None and len(_found_WS_terms) >= 1:
                            _add_reasons.append(f"Found Workstation reference to : {', '.join(_found_WS_terms)}")
                            _filter_coutner += 1
                        if _found_FL_terms != None and len(_found_FL_terms) >= 1:
                            _add_reasons.append(f"Found Folder reference to : {', '.join(_found_FL_terms)}")
                            _filter_coutner += 1
                        if _found_SN_terms != None and len(_found_SN_terms) >= 1:
                            _add_reasons.append(f"Found Stream Name reference to : {', '.join(_found_SN_terms)}")
                            _filter_coutner += 1

                        if _filter_coutner >= _filter_min_count:
                            _should_add_Draft = True
                        else:
                            _filterCategoryList = []
                            if _found_WS_terms != None : 
                                _filterCategoryList.append(f"Workstation (min 1): {_found_WS_terms}")
                            if _found_FL_terms != None : 
                                _filterCategoryList.append(f"Folder (min 1): {_found_FL_terms}")
                            if _found_SN_terms != None : 
                                _filterCategoryList.append(f"Stream Name (min 1): {_found_SN_terms}")
                            _skip_reasons.append(f"Did not match enough Filters : {', '.join(_filterCategoryList)}")        
                    else:
                        _should_add_Draft = True


                    if _has_Draft == True:
                        _should_add_Draft = False
                        _skip_reasons.append(f"Stream already set to 'DRAFT'")

                    if _should_add_Draft == True:
                        _desc_id = int(_desc_ids[-1]+1)
                        _source_lines.insert(_desc_id, 'DRAFT')
                        _output_log_holder.append(f"    - Adding 'DRAFT' to Job Stream : '{_source_lines[_start_id].split(' ')[-1]}'")
                        for _rc, _r in enumerate(_add_reasons):
                            _output_log_holder.append(f"      - [{_rc+1}] {_r}")
                        _fileChanged = True
                    else:
                        _output_log_holder.append(f"    - Skipping 'DRAFT' for Job Stream : '{_source_lines[_start_id].split(' ')[-1]}'")
                        for _rc, _r in enumerate(_skip_reasons):
                            _output_log_holder.append(f"      - [{_rc+1}] {_r}")

                if _fileChanged == True :
                    _updatedText = '\n'.join(_source_lines)
                    with open(output_filePath, "w") as output_file:
                        output_file.write(_updatedText)
                    _output_log_holder.append(f" [{counter+1}] - Updated File : '{output_filePath}'")
        except Exception as e:
            _output_log_holder.append(f" [{counter+1}] - Error processing file : {os.path.basename(filePath)} - {e}")
        
        _output_log_holder.append('-'*100)


#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    # get all jil files in path and all subdirectories
    jil_files_dictionary = get_jil_files(source_directory)
    #collects saerchtersm as a list form source dictionary
    search_terms = list(Streams_to_DRAFT)
    #filter list of files down to those that contian the sarch terms
    

    _output_log_holder.append(f"Running process - Set Job Streams to DRAFT")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Soruce directory : '{source_directory}'")
    _output_log_holder.append(f"Output directory : '{output_directory}'")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of files found in source Directory: [{len(jil_files_dictionary)}]")
    _output_log_holder.append(f"Number of Search Terms: [{len(Streams_to_DRAFT)}]")
    for _term_count, _term in enumerate(Streams_to_DRAFT):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term}")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of Workstation Terms: [{len(target_workstations)}]")
    for _term_count, _term in enumerate(target_workstations):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term}")
    _output_log_holder.append('-'*100)
    fitlered_files = files_with_search_terms (jil_files_dictionary, Streams_to_DRAFT)
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of files found with Search criteria: [{len(fitlered_files)}]")
    _output_log_holder.append('-'*100)

    Add_Draft_to_Stream (
        path_list=fitlered_files,
        output_path=output_directory,
        targetWorkstationList = target_workstations,
        targetFolderList = None,
        targetStreamNameList = Streams_to_DRAFT
    )


    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")