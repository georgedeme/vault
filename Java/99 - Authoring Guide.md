# Java — Authoring Guide

Working notes for writing the Java chapters: what each unwritten chapter must cover, the conventions the written chapters follow, and the decisions made so far. This is the author's reference. The reader-facing chapter list is [[Java/00 - Syllabus|Syllabus]].

Each chapter brief has up to three parts:
- **Cover:** the scope.
- **Traps:** trick questions and edge cases that must be included (see the completeness rule in `CLAUDE.md`).
- **Promised by:** places in already-written notes that say "covered in …" and point to this chapter. The chapter must deliver these, and those notes should get a back-link once it exists.

When a chapter is written, delete its brief here (or trim it to anything still useful), and follow [[#Checklist when a chapter is finished|the checklist]].

## Chapter Briefs

### Part IV — Object-Oriented Programming

#### Polymorphism

[[Java/04 - Object-Oriented Programming/04 - Polymorphism|Polymorphism]]: dynamic dispatch, upcasting/downcasting in practice.

- **Cover:** a supertype reference to a subtype object; dynamic dispatch (runtime choice of the overriding method); overloading (compile time) vs. overriding (runtime) side by side; upcasting and downcasting, `instanceof` and pattern matching for `instanceof` (Java 16+); designing with polymorphism instead of `if`/`instanceof` chains.
- **Traps:** the declared type decides which methods can be *called*, and the runtime type decides which override *runs*; static methods and fields use the declared type (hiding, no dispatch); an overload chosen at compile time plus an override chosen at runtime in the same call; `ClassCastException` on a bad downcast that compiled; generics are invariant (`List<Dog>` is not a `List<Animal>`).
- **Promised by:** [[Java/03 - Program Structure/01 - Methods|Methods]] § 7.2 (overloading chosen by declared type vs. overriding), [[Java/04 - Object-Oriented Programming/01 - Classes and Objects|Classes and Objects]] § 8.4 (static methods through a reference don't dispatch); [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]] § 3.1 (declared type decides what can be called, runtime type what runs), § 8 (field and static-method hiding: link, don't repeat), § 11 (`switch` over a sealed hierarchy without `default`, Java 21). Link to [[Java/01 - Foundations/04 - Type Casting#7. Reference (Object) Casting|Type Casting § 7]] and [[Java/05 - Working with Data and Errors/02 - Generics#5. Generics Are Invariant|Generics § 5]].

#### Abstraction

[[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]]: abstract classes and interfaces, when to use each.

- **Cover:** `abstract` classes and methods; interfaces (implicitly `public abstract` methods, `public static final` constants); `default`, `static`, and `private` interface methods; implementing several interfaces; abstract class vs. interface comparison table; functional interfaces as a preview of Part VI; sealed interfaces.
- **Traps:** an abstract class can have constructors and state, an interface can't have instance fields; a class inheriting the same `default` method from two interfaces must override it (`A.super.m()` to pick one); interface fields are constants even without `static final`; `abstract` + `final`/`private`/`static` is a compile error; a concrete class that misses one abstract method must itself be `abstract`.
- **Promised by:** [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]] § 2.2 (two interfaces with the same `default` method), § 9 (`abstract` + `final`), § 11 (sealed interfaces).

#### Object Methods

[[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]: the `equals` / `hashCode` / `toString` contract that every class inherits from `Object`.

- **Cover:** what `Object` provides; overriding `toString`; the `equals` contract (reflexive, symmetric, transitive, consistent, `x.equals(null) == false`); the `hashCode` contract and why it must agree with `equals`; writing both correctly (`Objects.equals`, `Objects.hash`); `instanceof` vs. `getClass()` in `equals` and the symmetry problem with subclasses; records generate all three; a brief note on `clone` and the deprecated `finalize`.
- **Traps:** `equals(Student other)` *overloads* instead of overriding (collections still use `Object.equals`), which `@Override` would catch; overriding `equals` without `hashCode` makes `HashSet.contains` and `HashMap.get` fail; changing a field used in `hashCode` after inserting into a `HashSet` "loses" the object; `==` vs. `equals` on strings and wrappers (link, don't repeat); `equals` on arrays is identity.
- **Promised by:** [[Java/04 - Object-Oriented Programming/01 - Classes and Objects|Classes and Objects]] § 2.2 and § 10.3 (overriding the inherited `toString`/`equals`/`hashCode`). Needed by *Collections Framework*.

#### Enums

[[Java/04 - Object-Oriented Programming/07 - Enums|Enums]]: type-safe constants, enums with fields and methods, `switch` on enums.

- **Cover:** basic `enum`; `values()`, `valueOf`, `name()`, `ordinal()`, `compareTo`; fields, constructors (implicitly `private`), and methods; constant-specific method bodies; enums implementing interfaces; `switch` on an enum (classic and arrow form); `EnumMap` and `EnumSet`; the enum singleton.
- **Traps:** `valueOf("unknown")` throws `IllegalArgumentException` (and it's case-sensitive); relying on `ordinal()` breaks when constants are reordered; `case RED:` must be unqualified (not `Color.RED`) in a classic `switch`; `==` is safe (and preferred) for enum comparison; enums can't be extended, can't be generic, and can't be created with `new`; a `switch` expression over an enum must be exhaustive.

#### Nested and Anonymous Classes

[[Java/04 - Object-Oriented Programming/08 - Nested and Anonymous Classes|Nested and Anonymous Classes]]: static nested, inner, local, and anonymous classes.

- **Cover:** the four kinds with a comparison table; creating inner-class instances (`outer.new Inner()`); `Outer.this.field`; access to the outer class's private members; local classes; anonymous classes (implementing an interface or extending a class inline, e.g. a `Comparator`); capturing local variables (effectively final); when to use each. End with the bridge to lambdas (anonymous class → lambda).
- **Traps:** an inner class needs an outer instance (can't be created from `static main` without one); a captured local that is modified later is a compile error; `this` inside an anonymous class is the anonymous object, not the outer one; shadowing between inner and outer fields; an inner class keeps a hidden reference to its outer object (memory leaks); static members in inner classes were illegal before Java 16.

### Part V — Working with Data and Errors

#### Exception Handling

[[Java/05 - Working with Data and Errors/01 - Exception Handling|Exception Handling]]: `try` / `catch` / `finally`, checked vs. unchecked exceptions, custom exceptions.

- **Cover:** the `Throwable` hierarchy (`Error`, `Exception`, `RuntimeException`); checked vs. unchecked and the "catch or declare" rule; `throw` vs. `throws`; `try`/`catch`/`finally`; multi-catch; **try-with-resources** and `AutoCloseable`, with suppressed exceptions; custom exceptions; reading a stack trace; good practice (don't swallow exceptions, don't catch `Exception` blindly).
- **Traps:** catch blocks in the wrong order (a superclass before a subclass is an unreachable-code compile error); a `return` in `finally` overrides the `try`'s return and swallows exceptions; an exception thrown in `finally` masks the original one; `finally` runs even after `return` (but not after `System.exit`); catching a checked exception that the `try` can't throw is a compile error; overriding methods can't throw broader checked exceptions; generic classes can't extend `Throwable`, but `<T extends Exception> … throws T` is allowed.
- **Promised by:** [[Java/03 - Program Structure/01 - Methods|Methods]] § 2 (the `throws` clause); [[Java/04 - Object-Oriented Programming/01 - Classes and Objects|Classes and Objects]] § 3.4 (try-with-resources for closing resources); [[Java/05 - Working with Data and Errors/02 - Generics#7.2 What Erasure Forbids|Generics § 7.2]]; [[Java/01 - Foundations/05 - Reading Input|Reading Input]] §§ 5.3–5.4 and 9.1 (uses `try`/`catch` with `InputMismatchException`/`NumberFormatException`, and `throws IOException`, with only a one-line explanation and a forward link).

#### Comparable and Comparator

[[Java/05 - Working with Data and Errors/03 - Comparable and Comparator|Comparable and Comparator]]: natural ordering vs. custom orderings, sorting objects.

- **Cover:** `Comparable<T>` and `compareTo` (natural ordering) vs. `Comparator<T>` (external orderings); the `compareTo` contract (sign, antisymmetry, transitivity) and consistency with `equals`; sorting with `Arrays.sort`, `Collections.sort`, `List.sort`; multi-key sorting; `Comparator.comparing`, `thenComparing`, `reversed`, `nullsFirst` (show them with anonymous classes or a brief lambda preview, since lambdas only come in Part VI, and forward-link); sort stability.
- **Traps:** `return a - b;` in `compareTo` overflows for large or negative values (use `Integer.compare`); a `compareTo` inconsistent with `equals` makes a `TreeSet`/`TreeMap` silently drop "duplicates"; `Comparator<? super T>` and `<T extends Comparable<? super T>>` (link [[Java/05 - Working with Data and Errors/02 - Generics#4.3 Recursive Bounds and `Comparable`|Generics § 4.3]], don't repeat); `reversed()` on a chain applies to the whole chain; sorting a list containing `null` with natural ordering throws `NullPointerException`; the raw `Comparable` mistake (Generics § 2.4).
- **Promised by:** [[Java/05 - Working with Data and Errors/02 - Generics|Generics]] (intro, Next link, and Related).

#### Collections Framework

[[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]]: `List`, `Set`, `Map`, and choosing between implementations.

- **Cover:** the interface hierarchy (`Iterable` → `Collection` → `List`/`Set`/`Queue`; `Map` separately); `ArrayList` vs. `LinkedList`; `HashSet`/`LinkedHashSet`/`TreeSet`; `HashMap`/`LinkedHashMap`/`TreeMap`; `Queue`, `Deque` (`ArrayDeque` as a stack and a queue), `PriorityQueue`; iterating and `Iterator`; useful `Map` methods (`getOrDefault`, `putIfAbsent`, `computeIfAbsent`, `merge`, `entrySet`); the `Collections` utility class; immutable collections; a "which implementation?" table with complexities (link the DSA notes).
- **Traps:** `ConcurrentModificationException` when removing inside a for-each (use `Iterator.remove` or `removeIf`); `List.of`/`Map.of` are unmodifiable and reject `null`; `Arrays.asList` is fixed-size (link [[Java/02 - Control Flow/03 - Arrays#8.4 `asList`|Arrays § 8.4]]); `HashSet`/`HashMap` depend on `equals`/`hashCode` (link *Object Methods*); `TreeSet`/`TreeMap` depend on `compareTo` (link *Comparable and Comparator*); `Map.get` returning `null` is ambiguous (absent key vs. `null` value); `PriorityQueue` iteration order isn't sorted; `Stack`/`Vector` are legacy. The autoboxing traps (`remove(int)` vs. `remove(Object)`, wrong key types) are in [[Java/05 - Working with Data and Errors/02 - Generics#9. Generics and Autoboxing — Traps|Generics § 9]]: link, don't repeat.
- **Promised by:** [[Java/02 - Control Flow/03 - Arrays|Arrays]] (`ArrayList` as a resizable alternative), [[Java/05 - Working with Data and Errors/02 - Generics|Generics]] (intro and Related).

### Part VI — Functional Programming

#### Lambdas and Functional Interfaces

[[Java/06 - Functional Programming/01 - Lambdas and Functional Interfaces|Lambdas and Functional Interfaces]]: lambda syntax, `java.util.function`, method references.

- **Cover:** from anonymous class to lambda; lambda syntax forms (parameters, block vs. expression body); functional interfaces and `@FunctionalInterface`; target typing; the core `java.util.function` interfaces (`Function`, `BiFunction`, `Predicate`, `Supplier`, `Consumer`, `UnaryOperator`, `BinaryOperator`) and their primitive specializations; the four kinds of method references; composing (`andThen`, `compose`, `Predicate.and/negate`); `Comparator.comparing` chains in full.
- **Traps:** captured locals must be effectively final (and why a one-element array or `AtomicInteger` "works around" it); `this` in a lambda is the enclosing object, unlike in an anonymous class; a lambda can't shadow a local variable of the enclosing method; a lambda can't throw a checked exception its functional interface doesn't declare; overloaded methods taking different functional interfaces can make a lambda call ambiguous; `var` is not allowed for a lambda variable (`var f = x -> x;` has no target type).

#### Streams

[[Java/06 - Functional Programming/02 - Streams|Streams]]: the Stream API, pipelines, intermediate and terminal operations, collectors.

- **Cover:** creating streams (collections, `Arrays.stream`, `Stream.of`, `IntStream.range`, `Stream.iterate`/`generate`); intermediate operations (`filter`, `map`, `flatMap`, `distinct`, `sorted`, `limit`, `skip`, `peek`); terminal operations (`forEach`, `collect`, `reduce`, `count`, `min`/`max`, `anyMatch`/`allMatch`/`noneMatch`, `findFirst`); `Collectors` (`toList`, `toSet`, `toMap`, `joining`, `groupingBy`, `partitioningBy`, `counting`); primitive streams (`IntStream`, `mapToInt`, `sum`, `average`, `boxed`); when a loop is clearer.
- **Traps:** streams are lazy (no terminal operation → nothing runs, including `peek`); a stream can be consumed only once (`IllegalStateException`); `Collectors.toMap` throws on duplicate keys unless given a merge function; `Stream.toList()` (Java 16+) is unmodifiable while `Collectors.toList()` makes no guarantee; `allMatch` on an empty stream is `true`; `IntStream.average()` returns an `OptionalDouble`; short-circuiting with infinite streams (`limit` placement); side effects in `map`/`forEach` and parallel streams.

#### Optional

[[Java/06 - Functional Programming/03 - Optional|Optional]]: representing "maybe a value" without `null`.

- **Cover:** why `Optional` exists; creating (`of`, `ofNullable`, `empty`); consuming (`isPresent`/`isEmpty`, `ifPresent`, `ifPresentOrElse`, `orElse`, `orElseGet`, `orElseThrow`); transforming (`map`, `flatMap`, `filter`); where it is and isn't appropriate (return types yes; fields, parameters, collections no); `OptionalInt` and friends.
- **Traps:** `Optional.of(null)` throws `NullPointerException`; `orElse(expensive())` **always** evaluates its argument, `orElseGet` doesn't; `get()` on an empty `Optional` throws `NoSuchElementException`; an `Optional` variable that is itself `null`; `map` vs. `flatMap` nesting (`Optional<Optional<T>>`).

### Part VII — Input and Output

#### File I/O

[[Java/07 - Input and Output/01 - File I-O|File I/O]]: reading and writing text files. The file name uses `I-O` because `/` can't appear in a file name.

- **Cover:** `Path` and `Files` (`readAllLines`, `readString`, `lines`, `write`, `writeString`, `newBufferedReader`/`newBufferedWriter`); classic `java.io` (`FileReader`, `BufferedReader`, `PrintWriter`, `FileWriter`); try-with-resources throughout; appending vs. overwriting; character encodings (always name `UTF-8`); `Scanner` on a file; checking and creating files and directories.
- **Traps:** relative paths resolve against the **working directory**, not the source file's folder; `new FileWriter(f)` truncates the file (append needs `true`); `Files.lines` must be closed; forgetting to `flush`/`close` loses buffered output; `IOException` is checked; the platform-default charset garbles non-ASCII (e.g. Greek) text; `\` vs. `/` in paths.
- **Promised by:** [[Java/01 - Foundations/05 - Reading Input|Reading Input]] § 9.4 (`Scanner`/`BufferedReader` on a file; Greek console input and charsets) and § 10.1 (Scanners on files *should* be closed). Keyboard-reading traps (`nextInt`/`nextLine`, locale, `split` empty tokens) are already there: link, don't repeat.

### Later — Optional Chapters

Scope notes for the unscheduled chapters in the Syllabus. When one is promoted, give it a numbered folder/note and a full brief here.

- **Concurrency:** threads, `Runnable`, `synchronized`, `volatile`, `ExecutorService`, race conditions.
- **Testing with JUnit.**
- **Build tools:** Maven / Gradle.
- **Date and time:** `java.time` (`LocalDate`, `Duration`, formatting).
- **Modules:** `module-info.java`.
- **Wrapper classes:** `parseInt`, `valueOf`, caching, `MIN_VALUE`/`MAX_VALUE`. Only needed if the material scattered in [[Java/01 - Foundations/04 - Type Casting|Type Casting]] § 9 and [[Java/05 - Working with Data and Errors/02 - Generics|Generics]] § 9 turns out not to be enough.

---

## How to Write a Chapter

- **Language:** English. The Java notes follow their own layout rather than the Greek ΕΠΛ111 model: one note per chapter, with the quick-reference table and the trick questions inside the note instead of a separate cheat sheet or exercises note.
- **Structure**, as in the written chapters (use [[Java/03 - Program Structure/01 - Methods|Methods]] or [[Java/05 - Working with Data and Errors/02 - Generics|Generics]] as the template):
	1. `# <Topic> in Java`, then an intro paragraph (key term in `hl-blue`, what the chapter covers) and a second paragraph linking prerequisites and where related topics live.
	2. `## Contents`: a list of `[[#N. Heading|N. Heading]]` links. **Copy the heading text exactly, including backticks**, or the link won't jump.
	3. Numbered sections `## 1. …` with subsections `### 1.1 …`, separated by `---`.
	4. Callouts: `> [!note] Definitions`, `> [!important] Key rule: …`, `> [!warning] Common mistake: …` / `Trick: …`, `> [!tip]`, collapsed `> [!info]-` for deep "why" explanations, collapsed `> [!example]- Worked example: …`.
	5. Closing sections, in this order: `Common Pitfalls` (bullets), `Quick Reference — Non-Obvious Outcomes` (table: Code | Result | Why), `Practice — Trick Questions` (**Q1.** …, each with a collapsed `> [!success]- Answer`, often a table), `Summary` (bullets), `Related` (Syllabus link first, then `Previous: … · Next: …`, then cross-links with a short reason each).
- **Headings:** avoid `:`, `|`, `#`, and `^` in headings (they break heading links). Put `<`/`>` only inside backticks.
- **Links:** use full vault paths for cross-folder links (`[[Java/05 - Working with Data and Errors/02 - Generics#7.2 What Erasure Forbids|Generics § 7.2]]`). Links to planned chapters in the Syllabus and in this guide already use the final numbered paths, so clicking them creates the note in the right place.
- **Diagrams:** Excalidraw drawings live in `Java/99 - Drawings/`, named `<Chapter> - <Topic>` (e.g. `Arrays - Shallow vs Deep Copy`), and are embedded right after the passage they illustrate with `![[<name>.excalidraw|800]]`. They add to the text and never replace it, and their captions shouldn't name fill colours: the drawings are exported for dark mode, where orange and yellow fills look brown. Good candidates are memory pictures (stack/heap/references), step-by-step state changes, flowcharts, and "looks the same but isn't" comparisons.
- **Verify every code claim.** JDK 17 is installed (Eclipse Adoptium, `javac`/`java` on the PATH). Before finishing a chapter, compile and run every "compiles / compile error / prints X" claim in a temporary folder. Don't name the test class `T` (it collides with type parameters named `T`). Features newer than Java 17 (e.g. Java 21 pattern `switch`, Java 25 compact source files) can't be checked locally, so mark them with their version.

## Checklist when a chapter is finished

1. Tick its box in the [[Java/00 - Syllabus|Syllabus]], and delete or trim its brief here.
2. Fix `Previous` / `Next` in the neighbouring chapters' `Related` sections.
3. Deliver everything listed under **Promised by**, then add back-links in those notes.
4. Add short mentions in earlier notes where the topic was used without explanation. Keep them to a sentence or a table row with a link, not a second explanation.
5. Run a link check: every `[[…#heading]]` must match a real heading.

## Renaming and Moving Notes

- Use Obsidian, never the shell: `obsidian.com vault="Obsidian Vault" move path="Java/…/Old.md" to="Java/…/NN - Old.md"`.
- Obsidian rewrites a link alias that equals the old file name (`[[Syllabus|Syllabus]]` became `[[00 - Syllabus|00 - Syllabus]]`), and it missed some full-path links inside tables. After any rename, grep the `Java/` folder and fix both.
- Links to notes that don't exist yet are **not** updated by Obsidian. Repoint them by hand (or with `sed`), in the Syllabus, in this guide, and in the chapters.

## Decisions and History

- **2026-09-29:** all notes renamed with `NN - ` prefixes, and the syllabus renamed to `00 - Syllabus`. *Generics* added (it was missing from the syllabus), in Part V after *Exception Handling*, because it needs *Inheritance* and *Abstraction* (subtyping, interfaces). After a gap review, these chapters were also added: *Reading Input*, *Object Methods*, *Enums*, *Nested and Anonymous Classes*, *Comparable and Comparator*, and Parts VI and VII.
- *Collections Framework* moved from `03` to `04` in Part V, to come after *Comparable and Comparator*.
- The `equals`/`hashCode` contract moved out of *Inheritance* into its own chapter, *Object Methods*. [[Java/04 - Object-Oriented Programming/01 - Classes and Objects|Classes and Objects]] now points there.
- The Syllabus is kept short (titles and one-line descriptions only) at the user's request. All authoring detail lives in this guide.
- **2026-09-29:** *Reading Input* written. It also covers `BufferedReader` (§ 9), `StringTokenizer`, `System.console()`, and a measured Scanner-vs-BufferedReader timing. It uses `try`/`catch` before *Exception Handling* with a one-line explanation, because a validation chapter without it would be incomplete. It recommends line-based reading (`nextLine` + `parseX`) as the default validation pattern. [[Java/01 - Foundations/04 - Type Casting|Type Casting]] and [[Java/02 - Control Flow/01 - Conditional Statements|Conditional Statements]] have no `Related` section, so their Previous/Next links couldn't be updated. Add them if those notes get a `Related` section.
- **2026-10-01:** 25 Excalidraw diagrams added to the written chapters (2–3 per chapter, 1 for *Reading Input* and *Loops*), stored in `Java/99 - Drawings/`. The only change to the chapter text is the embed lines. New chapters should get diagrams the same way (see *How to Write a Chapter*).
- **2026-10-01:** *Encapsulation* written, with two drawings (*Access Levels*, *Leaking Mutable State*). Besides the brief it covers a short packages recap (§ 2), `protected` constructors and the other-package restriction, a public member of a package-private class, `Collections.unmodifiableList` (view) vs. `List.copyOf` (snapshot), `public static final` arrays, private constructors, and the record trap that generated `toString`/`equals` read fields, not overridden accessors. Drawings are generated with ExcalidrawAutomate scripts in `%TEMP%/exdraw` (`lib.js`, `run.js`, `go.sh`; run with `FOLDER="Java/99 - Drawings" bash go.sh 1 <script>`), a temporary folder that may be gone later.
- **2026-10-01:** *Inheritance* written, with two drawings (*Constructor Chain*, *Fields Hide, Methods Override*). Beyond the brief it covers: calls inside `super.m()` still dispatch (§ 3.1), `SC.x` initializing only the declaring superclass (§ 6), constant `final` fields being visible during the super constructor (§ 7), package-private methods not overridden across packages (§ 8.4), and the fragile base class problem with the `CountingSet extends HashSet` example and composition (§ 12). Dynamic dispatch is only introduced; the full treatment stays in *Polymorphism*.
- **Known issue (not yet fixed):** the Contents links in [[Java/02 - Control Flow/01 - Conditional Statements|Conditional Statements]] and [[Java/02 - Control Flow/02 - Loops|Loops]], and two links to § 5 inside [[Java/01 - Foundations/04 - Type Casting|Type Casting]], leave out backticks that their headings have (e.g. `#1. The if Statement` for "1. The `if` Statement"). Check in Obsidian whether they jump, and fix them if not.
