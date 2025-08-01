"""Tree-sitter query for JavaScript code analysis."""

# JavaScript tree-sitter query for extracting key code elements
query_javascript = """
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

; Arrow function assignments
(variable_declarator
  name: (identifier) @name.definition.function
  value: (arrow_function)) @definition.function

; Method definitions
(method_definition
  name: (property_identifier) @name.definition.method) @definition.method

; Variable declarations (const, let, var)
(variable_declaration
  (variable_declarator
    name: (identifier) @name.definition.variable)) @definition.variable

; Function expressions
(variable_declarator
  name: (identifier) @name.definition.function
  value: (function_expression)) @definition.function

; Generator functions
(generator_function_declaration
  name: (identifier) @name.definition.function) @definition.function.generator

; Async functions
(function_declaration
  "async"
  name: (identifier) @name.definition.function) @definition.function.async

; Constructor definitions
(method_definition
  name: (property_identifier) @constructor
  (#eq? @constructor "constructor")) @definition.constructor

; Getter definitions
(method_definition
  "get"
  name: (property_identifier) @name.definition.getter) @definition.getter

; Setter definitions
(method_definition
  "set"
  name: (property_identifier) @name.definition.setter) @definition.setter

; Object property assignments (for modules/objects)
(assignment_expression
  left: (member_expression
    property: (property_identifier) @name.definition.property)) @definition.property

; Immediately Invoked Function Expressions (IIFE)
(call_expression
  function: (parenthesized_expression
    (arrow_function))) @definition.iife

; CommonJS exports
(assignment_expression
  left: (member_expression
    object: (identifier) @module
    property: (property_identifier) @exports
    (#eq? @module "module")
    (#eq? @exports "exports"))) @definition.export

; CommonJS require statements
(variable_declarator
  name: (identifier) @name.definition.import
  value: (call_expression
    function: (identifier) @require
    (#eq? @require "require"))) @definition.import
"""
