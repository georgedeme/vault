# Polymorphism in Java

<span class="hl-blue">Polymorphism</span> ("many forms") means one piece of code can work with objects of many different classes, and each object responds in its own way. In Java this comes from two things working together: a supertype reference can point to a subtype object, and the overriding method of the object's actual class is chosen **at runtime** (*dynamic dispatch*). This chapter covers declared vs. runtime types, how dynamic dispatch works and what it doesn't apply to, how overloading (compile time) and overriding (runtime) combine in a single call, upcasting and downcasting, `instanceof` and pattern matching for `instanceof`, pattern matching in `switch` over sealed types, and how to design with polymorphism instead of `instanceof` chains.

It builds on [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]] (overriding, `super`, hiding, sealed classes), [[01 - Methods#7.2 How the Compiler Chooses an Overload|Methods § 7.2]] (overload resolution), and [[Java/01 - Foundations/04 - Type Casting#7. Reference (Object) Casting|Type Casting § 7]] (the basics of reference casts). Interfaces, the other main source of supertypes, are in [[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]], and polymorphism with generic types (`List<Dog>` vs. `List<Animal>`) is in [[Java/05 - Working with Data and Errors/02 - Generics#5. Generics Are Invariant|Generics § 5]].

## Contents

- [[#1. Polymorphism — The Idea|1. Polymorphism — The Idea]]
- [[#2. Declared Type vs. Runtime Type|2. Declared Type vs. Runtime Type]]
- [[#3. Dynamic Dispatch|3. Dynamic Dispatch]]
- [[#4. Overloading and Overriding in the Same Call|4. Overloading and Overriding in the Same Call]]
- [[#5. Upcasting|5. Upcasting]]
- [[#6. Downcasting and `instanceof`|6. Downcasting and `instanceof`]]
- [[#7. Pattern Matching for `instanceof` (Java 16+)|7. Pattern Matching for `instanceof` (Java 16+)]]
- [[#8. Pattern Matching in `switch` over Sealed Types (Java 21)|8. Pattern Matching in `switch` over Sealed Types (Java 21)]]
- [[#9. Designing with Polymorphism|9. Designing with Polymorphism]]
- [[#10. Where Polymorphism Stops|10. Where Polymorphism Stops]]
- [[#11. Common Pitfalls|11. Common Pitfalls]]
- [[#12. Quick Reference — Non-Obvious Outcomes|12. Quick Reference — Non-Obvious Outcomes]]
- [[#13. Practice — Trick Questions|13. Practice — Trick Questions]]
- [[#14. Summary|14. Summary]]

---

## 1. Polymorphism — The Idea

The examples in this chapter use this small hierarchy:

```java
class Animal {
    String name;
    void eat()   { System.out.println(name + " eats"); }
    void speak() { System.out.println("..."); }
}

class Dog extends Animal {
    @Override void speak() { System.out.println("Woof"); }
    void fetch() { System.out.println(name + " fetches"); }
}

class Cat extends Animal {
    @Override void speak() { System.out.println("Meow"); }
}
```

One loop, one call, three different behaviors:

```java
Animal[] zoo = { new Dog(), new Cat(), new Animal() };
for (Animal a : zoo) {
    a.speak();          // Woof, then Meow, then ...
}

static void talk(Animal a) { a.speak(); }   // works for every Animal subclass,
talk(new Dog());                            // even ones written after talk() was compiled
```

The code calling `speak()` doesn't know or care which kind of animal it has. Each object brings its own `speak()`.

> [!note] Definitions
> - **Polymorphism**: the ability of one reference type (here `Animal`) to refer to objects of many classes, with each object's own version of a method running.
> - **Supertype reference**: a variable, parameter, field, array element, or return value whose type is a superclass (or interface) of the object it holds. `Animal a = new Dog();` is legal because a `Dog` **is an** `Animal` ([[Java/04 - Object-Oriented Programming/03 - Inheritance#1. Inheritance — The Idea|Inheritance § 1]]).
> - **Dynamic dispatch** (also *dynamic binding*, *late binding*): choosing which overriding method runs **at runtime**, from the class of the object ([[#3. Dynamic Dispatch|§ 3]]).

The word "polymorphism" covers three different mechanisms in Java. On its own, it almost always means the first one:

| Kind | Java feature | Decided | Where |
|---|---|---|---|
| **Subtype** polymorphism | overriding + supertype references | at **runtime** | this chapter |
| **Ad-hoc** polymorphism | overloading (`print(int)`, `print(String)`) | at **compile time** | [[01 - Methods#7. Method Overloading|Methods § 7]] |
| **Parametric** polymorphism | generics (`List<T>`) | at **compile time** | [[Java/05 - Working with Data and Errors/02 - Generics|Generics]] |

---

## 2. Declared Type vs. Runtime Type

### 2.1 Two Types for Every Reference

```java
Animal a = new Dog();
//  ↑            ↑
//  declared     runtime
//  type         type
```

> [!note] Definitions
> - The **declared type** (also *static type*, *compile-time type*) is the type of the variable or expression as written in the source. It's all the **compiler** knows.
> - The **runtime type** (also *dynamic type*) is the class of the object actually referred to. It's fixed when the object is created with `new` and **never changes**. `a.getClass()` returns it.
>
> A variable's declared type never changes either, but the variable can be reassigned to objects of different runtime types: `a = new Cat();`.

### 2.2 What Each Type Decides

<span class="hl-yellow">The central rule of this chapter.</span>

> [!important] Key rule: the declared type decides what can be **called**, the runtime type decides which override **runs**
> | Question | Decided by | When |
> |---|---|---|
> | Does `a.fetch()` exist? Is `a.name` a field? | **declared** type | compile time |
> | Which overload of `a.meet(…)`? | **declared** types of `a` and of the arguments | compile time |
> | What type does the call return? Which checked exceptions must be handled? | the **declared** type's method | compile time |
> | Which body of an overridden method runs? | **runtime** type | runtime |
> | Which field, which static method? | **declared** type (hiding, [[#10. Where Polymorphism Stops|§ 10]]) | compile time |

```java
Animal a = new Dog();
a.speak();          // Woof : runtime type Dog decides which speak() runs
a.eat();            // inherited from Animal, runs fine
a.fetch();          // compile error: cannot find symbol (Animal has no fetch())
((Dog) a).fetch();  // OK: the cast changes the declared type to Dog

Object o = a;
o.toString();       // runs the Dog's toString (if it overrides it)
o.speak();          // compile error: Object has no speak()
```

The object never changes: the declared type is only a **view** of it, and the view limits what you may ask the object to do.

![[Polymorphism - One Object, Many Views.excalidraw|800]]

> [!warning] Trick: inside `Animal`, a private field can't be read through a `Dog` reference
> ```java
> class Animal {
>     private int secret = 1;
>     int peek(Animal a) { return a.secret; }               // OK
>     int peek(Dog d)    { return d.secret; }               // compile error: secret has private access in Animal
>     int peek2(Dog d)   { return ((Animal) d).secret; }    // OK
> }
> class Dog extends Animal { }
> ```
> Private members aren't inherited, so the type `Dog` has no member named `secret`, even though the code is inside `Animal` and the object does contain the field. Member lookup goes by the declared type, and an upcast fixes it.

### 2.3 The Declared Type Also Fixes the Return Type and Exceptions

The override runs, but the **compiler** still checks the call against the declared type's method. Two consequences that surprise people:

```java
class Animal {
    Animal reproduce() { return new Animal(); }
    void load() throws IOException { … }
}
class Dog extends Animal {
    @Override Dog reproduce() { return new Dog(); }     // covariant return
    @Override void load() { … }                         // throws nothing
}

Animal a = new Dog();
Dog pup = a.reproduce();     // compile error: Animal cannot be converted to Dog
a.load();                    // compile error: unreported exception IOException

Dog d = new Dog();
Dog pup2 = d.reproduce();    // OK: through a Dog reference the return type is Dog
d.load();                    // OK: Dog's load() declares no exception
```

At runtime `a.reproduce()` really does run `Dog.reproduce()` and really does return a `Dog`, but the compiler only knows "some `Animal`'s `reproduce()`", whose return type is `Animal` and which may throw `IOException`. The covariant-return and exception rules are in [[Java/04 - Object-Oriented Programming/03 - Inheritance#3.3 The Rules for a Valid Override|Inheritance § 3.3]].

### 2.4 `var` and the Ternary Operator

`var` takes its type from the initializer, so it gives the **runtime class** as the declared type, not the supertype you may have meant:

```java
var a = new Dog();     // declared type Dog, not Animal
a = new Cat();         // compile error: Cat cannot be converted to Dog

Animal b = new Dog();  // write the supertype explicitly if the variable should hold any Animal
b = new Cat();         // OK
```

A conditional expression with two different classes has their closest common supertype as its type, so `var v = flag ? new Dog() : new Cat();` declares `v` as an `Animal`, and `v.speak()` dispatches as usual. The same happens with `return flag ? new Dog() : new Cat();` in a method returning `Animal`.

---

## 3. Dynamic Dispatch

### 3.1 How the JVM Finds the Method

When the compiler sees `a.speak()` with `a` declared as `Animal`, it checks that `Animal` has a `speak()` and records **"call `speak()`, as declared in `Animal`"** in the bytecode (an `invokevirtual` instruction, or `invokeinterface` for an interface type). It does **not** record which body to run.

At runtime, each time the call executes, the JVM:
1. takes the object that `a` currently refers to (`NullPointerException` if there is none),
2. looks for a method with that signature in the object's class,
3. if that class doesn't declare one, looks in its superclass, then that class's superclass, and so on, and runs the **first** one it finds.

```java
class A { String f() { return "A.f"; } String g() { return "A.g"; } }
class B extends A { @Override String f() { return "B.f"; } }
class C extends B { }                        // overrides nothing

A x = new C();
x.f() + " " + x.g()        // "B.f A.g" : C has neither, B has f, A has g
```

The search always finds something: the compiler already checked that the declared type has the method, and the runtime class is a subclass of it.

> [!info]- How JVMs make this fast: method tables
> Walking up the hierarchy on every call would be slow. In practice the JVM gives each class a **method table** (*vtable*): an array with one slot per overridable method. A subclass's table starts as a copy of its superclass's table, and each override replaces the entry in its slot; new methods get new slots at the end. A virtual call then becomes "read the object's class pointer, read slot number *k*, jump", where *k* was resolved once. On top of that, the JIT compiler notices when a call site always sees the same class and calls (or inlines) that method directly. None of this is visible to Java code: the result is always the one described above.

### 3.2 What Dispatches and What Doesn't

Only **overridable instance methods** are chosen at runtime. Everything else is fixed at compile time, which is why [[Java/04 - Object-Oriented Programming/03 - Inheritance#8. What Is Not Overridden — Hiding|Inheritance § 8]] calls it *hiding*:

| Member used through a reference | Chosen by | Dynamic dispatch? |
|---|---|---|
| instance method (`public`, `protected`, package-private) | runtime type | ✅ |
| `final` instance method | only one version exists | ✅ in principle, but there's nothing to choose; calls **inside** it still dispatch |
| `private` method | the class the call is written in | ❌ ([[Java/04 - Object-Oriented Programming/03 - Inheritance#8.3 Private Methods Are Not Overridden|Inheritance § 8.3]]) |
| `static` method | declared type | ❌ ([[Java/04 - Object-Oriented Programming/03 - Inheritance#8.2 Static Methods Are Hidden, Not Overridden|Inheritance § 8.2]], [[Java/04 - Object-Oriented Programming/01 - Classes and Objects#8.4 Accessing Static Members Through a Reference|Classes and Objects § 8.4]]) |
| field | declared type | ❌ ([[Java/04 - Object-Oriented Programming/03 - Inheritance#8.1 Fields Are Hidden, Not Overridden|Inheritance § 8.1]]) |
| `super.m()` | always the superclass's version | ❌ |
| constructor | the class named after `new` | ❌ |
| interface `default` method | runtime type | ✅ ([[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]]) |

```java
class Animal { static String kind() { return "Animal"; } String name = "animal"; }
class Dog extends Animal { static String kind() { return "Dog"; } String name = "dog"; }

Dog d = new Dog();
Animal a = d;
a.kind()              // "Animal" : static, declared type
d.kind()              // "Dog"
((Animal) d).name     // "animal" : field, declared type
d.name                // "dog"
```

> [!tip] Rule of thumb
> If you can't put `@Override` on it, it doesn't dispatch.

### 3.3 A Cast Doesn't Change Which Override Runs

<span class="hl-red">A common misconception</span> is that casting a reference "up" makes the superclass's version run:

```java
Dog d = new Dog();
((Animal) d).speak();      // Woof : still the Dog's speak()
((Object) d).toString();   // still the Dog's toString(), if Dog overrides it
```

The cast changes only the declared type, and the declared type doesn't choose overrides. From **outside** the class there is no way at all to run `Animal.speak()` on a `Dog` object. From **inside** `Dog`, `super.speak()` does it ([[Java/04 - Object-Oriented Programming/03 - Inheritance#4.1 Calling the Superclass Version|Inheritance § 4.1]]). The cast does matter for fields, static methods, and overload selection ([[#5. Upcasting|§ 5]]).

### 3.4 Calls on `this` Dispatch Too

A call with no explicit receiver, such as `name()` inside a method, is a call on `this`, and `this` has the runtime type of the current object. So a method written in the superclass ends up calling the subclass's overrides, even when it's `final` or reached through `super.`:

```java
class Animal {
    final String id() { return "Animal.id " + name(); }   // final, but name() inside still dispatches
    String name() { return "animal"; }
}
class Dog extends Animal { @Override String name() { return "dog"; } }

Animal a = new Dog();
a.id()        // "Animal.id dog"
```

This is the basis of the *template method* pattern ([[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]]), and also the source of two traps covered in Inheritance: `super.m()` calls whose inner calls still dispatch ([[Java/04 - Object-Oriented Programming/03 - Inheritance#3.1 Overriding in Action|§ 3.1]]), and overridable methods called from a constructor that run before the subclass's fields are initialized ([[Java/04 - Object-Oriented Programming/03 - Inheritance#7. Overridable Methods Called from Constructors|§ 7]]).

### 3.5 A `null` Receiver

Dispatch needs an object, so an instance call on `null` throws:

```java
Animal a = null;
a.speak();     // NullPointerException: Cannot invoke "Animal.speak()" because "a" is null
a.kind();      // static: no exception, compiled as Animal.kind()
```

The static call works because it never looks at the object ([[Java/04 - Object-Oriented Programming/01 - Classes and Objects#8.4 Accessing Static Members Through a Reference|Classes and Objects § 8.4]]). (The NPE message names the variable only when the class was compiled with debug information; otherwise it says `"<local1>"`.)

---

## 4. Overloading and Overriding in the Same Call

### 4.1 The Two Steps

<span class="hl-yellow">Exam favourite.</span> When a method is both overloaded and overridden, a call is resolved in two separate steps:

> [!important] Key rule: compile time picks the signature, runtime picks the body
> 1. **Compile time (overloading):** the compiler looks only at the methods of the receiver's **declared** type, and picks one **signature** from the **declared** types of the arguments ([[01 - Methods#7.2 How the Compiler Chooses an Overload|Methods § 7.2]]).
> 2. **Runtime (overriding):** the JVM runs the override of **that exact signature** found in the receiver's **runtime** class ([[#3.1 How the JVM Finds the Method|§ 3.1]]).
>
> The **runtime** types of the arguments are never used. Java dispatches on the receiver only: this is called **single dispatch**.

```java
class Animal {
    void meet(Animal x) { System.out.println("Animal meets Animal"); }
    void meet(Dog x)    { System.out.println("Animal meets Dog"); }
}
class Dog extends Animal {
    @Override void meet(Animal x) { System.out.println("Dog meets Animal"); }
    @Override void meet(Dog x)    { System.out.println("Dog meets Dog"); }
}

Animal a = new Dog(), b = new Dog();
Dog d = new Dog();

a.meet(b);            // Dog meets Animal
a.meet(d);            // Dog meets Dog
d.meet(b);            // Dog meets Animal
new Animal().meet(d); // Animal meets Dog
```

![[Polymorphism - Two Steps of a Call.excalidraw|800]]

> [!example]- Worked example: each call, step by step
> | Call | Step 1: signature (declared types) | Step 2: runtime class of receiver | Output |
> |---|---|---|---|
> | `a.meet(b)` | `b` is declared `Animal` → `meet(Animal)` | `Dog` | Dog meets Animal |
> | `a.meet(d)` | `d` is declared `Dog` → `meet(Dog)` (more specific) | `Dog` | Dog meets Dog |
> | `d.meet(b)` | `b` is declared `Animal` → `meet(Animal)` | `Dog` | Dog meets Animal |
> | `new Animal().meet(d)` | `meet(Dog)` | `Animal` | Animal meets Dog |
>
> In the first call, both objects are `Dog`s, yet "Dog meets **Animal**" is printed: the argument's runtime type played no part.

The same holds for static helper methods: the overload is picked from the declared type of the argument, whatever the object really is.

```java
static void describe(Animal a) { System.out.println("describe(Animal)"); }
static void describe(Dog d)    { System.out.println("describe(Dog)"); }

Animal a = new Dog();
describe(a);          // describe(Animal)
describe((Dog) a);    // describe(Dog) : the cast changes the declared type
```

### 4.2 An Overload Added in the Subclass

A subclass method with a **different** parameter type is a new overload, not an override. Through a superclass reference the compiler doesn't even see it:

```java
class A { void f(Object o) { System.out.println("A.f(Object)"); } }
class B extends A { void f(String s) { System.out.println("B.f(String)"); } }   // overload, not override

A x = new B();
B y = new B();
x.f("hi");             // A.f(Object) : A has only f(Object); B doesn't override it
y.f("hi");             // B.f(String) : through B, both overloads are visible, f(String) is more specific
y.f((Object) "hi");    // A.f(Object)
```

`x.f("hi")` surprises people because the object is a `B`, `B` has an `f(String)`, and the argument is a `String`. But step 1 searches only `A`'s methods and picks `f(Object)`, and step 2 finds no override of `f(Object)` in `B`. With `@Override` on `B.f`, the compiler would have rejected it as "does not override", which is the hint that this isn't what you wanted.

### 4.3 Overriding Only One of Several Overloads

```java
class A {
    void f(Object o) { System.out.println("A.f(Object)"); }
    void f(String s) { System.out.println("A.f(String)"); }
}
class B extends A {
    @Override void f(Object o) { System.out.println("B.f(Object)"); }
}

A x = new B();
x.f("hi");           // A.f(String) : f(String) is chosen at compile time, and B doesn't override it
Object o = "hi";
x.f(o);              // B.f(Object) : f(Object) chosen, and B overrides it
x.f(null);           // A.f(String) : String is more specific than Object
```

The "most specific" overload (`f(String)`) wins at compile time, even though the subclass only touched the other one. This is the trap behind `equals(Point)` vs. `equals(Object)` ([[Java/04 - Object-Oriented Programming/03 - Inheritance#3.4 Overriding vs. Overloading|Inheritance § 3.4]], [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]).

### 4.4 Double Dispatch

Sometimes the behavior must depend on the runtime types of **two** objects (collisions between shapes, operations between number types). Java picks only by the receiver, but two virtual calls in a row, one on each object, do the job. This is **double dispatch**, the core of the *Visitor* pattern:

> [!example]- Worked example: double dispatch with two shapes
> ```java
> interface Shape {                       // interfaces: see Abstraction
>     String hit(Shape other);            // 1st dispatch: on the receiver
>     String hitBy(Circle c);             // 2nd dispatch: on the argument
>     String hitBy(Square s);
> }
> class Circle implements Shape {
>     public String hit(Shape other) { return other.hitBy(this); }   // here `this` is declared Circle
>     public String hitBy(Circle c)  { return "circle hits circle"; }
>     public String hitBy(Square s)  { return "square hits circle"; }
> }
> class Square implements Shape {
>     public String hit(Shape other) { return other.hitBy(this); }   // here `this` is declared Square
>     public String hitBy(Circle c)  { return "circle hits square"; }
>     public String hitBy(Square s)  { return "square hits square"; }
> }
>
> Shape a = new Circle(), b = new Square();
> a.hit(b)     // "circle hits square"
> b.hit(a)     // "square hits circle"
> ```
> | Step | What happens |
> |---|---|
> | `a.hit(b)` | dispatches on `a`: runs `Circle.hit` |
> | `other.hitBy(this)` inside `Circle` | overload chosen at compile time from `this`'s declared type `Circle` → `hitBy(Circle)` |
> | | dispatches on `other` (a `Square`): runs `Square.hitBy(Circle)` |
>
> Each class's `hit` looks identical, but it can't be moved into a common superclass: the trick depends on `this` having the **subclass** as its declared type. With Java 21, a `switch` over a pair of sealed types is an alternative ([[#8. Pattern Matching in `switch` over Sealed Types (Java 21)|§ 8]]).

---

## 5. Upcasting

**Upcasting** is converting a subtype reference to a supertype (`Dog` → `Animal` → `Object`). It's always safe, so it's **implicit** ([[Java/01 - Foundations/04 - Type Casting#7.1 Upcasting (Implicit)|Type Casting § 7.1]]) and happens in every place a value is passed on:

```java
Animal a = new Dog();                       // assignment
talk(new Dog());                            // argument to an Animal parameter
Animal make() { return new Dog(); }         // return value
Animal[] zoo = { new Dog(), new Cat() };    // array element
List<Animal> pets = List.of(new Cat(), new Dog());   // collection element
```

> [!important] Key rule: upcasting never changes the object
> No copy is made and nothing is "cut off". The reference just has a more general declared type. `getClass()` still returns `Dog`, overridden methods still run the `Dog` versions, and a later downcast gets the full `Dog` back. (In C++, assigning a derived object to a base **variable** by value copies only the base part, called *slicing*. Java variables hold references, so this can't happen.)

What you lose is access **through that reference** to anything `Animal` doesn't declare (`a.fetch()` doesn't compile).

An **explicit** upcast, `(Animal) d`, is legal but rarely needed. It's useful in exactly the cases where the declared type matters:

| Use | Example | Effect |
|---|---|---|
| choose a different overload | `describe((Animal) d)` | `describe(Animal)` instead of `describe(Dog)` |
| reach a hidden field or static method | `((Animal) d).name` | `Animal`'s field ([[#3.2 What Dispatches and What Doesn't|§ 3.2]]) |
| reach a private member of the superclass from inside it | `((Animal) d).secret` | [[#2.2 What Each Type Decides|§ 2.2]] |
| run the superclass's override | `((Animal) d).speak()` | ❌ doesn't work: still `Woof` ([[#3.3 A Cast Doesn't Change Which Override Runs|§ 3.3]]) |

---

## 6. Downcasting and `instanceof`

### 6.1 Downcasting

**Downcasting** converts a supertype reference to a subtype (`Animal` → `Dog`). It may fail, so it needs an explicit cast, and the JVM **checks it at runtime**:

```java
Animal a = new Dog();
Dog d = (Dog) a;            // OK: the object is a Dog
d.fetch();

Animal c = new Cat();
Dog bad = (Dog) c;          // compiles, then at runtime:
// ClassCastException: class Cat cannot be cast to class Dog
```

A successful cast doesn't convert anything: it hands back the **same object** with a narrower declared type. A failing cast throws before any assignment happens.

### 6.2 What the Compiler Rejects and What Fails at Runtime

The compiler rejects a cast only when it can prove that **no** object could ever pass it. Otherwise it compiles the cast and leaves the decision to the runtime check (see also [[Java/01 - Foundations/04 - Type Casting#7.3 Casting Between Unrelated Types Fails at Compile Time|Type Casting § 7.3]]):

| Cast (with `Animal a`, `Dog d`) | Compiles? | At runtime |
|---|---|---|
| `(Dog) a`, object is a `Dog` | ✅ | OK |
| `(Dog) a`, object is a `Cat` | ✅ | `ClassCastException` |
| `(Dog) a`, `a` is `null` | ✅ | OK: the result is `null` (no exception) |
| `(Cat) d` | ❌ *incompatible types: Dog cannot be converted to Cat* | — (siblings: no object is both) |
| `(Rock) a`, `Rock` an unrelated `final` class | ❌ | — |
| `(Runnable) a`, `Animal` not `final` | ✅ | `ClassCastException` unless the object's class implements `Runnable` (a subclass might: [[Java/01 - Foundations/04 - Type Casting#7.3 Casting Between Unrelated Types Fails at Compile Time|Type Casting § 7.3]]) |
| `(Dog[]) animals`, array created as `new Dog[n]` | ✅ | OK |
| `(Dog[]) animals`, array created as `new Animal[n]` (even if every element is a `Dog`) | ✅ | `ClassCastException`: class `[LAnimal;` cannot be cast to class `[LDog;` |
| `(List<Dog>) listOfAnimals` (declared `List<Animal>`) | ❌ *incompatible types* | — (generics are invariant: [[Java/05 - Working with Data and Errors/02 - Generics#5. Generics Are Invariant|Generics § 5]]) |

> [!warning] Trick: casting an array checks the **array's** class, not its elements
> `Animal[] arr = { new Dog(), new Dog() };` creates an `Animal[]` object. Its elements are all dogs, but the array itself is not a `Dog[]`, so `(Dog[]) arr` throws. To get a `Dog[]`, create one and copy the elements over, casting each element.

### 6.3 Casts Bind Weaker Than Method Calls

A cast applies to the whole expression after it, **after** member access (`.`) has been done:

```java
(Dog) a.fetch();       // means (Dog) (a.fetch()): compile error, cannot find symbol fetch() in Animal
((Dog) a).fetch();     // correct: cast first, then call
```

As a statement on its own, `(Dog) a.fetch();` gives an even less helpful error (*not a statement*). Wrap the cast in its own parentheses whenever you call something on the result.

### 6.4 `instanceof` vs. `getClass()`

`x instanceof T` is `true` if `x` refers to an object whose class is `T` **or any subtype** of `T`, and `false` for `null` (no exception). The basics are in [[Java/01 - Foundations/03 - Operators#10.2 `instanceof`|Operators § 10.2]]. The classic safe-downcast idiom before Java 16 was test, then cast:

```java
if (a instanceof Dog) {
    Dog d = (Dog) a;       // can't fail: just checked
    d.fetch();
}
```

To test for an **exact** class, compare `getClass()` instead:

| Expression (with `Animal a = new Dog();`) | Result | Why |
|---|---|---|
| `a instanceof Dog` | `true` | |
| `a instanceof Animal` | `true` | subclasses count |
| `a instanceof Object` | `true` | every object |
| `a.getClass() == Dog.class` | `true` | exact class |
| `a.getClass() == Animal.class` | `false` | the object isn't exactly an `Animal` |
| `null instanceof Dog` | `false` | never throws |
| `null.getClass()` (through a `null` variable) | `NullPointerException` | |
| `new Dog() instanceof Cat` | compile error | the compiler can prove it's never true |

`instanceof` respects substitutability (a `Dog` is an `Animal`), `getClass()` doesn't. Which one `equals` should use is discussed in [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]. When the type is only known at runtime as a `Class` object, use `type.isInstance(x)` and `type.cast(x)` ([[Java/05 - Working with Data and Errors/02 - Generics#7.2 What Erasure Forbids|Generics § 7.2]]).

---

## 7. Pattern Matching for `instanceof` (Java 16+)

### 7.1 Syntax

A **type pattern** combines the test, the cast, and a new variable:

```java
if (a instanceof Dog d) {     // if a is a Dog, d is a (already cast) and in scope
    d.fetch();
}
```

`d` is called a **pattern variable** (or *binding variable*). It's assigned only if the test succeeds, so it can't be used anywhere the test might have failed. A `null` value never matches.

### 7.2 Where the Pattern Variable Is in Scope

The compiler puts the pattern variable in scope exactly where the test is **certainly true** (*flow scoping*). This is more flexible than a block, and sometimes surprising:

| Code | Is `s` usable there? |
|---|---|
| `if (o instanceof String s) { s.length(); }` | ✅ inside the `if` block |
| `o instanceof String s && s.length() > 3` | ✅ right of `&&`: it only runs if the test was true |
| `o instanceof String s \|\| s.isEmpty()` | ❌ compile error *cannot find symbol*: right of `\|\|` runs when the test was **false** |
| `if (o instanceof String s) { } System.out.println(s);` | ❌ after the `if`: the test may have failed |
| `if (!(o instanceof String s)) return; s.length();` | ✅ after the `if`: the only way to get past it is a successful test |
| `if (!(o instanceof String s)) { … } else { s.length(); }` | ✅ in the `else` |
| `!(o instanceof String s) ? -1 : s.length()` | ✅ in the "false" branch of `?:` |
| `while (!(o instanceof Integer i)) { o = 7; }  i + 1` | ✅ after the loop: it only exits once the test is true |

The negated form with an early `return` (or `throw`, `continue`) is the idiomatic "guard clause":

```java
static void process(Object o) {
    if (!(o instanceof String s)) {
        throw new IllegalArgumentException("need a String");
    }
    System.out.println(s.toUpperCase());     // s in scope for the rest of the method
}
```

### 7.3 Pattern Variable Traps

> [!warning] Trick: a pattern variable can't reuse a local's name, but it **can** shadow a field
> ```java
> String s = "";
> if (o instanceof String s) { }      // compile error: variable s is already defined
> ```
> With a **field** named `s`, it compiles, and `s` means different things in different places:
> ```java
> static String s = "field";
>
> static void test(Object o) {
>     if (!(o instanceof String s)) {
>         System.out.println(s);       // "field" : the pattern variable isn't in scope here
>         return;
>     }
>     System.out.println(s.length());  // the pattern variable
> }
> test(42);       // prints field
> ```

| Code | Result | Why |
|---|---|---|
| `String str = …; str instanceof String s` | compile error in Java 16–20: *expression type String is a subtype of pattern type String* | the test could only fail for `null`, so it was rejected as pointless. Java 21 removed this restriction. |
| `str instanceof CharSequence cs` (`str` a `String`) | compile error in Java 16–20, same reason | supertype of the declared type |
| `if (o instanceof String s) { s = "x"; }` | compiles | pattern variables are **not** implicitly `final` (but reassigning them is confusing) |
| `if (o instanceof final String s) { s = "x"; }` | compile error: *cannot assign a value to final variable s* | `final` is allowed on the pattern |
| `o instanceof List<String> l` (`o` an `Object`) | compile error: *Object cannot be safely cast to List\<String\>* | the type argument can't be checked at runtime ([[Java/05 - Working with Data and Errors/02 - Generics#7.2 What Erasure Forbids|Generics § 7.2]]) |
| `ls instanceof ArrayList<String> al` (`ls` a `List<String>`) | compiles | the only runtime check needed is "is it an `ArrayList`?" |

---

## 8. Pattern Matching in `switch` over Sealed Types (Java 21)

> ⚠️ Pattern matching in `switch` became a standard feature in Java 21 (it was a preview feature in Java 17–20). The code in this section can't be checked with the JDK 17 used for these notes. The general syntax (type patterns, `when` guards, `case null`, record patterns) is in [[Java/02 - Control Flow/01 - Conditional Statements#8. Pattern Matching in `switch` (Java 21+)|Conditional Statements § 8]]. This section covers what matters for class hierarchies.

### 8.1 Exhaustive `switch` Without `default`

A `switch` with patterns must be **exhaustive**: some case must match every possible value. Over a sealed hierarchy ([[Java/04 - Object-Oriented Programming/03 - Inheritance#11. Sealed Classes (Java 17+)|Inheritance § 11]]), listing every permitted subclass is enough, and no `default` is needed:

```java
abstract sealed class Shape permits Circle, Square { }   // abstract: no plain Shape object can exist
final class Circle extends Shape { double r; }
final class Square extends Shape { double side; }

static double area(Shape s) {
    return switch (s) {
        case Circle c -> Math.PI * c.r * c.r;
        case Square q -> q.side * q.side;
        // no default: the compiler knows these are the only possible Shapes
    };
}
```

The benefit appears later: when someone adds `final class Triangle extends Shape` to the `permits` list, **every** such `switch` stops compiling until it handles `Triangle`. A `default` branch would silence that check, so leave it out on purpose.

> [!warning] Trick: the sealed class must be `abstract` (or an interface)
> If `Shape` is not `abstract`, `new Shape()` is a possible value that neither `case Circle` nor `case Square` matches, so the `switch` above is **not** exhaustive and doesn't compile. Either make `Shape` `abstract` ([[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]]), use a sealed interface, or add `case Shape other ->`.

Exhaustiveness is required for every `switch` **expression**, and for a `switch` **statement** too as soon as it uses patterns or `case null`. An old-style `switch` statement over constants still doesn't need to be exhaustive.

### 8.2 Dominance, Guards, and `null`

| Situation | Result |
|---|---|
| `case Shape s ->` before `case Circle c ->` | compile error: *this case label is dominated by a preceding case label* (the `Circle` case could never be reached). Put specific types first. |
| `case Circle c when c.r == 0 -> "dot";` then `case Circle c -> …` | OK: a guarded case doesn't dominate the unguarded one |
| only `case Circle c when c.r > 0` for circles | not exhaustive: the compiler doesn't analyze guards, so circles with `r <= 0` are uncovered |
| selector is `null`, no `case null` | `NullPointerException`, as in every `switch` |
| `case null ->` present | matches `null` |

### 8.3 Overriding or `switch`?

Both are ways to make behavior depend on the runtime type. They have opposite strengths (this tradeoff is known as the *expression problem*):

| | Overriding: a method in each class | `switch` over a sealed type |
|---|---|---|
| Adding a new **subtype** | add one class; no existing code changes | every `switch` must get a new case (the compiler lists them, if there's no `default`) |
| Adding a new **operation** | edit every class in the hierarchy | write one new method with one `switch` |
| Where the behavior lives | with the data | in one place per operation |
| Works for classes you can't edit | ❌ | ✅ |
| Good fit | open hierarchies whose operations are stable (`Animal.speak()`) | closed sets of data types with many operations (syntax trees, messages, results) |

For ordinary object-oriented code, overriding is the default. A pattern `switch` is the right tool when the set of subtypes is deliberately closed (sealed) and operations are added more often than types.

---

## 9. Designing with Polymorphism

### 9.1 Replace `instanceof` Chains with Overriding

<span class="hl-red">The most common design mistake</span> in code that uses class hierarchies is asking each object what it is:

```java
// ❌ type-checking code
static double area(Shape s) {
    if (s instanceof Circle c)      return Math.PI * c.r * c.r;
    else if (s instanceof Square q) return q.side * q.side;
    else throw new IllegalArgumentException("unknown shape");
}
```

Every new `Shape` subclass needs a new branch here, **and** in every other method written the same way (`perimeter`, `draw`, `toJson` …). Forgetting one compiles fine and fails at runtime. The polymorphic version asks the object to do the work:

```java
// ✅ polymorphic code
abstract class Shape { abstract double area(); }     // abstract: see Abstraction
class Circle extends Shape { double r;    @Override double area() { return Math.PI * r * r; } }
class Square extends Shape { double side; @Override double area() { return side * side; } }

double total = 0;
for (Shape s : shapes) total += s.area();            // no type checks at all
```

Adding `Triangle` now means writing one class with its own `area()`. No existing code changes, and the compiler forces the new class to provide `area()` because it's `abstract`. This is the **open/closed principle**: code should be open for extension (new subclasses) but closed for modification (no edits to existing methods).

> [!tip] Smell test
> An `if`/`else if` chain or a `switch` testing `instanceof`, `getClass()`, or a "type" field (`if (kind == CIRCLE)`) in ordinary code usually means a method should move into the class hierarchy. The exception is a sealed hierarchy with an exhaustive pattern `switch` ([[#8.3 Overriding or `switch`?|§ 8.3]]), where the compiler does catch forgotten cases.

### 9.2 Program to the Supertype

Declare variables, parameters, and return types with the **most general type that has the methods you need**. The code then accepts any subtype, and the concrete class can change in one place:

```java
List<String> names = new ArrayList<>();        // not ArrayList<String> names
static double totalArea(List<Shape> shapes)     // any List, of any Shapes
static void feedAll(Animal[] animals)           // any animals, including future subclasses
```

If the declared type is the concrete class (`ArrayList<String> names`), switching to a `LinkedList` means changing every method that receives it. With interfaces ([[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]]) this becomes the standard style: *program to an interface, not an implementation*.

### 9.3 When `instanceof` Is the Right Tool

Type tests are not forbidden. They are the right choice when:
- implementing `equals(Object)`, which receives an arbitrary object ([[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]);
- the types belong to code you can't change (library classes), so you can't add a method to them;
- the hierarchy is sealed and a pattern `switch` is used on purpose ([[#8. Pattern Matching in `switch` over Sealed Types (Java 21)|§ 8]]);
- checking for an optional capability, e.g. the JDK's own `if (list instanceof RandomAccess)` to choose a faster algorithm for array-backed lists.

### 9.4 The Liskov Substitution Principle

Polymorphic code is only correct if every subclass really can stand in for its superclass. The **Liskov Substitution Principle** (LSP) states it: *a subtype object must work everywhere a supertype object is expected, without the caller noticing.* The compiler checks the method **signatures** ([[Java/04 - Object-Oriented Programming/03 - Inheritance#3.3 The Rules for a Valid Override|Inheritance § 3.3]]), but not the **behavior** the caller relies on.

The classic violation: mathematically a square is a rectangle, so `Square extends Rectangle` looks natural.

```java
class Rectangle {
    protected int w, h;
    void setWidth(int w)  { this.w = w; }
    void setHeight(int h) { this.h = h; }
    int area() { return w * h; }
}
class Square extends Rectangle {                 // keeps w == h
    @Override void setWidth(int s)  { w = s; h = s; }
    @Override void setHeight(int s) { w = s; h = s; }
}

static void resize(Rectangle r) {
    r.setWidth(5);
    r.setHeight(4);
    System.out.println(r.area());                // the caller expects 20
}

resize(new Rectangle());    // 20
resize(new Square());       // 16 : setHeight(4) also changed the width
```

Every method compiles and every override follows the rules, but `resize` breaks for squares, because `Rectangle` promises that `setHeight` leaves the width alone. A **mutable** square is not substitutable for a mutable rectangle. Fixes: make both immutable (then a square *is* a valid rectangle), or don't relate them by inheritance (both can implement a common `Shape` with `area()`).

> [!important] Key rule: an override must keep the superclass's promises
> - Accept at least everything the superclass method accepts (don't add stricter preconditions, e.g. rejecting values the superclass allowed).
> - Guarantee at least what the superclass method guarantees (don't weaken the result, e.g. returning `null` where the superclass never did).
> - Preserve the superclass's invariants, and don't throw new kinds of exceptions that callers can't expect. Unchecked exceptions always compile ([[Java/04 - Object-Oriented Programming/03 - Inheritance#3.3 The Rules for a Valid Override|Inheritance § 3.3]]), so this one is on you, not the compiler.

---

## 10. Where Polymorphism Stops

A summary of everything that does **not** follow the runtime type, with links to where each is explained:

| Feature | Behavior | Details |
|---|---|---|
| fields | declared type (hiding) | [[Java/04 - Object-Oriented Programming/03 - Inheritance#8.1 Fields Are Hidden, Not Overridden|Inheritance § 8.1]] |
| static methods | declared type (hiding) | [[Java/04 - Object-Oriented Programming/03 - Inheritance#8.2 Static Methods Are Hidden, Not Overridden|Inheritance § 8.2]] |
| private methods | not overridden | [[Java/04 - Object-Oriented Programming/03 - Inheritance#8.3 Private Methods Are Not Overridden|Inheritance § 8.3]] |
| package-private methods across packages | not overridden | [[Java/04 - Object-Oriented Programming/03 - Inheritance#8.4 Package-Private Methods Across Packages|Inheritance § 8.4]] |
| overload selection | declared types of the arguments | [[#4. Overloading and Overriding in the Same Call|§ 4]] |
| return type and checked exceptions of a call | the declared type's method | [[#2.3 The Declared Type Also Fixes the Return Type and Exceptions|§ 2.3]] |
| generic types | **invariant**: `List<Dog>` is not a `List<Animal>` | [[Java/05 - Working with Data and Errors/02 - Generics#5. Generics Are Invariant|Generics § 5]] |
| arrays | **covariant**: `Dog[]` is an `Animal[]`, checked at runtime with `ArrayStoreException` | [[Java/02 - Control Flow/03 - Arrays#11.2 Covariance and `ArrayStoreException`|Arrays § 11.2]] |

The last two rows matter whenever polymorphic code takes a collection:

```java
static void feedAll(List<Animal> animals) { … }
List<Dog> dogs = new ArrayList<>();
feedAll(dogs);                                  // compile error: List<Dog> cannot be converted to List<Animal>

static void feedAll2(List<? extends Animal> animals) { for (Animal a : animals) a.eat(); }
feedAll2(dogs);                                 // OK: a wildcard accepts a list of any Animal subtype

Animal[] arr = new Dog[2];                      // compiles: arrays are covariant
arr[0] = new Cat();                             // ArrayStoreException: Cat
```

If `List<Dog>` were a `List<Animal>`, `feedAll` could add a `Cat` to the list of dogs. Arrays allow the assignment and catch the bad store at runtime instead. The wildcard and its limits (`animals.add(…)` doesn't compile) are explained in [[Java/05 - Working with Data and Errors/02 - Generics#6.2 The Upper-Bounded Wildcard `? extends T`|Generics § 6.2]].

---

## 11. Common Pitfalls

- **Calling a subclass-only method through a supertype reference**: `a.fetch()` with `Animal a` doesn't compile, even when the object is a `Dog`.
- **Expecting a cast to select the superclass's override**: `((Animal) dog).speak()` still runs `Dog.speak()`. Only `super.speak()`, inside `Dog`, reaches `Animal`'s.
- **Expecting the argument's runtime type to choose the overload**: `a.meet(b)` with `b` declared `Animal` always calls `meet(Animal)`, whatever `b` is.
- **Adding an overload in the subclass and expecting it to override**: `B.f(String)` doesn't override `A.f(Object)`, and isn't even visible through an `A` reference. `@Override` catches this.
- **Overriding one overload and expecting it for all**: the compiler may pick a more specific overload that the subclass didn't override.
- **Expecting a covariant return or a narrower `throws` through a supertype reference**: `Dog pup = a.reproduce();` doesn't compile, and `a.load()` still needs a `try`/`catch`.
- **`var a = new Dog();`** declares a `Dog`, so `a = new Cat()` doesn't compile.
- **Downcasting without checking**: `(Dog) a` compiles for any `Animal`, and throws `ClassCastException` if the object isn't a `Dog`.
- **`(Dog) a.fetch()`**: the cast applies after the call. Write `((Dog) a).fetch()`.
- **Casting an `Animal[]` to `Dog[]`** because all its elements are dogs: the array's own class decides.
- **Using `getClass() ==` when `instanceof` was meant** (or the reverse): `getClass()` ignores subclasses.
- **Pattern variable scope**: not usable after `||`, or after an `if` that may have failed; but usable after `if (!(x instanceof T t)) return;`. A pattern variable can silently shadow a field of the same name.
- **`x instanceof SameType t`** is a compile error before Java 21.
- **Writing `default` in a `switch` over a sealed type**: it hides the compile error you want when a new subtype is added. And a sealed class that isn't `abstract` needs its own case.
- **`instanceof` chains** instead of overriding: every new subclass needs edits in many places, and forgotten ones fail only at runtime.
- **Subclasses that break the superclass's behavior** (mutable `Square extends Rectangle`): the code compiles, and polymorphic callers get wrong results.
- **Expecting fields, static methods, or generic types to be polymorphic** ([[#10. Where Polymorphism Stops|§ 10]]).

---

## 12. Quick Reference — Non-Obvious Outcomes

`Animal`, `Dog`, `Cat` as in [[#1. Polymorphism — The Idea|§ 1]].

| Code | Result | Why |
|---|---|---|
| `Animal a = new Dog(); a.speak();` | `Woof` | runtime type decides the override |
| `a.fetch()` | compile error | declared type `Animal` has no `fetch` |
| `Object o = new Dog(); o.speak();` | compile error | declared type `Object` |
| `((Animal) dog).speak()` | `Woof` | casts don't select overrides |
| `Animal a = null; a.speak();` | `NullPointerException` | dispatch needs an object |
| `Animal a = null; a.staticM();` | works | static: compiled as `Animal.staticM()` |
| `Dog pup = a.reproduce();` (`Dog` overrides with covariant `Dog`) | compile error | declared type's return type is `Animal` |
| `a.load()`, `Animal.load` throws `IOException`, `Dog.load` doesn't | compile error if unhandled | declared type's `throws` clause |
| `var a = new Dog(); a = new Cat();` | compile error | `var` inferred `Dog` |
| `var v = flag ? new Dog() : new Cat(); v.speak();` | compiles, dispatches | type is the common supertype `Animal` |
| inside `Animal`: `dog.secret` (`private` field, `Dog dog`) | compile error | private isn't inherited, `Dog` has no `secret` |
| … `((Animal) dog).secret` | compiles | |
| `A x = new C(); x.f()` with `f` overridden only in `B` (between) | `B.f` | search goes up from `C` |
| `final` method in `Animal` calling `name()`, overridden in `Dog` | `Dog.name()` runs | calls on `this` dispatch |
| `a.meet(b)`, both `Dog`s, `b` declared `Animal` | `Dog meets Animal` | overload by declared type, override by runtime type |
| `describe(a)` with `describe(Animal)`/`describe(Dog)`, `a` a `Dog` declared `Animal` | `describe(Animal)` | overloads use the declared type |
| `A x = new B(); x.f("hi")`, `A.f(Object)`, `B.f(String)` | `A.f(Object)` | `B.f(String)` is an overload, invisible through `A` |
| `A` has `f(Object)` and `f(String)`, `B` overrides `f(Object)`; `x.f("hi")` | `A.f(String)` | `f(String)` chosen at compile time, not overridden |
| … `x.f(null)` | `A.f(String)` | most specific overload |
| `(Dog) animalThatIsACat` | `ClassCastException` | runtime check |
| `(Dog) nullAnimal` | `null`, no exception | `null` passes every cast |
| `(Cat) aDogReference` | compile error | siblings: impossible |
| `(Runnable) anAnimal` | compiles; `ClassCastException` unless implemented | a subclass could implement it |
| `(Dog[]) new Animal[]{ new Dog() }` | `ClassCastException` | the array is an `Animal[]` |
| `Animal[] arr = new Dog[2]; arr[0] = new Cat();` | `ArrayStoreException` | arrays are covariant, checked at runtime |
| `(List<Dog>) listOfAnimals` | compile error | generics are invariant |
| `List<Animal> l = dogsList;` | compile error | use `List<? extends Animal>` |
| `(Dog) a.fetch()` | compile error | cast applies to the call's result |
| `a.getClass() == Animal.class` (object is a `Dog`) | `false` | exact class |
| `a instanceof Animal` (object is a `Dog`) | `true` | subclasses count |
| `null instanceof Dog` | `false` | no exception |
| `new Dog() instanceof Cat` | compile error | impossible type test |
| `o instanceof String s \|\| s.isEmpty()` | compile error | `s` not in scope after `\|\|` |
| `if (!(o instanceof String s)) return; s.length();` | compiles | `s` in scope after the guard |
| `while (!(o instanceof Integer i)) {…}  i + 1` | compiles | `i` in scope after the loop |
| local `String s` + `o instanceof String s` | compile error | already defined |
| field `s` + `if (!(o instanceof String s)) print(s)` | prints the field | pattern variable not in scope there |
| `str instanceof String s` (`str` a `String`) | compile error (Java 16–20) | pattern type not narrower than expression type |
| `if (o instanceof String s) s = "x";` | compiles | pattern variables aren't implicitly `final` |
| `o instanceof List<String> l` (`o` an `Object`) | compile error | not checkable at runtime |
| sealed `switch` with all subclasses, no `default` (Java 21) | compiles | exhaustive |
| … but the sealed class isn't `abstract` | compile error | `new Shape()` isn't covered |
| `case Shape s` before `case Circle c` | compile error | dominated case |
| `resize(new Square())` (sets width 5, height 4) | `16`, not `20` | LSP violation: the override changes both sides |

---

## 13. Practice — Trick Questions

**Q1.** What is printed?

```java
class Animal {
    void meet(Animal x) { System.out.println("A-A"); }
    void meet(Dog x)    { System.out.println("A-D"); }
}
class Dog extends Animal {
    @Override void meet(Animal x) { System.out.println("D-A"); }
    @Override void meet(Dog x)    { System.out.println("D-D"); }
}

Animal a = new Dog();
Animal b = new Dog();
Dog d = new Dog();
Animal plain = new Animal();

a.meet(b);
a.meet(d);
d.meet(b);
plain.meet(d);
a.meet((Dog) b);
```

> [!success]- Answer
> ```
> D-A
> D-D
> D-A
> A-D
> D-D
> ```
> | Call | Signature (compile time, declared argument type) | Receiver's runtime class | Output |
> |---|---|---|---|
> | `a.meet(b)` | `meet(Animal)` | `Dog` | D-A |
> | `a.meet(d)` | `meet(Dog)` | `Dog` | D-D |
> | `d.meet(b)` | `meet(Animal)` | `Dog` | D-A |
> | `plain.meet(d)` | `meet(Dog)` | `Animal` | A-D |
> | `a.meet((Dog) b)` | the cast makes the argument's declared type `Dog` → `meet(Dog)` | `Dog` | D-D |

**Q2.** What is printed?

```java
class A { void f(Object o) { System.out.println("A.f(Object)"); } }
class B extends A { void f(String s) { System.out.println("B.f(String)"); } }

A x = new B();
B y = new B();
x.f("hi");
y.f("hi");
((A) y).f("hi");
```

> [!success]- Answer
> ```
> A.f(Object)
> B.f(String)
> A.f(Object)
> ```
> `B.f(String)` is an **overload**, not an override (different parameter type). Through an `A` reference the compiler sees only `f(Object)`, and `B` doesn't override `f(Object)`, so `A`'s version runs, for `x` and for `((A) y)` alike. Through a `B` reference both overloads are visible and `f(String)` is more specific.

**Q3.** `Animal`, `Dog`, `Cat` as usual; `Rock` is an unrelated `final` class. For each line: compile error, runtime exception, or fine?

```java
Animal a = new Cat();
Animal n = null;
Dog d = new Dog();
Animal[] arr = { new Dog() };

Dog d1 = (Dog) a;                     // (1)
Dog d2 = (Dog) n;                     // (2)
Cat c = (Cat) d;                      // (3)
Rock r = (Rock) a;                    // (4)
Runnable run = (Runnable) a;          // (5)
Dog[] dogs = (Dog[]) arr;             // (6)
Object o = d; String s = (String) o;  // (7)
```

> [!success]- Answer
> | Line | Result | Why |
> |---|---|---|
> | (1) | `ClassCastException` | compiles (`Animal` → `Dog` is plausible), but the object is a `Cat` |
> | (2) | fine, `d2` is `null` | `null` passes every cast |
> | (3) | compile error | `Dog` and `Cat` are siblings: no object is both |
> | (4) | compile error | `Rock` is unrelated to `Animal`, and being `final` it has no subclasses that could be |
> | (5) | `ClassCastException` | compiles because some subclass of `Animal` might implement `Runnable`; `Cat` doesn't |
> | (6) | `ClassCastException` | the array object is an `Animal[]`, whatever its elements are |
> | (7) | `ClassCastException` | `Object` → `String` compiles; the object is a `Dog` |

**Q4.** Which lines compile?

```java
class Animal {
    Animal reproduce() { return new Animal(); }
    void load() throws java.io.IOException { }
}
class Dog extends Animal {
    @Override Dog reproduce() { return new Dog(); }
    @Override void load() { }
    void fetch() { }
}

Animal a = new Dog();
Dog d = new Dog();
Dog p1 = a.reproduce();            // (1)
Dog p2 = d.reproduce();            // (2)
a.load();                          // (3)   (no try/catch, method has no throws)
d.load();                          // (4)
a.fetch();                         // (5)
((Dog) a).fetch();                 // (6)
(Dog) a.fetch();                   // (7)
var v = new Dog(); v = new Cat();  // (8)
```

> [!success]- Answer
> | Line | Compiles? | Why |
> |---|---|---|
> | (1) | ❌ | the call is checked against `Animal.reproduce()`, which returns `Animal` |
> | (2) | ✅ | through `Dog`, the covariant return type `Dog` is visible |
> | (3) | ❌ | `Animal.load()` declares `IOException`, which must be handled, even though `Dog.load()` will run |
> | (4) | ✅ | `Dog.load()` declares nothing |
> | (5) | ❌ | `Animal` has no `fetch()` |
> | (6) | ✅ | cast first, then call |
> | (7) | ❌ | parsed as `(Dog) (a.fetch())` |
> | (8) | ❌ | `var` inferred `Dog` |

**Q5.** What is printed?

```java
class A {
    void f() { System.out.print("A.f "); g(); }
    void g() { System.out.println("A.g"); }
}
class B extends A { @Override void g() { System.out.println("B.g"); } }
class C extends B { @Override void f() { System.out.print("C.f "); super.f(); } }

A x = new C();
x.f();
new B().f();
```

> [!success]- Answer
> ```
> C.f A.f B.g
> A.f B.g
> ```
> `x.f()` runs `C.f`. Its `super.f()` goes to `B`'s `f`, which is the one `B` inherited from `A`. Inside `A.f`, `g()` is a call on `this`, a `C` object; `C` doesn't override `g`, so the search goes up to `B.g`. For `new B().f()`, `B` inherits `A.f`, and `g()` dispatches to `B.g`.

**Q6.** What is printed? What if `speak` were `static` in both classes (and called the same way)?

```java
class Animal { void speak() { System.out.println("..."); } }
class Dog extends Animal { @Override void speak() { System.out.println("Woof"); } }

Dog d = new Dog();
Animal a = d;
a.speak();
((Animal) d).speak();
((Object) d).toString();   // assume Dog doesn't override toString
```

> [!success]- Answer
> `Woof` twice (the last line prints nothing). A cast never selects an override: the object is a `Dog`. `toString()` runs `Object.toString` because `Dog` doesn't override it, and it would return `Dog@…`.
>
> If `speak` were `static` in both, `a.speak()` and `((Animal) d).speak()` would both print `...`: static methods are hidden, so the **declared** type `Animal` decides, and `@Override` would be a compile error.

**Q7.** Which lines compile? (Java 17; `o` is an `Object`, `str` a `String`.)

```java
if (o instanceof String s && s.length() > 2) { }       // (1)
if (o instanceof String s || s.length() > 2) { }       // (2)
if (!(o instanceof String s)) return; s.trim();        // (3)
if (o instanceof String s) { } s.trim();               // (4)
if (str instanceof String t) { }                       // (5)
if (o instanceof final Integer i) { i = 3; }           // (6)
int n = !(o instanceof String u) ? 0 : u.length();     // (7)
```

> [!success]- Answer
> | Line | Compiles? | Why |
> |---|---|---|
> | (1) | ✅ | `s` is in scope on the right of `&&` |
> | (2) | ❌ | the right of `\|\|` runs only when the test failed |
> | (3) | ✅ | after the guard, the test must have succeeded |
> | (4) | ❌ | after the `if`, the test may have failed |
> | (5) | ❌ (Java 16–20) | the pattern type must be narrower than `String`; Java 21 accepts it |
> | (6) | ❌ | a `final` pattern variable can't be reassigned |
> | (7) | ✅ | `u` is in scope in the branch taken when the test succeeded |

**Q8.** What is printed by `test(42); test("hello");`?

```java
static String s = "field";

static void test(Object o) {
    if (!(o instanceof String s)) {
        System.out.println("not a string: " + s);
        return;
    }
    System.out.println("length " + s.length());
}
```

> [!success]- Answer
> ```
> not a string: field
> length 5
> ```
> Inside the negated branch the pattern variable isn't in scope (the test failed), so `s` refers to the static **field**. After the `if`, the pattern variable is in scope and shadows the field. Using the same name for both is legal, but a bad idea.

**Q9.** What is printed?

```java
class Rectangle {
    protected int w, h;
    void setWidth(int w)  { this.w = w; }
    void setHeight(int h) { this.h = h; }
    int area() { return w * h; }
}
class Square extends Rectangle {
    @Override void setWidth(int s)  { w = s; h = s; }
    @Override void setHeight(int s) { w = s; h = s; }
}

static void resize(Rectangle r) { r.setWidth(5); r.setHeight(4); System.out.println(r.area()); }

resize(new Rectangle());
resize(new Square());
```

> [!success]- Answer
> `20`, then `16`. The `Square` overrides follow every compiler rule, but `setHeight(4)` also sets the width to 4. `resize` relies on `Rectangle`'s promise that the two sides are independent, and a mutable `Square` breaks it. This violates the **Liskov Substitution Principle**: polymorphism compiles, but the substitution isn't safe ([[#9.4 The Liskov Substitution Principle|§ 9.4]]).

**Q10.** (Java 21) Does each `switch` compile?

```java
sealed class Shape permits Circle, Square { }
final class Circle extends Shape { }
final class Square extends Shape { }

String a(Shape s) { return switch (s) { case Circle c -> "c"; case Square q -> "q"; }; }      // (1)
String b(Shape s) { return switch (s) { case Shape x -> "s"; case Circle c -> "c"; }; }       // (2)
String c(Shape s) { return switch (s) { case Circle c -> "c"; case Shape x -> "s"; }; }       // (3)
```

> [!success]- Answer
> | Method | Compiles? | Why |
> |---|---|---|
> | (1) | ❌ | `Shape` isn't `abstract`, so a plain `Shape` object can exist, and no case matches it. With `abstract sealed class Shape` it would compile. |
> | (2) | ❌ | `case Circle c` is **dominated** by `case Shape x`, which matches every circle first |
> | (3) | ✅ | specific case first; `case Shape x` covers everything else, so it's exhaustive |

**Q11.** What is printed?

```java
Animal[] arr = new Dog[2];
arr[0] = new Dog();
System.out.println("stored a Dog");
arr[1] = new Cat();
System.out.println("stored a Cat");
```

> [!success]- Answer
> ```
> stored a Dog
> Exception in thread "main" java.lang.ArrayStoreException: Cat
> ```
> The declared type `Animal[]` lets the compiler accept `arr[1] = new Cat()`. But the array object is a `Dog[]`, and arrays check every store at runtime. `List<Animal> l = new ArrayList<Dog>();` is rejected at compile time instead ([[#10. Where Polymorphism Stops|§ 10]]).

**Q12.** A method computes a price with `if (item instanceof Book b) … else if (item instanceof Food f) … else if (item instanceof Toy t) …`, and the same chain appears in `tax(item)` and `shippingCost(item)`. A new subclass `Gift` is added. What goes wrong, and what are the two better designs?

> [!success]- Answer
> Every chain needs a new `Gift` branch, the compiler doesn't point out the missing ones, and a forgotten branch only shows up at runtime (an exception, or a wrong default). Better:
> 1. **Overriding**: declare `price()`, `tax()`, and `shippingCost()` in the superclass (abstract) and implement them in each subclass. Adding `Gift` then means writing one class, and the compiler forces it to implement all three ([[#9.1 Replace `instanceof` Chains with Overriding|§ 9.1]]).
> 2. **Sealed hierarchy + pattern `switch`** (Java 21): make the item type `sealed` and use exhaustive `switch` expressions with no `default`. Adding `Gift` to `permits` turns every incomplete `switch` into a compile error ([[#8.1 Exhaustive `switch` Without `default`|§ 8.1]]). This is better when operations are added more often than item types.

---

## 14. Summary

- **Polymorphism**: a supertype reference (`Animal a`) can hold any subtype object (`new Dog()`), and calls run the object's own overrides. Code written against `Animal` works for subclasses written later.
- Every reference has a **declared type** (compile time, fixed by the source) and points to an object with a **runtime type** (fixed at `new`). The declared type decides what can be called, which overload, the return type, and the checked exceptions; the runtime type decides which **override** runs.
- **Dynamic dispatch**: the JVM looks for the chosen signature starting at the object's class and going up. Only overridable instance methods dispatch; fields, static methods, private methods, constructors, and `super.m()` are fixed at compile time. Calls on `this` inside inherited methods dispatch too.
- A cast changes the declared type only: `((Animal) dog).speak()` still runs `Dog.speak()`.
- **Overloading + overriding**: compile time picks the signature from the declared types (receiver and arguments); runtime picks the body from the receiver's object. Argument runtime types are never used (**single dispatch**); double dispatch needs two calls.
- **Upcasting** is implicit and never changes the object. **Downcasting** needs a cast, is checked at runtime (`ClassCastException`), and is a compile error only when provably impossible. `null` passes every cast; array casts check the array's class.
- **`instanceof`** includes subclasses and is `false` for `null`; `getClass() ==` tests the exact class. **Pattern matching** (`x instanceof Dog d`, Java 16+) binds a variable that is in scope wherever the test is certainly true.
- **Pattern `switch` over a sealed type** (Java 21) can be exhaustive without `default`, so adding a subtype breaks compilation until every `switch` handles it. The sealed class must be `abstract` (or an interface).
- Prefer **overriding** to `instanceof` chains, declare variables with the **most general type** you need, and make sure subclasses keep their superclass's behavioral promises (**Liskov**).
- **Generics are invariant** (`List<Dog>` is not a `List<Animal>`; use `List<? extends Animal>`), while arrays are covariant and checked at runtime.

## Related

- [[Java/00 - Syllabus|Syllabus]]
- Previous: [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]] · Next: [[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]]
- [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]]: overriding rules, `super`, hiding of fields and static methods, sealed classes
- [[01 - Methods#7.2 How the Compiler Chooses an Overload|Methods § 7.2]]: how the compiler chooses an overload (step 1 of every call)
- [[Java/01 - Foundations/04 - Type Casting#7. Reference (Object) Casting|Type Casting § 7]]: the basics of upcasting and downcasting
- [[Java/01 - Foundations/03 - Operators#10.2 `instanceof`|Operators § 10.2]]: the `instanceof` operator
- [[Java/02 - Control Flow/01 - Conditional Statements#8. Pattern Matching in `switch` (Java 21+)|Conditional Statements § 8]]: pattern `switch` syntax, guards, record patterns
- [[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]]: abstract classes and interfaces, the main tools for polymorphic design
- [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]: `equals(Object)`, `instanceof` vs. `getClass()` in `equals`
- [[Java/05 - Working with Data and Errors/02 - Generics|Generics]]: invariance, wildcards, and `instanceof` with generic types
- [[Java/02 - Control Flow/03 - Arrays#11. Array Types, Covariance, and `ArrayStoreException`|Arrays § 11]]: array covariance and `ArrayStoreException`
