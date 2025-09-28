#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM0210301

Created by: Jim Lemaster
Date: 06/26/2024

Purpose: This script is designed to copy files from PROD into PPS.
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

from IWS_FileManager import IWS_ToolBox, ToolBoxAction, ToolBoxCheck, IWSLineType, ActionType
from datetime import datetime as dt

import os

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    # Capture current date and time when script begins
    _startTime = dt.now()

    """ Main script execution block. """
    # Define Source and Working Directories
    source_directory = "C:\\VS_Managed_Accounts\\KSXIX\\PROD"
    # Define Working and Output Directories
    working_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\RITM0210301"
    #Define Output Directory
    output_directory = os.path.join(working_directory, "step_1_output")
    
    
    
    # Create new instance of the IWS_ToolBox class
    toolbox = IWS_ToolBox(
        workingDirectoryPath=working_directory, 
        logFileName="KSXIX_RITM0210301_PRD-PPS_step_1_log.txt"
        )
    

    
    _action_1 = ToolBoxAction(
        name="MACH1 to Mach8 excluding files with Mach2 refs",
        checkList=[
            ToolBoxCheck(IWSLineType.ANY,value="@MACH1#"),
            ToolBoxCheck(IWSLineType.ANY,value="@MACH2#",include=False)
        ],
        responce= lambda x, y: print (x, y)
    )
        
        
        #lambda sourceContainer, line, lineindex : sourceContainer.searchRepalce(term_map = {
        #    "@MACH1#" :"@MACH8#",
        #    "/export/customer/kscmn/prod/job/autojob.sh":"/dsks/{APP_CMN}/{ENV_DIR}/autojob.sh",
        #    "export/ftp/kscmn/prod":"/dsks/ftp/{APP_CMN}/{ENV_DIR}",
        #    "export/home/kscmn":"/dsks/home/{APP_CMN}/{ENV_DIR}"
        #    "PROD":"{ENV}"
        #    "PRD":"{ENV}"
        #    "PPS":"{ENV}"
        #    }
        #)
    
    
    toolbox.add_sourcePath(source_directory)
    colelctedFileList = toolbox.collectSourceFiles()
    toolbox.loadCollectedFiles(colelctedFileList)
    toolbox.add_action(_action_1)
    toolbox.Process_Files_aginst_Actions()

    #colelctedFileList = toolbox.collectSourceFiles()
    #toolbox.searchReplaceTerms = {
    #    "@MACH1#" :"@MACH8#",
    #    "/export/customer/kscmn/prod/job/autojob.sh":"/dsks/{APP_CMN}/{ENV_DIR}/autojob.sh",
    #    "export/ftp/kscmn/prod":"/dsks/ftp/{APP_CMN}/{ENV_DIR}",
    #    "export/home/kscmn":"/dsks/home/{APP_CMN}/{ENV_DIR}"
    #}
    #toolbox.copy_collection_to_directory(targetDir=output_directory, fileList=colelctedFileList)

    _stopTime = dt.now()
    toolbox.logger.info(f"Process completed at :  at {_stopTime} elapsed time {format(_stopTime-_startTime)}")