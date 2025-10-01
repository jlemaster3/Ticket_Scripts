from ToolBox.ToolBox_logger import OutputLogger
from ToolBox.ToolBox_Object import ToolBox_Decorator, ToolBox_IWS_JIL_File, ToolBox_IWS_JobStreamObj, ToolBox_IWS_JobObj
from ToolBox.ToolBox_Utilities import gather_files
from ToolBox.ToolBox_Utilities import sync_Files_A_to_B


"""
Sets up a global log object to use through the ticket wherever called.

Does require the importing ticket script to run the following line 
before adding to the log inorder to set the ouptut folder and log file name:

log.init_logger(log_folder="path/where/log/goes", log_file="name_of_log_file.log")

"""
log:OutputLogger = OutputLogger().get_instance()

