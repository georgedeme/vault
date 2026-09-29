# Type Casting in Java

Type casting is the conversion of a value from one data type to another. Java performs some conversions automatically and requires others to be written explicitly. Understanding which category a conversion falls into — and what happens to the value during the conversion — is essential, since several common operations produce results that are not immediately obvious from the source code.

## Contents

- [[#1. Two Categories of Casting|1. Two Categories of Casting]]
- [[#2. Narrowing Between Integer Types — Overflow and Wraparound|2. Narrowing Between Integer Types — Overflow and Wraparound]]
- [[#3. Narrowing Between Floating-Point and Integer Types|3. Narrowing Between Floating-Point and Integer Types]]
- [[#4. Widening Between Integer and Floating-Point Types — Precision Loss|4. Widening Between Integer and Floating-Point Types — Precision Loss]]
- [[#5. char — A Special Case|5. char — A Special Case]]
- [[#6. Binary Numeric Promotion — Mixed-Type Arithmetic|6. Binary Numeric Promotion — Mixed-Type Arithmetic]]
- [[#7. Reference (Object) Casting|7. Reference (Object) Casting]]
- [[#8. What Casting Cannot Do|8. What Casting Cannot Do]]
- [[#9. Autoboxing and Unboxing (Related, Not True Casting)|9. Autoboxing and Unboxing (Related, Not True Casting)]]
- [[#10. Quick Reference — Non-Obvious Outcomes|10. Quick Reference — Non-Obvious Outcomes]]
- [[#11. Summary|11. Summary]]

---

## 1. Two Categories of Casting

### 1.1 Implicit Casting (Widening)

Also called **widening conversion**. The compiler performs this automatically because the destination type has a wider range than the source type, so the value's **magnitude** is always preserved. It is not always lossless, though: `int -> float`, `long -> float` and `long -> double` can silently lose **precision** (see [[#4. Widening Between Integer and Floating-Point Types — Precision Loss|section 4]]).

```java
int i = 100;
long l = i;      // int -> long, implicit
float f = l;     // long -> float, implicit
double d = f;    // float -> double, implicit
```

**Widening order for numeric primitives:**

```
byte -> short -> int -> long -> float -> double
```

`char` widens to `int`, `long`, `float`, and `double`, but is a separate branch from `byte`/`short` (see [[#5. char — A Special Case|char — A Special Case]]).

### 1.2 Explicit Casting (Narrowing)

Also called **narrowing conversion**. The destination type has a smaller range than the source, so data can be lost. The programmer must write the cast explicitly using `(type)` to acknowledge that risk:

```java
double d = 9.78;
int i = (int) d;   // explicit cast required, i == 9
```

If the cast is omitted, the code does not compile:

```java
int i = d;   // compile error: incompatible types: possible lossy conversion from double to int
```

`short <-> char` and `byte -> char` also need an explicit cast even though the sizes don't shrink (or even grow), because neither type's range contains the other's: `char` has no negatives, and `short`/`byte` can't hold values above 32,767 / 127.

### 1.3 Exceptions — Implicit Narrowing

Narrowing is *usually* explicit, but there are two cases where the compiler narrows for you:

1. **Compile-time constants.** If the right-hand side is a constant expression of type `int` (or `byte`/`short`/`char`) whose value fits in the target `byte`, `short` or `char`, the narrowing is implicit:

   ```java
   byte b = 10;              // OK — 10 is an int constant that fits in byte
   char c = 'a' + 1;         // OK — constant expression, value 98 fits in char
   final int K = 65;
   char k = K;               // OK — K is a constant variable
   byte tooBig = 200;        // compile error — doesn't fit in byte
   int v = 5;
   byte notConst = v;        // compile error — v is not a constant
   int fromLong = 5L;        // compile error — rule doesn't apply to long constants
   ```

2. **Compound assignment operators** (`+=`, `-=`, `*=`, `/=`, …) contain a hidden cast back to the left-hand type: `b += x` means `b = (byte) (b + x)`. So they compile even when the plain form doesn't — and they can silently wrap:

   ```java
   byte b = 10;
   // b = b + 1;   // compile error: b + 1 is int
   b += 1;         // OK — implicit (byte) cast
   b += 300;       // also compiles! b == (byte) 311 == 55, silent wraparound
   ```

   `++` and `--` behave the same way (`b++` compiles for a `byte`).

---

## 2. Narrowing Between Integer Types — Overflow and Wraparound

When a value is narrowed to a smaller integer type, Java keeps only the lowest-order bits that fit in the destination type. If the original value doesn't fit, the result silently **wraps around** rather than throwing an error or clamping.

```java
int i = 200;
byte b = (byte) i;   // b == -56
```

> [!info]- Why does `200` become `-56`?
> `byte` is 8 bits, signed, range −128 to 127. The bit pattern for 200 is `11001000`. Reinterpreted as a signed 8-bit value, that pattern represents −56.

**More examples:**

| Expression | Result | Reason |
|---|---|---|
| `(byte)(127 + 1)` | `-128` | wraps past the max `byte` value |
| `(byte) 300` | `44` | 300 mod 256 = 44 |
| `(short)(int) 70000` | `4464` | exceeds `short` range (−32,768 to 32,767), wraps |
| `(int)(long) 3_000_000_000L` | `-1294967296` | exceeds `int` range (−2,147,483,648 to 2,147,483,647), wraps |

(The inner `(int)` and `(long)` casts are redundant — `70000` is already an `int` literal and `3_000_000_000L` already a `long` — they're only there to make the source type visible.)

This wraparound happens with **no warning or exception at runtime** — it is a frequent source of silent bugs, especially when casting user input or values from I/O into a smaller type without validating range first.

> [!example]- Worked example — `(short)(int) 70000`
> `70000` starts as an `int`, which is 32 bits wide. In binary, padded to 32 bits, it is:
>
> ```
> 00000000 00000001 00010001 01110000
> ```
>
> `short` is only 16 bits wide, so the cast keeps just the **lowest-order 16 bits** and discards the rest:
>
> ```
> 32-bit int:   00000000 00000001 | 00010001 01110000
>                  discarded       |    kept (16 bits)
> ```
>
> The kept bits are `0001000101110000`. Reinterpreting this 16-bit pattern as a **signed** `short`:
>
> - The leftmost bit (the sign bit) is `0`, so the value is positive — no sign-flip happens this time, unlike the `byte` example above where the sign bit was `1`.
> - Converting the remaining bits to decimal: `0001000101110000` = 4464.
>
> So `(short)(int) 70000` produces `4464` simply because the top 16 bits of `70000`'s 32-bit representation are thrown away, leaving a smaller, unrelated value behind. This result happens to be positive only because bit 15 of the truncated pattern was `0`; had that bit been `1`, the same discard-and-reinterpret process would have produced a negative `short`, exactly as it did for `byte` above.

---

## 3. Narrowing Between Floating-Point and Integer Types

Casting a floating-point value to an integer type **truncates toward zero** — it does not round.

```java
double d1 = 9.99;
int i1 = (int) d1;   // i1 == 9, not 10

double d2 = -9.99;
int i2 = (int) d2;   // i2 == -9, not -10
```

If you want rounding instead of truncation, cast the result of `Math.round()`:

```java
int rounded = (int) Math.round(9.99);   // 10
```

The cast is needed because `Math.round(double)` returns a `long` (`Math.round(float)` returns an `int`). Also note that `Math.round` rounds halves **up** (towards positive infinity), not away from zero: `Math.round(2.5) == 3` but `Math.round(-2.5) == -2`.

If a floating-point value is outside the range of `int` or `long`, the result is clamped to the nearest boundary (this differs from the wraparound behavior seen with integer-to-integer narrowing; for `byte`/`short`/`char` see the warning below the table):

| Expression | Result | Reason |
|---|---|---|
| `(int) 1e30` | `2147483647` | clamped to `Integer.MAX_VALUE` |
| `(int) -1e30` | `-2147483648` | clamped to `Integer.MIN_VALUE` |
| `(int) Double.NaN` | `0` | `NaN` converts to `0` by definition |
| `(long) Double.POSITIVE_INFINITY` | `9223372036854775807` | clamped to `Long.MAX_VALUE` |
| `(byte) 1e30` | `-1` | clamped to `int` first, **then** wrapped to `byte` (see below) |
| `(byte) 300.7` | `44` | truncated to `int` `300`, then wrapped (300 mod 256) |

> [!warning] Clamping only happens to `int` or `long`
> A floating-point value cast to `byte`, `short` or `char` is converted in **two steps**: first to `int` (truncate toward zero, clamp if out of `int` range), then from `int` to the smaller type by ordinary integer narrowing, which **wraps**. So `(byte) 1e30` is not `127`: `1e30` clamps to `Integer.MAX_VALUE` (`0x7FFFFFFF`), and keeping its low 8 bits gives `0xFF` = `-1`. Likewise `(short) 1e30 == -1` and `(char) 1e30 == '￿'` (65535).

### 3.1 Narrowing double to float

Narrowing between the two floating-point types follows neither rule above — it **rounds** to the nearest `float`, and out-of-range values neither wrap nor clamp:

| Expression | Result | Reason |
|---|---|---|
| `(float) 0.1` | nearest `float` to 0.1 | rounded (so `(float) 0.1 == 0.1` is `false`) |
| `(float) 1e40` | `Infinity` | too large for `float` → overflows to ±`Infinity` |
| `(float) 1e-50` | `0.0` | too small for `float` → underflows to (signed) zero |

---

## 4. Widening Between Integer and Floating-Point Types — Precision Loss

Widening is not always lossless. `float` has only 24 bits of mantissa (significand) precision and `double` has 53, so `int -> float`, `long -> float` and `long -> double` can silently lose precision despite being *implicit* conversions. (`int -> double` is always exact, since 32 bits fit in 53.)

```java
int big = 16_777_217;                   // 2^24 + 1 — needs 25 bits
float f = big;                          // implicit widening — no cast needed
System.out.println((int) f);            // 16777216 — the last bit was lost
System.out.println((int) f == big);     // false

long lb = (1L << 53) + 1;               // 2^53 + 1 — needs 54 bits
double d = lb;                          // implicit widening
System.out.println((long) d == lb);     // false — even double can't hold it
```

The first integer that `float` cannot represent exactly is 2^24 + 1 = 16,777,217; for `double` it is 2^53 + 1. Every `int`/`long` below those limits (in absolute value) converts exactly.

> [!warning] Trick: a lossy round trip can still compare equal
> ```java
> long l = Long.MAX_VALUE;         // 2^63 − 1
> float f = l;                     // rounds UP to exactly 2^63
> System.out.println(f);           // 9.223372E18
> System.out.println((long) f == l); // true!
> ```
> Precision *was* lost (`f` is 2^63, one more than `Long.MAX_VALUE`), but converting back with `(long) f` **clamps** the out-of-range value to `Long.MAX_VALUE` (see [[#3. Narrowing Between Floating-Point and Integer Types|section 3]]), which happens to equal the original. So a round-trip test does not prove that a conversion was exact.

---

## 5. `char` — A Special Case

`char` is a 16-bit **unsigned** type (range 0 to 65,535) representing a UTF-16 code unit. It behaves differently from the other integer types in casting:

```java
char c1 = 'A';
int i = c1;          // implicit, i == 65 (the Unicode code point)

int i2 = 65;
char c2 = (char) i2; // explicit cast required, c2 == 'A'
```

**Casting a negative number to `char` does not produce a negative result** — because `char` is unsigned, the bit pattern is reinterpreted as an unsigned value:

```java
int negative = -1;
char c = (char) negative;
System.out.println((int) c);   // 65535, not -1
```

**`char` arithmetic promotes to `int`.** Adding two `char` values (or a `char` and an `int`) produces an `int`, not a `char` — so the result must be cast back explicitly to store it as a `char`:

```java
char a = 'a';
char b = 1;
// char c = a + b;       // compile error: possible lossy conversion from int to char
char c = (char) (a + b); // c == 'b'
```

Note that `char b = 1;` compiles without a cast because `1` is a constant that fits in `char` (see [[#1.3 Exceptions — Implicit Narrowing|1.3]]); likewise `char c = 'a' + 1;` compiles, and `c += 1;` compiles because of the hidden cast in compound assignment.

> [!tip] Common pitfall
> This is easy to get wrong when doing character-shifting logic (e.g. a Caesar cipher), where every intermediate `char + int` expression yields `int` and needs an explicit cast back.

---

## 6. Binary Numeric Promotion — Mixed-Type Arithmetic

When a binary arithmetic, comparison or bitwise operator (`+`, `-`, `*`, `/`, `%`, `<`, `==`, `&`, `|`, `^`, etc.) is applied to two numeric operands — whether or not their types differ — Java promotes both operands to a common type **before** performing the operation, following these rules in order:

1. If either operand is `double`, the other is converted to `double`.
2. Else if either operand is `float`, the other is converted to `float`.
3. Else if either operand is `long`, the other is converted to `long`.
4. Else both operands are converted to `int` (this includes `byte`, `short`, and `char` — they are **always** promoted to at least `int` in an arithmetic expression, even `byte + byte`).

```java
byte b1 = 10, b2 = 20;
// byte sum = b1 + b2;      // compile error: result of b1 + b2 is int
int sum = b1 + b2;          // fine — both bytes promoted to int
byte sum2 = (byte) (b1 + b2); // fine — explicit cast back down
```

Two related special cases:

- **Unary `-`, `+` and `~`** also promote `byte`/`short`/`char` to `int`: `byte n = -b1;` is a compile error.
- **Shift operators (`<<`, `>>`, `>>>`) do not use binary promotion.** Each operand is promoted on its own, and the result has the type of the (promoted) *left* operand: `1 << 33L` is an `int` (value `2`, since `int` shifts use only the low 5 bits of the distance: 33 & 31 = 1), not a `long`.

### 6.1 Integer Division Truncates Before Any Promotion to the Result Type

This is one of the most common sources of unexpected results in Java. Division between two integer types produces an integer result — truncated — **before** it is ever assigned or widened to a floating-point variable.

```java
int a = 7;
int b = 2;

double result = a / b;      // result == 3.0, NOT 3.5
```

> [!info]- Why does this happen?
> `a / b` is evaluated entirely in `int` arithmetic first (`7 / 2 == 3`), and *then* the `int` result `3` is widened to `double` for the assignment. The division never "knows" it's about to be assigned to a `double`.

To get the mathematically expected result, at least one operand must be a floating-point type **before** the division happens:

```java
double result1 = (double) a / b;   // 3.5 — a is cast first, forcing floating-point division
double result2 = a / (double) b;   // 3.5 — same effect, either operand works
double result3 = a / 2.0;          // 3.5 — literal 2.0 is already double
double result4 = (double) (a / b); // 3.0 — WRONG: casts the already-truncated int result
```

> [!warning] Common mistake
> `result4` is a common mistake: the parentheses cast the *result* of the integer division, not an operand, so truncation has already happened by the time the cast runs.

### 6.2 The Ternary Operator Also Applies Numeric Promotion

A subtle case: when both result branches of the conditional (ternary) operator `?:` are numeric, it converts them to a common type — in most cases by binary numeric promotion — even though only one branch is ever "used" at runtime.

```java
int x = 5;
double result = true ? x : 2.0;
System.out.println(result);   // 5.0, and the expression's static type is double

// Contrast with an if/else, which has no such promotion:
double result2;
if (true) {
    result2 = x;      // x (int) assigned into a double — 5.0, same value
} else {
    result2 = 2.0;
}
```

In the ternary case, because the second branch (`2.0`) is `double`, the *entire expression* is typed `double` at compile time — so even though the `true` branch selects `x`, `x` is promoted to `5.0`. This rarely changes the numeric value, but it does change the static type of the expression, which matters when the ternary result feeds into overload resolution or is itself part of a larger expression.

> [!warning] Ternary exceptions and traps
> The ternary's rules are **not** exactly binary numeric promotion:
> - If one branch is `byte`/`short`/`char` and the other is an `int` **constant** that fits in that type, the result keeps the smaller type:
>   ```java
>   System.out.println(true ? 'a' : 0);  // prints a   (type char)
>   int zero = 0;
>   System.out.println(true ? 'a' : zero); // prints 97 (type int — zero is not a constant)
>   ```
>   Similarly, `byte` vs `short` gives `short` (not `int`).
> - Wrapper-typed branches are **unboxed** and promoted too:
>   ```java
>   Object o = true ? Integer.valueOf(1) : Double.valueOf(2.0);
>   System.out.println(o);   // 1.0 — a Double, not the Integer 1
>
>   Integer n = null;
>   int r = true ? n : 0;    // NullPointerException — n is unboxed
>   ```

---

## 7. Reference (Object) Casting

Casting also applies to object references, and works differently from primitive casting — no bits are reinterpreted; only the *compile-time type* used to access the object changes.

### 7.1 Upcasting (Implicit)

Casting a subclass reference to a superclass (or interface) type is always safe and implicit:

```java
class Animal {}
class Dog extends Animal {}

Dog d = new Dog();
Animal a = d;   // implicit upcast — a Dog "is an" Animal
```

### 7.2 Downcasting (Explicit) and `ClassCastException`

Casting a superclass reference back down to a subclass requires an explicit cast, and is only safe if the object being referenced is *actually* an instance of that subclass at runtime:

```java
Animal a = new Dog();
Dog d = (Dog) a;        // OK — a really does refer to a Dog

Animal a2 = new Animal();
Dog d2 = (Dog) a2;      // compiles, but throws ClassCastException at runtime
```

The compiler only checks that the cast is *plausible* given the declared types (i.e. that some object could exist that is an instance of both — for classes, that one is a subclass of the other); it cannot know what the actual runtime object will be. Use `instanceof` to check before downcasting:

```java
if (a instanceof Dog) {
    Dog d = (Dog) a;
    // safe to use d here
}
```

Since Java 16, pattern matching lets you combine the check and the cast:

```java
if (a instanceof Dog d) {
    // d is already available here, no separate cast needed
}
```

### 7.3 Casting Between Unrelated Types Fails at Compile Time

If two reference types have no inheritance relationship at all, the cast is rejected before the program even runs:

```java
String s = "hello";
Integer i = (Integer) s;   // compile error: incompatible types
```

This differs from the `Animal`/`Dog` case above, where the cast compiles (because the types *are* related) but can still fail at runtime.

> [!warning] Interfaces are the exception
> A cast from a **non-`final`** class to an interface compiles even if the class doesn't implement it, because some subclass might:
> ```java
> Animal a = new Animal();
> Runnable r = (Runnable) a;   // compiles (a subclass of Animal could implement Runnable)
>                              // → ClassCastException at runtime
> ```
> If the class is `final` (like `String` or `Integer`) and doesn't implement the interface, no such subclass can exist, so the cast is a compile error.

---

## 8. What Casting Cannot Do

- **`boolean` cannot be cast to or from any numeric type**, unlike in C/C++. `(int) true` is a compile error.
- **Casting a `String` to a number is not casting** — `(int) "5"` does not compile. Use `Integer.parseInt("5")` or `Double.parseDouble("5")` instead (their rules and exceptions are in [[Java/01 - Foundations/05 - Reading Input#4. Parsing Strings into Numbers|Reading Input § 4]]).
- **Casting a number to a `String` is not casting either** — use `String.valueOf(5)`, `Integer.toString(5)`, or string concatenation (`"" + 5`).
- **Casting a floating-point value to an integer type does not round** — it truncates; see [[#3. Narrowing Between Floating-Point and Integer Types|section 3]]; use `Math.round()` first if rounding is intended. (The one narrowing cast that *does* round is `double -> float`, see [[#3.1 Narrowing double to float|3.1]].)

---

## 9. Autoboxing and Unboxing (Related, Not True Casting)

Autoboxing (converting a primitive to its wrapper class, e.g. `int` → `Integer`) and unboxing (the reverse) are conversions the compiler inserts automatically, but they are conceptually distinct from primitive widening/narrowing or reference casting (although a cast expression may include them, e.g. `(Integer) 5` or `(int) someInteger`). They are mentioned here because mixed expressions involving wrapper types can produce results that look like a casting problem but are actually an autoboxing/unboxing pitfall:

```java
Integer a = 1000;
Integer b = 1000;
System.out.println(a == b);        // usually false — compares object references, not values
System.out.println(a.equals(b));   // true — compares values (the correct way)

int c = 1000;
System.out.println(a == c);        // true — a is unboxed to int for the comparison
```

`Integer` values in the range −128 to 127 are cached by the JVM, so `==` comparisons on small boxed values can misleadingly return `true` while larger values return `false` — this is not a casting rule, but it is frequently confused with one. The upper bound of the cache can be raised with the JVM option `-XX:AutoBoxCacheMax=<n>`, in which case `a == b` above could print `true`; that's why the result is only "usually" `false`. To compare wrapper values, use `a.equals(b)` (or `a.intValue() == b.intValue()`), never `==`.

Other boxing gotchas that look like casting problems:

| Code | Result | Why |
|---|---|---|
| `Long x = 5;` | compile error | Java won't widen **and** box in one step (`int -> long -> Long`); write `5L` |
| `long y = Integer.valueOf(5);` | OK | unboxing **then** widening is allowed |
| `Long.valueOf(1).equals(1)` | `false` | `1` is boxed to `Integer`, and a `Long` never equals an `Integer` |
| `Integer n = null; int m = n;` | `NullPointerException` | unboxing `null` |

Generic collections can only hold wrappers (`List<Integer>`, never `List<int>`), so these traps show up constantly there, along with a few of their own, such as `list.remove(1)` removing an **index** rather than the value `1`. See [[Java/05 - Working with Data and Errors/02 - Generics#9. Generics and Autoboxing — Traps|Generics § 9]].

---

## 10. Quick Reference — Non-Obvious Outcomes

| Code | Result | Category |
|---|---|---|
| `(byte)(127 + 1)` | `-128` | integer overflow wraparound |
| `(int) 9.99` | `9` | truncation, not rounding |
| `(int) -9.99` | `-9` | truncation toward zero |
| `(char) -1` | `'￿'` (65535 as `int`) | unsigned reinterpretation |
| `7 / 2` | `3` | integer division truncates |
| `(double) (7 / 2)` | `3.0` | cast applied after truncation already happened |
| `(double) 7 / 2` | `3.5` | cast applied before division |
| `'a' + 1` | `98` (an `int`) | char promotes to int in arithmetic |
| `(char) ('a' + 1)` | `'b'` | explicit cast back to char |
| `(int) 1e30` | `2147483647` | clamped, not wrapped, for floating-point→int overflow (`1e30` is a `double` literal) |
| `(byte) 1e30` | `-1` | clamped to `int` first, then wrapped to `byte` |
| `true ? 5 : 2.0` | `5.0` | ternary promotes both branches to a common type |
| `true ? 'a' : 0` | `'a'` (a `char`) | ternary special case: `int` constant fits in `char` |
| `(float) 1e40` | `Infinity` | `double -> float` overflows, doesn't clamp |
| `byte b = 10; b += 300;` | `b == 54` | compound assignment hides a narrowing cast |
| `(long)(float) Long.MAX_VALUE == Long.MAX_VALUE` | `true` | precision lost, but clamping hides it |
| `new Integer(1000) == new Integer(1000)` | `false` | reference comparison, not a casting issue (`new Integer` is deprecated since Java 9 — use `Integer.valueOf`) |
| `(Dog)(Animal) new Animal()` | throws `ClassCastException` | compiles, fails at runtime |
| `(Integer)(Object) "text"` | throws `ClassCastException` | compiles, fails at runtime |

---

## 11. Summary

- **Widening** is implicit and generally safe, but can still lose *precision* (not magnitude) when converting large `int`/`long` values to `float`, or large `long` values to `double`.
- **Narrowing** is explicit except for fitting compile-time constants and compound assignment (`+=` etc.), and can lose data in different ways depending on the types involved: **wraparound** (integer-to-integer), **clamping** (floating-point-to-`int`/`long`, followed by wraparound for `byte`/`short`/`char`), or **rounding/overflow to `Infinity`** (`double -> float`).
- **Truncation, not rounding**, is the rule whenever a fractional value is narrowed to an integer type.
- **Operator promotion happens before assignment** — this is the root cause of the classic "integer division" surprise, and also applies, less intuitively, to the ternary operator.
- **`char` is unsigned** and promotes to `int` under arithmetic, which affects both negative-number casts and character-arithmetic code.
- **Reference casting** doesn't change any bits — it only changes what compile-time type is used to access an object, and can fail at runtime with `ClassCastException` even when it compiles cleanly.
