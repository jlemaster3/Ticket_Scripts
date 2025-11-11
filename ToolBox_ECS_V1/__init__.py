from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.ToolBox_Main import ToolBox
from ToolBox_ECS_V1.Nodes import (
    ToolBox_ECS_Node,
    ToolBox_Base_File_Node,
    ToolBox_CSV_File_Node,
    ToolBox_XLSX_File_Node,
    ToolBox_IWS_XLSX_Runbook_File_Node,
    ToolBox_IWS_JIL_File_Node,
    ToolBox_Base_Node,
    ToolBox_IWS_OBJ_Nodes,
)
"""
Sets up a global log object to use through the ticket wherever called.

Does require the importing ticket script to run the following line 
before adding to the log inorder to set the ouptut folder and log file name:

log.init_logger(log_folder="path/where/log/goes", log_file="name_of_log_file.log")

"""

log:OutputLogger = OutputLogger().get_instance()

__all__ = [
    'log', 
    'ToolBox',
    'ToolBox_ECS_Node',
    'ToolBox_Base_File_Node',
    'ToolBox_CSV_File_Node',
    'ToolBox_XLSX_File_Node',
    'ToolBox_IWS_XLSX_Runbook_File_Node',
    'ToolBox_Base_Node',
    'ToolBox_IWS_JIL_File_Node',
    'ToolBox_IWS_OBJ_Nodes'
    ]