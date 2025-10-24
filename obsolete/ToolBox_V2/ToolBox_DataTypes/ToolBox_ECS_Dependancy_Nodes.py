#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import random, uuid, re
from typing import Any, Optional
from ToolBox_V2.ToolBox_logger import OutputLogger
from ToolBox_V2.ToolBox_DataTypes.ToolBox_IWS_JIL_File import ToolBox_IWS_JIL_File
from ToolBox_V2.ToolBox_DataTypes.ToolBox_ECS_Data_Nodes import (
    ToolBox_ECS_Node,
    ToolBox_Entity_types,
    ToolBox_REGEX_Patterns
)

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

class ToolBox_ECS_Dependency (ToolBox_ECS_Node):
    """Extends from ToolBox_ECS_Node
    
    This Node tpye is ment to handle unique relationships between otehr nodes that extends outside the
    basic "Parent-Child" hierarchy and relationships that most node trees would impliment.
    """
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    
    #------- private properties -------#

    _source_key:str
    _target_key:str

    #------- Initialize class -------#

    def __init__(
        self,
        id_key:str = None,
        name:str = None,
        parent_entitity:Optional[ToolBox_ECS_Node]=None, 
        initial_data:dict[str,Any]=None
    ) :
        _random_key = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(random.randrange(1000000000))))
        super().__init__(
            id_key = id_key if id_key is not None else _random_key,
            name = name if name is not None else f"dependency_{_random_key}",
            node_type = ToolBox_Entity_types.DEPENDENCY,
            parent_entitity = parent_entitity,
            initial_data = initial_data
        )
    
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
    def target_key (self) -> str:
        """Returns assigned Target Key ."""
        return self._target_key
        
    @target_key.setter
    def target_key (self, value:str) :
        """Sets the assigned Target Key."""
        self._target_key = value


#-------------------------------------------------
#   Defined Node Classes
#-------------------------------------------------

# IWS Connection node, handles and stores all information about a links between IWS nodes.
# This node type is meant to track and manage all non-"Parent to Child" or non-"Job Stream to Job".
# Extends from ToolBox_ECS_Dependency.

class ToolBox_ECS_Node_IWS_Dependancy (ToolBox_ECS_Dependency):
    """Extends from ToolBox_ECS_Dependency.
    
    IWS Connection node, handles and stores information about a links between IWS nodes,
    not meant to be used for "Parent to Child" or non-"Job Stream to Job" hierarchy.
    """
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    
    #------- private properties -------#
    _iws_object_type:ToolBox_Entity_types = None
    _source_file_path:str = None
    _source_file_obj:ToolBox_IWS_JIL_File = None
    _source_file_text:str = None
    _modified_file_text:str = None

     #------- Initialize class -------#

    def __init__(
        self,
        id_key:str,
        object_type:ToolBox_Entity_types.IWS_FOLLOW | ToolBox_Entity_types.IWS_JOIN | ToolBox_Entity_types.IWS_RESOURCE,
        name:str = None,
        parent_entitity:Optional[ToolBox_ECS_Node]=None, 
        initial_data:dict[str,Any]=None
    ) :
        super().__init__(
            id_key = id_key,
            name = name if name is not None else None,
            node_type = object_type,
            parent_entitity = parent_entitity, 
            initial_data = initial_data
        )
        self._iws_object_type = object_type


