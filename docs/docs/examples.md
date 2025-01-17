# Eryx examples
This page contains many example programs made using eryx and their corresponding output.

## Simple examples

### Variables
```C title="variables.eryx" linenums="1"
let a = 1;
let b = -2;
let c = 3.14;
let d = a;
let e = "Hello, World!";
let f = true;
let g = null;
let h = [1, 2, 3];
let i = {key: "value", num: 10};

print(a);
print(b);
print(c);
print(d);
print(e);
print(f);
print(g);
print(h);
print(i);
```
<details><summary>Output</summary>
```C linenums="1"
1
-2
3.14
1
Hello, World!
true
null
[ 1, 2, 3 ]
{ key: "value", num: 10 }
```
</details>

### Importing
```C linenums="1"
### math.eryx
func add(x, y) {
    return x + y;
}

const one = 1;
const pi = 22 / 7;


### test.eryx
import "math.eryx";
from "math.eryx" import ["add", "pi"];

print(add(5, 10), pi);
print(math.one);
```
<details><summary>Output</summary>
```C linenums="1"
15 3.142857142857143
1
```
</details>

### Functions
```C title="functions.eryx" linenums="1"
func add(x, y) {
    return x + y;
}

print(add(1, 2));
```
<details><summary>Output</summary>
```C linenums="1"
3
```
</details>

### If/Else statements
```C title="if_else.eryx" linenums="1"
let x = 10;
let y = 5;

if (x == y) {
    print("x is equal y");
} else {
    print("x is not equal y");
}
```
<details><summary>Output</summary>
```C linenums="1"
x is not equal y
```
</details>

### Loops
```rust title="loops.eryx" linenums="1"
let value = 0;
const threshold = 5;

loop {
    if (value >= threshold) {
        break;
    } else {
        value = value + 1
    }

    print(value);
}

print("done!");

value = 0;

while (value < threshold) {
    value = value + 1

    if (value % 2 != 0) {
        continue;
    }

    print(value);
}
```
<details><summary>Output</summary>
```C linenums="1"
1
2
3
4
5
done!
2
4
```
</details>

### Arithmetic operations
```rust title="arithmetic.eryx" linenums="1"
let x = 10;
let y = 5;

print(x + y);
print(x - y);
print(x * y);
print(x / y);
print(x % y);
print(x + y * 2 + x * (y + 2) - 5);
```
<details><summary>Output</summary>
```C linenums="1"
15
5
50
2
0
85
```
</details>

### Comparison operations
```C title="comparisons.eryx" linenums="1"
let x = 10;
let y = 5;

print(x == y);
print(x != y);
print(x < y);
print(x > y);
print(x <= y);
print(x >= y);
```
<details><summary>Output</summary>
```C linenums="1"
false
true
false
true
false
true
```
</details>

## Complex examples

### Factorial
Calculate the factorial of a number.
```C title="factorial.eryx" linenums="1"
func factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

print(factorial(5));
```
<details><summary>Output</summary>
```C linenums="1"
120
```
</details>

### Fibonacci
Calculate the nth Fibonacci number.
```C title="fibonacci.eryx" linenums="1"
func fibonacci(n) {
    if (n <= 0) {
        return 0;
    }
    if (n == 1) {
        return 1;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

print(fibonacci(10));
```
<details> <summary>Output</summary>
```C linenums="1"
55
```
</details>

### GCD
Find the greatest common divisor of two numbers using Euclid's algorithm.
```C title="gcd.eryx" linenums="1"
func gcd(a, b) {
    if (b == 0) {
        return a;
    }
    return gcd(b, a % b);
}

print(gcd(48, 18));
```
<details> <summary>Output</summary>
```C linenums="1"
6
```
</details>

### Prime Check
Check if a number is a prime number.
```C title="is_prime.eryx" linenums="1"
func isPrime(n, divisor) {
    if (n <= 1) {
        return false;
    }
    if (divisor == 1) {
        return true;
    }
    if (n % divisor == 0) {
        return false;
    }
    return isPrime(n, divisor - 1);
}

let number = 17;
print(isPrime(number, int(number ** 0.5)));
```
<details> <summary>Output</summary>
```C linenums="1"
true
```
</details>

### Offset adder
Create an adder with an offset then use it.
```C title="adder.eryx" linenums="1"
func makeAdder(offset) {
    func add(x, y) {
        return x + y + offset;
    }

    return add;
}

let adder = makeAdder(10);
print(adder(5, 10));
```
<details> <summary>Output</summary>
```C linenums="1"
25
```
</details>

### Sum digits
Sum all digits of a number.
```C title="sum_digits.eryx" linenums="1"
func sumOfDigits(n) {
    if (n == 0) {
        return 0;
    }
    return (n % 10) + sumOfDigits(int(n / 10));
}

print(sumOfDigits(12345));
```
<details> <summary>Output</summary>
```C linenums="1"
15
```
</details>

### Reverse number
Reverse the digits of a number.
```C title="reverse_number.eryx" linenums="1"
func reverseNumber(n, reversed) {
    if (n == 0) {
        return reversed;
    }
    reversed = reversed * 10 + (n % 10);
    return reverseNumber(int(n / 10), reversed);
}

print(reverseNumber(12345, 0));
```
<details> <summary>Output</summary>
```C linenums="1"
54321
```
</details>

### Is sorted
Check if a list is sorted.
```C title="is_sorted.eryx" linenums="1"
func isSorted(arr, idx) {
    if (idx == 0) {
        return true;
    }
    if (arr[idx] < arr[idx - 1]) {
        return false;
    }
    return isSorted(arr, idx - 1);
}

let nums = [1, 2, 3, 4, 5];
print(isSorted(nums, len(nums) - 1));
```
<details> <summary>Output</summary>
```C linenums="1"
true
```
</details>
