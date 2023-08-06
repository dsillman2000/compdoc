import fnmatch
import glob
import os

from compdoc.model import ClassDoc, DocType, FuncDoc


"""Documentation stubs for default formatters. Jinja implementations are in the default_formatters folder."""

class Href:
    def href(doc: DocType) -> str: # type: ignore
        """Returns a URL to the source file (and line number) defining the given `ModuleDoc`, `ClassDoc` or `FuncDoc`.

        Args:
            doc (DocType): Doc to get the source link to

        Returns:
            str: URL to the source of the Doc
        """        
        ...

class Ul:
    def format_class(cls: ClassDoc, link: bool = True) -> str: # type: ignore
        """Formats the docstring of the given `ClassDoc` as a unnumbered list ("ul"). If requested, indents the 
        result by `indent` spaces and optionally includes a hyperlink to the source code if link is `true`.

        Args:
            cls (ClassDoc): `ClassDoc` to format into "ul" form
            link (bool, optional): Whether or not to hyperlink the name of the function to the source code

        Returns:
            str: `ClassDoc` string, in "ul" format
        """        
        ...
    def format_function(func: FuncDoc, link: bool = True) -> str: # type: ignore
        """Formats the docstring of the given `FuncDoc` as an unnumbered list ("ul"). If requested, indents the 
        result by `indent` spaces and optionally includes a hyperlink to the source code if `link` is true.

        Args:
            func (FuncDoc): `FuncDoc` to format into "ul" form
            link (bool, optional): Whether or not to hyperlink the name of the function to the source code

        Returns:
            str: `FuncDoc` string, in "ul" format
        """        
        ...

class InlineUl:
    def format_class(cls: ClassDoc, link: bool = True) -> str: # type: ignore
        """Formats the docstring of the given `ClassDoc` as an inline HTML span for embedding in a table. Formats nearly 
        identically as the 'ul' formatter.

        Args:
            func (ClassDoc): `ClassDoc` to format into HTML inline "ul" form
            link (bool, optional): Whether or not to hyperlink the name of the class to the source code

        Returns:
            str: `ClassDoc` string, in HTML inline "ul" format
        """        
        ...

    def format_function(func: FuncDoc, link: bool = True) -> str: # type: ignore
        """Formats the docstring of the given `FuncDoc` as an inline HTML span for embedding in a table. Formats nearly 
        identically as the 'ul' formatter.

        Args:
            func (FuncDoc): FuncDoc to format into HTML inline "ul" form
            link (bool, optional): Whether or not to hyperlink the name of the function to the source code

        Returns:
            str: `FuncDoc` string, in HTML inline "ul" format
        """        
        ...


def load_formatters(out_folder: str, load_pattern: str = '*') -> dict[str, str]:
    """CLI callback for copying the default formatters (documented above, implemented in `default_formatters` subfolder)
    into the current project's directory.

    Args:
        out_folder (str): Name of the output folder to copy the default formatters to
        load_pattern (str, optional): Pattern for names of default formatters to copy. Defaults to '*'.

    Returns:
        dict[str, str]: Mapping of formatters to their local copy location, as in the .compdoc.yml.
    """    

    if not os.path.exists(out_folder):
        os.mkdir(out_folder)

    formatter_files = glob.glob('default_formatters/' + load_pattern, root_dir=os.path.dirname(__file__))
    print('formatter files = %s' % formatter_files)
    
    formatter_basenames = { os.path.basename(ff): ff for ff in formatter_files }
    matching_formatters = { k: v for k, v in formatter_basenames.items() if fnmatch.fnmatch(k, load_pattern) }

    for basename, path in matching_formatters.items():
        path = os.path.join('compdoc_cli', path)
        with open(path, 'r') as formatter_src:
            with open(os.path.join(out_folder, basename), 'w') as formatter_dst:
                formatter_dst.write(formatter_src.read())

    return { 
        basename[:basename.find('.')]: os.path.join(out_folder, basename) 
        for basename in matching_formatters 
    }