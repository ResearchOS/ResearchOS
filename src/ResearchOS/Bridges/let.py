from typing import TYPE_CHECKING, Union, Any
import json

if TYPE_CHECKING:
    from ResearchOS.research_object import ResearchObject

from ResearchOS.action import Action
from ResearchOS.research_object_handler import ResearchObjectHandler
from ResearchOS.Bridges.pipeline_parts import PipelineParts

class Let(PipelineParts):

    cls_name = "Let"
    table_name = "inlets_outlets"
    id_col = "let_id"
    col_names = ["is_input", "parent_ro_id", "vr_name_in_code", "value", "show"]
    insert_query_name = "inlets_outlets_insert"
    init_attr_names = ["parent_ro"]
    allowable_none_cols = ["value"]

    def __init__(self, id: int = None,
                 is_input: bool = False,
                 parent_ro: "ResearchObject" = None,
                 vr_name_in_code: str = None,
                 show: bool = None,
                 value: Any = None,
                 action: Action = None):
        """Initializes the Let object."""
        super().__init__(id = id, action = action)

        if id:
            self.load_from_db2(id, action)
            # Make sure that the objects are created.
            subclasses = ResearchObjectHandler._get_subclasses(ResearchObject)
            cls = [cls for cls in subclasses if cls.prefix == self.parent_ro_id[0:2]][0]
            self.parent_ro = cls(id=self.parent_ro_id, action=action)
            return
        
        attrs = {}
        parent_ro_id = parent_ro.id if parent_ro else None
        attrs["is_input"] = is_input
        attrs["parent_ro_id"] = parent_ro_id
        attrs["vr_name_in_code"] = vr_name_in_code        
        attrs["value"] = value
        attrs["show"] = show
        self.init_from_attrs(**attrs, action=action)
        self.get_id_if_present(attrs, action)
        if not self.id:
            self.assign_id(attrs, action)
            self.save(attrs, action)
        # if show is None:
        #     show = False
        # self.is_input = is_input
        # self.parent_ro = parent_ro
        # self.parent_ro_id = parent_ro.id if parent_ro is not None else None
        # self.vr_name_in_code = vr_name_in_code
        # self.show = show
        # self.value = value
        

    # def load_from_db(self, is_input: bool, parent_ro_id: str, vr_name_in_code: str, value: Any, show: bool, action: Action):
    #     """Load the let objects from the database."""
    #     from ResearchOS.PipelineObjects.pipeline_object import PipelineObject
    #     subclasses = ResearchObjectHandler._get_subclasses(PipelineObject)
    #     parent_ro = None
    #     cls = [cls for cls in subclasses if cls.prefix == parent_ro_id[0:2]][0]
    #     parent_ro = cls(id = parent_ro_id, action = self.action)
    #     self.is_input = is_input
    #     self.parent_ro = parent_ro
    #     self.vr_name_in_code = vr_name_in_code
    #     self.show = show
    #     self.value = json.loads(value) if value is not None else None

    def init_from_attrs(self, is_input: bool, parent_ro_id: str, vr_name_in_code: str, value: Any, show: bool, action: Action):
        from ResearchOS.research_object import ResearchObject
        subclasses = ResearchObjectHandler._get_subclasses(ResearchObject)
        cls = [cls for cls in subclasses if (hasattr(cls, "prefix") and cls.prefix == parent_ro_id[0:2])][0]
        parent_ro = cls(id = parent_ro_id, action = action)
        self.is_input = is_input
        self.parent_ro = parent_ro
        self.vr_name_in_code = vr_name_in_code
        self.show = show
        self.value = json.loads(value) if value is not None else None