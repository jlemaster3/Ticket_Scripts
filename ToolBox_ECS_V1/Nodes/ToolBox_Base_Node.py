#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import random, uuid, re
from typing import Any, Optional
from collections import UserDict
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import ToolBox_Entity_Types

#-------------------------------------------------
#   Decorator Functions / Wrappers
#-------------------------------------------------

def ToolBox_Decorator(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        return result
    return wrapper

#-------------------------------------------------
#   Base Classes
#-------------------------------------------------    

class ToolBox_ECS_Node (UserDict):
    """This class extends the UserDict class, and can be assigned (key,value) pairs when created,
    or have user defined keys and values after creation. 
    
    Example:
        node['key'] = value

    This Node type (None) is a generic and the root of all other node classes.
    Trcks an ID, Name, and simple "Parent - Child" relashonships and functionality.


    """
    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()
    
    #------- private properties -------#
    
    _key:str = None
    _name:str = None
    _node_type:ToolBox_Entity_Types = None
    _parent_entity:ToolBox_ECS_Node = None
    _children_entities:list[ToolBox_ECS_Node] = None

    #------- Initialize class -------#

    def __init__(
            self,
            name:str,
            node_type:ToolBox_Entity_Types,
            id_key:str|None=None,
            parent_entitity:Optional[ToolBox_ECS_Node]=None, 
            initial_data:dict[str,Any]=None
            
        ):
        """Required Attributes:
            name:(str) - Node's Name
            node_type:ToolBox_Entity_Types - 
        """
        super().__init__(initial_data)
        self._name = name
        self._key = id_key if id_key is not None else str(uuid.uuid5(uuid.NAMESPACE_DNS, str(random.randrange(1000000000))))
        self._node_type = node_type or ToolBox_Entity_Types.NONE
        self._parent_entity = parent_entitity
        self._children_entities = []

    def __setitem__(self, key, value):
        if isinstance(value, str):
            self.data[key] = value
        else:
            self.data[key] = value

    def __getitem__(self, key):
        if isinstance(key, str):
            key = key
        return self.data[key]
    
    def __repr__(self):
        return f"{type(self)} (name = {self._name}, node_type = {self._node_type})"
    
    def __contains__(self, item):
        return item in self._children_entities

    #-------public Getter & Setter methods -------#

    @property
    def id_key (self) -> str:
        """Returns this Nodes' ID / Key assignment."""
        return self._key

    @property
    def name (self) -> str:
        """Returns this Nodes' name."""
        return self._name
        
    @name.setter
    def name (self, value:str) :
        """Sets the name of the Node."""
        self._name = value

    @property
    def children (self) -> list[ToolBox_ECS_Node]:
        """Returns the current list of Children Nodes."""
        return self._children_entities
    

    @property
    def siblings(self) -> list[ToolBox_ECS_Node]:

        """Return a list of sibling entities (excluding self)."""
        if not self._parent_entity:
            return []
        return [sib for sib in self._parent_entity.children if sib is not self]
    
    @property
    def parent(self) -> list[ToolBox_ECS_Node]:
        """Return a list of sibling entities (excluding self)."""
        if not self._parent_entity:
            return None
        return self._parent_entity
    
    @parent.setter
    def parent (self, value:ToolBox_ECS_Node):
        self._parent_entity = value
    
    @property
    def node_type (self) -> str:
        return self._node_type
    
    #------- Methods / Functions -------#

    @ToolBox_Decorator
    def add_child(self, child: ToolBox_ECS_Node):
        """Attach a child entity while maintaining order."""
        if child in self._children_entities:
            return  # avoid duplicates
        self._children_entities.append(child)
        child._parent_entity = self

    @ToolBox_Decorator
    def remove_child(self, child: ToolBox_ECS_Node):
        """Removed child link if found"""
        if child in self._children_entities:
            self._children_entities.remove(child)
            child._parent_entity = None
