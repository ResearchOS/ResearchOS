import os

import networkx as nx

from ResearchOS.PipelineObjects.pipeline_object import PipelineObject
from ResearchOS.action import Action
from ResearchOS.stats_runner import StatsRunner
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
all_default_attrs["vrs_source_pr"] = {}
all_default_attrs["subset_id"] = None

# For static lookup trial
all_default_attrs["lookup_vrs"] = {}

# For batching
all_default_attrs["batch"] = None

computer_specific_attr_names = ["mfolder"]

class Stats(PipelineObject):
    
    prefix = "ST"

    def __init__(self, is_matlab: bool = all_default_attrs["is_matlab"],
                 mfolder: str = all_default_attrs["mfolder"],
                 mfunc_name: str = all_default_attrs["mfunc_name"],
                 method: str = all_default_attrs["method"],
                 level: str = all_default_attrs["level"],
                 input_vrs: dict = all_default_attrs["input_vrs"],
                 vrs_source_pr: dict = all_default_attrs["vrs_source_pr"],
                 subset_id: str = all_default_attrs["subset_id"],
                 lookup_vrs: dict = all_default_attrs["lookup_vrs"],
                 batch: str = all_default_attrs["batch"],
                 **kwargs):
        if self._initialized:
            return
        self.is_matlab = is_matlab
        self.mfolder = mfolder
        self.mfunc_name = mfunc_name
        self.method = method
        self.level = level
        self.input_vrs = input_vrs
        self.vrs_source_pr = vrs_source_pr
        self.subset_id = subset_id
        self.lookup_vrs = lookup_vrs
        self.batch = batch
        super().__init__(**kwargs)
    
    def set_input_vrs(self, **kwargs) -> None:
        """Convenience function to set the input variables with named variables rather than a dict."""
        self.__setattr__("input_vrs", VRHandler.add_slice_to_input_vrs(kwargs))

    def set_vrs_source_pr(self, **kwargs) -> None:
        """Convenience function to set the source process for the input variables with named variables rather than a dict."""
        self.__setattr__("vrs_source_pr", kwargs)

    def set_lookup_vrs(self, **kwargs) -> None:
        """Convenience function to set the lookup variables with named variables rather than a dict."""
        self.__setattr__("lookup_vrs", kwargs)
    
    def run(self, force_redo: bool = False) -> None:
        """Execute the attached method.

        Args:
            force_redo (bool, optional): _description_. Defaults to False.
        """
        start_msg = f"Running {self.mfunc_name} on {self.level.__name__}s."
        print(start_msg)
        action = Action(name = start_msg)
        stats_runner = StatsRunner()        
        batches_dict_to_run, all_batches_graph, G, pool = stats_runner.prep_for_run(self, action, force_redo)
        stats_runner.add_matlab_to_path(__file__)
        curr_batch_graph = nx.MultiDiGraph()
        for batch_id, batch_value in batches_dict_to_run.items():
            if self.batch is not None:
                curr_batch_graph = nx.MultiDiGraph(all_batches_graph.subgraph([batch_id] + list(nx.descendants(all_batches_graph, batch_id))))
            stats_runner.run_batch(batch_id, batch_value, G, curr_batch_graph)

        if stats_runner.matlab_loaded and self.is_matlab:
            StatsRunner.matlab_eng.rmpath(self.mfolder)
            
        for vr_name, vr in self.output_vrs.items():
            print(f"Saved VR {vr_name} (VR: {vr.id}).")

        if action.conn:
            pool.return_connection(action.conn)