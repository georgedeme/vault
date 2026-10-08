# Dynamic Programming — Fundamentals

<span class="hl-blue">Dynamic programming</span> (DP) solves a problem by combining the answers to smaller subproblems, where the same subproblems recur many times, and storing each answer so it's computed only once. It turns exponential recursions into polynomial algorithms. The difficulty is almost never the code, which is usually a loop over a table; it's choosing **what the subproblems are**. Once the state and the recurrence are right, the rest is mechanical.

This note is about that method rather than a catalogue of problems: when DP applies, the path from brute-force recursion to memoization to a table to `O(1)` space, a recipe for designing states and transitions, evaluation order, space optimisation and its traps, reconstructing the actual solution, and the view of DP as a shortest path in a DAG. The standard problems (knapsack, LIS, LCS, edit distance, …) are in [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]], and bitmask, tree, interval and digit DP in [[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]].

## Contents

- [[#1. When DP Applies|1. When DP Applies]]
- [[#2. From Recursion to DP: One Problem, Four Versions|2. From Recursion to DP: One Problem, Four Versions]]
- [[#3. Memoization vs. Tabulation|3. Memoization vs. Tabulation]]
- [[#4. The Recipe|4. The Recipe]]
- [[#5. Designing the State|5. Designing the State]]
- [[#6. Deriving the Transition|6. Deriving the Transition]]
- [[#7. Evaluation Order|7. Evaluation Order]]
- [[#8. Space Optimisation|8. Space Optimisation]]
- [[#9. Reconstructing the Solution|9. Reconstructing the Solution]]
- [[#10. Complexity and DP as Paths in a DAG|10. Complexity and DP as Paths in a DAG]]
- [[#11. Recognising DP Problems|11. Recognising DP Problems]]
- [[#12. Common Mistakes|12. Common Mistakes]]
- [[#13. Trick Questions and Special Cases|13. Trick Questions and Special Cases]]
- [[#14. Quick Reference — Non-Obvious Outcomes|14. Quick Reference — Non-Obvious Outcomes]]
- [[#15. Summary|15. Summary]]

---

## 1. When DP Applies

> [!note] The two properties
> - <span class="hl-blue">Optimal substructure</span>: an optimal (or complete) answer for the whole problem is built from optimal answers to subproblems. For counting problems, the count for the whole is a sum or product of counts for parts.
> - <span class="hl-blue">Overlapping subproblems</span>: a plain recursion would solve the same subproblem many times. That's what caching saves.

Without overlap, the recursion is already efficient and it's [[DSA/06 - Algorithm Design Paradigms/02 - Divide and Conquer|divide and conquer]]. Without optimal substructure, the subproblem answers can't be combined at all. Longest **simple** path in a general graph is the standard example: the longest path from `a` to `c` through `b` isn't made of longest paths `a → b` and `b → c`, because those two might share vertices.

| | Greedy | Divide and conquer | Dynamic programming |
|---|---|---|---|
| Subproblems | one, chosen greedily | independent | overlapping |
| Choices tried per step | one | none (fixed split) | all |
| Correctness | needs a proof | follows from the split | follows from the recurrence |

DP answers three kinds of question, and the combining operation follows from the kind:

| Question | Combine with | Base value of "nothing" | Example |
|---|---|---|---|
| How many ways? | `+` (and `×` for independent parts) | `1` way to do nothing | climbing stairs, decode ways |
| Best value? | `min` / `max` | `0` cost, or `±∞` for impossible | house robber, coin change |
| Is it possible? | `OR` | `true` for the empty case | word break, subset sum |

---

## 2. From Recursion to DP: One Problem, Four Versions

**House robber**: houses in a row hold `a[i]` money; robbing two adjacent houses triggers an alarm. Maximise the total.

**1. Brute-force recursion.** For house `i`: skip it, or rob it and skip the next one.

```java
static int robNaive(int[] a, int i) {             // best from houses i..n−1
    if (i >= a.length) return 0;
    return Math.max(robNaive(a, i + 1), a[i] + robNaive(a, i + 2));
}
```

The call tree branches twice per level and has Fibonacci-like size, `O(φⁿ)`. But there are only `n + 1` different arguments `i`: everything else is repetition.

**2. Memoization (top-down).** Same recursion, but cache each answer.

```java
static int robMemo(int[] a) {
    int[] memo = new int[a.length];
    Arrays.fill(memo, -1);                         // −1 = "not computed"; 0 is a valid answer
    return robFrom(a, 0, memo);
}

static int robFrom(int[] a, int i, int[] memo) {
    if (i >= a.length) return 0;
    if (memo[i] != -1) return memo[i];
    return memo[i] = Math.max(robFrom(a, i + 1, memo), a[i] + robFrom(a, i + 2, memo));
}
```

**3. Tabulation (bottom-up).** Fill a table in an order where every dependency is ready. Here `dp[i]` is the best using the first `i` houses (a prefix instead of a suffix; either direction works):

```
dp[0] = 0
dp[1] = a[0]
dp[i] = max(dp[i−1], dp[i−2] + a[i−1])        -- skip house i−1, or rob it
```

```java
static int robTab(int[] a) {
    int n = a.length;
    int[] dp = new int[n + 1];                     // dp[i]: best using the first i houses
    for (int i = 1; i <= n; i++)
        dp[i] = Math.max(dp[i - 1], a[i - 1] + (i >= 2 ? dp[i - 2] : 0));
    return dp[n];
}
```

**4. Space-optimised.** `dp[i]` only needs the previous two entries.

```java
static int rob(int[] a) {
    int prev2 = 0, prev1 = 0;                      // dp[i−2], dp[i−1]
    for (int x : a) {
        int cur = Math.max(prev1, prev2 + x);
        prev2 = prev1;
        prev1 = cur;
    }
    return prev1;
}
```

`[1, 2, 3, 1]` → `4`; `[2, 7, 9, 3, 1]` → `12` (houses 0, 2, 4); `[2, 1, 1, 2]` → `4` (houses 0 and 3). The last example is why "take every other house" isn't enough: neither the even nor the odd positions are optimal.

> [!tip] The progression is the method
> Write the brute-force recursion first, with the state as its parameters. If the parameters can repeat, memoize. If recursion depth or speed is a problem, turn it into a table. If each row only reads the previous one or two, keep only those. Each step is mechanical once the first one is right.

---

## 3. Memoization vs. Tabulation

| | Memoization (top-down) | Tabulation (bottom-up) |
|---|---|---|
| Written as | the recursion plus a cache | loops over a table |
| Evaluation order | automatic (recursion follows dependencies) | must be chosen so dependencies come first |
| States computed | only the reachable ones | all of them |
| Recursion depth | up to the longest dependency chain: can overflow the stack | none |
| Constant factor | higher (calls, cache checks) | lower |
| Space optimisation | hard | natural (rolling arrays) |
| Easiest when | the order is awkward or few states are reachable | the order is obvious |

> [!warning] Memoization pitfalls in Java
> - **The "not computed" marker must not be a valid answer.** `0` as a marker silently recomputes every state whose answer is 0. Use `-1` (if answers are non-negative), a separate `boolean[]`, or an `Integer[]`/`Long[]` with `null`.
> - **`Arrays.fill` on a 2D array** doesn't compile for `int[][]` with an `int` value; fill each row: `for (int[] row : memo) Arrays.fill(row, -1);`.
> - **Deep recursion**: `robMemo` on 100,000 houses recurses 100,000 deep and throws `StackOverflowError` ([[DSA/01 - Foundations/02 - Recursion#9. Stack Overflow Limits in Java|Recursion § 9]]). Tabulate, or run the recursion in a thread with a big stack.
> - **`HashMap` memo with `String` keys** like `i + "," + j` is correct but slow (string building and hashing per lookup). Prefer arrays; if a map is needed, encode the state in a `long` (`(long) i << 32 | j`).
> - **Static memo arrays across test cases**: reset or reallocate them per input.

A 2D example of both styles, **minimum path sum** (move only right or down):

```java
static int minPathSumMemo(int[][] g) {
    int[][] memo = new int[g.length][g[0].length];
    for (int[] row : memo) Arrays.fill(row, -1);
    return mps(g, g.length - 1, g[0].length - 1, memo);
}

static int mps(int[][] g, int r, int c, int[][] memo) {   // cheapest path from (0,0) to (r,c)
    if (r == 0 && c == 0) return g[0][0];
    if (memo[r][c] != -1) return memo[r][c];
    int best = Integer.MAX_VALUE;
    if (r > 0) best = Math.min(best, mps(g, r - 1, c, memo));
    if (c > 0) best = Math.min(best, mps(g, r, c - 1, memo));
    return memo[r][c] = best + g[r][c];            // best is finite: at least one neighbour exists
}

static int minPathSum(int[][] g) {
    int m = g.length, n = g[0].length;
    int[][] dp = new int[m][n];
    for (int r = 0; r < m; r++)
        for (int c = 0; c < n; c++) {
            if (r == 0 && c == 0) dp[r][c] = g[0][0];
            else if (r == 0) dp[r][c] = dp[r][c - 1] + g[r][c];      // first row: only from the left
            else if (c == 0) dp[r][c] = dp[r - 1][c] + g[r][c];      // first column: only from above
            else dp[r][c] = Math.min(dp[r - 1][c], dp[r][c - 1]) + g[r][c];
        }
    return dp[m - 1][n - 1];
}
```

`[[1, 3, 1], [1, 5, 1], [4, 2, 1]]` → `7`.

---

## 4. The Recipe

> [!important] Five decisions
> 1. **State**: what does `dp[...]` mean, in one precise sentence? ("`dp[i]` = the number of ways to decode the first `i` characters.")
> 2. **Transition**: how is a state computed from smaller ones? Think about the **last** decision.
> 3. **Base cases**: the smallest states, whose answers are known directly. Check that they make the transition correct for the first real state.
> 4. **Order**: an evaluation order in which every state's dependencies are already computed.
> 5. **Answer**: which state (or combination of states) is the final answer?

**Worked example: decode ways.** A string of digits encodes letters as `1 → A, …, 26 → Z`. Count the decodings.

1. **State**: `dp[i]` = number of ways to decode the first `i` characters.
2. **Transition** (the last piece is one digit or two):
   - if `s[i−1]` is `1–9`, the last piece can be that digit alone: add `dp[i−1]`;
   - if `s[i−2..i−1]` is `10–26`, the last piece can be those two digits: add `dp[i−2]`.
3. **Base**: `dp[0] = 1` (the empty prefix has one decoding, the empty one). This is what makes `"12"` count `"12" → L` as one way.
4. **Order**: increasing `i`.
5. **Answer**: `dp[n]`.

```java
static int numDecodings(String s) {
    int n = s.length();
    int[] dp = new int[n + 1];                     // dp[i]: decodings of the first i characters
    dp[0] = 1;
    for (int i = 1; i <= n; i++) {
        if (s.charAt(i - 1) != '0') dp[i] += dp[i - 1];                        // last piece: one digit 1–9
        if (i >= 2) {
            int two = (s.charAt(i - 2) - '0') * 10 + (s.charAt(i - 1) - '0');
            if (two >= 10 && two <= 26) dp[i] += dp[i - 2];                    // last piece: 10–26
        }
    }
    return dp[n];
}
```

`"12"` → `2`; `"226"` → `3`; `"06"` → `0` (`"06"` isn't `6`); `"10"` → `1`; `"100"` → `0`; `"11106"` → `2`. The `0` cases are the whole difficulty: a `0` can only be the second digit of `10` or `20`, and `two >= 10` excludes leading-zero pairs like `"06"`.

---

## 5. Designing the State

### 5.1 The state must summarise everything the future needs

A good state contains exactly the information about the past that affects what can still happen. If two partial solutions with the same state could have different best futures, the state is missing something; if the state distinguishes partial solutions whose futures are identical, it's bigger than it needs to be.

**Paint house**: `n` houses, three colours, `cost[i][c]` to paint house `i` colour `c`, and adjacent houses must differ. "Best cost for the first `i` houses" isn't enough: the next house's options depend on the colour of house `i`. Add it to the state: `dp[i][c]` = best cost for houses `0..i` with house `i` coloured `c`.

```java
static int minCostPaint(int[][] cost) {
    int r = 0, g = 0, b = 0;                       // best totals with the previous house red / green / blue
    for (int[] c : cost) {
        int nr = c[0] + Math.min(g, b);
        int ng = c[1] + Math.min(r, b);
        int nb = c[2] + Math.min(r, g);
        r = nr; g = ng; b = nb;                    // all three use the OLD values: compute first, then assign
    }
    return Math.min(r, Math.min(g, b));
}
```

`[[17, 2, 17], [16, 16, 5], [14, 3, 19]]` → `10` (`2 + 5 + 3`).

**House robber II** (houses in a circle, so the first and last are adjacent): the state "first `i` houses" can't see whether house 0 was robbed. Rather than adding that to the state, split into two linear problems: houses `0..n−2` and houses `1..n−1`.

```java
static int robCircular(int[] a) {
    if (a.length == 1) return a[0];                // both ranges below would be empty
    return Math.max(robRange(a, 0, a.length - 2), robRange(a, 1, a.length - 1));
}

static int robRange(int[] a, int lo, int hi) {    // house robber on a[lo..hi]
    int prev2 = 0, prev1 = 0;
    for (int i = lo; i <= hi; i++) {
        int cur = Math.max(prev1, prev2 + a[i]);
        prev2 = prev1;
        prev1 = cur;
    }
    return prev1;
}
```

`[2, 3, 2]` → `3`; `[1, 2, 3, 1]` → `4`; `[1]` → `1`.

### 5.2 State machines

When the past matters only through a small "mode" (holding a stock or not, in a cooldown or not), make the mode part of the state and write one transition per arrow of the machine.

**Stock with cooldown** (unlimited trades, but after selling you must wait a day before buying):

![[DP - Stock Cooldown State Machine.excalidraw|800]]

```java
static int maxProfitCooldown(int[] prices) {
    int hold = Integer.MIN_VALUE / 2, sold = Integer.MIN_VALUE / 2, rest = 0;   // −∞ for unreachable states
    for (int p : prices) {
        int newHold = Math.max(hold, rest - p);    // keep holding, or buy (only from rest)
        int newSold = hold + p;                    // sell today
        int newRest = Math.max(rest, sold);        // idle; yesterday's sale finishes its cooldown
        hold = newHold; sold = newSold; rest = newRest;
    }
    return Math.max(sold, rest);
}
```

`[1, 2, 3, 0, 2]` → `3` (buy 1, sell 2, cooldown, buy 0, sell 2); `[1]` → `0`. `Integer.MIN_VALUE / 2` stands for "impossible" while leaving room to add a price without overflowing.

**With a transaction fee** (pay `fee` per completed trade, no cooldown): two states.

```java
static int maxProfitFee(int[] prices, int fee) {
    int hold = -prices[0], cash = 0;               // day 0: bought, or did nothing
    for (int i = 1; i < prices.length; i++) {
        cash = Math.max(cash, hold + prices[i] - fee);
        hold = Math.max(hold, cash - prices[i]);   // uses the NEW cash: see the trick question
    }
    return cash;
}
```

`([1, 3, 2, 8, 4, 9], 2)` → `8`; `([1, 3, 7, 5, 10, 3], 3)` → `6`.

**At most `k` transactions**: the mode is "how many buys/sells so far" and whether a stock is held.

```java
static int maxProfitK(int k, int[] prices) {
    int[] buy = new int[k + 1], sell = new int[k + 1];   // best balance after the j-th buy / j-th sell
    Arrays.fill(buy, Integer.MIN_VALUE / 2);
    for (int p : prices)
        for (int j = 1; j <= k; j++) {
            buy[j] = Math.max(buy[j], sell[j - 1] - p);
            sell[j] = Math.max(sell[j], buy[j] + p);
        }
    return sell[k];
}
```

`(2, [3, 2, 6, 5, 0, 3])` → `7`; `(2, [3, 3, 5, 0, 0, 3, 1, 4])` → `6`; `(2, [2, 4, 1])` → `2`. With `k ≥ n/2`, the limit can never bind (a trade needs two days), so the answer is the unlimited version: the sum of all rises ([[DSA/06 - Algorithm Design Paradigms/01 - Greedy Algorithms#8.9 More one-liners worth knowing|Greedy § 8.9]]). Checking that first avoids allocating arrays for a `k` of a billion.

### 5.3 Common state shapes

| State | Meaning | Typical problems | Note |
|---|---|---|---|
| `dp[i]` | prefix of length `i` (or suffix from `i`) | house robber, decode ways, word break, LIS | this note, [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP]] |
| `dp[i][j]` over two sequences | prefixes of both | LCS, edit distance | [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP]] |
| `dp[r][c]` | grid cell | unique paths, min path sum | this note |
| `dp[i][w]` | first `i` items, capacity `w` | knapsack, subset sum | [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP]] |
| `dp[l][r]` | interval `l..r` | matrix chain, burst balloons | [[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]] |
| `dp[mask]` / `dp[mask][v]` | a set of chosen items | TSP, assignment | [[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]] |
| `dp[node][…]` | subtree | house robber III, tree diameter | [[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]] |
| `dp[pos][tight][…]` | digit position | count numbers with a digit property | [[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]] |
| `dp[i][mode]` | prefix plus a small mode | stock problems, paint house | this note |

---

## 6. Deriving the Transition

### 6.1 Think about the last step

Most transitions come from asking: **what was the last decision** in an optimal (or any) solution for this state? Each possibility leaves a smaller state, and the answer combines them.

| Problem | Last decision | Transition |
|---|---|---|
| Climbing stairs (1 or 2 steps) | the last step was 1 or 2 | `dp[i] = dp[i−1] + dp[i−2]` |
| House robber | was the last house robbed? | `max(dp[i−1], dp[i−2] + a[i−1])` |
| Decode ways | last piece has 1 or 2 digits | sum of the valid cases |
| Perfect squares | the last square used is `s²` | `min over s of dp[i − s²] + 1` |
| Word break | the last word is `s[j..i)` | `OR over j of dp[j] ∧ dict(s[j..i))` |

```java
static int climbStairs(int n) {
    int a = 1, b = 1;                              // ways to reach steps i−2 and i−1 (step 0: one way)
    for (int i = 2; i <= n; i++) { int c = a + b; a = b; b = c; }
    return b;
}

static int numSquares(int n) {                    // fewest perfect squares summing to n
    int[] dp = new int[n + 1];
    Arrays.fill(dp, Integer.MAX_VALUE);
    dp[0] = 0;
    for (int i = 1; i <= n; i++)
        for (int s = 1; s * s <= i; s++)
            dp[i] = Math.min(dp[i], dp[i - s * s] + 1);   // safe: dp[i − s²] is always finite (1 is a square)
    return dp[n];
}

static boolean wordBreak(String s, List<String> dict) {
    Set<String> words = new HashSet<>(dict);
    int maxLen = 0;
    for (String w : dict) maxLen = Math.max(maxLen, w.length());
    boolean[] dp = new boolean[s.length() + 1];   // dp[i]: s[0..i) can be split into words
    dp[0] = true;
    for (int i = 1; i <= s.length(); i++)
        for (int j = Math.max(0, i - maxLen); j < i && !dp[i]; j++)   // the last word is s[j..i)
            dp[i] = dp[j] && words.contains(s.substring(j, i));
    return dp[s.length()];
}
```

`climbStairs(5)` → `8`, `climbStairs(45)` → `1836311903` (the largest that fits in an `int`). `numSquares(12)` → `3` (`4 + 4 + 4`), `numSquares(13)` → `2` (`4 + 9`); greedy (largest square first) gives `9 + 1 + 1 + 1` for 12. `wordBreak("leetcode", [leet, code])` → `true`; `("applepenapple", [apple, pen])` → `true` (words can repeat); `("catsandog", [cats, dog, sand, and, cat])` → `false`.

### 6.2 Counting: disjoint, exhaustive cases

A counting transition is correct when the cases it adds are **disjoint** (no solution counted twice) and **exhaustive** (every solution counted once). Splitting by "the last decision" gives both automatically, as long as each solution has exactly one last decision. Double counting appears when the cases are defined by something a solution can have twice, such as "contains a 2" instead of "ends with a 2".

Counts grow exponentially, so problems ask for them modulo `10⁹ + 7`. Reduce after **every** addition; with `int`s, adding two values below the modulus stays below `2³¹`, but multiplying needs `long` ([[DSA/01 - Foundations/04 - Math for Algorithms#3. Modular Arithmetic|Math § 3]]).

```java
static int numRollsToTarget(int n, int k, int target) {   // n dice with faces 1..k summing to target
    final int MOD = 1_000_000_007;
    int[] dp = new int[target + 1];                // dp[t]: ways for the dice so far to sum to t
    dp[0] = 1;
    for (int d = 1; d <= n; d++) {
        int[] next = new int[target + 1];          // a fresh row: each die must be used exactly once
        for (int t = 1; t <= target; t++)
            for (int f = 1; f <= k && f <= t; f++)
                next[t] = (next[t] + dp[t - f]) % MOD;
        dp = next;
    }
    return dp[target];
}
```

`(1, 6, 3)` → `1`; `(2, 6, 7)` → `6`; `(30, 30, 500)` → `222616187`.

### 6.3 Optimisation: identities and "impossible"

`min` needs a starting value larger than any real answer, and some states are **unreachable** (no valid solution). Both are usually represented by an `INF`.

> [!warning] `Integer.MAX_VALUE` as infinity
> `INF + 1` overflows to `Integer.MIN_VALUE`, which then **wins** every `min`. Either check `dp[x] != INF` before adding, or use an `INF` with headroom, such as `Integer.MAX_VALUE / 2` or `1_000_000_000` (still larger than any real answer, and `INF + small` doesn't overflow). `numSquares` above is safe only because every state is reachable.

---

## 7. Evaluation Order

The states and their dependencies form a directed graph; tabulation must visit the states in a **topological order** of it (dependencies first). For the common shapes the order is simple:

| Dependencies | Order |
|---|---|
| `dp[i]` on smaller `i` | `i` increasing |
| `dp[r][c]` on `(r−1, c)` and `(r, c−1)` | row by row, left to right |
| `dp[i][j]` on `(i−1, j−1)`, `(i−1, j)`, `(i, j−1)` | same |
| `dp[l][r]` on shorter intervals inside it | by **length**, increasing |
| suffix states `dp[i]` on larger `i` | `i` decreasing |
| `dp[mask]` on subsets of `mask` | `mask` increasing (a subset is numerically smaller) |

![[DP - Dependency Order.excalidraw|800]]

**Unique paths** (count the right/down paths from the top-left to the bottom-right corner, avoiding obstacles):

```java
static int uniquePathsWithObstacles(int[][] g) {
    int m = g.length, n = g[0].length;
    int[][] dp = new int[m][n];
    for (int r = 0; r < m; r++)
        for (int c = 0; c < n; c++) {
            if (g[r][c] == 1) continue;            // obstacle: 0 paths (already 0)
            if (r == 0 && c == 0) { dp[r][c] = 1; continue; }
            dp[r][c] = (r > 0 ? dp[r - 1][c] : 0) + (c > 0 ? dp[r][c - 1] : 0);
        }
    return dp[m - 1][n - 1];
}
```

`[[0,0,0],[0,1,0],[0,0,0]]` → `2`; `[[1]]` → `0` (the start is blocked); `[[0,0],[1,0],[0,0]]` → `1` (right first, then down). Pre-filling the whole first row and column with 1 is a classic mistake: an obstacle in the first row blocks every cell after it.

> [!important] Cycles mean it isn't (plain) DP
> If moving up and left is also allowed, the cells depend on each other in cycles and no evaluation order exists. "Cheapest path in a grid with 4-direction moves" is a shortest-path problem (Dijkstra, [[DSA/05 - Graphs/03 - Shortest Path Algorithms|Shortest Path Algorithms]]). Memoizing such a recursion either loops forever or caches answers computed from incomplete information.

---

## 8. Space Optimisation

If a row of the table only reads the previous row (or the previous few entries), keep just those. The answer is unchanged; memory drops by a factor of the number of rows. Two things to get right:

1. **Which old values are still needed** when you overwrite a cell.
2. **The loop direction**, which decides whether a neighbour holds the old row's value or the new one.

**Unique paths, 2D → 1D.** `dp[r][c] = dp[r−1][c] + dp[r][c−1]`. In a single array `dp[c]`, before the update `dp[c]` still holds the row above (`dp[r−1][c]`), and `dp[c−1]` has already been updated to the current row (`dp[r][c−1]`). Left to right gives exactly the needed mix:

```java
static int uniquePaths(int m, int n) {
    int[] dp = new int[n];
    Arrays.fill(dp, 1);                            // first row: one way to each cell
    for (int r = 1; r < m; r++)
        for (int c = 1; c < n; c++)
            dp[c] += dp[c - 1];                    // old dp[c] = from above, new dp[c−1] = from the left
    return dp[n - 1];
}
```

`(3, 7)` → `28`; `(3, 2)` → `3`; `(1, 1)` → `1`.

**LCS length, 2D → 1D.** Here the transition also needs the **diagonal** `dp[i−1][j−1]`, which is the old `dp[j−1]`, and that was just overwritten. Save it in a variable before overwriting.

```java
static int lcsLength(String a, String b) {
    int[] dp = new int[b.length() + 1];            // dp[j]: LCS of a[0..i) and b[0..j), for the current i
    for (int i = 1; i <= a.length(); i++) {
        int diag = 0;                              // dp[i−1][j−1]
        for (int j = 1; j <= b.length(); j++) {
            int up = dp[j];                        // dp[i−1][j], about to be overwritten
            dp[j] = a.charAt(i - 1) == b.charAt(j - 1) ? diag + 1 : Math.max(up, dp[j - 1]);
            diag = up;                             // becomes the diagonal for j + 1
        }
    }
    return dp[b.length()];
}
```

![[DP - Rolling Array.excalidraw|800]]

`("abcde", "ace")` → `3`; `("abc", "def")` → `0`. The 2D version and its reconstruction are in [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]], along with the most famous direction trap: 0/1 knapsack in one array must loop capacities **downwards**, or each item gets used repeatedly.

> [!warning] Space optimisation loses the path
> With only the last row kept, the table needed to walk back and **reconstruct** the solution ([[#9. Reconstructing the Solution|§9]]) is gone. If the actual solution is needed, keep the full table (or use Hirschberg's divide-and-conquer trick, which recovers an LCS in linear space at twice the time).

---

## 9. Reconstructing the Solution

The table gives the **value**; to get the solution itself, walk backwards from the answer state, at each step finding which transition produced the stored value.

```java
static List<Integer> robWhich(int[] a) {          // indices of the robbed houses
    int n = a.length;
    int[] dp = new int[n + 1];
    for (int i = 1; i <= n; i++) dp[i] = Math.max(dp[i - 1], a[i - 1] + (i >= 2 ? dp[i - 2] : 0));
    List<Integer> taken = new ArrayList<>();
    for (int i = n; i >= 1; ) {
        if (dp[i] == dp[i - 1]) i--;               // skipping house i−1 explains dp[i]
        else { taken.add(i - 1); i -= 2; }         // otherwise house i−1 was robbed
    }
    Collections.reverse(taken);
    return taken;
}
```

`[2, 7, 9, 3, 1]` → `[0, 2, 4]`. When both transitions give the same value, either choice leads to **an** optimal solution; which one the walk picks decides which of several optimal answers is reported. Problems that want a specific one ("lexicographically smallest") must break ties deliberately. The alternative to recomputing during the walk is to store the choice made at each state (a `parent` or `choice` array) while filling the table.

---

## 10. Complexity and DP as Paths in a DAG

**Time = number of states × work per transition.** Space = number of states stored.

| Problem | States | Transition | Time |
|---|---|---|---|
| House robber, climbing stairs | `n` | `O(1)` | `O(n)` |
| Perfect squares | `n` | `O(√n)` | `O(n√n)` |
| Word break | `n` | `O(L)` lengths, each `O(L)` substring | `O(n·L²)` |
| Unique paths, LCS, edit distance | `m·n` | `O(1)` | `O(m·n)` |
| LIS (simple) | `n` | `O(n)` | `O(n²)` |
| Matrix chain | `n²` | `O(n)` | `O(n³)` |
| TSP over subsets | `2ⁿ·n` | `O(n)` | `O(2ⁿ·n²)` |

Reducing the **transition** cost is the main optimisation once the state is right: prefix sums over the previous row, a monotonic deque for "max over a sliding window of states", binary search, and the convex hull trick ([[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]]).

> [!info]- DP is a shortest (or longest) path in a DAG
> Make each state a vertex and each transition an edge from the smaller state to the larger, weighted by its cost. The dependency graph has no cycles (that's what an evaluation order means), so:
> - an **optimisation** DP is a shortest or longest path from the base states to the answer state;
> - a **counting** DP counts the paths;
> - a **feasibility** DP asks whether a path exists.
> Tabulating in topological order is exactly the DAG shortest-path algorithm. This view explains why cycles break DP (§7), and why problems like "coin change" can also be solved by BFS over amounts: the BFS explores the same graph.

---

## 11. Recognising DP Problems

Signals in the statement:

- "**How many** ways …", "**minimum / maximum** …", "**is it possible** …", "longest / shortest …" over sequences, strings, or grids.
- A sequence of **decisions**, where each decision constrains later ones (adjacency, capacity, cooldown).
- Brute force is exponential, but the "remaining problem" after some decisions is described by **a few numbers** (an index, a capacity, a mode).
- Constraints: `n ≤ 5000` suggests `O(n²)` DP; `n ≤ 500` suggests `O(n³)` (interval DP); `n ≤ 20` suggests bitmask DP; values up to `10⁴` with `n ≤ 100` suggests knapsack over values ([[DSA/01 - Foundations/01 - Complexity Analysis#12. From Constraints to Target Complexity|Complexity § 12]]).

Signals **against** plain DP: the state would have to include an unbounded history (the full set of visited cells in a large grid), or dependencies form cycles (shortest paths), or a greedy rule is provably optimal ([[DSA/06 - Algorithm Design Paradigms/01 - Greedy Algorithms|Greedy Algorithms]]).

---

## 12. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| State too small (missing the "mode") | wrong answers on inputs where history matters | add the mode: colour, holding, cooldown |
| Memo marker equals a valid answer (`0`) | exponential time on some inputs | `-1`, `null`, or a `boolean[]` |
| `Integer.MAX_VALUE` plus something | negative values win the `min` | `INF = MAX_VALUE / 2`, or skip unreachable states |
| `dp[0] = 0` in a counting DP | every count is 0 | the empty case has one way: `dp[0] = 1` |
| Updating three mode variables in sequence | later ones read new values | compute all new values, then assign |
| Wrong loop direction after compressing to 1D | items reused, or wrong mix of rows | check which neighbour must be old vs. new |
| Overwritten diagonal in 1D LCS / edit distance | wrong lengths | save `diag` before overwriting |
| Pre-filling the first row with 1 despite obstacles | paths through obstacles counted | compute the first row with the general rule |
| Deep memoized recursion | `StackOverflowError` | tabulate |
| Missing `% MOD` after an addition | overflow, wrong counts | reduce after every operation |
| Memoizing a recursion with cyclic dependencies | infinite loop or wrong caching | shortest-path algorithm |
| Reusing a static memo across test cases | stale answers | reset per input |
| Off-by-one between "first `i` items" and "item `i`" | index errors, skipped item | state the meaning of `dp[i]` precisely, then index `a[i−1]` |

---

## 13. Trick Questions and Special Cases

> [!question]- House robber on `[2, 1, 1, 2]`?
> `4` (houses 0 and 3). Robbing all even positions or all odd positions gives 3. Skipping **two** houses in a row can be optimal, which is why the recurrence compares `dp[i−1]` (skip) rather than forcing alternation.

> [!question]- What should `dp[0]` be in decode ways, and why does `numDecodings("")` matter?
> `dp[0] = 1`: one way to decode nothing. It's what makes the two-digit case work for the first two characters (`dp[2] += dp[0]`). Whether `""` itself should return 1 or 0 is a problem-statement choice; LeetCode guarantees a non-empty string.

> [!question]- `numDecodings("100")` and `numDecodings("2101")`?
> `0` (`"10"` + `"0"` leaves a lone `0`; `"1"` + `"00"` is invalid) and `1` (`2 · 10 · 1`, since `"21"` + `"01"` is invalid).

> [!question]- In `maxProfitFee`, `hold` is updated using the **new** `cash`. Why is that safe here but not in the cooldown version?
> Using the new `cash` means "sell today and buy back today", which earns `−fee` (nothing gained, fee paid), so it can never improve `hold`: the result is the same as using the old value. With a cooldown, buying on the day after a sale is **forbidden**, so mixing old and new values would allow an illegal transition. When in doubt, use temporaries.

> [!question]- `maxProfitK(1_000_000_000, prices)` with 1,000 prices?
> Allocating two arrays of a billion `int`s fails. With `k ≥ n/2` the limit never binds, so return the unlimited-trades answer (sum of all rises) instead.

> [!question]- `climbStairs(0)`?
> `1` with this code (and by the empty-path convention). Some definitions say 0; the convention that makes the recurrence work is 1.

> [!question]- Unique paths `(m, n) = (3, 7)`: is there a formula?
> Yes: the path is a sequence of `m − 1` downs and `n − 1` rights in some order, so `C(m + n − 2, m − 1) = C(8, 2) = 28`. The DP is still the right tool once obstacles or costs appear.

> [!question]- Why does `numSquares` use `Integer.MAX_VALUE` safely when the warning says not to?
> Every `dp[i − s²]` it reads is finite, because every number is a sum of 1s. The `+ 1` is never applied to the infinity. In coin change, where some amounts are unreachable, the same code overflows.

> [!question]- Can memoization be slower than the plain recursion?
> Only when subproblems don't repeat: then the cache adds overhead and memory for nothing. That's divide and conquer (merge sort), where memoizing makes no sense.

> [!question]- `wordBreak("aaaaaa", ["aaaa", "aaa"])`?
> `true` (`aaa + aaa`). A greedy that always takes the longest matching word first takes `aaaa` and is stuck with `aa`. DP tries every split point, so it finds the split greedy skipped.

> [!question]- Grid where you can move in all four directions, minimise the cost: why doesn't `dp[r][c] = min(neighbours) + cost` work?
> The neighbours depend on `(r, c)` too: the dependency graph has cycles, so there's no order in which all neighbours are final first. It's a shortest-path problem; use Dijkstra.

> [!question]- Paint house with a single house?
> The minimum of its three costs. The loop runs once with `r = g = b = 0` as the "previous house", which correctly imposes no constraint.

---

## 14. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `rob([2,1,1,2])` | `4` | skip two in a row |
| `robCircular([2,3,2])` | `3` | first and last adjacent |
| `robWhich([2,7,9,3,1])` | `[0, 2, 4]` | walk back through `dp` |
| `numDecodings("06")` / `("10")` / `("226")` | `0` / `1` / `3` | |
| `minCostPaint([[17,2,17],[16,16,5],[14,3,19]])` | `10` | colour in the state |
| `maxProfitCooldown([1,2,3,0,2])` | `3` | three-state machine |
| `maxProfitFee([1,3,2,8,4,9], 2)` | `8` | |
| `maxProfitK(2, [3,3,5,0,0,3,1,4])` | `6` | |
| `climbStairs(45)` | `1836311903` | largest in `int` |
| `numSquares(12)` | `3` | greedy says 4 |
| `wordBreak("catsandog", …)` | `false` | |
| `numRollsToTarget(30, 30, 500)` | `222616187` | mod `10⁹+7` |
| `uniquePaths(3, 7)` | `28` | `C(8, 2)` |
| `uniquePathsWithObstacles([[1]])` | `0` | start blocked |
| `lcsLength("abcde", "ace")` | `3` | 1D with saved diagonal |
| `INF = MAX_VALUE`, `INF + 1` | `MIN_VALUE` | use `MAX_VALUE / 2` |

---

## 15. Summary

- DP applies when an answer is built from answers to **overlapping** subproblems (optimal substructure + overlap). It counts (`+`), optimises (`min`/`max`), or decides (`OR`).
- The path: brute-force recursion → memoize → tabulate → keep only the rows you need.
- The recipe: **state** (one precise sentence), **transition** (the last decision), **base cases**, **order** (dependencies first), **answer**.
- The state must capture everything the future depends on; add a "mode" (colour, holding, cooldown) or split the problem (circular robber) when it doesn't.
- Evaluate in topological order of the dependencies; cycles mean shortest paths, not DP.
- Rolling arrays save memory but need care with loop direction and the diagonal, and lose the ability to reconstruct the solution.
- Time = states × transition cost; DP is a path problem on the DAG of states.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/06 - Algorithm Design Paradigms/03 - Backtracking|Backtracking]] · Next: [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]]
- [[DSA/01 - Foundations/02 - Recursion|Recursion]]: recursion trees and memoization
- [[DSA/01 - Foundations/01 - Complexity Analysis|Complexity Analysis]]: complexity with memoization, constraints → target complexity
- [[DSA/06 - Algorithm Design Paradigms/01 - Greedy Algorithms|Greedy Algorithms]]: when one choice per step suffices
- [[DSA/06 - Algorithm Design Paradigms/02 - Divide and Conquer|Divide and Conquer]]: the same recursion without overlap
- [[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]]: bitmask, tree, interval, digit DP and optimisations
- [[DSA/05 - Graphs/03 - Shortest Path Algorithms|Shortest Path Algorithms]]: when dependencies form cycles
