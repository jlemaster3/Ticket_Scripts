from ToolBox_V2.ToolBox_logger import OutputLogger
from ToolBox_V2.ToolBox_Filters import (
    ToolBox_Enum_AnyAll
)
from ToolBox_V2.ToolBox_Utilities import (
    ToolBox_Gather_Files,
    ToolBox_Gather_Directories
)
from ToolBox_V2.ToolBox_DataTypes.ToolBox_CSV_File import ToolBox_CSV_File
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_JIL_File import ToolBox_IWS_JIL_File
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_Stream_Obj import ToolBox_IWS_Stream_Obj
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_Job_Obj import ToolBox_IWS_Job_Obj

from ToolBox_V2.ToolBox_Actions import (
    Action_IWS_JIL_duplicate_streams,
    Action_IWS_JIL_sync_streams_A_B,
    Action_IWS_JIL_merge_Streams_A_B,
    Action_IWS_Stream_merge_Jobs_A_B,
    Action_IWS_Assets_merge_dependancies_A_B
)

"""
Sets up a global log object to use through the ticket wherever called.

Does require the importing ticket script to run the following line 
before adding to the log inorder to set the ouptut folder and log file name:

log.init_logger(log_folder="path/where/log/goes", log_file="name_of_log_file.log")

"""
log:OutputLogger = OutputLogger().get_instance()
