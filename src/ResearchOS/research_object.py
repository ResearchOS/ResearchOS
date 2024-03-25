from typing import Any
import copy

from .research_object_handler import ResearchObjectHandler
from .action import Action
from .sqlite_pool import SQLiteConnectionPool
from .default_attrs import DefaultAttrs
from .idcreator import IDCreator

all_default_attrs = {}
all_default_attrs["notes"] = None

computer_specific_attr_names = []

root_data_path = "data"

class ResearchObject():
    """One research object. Parent class of Data Objects & Pipeline Objects."""

    def __deepcopy__(self, memo):
        """Raise an error if attempting to deepcopy this object."""
        raise ValueError("Research objects cannot be deepcopied.")

    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, ResearchObject):
            return self.id == other.id and self is other
        return False
     
    def __new__(cls, **kwargs):
        """Create a new research object in memory. If the object already exists in memory with this ID, return the existing object."""
        if "id" not in kwargs.keys():
            raise ValueError("id is required as a kwarg")  
        id = kwargs["id"]
        if not IDCreator(None).is_ro_id(id):
            raise ValueError("id is not a valid ID.")
        del kwargs["id"]
        if id in ResearchObjectHandler.instances:
            ResearchObjectHandler.counts[id] += 1
            ResearchObjectHandler.instances[id].__dict__["prev_loaded"] = True
            ResearchObjectHandler.instances[id].__dict__["_initialized"] = True
            return ResearchObjectHandler.instances[id]
        
        ResearchObjectHandler.counts[id] = 1
        instance = super(ResearchObject, cls).__new__(cls)
        ResearchObjectHandler.instances[id] = instance
        instance.__dict__["id"] = id # Put the ID in the object.
        instance.__dict__["prev_loaded"] = False
        instance.__dict__["_initialized"] = False
        return instance 
    
    def __setattr__(self, name: str = None, value: Any = None, action: Action = None, all_attrs: DefaultAttrs = None, kwargs_dict: dict = {}) -> None:
        """Set the attribute value. If the attribute value is not valid, an error is thrown."""        
        if not self._initialized:
            self.__dict__[name] = value
            return
        # Ensure that the criteria to set the attribute are met.
        if not str(name).isidentifier():
            raise ValueError(f"{name} is not a valid attribute name.") # Offers some protection for having to eval() the name to get custom function names.        
        if name == "id":
            raise ValueError("Cannot change the ID of a research object.")
        if name == "prefix":
            raise ValueError("Cannot change the prefix of a research object.")
        if name == "name":
            if not str(value).isidentifier():
                raise ValueError(f"name attribute, value: {value} is not a valid attribute name.")
        if name == "slice" and self.id.startswith("VR"):
            self.__dict__[name] = value
            return # Store but don't save the changes to Variable slices. That is handled when saving the input VR's.
            
        # Set the attribute. Create Action when __setattr__ is called as the top level.
        if all_attrs is None:
            all_attrs = DefaultAttrs(self)                
        commit = False
        if action is None:
            commit = True
            action = Action(name = "attribute_changed")

        if not kwargs_dict:
            kwargs_dict = {name: value}
        self._setattrs(all_attrs.default_attrs, kwargs_dict, action, None)
        
        action.commit = commit
        action.exec = True
        action.execute()     
    
    def __init__(self, action: Action = None, **other_kwargs):
        """Initialize the research object.
        On initialization, all attributes should be saved! 
        Unless the object is being loaded, in which case only *changed* attributes should be saved."""
        attrs = DefaultAttrs(self) # Get the default attributes for the class.
        default_attrs_dict = attrs.default_attrs
        if "name" in other_kwargs:
            self.name = other_kwargs["name"] # Set the name to the default name.
        elif "name" not in self.__dict__:
            self.name = default_attrs_dict["name"] # Set the name to the default name.
        if "notes" in other_kwargs:
            self.notes = other_kwargs["notes"]
        elif "notes" not in self.__dict__:
            self.notes = all_default_attrs["notes"] # Set the notes to the default notes.

        prev_loaded = self.__dict__["prev_loaded"]
        del self.__dict__["prev_loaded"] # Remove prev_loaded attribute.      

        self_dict = copy.copy(self.__dict__) # Get the current values of the object's attributes. These are mostly default but could have been overriden in the constructor.
        del self_dict["_initialized"] # Remove the _initialized attribute from the kwargs so that it is not set as an attribute.        
        del self_dict["id"] # Remove the ID from the kwargs so that it is not set as an attribute.                    
        
        finish_action = False
        if action is None:
            action = Action(name = "__init__", exec = False) # One data object.
            finish_action = True                

        if prev_loaded:
            prev_exists = True
        else:
            prev_exists = ResearchObjectHandler.object_exists(self.id, action)        
        if not prev_exists:
            # Create a new object.
            query_name = "robj_exists_insert"
            params = (self.id, action.id)
            action.add_sql_query(id, query_name, params, group_name = "robj_insert")                                
        
        loaded_attrs = {}
        if prev_exists and not prev_loaded:
            # Load the existing object's attributes from the database.
            loaded_attrs = ResearchObjectHandler._load_ro(self, attrs, action)
            self.__dict__.update(loaded_attrs) # Set the loaded attributes.            
        
        # If creating a new object, save all attributes.
        # If loaded an existing object: save only the changed attributes.        
        save_dict = {}
        for attr in self_dict:
            try:
                if not prev_exists or (self_dict[attr] != default_attrs_dict[attr] and self_dict[attr] != loaded_attrs[attr]):
                    save_dict[attr] = self_dict[attr]
            except:
                pass
                
        self._setattrs(default_attrs_dict, save_dict, action, None)
        self._initialized = True

        # Set the attributes.
        if finish_action:
            action.exec = True
            action.commit = True
            action.execute()

    def _setattrs(self, default_attrs: dict, kwargs: dict, action: Action, pr_id: str) -> None:
        """Set the attributes of the object.
        default_attrs: The default attributes of the object.
        orig_kwargs: The original kwargs passed to the object.
        kwargs: The kwargs to be used to set the attributes. A combination of the default attributes and the original kwargs.
        pr_id: Indicates that I am setting VR attributes."""
        del_keys = []
        if self._initialized:
            for key in kwargs:
                try:
                    if key in self.__dict__ and self.__dict__[key] == kwargs[key]:
                        del_keys.append(key) # No change.
                except ValueError:
                    pass # Allow the Variable to not exist yet.
            
        for key in del_keys:
            del kwargs[key]
        # 1. Set simple & complex builtin attributes.
        ResearchObjectHandler._set_builtin_attributes(self, default_attrs, kwargs, action)

        # 2. Set VR attributes.
        if pr_id is not None:
            vr_attrs = {k: v for k, v in kwargs.items() if k not in default_attrs}
            ResearchObjectHandler._set_vr_values(self, vr_attrs, action, pr_id)

    def _get_dataset_id(self) -> str:
        """Get the most recent dataset ID."""        
        sqlquery = f"SELECT dataset_id FROM data_address_schemas"
        pool = SQLiteConnectionPool()
        conn = pool.get_connection()
        cursor = conn.cursor()
        result = cursor.execute(sqlquery).fetchall()
        pool.return_connection(conn)
        if not result:
            raise ValueError("Need to create a dataset and set up its schema first.")
        dataset_id = result[-1][0]        
        return dataset_id

    def get_current_schema_id(self, dataset_id: str) -> str:
        pool = SQLiteConnectionPool()
        conn = pool.get_connection()
        sqlquery = f"SELECT action_id FROM data_address_schemas WHERE dataset_id = '{dataset_id}'"
        action_ids = conn.cursor().execute(sqlquery).fetchall()
        action_ids = ResearchObjectHandler._get_time_ordered_result(action_ids, action_col_num=0)
        action_id_schema = action_ids[0][0] if action_ids else None
        if action_id_schema is None:
            pool.return_connection(conn)
            return # If the schema is empty and the addresses are empty, this is likely initialization so just return.

        sqlquery = f"SELECT schema_id FROM data_address_schemas WHERE dataset_id = '{dataset_id}' AND action_id = '{action_id_schema}'"
        schema_id = conn.execute(sqlquery).fetchone()
        schema_id = schema_id[0] if schema_id else None
        pool.return_connection(conn)
        return schema_id