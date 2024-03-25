## Recommended Folder Structure
```plaintext
project_folder/
│-- research_objects/
│   │-- my_data_objects.py
```
Data Objects can be defined by the user in the project folder. While the exact method is flexible as long as the user subclasses ResearchOS.data_objects.DataObject, I recommend to create a `research_objects` folder in the project folder and then create a `my_data_objects.py` file within that to define each Data Object. For each Data Object subclass, define a class that inherits from `DataObject`. For example, the following code defines a `Subject` and `Trial` Data Object:

```python
from ResearchOS.DataObjects.data_object import DataObject

class Subject(DataObject):

    prefix: str = "SJ" # Must be unique within the project.

class Trial(DataObject):

    prefix: str = "TR" # Must be unique within the project.
```
All of the above code must be present to define a custom Data Object. The class name and the two letter prefix should be changed to suit your needs. The `prefix` attribute is a two letter prefix that is used to generate the Data Object's ID.