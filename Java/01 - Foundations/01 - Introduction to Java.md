# Introduction to Java

Java is a **statically typed, object-oriented, garbage-collected** language whose source code is compiled not to machine code but to <span class="hl-blue">bytecode</span>, which is then executed by the <span class="hl-blue">Java Virtual Machine (JVM)</span>. This chapter covers the pieces of the Java platform (JVM, JRE, JDK), the path a program takes from a `.java` file to running code, the structure of a minimal program, and the rules around file names, `main`, and the command line that commonly trip up beginners.

The next chapter, [[02 - Variables and Data Types|Variables and Data Types]], starts on the language itself. This one is about the platform and program structure.

## Contents

- [[#1. What Java Is|1. What Java Is]]
- [[#2. JVM, JRE, and JDK|2. JVM, JRE, and JDK]]
- [[#3. From Source Code to Running Program|3. From Source Code to Running Program]]
- [[#4. A Minimal Java Program|4. A Minimal Java Program]]
- [[#5. Compiling and Running from the Command Line|5. Compiling and Running from the Command Line]]
- [[#6. Files, Classes, and Names|6. Files, Classes, and Names]]
- [[#7. The `main` Method|7. The `main` Method]]
- [[#8. Statements, Blocks, and Comments|8. Statements, Blocks, and Comments]]
- [[#9. Printing Output|9. Printing Output]]
- [[#10. Compile-Time vs. Runtime Errors|10. Compile-Time vs. Runtime Errors]]
- [[#11. Java Versions and Portability|11. Java Versions and Portability]]
- [[#12. Common Pitfalls|12. Common Pitfalls]]
- [[#13. Quick Reference — Non-Obvious Outcomes|13. Quick Reference — Non-Obvious Outcomes]]
- [[#14. Practice — Trick Questions|14. Practice — Trick Questions]]
- [[#15. Summary|15. Summary]]

---

## 1. What Java Is

| Property | Meaning in practice |
|---|---|
| **Compiled to bytecode** | `javac` turns source into platform-independent `.class` files, not into a native `.exe`. |
| **Runs on a virtual machine** | The JVM executes bytecode, so the same `.class` file runs on Windows, Linux, and macOS: "write once, run anywhere". |
| **Statically typed** | Every variable's type is known and checked at compile time (see [[Java/01 - Foundations/02 - Variables and Data Types|Variables and Data Types]]). |
| **Object-oriented** | All code lives inside classes. There are no free-standing functions (before Java 25; see [[#7.4 Java 25+ — Instance Main Methods and Compact Source Files|7.4]]). |
| **Garbage-collected** | Memory for objects is reclaimed automatically; there is no `free`/`delete`. |
| **Case-sensitive** | `Main`, `main`, and `MAIN` are three different identifiers. |

> [!warning] Common mistake
> Java and **JavaScript** are unrelated languages. The name similarity is a 1990s marketing decision. They differ in typing, runtime, and almost everything else.

---

## 2. JVM, JRE, and JDK

The three acronyms describe **nested** layers of the platform:

```
┌──────────────────────── JDK ────────────────────────┐
│  javac, jar, javap, jshell, javadoc, debugger ...   │
│  ┌───────────────────── JRE ─────────────────────┐  │
│  │  standard class library (java.lang, java.util…)│  │
│  │  ┌──────────────────── JVM ─────────────────┐  │  │
│  │  │ class loader · bytecode verifier ·       │  │  │
│  │  │ interpreter · JIT compiler · GC          │  │  │
│  │  └──────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

| Component | Full name | What it is | Needed to… |
|---|---|---|---|
| **JVM** | Java Virtual Machine | The engine that loads, verifies, and executes bytecode. It is platform-specific (there is a different JVM build per OS/CPU). | run bytecode |
| **JRE** | Java Runtime Environment | JVM + the standard class library. | **run** Java programs |
| **JDK** | Java Development Kit | JRE + development tools (`javac`, `jar`, `javap`, `jshell`, …). | **write and compile** Java programs |

> [!note] Definition — bytecode
> <span class="hl-blue">Bytecode</span> is the instruction set of the JVM: a compact, platform-independent format stored in `.class` files. It is not machine code for any real CPU. The JVM either interprets it or compiles it to native code at runtime.

> [!info]- Is the JRE still a separate download?
> Not since **Java 11**. Oracle and most vendors (e.g. Eclipse Temurin) now ship only the JDK. To distribute an application with a trimmed-down runtime, you build a custom one with the `jlink` tool. The *concept* of a JRE (runtime without the compiler) is still what exam questions mean by the term.

> [!important] Key rule
> **The bytecode is portable, but the JVM is not.** "Write once, run anywhere" works because each platform has its own JVM that understands the same bytecode.

---

## 3. From Source Code to Running Program

```
HelloWorld.java ──javac──▶ HelloWorld.class ──java──▶ JVM ──▶ output
  (source code)            (bytecode)                (loads, verifies,
                                                      interprets / JIT-compiles)
```

| Step | Tool | Input → Output | What can fail here |
|---|---|---|---|
| 1. Write | editor / IDE | → `HelloWorld.java` | — |
| 2. Compile | `javac` | `.java` → `.class` (one per class) | **compile-time errors**: syntax, types, missing symbols |
| 3. Load | JVM class loader | `.class` → in-memory class | `ClassNotFoundException`, `NoClassDefFoundError` |
| 4. Verify | bytecode verifier | checks the bytecode is safe/well-formed | `VerifyError` (rare with `javac` output) |
| 5. Execute | interpreter + **JIT** | bytecode → native code at runtime | **runtime exceptions**: `NullPointerException`, `ArithmeticException`, … |

> [!info]- What is the JIT compiler, and why does Java "warm up"?
> The JVM starts by **interpreting** bytecode instruction by instruction, which is slow. It profiles which methods run often ("hot spots") and compiles those to optimized native machine code with the **Just-In-Time (JIT) compiler**. So Java is *both* compiled (by `javac`, to bytecode) *and* compiled again (by the JIT, to native code at runtime). This is why a Java program often runs faster after a few seconds than at startup, and why naïve micro-benchmarks of Java code are misleading.

> [!tip] Seeing the bytecode
> `javap -c HelloWorld` disassembles a `.class` file and shows its bytecode instructions. It is useful later for checking what the compiler actually generated, e.g. for `i++` vs. `++i` or string concatenation.

---

## 4. A Minimal Java Program

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

| Piece | Meaning |
|---|---|
| `public class HelloWorld` | Declares a class named `HelloWorld`. Because it is `public`, the file **must** be named `HelloWorld.java`. |
| `{ … }` (outer) | The class body. Everything (fields, methods) lives inside a class. |
| `public` | The JVM must be able to call `main` from outside the class. |
| `static` | `main` belongs to the class itself, so the JVM can call it **without creating an object**. |
| `void` | `main` returns nothing. The exit code is set with `System.exit(n)`, not with `return n`. |
| `main` | The exact name the JVM looks for as the entry point. |
| `String[] args` | Command-line arguments, as an array of strings. |
| `System.out.println(...)` | Prints its argument followed by a newline. `System` is a class in `java.lang`, which is imported automatically. |
| `;` | Terminates each statement. |

---

## 5. Compiling and Running from the Command Line

### 5.1 The Two-Step Way

```
javac HelloWorld.java     ← compile: takes a FILE NAME (with .java)
java HelloWorld           ← run:     takes a CLASS NAME (no extension)
```

> [!warning] Common mistake
> `java HelloWorld.class` does **not** work:
> ```
> Error: Could not find or load main class HelloWorld.class
> Caused by: java.lang.ClassNotFoundException: HelloWorld.class
> ```
> `java` expects a *class name*, and it reads `HelloWorld.class` as "a class named `class` in package `HelloWorld`". Remember: **`javac` gets the file, `java` gets the class**.

### 5.2 The Single-File Source Launcher (Java 11+)

A single source file can be compiled in memory and run in one command:

```
java HelloWorld.java
```

No `.class` file is written to disk. This is convenient for small programs and scripts, but for anything with multiple files you still normally compile with `javac` (or a build tool/IDE). Java 22+ extends the launcher to programs spread over several source files.

### 5.3 Command-Line Arguments

```
java Greet Ada "Grace Hopper" 42
```

```java
public class Greet {
    public static void main(String[] args) {
        System.out.println(args.length);  // 3
        System.out.println(args[0]);      // Ada
        System.out.println(args[1]);      // Grace Hopper   (quotes group words)
        System.out.println(args[2] + 1);  // 421            (a String, not a number!)
    }
}
```

- `args[0]` is the **first argument**, not the program name (unlike C/C++'s `argv[0]`).
- With no arguments, `args` is an **empty array** (`args.length == 0`), **never `null`**. Accessing `args[0]` then throws `ArrayIndexOutOfBoundsException`.
- Every argument is a `String`. Convert explicitly with `Integer.parseInt(args[2])` (see [[04 - Type Casting#8. What Casting Cannot Do|What Casting Cannot Do]]). What `parseInt` accepts and rejects is in [[Java/01 - Foundations/05 - Reading Input#4. Parsing Strings into Numbers|Reading Input § 4]], and reading from the keyboard instead is covered in the rest of that chapter.

### 5.4 Packages and the Classpath

Real projects put classes in **packages**, and the directory structure must mirror the package name:

```java
// file: src/com/example/App.java
package com.example;

public class App {
    public static void main(String[] args) {
        System.out.println("packaged");
    }
}
```

```
javac -d out src/com/example/App.java    ← -d: write .class files under out/, creating com/example/
java -cp out com.example.App             ← -cp: where to look for classes; then the FULLY-QUALIFIED name
```

> [!warning] Common mistake
> For a class in a package, `cd out/com/example` followed by `java App` fails with `NoClassDefFoundError: App (wrong name: com/example/App)`. The JVM looks for classes relative to the **classpath root** (`out/`) and needs the **fully-qualified name** (`com.example.App`).

---

## 6. Files, Classes, and Names

> [!important] Key rules
> 1. A file may contain **at most one `public` top-level class**, and if it has one, the file **must** be named exactly after it (`Foo` → `Foo.java`, case included).
> 2. A file may contain **any number of non-public top-level classes**.
> 3. `javac` produces **one `.class` file per class**, not per source file.

```java
// File: Bar.java
public class Foo { }
// error: class Foo is public, should be declared in a file named Foo.java
```

```java
// File: Hello.java: compiles to Hello.class AND Helper.class
public class Hello {
    public static void main(String[] args) { }
}
class Helper { }
```

Edge cases:

- **No public class at all?** Then the file can be named anything (`Whatever.java` containing only `class A {}` compiles to `A.class`). Legal, but confusing. Don't do it.
- **Nested classes** get their own files with a `$`: `Outer.Inner` → `Outer$Inner.class`; anonymous classes → `Outer$1.class`.
- **Case on Windows:** the Windows file system is case-insensitive but Java is not. After compiling `Case.java` (class `Case`), running `java case` fails with `NoClassDefFoundError: case (wrong name: Case)`.

---

## 7. The `main` Method

### 7.1 What Counts as a Valid Entry Point (classic rules)

The JVM looks for a method that is **`public`, `static`, returns `void`, is named `main`, and takes a single `String[]` parameter**. Anything that satisfies that is fine, even if it looks unusual:

| Signature | Valid entry point? | Why |
|---|---|---|
| `public static void main(String[] args)` | ✅ | the canonical form |
| `public static void main(String... args)` | ✅ | varargs *is* a `String[]` parameter |
| `public static void main(String args[])` | ✅ | C-style array syntax, same type |
| `static public void main(String[] args)` | ✅ | modifier order doesn't matter |
| `public static void main(final String[] a)` | ✅ | `final` and parameter name are irrelevant |
| `public static final void main(String[] args)` | ✅ | `final` on a static method is allowed |
| `public void main(String[] args)` | ❌ (≤ Java 24) | runtime: *Main method is not static* |
| `public static int main(String[] args)` | ❌ | runtime: *Main method must return a value of type void* |
| `static void main(String[] args)` | ❌ (≤ Java 24) | runtime: *Main method not found* (not `public`) |
| `public static void main(String args)` | ❌ | a single `String`, not `String[]` |
| `public static void Main(String[] args)` | ❌ | case-sensitive name |

> [!warning] Common mistake: these compile!
> Every ❌ row above **compiles without error**. `main` is just an ordinary method as far as `javac` is concerned. The problem only appears at **run time**, when the `java` launcher fails to find a usable entry point. "It compiled, so `main` must be right" is false.

### 7.2 `main` Can Be Overloaded

```java
public class M {
    public static void main(String[] args) { main(5); }
    static void main(int x) { System.out.println("overload " + x); }   // prints: overload 5
}
```

Only the `(String[])` version is the entry point. The others are ordinary overloads (see [[01 - Methods#7. Method Overloading|Methods § 7]]).

### 7.3 Exit Status

`main` returns `void`, so a program reports success/failure with `System.exit(status)` (0 = success, non-zero = error). Returning normally from `main` ends the program with status 0, provided no other non-daemon threads are still running. An uncaught exception ends it with a non-zero status and a stack trace on standard error.

### 7.4 Java 25+ — Instance Main Methods and Compact Source Files

> [!info]- Newer, simplified entry points (finalized in Java 25)
> After previews in Java 21–24, **Java 25** (JEP 512) relaxed the launch rules for beginners:
> - `main` may be an **instance** method and need not be `public` (it must not be `private`). The launcher creates an object with the no-arg constructor and calls it.
> - `main` may take **no parameters**. `void main()` is accepted if no `main(String[])` exists.
> - A **compact source file** may contain methods and fields with no enclosing `class` declaration. The compiler wraps them in an implicit class.
> - The new `java.lang.IO` class offers `IO.println(...)` / `IO.readln(...)` shortcuts.
>
> ```java
> // Hello.java: valid on Java 25+
> void main() {
>     IO.println("Hello, World!");
> }
> ```
>
> On **any earlier JDK** this fails. On Java 17, `public void main(String[] args)` compiles but the launcher reports *Main method is not static*. Courses and exams usually expect the classic `public static void main(String[] args)`, and it remains valid on every version. Know which JDK you are using (`java -version`).

---

## 8. Statements, Blocks, and Comments

- A **statement** ends with `;`. A **block** is zero or more statements in `{ }`, and it also defines a variable scope (see [[02 - Variables and Data Types#8. Scope and Shadowing|Scope and Shadowing]]).
- **Whitespace and line breaks are insignificant** (except inside string literals and to separate tokens). The whole program could be on one line.
- An empty statement `;` is legal: `if (x > 0);` compiles, and it is a classic bug (see [[01 - Conditional Statements|Conditional Statements]]).

### 8.1 Three Kinds of Comments

```java
// single-line comment: to the end of the line

/* multi-line comment
   spanning several lines */

/**
 * Javadoc comment: processed by the javadoc tool to generate HTML documentation.
 * @param args the command-line arguments
 */
```

> [!warning] Block comments do not nest
> ```java
> /* outer /* inner */ this is now code! */   // compile error
> ```
> The first `*/` ends the comment, whatever `/*` came before it. Commenting out a region that already contains a `/* … */` breaks. Use `//` on each line (IDEs do this with Ctrl+/).

### 8.2 Unicode Escapes Are Processed *Before* Everything Else

<span class="hl-yellow">A classic trick question.</span> The compiler translates `\uXXXX` escapes into the actual characters **before** it even identifies comments, strings, and tokens. So escapes inside comments are not inert:

```java
public static void main(String[] args) {
    // \u000d System.out.println("printed from inside a comment!");
}
```

This **prints** the message. `\u000d` is a carriage return, i.e. a line break, so the `System.out.println` ends up on a new line *outside* the `//` comment.

The same rule produces two more surprises:

```java
// files live in C:\users\me
```
→ **compile error: illegal unicode escape**. `\users` starts with `\u`, which must be followed by four hex digits, even inside a comment.

```java
System.out.println("a\u0022.length());   // prints 1
```
`\u0022` is `"`, so this is really `System.out.println("a".length());`.

> [!info]- Why does the compiler work this way?
> The Java Language Specification defines Unicode-escape translation as the very **first lexical step**, so that a program written with only ASCII characters can express any Unicode character anywhere, including in identifiers. The consequence is that the translation cannot know what is "inside a comment" yet, because comments are recognized in a later step. Ordinary escapes like `\n` and `\t` are **not** like this. They are only interpreted inside char/string literals.

---

## 9. Printing Output

| Call | Behaviour |
|---|---|
| `System.out.println(x)` | prints `x`, then a newline |
| `System.out.println()` | prints just a newline |
| `System.out.print(x)` | prints `x`, **no** newline |
| `System.out.printf(fmt, ...)` | formatted output, no automatic newline (see [[Java/03 - Program Structure/02 - Strings#6. Formatted Output — `printf` and `String.format`|Strings § 6]]) |
| `System.err.println(x)` | prints to **standard error** (often shown in red in IDEs; not captured by `>` redirection) |

`println` is **overloaded** for every primitive type, `char[]`, `String`, and `Object`. That leads to some less obvious results:

```java
System.out.println('a' + 'b');    // 195 : char + char is int arithmetic (97 + 98)
System.out.println("" + 'a' + 'b'); // ab
char[] letters = {'h', 'i'};
System.out.println(letters);      // hi : the char[] overload prints the characters
int[] nums = {1, 2};
System.out.println(nums);         // [I@1b6d3586 : the Object overload prints type@hash
System.out.println(null);         // compile error: reference to println is ambiguous
```

> [!info]- Why is `println(null)` ambiguous?
> `null` fits both `println(char[])` and `println(String)`, and neither type is more specific than the other (they aren't related by inheritance), so the compiler can't choose. `println((String) null)` compiles and prints `null`, and `println((Object) null)` does too.

> [!tip]
> `System.out` and `System.err` are separate streams. When both are used, their output can appear **interleaved out of order** in the console, because they are buffered and flushed independently.

---

## 10. Compile-Time vs. Runtime Errors

| | Compile-time error | Runtime error (exception) |
|---|---|---|
| Detected by | `javac` | the JVM, while running |
| Program runs? | No, no `.class` file is produced | Yes, until the failing line |
| Examples | missing `;`, type mismatch, undefined variable, uninitialized local, unreachable code | `NullPointerException`, `ArithmeticException` (`/ by zero`), `ArrayIndexOutOfBoundsException`, `ClassCastException` |
| Also | — | **logic errors**: the program runs "successfully" but computes the wrong result; no tool reports these |

```java
int x = "hello";        // compile-time: incompatible types
int y = 5 / 0;          // compiles! runtime: ArithmeticException: / by zero
double z = 5.0 / 0;     // compiles and runs: z == Infinity, no error at all
```

The last two are covered in detail in [[03 - Operators#3. Division and Remainder — The Special Cases|Operators § 3]].

> [!tip] Reading compiler errors
> Fix the **first** error first. One missing `;` or `}` can cause a cascade of misleading errors further down, and they often disappear once the first is fixed. The reported line is where the compiler *noticed* the problem, which may be after where it actually is (e.g. a missing `;` is reported at the start of the next line).

---

## 11. Java Versions and Portability

- Java releases a new version **every six months**. Every few releases is an **LTS** (long-term support) version: **8, 11, 17, 21, 25**. Courses usually target an LTS.
- Each JDK version emits a specific **class-file version**: Java 8 → 52, 11 → 55, 17 → 61, 21 → 65, 25 → 69.
- A JVM can run class files from its **own and older** versions, **never newer** ones:

```
Exception in thread "main" java.lang.UnsupportedClassVersionError: App has been compiled
by a more recent version of the Java Runtime (class file version 65.0), this version of
the Java Runtime only recognizes class file versions up to 61.0
```
→ compiled with JDK 21, run on a Java 17 JVM. Fix: run with a newer JVM, or compile for the older target with `javac --release 17 App.java`.

> [!warning] Common mistake
> Having several JDKs installed and `javac` / `java` on the `PATH` pointing at **different** versions. Check both with `javac -version` and `java -version`.

---

## 12. Common Pitfalls

- **`java HelloWorld.class`** or **`java HelloWorld.java` when you meant the compiled class.** `java` takes a class name. The `.java` form works only via the source launcher (Java 11+).
- **Public class name ≠ file name** (including case: `helloWorld.java` for `public class HelloWorld`) → compile error.
- **`main` with the wrong signature** compiles fine and fails only at launch (§ 7.1).
- **Assuming `args[0]` is the program name**, or that `args` is `null` when there are no arguments. It's an empty array.
- **Treating command-line arguments as numbers.** They are `String`s, so `args[0] + 1` concatenates.
- **Nested `/* */` comments**, and **`\u` inside comments** (e.g. Windows paths like `C:\users`) → compile errors.
- **Missing semicolon reported on the wrong line.** Look at the end of the *previous* line.
- **Class compiled with a newer JDK than the JVM running it** → `UnsupportedClassVersionError`.
- **Running a packaged class from inside its directory** instead of from the classpath root with the fully-qualified name.

---

## 13. Quick Reference — Non-Obvious Outcomes

| Code / Command | Result | Category |
|---|---|---|
| `java HelloWorld.class` | `ClassNotFoundException: HelloWorld.class` | `java` takes a class name, not a file |
| `java HelloWorld.java` | compiles in memory and runs (Java 11+) | single-file source launcher |
| `public class Foo` in `Bar.java` | compile error | public class must match file name |
| two top-level classes in one file | compiles; **two** `.class` files | one `.class` per class |
| `public void main(String[] args)` | compiles; launch fails "not static" (≤ Java 24) | entry-point rules are checked at run time |
| `static public void main(String... a)` | valid entry point | modifier order / varargs / name don't matter |
| no arguments given | `args.length == 0`, `args != null` | args is never null |
| `// \u000d System.out.println("x");` | **prints** `x` | Unicode escapes processed before comments |
| `// C:\users\me` | compile error: illegal unicode escape | `\u` must be followed by 4 hex digits |
| `/* a /* b */ c */` | compile error | block comments don't nest |
| `System.out.println('a' + 'b')` | `195` | `char + char` is `int` addition |
| `System.out.println(new int[]{1})` | `[I@…` | arrays don't override `toString()` |
| `System.out.println(new char[]{'h','i'})` | `hi` | dedicated `println(char[])` overload |
| `System.out.println(null)` | compile error: ambiguous | `char[]` vs. `String` overloads |
| class from JDK 21 run on JVM 17 | `UnsupportedClassVersionError` | JVMs don't run newer class files |

---

## 14. Practice — Trick Questions

**Q1.** A file `Test.java` contains `class A {}` and `class B {}` and nothing else. Does it compile, and what files are produced?

> [!success]- Answer
> It compiles, producing `A.class` and `B.class` (and no `Test.class`). The file-name rule only applies to a **public** top-level class, and there isn't one.

**Q2.** Does this program compile? If yes, what happens when you run `java Q`?

```java
public class Q {
    public static void main(String args) {
        System.out.println("hi");
    }
}
```

> [!success]- Answer
> It **compiles** (it's a legal method). Running it fails with *Main method not found in class Q*, because the parameter is a `String`, not a `String[]`.

**Q3.** What does `java Sum 2 3` print?

```java
public class Sum {
    public static void main(String[] args) {
        System.out.println(args[0] + args[1]);
        System.out.println(Integer.parseInt(args[0]) + Integer.parseInt(args[1]));
    }
}
```

> [!success]- Answer
> ```
> 23
> 5
> ```
> Arguments are `String`s, so `+` concatenates them. They must be parsed to add them numerically.

**Q4.** What does this print?

```java
public class U {
    public static void main(String[] args) {
        int x = 1;
        // x is incremented below \u000a x++;
        System.out.println(x);
    }
}
```

> [!success]- Answer
> `2`. `\u000a` is a newline, translated before comments are recognized, so `x++;` lands on its own line and is real code.

**Q5.** True or false: "If a program compiles, `javac` has checked that `main` is a valid entry point."

> [!success]- Answer
> **False.** `javac` treats `main` like any other method. The entry-point requirements (`static`, `void`, `String[]` parameter, and `public` before Java 25) are checked by the `java` launcher at run time.

**Q6.** Which of JVM / JRE / JDK is the minimum needed to (a) run a `.class` file, (b) compile a `.java` file?

> [!success]- Answer
> (a) a **JRE** (JVM + class library). The JVM alone has no standard library, so it can't run a real program. (b) a **JDK**, since only it includes `javac`.

---

## 15. Summary

- Java source (`.java`) is compiled by **`javac`** into platform-independent **bytecode** (`.class`), which the **JVM** loads, verifies, interprets, and JIT-compiles at run time.
- **JDK ⊃ JRE ⊃ JVM**: the JDK adds development tools, the JRE adds the class library, and the JVM executes bytecode. The bytecode is portable, while the JVM is platform-specific.
- **`javac` takes file names, `java` takes class names.** `java File.java` works only through the Java 11+ single-file launcher.
- A file may hold **one public top-level class**, which must match the file name exactly. Each class compiles to its own `.class` file.
- The classic entry point is `public static void main(String[] args)`. A wrong signature **compiles** but fails at launch. Java 25+ also accepts instance/no-arg `main` methods and compact source files.
- `args` is never `null`, `args[0]` is the first real argument, and all arguments are `String`s.
- **Unicode escapes are translated before comments are recognized.** This is the source of several "impossible" compile errors and hidden code.
- Compile-time errors stop compilation. Runtime exceptions stop execution. Logic errors stop nothing.

## Related

- [[00 - Syllabus|Syllabus]]
- Next: [[02 - Variables and Data Types|Variables and Data Types]]
- [[03 - Operators|Operators]]: runtime arithmetic errors, `char` arithmetic
- [[02 - Strings|Strings]]: `printf` and formatted output
