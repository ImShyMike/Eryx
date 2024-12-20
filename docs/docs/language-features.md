# Language features

Eryx supports a wide range of features that are also present in other languages like python/javascript.
Bellow are of all features currently supported by Eryx.

## Comments
Single line comments are supported with the `#` character and can be stopped early with the `;` character.
```sh linenums="1"
print("Hello,") # This is a comment print("This will not be printed")
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

## Functions
Functions can be declared using the `func` keyword.

```C linenums="1"
func add(x, y) {
    return x + y; # Return statements must end in a semicolon
}
print(add(1, 2)) # Output: 3
```

There are also many reserved builtin functions:

* **print**: Print all values passed to it
* **time**: Get the current time in seconds since the Epoch
* **input**: Get user input as a string, optionally prompt with a message
* **readfile**: Read the contents of a file as a string
* **len**: Get the length of a string, array, or object
* **exit**: Exit the program, optionally with a status code
* **str**: Convert a value to its string representation
* **int**: Convert a value to an integer
* **bool**: Convert a value to a boolean
* **array**: Create a new array from the given values
* **type**: Get the type of the given value
* **sum**: Get the sum of an array of numbers
* **min**: Get the minimum value from an array of numbers
* **max**: Get the maximum value from an array of numbers

## Operators
Currently, all supported operators are:

### Arithmetic

* **+** Add
* **-** Subtract
* **\*** Multiply
* **/** Divide
* **%** Modulo
* **\*\*** Power

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

```C linenums="1"
if (1 == 1) {
    print("This will be printed")
} else {
    print("This will not be printed")
}
```