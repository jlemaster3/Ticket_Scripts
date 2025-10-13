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

contract = 'MMS-VA'
ticketNumber = 'RITM0221064'

source_path = "C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\MMS\\"
# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")

#-------------------------------------------------
#   Steps
#-------------------------------------------------

def Step_1 (sourcePath:str, outputPath:str, namedLists:dict[str, list[str]] = None) :
    
    _jil_filelist = ToolBox_Gather_Files( 
        source_dir = sourcePath, 
        isolate_directory_names= namedLists["ENV_List"],
        directory_AnyOrAll= ToolBox_Enum_AnyAll.ALL
    )
    _csv_filelist =  ToolBox_Gather_Files( 
        source_dir = namedLists['CSV_rootPath'], 
        isolate_formats= ['csv']
    )

    _docommand_changes:dict[str, str] = {}
    _missed_list = []
    for _csvFile in _csv_filelist:
        if isinstance(_csvFile, ToolBox_CSV_File):
            _csvFile.open_file()
            for _row in _csvFile.rows:
                if ('stream_name' in _row.keys()) and ('job_name' in _row.keys()) and ('target_command' in _row.keys()):
                    _streamName = '_'.join(_row['stream_name'].split('_')[3:]).upper()
                    _jobName = _row['job_name'].upper()
                    _docommand_changes[f"{_streamName}.{_jobName}"] = _row['target_command']
                else:
                    _missed_list.append(_row)
    log.info (f"Total number of DOCOMMAND target_values : [{len(_docommand_changes.keys())}]", data=_docommand_changes)
    if len (_missed_list) >= 1:
        log.warning (f"Items not compatible with script [{len(_missed_list)}]", data=_missed_list, list_data_as_table=True, column_count=1)
    _stream_names = list(set([_n.split('.')[0].upper() for _n in _docommand_changes.keys()]))    
    _changed_line_count = 0
    _changed_list = []
    for _file in _jil_filelist:
        if isinstance(_file, ToolBox_IWS_JIL_File):
            log.blank("-"*100)
            log.label(f"Processing File '{_file.relFilePath}'")
            _file.open_file()
            for _stream_obj in _file.job_stream_objects:
                _target_streamName = _stream_obj.name.upper()[1:]
                if any([_target_streamName in _name.upper() for _name in _stream_names]):
                    log.info (f"Found Stream: '{_stream_obj.full_path}'")
                    for _job in _stream_obj.job_objects:
                        _target_jobName = _job.full_path.split('.')[-1].upper()
                        _target_key = f"{_target_streamName}.{_target_jobName}"
                        for _name in _docommand_changes.keys():
                            if  _target_key in _name.upper():
                                try:
                                    log.info (f"Found job: '{_job.full_path}'")
                                    log.debug (f'Current DOCOMMAND :{_job.DOCOMMAND}')
                                    _job.DOCOMMAND = _docommand_changes[_name]
                                    log.debug (f'Target DOCOMMAND  :{_job.DOCOMMAND}')
                                    _changed_line_count += 1
                                    _changed_list.append(_target_key)
                                    _file.save_File(outputFolder=outputPath, useRelPath=True)
                                except:
                                    continue
            _file.close_file()
            
    _missed_list = []
    for _path in _docommand_changes.keys():
        _matches = []
        for _found in _changed_list:
            if (_found.upper()in _path.upper()):
                _matches.append(_path)
        if (_path not in _matches) and (_path not in _missed_list):
            _missed_list.append(_path)
    log.blank("-"*100)
    log.info(f"Total number of DOCOMMAND line changes made : [{_changed_line_count}]")
    if len(_missed_list) >= 1:
        log.info(f"Total number of DOCOMMAND line changes missed : [{len(_missed_list)}]", data=_missed_list, list_data_as_table=True, column_count= 1)
    else:
        log.info(f"Total number of DOCOMMAND line changes missed : [0]")
#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{dt.now().strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")

    Step_1(
        sourcePath = source_path,
        outputPath = os.path.join(working_directory,"DOCOMMAND_update"),
        namedLists = {
            "ENV_List" : ["PROD", "VA"],
            "CSV_rootPath" : working_directory
        }
    )

    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    print ("complete")