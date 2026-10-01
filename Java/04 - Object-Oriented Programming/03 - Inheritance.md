# Inheritance in Java

<span class="hl-blue">Inheritance</span> lets a new class (the **subclass**) be defined as an extension of an existing one (the **superclass**): it automatically gets the superclass's fields and methods, adds its own, and may replace (**override**) inherited methods with its own versions. This chapter covers `extends` and single inheritance, what is and isn't inherited, the exact rules for overriding, the `super` keyword, constructor chaining and the initialization order across a class hierarchy, why calling an overridable method from a constructor is dangerous, hiding (fields, static methods, private methods), `final` methods and classes, `protected` from the subclass's side, sealed classes, and when inheritance is the wrong tool.

It builds on [[Java/04 - Object-Oriented Programming/01 - Classes and Objects|Classes and Objects]] (constructors, `this(…)`, initialization order) and [[Java/04 - Object-Oriented Programming/02 - Encapsulation|Encapsulation]] (access levels). Using a superclass reference for a subclass object, and how Java picks the method to run at runtime, is the subject of [[Java/04 - Object-Oriented Programming/04 - Polymorphism|Polymorphism]]. Abstract classes and interfaces are in [[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]], and the `equals`/`hashCode` contract in [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]].

## Contents

- [[#1. Inheritance — The Idea|1. Inheritance — The Idea]]
- [[#2. `extends` and Single Inheritance|2. `extends` and Single Inheritance]]
- [[#3. Method Overriding|3. Method Overriding]]
- [[#4. The `super` Keyword|4. The `super` Keyword]]
- [[#5. Constructors and Inheritance|5. Constructors and Inheritance]]
- [[#6. Initialization Order Across a Hierarchy|6. Initialization Order Across a Hierarchy]]
- [[#7. Overridable Methods Called from Constructors|7. Overridable Methods Called from Constructors]]
- [[#8. What Is Not Overridden — Hiding|8. What Is Not Overridden — Hiding]]
- [[#9. `final` Methods and Classes|9. `final` Methods and Classes]]
- [[#10. `protected` and Inheritance|10. `protected` and Inheritance]]
- [[#11. Sealed Classes (Java 17+)|11. Sealed Classes (Java 17+)]]
- [[#12. Designing with Inheritance|12. Designing with Inheritance]]
- [[#13. Common Pitfalls|13. Common Pitfalls]]
- [[#14. Quick Reference — Non-Obvious Outcomes|14. Quick Reference — Non-Obvious Outcomes]]
- [[#15. Practice — Trick Questions|15. Practice — Trick Questions]]
- [[#16. Summary|16. Summary]]

---

## 1. Inheritance — The Idea

```java
class Animal {
    String name;
    void eat()   { System.out.println(name + " eats"); }
    void speak() { System.out.println("..."); }
}

class Dog extends Animal {                  // a Dog IS an Animal, plus more
    void fetch() { System.out.println(name + " fetches"); }   // new method
    @Override
    void speak() { System.out.println("Woof"); }              // replaces the inherited one
}

Dog d = new Dog();
d.name = "Rex";       // inherited field
d.eat();              // inherited method: Rex eats
d.fetch();            // own method:       Rex fetches
d.speak();            // overriding method: Woof
```

> [!note] Definitions
> - **Superclass** (parent, base class): the class being extended (`Animal`). **Subclass** (child, derived class): the class that extends it (`Dog`).
> - A subclass **inherits** the accessible members of its superclass, **adds** new members, and may **override** inherited instance methods.
> - **Is-a relationship**: every `Dog` is an `Animal`, so a `Dog` can be used wherever an `Animal` is expected (`Animal a = new Dog();`). This is what makes [[Java/04 - Object-Oriented Programming/04 - Polymorphism|polymorphism]] possible.
> - The **hierarchy** is the tree of classes formed by `extends`. A class's **ancestors** are its superclass, that class's superclass, and so on up to `Object`.

Inheritance is about **types** first and code reuse second: `Dog extends Animal` is a promise that a `Dog` can do everything an `Animal` can. When that promise isn't true, inheritance is the wrong tool ([[#12. Designing with Inheritance|§ 12]]).

---

## 2. `extends` and Single Inheritance

### 2.1 Syntax

```java
class Subclass extends Superclass { … }
class Subclass extends Superclass implements Interface1, Interface2 { … }   // extends comes first
```

- `extends` names exactly **one** class. `implements` (interfaces, see [[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]]) comes **after** it: `class X implements I extends P` is a compile error.
- A class with no `extends` implicitly extends `java.lang.Object`. Writing `class X extends Object { }` is legal but redundant.

### 2.2 One Direct Superclass

Java has **single inheritance** of classes: every class except `Object` has exactly one direct superclass.

| Code | Result |
|---|---|
| `class X extends A, B { }` | compile error (`'{' expected`): only one superclass |
| `class X extends Y { }` + `class Y extends X { }` | compile error: *cyclic inheritance involving X* |
| `class X extends String { }` | compile error: *cannot inherit from final String* ([[#9. `final` Methods and Classes|§ 9]]) |
| chain `C extends B`, `B extends A` | fine: `C` inherits from `B` **and** `A` (multilevel inheritance) |

> [!info]- Why no multiple inheritance of classes
> If `C` could extend both `A` and `B`, and both declared `void f()` or a field `x`, which one would `C` get? (This is the "diamond problem".) Java avoids it for state and constructors by allowing only one superclass. A class can implement **many interfaces**, and since Java 8 interfaces can carry `default` methods, so the method version of the question does arise, and Java resolves it with explicit rules ([[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]]).

### 2.3 What Is and Isn't Inherited

| Superclass member | Inherited by the subclass? |
|---|---|
| `public` and `protected` fields and methods | ✅ |
| package-private fields and methods | ✅ only if the subclass is in the **same package** |
| `private` fields and methods | ❌ not inherited: the subclass's code can't name them (but see below) |
| `static` fields and methods | ✅ accessible through the subclass (`Dog.count`), but **not overridden** ([[#8.2 Static Methods Are Hidden, Not Overridden|§ 8.2]]) |
| constructors | ❌ never ([[#5.1 Constructors Are Not Inherited|§ 5.1]]) |
| initializer blocks `{ }` / `static { }` | ❌ (they run as part of the superclass's own initialization) |
| nested classes | ✅ as members, under the same access rules |

> [!important] Key rule: private fields are not inherited, but they are there
> A `Dog` object **contains** every field declared in `Animal`, private ones included: the inherited methods of `Animal` use them. The `Dog` class's own code just can't access them by name. Access goes through inherited public/protected methods:
> ```java
> class Animal {
>     private int age;
>     int getAge() { return age; }
>     void birthday() { age++; }
> }
> class Dog extends Animal {
>     void test() {
>         birthday();                 // OK: inherited method changes the private field
>         System.out.println(getAge());   // OK: 1
>         System.out.println(age);    // compile error: age has private access in Animal
>     }
> }
> ```

---

## 3. Method Overriding

### 3.1 Overriding in Action

<span class="hl-blue">Overriding</span> means a subclass declares an instance method with the **same signature** as an inherited one, replacing it for objects of the subclass. Which version runs is decided at **runtime** by the object's actual class, not by the type of the variable:

```java
Animal a = new Dog();      // variable type Animal, object type Dog
a.speak();                 // Woof : the Dog's version runs
a.fetch();                 // compile error: the variable's type, Animal, has no fetch()
```

The declared type decides which methods can be **called**; the runtime type decides which override **runs**. The full mechanism is in [[Java/04 - Object-Oriented Programming/04 - Polymorphism|Polymorphism]]: declared vs. runtime type ([[Java/04 - Object-Oriented Programming/04 - Polymorphism#2. Declared Type vs. Runtime Type|§ 2]]), dynamic dispatch ([[Java/04 - Object-Oriented Programming/04 - Polymorphism#3. Dynamic Dispatch|§ 3]]), and casts and `instanceof` ([[Java/04 - Object-Oriented Programming/04 - Polymorphism#6. Downcasting and `instanceof`|§ 6]]).

> [!warning] Trick: a method called **inside** an inherited method still dispatches
> ```java
> class Shape {
>     double area()     { return 0; }
>     String describe() { return "shape " + area(); }      // calls area() on the current object
> }
> class Square extends Shape {
>     double side = 2;
>     @Override double area()     { return side * side; }
>     @Override String describe() { return "square, " + super.describe(); }
> }
>
> System.out.println(new Square().describe());   // square, shape 4.0
> ```
> `super.describe()` runs `Shape`'s `describe`, but the `area()` call **inside** it is an ordinary call on `this`, and `this` is a `Square`, so `Square.area()` runs. `super` only affects the one call it's written on.

### 3.2 The `@Override` Annotation

`@Override` tells the compiler "this method is meant to override something". If it doesn't, compilation fails:

```java
class Dog extends Animal {
    @Override void speek() { … }                 // compile error: method does not override or implement a method from a supertype
    @Override public String tostring() { … }     // same error: toString is spelled with a capital S
}
```

Without the annotation, both methods compile silently as **new** methods, and the inherited versions keep running. `@Override` is optional, but always use it: it turns a hard-to-find runtime bug into a compile error.

`@Override` is also a compile error on a `static` method (*static methods cannot be annotated with @Override*), on an inherited `private` method, and on a field (*annotation type not applicable to this kind of declaration*), because none of these can be overridden.

### 3.3 The Rules for a Valid Override

<span class="hl-yellow">Exam favourite.</span> Given a superclass method, the subclass method overrides it if it has the same **name** and the same **parameter types**. If it does, it must also follow these rules, or the code doesn't compile:

| Rule | Allowed | Compile error |
|---|---|---|
| **Parameter types**: exactly the same (after generics erasure) | `void f(int x)` → `void f(int y)` (names may differ) | a different parameter list is not an error, it's an **overload** ([[#3.4 Overriding vs. Overloading|§ 3.4]]) |
| **Return type**: the same, or a **subtype** for reference types (*covariant return*) | `Animal get()` → `Dog get()` | `int f()` → `long f()`: *return type long is not compatible with int* (primitives must match exactly) |
| **Access**: the same or **wider** | `protected` → `public` | `public` → package-private: *attempting to assign weaker access privileges; was public* |
| **Checked exceptions**: the same, fewer, or narrower (subclasses) | `throws IOException` → `throws FileNotFoundException`, or no `throws` at all | `throws IOException` → `throws Exception`; adding a checked exception to a method that declared none: *overridden method does not throw Exception* |
| **Unchecked exceptions** (`RuntimeException` and subclasses) | any, freely | — |
| superclass method is `final` | — | *overridden method is final* |
| `static` vs. instance | both `static` → **hiding**, not overriding ([[#8.2 Static Methods Are Hidden, Not Overridden|§ 8.2]]) | instance → `static`: *overriding method is static*; `static` → instance: *overridden method is static* |
| superclass method is `private` | a method with the same signature is simply a **new** method | — |

> [!tip] Why the rules make sense
> All of them follow from "a `Dog` must be usable wherever an `Animal` is expected". Code holding an `Animal` reference expects `get()` to return an `Animal` (a `Dog` is one), expects `speak()` to be callable (so it can't become less accessible), and only handles the checked exceptions `Animal`'s method declared (so the override can't throw new ones).

```java
class Animal {
    protected Animal reproduce() throws java.io.IOException { return new Animal(); }
}

class Dog extends Animal {
    @Override
    public Dog reproduce() { return new Dog(); }   // wider access, covariant return, no exceptions: all legal
}
```

A useful consequence of the covariant return: code that knows it has a `Dog` gets a `Dog` back without a cast (`Dog pup = dog.reproduce();`).

### 3.4 Overriding vs. Overloading

| | Overriding | Overloading |
|---|---|---|
| Where | subclass redefines an **inherited** method | same class (or subclass) adds a method with the same name |
| Parameters | **same** types | **different** types or number |
| Return type | same or covariant | anything |
| Decided | at **runtime**, by the object's class | at **compile time**, by the declared argument types ([[01 - Methods#7.2 How the Compiler Chooses an Overload|Methods § 7.2]]) |
| `@Override` | allowed (and recommended) | compile error |

> [!warning] Common mistake: overloading when you meant to override
> ```java
> class Point {
>     int x;
>     Point(int x) { this.x = x; }
>     public boolean equals(Point o) { return o != null && o.x == x; }   // OVERLOAD: parameter is Point, not Object
> }
>
> Point p1 = new Point(1), p2 = new Point(1);
> Object o2 = p2;
> p1.equals(p2)                          // true  : calls equals(Point)
> p1.equals(o2)                          // false : calls the inherited equals(Object), which is ==
> List.of(p1).contains(p2)               // false : collections call equals(Object)
> ```
> `Object.equals` takes an `Object`. A method taking `Point` is a second, unrelated method. With `@Override` the compiler would have rejected it. The correct version is in [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]].

### 3.5 Overriding `toString`

Every class inherits `toString()` from `Object`. Overriding it controls what `println` and string concatenation show:

```java
class Dog extends Animal {
    @Override
    public String toString() { return "Dog(" + name + ")"; }   // must be public: Object's is public
}
```

Writing it without `public` fails (*attempting to assign weaker access privileges; was public*). `equals` and `hashCode` follow in [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]].

---

## 4. The `super` Keyword

`super` refers to the **superclass part of the current object**. It has two uses: calling the superclass version of a method or field (`super.name`), and calling a superclass constructor (`super(…)`, [[#5. Constructors and Inheritance|§ 5]]).

### 4.1 Calling the Superclass Version

An override often **extends** the inherited behavior instead of replacing it:

```java
class Animal {
    void describe() { System.out.println("an animal"); }
}
class Dog extends Animal {
    @Override
    void describe() {
        super.describe();                       // run Animal's version first
        System.out.println("specifically a dog");
    }
}
```

Each `super.` call goes one level up, and that level can call `super.` again:

```java
class A { void f() { System.out.print("A "); } }
class B extends A { void f() { super.f(); System.out.print("B "); } }
class C extends B { void f() { super.f(); System.out.println("C"); } }

new C().f();      // A B C
```

`super.toString()` in an override calls `Object.toString`, which still prints the **runtime** class name, e.g. `Dog@1b6d3586`, not `Animal@…`: `Object.toString` uses `getClass()`, which is the object's actual class.

### 4.2 What `super` Can't Do

| Code | Result | Why |
|---|---|---|
| `super.super.f()` | compile error | only one level up; the grandparent's version is reachable only if the parent calls it |
| `super.f()` in a `static` method | compile error: *non-static variable super cannot be referenced from a static context* | no current object |
| `Animal a = super;` | compile error | `super` is not a value, unlike `this` |
| `super.privateMethod()` | compile error | private members aren't accessible |

---

## 5. Constructors and Inheritance

### 5.1 Constructors Are Not Inherited

A subclass does not get its superclass's constructors. Each class must declare (or receive by default) its own:

```java
class Animal {
    String name;
    Animal(String name) { this.name = name; }
}

class Dog extends Animal {
    Dog(String name) { super(name); }
}

new Dog("Rex");            // OK: Dog declares Dog(String)
```

If `Dog` declared only `Dog()`, then `new Dog("Rex")` would be a compile error, even though `Animal(String)` exists.

### 5.2 `super(…)` and the Implicit `super()`

Every constructor starts by running a constructor of the **direct superclass**, so the superclass part of the object is initialized before the subclass part. It does this in one of three ways:

| The constructor's first statement is… | What happens |
|---|---|
| `super(args)` | that superclass constructor runs |
| `this(args)` | another constructor of the same class runs first, and **it** eventually calls `super(…)` |
| anything else (or the body is empty) | the compiler inserts **`super();`**, a call to the superclass's **no-argument** constructor |

The compiler-generated **default constructor** ([[Java/04 - Object-Oriented Programming/01 - Classes and Objects#6.2 The Default Constructor|Classes and Objects § 6.2]]) is exactly `Dog() { super(); }`.

The chain continues all the way up: `Dog()` → `Animal()` → `Object()`. Constructors are **called** from the bottom up, and their bodies **finish** from the top down ([[#6. Initialization Order Across a Hierarchy|§ 6]]).

### 5.3 A Superclass Without a No-Arg Constructor

<span class="hl-yellow">Exam favourite.</span> If the superclass has **no** no-arg constructor (because it declares only constructors with parameters), the implicit `super()` has nothing to call:

```java
class Animal {
    Animal(String name) { … }              // the only constructor: no Animal() exists any more
}

class Dog extends Animal { }               // compile error: default constructor calls super()
class Cat extends Animal {
    Cat() { }                              // compile error: implicit super() → Animal() doesn't exist
}
class Cow extends Animal {
    Cow() { super("cow"); }                // OK
}
```

The error (*constructor Animal in class Animal cannot be applied to given types; required: String, found: no arguments*) is reported at the **subclass**, which is confusing because the subclass looks fine. The cause is in the superclass: adding a constructor with parameters removed its default constructor. Fix either side: give every subclass constructor an explicit `super(…)`, or add `Animal() { … }`.

### 5.4 Rules for `super(…)`

> [!important] Rules
> - `super(…)` must be the **first statement** of a constructor (before Java 25: see [[Java/04 - Object-Oriented Programming/01 - Classes and Objects#6.4 Constructor Chaining with `this(…)`|Classes and Objects § 6.4]] for the Java 25 relaxation). `int a = 1; super();` → *call to super must be first statement in constructor*.
> - A constructor has **either** `this(…)` **or** `super(…)`, never both.
> - It can appear only in a constructor.
> - Its arguments can't use the object being built: no instance fields (*cannot reference v before supertype constructor has been called*), no instance methods (*cannot reference this before supertype constructor has been called*). Parameters, constants, and **static** methods are fine: `super(normalize(name))` with a `static String normalize(String)`.

---

## 6. Initialization Order Across a Hierarchy

This extends the single-class order from [[Java/04 - Object-Oriented Programming/01 - Classes and Objects#9. Initialization Order|Classes and Objects § 9]] to several classes.

> [!important] Key rule: the order for `new Dog()`
> **Class initialization** (once, on first use): the **superclass first**: `Animal`'s static initializers, then `Dog`'s.
>
> **Object initialization** (every `new`):
> 1. All fields of the whole object, in every class of the chain, are set to default values.
> 2. `Dog()` is entered; its first action is `super(…)` (after any `this(…)` hops).
> 3. Recursively, `Animal()` calls `Object()`.
> 4. Back in `Animal`: its field initializers and instance blocks, in source order, then the rest of `Animal()`'s body.
> 5. Back in `Dog`: its field initializers and instance blocks, in source order, then the rest of `Dog()`'s body.

![[Inheritance - Constructor Chain.excalidraw|800]]

```java
class Animal {
    static { System.out.println("1 Animal static"); }
    { System.out.println("3 Animal instance block"); }
    Animal() { System.out.println("4 Animal ctor"); }
}

class Dog extends Animal {
    static { System.out.println("2 Dog static"); }
    String name = "Rex";
    { System.out.println("5 Dog instance block, name=" + name); }
    Dog() { super(); System.out.println("6 Dog ctor"); }
}

new Dog();
new Dog();
```

> [!example]- Output, step by step
> ```
> 1 Animal static
> 2 Dog static
> 3 Animal instance block
> 4 Animal ctor
> 5 Dog instance block, name=Rex
> 6 Dog ctor
> 3 Animal instance block
> 4 Animal ctor
> 5 Dog instance block, name=Rex
> 6 Dog ctor
> ```
> | Output | Reason |
> |---|---|
> | `1`, `2` | first use of `Dog` initializes its superclass first, then `Dog`: once only |
> | `3`, `4` | `Dog()` calls `super()`; `Animal`'s instance part runs completely before any of `Dog`'s |
> | `5` | only now does `Dog`'s field initializer `name = "Rex"` run, then its instance block |
> | `6` | the rest of `Dog()`'s body |
> | second object | no static blocks; the same instance sequence again |

> [!warning] Trick: using a static member through a subclass initializes only the declaring class
> ```java
> class SP { static int x = 1; static { System.out.println("SP init"); } }
> class SC extends SP { static { System.out.println("SC init"); } }
>
> System.out.println(SC.x);     // SP init, then 1 : "SC init" is never printed
> ```
> `x` is declared in `SP`, so reading `SC.x` is a use of `SP`, not of `SC`. Creating an `SC` object or calling a static method declared **in** `SC` would initialize both (`SP` first).

---

## 7. Overridable Methods Called from Constructors

<span class="hl-yellow">One of the nastiest traps in Java.</span> If a superclass constructor calls a method that a subclass overrides, the **subclass's version** runs, at step 4 above: before the subclass's field initializers and constructor body have run. The override sees the subclass's fields at their **default values**:

```java
class Base {
    Base() { describe(); }                     // calls an overridable method
    void describe() { System.out.println("Base"); }
}

class Derived extends Base {
    String label = "derived";
    final int m = Integer.parseInt("7");       // final, but not a compile-time constant
    final int k = 5;                           // compile-time constant
    Derived() { describe(); }

    @Override
    void describe() { System.out.println("label=" + label + " m=" + m + " k=" + k); }
}

new Derived();
// label=null m=0 k=5      ← from Base(): Derived's fields not initialized yet
// label=derived m=7 k=5   ← from Derived()
```

- `label` is `null` and `m` is `0`, even though `m` is `final`: a `final` field can be observed with two different values ([[Java/04 - Object-Oriented Programming/01 - Classes and Objects#9.3 Forward References|Classes and Objects § 9.3]]).
- `k` already shows `5`, because a `final` field initialized with a **constant expression** is a compile-time constant: the compiler replaces `k` with `5` everywhere, so no field read happens.
- With an object field, the same pattern gives a `NullPointerException` inside the override (`label.length()`).

> [!important] Key rule: constructors should only call methods that can't be overridden
> Call only `private`, `static`, or `final` methods from a constructor, or make the class `final`. The same applies to setters called from constructors for validation ([[Java/04 - Object-Oriented Programming/02 - Encapsulation#5.2 Validation in Setters (and Constructors)|Encapsulation § 5.2]]): use a `private` validation helper, or make the setter `final`.

---

## 8. What Is Not Overridden — Hiding

Only **accessible instance methods** are overridden. Fields, static methods, and private methods with the same name are **hidden** or simply **unrelated**: the version used is fixed at compile time.

![[Inheritance - Fields Hide, Methods Override.excalidraw|800]]

### 8.1 Fields Are Hidden, Not Overridden

A field in the subclass with the same name as a superclass field doesn't replace it. The object then has **two** fields, and which one an expression uses depends on the **declared type** of the reference:

```java
class P {
    String name = "parent";
    String getName() { return name; }        // always P's field: written in P
    String who()     { return name; }        // not overridden in C
}

class C extends P {
    String name = "child";                   // a SECOND field, hiding P's
    @Override String getName() { return name; }   // C's field
}

P p = new C();
p.name            // "parent" : declared type P
((C) p).name      // "child"  : declared type C
p.getName()       // "child"  : method overridden, runtime type C
p.who()           // "parent" : P's method sees P's field
```

Inside `C`, the hidden field is still reachable as `super.name`. <span class="hl-red">Hiding fields is almost always a mistake</span>: keep fields `private` and expose them through methods, which do behave polymorphically.

### 8.2 Static Methods Are Hidden, Not Overridden

A static method with the same signature as a superclass static method **hides** it. There is no dispatch: the **declared type** decides, even when the call is written on an object reference:

```java
class P { static String kind() { return "P"; } }
class C extends P { static String kind() { return "C"; } }

P p = new C();
p.kind()          // "P" : compiled as P.kind(), the object is never looked at
C.kind()          // "C"
```

Hiding follows the same return-type, access, and exception rules as overriding, and `@Override` on a static method is a compile error. Mixing static and instance with the same signature is a compile error in either direction ([[#3.3 The Rules for a Valid Override|§ 3.3]]). See also [[Java/04 - Object-Oriented Programming/01 - Classes and Objects#8.4 Accessing Static Members Through a Reference|Classes and Objects § 8.4]].

### 8.3 Private Methods Are Not Overridden

A subclass can't see a `private` method, so a method with the same signature in the subclass is a **new, unrelated** method. Code in the superclass keeps calling its own:

```java
class Q {
    void call() { helper(); }
    private void helper() { System.out.println("Q.helper"); }
}

class R extends Q {
    void helper() { System.out.println("R.helper"); }    // NOT an override
}

new R().call();     // Q.helper
```

If `Q.helper` were not `private`, `R.helper` would override it and the same call would print `R.helper`. This is also why `@Override` on `R.helper` would be a compile error here.

### 8.4 Package-Private Methods Across Packages

A package-private method is only inherited within its package. A subclass in **another** package that declares the same method doesn't override it:

```java
package a;
public class Base {
    void hook() { System.out.println("Base.hook"); }   // package-private
    public void run() { hook(); }
}
```

```java
package b;
public class Sub extends a.Base {
    void hook() { System.out.println("Sub.hook"); }    // NOT an override: Base.hook is invisible here
}

new Sub().run();      // Base.hook
```

Making `hook` `protected` (or `public`) in `Base` turns `Sub.hook` into an override, and `run()` would then print `Sub.hook`.

---

## 9. `final` Methods and Classes

`final` has a different meaning on each kind of declaration:

| On | Meaning |
|---|---|
| a variable or field | can't be **reassigned** ([[02 - Variables and Data Types#7. Constants (`final`)|Variables and Data Types § 7]]) |
| a method | can't be **overridden** (or hidden): *overridden method is final* |
| a class | can't be **extended**: *cannot inherit from final X* |

```java
class Account {
    final void audit() { … }          // subclasses inherit it but can't replace it
}

final class Money { … }               // no subclasses at all
class Euro extends Money { }          // compile error: cannot inherit from final Money
```

When to use them:
- **`final` class**: immutable value classes (`String`, `Integer`, `LocalDate`, see [[Java/04 - Object-Oriented Programming/02 - Encapsulation#7.3 Why the Class Should Be `final`|Encapsulation § 7.3]]), utility classes, and any class not designed for extension.
- **`final` method**: a method whose behavior other methods rely on (template steps, security checks), or one called from a constructor ([[#7. Overridable Methods Called from Constructors|§ 7]]).

> [!info]- Small print about `final`
> - `private` methods are implicitly unoverridable, so `private final` is redundant. `static` methods can be `final` too (it prevents hiding).
> - A `final` method **can be overloaded**: `final void f()` and `void f(int x)` coexist fine.
> - An overriding method may itself be declared `final`, stopping further overriding below it.
> - `abstract` and `final` together (on a class or a method) are a compile error: one requires a subclass, the other forbids it ([[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]]).
> - Records and enums are implicitly `final` (enums with constant-specific bodies are a special case, see [[Java/04 - Object-Oriented Programming/07 - Enums|Enums]]).

---

## 10. `protected` and Inheritance

`protected` exists for inheritance: it opens a member to subclasses (and the whole package). The access table is in [[Java/04 - Object-Oriented Programming/02 - Encapsulation#3.5 `protected`|Encapsulation § 3.5]]. From the subclass's side, the rules that matter are:

- In the same package, `protected` behaves like package-private: anything goes.
- In a **different** package, the subclass can use an inherited `protected` instance member only on **its own type**: `this.x`, `super.x`, `otherDog.x` with `otherDog` a `Dog`. Through an `Animal` reference it's a compile error, even inside `Dog`.
- A `protected` constructor can be called from a subclass in another package **only** through `super(…)`, never with `new`.
- An override may **widen** `protected` to `public`, but not narrow it ([[#3.3 The Rules for a Valid Override|§ 3.3]]).

> [!tip] Prefer `private` fields with `protected` methods
> A `protected` field is part of the class's contract with every future subclass: it can never be renamed or validated again without breaking them. Usually it's better to keep the field `private` and give subclasses a `protected` getter, or a `protected` method that does the work, so the superclass keeps its invariants ([[Java/04 - Object-Oriented Programming/02 - Encapsulation|Encapsulation]]).

---

## 11. Sealed Classes (Java 17+)

A <span class="hl-blue">sealed class</span> lists exactly which classes may extend it. It sits between "anyone may extend this" and `final` ("no one may"):

```java
sealed class Shape permits Circle, Square, Polygon { }

final class Circle extends Shape { }                         // no further subclasses
sealed class Square extends Shape permits Cube { }           // restricted again
final class Cube extends Square { }
non-sealed class Polygon extends Shape { }                   // open again: anyone may extend Polygon
class Triangle extends Polygon { }                           // fine
```

> [!important] Rules
> - Every permitted subclass must **directly extend** the sealed class, and must declare exactly one of **`final`**, **`sealed`**, or **`non-sealed`**. Leaving it out → *sealed, non-sealed or final modifiers expected*.
> - A class not in the `permits` list can't extend it → *class is not allowed to extend sealed class: Shape (as it is not listed in its permits clause)*.
> - If the sealed class and all its subclasses are in the **same file**, `permits` may be omitted, and the compiler infers the list.
> - A sealed class must have at least one subclass (*sealed class must have subclasses*), and listing a class in `permits` that doesn't extend it is an error (*invalid permits clause*).
> - Permitted subclasses must be in the same package (or, in a named module, the same module).
> - `final sealed` is a compile error: *illegal combination of modifiers*.

Why seal a class: it documents a **closed set** of variants (a `Shape` is a circle, a square, or a polygon), and it lets the compiler check that code handles all of them. With pattern matching for `switch` (Java 21), a `switch` over a sealed type needs no `default` if every permitted subclass is covered ([[Java/04 - Object-Oriented Programming/04 - Polymorphism#8. Pattern Matching in `switch` over Sealed Types (Java 21)|Polymorphism § 8]]). Interfaces can be sealed too ([[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]]).

---

## 12. Designing with Inheritance

### 12.1 Is-a vs. Has-a

Use inheritance only when the subclass **is** a kind of the superclass, everywhere the superclass is used. Otherwise use a field (**composition**, a *has-a* relationship):

| Relationship | Example | Use |
|---|---|---|
| is-a | a `Dog` is an `Animal`; a `SavingsAccount` is an `Account` | `extends` |
| has-a | a `Car` has an `Engine`; a `Team` has `Player`s | a field |
| "uses some code of" | a `Stack` that wants `ArrayList`'s storage | a field, **not** `extends` |

> [!warning] Common mistake: inheriting to reuse code
> `java.util.Stack extends Vector` is the textbook example. Because a `Stack` *is* a `Vector`, it inherits `add(index, e)`, `remove(index)`, and `get(index)`, so any caller can insert into the middle of a "stack" and break its last-in-first-out behavior. A stack **has** storage; it isn't a list. (Use `ArrayDeque` instead, see [[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]].)

### 12.2 The Fragile Base Class Problem

A subclass depends on **how** its superclass is implemented, not only on what it promises. Overriding a method can break when the superclass calls its own methods internally:

```java
class CountingSet<E> extends HashSet<E> {
    int added = 0;

    @Override public boolean add(E e) {
        added++;
        return super.add(e);
    }
    @Override public boolean addAll(Collection<? extends E> c) {
        added += c.size();
        return super.addAll(c);           // HashSet's addAll calls add() for each element...
    }
}

CountingSet<String> s = new CountingSet<>();
s.addAll(List.of("a", "b", "c"));
System.out.println(s.added);              // 6, not 3: each element counted twice
```

`HashSet.addAll` (inherited from `AbstractCollection`) calls `add` for each element, and that call dispatches to the overridden `add`. Nothing in `HashSet`'s public API says so, and a future JDK could change it. The subclass is fragile because it relies on an implementation detail.

### 12.3 Composition over Inheritance

The robust alternative is to **wrap** an object instead of extending its class, and forward calls to it:

```java
class CountingSet<E> {
    private final Set<E> inner = new HashSet<>();    // has-a
    private int added = 0;

    public boolean add(E e) { added++; return inner.add(e); }
    public boolean addAll(Collection<? extends E> c) {
        added += c.size();
        return inner.addAll(c);          // inner's internal add() calls don't come back here
    }
    public int added() { return added; }
}
```

Now `inner.addAll` calling `inner.add` internally can't reach the wrapper's `add`, so the count is correct whatever `HashSet` does inside. The price is writing forwarding methods (usually by implementing the `Set` interface).

> [!tip] Design for inheritance, or forbid it
> A class meant to be extended should document which of its methods call which overridable methods, and its constructors must not call overridable methods. A class not designed for this should be `final`. "Design and document for inheritance or else prohibit it" (Joshua Bloch, *Effective Java*).

---

## 13. Common Pitfalls

- **Expecting constructors to be inherited**: `new Dog("Rex")` needs a `Dog(String)` constructor in `Dog`.
- **A superclass with only parameterized constructors**: subclasses relying on the implicit `super()` (including the default constructor) don't compile. The error points at the subclass.
- **`super(…)` not first**, combined with `this(…)`, or with arguments that use instance fields or instance methods.
- **Calling an overridable method from a constructor**: the override sees the subclass's fields at default values (`null`, `0`), even `final` ones.
- **Forgetting `@Override`**, so a typo (`tostring`, `speek`) or a wrong parameter type (`equals(Point)`) silently creates a new method.
- **Overloading instead of overriding**, especially `equals(MyClass)` instead of `equals(Object)`.
- **Narrowing access** in an override (`toString()` without `public`), changing a primitive return type, or adding a checked exception.
- **Expecting fields to be polymorphic**: a field with the same name in the subclass hides the superclass's field, and the declared type decides which one is used.
- **Expecting static methods to dispatch**: `p.kind()` uses the declared type.
- **"Overriding" a private method**, or a package-private one from another package: the superclass keeps calling its own version.
- **`super.super.f()`**, or `super` in a static method.
- **Thinking `super.describe()` makes all calls inside it use the superclass versions.** Calls on `this` inside it still dispatch to overrides.
- **Assuming `SC.x` initializes `SC`** when `x` is declared in its superclass.
- **Using `extends` for code reuse** where there's no is-a relationship (`Stack extends Vector`), and overriding methods that the superclass calls internally (`addAll` → `add`).
- **Sealed classes**: forgetting `final`/`sealed`/`non-sealed` on a permitted subclass, or extending a sealed class without being listed.

---

## 14. Quick Reference — Non-Obvious Outcomes

| Code | Result | Why |
|---|---|---|
| `class X extends A, B` | compile error | single inheritance |
| `class X implements I extends P` | compile error | `extends` must come first |
| `class X extends Y`, `class Y extends X` | compile error | cyclic inheritance |
| `class X extends String` | compile error | `String` is `final` |
| subclass code reads superclass `private` field | compile error | private isn't inherited (but the field exists) |
| `new Dog("Rex")` with only `Animal(String)` declared | compile error | constructors aren't inherited |
| superclass has only `Animal(String)`; `class Dog extends Animal { }` | compile error at `Dog` | implicit `super()` has no target |
| `Dog() { int a = 1; super(); }` | compile error (≤ Java 24) | `super(…)` must be first |
| `Dog() { this(1); super(); }` | compile error | only one of `this(…)`/`super(…)` |
| `super(field)` / `super(instanceMethod())` | compile error | object not constructed yet |
| `super(staticMethod())` | compiles | no object needed |
| override `Animal get()` with `Dog get()` | compiles | covariant return |
| override `int f()` with `long f()` | compile error | primitive return must match |
| override `public` with package-private | compile error | weaker access |
| override `protected` with `public` | compiles | wider access is fine |
| override adds `throws Exception` | compile error | broader checked exception |
| override adds `throws RuntimeException` | compiles | unchecked exceptions are free |
| override drops the `throws` clause | compiles | fewer exceptions is fine |
| override a `final` method | compile error | overridden method is final |
| instance method "overrides" a static one | compile error | overridden method is static |
| static method "overrides" an instance one | compile error | overriding method is static |
| `@Override` on a typo (`tostring`) | compile error | doesn't override anything |
| `@Override` on a static method | compile error | static methods can't be overridden |
| `@Override` on a field | compile error | not applicable |
| `public boolean equals(Point o)` | an overload | `Object.equals` takes `Object` |
| `toString()` without `public` | compile error | narrows `Object`'s `public` |
| `super.super.f()` | compile error | one level only |
| `super.f()` in a `static` method | compile error | no current object |
| `super.describe()` that calls `area()` | runs the **subclass's** `area()` | the inner call dispatches on `this` |
| `super.toString()` in `Dog` | `Dog@…` | `getClass()` is the runtime class |
| `new Dog()` order | `Animal` static → `Dog` static → `Animal` init + ctor → `Dog` init + ctor | superclass first |
| `SC.x` with `x` declared in `SP` | only `SP` is initialized | static member of `SP` |
| superclass constructor calls overridden method | subclass fields seen as `0`/`null` | not initialized yet |
| … and the subclass field is `final int k = 5` | `5` | compile-time constant, inlined |
| `P p = new C(); p.name` (field in both) | `P`'s field | fields aren't polymorphic |
| `P p = new C(); p.staticM()` | `P`'s static method | hiding, no dispatch |
| superclass calls its `private helper()`, subclass declares `helper()` | superclass's helper runs | private methods aren't overridden |
| subclass in another package redeclares a package-private method | superclass's version runs | not inherited, so not overridden |
| `CountingSet extends HashSet`, `addAll(3 items)` | count 6 | `addAll` calls overridden `add` |
| permitted subclass without `final`/`sealed`/`non-sealed` | compile error | modifier required |
| unlisted class extends a sealed class | compile error | not in `permits` |
| `final sealed class` | compile error | illegal combination |

---

## 15. Practice — Trick Questions

**Q1.** What is printed?

```java
class A {
    static { System.out.print("As "); }
    { System.out.print("Ai "); }
    A() { System.out.print("Ac "); }
}
class B extends A {
    static { System.out.print("Bs "); }
    { System.out.print("Bi "); }
    B() { System.out.print("Bc "); }
}

new B();
new B();
```

> [!success]- Answer
> `As Bs Ai Ac Bi Bc Ai Ac Bi Bc`
>
> Class initialization runs once, superclass first (`As Bs`). For each object, `A`'s instance block and constructor body run completely before `B`'s instance block and constructor body. The second `new B()` repeats only the instance part.

**Q2.** What is printed?

```java
class Base {
    Base() { print(); }
    void print() { System.out.println("Base"); }
}
class Sub extends Base {
    int x = 10;
    String s = "hi";
    final int c = 3;
    Sub() { print(); }
    @Override void print() { System.out.println(x + " " + s + " " + c); }
}

new Sub();
```

> [!success]- Answer
> ```
> 0 null 3
> 10 hi 3
> ```
> `Base()` runs before `Sub`'s field initializers, but `print()` is overridden, so `Sub.print` runs and sees `x` and `s` at their defaults. `c` is a compile-time constant (`final` + constant initializer), so the compiler inlined `3`. After `super()` returns, `Sub`'s fields are initialized, and the second call sees them.

**Q3.** `P` is below. Which of the subclass methods compile? (Consider each one alone in `class C extends P`.)

```java
class P {
    Object get() { return null; }
    protected void a() { }
    void b() throws IOException { }
    int n() { return 0; }
    static void s() { }
    final void f() { }
    public void g() { }
}
```

```java
String get() { return ""; }                         // (1)
void a() { }                                         // (2)
void b() throws FileNotFoundException { }            // (3)
long n() { return 0; }                               // (4)
void s() { }                                         // (5)
void f() { }                                         // (6)
public void g() throws IllegalStateException { }     // (7)
void b() { }                                         // (8)
```

> [!success]- Answer
> | Method | Compiles? | Reason |
> |---|---|---|
> | (1) | ✅ | covariant return: `String` is a subtype of `Object` |
> | (2) | ❌ | narrows `protected` to package-private |
> | (3) | ✅ | `FileNotFoundException` is a subclass of `IOException` |
> | (4) | ❌ | primitive return types must match exactly |
> | (5) | ❌ | an instance method can't override a static one |
> | (6) | ❌ | `f` is `final` |
> | (7) | ✅ | unchecked exceptions are always allowed |
> | (8) | ✅ | throwing fewer checked exceptions is allowed |

**Q4.** What is printed?

```java
class P {
    String name = "P";
    static String id() { return "P"; }
    String show() { return name; }
}
class C extends P {
    String name = "C";
    static String id() { return "C"; }
    @Override String show() { return name; }
}

P p = new C();
System.out.println(p.name + " " + p.id() + " " + p.show() + " " + ((C) p).name);
```

> [!success]- Answer
> `P P C C`
>
> | Expression | Value | Why |
> |---|---|---|
> | `p.name` | `P` | fields are chosen by the declared type (`P`) |
> | `p.id()` | `P` | static methods are hidden, chosen by the declared type |
> | `p.show()` | `C` | overridden instance method: runtime type `C`, and `C.show` reads `C`'s field |
> | `((C) p).name` | `C` | the cast changes the declared type |

**Q5.** `class P { P(String s) { } }`. Which subclasses compile?

```java
class A extends P { }                                         // (A)
class B extends P { B() { super("b"); } }                     // (B)
class C extends P { C(String s) { } }                         // (C)
class D extends P { D() { this("x"); } D(String s) { super(s); } }   // (D)
```

> [!success]- Answer
> | Class | Compiles? | Reason |
> |---|---|---|
> | (A) | ❌ | the default constructor `A() { super(); }` needs `P()`, which doesn't exist |
> | (B) | ✅ | explicit `super("b")` |
> | (C) | ❌ | having a `String` parameter doesn't matter: the body has no `super(…)`, so `super()` is inserted |
> | (D) | ✅ | `D()` delegates to `D(String)`, which calls `super(s)` |

**Q6.** What is printed? What changes if `helper` in `Q` is made package-private (no modifier)?

```java
class Q {
    void call() { helper(); }
    private void helper() { System.out.println("Q.helper"); }
}
class R extends Q {
    void helper() { System.out.println("R.helper"); }
}

new R().call();
```

> [!success]- Answer
> `Q.helper`. A private method isn't inherited, so `R.helper` doesn't override it, and `Q.call` calls `Q`'s own `helper`. If `Q.helper` is package-private (and `R` is in the same package), `R.helper` **overrides** it, and the output becomes `R.helper`.

**Q7.** What is printed?

```java
class Point {
    int x;
    Point(int x) { this.x = x; }
    public boolean equals(Point o) { return o != null && o.x == x; }
}

Point p1 = new Point(1), p2 = new Point(1);
Object o2 = p2;
System.out.println(p1.equals(p2) + " " + p1.equals(o2) + " " + List.of(p1).contains(p2));
```

> [!success]- Answer
> `true false false`. `equals(Point)` **overloads** `Object.equals(Object)`, it doesn't override it. With a `Point` argument, the compiler picks `equals(Point)`. With an `Object` argument, only `equals(Object)` applies, which is still `Object`'s identity check. `contains` calls `equals(Object)`. Adding `@Override` would have caught this as a compile error.

**Q8.** What is printed?

```java
class Shape {
    double area() { return 0; }
    String describe() { return "shape " + area(); }
}
class Square extends Shape {
    double side = 2;
    @Override double area() { return side * side; }
    @Override String describe() { return "square, " + super.describe(); }
}

System.out.println(new Square().describe());
```

> [!success]- Answer
> `square, shape 4.0`. `super.describe()` runs `Shape.describe`, but inside it `area()` is called on `this`, which is a `Square`, so `Square.area()` runs and returns `4.0`. (The object is fully constructed here, so `side` is already `2`.)

**Q9.** What is printed?

```java
class A { void f() { System.out.print("A "); } }
class B extends A { void f() { super.f(); System.out.print("B "); } }
class C extends B { void f() { super.f(); System.out.println("C"); } }

A obj = new C();
obj.f();
```

> [!success]- Answer
> `A B C`. The object is a `C`, so `C.f` runs. Each `super.f()` goes up exactly one level, and the output appears in top-down order because each method prints after its `super` call returns.

**Q10.** What is printed?

```java
class SP { static int x = 1; static { System.out.println("SP init"); } }
class SC extends SP { static { System.out.println("SC init"); } }

System.out.println(SC.x);
```

> [!success]- Answer
> ```
> SP init
> 1
> ```
> `x` is declared in `SP`. Accessing it through the name `SC` is still a use of `SP`'s field, so only `SP` is initialized. `SC init` is never printed.

**Q11.** A programmer writes `CountingSet extends HashSet` with overridden `add` (counts 1) and `addAll` (counts `c.size()`, then calls `super.addAll(c)`). After `addAll(List.of("a", "b", "c"))`, the count is 6. Why, and what is the robust fix?

> [!success]- Answer
> `HashSet.addAll` is implemented by calling `add` for each element, and those calls dispatch to the overridden `add`, so each element is counted twice (3 in `addAll` + 3 in `add`). Removing the count from `addAll` would "fix" it only as long as the JDK keeps that implementation detail. The robust fix is **composition**: keep a private `HashSet` field and forward to it, so the inner set's internal calls never reach the counting code ([[#12.3 Composition over Inheritance|§ 12.3]]).

**Q12.** Which lines compile? (Java 17.)

```java
sealed class Vehicle permits Car, Truck, Bike { }
final class Car extends Vehicle { }            // (1)
class Truck extends Vehicle { }                // (2)
non-sealed class Bike extends Vehicle { }      // (3)
class MountainBike extends Bike { }            // (4)
final class Bus extends Vehicle { }            // (5)
```

> [!success]- Answer
> | Line | Compiles? | Reason |
> |---|---|---|
> | (1) | ✅ | permitted and `final` |
> | (2) | ❌ | a permitted subclass must say `final`, `sealed`, or `non-sealed` |
> | (3) | ✅ | permitted and `non-sealed` |
> | (4) | ✅ | `Bike` is `non-sealed`, so anyone may extend it |
> | (5) | ❌ | `Bus` isn't in the `permits` list |

---

## 16. Summary

- `class Sub extends Super`: the subclass inherits accessible fields and methods, adds its own, and may override instance methods. Java has **single inheritance** of classes; every class ultimately extends `Object`.
- **Not inherited**: constructors, `private` members (they still exist in the object), and package-private members across packages. Static members are inherited but not overridden.
- **Overriding** needs the same name and parameter types; the return type may be covariant (references only); access may only widen; checked exceptions may only narrow; `final` methods can't be overridden; static and instance methods can't override each other. Always use **`@Override`**.
- Overriding is decided at **runtime** by the object's class; overloading at **compile time** by the declared argument types. `equals(MyClass)` is an overload.
- **`super.m()`** calls the superclass's version, one level up only; calls inside it on `this` still dispatch to overrides.
- Every constructor starts with **`super(…)`** (explicit or the implicit `super()`), or with `this(…)`. A superclass without a no-arg constructor forces explicit `super(…)` calls in subclasses.
- **Initialization order**: superclass static init, subclass static init (once); then per object, superclass field initializers and constructor body, then the subclass's.
- **Never call overridable methods from a constructor**: the override sees uninitialized subclass fields.
- **Fields and static methods are hidden, not overridden**: the declared type decides. Private (and cross-package package-private) methods aren't overridden at all.
- **`final`** methods can't be overridden, `final` classes can't be extended. **Sealed** classes (Java 17) permit only listed subclasses, each `final`, `sealed`, or `non-sealed`.
- Inherit only for real **is-a** relationships. Overriding methods that the superclass calls internally makes subclasses **fragile**; **composition** (wrap and forward) avoids it.

## Related

- [[00 - Syllabus|Syllabus]]
- Previous: [[Java/04 - Object-Oriented Programming/02 - Encapsulation|Encapsulation]] · Next: [[Java/04 - Object-Oriented Programming/04 - Polymorphism|Polymorphism]]
- [[Java/04 - Object-Oriented Programming/01 - Classes and Objects|Classes and Objects]]: constructors, the default constructor, `this(…)`, single-class initialization order
- [[Java/04 - Object-Oriented Programming/02 - Encapsulation|Encapsulation]]: access levels and `protected`, immutable classes and why they're `final`
- [[01 - Methods#7. Method Overloading|Methods § 7]]: overloading, which is resolved at compile time
- [[Java/04 - Object-Oriented Programming/04 - Polymorphism|Polymorphism]]: superclass references, dynamic dispatch, casting, `instanceof`
- [[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]]: abstract classes, interfaces, `default` methods, sealed interfaces
- [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]: overriding `equals`, `hashCode`, and `toString` correctly
- [[Java/05 - Working with Data and Errors/01 - Exception Handling|Exception Handling]]: checked vs. unchecked exceptions, the `throws` rules for overrides
- [[Java/05 - Working with Data and Errors/02 - Generics|Generics]]: subtyping with generic types, why `List<Dog>` isn't a `List<Animal>`
