from typing import Any, TYPE_CHECKING
import json

if TYPE_CHECKING:
    from ResearchOS.action import Action
    from ResearchOS.DataObjects.data_object import DataObject

import networkx as nx

from ResearchOS.PipelineObjects.pipeline_object import PipelineObject
from ResearchOS.DataObjects.dataset import Dataset
from ResearchOS.variable import Variable
from ResearchOS.idcreator import IDCreator
from ResearchOS.research_object_handler import ResearchObjectHandler
from ResearchOS.action import Action

all_default_attrs = {}
all_default_attrs["conditions"] = {}

computer_specific_attr_names = []

numeric_logic_options = (">", "<", ">=", "<=", )
any_type_logic_options = ("==", '=', "!=", "in", "not in", "is", "is not", "contains", "not contains")
logic_options = numeric_logic_options + any_type_logic_options
plural_logic = ("in", "not in", "contains", "not contains")

class Subset(PipelineObject):
    """Provides rules to select a subset of data from a dataset."""
    
    prefix = "SS"

    ## conditions
    
    def validate_conditions(self, conditions: dict, action: Action, default: Any) -> None:
        """Validate the condition recursively.
        Example usage:
        conditions = {
            "and": [
                [vr1.id, "<", 4],
                {
                    "or": [
                        [vr1.id, ">", 2],
                        [vr1.id, "=", 7]
                    ]
                }
            ]
        }
        
        Args:
            self
            conditions (dictionary): a dict where the keys are IDK and the values are the different conditions IDK
            action (Action): the actions associated with the conditions
            default (Any): default conditions attribute stored in ''all_default_attributes''
            
        Returns:
            None
        """
        if conditions == default:
            return
        # Validate a single condition.
        if isinstance(conditions, list):
            if len(conditions) != 3:
                raise ValueError("Condition must be a list of length 3.")
            if not IDCreator(action.conn).is_ro_id(conditions[0]):
                raise ValueError("Variable ID must be a valid Variable ID.")
            if not ResearchObjectHandler.object_exists(conditions[0], action):
                raise ValueError("Variable must be pre-existing.")
            if conditions[1] not in logic_options:
                raise ValueError("Invalid logic.")
            if conditions[1] in numeric_logic_options and not isinstance(conditions[2], int):
                raise ValueError("Numeric logical symbols must have an int value.")
            try:
                a = json.dumps(conditions[2])
            except:
                raise ValueError("Value must be JSON serializable.")
            return

        # Validate the "and"/"or" keys.
        if not isinstance(conditions, dict):
            raise ValueError("Condition must be a dict.")
        if "and" not in conditions and "or" not in conditions:
            raise ValueError("Condition must contain an 'and' or 'or' key.")
        if "and" in conditions and "or" in conditions:
            raise ValueError("Condition cannot contain both 'and' and 'or' keys.")
        
        for key, value in conditions.items():
            if key not in ("and", "or"):
                raise ValueError("Invalid key in condition.")
            if not isinstance(value, list):
                raise ValueError("Value must be a list.")
            if not isinstance(value, (list, dict)):
                raise ValueError("Value must be a list of lists or dicts.")
            a = [self.validate_conditions(cond, action, default = default) for cond in value] # Assigned to a just to make interpreter happy.
            
    def get_subset(self) -> nx.MultiDiGraph:
        """Resolve the conditions to the actual subset of data.
        
        Args:
            self
            
        Returns:
            A MultiDiGraph of the nodes in the subgraph IDK"""
        # 1. Get the dataset.
        dataset_id = self.get_dataset_id()
        ds = Dataset(id = dataset_id)

        # 2. For each node_id in the address_graph, check if it meets the conditions.
        nodes_for_subgraph = []
        G = ds.get_addresses_graph()
        sorted_nodes = list(nx.topological_sort(G))
        subclasses = ResearchObjectHandler.get_subclasses()
        for idx, node_id in enumerate(sorted_nodes):
            # cls = [cls for cls in subclasses if cls.prefix == node_id[0:2]][0]
            if not self.meets_conditions(node_id, self.conditions, G, subclasses):
                continue
            curr_nodes = [node_id]
            curr_nodes.extend(nx.ancestors(G, node_id))
            nodes_for_subgraph.extend([node_id for node_id in curr_nodes if node_id not in nodes_for_subgraph])
        return G.subgraph(nodes_for_subgraph) # Maintains the relationships between all of the nodes in the subgraph.

    def meets_conditions(self, node_id: str, conditions: dict, G: nx.MultiDiGraph, subclasses: list) -> bool:
        """Check if the node_id meets the conditions.
        
        Args:
            self
            node_id (string): the node ID you want to check the conditions of
            conditions (dictionary): a dict where the keys are IDK and the values are the different conditions IDK
            G (MultiDiGraph): a multi dimentional graph of the nodes surrounding the given conditions IDK
            subclasses (list): subclasses to IDK QUESTION how are you using subclasses
            
        Returns:
            boolean indicating whether or not the node ID meets the given conditions""" 
        if isinstance(conditions, dict):
            if "and" in conditions:
                for cond in conditions["and"]:
                    cls = [cls for cls in subclasses if cls.prefix == cond[0][0:2]][0]
                    if not self.meets_conditions(node_id, cond, G, subclasses):
                        return False
                return True
                # return all([self.meets_conditions(node_id, cond, G) for cond in conditions["and"]])
            if "or" in conditions:
                return any([self.meets_conditions(node_id, cond, G) for cond in conditions["or"]])
                    
        # Check the condition.
        vr_id = conditions[0]
        logic = conditions[1]
        value = conditions[2]
        vr = Variable(id = vr_id)
        vr_name = vr.name
        if not hasattr(node, vr_name):
            anc_nodes = nx.ancestors(G, node_id)
            found_attr = False
            for anc_node in anc_nodes:
                if not hasattr(anc_node, vr_name):
                    continue
                found_attr = True
                break
            if found_attr and self.meets_conditions(anc_node, conditions, G, subclasses):
                return True
            return False
        vr_value = getattr(node_id, vr_name)

        # This is probably shoddy logic, but it'll serve as a first pass to handle None types.
        if logic in plural_logic:
            if logic == "contains" and vr_value is None:
                return False
            elif logic == "not contains" and vr_value is None and value is not None:                
                return True
            elif logic == "in" and value is None:
                return False
            elif logic == "not in" and value is None:
                return True

        # Numeric
        bool_val = False
        if logic == ">" and vr_value > value:
            bool_val = True
        elif logic == "<" and vr_value < value:
            bool_val = True
        elif logic == ">=" and vr_value >= value:
            bool_val = True
        elif logic == "<=" and vr_value <= value:
            bool_val = True
        # Any type
        elif logic in ["==","="] and vr_value == value:
            bool_val = True
        elif logic == "!=" and vr_value != value:
            bool_val = True
        elif logic == "in" and vr_value in value:
            bool_val = True
        elif logic == "not in" and vr_value not in value:
            bool_val = True
        elif logic == "is" and vr_value is value:
            bool_val = True
        elif logic == "is not" and vr_value is not value:
            bool_val = True
        elif logic == "contains" and value in vr_value:
            bool_val = True
        elif logic == "not contains" and not value in vr_value:
            bool_val = True

        return bool_val
            
        

    

    