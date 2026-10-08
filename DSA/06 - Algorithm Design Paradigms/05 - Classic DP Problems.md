# Classic DP Problems

The problems in this note are the building blocks that most DP questions reduce to: knapsack (0/1, unbounded, bounded), subset sums and partitions, coin change in its two counting forms, longest increasing subsequence, longest common subsequence and its relatives, edit distance and pattern matching, grid paths, matrix-chain multiplication, and partitioning a sequence. Each one is stated with its state and recurrence first, then implemented in Java. The method behind them (state, transition, order, space optimisation) is in [[DSA/06 - Algorithm Design Paradigms/04 - Dynamic Programming Fundamentals|Dynamic Programming — Fundamentals]].

The traps here are specific and recurring: a loop that runs in the wrong direction turns 0/1 knapsack into unbounded knapsack, swapping two loops turns "combinations" into "permutations", the `tails` array of the fast LIS isn't an LIS, and `*` means different things in regex and wildcard matching. Each is called out where it happens.

## Contents

- [[#1. 0/1 Knapsack|1. 0/1 Knapsack]]
- [[#2. Subset Sum and Partition|2. Subset Sum and Partition]]
- [[#3. Unbounded Knapsack and Coin Change|3. Unbounded Knapsack and Coin Change]]
- [[#4. Longest Increasing Subsequence|4. Longest Increasing Subsequence]]
- [[#5. Longest Common Subsequence|5. Longest Common Subsequence]]
- [[#6. Edit Distance and String Matching|6. Edit Distance and String Matching]]
- [[#7. Grid DP|7. Grid DP]]
- [[#8. Matrix-Chain Multiplication|8. Matrix-Chain Multiplication]]
- [[#9. Partitioning a Sequence|9. Partitioning a Sequence]]
- [[#10. Subarray DP|10. Subarray DP]]
- [[#11. Common Mistakes|11. Common Mistakes]]
- [[#12. Trick Questions and Special Cases|12. Trick Questions and Special Cases]]
- [[#13. Quick Reference — Non-Obvious Outcomes|13. Quick Reference — Non-Obvious Outcomes]]
- [[#14. Summary|14. Summary]]

---

## 1. 0/1 Knapsack

`n` items with weights `wt[i]` and values `val[i]`; a bag of capacity `W`. Each item is taken **at most once**. Maximise the total value.

> [!note] State and recurrence
> `dp[i][w]` = the best value using only the first `i` items with capacity `w`.
> ```
> dp[0][w] = 0
> dp[i][w] = dp[i−1][w]                                     -- skip item i−1
>          or dp[i−1][w − wt[i−1]] + val[i−1]   if wt[i−1] ≤ w    -- take it (the max of the two)
> ```
> Answer: `dp[n][W]`. Time and space `O(n·W)`.

```java
static int knapsack01(int[] wt, int[] val, int W) {
    int n = wt.length;
    int[][] dp = new int[n + 1][W + 1];
    for (int i = 1; i <= n; i++)
        for (int w = 0; w <= W; w++) {
            dp[i][w] = dp[i - 1][w];                                       // skip item i−1
            if (wt[i - 1] <= w) dp[i][w] = Math.max(dp[i][w], dp[i - 1][w - wt[i - 1]] + val[i - 1]);
        }
    return dp[n][W];
}
```

Weights `[1, 3, 4, 5]`, values `[1, 4, 5, 7]`, `W = 7` → `9` (the items of weight 3 and 4); weights `[10, 20, 30]`, values `[60, 100, 120]`, `W = 50` → `220`.

### 1.1 One array, capacities downwards

Row `i` only reads row `i − 1`, and only at the same or **smaller** capacities. In a single array, looping `w` from high to low means `dp[w − wt]` hasn't been updated for item `i` yet: it still holds row `i − 1`.

```java
static int knapsack01Compact(int[] wt, int[] val, int W) {
    int[] dp = new int[W + 1];                     // dp[w]: best value with capacity w, items so far
    for (int i = 0; i < wt.length; i++)
        for (int w = W; w >= wt[i]; w--)           // DOWNWARDS: each item used at most once
            dp[w] = Math.max(dp[w], dp[w - wt[i]] + val[i]);
    return dp[W];
}
```

![[Classic DP - Knapsack Loop Direction.excalidraw|800]]

> [!warning] Upwards turns it into unbounded knapsack
> With `for (w = wt[i]; w <= W; w++)`, `dp[w − wt[i]]` may already include item `i`, so the item can be added again and again. On `[60/10, 100/20, 120/30]` with `W = 50`, the upward loop answers `300` (five copies of the first item) instead of `220`. That's exactly the unbounded version ([[#3.1 Unbounded knapsack|§3.1]]), so the direction **is** the difference between the two problems.

### 1.2 Which items?

Walking back needs the 2D table: item `i − 1` was taken exactly when `dp[i][w] ≠ dp[i − 1][w]`.

```java
static List<Integer> knapsackItems(int[] wt, int[] val, int W) {
    int n = wt.length;
    int[][] dp = new int[n + 1][W + 1];
    for (int i = 1; i <= n; i++)
        for (int w = 0; w <= W; w++) {
            dp[i][w] = dp[i - 1][w];
            if (wt[i - 1] <= w) dp[i][w] = Math.max(dp[i][w], dp[i - 1][w - wt[i - 1]] + val[i - 1]);
        }
    List<Integer> items = new ArrayList<>();
    for (int i = n, w = W; i >= 1; i--)
        if (dp[i][w] != dp[i - 1][w]) { items.add(i - 1); w -= wt[i - 1]; }   // value changed: taken
    Collections.reverse(items);
    return items;
}
```

`[1, 3, 4, 5]`, `[1, 4, 5, 7]`, `W = 7` → `[1, 2]`.

### 1.3 Huge capacity, small values: swap the roles

`O(n·W)` is hopeless for `W = 10⁹`. If the **values** are small, index the table by value instead: `minW[v]` = the least weight that achieves value exactly `v`. The answer is the largest `v` with `minW[v] ≤ W`.

```java
static int knapsackByValue(int[] wt, int[] val, long W) {
    int V = 0;
    for (int v : val) V += v;
    long[] minW = new long[V + 1];
    Arrays.fill(minW, Long.MAX_VALUE / 2);         // unreachable values
    minW[0] = 0;
    for (int i = 0; i < wt.length; i++)
        for (int v = V; v >= val[i]; v--)          // still 0/1: downwards
            minW[v] = Math.min(minW[v], minW[v - val[i]] + wt[i]);
    for (int v = V; v >= 0; v--) if (minW[v] <= W) return v;
    return 0;
}
```

Weights `[10⁹, 999999999, 2]`, values `[10, 8, 3]`, `W = 1000000001` → `11` (the second and third items). `O(n · Σval)`.

> [!info]- Knapsack is NP-hard, yet `O(n·W)`?
> `O(n·W)` is <span class="hl-blue">pseudo-polynomial</span>: polynomial in the **value** of `W`, but `W` takes only `log W` bits to write down, so the running time is exponential in the input's size. That's why the DP is fast for `W ≤ 10⁵` and useless for `W = 10¹⁸`, and why it doesn't contradict NP-hardness. With `n ≤ 40` and huge weights, [[DSA/06 - Algorithm Design Paradigms/07 - Meet in the Middle|Meet in the Middle]] is the tool.

---

## 2. Subset Sum and Partition

Knapsack where only feasibility matters: is there a subset with sum exactly `s`? `can[s] |= can[s − x]`, downwards for each number.

### 2.1 Partition into two equal halves

```java
static boolean canPartition(int[] nums) {
    int sum = 0;
    for (int x : nums) sum += x;
    if (sum % 2 != 0) return false;                // an odd total can't split evenly
    int half = sum / 2;
    boolean[] can = new boolean[half + 1];         // can[s]: some subset of the numbers so far sums to s
    can[0] = true;
    for (int x : nums)
        for (int s = half; s >= x; s--)            // downwards: each number used once
            can[s] |= can[s - x];
    return can[half];
}
```

`[1, 5, 11, 5]` → `true` (`11 = 1 + 5 + 5`); `[1, 2, 3, 5]` → `false` (sum 11 is odd).

A `boolean` array updated with "OR shifted by `x`" is a bitset operation. `BigInteger` does it 64 bits at a time:

```java
static boolean canPartitionBits(int[] nums) {
    int sum = 0;
    for (int x : nums) sum += x;
    if (sum % 2 != 0) return false;
    java.math.BigInteger bits = java.math.BigInteger.ONE;    // bit s set ⇔ sum s reachable
    for (int x : nums) bits = bits.or(bits.shiftLeft(x));
    return bits.testBit(sum / 2);
}
```

### 2.2 Target sum: counting sign assignments

Put `+` or `−` before each number so that the total is `target`; count the ways. If `P` is the sum of the numbers with `+` and `N` the rest, then `P − N = target` and `P + N = total`, so `P = (total + target) / 2`. Count subsets with sum `P`.

```java
static int findTargetSumWays(int[] nums, int target) {
    int total = 0;
    for (int x : nums) total += x;
    if (Math.abs(target) > total || (total + target) % 2 != 0) return 0;
    int p = (total + target) / 2;                  // sum of the numbers given a + sign
    int[] ways = new int[p + 1];
    ways[0] = 1;
    for (int x : nums)
        for (int s = p; s >= x; s--) ways[s] += ways[s - x];
    return ways[p];
}
```

`([1, 1, 1, 1, 1], 3)` → `5`; `([1], 1)` → `1`; `([1], 2)` → `0`; `([0, 0, 0, 0, 0, 0, 0, 0, 1], 1)` → `256`. Each `0` doubles the count (`+0` and `−0` are different assignments), and the loop handles it without special cases: with `x = 0`, `ways[s] += ways[s]` doubles every entry. The `abs` check comes first because a negative `p` would index the array.

### 2.3 Closest split: last stone weight II

Smashing stones `x ≤ y` leaves `y − x`; the smallest possible final weight equals the smallest possible difference between two groups. Find the largest subset sum `≤ total / 2`.

```java
static int lastStoneWeightII(int[] stones) {
    int total = 0;
    for (int s : stones) total += s;
    boolean[] can = new boolean[total / 2 + 1];
    can[0] = true;
    for (int x : stones)
        for (int s = total / 2; s >= x; s--) can[s] |= can[s - x];
    for (int s = total / 2; ; s--) if (can[s]) return total - 2 * s;
}
```

`[2, 7, 4, 1, 8, 1]` → `1`; `[31, 26, 33, 21, 40]` → `5`. The same reduction solves "minimum subset sum difference" and "partition an array into two arrays to minimise the sum difference" (that last one with `n ≤ 30` and large values needs [[DSA/06 - Algorithm Design Paradigms/07 - Meet in the Middle|Meet in the Middle]]).

---

## 3. Unbounded Knapsack and Coin Change

### 3.1 Unbounded knapsack

Each item may be taken **any number of times**. Same array, capacities **upwards**: `dp[w − wt[i]]` may already include item `i`, which is now exactly what we want.

```java
static int knapsackUnbounded(int[] wt, int[] val, int W) {
    int[] dp = new int[W + 1];
    for (int i = 0; i < wt.length; i++)
        for (int w = wt[i]; w <= W; w++)           // UPWARDS: reuse allowed
            dp[w] = Math.max(dp[w], dp[w - wt[i]] + val[i]);
    return dp[W];
}
```

`[60/10, 100/20, 120/30]`, `W = 50` → `300`.

### 3.2 Coin change: fewest coins

```java
static int coinChange(int[] coins, int amount) {
    final int INF = Integer.MAX_VALUE / 2;         // + 1 must not overflow
    int[] dp = new int[amount + 1];
    Arrays.fill(dp, INF);
    dp[0] = 0;
    for (int a = 1; a <= amount; a++)
        for (int c : coins)
            if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);   // the last coin is c
    return dp[amount] >= INF ? -1 : dp[amount];
}
```

`([1, 2, 5], 11)` → `3`; `([2], 3)` → `−1`; `([1], 0)` → `0`; `([1, 3, 4], 6)` → `2` (greedy says 3, [[DSA/06 - Algorithm Design Paradigms/01 - Greedy Algorithms#7. Coin Change and Canonical Coin Systems|Greedy § 7]]). For the minimum, the loop order doesn't matter: the order of coins in a solution doesn't change how many there are.

### 3.3 Counting: combinations vs. permutations

For **counting**, the loop order decides what is counted.

```java
static int change(int amount, int[] coins) {      // combinations: {1, 2} and {2, 1} are the same
    int[] ways = new int[amount + 1];
    ways[0] = 1;
    for (int c : coins)                            // coins OUTER
        for (int a = c; a <= amount; a++) ways[a] += ways[a - c];
    return ways[amount];
}

static int combinationSum4(int[] nums, int target) {   // sequences: (1, 2) and (2, 1) are different
    int[] ways = new int[target + 1];
    ways[0] = 1;
    for (int a = 1; a <= target; a++)              // amount OUTER
        for (int x : nums) if (x <= a) ways[a] += ways[a - x];   // the LAST number is x
    return ways[target];
}
```

![[Classic DP - Combinations vs Permutations.excalidraw|800]]

`change(5, [1, 2, 5])` → `4`; `change(3, [2])` → `0`; `change(0, [7])` → `1`. `combinationSum4([1, 2, 3], 4)` → `7`; `([9], 3)` → `0`.

> [!important] Why the loop order decides it
> **Coins outer**: all uses of coin 1 are added before coin 2 is considered at all, so every counted way uses its coins in the fixed order "1s, then 2s, then 5s". Each multiset is built in exactly one order: combinations.
> **Amount outer**: for each amount, the transition chooses **the last** element freely among all values. Different last elements give different sequences: `(1, 2)` ends in 2, `(2, 1)` ends in 1, and both are counted: permutations.

### 3.4 Bounded knapsack: `cnt[i]` copies of item `i`

Treating each copy as a separate 0/1 item costs `O(W · Σcnt)`. Split `cnt` copies into bundles of `1, 2, 4, …, 2ᵏ` plus a remainder; any count from `0` to `cnt` is a sum of distinct bundles, and there are only `O(log cnt)` of them.

```java
static int knapsackBounded(int[] wt, int[] val, int[] cnt, int W) {
    int[] dp = new int[W + 1];
    for (int i = 0; i < wt.length; i++)
        for (int k = 1, left = cnt[i]; left > 0; k <<= 1) {   // bundles 1, 2, 4, …, then the remainder
            int take = Math.min(k, left);
            left -= take;
            int bw = take * wt[i], bv = take * val[i];
            for (int w = W; w >= bw; w--) dp[w] = Math.max(dp[w], dp[w - bw] + bv);   // a 0/1 item
        }
    return dp[W];
}
```

`cnt = 13` becomes bundles `1, 2, 4, 6`: `O(W · Σ log cnt)`. (A monotonic-queue version reaches `O(n·W)`; it's rarely needed.)

---

## 4. Longest Increasing Subsequence

The longest **strictly increasing** subsequence (not necessarily contiguous).

### 4.1 `O(n²)`: ending at each index

```java
static int lengthOfLISQuadratic(int[] a) {
    int n = a.length, best = 0;
    int[] dp = new int[n];                         // dp[i]: longest increasing subsequence ENDING at a[i]
    for (int i = 0; i < n; i++) {
        dp[i] = 1;
        for (int j = 0; j < i; j++)
            if (a[j] < a[i]) dp[i] = Math.max(dp[i], dp[j] + 1);
        best = Math.max(best, dp[i]);              // the answer can end anywhere, not just at n − 1
    }
    return best;
}
```

`[10, 9, 2, 5, 3, 7, 101, 18]` → `4`; `[0, 1, 0, 3, 2, 3]` → `4`; `[7, 7, 7, 7]` → `1`.

### 4.2 `O(n log n)`: the tails array

Keep `tails[k]` = the **smallest** possible last element of an increasing subsequence of length `k + 1` seen so far. `tails` is always strictly increasing, so each new `x` can be placed by binary search: it replaces the first tail `≥ x` (a length-`k + 1` subsequence can now end lower), or extends the longest one if `x` is larger than all tails.

```
for x in a:
    i = first index with tails[i] ≥ x          -- lower bound
    tails[i] = x                                -- replace, or append if i = len
    if i = len: len = len + 1
```

```java
static int lengthOfLIS(int[] a) {
    int[] tails = new int[a.length];
    int len = 0;
    for (int x : a) {
        int lo = 0, hi = len;                      // lower bound of x in tails[0..len)
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (tails[mid] < x) lo = mid + 1; else hi = mid;
        }
        tails[lo] = x;
        if (lo == len) len++;
    }
    return len;
}
```

![[Classic DP - LIS Tails.excalidraw|800]]

> [!warning] `tails` is not a subsequence
> On `[3, 4, 5, 1]`, `tails` ends as `[1, 4, 5]`: correct length 3, but `1` comes **after** 4 and 5 in the array. Only `len` is meaningful; recovering an actual LIS needs parent pointers (§4.3).

**Strict vs. non-decreasing**: lower bound (`tails[mid] < x`) gives strictly increasing; for non-decreasing, use the upper bound (`tails[mid] <= x`), so an equal value extends instead of replacing. `[7, 7, 7, 7]` → `1` strict, `4` non-decreasing. The minimum number of elements to delete so the array becomes sorted is `n − LNDS`.

### 4.3 Recovering the sequence

Store indices in `tails`, and for each element its predecessor: the tail of the length just below where it lands.

```java
static List<Integer> lisSequence(int[] a) {
    int n = a.length, len = 0;
    int[] tailIdx = new int[n], parent = new int[n];   // tailIdx[k]: index of the tail of length k + 1
    for (int i = 0; i < n; i++) {
        int lo = 0, hi = len;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (a[tailIdx[mid]] < a[i]) lo = mid + 1; else hi = mid;
        }
        parent[i] = lo > 0 ? tailIdx[lo - 1] : -1;
        tailIdx[lo] = i;
        if (lo == len) len++;
    }
    LinkedList<Integer> seq = new LinkedList<>();
    for (int i = len == 0 ? -1 : tailIdx[len - 1]; i != -1; i = parent[i]) seq.addFirst(a[i]);
    return seq;
}
```

`[10, 9, 2, 5, 3, 7, 101, 18]` → `[2, 3, 7, 18]`; `[3, 4, 5, 1]` → `[3, 4, 5]`.

### 4.4 Counting the longest subsequences

Track, for each `i`, both the longest length ending there and **how many** subsequences achieve it.

```java
static int findNumberOfLIS(int[] a) {
    int n = a.length, best = 0, total = 0;
    int[] len = new int[n], cnt = new int[n];
    for (int i = 0; i < n; i++) {
        len[i] = 1; cnt[i] = 1;
        for (int j = 0; j < i; j++)
            if (a[j] < a[i]) {
                if (len[j] + 1 > len[i]) { len[i] = len[j] + 1; cnt[i] = cnt[j]; }   // a longer one: reset
                else if (len[j] + 1 == len[i]) cnt[i] += cnt[j];                    // as long: add
            }
        if (len[i] > best) { best = len[i]; total = cnt[i]; }
        else if (len[i] == best) total += cnt[i];
    }
    return total;
}
```

`[1, 3, 5, 4, 7]` → `2` (`1,3,5,7` and `1,3,4,7`); `[2, 2, 2, 2, 2]` → `5` (each single element is an LIS of length 1).

### 4.5 Two dimensions: Russian doll envelopes

An envelope fits inside another if **both** its width and height are strictly smaller. Sort by width ascending and, for equal widths, height **descending**; then the answer is the LIS of the heights.

```java
static int maxEnvelopes(int[][] envelopes) {
    int[][] e = envelopes.clone();
    Arrays.sort(e, (x, y) -> x[0] != y[0] ? Integer.compare(x[0], y[0]) : Integer.compare(y[1], x[1]));
    int[] h = new int[e.length];
    for (int i = 0; i < e.length; i++) h[i] = e[i][1];
    return lengthOfLIS(h);                         // strictly increasing heights
}
```

`[[5, 4], [6, 4], [6, 7], [2, 3]]` → `3` (`[2,3] → [5,4] → [6,7]`); `[[1, 1], [1, 1], [1, 1]]` → `1`. With heights ascending inside equal widths, `[6, 4]` and `[6, 7]` would form an increasing pair of heights and be counted as nesting, though equal widths can't nest. Descending order makes equal-width envelopes a decreasing run, from which an increasing subsequence takes at most one.

| Problem | Reduction |
|---|---|
| Maximum length of a pair chain | sort by end, greedy (or LIS) |
| Largest divisible subset | sort, then LIS-style DP with `a[i] % a[j] == 0` |
| Longest bitonic subsequence | LIS ending at `i` + LDS starting at `i` − 1 |
| Minimum deletions to make sorted | `n − ` longest non-decreasing subsequence |
| LCS of two **permutations** | relabel by positions in one, LIS of the other: `O(n log n)` |
| Box stacking, building bridges | sort by one dimension, LIS on the other |

---

## 5. Longest Common Subsequence

> [!note] State and recurrence
> `dp[i][j]` = length of the LCS of the prefixes `a[0..i)` and `b[0..j)`.
> ```
> dp[i][0] = dp[0][j] = 0
> dp[i][j] = dp[i−1][j−1] + 1                    if a[i−1] = b[j−1]
>          = max(dp[i−1][j], dp[i][j−1])           otherwise
> ```

If the last characters match, using them as the last pair of the LCS is always safe. If not, at least one of them is unused, so drop one or the other.

```java
static String lcs(String a, String b) {
    int m = a.length(), n = b.length();
    int[][] dp = new int[m + 1][n + 1];
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++)
            dp[i][j] = a.charAt(i - 1) == b.charAt(j - 1) ? dp[i - 1][j - 1] + 1
                                                          : Math.max(dp[i - 1][j], dp[i][j - 1]);
    StringBuilder sb = new StringBuilder();        // walk back from the bottom-right corner
    for (int i = m, j = n; i > 0 && j > 0; ) {
        if (a.charAt(i - 1) == b.charAt(j - 1)) { sb.append(a.charAt(i - 1)); i--; j--; }
        else if (dp[i - 1][j] >= dp[i][j - 1]) i--;
        else j--;
    }
    return sb.reverse().toString();
}
```

`("abcde", "ace")` → `"ace"`; `("abc", "def")` → `""`. The one-array version with a saved diagonal is in [[DSA/06 - Algorithm Design Paradigms/04 - Dynamic Programming Fundamentals#8. Space Optimisation|DP Fundamentals § 8]].

### 5.1 Relatives of LCS

| Problem | Answer |
|---|---|
| Minimum deletions (from both) to make two strings equal | `m + n − 2·LCS` |
| Minimum insertions + deletions to turn `a` into `b` | `(m − LCS)` deletions + `(n − LCS)` insertions |
| Shortest common supersequence length | `m + n − LCS` |
| Longest palindromic subsequence | `LCS(s, reverse(s))`, or interval DP |
| Minimum insertions to make a palindrome | `n − LPS` |
| Longest common **substring** | contiguous: reset to 0 on a mismatch |

```java
static String shortestCommonSupersequence(String a, String b) {
    int m = a.length(), n = b.length();
    int[][] dp = new int[m + 1][n + 1];
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++)
            dp[i][j] = a.charAt(i - 1) == b.charAt(j - 1) ? dp[i - 1][j - 1] + 1
                                                          : Math.max(dp[i - 1][j], dp[i][j - 1]);
    StringBuilder sb = new StringBuilder();
    int i = m, j = n;
    while (i > 0 && j > 0) {
        if (a.charAt(i - 1) == b.charAt(j - 1)) { sb.append(a.charAt(i - 1)); i--; j--; }   // shared: once
        else if (dp[i - 1][j] >= dp[i][j - 1]) sb.append(a.charAt(--i));                  // a's char alone
        else sb.append(b.charAt(--j));                                                     // b's char alone
    }
    while (i > 0) sb.append(a.charAt(--i));
    while (j > 0) sb.append(b.charAt(--j));
    return sb.reverse().toString();
}

static int longestPalindromeSubseq(String s) {
    int n = s.length();
    int[][] dp = new int[n][n];                    // dp[l][r]: longest palindromic subsequence of s[l..r]
    for (int l = n - 1; l >= 0; l--) {             // l decreasing: dp[l+1][…] is ready
        dp[l][l] = 1;
        for (int r = l + 1; r < n; r++)
            dp[l][r] = s.charAt(l) == s.charAt(r) ? dp[l + 1][r - 1] + 2
                                                  : Math.max(dp[l + 1][r], dp[l][r - 1]);
    }
    return dp[0][n - 1];
}

static int longestCommonSubstring(String a, String b) {
    int best = 0;
    int[][] dp = new int[a.length() + 1][b.length() + 1];   // longest common SUFFIX of the two prefixes
    for (int i = 1; i <= a.length(); i++)
        for (int j = 1; j <= b.length(); j++)
            if (a.charAt(i - 1) == b.charAt(j - 1)) {
                dp[i][j] = dp[i - 1][j - 1] + 1;
                best = Math.max(best, dp[i][j]);
            }                                      // mismatch: stays 0, the run is broken
    return best;
}
```

`shortestCommonSupersequence("abac", "cab")` → `"cabac"` (length `4 + 3 − 2 = 5`); `longestPalindromeSubseq("bbbab")` → `4`, `("cbbd")` → `2`; `longestCommonSubstring("abcdxyz", "xyzabcd")` → `4` (`"abcd"`), while their LCS is also 4 here but differs in general: `("abcde", "ace")` has LCS 3 and common substring 1.

---

## 6. Edit Distance and String Matching

### 6.1 Edit distance (Levenshtein)

The fewest single-character insertions, deletions and replacements to turn `a` into `b`.

> [!note] State and recurrence
> `dp[i][j]` = edits to turn `a[0..i)` into `b[0..j)`.
> ```
> dp[i][0] = i  (delete everything)        dp[0][j] = j  (insert everything)
> dp[i][j] = dp[i−1][j−1]                              if a[i−1] = b[j−1]
>          = 1 + min(dp[i−1][j−1],   -- replace a[i−1] by b[j−1]
>                    dp[i−1][j],     -- delete a[i−1]
>                    dp[i][j−1])     -- insert b[j−1]
> ```

```java
static int minDistance(String a, String b) {
    int m = a.length(), n = b.length();
    int[][] dp = new int[m + 1][n + 1];
    for (int i = 0; i <= m; i++) dp[i][0] = i;
    for (int j = 0; j <= n; j++) dp[0][j] = j;
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++)
            if (a.charAt(i - 1) == b.charAt(j - 1)) dp[i][j] = dp[i - 1][j - 1];
            else dp[i][j] = 1 + Math.min(dp[i - 1][j - 1], Math.min(dp[i - 1][j], dp[i][j - 1]));
    return dp[m][n];
}
```

![[Classic DP - Edit Distance Table.excalidraw|800]]

`("horse", "ros")` → `3`; `("intention", "execution")` → `5`; `("", "abc")` → `3`. With only insertions and deletions allowed (no replace), the answer is `m + n − 2·LCS` instead. Checking whether two strings are **one** edit apart doesn't need the table: compare from both ends in `O(n)`.

### 6.2 Distinct subsequences: counting embeddings

How many times does `t` occur in `s` as a subsequence? Either `s[i−1]` is used for `t[j−1]` (if they match) or it isn't.

```java
static int numDistinct(String s, String t) {
    int n = t.length();
    long[] dp = new long[n + 1];                   // dp[j]: ways to form t[0..j) from the part of s seen so far
    dp[0] = 1;                                     // the empty t: one way
    for (int i = 1; i <= s.length(); i++)
        for (int j = Math.min(i, n); j >= 1; j--)  // downwards: s[i−1] is used at most once per embedding
            if (s.charAt(i - 1) == t.charAt(j - 1)) dp[j] += dp[j - 1];
    return (int) dp[n];
}
```

`("rabbbit", "rabbit")` → `3`; `("babgbag", "bag")` → `5`.

### 6.3 Regular expression matching (`.` and `*`)

`.` matches any single character; `x*` matches **zero or more** copies of the preceding element `x`. The match must cover the whole string.

```java
static boolean isMatch(String s, String p) {
    int m = s.length(), n = p.length();
    boolean[][] dp = new boolean[m + 1][n + 1];    // dp[i][j]: s[0..i) matches p[0..j)
    dp[0][0] = true;
    for (int j = 2; j <= n; j++)                   // "a*", "a*b*", … match the empty string
        dp[0][j] = p.charAt(j - 1) == '*' && dp[0][j - 2];
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++) {
            char pc = p.charAt(j - 1);
            if (pc == '*') {
                char prev = p.charAt(j - 2);
                dp[i][j] = dp[i][j - 2]                                               // x* matches nothing
                        || ((prev == '.' || prev == s.charAt(i - 1)) && dp[i - 1][j]);  // x* takes one more char
            } else {
                dp[i][j] = (pc == '.' || pc == s.charAt(i - 1)) && dp[i - 1][j - 1];
            }
        }
    return dp[m][n];
}
```

`("aa", "a")` → `false`; `("aa", "a*")` → `true`; `("ab", ".*")` → `true`; `("aab", "c*a*b")` → `true` (`c*` matches nothing); `("mississippi", "mis*is*p*.")` → `false`.

### 6.4 Wildcard matching (`?` and `*`)

Here `?` matches one character and `*` matches **any sequence on its own**, not a repetition of the previous element.

```java
static boolean isMatchWildcard(String s, String p) {
    int m = s.length(), n = p.length();
    boolean[][] dp = new boolean[m + 1][n + 1];
    dp[0][0] = true;
    for (int j = 1; j <= n; j++) dp[0][j] = p.charAt(j - 1) == '*' && dp[0][j - 1];
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++) {
            char pc = p.charAt(j - 1);
            if (pc == '*') dp[i][j] = dp[i][j - 1] || dp[i - 1][j];   // * matches nothing, or one more char
            else dp[i][j] = (pc == '?' || pc == s.charAt(i - 1)) && dp[i - 1][j - 1];
        }
    return dp[m][n];
}
```

`("aa", "a")` → `false`; `("aa", "*")` → `true`; `("cb", "?a")` → `false`; `("adceb", "*a*b")` → `true`; `("acdcb", "a*c?b")` → `false`.

> [!warning] The two `*`s
> In a **regex**, `a*` is one unit ("any number of `a`"), so the `*` looks back at `p[j−2]` and the transition skips **two** pattern characters. In a **wildcard**, `*` stands alone ("anything"), and the transition skips one. Copying one solution into the other problem is a classic error: `isMatch("ab", "*")` isn't even a valid regex.

---

## 7. Grid DP

Unique paths and minimum path sum are worked through in [[DSA/06 - Algorithm Design Paradigms/04 - Dynamic Programming Fundamentals#7. Evaluation Order|DP Fundamentals § 7]]. Three more patterns:

**Triangle** (minimum path from top to bottom, moving to an adjacent number below): solve **bottom-up**, so the answer ends in a single cell and there are no edge cases at the borders.

```java
static int minimumTotal(List<List<Integer>> tri) {
    int n = tri.size();
    int[] dp = new int[n + 1];                     // dp[c]: best path from row r + 1, position c, to the bottom
    for (int r = n - 1; r >= 0; r--)
        for (int c = 0; c <= r; c++)
            dp[c] = tri.get(r).get(c) + Math.min(dp[c], dp[c + 1]);
    return dp[0];
}
```

`[[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]` → `11` (`2 + 3 + 5 + 1`).

**Maximal square** (the largest square of 1s): a square with bottom-right corner `(r, c)` can be one larger than the smallest of the three squares ending above, to the left, and diagonally.

```java
static int maximalSquare(char[][] g) {
    int m = g.length, n = g[0].length, best = 0;
    int[][] dp = new int[m + 1][n + 1];            // dp[r+1][c+1]: side of the largest square ending at (r, c)
    for (int r = 0; r < m; r++)
        for (int c = 0; c < n; c++)
            if (g[r][c] == '1') {
                dp[r + 1][c + 1] = 1 + Math.min(dp[r][c], Math.min(dp[r][c + 1], dp[r + 1][c]));
                best = Math.max(best, dp[r + 1][c + 1]);
            }
    return best * best;                            // the problem asks for the AREA
}
```

`["10100", "10111", "11111", "10010"]` → `4`; `[["0"]]` → `0`. The largest **rectangle** of 1s is a different technique: histogram heights per row plus a monotonic stack ([[DSA/02 - Linear Data Structures/04 - Stacks|Stacks]]).

**Dungeon game** (the minimum starting health so that it never drops to 0 on some right/down path): a forward DP would need to know both the current health and the lowest point so far. Backwards, one number suffices: the health needed **on entering** each cell.

```java
static int calculateMinimumHP(int[][] d) {
    int m = d.length, n = d[0].length;
    int[][] need = new int[m + 1][n + 1];          // need[r][c]: minimum health when entering (r, c)
    for (int[] row : need) Arrays.fill(row, Integer.MAX_VALUE);
    need[m][n - 1] = need[m - 1][n] = 1;           // after the last cell, at least 1 health must remain
    for (int r = m - 1; r >= 0; r--)
        for (int c = n - 1; c >= 0; c--)
            need[r][c] = Math.max(1, Math.min(need[r + 1][c], need[r][c + 1]) - d[r][c]);
    return need[0][0];
}
```

`[[-2, -3, 3], [-5, -10, 1], [10, 30, -5]]` → `7`; `[[0]]` → `1`; `[[100]]` → `1` (health can't start at 0, however big the reward). The `max(1, …)` is what prevents a huge later reward from "paying back" a death earlier on the path.

---

## 8. Matrix-Chain Multiplication

Multiplying a `p × q` matrix by a `q × r` matrix costs `p·q·r` scalar multiplications. A chain `A₁A₂…Aₙ` can be parenthesised in many ways, all giving the same product but very different costs. Matrix `i` has dimensions `dims[i] × dims[i+1]`.

> [!note] Interval DP
> `dp[l][r]` = the cheapest way to multiply matrices `l..r`. The **last** multiplication splits the chain at some `k`: `(l..k) × (k+1..r)`.
> ```
> dp[l][l] = 0
> dp[l][r] = min over l ≤ k < r of  dp[l][k] + dp[k+1][r] + dims[l]·dims[k+1]·dims[r+1]
> ```
> Fill by interval **length**: `O(n³)` time, `O(n²)` space.

```java
static long matrixChain(int[] dims) {
    int n = dims.length - 1;                       // number of matrices
    long[][] dp = new long[n][n];
    for (int len = 2; len <= n; len++)
        for (int l = 0; l + len - 1 < n; l++) {
            int r = l + len - 1;
            dp[l][r] = Long.MAX_VALUE;
            for (int k = l; k < r; k++)
                dp[l][r] = Math.min(dp[l][r], dp[l][k] + dp[k + 1][r] + (long) dims[l] * dims[k + 1] * dims[r + 1]);
        }
    return dp[0][n - 1];
}
```

`[10, 30, 5, 60]` → `4500` (`(AB)C`: `10·30·5 + 10·5·60`; `A(BC)` would cost `27000`); `[40, 20, 30, 10, 30]` → `26000`; a single matrix `[5, 10]` → `0`. This is the template for every interval DP (burst balloons, minimum cost to cut a stick, optimal BST), covered in [[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]].

---

## 9. Partitioning a Sequence

"Cut the sequence into pieces, each with a property, optimising something": `dp[i]` over prefixes, and the transition chooses where the **last piece** starts.

**Palindrome partitioning II** (fewest cuts so that every piece is a palindrome):

```java
static int minCut(String s) {
    int n = s.length();
    boolean[][] pal = new boolean[n][n];           // pal[j][i]: s[j..i] is a palindrome
    int[] cuts = new int[n];                       // cuts[i]: fewest cuts for s[0..i]
    for (int i = 0; i < n; i++) {
        cuts[i] = i;                               // worst case: cut between every character
        for (int j = 0; j <= i; j++)
            if (s.charAt(j) == s.charAt(i) && (i - j < 2 || pal[j + 1][i - 1])) {
                pal[j][i] = true;                  // the last piece is s[j..i]
                cuts[i] = j == 0 ? 0 : Math.min(cuts[i], cuts[j - 1] + 1);
            }
    }
    return cuts[n - 1];
}
```

`"aab"` → `1`; `"a"` → `0`; `"ab"` → `1`; `"abacdc"` → `1` (`aba | cdc`). Listing all partitions instead is backtracking ([[DSA/06 - Algorithm Design Paradigms/03 - Backtracking#5.3 Palindrome partitioning|Backtracking § 5.3]]).

| Problem | Last piece | Note |
|---|---|---|
| Word break | a dictionary word `s[j..i)` | [[DSA/06 - Algorithm Design Paradigms/04 - Dynamic Programming Fundamentals#6.1 Think about the last step|DP Fundamentals § 6.1]] |
| Palindrome partitioning II | a palindrome `s[j..i]` | above |
| Split array largest sum (into `k` parts) | `dp[i][k] = min over j of max(dp[j][k−1], sum(j..i))` | `O(k·n²)`; binary search on the answer is `O(n log S)` ([[DSA/03 - Sorting and Searching/02 - Binary Search#6.2 Ship packages within D days / split array largest sum (minimise the maximum)|Binary Search § 6.2]]) |
| Partition array for maximum sum (pieces of length ≤ k, each becomes its max) | the last `≤ k` elements | `O(n·k)` |
| Partition into `k` equal-sum subsets (not contiguous) | — | bitmask DP or backtracking ([[DSA/06 - Algorithm Design Paradigms/03 - Backtracking#9. Pruning Strategies|Backtracking § 9]]) |

---

## 10. Subarray DP

For contiguous subarrays the state is "best subarray **ending at** `i`", and the answer is the best over all `i`.

**Maximum subarray sum**: Kadane, `endingHere = max(a[i], endingHere + a[i])` ([[DSA/06 - Algorithm Design Paradigms/02 - Divide and Conquer#5. Maximum Subarray|Divide and Conquer § 5]]).

**Maximum product subarray**: a negative number turns the smallest product into the largest, so track both the largest and the smallest product ending at `i`.

```java
static int maxProduct(int[] a) {
    int best = a[0], hi = a[0], lo = a[0];         // largest / smallest product of a subarray ending here
    for (int i = 1; i < a.length; i++) {
        int x = a[i];
        int h = Math.max(x, Math.max(hi * x, lo * x));
        int l = Math.min(x, Math.min(hi * x, lo * x));
        hi = h; lo = l;                            // both from the OLD hi and lo
        best = Math.max(best, hi);
    }
    return best;
}
```

`[2, 3, -2, 4]` → `6`; `[-2, 0, -1]` → `0`; `[-2, 3, -4]` → `24` (the whole array: two negatives). Other subarray DPs: maximum circular subarray sum (`max(kadane, total − min subarray)`, unless all are negative), longest turbulent subarray, and "maximum sum with one deletion" (two states: deletion used or not).

---

## 11. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| 0/1 knapsack in 1D with an upward loop | items reused: `300` instead of `220` | capacities downwards |
| Unbounded knapsack with a downward loop | each item at most once | capacities upwards |
| Coin change II with the amount loop outside | permutations counted (`(1,2)` and `(2,1)`) | coins outer for combinations |
| `INF = Integer.MAX_VALUE` in coin change | `INF + 1` overflows, wins the `min` | `MAX_VALUE / 2` |
| Target sum without the parity / `abs` check | negative index or wrong count | check `|target| ≤ total` and parity first |
| LIS answer taken as `dp[n−1]` | wrong when the LIS ends earlier | `max` over all `dp[i]` |
| Treating `tails` as the LIS | not a subsequence | parent pointers |
| Lower vs. upper bound mixed up in LIS | strict/non-strict swapped | `<` for strict, `<=` for non-decreasing |
| Envelopes sorted with heights ascending | equal widths counted as nesting | heights descending within equal widths |
| LCS reconstruction with the 1D table | path information lost | keep the 2D table |
| Common substring computed like LCS (`max` on mismatch) | subsequence length instead | reset to 0 on a mismatch |
| Edit distance base row/column left at 0 | distance to `""` is 0 | `dp[i][0] = i`, `dp[0][j] = j` |
| Regex `*` treated like a wildcard | `"aa"` vs `"a*"` misjudged | `x*` is a unit, look back two |
| Empty-string row of the match table not initialised | `"aab"` vs `"c*a*b"` false | `dp[0][j]` for `x*` patterns |
| Dungeon game without `max(1, …)` | later rewards "repay" an earlier death | clamp to at least 1 |
| Matrix chain cost in `int` | overflow | `long` |
| Max product tracking only the maximum | `[-2, 3, -4]` → 3 | track min and max |

---

## 12. Trick Questions and Special Cases

> [!question]- What changes between 0/1 and unbounded knapsack in the one-array code?
> Only the direction of the capacity loop: downwards reads the previous item's values (each item once), upwards reads values that may already include the current item (unlimited copies).

> [!question]- `change(0, coins)` and `coinChange(coins, 0)`?
> `1` way (choose nothing) and `0` coins. Both follow from the base case `dp[0]`.

> [!question]- `change(4, [1, 2])` vs. `combinationSum4([1, 2], 4)`?
> `3` combinations (`1111`, `112`, `22`) vs. `5` sequences (`1111`, `112`, `121`, `211`, `22`). Same transition, swapped loops.

> [!question]- `combinationSum4` intermediate values overflow `int`, but the answer fits. Is the answer wrong?
> No. Java `int` addition wraps modulo `2³²`, and the DP only adds, so every value is correct modulo `2³²`. If the true answer is below `2³¹`, the wrapped result **is** the true answer. (This fails as soon as a `min`, `max` or comparison is involved.)

> [!question]- `findTargetSumWays([0, 0, 0, 0, 0, 0, 0, 0, 1], 1)`?
> `256`. The 1 must be `+1`, and each of the eight zeros can be `+0` or `−0`: `2⁸` assignments.

> [!question]- `lengthOfLIS([0, 1, 0, 3, 2, 3])` and the final `tails`?
> `4`, with `tails = [0, 1, 2, 3]`. Here `tails` happens to be a valid LIS; on `[3, 4, 5, 1]` it's `[1, 4, 5]`, which isn't.

> [!question]- Longest non-decreasing subsequence of `[1, 3, 3, 2, 3]`?
> `4` (`1, 3, 3, 3`) with the upper bound. The strict LIS is `2`... no: `1, 2, 3` gives `3`. Strict `3`, non-decreasing `4`.

> [!question]- `maxEnvelopes([[1, 1], [1, 1], [1, 1]])`?
> `1`. Identical envelopes don't nest (strictly smaller in both dimensions is required).

> [!question]- Is the LCS unique?
> No. `("ab", "ba")` has two LCSs of length 1, `"a"` and `"b"`; the walk-back's tie rule (`>=` prefers moving up) decides which one is returned.

> [!question]- Edit distance between a string and its reverse, `("ab", "ba")`?
> `2` (replace both, or delete and insert). Edit distance has no "swap" operation; the Damerau variant adds transpositions and gives 1.

> [!question]- `isMatch("", "a*b*c*")` and `isMatchWildcard("", "***")`?
> Both `true`: every `x*` and every `*` can match nothing. That's what the `dp[0][j]` initialisation computes.

> [!question]- Why does dungeon game run from the bottom-right corner?
> Going forward, the best choice at a cell depends on two numbers (current health and the minimum reached so far), and neither alone gives optimal substructure. Backwards, "minimum health needed from here on" is one number and does.

> [!question]- Matrix chain with dimensions `[10, 20]` (one matrix)?
> `0`: nothing to multiply. With two matrices there's only one order, so the answer is just `dims[0]·dims[1]·dims[2]`.

> [!question]- `maxProduct([0, 2])` and `maxProduct([-2])`?
> `2` and `-2`. A single negative element is its own best subarray; the answer must be non-empty, so it can't be 0 or 1 by default.

> [!question]- `canPartition([2, 2, 3, 5])`?
> `false`. The total 12 is even and half is 6, but no subset sums to 6 (`2 + 2 = 4`, `2 + 3 = 5`, `2 + 2 + 3 = 7`). Even totals are necessary, not sufficient.

---

## 13. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `knapsack01([10,20,30], [60,100,120], 50)` | `220` | upward loop gives 300 |
| `knapsackItems([1,3,4,5], [1,4,5,7], 7)` | `[1, 2]` | |
| `knapsackByValue(…, W = 10⁹+1)` | `11` | table by value |
| `canPartition([1,2,3,5])` | `false` | odd total |
| `findTargetSumWays([1,1,1,1,1], 3)` | `5` | `P = (5+3)/2 = 4` |
| `lastStoneWeightII([2,7,4,1,8,1])` | `1` | closest split |
| `coinChange([2], 3)` | `−1` | unreachable |
| `change(5, [1,2,5])` | `4` | coins outer |
| `combinationSum4([1,2,3], 4)` | `7` | amount outer |
| `lengthOfLIS([10,9,2,5,3,7,101,18])` | `4` | |
| `findNumberOfLIS([2,2,2,2,2])` | `5` | |
| `maxEnvelopes([[5,4],[6,4],[6,7],[2,3]])` | `3` | heights descending per width |
| `lcs("abcde", "ace")` | `"ace"` | |
| `shortestCommonSupersequence("abac", "cab")` | `"cabac"` | `m + n − LCS` |
| `minDistance("intention", "execution")` | `5` | |
| `numDistinct("babgbag", "bag")` | `5` | |
| `isMatch("aab", "c*a*b")` | `true` | `c*` = nothing |
| `isMatchWildcard("acdcb", "a*c?b")` | `false` | |
| `calculateMinimumHP([[100]])` | `1` | at least 1 to start |
| `matrixChain([10,30,5,60])` | `4500` | `(AB)C` |
| `minCut("aab")` | `1` | `aa | b` |
| `maxProduct([-2,3,-4])` | `24` | min becomes max |

---

## 14. Summary

- **0/1 knapsack**: `dp[i][w] = max(skip, take)`; in one array, capacities **downwards**. Huge capacity with small values: index by value.
- **Subset sum / partition / target sum**: knapsack over sums with `OR` or `+`; target sum reduces to a subset count with `P = (total + target) / 2`.
- **Unbounded knapsack / coin change**: capacities **upwards**. Counting: coins outer → combinations, amount outer → permutations. Bounded counts: binary bundles.
- **LIS**: `O(n²)` "ending at `i`", or `O(n log n)` with `tails` (lower bound strict, upper bound non-decreasing); `tails` isn't the sequence. Envelopes: sort width asc, height desc.
- **LCS** and relatives (SCS, deletions, palindromic subsequence, common substring); **edit distance** with three operations; **distinct subsequences**; **regex** (`x*` is a unit) vs **wildcard** (`*` alone).
- **Grid**: triangle bottom-up, maximal square from three neighbours, dungeon backwards.
- **Matrix chain**: interval DP by length, `O(n³)`. **Partitioning**: the last piece; **subarrays**: best ending at `i` (track min and max for products).

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/06 - Algorithm Design Paradigms/04 - Dynamic Programming Fundamentals|Dynamic Programming — Fundamentals]] · Next: [[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]]
- [[DSA/06 - Algorithm Design Paradigms/01 - Greedy Algorithms|Greedy Algorithms]]: fractional knapsack, canonical coin systems
- [[DSA/06 - Algorithm Design Paradigms/03 - Backtracking|Backtracking]]: listing solutions instead of counting them
- [[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]]: lower/upper bound in the LIS tails array
- [[DSA/06 - Algorithm Design Paradigms/07 - Meet in the Middle|Meet in the Middle]]: subset sums with huge values
- [[DSA/07 - String Algorithms/03 - Palindromes|Palindromes]]: longest palindromic substring, Manacher
