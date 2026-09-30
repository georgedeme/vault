# Encapsulation in Java

<span class="hl-blue">Encapsulation</span> means keeping an object's state behind its methods: fields are hidden, and the only way to read or change them is through code the class controls. That lets the class guarantee its own rules (a balance never negative, a range with `lo ≤ hi`), and change its internals later without breaking callers. This chapter covers the four access levels and exactly who each one lets in, access being per class rather than per object, getters and setters with validation, how private state leaks through mutable objects and how defensive copies stop it, immutable classes, and **records**.

It builds on [[Java/04 - Object-Oriented Programming/01 - Classes and Objects|Classes and Objects]] (fields, constructors, `final` fields, `static`). Packages are introduced in [[01 - Introduction to Java#5.4 Packages and the Classpath|Introduction to Java § 5.4]]. `protected` is explained here for access, and again from the subclass's side in [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]]. Overriding the `equals`/`hashCode`/`toString` that records generate is covered in [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]].

## Contents

- [[#1. Encapsulation — The Idea|1. Encapsulation — The Idea]]
- [[#2. Packages in One Minute|2. Packages in One Minute]]
- [[#3. The Four Access Levels|3. The Four Access Levels]]
- [[#4. Access Is per Class, Not per Object|4. Access Is per Class, Not per Object]]
- [[#5. Getters and Setters|5. Getters and Setters]]
- [[#6. Leaking Internal State|6. Leaking Internal State]]
- [[#7. Immutable Classes|7. Immutable Classes]]
- [[#8. Records (Java 16+)|8. Records (Java 16+)]]
- [[#9. Private Constructors and Helper Methods|9. Private Constructors and Helper Methods]]
- [[#10. Common Pitfalls|10. Common Pitfalls]]
- [[#11. Quick Reference — Non-Obvious Outcomes|11. Quick Reference — Non-Obvious Outcomes]]
- [[#12. Practice — Trick Questions|12. Practice — Trick Questions]]
- [[#13. Summary|13. Summary]]

---

## 1. Encapsulation — The Idea

Here is a class with no protection at all:

```java
class Account {
    double balance;                 // anyone can write anything here
}

Account a = new Account();
a.balance = -1_000_000;             // compiles; the object is now in a state that makes no sense
```

Every piece of code in the package can put an `Account` into an invalid state, and if the representation ever changes (say, to `long cents`), every one of those places breaks. The encapsulated version:

```java
public class Account {
    private long cents;                              // hidden: only Account's code can touch it

    public void deposit(long amount) {
        if (amount <= 0) throw new IllegalArgumentException("amount must be positive");
        cents += amount;
    }

    public boolean withdraw(long amount) {
        if (amount <= 0 || amount > cents) return false;
        cents -= amount;
        return true;
    }

    public long getBalance() { return cents; }
}
```

> [!note] Definitions
> - An **invariant** is a rule about an object's state that must always hold between method calls, e.g. "`cents` is never negative".
> - **Encapsulation**: make the fields inaccessible from outside (`private`), and offer methods that change the state only in ways that keep the invariants true.
> - The **public interface** (or API) of a class is what other code can use: its public (and, for subclasses, protected) members. Everything else is **implementation detail** and can change freely.

> [!important] Key rule: why hide state
> 1. **Invariants**: if only the class's own methods can change a field, only those methods need checking.
> 2. **Freedom to change**: callers depend on method signatures, not on field names or types.
> 3. **Fewer surprises**: a hidden field can't be changed behind the object's back (but see [[#6. Leaking Internal State|§ 6]] for the ways it still can).

---

## 2. Packages in One Minute

Access levels are defined in terms of **classes** and **packages**, so the package rules matter here.

- A **package** is a named group of classes, declared on the first line of the file: `package bank.core;`. The folders must match (`bank/core/Account.java`).
- A file with no `package` line is in the **unnamed (default) package**. All such classes in the same directory count as one package, which is why package-private access "just works" in small exercises.
- Classes in another package are used with their full name (`java.util.ArrayList`) or with an `import`. `java.lang` is imported automatically.
- Packages are **not** nested for access purposes: `bank` and `bank.core` are two completely unrelated packages, whatever their names suggest.

Compiling and running packaged classes: [[01 - Introduction to Java#5.4 Packages and the Classpath|Introduction to Java § 5.4]].

---

## 3. The Four Access Levels

### 3.1 The Access Table

<span class="hl-yellow">Exam favourite.</span>

| Modifier | Same class | Same package | Subclass in another package | Any other class |
|---|---|---|---|---|
| `private` | ✅ | ❌ | ❌ | ❌ |
| *(none)* = package-private | ✅ | ✅ | ❌ | ❌ |
| `protected` | ✅ | ✅ | ✅ (with a restriction, [[#3.5 `protected`|§ 3.5]]) | ❌ |
| `public` | ✅ | ✅ | ✅ | ✅ |

![[Encapsulation - Access Levels.excalidraw|800]]

Each row allows everything the row above it allows, plus one more region. Two things follow that people often get backwards:

- **Package-private is more restrictive than `protected`**, not less. A subclass in another package can't see package-private members, but it can see `protected` ones.
- **`protected` includes the whole package.** Any class in the same package, subclass or not, can use a `protected` member.

### 3.2 Where Each Modifier Is Allowed

| Declaration | Allowed access modifiers |
|---|---|
| top-level class, interface, enum, record | `public` or none. `private class X {}` → *modifier private not allowed here* (same for `protected`) |
| field, method, constructor, nested class | all four |
| local variable, parameter | **none**. `private int n = 1;` inside a method → *illegal start of expression* |
| interface member | implicitly `public` (details in [[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]]) |

- A `.java` file can hold at most one `public` top-level class, named after the file ([[01 - Introduction to Java#6. Files, Classes, and Names|Introduction to Java § 6]]).
- The **default constructor** the compiler generates has the **same access as its class** ([[Java/04 - Object-Oriented Programming/01 - Classes and Objects#6.2 The Default Constructor|Classes and Objects § 6.2]]).
- Only one access modifier per declaration: `public private int x;` is a compile error.

### 3.3 `private`

Visible only **inside the top-level class that declares it**, including all its nested classes (the outer class can read a nested class's `private` members and vice versa). Use it for all fields by default, and for helper methods that aren't part of the API.

`private` members are **not inherited**: a subclass object still contains the superclass's private fields, but the subclass's code can't name them.

```java
class P { private int s; }
class X extends P {
    int g() { return s; }   // compile error: s has private access in P
}
```

### 3.4 Package-Private (No Modifier)

Written by leaving the modifier out. Visible to every class in the **same package** and nowhere else. There is no keyword for it: `package int x;` or `default int x;` don't compile.

It's useful for classes and methods that cooperate inside one package but aren't meant for outside use, and for tests that live in the same package. Most earlier chapters used it only to keep the examples short.

> [!warning] Common mistake: "no modifier" is not `public`
> Leaving out the modifier looks harmless in single-folder exercises, because every class is in the same unnamed package. As soon as the code is split into packages, those members disappear for other packages.

### 3.5 `protected`

Visible to the whole package **plus** subclasses in other packages, with one restriction on the subclass side:

> [!important] Key rule: `protected` from a subclass in another package
> The subclass can use an inherited `protected` **instance** member only on objects of **its own type** (or a subtype of it): through `this`, `super`, or a reference of the subclass's type. It can **not** use it through a reference of the superclass type. It also can't call a `protected` constructor with `new`, only via `super(…)`.

```java
package a;
public class Parent {
    protected int p = 1;
    protected Parent() { }
    protected void hello() { }
}
```

```java
package b;
import a.Parent;

public class Child extends Parent {
    void test(Parent other, Child sibling) {
        System.out.println(p);         // OK: inherited, same as this.p
        System.out.println(sibling.p); // OK: reference of type Child
        System.out.println(other.p);   // compile error: p has protected access in Parent
        other.hello();                 // compile error: hello() has protected access in Parent
        new Parent();                  // compile error: Parent() has protected access in Parent
    }
}
```

> [!info]- Why the restriction exists
> `protected` means "for the implementation of subclasses". `Child` is responsible for `Child` objects, so it may reach into the `Parent` part of **its own kind** of object. A `Parent` reference could point to a completely unrelated subclass (`OtherChild`, written by someone else), and `Child` has no business changing that object's internals. The rule applies to instance members only: a `protected static` member can be used from a subclass in another package without that restriction, since no object is involved.

The same code with `Child` moved into package `a` compiles completely, because then the package rule applies.

### 3.6 `public`

Visible everywhere the class itself is visible. Use it for the API: the constructors and methods other code is meant to call, and constants (`public static final`).

> [!tip] Start as private as possible
> Make every field `private`. Make methods `private` unless another class needs them, then package-private, and `public` only for the real API. Widening access later is easy and breaks no one; narrowing it breaks every caller that relied on it.

### 3.7 A Member Is Only as Visible as Its Class

A `public` member of a package-private class can't be reached from another package, because the class name itself can't be used there:

```java
package a;
class Hidden {                    // package-private class
    public int v = 7;             // public member, but...
}
```

```java
package b;
a.Hidden h = null;                // compile error: Hidden is not public in a; cannot be accessed from outside package
```

The same applies to nested classes: a `public` method of a `private` nested class is effectively private to the outer class.

---

## 4. Access Is per Class, Not per Object

<span class="hl-yellow">A classic trick question.</span> `private` means "only code **written inside this class** may use it", not "only **this object** may use it". A method can read and write the private fields of **any** object of the same class:

```java
class Account {
    private double balance;
    Account(double b) { balance = b; }

    boolean richerThan(Account other) {
        return balance > other.balance;      // OK: other's private field, same class
    }

    void steal(Account other) {
        balance += other.balance;            // OK: compiles and runs
        other.balance = 0;
    }
}

Account a = new Account(10), b = new Account(5);
a.steal(b);                                  // a: 15.0, b: 0.0
```

This is what makes `equals`, `compareTo`, and copy constructors possible without getters (`Point(Point other) { this.x = other.x; … }`). The protection is against **other classes**, which are written by other people. The class's own code is trusted to keep the invariants of all its objects.

> [!warning] Trick: access is checked at compile time, using the declared type
> The compiler decides access from the **class where the code is written** and the **declared type** of the reference. Nothing is checked per object at runtime. (Reflection with `setAccessible(true)` can bypass access checks, within limits set by the module system. Normal code never needs it.)

---

## 5. Getters and Setters

A <span class="hl-blue">getter</span> (accessor) returns a field's value, and a <span class="hl-blue">setter</span> (mutator) changes it. The field itself stays `private`.

### 5.1 Naming Conventions

```java
public class Student {
    private String name;
    private int year;
    private boolean active;

    public String getName()          { return name; }
    public void   setName(String n)  { this.name = n; }

    public int  getYear()            { return year; }
    public void setYear(int year)    { this.year = year; }    // parameter shadows the field → this. is required

    public boolean isActive()        { return active; }       // boolean: isX, not getX
    public void    setActive(boolean active) { this.active = active; }
}
```

| Field | Getter | Setter |
|---|---|---|
| `String name` | `getName()` | `setName(String)` |
| `boolean active` | `isActive()` (`getActive()` also works but is unusual) | `setActive(boolean)` |
| record component `name` | `name()` ([[#8. Records (Java 16+)|§ 8]]) | none |

These are the **JavaBeans** conventions. They matter because many libraries and frameworks find properties by these exact names. The setter parameter usually has the same name as the field, so the setter needs `this.year = year;` (`year = year;` silently does nothing, [[Java/04 - Object-Oriented Programming/01 - Classes and Objects#7.1 Use 1 — Reaching a Shadowed Field|Classes and Objects § 7.1]]).

### 5.2 Validation in Setters (and Constructors)

A setter is the place to enforce invariants:

```java
public class Temperature {
    private double celsius;

    public Temperature(double celsius) {
        setCelsius(celsius);                   // reuse the check, don't bypass it
    }

    public void setCelsius(double celsius) {
        if (celsius < -273.15) {
            throw new IllegalArgumentException("below absolute zero: " + celsius);
        }
        this.celsius = celsius;
    }

    public double getCelsius()    { return celsius; }
    public double getFahrenheit() { return celsius * 9 / 5 + 32; }   // derived: no field behind it
}
```

> [!warning] Common mistake: the constructor bypasses the setter's check
> ```java
> Temperature(double c) { this.celsius = c; }   // no validation here...
> new Temperature(-500).getCelsius()            // -500.0: the invariant is broken from the start
> ```
> Every way into the field must validate: the constructors as well as the setters. Either call a shared validation method or put the check in both.

> [!info]- Calling an overridable setter from a constructor
> The `Temperature` constructor above calls the `public` method `setCelsius`. If a subclass overrides `setCelsius`, the constructor runs the **subclass's** version before the subclass's own fields are initialized. To be safe, make such a class `final`, make the setter `final`, or call a `private` validation helper instead. The details are in [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]].

`getFahrenheit()` shows a second benefit: a getter need not correspond to a field. Callers can't tell stored values from computed ones, so the class can switch between the two later.

### 5.3 Not Every Field Needs a Getter or Setter

Generating a public getter and setter for every private field is **not** encapsulation: it's a public field with more typing. Instead:

- **No setter** for values that shouldn't change after construction (an ID, a creation date). Make the field `final`.
- **No getter** for purely internal state (a cache, a counter used by the algorithm).
- **Behavior instead of setters**: `account.deposit(50)` rather than `account.setBalance(account.getBalance() + 50)`. The method can check the rule, and the caller can't get it wrong. This idea is often summed up as "tell, don't ask".

---

## 6. Leaking Internal State

<span class="hl-yellow">The part of encapsulation most often missed.</span> `private` protects the **field** (the reference). If that field refers to a **mutable object** (an array, a `List`, a `StringBuilder`, a `Date`), anyone who gets a reference to the same object can change it, and `private` does nothing about that.

### 6.1 Returning a Mutable Field

```java
class Team {
    private final List<String> members = new ArrayList<>();
    private final int[] scores = {1, 2, 3};

    List<String> getMembers() { return members; }    // hands out the real list
    int[] getScores()         { return scores; }     // hands out the real array
}

Team t = new Team();
t.getMembers().add("Mallory");        // adds to the Team's private list
t.getScores()[0] = 99;                // changes the Team's private array
// members is now [Mallory], scores[0] is 99
```

### 6.2 Storing the Caller's Object

The same leak happens in the other direction, when the constructor or a setter keeps the object it was given:

```java
class Team {
    private final int[] scores;
    Team(int[] scores) { this.scores = scores; }      // keeps the caller's array
}

int[] s = {1, 2, 3};
Team t = new Team(s);
s[0] = 99;                                            // changes t's "private" array
```

![[Encapsulation - Leaking Mutable State.excalidraw|800]]

### 6.3 Defensive Copies and Unmodifiable Views

The fix is a <span class="hl-blue">defensive copy</span>: copy mutable objects on the way **in** and on the way **out**.

```java
class Team {
    private final int[] scores;
    private final List<String> members;

    Team(int[] scores, List<String> members) {
        this.scores  = scores.clone();              // copy IN
        this.members = new ArrayList<>(members);    // copy IN
        if (this.scores.length == 0) throw new IllegalArgumentException("no scores");   // validate the COPY
    }

    int[] getScores()         { return scores.clone(); }                   // copy OUT
    List<String> getMembers() { return Collections.unmodifiableList(members); }   // read-only view OUT
}
```

> [!important] Key rule: copy first, then validate the copy
> If the constructor checks the caller's array and **then** copies it, another thread (or a callback) could change the array between the check and the copy. Checking the copy closes that gap. It's also the reason to copy with `clone()`/`new ArrayList<>(…)` rather than trusting a subclass's own copy method.

Choosing how to hand out a collection:

| Code | Caller can modify it? | Sees later changes made by the class? | Cost |
|---|---|---|---|
| `return members;` | ✅ (the leak) | ✅ | none |
| `return new ArrayList<>(members);` | ✅, but only its own copy | ❌ | copies every call |
| `return Collections.unmodifiableList(members);` | ❌ (`UnsupportedOperationException`) | ✅ (it's a **view**) | none |
| `return List.copyOf(members);` (Java 10+) | ❌ (`UnsupportedOperationException`) | ❌ (a snapshot) | copies (skipped if already unmodifiable); **rejects `null` elements** with `NullPointerException` |

> [!warning] Trick: an unmodifiable view is not a frozen copy
> ```java
> List<String> base = new ArrayList<>(List.of("a"));
> List<String> view = Collections.unmodifiableList(base);
> List<String> copy = List.copyOf(base);
> base.add("b");
> System.out.println(view + " " + copy);   // [a, b] [a]
> ```
> The view blocks changes **through the view**, but it shows every change made to the underlying list. Wrapping a list the class keeps changing is fine for a getter. Wrapping a list the **caller** still holds (in a constructor) is not: copy it.

> [!warning] Common mistake: a shallow copy of a 2D array or of a list of mutable objects
> `grid.clone()` copies the row **references**, so the rows are still shared ([[03 - Arrays#7.1 Shallow vs. Deep Copy|Arrays § 7.1]]). A copied `List<StringBuilder>` still shares the `StringBuilder`s. A defensive copy has to go as deep as the mutability does: clone each row, or store immutable elements (`String`, records of immutable values).

Immutable objects need no defensive copies at all: a `String`, an `Integer`, or a `LocalDate` can be shared freely. That is one of the main reasons to prefer them ([[#7. Immutable Classes|§ 7]]).

### 6.4 `public static final` Arrays

```java
class Days {
    public static final String[] NAMES = {"Mon", "Tue"};
}

Days.NAMES[0] = "Hacked";      // compiles and runs: final fixes the reference, not the elements
```

`public static final` is the usual way to publish a constant, but for an array it publishes a **mutable global**. Expose an unmodifiable list instead (`public static final List<String> NAMES = List.of("Mon", "Tue");`), or keep the array `private` and return `NAMES.clone()` from a method.

---

## 7. Immutable Classes

An <span class="hl-blue">immutable</span> object can't change after construction: every field has the same value for the object's whole life. `String`, the wrappers (`Integer`, `Double`, …), `BigDecimal`, and the `java.time` classes (`LocalDate`) are all immutable.

Why bother:
- **No defensive copies needed**: sharing an immutable object is always safe.
- **Invariants are checked once**, in the constructor, and can never be broken later.
- **Safe as `HashMap` keys and `HashSet` elements**: their hash code can't change after insertion (see [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]).
- **Thread-safe** without any locking.

### 7.1 The Recipe

```java
public final class Period {                              // (1) final class
    private final LocalDate start;                       // (2) private final fields
    private final LocalDate end;                         //     (LocalDate is itself immutable)
    private final List<String> tags;

    public Period(LocalDate start, LocalDate end, List<String> tags) {
        if (start.isAfter(end)) throw new IllegalArgumentException("start after end");
        this.start = start;
        this.end = end;
        this.tags = List.copyOf(tags);                   // (4) defensive copy IN (and unmodifiable)
    }

    public LocalDate getStart()  { return start; }       // safe: immutable value
    public LocalDate getEnd()    { return end; }
    public List<String> getTags() { return tags; }       // safe: already unmodifiable

    public Period withEnd(LocalDate newEnd) {            // (5) "change" = return a new object
        return new Period(start, newEnd, tags);
    }
    // (3) no setters
}
```

> [!important] Key rule: the five steps
> 1. Make the class **`final`** (or make all constructors `private` and provide static factories), so no subclass can add mutable state or override methods ([[#7.3 Why the Class Should Be `final`|§ 7.3]]).
> 2. Make all fields **`private final`**.
> 3. Provide **no setters** or other methods that change fields.
> 4. **Defensive copies** of mutable components, both in (constructor) and out (getters), unless the component is itself immutable or unmodifiable.
> 5. Don't let **`this` escape** from the constructor (don't register it with other objects or pass it to overridable methods), since other code could then see the object half-built.

> [!warning] Trick: `final` fields don't make a class immutable
> ```java
> final class Holder {
>     private final StringBuilder sb = new StringBuilder("x");
>     StringBuilder get() { return sb; }
> }
> new Holder().get().append("y");       // the "immutable" Holder now holds "xy"
> ```
> `final` stops the field from being **reassigned**. It says nothing about the object the field refers to ([[02 - Variables and Data Types#7.2 `final` Doesn't Mean Immutable|Variables and Data Types § 7.2]]). An immutable class needs `final` fields **and** immutable (or never-exposed) contents.

### 7.2 "Changing" an Immutable Object

Methods that look like they modify an immutable object return a **new** object and leave the original alone. Ignoring the return value is the usual bug:

```java
Money m = new Money(100);
m.plus(new Money(50));           // result thrown away
System.out.println(m);           // 100c
m = m.plus(new Money(50));       // reassign the variable to the new object
System.out.println(m);           // 150c
```

It's exactly the same mistake as `s.toUpperCase();` on a `String` ([[02 - Strings#1. The String Class and Immutability|Strings § 1]]). Such methods are often named `withX`, `plus`, or `minus` to signal that they return a new object.

### 7.3 Why the Class Should Be `final`

If an immutable-looking class can be extended, a subclass can break the guarantee:

```java
class Point {                                   // not final
    private final int x;
    Point(int x) { this.x = x; }
    int getX() { return x; }
}

class SneakyPoint extends Point {
    int fakeX;                                  // mutable
    SneakyPoint(int x) { super(x); }
    @Override int getX() { return fakeX; }      // lies about the "immutable" state
}
```

Code that receives a `Point` can't know it's really a `SneakyPoint`. `final` on the class (or only `private` constructors) rules this out. `String` and `Integer` are `final` for this reason.

---

## 8. Records (Java 16+)

A <span class="hl-blue">record</span> is a compact way to declare a class whose purpose is to carry a fixed set of values:

```java
record Point(int x, int y) { }
```

### 8.1 What a Record Declaration Generates

From the header `record Point(int x, int y)`, the compiler generates:

| Generated | For `Point(int x, int y)` |
|---|---|
| a `private final` field per component | `private final int x;` `private final int y;` |
| the **canonical constructor** (all components, in order) | `Point(int x, int y)` |
| a **public accessor** per component, named like the component | `x()` and `y()`, **not** `getX()` |
| `equals` | `true` if all components are equal (`==` for primitives, `equals` for references) |
| `hashCode` | combines all components |
| `toString` | `Point[x=1, y=2]` |

The record class is implicitly **`final`** and implicitly extends `java.lang.Record`.

```java
Point p = new Point(1, 2);
System.out.println(p);                            // Point[x=1, y=2]
System.out.println(p.x());                        // 1
System.out.println(p.equals(new Point(1, 2)));    // true : by value, unlike ordinary classes
System.out.println(p instanceof Record);          // true
```

A `boolean` component `active` gets the accessor `active()`, not `isActive()`.

### 8.2 Compact Constructors — Validation and Normalization

To validate or adjust the arguments, write a <span class="hl-blue">compact constructor</span>: the record name with **no parameter list**. Its parameters are implicitly the components, and the fields are assigned automatically **after** its body runs:

```java
record Range(int lo, int hi) {
    Range {                                      // compact canonical constructor
        if (lo > hi) {                           // normalize: swap instead of failing
            int t = lo; lo = hi; hi = t;         // reassigns the PARAMETERS
        }
    }                                            // here: this.lo = lo; this.hi = hi; (implicit)
}

System.out.println(new Range(5, 1));             // Range[lo=1, hi=5]
```

```java
record Student(String name, int year) {
    Student {
        Objects.requireNonNull(name, "name");
        if (year < 1) throw new IllegalArgumentException("year must be ≥ 1");
    }
}
```

> [!warning] Trick: no `this.x = …` in a compact constructor
> ```java
> record X(int a) {
>     X { this.a = a; }        // compile error: cannot assign a value to final variable a
> }
> ```
> The fields are assigned by the compiler at the end. Inside the body you change the **parameter** (`a = …`), and that value is what gets stored.

> [!info]- The long form: an explicit canonical constructor
> Instead of the compact form you can write the canonical constructor in full, as in an ordinary class:
> ```java
> record Range(int lo, int hi) {
>     Range(int lo, int hi) {
>         if (lo > hi) throw new IllegalArgumentException();
>         this.lo = lo;              // here you MUST assign every field yourself
>         this.hi = hi;
>     }
> }
> ```
> Its parameter names must be exactly the component names (`Range(int a, int b)` → *invalid canonical constructor … invalid parameter names*). You can have the compact form or the long form, not both. The canonical constructor can't be less accessible than the record itself (`private Range { }` in a package-private record → *invalid canonical constructor … attempting to assign stronger access privileges*).

### 8.3 Other Constructors, Methods, and Static Members

```java
record Named(String name) {
    static int created = 0;                         // static fields: allowed
    static final int MAX = 50;

    Named {                                         // compact canonical constructor
        created++;
    }

    Named() { this("anon"); }                       // extra constructor: MUST start with this(…)

    static Named of(String s) { return new Named(s.strip()); }   // static factory: allowed
    String shout() { return name.toUpperCase() + "!"; }          // instance method: allowed
}
```

- Any constructor other than the canonical one must **delegate** to another constructor with `this(…)` as its first statement (*constructor is not canonical, so its first statement must invoke another constructor*). Only the canonical constructor assigns the fields.
- Records may declare static fields, static methods, instance methods, nested types, and may `implement` interfaces (`record Point(int x, int y) implements Comparable<Point> { … }`).
- An **accessor may be overridden**, but it must be `public` and have the same return type (a package-private `int x()` → *invalid accessor method … accessor method must be public*).

> [!warning] Trick: overriding an accessor doesn't change `toString`/`equals`
> ```java
> record Name(String s) {
>     public String s() { return s.toLowerCase(); }
> }
> Name n = new Name("A");
> System.out.println(n + " " + n.s());                  // Name[s=A] a
> System.out.println(n.equals(new Name("a")));          // false
> ```
> The generated `toString`, `equals`, and `hashCode` read the **fields**, not the accessors. Normalize values in the compact constructor instead, so the field itself holds the normalized value.

### 8.4 What Records Can't Do

| Attempt | Result |
|---|---|
| instance field in the body: `record X(int a) { int b; }` | compile error: *field declaration must be static* |
| `record X(int a) extends P { }` | compile error: records can't extend a class (they already extend `Record`) |
| `class Y extends SomeRecord` | compile error: *cannot inherit from final* |
| `abstract record X(…)` | compile error: *modifier abstract not allowed here* |
| a setter: `void set(int v) { a = v; }` | compile error: *cannot assign a value to final variable a* |
| instance initializer `{ … }` | compile error: *instance initializers not allowed in records* |
| a nested record using the outer object's fields | compile error: a nested record is implicitly `static` |

Records **can** be generic (`record Pair<A, B>(A first, B second) { }`) and can be declared **locally** inside a method, which is handy for a temporary grouping of values.

### 8.5 Records Are Only Shallowly Immutable

A record's fields are `final`, but its accessors return them **as they are**. A record with a mutable component leaks exactly like the `Team` class in [[#6. Leaking Internal State|§ 6]]:

```java
record Tags(int[] values) { }

int[] arr = {1, 2};
Tags t = new Tags(arr);
arr[0] = 7;                        // the caller's array IS the record's array
t.values()[1] = 8;                 // the accessor hands out the same array
System.out.println(Arrays.toString(t.values()));        // [7, 8]
System.out.println(t.equals(new Tags(new int[]{7, 8}))); // false : arrays compared with ==
System.out.println(t);             // Tags[values=[I@238e0d81] : array's toString
```

Three problems at once: the record is mutable, `equals` compares the array by **identity** ([[03 - Arrays#6.2 Comparing Arrays: `==`, `.equals()`, `Arrays.equals`|Arrays § 6.2]]), and `toString` prints the array's address. For collections, a defensive copy in the compact constructor fixes it:

```java
record Scores(List<Integer> list) {
    Scores { list = List.copyOf(list); }       // unmodifiable snapshot; List.equals compares content
}
```

For arrays, prefer a `List` component. If it must be an array, clone it in the compact constructor **and** override the accessor to return a clone, and override `equals`/`hashCode`/`toString` with the `Arrays` versions.

> [!tip] Record or class?
> Use a record when the object **is** its data: a point, a pair, a DTO, a map key, a method returning several values ([[01 - Methods#4.5 Returning More Than One Value|Methods § 4.5]]). Use an ordinary class when it has hidden state, changing state, or needs to extend another class.

---

## 9. Private Constructors and Helper Methods

`private` isn't only for fields.

**Private constructors** stop other classes from calling `new`:

```java
public final class MathUtil {
    private MathUtil() { }                       // no instances: it's a bag of static methods
    public static int twice(int n) { return 2 * n; }
}

new MathUtil();         // (elsewhere) compile error: MathUtil() has private access in MathUtil
```

- **Utility classes** (`Math`, `Arrays`, `Collections`) use this so that meaningless objects can't be created. Without it, the compiler would generate a public default constructor.
- **Static factories**: with a private constructor, the class controls creation completely (caching, validation, returning a subclass, see [[Java/04 - Object-Oriented Programming/01 - Classes and Objects#8.6 When to Use `static`|Classes and Objects § 8.6]]).
- A class whose constructors are all `private` also **can't be subclassed** from outside, because a subclass constructor must call `super(…)`. (Nested classes inside it still can, since they share its private access.)

**Private helper methods** split a long public method into steps without adding them to the API, so they can be renamed or removed later without breaking anyone.

---

## 10. Common Pitfalls

- **Public (or package-private) mutable fields**: any code in scope can break the object's invariants.
- **Thinking package-private is wider than `protected`.** It's the other way round: `protected` = package + subclasses.
- **Forgetting that `protected` grants access to the whole package**, not only to subclasses.
- **Using a `protected` member through a superclass-typed reference** from a subclass in another package, or calling `new` on a `protected` constructor there.
- **`private` or `protected` on a top-level class**, or any access modifier on a local variable.
- **A `public` member of a package-private class** expected to be usable from other packages.
- **Believing `private` protects each object from the others.** Access is per class: any `Account` method can change any `Account`'s private fields.
- **`year = year;` in a setter** because the parameter shadows the field.
- **Validating in the setter but not in the constructor** (or the other way round).
- **A getter and setter for every field** by reflex, which is a public field in disguise.
- **Returning a mutable field** (array, list, `StringBuilder`, `Date`) from a getter, or **storing the caller's object** in a constructor or setter without copying it.
- **Validating the caller's object and then copying it** instead of copying first.
- **Shallow defensive copies** of 2D arrays or of lists of mutable objects.
- **Confusing an unmodifiable view with a copy**: `Collections.unmodifiableList` shows later changes to the list it wraps.
- **`public static final` arrays**, which anyone can modify element by element.
- **Assuming `final` fields make a class immutable.** The referenced objects can still change.
- **A non-final "immutable" class** that a subclass can make mutable.
- **Calling `plus`/`withX`/`toUpperCase` on an immutable object and ignoring the result.**
- **Records**: calling `getX()` instead of `x()`; `this.x = x` in a compact constructor; adding instance fields; trusting that a record with an array or list component is immutable or compares by content; normalizing in an overridden accessor instead of in the constructor.

---

## 11. Quick Reference — Non-Obvious Outcomes

| Code | Result | Why |
|---|---|---|
| `private class X { }` (top level) | compile error | only `public` or package-private at top level |
| `private int n = 1;` inside a method | compile error | no access modifiers on locals |
| `other.balance` inside `Account`, `other` another `Account` | compiles | access is per class, not per object |
| subclass reads a superclass's `private` field | compile error | private members are not inherited |
| class in the same package reads a `protected` field | compiles | `protected` includes the package |
| subclass in another package: `this.p` / `childRef.p` | compiles | through its own type |
| subclass in another package: `parentRef.p` | compile error | *p has protected access* |
| subclass in another package: `new Parent()` (protected constructor) | compile error | only `super(…)` may call it |
| subclass in another package: protected **static** member | compiles | no object involved |
| other package uses a public member of a package-private class | compile error | *not public in a; cannot be accessed from outside package* |
| override narrows `public` to package-private | compile error | *attempting to assign weaker access privileges* |
| constructor assigns directly, setter validates | invalid objects can be created | constructor bypasses the check |
| `getMembers().add(x)` when getter returns the field | private list changes | reference leaked |
| `new Team(arr)` storing `arr`, then `arr[0] = 99` | Team's array changes | caller keeps the reference |
| `unmodifiableList(base)`, then `base.add("b")` | the view shows `"b"` | a view, not a copy |
| `List.copyOf(list with null)` | `NullPointerException` | rejects `null` elements |
| `view.add(…)` / `List.copyOf(…).add(…)` | `UnsupportedOperationException` | unmodifiable |
| `grid.clone()` then `copy[0][0] = 9` | `grid[0][0] == 9` | rows are shared (shallow) |
| `public static final int[] A`; `A[0] = 5` | compiles, changes the constant | `final` fixes the reference only |
| `final StringBuilder sb`; `sb.append("y")` | allowed | the object is mutable |
| `m.plus(other);` with immutable `m` | `m` unchanged | result discarded |
| `new Point(1, 2).toString()` (record) | `Point[x=1, y=2]` | generated |
| `p.getX()` on a record | compile error | accessor is `x()` |
| `new Point(1,2).equals(new Point(1,2))` (record) | `true` | value-based `equals` |
| same with an ordinary class, no override | `false` | `Object.equals` is identity |
| `record X(int a) { X { this.a = a; } }` | compile error | fields assigned implicitly after the body |
| `record X(int a) { int b; }` | compile error | *field declaration must be static* |
| record constructor `X(String s) { … }` without `this(…)` | compile error | non-canonical constructors must delegate |
| record accessor `int a()` without `public` | compile error | *accessor method must be public* |
| record canonical constructor with other parameter names | compile error | names must match the components |
| `class Y extends SomeRecord` | compile error | records are `final` |
| record with overridden accessor, then `toString` | shows the raw field | generated methods read fields |
| record with `int[]` component: `equals` on equal contents | `false` | arrays compared by identity |
| record with `int[]` component: `toString` | `[I@…` | array's own `toString` |
| compact constructor reassigning its parameter | the new value is stored | fields assigned from the parameters at the end |
| `new MathUtil()` with a private constructor | compile error | *has private access* |

---

## 12. Practice — Trick Questions

**Q1.** `Parent` is in package `a`, and `Child extends Parent` and `Other` are in package `b`. Which lines compile?

```java
package a;
public class Parent {
    private   int w;
              int x;
    protected int y;
    public    int z;
    protected Parent() { }
}
```

```java
package b;
public class Child extends a.Parent {
    void test(a.Parent p, Child c) {
        System.out.println(w);        // (1)
        System.out.println(x);        // (2)
        System.out.println(y);        // (3)
        System.out.println(c.y);      // (4)
        System.out.println(p.y);      // (5)
        System.out.println(p.z);      // (6)
        new a.Parent();               // (7)
    }
}
```

> [!success]- Answer
> | Line | Compiles? | Reason |
> |---|---|---|
> | (1) | ❌ | `private`: only inside `Parent` |
> | (2) | ❌ | package-private: `Child` is in another package, being a subclass doesn't help |
> | (3) | ✅ | inherited `protected`, used through `this` |
> | (4) | ✅ | `protected` through a reference of `Child`'s own type |
> | (5) | ❌ | `protected` through a `Parent` reference from another package |
> | (6) | ✅ | `public` |
> | (7) | ❌ | a `protected` constructor can only be called via `super(…)` from another package |
>
> If `Child` were moved into package `a`, (2), (5), and (7) would compile too; only (1) would still fail.

**Q2.** Rank these from most to least restrictive: `public`, `private`, `protected`, package-private. Which class in the same package as `Parent` can use a `protected` member?

> [!success]- Answer
> `private` → package-private → `protected` → `public`. **Every** class in the same package can use a `protected` member, whether it's a subclass or not. `protected` only **adds** subclasses in other packages on top of package access.

**Q3.** What is printed?

```java
class Account {
    private double balance;
    Account(double b) { balance = b; }
    void steal(Account other) { balance += other.balance; other.balance = 0; }
    double get() { return balance; }
}

Account a = new Account(10), b = new Account(5);
a.steal(b);
System.out.println(a.get() + " " + b.get());
```

> [!success]- Answer
> `15.0 0.0`. It compiles: `steal` is written inside `Account`, so it may use the `private` field of **any** `Account` object. Access control is per class, not per object.

**Q4.** The class below is meant to be immutable. Find every way a caller can still change a `Schedule` after construction.

```java
public class Schedule {
    private final String[] days;
    private final List<Integer> hours;

    public Schedule(String[] days, List<Integer> hours) {
        this.days = days;
        this.hours = hours;
    }
    public String[] getDays()      { return days; }
    public List<Integer> getHours() { return hours; }
}
```

> [!success]- Answer
> | Hole | Attack | Fix |
> |---|---|---|
> | constructor keeps the caller's array | `arr[0] = "X";` after `new Schedule(arr, …)` | `this.days = days.clone();` |
> | constructor keeps the caller's list | `list.add(99);` | `this.hours = List.copyOf(hours);` |
> | getter returns the array | `s.getDays()[0] = "X";` | `return days.clone();` |
> | getter returns the list | `s.getHours().clear();` | return the unmodifiable copy (already safe after the fix above) |
> | class not `final` | a subclass overrides `getDays()` or adds mutable state | `public final class Schedule` |
>
> `final` on the fields only stops reassignment. The elements (`String`, `Integer`) are immutable, so copying the array and list is deep enough here.

**Q5.** What is printed?

```java
List<String> base = new ArrayList<>(List.of("a"));
List<String> view = Collections.unmodifiableList(base);
List<String> copy = List.copyOf(base);
base.add("b");
System.out.println(view.size() + " " + copy.size());
view.add("c");
```

> [!success]- Answer
> `2 1`, then `view.add("c")` throws `UnsupportedOperationException`. The unmodifiable view blocks changes **through itself** but reflects changes made to `base`. `List.copyOf` made an independent snapshot.

**Q6.** What is printed?

```java
class Temp {
    private double c;
    Temp(double c) { this.c = c; }
    void setC(double c) {
        if (c < -273.15) throw new IllegalArgumentException();
        this.c = c;
    }
    double getC() { return c; }
}

Temp t = new Temp(-500);
System.out.println(t.getC());
t.setC(-500);
```

> [!success]- Answer
> `-500.0`, then the `setC` call throws `IllegalArgumentException`. The constructor assigns the field directly and skips the validation, so an invalid object was created. Validation has to be on **every** path into the field.

**Q7.** Which records compile?

```java
record A(int x) { int y; }                                 // (1)
record B(int x) { static int count; }                      // (2)
record C(int x) { C { this.x = Math.abs(x); } }            // (3)
record D(int x) { D { x = Math.abs(x); } }                 // (4)
record E(int x) { E(String s) { System.out.println(s); } } // (5)
record F(int x) { F() { this(0); } }                       // (6)
record G(int x) { int x() { return x; } }                  // (7)
record H(int x) implements Comparable<H> {                 // (8)
    public int compareTo(H o) { return Integer.compare(x, o.x); }
}
```

> [!success]- Answer
> | Record | Compiles? | Reason |
> |---|---|---|
> | (1) | ❌ | instance fields aren't allowed (*field declaration must be static*) |
> | (2) | ✅ | static fields are fine |
> | (3) | ❌ | can't assign the field in a compact constructor (*cannot assign a value to final variable x*) |
> | (4) | ✅ | reassigning the **parameter** is the correct way; the field gets `Math.abs(x)` |
> | (5) | ❌ | a non-canonical constructor must start with `this(…)` |
> | (6) | ✅ | delegates to the canonical constructor |
> | (7) | ❌ | an accessor must be `public` |
> | (8) | ✅ | records can implement interfaces |

**Q8.** What is printed?

```java
record Range(int lo, int hi) {
    Range { if (lo > hi) { int t = lo; lo = hi; hi = t; } }
}
record Name(String s) {
    public String s() { return s.toUpperCase(); }
}

System.out.println(new Range(5, 1));
Name n = new Name("ann");
System.out.println(n + " " + n.s() + " " + n.equals(new Name("ANN")));
```

> [!success]- Answer
> ```
> Range[lo=1, hi=5]
> Name[s=ann] ANN false
> ```
> The compact constructor swapped the **parameters**, and the fields were assigned from them afterwards. For `Name`, the generated `toString` and `equals` use the **field** (`"ann"`), not the overridden accessor, so `toString` shows `ann` and the two records aren't equal (`"ann"` vs. `"ANN"`).

**Q9.** What is printed?

```java
record Tags(int[] values) { }

int[] arr = {1, 2};
Tags t = new Tags(arr);
arr[0] = 7;
System.out.println(t.values()[0] + " " + t.equals(new Tags(new int[]{7, 2})) + " " + t.equals(new Tags(arr)));
```

> [!success]- Answer
> `7 false true`. The record stores the caller's array, so changing `arr` changes the record. The generated `equals` compares the array component with `equals`, which for arrays is identity: a different array with the same contents is not equal, but a record holding the **same** array is.

**Q10.** What is printed?

```java
final class Money {
    private final long cents;
    Money(long cents) { this.cents = cents; }
    Money plus(Money o) { return new Money(cents + o.cents); }
    public String toString() { return cents + "c"; }
}

Money m = new Money(100);
m.plus(new Money(50));
System.out.println(m);
```

> [!success]- Answer
> `100c`. `Money` is immutable, so `plus` returns a **new** object, and that result is thrown away. It should be `m = m.plus(new Money(50));`. The same bug as `s.toUpperCase();` on a `String`.

**Q11.** What is printed, and how should the constant be declared?

```java
class Config {
    public static final String[] MODES = {"easy", "hard"};
}

Config.MODES[1] = "impossible";
System.out.println(Config.MODES[1]);
```

> [!success]- Answer
> `impossible`. `final` only prevents `MODES = …`; the array's elements can still be changed by any class. Use `public static final List<String> MODES = List.of("easy", "hard");` (unmodifiable), or keep the array `private` and return a clone.

---

## 13. Summary

- **Encapsulation** hides fields behind methods so the class can keep its invariants and change its internals freely.
- **Access levels**, from narrowest: `private` (the class, including its nested classes) → package-private, no keyword (the package) → `protected` (the package **plus** subclasses) → `public` (everyone). Top-level classes are only `public` or package-private. Local variables take no access modifier.
- From a subclass in **another package**, `protected` instance members work only through `this`/`super` or a reference of the subclass's type, and `protected` constructors only through `super(…)`.
- A member is never more visible than its class. `private` members aren't inherited.
- Access is checked **per class at compile time**, not per object: a class's code may use the private members of any instance of that class.
- **Getters/setters** follow the `getX`/`isX`/`setX` conventions. Setters and constructors must both validate. Not every field needs them; behavior methods are often better.
- `private` protects the reference, not the object it points to. **Defensive copies** on the way in (copy, then validate) and out stop leaks. Unmodifiable views reflect later changes; `List.copyOf` makes a snapshot. `public static final` arrays are mutable.
- **Immutable classes**: `final` class, `private final` fields, no setters, defensive copies, no escaping `this`. "Modifying" methods return new objects, whose result must be used.
- **Records** (Java 16+) generate private final fields, the canonical constructor, `x()` accessors, and value-based `equals`/`hashCode`/`toString`. Validate or normalize in a **compact constructor** by reassigning parameters. Records are `final`, extend `Record`, allow no instance fields, and are only **shallowly** immutable.
- **Private constructors** prevent instantiation (utility classes) and give static factories full control.

## Related

- [[00 - Syllabus|Syllabus]]
- Previous: [[Java/04 - Object-Oriented Programming/01 - Classes and Objects|Classes and Objects]] · Next: [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]]
- [[Java/04 - Object-Oriented Programming/01 - Classes and Objects|Classes and Objects]]: fields, constructors, `this`, `final` fields, static factories
- [[01 - Introduction to Java#5.4 Packages and the Classpath|Introduction to Java § 5.4]]: packages and how to compile them
- [[02 - Variables and Data Types#7.2 `final` Doesn't Mean Immutable|Variables and Data Types § 7.2]]: `final` vs. immutable
- [[03 - Arrays|Arrays]]: aliasing, `clone()`, shallow vs. deep copies
- [[02 - Strings|Strings]]: `String` as the model immutable class
- [[01 - Methods#5.4 Immutable Objects Look Like Primitives|Methods § 5.4]]: why passing an immutable object feels like passing a primitive
- [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]]: `protected` from the subclass side, overriding can't narrow access, overridable methods in constructors
- [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]: writing `equals`/`hashCode`/`toString` by hand, and why mutable keys break hash collections
- [[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]]: unmodifiable collections, `List.of`/`List.copyOf`
