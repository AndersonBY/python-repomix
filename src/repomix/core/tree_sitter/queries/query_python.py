"""Tree-sitter query for Python code analysis."""

# Python tree-sitter query for extracting key code elements
query_python = """
; Import statements
(import_statement) @definition.import
(import_from_statement) @definition.import

; Class definitions
(class_definition) @definition.class

; Function definitions
(function_definition) @definition.function

; Module-level variable assignments (only simple ones)
(module 
  (expression_statement
    (assignment
      left: (identifier))) @definition.variable)

; Decorators
(decorator) @definition.decorator

; Global and nonlocal statements
(global_statement) @statement.global
(nonlocal_statement) @statement.nonlocal
"""
