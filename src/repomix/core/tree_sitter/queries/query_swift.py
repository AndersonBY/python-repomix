"""Tree-sitter query for Swift code analysis."""

# Swift tree-sitter query for extracting key code elements
query_swift = """
; Comments
(comment) @comment
(multiline_comment) @comment

; Import statements
(import_declaration) @definition.import

; Class definitions
(class_declaration
  name: (type_identifier) @name.definition.class) @definition.class

; Struct definitions
(struct_declaration
  name: (type_identifier) @name.definition.class) @definition.class

; Enum definitions
(enum_declaration
  name: (type_identifier) @name.definition.class) @definition.class

; Protocol definitions
(protocol_declaration
  name: (type_identifier) @name.definition.interface) @definition.interface

; Function definitions
(function_declaration
  name: (simple_identifier) @name.definition.function) @definition.function

; Extension definitions
(extension_declaration
  (type_identifier) @name.definition.extension) @definition.extension

; Typealias definitions
(typealias_declaration
  name: (type_identifier) @name.definition.type) @definition.type
"""
