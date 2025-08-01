"""Tree-sitter query for Go code analysis."""

# Go tree-sitter query for extracting key code elements
query_go = """
; Comments
(comment) @comment

; Package declaration
(package_clause
  (package_identifier) @name.definition.package) @definition.package

; Import declarations
(import_declaration) @definition.import

; Function declarations
(function_declaration
  name: (identifier) @name.definition.function) @definition.function

; Method declarations (with receivers)
(method_declaration
  receiver: (parameter_list
    (parameter_declaration
      name: (identifier)? @receiver.name
      type: (_) @receiver.type))
  name: (identifier) @name.definition.method) @definition.method

; Type declarations
(type_declaration
  (type_spec
    name: (type_identifier) @name.definition.type)) @definition.type

; Interface declarations
(type_declaration
  (type_spec
    name: (type_identifier) @name.definition.interface
    type: (interface_type))) @definition.interface

; Struct declarations
(type_declaration
  (type_spec
    name: (type_identifier) @name.definition.struct
    type: (struct_type))) @definition.struct

; Variable declarations
(var_declaration
  (var_spec
    name: (identifier) @name.definition.variable)) @definition.var

; Constant declarations
(const_declaration
  (const_spec
    name: (identifier) @name.definition.constant)) @definition.const

; Short variable declarations
(short_var_declaration
  left: (expression_list
    (identifier) @name.definition.variable)) @definition.var.short

; Function types (for function variables)
(var_declaration
  (var_spec
    name: (identifier) @name.definition.function
    type: (function_type))) @definition.function.type

; Channel type declarations
(type_declaration
  (type_spec
    name: (type_identifier) @name.definition.channel
    type: (channel_type))) @definition.channel

; Map type declarations
(type_declaration
  (type_spec
    name: (type_identifier) @name.definition.map
    type: (map_type))) @definition.map

; Slice type declarations
(type_declaration
  (type_spec
    name: (type_identifier) @name.definition.slice
    type: (slice_type))) @definition.slice

; Pointer type declarations
(type_declaration
  (type_spec
    name: (type_identifier) @name.definition.pointer
    type: (pointer_type))) @definition.pointer

; Embedded fields in structs
(struct_type
  (field_declaration
    name: (identifier)? @name.definition.field
    type: (_) @field.type)) @definition.field

; Interface methods
(interface_type
  (method_spec
    name: (identifier) @name.definition.interface.method)) @definition.interface.method

; Init functions
(function_declaration
  name: (identifier) @init
  (#eq? @init "init")) @definition.init

; Main function
(function_declaration
  name: (identifier) @main
  (#eq? @main "main")) @definition.main
"""
