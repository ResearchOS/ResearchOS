from typing import TYPE_CHECKING

from networkx import MultiDiGraph

if TYPE_CHECKING:
    from ResearchOS.research_object import ResearchObject

from ResearchOS.Digraph.pipeline_digraph import PipelineDiGraph
from ResearchOS.Digraph.data_digraph import DataDiGraph 
from ResearchOS.action import Action
from ResearchOS.sql.sql_runner import sql_order_result


class ResearchObjectDigraph(MultiDiGraph):
    """Research Object Digraph."""

    def __init__(self, 
                 pipeline: bool = True, 
                 data: bool = False,
                 action: Action = None,
                 is_super: bool = False):
        """Arguments:
            pipeline: If True, include Pipeline Objects in the DiGraph.
            data: If True, include Data Objects in the DiGraph.
            parent_node_id: If not None, only include the objects that are target objects of the specified node.
            
            Bridges between Data & Pipeline Graphs are with Project & Dataset objects, and also between DataObject & Process objects, with Variables as edge ID's."""             
        # 1. Initialize the digraph.
        super().__init__() # So that this object is properly initialized as a MultiDiGraph.
        self.pipeline = pipeline
        self.data = data
        if not action:
            action = Action(name = "Construct DiGraph")
        is_super = True
        if pipeline:
            pipeline_digraph = PipelineDiGraph(action)
            self.add_nodes_from(pipeline_digraph.nodes(data=True))
            self.add_edges_from(pipeline_digraph.edges(data=True))
            del pipeline_digraph
        if data:
            data_digraph = DataDiGraph(is_super, action)
            self.add_nodes_from(data_digraph.nodes(data=True))
            self.add_edges_from(data_digraph.edges(data=True))
            del data_digraph

        if not (pipeline and data):
            return
        
        # Add the edges between the Data & Pipeline graphs.
        self.add_bridge_edges()

    def load(self, ro_id: str) -> "ResearchObject":        
        """Loads that object from the database."""
        from ResearchOS.research_object_handler import ResearchObjectHandler
        from ResearchOS.variable import Variable
        # 1. Check that the key is one of the nodes in the digraph.
        is_vr = ro_id.startswith(Variable.prefix)
        if not is_vr and ro_id not in self.nodes:
            ValueError("Key is not a node in the digraph!")

        if is_vr:
            vr_edges = [(source, target, edge_id) for source, target, edge_id, data in self.edges(keys=True, data=True) if data["edge_id"] == ro_id]
            if ro_id not in [vr_edge[2] for vr_edge in vr_edges]:
                ValueError("Variable ID is not an edge in the digraph!")
            return Variable(id = ro_id)

        # 2. Load it from the database.
        cls = ResearchObjectHandler._prefix_to_class(ro_id[:2])
        return cls(id = ro_id)
    
    def add_bridge_edges(self, action: Action) -> None:
        """Query the database for the bridging edges, and add them to the DiGraph from an edge list.
        """
        from ResearchOS.PipelineObjects.pipeline_object import PipelineObject
        pipeline_classes = PipelineObject.__subclasses__()
        pipeline_prefixes = [cls.prefix for cls in pipeline_classes]

        cursor = action.conn.cursor()

        # Source object ID's & their edge ID's. Source not target because source objects compute on the output VR's for each data object.
        # Dict, where the keys are the source object ID's (most likely PR's), and the values are lists of the edge ID's (most likely VR's).
        pipeline_source_obj_edge_ids = {}
        for edge_list in self.edges:
            if edge_list[1][:2] not in pipeline_prefixes:
                continue
            source_obj_id = self.edges[edge_list][1]
            edge_id = self.edges[edge_list][1]["edge_id"]
            if not pipeline_source_obj_edge_ids.get(source_obj_id):
                pipeline_source_obj_edge_ids[source_obj_id] = [edge_id]
            else:
                pipeline_source_obj_edge_ids[source_obj_id].append(edge_id)

        # Add the "edge_ids" (VR's) from Process objects that are not used as inputs anywhere.
        sqlquery_raw = "SELECT pr_id, vr_id FROM data_values WHERE schema_id = ?"
        sqlquery = sql_order_result(action, sqlquery_raw, ["pr_id", "vr_id"], user = True, computer = False)
        result = cursor.execute(sqlquery, (self.schema_id,)).fetchall()
        for row in result:
            pipeline_source_obj_edge_ids[row[0]].append(row[1])

        bridge_edges = []
        for edge_ids in pipeline_source_obj_edge_ids.values():
            # Get the Data Objects that are connected to the PR because they both have an edge with the same VR ID.
            sqlquery_raw = "SELECT dataobject_id FROM vr_dataobjects WHERE vr_id IN ({}) AND is_active = 1".format(", ".join(["?" for _ in edge_ids]))
            params = tuple(edge_ids)
            sqlquery = sql_order_result(action, sqlquery_raw, params, ["dataobject_id"], user = True, computer = False)
            cursor = action.conn.cursor()
            result = cursor.execute(sqlquery, params).fetchall()

            for row in result:
                data_obj_id = row[0]
                for edge_id in edge_ids:
                    bridge_edges.append((pipeline_target_obj_id, data_obj_id, edge_id))

        for bridge_edge in bridge_edges:
            self.add_edge(bridge_edge[0], bridge_edge[1], edge_id = bridge_edge[2])