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
    for _file_index, _file_node in enumerate(ToolBox.file_nodes):
        log.info (f"[{_file_index+1}] Processing file '{_file_node.relFilePath}'")
        _file_node.open_file(
            enable_post_porcesses=False
        )
        _copy_of_text:str = copy.deepcopy(_file_node._source_file_text) or ''
        _has_been_updated:bool = False
        if isinstance(_copy_of_text, str):
            for _search, _replace in Search_Replace_Terms.items():
                _replaced = _copy_of_text.replace(_search,_replace)
                if _replaced != _copy_of_text:
                    if (quite_logging != True) :log.debug (f"Found search term '{_search}' and repalcing with '{_replace}'")
                    _copy_of_text = _replaced
                    _has_been_updated = True
        if _has_been_updated == True and isinstance(_copy_of_text, str):
            _file_node._modified_file_text = f"{_file_node._source_file_text}\n\n{_copy_of_text}"
            _file_node.save_File(
                outputFolder= Output_Folder_path,
                useRelPath=True
            )
        _file_node.close_file()

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    Contract_Name = 'NVXIX'
    Ticket_Number = 'RITM0244294'
    Source_Path = 'C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\NVXIX\\MOD'
    Working_Path = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\"
    Output_folder_name = 'MODE_note_toggle'

    
    _start_time = dt.now()
    
    _working_path:str = os.path.join (Working_Path, f"{Contract_Name}_{Ticket_Number}")
    # Capture current date and time when script begins
    log.init_logger(log_folder=_working_path, log_file=f"{Contract_Name}_{Ticket_Number}_{_start_time.strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {Ticket_Number} under contract : {Contract_Name}")
    _output_path:str = os.path.join (_working_path, Output_folder_name)

    ToolBox.collect_files_as_nodes(
        source_dir = Source_Path,
        quite_logging=True
    )
    
    _end_of_file_note = "### REMOVE THIS NOTE ###"
    for _file in ToolBox.JIL_file_nodes:
        _file.open_file(
            quite_logging=False,
            enable_post_porcesses=False
        )
        if _file._modified_file_text is not None:
            if _end_of_file_note in _file._modified_file_text: 
                _file._modified_file_text = _file._modified_file_text.replace(_end_of_file_note, '')
            else:
                _file._modified_file_text += f'\n{_end_of_file_note}'
            _file.save_File(outputFolder=_output_path, useRelPath= True)
           
    log.blank('-'*100)
    log.critical(f"End of log for ticket : {Ticket_Number} under contract : {Contract_Name}")
    log .info (f"Script processing time : {dt.now() - _start_time}")

    print ("Complete.")