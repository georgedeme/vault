# Variables and Data Types in Java

A <span class="hl-blue">variable</span> is a named storage location that holds a value of a specific type. Java is **statically and strongly typed**: every variable's type is fixed at compile time, and the compiler rejects any operation that isn't valid for that type. This chapter covers how variables are declared, the two fundamental type categories, how literals are written, and the handful of places where the rules produce results that aren't obvious from a quick reading of the code.

For how values convert *between* types (widening, narrowing, promotion), see [[Java/Type Casting|Type Casting]] — this chapter focuses on declaring and initializing variables, not converting them.

## Contents

- [[#1. Declaring a Variable|1. Declaring a Variable]]
- [[#2. Primitive Types|2. Primitive Types]]
- [[#3. Reference Types|3. Reference Types]]
- [[#4. Literals|4. Literals]]
- [[#5. Local, Instance, and Static Variables|5. Local, Instance, and Static Variables]]
- [[#6. Default Values|6. Default Values]]
- [[#7. Constants (`final`)|7. Constants (`final`)]]
- [[#8. Scope and Shadowing|8. Scope and Shadowing]]
- [[#9. Type Inference with `var`|9. Type Inference with `var`]]
- [[#10. Quick Reference — Non-Obvious Outcomes|10. Quick Reference — Non-Obvious Outcomes]]
- [[#11. Summary|11. Summary]]

---

## 1. Declaring a Variable

A declaration states a variable's type and name; initialization gives it a value. These can happen together or separately:

```java
int age;        // declaration only
age = 21;       // initialization, separately

int score = 100; // declaration + initialization together
```

Multiple variables of the same type can be declared in one statement:

```java
int x = 1, y = 2, z = 3;
```

**Naming rules (enforced by the compiler):**
- Must start with a letter, `_`, or `$`; subsequent characters may also include digits.
- Cannot be a reserved keyword (`class`, `int`, `if`, `return`, etc.).
- Case-sensitive — `total` and `Total` are different variables.

**Naming conventions (not enforced, but standard):**
- `camelCase` for variables and methods (`totalScore`).
- `UPPER_SNAKE_CASE` for constants (`MAX_SIZE`).
- `PascalCase` for class names (`BankAccount`).

> [!warning] Common mistake
> `$` and `_` are legal in identifiers, so `$total` and `_total` compile fine — but a name consisting of a **single underscore**, `_`, is specifically reserved and **cannot** be used as an identifier since Java 9. `int _ = 5;` is a compile error.

---

## 2. Primitive Types

Java has exactly **eight primitive types**. They are not objects, hold their value directly (not a reference), and always have a default value when used as fields (see [[#6. Default Values|section 6]]).

| Type | Size | Range | Default | Wrapper Class |
|---|---|---|---|---|
| `byte` | 8-bit | −128 to 127 | `0` | `Byte` |
| `short` | 16-bit | −32,768 to 32,767 | `0` | `Short` |
| `int` | 32-bit | −2,147,483,648 to 2,147,483,647 | `0` | `Integer` |
| `long` | 64-bit | −9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 | `0L` | `Long` |
| `float` | 32-bit (IEEE 754) | ~6–7 significant decimal digits | `0.0f` | `Float` |
| `double` | 64-bit (IEEE 754) | ~15–16 significant decimal digits | `0.0d` | `Double` |
| `char` | 16-bit, **unsigned** | `\u0000` to `￿` (0 to 65,535) | `'\u0000'` | `Character` |
| `boolean` | not precisely defined | `true` / `false` only | `false` | `Boolean` |

> [!info]- Why doesn't the spec define a bit size for `boolean`?
> The Java Language Specification deliberately leaves `boolean`'s in-memory size unspecified — it's conceptually one bit, but the JVM is free to implement it however is most efficient (in practice, most JVMs use a full byte or even a 32-bit `int` slot on the stack for a `boolean` local variable). This is different from `byte`/`short`/`int`/etc., whose sizes **are** fixed exactly by the spec. It has no practical effect on your code, but it explains why `boolean` has no defined bit-width in the table above.

`byte`, `short`, `int`, `long`, `float`, and `double` are all numeric and participate in arithmetic and widening/narrowing as described in [[Java/Type Casting|Type Casting]]. `char` is numeric too (it can be used in arithmetic), but is unsigned and represents a UTF-16 code unit rather than a general-purpose number. `boolean` is not numeric at all — see [[Java/Type Casting#8. What Casting Cannot Do|What Casting Cannot Do]] for why it can't be cast to or from numeric types.

---

## 3. Reference Types

Everything that isn't a primitive is a <span class="hl-blue">reference type</span>: objects, arrays, and `String`. A reference variable doesn't store the object itself — it stores a reference (effectively, an address) to an object on the heap, or the special value `null`, meaning "refers to nothing."

```java
String name = "Ada";     // name holds a reference to a String object
int[] scores = {90, 85}; // scores holds a reference to an array object
Object obj = null;       // obj refers to nothing
```

> [!warning] Common mistake
> `String` is **not** a primitive, despite `String s = "hi";` looking similar to `int i = 5;`. It's a full class, and `"hi"` is a reference to a `String` object stored in the JVM's **string pool** (a special cache for string literals). This matters for `==` comparisons: `"hi" == "hi"` is `true` (same pooled object), but `new String("hi") == "hi"` is `false` (a freshly constructed object, not pooled) even though `.equals()` returns `true` for both. Never compare `String` contents with `==`; always use `.equals()`.

---

## 4. Literals

A literal is a fixed value written directly in source code. Each type has its own literal syntax, and several of the rules here are common sources of compile errors.

### 4.1 Integer Literals

```java
int decimal = 42;
int binary  = 0b101010;   // 42, binary (0b prefix)
int octal   = 052;        // 42, octal (leading 0)
int hex     = 0x2A;       // 42, hexadecimal (0x prefix)
int spaced  = 1_000_000;  // underscores allowed as visual separators (Java 7+)
```

Underscores can appear **between** digits only — not at the start, end, immediately next to a decimal point, or next to a prefix/suffix:

```java
int bad1 = _1000;    // compile error — leading underscore
int bad2 = 1000_;    // compile error — trailing underscore
int bad3 = 1_.5;     // compile error — underscore next to decimal point
```

### 4.2 The `long` Suffix

An integer literal is `int` by default. To assign a value outside `int`'s range, the literal must carry an `L` (or `l`, though `L` is preferred to avoid confusion with the digit `1`) suffix:

```java
long big = 3000000000L;   // OK — L suffix makes this a long literal
long bad = 3000000000;    // compile error: integer number too large
```

> [!info]- Why does the version without `L` fail?
> `3000000000` is written as a plain integer literal, so the compiler first treats it as an `int` — but it exceeds `Integer.MAX_VALUE` (2,147,483,647) *before* any assignment or widening ever happens. The error occurs at the literal itself, not at the assignment. Adding `L` tells the compiler to treat the literal as a `long` from the start, whose range comfortably fits the value.

### 4.3 The `float` Suffix

A floating-point literal is `double` by default. Assigning one to a `float` variable without an `f` suffix is a narrowing conversion and does not compile:

```java
float f1 = 1.0f;   // OK — f suffix makes this a float literal
float f2 = 1.0;    // compile error: incompatible types, possible lossy conversion
float f3 = (float) 1.0;  // OK — explicit cast also works
```

`d`/`D` suffixes exist for `double` too, but are optional since `double` is already the default for decimal literals.

### 4.4 The Most Negative `int` and `long` — A Special-Case Grammar Rule

<span class="hl-yellow">This one catches people who understand literal ranges well enough to expect it *not* to compile:</span>

```java
int min = -2147483648;   // compiles fine
```

`2147483648` by itself exceeds `Integer.MAX_VALUE` (2,147,483,647), so as a standalone literal it would be illegal — yet the line above compiles without any suffix or cast. This works because the Java grammar special-cases the exact token sequence `-2147483648` (a unary minus immediately followed by that literal) and treats it as the single literal `Integer.MIN_VALUE`, rather than parsing it as "negate `2147483648`." The same special case exists for `long`:

```java
long min = -9223372036854775808L;   // compiles — special-cased, like above

long broken = -(9223372036854775808L); // compile error!
```

The second line fails because wrapping the literal in parentheses breaks the special-cased token sequence — now the compiler must parse `9223372036854775808L` as a standalone literal first (which exceeds `Long.MAX_VALUE`), *then* negate it, and the standalone literal is illegal before negation ever applies.

### 4.5 Character Literals

```java
char letter = 'a';
char digit  = '9';          // a char, NOT the number 9
char code   = 97;           // 'a' — an int literal that fits char's range
char escape = '\n';         // newline
char unicode = 'A';    // 'A', written as a Unicode escape
```

> [!warning] Common mistake
> A `char` literal must be a **single** character in single quotes. `char c = 'ab';` is a compile error. Also note `'9'` (a character) and `9` (an integer) are entirely different values — `'9'` is actually the integer 57 under the hood (its Unicode code point), not 9.

### 4.6 Boolean Literals

`boolean` has exactly two literals: `true` and `false`. Unlike C/C++, integers cannot substitute for booleans:

```java
boolean flag = true;
boolean bad = 1;   // compile error — 1 is not a boolean in Java
if (1) { }          // compile error — condition must be boolean
```

---

## 5. Local, Instance, and Static Variables

Java has three variable categories, and **which one you're using changes whether it gets a default value**:

| Category | Declared | Gets a default value? |
|---|---|---|
| **Local variable** | Inside a method, constructor, or block | **No** — must be explicitly assigned before use |
| **Instance variable** (field) | Inside a class, outside any method, no `static` | Yes |
| **Static variable** | Inside a class, outside any method, with `static` | Yes (shared across all instances) |

```java
class Example {
    int instanceVar;         // default: 0 (field, gets a default)
    static int staticVar;    // default: 0 (static field, gets a default)

    void method() {
        int localVar;              // no default!
        System.out.println(localVar); // compile error: variable might not have been initialized
    }
}
```

> [!warning] Common mistake — this is one of the most-tested rules in Java
> Reading an uninitialized **local** variable is a *compile-time* error, not a runtime `0`/`null`. Reading an uninitialized **field** is perfectly legal and simply returns its default value. Students who test with fields first and locals later (or vice versa) are often surprised the same-looking code behaves differently.

Method **parameters** behave like local variables for this purpose — they must be supplied a value by the caller (there's no such thing as an "uninitialized" parameter, since a value is required at the call site), but they follow local-variable scoping and get no independent default.

---

## 6. Default Values

For fields (instance and static), the JVM guarantees the following defaults if no explicit initializer is given:

| Type | Default |
|---|---|
| `byte`, `short`, `int` | `0` |
| `long` | `0L` |
| `float` | `0.0f` |
| `double` | `0.0d` |
| `char` | `'\u0000'` (the null character — prints as nothing, not `0`) |
| `boolean` | `false` |
| Any reference type (`String`, arrays, objects) | `null` |

> [!info]- Why does `char`'s default print as blank instead of showing `0`?
> `'\u0000'` is a real, valid `char` value (Unicode code point 0), but it's a non-printing control character, so most consoles render it as nothing visible rather than an error or a `0`. If you convert it explicitly — `(int) '\u0000'` — you do get `0`, confirming it's the numeric default underneath.

**Local variables never get any of these defaults** — see [[#5. Local, Instance, and Static Variables|section 5]].

---

## 7. Constants (`final`)

The `final` keyword prevents a variable from being reassigned after its first assignment:

```java
final int MAX_SIZE = 100;
MAX_SIZE = 200;   // compile error — cannot assign a value to a final variable
```

By convention, constants are named in `UPPER_SNAKE_CASE`. `final` can apply to local variables, fields, static fields, and parameters.

### 7.1 Blank Finals

A `final` field doesn't have to be initialized at the point of declaration — it can be a **blank final**, as long as the compiler can prove it is assigned exactly once on every possible path before it's used (e.g. in every constructor):

```java
class Point {
    final int x;   // blank final — no initializer here

    Point(int x) {
        this.x = x;   // must be assigned here (or it's a compile error)
    }
}
```

### 7.2 `final` Doesn't Mean Immutable

`final` prevents *reassigning the variable* — it says nothing about whether the object the variable refers to can change internally:

```java
final int[] arr = {1, 2, 3};
arr[0] = 99;        // OK — the array's contents can change
arr = new int[5];   // compile error — arr itself cannot be reassigned
```

This is a frequent point of confusion: `final` on a reference variable locks the *reference*, not the object's mutable state.

---

## 8. Scope and Shadowing

A local variable's scope begins at its declaration and ends at the closing brace `}` of its enclosing block. A variable cannot be redeclared within a scope where it's already visible:

```java
void method() {
    int x = 1;
    {
        int x = 2;   // compile error — x is already defined in this method
    }
}
```

However, a **parameter or local variable is allowed to shadow an instance field** with the same name — this compiles, but hides the field within that scope:

```java
class Counter {
    int count = 0;

    void setCount(int count) {   // parameter shadows the field
        count = count;           // does nothing useful! assigns the parameter to itself
        this.count = count;      // correct — explicitly targets the field
    }
}
```

> [!warning] Common mistake
> `count = count;` inside `setCount` above compiles cleanly and does *nothing* to the field — both sides refer to the parameter, since the parameter shadows the field for the rest of that scope. This is a classic bug in constructors and setters. Use `this.fieldName = parameterName;` whenever a parameter intentionally shares a name with a field.

---

## 9. Type Inference with `var`

Since Java 10, `var` lets the compiler infer a local variable's type from its initializer, rather than writing the type explicitly:

```java
var count = 10;          // inferred as int
var name = "Ada";        // inferred as String
var list = new ArrayList<String>(); // inferred as ArrayList<String>
```

`var` is **not** dynamic typing — the type is fixed at compile time, exactly as if you'd written it explicitly. It's purely a source-code shorthand.

```java
var x = 10;
x = "hello";   // compile error — x is int, permanently, despite the var syntax
```

### 9.1 Where `var` Cannot Be Used

- **Fields, method parameters, and return types** — `var` is local-variables-only (except lambda parameters, permitted since Java 11).
- **Without an initializer** — `var x;` is a compile error; there's nothing to infer the type from.
- **With a bare `null` initializer** — `var x = null;` is a compile error, since `null` carries no type information to infer from. (`var x = (String) null;` compiles, because the cast supplies a type.)
- **In multi-variable declarations** — `var a = 1, b = 2;` is a compile error, even though the equivalent `int a = 1, b = 2;` is legal.
- **For array literals without `new`** — `var arr = {1, 2, 3};` is a compile error; you must write `var arr = new int[]{1, 2, 3};`.

> [!info]- Is `var` a reserved keyword?
> No — `var` is a **reserved type name**, not a keyword. This means it cannot be used as a class or interface name, but it *can* still be used as a regular variable, method, or package name: `int var = 5;` compiles fine. This is a deliberate design choice that kept `var`'s introduction from breaking any existing code that already used `var` as an identifier.

---

## 10. Quick Reference — Non-Obvious Outcomes

| Code | Result | Category |
|---|---|---|
| `long l = 3000000000;` | compile error | missing `L` suffix, literal exceeds `int` range |
| `float f = 1.0;` | compile error | literal is `double` by default, needs `f` suffix or cast |
| `int min = -2147483648;` | compiles | special-cased literal grammar for `Integer.MIN_VALUE` |
| `long x = -(9223372036854775808L);` | compile error | parentheses break the special-case, literal alone exceeds `long` range |
| `int x;` then `System.out.println(x);` (local) | compile error | local variables have no default value |
| `int x;` (instance field) then read | `0` | fields always get a default value |
| `char c = '\u0000';` printed | prints nothing (not `0`) | valid non-printing default char |
| `final int[] a = {1}; a[0] = 2;` | compiles, `a[0] == 2` | `final` locks the reference, not the contents |
| `var x = null;` | compile error | no type to infer from a bare `null` |
| `var a = 1, b = 2;` | compile error | `var` disallows multi-declarator statements |
| `boolean b = 1;` | compile error | Java booleans are not interchangeable with integers |
| `new String("hi") == "hi"` | `false` | one is pooled, one is a new heap object — use `.equals()` |
| parameter shadowing a field, then `x = x;` | field unchanged | both sides resolve to the parameter, not the field |

---

## 11. Summary

- Java has **eight primitive types** and everything else is a **reference type**; primitives hold values directly, references point to heap objects (or `null`).
- **Local variables get no default value** and must be definitely assigned before use (a compile-time check); **fields always do**.
- Numeric literals default to `int`/`double` — assigning outside those types (`long`, `float`) requires an explicit suffix (`L`, `f`) or cast.
- A handful of literal edge cases (`-2147483648`, underscore placement, `char` vs. `int` literals) are special-cased by the grammar and worth memorizing on their own.
- `final` prevents reassigning a variable, not mutating the object it refers to.
- `var` is compile-time type inference, not dynamic typing, and has several syntactic restrictions on where it's legal.
- Shadowing a field with a same-named parameter or local variable is legal but a common source of silent no-op bugs — disambiguate with `this.`.
