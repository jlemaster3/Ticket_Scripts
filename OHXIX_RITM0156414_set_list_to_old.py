#-------------------------------------------------
#   About - See Updates and Notes at bottom of script for more information.
#-------------------------------------------------

'''
Ticket RITM00150789
'''

#-------------------------------------------------
#   Imports
#-------------------------------------------------

import os, shutil

#-------------------------------------------------
#   Variables
#-------------------------------------------------

# location of local repository directory:
source_directory = "C:\\VS_Managed_Accounts\\OHXIX\\PROD"

# where the output files shold go, dont use source location
output_directory = "C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\Documents\\_Ticket_Repo\\RITM0156414\\output"

output_log_file = os.path.join(output_directory, 'env_change_log.txt')

files_to_find = ["PD5_MGD_INF", "PD5_MGD_INFXFR", "PD5_MGD_MMA_INF", "PD5_TPL_PBM_INF", "PD_TPL_INFINEXEC", "PD_TPL_INFOUT", "PM_MGD_INFT_FST", "PRQ_TPL_INF", "PW_MGD_INFT", "PW_RCP_OIS_FILES", "PW_TPL_INF_OUT2", "PW_TPL_MCO_INTF", "PAN_TPL", "PBUY_BUY_DRPTS", "PBUY_BUY_WRPTS", "PBUY_DCOBA", "PBUY_DIN", "PBUY_DIN_SND", "PBUY_DLINK", "PBUY_DRPTS", "PBUY_DTBQ", "PBUY_MBUY_RPTS", "PBUY_MMARECVRPTS", "PBUY_MMASNDRPTSD", "PBUY_MMASNDRPTSM", "PBUY_MMA_FILE_D", "PBUY_MMA_FILE_M", "PBUY_MMA_PROC", "PBUY_WIN", "PBUY_WRPT", "PBUY_WTBQ", "PD5_MGD_CARA_SI", "PD5_MGD_CMSTXNCO", "PD5_MGD_CMS_TXN", "PD5_MGD_DTRR", "PD5_MGD_MAIN", "PD5_MGD_MMA_LD", "PD5_MGD_OELTRRCP", "PD5_MGD_OE_LTR", "PD5_MGD_RPTS", "PD5_TPL_PBM", "PD7_BUY_SETDATE", "PD7_MGD_AM", "PD7_MGD_CONDRQST", "PD7_MGD_INFT", "PD7_MGD_MAILALRT", "PD7_MGD_PM", "PD7_RCP_AHS_OB", "PD7_RCP_AHS_RPTS", "PD7_RCP_D099O", "PD7_RCP_FI_HSP", "PD7_RCP_FI_HSP_S", "PD7_RCP_FI_RPTS", "PD7_RCP_HINS", "PD7_RCP_HOSPICE", "PD7_RCP_HSPRPTS", "PD7_RCP_HSPSHDN", "PD7_RCP_HSPSPNM", "PD7_RCP_LINK", "PD7_RCP_MCIMAINT", "PD7_RCP_MCI_OB", "PD7_RCP_MDN", "PD7_RCP_MSP", "PD7_RCP_PARMSCWS", "PD7_RCP_PRSTV", "PD7_RCP_RDMUPDTS", "PD7_RCP_RECPRLTM", "PD7_RCP_RPTS", "PD7_RCP_SCWS", "PD7_RCP_SIELGSHD", "PD7_RCP_SIRSPERR", "PD7_RCP_SI_ELG", "PD7_RCP_UNLINK", "PD_TPL_EXEC", "PD_TPL_SETS", "PMGDD051_PAR", "PMGDD100_PAR", "PMGDD101_PAR", "PMGDD415_PAR", "PMGDM051_PAR", "PM_BUY_COBASND", "PM_MGD_EOMDISNRL", "PM_MGD_HICN", "PM_MGD_ICDSWVR", "PM_MGD_ICDSWVRD", "PM_MGD_MISC", "PM_MGD_RPTS", "PM_MGD_RPTS_FST", "PM_TPL1", "PM_TPL_JOB2", "PONREQ_BUY", "PONREQ_MGDMCOLTR", "PONREQ_MGDMCOSTP", "PONREQ_TPL_DEERS", "PONRQST_MGD_SPEC", "PONRQ_MGD", "PONRQ_MGD_TRNSF", "PQT_TPL", "PREQ_MGD_CARA_SI", "PRQ_TPL_RDM", "PRQ_TPL_TERMED", "PW_MGD_RPTS", "PW_RCP", "PW_RCP_AHS_OB", "PW_RCP_AHS_REST", "PW_RCP_OBFUPDTS", "PW_RCP_RPTS", "PW_RCP_SUNDAY", "PW_TPL_HMS", "PW_TPL_MCO", "PW_TPL_MCO_RPTS", "PM_TPL_MCO_INTF", "PSCHED_DISNRL", "PSCHED_OHRDISNRL", "PELG_OIS_FILES", "PELGD_RPT_ST", "PD7_SCWS_WCHR"]

exclude_text = ["@MACH2#", "@MACH3#", "@MACH7#"]

_output_log_holder = []

#-------------------------------------------------
#   Functions
#-------------------------------------------------

# collects all files in source folder path that end with items found in file_types list
def get_jil_files_from_list (source_path:str, nameList:list[str], file_types:list=['.jil', '.job'])->list[str]|None:
    path = os.path.abspath(source_path)
    if not os.path.exists(path):
        print (f"Path not found : {source_path}")
        return None
    file_list = []
    for root, _, files in os.walk(path):
        for file in files:
            if any(file.lower().endswith(ft) for ft in file_types) and any(_str.lower() in file.lower() for _str in nameList):
                file_list.append(os.path.join(root, file))
    return file_list


# output files will be saved in the provided output_path with the same file name as the source
# output file will contain both the orriginal contents and the duplicated/edited contents in the same file.
def set_to_old (path_list:list, output_path:str, overwrite_original_file:bool=False):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for counter, filePath in enumerate(path_list):
        try:    
            _rel_path = os.path.relpath(filePath, source_directory)
            output_filePath = f"{filePath}.old"            
            os.rename(filePath, output_filePath)
            _output_log_holder.append(f" [{counter+1}] - renaming File : '{os.path.basename(_rel_path)}' to '{os.path.basename(_rel_path)}.old'")
            print (filePath)
            print (output_filePath)
        except Exception as e:
            _output_log_holder.append(f" [{counter+1}] - Error processing file : {os.path.basename(filePath)} - {e}")
        
#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    # get all jil files in path and all subdirectories
    jil_files_dictionary = get_jil_files_from_list(source_directory, files_to_find)



    _output_log_holder = []
    _output_log_holder.append(f"Soruce directory : '{source_directory}'")
    _output_log_holder.append(f"Soruce output directory : '{output_directory}'")
    _output_log_holder.append(f"Files being removed (set to '*.old')")
    _output_log_holder.append('-'*100)
    
    # create new files that contains a copy of the edited contents
    set_to_old(
        path_list=jil_files_dictionary, 
        output_path=output_directory, 
        overwrite_original_file=False
    )

    with open (output_log_file, 'w') as _log_file:
        _log_file.write("\n".join(_output_log_holder))
    
    print (f"Done processing")