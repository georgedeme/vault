# Arrays in Java

An <span class="hl-blue">array</span> is a **fixed-length**, **zero-indexed** container that holds values of **one type**. In Java an array is an **object**. It lives on the heap, the variable holds a *reference* to it, and it carries its own `length`. That one fact explains most of the surprising behaviour: assignment makes an alias rather than a copy, `==` and `.equals()` compare identity, printing shows `[I@1b6d3586`, and a method can change the caller's array. This chapter covers declaring, creating, accessing, copying, and comparing arrays, multi-dimensional (jagged) arrays, the `java.util.Arrays` utility class, and the places where the rules are easy to get wrong.

Loops over arrays are covered in [[02 - Loops|Loops]]. Arrays as a data structure (dynamic arrays, amortized resizing, rotation) are covered in [[DSA/Arrays|DSA: Arrays]]. This chapter is about the Java language feature.

## Contents

- [[#1. What an Array Is|1. What an Array Is]]
- [[#2. Declaring an Array Variable|2. Declaring an Array Variable]]
- [[#3. Creating and Initializing Arrays|3. Creating and Initializing Arrays]]
- [[#4. Accessing Elements and `length`|4. Accessing Elements and `length`]]
- [[#5. Iterating Over an Array|5. Iterating Over an Array]]
- [[#6. Arrays Are Objects — Reference Semantics|6. Arrays Are Objects — Reference Semantics]]
- [[#7. Copying Arrays|7. Copying Arrays]]
- [[#8. The `java.util.Arrays` Class|8. The `java.util.Arrays` Class]]
- [[#9. Multi-Dimensional Arrays|9. Multi-Dimensional Arrays]]
- [[#10. Arrays and Methods|10. Arrays and Methods]]
- [[#11. Array Types, Covariance, and `ArrayStoreException`|11. Array Types, Covariance, and `ArrayStoreException`]]
- [[#12. Common Array Algorithms|12. Common Array Algorithms]]
- [[#13. Common Pitfalls|13. Common Pitfalls]]
- [[#14. Quick Reference — Non-Obvious Outcomes|14. Quick Reference — Non-Obvious Outcomes]]
- [[#15. Practice — Trick Questions|15. Practice — Trick Questions]]
- [[#16. Summary|16. Summary]]

---

## 1. What an Array Is

> [!note] Definitions
> - An **array** is an object holding a fixed number of **elements** (also called *components*), all of the same **component type**.
> - Each element is identified by an **index**, an `int` from `0` to `length - 1`.
> - The **length** is fixed when the array is created and can **never change**.
> - The **component type** can be a primitive (`int[]`), a reference type (`String[]`), or itself an array type (`int[][]`, an array of `int[]`).

| Property | Arrays in Java |
|---|---|
| Size | fixed at creation, stored in the `final` field `length` |
| Indexing | `0` … `length - 1`, bounds **checked at runtime** |
| Element type | one type, checked at compile time (and at runtime for reference arrays, see [[#11. Array Types, Covariance, and `ArrayStoreException`|§ 11]]) |
| Storage | a heap object. The variable holds a reference to it |
| Access time | `a[i]` is O(1): the address is computed directly from `i` |
| Default contents | every element starts at its type's default value (`0`, `false`, `null`, …) |

If you need a sequence that grows and shrinks, use `ArrayList` (see [[Java/05 - Working with Data and Errors/03 - Collections Framework|Collections Framework]]). An array cannot be resized. You can only create a new, bigger one and copy into it ([[#7. Copying Arrays|§ 7]]).

---

## 2. Declaring an Array Variable

A declaration creates a **variable that can refer to** an array. It does **not** create an array.

```java
int[] scores;        // preferred: the brackets belong to the type
int scores2[];       // legal C-style form, discouraged
String[] names;
double[][] matrix;   // an array of double[]
```

> [!important] Key rule: brackets on the type apply to every variable, brackets on the name apply to that one only
> ```java
> int[] a, b;      // a is int[],   b is int[]
> int a[], b;      // a is int[],   b is int   (!)
> int[] a, b[];    // a is int[],   b is int[][]
> int[] a[], b;    // a is int[][], b is int[]
> ```
> This is a common exam question. Put the brackets on the type and declare one variable per line, and the problem goes away.

The length is **never** part of the declared type. `int[5] a;` and `int a[5];` are compile errors. The length belongs to the object, not to the variable, so the same `int[]` variable can refer to arrays of different lengths over its lifetime:

```java
int[] a = new int[3];
a = new int[100];    // fine: a now refers to a different, longer array
```

A declared but unassigned **local** array variable is not usable, just like any other local variable:

```java
int[] a;
System.out.println(a.length);   // compile error: variable a might not have been initialized
```

An array **field** that has not been assigned is `null` by default (see [[02 - Variables and Data Types#6. Default Values|Default Values]]), so the same code on a field compiles and throws `NullPointerException` at runtime.

---

## 3. Creating and Initializing Arrays

### 3.1 With `new` and a Length

```java
int[] a = new int[5];            // {0, 0, 0, 0, 0}
String[] s = new String[3];      // {null, null, null}
boolean[] flags = new boolean[4];// {false, false, false, false}
```

Every element gets its type's **default value**, whether the array is a local variable or a field:

| Component type | Default |
|---|---|
| `byte`, `short`, `int`, `long` | `0` / `0L` |
| `float`, `double` | `0.0f` / `0.0` |
| `char` | `'\u0000'` (the NUL character, **not** `' '` or `'0'`) |
| `boolean` | `false` |
| any reference type (`String`, `Integer`, `int[]`, …) | `null` |

> [!warning] Common mistake: an array of objects contains no objects
> `new String[3]` creates **one** array object with three `null` slots. It does not create any `String`s. The same is true for arrays of your own classes:
> ```java
> Student[] group = new Student[30];
> group[0].getName();                 // NullPointerException: group[0] is null
> group[0] = new Student("Maria");     // each element must be created separately
> ```

The length expression is evaluated **at runtime** and can be any expression of type `int` (or of a type that promotes to `int`):

```java
int n = scanner.nextInt();
int[] a = new int[n];            // OK: the length need not be a constant
int[] b = new int['A'];          // OK: char promotes to int, length 65
int[] c = new int[0];            // OK: an empty array, length 0
int[] d = new int[5L];           // compile error: possible lossy conversion from long to int
int[] e = new int[2.0];          // compile error: double is not an int
int[] f = new int[-1];           // compiles! throws NegativeArraySizeException at runtime
```

> [!info]- Why is a zero-length array useful?
> A method that returns "no results" should return an empty array, not `null`. The caller can then loop over it and check `length` without a `null` check. `new int[0]` and `{}` both create one. `main` also receives a zero-length (never `null`) `args` array when no command-line arguments are given (see [[01 - Introduction to Java#5.3 Command-Line Arguments|Command-Line Arguments]]).

### 3.2 With an Array Initializer

An **array initializer** lists the elements in braces. The length is inferred from the number of elements.

```java
int[] primes = {2, 3, 5, 7, 11};        // length 5
String[] days = {"Mon", "Tue", "Wed"};  // length 3
int[] empty = {};                        // length 0
int[] trailing = {1, 2, 3,};             // legal: a trailing comma is allowed
```

> [!important] Key rule: the short form `{...}` is only allowed in a declaration
> ```java
> int[] a = {1, 2, 3};           // OK: part of the declaration
>
> int[] b;
> b = {1, 2, 3};                 // compile error: illegal start of expression
> b = new int[] {1, 2, 3};       // OK: an array creation expression works anywhere
>
> sum({1, 2, 3});                // compile error
> sum(new int[] {1, 2, 3});      // OK: an "anonymous array"
>
> return {1, 2};                 // compile error
> return new int[] {1, 2};       // OK
> ```

> [!warning] Common mistake: a length **and** an initializer
> ```java
> int[] a = new int[3] {1, 2, 3};   // compile error: array creation with both dimension expression and initialization is illegal
> int[] a = new int[] {1, 2, 3};    // OK: the length comes from the initializer
> ```

Initializer elements are converted to the component type as in an assignment, so the usual widening and constant-narrowing rules apply:

```java
double[] d = {1, 2, 3};      // OK: {1.0, 2.0, 3.0}
byte[] b = {1, 2, 127};      // OK: each constant fits in a byte
byte[] c = {1, 2, 128};      // compile error: 128 does not fit in a byte
int[] i = {1, 2, 3.0};       // compile error: double to int needs a cast
long[] l = {1, 2, 3};        // OK
char[] ch = {'a', 98, 'c'};  // OK: {'a', 'b', 'c'}, 98 is a constant that fits in char
```

### 3.3 `var` and Arrays

```java
var a = new int[] {1, 2, 3};   // OK: a is int[]
var b = new int[5];            // OK
var c = {1, 2, 3};             // compile error: an initializer needs an explicit target type
var d[] = new int[3];          // compile error: var is not allowed as an element type of an array
```

See [[02 - Variables and Data Types#9.1 Where `var` Cannot Be Used|Where `var` Cannot Be Used]].

---

## 4. Accessing Elements and `length`

```java
int[] a = {10, 20, 30};
System.out.println(a[0]);        // 10  (first element)
System.out.println(a[a.length - 1]); // 30  (last element)
a[1] = 99;                       // {10, 99, 30}
a[2] += 5;                       // {10, 99, 35}
a[0]++;                          // {11, 99, 35}
```

### 4.1 `length` Is a Field, Not a Method

<span class="hl-yellow">A classic mix-up, and a compile error every time.</span>

| Type | How you get the size |
|---|---|
| array | `a.length` (a **field**, no parentheses) |
| `String` | `s.length()` (a **method**) |
| `ArrayList`, `List`, `Set`, `Map` | `list.size()` (a **method**) |

```java
int[] a = new int[4];
a.length;       // 4
a.length();     // compile error: cannot find symbol
a.size();       // compile error
a.length = 10;  // compile error: cannot assign a value to final variable length
```

### 4.2 Index Rules

- The index must be of type `int` after promotion. `byte`, `short`, and `char` indexes are promoted, so `a['a']` means `a[97]`.
- A `long` index is a compile error (`a[0L]`), and so is a `double` one (`a[1.0]`).
- Valid indexes are `0 … length - 1`. Anything else, **including negative indexes**, throws `ArrayIndexOutOfBoundsException` at **runtime**. The compiler does not check, even for a constant index.

```java
int[] a = new int[3];
a[3] = 1;      // compiles, then throws ArrayIndexOutOfBoundsException: Index 3 out of bounds for length 3
a[-1] = 1;     // compiles, then throws. Java has no Python-style negative indexing
int[] e = {};
e[0] = 1;      // throws: there is no index 0 in an empty array
```

> [!warning] Common mistake: `null` vs. empty
> `int[] a = null;` has no array at all, so `a.length`, `a[0]` and `for (int x : a)` all throw `NullPointerException`. `int[] a = {};` is a real array with `length == 0`: `a.length` is fine, `for (int x : a)` runs zero times, and only `a[0]` throws (with `ArrayIndexOutOfBoundsException`).

### 4.3 Evaluation Order of `a[i] = …`

Java evaluates an array assignment **strictly left to right**, and it checks for `null` and for bounds only **after** evaluating the right-hand side (JLS § 15.26.1):

1. Evaluate the array reference (`a`).
2. Evaluate the index (`i`).
3. Evaluate the right-hand side.
4. If the array reference is `null`, throw `NullPointerException`.
5. If the index is out of bounds, throw `ArrayIndexOutOfBoundsException`.
6. Store the value.

```java
int[] a = {0, 0, 0};
int i = 0;
a[i] = i = 2;          // index 0 is fixed first, so a == {2, 0, 0}, i == 2

i = 0;
int[] b = {10, 20, 30};
b[i++] = b[i];         // left index is 0 (i becomes 1), right side reads b[1]: b == {20, 20, 30}
```

> [!example]- Step by step: the side effects happen even when the store fails
> ```java
> int[] a = null;
> int i = 0;
> a[i++] = compute();   // compute() prints "called"
> ```
> | Step | What happens | State afterwards |
> |---|---|---|
> | 1 | array reference `a` evaluated → `null` (no exception yet) | |
> | 2 | index `i++` evaluated → `0` | `i == 1` |
> | 3 | `compute()` runs and prints `called` | |
> | 4 | array reference is `null` → `NullPointerException` | `i` is still `1` |
>
> The same holds for an out-of-bounds index: with `int[] b = new int[3];`, the statement `b[5] = compute();` still calls `compute()` before throwing. Reading follows the same order: in `x = a[i++]` with a `null` `a`, the index is evaluated (and `i` incremented) before the `NullPointerException` is thrown.

---

## 5. Iterating Over an Array

The loop forms are covered in detail in [[02 - Loops|Loops]]. For arrays:

```java
int[] a = {3, 1, 4, 1, 5};

// index-based: needed to write, to know the position, to go backwards, or to skip
for (int i = 0; i < a.length; i++) {
    a[i] *= 2;
}

// backwards
for (int i = a.length - 1; i >= 0; i--) {
    System.out.print(a[i] + " ");
}

// enhanced for (for-each): read-only access to each value
for (int x : a) {
    System.out.print(x + " ");
}
```

> [!warning] Common mistake: the for-each variable is a copy
> Assigning to the loop variable does **not** change the array (see [[02 - Loops#4. The Enhanced `for` Loop (for-each)|Loops § 4]]):
> ```java
> for (int x : a) { x = 0; }     // a is unchanged
> for (int i = 0; i < a.length; i++) { a[i] = 0; }   // a is now all zeros
> ```
> For an array of objects, the loop variable is a copy of the **reference**, so calling a mutating method on it (`s.setName(...)`) does change the object in the array. Only reassigning the variable (`s = new Student()`) has no effect.

> [!tip] Loop bounds
> Always write `i < a.length`, never `i <= a.length` (one step too far) and never a hard-coded number like `i < 5` (breaks when the array changes size).

---

## 6. Arrays Are Objects — Reference Semantics

### 6.1 Assignment Creates an Alias, Not a Copy

```java
int[] a = {1, 2, 3};
int[] b = a;          // b refers to the SAME array object
b[0] = 99;
System.out.println(a[0]);   // 99
```

```
a ──┐
    ├──► [ 99 | 2 | 3 ]
b ──┘
```

To get an independent array you must **copy** it ([[#7. Copying Arrays|§ 7]]).

### 6.2 Comparing Arrays: `==`, `.equals()`, `Arrays.equals`

<span class="hl-yellow">Exam favourite: `.equals()` on arrays does not compare contents.</span> Arrays do not override `Object.equals`, so it behaves exactly like `==`.

```java
int[] a = {1, 2, 3};
int[] b = {1, 2, 3};

a == b;                    // false : two different objects
a.equals(b);               // false : same as ==
Arrays.equals(a, b);       // true  : element by element

int[][] x = {{1, 2}, {3}};
int[][] y = {{1, 2}, {3}};
Arrays.equals(x, y);       // false : compares the inner int[] with equals, i.e. identity
Arrays.deepEquals(x, y);   // true  : recurses into nested arrays
```

### 6.3 Printing Arrays

```java
int[] a = {1, 2, 3};
System.out.println(a);                    // [I@1b6d3586  (type code + hash, not the contents)
System.out.println(Arrays.toString(a));   // [1, 2, 3]

int[][] g = {{1, 2}, {3, 4}};
System.out.println(Arrays.toString(g));     // [[I@4554617c, [I@74a14482]
System.out.println(Arrays.deepToString(g)); // [[1, 2], [3, 4]]
```

The `[I` prefix is the JVM's name for `int[]`. Others are `[D` (`double[]`), `[Z` (`boolean[]`), `[C` (`char[]`), `[[I` (`int[][]`), and `[Ljava.lang.String;` (`String[]`).

> [!warning] The `char[]` exception
> `println` has a special overload for `char[]` that prints the characters. That overload is only chosen when the argument is exactly a `char[]`:
> ```java
> char[] c = {'h', 'i'};
> System.out.println(c);             // hi
> System.out.println("c = " + c);    // c = [C@6d06d69c : concatenation calls c.toString()
> System.out.println(c.toString());  // [C@6d06d69c
> System.out.println(String.valueOf(c)); // hi
> System.out.println(new String(c));     // hi
> Object o = c;
> System.out.println(o);             // [C@6d06d69c : the println(Object) overload is chosen at compile time
> ```
> Overload choice depends on the compile-time type of the argument. See [[01 - Methods#7. Method Overloading|Methods § 7]].

### 6.4 `final` Arrays Are Still Mutable

`final` fixes the **reference**, not the contents (see [[02 - Variables and Data Types#7.2 `final` Doesn't Mean Immutable|`final` Doesn't Mean Immutable]]):

```java
final int[] a = {1, 2, 3};
a[0] = 99;            // OK: the array's contents can change
a = new int[3];       // compile error: cannot assign a value to final variable a
```

There is no way to make a Java array read-only. For a read-only view use `List.of(...)` or `Collections.unmodifiableList(...)`.

---

## 7. Copying Arrays

| Technique | Creates a new array? | Can change length? | Notes |
|---|---|---|---|
| `b = a` | ❌ | — | alias only, not a copy |
| manual loop | ✅ (you create it) | ✅ | most flexible, most verbose |
| `a.clone()` | ✅ | ❌ | returns `int[]` directly (no cast needed) |
| `Arrays.copyOf(a, newLength)` | ✅ | ✅ | truncates, or pads with default values |
| `Arrays.copyOfRange(a, from, to)` | ✅ | ✅ | `from` inclusive, `to` exclusive, `to` may exceed `a.length` (pads) |
| `System.arraycopy(src, srcPos, dest, destPos, len)` | ❌ (`dest` must exist) | — | fastest, handles overlapping ranges correctly |

```java
int[] a = {1, 2, 3};

int[] c1 = a.clone();                   // {1, 2, 3}
int[] c2 = Arrays.copyOf(a, 5);         // {1, 2, 3, 0, 0}
int[] c3 = Arrays.copyOf(a, 2);         // {1, 2}
int[] c4 = Arrays.copyOfRange(a, 1, 3); // {2, 3}
int[] c5 = Arrays.copyOfRange(a, 2, 6); // {3, 0, 0, 0}

int[] dest = new int[5];
System.arraycopy(a, 0, dest, 1, 3);     // dest == {0, 1, 2, 3, 0}
```

Growing an array is always "create a bigger one and copy":

```java
a = Arrays.copyOf(a, a.length * 2);     // a now refers to a new, twice-as-long array
```

> [!warning] Exceptions from the copy methods
> | Call | Result |
> |---|---|
> | `Arrays.copyOf(a, -1)` | `NegativeArraySizeException` |
> | `Arrays.copyOfRange(a, 2, 1)` (`from > to`) | `IllegalArgumentException` |
> | `Arrays.copyOfRange(a, 4, 6)` with `a.length == 3` (`from > length`) | `ArrayIndexOutOfBoundsException` |
> | `System.arraycopy` with any range outside `src` or `dest` | `ArrayIndexOutOfBoundsException` (nothing is copied) |
> | `System.arraycopy(intArr, 0, longArr, 0, n)` | `ArrayStoreException`: no primitive widening between array types |
> | `System.arraycopy(null, …)` | `NullPointerException` |

### 7.1 Shallow vs. Deep Copy

Every technique above is a **shallow copy**: it copies the element values. For primitives that is the data itself. For references (objects, or the rows of a 2D array) it copies the **references**, so the copy and the original share the same objects.

```java
int[][] g = {{1, 2}, {3, 4}};
int[][] s = g.clone();       // new outer array, SAME row arrays
s[0][0] = 99;
System.out.println(g[0][0]); // 99 : the row is shared
s[1] = new int[] {7, 7};
System.out.println(g[1][0]); // 3  : replacing a row in s does not affect g
```

```
          row 0     row 1
g ──► [   •    |    •   ]
          │         └──────► [3, 4]
          ▼
       [99, 2]   ◄── shared by g[0] and s[0]
          ▲
          │         ┌──────► [7, 7]   (new row, only in s)
s ──► [   •    |    •   ]
```

A **deep copy** of a 2D array copies each row:

```java
int[][] deep = new int[g.length][];
for (int r = 0; r < g.length; r++) {
    deep[r] = g[r].clone();
}
```

> [!info]- `System.arraycopy` and overlapping ranges
> When `src` and `dest` are the same array and the ranges overlap, `System.arraycopy` behaves as if the source range were first copied to a temporary array. This makes it the standard way to shift elements:
> ```java
> int[] a = {1, 2, 3, 4, 5};
> System.arraycopy(a, 0, a, 1, 4);  // shift right: {1, 1, 2, 3, 4}
> System.arraycopy(a, 1, a, 0, 4);  // shift left:  {1, 2, 3, 4, 4}
> ```
> A naive forward loop `for (i = 0; i < 4; i++) a[i + 1] = a[i];` would instead smear the first value across the array: `{1, 1, 1, 1, 1}`. Shifting right must loop **backwards**.

---

## 8. The `java.util.Arrays` Class

`java.util.Arrays` contains `static` helper methods for arrays. It needs `import java.util.Arrays;`.

| Method | What it does |
|---|---|
| `Arrays.toString(a)` | `"[1, 2, 3]"`. `"null"` if `a` is `null` |
| `Arrays.deepToString(a)` | same, recursing into nested arrays |
| `Arrays.equals(a, b)` | same length and equal elements, in order |
| `Arrays.deepEquals(a, b)` | same, recursing into nested arrays |
| `Arrays.sort(a)` | sorts in place, ascending |
| `Arrays.sort(a, from, to)` | sorts only `[from, to)` |
| `Arrays.sort(objArr, comparator)` | custom order (reference arrays only) |
| `Arrays.binarySearch(a, key)` | index of `key` in a **sorted** array (see below) |
| `Arrays.fill(a, value)` | sets every element to `value` |
| `Arrays.fill(a, from, to, value)` | sets `[from, to)` |
| `Arrays.copyOf`, `Arrays.copyOfRange` | see [[#7. Copying Arrays|§ 7]] |
| `Arrays.asList(T... a)` | a fixed-size `List` view backed by the array |
| `Arrays.stream(a)` | an `IntStream` / `Stream<T>` over the elements |
| `Arrays.hashCode(a)`, `Arrays.deepHashCode(a)` | content-based hash codes |
| `Arrays.compare(a, b)`, `Arrays.mismatch(a, b)` | lexicographic comparison / first differing index (Java 9+) |

### 8.1 Sorting

```java
int[] a = {5, 2, 9, 1};
Arrays.sort(a);                      // a == {1, 2, 5, 9}  (in place, returns void)

String[] s = {"banana", "Apple", "cherry"};
Arrays.sort(s);                      // {"Apple", "banana", "cherry"}: uppercase sorts before lowercase
Arrays.sort(s, String.CASE_INSENSITIVE_ORDER);

Integer[] boxed = {5, 2, 9, 1};
Arrays.sort(boxed, Collections.reverseOrder());   // {9, 5, 2, 1}
```

> [!warning] Common mistakes with `sort`
> - `Arrays.sort` returns `void`. `int[] sorted = Arrays.sort(a);` is a compile error.
> - **There is no descending sort for primitive arrays.** `Arrays.sort(intArr, Collections.reverseOrder())` is a compile error, because comparators only work on objects. Either sort ascending and reverse the array, or use an `Integer[]`.
> - `String`s are sorted by character code, so `"Z" < "a"` and `"10" < "9"`.
> - Sorting an array of your own class without a comparator requires the class to implement `Comparable`. Otherwise you get a `ClassCastException` at runtime.

> [!info]- Which algorithm does `Arrays.sort` use?
> For primitive arrays: a dual-pivot quicksort, O(n log n) on average. It is not stable, but stability does not matter for primitives because equal values cannot be told apart. For object arrays: TimSort, a **stable** merge-sort variant, O(n log n) worst case. Stable means equal elements keep their original relative order, which matters when sorting records by one field after another. More in [[DSA/Sorting Algorithms|DSA: Sorting Algorithms]].

### 8.2 `binarySearch`

```java
int[] a = {1, 3, 5, 7};
Arrays.binarySearch(a, 5);   //  2 : found at index 2
Arrays.binarySearch(a, 4);   // -3 : not found
```

> [!important] Key rule: a negative result encodes where the key would go
> If the key is missing, `binarySearch` returns `-(insertionPoint) - 1`, where `insertionPoint` is the index at which the key would be inserted to keep the array sorted. For `4` above, the insertion point is `2`, so the result is `-3`. The `- 1` is there so that "not found, would go at index 0" (`-1`) cannot be confused with "found at index 0" (`0`).
>
> - The array **must already be sorted**. On an unsorted array the result is undefined: it may be wrong without any exception.
> - With duplicates, it returns the index of **any one** of the equal elements, not necessarily the first.

### 8.3 `fill`

```java
int[] a = new int[5];
Arrays.fill(a, 7);             // {7, 7, 7, 7, 7}
Arrays.fill(a, 1, 3, 0);       // {7, 0, 0, 7, 7}
```

> [!warning] `fill` with an object shares one object
> ```java
> int[][] grid = new int[3][];
> Arrays.fill(grid, new int[3]);   // all three rows are the SAME int[] object
> grid[0][0] = 5;                  // grid[1][0] and grid[2][0] are now 5 too
> ```
> And `Arrays.fill(new int[3][3], 0)` **compiles** (it calls `fill(Object[], Object)` with a boxed `Integer`) but throws `ArrayStoreException` at runtime, because an `Integer` cannot be stored where an `int[]` row belongs. To fill a 2D array, fill each row: `for (int[] row : grid) Arrays.fill(row, 0);`

### 8.4 `asList`

```java
String[] arr = {"a", "b", "c"};
List<String> list = Arrays.asList(arr);
list.set(0, "z");            // OK, writes through: arr[0] is now "z"
arr[1] = "y";                // visible in list too: list.get(1) is "y"
list.add("d");               // UnsupportedOperationException: fixed size
list.remove(0);              // UnsupportedOperationException
List<String> growable = new ArrayList<>(Arrays.asList(arr));   // an independent, resizable copy
```

<span class="hl-red">Trap: `Arrays.asList` on a primitive array.</span> Generics cannot hold primitives, so the whole `int[]` becomes the single element:

```java
int[] p = {1, 2, 3};
Arrays.asList(p).size();         // 1 : the list is List<int[]>
Integer[] q = {1, 2, 3};
Arrays.asList(q).size();         // 3 : List<Integer>
Arrays.asList(1, 2, 3).size();   // 3 : varargs are boxed one by one
```

---

## 9. Multi-Dimensional Arrays

<span class="hl-blue">Java has no true multi-dimensional arrays.</span> An `int[][]` is an **array of references to `int[]` arrays**. Each row is a separate object, and rows can have different lengths.

### 9.1 Rectangular Arrays

```java
int[][] m = new int[3][4];       // 3 rows, 4 columns, all zero
m[1][2] = 7;                     // row 1, column 2
m.length;                        // 3 : number of rows
m[0].length;                     // 4 : length of row 0

int[][] n = {
    {1, 2, 3},
    {4, 5, 6}
};                               // 2 × 3
```

```
m ──► [ • | • | • ]           (outer array: length 3)
        │   │   │
        │   │   └──► [0, 0, 0, 0]
        │   └──────► [0, 0, 7, 0]
        └──────────► [0, 0, 0, 0]
```

`new int[3][4]` creates **four** objects: one outer array and three rows.

### 9.2 Jagged (Ragged) Arrays

Only the **first** dimension is required in `new`. The missing ones leave the rows `null`, to be created individually:

```java
int[][] tri = new int[3][];      // tri == {null, null, null}
tri[0] = new int[1];
tri[1] = new int[2];
tri[2] = new int[3];

int[][] jag = {{1}, {2, 3}, {4, 5, 6}};   // same shape, via an initializer

int[][] bad = new int[][3];      // compile error: the first dimension must be given
int[][] x = new int[3][];
x[0][0] = 1;                     // NullPointerException: x[0] is null
```

A rectangular array can become jagged at any time, because a row is just an element that holds a reference:

```java
int[][] m = new int[2][3];
m[0] = new int[10];              // legal: row 0 now has length 10
m[1] = null;                     // legal too
```

### 9.3 Iterating

```java
// index-based: use m[r].length, not m[0].length, so jagged arrays work
for (int r = 0; r < m.length; r++) {
    for (int c = 0; c < m[r].length; c++) {
        System.out.print(m[r][c] + " ");
    }
    System.out.println();
}

// for-each: the outer variable is a row (int[]), the inner is a value
for (int[] row : m) {
    for (int v : row) {
        System.out.print(v + " ");
    }
    System.out.println();
}
```

> [!warning] Common mistakes with 2D arrays
> - **`m[0].length` as the column count for every row.** Fine for rectangular arrays, wrong for jagged ones (index out of bounds, or rows skipped).
> - **Swapping the indexes.** `m[r][c]` is row first, column second. For a 3 × 4 array, `m[3][0]` throws while `m[0][3]` is fine.
> - **`m[1, 2]` (C#/Python style)** is a compile error. Java uses `m[1][2]`.
> - **`m.length` for the total number of elements.** It is the number of rows. The total is the sum of the row lengths.
> - **`clone()` or `Arrays.copyOf` on a 2D array** is shallow: the rows are shared ([[#7.1 Shallow vs. Deep Copy|§ 7.1]]).
> - **Printing with `Arrays.toString`** shows row addresses. Use `Arrays.deepToString`.

### 9.4 Declaration Forms and Higher Dimensions

```java
int[][] a;       // preferred
int a[][];       // legal
int[] a[];       // legal, and confusing
int[][][] cube = new int[2][3][4];   // 2 × 3 × 4; cube[i][j] is an int[] of length 4
int[][][] partial = new int[2][3][]; // legal: only trailing dimensions may be omitted
int[][][] gap = new int[2][][4];     // compile error: cannot skip a middle dimension
```

> [!info]- Row-major traversal is faster
> Each row is a separate contiguous block. Looping row by row (`r` outer, `c` inner) reads memory in order and uses the CPU cache well. Looping column by column (`c` outer, `r` inner) jumps to a different row object on every step, which can be several times slower for large arrays. The result is the same. Only the speed differs.

---

## 10. Arrays and Methods

Java passes **every** argument by value (see [[01 - Methods#5. Parameter Passing — Always Pass-by-Value|Methods § 5]]). For an array argument, the value that gets copied is the **reference**. So:

- The method **can change the elements** of the caller's array (both variables refer to the same object).
- The method **cannot make the caller's variable refer to a different array**. Reassigning the parameter only changes the method's local copy of the reference.

```java
static void zeroFirst(int[] arr) {
    arr[0] = 0;              // visible to the caller
}

static void replace(int[] arr) {
    arr = new int[] {9, 9};  // only the local parameter changes
    arr[0] = 42;             // modifies the NEW array, which the caller never sees
}

int[] data = {5, 6, 7};
zeroFirst(data);             // data == {0, 6, 7}
replace(data);               // data is still {0, 6, 7}
```

To give the caller a new array, **return** it:

```java
static int[] doubled(int[] arr) {
    int[] result = new int[arr.length];
    for (int i = 0; i < arr.length; i++) {
        result[i] = arr[i] * 2;
    }
    return result;
}
```

> [!tip] Returning arrays
> - Return an empty array (`new int[0]`) rather than `null` for "no results".
> - If a method returns an internal array field, the caller can modify your object's state through it. Return a copy (`return data.clone();`) when that matters (see [[Java/04 - Object-Oriented Programming/02 - Encapsulation|Encapsulation]]).

Varargs (`int... values`) are arrays under the hood. See [[01 - Methods#8. Variable-Length Arguments (Varargs)|Methods § 8]].

---

## 11. Array Types, Covariance, and `ArrayStoreException`

### 11.1 Array Type Compatibility

Array types have their own assignment rules, which differ from the element types' rules:

| Assignment | Compiles? | Why |
|---|---|---|
| `long[] l = new int[3];` | ❌ | no widening between primitive array types |
| `double[] d = new int[3];` | ❌ | same |
| `Object o = new int[3];` | ✅ | every array is an `Object` |
| `Object[] o = new int[3];` | ❌ | `int` is not an `Object`, so `int[]` is not an `Object[]` |
| `Object[] o = new String[3];` | ✅ | reference arrays are **covariant** |
| `Object[] o = new int[3][3];` | ✅ | the elements are `int[]`, which are `Object`s |
| `String[] s = new Object[3];` | ❌ | would need a downcast, and it would fail at runtime |
| `int[] a = (int[]) someObject;` | ✅ | a cast from `Object` compiles and is checked at runtime |

### 11.2 Covariance and `ArrayStoreException`

Because `String[]` is a subtype of `Object[]`, the compiler cannot always know what an array really holds. The JVM therefore checks every store into a reference array at runtime:

```java
Object[] objs = new String[2];   // compiles: covariance
objs[0] = "hello";               // OK: the real array is a String[]
objs[1] = Integer.valueOf(1);    // compiles, throws ArrayStoreException at runtime
```

<span class="hl-yellow">Exam favourite:</span> the static type of `objs` is `Object[]`, so the compiler allows any `Object`, but the **runtime type** of the array is `String[]`, and that is what is checked.

### 11.3 Arrays and Generics Don't Mix

```java
List<String>[] lists = new List<String>[10];   // compile error: generic array creation
T[] arr = new T[10];                            // compile error inside a generic class
List<String>[] ok = new List[10];              // compiles with an "unchecked" warning
```

Generics are checked only at compile time and erased at runtime, while arrays check their element type at runtime. The two models conflict, so Java forbids creating arrays of generic types. The usual answer is to use `List<List<String>>` instead. More in [[Java/05 - Working with Data and Errors/03 - Collections Framework|Collections Framework]].

---

## 12. Common Array Algorithms

These basic patterns come up constantly. Each is shown as pseudocode first and then in Java. Their complexity is covered in [[DSA/Foundations/Complexity Analysis|Complexity Analysis]], and the full algorithm treatments are in [[DSA/Arrays|DSA: Arrays]] and [[DSA/Binary Search|DSA: Binary Search]].

### 12.1 Sum and Average

```
sum ← 0
for each x in A:
    sum ← sum + x
average ← sum / length(A)        -- undefined if A is empty
```

```java
static double average(int[] a) {
    if (a.length == 0) {
        throw new IllegalArgumentException("empty array");
    }
    long sum = 0;                    // long: an int sum can overflow
    for (int x : a) {
        sum += x;
    }
    return (double) sum / a.length;  // cast first, otherwise integer division
}
```

> [!warning] Two traps in one line
> `int avg = sum / a.length;` truncates (integer division, see [[03 - Operators#3. Division and Remainder — The Special Cases|Operators § 3]]), and if `a` is empty it throws `ArithmeticException: / by zero`. With a `double` cast and an empty array you get `NaN` instead (`0.0 / 0`), silently.

### 12.2 Maximum (and Minimum)

```
if A is empty: error
max ← A[0]
for i ← 1 to length(A) - 1:
    if A[i] > max:
        max ← A[i]
return max
```

```java
static int max(int[] a) {
    if (a.length == 0) {
        throw new IllegalArgumentException("empty array");
    }
    int max = a[0];                  // NOT 0: all elements might be negative
    for (int i = 1; i < a.length; i++) {
        if (a[i] > max) {
            max = a[i];
        }
    }
    return max;
}
```

> [!warning] Common mistake: starting from `0`
> `int max = 0;` returns `0` for `{-5, -2, -9}`, a value that is not even in the array. Start from `a[0]`, or from `Integer.MIN_VALUE` (and for a minimum, from `a[0]` or `Integer.MAX_VALUE`).

### 12.3 Linear Search

```
for i ← 0 to length(A) - 1:
    if A[i] = key:
        return i
return -1                        -- not found
```

```java
static int indexOf(int[] a, int key) {
    for (int i = 0; i < a.length; i++) {
        if (a[i] == key) {
            return i;
        }
    }
    return -1;
}
```

For `String[]` or other object arrays, compare with `a[i].equals(key)` (or `Objects.equals(a[i], key)` if elements may be `null`), never `==` (see [[02 - Strings#2. Creating Strings — Literals vs. `new`|Strings § 2]]).

### 12.4 Reverse In Place

```
left ← 0
right ← length(A) - 1
while left < right:
    swap A[left] and A[right]
    left ← left + 1
    right ← right - 1
```

```java
static void reverse(int[] a) {
    int left = 0, right = a.length - 1;
    while (left < right) {
        int tmp = a[left];
        a[left] = a[right];
        a[right] = tmp;
        left++;
        right--;
    }
}
```

> [!warning] Common mistake: swapping all the way to the end
> `for (int i = 0; i < a.length; i++) swap(a[i], a[a.length - 1 - i])` swaps every pair **twice**, putting the array back as it was. Stop at the middle (`i < a.length / 2`). Also, a `swap(int x, int y)` method cannot swap the caller's elements (see [[01 - Methods#5. Parameter Passing — Always Pass-by-Value|Methods § 5]]). It must take the array and two indexes: `swap(int[] a, int i, int j)`.

### 12.5 Binary Search (Sorted Array)

```
low ← 0
high ← length(A) - 1
while low ≤ high:
    mid ← low + (high - low) / 2
    if A[mid] = key:  return mid
    if A[mid] < key:  low ← mid + 1
    else:             high ← mid - 1
return -1
```

```java
static int binarySearch(int[] a, int key) {
    int low = 0, high = a.length - 1;
    while (low <= high) {
        int mid = low + (high - low) / 2;   // not (low + high) / 2: that can overflow
        if (a[mid] == key) {
            return mid;
        } else if (a[mid] < key) {
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }
    return -1;
}
```

The midpoint overflow is explained in [[03 - Operators#4. Integer Overflow|Operators § 4]]. Using `low < high` instead of `low <= high` misses the key when it is the last remaining candidate.

### 12.6 Counting with a Frequency Array

When values fall in a small known range (like `0 … 9`, or the letters `'a' … 'z'`), an array indexed by value counts occurrences in one pass:

```
count ← array of size K, all 0
for each x in A:
    count[x] ← count[x] + 1
```

```java
static int[] letterCounts(String s) {
    int[] count = new int[26];
    for (char ch : s.toCharArray()) {
        if (ch >= 'a' && ch <= 'z') {
            count[ch - 'a']++;           // 'a' → 0, 'b' → 1, …
        }
    }
    return count;
}
```

`ch - 'a'` is an `int` (char arithmetic, see [[04 - Type Casting#5. `char` — A Special Case|Type Casting § 5]]), which is exactly what an index needs. Without the range check, an uppercase letter or a digit gives a negative index and an `ArrayIndexOutOfBoundsException`.

---

## 13. Common Pitfalls

- **Off-by-one:** `i <= a.length` in a loop condition, or `a[a.length]` for the last element. The last index is `a.length - 1`.
- **`length` vs. `length()` vs. `size()`**: arrays use the field `length`, `String` uses the method `length()`, collections use `size()`.
- **Assuming `b = a` copies.** It creates an alias. Use `clone()`, `Arrays.copyOf`, or `System.arraycopy`.
- **Comparing with `==` or `.equals()`.** Both compare identity. Use `Arrays.equals`, or `Arrays.deepEquals` for nested arrays.
- **Printing with `println(a)`** gives `[I@…`. Use `Arrays.toString`, or `Arrays.deepToString` for nested arrays.
- **Forgetting that `new Foo[n]` creates no `Foo` objects.** Every element is `null` until assigned.
- **Using `{...}` outside a declaration.** Write `new int[] {...}` instead.
- **`new int[3] {1, 2, 3}`**: a length and an initializer together is a compile error.
- **Initializing `max` to `0`**, which fails when all values are negative.
- **Expecting an array to grow.** Arrays have a fixed length. Copy into a bigger one, or use `ArrayList`.
- **Shallow copies of 2D arrays**: `clone()` and `Arrays.copyOf` share the row arrays.
- **`Arrays.fill(grid, new int[n])`** makes every row the same object.
- **`Arrays.asList(intArray)`** gives a one-element `List<int[]>`. And the list returned by `asList` is fixed-size.
- **`Arrays.binarySearch` on an unsorted array** returns an unreliable result with no error.
- **Modifying via the for-each variable**, which only changes a local copy.
- **`Object[] o = new String[n]; o[0] = 1;`**: compiles, but throws `ArrayStoreException`.

---

## 14. Quick Reference — Non-Obvious Outcomes

| Code | Result | Why |
|---|---|---|
| `int[] a, b;` | both `int[]` | brackets on the type apply to all |
| `int a[], b;` | `a` is `int[]`, `b` is `int` | brackets on the name apply to one |
| `int[] a = new int[3] {1,2,3};` | compile error | length + initializer |
| `int[] a; a = {1, 2};` | compile error | `{...}` only in a declaration |
| `int[] a = {1, 2, 3,};` | compiles, length 3 | trailing comma allowed |
| `new int[-1]` | compiles, `NegativeArraySizeException` | size checked at runtime |
| `new int[5L]` | compile error | length must be `int` |
| `new int['A'].length` | `65` | `char` promotes to `int` |
| `char[] c = new char[1];` → `(int) c[0]` | `0` | default `char` is `'\u0000'` |
| `String[] s = new String[2];` → `s[0] + "x"` | `"nullx"` | default reference is `null` |
| `a.length()` | compile error | `length` is a field |
| `a[-1]` | `ArrayIndexOutOfBoundsException` | no negative indexing |
| `a[i] = i = 2` (i = 0) | `a[0] == 2` | index evaluated before the RHS |
| `a[i++] = f()`, `a == null` | `f()` runs, `i` incremented, then NPE | null check after RHS |
| `int[] b = a; b[0] = 9;` | `a[0] == 9` | alias |
| `new int[]{1} == new int[]{1}` | `false` | identity |
| `new int[]{1}.equals(new int[]{1})` | `false` | `equals` not overridden |
| `Arrays.equals(new int[]{1}, new int[]{1})` | `true` | element comparison |
| `Arrays.equals` on two equal `int[][]` | `false` | inner rows compared by identity |
| `println(new int[]{1})` | `[I@…` | `Object.toString` |
| `println(new char[]{'h','i'})` | `hi` | `println(char[])` overload |
| `println("" + new char[]{'h','i'})` | `[C@…` | concatenation uses `toString()` |
| `final int[] a = {1}; a[0] = 2;` | compiles | `final` fixes the reference only |
| `Arrays.copyOf(new int[]{1,2}, 4)` | `[1, 2, 0, 0]` | pads with defaults |
| `Arrays.copyOfRange(a, 1, 1)` | `[]` | empty range |
| `Arrays.binarySearch(new int[]{1,3,5,7}, 4)` | `-3` | `-(2) - 1` |
| `Arrays.asList(new int[]{1,2,3}).size()` | `1` | `List<int[]>` |
| `Arrays.asList(1, 2).add(3)` | `UnsupportedOperationException` | fixed-size view |
| `Arrays.fill(new int[2][2], 0)` | `ArrayStoreException` | `Integer` stored into an `int[][]` |
| `Arrays.sort(intArr, Collections.reverseOrder())` | compile error | comparators need objects |
| `int[][] m = new int[3][]; m[0][0] = 1;` | `NullPointerException` | rows not created |
| `new int[][3]` | compile error | first dimension required |
| `new int[3][4].length` | `3` | number of rows |
| `long[] l = new int[2];` | compile error | no primitive array widening |
| `Object[] o = new int[2];` | compile error | `int` is not an `Object` |
| `Object[] o = new String[1]; o[0] = 1;` | `ArrayStoreException` | runtime element check |
| `new List<String>[3]` | compile error | generic array creation |
| `for (int x : (int[]) null)` | `NullPointerException` | no array to iterate |

---

## 15. Practice — Trick Questions

**Q1.** What are the types of `a`, `b`, `c`, and `d`?

```java
int[] a, b[];
int c[], d;
```

> [!success]- Answer
> | Variable | Type | Reason |
> |---|---|---|
> | `a` | `int[]` | base type `int[]` |
> | `b` | `int[][]` | base type `int[]` plus its own `[]` |
> | `c` | `int[]` | base type `int` plus its own `[]` |
> | `d` | `int` | base type `int`, no brackets of its own |

**Q2.** Which lines compile? For those that compile, which throw at runtime?

```java
int[] a = new int[0];        // (1)
int[] b = new int[] {};      // (2)
int[] c = new int[2] {1, 2}; // (3)
int[] d = {1, 2};            // (4)
d = {3, 4};                  // (5)
int[] e = new int[-2];       // (6)
int x = b[0];                // (7)
```

> [!success]- Answer
> | Line | Compiles? | Runtime | Reason |
> |---|---|---|---|
> | (1) | ✅ | OK | empty array |
> | (2) | ✅ | OK | empty array via an initializer |
> | (3) | ❌ | — | length and initializer together |
> | (4) | ✅ | OK | initializer in a declaration |
> | (5) | ❌ | — | `{...}` outside a declaration |
> | (6) | ✅ | `NegativeArraySizeException` | size checked at runtime |
> | (7) | ✅ | `ArrayIndexOutOfBoundsException` | `b` has no index 0 |

**Q3.** What is printed?

```java
int[] a = {1, 2, 3};
int[] b = a;
int[] c = a.clone();
b[0] = 10;
c[1] = 20;
System.out.println(Arrays.toString(a));
System.out.println(a == b);
System.out.println(a.equals(c));
System.out.println(Arrays.equals(a, new int[] {10, 2, 3}));
```

> [!success]- Answer
> ```
> [10, 2, 3]
> true
> false
> true
> ```
> `b` is an alias of `a`, so `b[0] = 10` changes `a`. `c` is an independent copy, so `c[1] = 20` does not. `a.equals(c)` compares identity. `Arrays.equals` compares the elements.

**Q4.** What is printed?

```java
static void change(int[] arr, int n) {
    arr[0] = 100;
    n = 100;
    arr = new int[] {-1, -1};
    arr[1] = 100;
}

int[] data = {1, 2};
int num = 1;
change(data, num);
System.out.println(data[0] + " " + data[1] + " " + num);
```

> [!success]- Answer
> `100 2 1`.
>
> | Statement | Affects the caller? | Why |
> |---|---|---|
> | `arr[0] = 100` | ✅ `data[0]` becomes 100 | `arr` and `data` refer to the same array |
> | `n = 100` | ❌ | `n` is a copy of the `int` |
> | `arr = new int[]{-1, -1}` | ❌ | only the local reference changes |
> | `arr[1] = 100` | ❌ | modifies the new array, which the caller never sees |

**Q5.** What is printed, or what goes wrong?

```java
int[][] m = new int[3][];
m[0] = new int[] {1, 2, 3};
m[1] = m[0];
m[1][0] = 9;
System.out.println(m[0][0]);
System.out.println(m.length + " " + m[0].length);
System.out.println(m[2].length);
```

> [!success]- Answer
> ```
> 9
> 3 3
> ```
> followed by a `NullPointerException` on the last line. `m[1] = m[0]` makes rows 0 and 1 the same object, so writing through `m[1]` changes `m[0]`. `m[2]` was never assigned, so it is `null`.

**Q6.** What does this print?

```java
char[] name = {'J', 'a', 'v', 'a'};
System.out.println(name);
System.out.println("Name: " + name);
System.out.println(name.length);
```

> [!success]- Answer
> ```
> Java
> Name: [C@<hash>
> 4
> ```
> `println(char[])` prints the characters. In the second line the argument is a `String` produced by concatenation, and concatenation calls `name.toString()`, which is `Object`'s version. Use `"Name: " + new String(name)` or `String.valueOf(name)`.

**Q7.** What is `a` after this code?

```java
int[] a = {1, 2, 3, 4};
int i = 0;
a[i] = i = 3;
a[i] = a[i - 1] = i--;
```

> [!success]- Answer
> `{3, 2, 3, 3}`.
>
> | Statement | Evaluation | State afterwards |
> |---|---|---|
> | `a[i] = i = 3` | index fixed at `0`, RHS `i = 3` gives `3` | `a == {3, 2, 3, 4}`, `i == 3` |
> | `a[i] = …` | index fixed at `3` | |
> | `a[i - 1] = …` | index fixed at `3 - 1 = 2` | |
> | `i--` | value `3`, then `i` becomes `2` | `i == 2` |
> | assignments | `a[2] = 3`, then `a[3] = 3` | `a == {3, 2, 3, 3}` |

**Q8.** Does this compile? If so, what happens when it runs?

```java
Object[] things = new Integer[3];
things[0] = 42;
things[1] = "forty-two";
```

> [!success]- Answer
> It compiles. Line 2 is fine: `42` is boxed to an `Integer`, and the real array is an `Integer[]`. Line 3 throws `ArrayStoreException: java.lang.String` at runtime. The compiler only sees `Object[]`, but the JVM checks each store against the array's real component type.

**Q9.** A student writes this method to find the largest value. Give an input where it is wrong, and fix it.

```java
static int largest(int[] a) {
    int max = 0;
    for (int i = 0; i <= a.length; i++) {
        if (a[i] > max) max = a[i];
    }
    return max;
}
```

> [!success]- Answer
> There are two bugs.
> 1. `i <= a.length` reads `a[a.length]` on the last pass, so **every** call throws `ArrayIndexOutOfBoundsException`. It should be `i < a.length`.
> 2. With that fixed, `max = 0` still gives the wrong answer for `{-3, -7, -1}` (returns `0` instead of `-1`). Start from `a[0]` and loop from `i = 1`, after checking that the array is not empty (see [[#12.2 Maximum (and Minimum)|§ 12.2]]).

**Q10.** What is printed?

```java
int[] a = {5, 3, 1};
List<int[]> l1 = Arrays.asList(a);
List<Integer> l2 = Arrays.asList(5, 3, 1);
System.out.println(l1.size() + " " + l2.size());
Arrays.sort(a);
System.out.println(l1.get(0)[0]);
```

> [!success]- Answer
> ```
> 1 3
> 1
> ```
> `Arrays.asList(a)` wraps the whole `int[]` as one element. The list holds a reference to `a` itself (not a copy), so after sorting `a` in place, `l1.get(0)` is the sorted array and its first element is `1`.

---

## 16. Summary

- An array is a **fixed-length object** holding elements of one type, indexed from `0` to `length - 1`. The length is a `final` **field** (`a.length`, no parentheses).
- **Declaration does not create an array.** `new int[n]` fills the array with default values, and `{...}` lists the elements but is only allowed in a declaration (use `new int[] {...}` elsewhere). A length and an initializer cannot be combined.
- Bounds and negative sizes are checked **at runtime**. `a[-1]`, `a[a.length]` and `new int[-1]` all compile.
- An array variable holds a **reference**. Assignment makes an **alias**, `==` and `.equals()` compare identity, and `println` shows `[I@…`. Use `Arrays.equals`/`deepEquals` and `Arrays.toString`/`deepToString`.
- Copy with `clone()`, `Arrays.copyOf`, `Arrays.copyOfRange`, or `System.arraycopy`. **All are shallow**, which matters for 2D arrays and arrays of objects.
- `java.util.Arrays` provides `sort`, `binarySearch` (sorted input only, negative result = `-(insertionPoint) - 1`), `fill`, `asList` (fixed-size, backed by the array, not usable with primitive arrays), and more.
- **2D arrays are arrays of arrays.** Rows are separate objects, can have different lengths (jagged), and are `null` if only the first dimension was given.
- Passing an array to a method copies the **reference**. The method can change the elements but cannot replace the caller's array.
- Reference arrays are **covariant** (`String[]` is an `Object[]`), so stores are checked at runtime (`ArrayStoreException`). Primitive array types are unrelated to each other, and generic arrays cannot be created.

## Related

- [[00 - Syllabus|Syllabus]]
- Previous: [[02 - Loops|Loops]] · Next: [[01 - Methods|Methods]]
- [[02 - Variables and Data Types|Variables and Data Types]]: default values, reference types, `final`, `var`
- [[02 - Strings|Strings]]: `char[]` ↔ `String`, `length()` vs. `length`
- [[Java/05 - Working with Data and Errors/03 - Collections Framework|Collections Framework]]: `ArrayList` as a resizable alternative
- [[DSA/Arrays|DSA: Arrays]] · [[DSA/Binary Search|DSA: Binary Search]] · [[DSA/Sorting Algorithms|DSA: Sorting Algorithms]]
