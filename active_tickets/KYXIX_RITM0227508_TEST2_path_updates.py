#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, sys
from datetime import datetime as dt

## Imports ToolBox, and log
_curr_dir = os.path.dirname(os.path.abspath(__file__))
_prnt_dir = os.path.dirname(_curr_dir)
sys.path.append(_prnt_dir)
from ToolBox_V2 import *

#-------------------------------------------------
#   Variables
#-------------------------------------------------

contract = 'KYXYX'
ticketNumber = 'RITM0227508'

source_path = "C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\KYXIX\\TEST2"
# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")

#-------------------------------------------------
#   Steps
#-------------------------------------------------


def step_1 (sourcePath:str, outputPath:str, namedLists:dict[str, list[str]] = None) :
    _paths = ToolBox_Gather_Directories(
        source_dir = sourcePath
    )

    _filelist = ToolBox_Gather_Files( 
        source_dir = sourcePath, 
        isolate_directory_names = namedLists['Target_Env_list'],
    )

    _files_updated = 0
    for _file in _filelist:
        _file.open_file()
        _change_made = False
        #log.blank('-'*100)
        #log.label(f"Checking File '{_file.relFilePath}'")
        for _stream in _file.job_stream_objects:
            if any (_ws.upper() in _stream.full_path.upper() for _ws in namedLists["Workstation_list"]):
                _stream_text = _stream.get_current_text()
                for _searchTerm, _replaceTerm in namedLists['Search_Replace_Terms'].items():
                    if _searchTerm in _stream_text:
                        log.blank('-'*100)
                        log.label(f"Checking File '{_file.relFilePath}'")
                        _stream.search_replace_text(searchString=_searchTerm,replaceString=_replaceTerm)
                        _change_made = True
        for _job in _file.job_objects:
            if any (_ws.upper() in _job.full_path.upper() for _ws in namedLists["Workstation_list"]):
                _job_text = _job.get_current_text()
                for _searchTerm, _replaceTerm in namedLists['Search_Replace_Terms'].items():
                    if _searchTerm in _job_text:
                        if _change_made == False:
                            log.blank('-'*100)
                            log.label(f"Checking File '{_file.relFilePath}'")
                        _job.search_replace_text(searchString=_searchTerm,replaceString=_replaceTerm)
                        _change_made = True
        if _change_made == True:
            _file.save_File(outputPath, useRelPath=True)
            _files_updated += 1
        #else:
            #log.info(f"No changes to make, closing File '{_file.relFilePath}'")
    log.blank('-'*100)
    log.info(f"Updated a total of [{_files_updated}] out of [{len(_filelist)}] files found in filters.")

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    _start_time = dt.now()
    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{_start_time.strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")
    log.critical(f"", data = {
        "requirment 1" : "Changes will be made to the workstation USOLLUKKFS001 Folder: TEST2.",
        "requirment 2" : "The changes are to change the prefix of the file names below from what they are now in IWS now to what they need to be changed in IWS now.",
        "Prefix 1" : "From: /export/ftp/prod/ to: /dsky/test/ftp/",
        "Prefix 2" : "From: /tmpsort2/prod/ to: /tmpsort2/test/",
        "Prefix 3" : "From: /cust/prod/dsky/ to: /dsky/prod/"
    })

    step_1(
        sourcePath = source_path,
        outputPath = os.path.join(working_directory,"TEST2"),
        namedLists = {
            "Target_Env_list" : ["TEST2"],
            "Workstation_list" : ["@MACH7#"],
            "Search_Replace_Terms" : {
                "/export/ftp/prod/": "/dsky/{ENV}/ftp/",
                "/tmpsort2/prod/" : "/tmpsort2/{ENV}/",
                "/cust/prod/dsky/" : "/dsky/{ENV}/"
            },
        }
    )
    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    log .info (f"Script processing time : {dt.now() - _start_time}")
    print ("complete")