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
import os
from ..ToolBox import *
from datetime import datetime as dt
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
_saved_file_count = 0
def step_1 (sourcePath:str, workingDirectory:str, outputputRootPath:str, outputUsingRelPaths:bool=True, compareFolders:list[str]=None, streamNameGroups:dict[str, list[str]] = None, quite_logging=True):
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
    _FileList = gather_files(sourcePath, quite_logging=quite_logging)
    _collected_lists:dict[str,dict[str,ToolBox_FileData]] = {}
    for _file in _FileList.values():
        if (compareFolders != None) and (len(compareFolders) >= 1):
            if any(_cp.upper() in _file.sourceFileDirRelPath.upper() for _cp in compareFolders):
                if _file.sourceFileDirRelPath not in _collected_lists.keys():
                    _collected_lists[_file.sourceFileDirRelPath] = {}
                _collected_lists[_file.sourceFileDirRelPath][_file.sourceFileName] = _file
    
    _used_resources:dict[str,dict[str,list[str]]] = {}

    if (compareFolders != None):
        # take action based off criteria used for comapareFolders list if found.
        # this area is custom and needs to be factored in a better way.                
        global _saved_file_count
        _saved_file_count = 0
        def file_action (_file:ToolBox_FileData, targetOutput:str, grp:str, calling_action:str):
            #global actions to apply to all files before saving
            _file.openFile()
            for _check_name in streamNameGroups["set_ONREQUEST_true"]:
                if _check_name.lower() in _file.sourceFileBaseName.lower():
                    log.debug(f"File '{os.path.join(_file.sourceFileDirRelPath, _file.sourceFileName)}' was found in list to  'set_ONREQUEST_true'.")
                    _file.set_Streams_ONREQUEST(True, remove_RUNCYCLE_lines=True)
                    _file.set_Streams_DRAFT(False)
                    _file.set_Jobs_NOP(False)                    
            os.makedirs(targetOutput, exist_ok=True)
            _outputFilePath = os.path.join (targetOutput, _file.sourceFileName)
            # save file to output location.
            _file.saveTo(targetOutput)
            global _saved_file_count
            _saved_file_count += 1
            log.info (f"Saving file from '{os.path.join(_file.sourceFileDirRelPath, _file.sourceFileName)}' to location '{_outputFilePath}', by {calling_action}")   
            
            _grp = grp.split('\\')[0]
            if _grp not in _used_resources.keys():
                _used_resources[_grp] = {
                    'NEEDS':[],
                    'RCG':[]
                }
            _needlist = _file.get_NEEDS_reference()
            for _need in _needlist:
                if _need not in _used_resources[_grp]['NEEDS']:
                    _used_resources[_grp]['NEEDS'].append(_need)
            _rcglist = _file.get_RCG_reference()
            for _rcg in _rcglist:
                if _rcg not in _used_resources[_grp]['RCG']:
                    _used_resources[_grp]['RCG'].append(_rcg)
            _file.closeFile()


        def process_paths (path_A:str, list_A:list[str], path_B:str):
            """handles each set of paths to comapir aginst each other"""
            list_B = [_fn for _fn in _collected_lists[path_B].keys()]
            _set_A = set(list_A)
            _set_B = set(list_B)
            _results = {
                "List_A_Path" : path_A,
                "List_B_Path" : path_B,
                "List_A_Only" : list(_set_A - _set_B),
                "List_B_Only" : list(_set_B - _set_A),
                "MATCHING" : list(_set_A.intersection(_set_B))
            }
            if (quite_logging != True) : log.debug (f"Comapring folders '{_prdPath}' with '{path_B}'", data=_results)
            _outputPath = os.path.join (outputputRootPath, path_B)
            os.makedirs(_outputPath, exist_ok=True)
            for _fileName in _results["List_A_Only"]:
                _fileData = _collected_lists[path_A][_fileName]
                _fileData.openFile()
                #_fileData.reset_default_collections()
                log.debug(f"File '{os.path.join(path_A,_fileName)}' not found in target Directory : '{path_B}'.")
                for _env in ['MODB', 'TESTB']:
                    if _env.upper() in path_A.upper():
                        _fileData.copy_Streams_By_Workstation ("@BAT1#", "@BAT2#")
                _fileData.set_Streams_ONREQUEST(True, remove_RUNCYCLE_lines=False)
                file_action(_fileData, _outputPath, path_B, "List_A_Only")                                
            
            for _fileName in _results["List_B_Only"]:
                _fileData = _collected_lists[path_B][_fileName]
                if any (_checkname.lower() in _fileData.sourceFileName.lower() for _checkname in streamNameGroups["set_ONREQUEST_true"]):
                    file_action(_fileData, _outputPath, path_B, "List_B_Only")
                #elif any(_env in path_B for _env in ['MODB', 'TESTB']):
                #    _fileData.openFile()
                #    _bat2_added = _fileData.copy_Streams_By_Workstation ("@BAT1#", "@BAT2#")
                #    if _bat2_added == True : 
                #        file_action(_fileData, _outputPath, path_B, "List_B_Only")

            for _fileName in _results["MATCHING"]:
                _fileData_A = _collected_lists[path_A][_fileName]
                _fileData_B = _collected_lists[path_B][_fileName]
                if compare_FileData_text_matching (_fileData_A, _fileData_B) == False:
                    _applied_a_change = merge_Streams_and_Jobs_A_to_B (_fileData_A, _fileData_B)
                    if _applied_a_change == True:
                        file_action(_fileData_B, _outputPath, path_B, "MATCHING")
                else:
                    if any (_checkname.lower() in _fileData_B.sourceFileName.lower() for _checkname in streamNameGroups["set_ONREQUEST_true"]):
                        file_action(_fileData_B, _outputPath, path_B, "MATCHING")
            

        _PROD_key_list:list[str] = [key for key in _collected_lists.keys() if 'PROD' in key]
        _UAT_key_list:list[str] = [key for key in _collected_lists.keys() if 'UAT' in key]
        _MOD_key_list:list[str] = [key for key in _collected_lists.keys()  if 'MOD' in key]
        _TEST_key_list:list[str] = [key for key in _collected_lists.keys()  if 'TEST' in key]

        merged_paths = list(set(_UAT_key_list + _MOD_key_list + _TEST_key_list))
        _common_prefix = os.path.commonprefix(_PROD_key_list)
        _total_dir_counter = 0
        _common_prefix = os.path.commonprefix(_PROD_key_list)
        
        for _prdPath in _PROD_key_list:
            _prdfileNames = [_fn for _fn in _collected_lists[_prdPath].keys()]
            _prd_subPath = _prdPath.removeprefix(_common_prefix)
            for _target_subPath in [_path for _path in merged_paths if _prd_subPath in _path]:
                process_paths (_prdPath, _prdfileNames, _target_subPath)
                _total_dir_counter += 1
                

        log.info (f"Creted a total of [{_saved_file_count}] files into [{_total_dir_counter}] sub directories")
    else:
        # do same actions to all files found in collection.
        pass
    
    log.info (f"Found Resources by ENV : ", data=_used_resources)

    log.critical (f"Completed Step 1")


#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{dt.now().strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")

    log.critical(f"", data = {
        "requirment 1" : 'All job stream/runbooks listed below in non-prod environments should have the frequency set to "ON REQUEST". ',
        "requirment 2" : 'For all non-prod environment jobs under the listed below listed job stream/runbooks\n    - Job stream Draft should be set to “FALSE”.\n    - Jobs Operation (NOP) should be set to “FALSE”.',
        "Job Stream List": [
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
            "/PRXIX/MIS/PROD/" : "/PRXIX/PRPRODLBATCH001"
        },
        "Non-PROD Workstations" : {
            "/PRXIX/MIS/TEST/" : "/PRXIX/PRTSTLBATCH001",
            "/PRXIX/MIS/TESTA/" : "/PRXIX/PRTSTLBATCH001",
            "/PRXIX/MIS/TESTB/" : "/PRXIX/PRTSTLBATCH001",
            "/PRXIX/MIS/TESTB/" : "/PRXIX/PRTSTLBATCH002",
            "/PRXIX/MIS/MOD/" : "/PRXIX/PRMODLBATCH001",
            "/PRXIX/MIS/MODA/" : "/PRXIX/PRMODLBATCH001",
            "/PRXIX/MIS/MODB/" : "/PRXIX/PRMODLBATCH001",
            "/PRXIX/MIS/MODB/" : "/PRXIX/PRTSTLBATCH002",
            "/PRXIX/MIS/UAT/" : "/PRXIX/PRUATLBATCH001",
            "/PRXIX/MIS/UATB/" : "/PRXIX/PRUATLBATCH001"
        },
        "Added Requirment 6" : "If a Job Stream or Job is found in PROD that does not exist in either MODB or TESTB and is set to use '@BAT1' as the workstation, Duplicate the '@BAT1' Jobs and Jobs Streams and point the duplciate to '@BAT2' within the same *.jil File."
    })

    step_1 (
        sourcePath = source_path,
        workingDirectory = working_directory,
        outputputRootPath = os.path.join (working_directory, 'step_1'),
        outputUsingRelPaths = True,
        compareFolders = [
            "PROD", 
            "MOD","MODA","MODB",
            "TEST", "TESTA", "TESTB", 
            "UAT", "UATA", "UATB"
        ],
        streamNameGroups = {
            "set_ONREQUEST_true" : [
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
        }
    )
    log.critical(f"Ending log for ticket : {ticketNumber} under contract : {contract} - Processing Complete.")