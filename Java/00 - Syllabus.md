# Java — Syllabus

This note is the index for the `Java/` folder. Each chapter below is (or will become) its own note, ordered roughly in the sequence it should be studied. This is not an exhaustive list of every Java topic — it covers the core progression needed to build a solid foundation. Additional chapters (concurrency, testing, build tools, etc.) are listed under [[#Later — Optional Chapters|Later — Optional Chapters]] and can be promoted into a part as they come up.

Checkboxes track progress: checked means the note exists and is written; unchecked means the chapter is planned but not yet created. Clicking an unchecked link in Obsidian will create the note at its final, numbered path.

Unwritten chapters carry a brief underneath them:
- **Cover** — the scope, in addition to the one-line description.
- **Traps** — trick questions and edge cases that must be included (see the completeness rule in `CLAUDE.md`).
- **Promised by** — places in already-written notes that say "covered in …" and point here. The chapter must deliver these, and those notes should get a back-link once it exists.

## Part I — Foundations

- [x] [[01 - Introduction to Java|Introduction to Java]] — the JVM, JDK, and JRE; compiling and running a program; the structure of a minimal Java file
- [x] [[02 - Variables and Data Types|Variables and Data Types]] — primitive types, reference types, declaration, and initialization
- [x] [[03 - Operators|Operators]] — arithmetic, relational, logical, assignment, and bitwise operators; operator precedence
- [x] [[04 - Type Casting|Type Casting]] — implicit and explicit conversion between types, and where the results are non-obvious
- [ ] [[Java/01 - Foundations/05 - Reading Input|Reading Input]] — reading keyboard input with `Scanner` and `BufferedReader`, parsing numbers, validating input
	- **Cover:** `new Scanner(System.in)`; `next`, `nextLine`, `nextInt`, `nextDouble`, `hasNextInt`, … (token-based vs. line-based reading); an input-validation loop with `hasNextX`; `Integer.parseInt` / `Double.parseDouble`; `BufferedReader` + `readLine` (faster, throws `IOException`); reading until end of input. Command-line arguments are already in [[01 - Introduction to Java#5.3 Command-Line Arguments|Introduction to Java § 5.3]]; link, don't repeat.
	- **Traps:** `nextInt()` followed by `nextLine()` returns `""` (the leftover newline); `InputMismatchException` leaves the bad token in the buffer, so a `try`/`catch` retry loop spins forever unless it calls `next()`; `nextDouble()` is **locale-dependent** (on a Greek-locale machine it expects `3,5`, not `3.5`; fix with `useLocale(Locale.US)`); `NumberFormatException` from `parseInt(" 42")` (spaces) and `parseInt("4.0")`; closing a `Scanner` on `System.in` closes `System.in` for good; two `Scanner`s on `System.in` steal each other's buffered input; comparing input with `==` instead of `equals`.
	- **Promised by:** none formally, but [[02 - Loops|Loops]] and [[03 - Arrays|Arrays]] use `Scanner` in examples without explaining it. Add back-links there.

## Part II — Control Flow

- [x] [[01 - Conditional Statements|Conditional Statements]] — `if` / `else if` / `else`, `switch`
- [x] [[02 - Loops|Loops]] — `for`, `while`, `do-while`, `break`, `continue`
- [x] [[03 - Arrays|Arrays]] — declaration, initialization, multi-dimensional arrays, common pitfalls

## Part III — Program Structure

- [x] [[01 - Methods|Methods]] — declaration, parameters, return types, overloading, varargs, recursion
- [x] [[02 - Strings|Strings]] — the `String` class, immutability, common `String` methods, `StringBuilder`, formatted output with `printf`/`String.format`

## Part IV — Object-Oriented Programming

- [x] [[01 - Classes and Objects|Classes and Objects]] — fields, constructors, `this`, instance vs. static members
- [ ] [[Java/04 - Object-Oriented Programming/02 - Encapsulation|Encapsulation]] — access modifiers, getters and setters, why state is hidden
	- **Cover:** the four access levels in a table (`private`, package-private, `protected`, `public`), with what each allows from the same class, the same package, a subclass, and anywhere; top-level classes can only be `public` or package-private; getters/setters and validation in setters; immutable classes (`final` fields, no setters, `final` class, defensive copies); **records** (compact constructors, validation, accessors `x()` not `getX()`, what records can and can't do).
	- **Traps:** access is per **class**, not per object (a method can read another instance's `private` fields); returning an internal array or list lets callers change private state; a `final` field holding a mutable object isn't immutable; `protected` also grants access to the whole package; a record's accessors return the field as-is (shallow).
	- **Promised by:** [[01 - Classes and Objects|Classes and Objects]] (access modifiers, per-class access, records "covered with immutable design", `private` in § 11); [[03 - Arrays|Arrays]] § 10 (defensive copies of array fields); [[01 - Methods|Methods]] § 2 (modifiers).
- [ ] [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]] — `extends`, method overriding, `super`
	- **Cover:** `extends` and single inheritance; what is and isn't inherited; overriding rules (same signature, `@Override`, covariant return types, access can't be narrowed, can't throw broader checked exceptions); `super.method()`; constructor chaining with `super(…)` and the implicit `super()`; initialization order across a hierarchy; `final` methods and classes; `protected`; field **hiding** vs. method overriding; sealed classes (Java 17+). Overriding `toString` can be shown briefly, but the full `equals`/`hashCode` contract is in *Object Methods* below.
	- **Traps:** a superclass without a no-arg constructor breaks subclasses that rely on the implicit `super()`; `super(…)`/`this(…)` must be the first statement; calling an overridable method from a constructor sees uninitialized subclass fields; private methods and static methods are not overridden; fields aren't polymorphic; `@Override` catches signature typos.
	- **Promised by:** [[01 - Classes and Objects|Classes and Objects]] (constructors not inherited, implicit `super()` and the default constructor, superclass step in initialization order); [[01 - Methods|Methods]] (overriding).
- [ ] [[Java/04 - Object-Oriented Programming/04 - Polymorphism|Polymorphism]] — dynamic dispatch, upcasting/downcasting in practice
	- **Cover:** a supertype reference to a subtype object; dynamic dispatch (runtime choice of the overriding method); overloading (compile time) vs. overriding (runtime) side by side; upcasting and downcasting, `instanceof` and pattern matching for `instanceof` (Java 16+); designing with polymorphism instead of `if`/`instanceof` chains.
	- **Traps:** the declared type decides which methods can be *called*, and the runtime type decides which override *runs*; static methods and fields use the declared type (hiding, no dispatch); an overload chosen at compile time plus an override chosen at runtime in the same call; `ClassCastException` on a bad downcast that compiled; generics are invariant (`List<Dog>` is not a `List<Animal>`).
	- **Promised by:** [[01 - Methods|Methods]] § 7.2 (overloading chosen by declared type vs. overriding), [[01 - Classes and Objects|Classes and Objects]] § 8.4 (static methods through a reference don't dispatch). Link to [[Java/01 - Foundations/04 - Type Casting#7. Reference (Object) Casting|Type Casting § 7]] and [[Java/05 - Working with Data and Errors/02 - Generics#5. Generics Are Invariant|Generics § 5]].
- [ ] [[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]] — abstract classes and interfaces, when to use each
	- **Cover:** `abstract` classes and methods; interfaces (implicitly `public abstract` methods, `public static final` constants); `default`, `static`, and `private` interface methods; implementing several interfaces; abstract class vs. interface comparison table; functional interfaces as a preview of Part VI; sealed interfaces.
	- **Traps:** an abstract class can have constructors and state, an interface can't have instance fields; a class inheriting the same `default` method from two interfaces must override it (`A.super.m()` to pick one); interface fields are constants even without `static final`; `abstract` + `final`/`private`/`static` is a compile error; a concrete class that misses one abstract method must itself be `abstract`.
- [ ] [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]] — the `equals` / `hashCode` / `toString` contract that every class inherits from `Object`
	- **Cover:** what `Object` provides; overriding `toString`; the `equals` contract (reflexive, symmetric, transitive, consistent, `x.equals(null) == false`); the `hashCode` contract and why it must agree with `equals`; writing both correctly (`Objects.equals`, `Objects.hash`); `instanceof` vs. `getClass()` in `equals` and the symmetry problem with subclasses; records generate all three; a brief note on `clone` and the deprecated `finalize`.
	- **Traps:** `equals(Student other)` *overloads* instead of overriding (collections still use `Object.equals`), which `@Override` would catch; overriding `equals` without `hashCode` makes `HashSet.contains` and `HashMap.get` fail; changing a field used in `hashCode` after inserting into a `HashSet` "loses" the object; `==` vs. `equals` on strings and wrappers (link, don't repeat); `equals` on arrays is identity.
	- **Promised by:** [[01 - Classes and Objects|Classes and Objects]] § 2.2 and § 10.3 (overriding the inherited `toString`/`equals`/`hashCode`). Needed by *Collections Framework*.
- [ ] [[Java/04 - Object-Oriented Programming/07 - Enums|Enums]] — type-safe constants, enums with fields and methods, `switch` on enums
	- **Cover:** basic `enum`; `values()`, `valueOf`, `name()`, `ordinal()`, `compareTo`; fields, constructors (implicitly `private`), and methods; constant-specific method bodies; enums implementing interfaces; `switch` on an enum (classic and arrow form); `EnumMap` and `EnumSet`; the enum singleton.
	- **Traps:** `valueOf("unknown")` throws `IllegalArgumentException` (and it's case-sensitive); relying on `ordinal()` breaks when constants are reordered; `case RED:` must be unqualified (not `Color.RED`) in a classic `switch`; `==` is safe (and preferred) for enum comparison; enums can't be extended, can't be generic, and can't be created with `new`; a `switch` expression over an enum must be exhaustive.
- [ ] [[Java/04 - Object-Oriented Programming/08 - Nested and Anonymous Classes|Nested and Anonymous Classes]] — static nested, inner, local, and anonymous classes
	- **Cover:** the four kinds with a comparison table; creating inner-class instances (`outer.new Inner()`); `Outer.this.field`; access to the outer class's private members; local classes; anonymous classes (implementing an interface or extending a class inline, e.g. a `Comparator`); capturing local variables (effectively final); when to use each. End with the bridge to lambdas (anonymous class → lambda).
	- **Traps:** an inner class needs an outer instance (can't be created from `static main` without one); a captured local that is modified later is a compile error; `this` inside an anonymous class is the anonymous object, not the outer one; shadowing between inner and outer fields; an inner class keeps a hidden reference to its outer object (memory leaks); static members in inner classes were illegal before Java 16.

## Part V — Working with Data and Errors

- [ ] [[Java/05 - Working with Data and Errors/01 - Exception Handling|Exception Handling]] — `try` / `catch` / `finally`, checked vs. unchecked exceptions, custom exceptions
	- **Cover:** the `Throwable` hierarchy (`Error`, `Exception`, `RuntimeException`); checked vs. unchecked and the "catch or declare" rule; `throw` vs. `throws`; `try`/`catch`/`finally`; multi-catch; **try-with-resources** and `AutoCloseable`, with suppressed exceptions; custom exceptions; reading a stack trace; good practice (don't swallow exceptions, don't catch `Exception` blindly).
	- **Traps:** catch blocks in the wrong order (a superclass before a subclass is an unreachable-code compile error); a `return` in `finally` overrides the `try`'s return and swallows exceptions; an exception thrown in `finally` masks the original one; `finally` runs even after `return` (but not after `System.exit`); catching a checked exception that the `try` can't throw is a compile error; overriding methods can't throw broader checked exceptions; generic classes can't extend `Throwable`, but `<T extends Exception> … throws T` is allowed.
	- **Promised by:** [[01 - Methods|Methods]] § 2 (the `throws` clause); [[01 - Classes and Objects|Classes and Objects]] § 3.4 (try-with-resources for closing resources); [[Java/05 - Working with Data and Errors/02 - Generics#7.2 What Erasure Forbids|Generics § 7.2]].
- [x] [[Java/05 - Working with Data and Errors/02 - Generics|Generics]] — generic classes and methods, bounded types, invariance, wildcards and PECS, type erasure, raw types, autoboxing traps
- [ ] [[Java/05 - Working with Data and Errors/03 - Comparable and Comparator|Comparable and Comparator]] — natural ordering vs. custom orderings, sorting objects
	- **Cover:** `Comparable<T>` and `compareTo` (natural ordering) vs. `Comparator<T>` (external orderings); the `compareTo` contract (sign, antisymmetry, transitivity) and consistency with `equals`; sorting with `Arrays.sort`, `Collections.sort`, `List.sort`; multi-key sorting; `Comparator.comparing`, `thenComparing`, `reversed`, `nullsFirst` (show them with anonymous classes or a brief lambda preview, since lambdas only come in Part VI, and forward-link); sort stability.
	- **Traps:** `return a - b;` in `compareTo` overflows for large or negative values (use `Integer.compare`); a `compareTo` inconsistent with `equals` makes a `TreeSet`/`TreeMap` silently drop "duplicates"; `Comparator<? super T>` and `<T extends Comparable<? super T>>` (link [[Java/05 - Working with Data and Errors/02 - Generics#4.3 Recursive Bounds and `Comparable`|Generics § 4.3]], don't repeat); `reversed()` on a chain applies to the whole chain; sorting a list containing `null` with natural ordering throws `NullPointerException`; the raw `Comparable` mistake (Generics § 2.4).
- [ ] [[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]] — `List`, `Set`, `Map`, and choosing between implementations
	- **Cover:** the interface hierarchy (`Iterable` → `Collection` → `List`/`Set`/`Queue`; `Map` separately); `ArrayList` vs. `LinkedList`; `HashSet`/`LinkedHashSet`/`TreeSet`; `HashMap`/`LinkedHashMap`/`TreeMap`; `Queue`, `Deque` (`ArrayDeque` as a stack and a queue), `PriorityQueue`; iterating and `Iterator`; useful `Map` methods (`getOrDefault`, `putIfAbsent`, `computeIfAbsent`, `merge`, `entrySet`); the `Collections` utility class; immutable collections; a "which implementation?" table with complexities (link the DSA notes).
	- **Traps:** `ConcurrentModificationException` when removing inside a for-each (use `Iterator.remove` or `removeIf`); `List.of`/`Map.of` are unmodifiable and reject `null`; `Arrays.asList` is fixed-size (link [[03 - Arrays#8.4 `asList`|Arrays § 8.4]]); `HashSet`/`HashMap` depend on `equals`/`hashCode` (link *Object Methods*); `TreeSet`/`TreeMap` depend on `compareTo` (link *Comparable and Comparator*); `Map.get` returning `null` is ambiguous (absent key vs. `null` value); `PriorityQueue` iteration order isn't sorted; `Stack`/`Vector` are legacy. The autoboxing traps (`remove(int)` vs. `remove(Object)`, wrong key types) are in [[Java/05 - Working with Data and Errors/02 - Generics#9. Generics and Autoboxing — Traps|Generics § 9]]: link, don't repeat.
	- **Promised by:** [[03 - Arrays|Arrays]] (`ArrayList` as a resizable alternative), [[Java/05 - Working with Data and Errors/02 - Generics|Generics]] (intro and Related).

## Part VI — Functional Programming

- [ ] [[Java/06 - Functional Programming/01 - Lambdas and Functional Interfaces|Lambdas and Functional Interfaces]] — lambda syntax, `java.util.function`, method references
	- **Cover:** from anonymous class to lambda; lambda syntax forms (parameters, block vs. expression body); functional interfaces and `@FunctionalInterface`; target typing; the core `java.util.function` interfaces (`Function`, `BiFunction`, `Predicate`, `Supplier`, `Consumer`, `UnaryOperator`, `BinaryOperator`) and their primitive specializations; the four kinds of method references; composing (`andThen`, `compose`, `Predicate.and/negate`); `Comparator.comparing` chains in full.
	- **Traps:** captured locals must be effectively final (and why a one-element array or `AtomicInteger` "works around" it); `this` in a lambda is the enclosing object, unlike in an anonymous class; a lambda can't shadow a local variable of the enclosing method; a lambda can't throw a checked exception its functional interface doesn't declare; overloaded methods taking different functional interfaces can make a lambda call ambiguous; `var` is not allowed for a lambda variable (`var f = x -> x;` has no target type).
- [ ] [[Java/06 - Functional Programming/02 - Streams|Streams]] — the Stream API: pipelines, intermediate and terminal operations, collectors
	- **Cover:** creating streams (collections, `Arrays.stream`, `Stream.of`, `IntStream.range`, `Stream.iterate`/`generate`); intermediate operations (`filter`, `map`, `flatMap`, `distinct`, `sorted`, `limit`, `skip`, `peek`); terminal operations (`forEach`, `collect`, `reduce`, `count`, `min`/`max`, `anyMatch`/`allMatch`/`noneMatch`, `findFirst`); `Collectors` (`toList`, `toSet`, `toMap`, `joining`, `groupingBy`, `partitioningBy`, `counting`); primitive streams (`IntStream`, `mapToInt`, `sum`, `average`, `boxed`); when a loop is clearer.
	- **Traps:** streams are lazy (no terminal operation → nothing runs, including `peek`); a stream can be consumed only once (`IllegalStateException`); `Collectors.toMap` throws on duplicate keys unless given a merge function; `Stream.toList()` (Java 16+) is unmodifiable while `Collectors.toList()` makes no guarantee; `allMatch` on an empty stream is `true`; `IntStream.average()` returns an `OptionalDouble`; short-circuiting with infinite streams (`limit` placement); side effects in `map`/`forEach` and parallel streams.
- [ ] [[Java/06 - Functional Programming/03 - Optional|Optional]] — representing "maybe a value" without `null`
	- **Cover:** why `Optional` exists; creating (`of`, `ofNullable`, `empty`); consuming (`isPresent`/`isEmpty`, `ifPresent`, `ifPresentOrElse`, `orElse`, `orElseGet`, `orElseThrow`); transforming (`map`, `flatMap`, `filter`); where it is and isn't appropriate (return types yes; fields, parameters, collections no); `OptionalInt` and friends.
	- **Traps:** `Optional.of(null)` throws `NullPointerException`; `orElse(expensive())` **always** evaluates its argument, `orElseGet` doesn't; `get()` on an empty `Optional` throws `NoSuchElementException`; an `Optional` variable that is itself `null`; `map` vs. `flatMap` nesting (`Optional<Optional<T>>`).

## Part VII — Input and Output

- [ ] [[Java/07 - Input and Output/01 - File I-O|File I/O]] — reading and writing text files
	- **Cover:** `Path` and `Files` (`readAllLines`, `readString`, `lines`, `write`, `writeString`, `newBufferedReader`/`newBufferedWriter`); classic `java.io` (`FileReader`, `BufferedReader`, `PrintWriter`, `FileWriter`); try-with-resources throughout; appending vs. overwriting; character encodings (always name `UTF-8`); `Scanner` on a file; checking and creating files and directories.
	- **Traps:** relative paths resolve against the **working directory**, not the source file's folder; `new FileWriter(f)` truncates the file (append needs `true`); `Files.lines` must be closed; forgetting to `flush`/`close` loses buffered output; `IOException` is checked; the platform-default charset garbles non-ASCII (e.g. Greek) text; `\` vs. `/` in paths.
	- **Note:** the file name uses `I-O` because `/` can't appear in a file name.

## Later — Optional Chapters

Not scheduled yet. Promote into a part (with a numbered folder and a brief like the ones above) when needed:

- Concurrency: threads, `Runnable`, `synchronized`, `volatile`, `ExecutorService`, race conditions
- Testing with JUnit
- Build tools: Maven / Gradle
- Date and time: `java.time` (`LocalDate`, `Duration`, formatting)
- Modules (`module-info.java`)
- Wrapper classes as a group (`parseInt`, `valueOf`, caching, `MIN_VALUE`/`MAX_VALUE`), if the material scattered in [[04 - Type Casting|Type Casting]] § 9 and [[Java/05 - Working with Data and Errors/02 - Generics|Generics]] § 9 turns out not to be enough

## Notes

- Order within each part is the intended reading order; order across parts is intended to be sequential (Part I before Part II, and so on).
- This syllabus will be updated as chapters are added or reordered.

### How to write a chapter (conventions for the Java notes)

- **Language:** English. The Java notes follow their own layout rather than the Greek ΕΠΛ111 model: one note per chapter, with the quick-reference table and the trick questions inside the note instead of a separate cheat sheet or exercises note.
- **Structure**, as in the written chapters (use [[01 - Methods|Methods]] or [[Java/05 - Working with Data and Errors/02 - Generics|Generics]] as the template):
	1. `# <Topic> in Java`, then an intro paragraph (key term in `hl-blue`, what the chapter covers) and a second paragraph linking prerequisites and where related topics live.
	2. `## Contents`: a list of `[[#N. Heading|N. Heading]]` links. **Copy the heading text exactly, including backticks**, or the link won't jump.
	3. Numbered sections `## 1. …` with subsections `### 1.1 …`, separated by `---`.
	4. Callouts: `> [!note] Definitions`, `> [!important] Key rule: …`, `> [!warning] Common mistake: …` / `Trick: …`, `> [!tip]`, collapsed `> [!info]-` for deep "why" explanations, collapsed `> [!example]- Worked example: …`.
	5. Closing sections, in this order: `Common Pitfalls` (bullets), `Quick Reference — Non-Obvious Outcomes` (table: Code | Result | Why), `Practice — Trick Questions` (**Q1.** …, each with a collapsed `> [!success]- Answer`, often a table), `Summary` (bullets), `Related` (Syllabus link first, then `Previous: … · Next: …`, then cross-links with a short reason each).
- **Headings:** avoid `:`, `|`, `#`, and `^` in headings (they break heading links). Put `<`/`>` only inside backticks.
- **Links:** use full vault paths for cross-folder links (`[[Java/05 - Working with Data and Errors/02 - Generics#7.2 What Erasure Forbids|Generics § 7.2]]`). Links to planned chapters in this syllabus already use the final numbered paths, so clicking them creates the note in the right place.
- **Verify every code claim.** JDK 17 is installed (Eclipse Adoptium, `javac`/`java` on the PATH). Before finishing a chapter, compile and run every "compiles / compile error / prints X" claim in a temporary folder. Don't name the test class `T` (it collides with type parameters named `T`). Features newer than Java 17 (e.g. Java 21 pattern `switch`, Java 25 compact source files) can't be checked locally, so mark them with their version.

### Checklist when a chapter is finished

1. Tick its box here, and trim its brief if it is no longer useful.
2. Fix `Previous` / `Next` in the neighbouring chapters' `Related` sections.
3. Deliver everything listed under **Promised by**, then add back-links in those notes.
4. Add short mentions in earlier notes where the topic was used without explanation. Keep them to a sentence or a table row with a link, not a second explanation.
5. Run a link check: every `[[…#heading]]` must match a real heading.

### Renaming and moving notes

- Use Obsidian, never the shell: `obsidian.com vault="Obsidian Vault" move path="Java/…/Old.md" to="Java/…/NN - Old.md"`.
- Obsidian rewrites a link alias that equals the old file name (`[[Syllabus|Syllabus]]` became `[[00 - Syllabus|00 - Syllabus]]`), and it missed some full-path links inside tables. After any rename, grep the `Java/` folder and fix both.
- Links to notes that don't exist yet are **not** updated by Obsidian. Repoint them by hand (or with `sed`).

### Decisions and history

- **2026-09-29:** all notes renamed with `NN - ` prefixes, and this note renamed to `00 - Syllabus`. *Generics* added (it was missing from the syllabus), in Part V after *Exception Handling*, because it needs *Inheritance* and *Abstraction* (subtyping, interfaces). After a gap review, these chapters were also added: *Reading Input*, *Object Methods*, *Enums*, *Nested and Anonymous Classes*, *Comparable and Comparator*, and Parts VI and VII.
- *Collections Framework* moved from `03` to `04` in Part V, to come after *Comparable and Comparator*.
- The `equals`/`hashCode` contract moved out of *Inheritance* into its own chapter, *Object Methods*. [[01 - Classes and Objects|Classes and Objects]] now points there.
- **Known issue (not yet fixed):** the Contents links in [[01 - Conditional Statements|Conditional Statements]] and [[02 - Loops|Loops]], and two links to § 5 inside [[04 - Type Casting|Type Casting]], leave out backticks that their headings have (e.g. `#1. The if Statement` for "1. The `if` Statement"). Check in Obsidian whether they jump, and fix them if not.
