# Dataset
Dataset imports a data type unique to ResearchOS called an **Action**.
An Action is a set of sequal queries that perform multiple commands with one Action object call.
The Actions are identified by **Action IDs** which together form a record of past changes made to the object.
Actions IDs map many changes to one ID.
They are a behind the scenes feature that users only interact with while *undoing* or *redoing* their work. 

Inherits from [DataObject](data_object.md)

::: src.ResearchOS.DataObjects.dataset.Dataset