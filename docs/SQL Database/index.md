# SQLite Database

## Introduction
ResearchOS uses two SQLite databases to store data. The first database is used to store the [Research Objects](../Research%20Objects/research_object.md) that define the structure and maintain the history of your project. The second database is used to store the data itself. These databases are stored in the root of the project folder and are named `researchos.db` and `researchos_data.db`, respectively. Because `researchos_data.db` contains the project's data, and can therefore become quite large, I recommend that it be added to the `.gitignore` file to prevent it from being uploaded to a repository.

## Database Structure
![Database Structure](../Database/Screenshot%202024-03-25%20at%2012.18.25 AM.png)
The `researchos.db` database contains the following tables:

- **research_objects**: The reference list of Research Objects. If the Research Object doesn't exist in this table, then it doesn't exist for the project.

- **actions**: The reference list of Actions that have been performed on this project.

- **users_computers**: The reference list of Users and Computers that have been used in this project. Helps to track attributes such as paths that are specific to each computer.

- **simple_attributes**: The history of attributes with values that are JSON-serializable and did not require a custom `load`/`save` method. 

- **attributes_list**: Maps the ID of an attribute in the `simple_attributes` table to the attribute's name in the Research Object.

- **data_address_schemas**: The schema for the data addresses that are used to store the data in the `researchos_data.db` database.

- **data_addresses**: The edge list of data addresses containing the relationships between all `Data Object` instances.

- **data_values**: Tracks the data hash of each [Variable](../Research%20Objects/variable.md) for each `Data Object` instance, and which [Process](../Research%20Objects/Pipeline%20Objects/process.md) (or [Logsheet](../Research%20Objects/research_object.md)) computed the value.

- **vr_dataobjects**: Tracks which [Data Object](../Research%20Objects/Data%20Objects/data_object.md) instances are associated with each [Variable](../Research%20Objects/variable.md). Does *not* store the data itself.

- **pipelineobjects_graph**: The graph of all [Pipeline Objects](../Research%20Objects/Pipeline%20Objects/pipeline_object.md) in the project. The graph is stored as an edge list, and the [Variables](../Research%20Objects/variable.md) are stored as the "edge_id" property of each edge in the graph.

`researchos_data.db` contains the following tables:

- **data_blob**: The data table that stores the data for the project. The data is stored in a binary format to allow for the storage of pickled data, and the table is indexed by the `data_hash` column.