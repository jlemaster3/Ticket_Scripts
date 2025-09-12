#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM0181157
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, copy

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0176143\\adding_005_006"

# where the output files shold go, dont use source location
output_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0181157\\removed_001_002"


output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0181157\\MSXIX_removeing_old_001_002_ws_log.txt"

search_terms = [
    "@APP1#",
    "@APP2#"
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


def get_stream_bounds (source_string:str, search_terms:list[str]):
    _source_lines = str(source_string).split('\n')    
    _stream_start_ids:list[int] = []
    _stream_edge_ids:list[int] = []
    _stream_end_ids:list[int] = []
    for _line_id, _line in enumerate(_source_lines):
        if "SCHEDULE" in str(_line).strip()[0:9]:
            _stream_start_ids.append(_line_id)
        if ':' in _line[0:2]:
            _stream_edge_ids.append(_line_id)
        if "END" in str(_line).strip()[0:4] and 'ENDJOIN' not in str(_line).strip():
            _stream_end_ids.append(_line_id)
    _cleaned_lines = []
    for _stream_id in range(len(_stream_start_ids)):
        _stream_idx = _stream_start_ids[_stream_id]
        _stream_end = _stream_end_ids[_stream_id]
        _remove = False
        for _t in search_terms:
            if _t in _source_lines[_stream_idx]:
                _output_log_holder.append(f"    - Removing lines betwen [{_stream_idx}] - [{_stream_end}] - Found : '{_t}'")
                _remove = True
        if _remove == False:
            for _i in range(_stream_idx, _stream_end +1):
                _cleaned_lines.append(_source_lines[_i])

    return '\n'.join(_cleaned_lines)


def remove_jobstreams_by_searchTerms (path_list:list,  output_path:str, search_terms:list[str]) :    
    for counter, filePath in enumerate(path_list):
        try:
            file_name = os.path.basename(filePath)
            if os.path.isfile(filePath):
                # output_filePath
                _rel_path = os.path.relpath(filePath, source_directory)
                _target_path = os.path.join(output_path, os.path.dirname(_rel_path))
                if not (os.path.exists(_target_path)):
                    os.makedirs(_target_path)
                output_filePath = os.path.join(_target_path, file_name)    
                #read_sourceFile
                source_file = open(filePath, "r")
                source_string = source_file.read()
                _output_log_holder.append(f" [{counter+1}] - checking file {os.path.basename(filePath)}")
                _cleaned_string = get_stream_bounds( str(copy.deepcopy(source_string)) , search_terms).strip().replace("### REMOVE THIS NOTE ###", "")
                with open(output_filePath, "w") as output_file:
                    output_file.write(_cleaned_string)
                    _output_log_holder.append(f" [{counter+1}] - Created cleaned file: {output_filePath}")
        except Exception as e:
            _output_log_holder.append(f" [{counter+1}] - Error processing file : {os.path.basename(filePath)} - {e}")
        
        _output_log_holder.append('-'*100)      
                        

    
        

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    # get all jil files in path and all subdirectories
    jil_files_dictionary = get_jil_files(source_directory)
    #filter list of files down to those that contian the sarch terms
    fitlered_files = files_with_search_terms (jil_files_dictionary, search_terms)
    # create new files that contains a copy of the edited contents

    _output_log_holder.append(f"Running Search and Replace process")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Source directory : '{source_directory}'")
    _output_log_holder.append(f"Output directory : '{output_directory}'")
    _output_log_holder.append('-'*100)

    _output_log_holder.append(f"Number of Search Terms: [{len(search_terms)}]")
    for _term_count, _term in enumerate(search_terms):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term}")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of files found in source Directory: [{len(jil_files_dictionary)}]")
    _output_log_holder.append(f"Number of files found with 1 or more terms: [{len(fitlered_files)}]")
    _output_log_holder.append('-'*100)

    remove_jobstreams_by_searchTerms(fitlered_files, output_directory, search_terms)


    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))

    print (f"Done processing")