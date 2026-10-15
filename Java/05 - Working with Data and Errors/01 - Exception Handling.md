# Exception Handling in Java

An <span class="hl-blue">exception</span> is an object that reports that something went wrong while the program was running: a file that doesn't exist, a string that isn't a number, an index past the end of an array. When code **throws** an exception, normal execution stops and the JVM looks back through the method calls for code that **catches** it. If nothing catches it, the program ends with a stack trace. This chapter covers the `Throwable` hierarchy, checked vs. unchecked exceptions and the "catch or declare" rule, `throw` and `throws`, `try`/`catch`/`finally`, multi-catch, try-with-resources and suppressed exceptions, custom exceptions, chaining and rethrowing, reading a stack trace, exceptions in constructors and initializers, and good practice.

Earlier chapters already used `try`/`catch` with only a short explanation: [[Java/01 - Foundations/05 - Reading Input#5.3 Retrying with `try` and `catch`|Reading Input § 5.3]] (retrying after bad input) and [[Java/01 - Foundations/05 - Reading Input#9.1 Reading Lines and Parsing Them|§ 9.1]] (`throws IOException`). The overriding rules for `throws` are in [[Java/04 - Object-Oriented Programming/03 - Inheritance#3.3 The Rules for a Valid Override|Inheritance § 3.3]], and the way a reference's declared type fixes which checked exceptions a call can throw is in [[Java/04 - Object-Oriented Programming/04 - Polymorphism#2.3 The Declared Type Also Fixes the Return Type and Exceptions|Polymorphism § 2.3]]. Reading and writing files, where exceptions are unavoidable, is in [[Java/07 - Input and Output/01 - File I-O|File I/O]].

## Contents

- [[#1. What Happens When an Exception Is Thrown|1. What Happens When an Exception Is Thrown]]
- [[#2. The `Throwable` Hierarchy|2. The `Throwable` Hierarchy]]
- [[#3. Checked vs. Unchecked Exceptions|3. Checked vs. Unchecked Exceptions]]
- [[#4. Throwing Exceptions with `throw` and `throws`|4. Throwing Exceptions with `throw` and `throws`]]
- [[#5. Catching Exceptions with `try` and `catch`|5. Catching Exceptions with `try` and `catch`]]
- [[#6. The `finally` Block|6. The `finally` Block]]
- [[#7. Try-with-Resources|7. Try-with-Resources]]
- [[#8. Custom Exceptions|8. Custom Exceptions]]
- [[#9. Chaining and Rethrowing|9. Chaining and Rethrowing]]
- [[#10. Reading a Stack Trace|10. Reading a Stack Trace]]
- [[#11. Exceptions, Inheritance, and Initialization|11. Exceptions, Inheritance, and Initialization]]
- [[#12. Good Practice|12. Good Practice]]
- [[#13. Common Pitfalls|13. Common Pitfalls]]
- [[#14. Quick Reference — Non-Obvious Outcomes|14. Quick Reference — Non-Obvious Outcomes]]
- [[#15. Practice — Trick Questions|15. Practice — Trick Questions]]
- [[#16. Summary|16. Summary]]

---

## 1. What Happens When an Exception Is Thrown

### 1.1 Propagation up the Call Stack

Every method call pushes a frame onto the call stack ([[Java/03 - Program Structure/01 - Methods#6.2 The Call Stack|Methods § 6.2]]). When an exception is thrown, the JVM **abandons** the current method at that point and checks each frame from the top down for a matching `catch`:

```java
public class Main {
    static void c(int x) {
        if (x < 0) throw new IllegalArgumentException("x must be >= 0, was " + x);
    }
    static void b(int x) { c(x); }
    static void a(int x) {
        try { b(x); } finally { System.out.println("finally in a"); }
    }
    public static void main(String[] args) {
        a(-1);
        System.out.println("never printed");
    }
}
```

```
finally in a
Exception in thread "main" java.lang.IllegalArgumentException: x must be >= 0, was -1
	at Main.c(Main.java:3)
	at Main.b(Main.java:5)
	at Main.a(Main.java:7)
	at Main.main(Main.java:10)
```

1. `c` throws. The rest of `c` is skipped, and `c` has no `catch`, so its frame is removed.
2. `b` has no `catch` either: its frame is removed too.
3. `a` has a `try` with a `finally` but no matching `catch`. The `finally` block runs, then the exception keeps going.
4. `main` doesn't catch it. The thread dies, and the JVM's default handler prints the exception and its <span class="hl-blue">stack trace</span> to `System.err`. The program exits with status `1`, and `"never printed"` is never printed.

This process is called <span class="hl-blue">propagation</span>, or *unwinding the stack*. A thrown exception travels **up the call chain**, never down, and every frame it passes through ends immediately.

![[Exceptions - Propagation and the Stack Trace.excalidraw|800]]

> [!important] Key idea
> Throwing an exception is a second way out of a method, next to `return`. A method either **returns normally** (with or without a value) or **completes abruptly** by throwing. The caller can tell the two apart: a normal return continues with the next statement, while a throw jumps to the nearest matching `catch`, anywhere up the stack.

### 1.2 Why Not Just Return an Error Code

Before exceptions, functions reported errors through special return values (`-1`, `null`, `false`). That has three problems, and exceptions solve all three:

| Error codes | Exceptions |
|---|---|
| Easy to ignore: nothing forces the caller to check `-1` | Unhandled exceptions stop the program, and checked ones must be handled to compile ([[#3. Checked vs. Unchecked Exceptions|§ 3]]) |
| The error value takes up a legal result (`indexOf` uses `-1` because an index can't be negative, but what can `parseInt` return for "abc"?) | The normal return type stays clean: `parseInt` returns any `int` |
| Every intermediate method must check and pass the code along | Intermediate methods do nothing: the exception propagates on its own |

Return values are still the right tool for **expected, frequent** outcomes: `Map.get` returns `null` for a missing key, `String.indexOf` returns `-1`. Exceptions are for situations the method can't handle itself ([[#12. Good Practice|§ 12]]).

---

## 2. The `Throwable` Hierarchy

### 2.1 The Three Branches

Only objects whose class extends `java.lang.Throwable` can be thrown or caught. Below `Throwable`, the hierarchy splits into three branches with different meanings:

```
Throwable
├── Error                          serious JVM problems: don't catch
│   ├── OutOfMemoryError
│   ├── StackOverflowError
│   ├── ExceptionInInitializerError
│   ├── NoClassDefFoundError
│   └── AssertionError
└── Exception                      conditions a program may want to handle
    ├── IOException                (checked)
    │   ├── FileNotFoundException
    │   └── EOFException
    ├── InterruptedException       (checked)
    ├── CloneNotSupportedException (checked)
    └── RuntimeException           (unchecked): usually programming errors
        ├── NullPointerException
        ├── ArithmeticException
        ├── ClassCastException
        ├── ArrayStoreException
        ├── NegativeArraySizeException
        ├── IndexOutOfBoundsException
        │   ├── ArrayIndexOutOfBoundsException
        │   └── StringIndexOutOfBoundsException
        ├── IllegalArgumentException
        │   └── NumberFormatException
        ├── IllegalStateException
        ├── UnsupportedOperationException
        ├── ConcurrentModificationException
        └── NoSuchElementException
            └── InputMismatchException
```

![[Exceptions - The Throwable Hierarchy.excalidraw|800]]

> [!note] Definitions
> - An **`Error`** signals a problem in the JVM or the environment that an ordinary program can't recover from: running out of memory, a stack overflow, a class that failed to load. Code normally doesn't catch these.
> - An **`Exception`** signals a condition a program might reasonably handle.
> - A **`RuntimeException`** is an `Exception` that usually signals a **bug** in the calling code: a `null` where an object was needed, a bad index, an illegal argument.
> - The words *error* and *exception* are also used loosely in conversation, but in Java `Error` and `Exception` are two specific, separate classes.

> [!warning] Trick: some names hide their parent class
> - `NumberFormatException` **is an** `IllegalArgumentException`. A `catch (IllegalArgumentException e)` also catches it.
> - `InputMismatchException` (from `Scanner.nextInt`) **is a** `NoSuchElementException`.
> - `FileNotFoundException` **is an** `IOException`.
> - `StackOverflowError` and `OutOfMemoryError` are **`Error`s**, not `Exception`s. `catch (Exception e)` does **not** catch them, and neither does `catch (RuntimeException e)`. Only `catch (Error e)` or `catch (Throwable e)` does.
> - `UncheckedIOException` sounds like an `IOException`, but it extends `RuntimeException`. It is a wrapper used to carry an `IOException` through code that can't throw checked exceptions ([[#9.4 Turning a Checked Exception into an Unchecked One|§ 9.4]]).

### 2.2 Common Exceptions and What Causes Them

| Exception | Typical cause | Message (JDK 17) |
|---|---|---|
| `NullPointerException` | calling a method or reading a field through `null`, unboxing `null`, `throw null` | `Cannot invoke "String.length()" because "<local1>" is null` |
| `ArrayIndexOutOfBoundsException` | `a[i]` with `i < 0` or `i >= a.length` | `Index 5 out of bounds for length 3` |
| `StringIndexOutOfBoundsException` | `charAt`, `substring` with a bad index | `String index out of range: 7` |
| `ArithmeticException` | **integer** division or remainder by zero | `/ by zero` |
| `ClassCastException` | a downcast to the wrong class | `class java.lang.String cannot be cast to class java.lang.Integer (…)` |
| `NumberFormatException` | `Integer.parseInt("12a")`, `parseInt(null)` | `For input string: "12a"` / `Cannot parse null string` |
| `IllegalArgumentException` | a method rejects an argument | whatever the method says |
| `IllegalStateException` | a method called at the wrong time (e.g. `Iterator.remove()` twice) | whatever the method says |
| `UnsupportedOperationException` | modifying an unmodifiable collection (`List.of(1).add(2)`) | often no message at all (`null`) |
| `ConcurrentModificationException` | changing a collection while iterating over it ([[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]]) | usually none |
| `NegativeArraySizeException` | `new int[-1]` | `-1` |
| `InputMismatchException` | `Scanner.nextInt()` on a non-number or an out-of-range number ([[Java/01 - Foundations/05 - Reading Input#5.3 Retrying with `try` and `catch`|Reading Input § 5.3]]) | none for `abc`; `For input string: "99999999999"` on overflow |
| `StackOverflowError` | unbounded recursion ([[Java/03 - Program Structure/01 - Methods#9.3 `StackOverflowError`|Methods § 9.3]]) | none |

> [!warning] Trick: `5 / 0` throws, `5.0 / 0` doesn't
> Only **integer** division by zero throws `ArithmeticException`. Floating-point division by zero gives `Infinity`, `-Infinity`, or `NaN`, and no exception is thrown ([[Java/01 - Foundations/03 - Operators#3. Division and Remainder — The Special Cases|Operators § 3]]).

> [!info]- Helpful `NullPointerException` messages (Java 14+)
> Since Java 14 (on by default from Java 15), an NPE's message says exactly which expression was `null`: `Cannot invoke "String.length()" because "s" is null`. Local variable **names** appear only if the class was compiled with debug information for locals (`javac -g`). Without it, which is javac's default, the message shows the variable's slot instead: `"<local1>"`. Fields always show by name: `because "this.name" is null`, or `"<local2>.name"` when the object itself is in a local variable. IDEs usually compile with `-g`, which is why the messages look nicer there.

---

## 3. Checked vs. Unchecked Exceptions

### 3.1 Which Is Which

> [!important] Key rule: checked vs. unchecked
> - **Unchecked** exceptions are `RuntimeException`, `Error`, and all of their subclasses.
> - **Checked** exceptions are **every other** `Throwable`: `Exception` itself, `IOException`, `InterruptedException`, your own `class MyException extends Exception`, and even a direct subclass of `Throwable`.
>
> "Checked" means **checked by the compiler**. Both kinds are thrown and caught the same way at runtime. The only difference is the compile-time rule in § 3.2.

| | Checked | Unchecked |
|---|---|---|
| Classes | `Exception` and subclasses, except `RuntimeException`'s branch | `RuntimeException`, `Error`, and their subclasses |
| Compiler enforces catch-or-declare? | **yes** | no |
| Usually means | an expected problem outside the program's control (missing file, network down) | a bug in the code (`null`, bad index), or a JVM failure |
| Caller can… | recover: retry, ask for another file name, use a default | fix the code |
| Examples | `IOException`, `FileNotFoundException`, `InterruptedException`, `SQLException` | `NullPointerException`, `IllegalArgumentException`, `ArithmeticException` |

### 3.2 The Catch-or-Declare Rule

<span class="hl-yellow">For every checked exception that a statement can throw, the method containing it must either **catch** it or **declare** it in its `throws` clause.</span> Otherwise the code doesn't compile. The rule is also called *handle or declare*.

```java
static String firstLine(BufferedReader in) {
    return in.readLine();      // compile error: unreported exception IOException;
}                              //   must be caught or declared to be thrown
```

Two ways to satisfy the compiler:

```java
// 1. Catch it: this method deals with the problem itself
static String firstLine(BufferedReader in) {
    try {
        return in.readLine();
    } catch (IOException e) {
        return "";                       // a deliberate fallback
    }
}

// 2. Declare it: pass the responsibility to the caller
static String firstLine(BufferedReader in) throws IOException {
    return in.readLine();
}
```

Declaring moves the problem one level up: now every **caller** of `firstLine` faces the same choice. At the top, `main` can also declare `throws IOException` (or `throws Exception`). Then an exception that reaches `main` ends the program with a stack trace, which is fine for small programs and exercises.

> [!warning] Trick: the rule is about the *declared* exceptions, not what really happens
> The compiler doesn't know what a method actually does at runtime. It only reads `throws` clauses:
> ```java
> void b() throws IOException { }   // never throws anything
> void c() { b(); }                 // compile error: unreported exception IOException
> ```
> And it reads them from the **declared type** of the receiver. Calling an overriding method that declares no exceptions through a supertype reference still needs a `try` ([[Java/04 - Object-Oriented Programming/04 - Polymorphism#2.3 The Declared Type Also Fixes the Return Type and Exceptions|Polymorphism § 2.3]]):
> ```java
> interface Task { void run() throws Exception; }
> class Hello implements Task { public void run() { System.out.println("hello"); } }
>
> new Hello().run();     // OK: Hello.run() declares nothing
> Task t = new Hello();
> t.run();               // compile error: unreported exception Exception
> ```

> [!warning] Trick: unchecked exceptions are never forced, even when declared
> ```java
> static int max(int a, int b) throws IllegalStateException { … }
> max(1, 2);    // compiles without try: IllegalStateException is unchecked
> ```
> Listing an unchecked exception in `throws` is legal and serves as documentation only (the example in [[Java/03 - Program Structure/01 - Methods#2. Declaring a Method|Methods § 2]] does this). The compiler ignores it.

### 3.3 Which Kind to Use

When a method has to report a problem:

- Use an **unchecked** exception when the caller **broke the rules**: passed a negative age, called `next()` with no elements left, used an object after closing it. The fix is to change the calling code, so forcing every caller to write a `try` would just add noise. Most exceptions you throw yourself are of this kind: `IllegalArgumentException`, `IllegalStateException`, `NullPointerException`.
- Use a **checked** exception when the problem can happen to **correct code** and a caller could reasonably recover: a file that was deleted, a network timeout, a business rule such as "insufficient funds" ([[#8. Custom Exceptions|§ 8]]).

> [!info]- The checked-exception debate
> Checked exceptions are a Java peculiarity: C#, Kotlin, Scala, and Python have only unchecked ones. The criticism is that they make signatures brittle (adding a checked exception to a method breaks every caller), that they don't work with lambdas ([[Java/06 - Functional Programming/01 - Lambdas and Functional Interfaces|Lambdas]]), and that they push programmers into writing empty `catch` blocks just to make the code compile. Modern Java APIs lean towards unchecked exceptions; `java.io` and `java.sql` still use checked ones. For exams and for working with the standard library, you need both.

---

## 4. Throwing Exceptions with `throw` and `throws`

### 4.1 The `throw` Statement

`throw` takes an **object** of a `Throwable` type and throws it. The object is normally created on the spot with `new`:

```java
void setAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("age must be >= 0, was " + age);
    }
    this.age = age;
}
```

This is the standard way to validate arguments in constructors and setters ([[Java/04 - Object-Oriented Programming/02 - Encapsulation#5.2 Validation in Setters (and Constructors)|Encapsulation § 5.2]]). Put the bad value in the message: "age must be >= 0, was -5" saves a debugging session, "invalid age" doesn't.

> [!warning] Traps with `throw`
> ```java
> throw "error";                           // compile error: String cannot be converted to Throwable
> throw new IllegalStateException();
> System.out.println("x");                 // compile error: unreachable statement
> throw null;                              // compiles! throws NullPointerException at runtime
> new MyException("oops");                 // compiles, but throws NOTHING: the object is just created and discarded
> ```
> Creating an exception object doesn't throw it. Without the `throw` keyword it's an ordinary object.

A method whose body ends in `throw` doesn't need a `return`, because the compiler knows the end of the method can't be reached ([[Java/03 - Program Structure/01 - Methods#4.2 Every Path Must Return — As the Compiler Sees It|Methods § 4.2]]):

```java
int notImplementedYet() {
    throw new UnsupportedOperationException("TODO");    // compiles: no return needed
}
```

### 4.2 The `throws` Clause

`throws` is part of a method's (or constructor's) **declaration**. It lists the checked exceptions the method may let escape, separated by commas:

```java
String load(Path p) throws IOException, InterruptedException { … }
```

| | `throw` | `throws` |
|---|---|---|
| What it is | a **statement** | part of a method or constructor **header** |
| Where | inside a method body | after the parameter list |
| Followed by | one exception **object** | one or more exception **classes** |
| Effect | throws the exception now | tells the compiler (and callers) what may be thrown |
| Example | `throw new IOException("x");` | `void f() throws IOException` |

The rules for `throws` when a method is **overridden** (the override may throw the same checked exceptions, fewer, or narrower ones, but never broader or new ones) are in [[Java/04 - Object-Oriented Programming/03 - Inheritance#3.3 The Rules for a Valid Override|Inheritance § 3.3]]. The same rule applies when a class implements an interface method ([[#11.1 Overriding and Interfaces|§ 11.1]]).

---

## 5. Catching Exceptions with `try` and `catch`

### 5.1 Syntax and Flow

```java
try {
    // code that may throw
} catch (ExceptionType1 e) {
    // runs if the try block threw an ExceptionType1 (or a subclass)
} catch (ExceptionType2 e) {
    // runs if it threw an ExceptionType2 (or a subclass)
}
// execution continues here after the try statement
```

1. The `try` block runs statement by statement.
2. If no exception is thrown, all `catch` blocks are skipped.
3. If an exception is thrown, the **rest of the `try` block is skipped**. The `catch` clauses are checked **top to bottom**, and the **first** one whose type matches (the same class or a superclass of the thrown exception) runs. Only one `catch` block ever runs.
4. After the `catch` block finishes, execution continues **after the whole `try` statement**. It does **not** go back into the `try` block.
5. If no `catch` matches, the exception propagates to the caller as if there were no `try`.

```java
static void test(String s) {
    try {
        System.out.println("try start");
        int n = Integer.parseInt(s);
        System.out.println("parsed " + n);
    } catch (NumberFormatException e) {
        System.out.println("catch");
    }
    System.out.println("after");
}
```

| Call | Output |
|---|---|
| `test("5")` | `try start`, `parsed 5`, `after` |
| `test("x")` | `try start`, `catch`, `after` |

Every part of the `try` statement is a block, so the braces are **required**, even around a single statement (unlike `if`).

### 5.2 Order of `catch` Blocks

Since the first matching `catch` wins, a `catch` for a superclass placed before a `catch` for its subclass would make the second one unreachable. The compiler rejects it:

```java
try {
    readFile();                              // throws IOException
} catch (IOException e) {
    …
} catch (FileNotFoundException e) {          // compile error: exception FileNotFoundException
    …                                        //   has already been caught
}
```

<span class="hl-yellow">Order `catch` blocks from the most specific to the most general.</span> Unrelated exception types (for example `IOException` and `NumberFormatException`) can be in any order.

### 5.3 Catching What Can't Be Thrown

For a **checked** exception class, the compiler also checks that the `try` block can actually throw it:

```java
try {
    int x = 1;
} catch (IOException e) { }        // compile error: exception IOException is never thrown
                                   //   in body of corresponding try statement
```

| `catch` clause, with a `try` block that throws no checked exceptions | Compiles? | Why |
|---|---|---|
| `catch (IOException e)` | ❌ | checked, and nothing in the `try` can throw it |
| `catch (FileNotFoundException e)` | ❌ | same |
| `catch (RuntimeException e)` / `catch (NullPointerException e)` | ✅ | unchecked exceptions can come from anywhere |
| `catch (Exception e)` | ✅ | `Exception` includes `RuntimeException` |
| `catch (Throwable e)` | ✅ | includes `Error` and `RuntimeException` |

A subclass of what the `try` can throw is fine: if `readFile()` declares `throws IOException`, catching `FileNotFoundException` compiles, because the `IOException` may well be a `FileNotFoundException` at runtime.

### 5.4 Multi-Catch

Since Java 7, one `catch` can handle several unrelated exception types, separated by `|`:

```java
try {
    String line = in.readLine();
    int n = Integer.parseInt(line);
} catch (IOException | NumberFormatException e) {
    System.out.println("bad input: " + e.getMessage());
}
```

> [!important] Rules for multi-catch
> - The alternatives may **not** be related by subclassing: `catch (FileNotFoundException | IOException e)` is a compile error (*Alternatives in a multi-catch statement cannot be related by subclassing*). Catching `IOException` alone already covers both.
> - The parameter `e` is **implicitly `final`**: `e = null;` is a compile error (*multi-catch parameter e may not be assigned*). A single-type `catch` parameter can be reassigned, though doing so is bad style.
> - The static type of `e` is the **closest common supertype** of the alternatives: here `Exception`. Only methods of that type can be called on `e` without a cast.

### 5.5 The Exception Object

The `catch` parameter is an ordinary object with useful methods, all inherited from `Throwable`:

| Method | Returns | Example result |
|---|---|---|
| `getMessage()` | the detail message, **possibly `null`** | `"For input string: \"12a\""` |
| `toString()` | class name, then `": " + message` if there is one | `java.lang.NumberFormatException: For input string: "12a"` |
| `printStackTrace()` | prints `toString()` and the stack trace to **`System.err`** | see [[#10. Reading a Stack Trace|§ 10]] |
| `getCause()` | the wrapped exception, or `null` | [[#9.1 Wrapping an Exception — the Cause|§ 9.1]] |
| `getSuppressed()` | exceptions suppressed by try-with-resources | [[#7.4 Suppressed Exceptions|§ 7.4]] |
| `getStackTrace()` | the frames as a `StackTraceElement[]` | |

> [!warning] Trick: `getMessage()` can be `null`
> ```java
> new RuntimeException().getMessage()      // null
> List.of(1).add(2)                        // UnsupportedOperationException with message null
> System.out.println(new RuntimeException());                          // java.lang.RuntimeException
> new RuntimeException(new IOException("disk")).getMessage()           // "java.io.IOException: disk"
> ```
> Printing `"Error: " + e.getMessage()` can therefore print `Error: null`. Printing `e` itself (its `toString()`) always shows at least the class name. The last line shows that an exception created from just a cause takes the cause's `toString()` as its message.

> [!warning] Trick: `printStackTrace()` and `System.out` can appear out of order
> `printStackTrace()` writes to `System.err`, a separate stream from `System.out`. In a console or IDE, the two streams can interleave in a different order from the one the code ran in. Use `e.printStackTrace(System.out)` if the order matters, for example when comparing output.

### 5.6 Scope of Variables in `try`

A variable declared inside the `try` block is local to that block. It isn't visible in `catch`, in `finally`, or after the `try`:

```java
try {
    int m = Integer.parseInt(s);
} catch (NumberFormatException e) { }
System.out.println(m);                   // compile error: cannot find symbol m
```

Declaring it before the `try` solves the scope problem but creates another one:

```java
int n;
try {
    n = Integer.parseInt(s);
} catch (NumberFormatException e) {
    System.out.println("bad");
}
System.out.println(n);                   // compile error: variable n might not have been initialized
```

If `parseInt` throws, the assignment never happens, and the `catch` doesn't assign `n` either. Initialize it at the declaration (`int n = 0;`), assign it in the `catch` too, or `return`/`throw` from the `catch`.

The `catch` parameter is also a local variable. It can't reuse the name of a local that is still in scope: `String e = "x"; try { … } catch (RuntimeException e) { }` is a compile error (*variable e is already defined*).

---

## 6. The `finally` Block

### 6.1 When `finally` Runs

A `finally` block runs **after** the `try` (and the `catch`, if one ran), **however** the `try` statement ends:

| How the `try`/`catch` ends | Does `finally` run? | What happens afterwards |
|---|---|---|
| normally | ✅ | continue after the `try` statement |
| exception thrown and caught | ✅, after the `catch` block | continue after the `try` statement |
| exception thrown and **not** caught | ✅ | the exception continues propagating |
| exception thrown **inside a `catch`** | ✅ | the new exception propagates |
| `return`, `break`, or `continue` inside `try` or `catch` | ✅, **before** the method returns or the loop jumps | the `return`/`break`/`continue` completes |
| `System.exit(…)` inside `try` or `catch` | ❌ | the JVM stops at once |

`finally` exists for **cleanup** that must happen no matter what: closing a file, releasing a lock, restoring a setting. For resources, try-with-resources ([[#7. Try-with-Resources|§ 7]]) is better.

A `try` must have at least one `catch` or a `finally` (or resources, [[#7. Try-with-Resources|§ 7]]). `try { … } finally { … }` with no `catch` is allowed, and common: clean up, but let the exception propagate. A bare `try { … }` is a compile error (*'try' without 'catch', 'finally' or resource declarations*).

![[Exceptions - try catch finally Paths.excalidraw|800]]

> [!warning] Trick: when `finally` does NOT run
> ```java
> try {
>     System.out.println("try");
>     System.exit(0);
> } finally {
>     System.out.println("finally");      // never printed
> }
> ```
> `finally` also doesn't run if the JVM crashes or is killed, or if the `try` block never ends (an infinite loop, or a thread that blocks forever).

### 6.2 `finally` and `return` — the Returned Value

When the `try` block executes `return expr;`, the value of `expr` is computed and **saved** first, then `finally` runs, then the method returns the saved value:

```java
static int a() {
    int x = 1;
    try {
        return x;           // the value 1 is saved here
    } finally {
        x = 2;              // changes the variable, not the saved value
    }
}                           // returns 1

static StringBuilder b() {
    StringBuilder sb = new StringBuilder("a");
    try {
        return sb;          // the REFERENCE is saved
    } finally {
        sb.append("b");     // mutates the object the saved reference points to
    }
}                           // returns a StringBuilder containing "ab"
```

This is the same distinction as in parameter passing ([[Java/03 - Program Structure/01 - Methods#5.2 References: Mutating vs. Reassigning|Methods § 5.2]]): reassigning the variable in `finally` has no effect on the result, but mutating the object it refers to does.

### 6.3 A `return` in `finally` Wins — and Swallows Exceptions

<span class="hl-red">Never `return` from a `finally` block.</span> A `return` in `finally` replaces whatever the `try` or `catch` was doing, including **throwing an exception**:

```java
static int c() {
    try { return 1; }
    finally { return 2; }                         // returns 2
}

static int d() {
    try { throw new RuntimeException("lost"); }
    finally { return 3; }                         // returns 3: the exception disappears
}

static int e() {
    try { throw new Error("lost too"); }
    finally { return 4; }                         // returns 4: even an Error disappears
}
```

All three compile without any warning by default. `javac -Xlint:finally` warns *finally clause cannot complete normally*. A `break` or `continue` in `finally` has the same effect: it abandons the pending exception or return.

```java
for (int i = 0; i < 3; i++) {
    try { throw new RuntimeException("swallowed " + i); }
    finally { System.out.println("finally " + i); break; }
}
System.out.println("after loop, no exception");     // printed: the exception was discarded
```

### 6.4 An Exception in `finally` Masks the Original

If `finally` itself throws, its exception **replaces** the one that was propagating. The original is lost, with no trace:

```java
static String g() {
    try {
        throw new IllegalStateException("original");
    } finally {
        throw new IllegalArgumentException("from finally");
    }
}
// g() throws IllegalArgumentException("from finally"); "original" is gone
// (getSuppressed() is empty)
```

This happens in practice when cleanup code fails: a `close()` in `finally` throws while an exception from the `try` body is already propagating, and the real cause of the problem disappears. Try-with-resources solves exactly this ([[#7.4 Suppressed Exceptions|§ 7.4]]).

### 6.5 Nested `try` Statements

An exception thrown in a `catch` block is **not** caught by the other `catch` blocks of the same `try`. Those only guard the `try` block. It propagates outwards, after the `finally` of the same statement runs:

```java
try {
    try {
        throw new IllegalArgumentException("first");
    } catch (IllegalArgumentException e) {
        throw new IllegalStateException("from catch");
    } catch (IllegalStateException e) {
        System.out.println("sibling catch");            // NOT printed
    } finally {
        System.out.println("inner finally");            // 1st
    }
} catch (IllegalStateException e) {
    System.out.println("outer catch: " + e.getMessage());   // 2nd: outer catch: from catch
}
```

---

## 7. Try-with-Resources

### 7.1 The Problem It Solves

Files, network connections, and database connections must be **closed** when no longer needed, whether the code using them succeeds or fails. The garbage collector doesn't do it ([[Java/04 - Object-Oriented Programming/01 - Classes and Objects#3.4 Object Lifetime and Garbage Collection|Classes and Objects § 3.4]]). Doing it correctly with `finally` is verbose and still flawed:

```java
BufferedReader in = null;
try {
    in = new BufferedReader(new FileReader("data.txt"));
    return in.readLine();
} finally {
    if (in != null) {            // the constructor may have failed
        in.close();              // may throw, masking an exception from readLine (§ 6.4)
    }
}
```

### 7.2 Syntax

Since Java 7, resources can be declared in parentheses after `try`. They are **closed automatically** at the end of the block, however it ends:

```java
try (BufferedReader in = new BufferedReader(new FileReader("data.txt"))) {
    return in.readLine();
}                                // in.close() is called here, always
```

> [!important] Rules for try-with-resources
> - A resource's type must implement **`java.lang.AutoCloseable`** (one method: `void close() throws Exception`). `java.io.Closeable` extends it, with `close() throws IOException`. Files, readers, writers, streams, `Scanner`, and database connections all implement it. Otherwise: *try-with-resources not applicable to variable type*.
> - Several resources are separated by `;`. They are closed in **reverse order** of declaration: the last one opened is closed first.
> - Resource variables are implicitly **`final`**: `r = new R();` inside the block is a compile error (*auto-closeable resource r may not be assigned*).
> - Since Java 9, an existing variable can be used as a resource if it is final or effectively final: `try (in) { … }`.
> - A `null` resource is allowed: `close()` is simply not called on it.
> - A try-with-resources statement may have **no** `catch` and **no** `finally`. If it does have them, they run **after** the resources have been closed.

```java
static class Res implements AutoCloseable {
    final String name;
    Res(String name) { this.name = name; System.out.println("open " + name); }
    @Override public void close() { System.out.println("close " + name); }
}

try (Res a = new Res("A"); Res b = new Res("B")) {
    System.out.println("body");
    throw new RuntimeException("body failed");
} catch (RuntimeException e) {
    System.out.println("catch: " + e.getMessage());
} finally {
    System.out.println("finally");
}
```

```
open A
open B
body
close B
close A
catch: body failed
finally
```

<span class="hl-yellow">The resources are already closed when `catch` and `finally` run.</span> A `catch` block can't use the resource to recover, for example to read the rest of a file.

> [!warning] Trick: `AutoCloseable.close()` declares `throws Exception`
> ```java
> try (AutoCloseable r = () -> System.out.println("closed")) {
>     System.out.println("body");
> }   // compile error: unreported exception Exception; must be caught or declared to be thrown
>     //   (exception thrown from implicit call to close() on resource variable 'r')
> ```
> The hidden `close()` call is checked like any other call. A resource declared as `AutoCloseable` forces the code to handle `Exception`, and one declared as `Closeable` (or `BufferedReader`, `FileReader`, …) forces `IOException`. A class implementing `AutoCloseable` should **narrow** `close()`'s `throws` clause to what it really throws, or drop it entirely, as `Res` above does. `Scanner.close()` declares nothing, so a `Scanner` resource needs no `catch`.

### 7.3 If Opening a Resource Fails

Resources are opened left to right. If one fails to open, the ones **already opened are closed**, and the body never runs:

```java
try (Res a = new Res("A"); Res b = make()) {   // make() throws "cannot open B"
    System.out.println("body");                // not printed
} catch (RuntimeException e) {
    System.out.println("catch: " + e.getMessage());
}
// open A / close A / catch: cannot open B
```

<span class="hl-purple">A subtle leak:</span> in `try (BufferedReader in = new BufferedReader(new FileReader(f)))`, only `in` is a resource. If the `BufferedReader` constructor failed after the `FileReader` had opened the file, the file would stay open. `BufferedReader`'s constructor practically never fails, so this form is the usual idiom. Declaring each layer as its own resource is the fully safe version: `try (FileReader fr = new FileReader(f); BufferedReader in = new BufferedReader(fr))`.

### 7.4 Suppressed Exceptions

If the body throws an exception **and** `close()` throws too, try-with-resources keeps the **body's** exception, which is usually the real cause. It attaches the `close()` exception to it as a <span class="hl-blue">suppressed exception</span>, so nothing is lost:

```java
try (Res a = new Res("A", /* failClose */ true)) {
    throw new RuntimeException("body failed");
} catch (RuntimeException e) {
    System.out.println("catch: " + e.getMessage());           // catch: body failed
    for (Throwable s : e.getSuppressed()) {
        System.out.println("  suppressed: " + s.getMessage()); //   suppressed: close A failed
    }
}
```

If only `close()` throws (the body succeeded), the `close()` exception is the one that propagates, with nothing suppressed. In a stack trace, suppressed exceptions are listed under the main one, indented, with a `Suppressed:` prefix ([[#10. Reading a Stack Trace|§ 10]]).

| Situation | `finally { r.close(); }` (old style) | try-with-resources |
|---|---|---|
| body OK, `close` OK | no exception | no exception |
| body throws, `close` OK | body's exception | body's exception |
| body OK, `close` throws | `close`'s exception | `close`'s exception |
| body throws, `close` throws | `close`'s exception; **body's is lost** | body's exception, with `close`'s in `getSuppressed()` |
| the resource variable is `null` | `NullPointerException` unless checked | `close` is skipped |

![[Exceptions - finally vs Try-with-Resources.excalidraw|800]]

> [!warning] Common mistake: closing `System.in`
> `try (Scanner sc = new Scanner(System.in)) { … }` closes `System.in` when the block ends, and every later read from the keyboard fails, even with a new `Scanner`. Never put a keyboard `Scanner` in try-with-resources unless the block is the whole program ([[Java/01 - Foundations/05 - Reading Input#10.1 Don't Close a `Scanner` on `System.in`|Reading Input § 10.1]]). For files, try-with-resources is exactly right ([[Java/07 - Input and Output/01 - File I-O|File I/O]]).

---

## 8. Custom Exceptions

### 8.1 Declaring One

A custom exception is a class that extends `Exception` (checked) or `RuntimeException` (unchecked). By convention its name ends in `Exception`. It normally offers the standard constructors and passes them to `super`, and it may carry extra fields that describe the problem:

```java
public class InsufficientFundsException extends Exception {     // checked
    private final long missing;

    public InsufficientFundsException(long missing) {
        super("insufficient funds: missing " + missing + " cents");
        this.missing = missing;
    }

    public long getMissing() { return missing; }
}

public class Account {
    private long balance;

    public void withdraw(long amount) throws InsufficientFundsException {
        if (amount <= 0) {
            throw new IllegalArgumentException("amount must be positive: " + amount);  // a bug in the caller
        }
        if (amount > balance) {
            throw new InsufficientFundsException(amount - balance);                    // a business case
        }
        balance -= amount;
    }
}

try {
    acc.withdraw(900);
} catch (InsufficientFundsException e) {
    System.out.println(e.getMessage() + " (" + e.getMissing() + ")");
}
```

The method uses both kinds on purpose. A negative amount is a programming error (unchecked), while too little money is an expected situation that correct code must handle (checked, so the compiler makes sure every caller does).

> [!tip] The usual set of constructors
> ```java
> public class DataException extends Exception {
>     public DataException() { }
>     public DataException(String message) { super(message); }
>     public DataException(String message, Throwable cause) { super(message, cause); }
>     public DataException(Throwable cause) { super(cause); }
> }
> ```
> The constructors with a `cause` are what make chaining possible ([[#9.1 Wrapping an Exception — the Cause|§ 9.1]]). Constructors are not inherited ([[Java/04 - Object-Oriented Programming/03 - Inheritance#5.1 Constructors Are Not Inherited|Inheritance § 5.1]]), so each one has to be written out.

> [!info]- The `serialVersionUID` warning
> `Throwable` implements `Serializable`, so with `javac -Xlint` (or in an IDE) a custom exception without a `private static final long serialVersionUID = 1L;` field gets a *serializable class has no definition of serialVersionUID* warning. It only matters if exception objects are serialized (sent over a network or saved to disk). Adding the field silences it.

### 8.2 Prefer the Standard Exceptions

Before writing a new class, check whether a standard exception already says what you mean. Callers recognise them, and they need no extra code:

| Situation | Exception |
|---|---|
| an argument is invalid | `IllegalArgumentException` |
| an argument is `null` where it mustn't be | `NullPointerException`, via `Objects.requireNonNull(x, "x must not be null")` |
| an index is out of range | `IndexOutOfBoundsException`, via `Objects.checkIndex(i, size)` |
| the object is in the wrong state for this call | `IllegalStateException` |
| the operation isn't supported (e.g. a read-only view) | `UnsupportedOperationException` |
| a requested element doesn't exist | `NoSuchElementException` |
| a low-level I/O failure | `IOException` or one of its subclasses |

Write a custom exception when callers need to catch **this specific problem** separately from others, or when the exception should carry extra data (like `getMissing()` above).

### 8.3 What Custom Exceptions Can't Do

- They can't be **generic**: `class Bad<T> extends Exception` is a compile error (*a generic class may not extend java.lang.Throwable*), because `catch` needs a runtime type and type arguments are erased ([[Java/05 - Working with Data and Errors/02 - Generics#7.2 What Erasure Forbids|Generics § 7.2]]).
- A type parameter can't be caught: `catch (T e)` is a compile error. But a generic method may declare `throws T`: `static <T extends Exception> void f() throws T` compiles, and the caller's `T` decides which checked exception it must handle.
- Extending `Throwable` directly, or `Error`, is legal but wrong: `Error` is reserved for the JVM, and a direct `Throwable` subclass is checked yet isn't caught by `catch (Exception e)`.

---

## 9. Chaining and Rethrowing

### 9.1 Wrapping an Exception — the Cause

A method at a higher level of abstraction often catches a low-level exception and throws its **own** exception instead, passing the original as the <span class="hl-blue">cause</span>. The caller sees a meaningful exception, and the low-level details stay available:

```java
static void load() throws ConfigException {
    try {
        read();                                                   // throws FileNotFoundException
    } catch (IOException e) {
        throw new ConfigException("cannot load configuration", e);   // e is the cause
    }
}
```

`e.getCause()` returns the original, and the stack trace shows both, joined by `Caused by:` ([[#10. Reading a Stack Trace|§ 10]]).

> [!warning] Common mistake: losing the cause
> ```java
> catch (IOException e) {
>     throw new ConfigException("cannot load configuration");              // ❌ cause lost
>     throw new ConfigException("cannot load: " + e.getMessage());          // ❌ message kept, stack trace lost
>     throw new ConfigException("cannot load configuration", e);           // ✅
> }
> ```
> Without the cause, the stack trace ends at the `throw` in `catch`, and the line where the real failure happened is gone.

### 9.2 Rethrowing

A `catch` block can do something (log, clean up, count) and then rethrow the **same** exception object with `throw e;`. The stack trace is kept: it records where the exception was **created**, not where it was last thrown.

```java
try {
    process(file);
} catch (IOException e) {
    System.err.println("failed on " + file);
    throw e;                                 // same object, same stack trace
}
```

### 9.3 Precise Rethrow

Since Java 7, the compiler tracks which exceptions a rethrown `catch` parameter can really hold. If `e` is effectively final, `throw e` rethrows only the checked exceptions the `try` block can throw, not everything the `catch` type allows:

```java
void a() throws IOException {                  // IOException is enough, not Exception
    try {
        io();                                  // throws IOException
    } catch (Exception e) {
        System.out.println("log");
        throw e;                               // compiler knows: IOException or unchecked
    }
}

void b() {                                     // no throws clause at all!
    try {
        int x = 1;                             // can throw no checked exception
    } catch (Exception e) {
        throw e;                               // so e can only be unchecked here
    }
}

void c() throws IOException {
    try {
        io();
    } catch (Exception e) {
        e = new Exception();                   // e is reassigned: precise analysis is switched off
        throw e;                               // compile error: unreported exception Exception
    }
}
```

### 9.4 Turning a Checked Exception into an Unchecked One

Sometimes a checked exception has to pass through code that can't declare it, for example a method implementing an interface without a `throws` clause, or (later) a lambda. The standard approach is to wrap it in an unchecked exception, keeping the cause:

```java
catch (IOException e) {
    throw new UncheckedIOException(e);       // java.io.UncheckedIOException extends RuntimeException
}
catch (SomeCheckedException e) {
    throw new RuntimeException(e);           // generic version
}
```

---

## 10. Reading a Stack Trace

A stack trace lists the call stack **at the moment the exception was created**, from the innermost call to the outermost:

```
Main$ConfigException: cannot load configuration          ← 1. exception class and message
	at Main.load(Main.java:8)                             ← 2. where it was thrown (top frame)
	at Main.main(Main.java:11)                            ← 3. who called that, and so on down
Caused by: java.io.FileNotFoundException: app.cfg (No such file or directory)   ← 4. the cause
	at Main.read(Main.java:6)                             ← 5. where the cause was thrown
	... 2 more                                            ← 6. frames identical to the trace above
```

1. The **first line** is the exception's `toString()`: class name and message. `Main$ConfigException` means a class `ConfigException` nested inside `Main`.
2. Each `at` line is one stack frame: `Class.method(File.java:line)`. The **top** frame is the line that threw.
3. Frames below it are the callers, ending with `main` (or `Thread.run`).
4. `Caused by:` starts the trace of the wrapped exception ([[#9.1 Wrapping an Exception — the Cause|§ 9.1]]). There can be several levels of causes.
5. **The deepest `Caused by:` is usually the real problem.** Read it first.
6. `... 2 more` means the remaining frames of the cause are the same as the last 2 frames of the enclosing trace, so they're not repeated.

Suppressed exceptions ([[#7.4 Suppressed Exceptions|§ 7.4]]) appear indented under the main exception:

```
java.lang.Exception: main
	at Main.main(Main.java:3)
	Suppressed: java.lang.RuntimeException: secondary
		at Main.main(Main.java:4)
```

> [!tip] How to debug from a stack trace
> 1. Read the message. Often it says everything: `Index 5 out of bounds for length 3`.
> 2. Find the deepest `Caused by:`.
> 3. In that trace, find the **first frame in your own code**. Frames in `java.util`, `java.base`, or a library show where the problem was detected, not where it was caused. The bug is almost always in the first frame that is yours.

The drawing in [[#1.1 Propagation up the Call Stack|§ 1.1]] shows how each `at` line corresponds to one frame of the call stack.

When an uncaught exception ends `main`, any `finally` blocks on the way out run **before** the JVM prints the stack trace:

```java
try { throw new RuntimeException("boom"); }
finally { System.out.println("finally runs first"); }
```

```
finally runs first
Exception in thread "main" java.lang.RuntimeException: boom
	at Main.main(Main.java:3)
```

---

## 11. Exceptions, Inheritance, and Initialization

### 11.1 Overriding and Interfaces

An overriding method may throw the **same, fewer, or narrower** checked exceptions than the method it overrides, and any unchecked exceptions ([[Java/04 - Object-Oriented Programming/03 - Inheritance#3.3 The Rules for a Valid Override|Inheritance § 3.3]]). The same applies to a class implementing an interface method:

```java
interface Task { void run() throws Exception; }

class Hello implements Task {
    public void run() { System.out.println("hello"); }   // OK: throws nothing
}
```

Which `throws` clause the compiler uses for a call depends on the **declared** type of the reference ([[#3.2 The Catch-or-Declare Rule|§ 3.2]]).

A `catch` for a superclass catches every subclass, so one `catch (IOException e)` handles a `FileNotFoundException` too. `catch (RuntimeException e)` catches every unchecked exception except `Error`s.

### 11.2 Constructors

A constructor can declare `throws` like a method. If it throws, the object is never handed to the caller: the `new` expression completes abruptly and the variable is not assigned.

<span class="hl-yellow">Trick case:</span> a subclass constructor **can't catch** an exception from its superclass constructor, because `super(…)` must be the first statement ([[Java/04 - Object-Oriented Programming/03 - Inheritance#5.4 Rules for `super(…)`|Inheritance § 5.4]]) and can't be inside a `try`. It must declare the exception:

```java
class Base { Base() throws IOException { … } }

class Ok extends Base {
    Ok() throws IOException { super(); }                  // OK
}
class Bad extends Base {
    Bad() { }                                             // compile error: unreported exception IOException
}                                                         //   (from the implicit super())
class Bad2 extends Base {
    Bad2() { try { super(); } catch (IOException e) { } } // compile error: call to super must be first statement
}
class Bad3 extends Base { }                               // compile error: unreported exception IOException
                                                          //   in default constructor
```

### 11.3 Field Initializers and Static Initializers

An instance field initializer (or instance initializer block) runs as part of **every constructor**, so it may throw a checked exception only if **every** constructor declares it:

```java
class A { int x = load(); A() throws IOException { } }    // OK: load() throws IOException
class B { int x = load(); B() { } }                       // compile error: unreported exception IOException
```

A **static** initializer can't throw checked exceptions at all: no caller could catch them, since class initialization happens implicitly ([[Java/04 - Object-Oriented Programming/01 - Classes and Objects#9.1 Class Initialization (Static)|Classes and Objects § 9.1]]). `static int y = load();` is a compile error, and `static { throw new RuntimeException(); }` is too (*initializer must be able to complete normally*).

If a static initializer throws an **unchecked** exception at runtime, the JVM wraps it in an `ExceptionInInitializerError`, and the class is marked as failed. Every later use of the class throws `NoClassDefFoundError`:

```java
class Cfg {
    static final int VALUE = Integer.parseInt("not a number");
}

Cfg.VALUE;   // 1st use: ExceptionInInitializerError, cause NumberFormatException: For input string: "not a number"
Cfg.VALUE;   // 2nd use: NoClassDefFoundError: Could not initialize class Cfg
```

The second error is confusing, because the class file exists. The real cause is the **first** error, which may be far back in the log.

---

## 12. Good Practice

> [!important] Key rules
> 1. **Never swallow an exception.** An empty `catch` hides the bug and the program continues in a broken state. At the very least, log it. If you really mean to ignore it, write a comment saying why.
> 2. **Catch only what you can handle, where you can handle it.** If a method can't do anything useful about an exception, it should let it propagate (declare it), not catch and ignore it. *Throw early, catch late*: check arguments as soon as possible, and handle failures at the level that knows what to do (often near the user interface).
> 3. **Don't catch `Exception` or `Throwable` blindly.** `catch (Exception e)` also catches every `NullPointerException` and `IndexOutOfBoundsException`, so real bugs get treated as "expected" failures. `catch (Throwable t)` also catches `OutOfMemoryError` and `StackOverflowError`. Catch the specific types. A catch-all belongs only at the very top of a program (to log and exit cleanly).
> 4. **Don't use exceptions for ordinary control flow.** They are slow (creating one records the whole stack) and they hide the intent.
> 5. **Keep the cause** when wrapping ([[#9.1 Wrapping an Exception — the Cause|§ 9.1]]).
> 6. **Use try-with-resources** for anything that must be closed.
> 7. **Write useful messages**, with the bad value and the context: `"age must be >= 0, was -5"`, not `"error"`.
> 8. **Document** what a method throws, including unchecked exceptions, with Javadoc `@throws`.

> [!example]- Worked example: exceptions as control flow
> ```java
> int[] a = {1, 2, 3};
> int sum = 0;
> try {
>     int i = 0;
>     while (true) sum += a[i++];               // ends by running off the array
> } catch (ArrayIndexOutOfBoundsException e) { }
> System.out.println(sum);                       // 6
> ```
> It works, but it is slower than a normal loop, harder to read, and it also hides any *real* index bug inside the loop. Use `for (int x : a) sum += x;`.

> [!warning] Trick: `assert` is off by default
> ```java
> int x = -5;
> assert x > 0 : "x must be positive";
> System.out.println("assert did nothing: " + x);      // printed
> ```
> Assertions only run when the JVM is started with `-ea` (*enable assertions*). Then a failed `assert` throws an `AssertionError`. Never use `assert` to validate arguments or input, because in production it usually does nothing. Use it for internal checks during development; use `if` + `throw` for real validation.

---

## 13. Common Pitfalls

- **Empty `catch` blocks** that silently swallow exceptions.
- **Catching `Exception` or `Throwable`** where a specific type was meant, hiding bugs.
- **`catch` blocks in the wrong order**: a superclass before a subclass is a compile error.
- **Catching a checked exception the `try` can't throw**: a compile error.
- **Expecting `catch (Exception e)` to catch `StackOverflowError` or `OutOfMemoryError`.** They are `Error`s.
- **Forgetting that a `throws` clause on a callee forces the caller** to catch or declare, even if the callee never actually throws.
- **Creating an exception without `throw`**: `new IllegalArgumentException("x");` does nothing.
- **Using a variable declared inside `try` after the `try`**, or a variable that is only assigned inside the `try` (*might not have been initialized*).
- **Expecting execution to resume inside `try`** after a `catch`. It continues after the whole statement.
- **`return`, `break`, or `continue` in `finally`**: overrides the `try`'s result and silently discards exceptions.
- **An exception thrown from `finally`** (often from `close()`) masking the original exception.
- **Expecting `finally` to run after `System.exit`.**
- **Expecting a `finally` block to change a returned primitive** by reassigning the variable.
- **Closing resources by hand** instead of with try-with-resources, or forgetting to close them at all.
- **Using the resource in `catch`/`finally`** of a try-with-resources. It is already closed.
- **Putting a `System.in` `Scanner` in try-with-resources.**
- **Losing the cause** when wrapping an exception.
- **Printing `e.getMessage()`**, which may be `null`, instead of `e`.
- **Using `assert` for validation.** It is disabled unless the JVM runs with `-ea`.
- **Using exceptions for normal control flow.**
- **Reading only the first line of a stack trace** instead of the deepest `Caused by:` and the first frame in your own code.

---

## 14. Quick Reference — Non-Obvious Outcomes

| Code | Result | Why |
|---|---|---|
| `throw new Exception();` in a method without `throws` | compile error | checked: catch or declare |
| `void c() { b(); }` with `void b() throws IOException { }` | compile error | the declared `throws` counts, not what `b` really does |
| `max(1, 2)` with `max(…) throws IllegalStateException` | compiles | unchecked exceptions are never forced |
| `try { } catch (IOException e) { }` | compile error | never thrown in the `try` body |
| `try { } catch (Exception e) { }` | compiles | `Exception` includes unchecked exceptions |
| `catch (IOException e)` before `catch (FileNotFoundException e)` | compile error | *has already been caught* |
| `catch (FileNotFoundException \| IOException e)` | compile error | alternatives related by subclassing |
| `catch (A \| B e) { e = null; }` | compile error | a multi-catch parameter is implicitly `final` |
| `try { … }` alone | compile error | needs `catch`, `finally`, or resources |
| `catch (Exception e)` around infinite recursion | doesn't catch it | `StackOverflowError` is an `Error` |
| `throw null;` | `NullPointerException` | `throw` needs an object |
| `throw "error";` | compile error | `String` is not a `Throwable` |
| `new IllegalStateException("x");` (no `throw`) | nothing happens | creating ≠ throwing |
| `int f() { throw new X(); }` | compiles | no `return` needed after `throw` |
| statement after `throw` | compile error | unreachable statement |
| `5 / 0` vs. `5.0 / 0` | `ArithmeticException` vs. `Infinity` | only integer division throws |
| `new RuntimeException().getMessage()` | `null` | no message given |
| `new RuntimeException(new IOException("disk")).getMessage()` | `"java.io.IOException: disk"` | message taken from the cause |
| `int x = 1; try { return x; } finally { x = 2; }` | returns `1` | the value was saved before `finally` |
| `try { return sb; } finally { sb.append("b"); }` | returned builder contains the append | the object is shared |
| `try { return 1; } finally { return 2; }` | returns `2` | `finally`'s `return` wins |
| `try { throw new RuntimeException(); } finally { return 3; }` | returns `3`, no exception | `finally`'s `return` swallows it |
| `try { throw A; } finally { throw B; }` | `B` propagates, `A` is lost | `finally` masks it |
| `System.exit(0)` in `try` | `finally` doesn't run | the JVM stops |
| exception thrown in a `catch` block | not caught by sibling `catch`es | they only guard the `try` block |
| `try (AutoCloseable r = …) { }` | compile error unless `Exception` is handled | the implicit `close()` throws `Exception` |
| `try (R r = …) { r = other; }` | compile error | resources are implicitly `final` |
| `try (String s = "x") { }` | compile error | not `AutoCloseable` |
| `try (R r = null) { }` | runs, no exception | `close()` is skipped for `null` |
| body and `close()` both throw (try-with-resources) | body's exception, `close`'s suppressed | nothing is lost |
| body and `close()` both throw (`close` in `finally`) | `close`'s exception, body's lost | masking |
| try-with-resources with `catch` | resources closed **before** `catch` runs | |
| `catch (Exception e) { throw e; }` around code with no checked exceptions | compiles, no `throws` needed | precise rethrow |
| …and `e` reassigned before `throw e` | compile error | precise rethrow switched off |
| `class E<T> extends Exception` | compile error | generic `Throwable` |
| `Bad() { }` when `Base()` declares `throws IOException` | compile error | the implicit `super()` throws it |
| `static int y = load();` with `load() throws IOException` | compile error | static initializers can't throw checked exceptions |
| exception in a static initializer, then the class is used again | `ExceptionInInitializerError`, then `NoClassDefFoundError` | the class is marked as failed |
| `assert x > 0;` with `x = -5` | nothing | assertions are off without `-ea` |
| uncaught exception in `main` | `finally` blocks run, then the stack trace, exit status 1 | |

---

## 15. Practice — Trick Questions

**Q1.** Which of these compile? `io()` is declared `void io() throws IOException`.

```java
void a() { try { int x = 1; } catch (IOException e) { } }                                 // (1)
void b() { try { int x = 1; } catch (Exception e) { } }                                   // (2)
void c() { try { int x = 1; } catch (NullPointerException e) { } }                        // (3)
void d() { try { io(); } catch (FileNotFoundException e) { } }                            // (4)
void e() { try { io(); } catch (FileNotFoundException e) { } catch (IOException e) { } }  // (5)
void f() { try { io(); } catch (IOException e) { } catch (FileNotFoundException e) { } }  // (6)
void g() { try { io(); } catch (FileNotFoundException | IOException e) { } }              // (7)
void h() throws Exception { io(); }                                                       // (8)
```

> [!success]- Answer
> | Method | Compiles? | Reason |
> |---|---|---|
> | (1) | ❌ | `IOException` is checked and can't be thrown by the `try` body |
> | (2) | ✅ | `Exception` includes unchecked exceptions, so it's always allowed |
> | (3) | ✅ | unchecked: always allowed |
> | (4) | ❌ | the `catch` is fine, but an `IOException` that isn't a `FileNotFoundException` is neither caught nor declared: *unreported exception IOException* |
> | (5) | ✅ | specific before general |
> | (6) | ❌ | `FileNotFoundException` has already been caught |
> | (7) | ❌ | alternatives related by subclassing |
> | (8) | ✅ | declaring a broader exception than needed is allowed |

**Q2.** What does each method return?

```java
static int a() { int x = 1; try { return x; } finally { x = 2; } }
static int b() { try { return 1; } finally { return 2; } }
static int c() { try { throw new RuntimeException(); } finally { return 3; } }
static int d() {
    int i = 0;
    while (true) {
        try { i++; if (i >= 3) return i * 10; }
        finally { if (i < 5) continue; }
    }
}
```

> [!success]- Answer
> | Method | Returns | Why |
> |---|---|---|
> | `a()` | `1` | the return value is saved before `finally`; reassigning `x` doesn't change it |
> | `b()` | `2` | `finally`'s `return` replaces the pending one |
> | `c()` | `3` | `finally`'s `return` discards the exception; nothing is thrown |
> | `d()` | `50` | at `i = 3` and `i = 4`, the `continue` in `finally` cancels the pending `return`. At `i = 5`, `finally` completes normally and `return 50` goes through |

**Q3.** What is printed?

```java
try {
    try {
        throw new IllegalArgumentException("first");
    } catch (IllegalArgumentException e) {
        System.out.println("A");
        throw new IllegalStateException("second");
    } catch (IllegalStateException e) {
        System.out.println("B");
    } finally {
        System.out.println("C");
    }
    System.out.println("D");
} catch (RuntimeException e) {
    System.out.println("E " + e.getMessage());
} finally {
    System.out.println("F");
}
```

> [!success]- Answer
> ```
> A
> C
> E second
> F
> ```
> The `IllegalStateException` comes from a `catch` block, so the sibling `catch (IllegalStateException e)` doesn't see it (`B` is not printed). The inner `finally` runs (`C`), the exception leaves the inner `try` statement, so `D` is skipped, and the outer `catch` handles it (`E second`). The outer `finally` runs last (`F`).

**Q4.** What is printed? `Res(name)` prints `open name`, and `close()` prints `close name`.

```java
try (Res a = new Res("A"); Res b = new Res("B")) {
    System.out.println("body");
    throw new IllegalStateException("x");
} catch (IllegalStateException e) {
    System.out.println("catch");
} finally {
    System.out.println("finally");
}
```

> [!success]- Answer
> ```
> open A
> open B
> body
> close B
> close A
> catch
> finally
> ```
> Resources are closed in **reverse** order, and **before** `catch` and `finally` run.

**Q5.** `Res.close()` always throws `IllegalStateException("close failed")`. What exception reaches the caller in each version, and what do `getSuppressed()` and the message show?

```java
// Version 1
Res r = new Res();
try { throw new RuntimeException("body"); }
finally { r.close(); }

// Version 2
try (Res r = new Res()) { throw new RuntimeException("body"); }
```

> [!success]- Answer
> - **Version 1:** `IllegalStateException("close failed")`, with nothing suppressed. The exception from `finally` replaces the body's exception, which is **lost**.
> - **Version 2:** `RuntimeException("body")`, with `getSuppressed()` containing the `IllegalStateException("close failed")`. Try-with-resources keeps the primary exception and attaches the other one.

**Q6.** Which lines compile?

```java
class Base { Base() throws IOException { } }

class A extends Base { A() throws IOException { } }                    // (1)
class B extends Base { B() throws Exception { } }                      // (2)
class C extends Base { C() { } }                                        // (3)
class D extends Base { }                                                // (4)
class E extends Base { E() { try { super(); } catch (IOException e) { } } }   // (5)
```

> [!success]- Answer
> | Class | Compiles? | Reason |
> |---|---|---|
> | `A` | ✅ | declares what the implicit `super()` throws |
> | `B` | ✅ | a constructor may declare a broader exception: constructors aren't overridden, so the override rules don't apply |
> | `C` | ❌ | the implicit `super()` throws `IOException`, which is neither caught nor declared |
> | `D` | ❌ | same, in the default constructor: *unreported exception IOException in default constructor* |
> | `E` | ❌ | `super()` must be the first statement, so it can't be inside a `try` |

**Q7.** Which methods compile? `io()` is declared `throws IOException`.

```java
void a() throws IOException { try { io(); } catch (Exception e) { throw e; } }                       // (1)
void b() { try { int x = 1; } catch (Exception e) { throw e; } }                                     // (2)
void c() throws IOException { try { io(); } catch (Exception e) { e = new Exception(); throw e; } }  // (3)
void d() { try { io(); } catch (IOException e) { throw new RuntimeException(e); } }                  // (4)
```

> [!success]- Answer
> | Method | Compiles? | Reason |
> |---|---|---|
> | (1) | ✅ | precise rethrow: `e` can only be an `IOException` or an unchecked exception |
> | (2) | ✅ | precise rethrow: the `try` can't throw a checked exception, so `e` must be unchecked and no `throws` is needed |
> | (3) | ❌ | `e` is reassigned, so the compiler treats it as a plain `Exception`, which isn't declared |
> | (4) | ✅ | `RuntimeException` is unchecked |

**Q8.** What is printed? Assume the program is run with plain `java Main`.

```java
static int depth = 0;
static void down() { depth++; down(); }

public static void main(String[] args) {
    int x = -1;
    assert x >= 0 : "negative";
    try {
        down();
    } catch (Exception e) {
        System.out.println("Exception");
    } catch (Throwable t) {
        System.out.println("Throwable: " + t.getClass().getSimpleName());
    }
}
```

> [!success]- Answer
> `Throwable: StackOverflowError`. The `assert` does nothing because assertions are disabled without `-ea`. The infinite recursion throws `StackOverflowError`, an `Error`, so `catch (Exception e)` doesn't match and `catch (Throwable t)` does.

**Q9.** What is printed?

```java
class Cfg {
    static final int VALUE = Integer.parseInt("abc");
}

for (int i = 0; i < 2; i++) {
    try {
        System.out.println(Cfg.VALUE);
    } catch (Throwable t) {
        System.out.println(t.getClass().getSimpleName());
    }
}
```

> [!success]- Answer
> ```
> ExceptionInInitializerError
> NoClassDefFoundError
> ```
> The first access runs the static initializer, which throws `NumberFormatException`; the JVM wraps it in `ExceptionInInitializerError`. The class is now marked as unusable, so the second access fails immediately with `NoClassDefFoundError: Could not initialize class Cfg`.

**Q10.** Find the bugs.

```java
static int parseOrZero(String s) {
    int n;
    try {
        n = Integer.parseInt(s);
    } catch (Exception e) { }
    return n;
}
```

> [!success]- Answer
> 1. **Compile error:** `n` might not have been initialized. If `parseInt` throws, nothing assigns `n`.
> 2. **`catch (Exception e)` is too broad.** Only `NumberFormatException` is expected here. With `s == null`, `parseInt` throws `NumberFormatException` too (*Cannot parse null string*), so the broad catch isn't even needed for that.
> 3. **The `catch` is empty**: the failure vanishes silently. That's acceptable here only because "return 0 on bad input" is the documented purpose of the method, and returning the fallback makes the intent explicit.
>
> ```java
> static int parseOrZero(String s) {
>     try {
>         return Integer.parseInt(s);
>     } catch (NumberFormatException e) {
>         return 0;                       // documented fallback
>     }
> }
> ```

**Q11.** Which lines compile?

```java
throw new Exception("x");                         // (1) in a method without throws
throw new RuntimeException("x");                  // (2) in a method without throws
new IllegalStateException("x");                   // (3)
throw null;                                       // (4)
class MyEx<T> extends RuntimeException { }        // (5)
static <T extends Exception> void f() throws T { }   // (6)
```

> [!success]- Answer
> | Line | Compiles? | Note |
> |---|---|---|
> | (1) | ❌ | checked: must be caught or declared |
> | (2) | ✅ | unchecked |
> | (3) | ✅ | but it throws nothing: the object is created and discarded |
> | (4) | ✅ | throws `NullPointerException` at runtime |
> | (5) | ❌ | a generic class may not extend `Throwable` |
> | (6) | ✅ | `throws T` with a bounded type parameter is allowed |

**Q12.** What is printed?

```java
static StringBuilder build() {
    StringBuilder sb = new StringBuilder("a");
    try {
        sb.append("b");
        return sb;
    } finally {
        sb.append("c");
        sb = new StringBuilder("z");
    }
}

System.out.println(build());
```

> [!success]- Answer
> `abc`. The `return` saves the **reference** to the builder holding `"ab"`. `finally` mutates that same object (`"abc"`), then points the local variable `sb` at a new builder, which doesn't affect the saved reference.

---

## 16. Summary

- An **exception** is an object that is **thrown** when something goes wrong. It propagates up the call stack, ending each method it passes through, until a matching `catch` handles it. If none does, the thread ends with a **stack trace**.
- Everything throwable extends **`Throwable`**. **`Error`**s are JVM problems not meant to be caught; **`Exception`**s are for the program; **`RuntimeException`**s usually mean bugs.
- **Checked** exceptions (all `Exception`s outside the `RuntimeException` branch) must be **caught or declared** in `throws`. The compiler checks this using declared types. **Unchecked** exceptions are never forced.
- **`throw`** throws an object; **`throws`** in a header declares what may escape. Creating an exception without `throw` does nothing.
- In `try`/`catch`, the **first** matching `catch` runs, then execution continues **after** the statement. Order `catch` blocks from specific to general. A `catch` for a checked exception the `try` can't throw doesn't compile. **Multi-catch** alternatives can't be related, and its parameter is `final`.
- **`finally`** runs however the `try` ends, except after `System.exit`. A `return` value is saved before `finally` runs. A `return`/`break`/`continue` in `finally` swallows exceptions, and an exception in `finally` masks the original.
- **Try-with-resources** closes `AutoCloseable` resources automatically, in reverse order, **before** `catch`/`finally`. If both the body and `close()` throw, the body's exception wins and the other is **suppressed**, not lost.
- **Custom exceptions** extend `Exception` or `RuntimeException` and can't be generic. Prefer the standard exceptions (`IllegalArgumentException`, `IllegalStateException`, …) when they fit.
- When wrapping, **keep the cause**. When reading a stack trace, find the deepest `Caused by:` and the first frame in your own code.
- A subclass constructor must declare its superclass constructor's checked exceptions. Static initializers can't throw checked exceptions; a runtime failure there gives `ExceptionInInitializerError`, then `NoClassDefFoundError`.
- Don't swallow exceptions, don't catch `Exception` blindly, don't use exceptions for control flow, and don't rely on `assert` for validation.

## Related

- [[Java/00 - Syllabus|Syllabus]]
- Previous: [[Java/04 - Object-Oriented Programming/08 - Nested and Anonymous Classes|Nested and Anonymous Classes]] · Next: [[Java/05 - Working with Data and Errors/02 - Generics|Generics]]
- [[Java/01 - Foundations/05 - Reading Input|Reading Input]]: `try`/`catch` for invalid input (`InputMismatchException`, `NumberFormatException`), `throws IOException` with `BufferedReader`
- [[Java/03 - Program Structure/01 - Methods|Methods]]: the `throws` clause in a method header, the call stack, `StackOverflowError`
- [[Java/04 - Object-Oriented Programming/03 - Inheritance#3.3 The Rules for a Valid Override|Inheritance § 3.3]]: `throws` rules for overriding methods
- [[Java/04 - Object-Oriented Programming/04 - Polymorphism#2.3 The Declared Type Also Fixes the Return Type and Exceptions|Polymorphism § 2.3]]: the declared type decides which checked exceptions a call throws
- [[Java/04 - Object-Oriented Programming/01 - Classes and Objects#3.4 Object Lifetime and Garbage Collection|Classes and Objects § 3.4]]: why resources must be closed explicitly
- [[Java/05 - Working with Data and Errors/02 - Generics#7.2 What Erasure Forbids|Generics § 7.2]]: why exception classes can't be generic
- [[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]]: `ConcurrentModificationException`, `UnsupportedOperationException`, `NoSuchElementException` in practice
- [[Java/07 - Input and Output/01 - File I-O|File I/O]]: try-with-resources with files, `IOException` everywhere
