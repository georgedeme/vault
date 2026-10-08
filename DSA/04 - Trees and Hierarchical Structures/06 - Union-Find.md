# Union-Find (Disjoint Set Union)

A <span class="hl-blue">union-find</span> structure, also called **disjoint set union** (DSU), keeps track of a collection of elements split into non-overlapping groups. It supports two operations: **find** (which group is `x` in?) and **union** (merge the groups of `x` and `y`). With two small optimisations, union by size and path compression, both run in `O(α(n))` amortized time, where `α` is the inverse Ackermann function. That's at most 4 for any input that fits in the universe, so effectively constant.

Union-find is the tool for **dynamic connectivity**: edges arrive one at a time, and you need to know whether two vertices are connected, how many components there are, or whether a new edge closes a cycle. It's the core of Kruskal's minimum spanning tree algorithm and of many grid, grouping, and equivalence problems. This note covers the naive versions and why they're slow, the two optimisations, a complete Java implementation, the standard applications, sets with extra data, offline tricks (reversing deletions, sorting queries by threshold), weighted DSU for ratios and parity, and rollback DSU.

## Contents

- [[#1. The Problem|1. The Problem]]
- [[#2. Naive Implementations|2. Naive Implementations]]
- [[#3. Union by Size or Rank|3. Union by Size or Rank]]
- [[#4. Path Compression|4. Path Compression]]
- [[#5. Complexity|5. Complexity]]
- [[#6. Implementation|6. Implementation]]
- [[#7. Applications|7. Applications]]
- [[#8. Offline Techniques|8. Offline Techniques]]
- [[#9. Weighted Union-Find|9. Weighted Union-Find]]
- [[#10. Rollback DSU (advanced)|10. Rollback DSU (advanced)]]
- [[#11. Common Mistakes|11. Common Mistakes]]
- [[#12. Trick Questions and Special Cases|12. Trick Questions and Special Cases]]
- [[#13. Quick Reference — Non-Obvious Outcomes|13. Quick Reference — Non-Obvious Outcomes]]
- [[#14. Summary|14. Summary]]

---

## 1. The Problem

> [!note] Operations
> - `makeSet(x)`: put `x` in a group of its own (usually done for `0..n−1` at construction).
> - `find(x)`: return the **representative** (root) of `x`'s group. Two elements are in the same group exactly when `find` returns the same representative.
> - `union(x, y)`: merge the groups containing `x` and `y` (nothing happens if they're already one group).

The groups are the equivalence classes of a relation that's built up over time: "connected by edges added so far", "known to be the same account", "known to be equal". Union-find can merge groups but **never split** them; that's the price of its speed ([[#8. Offline Techniques|§8]] and [[#10. Rollback DSU (advanced)|§10]] show the workarounds).

| Need | BFS/DFS | Union-find |
|---|---|---|
| Components of a fixed graph | `O(V + E)` once | `O(E α(V))` |
| Connectivity while edges are **added** | re-run per query: `O(V + E)` each | `O(α(V))` per edge and per query |
| Edges **deleted** | re-run | not supported directly |
| The actual path between two vertices | yes | no |
| Shortest distances | BFS | no |

---

## 2. Naive Implementations

Each group is stored as a tree: every element points to a **parent**, and the root (which points to itself) is the representative.

**Quick-find** stores the representative directly: `id[x]` is `x`'s group. `find` is `O(1)`, but `union` must relabel every member of one group: `O(n)` per union, `O(n²)` for `n` unions.

**Quick-union** links one root under the other:

```
find(x):
    while parent[x] ≠ x: x = parent[x]
    return x

union(a, b):
    parent[find(a)] = find(b)
```

`union` is now cheap, but nothing controls the trees' height. Uniting `0–1`, then `0–2`, `0–3`, … (always putting the old tree under the new single element) builds a chain, and `find` costs `O(n)`.

> [!warning] Link the **roots**, not the elements
> `parent[a] = b` instead of `parent[find(a)] = find(b)` detaches `a` from its group: every other member of `a`'s old group stays behind, still pointing to the old root, and the two groups don't merge. It also orphans `b`'s side if `a` was the old root of a large tree. Always find both roots first.

---

## 3. Union by Size or Rank

When merging, attach the root of the **smaller** tree under the root of the larger one.

```
union(a, b):
    ra = find(a); rb = find(b)
    if ra = rb: return false
    if size[ra] < size[rb]: swap(ra, rb)       -- ra is the larger
    parent[rb] = ra
    size[ra] = size[ra] + size[rb]
    return true
```

![[Union-Find - Union by Size.excalidraw|800]]

**Why the height stays `O(log n)`**: an element's depth grows by one only when its tree is attached under a tree that's at least as large, which at least doubles the size of the tree it's in. A tree can double at most `log₂ n` times, so no element is deeper than `log₂ n`.

**Union by rank** is the same idea with an upper bound on height (`rank`) instead of size: attach the lower-rank root under the higher-rank one, and increase the rank only when the two are equal. Size is usually more useful, because it also answers "how big is `x`'s group?".

---

## 4. Path Compression

During `find(x)`, every node on the path from `x` to the root is pointed **directly at the root**. Later finds from any of those nodes, or from their descendants, take one step.

```
find(x):                                -- recursive form
    if parent[x] ≠ x: parent[x] = find(parent[x])
    return parent[x]
```

![[Union-Find - Path Compression.excalidraw|800]]

| Variant | Code | Passes |
|---|---|---|
| Full compression, recursive | `return parent[x] == x ? x : (parent[x] = find(parent[x]));` | one (with recursion) |
| Full compression, iterative | find the root, then walk the path again repointing each node | two |
| Path halving | `while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }` | one, no recursion |

Path halving makes every node on the path point to its grandparent. It doesn't flatten the path in one go, but it has the same asymptotic guarantee and needs neither recursion nor a second pass.

> [!warning] Recursive `find` and stack depth
> Without union by size, the trees can become chains of length `n` before the first compression, and a recursive `find` on a chain of `10⁵` elements overflows Java's stack ([[DSA/01 - Foundations/02 - Recursion#9. Stack Overflow Limits in Java|Recursion § 9]]). With union by size, the depth is at most `log₂ n` and recursion is safe. The iterative version is safe in both cases.

---

## 5. Complexity

| Version | `union` / `find`, amortized over a sequence of operations |
|---|---|
| Quick-find | `O(n)` / `O(1)` |
| Quick-union, no heuristics | `O(n)` / `O(n)` |
| Union by size or rank only | `O(log n)` worst case |
| Path compression only | `O(log n)` amortized |
| **Both** | **`O(α(n))`** amortized |

`α(n)`, the inverse Ackermann function, grows absurdly slowly: `α(n) ≤ 4` for every `n` below `2^(2^(2^65536))`. Tarjan proved the bound is tight: no pointer-based structure can do better than `Θ(α(n))` amortized per operation.

> [!info]- Why "amortized"
> A single `find` can still take `O(log n)` steps (with union by size) the first time it walks a long path. But it then flattens that path, so the same work isn't paid again. Averaged over any sequence of `m` operations, the total is `O(m α(n))`. The analysis (Tarjan 1975; a cleaner proof by Seidel and Sharir) is well beyond interview level; the practical rule is "use both optimisations and treat each operation as constant time".

---

## 6. Implementation

```java
static class DSU {
    private final int[] parent, size;
    private int components;

    DSU(int n) {
        parent = new int[n];
        size = new int[n];
        for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; }
        components = n;
    }

    int find(int x) {
        int root = x;
        while (parent[root] != root) root = parent[root];
        while (parent[x] != root) {                // second pass: compress the path
            int next = parent[x];
            parent[x] = root;
            x = next;
        }
        return root;
    }

    boolean union(int a, int b) {                  // false if a and b were already together
        int ra = find(a), rb = find(b);
        if (ra == rb) return false;
        if (size[ra] < size[rb]) { int t = ra; ra = rb; rb = t; }   // ra: the larger group
        parent[rb] = ra;
        size[ra] += size[rb];
        components--;
        return true;
    }

    boolean connected(int a, int b) { return find(a) == find(b); }
    int sizeOf(int x) { return size[find(x)]; }    // size[] is only valid at roots
    int components() { return components; }
}
```

Returning a `boolean` from `union` is the most useful design choice: `false` means "this edge connects two vertices that were already connected", which is cycle detection, redundant-edge detection, and "did the number of components change?" in one call. Every successful union reduces the component count by one, so the count is `n − (successful unions)`.

### 6.1 Keeping data per group

Any value that combines associatively over a merge (size, sum, minimum, maximum, a count of special elements) can be stored at the root and combined in `union`:

```
union(a, b):
    … after parent[rb] = ra:
    sum[ra] += sum[rb]; min[ra] = min(min[ra], min[rb]); …
```

The values at non-root elements become stale and must never be read directly: always go through `find`. Data that would have to be **split** (a list of members that's later partitioned) doesn't fit; data that just merges does. For merging actual member lists, append the smaller list to the larger ("small to large"), which keeps the total work `O(n log n)`.

### 6.2 Elements that aren't `0..n−1`

For strings, coordinates, or large sparse integers, map each element to an index the first time it's seen (`Map<T, Integer>`, with `map.size()` as the next index), or keep the parent links themselves in a `HashMap<T, T>`. Grid cell `(r, c)` in an `R × C` grid is usually index `r · C + c`.

---

## 7. Applications

### 7.1 Counting components; making a network connected

```java
static int countComponents(int n, int[][] edges) {
    DSU d = new DSU(n);
    for (int[] e : edges) d.union(e[0], e[1]);
    return d.components();
}
```

"Minimum number of cable moves to connect all `n` computers" is `components − 1`, provided there are at least `n − 1` cables in total (otherwise `−1`): every redundant cable can be moved to join two components.

### 7.2 Cycle detection in undirected graphs

An edge whose endpoints are already connected closes a cycle.

```java
static int[] findRedundantConnection(int[][] edges) {    // vertices 1..n, n = edges.length
    DSU d = new DSU(edges.length + 1);
    for (int[] e : edges) if (!d.union(e[0], e[1])) return e;
    return new int[0];
}

static boolean validTree(int n, int[][] edges) {
    if (edges.length != n - 1) return false;       // a tree on n vertices has exactly n − 1 edges
    DSU d = new DSU(n);
    for (int[] e : edges) if (!d.union(e[0], e[1])) return false;   // a cycle
    return true;                                   // n − 1 edges and no cycle ⇒ connected
}
```

`[[1, 2], [1, 3], [2, 3]]` → `[2, 3]`. For `validTree`, checking the edge count first is what makes "no cycle" sufficient: an acyclic graph with `n − 1` edges is connected. This only works for **undirected** graphs; directed cycles need DFS colouring or topological sort ([[DSA/05 - Graphs/02 - Topological Sorting|Topological Sorting]]).

### 7.3 Equality equations

Given equations like `"a==b"` and `"b!=c"`, can they all hold? Merge for every `==` **first**, then check that no `!=` connects two letters in the same group.

```java
static boolean equationsPossible(String[] eqs) {
    DSU d = new DSU(26);
    for (String e : eqs)
        if (e.charAt(1) == '=') d.union(e.charAt(0) - 'a', e.charAt(3) - 'a');
    for (String e : eqs)
        if (e.charAt(1) == '!' && d.connected(e.charAt(0) - 'a', e.charAt(3) - 'a')) return false;
    return true;
}
```

`["a==b", "b!=a"]` → `false`; `["a==b", "b==c", "a==c"]` → `true`; `["a!=a"]` → `false`. Checking `!=` in input order, before later `==` equations are merged, accepts `["a!=c", "a==b", "b==c"]`, which is contradictory.

### 7.4 Accounts merge

Each account is a name followed by emails; two accounts belong to the same person if they share **any** email. Union account indices through shared emails, then collect each group's emails.

```java
static List<List<String>> accountsMerge(List<List<String>> accounts) {
    Map<String, Integer> owner = new HashMap<>();  // email → first account that listed it
    DSU d = new DSU(accounts.size());
    for (int i = 0; i < accounts.size(); i++)
        for (int k = 1; k < accounts.get(i).size(); k++) {
            Integer prev = owner.putIfAbsent(accounts.get(i).get(k), i);
            if (prev != null) d.union(prev, i);    // shared email: same person
        }
    Map<Integer, TreeSet<String>> groups = new HashMap<>();
    for (Map.Entry<String, Integer> e : owner.entrySet())
        groups.computeIfAbsent(d.find(e.getValue()), x -> new TreeSet<>()).add(e.getKey());
    List<List<String>> res = new ArrayList<>();
    for (Map.Entry<Integer, TreeSet<String>> g : groups.entrySet()) {
        List<String> acc = new ArrayList<>();
        acc.add(accounts.get(g.getKey()).get(0));  // the name
        acc.addAll(g.getValue());                  // emails, sorted
        res.add(acc);
    }
    return res;
}
```

Two accounts with the **same name** but no shared email are different people and must stay separate; grouping by name is the classic wrong answer.

### 7.5 Online grid connectivity: number of islands II

Cells of a water grid become land one at a time; report the number of islands after each addition. A new cell is a new island, and each successful union with a neighbouring land cell merges two islands into one.

```java
static List<Integer> numIslands2(int m, int n, int[][] positions) {
    DSU d = new DSU(m * n);
    boolean[] land = new boolean[m * n];
    int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
    int islands = 0;
    List<Integer> res = new ArrayList<>();
    for (int[] p : positions) {
        int id = p[0] * n + p[1];
        if (!land[id]) {                           // the same cell may be added twice
            land[id] = true;
            islands++;
            for (int[] dd : dirs) {
                int r = p[0] + dd[0], c = p[1] + dd[1];
                if (r >= 0 && r < m && c >= 0 && c < n && land[r * n + c] && d.union(id, r * n + c))
                    islands--;                     // two islands became one
            }
        }
        res.add(islands);
    }
    return res;
}
```

`m = n = 3`, positions `[[0, 0], [0, 1], [1, 2], [2, 1]]` → `[1, 1, 2, 3]`. `d.components()` can't be used here: it also counts the water cells. A static grid is easier with BFS/DFS flood fill ([[DSA/05 - Graphs/01 - Graph Representations and Traversals|Graph Traversals]]); union-find wins when the grid changes between queries.

### 7.6 Groups whose members can be freely rearranged

If positions `i` and `j` can be swapped any number of times, then within a connected group of positions **any** permutation is reachable. So: find the groups, sort each group's letters, and put them back in the group's positions in order.

```java
static String smallestStringWithSwaps(String s, List<List<Integer>> pairs) {
    int n = s.length();
    DSU d = new DSU(n);
    for (List<Integer> p : pairs) d.union(p.get(0), p.get(1));
    Map<Integer, PriorityQueue<Character>> groups = new HashMap<>();
    for (int i = 0; i < n; i++)
        groups.computeIfAbsent(d.find(i), x -> new PriorityQueue<>()).add(s.charAt(i));
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < n; i++) sb.append(groups.get(d.find(i)).poll());   // smallest letter left in i's group
    return sb.toString();
}
```

`"dcab"`, pairs `[[0, 3], [1, 2]]` → `"bacd"`; with `[0, 2]` added → `"abcd"`. The same "connected positions are interchangeable" idea solves "minimise Hamming distance after allowed swaps".

### 7.7 Longest consecutive sequence

Union each value with its successor if present; the largest group is the answer.

```java
static int longestConsecutive(int[] a) {
    Map<Integer, Integer> idx = new HashMap<>();
    for (int x : a) idx.putIfAbsent(x, idx.size());     // distinct values → 0, 1, 2, …
    DSU d = new DSU(idx.size());
    for (int x : idx.keySet())
        if (x != Integer.MAX_VALUE && idx.containsKey(x + 1))   // x + 1 would wrap to MIN_VALUE
            d.union(idx.get(x), idx.get(x + 1));
    int best = 0;
    for (int i = 0; i < idx.size(); i++) best = Math.max(best, d.sizeOf(i));
    return best;
}
```

`[100, 4, 200, 1, 3, 2]` → `4`. The hash-set solution that only starts counting at sequence starts is simpler and also `O(n)` ([[DSA/02 - Linear Data Structures/06 - Hash Tables#9.2 Longest consecutive sequence in O(n)|Hash Tables § 9.2]]); this version shows how DSU works over arbitrary values.

### 7.8 Kruskal's minimum spanning tree

Sort edges by weight and take each edge whose `union` succeeds (it joins two different components). Covered in [[DSA/05 - Graphs/04 - Minimum Spanning Trees|Minimum Spanning Trees]].

---

## 8. Offline Techniques

Union-find can't delete, and it can't answer "were `u` and `v` connected using only edges lighter than `L`?" once heavier edges are in. Both limits disappear when all operations are known in advance and can be **reordered**.

### 8.1 Reversing deletions

"Edges are removed one by one; after each removal, how many components are there?" Read the removals backwards: starting from the graph with all of them already removed, each step of the reversed sequence **adds** an edge, which union-find handles.

```java
static int[] componentsAfterRemovals(int n, int[][] edges, int[] removeOrder) {   // indices into edges
    boolean[] removed = new boolean[edges.length];
    for (int e : removeOrder) removed[e] = true;
    DSU d = new DSU(n);
    for (int i = 0; i < edges.length; i++)
        if (!removed[i]) d.union(edges[i][0], edges[i][1]);    // the graph after ALL removals
    int[] res = new int[removeOrder.length];
    for (int k = removeOrder.length - 1; k >= 0; k--) {
        res[k] = d.components();                   // state right after the k-th removal
        int e = removeOrder[k];
        d.union(edges[e][0], edges[e][1]);         // step back in time: un-remove it
    }
    return res;
}
```

![[Union-Find - Reversed Deletions.excalidraw|800]]

Path `0 – 1 – 2` with edges `[[0, 1], [1, 2]]`, removing edge 0 then edge 1 → `[2, 3]`. The answer for step `k` must be recorded **before** re-adding the `k`-th edge.

### 8.2 Queries sorted by a threshold

"Is there a path from `u` to `v` using only edges with weight `< limit`?", many queries with different limits. Sort the edges by weight and the queries by limit; before answering a query, union every edge lighter than its limit.

```java
static boolean[] distanceLimitedPathsExist(int n, int[][] edges, int[][] queries) {   // queries: {u, v, limit}
    int[][] es = edges.clone();
    Arrays.sort(es, Comparator.comparingInt(e -> e[2]));
    Integer[] order = new Integer[queries.length];
    for (int i = 0; i < order.length; i++) order[i] = i;
    Arrays.sort(order, Comparator.comparingInt(i -> queries[i][2]));
    DSU d = new DSU(n);
    boolean[] res = new boolean[queries.length];
    int j = 0;
    for (int qi : order) {
        while (j < es.length && es[j][2] < queries[qi][2]) {   // strictly lighter than the limit
            d.union(es[j][0], es[j][1]);
            j++;
        }
        res[qi] = d.connected(queries[qi][0], queries[qi][1]);
    }
    return res;
}
```

`n = 3`, edges `[[0, 1, 2], [1, 2, 4], [2, 0, 8], [1, 0, 16]]`, queries `[[0, 1, 2], [0, 2, 5]]` → `[false, true]`: the only `0–1` edge lighter than 2 doesn't exist, and `0 – 1 – 2` uses weights 2 and 4, both below 5. `O((E + Q) log)` for the sorts, near-linear after. The same shape solves "minimum effort path" when phrased as "smallest threshold that connects the corners" ([[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]] on the answer is the alternative).

---

## 9. Weighted Union-Find

Store, on each edge to the parent, a **relation** between an element and its parent, and compose relations along the path during `find`. The relation must compose and invert: ratios (multiply), offsets (add), parities (XOR).

### 9.1 Ratios: evaluate division

Given `a / b = 2` and `b / c = 3`, answer `a / c`. Keep `ratio(x) = x / parent(x)`; after path compression, `ratio(x) = x / root`, so `a / b = ratio(a) / ratio(b)` when they share a root.

```java
static class RatioDSU {
    private final Map<String, String> parent = new HashMap<>();
    private final Map<String, Double> ratio = new HashMap<>();   // ratio(x) = x / parent(x)

    private void add(String x) {
        if (!parent.containsKey(x)) { parent.put(x, x); ratio.put(x, 1.0); }
    }

    String find(String x) {                        // afterwards ratio(x) = x / root
        String p = parent.get(x);
        if (p.equals(x)) return x;
        String root = find(p);
        ratio.put(x, ratio.get(x) * ratio.get(p)); // x/p · p/root
        parent.put(x, root);
        return root;
    }

    void union(String a, String b, double value) { // records a / b = value
        add(a); add(b);
        String ra = find(a), rb = find(b);
        if (ra.equals(rb)) return;
        parent.put(ra, rb);
        ratio.put(ra, value * ratio.get(b) / ratio.get(a));   // ra/rb = (a/b) · (b/rb) / (a/ra)
    }

    double query(String a, String b) {
        if (!parent.containsKey(a) || !parent.containsKey(b)) return -1.0;   // unknown variable
        if (!find(a).equals(find(b))) return -1.0;                           // no relation known
        return ratio.get(a) / ratio.get(b);        // (a/root) / (b/root)
    }
}
```

![[Union-Find - Weighted Ratios.excalidraw|800]]

With `a / b = 2`, `b / c = 3`: `a / c = 6`, `b / a = 0.5`, `a / a = 1`, `a / e = −1` (unknown), and `x / x = −1` for a variable never mentioned (the problem says so: "unknown" beats "trivially 1").

### 9.2 Parity: bipartiteness online

Store `parity(x) = colour(x) XOR colour(parent(x))`. An edge `u–v` requires different colours. If `u` and `v` are already in the same set and have the **same** parity relative to the root, the edge closes an odd cycle, and the graph isn't bipartite.

```java
static boolean isBipartiteDSU(int n, int[][] edges) {
    int[] parent = new int[n], parity = new int[n];    // parity[x] = colour(x) XOR colour(parent[x])
    for (int i = 0; i < n; i++) parent[i] = i;
    for (int[] e : edges) {
        int[] ru = findParity(parent, parity, e[0]), rv = findParity(parent, parity, e[1]);
        if (ru[0] == rv[0]) {
            if (ru[1] == rv[1]) return false;          // same set, same colour: odd cycle
        } else {
            parent[ru[0]] = rv[0];
            parity[ru[0]] = ru[1] ^ rv[1] ^ 1;         // forces colour(u) ≠ colour(v)
        }
    }
    return true;
}

static int[] findParity(int[] parent, int[] parity, int x) {   // {root, colour of x relative to the root}
    if (parent[x] == x) return new int[]{x, 0};
    int[] r = findParity(parent, parity, parent[x]);
    parity[x] ^= r[1];                                 // now relative to the root
    parent[x] = r[0];
    return new int[]{r[0], parity[x]};
}
```

A triangle `0–1–2–0` → `false`; a square → `true`. The same scheme handles "`x` and `y` are enemies / friends" puzzles. BFS 2-colouring is simpler when the whole graph is given at once ([[DSA/05 - Graphs/06 - Bipartite Graphs and Matching|Bipartite Graphs]]); the DSU version handles edges arriving over time and tells you the **first** edge that breaks bipartiteness.

> [!info]- Deriving the parity of the new link
> Let `pu` and `pv` be the parities of `u` and `v` relative to their roots `ru` and `rv`, so `colour(u) = pu ⊕ colour(ru)` and `colour(v) = pv ⊕ colour(rv)`. Linking `ru` under `rv` with parity `q` sets `colour(ru) = q ⊕ colour(rv)`. The edge requires `colour(u) ⊕ colour(v) = 1`, that is `pu ⊕ q ⊕ pv = 1`, so `q = pu ⊕ pv ⊕ 1`. The ratio formula in §9.1 comes from the same algebra with multiplication instead of XOR.

---

## 10. Rollback DSU (advanced)

Some offline algorithms (divide and conquer over time, "offline dynamic connectivity" with a segment tree over the time axis, backtracking searches) need to **undo** the most recent unions. Path compression rewrites many pointers per `find`, so it can't be undone cheaply. Drop it, keep union by size (height `≤ log₂ n`, so `find` is `O(log n)`), and record every union on a stack:

```java
static class RollbackDSU {
    private final int[] parent, size;
    private final Deque<int[]> history = new ArrayDeque<>();   // {attached root, new parent root}

    RollbackDSU(int n) {
        parent = new int[n]; size = new int[n];
        for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; }
    }

    int find(int x) {                              // no path compression: it couldn't be undone
        while (parent[x] != x) x = parent[x];
        return x;
    }

    boolean union(int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra == rb) { history.push(new int[]{-1, -1}); return false; }   // record no-ops too
        if (size[ra] < size[rb]) { int t = ra; ra = rb; rb = t; }
        parent[rb] = ra;
        size[ra] += size[rb];
        history.push(new int[]{rb, ra});
        return true;
    }

    void rollback() {                              // undo the most recent union() call
        int[] h = history.pop();
        if (h[0] == -1) return;
        parent[h[0]] = h[0];
        size[h[1]] -= size[h[0]];
    }
}
```

Recording failed unions as no-ops keeps "one `rollback` per `union` call", so callers don't need to remember which calls succeeded. A **persistent** DSU (every version queryable) is built the same way on top of persistent arrays; both are contest-level tools.

---

## 11. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| `parent[a] = b` | groups don't merge; members left behind | `parent[find(a)] = find(b)` |
| Reading `size[x]` or other data at a non-root | stale values | `size[find(x)]` |
| No union by size and recursive `find` | `StackOverflowError` on chains | union by size, or iterative `find` |
| Updating `size` of the wrong root after the swap | sizes wrong; balancing breaks | swap first, then attach `rb` under `ra` and add to `ra` |
| Decrementing the component count on every `union` call | count too low | only on successful unions |
| Comparing `parent[a] == parent[b]` for connectivity | false negatives before compression | `find(a) == find(b)` |
| `validTree` without the edge count check | disconnected forests accepted | require `n − 1` edges |
| Union-find for directed cycles | wrong answers | DFS colouring / topological sort |
| Checking `!=` constraints during the `==` pass | contradictions missed | all unions first, then checks |
| Grouping accounts by name | different people merged | union through shared emails only |
| `numIslands2` counting a repeated cell again | island count too high | skip cells that are already land |
| Using `components()` when not all elements are "active" | water counted as islands | keep a separate counter |
| Recording a reversed-deletion answer after re-adding the edge | answers shifted by one step | record, then add |
| Path compression in a rollback DSU | rollback restores the wrong structure | union by size only |
| `x + 1` on `Integer.MAX_VALUE` | wraps to `MIN_VALUE`, links unrelated values | guard the overflow |

---

## 12. Trick Questions and Special Cases

> [!question]- After `n` elements and `k` calls to `union`, how many components are there?
> `n − (number of unions that returned true)`. Calls that join already-connected elements change nothing, so `n − k` is only a lower bound.

> [!question]- With union by size and no path compression, what's the maximum depth of any element?
> `⌊log₂ n⌋`. An element gets deeper only when its tree joins one at least as large, which doubles the size of its tree; that can happen at most `log₂ n` times.

> [!question]- Is `α(n)` really constant?
> Not mathematically: it grows without bound. But `α(n) ≤ 4` for every `n` that could ever be stored, so in practice union-find with both optimisations is constant time per operation.

> [!question]- After path compression, is `rank` still the height of the tree?
> No: compression can make the tree shorter without updating ranks. Rank becomes an **upper bound** on height, which is all union by rank needs. (Size, by contrast, stays exact, because compression doesn't change membership.)

> [!question]- Can union-find tell you whether a **directed** graph has a cycle?
> No. Edges `0 → 1`, `0 → 2`, `1 → 2` have no directed cycle, but the third edge joins two already-connected vertices, so union-find reports one. It ignores direction.

> [!question]- Can union-find remove an edge?
> Not directly: a union might have been the only link between two parts, and nothing records that. Workarounds: process the operations backwards (§8.1), roll back in LIFO order (§10), or use a dynamic connectivity structure (link-cut trees, Euler tour trees: advanced).

> [!question]- `equationsPossible(["a!=c", "a==b", "b==c"])`?
> `false`: `a == b == c` contradicts `a != c`. A single left-to-right pass that checks each `!=` when it's read sees `a` and `c` still separate and wrongly answers `true`.

> [!question]- Two accounts `["John", "a@x"]` and `["John", "b@x"]`: one person or two?
> Two. Accounts merge only through a shared email; equal names prove nothing.

> [!question]- `validTree(4, [[0, 1], [2, 3], [1, 0]])`?
> `false`, for two reasons: there are 3 edges (correct count), but `[1, 0]` closes a cycle, and vertices `{2, 3}` are cut off from `{0, 1}`. With exactly `n − 1` edges, "no cycle" and "connected" are equivalent, so either check alone (plus the count) suffices.

> [!question]- In evaluate division, what's `x / x` when `x` never appeared in any equation?
> `−1.0` ("unknown"), by the problem's definition, even though any number divided by itself is 1. `a / a` for a known `a` is `1.0`.

> [!question]- Are a triangle and a 4-cycle bipartite?
> The triangle isn't (odd cycle: the parity DSU finds `u` and `v` in the same set with the same colour); the 4-cycle is.

> [!question]- Why does reversing deletions work, and what must the input guarantee?
> Running the removal sequence backwards turns every removal into an insertion, which union-find supports. It needs the entire sequence of removals in advance (offline), and each edge must be removed at most once (otherwise "the graph after all removals" isn't well defined without multiplicities).

> [!question]- `numIslands2` adds the same cell twice. What should the count do?
> Nothing: the second addition changes no land. Code that doesn't check `land[id]` first increments the island count, and then every union with the neighbours fails (they're already in the cell's group), so the count ends one too high.

> [!question]- Does it matter which root becomes the parent when the sizes are equal?
> Not for correctness or complexity; either choice keeps the doubling argument (the attached tree is at most as large as the other). It does matter for the parity and ratio DSUs, where the stored relation must match the direction of the link.

---

## 13. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `union(a, b)` when already connected | `false`, no change | |
| Components | `n − successful unions` | |
| Max depth with union by size | `⌊log₂ n⌋` | doubling argument |
| Both optimisations | `O(α(n))` amortized, `α ≤ 4` | |
| Path compression only | `O(log n)` amortized | |
| `size[x]` at a non-root | stale | read `size[find(x)]` |
| Rank after compression | upper bound on height | |
| Directed cycle detection | not possible | direction ignored |
| `findRedundantConnection([[1,2],[1,3],[2,3]])` | `[2, 3]` | first edge closing a cycle |
| `equationsPossible(["a!=c","a==b","b==c"])` | `false` | unions first |
| `numIslands2(3, 3, [[0,0],[0,1],[1,2],[2,1]])` | `[1, 1, 2, 3]` | |
| `smallestStringWithSwaps("dcab", [[0,3],[1,2]])` | `"bacd"` | sort per group |
| Evaluate division `a/b=2, b/c=3` → `a/c` | `6.0` | ratio to root |
| `x / x` for an unknown `x` | `−1.0` | unknown variable |
| Triangle bipartite? | `false` | odd cycle |
| Remove edges | reverse the sequence offline | |
| Rollback DSU `find` | `O(log n)` | no compression |

---

## 14. Summary

- Union-find maintains disjoint groups under **merges**: `find` returns a group's root, `union` links two roots. It can't split groups.
- **Union by size** (or rank) keeps trees `O(log n)` deep; **path compression** flattens paths during `find`. Together they give `O(α(n))`, effectively constant.
- A `boolean` `union` detects redundant edges and cycles in undirected graphs; a component counter decreases on each successful union; per-group data lives at the root.
- Applications: components, cycle detection, valid tree, equality constraints (unions before checks), accounts merge, online islands, interchangeable positions, Kruskal.
- **Offline** reordering handles deletions (process them backwards) and threshold queries (sort edges and queries together).
- **Weighted** DSU stores a relation to the parent (ratio, offset, parity) and composes it along paths; **rollback** DSU drops path compression to support undo.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/04 - Trees and Hierarchical Structures/05 - Tries|Tries]] · Next: [[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees|Segment Trees]]
- [[DSA/05 - Graphs/01 - Graph Representations and Traversals|Graph Representations and Traversals]]: BFS/DFS components on static graphs
- [[DSA/05 - Graphs/04 - Minimum Spanning Trees|Minimum Spanning Trees]]: Kruskal's algorithm
- [[DSA/05 - Graphs/06 - Bipartite Graphs and Matching|Bipartite Graphs and Matching]]: 2-colouring
- [[DSA/05 - Graphs/05 - Graph Connectivity|Graph Connectivity]]: bridges, articulation points, SCCs (what DSU can't do)
- [[DSA/02 - Linear Data Structures/06 - Hash Tables|Hash Tables]]: mapping arbitrary elements to indices
- [[DSA/01 - Foundations/01 - Complexity Analysis|Complexity Analysis]]: amortized analysis
