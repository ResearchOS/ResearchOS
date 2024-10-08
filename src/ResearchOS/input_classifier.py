from typing import Any
import os

import tomli as tomllib
import json

from ResearchOS.constants import LOAD_CONSTANT_FROM_FILE_KEY, LOGSHEET_VAR_KEY, DATA_FILE_KEY, DATA_OBJECT_NAME_KEY
from ResearchOS.custom_classes import InputVariable, Constant, DataObjectName, Unspecified, DataFilePath, LoadConstantFromFile, LogsheetVariable
from ResearchOS.helper_functions import is_dynamic_variable, is_specified

def classify_input_type(input: Any, package_folder: str = "") -> tuple:
    """Takes in an input from a TOML file and returns the class of the input.
    Also returns the attributes as a dict, which may be empty if unneeded for that input type."""
    attrs = {}

    if not is_specified(input):
        return Unspecified, attrs
    
    if isinstance(input, str):
        if input.startswith("__"):
            if input == DATA_OBJECT_NAME_KEY:
                return DataObjectName, attrs
            if input.startswith(LOGSHEET_VAR_KEY):
                return LogsheetVariable, attrs
        if is_dynamic_variable(input):
            return InputVariable, attrs
        attrs = {'value': input}
        return Constant, attrs
    
    if isinstance(input, dict):
        if len(input.keys()) != 1:
            attrs['value'] = input
            return Constant, attrs
        key = list(input.keys())[0]
        if key == LOAD_CONSTANT_FROM_FILE_KEY:
            attrs['value'] = load_constant_from_file(input[key], package_folder)
            return LoadConstantFromFile, attrs
        if key == DATA_FILE_KEY:
            attrs = {'value': input[key]}
            return DataFilePath, attrs

    attrs['value'] = input
    return Constant, attrs

def load_constant_from_file(file_name: str, package_folder: str) -> Any:
    """Load a constant from a file."""
    full_path = os.path.join(package_folder, file_name)
    if full_path.endswith('.toml'):
        with open(full_path, 'rb') as f:
            value = tomllib.load(f)
    elif full_path.endswith('.json'):
        with open(full_path, 'rb') as f:
            value = json.load(f)
    return value