from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass    
    # from ResearchOS.research_object import ResearchObject

from ResearchOS.variable import Variable
from ResearchOS.DataObjects.data_object import DataObject

class VRHandler():

    @staticmethod
    def add_slice_to_input_vrs(input_dict: dict):
        """To add a slice to a "vr", it must be a ResearchOS Variable object."""
        new_dict = {}
        for key, vr in input_dict.items():
            if not isinstance(vr, Variable) and not (isinstance(vr, dict) and list(vr.keys())[0] in DataObject.__subclasses__()):
                new_dict[key] = vr # The variable is hard-coded
            else:
                new_dict[key] = {}
                new_dict[key]["VR"] = vr
                slice = getattr(vr, "slice", None)
                new_dict[key]["slice"] = slice
                try:
                    del vr.slice
                except:
                    pass
        return new_dict