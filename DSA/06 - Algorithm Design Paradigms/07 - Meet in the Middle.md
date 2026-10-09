# Meet in the Middle

<span class="hl-blue">Meet in the middle</span> (MITM) splits an exponential search into two halves, enumerates each half separately, and combines the two lists of partial results with sorting, binary search, two pointers or hashing. For subsets of `n` items, that replaces `2ⁿ` with about `2 · 2^(n/2)`: for `n = 40`, about two million instead of a trillion. It's the tool when `n` is too large for plain brute force (`n ≈ 30–45`) and the values are too large for a DP over sums or capacities.

This note covers the general shape and its cost, generating sorted subset sums of a half in linear time, the standard problems (counting subsets with a given sum, closest subset sum, 0/1 knapsack with huge weights, splitting into two equal-size halves), the pair-sum version (4Sum II), bidirectional BFS as MITM on graphs, and baby-step giant-step for discrete logarithms.

## Contents

- [[#1. The Idea|1. The Idea]]
- [[#2. Generating the Half Sums|2. Generating the Half Sums]]
- [[#3. Subset Sum with Large Values|3. Subset Sum with Large Values]]
- [[#4. Closest Subset Sum|4. Closest Subset Sum]]
- [[#5. Knapsack with Huge Weights|5. Knapsack with Huge Weights]]
- [[#6. Splitting into Two Equal-Size Halves|6. Splitting into Two Equal-Size Halves]]
- [[#7. Pair Sums: 4Sum II|7. Pair Sums: 4Sum II]]
- [[#8. Bidirectional BFS|8. Bidirectional BFS]]
- [[#9. Baby-Step Giant-Step (advanced)|9. Baby-Step Giant-Step (advanced)]]
- [[#10. When It Applies|10. When It Applies]]
- [[#11. Common Mistakes|11. Common Mistakes]]
- [[#12. Trick Questions and Special Cases|12. Trick Questions and Special Cases]]
- [[#13. Quick Reference — Non-Obvious Outcomes|13. Quick Reference — Non-Obvious Outcomes]]
- [[#14. Summary|14. Summary]]

---

## 1. The Idea

```
meetInTheMiddle(items):
    split items into halves A and B
    LA = all partial results from A            -- 2^|A| of them
    LB = all partial results from B            -- 2^|B| of them
    sort LB (or put it in a hash map)
    for each x in LA:
        find the best / matching partners y in LB      -- binary search, two pointers, or hash lookup
    combine
```

![[Meet in the Middle - Splitting the Search.excalidraw|800]]

A complete solution is a choice for the first half **and** a choice for the second. The search over pairs is only fast if the **combine** step doesn't look at every pair, so the objective must decompose: "sum equals `T`" becomes "partner equals `T − x`", "closest to `T`" becomes "nearest neighbour of `T − x` in a sorted list", "weight `≤ W`, maximise value" becomes "best value among partners with weight `≤ W − w`".

| `n` | Brute force `2ⁿ` | MITM `~2 · 2^(n/2)` (plus a log for sorting) |
|---|---|---|
| 20 | `10⁶` | `2·10³` |
| 30 | `10⁹` | `6.5·10⁴` |
| 40 | `10¹²` | `2·10⁶` |
| 50 | `10¹⁵` | `6.7·10⁷` (memory becomes the limit) |

The cost is **memory**: one half's list must be stored, `2^(n/2)` entries. For `n = 40` that's a million `long`s (8 MB); for `n = 60` it would be a billion.

> [!note] MITM vs. DP over sums
> A subset-sum DP is `O(n · S)` where `S` is the range of sums: great for `S ≤ 10⁶`, useless for values up to `10⁹`. MITM is `O(2^(n/2) · n)` regardless of the values. Small `n` and large values → MITM; large `n` and small values → DP ([[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems#2. Subset Sum and Partition|Classic DP § 2]]).

---

## 2. Generating the Half Sums

The direct way is to loop over every mask of the half and add up its bits: `O(2^h · h)`, then sort for another `O(2^h · h)`. A neater way builds the sorted list directly: start from `[0]`, and for each element `x`, the new list is the merge of the old list with "the old list plus `x`". Adding a constant keeps a list sorted, so each step is a linear merge, and the sizes `1, 2, 4, …, 2^h` add up to `O(2^h)`.

```java
static long[] sortedSubsetSums(int[] a, int from, int to) {   // all 2^(to−from) subset sums of a[from..to), sorted
    long[] sums = {0};
    for (int i = from; i < to; i++) {
        long[] with = new long[sums.length];
        for (int k = 0; k < sums.length; k++) with[k] = sums[k] + a[i];   // sorted, because sums is
        sums = mergeSorted(sums, with);
    }
    return sums;
}

static long[] mergeSorted(long[] x, long[] y) {
    long[] r = new long[x.length + y.length];
    int i = 0, j = 0, k = 0;
    while (i < x.length && j < y.length) r[k++] = x[i] <= y[j] ? x[i++] : y[j++];
    while (i < x.length) r[k++] = x[i++];
    while (j < y.length) r[k++] = y[j++];
    return r;
}
```

`sortedSubsetSums([3, 1, 2], 0, 3)` → `[0, 1, 2, 3, 3, 4, 5, 6]`. Negative elements are fine: adding a negative constant also preserves the order. Equal sums from different subsets stay as separate entries, which matters when **counting**.

---

## 3. Subset Sum with Large Values

Count the subsets (including the empty one) whose sum is exactly `T`, for `n ≤ 40` and values up to `10⁹`. Each subset is a left part plus a right part; for each left sum `s`, count the right sums equal to `T − s` by binary search on the sorted right list.

```java
static long countSubsetsWithSum(int[] a, long target) {
    int h = a.length / 2;
    long[] left = sortedSubsetSums(a, 0, h), right = sortedSubsetSums(a, h, a.length);
    long count = 0;
    for (long s : left)
        count += firstGreater(right, target - s) - firstAtLeast(right, target - s);   // copies of T − s
    return count;
}

static int firstAtLeast(long[] a, long x) {       // lower bound
    int lo = 0, hi = a.length;
    while (lo < hi) { int mid = (lo + hi) >>> 1; if (a[mid] < x) lo = mid + 1; else hi = mid; }
    return lo;
}

static int firstGreater(long[] a, long x) {       // upper bound
    int lo = 0, hi = a.length;
    while (lo < hi) { int mid = (lo + hi) >>> 1; if (a[mid] <= x) lo = mid + 1; else hi = mid; }
    return lo;
}
```

`([1, 2, 3, 4], 5)` → `2` (`{1, 4}` and `{2, 3}`); `([3, 34, 4, 12, 5, 2], 9)` → `2`; `([10⁹, 10⁹, −10⁹, 1], 1)` → `3` (`{1}` and both `{10⁹, −10⁹, 1}`); `([5], 0)` → `1` (the empty subset). `O(2^(n/2) · n)` overall. The upper and lower bounds come from [[DSA/03 - Sorting and Searching/02 - Binary Search#3. Lower and Upper Bound|Binary Search § 3]]; a `HashMap<Long, Integer>` of right sums gives the same counts with `O(1)` lookups.

> [!warning] Sums need `long`
> Twenty values of `10⁹` add up to `2·10¹⁰`, far beyond `int`. Every sum, and `T − s`, must be `long`.

---

## 4. Closest Subset Sum

Choose a subsequence (any subset) whose sum is as close as possible to `goal`; return `|sum − goal|` (LeetCode "closest subsequence sum", `n ≤ 40`). With both halves sorted, two pointers find the closest pair sum in linear time, as in sorted two-sum ([[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]]): if the current pair is too small, only a larger left value can help; if too large, only a smaller right value.

```java
static long minAbsDifference(int[] nums, long goal) {
    int h = nums.length / 2;
    long[] L = sortedSubsetSums(nums, 0, h), R = sortedSubsetSums(nums, h, nums.length);
    long best = Long.MAX_VALUE;
    int i = 0, j = R.length - 1;                   // smallest left, largest right
    while (i < L.length && j >= 0) {
        long sum = L[i] + R[j];
        best = Math.min(best, Math.abs(sum - goal));
        if (sum < goal) i++;
        else if (sum > goal) j--;
        else return 0;
    }
    return best;
}
```

![[Meet in the Middle - Two Pointers on Half Sums.excalidraw|800]]

`([5, -7, 3, 5], 6)` → `0` (`5 − 7 + 3 + 5`); `([7, -9, 15, -2], -5)` → `1`; `([1, 2, 3], -7)` → `7` (the empty subsequence, sum 0, is closest). The empty subset is allowed here; if a problem requires a non-empty one, the pair (empty, empty) must be excluded.

---

## 5. Knapsack with Huge Weights

0/1 knapsack with `n ≤ 40`, weights and capacity up to `10¹⁵`: neither the capacity DP nor the value DP ([[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems#1.3 Huge capacity, small values: swap the roles|Classic DP § 1.3]]) fits. Enumerate the right half's subsets as (weight, value) pairs, sort them by weight, and keep a **prefix maximum** of values: `best[k]` = the best value among the `k + 1` lightest right subsets. For each left subset with weight `w ≤ W`, binary-search the heaviest right subset that still fits and take `best` there.

```java
static long knapsackMITM(long[] wt, long[] val, long W) {
    int n = wt.length, h = n / 2, m = n - h;
    long[][] right = new long[1 << m][];           // {weight, value} of every subset of the right half
    for (int mask = 0; mask < (1 << m); mask++) {
        long w = 0, v = 0;
        for (int i = 0; i < m; i++) if ((mask >> i & 1) == 1) { w += wt[h + i]; v += val[h + i]; }
        right[mask] = new long[]{w, v};
    }
    Arrays.sort(right, (x, y) -> Long.compare(x[0], y[0]));
    long[] rw = new long[right.length], best = new long[right.length];
    for (int k = 0; k < right.length; k++) {
        rw[k] = right[k][0];
        best[k] = Math.max(k > 0 ? best[k - 1] : 0, right[k][1]);   // best value with weight ≤ rw[k]
    }
    long ans = 0;
    for (int mask = 0; mask < (1 << h); mask++) {
        long w = 0, v = 0;
        for (int i = 0; i < h; i++) if ((mask >> i & 1) == 1) { w += wt[i]; v += val[i]; }
        if (w > W) continue;
        int k = firstGreater(rw, W - w) - 1;       // the heaviest right subset that still fits
        if (k >= 0) ans = Math.max(ans, v + best[k]);
    }
    return ans;
}
```

Weights `[10⁹, 999999999, 2, 5]`, values `[10, 8, 3, 4]`, `W = 1000000001` → `11` (the second and third items). The prefix maximum is what makes one binary search enough: without it, the heaviest fitting subset isn't necessarily the most valuable one.

---

## 6. Splitting into Two Equal-Size Halves

Split `2n` numbers into two groups of exactly `n` each, minimising the absolute difference of their sums (`n ≤ 15`, values up to `10⁷`, possibly negative). If `k` of the first group's elements come from the left half, the other `n − k` must come from the right half, so the half sums are **grouped by subset size** and only matching sizes are combined. With group sum `S`, the difference is `|total − 2S|`.

```java
static long minimumDifference(int[] nums) {
    int n = nums.length / 2;
    long total = 0;
    for (int x : nums) total += x;
    List<List<Long>> left = new ArrayList<>(), right = new ArrayList<>();   // sums grouped by subset size
    for (int k = 0; k <= n; k++) { left.add(new ArrayList<>()); right.add(new ArrayList<>()); }
    for (int mask = 0; mask < (1 << n); mask++) {
        long ls = 0, rs = 0;
        for (int i = 0; i < n; i++)
            if ((mask >> i & 1) == 1) { ls += nums[i]; rs += nums[n + i]; }
        left.get(Integer.bitCount(mask)).add(ls);
        right.get(Integer.bitCount(mask)).add(rs);
    }
    for (List<Long> r : right) Collections.sort(r);
    long best = Long.MAX_VALUE;
    for (int k = 0; k <= n; k++)                   // k elements from the left half, n − k from the right
        for (long ls : left.get(k)) {
            List<Long> r = right.get(n - k);
            int lo = 0, hi = r.size();             // first partner with 2·(ls + rs) ≥ total
            while (lo < hi) {
                int mid = (lo + hi) >>> 1;
                if (2 * (ls + r.get(mid)) < total) lo = mid + 1; else hi = mid;
            }
            for (int t = lo - 1; t <= lo; t++)     // the partners just below and just above
                if (t >= 0 && t < r.size()) best = Math.min(best, Math.abs(total - 2 * (ls + r.get(t))));
        }
    return best;
}
```

`[3, 9, 7, 3]` → `2` (`{3, 9}` vs `{7, 3}`); `[-36, 36]` → `72`; `[2, -1, 0, 4, -2, -9]` → `0`. Without the size grouping, the closest pair might use 5 elements from the left and 4 from the right, which isn't a valid split into equal halves. A DP over sums would be `n · (range of sums)`, about `30 · 3·10⁸`: too slow, hence MITM.

---

## 7. Pair Sums: 4Sum II

Count tuples `(i, j, k, l)` with `a[i] + b[j] + c[k] + d[l] = 0` for four arrays of length `n ≤ 200`. Brute force is `n⁴`; storing every `a[i] + b[j]` in a hash map and looking up `−(c[k] + d[l])` is `O(n²)`. The "halves" here are pairs of arrays rather than halves of a set, but it's the same idea.

```java
static int fourSumCount(int[] a, int[] b, int[] c, int[] d) {
    Map<Integer, Integer> ab = new HashMap<>();    // pair sum → how many (i, j) give it
    for (int x : a) for (int y : b) ab.merge(x + y, 1, Integer::sum);
    int count = 0;
    for (int x : c) for (int y : d) count += ab.getOrDefault(-(x + y), 0);
    return count;
}
```

`([1, 2], [-2, -1], [-1, 2], [0, 2])` → `2`; `([0], [0], [0], [0])` → `1`. The same split solves "does any 4-element subset sum to `T`?" in `O(n² log n)` instead of `O(n⁴)`, with the care that the two pairs must use **different** indices when they come from the same array.

---

## 8. Bidirectional BFS

In a graph where each node has about `b` neighbours, a BFS to depth `d` explores about `bᵈ` nodes. Searching from **both** ends at once and stopping when the two frontiers touch explores about `2 · b^(d/2)`: the same square-root saving as on subsets, because a shortest path of length `d` splits into two halves of length about `d/2`.

![[Meet in the Middle - Bidirectional BFS.excalidraw|800]]

**Word ladder**: the fewest words in a chain from `begin` to `end` changing one letter at a time, every intermediate word in the dictionary.

```java
static int ladderLength(String begin, String end, List<String> wordList) {
    Set<String> dict = new HashSet<>(wordList);
    if (!dict.contains(end)) return 0;
    Set<String> front = new HashSet<>(List.of(begin)), back = new HashSet<>(List.of(end));
    Set<String> visited = new HashSet<>(List.of(begin, end));
    for (int len = 1; !front.isEmpty() && !back.isEmpty(); len++) {   // len = edges used so far
        if (front.size() > back.size()) { Set<String> t = front; front = back; back = t; }   // grow the smaller side
        Set<String> next = new HashSet<>();
        for (String w : front) {
            char[] cs = w.toCharArray();
            for (int i = 0; i < cs.length; i++) {
                char orig = cs[i];
                for (char ch = 'a'; ch <= 'z'; ch++) {
                    if (ch == orig) continue;
                    cs[i] = ch;
                    String nw = new String(cs);
                    if (back.contains(nw)) return len + 1;          // the frontiers meet: len + 1 words
                    if (dict.contains(nw) && visited.add(nw)) next.add(nw);
                }
                cs[i] = orig;
            }
        }
        front = next;
    }
    return 0;
}
```

`("hit", "cog", [hot, dot, dog, lot, log, cog])` → `5` (`hit → hot → dot → dog → cog`); without `cog` in the list → `0`. Two rules make it work: check for a meeting **before** marking a word visited, and always expand the **smaller** frontier (otherwise one side can grow much faster and most of the saving is lost). Plain BFS is in [[DSA/05 - Graphs/01 - Graph Representations and Traversals|Graph Representations and Traversals]].

> [!info]- Other "meet in the middle on states" problems
> Puzzles with a known goal state (the 15-puzzle, Rubik's-cube style permutations, "reach this configuration in at most `k` moves") use the same trick: BFS `k/2` moves from the start, `k/2` moves backwards from the goal, and intersect. The backward search needs **reversible** moves (or the inverse moves), and both sides must use the same state encoding so the intersection test is a hash lookup.

---

## 9. Baby-Step Giant-Step (advanced)

The <span class="hl-blue">discrete logarithm</span>: the smallest `x ≥ 0` with `aˣ ≡ b (mod m)`, for `gcd(a, m) = 1`. Trying every `x` is `O(m)`. Write `x = i·n − j` with `n = ⌈√m⌉`, `1 ≤ i ≤ n` and `0 ≤ j < n`. Then `aˣ ≡ b` becomes `a^(i·n) ≡ b · aʲ`: store every **baby step** `b · aʲ` in a hash map, then walk the **giant steps** `a^(i·n)` and look each one up. `O(√m)` time and memory.

```java
static long discreteLog(long a, long b, long m) {  // smallest x ≥ 0 with a^x ≡ b (mod m); gcd(a, m) = 1; −1 if none
    a %= m; b %= m;
    if (b == 1 % m) return 0;                      // a^0 = 1 (and everything is 0 mod 1)
    long n = (long) Math.ceil(Math.sqrt((double) m));
    Map<Long, Long> baby = new HashMap<>();        // b·a^j mod m → j (a later, larger j overwrites)
    long cur = b;
    for (long j = 0; j < n; j++) { baby.put(cur, j); cur = cur * a % m; }
    long step = 1;
    for (long j = 0; j < n; j++) step = step * a % m;   // a^n
    long giant = 1;
    for (long i = 1; i <= n; i++) {
        giant = giant * step % m;                  // a^(i·n)
        Long j = baby.get(giant);
        if (j != null) return i * n - j;           // a^(i·n) = b·a^j  ⇒  a^(i·n − j) = b
    }
    return -1;
}
```

`(2, 3, 5)` → `3` (`2³ = 8 ≡ 3`); `(3, 13, 17)` → `4`; `(2, 1, 7)` → `0`; `(2, 3, 7)` → `−1` (the powers of 2 mod 7 are only 1, 2, 4). Keeping the **largest** `j` for each baby-step value and scanning `i` upwards gives the smallest `x`. The products `cur * a` need `m < 3·10⁹` to stay inside a `long`; modular arithmetic is in [[DSA/01 - Foundations/04 - Math for Algorithms#3. Modular Arithmetic|Math § 3]].

---

## 10. When It Applies

> [!important] Checklist
> 1. **Size**: brute force is `2ⁿ` (or `bᵈ`) with `n` around 30–45: too big for brute force, too small to need anything cleverer.
> 2. **Values**: a DP over sums, capacities or values would be too large (values up to `10⁹` or more).
> 3. **Decomposable objective**: a full solution is a pair (left part, right part), and the condition on the pair can be checked by **searching** the other half's list (equal to, closest to, at most) rather than by trying every pair.
> 4. **Memory**: `2^(n/2)` entries fit (`n ≤ ~44` for `long`s in a few hundred MB).

| Problem | Combine step | Cost |
|---|---|---|
| Count subsets with sum `T` | binary search / hash map | `O(2^(n/2) · n)` |
| Closest subset sum | two pointers on sorted halves | `O(2^(n/2))` after generation |
| Knapsack, huge weights | sort by weight, prefix max, binary search | `O(2^(n/2) · n)` |
| Equal-size split, min difference | group by size, binary search | `O(2^n · n)` for `2n` elements |
| 4Sum II / four-number subset sum | hash map of pair sums | `O(n²)` |
| Shortest path in a huge implicit graph | bidirectional BFS | `O(b^(d/2))` |
| Discrete logarithm | hash map of baby steps | `O(√m)` |

What MITM **can't** do well: objectives where the two halves interact through more than a single number (a constraint between specific left and right elements, like "no two adjacent items"), or problems where the full search space doesn't factor into two independent halves at all.

---

## 11. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Sums in `int` | overflow with large values | `long` everywhere |
| Deduplicating half sums when counting | counts too low | keep duplicates; count multiplicities |
| Sorting both halves and nested-looping the pairs | `O(2ⁿ)` again | binary search, two pointers, or hashing |
| Forgetting the empty subset | off by one in counts and closest sums | it's one of the `2^h` sums (exclude only if the problem says non-empty) |
| Knapsack MITM without the prefix maximum | lighter but more valuable subsets missed | `best[k] = max(best[k−1], value[k])` |
| Equal-size split combining any left and right sums | groups of the wrong size | group sums by subset size |
| Bidirectional BFS expanding a fixed side | little or no speed-up | expand the smaller frontier |
| Bidirectional BFS marking before checking the other frontier | meeting missed or detected late | check the other side first |
| Word ladder answer as the number of edges | off by one | the count is of **words**: edges + 1 |
| Baby-step giant-step with `gcd(a, m) > 1` | wrong answers | this version needs `a` invertible mod `m` |
| `n = 50` with MITM on a 256 MB limit | out of memory | `2²⁵` longs per half is already 256 MB; reduce or change approach |

---

## 12. Trick Questions and Special Cases

> [!question]- Why split into halves and not, say, thirds?
> With thirds, combining three lists without trying all pairs is hard: two of them would have to be merged first into a list of size `2^(2n/3)`, which is worse than `2^(n/2)`. Halves balance the two lists, which minimises the larger one. (Specialised 4-way schemes like Schroeppel–Shamir reduce the **memory** to `2^(n/4)` while keeping `2^(n/2)` time.)

> [!question]- With an odd `n`, which half gets the extra element?
> Either; the cost is dominated by the larger half, `2^⌈n/2⌉`. Giving the extra element to the half that's **sorted and searched** costs slightly more memory; to the half that's only scanned, slightly more time.

> [!question]- `countSubsetsWithSum([0, 0, 0], 0)`?
> `8`: every subset of three zeros sums to 0, including the empty one. Each half keeps its duplicate sums, so the counts multiply correctly.

> [!question]- `minAbsDifference([1, 2, 3], -7)`?
> `7`. Every non-empty subset has a positive sum, so the empty subset (sum 0) is the closest to −7.

> [!question]- Is sorting both halves and using two pointers enough for "count subsets with sum exactly `T`"?
> Yes, but only with care: equal values on both sides form blocks, and the count for a matching pair of blocks is the **product** of their sizes. Binary search for the lower and upper bound (or a hash map) handles multiplicities with less bookkeeping.

> [!question]- `minimumDifference([-36, 36])`?
> `72`. Each group must have exactly one element, so the only split is `{−36}` vs `{36}`. Picking the closest sums without the size constraint would answer 0 (everything vs nothing).

> [!question]- Word ladder where `begin` isn't in the word list?
> That's normal: `begin` doesn't need to be in the list, only the intermediate words and `end`. If `end` isn't in the list, the answer is `0` immediately.

> [!question]- How much does bidirectional BFS save for branching factor 10 and depth 6?
> About `10⁶` vs `2 · 10³` nodes: the saving is a square root, not a constant factor, as long as the two frontiers grow at similar rates.

> [!question]- `discreteLog(2, 3, 7)`?
> `−1`. Powers of 2 modulo 7 cycle through 1, 2, 4 only, so 3 is never reached. Not every `b` has a discrete logarithm unless `a` is a generator (primitive root) of the group.

> [!question]- `fourSumCount` with the four arrays all equal to `[0, 0]`?
> `16`: every choice of indices works, `2⁴` tuples. The hash map stores `0 → 4` (four `(i, j)` pairs), and each of the four `(k, l)` pairs adds 4.

---

## 13. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `n = 40`: brute force vs MITM | `10¹²` vs `~2·10⁶` | `2ⁿ` → `2 · 2^(n/2)` |
| `sortedSubsetSums([3,1,2])` | `[0,1,2,3,3,4,5,6]` | duplicates kept |
| `countSubsetsWithSum([1,2,3,4], 5)` | `2` | |
| `countSubsetsWithSum([10⁹,10⁹,−10⁹,1], 1)` | `3` | `long` sums |
| `countSubsetsWithSum([0,0,0], 0)` | `8` | multiplicities |
| `minAbsDifference([5,-7,3,5], 6)` | `0` | |
| `minAbsDifference([1,2,3], -7)` | `7` | empty subset |
| `knapsackMITM(…, W = 10⁹+1)` | `11` | prefix max + binary search |
| `minimumDifference([3,9,7,3])` | `2` | grouped by size |
| `minimumDifference([-36,36])` | `72` | sizes must match |
| `fourSumCount([1,2],[-2,-1],[-1,2],[0,2])` | `2` | pair sums in a map |
| `ladderLength("hit","cog",…)` | `5` | words, not edges |
| `discreteLog(3, 13, 17)` | `4` | baby-step giant-step |
| `discreteLog(2, 3, 7)` | `−1` | 2 isn't a generator mod 7 |

---

## 14. Summary

- MITM splits a `2ⁿ` search into two halves of `2^(n/2)`, enumerates both, and **combines** with sorting plus binary search, two pointers, or hashing. The combine step must not try all pairs.
- Use it for `n ≈ 30–45` with values too large for a DP; the price is `2^(n/2)` memory.
- Sorted half sums can be generated in `O(2^h)` by merging "without `x`" and "with `x`".
- Standard problems: count subsets with sum `T` (bounds or a hash map, keep duplicates), closest subset sum (two pointers), knapsack with huge weights (sort by weight, prefix max of values), equal-size splits (group by subset size), 4Sum II (pair sums in a map).
- **Bidirectional BFS** is MITM on graphs: expand the smaller frontier, stop when the frontiers touch. **Baby-step giant-step** solves `aˣ ≡ b` in `O(√m)`.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]] · Next: [[DSA/07 - String Algorithms/01 - String Matching|String Matching]]
- [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]]: subset sum and knapsack when the values are small
- [[DSA/06 - Algorithm Design Paradigms/03 - Backtracking|Backtracking]]: enumerating subsets
- [[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]] and [[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]]: the combine step
- [[DSA/02 - Linear Data Structures/06 - Hash Tables|Hash Tables]]: pair sums, baby steps
- [[DSA/05 - Graphs/01 - Graph Representations and Traversals|Graph Representations and Traversals]]: BFS
- [[DSA/01 - Foundations/04 - Math for Algorithms|Math for Algorithms]]: modular arithmetic for the discrete logarithm
