import platform
import csv
import time
import os
import uuid
from typing import Any
import builtins
import math

import tomli as tomllib
import networkx as nx

from ResearchOS.constants import DATASET_SCHEMA_KEY, DATASET_KEY, LOGSHEET_NAME, SAVE_DATA_FOLDER_KEY, DATASET_FILE_SCHEMA_KEY, PACKAGE_SETTINGS_KEY
from ResearchOS.custom_classes import Logsheet, OutputVariable
from ResearchOS.validation_classes import RunnableFactory
from ResearchOS.helper_functions import get_package_setting
from ResearchOS.hash_dag import hash_node
from ResearchOS.create_dag_from_toml import get_package_index_dict
from ResearchOS.parallelization import locked_write_parquet

def _read_and_clean_logsheet(logsheet_path: str, nrows: int = None, delimiter: str = ",") -> list:
        """Read the logsheet (CSV only) and clean it.
        If nrows is provided, only read the first nrows rows."""
        logsheet = []
        if platform.system() == "Windows":
            first_elem_prefix = "ï»¿"
        else:
            first_elem_prefix = '\ufeff'
        if logsheet_path.endswith(("xlsx", "xls")):
            raise ValueError("CSV files only!")
        if not os.path.exists(logsheet_path):
            raise ValueError(f"The logsheet file does not exist: {logsheet_path}")
        with open(logsheet_path, "r") as f:
            reader = csv.reader(f, delimiter=delimiter, quotechar='"')            

            for row_num, row in enumerate(reader):
                if not isinstance(row, list):
                    raise Exception(f"Row number: {row_num} is not encoded as a list! Check that row.")
                logsheet.append(row)
                if nrows is not None and row_num == nrows-1:
                    break
        
        # 7. Check that the headers all match the logsheet.
        if logsheet[0][0].startswith(first_elem_prefix):
            logsheet[0][0] = logsheet[0][0][len(first_elem_prefix):]
        return logsheet

def read_logsheet(project_folder: str = None, logsheet_toml_path: str = None, delimiter: str = ",") -> None:
    """Run the logsheet import process.
    
    Returns:
        None
    
    Raises:
        ValueError: more header rows than logsheet rows or incorrect schema format?"""
    logsheet_start_time = time.time()

    if not project_folder:
        project_folder = os.getcwd()

    # 2. Get the logsheet object
    logsheet_dict = get_logsheet_dict(project_folder, logsheet_toml_path) 
    logsheet_path = logsheet_dict['path']  
    num_header_rows = logsheet_dict['num_header_rows']    
    dataset_factors = logsheet_dict['dataset_factors']

    # 1. Read the logsheet file (using built-in Python libraries)
    full_logsheet = _read_and_clean_logsheet(logsheet_path, delimiter=delimiter)    

    if len(full_logsheet) < num_header_rows:
        raise ValueError("The number of header rows is greater than the number of rows in the logsheet!")
    elif len(full_logsheet) == num_header_rows:
        logsheet = []
    else:
        logsheet = full_logsheet[num_header_rows:]
    
    # For each row, connect instances of the appropriate DataObject subclass to all other instances of appropriate DataObject subclasses.
    headers_in_logsheet = [f.lower() for f in full_logsheet[0]]
    var_names = [h for h in logsheet_dict['headers'].keys()]
    num_columns = len(var_names)
    header_names = [h["column_name"] for h in logsheet_dict['headers'].values()]
    header_types = [h["type"] for h in logsheet_dict['headers'].values()]
    header_levels = [h["level"] for h in logsheet_dict['headers'].values()]
        
    # Order the class column names by precedence in the schema so that higher level objects always exist before lower level.
    schema = dataset_factors
    if len(schema) <= 1:
        raise ValueError("The schema must have at least 2 elements including the Dataset!")
    order = schema # Remove the Dataset class from the order.
    factor_column_names_ordered = [] # The column header names for the factors in the schema, in order.
    for factor in dataset_factors:
        if factor not in var_names:
            raise ValueError(f"Dataset factor {factor} not found in logsheet output variable names!")        
        factor_column_names_ordered.append(header_names[var_names.index(factor)].lower())

    # Get all of the names of the data objects in the lowest level ONLY - this avoids redundancy.
    dobj_cols_idx = [headers_in_logsheet.index(header) for header in factor_column_names_ordered] # Get the indices of the data objects columns in the logsheet
    dobj_names = [] # The matrix of data object names (values in the logsheet).
    for row_num, row in enumerate(logsheet): 
        curr_dobj_name = []
        for idx in dobj_cols_idx:
            raw_value = row[idx]
            type_class = header_types[idx]
            value = _clean_value(type_class, raw_value)
            # Check that all of the data object names are valid variable names.
            if not value:
                raise ValueError(f"Logsheet row #{row_num+num_header_rows+1} Column {idx+1}: All data object names must be non-empty!")
            curr_dobj_name.append(str(value))
        dobj_names.append(','.join(curr_dobj_name))        
                    
    # Get all Data Object names that are not in the lowest level.
    for idx in range(len(order[0:-1])):
        # Get the index of the n'th delimiter (comma) in the string.
        data_objects_in_level_names = [",".join(dobj_name.split(",")[0:idx+1]) for dobj_name in dobj_names]
        # Make this list unique.
        data_objects_in_level_names = list(set(data_objects_in_level_names))
        # Add the names to the dobj_names list.
        [dobj_names.append(name) for name in data_objects_in_level_names if name not in dobj_names]

    # To format the print statements.
    max_len = -1
    for header in headers_in_logsheet:
        if len(header) > max_len:
            max_len = len(header)   
    
    # Assign the values to the DataObject instances.
    all_attrs = {}
    for col_idx in range(num_columns):        
        level = header_levels[col_idx]
        type_class = header_types[col_idx]
        level_idx = [o.lower() for o in order].index(level.lower())
        level_dobjs = [dobj for dobj in dobj_names if dobj.count(",") == level_idx]        
        # Get the index of the column that corresponds to the level of the DataObjects.
        level_column_idx = dobj_cols_idx[level_idx]
        print("{:<{width}} {:<25}".format(f"Column: {header_names[col_idx]}", f"Level: {level}", width=max_len+2))                
        for dobj in level_dobjs:
            # Get all of the values
            values = [_clean_value(type_class, row[col_idx]) for row in logsheet if dobj == str(_clean_value(type_class, row[level_column_idx]))]
            non_none_values = list(set([value for value in values if value is not None]))
            num_values_non_none = len(non_none_values)
            if num_values_non_none == 0:
                value = None
            elif num_values_non_none > 1:
                raise ValueError(f"Logsheet Column: {header_names[col_idx]} Data Object: {dobj.name} has multiple values!")
            else:
                value = non_none_values[0]

            # Store it to the all_attrs dict.
            if dobj not in all_attrs:
                all_attrs[dobj] = {}
            all_attrs[dobj][var_names[col_idx].lower()] = value     

    # Create logsheet runnable node.
    print("Assigning Data Object values...")
    logsheet_attrs = {}
    logsheet_attrs['outputs'] = [header.lower() for header in logsheet_dict['headers']]
    logsheet_node = Logsheet(id = str(uuid.uuid4()), name = LOGSHEET_NAME, attrs = logsheet_attrs)

    logsheet_graph = nx.MultiDiGraph()
    logsheet_graph.add_node(logsheet_node.id, node = logsheet_node)  

    mapping = {}
    for idx, column in enumerate(logsheet_attrs['outputs']):
        output_var = OutputVariable(id=str(uuid.uuid4()), name=LOGSHEET_NAME + "." + var_names[idx], attrs={})
        mapping[column] = output_var.id
        logsheet_graph.add_node(output_var.id, node = output_var)
        logsheet_graph.add_edge(logsheet_node.id, output_var.id)
    
    # Get the hash for each output variable.    
    hashes = {}
    for column in mapping:
        node_id = mapping[column]
        hashes[node_id] = hash_node(logsheet_graph, node_id)

    # Write the values to the DataObjects.    
    try:
        save_folder_path = os.environ[SAVE_DATA_FOLDER_KEY]
    except KeyError:
        index_dict = get_package_index_dict(project_folder)
        if "save_path" not in index_dict:
            save_folder_path = project_folder
        else:            
            save_folder_path = os.sep.join([project_folder, index_dict["save_path"][0]]) if not os.path.isabs(index_dict["save_path"][0]) else index_dict["save_path"][0]               
    if save_folder_path == ".":
        save_folder_path = project_folder
    
    # Sort the all_attrs dict alphabetically by key
    sorted_keys = sorted(all_attrs.keys())
    all_attrs = {key: all_attrs[key] for key in sorted_keys}
    count = 0
    num_dobjs = len(all_attrs)    
    for dobj, attrs in all_attrs.items():
        count += 1
        dobj_to_save = {}
        for attr in attrs:
            node_id = mapping[attr]
            hash = hashes[node_id]
            dobj_to_save[hash] = attrs[attr] if attrs[attr] is not None else math.nan
        # Save the values to file.
        save_file_path = os.path.join(save_folder_path, dobj.replace(delimiter, os.sep) + ".parquet")
        print(f"Saving Data Object {count} of {num_dobjs}: ", dobj)
        # locked_write_parquet(save_file_path, df)

    elapsed_time = time.time() - logsheet_start_time
    print(f"Logsheet import complete (nrows={len(logsheet)}). Created {len(all_attrs)} new DataObjects, modified {0} DataObjects in {round(elapsed_time, 2)} seconds.")

def _clean_value(type_str: str, raw_value: Any) -> Any:
    """Convert to proper type and clean the value of the logsheet cell."""
    allowable_classes = ["str", "num", "bool"]
    if type_str not in allowable_classes:
        raise ValueError(f"Invalid type class: {type_str}. Must be one of {allowable_classes}")
    if type_str == "num":
        type_str = "float"
    type_class = getattr(builtins, type_str)
    try:
        value = type_class(raw_value)
    except ValueError:
        value = raw_value
    if isinstance(value, str):
        value = value.replace("'", "''") # Handle single quotes.
        value = value.strip()
    if value == '': # Empty
        value = None
    if type_class is float:
        if value is None:
            pass
            # value = np.array(float('nan'))
        else:
            value = float(value)
    return value

def get_logsheet_dict(project_folder: str = None, logsheet_toml_path: str = None) -> dict:
    """Return the logsheet dict from the project_settings.toml file."""

    if logsheet_toml_path is None:
        logsheet_dict = get_package_setting(project_folder, setting_name=LOGSHEET_NAME, default_value=[])
    else:
        logsheet_dict = get_package_setting(project_folder, setting_name=LOGSHEET_NAME, default_value=[], package_settings_path = logsheet_toml_path)
    if not logsheet_dict:
        return {}

    logsheet_type = RunnableFactory.create(runnable_type=LOGSHEET_NAME)
    logsheet_dict['outputs'] = [key for key in logsheet_dict['headers'].keys()] # Outputs are needed for validation.
    is_valid, err_msg = logsheet_type.validate(logsheet_dict, compilation_only=True) # Validate the logsheet.
    if not is_valid:
        raise ValueError(f"The logsheet TOML file is not valid. {err_msg}")
    logsheet_dict = logsheet_type.standardize(logsheet_dict, compilation_only=True) # Standardize the logsheet.
    return logsheet_dict
    

if __name__ == "__main__":
    read_logsheet("/Users/mitchelltillman/Desktop/Work/Stevens_PhD/Non_Research_Projects/ResearchOS_Test_Project_Folder")