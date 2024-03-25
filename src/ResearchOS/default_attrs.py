import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ResearchOS.research_object import ResearchObject

class DefaultAttrs():
    """A class to store the default attributes of a class across all three levels."""
    def __init__(self, research_object: "ResearchObject"):
        """Initialize the default attributes."""        
        from ResearchOS.research_object_handler import ResearchObjectHandler

        cls = research_object.__class__
        if cls in ResearchObjectHandler.default_attrs:
            self.__dict__ = ResearchObjectHandler.default_attrs[cls]
            self.__dict__["default_attrs"]["name"] = research_object.id
            return
        
        from ResearchOS.research_object import all_default_attrs as ro_default_attrs
        from ResearchOS.PipelineObjects.pipeline_object import all_default_attrs as p_default_attrs
        from ResearchOS.DataObjects.data_object import all_default_attrs as d_default_attrs

        from ResearchOS.research_object import computer_specific_attr_names as ro_computer_specific_attr_names
        from ResearchOS.PipelineObjects.pipeline_object import computer_specific_attr_names as p_computer_specific_attr_names
        from ResearchOS.DataObjects.data_object import computer_specific_attr_names as d_computer_specific_attr_names

        from ResearchOS.DataObjects.data_object import DataObject
        from ResearchOS.PipelineObjects.pipeline_object import PipelineObject

        from ResearchOS.DataObjects.dataset import Dataset

        try:
            module = importlib.import_module(cls.__module__)
        except ImportError:
            raise ImportError(f"The class {cls} could not be imported.")

        # Custom Data Object subclasses don't have default attrs, so for consistency give them dummy empty default attrs
        class_default_attrs = {}
        class_computer_specific_attr_names = []
        if cls not in DataObject.__subclasses__() or cls == Dataset:        
            class_default_attrs = getattr(module, "all_default_attrs")
            class_computer_specific_attr_names = getattr(module, "computer_specific_attr_names")

        if cls in DataObject.__subclasses__():
            parent_default_attrs = d_default_attrs
            parent_computer_specific_attr_names = d_computer_specific_attr_names
        elif cls in PipelineObject.__subclasses__():
            parent_default_attrs = p_default_attrs
            parent_computer_specific_attr_names = p_computer_specific_attr_names
        else:
            # Variable class
            parent_default_attrs = {}
            parent_computer_specific_attr_names = []

        class_default_attrs["name"] = research_object.id
        self.default_attrs = {**ro_default_attrs, **parent_default_attrs, **class_default_attrs}
        self.computer_specific_attr_names = ro_computer_specific_attr_names + parent_computer_specific_attr_names + class_computer_specific_attr_names
        ResearchObjectHandler.default_attrs[cls] = self.__dict__