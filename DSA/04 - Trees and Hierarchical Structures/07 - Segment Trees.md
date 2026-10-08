# Segment Trees

A <span class="hl-blue">segment tree</span> stores an array in a balanced binary tree where every node holds the answer (sum, minimum, maximum, …) for one contiguous **segment** of the array: the root covers the whole array, its children the two halves, and so on down to single elements. Any range `[l, r]` splits into `O(log n)` of these stored segments, so a range query costs `O(log n)`; changing one element touches only the `O(log n)` segments containing it.

Prefix sums answer range queries in `O(1)` but can't handle updates ([[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays#8. Static vs. Dynamic Data|Prefix Sums § 8]]); a segment tree handles both, for any associative operation, and with **lazy propagation** it also applies updates to whole ranges in `O(log n)`. This note covers the structure, the recursive and iterative implementations, which operations work (and the identity-element trap), custom node data such as maximum subarray sums, descending the tree to search, lazy propagation for range updates (add, assign, and their composition), dynamic segment trees over huge coordinate ranges, and merge-sort trees.

## Contents

- [[#1. The Problem|1. The Problem]]
- [[#2. Structure|2. Structure]]
- [[#3. Build, Query, Update|3. Build, Query, Update]]
- [[#4. Which Operations Work|4. Which Operations Work]]
- [[#5. Searching Inside the Tree|5. Searching Inside the Tree]]
- [[#6. Iterative (Bottom-Up) Segment Tree|6. Iterative (Bottom-Up) Segment Tree]]
- [[#7. Lazy Propagation|7. Lazy Propagation]]
- [[#8. Applications|8. Applications]]
- [[#9. Dynamic Segment Trees|9. Dynamic Segment Trees]]
- [[#10. Merge-Sort Tree (advanced)|10. Merge-Sort Tree (advanced)]]
- [[#11. Common Mistakes|11. Common Mistakes]]
- [[#12. Trick Questions and Special Cases|12. Trick Questions and Special Cases]]
- [[#13. Quick Reference — Non-Obvious Outcomes|13. Quick Reference — Non-Obvious Outcomes]]
- [[#14. Summary|14. Summary]]

---

## 1. The Problem

Given an array `a[0..n−1]`, support, in any interleaving:

- **query(l, r)**: the sum (or min, max, gcd, …) of `a[l..r]`;
- **update(i, v)**: set `a[i] = v` (point update), or add `v` to every element of `a[l..r]` (range update).

| Structure | Point update | Range query | Range update | Operations |
|---|---|---|---|---|
| Plain array | `O(1)` | `O(n)` | `O(n)` | any |
| Prefix sums | `O(n)` | `O(1)` | `O(n)` | invertible (sum, XOR) |
| Difference array | `O(n)` to read | — | `O(1)` | add |
| Sparse table | rebuild | `O(1)` | rebuild | idempotent (min, max, gcd) |
| Sqrt decomposition | `O(1)` | `O(√n)` | `O(√n)` | most ([[DSA/04 - Trees and Hierarchical Structures/09 - Sqrt Decomposition|Sqrt Decomposition]]) |
| Fenwick tree | `O(log n)` | `O(log n)` | `O(log n)` (add) | invertible ([[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees]]) |
| **Segment tree** | `O(log n)` | `O(log n)` | `O(log n)` with lazy | any **associative** operation |

The segment tree is the most general of these: anything that combines two adjacent segments' answers into the answer for their union works, including min/max (not invertible, so no Fenwick tree) and composite data (maximum subarray sum, count of the maximum, a sorted list).

---

## 2. Structure

> [!note] Definition
> - The root covers `[0, n − 1]`.
> - A node covering `[l, r]` with `l < r` has two children covering `[l, m]` and `[m + 1, r]`, where `m = (l + r) / 2`.
> - A node covering `[l, l]` is a leaf and stores `a[l]`.
> - Every node stores `op` over its segment: `t[node] = op(t[left], t[right])`.

Nodes are stored in an array like a heap ([[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues#1. The Heap Property|Heaps § 1]]): the root is index 1, and node `i` has children `2i` and `2i + 1`. The tree has height `⌈log₂ n⌉`, `n` leaves and `n − 1` internal nodes, but because it isn't a complete tree when `n` isn't a power of two, the indices can go higher than `2n`: allocate **`4n`**.

![[Segment Trees - Structure and Query.excalidraw|800]]

**Why a query touches `O(log n)` nodes.** A query range `[ql, qr]` meets each level of the tree in a set of consecutive nodes. Only the two at the ends can be **partially** covered; everything in between is fully covered and its stored answer is used without going deeper. So at most 2 nodes per level recurse further and at most 4 are visited per level: `O(log n)` in total, combining at most `2 log₂ n` stored segments.

---

## 3. Build, Query, Update

```
build(node, l, r):
    if l = r: t[node] = a[l]; return
    m = (l + r) / 2
    build(2·node, l, m); build(2·node + 1, m + 1, r)
    t[node] = op(t[2·node], t[2·node + 1])

query(node, l, r, ql, qr):              -- op over a[ql..qr] ∩ [l, r]
    if qr < l or r < ql: return IDENTITY            -- disjoint
    if ql ≤ l and r ≤ qr: return t[node]            -- fully inside
    m = (l + r) / 2
    return op(query(2·node, l, m, ql, qr), query(2·node + 1, m + 1, r, ql, qr))

update(node, l, r, i, v):               -- a[i] = v
    if l = r: t[node] = v; return
    m = (l + r) / 2
    if i ≤ m: update(2·node, l, m, i, v) else update(2·node + 1, m + 1, r, i, v)
    t[node] = op(t[2·node], t[2·node + 1])
```

```java
static class SegTree {                             // range sum, point assignment
    private final int n;
    private final long[] t;                        // t[node] = sum of the node's segment; root = 1

    SegTree(int[] a) {
        n = a.length;
        t = new long[4 * Math.max(1, n)];
        if (n > 0) build(a, 1, 0, n - 1);
    }

    private void build(int[] a, int node, int l, int r) {
        if (l == r) { t[node] = a[l]; return; }
        int m = (l + r) >>> 1;
        build(a, 2 * node, l, m);
        build(a, 2 * node + 1, m + 1, r);
        t[node] = t[2 * node] + t[2 * node + 1];
    }

    void update(int i, int value) { update(1, 0, n - 1, i, value); }

    private void update(int node, int l, int r, int i, int value) {
        if (l == r) { t[node] = value; return; }
        int m = (l + r) >>> 1;
        if (i <= m) update(2 * node, l, m, i, value);
        else update(2 * node + 1, m + 1, r, i, value);
        t[node] = t[2 * node] + t[2 * node + 1];   // recompute on the way back up
    }

    long query(int ql, int qr) { return query(1, 0, n - 1, ql, qr); }   // sum of a[ql..qr]

    private long query(int node, int l, int r, int ql, int qr) {
        if (qr < l || r < ql) return 0;            // disjoint: the identity of +
        if (ql <= l && r <= qr) return t[node];    // fully covered: stored answer
        int m = (l + r) >>> 1;
        return query(2 * node, l, m, ql, qr) + query(2 * node + 1, m + 1, r, ql, qr);
    }
}
```

`a = [5, 8, 6, 3, 2, 7, 2, 6]`: `query(2, 6)` = `6 + 3 + 2 + 7 + 2 = 20`, combining the nodes `[2, 3]`, `[4, 5]`, and `[6, 6]`. After `update(4, 10)`: `28`. Build `O(n)`, query and update `O(log n)`, memory `O(n)`.

> [!tip] "Add to an element" vs "set an element"
> `update` above **sets** `a[i]`. To **add** `v`, change the leaf line to `t[node] += v`. With sums, adding at a leaf and recomputing parents is the same as adding `v` to every node on the path, which is how Fenwick trees work.

---

## 4. Which Operations Work

The operation must be **associative**: `op(op(x, y), z) = op(x, op(y, z))`, because the tree groups elements in a fixed way that has nothing to do with the query. It does **not** need to be commutative (if the left child's result always goes first), invertible, or idempotent.

| Operation | Identity (for disjoint nodes) | Notes |
|---|---|---|
| sum | `0` | use `long` |
| min | `+∞` (`Integer.MAX_VALUE` / `Long.MAX_VALUE`) | **not 0** |
| max | `−∞` | **not 0** |
| gcd | `0` (`gcd(0, x) = x`) | |
| product mod `p` | `1` | |
| XOR | `0` | |
| bitwise AND / OR | all ones / `0` | |
| (min, count of min) | `(+∞, 0)` | ties add counts |
| matrix product | identity matrix | **not commutative**: keep left before right |
| string / hash concatenation | empty | not commutative |

> [!warning] The identity element must really be neutral
> Returning `0` for disjoint nodes in a **min** tree makes every query whose range doesn't exactly align with nodes return `min(…, 0)`, which is wrong for positive data. Returning `Integer.MIN_VALUE` in a max tree is right; returning it in a min tree is wrong. When no clean identity exists (or to avoid thinking about it), branch on which children the query actually overlaps, as in [[#4.1 Custom node data: maximum subarray sum|§4.1]].

### 4.1 Custom node data: maximum subarray sum

The answer for a range can need **more** than the answer for its halves. The maximum subarray sum of `[l, r]` is either inside the left half, inside the right half, or crosses the middle, made of a suffix of the left half and a prefix of the right half. So each node stores four values:

| Field | Meaning | Combine `(L, R)` |
|---|---|---|
| `sum` | total | `L.sum + R.sum` |
| `pre` | best prefix sum | `max(L.pre, L.sum + R.pre)` |
| `suf` | best suffix sum | `max(R.suf, R.sum + L.suf)` |
| `best` | best subarray sum | `max(L.best, R.best, L.suf + R.pre)` |

![[Segment Trees - Max Subarray Merge.excalidraw|800]]

```java
static long[] combine(long[] L, long[] R) {        // {sum, pre, suf, best}
    return new long[]{
        L[0] + R[0],
        Math.max(L[1], L[0] + R[1]),
        Math.max(R[2], R[0] + L[2]),
        Math.max(Math.max(L[3], R[3]), L[2] + R[1])
    };
}

static class MaxSubarrayTree {
    private final int n;
    private final long[][] t;

    MaxSubarrayTree(int[] a) {
        n = a.length;
        t = new long[4 * n][];
        build(a, 1, 0, n - 1);
    }

    private static long[] leaf(long v) { return new long[]{v, v, v, v}; }   // non-empty subarrays only

    private void build(int[] a, int node, int l, int r) {
        if (l == r) { t[node] = leaf(a[l]); return; }
        int m = (l + r) >>> 1;
        build(a, 2 * node, l, m);
        build(a, 2 * node + 1, m + 1, r);
        t[node] = combine(t[2 * node], t[2 * node + 1]);
    }

    void update(int i, int v) { update(1, 0, n - 1, i, v); }

    private void update(int node, int l, int r, int i, int v) {
        if (l == r) { t[node] = leaf(v); return; }
        int m = (l + r) >>> 1;
        if (i <= m) update(2 * node, l, m, i, v); else update(2 * node + 1, m + 1, r, i, v);
        t[node] = combine(t[2 * node], t[2 * node + 1]);
    }

    long query(int ql, int qr) { return query(1, 0, n - 1, ql, qr)[3]; }

    private long[] query(int node, int l, int r, int ql, int qr) {
        if (ql <= l && r <= qr) return t[node];
        int m = (l + r) >>> 1;
        if (qr <= m) return query(2 * node, l, m, ql, qr);         // only the left child overlaps
        if (ql > m) return query(2 * node + 1, m + 1, r, ql, qr);  // only the right child overlaps
        return combine(query(2 * node, l, m, ql, qr), query(2 * node + 1, m + 1, r, ql, qr));
    }
}
```

`[-2, 1, -3, 4, -1, 2, 1, -5, 4]`: `query(0, 8)` → `6` (`[4, −1, 2, 1]`); `query(0, 2)` → `1`; after `update(7, 5)`, `query(0, 8)` → `15` (`4, −1, 2, 1, 5, 4`). Branching on which children overlap means `query` never needs an identity element. `combine` isn't commutative: the left child must be passed first.

---

## 5. Searching Inside the Tree

A segment tree can also **find** positions by walking down from the root and choosing a child using the stored values, `O(log n)`, instead of binary searching over `O(log n)` queries (`O(log² n)`).

**First index with `a[i] ≥ x`** in a max tree: if the left child's maximum is `≥ x`, the answer is in the left half; otherwise, in the right half.

```java
static class MaxTree {
    private final int n;
    private final int[] t;

    MaxTree(int[] a) {
        n = a.length;
        t = new int[4 * n];
        build(a, 1, 0, n - 1);
    }

    private void build(int[] a, int node, int l, int r) {
        if (l == r) { t[node] = a[l]; return; }
        int m = (l + r) >>> 1;
        build(a, 2 * node, l, m);
        build(a, 2 * node + 1, m + 1, r);
        t[node] = Math.max(t[2 * node], t[2 * node + 1]);
    }

    void update(int i, int v) { update(1, 0, n - 1, i, v); }

    private void update(int node, int l, int r, int i, int v) {
        if (l == r) { t[node] = v; return; }
        int m = (l + r) >>> 1;
        if (i <= m) update(2 * node, l, m, i, v); else update(2 * node + 1, m + 1, r, i, v);
        t[node] = Math.max(t[2 * node], t[2 * node + 1]);
    }

    int firstAtLeast(int x) {                      // leftmost i with a[i] ≥ x, or −1
        if (t[1] < x) return -1;
        int node = 1, l = 0, r = n - 1;
        while (l < r) {
            int m = (l + r) >>> 1;
            if (t[2 * node] >= x) { node = 2 * node; r = m; }   // the left half has one: go left
            else { node = 2 * node + 1; l = m + 1; }
        }
        return l;
    }
}
```

`[3, 1, 4, 1, 5, 9, 2, 6]`: `firstAtLeast(4)` → `2`, `firstAtLeast(6)` → `5`, `firstAtLeast(10)` → `−1`. This is "first fit": with `a[i]` = free space in bin `i`, put an item of size `x` into bin `firstAtLeast(x)`, then `update(i, a[i] − x)`.

The same descent finds the **`k`-th one** in a 0/1 array stored as a count tree (go left if the left count is `≥ k`, else subtract it and go right), which gives "the `k`-th smallest value present" over compressed values, and "the `k`-th empty seat".

---

## 6. Iterative (Bottom-Up) Segment Tree

A shorter, faster version for point updates and range queries. The leaves go at indices `n … 2n − 1`, and node `i` is the parent of `2i` and `2i + 1`, for **any** `n`:

```java
static class IterSegTree {                         // range sum, point assignment; queries on [l, r)
    private final int n;
    private final long[] t;

    IterSegTree(int[] a) {
        n = a.length;
        t = new long[2 * n];
        for (int i = 0; i < n; i++) t[n + i] = a[i];
        for (int i = n - 1; i > 0; i--) t[i] = t[2 * i] + t[2 * i + 1];
    }

    void set(int i, int value) {
        for (t[i += n] = value; i > 1; i >>= 1) t[i >> 1] = t[i] + t[i ^ 1];   // i ^ 1: the sibling
    }

    long query(int l, int r) {                     // sum of a[l..r), r EXCLUSIVE
        long res = 0;
        for (l += n, r += n; l < r; l >>= 1, r >>= 1) {
            if ((l & 1) == 1) res += t[l++];       // l is a right child: its parent covers too much
            if ((r & 1) == 1) res += t[--r];       // likewise on the right end
        }
        return res;
    }
}
```

![[Segment Trees - Iterative Layout.excalidraw|800]]

`O(log n)` per operation, `2n` memory, no recursion. The loop climbs both ends of the range at once: whenever a boundary node's parent would include elements outside the range, that node is taken on its own and the boundary moves inward.

> [!warning] Two traps of the bottom-up version
> - **The right end is exclusive.** `query(l, r)` sums `a[l..r)`; for an inclusive range, call `query(l, r + 1)`.
> - **Order isn't preserved for arbitrary `n`.** When `n` isn't a power of two, an internal node can combine elements that aren't in array order (with `n = 3`, the root combines `a[1] + a[2]` with `a[0]`). Sums, min, max, gcd don't care. For a **non-commutative** operation, keep two accumulators (`resLeft = op(resLeft, t[l++])`, `resRight = op(t[--r], resRight)`) and combine them at the end, and pad `n` to a power of two if the root itself must be in order.

---

## 7. Lazy Propagation

Range **updates** ("add `v` to every element of `a[l..r]`") would touch every leaf in the range, `O(n)`. Lazy propagation stops at the `O(log n)` fully covered nodes, updates their stored answers directly, and leaves a **tag** saying "my children still owe this update". The tag is pushed one level down only when a later operation needs to go below that node.

```
apply(node, l, r, v):                   -- add v to every element of [l, r]
    sum[node] += v · (r − l + 1)
    tag[node] += v

push(node, l, r):                       -- hand the pending update to the children
    if tag[node] ≠ 0:
        apply(left, l, m, tag[node]); apply(right, m + 1, r, tag[node])
        tag[node] = 0

rangeAdd(node, l, r, ql, qr, v):
    if disjoint: return
    if fully covered: apply(node, l, r, v); return     -- stop here
    push(node, l, r)
    recurse into both children
    sum[node] = sum[left] + sum[right]

query(node, l, r, ql, qr):
    if disjoint: return 0
    if fully covered: return sum[node]
    push(node, l, r)                                   -- children must be up to date
    return query(left, …) + query(right, …)
```

![[Segment Trees - Lazy Propagation.excalidraw|800]]

```java
static class LazySegTree {                         // range add, range sum
    private final int n;
    private final long[] sum, tag;                 // tag: pending add for the node's children

    LazySegTree(int[] a) {
        n = a.length;
        sum = new long[4 * n];
        tag = new long[4 * n];
        build(a, 1, 0, n - 1);
    }

    private void build(int[] a, int node, int l, int r) {
        if (l == r) { sum[node] = a[l]; return; }
        int m = (l + r) >>> 1;
        build(a, 2 * node, l, m);
        build(a, 2 * node + 1, m + 1, r);
        sum[node] = sum[2 * node] + sum[2 * node + 1];
    }

    private void apply(int node, int l, int r, long v) {
        sum[node] += v * (r - l + 1);              // every element of the segment grows by v
        tag[node] += v;
    }

    private void push(int node, int l, int r) {
        if (tag[node] != 0) {
            int m = (l + r) >>> 1;
            apply(2 * node, l, m, tag[node]);
            apply(2 * node + 1, m + 1, r, tag[node]);
            tag[node] = 0;
        }
    }

    void rangeAdd(int ql, int qr, long v) { rangeAdd(1, 0, n - 1, ql, qr, v); }

    private void rangeAdd(int node, int l, int r, int ql, int qr, long v) {
        if (qr < l || r < ql) return;
        if (ql <= l && r <= qr) { apply(node, l, r, v); return; }
        push(node, l, r);
        int m = (l + r) >>> 1;
        rangeAdd(2 * node, l, m, ql, qr, v);
        rangeAdd(2 * node + 1, m + 1, r, ql, qr, v);
        sum[node] = sum[2 * node] + sum[2 * node + 1];
    }

    long query(int ql, int qr) { return query(1, 0, n - 1, ql, qr); }

    private long query(int node, int l, int r, int ql, int qr) {
        if (qr < l || r < ql) return 0;
        if (ql <= l && r <= qr) return sum[node];
        push(node, l, r);
        int m = (l + r) >>> 1;
        return query(2 * node, l, m, ql, qr) + query(2 * node + 1, m + 1, r, ql, qr);
    }
}
```

`a = [1, 2, 3, 4, 5]`: `rangeAdd(1, 3, 10)` then `query(0, 4)` → `45`, `query(2, 2)` → `13`, `query(4, 4)` → `5`. Both operations are `O(log n)`. A leaf is never pushed: an operation that reaches a leaf always finds it either disjoint or fully covered, so the children of leaves (which don't exist in the array) are never touched.

> [!warning] What the stored value means with lazy tags
> `sum[node]` already **includes** every update applied to the node or its ancestors' pushed tags; `tag[node]` is only what its **children** haven't seen yet. Mixing up the two conventions (adding the tag again when reading `sum[node]`, or forgetting `· (r − l + 1)` when applying it to a sum) is the most common lazy-propagation bug. For a min/max tree, applying "add `v`" changes the stored min by `v`, with no length factor.

### 7.1 Range assignment, and combining it with add

"Set every element of `a[l..r]` to `v`" uses the same machinery with an assignment tag. When **both** assign and add can be pending, the tags must compose correctly:

| Pending | New update | Result |
|---|---|---|
| none | assign `v` | assign `v` |
| add `d` | assign `v` | assign `v` (the add is overwritten) |
| assign `v` | add `d` | assign `v + d` |
| add `d` | add `e` | add `d + e` |

A clean way to get this right is to represent every update as an affine map `x ↦ m·x + c`: "add `d`" is `(1, d)`, "assign `v`" is `(0, v)`, and applying `(m₂, c₂)` after `(m₁, c₁)` gives `(m₂·m₁, m₂·c₁ + c₂)`. On a sum over a segment of length `len`, `(m, c)` changes the sum to `m·sum + c·len`. The table above is exactly this composition, and range multiplication comes for free.

> [!warning] Don't use 0 as "no pending assignment"
> If the assign tag is a plain `long` with `0` meaning "nothing pending", then assigning **0** to a range is silently ignored on push. Use a separate `boolean hasAssign`, a sentinel outside the value range, or the affine form above (where "nothing" is `(1, 0)`).

---

## 8. Applications

### 8.1 Count of smaller numbers after self

For each `i`, count `j > i` with `a[j] < a[i]`. Scan from the right, keeping a count of every value seen so far in a segment tree indexed by value (**coordinate-compressed**, so the values fit in an array of size `n`):

```java
static List<Integer> countSmaller(int[] a) {
    int[] sorted = Arrays.stream(a).distinct().sorted().toArray();   // value → rank
    SegTree counts = new SegTree(new int[sorted.length]);            // counts[rank] of values seen
    Integer[] res = new Integer[a.length];
    for (int i = a.length - 1; i >= 0; i--) {      // the tree holds a[i+1..n−1]
        int v = Arrays.binarySearch(sorted, a[i]);
        res[i] = v == 0 ? 0 : (int) counts.query(0, v - 1);       // strictly smaller values
        counts.update(v, (int) counts.query(v, v) + 1);
    }
    return Arrays.asList(res);
}
```

`[5, 2, 6, 1]` → `[2, 1, 1, 0]`; `[-1, -1]` → `[0, 0]` (equal values aren't smaller). `O(n log n)`. A Fenwick tree does the same in less code ([[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees]]), and merge sort counts it too ([[DSA/03 - Sorting and Searching/01 - Sorting Algorithms#3.2 Counting inversions while merging|Sorting § 3.2]]).

### 8.2 Problems by node data

| Problem | Node stores | Update |
|---|---|---|
| Range minimum / maximum with updates | min / max | point |
| Range sum with range add | sum + add tag | range (lazy) |
| Number of elements equal to the range maximum | `(max, count)` | point |
| Maximum subarray sum in a range | `(sum, pre, suf, best)` | point |
| Longest run of 1s in a range (seats, hotel rooms) | `(pre ones, suf ones, best, length)` | range assign (lazy) |
| Range GCD / are all elements divisible by `g`? | gcd | point |
| `k`-th smallest value present, `k`-th free slot | counts over value / position | point + descent |
| Maximum overlap of booked intervals (My Calendar III) | max + add tag | range add, dynamic (§9) |
| Area of the union of rectangles | covered length + cover count | sweep line, range add (advanced) ([[DSA/08 - Specialized Topics/01 - Intervals and Sweep Line|Sweep Line]]) |
| Brackets: longest correct subsequence in a range | `(matched, unmatched open, unmatched close)` | point |

---

## 9. Dynamic Segment Trees

When indices range over `[0, 10⁹]` and the operations aren't known in advance (so coordinates can't be compressed), create nodes **only when they're needed**: each node has `left`/`right` references that stay `null` until an update splits that node. `q` operations create `O(q log C)` nodes for a coordinate range of size `C`.

**My Calendar III**: after each booking `[start, end)`, report the maximum number of overlapping bookings. That's "range add 1 on `[start, end − 1]`, then global maximum".

```java
static class DynamicMaxTree {                      // range add, global max, over [0, 10⁹]
    private static class Node {
        long max, add;                             // max of the segment, INCLUDING this node's own add
        Node left, right;
    }

    private final Node root = new Node();
    private static final int LO = 0, HI = 1_000_000_000;

    void rangeAdd(int ql, int qr, long v) { rangeAdd(root, LO, HI, ql, qr, v); }

    private void rangeAdd(Node node, int l, int r, int ql, int qr, long v) {
        if (qr < l || r < ql) return;
        if (ql <= l && r <= qr) { node.max += v; node.add += v; return; }
        int m = l + (r - l) / 2;
        if (node.left == null) node.left = new Node();   // create children only on a split
        if (node.right == null) node.right = new Node();
        rangeAdd(node.left, l, m, ql, qr, v);
        rangeAdd(node.right, m + 1, r, ql, qr, v);
        node.max = node.add + Math.max(node.left.max, node.right.max);
    }

    long max() { return root.max; }
}

static class MyCalendarThree {
    private final DynamicMaxTree tree = new DynamicMaxTree();

    int book(int start, int end) {                 // half-open [start, end)
        tree.rangeAdd(start, end - 1, 1);
        return (int) tree.max();
    }
}
```

Bookings `(10, 20), (50, 60), (10, 40), (5, 15), (5, 10), (25, 55)` → `1, 1, 2, 3, 3, 3`. This version never pushes tags: each node's `max` counts its own `add` plus the best child, and since only the global maximum is asked for, ancestors' adds are included on the way up. That **non-propagating tag** trick works when updates commute (adds) and queries only read the root; range queries need the pushing version.

> [!tip] Compress first when you can
> If all operations are known in advance (offline), collect every coordinate, sort and deduplicate, and use a normal array-based tree over the `≤ 2q` compressed points. It's faster and lighter than allocating nodes. Note that compressing **intervals** needs care: compressed points `[1, 10]` and `[11, 20]` become adjacent indices even though, for intervals, the gap matters only if something can land in it.

---

## 10. Merge-Sort Tree (advanced)

Store at each node the **sorted list** of its segment's elements (exactly the lists merge sort produces at each level). A query "how many elements of `a[l..r]` are `≤ k`?" combines `O(log n)` nodes, binary searching each one's list.

```java
static class MergeSortTree {
    private final int n;
    private final int[][] t;

    MergeSortTree(int[] a) {
        n = a.length;
        t = new int[4 * n][];
        build(a, 1, 0, n - 1);
    }

    private void build(int[] a, int node, int l, int r) {
        if (l == r) { t[node] = new int[]{a[l]}; return; }
        int m = (l + r) >>> 1;
        build(a, 2 * node, l, m);
        build(a, 2 * node + 1, m + 1, r);
        int[] x = t[2 * node], y = t[2 * node + 1], z = new int[x.length + y.length];
        for (int i = 0, j = 0, k = 0; k < z.length; k++)        // the merge step of merge sort
            z[k] = (j == y.length || (i < x.length && x[i] <= y[j])) ? x[i++] : y[j++];
        t[node] = z;
    }

    int countAtMost(int ql, int qr, int k) { return count(1, 0, n - 1, ql, qr, k); }

    private int count(int node, int l, int r, int ql, int qr, int k) {
        if (qr < l || r < ql) return 0;
        if (ql <= l && r <= qr) return upperBound(t[node], k);
        int m = (l + r) >>> 1;
        return count(2 * node, l, m, ql, qr, k) + count(2 * node + 1, m + 1, r, ql, qr, k);
    }

    private static int upperBound(int[] s, int k) {         // number of elements ≤ k
        int lo = 0, hi = s.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (s[mid] <= k) lo = mid + 1; else hi = mid;
        }
        return lo;
    }
}
```

`[3, 1, 4, 1, 5, 9, 2, 6]`: `countAtMost(2, 6, 4)` → `3` (`4, 1, 2`). Memory `O(n log n)` (each element appears once per level), query `O(log² n)`, no updates. The `k`-th smallest in a range follows by binary searching on the value (`O(log³ n)`); a **persistent segment tree** (a new root per prefix, sharing unchanged nodes) answers it in `O(log n)` and is the standard contest tool for that.

---

## 11. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Array of size `2n` for the recursive tree | `ArrayIndexOutOfBoundsException` for some `n` | `4n` |
| `0` as the identity in a min tree (or `MIN_VALUE` in a min tree) | queries return 0 / garbage | true identity, or branch on overlap |
| `int` sums | overflow | `long` |
| Forgetting to recompute the parent after an update | stale answers above | `t[node] = op(children)` on the way up |
| Query with `ql > qr` | returns the identity silently | validate or swap |
| Lazy: not pushing before descending | children see old values | `push` in update **and** query |
| Lazy: tag applied to a sum without the length | sums off by a factor | `v · (r − l + 1)` |
| Lazy: `0` as "no assignment" | assigning 0 ignored | separate flag |
| Lazy: assign then add composed in the wrong order | wrong values | assign clears add; add after assign adds to it |
| Bottom-up tree queried with an inclusive right end | last element missing | `query(l, r + 1)` |
| Bottom-up tree with a non-commutative op | wrong order | separate left/right accumulators |
| `(l + r) / 2` on huge coordinate ranges | overflow (`int`) | `l + (r − l) / 2` or `>>> 1` |
| Dynamic tree reading a `null` child | `NullPointerException` | create on split, treat `null` as empty |
| Using a segment tree where prefix sums suffice | slower, more code | static data → prefix sums / sparse table |

---

## 12. Trick Questions and Special Cases

> [!question]- Why `4n` and not `2n` for the recursive tree?
> The recursive tree has `2n − 1` nodes, but it isn't complete, so heap-style indices skip numbers: a deep leaf on the right side of the last level gets an index near `2 · 2^⌈log₂ n⌉`. For some sizes that's close to `4n` (`n = 4160` uses index 16 257, about `3.9n`), while an array of `2n` already fails at `n = 6`, which uses index 13. `2 · 2^⌈log₂ n⌉ ≤ 4n` always suffices. (The iterative bottom-up layout uses exactly `2n`.)

> [!question]- How many stored segments make up the answer to a query? How many nodes does it visit?
> At most `2⌈log₂ n⌉` segments are combined (at most two per level), and at most `4` nodes are visited per level. For `n = 8`, `query(1, 6)` combines `[1, 1]`, `[2, 3]`, `[4, 5]`, `[6, 6]`.

> [!question]- Can a Fenwick tree replace a segment tree for range minimum with arbitrary updates?
> No. A Fenwick tree answers prefix queries and gets a range by subtracting two prefixes, which needs an inverse; `min` has none. (It can handle prefix minimums when values only decrease, but not arbitrary ranges or increases.)

> [!question]- Does the operation need to be commutative?
> No, only associative: the tree always combines the left child before the right. Matrix products and string hashes work in the recursive version. The bottom-up version's simple loop assumes commutativity unless you keep separate left and right accumulators.

> [!question]- In the bottom-up tree with `n = 3`, which elements does node 1 combine, and in what order?
> Leaves are at indices 3, 4, 5 (`a[0]`, `a[1]`, `a[2]`); node 2 = `a[1] + a[2]`, node 1 = node 2 + node 3 = `(a[1] + a[2]) + a[0]`. The total is right for sums, but the order is not the array order, so a non-commutative operation at the root is wrong.

> [!question]- Range add `+5` on `[0, 7]` of an 8-element lazy tree: how many nodes are touched?
> One: the root is fully covered, so `apply` updates its sum by `5 · 8` and sets its tag. Nothing below changes until a later operation needs to go deeper.

> [!question]- Range assign 0 on `[2, 4]`, then query `[2, 4]`, with a tag where 0 means "nothing pending". What's returned?
> The old values. Assigning 0 sets the tag to 0, which looks like "no pending assignment", so the push does nothing; and if `apply` also skips zeros, even the covered node's sum isn't updated. Use a separate flag.

> [!question]- Assign `7` on `[0, 3]`, then add `2` on `[0, 3]`, then assign `1` on `[2, 3]`. What's `a`?
> `[9, 9, 1, 1]`. The add after an assignment adds to it (`7 + 2`); the later assignment overwrites the add in its range. With the affine form, the tags compose automatically.

> [!question]- `firstAtLeast(x)` on a max tree: why not binary search with range-max queries?
> That works too, but each step is an `O(log n)` query: `O(log² n)` total. Descending from the root makes one choice per level: `O(log n)`.

> [!question]- Count smaller after self for `[2, 2, 1]`?
> `[1, 1, 0]`: for each `2`, only the `1` to its right is strictly smaller; equal values don't count. Querying `[0, v]` instead of `[0, v − 1]` counts equal values and gives `[2, 1, 0]`.

> [!question]- My Calendar III: are bookings `[10, 20)` and `[20, 30)` overlapping?
> No: the range added is `[start, end − 1]`, so the first covers 10–19 and the second 20–29. Adding on `[start, end]` makes touching bookings overlap at 20.

> [!question]- When is a segment tree the wrong choice?
> When the data is static (prefix sums give `O(1)` sums; a sparse table gives `O(1)` min/max), when only prefix sums with point updates are needed (a Fenwick tree is shorter and faster), and when all queries are offline and Mo's algorithm fits ([[DSA/04 - Trees and Hierarchical Structures/09 - Sqrt Decomposition|Sqrt Decomposition]]).

---

## 13. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| Recursive tree array size | `4n` | not complete |
| Bottom-up tree size | `2n` | leaves at `n…2n−1` |
| Segments per query | `≤ 2⌈log₂ n⌉` | two per level |
| Nodes visited per level | `≤ 4` | only ends recurse |
| Identity for min / max / gcd / product | `+∞` / `−∞` / `0` / `1` | |
| `query(2, 6)` on `[5,8,6,3,2,7,2,6]` | `20` | `[2,3] + [4,5] + [6,6]` |
| Max subarray `[-2,1,-3,4,-1,2,1,-5,4]` | `6` | crossing case `L.suf + R.pre` |
| `firstAtLeast(6)` on `[3,1,4,1,5,9,2,6]` | `5` | descent |
| Bottom-up `query(l, r)` | `a[l..r)` | exclusive right |
| Lazy `rangeAdd(1,3,10)` on `[1,2,3,4,5]`, sum all | `45` | |
| Assign 7, add 2, assign 1 on `[2,3]` | `[9, 9, 1, 1]` | tag composition |
| Count smaller `[5,2,6,1]` | `[2, 1, 1, 0]` | |
| Calendar III example | `1,1,2,3,3,3` | `[start, end − 1]` |
| Merge-sort tree memory / query | `O(n log n)` / `O(log² n)` | |
| Dynamic tree nodes | `O(q log C)` | created on split |

---

## 14. Summary

- A segment tree stores op-over-segment at every node of a balanced tree over the array; root at index 1, children `2i` and `2i + 1`, array size `4n`.
- Queries combine `O(log n)` fully covered nodes; point updates recompute one root-to-leaf path. Any **associative** operation works; the identity for disjoint nodes must be truly neutral (or branch instead).
- Nodes can store composite data: `(sum, pre, suf, best)` for maximum subarray sums, `(max, count)`, gcds, counts for `k`-th-element descents.
- The **bottom-up** version is short and fast for point updates (`2n` memory, right end exclusive, careful with non-commutative ops).
- **Lazy propagation** applies range updates in `O(log n)` with tags pushed down on demand; assign/add combine like affine maps; never use 0 as "no assignment".
- **Dynamic** trees create nodes on demand for huge ranges; **merge-sort trees** answer order-statistics questions on static ranges.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/04 - Trees and Hierarchical Structures/06 - Union-Find|Union-Find]] · Next: [[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees]]
- [[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]]: the static versions
- [[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees]]: shorter code for invertible operations
- [[DSA/04 - Trees and Hierarchical Structures/09 - Sqrt Decomposition|Sqrt Decomposition]]: a simpler `O(√n)` alternative, and offline queries
- [[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]]: implicit treaps for sequences with insertions
- [[DSA/02 - Linear Data Structures/01 - Arrays|Arrays]]: Kadane's algorithm, the single-query version of maximum subarray
- [[DSA/05 - Graphs/09 - Heavy-Light Decomposition|Heavy-Light Decomposition]]: segment trees over tree paths
- [[DSA/08 - Specialized Topics/01 - Intervals and Sweep Line|Intervals and Sweep Line]]: rectangle union and interval coverage
