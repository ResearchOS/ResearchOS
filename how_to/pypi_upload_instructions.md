From here: https://packaging.python.org/en/latest/tutorials/packaging-projects/
# Build the package.
## NOTE: In pyproject.toml, the version number must be updated (unique) before running the following commands.
1. python3 -m pip install --upgrade build
2. python3 -m build
3. python3 -m pip install --upgrade twine

All actions are performed in the command line from the root directory of the project.

# Test PyPI
## Upload
### NOTE: Remove all other files from the dist folder before running this command.
1. python3 -m twine upload --repository testpypi dist/*
## Install
<!-- 2. python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps ResearchOS -->
### NOTE: This installs the package from the test PyPI repository but dependencies are installed from the main PyPI repository.
2. python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple ResearchOS

# PyPI
## Upload
1. python3 -m twine upload dist/*
## Install
2. python3 -m pip install ResearchOS