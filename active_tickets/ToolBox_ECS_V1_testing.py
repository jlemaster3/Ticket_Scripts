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

source_path = f"C:\\Users\\jlemaster3\OneDrive - Gainwell Technologies\Documents\\_Ticket_Repo\\{contract}_{ticketNumber}\\TEST_ENV"

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
        isolate_directory_names= ['prod'],
        isolate_fileName_names = ["Temp_test"],
        isolate_formats=['jil','job']
    )
    log.info (f"Total files found:[{len(_file_list)}]")
    ToolBox.load_file_nodes()
    log.blank('-'*100)
    log.info (f"Total Nodes being Tracked :[{len(ToolBox)}]")
    log.blank('-'*100)

    for _stream in ToolBox.IWS_Job_Stream_nodes:
        log.info (f"{_stream.full_path}", data=_stream.format_as_Job_Stream(
            indent=0,
            include_notes=False,
            include_jobs=False,
            include_end=False
        ), list_data_as_table=True, column_count=1)

    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    log .info (f"Script processing time : {dt.now() - _start_time}")
    print ("Complete.")