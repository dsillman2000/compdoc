import os
from typing import Optional, TypedDict

from jinja2 import BaseLoader, Environment, Template
from jinja2.environment import TemplateModule

from compdoc.exceptions import (
    CompileClassFuncNotFoundException,
    CompileException,
    CompileUnrecognizedFormatterException,
    CompileUnrecognizedModuleAttrException,
    CompileUnrecognizedModuleException,
    FormatterMissingException,
)
from compdoc.model import ClassDoc, DocType, FuncDoc, ModuleDoc
from compdoc.parser import parse_module


class CompDocBase:
    doc: DocType

class CompDocFunction(CompDocBase):
    """Thin wrapper around FuncDoc to match APIs with other Jinja context objects (CompDocClass & CompDocModule).
    """    
    doc: FuncDoc

    def __init__(self, doc: FuncDoc):
        """Set the inner FuncDoc instance

        Args:
            doc (FuncDoc): FuncDoc instance to expose to the Jinja context as `doc`
        """        
        self.doc = doc


class CompDocClass(CompDocBase):
    """Jinja context object containing documentation details about a Python class.
    """    
    doc: ClassDoc
    attrs: dict[str, CompDocFunction]

    def __init__(self, doc: ClassDoc):
        """Builds a CompDoc wrapper around the ClassDoc's functions.

        Args:
            doc (ClassDoc): ClassDoc to parse into a Jinja context object
        """        
        self.doc = doc
        self.attrs = {}
        for d in self.doc.elements:
            self.attrs[d.func_name] = CompDocFunction(d)

    def __getattribute__(self, name: str) -> CompDocFunction:
        """Allows Jinja context to use attribute-getting "a.b" operations to reference module contents.

        Args:
            name (str): Name of the function to attempt to get

        Raises:
            CompileClassFuncNotFoundException: If the name requested does not map to an explicitly defined function in 
            the class.

        Returns:
            CompDocFunction: The class function, as a CompDocFunction, if it exists
        """        
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name in self.attrs:
                return self.attrs[name]
            raise CompileClassFuncNotFoundException("Could not find function %s in class %s" % (name, self.doc.class_name))
    

class CompDocModule(CompDocBase):
    """Jinja context object containing documentation details about a Python module.
    """    
    doc: ModuleDoc
    attrs: dict[str, CompDocClass | CompDocFunction]
    
    def __init__(self, doc: ModuleDoc):
        """Recursively builds out a CompDoc wrapper around the ModuleDoc's class and function tree.

        Args:
            doc (ModuleDoc): ModuleDoc to parse into a Jinja context object
        """        
        self.doc = doc
        self.attrs = {}
        for d in self.doc.docs:
            if isinstance(d, ClassDoc):
                self.attrs[d.class_name] = CompDocClass(d)
            else:
                self.attrs[d.func_name] = CompDocFunction(d)

    def __getattribute__(self, name: str) -> CompDocBase:
        """Allows Jinja context to use attribute-getting "a.b" operations to reference module contents.

        Args:
            name (str): Name of attribute to attempt to get

        Raises:
            CompileUnrecognizedModuleAttrException: If an unrecognized attribute is being requested

        Returns:
            CompDocBase: The module element, either a CompDocClass or CompDocFunction, if it exists
        """        
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name in self.attrs:
                return self.attrs[name]
            raise CompileUnrecognizedModuleAttrException('Could not find element %s of module %s' % (name, self.doc.module_name))


class CompDoc:
    """Jinja Context object for submitting CompDoc directives like `compdoc.module` and `compdoc.formatter`.
    """    
    config: dict[str, dict]
    env: Environment

    def __init__(self, config_dict: dict[str, dict], env: Environment):
        """Instantiate a new CompDoc context

        Args:
            config_dict (dict[str, dict]): Configuration for the CompDoc context, from a `.compdoc.yml` file
            env (Environment): Jinja environment from which this context is being used
        """        
        self.config = config_dict
        self.env = env

    def module(self, module_name: str) -> CompDocModule:
        """Returns a CompDocModule containing documentation details for the module's contents, if it's been
        indexed in the configuration .compdoc.yml file.

        Args:
            module_name (str): Module name to look up in the configuration module index

        Raises:
            CompileUnrecognizedModuleException: If the module name could not be found in the configuration yaml

        Returns:
            CompDocModule: CompDocModule containing documentation details for the module, if it could be found
        """        
        if module_name not in self.config['modules']:
            raise CompileUnrecognizedModuleException('Did not recognize module "%s"' % module_name)
        return CompDocModule(parse_module(self.config['modules'][module_name]))
    
    def formatter(self, formatter: str) -> TemplateModule:
        """Returns a module to the Jinja template for the requested formatter name. The formatter name must be indexed 
        in .compdoc.yml. The contained formatting macros can be called from the returned module.

        Args:
            formatter (str): Formatter name to look up and use

        Raises:
            CompileUnrecognizedFormatterException: The requested formatter is not indexed in .compdoc.yml
            FormatterMissingException: The formatter's Jinja template file could not be found

        Returns:
            TemplateModule: The module implementing the formatter's Jinja macros
        """        
        
        if formatter not in self.config['formatters']:
            raise CompileUnrecognizedFormatterException('Unrecognized formatter: %s' % formatter)
        
        macros_path = self.config['formatters'][formatter]

        if not os.path.exists(macros_path):
            raise FormatterMissingException("Couldn't find formatter: %s" % macros_path)

        with open(macros_path, 'r') as tf:
            formatter_module = self.env.from_string(tf.read()).make_module()

        return formatter_module


def compile_compdoc_mdj2(template_path: str, config_dict: dict[str, dict], out_path: Optional[str] = None):

    template_basename, template_ext = os.path.splitext(os.path.basename(template_path))
    env = Environment(extensions=['jinja2.ext.do'], loader=BaseLoader())
    _compdoc = CompDoc(config_dict, env=env)
    env_globals = env.make_globals({
        "compdoc": _compdoc
    })

    if out_path is None:
        if template_path.endswith('.j2'):
            out_path = template_path.removesuffix('.j2')
        else:
            out_path = template_basename + '.compiled.' + template_ext
    
    with open(template_path, 'r') as f:
        template = env.from_string(f.read(), globals=env_globals)

    try:
        with open(out_path, 'w') as f:
            f.write(template.render())
    except Exception as e:
        raise CompileException('Failed to compile template %s. Error message: %s' % (template_path, str(e)))

