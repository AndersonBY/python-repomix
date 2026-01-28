"""Tree-sitter query for C code analysis."""

# C tree-sitter query for extracting key code elements
query_c = """
; Comments
(comment) @comment

; Include statements
(preproc_include) @definition.import

; Function definitions
(function_definition
  declarator: (function_declarator
    declarator: (identifier) @name.definition.function)) @definition.function

; Struct definitions
(struct_specifier
  name: (type_identifier) @name.definition.class) @definition.class

; Enum definitions
(enum_specifier
  name: (type_identifier) @name.definition.class) @definition.class

; Typedef definitions
(type_definition
  declarator: (type_identifier) @name.definition.type) @definition.type

; Macro definitions
(preproc_def
  name: (identifier) @name.definition.macro) @definition.macro

(preproc_function_def
  name: (identifier) @name.definition.macro) @definition.macro
"""
