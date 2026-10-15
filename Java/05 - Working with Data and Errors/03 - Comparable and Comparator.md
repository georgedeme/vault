# Comparable and Comparator in Java

Numbers can be compared with `<`, but objects can't: `"apple" < "pear"` doesn't compile. To sort objects, find a maximum, or keep them in a sorted collection, Java needs to be told what order to use. There are two ways. A class can define its own <span class="hl-blue">natural ordering</span> by implementing `Comparable<T>` and its `compareTo` method. Or any code can supply an external ordering as a `Comparator<T>` object with a `compare` method. This chapter covers both, the contract they must obey (and the subtraction overflow and `double` traps that break it), consistency with `equals` and why sorted sets silently drop "duplicates", building comparators with `comparing`/`thenComparing`/`reversed`/`nullsFirst`, multi-key sorting, stability, and the sorting and searching methods of `Arrays` and `Collections`.

This chapter uses generic interfaces from [[Java/05 - Working with Data and Errors/02 - Generics|Generics]], whose bounds `<T extends Comparable<? super T>>` and `Comparator<? super T>` are explained in [[Java/05 - Working with Data and Errors/02 - Generics#4.3 Recursive Bounds and `Comparable`|Generics § 4.3]] and [[Java/05 - Working with Data and Errors/02 - Generics#6.4 PECS — Producer `extends`, Consumer `super`|§ 6.4]]. Comparators are written as anonymous classes ([[Java/04 - Object-Oriented Programming/08 - Nested and Anonymous Classes|Nested and Anonymous Classes]]) and, in their short form, as lambdas, which are previewed in [[#5.2 Three Ways to Write One|§ 5.2]] and covered fully in [[Java/06 - Functional Programming/01 - Lambdas and Functional Interfaces|Lambdas and Functional Interfaces]]. The sorting **algorithms** themselves (TimSort, quicksort, stability proofs, contest patterns) are in [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms|DSA: Sorting Algorithms]]. Sorted collections (`TreeSet`, `TreeMap`, `PriorityQueue`) are in [[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]].

## Contents

- [[#1. Why Objects Need an Ordering|1. Why Objects Need an Ordering]]
- [[#2. `Comparable` — the Natural Ordering|2. `Comparable` — the Natural Ordering]]
- [[#3. The `compareTo` Contract|3. The `compareTo` Contract]]
- [[#4. Consistency with `equals`|4. Consistency with `equals`]]
- [[#5. `Comparator` — External Orderings|5. `Comparator` — External Orderings]]
- [[#6. Building Comparators from Parts|6. Building Comparators from Parts]]
- [[#7. Multi-Key Sorting|7. Multi-Key Sorting]]
- [[#8. Sorting and Searching Arrays and Lists|8. Sorting and Searching Arrays and Lists]]
- [[#9. Comparable, Inheritance, and Generics|9. Comparable, Inheritance, and Generics]]
- [[#10. Common Pitfalls|10. Common Pitfalls]]
- [[#11. Quick Reference — Non-Obvious Outcomes|11. Quick Reference — Non-Obvious Outcomes]]
- [[#12. Practice — Trick Questions|12. Practice — Trick Questions]]
- [[#13. Summary|13. Summary]]

---

## 1. Why Objects Need an Ordering

The relational operators only work on numbers and `char`s:

```java
String a = "apple", b = "pear";
if (a < b) { … }       // compile error: bad operand types for binary operator '<'
```

And a sorting method can't guess how to order a class it has never seen:

```java
class Student {
    String name;
    Student(String name) { this.name = name; }
}

Student[] two = { new Student("Ada"), new Student("Bob") };
Arrays.sort(two);      // compiles, then throws ClassCastException:
                       // class Student cannot be cast to class java.lang.Comparable
```

`Arrays.sort(Object[])` sorts by natural ordering, so it casts every element to `Comparable` at runtime, and `Student` isn't one. Java offers two fixes:

| | `Comparable<T>` | `Comparator<T>` |
|---|---|---|
| Package | `java.lang` | `java.util` |
| Method | `int compareTo(T other)` | `int compare(T a, T b)` |
| Implemented by | the class **itself** | a **separate** object |
| Number of orderings | **one**: the natural ordering | as many as you like |
| Changes the class? | yes | no: works for classes you can't edit (`String`, library classes) |
| Used by | `Arrays.sort(a)`, `Collections.sort(list)`, `list.sort(null)`, `new TreeSet<>()`, `Collections.max(c)` | `Arrays.sort(a, cmp)`, `list.sort(cmp)`, `new TreeSet<>(cmp)`, `Collections.max(c, cmp)` |
| Typical use | the "obvious" order: numbers by value, dates by time, students by ID | anything else: by name, by GPA descending, by length |

> [!warning] Trick: zero or one element sorts without error
> ```java
> Student[] one = { new Student("Ada") };
> Arrays.sort(one);     // no exception: nothing to compare, so nothing is ever cast
> ```
> The `ClassCastException` only appears once two elements are compared. A test with a one-element array passes, and the bug shows up later. A `TreeSet`, by contrast, checks even the first element: `new TreeSet<Object>().add(new Object())` throws at once, and so does `PriorityQueue`.

---

## 2. `Comparable` — the Natural Ordering

### 2.1 Implementing `compareTo`

```java
public interface Comparable<T> {
    int compareTo(T other);
}
```

> [!important] Key rule: what the result of `compareTo` means
> `a.compareTo(b)` returns:
> - a **negative** number if `a` comes **before** `b`,
> - **zero** if they are **tied** (same position in the order),
> - a **positive** number if `a` comes **after** `b`.
>
> **Only the sign matters.** `-1`, `-2`, and `-1000` all mean "before". Never test `compareTo(…) == -1`; test `< 0`.
>
> A good way to remember it: `a.compareTo(b)` behaves like `a - b`, and `a.compareTo(b) < 0` reads as `a < b`. Just don't **compute** it with `-` ([[#3.2 Don't Subtract|§ 3.2]]).

![[Comparable - The Sign of compareTo.excalidraw|800]]

A `Student` ordered by ID:

```java
public class Student implements Comparable<Student> {
    private final int id;
    private final String name;
    private final double gpa;

    public Student(int id, String name, double gpa) { … }

    @Override
    public int compareTo(Student other) {
        return Integer.compare(this.id, other.id);
    }
}

List<Student> list = new ArrayList<>(List.of(
        new Student(3, "Cleo", 3.2), new Student(1, "Ada", 3.9), new Student(2, "Bob", 3.2)));
Collections.sort(list);           // [Ada(1), Bob(2), Cleo(3)]
Collections.max(list);            // Cleo(3)
```

- Implement the **generic** `Comparable<Student>`, so the parameter is a `Student`. The raw `implements Comparable` would require `compareTo(Object)`, and a `compareTo(Student)` would only be an overload ([[Java/05 - Working with Data and Errors/02 - Generics#2.4 Generic Interfaces|Generics § 2.4]]).
- `Integer.compare(x, y)`, `Long.compare`, `Double.compare`, `Character.compare`, and `Boolean.compare` all return the correct sign for their primitive types. Use them instead of writing `if`s.
- For a field that is itself `Comparable` (a `String`, a `LocalDate`), delegate: `return this.name.compareTo(other.name);`.

### 2.2 Classes That Already Have a Natural Ordering

| Class | Natural ordering | Watch out for |
|---|---|---|
| `Integer`, `Long`, `Short`, `Byte`, `BigInteger` | numeric | |
| `Double`, `Float` | numeric, with `-0.0 < 0.0`, and `NaN` **after** everything, even `+∞` | differs from `<` and `==` ([[#3.3 Comparing `double` Fields|§ 3.3]]) |
| `BigDecimal` | numeric value, ignoring scale | `2.0` and `2.00` compare equal but aren't `equals` ([[#4.2 Sorted Sets and Maps Use `compareTo`, Not `equals`|§ 4.2]]) |
| `String` | lexicographic by UTF-16 code unit | `"Zebra" < "apple"`, `"10" < "9"` ([[#2.3 How Strings Compare|§ 2.3]]) |
| `Character` | by code unit | |
| `Boolean` | `false` before `true` | |
| enums | **declaration order** (`ordinal()`); `compareTo` is `final` | reordering the constants changes the order ([[Java/04 - Object-Oriented Programming/07 - Enums|Enums]]) |
| `LocalDate`, `LocalDateTime`, `Instant`, `Duration` | chronological | |
| `StringBuilder` (Java 11+) | lexicographic, like `String` | its `equals` is identity, so it isn't consistent with `equals` |

Not `Comparable`: `Object`, arrays (`int[]`, `String[]`), `List`, `Map`, records (unless you implement it, [[#9.3 Records and Enums|§ 9.3]]), and most classes you write yourself.

### 2.3 How Strings Compare

`String.compareTo` walks both strings from the start and stops at the first position where the characters differ. It returns the **difference of those two `char` values**. If one string is a prefix of the other, it returns the **difference of the lengths**:

| Call | Result | Why |
|---|---|---|
| `"apple".compareTo("apricot")` | `-2` | first difference at index 2: `'p' - 'r'` = 112 − 114 |
| `"ab".compareTo("abc")` | `-1` | `"ab"` is a prefix: length 2 − 3. Shorter comes first |
| `"b".compareTo("a")` | `1` | `'b' - 'a'` |
| `"Zebra".compareTo("apple")` | `-7` | `'Z'` (90) − `'a'` (97): **all upper-case letters come before all lower-case ones** |
| `"10".compareTo("9")` | `-8` | `'1'` (49) − `'9'` (57): digits are compared as characters, not as numbers |
| `"ä".compareTo("z")` | `106` | `'ä'` is 228: accented and non-Latin letters (including Greek) come after `z` |
| `"Zebra".compareToIgnoreCase("apple")` | `25` | compares as if lower-case: `'z' - 'a'` |

> [!warning] Common mistake: expecting dictionary order
> `String`'s natural ordering is by character code, not the way a dictionary or a phone book sorts:
> - case matters: `["apple", "Banana", "cherry"]` sorts to `[Banana, apple, cherry]`. Use `String.CASE_INSENSITIVE_ORDER` (a ready-made `Comparator<String>`) or `compareToIgnoreCase`.
> - numbers inside strings sort character by character: `["file10", "file9"]` stays in that order. Extract the number and compare it as an `int`.
> - accents and other alphabets sort after `z`, and accented letters land in odd places. In Greek, `["ω", "Β", "ά", "α", "β"]` sorts to `[Β, ά, α, β, ω]`: capitals first, and `ά` (U+03AC) **before** `α` (U+03B1). For language-aware ordering, use a `java.text.Collator`, which is a `Comparator`: `list.sort(Collator.getInstance(Locale.forLanguageTag("el")))` gives `[α, ά, β, Β, ω]`.

### 2.4 Where the Natural Ordering Is Used

Everything below uses `compareTo` when it isn't given a `Comparator`:

- `Arrays.sort(Object[])`, `Collections.sort(List)`, `list.sort(null)`
- `Collections.max`/`min`, `Arrays.binarySearch`, `Collections.binarySearch`
- `TreeSet`, `TreeMap` (for the keys), `PriorityQueue` ([[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]])
- streams: `sorted()`, `max(Comparator.naturalOrder())` ([[Java/06 - Functional Programming/02 - Streams|Streams]])

> [!warning] Trick: `Collections.sort` checks at compile time, `Arrays.sort` at runtime
> ```java
> record P(int x) { }                     // records are not Comparable
>
> Collections.sort(listOfP);              // compile error: no suitable method found for sort(List<P>)
> Arrays.sort(arrayOfP);                  // compiles, ClassCastException at runtime
> listOfP.sort(null);                     // compiles, ClassCastException at runtime
> new TreeSet<P>().add(new P(1));         // compiles, ClassCastException at runtime
> ```
> `Collections.sort` is declared `<T extends Comparable<? super T>> void sort(List<T> list)`, so the bound is checked by the compiler. The other three take any element type and cast to `Comparable` while running.

---

## 3. The `compareTo` Contract

### 3.1 The Rules

The sorting methods and sorted collections **assume** that `compareTo` (and `compare`) behave like a real ordering. The Javadoc states this as a contract, writing `sgn` for the sign (−1, 0, or +1):

> [!important] Key rule: the `compareTo` contract
> 1. **Antisymmetry:** `sgn(a.compareTo(b)) == -sgn(b.compareTo(a))`. If `a` comes before `b`, then `b` comes after `a`. In particular, `a.compareTo(a)` must be `0`.
> 2. **Transitivity:** if `a.compareTo(b) > 0` and `b.compareTo(c) > 0`, then `a.compareTo(c) > 0`.
> 3. **Ties are consistent:** if `a.compareTo(b) == 0`, then `a` and `b` compare the same way with every other `c`.
> 4. **`null`:** `a.compareTo(null)` should throw `NullPointerException`. (Contrast `equals`, where `a.equals(null)` must return `false`.)
> 5. **Recommended, not required:** consistency with `equals` ([[#4. Consistency with `equals`|§ 4]]).
>
> A `Comparator`'s `compare(a, b)` must obey the same rules.

### 3.2 Don't Subtract

The textbook shortcut `return this.age - other.age;` is <span class="hl-red">wrong for large or negative values</span>, because `int` subtraction overflows ([[Java/01 - Foundations/03 - Operators#4. Integer Overflow|Operators § 4]]):

```java
static int bad(int a, int b) { return a - b; }

bad(-2_000_000_000, 2_000_000_000);   //  294967296: positive, so "-2 billion comes after 2 billion"
bad(Integer.MIN_VALUE, 1);            //  2147483647: positive, so "MIN_VALUE comes after 1"
Integer.compare(-2_000_000_000, 2_000_000_000);   // -1: correct
```

Sorting with the subtracting comparator gives a silently wrong order:

```java
Integer[] a = { 3, Integer.MIN_VALUE, 0, -2_000_000_000, 2_000_000_000, 1 };
Arrays.sort(a, (x, y) -> x - y);      // [-2000000000, 0, 1, 3, 2000000000, -2147483648]
Arrays.sort(a, Integer::compare);     // [-2147483648, -2000000000, 0, 1, 3, 2000000000]
```

With small, non-negative values (ages, scores from 0 to 100) subtraction happens to work, which is why the bug survives in so much code. `Integer.compare` costs nothing extra and is always right.

### 3.3 Comparing `double` Fields

<span class="hl-red">Casting a `double` difference to `int` is even worse:</span>

```java
public int compareTo(Student other) {
    return (int) (this.gpa - other.gpa);     // ❌ 3.7 - 3.2 = 0.5, cast to 0: "tied"!
}
```

Every pair of GPAs less than 1.0 apart counts as equal, so the order is wrong and, worse, a `TreeSet` treats such students as duplicates ([[#4.2 Sorted Sets and Maps Use `compareTo`, Not `equals`|§ 4.2]]). Use `Double.compare(this.gpa, other.gpa)`.

`Double.compare` is also different from the operators in two corners ([[Java/01 - Foundations/03 - Operators#7.2 `NaN` and `-0.0`|Operators § 7.2]]), on purpose, so that it defines a proper total order:

| Expression | Operators | `Double.compare` |
|---|---|---|
| `0.0` vs. `-0.0` | `0.0 == -0.0` is `true` | `Double.compare(0.0, -0.0)` is `1`: `-0.0` comes first |
| `NaN` vs. `+∞` | `NaN > Double.POSITIVE_INFINITY` is `false` (every comparison with `NaN` is `false`) | `Double.compare(NaN, +∞)` is `1`: `NaN` comes **last** |
| `NaN` vs. `NaN` | `NaN == NaN` is `false` | `Double.compare(NaN, NaN)` is `0` |

A comparator built from `<` and `>` (`a < b ? -1 : a > b ? 1 : 0`) says `NaN` is tied with every number, which breaks transitivity. `Double.compare` doesn't.

### 3.4 What Breaking the Contract Does

The damage depends on who uses the broken ordering:

- **Sorting** gives a wrong order without any error, or sometimes throws `IllegalArgumentException: Comparison method violates its general contract!`. Whether it throws depends on the input, so small tests often pass ([[DSA/03 - Sorting and Searching/01 - Sorting Algorithms#10.2 Comparator traps|DSA: Sorting § 10.2]]).
- **`TreeSet`/`TreeMap`** lose elements, find elements that aren't there, or fail to find ones that are.
- **`binarySearch`** returns wrong indices.

> [!warning] Common mistake: a comparator that never returns 0
> ```java
> (a, b) -> a < b ? -1 : 1        // compare(x, x) is 1: violates antisymmetry
> ```
> And never sort with a **random** comparator to shuffle a list: it violates every rule. Use `Collections.shuffle(list)`.

---

## 4. Consistency with `equals`

### 4.1 What It Means

An ordering is <span class="hl-blue">consistent with `equals`</span> when `a.compareTo(b) == 0` exactly when `a.equals(b)` is `true`. In other words, "tied in the order" and "equal" mean the same thing. The contract only *recommends* it, but it matters as soon as objects go into sorted collections.

### 4.2 Sorted Sets and Maps Use `compareTo`, Not `equals`

<span class="hl-yellow">A `HashSet` decides "already present" with `equals`/`hashCode`. A `TreeSet` decides it with `compareTo` (or its comparator), and never calls `equals`.</span> When the two disagree, the same elements give different sets:

```java
BigDecimal a = new BigDecimal("2.0"), b = new BigDecimal("2.00");
a.equals(b);                               // false: same value, different scale
a.compareTo(b);                            // 0: numerically equal

new HashSet<>(List.of(a, b)).size();       // 2
new TreeSet<>(List.of(a, b)).size();       // 1: b is a "duplicate" of a

Map<BigDecimal, String> tm = new TreeMap<>();
tm.put(a, "first");
tm.put(b, "second");
System.out.println(tm);                    // {2.0=second}: the KEY 2.0 stays, the value is replaced
```

![[Comparable - HashSet vs TreeSet Duplicates.excalidraw|800]]

The same thing happens with your own classes. A `Student` compared **only by GPA**:

```java
Set<Student> s = new TreeSet<>();
s.add(new Student("Ada", 3.9));     // true
s.add(new Student("Bob", 3.2));     // true
s.add(new Student("Cleo", 3.2));    // false: same GPA as Bob, so "already present"
System.out.println(s);              // [Bob, Ada]: Cleo is gone, with no error
s.contains(new Student("Nobody", 3.9));   // true!
```

Sorting a **list** with the same ordering keeps everyone (`[Bob, Cleo, Ada]`). Only sets and map keys use "tied" to mean "duplicate".

> [!warning] Trick: an inconsistent ordering even makes `equals` between sets asymmetric
> ```java
> Set<String> ts = new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
> ts.addAll(List.of("hello", "HELLO", "World"));     // [hello, World]: "HELLO" was a duplicate
> ts.contains("WORLD");                              // true
>
> Set<String> hs = new HashSet<>(List.of("HELLO", "World"));
> ts.equals(hs);    // true:  ts "contains" HELLO and World, by its comparator
> hs.equals(ts);    // false: hs doesn't contain "hello", by equals
> ```
> `Set.equals` checks sizes and then `containsAll`, and each set uses its own idea of "contains". That breaks the symmetry `equals` is supposed to have ([[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]).

### 4.3 Making the Ordering Consistent

If a sorted collection must keep every distinct object, the ordering must not tie two objects that aren't `equals`. Add **tie-breakers** until it compares every field that `equals` compares:

```java
@Override
public int compareTo(Student other) {
    int r = Double.compare(this.gpa, other.gpa);
    if (r != 0) return r;
    r = this.name.compareTo(other.name);
    if (r != 0) return r;
    return Integer.compare(this.id, other.id);      // id is unique: no two different students tie
}
```

When a ranking is meant to tie (a leaderboard where equal scores share a place), keep it as a `Comparator` used for **sorting lists**, and don't use it for a `TreeSet` or as a `TreeMap` key ordering.

---

## 5. `Comparator` — External Orderings

### 5.1 When to Use a Comparator

```java
@FunctionalInterface
public interface Comparator<T> {
    int compare(T a, T b);           // negative: a first; 0: tie; positive: b first
    // … plus many default and static methods (§ 6)
}
```

Use a `Comparator` when:

- the class has **no** natural ordering, or it isn't yours to change (sorting `String`s by length);
- you need **several** orderings of the same class (students by name, by GPA, by age);
- you need the **reverse** or some variation of the natural ordering.

### 5.2 Three Ways to Write One

The same "by length" ordering, in three forms:

```java
// 1. A named class: reusable, can have fields
class ByLength implements Comparator<String> {
    @Override
    public int compare(String a, String b) {
        return Integer.compare(a.length(), b.length());
    }
}
words.sort(new ByLength());

// 2. An anonymous class: defined right where it's used
words.sort(new Comparator<String>() {
    @Override
    public int compare(String a, String b) {
        return Integer.compare(a.length(), b.length());
    }
});

// 3. A lambda (Java 8+): the same anonymous class, written briefly
words.sort((a, b) -> Integer.compare(a.length(), b.length()));
```

> [!note] Lambda preview
> `Comparator` has a single abstract method, so Java lets you write just its **parameters and body**: `(a, b) -> Integer.compare(a.length(), b.length())`. The compiler knows from the context that this is a `Comparator<String>`, so `a` and `b` are `String`s. A **method reference** such as `String::length` is shorter still: "a function that calls `length()` on its argument". Both are explained in [[Java/06 - Functional Programming/01 - Lambdas and Functional Interfaces|Lambdas and Functional Interfaces]]. The rest of this chapter uses them, because that's how comparators are written in practice. Each one can be read as the anonymous class in form 2.

### 5.3 Where a Comparator Can Be Passed

| Call | Effect |
|---|---|
| `Arrays.sort(array, cmp)` | sorts an **object** array |
| `Arrays.sort(array, from, to, cmp)` | sorts the range `[from, to)` |
| `list.sort(cmp)` / `Collections.sort(list, cmp)` | sorts a list in place |
| `list.sort(null)` | natural ordering |
| `new TreeSet<>(cmp)`, `new TreeMap<>(cmp)` | a sorted set / map ordered by `cmp` |
| `new PriorityQueue<>(cmp)` | a heap ordered by `cmp` |
| `Collections.max(coll, cmp)`, `Collections.min(coll, cmp)` | the extreme element |
| `Arrays.binarySearch(array, key, cmp)` | search an array **sorted by `cmp`** ([[#8.4 Binary Search Needs the Same Ordering|§ 8.4]]) |
| `stream.sorted(cmp)`, `stream.max(cmp)` | in streams ([[Java/06 - Functional Programming/02 - Streams|Streams]]) |

> [!warning] Trick: no comparator for primitive arrays
> ```java
> int[] a = { 3, 1, 2 };
> Arrays.sort(a, Collections.reverseOrder());   // compile error: no suitable method found for sort(int[], …)
> ```
> A comparator compares objects, and `T` can't be `int` ([[Java/05 - Working with Data and Errors/02 - Generics#3.1 Declaring and Calling|Generics § 3.1]]). Sort ascending and reverse in place, or use an `Integer[]` ([[DSA/03 - Sorting and Searching/01 - Sorting Algorithms#9. Sorting in Java|DSA: Sorting § 9]]).

---

## 6. Building Comparators from Parts

Since Java 8, `Comparator` has static factory methods and default methods that build comparators from small pieces. They are far less error-prone than hand-written `compare` methods.

### 6.1 `comparing` and Key Extractors

`Comparator.comparing(keyExtractor)` takes a function that pulls a **sort key** out of each object, and compares the keys by their natural ordering:

```java
record Person(String name, int age) { }

Comparator<Person> byName = Comparator.comparing(Person::name);        // key: the name (a String)
Comparator<Person> byAge  = Comparator.comparingInt(Person::age);      // key: an int, no boxing
Comparator<String> byLen  = Comparator.comparing(String::length);      // key: the length

people.sort(byName);
```

- `comparingInt`, `comparingLong`, `comparingDouble` take primitive keys. They avoid boxing and are the right choice for numeric fields.
- `comparing(keyExtractor, keyComparator)` compares the keys with a given comparator instead of their natural ordering: `comparing(Person::name, String.CASE_INSENSITIVE_ORDER)`.

### 6.2 `thenComparing` — Tie-Breakers

`c1.thenComparing(c2)` uses `c2` only for pairs that `c1` considers tied:

```java
Comparator<Student> order = Comparator.comparingDouble(Student::gpa).reversed()   // best GPA first
        .thenComparingInt(Student::grade)                                         // then lower grade
        .thenComparing(Student::name);                                            // then by name
```

`thenComparing` accepts a key extractor (`thenComparing(Student::name)`), a key extractor plus a key comparator (`thenComparing(Student::name, Comparator.reverseOrder())`), or a whole comparator (`thenComparing(otherComparator)`). There are `thenComparingInt`/`Long`/`Double` versions too.

### 6.3 `reversed` and `reverseOrder`

| Expression | Meaning |
|---|---|
| `Comparator.naturalOrder()` | the natural ordering, as a `Comparator` |
| `Comparator.reverseOrder()` / `Collections.reverseOrder()` | the natural ordering, reversed |
| `Collections.reverseOrder(cmp)` / `cmp.reversed()` | `cmp`, reversed |

> [!warning] Trick: `reversed()` reverses the whole chain built so far
> `reversed()` is a method called on a comparator, so it reverses **everything to its left**. With the words `[bb, a, ccc, ab, b]`:
>
> | Comparator | Result |
> |---|---|
> | `comparing(String::length).thenComparing(naturalOrder())` | `[a, b, ab, bb, ccc]` |
> | `comparing(String::length).thenComparing(naturalOrder()).reversed()` | `[ccc, bb, ab, b, a]`: **both** keys reversed |
> | `comparing(String::length).reversed().thenComparing(naturalOrder())` | `[ccc, ab, bb, a, b]`: only the length reversed |
> | `comparing(String::length, reverseOrder()).thenComparing(naturalOrder())` | `[ccc, ab, bb, a, b]`: the same, written per key |
>
> To reverse one key in the middle of a chain, give that key its own comparator: `thenComparing(key, Comparator.reverseOrder())`.

![[Comparator - Where reversed Applies.excalidraw|800]]

> [!warning] Trick: a lambda key plus `reversed()` doesn't compile
> ```java
> words.sort(Comparator.comparing(s -> s.length()));                 // OK
> words.sort(Comparator.comparing(s -> s.length()).reversed());      // compile error: cannot find symbol
>                                                                    //   method length(), location: variable s of type Object
> words.sort(Comparator.comparing(String::length).reversed());       // OK
> words.sort(Comparator.comparing((String s) -> s.length()).reversed());   // OK
> ```
> In the second line, `comparing(…)` is no longer the argument of `sort`; it's the receiver of `.reversed()`. Java infers a lambda's parameter types from the **target**, and a receiver has no target, so `s` falls back to `Object`. A method reference or an explicitly typed parameter fixes it. The same happens with `.thenComparing(…)` chains.

### 6.4 `null` Elements and `null` Keys

Natural ordering throws `NullPointerException` on `null` (contract rule 4):

```java
Collections.sort(Arrays.asList("b", null, "a"));                         // NullPointerException

List<String> withNull = Arrays.asList("b", null, "a");
withNull.sort(Comparator.nullsFirst(Comparator.naturalOrder()));         // [null, a, b]
withNull.sort(Comparator.nullsLast(Comparator.reverseOrder()));          // [b, a, null]
```

`nullsFirst(cmp)` and `nullsLast(cmp)` wrap a comparator: they handle `null` **elements** themselves and pass non-`null` pairs to `cmp`.

> [!warning] Trick: `nullsFirst` around `comparing` doesn't protect against `null` keys
> ```java
> people.add(new Person(null, 25));
>
> people.sort(Comparator.comparing(Person::name));                          // NPE: compares a null name
> people.sort(Comparator.nullsFirst(Comparator.comparing(Person::name)));   // still NPE!
> people.sort(Comparator.comparing(Person::name,
>                                  Comparator.nullsFirst(Comparator.naturalOrder())));   // OK
> ```
> The second version only handles a `null` **`Person`**. Here the person exists and its **name** is `null`. The `null`-handling comparator has to go where the keys are compared: as the second argument of `comparing`.

### 6.5 The Method Table

| Method | Kind | Result |
|---|---|---|
| `Comparator.comparing(f)` | static | compare `f(x)` by natural ordering |
| `Comparator.comparing(f, cmp)` | static | compare `f(x)` with `cmp` |
| `comparingInt(f)` / `comparingLong` / `comparingDouble` | static | compare a primitive key, no boxing |
| `Comparator.naturalOrder()` / `reverseOrder()` | static | natural ordering / its reverse |
| `Comparator.nullsFirst(cmp)` / `nullsLast(cmp)` | static | `null` elements first / last, others by `cmp` |
| `cmp.reversed()` | default | `cmp` backwards (the whole chain so far) |
| `cmp.thenComparing(f)` / `(f, keyCmp)` / `(cmp2)` | default | tie-breaker |
| `thenComparingInt(f)` / `Long` / `Double` | default | primitive tie-breaker |
| `String.CASE_INSENSITIVE_ORDER` | constant | strings ignoring case |
| `Map.Entry.comparingByKey()` / `comparingByValue()` | static | for sorting map entries ([[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]]) |

---

## 7. Multi-Key Sorting

Example: sort students by GPA **descending**, then by grade **ascending**, then by name.

### 7.1 By Hand

Compare the first key, and return its result unless it's a tie. Then do the same with the next key:

```java
Comparator<Student> manual = new Comparator<>() {
    @Override
    public int compare(Student a, Student b) {
        int r = Double.compare(b.gpa(), a.gpa());          // b before a: DESCENDING
        if (r != 0) return r;
        r = Integer.compare(a.grade(), b.grade());
        if (r != 0) return r;
        return a.name().compareTo(b.name());
    }
};
```

Swapping the arguments (`compare(b, a)`) is the cleanest way to reverse one key by hand. Writing `-Double.compare(a, b)` also works for the `compare` methods, which only return −1, 0, or 1, but negating an arbitrary `compareTo` result is a bad habit: `-Integer.MIN_VALUE` is still negative.

### 7.2 With a Comparator Chain

```java
Comparator<Student> chain = Comparator.comparingDouble(Student::gpa).reversed()
        .thenComparingInt(Student::grade)
        .thenComparing(Student::name);
```

Both give the same order:

```
Student[name=Ada,  grade=1, gpa=3.9]
Student[name=Dan,  grade=1, gpa=3.9]
Student[name=Bob,  grade=2, gpa=3.9]
Student[name=Cleo, grade=2, gpa=3.5]
Student[name=Eve,  grade=2, gpa=3.5]
```

Note that `.reversed()` comes **right after the first key**, before any `thenComparing`, so it reverses only the GPA ([[#6.3 `reversed` and `reverseOrder`|§ 6.3]]).

### 7.3 Through a Stable Sort

A sort is <span class="hl-blue">stable</span> if elements that compare as tied keep their original relative order. Java's object sorts (`Arrays.sort(Object[])`, `Collections.sort`, `List.sort`) are guaranteed stable. That allows sorting by several keys in several passes, **least important key first**:

```java
record S(String name, int grade) { }

list = [Ada2, Bob1, Cleo2, Dan1];
list.sort(Comparator.comparing(S::name));        // [Ada2, Bob1, Cleo2, Dan1]   (by name)
list.sort(Comparator.comparingInt(S::grade));    // [Bob1, Dan1, Ada2, Cleo2]   (by grade; names stay in order)
```

The second sort only looks at the grade, and among equal grades it keeps the order the first sort produced. This is how spreadsheets sort when you click one column header after another. In code, a single comparator chain ([[#7.2 With a Comparator Chain|§ 7.2]]) is clearer and faster.

![[Comparator - Multi-Key Sort with a Stable Sort.excalidraw|800]]

---

## 8. Sorting and Searching Arrays and Lists

### 8.1 The Sorting Methods

| Method | Sorts | Ordering | Stable |
|---|---|---|---|
| `Arrays.sort(int[] a)` (all primitives) | primitive array | numeric | n/a: equal primitives are indistinguishable |
| `Arrays.sort(a, from, to)` | the range `[from, to)` — `to` is **exclusive** | numeric / natural | |
| `Arrays.sort(Object[] a)` | object array | natural (`Comparable`) | ✅ |
| `Arrays.sort(T[] a, cmp)` / `(a, from, to, cmp)` | object array / range | `cmp` | ✅ |
| `Collections.sort(list)` / `list.sort(null)` | list | natural | ✅ |
| `Collections.sort(list, cmp)` / `list.sort(cmp)` | list | `cmp` | ✅ |
| `Arrays.parallelSort(a)` | large arrays, using several threads | natural | ✅ for objects |

`Collections.sort(list, cmp)` simply calls `list.sort(cmp)`. Prefer `list.sort(cmp)`. The algorithms behind these methods (dual-pivot quicksort for primitives, TimSort for objects) and their complexities are in [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms#9. Sorting in Java|DSA: Sorting § 9]].

```java
int[] a = { 5, 4, 3, 2, 1 };
Arrays.sort(a, 1, 4);                                  // [5, 2, 3, 4, 1]: only indices 1, 2, 3
Integer[] b = { 5, 4, 3, 2, 1 };
Arrays.sort(b, 0, 3, Comparator.reverseOrder());       // [5, 4, 3, 2, 1]: indices 0..2 already descending
```

### 8.2 Stability — and What Isn't Stable

- Object sorts are stable ([[#7.3 Through a Stable Sort|§ 7.3]]).
- A **`PriorityQueue`** is not: among tied elements, the order they come out in is unspecified. Adding `Dan2, Ada1, Cleo2, Bob1, Eve1` to a `PriorityQueue` ordered by grade and polling everything gives `Ada1, Eve1, Bob1, Cleo2, Dan2`: Eve overtook Bob although Bob was added first. If ties must come out in insertion order, add a tie-breaker such as a sequence number.
- A **`TreeSet`** doesn't keep ties at all ([[#4.2 Sorted Sets and Maps Use `compareTo`, Not `equals`|§ 4.2]]).

### 8.3 What Can't Be Sorted

| Attempt | Result |
|---|---|
| `List.of(3, 1, 2).sort(null)` | `UnsupportedOperationException`, **even when already sorted** (`List.of(1, 2, 3).sort(null)` throws too) |
| `Collections.unmodifiableList(list).sort(null)` | `UnsupportedOperationException` |
| `Arrays.asList(3, 1, 2)` then `Collections.sort` | ✅ works: a fixed-size list allows `set`, which is all sorting needs ([[Java/02 - Control Flow/03 - Arrays#8.4 `asList`|Arrays § 8.4]]) |
| a list or array containing `null`, natural ordering | `NullPointerException` ([[#6.4 `null` Elements and `null` Keys|§ 6.4]]) |
| elements that aren't `Comparable`, no comparator | `ClassCastException` (or a compile error with `Collections.sort`, [[#2.4 Where the Natural Ordering Is Used|§ 2.4]]) |
| mixed types, e.g. `Object[] { 1, "a" }` | `ClassCastException`: `Integer` can't be compared with `String` |
| `int[]` with a comparator | compile error ([[#5.3 Where a Comparator Can Be Passed|§ 5.3]]) |

### 8.4 Binary Search Needs the Same Ordering

`Arrays.binarySearch` and `Collections.binarySearch` assume the data is **sorted by the ordering they use**. If it isn't, the result is undefined: often a wrong "not found".

```java
String[] a = { "pear", "fig", "banana", "kiwi", "apple" };
Comparator<String> byLen = Comparator.comparing(String::length);
Arrays.sort(a, byLen);                       // [fig, pear, kiwi, apple, banana]

Arrays.binarySearch(a, "banana");            // -1: searched by NATURAL ordering → "not found", but it's at index 4
Arrays.binarySearch(a, "banana", byLen);     // 4: same comparator as the sort
Arrays.binarySearch(a, "plum", byLen);       // 2: "plum" has length 4, and so does "kiwi": a TIE counts as found
```

The last line is a second trap: with a comparator, "found" means "**compares as 0**", not "equals". `"plum"` isn't in the array, but `"kiwi"` ties with it.

When the key is not found, the result is `-(insertionPoint) - 1`, where the insertion point is the index where the key would go: with `[apple, banana, fig, kiwi, pear]`, `binarySearch(a, "cherry")` is `-3` (insertion point 2). Binary search itself is in [[DSA/03 - Sorting and Searching/02 - Binary Search|DSA: Binary Search]].

---

## 9. Comparable, Inheritance, and Generics

### 9.1 A Subclass Can't Re-implement `Comparable`

```java
class Animal implements Comparable<Animal> {
    int weight;
    public int compareTo(Animal o) { return Integer.compare(weight, o.weight); }
}

class Dog extends Animal implements Comparable<Dog> { … }
// compile error: Comparable cannot be inherited with different arguments: <Dog> and <Animal>
```

A class can't implement the same generic interface twice with different type arguments: after erasure both would be the same `Comparable` ([[Java/05 - Working with Data and Errors/02 - Generics#7.1 What the Compiler Does|Generics § 7.1]]). A `Dog` *is* a `Comparable<Animal>`, and that's its natural ordering. A different ordering for dogs has to be a `Comparator<Dog>`.

> [!info]- Why `equals` with subclasses has a similar problem
> If `Dog` added a field and wanted it in the ordering, `compareTo(Animal)` would have to compare a `Dog` with a plain `Animal`, and there's no way to do that consistently in both directions. This is the same symmetry problem `equals` has with subclasses ([[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]). The usual answers are the same: compose instead of extending ([[Java/04 - Object-Oriented Programming/03 - Inheritance#12.3 Composition over Inheritance|Inheritance § 12.3]]), or make the class `final`.

### 9.2 `Comparable<? super T>` and `Comparator<? super T>`

Because `Dog` is a `Comparable<Animal>` and not a `Comparable<Dog>`, the library signatures use `? super`:

```java
static <T extends Comparable<? super T>> void sort(List<T> list)    // Collections.sort
void sort(Comparator<? super E> c)                                  // List.sort
```

So both of these compile and work:

```java
List<Dog> dogs = new ArrayList<>(List.of(new Dog(30), new Dog(10), new Dog(20)));
Collections.sort(dogs);                                     // [Dog10, Dog20, Dog30]: uses compareTo(Animal)
Comparator<Animal> byWeightDesc = (x, y) -> Integer.compare(y.weight, x.weight);
dogs.sort(byWeightDesc);                                    // [Dog30, Dog20, Dog10]: a Comparator<Animal> sorts dogs
```

The reasoning (a comparator **consumes** elements, so PECS says `super`) is in [[Java/05 - Working with Data and Errors/02 - Generics#4.3 Recursive Bounds and `Comparable`|Generics § 4.3]] and [[Java/05 - Working with Data and Errors/02 - Generics#6.4 PECS — Producer `extends`, Consumer `super`|§ 6.4]].

### 9.3 Records and Enums

**Records** get `equals`, `hashCode`, and `toString` generated, but **not** `compareTo`. To give one a natural ordering, implement `Comparable` and, conveniently, delegate to a comparator chain kept in a `static` field:

```java
record Version(int major, int minor) implements Comparable<Version> {
    private static final Comparator<Version> ORDER =
            Comparator.comparingInt(Version::major).thenComparingInt(Version::minor);

    @Override
    public int compareTo(Version other) { return ORDER.compare(this, other); }
}

// [1.10, 1.2, 0.9] sorts to [0.9, 1.2, 1.10]: compared as numbers, not as strings
```

This ordering is consistent with `equals`: the record's `equals` compares `major` and `minor`, and so does `compareTo`.

**Enums** are `Comparable` by **declaration order**, and `compareTo` is `final`: an enum can't override it (*overridden method is final*). For another order, use a `Comparator` ([[Java/04 - Object-Oriented Programming/07 - Enums|Enums]]).

```java
enum Size { SMALL, MEDIUM, LARGE }
Size.SMALL.compareTo(Size.LARGE);     // -2 (ordinal 0 - ordinal 2)
```

---

## 10. Common Pitfalls

- **Comparing objects with `<`**, or sorting a class that implements neither `Comparable` nor gets a `Comparator` (`ClassCastException`, which a one-element test never shows).
- **Testing `compareTo(…) == -1` or `== 1`.** Only the sign is guaranteed.
- **`return a - b;`** in `compareTo`/`compare`: overflows for large or negative values. Use `Integer.compare`.
- **`(int) (a - b)` for `double`s**: differences below 1 become ties. Use `Double.compare`.
- **A comparator that never returns 0**, or a random comparator for shuffling.
- **An ordering inconsistent with `equals`** used for a `TreeSet`/`TreeMap`: "duplicates" vanish silently, and `contains` finds objects that aren't there.
- **Expecting a `TreeSet` to use `equals`.** It only uses `compareTo`/the comparator.
- **Implementing the raw `Comparable`** (then `compareTo(Student)` is only an overload).
- **Trying to give a subclass its own `Comparable<Sub>`**: a compile error. Use a `Comparator`.
- **Expecting `String` to sort like a dictionary**: upper case first, digits as characters, accents after `z`.
- **Placing `.reversed()` at the end of a chain** when only the first key should be reversed.
- **`comparing(s -> s.length()).reversed()`**: doesn't compile. Use `String::length`.
- **Wrapping `comparing(…)` in `nullsFirst`** to handle `null` keys. It only handles `null` elements.
- **Sorting a list with `null`s** by natural ordering (`NullPointerException`).
- **Sorting `List.of(…)`** (`UnsupportedOperationException`, even if already sorted).
- **Passing a comparator with an `int[]`.**
- **`binarySearch` with a different ordering** from the one used to sort, or forgetting that with a comparator "found" means "ties".
- **Mutating a field used by `compareTo`** while the object is in a `TreeSet`/`TreeMap` ([[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]]).
- **Expecting a `PriorityQueue` to keep ties in insertion order.**
- **Relying on enum `ordinal` order** when the constants may be reordered.

---

## 11. Quick Reference — Non-Obvious Outcomes

| Code | Result | Why |
|---|---|---|
| `"a" < "b"` | compile error | `<` only works on numbers and `char`s |
| `Arrays.sort` on 2+ non-`Comparable` objects | `ClassCastException` | natural ordering casts to `Comparable` |
| …on 1 non-`Comparable` object | no exception | nothing is compared |
| `new TreeSet<Object>().add(new Object())` | `ClassCastException` | `TreeSet` checks even the first element |
| `Collections.sort(listOfRecords)` | compile error | bound `T extends Comparable<? super T>` |
| `Arrays.sort(arrayOfRecords)` | `ClassCastException` at runtime | no compile-time bound |
| `"apple".compareTo("apricot")` | `-2` | `'p' - 'r'` |
| `"ab".compareTo("abc")` | `-1` | prefix: length difference |
| `"Zebra".compareTo("apple")` | `-7` (negative) | upper case before lower case |
| `"10".compareTo("9")` | `-8` (negative) | characters, not numbers |
| `"ä".compareTo("z")` | `106` (positive) | accented letters after `z` |
| `["ω", "Β", "ά", "α", "β"]` sorted naturally | `[Β, ά, α, β, ω]` | code order: `ά` (U+03AC) before `α` (U+03B1); use a `Collator` |
| `Boolean.FALSE.compareTo(true)` | `-1` | `false` first |
| `bad(-2_000_000_000, 2_000_000_000)` with `a - b` | `294967296` (positive) | overflow |
| `bad(Integer.MIN_VALUE, 1)` with `a - b` | `2147483647` (positive) | overflow |
| `(int) (3.7 - 3.2)` | `0` | cast truncates: a false tie |
| `Double.compare(0.0, -0.0)` | `1` | `-0.0` first, although `0.0 == -0.0` |
| `Double.compare(NaN, POSITIVE_INFINITY)` | `1` | `NaN` last |
| `"a".compareTo(null)` | `NullPointerException` | unlike `"a".equals(null)` → `false` |
| `new BigDecimal("2.0").equals(new BigDecimal("2.00"))` | `false` | scale differs |
| …`.compareTo(…)` | `0` | same value |
| `HashSet` / `TreeSet` of `2.0` and `2.00` | size 2 / size 1 | `equals` vs. `compareTo` |
| `TreeMap`: `put(2.0, "first")`, `put(2.00, "second")` | `{2.0=second}` | key kept, value replaced |
| `TreeSet` by GPA only, two students with GPA 3.2 | second `add` returns `false` | a tie means "duplicate" |
| `TreeSet(CASE_INSENSITIVE_ORDER)` `{hello, World}` vs. `HashSet {HELLO, World}` | `ts.equals(hs)` `true`, `hs.equals(ts)` `false` | each uses its own "contains" |
| `class Dog extends Animal implements Comparable<Dog>` (Animal is `Comparable<Animal>`) | compile error | inherited with different arguments |
| `dogs.sort(comparatorOfAnimal)` | compiles | `Comparator<? super E>` |
| `comparing(s -> s.length()).reversed()` | compile error | lambda parameter inferred as `Object` |
| `comparing(len).thenComparing(alpha).reversed()` | both keys reversed | `reversed` applies to the whole chain |
| `nullsFirst(comparing(Person::name))` with a `null` name | `NullPointerException` | handles `null` persons, not `null` names |
| `Collections.sort(Arrays.asList("b", null, "a"))` | `NullPointerException` | natural ordering and `null` |
| `List.of(1, 2, 3).sort(null)` | `UnsupportedOperationException` | immutable, even if sorted |
| `Collections.sort(Arrays.asList(3, 1, 2))` | `[1, 2, 3]` | fixed size, but `set` works |
| `Arrays.sort(intArray, cmp)` | compile error | no comparators for primitives |
| `Arrays.sort(a, 1, 4)` on `[5, 4, 3, 2, 1]` | `[5, 2, 3, 4, 1]` | `to` is exclusive |
| `binarySearch` with the natural ordering on a by-length-sorted array | wrong answer (e.g. `-1`) | data not sorted by that ordering |
| `binarySearch(a, "plum", byLen)` where `"kiwi"` is present | index of `"kiwi"` | "found" means "compares as 0" |
| enum overriding `compareTo` | compile error | `Enum.compareTo` is `final` |
| `Size.SMALL.compareTo(Size.LARGE)` | `-2` | ordinal difference |
| `PriorityQueue` with ties | not in insertion order | heaps aren't stable |

---

## 12. Practice — Trick Questions

**Q1.** What does each line print (sign only, where the exact value doesn't matter)?

```java
System.out.println("Apple".compareTo("apple"));
System.out.println("apple".compareTo("app"));
System.out.println("100".compareTo("20"));
System.out.println(Integer.valueOf(100).compareTo(20));
System.out.println(Boolean.TRUE.compareTo(false));
```

> [!success]- Answer
> | Call | Result | Reason |
> |---|---|---|
> | `"Apple".compareTo("apple")` | negative (`-32`) | `'A'` (65) − `'a'` (97) |
> | `"apple".compareTo("app")` | positive (`2`) | `"app"` is a prefix: length 5 − 3 |
> | `"100".compareTo("20")` | negative (`-1`) | `'1'` − `'2'`: compared as text |
> | `Integer.valueOf(100).compareTo(20)` | positive (`1`) | compared as numbers |
> | `Boolean.TRUE.compareTo(false)` | positive (`1`) | `false` comes first |

**Q2.** What is wrong with each `compareTo`? `age` is an `int`, `gpa` a `double`.

```java
public int compareTo(Student o) { return age - o.age; }                    // (a)
public int compareTo(Student o) { return (int) (gpa - o.gpa); }            // (b)
public int compareTo(Student o) { return age < o.age ? -1 : 1; }           // (c)
public int compareTo(Student o) { return gpa > o.gpa ? 1 : gpa < o.gpa ? -1 : 0; }   // (d)
```

> [!success]- Answer
> - (a) Overflows when the difference doesn't fit in an `int` (only possible with large or negative values; with real ages it happens to work). Use `Integer.compare(age, o.age)`.
> - (b) Truncates: any two GPAs less than 1.0 apart are "tied". A `TreeSet` would drop students. Use `Double.compare(gpa, o.gpa)`.
> - (c) Never returns 0: `s.compareTo(s)` is `1`, and two students with the same age each come "after" the other. This breaks antisymmetry, and sorting may throw *Comparison method violates its general contract!*
> - (d) Correct for ordinary numbers, but `NaN` compares as tied with everything, which breaks transitivity, and `-0.0` ties with `0.0`. `Double.compare` handles both.

**Q3.** What is printed?

```java
record Student(String name, double gpa) implements Comparable<Student> {
    public int compareTo(Student o) { return Double.compare(gpa, o.gpa); }
}

Set<Student> tree = new TreeSet<>();
Set<Student> hash = new HashSet<>();
for (Student s : List.of(new Student("Ada", 3.9), new Student("Bob", 3.2), new Student("Cleo", 3.2))) {
    tree.add(s);
    hash.add(s);
}
System.out.println(tree.size() + " " + hash.size());
System.out.println(tree.contains(new Student("Nobody", 3.2)));
System.out.println(hash.contains(new Student("Nobody", 3.2)));
```

> [!success]- Answer
> ```
> 2 3
> true
> false
> ```
> The `TreeSet` uses `compareTo`: Cleo ties with Bob (same GPA), so she's treated as a duplicate and not added, and "Nobody" with GPA 3.2 is "found". The `HashSet` uses the record's generated `equals`/`hashCode`, which compare both fields, so all three students are kept and "Nobody" isn't found.

**Q4.** Each line sorts `[bb, a, ccc, ab, b]`. What is the result?

```java
(1) comparing(String::length)
(2) comparing(String::length).reversed()
(3) comparing(String::length).thenComparing(naturalOrder())
(4) comparing(String::length).thenComparing(naturalOrder()).reversed()
(5) comparing(String::length).reversed().thenComparing(naturalOrder())
(6) Comparator.<String>naturalOrder().reversed()
```

> [!success]- Answer
> | | Result | Note |
> |---|---|---|
> | (1) | `[a, b, bb, ab, ccc]` | ties (`a`/`b`, `bb`/`ab`) keep their original order: the sort is stable |
> | (2) | `[ccc, bb, ab, a, b]` | ties still in original relative order |
> | (3) | `[a, b, ab, bb, ccc]` | |
> | (4) | `[ccc, bb, ab, b, a]` | both keys reversed |
> | (5) | `[ccc, ab, bb, a, b]` | only the length reversed |
> | (6) | `[ccc, bb, b, ab, a]` | reverse alphabetical |
>
> (1) and (2) depend on stability: `List.sort` keeps tied elements in the order they had before the sort.

**Q5.** Which lines compile?

```java
List<String> w = new ArrayList<>(List.of("bb", "a"));
w.sort(Comparator.comparing(s -> s.length()));                     // (1)
w.sort(Comparator.comparing(s -> s.length()).reversed());          // (2)
w.sort(Comparator.comparing(String::length).reversed());           // (3)
w.sort(Comparator.comparing((String s) -> s.length()).reversed()); // (4)
int[] a = { 2, 1 };
Arrays.sort(a, Comparator.reverseOrder());                         // (5)
Integer[] b = { 2, 1 };
Arrays.sort(b, Comparator.reverseOrder());                         // (6)
```

> [!success]- Answer
> | Line | Compiles? | Reason |
> |---|---|---|
> | (1) | ✅ | `sort`'s parameter type gives the lambda its target: `s` is a `String` |
> | (2) | ❌ | `comparing(…)` is now the receiver of `.reversed()`: no target, so `s` is an `Object` and has no `length()` |
> | (3) | ✅ | the method reference fixes the type |
> | (4) | ✅ | explicitly typed parameter |
> | (5) | ❌ | no `sort(int[], Comparator)`: comparators need objects |
> | (6) | ✅ | `[2, 1]` |

**Q6.** What is printed?

```java
String[] a = { "pear", "fig", "banana", "kiwi", "apple" };
Comparator<String> byLen = Comparator.comparing(String::length);
Arrays.sort(a, byLen);
System.out.println(Arrays.toString(a));
System.out.println(Arrays.binarySearch(a, "banana"));
System.out.println(Arrays.binarySearch(a, "banana", byLen));
System.out.println(Arrays.binarySearch(a, "plum", byLen));
```

> [!success]- Answer
> ```
> [fig, pear, kiwi, apple, banana]
> -1
> 4
> 2
> ```
> Stable sort by length: `pear` stays before `kiwi`. Searching with the natural ordering on data that isn't sorted that way gives a wrong "not found". With the right comparator, `"banana"` is found. `"plum"` isn't in the array, but it has length 4 and ties with `"kiwi"`, so `binarySearch` reports index 2.

**Q7.** Which compile, and what happens at runtime?

```java
record P(int x) { }
List<P> list = new ArrayList<>(List.of(new P(2), new P(1)));
P[] arr = { new P(2), new P(1) };

Collections.sort(list);                     // (1)
list.sort(null);                            // (2)
Arrays.sort(arr);                           // (3)
list.sort(Comparator.comparingInt(P::x));   // (4)
new TreeSet<P>().add(new P(1));             // (5)
```

> [!success]- Answer
> | Line | Result |
> |---|---|
> | (1) | **compile error**: `P` is not `Comparable`, and `Collections.sort` requires `T extends Comparable<? super T>` |
> | (2) | compiles, **`ClassCastException`** at runtime |
> | (3) | compiles, **`ClassCastException`** at runtime |
> | (4) | compiles, sorts to `[P[x=1], P[x=2]]` |
> | (5) | compiles, **`ClassCastException`** on the very first `add` |

**Q8.** Find the bug and fix it. The list contains a person whose name is `null`.

```java
people.sort(Comparator.nullsLast(Comparator.comparing(Person::name)));
```

> [!success]- Answer
> `nullsLast` only handles `null` **elements** (a `null` `Person`). The persons are all there; one of them has a `null` **name**, and `comparing` compares names with `String.compareTo`, which throws `NullPointerException`. Put the `null` handling on the key:
> ```java
> people.sort(Comparator.comparing(Person::name, Comparator.nullsLast(Comparator.naturalOrder())));
> ```

**Q9.** What is printed?

```java
TreeMap<String, Integer> m = new TreeMap<>(String.CASE_INSENSITIVE_ORDER);
m.put("Apple", 1);
m.put("APPLE", 2);
m.put("banana", 3);
System.out.println(m + " " + m.get("aPPle"));
```

> [!success]- Answer
> `{Apple=2, banana=3} 2`. With a case-insensitive comparator, `"APPLE"` is the same key as `"Apple"`: `put` replaces the **value** but keeps the **original key** object `"Apple"`. `get("aPPle")` finds it too.

**Q10.** Sort students by grade ascending, then by name, using only two sorts by a single key each. In which order must the two sorts be done, and why does it work?

> [!success]- Answer
> First by **name** (the secondary key), then by **grade** (the primary key). The second sort decides the main order, and because Java's object sorts are **stable**, students with the same grade keep the name order from the first sort. Doing them the other way round would leave the list sorted by name only.

**Q11.** Why doesn't this compile, and what should be done instead?

```java
class Animal implements Comparable<Animal> { … }
class Dog extends Animal implements Comparable<Dog> {
    public int compareTo(Dog other) { … }
}
```

> [!success]- Answer
> *Comparable cannot be inherited with different arguments: <Dog> and <Animal>.* `Dog` already implements `Comparable<Animal>` through `Animal`, and a class can't implement the same generic interface with two different type arguments (they'd erase to the same interface). Dogs keep `Animal`'s natural ordering. Any other ordering for dogs is a `Comparator<Dog>`.

**Q12.** A `TreeSet<Box>` orders boxes by `size`. After adding `Box(1)`, `Box(5)`, and `Box(9)`, the program sets the first box's `size` to `10`. What do `set.contains(b1)` and `set.remove(b1)` return, and what does printing the set show?

> [!success]- Answer
> `contains` and `remove` both return **`false`**, and the set prints `[Box10, Box5, Box9]`, out of order. The tree placed `b1` at the far left when its size was 1. A search for size 10 now goes right from the root and never looks there. The object is still in the set but can't be found or removed. Never change a field used by `compareTo` (or by `hashCode`/`equals`, for hash sets) while the object is inside a collection.

---

## 13. Summary

- Objects are ordered by **`Comparable<T>`** (`compareTo`, the class's single **natural ordering**) or by a **`Comparator<T>`** (`compare`, any number of external orderings).
- The result's **sign** is what counts: negative means "before", zero "tied", positive "after". Compute it with `Integer.compare`, `Double.compare`, or a field's own `compareTo`, **never by subtracting** (overflow) or casting a `double` difference (false ties).
- The contract requires antisymmetry, transitivity, and consistent ties, and `compareTo(null)` throws. Breaking it gives wrong orders, sorting exceptions, and broken sorted collections.
- `String` compares by character code: upper case before lower case, digits as characters, accents after `z`.
- **`TreeSet`/`TreeMap` use `compareTo`, not `equals`.** An ordering that ties non-equal objects makes them drop "duplicates" silently. Add tie-breakers to keep it consistent with `equals`.
- Build comparators with **`comparing`/`comparingInt`**, **`thenComparing`**, **`reversed`** (which reverses the whole chain so far), **`reverseOrder`**, and **`nullsFirst`/`nullsLast`** (which handle `null` elements, not `null` keys).
- Multi-key sorts: one comparator chain, or several **stable** sorts from the least important key to the most important.
- Object sorts are stable; `PriorityQueue` is not. `List.of(…)` can't be sorted. Comparators don't work on primitive arrays. `binarySearch` needs data sorted by the same ordering.
- A subclass can't implement `Comparable` again with its own type; library methods accept `Comparable<? super T>` and `Comparator<? super T>`. Records need `Comparable` implemented by hand; enums are ordered by declaration and their `compareTo` is `final`.

## Related

- [[Java/00 - Syllabus|Syllabus]]
- Previous: [[Java/05 - Working with Data and Errors/02 - Generics|Generics]] · Next: [[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]]
- [[Java/05 - Working with Data and Errors/02 - Generics#4.3 Recursive Bounds and `Comparable`|Generics § 4.3]]: `<T extends Comparable<? super T>>`; [[Java/05 - Working with Data and Errors/02 - Generics#2.4 Generic Interfaces|§ 2.4]]: the raw `Comparable` mistake
- [[Java/05 - Working with Data and Errors/04 - Collections Framework|Collections Framework]]: `TreeSet`, `TreeMap`, `PriorityQueue`, and sorting map entries
- [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]: `equals` and `hashCode`, which the ordering should agree with
- [[Java/04 - Object-Oriented Programming/07 - Enums|Enums]]: enum ordering by declaration
- [[Java/04 - Object-Oriented Programming/08 - Nested and Anonymous Classes|Nested and Anonymous Classes]]: anonymous comparator classes
- [[Java/06 - Functional Programming/01 - Lambdas and Functional Interfaces|Lambdas and Functional Interfaces]]: lambdas and method references such as `String::length`
- [[Java/02 - Control Flow/03 - Arrays#8.1 Sorting|Arrays § 8.1]]: `Arrays.sort` on arrays
- [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms|DSA: Sorting Algorithms]]: how the sorts work, stability, comparator patterns for contests
