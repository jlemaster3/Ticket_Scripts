#-------------------------------------------------
#   About
#-------------------------------------------------

'''
Ticket RITM0216982

Duplicate all Steams and Jobs on the following workstation in UAT

USOLSLWI228 -> WIXODCLPAPP280
USOLSLWI230 -> WIXODCLPAPP281
USOLSLWI231 -> WIXODCLPAPP282

MACH3 -> MACH12
MACH4 -> MACH13
MACH5 -> MACH14

'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, copy
from ToolBox import *
from datetime import datetime as dt
#-------------------------------------------------
#   Variables
#-------------------------------------------------

contract = 'WIXIX'
ticketNumber = 'RITM0216982'

source_path = "C:\\VS_Managed_Accounts\\WIXIX\\UAT"
# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")

#-------------------------------------------------
#   Steps
#-------------------------------------------------

def step_1 (sourcePath:str, workingDirectory:str, outputputRootPath:str, outputUsingRelPaths:bool=True, search_replace_terms:dict[str,str]=None, quite_logging=True):
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
    
    _used_resources = {
    'NEEDS':[],
    'RCG':[]
    }
    _updated_count = 0
    for _file in _FileList.values():
        _outputPath = os.path.join (outputputRootPath, _file.sourceFileDirRelPath)
        os.makedirs(_outputPath, exist_ok=True)
        _file.openFile()
        _found_change = _file.search_replace_terms (search_replace_terms)
        if _found_change == True:
            _duplicate_test = copy.deepcopy(_file.text_modified)
            _file.reset_mod_lines()
            _file.add_streamText_to_File(_duplicate_test)    
            _file.saveTo(_outputPath, useRelPath=True)
            log.info (f"Saving file from '{os.path.join(_file.sourceFileDirRelPath, _file.sourceFileName)}' to location '{os.path.join(_outputPath, _file.sourceFileName)}'")
            _updated_count += 1
        _needlist = _file.get_NEEDS_reference()
        for _need in _needlist:
            if _need not in _used_resources['NEEDS']:
                _used_resources['NEEDS'].append(_need)
        _rcglist = _file.get_RCG_reference()
        for _rcg in _rcglist:
            if _rcg not in _used_resources['RCG']:
                _used_resources['RCG'].append(_rcg)
        _file.closeFile()
    log.info (f"Creted a total of [{_updated_count}] files.")
    log.info (f"Found Resources by ENV : ", data=_used_resources)    
    log.critical (f"Completed Step 1")
#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{dt.now().strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")

    step_1 (
        sourcePath = source_path,
        workingDirectory = working_directory,
        outputputRootPath = os.path.join (working_directory, 'UAT'),
        outputUsingRelPaths = True,
        search_replace_terms = {
            "@MACH3#" : "@MACH12#",
            "@MACH4#" : "@MACH13#",
            "@MACH5#" : "@MACH14#"
        }
    )