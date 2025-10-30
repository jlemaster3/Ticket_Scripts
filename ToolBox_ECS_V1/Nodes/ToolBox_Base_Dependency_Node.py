#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import os, copy, uuid, re
from datetime import datetime
from typing import Any, Optional, TYPE_CHECKING, Literal
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Nodes.ToolBox_Base_Node import ToolBox_ECS_Node
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import ToolBox_Entity_Types

if TYPE_CHECKING:
    from ToolBox_ECS_V1.Nodes.ToolBox_Base_Node import ToolBox_ECS_Node
    from ToolBox_ECS_V1.ToolBox_Manager import ToolBox

#-------------------------------------------------
#   Decorator Functions / Wrappers
#-------------------------------------------------

def ToolBox_Decorator(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        return result
    return wrapper

#-------------------------------------------------
#   Defined Node Classes
#-------------------------------------------------

class ToolBox_ECS_Dependency_Node (ToolBox_ECS_Node):
    """Extends from ToolBox_ECS_Node
    
    This Node tpye is ment to handle unique relationships between otehr nodes that extends outside the
    basic "Parent-Child" hierarchy and relationships that most node trees would impliment.
    """
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    
    #------- private properties -------#

    _dependancy_owner:ToolBox_ECS_Node
    _dependancy_type:ToolBox_Entity_Types
    _source_key:str
    _source_node:ToolBox_ECS_Node|None
    _target_key:str
    _target_node:ToolBox_ECS_Node|None

    #------- Initialize class -------#

    def __init__(
            self,
            source_key:str,
            target_key:str,
            dependancy_type:Literal[ToolBox_Entity_Types.NONE],
            node_type:Literal[ToolBox_Entity_Types.DEPENDENCY],
            owning_node:ToolBox_ECS_Node,
            name:str,
            id_key:str,
            parent_entitity:Optional[ToolBox_ECS_Node], 
            initial_data:dict[str,Any]
        ):
        self._dependancy_owner = owning_node
        self._dependancy_type = dependancy_type
        super().__init__(
            id_key = id_key,
            name = name,
            node_type = node_type, 
            parent_entitity = parent_entitity,
            initial_data = initial_data
        )
        self._source_key = source_key
        self._target_key = target_key
        self._source_node = ToolBox[source_key] if source_key in ToolBox else None
        self._target_node = ToolBox[target_key] if target_key in ToolBox else None

        #-------public Getter & Setter methods -------#

    @property
    def source_key (self) -> str:
        """Returns assigned Source Key ."""
        return self._source_key
        
    @source_key.setter
    def source_key (self, value:str) :
        """Sets the assigned Source Key."""
        self._source_key = value

    @property
    def source_node (self) -> ToolBox_ECS_Node|None:
        """Returns Source Node."""
        return self._source_node
    
    @property
    def target_key (self) -> str:
        """Returns assigned Target Key ."""
        return self._target_key
        
    @target_key.setter
    def target_key (self, value:str) :
        """Sets the assigned Target Key."""
        self._target_key = value

    @property
    def target_node (self) -> ToolBox_ECS_Node|None:
        """Returns Target Node."""
        return self._target_node