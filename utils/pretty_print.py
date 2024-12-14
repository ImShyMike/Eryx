"""
Class to pretty print a class instance for debugging. (the code is actual garbage but it works)
"""

import os

from colorama import Fore, init

if os.name == "nt":
    init(autoreset=True)


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
    return COLOR_DICT.get(type(class_instance).__name__, Fore.WHITE)


def handle_array(
    val, use_color, use_newlines, indent, _tabs, is_tuple=False, is_set=False
):
    """Helper function to handle lists, tuples and sets."""
    string = "{" if is_set else "[" if not is_tuple else "("
    if use_newlines:
        string += f"{' '*(indent*(_tabs+1))}"

    for i, item in enumerate(val):
        if isclass(item):
            if i > 0:
                string += ","
                if use_newlines:
                    string += f"\n{' '*(indent*(_tabs+1))}"

            if use_newlines:
                string += f"\n{' '*(indent*(_tabs+1))}"

            string += pprint(
                item,
                print_output=False,
                use_color=use_color,
                use_newlines=use_newlines,
                indent=indent,
                _tabs=_tabs + 1,
            )
        else:
            if i > 0:
                string += ","
                if not use_newlines:
                    string += " "

            if use_newlines:
                string += f"\n{' '*(indent*(_tabs+1))}"

            if isinstance(item, list):
                # If list, call handle_array
                string += handle_array(item, use_color, use_newlines, indent, _tabs + 1)
            elif isinstance(item, tuple):
                # If tuple, call handle_array with is_tuple=True
                string += handle_array(
                    item, use_color, use_newlines, indent, _tabs + 1, is_tuple=True
                )
            elif isinstance(item, dict):
                # If dict, call handle_dict
                string += handle_dict(item, use_color, use_newlines, indent, _tabs + 1)
            elif isinstance(item, set):
                # If set, call handle_array with is_set=True
                string += handle_array(
                    item, use_color, use_newlines, indent, _tabs + 1, is_set=True
                )
            elif isinstance(item, str):
                # If string, call handle_str
                string += handle_str(item, use_color)
            elif isfunction(val):
                # If function, add the function name
                string += get_color(val) + f"{val.__name__}" + Fore.WHITE + "()"
            else:
                # Else add the value with color
                string += get_color(item) + str(item) + Fore.WHITE
    if use_newlines:
        string += f"\n{' '*(indent*(_tabs))}"
    string += "}" if is_set else "]" if not is_tuple else ")"
    return string


def handle_dict(val, use_color, use_newlines, indent, _tabs):
    """Helper function to handle dictionaries."""
    string = "{"
    if use_newlines:
        string += f"{' '*(indent*(_tabs+1))}"

    for i, (key, value) in enumerate(val.items()):
        if use_newlines:
            string += f"\n{' '*(indent*(_tabs+1))}"
        if use_color:
            string += COLOR_DICT["key"]
        string += f"{key}"
        if use_color:
            string += Fore.WHITE
        string += ": "

        if use_color:
            string += get_color(value)

        if isclass(value):
            # If class, recursively call pprint
            string += pprint(
                value,
                print_output=False,
                use_color=use_color,
                use_newlines=use_newlines,
                indent=indent,
                _tabs=_tabs + 1,
            )
        elif isinstance(value, list):
            # If list, call handle_array
            string += handle_array(value, use_color, use_newlines, indent, _tabs + 1)
        elif isinstance(value, dict):
            # If dict, call handle_dict
            string += handle_dict(value, use_color, use_newlines, indent, _tabs + 1)
        elif isinstance(value, tuple):
            # If tuple, call handle_array with is_tuple=True
            string += handle_array(
                value, use_color, use_newlines, indent, _tabs + 1, is_tuple=True
            )
        elif isinstance(value, set):
            # If set, call handle_array with is_set=True
            string += handle_array(
                value, use_color, use_newlines, indent, _tabs + 1, is_set=True
            )
        elif isinstance(value, str):
            # If string, call handle_str
            string += handle_str(value, use_color)
        elif isfunction(val):
            # If function, add the function name
            string += get_color(val) + f"{val.__name__}" + Fore.WHITE + "()"
        else:
            # Else add the value with color
            string += get_color(value) + str(value) + Fore.WHITE

        if use_color:
            string += Fore.WHITE

        if i + 1 < len(val):
            string += ","
            if not use_newlines:
                string += " "

    string += f"\n{' '*(indent*(_tabs))}" + "}"
    return string


def handle_str(val, use_color):
    """Helper function to handle strings."""
    if use_color:
        return f'"{val}"'
    return val


def pprint(
    class_instance,
    print_output: bool = True,
    use_color: bool = True,
    use_newlines: bool = True,
    indent: int = 2,
    _tabs=0,
):
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
        string += Fore.WHITE
    string += "("

    # Loop through the properties
    for n, class_property in enumerate(properties):
        # Get the value of the property
        val = getattr(class_instance, class_property)

        # Add newlines and indentation
        if use_newlines:
            string += f'\n{" "*(indent*(_tabs+1))}'

        # Add color
        if use_color:
            string += COLOR_DICT["key"]

        # Add the property name
        string += f"{class_property}"

        if use_color:
            string += Fore.WHITE
        string += ": "

        # Add color for the value
        if use_color:
            string += get_color(val)

        if isclass(val):
            # If class, recursively call pprint
            string += pprint(
                val,
                print_output=False,
                use_color=use_color,
                use_newlines=use_newlines,
                indent=indent,
                _tabs=_tabs + 1,
            )
        elif isinstance(val, list):
            # If list, call handle_array
            string += handle_array(val, use_color, use_newlines, indent, _tabs + 1)
        elif isinstance(val, dict):
            # If dict, call handle_dict
            string += handle_dict(val, use_color, use_newlines, indent, _tabs + 1)
        elif isinstance(val, tuple):
            # If tuple, call handle_array with is_tuple=True
            string += handle_array(
                val, use_color, use_newlines, indent, _tabs + 1, is_tuple=True
            )
        elif isinstance(val, set):
            # If set, call handle_array with is_set=True
            string += handle_array(
                val, use_color, use_newlines, indent, _tabs + 1, is_set=True
            )
        elif isinstance(val, str):
            # If string, call handle_str
            string += handle_str(val, use_color)
        elif isfunction(val):
            # If function, add the function name
            string += get_color(val) + f"{val.__name__}" + Fore.WHITE + "()"
        else:
            # Else add the value with color
            string += get_color(val) + str(val) + Fore.WHITE

        # Reset color
        if use_color:
            string += Fore.WHITE

        # Add a comma if not the last property
        if n + 1 < len(properties):
            string += ","
            if not use_newlines:
                string += " "

    # Add newlines and indentation and close the class
    if use_newlines:
        string += f"\n{' '*(indent*_tabs)})"
    else:
        string += ")"

    # Print or return the string
    if print_output:
        print(string)
    else:
        return string


if __name__ == "__main__":

    class Test:
        """Dummy class."""

        def __init__(self, prop, cls):
            self.prop = prop
            self.number = 7
            self.dct = {"abc": 92, "Foo": "Bar"}
            self.lst = [1, 2, 3, 4]
            self.abc = "test"
            self.cls = cls

    class Test2:
        """Dummy class 2."""

        def __init__(self, cls=None):
            self.abc = 6
            self.dict2 = {"Foo": "Bar"}
            self.cls = cls

    class Test3:
        """Dummy class 3 with various types."""

        def __init__(self):
            self.string = "Hello"
            self.number = 42
            self.float_num = 3.14
            self.bool_val = True
            self.nested_list = [Test2(), 2, [3, 4], {"key": "value"}, (5, 6), set([7, 8])]
            self.nested_dict = {
                "key1": "value1",
                "key2": [1, 2, 3],
                "key3": {"key": "value"},
                "key4": Test2(),
            }

    # Test with nested class instances
    t = Test("abc", Test2(Test2()))
    print("Test 1:")
    pprint(t)

    # Test with a class instance with a class instance
    t2 = Test2(Test3())
    print("\nTest 2:")
    pprint(t2)

    # Test with a class instance with various types
    t3 = Test3()
    print("\nTest 3:")
    pprint(t3)
