#-------------------------------------------------
#   About
#-------------------------------------------------

'''
Ticket RITM0223648



'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, sys
from datetime import datetime as dt

## Imports ToolBox, and log
_curr_dir = os.path.dirname(os.path.abspath(__file__))
_prnt_dir = os.path.dirname(_curr_dir)
sys.path.append(_prnt_dir)
from ToolBox import *

#-------------------------------------------------
#   Variables
#-------------------------------------------------

contract = 'ORXIX'
ticketNumber = 'RITM0223648'

source_path = "C:\\VS_Managed_Accounts\\ORXIX"
# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")

#-------------------------------------------------
#   Steps
#-------------------------------------------------


def step_1 (
        sourcePath:str, 
        workingDirectory:str, 
        outputputRootPath:str, 
        outputUsingRelPaths:bool=True,
        namedLists:dict[str, list[str]] = None,
        quite_logging=False
    ):
    """Collect files by sub-directory comapred to source path for comparisons."""
    log.critical (f"Starting Step 1")
    if (not os.path.isdir(sourcePath)):
        log.error (f"Target source path is not a valid Directory Path : '{sourcePath}'")
        return
    if (not os.path.exists(sourcePath)):
        log.error (f"Target source path does not exists : '{sourcePath}'")
        return
    
    if (not os.path.isdir(workingDirectory)):
        log.error (f"Target Working Directory is not a valid directory path : '{workingDirectory}'")
        return
    os.makedirs(workingDirectory, exist_ok=True)
    if (outputputRootPath == None):
        # if output directory is note provided use working directory
        outputputRootPath = working_directory
    log.info (f"Gathering IWS *.jil and *.job files from source : '{sourcePath}'")
    log.info (f"Workstaion filter criteria : ", data=namedLists['Workstation_Swap'])
    _file_collection = gather_files(
        source_path = sourcePath,
        include_subfolders= namedLists['Folder_Filter_List'],
        include_name_terms = namedLists['Job_Stream_Names'],
        quite_logging = quite_logging
    )
    for _fileList in _file_collection.values():
        for _file in _fileList:
            log.info (f"Processing file : '{os.path.join(_file.sourceFileDirRelPath, _file.sourceFileName)}'")
            _file.openFile()
            for _sn in _file.jobStreamPaths:
                for _sourceWS, targetWS in namedLists['Workstation_Swap'].items():
                    _streamName = _sn.split('/')[-1].split('.')[0]
                    _file.duplciate_jobStream_by_workstaion(_streamName, _sourceWS, targetWS)
            _file.saveFileTo(outputputRootPath, useRelPath=True)
    log.critical (f"Completed Step 1")

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{dt.now().strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")
        
    log.critical(f"", data = {
        "Requirment 1" :"Duplicate the list of jobs found on workstation 'UKOHS018' (@APP1#) and point them to workstaion 'ORXIXSITLAPP001' (@APP2#)."
    })
    step_1 (
        sourcePath = source_path,
        workingDirectory = working_directory,
        outputputRootPath = os.path.join (working_directory, 'step_1'),
        outputUsingRelPaths = True,
        namedLists = {
            "Workstation_Swap" : {
                '@APP1#' : '@APP2#',
                '@MACH1#' : '@APP2#'
            },
            "Folder_Filter_List" : [
                "SIT",
                "SIT2",
                "SIT3",
                "SIT4",
                "SIT5"
            ],
            "Job_Stream_Names" : [
                "BUY_SETDATE",
                "CLDNDY_BOUNCE",
                "CLDNDY",
                "CYCDATE",
                "ELG_D_EXTRACT",
                "ELG_D_CLEANUP",
                "ELG_FILE_WATCH",
                "ELG_INTERFACE",
                "ELG_REPERC",
                "ELGD5_INCARC",
                "DMGD_MC_CYCLE",
                "PRV_DAILY_9PM",
                "SYD130"
            ]
        }
    )











