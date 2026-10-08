# Divide and Conquer

<span class="hl-blue">Divide and conquer</span> solves a problem by splitting it into smaller **independent** instances of the same problem, solving those recursively, and combining their answers. Merge sort, quicksort, and binary search are the familiar examples. The technique pays off when the **combine** step is cheap relative to solving the whole problem directly, and the interesting work in most D&C algorithms is in that step: counting the pairs that cross the split, checking the narrow strip around a dividing line, or merging two partial answers.

This note covers the general template and how to analyse it with recurrences, the merge-sort pattern for counting pairs (inversions, smaller elements after self, reverse pairs), quickselect and the deterministic median of medians, maximum subarray, closest pair of points, Karatsuba multiplication, and a set of D&C problems on strings and expressions. It ends with how D&C relates to dynamic programming: the same recursion with overlapping subproblems needs memoization.

## Contents

- [[#1. The Pattern|1. The Pattern]]
- [[#2. Analysing Divide and Conquer|2. Analysing Divide and Conquer]]
- [[#3. Merge-Sort-Style Counting|3. Merge-Sort-Style Counting]]
- [[#4. Quickselect|4. Quickselect]]
- [[#5. Maximum Subarray|5. Maximum Subarray]]
- [[#6. Closest Pair of Points|6. Closest Pair of Points]]
- [[#7. Faster Arithmetic: Karatsuba and Strassen|7. Faster Arithmetic: Karatsuba and Strassen]]
- [[#8. More Divide and Conquer Problems|8. More Divide and Conquer Problems]]
- [[#9. Divide and Conquer vs. Dynamic Programming|9. Divide and Conquer vs. Dynamic Programming]]
- [[#10. Common Mistakes|10. Common Mistakes]]
- [[#11. Trick Questions and Special Cases|11. Trick Questions and Special Cases]]
- [[#12. Quick Reference — Non-Obvious Outcomes|12. Quick Reference — Non-Obvious Outcomes]]
- [[#13. Summary|13. Summary]]

---

## 1. The Pattern

```
solve(problem):
    if problem is small enough:
        return the answer directly              -- base case
    split problem into subproblems P₁ … Pₐ        -- divide
    rᵢ = solve(Pᵢ) for each i                    -- conquer (recursively)
    return combine(r₁, …, rₐ)                    -- combine
```

> [!note] Three related shapes
> - **Divide and conquer**: several subproblems, all solved (merge sort: two halves).
> - <span class="hl-blue">Decrease and conquer</span>: one subproblem is enough, the rest is discarded (binary search, quickselect, fast exponentiation). Usually becomes a loop.
> - **Dynamic programming**: the subproblems **overlap**, so the same one would be solved many times; cache them ([[#9. Divide and Conquer vs. Dynamic Programming|§9]]).

The questions to settle when designing one:

1. **How to split**: by index (halves), by value (a pivot), by a dividing line (geometry), at an operator (expressions), at a character that can't be part of the answer (strings).
2. **What the recursive call returns**: often more than the final answer needs. Counting inversions also returns the half **sorted**; closest pair also returns the points sorted by `y`; maximum subarray can return four numbers instead of one.
3. **How to combine** the parts in time proportional to their size (or less).

---

## 2. Analysing Divide and Conquer

The running time satisfies a recurrence: `T(n) = a·T(n/b) + f(n)`, where `a` is the number of subproblems, `n/b` their size, and `f(n)` the cost of dividing and combining. The [[DSA/01 - Foundations/01 - Complexity Analysis#7. The Master Theorem|master theorem]] solves most of them; the recursion-tree picture explains them all: add up the work level by level.

| Algorithm | Recurrence | Result |
|---|---|---|
| Binary search, fast power | `T(n/2) + O(1)` | `O(log n)` |
| Quickselect (expected) | `T(n/2) + O(n)` | `O(n)` |
| Median of medians | `T(n/5) + T(7n/10) + O(n)` | `O(n)` |
| Tree traversal | `2T(n/2) + O(1)` | `O(n)` |
| Merge sort, inversions, closest pair | `2T(n/2) + O(n)` | `O(n log n)` |
| Closest pair, re-sorting the strip each time | `2T(n/2) + O(n log n)` | `O(n log² n)` |
| Karatsuba | `3T(n/2) + O(n)` | `O(n^1.585)` |
| Strassen | `7T(n/2) + O(n²)` | `O(n^2.807)` |
| Quickselect / quicksort, worst case | `T(n − 1) + O(n)` | `O(n²)` |

> [!tip] Reading a recurrence at a glance
> With `a` subproblems of size `n/b`, the work at depth `d` is `aᵈ · f(n/bᵈ)`. If the levels **shrink** geometrically (quickselect: `n, n/2, n/4, …`), the top level dominates. If they're **equal** (merge sort: `n` per level), multiply by the depth `log n`. If they **grow** (Karatsuba: `n, 3n/2, 9n/4, …`), the leaves dominate: there are `a^(log_b n) = n^(log_b a)` of them.

Unequal splits (median of medians) are outside the master theorem; if the subproblem sizes add up to a fraction **below 1** of `n` (`1/5 + 7/10 = 9/10`), each level does at most `9/10` of the previous level's work and the total is linear. If they add up to exactly `n` (`T(n/3) + T(2n/3) + n`), every level costs `n` and the result is `O(n log n)`.

---

## 3. Merge-Sort-Style Counting

Many problems ask for the number of pairs `i < j` with some relation between `a[i]` and `a[j]`. Split the array into halves: pairs inside a half are counted recursively, and pairs **crossing** the split have `i` in the left half and `j` in the right. If both halves are sorted, the crossing pairs can be counted in a linear scan, and merging restores the sorted order for the level above. Total `O(n log n)`.

### 3.1 Counting inversions

An inversion is a pair `i < j` with `a[i] > a[j]`. While merging, whenever the next element comes from the **right** half, it's smaller than every element still waiting in the left half, and each of those forms an inversion with it.

```
sortCount(a, lo, hi):                         -- a[lo..hi), returns inversions, sorts a[lo..hi)
    if hi − lo ≤ 1: return 0
    mid = (lo + hi) / 2
    count = sortCount(a, lo, mid) + sortCount(a, mid, hi)
    merge the halves; each time the right half's element is taken
        while i < mid elements remain on the left: count += mid − i
    return count
```

```java
static long countInversions(int[] a) {
    int[] b = a.clone();                           // don't sort the caller's array
    return sortCount(b, new int[b.length], 0, b.length);
}

static long sortCount(int[] a, int[] tmp, int lo, int hi) {   // [lo, hi)
    if (hi - lo <= 1) return 0;
    int mid = (lo + hi) >>> 1;
    long count = sortCount(a, tmp, lo, mid) + sortCount(a, tmp, mid, hi);
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) {
        if (a[i] <= a[j]) tmp[k++] = a[i++];       // <= : equal values are NOT an inversion
        else { count += mid - i; tmp[k++] = a[j++]; }   // a[j] < every a[i..mid)
    }
    while (i < mid) tmp[k++] = a[i++];
    while (j < hi) tmp[k++] = a[j++];
    System.arraycopy(tmp, lo, a, lo, hi - lo);
    return count;
}
```

![[Divide and Conquer - Counting Cross Inversions.excalidraw|800]]

`[2, 4, 1, 3, 5]` → `3`; `[5, 4, 3, 2, 1]` → `10` (`n(n−1)/2`, the maximum); `[1, 1, 1]` → `0`. The count can reach about `n²/2`, so it needs a `long` once `n` is above about 65,000. The inversion count is also the number of swaps bubble sort or insertion sort performs ([[DSA/03 - Sorting and Searching/01 - Sorting Algorithms#3.2 Counting inversions while merging|Sorting § 3.2]]). The Fenwick-tree alternative is in [[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees#6.1 Counting inversions|Fenwick Trees § 6.1]].

### 3.2 Count of smaller numbers after self

For each `i`, count the `j > i` with `a[j] < a[i]`: a per-element inversion count. Sort **indices** instead of values so each count can be credited to its original position. When an element of the left half is placed, every right-half element placed before it is smaller and comes after it in the original array.

```java
static List<Integer> countSmaller(int[] a) {
    int n = a.length;
    int[] idx = new int[n], tmp = new int[n], cnt = new int[n];
    for (int i = 0; i < n; i++) idx[i] = i;
    countSmallerRec(a, idx, tmp, cnt, 0, n);
    List<Integer> res = new ArrayList<>();
    for (int c : cnt) res.add(c);
    return res;
}

static void countSmallerRec(int[] a, int[] idx, int[] tmp, int[] cnt, int lo, int hi) {
    if (hi - lo <= 1) return;
    int mid = (lo + hi) >>> 1;
    countSmallerRec(a, idx, tmp, cnt, lo, mid);
    countSmallerRec(a, idx, tmp, cnt, mid, hi);
    int i = lo, j = mid, k = lo;
    while (i < mid || j < hi) {
        if (j == hi || (i < mid && a[idx[i]] <= a[idx[j]])) {
            cnt[idx[i]] += j - mid;                // right-half elements already placed are smaller
            tmp[k++] = idx[i++];
        } else tmp[k++] = idx[j++];
    }
    System.arraycopy(tmp, lo, idx, lo, hi - lo);
}
```

`[5, 2, 6, 1]` → `[2, 1, 1, 0]`; `[-1, -1]` → `[0, 0]` (equal isn't smaller, which is why ties take the left element first).

### 3.3 Reverse pairs: count first, then merge

Count pairs `i < j` with `a[i] > 2·a[j]`. The condition isn't the merge order, so the counting can't happen inside the merge. Do a **separate** two-pointer pass over the two sorted halves first, then merge normally.

```java
static int reversePairs(int[] nums) {
    int[] a = nums.clone();
    return (int) reverseRec(a, new int[a.length], 0, a.length);
}

static long reverseRec(int[] a, int[] tmp, int lo, int hi) {
    if (hi - lo <= 1) return 0;
    int mid = (lo + hi) >>> 1;
    long count = reverseRec(a, tmp, lo, mid) + reverseRec(a, tmp, mid, hi);
    for (int i = lo, j = mid; i < mid; i++) {      // both halves sorted: j only moves forward
        while (j < hi && a[i] > 2L * a[j]) j++;    // 2L: 2 · a[j] overflows int
        count += j - mid;
    }
    int i = lo, j = mid, k = lo;                   // ordinary merge
    while (i < mid && j < hi) tmp[k++] = a[i] <= a[j] ? a[i++] : a[j++];
    while (i < mid) tmp[k++] = a[i++];
    while (j < hi) tmp[k++] = a[j++];
    System.arraycopy(tmp, lo, a, lo, hi - lo);
    return count;
}
```

`[1, 3, 2, 3, 1]` → `2`; `[2, 4, 3, 5, 1]` → `3`; `[2147483647, 2147483647, 2147483647]` → `0`, but `2 * a[j]` in `int` wraps to `−2` and reports `3`.

| Problem | What's counted across the split |
|---|---|
| Inversions | `a[i] > a[j]` |
| Count smaller after self | the same, credited per `i` |
| Reverse pairs | `a[i] > 2·a[j]` (separate pass) |
| Count of range sum in `[lower, upper]` | pairs of **prefix sums** `P[j] − P[i]` in range: two pointers over sorted halves |
| Global vs. local inversions | compare the counts; equal iff no `a[i] > a[j]` with `j ≥ i + 2` |

> [!info]- CDQ divide and conquer (advanced)
> The same idea generalises to "offline" problems with several dimensions: sort by the first coordinate, split by index, and in the combine step let the left half's **updates** affect the right half's **queries** (with a Fenwick tree over the second coordinate). It counts 3D dominance (`aᵢ ≤ aⱼ`, `bᵢ ≤ bⱼ`, `cᵢ ≤ cⱼ`) in `O(n log² n)`, and turns some dynamic problems into static ones. It's a contest technique, named after Chen Danqi.

---

## 4. Quickselect

Find the `k`-th smallest element without sorting. Partition around a pivot as in quicksort ([[DSA/03 - Sorting and Searching/01 - Sorting Algorithms#4. Quicksort|Sorting § 4]]); the pivot lands at its final sorted position `p`. If `p = k`, done; otherwise **only one side** can contain the answer, so recurse into that side alone.

```
quickselect(a, k):                            -- k is 0-based
    lo = 0; hi = n − 1
    loop:
        pick a random pivot in a[lo..hi]
        partition a[lo..hi] into  < pivot | = pivot | > pivot
        if k is in the "<" part: hi = end of that part
        else if k is in the ">" part: lo = start of that part
        else: return pivot
```

```java
static int quickselect(int[] arr, int k) {        // k-th smallest, 0-based
    int[] a = arr.clone();
    Random rnd = new Random();
    int lo = 0, hi = a.length - 1;
    while (true) {
        int pivot = a[lo + rnd.nextInt(hi - lo + 1)];
        int lt = lo, i = lo, gt = hi;             // a[lo..lt) < pivot, a[lt..i) = pivot, a(gt..hi] > pivot
        while (i <= gt) {
            if (a[i] < pivot) swap(a, lt++, i++);
            else if (a[i] > pivot) swap(a, i, gt--);
            else i++;
        }
        if (k < lt) hi = lt - 1;
        else if (k > gt) lo = gt + 1;
        else return pivot;                         // k is among the copies of the pivot
    }
}

static void swap(int[] a, int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }

static int findKthLargest(int[] a, int k) {       // k-th largest, 1-based
    return quickselect(a, a.length - k);
}
```

![[Divide and Conquer - Quickselect One Side.excalidraw|800]]

`findKthLargest([3, 2, 1, 5, 6, 4], 2)` → `5`; `findKthLargest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4)` → `4`.

**Cost**: a random pivot lands in the middle half of the range with probability `1/2`, which shrinks the range to at most `3/4`. So on average every two rounds remove a quarter of the range, the sizes form a geometric series, and the expected total is `O(n)`. The worst case, a pivot that's always the minimum or maximum, is `O(n²)`; with random pivots it's vanishingly unlikely, but a **fixed** pivot (first element) hits it on sorted input.

> [!warning] Duplicates and the two-way partition
> A Lomuto partition puts every element equal to the pivot on one side. On an array of `n` equal values, each round removes only the pivot itself: `O(n²)` even with random pivots. The three-way partition above stops as soon as `k` falls in the "equal" block, so an all-equal array takes one round.

**After quickselect** (on the array it works on), `a[k]` is the `k`-th smallest, everything before it is `≤`, and everything after is `≥`. That's exactly what "the `k` closest points" or "the `k` smallest" need, in `O(n)` expected time and unsorted. A size-`k` heap ([[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues#5. Top-k Problems|Heaps § 5]]) is `O(n log k)` but works on a stream and has no bad cases.

> [!info]- Median of medians: worst-case O(n) selection
> Choose the pivot so that it's guaranteed to be near the middle:
> ```
> select(a, k):
>     if |a| < 5: sort and return a[k]
>     split a into groups of 5; take the median of each group
>     pivot = select(medians, |medians| / 2)        -- the median of the medians
>     partition around pivot and continue in the side containing k
> ```
> Half of the `n/5` group medians are `≤` the pivot, and each of those groups has 3 elements `≤` its median, so at least `3n/10` elements are `≤` the pivot (and as many `≥`). The side that remains has at most `7n/10` elements: `T(n) ≤ T(n/5) + T(7n/10) + O(n) = O(n)`, because `1/5 + 7/10 < 1`. With groups of 3 the fractions add up to `1` and the bound degrades to `O(n log n)`.
> ```java
> static int selectMoM(int[] a, int lo, int hi, int k) {    // k-th smallest overall index, lo ≤ k ≤ hi; reorders a
>     while (true) {
>         if (hi - lo < 5) { Arrays.sort(a, lo, hi + 1); return a[k]; }
>         int pivot = medianOfMedians(a, lo, hi);
>         int lt = lo, i = lo, gt = hi;
>         while (i <= gt) {
>             if (a[i] < pivot) swap(a, lt++, i++);
>             else if (a[i] > pivot) swap(a, i, gt--);
>             else i++;
>         }
>         if (k < lt) hi = lt - 1;
>         else if (k > gt) lo = gt + 1;
>         else return pivot;
>     }
> }
>
> static int medianOfMedians(int[] a, int lo, int hi) {
>     int m = lo;                                   // group medians are collected in a[lo..m)
>     for (int g = lo; g <= hi; g += 5) {
>         int e = Math.min(g + 4, hi);
>         Arrays.sort(a, g, e + 1);                 // sorting 5 elements is O(1)
>         swap(a, m++, (g + e) >>> 1);
>     }
>     return selectMoM(a, lo, m - 1, (lo + m - 1) >>> 1);
> }
> ```
> The constant factor is large: random-pivot quickselect is faster in practice. Introselect (C++ `std::nth_element`) starts with quickselect and falls back to median of medians if the recursion goes badly.

---

## 5. Maximum Subarray

Largest sum of a non-empty contiguous subarray. The best subarray lies entirely in the left half, entirely in the right half, or **crosses** the middle. A crossing subarray is the best suffix of the left half plus the best prefix of the right half, both found by a linear scan outward from the middle.

```java
static long maxSubarrayDC(int[] a, int lo, int hi) {   // inclusive bounds, lo ≤ hi
    if (lo == hi) return a[lo];
    int mid = (lo + hi) >>> 1;
    long best = Math.max(maxSubarrayDC(a, lo, mid), maxSubarrayDC(a, mid + 1, hi));
    long s = 0, leftBest = Long.MIN_VALUE;
    for (int i = mid; i >= lo; i--) { s += a[i]; leftBest = Math.max(leftBest, s); }    // must include a[mid]
    s = 0;
    long rightBest = Long.MIN_VALUE;
    for (int j = mid + 1; j <= hi; j++) { s += a[j]; rightBest = Math.max(rightBest, s); }   // must include a[mid+1]
    return Math.max(best, leftBest + rightBest);
}
```

`[-2, 1, -3, 4, -1, 2, 1, -5, 4]` → `6` (`[4, -1, 2, 1]`); `[-3, -1, -2]` → `-1`. That's `O(n log n)`; Kadane's scan is `O(n)` and simpler:

```java
static long kadane(int[] a) {
    long best = a[0], endingHere = a[0];
    for (int i = 1; i < a.length; i++) {
        endingHere = Math.max(a[i], endingHere + a[i]);   // extend, or start fresh at i
        best = Math.max(best, endingHere);
    }
    return best;
}
```

The D&C version still matters: returning **four** values per half (total, best prefix, best suffix, best) makes the combine `O(1)` and the whole thing `O(n)`, and that combine is exactly what a segment tree node stores to answer maximum-subarray queries on **ranges** with updates ([[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees#4.1 Custom node data: maximum subarray sum|Segment Trees § 4.1]]).

---

## 6. Closest Pair of Points

Given `n` points in the plane, find the smallest distance between two of them. Checking all pairs is `O(n²)`. D&C gets `O(n log n)`.

```
closest(P sorted by x):
    if |P| ≤ 3: brute force
    split at the median x into left L and right R (the line x = midX)
    δ = min(closest(L), closest(R))
    strip = points with |x − midX| < δ, sorted by y
    for each point p in strip:
        compare p with the following strip points while their y differs by < δ
    return the smallest distance found
```

**Why the strip check is linear**: a pair closer than `δ` that crosses the line has both points within `δ` of it, and their `y` values differ by less than `δ`. For a point `p`, the candidates lie in a `2δ × δ` rectangle above it. Split that rectangle into eight `δ/2 × δ/2` squares; two points in one square would be closer than `δ` on the **same** side, which contradicts `δ` being the best distance on each side. So at most 7 other points need checking per strip point.

![[Divide and Conquer - Closest Pair Strip.excalidraw|800]]

Re-sorting the strip by `y` at every level costs `O(n log² n)`. Returning each half **sorted by `y`** (merging, as in merge sort) keeps every level linear:

```java
static long closestPairSq(int[][] pts) {          // smallest SQUARED distance; needs ≥ 2 points
    int[][] p = pts.clone();
    Arrays.sort(p, (a, b) -> Integer.compare(a[0], b[0]));
    return closest(p, 0, p.length, new int[p.length][]);
}

static long closest(int[][] p, int lo, int hi, int[][] tmp) {   // [lo, hi); leaves p[lo..hi) sorted by y
    if (hi - lo <= 3) {
        long best = Long.MAX_VALUE;
        for (int i = lo; i < hi; i++)
            for (int j = i + 1; j < hi; j++) best = Math.min(best, dist2(p[i], p[j]));
        Arrays.sort(p, lo, hi, (a, b) -> Integer.compare(a[1], b[1]));
        return best;
    }
    int mid = (lo + hi) >>> 1;
    long midX = p[mid][0];                         // read before the recursion reorders p
    long d = Math.min(closest(p, lo, mid, tmp), closest(p, mid, hi, tmp));
    int i = lo, j = mid, k = lo;                   // merge the halves by y
    while (i < mid || j < hi)
        tmp[k++] = (j == hi || (i < mid && p[i][1] <= p[j][1])) ? p[i++] : p[j++];
    System.arraycopy(tmp, lo, p, lo, hi - lo);
    int m = 0;                                     // the strip, in y order, reuses tmp
    for (int t = lo; t < hi; t++) {
        long dx = p[t][0] - midX;
        if (dx * dx >= d) continue;
        for (int s = m - 1; s >= 0; s--) {
            long dy = (long) p[t][1] - tmp[s][1];
            if (dy * dy >= d) break;               // further strip points are even further in y
            d = Math.min(d, dist2(p[t], tmp[s]));
        }
        tmp[m++] = p[t];
    }
    return d;
}

static long dist2(int[] a, int[] b) {
    long dx = (long) a[0] - b[0], dy = (long) a[1] - b[1];
    return dx * dx + dy * dy;
}
```

`[[0, 0], [5, 4], [3, 1], [9, 9], [6, 3]]` → `2` (the points `(5, 4)` and `(6, 3)`, distance `√2`). Working with **squared** distances keeps everything in exact integer arithmetic; take `Math.sqrt` only at the end. Coordinates up to `10⁹` make squared distances up to `8·10¹⁸`, which still fits in a `long`.

> [!warning] Sorting by `x` and checking neighbours is not enough
> `(0, 0)`, `(1, 100)`, `(2, 0)`: neighbours in `x` order are about 100 apart, but the closest pair, `(0, 0)` and `(2, 0)`, are 2 apart and not adjacent. The strip step is what catches pairs that are close in both coordinates but separated in the sorted order.

---

## 7. Faster Arithmetic: Karatsuba and Strassen

Multiplying two `n`-digit numbers by the school method is `O(n²)`. Split each number into a high and low half, `x = x₁·B + x₀` and `y = y₁·B + y₀`. The product needs `x₁y₁`, `x₀y₀` and `x₁y₀ + x₀y₁`, which looks like four half-size products, but the middle term is `(x₁ + x₀)(y₁ + y₀) − x₁y₁ − x₀y₀`: **three** products suffice. `T(n) = 3T(n/2) + O(n) = O(n^(log₂ 3)) ≈ O(n^1.585)`.

```
karatsuba(x, y):
    if x and y are small: return x · y
    split: x = x₁·B + x₀, y = y₁·B + y₀
    z₂ = karatsuba(x₁, y₁); z₀ = karatsuba(x₀, y₀)
    z₁ = karatsuba(x₁ + x₀, y₁ + y₀) − z₂ − z₀
    return z₂·B² + z₁·B + z₀
```

```java
static java.math.BigInteger karatsuba(java.math.BigInteger x, java.math.BigInteger y) {   // x, y ≥ 0
    int n = Math.max(x.bitLength(), y.bitLength());
    if (n <= 64) return x.multiply(y);             // small enough: multiply directly
    int half = n / 2;                              // B = 2^half
    java.math.BigInteger x1 = x.shiftRight(half), x0 = x.subtract(x1.shiftLeft(half));
    java.math.BigInteger y1 = y.shiftRight(half), y0 = y.subtract(y1.shiftLeft(half));
    java.math.BigInteger z2 = karatsuba(x1, y1), z0 = karatsuba(x0, y0);
    java.math.BigInteger z1 = karatsuba(x1.add(x0), y1.add(y0)).subtract(z2).subtract(z0);
    return z2.shiftLeft(2 * half).add(z1.shiftLeft(half)).add(z0);
}
```

Java's own `BigInteger.multiply` already switches to Karatsuba and then Toom-Cook above size thresholds, so this is for understanding, not for use. **Strassen** applies the same trick to matrices: 7 half-size matrix products instead of 8, `O(n^2.807)`. Both only win for large inputs, which is why real implementations switch to the simple method below a cutoff.

---

## 8. More Divide and Conquer Problems

### 8.1 Different ways to add parentheses

Return every value an expression like `"2*3-4*5"` can take under all parenthesizations. Split at **each operator**: the left and right sides are evaluated in all possible ways recursively, and every pair of results is combined.

```java
static Map<String, List<Integer>> exprMemo = new HashMap<>();

static List<Integer> diffWaysToCompute(String e) {
    List<Integer> cached = exprMemo.get(e);
    if (cached != null) return cached;
    List<Integer> res = new ArrayList<>();
    for (int i = 0; i < e.length(); i++) {
        char c = e.charAt(i);
        if (c != '+' && c != '-' && c != '*') continue;
        for (int x : diffWaysToCompute(e.substring(0, i)))
            for (int y : diffWaysToCompute(e.substring(i + 1)))
                res.add(c == '+' ? x + y : c == '-' ? x - y : x * y);
    }
    if (res.isEmpty()) res.add(Integer.parseInt(e));   // no operator: a plain number
    exprMemo.put(e, res);
    return res;
}
```

`"2-1-1"` → `[2, 0]` (`2-(1-1)` and `(2-1)-1`); `"2*3-4*5"` → `[-34, -10, -14, -10, 10]`, with `-10` **twice** because two different parenthesizations give it. The number of results for `m` operators is the Catalan number `Cₘ`, so the output itself is exponential. The same sub-expressions recur in different splits, so the memo (keyed by substring) avoids recomputing them: that's [[#9. Divide and Conquer vs. Dynamic Programming|DP]].

### 8.2 Splitting on what can't be in the answer

**Longest substring in which every character appears at least `k` times.** Any character whose count in the current range is below `k` can't be part of the answer, so the answer lies entirely in one of the pieces between such characters.

```java
static int longestSubstring(String s, int k) {
    return longestSub(s, 0, s.length(), k);
}

static int longestSub(String s, int lo, int hi, int k) {   // [lo, hi)
    if (hi - lo < k) return 0;
    int[] cnt = new int[26];
    for (int i = lo; i < hi; i++) cnt[s.charAt(i) - 'a']++;
    boolean split = false;
    for (int i = lo; i < hi; i++) if (cnt[s.charAt(i) - 'a'] < k) { split = true; break; }
    if (!split) return hi - lo;                    // every character is frequent enough
    int best = 0, start = lo;
    for (int j = lo; j <= hi; j++)
        if (j == hi || cnt[s.charAt(j) - 'a'] < k) {   // a separator (or the end)
            best = Math.max(best, longestSub(s, start, j, k));
            start = j + 1;
        }
    return best;
}
```

`("aaabb", 3)` → `3`; `("ababbc", 2)` → `5`; `("abc", 1)` → `3`. A piece never contains the characters that separated it, so each level of recursion loses at least one letter of the alphabet: depth `≤ 26`, `O(26 · n)` total. A plain sliding window doesn't work directly, because "every character at least `k` times" isn't monotone in the window; it works only after also fixing the number of distinct letters (26 passes).

### 8.3 Merging k sorted lists pairwise

Merging `k` sorted arrays one after another into a growing result costs `O(N·k)` for `N` total elements: early elements are copied again in every round. Merging them in **pairs**, like the levels of merge sort, copies each element `log₂ k` times: `O(N log k)`, the same as the heap method ([[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues#6. K-Way Merge|Heaps § 6]]).

```java
static int[] mergeK(int[][] arrays, int lo, int hi) {     // merges arrays[lo..hi]; call with 0, k − 1
    if (lo == hi) return arrays[lo];
    int mid = (lo + hi) >>> 1;
    return merge2(mergeK(arrays, lo, mid), mergeK(arrays, mid + 1, hi));
}

static int[] merge2(int[] a, int[] b) {
    int[] r = new int[a.length + b.length];
    int i = 0, j = 0, k = 0;
    while (i < a.length && j < b.length) r[k++] = a[i] <= b[j] ? a[i++] : b[j++];
    while (i < a.length) r[k++] = a[i++];
    while (j < b.length) r[k++] = b[j++];
    return r;
}
```

`[[1, 4, 5], [1, 3, 4], [2, 6]]` → `[1, 1, 2, 3, 4, 4, 5, 6]`. With `k = 0` there's nothing to merge; guard for it before calling.

### 8.4 Beautiful array: building the answer from smaller answers

Find a permutation of `1..n` with no `i < k < j` such that `2·a[k] = a[i] + a[j]`. Put all the odd numbers first and all the even numbers second: an odd plus an even is odd, so no middle element can be their average. Inside each half, the problem repeats: if `b` is beautiful, so are `2b − 1` (the odds) and `2b` (the evens), because the condition survives multiplying by 2 and subtracting 1.

```java
static int[] beautifulArray(int n) {
    if (n == 1) return new int[]{1};
    int[] odd = beautifulArray((n + 1) / 2), even = beautifulArray(n / 2);
    int[] res = new int[n];
    int k = 0;
    for (int x : odd) res[k++] = 2 * x - 1;
    for (int x : even) res[k++] = 2 * x;
    return res;
}
```

`4` → `[1, 3, 2, 4]`; `5` → `[1, 5, 3, 2, 4]`. `O(n log n)`.

### 8.5 Divide and conquer elsewhere in the syllabus

| Problem | Split | Note |
|---|---|---|
| Merge sort, quicksort | halves / pivot | [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms|Sorting Algorithms]] |
| Binary search, search on the answer | discard one half | [[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]] |
| Median of two sorted arrays | discard `k/2` from one array | [[DSA/03 - Sorting and Searching/02 - Binary Search#9.5 Median of two sorted arrays (advanced)|Binary Search § 9.5]] |
| Fast exponentiation | halve the exponent | [[DSA/01 - Foundations/04 - Math for Algorithms#4. Fast (Binary) Exponentiation|Math § 4]] |
| Build a tree from traversals, sorted array → balanced BST | root splits the range | [[DSA/04 - Trees and Hierarchical Structures/01 - Binary Trees#9. Building a Tree from Traversals|Binary Trees § 9]] |
| Segment trees | halves of the index range | [[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees|Segment Trees]] |
| Skyline problem | merge two skylines | [[DSA/08 - Specialized Topics/01 - Intervals and Sweep Line|Intervals and Sweep Line]] |
| Convex hull, closest pair | dividing line | [[DSA/08 - Specialized Topics/02 - Computational Geometry|Computational Geometry]] |
| D&C optimisation of DP | the optimal split point is monotone | [[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]] |

---

## 9. Divide and Conquer vs. Dynamic Programming

Both split a problem into subproblems. The difference is whether the subproblems **overlap**.

| | Divide and conquer | Dynamic programming |
|---|---|---|
| Subproblems | disjoint (left half, right half) | shared by many larger problems |
| Each subproblem solved | once, naturally | once, **because** it's cached |
| Without caching | already efficient | often exponential |
| Typical examples | merge sort, closest pair | Fibonacci, knapsack, edit distance |

Naive Fibonacci is "divide and conquer" on overlapping subproblems, and that's why it's exponential ([[DSA/01 - Foundations/02 - Recursion#4.1 Naive Fibonacci|Recursion § 4.1]]). §8.1 sits in between: its splits overlap (the substring `"3-4"` appears in several), so memoizing helps. If a D&C recursion's arguments can repeat, cache it; if they can't (every call works on a disjoint range), caching only wastes memory.

---

## 10. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| `mid = (lo + hi) / 2` with huge indices | overflow to a negative index | `(lo + hi) >>> 1` or `lo + (hi − lo) / 2` |
| Base case missing size 0 or 1 | infinite recursion | `if (hi - lo <= 1) return` |
| Counting inversions with `<` instead of `<=` in the merge | equal elements counted | take the left element on ties |
| `int` inversion count | overflow above ~65,000 elements | `long` |
| Counting reverse pairs inside the merge | wrong counts | separate pass, then merge |
| `2 * a[j]` in `int` | overflow for large values | `2L * a[j]` |
| Fixed pivot in quickselect | `O(n²)` on sorted input | random pivot |
| Two-way partition with many duplicates | `O(n²)` | three-way partition |
| Recursive quickselect / quicksort without care | `StackOverflowError` in bad cases | loop for the single side; recurse on the smaller side |
| `k`-th largest passed as `k` to a smallest-first select | wrong element | `n − k` (0-based) |
| Closest pair: reading `p[mid][0]` after recursing | wrong dividing line (the halves are now sorted by `y`) | read `midX` first |
| Closest pair with `double` distances or `int` squares | rounding, overflow | squared distances in `long` |
| Max subarray crossing part allowed to be empty | sums from non-adjacent pieces | crossing sum must include `a[mid]` and `a[mid+1]` |
| Merging `k` lists sequentially | `O(N·k)` | pairwise or heap: `O(N log k)` |
| Memoizing a D&C whose subproblems never repeat | memory wasted, slower | memoize only overlapping subproblems |

---

## 11. Trick Questions and Special Cases

> [!question]- `countInversions([1, 1])` and the number of inversions in a sorted array?
> Both `0`. Inversions need `a[i] > a[j]` strictly. A merge that takes the right element on ties (`<` instead of `<=`) would report 1 for `[1, 1]`.

> [!question]- What's the maximum number of inversions in an array of `n` elements, and which array has it?
> `n(n − 1)/2`, for a strictly decreasing array: every pair is inverted. For `n = 10⁵` that's about `5·10⁹`, beyond `int`.

> [!question]- Does quickselect sort the array?
> No. It leaves the `k`-th smallest at index `k` with smaller-or-equal elements before it and larger-or-equal after, but each side is in arbitrary order. That's enough for "top `k`" answers that may be returned in any order.

> [!question]- Quickselect on `[7, 7, 7, 7, 7]` with Lomuto partitioning and a random pivot: how long?
> `O(n²)`: every element equals the pivot, all of them go to one side, and each round removes one element. A three-way partition finishes in one round.

> [!question]- Why groups of 5 in median of medians? Would 3 or 7 work?
> 7 works (`1/7 + 5/7 < 1`), and so does any odd group size of at least 5. With 3, the pivot is only guaranteed to have `n/3` elements on each side: `T(n) = T(n/3) + T(2n/3) + O(n)`, whose fractions add to 1, giving `O(n log n)`.

> [!question]- Is the median of medians the true median?
> Not necessarily. It's only guaranteed to be between the 30th and 70th percentile, which is all the linear bound needs.

> [!question]- Closest pair: the strip step compares each point with "the next few" by `y`. Why not all strip points?
> The strip can contain all `n` points (e.g. all on the dividing line), so comparing all pairs would be `O(n²)`. The packing argument limits the useful comparisons to at most 7 per point, and the `break` on `dy² ≥ d` enforces it without counting.

> [!question]- Closest pair with duplicate points?
> The answer is `0`. The algorithm handles it: the duplicates land in the same half or in the strip, and `dx² < d` is false once `d = 0`, so nothing else is checked.

> [!question]- `T(n) = 2T(n/2) + n log n`: is it `O(n log n)`?
> No, `Θ(n log² n)`: each of the `log n` levels does about `n log n` work. That's the cost of the closest-pair version that re-sorts the strip at every level.

> [!question]- Max subarray D&C on `[-1, -2]`: what does the crossing part give?
> `-3` (`-1` from the left suffix plus `-2` from the right prefix); the halves give `-1` and `-2`; answer `-1`. The crossing part must take at least one element from each side, which is why both scans start at the middle elements rather than at an empty sum of 0.

> [!question]- How many results does `diffWaysToCompute` return for an expression with `m` operators?
> The Catalan number `Cₘ` (with duplicates): `1, 1, 2, 5, 14, 42, …`. For `"2*3-4*5"` (3 operators) that's 5 values, two of them equal (`-10`).

> [!question]- `longestSubstring("ababacb", 3)`?
> `0`. `c` appears once, so split around it: `"ababa"` and `"b"`. In `"ababa"`, `b` appears twice, so split on both `b`s: pieces `"a"`, `"a"`, `"a"`, each shorter than 3. Nothing qualifies.

> [!question]- Why is Karatsuba's base case "≤ 64 bits" and not "1 bit"?
> Below some size, the three recursive calls plus additions cost more than one direct multiplication. Every practical D&C (merge sort switching to insertion sort, Karatsuba, Strassen) stops recursing at a cutoff.

> [!question]- `beautifulArray(1)` and `beautifulArray(2)`?
> `[1]` and `[1, 2]`. Any array of length at most 2 is beautiful (there's no middle index).

---

## 12. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `countInversions([2,4,1,3,5])` | `3` | |
| `countInversions([5,4,3,2,1])` | `10` | `n(n−1)/2` |
| `countSmaller([5,2,6,1])` | `[2, 1, 1, 0]` | index sort |
| `reversePairs([2,4,3,5,1])` | `3` | separate count pass |
| `reversePairs([MAX, MAX, MAX])` | `0` | `2L *`, else 3 |
| `findKthLargest([3,2,1,5,6,4], 2)` | `5` | select `n − k` |
| Quickselect expected / worst | `O(n)` / `O(n²)` | |
| Median of medians | `O(n)` worst case | `1/5 + 7/10 < 1` |
| `maxSubarrayDC([-2,1,-3,4,-1,2,1,-5,4])` | `6` | |
| Max subarray D&C with 4-value returns | `O(n)` | segment tree merge |
| Closest pair `(0,0),(5,4),(3,1),(9,9),(6,3)` | squared distance `2` | |
| Closest pair, re-sorting the strip | `O(n log² n)` | |
| Karatsuba | `O(n^1.585)` | 3 products, not 4 |
| `diffWaysToCompute("2*3-4*5")` | 5 values, `-10` twice | Catalan |
| `longestSubstring("ababbc", 2)` | `5` | split on `c` |
| `beautifulArray(5)` | `[1, 5, 3, 2, 4]` | odds, then evens |
| Merge `k` lists sequentially / pairwise | `O(Nk)` / `O(N log k)` | |

---

## 13. Summary

- Divide and conquer splits a problem into **independent** subproblems, solves them recursively, and **combines** the answers; the combine step is where the algorithm lives.
- Analyse with `T(n) = a·T(n/b) + f(n)`: shrinking levels → top dominates, equal levels → times `log n`, growing levels → leaves dominate. Unequal splits whose sizes sum below `n` are linear.
- **Merge-sort counting**: count pairs crossing the split using two sorted halves (inversions, smaller after self, reverse pairs, range sums), then merge.
- **Quickselect**: partition, keep one side, `O(n)` expected; three-way partition for duplicates; median of medians for a worst-case `O(n)` guarantee.
- **Maximum subarray** combines a best suffix and a best prefix; **closest pair** checks a strip around the dividing line with at most 7 neighbours per point, keeping halves sorted by `y`.
- **Karatsuba** and **Strassen** save one subproblem per level, which changes the exponent.
- When subproblems overlap, D&C becomes DP: memoize.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/06 - Algorithm Design Paradigms/01 - Greedy Algorithms|Greedy Algorithms]] · Next: [[DSA/06 - Algorithm Design Paradigms/03 - Backtracking|Backtracking]]
- [[DSA/01 - Foundations/01 - Complexity Analysis|Complexity Analysis]]: recurrences and the master theorem
- [[DSA/01 - Foundations/02 - Recursion|Recursion]]: recursion trees and the call stack
- [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms|Sorting Algorithms]]: merge sort, quicksort, partitioning
- [[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]]: decrease and conquer
- [[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees|Segment Trees]]: D&C stored as a data structure
- [[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees]]: the other way to count inversions
- [[DSA/06 - Algorithm Design Paradigms/04 - Dynamic Programming Fundamentals|Dynamic Programming — Fundamentals]]: overlapping subproblems
- [[DSA/08 - Specialized Topics/05 - Randomized Algorithms|Randomized Algorithms]]: why random pivots work
