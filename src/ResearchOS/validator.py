from typing import TYPE_CHECKING, Any, Callable
import sys, os

import networkx as nx

if TYPE_CHECKING:
    from ResearchOS.research_object import ResearchObject

from ResearchOS.action import Action
from ResearchOS.default_attrs import DefaultAttrs
from ResearchOS.code_inspector import get_returned_variable_names, get_input_variable_names
from ResearchOS.Digraph.rodigraph import ResearchObjectDigraph

class Validator():
    def __init__(self, research_object: "ResearchObject", action = Action):
        self.robj = research_object
        self.default_attrs = DefaultAttrs(research_object).default_attrs
        self.action = action

    def validate(self, attrs: dict, default_attrs: dict):
        for key, value in attrs.items():            
            validate_method = getattr(self.robj, f'validate_{key}', None)
            method_in_ro = True
            # If the validation method isn't in the research object, check the validator.
            if not validate_method:                
                validate_method = getattr(Validator, f'validate_{key}', None)
                method_in_ro = False
            # If the validation method was found, use it.
            if validate_method:
                if method_in_ro:
                    validate_method(value, self.action, default_attrs[key])
                else:
                    validate_method(self.robj, value, self.action, default_attrs[key])

    ## input & output VRs methods
    @staticmethod
    def validate_input_vrs(robj: "ResearchObject", inputs: dict, action: Action, default: Any) -> None:
        """Validate that the input variables are correct."""
        from ResearchOS.research_object_handler import ResearchObjectHandler
        input_vr_names_in_code = []
        if not robj.is_matlab:
            input_vr_names_in_code = get_input_variable_names(robj.method)
        if inputs == default:
            return
        Validator.validate_method(robj, robj.method, action, None)
        if not isinstance(inputs, dict):
            raise ValueError("Variables must be a dictionary.")
        default_attrs_list = list(DefaultAttrs(robj).default_attrs.keys())
        for key, value in inputs.items():
            if not isinstance(key, str):
                raise ValueError("Variable names in code must be strings.")
            if not str(key).isidentifier():
                raise ValueError("Variable names in code must be valid variable names.")
            if not isinstance(value, dict):
                raise ValueError("Variables must be dicts themselves.")
            if ["VR", "slice"] != list(value.keys()):
                raise ValueError("Variables must have keys 'VR' and 'slice'.")
            if isinstance(value["VR"], dict):
                _validate_dataobject_level_attr(value["VR"], action, default_attrs_list)
            else:
                if not ResearchObjectHandler.object_exists(value["VR"].id, action):
                    raise ValueError("Variable ID's must reference existing Variables.")

    @staticmethod
    def validate_output_vrs(robj: "ResearchObject", outputs: dict, action: Action, default: Any) -> None:
        """Validate that the output variables are correct."""
        from ResearchOS.research_object_handler import ResearchObjectHandler
        from ResearchOS.variable import Variable
        output_vr_names_in_code = []
        if not robj.is_matlab:
            output_vr_names_in_code = get_returned_variable_names(robj.method)
        if outputs == default:
            return
        Validator.validate_method(robj, robj.method, action, None)
        if not isinstance(outputs, dict):
            raise ValueError("Variables must be a dictionary.")
        for key, value in outputs.items():
            if not isinstance(key, str):
                raise ValueError("Variable names in code must be strings.")
            if not str(key).isidentifier():
                raise ValueError("Variable names in code must be valid variable names.")
            if not isinstance(value, Variable):
                raise ValueError("Variable ID's must be Variable objects.")
            if not ResearchObjectHandler.object_exists(value.id, action):
                raise ValueError("Variable ID's must reference existing Variables.")
        if not robj.is_matlab and output_vr_names_in_code is not None and not all([vr_name in output_vr_names_in_code for vr_name in outputs.keys()]):
            raise ValueError("Output variables must be returned by the method.")
        
    @staticmethod
    def validate_vrs_source_pr(self, vrs_source_pr: dict, action: Action, default: Any) -> None:
        """Validate that the source process for the input variables is correct."""
        from ResearchOS.research_object_handler import ResearchObjectHandler
        from ResearchOS.PipelineObjects.process import Process
        from ResearchOS.PipelineObjects.logsheet import Logsheet
        if vrs_source_pr == default:
            return
        if not isinstance(vrs_source_pr, dict):
            raise ValueError("Source process must be a dictionary.")
        pGraph = ResearchObjectDigraph(action = action)
        # Temporarily add the new connections to the graph.
        # Make them all lists.
        all_edges = []
        tmp_vrs_source_pr = {}
        for vr_name_in_code, pr in vrs_source_pr.items():
            tmp_vrs_source_pr[vr_name_in_code] = pr
            if not isinstance(pr, list):
                tmp_vrs_source_pr[vr_name_in_code] = [pr]
            curr_var_list = tmp_vrs_source_pr[vr_name_in_code]
            for pr_elem in curr_var_list:
                for vr_name, vr in self.input_vrs.items():
                    if vr_name not in tmp_vrs_source_pr.keys():
                        continue
                    all_edges.append((pr_elem.id, self.id, vr["VR"].id))
        # all_edges = [(pr.id, self.id, vr.id) for vr in self.input_vrs.values() for pr in vrs_source_pr.values()]
        for edge in all_edges:
            pGraph.add_edge(edge[0], edge[1], edge_id = edge[2])
        for vr_name_in_code, pr in tmp_vrs_source_pr.items():
            if not isinstance(vr_name_in_code, str):
                raise ValueError("Variable names in code must be strings.")
            if not str(vr_name_in_code).isidentifier():
                raise ValueError("Variable names in code must be valid variable names.")
            if not all([isinstance(pr_elem, (Process, Logsheet)) for pr_elem in pr]):
                raise ValueError("Source process must be a Process or Logsheet object.")
            if not all([ResearchObjectHandler.object_exists(pr_elem.id, action) for pr_elem in pr]):
                raise ValueError("Source process must reference existing Process.")
            # if not (vr_name_in_code in self.input_vrs.keys() or vr_name_in_code in self.lookup_vrs.keys()):
            #     raise ValueError("Source process VR's must reference the input variables to this function. Ensure that the 'self.set_vrs_source_pr()' line is after the 'self.set_input_vrs()' line.")
        # Check that the PipelineObject Graph does not contain a cycle.
        if not nx.is_directed_acyclic_graph(pGraph):
            cycles = nx.simple_cycles(pGraph)
            for cycle in cycles:
                print('Cycle:', cycle)
                for node, next_node in zip(cycle, cycle[1:]):
                    print('Edge:', node, '-', next_node)
            raise ValueError("Source process VR's must not create a cycle in the PipelineObject Graph.")
    
    @staticmethod
    def validate_batch(self, batch: list, action: Action, default: Any) -> None:
        """Validate that the batch is correct."""
        from ResearchOS.DataObjects.dataset import Dataset
        from ResearchOS.DataObjects.data_object import DataObject
        if batch == default:
            return
        if not isinstance(batch, list):
            raise ValueError("Batch must be a list.")
        data_subclasses = DataObject.__subclasses__()
        if not all([batch_elem in data_subclasses for batch_elem in batch]):
            raise ValueError("Batch elements must be DataObject types.")
        if len(batch) <= 1:
            return
        ds = Dataset(id = self._get_dataset_id(), action = action)
        schema_graph = nx.MultiDiGraph(ds.schema)
        schema_ordered = list(nx.topological_sort(schema_graph))        
        max_idx = 0
        for batch_elem in batch:
            idx = schema_ordered.index(batch_elem)
            if idx < max_idx:
                raise ValueError("Batch elements must be in order of the schema, from highest to lowest.")
            max_idx = idx

    @staticmethod
    def validate_subset_id(self, subset_id: str, action: Action, default: Any) -> None:
        """Validate that the subset ID is correct."""
        from ResearchOS.research_object_handler import ResearchObjectHandler
        if subset_id == default:
            return
        if not ResearchObjectHandler.object_exists(subset_id, action):
            raise ValueError("Subset ID must reference an existing Subset.")
        
    @staticmethod
    def validate_level(self, level: type, action: Action, default: Any) -> None:
        """Validate that the level is correct."""
        from ResearchOS.DataObjects.data_object import DataObject
        if level == default:
            return
        if not isinstance(level, type):
            raise ValueError("Level must be a type!")
        if level not in DataObject.__subclasses__():
            raise ValueError("Level must be a subclass of DataObject.")
        
    @staticmethod
    def validate_method(self, method: Callable, action: Action, default: Any) -> None:
        """Validate that the Python method attribute is correct.
        
        Args:
            self
            method (Callable) : IDK what callable is
        
        Returns:
            None
        
        Raises:
            ValueError: incorrect inputted method format"""
        if method == default:
            return
        if method is None and self.is_matlab:
            return
        if not self.is_matlab and method is None:
            raise ValueError("Method cannot be None if is_matlab is False.")
        if not isinstance(method, Callable):
            raise ValueError("Method must be a callable function!")
        if method.__module__ not in sys.modules:
            raise ValueError("Method must be in an imported module!")
        
    @staticmethod
    def validate_mfolder(self, mfolder: str, action: Action, default: Any) -> None:
        """Validate that the MATLAB folder attribute is correct."""
        if mfolder == default:
            return
        if not self.is_matlab and mfolder is None:
            return
        if not isinstance(mfolder, str):
            raise ValueError("Path must be a string!")
        if not os.path.exists(mfolder):
            raise ValueError("Path must be a valid existing folder path!")
        
    @staticmethod
    def validate_mfunc_name(self, mfunc_name: str, action: Action, default: Any) -> None:
        """Validate that the MATLAB function name is correct."""
        if mfunc_name == default:
            return
        Validator.validate_mfolder(self, self.mfolder, action, None)
        if not self.is_matlab and mfunc_name is None: 
            return
        if not isinstance(mfunc_name, str):
            raise ValueError("Function name must be a string!")
        if not str(mfunc_name).isidentifier():
            raise ValueError("Function name must be a valid variable name!") 
        
    @staticmethod
    def validate_lookup_vrs(self, lookup_vrs: dict, action: Action, default: Any) -> None:
        """Validate that the lookup variables are correct.
        Dict keys are var names in code, values are dicts with keys as Variable objects and values as lists of strings of var names in code."""
        from ResearchOS.variable import Variable
        if lookup_vrs == default:
            return
        if not isinstance(lookup_vrs, dict):
            raise ValueError("Lookup variables must be a dictionary.")
        for key, value in lookup_vrs.items():
            if not isinstance(key, str):
                raise ValueError("Variable names in code must be strings.")
            if not str(key).isidentifier():
                raise ValueError("Variable names in code must be valid variable names.")
            if not isinstance(value, dict):
                raise ValueError("Lookup variable values must be a dictionary.")
            for k, v in value.items():
                if not isinstance(k, Variable):
                    raise ValueError("Lookup variable keys must be Variable objects.")
                if not all([isinstance(vr_name, str) for vr_name in v]):
                    raise ValueError("Lookup variable values must be lists of strings.")
                if not all([str(vr_name).isidentifier() for vr_name in v]):
                    raise ValueError("Lookup variable values must be lists of valid variable names.")
                # if not all([vr_name in get_input_variable_names(self.method) for vr_name in v]):
                #     raise ValueError("Lookup variable values must be lists of valid variable names in the method.")
        
def _validate_dataobject_level_attr(level_attr: dict, action: Action, default_attr_names: list) -> None:
    """Validate the data object level attribute. Correct format is a dictionary with the level as the key and the attribute name as the value."""
    if not isinstance(level_attr, dict):
        raise ValueError("Data object level & attribute must be a dict!")
    for key, value in level_attr.items():
        if not isinstance(key, type):
            raise ValueError("Data object level must be a type!")
        if value not in default_attr_names:
            raise ValueError("Data object attribute must be a valid attribute name!")