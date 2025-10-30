#-------------------------------------------------
#   Imports
#-------------------------------------------------
import re, uuid, copy
from enum import StrEnum
from typing import Literal, Any
from collections import UserDict
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import (
    ToolBox_Amount_Options,
    ToolBox_Entity_Types,
    ToolBox_REGEX_Patterns
)

#-------------------------------------------------
#   Variables
#-------------------------------------------------

log:OutputLogger = OutputLogger().get_instance()

#-------------------------------------------------
#   Functions
#-------------------------------------------------


