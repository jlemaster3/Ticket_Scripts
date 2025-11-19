#-------------------------------------------------
#   Imports
#-------------------------------------------------
import threading
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Union, Hashable

from ..ToolBox_Logger import OutputLogger

from .shared_utils.ToolBox_Utils import (
    gen_uuid_key
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
#   Classes
#-------------------------------------------------

class ToolBox_Data_Silo_Manager:

    #------- public properties -------#

    log:OutputLogger = OutputLogger().get_instance()

    #------- private properties -------#

    _instance = None
    _lock = threading.Lock()

    _dataframe:pd.DataFrame
    #------- Initialize class -------#
    
    def __new__(cls):
        with cls._lock:

            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._dataframe = pd.DataFrame(columns=['entity_id'])
                cls._dataframe.set_index("entity_id", inplace=True)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> "ToolBox_Data_Silo_Manager":
        """Returns the singleton instance of ToolBox_Data_Silo_Manager, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    #-------public Getter & Setter methods -------#
    @property
    def entity_count (self) -> int:
        return self._dataframe.shape[0]
    
    @property
    def component_count (self) -> int:
        """Returns the number of components (columns in dataframe)"""
        return self._dataframe.shape[1]
    
    @property
    def get_column_names(self)->list[str]:
        return self._dataframe.columns.to_list()
    
    @property
    def statistics(self) -> str:
        _results:list[str] = []
        for _col_idx, _col_name in enumerate(self.get_column_names):
            _entities_with_col = self.get_entities_with_components(_col_name)
            _results.append(f"[{_col_idx}] '{_col_name}' [{len(_entities_with_col)}]")
        return '\n'.join(_results)
    
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
            self.log.error(f"Entity '{entity_id}' does not exist")
            return
        if component_name not in self._dataframe.columns:
            self._dataframe[component_name] = None
        self._dataframe.at[entity_id, component_name] = component_data

    @ToolBox_Decorator
    def update_component(self, entity_id:str, component_name:str, component_data:Any):
        """Update a component for an entity."""
        if entity_id not in self._dataframe.index:
            self.log.error(f"Entity '{entity_id}' does not exist")
            return
        if component_name not in self._dataframe.columns:
            self.add_component(entity_id, component_name, component_data)
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
            self.log.error(f"Entity '{entity_id}' not found.")
            return {}
        series_dict = self._dataframe.loc[entity_id].dropna().to_dict()
        return {str(k): v for k, v in series_dict.items()}
    
    @ToolBox_Decorator
    def get_entities_with_components (self, components: Union[str, list[str]]) -> pd.DataFrame:
        """Returns enitites that have specific components(s) present."""
        if isinstance(components, str):
            components = [components]
        _mask = self._dataframe[components].notna().all(axis=1)
        return self._dataframe[_mask]

    @ToolBox_Decorator
    def get_entity_keys_by_component_value(self, component: str, value: Any, **component_filters) -> list[str]:
        """Return entity keys whose components match the provided component/value and any additional filters.
        - If a component name is not an exact column match it is treated as a substring and all columns containing it are considered.
        - Additional filters passed via **component_filters use the same matching logic.
        - If value (or a filter value) is a list/tuple/set, any of the contained values (including None/NaN) are considered a match.
        - For additional component_filters: if no exact match is found, and the filter value is a string (or a list of strings),
          a second pass performs a case-insensitive substring search across the resolved columns (spanning multiline strings).
        """
        df = self._dataframe
        if df.empty:
            return []
        columns = df.columns.tolist()
        def resolve_columns(name: str) -> list[str]:
            if name in columns:
                return [name]
            return [c for c in columns if name in c]
        def build_mask(target_cols: list[str], target_value: Any) -> pd.Series:
            if not target_cols:
                return pd.Series(False, index=df.index)
            # Multi-value support (list / tuple / set)
            if isinstance(target_value, (list, tuple, set)):
                values = list(target_value)
                if not values:
                    return pd.Series(False, index=df.index)
                null_requested = any(pd.isna(v) for v in values)
                non_null_values = [v for v in values if not pd.isna(v)]
                col_masks = []
                for col in target_cols:
                    series = df[col]
                    m = pd.Series(False, index=df.index)
                    if non_null_values:
                        m |= series.isin(non_null_values)
                    if null_requested:
                        m |= series.isna()
                    col_masks.append(m.fillna(False))
                # OR across columns
                out = col_masks[0]
                for m in col_masks[1:]:
                    out |= m
                return out.fillna(False)
            # Single-value path
            if pd.isna(target_value):
                comp = df[target_cols].isna()
            else:
                comp = df[target_cols].eq(target_value)
            if len(target_cols) == 1:
                return comp.iloc[:, 0].fillna(False)
            return comp.any(axis=1).fillna(False)
        # Main component filter
        main_cols = resolve_columns(component)
        if not main_cols:
            return []
        final_mask = build_mask(main_cols, value)
        if not final_mask.any():
            return []
        # Additional component filters
        for filt_name, filt_value in component_filters.items():
            filt_cols = resolve_columns(filt_name)
            if not filt_cols:
                return []
            filt_mask = build_mask(filt_cols, filt_value)
            # Fallback substring search
            def substring_search(values: list[str]) -> pd.Series:
                lower_values = [v.lower() for v in values if isinstance(v, str)]
                if not lower_values:
                    return pd.Series(False, index=df.index)
                substring_mask = pd.Series(False, index=df.index)
                for col in filt_cols:
                    col_series = df[col]
                    col_match = col_series.apply(
                        lambda x: isinstance(x, str) and any(lv in x.lower() for lv in lower_values)
                    )
                    substring_mask |= col_match.fillna(False)
                return substring_mask
            if not filt_mask.any():
                # Determine if we can attempt substring fallback
                if isinstance(filt_value, (list, tuple, set)):
                    # Only attempt if at least one string present
                    if any(isinstance(v, str) for v in filt_value):
                        sub_mask = substring_search(list(filt_value))
                        if sub_mask.any():
                            filt_mask = sub_mask
                        else:
                            return []
                    else:
                        return []
                elif isinstance(filt_value, str):
                    sub_mask = substring_search([filt_value])
                    if sub_mask.any():
                        filt_mask = sub_mask
                    else:
                        return []
                else:
                    return []
            final_mask &= filt_mask
            if not final_mask.any():
                return []
        return final_mask[final_mask].index.tolist()

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
    
    @ToolBox_Decorator
    def get_component(self, key:str, component_name:str, default:Any=None) -> Any:
        """Retrieve the value of a specific component for a given entity key.
        Returns teh default value if component_name can not be found."""
        if key not in self._dataframe.index:
            return default
        if component_name not in self._dataframe.columns:
            return default
        value = self._dataframe.at[key, component_name]
        if (value is None):
            return default
        return value

    @ToolBox_Decorator
    def entity_has_component(self, key:str, component_name:str) -> bool:
        """Check if a given entity has a specific component."""
        if key not in self._dataframe.index:
            return False
        if component_name not in self._dataframe.columns:
            return False
        value = self._dataframe.at[key, component_name]
        return (value is not None or not all(pd.isna(value)))
    
    @ToolBox_Decorator
    def entity_exists(self, key:str) -> bool:
        """Check if a given entity exists."""
        return key in self._dataframe.index
    
    @ToolBox_Decorator
    def update_entity_components(self, key:str, components:dict[str,Any]):
        """Update the components of a given entity."""
        for component_name, value in components.items():
            if component_name in self._dataframe.columns:
                self.update_component(key, component_name, value)
            else:
                self.add_component(key, component_name, value)

DataSilo:ToolBox_Data_Silo_Manager = ToolBox_Data_Silo_Manager().get_instance()