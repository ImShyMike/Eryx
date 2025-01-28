"""
Module to pretty print a class instance for debugging. (the code is actual garbage but it works)
"""

from colorama import Fore

from eryx.frontend.parser import Statement


# https://stackoverflow.com/questions/395735/how-to-check-whether-a-variable-is-a-class-or-not
def isclass(cls):
    """Check if a variable is a class."""
    return str(type(cls)).startswith("<class") and hasattr(cls, "__weakref__")


def isenum(cls):
    """Check if a variable is an enum."""
    return str(type(cls)).startswith("<enum") and hasattr(cls, "__weakref__")


def isfunction(func):
    """Check if a variable is a function."""
    return str(type(func)) == "<class 'function'>"

def fmt_pos(node: Statement) -> str:
    """Format position."""
    return f" (Ln {node.position[0]}, Col {node.position[1] - node.position[2]})"


COLOR_DICT = {
    "class": Fore.MAGENTA,
    "enum": Fore.CYAN,
    "key": Fore.BLUE,
    "str": Fore.GREEN,
    "int": Fore.YELLOW,
    "float": Fore.YELLOW,
    "bool": Fore.RED,
    "function": Fore.CYAN,
    "NoneType": Fore.RED,
}


def get_color(class_instance):
    """Helper function to get the color of a value type."""
    # Extra check for enums
    if isenum(class_instance):
        return COLOR_DICT["enum"]
    # Class colors
    return COLOR_DICT.get(type(class_instance).__name__, Fore.RESET)


def handle_array(
    val, use_color, use_newlines, indent, _tabs, is_tuple=False, is_set=False
):
    """Helper function to handle lists, tuples and sets."""
    string = "{" if is_set else "[" if not is_tuple else "("
    if use_newlines:
        string += f"{' ' * (indent * (_tabs + 1))}"

    for i, item in enumerate(val):
        if isclass(item):
            if i > 0:
                string += ","
                if use_newlines:
                    string += f"\n{' ' * (indent * (_tabs + 1))}"

            if use_newlines:
                string += f"\n{' ' * (indent * (_tabs + 1))}"

            string += str(
                pprint(
                    item,
                    print_output=False,
                    use_color=use_color,
                    use_newlines=use_newlines,
                    indent=indent,
                    _tabs=_tabs + 1,
                )
            )
        else:
            if i > 0:
                string += ","
                if not use_newlines:
                    string += " "

            if use_newlines:
                string += f"\n{' ' * (indent * (_tabs + 1))}"

            if isinstance(item, (list, tuple, set)):
                # If list, set or tuple, call handle_array
                string += handle_array(
                    item,
                    use_color,
                    use_newlines,
                    indent,
                    _tabs + 1,
                    is_tuple=isinstance(item, tuple),
                    is_set=isinstance(item, set),
                )
            elif isinstance(item, dict):
                # If dict, call handle_dict
                string += handle_dict(item, use_color, use_newlines, indent, _tabs + 1)
            elif isinstance(item, str):
                # If string, call handle_str
                string += handle_str(item, use_color)
            elif isfunction(item):
                # If function, add the function name
                string += (
                    get_color(item) + f"{val.__name__}" + Fore.RESET
                    if use_color
                    else "" + "()"
                )
            else:
                # Else add the value with color
                string += (
                    (get_color(item) if use_color else "")
                    + str(item)
                    + (Fore.RESET if use_color else "")
                )
    if use_newlines:
        string += f"\n{' ' * (indent * (_tabs))}"
    string += "}" if is_set else "]" if not is_tuple else ")"
    return string


def handle_dict(val, use_color, use_newlines, indent, _tabs):
    """Helper function to handle dictionaries."""
    string = "{"
    if use_newlines:
        string += f"{' ' * (indent * (_tabs + 1))}"

    for i, (key, value) in enumerate(val.items()):
        if use_newlines:
            string += f"\n{' ' * (indent * (_tabs + 1))}"
        if use_color:
            string += COLOR_DICT["key"]
        string += f"{key}"
        if use_color:
            string += Fore.RESET
        string += ": "

        if use_color:
            string += get_color(value)

        if isclass(value):
            # If class, recursively call pprint
            string += str(
                pprint(
                    value,
                    print_output=False,
                    use_color=use_color,
                    use_newlines=use_newlines,
                    indent=indent,
                    _tabs=_tabs + 1,
                )
            )
        elif isinstance(value, (list, tuple, set)):
            # If list, set or tuple, call handle_array
            string += handle_array(
                value,
                use_color,
                use_newlines,
                indent,
                _tabs + 1,
                is_tuple=isinstance(value, tuple),
                is_set=isinstance(value, set),
            )
        elif isinstance(value, dict):
            # If dict, call handle_dict
            string += handle_dict(value, use_color, use_newlines, indent, _tabs + 1)
        elif isinstance(value, str):
            # If string, call handle_str
            string += handle_str(value, use_color)
        elif isfunction(val):
            # If function, add the function name
            string += (
                get_color(val) + f"{val.__name__}" + Fore.RESET
                if use_color
                else "" + "()"
            )
        else:
            # Else add the value with color
            string += (
                (get_color(value) if use_color else "")
                + str(value)
                + (Fore.RESET if use_color else "")
            )

        if use_color:
            string += Fore.RESET

        if i + 1 < len(val):
            string += ","
            if not use_newlines:
                string += " "

    string += f"\n{' ' * (indent * (_tabs))}" + "}"
    return string


def handle_str(val, use_color):
    """Helper function to handle strings."""
    if use_color:
        return f'{get_color(val)}"{val}"{Fore.RESET}'
    return f'"{val}"'


def pprint(
    class_instance,
    print_output: bool = True,
    use_color: bool = True,
    use_newlines: bool = True,
    indent: int = 2,
    _tabs=0,
) -> str | None:
    """
    Pretty print a class instance.
    """

    if not isclass(class_instance):
        raise TypeError("Argument must be a class instance.")

    # Get the properties of the class (excluding dunder methods)
    properties = list(filter(lambda x: not x.startswith("__"), dir(class_instance)))
    string = ""
    # Add color for the class name
    if use_color:
        string += COLOR_DICT["class"]
    # Add the class name
    string += f"{type(class_instance).__name__}"

    # Reset color and add an opening parenthesis
    if use_color:
        string += Fore.RESET
    string += "("

    # Loop through the properties
    for n, class_property in enumerate(properties):
        # Get the value of the property
        val = getattr(class_instance, class_property)

        # Add newlines and indentation
        if use_newlines:
            string += f"\n{' ' * (indent * (_tabs + 1))}"

        # Add color
        if use_color:
            string += COLOR_DICT["key"]

        # Add the property name
        string += f"{class_property}"

        if use_color:
            string += Fore.RESET
        string += ": "

        # Add color for the value
        if use_color:
            string += get_color(val)

        if isclass(val):
            # If class, recursively call pprint
            string += str(
                pprint(
                    val,
                    print_output=False,
                    use_color=use_color,
                    use_newlines=use_newlines,
                    indent=indent,
                    _tabs=_tabs + 1,
                )
            )
        elif isinstance(val, (list, tuple, set)):
            # If list, set or tuple, call handle_array
            string += handle_array(
                val,
                use_color,
                use_newlines,
                indent,
                _tabs + 1,
                is_tuple=isinstance(val, tuple),
                is_set=isinstance(val, set),
            )
        elif isinstance(val, dict):
            # If dict, call handle_dict
            string += handle_dict(val, use_color, use_newlines, indent, _tabs + 1)
        elif isinstance(val, str):
            # If string, call handle_str
            string += handle_str(val, use_color)
        elif isfunction(val):
            # If function, add the function name
            string += (
                get_color(val) + f"{val.__name__}" + Fore.RESET
                if use_color
                else "" + "()"
            )
        else:
            # Else add the value with color
            string += (
                (get_color(val) if use_color else "")
                + str(val)
                + (Fore.RESET if use_color else "")
            )

        # Reset color
        if use_color:
            string += Fore.RESET

        # Add a comma if not the last property
        if n + 1 < len(properties):
            string += ","
            if not use_newlines:
                string += " "

    # Add newlines and indentation and close the class
    if use_newlines:
        string += f"\n{' ' * (indent * _tabs)})"
    else:
        string += ")"

    # Print or return the string
    if not print_output:
        return string
    print(string)
    return None
