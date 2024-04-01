import pytest
from copy import deepcopy

import ResearchOS as ros

classes_and_ids = [
    (ros.Process, "PR1"),
    (ros.Subset, "SS1"),
    (ros.Logsheet, "LG1"),
    (ros.Dataset, "DS1"),
    (ros.Variable, "VR1")    
]

classes_and_ids_no_vr = deepcopy(classes_and_ids)
classes_and_ids_no_vr.remove((ros.Variable, "VR1"))

@pytest.mark.parametrize("cls,id", classes_and_ids)
def test_create_new_ro_with_position_args(cls, id):
    """No positional arguments are allowed. Throws an error if any are provided."""
    try:
        ro = cls(id)
    except TypeError as e:
        assert str(e) == "ResearchObject.__new__() takes 1 positional argument but 2 were given"

@pytest.mark.parametrize("cls,id", classes_and_ids)
def test_create_new_ro_with_no_args(cls, id):
    """Required to have at least one kwarg. Throws an error if none are provided."""
    try:
        ro = cls()
    except ValueError as e:
        assert str(e) == "id is required as a kwarg"

@pytest.mark.parametrize("cls,id", classes_and_ids)
def test_create_new_ro_with_other_kwargs_not_id(cls, id):
    """Required to have id as a kwarg. Throws an error if not provided."""
    try:
        ro = cls(other_kwarg = id)
    except ValueError as e:
        assert str(e) == "id is required as a kwarg"

@pytest.mark.parametrize("cls,id", classes_and_ids_no_vr)
def test_missing_vr_create_new_ro_with_id_kwarg_and_custom_kwargs_attrs(cls, id, db_connection):
    """Attempt to create a new Research Object with the id kwarg and other kwargs.
    Fails because there is no VR with the name "other_kwarg"."""
    try:
        ro = cls(id = id, not_a_real_name = "test")
        assert False
    except ValueError as e:
        assert str(e) == "No unassociated VR with that name exists." 

@pytest.mark.parametrize("cls,id", classes_and_ids_no_vr)
def test_happy_id_kwarg_only_create_new_ro(cls, id, db_connection):
    """Create a new Research Object with only the id kwarg."""
    ro = cls(id = id) # VR requires a name.
    # Check the object's common attributes.
    assert ro.id == id

    # Check the contents of the SQL tables.       

@pytest.mark.parametrize("cls,id", classes_and_ids_no_vr)
def test_missing_dataset_create_new_ro_with_id_kwarg_and_custom_kwargs_vars(cls, id, db_connection):
    """Create a new Research Object with the id kwarg and other kwargs."""
    vr = ros.Variable(id = "VR1", name = "test_vr")
    try:
        ro = cls(id = id, test_vr = "test")
    except ValueError as e:
        assert str(e) == "Need to create a dataset and set up its schema first."

    # Check the contents of the SQL tables.

@pytest.mark.parametrize("cls,id", classes_and_ids_no_vr)
def test_happy_with_zz_id_kwarg_and_custom_kwargs_vars_create_new_ro(cls, id, schema, db_connection):
    """Create a new Research Object with the id kwarg and other kwargs."""
    ds = ros.Dataset(id = "DS2")
    ds.schema = schema
    vr = ros.Variable(id = "VR1", name = "test_vr")
    ro = cls(id = id, test_vr = "test")
    # Check the object's common attributes.
    assert ro.id == id
    assert vr.name == "test_vr"
    assert ro.prefix == cls.prefix
    assert ro.__dict__["test_vr"] == vr
    assert ro.test_vr == "test"
    a = ro.test_vr
    assert a == "test"
    assert getattr(ro,"test_vr") == "test"

project_builtin_args = [
    (ros.Project, "PJ1", "AN1", "DS1")
]

@pytest.mark.parametrize("cls,id,current_analysis_id,current_dataset_id", project_builtin_args)
def test_create_new_ro_with_id_kwarg_and_other_builtin_kwargs(cls, id, current_analysis_id, current_dataset_id, db_connection):
    """Create a new Research Object with the id kwarg and other builtin kwargs."""
    ro = cls(id = id, current_analysis_id = current_analysis_id, current_dataset_id = current_dataset_id)
    # Check the object's common attributes.
    assert ro.id == id
    assert ro.current_analysis_id == current_analysis_id
    assert ro.current_dataset_id == current_dataset_id

    # Check the contents of the SQL tables.
        
if __name__=="__main__":
    pass