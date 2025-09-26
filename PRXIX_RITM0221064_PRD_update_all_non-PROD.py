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
from ToolBox import *
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

def step_1 (sourcePath:str, workingDirectory:str, outputputRootPath:str, outputUsingRelPaths:bool=True, compareFolders:list[str]=None, streamNameGroups:dict[str, list[str]] = None, quite_logging=True):
    """Collect files by sub-directory comapred to source path for comparisons."""
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
    
    if (compareFolders != None):
        # take action based off criteria used for comapareFolders list if found.
        # this area is custom and needs to be factored in a better way.
        _PROD_key_list:list[str] = [key for key in _collected_lists.keys() if 'PROD' in key]
        _UAT_key_list:list[str] = [key for key in _collected_lists.keys() if 'UAT' in key]
        _MOD_key_list:list[str] = [key for key in _collected_lists.keys()  if 'MOD' in key]
        _TEST_key_list:list[str] = [key for key in _collected_lists.keys()  if 'TEST' in key]
        _common_prefix = os.path.commonprefix(_PROD_key_list)
        
        
        def _file_action (_file:ToolBox_FileData, targetOutput:str):
            #global actions to apply to all files before saving
            if _file.sourceFileBaseName.lower() in streamNameGroups['set_onRequest_true']:
                _file.openFile()
                _file.set_Streams_onRequest()
            os.makedirs(targetOutput, exist_ok=True)
            _outputFilePath = os.path.join (targetOutput, _file.sourceFileName)
            _file.saveTo(targetOutput)
            if (quite_logging != True) : log.debug (f"Saving file from '{os.path.join(_file.sourceFileDirRelPath, _file.sourceFileName)}' to location '{_outputFilePath}'")   

        def _process_paths (path_A:str, list_A:list[str], path_B:str):
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

            _curr_path_file_created = 0
            _outputPath = os.path.join (outputputRootPath, path_B)
            os.makedirs(_outputPath, exist_ok=True)
            for _fileName in _results["List_A_Only"]:
                _fileData = _collected_lists[path_A][_fileName]
                _curr_path_file_created += 1 
                # if file is copied form PROD set add ONRESQUES if not already set.
                _fileData.openFile()
                _fileData.set_Streams_onRequest()
                _file_action(_fileData, _outputPath)
                                
            for _fileName in _results["List_B_Only"]:
                _fileData = _collected_lists[path_B][_fileName]
                _fileData.openFile()
                _curr_path_file_created += 1 
                #_file_action(_fileData, _outputPath)

            for _fileName in _results["MATCHING"]:
                _fileData = _collected_lists[path_B][_fileName]
                _curr_path_file_created += 1 
                #_file_action(_fileData, _outputPath)

            log.info (f"Creted a total of [{_curr_path_file_created}] in '{_outputPath}'")
            
            return _curr_path_file_created
            

        merged_paths = list(set(_UAT_key_list + _MOD_key_list + _TEST_key_list))
        
        _total_files_created = 0
        _total_dir_counter = 0
        for _prdPath in _PROD_key_list:
            _prdfileNames = [_fn for _fn in _collected_lists[_prdPath].keys()]
            _prd_subPath = _prdPath.removeprefix(_common_prefix)
            for _target_subPath in [_path for _path in merged_paths if _prd_subPath in _path]:
                _createdCount = _process_paths (_prdPath, _prdfileNames, _target_subPath)
                _total_dir_counter += 1
                _total_files_created += _createdCount

        log.info (f"Creted a total of [{_total_files_created}] files into [{_total_dir_counter}] sub directories")
    else:
        # do same actions to all files found in collection.
        print ('comapring paths')



#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"_{dt.now().strftime('%Y%m%d')}.log")
    log.info(f"Starting log for ticket : {ticketNumber} under contract : {contract}")

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
            "set_onRequest_true" : [
                "{E}D5MGD_834INB",
                "{E}D5MGD_834RSTRMV",
                "{E}D5MGD_834RSTR_A",
                "{E}D5MGD_834RSTR_B",
                "{E}D5MGD_834RSTR_C",
                "{E}D5MGD_ASGNRPT",
                "{E}D5MGD_RATECELL",
                "{E}MMGD_820_RLS",
                "{E}MMGD_834RPTS",
                "{E}MMGD_834RSTR",
                "{E}MMGD_CAP_820",
                "{E}MMGD_CAP_ADJCYC",
                "{E}MMGD_CAP_CYC_MN",
                "{E}MMGD_CAP_FCST",
                "{E}MMGD_CAP_OTP",
                "{E}MMGD_CAP_RPT",
                "{E}MMGD_CMS64",
                "{E}MMGD_RATECELL",
                "{E}MMGD_SUBCAP"
            ]
        }
    )

    print (f"done")