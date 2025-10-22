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

contract = 'KYXYX'
ticketNumber = 'RITM0227508'

source_path = "C:\\Users\\jlemaster3\\source\\Workspaces\\Managed-Accounts\\KYXIX\\TEST2"
# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")

#-------------------------------------------------
#   Steps
#-------------------------------------------------


def step_1 (sourcePath:str, outputPath:str, namedLists:dict[str, list[str]] = None) :
    _paths = ToolBox_Gather_Directories(
        source_dir = sourcePath
    )

    _filelist = ToolBox_Gather_Files( 
        source_dir = sourcePath, 
        isolate_directory_names = namedLists['Target_Env_list'],
        isolate_fileName_names = namedLists['Stream_list']
    )
    log.blank("-"*100)
    log.info(f"Search Terms -> Replace Terms : [{len(namedLists['Search_Replace_Terms'].keys())}]", data = namedLists['Search_Replace_Terms'])
    log.info(f"limiting Job Stream edits to workstations : [{len(namedLists['Workstation_list'])}]", data=namedLists['Workstation_list'], list_data_as_table=True, column_count=1)
    _files_updated = 0
    for _file in _filelist:
        _file.open_file()
        _change_made = False
        #log.blank('-'*100)
        #log.label(f"Checking File '{_file.relFilePath}'")
        for _stream in _file.job_stream_objects:
            if any (_ws.upper() in _stream.full_path.upper() for _ws in namedLists["Workstation_list"]):
                _stream_text = _stream.get_current_text()
                for _searchTerm, _replaceTerm in namedLists['Search_Replace_Terms'].items():
                    if _searchTerm in _stream_text:
                        log.blank('-'*100)
                        log.label(f"Checking File '{_file.relFilePath}'")
                        _stream.search_replace_text(searchString=_searchTerm,replaceString=_replaceTerm)
                        _change_made = True
        for _job in _file.job_objects:
            if any (_ws.upper() in _job.full_path.upper() for _ws in namedLists["Workstation_list"]):
                _job_text = _job.get_current_text()
                for _searchTerm, _replaceTerm in namedLists['Search_Replace_Terms'].items():
                    if _searchTerm in _job_text:
                        if _change_made == False:
                            log.blank('-'*100)
                            log.label(f"Checking File '{_file.relFilePath}'")
                        _job.search_replace_text(searchString=_searchTerm,replaceString=_replaceTerm)
                        _change_made = True
        #if _change_made == True:
        _file.save_File(outputPath, useRelPath=True)
        _files_updated += 1
        #else:
            #log.info(f"No changes to make, closing File '{_file.relFilePath}'")
    log.blank('-'*100)
    log.info(f"Updated a total of [{_files_updated}] out of [{len(_filelist)}] files found in filters.")

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":
    _start_time = dt.now()
    # Capture current date and time when script begins
    log.init_logger(log_folder=working_directory, log_file=f"{contract}_{ticketNumber}_{_start_time.strftime('%Y%m%d')}.log")
    log.critical(f"Starting log for ticket : {ticketNumber} under contract : {contract}")
    log.critical(f"", data = {
        "requirment 1" : "Changes will be made to the workstation USOLLUKKFS001 Folder: TEST2.",
        "requirment 2" : "The changes are to change the prefix of the file names below from what they are now in IWS now to what they need to be changed in IWS now.",
        "Prefix 1" : "From: /export/ftp/prod/ to: /dsky/test/ftp/",
        "Prefix 2" : "From: /tmpsort2/prod/ to: /tmpsort2/test/",
        "Prefix 3" : "From: /cust/prod/dsky/ to: /dsky/prod/"
    })

    step_1(
        sourcePath = source_path,
        outputPath = os.path.join(working_directory,"TEST2"),
        namedLists = {
            "Target_Env_list" : ["TEST2"],
            "Workstation_list" : ["@MACH7#", "@MACH6#"],
            "Search_Replace_Terms" : {
                "/export/ftp/prod/": "/dsky/{ENV}/ftp/",
                "/tmpsort2/prod/" : "/tmpsort2/{ENV}/",
                "/cust/prod/dsky/" : "/dsky/{ENV}/",
                 "/dsky/{ENV}/ftp/" : "/dsky/{ENV_FLDR}/ftp/",
                "/tmpsort2/{ENV}/" : "/tmpsort2/{ENV_FLDR}/",
                 "/dsky/{ENV}/" : "/dsky/{ENV_FLDR}/"
            },
            "Stream_list" : [
                "DBR_PFM_ETL_LD",
                "DWSMDMVS",
                "DWSWFT_PAIPDL",
                "DWSWMXPA",
                "BUYD_MMA",
                "BUYD_MMA",
                "BUYMBUYIN",
                "BUYWFTPARTDFILE",
                "BUYWFT_TBQ_FILE",
                "BUY_DAILY_TBQ",
                "BUY_DAILY_TBQ",
                "BUY_DBUYIN",
                "CLD630",
                "CLDNDY",
                "CLMMMMANDONTFY",
                "CYCMMCO834EML",
                "DRGMFT_CONTFL",
                "DRGMFT_OUTFL",
                "DRGMSHPAPLCONFL",
                "DRGMSHPAPLOUTFL",
                "DRGMSHPCON_FL",
                "DRGMSHPOUTFL",
                "ELGBFTCOBA70058",
                "ELGBFTCOBA70074",
                "ELGBFTCOBA70075",
                "ELGBFTCOBA70083",
                "ELGBFTCOBA70084",
                "ELGBFTCOBA70086",
                "ELGBFTCOBA77184",
                "ELGBFTCOBA77185",
                "ELGDMMANDONTFY",
                "ELGKHBERTRRECON",
                "ELGKHBERTRRECON",
                "ELGMDEMO_INFO",
                "ELGMFTRCNKHBE",
                "ELGMFTRCNPAT",
                "ELGMFTRCRTRKHBE",
                "ELGMRCN1FLMON",
                "ELG_AUTH_REP",
                "ELG_DLYMAIDCRD",
                "ELG_IEES_TERM",
                "ELG_MFP_UK",
                "ELG_MNTHRCNPAT",
                "ELG_MONTHLY_EVV",
                "ELG_MTH_KHBE",
                "ELG_MTH_KHBE",
                "ELG_VITAL_STAT",
                "FIN_HISTORY",
                "FIN_QNONBAL",
                "MGDMFTPASSMBRFL",
                "MGDMFT_AETMBRFL",
                "MGDMFT_ANTMBRFL",
                "MGDMFT_HUMMBRFL",
                "MGDMFT_MOLMBRFL",
                "MGDMFT_UHCMBRFL",
                "MGDMFT_WELMBRFL",
                "MGDMMCOCNTFY",
                "MGDMMCO_CAPEXTR",
                "MGDMMCO_MBR_AET",
                "MGDMMCO_MBR_ANT",
                "MGDMMCO_MBR_HUM",
                "MGDMMCO_MBR_MOL",
                "MGDMMCO_MBR_P31",
                "MGDMMCO_MBR_UHC",
                "MGDMMCO_MBR_WEL",
                "MGDMNEMTCNTFY",
                "MGDMPACECNTFY",
                "MGD_DLY_MCO_MBR",
                "PROV_DAILY_IN",
                "REFWFTFDBFDBFL",
                "REFWFTFDBUDBFL",
                "RFMMAC",
                "RFWFDB",
                "RFWMAC",
                "TPDWTCH",
                "TPD_DLY_AET_DTM",
                "TPD_DLY_ANT_DTM",
                "TPD_DLY_HUM_DTM",
                "TPD_DLY_MOL_DTM",
                "TPD_DLY_UHC_DTM",
                "TPD_DLY_WEL_DTM",
                "TPMKCSR",
                "TPWWTCH"
            ]
        }
    )
    log.critical(f"End of log for ticket : {ticketNumber} under contract : {contract}")
    log .info (f"Script processing time : {dt.now() - _start_time}")
    print ("complete")