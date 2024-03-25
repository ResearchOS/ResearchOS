import pytest, shutil, os
import weakref

import ResearchOS as ros

from ResearchOS.db_initializer import DBInitializer
# from ResearchOS.db_connection_factory import DBConnectionFactory
# from ResearchOS.db_connection import DBConnection
from ResearchOS.sqlite_pool import SQLiteConnectionPool
from ResearchOS.config import Config
from ResearchOS.research_object_handler import ResearchObjectHandler

# Function scoped
@pytest.fixture(scope="function")
def temp_db_file(tmp_path):
    config = Config()
    db_file = str(tmp_path / "test.db")
    config.db_file = db_file
    print(db_file)
    return db_file
  
@pytest.fixture(scope="function")
def db_init(temp_db_file):
    return DBInitializer(temp_db_file)  
            
@pytest.fixture(scope="function")
def db_connection(temp_db_file, db_init):
    ResearchObjectHandler.instances = weakref.WeakValueDictionary() # Keep track of all instances of all research objects.
    ResearchObjectHandler.counts = {} # Keep track of the number of instances of each ID.
    pool = SQLiteConnectionPool()
    return pool

@pytest.fixture(scope="session")
def temp_logsheet_file(tmp_path_factory):
    logsheet_path = str(tmp_path_factory.mktemp("test").joinpath("logsheet.csv"))
    shutil.copy("Spr23TWW_OA_AllSubjects_032323.csv", logsheet_path)
    return logsheet_path

# Dataset
@pytest.fixture(scope="function")
def addresses():
    addresses = [
        ["DS1", "SJ1"],
        ["DS1", "SJ2"],
        ["SJ1", "TR1"],
        ["SJ1", "TR2"],
        ["SJ2", "TR1"],
        ["SJ2", "TR2"]
    ]
    for address_edge in addresses:
        for address in address_edge:
            cls = ResearchObjectHandler._prefix_to_class(address[0:2])
            cls(id = address)
    return addresses

@pytest.fixture(scope="function")
def schema():
    schema = [
        [ros.Dataset, ros.Subject],
        [ros.Subject, ros.Trial]
    ]
    return schema

# Logsheet
@pytest.fixture(scope="function")
def logsheet_headers(db_connection):
    incomplete_headers = [
        ("Date", str, ros.Subject),
        ("Subject_Codename", str, ros.Subject),
        ("Cohort", str, ros.Subject),
        ("Age", int, ros.Subject),
        ("Gender", str, ros.Subject),
        ("FPs_Used", str, ros.Subject),
        ("Visit_Number", int, ros.Subject),
        ("Trial_Name_Number", str, ros.Trial),
        ("Trial_Type_Task", str, ros.Trial),
        ("Side_Of_Interest", str, ros.Trial),
        ("Perfect_Trial", int, ros.Trial),
        ("Subject_Comments", str, ros.Trial),
        ("Researcher_Comments", str, ros.Trial),
        ("Motive_Initial_Frame", int, ros.Trial),
        ("Motive_Final_Frame", int, ros.Trial)
    ]
    headers = []
    for i in range(0, 15):
        vr = ros.Variable(id = f"VR{i}", name = incomplete_headers[i][0])
        headers.append((incomplete_headers[i][0], incomplete_headers[i][1], incomplete_headers[i][2], vr.id))
    return headers

if __name__ == "__main__":
    # pytest.main(["-v", "-s", "tests/"])
    pytest.main(["-v", "tests/"])
