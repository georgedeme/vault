# Operators in Java

An <span class="hl-blue">operator</span> is a symbol that performs an operation on one, two, or three <span class="hl-blue">operands</span> and produces a result. Most operators look the same as in mathematics or C, which makes them easy to misread. The operand types decide what the operator actually does (`7 / 2` and `7.0 / 2` do different things), and precedence, associativity, and evaluation order decide how a compound expression is grouped and evaluated. This chapter goes through each operator family and the places where Java's rules give results you might not expect.

How operands of *different* types are converted before an operation (binary numeric promotion) is covered in [[04 - Type Casting#6. Binary Numeric Promotion — Mixed-Type Arithmetic|Type Casting § 6]]. This chapter assumes those rules and links back where they matter.

## Contents

- [[#1. Operator Categories at a Glance|1. Operator Categories at a Glance]]
- [[#2. Arithmetic Operators|2. Arithmetic Operators]]
- [[#3. Division and Remainder — The Special Cases|3. Division and Remainder — The Special Cases]]
- [[#4. Integer Overflow|4. Integer Overflow]]
- [[#5. Increment and Decrement|5. Increment and Decrement]]
- [[#6. Assignment and Compound Assignment|6. Assignment and Compound Assignment]]
- [[#7. Relational and Equality Operators|7. Relational and Equality Operators]]
- [[#8. Logical Operators|8. Logical Operators]]
- [[#9. Bitwise and Shift Operators|9. Bitwise and Shift Operators]]
- [[#10. The Ternary Operator and `instanceof`|10. The Ternary Operator and `instanceof`]]
- [[#11. `+` as String Concatenation|11. `+` as String Concatenation]]
- [[#12. Precedence and Associativity|12. Precedence and Associativity]]
- [[#13. Evaluation Order — Not the Same as Precedence|13. Evaluation Order — Not the Same as Precedence]]
- [[#14. Common Pitfalls|14. Common Pitfalls]]
- [[#15. Quick Reference — Non-Obvious Outcomes|15. Quick Reference — Non-Obvious Outcomes]]
- [[#16. Practice — Trick Questions|16. Practice — Trick Questions]]
- [[#17. Summary|17. Summary]]

---

## 1. Operator Categories at a Glance

| Category | Operators | Operand types | Result type |
|---|---|---|---|
| Arithmetic | `+` `-` `*` `/` `%`, unary `+` `-` | numeric (incl. `char`) | promoted numeric type (at least `int`) |
| Increment / decrement | `++` `--` (prefix and postfix) | numeric **variable** | same as the variable |
| Assignment | `=` `+=` `-=` `*=` `/=` `%=` `&=` `\|=` `^=` `<<=` `>>=` `>>>=` | variable + value | type of the variable |
| Relational | `<` `>` `<=` `>=` | numeric | `boolean` |
| Equality | `==` `!=` | numeric, `boolean`, or references | `boolean` |
| Logical | `&&` `\|\|` `!` (and `&` `\|` `^` on booleans) | `boolean` | `boolean` |
| Bitwise | `&` `\|` `^` `~` | integral (`int`, `long`, …) | promoted integral type |
| Shift | `<<` `>>` `>>>` | integral | promoted type of the **left** operand |
| Conditional (ternary) | `? :` | `boolean` + two values | common type of the branches |
| Type test | `instanceof` | reference + type | `boolean` |
| String concatenation | `+` | at least one `String` | `String` |

> [!note] Definitions
> - **Unary** operators take one operand (`-x`, `!b`, `i++`), **binary** operators take two (`a + b`), and the only **ternary** operator takes three (`c ? x : y`).
> - An **expression** is anything that produces a value. Every operator application is an expression, and that includes assignment (`x = 5` has the value `5`).

---

## 2. Arithmetic Operators

| Operator | Meaning | Example | Result |
|---|---|---|---|
| `+` | addition | `7 + 2` | `9` |
| `-` | subtraction | `7 - 2` | `5` |
| `*` | multiplication | `7 * 2` | `14` |
| `/` | division | `7 / 2` | `3` (**integer** division) |
| `%` | remainder | `7 % 2` | `1` |
| unary `-` | negation | `-7` | `-7` |
| unary `+` | numeric promotion (rarely useful) | `+'a'` | `97` (an `int`) |

> [!important] Key rule: operand types decide the operation
> - If **both** operands are integral (`byte`, `short`, `char`, `int`, `long`), the operation is **integer arithmetic**: `/` truncates toward zero.
> - If **either** is `float`/`double`, the operation is **floating-point** arithmetic.
> - `byte`, `short`, and `char` are **always promoted to at least `int`** first. `byte + byte` is an `int`.
>
> Full rules: [[04 - Type Casting#6. Binary Numeric Promotion — Mixed-Type Arithmetic|Type Casting § 6]].

```java
System.out.println(7 / 2);      // 3
System.out.println(7 / 2.0);    // 3.5
System.out.println(1 / 2 * 4.0);// 0.0  : 1/2 is int division (0) BEFORE the double appears
System.out.println(4.0 * 1 / 2);// 2.0  : left-to-right, 4.0*1 is already double
System.out.println('a' + 1);    // 98   : char promoted to int, not 'b'
```

```java
byte b = 5;
byte c = -b;       // compile error: unary minus promotes to int too
byte d = (byte) -b; // OK
```

### 2.1 Floating-Point Arithmetic Is Approximate

`double` and `float` are binary fractions, so most decimal values (0.1, 0.2, …) are not stored exactly:

```java
System.out.println(0.1 + 0.2);           // 0.30000000000000004
System.out.println(0.1 + 0.2 == 0.3);    // false
System.out.println(0.1 * 3 == 0.3);      // false
System.out.println((0.1 + 0.2) + 0.3 == 0.1 + (0.2 + 0.3)); // false : FP addition isn't associative
```

> [!tip] Comparing doubles
> Compare with a tolerance: `Math.abs(a - b) < 1e-9`. For money, use `long` cents or `java.math.BigDecimal`, never `double`.

---

## 3. Division and Remainder — The Special Cases

### 3.1 `%` Takes the Sign of the Dividend

Java's `%` is a **remainder**, not a mathematical modulo. The result has the sign of the **left** operand (the dividend), because integer `/` truncates toward zero and `a == (a / b) * b + (a % b)` always holds:

| Expression | `/` result | `%` result | Check: `(a/b)*b + a%b` |
|---|---|---|---|
| `7 / 3`, `7 % 3` | `2` | `1` | `6 + 1 = 7` |
| `-7 / 3`, `-7 % 3` | `-2` | `-1` | `-6 + (-1) = -7` |
| `7 / -3`, `7 % -3` | `-2` | `1` | `6 + 1 = 7` |
| `-7 / -3`, `-7 % -3` | `2` | `-1` | `6 + (-1) = -7` |

> [!warning] Common mistake: the odd-number check
> ```java
> boolean isOdd = n % 2 == 1;   // WRONG for negative n: -3 % 2 == -1
> boolean isOdd = n % 2 != 0;   // correct
> boolean isOdd = (n & 1) == 1; // correct (bitwise, works for negatives too)
> ```

For a mathematical modulo (always non-negative for a positive divisor), use `Math.floorMod(-7, 3)`, which gives `2`. `Math.floorDiv(-8, 3)` is `-3` (floor), while `-8 / 3` is `-2` (truncation).

`%` also works on floating-point values: `5.5 % 2 == 1.5`, `-5.5 % 2 == -1.5`.

### 3.2 Division by Zero: Integer vs. Floating-Point

<span class="hl-yellow">Exam favourite: the same-looking expression either crashes or quietly produces a special value, depending only on the operand types.</span>

| Expression | Result |
|---|---|
| `5 / 0` | throws `ArithmeticException: / by zero` |
| `5 % 0` | throws `ArithmeticException: / by zero` |
| `5.0 / 0` | `Infinity` (no exception) |
| `-5.0 / 0` | `-Infinity` |
| `1 / -0.0` | `-Infinity` (negative zero exists for `double`) |
| `0.0 / 0` | `NaN` |
| `5.0 % 0` | `NaN` |
| `Infinity - Infinity`, `0 * Infinity` | `NaN` |

> [!info]- Why the difference?
> Integers have no bit pattern for "infinity" or "not a number", so the only safe option is to throw. `float`/`double` follow the **IEEE 754** standard, which reserves special values (`±Infinity`, `NaN`, `-0.0`) for exactly these cases, so the computation continues silently. This makes floating-point errors **harder** to notice: a `NaN` can propagate through a long calculation without any exception.

### 3.3 The One Integer Division That Overflows

```java
int min = Integer.MIN_VALUE;
System.out.println(min / -1);   // -2147483648 : no exception!
System.out.println(min % -1);   // 0
```

The true answer, 2,147,483,648, is one more than `Integer.MAX_VALUE`, so it wraps back to `MIN_VALUE`. This is the only integer division that overflows.

---

## 4. Integer Overflow

Integer arithmetic **wraps around silently**. There is no exception and no warning:

```java
int max = Integer.MAX_VALUE;           // 2147483647
System.out.println(max + 1);           // -2147483648
System.out.println(max + 1 < max);     // true (!)
System.out.println(Math.abs(Integer.MIN_VALUE)); // -2147483648 : abs of MIN is still negative
System.out.println(-Integer.MIN_VALUE);          // -2147483648
```

> [!warning] Common mistake: overflow happens before widening
> ```java
> long microsPerDay = 24 * 60 * 60 * 1000 * 1000;   // 500654080 : WRONG
> long microsPerDay = 24L * 60 * 60 * 1000 * 1000;  // 86400000000 : correct
> ```
> The right-hand side is computed entirely in `int` (all literals are `int`) and overflows **before** being widened to `long` for the assignment. Making the **first** operand `long` forces the whole left-to-right chain into `long` arithmetic. Same trap: `long big = Integer.MAX_VALUE * 2;` gives `-2`.

> [!warning] Classic DSA bug: the midpoint of binary search
> ```java
> int mid = (low + high) / 2;          // overflows when low + high > Integer.MAX_VALUE
> int mid = low + (high - low) / 2;    // safe
> int mid = (low + high) >>> 1;        // safe: unsigned shift reinterprets the overflowed sum correctly
> ```
> With `low = 2_000_000_000`, `high = 2_100_000_000`: the first gives `-97483648`, the other two give `2050000000`.

To **detect** overflow instead of wrapping, use `Math.addExact`, `Math.subtractExact`, `Math.multiplyExact`, `Math.negateExact`, `Math.toIntExact`. These throw `ArithmeticException: integer overflow`.

Floating-point overflow doesn't wrap. It goes to `Infinity`: `1e308 * 10 == Double.POSITIVE_INFINITY`.

---

## 5. Increment and Decrement

| Form | Name | Effect | Value of the expression |
|---|---|---|---|
| `++x` | pre-increment | `x = x + 1` | the **new** value |
| `x++` | post-increment | `x = x + 1` | the **old** value |
| `--x` | pre-decrement | `x = x - 1` | the **new** value |
| `x--` | post-decrement | `x = x - 1` | the **old** value |

```java
int x = 5;
int a = x++;   // a == 5, x == 6
int b = ++x;   // b == 7, x == 7
```

When used as a standalone statement (`i++;`), prefix and postfix are identical. The difference only matters when the **value** of the expression is used.

### 5.1 `x = x++` Does Nothing

```java
int i = 5;
i = i++;
System.out.println(i);   // 5, not 6
```

> [!example]- Step by step: why `i` stays 5
> 1. `i++` is evaluated: its **value** (the old `i`, 5) is saved as a temporary.
> 2. As a side effect, `i` becomes 6.
> 3. The assignment `i = <temporary>` runs **last** and stores 5 back into `i`, overwriting the 6.
>
> | Step | Temporary | `i` |
> |---|---|---|
> | start | — | 5 |
> | evaluate `i++` (value) | 5 | 5 |
> | `i++` side effect | 5 | 6 |
> | assign temp to `i` | — | **5** |

### 5.2 Several Increments in One Expression

Operands are evaluated **left to right** (see [[#13. Evaluation Order — Not the Same as Precedence|§ 13]]), and each `++` takes effect immediately, before the next operand is evaluated:

```java
int x = 5;
int r = x++ + ++x;   // 5 + 7 = 12, x == 7
```

| Operand | Value used | `x` afterwards |
|---|---|---|
| `x++` | 5 | 6 |
| `++x` | 7 | 7 |

```java
int w = 0;
w = w++ + w++;       // 0 + 1 = 1   (the side effects are overwritten by the assignment)
```

> [!tip]
> Such expressions are **well-defined in Java** (unlike C/C++, where they're undefined behaviour), so exams love them. In real code, never write more than one `++`/`--` on the same variable in one expression.

### 5.3 What `++` / `--` Can and Cannot Be Applied To

- Works on any numeric variable, **including `char`, `double`, and `byte`**: `char c = 'a'; c++;` gives `'b'`, and `double d = 1.5; d++;` gives `2.5`.
- `++` on a `byte`/`short`/`char` includes an **implicit cast back**, so `b++` compiles even though `b = b + 1` doesn't.
- **Needs a variable**: `5++`, `(x + 1)++`, and `x++++` are compile errors ("unexpected type"), because the result of `x++` is a value, not a variable.
- Not on `boolean`: `flag++` is a compile error.
- Not on a `final` variable: `final int f = 1; f++;` → *cannot assign a value to final variable*.

> [!info]- Tokenizing `i+++j` and `i+++++j`
> The lexer uses **maximal munch**: it always grabs the longest valid token. `i+++j` becomes `i ++ + j` → `(i++) + j`, which compiles. `i+++++j` becomes `i ++ ++ + j` → `(i++)++ + j`, a compile error even though `i++ + ++j` (with spaces) would be fine.

---

## 6. Assignment and Compound Assignment

### 6.1 Assignment Is an Expression

`=` stores the right-hand value into the variable **and** evaluates to that value. It is **right-associative**, which makes chaining work:

```java
int a, b, c;
a = b = c = 7;          // parsed as a = (b = (c = 7)); all three are 7
```

```java
while ((line = reader.readLine()) != null) { ... }   // idiomatic use of the assignment's value
```

> [!warning] Common mistake: typos that still compile
> ```java
> int x = 10;
> x =+ 5;   // x = (+5)  → x == 5, not 15
> x =- 5;   // x = (-5)  → x == -5
> boolean done = false;
> done =! done;   // done = (!done): compiles, and happens to toggle
> ```
> `=+`, `=-`, and `=!` aren't operators. The lexer reads them as `=` followed by a unary operator.

### 6.2 Compound Assignment

`x op= y` is shorthand for `x = (T) (x op (y))`, where `T` is the type of `x`. That definition contains three details:

> [!important] Key rule: `x op= y` is `x = (T)(x op (y))`, with `x` evaluated once
> 1. **An implicit narrowing cast** `(T)` is included, so compound assignment can silently truncate or wrap.
> 2. **The right-hand side is parenthesized.** `x *= 2 + 3` is `x = x * (2 + 3)`, not `x * 2 + 3`.
> 3. **The left-hand side is evaluated only once.**

```java
byte b = 10;
b = b + 5;    // compile error: b + 5 is int
b += 5;       // OK: implicit (byte) cast; b == 15
b += 300;     // compiles! wraps silently: b == 59

int i = 5;
i += 3.7;     // compiles: i = (int)(5 + 3.7) = (int) 8.7 = 8

char c = 'a';
c += 1;       // OK: 'b'  (c = c + 1 would not compile)

int m = 3;
m *= 2 + 3;   // m = 3 * (2 + 3) = 15, not 3 * 2 + 3 = 9
```

```java
int[] arr = {10};
arr[next()] += 1;                 // next() called ONCE
arr[next()] = arr[next()] + 1;    // next() called TWICE: may touch two different elements
```

The left operand's value is saved **before** the right side is evaluated:

```java
int k = 1;
k += (k = 4);   // k = 1 + 4 = 5, not 4 + 4 = 8
```

String compound assignment evaluates the right side as its own expression first:

```java
String s = "v";
s += 1 + 2;     // "v3"  : right side 1 + 2 is computed first (int 3)
s = s + 1 + 2;  // "v12" : left-to-right, "v" + 1 is already a String
```

### 6.3 Compile-Time Constants Can Be Narrowed Without a Cast

Normally an `int` expression can't be assigned to a `byte`/`short`/`char` without a cast. There is one exception: if the expression is a **compile-time constant** of type `int` (or smaller) and its **value fits** the target type, the compiler narrows it for you.

| Code | Compiles? | Why |
|---|---|---|
| `byte b = 10 + 20;` | ✅ | constant `30` fits in `byte` |
| `byte b = 127 + 1;` | ❌ | constant `128` doesn't fit |
| `char c = 65 + 1;` | ✅ | constant `66` fits in `char` (`'B'`) |
| `int one = 1; char c = one + 65;` | ❌ | `one` is a variable, not a constant |
| `final int one = 1; char c = one + 65;` | ✅ | a `final` variable initialized with a constant **is** a constant |
| `short s = 5; s = s * 1;` | ❌ | `s` isn't a constant |
| `int i = 5L;` | ❌ | the rule doesn't cover `long` constants |
| `float f = 1.5;` | ❌ | nor `double` constants (see [[Java/01 - Foundations/02 - Variables and Data Types#4.3 The `float` Suffix|the `float` suffix]]) |

---

## 7. Relational and Equality Operators

| Operator | Meaning |
|---|---|
| `<` `>` `<=` `>=` | ordering, **numeric operands only** (including `char`) |
| `==` `!=` | equality: numeric, `boolean`, or **reference** comparison |

```java
10 == 10.0     // true : int promoted to double
'a' == 97      // true : char promoted to int
'a' < 'b'      // true : compares code points
"a" < "b"      // compile error: use "a".compareTo("b") < 0
true < false   // compile error: booleans have no ordering
```

### 7.1 Comparisons Don't Chain

```java
int a = 1, b = 2, c = 3;
a < b < c      // compile error: (a < b) is boolean, and boolean < int is meaningless
a == b == c    // compile error: incomparable types: boolean and int
```

Write `a < b && b < c`. There's also a catch with booleans, where chaining **does** compile:

```java
false == false == false   // false : (false == false) is true, and true == false is false
```

### 7.2 `NaN` and `-0.0`

```java
double nan = Double.NaN;
nan == nan     // false : NaN is not equal to anything, including itself
nan != nan     // true
nan < 1        // false
nan > 1        // false : every ordered comparison with NaN is false
0.0 == -0.0    // true
Double.valueOf(0.0).equals(-0.0)   // false : equals() distinguishes them
```

Test for NaN with `Double.isNaN(x)`, never with `x == Double.NaN`.

`float` vs. `double`: `0.1f == 0.1` is `false`, since the `float` 0.1 is a less precise approximation than the `double` 0.1. `0.5f == 0.5` is `true` because 0.5 is exactly representable in binary.

### 7.3 `==` on References Compares Identity, Not Content

For objects, `==` asks "is this the **same object**?", not "do they contain the same data?". Use `.equals()` for content:

```java
String s1 = "hi", s2 = new String("hi");
s1 == s2          // false : different objects
s1.equals(s2)     // true

Integer i1 = 127, i2 = 127;  i1 == i2   // true  : cached boxes (-128..127)
Integer i3 = 128, i4 = 128;  i3 == i4   // false : different objects
i3 <= i4 && i3 >= i4                    // true  : <, <=, >, >= always unbox!

Integer n = 1; Long l = 1L;
n == l            // compile error: incomparable types: Integer and Long
n.equals(l)       // false : different classes
```

See [[Java/03 - Program Structure/02 - Strings#2. Creating Strings — Literals vs. `new`|Strings § 2]] and [[04 - Type Casting#9. Autoboxing and Unboxing (Related, Not True Casting)|Type Casting § 9]].

![[Operators - Identity and the Integer Cache.excalidraw|800]]

> [!info]- When does `==` on strings return `true` unexpectedly?
> Compile-time constant expressions are computed by the compiler and **pooled**:
> ```java
> "a" + "b" == "ab"            // true : folded to the literal "ab" at compile time
> final String f = "a";
> f + "b" == "ab"              // true : f is a constant variable
> String v = "a";
> v + "b" == "ab"              // false : computed at run time → new object
> ```
> This is why `==` on strings "works sometimes" in small tests. It's still the wrong operator.

---

## 8. Logical Operators

| Operator | Name | `true` when | Short-circuits? |
|---|---|---|---|
| `&&` | conditional AND | both operands true | ✅ skips the right side if the left is `false` |
| `\|\|` | conditional OR | at least one true | ✅ skips the right side if the left is `true` |
| `!` | NOT | operand is false | — |
| `&` | logical AND (on `boolean`) | both true | ❌ always evaluates both |
| `\|` | logical OR (on `boolean`) | at least one true | ❌ always evaluates both |
| `^` | XOR (on `boolean`) | operands **differ** | ❌ (must see both) |

Truth table:

| `a` | `b` | `a && b` | `a \|\| b` | `a ^ b` | `!a` |
|---|---|---|---|---|---|
| T | T | T | T | **F** | F |
| T | F | F | T | T | F |
| F | T | F | T | T | T |
| F | F | F | F | F | T |

### 8.1 Short-Circuiting

Short-circuiting is how you guard an operation that would otherwise fail:

```java
if (s != null && s.length() > 0) { ... }   // safe: length() never runs when s is null
if (d != 0 && n / d > 2) { ... }           // safe: no division by zero
if (s != null & s.length() > 0) { ... }    // NullPointerException when s is null!
```

It also means **side effects in the right operand may never run**:

```java
int n = 0;
boolean r1 = false && n++ > 0;   // n == 0 : n++ skipped
boolean r2 = false &  n++ > 0;   // n == 1 : & evaluates both sides

int y = 3;
boolean r3 = y > 2 || y++ > 0;   // y == 3 : left is true, y++ skipped
```

> [!warning] Common mistake: `&=` and `|=` do not short-circuit
> ```java
> boolean allOk = true;
> allOk &= check1();   // check2() is called even if check1() returned false
> allOk &= check2();
> ```
> There is no `&&=` operator. `&=` is the non-short-circuit `&`. That's fine if every check *should* run (e.g. validating all form fields), but wrong if a later check depends on an earlier one succeeding.

### 8.2 `!` Only Applies to `boolean`

```java
int x = 1;
!x          // compile error: Java has no "truthiness"; use x == 0
!x > 0      // compile error: parsed as (!x) > 0 since ! binds tighter than >
!(x > 0)    // OK
!true == false   // true : (!true) == false
```

---

## 9. Bitwise and Shift Operators

These operate on the **binary (two's complement) representation** of integral values. `byte`/`short`/`char` are promoted to `int` first.

| Operator | Name | Rule per bit | Example (4-bit view) |
|---|---|---|---|
| `&` | AND | 1 if both 1 | `0101 & 0011 = 0001` → `5 & 3 == 1` |
| `\|` | OR | 1 if either 1 | `0101 \| 0011 = 0111` → `5 \| 3 == 7` |
| `^` | XOR | 1 if different | `0101 ^ 0011 = 0110` → `5 ^ 3 == 6` |
| `~` | NOT (complement) | flips every bit | `~5 == -6` |
| `<<` | left shift | shift left, fill with 0 | `1 << 3 == 8` |
| `>>` | signed right shift | shift right, fill with the **sign bit** | `-8 >> 1 == -4` |
| `>>>` | unsigned right shift | shift right, fill with **0** | `-1 >>> 28 == 15` |

> [!important] Key identities
> - `~x == -x - 1` (so `~5 == -6`, `~-1 == 0`). This follows from two's complement.
> - `x << n` equals `x * 2ⁿ` (until overflow).
> - `x >> n` equals `Math.floorDiv(x, 2ⁿ)`, rounding toward **negative infinity**, so it is **not** the same as `x / 2ⁿ` for negative odd numbers: `-7 >> 1 == -4`, but `-7 / 2 == -3`.
> - `x & 1` is the lowest bit, so it tells you whether `x` is odd, and works for negatives too.
> - `n > 0 && (n & (n - 1)) == 0` tests whether `n` is a power of two.

> [!example]- Worked example: why `-8 >> 1` is `-4` but `-8 >>> 1` is huge
> `-8` as a 32-bit `int` is `11111111 11111111 11111111 11111000`.
>
> | Operation | Fill bit | Result bits | Value |
> |---|---|---|---|
> | `-8 >> 1` | sign bit (`1`) | `11111111 11111111 11111111 11111100` | `-4` |
> | `-8 >>> 1` | `0` | `01111111 11111111 11111111 11111100` | `2147483644` |
>
> `>>` keeps the number negative, while `>>>` treats the bit pattern as if it were unsigned.

### 9.1 Shift Distances Are Masked

<span class="hl-yellow">Classic trick question:</span> for an `int`, only the **lowest 5 bits** of the shift distance are used (`distance & 31`). For a `long`, the lowest 6 bits (`& 63`).

```java
1 << 32     // 1   : 32 & 31 == 0, so no shift at all
1 << 33     // 2   : same as 1 << 1
1 << -1     // -2147483648 : -1 & 31 == 31
-1 >>> 32   // -1  : not 0!
1L << 32    // 4294967296 : long uses & 63, so this really shifts
1 << 31     // -2147483648 : the 1 lands in the sign bit
```

The **type of a shift is the (promoted) type of the left operand only**. The right operand doesn't affect it, so `int i = 1 << 32L;` compiles (and gives `1`).

### 9.2 `>>>` on `byte` / `short` Doesn't Do What You'd Expect

```java
byte b = -1;
b >>>= 4;
System.out.println(b);   // -1 (!)
```

> [!example]- Step by step
> | Step | Type | Bits | Value |
> |---|---|---|---|
> | `b` | `byte` | `11111111` | `-1` |
> | promoted | `int` | `11111111 11111111 11111111 11111111` | `-1` |
> | `>>> 4` | `int` | `00001111 11111111 11111111 11111111` | `268435455` |
> | implicit `(byte)` cast in `>>>=` | `byte` | `11111111` (lowest 8 bits) | **`-1`** |
>
> The zeros shifted in are at the top of the 32-bit `int`, and the cast back to `byte` throws them away. To shift a byte's bits as unsigned, mask first: `(b & 0xFF) >>> 4` gives `15`.

### 9.3 `&`, `|`, `^` Have Two Meanings

On integral operands they are bitwise. On `boolean` operands they are the non-short-circuit logical operators from [[#8. Logical Operators|§ 8]]. `~` is **only** bitwise: `~true` is a compile error (use `!`).

> [!warning] Common mistake: bitwise operators bind more loosely than `==`
> ```java
> if (x & 1 == 0) { }     // compile error: parsed as x & (1 == 0), i.e. int & boolean
> if ((x & 1) == 0) { }   // correct
> ```
> In C this compiles and silently does the wrong thing. In Java it's at least a compile error. Also: `5 & 6 + 1` is `5 & 7 == 5`, because `+` binds tighter than `&`.

> [!info]- The XOR swap and its trap
> ```java
> a ^= b; b ^= a; a ^= b;   // swaps a and b without a temporary
> ```
> It works because `x ^ x == 0` and `x ^ 0 == x`. But if both refer to the **same storage** (e.g. `arr[i]` and `arr[j]` with `i == j`), the first step zeroes it: `x ^= x` gives `0`, and the value is lost. A temporary variable is clearer and just as fast.

---

## 10. The Ternary Operator and `instanceof`

### 10.1 `condition ? valueIfTrue : valueIfFalse`

An **expression** (it produces a value), unlike the `if` statement:

```java
String label = (age >= 18) ? "adult" : "minor";
int max = (a > b) ? a : b;
```

- Only the selected branch is **evaluated**, but both branches determine the **type**. `true ? 5 : 2.0` is `5.0` (see [[04 - Type Casting#6.2 The Ternary Operator Also Applies Numeric Promotion|Type Casting § 6.2]]).
- It is **right-associative**: `a ? b : c ? d : e` means `a ? b : (c ? d : e)`.
- It can't stand alone as a statement: `x > 0 ? foo() : bar();` is a compile error.
- **Unboxing trap:** if one branch is a boxed `Integer` that is `null` and the other is a primitive `int`, the result type is `int` and the `null` gets unboxed:

```java
Integer maybe = null;
int v = true ? maybe : 0;   // NullPointerException
```

For choosing between the ternary and `if`/`else`, see [[01 - Conditional Statements#10. The Ternary Operator vs. `if` / `else`|Conditional Statements § 10]].

### 10.2 `instanceof`

Tests whether a reference points to an object of a given type (or subtype):

```java
Object o = "hi";
o instanceof String       // true
null instanceof Object    // false : null is never an instance of anything (no exception)
"x" instanceof Integer    // compile error: String can never be an Integer

if (o instanceof String s && s.length() > 1) { ... }   // pattern matching (Java 16+)
```

In the last line, `s` is in scope on the right of `&&` because that side only runs if the test succeeded. With `||` it would **not** be in scope. More in [[04 - Type Casting#7. Reference (Object) Casting|Type Casting § 7]], and the full scope rules in [[Java/04 - Object-Oriented Programming/04 - Polymorphism#7.2 Where the Pattern Variable Is in Scope|Polymorphism § 7.2]].

---

## 11. `+` as String Concatenation

If **either** operand of `+` is a `String`, it means concatenation. The other operand is converted to its string form. Because `+` is **left-associative**, the result depends on *where* the first `String` appears:

```java
1 + 2 + "3"         // "33"   : (1 + 2) is int 3, then 3 + "3"
"1" + 2 + 3         // "123"  : ("1" + 2) is "12", then "12" + 3
"1" + (2 + 3)       // "15"
3 + 4 + "" + 3 + 4  // "734"
'a' + 'b' + "c"     // "195c" : char + char is int arithmetic first
"" + 'a' + 'b'      // "ab"
"x" + null          // "xnull"
```

`-`, `*`, `/` have no string meaning: `"a" - "a"` and `s -= "a"` are compile errors. Performance of `+` in loops and `StringBuilder` are covered in [[Java/03 - Program Structure/02 - Strings#4. String Concatenation|Strings § 4]].

---

## 12. Precedence and Associativity

<span class="hl-blue">Precedence</span> decides how operands are **grouped** when different operators appear together. <span class="hl-blue">Associativity</span> decides the grouping when operators of the **same** precedence are chained. Highest precedence first:

| Level | Operators | Description | Associativity |
|---|---|---|---|
| 1 | `x++` `x--` `.` `[]` `()` (call) | postfix, member access | left → right |
| 2 | `++x` `--x` `+x` `-x` `~` `!` `(type)` | unary, cast | **right → left** |
| 3 | `*` `/` `%` | multiplicative | left → right |
| 4 | `+` `-` | additive, concatenation | left → right |
| 5 | `<<` `>>` `>>>` | shift | left → right |
| 6 | `<` `>` `<=` `>=` `instanceof` | relational | left → right |
| 7 | `==` `!=` | equality | left → right |
| 8 | `&` | bitwise / logical AND | left → right |
| 9 | `^` | bitwise / logical XOR | left → right |
| 10 | `\|` | bitwise / logical OR | left → right |
| 11 | `&&` | conditional AND | left → right |
| 12 | `\|\|` | conditional OR | left → right |
| 13 | `? :` | ternary | **right → left** |
| 14 | `=` `+=` `-=` `*=` … `->` | assignment, lambda | **right → left** |

> [!tip] Mnemonic for the middle of the table
> **Unary → Arithmetic → Shift → Relational → Equality → Bitwise (`& ^ |`) → Logical (`&& ||`) → Ternary → Assignment.** Arithmetic binds tightest among binary operators, and assignment binds loosest.

Worked groupings:

| Expression | Grouped as | Value |
|---|---|---|
| `1 + 2 * 3 % 4` | `1 + ((2 * 3) % 4)` | `3` |
| `2 << 1 + 1` | `2 << (1 + 1)` | `8` |
| `8 >> 1 >> 1` | `(8 >> 1) >> 1` | `2` |
| `10 - 4 - 3` | `(10 - 4) - 3` | `3` (not `9`) |
| `100 / 10 / 5` | `(100 / 10) / 5` | `2` (not `50`) |
| `true \|\| false && false` | `true \|\| (false && false)` | `true` |
| `true \| false & false` | `true \| (false & false)` | `true` |
| `(int) 3.7 + 0.5` | `((int) 3.7) + 0.5` | `3.5` (the cast binds to `3.7` only) |
| `-x++` (x = 5) | `-(x++)` | `-5`, then `x == 6` |
| `10 / 3 * 3 + 10 % 3` | `((10 / 3) * 3) + (10 % 3)` | `10` |
| `a = b = 5` | `a = (b = 5)` | `5` |

> [!warning] Common mistake: `&&` binds tighter than `||`
> `a || b && c` is `a || (b && c)`, not `(a || b) && c`. When mixing them, **always add parentheses**, even if you know the table. The next reader may not.

---

## 13. Evaluation Order — Not the Same as Precedence

Precedence only tells you **how the expression is grouped**. The **order in which operands are evaluated** is a separate rule:

> [!important] Key rule: left to right
> Java evaluates the **left operand fully before the right operand**, method arguments **left to right**, and all operands **before** the operation itself. The JLS guarantees this. Unlike C/C++, it is never "unspecified".

```java
static int a() { System.out.print("a "); return 1; }
static int b() { System.out.print("b "); return 2; }
static int c() { System.out.print("c "); return 3; }

int r = a() + b() * c();   // prints: a b c   (r == 7)
```

`*` has higher precedence, so the expression is grouped as `a() + (b() * c())`, but `a()` is still **called first** because it's the left operand of `+`.

![[Operators - Precedence vs Evaluation Order.excalidraw|800]]

```java
int i = 2;
int r = i * (i = 3);     // 2 * 3 = 6 : left operand i read as 2 BEFORE the assignment runs

int[] arr = new int[2];
int idx = 0;
arr[idx] = idx = 1;      // arr[0] == 1 : the array index is evaluated before the right side
```

Exceptions to "all operands first": `&&`, `||`, and `? :` may **skip** operands entirely ([[#8.1 Short-Circuiting|§ 8.1]]).

---

## 14. Common Pitfalls

- **Integer division** where a fraction was expected: `double avg = sum / count;` with `int`s. Cast an operand first: `(double) sum / count` ([[04 - Type Casting#6.1 Integer Division Truncates Before Any Promotion to the Result Type|Type Casting § 6.1]]).
- **`n % 2 == 1` as an odd test.** It fails for negative `n`. Use `n % 2 != 0`.
- **Overflow in an `int` expression assigned to a `long`.** Make the first operand `long` (`24L * …`).
- **`i = i++`**, and several `++` on one variable in a single expression.
- **Compound assignment silently narrows**: `byteVar += 300`, `intVar += 3.7`.
- **`x =+ 5` / `x =- 5`** typos that compile.
- **`&` / `|` instead of `&&` / `||`**. You lose short-circuiting, which can cause `NullPointerException` or division by zero.
- **`==` on objects** (`String`, `Integer`, …) instead of `.equals()`.
- **`==` on `double`** instead of a tolerance, and `x == Double.NaN` (always `false`).
- **Chained comparisons** `a < b < c`: a compile error for numbers, and a silent logic error for booleans.
- **Bitwise vs. comparison precedence**: `x & 1 == 0` needs parentheses.
- **Shift distance ≥ 32 on an `int`**: masked, not "shifts everything out".
- **`>>>` on a negative `byte`/`short`**: promoted to `int` first, so mask with `& 0xFF` / `& 0xFFFF`.
- **Mixing `&&` and `||` without parentheses.**

---

## 15. Quick Reference — Non-Obvious Outcomes

| Code | Result | Category |
|---|---|---|
| `7 / 2` | `3` | integer division truncates |
| `1 / 2 * 4.0` | `0.0` | int division happens before the double appears |
| `-7 % 3` | `-1` | remainder takes the dividend's sign |
| `Math.floorMod(-7, 3)` | `2` | true modulo |
| `5 / 0` | `ArithmeticException` | integer division by zero |
| `5.0 / 0` | `Infinity` | IEEE 754, no exception |
| `0.0 / 0` | `NaN` | IEEE 754 |
| `Integer.MIN_VALUE / -1` | `-2147483648` | the only overflowing division |
| `Integer.MAX_VALUE + 1` | `-2147483648` | silent wraparound |
| `Math.abs(Integer.MIN_VALUE)` | `-2147483648` | no positive counterpart |
| `24 * 60 * 60 * 1000 * 1000` | `500654080` | `int` overflow before widening |
| `i = i++` (i = 5) | `i == 5` | old value assigned back |
| `x++ + ++x` (x = 5) | `12` | 5 + 7, left to right |
| `byte b = 10; b += 300;` | `59` | compound assignment casts implicitly |
| `int i = 5; i += 3.7;` | `8` | compound assignment casts implicitly |
| `m *= 2 + 3` (m = 3) | `15` | RHS parenthesized |
| `k += (k = 4)` (k = 1) | `5` | LHS value saved first |
| `x =+ 5` | `x == 5` | `=` then unary `+` |
| `byte b = 10 + 20;` | compiles | constant fits → implicit narrowing |
| `0.1 + 0.2 == 0.3` | `false` | binary floating point |
| `Double.NaN == Double.NaN` | `false` | NaN equals nothing |
| `0.0 == -0.0` | `true` | but `Double.equals` says `false` |
| `a < b < c` (ints) | compile error | `boolean < int` |
| `false == false == false` | `false` | `(true) == false` |
| `Integer 128 == Integer 128` | `false` | reference comparison outside the cache |
| `"a" + "b" == "ab"` | `true` | compile-time constant, pooled |
| `false & (n++ > 0)` | `n` incremented | `&` doesn't short-circuit |
| `~5` | `-6` | `~x == -x - 1` |
| `-7 >> 1` vs `-7 / 2` | `-4` vs `-3` | shift floors, division truncates |
| `1 << 32` | `1` | shift distance masked (`& 31`) |
| `-1 >>> 32` | `-1` | shift distance masked |
| `byte b = -1; b >>>= 4;` | `-1` | promotion to int, then cast back |
| `x & 1 == 0` | compile error | `==` binds tighter than `&` |
| `1 + 2 + "3"` | `"33"` | left-associative `+` |
| `'a' + 'b'` | `195` | char arithmetic is int |
| `true ? (Integer) null : 0` → `int` | `NullPointerException` | ternary unboxing |
| `null instanceof Object` | `false` | never throws |
| `(int) 3.7 + 0.5` | `3.5` | cast binds tighter than `+` |

---

## 16. Practice — Trick Questions

**Q1.** What is printed?

```java
int x = 10;
x = x++ + ++x;
System.out.println(x);
```

> [!success]- Answer
> `22`.
>
> | Operand | Value used | `x` afterwards |
> |---|---|---|
> | `x++` | 10 | 11 |
> | `++x` | 12 | 12 |
> | assignment | `10 + 12 = 22` | **22** |

**Q2.** Which lines compile?

```java
byte a = 10;
byte b = a + 1;      // (1)
byte c = a++;        // (2)
byte d = 10 + 1;     // (3)
a += 1;              // (4)
a = -a;              // (5)
```

> [!success]- Answer
> | Line | Compiles? | Reason |
> |---|---|---|
> | (1) | ❌ | `a + 1` is `int`, and `a` isn't a constant |
> | (2) | ✅ | `a++` has type `byte` |
> | (3) | ✅ | constant `11` fits in `byte` |
> | (4) | ✅ | compound assignment casts implicitly |
> | (5) | ❌ | unary `-` promotes to `int` |

**Q3.** What is printed?

```java
System.out.println(1 + 2 + "3" + 4 + 5);
System.out.println('1' + 2 + "3");
```

> [!success]- Answer
> ```
> 3345
> 513
> ```
> Line 1: `1 + 2 = 3`, then `"33"`, then `"334"`, then `"3345"`.
> Line 2: `'1'` has code point 49, so `49 + 2 = 51`, then `"513"`.

**Q4.** What is `i` after this code?

```java
int i = 0;
boolean r = (i++ > 0) && (i++ > 0) || (i++ > 0);
```

> [!success]- Answer
> `i == 2`, `r == true`. Grouping: `((i++ > 0) && (i++ > 0)) || (i++ > 0)`.
>
> | Step | Evaluates | Result | `i` afterwards |
> |---|---|---|---|
> | 1 | `i++ > 0` → `0 > 0` | `false` | 1 |
> | 2 | `&&` short-circuits, middle `i++` **skipped** | `false` | 1 |
> | 3 | `\|\|` must check the right side: `1 > 0` | `true` | 2 |

**Q5.** What are the outputs?

```java
System.out.println(-17 % 5);
System.out.println(17 % -5);
System.out.println(-17 / 5);
System.out.println(-17 >> 2);
```

> [!success]- Answer
> ```
> -2
> 2
> -3
> -5
> ```
> `%` takes the dividend's sign. `/` truncates toward zero (`-3.4 → -3`). `>> 2` is floor division by 4 (`-4.25 → -5`).

**Q6.** A student writes `long nanosPerYear = 365 * 24 * 60 * 60 * 1_000_000_000;`. Is the value correct? Fix it.

> [!success]- Answer
> No. Every operand is an `int`, so the product overflows `int` long before the assignment widens it. Fix: `365L * 24 * 60 * 60 * 1_000_000_000`. The first operand must be `long` so that every step of the left-to-right chain is done in `long`.

**Q7.** Does this print `true` or `false`, and why?

```java
double d = 0.0 / 0.0;
System.out.println(d == d);
System.out.println(d != d);
```

> [!success]- Answer
> `false`, then `true`. `0.0 / 0.0` is `NaN`, and `NaN` compares unequal to everything, itself included. (`d != d` is in fact a known NaN test, though `Double.isNaN(d)` is clearer.)

**Q8.** What is printed?

```java
int a = 5;
a += a++ * 2;
System.out.println(a);
```

> [!success]- Answer
> `15`. `a += expr` is `a = a + (expr)`, and the left `a` (5) is saved **first**. Then `a++ * 2` gives `5 * 2 = 10` (with `a` briefly becoming 6). The result is `5 + 10 = 15`, which overwrites the 6.

**Q9.** Which of these compile, and what are the values of those that do?

```java
int p = 1 << 35;
long q = 1 << 35;
long r = 1L << 35;
```

> [!success]- Answer
> All three compile.
> - `p == 8`: `35 & 31 == 3`, so `1 << 3`.
> - `q == 8`: the shift is still done in `int` (the left operand is `int`), and only the result is widened to `long`.
> - `r == 34359738368`: a real 35-bit shift in `long`.

---

## 17. Summary

- The **operand types** decide what an operator does: integer vs. floating-point division, bitwise vs. logical `&`/`|`/`^`, and numeric `+` vs. concatenation.
- **Integer arithmetic wraps silently**, and integer division by zero **throws**. **Floating-point arithmetic** produces `Infinity`/`NaN` and is approximate, so never compare doubles with `==`.
- `%` is a **remainder** that keeps the dividend's sign. Use `Math.floorMod` for a true modulo.
- **Prefix** `++x` yields the new value and **postfix** `x++` the old. `x = x++` leaves `x` unchanged.
- **Compound assignment** `x op= y` means `x = (T)(x op (y))`: it casts implicitly, parenthesizes the right side, and evaluates the left side once.
- `&&` and `||` **short-circuit**. `&`, `|`, `&=`, `|=` do not.
- `==` compares **values** for primitives and **identity** for objects. Use `.equals()` for object content.
- Shifts **mask** their distance (`& 31` for `int`, `& 63` for `long`). `>>` preserves the sign and `>>>` fills with zeros. `byte`/`short` are promoted to `int` first.
- **Precedence** controls grouping, **associativity** controls chains of equal-precedence operators, and **evaluation order** is always left to right. These are three separate rules.

## Related

- [[Java/00 - Syllabus|Syllabus]]
- Previous: [[02 - Variables and Data Types|Variables and Data Types]] · Next: [[04 - Type Casting|Type Casting]]
- [[01 - Introduction to Java|Introduction to Java]]
- [[01 - Conditional Statements|Conditional Statements]]: conditions, `switch`, the ternary operator
- [[Java/03 - Program Structure/02 - Strings|Strings]]: `equals` vs `==`, concatenation performance
