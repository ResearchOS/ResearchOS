# Logsheet

## Introduction
Most researchers take notes during their experiments. These notes come in many forms, from informal handwritten to very formalized forms or spreadsheets. The `Logsheet` object is designed to capture these notes in a structured way. The `Logsheet` object is a Pipeline Object, and must be the first object in the pipeline because it constructs the Data Objects in the `Dataset`. 

The format of the `Logsheet` spreadsheets will vary widely between labs and disciplines. However, there are broadly two types of columns in a `Logsheet`: `Data Object` columns and `Variable` columns. `Data Object` columns are used to define the `Dataset` `schema`, and `Variable` columns define attributes for each `Data Object`. 

## Setting Attributes

### Logsheet Path
The path to the logsheet file is computer-specific. I recommend that you put the logsheet path in a `paths.py` file and import it into the research_objects/logsheets.py file. By putting the `paths.py` file into the `.gitignore` file (keeping it out of the project's GitHub repository) you can maintain different paths for different computers.

### Headers
The headers attribute is a list of tuples. Each tuple contains, in order: the name of the column (which must match the first row of the column exactly), the data type of the column, the custom `Data Object` class that the column belongs to, and the `Variable` object that the column is associated with. For example:
```python
headers = [
    ("Subject", str, Subject, vr.subject_name), # This is a `Data Object` column
    ("Trial", str, Trial, vr.trial_name), # This is a `Data Object` column
    ("Value", int, Trial, vr.value) # This is a `Variable` column
]
```

### Number of Header Rows
This attribute is an integer that specifies the number of rows at the top of the logsheet that are not part of the data. This is useful for logsheet files that have one or more header rows that describe the contents of the columns.

### Class Column Names
This attribute is a dictionary that maps the names of the `Data Object` columns to the custom `Data Object` classes that they belong to. Note that the keys must match the first row of the column exactly. For example:
```python
class_column_names = {
    "Subject": Subject,
    "Trial": Trial
}
```

::: src.ResearchOS.PipelineObjects.logsheet.Logsheet