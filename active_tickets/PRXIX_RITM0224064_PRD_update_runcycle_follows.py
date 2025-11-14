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

contract = 'PRXIX'
ticketNumber = 'RITM0224064'

source_path = f"C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\PRXIX"

# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")

#-------------------------------------------------
#   Steps
#-------------------------------------------------

def Action_compare_configs_in_file (
        source_jil_node:ToolBox_IWS_JIL_File_Node,
        target_jil_nodes:list[ToolBox_IWS_JIL_File_Node],
        output_root_path:str
    ):
    """"""
    log.blank('='*100)
    log.info (f"Loading source and target file data")
    source_jil_node.open_file(
        enable_post_porcesses=False,
        quite_logging=False
    )
    
    _source_stream_start_matchs = re.finditer(ToolBox.REGEX_Patterns.IWS_STREAM_START_LINE, source_jil_node._modified_file_text, re.IGNORECASE|re.MULTILINE) if source_jil_node._modified_file_text is not None else []
    _source_stream_edge_matchs = re.finditer(ToolBox.REGEX_Patterns.IWS_STREAM_EDGE_LINE, source_jil_node._modified_file_text, re.IGNORECASE|re.MULTILINE) if source_jil_node._modified_file_text is not None else []
    _source_stream_config_lines:dict[str, str] = {}
    for _obj_idx, (_start_obj, _edge_obj) in enumerate(zip(_source_stream_start_matchs,_source_stream_edge_matchs)):
        _config_lines = source_jil_node._modified_file_text[_start_obj.start() : _edge_obj.end()] if source_jil_node._modified_file_text is not None else ''
        _source_stream_config_lines[''.join([_start_obj.groupdict()[_k] for _k in _start_obj.groupdict().keys()])] = _config_lines
    for _nonP_coutner, _target_node in enumerate(target_jil_nodes):
        _target_node.open_file(
        enable_post_porcesses=False,
        quite_logging=True
        )
        _target_stream_start_matchs = re.finditer(ToolBox.REGEX_Patterns.IWS_STREAM_START_LINE, _target_node._modified_file_text, re.IGNORECASE|re.MULTILINE) if _target_node._modified_file_text is not None else []
        _target_stream_edge_matchs = re.finditer(ToolBox.REGEX_Patterns.IWS_STREAM_EDGE_LINE, _target_node._modified_file_text, re.IGNORECASE|re.MULTILINE) if _target_node._modified_file_text is not None else []
        _target_file_lines:list[str] = _target_node._modified_file_text.splitlines() if _target_node._modified_file_text is not None else []
        _target_file_changed:bool = False
        _insert_collection:dict[int,str] = {}
        for _obj_idx, (_start_obj, _edge_obj) in enumerate(zip(_target_stream_start_matchs,_target_stream_edge_matchs)):
            _line_offset_index:int = _target_file_lines.index(_start_obj.group(0).strip()) if _start_obj.group(0).strip() in _target_file_lines else 0
            _target_stream_full_path = ''.join([_start_obj.groupdict()[_k] for _k in _start_obj.groupdict().keys()])
            _source_config_lines = next((_source_stream_config_lines[key] for key in _source_stream_config_lines if _target_stream_full_path.split('#')[-1].upper() in key.upper()), None)
            _source_runcycle_lines = [_l for _l in _source_config_lines.splitlines() if 'runcycle'.upper() in _l.upper()] if _source_config_lines is not None else []
            _target_config_lines = _target_node._modified_file_text[_start_obj.start() : _edge_obj.end()].splitlines() if _target_node._modified_file_text is not None else []
            _target_runcycle_lines = [_l for _l in _target_config_lines if 'runcycle'.upper() in _l.upper()]
            if (len(_source_runcycle_lines) >= 1):
                for _source_line_idx, _source_line in enumerate(_source_runcycle_lines):
                    if (_source_line not in _target_runcycle_lines):
                        _insert_idx:int = _line_offset_index
                        for _t_idx, _t_line in enumerate(_target_config_lines):
                            if 'ON REQUEST' in _t_line.upper():
                                _insert_idx += _t_idx + 1
                                break
                            elif 'MATCHING' in _t_line.upper():
                                _insert_idx += _t_idx 
                                break
                        if _insert_idx is not None:
                            _insert_collection[_insert_idx] = f"{_source_line.strip()}"
                            _target_file_changed = True
        if _target_file_changed:
            _key_order = sorted(_insert_collection.keys(), reverse=True)
            for _key in _key_order:
                _target_file_lines.insert(_key, _insert_collection[_key])
            _target_node._modified_file_text = '\n'.join(_target_file_lines)
            _target_node.save_File(
                outputFolder= output_root_path,
                useRelPath= True,
            quite_logging= False
            )

        _target_node.close_file(
        quite_logging=True
        )
    source_jil_node.close_file(
        quite_logging=True
    )
    log.blank('='*100)

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------
if __name__ == "__main__":
    _start_time = dt.now()
    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_runcycles_{_start_time.strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")
    
    _output_path = os.path.join(working_directory, "runcycle_updates")

    _file_name_terms:list[str] =[
        "D5MGD_834INB",
        "D5MGD_834RSTRMV",
        "D5MGD_834RSTR_A",
        "D5MGD_834RSTR_B",
        "D5MGD_834RSTR_C",
        "D5MGD_ASGNRPT",
        "D5MGD_RATECELL",
        "MMGD_820_RLS",
        "MMGD_834RPTS",
        "MMGD_834RSTR",
        "MMGD_CAP_820",
        "MMGD_CAP_ADJCYC",
        "MMGD_CAP_CYC_MN",
        "MMGD_CAP_FCST",
        "MMGD_CAP_OTP",
        "MMGD_CAP_RPT",
        "MMGD_CMS64",
        "MMGD_RATECELL",
        "MMGD_SUBCAP"
    ]

    ToolBox.collect_files_as_nodes(
        source_dir = source_path,
        isolate_fileName_names= _file_name_terms,
        isolate_formats=['jil','job'],
        quite_logging=True
    )

    _prod_file_list:list[ToolBox_IWS_JIL_File_Node] = [_n for _n in ToolBox.JIL_file_nodes if 'PROD' in _n.sourcePath.upper()]
    _nonprod_file_list:list[ToolBox_IWS_JIL_File_Node] = [_n for _n in ToolBox.JIL_file_nodes if 'PROD' not in _n.sourcePath.upper()]

    
    for _prod_counter, _prod_file_node in enumerate(_prod_file_list):
        if _prod_counter >= 2 : break
        log.info (f"[{_prod_counter+1}] Processing PROD file : '{_prod_file_node.relFilePath}'")
        _prd_file_name_minus_env = _prod_file_node._file_name[1:]
        _non_prod_list:list[ToolBox_IWS_JIL_File_Node] = [_n for _n in _nonprod_file_list if _prd_file_name_minus_env.upper() in _n._file_name.upper()]
        Action_compare_configs_in_file(_prod_file_node, _non_prod_list, _output_path)
    
    log.blank('='*100)
    log.blank(ToolBox.dataSilo.statistics)
    log.blank('='*100)
    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    log .info (f"Script processing time : {dt.now() - _start_time}")
    print ("Complete.")