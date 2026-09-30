# Generics in Java

<span class="hl-blue">Generics</span> let a class, interface, or method take **types as parameters**. You write the code once, as `Box<T>` or `<T> T max(List<T> list)`, and the caller chooses the type: `Box<String>`, `max(List<Integer>)`. The compiler then checks every use against that type, so the wrong kind of object is caught **at compile time** and no casts are needed when reading. This chapter covers generic classes, interfaces, and methods, the diamond operator, bounded type parameters, why generics are invariant, wildcards and PECS, type erasure and everything it forbids, raw types, and the autoboxing traps that come with collections of wrappers.

Generics build on interfaces and subtyping from [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]] and [[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]], and on autoboxing from [[Java/01 - Foundations/04 - Type Casting#9. Autoboxing and Unboxing (Related, Not True Casting)|Type Casting § 9]]. Their main users are [[Java/05 - Working with Data and Errors/03 - Comparable and Comparator|Comparable and Comparator]] and the collections in [[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]], which is why this chapter comes before them.

## Contents

- [[#1. Why Generics Exist|1. Why Generics Exist]]
- [[#2. Generic Classes and Interfaces|2. Generic Classes and Interfaces]]
- [[#3. Generic Methods|3. Generic Methods]]
- [[#4. Bounded Type Parameters|4. Bounded Type Parameters]]
- [[#5. Generics Are Invariant|5. Generics Are Invariant]]
- [[#6. Wildcards|6. Wildcards]]
- [[#7. Type Erasure|7. Type Erasure]]
- [[#8. Raw Types and Heap Pollution|8. Raw Types and Heap Pollution]]
- [[#9. Generics and Autoboxing — Traps|9. Generics and Autoboxing — Traps]]
- [[#10. Reading Standard-Library Signatures|10. Reading Standard-Library Signatures]]
- [[#11. Common Pitfalls|11. Common Pitfalls]]
- [[#12. Quick Reference — Non-Obvious Outcomes|12. Quick Reference — Non-Obvious Outcomes]]
- [[#13. Practice — Trick Questions|13. Practice — Trick Questions]]
- [[#14. Summary|14. Summary]]

---

## 1. Why Generics Exist

Before Java 5 (2004), collections held plain `Object`s. Anything could go in, and every read needed a cast that was only checked at runtime:

```java
List names = new ArrayList();            // pre-Java 5 style (a "raw type" today)
names.add("Ada");
names.add(42);                           // compiles: an Integer is an Object
String first  = (String) names.get(0);   // a cast on every read
String second = (String) names.get(1);   // ClassCastException at runtime
```

With generics, the list states what it holds and the compiler enforces it:

```java
List<String> names = new ArrayList<>();
names.add("Ada");
names.add(42);                  // compile error: int cannot be converted to String
String first = names.get(0);    // no cast needed
```

> [!important] Key idea
> Generics move the type check from **runtime** (`ClassCastException`, far from the bug) to **compile time** (an error on the exact line that is wrong). They exist **only for the compiler**. At runtime the type arguments are gone ([[#7. Type Erasure|§ 7]]), and `List<String>` and `List<Integer>` are the same class.

### 1.1 Terminology

> [!note] Definitions
> - A **type parameter** (or *type variable*) is the placeholder in a declaration: `T` in `class Box<T>`.
> - A **type argument** is the actual type supplied at use: `String` in `Box<String>`.
> - A **generic type** is a class or interface declared with type parameters: `Box<T>`, `List<E>`, `Map<K, V>`.
> - A **parameterized type** is a generic type with arguments filled in: `Box<String>`, `Map<String, Integer>`.
> - A **raw type** is a generic type used **without** any type arguments: plain `Box` or `List` ([[#8. Raw Types and Heap Pollution|§ 8]]).
> - A **generic method** declares its own type parameters: `static <T> T first(List<T> list)`.
>
> The pair *parameter / argument* works exactly as it does for methods: `T` is to `Box<T>` what `x` is to `square(int x)`.

By convention, type parameters are **single upper-case letters**, which keeps them visually distinct from class names:

| Name | Usual meaning | Example |
|---|---|---|
| `T` | Type (the general case) | `Box<T>`, `Optional<T>` |
| `E` | Element (of a collection) | `List<E>`, `Set<E>` |
| `K`, `V` | Key, Value | `Map<K, V>` |
| `R` | Result / return type | `Function<T, R>` |
| `N` | Number | `<N extends Number>` |
| `S`, `U`, `V` | 2nd, 3rd, 4th type | `<T, U> Pair<T, U> zip(…)` |

---

## 2. Generic Classes and Interfaces

### 2.1 Declaring and Using a Generic Class

The type parameters go in angle brackets **after the class name**. Inside the class, `T` is used like any other type:

```java
public class Box<T> {
    private T value;

    public Box(T value) { this.value = value; }

    public T get()             { return value; }
    public void set(T value)   { this.value = value; }
    public boolean isEmpty()   { return value == null; }
}

Box<String> b = new Box<>("hi");
String s = b.get();       // no cast: the compiler knows get() returns String here
b.set("bye");             // OK
b.set(42);                // compile error: int cannot be converted to String
```

Several type parameters are separated by commas. Records can be generic too:

```java
public class Pair<K, V> {
    private final K key;
    private final V value;
    public Pair(K key, V value) { this.key = key; this.value = value; }
    public K getKey()   { return key; }
    public V getValue() { return value; }
}

Pair<String, Integer> p = new Pair<>("age", 30);

record Entry<A, B>(A first, B second) { }        // generic record (Java 16+)
Entry<String, Double> e = new Entry<>("pi", 3.14);
```

Inside a generic class, `T` may be used as the type of a field, parameter, return value, or local variable, and as a type argument to other generic types (`List<T>`). It may **not** be used with `new T()`, `new T[n]`, `T.class`, `instanceof T`, or in a `static` member. Those restrictions all come from type erasure ([[#7.2 What Erasure Forbids|§ 7.2]]).

### 2.2 Type Arguments Must Be Reference Types

```java
List<int> a;             // compile error: unexpected type (required: reference, found: int)
List<Integer> b;         // OK: use the wrapper class
List<int[]> c;           // OK: an array is an object, even an array of primitives
```

Autoboxing makes wrapper type arguments mostly painless:

```java
List<Integer> nums = new ArrayList<>();
nums.add(5);             // int 5 is boxed to Integer
int x = nums.get(0);     // Integer is unboxed to int
```

The boxing is still there, though, and it causes some of the nastiest bugs with generic collections ([[#9. Generics and Autoboxing — Traps|§ 9]]). It also explains the `Arrays.asList(int[])` trap in [[Java/02 - Control Flow/03 - Arrays#8.4 `asList`|Arrays § 8.4]]: `T` can't be `int`, so the whole `int[]` becomes a single element.

### 2.3 The Diamond Operator

Since Java 7, the type arguments on the right-hand side of `new` can be left out and written as `<>` (the <span class="hl-blue">diamond</span>). The compiler infers them from the **target**: the declared variable, the parameter being passed to, or the return type.

```java
Map<String, List<Integer>> m1 = new HashMap<String, List<Integer>>();  // before Java 7
Map<String, List<Integer>> m2 = new HashMap<>();                       // Java 7+: same thing

List<String> names() { return new ArrayList<>(); }                     // inferred from the return type
printAll(new ArrayList<>());                                           // inferred from the parameter type
```

> [!warning] Common mistake: `new ArrayList()` is not the diamond
> ```java
> List<String> a = new ArrayList<>();   // diamond: ArrayList<String>
> List<String> b = new ArrayList();     // RAW type: compiles, but with an "unchecked" warning
> ```
> Forgetting the `<>` silently creates a raw type ([[#8. Raw Types and Heap Pollution|§ 8]]). It happens to work in this line, but it switches off the compiler's checks for that expression.

> [!warning] Trick: `var` plus diamond infers `Object`
> ```java
> var a = new ArrayList<>();         // ArrayList<Object>: there is no target to infer from
> var b = new ArrayList<String>();   // ArrayList<String>
>
> a.add("x");
> a.add(1);                          // both compile: a holds Objects
> String s = a.get(0);               // compile error: Object cannot be converted to String
> ```
> With `var`, the type argument must be written on the right. Note also that `var` gives the **concrete** type (`ArrayList<String>`), not the interface (`List<String>`). See [[Java/01 - Foundations/02 - Variables and Data Types#9. Type Inference with `var`|Variables and Data Types § 9]].

The diamond can be used with anonymous classes only since Java 9. In Java 7–8, `new Comparator<>() { … }` was a compile error.

### 2.4 Generic Interfaces

Interfaces take type parameters the same way. The standard library is full of them: `Comparable<T>`, `Comparator<T>`, `Iterable<T>`, `List<E>`, `Map<K, V>`, `Function<T, R>`.

```java
public interface Container<T> {
    void put(T item);
    T take();
}
```

A class implementing a generic interface has three options:

```java
class StringStack implements Container<String> {   // 1. fix the type argument
    public void put(String item) { … }
    public String take() { … }
}

class Stack<T> implements Container<T> {           // 2. stay generic and pass T through
    public void put(T item) { … }
    public T take() { … }
}

class OldStack implements Container {              // 3. raw type: methods take and return Object. Avoid.
    public void put(Object item) { … }
    public Object take() { … }
}
```

The most common case is `Comparable`, which gives a class a natural ordering:

```java
class Student implements Comparable<Student> {
    String name;
    double gpa;

    @Override
    public int compareTo(Student other) {
        return Double.compare(this.gpa, other.gpa);
    }
}
```

> [!warning] Common mistake: implementing the raw `Comparable`
> ```java
> class Student implements Comparable {             // raw type
>     public int compareTo(Student other) { … }     // compile error: Student is not abstract
> }                                                 // and does not override compareTo(Object)
> ```
> With the raw interface, the method to implement is `compareTo(Object)`. A `compareTo(Student)` is just an overload, so the class doesn't satisfy the interface. Write `implements Comparable<Student>`.

### 2.5 Extending and Implementing Generic Types

```java
class Box<T> { … }

class StringBox extends Box<String> { }              // non-generic subclass: T is fixed to String
class LabeledBox<T> extends Box<T> { String label; } // generic subclass: passes its T up
class PairBox<T, U> extends Box<T> { U extra; }      // adds a second parameter of its own
class Bad extends Box<T> { }                         // compile error: cannot find symbol T
```

In `Bad`, `T` was never declared: a type parameter must be introduced (`class Bad<T>`) before it can be used.

Not everything can be generic:

- **Enums** can't declare type parameters (`enum Color<T>` is a compile error).
- **Anonymous classes** can't declare type parameters (they have no name to put them on).
- **Exception classes** can't be generic ([[#7.2 What Erasure Forbids|§ 7.2]]).

### 2.6 Type Parameters and `static`

```java
class Box<T> {
    static T defaultValue;                    // compile error: non-static type variable T
    static T make() { … }                     //   cannot be referenced from a static context

    static <U> Box<U> of(U value) {           // OK: a static GENERIC METHOD with its own parameter
        return new Box<>(value);
    }

    static int created = 0;                   // ONE counter, shared by Box<String>, Box<Integer>, …
    Box() { created++; }
}
```

The class's `T` belongs to each **object**: one box is a `Box<String>`, another is a `Box<Integer>`. Static members belong to the **class**, and at runtime there is only one class `Box` ([[#7. Type Erasure|§ 7]]). So a static member can't know which `T` is meant, and a static field is shared by every parameterization. Access it as `Box.created`: `Box<String>.created` is not valid syntax.

---

## 3. Generic Methods

### 3.1 Declaring and Calling

A generic method declares its own type parameters in angle brackets **between the modifiers and the return type**. It can live in any class, generic or not, and can be `static` or not.

```java
public class Util {
    public static <T> T last(List<T> list) {
        return list.get(list.size() - 1);
    }

    public static <K, V> Map<V, K> invert(Map<K, V> map) {
        Map<V, K> result = new HashMap<>();
        for (Map.Entry<K, V> e : map.entrySet()) {
            result.put(e.getValue(), e.getKey());
        }
        return result;
    }

    public static <T> void swap(T[] a, int i, int j) {
        T tmp = a[i];
        a[i] = a[j];
        a[j] = tmp;
    }
}

String s = Util.last(List.of("a", "b"));   // T = String
Integer n = Util.last(List.of(1, 2, 3));   // T = Integer
```

> [!warning] Common mistakes in the header
> ```java
> public static <T> T f(T x)   // ✅ type parameters right before the return type
> public <T> static T f(T x)   // ❌ compile error: <T> must come after ALL modifiers
> public static T <T> f(T x)   // ❌ compile error: <T> must come before the return type
> public static T f(T x)       // ❌ in a non-generic class: cannot find symbol T (never declared)
> ```

> [!warning] Trick: generic methods don't accept primitive arrays
> ```java
> String[] s = {"a", "b"};
> Util.swap(s, 0, 1);       // OK: T = String
>
> int[] n = {1, 2};
> Util.swap(n, 0, 1);       // compile error: T can't be int, and int[] is not a T[] for any T
> ```
> `Integer[]` works. This is why `java.util.Arrays` has a separate `sort(int[])`, `sort(double[])`, … for every primitive type instead of one generic version.

### 3.2 Type Inference and Explicit Type Arguments

Usually the compiler **infers** the type arguments from the method arguments and, if needed, from the target type:

```java
List<String> empty = Collections.emptyList();   // T inferred as String from the target
```

The type argument can also be written explicitly (a *type witness*). It must then be qualified by a class name, `this`, or an object:

```java
List<String> a = Collections.<String>emptyList();   // OK
this.<String>helper();                              // OK
<String>helper();                                   // compile error: illegal start of expression
```

> [!warning] Trick: two `T` parameters don't force the same type
> ```java
> static <T> boolean same(T a, T b) { return a.equals(b); }
>
> same("1", 1);    // compiles! T is inferred as a common supertype of String and Integer
>                  // (at least Object), so the call returns false
> same(1, 1L);     // compiles, returns false: Integer vs. Long
> ```
> `T` only means "some type that both arguments fit". With no bound, `Object` always fits. To really force matching types, the relationship has to come from elsewhere, e.g. `<T> void add(List<T> list, T item)`, where the list fixes `T`.

### 3.3 A Method's Type Parameter Shadows the Class's

```java
class Box<T> {
    private T value;

    <T> void set(T v) {      // this <T> declares a NEW type parameter that hides the class's T
        value = v;           // compile error: incompatible types: T#1 cannot be converted to T#2
    }
}
```

The error message looks absurd at first: `T` can't be converted to `T`. javac numbers them `T#1` and `T#2` because they are two **different** type variables that happen to share a name. An instance method that wants the class's `T` simply uses it, without declaring `<T>` again: `void set(T v)`.

---

## 4. Bounded Type Parameters

### 4.1 Upper Bounds with `extends`

An unbounded `T` could be any type, so the compiler only lets you call `Object`'s methods on it:

```java
static <T> T max(T a, T b) {
    return a.compareTo(b) >= 0 ? a : b;     // compile error: cannot find symbol compareTo(T)
}
```

A <span class="hl-blue">bound</span> restricts which type arguments are allowed and, in exchange, lets the code use the bound's methods:

```java
static <T extends Comparable<T>> T max(T a, T b) {
    return a.compareTo(b) >= 0 ? a : b;     // OK: every T has compareTo
}

static <T extends Number> double sum(List<T> list) {
    double total = 0;
    for (T x : list) {
        total += x.doubleValue();            // OK: every T is a Number
    }
    return total;
}

sum(List.of(1, 2, 3));      // 6.0   (T = Integer)
sum(List.of(1.5, 2.5));     // 4.0   (T = Double)
sum(List.of("a"));          // compile error: String is not within the bound of T
```

> [!important] Rules for bounds
> - In a bound, `extends` means "**is a subtype of**", for classes **and** interfaces alike. `implements` never appears in a bound: `<T implements Comparable<T>>` is a compile error.
> - The bound itself is allowed: `sum(List<Number>)` works, because `Number` is a subtype of itself.
> - Type parameters have **no lower bounds**. `<T super Integer>` is a compile error. `super` exists only on wildcards ([[#6.3 The Lower-Bounded Wildcard `? super T`|§ 6.3]]).

### 4.2 Multiple Bounds

A type parameter can have several bounds, joined with `&`. **At most one** of them may be a class, and it must come **first**; the rest must be interfaces.

```java
class Stats<T extends Number & Comparable<T>> { … }

<T extends Number & Comparable<T>>          // ✅ class first, then interfaces
<T extends Comparable<T> & Number>          // ❌ compile error: the class bound must come first
<T extends Integer & Double>                // ❌ compile error: two classes
<T extends Comparable<T> & Serializable>    // ✅ only interfaces: any order
```

<span class="hl-yellow">Trick case:</span> for `Stats` above, `Stats<Integer>` and `Stats<Double>` compile, but `Stats<Number>` does **not**. `Number` itself doesn't implement `Comparable`, so it satisfies only the first bound. `Stats<String>` fails the first bound.

With multiple bounds, the **first** bound decides the erased type ([[#7.1 What the Compiler Does|§ 7.1]]).

### 4.3 Recursive Bounds and `Comparable`

`<T extends Comparable<T>>` reads "`T` can be compared with other `T`s". It is the standard way to write "any type with a natural ordering":

```java
static <T extends Comparable<T>> T maxOf(List<T> list) {
    T best = list.get(0);
    for (T x : list) {
        if (x.compareTo(best) > 0) best = x;
    }
    return best;
}

maxOf(List.of(3, 9, 4));          // 9
maxOf(List.of("pear", "apple"));  // "pear"
```

This bound is slightly too strict when `compareTo` is inherited:

```java
class Animal implements Comparable<Animal> {
    int weight;
    public int compareTo(Animal o) { return Integer.compare(weight, o.weight); }
}
class Dog extends Animal { }

List<Dog> dogs = List.of(new Dog(), new Dog());
maxOf(dogs);    // compile error: Dog is a Comparable<Animal>, not a Comparable<Dog>
```

The fix is a wildcard: `<T extends Comparable<? super T>>`, "`T` can be compared with `T` **or some supertype of `T`**". This is exactly the signature of `Collections.sort` and `Collections.max` ([[#10. Reading Standard-Library Signatures|§ 10]]), and the reasoning behind it is PECS ([[#6.4 PECS — Producer `extends`, Consumer `super`|§ 6.4]]).

---

## 5. Generics Are Invariant

### 5.1 Why the Rule Exists

`Integer` is a subtype of `Number`, yet <span class="hl-yellow">`List<Integer>` is **not** a subtype of `List<Number>`</span>. Generic types are <span class="hl-blue">invariant</span>: for two different types `A` and `B`, `List<A>` and `List<B>` are unrelated, whatever the relationship between `A` and `B`.

```java
List<Integer> ints = new ArrayList<>(List.of(1, 2));
List<Number> nums = ints;           // compile error: incompatible types
List<Object> objs = ints;           // compile error, too: not even List<Object> is a supertype
```

If the second line were allowed, the list could be corrupted without any cast:

```java
nums.add(3.14);                     // a Double is a Number, so this would be legal…
Integer i = ints.get(2);            // …and this would throw ClassCastException
```

The compiler can't allow that, so it rejects the assignment. When a method really needs "a list of any kind of number", the answer is a wildcard: `List<? extends Number>` ([[#6.2 The Upper-Bounded Wildcard `? extends T`|§ 6.2]]).

### 5.2 Arrays vs. Generics

Arrays made the opposite choice, and pay for it with a runtime check ([[Java/02 - Control Flow/03 - Arrays#11.2 Covariance and `ArrayStoreException`|Arrays § 11.2]]):

```java
Object[] objs = new Integer[2];     // compiles: arrays are covariant
objs[0] = "hello";                  // compiles, throws ArrayStoreException at runtime

List<Object> list = new ArrayList<Integer>();   // doesn't compile: generics are invariant
```

| | Arrays | Generics |
|---|---|---|
| Subtyping | **covariant**: `Integer[]` is an `Object[]` | **invariant**: `List<Integer>` is not a `List<Object>` |
| Element type at runtime | kept (**reified**) | removed (**erased**) |
| A wrong element is caught… | at runtime (`ArrayStoreException`) | at compile time |
| Primitive elements | allowed (`int[]`) | not allowed (`List<int>`) |
| Generic arrays (`new T[n]`, `new List<String>[n]`) | — | not allowed ([[#7.2 What Erasure Forbids|§ 7.2]]) |

This clash between the two models is why arrays and generics don't mix well ([[Java/02 - Control Flow/03 - Arrays#11.3 Arrays and Generics Don't Mix|Arrays § 11.3]]). Prefer `List<T>` over `T[]` in generic code.

### 5.3 What Is a Subtype

Invariance only concerns the **type argument**. Subtyping along the generic **class** works as usual, and wildcards add flexibility:

| Assignment | Compiles? | Why |
|---|---|---|
| `List<String> l = new ArrayList<String>();` | ✅ | `ArrayList<String>` implements `List<String>` |
| `Collection<String> c = new ArrayList<String>();` | ✅ | same argument, supertype along the class |
| `Iterable<String> it = new ArrayList<String>();` | ✅ | same |
| `List<Object> l = new ArrayList<String>();` | ❌ | different argument: invariance |
| `ArrayList<String> a = new List<String>();` | ❌ | `List` is an interface: can't be instantiated |
| `List<?> l = new ArrayList<String>();` | ✅ | every `List<X>` is a `List<?>` |
| `List<? extends Number> l = new ArrayList<Integer>();` | ✅ | `Integer` is within `? extends Number` |
| `List<? super Integer> l = new ArrayList<Number>();` | ✅ | `Number` is within `? super Integer` |
| `List<? extends Number> l = new ArrayList<String>();` | ❌ | `String` is not a `Number` |
| `List raw = new ArrayList<String>();` | ✅ | parameterized → raw is always allowed |
| `List<String> l = new ArrayList();` | ⚠️ | raw → parameterized: compiles with an unchecked warning |

![[Generics - Invariance and Wildcards.excalidraw|800]]

---

## 6. Wildcards

A <span class="hl-blue">wildcard</span> `?` in a type argument stands for "some **unknown** type". It restores the flexibility that invariance takes away, at the price of limiting what can be done with the object.

### 6.1 The Unbounded Wildcard `?`

`List<?>` means "a list of some specific type, but I don't know which":

```java
static void printAll(List<?> list) {
    for (Object o : list) {         // every element is at least an Object
        System.out.println(o);
    }
}

printAll(List.of(1, 2));            // OK
printAll(List.of("a", "b"));        // OK
```

Reading gives `Object`. Adding is forbidden, because the compiler can't check the element against an unknown type. The one exception is `null`, which belongs to every reference type. Methods that don't take the element type still work:

```java
List<?> list = new ArrayList<>(List.of("a", "b"));
list.add("c");          // compile error: the list might be a List<Integer>
list.add(null);         // compiles
list.size();            // OK
list.remove("a");       // compiles! remove takes an Object, not an E
list.contains(42);      // compiles, returns false (contains takes an Object too)
list.clear();           // OK
```

<span class="hl-yellow">`List<?>` vs. `List<Object>` vs. raw `List`</span> are three different things:

| | `List<Object>` | `List<?>` | `List` (raw) |
|---|---|---|---|
| Accepts a `List<String>`? | ❌ | ✅ | ✅ |
| `add("x")`? | ✅ | ❌ | ⚠️ with an unchecked warning |
| Type of `get(0)` | `Object` | `Object` | `Object` |
| Type-safe? | yes | yes | **no** |
| Meaning | a list that may hold anything | a list of *some* type I don't know | generics switched off |

### 6.2 The Upper-Bounded Wildcard `? extends T`

`List<? extends Number>` means "a list of `Number` or of some subtype of `Number`". Every element can be **read as a `Number`**, but nothing can be **added**:

```java
static double sum(List<? extends Number> list) {
    double total = 0;
    for (Number n : list) {
        total += n.doubleValue();
    }
    return total;
}

sum(List.of(1, 2));              // OK: List<Integer>
sum(List.of(1.5, 2.5));          // OK: List<Double>
sum(new ArrayList<Number>());    // OK

List<? extends Number> nums = new ArrayList<Integer>();
nums.add(1);                     // compile error
nums.add(1.5);                   // compile error
nums.add(null);                  // compiles
Number first = nums.get(0);      // OK (if the list isn't empty)
```

Why can't `nums.add(1)` compile when the list really is an `ArrayList<Integer>`? Because the compiler only sees the declared type. `List<? extends Number>` might just as well be a `List<Double>`, and an `Integer` doesn't belong there. The same reasoning rejects every type, so the list is **read-only** (except for `null` and removals).

### 6.3 The Lower-Bounded Wildcard `? super T`

`List<? super Integer>` means "a list of `Integer` or of some **supertype** of `Integer`": `List<Integer>`, `List<Number>`, or `List<Object>`. Any `Integer` can be **added**, but reading gives only `Object`:

```java
static void fillOneToN(List<? super Integer> list, int n) {
    for (int i = 1; i <= n; i++) {
        list.add(i);                  // OK: an Integer fits all three possible lists
    }
}

fillOneToN(new ArrayList<Integer>(), 3);   // OK
fillOneToN(new ArrayList<Number>(), 3);    // OK
fillOneToN(new ArrayList<Object>(), 3);    // OK
fillOneToN(new ArrayList<Double>(), 3);    // compile error: Double is not a supertype of Integer

List<? super Integer> list = new ArrayList<Number>();
list.add(5);                  // OK
list.add(2.5);                // compile error: a Double is not an Integer
Object o = list.get(0);       // OK
Number n = list.get(0);       // compile error: the list could be a List<Object>
Integer i = list.get(0);      // compile error
```

### 6.4 PECS — Producer `extends`, Consumer `super`

<span class="hl-yellow">PECS</span> is the rule of thumb for choosing a wildcard, from the point of view of **the method** using the parameter:

| The parameter… | Use | You can | Example |
|---|---|---|---|
| **produces** values the method reads | `? extends T` | read as `T` | the source in a copy, a list to sum |
| **consumes** values the method writes | `? super T` | write a `T` | the destination in a copy, a `Comparator` |
| does both | exact `T` | read and write | a list the method sorts in place |
| does neither with its elements | `?` | size, clear, … | `printAll`, `size` |

```java
static <T> void copy(List<? super T> dest, List<? extends T> src) {
    for (T item : src) {        // src PRODUCES Ts
        dest.add(item);         // dest CONSUMES Ts
    }
}

List<Integer> ints = List.of(1, 2, 3);
List<Number> nums = new ArrayList<>();
List<Object> objs = new ArrayList<>();

copy(nums, ints);     // OK: Integers into a List<Number>
copy(objs, ints);     // OK: Integers into a List<Object>
copy(ints, nums);     // compile error: Numbers can't go into a List<Integer>
```

![[Generics - PECS.excalidraw|800]]

A `Comparator<? super T>` is a consumer: it *takes* `T`s to compare them. That is why a `Comparator<Animal>` can sort a `List<Dog>`, and why `List.sort` is declared as `sort(Comparator<? super E> c)`.

> [!tip] Tip
> Wildcards belong in **parameters**, not in **return types**. A method returning `List<? extends Number>` forces every caller to work with a read-only list of unknown type. Return `List<Number>` or a generic `List<T>` instead.

### 6.5 Wildcard or Type Parameter?

Many signatures can be written either way:

```java
static void printAll(List<?> list)          // wildcard
static <T> void printAll(List<T> list)      // type parameter: equivalent here
```

- If the type appears **once** and nothing else depends on it, prefer the **wildcard**: it's simpler and says "I don't care".
- If the type must **link** several parameters, or a parameter and the return type, use a **type parameter**: `static <T> T first(List<T> list)`, `static <T> void addTwice(List<T> list, T item)`.

> [!info]- Wildcard capture: why `List<?>` can't even swap its own elements
> ```java
> static void swap(List<?> list, int i, int j) {
>     list.set(i, list.get(j));   // compile error: Object cannot be converted to capture of ?
> }
> ```
> `list.get(j)` returns an `Object`, and `set` needs "the unknown type", so the compiler refuses, even though the element came out of the same list. The standard fix is a private generic helper that gives the unknown type a name (this is called *capturing* the wildcard):
> ```java
> static void swap(List<?> list, int i, int j) {
>     swapHelper(list, i, j);           // T is inferred as "the capture of ?"
> }
> private static <T> void swapHelper(List<T> list, int i, int j) {
>     T tmp = list.get(i);
>     list.set(i, list.get(j));
>     list.set(j, tmp);
> }
> ```
> `Collections.swap(List<?> list, int i, int j)` has exactly this public signature.

### 6.6 Where Wildcards Can't Appear

A wildcard describes a variable's type. It can't be used to **create** something or to **declare** a type:

```java
new ArrayList<?>()                     // compile error: can't instantiate an unknown type
new ArrayList<? extends Number>()      // compile error
class Box<?> { }                       // compile error: type parameters need names
class MyList extends ArrayList<?> { }  // compile error: a supertype may not specify a wildcard
Util.<?>last(list)                     // compile error: explicit type arguments can't be wildcards

new ArrayList<List<?>>()               // OK: the wildcard is nested, the list itself is concrete
List<?>[] arr = new List<?>[3];        // OK: unbounded-wildcard arrays are allowed (see § 7.2)
```

---

## 7. Type Erasure

### 7.1 What the Compiler Does

Generics were added in Java 5 without changing the JVM, so that old compiled code would keep working. The compiler therefore checks the generic types and then **erases** them. This is called <span class="hl-blue">type erasure</span>:

```java
// What you write
class Box<T> {
    private T value;
    T get()          { return value; }
    void set(T v)    { value = v; }
}
Box<String> b = new Box<>();
b.set("hi");
String s = b.get();

// Roughly what the compiled bytecode contains
class Box {
    private Object value;
    Object get()       { return value; }
    void set(Object v) { value = v; }
}
Box b = new Box();
b.set("hi");
String s = (String) b.get();     // cast inserted by the compiler
```

| Before erasure | After erasure |
|---|---|
| `T` (unbounded) | `Object` |
| `T extends Number` | `Number` |
| `T extends Number & Comparable<T>` | `Number` (the **first** bound) |
| `List<String>`, `List<T>`, `List<?>` | `List` |
| a read of a `T` value where a `String` is needed | a cast `(String)` |

So at runtime there is just one class:

```java
List<String>  a = new ArrayList<>();
List<Integer> b = new ArrayList<>();
System.out.println(a.getClass() == b.getClass());   // true: both are plain ArrayList
System.out.println(a.getClass().getName());         // java.util.ArrayList
```

![[Generics - Type Erasure.excalidraw|800]]

> [!info]- Bridge methods
> Erasure can break overriding. `Student implements Comparable<Student>` defines `compareTo(Student)`, but after erasure the interface method is `compareTo(Object)`. They no longer have the same signature. The compiler silently adds a **bridge method** to connect them:
> ```java
> public int compareTo(Object o) {          // generated by the compiler
>     return compareTo((Student) o);        // calls the real method
> }
> ```
> This is invisible in normal code. It explains why calling `compareTo` through a raw `Comparable` with the wrong type throws `ClassCastException` from a line you never wrote, and why stack traces sometimes show a method twice.

### 7.2 What Erasure Forbids

Since `T` doesn't exist at runtime, nothing that needs the type argument **at runtime** can compile:

| You can't write | Why | Workaround |
|---|---|---|
| `new T()` | the class to instantiate is unknown | take a `Supplier<T>` or a `Class<T>` parameter |
| `new T[n]` | generic array creation | use a `List<T>`, or `(T[]) new Object[n]` with an unchecked warning |
| `new List<String>[n]` | generic array creation | `List<List<String>>`, or `new List<?>[n]` |
| `obj instanceof T` | `T` is erased | pass a `Class<T> type` and call `type.isInstance(obj)` |
| `obj instanceof List<String>` (with `obj` an `Object`) | the `String` part can't be checked | `obj instanceof List<?>` |
| `T.class`, `List<String>.class` | there is only one `Class` object | `List.class` |
| `static T field;` | [[#2.6 Type Parameters and `static`|§ 2.6]] | a static generic method |
| `class MyEx<T> extends Exception` | a generic class may not extend `Throwable` | store the extra data in a field of type `Object` |
| `catch (T e)` | `catch` needs a runtime type | `throws T` **is** allowed: `<T extends Exception> void f() throws T` |
| `List<int>` | [[#2.2 Type Arguments Must Be Reference Types|§ 2.2]] | `List<Integer>` |

> [!info]- `instanceof` with a parameterized type (Java 16+)
> Since Java 16, `instanceof` with a parameterized type **is** allowed when the compiler can prove it's safe from the static type alone:
> ```java
> List<String> list = getList();
> if (list instanceof ArrayList<String> al) { … }   // OK: only "is it an ArrayList?" is checked at runtime
>
> Object o = getList();
> if (o instanceof List<String> l) { … }            // still a compile error: Object says nothing about String
> ```

> [!warning] Trick: the `(T[]) new Object[n]` array escapes
> ```java
> class Stack<T> {
>     private T[] items = (T[]) new Object[10];   // unchecked warning, but fine INSIDE the class
>     private int size;
>     void push(T x)  { items[size++] = x; }
>     T peek()        { return items[size - 1]; }
>     T[] toArray()   { return Arrays.copyOf(items, size); }
> }
>
> Stack<String> s = new Stack<>();
> s.push("a");
> String top = s.peek();          // OK: the inserted cast is (String), and the element is a String
> String[] all = s.toArray();     // ClassCastException: Object[] cannot be cast to String[]
> ```
> The array is really an `Object[]`. As long as it stays private this doesn't matter, but as soon as it is handed out as a `T[]`, the cast the compiler inserts at the call site fails. This is why `ArrayList.toArray()` returns `Object[]`, and `toArray(T[] a)` asks the caller for an array of the right type.

### 7.3 Overloads That Clash After Erasure

Two methods whose parameter types **erase to the same thing** can't coexist, even though they look different in the source:

```java
void print(List<String> list)  { … }
void print(List<Integer> list) { … }     // compile error: name clash: both have the same erasure print(List)

<T> void f(T x)       { … }
void f(Object x)      { … }              // compile error: both erase to f(Object)

<T extends Number> void g(T x) { … }
void g(Object x)               { … }     // OK: g(Number) and g(Object) are different
```

A different return type doesn't help, since the return type is not part of the signature (see [[Java/03 - Program Structure/01 - Methods#7.1 What Does and Doesn't Count as a Different Overload|Methods § 7.1]]). Use different method names instead: `printStrings`, `printInts`.

### 7.4 Unchecked Casts and Warnings

A cast to a parameterized type compiles, but it can only check the **erased** part:

```java
Object o = List.of(1, 2);
List<String> strings = (List<String>) o;    // unchecked warning; only "is it a List?" is checked
String s = strings.get(0);                  // ClassCastException happens HERE, not on the cast
```

An **unchecked warning** means "the compiler can no longer guarantee type safety here". Ignoring one can cause a `ClassCastException` at a line that contains no cast at all. `@SuppressWarnings("unchecked")` hides the warning. Use it only when you have proven the operation safe, and on the smallest possible scope (one variable declaration or one method, never a whole class).

> [!info]- Generic varargs and `@SafeVarargs`
> A varargs parameter is an array ([[Java/03 - Program Structure/01 - Methods#8. Variable-Length Arguments (Varargs)|Methods § 8]]), so `static <T> List<T> listOf(T... items)` really creates a `T[]`, a generic array. The compiler allows it but warns about *possible heap pollution*. A method that only reads from the array can be marked `@SafeVarargs` to suppress the warning at every call site. `Arrays.asList` and `List.of` are marked this way.

---

## 8. Raw Types and Heap Pollution

A <span class="hl-blue">raw type</span> is a generic type used without type arguments: `List`, `Box`, `Comparable`. Raw types exist only so that pre-Java-5 code still compiles. **Don't use them in new code.**

```java
List<String> strings = new ArrayList<>();
List raw = strings;              // allowed, no warning: parameterized → raw
raw.add(42);                     // unchecked warning: an Integer now sits in a List<String>

System.out.println(strings.size());   // 1
Object o = strings.get(0);            // no exception: no cast is needed to store it in an Object
String s = strings.get(0);            // ClassCastException: Integer cannot be cast to String
```

<span class="hl-blue">Heap pollution</span> is exactly this situation: a variable of a parameterized type refers to an object that doesn't match it. The error appears only where the compiler inserted a cast, which may be far away from the real bug (the `raw.add(42)` line).

> [!warning] Trick: a raw type erases ALL of its generic members
> Using a raw type erases generics from **every** member, even members unrelated to the class's own type parameter:
> ```java
> class Course<T> {
>     List<String> students() { return List.of("Ada", "Alan"); }
> }
>
> Course<Integer> c1 = new Course<>();
> for (String s : c1.students()) { }   // OK
>
> Course c2 = new Course();            // raw
> for (String s : c2.students()) { }   // compile error: Object cannot be converted to String
> ```
> On the raw `Course`, `students()` returns a raw `List`, whose elements are `Object`s.

Raw types are still needed in two places, because there is no parameterized form:

- **class literals**: `List.class` (not `List<String>.class`)
- **`instanceof`** on an `Object`: `obj instanceof List` (or, better, `obj instanceof List<?>`)

---

## 9. Generics and Autoboxing — Traps

Generic collections hold wrappers (`Integer`, `Long`, …), not primitives. The automatic boxing and unboxing between them causes several classic bugs.

### 9.1 `remove(int)` vs. `remove(Object)`

`List<E>` has two `remove` methods: `remove(int index)` and `remove(Object o)`. With a `List<Integer>`, both look applicable:

```java
List<Integer> list = new ArrayList<>(List.of(10, 20, 30, 1));
list.remove(1);                    // removes the element at INDEX 1 (20)  → [10, 30, 1]
list.remove(Integer.valueOf(1));   // removes the VALUE 1                  → [10, 30]
```

`remove(1)` matches `remove(int)` exactly, in phase 1 of overload resolution, before boxing is ever tried ([[Java/03 - Program Structure/01 - Methods#7.2 How the Compiler Chooses an Overload|Methods § 7.2]]). To remove a value, pass an `Integer`: `Integer.valueOf(1)` or `(Integer) 1`.

### 9.2 Methods That Take `Object` Accept the Wrong Type

`remove`, `contains`, `indexOf` and `Map.get` / `containsKey` take an **`Object`**, not an `E`. So passing the wrong type is **not** a compile error. It just never matches:

```java
Set<Short> set = new HashSet<>();
for (short i = 0; i < 100; i++) {
    set.add(i);          // boxes a Short
    set.remove(i - 1);   // i - 1 is an int → boxes an Integer, which never equals a Short
}
System.out.println(set.size());    // 100, not 1
```

```java
Map<Long, String> m = new HashMap<>();
m.put(1L, "one");
m.get(1);        // null: the key is boxed to Integer 1, and Integer.equals(Long) is false
m.get(1L);       // "one"
m.put(2, "two"); // compile error: put takes a K (Long), and int can't become Long
```

### 9.3 `==` on Boxed Elements

```java
List<Integer> a = List.of(100, 100);
List<Integer> b = List.of(1000, 1000);
a.get(0) == a.get(1);        // true: small values come from the Integer cache (−128 … 127)
b.get(0) == b.get(1);        // usually false: two different Integer objects
b.get(0).equals(b.get(1));   // true: always compare wrapper values with equals
```

See [[Java/01 - Foundations/04 - Type Casting#9. Autoboxing and Unboxing (Related, Not True Casting)|Type Casting § 9]] and [[Java/01 - Foundations/03 - Operators#7.3 `==` on References Compares Identity, Not Content|Operators § 7.3]].

### 9.4 Unboxing `null`

```java
Map<String, Integer> counts = new HashMap<>();
int c = counts.get("missing");              // NullPointerException: get returns null, which can't unbox
int d = counts.getOrDefault("missing", 0);  // 0
```

### 9.5 No Widening Plus Boxing

```java
List<Long> longs = new ArrayList<>();
longs.add(5);        // compile error: int can't be converted to Long (Java won't widen AND box)
longs.add(5L);       // OK

List<Double> ds = new ArrayList<>();
ds.add(1);           // compile error for the same reason
ds.add(1.0);         // OK
```

---

## 10. Reading Standard-Library Signatures

The standard library's signatures look intimidating, but they are just the rules of this chapter combined:

| Signature | Read it as |
|---|---|
| `boolean addAll(Collection<? extends E> c)` in `List<E>` | add all elements of a collection of `E` or any subtype (a producer) |
| `void sort(Comparator<? super E> c)` in `List<E>` | a comparator for `E` or any supertype of `E` (a consumer) |
| `static <T extends Comparable<? super T>> void sort(List<T> list)` in `Collections` | `T` must be comparable to itself, possibly via a supertype ([[#4.3 Recursive Bounds and `Comparable`|§ 4.3]]) |
| `static <T> void copy(List<? super T> dest, List<? extends T> src)` | PECS: read from `src`, write to `dest` |
| `static <T extends Object & Comparable<? super T>> T max(Collection<? extends T> coll)` | like `sort`, see below for the `Object &` |
| `V get(Object key)` in `Map<K, V>` | takes any `Object`, not just a `K` ([[#9.2 Methods That Take `Object` Accept the Wrong Type|§ 9.2]]) |
| `static <T> List<T> of(T... elements)` in `List` | generic varargs factory; `T` inferred from the arguments |
| `interface Function<T, R> { R apply(T t); }` | takes a `T`, returns an `R` |

> [!info]- Why does `Collections.max` say `T extends Object & Comparable<…>`?
> Every `T` already extends `Object`, so the `Object &` adds no restriction. It is there for **erasure**: the erasure of a type parameter is its first bound. With `Object` first, `max` erases to `Object max(Collection)`, exactly the signature it had before Java 5, so old compiled code calling it still links. With just `Comparable<? super T>`, it would have erased to `Comparable max(Collection)` and broken binary compatibility.

---

## 11. Common Pitfalls

- **Forgetting the diamond**: `new ArrayList()` is a raw type, not `new ArrayList<>()`.
- **`var x = new ArrayList<>();`** gives an `ArrayList<Object>`.
- **Using a primitive as a type argument** (`List<int>`). Use the wrapper class.
- **Expecting `List<Integer>` to be a `List<Number>`** (or `List<Object>`). Generics are invariant; use `List<? extends Number>`.
- **Trying to add to a `List<? extends T>`** or to a `List<?>`. Only `null` can be added.
- **Reading from a `List<? super T>` as a `T`**. Reading gives only `Object`.
- **Mixing up PECS**: `extends` for what you read from, `super` for what you write to.
- **Writing `implements` in a bound**, or putting the class bound after an interface bound.
- **Calling methods on an unbounded `T`** (`a.compareTo(b)`). Add a bound.
- **Using `<T extends Comparable<T>>` where subclasses must work**. Use `Comparable<? super T>`.
- **Declaring `<T>` on a method of a generic class** and accidentally shadowing the class's `T`.
- **Using `T` in a `static` member** of a generic class.
- **`new T()`, `new T[n]`, `instanceof T`, `T.class`**: all impossible because of erasure.
- **Overloading on type arguments only** (`f(List<String>)` / `f(List<Integer>)`): a name clash after erasure.
- **Ignoring unchecked warnings**. They lead to heap pollution and a `ClassCastException` on a line without a cast.
- **Raw types in new code**, including a raw `implements Comparable`.
- **`list.remove(1)` on a `List<Integer>`** removes an index, not a value.
- **Passing the wrong key type** to `get`, `remove`, `contains`: it compiles and silently doesn't match (`Map<Long, …>.get(1)`).
- **Comparing boxed elements with `==`**.
- **Unboxing a `null`** returned by `Map.get`.
- **Returning the internal `(T[]) new Object[n]` array** from a generic class as a `T[]`.

---

## 12. Quick Reference — Non-Obvious Outcomes

| Code | Result | Why |
|---|---|---|
| `List<int> l;` | compile error | type arguments must be reference types |
| `List<int[]> l;` | compiles | arrays are objects |
| `var l = new ArrayList<>();` | `ArrayList<Object>` | nothing to infer from |
| `List<String> l = new ArrayList();` | compiles, unchecked warning | raw type, not the diamond |
| `List<Number> l = new ArrayList<Integer>();` | compile error | invariance |
| `List<Object> l = new ArrayList<String>();` | compile error | invariance |
| `List<?> l = new ArrayList<String>();` | compiles | every `List<X>` is a `List<?>` |
| `List<?> l;` then `l.add("x")` | compile error | unknown element type |
| `List<?> l;` then `l.add(null)` | compiles | `null` fits every type |
| `List<?> l;` then `l.remove("x")` | compiles | `remove` takes `Object` |
| `List<? extends Number> l;` then `l.add(1)` | compile error | `l` could be a `List<Double>` |
| `List<? super Integer> l;` then `l.add(1)` | compiles | an `Integer` fits every possible list |
| `List<? super Integer> l;` then `Integer x = l.get(0)` | compile error | only `Object` is guaranteed |
| `new ArrayList<?>()` | compile error | can't instantiate a wildcard type |
| `new List<?>[3]` | compiles | unbounded-wildcard arrays are allowed |
| `new List<String>[3]` | compile error | generic array creation |
| `new T()`, `new T[3]` | compile error | erasure |
| `o instanceof List<String>` (`o` an `Object`) | compile error | not checkable at runtime |
| `o instanceof List<?>` | compiles | only the erased part is checked |
| `List<String>.class` | compile error | only `List.class` exists |
| `new ArrayList<String>().getClass() == new ArrayList<Integer>().getClass()` | `true` | one runtime class |
| `static T x;` in `class Box<T>` | compile error | static context |
| `class E<T> extends Exception` | compile error | generic `Throwable` not allowed |
| `f(List<String>)` and `f(List<Integer>)` | compile error | same erasure |
| `<T> f(T)` and `f(Object)` | compile error | same erasure |
| `<T super Integer>` | compile error | only wildcards take `super` |
| `<T implements Comparable<T>>` | compile error | bounds always use `extends` |
| `<T extends Comparable<T> & Number>` | compile error | the class bound must come first |
| `Stats<Number>` with `Stats<T extends Number & Comparable<T>>` | compile error | `Number` is not `Comparable` |
| `<T> void swap(T[] a, …)` called with an `int[]` | compile error | `int[]` is not a `T[]` |
| `<T> boolean same(T a, T b)`, call `same("1", 1)` | compiles, `false` | `T` inferred as a common supertype |
| `Util.<String>m()` / `<String>m()` | compiles / compile error | an explicit type argument needs a qualifier |
| `<T> void set(T v) { value = v; }` in `Box<T>` | compile error | the method's `T` shadows the class's `T` |
| raw `Course` → `c.students()` declared `List<String>` | returns a raw `List` | a raw type erases all generic members |
| `(List<String>) someObject` | unchecked warning | only `List` is checked |
| `String[] a = stack.toArray()` with an internal `(T[]) new Object[n]` | `ClassCastException` | the array is really an `Object[]` |
| `List<Integer>` `[10, 20, 30]`, then `remove(1)` | removes `20` | `remove(int index)` wins |
| `Set<Short>`, then `remove(i - 1)` | never removes | `Integer` never equals `Short` |
| `Map<Long, String>`, then `get(1)` | `null` | `Integer` key ≠ `Long` key |
| `List<Long>`, then `add(5)` | compile error | no widening + boxing |
| `int n = map.get("missing");` | `NullPointerException` | unboxing `null` |

---

## 13. Practice — Trick Questions

**Q1.** Which lines compile?

```java
List<Number> a = new ArrayList<Integer>();            // (1)
List<? extends Number> b = new ArrayList<Integer>();  // (2)
b.add(1);                                             // (3)
List<? super Integer> c = new ArrayList<Number>();    // (4)
c.add(1);                                             // (5)
Number n = c.get(0);                                  // (6)
List<?> d = new ArrayList<String>();                  // (7)
d.add("x");                                           // (8)
d.remove("x");                                        // (9)
Collection<String> e = new ArrayList<String>();       // (10)
```

> [!success]- Answer
> | Line | Compiles? | Reason |
> |---|---|---|
> | (1) | ❌ | invariance: `List<Integer>` is not a `List<Number>` |
> | (2) | ✅ | `Integer` is within `? extends Number` |
> | (3) | ❌ | `b` could be a `List<Double>`: nothing but `null` can be added |
> | (4) | ✅ | `Number` is a supertype of `Integer` |
> | (5) | ✅ | an `Integer` fits any list of `Integer` or its supertypes |
> | (6) | ❌ | `c` could be a `List<Object>`: reading gives only `Object` |
> | (7) | ✅ | every `List<X>` is a `List<?>` |
> | (8) | ❌ | unknown element type |
> | (9) | ✅ | `remove(Object)` doesn't use the element type |
> | (10) | ✅ | same type argument, supertype along the class |

**Q2.** What is printed?

```java
class Box<T> {
    static int created = 0;
    Box() { created++; }
}

Box<String>  s = new Box<>();
Box<Integer> i = new Box<>();
System.out.println(Box.created);
System.out.println(s.getClass() == i.getClass());
System.out.println(s.getClass().getName());
```

> [!success]- Answer
> ```
> 2
> true
> Box
> ```
> After erasure there is a single class `Box`. Both objects increment the **same** static counter, have the same `Class` object, and its name is `Box`, not `Box<String>`. (This assumes `Box` is a top-level class in the default package. A nested class would print as `Outer$Box`.)

**Q3.** What is printed?

```java
List<Integer> list = new ArrayList<>(List.of(3, 2, 1, 0));
list.remove(1);
list.remove(Integer.valueOf(1));
list.remove((Object) 0);
System.out.println(list);
```

> [!success]- Answer
> `[3]`
>
> | Call | Chosen overload | List afterwards |
> |---|---|---|
> | `remove(1)` | `remove(int)`: exact match in phase 1 → removes **index** 1 (the `2`) | `[3, 1, 0]` |
> | `remove(Integer.valueOf(1))` | `remove(Object)` → removes the **value** 1 | `[3, 0]` |
> | `remove((Object) 0)` | `remove(Object)`: the cast boxes `0` to an `Integer` → removes the value 0 | `[3]` |

**Q4.** What is printed, and why?

```java
Set<Short> set = new HashSet<>();
for (short i = 0; i < 100; i++) {
    set.add(i);
    set.remove(i - 1);
}
System.out.println(set.size());
```

> [!success]- Answer
> `100`. `i - 1` is an `int` expression (binary numeric promotion), so it is boxed to an **`Integer`**. `remove` takes an `Object`, so this compiles, but an `Integer` never `equals` a `Short`, and nothing is ever removed. Fix: `set.remove((short) (i - 1));`.

**Q5.** Which line throws an exception, and which exception?

```java
List<String> names = new ArrayList<>();
List raw = names;
raw.add(7);                            // (1)
Object first = names.get(0);           // (2)
System.out.println(names.size());      // (3)
String s = names.get(0);               // (4)
```

> [!success]- Answer
> Only **(4)**, with a `ClassCastException` (`Integer cannot be cast to String`).
> - (1) compiles with an unchecked warning and runs fine: at runtime the list is just an `ArrayList` of `Object`s. This is the actual bug (heap pollution).
> - (2) runs fine: the value is stored in an `Object`, so the compiler inserts no cast.
> - (3) prints `1`.
> - (4) needs a `String`, so the compiler inserted `(String)` here, and that cast fails.

**Q6.** Which pairs can be declared together in the same class?

```java
(a) void f(List<String> x)          and  void f(List<Integer> x)
(b) void f(List<String> x)          and  void f(ArrayList<Integer> x)
(c) <T> void f(T x)                 and  void f(Object x)
(d) <T extends Number> void f(T x)  and  void f(Object x)
(e) void f(Box<String> x)           and  int f(Box<Integer> x)
```

> [!success]- Answer
> | Pair | Legal? | Erasures |
> |---|---|---|
> | (a) | ❌ | both `f(List)`: name clash |
> | (b) | ✅ | `f(List)` vs. `f(ArrayList)` |
> | (c) | ❌ | both `f(Object)` |
> | (d) | ✅ | `f(Number)` vs. `f(Object)` |
> | (e) | ❌ | both `f(Box)`: the different return type doesn't help |

**Q7.** (a) Why doesn't this compile? (b) Fix it. (c) After the obvious fix, `maxOf(List<Dog>)` still fails when `Dog extends Animal` and `Animal implements Comparable<Animal>`. Why, and what is the full fix?

```java
static <T> T maxOf(List<T> list) {
    T best = list.get(0);
    for (T x : list) {
        if (x.compareTo(best) > 0) best = x;
    }
    return best;
}
```

> [!success]- Answer
> (a) `T` is unbounded, so the compiler only knows it is an `Object`, and `Object` has no `compareTo`: *cannot find symbol*.
>
> (b) Add a bound: `static <T extends Comparable<T>> T maxOf(List<T> list)`.
>
> (c) With `List<Dog>`, `T` must be exactly `Dog`, and the bound requires `Dog extends Comparable<Dog>`. But `Dog` inherits `Comparable<Animal>`, and generics are invariant, so `Comparable<Animal>` is not a `Comparable<Dog>`. The full fix lets `T` be comparable through a supertype:
> ```java
> static <T extends Comparable<? super T>> T maxOf(List<? extends T> list)
> ```
> The `List<? extends T>` part is PECS again: the list only produces `T`s.

**Q8.** Which line fails, and how?

```java
var list = new ArrayList<>();
list.add("a");
list.add(1);
String s = list.get(0);
```

> [!success]- Answer
> Line 4: *incompatible types: Object cannot be converted to String*. With nothing to infer from, `new ArrayList<>()` becomes an `ArrayList<Object>`, so lines 2 and 3 both compile and `get` returns `Object`. Write `var list = new ArrayList<String>();` or `List<String> list = new ArrayList<>();`.

**Q9.** Which lines compile?

```java
class Course<T> {
    List<String> students() { return List.of("Ada"); }
}

Course<Integer> c1 = new Course<>();
Course c2 = new Course();
String a = c1.students().get(0);    // (1)
String b = c2.students().get(0);    // (2)
```

> [!success]- Answer
> (1) compiles. (2) does **not**: *Object cannot be converted to String*. `c2` is a raw type, and a raw type loses the generics of **all** its members, including `students()`, which has nothing to do with `T`. It returns a raw `List` with `Object` elements.

**Q10.** What is printed?

```java
static <T> boolean same(T a, T b) {
    return a.equals(b);
}

System.out.println(same("1", 1));
System.out.println(same(1, 1L));
System.out.println(same(1, 1));
```

> [!success]- Answer
> ```
> false
> false
> true
> ```
> All three compile. A single `T` doesn't force both arguments to have the same type: the compiler infers `T` as a common supertype (at worst `Object`). `"1"` is not equal to `1`, and `Integer.valueOf(1).equals(Long.valueOf(1))` is `false` because the classes differ.

**Q11.** Which of these compile?

```java
class Stats<T extends Number & Comparable<T>> { }

Stats<Integer> a;                                // (1)
Stats<Number>  b;                                // (2)
Stats<String>  c;                                // (3)
class Other<T extends Comparable<T> & Number> { } // (4)
static <T super Integer> void f(List<T> l) { }   // (5)
```

> [!success]- Answer
> | Line | Compiles? | Reason |
> |---|---|---|
> | (1) | ✅ | `Integer` is a `Number` and a `Comparable<Integer>` |
> | (2) | ❌ | `Number` doesn't implement `Comparable` |
> | (3) | ❌ | `String` is not a `Number` |
> | (4) | ❌ | the class bound (`Number`) must come first |
> | (5) | ❌ | type parameters can't have a `super` bound; write `static void f(List<? super Integer> l)` |

**Q12.** A generic stack stores its elements in `(T[]) new Object[10]`. `push` and `peek` work, but `String[] all = stack.toArray();` throws. Why, and how does the standard library avoid this?

> [!success]- Answer
> The internal array is an `Object[]` at runtime. `toArray()` returns it (or a copy of it) typed as `T[]`, and at the call site the compiler inserts a cast to `String[]`, which fails with `ClassCastException: Object[] cannot be cast to String[]`. `peek()` works because each **element** really is a `String`. The standard library either returns `Object[]` (`ArrayList.toArray()`) or asks the caller for an array of the correct runtime type (`toArray(T[] a)`, `toArray(String[]::new)`).

---

## 14. Summary

- **Generics** parameterize classes, interfaces, and methods by type. They catch type errors at **compile time** and remove the need for casts. Type arguments must be **reference types** (`List<Integer>`, not `List<int>`).
- The **diamond** `<>` infers type arguments from the target. `new ArrayList()` without it is a **raw type**, and `var x = new ArrayList<>()` gives `ArrayList<Object>`.
- **Generic methods** declare `<T>` right before the return type and have their type arguments inferred. An explicit type argument needs a qualifier (`Util.<String>m()`). A method's `<T>` shadows the class's `T`.
- **Bounds** (`<T extends Number>`, `<T extends A & I1 & I2>`) allow calling the bound's methods. Bounds always use `extends`, the class comes first, and type parameters have no `super` bound.
- Generics are **invariant**: `List<Integer>` is not a `List<Number>`, unlike covariant arrays.
- **Wildcards** add flexibility: `?` (unknown, read as `Object`), `? extends T` (read as `T`, can't add), `? super T` (can add `T`, read as `Object`). **PECS**: producer `extends`, consumer `super`.
- **Type erasure** removes type arguments after compilation: `T` becomes its first bound (or `Object`), and casts are inserted. So `new T()`, `new T[]`, generic arrays, `instanceof List<String>`, `T.class`, static `T`, generic exceptions, and overloads that differ only in type arguments are all forbidden.
- **Raw types** and ignored **unchecked warnings** cause heap pollution: a `ClassCastException` on a line with no visible cast.
- With wrapper collections, watch `remove(int)` vs. `remove(Object)`, methods that take `Object` (`get`, `remove`, `contains`) silently accepting the wrong key type, `==` on boxed values, and unboxing `null`.

## Related

- [[Java/00 - Syllabus|Syllabus]]
- Previous: [[Java/05 - Working with Data and Errors/01 - Exception Handling|Exception Handling]] · Next: [[Java/05 - Working with Data and Errors/03 - Comparable and Comparator|Comparable and Comparator]]
- [[Java/02 - Control Flow/03 - Arrays#11. Array Types, Covariance, and `ArrayStoreException`|Arrays § 11]]: covariant arrays, `ArrayStoreException`, generic array creation
- [[Java/03 - Program Structure/01 - Methods#7. Method Overloading|Methods § 7]]: overload resolution, which explains `remove(int)` vs. `remove(Object)` and erasure clashes
- [[Java/01 - Foundations/04 - Type Casting#9. Autoboxing and Unboxing (Related, Not True Casting)|Type Casting § 9]]: autoboxing, the `Integer` cache
- [[Java/01 - Foundations/02 - Variables and Data Types#9. Type Inference with `var`|Variables and Data Types § 9]]: `var` and inference
- [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]] · [[Java/04 - Object-Oriented Programming/05 - Abstraction|Abstraction]]: subtyping and interfaces such as `Comparable`
- [[Java/05 - Working with Data and Errors/03 - Comparable and Comparator|Comparable and Comparator]]: `Comparable<T>`, `Comparator<? super T>` in practice
- [[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]]: `List`, `Set`, `Map` and their generic APIs
