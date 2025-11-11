#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import random, uuid, re
from typing import Any, Optional, TYPE_CHECKING
from collections import UserDict
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Data_Silo import ToolBox_Data_Silo_Manager
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import ToolBox_Entity_Types

if TYPE_CHECKING:
    from ToolBox_ECS_V1.ToolBox_Main import ToolBox_Manager
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
    dataSilo:ToolBox_Data_Silo_Manager

    #------- private properties -------#
    
    _id_key:str
    _name:str
    _node_type:ToolBox_Entity_Types
    _parent_key:str|None
    _children_keys:list[str]

    #------- Initialize class -------#

    def __init__(
            self,
            name:str|None,
            node_type:ToolBox_Entity_Types,
            id_key:str|None=None,
            parent_entitity:ToolBox_ECS_Node|str|None=None, 
            initial_data:dict[str,Any]|None=None
            
        ):
        """Required Attributes:
            name:(str) - Node's Name
            node_type:ToolBox_Entity_Types - 
        """
        super().__init__(initial_data)
        self.dataSilo = ToolBox_Data_Silo_Manager.get_instance()
        self._name = name if isinstance(name, str) else 'N/A'
        self._id_key = id_key if id_key is not None else str(uuid.uuid5(uuid.NAMESPACE_DNS, str(random.randrange(1000000000))))
        self._node_type = node_type or ToolBox_Entity_Types.NONE
        self._parent_key = parent_entitity.id_key if isinstance(parent_entitity,ToolBox_ECS_Node) else parent_entitity if isinstance(parent_entitity,str) else None
        self._children_keys = []

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
        return item in self._children_keys

    #-------public Getter & Setter methods -------#

    @property
    def id_key (self) -> str:
        """Returns this Nodes' ID / Key assignment."""
        return self._id_key

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
        _holder:list[ToolBox_ECS_Node] = []
        for _key in self._children_keys:
            _node = self.dataSilo[_key]
            _holder.append(_node)
        return _holder
    

    @property
    def siblings(self) -> list[ToolBox_ECS_Node]:
        """Return a list of sibling entities (excluding self)."""
        if not self._parent_key:
            return []
        _parent_node = self.dataSilo[self._parent_key]
        _holder:list[ToolBox_ECS_Node] = []
        for _key in _parent_node.children:
            if _key != self._id_key and self.dataSilo.get(_key) not in _holder:
                _holder.append(self.dataSilo.get(_key))
        return _holder
    
    @property
    def parent(self) -> ToolBox_ECS_Node|None:
        """Return the parent node if one is set, if not, returns None."""
        if self._parent_key is None:
            return None
        elif self._parent_key in self.dataSilo:
            return self.dataSilo[self._parent_key]
    
    @parent.setter
    def parent (self, value:ToolBox_ECS_Node|str):
        """Sets the parent Node for the current Node."""
        if isinstance(value, str):
            self._parent_key = value
        if isinstance(value, ToolBox_ECS_Node):
            self._parent_key = value._id_key
    
    @property
    def node_type (self) -> str:
        return self._node_type
    
    #------- Methods / Functions -------#

    @ToolBox_Decorator
    def add_child(self, child: ToolBox_ECS_Node|str):
        """Attach a child entity while maintaining order."""
        if isinstance(child, ToolBox_ECS_Node):
            if child._id_key in self._children_keys:
                return  # avoid duplicates
            self._children_keys.append(child._id_key)
            child._parent_key = self._id_key
        if isinstance(child, str) and child not in  self._children_keys:
            if child in self._children_keys:
                return # avoid duplicates
            self._children_keys.append(child)
            self.dataSilo[child]._parent_key = self._id_key

    @ToolBox_Decorator
    def remove_child(self, child: ToolBox_ECS_Node|str):
        """Removed child link if found"""
        if isinstance(child, ToolBox_ECS_Node):
            self._children_keys.remove(child._id_key)
            child._parent_key = None
        if isinstance(child, str) and child in self.dataSilo:
            self._children_keys.remove(child)
            self.dataSilo[child]._parent_key = None

    @ToolBox_Decorator
    def node_stricture_to_string (self, indent:int=0) -> str:
        _indent = "    "*indent
        _results = f"{_indent}{self.name} [{len(self.children)}]- {self.node_type}\n"
        for _child in self.children:
            _results += _child.node_stricture_to_string(indent = indent+1)
        return _results