#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, sys, copy, re
from datetime import datetime as dt

## Imports ToolBox, and log
_curr_dir = os.path.dirname(os.path.abspath(__file__))
_prnt_dir = os.path.dirname(_curr_dir)
sys.path.append(_prnt_dir)
from ToolBox_ECS_V1 import *


#-------------------------------------------------
#   Steps
#-------------------------------------------------

#def list_of_named_rows_to_string (source_row_list:list[dict[str,str|int|float|bool|None]]) -> str:
#    _headers = list(source_row_list[0].keys())
#    _headers.insert(0,'Row Index')
#    _col_width:dict[str,int] = {_h: len(_h) for _h in _headers}
#    for _indx, _row in enumerate(source_row_list):
#        _row['Row Index'] = _indx + 1
#        for _header, _value in _row.items():
#            _col_width[_header] = max(_col_width[_header], len(str(_value)))
#    _header_row = " | ".join(f"{_h:^{_col_width[_h]}}" for _h in _headers)
#    _separator = '-+-'.join("-" * _w for _w in _col_width.values())
#    _data_rows = []
#    for _row in source_row_list:
#        _parts = []
#        for _h in _headers:
#            _target_val = _row.get(_h, None)
#            if isinstance(_target_val,str):
#                _parts.append(f"{str(_target_val):<{_col_width[_h]}}")
#            else:
#                _parts.append(f"{str(_target_val):^{_col_width[_h]}}")
#        _row_str = " | ".join(_parts)
#        _data_rows.append(_row_str)
#    _table_parts = [_header_row, _separator]+_data_rows
#    return '\n'.join(_table_parts)

def Action_Add_DEADLINE_to_streams (
    Output_Folder_path:str ,
    quite_logging:bool = True
):
    """For each file in source path, find all IWS assets, and duplicate them, then preform a search and replace on teh duplicated assest's text.
    Append the duplcated and udpated text to the current file, and save a copy of the file to a new location for review."""
    _target_deadline_objects:dict[str, str] = {}
    _target_deadline_with_notes:dict[str, str] = {}
    for _file_node in ToolBox.XLSX_file_nodes:
        _file_node.open_file(quite_logging= quite_logging)    
        for _row in _file_node._sheets_as_tables['Job List']:
            _job_name = _row['IWS - Prod Job Name']
            _add_deadLine = True if any([str(_row['DEADLINE 0400 WARN? (Y/N)']).lower() == _v.lower() for _v in ['Y','y','1','true']]) else False
            _has_notes = False if (_row['Notes'] is None) or (str(_row['Notes']).strip() == '') else True
            _target_name = f"@.{_job_name}"
            if _add_deadLine == True and _has_notes == False:
                if _target_name not in _target_deadline_objects.keys():
                    _target_deadline_objects[_target_name] = 'DEADLINE 0400 WARN' 
            elif _add_deadLine == True and _has_notes == True:
                if _target_name not in _target_deadline_with_notes.keys():
                    _target_deadline_with_notes[_target_name] = _row['Notes']
        if (quite_logging != True): log.blank(ToolBox.Foramt_list_of_dictionaries_to_multiline_str(_file_node._sheets_as_tables['Job List']))
        log.info (f"numebr of items to set DEDALINE at 0400 without special notes : [{len(_target_deadline_objects)}]")
        log.info (f"numebr of items to set DEADLINE 0400 and WARN with special notes : [{len(_target_deadline_with_notes)}]")
        _found_table_list:list[dict[str, str]] = [{"Job Name": str(_k), "DEADLINE 0400 WARN? (Y/N)":"Y", "Note":_v} for _k,_v in _target_deadline_with_notes.items()]
        log.info (f"Item do not match criteria and are being exlcuded from list : ")
        log.blank(ToolBox.Foramt_list_of_dictionaries_to_multiline_str(_found_table_list))
    _deadline_rows:dict[str,dict[str,str]] = {}
    _missing_deadline_rows:list[str] = []
    for _runbk in ToolBox.IWS_Runbook_file_nodes:
        log.info(f"runbook : '{_runbk.relFilePath}' contains [{len(_runbk.job_stream_full_paths)}] Job Stream and [{len(_runbk.job_full_paths)}] Job Definitions")
        if _runbk.relFilePath not in _deadline_rows.keys():
            _deadline_rows[_runbk.relFilePath] = {}
        for _row in _runbk._runbook_data_table_obj:
            _sub_data_row = {}
            if (('Full Path') in _row.keys() and 
                _row['Full Path'] is not None and 
                'Deadline' in _row.keys() and
                _row['Deadline'] is not None
            ):
                if 'Full Path' not in _sub_data_row.keys():
                    _sub_data_row['Full Path'] = _row['Full Path']
                if 'Deadline' not in _sub_data_row.keys():
                    _sub_data_row['Deadline'] = _row['Deadline']
            if len(_sub_data_row) >= 1:
                _deadline_rows[_runbk.relFilePath] = _sub_data_row
        if len(_deadline_rows[_runbk.relFilePath].keys()) == 0:
            
            del _deadline_rows[_runbk.relFilePath]
            _missing_deadline_rows.append(_runbk.relFilePath)
    log.debug(f"Found a total of [{len(_deadline_rows)}] items marrked for Deadline updates in runbooks")
    log.blank(ToolBox.Foramt_list_of_dictionaries_to_multiline_str(list(_deadline_rows.values())))


    log.debug(f"Found a total of [{len(_missing_deadline_rows)}] provided but does not contain any values the  'Deadline' column")
    log.blank(data=_missing_deadline_rows, list_data_as_table=True, column_count=1)

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    Contract_Name = 'MSXIX'
    Ticket_Number = 'RITM0244144'
    Source_Path = 'C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\MSXIX\\'
    Working_Path = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\"
    Output_folder_name = 'DEADLINE_added'
    # Capture current date and time when script begins
    _start_time = dt.now()
    
    _working_path:str = os.path.join (Working_Path, f"{Contract_Name}_{Ticket_Number}")
    log.init_logger(log_folder=_working_path, log_file=f"{Contract_Name}_{Ticket_Number}_{_start_time.strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {Ticket_Number} under contract : {Contract_Name}")
    _output_path:str = os.path.join (_working_path, Output_folder_name)
    
    ToolBox.collect_files_as_nodes(
        source_dir = Source_Path,
        isolate_directory_names=['PROD'],
        isolate_formats=['jil', 'job'],
        quite_logging=True
    )
    #
    #ToolBox.load_file_nodes(
    #    skip_duplicates=False, 
    #    quite_logging=True
    #    )
    #log.info (f"Total Nodes being Tracked :[{len(ToolBox)}]")
    #log.blank('-'*100)
    
    ToolBox.collect_files_as_nodes(
        source_dir = _working_path,
        isolate_formats=['xlsx'],
        quite_logging=True
    )

    Action_Add_DEADLINE_to_streams(
        Output_Folder_path=_output_path
    )
    
    log.critical(f"End of log for ticket : {Ticket_Number} under contract : {Contract_Name}")
    log .info (f"Script processing time : {dt.now() - _start_time}")

    print ("Complete.")