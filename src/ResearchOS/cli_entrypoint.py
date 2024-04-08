import os, sys
import importlib

import typer
from typer.testing import CliRunner
import toml

from ResearchOS.research_object import ResearchObject
from ResearchOS.research_object_handler import ResearchObjectHandler
from ResearchOS.config import Config
from ResearchOS.cli.quickstart import create_folders
from ResearchOS.db_initializer import DBInitializer
from ResearchOS.action import Action

app = typer.Typer()
# Add the current working directory to the path so that the code can be imported.
sys.path.append(os.getcwd())

@app.command()
def init_project(folder: str = typer.Option(None, help="Folder name"),
               repo: str = typer.Option(None, help="Repository URL to clone code from")
               ):
    """Create a new blank project in the specified folder. If no arguments are provided, creates a new project in the current working directory.
    If a URL is provided, clones the repository specified by the URL."""
    cwd = os.getcwd()
    if folder is None:
        folder = cwd
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except FileNotFoundError:
            raise ValueError(f"Folder {folder} is not a valid folder path.")
    # create_folders(folder, files = ["config.json"]) # This needs to exist before the Config object is created.
    create_folders(folder)
    # If this is a project (because the current working directory and the folder name match) create project-specific folders & files.
    create_folders(folder, folders = ["data", "output", "output/plots", "output/stats", "packages"], files = ["paths.py", ".gitignore", "src/research_objects/dataset.py", "src/research_objects/logsheets.py"])
    config = Config(type="Project")
    user_input = "y"
    print(config.__dict__)
    if os.path.exists(config.db_file) or os.path.exists(config.data_db_file):
        user_input = input("Databases already exist. Do you want to overwrite them? (y/n) ")
    if user_input.lower() == "y":
        db = DBInitializer() # Create the databases.
        print("Databases reset to default state.")
    else:
        print("Databases not modified.")
    if repo:
        pass
    print(f"Project initialized in {folder}")

@app.command()
def init_package(name: str = typer.Argument(help="Package name. This will be the name of the folder.")):
    """Initialize the folder structure to create a package. Must provide the subfolder to create the package in."""
    cwd = os.getcwd()
    packages_folder = os.path.join(cwd, "packages")
    package_folder = os.path.join(packages_folder, name)
    if not os.path.exists(package_folder):
        try:
            os.makedirs(package_folder)
        except FileNotFoundError:
            raise ValueError(f"Folder {package_folder} is not a valid folder path.")
    create_folders(package_folder)
    print(f"Package {name} initialized in {package_folder}")

@app.command()
def config(github_token: str = typer.Option(None, help="GitHub token"),
           db_file: str = typer.Option("researchos.db", help="Database file"),
           data_db_file: str = typer.Option("researchos_data.db", help="Data database file"),
           data_objects_path: str = typer.Option("research_objects.data_objects.py", help="Path to data objects")
        ):
    config = Config()
    if github_token:
        config.github_token = github_token
    if db_file:
        config.db_file = db_file
    if data_db_file:
        config.data_db_file = data_db_file
    if data_objects_path:
        config.data_objects_path = data_objects_path

@app.command()
def dobjs(is_active: int = typer.Option(1, help="1 for active, 0 for inactive, default 1")):
    """List all available data objects."""    
    action = Action(name = "list_dobjs")
    cursor = action.conn.cursor()
    sqlquery = "SELECT path_id, dataobject_id, path FROM paths WHERE is_active = ?"
    params = (is_active,)    
    result = cursor.execute(sqlquery, params).fetchall()      
    max_num_levels = -1
    str_lens = []
    for row in result:
        str_lens_in_row = []
        for col in row:
            curr_len = len(str(col))
            str_lens_in_row.append(curr_len)
            max_num_levels = max(max_num_levels, curr_len)
        str_lens.append(str_lens_in_row)
     
    lens = [-1 for i in range(max_num_levels)]
    for i in range(max_num_levels):
        lens[i] = max([row[i] for row in str_lens if len(row)>=i+1])
    
    print("here")
    lens_str = [f"{{:<{lens[i]}}}" for i in range(max_num_levels)]
    for row in result:
        row = row.append([""]*(max_num_levels-len(row)))
        style_str = "{:<12} {:<15} {:<5} " + lens_str
        print(style_str.format(f"Path ID: {row[0]}", f"DataObject ID: {row[1]}", f"Path: {row[2]}"))

@app.command()
def db_reset():
    """Reset the databases to their default state."""
    # Ask the user for confirmation.
    user_input = input("Are you sure you want to reset the databases to their default (empty) state? All data will be deleted! (y/n) ")
    if user_input.lower() != "y":
        print("Databases not modified.")
        return
    db = DBInitializer()
    print("Databases reset to default state.")

@app.command()
def logsheet_read(path: str = typer.Argument(help="Path to the logsheet research object file. Default is research_objects.logsheets.py", default="research_objects.logsheets")):
    """Run the logsheet."""    
    lgs = importlib.import_module(path)
    # dir() returns names of the attributes of the module. So getattr(module, name) gets the object.
    lg_objs = [getattr(lgs, lg_obj) for lg_obj in dir(lgs) if hasattr(getattr(lgs, lg_obj),"prefix") and getattr(lgs, lg_obj).prefix == "LG"]
    lg_obj = lg_objs[0]
    lg_obj.read_logsheet()

@app.command()
def graph_show(package_or_project_name: str = typer.Argument(default=None, help="Name of the package or project to visualize.")):
    """Show the directed graph of Pipeline Objects within one package or project.
    If no argument is entered, look in the current project's database for the objects.
    If a package name is provided, look in the package's code for the objects."""
    if package_or_project_name is None:
        project_name = os.path.basename(os.getcwd())
        package_or_project_name = os.path.basename(os.getcwd())

@app.command()
def open(ro_type: str = typer.Argument(help="Research object type (e.g. data, logsheet, pipeline)"),
         p: str = typer.Option(None, help="The package name to open the research object from")):
    """Open a research object in the default editor.
    They can come from a few places:
    1. The project: Looks in the root/pyproject.toml file for the research object location.
    2. The package: Looks in root/packages/package_name/pyproject.toml for the research object location. 
    If root/packages/package_name does not exist, searches through the pip installed packages for a package with the name package_name."""
    subclasses = ResearchObjectHandler._get_subclasses()
    name_list = [cls.__name__ for cls in subclasses if cls.__name__.lower() == ro_type.lower()]
    if len(name_list) == 0:        
        name_list = [cls.__name__ for cls in subclasses if cls.prefix.lower() == ro_type.lower()]
    if len(name_list) == 0:
        raise ValueError(f"Research object type {ro_type} not found.")
    ro_type = name_list[0]
    # Get the pyproject.toml file path.
    root_path = os.getcwd()
    root_package_path = os.path.join(root_path, "packages", str(p))
    venv_package_path = os.path.join(os.getcwd(), "venv", "lib", "site-packages", str(p))
    if os.path.exists(os.path.join(root_path, "pyproject.toml")):
        toml_path = os.path.join(root_path, "pyproject.toml")
    elif os.path.exists(os.path.join(root_package_path, "pyproject.toml")):
        toml_path = os.path.join(root_package_path, "pyproject.toml")
    elif os.path.exists(os.path.join(venv_package_path, "pyproject.toml")):
        toml_path = os.path.join(venv_package_path, "pyproject.toml")

    if not os.path.exists(toml_path):
        raise ValueError(f"pyproject.toml file not found in {root_path} or {root_package_path} or {venv_package_path}")
    
    with open(toml_path, "r") as f:
        pyproject = toml.load(f)

    if "tool" not in pyproject:
        raise ValueError("No tool section in pyproject.toml file.")
    
    if "researchos" not in pyproject["tool"]:
        raise ValueError("No researchos section in pyproject.toml file.")
    
    if "paths" not in pyproject["tool"]["researchos"]:
        raise ValueError("No paths section in pyproject.toml file.")
    
    if ro_type not in pyproject["tool"]["researchos"]["paths"]:
        raise ValueError(f"No path for {ro_type} in pyproject.toml file.")

    path = pyproject["tool"]["researchos"]["paths"][ro_type]

    command = ["code", path]

    os.system(" ".join(command))

if __name__ == "__main__":
    # app()
    app(["init-project"])