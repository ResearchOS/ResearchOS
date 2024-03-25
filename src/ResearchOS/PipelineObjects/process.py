from typing import Any
from typing import Callable
import logging

import networkx as nx

from ResearchOS.PipelineObjects.pipeline_object import PipelineObject
from ResearchOS.action import Action
from ResearchOS.process_runner import ProcessRunner
from ResearchOS.vr_handler import VRHandler

all_default_attrs = {}
# For MATLAB
all_default_attrs["is_matlab"] = False
all_default_attrs["mfolder"] = None
all_default_attrs["mfunc_name"] = None

# Main attributes
all_default_attrs["method"] = None
all_default_attrs["level"] = None
all_default_attrs["input_vrs"] = {}
all_default_attrs["output_vrs"] = {}
all_default_attrs["vrs_source_pr"] = {}
all_default_attrs["subset_id"] = None

# For import
all_default_attrs["import_file_ext"] = None
all_default_attrs["import_file_vr_name"] = None

# For including other Data Object attributes from the node lineage in the input variables.
# For example, if a Process is run on a Trial, and one of the inputs needs to be the Subject's name.
# Then, "data_object_level_attr" would be "{ros.Subject: 'name'}"
# NOTE: This is always the last input variable(s), in the order of the input variables dict.
# all_default_attrs["data_object_level_attr"] = {}

# For static lookup trial
all_default_attrs["lookup_vrs"] = {}

# For batching
all_default_attrs["batch"] = None

computer_specific_attr_names = ["mfolder"]

# log_stream = open("logfile_run_process.log", "w")

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename = "logfile.log", filemode = "w", format = "%(asctime)s - %(levelname)s - %(message)s")

do_run = False

class Process(PipelineObject):

    prefix = "PR"
    # __slots__ = tuple(all_default_attrs.keys())

    def __init__(self, is_matlab: bool = all_default_attrs["is_matlab"],
                 mfolder: str = all_default_attrs["mfolder"], 
                 mfunc_name: str = all_default_attrs["mfunc_name"], 
                 method: Callable = all_default_attrs["method"], 
                 level: type = all_default_attrs["level"], 
                 input_vrs: dict = all_default_attrs["input_vrs"], 
                 output_vrs: dict = all_default_attrs["output_vrs"], 
                 subset_id: str = all_default_attrs["subset_id"], 
                 import_file_ext: str = all_default_attrs["import_file_ext"], 
                 import_file_vr_name: str = all_default_attrs["import_file_vr_name"], 
                 vrs_source_pr: dict = all_default_attrs["vrs_source_pr"],
                 lookup_vrs: dict = all_default_attrs["lookup_vrs"],
                 batch: list = all_default_attrs["batch"],
                 **kwargs) -> None:
        if self._initialized:
            return
        self.is_matlab = is_matlab
        self.mfolder = mfolder
        self.mfunc_name = mfunc_name
        self.method = method
        self.level = level
        self.input_vrs = input_vrs
        self.output_vrs = output_vrs
        self.subset_id = subset_id
        self.import_file_ext = import_file_ext
        self.import_file_vr_name = import_file_vr_name
        self.vrs_source_pr = vrs_source_pr
        self.lookup_vrs = lookup_vrs
        self.batch = batch
        super().__init__(**kwargs)                                                                        
        
    ## import_file_ext
        
    def validate_import_file_ext(self, file_ext: str, action: Action, default: Any) -> None:
        if file_ext == default:
            return
        if not self.import_file_vr_name and file_ext is None:
            return
        if self.import_file_vr_name and file_ext is None:
            raise ValueError("File extension must be specified if import_file_vr_name is specified.")
        if not isinstance(file_ext, str):
            raise ValueError("File extension must be a string.")
        if not file_ext.startswith("."):
            raise ValueError("File extension must start with a period.")
        
    ## import_file_vr_name
        
    def validate_import_file_vr_name(self, vr_name: str, action: Action, default: Any) -> None:
        if vr_name == default:
            return
        if not isinstance(vr_name, str):
            raise ValueError("Variable name must be a string.")
        if not str(vr_name).isidentifier():
            raise ValueError("Variable name must be a valid variable name.")
        if vr_name not in self.input_vrs:
            raise ValueError("Variable name must be a valid input variable name.")                                                        
    
    def set_input_vrs(self, **kwargs) -> None:
        """Convenience function to set the input variables with named variables rather than a dict."""
        self.__setattr__("input_vrs", VRHandler.add_slice_to_input_vrs(kwargs))

    def set_output_vrs(self, **kwargs) -> None:
        """Convenience function to set the output variables with named variables rather than a dict."""
        self.__setattr__("output_vrs", kwargs)

    def set_vrs_source_pr(self, **kwargs) -> None:
        """Convenience function to set the source process for the input variables with named variables rather than a dict."""
        self.__setattr__("vrs_source_pr", kwargs)

    def set_lookup_vrs(self, **kwargs) -> None:
        """Convenience function to set the lookup variables with named variables rather than a dict."""
        self.__setattr__("lookup_vrs", kwargs)

    def run(self, force_redo: bool = False) -> None:
        """Execute the attached method.
        kwargs are the input VR's."""        
        start_msg = f"Running {self.mfunc_name} on {self.level.__name__}s."
        print(start_msg)
        action = Action(name = start_msg)
        process_runner = ProcessRunner()        
        batches_dict_to_run, all_batches_graph, G, pool = process_runner.prep_for_run(self, action, force_redo)
        curr_batch_graph = nx.MultiDiGraph()
        process_runner.add_matlab_to_path(__file__)
        for batch_id, batch_value in batches_dict_to_run.items():
            if self.batch is not None:
                curr_batch_graph = nx.MultiDiGraph(all_batches_graph.subgraph([batch_id] + list(nx.descendants(all_batches_graph, batch_id))))
            process_runner.run_batch(batch_id, batch_value, G, curr_batch_graph)

        if process_runner.matlab_loaded and self.is_matlab:
            ProcessRunner.matlab_eng.rmpath(self.mfolder)
            
        for vr_name, vr in self.output_vrs.items():
            print(f"Saved VR {vr_name} (VR: {vr.id}).")

        if action.conn:
            pool.return_connection(action.conn)
