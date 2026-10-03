# Classes and Objects in Java

A <span class="hl-blue">class</span> is a blueprint that describes a kind of thing: what data it holds (**fields**) and what it can do (**methods**). An <span class="hl-blue">object</span> is one concrete thing built from that blueprint, with its own copy of the data. This chapter covers how a class is declared, how `new` creates objects and what the variable actually holds, fields and their defaults, instance methods, constructors and constructor chaining, the `this` keyword, `static` (class-level) members, and the exact order in which a class and its objects are initialized.

Access modifiers (`private`, `public`, …) and getters/setters are covered in [[Java/04 - Object-Oriented Programming/02 - Encapsulation|Encapsulation]], and `extends`/`super` in [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]]. This chapter uses package-private members (no modifier) in most examples to keep the focus on classes and objects themselves.

## Contents

- [[#1. Classes and Objects — The Idea|1. Classes and Objects — The Idea]]
- [[#2. Declaring a Class|2. Declaring a Class]]
- [[#3. Creating Objects with `new`|3. Creating Objects with `new`]]
- [[#4. Fields (Instance Variables)|4. Fields (Instance Variables)]]
- [[#5. Instance Methods|5. Instance Methods]]
- [[#6. Constructors|6. Constructors]]
- [[#7. The `this` Keyword|7. The `this` Keyword]]
- [[#8. Static Members|8. Static Members]]
- [[#9. Initialization Order|9. Initialization Order]]
- [[#10. Objects and References in Practice|10. Objects and References in Practice]]
- [[#11. Putting It Together — A Complete Class|11. Putting It Together — A Complete Class]]
- [[#12. Common Pitfalls|12. Common Pitfalls]]
- [[#13. Quick Reference — Non-Obvious Outcomes|13. Quick Reference — Non-Obvious Outcomes]]
- [[#14. Practice — Trick Questions|14. Practice — Trick Questions]]
- [[#15. Summary|15. Summary]]

---

## 1. Classes and Objects — The Idea

> [!note] Definitions
> - A **class** is a user-defined **type**. It declares the fields every object of that type will have and the methods that operate on them.
> - An **object** (an **instance** of the class) is a block of memory on the heap holding one set of values for those fields. Many objects can be created from one class.
> - **State** is the current values of an object's fields. **Behavior** is what its methods do, usually reading or changing that state.
> - A **member** of a class is anything declared directly in its body: fields, methods, nested types. Constructors and initializer blocks are declared there too, but are not members.
> - **Instance** members belong to each object. **Static** members belong to the class itself and are shared by all objects ([[#8. Static Members|§ 8]]).

```java
public class Point {
    int x;                       // field: every Point has its own x
    int y;                       // field: every Point has its own y

    double distanceToOrigin() {  // instance method: works on THIS point's x and y
        return Math.sqrt(x * x + y * y);
    }
}
```

```java
Point a = new Point();           // object #1
a.x = 3;
a.y = 4;

Point b = new Point();           // object #2, completely separate state
b.x = 6;

System.out.println(a.distanceToOrigin());   // 5.0
System.out.println(b.distanceToOrigin());   // 6.0
```

One class (`Point`), two objects, two independent sets of `x` and `y`. The method is written once in the class but runs against whichever object it is called on.

---

## 2. Declaring a Class

```java
public class Student {
    // fields
    String name;
    int year = 1;

    // constructor
    Student(String name) {
        this.name = name;
    }

    // method
    void promote() {
        year++;
    }
}
```

| Part | Example | Notes |
|---|---|---|
| Modifiers | `public` | for top-level classes only `public` or nothing (package-private); also `final`, `abstract` |
| `class` + name | `class Student` | by convention a noun in `UpperCamelCase` |
| Body `{ … }` | | contains fields, constructors, methods, initializer blocks, nested types, in **any order** |

A class can also take **type parameters** after its name (`class Box<T> { T value; … }`) so that the same code works for `Box<String>`, `Box<Integer>`, and so on. See [[Java/05 - Working with Data and Errors/02 - Generics|Generics]].

### 2.1 Files and Class Names

- A `.java` file may contain **several** top-level classes, but **at most one** may be `public`, and that one must have the **same name as the file** (`public class Student` → `Student.java`). See [[01 - Introduction to Java#6. Files, Classes, and Names|Introduction to Java § 6]].
- Compiling produces **one `.class` file per class**, including non-public and nested ones (`Student.class`, `Helper.class`, `Outer$Inner.class`).
- The order of members inside a class does not matter for methods: a method can use a field or call a method declared further down. It **does** matter for field initializers ([[#9.3 Forward References|§ 9.3]]).

### 2.2 Every Class Extends `Object`

A class that doesn't say `extends` implicitly extends `java.lang.Object`. That is why every object, even one of an empty class, already has `toString()`, `equals(Object)`, and `hashCode()`:

```java
class Empty { }

Empty e = new Empty();
System.out.println(e.toString());    // Empty@1b6d3586  (class name @ hex hash code; the number varies)
System.out.println(e.equals(e));     // true
```

The inherited versions are rarely what you want ([[#10.3 Printing and Comparing Objects|§ 10.3]]); overriding them is covered in [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]].

> [!info]- Records: a shortcut for "data carrier" classes (Java 16+)
> ```java
> record Point(int x, int y) { }
> ```
> declares a final class with two `private final` fields, a constructor `Point(int x, int y)`, accessor methods `x()` and `y()` (not `getX()`), and sensible `equals`, `hashCode`, and `toString` (`Point[x=1, y=2]`). Records are covered with immutable design in [[Java/04 - Object-Oriented Programming/02 - Encapsulation#8. Records (Java 16+)|Encapsulation § 8]]. This chapter uses ordinary classes, because records hide exactly the mechanics being explained here.

---

## 3. Creating Objects with `new`

### 3.1 What `new` Does

```java
Point p = new Point();
```

This one line does four separate things:

| Step | What happens |
|---|---|
| 1 | `Point p` declares a **reference variable**. It can refer to a `Point`, but by itself creates no object. |
| 2 | `new Point` allocates memory for a new object on the **heap**, and sets every field to its **default value** (`0`, `false`, `null`). |
| 3 | The field initializers, initializer blocks, and the matching **constructor** run ([[#9. Initialization Order|§ 9]]). |
| 4 | `new` evaluates to a **reference** to the new object, which is stored in `p`. |

> [!important] Key rule: the variable is not the object
> A variable of a class type holds a **reference** (roughly, the address of an object), never the object itself. Assigning, passing, or returning it copies the reference, not the object. Only `new` (or something that calls `new` internally) creates an object.

```
stack                heap
p ──────────────►   ┌ Point ───┐
                    │ x = 0    │
                    │ y = 0    │
                    └──────────┘
```

### 3.2 Declaring a Variable Creates No Object

```java
Point p;                 // no object exists yet
p.x = 5;                 // compile error (local): variable p might not have been initialized

Point q = null;          // explicitly refers to nothing
q.x = 5;                 // compiles, but throws NullPointerException at runtime
```

- A **local** reference variable has no default value, so using it before assignment is a **compile** error (see [[02 - Variables and Data Types#5. Local, Instance, and Static Variables|Variables and Data Types § 5]]).
- A reference that is **`null`** compiles fine, and any attempt to reach a field or instance method through it throws `NullPointerException` at runtime.
- A reference **field** defaults to `null`, so the same runtime error appears when a field was never assigned an object.

### 3.3 Several Ways to Hold the Result

```java
Point p = new Point();          // usual form
var p2 = new Point();           // Java 10+: type inferred as Point (local variables only)
new Point();                    // legal: the object is created and immediately unreachable
double d = new Point().distanceToOrigin();   // legal: use the object once without naming it
```

### 3.4 Object Lifetime and Garbage Collection

Objects are **never freed explicitly**. There is no `delete` and no destructor. An object becomes eligible for **garbage collection** once no chain of references from a running method (or a static field) reaches it. The JVM reclaims it at some unspecified later time, or never if memory is plentiful.

```java
Point a = new Point();   // object #1
Point b = new Point();   // object #2
a = b;                   // object #1 is now unreachable → eligible for GC
b = null;                // object #2 is still reachable through a
```

> [!warning] Common mistake: expecting cleanup code to run
> `Object.finalize()` is deprecated (Java 9) and was never guaranteed to run. `System.gc()` is only a hint. Resources such as files must be closed explicitly, normally with `try`-with-resources ([[Java/05 - Working with Data and Errors/01 - Exception Handling|Exception Handling]]), never by relying on the garbage collector.

---

## 4. Fields (Instance Variables)

A <span class="hl-blue">field</span> is a variable declared directly in the class body. Without `static`, it is an **instance field**: every object gets its own copy, created with the object and living as long as the object does.

### 4.1 Default Values and Explicit Initializers

Fields, unlike local variables, always have a value. If no initializer is given, they get the type's default:

```java
class Settings {
    int volume;              // 0
    boolean muted;           // false
    double ratio;            // 0.0
    char mode;               // '\u0000'
    String name;             // null
    int[] levels;            // null (the array itself is not created)

    int maxVolume = 100;     // explicit initializer: runs for every new object
    int[] slots = new int[4];// each object gets its OWN new array
}
```

Full table: [[02 - Variables and Data Types#6. Default Values|Variables and Data Types § 6]].

> [!warning] Trick: an initializer that creates an object runs once **per object**
> `int[] slots = new int[4];` creates a fresh array for each `Settings`. Two `Settings` objects do **not** share `slots`. Sharing happens only with `static` fields ([[#8.1 Static Fields — One Copy per Class|§ 8.1]]).

### 4.2 Accessing Fields

```java
Settings s = new Settings();
s.volume = 30;                  // outside the class: reference.field
System.out.println(s.volume);   // 30
```

Inside the class's own instance methods and constructors, a field can be written by its plain name (`volume`), which means `this.volume` ([[#7. The `this` Keyword|§ 7]]).

### 4.3 `final` Fields

A `final` field must be assigned **exactly once**, and the compiler checks it. It can be assigned either in its declaration, or in an instance initializer block, or in **every** constructor (a *blank final*, see [[02 - Variables and Data Types#7.1 Blank Finals|Variables and Data Types § 7.1]]):

```java
class Account {
    final int id;
    final String currency = "EUR";

    Account(int id) { this.id = id; }     // OK
    Account()       { }                   // compile error: variable id might not have been initialized

    void reset()    { id = 0; }           // compile error: cannot assign a value to final variable id
}
```

`final` stops **reassigning** the field. If the field refers to a mutable object (an array, a `StringBuilder`), the object itself can still change ([[02 - Variables and Data Types#7.2 `final` Doesn't Mean Immutable|`final` Doesn't Mean Immutable]]).

---

## 5. Instance Methods

An <span class="hl-blue">instance method</span> (a method without `static`) always runs **on a specific object**, the one before the dot, and reads and writes that object's fields.

```java
class Counter {
    int count;

    void increment()  { count++; }            // changes this object's state
    int  get()        { return count; }       // reads this object's state
    boolean isAbove(Counter other) {          // can also read another object's fields
        return count > other.count;
    }
}

Counter a = new Counter();
Counter b = new Counter();
a.increment();
a.increment();
b.increment();
System.out.println(a.get() + " " + b.get() + " " + a.isAbove(b));   // 2 1 true
```

- The same method code serves every object. The JVM passes the target object in as a hidden parameter, which is what `this` refers to.
- Calling an instance method needs an object: `reference.method(…)`. Through a `null` reference it throws `NullPointerException`.
- An instance method of a class may use **another object's** fields of the same class (`other.count`), even `private` ones. Access control is per class, not per object ([[Java/04 - Object-Oriented Programming/02 - Encapsulation#4. Access Is per Class, Not per Object|Encapsulation § 4]]).
- Declaration, parameters, overloading, and pass-by-value work exactly as in [[01 - Methods|Methods]].

> [!tip] Instance or static?
> If a method uses any instance field or calls any instance method, it must be an instance method. If it uses only its parameters (like `Math.max`), make it `static` ([[#8.2 Static Methods|§ 8.2]]).

---

## 6. Constructors

A <span class="hl-blue">constructor</span> is a special block of code that runs when an object is created with `new`. Its job is to put the new object into a valid starting state.

```java
class Point {
    int x;
    int y;

    Point(int x, int y) {      // constructor: same name as the class, NO return type
        this.x = x;
        this.y = y;
    }
}

Point p = new Point(3, 4);     // arguments are passed to the constructor
```

### 6.1 Constructor Rules

> [!important] Rules
> - The name must be **exactly the class name**.
> - There is **no return type**, not even `void`. With a return type it is an ordinary method that `new` never calls (see [[01 - Methods#2.1 Where Methods Can (and Can't) Go|Methods § 2.1]]).
> - A bare `return;` is allowed (it ends the constructor early). `return value;` is a compile error (*unexpected return value*).
> - Allowed modifiers: only access modifiers (`public`, `protected`, `private`, or none). `static`, `final`, and `abstract` are compile errors (*modifier static not allowed here*).
> - Constructors are **not members** and are **not inherited**. A subclass must declare its own ([[Java/04 - Object-Oriented Programming/03 - Inheritance#5.1 Constructors Are Not Inherited|Inheritance § 5.1]]).
> - A constructor can be called **only** through `new`, or as the first statement of another constructor (`this(…)` / `super(…)`). It cannot be called like a method: `p.Point(1, 2)` does not compile.

### 6.2 The Default Constructor

If a class declares **no constructor at all**, the compiler adds a <span class="hl-blue">default constructor</span>: no parameters, an empty body, and the same access level as the class.

```java
class Box { int size; }        // no constructor written
Box b = new Box();             // OK: uses the compiler-generated Box()
```

> [!warning] Trick: declaring **any** constructor removes the default one
> <span class="hl-yellow">Exam favourite.</span>
> ```java
> class Box {
>     int size;
>     Box(int size) { this.size = size; }
> }
>
> Box a = new Box(5);   // OK
> Box b = new Box();    // compile error: constructor Box in class Box cannot be applied to given types
> ```
> The default constructor exists **only** when you write none. As soon as you add `Box(int)`, `new Box()` stops compiling. If you still need it, declare `Box() { }` yourself. This also breaks subclasses whose constructors implicitly call `super()` ([[Java/04 - Object-Oriented Programming/03 - Inheritance#5.3 A Superclass Without a No-Arg Constructor|Inheritance § 5.3]]).

### 6.3 Overloaded Constructors

A class can have several constructors, as long as their parameter lists differ. The usual overload rules apply ([[01 - Methods#7. Method Overloading|Methods § 7]]):

```java
class Rectangle {
    double width, height;

    Rectangle(double width, double height) { this.width = width; this.height = height; }
    Rectangle(double side)                 { this.width = side;  this.height = side;   }
    Rectangle()                            { this.width = 1;     this.height = 1;      }
}

new Rectangle(2, 3);   // Rectangle(double, double): the ints widen to double
new Rectangle(5);      // Rectangle(double)
new Rectangle();       // Rectangle()
```

The three bodies above repeat the same assignments. Constructor chaining removes that duplication.

### 6.4 Constructor Chaining with `this(…)`

One constructor can hand over to another constructor of the **same class** with `this(arguments)`. All the real work then lives in one "main" constructor:

```java
class Rectangle {
    double width, height;

    Rectangle(double width, double height) {   // the one that does the work
        this.width = width;
        this.height = height;
    }
    Rectangle(double side) { this(side, side); }   // delegates
    Rectangle()            { this(1); }            // delegates, which delegates again
}
```

> [!important] Rules for `this(…)`
> - It must be the **first statement** of a constructor (before Java 25, see the note below). `x = 1; this(2);` is a compile error (*call to this must be first statement in constructor*).
> - It can appear **only in a constructor**, never in a method.
> - A constructor can call **at most one** of `this(…)` or `super(…)`, never both.
> - Constructors must not call each other in a **cycle**: `A() { this(1); }` with `A(int x) { this(); }` is a compile error (*recursive constructor invocation*).
> - The arguments to `this(…)` cannot use instance fields or instance methods of the object under construction (it doesn't exist properly yet). They can use parameters, constants, and `static` methods.

> [!info]- Java 25+: statements before `this(…)` / `super(…)`
> Java 25 finalized **flexible constructor bodies** (JEP 513). Statements may now come **before** the `this(…)` or `super(…)` call, typically to validate or compute arguments:
> ```java
> Rectangle(double side) {
>     if (side <= 0) throw new IllegalArgumentException("side must be positive");
>     this(side, side);
> }
> ```
> Code in this "prologue" still may not use the object being constructed: no reading fields, no calling instance methods, no `this` as a value. (It may assign fields that have no initializer.) On Java 24 and earlier, and in most course material, the "first statement" rule above holds.

### 6.5 A Constructor Cannot Return a Different Object

A constructor always initializes **the object `new` just created**. It cannot return a different or existing object, and it cannot return `null`. If creation should sometimes reuse an object or fail softly, use a **static factory method** instead ([[#8.6 When to Use `static`|§ 8.6]]).

If a constructor **throws** an exception, the `new` expression fails, nothing is assigned to the variable, and the half-built object is simply discarded:

```java
class Age {
    int value;
    Age(int value) {
        if (value < 0) throw new IllegalArgumentException("negative age");
        this.value = value;
    }
}

Age a = null;
try { a = new Age(-1); } catch (IllegalArgumentException e) { }
System.out.println(a);   // null: the assignment never happened
```

---

## 7. The `this` Keyword

Inside an instance method or a constructor, <span class="hl-blue">`this`</span> is a reference to **the current object**: the object the method was called on, or the object being constructed.

### 7.1 Use 1 — Reaching a Shadowed Field

When a parameter or local variable has the same name as a field, the plain name means the **parameter**, and `this.name` means the **field**:

```java
class Point {
    int x, y;

    Point(int x, int y) {
        this.x = x;       // field x = parameter x
        this.y = y;
    }
}
```

> [!warning] Common mistake: `x = x;`
> ```java
> Point(int x, int y) {
>     x = x;            // assigns the parameter to itself: the field is untouched
>     y = y;
> }
> new Point(3, 4).x     // 0, not 3
> ```
> This compiles without error (at most an IDE warning) and silently leaves the fields at their defaults. It is the most common constructor bug. See [[02 - Variables and Data Types#8. Scope and Shadowing|Scope and Shadowing]].

When there is **no** name clash, `this.` is optional: `count++` inside `Counter` already means `this.count++`.

### 7.2 Use 2 — Calling Another Constructor: `this(…)`

Covered in [[#6.4 Constructor Chaining with `this(…)`|§ 6.4]]. Note the difference: `this.x` is the current object's field, `this(…)` is a constructor call.

### 7.3 Use 3 — Passing or Returning the Current Object

```java
class Node {
    Node next;
    void linkTo(Node other) { other.next = this; }  // pass the current object along
}

class Builder {
    StringBuilder sb = new StringBuilder();

    Builder add(String s) {
        sb.append(s);
        return this;                 // return the current object → calls can be chained
    }
}

String s = new Builder().add("a").add("b").add("c").sb.toString();   // "abc"
```

Returning `this` is what makes **method chaining** (`sb.append(x).append(y)`) possible. `StringBuilder` itself works this way ([[Java/03 - Program Structure/02 - Strings#5. StringBuilder|Strings § 5]]).

### 7.4 What `this` Can't Do

| Code | Result | Why |
|---|---|---|
| `this` inside a `static` method | compile error: *non-static variable this cannot be referenced from a static context* | a static method runs without any object |
| `this = other;` | compile error: *cannot assign to 'this'* | `this` is fixed for the whole call |
| `this == null` | always `false` | an instance method can never be running on `null` (the call would have thrown first) |
| `this(…)` inside a method | compile error | constructor calls only as the first statement of a constructor |

---

## 8. Static Members

A member declared with <span class="hl-blue">`static`</span> belongs to the **class itself**, not to any object. There is exactly one copy, which exists even if no object is ever created.

### 8.1 Static Fields — One Copy per Class

```java
class Player {
    static int playersCreated = 0;   // ONE counter shared by the whole class
    String name;                     // one name per Player object

    Player(String name) {
        this.name = name;
        playersCreated++;            // every constructor call updates the shared counter
    }
}

new Player("Ann");
new Player("Bob");
System.out.println(Player.playersCreated);   // 2
```

```
class Player (one copy)          objects (one copy each)
┌───────────────────────┐        ┌ Player ─────┐   ┌ Player ─────┐
│ playersCreated = 2    │        │ name "Ann"  │   │ name "Bob"  │
└───────────────────────┘        └─────────────┘   └─────────────┘
```

![[Classes - Instance vs Static Fields.excalidraw|800]]

A change to a static field through **any** path is visible through **every** path, because there is only one variable.

### 8.2 Static Methods

A static method belongs to the class and runs **without a current object**. So it has no `this`, and cannot use instance fields or instance methods directly:

```java
class Temperature {
    double celsius;

    static double toFahrenheit(double c) {      // uses only its parameter: fine as static
        return c * 9 / 5 + 32;
    }

    static void bad() {
        System.out.println(celsius);    // compile error: non-static variable celsius cannot be referenced from a static context
        show();                         // compile error: non-static method show() cannot be referenced from a static context
    }

    static void ok(Temperature t) {
        System.out.println(t.celsius);  // OK: an explicit object is given
        t.show();                       // OK
    }

    void show() {
        System.out.println(toFahrenheit(celsius));   // OK: instance code may use static members freely
    }
}

double f = Temperature.toFahrenheit(100);           // 212.0 : called on the class
```

This is exactly why `main`, which is `static`, cannot call the instance methods of its own class without first creating an object ([[01 - Methods#3.1 Calling Instance Methods from `main`|Methods § 3.1]]).

### 8.3 Instance vs. Static at a Glance

| | Instance member | Static member |
|---|---|---|
| Belongs to | each object | the class |
| Number of copies | one per object | exactly one |
| Created | with each `new` | when the class is initialized ([[#9.1 Class Initialization (Static)|§ 9.1]]) |
| Normal access | `reference.name` | `ClassName.name` |
| Has `this`? | ✅ | ❌ |
| May use instance members directly? | ✅ | ❌ (needs an explicit object) |
| May use static members directly? | ✅ | ✅ |
| Typical use | an object's state and behavior | shared counters, constants, utility methods, factories |

### 8.4 Accessing Static Members Through a Reference

Java allows `reference.staticMember`, but the compiler simply replaces it with `ClassName.staticMember`. <span class="hl-yellow">The object is never looked at, so even a `null` reference works:</span>

```java
class Counter {
    static int total = 7;
    int mine;
}

Counter c = null;
System.out.println(c.total);    // 7 : no NullPointerException! compiled as Counter.total
System.out.println(c.mine);     // NullPointerException: an instance field needs a real object
```

```java
Counter a = new Counter(), b = new Counter();
a.total = 100;                  // looks like it changes a's copy...
System.out.println(b.total);    // 100 : ...but there is only one total
```

> [!tip] Always write `ClassName.member` for statics
> Accessing statics through a reference compiles (most IDEs warn), but it misleads readers into thinking the value belongs to that object. Static methods called through a reference also do **not** use dynamic dispatch: the declared type decides which one runs ([[Java/04 - Object-Oriented Programming/04 - Polymorphism#3.2 What Dispatches and What Doesn't|Polymorphism § 3.2]]).

### 8.5 Constants: `static final`

A value that is the same for all objects and never changes is declared `static final`, named in `UPPER_SNAKE_CASE`:

```java
class Circle {
    static final double PI_APPROX = 3.14159;
    static final int MAX_RADIUS;            // blank static final:
    static { MAX_RADIUS = 1000; }           // must be assigned in a static initializer block

    double radius;
}
```

- A `static final` field must be assigned in its declaration or in a `static` block. It can **not** be assigned in a constructor (constructors run per object, possibly never or many times).
- `final` alone (non-static) means one unchangeable value **per object**, e.g. an ID. `static` alone means one **shared, changeable** value. `static final` means one shared, unchangeable value.

### 8.6 When to Use `static`

- **Constants** shared by all objects: `Math.PI`, `Integer.MAX_VALUE`.
- **Utility methods** that depend only on their parameters: `Math.sqrt`, `Arrays.sort`, `Integer.parseInt`. Such utility classes often have a `private` constructor so that no objects can be created.
- **Class-wide state**, such as a counter of created objects or the next ID to assign.
- **Static factory methods**: named alternatives to constructors that may validate, cache, or return an existing object: `Integer.valueOf(5)`, `List.of(…)`, `LocalDate.of(2026, 9, 26)`.

> [!warning] Common mistake: making everything `static` to silence the compiler
> Beginners often "fix" *cannot be referenced from a static context* by marking fields `static`. The code then compiles, but every object shares one value: two `Player`s with a `static String name` both end up with the last name assigned. Fix the design instead: create an object and call the instance method on it.

> [!info]- `static` can't be used on local variables
> `void f() { static int calls = 0; }` is a compile error. Java has no C-style static locals. A value that must survive between calls has to be a field (static or instance).

---

## 9. Initialization Order

<span class="hl-yellow">A common source of "what does this print?" questions.</span> Two separate processes are involved: initializing the **class** (once) and initializing each **object** (on every `new`).

### 9.1 Class Initialization (Static)

The class is initialized **once**, the first time it is actively used:

1. All static fields are set to their default values.
2. The **static field initializers** and **`static { … }` blocks** run **top to bottom, in the order they appear in the source**.

What triggers it, and what doesn't:

| Triggers class initialization | Does **not** trigger it |
|---|---|
| the first `new ClassName(…)` | declaring a variable: `Point p;` |
| calling a static method | creating an array: `new Point[10]` |
| reading or writing a static field (other than a constant) | reading a compile-time constant (`static final int X = 5;`), which the compiler copies inline |
| running the class as the program (`main`) | |

```java
class Config {
    static final int SIZE = 5;              // compile-time constant
    static final Integer LIMIT = 6;         // NOT a constant (Integer is not a primitive/String)
    static { System.out.println("Config initialized"); }
}

System.out.println(Config.SIZE);    // 5                 (no initialization)
System.out.println(Config.LIMIT);   // Config initialized, then 6
```

### 9.2 Object Initialization (Instance)

On **every** `new`:

1. Memory is allocated and **all** instance fields get their default values.
2. The constructor is called with the arguments. If its first statement is `this(…)`, that other constructor is entered first (and so on).
3. The superclass constructor runs (`super(…)`, explicit or implicit, see [[Java/04 - Object-Oriented Programming/03 - Inheritance#6. Initialization Order Across a Hierarchy|Inheritance § 6]] for the full order across a hierarchy).
4. The **instance field initializers** and **instance initializer blocks `{ … }`** run **top to bottom in source order**.
5. The rest of the constructor body runs (and then, returning up the chain, the rest of any constructor that called `this(…)`).

> [!important] Key rule: initializers run once per object, even with `this(…)`
> Field initializers and `{ }` blocks run as part of the constructor that does **not** start with `this(…)` (the one at the end of the chain). They are never repeated for the delegating constructors.

```java
class Demo {
    static { System.out.println("A"); }
    { System.out.println("B"); }
    Demo()         { this("x"); System.out.println("C"); }
    Demo(String s) { System.out.println("D" + s); }
    static { System.out.println("E"); }
}

new Demo();
new Demo("y");
```

> [!example]- Step by step: output of `new Demo(); new Demo("y");`
> ```
> A
> E
> B
> Dx
> C
> B
> Dy
> ```
> | Output | Reason |
> |---|---|
> | `A`, `E` | first use of `Demo` → class initialization: both static blocks in source order, **once** |
> | `B` | `Demo()` delegates to `Demo(String)`; that one runs the instance block before its body |
> | `Dx` | body of `Demo(String)` |
> | `C` | back in `Demo()`, the rest of its body |
> | `B`, `Dy` | second object: no static blocks this time; instance block, then constructor body |
>
> Note that `B` is printed **once per object**, not once per constructor in the chain.

![[Classes - Initialization Order.excalidraw|800]]

> [!tip] Instance initializer blocks are rarely needed
> A plain `{ … }` block in a class body runs for every object before the constructor body. It is useful only for setup shared by several constructors that don't chain. Normally `this(…)` chaining is the clearer way. Static blocks are more common, for computing complex static constants.

### 9.3 Forward References

A field initializer may not read, **by its simple name**, a field declared **further down**:

```java
class F {
    int a = b + 1;          // compile error: illegal forward reference
    int b = 5;
}
```

But the rule is purely textual, so the compiler cannot catch indirect reads, which see the **default value**:

```java
class F {
    int a = getB();         // calls a method that reads b before b's initializer has run
    int c = this.b + 1;     // qualified name: allowed, reads the default 0
    int b = 5;
    int getB() { return b; }
}

F f = new F();
System.out.println(f.a + " " + f.c + " " + f.b);   // 0 1 5
```

The same happens with a `final` field read by a method called from the constructor before the assignment:

```java
class G {
    final int x;
    G() {
        show();     // x=0 : the final field is read before it is assigned
        x = 1;
        show();     // x=1 : so a final field can be seen with TWO different values
    }
    void show() { System.out.println("x=" + x); }
}
```

> [!example]- Trick: a static field initialized "after" a static instance
> ```java
> class Single {
>     static Single INSTANCE = new Single();   // (1) runs the constructor right now
>     static int count = 0;                    // (2) then resets count to 0
>     static int count2;                       // no initializer: never reset
>
>     Single() { count++; count2++; }
> }
>
> System.out.println(Single.count + " " + Single.count2);   // 0 1
> ```
> Static initializers run in source order. At (1) both counters are still at their default `0`, and the constructor increments both to `1`. Then (2) executes the initializer `count = 0`, wiping out the increment. `count2` has no initializer, so nothing resets it. Moving `INSTANCE` below the counters gives `1 1`.

---

## 10. Objects and References in Practice

### 10.1 Assignment Creates an Alias

```java
Point p = new Point(1, 2);
Point q = p;             // copies the REFERENCE: one object, two names
q.x = 99;
System.out.println(p.x); // 99
```

To get an independent copy, create a new object and copy the fields (for example a *copy constructor* `Point(Point other) { this(other.x, other.y); }`). The same aliasing applies to arrays ([[03 - Arrays#6.1 Assignment Creates an Alias, Not a Copy|Arrays § 6.1]]).

### 10.2 Objects as Parameters and Return Values

Passing an object to a method copies the reference. The method can change the object's fields (the caller sees it) but cannot make the caller's variable refer to another object (see [[01 - Methods#5. Parameter Passing — Always Pass-by-Value|Methods § 5]]):

```java
static void moveRight(Point p) { p.x++; }             // visible to the caller
static void replace(Point p)   { p = new Point(0, 0); } // not visible: local copy reassigned

static Point midpoint(Point a, Point b) {             // returning a new object
    return new Point((a.x + b.x) / 2, (a.y + b.y) / 2);
}
```

### 10.3 Printing and Comparing Objects

Until a class overrides them, the methods inherited from `Object` work on **identity**, not content:

```java
Point p = new Point(1, 2);
Point q = new Point(1, 2);
Point r = p;

System.out.println(p);            // Point@6d06d69c : class name + hash code, not "(1, 2)"
System.out.println(p == q);       // false : two different objects
System.out.println(p == r);       // true  : same object
System.out.println(p.equals(q));  // false : Object.equals is the same as ==
```

To print or compare by content, the class must override `toString()` and `equals()` (and `hashCode()` together with `equals`):

```java
class Point {
    int x, y;
    Point(int x, int y) { this.x = x; this.y = y; }

    @Override
    public String toString() { return "(" + x + ", " + y + ")"; }
}

System.out.println(new Point(1, 2));          // (1, 2)
System.out.println("P = " + new Point(1, 2)); // P = (1, 2) : concatenation calls toString()
```

Overriding `equals`/`hashCode` correctly is covered in [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]. `==` on references is covered in [[03 - Operators#7.3 `==` on References Compares Identity, Not Content|Operators § 7.3]].

### 10.4 Arrays of Objects Start Full of `null`

```java
Point[] pts = new Point[3];        // ONE array object, ZERO Point objects
System.out.println(pts[0]);        // null
pts[0].x = 5;                      // NullPointerException

for (int i = 0; i < pts.length; i++) {
    pts[i] = new Point(i, i);      // each element needs its own new
}
```

> [!warning] Common mistake
> `new Point[3]` creates an array of three **references**, all `null`. It does not call any `Point` constructor (it doesn't even initialize the `Point` class). Each element must be created separately.

---

## 11. Putting It Together — A Complete Class

This class uses every idea from the chapter. It also uses `private`, which is explained in the next chapter ([[Java/04 - Object-Oriented Programming/02 - Encapsulation#3. The Four Access Levels|Encapsulation § 3]]): for now, read it as "only code inside `BankAccount` may touch this".

```java
public class BankAccount {
    private static int nextId = 1;              // class-wide: next ID to hand out

    private final int id;                       // per object, set once
    private final String owner;                 // per object, set once
    private double balance;                     // per object, changes

    public BankAccount(String owner, double balance) {   // main constructor
        if (balance < 0) {
            throw new IllegalArgumentException("negative balance");
        }
        this.id = nextId++;                     // reads and advances the shared counter
        this.owner = owner;
        this.balance = balance;
    }

    public BankAccount(String owner) {          // convenience constructor
        this(owner, 0.0);                       // delegates: validation lives in one place
    }

    public BankAccount deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("amount must be positive");
        }
        balance += amount;
        return this;                            // allows chaining
    }

    public boolean withdraw(double amount) {
        if (amount <= 0 || amount > balance) {
            return false;
        }
        balance -= amount;
        return true;
    }

    public double getBalance() { return balance; }

    public static int accountsOpened() {        // static: about the class, not one account
        return nextId - 1;
    }

    @Override
    public String toString() {
        return "#" + id + " " + owner + ": " + balance;
    }
}
```

```java
BankAccount a = new BankAccount("Ann").deposit(50).deposit(25);
BankAccount b = new BankAccount("Bob", 100);

System.out.println(a);                            // #1 Ann: 75.0
System.out.println(b);                            // #2 Bob: 100.0
System.out.println(b.withdraw(500));              // false
System.out.println(BankAccount.accountsOpened()); // 2
```

| Design choice | Why |
|---|---|
| `nextId` is `static` | one counter shared by all accounts; an instance field would give every account ID 1 |
| `id` and `owner` are `final` | they must never change after construction, and the compiler enforces it |
| one main constructor, others use `this(…)` | validation is written once |
| `deposit` returns `this` | fluent chaining |
| `accountsOpened` is `static` | it describes the class, needs no particular account |
| `toString` overridden | printing shows content instead of `BankAccount@1b6d3586` |

---

## 12. Common Pitfalls

- **Declaring a reference and using it without `new`**: a local gives *might not have been initialized*; a field or `null` gives `NullPointerException`.
- **Expecting `new Point[3]` to create three points.** It creates three `null` references.
- **`x = x;` in a constructor or setter** when the parameter shadows the field. Write `this.x = x;`.
- **Adding a constructor with parameters and still calling `new ClassName()`**: the default constructor is gone. Declare the no-arg constructor explicitly if you need it.
- **Giving a constructor a return type** (`void Point()`): it becomes a method that `new` never calls.
- **`this(…)` not as the first statement** (before Java 25), in a method, or in a cycle of constructors.
- **Using instance fields or methods from a `static` method** (including `main`), or using `this` there.
- **Marking fields `static` to make the compiler happy**, so every object silently shares one value.
- **Accessing a static through a reference** (`obj.count`) and believing it is per object. It is one shared variable, and it even "works" on `null`.
- **Forgetting that a static field initializer runs once**, not per object, while an instance field initializer runs for every object.
- **Wrong assumptions about initialization order**: static blocks run once in source order on first use; instance initializers run before the constructor body; a later static initializer can overwrite what an earlier one did.
- **Reading a field from a method called during initialization**: it may still hold its default value, even if it is `final`.
- **Comparing objects with `==`** or relying on the inherited `equals` to compare content. Both compare identity until `equals` is overridden.
- **Printing an object and getting `ClassName@1b6d3586`**: override `toString()`.
- **Assigning an object to another variable and expecting a copy.** Both variables refer to the same object.
- **Relying on the garbage collector or `finalize` for cleanup.** Close resources explicitly.

---

## 13. Quick Reference — Non-Obvious Outcomes

| Code | Result | Why |
|---|---|---|
| `Point p; p.x = 1;` (local) | compile error | local not initialized |
| `Point p = null; p.x = 1;` | `NullPointerException` | no object |
| `new Point[3]` | 3 `null`s, 0 `Point` objects | only the array is created |
| `new Point()` after declaring only `Point(int, int)` | compile error | default constructor no longer generated |
| `public void Point() { … }` | a method, not a constructor | constructors have no return type |
| `Point() { return; }` | compiles | bare `return` allowed |
| `Point() { return this; }` | compile error | unexpected return value |
| `static Point() { }` / `final Point() { }` | compile error | modifier not allowed |
| `Point(int x) { x = x; }` | field stays `0` | parameter assigned to itself |
| `Point() { x = 1; this(2); }` | compile error (≤ Java 24) | `this(…)` must be first |
| `A() { this(1); }` + `A(int x) { this(); }` | compile error | recursive constructor invocation |
| `void f() { this(); }` | compile error | `this(…)` only in constructors |
| `this = other;` | compile error | cannot assign to `this` |
| `this` in a `static` method | compile error | no current object |
| instance field used in `static` method | compile error | non-static from static context |
| `void f() { static int n = 0; }` | compile error | no static locals |
| `Counter c = null; c.total` (static) | the value, no exception | compiled as `Counter.total` |
| `Counter c = null; c.mine` (instance) | `NullPointerException` | needs an object |
| `a.total = 5;` then `b.total` | `5` | one shared static variable |
| `final int id;` not set in one constructor | compile error | might not have been initialized |
| `final` field set in `A()` after `this(…)` already set it | compile error | might already have been assigned |
| `static final int K;` with no initializer or static block | compile error | must be assigned in class initialization |
| `int a = b + 1; int b = 5;` | compile error | illegal forward reference |
| `int a = getB(); int b = 5;` | `a == 0` | method reads default value |
| `int a = this.b + 1; int b = 5;` | `a == 1` | qualified name allowed, reads default |
| `final` field read by a method before assignment | its default value | readable before assignment through a method |
| `static A INST = new A(); static int count = 0;`, constructor does `count++` | `count == 0` | later initializer resets it |
| static block, instance block, constructor | static (once) → instance block → constructor body | initialization order |
| instance block + `A() { this(1); }` | block runs once per object | only in the non-delegating constructor |
| accessing `static final int X = 5` | no class initialization | compile-time constant inlined |
| accessing `static final Integer X = 5` | class initialized | not a constant |
| `new A[10]` | no class initialization | creating an array isn't a use of `A` |
| `System.out.println(p)` without `toString` | `Point@<hex>` | `Object.toString` |
| `new Point(1,2) == new Point(1,2)` | `false` | different objects |
| `p.equals(q)` without override | same as `p == q` | `Object.equals` is identity |
| `q = p; q.x = 9;` | `p.x == 9` | alias |
| constructor throws | variable keeps its old value | assignment never happens |

---

## 14. Practice — Trick Questions

**Q1.** Which lines fail to compile, and why?

```java
class Robot {
    int battery = 100;
    static int built = 0;

    Robot(int battery) { this.battery = battery; built++; }

    void charge()        { battery = 100; }                      // (1)
    static void reset()  { battery = 0; }                        // (2)
    static int count()   { return built; }                       // (3)
    static void report() { System.out.println(this.battery); }   // (4)
    void info()          { System.out.println(built); }          // (5)
}

Robot r1 = new Robot(50);                                        // (6)
Robot r2 = new Robot();                                          // (7)
```

> [!success]- Answer
> | Line | Compiles? | Reason |
> |---|---|---|
> | (1) | ✅ | instance method using an instance field |
> | (2) | ❌ | static method using an instance field |
> | (3) | ✅ | static method using a static field |
> | (4) | ❌ | no `this` in a static method |
> | (5) | ✅ | instance code may use static members |
> | (6) | ✅ | matches `Robot(int)` |
> | (7) | ❌ | the class declares a constructor, so there is no default `Robot()` |

**Q2.** What is printed?

```java
class Counter {
    static int total = 0;
    int mine = 0;
    Counter() { total++; mine++; }
}

Counter a = new Counter();
Counter b = new Counter();
Counter c = b;
c.mine++;
System.out.println(a.total + " " + a.mine + " " + b.mine + " " + Counter.total);
```

> [!success]- Answer
> `2 1 2 2`
>
> Two objects were created, so the single `total` is `2` (reading it as `a.total` makes no difference). `a.mine` is `1`. `c` is an alias for `b`, so `c.mine++` raises `b.mine` to `2`. No third object was created by `Counter c = b;`.

**Q3.** What is printed?

```java
class Point {
    int x, y;
    Point(int x, int y) { x = x; y = y; }
}

Point p = new Point(3, 4);
System.out.println(p.x + " " + p.y);
```

> [!success]- Answer
> `0 0`. Inside the constructor, `x` and `y` refer to the parameters, which shadow the fields. `x = x;` assigns the parameter to itself, and the fields keep their default `0`. The fix is `this.x = x; this.y = y;`.

**Q4.** What is printed?

```java
class Demo {
    static { System.out.println("S1"); }
    int v = init("F");
    { System.out.println("I"); }
    Demo()      { this(0); System.out.println("C0"); }
    Demo(int n) { System.out.println("C1"); }
    static { System.out.println("S2"); }
    static int init(String s) { System.out.println(s); return 1; }
}

System.out.println("start");
new Demo();
new Demo(5);
```

> [!success]- Answer
> ```
> start
> S1
> S2
> F
> I
> C1
> C0
> F
> I
> C1
> ```
> The class is initialized on the first `new`, after `start`: both static blocks, in source order, once. For each object, the field initializer and instance block run in source order, then the body of the non-delegating constructor `Demo(int)`. For the first object `Demo()` then finishes with `C0`. `F` and `I` appear once per object, not once per constructor.

**Q5.** What is printed, and which line throws?

```java
class Settings {
    static String theme = "dark";
    String user = "guest";
}

Settings s = null;
System.out.println(s.theme);   // (1)
System.out.println(s.user);    // (2)
```

> [!success]- Answer
> (1) prints `dark`: a static field accessed through a reference is compiled as `Settings.theme`, so the `null` value of `s` is never used. (2) throws `NullPointerException`: an instance field needs a real object.

**Q6.** What is printed?

```java
class Registry {
    static Registry DEFAULT = new Registry();
    static int size = 0;
    static int created;

    Registry() { size++; created++; }
}

System.out.println(Registry.size + " " + Registry.created);
```

> [!success]- Answer
> `0 1`. Static initializers run top to bottom. `DEFAULT = new Registry()` runs the constructor first, raising both fields from `0` to `1`. Then `size = 0` executes and resets `size`. `created` has no initializer, so it keeps `1`.

**Q7.** What is printed?

```java
class Point {
    int x, y;
    Point(int x, int y) { this.x = x; this.y = y; }
}

Point p = new Point(1, 2);
Point q = new Point(1, 2);
Point r = p;
r.x = 9;
System.out.println(p.x + " " + (p == q) + " " + (p == r) + " " + p.equals(q));
```

> [!success]- Answer
> `9 false true false`. `r` is an alias for `p`, so changing `r.x` changes `p.x`. `p` and `q` are two different objects, so `==` is `false`. `Point` does not override `equals`, so the inherited `Object.equals` also compares identity and gives `false`, even though the coordinates are equal.

**Q8.** How many `Point` objects exist after these lines, and what happens on the last one?

```java
Point[] pts = new Point[4];
pts[1] = new Point(1, 1);
pts[2] = pts[1];
pts[3].x = 5;
```

> [!success]- Answer
> **One** `Point` object (plus one array object). `new Point[4]` creates four `null` references, `pts[1]` gets the only `Point`, and `pts[2]` is an alias to the same object. `pts[3]` is still `null`, so the last line throws `NullPointerException`.

**Q9.** Which of these constructors compile?

```java
class A {
    final int x;
    A()              { this(1); }                       // (1)
    A(int v)         { x = v; }                         // (2)
    A(String s)      { }                                // (3)
    A(double d)      { this(1); x = 2; }                // (4)
    void A(long n)   { }                                // (5)
    A(char c)        { if (c == 'q') return; x = c; }   // (6)
}
```

> [!success]- Answer
> | Constructor | Compiles? | Reason |
> |---|---|---|
> | (1) | ✅ | `A(int)` assigns `x` |
> | (2) | ✅ | assigns the blank final once |
> | (3) | ❌ | `x` might not have been initialized |
> | (4) | ❌ | `x` might already have been assigned (by `A(int)`) |
> | (5) | ✅ | it is a **method** named `A` (it has a return type), so the final-field rule doesn't apply |
> | (6) | ❌ | on the `return` path `x` is never assigned: *might not have been initialized* |

**Q10.** What is printed?

```java
class F {
    int a = twiceB();
    int b = 5;
    int twiceB() { return b * 2; }
}

F f = new F();
System.out.println(f.a + " " + f.b);
```

> [!success]- Answer
> `0 5`. Field initializers run in source order. When `a` is initialized, `b`'s initializer hasn't run yet, so `twiceB()` sees the default `0` and returns `0`. Writing `int a = b * 2;` directly would not compile (*illegal forward reference*), but calling a method hides the forward reference from the compiler.

**Q11.** A student writes this to give each player a name. Two players are created as `new Player("Ann")` and `new Player("Bob")`, but both print `Bob`. Why, and how is it fixed?

```java
class Player {
    static String name;
    Player(String n) { name = n; }
    void print() { System.out.println(name); }
}
```

> [!success]- Answer
> `name` is `static`, so there is only **one** `name` for the whole class. The second constructor call overwrites it, and both objects print the same shared value. Remove `static`: each `Player` then has its own `name`. (A common origin of this bug is adding `static` to fix a *non-static … from a static context* error in `main`.)

---

## 15. Summary

- A **class** is a type that declares fields and methods. An **object** is an instance of it on the heap with its own copy of the instance fields. Every class implicitly extends `Object`.
- A class-type variable holds a **reference**. Only `new` creates objects. Assigning a reference creates an **alias**. `null` references throw `NullPointerException` on instance access. Unreachable objects are garbage collected, with no destructors.
- **Fields** get default values (unlike locals). A `final` field must be assigned exactly once: at its declaration, in an initializer, or in every constructor.
- **Instance methods** run on a specific object, available as `this`.
- **Constructors** have the class's name and no return type. They cannot be `static`/`final`/`abstract` and are not inherited. The compiler supplies a no-arg **default constructor** only if the class declares none. `this(…)` chains to another constructor and must be the first statement (before Java 25).
- **`this`** refers to the current object: it resolves field/parameter shadowing (`this.x = x`), calls other constructors (`this(…)`), and can be passed or returned (method chaining). It does not exist in static code.
- **Static** members belong to the class, with one shared copy. Static methods cannot use instance members without an explicit object. Statics accessed through a reference are compiled as `ClassName.member`, even when the reference is `null`. `static final` makes a shared constant.
- **Initialization order**: once per class, static initializers and blocks in source order on first active use; per object, defaults → (superclass constructor) → instance initializers and blocks in source order → constructor body. Code that reads fields early sees default values.
- Until overridden, `toString()` prints `ClassName@hash`, and `equals` is the same as `==` (identity).

## Related

- [[Java/00 - Syllabus|Syllabus]]
- Previous: [[Java/03 - Program Structure/02 - Strings|Strings]] · Next: [[Java/04 - Object-Oriented Programming/02 - Encapsulation|Encapsulation]]
- [[02 - Variables and Data Types|Variables and Data Types]]: instance/static variables, default values, blank finals, shadowing
- [[01 - Methods|Methods]]: declaring and overloading methods, pass-by-value, `static main`
- [[03 - Arrays|Arrays]]: arrays as objects, aliasing
- [[03 - Operators#7.3 `==` on References Compares Identity, Not Content|Operators § 7.3]]: `==` on references
- [[Java/04 - Object-Oriented Programming/02 - Encapsulation|Encapsulation]]: access modifiers, getters/setters, immutable classes
- [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]]: `extends`, `super`, overriding
- [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]: the `equals`/`hashCode`/`toString` contract
- [[Java/04 - Object-Oriented Programming/04 - Polymorphism|Polymorphism]]: dynamic dispatch, why static methods are not overridden
- [[Java/05 - Working with Data and Errors/02 - Generics|Generics]]: generic classes, why static members can't use `T`
