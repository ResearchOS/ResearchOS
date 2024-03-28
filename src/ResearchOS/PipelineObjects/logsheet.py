from typing import Any
import json, csv, platform, os
import copy

import networkx as nx
import numpy as np

import time

from ResearchOS.DataObjects.data_object import DataObject
from ResearchOS.variable import Variable
from ResearchOS.DataObjects.dataset import Dataset
from ResearchOS.research_object import ResearchObject
from ResearchOS.PipelineObjects.pipeline_object import PipelineObject
from ResearchOS.action import Action
from ResearchOS.research_object_handler import ResearchObjectHandler
from ResearchOS.idcreator import IDCreator
from ResearchOS.default_attrs import DefaultAttrs
from ResearchOS.DataObjects.data_object import load_data_object_classes
from ResearchOS.validator import Validator

# Defaults should be of the same type as the expected values.
all_default_attrs = {}
all_default_attrs["path"] = None
all_default_attrs["headers"] = []
all_default_attrs["num_header_rows"] = None
all_default_attrs["class_column_names"] = {}

computer_specific_attr_names = ["path"]

# read_logsheet_stream = open("logfile_read_logsheet.log", "w")

class Logsheet(PipelineObject):

    prefix = "LG"

    def __init__(self, path: str = all_default_attrs["path"], headers: list = all_default_attrs["headers"],
                num_header_rows: int = all_default_attrs["num_header_rows"], class_column_names: dict = all_default_attrs["class_column_names"], **kwargs):
        if self._initialized:
            return
        self.path = path
        self.headers = headers
        self.num_header_rows = num_header_rows
        self.class_column_names = class_column_names
        super().__init__(**kwargs)

    ### Logsheet path
        
    def validate_path(self, path: str, action: Action, default: Any) -> None:
        """Validate the logsheet path.
        
        Args:
            self
            path (string) : logsheet path as a string
        
        Returns:
            None
        
        Raises:
            ValueError: invalid path format"""
        if path == default:
            return
        # 1. Check that the path exists in the file system.
        if not isinstance(path, str):
            raise ValueError("Path must be a string!")
        if not os.path.exists(path):
            raise ValueError("Specified path does not exist!")
        # 2. Check that the path is a file.
        if not os.path.isfile(path):
            raise ValueError("Specified path is not a file!")
        # 3. Check that the file is a CSV.
        if not path.endswith(("csv", "xlsx", "xls")):
            raise ValueError("Specified file is not a CSV!")
        
    def load_path(self, action: Action) -> None:
        """Load the logsheet path."""
        return ResearchObjectHandler.get_user_computer_path(self, "path", action)
        
    ### Logsheet headers
    
    def validate_headers(self, headers: list, action: Action, default: Any) -> None:
        """Validate the logsheet headers. These are the headers that are in the logsheet file.
        The headers must be a list of tuples, where each tuple has 3 elements:
        1. A string (the name of the header)
        2. A type (the type of the header)
        3. A valid variable ID (the ID of the Variable that the header corresponds to)
        
        Args: 
            self
            headers (list) : headers in the logsheet file as a list of tuples each with 3 elements
        
        Returns:
            None
        
        Raises:
            ValueError: incorrect ''header'' format"""
        if headers == default:
            return
        self.validate_path(self.path, action, None)

        # 1. Check that the headers are a list.
        if not isinstance(headers, list):
            raise ValueError("Headers must be a list!")
        
        # 2. Check that the headers are a list of tuples and meet the other requirements.        
        for header in headers:
            if not isinstance(header, tuple):
                raise ValueError("Headers must be a list of tuples!")
            # 3. Check that each header tuple has 3 elements.        
            if len(header) != 4:
                raise ValueError("Each header tuple must have 4 elements!")
            # 4. Check that the first element of each header tuple is a string.        
            if not isinstance(header[0], str):
                raise ValueError("First element of each header tuple must be a string!")
            if header[1] not in [str, int, float]:
                raise ValueError("Second element of each header tuple must be a Python type!")
            if header[2] not in DataObject.__subclasses__():
                raise ValueError("Third element of each header tuple must be a ResearchObject subclass!")
            # 6. Check that the third element of each header tuple is a valid variable ID.                
            if not isinstance(header[3],(str, Variable)):
                raise ValueError("Fourth element of each header tuple must be a valid pre-existing variable ID OR the variable object itself!")
            if isinstance(header[3], str) and not (header[3].startswith(Variable.prefix) and ResearchObjectHandler.object_exists(header[3], action)):
                raise ValueError("Fourth element of each header tuple (if provided as a str) must be a valid pre-existing variable ID!")
            
        logsheet = self._read_and_clean_logsheet(nrows = 1)
        headers_in_logsheet = logsheet[0]
        header_names = [header[0] for header in headers]
        missing = [header for header in headers_in_logsheet if header not in header_names]

        if len(missing) > 0:
            raise ValueError(f"The headers {missing} do not match between logsheet and code!")
            
    def to_json_headers(self, headers: list, action: Action) -> str:
        """Convert the headers to a JSON string.
        Also sets the VR's name and level.
        
        Args:
            self
            headers (list) : headers in the logsheet file as a list of tuples
            
        Returns:
            ''headers'' as a JSON string using ''json.dumps''"""
        str_headers = []        
        for header in headers:
            # Update the Variable object with the name if it is not already set, and the level.
            if isinstance(header[3], Variable):
                vr = header[3]                
            else:
                vr = Variable(id = header[3], action = action)
            default_attrs = DefaultAttrs(vr).default_attrs
            kwarg_dict = {"name": header[0]}
            vr._setattrs(default_attrs, kwarg_dict, action, None)
            str_headers.append((header[0], str(header[1])[8:-2], header[2].prefix, vr.id))
        return json.dumps(str_headers)

    def from_json_headers(self, json_var: str, action: Action) -> list:
        """Convert the JSON string to a list of headers.
        
        
        Args:
            self
            json_var (string) : JSON string returned by ''to_json_headers''
            
        Returns:
            formatted list of headers"""
        load_data_object_classes()
        subclasses = DataObject.__subclasses__()
        str_var = json.loads(json_var)
        headers = []
        mapping = {
            "str": str,
            "int": int,
            "float": float
        }
        for header in str_var:
            cls_header = [cls for cls in subclasses if cls.prefix == header[2]][0]
            headers.append((header[0], mapping[header[1]], cls_header, header[3]))                
        return headers
            
    ### Num header rows
            
    def validate_num_header_rows(self, num_header_rows: int, action: Action, default: Any) -> None:
        """Validate the number of header rows. If it is not valid, the value is rejected.
        
        Args:
            self
            num_header_rows (int) : number of header rows as an integer
            
        Returns:
            None
            
        Raises:
            ValueError: invalid ''num_header_rows'' format"""
        if num_header_rows == default:
            return
        if not isinstance(num_header_rows, (int, float)):
            raise ValueError("Num header rows must be numeric!")
        if num_header_rows<0:
            raise ValueError("Num header rows must be positive!")
        if num_header_rows % 1 != 0:
            raise ValueError("Num header rows must be an integer!")  
        
    ### Class column names
        
    def validate_class_column_names(self, class_column_names: dict, action: Action, default: Any) -> None:
        """Validate the class column names. Must be a dict where the keys are the column names in the logsheet and the values are the DataObject subclasses.
        
        Must be a dict where the keys are the column names in the logsheet and the values are the DataObject subclasses.
        
        Args:
            self
            class_column_names (dict) : dictionary where keys are logsheet column names & values are ''DataObject'' subcclasses
            
        Returns:
            None
            
        Raises:
            ValueError: incorrect format of ''class_column_names'' """
        if class_column_names == default:
            return
        self.validate_path(self.path, action, None)
        # 1. Check that the class column names are a dict.
        if not isinstance(class_column_names, dict):
            raise ValueError("Class column names must be a dict!")
        # 2. Check that the class column names are a dict of str to type.        
        for key, value in class_column_names.items():
            if not isinstance(key, str):
                raise ValueError("Keys of class column names must be strings!")
            if not issubclass(value, DataObject):
                raise ValueError("Values of class column names must be Python types that subclass DataObject!")
            
        headers = self._read_and_clean_logsheet(nrows = 1)[0]
        if not all([header in headers for header in class_column_names.keys()]):
            raise ValueError("The class column names must be in the logsheet headers!")

    def from_json_class_column_names(self, json_var: dict, action: Action) -> dict:
        """Convert the dict from JSON string where values are class prefixes to a dict where keys are column names and values are DataObject subclasses.
        QUESTION confused about data flow/the order that these functions are called"""     
        prefix_var = json.loads(json_var)
        class_column_names = {}
        all_classes = ResearchObjectHandler._get_subclasses(ResearchObject)
        for key, prefix in prefix_var.items():
            for cls in all_classes:
                if hasattr(cls, "prefix") and cls.prefix == prefix:
                    class_column_names[key] = cls
                    break
        return class_column_names
    
    def to_json_class_column_names(self, var: dict, action: Action) -> dict:
        """Convert the dict from a dict where keys are column names and values are DataObject subclasses to a JSON string where values are class prefixes.
        
        Convert the dict from a dict where keys are column names and values are DataObject subclasses to a JSON string where values are class prefixes.
        UNCLEAR QUESTION does it return a JSON string or a dict? is the JSON string just the format of the new dict values?
        
        Args:
            self
            var (dict) : same dict as ''class_column_name'' in ''validate_class_column_names''
        
        Returns:
            new dict where keys are are logsheet column names and values are a JSON sring of class prefixes IDK"""        
        prefix_var = {}
        for key in var:
            prefix_var[key] = var[key].prefix
        return json.dumps(prefix_var)

    #################### Start class-specific methods ####################
    def _read_and_clean_logsheet(self, nrows: int = None) -> list:
        """Read the logsheet (CSV only) and clean it."""
        logsheet = []
        if platform.system() == "Windows":
            first_elem_prefix = "ï»¿"
        else:
            first_elem_prefix = '\ufeff'
        if self.path.endswith(("xlsx", "xls")):
            raise ValueError("CSV files only!")
        with open(self.path, "r") as f:
            reader = csv.reader(f, delimiter=',', quotechar='"')            

            for row_num, row in enumerate(reader):                                    
                logsheet.append(row)
                if nrows is not None and row_num == nrows-1:
                    break
        
        # 7. Check that the headers all match the logsheet.
        logsheet[0][0] = logsheet[0][0][len(first_elem_prefix):]
        return logsheet
    
    def load_xlsx(self) -> list:
        """Load the logsheet as a list of lists using Pandas.
        
        Returns:
            list of logsheet values from excel"""        
        df = pd.read_excel(self.path, header = None)
        return df.values.tolist()
    
    # @profile(stream = read_logsheet_stream)
    def read_logsheet(self) -> None:
        """Run the logsheet import process.
        
        Returns:
            None
        
        Raises:
            ValueError: more header rows than logsheet rows or incorrect schema format?"""
        global all_default_attrs
        action = Action(name = "read logsheet")
        ds = Dataset(id = self._get_dataset_id(), action = action)
        validator = Validator(self, action)      
        validator.validate(self.__dict__, all_default_attrs)

        # 1. Load the logsheet (using built-in Python libraries)
        if self.path.endswith(("xlsx", "xls")):
            full_logsheet = self.load_xlsx()
        else:
            full_logsheet = self._read_and_clean_logsheet()

        if len(full_logsheet) < self.num_header_rows:
            raise ValueError("The number of header rows is greater than the number of rows in the logsheet!")

        # Run the logsheet import.
        # headers = full_logsheet[0:self.num_header_rows]
        if len(full_logsheet) == self.num_header_rows:
            logsheet = []
        else:
            logsheet = full_logsheet[self.num_header_rows:]

        # logsheet = logsheet[0:50] # For testing purposes, only read the first 50 rows.
        
        # For each row, connect instances of the appropriate DataObject subclass to all other instances of appropriate DataObject subclasses.
        headers_in_logsheet = full_logsheet[0]
        all_headers = self.headers
        header_names = [header[0] for header in self.headers]
        header_types = [header[1] for header in self.headers]
        header_levels = [header[2] for header in self.headers]
        header_vrids = [header[3] for header in self.headers]
        # Load/create all of the Variables
        vr_list = []
        vr_obj_list = []
        for idx, vr_id in enumerate(header_vrids):
            if isinstance(vr_id, Variable):
                vr = vr_id
            else:
                vr = Variable(id = vr_id, action = action)
            vr_obj_list.append(vr)
            vr_list.append(vr.id)
            
        # Order the class column names by precedence in the schema so that higher level objects always exist before lower level.
        schema = ds.schema
        schema_graph = nx.DiGraph()
        schema_graph.add_edges_from(schema)
        order = list(nx.topological_sort(schema_graph))
        if len(order) <= 1:
            raise ValueError("The schema must have at least 2 elements including the Dataset!")
        order = order[1:] # Remove the Dataset class from the order.
        dobj_column_names = []
        for cls in order:
            for column_name, cls_item in self.class_column_names.items():
                if cls is cls_item:
                    dobj_column_names.append(column_name)

        start_get_dobj_names = time.time()
        # Get all of the names of the data objects, after they're cleaned for SQLite.
        cols_idx = [headers_in_logsheet.index(header) for header in dobj_column_names] # Get the indices of the data objects columns.
        dobj_names = [] # The matrix of data object names (values in the logsheet).
        for row in logsheet:
            dobj_names.append([])
            for idx in cols_idx:
                raw_value = row[idx]
                type_class = header_types[idx]
                value = self._clean_value(type_class, raw_value)
                dobj_names[-1].append(value)
        for row_num, row in enumerate(dobj_names):
            if not all([str(cell).isidentifier() for cell in row]):
                raise ValueError(f"Row #{row_num+self.num_header_rows+1} (1-based): All data object names must be non-empty and valid variable names!")        
                        
        for idx, cls in enumerate(order):
            lists = list(set([tuple(row[0:idx+1]) for row in dobj_names]))
            [dobj_names.append(list(l)) for l in lists if len(list(l)) < len(order) and list(l) not in dobj_names]

        all_dobjs_ordered = [] # The list of DataObject instances.
        id_creator = IDCreator(action.conn)
        for row in dobj_names:
            cls = order[len(row)-1] # The class to create.
            all_dobjs_ordered.append(cls(id = id_creator.create_ro_id(cls), action = action, name = row[-1])) # Add the Data Object to the beginning of each row.                                      
        
        # Assign the values to the DataObject instances.
        # Validates that the logsheet is of valid format.
        # i.e. Doesn't have conflicting values for one level (empty/None is OK)
        attrs_cache_dict = {}
        default_none_vals = {str: None, int: np.array(float('nan')), float: np.array(float('nan'))}
        for row_num, row in enumerate(logsheet):
            row_attrs = [{} for _ in range(len(order))] # The list of dicts of attributes for each DataObject instance.

            # Get the list of data object names for this row.
            row_dobj_names = dobj_names[row_num]
            row_dobjs = []
            for idx in range(len(row_dobj_names)):
                curr_list = row_dobj_names[0:idx+1]
                curr_list_idx = dobj_names.index(curr_list)
                row_dobjs.append(all_dobjs_ordered[curr_list_idx])

            # Assign all of the data to the appropriate DataObject instances.
            # Includes the "data object columns" so that the DataObjects have an attribute with the name of the header name.
            for header in all_headers:
                name = header[0]
                col_idx = headers_in_logsheet.index(name)                
                type_class = header[1]
                level = header[2]
                level_idx = order.index(level)
                vr_id = header[3]                
                value = self._clean_value(type_class, row[headers_in_logsheet.index(name)])                                    
                # Set up the cache dict for this data object.
                if not row_dobjs[level_idx].id in attrs_cache_dict:
                    attrs_cache_dict[row_dobjs[level_idx].id] = {}
                # Set up the cache dict for this data object for this attribute.
                if name not in attrs_cache_dict[row_dobjs[level_idx].id]:
                    attrs_cache_dict[row_dobjs[level_idx].id][name] = default_none_vals[type_class]
                print("Row: ", row_num+self.num_header_rows+1, "Column: ", name, "Value: ", value)
                prev_value = attrs_cache_dict[row_dobjs[level_idx].id][name]
                if prev_value is not default_none_vals[type_class] and (type(prev_value) == np.ndarray and not np.isnan(prev_value)):                    
                    if prev_value == value or value == default_none_vals[type_class] or np.isnan(value):
                        continue
                    raise ValueError(f"Row # (1-based): {row_num+self.num_header_rows+1} Column: {name} has conflicting values!")
                attrs_cache_dict[row_dobjs[level_idx].id][name] = value
                row_attrs[level_idx][vr_id] = attrs_cache_dict[row_dobjs[level_idx].id][name]
            for idx, attrs in enumerate(row_attrs):
                row_dobjs[idx]._setattrs({}, attrs, action = action, pr_id = self.id)                           

        # Arrange the address ID's that were generated into an edge list.
        # Then assign that to the Dataset.
        addresses = []
        dobj_names = [[ds.name] + row for row in dobj_names]
        for row in dobj_names:
            for idx in range(1, len(row)):
                pair = [row[idx-1], row[idx]]
                if pair not in addresses:
                    addresses.append(pair)
        all_default_attrs = DefaultAttrs(ds)
        ds._setattrs(all_default_attrs.default_attrs, {"addresses": addresses}, action = action, pr_id = self.id)

        # Set all the paths to the DataObjects.
        for idx, row in enumerate(dobj_names):
            action.add_sql_query(all_dobjs_ordered[idx].id, "path_insert", (action.id_num, all_dobjs_ordered[idx].id, json.dumps(row[1:])))

        action.exec = True
        action.commit = True
        action.execute() # Commit the action.

    def _clean_value(self, type_class: type, raw_value: Any) -> Any:
        """Convert to proper type and clean the value of the logsheet cell."""
        try:
            value = type_class(raw_value)
        except ValueError:
            value = raw_value
        if isinstance(value, str):
            value = value.replace("'", "''") # Handle single quotes.
            value = value.strip()
        if value == '': # Empty
            value = None
        if type_class is int:
            if value is None:
                value = np.array(float('nan'))
            else:
                value = float(value)
        return value