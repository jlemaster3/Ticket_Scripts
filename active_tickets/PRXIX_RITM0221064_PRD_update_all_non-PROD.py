#-------------------------------------------------
#   About
#-------------------------------------------------

'''
Ticket RITM0221064

1)	All job stream/runbooks listed below in non-prod environments should have the frequency set to “ON REQUEST”. 
2)	For all non-prod environment jobs under the listed below listed job stream/runbooks:
•	Job stream Draft should be set to “FALSE”.
•	Jobs Operation (NOP) should be set to “FALSE”.
3)	Some jobs are missing in non-prod environments compared to the PROD. To add the missing jobs along with their respective Predecessors to ensure Synchronization with PROD.
4)	Some job streams are also missing in non-prod environment workstation. These should be created with frequency set to “ON REQUEST”
5)	No changes are required for job streams or jobs that exists in non-prod environment but not in PROD.

for TEST, TESTA, TESTB, MOD, MODA, MODB, UAT, UATB

'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, sys
from datetime import datetime as dt

## Imports ToolBox, and log
_curr_dir = os.path.dirname(os.path.abspath(__file__))
_prnt_dir = os.path.dirname(_curr_dir)
sys.path.append(_prnt_dir)
from ToolBox import *

#-------------------------------------------------
#   Variables
#-------------------------------------------------

contract = 'PRXIX'
ticketNumber = 'RITM0221064'

source_path = "C:\\VS_Managed_Accounts\\PRXIX"
# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")

#-------------------------------------------------
#   Steps
#-------------------------------------------------

def step_1 (sourcePath:str, workingDirectory:str, outputputRootPath:str, outputUsingRelPaths:bool=True, compareFolders:list[str]=None, namedLists:dict[str, list[str]] = None, quite_logging=True):
    """Collect files by sub-directory comapred to source path for comparisons."""
    log.critical (f"Starting Step 1")
    if (not os.path.isdir(sourcePath)):
        log.error (f"Target source path is not a valid Directory Path : '{sourcePath}'")
        return
    if (not os.path.exists(sourcePath)):
        log.error (f"Target source path does not exists : '{sourcePath}'")
        return
    
    if (not os.path.isdir(workingDirectory)):
        log.error (f"Target Working Directory is not a valid directory path : '{workingDirectory}'")
        return
    os.makedirs(workingDirectory, exist_ok=True)
    if (outputputRootPath == None):
        # if output directory is note provided use working directory
        outputputRootPath = working_directory
    log.info (f"Gathering IWS *.jil and *.job files from source : '{sourcePath}'")
    _file_collection = gather_files(
        source_path = sourcePath, 
        isolate_name_terms = namedLists["Job_Stream_List"],
        quite_logging = quite_logging
    )

    _collected_lists:dict[str,list[ToolBox_IWS_JIL_File]] = {}

    for _subPath, _fileList in _file_collection.items():
        for _comPath in compareFolders:
            if (_comPath.upper() in _subPath.upper()) and (_comPath.upper() != _subPath.upper()):
                if _subPath not in _collected_lists.keys():
                        _collected_lists[_subPath] = []
        for _file in _fileList:
            if (compareFolders != None) and (len(compareFolders) >= 1):
                if any(_cp.upper() in _file.sourceFileDirRelPath.upper() for _cp in compareFolders):
                    if _file.sourceFileDirRelPath not in _collected_lists.keys():
                        _collected_lists[_file.sourceFileDirRelPath] = []
                    _collected_lists[_file.sourceFileDirRelPath].append(_file)

    _PROD_key_list:list[str] = [key for key in _collected_lists.keys() if 'PROD' in key]
    _UAT_key_list:list[str] = [key for key in _collected_lists.keys() if 'UAT' in key]
    _MOD_key_list:list[str] = [key for key in _collected_lists.keys()  if 'MOD' in key]
    _TEST_key_list:list[str] = [key for key in _collected_lists.keys()  if 'TEST' in key]
    _merged_paths = list(set(_UAT_key_list + _MOD_key_list + _TEST_key_list))
    _common_prefix = os.path.commonprefix(_PROD_key_list)
    _saved_file_count = 0
    for _prd_relativePath in _PROD_key_list:
        for _prd_file in _collected_lists[_prd_relativePath]:
            log.info (f"Processing file : '{os.path.join(_file.sourceFileDirRelPath, _file.sourceFileName)}'")
            _target_relPaths =  [_path for _path in _merged_paths if _prd_relativePath.removeprefix(_common_prefix) in _path]
            _found_files = [_f for _p in _merged_paths for _f in _collected_lists[_p] if _prd_file.sourceFileBaseName[1:].upper() in _f.sourceFileName.upper()]
            _found_relPaths = [_f.sourceFileDirRelPath for _f in _found_files]            
            _relPaths_missing_file = list(set(_target_relPaths) - set(_found_relPaths))
            for _file in _found_files:
                # check and udpate file
                log.debug (f"Found copy of file : '{os.path.join(_prd_relativePath, _prd_file.sourceFileName)}' in path : '{os.path.join(_file.sourceFileDirRelPath, _file.sourceFileName)}', checking file.")
                _target_outgoing = os.path.join(outputputRootPath, _file.sourceFileDirRelPath)
                merge_missing_streams_A_to_B(
                    file_A=_prd_file,
                    file_B=_file,
                )
                _found_name = True if any(_cn.upper() in _file.sourceFileName.upper() for _cn in namedLists["Job_Stream_List"]) else False
                if _found_name == True :
                    log.debug(f"File name : '{_file.sourceFileBaseName}' was found to match a term in the list : 'Job_Stream_List'.")
                    _file.set_Streams_ONREQUEST(True)
                    _file.set_Streams_DRAFT(False)
                    _file.set_Jobs_NOP(False)

                for _e in namedLists['BAT2_Environment_checkList']:
                    if _e.upper() in _target_outgoing.upper():
                        log.debug(f"Target output folder contains '{_e}', checking for '@BAT2' workstation refrence in file.")
                        _found_bat2 = True if any (["@BAT2#" in _path for _path in _file.jobStreamPaths()]) else False
                        if _found_bat2 == True:
                            # Bat2 found compare bat1 to bat2
                            sync_streams_in_file (_file, {"@BAT1#" : "@BAT2#"})
                        else:
                            # BAT2 not found
                            log.debug(f"Can't find workstation refrerence to '@BAT2#' in file : '{os.path.join(_file.sourceFileDirRelPath, _file.sourceFileName)}', duplicating strems from workstation '@BAT1#' on workstation '@BAT2#'.")
                            for _js_path in _file.jobStreamPaths():
                                _jsName = _js_path.split('/')[-1].split('.')[0]
                                _file.duplciate_jobStream_by_workstaion(_jsName, '@BAT1#', '@BAT2#')

                _file.saveFileTo(outputputRootPath, useRelPath=True)
                _saved_file_count += 1
                _file.closeFile()
                _prd_file.closeFile()

            for _missingPath in  _relPaths_missing_file:
                log.debug (f"File : '{os.path.join(_prd_relativePath, _prd_file.sourceFileName)}' is missing in path : '{_missingPath}', creating copy.")
                _target_outgoing = os.path.join(outputputRootPath, _missingPath)
                _prd_file.openFile()
                _prd_file._reload_streams_and_jobs()
                _found_name = True if any(_cn.upper() in _prd_file.sourceFileName.upper() for _cn in namedLists["Job_Stream_List"]) else False
                if _found_name == True :
                    log.debug(f"File name : '{_prd_file.sourceFileBaseName}' was found to match a term in the list : 'Job_Stream_List'.")
                    _prd_file.set_Streams_ONREQUEST(True)
                    _prd_file.set_Streams_DRAFT(False)
                    _prd_file.set_Jobs_NOP(False)
                else:
                    _prd_file.set_Streams_ONREQUEST(True)
                
                for _e in namedLists['BAT2_Environment_checkList']:
                    if _e.upper() in _target_outgoing.upper():
                        log.debug(f"Target output folder contains '{_e}', checking for '@BAT2' workstation refrence in file.")
                        for _path in _prd_file.jobStreamPaths():
                            _found_bat2 = True if any (["@BAT2#" in _path for _path in _file.jobStreamPaths()]) else False
                            if _found_bat2 == False:
                                log.debug(f"can't find '@BAT2#' workstation version in file : '{os.path.join(_prd_file.sourceFileDirRelPath, _prd_file.sourceFileName)}', duplicating '@BAT1#' streams")
                                for _js_path in _prd_file.jobStreamPaths():
                                    _jsName = _js_path.split('/')[-1].split('.')[0]
                                    _target_stream = _prd_file.duplciate_jobStream_by_workstaion(_jsName, '@BAT1#', '@BAT2#')
                                    if _target_stream is not None:
                                        _target_stream.set_ONREQUEST(True)                                
                _prd_file.saveFileTo(_target_outgoing, useRelPath=False)
                _saved_file_count += 1
                _prd_file.closeFile()
    log.info (f"updated a total of [{_saved_file_count}] files.")
    log.critical (f"Completed Step 1")


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
    })

    step_1 (
        sourcePath = source_path,
        workingDirectory = working_directory,
        outputputRootPath = os.path.join (working_directory, 'step_1_old'),
        outputUsingRelPaths = True,
        compareFolders = [
            "PROD", 
            "MOD","MODA","MODB",
            "TEST", "TESTA", "TESTB", 
            "UAT", "UATA", "UATB"
        ],
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
    log.critical(f"Ending log for ticket : {ticketNumber} under contract : {contract} - Processing Complete.")