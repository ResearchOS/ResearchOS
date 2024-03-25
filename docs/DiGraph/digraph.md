# DiGraph
## Introduction
The [NetworkX MultiDiGraph (directional graph that can have multiple parallel edges)](https://networkx.org/documentation/stable/reference/classes/multidigraph.html#networkx.MultiDiGraph) is the data structure that organizes the relationships between all of the different research objects. Just like the objects themselves, the Research Object DiGraph models the relationships between all research objects within the database.

The Research Object DiGraph consists of both Data Objects and Pipeline Objects - therefore it can become quite large and cumbersome to work with. For example if there are 10 Trial objects (DataObject) each referencing 10 Variable objects (DataObject & PipelineObject), this can quickly become quite large (100 connections in this small example). Often, it is not necessary to have both DataObjects and PipelineObjects in the same graph. Therefore, Data Object DiGraphs and Pipeline Object DiGraphs can be created separately by using ``data_objects = True`` and ``pipeline_objects = True`` keyword arguments.

Subgraphs can also be created by specifying the top level node. For example, to work with just one project's DiGraph, use the ``source_node = {research_object_id}`` keyword argument in the constructor, where ``{research_object_id}`` is the Project object's ID.

## Note About Adding Objects to the DiGraph
When adding objects to the DiGraph, they must exist *before* being added to the DiGraph! In the future the ability to create objects by adding them to the DiGraph may be added, but for now object creation and addition to the DiGraph are two entirely separate steps.