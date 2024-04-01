from typing import Any, TYPE_CHECKING, Callable
import json, sys, os
import importlib

if TYPE_CHECKING:
    from ResearchOS.research_object import ResearchObject

from ResearchOS.action import Action


class JSONConverter():
    """First looks in the ResearchObject for a method to convert to/from JSON. If not found, looks for a method in this class.
    If still not found, uses json.dumps/loads."""

    def to_json(robj: "ResearchObject", name: str, input: Any, action: Action) -> str:
        to_json_method = getattr(robj, f"to_json_{name}", None)
        method_from_ro = True
        if to_json_method is None:
            to_json_method = getattr(JSONConverter, f"to_json_{name}", None)
            method_from_ro = False
        if to_json_method is not None:
            if not method_from_ro:
                return to_json_method(robj, input, action)
            else:
                return to_json_method(input, action)
        else:
            return json.dumps(input)

    def from_json(robj: "ResearchObject", name: str, input: str, action: Action) -> Any:
        from_json_method = getattr(robj, f"from_json_{name}", None)
        method_from_ro = True
        if from_json_method is None:            
            from_json_method = getattr(JSONConverter, f"from_json_{name}", None)
            method_from_ro = False
        if from_json_method is not None:
            if not method_from_ro:
                return from_json_method(robj, input, action)
            else:
                return from_json_method(input, action)
        else:
            return json.loads(input)
        
    @staticmethod
    def from_json_input_vrs(self, input_vrs: str, action: Action) -> dict:
        """Convert a JSON string to a dictionary of input variables."""
        from ResearchOS.variable import Variable
        from ResearchOS.DataObjects.data_object import DataObject
        input_vr_ids_dict = json.loads(input_vrs)
        input_vrs_dict = {}
        dataobject_subclasses = DataObject.__subclasses__()
        for name, vr_dict in input_vr_ids_dict.items():
            # Two keys: "VR" and "slice".
            input_vrs_dict[name] = {}
            if not isinstance(vr_dict, dict) or (isinstance(vr_dict, dict) and "VR" not in vr_dict.keys()):
                input_vrs_dict[name] = vr_dict
                continue
            if isinstance(vr_dict["VR"], dict):
                cls_prefix = [key for key in vr_dict["VR"].keys()][0]
                attr_name = [value for value in vr_dict["VR"].values()][0]
                cls = [cls for cls in dataobject_subclasses if cls.prefix == cls_prefix][0]
                input_vrs_dict[name]["VR"] = {cls: attr_name}                
            else:
                vr = Variable(id = vr_dict["VR"], action = action)
                input_vrs_dict[name]["VR"] = vr
            slice_var_tmp = input_vr_ids_dict[name]["slice"]
            if not isinstance(slice_var_tmp, (str, type(None))):
                slice_var = []
                for i in range(len(slice_var_tmp)):
                    if isinstance(slice_var_tmp[i], dict):
                        slice_var.append(slice(slice_var_tmp[i]['start'], slice_var_tmp[i]['stop'], slice_var_tmp[i]['step']))
                    else:
                        slice_var.append(slice_var_tmp[i])
            else:
                slice_var = slice_var_tmp
            input_vrs_dict[name]["slice"] = slice_var
        return input_vrs_dict
    
    @staticmethod
    def to_json_input_vrs(self, input_vrs: dict, action: Action) -> str:
        """Convert a dictionary of input variables to a JSON string."""        
        tmp_dict = {}
        for key, vr_dict in input_vrs.items():
            tmp_dict[key] = {}
            if not isinstance(vr_dict, dict) or (isinstance(vr_dict, dict) and "VR" not in vr_dict.keys()):
                tmp_dict[key] = vr_dict
                continue
            if isinstance(vr_dict["VR"], dict):
                tmp_dict[key]["VR"] = {key.prefix: value for key, value in vr_dict["VR"].items()} # DataObject level & attribute.
            else:
                tmp_dict[key]["VR"] = vr_dict["VR"].id # Variables
            slice_var_tmp = vr_dict["slice"]
            if not isinstance(slice_var_tmp, (str, type(None))):
                slice_var = []
                for curr_slice_var in slice_var_tmp:
                    if isinstance(curr_slice_var, slice):
                        slice_var.append({'start': curr_slice_var.start, 'stop': curr_slice_var.stop, 'step': curr_slice_var.step})
                    else:
                        slice_var.append(curr_slice_var)
            else:
                slice_var = slice_var_tmp
            tmp_dict[key]["slice"] = slice_var
        return json.dumps(tmp_dict)
    
    @staticmethod
    def from_json_output_vrs(self, output_vrs: str, action: Action) -> dict:
        """Convert a JSON string to a dictionary of output variables."""
        from ResearchOS.variable import Variable
        from ResearchOS.DataObjects.data_object import DataObject
        data_subclasses = DataObject.__subclasses__()
        output_vr_ids_dict = json.loads(output_vrs)
        output_vrs_dict = {}
        for name, vr_id in output_vr_ids_dict.items():
            if isinstance(vr_id, dict):
                for key, value in vr_id.items():
                    cls = [cls for cls in data_subclasses if cls.prefix == key]
                    output_vrs_dict[name] = {cls: value}
            else:
                vr = Variable(id = vr_id, action = action)
                output_vrs_dict[name] = vr
        return output_vrs_dict
    
    @staticmethod
    def to_json_output_vrs(self, output_vrs: dict, action: Action) -> str:
        """Convert a dictionary of output variables to a JSON string."""
        return json.dumps({key: value.id for key, value in output_vrs.items()})
    
    @staticmethod
    def from_json_vrs_source_pr(self, vrs_source_pr: str, action: Action) -> dict:
        """Convert a JSON string to a dictionary of source processes for the input variables."""
        from ResearchOS.PipelineObjects.logsheet import Logsheet
        from ResearchOS.PipelineObjects.process import Process
        vrs_source_pr_ids_dict = json.loads(vrs_source_pr)
        vrs_source_pr_dict = {}
        for name, pr_id in vrs_source_pr_ids_dict.items():            
            if not isinstance(pr_id, list):
                if pr_id.startswith(Process.prefix):
                    pr = Process(id = pr_id, action = action)
                else:
                    pr = Logsheet(id = pr_id, action = action)                
            else:
                pr = [Process(id = pr_id, action = action) if pr_id.startswith(Process.prefix) else Logsheet(id = pr_id, action = action) for pr_id in pr_id]
            vrs_source_pr_dict[name] = pr
        return vrs_source_pr_dict
    
    @staticmethod
    def to_json_vrs_source_pr(self, vrs_source_pr: dict, action: Action) -> str:
        """Convert a dictionary of source processes for the input variables to a JSON string."""
        json_dict = {}
        for vr_name, pr in vrs_source_pr.items():
            if not isinstance(pr, list):
                json_dict[vr_name] = pr.id
            else:
                json_dict[vr_name] = [value.id for value in pr]
        return json.dumps(json_dict) 
    
    @staticmethod
    def from_json_batch(self, batch: str, action: Action) -> list:
        """Convert a JSON string to a list of batch elements."""
        from ResearchOS.DataObjects.data_object import DataObject
        prefix_list = json.loads(batch)
        if prefix_list is None:
            return None
        data_subclasses = DataObject.__subclasses__()
        return [cls for cls in data_subclasses if cls.prefix in prefix_list]    
    
    @staticmethod
    def to_json_batch(self, batch: list, action: Action) -> str:
        """Convert a list of batch elements to a JSON string."""
        if batch is None:
            return json.dumps(None)
        return json.dumps([cls.prefix for cls in batch])
    
    @staticmethod
    def from_json_lookup_vrs(self, lookup_vrs: str, action: Action) -> dict:
        """Convert a JSON string to a dictionary of lookup variables."""
        from ResearchOS.variable import Variable
        lookup_vrs_ids_dict = json.loads(lookup_vrs)
        lookup_vrs_dict = {}
        for key, value in lookup_vrs_ids_dict.items():
            lookup_vrs_dict[key] = {}
            for vr_id, vr_names in value.items():             
                vr = Variable(id = vr_id, action = action)
                lookup_vrs_dict[key][vr] = vr_names 
        return lookup_vrs_dict                
    
    @staticmethod
    def to_json_lookup_vrs(self, lookup_vrs: dict, action: Action) -> str:
        """Convert a dictionary of lookup variables to a JSON string."""
        return json.dumps({key: {k.id: v for k, v in value.items()} for key, value in lookup_vrs.items()})
    
    @staticmethod
    def from_json_level(self, json_level: str, action: Action) -> type:
        """Convert a JSON string to a Process level.
        
        Args:
            self
            level (string) : IDK
            
        Returns:
            the JSON ''level'' as a type"""
        from ResearchOS.DataObjects.data_object import DataObject
        level = json.loads(json_level)
        classes = DataObject.__subclasses__()
        for cls in classes:
            if hasattr(cls, "prefix") and cls.prefix == level:
                return cls

    @staticmethod
    def to_json_level(self, level: type, action: Action) -> str:
        """Convert a Process level to a JSON string."""
        if level is None:
            return json.dumps(None)
        return json.dumps(level.prefix)
    
    @staticmethod
    def from_json_method(self, json_method: str, action: Action) -> Callable:
        """Convert a JSON string to a method.
        
        Args:
            self
            json_method (string) : JSON method to convert as a string
        
        Returns:
            Callable: IDK note add fancy linking thing once you know what a callable
            Returns None if the method name is not found (e.g. if code changed locations or something)"""
        method_name = json.loads(json_method)
        if method_name is None:
            return None
        module_name, *attribute_path = method_name.split(".")
        if module_name not in sys.modules:
            module = importlib.import_module(module_name)
        attribute = module
        for attr in attribute_path:
            attribute = getattr(attribute, attr)
        return attribute

    @staticmethod
    def to_json_method(self, method: Callable, action: Action) -> str:
        """Convert a method to a JSON string.
        
        Args:
            self
            method (Callable) : python object representing code thats about to be run
        
        Returns:
            the method as a JSON string"""
        if method is None:
            return json.dumps(None)
        return json.dumps(method.__module__ + "." + method.__qualname__)