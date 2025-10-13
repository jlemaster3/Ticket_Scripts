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

contract = 'PRXIX'
ticketNumber = 'RITM0221064'

source_path = "C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\PRXIX"
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


def Step_1 (sourcePath:str, outputPath:str, namedLists:dict[str, list[str]] = None) :
    _paths = ToolBox_Gather_Directories(
        source_dir = sourcePath
    )
    _filelist = ToolBox_Gather_Files( 
        source_dir = sourcePath, 
        isolate_fileName_names = namedLists["Stream_Name_filter"],
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
        log.blank("-"*32)
        # Process missing files
        _paths_missing_file = list(set(_app_paths) - set(_found_relpaths))
        if len(_paths_missing_file) >= 1:
            Create_Missing_Varients_by_Environment (_prdFile, _paths_missing_file, outputPath, namedLists)                
        log.label(f"End Processing for File '{_prdFile.relFilePath}'")
        log.blank("-"*100)
    log.blank("-"*100)
    log.info (f"Total number of files missing that where created : [{duplicates_created}]")
    log.info (f"Total number of files in Non-Production counterpart files for PROD files : [{files_compared}]")
            
            

        


#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{dt.now().strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")
    log.critical(f"", data = {
        "requirment 1" : "All job stream/runbooks listed below in non-prod environments should have the frequency set to 'ON REQUEST'. ",
        "requirment 2" : 'For all non-prod environment jobs under the listed below listed job stream/runbooks',
        "requirment 2 A" : '    - Job stream Draft should be set to “FALSE”.',
        "requirment 2 B" : '    - Jobs Operation (NOP) should be set to “FALSE”.',
        "Job Stream List" : [
            "PD5MGD_834INB",
            "PD5MGD_834RSTRMV",
            "PD5MGD_834RSTR_A",
            "PD5MGD_834RSTR_B",
            "PD5MGD_834RSTR_C",
            "PD5MGD_ASGNRPT",
            "PD5MGD_RATECELL",
            "PMMGD_820_RLS",
            "PMMGD_834RPTS",
            "PMMGD_834RSTR",
            "PMMGD_CAP_820",
            "PMMGD_CAP_ADJCYC",
            "PMMGD_CAP_CYC_MN",
            "PMMGD_CAP_FCST",
            "PMMGD_CAP_OTP",
            "PMMGD_CAP_RPT",
            "PMMGD_CMS64",
            "PMMGD_RATECELL",
            "PMMGD_SUBCAP"
        ], 
        "requirment 3" : 'Some jobs are missing in non-prod environments compared to the PROD. To add the missing jobs along with their respective Predecessors to ensure Synchronization with PROD.',
        "requirment 4" : 'Some job streams are also missing in non-prod environment workstation. These should be created with frequency set to “ON REQUEST”',
        "requirment 5" : 'No changes are required for job streams or jobs that exists in non-prod environment but not in PROD.',
        "PROD Workstation" : {
            "/PRXIX/MIS/PROD/" : "/PRXIX/PRPRODLBATCH001 - @BAT1#"
        },
        "Non-PROD Workstations" : {
            "/PRXIX/MIS/TEST/" : "/PRXIX/PRTSTLBATCH001 - @BAT1#",
            "/PRXIX/MIS/TESTA/" : "/PRXIX/PRTSTLBATCH001 - @BAT1#",
            "/PRXIX/MIS/TESTB/" : "/PRXIX/PRTSTLBATCH001 - @BAT1#",
            "/PRXIX/MIS/TESTB/" : "/PRXIX/PRTSTLBATCH002 - @BAT2#",
            "/PRXIX/MIS/MOD/" : "/PRXIX/PRMODLBATCH001 - @BAT1#",
            "/PRXIX/MIS/MODA/" : "/PRXIX/PRMODLBATCH001 - @BAT1#",
            "/PRXIX/MIS/MODB/" : "/PRXIX/PRMODLBATCH001 - @BAT1#",
            "/PRXIX/MIS/MODB/" : "/PRXIX/PRTSTLBATCH002 - @BAT2#",
            "/PRXIX/MIS/UAT/" : "/PRXIX/PRUATLBATCH001 - @BAT1#",
            "/PRXIX/MIS/UATB/" : "/PRXIX/PRUATLBATCH001 - @BAT1#"
        },
        "Added Requirment 6" : "If a Job Stream or Job is found in PROD that does not exist in either MODB or TESTB and is set to use '@BAT1' as the workstation, Duplicate the '@BAT1' Jobs and Jobs Streams and point the duplciate to '@BAT2' within the same *.jil File."
    }, list_data_as_table=True, column_count=4)

    Step_1(
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
            ], # environment charecter has been removed
            "Stream_Name_filter": [
                "MGD",
                "CMS"
            ]
        }
    )

    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    print ("complete")