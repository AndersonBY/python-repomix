"""Tree-sitter query for C++ code analysis."""

# C++ tree-sitter query for extracting key code elements
query_cpp = """
; Comments
(comment) @comment

; Include statements
(preproc_include) @definition.import

; Namespace definitions
(namespace_definition
  name: (identifier) @name.definition.namespace) @definition.namespace

; Class definitions
(class_specifier
  name: (type_identifier) @name.definition.class) @definition.class

; Struct definitions
(struct_specifier
  name: (type_identifier) @name.definition.class) @definition.class

; Function definitions
(function_definition
  declarator: (function_declarator
    declarator: (identifier) @name.definition.function)) @definition.function

; Method definitions (inside class)
(function_definition
  declarator: (function_declarator
    declarator: (qualified_identifier
      name: (identifier) @name.definition.method))) @definition.method

; Template definitions
(template_declaration) @definition.template

; Enum definitions
(enum_specifier
  name: (type_identifier) @name.definition.class) @definition.class

; Typedef definitions
(type_definition
  declarator: (type_identifier) @name.definition.type) @definition.type
"""
