from typing import Literal, NamedTuple, Optional, Union

from docstring_parser import Docstring


class FuncAnnotations(NamedTuple):
    """Struct for storing string representations of the components of a function's signature.
    """    
    first_arg: Optional[Literal['self', 'cls']]
    args: list[tuple[str, str]]
    returns: str

class FuncDoc(NamedTuple):
    """Struct for storing documentation details about functions, including their signature & docstring.
    """    
    func_name: str
    filepath: str
    line_no: int
    annotations: FuncAnnotations
    doc: Optional[str]
    docstring: Optional[Docstring]

class ClassDoc(NamedTuple):
    """Struct for storing documentation details of the functions which compose a class, including a docstring for the 
    class itself.
    """    
    class_name: str
    filepath: str
    line_no: int
    doc: Optional[str]
    docstring: Optional[Docstring]
    bases: list[str]
    elements: list[FuncDoc]
    def get_func(self, name: str) -> Optional[FuncDoc]:
        """Searches the class for a function with the given name, returning its FuncDoc if it could be found.

        Args:
            name (str): Function name to search for

        Returns:
            Optional[FuncDoc]: FuncDoc for the specified function, if it could be found
        """        
        return next(filter(lambda f: f.func_name == name, self.elements), None)

DocType = Union[ClassDoc, FuncDoc]

class ModuleDoc(NamedTuple):
    """Struct for storing documentation details of the composite functions and classes of a Python module.
    """    
    module_name: str
    filepath: str
    docs: list[DocType]

    def get_class(self, name: str) -> Optional[ClassDoc]:
        """Searches the module for a class with the given name, returning its ClassDoc if it could be found.

        Args:
            name (str): Class name to search for

        Returns:
            Optional[ClassDoc]: ClassDoc for the specified class, if it could be found
        """        
        return next(filter(lambda c: getattr(c, 'class_name', None) == name, self.docs), None)
    

    def get_func(self, name: str) -> Optional[FuncDoc]:
        """Searches the module for a function with the given name, returning its FuncDoc if it could be found.

        Args:
            name (str): Function name to search for, supporting ClassName.func_name or func_name

        Returns:
            Optional[FuncDoc]: FuncDoc for the specified function, if it could be found
        """        
        if name.count('.') == 1:
            cl, fn = name.split('.')
            cl = self.get_class(cl)
            if cl is None:
                return None
            return cl.get_func(fn)
        elif '.' not in name:
            return next(filter(lambda f: getattr(f, 'func_name', None) == name, self.docs), None)
        else:
            return None