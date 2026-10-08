# Fenwick Trees (Binary Indexed Trees)

A <span class="hl-blue">Fenwick tree</span> (binary indexed tree, BIT) supports two operations on an array in `O(log n)` each: **add** a value to one element, and get a **prefix sum** `a[0] + … + a[i]`. Range sums follow as a difference of two prefixes. It does what a sum segment tree does, in about ten lines, `n + 1` array slots, and with a smaller constant, by storing partial sums whose ranges are determined by the **binary representation** of the index: entry `i` holds the sum of the last `lowbit(i)` elements up to `i`, where `lowbit(i) = i & −i`.

The trade-off is generality: a Fenwick tree needs an **invertible** operation (sum, XOR, counts) to answer arbitrary ranges, so it can't replace a segment tree for range min/max. This note covers how the index arithmetic works, the basic operations, `O(n)` construction, range-update variants (difference arrays and the two-tree trick), binary-lifting search for the `k`-th element, counting inversions and similar order statistics with coordinate compression, prefix-maximum Fenwick trees (for LIS), and 2D Fenwick trees.

## Contents

- [[#1. The Idea|1. The Idea]]
- [[#2. Prefix Query and Point Update|2. Prefix Query and Point Update]]
- [[#3. Building in O(n)|3. Building in O(n)]]
- [[#4. Range Updates|4. Range Updates]]
- [[#5. Searching: k-th Element by Binary Lifting|5. Searching: k-th Element by Binary Lifting]]
- [[#6. Counting with Coordinate Compression|6. Counting with Coordinate Compression]]
- [[#7. Prefix Maximum Fenwick Trees|7. Prefix Maximum Fenwick Trees]]
- [[#8. 2D Fenwick Trees|8. 2D Fenwick Trees]]
- [[#9. Fenwick Tree vs. Segment Tree|9. Fenwick Tree vs. Segment Tree]]
- [[#10. Common Mistakes|10. Common Mistakes]]
- [[#11. Trick Questions and Special Cases|11. Trick Questions and Special Cases]]
- [[#12. Quick Reference — Non-Obvious Outcomes|12. Quick Reference — Non-Obvious Outcomes]]
- [[#13. Summary|13. Summary]]

---

## 1. The Idea

Use **1-based** indices `1..n`. Let `lowbit(i)` be the value of the lowest set bit of `i`, computed as `i & −i` in two's complement ([[DSA/01 - Foundations/03 - Bit Manipulation#4. Lowest and Highest Set Bit Tricks|Bit Manipulation § 4]]).

> [!note] Definition
> `tree[i]` stores the sum of the `lowbit(i)` elements ending at `i`:
>
> **`tree[i] = a[i − lowbit(i) + 1] + … + a[i]`**, i.e. the range `(i − lowbit(i), i]`.

| `i` | binary | `lowbit(i)` | `tree[i]` covers |
|---|---|---|---|
| 1 | `0001` | 1 | `a[1]` |
| 2 | `0010` | 2 | `a[1..2]` |
| 3 | `0011` | 1 | `a[3]` |
| 4 | `0100` | 4 | `a[1..4]` |
| 6 | `0110` | 2 | `a[5..6]` |
| 8 | `1000` | 8 | `a[1..8]` |
| 12 | `1100` | 4 | `a[9..12]` |

![[Fenwick - Responsibility Ranges.excalidraw|800]]

Odd indices hold a single element, multiples of 2 hold 2 elements or more, powers of two hold the whole prefix. These ranges nest like a binary tree, hence the name, but no tree is ever stored: the array **is** the tree, and moving to a parent or to the previous range is one bit operation.

**Why the 1-based index matters**: `lowbit(0) = 0`, so with index 0 in use, the update loop `i += lowbit(i)` would never advance. The usual API accepts 0-based indices and adds 1 internally.

---

## 2. Prefix Query and Point Update

**Prefix sum of `a[1..i]`**: `tree[i]` covers `(i − lowbit(i), i]`; then continue from `i − lowbit(i)`. Each step clears the lowest set bit, so there are at most `popcount(i) ≤ log₂ n` steps.

**Add `δ` to `a[i]`**: every `tree[j]` whose range contains `i` must change. Those are `i`, then `i + lowbit(i)`, then that plus its lowbit, and so on: adding the lowest set bit carries into the next range that covers `i`.

```
prefix(i):                              -- a[1] + … + a[i]
    s = 0
    while i > 0: s += tree[i]; i −= i & −i
    return s

add(i, δ):                              -- a[i] += δ
    while i ≤ n: tree[i] += δ; i += i & −i
```

![[Fenwick - Query and Update Paths.excalidraw|800]]

`prefix(13)`: `13 = 1101 → 12 = 1100 → 8 = 1000 → 0`, summing `tree[13] + tree[12] + tree[8] = a[13] + a[9..12] + a[1..8]`. `add(5)` with `n = 16`: `5 = 0101 → 6 = 0110 → 8 = 1000 → 16 = 10000`, exactly the four entries whose ranges contain position 5.

```java
static class Fenwick {                             // 0-based API; 1-based inside
    private final long[] tree;                     // tree[i] = sum of a over (i − lowbit(i), i]

    Fenwick(int n) { tree = new long[n + 1]; }

    Fenwick(int[] a) {                             // O(n) construction (§3)
        this(a.length);
        for (int i = 1; i <= a.length; i++) {
            tree[i] += a[i - 1];
            int parent = i + (i & -i);
            if (parent < tree.length) tree[parent] += tree[i];
        }
    }

    void add(int idx, long delta) {                // a[idx] += delta
        for (int i = idx + 1; i < tree.length; i += i & -i) tree[i] += delta;
    }

    long prefix(int idx) {                         // a[0] + … + a[idx]; prefix(−1) = 0
        long s = 0;
        for (int i = idx + 1; i > 0; i -= i & -i) s += tree[i];
        return s;
    }

    long rangeSum(int l, int r) { return prefix(r) - prefix(l - 1); }

    int lowerBound(long k) {                       // smallest idx with prefix(idx) ≥ k; n if none (§5)
        int pos = 0;
        for (int step = Integer.highestOneBit(tree.length - 1); step > 0; step >>= 1) {
            if (pos + step < tree.length && tree[pos + step] < k) {
                pos += step;
                k -= tree[pos];
            }
        }
        return pos;                                // 1-based pos + 1 is the answer; 0-based that's pos
    }
}
```

`a = [3, 2, −1, 6, 5, 4, −3, 3, 7, 2, 3]`: `prefix(4)` → `15`, `rangeSum(2, 5)` → `14`; after `add(3, 4)`: `rangeSum(2, 5)` → `18`.

> [!tip] Setting an element instead of adding
> The tree only knows how to add. To **set** `a[i] = v`, keep a copy of the current values and add the difference: `add(i, v − cur[i]); cur[i] = v;`. Forgetting the copy and calling `add(i, v)` adds `v` on top of the old value.

---

## 3. Building in O(n)

Calling `add` for every element costs `O(n log n)`. Instead, fill each `tree[i]` with `a[i]`, and then, in increasing order of `i`, add `tree[i]` into its parent `i + lowbit(i)`. When `i` is processed, all its children (indices smaller than `i`) have already added into it, so its range sum is complete before it's passed up. That's the second constructor above, `O(n)`.

An equivalent way: `tree[i] = P[i] − P[i − lowbit(i)]` from a prefix-sum array `P` ([[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums]]).

> [!warning] The tree array is not the prefix-sum array
> `tree[4]` happens to equal `a[1] + … + a[4]`, because 4 is a power of two, but `tree[3] = a[3]` and `tree[6] = a[5] + a[6]`. Reading `tree[i]` as "the sum up to `i`" is a common misunderstanding; always go through `prefix`.

---

## 4. Range Updates

### 4.1 Range add, point query

Store the **difference array** ([[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays#7. Difference Arrays|Prefix Sums § 7]]) in a Fenwick tree. Adding `v` to `a[l..r]` changes two differences; the current `a[i]` is the prefix sum of the differences.

```java
static class RangeAddPointQuery {
    private final Fenwick diff;

    RangeAddPointQuery(int n) { diff = new Fenwick(n + 1); }   // + 1: room for r + 1 = n

    void rangeAdd(int l, int r, long v) {
        diff.add(l, v);
        diff.add(r + 1, -v);
    }

    long get(int i) { return diff.prefix(i); }
}
```

Both operations are `O(log n)`, so updates and point reads can interleave freely, which a plain difference array can't do.

### 4.2 Range add, range sum: two trees

With differences `d`, the prefix sum of `a` is

`a[0] + … + a[i] = Σ_{j ≤ i} d[j] · (i − j + 1) = (i + 1) · Σ_{j ≤ i} d[j] − Σ_{j ≤ i} d[j] · j`.

So keep one tree for `d[j]` and one for `d[j] · j`:

```java
static class RangeAddRangeSum {
    private final Fenwick b1, b2;                  // b1: d[j], b2: d[j] · j

    RangeAddRangeSum(int n) { b1 = new Fenwick(n + 1); b2 = new Fenwick(n + 1); }

    void rangeAdd(int l, int r, long v) {
        b1.add(l, v);      b1.add(r + 1, -v);
        b2.add(l, v * l);  b2.add(r + 1, -v * (r + 1));
    }

    long prefix(int i) { return b1.prefix(i) * (i + 1) - b2.prefix(i); }   // a[0..i]

    long rangeSum(int l, int r) { return prefix(r) - prefix(l - 1); }
}
```

`n = 6`: `rangeAdd(1, 3, 5)`, `rangeAdd(2, 5, 2)` → `a = [0, 5, 7, 7, 2, 2]`, `rangeSum(0, 5)` → `23`, `rangeSum(3, 4)` → `9`. This matches a lazy segment tree for range add + range sum with much less code; for anything else (assignments, min/max), use the segment tree ([[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees#7. Lazy Propagation|Segment Trees § 7]]).

---

## 5. Searching: k-th Element by Binary Lifting

With **non-negative** elements, prefix sums are non-decreasing, so "the smallest `i` with `prefix(i) ≥ k`" can be binary searched. Binary searching with `prefix` costs `O(log² n)`; walking the tree's own structure costs `O(log n)`. Start at position 0 and try steps of `2ʲ` from the largest power of two `≤ n` down to 1: `tree[pos + 2ʲ]` is exactly the sum of the next `2ʲ` elements (because `pos` is a multiple of `2ʲ⁺¹` at that point), so take the step if that sum is still `< k`.

```
lowerBound(k):
    pos = 0
    for step = highest power of two ≤ n down to 1:
        if pos + step ≤ n and tree[pos + step] < k:
            pos += step; k −= tree[pos]
    return pos + 1                      -- 1-based; 0-based this is pos
```

That's the `lowerBound` method of the class above. Its main use is the **`k`-th smallest element of a dynamic multiset**: keep a count per value (compressed); `lowerBound(k)` is the value rank of the `k`-th smallest.

```java
// multiset of values in [0, 10): counts in a Fenwick tree
Fenwick cnt = new Fenwick(10);
for (int v : new int[]{5, 1, 5, 7, 3}) cnt.add(v, 1);
cnt.lowerBound(1);   // 1: the smallest
cnt.lowerBound(3);   // 5: sorted 1 3 5 5 7
cnt.lowerBound(4);   // 5
cnt.add(5, -2);      // remove both 5s
cnt.lowerBound(3);   // 7
cnt.lowerBound(9);   // 10 = n: fewer than 9 elements
```

This gives `TreeSet`-like order statistics (`k`-th element, rank = `prefix(v − 1)`) that `TreeSet` itself lacks ([[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees#7.3 Traps|Balanced Trees § 7.3]]), as long as the value universe is known and can be compressed.

> [!warning] Negative values break the search
> With negative elements, prefix sums aren't monotonic, and the greedy descent can skip past the answer. The search is for counts and other non-negative data.

---

## 6. Counting with Coordinate Compression

"For each element, how many earlier/later elements are smaller/larger?" is a Fenwick tree over **value ranks**: scan the array, and before inserting each value, ask how many inserted values lie in the relevant range. Values up to `10⁹` (or negative) are first **compressed** to ranks `0..m−1` by sorting the distinct values.

### 6.1 Counting inversions

An inversion is a pair `i < j` with `a[i] > a[j]`. Scan from the right; the tree holds the elements to the right of `i`, and the elements **strictly smaller** than `a[i]` among them pair with it.

```java
static long countInversions(int[] a) {
    int[] sorted = Arrays.stream(a).distinct().sorted().toArray();   // value → rank
    Fenwick seen = new Fenwick(sorted.length);
    long inv = 0;
    for (int i = a.length - 1; i >= 0; i--) {      // seen = counts of a[i+1..n−1] by rank
        int r = Arrays.binarySearch(sorted, a[i]);
        inv += seen.prefix(r - 1);                 // strictly smaller values to the right
        seen.add(r, 1);
    }
    return inv;
}
```

![[Fenwick - Counting Inversions.excalidraw|800]]

`[2, 4, 1, 3, 5]` → `3`; `[3, 3, 3]` → `0` (equal values aren't inversions, hence `prefix(r − 1)`, not `prefix(r)`); `[5, 4, 3, 2, 1]` → `10`. `O(n log n)`, the same count merge sort produces ([[DSA/03 - Sorting and Searching/01 - Sorting Algorithms#3.2 Counting inversions while merging|Sorting § 3.2]]). Keeping the per-`i` counts instead of their total answers "count of smaller numbers after self" ([[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees#8.1 Count of smaller numbers after self|Segment Trees § 8.1]]).

### 6.2 Reverse pairs: `a[i] > 2 · a[j]`

The comparison involves a **transformed** value, so compress the original values and the doubled values together:

```java
static int reversePairs(int[] a) {
    long[] vals = new long[2 * a.length];
    for (int i = 0; i < a.length; i++) { vals[2 * i] = a[i]; vals[2 * i + 1] = 2L * a[i]; }
    long[] sorted = Arrays.stream(vals).distinct().sorted().toArray();
    Fenwick seen = new Fenwick(sorted.length);     // counts of 2·a[j] for j > i
    int res = 0;
    for (int i = a.length - 1; i >= 0; i--) {
        int r = Arrays.binarySearch(sorted, (long) a[i]);
        res += seen.prefix(r - 1);                 // 2·a[j] < a[i]
        seen.add(Arrays.binarySearch(sorted, 2L * a[i]), 1);
    }
    return res;
}
```

`[1, 3, 2, 3, 1]` → `2`; `[2, 4, 3, 5, 1]` → `3`. `2L * a[i]` must be computed in `long`: for `a[i] = 2³⁰` and above, `2 * a[i]` overflows `int`.

### 6.3 More problems of this shape

| Problem | Tree indexed by | Per element |
|---|---|---|
| Count of smaller numbers after self | value rank | scan right to left, `prefix(r − 1)` |
| Count of range sum in `[lo, hi]` | rank of prefix sums `P[j]` | count earlier `P[i]` in `[P[j] − hi, P[j] − lo]` |
| Number of teams (triples `i < j < k` increasing or decreasing) | value rank | smaller-left × larger-right per middle element |
| Create sorted array via instructions (cost = min(smaller, larger) already inserted) | value rank | two prefix queries |
| Queue reconstruction / "position among the remaining" | position (1 = free) | `lowerBound(k)` finds the `k`-th free slot |

---

## 7. Prefix Maximum Fenwick Trees

Replacing `+` with `max` gives a tree that answers **prefix maxima**, with one restriction: an update may only **increase** a value. (With `max`, there's no inverse: a decrease can't be "subtracted out", and a range `[l, r]` can't be computed from two prefixes.)

That's exactly what the `O(n log n)` **longest increasing subsequence** needs: process elements left to right; the longest increasing subsequence ending at `x` is `1 +` the best length ending at any **smaller** value seen so far, a prefix maximum over value ranks.

```java
static int lengthOfLIS(int[] a) {
    int[] sorted = Arrays.stream(a).distinct().sorted().toArray();
    int m = sorted.length;
    int[] best = new int[m + 1];                   // max-Fenwick over value ranks, 1-based
    int ans = 0;
    for (int x : a) {
        int r = Arrays.binarySearch(sorted, x) + 1;
        int q = 0;
        for (int i = r - 1; i > 0; i -= i & -i) q = Math.max(q, best[i]);   // best over values < x
        int cur = q + 1;
        ans = Math.max(ans, cur);
        for (int i = r; i <= m; i += i & -i) best[i] = Math.max(best[i], cur);   // values only grow
    }
    return ans;
}
```

`[10, 9, 2, 5, 3, 7, 101, 18]` → `4`; `[7, 7, 7]` → `1` (querying ranks `< r` makes it strictly increasing; querying `≤ r` would count non-decreasing subsequences). The binary-search "patience" version is shorter ([[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]]); the Fenwick version generalises to weighted LIS (maximum **sum** increasing subsequence) and to counting LIS (store `(length, count)` pairs).

---

## 8. 2D Fenwick Trees

The same index arithmetic in each dimension: `tree[i][j]` covers rows `(i − lowbit(i), i]` × columns `(j − lowbit(j), j]`. Updates and prefix-rectangle queries are nested loops, `O(log R · log C)`.

```java
static class Fenwick2D {
    private final long[][] tree;

    Fenwick2D(int rows, int cols) { tree = new long[rows + 1][cols + 1]; }

    void add(int r, int c, long delta) {
        for (int i = r + 1; i < tree.length; i += i & -i)
            for (int j = c + 1; j < tree[0].length; j += j & -j) tree[i][j] += delta;
    }

    long prefix(int r, int c) {                    // sum of the rectangle (0, 0)..(r, c)
        long s = 0;
        for (int i = r + 1; i > 0; i -= i & -i)
            for (int j = c + 1; j > 0; j -= j & -j) s += tree[i][j];
        return s;
    }

    long sumRegion(int r1, int c1, int r2, int c2) {   // inclusion–exclusion, as with 2D prefix sums
        return prefix(r2, c2) - prefix(r1 - 1, c2) - prefix(r2, c1 - 1) + prefix(r1 - 1, c1 - 1);
    }
}
```

The query is the same inclusion–exclusion as for static 2D prefix sums ([[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays#4. 2D Prefix Sums|Prefix Sums § 4]]); the tree adds `O(log R · log C)` updates. Memory is `R · C`, which limits it to grids of a few million cells; for sparse 2D points, sort one coordinate offline and use a 1D tree over the other (a sweep line).

---

## 9. Fenwick Tree vs. Segment Tree

| | Fenwick tree | Segment tree |
|---|---|---|
| Code | ~10 lines | 30–80 lines |
| Memory | `n + 1` | `4n` (recursive) / `2n` (bottom-up) |
| Speed | faster (tight loops, no recursion) | slower constant |
| Range query | needs an **inverse** (sum, XOR, count) | any associative operation |
| Range min / max | prefix only, values only increasing | yes |
| Range update | add only (two trees for range sum) | anything with lazy tags |
| Search (`k`-th, first ≥) | `lowerBound` for non-negative sums | descent for any monotone condition |
| Composite node data (max subarray, …) | no | yes |

Rule of thumb: sums and counts with point or range-add updates → Fenwick tree. Anything else → segment tree.

---

## 10. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Using index 0 inside the tree | infinite loop in `add` (`0 & −0 = 0`) | shift to 1-based |
| Tree array of size `n` | `ArrayIndexOutOfBounds` at index `n` | size `n + 1` |
| `rangeSum(l, r) = prefix(r) − prefix(l)` | first element of the range missing | `prefix(l − 1)` |
| Calling `add(i, v)` to set a value | value accumulates | add `v − current` |
| Reading `tree[i]` as a prefix sum | wrong for non-powers of two | call `prefix(i)` |
| `prefix(r)` instead of `prefix(r − 1)` when counting smaller values | equal values counted as inversions | strict: rank − 1 |
| Not compressing values | huge or negative indices | sort distinct values, use ranks |
| `2 * a[i]` in `int` | overflow for large values | `2L * a[i]` |
| `lowerBound` with negative elements | wrong answers | only for non-negative data |
| Max-Fenwick with decreasing updates | stale maxima | segment tree |
| Range-add tree of size `n` | `r + 1 = n` out of bounds | size `n + 1` |
| `int` tree for sums | overflow | `long[]` |
| Building with `n` calls to `add` when time is tight | `O(n log n)` | linear build |

---

## 11. Trick Questions and Special Cases

> [!question]- Which elements does `tree[12]` cover? `tree[7]`? `tree[16]`?
> `12 = 1100₂`, `lowbit = 4`: `a[9..12]`. `7 = 0111₂`, `lowbit = 1`: just `a[7]`. `16 = 10000₂`: `a[1..16]`. (All 1-based.)

> [!question]- How many entries does `prefix(15)` read? `prefix(16)`? `add(1)` for `n = 16`?
> `prefix(15)`: `15 → 14 → 12 → 8`, four entries (`popcount(15) = 4`). `prefix(16)`: one entry. `add(1)`: `1 → 2 → 4 → 8 → 16`, five entries.

> [!question]- Why does `i & −i` give the lowest set bit?
> In two's complement, `−i = ~i + 1`. Inverting flips every bit; adding 1 turns the trailing 1s of `~i` (which were the trailing 0s of `i`) back to 0 and sets the first 0 (the lowest set bit of `i`) to 1. So `i` and `−i` share exactly that one bit.

> [!question]- What happens if the tree uses index 0?
> `add(0, δ)` loops forever: `0 + (0 & −0) = 0`. And `prefix(0)` never reads `tree[0]` (the loop condition `i > 0` fails), so a value stored there is invisible. Shift everything by one.

> [!question]- Can a Fenwick tree answer range minimum queries?
> Not for arbitrary ranges: the range `[l, r]` is computed as `prefix(r) − prefix(l − 1)`, and `min` has no inverse. It can maintain prefix minima if values only decrease. For range min with updates, use a segment tree.

> [!question]- Inversions of `[1, 1, 1]`? Of `[3, 1, 2]`?
> `0`: equal elements don't form inversions, so only strictly smaller values are counted. `2`: `(3, 1)` and `(3, 2)`.

> [!question]- `rangeAdd(0, n − 1, v)` on a range-add tree built with `new Fenwick(n)`?
> It calls `add(n, −v)`, which touches `tree[n + 1]`: out of bounds. The difference-array tree needs room for index `n` (size `n + 1` in 0-based terms).

> [!question]- Range add + range sum with two trees: `rangeAdd(1, 3, 5)`, `rangeAdd(2, 5, 2)` on 6 zeros. What's `rangeSum(3, 4)`?
> `9`: `a = [0, 5, 7, 7, 2, 2]`, and `a[3] + a[4] = 7 + 2`. One tree alone (the difference tree) would give point values but not range sums in `O(log n)`.

> [!question]- `lowerBound(k)` on counts: what does it return when there are fewer than `k` elements?
> `n` (one past the last valid index): the search walks all the way to the end without the prefix reaching `k`. Callers must check for it.

> [!question]- Longest strictly increasing subsequence of `[7, 7, 7]` with the max-Fenwick? What changes for non-decreasing?
> `1`. The query covers ranks strictly below `x`, so equal values can't extend each other. Querying ranks `≤ x` (prefix up to `r` instead of `r − 1`) gives the longest **non-decreasing** subsequence, `3`.

> [!question]- Does building with `n` adds and with the linear algorithm give the same `tree` array?
> Yes. Both compute exactly `tree[i] = sum of (i − lowbit(i), i]`, which is fully determined by `a`. (Unlike heaps, where different construction orders give different valid arrays.)

> [!question]- Why does the binary-lifting search start with the largest power of two `≤ n`?
> Positions are built bit by bit from the top: after choosing the higher bits, `pos` is a multiple of `2 · step`, so `tree[pos + step]` covers exactly `(pos, pos + step]`, the next `step` elements. Starting with a smaller step would make `pos + step` land on indices whose ranges extend before `pos`.

---

## 12. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `tree[i]` covers | `(i − lowbit(i), i]` | 1-based |
| `12 & −12` | `4` | lowest set bit |
| `prefix(13)` reads | `tree[13], tree[12], tree[8]` | clear lowest bit |
| `add(5)` with `n = 16` touches | `5, 6, 8, 16` | add lowest bit |
| Steps per operation | `≤ ⌊log₂ n⌋ + 1` | bits |
| Linear build | `tree[i + lowbit(i)] += tree[i]` | children before parents |
| Range sum | `prefix(r) − prefix(l − 1)` | |
| Range add, point query | Fenwick over the difference array | |
| Range add, range sum | `sum1(i)·(i + 1) − sum2(i)` | two trees |
| `countInversions([2,4,1,3,5])` | `3` | |
| `countInversions([3,3,3])` | `0` | strictly smaller |
| `reversePairs([2,4,3,5,1])` | `3` | compress `a` and `2a` together |
| `lengthOfLIS([10,9,2,5,3,7,101,18])` | `4` | max-Fenwick |
| `lowerBound` with too few elements | `n` | |
| Range min with arbitrary updates | not possible | no inverse |
| Index 0 in the tree | infinite loop | `lowbit(0) = 0` |

---

## 13. Summary

- `tree[i]` stores the sum of `(i − lowbit(i), i]` with `lowbit(i) = i & −i`, 1-based. Prefix queries clear the lowest bit (`i −= i & −i`); updates add it (`i += i & −i`). Both `O(log n)`.
- Ranges come from two prefixes, so the operation must be invertible: sums, XOR, counts.
- Build in `O(n)` by pushing each `tree[i]` into `tree[i + lowbit(i)]`.
- Range add with point queries: Fenwick over the difference array. Range add with range sums: two trees.
- Binary lifting finds the `k`-th element of a count tree in `O(log n)`.
- With coordinate compression, Fenwick trees count inversions, smaller-after-self, reverse pairs, and other rank statistics.
- A max-Fenwick works for prefix maxima under increasing updates (LIS); 2D trees nest the loops.
- For min/max ranges, assignments, or composite data, use a segment tree.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees|Segment Trees]] · Next: [[DSA/04 - Trees and Hierarchical Structures/09 - Sqrt Decomposition|Sqrt Decomposition]]
- [[DSA/01 - Foundations/03 - Bit Manipulation|Bit Manipulation]]: `i & −i` and two's complement
- [[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]]: the static versions
- [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms|Sorting Algorithms]]: counting inversions with merge sort
- [[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees|Segment Trees]]: the general alternative
- [[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]]: order statistics without a fixed universe (treaps)
- [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]]: longest increasing subsequence
