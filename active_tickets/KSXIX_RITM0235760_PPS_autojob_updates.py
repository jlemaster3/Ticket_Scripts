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

contract = 'KSXYX'
ticketNumber = 'RITM0235760'

source_path = "C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\KSXIX\\"
# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")

#-------------------------------------------------
#   Steps
#-------------------------------------------------

def step_1 (sourcePath:str, outputPath:str, namedLists:dict[str, list[str]] = None) :
    _filelist = ToolBox_Gather_Files( 
        source_dir = sourcePath,
        isolate_directory_names= namedLists["ENV_LIST"] 
    )
    log.blank("-"*100)
    log.info(f"Search Terms -> Replace Terms : [{len(namedLists['Search_Replace'].keys())}]", data = namedLists['Search_Replace'])
    log.info(f"limiting Job Stream edits to workstations : [{len(namedLists['workstation_refs'])}]", data=namedLists['workstation_refs'], list_data_as_table=True, column_count=1)
    _files_updated = 0
    for _file in _filelist:
        if isinstance(_file, ToolBox_IWS_JIL_File):
            _file_changed:bool = False
            _file.open_file()
            log.blank("-"*100)
            log.label(f"Processing File '{_file.relFilePath}'")
            _file.open_file()
            for _job in _file.job_objects:
                for _ws in namedLists['workstation_refs']:
                    if _ws.upper() in _job.full_path.upper():
                        for _search, _reaplce in namedLists['Search_Replace'].items():
                            _job.search_replace_text(_search, _reaplce)
                            if _job._source_text != _job._modified_text:
                                _file_changed = True
            
            if _file_changed == True:
                _file.save_File(outputFolder=outputPath, useRelPath=True)
                _files_updated += 1
            _file.close_file()
    log.info(f"Total number of files changed : [{_files_updated}]")


#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    _start_time = dt.now()
    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{_start_time.strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")

    step_1 (
        sourcePath = source_path,
        outputPath = os.path.join(working_directory,"KSXIX_autojob_updates"),
        namedLists = {
            "workstation_refs" : ['@MACH8#', '@MACH9#'],
            "ENV_LIST" : ["PPS", "DEVB", "DEVC", "SITB", "SITC", "UATB", "UATC"],
            "Search_Replace": {   
                "/dsks/{APP_CMN}/{ENV_DIR}/autojob.sh":"/dsks/{APP_CMN}/{ENV_DIR}/job/autojob.sh",
                "/export/customer/kscmn/prod/job/autojob.sh":"/dsks/{APP_CMN}/{ENV_DIR}/job/autojob.sh",
                "/export/customer/kscmn/pre/job/autojob.sh":"/dsks/{APP_CMN}/{ENV_DIR}/job/autojob.sh",
                "/export/customer/kscmnb/test/job/autojob.sh":"/dsks/{APP_CMN}/{ENV_DIR}/job/autojob.sh",
                "/export/customer/kscmnc/test/job/autojob.sh":"/dsks/{APP_CMN}/{ENV_DIR}/job/autojob.sh",
                "/export/customer/kscmnb/acc/job/autojob.sh":"/dsks/{APP_CMN}/{ENV_DIR}/job/autojob.sh",
                "/export/customer/kscmnc/acc/job/autojob.sh":"/dsks/{APP_CMN}/{ENV_DIR}/job/autojob.sh",
                "/export/customer/kscmnb/mod/job/autojob.sh":"/dsks/{APP_CMN}/{ENV_DIR}/job/autojob.sh",
                "/export/customer/kscmnc/mod/job/autojob.sh":"/dsks/{APP_CMN}/{ENV_DIR}/job/autojob.sh",
                "{JOBDIR}/autojob.sh": "/dsks/{APP_CMN}/{ENV_DIR}/job/autojob.sh",
                "/export/ftp/kspbc/prod":"/dsks/ftp/{APP_PBC}/{ENV_DIR}",
                "/export/ftp/kspbc/pre":"/dsks/ftp/{APP_PBC}/{ENV_DIR}",
                "/export/ftp/kspbc/test":"/dsks/ftp/{APP_PBC}/{ENV_DIR}",
                "/export/ftp/kspbc/mod":"/dsks/ftp/{APP_PBC}/{ENV_DIR}",
                "/export/ftp/kspbc/acc":"/dsks/ftp/{APP_PBC}/{ENV_DIR}",
                "/export/home/kspbc":"/dsks/home/{APP_PBC}/{ENV_DIR}",
                "DEVB" :"{ENV}",
                "SITB" :"{ENV}",
                "UATB" :"{ENV}",
                "DEVC" :"{ENV}",
                "SITC" :"{ENV}",
                "UATC" :"{ENV}",
                "PPS" :"{ENV}",
                "PROD" :"{ENV}"
            }
        }
    )

    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    log .info (f"Script processing time : {dt.now() - _start_time}")
    print ("complete")