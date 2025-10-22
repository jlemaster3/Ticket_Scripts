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

contract = 'DEXIX'
ticketNumber = 'RITM0229309'

source_path = "C:\\Users\\jlemaster3\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\DEXIX_RITM0229309\\TSTB"
# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")

#-------------------------------------------------
#   Steps
#-------------------------------------------------

def step_1 (sourcePath:str, outputPath:str, namedLists:dict[str, list[str]] = None) :
    _filelist = ToolBox_Gather_Files( 
        source_dir = sourcePath
    )

    dataECS.import_file_list(_filelist)
    

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    _start_time = dt.now()
    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{_start_time.strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")

    step_1(
        sourcePath = source_path,
        outputPath = os.path.join(working_directory,"TSTB_Cleaned"),
        namedLists = {
        }
    )


    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    log .info (f"Script processing time : {dt.now() - _start_time}")
    print ("complete")