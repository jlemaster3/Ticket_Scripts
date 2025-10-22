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

    _file_list = ToolBox_Gather_Files(
        source_dir = source_path,
        #isolate_directory_names= ['prod'],
        isolate_fileName_names = ["Temp_test"],
        isolate_formats=['jil','job'],
    )
    log.info (f"Total files found:[{len(_file_list)}]")
    dataECS.import_file_list(_file_list)
    _nodes_by_files = dataECS.get_IWS_nodes_by_file()
    _total = sum([len(_list) for _list in _nodes_by_files.values()])
    log.blank('-'*100)
    log.info (f"Total Nodes being tracked :[{_total}]")
    for _file_idx, (filePath, nodeList) in enumerate(_nodes_by_files.items()):
        log.blank('-'*75)
        log.label (f"[{_file_idx}] - File : '{filePath}' nodes :")
        for _node_idx, node in enumerate(nodeList):
            if isinstance(node, ToolBox_ECS_Node_IWS_Obj):
                log.debug (f"[{_node_idx}] - {node.full_path}")
                
    log.blank('-'*100)
    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    log .info (f"Script processing time : {dt.now() - _start_time}")
    print ("Complete.")