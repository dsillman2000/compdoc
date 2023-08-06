import ast

import pytest

from compdoc.model import ClassDoc, FuncDoc, ModuleDoc
from compdoc.parser import parse_module


def test_parse_module():

    rval = parse_module('tests/vectortest/vec.py')
    
    assert rval.module_name == 'vec'
    assert rval.filepath == 'tests/vectortest/vec.py'
    assert len(rval.docs) == 4

    vec2doc = rval.docs[0]
    assert isinstance(vec2doc, ClassDoc)
    assert vec2doc.class_name == 'Vec2'
    assert vec2doc.filepath == 'tests/vectortest/vec.py'
    assert vec2doc.line_no == 7
    assert vec2doc.bases == ['NamedTuple']
    assert vec2doc.string == '2-dimensional vector struct, represented as a named tuple.'
    assert len(vec2doc.elements) == 1

    vec2normdoc = vec2doc.elements[0]
    assert isinstance(vec2normdoc, FuncDoc)
    assert vec2normdoc.func_name == 'norm'
    assert vec2normdoc.filepath == 'tests/vectortest/vec.py'
    assert vec2normdoc.line_no == 13
    assert vec2normdoc.annotations._asdict() == {'first_arg': 'self', 'args': [], 'returns': 'float'}
    assert vec2normdoc.string == 'Computes the L2 norm of the vector.\n\nReturns:\n    float: Norm of this vector'

    vec3doc = rval.docs[1]
    assert isinstance(vec3doc, ClassDoc)
    assert vec3doc.class_name == 'Vec3'
    assert vec3doc.filepath == 'tests/vectortest/vec.py'
    assert vec3doc.line_no == 22
    assert vec3doc.bases == ['NamedTuple']
    assert vec3doc.string == '3-dimensional vector struct, represented as a named tuple.'
    assert len(vec3doc.elements) == 1

    vec3normdoc = vec3doc.elements[0]
    assert isinstance(vec3normdoc, FuncDoc)
    assert vec3normdoc.func_name == 'norm'
    assert vec3normdoc.filepath == 'tests/vectortest/vec.py'
    assert vec3normdoc.line_no == 29
    assert vec3normdoc.annotations._asdict() == {'first_arg': 'self', 'args': [], 'returns': 'float'}
    assert vec3normdoc.string == 'Computes the L2 norm of the vector.\n\nReturns:\n    float: Norm of this vector'

    vecndoc = rval.docs[2]
    assert isinstance(vecndoc, ClassDoc)
    assert vecndoc.class_name == 'VecN'
    assert vecndoc.filepath == 'tests/vectortest/vec.py'
    assert vecndoc.line_no == 38
    assert vecndoc.bases == ['NamedTuple']
    assert vecndoc.string == 'N-dimensional vector struct, represented as a named tuple.'
    assert len(vecndoc.elements) == 3

    vecnfromcomponentsdoc = vecndoc.elements[0] 
    assert isinstance(vecnfromcomponentsdoc, FuncDoc)
    assert vecnfromcomponentsdoc.func_name == 'from_components'
    assert vecnfromcomponentsdoc.filepath == 'tests/vectortest/vec.py'
    assert vecnfromcomponentsdoc.line_no == 45
    assert vecnfromcomponentsdoc.annotations._asdict() == {
        'first_arg': 'cls', 'args': [('*components', 'float')], 'returns': 'VecN'
    }
    assert vecnfromcomponentsdoc.string == ('Constructs a VecN from however many floating point components are provided.\n'
                                        '\nReturns:\n    VecN: A new n-dimensional vector with the specified components')
    
    vecnfromlistdoc = vecndoc.elements[1]
    assert isinstance(vecnfromlistdoc, FuncDoc)
    assert vecnfromlistdoc.func_name == 'from_list'
    assert vecnfromlistdoc.annotations._asdict() == {
        'first_arg': 'cls', 'args': [('xs', 'list[float]')], 'returns': 'VecN'
    }

    flattenvecsdoc = rval.docs[3]
    assert isinstance(flattenvecsdoc, FuncDoc)
    assert flattenvecsdoc.func_name == 'flatten_vecs'
    assert flattenvecsdoc.annotations._asdict() == {
        'first_arg': None, 'args': [('vecs', 'list[VecN]')], 'returns': 'VecN'
    }

def test_func_query():

    vec = parse_module('tests/vectortest/vec.py')
    assert vec.get_class('Vec1') is None

    vec2doc = vec.get_class('Vec2')
    assert vec2doc is not None
    assert vec.get_func('Vec2.norm') == vec2doc.elements[0]

    fvecdoc = vec.get_func('flatten_vecs')
    assert fvecdoc is not None
    assert fvecdoc.annotations.returns == 'VecN'