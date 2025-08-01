"""Tree-sitter query for TypeScript code analysis."""

# TypeScript tree-sitter query (using JavaScript parser)
query_typescript = """
; Comments
(comment) @comment

; Import statements
(import_statement) @definition.import

; Export statements
(export_statement) @definition.export

; Class definitions
(class_declaration
  name: (identifier) @name.definition.class) @definition.class

; Function declarations
(function_declaration
  name: (identifier) @name.definition.function) @definition.function

; Method definitions
(method_definition
  name: (property_identifier) @name.definition.method) @definition.method

; Variable declarations (const, let, var)
(lexical_declaration
  (variable_declarator
    name: (identifier) @name.definition.variable)) @definition.variable

; Regular variable declarations
(variable_declaration
  (variable_declarator
    name: (identifier) @name.definition.variable)) @definition.variable
"""
