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


- [**`ModuleDoc`**](compdoc/model.py#L70): Struct for storing documentation details of the composite functions and classes of a Python module.
  - _Base(s)_: NamedTuple
  - **Attributes**:
    - `module_name (str)`: Name of the module, as in `__module__`.
    - `filepath (str)`: Path to the source file, relative to the project root.
    - `docs (list[ClassDoc | FuncDoc])`: Implemented classes and functions in the module.


- [**`ClassDoc`**](compdoc/model.py#L37): Struct for storing documentation details of the functions which compose a class, including a docstring for the class itself.
  - _Base(s)_: NamedTuple
  - **Attributes**:
    - `class_name (str)`: Name of the class, as in `__class__`.
    - `filepath (str)`: Path to the source file, relative to the project root.
    - `line_no (int)`: Line number of the class implementation.
    - `string (str)`: Plaintext docstring at the top of the class implementation.
    - `docstring (Docstring)`: Parsed docstring contents, as a `docstring_parser.Docstring`.
    - `bases (list[str])`: List of base classes of this class implementation.
    - `elements (list[FuncDoc])`: List of implemented methods of this class.


- [**`FuncDoc`**](compdoc/model.py#L19): Struct for storing documentation details about functions, including their signature & docstring.
  - _Base(s)_: NamedTuple
  - **Attributes**:
    - `func_name (str)`: Name of the function.
    - `filepath (str)`: Path to the source file, relative to the project root.
    - `line_no (int)`: Line number of the function implementation.
    - `annotations (FuncAnnotations)`: Object containing metadata of the function signature.
    - `string (str)`: Plaintext docstring at the top of the function implementation.
    - `docstring (Docstring)`: Parsed docstring contents, as a `docstring_parser.Docstring`.

The containment relationships between these constructs are summarized symbolically:

```
ModuleDoc* {
    ClassDoc* {
        FuncDoc*
    }
    FuncDoc*
}
```

In order to load documentation details into your Jinja context, you use the [`compdoc.module`](
compdoc/compiler.py#L130) function:

```j2
{% set mymodule = compdoc.module('mymodule') %}
```

Which will have attributes for the constituent classes and functions. For example, we can use it to format verbatim 
docstrings from our source code:

```j2
The `mymodule` module implements `MyClass`:
- {{ mymodule.MyClass.doc.string }}
```

> Note that accessing the attributes enumerated in the above docs for `ClassDoc` and `FuncDoc` must be done through the 
> `doc` attribute. In this case, we're accessing the `string` attribute of `ClassDoc` via the `doc` attribute on
> `mymodule.MyClass`.

Likewise, we can access the verbatim docstrings from function definitions as well:

```j2
Docstring for `MyClass.my_function` method:
- {{ mymodule.MyClass.my_function.doc.string }}

Docstring for `mymodule.my_standalone_function` method:
- {{ mymodule.my_standalone_function.doc.string }}
```

### Formatters

TODO: section on formatters