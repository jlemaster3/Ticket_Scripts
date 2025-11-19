from ToolBox_ECS_V2.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V2.ToolBox_Main import ToolBox

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
]