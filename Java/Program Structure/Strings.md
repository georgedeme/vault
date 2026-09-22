# Strings in Java

A `String` represents a sequence of characters. Unlike C-style languages, Java's `String` is not a primitive or a raw character array — it's a full class (`java.lang.String`), and it is **immutable**: once created, a `String` object's contents can never change. Every method that looks like it "modifies" a string actually returns a brand-new one. This chapter covers the `String` class, its common methods, the mutable `StringBuilder` alternative, and formatted output with `printf`/`String.format`.

For how `String` fits among Java's types generally, see [[Java/Foundations/Variables and Data Types|Variables and Data Types]] — this chapter assumes that background and focuses on `String`-specific behavior.

## Contents

- [[#1. The String Class and Immutability|1. The String Class and Immutability]]
- [[#2. Creating Strings — Literals vs. `new`|2. Creating Strings — Literals vs. `new`]]
- [[#3. Common String Methods|3. Common String Methods]]
- [[#4. String Concatenation|4. String Concatenation]]
- [[#5. StringBuilder|5. StringBuilder]]
- [[#6. Formatted Output — `printf` and `String.format`|6. Formatted Output — `printf` and `String.format`]]
- [[#7. Common Pitfalls|7. Common Pitfalls]]
- [[#8. Quick Reference|8. Quick Reference]]
- [[#9. Summary|9. Summary]]

---

## 1. The String Class and Immutability

A `String` object's character data cannot be changed after construction. Every method on `String` that appears to transform it — `toUpperCase()`, `replace()`, `substring()`, `trim()` — leaves the original object untouched and returns a new `String` with the result.

```java
String s = "hello";
s.toUpperCase();          // return value is discarded — s is still "hello"!
System.out.println(s);    // hello

String upper = s.toUpperCase();  // correct — capture the returned value
System.out.println(upper);       // HELLO
```

> [!warning] Common mistake
> Calling a `String` method for its "side effect" and ignoring the return value is one of the most common beginner bugs. There is no side effect — `String` has none to have. Always assign the result back to a variable (the same one, or a new one).

Immutability has real benefits beyond avoiding surprises: `String`s are safe to share freely across threads without synchronization, safe to use as `HashMap` keys (their hash code never changes), and safe to cache in the string pool (see [[#2. Creating Strings — Literals vs. `new`|section 2]]).

---

## 2. Creating Strings — Literals vs. `new`

```java
String a = "hi";              // literal — interned in the string pool
String b = "hi";              // same pooled object as a
String c = new String("hi");  // a new object on the heap, not pooled
```

The JVM maintains a **string pool** — a cache of string literals. Every time the same literal text appears in source code, it refers to the *same* pooled object rather than creating a new one. `new String(...)` deliberately bypasses the pool and always allocates a fresh object.

```java
System.out.println(a == b);          // true  — same pooled object
System.out.println(a == c);          // false — c is a separate heap object
System.out.println(a.equals(c));     // true  — same character content
```

> [!warning] Never compare `String` content with `==`
> `==` compares references (identity), not content. It happens to work for two literals because of pooling, but that's an implementation detail you shouldn't rely on — and it silently breaks the moment either side comes from `new String(...)`, user input, file I/O, or concatenation built at runtime. Always use `.equals()` (or `.equalsIgnoreCase()`) for content comparison.

---

## 3. Common String Methods

`String` provides a large API; the following covers the methods used most often. Every one of these returns a new value rather than modifying the original.

| Method | Purpose | Example |
|---|---|---|
| `length()` | number of characters | `"hello".length()` → `5` |
| `charAt(int)` | character at an index | `"hello".charAt(1)` → `'e'` |
| `substring(int)` | from index to end | `"hello".substring(2)` → `"llo"` |
| `substring(int, int)` | from index (inclusive) to index (exclusive) | `"hello".substring(1, 3)` → `"el"` |
| `indexOf(String)` | first index of a substring, or `-1` | `"hello".indexOf("l")` → `2` |
| `contains(CharSequence)` | whether a substring is present | `"hello".contains("ell")` → `true` |
| `equals(Object)` | content equality | `"hi".equals("hi")` → `true` |
| `equalsIgnoreCase(String)` | case-insensitive equality | `"Hi".equalsIgnoreCase("hi")` → `true` |
| `compareTo(String)` | lexicographic ordering (negative/zero/positive) | `"a".compareTo("b")` → negative |
| `toUpperCase()` / `toLowerCase()` | case conversion | `"Hi".toUpperCase()` → `"HI"` |
| `trim()` | removes leading/trailing whitespace (pre-Java 11 style, ASCII-only) | `"  hi  ".trim()` → `"hi"` |
| `strip()` | like `trim()`, but Unicode-aware (Java 11+) | `"  hi  ".strip()` → `"hi"` |
| `replace(CharSequence, CharSequence)` | replaces all occurrences | `"hello".replace("l", "L")` → `"heLLo"` |
| `split(String regex)` | splits into an array by a regex delimiter | `"a,b,c".split(",")` → `["a","b","c"]` |
| `concat(String)` | appends another string | `"foo".concat("bar")` → `"foobar"` |
| `isEmpty()` | `true` if length is `0` | `"".isEmpty()` → `true` |
| `isBlank()` | `true` if empty or all whitespace (Java 11+) | `"  ".isBlank()` → `true` |
| `toCharArray()` | converts to a `char[]` | `"hi".toCharArray()` → `['h','i']` |

```java
String greeting = "Hello, World!";
System.out.println(greeting.length());          // 13
System.out.println(greeting.substring(7, 12));   // World
System.out.println(greeting.toLowerCase());      // hello, world!
System.out.println(greeting.replace("World", "Java")); // Hello, Java!
```

> [!info]- Why does `indexOf` return `-1` instead of throwing?
> "Not found" is a common, expected outcome for a search — not an exceptional one — so `indexOf` signals it with a sentinel value (`-1`, which can never be a valid index) rather than an exception. Contrast this with `charAt(int)`, where an out-of-range index genuinely is a programming error and throws `StringIndexOutOfBoundsException`.

---

## 4. String Concatenation

The `+` operator is overloaded for `String` — when either operand is a `String`, `+` performs concatenation rather than arithmetic, and any non-`String` operand is automatically converted via its `toString()`.

```java
String name = "Ada";
int age = 30;
String message = "Name: " + name + ", Age: " + age;
// "Name: Ada, Age: 30"
```

```java
System.out.println(1 + 2 + "x");   // "3x"  — left-to-right: 1+2 is int addition first
System.out.println("x" + 1 + 2);   // "x12" — left-to-right: "x"+1 concatenates first
```

> [!warning] Concatenation order matters with mixed types
> `+` is evaluated strictly left-to-right. Numeric operands only add numerically if *both* sides at that point in the expression are numeric — as soon as a `String` appears, everything to its right becomes string conversion, one operand at a time. This is a frequent source of confusion, as shown above.

Each `+` between strings compiles (in most cases) into an efficient `StringBuilder` chain under the hood for a single expression — but concatenating inside a **loop** with `+=` builds a new `String` object on every iteration, which is quadratic in cost for large loops. See [[#5. StringBuilder|section 5]] for the fix.

---

## 5. StringBuilder

`StringBuilder` is a **mutable** sequence of characters — unlike `String`, its methods modify the object in place rather than returning a new one, which makes it efficient for building up text incrementally.

```java
StringBuilder sb = new StringBuilder();
sb.append("Hello");
sb.append(", ");
sb.append("World!");
System.out.println(sb.toString());   // Hello, World!
```

Common methods:

| Method | Purpose |
|---|---|
| `append(...)` | adds text to the end (overloaded for all primitive types and `Object`) |
| `insert(int, ...)` | inserts text at a given index |
| `delete(int, int)` | removes characters in a range |
| `deleteCharAt(int)` | removes a single character |
| `replace(int, int, String)` | replaces a range of characters |
| `reverse()` | reverses the sequence in place |
| `toString()` | converts to an immutable `String` |

```java
StringBuilder sb = new StringBuilder("Hello");
sb.append(" World");     // "Hello World"
sb.insert(5, ",");        // "Hello, World"
sb.reverse();              // "dlroW ,olleH"
```

Method calls on `StringBuilder` can be chained, since most return the `StringBuilder` itself:

```java
String result = new StringBuilder()
    .append("a")
    .append("b")
    .append("c")
    .toString();   // "abc"
```

> [!tip] When to prefer `StringBuilder` over `+`
> A handful of `+` concatenations in a single expression is fine — the compiler optimizes it. But building a string across **loop iterations** should use `StringBuilder`, since repeated `+=` on a `String` allocates a new object every pass:
> ```java
> StringBuilder sb = new StringBuilder();
> for (int i = 0; i < 1000; i++) {
>     sb.append(i).append(",");   // one mutable buffer, no per-iteration allocation
> }
> ```

---

## 6. Formatted Output — `printf` and `String.format`

`System.out.printf` and `String.format` both build output from a **format string** containing literal text plus `%`-prefixed **format specifiers**, each consumed in order by one of the trailing arguments. The difference is only what happens to the result: `printf` writes it straight to the stream (usually the console), while `String.format` returns it as a `String` to use however you like.

```java
System.out.printf("Name: %s, Age: %d%n", "Ada", 30);
// Name: Ada, Age: 30

String message = String.format("Name: %s, Age: %d", "Ada", 30);
// message now holds "Name: Ada, Age: 30" — nothing is printed
```

### 6.1 The Structure of a `printf`/`format` Call

Both methods share the same parameter shape:

```java
printf(String format, Object... args)
String.format(String format, Object... args)
```

- **The first parameter is always the format string** — a literal (or any `String`) containing ordinary text mixed with `%`-prefixed format specifiers. It is never itself one of the values being formatted; it's the *template*.
- **Everything after it is a varargs list of arguments** (`Object... args`) — the values to substitute into the template. You can pass any number of them, comma-separated, exactly like calling a method with multiple parameters.
- **Matching happens positionally, left to right**: the first `%` specifier encountered in the format string consumes the first argument, the second specifier consumes the second argument, and so on. The specifier's *type* (`%s`, `%d`, `%f`, ...) determines how its matched argument is converted to text — it does not select *which* argument is used; position does.

```java
System.out.printf("%s scored %d out of %d%n", "Ada", 90, 100);
//                  ^1st        ^2nd       ^3rd
//                  "Ada"        90         100
// Ada scored 90 out of 100
```

Walking through this call: `"%s scored %d out of %d%n"` is the format string — everything outside `%...` (`" scored "`, `" out of "`) is printed verbatim, unchanged. The three arguments `"Ada"`, `90`, `100` are supplied after it, separated by commas, and each is consumed by the next `%` specifier in the string, in order. `%n` needs no argument at all — it always inserts a line separator regardless of position.

Since primitive values (`int`, `double`, `boolean`, etc.) are autoboxed into their wrapper types to satisfy the `Object...` parameter, you can pass primitives, `String`s, and objects freely in the same call — no explicit conversion is needed on your part:

```java
int quantity = 3;
double price = 4.5;
String item = "apple";
System.out.printf("%d %s(s) at $%.2f each%n", quantity, item, price);
// 3 apple(s) at $4.50 each
```

**The number of specifiers that require an argument must match the number of arguments supplied** — every `%s`/`%d`/`%f`/etc. needs one corresponding argument in the same call; `%n` and `%%` are the only specifiers that don't consume one (see [[#6.4 Argument Order — Consuming, Skipping, and Reusing Arguments|section 6.4]] for what happens when the counts don't line up, and for reusing an argument more than once).

### 6.2 Common Conversions

| Specifier | Converts | Example |
|---|---|---|
| `%s` | any type, via `toString()` | `%s` with `"hi"` → `hi` |
| `%d` | integer types (`int`, `long`, etc.) | `%d` with `42` → `42` |
| `%f` | floating-point types | `%f` with `3.14` → `3.140000` |
| `%c` | a single character | `%c` with `'A'` → `A` |
| `%b` | boolean | `%b` with `true` → `true` |
| `%x` | integer, as hexadecimal | `%x` with `255` → `ff` |
| `%n` | platform-specific line separator | — |
| `%%` | a literal `%` character | `%%` → `%` |

> [!warning] Use `%n`, not `\n`
> `%n` inserts the platform's own line separator (`\r\n` on Windows, `\n` on Unix); `\n` always inserts a bare line feed regardless of platform. Inside a format string, prefer `%n` for portability — it's a format specifier processed by `printf`/`format`, while `\n` is a plain Java escape sequence baked into the string before formatting ever runs. Both usually look identical on screen, but they're not the same character sequence.

### 6.3 Width and Precision

A specifier can include flags, a minimum field width, and (for `%f`/`%s`) a precision, in the form `%[flags][width][.precision]conversion`:

```java
System.out.printf("[%10s]%n", "hi");     // [        hi]  — right-aligned, width 10
System.out.printf("[%-10s]%n", "hi");    // [hi        ] — left-aligned (- flag), width 10
System.out.printf("[%05d]%n", 42);       // [00042]      — zero-padded, width 5
System.out.printf("[%.2f]%n", 3.14159);  // [3.14]       — 2 digits after the decimal point
System.out.printf("[%8.2f]%n", 3.14159); // [    3.14]   — width 8, precision 2
```

> [!info]- Why does `%f` default to six decimal places?
> `%f` with no explicit precision always pads or truncates to exactly **six** digits after the decimal point — this is the same default `printf` uses in C, which Java's format syntax deliberately mirrors. `3.14` becomes `3.140000` unless a precision like `%.2f` is specified.

### 6.4 Argument Order — Consuming, Skipping, and Reusing Arguments

By default, as established in [[#6.1 The Structure of a `printf`/`format` Call|section 6.1]], specifiers consume arguments **left to right, one each**, in the order both appear. An explicit index (`n$`, placed right after the `%`) overrides that default and points a specifier at a *specific* argument position instead — which lets you reuse the same argument more than once, or print them out of order:

```java
System.out.printf("%s is %d, and %1$s is still %2$d%n", "Ada", 30);
// Ada is 30, and Ada is still 30 — %1$s and %2$d re-reference the 1st and 2nd args
```

Reading that call: the first `%s` and `%d` consume arguments 1 and 2 normally (positional, no index given). `%1$s` then explicitly re-targets argument 1 (`"Ada"`) a second time, and `%2$d` re-targets argument 2 (`30`) a second time — without either of them, the format string would run out of arguments after the first two specifiers.

```java
System.out.printf("%2$s before %1$s%n", "second", "first");
// first before second — explicit indices printed out of their argument order
```

> [!warning] Common mistakes
> - **Type mismatch** — `%d` requires an integer type; passing a `double` (even `3.0`) throws `IllegalFormatConversionException` at runtime. Use `%f` for floating-point values.
> - **Too few arguments** — a specifier with no matching argument (more `%`-specifiers than values supplied) throws `MissingFormatArgumentException` at runtime, not a compile error, since the format string is just a regular `String` as far as the compiler is concerned and isn't checked against the argument list until the call actually executes.
> - **Too many arguments** — extra arguments beyond what the specifiers consume are silently ignored; this is legal, not an error.
> - **Forgetting `%n`/newline entirely** — `printf` (unlike `println`) never adds a trailing newline on its own; consecutive calls run together on one line unless you include `%n` yourself.

---

## 7. Common Pitfalls

- **Ignoring a `String` method's return value**, expecting mutation — covered in [[#1. The String Class and Immutability|section 1]]. Nothing on `String` ever mutates.
- **Comparing content with `==`** instead of `.equals()` — covered in [[#2. Creating Strings — Literals vs. `new`|section 2]]. Works by accident for pooled literals, breaks for everything else.
- **Building large strings with `+=` in a loop** instead of `StringBuilder` — quietly quadratic, not a compile error or an obvious runtime failure, just slow at scale.
- **Passing the wrong type to a format specifier** (`%d` with a `double`, `%s` with `null` — the latter actually prints `"null"` safely, but mismatched numeric types throw at runtime).
- **`substring(int, int)` off-by-one confusion** — the end index is exclusive, so `s.substring(0, s.length())` is the whole string, and `s.substring(i, i)` is always `""`.

---

## 8. Quick Reference

| Code | Result | Why |
|---|---|---|
| `s.toUpperCase();` (return value discarded) | `s` unchanged | `String` is immutable; nothing mutates in place |
| `"hi" == new String("hi")` | `false` | one is pooled, one is a fresh heap object |
| `"hi".equals(new String("hi"))` | `true` | `.equals()` compares content, not identity |
| `1 + 2 + "x"` | `"3x"` | numeric addition happens before the first `String` operand |
| `"x" + 1 + 2` | `"x12"` | once a `String` appears, everything after concatenates |
| `String.format("%d", 3.0)` | throws `IllegalFormatConversionException` | `%d` requires an integer type, not `double` |
| `String.format("%.2f", 3.14159)` | `"3.14"` | precision truncates/rounds decimal digits |
| `printf("%n")` vs `printf("\n")` | both print a newline, but `%n` is platform-correct | `%n` is a format specifier, `\n` a literal escape |
| `"hello".substring(0, 5)` | `"hello"` | end index is exclusive, equals `length()` for "to the end" |

---

## 9. Summary

- `String` is immutable — every transforming method returns a **new** `String`; the original is never modified.
- String literals are pooled and shared; `new String(...)` always creates a separate object. Compare content with `.equals()`, never `==`.
- The core method set (`substring`, `indexOf`, `replace`, `split`, `trim`/`strip`, case conversion) covers most day-to-day text handling.
- `+` concatenation is fine for one-off expressions but is quadratic across loop iterations — use `StringBuilder` for building text incrementally.
- `printf` (writes to a stream) and `String.format` (returns a `String`) share the same format-specifier syntax (`%s`, `%d`, `%f`, width, precision, `%n`); mismatched conversion types and missing arguments fail at *runtime*, not compile time, since format strings are ordinary `String`s to the compiler.
