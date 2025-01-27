# Language features

Eryx supports a wide range of features that are also present in other languages like python/javascript.
Bellow are of all features currently supported by Eryx.

## Comments

Single line comments are supported with the `#` character and can be stopped early with the `;` character.

```sh linenums="1"
print("Hello, "); # This is a comment print("This will not be printed")
print("World!"); # This is also a comment ; print("This will be printed")
```

!!! note "Stopping line comments"
The `;` above makes it so the code after it is also executed, making the output:

    ```C linenums="1"
    Hello,
    World!
    This will be printed
    ```

## Variable declarations

Mutable variables and constants are supported.

```sh linenums="1"
let var = 1; # This is a mutable variable
const constant = true; # This is a constant
var = 100; # Redefining a variable's value does not need a semicolon
```

!!! note "Semicolon usage"
All variable declarations **must** end in a semicolon (`;`)

## Variable deletion

Variables can be deleted with the `del` keyword:

```sh linenums="1"
const var = 1; # Declare a constant variable
del var; # Delete it so it can be redeclared
```

## Value types

All currently suppoted value types are:

- Numbers (currently there isn't a differnce between integers and floats)
- Strings
- Booleans
- Arrays
- Dictionaries/Objects
- Nulls

```sh linenums="1"
let num = 1; # This is a number
let neg_num = -1; # This is a negative number
let float_num = 3.14; # This is a float
let boolean = true; # This is a boolean
let string = "Hello, World!"; # This is a string
let arr = [1, 2, 3, 5]; # This is an array
let dict = {key: "value", num: 3}; # This is a dictionary/object
let null_val = null; # This is a null
```

## Importing

Importing is done with the `import` keyword.

```sh linenums="1"
import "test.erx"; # Imports a file name 'test.eryx'
from "test.eryx" import ["add", "pi"]; # Imports the function 'add' and variable 'pi' from 'test.eryx'
import "math" as "meth"; # Imports the builtin 'math' module as 'meth'
```

!!! note "Builtins"
Builtin modules and installed packages are imported without the ".eryx" (example: "math")

## Functions

Functions can be declared using the `func` keyword.

```C linenums="1"
func add(x, y) {
    return x + y; # Return statements must end in a semicolon and can be empty
}
print(add(1, 2)); # Output: 3
```

## Builtin functions

| Function                                                             | Description                                                              |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **print(** ... **)** -> null                                         | Print all values passed to it.                                           |
| **input(** text?: str **)** -> str                                   | Get user input as a string, optionally prompt with a message.            |
| **len(** item: str \| array \| object **)** -> number                | Get the length of a string, array, or object.                            |
| **exit(** code?: number **)** -> null                                | Exit the program, optionally with a status code.                         |
| **str(** value?: any **)** -> str                                    | Convert a value to its string representation.                            |
| **int(** value?: str **)** -> number                                 | Convert a value to an integer.                                           |
| **bool(** value?: any **)** -> number                                | Convert a value to a boolean.                                            |
| **array(** ... \| string: str **)** -> array                         | Create a new array from the given values or turn a string into an array. |
| **type(** value **)** -> str                                         | Get the type of the given value.                                         |
| **range(** start: number, end?: number, step?: number **)** -> array | Generates an array from start to end with step.                          |

!!! note "Values"
Values containing '?' are optional and '...' refers to any amount of arguments.

## Builtin modules

Builtin modules can be imported using `import` (without ".eryx")

### math

| Function                                                | Description                                                 |
| ------------------------------------------------------- | ----------------------------------------------------------- |
| **log(** x: number, base? **)** -> number               | Get the logarithm of a number with the specified base.      |
| **sqrt(** x: number **)** -> number                     | Get the square root of a number.                            |
| **random()** -> number                                  | Get a random number between 0 and 1.                        |
| **round(** x: number, digits?: number **)** -> number   | Round a number to the specified number of digits.           |
| **sum(** array: array **)** -> number                   | Get the sum of an array of numbers.                         |
| **min(** array: array **)** -> number                   | Get the minimum value in an array of numbers.               |
| **max(** array: array **)** -> number                   | Get the maximum value in an array of numbers.               |
| **abs(** x: number **)** -> number                      | Get the absolute value of a number.                         |
| **pow(** base: number, exponent: number **)** -> number | Get the result of raising a base to an exponent.            |
| **log10(** x: number **)** -> number                    | Get the base-10 logarithm of a number.                      |
| **sin(** x: number **)** -> number                      | Get the sine of a number.                                   |
| **cos(** x: number **)** -> number                      | Get the cosine of a number.                                 |
| **tan(** x: number **)** -> number                      | Get the tangent of a number.                                |
| **asin(** x: number **)** -> number                     | Get the arcsine of a number.                                |
| **acos(** x: number **)** -> number                     | Get the arccosine of a number.                              |
| **atan(** x: number **)** -> number                     | Get the arctangent of a number.                             |
| **floor(** x: number **)** -> number                    | Get the largest integer less than or equal to a number.     |
| **ceil(** x: number **)** -> number                     | Get the smallest integer greater than or equal to a number. |
| **factorial(** x: number **)** -> number                | Get the factorial of a number.                              |

### file

| Function                                              | Description                  |
| ----------------------------------------------------- | ---------------------------- |
| **read(** filename: str **)** -> str                  | Read the contents of a file. |
| **write(** filename: str, content: str **)** -> null  | Write content to a file.     |
| **append(** filename: str, content: str **)** -> null | Append content to a file.    |
| **exists(** filename: str **)** -> bool               | Check if a file exists.      |
| **delete(** filename: str **)** -> null               | Delete a file.               |
| **copy(** source: str, destination: str **)** -> null | Copy a file.                 |
| **move(** source: str, destination: str **)** -> null | Move a file.                 |
| **list(** directory: str **)** -> array               | List files in a directory.   |
| **size(** filename: str **)** -> number               | Get the size of a file.      |

### http

| Function                                                    | Description                             |
| ----------------------------------------------------------- | --------------------------------------- |
| **get(** url: str **)** -> object{data, status}             | Make a GET request to a URL.            |
| **post(** url: str, data: str **)** -> object{data, status} | Make a POST request to a URL with data. |
| **put(** url: str, data: str **)** -> object{data, status}  | Make a PUT request to a URL with data.  |
| **delete(** url: str **)** -> object{data, status}          | Make a DELETE request to a URL.         |
| **urlencode(** data: str **)** -> str                       | URL-encode a string.                    |
| **urldecode(** data: str **)** -> str                       | URL-decode a string.                    |

### time

| Function                                 | Description                                      |
| ---------------------------------------- | ------------------------------------------------ |
| **time()** -> number                     | Get the current time in seconds since the epoch. |
| **sleep(** seconds: number **)** -> null | Sleep for a specified number of seconds.         |
| **format(** time: number **)** -> str    | Format a time value as a string.                 |
| **timezone_offset()** -> number          | Get the timezone offset in seconds.              |

### string

| Function                                                         | Description                                     |
| ---------------------------------------------------------------- | ----------------------------------------------- |
| **split(** string: str, separator: str **)** -> array            | Split a string by a separator.                  |
| **join(** array: array, separator: str **)** -> str              | Join an array of strings with a separator.      |
| **replace(** string: str, search: str, replace: str **)** -> str | Replace occurrences of a substring in a string. |
| **contains(** string: str, search: str **)** -> bool             | Check if a string contains a substring.         |

### array

| Function                                            | Description                                      |
| --------------------------------------------------- | ------------------------------------------------ |
| **push(** array: array, value: any **)** -> null    | Add a value to the end of an array.              |
| **pop(** array: array **)** -> any                  | Remove and return the last value from an array.  |
| **shift(** array: array **)** -> any                | Remove and return the first value from an array. |
| **unshift(** array: array, value: any **)** -> null | Add a value to the beginning of an array.        |
| **sort(** array: array **)** -> null                | Sort an array of numbers.                        |

### os

| Function                                               | Description                                                                                        |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| **cwd()** -> str                                       | Get the current working directory.                                                                 |
| **chdir(** directory: str **)** -> null                | Change the current working directory.                                                              |
| **env(** variable?: str **)** -> str \| array[str]     | Get the value of an environment variable or all environment variables if no variable is specified. |
| **exec(** command: str **)** -> object{output, status} | Executes a system command and return the result.                                                   |

### json

| Function                                   | Description                        |
| ------------------------------------------ | ---------------------------------- |
| **parse(** string: str **)** -> object     | Parse a string into a JSON object. |
| **stringify(** object: object **)** -> str | Turn a JSON object into a string.  |

## Classes

Classes can be made using the `class` keyword:

```C linenums="1"
# They can have initializeable arguments
class Clock {
    time: Number # Type hints are done using a colon
}

let clock = Clock(0);
clock.time = 100;

print(clock); # Output: 100
```

```C linenums="1"
# They can also have pre-declared variables
class Clock {
    time: Number = 0
}

print(clock.time); # Output: 0

clock.time = 100; # This will set the value permanently

print(clock); # Output: 100
```

```C linenums="1"
# They can also have functions
class Maths {
    func sum(a: Number, b: Number) {
        return a + b;
    }
}

print(Maths.sum(10, 5)); # Output: 15
```

!!! note "Own property access"
Currently, there is no way to access properties from the class from within its own functions (like `self` (python) or `this` (javascript))

## Enums

Enums can be created using `enum`:

```C linenums="1"
# They can also have pre-declared variables
enum Colors {
    green
    blue
    red
    white
    yellow
}

print(Colors.green); # Output: green
```

## Operators

Currently, all supported operators are:

### Arithmetic

- **+** Add
- **-** Subtract
- **\*** Multiply
- **/** Divide
- **%** Modulo
- **\*\*** Power

!!! note "+ Operator"
The `+ (Add)` operator can also be used to concatenate strings, arrays and dictionaries/objects.

### Bitwise

- **^** XOR
- **&** AND
- **|** OR
- **<<** Left shift
- **>>** Right shift

### Logical

- **&&** And
- **||** Or

### Comparison

- **==** Equals
- **!=** Not equals
- **<** Smaller
- **>** Greater
- **<=** Smaller or equal
- **>=** Greater or equal

### In place

- **++** Add 1
- **--** Subtract 1
- **+=** Add
- **-=** Subtract
- **\*=** Multiply
- **/=** Divide
- **%=** Modulo
- **^=** XOR
- **&=** AND
- **|=** OR

!!! note "`++` and `--`"
The `++` and `--` operators are used **before** the variable (example: `++variable`).

## Control structures

### If/Else statements

```C linenums="1"
if (1 == 1) {
    print("This will be printed");
} else {
    print("This will not be printed");
}
```

### Loops

Infinite loops, while loops and for loops are supported.

!!! note "For Loops"
For loops can only iterate over arrays.

```C linenums="1"
loop {
    print("This will be printed forever!");
}

let value = 0;
const threshold = 3;
while (value < threshold) {
    value = value + 1

    print(value);
}

# For loops work by going over an iterator
for i in range(5) {
    print(i)
}
```

Supported keywords are:

- **break**: Exit the loop
- **continue**: Skip to the next loop iteration
