# Conditional Statements in Java

Conditional statements let a program choose which code runs based on a boolean condition. Java offers several forms — `if`, `if`/`else`, `else if` chains, the traditional `switch` statement, and the modern `switch` expression introduced in later versions of the language — and picking the right one, and understanding how each evaluates, avoids a number of subtle bugs.

## Contents

- [[#1. The if Statement|1. The if Statement]]
- [[#2. if / else|2. if / else]]
- [[#3. else if Chains|3. else if Chains]]
- [[#4. Nested Conditionals and the Dangling else|4. Nested Conditionals and the Dangling else]]
- [[#5. The Traditional switch Statement|5. The Traditional switch Statement]]
- [[#6. Fallthrough — Why break Matters|6. Fallthrough — Why break Matters]]
- [[#7. The Modern switch Expression (Java 14+)|7. The Modern switch Expression (Java 14+)]]
- [[#8. Pattern Matching in switch (Java 21+)|8. Pattern Matching in switch (Java 21+)]]
- [[#9. What Types Can Drive a switch|9. What Types Can Drive a switch]]
- [[#10. The Ternary Operator vs. if / else|10. The Ternary Operator vs. if / else]]
- [[#11. Common Pitfalls|11. Common Pitfalls]]
- [[#12. Summary|12. Summary]]

---

## 1. The `if` Statement

The simplest conditional. The block runs only if the condition evaluates to `true`.

```java
int age = 20;
if (age >= 18) {
    System.out.println("Adult");
}
```

The condition must be a `boolean` (or `Boolean`, which is auto-unboxed) — unlike C, an `int` cannot be used as a condition:

```java
int flag = 1;
// if (flag) { }   // compile error: incompatible types: int cannot be converted to boolean
if (flag != 0) { }  // must compare explicitly
```

If the body is a single statement, the braces are optional:

```java
if (age >= 18)
    System.out.println("Adult");
```

> [!tip] Use braces anyway
> Omitting braces is a common source of bugs when a second line is later added to the body without noticing it falls outside the `if` (see [[#11. Common Pitfalls|Common Pitfalls]]). Most style guides require braces on every `if`, even single-line ones.

---

## 2. `if` / `else`

Provides an alternative branch when the condition is `false`:

```java
int age = 15;
if (age >= 18) {
    System.out.println("Adult");
} else {
    System.out.println("Minor");
}
```

Exactly one of the two branches runs — never both, never neither.

---

## 3. `else if` Chains

Chains multiple conditions, evaluated top to bottom. The first `true` condition's branch runs, and the rest are skipped — including any conditions further down that would *also* have been `true`.

```java
int score = 82;

if (score >= 90) {
    System.out.println("A");
} else if (score >= 80) {
    System.out.println("B");
} else if (score >= 70) {
    System.out.println("C");
} else {
    System.out.println("F");
}
// prints "B" — the score >= 70 branch is never reached, even though it's also true
```

> [!warning] Order matters
> Conditions in an `else if` chain must be ordered from most specific to least specific when ranges overlap. Reversing the order above (`score >= 70` checked before `score >= 80`) would cause every score of 80 or above to incorrectly print `"C"`.

The trailing `else` is optional. If omitted and no condition matches, no branch runs at all.

---

## 4. Nested Conditionals and the Dangling `else`

An `else` always binds to the **nearest preceding unmatched `if`**, regardless of indentation. Indentation is purely cosmetic to the compiler — it does not determine which `if` an `else` belongs to.

```java
if (a)
    if (b)
        System.out.println("both true");
    else
        System.out.println("a true, b false");   // binds to the inner if (b), not outer if (a)
```

This is misleading if formatted to *suggest* the `else` belongs to the outer `if`:

```java
// Formatting below is misleading — the else still binds to "if (b)"
if (a)
    if (b)
        System.out.println("both true");
else
    System.out.println("a is false");   // WRONG belief — this still only runs when a is true and b is false
```

![[Conditionals - Dangling Else.excalidraw|800]]

> [!tip] Fix with braces
> Wrapping the inner `if` in braces removes the ambiguity entirely and makes the binding visually match the binding the compiler actually uses:
> ```java
> if (a) {
>     if (b) {
>         System.out.println("both true");
>     }
> } else {
>     System.out.println("a is false");
> }
> ```

---

## 5. The Traditional `switch` Statement

`switch` dispatches on the value of a single expression, comparing it against a list of `case` labels. It was historically restricted to `byte`, `short`, `char`, `int` (and their wrapper classes), `String` (since Java 7), and `enum` types.

```java
int day = 3;
String name;

switch (day) {
    case 1:
        name = "Monday";
        break;
    case 2:
        name = "Tuesday";
        break;
    case 3:
        name = "Wednesday";
        break;
    default:
        name = "Unknown";
        break;
}
System.out.println(name);   // Wednesday
```

- `case` labels must be **compile-time constants** — a `final` local variable initialized with a constant works, but a regular variable does not.
- `default` handles any value not matched by an explicit `case`. It's conventional to place it last, but it can legally appear anywhere in the `switch` body.
- Multiple labels can share one body by stacking them:

```java
switch (day) {
    case 6:
    case 7:
        System.out.println("Weekend");
        break;
    default:
        System.out.println("Weekday");
        break;
}
```

---

## 6. Fallthrough — Why `break` Matters

Without `break`, execution **falls through** to the next `case` body, regardless of whether that case's label matches. This is the single most common `switch` bug.

```java
int day = 2;
switch (day) {
    case 1:
        System.out.println("Monday");
    case 2:
        System.out.println("Tuesday");
    case 3:
        System.out.println("Wednesday");
    default:
        System.out.println("Unknown");
}
```

```
Tuesday
Wednesday
Unknown
```

![[Conditionals - Switch Fallthrough.excalidraw|800]]

> [!info]- Why does this print three lines?
> Execution jumps to the matching `case 2:` label and then runs **every statement below it** until it hits a `break` or the end of the `switch` block — it does not re-check any labels. Since none of the cases here have a `break`, control falls straight through `case 3` and into `default`.

`break` exits the `switch` block immediately:

```java
switch (day) {
    case 1:
        System.out.println("Monday");
        break;
    case 2:
        System.out.println("Tuesday");
        break;
    // ...
}
```

> [!tip] Intentional fallthrough
> Fallthrough is occasionally used deliberately (the stacked weekend labels in [[#5. The Traditional switch Statement|section 5]] are one example), so compilers don't warn by default on every missing `break`. Some static analyzers flag fallthrough cases that lack a `// fall through` comment, precisely because it's hard to tell intentional fallthrough from a forgotten `break` just by reading the code.

---

## 7. The Modern `switch` Expression (Java 14+)

Java 14 standardized a `switch` **expression** form (previewed in 12–13) using `->` arrow labels. It fixes fallthrough by design — each arrow's right-hand side is scoped independently, with no fall-through to the next label — and it can produce a value directly, so it can be used in an assignment, `return`, or anywhere a value is expected.

```java
int day = 3;
String name = switch (day) {
    case 1 -> "Monday";
    case 2 -> "Tuesday";
    case 3 -> "Wednesday";
    default -> "Unknown";
};
System.out.println(name);   // Wednesday
```

Multiple labels per branch use a comma, not stacked `case` lines:

```java
String type = switch (day) {
    case 6, 7 -> "Weekend";
    default -> "Weekday";
};
```

For a branch that needs multiple statements, use a block body with `yield` to produce the value:

```java
String description = switch (day) {
    case 1, 2, 3, 4, 5 -> {
        System.out.println("Logging a weekday");
        yield "Weekday";
    }
    case 6, 7 -> "Weekend";
    default -> throw new IllegalArgumentException("Invalid day: " + day);
};
```

> [!info] `yield` vs. `return`
> `yield` produces the value of a `switch` **expression** branch; it does not exit the enclosing method the way `return` would. Using `return` inside a `switch` expression's block would exit the whole method, not just supply that branch's value.

When every possible input is covered (e.g. all `enum` constants, or a `default` branch is present), the compiler considers the `switch` expression **exhaustive**, which is required — a `switch` expression must always produce a value for every possible input, unlike the old `switch` statement, where omitting `default` is legal.

---

## 8. Pattern Matching in `switch` (Java 21+)

`switch` can match on the **type** of the expression, binding a variable to the matched value automatically — no separate `instanceof` check and manual cast needed.

```java
Object obj = 42;

String result = switch (obj) {
    case Integer i -> "Integer: " + i;
    case String s -> "String: " + s;
    case null -> "It's null";
    default -> "Something else";
};
```

- `case null` is legal directly in a pattern-matching `switch` (it was a `NullPointerException` in a traditional `switch`, which never accepted a `null` selector).
- Patterns can carry a `when` clause (a **guard**) for extra conditions beyond the type check:

```java
String describe(Object obj) {
    return switch (obj) {
        case Integer i when i > 0 -> "Positive integer";
        case Integer i when i < 0 -> "Negative integer";
        case Integer i -> "Zero";
        case String s -> "String of length " + s.length();
        default -> "Unknown";
    };
}
```

- Record types can be **deconstructed** directly in a `case` label:

```java
record Point(int x, int y) {}

String locate(Object obj) {
    return switch (obj) {
        case Point(int x, int y) when x == 0 && y == 0 -> "Origin";
        case Point(int x, int y) -> "Point at (" + x + ", " + y + ")";
        default -> "Not a point";
    };
}
```

---

## 9. What Types Can Drive a `switch`

| Type | Traditional `switch` | Pattern-matching `switch` |
|---|---|---|
| `byte`, `short`, `char`, `int` (and wrappers) | Yes | Yes |
| `String` | Yes (since Java 7) | Yes |
| `enum` | Yes | Yes |
| `long`, `float`, `double`, `boolean` | **No** | No |
| Arbitrary reference types / records | No | Yes (Java 21+) |

`long`, `float`, `double`, and `boolean` have never been legal `switch` selector types — a `switch` on a `boolean` should simply be written as `if`/`else`, and a `switch` on a `long` or floating-point value must first be handled some other way (e.g. bucketed into ranges via `if`/`else if`).

---

## 10. The Ternary Operator vs. `if` / `else`

The ternary operator `?:` is an *expression*, not a statement — it evaluates to a value and can appear inside a larger expression, whereas `if`/`else` cannot.

```java
int a = 5, b = 10;
int max = (a > b) ? a : b;
```

It is well suited to short, single-value choices, but nesting ternaries to express multi-branch logic quickly becomes hard to read:

```java
// Legal, but hard to read at a glance
String grade = (score >= 90) ? "A" : (score >= 80) ? "B" : (score >= 70) ? "C" : "F";
```

An `else if` chain or a `switch` expression is usually clearer once there are more than two outcomes.

> [!tip] See also
> The ternary operator has its own numeric-promotion behavior that can produce surprising types when its two branches don't match — covered in [[04 - Type Casting#6.2 The Ternary Operator Also Applies Numeric Promotion|Type Casting, section 6.2]].

---

## 11. Common Pitfalls

- **Missing braces on multi-line intent.** Adding a second statement under an `if` without braces attaches it unconditionally, not to the `if`:

```java
if (age >= 18)
    System.out.println("Adult");
    System.out.println("Can vote");   // runs regardless of age — not part of the if
```

- **Using `=` instead of `==`.** In Java this is caught at compile time for `boolean` conditions (unlike C), because `age = 18` is an `int` assignment expression, not a `boolean` — so it won't silently compile unless the variable itself is a `boolean`:

```java
boolean isAdult = false;
// if (isAdult = true) { }   // compiles! Assigns true to isAdult, then evaluates that as the condition — always true
if (isAdult == true) { }     // intended comparison (though `if (isAdult)` is the idiomatic form)
```

- **Forgetting `break` in a traditional `switch`** — see [[#6. Fallthrough — Why break Matters|section 6]].
- **Comparing objects (including boxed types and `String`) with `==` inside a condition** instead of `.equals()` — this compares references, not contents, and is a frequent source of conditions that are `true`/`false` unpredictably depending on caching or interning. See the autoboxing caching pitfall in [[04 - Type Casting#9. Autoboxing and Unboxing (Related, Not True Casting)|Type Casting, section 9]].
- **Non-exhaustive `switch` expressions.** Unlike a `switch` statement, a `switch` expression must cover every possible input (via `default` or, for an `enum`, every constant) — otherwise it fails to compile.

---

## 12. Summary

- `if` / `else` / `else if` evaluate top to bottom; the first `true` branch runs and the rest are skipped, so condition order matters whenever ranges overlap.
- An `else` binds to the nearest unmatched `if`, not to whichever `if` the indentation visually suggests — brace nested conditionals to avoid the dangling-`else` trap.
- The traditional `switch` **statement** falls through by default unless each case ends with `break`; the modern `switch` **expression** (`->` syntax, Java 14+) has no fallthrough and can produce a value directly via `yield`.
- Pattern matching in `switch` (Java 21+) can match on type, bind a variable, apply `when` guards, deconstruct records, and — unlike a traditional `switch` — legally match `null`.
- `switch` can only be driven by `byte`/`short`/`char`/`int` (and wrappers), `String`, `enum`, or (with pattern matching) arbitrary reference types — never `long`, `float`, `double`, or `boolean`.
- The ternary operator is an expression suited to simple two-way choices; beyond that, `else if` or a `switch` expression stays more readable.
