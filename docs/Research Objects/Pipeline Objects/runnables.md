## Introduction

[Process](process.md), [Plot](plot.md), and [Stats](stats.md) are all runnable Pipeline Objects. This means that they all share very similar attributes and behaviors. After the attributes listed below are all properly specified, these runnable Pipeline Objects all have a `run()` method which executes the code associated with that object, using the specified input and output [Variables](../variable.md).

This page will list the behaviors and attributes that are common to all runnable Pipeline Objects. Check their individual pages for more information on their specific attributes and behaviors.

## General Attributes
### level (Required)
Specify which set of Data Objects this object operates on. For example, a Process that operates on Trials would have `level = Trial`. This is a required attribute. Often, the `level` is the lowest level of Data Object in the `Dataset`'s `schema` attribute. For example, if the `schema` is
```python
# research_objects/dataset.py
import ResearchOS as ros

schema = [
    [ros.Dataset, Subject],
    [Subject, Trial]
]
```
Generally, most of my analysis will probably focus on the `Trial` level.

### input_vrs (Required)
The runnable Pipeline Objects expect `input_vrs` to be a dictionary, where the keys are strings representing the variable's name in the runnable Pipeline object's code to be run, and the value is the variable's value. Most commonly, that looks something like this:
```python
# research_objects/processes.py
import ResearchOS as ros
from research_objects import variables as vr

test_pr = ros.Process(id = "test_pr")
input_vrs = {
    "input_variable_name_in_code1": input_variable_object1,
    "input_variable_name_in_code2": input_variable_object2,
    ...
}
```
where `input_variable_name_in_code` is the name of the variable as it appears in the code associated with this object, and `input_variable_object` is the [Variable](../variable.md) object that represents the data value for that variable.

A helper function `set_input_vrs()` is provided so that you can set the `input_vrs` attribute using keyword arguments. For example:
```python
# research_objects/processes.py
import ResearchOS as ros
from research_objects import variables as vr

test_pr = ros.Process(id = "test_pr")
test_pr.set_input_vrs(input_variable_name_in_code = vr.input_variable_object)
```

This syntax can be used to specify the input Variables that have either dynamic or hard-coded values. However, there are some rare cases that require the inputs to be specified in a different way.

**NOTE**: For keyword arguments to a function, the order of the input_vrs does not matter. But for positional arguments (including all MATLAB functions), the order must match the order of the input arguments.

#### Data Object attributes
Sometimes, the code being run requires an attribute of the Data Object to be passed as an input. For example, if the code being run on a particular `Trial` requires the `Subject` name, or requires the `Task` type of a particular `Trial`. In this case, the `input_vr` dictionary can be specified as follows, using the helper function `set_input_vrs()`:
```python
# research_objects/processes.py
import ResearchOS as ros
from research_objects import variables as vr
from research_objects.my_data_objects import Subject, Trial

test_pr = ros.Process(id = "test_pr", level = Trial)
test_pr.set_input_vr(subject_name = {Subject: "name"})
```
This syntax tells ResearchOS that for each `Trial` object, the `Subject` object associated with that `Trial` should have its `name` attribute passed to the code being run for the `subject_name` input variable.

### vrs_source_pr (Recommended)
This attribute tells the runnable Pipeline Object where to look for the input [Variables](../variable.md) that are specified in the `input_vrs` attribute. The source of the input [Variables](../variable.md) can be either a [Process](../Pipeline%20Objects/process.md) or [Logsheet](../Pipeline%20Objects/logsheet.md) object. This helps to manage the flow of data through the pipeline, especially when a [Variable](../variable.md) is overwritten by one or more runnable Pipeline Objects. If no source_pr is specified for a [Variable](../variable.md), then it is assumed that the [Process](../Pipeline%20Objects/process.md) that most recently outputted that [Variable](../variable.md) is the source of that [Variable](../variable.md). Hard-coded [Variables](../variable.md) will not be included here, because they don't have a "source" in the same way that Variables that are passed from another object do.

Similar to the `input_vrs` this attribute is specified as a dictionary, where the keys are the names of the input [Variables](../variable.md) in the code and the values are the [Process](../Pipeline%20Objects/process.md) or [Logsheet](../Pipeline%20Objects/logsheet.md) object that is the source of that [Variable](../variable.md). For example:
```python
# research_objects/processes.py
import ResearchOS as ros
from research_objects import variables as vr
from research_objects.logsheets import logsheet

source_pr1 = ros.Process(id = "PR1")
source_pr2 = ros.Process(id = "PR2")

test_pr = ros.Process(id = "PR3")
vrs_source_pr = {
    "input_variable_name_in_code1": source_pr1,
    "input_variable_name_in_code2": source_pr2,
    "input_variable_name_in_code3": logsheet,
    ...
}
test_pr.vrs_source_pr = vrs_source_pr
```
There is also a helper function `set_vrs_source_pr()` that can be used to set the `vrs_source_pr` attribute using keyword arguments. For example:
```python
# research_objects/processes.py
import ResearchOS as ros
from research_objects import variables as vr
from research_objects.logsheets import logsheet

source_pr1 = ros.Process(id = "PR1")
source_pr2 = ros.Process(id = "PR2")

test_pr = ros.Process(id = "PR3")
test_pr.set_vrs_source_pr(input_variable_name_in_code1 = source_pr1, input_variable_name_in_code2 = source_pr2, input_variable_name_in_code3 = logsheet, ...)
```

There are a few instances where this syntax needs to be modified to accommodate different workflows.
#### Multiple sources
If a [Variable](../variable.md) is derived from multiple sources, then the `vrs_source_pr` attribute should be a list of the sources. For example, a `Subject`'s mass could be calculated from a `Process` or it could be listed in the `Logsheet`:
```python
# research_objects/processes.py
import ResearchOS as ros
from research_objects import variables as vr
from research_objects.logsheets import logsheet

# outputs the mass of the subject
compute_subject_mass = ros.Process(id = "PR1")

# a Process that uses the mass of the subject. If for a Data Object instance, the mass is not calculated, then it will use the mass from the logsheet
uses_subject_mass = ros.Process(id = "PR2")
uses_subject_mass.set_input_vrs(subject_mass = vr.mass)
uses_subject_mass.set_vrs_source_pr(subject_mass = [compute_subject_mass, logsheet])
```

### output_vrs (PR, ST Required)
Similar to input_vrs, the _output_vrs are specified as a dictionary. The keys are the names of the output [Variables](../variable.md) in the code and the values are the [Variable](../variable.md) objects that represent the data value for that variable. For example:
```python
# research_objects/processes.py
import ResearchOS as ros
from research_objects import variables as vr

test_pr = ros.Process(id = "PR0")
output_vrs = {
    "output_variable_name_in_code1": vr.output_variable_object1,
    "output_variable_name_in_code2": vr.output_variable_object2,
    ...
}
test_pr.output_vrs = output_vrs
```

Using the helper function `set_output_vrs()` is also an option. For example:
```python
# research_objects/processes.py
import ResearchOS as ros
from research_objects import variables as vr

test_pr = ros.Process(id = "PR0")
test_pr.set_output_vrs(output_variable_name_in_code1 = vr.output_variable_object1, output_variable_name_in_code2 = vr.output_variable_object2, ...)
```

### lookup_vrs (Optional)
For some workflows, it is necessary to look up the value of a [Variable](../variable.md) from a different Data Object. For example, if a `Trial` object needs to retrieve some calibrated value from a calibration `Trial`, then the `lookup_vrs` attribute can be used. This attribute is specified as a dictionary, where the keys are the names of the [Variables](../variable.md) in the code and the values are dictionaries themselves. The inner dictionaries have the [Variable](../variable.md) object as the key, and a list of strings as the value. The strings are the variable names in code that are being looked up in another Data Object. In the below example, the `lookup_input_variable_name_in_code` is the name of the [Variable](../variable.md) that specifies which Data Object to reference, and `other_input_vr` is the name of the [Variable](../variable.md) to retrieve from that Data Object.
```python
# research_objects/processes.py
import ResearchOS as ros
from research_objects import variables as vr

test_pr = ros.Process(id = "PR0")
test_pr.set_input_vrs(lookup_input_variable_name_in_code = vr.input_variable_object, other_input_vr = vr.other_input_variable_object)
lookup_vrs = {
    "lookup_input_variable_name_in_code": {vr.lookup_variable_object: ["other_input_vr", ...]}
}
```

### batch (Optional)
Specify whether this object should be run in batch mode. The default is `None`, indicating that only one Data Object's values are provided at a time to the runnable Pipeline Object, as would be expected. If `batch = []`, then all Data Objects at the specified level are provided to the runnable Pipeline Object at once. If `batch` is a list of Data Object classes, then all Data Objects that are of the specified classes are provided to the runnable Pipeline Object at once.

For example, if the [Dataset](../Data%20Objects/dataset.md) `schema` is
```python
# research_objects/dataset.py
import ResearchOS as ros
from research_objects.my_data_objects import Subject, Trial
schema = [
    [ros.Dataset, Subject],
    [Subject, Trial]
]
```
and for a [Process](../Pipeline%20Objects/process.md) object the `batch` is:
```python
# research_objects/processes.py
import ResearchOS as ros
from research_objects.my_data_objects import Subject, Trial
test_pr = ros.Process(id = "test_pr")
test_pr.batch = [Subject, Trial]
```
Then all `Trials` for one `Subject` are provided to the runnable Pipeline Object at once in the form of a dictionary with each `Trial`'s `id` as the key and that `Variable`'s value for that `Trial` object as the value.

## Python-specific Attributes
Be sure that `is_matlab` is set to `False` for this object to run Python code.
### method (Required)
A `Callable` attribute that is `None` by default. This is the handle to the function that will be called when the `run()` method is executed. This method's code should take the input [Variables](../variable.md) as arguments and return the output [Variables](../variable.md).

Note that when loading this object from the database, the method needs to be in the global namespace. This is because the method is stored as a string in the database and is then loaded from sys.modules when the object is loaded.

## MATLAB-specific Attributes
### is_matlab (Required)
A boolean attribute that is `False` by default. Set this to `True` if the code associated with this object is written in MATLAB. Note that this requires that MATLAB is installed on your system and that the MATLAB Engine API is installed in your Python environment.

### mfolder (Required)
A string attribute that is `None` by default. Set this to the path to the folder containing the MATLAB code associated with this object. This is used to set the MATLAB working directory to the correct location before running the MATLAB code. **It is computer-specific**.

For maximum portability between computers and users, I recommend defining a `paths.py` file in the project folder that contains the path to the folder containing the MATLAB code. You can import this path into the .py file that defines your runnable Pipeline Objects.

```python
# paths.py
mfolder = "path/to/matlab/folder"

# processes.py
from paths import mfolder
import ResearchOS as ros

test_pr = ros.Process(id = "PR0")
test_pr.mfolder = mfolder
```

### mfunc_name (Required)
Specifies the name of the MATLAB function to be run. This is a string attribute that is `None` by default. This is the name of the MATLAB function that will be called when the `run()` method is executed.

