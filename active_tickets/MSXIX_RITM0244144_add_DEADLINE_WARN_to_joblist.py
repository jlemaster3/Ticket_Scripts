#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, sys, copy, re
from datetime import datetime as dt
from typing import Any

## Imports ToolBox, and log
_curr_dir = os.path.dirname(os.path.abspath(__file__))
_prnt_dir = os.path.dirname(_curr_dir)
sys.path.append(_prnt_dir)
from ToolBox_ECS_V1 import *


#-------------------------------------------------
#   Steps
#-------------------------------------------------


def Action_Add_DEADLINE_to_streams (
    Output_Folder_path:str ,
    quite_logging:bool = True
):
    """For each file in source path, find all IWS assets, and duplicate them, then preform a search and replace on teh duplicated assest's text.
    Append the duplcated and udpated text to the current file, and save a copy of the file to a new location for review."""
    
    _target_name_to_deadline:dict[str,str] = {}
    _target_deadline_objects:dict[str, str] = {}
    _target_deadline_with_notes:dict[str, str] = {}
    for _file_node in ToolBox.XLSX_file_nodes:
        _file_node.open_file(quite_logging= quite_logging)    
        for _row in _file_node._sheets_as_tables['Job List']:
            _job_name = _row['IWS - Prod Job Name']
            _add_deadLine = True if any([str(_row['DEADLINE 0400 WARN? (Y/N)']).lower() == _v.lower() for _v in ['Y','y','1','true']]) else False
            _has_notes = False if (_row['Notes'] is None) or (str(_row['Notes']).strip() == '') else True
            _target_name = f"{_job_name}"
            if _add_deadLine == True and _has_notes == False:
                if _target_name not in _target_deadline_objects.keys():
                    _target_deadline_objects[_target_name] = 'DEADLINE 0400 WARN'
                    _target_name_to_deadline[_target_name] = 'DEADLINE 0400 WARN'
            elif _add_deadLine == True and _has_notes == True:
                if _target_name not in _target_deadline_with_notes.keys():
                    _target_deadline_with_notes[_target_name] = _row['Notes']
        if (quite_logging != True): log.blank(ToolBox.Foramt_list_of_dictionaries_to_multiline_str(_file_node._sheets_as_tables['Job List']))
        log.info (f"numebr of items to set DEDALINE at 0400 without special notes : [{len(_target_deadline_objects)}]")
        _found_table_list:list[dict[str, str]] = [{"Job Name": str(_k), "DEADLINE 0400 WARN? (Y/N)":"Y", "Note":_v} for _k,_v in _target_deadline_objects.items()]
        log.blank(ToolBox.Foramt_list_of_dictionaries_to_multiline_str(_found_table_list))
        log.blank('-'*100)
        log.info (f"numebr of items to set DEADLINE 0400 and WARN with special notes : [{len(_target_deadline_with_notes)}]")
        _found_table_list_with_notes:list[dict[str, str]] = [{"Job Name": str(_k), "DEADLINE 0400 WARN? (Y/N)":"Y", "Note":_v} for _k,_v in _target_deadline_with_notes.items()]
        if len(_found_table_list_with_notes) >= 1:
            log.info (f"Item do not match criteria and are being exlcuded from list : ")
            log.blank(ToolBox.Foramt_list_of_dictionaries_to_multiline_str(_found_table_list_with_notes))
            log.blank('-'*100)
    #_deadline_rows:list[dict[str,str]] = []
    #for _runbk in ToolBox.IWS_Runbook_file_nodes:
    #    log.info(f"runbook : '{_runbk.relFilePath}' contains [{len(_runbk.job_stream_full_paths)}] Job Stream and [{len(_runbk.job_full_paths)}] Job Definitions")
    #    for _row in _runbk._runbook_data_table_obj:
    #        if (_row['Deadline'] is not None and 
    #            _row['Full Path'] is not None and
    #            _row['Object Type'] is not None
    #        ):
    #            _target_name = _row['Full Path'].split('/')[-1]
    #            if _row['Object Type'] == 'Job Stream':
    #                _target_name = _target_name.split('.')[0]
    #            elif _row['Object Type'] == 'Job':
    #                _target_name = _target_name.split('.')[-1]
    #            _target_name_to_deadline[_target_name] = _row['Deadline']
    #            _deadline_rows.append({
    #                'Full Path':_row['Full Path'],
    #                'Object Type':_row['Object Type'],
    #                'Deadline':_row['Deadline'],
    #            })
    #log.blank(ToolBox.Foramt_list_of_dictionaries_to_multiline_str([_r for _r in _deadline_rows]))
    #log.blank('-'*100)

    _files_to_edit:dict[str,list[str]] = {}
    _found:list[str] = []
    for _node in ToolBox.IWS_object_nodes:
        _node_name = _node.name.replace('{E}', 'P').replace('{ENV}','PROD')
        if _node_name in _target_name_to_deadline.keys():
            _found.append(_node_name)
            if _node.sourceFile_Path not in _files_to_edit:
                _files_to_edit[_node.sourceFile_Path] =[]
            _files_to_edit[_node.sourceFile_Path].append(_node_name)
            deadline_settings = _target_name_to_deadline[_node_name]
            
            _dl_time = re.search(r'(\d{4})',deadline_settings, re.IGNORECASE)
            _dl_time = _dl_time.group(1) if _dl_time is not None else "0400"
            _dl_plus_minus_day = re.search(r'([+-] ?\d*)\s*[Dd][Aa][Yy]',deadline_settings, re.IGNORECASE)
            _dl_plus_minus_day = _dl_plus_minus_day.group(1) if _dl_plus_minus_day is not None else None
            
            log.info(f"Setting '{_node.full_path}' Deadline to : '{deadline_settings}'", data=[('time',_dl_time),('day_offset',_dl_plus_minus_day)])
            _node.set_DEADLINE(time_hhmm=_dl_time,day_offset=_dl_plus_minus_day)
            log.blank('-'*100)
    _total = sum([len(_v) for _v in _files_to_edit.values()])
    
    print (f'total found {_total} in {len(_files_to_edit.keys())}')
    
    for _jil_file in ToolBox.JIL_file_nodes:
        #log.blank(_jil_file.node_stricture_to_string())
        _jil_file.save_File(Output_Folder_path, useRelPath=True, quite_logging= False, skip_unchanged=True)
    

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
#        isolate_fileName_names= [
#            "PAELG_REPORTS",
#            "PBBUY_COBA_RECV",
#            "PBBUY_COBA_SEND",
#            "PD5BUY_DREPORTS",
#            "PD5BUY_DSTATE",
#            "PD5ELG_ID_CARD",
#            "PD5ELG_INT_RPTS",
#            "PD5ELG_LU_RPTS",
#            "PD5MGD_ENROLL",
#            "PD5MGD_INIT",
#            "PD5MGD_ROSTER",
#            "PD5MGD_UPD_MAIL",
#            "PD5PRV",
#            "PD5RBT_JOBS",
#            "PD7EDI_RPTS",
#            "PD7PAU",
#            "PD7PRV_7",
#            "PMBUY_EOM_RPTS",
#            "PMBUY_MBILL_RPTS",
#            "PMCTM",
#            "PMEDI_RPTS",
#            "PMELG_REPORTS",
#            "PMMGD",
#            "PMMGD_1ST_MONTH",
#            "PMMGD_2WK_BF_RST",
#            "PMMGD_3RD_WED",
#            "PMMGD_CAP_AFT_FN",
#            "PMMGD_CAP_SUM",
#            "PMMGD_LASTCALDAY",
#            "PMMGD_ROSTER",
#            "PMPAU_REPORTS",
#            "PMPRV",
#            "PMRBT_JOBS",
#            "PQELG_REPORTS",
#            "PQPRV",
#            "PRPRV_ANNUAL",
#            "PRRBT_ORQST",
#            "PWBUY_WREPORTS",
#            "PWEDI_RPTS",
#            "PWELG_DUP_RPT",
#            "PWELG_REPORTS",
#            "PWPAU",
#            "PWPRV",
#            "PWRBT_JOBS",
#            "PADUR_PD10",
#            "PD5CLM_PBA_EXTR",
#            "PD6CLM_205",
#            "PD7CLM_DBRD_STAT",
#            "PD7CLM_RPT_LATE",
#            "PD7CLM_VERINT",
#            "PD7FIN_RPT_MOVE",
#            "PD7REF_DRUG_INFO",
#            "PD7REF_PROC_INFO",
#            "PM1SATCLM_EOM",
#            "PMDUR_FDB_LOAD",
#            "PMDUR_PD10",
#            "PQCLM",
#            "PQFIN_FP",
#            "PWCLM_RATEADJ",
#            "PWFRICLM_205",
#            "PWFRICLM_EOW",
#            "PWFRICLM_EXW",
#            "PWREF061",
#            "PWREF062",
#            "PWREF063",
#            "PWREF_FDB_UPD",
#            "PWREF_WW00",
#            "PWSUNENC_RESP"
#        ],
        quite_logging=True
    )
    
    ToolBox.load_file_nodes(
        skip_duplicates=False,
        quite_logging=True,
        enable_post_porcesses = True
        )
    
    ToolBox.collect_files_as_nodes(
        source_dir = _working_path,
        isolate_formats=['xlsx'],
        quite_logging=True
    )
    
    Action_Add_DEADLINE_to_streams(
        Output_Folder_path=_output_path
    )
    
    log.blank('-'*100)
    log.blank(ToolBox.node_stats)
    log.blank('-'*100)

    log.critical(f"End of log for ticket : {Ticket_Number} under contract : {Contract_Name}")
    log .info (f"Script processing time : {dt.now() - _start_time}")

    print ("Complete.")