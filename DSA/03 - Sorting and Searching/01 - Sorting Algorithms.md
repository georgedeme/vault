# Sorting Algorithms

<span class="hl-blue">Sorting</span> rearranges elements into non-decreasing order according to some comparison. It's the most common preprocessing step in algorithms: once data is sorted, duplicates sit next to each other, binary search works, two pointers work, intervals can be swept left to right, and "closest pair" questions only need to look at neighbours.

This note covers the classic algorithms (bubble, selection, insertion, merge, quick, heap), the `Ω(n log n)` lower bound for comparison sorts and the linear-time sorts that get around it (counting, radix, bucket), stability and why it matters, and the practical side: what Java's `Arrays.sort` and `Collections.sort` actually do, how to write comparators that don't break, and the traps in both.

## Contents

- [[#1. Vocabulary|1. Vocabulary]]
- [[#2. Elementary Sorts|2. Elementary Sorts]]
- [[#3. Merge Sort|3. Merge Sort]]
- [[#4. Quicksort|4. Quicksort]]
- [[#5. Heap Sort|5. Heap Sort]]
- [[#6. The Ω(n log n) Lower Bound|6. The Ω(n log n) Lower Bound]]
- [[#7. Non-Comparison Sorts|7. Non-Comparison Sorts]]
- [[#8. Stability in Practice|8. Stability in Practice]]
- [[#9. Sorting in Java|9. Sorting in Java]]
- [[#10. Comparators|10. Comparators]]
- [[#11. Sorting as a Tool|11. Sorting as a Tool]]
- [[#12. Common Mistakes|12. Common Mistakes]]
- [[#13. Trick Questions and Special Cases|13. Trick Questions and Special Cases]]
- [[#14. Quick Reference — Non-Obvious Outcomes|14. Quick Reference — Non-Obvious Outcomes]]
- [[#15. Summary|15. Summary]]

---

## 1. Vocabulary

> [!note] Properties of a sorting algorithm
> - <span class="hl-blue">Stable</span>: elements with **equal keys** keep their original relative order.
> - <span class="hl-blue">In-place</span>: uses `O(1)` extra memory (in practice, `O(log n)` for a recursion stack still counts as in-place).
> - <span class="hl-blue">Adaptive</span>: runs faster when the input is already partly sorted.
> - <span class="hl-blue">Comparison-based</span>: learns about the elements only by asking "is `a < b`?". Such sorts can't beat `Ω(n log n)` ([[#6. The Ω(n log n) Lower Bound|§6]]).
> - <span class="hl-blue">Online</span>: can sort elements as they arrive, without seeing the whole input first (insertion sort is online).

An <span class="hl-blue">inversion</span> is a pair of positions `i < j` with `a[i] > a[j]`. A sorted array has `0` inversions; a reversed one has the maximum, `n(n−1)/2`. The number of inversions measures "how unsorted" an array is, and it's exactly the number of swaps that bubble sort makes and the number of shifts that insertion sort makes.

### 1.1 Overview

| Algorithm | Best | Average | Worst | Extra space | Stable | Adaptive |
|---|---|---|---|---|---|---|
| Bubble (with early exit) | `n` | `n²` | `n²` | `1` | yes | yes |
| Selection | `n²` | `n²` | `n²` | `1` | **no** | no |
| Insertion | `n` | `n²` | `n²` | `1` | yes | yes: `O(n + inversions)` |
| Merge | `n log n` | `n log n` | `n log n` | `n` | yes | only with the "already in order" check |
| Quick (random pivot) | `n log n` | `n log n` | `n²` | `log n` stack | **no** | no |
| Heap | `n log n` | `n log n` | `n log n` | `1` | **no** | no |
| Counting (keys `0..k−1`) | `n + k` | `n + k` | `n + k` | `n + k` | yes | — |
| Radix (`d` digits, base `b`) | `d(n + b)` | `d(n + b)` | `d(n + b)` | `n + b` | yes | — |
| Bucket (uniform input) | `n` | `n` | `n²` | `n` | if the inner sort is | — |
| TimSort (Java objects) | `n` | `n log n` | `n log n` | `n` | yes | yes |

---

## 2. Elementary Sorts

These three are `O(n²)` and are rarely the right choice on their own. But insertion sort is used inside every fast library sort for small subarrays, and each of them shows up in "how many swaps/passes" questions.

### 2.1 Bubble sort

Repeatedly swap adjacent elements that are out of order. After pass `p`, the largest `p + 1` elements are in their final positions at the end. If a pass makes no swaps, the array is sorted.

```
bubbleSort(a):
    for pass = 0 to n − 2:
        swapped = false
        for j = 0 to n − 2 − pass:          -- the last `pass` elements are already final
            if a[j] > a[j + 1]: swap(a[j], a[j + 1]); swapped = true
        if not swapped: return               -- early exit makes the best case O(n)
```

```java
static void bubbleSort(int[] a) {
    int n = a.length;
    for (int pass = 0; pass < n - 1; pass++) {
        boolean swapped = false;
        for (int j = 0; j < n - 1 - pass; j++) {
            if (a[j] > a[j + 1]) { swap(a, j, j + 1); swapped = true; }
        }
        if (!swapped) break;
    }
}

static void swap(int[] a, int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }
```

Each swap fixes exactly one inversion, so bubble sort makes exactly `inversions` swaps. It's stable because it only swaps on **strict** `>`.

> [!info]- Rabbits and turtles
> A large element near the front ("rabbit") moves to the end in a single pass. A small element near the end ("turtle") moves only **one** position left per pass. So `[2, 3, 4, 5, 1]` needs `n − 1` passes even though only one element is out of place. **Cocktail shaker sort** alternates left-to-right and right-to-left passes to move turtles quickly; it's still `O(n²)`.

### 2.2 Selection sort

Find the minimum of the unsorted part and swap it to the front.

```
selectionSort(a):
    for i = 0 to n − 2:
        min = index of the smallest element in a[i..n−1]
        swap(a[i], a[min])
```

```java
static void selectionSort(int[] a) {
    int n = a.length;
    for (int i = 0; i < n - 1; i++) {
        int min = i;
        for (int j = i + 1; j < n; j++) if (a[j] < a[min]) min = j;
        swap(a, i, min);
    }
}
```

- Always `n(n−1)/2` comparisons, even on sorted input: not adaptive.
- At most `n − 1` swaps. That's its one advantage, when writes are expensive (flash memory, large records).
- **Not stable**: the long-distance swap can jump an element over an equal one. `[2a, 2b, 1]`: the first step swaps `2a` with `1`, giving `[1, 2b, 2a]`.

### 2.3 Insertion sort

Grow a sorted prefix. Take the next element and shift larger elements right until its slot appears, like sorting a hand of cards.

```
insertionSort(a):
    for i = 1 to n − 1:
        x = a[i]; j = i − 1
        while j ≥ 0 and a[j] > x:            -- strict: equal elements are not passed, so stable
            a[j + 1] = a[j]; j −= 1
        a[j + 1] = x
```

```java
static void insertionSort(int[] a) {
    for (int i = 1; i < a.length; i++) {
        int x = a[i], j = i - 1;
        while (j >= 0 && a[j] > x) { a[j + 1] = a[j]; j--; }
        a[j + 1] = x;
    }
}
```

> [!important] Insertion sort is O(n + inversions)
> Each shift removes exactly one inversion. So on an array where every element is at most `k` positions from its sorted place, there are at most `nk` inversions, and insertion sort runs in `O(nk)`. On sorted input it's `O(n)`, and on small arrays it beats everything else (tight loop, no recursion, cache-friendly). This is why Java's sorts switch to insertion sort for subarrays below a few dozen elements.

**Binary insertion sort** finds the slot with binary search: `O(n log n)` comparisons, but still `O(n²)` moves. TimSort uses it for short runs, because comparisons of objects are more expensive than moves.

### 2.4 Comparing the three

| | Bubble | Selection | Insertion |
|---|---|---|---|
| Comparisons | `O(n²)`; `n − 1` on sorted input | always `n(n−1)/2` | `O(n²)`; `n − 1` on sorted input |
| Swaps / writes | `inversions` swaps | `≤ n − 1` swaps | `inversions` shifts |
| Stable | yes | no | yes |
| Online | no | no | yes |
| Use it for | nothing, in practice | minimising writes | small or nearly sorted arrays |

---

## 3. Merge Sort

Split the array in half, sort each half recursively, and **merge** the two sorted halves with two pointers.

```
mergeSort(a, lo, hi):                        -- sorts a[lo..hi), half-open
    if hi − lo < 2: return
    mid = (lo + hi) / 2
    mergeSort(a, lo, mid)
    mergeSort(a, mid, hi)
    merge(a, lo, mid, hi)

merge(a, lo, mid, hi):
    copy a[lo..hi) to tmp
    i = lo; j = mid
    for k = lo to hi − 1:
        if j == hi or (i < mid and tmp[i] ≤ tmp[j]): a[k] = tmp[i]; i += 1    -- ≤ keeps it stable
        else: a[k] = tmp[j]; j += 1
```

```java
static void mergeSort(int[] a) {
    mergeSort(a, new int[a.length], 0, a.length);    // one buffer for the whole sort
}

static void mergeSort(int[] a, int[] tmp, int lo, int hi) {
    if (hi - lo < 2) return;
    int mid = (lo + hi) >>> 1;
    mergeSort(a, tmp, lo, mid);
    mergeSort(a, tmp, mid, hi);
    if (a[mid - 1] <= a[mid]) return;                 // halves already in order: O(n) on sorted input
    merge(a, tmp, lo, mid, hi);
}

static void merge(int[] a, int[] tmp, int lo, int mid, int hi) {
    System.arraycopy(a, lo, tmp, lo, hi - lo);
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) a[k++] = (tmp[i] <= tmp[j]) ? tmp[i++] : tmp[j++];
    while (i < mid) a[k++] = tmp[i++];
    // leftover right-half elements are already in their final place
}
```

![[Sorting - Merge Step.excalidraw|800]]

- **Time** `Θ(n log n)` in every case: `log n` levels of recursion, `O(n)` merging per level ([[DSA/01 - Foundations/01 - Complexity Analysis#6. Recurrence Relations|Complexity Analysis § 6]]: `T(n) = 2T(n/2) + n`).
- **Space** `O(n)` for the buffer plus `O(log n)` stack. In-place merging exists but is complicated and slow.
- **Stable**, as long as ties take from the **left** half (`<=`). Using `<` takes the right element first and silently breaks stability.
- Works on **linked lists** with `O(1)` extra space for merging (relink nodes instead of copying), which is why it's the standard linked-list sort ([[DSA/02 - Linear Data Structures/03 - Linked Lists|Linked Lists]]). It's also the basis of **external sorting** (data that doesn't fit in memory: sort chunks, then k-way merge them).

> [!warning] Don't allocate inside `merge`
> `int[] tmp = new int[hi - lo]` inside every merge call allocates `O(n log n)` memory in total over the sort (garbage collected, but slow). Allocate one buffer of size `n` up front and pass it down.

### 3.1 Bottom-up merge sort

No recursion: merge runs of width 1, then 2, 4, 8, …

```java
static void mergeSortBottomUp(int[] a) {
    int n = a.length;
    int[] tmp = new int[n];
    for (int width = 1; width < n; width *= 2)
        for (int lo = 0; lo < n - width; lo += 2 * width)          // a right half must exist
            merge(a, tmp, lo, lo + width, Math.min(lo + 2 * width, n));
}
```

The `Math.min` handles the last, shorter run; the loop condition `lo < n − width` skips a final run that has no partner.

### 3.2 Counting inversions while merging

When the merge takes `tmp[j]` from the right half, it jumps ahead of every element still remaining in the left half, `mid − i` of them, and each of those forms an inversion with it.

```java
static long countInversions(int[] a, int[] tmp, int lo, int hi) {
    if (hi - lo < 2) return 0;
    int mid = (lo + hi) >>> 1;
    long inv = countInversions(a, tmp, lo, mid) + countInversions(a, tmp, mid, hi);
    System.arraycopy(a, lo, tmp, lo, hi - lo);
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) {
        if (tmp[i] <= tmp[j]) a[k++] = tmp[i++];        // <=: equal elements are NOT inversions
        else { inv += mid - i; a[k++] = tmp[j++]; }
    }
    while (i < mid) a[k++] = tmp[i++];
    while (j < hi) a[k++] = tmp[j++];
    return inv;
}
```

`[2, 4, 1, 3, 5]` has `3` inversions: `(2,1)`, `(4,1)`, `(4,3)`. The result needs `long`: up to `n(n−1)/2 ≈ 5·10⁹` for `n = 10⁵`. The same counts come from a Fenwick tree ([[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees]]), and the technique generalises in [[DSA/06 - Algorithm Design Paradigms/02 - Divide and Conquer|Divide and Conquer]] ("reverse pairs" with `a[i] > 2·a[j]` needs a separate counting pass before the merge).

---

## 4. Quicksort

Pick a **pivot**, **partition** the array so smaller elements come before it and larger after, then sort the two sides recursively. All the work happens in the partition; there is no merge step.

```
quickSort(a, lo, hi):                        -- inclusive bounds
    if lo ≥ hi: return
    p = partition(a, lo, hi)                 -- pivot ends at index p, in its final position
    quickSort(a, lo, p − 1)
    quickSort(a, p + 1, hi)
```

### 4.1 Lomuto partition

Use `a[hi]` as the pivot. `i` marks the end of the "less than pivot" region; scan with `j` and swap smaller elements into it.

```
lomuto(a, lo, hi):
    pivot = a[hi]; i = lo
    for j = lo to hi − 1:                    -- invariant: a[lo..i) < pivot ≤ a[i..j)
        if a[j] < pivot: swap(a[i], a[j]); i += 1
    swap(a[i], a[hi])                        -- pivot into its final place
    return i
```

```java
static int lomuto(int[] a, int lo, int hi) {
    int pivot = a[hi], i = lo;
    for (int j = lo; j < hi; j++)
        if (a[j] < pivot) swap(a, i++, j);
    swap(a, i, hi);
    return i;
}
```

![[Sorting - Lomuto Partition.excalidraw|800]]

### 4.2 Hoare partition

Two indices move toward each other, stopping at elements on the wrong side, and swap them. It does about three times fewer swaps than Lomuto and splits runs of equal elements evenly. But the pivot does **not** end at the returned index, so the recursion is different.

```
hoare(a, lo, hi):
    pivot = a[(lo + hi) / 2]                 -- middle, rounded DOWN
    i = lo − 1; j = hi + 1
    loop:
        do i += 1 while a[i] < pivot
        do j −= 1 while a[j] > pivot
        if i ≥ j: return j                   -- a[lo..j] ≤ pivot ≤ a[j+1..hi]
        swap(a[i], a[j])
```

```java
static int hoare(int[] a, int lo, int hi) {
    int pivot = a[(lo + hi) >>> 1];
    int i = lo - 1, j = hi + 1;
    while (true) {
        do i++; while (a[i] < pivot);
        do j--; while (a[j] > pivot);
        if (i >= j) return j;
        swap(a, i, j);
    }
}

static void quickSortHoare(int[] a, int lo, int hi) {
    if (lo >= hi) return;
    int p = hoare(a, lo, hi);
    quickSortHoare(a, lo, p);          // p, NOT p − 1: the pivot isn't necessarily at p
    quickSortHoare(a, p + 1, hi);
}
```

> [!warning] Hoare's two traps
> - **Recursing on `(lo, p − 1)` and `(p + 1, hi)`** as with Lomuto loses elements: index `p` belongs to the left part, and isn't the pivot.
> - **Choosing `a[hi]` as the pivot** (or rounding the middle up) can return `j = hi`, so the call `quickSort(lo, hi)` recurses on the same range forever. On `[1, 2]` with pivot `a[hi] = 2`, both indices stop at index 1 and `j = 1 = hi` is returned. The middle rounded down guarantees `j < hi`.

### 4.3 Pivot choice and the worst case

Quicksort is `O(n log n)` when partitions are reasonably balanced and `O(n²)` when one side keeps getting (almost) everything.

| Pivot rule | Worst-case input | Notes |
|---|---|---|
| First or last element | **already sorted** or reversed | the classic disaster: sorted input is common |
| Middle element | specially built "median-of-3 killer" arrays | fine on sorted input |
| Median of three (first, middle, last) | still constructible | used in practice, cheap |
| **Random** element | none: `O(n log n)` **expected** on every input | the standard choice; worst case has negligible probability |
| Median of medians | none: `O(n log n)` guaranteed | large constant, used in theory ([[DSA/06 - Algorithm Design Paradigms/02 - Divide and Conquer|Divide and Conquer]]) |

```java
static final Random RNG = new Random();

static void quickSort(int[] a, int lo, int hi) {
    while (lo < hi) {
        swap(a, lo + RNG.nextInt(hi - lo + 1), hi);        // random pivot moved to the end
        int p = lomuto(a, lo, hi);
        if (p - lo < hi - p) { quickSort(a, lo, p - 1); lo = p + 1; }   // recurse on the SMALLER side
        else                 { quickSort(a, p + 1, hi); hi = p - 1; }   // loop on the larger one
    }
}
```

> [!important] Recurse on the smaller side, loop on the larger
> Plain recursion has depth `n` in the worst case, which overflows the Java stack around `10⁴`–`10⁵` levels. Recursing only into the smaller part (at most half the range) and turning the other call into a loop bounds the depth by `log₂ n`, whatever the pivots. It doesn't change the time.

### 4.4 Equal keys: three-way partitioning

With many duplicates, Lomuto degrades badly: if **all elements are equal**, `a[j] < pivot` is never true, the pivot lands at `lo`, and every partition removes just one element. That's `O(n²)` **even with a random pivot**. The fix is to partition into three regions, `< pivot`, `= pivot`, `> pivot`, and recurse only on the outer two (Dijkstra's **Dutch national flag** partition, also in [[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]]).

```
quickSort3(a, lo, hi):
    if lo ≥ hi: return
    p = a[random index in lo..hi]
    lt = lo; i = lo; gt = hi                 -- a[lo..lt) < p, a[lt..i) = p, a(gt..hi] > p
    while i ≤ gt:
        if a[i] < p: swap(a[lt], a[i]); lt += 1; i += 1
        elif a[i] > p: swap(a[i], a[gt]); gt −= 1          -- don't advance i: a[i] is new
        else: i += 1
    quickSort3(a, lo, lt − 1)
    quickSort3(a, gt + 1, hi)
```

```java
static void quickSort3(int[] a, int lo, int hi) {
    if (lo >= hi) return;
    int p = a[lo + RNG.nextInt(hi - lo + 1)];
    int lt = lo, i = lo, gt = hi;
    while (i <= gt) {
        if (a[i] < p) swap(a, lt++, i++);
        else if (a[i] > p) swap(a, i, gt--);
        else i++;
    }
    quickSort3(a, lo, lt - 1);
    quickSort3(a, gt + 1, hi);
}
```

With only `k` distinct values, three-way quicksort runs in `O(n log k)`; with all elements equal, it's a single `O(n)` pass.

### 4.5 Properties and relatives

- **Not stable**: partitioning swaps elements over long distances.
- **In-place**: `O(log n)` stack with the smaller-side rule.
- Faster than merge sort and heap sort in practice on arrays of primitives: tight inner loop, sequential memory access, no copying.
- **Introsort** (C++ `std::sort`) runs quicksort but switches to heap sort if the recursion gets deeper than `~2 log n`, guaranteeing `O(n log n)`. Java's dual-pivot quicksort does the same since JDK 14 ([[#9. Sorting in Java|§9]]).
- **Quickselect** partitions once and recurses into **one** side only, finding the `k`-th smallest in `O(n)` expected time. It's covered in [[DSA/06 - Algorithm Design Paradigms/02 - Divide and Conquer|Divide and Conquer]] and [[DSA/08 - Specialized Topics/05 - Randomized Algorithms|Randomized Algorithms]].

---

## 5. Heap Sort

Turn the array into a **max-heap** (the largest element at index 0, every parent `≥` its children), then repeatedly swap the maximum to the end and restore the heap on the shrunken prefix. Heaps themselves are covered in [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|Heaps and Priority Queues]].

```
heapSort(a):
    for i = n/2 − 1 down to 0: siftDown(a, i, n)        -- build the heap bottom-up: O(n)
    for end = n − 1 down to 1:
        swap(a[0], a[end])                              -- the max goes to its final place
        siftDown(a, 0, end)                             -- heap is now a[0..end)

siftDown(a, i, n):                                       -- children of i are 2i+1 and 2i+2
    while i has a child in a[0..n):
        c = the larger child
        if a[c] ≤ a[i]: return
        swap(a[i], a[c]); i = c
```

```java
static void heapSort(int[] a) {
    int n = a.length;
    for (int i = n / 2 - 1; i >= 0; i--) siftDown(a, i, n);
    for (int end = n - 1; end > 0; end--) {
        swap(a, 0, end);
        siftDown(a, 0, end);
    }
}

static void siftDown(int[] a, int i, int n) {
    while (true) {
        int largest = i, l = 2 * i + 1, r = l + 1;
        if (l < n && a[l] > a[largest]) largest = l;
        if (r < n && a[r] > a[largest]) largest = r;
        if (largest == i) return;
        swap(a, i, largest);
        i = largest;
    }
}
```

- `O(n log n)` worst case **and** `O(1)` extra space: the only common sort with both.
- **Not stable**, and slower than quicksort in practice: it jumps around the array (parent ↔ child), so it's cache-unfriendly.
- Building the heap bottom-up is `O(n)`, not `O(n log n)`: most nodes are near the bottom and sift down only a few levels.
- Use a **max**-heap to sort ascending. A min-heap would put the smallest element at index 0, where it already belongs, and leave no place to store extracted elements.

---

## 6. The Ω(n log n) Lower Bound

> [!important] No comparison sort can beat Ω(n log n) in the worst case
> A comparison sort is a **decision tree**: each internal node is a comparison, each leaf is one output order. To sort every input correctly, the tree needs at least one leaf per permutation, `n!` leaves. A binary tree with `n!` leaves has height at least `log₂(n!)`, and `log₂(n!) = Θ(n log n)` (Stirling: `log₂(n!) ≈ n log₂ n − 1.44 n`). The height is the worst-case number of comparisons.

Concrete consequences:

- Sorting 3 elements needs **3** comparisons in the worst case (`⌈log₂ 6⌉ = 3`); 2 can't distinguish 6 orders.
- Sorting 5 elements needs at least `⌈log₂ 120⌉ = 7` comparisons, and 7 is achievable.
- The bound is also `Ω(n log n)` on **average** (most leaves are deep in any binary tree with `n!` leaves), so randomization can't beat it either.

The bound applies only to sorts that learn by comparing. Counting, radix, and bucket sort look at the keys' **values** (use them as array indices), so they can be linear, at the cost of assumptions about the keys.

Related lower bounds by the same argument: **merging** two sorted lists of length `n` needs `2n − 1` comparisons in the worst case; checking whether all elements are **distinct** needs `Ω(n log n)` comparisons (hashing gets `O(n)` expected by not being comparison-based).

---

## 7. Non-Comparison Sorts

### 7.1 Counting sort

For integer keys in a small range `0..k−1`: count how often each value occurs, turn the counts into **starting positions** with a prefix sum, and place each element at its value's next free position.

```
countingSort(a, k):                          -- keys in 0..k−1
    start = array of k + 1 zeros
    for x in a: start[x + 1] += 1            -- start[v + 1] counts v
    for v = 0 to k − 1: start[v + 1] += start[v]      -- now start[v] = first index for value v
    for x in a (left to right):              -- left to right: equal keys keep their order
        out[start[x]] = x; start[x] += 1
    return out
```

```java
static int[] countingSort(int[] a, int k) {
    int[] start = new int[k + 1];
    for (int x : a) start[x + 1]++;
    for (int v = 0; v < k; v++) start[v + 1] += start[v];
    int[] out = new int[a.length];
    for (int x : a) out[start[x]++] = x;
    return out;
}
```

![[Sorting - Counting Sort.excalidraw|800]]

`O(n + k)` time and space. The placement pass is what makes it **stable**, which matters when the keys carry other data (records sorted by age, or radix-sort digits). When the elements are plain integers with nothing attached, just write each value `count[v]` times:

```java
static void countingSortRange(int[] a) {
    if (a.length == 0) return;
    int min = a[0], max = a[0];
    for (int x : a) { min = Math.min(min, x); max = Math.max(max, x); }
    int[] cnt = new int[max - min + 1];              // offset by min: negatives are fine
    for (int x : a) cnt[x - min]++;
    int k = 0;
    for (int v = 0; v < cnt.length; v++)
        while (cnt[v]-- > 0) a[k++] = v + min;
}
```

> [!warning] Counting sort and the range
> It's only linear when `k = O(n)`. Sorting 10 numbers in `0..10⁹` allocates a 4 GB array. And `max − min + 1` overflows `int` when the values span more than `2³¹` (e.g. `Integer.MIN_VALUE` and `Integer.MAX_VALUE` both present). Use radix sort or a comparison sort when the range is large.

### 7.2 Radix sort (LSD)

Sort by the **least significant digit** first, then the next digit, and so on, using a **stable** sort (counting sort) for each digit. After the pass on digit `d`, the numbers are sorted by their last `d + 1` digits, because stability preserves the order from the earlier passes among numbers that tie on the current digit.

```
radixSort(a):                                -- base 256: four passes over a 32-bit int
    for shift in 0, 8, 16, 24:
        stable counting sort of a by digit (a[i] >> shift) & 255
```

```java
static void radixSort(int[] a) {
    int n = a.length;
    int[] out = new int[n];
    for (int shift = 0; shift < 32; shift += 8) {
        int[] start = new int[257];
        for (int x : a) start[digit(x, shift) + 1]++;
        for (int d = 0; d < 256; d++) start[d + 1] += start[d];
        for (int x : a) out[start[digit(x, shift)]++] = x;
        System.arraycopy(out, 0, a, 0, n);
    }
}

static int digit(int x, int shift) {
    int d = (x >>> shift) & 0xFF;
    return shift == 24 ? d ^ 0x80 : d;     // flip the sign bit: negatives sort before positives
}
```

`O(d · (n + b))` for `d` digits in base `b`: here 4 passes with `b = 256`, so linear in `n`. Without the sign-bit flip, negative numbers (whose top bit is 1) would sort **after** all positives, since the top byte of `−1` is `0xFF`.

> [!warning] LSD needs a stable inner sort
> If the per-digit sort is unstable, the order established by earlier (less significant) digits is destroyed, and the result is only sorted by the most significant digit. **MSD** radix sort (most significant digit first, recursing into each bucket) doesn't need stability, and it's the natural choice for strings of varying length; LSD on strings needs equal lengths or padding.

### 7.3 Bucket sort

For real numbers spread **uniformly** over `[0, 1)`: create `n` buckets, drop each value into bucket `⌊x · n⌋`, sort each bucket (insertion sort; each holds `O(1)` elements on average), and concatenate.

```java
static void bucketSort(double[] a) {                      // values in [0, 1)
    int n = a.length;
    List<List<Double>> buckets = new ArrayList<>();
    for (int i = 0; i < n; i++) buckets.add(new ArrayList<>());
    for (double x : a) buckets.get((int) (x * n)).add(x);
    int k = 0;
    for (List<Double> b : buckets) {
        Collections.sort(b);
        for (double x : b) a[k++] = x;
    }
}
```

`O(n)` expected for uniform input. If everything lands in one bucket (all values in `[0.5, 0.5 + 1/n)`), it degenerates to the inner sort's worst case. The bucket idea also appears without sorting: "maximum gap between sorted neighbours" in `O(n)` uses `n − 1` buckets and the pigeonhole principle (the maximum gap can't be inside a bucket).

---

## 8. Stability in Practice

Stability matters only when equal keys are **distinguishable**: records with other fields, or indices sorted by value. Sorting plain `int`s, stability is invisible.

![[Sorting - Stable vs Unstable.excalidraw|800]]

> [!tip] Multi-key sorting with a stable sort
> To sort by key `A`, ties broken by key `B`: either use **one** comparator that compares `A` and then `B`, or **stable**-sort by `B` first, then stable-sort by `A`. The second pass keeps the `B` order among equal `A`s. Sorting by the **primary key first** is backwards: the second sort destroys it. Spreadsheets "sort by column" work this way, and so does LSD radix sort.

Any sort can be made stable by sorting `(key, original index)` pairs, at the cost of the extra index.

---

## 9. Sorting in Java

| Call | Algorithm | Stable | Worst case |
|---|---|---|---|
| `Arrays.sort(int[])` (and the other primitives) | dual-pivot quicksort, insertion sort for small ranges, run-merging for nearly sorted data | n/a (primitives) | `O(n log n)` on JDK 14+ (heap-sort fallback); **`O(n²)`** on JDK 7–13 |
| `Arrays.sort(T[])`, `Arrays.sort(T[], cmp)` | TimSort | **yes** | `O(n log n)`; `O(n)` on sorted input |
| `Collections.sort(list)`, `list.sort(cmp)` | copies to an array, TimSort, writes back | **yes** | `O(n log n)` |
| `Arrays.sort(a, from, to)` | as above, on `a[from..to)` | | `to` is **exclusive** |
| `Arrays.parallelSort(a)` | parallel merge sort for large arrays | yes (objects) | `O(n log n)` |

**TimSort** finds existing ascending runs (and reverses strictly descending ones), extends short runs to a minimum length with binary insertion sort, and merges runs with a stack-based policy plus "galloping" when one run keeps winning. On real-world data, which is often partly sorted, it does far fewer comparisons than `n log n`.

> [!warning] Anti-quicksort tests
> On JDK 13 and earlier, `Arrays.sort(int[])` could be driven to `O(n²)` by a specially constructed array, and Codeforces hacks did exactly that to Java solutions. Defences, in order of preference: **shuffle before sorting**; sort an `Integer[]`/`Long[]` (TimSort, guaranteed `O(n log n)`, but slower and more memory); or put the values in an `ArrayList` and use `Collections.sort`.
>
> ```java
> static void shuffleThenSort(int[] a) {
>     Random rnd = new Random();
>     for (int i = a.length - 1; i > 0; i--) {             // Fisher–Yates
>         int j = rnd.nextInt(i + 1);
>         int t = a[i]; a[i] = a[j]; a[j] = t;
>     }
>     Arrays.sort(a);
> }
> ```

> [!warning] There is no `Arrays.sort(int[], Comparator)`
> Comparators work only on object arrays. To sort an `int[]` in descending order: sort ascending and reverse in place (fastest), or box to `Integer[]` and use `Collections.reverseOrder()`. **Negating** the values, sorting, and negating back fails for `Integer.MIN_VALUE`, because `-Integer.MIN_VALUE == Integer.MIN_VALUE`.
>
> ```java
> static void sortDescending(int[] a) {
>     Arrays.sort(a);
>     for (int i = 0, j = a.length - 1; i < j; i++, j--) { int t = a[i]; a[i] = a[j]; a[j] = t; }
> }
> ```

> [!warning] `Arrays.asList(int[])` is a list of one array
> `Arrays.asList(new int[]{3, 1, 2})` is a `List<int[]>` of size **1**, so `Collections.sort` on it does nothing useful. `Arrays.asList` boxes nothing; it only works as expected on an `Integer[]`. Also, `List.of(...)` is immutable: `List.of(3, 1, 2).sort(null)` throws `UnsupportedOperationException`.

Other details:

- `Arrays.sort(double[])` uses the total order of `Double.compare`: `-0.0` before `0.0`, and `NaN` **last** (even though `NaN < x` and `NaN > x` are both false). `[0.0, -0.0, NaN, -1.0, ∞]` sorts to `[-1.0, -0.0, 0.0, ∞, NaN]`.
- `String`s sort by UTF-16 code: `"Zebra" < "apple"` (uppercase first) and `"10" < "9"` ([[DSA/02 - Linear Data Structures/02 - Strings|Strings § 10.2]]). Use `String.CASE_INSENSITIVE_ORDER`, or compare numbers as numbers.
- To sort the characters of a string: `char[] cs = s.toCharArray(); Arrays.sort(cs); String t = new String(cs);`. `cs.toString()` gives `[C@1b6d3586`, not the characters.

---

## 10. Comparators

A comparator `compare(x, y)` returns a **negative** number if `x` comes first, **positive** if `y` comes first, and `0` if they're tied.

### 10.1 Writing them

```java
// int[][] intervals by start
Arrays.sort(intervals, (p, q) -> Integer.compare(p[0], q[0]));
Arrays.sort(intervals, Comparator.comparingInt(p -> p[0]));        // same thing

// by height descending, then by k ascending (queue reconstruction by height)
Arrays.sort(people, (p, q) -> p[0] != q[0] ? Integer.compare(q[0], p[0])
                                           : Integer.compare(p[1], q[1]));

// strings by length, ties alphabetically
words.sort(Comparator.comparing(String::length).thenComparing(Comparator.naturalOrder()));

// indices of a[] sorted by value (argsort)
Integer[] idx = new Integer[n];
for (int i = 0; i < n; i++) idx[i] = i;
Arrays.sort(idx, (i, j) -> Integer.compare(a[i], a[j]));
```

> [!example]- Sort by frequency ascending, ties by value descending
> `[2, 3, 1, 3, 2]` → `[1, 3, 3, 2, 2]` (`1` occurs once; `3` and `2` twice, the larger value first).
> ```java
> static int[] frequencySort(int[] a) {
>     Map<Integer, Integer> freq = new HashMap<>();
>     for (int x : a) freq.merge(x, 1, Integer::sum);
>     Integer[] boxed = new Integer[a.length];
>     for (int i = 0; i < a.length; i++) boxed[i] = a[i];
>     Arrays.sort(boxed, (x, y) -> {
>         int fx = freq.get(x), fy = freq.get(y);         // unbox: compare as int
>         return fx != fy ? Integer.compare(fx, fy) : Integer.compare(y, x);
>     });
>     int[] res = new int[a.length];
>     for (int i = 0; i < a.length; i++) res[i] = boxed[i];
>     return res;
> }
> ```

> [!tip] Packing into a `long` to avoid boxing
> Sorting `Integer[]` with a lambda is several times slower than `Arrays.sort(long[])`. For an argsort of `int` values, pack `((long) a[i] << 32) | i` into a `long[]`, sort it, and read the index back with `(int) packed`. This works for negative values too: the value sits in the high bits, which decide the order, and the non-negative index fills the low 32 bits.

### 10.2 Comparator traps

> [!warning] `(a, b) -> a - b` overflows
> `Integer.MIN_VALUE - 1` wraps to `Integer.MAX_VALUE`, so this comparator claims `MIN_VALUE > 1`. And `2_000_000_000 - (-2_000_000_000)` is negative. The sort silently produces a wrong order, or throws. Always use `Integer.compare(a, b)` (or `Long.compare`, `Double.compare`).

> [!warning] `reversed()` applies to everything before it
> - `comparing(String::length).thenComparing(naturalOrder()).reversed()` reverses **both** keys: longest first, ties in **reverse** alphabetical order (`[ccc, bb, ab, b, a]`).
> - `comparing(String::length).reversed().thenComparing(naturalOrder())` reverses only the length: `[ccc, ab, bb, a, b]`.
>
> To reverse only one key in the middle of a chain, use `thenComparing(key, Comparator.reverseOrder())`.

> [!warning] `comparing(s -> s.length()).reversed()` doesn't compile
> When `.reversed()` is chained on, Java can't infer the lambda's parameter type from the target, so `s` is an `Object` and `s.length()` is "cannot find symbol". Write `comparing(String::length).reversed()` or `comparing((String s) -> s.length()).reversed()`. Without the `.reversed()`, the same lambda compiles.

> [!warning] Breaking the comparator contract
> A comparator must be consistent: `sgn(compare(x, y)) == −sgn(compare(y, x))`, transitive, and `compare(x, x) == 0`. `(x, y) -> x < y ? -1 : 1` never returns `0`, so `compare(x, x)` is `1`. TimSort detects such inconsistencies and throws `IllegalArgumentException: Comparison method violates its general contract!`, but only sometimes (it depends on the input), so the bug can pass small tests. A **random** comparator, for shuffling, is the same mistake; use `Collections.shuffle`.

> [!warning] A comparator decides equality for `TreeSet` and `TreeMap`
> `new TreeSet<>(Comparator.comparing(String::length))` treats strings of equal length as **duplicates**: adding `"bb", "a", "ccc", "ab", "b"` keeps only `[a, bb, ccc]`. Sorting a list with that comparator keeps everything; a sorted **set** uses `compare == 0` as its definition of "already present". Add a tie-breaker (`thenComparing(naturalOrder())`) whenever distinct elements can tie.

- `Comparator.nullsFirst(cmp)` / `nullsLast(cmp)` handle `null` elements; otherwise sorting a list containing `null` throws `NullPointerException`.
- A class's `compareTo` (`Comparable`) defines its **natural** order; a `Comparator` is an external order. If you implement `compareTo`, keep it consistent with `equals`, or sorted collections and hash collections will disagree about duplicates (`BigDecimal("2.0")` and `BigDecimal("2.00")` are `compareTo`-equal but not `equals`).

---

## 11. Sorting as a Tool

### 11.1 Sort, then scan

| Problem | After sorting |
|---|---|
| Contains duplicate | duplicates are adjacent |
| Minimum difference between any two elements | it's between **neighbours** |
| Merge overlapping intervals | sort by start; each interval only overlaps the last merged one ([[DSA/08 - Specialized Topics/01 - Intervals and Sweep Line|Intervals]]) |
| Meeting rooms: can one person attend all? | sort by start; check `start[i] ≥ end[i − 1]` |
| Group anagrams | sorted characters as the key ([[DSA/02 - Linear Data Structures/02 - Strings#6.2 Grouping anagrams|Strings § 6.2]]) |
| Two sum / 3Sum without a hash map | [[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]] |
| `k`-th largest | index `n − k` (or quickselect `O(n)`, or a size-`k` heap `O(n log k)`) |
| H-index | sorted descending, the largest `h` with `a[h − 1] ≥ h` |
| Assign tasks to workers, boats to people, cookies to children | greedy matching on sorted lists ([[DSA/06 - Algorithm Design Paradigms/01 - Greedy Algorithms|Greedy Algorithms]]) |

> [!tip] Is sorting allowed?
> Sorting costs `O(n log n)` and destroys the original order. If the answer needs **original indices** (two sum returning indices), sort an index array or `(value, index)` pairs. If the problem says "subarray" (contiguous), sorting is usually wrong; if it says "subset", "pairs", or "subsequence where order doesn't matter", sorting is often the first step.

### 11.2 Minimum number of swaps to sort

**Any two elements** may be swapped: the answer is `n − (number of cycles)` in the permutation that maps each position to where its element belongs. A cycle of length `L` needs `L − 1` swaps.

```java
static int minSwaps(int[] a) {                             // distinct values
    int n = a.length;
    Integer[] idx = new Integer[n];
    for (int i = 0; i < n; i++) idx[i] = i;
    Arrays.sort(idx, (i, j) -> Integer.compare(a[i], a[j]));   // idx[k] = where the k-th smallest is now
    boolean[] seen = new boolean[n];
    int swaps = 0;
    for (int i = 0; i < n; i++) {
        int len = 0;
        for (int j = i; !seen[j]; j = idx[j]) { seen[j] = true; len++; }
        if (len > 0) swaps += len - 1;
    }
    return swaps;
}
```

`[4, 3, 2, 1]` → `2` (two 2-cycles: swap the ends, swap the middle). `[2, 3, 4, 1]` → `3` (one 4-cycle).

Only **adjacent** swaps allowed: the answer is the number of **inversions** ([[#3.2 Counting inversions while merging|§3.2]]): `[2, 3, 4, 1]` needs `3`, `[4, 3, 2, 1]` needs `6`. Same arrays, different answers, depending on which swaps are allowed.

### 11.3 Choosing a sort

| Situation | Choice |
|---|---|
| General use in Java | `Arrays.sort` / `list.sort`: don't write your own |
| Must be stable, objects | `Arrays.sort(T[])`, `Collections.sort`: TimSort is stable |
| Small integers (`k = O(n)`) | counting sort |
| Many 32/64-bit integers, speed critical | radix sort |
| Nearly sorted, or tiny | insertion sort |
| Linked list | merge sort |
| `O(1)` extra space and guaranteed `O(n log n)` | heap sort |
| Minimum writes | selection sort (or cycle sort: the minimum possible number of writes) |
| Old-JDK judge with hack-able tests | shuffle, then `Arrays.sort` |
| Need only the smallest `k`, or the `k`-th | heap or quickselect, not a full sort |

---

## 12. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| `(a, b) -> a - b` | wrong order with large or negative values | `Integer.compare` |
| Merge with `<` instead of `<=` | merge sort no longer stable; inversion count includes equal pairs | `<=` takes from the left on ties |
| `new int[...]` inside `merge` | slow, lots of garbage | one buffer passed down |
| Lomuto quicksort on many duplicates | `O(n²)`, even with a random pivot | three-way partitioning, or Hoare |
| Hoare partition recursing on `p − 1` | elements lost, wrong result | recurse on `(lo, p)` and `(p + 1, hi)` |
| Hoare with pivot `a[hi]` | infinite recursion | middle element, rounded down |
| First/last element as the pivot | `O(n²)` on sorted input | random pivot |
| Deep quicksort recursion | `StackOverflowError` | recurse on the smaller side |
| Heap sort with a min-heap | doesn't sort ascending in place | max-heap |
| LSD radix with an unstable digit sort | wrong order | stable counting sort per digit |
| Radix sort ignoring the sign | negatives after positives | flip the sign bit on the top digit |
| Counting sort over `0..10⁹` | out of memory | radix or comparison sort |
| Negating to sort `int[]` descending | `MIN_VALUE` stays first | sort and reverse |
| `Arrays.sort(a, from, to)` with `to` inclusive | last element not sorted | `to` is exclusive |
| Comparator that never returns `0` | sometimes `IllegalArgumentException` | return `0` for ties |
| `TreeSet` with a comparator that ties distinct elements | elements silently dropped | add a tie-breaker |
| `.reversed()` at the end of a chain | all keys reversed | reverse only the key you mean |
| Old JDK + `Arrays.sort(int[])` on a hackable judge | TLE from anti-quicksort input | shuffle first |

---

## 13. Trick Questions and Special Cases

> [!question]- Which of bubble, selection, and insertion sort is stable? Which makes the fewest swaps?
> Bubble and insertion are stable; selection is not (`[2a, 2b, 1]` → `[1, 2b, 2a]`). Selection makes the fewest swaps: at most `n − 1`. Bubble makes exactly `inversions` swaps, up to `n(n−1)/2`.

> [!question]- What is insertion sort's running time on `[2, 1, 4, 3, 6, 5, …]` (adjacent pairs swapped)?
> `O(n)`. There are only `n/2` inversions, and insertion sort is `O(n + inversions)`. Big-O "worst case `O(n²)`" says nothing about this input.

> [!question]- Bubble sort on `[2, 3, 4, 5, 1]` vs. `[5, 1, 2, 3, 4]`: how many passes?
> `[5, 1, 2, 3, 4]`: the first pass carries `5` all the way to the end, and the second pass sees no swaps: 2 passes. `[2, 3, 4, 5, 1]`: the `1` moves left only one position per pass, so all `n − 1 = 4` passes are needed. Both arrays have 4 inversions, so both take exactly 4 swaps; only the number of passes differs (rabbits vs. turtles).

> [!question]- Quicksort with a random pivot on an array of 10⁵ equal elements: how fast?
> With Lomuto: `O(n²)`, about `5·10⁹` comparisons, a TLE. `a[j] < pivot` is never true, so every partition splits off only the pivot. Random pivots don't help because every pivot is the same value. Hoare's partition stops on equal elements from both sides and splits them evenly (`O(n log n)`); three-way partitioning finishes in a single `O(n)` pass.

> [!question]- Is merge sort adaptive?
> Not as usually written: it does `Θ(n log n)` work even on sorted input. The one-line check `if (a[mid − 1] <= a[mid]) return;` before merging makes sorted input `O(n)` (every merge is skipped after one comparison). TimSort goes further by detecting existing runs.

> [!question]- Can any comparison sort sort 5 elements in 6 comparisons?
> No. There are `5! = 120` orders and 6 comparisons distinguish at most `2⁶ = 64` outcomes. At least `⌈log₂ 120⌉ = 7` are needed (and 7 is achievable with a clever scheme; merge sort uses 8 in the worst case).

> [!question]- Counting sort is `O(n + k)`. Does that beat the `Ω(n log n)` bound?
> It doesn't contradict it: the bound is for **comparison** sorts, and counting sort never compares two elements; it uses each value as an array index. The price is the assumption that keys are small integers. With `k = n²` it's slower than a comparison sort.

> [!question]- Radix sort `[170, 45, 75, 90, 802, 24, 2, 66]` LSD in base 10: what's the order after the first pass?
> `[170, 90, 802, 2, 24, 45, 75, 66]`, sorted by the last digit (`0, 0, 2, 2, 4, 5, 5, 6`), with ties in their **original** order (`170` before `90`, `802` before `2`, `45` before `75`). After the tens pass: `[802, 2, 24, 45, 66, 170, 75, 90]`. After the hundreds pass: sorted.

> [!question]- `Arrays.sort(new double[]{0.0, -0.0, Double.NaN, -1.0})` — the result?
> `[-1.0, -0.0, 0.0, NaN]`. `Arrays.sort(double[])` uses `Double.compare`'s total order, in which `-0.0 < 0.0` and `NaN` is greater than everything, even though `-0.0 == 0.0` is `true` and every `<` comparison with `NaN` is `false`. A hand-written sort using `<` would leave `NaN` wherever it happens to stop.

> [!question]- You sort by name, then sort by age (stable). What's the final order?
> By age, with people of the same age in **alphabetical** order. The second (stable) sort decides the primary key; the first sort survives as the tie-breaker. Sorting by age first and then by name would give alphabetical order with age only as the tie-breaker, the opposite of what's usually intended.

> [!question]- `Comparator.comparing(String::length).thenComparing(Comparator.naturalOrder()).reversed()` on `["bb", "a", "ccc", "ab", "b"]`?
> `[ccc, bb, ab, b, a]`: `.reversed()` flips the whole chain, so ties are in **reverse** alphabetical order. With `.reversed()` right after `comparing(String::length)`, ties stay alphabetical: `[ccc, ab, bb, a, b]`.

> [!question]- Minimum swaps to sort `[4, 3, 2, 1]`: with arbitrary swaps, and with adjacent swaps only?
> Arbitrary: `2` (`n − cycles = 4 − 2`). Adjacent: `6` (the number of inversions). The question's wording about which swaps are allowed changes the algorithm completely.

> [!question]- Sort `[3, 30, 34, 5, 9]` to form the largest number. Why not just sort descending?
> Descending numeric order gives `"34 30 9 5 3"`, and descending string order gives `"9 5 34 30 3"` → `"9534303"`, but the answer is `"9534330"`: `"3"` should come before `"30"` because `"330" > "303"`. The comparator is `(a, b) -> (b + a).compareTo(a + b)`, and all-zero input must return `"0"`, not `"000"` ([[DSA/02 - Linear Data Structures/02 - Strings|Strings]]).

> [!question]- Heap sort is `O(n log n)` worst case and in place, quicksort can be `O(n²)`. Why is quicksort the default?
> Constant factors and memory behaviour. Quicksort's partition scans memory sequentially and does few swaps; heap sort jumps between `i` and `2i + 1`, missing the cache on large arrays, and it does more comparisons (about `2n log₂ n` vs. `1.39n log₂ n`). With random pivots the `O(n²)` case has negligible probability, and introsort removes it entirely by falling back to heap sort.

> [!question]- Does `Collections.sort` on a `LinkedList` take `O(n² log n)` because `get(i)` is `O(n)`?
> No. `List.sort` copies the list into an array, sorts the array, then writes the elements back through a list iterator: `O(n log n)` total with `O(n)` extra memory.

---

## 14. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| Selection sort stable? | no | long-distance swaps |
| Insertion sort, `k`-sorted input | `O(nk)` | `O(n + inversions)` |
| Bubble sort swaps | = number of inversions | one inversion per swap |
| Lomuto, all elements equal | `O(n²)` even with random pivot | `<` never true |
| Hoare with pivot `a[hi]` | can recurse forever | returns `j = hi` |
| Quicksort stack depth (smaller side first) | `O(log n)` | |
| Merge sort with `<` in merge | not stable | takes right element on ties |
| Build heap bottom-up | `O(n)` | most nodes are near the leaves |
| Comparisons to sort 5 elements | at least 7 | `⌈log₂ 120⌉` |
| Inversions in a reversed array of `n` | `n(n−1)/2` | |
| `Arrays.sort(int[])` stable? | meaningless (primitives) | |
| `Arrays.sort(Integer[])` stable? | yes | TimSort |
| `Arrays.sort(int[])` worst case, JDK ≤ 13 | `O(n²)` | dual-pivot quicksort |
| `Arrays.sort(a, 1, 3)` | sorts `a[1]`, `a[2]` | end exclusive |
| `Arrays.sort(double[])` with `NaN`, `-0.0` | `-0.0` before `0.0`, `NaN` last | `Double.compare` |
| `"Zebra"` vs `"apple"` | `"Zebra"` first | `'Z' = 90 < 'a' = 97` |
| `(a, b) -> a - b` with `MIN_VALUE` and `1` | says `MIN_VALUE > 1` | overflow |
| `-Integer.MIN_VALUE` | `Integer.MIN_VALUE` | overflow |
| `Arrays.asList(new int[]{3,1,2}).size()` | `1` | a `List<int[]>` |
| `TreeSet` with a length comparator | equal-length strings dropped | `compare == 0` means duplicate |
| Min swaps `[2,3,4,1]`, any / adjacent | `3` / `3` | one 4-cycle / 3 inversions |
| Min swaps `[4,3,2,1]`, any / adjacent | `2` / `6` | two 2-cycles / 6 inversions |

---

## 15. Summary

- **Elementary sorts** are `O(n²)`. Insertion sort is `O(n + inversions)`, stable, and the fastest on tiny or nearly sorted arrays; selection sort minimises swaps but isn't stable.
- **Merge sort**: `Θ(n log n)` always, stable (merge with `<=`), `O(n)` extra space. Best for linked lists and external data; counts inversions as a by-product.
- **Quicksort**: `O(n log n)` expected with a random pivot, in place, fastest in practice, not stable. Use three-way partitioning for duplicates and recurse on the smaller side to bound the stack.
- **Heap sort**: `O(n log n)` worst case with `O(1)` space, but not stable and cache-unfriendly.
- Comparison sorts need `Ω(n log n)` comparisons (`log₂ n!`). **Counting**, **radix**, and **bucket** sort beat it by using key values, under assumptions about the keys.
- **Stability** matters when equal keys carry other data; a stable sort by the secondary key followed by one by the primary key sorts by both.
- **Java**: `Arrays.sort(int[])` is dual-pivot quicksort (shuffle first on old JDKs); object sorts are stable TimSort. Write comparators with `Integer.compare`, watch where `.reversed()` goes, and never break the contract.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/02 - Linear Data Structures/06 - Hash Tables|Hash Tables]] · Next: [[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]]
- [[DSA/01 - Foundations/01 - Complexity Analysis|Complexity Analysis]]: the merge sort recurrence and the master theorem
- [[DSA/02 - Linear Data Structures/03 - Linked Lists|Linked Lists]]: merge sort on a linked list
- [[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]]: merging, partitioning, the Dutch national flag
- [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|Heaps and Priority Queues]]: the heap behind heap sort, top-`k` problems
- [[DSA/06 - Algorithm Design Paradigms/02 - Divide and Conquer|Divide and Conquer]]: quickselect, inversions, median of medians
- [[DSA/08 - Specialized Topics/05 - Randomized Algorithms|Randomized Algorithms]]: why random pivots work, Fisher–Yates
