# Language features

Eryx supports a wide range of features that are also present in other languages like python/javascript.
Bellow are of all features currently supported by Eryx.

## Comments
Single line comments are supported with the `#` character and can be stopped early with the `;` character.
```sh linenums="1"
print("Hello, ") # This is a comment print("This will not be printed")
print("World!") # This is also a comment ; print("This will be printed")
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
```C linenums="1"
let var = 1; # This is a mutable variable
const constant = true; # This is a constant
var = 100 # Redefining a variable's value does not need a semicolon
```
!!! note "Semicolon usage"
    All variable declarations **must** end in a semicolon (`;`)

## Value types
All currently suppoted value types are:

* Numbers (currently there isn't a differnce between integers and floats)
* Strings
* Booleans
* Arrays
* Dictionaries/Objects
* Nulls

```C linenums="1"
let num = 1; # This is a number
let neg_num = -1; # This is a negative number
let float_num = 3.14; # This is a float
let boolean = true; # This is a boolean
let string = "Hello, World!"; # This is a string
let arr = [1, 2, 3, 5]; # This is an array
let dict = {key: "value", num: 3} # This is a dictionary/object
let null_val = null; # This is a null
```

## Importing
Importing is done with the `import` keyword.

```C linenums="1"
import "test.erx" # Imports a file name 'test.eryx'
from "test.eryx" import ["add", "pi"] # Imports the function 'add' and variable 'pi' from 'test.eryx'
import "math" as "meth" # Imports the builtin 'math' module as 'meth'
```

!!! note "Builtins"
    Builtin modules and installed packages are imported without the ".eryx" (example: "math")

## Functions
Functions can be declared using the `func` keyword.

```C linenums="1"
func add(x, y) {
    return x + y; # Return statements must end in a semicolon and can be empty
}
print(add(1, 2)) # Output: 3
```

There are also many builtin functions:

!!! note "Values"
    Values containing '?' are optional and '...' reffers to any amount of arguments.

* **print(** ... **)**: Print all values passed to it
* **input(** text? **)**: Get user input as a string, optionally prompt with a message
* **len(** item **)**: Get the length of a string, array, or object
* **exit(** code? **)**: Exit the program, optionally with a status code
* **str(** value? **)**: Convert a value to its string representation
* **int(** value? **)**: Convert a value to an integer
* **bool(** value? **)**: Convert a value to a boolean
* **array(** ... or string **)**: Create a new array from the given values or turn a string into an array
* **type(** value **)**: Get the type of the given value


There are also many builtin modules:

- **time**:
    - **time()**: Get the current time in seconds since the Epoch
- **math**:
    - **sum(** array **)**: Get the sum of an array of numbers
    - **round(** number, n? **)**: Round a number to the n'th decimal place (default 0)
    - **min(** array **)**: Get the minimum value from an array of numbers
    - **max(** array **)**: Get the maximum value from an array of numbers
    - **random()**: Get a random number between 0 and 1
    - **pi**: The value for pi
- **file**:
    - **read(** filename **)**: Read the contents of a file as a string
    - **write(** filename, text **)**: Write to a file
    - **append(** filename, text **)**: Append to the contents of a file
- **http**: (WIP)
    - **get(** url **)**: Send a get request to a URL
    - **post(** url, data **)**: Send a post request with JSON data as a string to a URL

## Operators
Currently, all supported operators are:

### Arithmetic

* **+** Add
* **-** Subtract
* **\*** Multiply
* **/** Divide
* **%** Modulo
* **\*\*** Power

### Bitwise

* **^** XOR
* **&** AND
* **|** OR
* **<<** Left shift
* **>>** Right shift

### Logical

* **&&** And
* **||** Or

### Comparison

* **==** Equals
* **!=** Not equals
* **<** Smaller
* **>** Greater
* **<=** Smaller or equal
* **>=** Greater or equal

!!! note "+ Operator"
    The `+ (Add)` operator can also be used to concatenate strings, arrays and dictionaries/objects.

## Control structures
For now, the only supported control structures are:

### If/Else statements

```C linenums="1"
if (1 == 1) {
    print("This will be printed")
} else {
    print("This will not be printed")
}
```
