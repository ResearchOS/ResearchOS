# Dataset

Inherits from [DataObject](data_object.md).

## Introduction
`Dataset` is the only built-in Data Object, because all projects will have data contained within a Dataset. Dataset has two attributes that must be defined: `dataset_path` and `schema`. There is also one optional attribute `file_schema`.

## Dataset Path
This is the path to where the dataset is stored in the file system. For example, if the dataset is stored in a folder inside the project folder, the `dataset_path` can be specified as a relative path, e.g. `folder_name`. If it is stored in another folder outside of the project folder, then the `dataset_path` should be specified as an absolute path, e.g. `/path/to/folder`.

## Schema
This defines how the `Dataset` is structured: which Data Objects are in this Dataset, and the hierarchical relationships between them. The `schema` is defined as an "edge list", which is a list of lists. Each sublist contains two elements: the parent Data Object and the child Data Object, always starting with the `Dataset` class. For example, if the `Dataset` contains `Subject` and `Trial` Data Objects, and each `Subject` has multiple `Trials`, the `schema` would be defined as 
```python
import ResearchOS as ros
from research_objects.data_objects import Subject, Trial
schema = [
    [ros.Dataset, Subject],
    [Subject, Trial]
]
```
In this case the `Dataset` is the parent of `Subject`, and `Subject` is the parent of `Trial`. `Subject` and `Trial` need to be [custom defined as Data Objects](defining_data_objects.md).
## File Schema
Sometimes, the dataset is structured in the file system in the exact same way as it is specified in the schema. In this case, the `file_schema` attribute does not need to be manually entered because it is filled in by the `schema` attribute. In our example `schema` of `Subject` Data Objects which each have multiple `Trial` Data Objects, we may have a directory structure like this containing our data:
```txt
dataset_folder
│-- Subject1/
│   │-- Trial1.ext
│   │-- Trial2.ext
│-- Subject2/
│   │-- Trial1.ext
│   │-- Trial2.ext
```

However, for various reasons, sometimes the file system structure is different from the `schema`. In this case, the `file_schema` attribute can be used to specify the file system structure differently than the `Dataset` `schema`. For example, if my file structure were the same as above, but my `schema` consisted of a `Subject` Data Object which had multiple `Task` Data Objects, and each `Task` contained multiple `Trial` Data Objects, the schema would be defined as
```python
import ResearchOS as ros
from research_objects.data_objects import Subject, Task, Trial
schema = [
    [ros.Dataset, Subject],
    [Subject, Task],
    [Task, Trial]
]
```
Because file system structure may still look like the above folder structure, the `file_schema` in this case would be defined as
```python
import ResearchOS as ros
from research_objects.data_objects import Subject, Trial
file_schema = [
    [ros.Dataset, Subject],
    [Subject, Trial]
]
```


::: src.ResearchOS.DataObjects.dataset.Dataset