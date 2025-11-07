"""
TypedDict Generator - Convert JSON to Python TypedDict classes
"""
from typing import Any, Dict, List, Set, Tuple
import re


def to_pascal_case(name: str) -> str:
    """Convert string to PascalCase for class names."""
    # Remove special characters and split
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    parts = name.split('_')
    return ''.join(word.capitalize() for word in parts if word)


def infer_type(value: Any, key_name: str = "") -> Tuple[str, Set[str]]:
    """
    Infer Python type from a value.
    Returns (type_string, set_of_nested_classes)
    """
    nested_classes = set()
    
    if value is None:
        return "None", nested_classes
    elif isinstance(value, bool):
        return "bool", nested_classes
    elif isinstance(value, int):
        return "int", nested_classes
    elif isinstance(value, float):
        return "float", nested_classes
    elif isinstance(value, str):
        return "str", nested_classes
    elif isinstance(value, list):
        if not value:
            return "List[Any]", nested_classes
        
        # Infer type from all elements
        element_types = set()
        for item in value:
            item_type, item_nested = infer_type(item, key_name)
            element_types.add(item_type)
            nested_classes.update(item_nested)
        
        if len(element_types) == 1:
            return f"List[{element_types.pop()}]", nested_classes
        else:
            # Multiple types - use Union
            types_str = ", ".join(sorted(element_types))
            return f"List[Union[{types_str}]]", nested_classes
            
    elif isinstance(value, dict):
        # Create a nested TypedDict class
        class_name = to_pascal_case(key_name) if key_name else "NestedObject"
        nested_classes.add(class_name)
        return class_name, nested_classes
    else:
        return "Any", nested_classes


def generate_typeddict_class(
    class_name: str,
    data: Dict[str, Any],
    indent: int = 0
) -> Tuple[str, List[str]]:
    """
    Generate a TypedDict class definition from a dictionary.
    Returns (class_definition, list_of_nested_class_definitions)
    """
    indent_str = "    " * indent
    lines = []
    nested_defs = []
    required_imports = set()
    
    # Class definition
    lines.append(f"{indent_str}class {class_name}(TypedDict):")
    
    if not data:
        lines.append(f"{indent_str}    pass")
        return "\n".join(lines), nested_defs
    
    # Analyze all fields
    for key, value in data.items():
        type_str, nested_classes = infer_type(value, key)
        
        # Handle nested dictionaries - generate their classes first
        if isinstance(value, dict):
            nested_class_name = to_pascal_case(key)
            nested_def, sub_nested = generate_typeddict_class(
                nested_class_name, value, indent
            )
            nested_defs.append(nested_def)
            nested_defs.extend(sub_nested)
            type_str = nested_class_name
        
        # Add field to class
        # TypedDict uses key: type syntax
        lines.append(f"{indent_str}    {key}: {type_str}")
        
        # Track imports needed
        if "List[" in type_str:
            required_imports.add("List")
        if "Union[" in type_str:
            required_imports.add("Union")
        if "Any" in type_str:
            required_imports.add("Any")
    
    return "\n".join(lines), nested_defs


def json_to_typeddict(
    data: Any,
    root_class_name: str = "RootObject"
) -> str:
    """
    Convert JSON data to TypedDict class definitions.
    
    Args:
        data: Parsed JSON data (dict or list)
        root_class_name: Name for the root class
        
    Returns:
        Complete Python code with imports and class definitions
    """
    if not isinstance(data, (dict, list)):
        return f"# Error: Input must be a dict or list, got {type(data).__name__}"
    
    # Handle list at root
    if isinstance(data, list):
        if not data:
            return "# Error: Cannot generate TypedDict from empty list"
        # Use first element as template
        data = data[0]
        root_class_name = f"{root_class_name}Item"
    
    if not isinstance(data, dict):
        return f"# Error: List elements must be objects, got {type(data).__name__}"
    
    # Generate class definitions
    main_class, nested_classes = generate_typeddict_class(root_class_name, data)
    
    # Collect all required imports
    all_classes = [main_class] + nested_classes
    all_code = "\n\n".join(all_classes)
    
    required_imports = set()
    if "List[" in all_code:
        required_imports.add("List")
    if "Union[" in all_code:
        required_imports.add("Union")
    if "Any" in all_code:
        required_imports.add("Any")
    
    # Build final code
    output_lines = []
    
    # Add imports
    if required_imports:
        imports = ", ".join(sorted(required_imports))
        output_lines.append(f"from typing import {imports}, TypedDict")
    else:
        output_lines.append("from typing import TypedDict")
    
    output_lines.append("")
    output_lines.append("")
    
    # Add nested classes first (in reverse order so dependencies work)
    for nested_class in reversed(nested_classes):
        output_lines.append(nested_class)
        output_lines.append("")
        output_lines.append("")
    
    # Add main class
    output_lines.append(main_class)
    
    return "\n".join(output_lines)


def generate_from_json_string(
    json_str: str,
    class_name: str = "RootObject"
) -> str:
    """
    Helper function to parse JSON string and generate TypedDict.
    
    Args:
        json_str: JSON string
        class_name: Name for the root class
        
    Returns:
        Python TypedDict code or error message
    """
    import json
    from .parser import safe_parse
    
    try:
        data = safe_parse(json_str)
        if isinstance(data, str):
            return f"# Error: Could not parse input as JSON or Python literal"
        return json_to_typeddict(data, class_name)
    except Exception as e:
        return f"# Error generating TypedDict: {e}"
