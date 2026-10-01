# Java — Syllabus

This note is the index for the `Java/` folder. Each chapter below is (or will become) its own note, ordered roughly in the sequence it should be studied. It covers the core progression needed to build a solid foundation. More chapters can be added as they come up.

Checkboxes track progress: checked means the note exists and is written; unchecked means the chapter is planned but not yet created.

## Part I — Foundations

- [x] [[01 - Introduction to Java|Introduction to Java]] — the JVM, JDK, and JRE; compiling and running a program; the structure of a minimal Java file
- [x] [[02 - Variables and Data Types|Variables and Data Types]] — primitive types, reference types, declaration, and initialization
- [x] [[03 - Operators|Operators]] — arithmetic, relational, logical, assignment, and bitwise operators; operator precedence
- [x] [[04 - Type Casting|Type Casting]] — implicit and explicit conversion between types, and where the results are non-obvious
- [x] [[Java/01 - Foundations/05 - Reading Input|Reading Input]] — reading keyboard input with `Scanner` and `BufferedReader`, parsing and validating it

## Part II — Control Flow

- [x] [[01 - Conditional Statements|Conditional Statements]] — `if` / `else if` / `else`, `switch`
- [x] [[02 - Loops|Loops]] — `for`, `while`, `do-while`, `break`, `continue`
- [x] [[03 - Arrays|Arrays]] — declaration, initialization, multi-dimensional arrays, common pitfalls

## Part III — Program Structure

- [x] [[01 - Methods|Methods]] — declaration, parameters, return types, overloading, varargs, recursion
- [x] [[02 - Strings|Strings]] — the `String` class, immutability, common `String` methods, `StringBuilder`, formatted output with `printf`/`String.format`

## Part IV — Object-Oriented Programming

- [x] [[01 - Classes and Objects|Classes and Objects]] — fields, constructors, `this`, instance vs. static members
- [x] [[Java/04 - Object-Oriented Programming/02 - Encapsulation|Encapsulation]] — access modifiers, getters and setters, why state is hidden
- [x] [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]] — `extends`, method overriding, `super`
- [x] [[Java/04 - Object-Oriented Programming/04 - Polymorphism|Polymorphism]] — dynamic dispatch, upcasting/downcasting in practice
- [ ] [[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]] — abstract classes and interfaces, when to use each
- [ ] [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]] — `equals`, `hashCode`, and `toString`
- [ ] [[Java/04 - Object-Oriented Programming/07 - Enums|Enums]] — type-safe constants, enums with fields and methods
- [ ] [[Java/04 - Object-Oriented Programming/08 - Nested and Anonymous Classes|Nested and Anonymous Classes]] — static nested, inner, local, and anonymous classes

## Part V — Working with Data and Errors

- [ ] [[Java/05 - Working with Data and Errors/01 - Exception Handling|Exception Handling]] — `try` / `catch` / `finally`, checked vs. unchecked exceptions, custom exceptions
- [x] [[Java/05 - Working with Data and Errors/02 - Generics|Generics]] — generic classes and methods, bounded types, wildcards, type erasure
- [ ] [[Java/05 - Working with Data and Errors/03 - Comparable and Comparator|Comparable and Comparator]] — natural and custom orderings, sorting objects
- [ ] [[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]] — `List`, `Set`, `Map`, and choosing between implementations

## Part VI — Functional Programming

- [ ] [[Java/06 - Functional Programming/01 - Lambdas and Functional Interfaces|Lambdas and Functional Interfaces]] — lambda syntax, `java.util.function`, method references
- [ ] [[Java/06 - Functional Programming/02 - Streams|Streams]] — stream pipelines, operations, and collectors
- [ ] [[Java/06 - Functional Programming/03 - Optional|Optional]] — representing "maybe a value" without `null`

## Part VII — Input and Output

- [ ] [[Java/07 - Input and Output/01 - File I-O|File I/O]] — reading and writing text files

## Later — Optional Chapters

- Concurrency
- Testing with JUnit
- Build tools (Maven / Gradle)
- Date and time (`java.time`)
- Modules

## Notes

- Order within each part is the intended reading order; order across parts is intended to be sequential (Part I before Part II, and so on).
- This syllabus will be updated as chapters are added or reordered.
- Authoring details (what each chapter must cover, conventions, decisions) are in [[Java/99 - Authoring Guide|Authoring Guide]].
