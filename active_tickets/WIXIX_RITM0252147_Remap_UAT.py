#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, sys, copy, re
from datetime import datetime as dt
from typing import Any

## Imports ToolBox, and log
_curr_dir = os.path.dirname(os.path.abspath(__file__))
_prnt_dir = os.path.dirname(_curr_dir)
sys.path.append(_prnt_dir)
from ToolBox_ECS_V1 import *


#-------------------------------------------------
#   Steps
#-------------------------------------------------

def Action_Search_Replace_Text (
    Output_Folder_path:str ,
    Search_Replace_Terms:dict[str,str],
    quite_logging:bool = True
):
    """For each file in source path, find all IWS assets, and duplicate them, then preform a search and replace on teh duplicated assest's text.
    Append the duplcated and udpated text to the current file, and save a copy of the file to a new location for review."""
    _udpated_files:list[ToolBox_ECS_Node] = []
    log.info (f"Total number of search terms to evaluate : [{len(Search_Replace_Terms.keys())}]")
    log.info(f"Search and Duplicate values : [{len(Search_Replace_Terms.keys())}]", data=Search_Replace_Terms)
    
    log.blank('-'*100)
    for _file_index, _file_node in enumerate(ToolBox.JIL_file_nodes):
        _file_node.open_file(
            enable_post_porcesses=False,
            quite_logging=True
        )
        _has_been_updated:bool = False
        if _file_node._modified_file_text is not None:
            for _search, _replace in Search_Replace_Terms.items():
                if _search.upper() in _file_node._modified_file_text.upper():
                    _file_node._modified_file_text = _file_node._modified_file_text.replace(_search, _replace)
                    log.debug (f"[{len(_udpated_files)+1}] - Found search term '{_search}', repalcing with '{_replace}'")
                    
                    _udpated_files.append(_file_node)
                    _has_been_updated = True

        if _has_been_updated == True:
            _file_node.save_File(outputFolder=Output_Folder_path, useRelPath= True, quite_logging= False)
            
        _file_node.close_file(
            quite_logging = True
        )
        
    log.info(f"Found a total of [{len(_udpated_files)}] files that contained 1 or more of the [{len(Search_Replace_Terms.keys())}] search terms and where udpated with duplciated Job Streams and/or Jobs.")
    log.blank('\n'.join([f"[{_c+1}] '{_n.relFilePath}'" for _c, _n in enumerate(_udpated_files) if isinstance(_n, ToolBox_IWS_JIL_File_Node)]))

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    Contract_Name = 'WIXIX'
    Ticket_Number = 'RITM0252147'
    Source_Path = 'C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\WIXIX\\'
    Working_Path = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\"
    Output_folder_name = 'PROD_Duplicate'

    # Capture current date and time when script begins
    _start_time = dt.now()
    
    _working_path:str = os.path.join (Working_Path, f"{Contract_Name}_{Ticket_Number}")
    log.init_logger(log_folder=_working_path, log_file=f"{Contract_Name}_{Ticket_Number}_{_start_time.strftime('%Y%m%d')}_UAT.log")
    log.critical(f"Starting log for ticket : {Ticket_Number} under contract : {Contract_Name}")
    _output_path:str = os.path.join (_working_path, Output_folder_name)

    ToolBox.collect_files_as_nodes(
    source_dir = Source_Path,
    isolate_directory_names=['UAT'],
    isolate_formats=['jil', 'job'],
    )

    Action_Search_Replace_Text(
        Output_Folder_path=_output_path,
        Search_Replace_Terms = {
            '@MACH12#':'@MACH9#',
            '@MACH13#':'@MACH10#',
            '@MACH14#':'@MACH11#'
        },
        quite_logging=False
    )

    log.critical(f"End of log for ticket : {Ticket_Number} under contract : {Contract_Name}")
    log .info (f"Script processing time : {dt.now() - _start_time}")

    print ("Complete.")