import ast
import glob
import os
from typing import Optional

import docstring_parser

from compdoc.exceptions import (
    AstParseException,
    ModuleNotFoundException,
    ParseArgAnnotationException,
    ParseClassBaseException,
)
from compdoc.model import ClassDoc, FuncAnnotations, FuncDoc, ModuleDoc


def index_modules(project_filepath: str) -> dict[str, str]:
    python_files = glob.glob('*.py', root_dir=project_filepath) + glob.glob('**/*.py', root_dir=project_filepath)
    python_files = [ p.removeprefix('./') for p in python_files ]
    module_shortnames = [ p.replace('/', '.').removesuffix('.py') for p in python_files ]
    return dict(zip(module_shortnames, python_files))


def parse_module(source_filepath: str) -> ModuleDoc:
    
    if not os.path.exists(source_filepath):
        raise ModuleNotFoundException('Could not find module: ' + source_filepath)

    with open(source_filepath, 'r') as handle:
        try:
            module: ast.Module = ast.parse(handle.read(), filename=source_filepath)
        except Exception as e:
            raise AstParseException('AST Failed to parse module: ' + source_filepath + '\nReason:\n' + str(e))

    module_name = os.path.basename(source_filepath).removesuffix('.py')
    module_doc = ModuleDoc(module_name, source_filepath, [])
    
    for statement in module.body:

        if isinstance(statement, ast.ClassDef):
            class_doc: ClassDoc = parse_class_def(statement, source_filepath)
            module_doc = module_doc._replace(docs=module_doc.docs + [class_doc])
        elif isinstance(statement, ast.FunctionDef):
            func_doc: FuncDoc = parse_function_def(statement, source_filepath)
            module_doc = module_doc._replace(docs=module_doc.docs + [func_doc])

    return module_doc


def parse_class_def(class_def: ast.ClassDef, filepath: str) -> ClassDoc:

    class_bases: list[str] = []

    for base in class_def.bases:
        if isinstance(base, ast.Name):
            class_bases += [ base.id ]
        elif isinstance(base, ast.Subscript):
            assert isinstance(base.value, ast.Name) and isinstance(base.slice, ast.Name)
            class_bases += [ base.value.id + '[' + base.slice.id + ']' ]
        else:
            raise ParseClassBaseException('Failed to parse base %s of class %s' % (base, class_def.name))

    class_doc = ClassDoc(
        class_def.name, 
        filepath, 
        class_def.lineno, 
        None, 
        None,
        class_bases, 
        [],
    )

    if isinstance(class_def.body[0], ast.Expr):
        if isinstance(class_def.body[0].value, ast.Constant):
            if class_def.body[0].value.s  is not None:
                body_offset: int = class_def.col_offset + 4
                docstring = class_def.body[0].value.s.replace('\n' + ' ' * body_offset, '\n').strip()
                class_doc = class_doc._replace(
                    string=docstring,
                    docstring=docstring_parser.parse(docstring),
                )

    for statement in class_def.body:

        if isinstance(statement, ast.FunctionDef):
            func_doc: FuncDoc = parse_function_def(statement, filepath)
            class_doc = class_doc._replace(elements=class_doc.elements + [func_doc])

    return class_doc


def parse_function_def(function_def: ast.FunctionDef, filepath: str) -> FuncDoc:
    
    func_doc = FuncDoc(
        function_def.name,
        filepath,
        function_def.lineno,
        parse_function_annotations(function_def),
        None,
        None,
    )

    if isinstance(function_def.body[0], ast.Expr):
        if isinstance(function_def.body[0].value, ast.Constant):
            if function_def.body[0].value.s is not None:
                body_offset: int = function_def.col_offset + 4
                docstring = function_def.body[0].value.s.replace('\n' + ' ' * body_offset, '\n').strip()
                func_doc = func_doc._replace(
                    string=docstring,
                    docstring=docstring_parser.parse(docstring),
                )

    return func_doc

def parse_function_annotations(function_def: ast.FunctionDef) -> FuncAnnotations:

    def _parse_arg_annotation(annotation: Optional[ast.expr], default='None') -> str:
        if annotation is None:
            return default
        if isinstance(annotation, ast.Name):
            return annotation.id
        if isinstance(annotation, ast.Subscript):
            if not isinstance(annotation.value, ast.Name):
                raise ParseArgAnnotationException('Failed to parse subscript value: %s' % annotation.value)
            return annotation.value.id + '[' + _parse_arg_annotation(annotation.slice) + ']'
        if isinstance(annotation, ast.Constant):
            return annotation.value
        if isinstance(annotation, ast.Tuple):
            return ', '.join(map(_parse_arg_annotation, annotation.elts))
        raise ParseArgAnnotationException('Failed to parse arg annotation: %s' % annotation)

    return_type = _parse_arg_annotation(function_def.returns)

    first_arg = None
    arg_names: list[str] = []
    arg_types: list[str] = []
    if len(function_def.args.args) > 0:

        """Parse leading argument, if it is _self_ or _cls_ and has no annotations"""
        match (function_def.args.args[0].arg, function_def.args.args[0].annotation):
            case ('self', None):
                first_arg = 'self'
            case ('cls', None):
                first_arg = 'cls'
        
        """Parse named arguments"""
        named_args_offset = 0 if first_arg is None else 1
        arg_names += [ a.arg for a in function_def.args.args[named_args_offset:] ]

        """Parse types of named arguments"""
        for arg in function_def.args.args[named_args_offset:]:
            arg_types += [ _parse_arg_annotation(arg.annotation) ]

        """Parse var arg name and type, if it exists"""
        if function_def.args.vararg is not None:
            arg_names += [ '*' + function_def.args.vararg.arg ]
            var_arg_type: str = _parse_arg_annotation(function_def.args.vararg.annotation, default='Any')
            arg_types += [ var_arg_type ]

        """Parse kw arg name and type, if it exists"""
        if function_def.args.kwarg is not None:
            arg_names += [ '**' + function_def.args.kwarg.arg ]
            kw_arg_type: str = _parse_arg_annotation(function_def.args.kwarg.annotation, default='Any')
            arg_types += [ kw_arg_type ]

    func_annotations = FuncAnnotations(
        first_arg,
        list(zip(arg_names, arg_types)),
        return_type,
    )

    return func_annotations