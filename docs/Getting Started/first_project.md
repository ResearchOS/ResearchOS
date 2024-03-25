# First Project
To familiarize you with the basics of how ResearchOS works, let's create a simple one step pipeline that reads a single number from a [Logsheet](../Research%20Objects/Pipeline%20Objects/logsheet.md), squares it, and stores that value. 

These instructions will begin with the assumption that you have already created a new project directory, activated a virtual environment within that folder, and installed ResearchOS. If you have not done so, please refer to the [Installation](../Getting%20Started/installation.md) section.

Similar to the [Installation](../Getting%20Started/installation.md) section, I will be providing instructions for Visual Studio Code (VS Code), but the process is similar for other programs.

## Step 1: Initialize the database.
1. In VS Code, create a new file called `run_project.py` in your project directory. In that file, type the following:
```python
import researchos as ros

ros.DBInitializer()
```
Run that file and it will create two new files in the project folder: `researchos.db` and `researchos_data.db`. The `researchos.db` file stores all of the information about the structure and history of our project, while the `researchos_data.db` file stores the actual data that we compute.

## Step 2: Create some dummy data.
We'll need to create some dummy data so that our project has something to work with. We need to create a .csv file, which ResearchOS calls a [Logsheet](../Research%20Objects/Pipeline%20Objects/logsheet.md). In a typical project, this file would contain the records of an experiment, but for this example we'll just create a file called `dummy_logsheet.csv` with the following contents:
```csv
"Subject",  "Trial",  "Value"
"Larry",    1,        3
```

The first row is our headers, and the second row contains the value for the one trial we've recorded of our one subject, Larry. We'll use this data later.

## Step 3: Define the Dataset.
Next, we need to define some [Research Objects](../Research Objects/research_object.md) that our pipeline will be built from. In your project folder, create a new folder called `research_objects`. We'll need a few types of research objects, so in this folder we will create a new file for each type. To define our [Dataset](../Research%20Objects//Data%20Objects/dataset.md), create a file called `dataset.py`.

We need to define the attributes of this dataset. The minimum attributes that we need to define are its `schema` and `dataset_path`. We need to define a schema to tell ResearchOS how our data is structured. In this case, we have a [Dataset](../Research%20Objects//Data%20Objects/dataset.md) that contains `Subject` Data Objects, and each `Subject` contains `Trial` Data Objects. These are two examples of custom [Data Objects](../Research%20Objects/Data%20Objects/data_object.md). In order for ResearchOS to cover any branch of science, Data Objects are custom defined each project. To define a `Subject` and `Trial` class, let's create a new folder for our data objects `research_objects/data_objects`. In the `research_objects/data_objects` folder, create a file called `subject.py` with the following contents:
```python
import ResearchOS as ros

class Subject(ros.DataObject):

    prefix: str = "SJ" # Needs to start with "SJ" for "Subject", and be unique within the project.
```

Similarly, create a file called `trial.py` in the `research_objects/data_objects` folder with the following contents:
```python
import ResearchOS as ros

class Trial(ros.DataObject):

    prefix: str = "TR" # Needs to start with "TR" for "Trial", and be unique within the project.
```
Now that the [Data Objects](../Research%20Objects/Data%20Objects/data_object.md) are defined we can define the schema for the Dataset. We'll also define the `dataset_path` now too, which requires that we specify a folder in your project to put the data. Let's call it `data`. Type the following into `research_objects/dataset.py`:
```python
import ResearchOS as ros
from research_objects.data_objects import Subject, Trial

dataset = ros.Dataset(id = "DS1") # Needs to start with "DS" for "Dataset", and be unique within the project.
dataset.schema = [
    [ros.Dataset, Subject],
    [Subject, Trial]
]
dataset.dataset_path = "your_project_folder/data"
```

## Step 4: Define the Variables.
Next, we need to define the [Variables](../Research%20Objects/variable.md) that we'll be using. Create a file called `research_objects/variables.py`. In `research_objects/variable.py`, type the following:
```python
import ResearchOS as ros

subject_name = ros.Variable(id = "VR1") # Needs to start with "VR" for "Variable", and be unique within the project.
trial_name = ros.Variable(id = "VR2")
value = ros.Variable(id = "VR3")
```

## Step 5: Define the Logsheet
To define the [Logsheet](../Research%20Objects/Pipeline%20Objects/logsheet.md) that we created in [Step 2](#step-2-create-some-dummy-data), create a file called `research_objects/logsheet.py`. We need to define the [Logsheet](../Research%20Objects/Pipeline%20Objects/logsheet.md) attributes for the csv file that we created in step 2. The minimum attributes that we need to define are its `path`, `headers`, `num_header_rows`, and `class_column_names`.

In `research_objects/logsheet.py`, type the following:
```python
import ResearchOS as ros

logsheet = ros.Logsheet(id = "LG1") # Needs to start with "LG" for "Logsheet", and be unique within the project.
logsheet.path = "your_project_folder/dummy_logsheet.csv"
logsheet.num_header_rows = 1
logsheet.class_column_names = {
    "Subject": Subject,
    "Trial": Trial
}
logsheet.headers = [
    ("Subject", str, Subject, vr.subject_name),
    ("Trial", int, Trial, vr.trial_name),
    ("Value", int, Trial, vr.value)
]
```

## Step 6: Run the Logsheet.
Now that we have defined our [Research Objects](../Research%20Objects/research_object.md), we can run the Logsheet to initialize the dataset in our database. In `run_project.py`, type the following:
```python
from research_objects import logsheet as lg
from research_objects import dataset as ds

lg.logsheet.read_logsheet()
```
After running this file, you should see a new dataset in your database with the data from the Logsheet.

## Step 7: Define the Process.
We need to define the [Process](../Research%20Objects/Pipeline%20Objects/process.md) that will square the value in our dataset. In `research_objects/processes.py`, type the following:
```python
import ResearchOS as ros
from research_objects import variables as vr
from square_value import square_value

square_value = ros.Process(id = "PR1") # Needs to start with "PR" for "Process", and be unique within the project.
square_value.set_input_vr(number = vr.value)
square_value.set_output_vr(squared = vr.squared_value)
square_value.subset_id = "SS1"
square_value.method = square_value
```
In another file called `square_value.py`, type the following:
```python
def square_value(number: int):
    return number ** 2
```

## Step 8: Create the Subset.
We need to define the [Subset](../Research%20Objects/Pipeline%20Objects/subset.md) to know which subset of our data the Process will operate on. In `research_objects/subset.py`, type the following to define a subset that includes all of the data in our dataset:
```python
import ResearchOS as ros

subset = ros.Subset(id = "SS1") # Needs to start with "SS" for "Subset", and be unique within the project.
subset.conditions = {}
```
## Step 9: Run the Process.
Finally, we will run the Process to square the value in our dataset. In `run_project.py`, type the following:
```python
from research_objects import processes as pr

pr.square_value.run()
```