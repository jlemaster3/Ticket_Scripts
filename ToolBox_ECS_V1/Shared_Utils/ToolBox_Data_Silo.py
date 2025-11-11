#-------------------------------------------------
#   Imports
#-------------------------------------------------
from __future__ import annotations

import threading, copy
import pandas as pd
import numpy as np
from typing import Any, TYPE_CHECKING, Dict, List, Optional, Union, Hashable
from collections import UserDict

from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Filters import *
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Types import (
    ToolBox_Amount_Options,
    ToolBox_File_Types, 
    ToolBox_Entity_Types, 
    ToolBox_REGEX_Patterns
)
from ToolBox_ECS_V1.Shared_Utils.ToolBox_Utils import (
    gen_uuid_key
)

if TYPE_CHECKING:
    from ToolBox_ECS_V1.Nodes import *

#-------------------------------------------------
#   Decorator Functions / Wrappers
#-------------------------------------------------

def ToolBox_Decorator(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        return result
    return wrapper

#-------------------------------------------------
#   Classes
#-------------------------------------------------


class ToolBox_Data_Silo_Manager (UserDict):

    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()

    # Using imported types from ToolBox_Types
    File_Types = ToolBox_File_Types
    Entity_Types = ToolBox_Entity_Types
    Amount_Options = ToolBox_Amount_Options
    REGEX_Patterns = ToolBox_REGEX_Patterns

    #------- private properties -------#

    _instance = None
    _lock = threading.Lock()

    _delimiter:str = "."
    _nodes_by_types:dict[str,dict[str,ToolBox_ECS_Node]] = {}# str is node._id_kay
    _settings:dict[str,Any] = {} # contrains nesting settings

    _dataframe:pd.DataFrame
    #------- Initialize class -------#

    
    def __new__(cls):
        with cls._lock:

            if cls._instance is None:
                cls._instance = super().__new__(cls)
                if not hasattr(cls, '_ToolBox_ECS_Node'):
                    from ToolBox_ECS_V1.Nodes import ToolBox_ECS_Node
                    cls._ToolBox_ECS_Node = ToolBox_ECS_Node
                cls._nodes_by_types:dict[str,dict[str,ToolBox_ECS_Node]] = {}
                cls._dataframe = pd.DataFrame(columns=['entity_id'])
                cls._dataframe.set_index("entity_id", inplace=True)
                if not hasattr(cls, '_ToolBox_ECS_File_Node'):
                    from ToolBox_ECS_V1.Nodes import ToolBox_ECS_File_Node
                    cls._ToolBox_ECS_File_Node = ToolBox_ECS_File_Node
                if not hasattr(cls, 'ToolBox_XLSX_File_Node'):
                    from ToolBox_ECS_V1.Nodes import ToolBox_XLSX_File_Node
                    cls._ToolBox_XLSX_File_Node = ToolBox_XLSX_File_Node
                if not hasattr(cls, 'ToolBox_IWS_XLSX_Runbook_File_Node'):
                    from ToolBox_ECS_V1.Nodes import ToolBox_IWS_XLSX_Runbook_File_Node
                    cls._ToolBox_IWS_XLSX_Runbook_File_Node = ToolBox_IWS_XLSX_Runbook_File_Node
                if not hasattr(cls, 'ToolBox_IWS_JIL_File_Node'):
                    from ToolBox_ECS_V1.Nodes import ToolBox_IWS_JIL_File_Node
                    cls._ToolBox_IWS_JIL_File_Node = ToolBox_IWS_JIL_File_Node
                if not hasattr(cls, 'ToolBox_IWS_Obj_Node'):
                    from ToolBox_ECS_V1.Nodes import ToolBox_IWS_Obj_Node
                    cls._ToolBox_IWS_Obj_Node = ToolBox_IWS_Obj_Node
                if not hasattr(cls, 'ToolBox_CSV_File_Node'):
                    from ToolBox_ECS_V1.Nodes import ToolBox_CSV_File_Node
                    cls._ToolBox_CSV_File_Node = ToolBox_CSV_File_Node
        return cls._instance
    
    def __setitem__(self, key, value):
        if isinstance(value, str):
            self.data[key] = value
        else:
            self.data[key] = value
    
    def __getitem__(self, key:str):
        if isinstance(key, str):
            return self.get(key)
    
    def __len__(self):
        """Returns the total number of nodes contained."""
        _total:int = len(self.data.keys())
        for _node_type in self._nodes_by_types.keys():
            _total += len(self._nodes_by_types[_node_type].keys())
        return _total
    
    def __str__(self) -> str:
        return self._format_dict(self._nodes_by_types)
    
    @classmethod
    def get_instance(cls) -> "ToolBox_Data_Silo_Manager":
        """Returns the singleton instance of ToolBox_Data_Silo_Manager, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @ToolBox_Decorator
    def get (self, key:str, default:Any = None) -> Any:
        keys = key.split(self._delimiter)
        try:
            _found_settings:Any = None
            _found_node:Any = None
            for k in keys:
                if k in self._settings.keys():
                    _found_settings = self._settings[k]
                for _type, _nodes in self._nodes_by_types.items():
                    if k in _nodes.keys():
                        _found_node = _nodes[k]
            if _found_settings is not None:
                return _found_settings
            if _found_node is not None:
                return _found_node
            return self.data[key]
        except (KeyError, TypeError):
            return default
        
    #-------public Getter & Setter methods -------#

    @property
    def nodes (self) -> list[ToolBox_ECS_Node]:
        """Returns this a list of all Nodes"""
        return [_n for _et_v in self._nodes_by_types.values() for _n in _et_v.values() if isinstance(_n, self._ToolBox_ECS_Node)]
    
    @property
    def file_nodes (self) -> list[ToolBox_ECS_File_Node]:
        """Returns this a list of all File Nodes"""
        return [_n for _et_v in self._nodes_by_types.values() for _n in _et_v.values() if isinstance(_n, self._ToolBox_ECS_File_Node)]
        
    
    @property
    def JIL_file_nodes (self) -> list[ToolBox_IWS_JIL_File_Node]:
        """Returns this a list of all *.jil or *.job File Nodes"""
        return [_n for _et_v in self._nodes_by_types.values() for _n in _et_v.values() if (
            isinstance(_n, self._ToolBox_IWS_JIL_File_Node) and (
                _n.node_type == ToolBox_Entity_Types.FILE_JIL or
                _n.node_type == ToolBox_Entity_Types.FILE_JOB
            )
        )]

    @property
    def CSV_file_nodes (self) -> list[ToolBox_CSV_File_Node]:
        """Returns this a list of all *.csv Nodes"""
        return [_n for _et_v in self._nodes_by_types.values() for _n in _et_v.values() if ( 
            isinstance(_n, self._ToolBox_CSV_File_Node) and 
            _n.node_type == ToolBox_Entity_Types.FILE_CSV
        )]
        
    @property
    def XLSX_file_nodes (self) -> list[ToolBox_XLSX_File_Node]:
        """Returns this a list of all *.xlsx Nodes"""
        return [_n for _et_v in self._nodes_by_types.values() for _n in _et_v.values() if ( 
            isinstance(_n, self._ToolBox_XLSX_File_Node) and 
            _n.node_type == ToolBox_Entity_Types.FILE_XLSX
        )]
        
    @property
    def IWS_Runbook_file_nodes (self) -> list[ToolBox_IWS_XLSX_Runbook_File_Node]:
        """Returns this a list of all *.xlsx Runbook Nodes"""
        return [_n for _et_v in self._nodes_by_types.values() for _n in _et_v.values() if ( 
            isinstance(_n, self._ToolBox_IWS_XLSX_Runbook_File_Node) and 
            _n.node_type == ToolBox_Entity_Types.IWS_XLS_RUNBOOK
        )]

    @property
    def IWS_object_nodes (self) -> list[ToolBox_IWS_Obj_Node]:
        """Returns this a list of all IWS Object Nodes"""
        return [_n for _et_v in self._nodes_by_types.values() for _n in _et_v.values() if isinstance(_n, self._ToolBox_IWS_Obj_Node)]        

    @property
    def IWS_Job_Stream_nodes (self) -> list[ToolBox_IWS_Obj_Node]:
        """Returns this a list of all IWS Job Stream Nodes"""
        return [_n for _n in self._nodes_by_types[ToolBox_Entity_Types.IWS_JOB_STREAM].values() if isinstance(_n, self._ToolBox_IWS_Obj_Node)]
        
    @property
    def IWS_Job_nodes (self) -> list[ToolBox_IWS_Obj_Node]:
        """Returns this a list of all IWS Job Stream Nodes"""
        return [_n for _n in self._nodes_by_types[ToolBox_Entity_Types.IWS_JOB].values() if isinstance(_n, self._ToolBox_IWS_Obj_Node)]
    
    @property
    def statistics (self) -> str:
        _line_holder = [f"Data Silo Stats :"]
        for _type_counter, (_type_name, _type_collection) in enumerate(self._nodes_by_types.items()):
            _line_holder.append(f"[{_type_counter}] '{_type_name}' - Total nodes: [{len(_type_collection.keys())}]")
        return '\n'.join(_line_holder)

    #------- Methods / Functions -------#

    @ToolBox_Decorator
    def _update_node_types (self):
        """adds all avalible ToolBox_Entity_Types as avalible keys in self._nodes_by_types"""
        for _et in ToolBox_Entity_Types:
            if _et.name not in self._nodes_by_types.keys():
                self._nodes_by_types[_et.name] = {}

    @ToolBox_Decorator
    def _format_dict(cls, data:dict[str, Any], indent: int = 0) -> str:
        """Recursively formats a dictionary as an indented tree."""
        tree_str =""
        if isinstance(data, dict):
            for key, val in data.items():
                keyStr = f"[{str(key)}]" if isinstance(val, dict) else str(key)+ " : "
                tree_str += "\n"+" " * indent + keyStr
                tree_str += cls._format_dict(val, indent + 4)
        else:
            tree_str += str(data)
        return tree_str

    @ToolBox_Decorator
    def append_node (self, node:ToolBox_ECS_Node):
        if node.node_type not in self._nodes_by_types.keys():
            self._nodes_by_types[node.node_type] = {}
        if node._id_key not in self._nodes_by_types[node.node_type].keys():
            self._nodes_by_types[node.node_type][node._id_key] = node
        else:
            self.log.warning(f"Duplicate ID Key found in '{node.node_type}', dropping duplciate node : '{node.name}' key :  [{node._id_key}]")

    @ToolBox_Decorator
    def remove_node(self, key:str):
        for _et in ToolBox_Entity_Types:
            if key in self._nodes_by_types[_et].keys():
                self.log.debug(f"Removing Node : [{self._nodes_by_types[_et][key]._id_key}] - '{self._nodes_by_types[_et][key].name}'")
                del self._nodes_by_types[_et][key]
                
    @ToolBox_Decorator
    def get_nodes_by_name_containing_term (self, term:str) -> list[ToolBox_ECS_Node]:
        """Returns a list of nodes wit the target name."""
        _holder:list[ToolBox_ECS_Node] = []
        for _node in self.nodes:
            if term.upper() in _node.name.upper():
                _holder.append(_node)
        return _holder
    
    @ToolBox_Decorator
    def get_IWS_nodes_containing_term (self, term:str) -> list[ToolBox_IWS_Obj_Node]:
        """Returns a list of nodes wit the target name."""
        _holder:list[ToolBox_IWS_Obj_Node] = []

        for _node in self.IWS_object_nodes:
            if term.upper() in _node.name.upper():
                _holder.append(_node)
        return _holder

    #------- Methods / Functions -------#
    @ToolBox_Decorator
    def create_entity (self, key_id:str|None=None, components:Optional[Dict[str, Any]] = None) -> str:
        """Crearte a new entity with optional components."""
        if (key_id is None or (isinstance(key_id,str) and key_id.strip() == '')):
            _rand_key = str(np.random.randint(1000,1000000))
            _enitity_id = gen_uuid_key(_rand_key)
        else:
            _enitity_id = key_id
        _data = components or {}

        for _comp_name in _data.keys():
            if _comp_name not in self._dataframe.columns:
                self._dataframe[_comp_name] = None

        _row = pd.Series(_data, name = _enitity_id)
        self._dataframe.loc[_enitity_id] = _row
        return _enitity_id
    
    @ToolBox_Decorator
    def add_component (self, entity_id:str, component_name:str, component_data:Any):
        """Add or update a component for an entity."""
        if entity_id not in self._dataframe.index:
            raise KeyError(f"Entity '{entity_id}' does not exist")
        if component_name not in self._dataframe.columns:
            self._dataframe[component_name] = None
        self._dataframe.at[entity_id, component_name] = component_data

    @ToolBox_Decorator
    def delete_entity (self, entity_id:str):
        """Removes the entity entirly"""
        if entity_id in self._dataframe.index:
            self._dataframe.drop(entity_id, inplace=True)
    
    @ToolBox_Decorator
    def get_entity (self, entity_id:str) -> Dict[str, Any]:
        """Returns all components for entity as a Dictionary"""
        if entity_id not in self._dataframe.index:
            raise KeyError(f"Entity '{entity_id}' not found.")
        series_dict = self._dataframe.loc[entity_id].dropna().to_dict()
        return {str(k): v for k, v in series_dict.items()}
    
    @ToolBox_Decorator
    def get_entities_with (self, components: Union[str, list[str]]) -> pd.DataFrame:
        """Returns enitites that have specific components(s) present."""
        if isinstance(components, str):
            components = [components]
        _mask = self._dataframe[components].notna().all(axis=1)
        return self._dataframe[_mask]
    
    @ToolBox_Decorator
    def get_entities_where(self, **component_filters) -> pd.DataFrame:
        """Return entities that match specific component key/value pairs."""
        df = self._dataframe.copy()
        for comp, val in component_filters.items():
            if comp not in df.columns:
                return pd.DataFrame(columns=df.columns)
            df = df[df[comp] == val]
        return df

    @ToolBox_Decorator
    def all_entities(self) -> dict[str, dict[str,Any]]:
        """Return the full DataFrame of entities and components."""
        _results = {}
        for _key, _row in self._dataframe.iterrows():
            _row_dict: dict[str, Any] = {}
            for _col, _val in _row.items():
                # If value is an array-like or series, include only when it has length/size >= 1
                if isinstance(_val, (np.ndarray, pd.Series)):
                    try:
                        # Prefer shape[0] for numpy/pandas, fallback to len()
                        length = _val.shape[0] if hasattr(_val, "shape") else len(_val)
                    except Exception:
                        try:
                            length = len(_val)
                        except Exception:
                            length = 0
                    if length >= 1:
                        _row_dict[str(_col)] = _val
                elif isinstance(_val , (list, tuple, set)):
                    if len(_val ) >= 1:
                        _row_dict[str(_col)] = _val
                else:
                    # For scalars, use pd.isna to safely check for missing values
                    if not pd.isna(_val):
                        _row_dict[str(_col)] = _val
            _results[_key] = _row_dict
        return _results
    
    @property
    def entity_count (self) -> int:
        return self._dataframe.shape[0]
    
    @property
    def component_count (self) -> int:
        """Returns the number of components (columns in dataframe)"""
        return self._dataframe.shape[1]
    
    @property
    def loc(self):
        """Expose the .loc accessor of the internal DataFrame."""
        return self._dataframe.loc

    @property
    def iloc(self):
        """Expose the .iloc accessor of the internal DataFrame."""
        return self._dataframe.iloc
    
    @property
    def get_column_names(self)->list[str]:
        return self._dataframe.columns.to_list()

DataSilo:ToolBox_Data_Silo_Manager = ToolBox_Data_Silo_Manager().get_instance()