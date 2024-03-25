import networkx as nx

from ResearchOS.action import Action

class DataDiGraph(nx.MultiDiGraph):

    def __init__(self, action: "Action"):
        """Initialize the Data DiGraph."""
        super().__init__()   

        # There could be an option for loading all addresses of the data objects (for smaller datasets) OR just the schema levels (for larger datasets).
        # Advantage of the schema level is drastically reducing the number of edges between DataObject & Variable nodes.
        # Disadvantage is that you lose the granularity of exactly which data objects are connected to which variables.