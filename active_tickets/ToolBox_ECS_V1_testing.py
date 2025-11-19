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

source_path = f"C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\{contract}_{ticketNumber}\\TEST_ENV"
source_path_1 = f"C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\DEXIX"
source_path_2 = f"C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\DEXIX_RITM0229309\\TSTB_replaced"

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
        isolate_formats=['jil','job'],
        quite_logging=False
    )
    ToolBox.load_file_nodes(
        skip_duplicates=False, 
        quite_logging=False,
        contents_as_entities=True
        )
    
    log.blank('-'*100)
    log.info (f"Total Nodes being Tracked :[{len(ToolBox)}]")
    

    log.blank(ToolBox.node_stats)
    for _jil_file in ToolBox.JIL_file_nodes:
        log.debug(f"{_jil_file.relFilePath} | Children [{len(_jil_file.children)}]", data = _jil_file.children)
        for _child in _jil_file.children:
            log.debug(f"{type(_child)}",data=_child)

    log.blank('-'*100)

    for _col_idx, _col_name in enumerate(ToolBox.dataSilo.get_column_names):
        _entities_with_col = ToolBox.dataSilo.get_entities_with_components(_col_name)
        log.blank(f"[{_col_idx}] '{_col_name}' [{len(_entities_with_col)}]")

    
    for _idx, (_key, _components) in enumerate(ToolBox.dataSilo.all_entities().items()):
        log.blank('-'*100)
        log.debug (f"[{_idx}] '{_key}' | Component list : [{len(_components.keys())}]")
        for _k, _v in _components.items():
            
            log.blank(f"'{_k}' : {_v}")


    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    log .info (f"Script processing time : {dt.now() - _start_time}")
    print ("Complete.")