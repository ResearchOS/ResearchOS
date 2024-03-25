import networkx as nx
from ResearchOS.action import Action
from ResearchOS.sql.sql_runner import sql_order_result

class PipelineDiGraph(nx.MultiDiGraph):

    def __init__(self, action: Action = None):
        """Initialize the Pipeline DiGraph.
        Be sure to consider the case of a PR object whose output VR's are not used as inputs anywhere?"""
        # 1. Ensure it is a MultiDiGraph.
        super().__init__()

        # 1. Get all Process nodes.
        cursor = action.conn.cursor()
        sqlquery = "SELECT object_id FROM research_objects WHERE object_id LIKE 'PR%'"
        result = cursor.execute(sqlquery).fetchall()
        node_ids = [row[0] for row in result]
        self.add_nodes_from(node_ids)

        # 2. Add the nodes and edges.
        sqlquery_raw = "SELECT source_object_id, target_object_id, edge_id FROM pipelineobjects_graph WHERE is_active = 1"
        sqlquery = sql_order_result(action, sqlquery_raw, ["source_object_id", "target_object_id", "edge_id"], user = True, computer = False)        
        result = cursor.execute(sqlquery).fetchall()

        for row in result:
            self.add_edge(row[0], row[1], edge_id = row[2])


