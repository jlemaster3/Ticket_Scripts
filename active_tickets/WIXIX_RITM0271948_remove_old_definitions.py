#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os
import sys
import re
from datetime import datetime as dt

## Imports ToolBox, and log
_curr_dir = os.path.dirname(os.path.abspath(__file__))
_prnt_dir = os.path.dirname(_curr_dir)
sys.path.append(_prnt_dir)
from ToolBox_ECS_V2 import *

#-------------------------------------------------
#   Variables
#-------------------------------------------------

contract = 'WIXIX'
ticketNumber = 'RITM0271948'

source_path = f"C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\{contract}"

# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")


#-------------------------------------------------
#   Steps
#-------------------------------------------------

def remove_old_definitions(search_terms:list[str]):
    """Removes old definitions from IWS Job and JIL files based on search terms."""
    
    ToolBox.IWS_JIL_File_Manager.load_files(quite_logging=False, enable_post_porcesses=False)

    for _file_key in ToolBox.JIL_file_keys:
        _file_e = ToolBox.dataSilo.get_entity(_file_key)
        if 'file_text' in _file_e.keys():
            _original_text:str = _file_e.get('file_text', '')
            _modified_text:str = _original_text
            _has_been_modified:bool = False

            _stream_start_results = list(re.finditer(pattern=ToolBox.Regex_Patterns.IWS_STREAM_START_LINE, string=_modified_text, flags=re.MULTILINE))
            _stream_ends_results = list(re.finditer(pattern=ToolBox.Regex_Patterns.IWS_STREAM_END_LINE, string=_modified_text, flags=re.MULTILINE))    
            
            if len(_stream_start_results) >= 1 and len(_stream_ends_results) >= 1:
                for _i in range(len(_stream_start_results)):
                    _start_match = _stream_start_results[_i]
                    _end_match = _stream_ends_results[_i]
                    if any(term in _start_match.group('workstation') for term in search_terms):
                        _stream_block = _modified_text[_start_match.start():_end_match.end()]
                        _modified_text = _modified_text.replace(_stream_block, '').strip()
                        _has_been_modified = True
            if _has_been_modified:
                ToolBox.dataSilo.update_component(
                    entity_id=_file_key,
                    component_name='file_text',
                    component_data=_modified_text
                )
                ToolBox.dataSilo.add_component(entity_id=_file_key, component_name='is_modified', component_data=True)
                log.info (f"Removed old definitions from JIL File Entity : '{_file_e.get('file_name','unknown')}{_file_e.get('file_format','*')}'")

    

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    _start_time = dt.now()
    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{_start_time.strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")
    
    _output_path = os.path.join(working_directory, 'Updated_JIL_Files')
    _search_terms:list[str] = ['@MACH3#', '@MACH4#', '@MACH5#']

    ToolBox.collect_files (
        source_dir=source_path,
        isolate_directory_names= ['prod'],
        isolate_formats=['jil', 'job'],
        containing_terms= _search_terms
    )

    remove_old_definitions(_search_terms)   
    
    ToolBox.IWS_JIL_File_Manager.save_files(
        outputFolder=_output_path,
        useRelPath=True,
        is_modified=True
    )
    #log.blank('-'*100)
    #for _key_counter, _key in enumerate(ToolBox.dataSilo.get_entity_keys_by_component_value( component='object_type', value=ToolBox.Entity_Types.FILE_JIL)):
    #    log.blank(f"[{_key_counter + 1}] {_key}", data =ToolBox.dataSilo.get_entity(_key))
    #    log.blank('-'*100)

    log.blank('-'*100)
    
    log.blank(ToolBox.dataSilo.statistics)
    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    log .info (f"Script processing time : {dt.now() - _start_time}")
    print ("Complete.")