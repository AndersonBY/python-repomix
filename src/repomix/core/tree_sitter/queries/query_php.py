"""Tree-sitter query for PHP code analysis."""

# PHP tree-sitter query for extracting key code elements
query_php = """
; Comments
(comment) @comment

; Use statements
(namespace_use_declaration) @definition.import

; Namespace definitions
(namespace_definition
  name: (namespace_name) @name.definition.namespace) @definition.namespace

; Class definitions
(class_declaration
  name: (name) @name.definition.class) @definition.class

; Interface definitions
(interface_declaration
  name: (name) @name.definition.interface) @definition.interface

; Trait definitions
(trait_declaration
  name: (name) @name.definition.trait) @definition.trait

; Function definitions
(function_definition
  name: (name) @name.definition.function) @definition.function

; Method definitions
(method_declaration
  name: (name) @name.definition.method) @definition.method
"""
