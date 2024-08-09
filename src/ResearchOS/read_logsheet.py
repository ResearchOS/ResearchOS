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

from ResearchOS.create_dag_from_toml import get_package_index_dict
from ResearchOS.constants import DATASET_SCHEMA_KEY, DATASET_KEY, LOGSHEET_NAME, MAT_DATA_FOLDER_KEY, DATASET_FILE_SCHEMA_KEY, PACKAGE_SETTINGS_KEY
from ResearchOS.custom_classes import Logsheet, OutputVariable
from ResearchOS.hash_dag import get_output_var_hash
from ResearchOS.matlab_eng import import_matlab
from ResearchOS.io import schema_to_file

def _read_and_clean_logsheet(logsheet_path: str, nrows: int = None) -> list:
        """Read the logsheet (CSV only) and clean it.
        If nrows is provided, only read the first nrows rows."""
        logsheet = []
        if platform.system() == "Windows":
            first_elem_prefix = "ï»¿"
        else:
            first_elem_prefix = '\ufeff'
        if logsheet_path.endswith(("xlsx", "xls")):
            raise ValueError("CSV files only!")
        with open(logsheet_path, "r") as f:
            reader = csv.reader(f, delimiter=',', quotechar='"')            

            for row_num, row in enumerate(reader):                                    
                logsheet.append(row)
                if nrows is not None and row_num == nrows-1:
                    break
        
        # 7. Check that the headers all match the logsheet.
        if logsheet[0][0].startswith(first_elem_prefix):
            logsheet[0][0] = logsheet[0][0][len(first_elem_prefix):]
        return logsheet

def read_logsheet(project_folder: str = None) -> None:
    """Run the logsheet import process.
    
    Returns:
        None
    
    Raises:
        ValueError: more header rows than logsheet rows or incorrect schema format?"""
    logsheet_start_time = time.time()

    if not project_folder:
        project_folder = os.getcwd()

    matlab = import_matlab(is_matlab=True)

    # 2. Get the logsheet object
    logsheet = get_logsheet_dict(project_folder)    
    logsheet_path = logsheet['path']
    num_header_rows = logsheet['num_header_rows']
    headers_in_toml = logsheet['headers']
    class_column_names = logsheet['class_column_names']
    data_objects_str = os.environ[DATASET_SCHEMA_KEY]
    data_objects = data_objects_str.split(".")

    # 1. Read the logsheet file (using built-in Python libraries)
    full_logsheet = _read_and_clean_logsheet(logsheet_path)    

    if len(full_logsheet) < num_header_rows:
        raise ValueError("The number of header rows is greater than the number of rows in the logsheet!")
    elif len(full_logsheet) == num_header_rows:
        logsheet = []
    else:
        logsheet = full_logsheet[num_header_rows:]
    
    # For each row, connect instances of the appropriate DataObject subclass to all other instances of appropriate DataObject subclasses.
    headers_in_logsheet = full_logsheet[0]
    header_names = [h for h in headers_in_toml.keys()]
    header_types = [value[1] for _, value in headers_in_toml.items()]
        
    # Order the class column names by precedence in the schema so that higher level objects always exist before lower level.
    schema = data_objects
    order = schema
    if len(order) <= 1:
        raise ValueError("The schema must have at least 2 elements including the Dataset!")
    order = order[1:] # Remove the Dataset class from the order.
    dobj_column_names = []
    for schema_cls in order:
        for cls, cls_column_name in class_column_names.items():
            if cls == schema_cls:
                dobj_column_names.append(cls_column_name)

    # Get all of the names of the data objects, after they're cleaned for SQLite.
    dobj_cols_idx = [headers_in_logsheet.index(header) for header in dobj_column_names] # Get the indices of the data objects columns.
    dobj_names = [] # The matrix of data object names (values in the logsheet).
    for row_num, row in enumerate(logsheet): 
        curr_dobj_name = ""
        for idx in dobj_cols_idx:
            raw_value = row[idx]
            type_class = header_types[idx]
            if type_class != "str":
                raise ValueError(f"Check TOML for Data Object Column {header_names[idx]}: Data object names must be strings!")
            value = _clean_value(type_class, raw_value)
            # Check that all of the data object names are valid variable names.
            if not value.isidentifier():
                raise ValueError(f"Logsheet row #{row_num+num_header_rows+1} Column {idx+1}: All data object names must be non-empty and valid variable names!")
            curr_dobj_name += value + "."
        curr_dobj_name = curr_dobj_name[:-1] # Remove the trailing period.
        dobj_names.append(curr_dobj_name)        
                    
    # Get all Data Object names that are not in the lowest level.
    for idx, type_str in enumerate(order[0:-1]):
        # Get the index of the n'th period in the string.
        type_names = [".".join(dobj_name.split(".")[0:idx+1]) for dobj_name in dobj_names]
        # Make this list unique.
        type_names = list(set(type_names))
        # Add the names to the dobj_names list.
        [dobj_names.append(name) for name in type_names if name not in dobj_names]

    # To format the print statements.
    max_len = -1
    for header in headers_in_logsheet:
        if len(header) > max_len:
            max_len = len(header)   
    
    # Assign the values to the DataObject instances.
    all_attrs = {}
    for column in headers_in_toml:
        col_idx = headers_in_logsheet.index(column)
        level = headers_in_toml[column][0]
        level_idx = order.index(level)
        level_dobjs = [dobj for dobj in dobj_names if dobj.count(".") == level_idx]
        type_class = headers_in_toml[column][1]
        # Get the index of the column that corresponds to the level of the DataObjects.
        level_column_idx = dobj_cols_idx[level_idx]
        print("{:<{width}} {:<25}".format(f"Column: {column}", f"Level: {level}", width = max_len+2))
        for dobj in level_dobjs:
            # Get all of the values
            values = [_clean_value(type_class, row[col_idx]) for row in logsheet if dobj == row[level_column_idx]]
            non_none_values = list(set([value for value in values if value is not None]))
            num_values_non_none = len(non_none_values)
            if num_values_non_none == 0:
                value = None
            elif num_values_non_none > 1:
                raise ValueError(f"Logsheet Column: {column[0]} Data Object: {dobj.name} has multiple values!")
            else:
                value = non_none_values[0]

            # Store it to the all_attrs dict.
            if dobj not in all_attrs:
                all_attrs[dobj] = {}
            all_attrs[dobj][column] = value     

    # Create logsheet runnable node.
    print("Assigning Data Object values...")
    logsheet_attrs = {}
    logsheet_attrs['outputs'] = [header for header in headers_in_toml]
    logsheet_node = Logsheet(id = str(uuid.uuid4()), name = LOGSHEET_NAME, attrs = logsheet_attrs)

    logsheet_graph = nx.MultiDiGraph()
    logsheet_graph.add_node(logsheet_node.id, node = logsheet_node)  

    mapping = {}
    for column in headers_in_toml:
        output_var = OutputVariable(id=str(uuid.uuid4()), name=LOGSHEET_NAME + "." + column, attrs={})
        mapping[column] = output_var.id
        logsheet_graph.add_node(output_var.id, node = output_var)
        logsheet_graph.add_edge(logsheet_node.id, output_var.id)
    
    # Get the hash for each output variable.    
    hashes = {}
    for column in mapping:
        node_id = mapping[column]
        hashes[node_id] = get_output_var_hash(logsheet_graph, node_id)

    # Write the values to the DataObjects.
    matlab_eng = matlab['matlab_eng']
    ros_m_files_folder = "/Users/mitchelltillman/Desktop/Work/Stevens_PhD/Non_Research_Projects/ResearchOS_Python/src/ResearchOS/overhaul"
    save_fcn_name = "safe_save"
    matlab_eng.addpath(ros_m_files_folder)
    mat_data_folder = os.environ[MAT_DATA_FOLDER_KEY.upper()]
    if mat_data_folder == ".":
        mat_data_folder = project_folder
    save_fcn = getattr(matlab_eng, save_fcn_name)
    # Sort the all_attrs dict alphabetically by key
    sorted_keys = sorted(all_attrs.keys())
    all_attrs = {key: all_attrs[key] for key in sorted_keys}
    count = 0
    num_dobjs = len(all_attrs)
    for dobj, attrs in all_attrs.items():
        count += 1
        dobj_to_save = {}
        # TESTING
        # if count >= 10:
        #     break
        for attr in attrs:
            node_id = mapping[attr]
            hash = hashes[node_id]
            dobj_to_save[hash] = attrs[attr] if attrs[attr] is not None else math.nan
        # Save the values to file.
        lock_file_path = os.path.join(mat_data_folder, dobj.replace('.', os.sep) + ".lock")
        try:
            os.remove(lock_file_path)
        except FileNotFoundError:
            pass
        print(f"Saving Data Object {count} of {num_dobjs}: ", dobj)
        save_fcn(mat_data_folder, dobj, dobj_to_save, nargout=0)

    # Save the logsheet output to "logsheet_output.mat" file in the project's "src/" folder.
    # schema: [data_object_type1, data_object_type2, ...]
    # data_objects: [data_object1, data_object2, ...]
    logsheet_wrapper_m_file_name = "save_logsheet_output"
    logsheet_save = getattr(matlab_eng, logsheet_wrapper_m_file_name)
    logsheet_save(mat_data_folder, schema, dobj_names, nargout=0)

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

def get_logsheet_dict(project_folder: str) -> dict:
    """Return the logsheet dict from the project_settings.toml file."""
    index_dict = get_package_index_dict(project_folder)
    logsheet_path = index_dict[LOGSHEET_NAME]
    if not logsheet_path:
        raise ValueError("The package settings file path must be specified in the index.toml! Default is 'src/project_settings.toml'.")
    if not os.path.isabs(logsheet_path[0]):
        logsheet_path[0] = os.path.join(project_folder, logsheet_path[0])
    with open(logsheet_path[0], "rb") as f:
        logsheet_dict = tomllib.load(f)
    return logsheet_dict
    

if __name__ == "__main__":
    read_logsheet("/Users/mitchelltillman/Desktop/Work/Stevens_PhD/Non_Research_Projects/ResearchOS_Test_Project_Folder")