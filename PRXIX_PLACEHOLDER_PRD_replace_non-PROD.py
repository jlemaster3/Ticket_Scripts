#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket PLACEHOLDER

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

#-------------------------------------------------
#   Variables
#-------------------------------------------------
contract = 'PRXIX'
ticketNumber = 'PLACEHOLDER'

source_path = "C:\\VS_Managed_Accounts\\PRXIX\\PROD"
# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")

#-------------------------------------------------
#   Steps
#-------------------------------------------------

def step_1 (sourcePath:str, outputputPath:str):
    log.info (f"Gathering IWS *.jil and *.job files from source : '{sourcePath}'")
    _filelist = gather_files(sourcePath)
    log.info (f"Collected [{len(_filelist)}] file")
    _copyCount = 0
    for _file in _filelist:
        try:
            _output_path = _file.saveTo (outputputPath, useRelPath=True)
            log.info (f"Saved copy of file : '{_file.sourcePath_full}'  '{_output_path}'")
            _copyCount +=1
        except:
            log.warning (f"Failed to save copy of output file : '{_file._}'.")


def step_2 (sourcePath:str, target_streamNames:list[str]):
    log.info (f"Gathering IWS *.jil and *.job files from source : '{sourcePath}'")
    _filelist = gather_files(sourcePath,isolateByFileNames=target_streamNames)
    log.info (f"Collected [{len(_filelist)}] file")
    log.info (f"Setting Streams to ONREQUEST  [{len(target_streamNames)}]: ", data=target_streamNames)
    for _file in _filelist:
        _file.set_Streams_onRequest()
        if _file.raw_text != _file.modified_text:
            _output_path = _file.saveTo(sourcePath, useRelPath=True)
            log.info (f"Saved modified file : '{_file.sourcePath_full}'  '{_output_path}'")
    



#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file='PRXIX_PH_log.log')
    log.info(f"Starting log for ticket : {ticketNumber} under contract : {contract}")

    _sp1_output = os.path.join(working_directory, 'PROD_copy')

    step_1(
        sourcePath = source_path,
        outputputPath = _sp1_output
    )

    step_2(
        sourcePath = _sp1_output,
        target_streamNames = [
            "D5MGD_834INB" ,
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
            "MMGD_CAP_FCST"  ,
            "MMGD_CAP_OTP"  ,
            "MMGD_CAP_RPT" ,
            "MMGD_CMS64",
            "MMGD_RATECELL",
            "MMGD_SUBCAP"
        ]
    )