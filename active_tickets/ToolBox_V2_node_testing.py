#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, sys
from datetime import datetime as dt

## Imports ToolBox, and log
_curr_dir = os.path.dirname(os.path.abspath(__file__))
_prnt_dir = os.path.dirname(_curr_dir)
sys.path.append(_prnt_dir)
from ToolBox_ECS_V2 import *

#-------------------------------------------------
#   Variables
#-------------------------------------------------

contract = 'Toolbox'
ticketNumber = 'RITM01234567'

source_path = f"C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\{contract}_{ticketNumber}\\TEST_ENV"

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
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_ECS_V2_{_start_time.strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")

    ToolBox.collect_files (
        source_dir=source_path,
        #isolate_directory_names= ['prod'],
        isolate_fileName_names = ["RCG"],
        isolate_formats=['jil', 'job', 'json', 'txt', 'csv'],
        quite_logging=False
    )
    log.blank(ToolBox.dataSilo.statistics)
    #log.blank(data=ToolBox.dataSilo.all_entities())
    log.blank('-'*100)

    ToolBox.IWS_TEXT_File_Manager.load_files(quite_logging=False)
    #ToolBox.IWS_TEXT_File_Manager.decode_IWS_calendar_text()
    ToolBox.IWS_TEXT_File_Manager.decode_IWS_RCG_text()
    #ToolBox.CSV_File_Manager.load_files(quite_logging=False)
    #ToolBox.IWS_CONFIG_File_Manager.load_files(quite_logging=False)
    #ToolBox.IWS_JIL_File_Manager.load_files(quite_logging=False)
    log.blank('-'*100)
    
    #ToolBox.Action_Manager.calendar_report_to_CSV(
    #    output_name="calendar_names_ranges.csv",
    #    output_path=working_directory
    #)

    

    _config_keys:list[str] = ToolBox.dataSilo.get_entity_keys_by_component_value( component='object_type', value=ToolBox.Entity_Types.FILE_JSON)
    _stream_keys:list[str] = ToolBox.dataSilo.get_entity_keys_by_component_value( component='object_type', value=ToolBox.Entity_Types.IWS_JOB_STREAM)
    _job_keys:list[str] = ToolBox.dataSilo.get_entity_keys_by_component_value( component='object_type', value=ToolBox.Entity_Types.IWS_JOB)
    _calendar_keys:list[str] = ToolBox.dataSilo.get_entity_keys_by_component_value( component='object_type', value=ToolBox.Entity_Types.IWS_CALENDAR)
    _csv_keys:list[str] = ToolBox.dataSilo.get_entity_keys_by_component_value( component='object_type', value=ToolBox.Entity_Types.FILE_CSV)
    _rcg_keys:list[str] = ToolBox.dataSilo.get_entity_keys_by_component_value( component='object_type', value=ToolBox.Entity_Types.IWS_RUNCYCLEGROUP)
    _merged_key_list = _stream_keys + _job_keys +_csv_keys + _rcg_keys
    
    log .info (f"Total of [{len(_merged_key_list)}] of IWS assets loaded : ")
    log.blank('-'*100)
    for _key_counter, _key in enumerate(_merged_key_list):
        
        log.blank(f"[{_key_counter + 1}] {_key}", data =ToolBox.dataSilo.get_entity(_key))
        log.blank('-'*100)
    

    ToolBox.Action_Manager.RCG_report_to_CSV (
        output_name = "RCG_date_ranges", 
        output_path = working_directory, 
        #component_filters = {"date_values": lambda dates: dates is not None and len(dates) >= 1}
    )

    log.blank('-'*100)
    
    log.blank(ToolBox.dataSilo.statistics)
    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    log .info (f"Script processing time : {dt.now() - _start_time}")
    print ("Complete.")