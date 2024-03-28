from typing import Any

import numpy as np

def convert_var(var: Any, matlab_numeric_types: tuple) -> Any:
    """Walk through the variable and convert any matlab numeric types to numpy arrays.
    """        
    if isinstance(var, dict):
        for key, value in var.items():
            var[key] = convert_var(value, matlab_numeric_types)
    elif isinstance(var, list):
        all_numeric = all([isinstance(value, matlab_numeric_types) for value in var])
        if all_numeric:
            try:
                var = np.array(var)
            except: # Cell arrays
                var = [convert_var(value, matlab_numeric_types) for value in var]
    elif isinstance(var, matlab_numeric_types):
        var = np.array(var)
    return var

# def convert_py_to_matlab(var: Any, matlab_numeric_types: list) -> Any:
#     """Convert any numeric matlab arrays to numpy arrays.
#     """
#     if isinstance(var, dict):
#         for key, value in var.items():
#             var[key] = convert_py_to_matlab(value)
#     elif isinstance(var, list):
#         for idx, value in enumerate(var):
#             var[idx] = convert_py_to_matlab(value)
#     elif isinstance(var, matlab_numeric_types):
#         var = matlab.double(var.tolist())
#     return var