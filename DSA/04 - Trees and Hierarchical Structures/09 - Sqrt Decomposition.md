# Sqrt Decomposition and Mo's Algorithm

<span class="hl-blue">Sqrt decomposition</span> splits an array into about `√n` blocks of about `√n` elements and keeps a summary per block. A range query then consists of at most two partial blocks, handled element by element, and at most `√n` whole blocks, handled by their summaries: `O(√n)` per query. That's slower than a segment tree's `O(log n)`, but the idea is simpler, the code is short, and it works for operations that don't combine neatly in a tree, such as "how many elements in `[l, r]` are `≥ x`" with updates.

The same "balance two costs at `√n`" idea appears in other forms: splitting values into **heavy and light** by a threshold, rebuilding a structure every `√q` operations, and **Mo's algorithm**, which answers offline range queries by reordering them so that a sliding window moves only `O((n + q)√n)` steps in total. This note covers block decomposition with point and range updates, choosing the block size, blocks with sorted contents, threshold (small step / large step) splits, Mo's algorithm with its ordering and pitfalls, and when each technique beats the tree structures of the previous chapters.

## Contents

- [[#1. Block Decomposition|1. Block Decomposition]]
- [[#2. Range Updates with Block Tags|2. Range Updates with Block Tags]]
- [[#3. Choosing the Block Size|3. Choosing the Block Size]]
- [[#4. Blocks with Richer Contents|4. Blocks with Richer Contents]]
- [[#5. Threshold Splits: Small and Large Cases|5. Threshold Splits: Small and Large Cases]]
- [[#6. Mo's Algorithm|6. Mo's Algorithm]]
- [[#7. When to Use What|7. When to Use What]]
- [[#8. Common Mistakes|8. Common Mistakes]]
- [[#9. Trick Questions and Special Cases|9. Trick Questions and Special Cases]]
- [[#10. Quick Reference — Non-Obvious Outcomes|10. Quick Reference — Non-Obvious Outcomes]]
- [[#11. Summary|11. Summary]]

---

## 1. Block Decomposition

Choose a block size `B` (about `√n`). Element `i` belongs to block `i / B`; block `b` covers indices `[b·B, min(n, (b + 1)·B) − 1]`, so the **last block may be shorter**. Store one summary per block (here, its sum).

```
query(l, r):                            -- inclusive
    bl = l / B; br = r / B
    if bl = br: return a[l] + … + a[r]                 -- inside one block: just scan
    s = a[l .. end of block bl]                         -- partial left block
      + block[bl + 1] + … + block[br − 1]               -- whole blocks
      + a[start of block br .. r]                       -- partial right block
    return s

set(i, v):
    block[i / B] += v − a[i]; a[i] = v
```

![[Sqrt - Block Decomposition.excalidraw|800]]

```java
static class SqrtSum {                             // range sum, point assignment
    private final int[] a;
    private final long[] block;
    private final int B;

    SqrtSum(int[] arr) {
        a = arr.clone();
        B = Math.max(1, (int) Math.sqrt(a.length));   // max(1, …): n = 0 or 1 would give B = 0
        block = new long[(a.length + B - 1) / B];
        for (int i = 0; i < a.length; i++) block[i / B] += a[i];
    }

    void set(int i, int v) {
        block[i / B] += v - a[i];
        a[i] = v;
    }

    long query(int l, int r) {
        int bl = l / B, br = r / B;
        long s = 0;
        if (bl == br) {
            for (int i = l; i <= r; i++) s += a[i];
            return s;
        }
        for (int i = l; i < (bl + 1) * B; i++) s += a[i];    // tail of the first block
        for (int b = bl + 1; b < br; b++) s += block[b];      // whole blocks in between
        for (int i = br * B; i <= r; i++) s += a[i];          // head of the last block
        return s;
    }
}
```

Each query scans fewer than `2B` elements and fewer than `n/B` blocks: `O(B + n/B) = O(√n)` with `B = √n`. A point update is `O(1)` for sums. For **min/max**, a point update has to recompute the block's minimum from scratch, `O(B)` (min has no inverse to "subtract" the old value).

---

## 2. Range Updates with Block Tags

Like lazy propagation in a segment tree, but with one level: a range add applies to partial blocks element by element, and to whole blocks through a per-block **tag**.

```java
static class SqrtRangeAdd {                        // range add, range sum
    private final long[] a, sum, lazy;             // a[i] excludes its block's lazy tag; sum[b] includes it
    private final int B, n;

    SqrtRangeAdd(int[] arr) {
        n = arr.length;
        B = Math.max(1, (int) Math.sqrt(n));
        a = new long[n];
        int nb = (n + B - 1) / B;
        sum = new long[nb];
        lazy = new long[nb];
        for (int i = 0; i < n; i++) { a[i] = arr[i]; sum[i / B] += arr[i]; }
    }

    void rangeAdd(int l, int r, long v) {
        int bl = l / B, br = r / B;
        if (bl == br) {
            for (int i = l; i <= r; i++) a[i] += v;
            sum[bl] += v * (r - l + 1);
            return;
        }
        for (int i = l; i < (bl + 1) * B; i++) a[i] += v;
        sum[bl] += v * ((bl + 1) * B - l);
        for (int b = bl + 1; b < br; b++) { lazy[b] += v; sum[b] += v * B; }   // inner blocks are full
        for (int i = br * B; i <= r; i++) a[i] += v;
        sum[br] += v * (r - br * B + 1);
    }

    long query(int l, int r) {
        int bl = l / B, br = r / B;
        long s = 0;
        if (bl == br) {
            for (int i = l; i <= r; i++) s += a[i] + lazy[bl];
            return s;
        }
        for (int i = l; i < (bl + 1) * B; i++) s += a[i] + lazy[bl];
        for (int b = bl + 1; b < br; b++) s += sum[b];
        for (int i = br * B; i <= r; i++) s += a[i] + lazy[br];
        return s;
    }
}
```

Blocks strictly between `bl` and `br` are never the last block, so they always have exactly `B` elements, and `v · B` is correct for them. Tags never need pushing down: the true value of `a[i]` is always `a[i] + lazy[i / B]`. (For **range assignment**, a block-level "assigned value" tag that overrides the elements is used instead, and partial updates must first write the pending assignment into the block's elements.)

---

## 3. Choosing the Block Size

With block size `B`, a query costs `O(B)` for the partial blocks plus `O(n/B)` for the whole blocks. The sum `B + n/B` is smallest when the two terms are equal: `B = √n`, giving `2√n`.

When the two parts have different costs, balance those instead:

| Situation | Costs | Best `B` |
|---|---|---|
| Plain sums | `B + n/B` | `√n` |
| Block summary needs a sorted block (binary search per block) | `B + (n/B) · log B` | `≈ √(n log n)` |
| Update rebuilds a block in `O(B log B)`, query is `O(B + n/B)` | depends on the update/query ratio | tune |
| Mo's algorithm with `q` queries | `q · B + n · (n/B)` | `n / √q` |

In practice, constant factors matter as much as the formula: `√(10⁵) ≈ 316`, and trying `B` in a range like 200–700 is a common last-step optimisation. Computing `B` with `(int) Math.sqrt(n)` gives 0 for `n = 0`, so always take `max(1, …)`.

---

## 4. Blocks with Richer Contents

The strength of sqrt decomposition is that a block's summary can be **anything that's cheap to query and rebuild**, not just something that merges in `O(1)`.

**How many elements of `a[l..r]` are `≥ x`, with point updates?** A segment tree would need sorted lists in every node and couldn't update them cheaply (the merge-sort tree of [[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees#10. Merge-Sort Tree (advanced)|Segment Trees § 10]] is static). With blocks, keep a **sorted copy** of each block: whole blocks are answered by binary search, partial blocks by scanning, and an update fixes one sorted copy by moving a single element.

```java
static class SqrtCountAtLeast {
    private final int[] a;
    private final int[][] sorted;                  // sorted copy of each block
    private final int B;

    SqrtCountAtLeast(int[] arr) {
        a = arr.clone();
        B = Math.max(1, (int) Math.sqrt(a.length));
        int nb = (a.length + B - 1) / B;
        sorted = new int[nb][];
        for (int b = 0; b < nb; b++) {
            sorted[b] = Arrays.copyOfRange(a, b * B, Math.min(a.length, (b + 1) * B));
            Arrays.sort(sorted[b]);
        }
    }

    void set(int i, int v) {                       // O(B): replace one value, slide it into place
        int[] s = sorted[i / B];
        int p = Arrays.binarySearch(s, a[i]);      // a position holding the old value
        s[p] = v;
        a[i] = v;
        while (p > 0 && s[p - 1] > s[p]) { int t = s[p]; s[p] = s[p - 1]; s[p - 1] = t; p--; }
        while (p + 1 < s.length && s[p + 1] < s[p]) { int t = s[p]; s[p] = s[p + 1]; s[p + 1] = t; p++; }
    }

    int countAtLeast(int l, int r, int x) {
        int bl = l / B, br = r / B, c = 0;
        if (bl == br) {
            for (int i = l; i <= r; i++) if (a[i] >= x) c++;
            return c;
        }
        for (int i = l; i < (bl + 1) * B; i++) if (a[i] >= x) c++;
        for (int b = bl + 1; b < br; b++) c += sorted[b].length - lowerBound(sorted[b], x);
        for (int i = br * B; i <= r; i++) if (a[i] >= x) c++;
        return c;
    }

    private static int lowerBound(int[] s, int x) {    // first index with s[i] ≥ x
        int lo = 0, hi = s.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (s[mid] < x) lo = mid + 1; else hi = mid;
        }
        return lo;
    }
}
```

`[5, 1, 4, 2, 8, 3, 7, 6, 9]`: `countAtLeast(1, 7, 4)` → `4` (`4, 8, 7, 6`); after `set(3, 10)`, → `5`. Query `O(√n log n)`, update `O(√n)`. The same "sorted blocks" pattern answers "`k`-th smallest in a range with updates" by binary searching on the value.

Other block contents that work the same way:

| Block keeps | Answers |
|---|---|
| a frequency map / count array | "how many times does `x` occur in `[l, r]`?" with updates |
| a sorted copy | counts `≥ x`, `≤ x`; `k`-th smallest by binary search on the value |
| a bitset of present values | distinct values, mex with small value ranges |
| a linked list of fixed capacity (split when too big) | insert/delete at any position with `O(√n)` index lookup (a "rope" made of blocks) |

---

## 5. Threshold Splits: Small and Large Cases

Many problems have a parameter where small values are cheap to **precompute** and large values are cheap to **brute force**. Splitting at `√n` makes both sides `O(√n)` per query (or `O(n√n)` in total).

**Sums over evenly spaced indices**: for each query `(x, y)`, return `a[x] + a[x + y] + a[x + 2y] + …` (modulo `10⁹ + 7`).

- Large step `y ≥ √n`: at most `n / y ≤ √n` terms, so add them directly.
- Small step `y < √n`: precompute the suffix sums `suf[i] = a[i] + suf[i + y]` for that `y` in `O(n)`, then answer each such query in `O(1)`. There are fewer than `√n` distinct small steps, so precomputation costs `O(n√n)`; processing the queries grouped by `y` reuses one array.

```java
static int[] evenlySpacedSums(int[] a, int[][] queries) {    // queries[k] = {x, y}
    final int MOD = 1_000_000_007;
    int n = a.length, S = (int) Math.sqrt(n) + 1;            // steps < S are "small"
    Integer[] order = new Integer[queries.length];
    for (int k = 0; k < order.length; k++) order[k] = k;
    Arrays.sort(order, Comparator.comparingInt(k -> queries[k][1]));   // group by step
    long[] suf = new long[n];
    int builtFor = -1;
    int[] res = new int[queries.length];
    for (int k : order) {
        int x = queries[k][0], y = queries[k][1];
        if (y < S) {
            if (y != builtFor) {                   // O(n), at most S − 1 times
                for (int i = n - 1; i >= 0; i--) suf[i] = (a[i] + (i + y < n ? suf[i + y] : 0)) % MOD;
                builtFor = y;
            }
            res[k] = (int) suf[x];
        } else {
            long s = 0;
            for (int j = x; j < n; j += y) s += a[j];          // fewer than n / S + 1 terms
            res[k] = (int) (s % MOD);
        }
    }
    return res;
}
```

`[0, 1, 2, 3, 4, 5, 6, 7]`, queries `[[0, 3], [5, 1], [4, 2]]` → `[9, 18, 10]`. Precomputing a separate suffix array for **every** small step at once needs `O(n√n)` memory (about 90 MB of `long`s for `n = 5·10⁴`); grouping the queries offline keeps it at `O(n)`.

![[Sqrt - Small and Large Steps.excalidraw|800]]

The same split appears as **heavy/light** elements: in a graph, vertices with degree `> √m` are "heavy" (at most `2√m` of them), so heavy–heavy interactions can be precomputed and light vertices handled by scanning their few neighbours (triangle counting in `O(m√m)`); in string problems, patterns longer than `√L` are rare, and short ones can be enumerated.

> [!tip] Rebuilding every √q operations
> Another sqrt trick works on **time** instead of space: keep a static structure (say, prefix sums) plus a short list of recent updates. Each query reads the static structure and corrects for the pending updates (`O(√q)` of them); after `√q` updates, rebuild the static structure in `O(n)`. Total `O(q√q + (q/√q)·n)`. It turns any "fast queries on static data" structure into one that accepts updates, without designing a dynamic version.

---

## 6. Mo's Algorithm

Mo's algorithm answers `q` **offline** range queries `[l, r]` when you can maintain the answer for a sliding window `[curL, curR]` and **add or remove one element in `O(1)`** (or `O(log n)`). Moving the window from one query to the next costs `|Δl| + |Δr|` steps, so the order of the queries determines the total cost. Sorting by `(block of l, r)` keeps it at `O((n + q)√n)`.

```
mo(queries):
    sort queries by (l / B, then r)
    curL = 0; curR = −1                 -- empty window
    for each query (l, r) in that order:
        while curR < r: add(++curR)     -- extend first,
        while curL > l: add(--curL)
        while curR > r: remove(curR--)  -- then shrink
        while curL < l: remove(curL++)
        answer[query] = current answer
```

![[Sqrt - Mo's Ordering.excalidraw|800]]

**Why `O((n + q)√n)`** with `B = √n`:
- Within one block of `l` values, queries are sorted by `r`, so `curR` only moves forward: `O(n)` per block, `O(n · n/B) = O(n√n)` over all blocks.
- `curL` stays within one block (or moves to the next), so each query moves it at most `O(B)`: `O(q√n)` in total.

**Distinct elements in each range**, the classic example: keep a count per value and the number of values with a non-zero count.

```java
static int[] distinctInRanges(int[] a, int[][] queries) {    // queries[k] = {l, r}, inclusive
    int n = a.length, q = queries.length;
    int[] vals = Arrays.stream(a).distinct().sorted().toArray();
    int[] c = new int[n];
    for (int i = 0; i < n; i++) c[i] = Arrays.binarySearch(vals, a[i]);   // compress: counts in an array
    int B = Math.max(1, (int) (n / Math.sqrt(Math.max(1, q))));
    Integer[] order = new Integer[q];
    for (int k = 0; k < q; k++) order[k] = k;
    Arrays.sort(order, (x, y) -> {
        int bx = queries[x][0] / B, by = queries[y][0] / B;
        if (bx != by) return Integer.compare(bx, by);
        return (bx & 1) == 0 ? Integer.compare(queries[x][1], queries[y][1])   // even block: r ascending
                             : Integer.compare(queries[y][1], queries[x][1]);  // odd block: r descending
    });
    int[] cnt = new int[vals.length], res = new int[q];
    int curL = 0, curR = -1, distinct = 0;
    for (int k : order) {
        int l = queries[k][0], r = queries[k][1];
        while (curR < r) if (cnt[c[++curR]]++ == 0) distinct++;
        while (curL > l) if (cnt[c[--curL]]++ == 0) distinct++;
        while (curR > r) if (--cnt[c[curR--]] == 0) distinct--;
        while (curL < l) if (--cnt[c[curL++]] == 0) distinct--;
        res[k] = distinct;
    }
    return res;
}
```

`[1, 1, 2, 1, 3]`, queries `[[0, 4], [1, 3], [2, 4], [0, 1]]` → `[3, 2, 3, 1]`. Three details:

- **Block size `n / √q`** instead of `√n` balances the two costs when `q` differs a lot from `n` (it's `O(n√q)` overall).
- **Odd-even ordering**: reversing the `r` order in every other block lets `curR` sweep back down instead of jumping from `n` to the start of the next block, often cutting the runtime by a third or more.
- **Extend before shrinking**: doing the shrinking loops first can make `curL` pass `curR + 1`, removing elements that were never added, which drives counts negative.

| Mo's algorithm works when | It doesn't work when |
|---|---|
| all queries are known in advance (offline) | queries arrive online and must be answered immediately |
| the array doesn't change (basic version) | updates are interleaved (Mo's with updates adds a time dimension: `O(n^{5/3})`) |
| add/remove are `O(1)` or `O(log n)` | removal is impossible or expensive (use "rollback Mo's", which only adds and undoes) |
| the answer is maintained incrementally | the answer needs the whole window recomputed |

Typical Mo's problems: number of distinct values, number of pairs of equal values (`Σ cnt·(cnt − 1)/2`, adjusted on each add/remove), "most frequent value count", sum of `cnt² · value`, count of subarrays with XOR `k` inside a range (on prefix XORs). Mo's on **trees** runs the same algorithm on an Euler tour ([[DSA/05 - Graphs/07 - Lowest Common Ancestor|Lowest Common Ancestor]]); a **Hilbert curve** ordering of `(l, r)` reduces movement further.

---

## 7. When to Use What

| Need | Best fit | Why |
|---|---|---|
| Range sums, no updates | prefix sums | `O(1)` query |
| Range sums with point updates | Fenwick tree | `O(log n)`, tiny code |
| Range min/max, any associative op, lazy range updates | segment tree | `O(log n)`, general |
| Order-statistic queries on ranges with updates (`≥ x`, `k`-th) | sqrt blocks with sorted copies | trees need heavier machinery |
| Offline range queries with add/remove-one maintenance (distinct values, pair counts) | Mo's algorithm | no merge needed at all |
| Parameterised queries (steps, degrees, lengths) | threshold split at `√` | precompute small, brute force large |
| Data structure only fast when static | rebuild every `√q` updates | reuse the static structure |
| Insert/delete anywhere in a sequence, index access | block list, or an implicit treap ([[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees#5. Treaps|Balanced Trees § 5]]) | |

Rough budget: `n = q = 10⁵` gives `(n + q)√n ≈ 6 · 10⁷` elementary steps, comfortably fast in Java; `n = q = 10⁶` makes it `2 · 10⁹`, too slow, so `O(log n)` structures are required there.

---

## 8. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| `B = (int) Math.sqrt(n)` with `n = 0` or tiny | `B = 0`: division by zero | `max(1, …)` |
| Assuming every block has `B` elements | wrong sums for the last block | `min(n, (b + 1)·B)` |
| `l` and `r` in the same block handled by the three-part code | elements counted twice | special-case `bl == br` |
| Block tag applied with `· B` to a partial or last block | wrong totals | count the actual elements |
| Min/max block updated with `+=` | stale minimum | recompute the block |
| Mo's: shrinking before extending | negative counts, wrong answers | extend `curR`/`curL` first |
| Mo's: comparator sorting by `l` then `r` | `O(n·q)` movement | sort by **block** of `l`, then `r` |
| Mo's: using `HashMap` counts | 5–10× slower | compress values, use an array |
| Mo's with online queries or updates | not applicable | segment tree / Mo's with updates |
| Threshold split precomputing all small steps at once | memory limit exceeded | group queries offline, reuse one array |
| Sorted-block update re-sorting the whole block | `O(B log B)` instead of `O(B)` | replace and slide one element |
| Inclusive `r` treated as exclusive (or vice versa) in Mo's loops | off-by-one windows | `curR = −1` start, `r` inclusive |

---

## 9. Trick Questions and Special Cases

> [!question]- `n = 10`, `B = 3`: which blocks are there, and how is `query(2, 7)` split?
> Blocks `[0..2]`, `[3..5]`, `[6..8]`, `[9]`: the last block has one element. `query(2, 7)`: partial block 0 contributes `a[2]`, block 1 is whole, partial block 2 contributes `a[6] + a[7]`.

> [!question]- Why is the best block size `√n` and not, say, `log n`?
> A query costs about `B` (partial blocks) plus `n / B` (whole blocks). With `B = log n`, the `n / log n` whole blocks dominate. The sum `B + n/B` is minimised where the terms are equal, at `B = √n`.

> [!question]- A query `[l, r]` lies entirely inside one block. What does the three-part code do if `bl == br` isn't special-cased?
> The "tail of the first block" loop runs from `l` to the block's end (past `r`), and the "head of the last block" loop runs from the block's start to `r` (before `l`), so the overlap is counted twice and elements outside the range are included.

> [!question]- Can sqrt decomposition answer range minimum with point updates? How fast?
> Yes: query `O(√n)`; update `O(√n)`, because the block's minimum must be recomputed when its minimum element increases. A segment tree does both in `O(log n)`.

> [!question]- In Mo's algorithm, why sort by the block of `l` rather than by `l` itself?
> Sorting by `l` (then `r`) lets `r` jump back and forth across the whole array between consecutive queries: up to `O(n)` per query, `O(nq)` total. Grouping by the block of `l` lets `r` increase monotonically inside each group, so it travels `O(n)` per block.

> [!question]- What goes wrong if Mo's loops shrink before they extend?
> Moving from window `[5, 6]` to `[0, 1]`: shrinking first runs `while (curL < l)` with nothing to do, then `while (curR > r)` removes 6, 5, 4, 3, 2, but 4, 3, and 2 were never added. Counts go negative and "distinct" goes wrong. Extending first keeps the window non-empty and valid throughout.

> [!question]- Can Mo's algorithm handle an update between queries?
> Not the basic version: it reorders queries, which is only valid if the array is the same for all of them. "Mo's with updates" adds time as a third coordinate (block size `n^{2/3}`, total `O(n^{5/3})`), but if the updates are point updates and the queries are sums, a Fenwick tree is far simpler.

> [!question]- Evenly spaced sums: why not precompute suffix sums for every step `y`?
> For all `n` steps that's `O(n²)` time and memory. Only steps below `√n` are worth precomputing; larger steps have at most `√n` terms and are summed directly.

> [!question]- Distinct values in `[1, 1, 2, 1, 3]` for the range `[0, 1]`? `[1, 3]`?
> `1` (just the value 1) and `2` (values 1 and 2).

> [!question]- With `q = 100` queries on `n = 10⁶` elements, which block size for Mo's?
> `n / √q = 10⁵`. With `B = √n = 1000`, `curR` would sweep the array once per block of `l` values (up to 1000 sweeps of `10⁶`); with `B = 10⁵`, there are only 10 blocks, and `curL` moves at most `10⁵` per query: about `2 · 10⁷` steps instead of `10⁹`.

> [!question]- Is sqrt decomposition ever faster than a segment tree in practice?
> For moderate `n` (say `10⁵`) with simple operations, its tight loops over contiguous memory can be competitive with a recursive segment tree, and it wins outright on problems where the segment tree would need complex node data (sorted lists with updates, per-block hash maps). For large `n` and many queries, `O(log n)` wins.

---

## 10. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| Block of index `i` | `i / B` | |
| Last block length | `n − (nb − 1)·B` | may be short |
| Query cost | `O(B + n/B)` | partial + whole blocks |
| Best `B` | `√n` | equal terms |
| Point update, sum / min | `O(1)` / `O(B)` | min must be recomputed |
| Range add with block tags | `O(√n)` | inner blocks get a tag |
| Sorted blocks: count `≥ x` | `O(√n log n)` query, `O(√n)` update | |
| `evenlySpacedSums([0..7], [[0,3],[5,1],[4,2]])` | `[9, 18, 10]` | |
| Mo's total movement, `B = √n` | `O((n + q)√n)` | `r` monotone per block |
| Mo's block size for `q ≪ n` | `n / √q` | |
| Mo's loop order | extend, then shrink | no negative counts |
| Distinct values `[1,1,2,1,3]`, `[0,4]` | `3` | |
| Odd-even ordering | fewer `r` moves | sweeps back instead of resetting |
| `(int) Math.sqrt(0)` | `0` | guard with `max(1, …)` |

---

## 11. Summary

- **Blocks of `√n`**: queries combine at most two partial blocks (scanned) and `√n` whole blocks (summaries); point updates fix one block. Special-case ranges inside one block, and remember the last block can be short.
- **Block tags** give range updates without pushing anything down; the real value is `a[i] + tag[block]`.
- Choose `B` by balancing the two costs; `√n` for the simple case, other values when per-block work has a log factor or when `q ≠ n`.
- Blocks can hold sorted copies, counts, or maps, which handles problems that don't merge well in a tree.
- **Threshold splits** precompute the small cases and brute-force the large ones; rebuilding every `√q` updates adds updates to static structures.
- **Mo's algorithm** reorders offline range queries by `(block of l, r)` so a sliding window moves `O((n + q)√n)` steps; extend before shrinking, use array counts, and alternate `r` direction per block.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees]] · Next: [[DSA/05 - Graphs/01 - Graph Representations and Traversals|Graph Representations and Traversals]]
- [[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]]: the static baseline
- [[DSA/03 - Sorting and Searching/04 - Sliding Window|Sliding Window]]: the add/remove window that Mo's algorithm moves
- [[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees|Segment Trees]] and [[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees]]: the `O(log n)` alternatives
- [[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]]: searching inside sorted blocks
- [[DSA/01 - Foundations/01 - Complexity Analysis|Complexity Analysis]]: balancing costs
