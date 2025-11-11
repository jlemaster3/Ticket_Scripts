#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, sys, re
from datetime import datetime as dt

## Imports ToolBox, and log
_curr_dir = os.path.dirname(os.path.abspath(__file__))
_prnt_dir = os.path.dirname(_curr_dir)
sys.path.append(_prnt_dir)
from ToolBox_ECS_V1 import *

#-------------------------------------------------
#   Variables
#-------------------------------------------------

contract = 'DEXIX'
ticketNumber = 'RITM0229309'

source_path = "C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\DEXIX\\TSTB"
# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")

#-------------------------------------------------
#   Steps
#-------------------------------------------------


def udpate_docommnad (search_replace:dict[str,str], output_path:str):
    
    ToolBox.collect_files_as_nodes(
        source_dir = source_path,
        quite_logging=True
    )

    for _file in ToolBox.JIL_file_nodes:
        _file.open_file(
            quite_logging=False,
            enable_post_porcesses=False
        )

        if _file._modified_file_text is not None:
            _text_line_list = _file._modified_file_text.splitlines()
            _has_been_updated = False
            for _line_idx, _line_string in enumerate(_text_line_list):
                _docoammand_match =  re.search(ToolBox.REGEX_Patterns.IWS_DOCOMMAND_LINE, _line_string, re.IGNORECASE|re.MULTILINE)
                if _docoammand_match is not None:
                    #log.debug(f"[{_line_idx}] [{_docoammand_match.span()}] '{_line_string}'")
                    for _task_text in _docoammand_match.groupdict().values():                        
                        for _sr_idx, (_search, _replace) in enumerate(search_replace.items()):
                            if _search in _task_text:
                                log.debug(f"Line: [{_line_idx}] | '{_line_string}' | Found : '{_search}' | Replacing : '{_replace}'")
                                _text_line_list[_line_idx] = _text_line_list[_line_idx].replace(_search, _replace)
                                _has_been_updated = True
            
            if _has_been_updated == True:
                _file._modified_file_text = '\n'.join(_text_line_list)
                _file.save_File(
                    outputFolder=output_path,
                    useRelPath=True,
                    quite_logging= False
                )
            _file.close_file(
                quite_logging=False
            )
        log.blank('-'*100)

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    _start_time = dt.now()
    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{_start_time.strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")

    udpate_docommnad(
        search_replace = {
            '/{ENV}/' : '/{ENV_DIR}/',
            '/logs' : '/log'
        },
        output_path=os.path.join(working_directory,'_corrections')
    )


    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    log .info (f"Script processing time : {dt.now() - _start_time}")
    print ("complete")