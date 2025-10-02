#-------------------------------------------------
#   About
#-------------------------------------------------

'''
Ticket RITM0221442

Update STREAMLOGON for every Windows job on (NPR) /RIXIX/CHINFADEV02 and (PRD) /RIXIX/RIXODCWPAPP001 from RHSPROAD\rixix_autosys to RI\rixix_autosys

Already updated in IWS. Requires repository updated.

WBS Code C.000027.01.13.11.03.89 - APPS ODC to NTT Migration

All Windows jobs on /RIXIX/CHINFADEV02 and /RIXIX/RIXODCWPAPP001

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

contract = 'RIXIX'
ticketNumber = 'RITM0221442'

source_path = "C:\\VS_Managed_Accounts\\RIXIX"
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
        workstationFilterList:list = None,
        quite_logging=True
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
    log.info (f"Workstaion filter criteria : ", data=workstationFilterList)
    _FileList = gather_files(sourcePath, quite_logging=quite_logging)
    
    _used_resources = {
    'NEEDS':[],
    'RCG':[]
    }
    _updated_count = 0
    if (workstationFilterList != None):
        for _file in _FileList.values():
            
            
            _file.openFile()
            _jobPaths = _file.get_Job_names()
            _windows_jobs = []
            for _jobPath in _jobPaths:
                for _ws in workstationFilterList:
                    if _ws.upper() in _jobPath.upper():
                        _windows_jobs.append(_jobPath.split('.')[-1])
            
            if (len(_windows_jobs) >= 1):
                log.info (f"Found [{len(_windows_jobs)}] Jobs in file : '{os.path.join(_file.sourceFileDirRelPath, _file.sourceFileName)}'")
                _file.set_Jobs_STREAMLOGON('"^USER_CHS_{ENV}^"',filter_jobNames=_windows_jobs)
                _outputPath = os.path.join (outputputRootPath, _file.sourceFileDirRelPath)
                os.makedirs(_outputPath, exist_ok=True)
                _file.saveTo(_outputPath, useRelPath=False)
                _updated_count += 1
                _file.closeFile()
            else:
                log.info (f"skipping file : '{os.path.join(_file.sourceFileDirRelPath, _file.sourceFileName)}', does not match filter criteria")

    log.info (f" Updated a total of [{_updated_count}] files")
    log.critical (f"Completed Step 1")
    


#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{dt.now().strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")
    log.critical(f"", data = {
        "Requirment 1" :"Update STREAMLOGON for every Windows job on (NPR) /RIXIX/CHINFADEV02 (@MACH7#) from 'RHSPROAD\\rixix_autosys' to 'RI\\rixix_autosys'",
        "Requirment 2" :"Update STREAMLOGON for every Windows job on (PRD) /RIXIX/RIXODCWPAPP001 (@MACH8#) from 'RHSPROAD\\rixix_autosys' to 'RI\\rixix_autosys'"
    })
    step_1 (
        sourcePath = source_path,
        workingDirectory = working_directory,
        outputputRootPath = os.path.join (working_directory, 'step_1'),
        outputUsingRelPaths = True,
        workstationFilterList = [
            "@MACH7#", # "CHINFADEV02", "CHINFAPROD02"            
            "@MACH8#" # "RIXODCWPAPP001"
        ]
    )