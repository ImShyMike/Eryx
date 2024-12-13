"""
    Class to pretty print a class instance for debugging. (the code is actual garbage but it works)
"""

import os

from colorama import Fore, init


# https://stackoverflow.com/questions/395735/how-to-check-whether-a-variable-is-a-class-or-not
def isclass(cls):
    """Check if a variable is a class."""
    return str(type(cls)).startswith("<class") and hasattr(cls, "__weakref__")

def isenum(cls):
    """Check if a variable is an enum."""
    return str(type(cls)).startswith("<enum") and hasattr(cls, "__weakref__")

COLOR_DICT = {
    "class": Fore.MAGENTA,
    "enum": Fore.CYAN,
    "key": Fore.BLUE,
    "str": Fore.GREEN,
    "int": Fore.YELLOW,
    "float": Fore.YELLOW,
    "bool": Fore.RED,
    "NoneType": Fore.RED,
}


def get_color(class_instance):
    """Helper function to get the color of a value type."""
    # Extra check for enums
    if isenum(class_instance):
        return COLOR_DICT["enum"]
    # Class colors
    return COLOR_DICT.get(type(class_instance).__name__, Fore.WHITE)


def pprint(
    class_instance,
    print_output: bool = True,
    use_color: bool = True,
    use_newlines: bool = True,
    spaces_count: int = 2,
    _tabs=0,
):
    """Pretty print a class instance."""

    if not isclass(class_instance):
        raise TypeError("Argument must be a class instance.")

    properties = list(filter(lambda x: not x.startswith("__"), dir(class_instance)))
    string = ""
    if use_color:
        string += COLOR_DICT["class"]
    string += f"{type(class_instance).__name__}"

    if use_color:
        string += Fore.WHITE
    string += "("

    for n, property in enumerate(properties):
        val = getattr(class_instance, property)

        if use_newlines:
            string += f'\n{" "*(spaces_count*(_tabs+1))}'

        if use_color:
            string += COLOR_DICT["key"]
        string += f"{property}"

        if use_color:
            string += Fore.WHITE
        string += ": "

        if use_color:
            string += get_color(val)

        if isinstance(val, str):
            string += '"'

        if isclass(val):
            string += pprint(
                val,
                print_output=False,
                use_color=use_color,
                use_newlines=use_newlines,
                spaces_count=spaces_count,
                _tabs=_tabs + 1,
            )
        elif isinstance(val, list):
            string += "[\n"
            if use_newlines:
                string += f"{' '*(spaces_count*(_tabs+2))}"

            for i, item in enumerate(val):
                if isclass(item):
                    if i > 0:
                        string += ","
                        if use_newlines:
                            string += f"\n{' '*(spaces_count*(_tabs+2))}"

                    string += pprint(
                        item,
                        print_output=False,
                        use_color=use_color,
                        use_newlines=use_newlines,
                        spaces_count=spaces_count,
                        _tabs=_tabs + 2,
                    )
                else:
                    if isinstance(item, str):
                        string += '"'
                    string += str(item)
                    if isinstance(item, str):
                        string += '"'
                    if i + 1 < len(val):
                        string += ", "
            string += "]"
        else:
            string += str(val)

        if isinstance(val, str):
            string += '"'

        if use_color:
            string += Fore.WHITE

        if n + 1 < len(properties):
            string += ", "

    if use_newlines:
        string += f"\n{' '*(spaces_count*_tabs)})"
    else:
        string += ")"

    if print_output:
        print(string)
    else:
        return string


if __name__ == "__main__":
    if os.name == "nt":
        init(autoreset=True)

    class Test:
        """Dummy class."""

        def __init__(self, prop, cls):
            self.prop = prop
            self.number = 7
            self.lst = {"abc": 92, "Foo": "Bar"}
            self.abc = "test"
            self.cls = cls

    class Test2:
        """Dummy class 2."""

        def __init__(self):
            self.abc = 6

    t = Test("abc", Test2())
    pprint(t)
