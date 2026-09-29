# Methods in Java

A <span class="hl-blue">method</span> is a named block of code that belongs to a class, takes zero or more inputs (**parameters**), and may produce one output (the **return value**). Methods let you write a piece of logic once, give it a name, and call it from anywhere. This chapter covers how a method is declared and called, return types and the compiler's `return` rules, how arguments are passed (always by value, including references), local variables and the call stack, overloading and how the compiler picks an overload, variable-length arguments, and recursion.

Instance methods, constructors, and `this` are covered in [[01 - Classes and Objects|Classes and Objects]], and overriding in [[Java/04 - Object-Oriented Programming/03 - Inheritance|Inheritance]]. This chapter uses `static` methods for its examples, because those can be called straight from `main`.

## Contents

- [[#1. What a Method Is|1. What a Method Is]]
- [[#2. Declaring a Method|2. Declaring a Method]]
- [[#3. Calling a Method|3. Calling a Method]]
- [[#4. Return Types and the `return` Statement|4. Return Types and the `return` Statement]]
- [[#5. Parameter Passing — Always Pass-by-Value|5. Parameter Passing — Always Pass-by-Value]]
- [[#6. Local Variables, Scope, and the Call Stack|6. Local Variables, Scope, and the Call Stack]]
- [[#7. Method Overloading|7. Method Overloading]]
- [[#8. Variable-Length Arguments (Varargs)|8. Variable-Length Arguments (Varargs)]]
- [[#9. Recursion|9. Recursion]]
- [[#10. Writing Good Methods|10. Writing Good Methods]]
- [[#11. Common Pitfalls|11. Common Pitfalls]]
- [[#12. Quick Reference — Non-Obvious Outcomes|12. Quick Reference — Non-Obvious Outcomes]]
- [[#13. Practice — Trick Questions|13. Practice — Trick Questions]]
- [[#14. Summary|14. Summary]]

---

## 1. What a Method Is

> [!note] Definitions
> - A **method** is a named, reusable block of statements declared inside a class.
> - A **parameter** (*formal parameter*) is a variable listed in the method's declaration: `x` in `int square(int x)`.
> - An **argument** (*actual parameter*) is the value passed in a call: `5` in `square(5)`.
> - The **return type** is the type of value the method gives back, or `void` if it gives nothing back.
> - The **signature** is the method's **name plus the list of parameter types**, e.g. `square(int)`. The return type, parameter names, and modifiers are **not** part of the signature. Within one class, no two methods may have the same signature.

```java
public class Geometry {
    static double circleArea(double radius) {   // declaration
        return Math.PI * radius * radius;
    }

    public static void main(String[] args) {
        double a = circleArea(2.0);              // call, with argument 2.0
        System.out.println(a);                   // 12.566370614359172
    }
}
```

Java has no free-standing functions. Every method belongs to a class (or interface, enum, or record). Utilities like `Math.sqrt` are `static` methods of a class. Even the top-level methods of a Java 25+ compact source file are members of an implicitly declared class (see [[01 - Introduction to Java#7.4 Java 25+ — Instance Main Methods and Compact Source Files|Introduction to Java § 7.4]]).

---

## 2. Declaring a Method

```java
public static int max(int a, int b) throws IllegalStateException {
    return a > b ? a : b;
}
```

| Part | Example | Required? | Meaning |
|---|---|---|---|
| Modifiers | `public static` | no | access level ([[Java/04 - Object-Oriented Programming/02 - Encapsulation|Encapsulation]]), `static`, `final`, `abstract`, … |
| Return type | `int` | **yes** | the type returned, or `void` |
| Name | `max` | **yes** | by convention a verb in `lowerCamelCase`: `computeTotal`, `isEmpty` |
| Parameter list | `(int a, int b)` | **yes** (may be empty `()`) | each parameter needs its own type |
| `throws` clause | `throws IllegalStateException` | no | exceptions the method may throw ([[Java/05 - Working with Data and Errors/01 - Exception Handling|Exception Handling]]) |
| Body | `{ … }` | yes (except `abstract`/interface methods) | the statements to run |

A method can also declare its own **type parameters**, written right before the return type: `static <T> T last(List<T> list)` works for a list of any type. These *generic methods* are covered in [[Java/05 - Working with Data and Errors/02 - Generics#3. Generic Methods|Generics § 3]].

> [!warning] Common mistakes in the header
> ```java
> static int max(int a, b) { … }     // compile error: every parameter needs its own type
> static max(int a, int b) { … }     // compile error: missing return type (only constructors have none)
> static int max(int a, int a) { … } // compile error: duplicate parameter name
> ```

### 2.1 Where Methods Can (and Can't) Go

- Methods are declared **directly inside a class**, never inside another method. Java has no nested functions. `void f() { void g() {} }` is a compile error (lambdas and local classes are the alternatives).
- Declaration order doesn't matter: a method can call another method declared **further down** in the same class. There is no need to declare anything first, as C requires.
- A method and a field (or local variable) can share a name. They are looked up in separate namespaces, so `int count;` and `int count() { … }` can coexist (it's legal but confusing).

> [!warning] Trick: a "constructor" with a return type is just a method
> ```java
> public class Dog {
>     public void Dog() {                 // NOT a constructor: it has a return type
>         System.out.println("woof");
>     }
> }
> new Dog();   // prints nothing: the compiler supplied a default constructor
> ```
> A method may have the same name as its class. It compiles, but it is an ordinary method that `new` never calls. Constructors have **no** return type, not even `void`. See [[01 - Classes and Objects|Classes and Objects]].

---

## 3. Calling a Method

A call evaluates the arguments, copies them into the parameters, runs the body, and then continues after the call, using the return value if there is one.

```java
int m = max(3, 7);                  // same class: just the name
double r = Math.sqrt(16);           // static method of another class: ClassName.method(...)
String s = "hello".toUpperCase();   // instance method: object.method(...)
```

- Arguments are **evaluated left to right**, fully, before the method body starts. `f(i++, i++)` with `i == 1` passes `1` and `2`, and `i` is `3` afterwards (see [[03 - Operators#13. Evaluation Order — Not the Same as Precedence|Operators § 13]]).
- The number of arguments, their order, and their types must match a declared parameter list (after the conversions in [[#7.2 How the Compiler Chooses an Overload|§ 7.2]]).
- A non-`void` return value **may be ignored**: `Math.max(1, 2);` is a legal statement. A `void` method's result **cannot be used** at all:

```java
static void greet() { System.out.println("hi"); }

greet();                          // OK
int x = greet();                  // compile error: void cannot be converted to int
System.out.println(greet());      // compile error: 'void' type not allowed here
```

### 3.1 Calling Instance Methods from `main`

<span class="hl-yellow">The error every beginner meets.</span> `main` is `static`: it runs without any object of its class. So it cannot call an instance (non-`static`) method of that class directly:

```java
public class App {
    void hello() { System.out.println("hello"); }       // instance method

    public static void main(String[] args) {
        hello();              // compile error: non-static method hello() cannot be referenced from a static context
        new App().hello();    // OK: create an object and call the method on it
    }
}
```

Either make the helper `static`, or create an object and call the method on it. The difference between `static` and instance members is covered in [[01 - Classes and Objects|Classes and Objects]].

---

## 4. Return Types and the `return` Statement

### 4.1 `void` vs. a Value

| Method kind | `return;` | `return expr;` | Falling off the end of the body |
|---|---|---|---|
| `void` | ✅ ends the method early | ❌ *unexpected return value* | ✅ allowed |
| non-`void` (e.g. `int`) | ❌ *missing return value* | ✅ `expr` must be assignable to the return type | ❌ *missing return statement* |

`return` **ends the method immediately**, even from inside a loop. There is no need for a `break` first:

```java
static int indexOf(int[] a, int key) {
    for (int i = 0; i < a.length; i++) {
        if (a[i] == key) {
            return i;          // leaves the loop AND the method
        }
    }
    return -1;                 // reached only if the loop found nothing
}
```

### 4.2 Every Path Must Return — As the Compiler Sees It

> [!important] Key rule: the compiler does not evaluate your conditions
> A non-`void` method must not be able to reach the closing `}`. The compiler checks this with fixed flow rules (JLS § 14.22), **without** working out whether conditions are true or false. The only exception is a constant `true` in a loop condition.

```java
static int sign(int x) {
    if (x > 0) return 1;
    else if (x <= 0) return 0;
}   // compile error: missing return statement (even though one branch always runs)
```

The fix is a final `else` (or a trailing `return`):

```java
static int sign(int x) {
    if (x > 0) return 1;
    else return 0;
}
```

<span class="hl-yellow">Trick cases:</span> these look like they break the rule, but all follow from it.

| Method body (return type `int`) | Compiles? | Why |
|---|---|---|
| `if (true) return 1;` | ❌ | an `if` is always treated as able to skip its body, even with a constant condition |
| `while (true) { }` | ✅ | the loop can never finish normally, so the end is unreachable |
| `for (;;);` | ✅ | same: no condition means `true` |
| `while (true) { if (x) break; }` then nothing | ❌ | a `break` makes the end reachable |
| `throw new RuntimeException();` | ✅ | a `throw` never completes normally either |
| `switch` with a `return` in every `case` but no `default` | ❌ | a value not matched by any `case` would fall through |

### 4.3 Unreachable Code Is a Compile Error

The same flow rules also reject statements that can **never** run:

```java
static void f() {
    return;
    System.out.println("never");       // compile error: unreachable statement
}

while (false) { … }                    // compile error: unreachable statement
if (false) { … }                       // OK: deliberately allowed, for "conditional compilation"
```

> [!info]- Why is `if (false)` allowed but `while (false)` rejected?
> The language designers wanted code like `if (DEBUG) { log(...); }` with a `static final boolean DEBUG = false;` to compile, so that debugging code can be switched off with one constant. So `if` is excluded from the unreachability check: its body is always considered reachable, and the statement after it too. The side effect is the `if (true) return 1;` case above: the compiler assumes the `if` might not run, so a return is still required after it.

### 4.4 The Returned Value Is Converted Like an Assignment

`return expr;` follows the same rules as assigning `expr` to a variable of the return type (see [[04 - Type Casting|Type Casting]]):

```java
static double half()  { return 5; }        // OK: int widened to 5.0
static long big()     { return 'a'; }      // OK: char widened to 97L
static int narrow()   { return 5L; }       // compile error: possible lossy conversion from long to int
static byte small()   { return 10; }       // OK: constant 10 fits in a byte
static byte small2()  { int x = 10; return x; }   // compile error: x is not a constant
static Integer boxed(){ return 5; }        // OK: autoboxing
static int unboxed()  { Integer n = null; return n; }  // compiles, NullPointerException at runtime
```

### 4.5 Returning More Than One Value

A method returns **one** value. To return several, return an object that holds them: an array (same type), a small class, or a `record` (Java 16+):

```java
record MinMax(int min, int max) { }

static MinMax minMax(int[] a) {
    int lo = a[0], hi = a[0];
    for (int x : a) {
        lo = Math.min(lo, x);
        hi = Math.max(hi, x);
    }
    return new MinMax(lo, hi);
}

MinMax r = minMax(new int[] {4, -2, 9});
System.out.println(r.min() + " " + r.max());   // -2 9
```

---

## 5. Parameter Passing — Always Pass-by-Value

> [!important] Key rule: Java is **always** pass-by-value
> When a method is called, the **value** of each argument is **copied** into the parameter.
> - For a **primitive**, the value is the number, `char`, or `boolean` itself. The method gets its own copy, and changing it never affects the caller.
> - For a **reference type** (objects, arrays, `String`), the value is the **reference**. The method gets a copy of the reference, which points to the **same object**. The method can therefore **change the object's state**, but **reassigning the parameter** only changes the local copy.
>
> Java has **no** pass-by-reference. No method can make the caller's variable hold a different value or refer to a different object.

### 5.1 Primitives

```java
static void addTen(int n) {
    n = n + 10;                // changes only the local copy
}

int x = 5;
addTen(x);
System.out.println(x);         // 5
```

### 5.2 References: Mutating vs. Reassigning

```java
static void modify(StringBuilder sb) {
    sb.append(" world");        // (1) mutates the shared object: the caller sees it
    sb = new StringBuilder("X");// (2) reassigns the local copy: the caller does not see it
    sb.append("!!!");           // (3) mutates the NEW object: the caller does not see it
}

StringBuilder s = new StringBuilder("hello");
modify(s);
System.out.println(s);          // hello world
```

```
before (2):   s ──┐
                  ├──► "hello world"
             sb ──┘

after (2):    s ─────► "hello world"
             sb ─────► "X!!!"        (discarded when modify returns)
```

The same holds for arrays (see [[03 - Arrays#10. Arrays and Methods|Arrays § 10]]).

### 5.3 The Classic `swap` That Doesn't Work

<span class="hl-yellow">Exam favourite.</span>

```java
static void swap(int a, int b) {
    int tmp = a; a = b; b = tmp;   // swaps the copies only
}

int x = 1, y = 2;
swap(x, y);
System.out.println(x + " " + y);   // 1 2
```

The same happens with objects: `swap(Integer a, Integer b)` or `swap(String a, String b)` also swaps only the local references. A working swap has to change something **inside** a shared object, e.g. two elements of an array:

```java
static void swap(int[] arr, int i, int j) {
    int tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
}
```

### 5.4 Immutable Objects Look Like Primitives

`String`, `Integer`, and the other wrapper types are **immutable**: they have no methods that change their state. So the only thing a method *could* do with the parameter is reassign it, which the caller never sees:

```java
static void shout(String s)  { s = s + "!"; }   // creates a new String, local only
static void bump(Integer n)  { n++; }           // n = Integer.valueOf(n + 1): a new object, local only

String t = "hi";   shout(t);  // t is still "hi"
Integer k = 5;     bump(k);   // k is still 5
```

This is not "strings are passed by value and objects by reference". Everything is passed the same way. `String` simply gives the method nothing it can mutate. See [[02 - Strings#1. The String Class and Immutability|Strings § 1]].

### 5.5 `final` Parameters

```java
static int area(final int w, final int h) {
    w = 10;              // compile error: final parameter w may not be assigned
    return w * h;
}
```

A `final` parameter cannot be reassigned inside the method. It has no effect on the caller at all (the caller's variable was safe anyway). For a reference parameter, `final` stops reassignment but still allows mutating the object.

---

## 6. Local Variables, Scope, and the Call Stack

### 6.1 Parameters Are Local Variables

Parameters behave like local variables that are initialized by the call. Both exist only while the method runs:

```java
static int f(int x) {
    int x = 5;          // compile error: variable x is already defined in method f(int)
    int y;
    return y;           // compile error: variable y might not have been initialized
}
```

- A local variable (or parameter) **cannot be redeclared** in a nested block of the same method.
- Local variables have **no default value**. They must be definitely assigned before they are read (fields, by contrast, default to `0`/`false`/`null`, see [[02 - Variables and Data Types#6. Default Values|Default Values]]).
- A parameter **may** have the same name as a field. It then **shadows** the field inside the method, and `this.name` is needed to reach the field (see [[02 - Variables and Data Types#8. Scope and Shadowing|Scope and Shadowing]]).
- A method **cannot see another method's** local variables, not even those of the method that called it.

### 6.2 The Call Stack

Each call gets its own <span class="hl-blue">stack frame</span>, a block of memory holding that call's parameters and local variables. The frame is pushed when the method is called and popped when it returns, so local variables disappear when the method ends and start fresh on every call.

```java
public static void main(String[] args) {
    int r = outer(2);
}
static int outer(int a) { return inner(a + 1) * 2; }
static int inner(int b) { return b * b; }
```

| Moment | Stack (top first) | Notes |
|---|---|---|
| `main` starts | `main [args, r=?]` | |
| `main` calls `outer(2)` | `outer [a=2]` · `main` | |
| `outer` calls `inner(3)` | `inner [b=3]` · `outer [a=2]` · `main` | `a + 1` evaluated before the call |
| `inner` returns `9` | `outer [a=2]` · `main` | `inner`'s frame is discarded |
| `outer` returns `18` | `main [r=18]` | |

Objects created with `new` live on the **heap**, not in the frame, so an object can outlive the call that created it as long as something still refers to it (for example, when the method returns it).

When the stack runs out of space, usually because of runaway recursion, the JVM throws `StackOverflowError` ([[#9. Recursion|§ 9]]).

---

## 7. Method Overloading

<span class="hl-blue">Overloading</span> means declaring several methods with the **same name** but **different parameter lists** in the same class. The compiler picks which one to call from the arguments.

```java
static int    add(int a, int b)          { return a + b; }
static double add(double a, double b)    { return a + b; }
static int    add(int a, int b, int c)   { return a + b + c; }
static String add(String a, int b)       { return a + b; }
static String add(int a, String b)       { return a + b; }   // different ORDER of types: legal

add(1, 2);         // add(int, int)          → 3
add(1.5, 2);       // add(double, double)    → 3.5
add(1, 2, 3);      // add(int, int, int)     → 6
add("x", 1);       // add(String, int)       → "x1"
```

`System.out.println` is overloaded for every primitive type, `char[]`, `String`, and `Object`. That is why it can print anything, and why `println(char[])` behaves differently from `println(Object)` (see [[03 - Arrays#6.3 Printing Arrays|Arrays § 6.3]]).

### 7.1 What Does and Doesn't Count as a Different Overload

| Methods differ only in… | Legal overload? | Notes |
|---|---|---|
| number of parameters | ✅ | `f(int)` / `f(int, int)` |
| parameter types | ✅ | `f(int)` / `f(double)` |
| order of parameter types | ✅ | `f(int, String)` / `f(String, int)` |
| **return type** | ❌ | `int f(int)` / `long f(int)`: *method f(int) is already defined* |
| parameter **names** | ❌ | `f(int x)` / `f(int y)`: same signature |
| modifiers (`static`, `public`, `final`) | ❌ | same signature |
| `throws` clause | ❌ | same signature |
| `int[]` vs. `int...` | ❌ | varargs **is** an array: *cannot declare both f(int[]) and f(int...)* |
| only the type arguments (`List<String>` vs. `List<Integer>`) | ❌ | *name clash: … have the same erasure*: both become `f(List)` after type erasure ([[Java/05 - Working with Data and Errors/02 - Generics#7.3 Overloads That Clash After Erasure|Generics § 7.3]]) |

> [!info]- Why can't the return type distinguish overloads?
> Because a return value can be ignored. For `f(5);` as a statement, nothing indicates whether `int f(int)` or `long f(int)` was meant. So the compiler chooses an overload from the arguments alone, and two methods with the same parameter types are considered duplicates.

### 7.2 How the Compiler Chooses an Overload

Overload resolution happens **at compile time**, using the **compile-time (declared) types** of the arguments. It runs in three phases and stops at the first phase that finds any applicable method:

| Phase | Conversions allowed | Example that is decided here |
|---|---|---|
| 1 | exact match, **primitive widening** (`int → long → float → double`, `char → int`), reference widening (`String → Object`) | `f(long)` for `f(5)` |
| 2 | phase 1 **plus boxing/unboxing** (`int ↔ Integer`) | `f(Integer)` for `f(5)` if there is no `f(long)`/`f(double)` |
| 3 | phase 2 **plus varargs** | `f(int...)` for `f(5)` if nothing else fits |

If a phase finds several applicable methods, the compiler picks the **most specific** one: the one whose parameter types could be passed to all the others. If none is most specific, the call is **ambiguous** and does not compile.

> [!important] Key rule: widening beats boxing beats varargs
> ```java
> static void f(long x)    { System.out.println("long"); }
> static void f(Integer x) { System.out.println("Integer"); }
> static void f(int... x)  { System.out.println("varargs"); }
>
> f(5);   // long : phase 1 (widening) wins before boxing is ever considered
> ```
> This rule preserved the behavior of pre-Java 5 code when boxing and varargs were added.

<span class="hl-yellow">The classic trick cases:</span>

```java
static void g(double d) { System.out.println("double " + d); }
g('a');            // double 97.0 : char widens to double

static void h(char c) { … }  static void h(int i) { … }
h((byte) 1);       // int : byte can widen to int but not to char

static void s(short x) { … }
s(5);              // compile error: 5 is an int, and method calls do NOT narrow constants
short v = 5;       // but this is fine: assignment DOES narrow constants

static void L(Long x) { … }
L(5);              // compile error: int cannot be converted to Long (no widening + boxing)
L(5L);             // OK

static void o(Object x) { … }
o(5);              // OK: boxing to Integer, then widening to Object (phase 2)
```

> [!warning] Common mistake: `null` and overloads
> ```java
> static void p(Object o) { System.out.println("Object"); }
> static void p(String s) { System.out.println("String"); }
> p(null);          // String : String is more specific than Object
>
> static void q(String s)  { … }
> static void q(Integer i) { … }
> q(null);          // compile error: reference to q is ambiguous (neither is more specific)
> q((String) null); // OK: the cast picks one
> ```

> [!warning] Common mistake: overloads are chosen by the declared type, not the runtime object
> ```java
> Object obj = "hello";      // declared Object, runtime String
> p(obj);                    // Object : the compiler only knows obj is an Object
> ```
> This is the key difference from **overriding** (runtime choice, based on the actual object). See [[Java/04 - Object-Oriented Programming/04 - Polymorphism|Polymorphism]].

> [!example]- Worked example: an ambiguous call with two parameters
> ```java
> static void r(int a, long b) { … }
> static void r(long a, int b) { … }
> r(1, 2);   // compile error: reference to r is ambiguous
> ```
> | Candidate | Arg 1 (`int`) | Arg 2 (`int`) | Applicable in phase 1? |
> |---|---|---|---|
> | `r(int, long)` | exact | widening | ✅ |
> | `r(long, int)` | widening | exact | ✅ |
>
> Is either more specific? `r(int, long)` can't be passed to `r(long, int)` (its `long` second parameter doesn't fit `int`), and the reverse fails for the first parameter. Neither is more specific, so the call is ambiguous. `r(1, 2L)` or `r(1L, 2)` compiles.

---

## 8. Variable-Length Arguments (Varargs)

A <span class="hl-blue">varargs</span> parameter, written `Type... name`, accepts **zero or more** arguments of that type. Inside the method it is an ordinary **array**.

```java
static int sum(int... nums) {        // nums is an int[]
    int total = 0;
    for (int n : nums) {
        total += n;
    }
    return total;
}

sum();                    // 0      : nums is an empty array (length 0), not null
sum(4);                   // 4
sum(1, 2, 3);             // 6
sum(new int[] {1, 2, 3}); // 6      : an existing array may be passed directly
```

> [!important] Rules
> - At most **one** varargs parameter per method, and it must be the **last** parameter: `f(String label, int... values)` is fine, and `f(int... values, String label)` is a compile error (*varargs parameter must be the last parameter*).
> - `f(int... a)` and `f(int[] a)` have the **same signature** and can't both exist.
> - Varargs is the **last resort** in overload resolution (phase 3, [[#7.2 How the Compiler Chooses an Overload|§ 7.2]]). A fixed-arity overload that fits always wins.
> - `main` may be declared as `public static void main(String... args)`.

Familiar varargs methods: `String.format(String format, Object... args)`, `System.out.printf(...)`, `Arrays.asList(T... a)`, `List.of(E... e)`.

> [!warning] Trick: `null` and varargs
> ```java
> static void v(int... a) { System.out.println(a == null ? "null" : "len " + a.length); }
> v();              // len 0
> v(null);          // null : null is passed as the array itself
>
> static void w(Object... a) { … same body … }
> w(null);          // null   (with a compiler warning: null is taken as the Object[] itself)
> w((Object) null); // len 1  : an array holding one null element
> ```
> A varargs parameter can therefore be `null` if the caller passes `null` explicitly. A defensive method should check for it.

> [!info]- Varargs and ambiguity
> `f(int... a)` together with `f(Integer... a)` makes `f(1)` ambiguous: both are applicable in phase 3 and neither is more specific. Avoid overloading varargs methods with each other.

---

## 9. Recursion

A method is <span class="hl-blue">recursive</span> when it calls itself. Every correct recursive method has:

1. a **base case**, which is answered directly without a recursive call, and
2. a **recursive case**, which calls the method on a **smaller** input that moves toward the base case.

Each recursive call gets its own stack frame ([[#6.2 The Call Stack|§ 6.2]]), so each level has its own copy of the parameters. The full topic (recursion trees, tail recursion, converting to iteration) is covered in [[DSA/Foundations/Recursion|DSA: Recursion]].

### 9.1 Factorial

```
factorial(n):
    if n ≤ 1:                         -- base case
        return 1
    return n × factorial(n − 1)       -- recursive case
```

```java
static long factorial(int n) {
    if (n < 0) {
        throw new IllegalArgumentException("n must be non-negative");
    }
    if (n <= 1) {
        return 1;                     // base case: 0! = 1! = 1
    }
    return n * factorial(n - 1);      // recursive case
}
```

> [!example]- Step by step: `factorial(4)`
> | Call | Waits for | Returns |
> |---|---|---|
> | `factorial(4)` | `4 * factorial(3)` | `4 * 6 = 24` |
> | `factorial(3)` | `3 * factorial(2)` | `3 * 2 = 6` |
> | `factorial(2)` | `2 * factorial(1)` | `2 * 1 = 2` |
> | `factorial(1)` | — (base case) | `1` |
>
> The calls go **down** until the base case, and the multiplications happen on the way back **up**, as each frame is popped.

> [!warning] Overflow comes quickly
> `factorial` returns `long` because `13!` already overflows `int`. Even `long` overflows at `21!`: `factorial(21)` silently returns `-4249290049419214848`. See [[03 - Operators#4. Integer Overflow|Operators § 4]]. Use `java.math.BigInteger` for larger values.

### 9.2 Fibonacci — Correct but Exponential

```
fib(n):
    if n ≤ 1:
        return n
    return fib(n − 1) + fib(n − 2)
```

```java
static long fib(int n) {
    if (n <= 1) {
        return n;                     // fib(0) = 0, fib(1) = 1
    }
    return fib(n - 1) + fib(n - 2);
}
```

This is a direct translation of the definition, but it recomputes the same values over and over: `fib(n)` makes roughly `φⁿ ≈ 1.6ⁿ` calls, so each `+1` on `n` makes it about 1.6 times slower. `fib(40)` takes a fraction of a second, but `fib(50)` takes tens of seconds, and `fib(60)` close to an hour. A loop (or memoization) is O(n):

```java
static long fibIterative(int n) {
    long prev = 0, curr = 1;
    for (int i = 0; i < n; i++) {
        long next = prev + curr;
        prev = curr;
        curr = next;
    }
    return prev;
}
```

### 9.3 `StackOverflowError`

A missing or unreachable base case makes the recursion infinite. Each call adds a frame until the stack is full:

```java
static int countDown(int n) {
    return countDown(n - 1);          // no base case
}                                     // → java.lang.StackOverflowError

static int bad(int n) {
    if (n == 0) return 0;
    return bad(n - 2);                // bad(5) → 3 → 1 → -1 → … never reaches 0
}
```

> [!tip] Checklist for a recursive method
> - Is there a base case, and is it checked **before** the recursive call?
> - Does **every** input reach the base case? Check odd/even numbers, negative numbers, and empty inputs.
> - Is the recursion depth reasonable? The default stack allows depths in the thousands to tens of thousands, not millions. Deep linear recursion (e.g. over a list of a million elements) should be a loop instead. Java does not optimize tail calls.

---

## 10. Writing Good Methods

- **One job per method.** If a method's name needs "and" (`readAndValidateAndSave`), split it.
- **Name by what it does or returns**: verbs for actions (`printReport`, `sort`), `is`/`has`/`can` for `boolean` results (`isEmpty`, `hasNext`).
- **Prefer returning a value to printing it.** `static int max(...)` is reusable, while a method that prints the maximum can only print it.
- **Don't modify arguments unexpectedly.** If a method changes an array or object passed to it, make that clear from its name (`sortInPlace`) or its documentation.
- **Validate inputs** at the start and throw an `IllegalArgumentException` for invalid ones, rather than returning a misleading value.
- **Keep parameter lists short.** Many parameters of the same type (`f(int, int, int, int)`) are easy to pass in the wrong order. Group them into an object or a `record`.

---

## 11. Common Pitfalls

- **Missing `return` on some path** of a non-`void` method. Remember that the compiler does not evaluate `if` conditions, so an `else if` chain that "covers everything" still needs a final `else` or `return`.
- **Code after `return`** is an unreachable-statement compile error.
- **Calling an instance method from `static main`**: *non-static method cannot be referenced from a static context*.
- **Expecting a method to change the caller's primitive or reassigned reference.** Java is always pass-by-value. Return the new value instead.
- **The broken `swap(int a, int b)`**, which only swaps local copies.
- **Using the result of a `void` method**, e.g. `int[] sorted = Arrays.sort(a);`.
- **Ignoring a return value that matters**, e.g. `s.toUpperCase();` or `Math.abs(x);` on its own line (see [[02 - Strings#1. The String Class and Immutability|Strings § 1]]).
- **Overloading by return type only**: it is a duplicate-method compile error.
- **Passing an `int` literal to a `short`/`byte` parameter** (`s(5)`): method calls don't narrow constants. Cast it: `s((short) 5)`.
- **Passing an `int` to a `Long` parameter** (`L(5)`): Java won't widen and then box. Use `5L`.
- **`null` arguments with overloads** can be ambiguous. Cast `null` to the intended type.
- **Assuming overloads are chosen by the runtime type.** They are chosen by the declared type at compile time.
- **Recursion without a reachable base case** gives a `StackOverflowError`.
- **Naive recursive Fibonacci** for large `n` is exponential.
- **Writing `void ClassName()` intending a constructor.** It is a regular method that `new` never calls.

---

## 12. Quick Reference — Non-Obvious Outcomes

| Code | Result | Why |
|---|---|---|
| `int f(int a, b)` | compile error | each parameter needs a type |
| `void f() { void g() {} }` | compile error | no nested methods |
| `if (x > 0) return 1; else if (x <= 0) return 0;` (end of `int` method) | compile error | missing return: conditions are not evaluated |
| `int f() { if (true) return 1; }` | compile error | `if` is always assumed skippable |
| `int f() { while (true) { } }` | compiles | end is unreachable |
| `int f() { throw new RuntimeException(); }` | compiles | end is unreachable |
| `return; x = 1;` | compile error | unreachable statement |
| `if (false) { … }` | compiles | deliberately exempt |
| `while (false) { … }` | compile error | unreachable body |
| `byte f() { return 10; }` | compiles | constant narrowing in `return` |
| `int f() { return 5L; }` | compile error | `long` → `int` is narrowing |
| `int f() { Integer n = null; return n; }` | `NullPointerException` | unboxing `null` |
| `int x = voidMethod();` | compile error | `void` has no value |
| `Math.max(1, 2);` | compiles | return values may be ignored |
| `f(i++, i++)` (i = 1) | `f(1, 2)`, then `i == 3` | arguments evaluated left to right |
| `swap(x, y)` on `int`s | no effect | copies swapped |
| `sb.append("!")` inside a method | caller sees it | same object |
| `sb = new StringBuilder()` inside a method | caller doesn't see it | local reference reassigned |
| `s = s + "!"` / `n++` on `String`/`Integer` param | caller doesn't see it | immutable → new object |
| `int f(int)` and `long f(int)` | compile error | return type not part of the signature |
| `f(int[])` and `f(int...)` | compile error | same signature |
| `f(long)` vs `f(Integer)`, call `f(5)` | `f(long)` | widening before boxing |
| `f(double)`, call `f('a')` | `97.0` | `char` → `double` widening |
| `f(char)` vs `f(int)`, call `f((byte) 1)` | `f(int)` | `byte` can't widen to `char` |
| `f(short)`, call `f(5)` | compile error | no constant narrowing in calls |
| `f(Long)`, call `f(5)` | compile error | no widening + boxing |
| `f(Object)`, call `f(5)` | compiles | boxing, then widening |
| `f(Object)` vs `f(String)`, call `f(null)` | `f(String)` | most specific |
| `f(String)` vs `f(Integer)`, call `f(null)` | compile error | ambiguous |
| `f(int, long)` vs `f(long, int)`, call `f(1, 2)` | compile error | ambiguous |
| `Object o = "s"; f(o)` with `f(Object)`/`f(String)` | `f(Object)` | compile-time type decides |
| `f(long)` vs `f(int...)`, call `f(5)` | `f(long)` | varargs is the last resort |
| `f(int... a)`, call `f()` | `a.length == 0` | empty array, not `null` |
| `f(int... a)`, call `f(null)` | `a == null` | `null` is the array |
| `f(int... a, int b)` | compile error | varargs must be last |
| `public void Dog()` in class `Dog` | a method, not a constructor | constructors have no return type |
| `factorial(21)` with `long` | negative number | `long` overflow |
| recursion with no base case | `StackOverflowError` | stack exhausted |

---

## 13. Practice — Trick Questions

**Q1.** Which of these methods compile?

```java
static int a(int x) { if (x > 0) return 1; if (x <= 0) return -1; }       // (1)
static int b(int x) { if (x > 0) return 1; return -1; }                   // (2)
static int c() { while (true) { } }                                       // (3)
static int d() { while (true) { break; } }                                // (4)
static void e() { return; }                                               // (5)
static int f() { return; }                                                // (6)
static byte g() { return 100; }                                           // (7)
static byte h() { return 200; }                                           // (8)
```

> [!success]- Answer
> | Method | Compiles? | Reason |
> |---|---|---|
> | (1) | ❌ | missing return: the compiler assumes both `if`s could be skipped |
> | (2) | ✅ | the final `return` covers every path |
> | (3) | ✅ | the end can't be reached |
> | (4) | ❌ | `break` makes the end reachable, and there is no return after the loop |
> | (5) | ✅ | a bare `return;` is fine in a `void` method |
> | (6) | ❌ | an `int` method must return a value |
> | (7) | ✅ | constant `100` fits in a `byte` |
> | (8) | ❌ | `200` does not fit in a `byte` (`-128 … 127`) |

**Q2.** What is printed?

```java
static void change(int n, int[] arr, StringBuilder sb, String s) {
    n = 99;
    arr[0] = 99;
    sb.append("!");
    s = s + "!";
    arr = new int[] {-1};
    sb = new StringBuilder("new");
}

int n = 1;
int[] arr = {1};
StringBuilder sb = new StringBuilder("sb");
String s = "s";
change(n, arr, sb, s);
System.out.println(n + " " + arr[0] + " " + sb + " " + s);
```

> [!success]- Answer
> `1 99 sb! s`
>
> | Statement | Visible to the caller? | Why |
> |---|---|---|
> | `n = 99` | ❌ | copy of a primitive |
> | `arr[0] = 99` | ✅ | mutates the shared array |
> | `sb.append("!")` | ✅ | mutates the shared object |
> | `s = s + "!"` | ❌ | a new `String`, assigned to the local reference |
> | `arr = new int[]{-1}` | ❌ | local reference reassigned |
> | `sb = new StringBuilder(...)` | ❌ | local reference reassigned |

**Q3.** Which overload is called in each line, or does the line fail to compile?

```java
static void m(int x)     { System.out.println("int"); }
static void m(long x)    { System.out.println("long"); }
static void m(Integer x) { System.out.println("Integer"); }
static void m(Object x)  { System.out.println("Object"); }
static void m(int... x)  { System.out.println("int..."); }

byte b = 1; long L = 1; Integer I = 1; char c = 'c';
m(b);        // (1)
m(L);        // (2)
m(I);        // (3)
m(c);        // (4)
m(1.0);      // (5)
m();         // (6)
m(1, 2);     // (7)
```

> [!success]- Answer
> | Call | Result | Phase / reason |
> |---|---|---|
> | (1) `m(b)` | `int` | phase 1: `byte → int` is the most specific widening |
> | (2) `m(L)` | `long` | phase 1: exact match |
> | (3) `m(I)` | `Integer` | phase 1: exact reference match (`Integer` is more specific than `Object`) |
> | (4) `m(c)` | `int` | phase 1: `char → int` widening |
> | (5) `m(1.0)` | `Object` | no primitive fits a `double`; phase 2 boxes to `Double`, which widens to `Object` |
> | (6) `m()` | `int...` | only varargs accepts zero arguments |
> | (7) `m(1, 2)` | `int...` | only varargs accepts two arguments |

**Q4.** Does this compile? If not, why, and how would you fix the call?

```java
static void print(String s)  { System.out.println("String"); }
static void print(Integer i) { System.out.println("Integer"); }

print(null);
```

> [!success]- Answer
> No: *reference to print is ambiguous*. `null` fits both `String` and `Integer`, and neither type is a subtype of the other, so neither method is more specific. Fix by casting: `print((String) null)`. If one overload took `Object` instead of `Integer`, `print(null)` would compile and pick the `String` version.

**Q5.** What is printed?

```java
static void show(Object o) { System.out.println("Object"); }
static void show(String s) { System.out.println("String"); }

Object x = "text";
show(x);
show((String) x);
show("text");
```

> [!success]- Answer
> ```
> Object
> String
> String
> ```
> Overload resolution uses the **declared** type. `x` is declared `Object`, so `show(Object)` is chosen, even though the object is really a `String`. The cast changes the compile-time type, and so the chosen overload.

**Q6.** What is printed?

```java
static int count = 0;
static int next() { return ++count; }
static void show(int a, int b, int c) { System.out.println(a + " " + b + " " + c); }

show(next(), next() * 10, next());
```

> [!success]- Answer
> `1 20 3`. Arguments are evaluated left to right, each fully before the next: `next()` → 1, `next() * 10` → `2 * 10 = 20`, `next()` → 3.

**Q7.** What does `mystery(5)` return, and what about `mystery(-1)`?

```java
static int mystery(int n) {
    if (n == 0) return 0;
    return n + mystery(n - 1);
}
```

> [!success]- Answer
> `mystery(5)` returns `15` (`5 + 4 + 3 + 2 + 1 + 0`). `mystery(-1)` goes `-1 → -2 → -3 → …` and never reaches `0`, so it throws `StackOverflowError`. The base case should be `n <= 0`.

**Q8.** Which pairs are legal overloads in the same class?

```java
(a) void f(int x)            and  void f(int y)
(b) int  f(int x)            and  void f(double x)
(c) void f(int... x)         and  void f(int[] x)
(d) static void f(String s)  and  void f(String s)
(e) void f(int a, String b)  and  void f(String a, int b)
(f) void f(long x)           and  long f(long x)
```

> [!success]- Answer
> | Pair | Legal? | Reason |
> |---|---|---|
> | (a) | ❌ | only the parameter names differ |
> | (b) | ✅ | different parameter types (the return type is irrelevant) |
> | (c) | ❌ | varargs is an array: same signature |
> | (d) | ❌ | only a modifier differs |
> | (e) | ✅ | different order of parameter types |
> | (f) | ❌ | only the return type differs |

**Q9.** A student wants a method that increments a counter held by the caller. Why doesn't this work, and give two ways to fix it.

```java
static void increment(int counter) { counter++; }
```

> [!success]- Answer
> `counter` is a copy of the caller's `int`, so incrementing it has no effect outside the method. Fixes:
> 1. **Return the new value**: `static int increment(int c) { return c + 1; }`, called as `counter = increment(counter);`.
> 2. **Pass a mutable holder**, for example a one-element array (`static void increment(int[] c) { c[0]++; }`), an `AtomicInteger`, or an object with a `count` field.
>
> Using `Integer counter` instead does **not** work: `Integer` is immutable, so `counter++` creates a new object and assigns it to the local copy.

---

## 14. Summary

- A method has a return type (or `void`), a name, a parameter list, and a body, and always lives inside a class. Its **signature** is the name plus the parameter types. It does not include the return type, parameter names, or modifiers.
- Arguments are evaluated **left to right** and copied into the parameters. `static main` cannot call instance methods directly.
- A non-`void` method must return a value on **every path the compiler can see**. The compiler does not evaluate `if` conditions (apart from constant-`true` loops), and unreachable statements are compile errors. `return` values are converted as in an assignment.
- Java is **always pass-by-value**. For references, the reference is copied: a method can mutate the shared object but can never reassign the caller's variable. Immutable types (`String`, `Integer`) therefore look unchanged.
- Each call gets its own **stack frame** for parameters and locals. Locals have no default value and vanish when the method returns.
- **Overloading** means the same name with different parameter lists. Overloads are chosen **at compile time** from the **declared** argument types: first widening, then boxing, then varargs, and within a phase the most specific method wins, or the call is ambiguous. Return type alone never distinguishes overloads.
- **Varargs** (`T... x`) is an array parameter. It must be last, accepts zero arguments (an empty array), and loses to any fixed-arity overload that fits.
- **Recursion** needs a base case that every input reaches. Without one it ends in a `StackOverflowError`. Naive recursion can be exponential (Fibonacci), and Java has no tail-call optimization.

## Related

- [[00 - Syllabus|Syllabus]]
- Previous: [[03 - Arrays|Arrays]] · Next: [[02 - Strings|Strings]]
- [[01 - Introduction to Java#7. The `main` Method|Introduction to Java § 7]]: the `main` method and its overloads
- [[04 - Type Casting|Type Casting]]: the widening and boxing conversions behind overload resolution
- [[03 - Operators#13. Evaluation Order — Not the Same as Precedence|Operators § 13]]: left-to-right evaluation
- [[01 - Classes and Objects|Classes and Objects]]: instance methods, constructors, `this`, `static`
- [[Java/04 - Object-Oriented Programming/04 - Polymorphism|Polymorphism]]: overriding vs. overloading
- [[Java/05 - Working with Data and Errors/02 - Generics|Generics]]: generic methods, overloads that clash after erasure
- [[DSA/Foundations/Recursion|DSA: Recursion]]
