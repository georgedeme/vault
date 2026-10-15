# Collections Framework in Java

The <span class="hl-blue">Collections Framework</span> (`java.util`) is Java's library of data structures: resizable lists, sets without duplicates, maps from keys to values, queues, deques, and priority queues. It is organised as a small set of **interfaces** (`List`, `Set`, `Queue`, `Deque`, `Map`) that say *what* a collection can do, and several **implementations** of each (`ArrayList`, `HashSet`, `TreeMap`, …) that decide *how*, with different speeds and orderings. This chapter covers the interface hierarchy, lists, iterating and modifying safely (`ConcurrentModificationException`), the three kinds of sets and maps, the useful `Map` methods (`getOrDefault`, `merge`, `computeIfAbsent`, …), queues and deques (`ArrayDeque` as a stack and a queue, `PriorityQueue`), unmodifiable collections, the `Collections` utility class, conversions to and from arrays, and how to choose an implementation.

Collections are generic, so this chapter relies on [[Java/05 - Working with Data and Errors/02 - Generics|Generics]]. The autoboxing traps of collections of wrappers (`remove(int)` vs. `remove(Object)`, wrong key types silently not matching, unboxing `null`) are in [[Java/05 - Working with Data and Errors/02 - Generics#9. Generics and Autoboxing — Traps|Generics § 9]] and are only linked here. Hash-based collections depend on `equals`/`hashCode` ([[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]), and sorted ones on `compareTo` or a `Comparator` ([[Java/05 - Working with Data and Errors/03 - Comparable and Comparator|Comparable and Comparator]]). How the structures work inside, with their complexity analysis, is in the DSA notes: [[DSA/02 - Linear Data Structures/01 - Arrays|dynamic arrays]], [[DSA/02 - Linear Data Structures/03 - Linked Lists|linked lists]], [[DSA/02 - Linear Data Structures/06 - Hash Tables|hash tables]], [[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|balanced trees]], and [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|heaps]].

## Contents

- [[#1. Why Collections|1. Why Collections]]
- [[#2. The Interface Hierarchy|2. The Interface Hierarchy]]
- [[#3. Lists|3. Lists]]
- [[#4. Iterating and Modifying|4. Iterating and Modifying]]
- [[#5. Sets|5. Sets]]
- [[#6. Maps|6. Maps]]
- [[#7. Queues, Deques, and Stacks|7. Queues, Deques, and Stacks]]
- [[#8. Unmodifiable Collections|8. Unmodifiable Collections]]
- [[#9. The `Collections` Utility Class|9. The `Collections` Utility Class]]
- [[#10. Converting Between Arrays and Collections|10. Converting Between Arrays and Collections]]
- [[#11. Equality and Mutable Elements|11. Equality and Mutable Elements]]
- [[#12. Choosing an Implementation|12. Choosing an Implementation]]
- [[#13. Common Pitfalls|13. Common Pitfalls]]
- [[#14. Quick Reference — Non-Obvious Outcomes|14. Quick Reference — Non-Obvious Outcomes]]
- [[#15. Practice — Trick Questions|15. Practice — Trick Questions]]
- [[#16. Summary|16. Summary]]

---

## 1. Why Collections

### 1.1 Arrays vs. Collections

An array has a fixed length, and finding, inserting, or removing an element is your job ([[Java/02 - Control Flow/03 - Arrays|Arrays]]). Collections take care of that:

| | Array | Collection |
|---|---|---|
| Size | fixed at creation | grows and shrinks |
| Element types | primitives or objects | objects only (`List<Integer>`, not `List<int>`) |
| Insert / remove in the middle | write the shifting loop yourself | `list.add(i, x)`, `list.remove(i)` |
| "Is `x` in here?" | write a loop | `contains(x)`, and fast (`O(1)` or `O(log n)`) for sets and maps |
| No duplicates, key → value lookup, sorted order | write it yourself | `Set`, `Map`, `TreeSet`/`TreeMap` |
| Printing | `Arrays.toString(a)` | `System.out.println(list)` prints `[a, b, c]` |
| Equality | `Arrays.equals(a, b)` | `list1.equals(list2)` compares contents |
| Speed and memory | best, especially for primitives | some overhead: objects, boxing |

Use an array for fixed-size data and for primitives in performance-critical code. Use a collection for almost everything else.

### 1.2 Interfaces and Implementations

Every collection type comes in two parts:

- an **interface** that describes the abstract data type: `List` (an ordered sequence with positions), `Set` (no duplicates), `Map` (keys to values), `Queue`/`Deque` (removal from the ends);
- one or more **classes** that implement it with a concrete data structure: `ArrayList` (a resizable array) and `LinkedList` (a doubly linked list) both implement `List`.

The interface decides which methods you can call; the class decides how fast they are and, for sets and maps, in what order elements come out.

---

## 2. The Interface Hierarchy

### 2.1 The Interfaces

```
Iterable<E>                          anything usable in a for-each loop
└── Collection<E>                    a group of elements: add, remove, contains, size, …
    ├── List<E>                      ordered, indexed, duplicates allowed       ArrayList, LinkedList
    ├── Set<E>                       no duplicates                              HashSet, LinkedHashSet
    │   └── SortedSet<E>
    │       └── NavigableSet<E>      sorted, with floor/ceiling/…               TreeSet
    └── Queue<E>                     removal from the head                      PriorityQueue
        └── Deque<E>                 insertion/removal at both ends             ArrayDeque, LinkedList

Map<K, V>                            keys → values; NOT a Collection            HashMap, LinkedHashMap
└── SortedMap<K, V>
    └── NavigableMap<K, V>           sorted keys, with floorKey/ceilingKey/…    TreeMap
```

![[Collections - Interface Hierarchy.excalidraw|800]]

> [!warning] Trick: a `Map` is not a `Collection`, and not `Iterable`
> ```java
> Collection<String> c = new HashMap<String, String>();   // compile error: incompatible types
> for (String k : map) { }                                // compile error: for-each not applicable to expression type
> for (String k : map.keySet()) { }                       // OK: iterate over one of its views (§ 6.2)
> ```
> A map holds **pairs**, so it has its own interface. It offers three `Collection` **views** of its contents: `keySet()`, `values()`, and `entrySet()`.

`LinkedList` implements **both** `List` and `Deque`. Since Java 21, `List`, `Deque`, `LinkedHashSet`, `SortedSet`, `LinkedHashMap`, and `SortedMap` also implement new `SequencedCollection`/`SequencedMap` interfaces, which add `getFirst()`, `getLast()`, `addFirst`, `addLast`, `removeFirst`, `removeLast`, and `reversed()` (Java 21, not available in Java 17).

### 2.2 Program to the Interface

Declare variables, parameters, and return types with the **interface**, and name the class only at `new`:

```java
List<String> names = new ArrayList<>();          // ✅ the rest of the code only knows "a List"
ArrayList<String> names = new ArrayList<>();     // works, but ties every user to ArrayList

static double average(Collection<Integer> nums) { … }   // accepts a List, a Set, a Queue, …
```

Switching to `LinkedList` or `CopyOnWriteArrayList` later then means changing one line. This is the general principle from [[Java/04 - Object-Oriented Programming/04 - Polymorphism#9.2 Program to the Supertype|Polymorphism § 9.2]]. An interface can't be instantiated: `new List<>()` is a compile error (*List is abstract; cannot be instantiated*).

### 2.3 Methods Every `Collection` Has

| Method | Returns | Note |
|---|---|---|
| `add(e)` | `boolean` | `false` if nothing changed: a `Set` that already contains `e` |
| `remove(Object o)` | `boolean` | removes **one** element equal to `o` |
| `contains(Object o)` | `boolean` | uses `equals` (or `compareTo` for sorted sets) |
| `size()`, `isEmpty()` | `int`, `boolean` | |
| `clear()` | | |
| `addAll(c)`, `removeAll(c)`, `retainAll(c)`, `containsAll(c)` | `boolean` | bulk operations: union, difference, intersection, subset ([[#5.4 Set Operations|§ 5.4]]) |
| `removeIf(predicate)` | `boolean` | removes every element matching a condition ([[#4.4 Removing Elements Safely|§ 4.4]]) |
| `iterator()` | `Iterator<E>` | [[#4.2 `Iterator` and `ListIterator`|§ 4.2]] |
| `toArray()`, `toArray(T[])`, `toArray(String[]::new)` | arrays | [[#10. Converting Between Arrays and Collections|§ 10]] |
| `stream()` | `Stream<E>` | [[Java/06 - Functional Programming/02 - Streams|Streams]] |

`remove`, `contains`, and friends take an **`Object`**, not an `E`, so passing the wrong type compiles and silently never matches ([[Java/05 - Working with Data and Errors/02 - Generics#9.2 Methods That Take `Object` Accept the Wrong Type|Generics § 9.2]]).

### 2.4 Optional Operations and `UnsupportedOperationException`

The modifying methods (`add`, `remove`, `set`, `clear`, …) are *optional*: a collection may refuse them by throwing `UnsupportedOperationException`. That is how unmodifiable and fixed-size collections work ([[#8. Unmodifiable Collections|§ 8]]). The compiler can't catch it, because `List.of(1)` and `new ArrayList<>()` both have the type `List<Integer>`.

---

## 3. Lists

A `List` is an ordered sequence: every element has an **index** from `0` to `size() - 1`, and duplicates and `null` are allowed (in `ArrayList` and `LinkedList`).

### 3.1 `List` Methods

| Method | Effect | Notes |
|---|---|---|
| `get(i)`, `set(i, e)` | read / replace at index `i` | `set` returns the **old** element |
| `add(e)` | append at the end | |
| `add(i, e)` | insert at `i`, shifting later elements right | `0 <= i <= size()` |
| `remove(int i)` | remove at index `i`, returns it | shifts later elements left |
| `remove(Object o)` | remove the **first** element equal to `o`, returns `boolean` | `remove(1)` on a `List<Integer>` picks the **index** version ([[Java/05 - Working with Data and Errors/02 - Generics#9.1 `remove(int)` vs. `remove(Object)`|Generics § 9.1]]) |
| `indexOf(o)`, `lastIndexOf(o)` | first / last index of `o`, or `-1` | uses `equals` |
| `subList(from, to)` | a **view** of `[from, to)` | [[#3.5 `subList` Is a View|§ 3.5]] |
| `sort(cmp)` | sort in place | `null` → natural ordering ([[Java/05 - Working with Data and Errors/03 - Comparable and Comparator|Comparable and Comparator]]) |
| `replaceAll(f)` | replace every element with `f(element)` | `list.replaceAll(String::toUpperCase)` |
| `List.of(…)`, `List.copyOf(c)` | unmodifiable lists | [[#8. Unmodifiable Collections|§ 8]] |

```java
List<Integer> m = new ArrayList<>();
m.add(1);
m.add(0, 2);              // [2, 1]
m.add(2, 9);              // [2, 1, 9]: index == size() appends
m.add(5, 3);              // IndexOutOfBoundsException: Index: 5, Size: 3
m.set(0, 7);              // returns 2; list is [7, 1, 9]
m.remove(Integer.valueOf(9));   // true; [7, 1]
m.remove(0);              // returns 7; [1]
```

### 3.2 `ArrayList` — Size vs. Capacity

`ArrayList` stores its elements in an internal array that is **bigger than needed**. When it fills up, a larger array (about 1.5×) is allocated and the elements are copied. That keeps `add` at the end `O(1)` *amortized* ([[DSA/02 - Linear Data Structures/01 - Arrays#3. Dynamic Arrays and Amortized Resizing|DSA: Arrays § 3]]).

- **size** = how many elements the list holds (`size()`).
- **capacity** = how many fit before the next resize. It is invisible from outside.

<span class="hl-red">Trick:</span> the constructor argument is the **capacity**, not the size:

```java
List<String> l = new ArrayList<>(100);   // room for 100, but it holds NOTHING
l.size();                                // 0
l.set(0, "x");                           // IndexOutOfBoundsException: Index 0 out of bounds for length 0
l.add("x");                              // OK: the only way to fill it
```

To create a list of `n` copies of a value, use `new ArrayList<>(Collections.nCopies(n, value))`.

### 3.3 `LinkedList`

`LinkedList` is a doubly linked list: each element sits in its own node with links to the previous and next nodes ([[DSA/02 - Linear Data Structures/03 - Linked Lists#11. Java's LinkedList|DSA: Linked Lists § 11]]). Adding or removing at either **end** is `O(1)`, but `get(i)` has to walk from the nearer end, which is `O(n)`.

<span class="hl-red">An indexed loop over a `LinkedList` is quadratic:</span>

```java
for (int i = 0; i < list.size(); i++) {
    sum += list.get(i);          // each get walks the list: O(n²) in total
}
for (int x : list) {             // the iterator moves one node at a time: O(n)
    sum += x;
}
```

With 100 000 elements, one run took 0 ms for the `ArrayList` indexed loop, about **2.5 s** for the `LinkedList` indexed loop, and 1 ms for the `LinkedList` for-each loop.

### 3.4 `ArrayList` or `LinkedList`

| Operation | `ArrayList` | `LinkedList` |
|---|---|---|
| `get(i)`, `set(i, e)` | `O(1)` | `O(n)` |
| `add(e)` at the end | `O(1)` amortized | `O(1)` |
| `add(0, e)`, `remove(0)` | `O(n)`: shifts everything | `O(1)` |
| `add(i, e)`, `remove(i)` in the middle | `O(n)` shifting | `O(n)` walking to `i` |
| `contains`, `indexOf` | `O(n)` | `O(n)` |
| memory per element | one reference | a node object with three references |
| cache-friendliness | excellent (contiguous array) | poor (scattered nodes) |

<span class="hl-yellow">Default to `ArrayList`.</span> Even where the table favours `LinkedList` on paper, `ArrayList` is often faster in practice because of memory locality. For a queue or a stack, use `ArrayDeque` ([[#7.2 `ArrayDeque` as a Stack and as a Queue|§ 7.2]]), not `LinkedList`.

### 3.5 `subList` Is a View

`list.subList(from, to)` doesn't copy anything. It returns a **view** of the range `[from, to)` of the original list. Changes through the view change the original:

```java
List<Integer> l = new ArrayList<>(List.of(0, 1, 2, 3, 4, 5));
List<Integer> sub = l.subList(1, 4);     // [1, 2, 3]
sub.set(0, 10);                          // l is now [0, 10, 2, 3, 4, 5]
sub.clear();                             // l is now [0, 4, 5]: the idiom for removing a range
l.add(99);                               // a structural change made directly to l…
sub.size();                              // …invalidates the view: ConcurrentModificationException
```

Use a sub-list briefly, for one operation, and don't keep it while the original list is changed. For an independent copy: `new ArrayList<>(l.subList(1, 4))`.

---

## 4. Iterating and Modifying

### 4.1 Four Ways to Iterate

```java
for (String s : list) { … }                       // 1. for-each: works on every Iterable

for (int i = 0; i < list.size(); i++) {           // 2. by index: only sensible for ArrayList
    String s = list.get(i);
}

Iterator<String> it = list.iterator();            // 3. explicit Iterator: needed to remove while iterating
while (it.hasNext()) {
    String s = it.next();
}

list.forEach(s -> System.out.println(s));         // 4. forEach with a lambda (Part VI)
```

The for-each loop is compiled into form 3: it calls `iterator()`, then `hasNext()`/`next()` ([[Java/02 - Control Flow/02 - Loops#4. The Enhanced `for` Loop (for-each)|Loops § 4]]). Assigning to the loop variable changes only the local copy, never the list: `for (String s : l) s = s + "!";` leaves `l` unchanged.

### 4.2 `Iterator` and `ListIterator`

| `Iterator<E>` method | Meaning |
|---|---|
| `hasNext()` | is there another element? |
| `next()` | return it and move past it; `NoSuchElementException` if there is none |
| `remove()` | remove the element **last returned by `next()`**; `IllegalStateException` if `next()` hasn't been called, or if `remove()` was already called for this element |

A `ListIterator` (`list.listIterator()`) also moves backwards (`hasPrevious`, `previous`), knows the index (`nextIndex`), and can `set(e)` (replace the last element returned) and `add(e)` (insert at the current position):

```java
List<String> l = new ArrayList<>(List.of("a", "b", "c"));
ListIterator<String> it = l.listIterator();
while (it.hasNext()) {
    if (it.next().equals("b")) {
        it.set("B");          // replace "b"
        it.add("b2");         // insert after it
    }
}
// l is [a, B, b2, c]
```

### 4.3 `ConcurrentModificationException`

<span class="hl-red">Adding or removing elements of a collection directly while a for-each loop is iterating over it throws `ConcurrentModificationException`</span> (CME), even in a single-threaded program:

```java
List<String> a = new ArrayList<>(List.of("a", "b", "c", "d"));
for (String s : a) {
    if (s.equals("a")) {
        a.remove(s);          // the removal itself works…
    }
}                             // …but the iterator's next step throws ConcurrentModificationException
```

The collection keeps a modification counter (`modCount`), which every structural change (add, remove, clear) increments. The iterator remembers the value it started with and checks it in `next()`. If it differs, the iterator can't know where it is any more, so it fails fast instead of skipping or repeating elements. `set(i, e)` isn't structural, so replacing elements during a for-each is fine.

> [!warning] Trick: removing the second-to-last element doesn't throw
> ```java
> List<String> b = new ArrayList<>(List.of("a", "b", "c"));
> for (String s : b) {
>     if (s.equals("b")) b.remove(s);
> }
> System.out.println(b);        // [a, c]: no exception, and "c" was never visited!
> ```
> After `"b"` is returned, the iterator's cursor is 2. Removing `"b"` makes `size()` 2. `hasNext()` only checks `cursor != size`, so it returns `false`, the loop ends normally, and `next()` (which does the check) is never called. The bug is still there: `"c"` was skipped. Removing the **last** element, on the other hand, does throw: the cursor (3) has passed the new size (2), so `hasNext()` is `true` and `next()` detects the change.

![[Collections - Removing During for-each.excalidraw|800]]

The same applies to maps: `map.put` of a **new** key, or `map.remove`, while iterating over `map.keySet()` (or `entrySet()`, `values()`) throws CME. Changing the value of an existing key with `put` is not structural and is allowed.

### 4.4 Removing Elements Safely

```java
List<Integer> l = new ArrayList<>(List.of(1, 2, 2, 3, 4, 4, 5));   // remove the even numbers

// ✅ 1. Iterator.remove()
Iterator<Integer> it = l.iterator();
while (it.hasNext()) {
    if (it.next() % 2 == 0) it.remove();
}

// ✅ 2. removeIf (Java 8+): shortest and fastest for ArrayList
l.removeIf(x -> x % 2 == 0);

// ✅ 3. an index loop running BACKWARDS
for (int i = l.size() - 1; i >= 0; i--) {
    if (l.get(i) % 2 == 0) l.remove(i);
}

// ❌ an index loop running FORWARDS skips elements
for (int i = 0; i < l.size(); i++) {
    if (l.get(i) % 2 == 0) l.remove(i);       // [1, 2, 3, 4, 5]: the second 2 and the second 4 survive
}

// ✅ for maps: through a view
map.entrySet().removeIf(e -> e.getValue() > 1);
map.values().removeIf(v -> v == 0);
```

The forward loop fails because removing index `i` shifts the next element into position `i`, and then `i++` jumps over it. No exception warns about it.

---

## 5. Sets

A `Set` contains no duplicates: `add` returns `false` and changes nothing if an equal element is already present.

```java
Set<Integer> s = new HashSet<>();
s.add(1);     // true
s.add(1);     // false: already there
```

### 5.1 `HashSet`

A `HashSet` stores elements in a hash table ([[DSA/02 - Linear Data Structures/06 - Hash Tables#7. HashMap and HashSet in Java|DSA: Hash Tables § 7]]). `add`, `remove`, and `contains` are `O(1)` on average. It finds an element by its `hashCode()` and confirms it with `equals()`, so <span class="hl-yellow">a class used in a `HashSet` (or as a `HashMap` key) must override both `equals` and `hashCode`, consistently</span>. Otherwise two "equal" objects are both kept, and `contains` with an equal-but-different object returns `false` ([[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]).

<span class="hl-red">The iteration order of a `HashSet` is unspecified.</span> It depends on the hash codes and the table size, and can change when the set grows. Sometimes it *looks* sorted, which makes the trap worse:

```java
new HashSet<>(List.of(3, 1, 2));      // prints [1, 2, 3]: small Integers hash to themselves
new HashSet<>(List.of(16, 1, 2));     // prints [16, 1, 2]: 16 lands in bucket 0 of a 16-bucket table
```

Never rely on that order. If order matters, use `LinkedHashSet` (insertion order) or `TreeSet` (sorted order).

### 5.2 `LinkedHashSet`

A `LinkedHashSet` is a `HashSet` that also links its entries in **insertion order**, and iterates in that order. It costs a little more memory. Re-adding an element that is already present doesn't move it. To move it to the end, remove it and add it again:

```java
Set<String> lhs = new LinkedHashSet<>(List.of("a", "b", "c"));
lhs.add("a");                         // [a, b, c]: unchanged
lhs.remove("a"); lhs.add("a");        // [b, c, a]
```

A classic use: removing duplicates from a list while keeping the first occurrence of each, `new ArrayList<>(new LinkedHashSet<>(list))`.

### 5.3 `TreeSet` and `NavigableSet`

A `TreeSet` keeps its elements **sorted**, in a red-black tree ([[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees#7. TreeMap and TreeSet in Java|DSA: Balanced Trees § 7]]). `add`, `remove`, and `contains` are `O(log n)`. It orders elements by their natural ordering or by a `Comparator` given to the constructor, and it uses that ordering, **not `equals`**, to decide what is a duplicate ([[Java/05 - Working with Data and Errors/03 - Comparable and Comparator#4.2 Sorted Sets and Maps Use `compareTo`, Not `equals`|Comparable and Comparator § 4.2]]). It doesn't accept `null` with natural ordering.

Being sorted, it can answer "nearest" questions that a `HashSet` can't:

```java
TreeSet<Integer> t = new TreeSet<>(List.of(10, 20, 30, 40));
t.first();          // 10          t.last();           // 40
t.floor(25);        // 20  (greatest ≤ 25)       t.ceiling(25);     // 30  (smallest ≥ 25)
t.lower(20);        // 10  (greatest < 20)       t.higher(20);      // 30  (smallest > 20)
t.floor(5);         // null: nothing ≤ 5
t.headSet(30);      // [10, 20]       (elements < 30)
t.tailSet(30);      // [30, 40]       (elements ≥ 30)
t.subSet(15, 35);   // [20, 30]       (15 ≤ x < 35)
t.descendingSet();  // [40, 30, 20, 10]
t.pollFirst();      // removes and returns 10
new TreeSet<Integer>().first();     // NoSuchElementException (but floor/ceiling/pollFirst return null)
```

`headSet`, `tailSet`, and `subSet` are **views**, like `subList`: changes to them change the set.

### 5.4 Set Operations

The bulk methods implement the mathematical set operations, but they **modify the set they are called on**. Copy first to keep the original:

```java
Set<Integer> a = new TreeSet<>(List.of(1, 2, 3, 4));
Set<Integer> b = Set.of(3, 4, 5);

Set<Integer> union = new TreeSet<>(a);  union.addAll(b);      // [1, 2, 3, 4, 5]
Set<Integer> inter = new TreeSet<>(a);  inter.retainAll(b);   // [3, 4]
Set<Integer> diff  = new TreeSet<>(a);  diff.removeAll(b);    // [1, 2]
a.containsAll(Set.of(1, 2));                                  // true: subset test
Collections.disjoint(a, Set.of(7, 8));                        // true: no common element
```

### 5.5 Comparing the Three

| | `HashSet` | `LinkedHashSet` | `TreeSet` |
|---|---|---|---|
| Iteration order | unspecified | insertion order | sorted |
| `add` / `remove` / `contains` | `O(1)` average | `O(1)` average | `O(log n)` |
| Decides duplicates with | `hashCode` + `equals` | `hashCode` + `equals` | `compareTo` / comparator |
| `null` element | one allowed | one allowed | no (with natural ordering) |
| Extra operations | — | — | `first`, `floor`, `ceiling`, `headSet`, … |

---

## 6. Maps

A `Map<K, V>` associates **keys** with **values**. Each key appears at most once and maps to exactly one value; values can repeat.

### 6.1 Basic Operations

| Method | Returns | Note |
|---|---|---|
| `put(k, v)` | the **previous** value for `k`, or `null` | replaces an existing value |
| `get(k)` | the value, or `null` if absent | `null` is ambiguous ([[#6.4 `null` Keys, `null` Values, and the Ambiguous `get`|§ 6.4]]) |
| `containsKey(k)`, `containsValue(v)` | `boolean` | `containsValue` is `O(n)` |
| `remove(k)` | the removed value, or `null` | |
| `remove(k, v)` | `boolean` | removes only if `k` currently maps to `v` |
| `size()`, `isEmpty()`, `clear()` | | |
| `keySet()`, `values()`, `entrySet()` | views | [[#6.2 Iterating over a Map — Views|§ 6.2]] |

```java
Map<String, Integer> m = new HashMap<>();
m.put("a", 1);       // returns null: no previous value
m.put("a", 2);       // returns 1; the map is {a=2}
```

### 6.2 Iterating over a Map — Views

A map can't be iterated directly ([[#2.1 The Interfaces|§ 2.1]]). Instead it offers three **views**, collections that read from and write through to the map:

| View | Type | Contains |
|---|---|---|
| `keySet()` | `Set<K>` | the keys |
| `values()` | `Collection<V>` | the values (duplicates possible, so not a `Set`) |
| `entrySet()` | `Set<Map.Entry<K, V>>` | key-value pairs, with `getKey()`, `getValue()`, `setValue(v)` |

```java
for (Map.Entry<String, Integer> e : m.entrySet()) {          // the usual way: one lookup per entry
    System.out.println(e.getKey() + " -> " + e.getValue());
}
for (String k : m.keySet()) {
    System.out.println(k + " -> " + m.get(k));               // works, but looks up each key again
}
```

The views are **live**:

```java
Map<String, Integer> m = new TreeMap<>(Map.of("a", 1, "b", 2, "c", 1));
Set<String> keys = m.keySet();
m.put("d", 4);                           // keys now shows [a, b, c, d]
keys.remove("a");                        // removes the MAPPING a=1 from m
m.values().remove(1);                    // removes the first mapping whose value is 1 (c=1)
for (Map.Entry<String, Integer> e : m.entrySet()) {
    e.setValue(e.getValue() * 100);      // writes through: m is {b=200, d=400}
}
keys.add("z");                           // UnsupportedOperationException: a key needs a value
```

![[Collections - Map Views.excalidraw|800]]

Sorting a map's entries by value is a common task. A map itself can't be sorted by value, but its entries can be copied into a list:

```java
List<Map.Entry<String, Integer>> es = new ArrayList<>(scores.entrySet());
es.sort(Map.Entry.comparingByValue());                                   // ascending by value
es.sort(Map.Entry.<String, Integer>comparingByValue().reversed());       // descending (needs the type witness)
```

### 6.3 Counting, Grouping, and Other Useful Methods

Since Java 8, `Map` has methods that replace the most common "check, then put" patterns:

| Method | Meaning |
|---|---|
| `getOrDefault(k, d)` | the value for `k`, or `d` if `k` is absent |
| `putIfAbsent(k, v)` | put only if `k` is absent **or mapped to `null`**; returns the existing value |
| `computeIfAbsent(k, f)` | if `k` is absent, store `f(k)`; returns the (new or existing) value |
| `computeIfPresent(k, f)` | if `k` is present, replace its value with `f(k, old)` |
| `compute(k, f)` | always: store `f(k, oldOrNull)` |
| `merge(k, v, f)` | if `k` is absent, store `v`; otherwise store `f(old, v)` |
| `replaceAll(f)` | replace every value with `f(k, v)` |
| `remove(k, v)`, `replace(k, v)`, `replace(k, old, new)` | conditional variants |

The two patterns every Java programmer writes constantly:

```java
// Counting occurrences
Map<String, Integer> counts = new TreeMap<>();
for (String w : "the cat and the hat and the bat".split(" ")) {
    counts.merge(w, 1, Integer::sum);         // absent → 1; present → old + 1
}
// {and=2, bat=1, cat=1, hat=1, the=3}

counts.put(w, counts.getOrDefault(w, 0) + 1); // the same thing, longer
counts.put(w, counts.get(w) + 1);             // ❌ NullPointerException for the first occurrence:
                                              //    get returns null, which can't be unboxed

// Grouping: a multimap (key → list of values)
Map<Integer, List<String>> byLength = new TreeMap<>();
for (String w : List.of("hi", "cat", "yo", "dog", "a")) {
    byLength.computeIfAbsent(w.length(), k -> new ArrayList<>()).add(w);
}
// {1=[a], 2=[hi, yo], 3=[cat, dog]}
```

`Integer::sum` and `k -> new ArrayList<>()` are a method reference and a lambda ([[Java/06 - Functional Programming/01 - Lambdas and Functional Interfaces|Lambdas]]). `computeIfAbsent` returns the list stored in the map, so `.add(w)` adds to the map's list directly.

> [!warning] Traps in the Java 8 `Map` methods
> - `map.get("a")++` doesn't compile (*unexpected type; required: variable, found: value*): `get` returns a value, not a variable. Use `merge` or `put(k, get(k) + 1)`.
> - `getOrDefault(k, d)` returns `d` only if the key is **absent**. If the key is present and mapped to `null`, it returns `null`.
> - `putIfAbsent` treats a key mapped to `null` as absent and replaces the `null`.
> - If the function given to `merge`, `compute`, or `computeIfPresent` returns `null`, the mapping is **removed**. If the function given to `computeIfAbsent` returns `null`, nothing is stored.
> - Don't modify the map from inside the function passed to `computeIfAbsent`/`compute`/`merge`. `HashMap` throws `ConcurrentModificationException` when it detects this.

### 6.4 `null` Keys, `null` Values, and the Ambiguous `get`

`HashMap` and `LinkedHashMap` allow **one `null` key** and any number of `null` values. `TreeMap` rejects a `null` key with natural ordering (`NullPointerException`), and `Map.of` rejects `null` everywhere ([[#8.1 `List.of`, `Set.of`, `Map.of`|§ 8.1]]).

That makes `get` ambiguous:

```java
Map<String, Integer> hm = new HashMap<>();
hm.put("a", null);
hm.get("a");            // null: the key is there, with a null value
hm.get("zz");           // null: the key isn't there at all
hm.containsKey("a");    // true: the only way to tell the two cases apart
```

Unboxing that `null` is the classic crash: `int n = map.get("missing");` throws `NullPointerException` ([[Java/05 - Working with Data and Errors/02 - Generics#9.4 Unboxing `null`|Generics § 9.4]]). The simplest rule is to **never store `null` values** in a map, so that `get` returning `null` always means "absent".

### 6.5 `HashMap`, `LinkedHashMap`, `TreeMap`

The three maps mirror the three sets (in fact each set is implemented with the matching map, storing the elements as keys):

| | `HashMap` | `LinkedHashMap` | `TreeMap` |
|---|---|---|---|
| Key order when iterating | unspecified | insertion order (or access order) | sorted by key |
| `get` / `put` / `remove` | `O(1)` average | `O(1)` average | `O(log n)` |
| Keys need | `equals` + `hashCode` | `equals` + `hashCode` | `Comparable` or a `Comparator` |
| `null` key | one allowed | one allowed | no (natural ordering) |
| Extra operations | — | access order, LRU caches ([[DSA/02 - Linear Data Structures/06 - Hash Tables#7. HashMap and HashSet in Java|DSA: Hash Tables § 7.3]]) | `firstKey`, `floorKey`, `ceilingEntry`, `headMap`, `tailMap`, … |

Putting an existing key into a `LinkedHashMap` keeps its original position: after `put("x", 1)`, `put("y", 2)`, `put("x", 3)` the map is `{x=3, y=2}`.

`TreeMap` has the same navigation methods as `TreeSet`, for keys:

```java
TreeMap<String, Integer> m = new TreeMap<>(Map.of("b", 2, "d", 4, "a", 1));   // {a=1, b=2, d=4}
m.firstKey();          // "a"
m.floorKey("c");       // "b"
m.ceilingEntry("c");   // d=4
m.headMap("c");        // {a=1, b=2}
m.tailMap("b");        // {b=2, d=4}
```

`EnumMap` and `EnumSet` are specialised, very fast versions for enum keys ([[Java/04 - Object-Oriented Programming/07 - Enums|Enums]]).

---

## 7. Queues, Deques, and Stacks

### 7.1 The Two Method Families

`Queue` has two methods for each operation: one **throws** when it can't do its job, the other returns a **special value** (`false` or `null`):

| Operation | Throws an exception | Returns a special value |
|---|---|---|
| insert at the tail | `add(e)` (`IllegalStateException` if full) | `offer(e)` → `false` if full |
| remove the head | `remove()` → `NoSuchElementException` if empty | `poll()` → `null` if empty |
| look at the head | `element()` → `NoSuchElementException` if empty | `peek()` → `null` if empty |

`Deque` ("double-ended queue", pronounced *deck*) has both families for **both ends**: `addFirst`/`offerFirst`, `addLast`/`offerLast`, `removeFirst`/`pollFirst`, `removeLast`/`pollLast`, `getFirst`/`peekFirst`, `getLast`/`peekLast`. The `Queue` methods operate at the ends a queue would use: `offer` = `offerLast`, `poll` = `pollFirst`, `peek` = `peekFirst`. The DSA view of these structures is in [[DSA/02 - Linear Data Structures/05 - Queues and Deques#4. Queues and Deques in Java|DSA: Queues and Deques § 4]].

Because `poll` and `peek` use `null` to mean "empty", queues generally don't allow `null` elements: `ArrayDeque` and `PriorityQueue` throw `NullPointerException` on `add(null)`. `LinkedList` allows them, which makes its `poll()` ambiguous.

### 7.2 `ArrayDeque` as a Stack and as a Queue

`ArrayDeque` (a circular array) is the standard choice for **both** a stack and a queue. All operations at both ends are `O(1)` amortized.

```java
// As a STACK (last in, first out): push, pop, and peek all work at the HEAD
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1); stack.push(2); stack.push(3);
System.out.println(stack);    // [3, 2, 1]: printed from the top
stack.peek();                 // 3
stack.pop();                  // 3; stack is [2, 1]

// As a QUEUE (first in, first out): offer at the tail, poll at the head
Deque<Integer> queue = new ArrayDeque<>();
queue.offer(1); queue.offer(2); queue.offer(3);
System.out.println(queue);    // [1, 2, 3]
queue.peek();                 // 1
queue.poll();                 // 1; queue is [2, 3]
```

![[Collections - ArrayDeque as Stack and Queue.excalidraw|800]]

| Stack operation | `Deque` method | Empty deque |
|---|---|---|
| push | `push(e)` = `addFirst(e)` | |
| pop | `pop()` = `removeFirst()` | `NoSuchElementException` |
| top | `peek()` = `peekFirst()` | `null` |

> [!warning] Trick: a stack prints in opposite orders depending on the class
> ```java
> Deque<Integer> d = new ArrayDeque<>();  d.push(1); d.push(2); d.push(3);
> Stack<Integer> s = new Stack<>();       s.push(1); s.push(2); s.push(3);
> System.out.println(d);    // [3, 2, 1]: ArrayDeque pushes at the FRONT
> System.out.println(s);    // [1, 2, 3]: Stack is a Vector, pushing at the END
> ```
> Both pop `3` first. The printed order (and the order of a for-each loop) is opposite, which matters when converting code from `Stack` to `ArrayDeque`.

### 7.3 `PriorityQueue`

A `PriorityQueue` always hands out its **smallest** element first (by natural ordering or a `Comparator`). It is a binary heap: `offer` and `poll` are `O(log n)`, `peek` is `O(1)`. The full treatment, including top-k and two-heap patterns, is in [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues#4. PriorityQueue in Java|DSA: Heaps § 4]].

```java
PriorityQueue<Integer> min = new PriorityQueue<>(List.of(5, 1, 4, 2, 3));
PriorityQueue<Integer> max = new PriorityQueue<>(Comparator.reverseOrder());   // a max-heap
```

> [!warning] Trick: a `PriorityQueue` is not sorted inside
> ```java
> System.out.println(min);                 // [1, 2, 4, 5, 3]: heap order, NOT sorted
> for (int x : min) System.out.print(x);   // 1 2 4 5 3: the iterator follows the array
> while (!min.isEmpty()) System.out.print(min.poll());   // 1 2 3 4 5: only poll gives sorted order
> ```
> Only the **head** is guaranteed to be the smallest. `toString`, for-each, and `toArray` show the internal array. Also: `contains` and `remove(Object)` are `O(n)`, ties come out in no particular order ([[Java/05 - Working with Data and Errors/03 - Comparable and Comparator#8.2 Stability — and What Isn't Stable|Comparable and Comparator § 8.2]]), and changing an element's priority while it is inside breaks the heap.

### 7.4 Legacy `Stack` and `Vector`

`Vector`, `Stack`, `Hashtable`, and `Enumeration` date from Java 1.0, before the Collections Framework. Their methods are all `synchronized` (slower, and no real help for thread safety), and `Stack extends Vector` exposes `add(0, x)`, `get(i)`, and `remove(i)`, so a "stack" can be modified in the middle, a textbook case of misused inheritance ([[Java/04 - Object-Oriented Programming/03 - Inheritance#12.1 Is-a vs. Has-a|Inheritance § 12.1]]). `Stack.pop()` on an empty stack throws `EmptyStackException` rather than `NoSuchElementException`.

| Legacy | Use instead |
|---|---|
| `Vector` | `ArrayList` |
| `Stack` | `ArrayDeque` (as a `Deque`) |
| `Hashtable` | `HashMap` (or `ConcurrentHashMap` for threads) |
| `Enumeration` | `Iterator` |

---

## 8. Unmodifiable Collections

### 8.1 `List.of`, `Set.of`, `Map.of`

Since Java 9, the static factories create small **unmodifiable** collections:

```java
List<String> l = List.of("a", "b", "c");
Set<Integer> s = Set.of(1, 2, 3);
Map<String, Integer> m = Map.of("one", 1, "two", 2);                       // up to 10 key-value pairs
Map<String, Integer> big = Map.ofEntries(Map.entry("one", 1), Map.entry("two", 2));   // any number
```

> [!warning] Rules that catch people out
> - **Every** modifying method throws `UnsupportedOperationException`: `add`, `set`, `remove`, `clear`, `sort`, and even calls that wouldn't change anything (`List.of().clear()`, `List.of(1).removeIf(x -> x > 5)`).
> - **`null` is rejected everywhere**: `List.of("a", null)` throws `NullPointerException`, and so do `List.of(1).contains(null)`, `Set.of(1).contains(null)`, `Map.of("a", 1).get(null)`, and `containsKey(null)`. Just *asking* about `null` throws.
> - **Duplicates** are rejected where they make no sense: `Set.of(1, 1)` throws `IllegalArgumentException: duplicate element: 1`, and `Map.of("a", 1, "a", 2)` throws `duplicate key: a`. `List.of(1, 1)` is fine.
> - The iteration order of `Set.of` and `Map.of` is **unspecified, and in practice changes from one run of the program to the next**. Don't print them in tests that compare output.
> - They are only **shallowly** immutable: `List.of(new int[]{1}).get(0)[0] = 99` changes the array inside.

### 8.2 Views vs. Copies

| Code | Modifiable? | `null`s | Changes to the source show through? |
|---|---|---|---|
| `List.of(a, b)` | ❌ | ❌ | (no source) |
| `List.copyOf(list)` (Java 10+) | ❌ | ❌ | ❌: a snapshot |
| `Collections.unmodifiableList(list)` | ❌ through the view | ✅ | ✅: a **view** |
| `Arrays.asList(array)` | `set` ✅, `add`/`remove` ❌ (fixed size) | ✅ | ✅: writes through to the array ([[Java/02 - Control Flow/03 - Arrays#8.4 `asList`|Arrays § 8.4]]) |
| `Collections.nCopies(n, x)`, `emptyList()`, `singletonList(x)` | ❌ | ✅ | (no source) |
| `stream.toList()` (Java 16+) | ❌ | ✅ | ❌ ([[Java/06 - Functional Programming/02 - Streams|Streams]]) |
| `new ArrayList<>(list)` | ✅ | ✅ | ❌: an independent copy |

```java
List<Integer> base = new ArrayList<>(List.of(1));
List<Integer> view = Collections.unmodifiableList(base);
List<Integer> copy = List.copyOf(base);
base.add(2);
System.out.println(view + " " + copy);      // [1, 2] [1]
```

When a class hands out its internal list, the choice between a view and a copy is a design decision: [[Java/04 - Object-Oriented Programming/02 - Encapsulation#6.3 Defensive Copies and Unmodifiable Views|Encapsulation § 6.3]].

---

## 9. The `Collections` Utility Class

`java.util.Collections` (with an **s**) is a class of static helper methods, the collections counterpart of `java.util.Arrays`. Don't confuse it with the interface `Collection`.

| Method | Effect |
|---|---|
| `sort(list)`, `sort(list, cmp)` | sort in place ([[Java/05 - Working with Data and Errors/03 - Comparable and Comparator|Comparable and Comparator]]) |
| `reverse(list)` | `[1, 2, 3, 4, 5]` → `[5, 4, 3, 2, 1]` |
| `swap(list, i, j)` | swap two positions |
| `rotate(list, d)` | shift right by `d`: `[1, 4, 3, 2, 5]` rotated by 2 → `[2, 5, 1, 4, 3]` |
| `shuffle(list)`, `shuffle(list, random)` | random permutation |
| `max(coll)`, `min(coll)`, with an optional comparator | `NoSuchElementException` on an empty collection |
| `frequency(coll, x)` | how many elements equal `x` |
| `binarySearch(list, key)` | the list must be sorted; `-(insertionPoint) - 1` if absent |
| `fill(list, x)` | overwrite every element |
| `addAll(coll, e1, e2, …)` | add several elements |
| `nCopies(n, x)` | an unmodifiable list of `n` times `x` |
| `disjoint(c1, c2)` | no element in common? |
| `emptyList()`, `singletonList(x)`, `emptyMap()`, … | small unmodifiable collections |
| `unmodifiableList(l)`, `unmodifiableSet`, `unmodifiableMap` | read-only views |
| `synchronizedList(l)`, … | thread-safe wrappers (see the optional Concurrency chapter) |
| `reverseOrder()`, `reverseOrder(cmp)` | reversed comparators |

---

## 10. Converting Between Arrays and Collections

| From → To | Code | Note |
|---|---|---|
| `String[]` → fixed-size `List` view | `Arrays.asList(arr)` | `set` writes through to the array; `add`/`remove` throw |
| `String[]` → independent `ArrayList` | `new ArrayList<>(Arrays.asList(arr))` or `new ArrayList<>(List.of(arr))` | `List.of` rejects `null`s |
| `int[]` → `List<Integer>` | a loop with `add`, or `Arrays.stream(arr).boxed().toList()` | `Arrays.asList(intArray)` gives a `List<int[]>` of size 1 ([[Java/02 - Control Flow/03 - Arrays#8.4 `asList`|Arrays § 8.4]]) |
| `List<String>` → `String[]` | `list.toArray(new String[0])` or `list.toArray(String[]::new)` (Java 11+) | |
| `List<String>` → `Object[]` | `list.toArray()` | |
| `List<Integer>` → `int[]` | a loop, or `list.stream().mapToInt(Integer::intValue).toArray()` | |
| `Collection` → `Set` (remove duplicates) | `new HashSet<>(coll)`, `new LinkedHashSet<>(coll)` (keeps order), `new TreeSet<>(coll)` (sorts) | |
| `Set`, `map.keySet()`, `map.values()` → `List` | `new ArrayList<>(set)` | copies |

> [!warning] Trick: `(String[]) list.toArray()` fails
> ```java
> String[] bad = (String[]) list.toArray();       // ClassCastException: Object[] cannot be cast to String[]
> String[] ok  = list.toArray(new String[0]);     // OK
> ```
> `toArray()` with no argument always creates an `Object[]`, because the list's element type is erased at runtime ([[Java/05 - Working with Data and Errors/02 - Generics#7.2 What Erasure Forbids|Generics § 7.2]]). Passing an array tells it which type to create.

> [!info]- `toArray(T[] a)` with an array that is too big
> If the given array is large enough, the elements are copied **into it** and the same array is returned. If it is larger than the list, the slot right after the last element is set to `null`, and the rest is left alone:
> ```java
> String[] big = { "x", "x", "x", "x" };
> String[] r = List.of("a", "b").toArray(big);   // r == big, and it is [a, b, null, x]
> ```
> That `null` marks the end of the data, which can surprise code that expected the old contents. Passing `new String[0]` (or `String[]::new`) always gets a correctly sized new array and is the recommended form.

---

## 11. Equality and Mutable Elements

### 11.1 Collection Equality

`equals` on collections compares **contents**, following each interface's rules, and works across implementations:

| Expression | Result | Rule |
|---|---|---|
| `new ArrayList<>(List.of(1, 2)).equals(new LinkedList<>(List.of(1, 2)))` | `true` | lists: same elements in the same order |
| `List.of(1, 2).equals(List.of(2, 1))` | `false` | order matters for lists |
| `new HashSet<>(List.of(1, 2)).equals(new TreeSet<>(List.of(2, 1)))` | `true` | sets: same elements, any order |
| `List.of(1, 2).equals(Set.of(1, 2))` | `false` | a list never equals a set |
| `new HashMap<>(Map.of("a", 1)).equals(new TreeMap<>(Map.of("a", 1)))` | `true` | maps: same key-value pairs |
| `List.of(new int[]{1}).contains(new int[]{1})` | `false` | arrays use identity `equals` |

A list that contains itself prints as `[(this Collection)]`, but its `hashCode()` recurses forever and throws `StackOverflowError`.

### 11.2 Don't Change an Element While It Is in a Set or Map

A `HashSet` files an element under its hash code at the moment it is added. If a field used by `hashCode` changes afterwards, the element sits in the wrong bucket, and the set can no longer find it:

```java
Set<List<Integer>> set = new HashSet<>();
List<Integer> key = new ArrayList<>(List.of(1, 2));
set.add(key);
key.add(3);                         // the hash code changes
set.contains(key);                  // false: searched in the bucket for [1, 2, 3]
set.contains(List.of(1, 2));        // false: right bucket, but the element no longer equals [1, 2]
set.size();                         // 1: it's still in there, unreachable
```

The same happens to `HashMap` keys, and to `TreeSet` elements or `TreeMap` keys when a field used by `compareTo` changes ([[Java/05 - Working with Data and Errors/03 - Comparable and Comparator#12. Practice — Trick Questions|Comparable and Comparator, Q12]]). Use immutable objects as keys and set elements: `String`, `Integer`, records with immutable fields ([[Java/04 - Object-Oriented Programming/02 - Encapsulation#7. Immutable Classes|Encapsulation § 7]]). More on hashing custom objects: [[DSA/02 - Linear Data Structures/06 - Hash Tables#8. Hashing Custom Objects|DSA: Hash Tables § 8]].

---

## 12. Choosing an Implementation

| Need | Use | Key costs |
|---|---|---|
| a list, mostly reading by index or appending | `ArrayList` | `get` `O(1)`; `add` `O(1)` amortized; insert/remove at the front `O(n)` |
| a stack or a queue | `ArrayDeque` | both ends `O(1)` amortized |
| "is `x` in the group?", no duplicates, order irrelevant | `HashSet` | `O(1)` average |
| … keeping insertion order | `LinkedHashSet` | `O(1)` average |
| … sorted, or "next larger / smaller" queries | `TreeSet` | `O(log n)` |
| key → value lookup | `HashMap` | `O(1)` average |
| … iterating in insertion order, or an LRU cache | `LinkedHashMap` | `O(1)` average |
| … sorted keys, or range / nearest-key queries | `TreeMap` | `O(log n)` |
| always take the smallest (or largest) next | `PriorityQueue` | `offer`/`poll` `O(log n)`; `peek` `O(1)` |
| fixed data that never changes | `List.of`, `Set.of`, `Map.of` | |
| enum keys or elements | `EnumMap`, `EnumSet` | array / bit-vector speed |
| a list with many insertions at the front | `ArrayDeque` if only the ends matter; otherwise usually still `ArrayList` | |

A more detailed complexity table for the Java collections is in [[DSA/01 - Foundations/01 - Complexity Analysis#11.2 Java collections|DSA: Complexity Analysis § 11.2]], including the hidden costs (`contains` inside a loop, `remove(0)` in a loop, `PriorityQueue.remove(Object)`).

---

## 13. Common Pitfalls

- **Declaring with the class** (`ArrayList<String> x`) instead of the interface (`List<String> x`).
- **`new ArrayList<>(n)` expecting `n` elements.** It's the capacity; the list is empty.
- **Indexed loops over a `LinkedList`** (`O(n²)`).
- **Removing from a collection inside a for-each loop** (`ConcurrentModificationException`, or, for the second-to-last element, a silently skipped element).
- **Removing by index in a forward loop**: skips the element after each removal.
- **Keeping a `subList` while modifying the original list.**
- **`list.remove(1)` on a `List<Integer>`** removes index 1 ([[Java/05 - Working with Data and Errors/02 - Generics#9.1 `remove(int)` vs. `remove(Object)`|Generics § 9.1]]).
- **Passing the wrong type to `contains`/`remove`/`get`**: compiles, never matches ([[Java/05 - Working with Data and Errors/02 - Generics#9.2 Methods That Take `Object` Accept the Wrong Type|Generics § 9.2]]).
- **Relying on `HashSet`/`HashMap` iteration order**, even when it happens to look sorted.
- **Custom classes in hash collections without `equals` and `hashCode`**, or in sorted collections with an ordering inconsistent with `equals`.
- **Mutating an element or key while it is inside a set or map.**
- **Expecting `retainAll`/`removeAll`/`addAll` to return a new set.** They modify the receiver.
- **`Map.get` returning `null`**: absent key or `null` value? And unboxing it throws `NullPointerException`.
- **`map.put(k, map.get(k) + 1)`** for a key that may be absent. Use `merge` or `getOrDefault`.
- **Iterating over a `Map` directly** (doesn't compile) or with `keySet()` + `get()` when `entrySet()` would do.
- **Modifying `List.of`/`Set.of`/`Map.of` collections**, putting `null` in them, or even calling `contains(null)` on them.
- **Expecting `Arrays.asList` to support `add`/`remove`**, or `Arrays.asList(intArray)` to give a list of numbers.
- **Treating an unmodifiable view as a frozen copy.**
- **`(String[]) list.toArray()`**: `ClassCastException`.
- **Using `Stack`, `Vector`, `Hashtable`.** Use `ArrayDeque`, `ArrayList`, `HashMap`.
- **Printing or iterating a `PriorityQueue` and expecting sorted order.**
- **Mixing up the throwing and the `null`-returning queue methods** (`remove()` vs. `poll()`).
- **Confusing `Collection` (the interface) with `Collections` (the utility class).**

---

## 14. Quick Reference — Non-Obvious Outcomes

| Code | Result | Why |
|---|---|---|
| `new List<>()` | compile error | an interface can't be instantiated |
| `Collection<String> c = new HashMap<…>()` | compile error | a `Map` is not a `Collection` |
| `for (String k : map)` | compile error | a `Map` is not `Iterable` |
| `new ArrayList<>(100).size()` | `0` | the argument is the capacity |
| `new ArrayList<>(100).set(0, x)` | `IndexOutOfBoundsException` | the list is empty |
| `list.add(size(), x)` / `list.add(size() + 1, x)` | appends / `IndexOutOfBoundsException` | `0 ≤ i ≤ size` |
| `list.set(0, x)` | returns the old element | |
| `map.put(k, v)` | returns the old value or `null` | |
| `set.add(existing)` | `false` | no duplicates |
| for-each removing the first element of `[a, b, c, d]` | `ConcurrentModificationException` | fail-fast iterator |
| for-each removing `b` from `[a, b, c]` | no exception, `c` never visited | `hasNext()` is `false` |
| for-each removing the last element | `ConcurrentModificationException` | |
| for-each calling `list.set(i, x)` | fine | not a structural change |
| `it.remove()` twice in a row | `IllegalStateException` | one `remove` per `next` |
| forward index loop removing evens from `[1, 2, 2, 3, 4, 4, 5]` | `[1, 2, 3, 4, 5]` | the shifted element is skipped |
| `sub = l.subList(1, 4); l.add(x); sub.size()` | `ConcurrentModificationException` | the view is invalidated |
| `sub.clear()` | removes that range from the original | views write through |
| `new HashSet<>(List.of(3, 1, 2))` printed | `[1, 2, 3]` | looks sorted by coincidence |
| `new HashSet<>(List.of(16, 1, 2))` printed | `[16, 1, 2]` | not sorted at all |
| `LinkedHashSet` `[a, b, c]`, then `add("a")` | still `[a, b, c]` | re-adding doesn't move it |
| `TreeSet` `floor(5)` with all elements > 5 | `null` | |
| `new TreeSet<Integer>().first()` | `NoSuchElementException` | |
| `a.retainAll(b)` | `a` itself becomes the intersection | modifies the receiver |
| `map.get("a")++` | compile error | `get` returns a value |
| `map.put(w, map.get(w) + 1)` for a new `w` | `NullPointerException` | unboxing `null` |
| `getOrDefault(k, 0)` when `k` maps to `null` | `null` | the key is present |
| `putIfAbsent(k, 5)` when `k` maps to `null` | stores `5` | `null` counts as absent |
| `merge(k, v, (a, b) -> null)` | removes `k` | `null` result removes |
| `computeIfAbsent(k, x -> null)` | stores nothing | |
| `map.keySet().remove(k)` | removes the mapping | live view |
| `map.keySet().add(k)` | `UnsupportedOperationException` | a key needs a value |
| `entry.setValue(v)` during `entrySet()` iteration | updates the map | live view |
| `Map.entry(k, v).setValue(x)` | `UnsupportedOperationException` | immutable entry |
| `new TreeMap<>().put(null, 1)` | `NullPointerException` | natural ordering |
| `new HashMap<>().put(null, 1)` | OK | one `null` key allowed |
| `LinkedHashMap`: `put x`, `put y`, `put x` again | `{x=…, y=…}` | the key keeps its position |
| `ArrayDeque`: `push(1)`, `push(2)`, `push(3)`, printed | `[3, 2, 1]` | pushes at the front |
| `Stack`: same, printed | `[1, 2, 3]` | a `Vector`, pushes at the end |
| `queue.poll()` / `queue.remove()` on an empty queue | `null` / `NoSuchElementException` | two method families |
| `new ArrayDeque<>().add(null)` | `NullPointerException` | `null` means "empty" |
| `new Stack<>().pop()` | `EmptyStackException` | legacy class |
| `PriorityQueue` of `5, 1, 4, 2, 3` printed | `[1, 2, 4, 5, 3]` | heap order |
| `List.of("a", null)` | `NullPointerException` | no `null`s |
| `List.of(1).contains(null)` | `NullPointerException` | even asking throws |
| `Set.of(1, 1)` / `List.of(1, 1)` | `IllegalArgumentException` / OK | duplicates only matter for sets |
| `List.of(1).removeIf(x -> x > 5)` | `UnsupportedOperationException` | even if nothing would be removed |
| `Arrays.asList(1, 2).set(0, 5)` / `.add(3)` | OK / `UnsupportedOperationException` | fixed size |
| `Collections.unmodifiableList(base)` after `base.add(x)` | shows `x` | it's a view |
| `List.copyOf(base)` after `base.add(x)` | doesn't show `x` | it's a copy |
| `Collections.nCopies(3, "x").add("y")` | `UnsupportedOperationException` | unmodifiable |
| `(String[]) list.toArray()` | `ClassCastException` | creates an `Object[]` |
| `List.of("a", "b").toArray(new String[4])` with contents `x` | `[a, b, null, x]` | `null` after the last element |
| `ArrayList` `equals` `LinkedList` with same elements | `true` | `List` equality |
| `List.of(1, 2).equals(Set.of(1, 2))` | `false` | a list never equals a set |
| `HashSet` `equals` `TreeSet` with same elements | `true` | `Set` equality |
| a list key mutated inside a `HashSet` | `contains` → `false` | wrong bucket |
| `Collections.max(emptyList)` | `NoSuchElementException` | |

---

## 15. Practice — Trick Questions

**Q1.** What is printed?

```java
List<String> list = new ArrayList<>(List.of("a", "b", "c"));
for (String s : list) {
    if (s.equals("b")) list.remove(s);
}
System.out.println(list);
```

> [!success]- Answer
> `[a, c]`, with **no** exception. After `"b"` is returned, the iterator's cursor is 2; removing `"b"` makes the size 2, so `hasNext()` (`cursor != size`) is `false` and the loop ends without ever calling `next()`, which is where the check for concurrent modification happens. `"c"` was never visited. Removing `"a"` or `"c"` instead would have thrown `ConcurrentModificationException`.

**Q2.** What does each line print, or what does it throw?

```java
List<Integer> a = new ArrayList<>(10);
System.out.println(a.size());          // (1)
a.add(0, 5);                           // (2)
a.add(2, 6);                           // (3)
System.out.println(a.set(0, 7));       // (4)
System.out.println(a);                 // (5)
```

> [!success]- Answer
> | Line | Result |
> |---|---|
> | (1) | `0`: 10 is the capacity |
> | (2) | OK: index 0 == size, so it appends. `a` is `[5]` |
> | (3) | `IndexOutOfBoundsException` (*Index: 2, Size: 1*): the index may be at most `size()` |
> | (4) | not reached. Without line (3), it would print `5`, the old element |
> | (5) | not reached. Without line (3): `[7]` |

**Q3.** What is the final list?

```java
List<Integer> l = new ArrayList<>(List.of(1, 2, 2, 3, 4, 4, 5));
for (int i = 0; i < l.size(); i++) {
    if (l.get(i) % 2 == 0) l.remove(i);
}
System.out.println(l);
```

> [!success]- Answer
> `[1, 2, 3, 4, 5]`. At `i = 1` the first `2` is removed, and the second `2` shifts into index 1, but `i` becomes 2 and skips it. The same happens to the second `4`. Iterate backwards, use `removeIf`, or use an `Iterator`.

**Q4.** What is printed?

```java
Map<String, Integer> m = new HashMap<>();
System.out.println(m.put("a", 1));
System.out.println(m.put("a", 2));
m.put("n", null);
System.out.println(m.getOrDefault("n", 0));
System.out.println(m.getOrDefault("zz", 0));
System.out.println(m.putIfAbsent("n", 5));
System.out.println(m.get("n"));
m.merge("a", 10, (oldV, newV) -> null);
System.out.println(m.containsKey("a"));
```

> [!success]- Answer
> ```
> null
> 1
> null
> 0
> null
> 5
> false
> ```
> `put` returns the previous value (`null`, then `1`). `getOrDefault` returns the default only for an **absent** key; `"n"` is present with a `null` value. `putIfAbsent` treats `null` as absent: it stores `5` and returns the old value, `null`. A `merge` function returning `null` removes the mapping.

**Q5.** What is printed?

```java
Deque<Integer> d = new ArrayDeque<>();
d.push(1); d.push(2); d.offer(3); d.push(4);
System.out.println(d);
System.out.println(d.pop() + " " + d.poll() + " " + d.pollLast());
System.out.println(d);
```

> [!success]- Answer
> ```
> [4, 2, 1, 3]
> 4 2 3
> [1]
> ```
> `push` adds at the **front**, `offer` at the **back**. After the four calls: `[4, 2, 1, 3]`. `pop` and `poll` both remove from the front (`4`, then `2`), and `pollLast` removes the `3`.

**Q6.** Which lines compile, and which throw at runtime?

```java
List<Integer> a = List.of(3, 1, 2);
List<Integer> b = Arrays.asList(3, 1, 2);
List<Integer> c = Collections.unmodifiableList(new ArrayList<>(b));
a.contains(null);          // (1)
b.set(0, 9);               // (2)
b.add(4);                  // (3)
c.contains(null);          // (4)
Collections.sort(b);       // (5)
a.sort(null);              // (6)
Set.of(1, 2, 1);           // (7)
```

> [!success]- Answer
> All lines compile (they all have ordinary `List`/`Set` types). At runtime:
>
> | Line | Result |
> |---|---|
> | (1) | `NullPointerException`: `List.of` collections reject even `contains(null)` |
> | (2) | OK: `Arrays.asList` supports `set`; `b` is `[9, 1, 2]` |
> | (3) | `UnsupportedOperationException`: fixed size |
> | (4) | `false`: the unmodifiable wrapper allows `null` queries |
> | (5) | OK: sorting only uses `set`; `b` is `[1, 2, 9]` |
> | (6) | `UnsupportedOperationException` |
> | (7) | `IllegalArgumentException: duplicate element: 1` |

**Q7.** What is printed?

```java
Set<Integer> a = new TreeSet<>(List.of(1, 2, 3, 4));
Set<Integer> b = new TreeSet<>(List.of(3, 4, 5));
a.retainAll(b);
b.addAll(a);
System.out.println(a + " " + b);
```

> [!success]- Answer
> `[3, 4] [3, 4, 5]`. `retainAll` modified `a` itself into the intersection. Adding `[3, 4]` to `b` changes nothing, since both are already there.

**Q8.** What is printed?

```java
PriorityQueue<Integer> pq = new PriorityQueue<>(List.of(5, 1, 4, 2, 3));
System.out.println(pq.peek());
System.out.println(pq);
pq.poll();
System.out.println(pq.peek());
```

> [!success]- Answer
> ```
> 1
> [1, 2, 4, 5, 3]
> 2
> ```
> The head is always the smallest, but `toString` shows the internal heap array, which is not sorted. After removing `1`, the next smallest, `2`, becomes the head.

**Q9.** What is printed?

```java
Map<String, Integer> m = new TreeMap<>(Map.of("a", 1, "b", 2, "c", 1));
m.keySet().remove("b");
m.values().remove(1);
System.out.println(m);
```

> [!success]- Answer
> `{c=1}`. The views write through to the map: removing key `"b"` from `keySet()` removes the mapping `b=2`. `values().remove(1)` removes **one** mapping whose value is `1`, the first one in iteration order, which for a `TreeMap` is `a=1`.

**Q10.** Find and fix the bug.

```java
Map<String, Integer> counts = new HashMap<>();
for (String w : words) {
    counts.put(w, counts.get(w) + 1);
}
```

> [!success]- Answer
> The first time a word appears, `counts.get(w)` returns `null`, and `null + 1` tries to unbox `null`: `NullPointerException`. Fixes:
> ```java
> counts.merge(w, 1, Integer::sum);
> counts.put(w, counts.getOrDefault(w, 0) + 1);
> ```

**Q11.** What is printed?

```java
Set<List<Integer>> set = new HashSet<>();
List<Integer> key = new ArrayList<>(List.of(1, 2));
set.add(key);
key.add(3);
System.out.println(set.contains(key));
System.out.println(set.contains(List.of(1, 2, 3)));
System.out.println(set.size());
```

> [!success]- Answer
> ```
> false
> false
> 1
> ```
> The list was stored in the bucket for the hash code of `[1, 2]`. After it changes to `[1, 2, 3]`, every lookup goes to the bucket for `[1, 2, 3]`'s hash code, where nothing is stored. The element is still there (`size()` is 1) but unreachable. Don't mutate elements of hash-based sets or keys of hash-based maps.

**Q12.** Which lines compile?

```java
Collection<Integer> c = new ArrayList<>();          // (1)
Iterable<Integer> it = new TreeSet<>();             // (2)
Collection<String> m = new HashMap<String, String>();   // (3)
Deque<Integer> d = new LinkedList<>();              // (4)
List<Integer> l = new LinkedList<>();               // (5)
Queue<Integer> q = new ArrayDeque<>();              // (6)
List<Integer> x = new ArrayDeque<>();               // (7)
```

> [!success]- Answer
> | Line | Compiles? | Reason |
> |---|---|---|
> | (1) | ✅ | `ArrayList` is a `List`, hence a `Collection` |
> | (2) | ✅ | every `Collection` is `Iterable` |
> | (3) | ❌ | a `Map` is not a `Collection` |
> | (4) | ✅ | `LinkedList` implements `Deque` |
> | (5) | ✅ | …and `List` |
> | (6) | ✅ | `Deque` extends `Queue` |
> | (7) | ❌ | `ArrayDeque` is not a `List`: it has no indices |

---

## 16. Summary

- The Collections Framework separates **interfaces** (`List`, `Set`, `Queue`, `Deque`, `Map`) from **implementations**. Declare variables with the interface. `Map` is not a `Collection` and is iterated through its views.
- **`ArrayList`** is the default list: `O(1)` access by index, amortized `O(1)` appends. Its constructor argument is the capacity, not the size. **`LinkedList`** is rarely the better choice, and indexed loops over it are quadratic.
- Don't add or remove elements directly during a for-each loop: it throws **`ConcurrentModificationException`**, except when removing the second-to-last element, which silently skips the last one. Use `Iterator.remove`, `removeIf`, or a backwards index loop.
- **Sets**: `HashSet` (fast, unordered, needs `equals` + `hashCode`), `LinkedHashSet` (insertion order), `TreeSet` (sorted, uses `compareTo`, navigation methods). Bulk operations modify the receiver.
- **Maps**: `HashMap`, `LinkedHashMap`, `TreeMap`, with the same trade-offs. Iterate with `entrySet()`. Use `merge` for counting, `computeIfAbsent` for grouping, `getOrDefault` for defaults. `get` returning `null` is ambiguous; avoid `null` values.
- **Queues and stacks**: use `ArrayDeque` for both (`push`/`pop`/`peek` at the head; `offer`/`poll`/`peek` for a queue). Know the throwing vs. `null`-returning methods. `PriorityQueue` hands out the smallest element first but isn't sorted inside. Avoid `Stack`, `Vector`, `Hashtable`.
- **`List.of`/`Set.of`/`Map.of`** are unmodifiable, reject `null` (even in `contains`), and reject duplicate set elements and map keys. `Collections.unmodifiableList` is a read-only **view**; `List.copyOf` is a **copy**; `Arrays.asList` is a fixed-size view of an array.
- `Collections` (with an s) holds the static helpers: `sort`, `reverse`, `shuffle`, `max`, `frequency`, `nCopies`, `unmodifiableX`, ….
- Convert lists to arrays with `toArray(new T[0])`, never by casting `toArray()`.
- Collection `equals` compares contents across implementations. Never mutate an object while it is an element of a set or a key of a map.

## Related

- [[Java/00 - Syllabus|Syllabus]]
- Previous: [[Java/05 - Working with Data and Errors/03 - Comparable and Comparator|Comparable and Comparator]] · Next: [[Java/06 - Functional Programming/01 - Lambdas and Functional Interfaces|Lambdas and Functional Interfaces]]
- [[Java/05 - Working with Data and Errors/02 - Generics|Generics]]: generic types, wildcards in collection signatures, and the autoboxing traps of § 9
- [[Java/05 - Working with Data and Errors/03 - Comparable and Comparator|Comparable and Comparator]]: orderings for `TreeSet`, `TreeMap`, `PriorityQueue`, and `sort`
- [[Java/04 - Object-Oriented Programming/06 - Object Methods|Object Methods]]: `equals` and `hashCode`, required by `HashSet` and `HashMap`
- [[Java/02 - Control Flow/03 - Arrays|Arrays]]: fixed-size arrays, `Arrays.asList`, `Arrays.sort`
- [[Java/04 - Object-Oriented Programming/02 - Encapsulation#6.3 Defensive Copies and Unmodifiable Views|Encapsulation § 6.3]]: handing out collections safely
- [[Java/04 - Object-Oriented Programming/03 - Inheritance#12.1 Is-a vs. Has-a|Inheritance § 12.1]]: why `Stack extends Vector` is a design mistake
- [[Java/05 - Working with Data and Errors/01 - Exception Handling|Exception Handling]]: `ConcurrentModificationException`, `UnsupportedOperationException`, `NoSuchElementException`
- [[Java/06 - Functional Programming/02 - Streams|Streams]]: processing collections with pipelines
- DSA: [[DSA/01 - Foundations/01 - Complexity Analysis#11.2 Java collections|complexities]] · [[DSA/02 - Linear Data Structures/06 - Hash Tables|Hash Tables]] · [[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]] · [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|Heaps]] · [[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]]
