from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass
    # from ResearchOS.variable import Variable
    # from ResearchOS.research_object import ResearchObject

class VRHandler():

    @staticmethod
    def add_slice_to_input_vrs(input_dict: dict):
        new_dict = {}
        for key, vr in input_dict.items():
            new_dict[key] = {}
            new_dict[key]["VR"] = vr
            slice = getattr(vr, "slice", None)
            new_dict[key]["slice"] = slice
            try:
                del vr.slice
            except:
                pass
        return new_dict