#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, sys, copy
from datetime import datetime as dt

## Imports ToolBox, and log
_curr_dir = os.path.dirname(os.path.abspath(__file__))
_prnt_dir = os.path.dirname(_curr_dir)
sys.path.append(_prnt_dir)
from ToolBox_V2 import *

#-------------------------------------------------
#   Variables
#-------------------------------------------------

contract = 'ORXIX'
ticketNumber = 'RITM0226400'

source_path = "C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\ORXIX"
# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")

#-------------------------------------------------
#   Steps
#-------------------------------------------------

def Step_1 (sourcePath:str, outputPath:str, namedLists:dict[str, list[str]] = None) :
    _filelist = ToolBox_Gather_Files( 
        source_dir = sourcePath, 
        isolate_directory_names= namedLists['Environment_List'],
        list_as_tables= True
    )
    log.blank("-"*100)
    log.info(f"Search Terms -> Replace Terms : [{len(namedLists['Search_Replace'].keys())}]", data = namedLists['Search_Replace'])
    _ws_list = list(namedLists['Workstation_Swap'].keys())
    log.info(f"Limiting edits to Job Streams and Jobs that are on Workstations : [{len(_ws_list)}]", data=_ws_list, list_data_as_table=True, column_count=1)
    _updated_file_count = 0
    _file_to_duplciate_streams = []
    for _file in _filelist:
        if isinstance(_file, ToolBox_IWS_JIL_File):
            _file.open_file()
            for _search in namedLists['Workstation_Swap'].keys():
                _file_to_duplciate_streams.append(_file)
    for _dup_file in _file_to_duplciate_streams:
        if isinstance(_dup_file, ToolBox_IWS_JIL_File):
            _dup_file.open_file()
            log.blank("-"*100)
            log.info(f"Processing File '{_dup_file.relFilePath}'")
            _file_updated:bool = False
            for _source_ws, _target_ws in namedLists["Workstation_Swap"].items():
                Action_IWS_JIL_duplicate_streams(_dup_file, _source_ws, _target_ws)
                _file_updated = True
            for _stream in _dup_file.job_stream_objects:
                if '@APP2#' in _stream.full_path.upper():
                    for _job in _stream.job_objects:
                        for _source_ws, _target_ws in namedLists["Workstation_Swap"].items():
                            _job.search_replace_text(_source_ws, _target_ws)
                            _file_updated = True
                        for _search, _replace in namedLists['Search_Replace'].items():
                            _job.search_replace_text(_search, _replace)
                            _file_updated = True

            if (_file_updated == True):
                _dup_file.save_File(outputFolder=outputPath, useRelPath=True)
                _updated_file_count += 1
            else:
                log.info (f"No workstation reference or search & replace reference found in file, no changes made, closing file.")
            _file.close_file()
    log.blank("-"*100)
    log.info(f"Total number of files changed : [{_updated_file_count}]")

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{dt.now().strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")
        
    log.critical(f"", data = {
        "Requirment 1" :"Duplicate Job Streams and Jobs found on workstation 'ukohs021' (@APP1#, @DB2#, @MACH1#) and point them to workstaion 'ORXIXIMULAPP001' (@APP2#)."
    })

    Step_1 (
        sourcePath = source_path,
        outputPath = os.path.join(working_directory,"step_1"),
        namedLists = {
            "Environment_List" : ['UAT2'],
            "Workstation_Swap" : {
                '@APP1#' : '@APP2#',
                '@DB2#': '@APP2#',
                '@MACH1#' : '@APP2#'
            },
            "Search_Replace" : {
                "/export/home/dsor" : "/home/dsor",
                "/export/customer/dsor" : "/dsor",
                "/export/ftp/dsor/uat" : "dsor/{ENV}/ftp"
            }
        }
    )