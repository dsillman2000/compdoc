# CompDoc









CompDoc is a Python CLI tool for Jinja-formatting docstrings from your library into other documentation formats.

### Introduction

My impetus for putting this tool together was running into these issues maintaining documentation, even for relatively 
simple Python libraries:

> 
> 1. "I have to copy any changes I make to my docstrings to my other documentation sources, like my README. It almost 
>   makes me not want to bother changing the API of my existing code."
> 
> 2. "When my code is edited or moves around, line number links need to be rewritten to point to the correct lines in 
>   the source code."
> 
> 3. "I make updates to APIs in my code, but sometimes forget to update the docstrings or other documentation."
> 

CompDoc solves these issues by providing a CLI for parsing your Python library's constitutent modules, classes and 
functions. CompDoc provides a Jinja environment variable, `compdoc`, which can be used to access both the docstrings of 
your code and its true annotations.

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

This will index your project, and create a configuration YAML called `.compdoc.yml` in the project folder. The 
configuration file will have a `modules` section, with indexed Python files, and a `formatters` section listing the 
default formatters available for templating in Jinja. The source code for the formatters will be available in a 
subfolder of your project folder, called `compdoc-formatters`, where you can edit or add new ones to your project.

> Note: To reference custom formatters from the Jinja environment, you must add an entry in the `formatters` section of 
> your configuration.

CompDoc knows how to index three different types of Python library constructs:

- **Modules**: Distinct Python `*.py` source files, anywhere in the project directory tree.
- **Classes**: Class definitions within `*.py` source files.
- **Functions**: Function definitions within `*.py` source files, including those defined within classes.

When parsing the project, CompDoc uses Python's native `ast` library to parse metadata about each of the Python 
constructs you've implemented.


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

In order to load documentation details into your Jinja context, you use the [`compdoc.module`]
(
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

## Formatters

### Built-in Formatters

The `compdoc` API provides a function for loading _formatters_ into the Jinja context, which are essentially namespaces
for storing helper Jinja macros which act on `ModuleDoc`, `ClassDoc` or `FuncDoc` instances. Some of the default 
out-of-the-box formatters are listed below:

|Formatter Name|Formatter API|
|-|-|
|`'href'`|<ul><li><code>[href](compdoc_cli/formatters.py#L11) : (doc: DocType) -> str</code></li><ul><li>Returns a URL to the source file (and line number) defining the given `ModuleDoc`, `ClassDoc` or `FuncDoc`.</li><span><li><b>Args</b>:</li><ul><li><code>doc (DocType)</code>: Doc to get the source link to</li></ul><li><b>Returns</b>:</li><ul><li><code>str</code>: URL to the source of the Doc</li></ul></ul></ul></span>|
|`'ul'`|<ul><li><code>[format_class](compdoc_cli/formatters.py#L23) : (cls: ClassDoc, link: bool) -> str</code></li><ul><li>Formats the docstring of the given `ClassDoc` as a unnumbered list ("ul"). If requested, indents the result by `indent` spaces and optionally includes a hyperlink to the source code if link is `true`.</li><span><li><b>Args</b>:</li><ul><li><code>cls (ClassDoc)</code>: `ClassDoc` to format into "ul" form</li><li><code>link (bool)</code>: Whether or not to hyperlink the name of the function to the source code</li></ul><li><b>Returns</b>:</li><ul><li><code>str</code>: `ClassDoc` string, in "ul" format</li></ul></ul></ul></span><br /><ul><li><code>[format_function](compdoc_cli/formatters.py#L35) : (func: FuncDoc, link: bool) -> str</code></li><ul><li>Formats the docstring of the given `FuncDoc` as an unnumbered list ("ul"). If requested, indents the result by `indent` spaces and optionally includes a hyperlink to the source code if `link` is true.</li><span><li><b>Args</b>:</li><ul><li><code>func (FuncDoc)</code>: `FuncDoc` to format into "ul" form</li><li><code>link (bool)</code>: Whether or not to hyperlink the name of the function to the source code</li></ul><li><b>Returns</b>:</li><ul><li><code>str</code>: `FuncDoc` string, in "ul" format</li></ul></ul></ul></span>|
|`'inline_ul'`|<ul><li><code>[format_class](compdoc_cli/formatters.py#L49) : (cls: ClassDoc, link: bool) -> str</code></li><ul><li>Formats the docstring of the given `ClassDoc` as an inline HTML span for embedding in a table. Formats nearly identically as the 'ul' formatter.</li><span><li><b>Args</b>:</li><ul><li><code>func (ClassDoc)</code>: `ClassDoc` to format into HTML inline "ul" form</li><li><code>link (bool)</code>: Whether or not to hyperlink the name of the class to the source code</li></ul><li><b>Returns</b>:</li><ul><li><code>str</code>: `ClassDoc` string, in HTML inline "ul" format</li></ul></ul></ul></span><br /><ul><li><code>[format_function](compdoc_cli/formatters.py#L62) : (func: FuncDoc, link: bool) -> str</code></li><ul><li>Formats the docstring of the given `FuncDoc` as an inline HTML span for embedding in a table. Formats nearly identically as the 'ul' formatter.</li><span><li><b>Args</b>:</li><ul><li><code>func (FuncDoc)</code>: FuncDoc to format into HTML inline "ul" form</li><li><code>link (bool)</code>: Whether or not to hyperlink the name of the function to the source code</li></ul><li><b>Returns</b>:</li><ul><li><code>str</code>: `FuncDoc` string, in HTML inline "ul" format</li></ul></ul></ul></span>

### Custom Formatters

Custom formatters, then, can be injected into your project's CompDoc configuration by creating a new set of Jinja macros
inside of the `compdoc-formatters` directory in your project, e.g.

```j2
{% macro format(class_or_func) %}
<span>
    <b>{{ class_or_func.doc.filepath }}, line {{ class_or_func.doc.line_no }}</b>
    <ul><li>{{ class_or_func.doc.docstring.short_description }}</li></ul>
</span>
{% endmacro %}
```

If we save this as `compdoc-formatters/fancy.html.j2` and add `fancy: compdoc-formatters/fancy.html.j2` to our 
`formatters` section of the configuration YAML, then we can use it in our CompDoc documents:

```j2
Fancily, our standalone function looks like:

{% set fancy = compdoc.formatter('fancy') -%}
{{ fancy.format(mymodule.my_standalone_function) }}
```

Which compiles to look like the following

> Fancily, our standalone function looks like:
> 
> <span>
>     <b>mymodule.py, line 15</b>
>     <ul><li>The short description from our docstring for the function.</li></ul>
> </span>