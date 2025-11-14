#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, sys, copy, re
from datetime import datetime as dt

## Imports ToolBox, and log
_curr_dir = os.path.dirname(os.path.abspath(__file__))
_prnt_dir = os.path.dirname(_curr_dir)
sys.path.append(_prnt_dir)
from ToolBox_ECS_V1 import *

#-------------------------------------------------
#   Steps
#-------------------------------------------------

def Action_Duplicate_IWS_nodes_to_New_Agent (
    Output_Folder_path:str ,
    Search_Replace_Terms:dict[str,str],
    quite_logging:bool = True
):
    """For each file in source path, find all IWS assets, and duplicate them, then preform a search and replace on teh duplicated assest's text.
    Append the duplcated and udpated text to the current file, and save a copy of the file to a new location for review."""
    
    log.info (f"Total number of search terms to evaluate : [{len(Search_Replace_Terms.keys())}]")
    log.info(f"Search and Duplicate values : [{len(Search_Replace_Terms.keys())}]", data=Search_Replace_Terms)
    log.blank('-'*100)
    _udpated_files:list[str] = []
    for _file_index, _file_node in enumerate(ToolBox.JIL_file_nodes):
        _file_node.open_file(
            enable_post_porcesses=False,
            quite_logging=True
        )
        _has_been_updated:bool = False
        _copy_of_text:str = copy.deepcopy(_file_node._source_file_text) or ''
        
        for _search, _replace in Search_Replace_Terms.items():
            _replaced = _copy_of_text.replace(_search,_replace)
            if _replaced != _copy_of_text:
                _udpated_files.append(_file_node.relFilePath)
                log.debug (f"[{len(_udpated_files)}] - Found search term '{_search}', duplciateing Job Stream and Jobs and repalcing with '{_replace}'")
                _copy_of_text = _replaced
                _has_been_updated = True
        if _has_been_updated == True:
            if isinstance(_copy_of_text, str):
                _file_node._modified_file_text = f"{_file_node._modified_file_text}\n\n{_copy_of_text}"
                log.debug (f"Adding duplciates to File : '{_file_node.relFilePath}'")
            _file_node.save_File(
                outputFolder= Output_Folder_path,
                useRelPath=True,
                quite_logging=False
            )
            log.blank('-'*100)    
        _file_node.close_file(
            quite_logging = True
        )
        
    log.info(f"Found a total of [{len(_udpated_files)}] files that contained 1 or more of the [{len(Search_Replace_Terms.keys())}] search terms and where udpated with duplciated Job Streams and/or Jobs.")
    log.blank('\n'.join([f"[{_c+1}] '{_nf_path}'" for _c, _nf_path in enumerate(_udpated_files)]))


#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    Contract_Name = 'ORXIX'
    Ticket_Number = 'RITM0255249'
    Source_Path = 'C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\ORXIX\\'
    Working_Path = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\"
    Output_folder_name = 'EDIT_Duplcate'

    
    _start_time = dt.now()
    
    _working_path:str = os.path.join (Working_Path, f"{Contract_Name}_{Ticket_Number}")
    # Capture current date and time when script begins
    log.init_logger(log_folder=_working_path, log_file=f"{Contract_Name}_{Ticket_Number}_{_start_time.strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {Ticket_Number} under contract : {Contract_Name}")
    _output_path:str = os.path.join (_working_path, Output_folder_name)

    ToolBox.collect_files_as_nodes(
        source_dir = Source_Path,
        isolate_directory_names=['EDIT'],
        isolate_formats=['jil', 'job'],
        quite_logging=True
    )
    
    Action_Duplicate_IWS_nodes_to_New_Agent (
        Output_Folder_path=_output_path,
        Search_Replace_Terms={
            "@APP1#":"@MACH6#",
            "@DB2#":"@MACH6#",
            "@MACH1#":"@MACH6#",
            "/export/home/dsor" : "/home/dsor",
	        "/export/customer/dsor" : "/dsor",
	        "/export/ftp/dsor/edit" : "/dsor/{ENV_DIR}/ftp"
        }
    )
           
    log.blank('-'*100)
    log.critical(f"End of log for ticket : {Ticket_Number} under contract : {Contract_Name}")
    log .info (f"Script processing time : {dt.now() - _start_time}")

    print ("Complete.")