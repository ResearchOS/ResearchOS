import os
import shutil
from pathlib import Path

import pytest
import toml

from ResearchOS.read_logsheet import get_logsheet_dict
from ResearchOS.constants import RUNNABLE_TYPES, PROCESS_NAME, PLOT_NAME, STATS_NAME, LOGSHEET_NAME
from fixtures.constants import TMP_PACKAGES_PATH
from ResearchOS.validation_classes import RunnableFactory

def test_get_logsheet_dict(tmp_path: Path = TMP_PACKAGES_PATH):

    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)

    shutil.copytree("tests/fixtures/packages", tmp_path)

    package_settings_file = tmp_path / "package1" / "src" / "package_settings.toml"
    with open(package_settings_file, "r") as f:
        package_settings = toml.load(f)

    logsheet_dict_toml = package_settings[LOGSHEET_NAME]
    del package_settings[LOGSHEET_NAME]

    # Remove the logsheet from the package settings file
    with open(package_settings_file, "w") as f:
        toml.dump(package_settings, f)

    package_folder = str(tmp_path / "package1")

    # Get the logsheet dict. Should error because the logsheet is missing.    
    with pytest.raises(ValueError):
        logsheet_dict = get_logsheet_dict(package_folder)

    # Add the logsheet back to the package settings file
    with open(package_settings_file, "w") as f:
        package_settings[LOGSHEET_NAME] = logsheet_dict_toml
        toml.dump(package_settings, f)
    logsheet_dict = get_logsheet_dict(package_folder)

    assert logsheet_dict == logsheet_dict_toml

    logsheet_type = RunnableFactory.create(runnable_type=LOGSHEET_NAME)
    logsheet_dict['outputs'] = [key for key in logsheet_dict['headers'].keys()] # Outputs are needed for validation
    is_valid, err_msg = logsheet_type.validate(logsheet_dict, compilation_only=True) # Validate the logsheet.
    if not is_valid:
        raise ValueError(f"The logsheet TOML file is not valid. {err_msg}")
    logsheet_dict = logsheet_type.standardize(logsheet_dict, compilation_only=True) # Standardize the logsheet.

    shutil.rmtree(tmp_path)

if __name__=="__main__":
    pytest.main(['-v', __file__])