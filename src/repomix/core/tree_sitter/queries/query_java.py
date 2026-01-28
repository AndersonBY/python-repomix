"""Tree-sitter query for Java code analysis."""

# Java tree-sitter query for extracting key code elements
query_java = """
; Comments
(line_comment) @comment
(block_comment) @comment

; Import statements
(import_declaration
  .
  (identifier) @name.reference.module) @definition.import

(package_declaration
  .
  (identifier) @name.reference.module) @definition.import

; Class definitions
(class_declaration
  name: (identifier) @name.definition.class) @definition.class

; Method definitions
(method_declaration
  name: (identifier) @name.definition.method) @definition.method

; Interface definitions
(interface_declaration
  name: (identifier) @name.definition.interface) @definition.interface
"""
