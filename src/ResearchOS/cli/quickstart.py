import os, shutil

# NOTE: If the path has ".." that means that the folder name should be inserted between the two dots.

# Create the folders
folders = [
    "docs", # The documentation for this package.
    "src", # The code for this package.
    "tests", # The tests for this package.    
    "src..plot",
    "src..process",
    "src..stats",
    "src..research_objects",
]

files = [
    "README.md",
    "LICENSE.md",
    "pyproject.toml",
    "src..process.tmp.py",
    "src..process.tmp.m",
    "src..research_objects.data_objects.py",
    "src..research_objects.plots.py",
    "src..research_objects.subsets.py",
    "src..research_objects.processes.py",
    "src..research_objects.stats.py",
    "src..research_objects.variables.py",
    "src..__init__.py",
    "src..main.py"
]

def create_folders(root_folder: str = None, folders: list = folders, files: list = files):
    """Creates the default folder structure in the specified directory. If a folder or file already exists, skips it."""
    # Check if this folder exists. If it does not, raise an error.
    if not os.path.exists(root_folder):
        raise FileNotFoundError(f"Folder {root_folder} does not exist.")
    
    # Get the lowest level folder name
    base_folder = os.path.basename(root_folder)
        
    for folder in folders:
        folder_path = replace_dots_with_sep(folder, is_folder=True, named_folder=base_folder)        
        os.makedirs(os.path.join(root_folder, folder_path), exist_ok=True)
    
    cli_root = os.path.dirname(os.path.abspath(__file__))
    quickstart_root = os.path.join(cli_root, "quickstart_files")
    for file in files:
        rel_file_path = replace_dots_with_sep(file, is_folder=False, named_folder=base_folder) # Replace dots with os.sep
        dest_file_path = os.path.join(root_folder, rel_file_path) # Make destination absolute path
        if base_folder in rel_file_path:
            rel_file_path = rel_file_path.replace(base_folder, "project_name")
        src_file_path = os.path.join(quickstart_root, rel_file_path) # Make source absolute path
        if os.path.exists(dest_file_path):
            continue # Don't overwrite an existing file.
        if os.path.exists(src_file_path):
            shutil.copyfile(src_file_path, dest_file_path)
        else:
            with open(dest_file_path, "w") as f:
                f.write("")

def replace_dots_with_sep(path: str, is_folder: bool, named_folder: str = None):
    """Replace all dots in a path with the os.sep except for the last dot because it's for the extension.
    If there are two dots next to each other, insert the named_folder between them."""
    # Insert the named folder if it exists.
    if named_folder is not None:
        path_with_named_folder = path.replace("..", "." + named_folder + ".")
    else:
        path_with_named_folder = path

    # Replace dots with os.sep
    dot_indices = [idx for idx, char in enumerate(path_with_named_folder) if char == "."]
    path_as_list = list(path_with_named_folder)
    if is_folder:
        use_dot_indices = dot_indices
    else:
        use_dot_indices = dot_indices[:-1]
    for idx in use_dot_indices:
        path_as_list[idx] = os.sep
    return ''.join(path_as_list)