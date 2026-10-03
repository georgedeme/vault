# Arrays

An <span class="hl-blue">array</span> is a fixed-length block of **contiguous** memory holding elements of one type, each reached by an integer index in `O(1)`. Almost every other structure in this syllabus is built on top of one: dynamic arrays, heaps, hash tables, circular queues, segment trees, adjacency lists.

This note covers arrays as a data structure: the memory model and what it costs, dynamic arrays and amortized resizing, the in-place operations that everything else uses (shifting, reversing, rotating, in-place rearrangement), 2D arrays and grids, and a handful of classic single-pass array algorithms. The Java language feature itself (declaration syntax, `Arrays` methods, copying) is in [[Java/02 - Control Flow/03 - Arrays|Java: Arrays]].

## Contents

- [[#1. The Memory Model|1. The Memory Model]]
- [[#2. Static vs. Dynamic Arrays|2. Static vs. Dynamic Arrays]]
- [[#3. Dynamic Arrays and Amortized Resizing|3. Dynamic Arrays and Amortized Resizing]]
- [[#4. ArrayList Internals and Traps|4. ArrayList Internals and Traps]]
- [[#5. Basic In-Place Operations|5. Basic In-Place Operations]]
- [[#6. Rotation|6. Rotation]]
- [[#7. In-Place Rearrangement Tricks|7. In-Place Rearrangement Tricks]]
- [[#8. Classic Single-Pass Array Algorithms|8. Classic Single-Pass Array Algorithms]]
- [[#9. 2D Arrays|9. 2D Arrays]]
- [[#10. Grid Techniques|10. Grid Techniques]]
- [[#11. Common Mistakes|11. Common Mistakes]]
- [[#12. Trick Questions and Special Cases|12. Trick Questions and Special Cases]]
- [[#13. Quick Reference — Non-Obvious Outcomes|13. Quick Reference — Non-Obvious Outcomes]]
- [[#14. Summary|14. Summary]]

---

## 1. The Memory Model

> [!note] Definition
> An array of length `n` occupies one contiguous block. Element `i` lives at
> ```
> address(i) = base + i × elementSize
> ```
> That is one multiplication and one addition, whatever `i` and `n` are. This is why <span class="hl-blue">random access</span> is `O(1)`, and why indexes start at `0` (the index *is* the offset).

### 1.1 Cost of the basic operations

| Operation | Cost | Why |
|---|---|---|
| Read / write `a[i]` | `O(1)` | address arithmetic |
| Search for a value (unsorted) | `O(n)` | must look at every element |
| Search for a value (sorted) | `O(log n)` | [[DSA/Binary Search|Binary Search]] |
| Insert / delete at index `i` | `O(n − i)` | everything after `i` shifts by one |
| Insert / delete at the end | `O(1)` (dynamic array: amortized) | nothing shifts |
| Insert / delete at the front | `O(n)` | everything shifts |
| Resize | impossible for a raw array; `O(n)` copy for a dynamic array | the block after the array may be in use |

### 1.2 Cache locality — why arrays beat their big-O

Memory moves between RAM and the CPU in **cache lines** of 64 bytes (16 `int`s). Reading `a[0]` brings `a[1..15]` along for free, and the hardware prefetcher notices sequential access and fetches ahead. A linked list with the same `O(n)` scan touches one node per cache line, scattered across the heap.

<span class="hl-yellow">A sequential scan of an `int[]` is typically several times faster than the same scan of a `LinkedList<Integer>` or even an `ArrayList<Integer>`</span>: the `ArrayList` stores references, and each `Integer` is a separate object somewhere else on the heap.

### 1.3 Java specifics that matter for DSA

| Fact | Consequence |
|---|---|
| Arrays are **objects** on the heap; the variable holds a reference | `b = a` aliases, it doesn't copy; passing an array to a method lets the method modify it |
| Length is fixed at creation; `a.length` is a field | "Growing" means allocating a new array and copying |
| Elements get **default values**: `0`, `0.0`, `false`, `'\u0000'`, `null` | No need to `fill` with zeros; but an object array starts full of `null` |
| Every access is **bounds-checked** | `ArrayIndexOutOfBoundsException` instead of silent corruption |
| `int[]` stores values; `Integer[]` stores references to boxed objects | `Integer[]` is ~4× the memory and much slower; `==` on its elements compares references |
| Max length is a little under `Integer.MAX_VALUE` | In practice the heap runs out first: `new int[100_000_000]` is already 400 MB |
| `boolean[]` uses **1 byte** per element on HotSpot | `java.util.BitSet` uses 1 bit if memory is tight |

Declaration, initialization, `Arrays.toString`/`equals`/`fill`/`copyOf`, and shallow vs. deep copying are covered in [[Java/02 - Control Flow/03 - Arrays|Java: Arrays]].

---

## 2. Static vs. Dynamic Arrays

| | Static array | Dynamic array |
|---|---|---|
| Size | fixed at creation | grows (and maybe shrinks) on demand |
| Java | `int[]`, `String[]` | `ArrayList<E>` (also `StringBuilder` for chars) |
| Append | not possible (unless you track a `size` yourself) | `O(1)` amortized |
| Memory | exactly `n` slots | up to ~2× slack (capacity ≥ size) |
| Primitives | yes (`int[]`) | `ArrayList` boxes: `ArrayList<Integer>` |

> [!tip] "Static" means fixed **size**, not compile-time allocation
> A Java `int[]` is allocated at run time on the heap with a size that can come from input (`new int[n]`). It's "static" only in the sense that its length can't change afterwards. In C, a "static array" may also mean a stack-allocated array whose size is known at compile time; don't carry that meaning over.

> [!tip] The contest middle ground: a raw array plus a size counter
> When the maximum size is known in advance, allocate `int[] a = new int[MAX]` and keep `int size = 0`. You get append (`a[size++] = x`), pop (`size--`), and clear (`size = 0`) in `O(1)` with no boxing. This is how array-based stacks, heaps, and adjacency lists are usually written in competitive programming.

---

## 3. Dynamic Arrays and Amortized Resizing

A <span class="hl-blue">dynamic array</span> keeps a backing array of some **capacity** and a separate **size** (how many slots are in use). When an append finds `size == capacity`, it allocates a bigger array, copies everything over, and continues.

```
add(x):
    if size == capacity:
        newData = allocate(capacity × GROWTH)      -- GROWTH > 1, e.g. 2 or 1.5
        copy data[0 .. size−1] into newData
        data = newData
    data[size] = x
    size = size + 1

remove(i):                                         -- remove at index i
    shift data[i+1 .. size−1] one slot left
    size = size − 1
    if size > 0 and size == capacity / 4:          -- shrink at 1/4, not 1/2
        resize to capacity / 2
```

### 3.1 Why appends are O(1) amortized

Doubling from capacity 1, the copies over `n` appends cost `1 + 2 + 4 + … + n < 2n`. Total work is `O(n)` for `n` appends, so `O(1)` **amortized** per append, even though a single append can cost `Θ(n)`. The derivation, and the accounting and potential methods, are in [[01 - Complexity Analysis#8.1 Aggregate method — dynamic arrays|Complexity Analysis § 8.1]].

> [!important] The two rules that make it work
> 1. **Grow by a factor, not by a constant.** Growing by `+c` slots each time gives `c + 2c + 3c + … = Θ(n²/c)` total copying, which is `Θ(n)` per append.
> 2. **Shrink at ¼ full, not at ½ full.** If you halve at ½, an alternating `add`/`remove` sequence right at the boundary resizes on *every* operation (thrashing), `Θ(n)` each. Halving at ¼ leaves the new array half full, so `Ω(n)` operations must happen before the next resize.

> [!info]- Growth factor 2 vs. 1.5
> Any factor `g > 1` gives `O(1)` amortized: the total copying is `n · g/(g − 1)`, so `2n` for `g = 2` and `3n` for `g = 1.5`. A smaller factor wastes less memory (at most `g − 1` of the array is slack) but copies more. Java's `ArrayList` uses 1.5 (`newCapacity = old + (old >> 1)`). C++ implementations use 2 (libstdc++) or 1.5 (MSVC). There's also an argument for factors below the golden ratio `φ ≈ 1.618`: freed old blocks can eventually be reused for a later allocation, which never happens with factor 2.

### 3.2 Implementation

```java
import java.util.Arrays;

public class DynamicArray<T> {
    private Object[] data = new Object[4];   // Object[]: can't write new T[4] (erasure)
    private int size = 0;

    public int size() { return size; }

    @SuppressWarnings("unchecked")
    public T get(int i) {
        checkIndex(i);
        return (T) data[i];
    }

    public void set(int i, T x) {
        checkIndex(i);
        data[i] = x;
    }

    public void add(T x) {                         // append: O(1) amortized
        if (size == data.length) resize(2 * data.length);
        data[size++] = x;
    }

    public void add(int i, T x) {                  // insert at i: O(n − i)
        if (i < 0 || i > size) throw new IndexOutOfBoundsException("index " + i + ", size " + size);
        if (size == data.length) resize(2 * data.length);
        System.arraycopy(data, i, data, i + 1, size - i);   // shift right; overlap is handled
        data[i] = x;
        size++;
    }

    @SuppressWarnings("unchecked")
    public T remove(int i) {                       // remove at i: O(n − i)
        checkIndex(i);
        T old = (T) data[i];
        System.arraycopy(data, i + 1, data, i, size - i - 1); // shift left
        data[--size] = null;                       // drop the reference so the GC can reclaim it
        if (size > 0 && size == data.length / 4) resize(data.length / 2);
        return old;
    }

    private void resize(int capacity) {
        data = Arrays.copyOf(data, capacity);
    }

    private void checkIndex(int i) {
        if (i < 0 || i >= size) throw new IndexOutOfBoundsException("index " + i + ", size " + size);
    }
}
```

> [!warning] Two details people leave out
> - **Valid indices are `0 .. size−1`, not `0 .. capacity−1`.** Checking against `data.length` lets a caller read slots that hold stale or `null` values. For `add(i, x)`, `i == size` *is* valid (it means append).
> - **`data[--size] = null` after a removal.** Without it the array keeps a reference to the removed object, so the GC can't reclaim it (a "loitering" reference, a real memory leak in long-running code).

---

## 4. ArrayList Internals and Traps

| Fact | Detail |
|---|---|
| Backing store | `Object[] elementData` plus `int size` |
| Initial capacity | `new ArrayList<>()` starts with a shared empty array; the first `add` allocates **10** |
| Growth | `1.5×` (`old + (old >> 1)`) |
| Shrinking | **never automatic**; `trimToSize()` shrinks capacity to size |
| Pre-sizing | `new ArrayList<>(n)` or `ensureCapacity(n)` avoids the intermediate copies |
| `add(x)` | `O(1)` amortized |
| `add(0, x)`, `remove(0)` | `O(n)`: `System.arraycopy` shifts everything |
| `remove(size() − 1)` | `O(1)` |
| `contains`, `indexOf`, `remove(Object)` | `O(n)` linear scan using `equals` |
| `get`, `set` | `O(1)` |

> [!warning] `remove(int)` vs. `remove(Object)` on a `List<Integer>`
> ```java
> List<Integer> list = new ArrayList<>(List.of(10, 20, 30));
> list.remove(1);                    // removes the element at INDEX 1 → [10, 30]
> list.remove(Integer.valueOf(10));  // removes the VALUE 10 → [30]
> ```
> Overload resolution picks `remove(int index)` for an `int` argument without boxing. If you meant the value, box it explicitly. More in [[Java/05 - Working with Data and Errors/02 - Generics#9. Generics and Autoboxing — Traps|Java: Generics § 9]].

> [!warning] Removing while iterating
> - **For-each + `list.remove(...)`** → `ConcurrentModificationException` (usually; see [[#12. Trick Questions and Special Cases|§12]] for the exception to the exception).
> - **Forward index loop + `remove(i)`** → skips the element right after each removed one, because everything shifts left into slot `i` and then `i++` moves past it.
> - **Fixes:** `list.removeIf(x -> …)` (`O(n)` total), an explicit `Iterator` with `it.remove()`, or a backward index loop. Repeated `remove(i)` is `O(n)` each, so removing many elements by index is `O(n²)`; `removeIf` or the write-pointer pattern ([[#5.3 Remove elements in place (write pointer)|§5.3]]) is `O(n)`.

> [!info]- `Arrays.asList`, `List.of`, `subList`, `toArray`
> - `Arrays.asList(arr)` is a **fixed-size view** of the array: `set` writes through to `arr`, but `add`/`remove` throw `UnsupportedOperationException`. Wrap it, `new ArrayList<>(Arrays.asList(arr))`, to get a real list.
> - `Arrays.asList(intArray)` where `intArray` is an `int[]` gives a `List<int[]>` of size **1**: generics can't hold primitives, so the whole array becomes the single element. Use `Arrays.stream(a).boxed().toList()` or a loop.
> - `List.of(...)` is fully immutable (even `set` throws) and rejects `null` elements.
> - `list.subList(a, b)` is a **view**: changes show through both ways, and structurally modifying the original list afterwards makes the view throw `ConcurrentModificationException`. `list.subList(a, b).clear()` is the idiomatic way to delete a range in one `O(n)` shift.
> - `list.toArray(new Integer[0])` returns a new `Integer[]`. There's no direct route to `int[]`; use `list.stream().mapToInt(Integer::intValue).toArray()`.

---

## 5. Basic In-Place Operations

These are the building blocks for everything else in this note. <span class="hl-blue">In-place</span> means `O(1)` auxiliary space ([[01 - Complexity Analysis#9.2 "In-place" is a claim about auxiliary space|Complexity Analysis § 9.2]]).

### 5.1 Insert and delete by shifting

```
insertAt(a, size, i, x):              -- requires size < len(a)
    for j = size down to i + 1:       -- go RIGHT TO LEFT
        a[j] = a[j − 1]
    a[i] = x
    return size + 1

deleteAt(a, size, i):
    for j = i up to size − 2:         -- go LEFT TO RIGHT
        a[j] = a[j + 1]
    return size − 1
```

```java
static int insertAt(int[] a, int size, int i, int x) {
    for (int j = size; j > i; j--) a[j] = a[j - 1];
    a[i] = x;
    return size + 1;
}

static int deleteAt(int[] a, int size, int i) {
    for (int j = i; j < size - 1; j++) a[j] = a[j + 1];
    return size - 1;
}
```

> [!warning] The direction of the shift matters
> Shifting right with a **left-to-right** loop copies `a[i]` into `a[i+1]`, then that same value into `a[i+2]`, and so on: the whole tail becomes copies of `a[i]`. When the source and destination overlap, copy **away from** the side you're moving toward. `System.arraycopy` handles overlap correctly ("as if" through a temporary array), so use it when you can.

### 5.2 Reverse a range

```
reverse(a, lo, hi):
    while lo < hi:
        swap a[lo], a[hi]
        lo = lo + 1; hi = hi − 1
```

```java
static void reverse(int[] a, int lo, int hi) {   // inclusive bounds
    while (lo < hi) {
        int t = a[lo];
        a[lo++] = a[hi];
        a[hi--] = t;
    }
}
```

`⌊n/2⌋` swaps. The middle element of an odd-length range never moves. `lo < hi` (not `<=`) is the right condition, although `<=` is also harmless here: it swaps the middle element with itself.

### 5.3 Remove elements in place (write pointer)

Keep a **write index** `w`: everything before `w` is the kept part. Scan with a read index; copy kept elements to `a[w++]`.

```
removeValue(a, val):
    w = 0
    for r = 0 to len(a) − 1:
        if a[r] ≠ val:
            a[w] = a[r]; w = w + 1
    return w                         -- new logical length; a[w..] is garbage
```

```java
static int removeValue(int[] a, int val) {
    int w = 0;
    for (int r = 0; r < a.length; r++) {
        if (a[r] != val) a[w++] = a[r];
    }
    return w;
}
```

`O(n)` time, `O(1)` space, and **stable** (kept elements stay in their original order). The same shape handles "move zeroes to the end" (filter, then fill `a[w..]` with `0`) and "remove duplicates from a sorted array" (keep `a[r]` when it differs from `a[w−1]`). The full family of read/write pointer patterns is in [[DSA/Two Pointers|Two Pointers]].

### 5.4 Swap, and why there's no `swap(int a, int b)`

```java
static void swap(int[] a, int i, int j) {
    int t = a[i]; a[i] = a[j]; a[j] = t;
}
```

Java passes primitives by value, so a method `swap(int x, int y)` swaps its own copies and the caller sees nothing. Swapping requires the **array and two indices** (or a mutable holder).

---

## 6. Rotation

<span class="hl-blue">Rotating right by `k`</span> moves every element `k` places to the right, wrapping around: `[1,2,3,4,5,6,7]` rotated right by 3 is `[5,6,7,1,2,3,4]`. Element at index `i` moves to `(i + k) mod n`. Rotating left by `k` is the same as rotating right by `n − k`.

> [!important] Normalize `k` first
> `k` can be larger than `n` (rotating by `n` is the identity) or negative (meaning the other direction). Use `k = Math.floorMod(k, n)`, which is always in `[0, n)`. Plain `k % n` keeps the sign of `k`, so a negative `k` stays negative. Also guard `n == 0` before computing `k mod n` (division by zero).

| Method | Time | Extra space | Notes |
|---|---|---|---|
| Copy into a new array | `O(n)` | `O(n)` | `b[(i + k) % n] = a[i]` |
| Rotate by one, `k` times | `O(n·k)` | `O(1)` | too slow when `k ~ n` |
| **Three reversals** | `O(n)` | `O(1)` | the standard answer |
| Juggling (cycle) | `O(n)` | `O(1)` | `gcd(n, k)` cycles, each element moves once |

### 6.1 Three reversals

Rotating right by `k` = reverse everything, then reverse the first `k`, then reverse the rest.

```
rotateRight(a, k):
    n = len(a); if n == 0: return
    k = k mod n                       -- floor mod: result in [0, n)
    reverse(a, 0, n − 1)
    reverse(a, 0, k − 1)
    reverse(a, k, n − 1)
```

```
[1 2 3 4 5 6 7], k = 3
reverse all      → [7 6 5 4 3 2 1]
reverse [0, 2]   → [5 6 7 | 4 3 2 1]
reverse [3, 6]   → [5 6 7 | 1 2 3 4]   ✓
```

```java
static void rotateRight(int[] a, int k) {
    int n = a.length;
    if (n == 0) return;
    k = Math.floorMod(k, n);       // k > n and negative k both handled
    reverse(a, 0, n - 1);
    reverse(a, 0, k - 1);          // k == 0: reverse(a, 0, -1) does nothing, correct
    reverse(a, k, n - 1);
}
```

**Why it works.** Write the array as `A B`, where `B` is the last `k` elements. We want `B A`. Reversing the whole thing gives `Bᴿ Aᴿ`, and reversing each part separately gives `B A`. For a **left** rotation by `k` (`A` is the first `k`), reverse the two parts first and the whole thing last: `Aᴿ Bᴿ → (Aᴿ Bᴿ)ᴿ = B A`.

### 6.2 Juggling (cyclic replacements)

Follow each element to its destination, carrying the displaced element along, until the cycle returns to its start. There are exactly `gcd(n, k)` cycles, each of length `n / gcd(n, k)`.

```java
static void rotateRightCycles(int[] a, int k) {
    int n = a.length;
    if (n == 0) return;
    k = Math.floorMod(k, n);
    int cycles = gcd(n, k);                 // gcd(n, 0) = n: n trivial cycles of length 1
    for (int start = 0; start < cycles; start++) {
        int cur = start, carried = a[start];
        do {
            int next = (cur + k) % n;
            int tmp = a[next];
            a[next] = carried;
            carried = tmp;
            cur = next;
        } while (cur != start);
    }
}

static int gcd(int a, int b) { return b == 0 ? a : gcd(b, a % b); }
```

> [!info]- Why there are gcd(n, k) cycles
> Starting from `s`, the cycle visits `s, s+k, s+2k, … (mod n)`. It returns to `s` after `t` steps where `t·k ≡ 0 (mod n)`; the smallest such `t` is `n / gcd(n, k)`. So each cycle has `n/g` elements and there are `g = gcd(n, k)` cycles. Starting points `0, 1, …, g−1` are in different cycles because every element of the cycle through `s` is `≡ s (mod g)`. A common bug is to assume a single cycle (true only when `gcd(n, k) = 1`): with `n = 6, k = 2`, starting from 0 visits `0, 2, 4` and stops, leaving half the array unrotated. See [[Math for Algorithms#2. GCD, LCM, and Euclid's Algorithm|Math for Algorithms § 2]].

> [!tip] Library and "virtual" rotation
> - `Collections.rotate(list, k)` rotates a `List` **right** by `k` (negative `k` rotates left), in place.
> - If you only need to **read** the rotated array, don't move anything: the element at rotated position `i` is `a[(i − k) mod n]` for a right rotation. This "offset" view is also how a circular buffer works ([[Queues and Deques|Queues and Deques]]) and how binary search on a rotated sorted array reasons ([[DSA/Binary Search|Binary Search]]).

---

## 7. In-Place Rearrangement Tricks

When the values are themselves valid indices (typically a permutation of `0..n−1` or values in `1..n`), the array can serve as its own hash table. These give `O(n)` time with `O(1)` extra space where the obvious solution needs a `HashSet`.

### 7.1 Cyclic sort: put each value at its "home" index

**First missing positive**: the smallest positive integer not in the array. The answer is in `1..n+1`, so only values in `1..n` matter. Put value `v` at index `v − 1`; then the first index `i` with `a[i] ≠ i + 1` gives the answer.

```
firstMissingPositive(a):
    n = len(a)
    for i = 0 to n − 1:
        while 1 ≤ a[i] ≤ n and a[a[i] − 1] ≠ a[i]:
            swap a[i] with a[a[i] − 1]           -- send a[i] home
    for i = 0 to n − 1:
        if a[i] ≠ i + 1: return i + 1
    return n + 1
```

```java
static int firstMissingPositive(int[] a) {
    int n = a.length;
    for (int i = 0; i < n; i++) {
        while (a[i] >= 1 && a[i] <= n && a[a[i] - 1] != a[i]) {
            int j = a[i] - 1;              // save the target index BEFORE swapping
            int t = a[i]; a[i] = a[j]; a[j] = t;
        }
    }
    for (int i = 0; i < n; i++) {
        if (a[i] != i + 1) return i + 1;
    }
    return n + 1;
}
```

**Why `O(n)` despite the nested `while`:** each swap puts at least one value permanently in its home slot, and there are only `n` slots. So there are at most `n` swaps in total.

> [!warning] Two bugs specific to this pattern
> - **The guard must be `a[a[i] − 1] != a[i]`, not `a[i] != i + 1`.** With duplicates (`[1, 1]`), the second `1` isn't home, but its home already holds a `1`. Swapping the two equal values changes nothing, and the loop spins forever.
> - **Compute the target index once.** `int t = a[i]; a[i] = a[a[i] − 1]; a[a[i] − 1] = t;` reads `a[i]` *after* it has been overwritten, so the second write goes to the wrong slot.

### 7.2 Sign marking

When values are in `1..n` and the array can be modified temporarily, the **sign** of `a[v − 1]` can record "I've seen `v`".

```java
// All values that appear twice, values in 1..n, each appears once or twice
static List<Integer> findDuplicates(int[] a) {
    List<Integer> out = new ArrayList<>();
    for (int i = 0; i < a.length; i++) {
        int v = Math.abs(a[i]);            // a[i] may already have been negated
        if (a[v - 1] < 0) out.add(v);      // seen before
        else a[v - 1] = -a[v - 1];
    }
    return out;
}
```

The same idea, with "add `n` to `a[v−1]`" instead of negating, works when values can be `0`. Restore the array afterwards (`Math.abs` everything) if the caller expects it unchanged.

### 7.3 Next permutation

The lexicographically next arrangement of the array, in place. `[1,2,3] → [1,3,2] → [2,1,3] → … → [3,2,1] → [1,2,3]` (wraps around).

```
nextPermutation(a):
    i = n − 2
    while i ≥ 0 and a[i] ≥ a[i+1]: i = i − 1        -- find the rightmost "ascent"
    if i < 0:
        reverse(a, 0, n − 1); return false           -- was the last permutation
    j = n − 1
    while a[j] ≤ a[i]: j = j − 1                     -- rightmost element larger than a[i]
    swap a[i], a[j]
    reverse(a, i + 1, n − 1)                         -- suffix was descending; make it ascending
    return true
```

```java
static boolean nextPermutation(int[] a) {
    int i = a.length - 2;
    while (i >= 0 && a[i] >= a[i + 1]) i--;
    if (i < 0) {
        reverse(a, 0, a.length - 1);
        return false;
    }
    int j = a.length - 1;
    while (a[j] <= a[i]) j--;
    swap(a, i, j);
    reverse(a, i + 1, a.length - 1);
    return true;
}
```

The suffix after `i` is non-increasing (that's why `i` is the rightmost ascent). Swapping `a[i]` with the smallest larger element in the suffix keeps the suffix non-increasing, and reversing it gives the smallest possible suffix. `O(n)` per call. Starting from the sorted array and calling it until it returns `false` enumerates every **distinct** permutation once, even with duplicates, which is why the comparisons are `>=` and `<=` rather than strict.

> [!example]- Trace: `[1, 5, 8, 4, 7, 6, 5, 3, 1]`
> - Rightmost ascent: `a[3] = 4 < a[4] = 7`, so `i = 3`. The suffix `7 6 5 3 1` is non-increasing.
> - Rightmost element > 4 in the suffix: `5` at index 6. Swap: `[1, 5, 8, 5, 7, 6, 4, 3, 1]`.
> - Reverse the suffix after index 3: `[1, 5, 8, 5, 1, 3, 4, 6, 7]`.

---

## 8. Classic Single-Pass Array Algorithms

### 8.1 Maximum subarray sum (Kadane's algorithm)

Find the contiguous, **non-empty** subarray with the largest sum. Let `cur` be the best sum of a subarray **ending at** `i`. It either extends the best one ending at `i − 1`, or starts fresh at `i`.

```
kadane(a):                            -- a non-empty
    cur = best = a[0]
    for i = 1 to n − 1:
        cur  = max(a[i], cur + a[i])
        best = max(best, cur)
    return best
```

```java
static long maxSubarraySum(int[] a) {
    long cur = a[0], best = a[0];
    for (int i = 1; i < a.length; i++) {
        cur = Math.max(a[i], cur + a[i]);
        best = Math.max(best, cur);
    }
    return best;
}
```

`O(n)`, `O(1)`. It's a one-dimensional DP where only the previous state is kept ([[DSA/Dynamic Programming Fundamentals|Dynamic Programming — Fundamentals]]).

> [!warning] All-negative input
> Starting with `cur = best = 0` (a popular version) returns `0` for `[-3, -1, -2]`. That's the answer only if the **empty** subarray is allowed. If the subarray must be non-empty, initialize from `a[0]`, and the answer is `-1`. Check which one the problem wants.

> [!info]- Variants
> - **Recover the indices:** when `cur` restarts (`a[i] > cur + a[i]`), record `start = i`; when `best` improves, record `(start, i)`.
> - **Maximum product subarray:** keep both the max and the min product ending at `i`, since multiplying by a negative swaps them.
> - **Circular array:** the answer is `max(kadane(a), total − minSubarray(a))`, except when every element is negative, in which case `total − minSubarray` describes the empty subarray, so return `kadane(a)`.

### 8.2 Majority element (Boyer–Moore voting)

Find the element that appears **more than `n/2`** times, in `O(n)` time and `O(1)` space.

```
majority(a):
    candidate = none; count = 0
    for x in a:
        if count == 0: candidate = x
        if x == candidate: count += 1 else count −= 1
    return candidate             -- verify with a second pass unless a majority is guaranteed
```

```java
static int majorityCandidate(int[] a) {
    int candidate = 0, count = 0;
    for (int x : a) {
        if (count == 0) candidate = x;
        count += (x == candidate) ? 1 : -1;
    }
    return candidate;
}
```

**Why it works:** each decrement cancels one candidate occurrence against one different element. A majority element has more occurrences than all other elements combined, so it can't be fully cancelled.

> [!warning] It always returns *something*
> On `[1, 2, 3]` it returns `3`, which isn't a majority. If the problem doesn't guarantee that a majority exists, count the candidate's occurrences in a second pass. The generalization to "elements appearing more than `n/k` times" keeps `k − 1` candidates and counters.

### 8.3 Product of array except self (prefix × suffix)

`out[i]` = product of all elements except `a[i]`, without division (division fails when there's a zero).

```java
static int[] productExceptSelf(int[] a) {
    int n = a.length;
    int[] out = new int[n];
    int prefix = 1;
    for (int i = 0; i < n; i++) {        // out[i] = product of a[0..i-1]
        out[i] = prefix;
        prefix *= a[i];
    }
    int suffix = 1;
    for (int i = n - 1; i >= 0; i--) {   // multiply in product of a[i+1..n-1]
        out[i] *= suffix;
        suffix *= a[i];
    }
    return out;
}
```

`O(n)` time, `O(1)` extra space besides the output. The "answer = something from the left × something from the right" pattern is the multiplicative cousin of prefix sums ([[DSA/Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]]).

### 8.4 Frequency arrays instead of maps

When values lie in a small known range (`0 ≤ v < 10⁶`, lowercase letters, digits), count with `int[] cnt = new int[RANGE]` rather than a `HashMap<Integer,Integer>`. It's the same `O(1)` per operation but with no hashing, no boxing, and much better cache behaviour. When values are large but there are few of them, compress them first ([[DSA/Intervals and Sweep Line|coordinate compression]]) or use a map ([[Hash Tables|Hash Tables]]).

---

## 9. 2D Arrays

### 9.1 Two memory layouts

| Layout | Element `(r, c)` | Used by |
|---|---|---|
| **Row-major** | `base + (r × cols + c) × size` | C, C++, Python (NumPy default), Java's flattened arrays |
| **Column-major** | `base + (c × rows + r) × size` | Fortran, MATLAB, R |

> [!important] Java has no true 2D arrays
> `int[][] g = new int[R][C]` is an array of `R` references, each pointing to a **separate** `int[C]` object. Consequences:
> - Rows can have different lengths (**jagged** arrays): `new int[R][]` creates `R` null rows to fill in yourself.
> - `g[r]` is a whole row you can pass around, swap in `O(1)` (`int[] t = g[0]; g[0] = g[1]; g[1] = t;`), or alias by accident.
> - `g.clone()` copies the row **references**, not the rows (shallow). A deep copy needs a loop of `g[r].clone()`.
> - Each row has its own object header (16 bytes on 64-bit HotSpot), so many short rows waste memory ([[#12. Trick Questions and Special Cases|§12]]).

### 9.2 Traverse in row-major order

```java
long sum = 0;
for (int r = 0; r < R; r++)
    for (int c = 0; c < C; c++)
        sum += g[r][c];          // walks each row array sequentially: cache-friendly
```

Swapping the loops (`c` outer, `r` inner) gives the same result but jumps to a different row array on every access. On a large grid that is often several times slower: a constant factor, invisible in big-O, but enough to turn AC into TLE.

### 9.3 Flattening a grid to 1D

```
id  = r × C + c            -- C = number of COLUMNS
r   = id / C
c   = id % C
```

Useful for storing a cell in one `int` (queues in BFS, union-find over cells, `visited` as a `boolean[R*C]`). Using `R` instead of `C` in any of these three lines is the classic bug; it only shows up on non-square grids.

### 9.4 Transpose and rotate by 90°

| Transform | New position of `(r, c)` in an `n × n` matrix | In place |
|---|---|---|
| Transpose | `(c, r)` | swap across the main diagonal |
| Rotate 90° clockwise | `(c, n − 1 − r)` | transpose, then reverse each row |
| Rotate 90° counter-clockwise | `(n − 1 − c, r)` | transpose, then reverse each column (or reverse each row, then transpose) |
| Rotate 180° | `(n − 1 − r, n − 1 − c)` | reverse each row, then reverse the row order |

```java
static void rotateClockwise(int[][] m) {      // n × n, in place
    int n = m.length;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) {     // j > i: swap each pair once
            int t = m[i][j]; m[i][j] = m[j][i]; m[j][i] = t;
        }
    for (int[] row : m) reverse(row, 0, n - 1);
}
```

> [!warning] Transposing with `j` from `0`
> Looping `j` over `0..n−1` swaps every pair **twice**, which puts everything back where it started. The inner loop must start at `j = i + 1` (or `j = i`, which also swaps the diagonal with itself).

> [!info]- Rotating a non-square `R × C` matrix
> The result is `C × R`, so it can't be done in place in a `R × C` array. Allocate `int[][] res = new int[C][R]` and set `res[c][R − 1 − r] = m[r][c]` for a clockwise rotation.

### 9.5 Spiral order

Shrink four boundaries after each side. The two `if` checks stop a single remaining row or column from being output twice.

```java
static List<Integer> spiralOrder(int[][] m) {
    List<Integer> out = new ArrayList<>();
    if (m.length == 0 || m[0].length == 0) return out;
    int top = 0, bottom = m.length - 1, left = 0, right = m[0].length - 1;
    while (top <= bottom && left <= right) {
        for (int c = left; c <= right; c++) out.add(m[top][c]);
        top++;
        for (int r = top; r <= bottom; r++) out.add(m[r][right]);
        right--;
        if (top <= bottom) {                         // a bottom row still exists
            for (int c = right; c >= left; c--) out.add(m[bottom][c]);
            bottom--;
        }
        if (left <= right) {                         // a left column still exists
            for (int r = bottom; r >= top; r--) out.add(m[r][left]);
            left++;
        }
    }
    return out;
}
```

### 9.6 Diagonals

| Cells with the same… | Lie on a… | Number of them in `R × C` | Key range |
|---|---|---|---|
| `r − c` | main-direction diagonal (↘) | `R + C − 1` | `−(C−1) … R−1` (add `C − 1` to index an array) |
| `r + c` | anti-diagonal (↙) | `R + C − 1` | `0 … R + C − 2` |

This is how N-queens checks attacks in `O(1)` ([[DSA/Backtracking|Backtracking]]) and how "traverse the matrix diagonally" problems group cells.

---

## 10. Grid Techniques

### 10.1 Direction arrays

```java
static final int[] DR = {-1, 0, 1, 0};      // up, right, down, left
static final int[] DC = {0, 1, 0, -1};

for (int d = 0; d < 4; d++) {
    int nr = r + DR[d], nc = c + DC[d];
    if (nr < 0 || nr >= R || nc < 0 || nc >= C) continue;   // bounds FIRST
    if (grid[nr][nc] == '#') continue;
    // ... visit (nr, nc)
}
```

For 8 directions use `DR = {-1,-1,-1,0,0,1,1,1}`, `DC = {-1,0,1,-1,1,-1,0,1}`. For knight moves, list the 8 `(±1, ±2), (±2, ±1)` offsets. With directions ordered clockwise, turning right is `d = (d + 1) % 4` and turning left is `d = (d + 3) % 4` (not `(d − 1) % 4`, which is `−1` when `d = 0`).

> [!tip] Padding instead of bounds checks
> Allocate `(R + 2) × (C + 2)` and put a wall around the border. Every real cell's neighbours then exist, and the bounds check disappears. It's common in simulation problems and Game of Life.

Grids as graphs (BFS/DFS, flood fill, multi-source BFS) are covered in [[DSA/Graph Representations and Traversals|Graph Representations and Traversals]].

### 10.2 Updating a grid in place when new values depend on old ones

In **Game of Life**, every cell's next state depends on its neighbours' **current** state. Overwriting cells as you go corrupts the neighbours that haven't been processed yet. Two standard fixes:

- **Copy** the grid first (`O(RC)` extra space).
- **Encode both states in one cell.** Bit 0 holds the current state, bit 1 the next. Compute every next state into bit 1 while reading only bit 0, then shift every cell right by 1.

```java
static void gameOfLife(int[][] b) {
    int R = b.length, C = b[0].length;
    for (int r = 0; r < R; r++)
        for (int c = 0; c < C; c++) {
            int live = 0;
            for (int dr = -1; dr <= 1; dr++)
                for (int dc = -1; dc <= 1; dc++) {
                    if (dr == 0 && dc == 0) continue;
                    int nr = r + dr, nc = c + dc;
                    if (nr >= 0 && nr < R && nc >= 0 && nc < C) live += b[nr][nc] & 1;  // current state only
                }
            boolean alive = (b[r][c] & 1) == 1;
            if (live == 3 || (alive && live == 2)) b[r][c] |= 2;   // next state in bit 1
        }
    for (int r = 0; r < R; r++)
        for (int c = 0; c < C; c++) b[r][c] >>= 1;
}
```

Bit tricks are in [[03 - Bit Manipulation|Bit Manipulation]].

### 10.3 Set matrix zeroes in O(1) extra space

If any cell is `0`, zero its whole row and column. Recording "row `r` must be zeroed" in a `boolean[R]` costs `O(R + C)`. To get `O(1)`, use the **first row and first column as the markers**, with two extra booleans for whether the first row and first column themselves contained a zero. Then zero the inner cells from the markers, and handle the first row and column **last**, so the markers aren't destroyed before they're read.

---

## 11. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Off-by-one in a loop bound (`i <= a.length`) | `ArrayIndexOutOfBoundsException` | `i < a.length`; for pairs, `i + 1 < a.length` |
| `b = a` to "copy" | changes to `b` show in `a` | `a.clone()` / `Arrays.copyOf` |
| `g.clone()` on a 2D array | rows still shared | clone each row |
| `Arrays.fill(grid, row)` | every row is the same object | allocate each row separately |
| Shifting right with a left-to-right loop | tail filled with copies of one value | loop right-to-left or use `System.arraycopy` |
| `k % n` with negative `k`, or `n == 0` | negative index / `ArithmeticException` | `Math.floorMod(k, n)` after checking `n > 0` |
| Juggling rotation assuming one cycle | only part of the array moves | loop over `gcd(n, k)` starts |
| Summing `int`s into an `int` | silent overflow | accumulate in `long` |
| Kadane initialized with `0` | wrong answer on all-negative input | start from `a[0]` |
| Removing from an `ArrayList` while iterating forward | skipped elements or `ConcurrentModificationException` | `removeIf`, iterator, or a backward loop |
| `list.remove(x)` with an `int x` meaning a value | removes by index | `list.remove(Integer.valueOf(x))` |
| Column-outer loop over a large grid | TLE with a correct algorithm | row-outer loop |
| `r * R + c` when flattening | wrong cell on non-square grids | `r * C + c` |
| `new int[n][2]` for a million pairs | high memory, slow | `new int[2][n]` or two `int[]`s |
| `Integer[]` / `ArrayList<Integer>` where `int[]` would do | 4× memory, slow, `==` bugs | primitives |

---

## 12. Trick Questions and Special Cases

> [!question]- Is `ArrayList.add` O(1)?
> **Amortized** `O(1)`; a single call is `Θ(n)` when it triggers a resize. Over any sequence of `n` appends the total is `O(n)`. But `add(0, x)` (or any `add(i, x)` near the front) is `Θ(n)` every time, because everything shifts. "ArrayList add is O(1)" is true only for appends.

> [!question]- Does removing elements make an `ArrayList` smaller in memory?
> No. `ArrayList` never shrinks its backing array automatically. A list that grew to 10⁶ elements and was then cleared still holds a 10⁶-slot array until you call `trimToSize()` or drop the list.

> [!question]- For-each over an `ArrayList`, remove an element inside the loop. Does it always throw `ConcurrentModificationException`?
> No. Removing the **second-to-last** element doesn't throw:
> ```java
> List<Integer> l = new ArrayList<>(List.of(1, 2, 3));
> for (Integer x : l) if (x == 2) l.remove(x);   // no exception; l = [1, 3]
> ```
> After the removal, `size` drops to 2 and the iterator's cursor is also 2, so `hasNext()` returns `false` and the loop ends before the next `next()` call, which is where the modification check happens. The last element is silently never visited. The behaviour is a "fail-fast, best effort" check, not a guarantee, so never rely on either outcome.

> [!question]- `int[][] grid = new int[3][3]; Arrays.fill(grid, 0);` — what happens?
> It compiles (an `int[][]` is an `Object[]`, so the `fill(Object[], Object)` overload applies and `0` is boxed to `Integer`), then throws **`ArrayStoreException`** at run time: an `Integer` can't be stored in an array whose element type is `int[]`. To fill a 2D array, loop over rows: `for (int[] row : grid) Arrays.fill(row, 0);`.

> [!question]- `int[][] g = new int[3][]; g[0][0] = 1;` — what happens?
> `NullPointerException`. Only the outer array was created; its three slots are `null` until you assign `g[0] = new int[...]`.

> [!question]- Memory: `new int[1_000_000][2]` vs. `new int[2][1_000_000]`?
> Roughly **28 MB vs. 8 MB** on 64-bit HotSpot. The first creates a million row objects, each with a 16-byte header plus 8 bytes of data, plus 4 bytes per reference in the outer array. The second creates two large rows. When storing many pairs (edges, points), use `int[2][n]` or two parallel arrays; it's also faster to allocate and scan.

> [!question]- Rotate an array of length 7 right by 10. What's the result?
> The same as rotating by `10 mod 7 = 3`. Rotation by `n` is the identity, so only `k mod n` matters. And rotating by `−3` equals rotating by `4` (`Math.floorMod(-3, 7) = 4`), not by `−3 % 7 = −3`.

> [!question]- Can you rotate in O(n) time and O(1) space if `k` and `n` share a factor?
> Yes, with three reversals (which don't care about `gcd`) or with juggling over `gcd(n, k)` separate cycles. The juggling version is only wrong if it assumes a single cycle.

> [!question]- Kadane's algorithm on `[-5, -2, -9]`?
> `-2`, if the subarray must be non-empty. A version that initializes `best = 0` returns `0`, which is only correct if the empty subarray is allowed.

> [!question]- Why does `firstMissingPositive` with guard `a[i] != i + 1` hang on `[1, 1]`?
> At `i = 1`, `a[1] = 1 ≠ 2`, so it tries to send `1` to index 0. Index 0 already holds `1`, the swap exchanges two equal values, nothing changes, and the loop repeats forever. The guard must ask whether the **destination** already holds the right value: `a[a[i] − 1] != a[i]`.

> [!question]- Is the nested-while cyclic sort O(n²)?
> No, it's `O(n)`. The `while` doesn't run `n` times for each `i`: every swap fixes one value permanently in its home slot, so there are at most `n` swaps across the whole run. This is an aggregate (amortized) argument, like the two-pointer case in [[01 - Complexity Analysis#4.6 Two pointers — a nested loop that isn't quadratic|Complexity Analysis § 4.6]].

> [!question]- Merge two sorted arrays where the first has enough trailing space for both. How, in place?
> Fill from the **back**. Compare the largest remaining elements of each, write the larger at the end of the first array, and move left. Filling from the front would overwrite elements of the first array that haven't been read yet. When the second array runs out, stop: the rest of the first array is already in place. See [[DSA/Two Pointers|Two Pointers]].

> [!question]- Product of array except self: what if the array contains zeros?
> The prefix × suffix method handles them with no special case. The division method (`total / a[i]`) fails: with one zero, every other position should be `0` but the zero's own position should be the product of the rest; with two zeros, everything is `0`. Division would also divide by zero.

> [!question]- `List<Integer>[] adj = new ArrayList<Integer>[n];` — does it compile?
> No: "generic array creation". Arrays need their exact element type at run time and generics are erased ([[Java/05 - Working with Data and Errors/02 - Generics#7.2 What Erasure Forbids|Java: Generics § 7.2]]). The standard workaround is `List<Integer>[] adj = new ArrayList[n];` (an unchecked warning, safe as long as you only put `ArrayList<Integer>`s in it), then initialize each slot in a loop. The alternative is `List<List<Integer>> adj = new ArrayList<>();`.

> [!question]- Is accessing `a[i]` really O(1) regardless of `i`?
> In the RAM model, yes. In real hardware, a sequential access pattern is much faster than a random one because of caching and prefetching. Both are `O(1)` per access, but a random-access loop over a 10⁸-element array can be an order of magnitude slower than a sequential one. Big-O hides constants, and memory access patterns are the biggest constant there is.

> [!question]- Does `Arrays.sort(int[])` always run in O(n log n)?
> On JDK 14 and later, yes: the dual-pivot quicksort falls back to heap sort if recursion gets too deep. On older JDKs (8, 11) it was a plain dual-pivot quicksort with an `O(n²)` worst case, and Codeforces "anti-Java-sort" tests exploited it. On a judge running an old JDK, shuffle the array before sorting, or sort an `Integer[]` (TimSort, guaranteed `O(n log n)`). See [[DSA/Sorting Algorithms|Sorting Algorithms]].

---

## 13. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `ArrayList.add(x)` | `O(1)` amortized, `Θ(n)` worst | occasional 1.5× resize |
| `ArrayList.add(0, x)` | `Θ(n)` every time | shifts everything |
| `new ArrayList<>()` capacity | 0, then 10 on first add | lazy allocation |
| `ArrayList` after `clear()` | same capacity | never shrinks automatically |
| Growth by `+c` instead of `×g` | `Θ(n)` per append | arithmetic, not geometric, series |
| Shrink at ½ full | thrashing, `Θ(n)` per op | shrink at ¼ instead |
| `-3 % 7` | `-3` | remainder keeps the sign of the dividend |
| `Math.floorMod(-3, 7)` | `4` | result in `[0, 7)` |
| Rotate right by `k` | reverse all, reverse `[0,k)`, reverse `[k,n)` | `AB → BᴿAᴿ → BA` |
| Juggling cycles | `gcd(n, k)` | each cycle has `n / gcd` elements |
| `Arrays.fill(int2D, 0)` | `ArrayStoreException` | `Integer` stored into `int[][]` |
| `new int[3][]` then `g[0][0]` | `NullPointerException` | rows not created |
| `g.clone()` on `int[][]` | rows shared | shallow copy |
| `new int[1e6][2]` vs `new int[2][1e6]` | ≈ 28 MB vs ≈ 8 MB | per-row object header |
| `Arrays.asList(intArr).size()` | `1` | `List<int[]>` |
| `Arrays.asList(...).add(x)` | `UnsupportedOperationException` | fixed-size view |
| Remove 2nd-to-last in for-each | no exception, last element skipped | `hasNext()` is false first |
| `list.remove(1)` on `List<Integer>` | removes index 1 | `remove(int)` overload |
| Kadane with `best = 0` on all-negative | `0` | only right if empty subarray allowed |
| Cyclic sort | `O(n)` total | each swap fixes one value |
| Transpose with `j` from `0` | matrix unchanged | every pair swapped twice |
| Clockwise rotation, `n × n` | transpose + reverse rows | `(r, c) → (c, n−1−r)` |
| Flatten `(r, c)` | `r * C + c` | `C` = columns |
| `(d − 1) % 4` for `d = 0` | `-1` | use `(d + 3) % 4` |

---

## 14. Summary

- An array is a contiguous block: `O(1)` access by index, `O(n)` insert/delete in the middle (shifting), and excellent cache behaviour for sequential scans.
- A **dynamic array** separates capacity from size, grows by a **factor**, and shrinks at **¼ full**, giving `O(1)` amortized appends. Java's `ArrayList` grows by 1.5× and never shrinks on its own.
- In-place building blocks: shift (in the right direction), reverse, swap, and the **write-pointer** filter.
- **Rotation**: normalize with `floorMod`, then three reversals. Juggling needs `gcd(n, k)` cycles.
- When values are valid indices, the array can be its own hash table: **cyclic sort** and **sign marking** give `O(n)` time and `O(1)` space.
- Single-pass classics: **Kadane** (watch the all-negative case), **Boyer–Moore** majority (verify if not guaranteed), **prefix × suffix** products, **next permutation**.
- Java 2D arrays are arrays of rows: jagged, shallow-cloned, header-per-row. Traverse row-major, flatten with `r * C + c`, and use direction arrays for grids.

## Related

- [[DSA/00 - Syllabus|00 - Syllabus]]
- Previous: [[Math for Algorithms|Math for Algorithms]] · Next: [[Strings|Strings]]
- [[Java/02 - Control Flow/03 - Arrays|Java: Arrays]]: syntax, `java.util.Arrays`, copying, multidimensional arrays
- [[01 - Complexity Analysis#8. Amortized Analysis|Complexity Analysis § 8]]: amortized analysis of dynamic arrays
- [[DSA/Two Pointers|Two Pointers]]: read/write pointers, merging, partitioning
- [[DSA/Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]]: range queries on arrays
- [[DSA/Binary Search|Binary Search]]: searching sorted and rotated arrays
- [[Hash Tables|Hash Tables]]: when a frequency array isn't enough
- [[DSA/Graph Representations and Traversals|Graph Representations and Traversals]]: grids as graphs
