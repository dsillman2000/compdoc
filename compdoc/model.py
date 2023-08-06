from enum import StrEnum
from typing import Literal, NamedTuple, Optional, Union

from docstring_parser import Docstring

class ValidationStatus(StrEnum):
    FAILURE = 'failure'
    SUCCESS = 'success'

class DocValidation:
    """Struct for representing the cumulative validation status of a collection of CompDoc documents.

    Attributes:
        name (str): The name for tracking this DocValidation
        status (ValidationStatus): The status of the validation ('success' or 'failure')
        message (str): The message associated with this DocValidation if it has on or more failures
    """    
    name: str
    status: ValidationStatus = ValidationStatus('success')
    message: Optional[str] = None

    def __init__(self, name: str):
        self.name = name

    def append_error(self, msg: str):
        """Instantiates a DocValidation failure with the specified message.

        Args:
            msg (str): Failure message to attach to the DocValidation object

        Returns:
            DocValidation: Resulting DocValidation object
        """        
        self.status = ValidationStatus('failure')
        self.message = (self.message if self.message else '') + '\n' + msg

    # def __add__(self, other: "DocValidation") -> "DocValidation":
    #     """Merge DocValidation results from a different CompDoc.

    #     Args:
    #         other (DocValidation): Other DocValidation to merge with

    #     Returns:
    #         DocValidation: Joint DocValidation object
    #     """        
    #     self.status = min(self.status, other.status)
    #     self.message = (self.message if self.message else '') + '\n' + (other.message if other.message else '')
    #     return self

class FuncAnnotations(NamedTuple):
    """Struct for storing string representations of the components of a function's signature.

    Attributes:
        first_arg ('self' | 'cls' | None): Leading argument of the function, for distinguishing instance/class/external
            methods.
        args (list[tuple[str, str]]): Pairs of arg_name, arg_type for the function signature's arguments.
        returns (str): Return type of the function, as a string.
    """    
    first_arg: Optional[Literal['self', 'cls']]
    args: list[tuple[str, str]]
    returns: str

class FuncDoc(NamedTuple):
    """Struct for storing documentation details about functions, including their signature & docstring.

    Attributes:
        func_name (str): Name of the function.
        filepath (str): Path to the source file, relative to the project root.
        line_no (int): Line number of the function implementation.
        annotations (FuncAnnotations): Object containing metadata of the function signature.
        string (str): Plaintext docstring at the top of the function implementation.
        docstring (Docstring): Parsed docstring contents, as a `docstring_parser.Docstring`.
    """    
    func_name: str
    filepath: str
    line_no: int
    annotations: FuncAnnotations
    string: Optional[str]
    docstring: Optional[Docstring]

    def validate(self) -> DocValidation:
        """Determines if there are disagreements between the annotations in the function signature and its docstring.
        If there is agreement, the resulting DocValidation will have `'success'` as its status. Otherwise, it will have
        `'fail'` as its status, and a message.

        Returns:
            DocValidation: Result of the function signature validation
        """        
        val = DocValidation(f'{self.filepath}\t@ {self.func_name}')
        if self.docstring is None:
            val.append_error("Docstring is missing.")
        elif len(self.docstring.params) != len(self.annotations.args):
            if self.annotations.first_arg is not None:
                if len(self.docstring.params) and self.docstring.params[0].arg_name == self.annotations.first_arg:
                    val.append_error('Neither "self" nor "cls" should be specified in function docstring arguments.')
            val.append_error('Mismatching function signature arguments:\nSignature: %s\nDocstring: %s' % \
                             (self.annotations.args, tuple((p.arg_name, p.type_name) for p in self.docstring.params)))
        return val


class ClassDoc(NamedTuple):
    """Struct for storing documentation details of the functions which compose a class, including a docstring for the 
        class itself.

    Attributes:
        class_name (str): Name of the class, as in `__class__`.
        filepath (str): Path to the source file, relative to the project root.
        line_no (int): Line number of the class implementation.
        string (str): Plaintext docstring at the top of the class implementation.
        docstring (Docstring): Parsed docstring contents, as a `docstring_parser.Docstring`.
        bases (list[str]): List of base classes of this class implementation.
        elements (list[FuncDoc]): List of implemented methods of this class.
    """    
    class_name: str
    filepath: str
    line_no: int
    string: Optional[str]
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
    
    def validate(self) -> list[DocValidation]:
        """Validate the constituent functions of a ClassDoc have matching docstrings and signatures.

        Returns:
            list[DocValidation]: List of validation results
        """        
        return [ el.validate() for el in self.elements ]


DocType = Union[ClassDoc, FuncDoc]

class ModuleDoc(NamedTuple):
    """Struct for storing documentation details of the composite functions and classes of a Python module.

    Attributes:
        module_name (str): Name of the module, as in `__module__`.
        filepath (str): Path to the source file, relative to the project root.
        docs (list[ClassDoc | FuncDoc]): Implemented classes and functions in the module.
    """    
    module_name: str
    filepath: str
    docs: list[DocType]

    @property
    def classes(self) -> list[ClassDoc]:
        return [ cdoc for cdoc in self.docs if isinstance(cdoc, ClassDoc) ]
    
    @property
    def external_functions(self) -> list[FuncDoc]:
        return [ fdoc for fdoc in self.docs if isinstance(fdoc, FuncDoc) ]

    def validate(self) -> list[DocValidation]:
        """Validates the constituent functions and classes in the ModuleDoc to determine if any of them have
        mismatching docstrings and signatures.

        Returns:
            list[DocValidation]: Results of the constituent validations
        """        
        vals = []
        for doc in self.docs:
            if isinstance(doc, FuncDoc):
                vals.append(doc.validate())
            else:
                vals.extend(doc.validate())
        return vals

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