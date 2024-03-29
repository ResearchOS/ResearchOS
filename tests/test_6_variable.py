import pytest

import ResearchOS as ros

def test_variable_exists(db_connection):
    """Make sure that the variable exists in the database after the variable is first created."""
    vr = ros.Variable(id = "VR1")
    assert isinstance(vr, ros.Variable)
    assert vr.id == "VR1"
    assert vr.name == vr.id
    assert vr.prefix == "VR"

# def test_variable_value(db_connection):
#     """Value cannot be set until the variable is assigned to a DataObject."""
#     vr = ros.Variable(id = "VR1")
#     try:
#         vr.value = 1
#         assert False
#     except Exception as e:                
#         assert True

# def test_variable_value_set(db_connection):
#     """Value can be set after the variable is assigned to a DataObject."""
#     vr = ros.Variable(id = "VR1")
#     ds = ros.Dataset(id = "DS1", test_vr = vr)
#     ds.test_vr = 4
#     assert vr.test_vr == 4
#     assert vr.test_vr.__class__ == ros.Variable