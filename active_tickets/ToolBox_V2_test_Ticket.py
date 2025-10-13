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

source_path = "C:\\VS_Managed_Accounts\\PRXIX"
# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")


duplicates_created:int = 0
files_compared:int = 0

#-------------------------------------------------
#   Steps
#-------------------------------------------------

def Compare_Streams_by_Environment (source_file:ToolBox_IWS_JIL_File, target_file_list:list[ToolBox_IWS_JIL_File], outputPath:str,namedLists:dict[str, list[str]] = None) :
    log.info(f"Found a total of [{len(target_file_list)}] matching non-Production varients for '{source_file.relFilePath}' in the following paths : ",
        data=list([_f.relFilePath for _f in target_file_list]),
        list_data_as_table=True,
        column_count = 8
        )
    for _compare_counter, _compFile in enumerate(target_file_list):
        log.blank(f'{"-"*32} [{_compare_counter + 1}]')
        log.label(f"Found non-PROD file '{_compFile.relFilePath}' to compare aginst PROD file '{source_file.relFilePath}'")
        _compFile.open_file()
        Action_IWS_JIL_merge_Streams_A_B (
            file_A = source_file,
            file_B = _compFile,
            include_jobs = True
        )
        _found_name = True if any(_cn.upper() in _compFile.sourceFilePath for _cn in namedLists["Job_Stream_List"]) else False
        if _found_name == True :
            log.debug(f"File name : '{source_file.name}' was found to match a term in the list : 'Job_Stream_List'.")
            source_file.set_all_Stream_ONREQUEST(True)
            source_file.set_all_Streams_DRAFT(False)
            source_file.set_all_Jobs_NOP(False)
        for _env in namedLists['BAT2_Environment_checkList']:
            if _env.upper() in _compFile.relPath.upper():
                log.debug(f"Target output folder contains '{_env}', checking for '@BAT2' workstation in file.")
                Action_IWS_JIL_sync_streams_A_B (
                    file = _compFile,
                    source_filter = '@BAT1#',
                    target_filter= '@BAT2#'
                )
        _compFile.save_File(outputPath, useRelPath = True)
        _compFile.close_file()
        source_file.close_file()
        global files_compared
        files_compared += 1


def Create_Missing_Varients_by_Environment (source_file:ToolBox_IWS_JIL_File, missing_dir_list:list[str], outputPath:str,namedLists:dict[str, list[str]] = None ):
    log.label(f"File '{source_file.relFilePath}' is missing [{len(missing_dir_list)}] in the following paths : ", 
        data=missing_dir_list,
        list_data_as_table=True,
        column_count = 9
    )
    for _missing_counter, _missingDir in enumerate(missing_dir_list):
        log.blank(f'{"-"*32} [{_missing_counter + 1}]')
        log.debug(f"Creating File '{os.path.join(_missingDir,source_file.name, source_file.foramt)}'")
        _found_name = True if any(_cn.upper() in source_file.sourceFilePath for _cn in namedLists["Job_Stream_List"]) else False
        source_file.open_file()
        if _found_name == True :
            log.debug(f"File name : '{source_file.name}' was found to match a term in the list : 'Job_Stream_List'.")
            source_file.set_all_Stream_ONREQUEST(True)
            source_file.set_all_Streams_DRAFT(False)
            source_file.set_all_Jobs_NOP(False)
        else:
            source_file.set_all_Stream_ONREQUEST(True)
        for _env in namedLists['BAT2_Environment_checkList']:
            if _env.upper() in _missingDir.upper():
                log.debug(f"Target output folder contains '{_env}', checking for '@BAT2' workstation refrence in file.")
                Action_IWS_JIL_duplicate_streams (source_file, '@BAT1#', '@BAT2#')
        source_file.save_File(outputFolder = os.path.join(outputPath, _missingDir), useRelPath = False)
        source_file.close_file()
        global duplicates_created
        duplicates_created += 1


def step_1 (sourcePath:str, outputPath:str, namedLists:dict[str, list[str]] = None) :
    _paths = ToolBox_Gather_Directories(
        source_dir = sourcePath
    )
    _filelist = ToolBox_Gather_Files( 
        source_dir = sourcePath, 
        #isolate_directory_names = ['TEST', 'MOD', 'UAT', 'PROD'],
        isolate_fileName_names = ["Temp_test"],
    )   
    _prd_files:list[ToolBox_IWS_JIL_File] = []
    _npr_files:list[ToolBox_IWS_JIL_File] = []
    for _file in _filelist:
        if 'PROD' in _file.relPath.upper():
            _prd_files.append(_file)
        else:
            _npr_files.append(_file)
    
    for _prdFile in _prd_files:
        log.blank("-"*100)
        log.label(f"Processing File '{_prdFile.relFilePath}'")
        _compare_files:list[ToolBox_IWS_JIL_File] = []
        _app_paths = [_p for _p in _paths if _prdFile.relPath.split('\\')[1].upper() in _p.upper() and _p not in _prdFile.relPath]
        _found_relpaths:list[str] = []
        for _nprFile in _npr_files:
            if _prdFile.name == _nprFile.name:
                if _nprFile.relPath not in _found_relpaths:
                    _found_relpaths.append(_nprFile.relPath)
                _compare_files.append (_nprFile)
        # Process found counterparts
        Compare_Streams_by_Environment (_prdFile, _compare_files, outputPath, namedLists)
        log.blank("-"*75)    
        # Process missing files
        _paths_missing_file = list(set(_app_paths) - set(_found_relpaths))
        #if len(_paths_missing_file) >= 1:
        #    Create_Missing_Varients_by_Environment (_prdFile, _paths_missing_file, outputPath, namedLists)
        log.label(f"End Processing for File '{_prdFile.relFilePath}'")
        log.blank("-"*100)
    log.blank("-"*100)
    log.info (f"Total number of files missing that where created : [{duplicates_created}]")
    log.info (f"Total number of files in Non-Production counterpart files for PROD files : [{files_compared}]")     


#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    _start_time = dt.now()
    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{_start_time.strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")

    step_1(
        sourcePath = source_path,
        outputPath = os.path.join(working_directory,"testing"),
        namedLists = {
            "Test_List" : ["Temp_test"],
            "BAT2_Environment_checkList" : ["MODB", "TESTB"],
            "Job_Stream_List" : [
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
            ] # environment charecter has been removed
        }
    )

    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    log .info (f"Script processing time : {dt.now() - _start_time}")
    print ("complete")