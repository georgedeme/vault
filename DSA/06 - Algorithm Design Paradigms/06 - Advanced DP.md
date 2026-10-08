# Advanced DP

The DPs in [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]] run over prefixes, pairs of prefixes and capacities. This note covers the state shapes that need more machinery: **subsets** as bitmasks (TSP, assignment, partitioning, profile DP over a grid), **sums over subsets**, **trees** (subtree states, rerooting), **intervals** (choosing the last or first operation), **digits** of a bound (counting numbers with a property), and **probabilities**. The second half covers **optimisations of the transition**: prefix sums, a monotonic deque, the convex hull trick, and divide-and-conquer optimisation, which turn `O(n²)` or `O(k·n²)` DPs into near-linear ones.

Most of this is *(advanced)* in the syllabus sense: contest-oriented, but bitmask DP, tree DP, interval DP and the monotonic-deque optimisation all appear in harder interview problems. The method from [[DSA/06 - Algorithm Design Paradigms/04 - Dynamic Programming Fundamentals|DP Fundamentals]] still applies to every section: define the state in one sentence, take the last decision, fix an evaluation order.

## Contents

- [[#1. Bitmask DP|1. Bitmask DP]]
- [[#2. DP over Subsets|2. DP over Subsets]]
- [[#3. Tree DP|3. Tree DP]]
- [[#4. Interval DP|4. Interval DP]]
- [[#5. Digit DP|5. Digit DP]]
- [[#6. Probability and Expected Value|6. Probability and Expected Value]]
- [[#7. Optimising Transitions|7. Optimising Transitions]]
- [[#8. Common Mistakes|8. Common Mistakes]]
- [[#9. Trick Questions and Special Cases|9. Trick Questions and Special Cases]]
- [[#10. Quick Reference — Non-Obvious Outcomes|10. Quick Reference — Non-Obvious Outcomes]]
- [[#11. Summary|11. Summary]]

---

## 1. Bitmask DP

When `n ≤ 20` or so and the state must remember **which** items have been used (not just how many), encode that set as an integer whose bit `i` says whether item `i` is in it ([[DSA/01 - Foundations/03 - Bit Manipulation#7. Bitmasks as Sets|Bit Manipulation § 7]]). There are `2ⁿ` sets, about a million for `n = 20`, so `O(2ⁿ · n)` or `O(2ⁿ · n²)` is feasible where `O(n!)` isn't.

> [!tip] Order of evaluation comes for free
> Adding an element to a set makes its mask numerically **larger** (a bit goes from 0 to 1). So iterating `mask` from `0` to `2ⁿ − 1` visits every subset before its supersets: a valid order for any DP whose transitions add elements.

### 1.1 Travelling salesman (Held–Karp)

The shortest tour that starts at city 0, visits every city once, and returns. Brute force is `(n − 1)!`; the DP only remembers **which** cities have been visited and **where** the path is now, not the order.

> [!note] State and recurrence
> `dp[mask][v]` = the shortest path that starts at 0, visits exactly the cities in `mask`, and ends at `v ∈ mask`.
> ```
> dp[{0}][0] = 0
> dp[mask ∪ {u}][u] = min(…, dp[mask][v] + dist[v][u])     for u ∉ mask
> answer = min over v of dp[all][v] + dist[v][0]
> ```
> `O(2ⁿ · n²)` time, `O(2ⁿ · n)` memory.

```java
static int tsp(int[][] dist) {
    int n = dist.length, full = 1 << n;
    if (n == 1) return 0;
    final int INF = Integer.MAX_VALUE / 2;
    int[][] dp = new int[full][n];
    for (int[] row : dp) Arrays.fill(row, INF);
    dp[1][0] = 0;                                  // at city 0, having visited {0}
    for (int mask = 1; mask < full; mask += 2)     // odd masks only: city 0 is always visited
        for (int v = 0; v < n; v++) {
            if (dp[mask][v] >= INF) continue;      // unreachable (or v ∉ mask)
            for (int u = 0; u < n; u++) {
                if ((mask >> u & 1) != 0) continue;
                int next = mask | 1 << u;
                dp[next][u] = Math.min(dp[next][u], dp[mask][v] + dist[v][u]);
            }
        }
    int best = INF;
    for (int v = 1; v < n; v++) best = Math.min(best, dp[full - 1][v] + dist[v][0]);
    return best;
}
```

![[Advanced DP - Bitmask States.excalidraw|800]]

`[[0,10,15,20],[10,0,35,25],[15,35,0,30],[20,25,30,0]]` → `80` (`0 → 1 → 3 → 2 → 0`). For `n = 20` the table holds `2²⁰ · 20 ≈ 2·10⁷` ints (80 MB): close to typical limits, which is why bitmask DP stops around `n = 20`.

### 1.2 Assignment: the mask says which jobs are taken

`n` people, `n` jobs, `cost[p][j]`; give each person one job, minimising the total. Assign people in order `0, 1, 2, …`: the number of jobs already taken, `popcount(mask)`, **is** the next person, so the state needs only the mask.

```java
static int minCostAssignment(int[][] cost) {
    int n = cost.length;
    int[] dp = new int[1 << n];                    // dp[mask]: cheapest way to give the jobs in mask to persons 0..|mask|−1
    Arrays.fill(dp, Integer.MAX_VALUE / 2);
    dp[0] = 0;
    for (int mask = 0; mask < (1 << n); mask++) {
        int person = Integer.bitCount(mask);
        if (person == n) continue;
        for (int job = 0; job < n; job++)
            if ((mask >> job & 1) == 0)
                dp[mask | 1 << job] = Math.min(dp[mask | 1 << job], dp[mask] + cost[person][job]);
    }
    return dp[(1 << n) - 1];
}
```

`[[9,2,7,8],[6,4,3,7],[5,8,1,8],[7,6,9,4]]` → `13` (`2 + 6 + 1 + 4`). `O(2ⁿ · n)`. Beyond `n ≈ 20`, the Hungarian algorithm solves assignment in `O(n³)`.

### 1.3 BFS over (node, mask): shortest path visiting every node

In an unweighted graph, the fewest edges in a walk that visits every node (revisits allowed, any start). The state is (current node, set visited); every edge costs 1, so BFS over states finds the answer.

```java
static int shortestPathLength(int[][] graph) {
    int n = graph.length, full = (1 << n) - 1;
    boolean[][] seen = new boolean[n][1 << n];
    ArrayDeque<int[]> q = new ArrayDeque<>();
    for (int v = 0; v < n; v++) { q.add(new int[]{v, 1 << v}); seen[v][1 << v] = true; }   // every start at once
    for (int steps = 0; !q.isEmpty(); steps++)
        for (int size = q.size(); size > 0; size--) {
            int[] s = q.poll();
            if (s[1] == full) return steps;
            for (int u : graph[s[0]]) {
                int m = s[1] | 1 << u;
                if (!seen[u][m]) { seen[u][m] = true; q.add(new int[]{u, m}); }
            }
        }
    return -1;
}
```

`[[1,2,3],[0],[0],[0]]` → `4` (`1 → 0 → 2 → 0 → 3`); `[[1],[0,2,4],[1,3,4],[2],[1,2]]` → `4`; a single node → `0`. Plain DP over masks doesn't work here, because revisiting nodes makes transitions go "sideways" (same mask), which is exactly what BFS handles.

### 1.4 Partition into k equal subsets with a mask

The backtracking version is in [[DSA/06 - Algorithm Design Paradigms/03 - Backtracking#9. Pruning Strategies|Backtracking § 9]]. As a DP: fill buckets one after another; for a set of used numbers, the partly filled current bucket holds `sum(mask) mod target`, so a reachable mask determines everything about the future.

```java
static boolean canPartitionKBitmask(int[] nums, int k) {   // nums[i] ≥ 1
    int n = nums.length, sum = 0;
    for (int x : nums) sum += x;
    if (sum % k != 0) return false;
    int target = sum / k;
    int[] fill = new int[1 << n];                  // fill[mask]: amount in the current bucket; −1 = unreachable
    Arrays.fill(fill, -1);
    fill[0] = 0;
    for (int mask = 0; mask < (1 << n); mask++) {
        if (fill[mask] < 0) continue;
        for (int i = 0; i < n; i++)
            if ((mask >> i & 1) == 0 && fill[mask] + nums[i] <= target)
                fill[mask | 1 << i] = (fill[mask] + nums[i]) % target;   // a full bucket wraps to 0
    }
    return fill[(1 << n) - 1] == 0;
}
```

`([4, 3, 2, 3, 5, 2, 1], 4)` → `true`; `([1, 2, 3, 4], 3)` → `false`. `O(2ⁿ · n)` with no worst-case surprises, unlike backtracking.

### 1.5 Profile DP: tiling a grid

Count the ways to tile an `R × C` grid with `1 × 2` dominoes. Fill the grid column by column; the state is the **profile**: which cells of the next column are already covered by horizontal dominoes sticking out of the current one.

> [!example]- Domino tilings with a column profile
> ```java
> static long dominoTilings(int rows, int cols) {          // rows ≤ ~12
>     long[] dp = new long[1 << rows];                     // dp[mask]: ways, with mask = cells of this column already covered
>     dp[0] = 1;
>     for (int c = 0; c < cols; c++) {
>         long[] next = new long[1 << rows];
>         for (int mask = 0; mask < (1 << rows); mask++)
>             if (dp[mask] != 0) fillColumn(0, rows, mask, 0, dp[mask], next);
>         dp = next;
>     }
>     return dp[0];                                        // nothing may stick out past the last column
> }
>
> static void fillColumn(int r, int rows, int cur, int nxt, long ways, long[] next) {
>     if (r == rows) { next[nxt] += ways; return; }
>     if ((cur >> r & 1) == 1) { fillColumn(r + 1, rows, cur, nxt, ways, next); return; }   // covered from the left
>     fillColumn(r + 1, rows, cur, nxt | 1 << r, ways, next);                               // horizontal: sticks into the next column
>     if (r + 1 < rows && (cur >> (r + 1) & 1) == 0)
>         fillColumn(r + 2, rows, cur, nxt, ways, next);                                    // vertical: rows r and r + 1
> }
> ```
> `2 × 3` → `3`; `3 × 4` → `11`; `4 × 4` → `36`; `8 × 8` → `12988816`; `3 × 3` → `0` (an odd area can't be tiled). Put the **smaller** dimension in `rows`: the state count is `2^rows`.

---

## 2. DP over Subsets

### 2.1 Enumerating submasks: `O(3ⁿ)` in total

Some transitions pick a **group** of items at once: `dp[mask] = min over valid groups g ⊆ mask of dp[mask \ g] + 1`. The loop `sub = (sub − 1) & mask` visits every non-empty submask of `mask` in decreasing order ([[DSA/01 - Foundations/03 - Bit Manipulation#7.2 Enumerating the submasks of a mask|Bit Manipulation § 7.2]]). Over all masks, the total number of (mask, submask) pairs is `3ⁿ`: each element is outside the mask, in the mask but not the submask, or in both.

**Minimum number of work sessions**: tasks with durations, sessions of length `T`; each session holds a group of tasks with total `≤ T`.

```java
static int minSessions(int[] tasks, int sessionTime) {
    int n = tasks.length, full = (1 << n) - 1;
    int[] sum = new int[1 << n];
    for (int mask = 1; mask <= full; mask++)       // sum of a mask from the mask without its lowest bit
        sum[mask] = sum[mask & (mask - 1)] + tasks[Integer.numberOfTrailingZeros(mask)];
    int[] dp = new int[1 << n];                    // dp[mask]: fewest sessions to finish the tasks in mask
    Arrays.fill(dp, Integer.MAX_VALUE / 2);
    dp[0] = 0;
    for (int mask = 1; mask <= full; mask++) {
        int low = mask & -mask;                    // the session that contains the lowest task
        for (int sub = mask; sub > 0; sub = (sub - 1) & mask)
            if ((sub & low) != 0 && sum[sub] <= sessionTime)
                dp[mask] = Math.min(dp[mask], dp[mask ^ sub] + 1);
    }
    return dp[full];
}
```

`([1, 2, 3], 3)` → `2`; `([3, 1, 3, 1, 1], 8)` → `2`; `([1, 2, 3, 4, 5], 15)` → `1`. Requiring the group to contain the lowest remaining task fixes **which** group is "last", so each partition is considered once instead of once per ordering of its groups. Without it the answer is the same but the work grows.

### 2.2 Sum over subsets (SOS DP): `O(n · 2ⁿ)`

For every mask, compute `F[mask] = Σ A[sub]` over **all** submasks. Enumerating submasks costs `3ⁿ`; SOS processes one bit at a time: after handling bits `0..b`, `F[mask]` holds the sum over submasks that may differ from `mask` only in those bits.

```java
static int[] sumOverSubsets(int[] a, int bits) {  // F[mask] = Σ a[sub] over all sub ⊆ mask
    int[] f = a.clone();
    for (int b = 0; b < bits; b++)
        for (int mask = 0; mask < (1 << bits); mask++)
            if ((mask >> b & 1) == 1) f[mask] += f[mask ^ (1 << b)];
    return f;
}

static int[] countSubmaskElements(int[] nums, int bits) {   // for each x: how many elements y have y ⊆ x
    int[] cnt = new int[1 << bits];
    for (int x : nums) cnt[x]++;
    int[] f = sumOverSubsets(cnt, bits);
    int[] res = new int[nums.length];
    for (int i = 0; i < nums.length; i++) res[i] = f[nums[i]];
    return res;
}
```

`countSubmaskElements([1, 3, 2, 7], 3)` → `[1, 3, 1, 4]` (e.g. `3 = 011` contains `1`, `2` and itself). The same loop with `f[mask] += f[mask | 1 << b]` over masks **without** bit `b` sums over **supersets**. Typical uses: counting pairs with `a & b = 0` (`b ⊆ ~a`), "for each mask, the best element that's a submask of it", inclusion–exclusion over sets.

---

## 3. Tree DP

The subproblems are **subtrees**. Each node's answer is combined from its children's answers in post-order, and the state often needs a small tuple per node ("best if this node is chosen / not chosen").

### 3.1 Returning a pair: house robber III

Houses form a binary tree; robbing two directly connected houses triggers the alarm.

```java
static class TreeNode {
    int val; TreeNode left, right;
    TreeNode(int v) { val = v; }
}

static int robTree(TreeNode root) {
    int[] r = robPair(root);
    return Math.max(r[0], r[1]);
}

static int[] robPair(TreeNode node) {             // {best if node is NOT robbed, best if it IS robbed}
    if (node == null) return new int[]{0, 0};
    int[] l = robPair(node.left), r = robPair(node.right);
    int skip = Math.max(l[0], l[1]) + Math.max(r[0], r[1]);   // the children may do either
    int take = node.val + l[0] + r[0];                         // the children must be skipped
    return new int[]{skip, take};
}
```

`[3, 2, 3, null, 3, null, 1]` → `7`; `[3, 4, 5, 1, 3, null, 1]` → `9`; `[2, 1, 3, null, 4]` → `7` (rob 4 and 3). The last one breaks "rob alternate **levels**": levels sum to 2, 4, 4, and alternating gives 6. Returning both values per node is what memoization by node would otherwise do, without a hash map.

### 3.2 Three states: binary tree cameras

A camera at a node watches the node, its parent and its children. Place the fewest cameras so every node is watched. Each subtree reports one of three states to its parent; deciding as late as possible (put a camera at a node only when a child needs it) is optimal.

```java
static int camerasPlaced;

static int minCameraCover(TreeNode root) {
    camerasPlaced = 0;
    if (cameraState(root) == 0) camerasPlaced++;   // the root itself is still unwatched
    return camerasPlaced;
}

static int cameraState(TreeNode n) {               // 0 = not watched, 1 = watched (no camera), 2 = has a camera
    if (n == null) return 1;                       // nothing to watch: never forces a camera
    int l = cameraState(n.left), r = cameraState(n.right);
    if (l == 0 || r == 0) { camerasPlaced++; return 2; }   // a child is unwatched: only a camera here can cover it
    if (l == 2 || r == 2) return 1;                // watched by a child's camera
    return 0;                                      // let the parent cover it
}
```

`[0, 0, null, 0, 0]` → `1`; `[0, 0, null, 0, null, 0, null, null, 0]` → `2`; a single node → `1`. Treating `null` as "has a camera" instead of "watched" would make every leaf's parent think it's watched, and the leaves would get no coverage.

### 3.3 General trees without recursion

Trees given as edge lists can be paths of `10⁵` nodes, deep enough to overflow a recursive DFS ([[DSA/01 - Foundations/02 - Recursion#9. Stack Overflow Limits in Java|Recursion § 9]]). A BFS order lists every parent before its children; processing it **backwards** gives a valid post-order.

```java
static List<List<Integer>> adjacency(int n, int[][] edges) {
    List<List<Integer>> g = new ArrayList<>();
    for (int i = 0; i < n; i++) g.add(new ArrayList<>());
    for (int[] e : edges) { g.get(e[0]).add(e[1]); g.get(e[1]).add(e[0]); }
    return g;
}

static int[] bfsOrder(List<List<Integer>> g, int[] parent) {   // root 0; fills parent[], returns the visit order
    int n = g.size();
    int[] order = new int[n];
    Arrays.fill(parent, -2);
    parent[0] = -1;
    int head = 0, tail = 0;
    order[tail++] = 0;
    while (head < tail) {
        int v = order[head++];
        for (int u : g.get(v)) if (parent[u] == -2) { parent[u] = v; order[tail++] = u; }
    }
    return order;
}

static int treeDiameter(int n, int[][] edges) {   // edges on the longest path
    List<List<Integer>> g = adjacency(n, edges);
    int[] parent = new int[n];
    int[] order = bfsOrder(g, parent);
    int[] down = new int[n];                       // down[v]: longest path from v down into its subtree
    int best = 0;
    for (int k = n - 1; k >= 0; k--) {             // children before parents
        int v = order[k], top1 = 0, top2 = 0;      // the two longest branches below v
        for (int u : g.get(v)) {
            if (u == parent[v]) continue;
            int len = down[u] + 1;
            if (len > top1) { top2 = top1; top1 = len; } else if (len > top2) top2 = len;
        }
        down[v] = top1;
        best = Math.max(best, top1 + top2);        // the longest path that turns at v
    }
    return best;
}
```

`treeDiameter(3, [[0,1],[0,2]])` → `2`; `treeDiameter(6, [[0,1],[1,2],[2,3],[1,4],[4,5]])` → `4`; `treeDiameter(1, [])` → `0`. The binary-tree version is in [[DSA/04 - Trees and Hierarchical Structures/01 - Binary Trees#7.1 Diameter|Binary Trees § 7.1]].

### 3.4 Rerooting: an answer for every root

**Sum of distances**: for every node, the sum of its distances to all other nodes. Running a DFS from each node is `O(n²)`. Rerooting does it in two `O(n)` passes:

1. **Down**, rooted at 0: `size[v]` and `down[v]` = sum of distances from `v` to the nodes in its subtree; `down[v] = Σ (down[c] + size[c])` over children `c`. Then `ans[0] = down[0]`.
2. **Moving the root** from `p` to its child `c`: the `size[c]` nodes in `c`'s subtree get one step closer, the other `n − size[c]` one step farther, so `ans[c] = ans[p] − size[c] + (n − size[c])`.

```java
static int[] sumOfDistancesInTree(int n, int[][] edges) {
    List<List<Integer>> g = adjacency(n, edges);
    int[] parent = new int[n];
    int[] order = bfsOrder(g, parent);
    int[] size = new int[n], down = new int[n], ans = new int[n];
    for (int k = n - 1; k >= 0; k--) {             // pass 1: children first
        int v = order[k];
        size[v]++;
        if (k > 0) {
            int p = parent[v];
            size[p] += size[v];
            down[p] += down[v] + size[v];          // every node below v is one edge farther from p
        }
    }
    ans[0] = down[0];
    for (int k = 1; k < n; k++) {                  // pass 2: parents first
        int v = order[k];
        ans[v] = ans[parent[v]] - size[v] + (n - size[v]);
    }
    return ans;
}
```

![[Advanced DP - Rerooting.excalidraw|800]]

`n = 6`, edges `[[0,1],[0,2],[2,3],[2,4],[2,5]]` → `[8, 12, 6, 10, 10, 10]`. Rerooting works whenever moving the root across one edge changes the answer by something computable from the two sides' summaries: farthest node from every node, number of edge reversals needed to reach every node from each root, and similar.

> [!info]- Tree knapsack and the `O(n²)` merging bound
> "Choose `k` nodes forming a connected subtree containing the root, maximising value" uses `dp[v][j]` = best with `j` nodes chosen in `v`'s subtree, merged child by child like a knapsack. Merging naively looks like `O(n³)`, but if each merge loops only up to the **current** sizes of the two parts, every pair of nodes is "merged" exactly once (at their lowest common ancestor), so the total is `O(n²)`, or `O(n·k)` with sizes capped at `k`.

---

## 4. Interval DP

`dp[l][r]` describes the subarray or substring `l..r` and is built from shorter intervals inside it, so it's filled **by increasing length** ([[DSA/06 - Algorithm Design Paradigms/04 - Dynamic Programming Fundamentals#7. Evaluation Order|DP Fundamentals § 7]]). The template is matrix-chain multiplication ([[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems#8. Matrix-Chain Multiplication|Classic DP § 8]]): choose a split point `k`, and the two sides must be **independent**. Picking the right operation to split on is the whole difficulty.

### 4.1 Burst balloons: choose the LAST one

Bursting balloon `k` earns `left · k · right`, where `left` and `right` are its **current** neighbours. Maximise the total.

Choosing the **first** balloon to burst doesn't split the problem: afterwards its two neighbours become adjacent, and the two sides interact. Choosing the **last** balloon `k` to burst inside the open interval `(l, r)` does: while everything else between `l` and `r` is burst, `k` is still standing and separates the two sides, and when `k` finally goes its neighbours are exactly `l` and `r`.

```java
static int maxCoins(int[] nums) {
    int n = nums.length;
    int[] v = new int[n + 2];                      // padded with a 1 at each end
    v[0] = v[n + 1] = 1;
    for (int i = 0; i < n; i++) v[i + 1] = nums[i];
    int[][] dp = new int[n + 2][n + 2];            // dp[l][r]: best for bursting everything strictly between l and r
    for (int len = 2; len <= n + 1; len++)         // len = r − l
        for (int l = 0; l + len <= n + 1; l++) {
            int r = l + len;
            for (int k = l + 1; k < r; k++)        // k is burst LAST in (l, r)
                dp[l][r] = Math.max(dp[l][r], dp[l][k] + dp[k][r] + v[l] * v[k] * v[r]);
        }
    return dp[0][n + 1];
}
```

![[Advanced DP - Burst Balloons Last.excalidraw|800]]

`[3, 1, 5, 8]` → `167`; `[1, 5]` → `10`. `O(n³)`.

### 4.2 Cutting a stick: choose the FIRST cut

A stick of length `n` must be cut at given positions; each cut costs the length of the piece being cut. Here the **first** cut in a piece is the natural split: it cuts the piece into two independent pieces, and it costs that piece's full length.

```java
static int minCostCut(int n, int[] cuts) {
    int m = cuts.length;
    int[] c = new int[m + 2];                      // 0, the cuts, n
    for (int i = 0; i < m; i++) c[i + 1] = cuts[i];
    c[m + 1] = n;
    Arrays.sort(c);                                // the input cuts may be in any order
    int[][] dp = new int[m + 2][m + 2];            // dp[i][j]: cheapest way to make every cut strictly between c[i] and c[j]
    for (int len = 2; len <= m + 1; len++)
        for (int i = 0; i + len <= m + 1; i++) {
            int j = i + len;
            dp[i][j] = Integer.MAX_VALUE;
            for (int k = i + 1; k < j; k++) dp[i][j] = Math.min(dp[i][j], dp[i][k] + dp[k][j]);
            dp[i][j] += c[j] - c[i];               // whichever cut is first, it cuts the whole piece
        }
    return dp[0][m + 1];
}
```

`(7, [1, 3, 4, 5])` → `16`; `(9, [5, 6, 1, 4, 2])` → `22`. The DP runs over **cut indices**, not positions on the stick, so it's `O(m³)` even when `n = 10⁹`.

### 4.3 Merging equal ends: strange printer

A printer prints a run of one character over any range, covering what was there. The fewest turns to print `s`? The character at `r` either gets its own turn, or is printed in the same turn as an earlier equal character `s[k]` (that turn covers `k..r`, and `k + 1..r − 1` is printed on top of it afterwards).

```java
static int strangePrinter(String s) {
    int n = s.length();
    int[][] dp = new int[n][n];                    // dp[i][j]: fewest turns to print s[i..j]
    for (int i = n - 1; i >= 0; i--) {
        dp[i][i] = 1;
        for (int j = i + 1; j < n; j++) {
            dp[i][j] = dp[i][j - 1] + 1;           // s[j] in a turn of its own
            for (int k = i; k < j; k++)
                if (s.charAt(k) == s.charAt(j))    // s[j] shares the turn that printed s[k]
                    dp[i][j] = Math.min(dp[i][j], dp[i][k] + (k + 1 <= j - 1 ? dp[k + 1][j - 1] : 0));
        }
    }
    return dp[0][n - 1];
}
```

`"aaabbb"` → `2`; `"aba"` → `2`; `"abcabc"` → `5`.

### 4.4 Two-player games on a row

Players alternately take a number from either end; both play optimally. Store the **difference** (current player minus opponent) for the subarray: whatever the player takes, the opponent then faces the rest and gets their own best difference there.

```java
static boolean predictTheWinner(int[] a) {
    int n = a.length;
    int[][] dp = new int[n][n];                    // dp[l][r]: (mover − other) under optimal play on a[l..r]
    for (int l = n - 1; l >= 0; l--) {
        dp[l][l] = a[l];
        for (int r = l + 1; r < n; r++)
            dp[l][r] = Math.max(a[l] - dp[l + 1][r], a[r] - dp[l][r - 1]);
    }
    return dp[0][n - 1] >= 0;                      // a tie counts as a win for player 1
}
```

`[1, 5, 2]` → `false`; `[1, 5, 233, 7]` → `true`. The "difference" trick avoids storing two scores per state; it's minimax in DP form ([[DSA/08 - Specialized Topics/03 - Game Theory|Game Theory]]).

| Problem | Split on | Note |
|---|---|---|
| Matrix chain | the last multiplication | [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems#8. Matrix-Chain Multiplication|Classic DP § 8]] |
| Burst balloons | the last balloon | §4.1 |
| Cut a stick | the first cut | §4.2 |
| Strange printer, remove boxes | merging with an equal character | §4.3 |
| Longest palindromic subsequence | matching ends | [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems#5.1 Relatives of LCS|Classic DP § 5.1]] |
| Optimal BST, merge stones | the root / last merge | Knuth optimisation (§7.5) |
| Stone game, predict the winner | the end taken | §4.4 |

---

## 5. Digit DP

"How many integers in `[L, R]` have property P?" with `R` up to `10¹⁸`. Count `f(N)` = how many in `[0, N]`, and answer `f(R) − f(L − 1)`. Build the number digit by digit from the left; the state is the position, whatever the property needs (a digit sum, a set of used digits, the previous digit), and a flag **tight**: whether every digit so far equals `N`'s digit, so that the next digit is limited by `N` instead of by 9.

![[Advanced DP - Digit DP Tight.excalidraw|800]]

```
count(pos, state, tight):
    if pos = number of digits: return 1 if state satisfies P else 0
    limit = tight ? N[pos] : 9
    total = Σ over d = 0..limit of count(pos + 1, update(state, d), tight and d = limit)
```

Only states with `tight = false` are memoized: there's exactly one tight path, so caching it gains nothing, and storing it in the same slot as the non-tight state would be wrong.

**Template: digit sum equal to `S`.**

```java
static long countDigitSum(long N, int S) {        // how many x in [0, N] have digit sum S
    if (N < 0) return 0;
    char[] d = Long.toString(N).toCharArray();
    long[][] memo = new long[d.length][S + 1];
    for (long[] row : memo) Arrays.fill(row, -1);
    return digitSumRec(d, 0, S, true, memo);
}

static long digitSumRec(char[] d, int pos, int left, boolean tight, long[][] memo) {
    if (left < 0) return 0;
    if (pos == d.length) return left == 0 ? 1 : 0;
    if (!tight && memo[pos][left] != -1) return memo[pos][left];
    int limit = tight ? d[pos] - '0' : 9;
    long count = 0;
    for (int dig = 0; dig <= limit; dig++)
        count += digitSumRec(d, pos + 1, left - dig, tight && dig == limit, memo);
    if (!tight) memo[pos][left] = count;
    return count;
}
```

`countDigitSum(100, 1)` → `3` (1, 10, 100); `countDigitSum(20, 2)` → `3` (2, 11, 20); two-digit numbers with digit sum 9: `countDigitSum(99, 9) − countDigitSum(9, 9)` → `9`. Numbers shorter than `N` are handled as numbers with leading zeros, which don't change a digit sum.

**Total count of digit 1 in `0..n`**: the state carries how many 1s have been written so far.

```java
static int countDigitOne(int n) {
    char[] d = Integer.toString(n).toCharArray();
    int[][] memo = new int[d.length][d.length + 1];
    for (int[] row : memo) Arrays.fill(row, -1);
    return onesRec(d, 0, 0, true, memo);
}

static int onesRec(char[] d, int pos, int ones, boolean tight, int[][] memo) {   // total 1s over all completions
    if (pos == d.length) return ones;
    if (!tight && memo[pos][ones] != -1) return memo[pos][ones];
    int limit = tight ? d[pos] - '0' : 9, total = 0;
    for (int dig = 0; dig <= limit; dig++)
        total += onesRec(d, pos + 1, ones + (dig == 1 ? 1 : 0), tight && dig == limit, memo);
    if (!tight) memo[pos][ones] = total;
    return total;
}
```

`13` → `6` (1, 10, 11 twice, 12, 13); `0` → `0`; `100` → `21`.

**Leading zeros matter** when the property looks at which digits appear. Numbers with at least one repeated digit in `1..n` = `n + 1 −` (numbers in `0..n` with all digits distinct). A flag **started** records whether a non-zero digit has appeared; zeros before it aren't digits of the number.

```java
static int numDupDigitsAtMostN(int n) {
    char[] d = Integer.toString(n).toCharArray();
    Integer[][] memo = new Integer[d.length][1 << 10];
    return n + 1 - distinctRec(d, 0, 0, true, false, memo);
}

static int distinctRec(char[] d, int pos, int mask, boolean tight, boolean started, Integer[][] memo) {
    if (pos == d.length) return 1;                 // one number (0, if nothing was started)
    if (!tight && started && memo[pos][mask] != null) return memo[pos][mask];
    int limit = tight ? d[pos] - '0' : 9, count = 0;
    for (int dig = 0; dig <= limit; dig++) {
        boolean nextTight = tight && dig == limit;
        if (!started && dig == 0) count += distinctRec(d, pos + 1, 0, nextTight, false, memo);   // still a leading zero
        else if ((mask >> dig & 1) == 0) count += distinctRec(d, pos + 1, mask | 1 << dig, nextTight, true, memo);
    }
    if (!tight && started) memo[pos][mask] = count;
    return count;
}
```

`20` → `1` (just 11); `100` → `10`; `1000` → `262`. Without `started`, `7` would be read as `007` and rejected for repeating 0.

---

## 6. Probability and Expected Value

The state holds a **probability** (or expected value) instead of a count or a cost; transitions multiply by the probability of each outcome and add. Everything else is the same.

**Knight probability**: a knight makes `k` uniformly random moves on an `n × n` board; what's the probability it never leaves the board?

```java
static double knightProbability(int n, int k, int row, int col) {
    int[][] moves = {{1,2},{2,1},{-1,2},{-2,1},{1,-2},{2,-1},{-1,-2},{-2,-1}};
    double[][] p = new double[n][n];               // p[r][c]: probability of being on (r, c), still on the board
    p[row][col] = 1;
    for (int step = 0; step < k; step++) {
        double[][] next = new double[n][n];
        for (int r = 0; r < n; r++)
            for (int c = 0; c < n; c++)
                if (p[r][c] > 0)
                    for (int[] m : moves) {
                        int nr = r + m[0], nc = c + m[1];
                        if (nr >= 0 && nr < n && nc >= 0 && nc < n) next[nr][nc] += p[r][c] / 8;   // off-board mass is lost
                    }
        p = next;
    }
    double total = 0;
    for (double[] line : p) for (double x : line) total += x;
    return total;
}
```

`(3, 2, 0, 0)` → `0.0625`; `(1, 0, 0, 0)` → `1.0`.

**New 21 game**: draw uniformly from `1..maxPts` while the total is below `k`; what's the probability of ending with at most `n`? `p[x] = (p[x−1] + … + p[x−maxPts]) / maxPts`, counting only predecessors that were still drawing (`< k`). The sum is a **sliding window** (§7.1), maintained in `O(1)` per step.

```java
static double new21Game(int n, int k, int maxPts) {
    if (k == 0 || n >= k - 1 + maxPts) return 1.0;   // the final total can't exceed n
    double[] p = new double[n + 1];                // p[x]: probability that the total is ever exactly x
    p[0] = 1;
    double window = 1, result = 0;                 // window: Σ p[y] over y in [x − maxPts, x − 1] with y < k
    for (int x = 1; x <= n; x++) {
        p[x] = window / maxPts;
        if (x < k) window += p[x]; else result += p[x];   // x ≥ k: the game stops here
        if (x - maxPts >= 0 && x - maxPts < k) window -= p[x - maxPts];
    }
    return result;
}
```

`(10, 1, 10)` → `1.0`; `(6, 1, 10)` → `0.6`; `(21, 17, 10)` → `0.73278` (rounded). Expected-value DPs (expected number of throws until …) have the same shape with `E[state] = 1 + Σ prob · E[next]`; when a state can lead back to itself, solve that one equation for `E` instead of recursing.

---

## 7. Optimising Transitions

Once the state is right, the remaining cost is the **transition**: `dp[i] = best over j of (…)`. If the candidates `j` have structure, the "best over `j`" can be maintained instead of recomputed.

| Transition shape | Technique | Cost |
|---|---|---|
| sum over a sliding range of `j` | prefix sums / running window | `O(1)` per state |
| max/min over the last `k` values of `dp[j]` | monotonic deque | `O(1)` amortized |
| `min over j of dp[j] + b(j)·a(i)` (linear in a value of `i`) | convex hull trick / Li Chao tree | `O(1)` amortized / `O(log n)` |
| `dp[k][i] = min over j < i of dp[k−1][j] + cost(j, i)`, optimal `j` monotone in `i` | divide and conquer optimisation | `O(k · n log n)` |
| interval DP with `opt[l][r−1] ≤ opt[l][r] ≤ opt[l+1][r]` | Knuth optimisation | `O(n²)` instead of `O(n³)` |

### 7.1 Prefix sums and running windows

When the transition **sums** `dp[j]` over a contiguous range of `j`, keep a running sum (as in new 21 game) or a prefix-sum array of `dp`. A transition summing over the last `maxPts` states drops from `O(maxPts)` to `O(1)`.

### 7.2 Monotonic deque: max over the last k states

**Constrained subsequence sum**: the largest sum of a non-empty subsequence in which consecutive chosen indices are at most `k` apart. `dp[i] = a[i] + max(0, max over i−k ≤ j < i of dp[j])`: the max over a sliding window of `dp`, which a monotonic deque provides ([[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]]).

```java
static int constrainedSubsetSum(int[] a, int k) {
    int n = a.length, best = Integer.MIN_VALUE;
    int[] dp = new int[n];                         // dp[i]: best valid subsequence ending at i
    ArrayDeque<Integer> dq = new ArrayDeque<>();   // indices in the window, dp values decreasing
    for (int i = 0; i < n; i++) {
        if (!dq.isEmpty() && dq.peekFirst() < i - k) dq.pollFirst();       // too far back
        dp[i] = a[i] + Math.max(0, dq.isEmpty() ? 0 : dp[dq.peekFirst()]);   // extend the best, or start at i
        while (!dq.isEmpty() && dp[dq.peekLast()] <= dp[i]) dq.pollLast();    // dominated: older and not larger
        dq.addLast(i);
        best = Math.max(best, dp[i]);
    }
    return best;
}
```

`([10, 2, -10, 5, 20], 2)` → `37`; `([-1, -2, -3], 1)` → `-1`; `([10, -2, -10, -5, 20], 2)` → `23`. `O(n)` instead of `O(n·k)`. "Jump game VI" (maximise the score of a path with jumps of at most `k`) is the same recurrence without the `max(0, …)`.

### 7.3 Convex hull trick

Transitions of the form `dp[i] = min over j < i of (dp[j] + cost(j, i))` where `cost` expands into a product of a value of `j` and a value of `i`. **Frog with squared jumps**: stones with heights `h` (strictly increasing), jumping from `j` to `i` costs `(h[i] − h[j])² + C`.

```
dp[i] = h[i]² + C + min over j < i of ( −2·h[j]·h[i] + dp[j] + h[j]² )
                                       slope m_j · x  +  intercept b_j      with x = h[i]
```

Each earlier stone `j` is a **line** `y = m_j·x + b_j`, and `dp[i]` needs the lowest line at `x = h[i]`. The lower envelope of lines is convex; lines that are never lowest can be discarded. Here slopes are added in decreasing order and queries come in increasing `x`, so a deque with pointer advances suffices.

```java
static long frog3(long[] h, long C) {              // h strictly increasing
    int n = h.length;
    long[] dp = new long[n];
    long[] M = new long[n], B = new long[n];       // lines y = M·x + B on the lower envelope, a deque [head, tail)
    int head = 0, tail = 0;
    M[tail] = -2 * h[0]; B[tail] = h[0] * h[0]; tail++;    // stone 0, dp[0] = 0
    for (int i = 1; i < n; i++) {
        long x = h[i];
        while (tail - head >= 2 && M[head + 1] * x + B[head + 1] <= M[head] * x + B[head]) head++;   // x only grows
        dp[i] = M[head] * x + B[head] + x * x + C;
        long m = -2 * h[i], b = dp[i] + h[i] * h[i];
        while (tail - head >= 2 && uselessMiddle(M[tail - 2], B[tail - 2], M[tail - 1], B[tail - 1], m, b)) tail--;
        M[tail] = m; B[tail] = b; tail++;
    }
    return dp[n - 1];
}

static boolean uselessMiddle(long m1, long b1, long m2, long b2, long m3, long b3) {
    // slopes m1 > m2 > m3: line 2 is never lowest if line 3 overtakes line 1 no later than line 2 does
    return (double) (b3 - b1) * (m1 - m2) <= (double) (b2 - b1) * (m1 - m3);
}
```

`h = [1, 2, 3, 4, 5]`, `C = 6` → `20`; `h = [500000, 1000000]`, `C = 10¹²` → `1250000000000`; `h = [1, 3, 4, 5, 10, 11, 12, 13]`, `C = 5` → `62`. `O(n)` instead of `O(n²)`. The intersection test multiplies values that can exceed `2⁶³`, hence the `double` (exact `BigInteger` or `Math.multiplyHigh` comparisons avoid rounding when values are adversarial).

> [!warning] The monotone deque needs monotone input
> The deque version requires slopes inserted in sorted order **and** queries in sorted order. If queries come in any order, binary-search the envelope (`O(log n)`); if slopes are unsorted, use a **Li Chao tree** (a segment tree over `x` storing one line per node, `O(log C)` per insert and query).

### 7.4 Divide and conquer optimisation

Layered DPs `dp[g][i] = min over j < i of dp[g−1][j] + cost(j, i)` cost `O(k · n²)`. If the optimal `j` for `i`, `opt(i)`, is **non-decreasing in `i`** (true when `cost` satisfies the quadrangle inequality, e.g. squares of segment sums with non-negative elements), compute the middle `i` of a range by brute force over its allowed `j`, then recurse: the left half only needs `j ≤ opt(mid)`, the right half only `j ≥ opt(mid)`. Each recursion level scans `O(n)` candidates in total, so a layer costs `O(n log n)`.

**Split an array of non-negative numbers into `k` contiguous groups, minimising the sum of the squared group sums:**

```java
static long minSquaredGroupSums(int[] a, int k) { // a[i] ≥ 0, 1 ≤ k ≤ n, groups non-empty
    int n = a.length;
    long[] P = new long[n + 1];
    for (int i = 0; i < n; i++) P[i + 1] = P[i] + a[i];
    long[] prev = new long[n + 1], cur = new long[n + 1];
    Arrays.fill(prev, Long.MAX_VALUE);
    prev[0] = 0;                                   // zero groups cover zero elements
    for (int g = 1; g <= k; g++) {
        Arrays.fill(cur, Long.MAX_VALUE);
        layer(1, n, 0, n - 1, P, prev, cur);
        long[] t = prev; prev = cur; cur = t;
    }
    return prev[n];
}

// cur[i] for i in [lo, hi], knowing the optimal j lies in [optLo, optHi]
static void layer(int lo, int hi, int optLo, int optHi, long[] P, long[] prev, long[] cur) {
    if (lo > hi) return;
    int mid = (lo + hi) >>> 1, bestJ = optLo;
    for (int j = optLo; j <= Math.min(mid - 1, optHi); j++) {
        if (prev[j] == Long.MAX_VALUE) continue;   // j elements can't form g − 1 groups
        long s = P[mid] - P[j], v = prev[j] + s * s;
        if (v < cur[mid]) { cur[mid] = v; bestJ = j; }
    }
    layer(lo, mid - 1, optLo, bestJ, P, prev, cur);
    layer(mid + 1, hi, bestJ, optHi, P, prev, cur);
}
```

`([1, 2, 3, 4], 2)` → `52` (`[1, 2, 3] | [4]`: `36 + 16`); `([1, 1, 1, 1], 4)` → `4`; `([5], 1)` → `25`. `O(k · n log n)`.

### 7.5 Knuth optimisation (interval DP)

For interval DPs `dp[l][r] = min over l ≤ k < r of dp[l][k] + dp[k+1][r] + w(l, r)` where `w` satisfies the quadrangle inequality and is monotone on nested intervals (merging adjacent piles with cost = total size, optimal BST), the optimal split satisfies `opt[l][r−1] ≤ opt[l][r] ≤ opt[l+1][r]`. Restricting `k` to that range makes the total work telescope to `O(n²)`. Matrix chain does **not** satisfy the condition in general; it needs the `O(n³)` DP (or Hu–Shing's `O(n log n)` algorithm).

---

## 8. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Bitmask DP with `n = 25` | `2²⁵ · 25` states: out of memory/time | check `n ≤ 20`; meet in the middle for subset sums |
| TSP looping over masks without city 0 | wasted work or wrong starts | start state `dp[1][0] = 0`; only odd masks |
| `1 << n` with `n ≥ 31` | overflow | `1L << n`, though such sizes are infeasible anyway |
| Submask loop `sub >= 0` | infinite loop (`(0 − 1) & mask = mask`) | `sub > 0`, handle `0` separately |
| Groups counted once per order in partition DPs | slower, and wrong for **counting** partitions | force the group to contain the lowest element |
| Tree DP recursing on a `10⁵`-node path | `StackOverflowError` | BFS order, processed backwards |
| Rerooting with an `O(n)` recomputation per root | `O(n²)` | move the root across one edge with a formula |
| Burst balloons choosing the **first** balloon | sides not independent, wrong answers | the **last** balloon in `(l, r)` |
| Cutting a stick without sorting the cuts | wrong piece lengths | sort, and add `0` and `n` |
| Interval DP filled row by row from the top | reads unfinished intervals | by length, or `l` decreasing |
| Digit DP memoizing tight states in the same slot | wrong counts | memoize only `tight = false` |
| Digit DP ignoring leading zeros | `7` read as `007` | a `started` flag |
| `f(R) − f(L)` instead of `f(R) − f(L − 1)` | `L` itself excluded | subtract `f(L − 1)` |
| New 21 game window including totals `≥ k` | probabilities too large | only states still drawing feed the window |
| Monotonic deque storing values instead of indices | can't evict out-of-range entries | store indices |
| CHT with unsorted slopes or queries | wrong minimum | binary search the hull, or a Li Chao tree |
| CHT intersection test in `long` | overflow | `double` or exact 128-bit comparison |
| D&C optimisation on a cost without monotone `opt` | wrong answers | verify the quadrangle inequality, or compare with the `O(k n²)` DP on small inputs |

---

## 9. Trick Questions and Special Cases

> [!question]- Why does iterating masks in increasing numeric order give a valid DP order?
> Adding an element sets a bit, which strictly increases the number. So every subset of a mask is numerically smaller and has been processed already.

> [!question]- What's the total cost of "for every mask, enumerate its submasks"?
> `3ⁿ`, not `4ⁿ`: each element is either outside the mask, inside the mask but not the submask, or inside both. For `n = 15`, `3¹⁵ ≈ 1.4·10⁷`; for `n = 20`, `3.5·10⁹` is too slow, which is when SOS DP (`n · 2ⁿ`) matters.

> [!question]- `tsp` with one city?
> `0`: there's nothing to visit. The general code would look for `v ≥ 1` and find none, hence the special case.

> [!question]- House robber III: is "rob every other level" optimal?
> No. `[2, 1, 3, null, 4]` → `7` (rob 3 and 4, which are on levels 1 and 2), while level sums 2, 4, 4 give at most 6 by alternating levels. The pair DP decides per node, not per level.

> [!question]- `minCameraCover` on a single node and on a path of 4 nodes?
> `1` and `2`. On a path `a – b – c – d` (as a chain of left children), cameras go on `c` (covering `b`, `c`, `d`) and then `a` is left unwatched, so a second camera goes on `a` (or `b`).

> [!question]- Burst balloons on `[5]` and on `[]`?
> `5` (`1 · 5 · 1`, the padding counts as neighbours) and `0`.

> [!question]- Why does burst balloons need the LAST balloon, while cutting a stick uses the FIRST cut?
> In both, the chosen operation must split the interval into two parts that don't interact. A cut, once made, separates the stick for good, so the first cut splits. A burst **joins** its two neighbours, so the sides interact after it; only the balloon that's still standing at the end keeps them apart throughout.

> [!question]- `predictTheWinner([1, 1])`?
> `true`. Both players get 1; a tie counts as a win for player 1. Changing `>= 0` to `> 0` breaks it.

> [!question]- `countDigitSum(0, 0)` and `countDigitSum(9, 0)`?
> Both `1`: the number 0 has digit sum 0. Ranges starting at 1 must subtract it: `f(R) − f(0)`.

> [!question]- `numDupDigitsAtMostN(10)` and `(11)`?
> `0` and `1`. 10 has distinct digits; 11 is the first with a repeat. Note `0` is counted by `distinctRec` and also by `n + 1`, so it cancels.

> [!question]- In the digit DP, why not memoize tight states too?
> Correctness: a tight state's set of completions depends on the remaining digits of `N`, a non-tight state's doesn't; sharing a slot mixes the two. Efficiency: there is only one tight path, so memoizing it saves nothing. (Adding `tight` as a third memo dimension is also correct.)

> [!question]- `new21Game(0, 0, 1)`?
> `1.0`: with `k = 0` no card is ever drawn and the total 0 is at most `n = 0`.

> [!question]- `constrainedSubsetSum([-5, -1, -3], 2)`?
> `-1`. The subsequence must be non-empty, so with all values negative the answer is the largest single element; the `max(0, …)` lets each `dp[i]` start fresh.

> [!question]- `minSquaredGroupSums([1, 2, 3, 4], 2)`: which split wins?
> `[1, 2, 3] | [4]`: `6² + 4² = 52`. The other splits give `1 + 81 = 82` and `9 + 49 = 58`. Squares punish large groups, so the groups' sums are pushed towards equal (`6` and `4` is as close as contiguous splits allow).

> [!question]- Domino tilings of `3 × 3`, `1 × 2`, and `2 × 1`?
> `0` (odd area), `1`, `1`.

---

## 10. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `tsp(4-city example)` | `80` | `O(2ⁿ n²)` |
| `minCostAssignment(4×4 example)` | `13` | popcount = next person |
| `shortestPathLength([[1,2,3],[0],[0],[0]])` | `4` | BFS over (node, mask) |
| `dominoTilings(8, 8)` | `12988816` | profile DP |
| Submask pairs over all masks | `3ⁿ` | |
| `minSessions([3,1,3,1,1], 8)` | `2` | groups with the lowest task |
| `countSubmaskElements([1,3,2,7], 3)` | `[1, 3, 1, 4]` | SOS |
| `robTree([2,1,3,null,4])` | `7` | not level alternation |
| `minCameraCover([0,0,null,0,0])` | `1` | three states |
| `treeDiameter(6, …)` | `4` | iterative post-order |
| `sumOfDistancesInTree(6, …)` | `[8,12,6,10,10,10]` | rerooting |
| `maxCoins([3,1,5,8])` | `167` | last balloon |
| `minCostCut(7, [1,3,4,5])` | `16` | first cut, sorted cuts |
| `strangePrinter("aba")` | `2` | merge equal ends |
| `predictTheWinner([1,5,233,7])` | `true` | difference DP |
| `countDigitOne(13)` | `6` | |
| `numDupDigitsAtMostN(1000)` | `262` | `started` flag |
| `knightProbability(3, 2, 0, 0)` | `0.0625` | |
| `new21Game(21, 17, 10)` | `≈ 0.73278` | sliding window |
| `constrainedSubsetSum([10,2,-10,5,20], 2)` | `37` | monotonic deque |
| `frog3([1,3,4,5,10,11,12,13], 5)` | `62` | convex hull trick |
| `minSquaredGroupSums([1,2,3,4], 2)` | `52` | D&C optimisation |

---

## 11. Summary

- **Bitmask DP** stores a set as an integer: TSP `dp[mask][v]`, assignment `dp[mask]` (popcount is the next person), BFS over `(node, mask)`, partition by `sum mod target`, profile DP for tilings. Feasible to `n ≈ 20`.
- **Subsets**: submask enumeration is `3ⁿ` in total (fix the group containing the lowest element); **SOS** sums over all submasks in `n·2ⁿ`.
- **Tree DP** returns a small tuple per subtree (rob / skip, camera states); process a BFS order backwards to avoid deep recursion; **rerooting** gets every root's answer in two passes.
- **Interval DP** by length; split on the operation that separates the sides: the **last** balloon, the **first** cut, a merge with an equal end; game DPs store the score difference.
- **Digit DP**: position + property state + `tight` (+ `started` for leading zeros); memoize non-tight states; ranges as `f(R) − f(L−1)`.
- **Probability DP** propagates probability mass; expected values add 1 per step.
- **Transition optimisations**: running sums, monotonic deque, convex hull trick (lines and a lower envelope), divide-and-conquer (monotone `opt`), Knuth (interval DP with monotone splits).

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]] · Next: [[DSA/06 - Algorithm Design Paradigms/07 - Meet in the Middle|Meet in the Middle]]
- [[DSA/06 - Algorithm Design Paradigms/04 - Dynamic Programming Fundamentals|Dynamic Programming — Fundamentals]]: states, transitions, evaluation order
- [[DSA/01 - Foundations/03 - Bit Manipulation|Bit Manipulation]]: masks, submask enumeration, popcount
- [[DSA/04 - Trees and Hierarchical Structures/01 - Binary Trees|Binary Trees]]: what a recursive call on a subtree returns
- [[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]]: the monotonic deque
- [[DSA/06 - Algorithm Design Paradigms/03 - Backtracking|Backtracking]]: when the state can't be compressed
- [[DSA/08 - Specialized Topics/03 - Game Theory|Game Theory]]: minimax and game DPs
- [[DSA/08 - Specialized Topics/02 - Computational Geometry|Computational Geometry]]: convex hulls of points (the CHT's geometric cousin)
