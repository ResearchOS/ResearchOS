## Introduction
ResearchOS uses a `config.json` file to manage the SQL database. This document will explain the file contents and how to use it.

## File Contents
### db_file
This is the path to the SQLite database file. If the file does not exist, it will be created. By default, it is `researchos.db`.

### data_db_file
This is the path to the SQLite database file for the data. If the file does not exist, it will be created. By default, it is `researchos_data.db`.

### data_objects_path
This is the path to the directory where the data objects are stored. By default, it is `research_objects.data_objects.py`. Note the use of the dot notation. This helps to import the data objects.

## Editing the Config File
Editing the config file can be done either programmatically, or by directly editing the config.json file. To edit the file programmatically, access the properties of the `Config` class.:
```python
import ResearchOS as ros

config = ros.config.Config()
config.db_file = "new_db_file.db"
config.data_db_file = "new_data_db_file.db"
config.data_objects_path = "new_data_objects_path"
```