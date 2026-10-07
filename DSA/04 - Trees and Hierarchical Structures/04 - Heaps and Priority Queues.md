# Heaps and Priority Queues

A <span class="hl-blue">priority queue</span> is a collection where you can add elements in any order and always remove the **smallest** (or largest) one next. A <span class="hl-blue">binary heap</span> is the standard way to implement it: a complete binary tree stored in an array, where every parent is `≤` its children. That one rule makes the minimum available in `O(1)` and insertion and removal `O(log n)`, without keeping everything sorted.

Heaps solve a recognisable family of problems: "the `k` largest", "the next event to happen", "merge `k` sorted streams", "the running median", "always combine the two cheapest", and they're the engine of Dijkstra's and Prim's algorithms. This note covers the heap property and array layout, sift-up and sift-down, `O(n)` heap construction, Java's `PriorityQueue` and its traps, top-`k`, `k`-way merge, two-heap, and greedy scheduling patterns, lazy deletion, and indexed heaps with decrease-key.

## Contents

- [[#1. The Heap Property|1. The Heap Property]]
- [[#2. Heap Operations|2. Heap Operations]]
- [[#3. Building a Heap in O(n)|3. Building a Heap in O(n)]]
- [[#4. PriorityQueue in Java|4. PriorityQueue in Java]]
- [[#5. Top-k Problems|5. Top-k Problems]]
- [[#6. K-Way Merge|6. K-Way Merge]]
- [[#7. Two Heaps|7. Two Heaps]]
- [[#8. Greedy Scheduling with Heaps|8. Greedy Scheduling with Heaps]]
- [[#9. Lazy Deletion and Indexed Heaps|9. Lazy Deletion and Indexed Heaps]]
- [[#10. Common Mistakes|10. Common Mistakes]]
- [[#11. Trick Questions and Special Cases|11. Trick Questions and Special Cases]]
- [[#12. Quick Reference — Non-Obvious Outcomes|12. Quick Reference — Non-Obvious Outcomes]]
- [[#13. Summary|13. Summary]]

---

## 1. The Heap Property

> [!note] Definition
> A **min-heap** is a complete binary tree in which every node's key is `≤` the keys of its children. A **max-heap** uses `≥`. Consequently:
> - the root holds the minimum (maximum);
> - every root-to-leaf path is sorted;
> - **nothing** is said about the order between siblings or cousins.

Because the tree is complete ([[DSA/04 - Trees and Hierarchical Structures/01 - Binary Trees#1.1 Shapes|Binary Trees § 1.1]]), it's stored in an array in level order, with no pointers:

| 0-based index `i` | Formula |
|---|---|
| left child | `2i + 1` |
| right child | `2i + 2` |
| parent | `(i − 1) / 2` |
| last internal node | `n/2 − 1` |
| leaves | indices `n/2 … n − 1` |

![[Heaps - Array Layout.excalidraw|800]]

The height is `⌊log₂ n⌋`, so any walk from the root to a leaf or back takes `O(log n)` steps.

> [!warning] A heap is not a sorted array
> `[1, 3, 2, 7, 4, 5, 6]` is a valid min-heap: every parent is smaller than its children. But it isn't sorted, and its inorder, level-order, and array orders are all different from sorted order. A heap answers exactly one question fast, "what's the minimum?". Searching for an arbitrary value is `O(n)`. (A sorted array **is** always a valid min-heap.)

| Operation | Binary heap | Sorted array | Unsorted array | Balanced BST |
|---|---|---|---|---|
| Peek min | `O(1)` | `O(1)` | `O(n)` | `O(log n)` |
| Insert | `O(log n)` | `O(n)` | `O(1)` | `O(log n)` |
| Extract min | `O(log n)` | `O(1)` (from the end of a descending array) | `O(n)` | `O(log n)` |
| Build from `n` elements | `O(n)` | `O(n log n)` | `O(1)` | `O(n log n)` |
| Remove an arbitrary element | `O(n)` find + `O(log n)` | `O(n)` | `O(n)` | `O(log n)` |
| Peek max **and** min | no | yes | no | yes |

A heap beats a balanced BST when only one end is needed: it's an array (cache-friendly, no node objects), builds in linear time, and has smaller constants.

---

## 2. Heap Operations

Two repair procedures do all the work:

- **sift up**: an element that's smaller than its parent swaps with it, repeatedly, until it isn't.
- **sift down**: an element that's larger than its smaller child swaps with that child, repeatedly, until it isn't (or it's a leaf).

```
push(x):
    a[n] = x; n = n + 1
    siftUp(n − 1)

pop():                                  -- remove and return the minimum
    top = a[0]
    n = n − 1; a[0] = a[n]              -- move the last element to the root
    siftDown(0)
    return top

siftUp(i):
    while i > 0 and a[parent(i)] > a[i]:
        swap(a[i], a[parent(i)]); i = parent(i)

siftDown(i):
    loop:
        s = index of the smallest of a[i], a[left(i)], a[right(i)]   -- children that exist
        if s = i: return
        swap(a[i], a[s]); i = s
```

![[Heaps - Sift Down After Extract.excalidraw|800]]

```java
static class MinHeap {
    private int[] a = new int[16];
    private int n = 0;

    void push(int x) {
        if (n == a.length) a = Arrays.copyOf(a, 2 * n);   // grow like ArrayList
        a[n] = x;
        siftUp(n++);
    }

    int peek() {
        if (n == 0) throw new NoSuchElementException();
        return a[0];
    }

    int pop() {
        if (n == 0) throw new NoSuchElementException();
        int top = a[0];
        a[0] = a[--n];                             // last element to the root
        siftDown(0);
        return top;
    }

    int size() { return n; }

    private void siftUp(int i) {
        while (i > 0) {
            int p = (i - 1) / 2;
            if (a[p] <= a[i]) return;
            swap(i, p);
            i = p;
        }
    }

    private void siftDown(int i) {
        while (true) {
            int s = i, l = 2 * i + 1, r = l + 1;
            if (l < n && a[l] < a[s]) s = l;
            if (r < n && a[r] < a[s]) s = r;   // s: the smallest of the three
            if (s == i) return;
            swap(i, s);
            i = s;
        }
    }

    private void swap(int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }
}
```

> [!warning] Sift down must pick the **smaller** child
> Swapping with the left child by default (or with the first child that's smaller than the parent) can move a larger value above a smaller sibling: with parent `9` and children `3` and `1`, swapping `9` with `3` makes `3` the parent of `1`. Always compare both children first, and check that each child index is `< n`.

Other operations built from the two:

| Operation | How | Cost |
|---|---|---|
| `replace` / pop-then-push | overwrite `a[0]` with the new value, sift down | one sift instead of two |
| `pushpop` (push, then pop) | if the new value is `≤ a[0]`, return it directly; otherwise replace | |
| Decrease a key at slot `i` (min-heap) | set it, sift up | `O(log n)`, but needs `i` ([[#9.2 Indexed priority queue with decrease-key (advanced)|§9.2]]) |
| Increase a key at slot `i` | set it, sift down | `O(log n)` |
| Remove slot `i` | move the last element to `i`, then sift up **or** down (whichever applies) | `O(log n)` |

> [!example]- Why removing slot `i` may need a sift **up**
> Min-heap `[1, 10, 2, 11, 12, 3, 4]`; remove index 4 (`12`). The last element, `4`, moves into index 4, whose parent is `10`. Now `4 < 10`, so it must sift **up**, not down. Code that always sifts down after a removal leaves `4` below `10` and breaks the heap. (`PriorityQueue.removeAt` handles both directions.)

**Max-heaps**: flip every comparison, or in Java pass a reversed comparator ([[#4. PriorityQueue in Java|§4]]). For heap sort, which uses an in-place max-heap, see [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms#5. Heap Sort|Sorting Algorithms § 5]].

---

## 3. Building a Heap in O(n)

Inserting `n` elements one at a time costs `O(n log n)`. Instead, put them all in the array and sift down every internal node, **from the last one back to the root**:

```
heapify(a):
    for i = n/2 − 1 down to 0: siftDown(i)
```

```java
static void heapify(int[] a) {                     // min-heap, in place
    for (int i = a.length / 2 - 1; i >= 0; i--) siftDownMin(a, i, a.length);
}

static void siftDownMin(int[] a, int i, int n) {
    while (true) {
        int s = i, l = 2 * i + 1, r = l + 1;
        if (l < n && a[l] < a[s]) s = l;
        if (r < n && a[r] < a[s]) s = r;
        if (s == i) return;
        int t = a[i]; a[i] = a[s]; a[s] = t;
        i = s;
    }
}
```

Going backwards guarantees that when node `i` is sifted, both of its subtrees are already heaps, so one sift down makes the subtree at `i` a heap. The leaves (the second half of the array) are one-element heaps already, which is why the loop starts at `n/2 − 1`.

![[Heaps - Build Heap Cost.excalidraw|800]]

**Why `O(n)`**: a sift down from a node of height `h` costs at most `h` swaps, and at most `⌈n / 2^(h+1)⌉` nodes have height `h`. Half the nodes are leaves (cost 0), a quarter have height 1 (cost ≤ 1), an eighth height 2, and so on:

`Σ h · n / 2^(h+1) = (n/2) · Σ h / 2^h = (n/2) · 2 = n`.

Most nodes are near the bottom, where sifting **down** is cheap. Building by sift-**up** inserts is slow for the opposite reason: most nodes are near the bottom, where sifting **up** is expensive.

> [!tip] In Java
> `new PriorityQueue<>(collection)` heapifies in `O(n)`. `pq.addAll(collection)` and a loop of `offer` calls cost `O(n log n)`. For top-`k` over a large array, heapifying all of it and polling `k` times costs `O(n + k log n)`.

---

## 4. PriorityQueue in Java

`java.util.PriorityQueue<E>` is a binary **min**-heap ordered by natural order or by a `Comparator`.

| Method | Cost | On an empty queue |
|---|---|---|
| `offer(e)` / `add(e)` | `O(log n)` | |
| `peek()` | `O(1)` | `null` |
| `element()` | `O(1)` | throws `NoSuchElementException` |
| `poll()` | `O(log n)` | `null` |
| `remove()` | `O(log n)` | throws `NoSuchElementException` |
| `remove(Object o)` | **`O(n)`** (linear search) | `false` |
| `contains(Object o)` | **`O(n)`** | `false` |
| `size()`, `isEmpty()`, `clear()` | `O(1)` / `O(1)` / `O(n)` | |
| `new PriorityQueue<>(collection)` | `O(n)` heapify | |
| iteration, `toString()`, `toArray()` | `O(n)`, in **array order, not sorted** | |

```java
PriorityQueue<Integer> min = new PriorityQueue<>();
PriorityQueue<Integer> max = new PriorityQueue<>(Collections.reverseOrder());
PriorityQueue<int[]> byFirst = new PriorityQueue<>((x, y) -> Integer.compare(x[0], y[0]));
PriorityQueue<int[]> byFirstThenSecond = new PriorityQueue<>(
        Comparator.<int[]>comparingInt(x -> x[0]).thenComparingInt(x -> x[1]));
PriorityQueue<String> byLength = new PriorityQueue<>(Comparator.comparingInt(String::length));
```

> [!warning] The `PriorityQueue` traps
> - **Printing or iterating isn't sorted.** `toString()` shows the internal array: after offering `5, 1, 4, 2, 3`, it prints `[1, 2, 4, 5, 3]`. To see the elements in order, `poll` them (destructively) or sort a copy.
> - **`(a, b) -> b - a` overflows.** For a max-heap holding `Integer.MIN_VALUE` and `1`, `MIN_VALUE − 1` wraps to a positive number, so `MIN_VALUE` is treated as the larger. Use `Collections.reverseOrder()` or `(a, b) -> Integer.compare(b, a)`.
> - **Changing an element's priority while it's inside** (mutating a field the comparator reads) silently breaks the heap: nothing re-sifts it. Remove it, change it, and re-insert it, or use lazy deletion ([[#9.1 Lazy deletion|§9.1]]).
> - **`int x = pq.poll();`** throws `NullPointerException` on an empty queue (unboxing `null`).
> - **Ties are not FIFO.** Equal-priority elements come out in no particular order. If arrival order matters, add a sequence number as the tiebreaker.
> - **No comparator and a non-`Comparable` type** (`PriorityQueue<int[]>`): the first `offer` throws `ClassCastException`, not the constructor.
> - **`new PriorityQueue<>(0)`** throws `IllegalArgumentException`: the initial capacity must be at least 1.
> - **`null` elements** are rejected with `NullPointerException`.

---

## 5. Top-k Problems

### 5.1 The k largest: a min-heap of size k

Keep the `k` largest elements seen so far in a **min**-heap. Its root is the smallest of them, the `k`-th largest so far, and it's exactly the element to evict when something larger arrives.

```
kthLargest(a, k):
    heap = empty min-heap
    for x in a:
        push x
        if size > k: pop                -- evict the smallest of the k + 1
    return peek                         -- the k-th largest
```

```java
static int findKthLargest(int[] a, int k) {
    PriorityQueue<Integer> pq = new PriorityQueue<>();     // min-heap of the k largest so far
    for (int x : a) {
        pq.offer(x);
        if (pq.size() > k) pq.poll();
    }
    return pq.peek();
}
```

`[3, 2, 1, 5, 6, 4]`, `k = 2` → `5`; `[3, 2, 3, 1, 2, 4, 5, 5, 6]`, `k = 4` → `4` (duplicates count separately). `O(n log k)` time and `O(k)` space, and it works on a **stream** where `n` is unknown or unbounded.

> [!tip] Which heap for which end?
> The `k` **largest** → **min**-heap of size `k`. The `k` **smallest** → **max**-heap of size `k`. The heap's root is the element on the **border** of the kept set, the one to throw out next. Using a max-heap for the `k` largest means keeping all `n` elements and popping `k` times.

| Approach | Time | Space | Notes |
|---|---|---|---|
| Sort, take `k` | `O(n log n)` | `O(1)`–`O(n)` | simplest |
| Min-heap of size `k` | `O(n log k)` | `O(k)` | streaming; best when `k ≪ n` |
| Heapify all, poll `k` | `O(n + k log n)` | `O(n)` | |
| Quickselect | `O(n)` average, `O(n²)` worst | `O(1)` | modifies the array; not streaming ([[DSA/06 - Algorithm Design Paradigms/02 - Divide and Conquer|Divide and Conquer]]) |
| Counting / buckets | `O(n + range)` | `O(range)` | small integer ranges |

### 5.2 k-th largest in a stream

```java
static class KthLargest {
    private final int k;
    private final PriorityQueue<Integer> pq = new PriorityQueue<>();

    KthLargest(int k, int[] nums) {
        this.k = k;
        for (int x : nums) add(x);
    }

    int add(int x) {
        pq.offer(x);
        if (pq.size() > k) pq.poll();
        return pq.peek();
    }
}
```

`k = 3`, initial `[4, 5, 8, 2]`; `add(3)` → `4`, `add(5)` → `5`, `add(10)` → `5`, `add(9)` → `8`, `add(4)` → `8`. The initial array can have fewer than `k` elements; the constructor must not assume otherwise.

### 5.3 Top k frequent elements

Count with a hash map, then keep the `k` most frequent entries in a min-heap ordered by count:

```java
static int[] topKFrequent(int[] a, int k) {
    Map<Integer, Integer> freq = new HashMap<>();
    for (int x : a) freq.merge(x, 1, Integer::sum);
    PriorityQueue<Map.Entry<Integer, Integer>> pq =
            new PriorityQueue<>((e1, e2) -> Integer.compare(e1.getValue(), e2.getValue()));
    for (Map.Entry<Integer, Integer> e : freq.entrySet()) {
        pq.offer(e);
        if (pq.size() > k) pq.poll();              // drop the least frequent
    }
    int[] res = new int[k];
    for (int i = k - 1; i >= 0; i--) res[i] = pq.poll().getKey();   // most frequent first
    return res;
}
```

`[1, 1, 1, 2, 2, 3]`, `k = 2` → `[1, 2]`. `O(n + m log k)` for `m` distinct values. A **bucket sort** by frequency is `O(n)`: frequencies are between 1 and `n`, so make `n + 1` buckets and read them from the top. For "top `k` frequent **words**" with ties broken alphabetically, the comparator must reverse the tie-break inside a min-heap: smaller count first, and for equal counts the alphabetically **larger** word first (it's the one to evict).

### 5.4 k closest points

```java
static int[][] kClosest(int[][] pts, int k) {
    PriorityQueue<int[]> pq = new PriorityQueue<>((p, q) -> Long.compare(dist2(q), dist2(p)));  // max-heap
    for (int[] p : pts) {
        pq.offer(p);
        if (pq.size() > k) pq.poll();              // drop the farthest
    }
    return pq.toArray(new int[0][]);
}

static long dist2(int[] p) { return (long) p[0] * p[0] + (long) p[1] * p[1]; }
```

Compare **squared** distances: `Math.sqrt` is slower and introduces rounding, and with coordinates up to `10⁴` the squares fit in `int` but sums of products of larger coordinates don't, hence `long`. The result comes out in heap order, not sorted by distance.

---

## 6. K-Way Merge

Merging `k` sorted sequences: the next output is the smallest of the `k` current heads. A min-heap of the heads gives it in `O(log k)`; after taking one, push its successor from the same sequence.

```
mergeK(lists):
    heap = min-heap of (head value, list id, position) for each non-empty list
    while heap not empty:
        (v, i, j) = pop; output v
        if list i has an element at j + 1: push (lists[i][j + 1], i, j + 1)
```

```java
static List<Integer> mergeKSorted(int[][] arrays) {
    PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(e -> e[0]));  // {value, array, index}
    for (int i = 0; i < arrays.length; i++)
        if (arrays[i].length > 0) pq.offer(new int[]{arrays[i][0], i, 0});   // skip empty arrays
    List<Integer> out = new ArrayList<>();
    while (!pq.isEmpty()) {
        int[] e = pq.poll();
        out.add(e[0]);
        int i = e[1], j = e[2] + 1;
        if (j < arrays[i].length) pq.offer(new int[]{arrays[i][j], i, j});
    }
    return out;
}
```

`O(N log k)` for `N` elements in total: better than merging the lists one after another (`O(N k)`), and the same as pairwise divide-and-conquer merging. The linked-list version is in [[DSA/02 - Linear Data Structures/03 - Linked Lists|Linked Lists]]. External sorting of files too large for memory uses exactly this: sort chunks, then `k`-way merge them.

### 6.1 Problems with the same shape

**k-th smallest in a row- and column-sorted matrix**: each row is a sorted list. Push the first element of each row, then pop `k − 1` times, pushing each popped element's right neighbour.

```java
static int kthSmallestMatrix(int[][] m, int k) {
    PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(e -> m[e[0]][e[1]]));  // {row, col}
    for (int r = 0; r < Math.min(m.length, k); r++) pq.offer(new int[]{r, 0});   // rows below k can't matter
    for (int i = 0; i < k - 1; i++) {
        int[] e = pq.poll();
        if (e[1] + 1 < m[e[0]].length) pq.offer(new int[]{e[0], e[1] + 1});
    }
    int[] e = pq.peek();
    return m[e[0]][e[1]];
}
```

`[[1, 5, 9], [10, 11, 13], [12, 13, 15]]`, `k = 8` → `13`. `O(k log min(n, k))`. Binary search on the **value** with a staircase count is `O(n log(max − min))` and better for large `k` ([[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]]).

**Smallest range covering one element from each of `k` lists**: the heap holds one element per list; the range is `[heap min, current max]`. Advance the list that holds the minimum (the only move that can shrink the range), and stop when any list runs out.

```java
static int[] smallestRange(int[][] lists) {
    PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(e -> lists[e[0]][e[1]]));  // {list, idx}
    int max = Integer.MIN_VALUE;
    for (int i = 0; i < lists.length; i++) {
        pq.offer(new int[]{i, 0});
        max = Math.max(max, lists[i][0]);
    }
    int bestLo = 0, bestHi = 0;
    long bestWidth = Long.MAX_VALUE;
    while (true) {
        int[] e = pq.poll();
        int min = lists[e[0]][e[1]];
        if ((long) max - min < bestWidth) { bestWidth = (long) max - min; bestLo = min; bestHi = max; }
        if (e[1] + 1 == lists[e[0]].length) break;     // this list is exhausted: no further range covers it
        int next = lists[e[0]][e[1] + 1];
        max = Math.max(max, next);
        pq.offer(new int[]{e[0], e[1] + 1});
    }
    return new int[]{bestLo, bestHi};
}
```

`[[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]` → `[20, 24]`. The width is computed in `long`: `max − min` overflows `int` for values near both extremes.

Other `k`-way-merge problems: **`k` pairs with the smallest sums** from two sorted arrays (the heap holds pairs `(i, j)`; after popping `(i, j)`, push `(i, j + 1)`), and **ugly numbers / super ugly numbers** (merge the sequences `2·u`, `3·u`, `5·u`, skipping duplicates).

---

## 7. Two Heaps

### 7.1 Median of a stream

Split the numbers into a **lower half** in a max-heap and an **upper half** in a min-heap, keeping the sizes equal or the lower half one larger. The median is then at the top of one or both heaps.

```
addNum(x):
    push x into lo (max-heap)
    move lo's maximum into hi            -- keeps every element of lo ≤ every element of hi
    if hi.size > lo.size: move hi's minimum back into lo

median:
    if lo.size > hi.size: lo.top
    else: (lo.top + hi.top) / 2
```

```java
static class MedianFinder {
    private final PriorityQueue<Integer> lo = new PriorityQueue<>(Collections.reverseOrder());  // smaller half
    private final PriorityQueue<Integer> hi = new PriorityQueue<>();                            // larger half

    void addNum(int x) {
        lo.offer(x);
        hi.offer(lo.poll());                       // the largest of the lower half moves up
        if (hi.size() > lo.size()) lo.offer(hi.poll());
    }

    double findMedian() {
        if (lo.size() > hi.size()) return lo.peek();
        return ((long) lo.peek() + hi.peek()) / 2.0;    // long: the sum can overflow int
    }
}
```

![[Heaps - Two Heap Median.excalidraw|800]]

`O(log n)` per insertion and `O(1)` per query. Adding `1, 2` → `1.5`; then `3` → `2`. The "push to `lo`, then move `lo`'s top to `hi`" step looks wasteful, but it's what keeps the halves correctly split without comparing `x` to anything: `x` lands in the right half automatically.

> [!warning] Two overflow traps in the median
> `(lo.peek() + hi.peek()) / 2.0` unboxes to `int` and adds **before** converting to `double`: `2147483647 + 2147483647` wraps to `−2`, and the "median" is `−1.0`. Cast one operand to `long` (or `double`) first. And `/ 2` (integer division) instead of `/ 2.0` silently truncates `1.5` to `1`.

### 7.2 Sliding window median

The window loses its oldest element at each step, and `PriorityQueue.remove(Object)` is `O(k)`. Instead, use **lazy deletion** ([[#9.1 Lazy deletion|§9.1]]): leave expired elements in the heaps, keep separate counts of **valid** elements, and discard expired ones only when they reach a top. Storing **indices** (ordered by value, then index) makes every element distinct, so "is this top expired?" is simply `index < windowStart`.

```java
static double[] medianSlidingWindow(int[] a, int k) {
    Comparator<Integer> byValue = (x, y) -> a[x] != a[y] ? Integer.compare(a[x], a[y]) : Integer.compare(x, y);
    PriorityQueue<Integer> lo = new PriorityQueue<>(byValue.reversed());   // indices of the lower half
    PriorityQueue<Integer> hi = new PriorityQueue<>(byValue);              // indices of the upper half
    boolean[] inLo = new boolean[a.length];
    int loValid = 0, hiValid = 0;
    double[] res = new double[a.length - k + 1];
    for (int i = 0; i < a.length; i++) {
        int start = i - k + 1;                                 // the window is a[start..i]
        if (start > 0) {                                       // index start − 1 just left the window
            if (inLo[start - 1]) loValid--; else hiValid--;
            prune(lo, start);
            prune(hi, start);
        }
        if (!lo.isEmpty() && byValue.compare(i, lo.peek()) < 0) { lo.offer(i); inLo[i] = true; loValid++; }
        else { hi.offer(i); hiValid++; }
        while (loValid > hiValid + 1) {                        // rebalance the VALID counts
            int x = lo.poll(); hi.offer(x); inLo[x] = false; loValid--; hiValid++;
            prune(lo, start);
        }
        while (hiValid > loValid) {
            int x = hi.poll(); lo.offer(x); inLo[x] = true; hiValid--; loValid++;
            prune(hi, start);
        }
        if (start >= 0)
            res[start] = k % 2 == 1 ? a[lo.peek()] : ((long) a[lo.peek()] + a[hi.peek()]) / 2.0;
    }
    return res;
}

static void prune(PriorityQueue<Integer> pq, int start) {
    while (!pq.isEmpty() && pq.peek() < start) pq.poll();   // expired indices at the top
}
```

`[1, 3, -1, -3, 5, 3, 6, 7]`, `k = 3` → `[1, -1, -1, 3, 5, 6]`. `O(n log n)`: each index is pushed and popped a bounded number of times. The heaps can hold up to `O(n)` expired indices, buried below the tops; that's the memory price of lazy deletion. The `TreeSet`-of-indices version removes exactly in `O(log k)` ([[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees#7.2 Patterns|Balanced Trees § 7.2]]); the array-based version of this problem is in [[DSA/03 - Sorting and Searching/04 - Sliding Window|Sliding Window]].

### 7.3 Two heaps with different keys: IPO

Start with capital `w`; each project needs capital `c[i]` to start and adds profit `p[i]`; do at most `k` projects. Sort the projects by capital; as `w` grows, move every newly affordable project into a **max-heap by profit**, and always take the most profitable affordable one.

```java
static int findMaximizedCapital(int k, int w, int[] profits, int[] capital) {
    int n = profits.length;
    int[][] proj = new int[n][];
    for (int i = 0; i < n; i++) proj[i] = new int[]{capital[i], profits[i]};
    Arrays.sort(proj, Comparator.comparingInt(p -> p[0]));         // by required capital
    PriorityQueue<Integer> affordable = new PriorityQueue<>(Collections.reverseOrder());  // profits
    for (int done = 0, j = 0; done < k; done++) {
        while (j < n && proj[j][0] <= w) affordable.offer(proj[j++][1]);
        if (affordable.isEmpty()) break;           // nothing affordable: stuck
        w += affordable.poll();
    }
    return w;
}
```

`k = 2`, `w = 0`, `profits = [1, 2, 3]`, `capital = [0, 1, 1]` → `4`. The sorted array acts as the second "heap" (a pointer into it), feeding the max-heap as the threshold rises.

---

## 8. Greedy Scheduling with Heaps

Many greedy algorithms ([[DSA/06 - Algorithm Design Paradigms/01 - Greedy Algorithms|Greedy Algorithms]]) repeatedly need "the cheapest", "the earliest-ending", or "the most frequent" item among those still available. A heap provides it.

### 8.1 Meeting rooms: minimum number of rooms

Process meetings by start time; a min-heap holds the **end times** of the meetings currently using rooms. If the earliest-ending one is over by the time the next meeting starts, its room is reused.

```java
static int minMeetingRooms(int[][] intervals) {
    int[][] iv = intervals.clone();
    Arrays.sort(iv, Comparator.comparingInt(x -> x[0]));
    PriorityQueue<Integer> ends = new PriorityQueue<>();   // end times of rooms in use
    for (int[] m : iv) {
        if (!ends.isEmpty() && ends.peek() <= m[0]) ends.poll();   // that room is free again
        ends.offer(m[1]);
    }
    return ends.size();
}
```

`[[0, 30], [5, 10], [15, 20]]` → `2`; `[[7, 10], [2, 4]]` → `1`; `[[1, 5], [5, 8]]` → `1` (`<=`: a meeting ending at 5 frees the room for one starting at 5). The sweep-line version counts `+1`/`−1` events ([[DSA/08 - Specialized Topics/01 - Intervals and Sweep Line|Intervals and Sweep Line]]).

### 8.2 Reorganize a string so no two adjacent letters are equal

Always place the most frequent remaining letter, except the one just placed. A max-heap by remaining count, plus one "held" letter that sits out a turn:

```java
static String reorganizeString(String s) {
    int[] cnt = new int[26];
    for (char c : s.toCharArray()) cnt[c - 'a']++;
    PriorityQueue<Integer> pq = new PriorityQueue<>((x, y) -> Integer.compare(cnt[y], cnt[x]));  // most left first
    for (int c = 0; c < 26; c++) if (cnt[c] > 0) pq.offer(c);
    StringBuilder sb = new StringBuilder();
    int held = -1;                                 // the letter just used: not allowed next
    while (!pq.isEmpty()) {
        int c = pq.poll();
        sb.append((char) ('a' + c));
        cnt[c]--;                                  // safe: c is not in the heap right now
        if (held >= 0) pq.offer(held);
        held = cnt[c] > 0 ? c : -1;
    }
    return held >= 0 ? "" : sb.toString();         // a letter still waiting = impossible
}
```

`"aab"` → `"aba"`; `"aaab"` → `""`. A solution exists exactly when the most frequent letter appears at most `⌈n/2⌉` times. The comparator reads `cnt`, which changes, and that's only safe because each letter's count changes while the letter is **outside** the heap. "Task scheduler" with a cooldown of `n` generalises this (hold letters in a queue for `n` turns).

### 8.3 Always combine the two smallest

**Minimum cost to connect sticks**: joining sticks of lengths `x` and `y` costs `x + y`. Joining the two shortest first is optimal; it's Huffman coding's merge rule ([[DSA/06 - Algorithm Design Paradigms/01 - Greedy Algorithms|Greedy Algorithms]]).

```java
static long connectSticks(int[] sticks) {
    PriorityQueue<Long> pq = new PriorityQueue<>();
    for (int s : sticks) pq.offer((long) s);
    long cost = 0;
    while (pq.size() > 1) {
        long x = pq.poll(), y = pq.poll();
        cost += x + y;
        pq.offer(x + y);
    }
    return cost;
}
```

`[2, 4, 3]` → `14` (`2 + 3 = 5`, then `5 + 4 = 9`); `[1, 8, 3, 5]` → `30`; a single stick → `0`. Sorting once and joining left to right is **not** the same: the merged stick must go back into the pool and may no longer be among the smallest.

### 8.4 Keep the best `k` choices, revise as you go

**Furthest building**: climbing from building `i` to a taller `i + 1` costs either a ladder or `h[i+1] − h[i]` bricks. Ladders should cover the **largest** climbs, but those aren't known in advance. Tentatively put every climb on a ladder (a min-heap of climbs); when there are more climbs than ladders, pay for the **smallest** climb in the heap with bricks.

```java
static int furthestBuilding(int[] h, int bricks, int ladders) {
    PriorityQueue<Integer> onLadders = new PriorityQueue<>();   // climbs currently covered by ladders
    for (int i = 0; i + 1 < h.length; i++) {
        int d = h[i + 1] - h[i];
        if (d <= 0) continue;                      // going down is free
        onLadders.offer(d);
        if (onLadders.size() > ladders) bricks -= onLadders.poll();   // smallest climb → bricks
        if (bricks < 0) return i;
    }
    return h.length - 1;
}
```

`[4, 2, 7, 6, 9, 14, 12]`, `bricks = 5`, `ladders = 1` → `4`; `[4, 12, 2, 7, 3, 18, 20, 3, 19]`, `10`, `2` → `7`. The same "commit tentatively, then evict the worst" idea solves "maximum number of courses within deadlines" (course schedule III, a max-heap of durations) and "minimum refuelling stops" (a max-heap of passed fuel stations).

### 8.5 Graph algorithms

| Algorithm | Heap holds | Pattern |
|---|---|---|
| Dijkstra | `(distance, vertex)` | pop the closest unfinished vertex; stale entries skipped (lazy deletion) ([[DSA/05 - Graphs/03 - Shortest Path Algorithms|Shortest Path Algorithms]]) |
| Prim | `(edge weight, vertex)` | pop the cheapest edge leaving the tree ([[DSA/05 - Graphs/04 - Minimum Spanning Trees|Minimum Spanning Trees]]) |
| A* | `(distance + heuristic, vertex)` | Dijkstra with a goal-directed priority |
| Topological sort, smallest-first | vertex ids with in-degree 0 | lexicographically smallest order |

---

## 9. Lazy Deletion and Indexed Heaps

A binary heap can't find an arbitrary element quickly, so "delete `x`" and "change `x`'s priority" need help.

### 9.1 Lazy deletion

Don't remove the element; **mark** it as dead (in a hash map of counts, a set of ids, or by an index/version check), and when a dead element reaches the top, pop it and discard it.

```
lazyPop():
    while top is marked dead: pop it (and unmark it)
    return pop
```

To change a priority, push a **new** entry and mark the old one dead (or detect staleness on pop by comparing with the current value). Dijkstra in Java usually does exactly this: `if (d > dist[u]) continue;` skips outdated `(d, u)` entries.

| | Lazy deletion | `remove(Object)` |
|---|---|---|
| Delete cost | `O(1)` to mark, `O(log n)` amortized to discard | `O(n)` search + `O(log n)` |
| Memory | dead entries stay until they surface: up to `O(total pushes)` | exact |
| Size | must be tracked separately (`pq.size()` counts dead entries) | `pq.size()` is correct |
| Correctness risk | every `peek` must prune first | none |

> [!warning] Lazy deletion with duplicate values
> Marking "one copy of value 5 is dead" in a count map works for a single heap, but with **two** heaps (sliding window median) a dead 5 may be discarded from the wrong one, desynchronising the size counters. Storing **indices** or unique ids instead of values (as in [[#7.2 Sliding window median|§7.2]]) makes every entry distinguishable and avoids the problem.

### 9.2 Indexed priority queue with decrease-key (advanced)

Keep, next to the heap array, a `pos` array mapping each item (an integer id) to its current slot. Every swap updates `pos`, so any item can be found in `O(1)` and moved in `O(log n)`. This is the textbook Dijkstra and Prim with `O(V)` heap size instead of `O(E)`.

```java
static class IndexMinPQ {
    private final int[] heap, pos;                 // heap[slot] = item; pos[item] = slot, or −1
    private final long[] key;
    private int n = 0;

    IndexMinPQ(int capacity) {
        heap = new int[capacity]; pos = new int[capacity]; key = new long[capacity];
        Arrays.fill(pos, -1);
    }

    boolean contains(int item) { return pos[item] != -1; }
    boolean isEmpty() { return n == 0; }

    void insert(int item, long k) {
        key[item] = k; heap[n] = item; pos[item] = n;
        up(n++);
    }

    void decreaseKey(int item, long k) {           // k must be ≤ the current key
        key[item] = k;
        up(pos[item]);
    }

    int pollMin() {
        int top = heap[0];
        swap(0, --n);
        pos[top] = -1;
        down(0);
        return top;
    }

    private void up(int i) {
        while (i > 0 && key[heap[(i - 1) / 2]] > key[heap[i]]) { swap(i, (i - 1) / 2); i = (i - 1) / 2; }
    }

    private void down(int i) {
        while (true) {
            int s = i, l = 2 * i + 1, r = l + 1;
            if (l < n && key[heap[l]] < key[heap[s]]) s = l;
            if (r < n && key[heap[r]] < key[heap[s]]) s = r;
            if (s == i) return;
            swap(i, s);
            i = s;
        }
    }

    private void swap(int i, int j) {
        int t = heap[i]; heap[i] = heap[j]; heap[j] = t;
        pos[heap[i]] = i;                          // keep the inverse map in sync
        pos[heap[j]] = j;
    }
}
```

In contests, lazy deletion with `PriorityQueue` is usually fast enough and much less code; the indexed version matters when memory is tight or the graph is dense.

### 9.3 Other heaps

| Heap | Insert | Extract-min | Decrease-key | Merge two heaps | Notes |
|---|---|---|---|---|---|
| Binary | `O(log n)` | `O(log n)` | `O(log n)` | `O(n)` | the default |
| `d`-ary | `O(log_d n)` | `O(d log_d n)` | `O(log_d n)` | `O(n)` | children `d·i + 1 … d·i + d`; shallower, good when decrease-keys dominate |
| Binomial | `O(1)` amortized | `O(log n)` | `O(log n)` | `O(log n)` | |
| Leftist / skew | `O(log n)` | `O(log n)` | — | `O(log n)` | simple mergeable heaps |
| Pairing | `O(1)` | `O(log n)` amortized | `o(log n)` amortized | `O(1)` | fast in practice |
| Fibonacci | `O(1)` | `O(log n)` amortized | `O(1)` amortized | `O(1)` | Dijkstra in `O(E + V log V)` in theory; large constants |

---

## 10. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Max-heap for the `k` largest | `O(n)` memory, `O(n log n)` | min-heap of size `k` |
| `(a, b) -> b - a` comparator | wrong order near `±2³¹` | `Collections.reverseOrder()` / `Integer.compare(b, a)` |
| Printing the queue to check order | looks unsorted, confusion | poll to see order |
| Sift down picking the first smaller child | heap property broken | compare both children, take the smaller |
| Child index not checked against `n` | stale values from beyond the heap used | `l < n`, `r < n` |
| Removing a slot and only sifting down | heap broken when the moved element is small | sift up or down |
| Heapify loop running upward from 0 | not a heap | go from `n/2 − 1` down to 0 |
| Building with `n` inserts when the data is known up front | `O(n log n)` instead of `O(n)` | `new PriorityQueue<>(list)` |
| Mutating an element's priority inside the heap | silently wrong order | remove, change, re-insert / lazy deletion |
| `pq.remove(x)` in a loop | `O(n)` each → `O(n²)` | lazy deletion |
| `int x = pq.poll()` on empty | `NullPointerException` | check `isEmpty()` |
| `(lo.peek() + hi.peek()) / 2.0` | overflow | `(long)` cast first |
| Median halves out of balance | wrong median | sizes equal, or lower half +1 |
| `k`-way merge pushing empty lists' heads | `ArrayIndexOutOfBounds` / `NullPointerException` | skip empty lists |
| Meeting rooms with `<` instead of `<=` | back-to-back meetings use two rooms | `ends.peek() <= start` |
| Lazy deletion with value counts across two heaps | sizes drift, wrong answers with duplicates | store indices / ids |
| `PriorityQueue<int[]>` without a comparator | `ClassCastException` on first `offer` | pass a comparator |

---

## 11. Trick Questions and Special Cases

> [!question]- Is a sorted array a min-heap? Is a min-heap's array sorted?
> A sorted (ascending) array is always a valid min-heap: each parent comes before its children. The converse is false: `[1, 3, 2]` is a min-heap and not sorted.

> [!question]- In a min-heap of distinct values, where can the second-smallest element be? The largest?
> The second-smallest must be a child of the root (index 1 or 2): its parent is smaller than it, and only the root is. The largest must be a **leaf** (indices `n/2 … n − 1`): every internal node has a child larger than itself, so no internal node can be the maximum. That only halves the search; finding the maximum of a min-heap still costs `O(n)`.

> [!question]- What's printed by `PriorityQueue` after `offer(5), offer(1), offer(4), offer(2), offer(3)`?
> `[1, 2, 4, 5, 3]`: the internal array. `toString()` and iteration follow array order, not priority order.

> [!question]- `findKthLargest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4)`?
> `4`. Duplicates count as separate elements: the sorted order is `6 5 5 4 …`. Deduplicating first (with a set) would give `3`.

> [!question]- Do `n` inserts and bottom-up heapify build the same heap array?
> Not necessarily; both produce **a** valid heap, but different ones. For `[5, 4, 3, 2, 1]`, inserting one by one gives `[1, 2, 4, 5, 3]`, while heapify gives `[1, 2, 3, 5, 4]`. A test that compares arrays (instead of checking the heap property) can fail for a correct implementation.

> [!question]- Why does heapify start at index `n/2 − 1` and go backwards?
> Indices `n/2 … n − 1` are leaves, already trivial heaps. Going backwards ensures both subtrees of a node are heaps before it's sifted down. Going forwards (from 0) sifts the root while its subtrees are still arbitrary, and the result is generally not a heap.

> [!question]- A max-heap comparator `(a, b) -> b - a` holds `Integer.MIN_VALUE` and `1`. Which comes out first?
> `Integer.MIN_VALUE`. `compare(1, MIN_VALUE) = MIN_VALUE − 1`, which wraps around to `Integer.MAX_VALUE` (positive), so the heap believes `MIN_VALUE` is larger than `1`.

> [!question]- Running median after adding `2147483647` twice?
> `2147483647.0`. Without the `long` cast, `(lo.peek() + hi.peek()) / 2.0` computes the `int` sum first, which wraps to `−2`, and returns `−1.0`.

> [!question]- Minimum cost to connect sticks `[5]`? `[1, 8, 3, 5]`?
> `0`: nothing to connect. `30`: `1 + 3 = 4` (cost 4), `4 + 5 = 9` (cost 9), `8 + 9 = 17` (cost 17). Sorting once and merging left to right gives `4 + 9 + 17 = 30` here by luck; with `[2, 2, 3, 3]`, the heap gives `4 + 6 + 10 = 20`, while left-to-right gives `4 + 7 + 10 = 21`.

> [!question]- Meeting rooms for `[[1, 5], [5, 8]]`?
> `1`. The first meeting ends exactly when the second starts. With `ends.peek() < start`, the room isn't considered free, and the answer is `2`.

> [!question]- `new PriorityQueue<int[]>()` compiles. When does it fail?
> On the first `offer`, with `ClassCastException`: `int[]` isn't `Comparable`, and the cast happens when the first element is placed, even though nothing is compared yet.

> [!question]- Can a heap answer "is `x` present?" in `O(log n)`?
> No: the heap property says nothing about left vs. right, so a search may have to visit every node (`O(n)`, with pruning of subtrees whose root is already larger than `x`). For membership plus ordering, use a `TreeSet`; for membership alone, a `HashSet` alongside the heap.

> [!question]- Reorganize `"aaabc"`? `"aaabb"`?
> `"aaabc"`: possible (`a` appears 3 times, `⌈5/2⌉ = 3`), e.g. `"abaca"`. `"aaabb"` is also possible: `"ababa"`. `"aaab"` isn't: 3 > `⌈4/2⌉ = 2`.

> [!question]- Why the k-th smallest in a sorted matrix only pushes the first `min(n, k)` rows?
> The `k`-th smallest is among the first `k` elements of the merged order, and every row beyond the `k`-th starts with a value at least as large as `k` earlier first-column values. Pushing all `n` rows is still correct, just slower for small `k`.

---

## 12. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| Children / parent of `i` (0-based) | `2i + 1`, `2i + 2` / `(i − 1)/2` | |
| Leaves | indices `n/2 … n − 1` | |
| Height | `⌊log₂ n⌋` | complete tree |
| Build by heapify | `O(n)` | most nodes sift a short way |
| Build by `n` inserts | `O(n log n)` | |
| `new PriorityQueue<>(list)` vs `addAll` | `O(n)` vs `O(n log n)` | |
| `pq.toString()` after `5, 1, 4, 2, 3` | `[1, 2, 4, 5, 3]` | array order |
| `pq.remove(x)` / `contains(x)` | `O(n)` | linear search |
| `(a, b) -> b - a` with `MIN_VALUE`, `1` | `MIN_VALUE` first | overflow |
| `k` largest | min-heap of size `k` | root = border element |
| `findKthLargest([3,2,1,5,6,4], 2)` | `5` | |
| Max of a min-heap | in the leaves, `O(n)` to find | |
| Second-smallest of a min-heap | index 1 or 2 | |
| Inserts vs heapify on `[5,4,3,2,1]` | `[1,2,4,5,3]` vs `[1,2,3,5,4]` | both valid |
| Median of `[2147483647, 2147483647]` | `2147483647.0` with a `long` cast | |
| Meeting rooms `[[1,5],[5,8]]` | `1` | `<=` |
| `connectSticks([2, 2, 3, 3])` | `20` | always the two smallest |
| `new PriorityQueue<>(0)` | `IllegalArgumentException` | capacity `≥ 1` |
| `PriorityQueue<int[]>` without comparator | `ClassCastException` on first `offer` | |
| Fibonacci-heap Dijkstra | `O(E + V log V)` | `O(1)` decrease-key |

---

## 13. Summary

- A binary heap is a complete tree in an array (`2i + 1`, `2i + 2`, `(i − 1)/2`) where each parent is `≤` its children: min in `O(1)`, push and pop in `O(log n)` with sift up and sift down.
- **Heapify** builds a heap in `O(n)` by sifting down from the last internal node back to the root.
- **`PriorityQueue`** is a min-heap; reverse it with `Collections.reverseOrder()`, not `b − a`. Its iteration order isn't sorted, `remove(Object)` is `O(n)`, and changing priorities in place breaks it.
- **Top-`k`**: a min-heap of size `k` for the `k` largest (and vice versa), `O(n log k)`, streaming.
- **`k`-way merge**: a heap of the current heads, `O(N log k)`; also `k`-th smallest in a sorted matrix and the smallest covering range.
- **Two heaps**: a max-heap for the lower half and a min-heap for the upper half give a running median; with lazy deletion (by index) they handle a sliding window.
- **Greedy**: earliest end (meeting rooms), most frequent remaining (reorganize string), two smallest (Huffman, connect sticks), and "tentatively commit, evict the worst" (furthest building).
- **Lazy deletion** replaces `remove`/decrease-key; an **indexed** heap supports real decrease-key in `O(log n)`.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]] · Next: [[DSA/04 - Trees and Hierarchical Structures/05 - Tries|Tries]]
- [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms#5. Heap Sort|Sorting Algorithms § 5]]: heap sort, an in-place max-heap
- [[DSA/04 - Trees and Hierarchical Structures/01 - Binary Trees|Binary Trees]]: complete trees and the array layout
- [[DSA/02 - Linear Data Structures/03 - Linked Lists|Linked Lists]]: merging `k` sorted lists
- [[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]]: FIFO queues and the monotonic deque
- [[DSA/03 - Sorting and Searching/04 - Sliding Window|Sliding Window]]: sliding window median
- [[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]]: when both ends or arbitrary deletions are needed
- [[DSA/05 - Graphs/03 - Shortest Path Algorithms|Shortest Path Algorithms]] and [[DSA/05 - Graphs/04 - Minimum Spanning Trees|Minimum Spanning Trees]]: Dijkstra and Prim
- [[DSA/06 - Algorithm Design Paradigms/01 - Greedy Algorithms|Greedy Algorithms]]: Huffman coding and scheduling
