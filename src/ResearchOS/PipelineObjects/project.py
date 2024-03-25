from typing import Any
import os

from ResearchOS.PipelineObjects.pipeline_object import PipelineObject

all_default_attrs = {}
all_default_attrs["current_analysis_id"] = None
all_default_attrs["current_dataset_id"] = None
all_default_attrs["project_path"] = None

computer_specific_attr_names = []

class Project(PipelineObject):
    """A project is a collection of analyses.
    Class-specific Attributes:
    1. current_analysis_id: The ID of the current analysis for this project.
    2. current_dataset_id: The ID of the current dataset for this project.
    3. project path: The root folder location of the project."""

    prefix: str = "PJ"

    ## current_analysis_id
    
    def validate_current_analysis_id(self, id: str, default: Any) -> None:
        """Validate the current analysis ID. If it is not valid, the value is rejected."""
        if id == default:
            return
        if not isinstance(id, str):
            raise ValueError("Specified value is not a string!")
        if not self.is_id(id):
            raise ValueError("Specified value is not an ID!")
        parsed_id = self.parse_id(id)
        if parsed_id[0] != "AN":
            raise ValueError("Specified ID is not an Analysis!")
        if not self.object_exists(id):
            raise ValueError("Analysis does not exist!")
        
    ## current_dataset_id
    
    def validate_current_dataset_id(self, id: str, default: Any) -> None:
        """Validate the current dataset ID. If it is not valid, the value is rejected."""
        if id == default:
            return
        if not self.is_id(id):
            raise ValueError("Specified value is not an ID!")
        parsed_id = self.parse_id(id)
        if parsed_id[0] != "DS":
            raise ValueError("Specified ID is not a Dataset!")
        if not self.object_exists(id):
            raise ValueError("Dataset does not exist!")
        
    ## project_path
        
    def validate_project_path(self, path: str, default: Any) -> None:
        """Validate the project path. If it is not valid, the value is rejected."""
        if path == default:
            return
        # 1. Check that the path exists in the file system.        
        if not isinstance(path, str):
            raise ValueError("Specified path is not a string!")
        if not os.path.exists(path):
            raise ValueError("Specified path is not a path or does not currently exist!")        
    
    
if __name__=="__main__":
    pass