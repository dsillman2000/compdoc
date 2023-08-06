class ModuleNotFoundException(Exception):
    pass

class AstParseException(Exception):
    pass

class ParseClassBaseException(Exception):
    pass

class ParseArgAnnotationException(Exception):
    pass

class FormatUnsupportedDocException(Exception):
    pass

class FormatterMissingException(Exception):
    pass

class CompileUnrecognizedModuleException(Exception):
    pass

class CompileUnrecognizedModuleAttrException(Exception):
    pass

class CompileUnrecognizedFormatterException(Exception):
    pass

class CompileClassFuncNotFoundException(Exception):
    pass

class CompileException(Exception):
    pass