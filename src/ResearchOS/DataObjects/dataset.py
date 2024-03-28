from typing import Any
import json, copy, os

import networkx as nx

from ResearchOS.DataObjects.data_object import DataObject
from ResearchOS.action import Action
from ResearchOS.research_object_handler import ResearchObjectHandler
from ResearchOS.idcreator import IDCreator
from ResearchOS.sqlite_pool import SQLiteConnectionPool

all_default_attrs = {}
all_default_attrs["schema"] = [] # Edge list of DataObjects
all_default_attrs["dataset_path"] = None # str
all_default_attrs["addresses"] = [] # Dict of empty dicts, where each key is the ID of the object and the value is a dict with the subclasses' ID's.
all_default_attrs["file_schema"] = [] # str

computer_specific_attr_names = ["dataset_path"]

class Dataset(DataObject):
    """A dataset is one set of data.
    Class-specific Attributes:
    1. data path: The root folder location of the dataset.
    2. data schema: The schema of the dataset (specified as a list of classes)"""

    prefix: str = "DS"

    def __init__(self, schema: list = all_default_attrs["schema"], 
                 dataset_path: str = all_default_attrs["dataset_path"], 
                 addresses: list = all_default_attrs["addresses"], 
                 file_schema: list = all_default_attrs["file_schema"],
                 **kwargs):                 
        """Create a new dataset."""
        if self._initialized:
            return
        self.schema = schema
        self.dataset_path = dataset_path
        self.addresses = addresses
        self.file_schema = file_schema
        super().__init__(**kwargs)
    
    ### Schema Methods
        
    def validate_schema(self, schema: list, action: Action, default: Any) -> None:
        """Validate that the data schema follows the proper format.
        Must be a dict of dicts, where all keys are Python types matching a DataObject subclass, and the lowest levels are empty.
        
        Args:
            self
            schema (list) : dict of dicts, all keys are Python types matching a DataObject subclass, and the lowest levels are empty
        Returns:
            None
        Raises:
            ValueError: Incorrect schema type"""
        from ResearchOS.research_object import ResearchObject
        if schema == default:
            return
        subclasses = ResearchObject.__subclasses__()
        dataobj_subclasses = DataObject.__subclasses__()
        vr = [x for x in subclasses if hasattr(x,"prefix") and x.prefix == "VR"][0]                
            
        graph = nx.MultiDiGraph()
        try:
            graph.add_edges_from(schema)
        except nx.NetworkXError:
            raise ValueError("The schema must be provided as an edge list!")
        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("The schema must be a directed acyclic graph!")
        
        non_subclass = [node for node in graph if node not in dataobj_subclasses]
        if non_subclass:
            raise ValueError("The schema must only include DataObject subclasses!")
        
        if Dataset not in graph:
            raise ValueError("The schema must include the Dataset class as a source node!")
        
        if vr in graph:
            raise ValueError("The schema must not include the Variable class as a target node!")
        
        if self.file_schema == all_default_attrs["file_schema"]:
            self.__setattr__("file_schema", schema, action)
        
        # nodes_with_no_targets = [node for node, out_degree in graph.out_degree() if out_degree == 0]
        # nodes_with_a_source = [node for node, in_degree in graph.in_degree() if in_degree > 0]
        # if graph[Dataset] in nodes_with_no_targets or graph[Dataset] in nodes_with_a_source:
        #     raise ValueError("The schema must include the Dataset class as a source node and not a target node!")
    
    def to_json_schema(self, schema: list, action: Action) -> str:
        """Convert the schema to a json string."""
        # 1. Convert the list of types to a list of str.
        str_schema = []
        for sch in schema:
            classes = []
            for cls in sch:
                classes.append(cls.prefix)
            str_schema.append(classes)
        # 2. Convert the list of str to a json string.
        json_schema = json.dumps(str_schema)
        return json_schema
    
    def from_json_schema(self, json_schema: str, action: Action) -> list:
        """Convert the schema from a json string to a list of DataObjects."""
        # 3. Convert the json string to a list of types.
        str_schema = json.loads(json_schema)
        schema = []
        for sch in str_schema:
            for idx, prefix in enumerate(sch):
                sch[idx] = ResearchObjectHandler._prefix_to_class(prefix)
            schema.append(sch)  
        return schema

    ### Dataset path methods

    def validate_dataset_path(self, path: str, action: Action, default: Any) -> None:
        """Validate the dataset path.
        
        Args:
            self
            path (string): your dataset path
        Returns:
            None
        Raises:
            ValueError: given path does not exist"""        
        if path == default:
            return
        if not os.path.exists(path):
            raise ValueError("Specified path is not a path or does not currently exist!")
        
    # def load_dataset_path(self, action: Action) -> str:
    #     """Load the dataset path from the database in a computer-specific way."""
    #     return ResearchObjectHandler.get_user_computer_path(self, "dataset_path", action)
    
    ### File Schema Methods

    def validate_file_schema(self, file_schema: list, action: Action, default: Any) -> None:
        """Validate that the file schema follows the proper format.
        Must be a list of DataObjects.
        
        Args:
            self
            file_schema (list) : list of strings
        Returns:
            None
        Raises:
            ValueError: Incorrect file schema type"""
        if file_schema == default:
            return
        if not isinstance(file_schema, list):
            raise ValueError("The file schema must be a list!")
        subclasses = DataObject.__subclasses__()
        if not all([sch in subclasses for sch in file_schema]):
            raise ValueError("The file schema must be a list of DataObject Types!")
        schema_graph = nx.MultiDiGraph()
        schema_graph.add_edges_from(self.schema)
        if len(schema_graph.nodes()) > 0:
            if not all([curr_type in schema_graph.nodes()]):
                raise ValueError("The file schema must consist only of types found within the schema!")
            
    def to_json_file_schema(self, file_schema: list, action: Action) -> str:
        """Convert the file schema to a json string."""
        return json.dumps([file_schema.prefix for file_schema in file_schema])
    
    def from_json_file_schema(self, json_file_schema: str, action: Action) -> list:
        """Convert the file schema from a json string to a list of DataObjects."""
        prefix_file_schema = json.loads(json_file_schema)
        subclasses = DataObject.__subclasses__()
        return [cls for cls in subclasses for prefix in prefix_file_schema if cls.prefix == prefix]
        
    ### Address Methods

    def validate_addresses(self, addresses: list, action: Action, default: Any) -> None:
        """Validate that the addresses are in the correct format.
        
        Args:
            self
            addresses (list) : list of addresses IDK
        Returns:
            None
        Raises:
            ValueError: invalid address provided"""
        if addresses == default:
            return False # Used by the Process.run() method to ascertain whether the addresses have been properly instantiated or not.
        self.validate_schema(self.schema, action, None)   

        try:
            graph = nx.MultiDiGraph()
            graph.add_edges_from(addresses)
        except nx.NetworkXError:
            raise ValueError("The addresses must be provided as an edge list!")
        
        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("The addresses must be a directed acyclic graph!")
        
        # non_ro_id = [node for node in graph if not IDCreator(action.conn).is_ro_id(node)]
        # if non_ro_id:
        #     raise ValueError("The addresses must only include ResearchObject ID's!")
                
        if not graph[self.id]:
            raise ValueError("The addresses must include the dataset ID!")
        
        vrs = [node for node in graph if node.startswith("VR")]
        if vrs:
            raise ValueError("The addresses must not include Variable ID's!")
        
        # schema = self.schema
        # schema_graph = nx.MultiDiGraph()
        # schema_graph.add_edges_from(schema)
        # for address_edge in addresses:
        #     cls0 = ResearchObjectHandler._prefix_to_class(address_edge[0])
        #     cls1 = ResearchObjectHandler._prefix_to_class(address_edge[1])
        #     if cls0 not in schema_graph.predecessors(cls1) or cls1 not in schema_graph.successors(cls0):
        #         raise ValueError("The addresses must match the schema!")

    def save_addresses(self, addresses: list, action: Action) -> list:
        """Save the addresses to the data_addresses table in the database.
        Args:
            self
            addresses (list) : list of addresses IDK
            action (Action) : IDK
        Returns:
            None"""                
        for address_names in addresses:
            params = (address_names[0], address_names[1], action.id_num)
            action.add_sql_query(self.id, "addresses_insert", params, group_name = "robj_complex_attr_insert")    

    def load_addresses(self, action: Action) -> list:
        """Load the addresses from the database."""

        # 2. Get the addresses.
        sqlquery = f"SELECT target_object_id, source_object_id FROM data_addresses"
        addresses = action.conn.execute(sqlquery).fetchall()

        # 3. Convert the addresses to a list of lists (from a list of tuples).
        addresses = [list(address) for address in addresses]

        return addresses

    def get_addresses_graph(self, objs: bool = False, action: Action = None) -> nx.MultiDiGraph:
        """Convert the addresses edge list to a MultiDiGraph.
        Args:
            self
            addresses (list) : list of addresses
        Returns:
            nx.MultiDiGraph of addresses"""
        addresses = self.addresses
        G = nx.MultiDiGraph()        
        G.add_edges_from(addresses)
        return G
    
if __name__=="__main__":
    pass