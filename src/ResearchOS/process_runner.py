from typing import TYPE_CHECKING, Any
import logging, time
import os
from datetime import datetime, timezone
import json
import copy

import networkx as nx
import numpy as np

if TYPE_CHECKING:
    from .action import Action
    from ResearchOS.PipelineObjects.process import Process
    from ResearchOS.DataObjects.dataset import Dataset    

# from ResearchOS.DataObjects.data_object import DataObject
# from ResearchOS.research_object_handler import ResearchObjectHandler
from ResearchOS.sql.sql_runner import sql_order_result
from ResearchOS.var_converter import convert_var
from ResearchOS.utils.suppress_output import suppress_stdout_stderr
from ResearchOS.code_runner import CodeRunner

class ProcessRunner(CodeRunner):

    def __init__(self):
        pass

    def compute_and_assign_outputs(self, vr_values_in: dict, pr: "Process", info: dict = {}, is_batch: bool = False) -> None:
        """Run the function and assign the output variables to the DataObject node.
        """
        # NOTE: For now, assuming that there is only one return statement in the entire method.  
        if pr.is_matlab:
            if not self.matlab_loaded:
                raise ValueError("MATLAB is not loaded.")            
            fcn = getattr(self.matlab_eng, pr.mfunc_name)                        
        else:
            fcn = getattr(pr, pr.method)

        if not is_batch:
            vr_vals_in = list(vr_values_in.values())
            if self.num_inputs > len(vr_vals_in): # There's an extra input open.
                vr_vals_in.append(info)
        else:
            # Convert the vr_values_in to the right format.
            vr_vals_in = []
            for vr_name in vr_values_in:
                vr_vals_in.append(vr_values_in[vr_name])

        try:
            vr_values_out = fcn(*vr_vals_in, nargout=len(pr.output_vrs))
        except ProcessRunner.matlab.engine.MatlabExecutionError as e:
            if "ResearchOS:" not in e.args[0]:
                print("'ResearchOS:' not found in error message, ending run.")
                raise e
            return # Do not assign anything, because nothing was computed!
                
        if not isinstance(vr_values_out, tuple):
            vr_values_out = (vr_values_out,)
        if len(vr_values_out) != len(pr.output_vrs):
            raise ValueError("The number of variables returned by the method must match the number of output variables registered with this Process instance.")
            
        # Set the output variables for this DataObject node.
        idx = -1 # For MATLAB. Requires that the args are in the proper order.
        kwargs_dict = {}
        output_var_names_in_code = [vr for vr in pr.output_vrs.keys()]
        for vr_name, vr in pr.output_vrs.items():
            if not pr.is_matlab:
                idx = output_var_names_in_code.index(vr_name) # Ensure I'm pulling the right VR name because the order of the VR's coming out and the order in the output_vrs dict are probably different.
            else:
                idx += 1
            # Search through the variable to look for any matlab numeric types and convert them to numpy arrays.
            kwargs_dict[vr] = convert_var(vr_values_out[idx], ProcessRunner.matlab_numeric_types) # Convert any matlab.double to numpy arrays. (This is a recursive function.)

        self.node._setattrs({}, kwargs_dict, action = self.action, pr_id = self.pl_obj.id)