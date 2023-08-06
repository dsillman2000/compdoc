import abc
import os

import jinja2

from compdoc.exceptions import FormatterMissingException, FormatUnsupportedDocException
from compdoc.model import ClassDoc, DocType, FuncDoc


def _format_class_doc(self, class_doc: ClassDoc, and_subfunctions: bool = False) -> str:
    spc = '&nbsp;'
    header2 = f"""## {class_doc.class_name}"""
    bases_headnote = f"""{spc * 4}_Base(s): {', '.join(class_doc.bases)}_\n"""
    doc_section = f"""{class_doc.doc}"""

    class_funcdocs = []
    inst_funcdocs = []
    if and_subfunctions:
        class_funcdocs = [ fdoc for fdoc in class_doc.elements if fdoc.annotations.first_arg == 'cls' ]
        inst_funcdocs = [ fdoc for fdoc in class_doc.elements if fdoc.annotations.first_arg == 'self' ]

    class_method_header = f"""### Class methods\n\n"""
    class_method_section = '\n\n'.join([self._format_func_doc(cfd) for cfd in class_funcdocs])
    
    inst_method_header = f"""### Instance methods\n\n"""
    inst_method_section = '\n\n'.join([self._format_func_doc(ifd) for ifd in inst_funcdocs])

    return f"""{header2}\n{'' if not class_doc.bases else bases_headnote}\n{doc_section}\n\n""" + \
        f"""{(class_method_header + class_method_section) if class_funcdocs else ''}""" + \
        f"""{(inst_method_header + inst_method_section) if inst_funcdocs else ''}"""

def _format_func_doc(self, func_doc: FuncDoc) -> str:
    spc = '&nbsp;'
    func_firstarg = func_doc.annotations.first_arg if func_doc.annotations.first_arg else ''
    if func_firstarg:
        func_zippedargs = ''.join(', ' + name + ': ' + type for name, type in func_doc.annotations.args)
    else:
        func_zippedargs = ', '.join(name + ': ' + type for name, type in func_doc.annotations.args)
    func_li = f"- `{func_doc.func_name} : ({func_firstarg}{func_zippedargs}) -> {func_doc.annotations.returns}`"
    func_doc_section = '' if not func_doc.doc else func_doc.doc.replace('\n\n', '\n\n  - ').replace('\n    ', '\n  - ')

    return f"""{func_li}\n\n  {func_doc_section}"""
