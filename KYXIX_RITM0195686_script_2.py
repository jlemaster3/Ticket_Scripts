#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM0195686 
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, re, time

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0195686\\Script_1_output"

output_log_file = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0195686\\KYXIX_script2_searchRepalce_log.txt"

# Key - Value piar, key string is the source string to saerch for, and the value is what to replace it with.
find_replace_strings = {
    "@MACH1#" : "@MACH7#",
    "@MACH2#" : "@MACH7#",
    "@MACH3#" : "@MACH7#",
    "@MACH4#" : "@MACH7#",
    "@MACH5#" : "@MACH6#",
    "/KYXIX/USOLWKYVM166#" : "@MACH6#",
    "/KYXIX/USOLGWKKFS130#" : "@MACH6#",
    "/KYXIX/UKKFS005#" : "@MACH7#",
    "/KYXIX/UKKFS006#" : "@MACH7#",
    "PHOLIDAY_FEDERAL" : "{E}HOLIDAY_FEDERAL",
    "PKYFDHOL" : "{E}KYFDHOL",
    "PKYPLHOL" : "{E}KYPLHOL",
    "PBUYACCR" : "{E}BUYACCR",
    "PBUYDRCV" : "{E}BUYDRCV",
    "PBUYMRCV" : "{E}BUYMRCV",
    "PBUYTBQR" : "{E}BUYTBQR",
    "PBUYWDEL" : "{E}BUYWDEL",
    "PCLD300" : "{E}CLD300",
    "PCLDNDY" : "{E}CLDNDY",
    "PCLMD350" : "{E}CLMD350",
    "PCLMD700" : "{E}CLMD700",
    "PCLMD701" : "{E}CLMD701",
    "PCLMD702" : "{E}CLMD702",
    "PCLMD703" : "{E}CLMD703",
    "PCLMD704" : "{E}CLMD704",
    "PCLMDA01" : "{E}CLMDA01",
    "PCLMDDS1" : "{E}CLMDDS1",
    "PCLMENCF" : "{E}CLMENCF",
    "PCLMMGEN" : "{E}CLMMGEN",
    "PEDIDMVF" : "{E}EDIDMVF",
    "PELGCOBA" : "{E}ELGCOBA",
    "PELGD096" : "{E}ELGD096",
    "PELGDNRT" : "{E}ELGDNRT",
    "PELGKHBE" : "{E}ELGKHBE",
    "PELGRTRO" : "{E}ELGRTRO",
    "PELGVSTS" : "{E}ELGVSTS",
    "PEND350" : "{E}END350",
    "PENONEMT" : "{E}ENONEMT",
    "PFINHISL" : "{E}FINHISL",
    "PFINHIST" : "{E}FINHIST",
    "PMASSADJ" : "{E}MASSADJ",
    "PMGDD570" : "{E}MGDD570",
    "PMGDM104" : "{E}MGDM104",
    "PMGDM416" : "{E}MGDM416",
    "PMGDM610" : "{E}MGDM610",
    "PMGDNRTC" : "{E}MGDNRTC",
    "PPRVD867" : "{E}PRVD867",
    "PREFW050" : "{E}REFW050",
    "PTPL787B" : "{E}TPL787B",
    "PTPL787E" : "{E}TPL787E",
    "PTPL787H" : "{E}TPL787H",
    "PTPLAND" : "{E}TPLAND",
    "PTPLCCD" : "{E}TPLCCD",
    "PTPLHUD" : "{E}TPLHUD",
    "PTPLM781" : "{E}TPLM781",
    "PTPLM782" : "{E}TPLM782",
    "PTPLM783" : "{E}TPLM783",
    "PTPLM785" : "{E}TPLM785",
    "PTPLM786" : "{E}TPLM786",
    "PTPLMOD" : "{E}TPLMOD",
    "PTPLUHD" : "{E}TPLUHD",
    "PTPLWCD" : "{E}TPLWCD",
    "PTPWJOBS" : "{E}TPWJOBS",
    "PTPWWTCH" : "{E}TPWWTCH",
    "PCNFLMON" : "{E}CNFLMON",
    "PSUQSURQ" : "{E}SUQSURQ",
    "PSUQSURY" : "{E}SUQSURY"
}

commentLinesWith_term = []

exclude_text = []

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


def find_first_nonWhiteSpace (sourceString:str) -> int :
    for i, char in enumerate(sourceString):
        if not char.isspace():
            return i
    return -1


def commentoutLineByTerms (source_string:str, search_term:str, fileindex:int) -> str:
    _source_lines = str(source_string).split('\n')    
    _stream_start_ids:list[int] = []
    _stream_edge_ids:list[int] = []
    _job_line_ids:list[int] = []
    _comment_term_ids:dict[int, list[str]] = {}
    _stream_end_ids:list[int] = []
    for _line_id, _line in enumerate(_source_lines):
        if "SCHEDULE" in str(_line).strip()[0:9]:
            _stream_start_ids.append(_line_id)
        if ':' in _line[0:2]:
            _stream_edge_ids.append(_line_id)
        if (('/' in str(_line).strip()[0:2]) or ('@' in str(_line).strip()[0:2])) or (any(_s in str(_line).strip()[0:5] for _s in ['PRD#', 'NPR#'])) and ('#' in str(_line[2:]).strip()):
            _job_line_ids.append(_line_id)        
        if "END" in str(_line).strip()[0:4] and 'ENDJOIN' not in str(_line).strip():
            _stream_end_ids.append(_line_id)
        for _term in search_term:
            if _term.upper() in _line.upper():
                if _line_id not in _comment_term_ids.keys():
                    _comment_term_ids[_line_id] = []
                _comment_term_ids[_line_id].append(_term)
    
    for _foundCount, (_lineIdx, _foundList) in enumerate(_comment_term_ids.items()):
        if (_lineIdx in _stream_start_ids) or (_lineIdx in _job_line_ids):
            _output_log_holder.append(f" [{fileindex+1}] [{_lineIdx}] - Stream or Job definition line contains term : {_term}")
            return "REMOVE"
        _terms = f"{', '.join(_foundList)}"
        _new_line = re.sub(r'(\S)', r'##\1', _source_lines[_lineIdx], 1)
        _source_lines[_lineIdx] = _new_line
        
        _output_log_holder.append(f" [{fileindex+1}] [{_lineIdx}] - Commenting out line containing term : {_terms}")
    
    return_string = '\n'.join(_source_lines)
    return return_string
    

# output files will be saved in the provided output_path with the same file name as the source
# output file will contain both the orriginal contents and the duplicated/edited contents in the same file.
def process_files (path_list:list, seach_replace_dictionary:dict):
    file_remove_list = []
    for counter, filePath in enumerate(path_list):
        file_name = os.path.basename(filePath)
        _rel_path = os.path.relpath(filePath, source_directory)
        try:    
            output_filePath = filePath
            if os.path.isfile(filePath):
                source_file = open(filePath, "r")
                source_string = source_file.read()
                _skip = False
                for _s in exclude_text:
                    if _s in source_string:
                        _output_log_holder.append (f" [{counter+1}] - Skipping file {file_name}, excluded text '{_s}' was found in source text.")
                        _skip = True
                        break
                _output_log_holder.append(f" [{counter+1}] - Processing File : '{_rel_path}'")
                if len(commentLinesWith_term) >= 1:
                    source_string = commentoutLineByTerms(source_string, commentLinesWith_term, counter)
                    if "REMOVE" in source_string[0:8].upper():
                        _output_log_holder.append (f" [{counter+1}] - Removing File from collection.")
                        _skip = True
                        file_remove_list.append(filePath)
                if _skip == True:
                    _output_log_holder.append('-'*100)
                    continue
                
                for _replace_counter, (search_key, repalce_val) in enumerate(seach_replace_dictionary.items()):
                    if search_key in source_string:
                        source_string = source_string.replace(str(search_key), str(repalce_val))
                        _output_log_holder.append (f" [{counter+1}] [{_replace_counter+1}] - Replaced : '{search_key}' With : '{repalce_val}'")


                with open(output_filePath, "w") as output_file:
                    output_file.write(source_string)
                    _output_log_holder.append(f" [{counter+1}] - Created new file")
        except Exception as e:
            _output_log_holder.append(f" [{counter+1}] - Error processing file : {os.path.basename(filePath)} - {e}")
        
        _output_log_holder.append('-'*100)

    for _fp in file_remove_list:
        os.remove(_fp)
        print (f"removed {_fp}")
                

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # get all jil files in path and all subdirectories
    jil_files_dictionary = get_jil_files(source_directory)
    #collects saerchtersm as a list form source dictionary
    search_terms = list(find_replace_strings.keys())
    #filter list of files down to those that contian the sarch terms
    fitlered_files = files_with_search_terms (jil_files_dictionary, search_terms)

    _output_log_holder.append(f"Running Search and Replace process")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Soruce directory : '{source_directory}'")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of Search and Replace Terms: [{len(search_terms)}]")
    for _term_count, (_term,_replace) in enumerate(find_replace_strings.items()):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term} -> {_replace}")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of Terms to search and Comment out: [{len(commentLinesWith_term)}]")
    for _term_count, _term in enumerate(commentLinesWith_term):
        _output_log_holder.append(f"  [{_term_count+1}] - {_term}")
    _output_log_holder.append('-'*100)
    _output_log_holder.append(f"Number of files found in source Directory: [{len(jil_files_dictionary)}]")
    _output_log_holder.append(f"Number of files found with Search Terms: [{len(fitlered_files)}]")
    _output_log_holder.append('-'*100)
    _output_log_holder.append('')
    _output_log_holder.append('-'*100)

    # create new files that contains a copy of the edited contents
    process_files(
        path_list=fitlered_files, 
        seach_replace_dictionary=find_replace_strings,
    )   

    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")