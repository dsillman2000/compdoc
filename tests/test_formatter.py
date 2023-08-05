from compdoc.format import DavidFormatter
from compdoc.parser import parse_module


def test_david_formatter():

    vec = parse_module('tests/vectortest/vec.py')

    df = DavidFormatter()
    
    assert df.format_doc(vec.docs[0])