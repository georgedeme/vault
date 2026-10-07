# Binary Search

<span class="hl-blue">Binary search</span> finds a target in a sorted array by repeatedly halving the range where it could be: compare with the middle element, then throw away the half that can't contain it. `n = 10⁹` elements need only about 30 steps.

The idea is much broader than "find `x` in a sorted array". Binary search works on **any monotone yes/no question**: a predicate that is false up to some point and true from then on. That covers lower/upper bounds, rotated arrays, peaks, and "binary search on the answer", where you search over possible answers instead of over an array. Almost every binary-search bug is an off-by-one or an infinite loop, so this note is careful about invariants and gives one template per situation.

## Contents

- [[#1. The Idea|1. The Idea]]
- [[#2. Classic Search|2. Classic Search]]
- [[#3. Lower and Upper Bound|3. Lower and Upper Bound]]
- [[#4. The General Template — First True, Last True|4. The General Template — First True, Last True]]
- [[#5. Binary Search in Java|5. Binary Search in Java]]
- [[#6. Binary Search on the Answer|6. Binary Search on the Answer]]
- [[#7. Rotated Sorted Arrays|7. Rotated Sorted Arrays]]
- [[#8. 2D Matrices|8. 2D Matrices]]
- [[#9. More Variants|9. More Variants]]
- [[#10. Ternary Search (advanced)|10. Ternary Search (advanced)]]
- [[#11. Common Mistakes|11. Common Mistakes]]
- [[#12. Trick Questions and Special Cases|12. Trick Questions and Special Cases]]
- [[#13. Quick Reference — Non-Obvious Outcomes|13. Quick Reference — Non-Obvious Outcomes]]
- [[#14. Summary|14. Summary]]

---

## 1. The Idea

> [!note] What binary search needs
> 1. A search space with **random access**: an array index, or a range of integers/reals you can evaluate at any point.
> 2. A **monotone predicate** `P` over that space: `false, false, …, false, true, true, …, true`. Binary search finds the boundary between the two parts.
>
> "`a[i] ≥ x`" on a sorted array is such a predicate. So is "can the packages be shipped in `D` days with capacity `c`?" over capacities `c`.

Each step halves the range, so after `k` steps `n / 2ᵏ` candidates remain: `⌈log₂(n + 1)⌉` steps in the worst case. `O(log n)` time, `O(1)` space.

| `n` | Max steps |
|---|---|
| `10³` | 10 |
| `10⁶` | 20 |
| `10⁹` | 30 |
| `10¹⁸` (a `long` range) | 60 |

> [!important] Think in invariants
> Every correct binary search maintains a statement like "the answer is in `[lo, hi]`" or "everything before `lo` is false and everything from `hi` on is true". Write that invariant down, make sure the initial values satisfy it, make sure each update preserves it, and make sure the range shrinks every iteration. The loop condition and the return value then follow from the invariant, not from memory.

---

## 2. Classic Search

Find the index of `target` in a sorted array, or `−1`.

```
binarySearch(a, target):
    lo = 0; hi = n − 1                       -- invariant: if target is present, it's in a[lo..hi]
    while lo ≤ hi:                           -- the range is non-empty
        mid = lo + (hi − lo) / 2
        if a[mid] == target: return mid
        if a[mid] < target: lo = mid + 1     -- target is right of mid
        else: hi = mid − 1                   -- target is left of mid
    return −1                                -- empty range: not present
```

```java
static int binarySearch(int[] a, int target) {
    int lo = 0, hi = a.length - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] == target) return mid;
        if (a[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
```

With duplicates, this returns **some** index of `target`, not necessarily the first or the last. For those, use the bounds in [[#3. Lower and Upper Bound|§3]].

> [!warning] `(lo + hi) / 2` overflows
> With `lo` and `hi` near `2³¹`, `lo + hi` wraps to a negative number, and `a[mid]` throws `ArrayIndexOutOfBoundsException`. This bug sat in the JDK's own `Arrays.binarySearch` for nine years (fixed in 2006). Use `lo + (hi - lo) / 2`, or `(lo + hi) >>> 1` (the unsigned shift treats the wrapped sum correctly, as long as both are non-negative).

> [!warning] Searching a range with negative numbers
> When `lo` and `hi` can be negative (binary search on an answer in `[−10⁹, 10⁹]`), `(lo + hi) / 2` rounds **toward zero**, not down: for `lo = −3, hi = −2` it gives `−2`, the **upper** middle. `(lo + hi) >>> 1` gives `2147483645`, garbage. Use `lo + (hi - lo) / 2` (`hi − lo ≥ 0`, so it rounds down) or `Math.floorDiv(lo + hi, 2)`, with `long` if `hi − lo` can exceed `int`.

---

## 3. Lower and Upper Bound

> [!note] Definitions
> On a sorted array `a`:
> - <span class="hl-blue">`lowerBound(x)`</span>: the first index `i` with `a[i] ≥ x` (or `n` if none). Where `x` would be inserted **before** any equal elements.
> - <span class="hl-blue">`upperBound(x)`</span>: the first index `i` with `a[i] > x` (or `n`). Where `x` would be inserted **after** any equal elements.
>
> The equal elements occupy exactly `a[lowerBound(x) .. upperBound(x))`.

```
lowerBound(a, x):
    lo = 0; hi = n                           -- half-open: the answer is in [lo, hi]; hi = n means "none"
    while lo < hi:
        mid = (lo + hi) / 2                  -- lo ≤ mid < hi, so a[mid] is always valid
        if a[mid] < x: lo = mid + 1          -- mid and everything left of it are too small
        else: hi = mid                       -- mid might be the answer: keep it
    return lo                                -- lo == hi
```

```java
static int lowerBound(int[] a, int x) {          // first i with a[i] >= x
    int lo = 0, hi = a.length;
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (a[mid] < x) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}

static int upperBound(int[] a, int x) {          // first i with a[i] > x
    int lo = 0, hi = a.length;
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (a[mid] <= x) lo = mid + 1;           // the only difference: <= instead of <
        else hi = mid;
    }
    return lo;
}
```

![[Binary Search - Lower and Upper Bound.excalidraw|800]]

Everything else is built from these two:

| Question (sorted `a`) | Answer |
|---|---|
| First occurrence of `x` | `i = lowerBound(x)`; valid if `i < n && a[i] == x` |
| Last occurrence of `x` | `j = upperBound(x) − 1`; valid if `j ≥ 0 && a[j] == x` |
| Count of `x` | `upperBound(x) − lowerBound(x)` |
| Insert position keeping order (search insert position) | `lowerBound(x)` |
| Number of elements `< x` | `lowerBound(x)` |
| Number of elements `≤ x` | `upperBound(x)` |
| Count in the range `[L, R]` | `upperBound(R) − lowerBound(L)` |
| Smallest element `≥ x` (ceiling) | `a[lowerBound(x)]` if `< n` |
| Smallest element `> x` (successor) | `a[upperBound(x)]` if `< n` |
| Largest element `≤ x` (floor) | `a[upperBound(x) − 1]` if `≥ 0` |
| Largest element `< x` (predecessor) | `a[lowerBound(x) − 1]` if `≥ 0` |

> [!example]- `a = [1, 2, 2, 2, 3, 5]`
> | `x` | `lowerBound` | `upperBound` | count | floor | ceiling |
> |---|---|---|---|---|---|
> | `2` | 1 | 4 | 3 | 2 | 2 |
> | `4` | 5 | 5 | 0 | 3 | 5 |
> | `0` | 0 | 0 | 0 | none (index −1) | 1 |
> | `9` | 6 | 6 | 0 | 5 | none (index 6 = n) |

> [!tip] `hi = n`, not `n − 1`
> The answer "no element is `≥ x`" is a legitimate result, represented by index `n`. Starting with `hi = n − 1` makes it impossible to return `n`, so searching for a value larger than everything returns `n − 1`, which is wrong. The half-open range `[lo, hi)` with `hi = n` includes that outcome naturally.

---

## 4. The General Template — First True, Last True

Lower bound is a special case of a universal pattern: given a monotone predicate `ok`, find the **first** `x` where it's true.

```
firstTrue(lo, hi, ok):                       -- ok is false…false true…true on [lo, hi]; ok(hi) is true
    while lo < hi:
        mid = lo + (hi − lo) / 2             -- lower middle
        if ok(mid): hi = mid                 -- mid could be the first true: keep it
        else: lo = mid + 1                   -- mid is false: the first true is after it
    return lo

lastTrue(lo, hi, ok):                        -- ok is true…true false…false on [lo, hi]; ok(lo) is true
    while lo < hi:
        mid = lo + (hi − lo + 1) / 2         -- UPPER middle
        if ok(mid): lo = mid
        else: hi = mid − 1
    return lo
```

```java
static long firstTrue(long lo, long hi, LongPredicate ok) {
    while (lo < hi) {
        long mid = lo + (hi - lo) / 2;
        if (ok.test(mid)) hi = mid;
        else lo = mid + 1;
    }
    return lo;
}

static long lastTrue(long lo, long hi, LongPredicate ok) {
    while (lo < hi) {
        long mid = lo + (hi - lo + 1) / 2;       // round UP, or lo = mid can loop forever
        if (ok.test(mid)) lo = mid;
        else hi = mid - 1;
    }
    return lo;
}
```

`firstTrue(1, 100, v -> v * v >= 50)` is `8`; `lastTrue(0, 100, v -> v * v <= 50)` is `7`.

![[Binary Search - First True Convergence.excalidraw|800]]

> [!important] Why the upper middle in `lastTrue`
> When `hi = lo + 1`, the lower middle is `lo`. If `ok(lo)` is true, the update `lo = mid` leaves the range unchanged, and the loop never ends. The rule: **if a branch sets `lo = mid`, round `mid` up; if a branch sets `hi = mid`, round it down.** Each branch must then shrink the range.

> [!tip] If the boundary might not exist
> `firstTrue` assumes `ok(hi)` is true. If you're not sure, search `[lo, hi + 1]` and treat `hi + 1` as "true by definition" (never evaluate it; `mid < hi` always holds inside the loop). A result of `hi + 1` then means "no `x` satisfies `ok`". That's exactly what `lowerBound` does with `hi = n`.

### 4.1 Three loop styles

All three are correct when used consistently; mixing pieces of them is where bugs come from.

| Style | Range meaning | Loop | Updates | Result |
|---|---|---|---|---|
| Closed `[lo, hi]` | answer, if any, is in `a[lo..hi]` | `lo <= hi` | `lo = mid + 1`, `hi = mid − 1` | found inside the loop, or `−1` |
| Half-open `[lo, hi)` / converge | answer is in `[lo, hi]`, `hi` may mean "none" | `lo < hi` | `lo = mid + 1`, `hi = mid` | `lo` (= `hi`) after the loop |
| Sentinels | `ok(lo)` false, `ok(hi)` true, both known | `hi − lo > 1` | `lo = mid` or `hi = mid` | `hi` is the first true, `lo` the last false |

```java
// sentinel style: lo = −1 is "false", hi = n is "true"; never evaluated
int lo = -1, hi = n;
while (hi - lo > 1) {
    int mid = (lo + hi) >>> 1;          // lo + hi ≥ 0 here: see below
    if (a[mid] >= x) hi = mid; else lo = mid;
}
// hi = lowerBound(x)
```

With `lo = −1` the sum `lo + hi` is `≥ −1 + 1 = 0` whenever the loop runs (`hi ≥ lo + 2`), so `>>> 1` is safe here; use `lo + (hi − lo) / 2` if the range itself can be negative.

---

## 5. Binary Search in Java

| Method | Returns | Notes |
|---|---|---|
| `Arrays.binarySearch(a, x)` | an index of `x`, or `−(insertionPoint) − 1` | **any** index if duplicates; array must be sorted |
| `Arrays.binarySearch(a, from, to, x)` | same, within `a[from..to)` | |
| `Arrays.binarySearch(T[] a, x, cmp)` | same, using a comparator | the array must be sorted **by that comparator** |
| `Collections.binarySearch(list, x)` | same | `O(log n)` for `ArrayList`; on a `LinkedList`, `O(n)` traversal |
| `TreeSet`: `floor`, `ceiling`, `lower`, `higher` | the element or `null` | dynamic data with inserts; `O(log n)` |
| `TreeMap`: `floorKey`, `ceilingKey`, `floorEntry`, … | key/entry or `null` | |

```java
int[] a = {1, 2, 2, 2, 3, 5};
Arrays.binarySearch(a, 4);    // -6: insertion point 5 → -(5) - 1
Arrays.binarySearch(a, 0);    // -1: insertion point 0 → -1 (NOT 0!)
Arrays.binarySearch(a, 9);    // -7
Arrays.binarySearch(a, 2);    // 1, 2 or 3: unspecified which

int r = Arrays.binarySearch(a, x);
int insertionPoint = r >= 0 ? r : -r - 1;      // or ~r: -r - 1 == ~r
```

> [!warning] `Arrays.binarySearch` traps
> - The "not found" encoding is `−(insertionPoint) − 1`, so that the result is negative **even when the insertion point is 0**. Testing `if (r > 0)` for "found" misses index 0; test `r >= 0`.
> - With duplicates, the index returned is **not** the first occurrence. For first/last/count, write `lowerBound`/`upperBound`.
> - On an unsorted array, the result is undefined: no exception, just a wrong answer.

> [!tip] Java's `TreeMap` as a sorted dictionary
> When elements are inserted and removed between queries, a sorted array can't be maintained cheaply. `TreeSet.floor(x)` / `ceiling(x)` answer the same questions as the bounds in `O(log n)` with updates ([[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]]). They return `null` when nothing qualifies, so unbox carefully.

---

## 6. Binary Search on the Answer

When a problem asks for the **minimum** value that makes something possible (or the **maximum** that keeps it possible), and "possible" is monotone in that value, binary search over the value itself. Each step runs a `check(value)` function, usually a greedy `O(n)` scan.

> [!important] Recognising it
> - "Minimize the maximum …" / "maximize the minimum …"
> - "Find the smallest `x` such that …" where a larger `x` only makes it easier (or harder).
> - The answer is a number in a known range, and **checking** a candidate answer is easy, while **constructing** the optimum directly is not.
>
> Total cost: `O(log(range) × cost of check)`.

The template has three decisions: the **range** `[lo, hi]` (must contain the answer), the **check** (and its direction), and **first true vs. last true**.

### 6.1 Minimum eating speed (minimise: first true)

Piles of bananas, `h` hours, eat at most `k` per hour from one pile per hour. Find the smallest `k` that finishes in time. A larger `k` never takes longer: monotone.

```
minEatingSpeed(piles, h):
    lo = 1; hi = max(piles)                  -- k = max(piles) finishes in n ≤ h hours
    while lo < hi:
        mid = (lo + hi) / 2
        if hours(mid) ≤ h: hi = mid          -- fast enough: try slower
        else: lo = mid + 1
    return lo
```

```java
static int minEatingSpeed(int[] piles, int h) {
    int lo = 1, hi = 0;
    for (int p : piles) hi = Math.max(hi, p);
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (hoursNeeded(piles, mid) <= h) hi = mid;
        else lo = mid + 1;
    }
    return lo;
}

static long hoursNeeded(int[] piles, int k) {
    long hours = 0;                                  // long: n piles × up to 10⁹ hours each
    for (int p : piles) hours += (p - 1) / k + 1;    // ceil(p / k) for p ≥ 1, without overflow
    return hours;
}
```

`[3, 6, 7, 11], h = 8` → `4`. The `long` matters: with `k = 1` and `10⁴` piles of `10⁹`, the hours total `10¹³`.

### 6.2 Ship packages within D days / split array largest sum (minimise the maximum)

Ship weights **in order**, each day's load at most the capacity. Find the minimum capacity that finishes in `days` days. "Split an array into `k` contiguous parts minimising the largest part sum" is the same problem.

```java
static int shipWithinDays(int[] w, int days) {
    int lo = 0, hi = 0;
    for (int x : w) { lo = Math.max(lo, x); hi += x; }  // lo: the heaviest package must fit
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (daysNeeded(w, mid) <= days) hi = mid;
        else lo = mid + 1;
    }
    return lo;
}

static int daysNeeded(int[] w, int cap) {               // greedy: fill each day as much as possible
    int days = 1, load = 0;
    for (int x : w) {
        if (load + x > cap) { days++; load = 0; }
        load += x;
    }
    return days;
}
```

`[1..10], days = 5` → `15`. The lower bound `max(w)` isn't just an optimisation: with `lo = 1`, `daysNeeded` with a capacity smaller than some package would put that package alone on a day that's still over capacity and return a misleadingly small count.

### 6.3 Maximise the minimum distance (last true)

Place `m` balls (or cows) in stalls at positions `pos` so that the minimum distance between any two is as **large** as possible. "Can we keep every gap `≥ d`?" is true for small `d` and false for large: search for the **last** true.

```java
static int maxMinDistance(int[] pos, int m) {
    int[] p = pos.clone();
    Arrays.sort(p);
    int lo = 1, hi = p[p.length - 1] - p[0];
    while (lo < hi) {
        int mid = lo + (hi - lo + 1) / 2;               // upper middle: lo = mid below
        if (canPlace(p, m, mid)) lo = mid;
        else hi = mid - 1;
    }
    return lo;
}

static boolean canPlace(int[] p, int m, int d) {         // greedy: place at the earliest valid stall
    int placed = 1, last = p[0];
    for (int i = 1; i < p.length && placed < m; i++)
        if (p[i] - last >= d) { placed++; last = p[i]; }
    return placed >= m;
}
```

`[1, 2, 3, 4, 7], m = 3` → `3` (positions 1, 4, 7).

### 6.4 Integer square root

The largest `r` with `r² ≤ x`, a last-true search. Use `long` for `mid * mid`.

```java
static int mySqrt(int x) {
    long lo = 0, hi = x;
    while (lo < hi) {
        long mid = lo + (hi - lo + 1) / 2;
        if (mid * mid <= x) lo = mid;
        else hi = mid - 1;
    }
    return (int) lo;
}
```

`mySqrt(8) = 2`, `mySqrt(Integer.MAX_VALUE) = 46340`. With `int mid`, `mid * mid` overflows for `mid > 46340` and the comparison goes wrong. `(int) Math.sqrt(x)` is fine for `int` inputs, but for `long` inputs near `2⁶³` the `double` rounding can be off by one: correct it with a `while` loop afterwards.

### 6.5 Counting instead of finding: k-th smallest

To find the `k`-th smallest value in a structure you can't sort cheaply, binary search on the **value** `v` with the predicate "at least `k` elements are `≤ v`". The first such `v` is the answer, and it's guaranteed to be an actual element.

**`k`-th smallest in an `m × n` multiplication table** (entry `(i, j)` is `i·j`): row `i` has `min(v / i, n)` entries `≤ v`.

```java
static int kthInMultiplicationTable(int m, int n, int k) {
    int lo = 1, hi = m * n;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        int count = 0;
        for (int i = 1; i <= m; i++) count += Math.min(mid / i, n);
        if (count >= k) hi = mid;
        else lo = mid + 1;
    }
    return lo;
}
```

`O(m log(mn))` instead of building and sorting `mn` entries. The same pattern solves "k-th smallest in a sorted matrix" ([[#8.3 k-th smallest in a sorted matrix|§8.3]]), "k-th smallest pair distance" (count pairs with two pointers), and "k-th smallest prime fraction".

### 6.6 Real-valued binary search

When the answer is a real number, loop a **fixed number of times** instead of `while (hi − lo > eps)`:

```java
static double cubeRoot(double x) {
    double lo = Math.min(-1, x), hi = Math.max(1, x);   // the root lies in this range for any x
    for (int it = 0; it < 100; it++) {                   // each step halves: 2⁻¹⁰⁰ of the range
        double mid = (lo + hi) / 2;
        if (mid * mid * mid < x) lo = mid;
        else hi = mid;
    }
    return lo;
}
```

> [!warning] `while (hi - lo > 1e-9)` can loop forever
> For large values (say `lo ≈ 10¹⁰`), adjacent `double`s are about `2·10⁻⁶` apart, so `hi − lo` can never drop below `10⁻⁹`: `mid` rounds to `lo` or `hi` and nothing changes. A fixed iteration count (60–100) always terminates and reaches full precision. If an absolute tolerance is required, use a relative one: `hi − lo > 1e-9 * Math.max(1, Math.abs(lo))`.

> [!example]- Maximum average subarray with length ≥ k
> "Is there a subarray of length `≥ k` with average `≥ v`?" is monotone in `v`. Subtract `v` from every element; the question becomes "is there a subarray of length `≥ k` with sum `≥ 0`?", which a prefix sum and a running minimum answer in `O(n)` ([[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums]]).
> ```java
> static double maxAverage(int[] a, int k) {
>     double lo = -1e4, hi = 1e4;                     // the value range from the constraints
>     for (int it = 0; it < 100; it++) {
>         double mid = (lo + hi) / 2;
>         if (hasAverageAtLeast(a, k, mid)) lo = mid;
>         else hi = mid;
>     }
>     return lo;
> }
>
> static boolean hasAverageAtLeast(int[] a, int k, double avg) {
>     double sum = 0, prev = 0, minPrev = 0;          // sum = P[i+1], prev = P[i+1−k]
>     for (int i = 0; i < k; i++) sum += a[i] - avg;
>     if (sum >= 0) return true;
>     for (int i = k; i < a.length; i++) {
>         sum += a[i] - avg;
>         prev += a[i - k] - avg;
>         minPrev = Math.min(minPrev, prev);          // best (smallest) prefix to cut off
>         if (sum - minPrev >= 0) return true;
>     }
>     return false;
> }
> ```
> `[1, 12, −5, −6, 50, 3], k = 4` → `12.75` (`[12, −5, −6, 50]`). Turning "maximise a ratio" into "is the ratio `≥ v`?" by subtracting `v` is a standard trick (fractional programming).

---

## 7. Rotated Sorted Arrays

A sorted array rotated at an unknown pivot, like `[4, 5, 6, 7, 0, 1, 2]`. It's not sorted, but it's made of **two sorted runs**, and the first run's values are all larger than the second's.

![[Binary Search - Rotated Array.excalidraw|800]]

### 7.1 Search (distinct values)

At every `mid`, at least one of the halves `[lo, mid]` and `[mid, hi]` is sorted. Check whether the target lies in the sorted half's value range; if it does, search there, otherwise search the other half.

```
searchRotated(a, target):
    lo = 0; hi = n − 1
    while lo ≤ hi:
        mid = (lo + hi) / 2
        if a[mid] == target: return mid
        if a[lo] ≤ a[mid]:                               -- left half a[lo..mid] is sorted
            if a[lo] ≤ target < a[mid]: hi = mid − 1
            else: lo = mid + 1
        else:                                            -- right half a[mid..hi] is sorted
            if a[mid] < target ≤ a[hi]: lo = mid + 1
            else: hi = mid − 1
    return −1
```

```java
static int searchRotated(int[] a, int target) {
    int lo = 0, hi = a.length - 1;
    while (lo <= hi) {
        int mid = (lo + hi) >>> 1;
        if (a[mid] == target) return mid;
        if (a[lo] <= a[mid]) {
            if (a[lo] <= target && target < a[mid]) hi = mid - 1;
            else lo = mid + 1;
        } else {
            if (a[mid] < target && target <= a[hi]) lo = mid + 1;
            else hi = mid - 1;
        }
    }
    return -1;
}
```

> [!warning] `a[lo] <= a[mid]`, not `<`
> When `lo == mid` (a two-element range), the left "half" is the single element `a[lo]`, which is trivially sorted. With `<`, the code decides the **right** half is sorted, and on `[3, 1]` searching for `1` it checks `3 < 1 ≤ 1`, which is false, and moves `hi` left, missing the `1`.

### 7.2 Find the minimum (the rotation point)

Compare `a[mid]` with `a[hi]`. If `a[mid] > a[hi]`, the drop is to the right of `mid`, so the minimum is in `(mid, hi]`. Otherwise `a[mid..hi]` is sorted, and the minimum is at `mid` or to its left.

```java
static int findMinIndex(int[] a) {                // distinct values
    int lo = 0, hi = a.length - 1;
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (a[mid] > a[hi]) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}
```

The index of the minimum is also the **number of rotations** (how many positions the sorted array was rotated right). `[4, 5, 6, 7, 0, 1, 2]` → index 4.

> [!warning] Compare with `a[hi]`, not `a[lo]`
> `a[mid] > a[lo]` doesn't tell you which side the minimum is on: in an **unrotated** array `[1, 2, 3, 4, 5]`, `a[mid] > a[lo]` and the minimum is on the left; in `[3, 4, 5, 1, 2]`, also `a[mid] > a[lo]`, and the minimum is on the right. Comparing with `a[hi]` has no such ambiguity. Another way to search a rotated array: find the minimum's index first, then run an ordinary binary search on the correct sorted run.

### 7.3 With duplicates

When `a[lo] == a[mid] == a[hi]`, there's no way to tell which side the drop is on: `[1, 1, 1, 0, 1]` and `[1, 0, 1, 1, 1]` look the same at those three positions. The only safe move is to shrink by one.

```java
static int findMinDup(int[] a) {
    int lo = 0, hi = a.length - 1;
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (a[mid] > a[hi]) lo = mid + 1;
        else if (a[mid] < a[hi]) hi = mid;
        else hi--;                       // a[mid] == a[hi]: a[hi] has a copy at mid, drop it
    }
    return a[lo];
}

static boolean searchRotatedDup(int[] a, int target) {
    int lo = 0, hi = a.length - 1;
    while (lo <= hi) {
        int mid = (lo + hi) >>> 1;
        if (a[mid] == target) return true;
        if (a[lo] == a[mid] && a[mid] == a[hi]) { lo++; hi--; }    // can't tell: shrink both ends
        else if (a[lo] <= a[mid]) {
            if (a[lo] <= target && target < a[mid]) hi = mid - 1;
            else lo = mid + 1;
        } else {
            if (a[mid] < target && target <= a[hi]) lo = mid + 1;
            else hi = mid - 1;
        }
    }
    return false;
}
```

> [!important] Duplicates make it O(n) in the worst case
> On `[1, 1, 1, …, 1, 0, 1, …, 1]`, every step can only discard one element, and any algorithm must potentially look at every position to find the `0`. Interviewers often ask exactly this follow-up: the answer is that `O(log n)` is impossible in the worst case, not that a cleverer comparison exists.

---

## 8. 2D Matrices

### 8.1 Fully sorted matrix

Each row sorted, and each row's first element greater than the previous row's last. Reading the rows one after another gives a sorted array of `R·C` elements; index `k` is cell `(k / C, k % C)`.

```java
static boolean searchMatrix(int[][] m, int target) {
    int rows = m.length, cols = m[0].length;
    int lo = 0, hi = rows * cols - 1;           // rows * cols can overflow int for huge matrices
    while (lo <= hi) {
        int mid = (lo + hi) >>> 1;
        int v = m[mid / cols][mid % cols];
        if (v == target) return true;
        if (v < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return false;
}
```

`O(log(R·C))`.

### 8.2 Rows and columns sorted: staircase search

Each row sorted left to right, each column sorted top to bottom, but rows can overlap in value. Binary search alone doesn't work. Start at the **top-right** corner: everything to its left is smaller, everything below is larger. So one comparison eliminates a whole row or a whole column.

```
staircase(m, target):
    r = 0; c = cols − 1
    while r < rows and c ≥ 0:
        if m[r][c] == target: return true
        if m[r][c] > target: c −= 1          -- the whole column below is even larger
        else: r += 1                         -- the whole row to the left is even smaller
    return false
```

```java
static boolean searchMatrix2(int[][] m, int target) {
    int r = 0, c = m[0].length - 1;
    while (r < m.length && c >= 0) {
        if (m[r][c] == target) return true;
        if (m[r][c] > target) c--;
        else r++;
    }
    return false;
}
```

![[Binary Search - Staircase Search.excalidraw|800]]

`O(R + C)`. Starting from the **top-left** (or bottom-right) doesn't work: both neighbours are larger (or both smaller), so a comparison doesn't tell you which way to go. The bottom-left corner works symmetrically. Binary searching each row is `O(R log C)`, better only when there are few long rows.

### 8.3 k-th smallest in a sorted matrix

Binary search on the value; count the entries `≤ v` with a staircase walk in `O(n)`.

```java
static int kthSmallest(int[][] m, int k) {          // n × n, rows and columns sorted
    int n = m.length;
    int lo = m[0][0], hi = m[n - 1][n - 1];
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;               // values may be negative: not >>> 1
        if (countAtMost(m, mid) >= k) hi = mid;
        else lo = mid + 1;
    }
    return lo;
}

static int countAtMost(int[][] m, int x) {
    int n = m.length, count = 0, c = n - 1;
    for (int r = 0; r < n; r++) {
        while (c >= 0 && m[r][c] > x) c--;          // c only moves left: O(n) total
        count += c + 1;
    }
    return count;
}
```

`[[1, 5, 9], [10, 11, 13], [12, 13, 15]], k = 8` → `13`. `O(n log(max − min))`. A min-heap of row heads gives `O(k log n)`, better for small `k`.

---

## 9. More Variants

### 9.1 Peak element (binary search on an unsorted array)

Find any index whose value is greater than its neighbours (with `a[−1] = a[n] = −∞`, and adjacent elements distinct). If `a[mid] < a[mid + 1]`, the values rise to the right of `mid`; since they must eventually "fall" to `−∞` at index `n`, there is a peak in `(mid, hi]`.

```java
static int findPeak(int[] a) {
    int lo = 0, hi = a.length - 1;
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;              // mid < hi, so a[mid + 1] exists
        if (a[mid] < a[mid + 1]) lo = mid + 1;  // uphill to the right: a peak is there
        else hi = mid;                          // downhill: mid or something left of it
    }
    return lo;
}
```

The predicate "`a[i] > a[i + 1]`" isn't monotone over the whole array, but the invariant "a peak exists in `[lo, hi]`" is preserved, and that's all binary search needs. The same code finds the maximum of a **bitonic** array (strictly increasing, then strictly decreasing); with plateaus (`a[mid] == a[mid + 1]`), it can fail.

### 9.2 Single element in a sorted array of pairs

Every element appears twice except one: `[1, 1, 2, 3, 3, 4, 4, 8, 8]` → `2`. Before the single element, each pair starts at an **even** index; after it, at an odd index.

```java
static int singleNonDuplicate(int[] a) {
    int lo = 0, hi = a.length - 1;
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (mid % 2 == 1) mid--;                // look at the pair starting at an even index
        if (a[mid] == a[mid + 1]) lo = mid + 2; // pair intact: the single one is further right
        else hi = mid;                          // pair broken: the single one is at mid or left
    }
    return a[lo];
}
```

`O(log n)`. XOR of all elements gives the answer in `O(n)` and works without sorting ([[DSA/01 - Foundations/03 - Bit Manipulation|Bit Manipulation]]), but doesn't use the sorted structure.

### 9.3 Exponential (galloping) search

When the size is unknown or huge (an "infinite" sorted stream, an API `get(i)` that returns a sentinel past the end), or the target is likely near the front: double `hi` until `a[hi] ≥ target`, then binary search in `[hi/2, hi]`.

```java
static int exponentialSearch(int[] a, int target) {
    if (a.length == 0) return -1;
    int hi = 1;
    while (hi < a.length && a[hi] < target) hi *= 2;
    int lo = hi / 2;
    hi = Math.min(hi, a.length - 1);
    while (lo <= hi) {
        int mid = (lo + hi) >>> 1;
        if (a[mid] == target) return mid;
        if (a[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
```

`O(log p)` where `p` is the target's position, not the array's size. TimSort's "galloping mode" uses exactly this when one run keeps winning the merge.

### 9.4 K closest elements

Return the `k` elements closest to `x` from a sorted array (ties go to the smaller element). The answer is a contiguous window `a[s..s+k)`; binary search for its **start** `s` in `[0, n − k]`. Compare the two elements that a window starting at `mid` would have to choose between: `a[mid]` (in) and `a[mid + k]` (out).

```java
static List<Integer> findClosest(int[] a, int k, int x) {
    int lo = 0, hi = a.length - k;
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (x - a[mid] > a[mid + k] - x) lo = mid + 1;    // a[mid + k] is strictly closer: shift right
        else hi = mid;
    }
    List<Integer> res = new ArrayList<>();
    for (int i = lo; i < lo + k; i++) res.add(a[i]);
    return res;
}
```

> [!warning] Don't compare absolute values
> `Math.abs(x - a[mid]) > Math.abs(a[mid + k] - x)` looks equivalent but breaks when `a[mid]` and `a[mid + k]` are **equal**, or both on the same side of `x`. For `a = [1, 2, 2, 4, 4, 4, 4], k = 1, x = 5`, the first probe is `mid = 3`: `a[3] = a[4] = 4`, the absolute distances tie, and the search moves **left**, ending at `[2]`. The signed version computes `5 − 4 = 1 > 4 − 5 = −1`, moves right, and returns `[4]`. Signed differences say which element is further **to the left**, which is what decides the direction.

### 9.5 Median of two sorted arrays (advanced)

Find the median of the union of two sorted arrays in `O(log(min(m, n)))`.

> [!example]- Partition binary search
> Choose how many elements `i` of the shorter array `a` go to the "left half" of the merged order; then `j = half − i` elements of `b` must go there too, where `half = ⌈(m + n)/2⌉`. The partition is correct when every left element is `≤` every right element: `a[i−1] ≤ b[j]` and `b[j−1] ≤ a[i]`. If `a[i−1] > b[j]`, too many elements come from `a`: decrease `i`. Otherwise increase it.
> ```java
> static double findMedianSortedArrays(int[] a, int[] b) {
>     if (a.length > b.length) return findMedianSortedArrays(b, a);   // binary search the shorter one
>     int m = a.length, n = b.length, half = (m + n + 1) / 2;
>     int lo = 0, hi = m;
>     while (lo <= hi) {
>         int i = (lo + hi) >>> 1;
>         int j = half - i;
>         int aLeft  = i == 0 ? Integer.MIN_VALUE : a[i - 1];
>         int aRight = i == m ? Integer.MAX_VALUE : a[i];
>         int bLeft  = j == 0 ? Integer.MIN_VALUE : b[j - 1];
>         int bRight = j == n ? Integer.MAX_VALUE : b[j];
>         if (aLeft <= bRight && bLeft <= aRight) {
>             int leftMax = Math.max(aLeft, bLeft);
>             if ((m + n) % 2 == 1) return leftMax;
>             return (leftMax + (double) Math.min(aRight, bRight)) / 2;   // double: no int overflow
>         }
>         if (aLeft > bRight) hi = i - 1;
>         else lo = i + 1;
>     }
>     throw new IllegalArgumentException("inputs not sorted");
> }
> ```
> `[1, 3]` and `[2]` → `2.0`; `[1, 2]` and `[3, 4]` → `2.5`. Searching the **shorter** array guarantees `0 ≤ j ≤ n`. The sentinels `MIN_VALUE`/`MAX_VALUE` stand for "no element on this side"; if the arrays may contain those values, use `long` sentinels.

### 9.6 Elsewhere

- **Longest increasing subsequence** in `O(n log n)`: binary search into the array of smallest tails ([[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]]).
- **Weighted random pick**: binary search the prefix sums for the first one `> r` ([[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums]]).
- **Two sum on a sorted array** for each element: `O(n log n)`, but [[DSA/03 - Sorting and Searching/03 - Two Pointers|two pointers]] do it in `O(n)`.
- **Binary lifting** on trees ([[DSA/05 - Graphs/07 - Lowest Common Ancestor|Lowest Common Ancestor]]) and **parallel binary search** are the same halving idea on other structures.

---

## 10. Ternary Search (advanced)

For a **unimodal** function (strictly increasing then strictly decreasing), find the maximum. Evaluate two interior points `m1 < m2`. If `f(m1) < f(m2)`, the maximum can't be in `[lo, m1]`: if it were, `f` would already be decreasing at `m1`, and `f(m2)` would be smaller. Otherwise, it can't be in `[m2, hi]`. Each step removes a third of the range.

```java
static double ternaryMin(double lo, double hi, DoubleUnaryOperator f) {   // convex f: find the minimum
    for (int it = 0; it < 200; it++) {             // (2/3)²⁰⁰: far below double precision
        double m1 = lo + (hi - lo) / 3, m2 = hi - (hi - lo) / 3;
        if (f.applyAsDouble(m1) < f.applyAsDouble(m2)) hi = m2;
        else lo = m1;
    }
    return (lo + hi) / 2;
}

static int ternaryMax(int lo, int hi, IntUnaryOperator f) {    // integers, strictly unimodal
    while (hi - lo > 2) {
        int m1 = lo + (hi - lo) / 3, m2 = hi - (hi - lo) / 3;
        if (f.applyAsInt(m1) < f.applyAsInt(m2)) lo = m1 + 1;
        else hi = m2 - 1;
    }
    int best = lo;                                 // at most 3 candidates left: check them all
    for (int x = lo + 1; x <= hi; x++) if (f.applyAsInt(x) > f.applyAsInt(best)) best = x;
    return best;
}
```

> [!tip] On integers, use binary search on the slope instead
> For integer domains, "first `x` with `f(x) > f(x + 1)`" is a monotone predicate on a unimodal function, and a plain `firstTrue` finds the maximum with one comparison of two evaluations per step. It's simpler and avoids the "last few candidates" cleanup. This is exactly the peak-element search of [[#9.1 Peak element (binary search on an unsorted array)|§9.1]].

> [!warning] Plateaus break ternary search
> If `f(m1) == f(m2)` on a flat stretch that isn't the maximum (`f` not **strictly** unimodal), there's no way to tell which side to discard, and the search may throw away the peak. Ternary search is only correct when the function is strictly increasing then strictly decreasing (or flat **only** at the optimum). Typical valid uses: minimising a convex function, such as the total distance `Σ |x − pᵢ|` or the maximum distance from a moving point.

**Golden-section search** chooses the two points so that one of them can be reused in the next step, needing one function evaluation per step instead of two. It only matters when `f` is expensive.

---

## 11. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| `mid = (lo + hi) / 2` with large indices | negative index, crash | `lo + (hi − lo) / 2` or `>>> 1` |
| `(lo + hi) / 2` or `>>> 1` with negative bounds | wrong middle, infinite loop | `lo + (hi − lo) / 2` |
| `lo = mid` with the lower middle | infinite loop when `hi = lo + 1` | round up: `lo + (hi − lo + 1) / 2` |
| `while (lo <= hi)` with `hi = mid` | infinite loop when `lo == hi` | `lo < hi` for the converging style |
| `hi = n − 1` for lower bound | "none" can't be returned | `hi = n` |
| `if (Arrays.binarySearch(...) > 0)` | index 0 counted as "not found" | `>= 0` |
| Expecting the first occurrence from `Arrays.binarySearch` | arbitrary duplicate returned | `lowerBound` |
| `int mid; mid * mid` in square root | overflow | `long` |
| Answer range that doesn't contain the answer | wrong answer on edge cases | prove `lo` and `hi` bounds (e.g. `lo = max(w)`) |
| Check function counting in `int` | overflow, wrong direction | `long` accumulators |
| Using a non-monotone predicate | wrong answer, no error | verify monotonicity before searching |
| `a[lo] < a[mid]` in rotated search | fails on two-element ranges | `<=` |
| Comparing with `a[lo]` to find the rotated minimum | wrong on unrotated input | compare with `a[hi]` |
| Expecting `O(log n)` on rotated arrays with duplicates | — | worst case is `O(n)` |
| `while (hi − lo > 1e-9)` on doubles | infinite loop | fixed iteration count |
| Staircase search from the top-left corner | can't decide direction | top-right or bottom-left |
| Ternary search on a function with plateaus | loses the optimum | strictly unimodal only |
| Binary search on an unsorted array | silently wrong | sort first, or don't |

---

## 12. Trick Questions and Special Cases

> [!question]- `Arrays.binarySearch(new int[]{1, 2, 2, 2, 3, 5}, 2)` — which index?
> Any of 1, 2, 3; the spec doesn't say. (This particular call returns 2, the first middle it probes.) For the first occurrence, use `lowerBound` (index 1); for the last, `upperBound − 1` (index 3).

> [!question]- `Arrays.binarySearch(new int[]{1, 3, 5}, 0)` — why `−1` and not `0`?
> The return value for "not found" is `−(insertionPoint) − 1`. The insertion point is 0, so the result is `−1`. If it were just `−insertionPoint`, inserting at position 0 would give `0`, indistinguishable from "found at index 0". `~r` (bitwise NOT) converts back: `~(−1) = 0`.

> [!question]- A binary search with `while (lo < hi) { mid = (lo + hi) / 2; if (ok(mid)) lo = mid; else hi = mid − 1; }` hangs. Why?
> When `hi = lo + 1`, `mid = lo`. If `ok(lo)` is true, `lo = mid = lo`, and nothing changes. Branches that assign `lo = mid` need the **upper** middle, `(lo + hi + 1) / 2`.

> [!question]- What's `(lo + hi) / 2` for `lo = −3`, `hi = −2`? And `(lo + hi) >>> 1`?
> `−2` and `2147483645`. Java's `/` truncates toward zero, so `−5 / 2 = −2` (the upper middle), and `>>> 1` treats `−5` as the unsigned number `2³² − 5`. `lo + (hi − lo) / 2 = −3` and `(lo + hi) >> 1 = −3` both round down. This matters when binary searching an answer range that includes negative numbers.

> [!question]- Can binary search find anything in an unsorted array?
> Yes, if the question has a monotone or invariant structure. A **peak element** can be found in `O(log n)` in any array with distinct neighbours: if `a[mid] < a[mid + 1]`, there's a peak to the right. The array isn't sorted, but the invariant "a peak lies in `[lo, hi]`" is maintained.

> [!question]- Search for `1` in the rotated array `[3, 1]`. What goes wrong with `a[lo] < a[mid]`?
> `lo = 0, hi = 1, mid = 0`. `a[0] = 3 ≠ 1`. With `<`, `3 < 3` is false, so the code assumes the right half `[mid..hi] = [3, 1]` is sorted, checks `3 < 1 ≤ 1` (false), and sets `hi = mid − 1 = −1`. Not found. With `<=`, it correctly treats `[3]` as the sorted half, sees `1` isn't in `[3, 3)`, and moves `lo` right to find it.

> [!question]- Minimum of a rotated array with duplicates `[1, 1, 1, 0, 1]` — can it be done in O(log n)?
> Not in the worst case. `a[lo] = a[mid] = a[hi] = 1`, and `[1, 0, 1, 1, 1]` gives the same three values with the `0` on the other side. Any algorithm may have to inspect every element, so the worst case is `Θ(n)`. The standard code shrinks `hi` by one in that case.

> [!question]- Integer square root of `2147395599`: what does `int mid` give?
> Garbage: `mid * mid` overflows `int` for `mid > 46340`, so the comparison with `x` can go either way. The correct answer is `46339` (`46339² = 2147302921 ≤ 2147395599 < 46340² = 2147395600`). Use `long mid`, or compare `mid <= x / mid` (careful with `mid = 0`).

> [!question]- Ship packages: why must the lower bound be `max(weights)` and not 1?
> Capacities below the heaviest package are infeasible, but the greedy check doesn't notice: it just starts a new day for the heavy package and continues, overloading that day. It can report a small number of days for an impossible capacity, and the binary search returns a capacity that doesn't actually work. Starting at `lo = max(weights)` makes every candidate at least physically possible.

> [!question]- "Find the minimum number of days to make `m` bouquets", "minimum speed to arrive on time", "smallest divisor given a threshold": what do they have in common?
> All are binary search on the answer: a numeric answer, a range that contains it, and a monotone `O(n)` check (more days ⇒ more flowers bloomed; higher speed ⇒ less time; larger divisor ⇒ smaller sum). Spot the monotonicity, choose first-true or last-true, and the code is the same template.

> [!question]- In a row-and-column-sorted matrix, why does the search start at the top-right corner?
> From the top-right, moving left decreases the value and moving down increases it, so every comparison has exactly one useful direction and eliminates a full row or column: `O(R + C)`. From the top-left, both moves increase the value, so a "too small" result doesn't say which way to go.

> [!question]- K closest elements to `x = 5` in `[1, 2, 2, 4, 4, 4, 4]` with `k = 1`?
> `[4]`. The signed comparison `x − a[mid] > a[mid + k] − x` gets it. Comparing `Math.abs` values returns `[2]`: at `mid = 3`, both `a[3]` and `a[4]` are `4`, the absolute distances tie, and the search wrongly moves left.

> [!question]- Real-valued binary search with `while (hi - lo > 1e-9)` on values around `10¹²`: what happens?
> It never ends. Consecutive `double`s near `10¹²` are about `1.2·10⁻⁴` apart, so `hi − lo` gets stuck at that gap: `mid` rounds to `lo` or `hi` and the range stops shrinking. Loop a fixed 100 times instead.

> [!question]- Does binary search need the whole array in memory?
> No, only random access to `O(log n)` positions. That's why it works on answers (the "array" of candidate answers is never built), on huge sorted files (seek to the middle byte), and on functions. Exponential search works even when the length is unknown.

---

## 13. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| Steps for `n = 10⁹` | ≈ 30 | `log₂ 10⁹` |
| `lowerBound([1,2,2,2,3,5], 2)` | `1` | first `≥ 2` |
| `upperBound([1,2,2,2,3,5], 2)` | `4` | first `> 2` |
| `lowerBound(..., 9)` (larger than all) | `n` | needs `hi = n` |
| Count of `x` | `upperBound − lowerBound` | |
| `Arrays.binarySearch([1,2,2,2,3,5], 4)` | `−6` | `−(5) − 1` |
| `Arrays.binarySearch([1,3,5], 0)` | `−1` | insertion point 0 |
| `Arrays.binarySearch` with duplicates | any matching index | unspecified |
| `(−3 + −2) / 2` | `−2` | truncation toward zero |
| `(−3 + −2) >>> 1` | `2147483645` | unsigned shift |
| `lo = mid` with `mid = (lo + hi) / 2` | infinite loop possible | use the upper middle |
| `mySqrt(Integer.MAX_VALUE)` | `46340` | needs `long` |
| Rotated search, duplicates, worst case | `O(n)` | `[1,1,1,0,1]` |
| Rotated minimum: compare with | `a[hi]` | `a[lo]` is ambiguous |
| Staircase search | `O(R + C)` | from the top-right |
| Peak element in an unsorted array | `O(log n)` | invariant, not sortedness |
| Exponential search | `O(log p)` | `p` = position of target |
| Real binary search | fixed 100 iterations | `eps` loops may not end |
| Ternary search per step | keeps `2/3` of the range | binary search on the slope keeps `1/2` |
| Median of two sorted arrays | `O(log min(m, n))` | partition the shorter array |

---

## 14. Summary

- Binary search finds the boundary of a **monotone predicate** in `O(log n)`. Sorted arrays are one case; answer spaces, rotated arrays, and peaks are others.
- Use invariants. Pick one style and stay in it: closed `[lo, hi]` with `lo <= hi` for exact search; converging `lo < hi` with `hi = mid` / `lo = mid + 1` for first-true; upper middle whenever a branch sets `lo = mid`.
- **Lower bound** (first `≥ x`) and **upper bound** (first `> x`) with `hi = n` answer first/last occurrence, counts, floor, ceiling, and insertion position.
- `Arrays.binarySearch` returns any matching index or `−(insertion point) − 1`.
- **Binary search on the answer** turns "minimise the maximum" / "maximise the minimum" into `log(range)` greedy checks. Get the range right and use `long` in the check.
- **Rotated arrays**: one half is always sorted; compare with `a[hi]` for the minimum; duplicates force `O(n)` worst case.
- **2D**: treat a fully sorted matrix as 1D; use the staircase from the top-right for row/column-sorted matrices; count-and-search for the `k`-th smallest.
- Real-valued searches: fixed iteration counts. **Ternary search** finds the optimum of a strictly unimodal function; on integers, binary search on the slope instead.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms|Sorting Algorithms]] · Next: [[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]]
- [[DSA/01 - Foundations/01 - Complexity Analysis|Complexity Analysis]]: why halving gives `log n`
- [[DSA/02 - Linear Data Structures/01 - Arrays|Arrays]]: rotation and the offset view of a rotated array
- [[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]]: binary search over prefix sums
- [[DSA/04 - Trees and Hierarchical Structures/02 - Binary Search Trees|Binary Search Trees]] and [[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]]: binary search with insertions and deletions
- [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]]: LIS in `O(n log n)`
