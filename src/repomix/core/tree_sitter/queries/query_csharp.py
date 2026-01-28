"""Tree-sitter query for C# code analysis."""

# C# tree-sitter query for extracting key code elements
query_csharp = """
; Comments
(comment) @comment

; Using statements
(using_directive) @definition.import

; Namespace definitions
(namespace_declaration
  name: (identifier) @name.definition.namespace) @definition.namespace

; Class definitions
(class_declaration
  name: (identifier) @name.definition.class) @definition.class

; Interface definitions
(interface_declaration
  name: (identifier) @name.definition.interface) @definition.interface

; Struct definitions
(struct_declaration
  name: (identifier) @name.definition.class) @definition.class

; Enum definitions
(enum_declaration
  name: (identifier) @name.definition.class) @definition.class

; Method definitions
(method_declaration
  name: (identifier) @name.definition.method) @definition.method

; Property definitions
(property_declaration
  name: (identifier) @name.definition.property) @definition.property

; Constructor definitions
(constructor_declaration
  name: (identifier) @name.definition.constructor) @definition.constructor
"""
