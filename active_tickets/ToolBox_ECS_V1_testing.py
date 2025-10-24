#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, sys
from datetime import datetime as dt

## Imports ToolBox, and log
_curr_dir = os.path.dirname(os.path.abspath(__file__))
_prnt_dir = os.path.dirname(_curr_dir)
sys.path.append(_prnt_dir)
from ToolBox_ECS_V1 import *

#-------------------------------------------------
#   Variables
#-------------------------------------------------

contract = 'Toolbox'
ticketNumber = 'RITM01234567'

source_path_2 = f"C:\\Users\\jlemaster3\OneDrive - Gainwell Technologies\Documents\\_Ticket_Repo\\{contract}_{ticketNumber}\\TEST_ENV"
source_path_1 = f"C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\DEXIX"
source_path = f"C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\DEXIX_RITM0229309\\TSTB_replaced"

# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")

#-------------------------------------------------
#   Steps
#-------------------------------------------------


#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    _start_time = dt.now()
    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{_start_time.strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")

    _file_list = ToolBox.collect_files_as_nodes(
        source_dir = source_path,
        isolate_directory_names= ['tstb'],
        #isolate_fileName_names = ["Temp_test"],
        isolate_formats=['jil','job']
    )
    log.info (f"Total files found:[{len(_file_list)}]")
    ToolBox.load_file_nodes(skip_duplicates=True)
    log.blank('-'*100)
    log.info (f"Total Nodes being Tracked :[{len(ToolBox)}]")
    log.blank('-'*100)

    _bad_files = []
    for _node in ToolBox.IWS_object_nodes:
        if ('@MACH2#' in _node._source_file_text) and (_node.sourceFile_Object.relPath not in _bad_files):
            _bad_files.append(_node.sourceFile_Object.relPath)
    log.blank('',data=_bad_files, list_data_as_table=True, column_count=1)
    print (len(_bad_files))
    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    log .info (f"Script processing time : {dt.now() - _start_time}")
    print ("Complete.")