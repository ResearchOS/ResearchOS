# How to deploy the documentation

# Required packages:
1. mkdocstrings
2. mkdocs-material
3. mkdocstrings-python
4. awesome-pages (https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin)

# Required files:
1. mkdocs.yml

# Usage:
1. To build the documentation locally for testing:
`mkdocs serve`

2. To publish the documentation:
First, commit and push all changes to the repository.
Then, run: `mkdocs gh-deploy`