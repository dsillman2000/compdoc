# CompDoc

CompDoc is a Python CLI tool for Jinja-formatting docstrings from your library into other documentation formats.

### Introduction

My impetus for putting this tool together was running into these issues maintaining documentation, even for relatively simple Python libraries:

> 
> 1. "I have to copy any changes I make to my docstrings to my other documentation sources, like my README. It almost makes me not want to bother changing the API of my existing code.
> 
> 2. "When my code is edited or moves around, line number links need to be rewritten to point to the correct lines in the source code."
> 
> 3. "I make updates to APIs in my code, but sometimes forget to update the docstrings or other documentation."
> 

CompDoc solves these issues by providing a CLI for parsing your Python library's constitutent modules, classes and functions. CompDoc provides a Jinja environment variable, `compdoc`, which can be used to access both the docstrings of your code and its true annotations.

### Getting Started

Install the CompDoc CLI using

```sh
pip install git+https://github.com/dsillman2000/compdoc.git
# soon: pip install compdoc
```

You can then initialize CompDoc in your project's root directory using

```sh
compdoc init path/to/project_folder
```

This will index your project, and create a configuration YAML called `.compdoc.yml` in the project folder. The configuration file will have a `modules` section, with indexed Python files, and a `formatters` section listing the default formatters available for templating in Jinja. The source code for the formatters will be available in 
a subfolder of your project folder, called `compdoc-formatters`, where you can edit or add new ones to your project.

> Note: To reference custom formatters from the Jinja environment, you must add an entry in the `formatters` section of your configuration.

CompDoc knows how to index three different types of Python library constructs:

- **Modules**: Distinct Python `*.py` source files, anywhere in the project directory tree.
- **Classes**: Class definitions within `*.py` source files.
- **Functions**: Function definitions within `*.py` source files, including those defined within classes.

When parsing the project, CompDoc uses Python's native `ast` library to parse metadata about each of the Python constructs you've implemented.