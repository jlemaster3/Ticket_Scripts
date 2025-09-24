#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM0214643

Created by: Jim Lemaster
Date: 09/19/2025

1. Copy all files from SETE directory to a temporary working folder for processing, except for files with:
 - SD5SYS_SMON.@
 - SD7SYS_AM.@
 - SD7SYS_NDY.@
 - SD7SYS_SMND.@
 - SMSYS_PATCH.@
 - SWSYS_SPCE.@

2. Get list of Job streams and Jobs on @MACH1#, then duplicate and copy all job streams found on @MACH1# and duplicate them to @MACH3# if the Job Stream is not already found assigned to @MACH3#:
 

3. Place the following streams on DRAFT on the @MACH3# agent:
 - /WIXIX/WIXODCLPAPP267#/WIXIX/MIS/SETE/SWSYS_REFRESH.@
 - /WIXIX/WIXODCLPAPP267#/WIXIX/MIS/SETE/SWSYS_REFRESH_PS.@
 - /WIXIX/ WIXODCLPAPP267#/WIXIX/DBA/SETE/SWDBA_CHG_PSWDS.@

'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

from IWS_FileManager import IWS_ToolBox
from datetime import datetime as dt

import os

#-------------------------------------------------
#   functions
#-------------------------------------------------

def main ():
    # Capture current date and time when script begins
    _startTime = dt.now()

    """ Main script execution block. """
    # Define Source and Working Directories
    source_directory = "C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\WIXIX\SETE"
    # Define Working and Output Directories
    working_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0214643"
    
    log_file_name = f'WIXIX_RITM0214643_SETE_Duplication.log'
    #Define Output Directory
    step_1_output_dir = os.path.join(working_directory, "SETE_copy")
    step_2_output_dir = os.path.join(working_directory, "SETE_final")
    
    # Create new instance of the IWS_ToolBox class
    toolbox = IWS_ToolBox(
        workingDirectoryPath=working_directory, 
        logFileName=log_file_name
        )
    toolbox.logger.info(f"Process started at : {_startTime}")
    
    # Step 1 - Copy source files
    _step_1 = toolbox.add_step('Step 1 - Copy SETE to temp directory')
    _step_1.add_sourcePath(source_directory).gather_files(
        excludedFileNames=[
            "D5SYS_SMON", 
            "D7SYS_AM", 
            "D7SYS_NDY", 
            "D7SYS_SMND", 
            "MSYS_PATCH", 
            "WSYS_SPCE"
        ]).copyFilesTo(step_1_output_dir)
    
    # Step 2 - duplcaite @MACH1# Streams 
    _step_2 = toolbox.add_step('Step 2 - Duplciate @Mach1# items to @MACH3# if not already on @MACH3#')
    _step_2.add_sourcePath(step_1_output_dir).gather_files()

    
    print (_step_2.fileCount, len(_step_2.fileList_FullPath))
    for _count, _filePath in enumerate(_step_2.fileList_FullPath):
        _fileData = toolbox.readFile(_filePath)        
        print(_count, _filePath, _fileData)
    _stopTime = dt.now()
    toolbox.logger.info(f"Process completed at :  at {_stopTime} elapsed time {format(_stopTime-_startTime)}")


#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    main()