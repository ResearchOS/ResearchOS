# Variable

## Introduction
Variables are the links between all of the research objects in your project. They represent the data that is collected/computed in your project. Every Variable must have a unique `ID` within the project, and must start with "VR" to indicate that it is a Variable. Because Variables are used so frequently in the project, their definition is very lightweight. The only required attribute is the `ID`, but you can also specify a `name` attribute to give the Variable a more descriptive name.

## Recommended Folder Structure
```plaintext
project_folder/
│-- research_objects/
│   │-- variables.py
```

In the `variables.py` file, Variables can be defined as follows:
```python
import ResearchOS as ros

test_vr1 = ros.Variable(id = "VR1") # ID needs to start with "VR" for "Variable", and be unique within the project.
test_vr2 = ros.Variable(id = "VR2", name = "Test Variable 2") # Can optionally specify a name attribute.
```

## Hard-Coded Variables
Sometimes, a Variable's value is not computed, but is instead hard-coded when a Variable represents a constant value. This could be a scalar value, for example to control how much smoothing to apply to a signal, or a string value to represent a specific condition, or anything else. In this case, the Variable's `hard_coded_value` attribute can be provided in the `variables.py` file. For example:
```python
import ResearchOS as ros

test_vr1 = ros.Variable(id = "VR1", hard_coded_value = 5) # ID needs to start with "VR" for "Variable", and be unique within the project.

test_vr2 = ros.Variable(id = "VR2")
test_vr2.hard_coded_value = "Condition A" # Can also be specified on a separate line, useful for longer hard-coded values.
```

In some cases, the hard-coded value can be rather complex, such as a dictionary or a list. In this case, a common strategy is to create a .json file that contains the hard-coded value, and then load the .json file in the `variables.py` file. 
```python
import ResearchOS as ros
import json

test_vr1 = ros.Variable(id = "VR1", hard_coded_value = json.load(open("path/to/hard_coded_value.json")))
```
### Removing Hard-Coded Value
If a Variable has a hard-coded value but you want to remove it, you can set the `hard_coded_value` attribute to `None`. For example:
```python
import ResearchOS as ros

test_vr1 = ros.Variable(id = "VR1", hard_coded_value = 5) # ID needs to start with "VR" for "Variable", and be unique within the project.
# Later in the code I decided that test_vr1 should not have a hard-coded value.
test_vr1.hard_coded_value = None # Now it does not have a hard-coded value, and is dynamically evaluated instead.
```
::: src.ResearchOS.variable.Variable