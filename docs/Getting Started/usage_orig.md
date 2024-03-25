# Usage
## Example 1
Let's use ResearchOS to create a simple one step pipeline that reads a single number from a text file, squares it, and stores that value.

First, after creating a new project directory and activating a virtual environment in that directory, install ResearchOS:
```bash
pip install researchos
```

Next, in the command line, run the following command:
```bash
python -m researchos quick-start
```

This will perform the following actions:

1. Create a new directory called 'researchos_db' in the current directory.

2. Create a .db file in the 'researchos_db' directory with the proper schema.

3. Create a new [Project](../Research%20Objects/Pipeline%20Objects/project.md) object in the .db file, and sets it to be the current [Project](../Research%20Objects/Pipeline%20Objects/project.md). 

Then, create a file called `example1.py` with the following contents:
```python
from researchos.pipeline_objects.project import Project
```

This will create a new project.