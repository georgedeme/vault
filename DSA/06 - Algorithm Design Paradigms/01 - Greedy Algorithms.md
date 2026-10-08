# Greedy Algorithms

A <span class="hl-blue">greedy algorithm</span> builds a solution one decision at a time, always taking the option that looks best **right now** and never revisiting a decision. When it works, it's usually the simplest and fastest solution available: often just a sort followed by a single scan. The hard part isn't the code but knowing **whether** greedy works: many plausible greedy rules are wrong, and a wrong greedy passes the sample tests and fails on a hidden case.

This note covers the two properties that make greedy correct, the two standard proof techniques (greedy stays ahead, exchange argument), and the classic families: interval scheduling and covering, job scheduling, fractional knapsack, Huffman coding, coin systems, and a catalogue of array/string greedy problems. A whole section collects the cases where greedy **fails**, with the counterexample for each, because recognising those is as important as knowing the algorithms.

## Contents

- [[#1. What Makes a Problem Greedy-Solvable|1. What Makes a Problem Greedy-Solvable]]
- [[#2. Proving a Greedy Algorithm Correct|2. Proving a Greedy Algorithm Correct]]
- [[#3. Interval Scheduling|3. Interval Scheduling]]
- [[#4. Job Scheduling|4. Job Scheduling]]
- [[#5. Fractional Knapsack|5. Fractional Knapsack]]
- [[#6. Huffman Coding|6. Huffman Coding]]
- [[#7. Coin Change and Canonical Coin Systems|7. Coin Change and Canonical Coin Systems]]
- [[#8. Greedy on Arrays and Strings|8. Greedy on Arrays and Strings]]
- [[#9. When Greedy Fails|9. When Greedy Fails]]
- [[#10. Common Mistakes|10. Common Mistakes]]
- [[#11. Trick Questions and Special Cases|11. Trick Questions and Special Cases]]
- [[#12. Quick Reference — Non-Obvious Outcomes|12. Quick Reference — Non-Obvious Outcomes]]
- [[#13. Summary|13. Summary]]

---

## 1. What Makes a Problem Greedy-Solvable

> [!note] The two properties
> - <span class="hl-blue">Greedy-choice property</span>: some optimal solution begins with the choice the greedy rule makes. So committing to it never rules out reaching an optimum.
> - <span class="hl-blue">Optimal substructure</span>: after making that choice, what remains is a smaller instance of the same problem, and an optimal solution to it, combined with the choice, is optimal overall.

Dynamic programming needs optimal substructure too. The difference is the first property: DP tries **every** choice for the next step and keeps the best ([[DSA/06 - Algorithm Design Paradigms/04 - Dynamic Programming Fundamentals|Dynamic Programming — Fundamentals]]); greedy tries **one** and has to be sure it's safe.

Most greedy algorithms have this shape:

```
greedy(candidates):
    sort candidates by some key            -- the whole art is choosing this key
    solution = empty
    for c in candidates:
        if solution + c is still feasible:
            solution = solution + c
    return solution
```

| | Greedy | Dynamic programming |
|---|---|---|
| Choices examined per step | one | all |
| Typical cost | `O(n log n)` (a sort) or `O(n)` | states × transitions |
| Correctness | needs a proof; wrong rules look plausible | follows from the recurrence |
| When it fails | gives a wrong answer silently | doesn't fail, just slower |

> [!tip] Practical check before trusting a greedy rule
> Write a brute force (try all orders / all subsets) for inputs of size ≤ 8, and compare it with the greedy on a few thousand random small inputs. A wrong greedy rule almost always fails within seconds, and the failing input is the counterexample you need. This is faster than trying to prove a rule that turns out to be false.

---

## 2. Proving a Greedy Algorithm Correct

You rarely write proofs in an interview, but knowing the two shapes tells you **why** a rule works, and the attempt to apply them is usually how you find out that a rule doesn't.

### 2.1 Greedy stays ahead

Show that after every step, the greedy solution is at least as good as any other solution after the same number of steps, measured by some quantity. Then it can't end up worse.

**Example (activity selection, [[#3.1 Activity selection: the most non-overlapping intervals|§3.1]])**: greedy picks intervals by earliest end time. Let `g₁, g₂, …` be greedy's picks and `o₁, o₂, …` any other valid selection, both sorted by end time. Claim: `end(gₖ) ≤ end(oₖ)` for every `k`. For `k = 1` it holds because `g₁` has the earliest end of all. If it holds for `k`, then `oₖ₊₁` starts after `end(oₖ) ≥ end(gₖ)`, so `oₖ₊₁` was still available to greedy at step `k + 1`, and greedy picked something ending no later. So greedy is never behind, and if the other selection had more intervals, greedy would have had room for one more too.

### 2.2 Exchange argument

Take any optimal solution that differs from the greedy one. Find the first place they disagree and **swap** a piece of the optimal solution to match greedy, showing the result is no worse. Repeating the swap turns the optimal solution into the greedy one without losing quality, so greedy is optimal.

**Example (minimise the total completion time, [[#4.1 Minimise total completion time: shortest job first|§4.1]])**: suppose an optimal order has two **adjacent** jobs with the longer one first, durations `a > b`. If the pair starts at time `T`, its finish times are `T + a` and `T + a + b`; after swapping they're `T + b` and `T + a + b`. Every other job finishes when it did before, so the total strictly drops by `a − b`. So an optimal order has no such adjacent inversion, which means it's sorted by duration.

![[Greedy - Exchange Argument.excalidraw|800]]

> [!info]- Matroids: when greedy is always optimal (advanced)
> A <span class="hl-blue">matroid</span> is a family of "independent" subsets of a ground set such that every subset of an independent set is independent, and any smaller independent set can be extended by some element of a larger one (the exchange property). Theorem (Rado–Edmonds): "sort by weight, add the element if the set stays independent" finds a maximum-weight independent set **for every weight function** exactly when the family is a matroid. Forests of a graph form a matroid (that's why Kruskal works, [[DSA/05 - Graphs/04 - Minimum Spanning Trees|Minimum Spanning Trees]]); so do linearly independent sets of vectors, and sets of unit jobs that can all meet their deadlines ([[#4.3 Unit jobs with deadlines and profits|§4.3]]). 0/1 knapsack feasibility isn't a matroid, which is why greedy fails there.

---

## 3. Interval Scheduling

Throughout this section intervals are `[start, end]`. Whether two intervals that **touch** (`[1, 2]` and `[2, 3]`) overlap is decided by the problem, and it's the single most common source of off-by-one errors: it flips a `<` into `<=`.

### 3.1 Activity selection: the most non-overlapping intervals

Choose as many pairwise non-overlapping intervals as possible.

```
activitySelection(intervals):
    sort intervals by end time
    count = 0; lastEnd = −∞
    for [s, e] in intervals:
        if s ≥ lastEnd:                  -- touching allowed; use s > lastEnd if it isn't
            count = count + 1
            lastEnd = e
    return count
```

```java
static int maxNonOverlapping(int[][] intervals) {
    int[][] iv = intervals.clone();
    Arrays.sort(iv, (x, y) -> Integer.compare(x[1], y[1]));   // by END time
    int count = 0;
    long lastEnd = Long.MIN_VALUE;                 // below every int, so the first interval is taken
    for (int[] x : iv)
        if (x[0] >= lastEnd) { count++; lastEnd = x[1]; }
    return count;
}
```

Why the earliest **end**: it leaves the most room for everything after it ([[#2.1 Greedy stays ahead|§2.1]]). The other natural keys are all wrong:

| Sort key | Counterexample | Greedy | Optimal |
|---|---|---|---|
| Earliest start | `[0, 10], [1, 2], [3, 4]` | 1 (takes `[0, 10]`) | 2 |
| Shortest length | `[0, 5], [4, 7], [6, 11]` | 1 (takes `[4, 7]`, which blocks both) | 2 |
| Fewest overlaps with others | `[0,3) [3,6) [6,9) [9,12)`, `[5,7)`, 3 × `[2,4)`, 3 × `[8,10)` | 3 (takes `[5,7)`, 2 overlaps) | 4 |
| **Earliest end** | none: provably optimal | | |

![[Greedy - Interval Scheduling Keys.excalidraw|800]]

### 3.2 Minimum removals to make intervals non-overlapping

The fewest intervals to delete is `n − (most you can keep)`, so it's §3.1 again. Here touching intervals don't overlap.

```java
static int eraseOverlapIntervals(int[][] intervals) {
    return intervals.length - maxNonOverlapping(intervals);
}
```

`[[1, 2], [2, 3], [3, 4], [1, 3]]` → `1`; `[[1, 2], [1, 2], [1, 2]]` → `2`; `[[1, 2], [2, 3]]` → `0`.

### 3.3 Minimum arrows to burst balloons

Balloons are intervals on the x-axis; an arrow shot at `x` bursts every balloon with `start ≤ x ≤ end`. Here **touching balloons share a point**, so one arrow gets both. Sort by end and shoot each arrow at the end of the first balloon it hasn't covered yet: that point is as far right as possible while still bursting that balloon.

```java
static int findMinArrowShots(int[][] points) {
    if (points.length == 0) return 0;
    int[][] p = points.clone();
    Arrays.sort(p, (x, y) -> Integer.compare(x[1], y[1]));     // NOT x[1] - y[1]: it overflows
    int arrows = 1;
    int arrowAt = p[0][1];
    for (int[] b : p)
        if (b[0] > arrowAt) { arrows++; arrowAt = b[1]; }      // strictly after: touching is covered
    return arrows;
}
```

`[[10, 16], [2, 8], [1, 6], [7, 12]]` → `2`; `[[1, 2], [3, 4], [5, 6], [7, 8]]` → `4`; `[[1, 2], [2, 3], [3, 4], [4, 5]]` → `2`. The values range over all of `int`, so `[[-2147483646, -2147483645], [2147483646, 2147483647]]` breaks a subtraction comparator: `x[1] − y[1]` overflows and the sort comes out wrong.

> [!warning] Same algorithm, different boundary
> §3.2 keeps an interval when `start >= lastEnd` (touching is fine); §3.3 needs a new arrow when `start > arrowAt` (touching is covered). Copying the condition from one problem to the other gives off-by-one answers on exactly the touching cases.

### 3.4 Weighted intervals: greedy fails, DP works

If each interval has a **profit** and the goal is maximum total profit, no greedy key works: a single long, very profitable interval can beat many short ones, and the reverse. Sort by end time and use DP: `best[i]` (the best using the first `i` intervals) either skips interval `i`, or takes it plus the best among the intervals that end by its start, found by binary search.

```java
static int jobScheduling(int[] start, int[] end, int[] profit) {
    int n = start.length;
    Integer[] idx = new Integer[n];
    for (int i = 0; i < n; i++) idx[i] = i;
    Arrays.sort(idx, (a, b) -> Integer.compare(end[a], end[b]));
    int[] ends = new int[n];
    for (int i = 0; i < n; i++) ends[i] = end[idx[i]];
    int[] best = new int[n + 1];                   // best[i]: max profit using the first i jobs (by end)
    for (int i = 1; i <= n; i++) {
        int j = idx[i - 1];
        int k = upperBound(ends, i - 1, start[j]); // jobs among the first i-1 that end ≤ start[j]
        best[i] = Math.max(best[i - 1], best[k] + profit[j]);
    }
    return best[n];
}

static int upperBound(int[] a, int hi, int x) {   // first index in a[0..hi) with a[idx] > x
    int lo = 0;
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (a[mid] <= x) lo = mid + 1; else hi = mid;
    }
    return lo;
}
```

`start = [1, 2, 3, 3]`, `end = [3, 4, 5, 6]`, `profit = [50, 10, 40, 70]` → `120` (jobs 1 and 4). Earliest-end greedy takes jobs 1 and 3 for 90. `O(n log n)`. [[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]] covers the `upperBound` variant used here.

### 3.5 Interval partitioning: the fewest rooms

Assign every interval to a room so that no room has two overlapping intervals, using as few rooms as possible. The answer is the **depth**: the largest number of intervals overlapping at a single point. Greedy achieves it: process by start time and reuse any room that's already free (a min-heap of room end times). The code is in [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues#8.1 Meeting rooms: minimum number of rooms|Heaps § 8.1]], and the sweep-line version in [[DSA/08 - Specialized Topics/01 - Intervals and Sweep Line|Intervals and Sweep Line]].

The depth is a lower bound for any assignment (those intervals need different rooms), and greedy opens a new room only when every open room is busy at the current start time, meaning that many intervals overlap there. So greedy matches the lower bound.

### 3.6 Covering a range with the fewest intervals

**Video stitching**: choose the fewest clips `[s, e]` that together cover `[0, time]`. Among the clips that start at or before the current covered end, take the one that reaches furthest. This is [[#8.1 Jump game I and II|jump game II]] in disguise.

```
cover(clips, time):
    covered = 0; count = 0
    while covered < time:
        best = max end among clips with start ≤ covered
        if best ≤ covered: return −1          -- a gap nobody covers
        covered = best; count = count + 1
    return count
```

```java
static int videoStitching(int[][] clips, int time) {
    int[] reach = new int[time + 1];               // reach[s]: furthest end of a clip starting at s
    for (int[] c : clips) if (c[0] <= time) reach[c[0]] = Math.max(reach[c[0]], c[1]);
    int count = 0, coveredTo = 0, farthest = 0;
    for (int t = 0; t < time; t++) {
        farthest = Math.max(farthest, reach[t]);
        if (t == coveredTo) {                      // need another clip to get past t
            if (farthest <= t) return -1;
            count++;
            coveredTo = farthest;
        }
    }
    return count;
}
```

`[[0, 2], [4, 6], [8, 10], [1, 9], [1, 5], [5, 9]]`, `time = 10` → `3` (`[0, 2]`, `[1, 9]`, `[8, 10]`); `[[0, 1], [1, 2]]`, `time = 5` → `−1`. Taking the **longest** clip first is wrong: what matters is how far a clip reaches, given that it has to start inside the part already covered.

---

## 4. Job Scheduling

### 4.1 Minimise total completion time: shortest job first

`n` jobs with durations `t[i]` run one after another; minimise the sum of their completion times (equivalently, the average waiting time). Sort by duration ascending: the exchange argument is in [[#2.2 Exchange argument|§2.2]].

```java
static long totalCompletionTime(int[] t) {
    int[] s = t.clone();
    Arrays.sort(s);
    long clock = 0, total = 0;
    for (int d : s) { clock += d; total += clock; }
    return total;
}
```

`[3, 1, 2]` → `10` (finishing at 1, 3, 6); the given order would finish at 3, 4, 6 for `13`.

**With weights** (minimise `Σ wᵢ·Cᵢ`): sort by `tᵢ / wᵢ` ascending (<span class="hl-blue">Smith's rule</span>). Compare by cross-multiplying, `t[a]·w[b]` vs. `t[b]·w[a]` in `long`, rather than dividing: no rounding and no division by zero.

### 4.2 Minimise the maximum lateness: earliest deadline first

Each job has a duration and a deadline; lateness is `max(0, finish − deadline)`. To minimise the **largest** lateness, run jobs in order of deadline, ignoring durations entirely. Exchange argument: an adjacent pair with the later deadline first can be swapped without increasing the maximum lateness.

```java
static long minMaxLateness(int[][] jobs) {         // {duration, deadline}
    int[][] j = jobs.clone();
    Arrays.sort(j, (a, b) -> Integer.compare(a[1], b[1]));
    long clock = 0, worst = 0;
    for (int[] x : j) {
        clock += x[0];
        worst = Math.max(worst, clock - x[1]);
    }
    return worst;
}
```

`[[3, 6], [2, 8], [1, 9], [4, 9], [3, 14], [2, 15]]` → `1`. Shortest-first would be wrong here: it optimises the sum of finish times, not the worst lateness.

### 4.3 Unit jobs with deadlines and profits

Each job takes one time unit and earns its profit only if it finishes by its deadline. Process jobs by deadline; keep the profits of the jobs accepted so far in a **min-heap**. If accepting a job means more jobs than time slots up to its deadline, drop the least profitable job accepted so far.

```java
static long maxProfitUnitJobs(int[][] jobs) {      // {deadline, profit}
    int[][] j = jobs.clone();
    Arrays.sort(j, (a, b) -> Integer.compare(a[0], b[0]));
    PriorityQueue<Integer> kept = new PriorityQueue<>();      // profits of scheduled jobs
    for (int[] x : j) {
        kept.offer(x[1]);
        if (kept.size() > x[0]) kept.poll();      // only x[0] slots end by this deadline
    }
    long sum = 0;
    for (int p : kept) sum += p;
    return sum;
}
```

`[[4, 20], [1, 10], [1, 40], [1, 30]]` → `60` (the 40 job, then the 20 job); `[[2, 100], [1, 19], [2, 27], [1, 25], [3, 15]]` → `142`. The textbook version sorts by profit descending and places each job in the latest free slot before its deadline, `O(n · maxDeadline)` or `O(n α(n))` with union-find over free slots ([[DSA/04 - Trees and Hierarchical Structures/06 - Union-Find|Union-Find]]).

### 4.4 The most courses: commit, then evict the longest

**Course schedule III**: course `i` takes `d` days and must be finished by day `last`. Process courses by `last`; take each one tentatively, and if the running total passes its deadline, drop the **longest** course taken so far (a max-heap). Dropping the longest frees the most time while lowering the count by the same one course.

```java
static int scheduleCourse(int[][] courses) {       // {duration, lastDay}
    int[][] c = courses.clone();
    Arrays.sort(c, (a, b) -> Integer.compare(a[1], b[1]));
    PriorityQueue<Integer> taken = new PriorityQueue<>(Collections.reverseOrder());
    int time = 0;
    for (int[] x : c) {
        time += x[0];
        taken.offer(x[0]);
        if (time > x[1]) time -= taken.poll();     // drop the longest (maybe the one just added)
    }
    return taken.size();
}
```

`[[100, 200], [200, 1300], [1000, 1250], [2000, 3200]]` → `3`; `[[3, 2], [4, 3]]` → `0`. The same "commit tentatively, evict the worst" pattern is in [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues#8.4 Keep the best `k` choices, revise as you go|Heaps § 8.4]].

---

## 5. Fractional Knapsack

Items have a value and a weight, and **fractions** of an item may be taken. Sort by value per unit of weight, take whole items while they fit, then the fitting fraction of the next one.

```java
static double fractionalKnapsack(int[] value, int[] weight, int capacity) {
    Integer[] idx = new Integer[value.length];
    for (int i = 0; i < idx.length; i++) idx[i] = i;
    Arrays.sort(idx, (a, b) -> Long.compare((long) value[b] * weight[a], (long) value[a] * weight[b]));  // ratio, descending
    double total = 0;
    int left = capacity;
    for (int i : idx) {
        if (left == 0) break;
        int take = Math.min(left, weight[i]);
        total += (double) value[i] * take / weight[i];
        left -= take;
    }
    return total;
}
```

Values `[60, 100, 120]`, weights `[10, 20, 30]`, capacity `50` → `240.0` (the first two whole, then `20/30` of the third).

> [!warning] The same greedy on **0/1** knapsack is wrong
> With whole items only, ratio order takes the 60 and the 100 items (weight 30), and the 120 item no longer fits: `160`. The optimum is `100 + 120 = 220`. Greedy fails because the leftover capacity is wasted; fractions are what make the greedy-choice property hold. 0/1 knapsack needs DP ([[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]]).

---

## 6. Huffman Coding

A <span class="hl-blue">prefix code</span> gives each symbol a bit string so that no code is a prefix of another, so a bit stream decodes unambiguously without separators. Prefix codes correspond to binary trees: symbols are leaves, `0` means left and `1` means right, and a symbol's code length is its depth. The cost of encoding a text is `Σ freq(s) · depth(s)`. <span class="hl-blue">Huffman coding</span> finds the tree with minimum cost.

```
huffman(freq):
    put one leaf per symbol into a min-heap keyed by frequency
    while the heap has more than one tree:
        x = extractMin(); y = extractMin()
        insert a new node with children x, y and frequency freq(x) + freq(y)
    return the remaining tree
```

![[Greedy - Huffman Tree.excalidraw|800]]

The total cost equals the **sum of all merged frequencies**: each merge adds one bit to every symbol below it, and those symbols' frequencies add up to the merged node's frequency. So the cost alone needs no tree:

```java
static long huffmanCost(int[] freq) {
    PriorityQueue<Long> pq = new PriorityQueue<>();
    for (int f : freq) pq.offer((long) f);
    long cost = 0;
    while (pq.size() > 1) {
        long merged = pq.poll() + pq.poll();
        cost += merged;
        pq.offer(merged);
    }
    return cost;
}
```

Building the actual codes needs nodes:

```java
static class HNode {
    final long freq; final char sym; final HNode left, right;
    HNode(long f, char s, HNode l, HNode r) { freq = f; sym = s; left = l; right = r; }
}

static Map<Character, String> huffmanCodes(char[] syms, int[] freq) {
    PriorityQueue<HNode> pq = new PriorityQueue<>((a, b) -> Long.compare(a.freq, b.freq));
    for (int i = 0; i < syms.length; i++) pq.offer(new HNode(freq[i], syms[i], null, null));
    while (pq.size() > 1) {
        HNode x = pq.poll(), y = pq.poll();
        pq.offer(new HNode(x.freq + y.freq, '\0', x, y));
    }
    Map<Character, String> codes = new TreeMap<>();
    assign(pq.poll(), "", codes);
    return codes;
}

static void assign(HNode n, String code, Map<Character, String> codes) {
    if (n == null) return;
    if (n.left == null && n.right == null) {
        codes.put(n.sym, code.isEmpty() ? "0" : code);   // a lone symbol still needs one bit
        return;
    }
    assign(n.left, code + "0", codes);
    assign(n.right, code + "1", codes);
}
```

Frequencies `a:5, b:9, c:12, d:13, e:16, f:45` give `f` a 1-bit code, `c`, `d`, `e` 3-bit codes and `a`, `b` 4-bit codes, for `224` bits in total (a fixed 3-bit code needs `300`). `O(n log n)` with a heap; if the frequencies arrive **sorted**, two queues (leaves, and merged nodes, which come out in non-decreasing order) give `O(n)`.

> [!info]- Why merging the two rarest is safe
> **Greedy choice**: in some optimal tree, the two least frequent symbols `x` and `y` are siblings at the deepest level. Take any optimal tree; its deepest level has two sibling leaves (a full binary tree's deepest leaf has a sibling). Swapping `x` and `y` into those positions moves less frequent symbols deeper and more frequent ones shallower, which can't increase the cost.
> **Optimal substructure**: replace `x` and `y` with one symbol of frequency `freq(x) + freq(y)`. Any tree for the smaller alphabet, with that leaf expanded into `x` and `y`, costs exactly `freq(x) + freq(y)` more. So an optimal tree for the smaller problem gives an optimal tree for the original.

The same merge rule solves **minimum cost to connect sticks** ([[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues#8.3 Always combine the two smallest|Heaps § 8.3]]) and "merge files with minimum total cost".

> [!warning] Huffman needs the merged node to go back into the pool
> Sorting the frequencies once and merging left to right (the running total with the next smallest) is **not** Huffman. On `[5, 5, 6, 6]`, left to right merges `5 + 5 = 10`, `10 + 6 = 16`, `16 + 6 = 22` for a cost of `48`; Huffman merges `5 + 5`, then `6 + 6` (both smaller than 10), then `10 + 12`, for `10 + 12 + 22 = 44`. Only the heap version is optimal.

---

## 7. Coin Change and Canonical Coin Systems

"Make `amount` with the fewest coins" by repeatedly taking the largest coin that fits works for euro and US coins, but not for coin systems in general.

```java
static int greedyCoins(int[] coins, int amount) {  // coins sorted ascending; -1 if greedy gets stuck
    int count = 0;
    for (int i = coins.length - 1; i >= 0 && amount > 0; i--) {
        count += amount / coins[i];
        amount %= coins[i];
    }
    return amount == 0 ? count : -1;
}
```

| Coins | Amount | Greedy | Optimal |
|---|---|---|---|
| `{1, 5, 10, 25}` | 30 | `25 + 5` → 2 | 2 |
| `{1, 3, 4}` | 6 | `4 + 1 + 1` → 3 | `3 + 3` → 2 |
| `{1, 10, 25}` (no 5) | 30 | `25 + 1·5` → 6 | `10·3` → 3 |
| `{3, 5}` | 9 | `5`, then 4 is stuck → **fails** | `3·3` → 3 |

A coin system where greedy is always optimal is <span class="hl-blue">canonical</span>. Whether a system is canonical can be checked: if it isn't, the smallest counterexample is below the sum of the two largest coins (Kozen–Zaks), so comparing greedy with the DP for every amount up to that bound settles it. In general, use the DP ([[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]]).

---

## 8. Greedy on Arrays and Strings

### 8.1 Jump game I and II

`a[i]` is the longest jump from index `i`. **I**: can you reach the last index? Track the furthest index reachable so far; if the scan ever gets past it, you're stuck.

```java
static boolean canJump(int[] a) {
    int reach = 0;
    for (int i = 0; i < a.length; i++) {
        if (i > reach) return false;               // i itself can't be reached
        reach = Math.max(reach, i + a[i]);
    }
    return true;
}
```

**II**: the fewest jumps (the last index is guaranteed reachable). Think of it as BFS where level `k` is the range of indices reachable in exactly `k` jumps; the next level ends at the furthest index any position in the current level can jump to.

```
jump(a):
    jumps = 0; levelEnd = 0; farthest = 0
    for i = 0 .. n−2:
        farthest = max(farthest, i + a[i])
        if i = levelEnd:                     -- leaving the current level
            jumps = jumps + 1
            levelEnd = farthest
    return jumps
```

```java
static int jump(int[] a) {
    int jumps = 0, levelEnd = 0, farthest = 0;
    for (int i = 0; i < a.length - 1; i++) {       // n − 1: no jump is needed FROM the last index
        farthest = Math.max(farthest, i + a[i]);
        if (i == levelEnd) { jumps++; levelEnd = farthest; }
    }
    return jumps;
}
```

![[Greedy - Jump Game Levels.excalidraw|800]]

`canJump([2, 3, 1, 1, 4])` → `true`, `canJump([3, 2, 1, 0, 4])` → `false`; `jump([2, 3, 1, 1, 4])` → `2`; `jump([0])` → `0`. "Always jump as far as possible" is the tempting wrong greedy: on `[2, 3, 1, 1, 4]` it goes `0 → 2 → 3 → 4`, three jumps.

### 8.2 Gas station

Station `i` gives `gas[i]` fuel and driving to station `i + 1` costs `cost[i]`, around a circle. Find the starting station from which the full loop is possible (the answer is unique if it exists).

```java
static int canCompleteCircuit(int[] gas, int[] cost) {
    int total = 0, tank = 0, start = 0;
    for (int i = 0; i < gas.length; i++) {
        int d = gas[i] - cost[i];
        total += d;
        tank += d;
        if (tank < 0) { start = i + 1; tank = 0; }   // nobody in start..i can be the answer
    }
    return total >= 0 ? start : -1;
}
```

`gas = [1, 2, 3, 4, 5]`, `cost = [3, 4, 5, 1, 2]` → `3`; `gas = [2, 3, 4]`, `cost = [3, 4, 3]` → `−1`.

> [!info]- Why skipping the whole failed stretch is safe, and why `total ≥ 0` is enough
> Suppose starting at `s` the tank first goes negative after station `i`. Any start `k` between `s` and `i` arrives at `k` (when starting from `s`) with a tank `≥ 0`, so starting **at** `k` with an empty tank is no better: it also runs dry by `i`. So the next candidate is `i + 1`.
> If `total ≥ 0`, the final `start` works. From `start` to the end of the array the tank never goes negative (otherwise `start` would have been reset), and it arrives back at station 0 holding `S`, the sum of `start..n−1`. The part before `start` is a series of failed stretches, each with a negative total but non-negative partial sums, so every prefix of that part sums to **at least** the whole part, `total − S`. The tank along it is therefore at least `S + (total − S) = total ≥ 0`.

### 8.3 Candy: two passes

Children in a row have ratings; each gets at least one candy, and a child with a higher rating than a **neighbour** gets more than that neighbour. Minimise the total. Satisfy the left-neighbour rule in one pass and the right-neighbour rule in a second pass, keeping the maximum.

```java
static int candy(int[] r) {
    int n = r.length;
    int[] c = new int[n];
    Arrays.fill(c, 1);
    for (int i = 1; i < n; i++) if (r[i] > r[i - 1]) c[i] = c[i - 1] + 1;
    for (int i = n - 2; i >= 0; i--) if (r[i] > r[i + 1]) c[i] = Math.max(c[i], c[i + 1] + 1);
    int sum = 0;
    for (int x : c) sum += x;
    return sum;
}
```

`[1, 0, 2]` → `5`; `[1, 2, 2]` → `4` (equal neighbours have no constraint: `1, 2, 1`); `[1, 2, 87, 87, 87, 2, 1]` → `13`. A single pass can't work: a long decreasing run to the right forces a large value that the left pass hasn't seen yet.

### 8.4 Matching small to small: cookies and boats

**Assign cookies**: child `i` is content with a cookie of size `≥ g[i]`. Sort both; give each cookie, smallest first, to the least greedy child it satisfies.

```java
static int findContentChildren(int[] g, int[] s) {
    int[] gs = g.clone(), ss = s.clone();
    Arrays.sort(gs); Arrays.sort(ss);
    int child = 0;
    for (int cookie = 0; cookie < ss.length && child < gs.length; cookie++)
        if (ss[cookie] >= gs[child]) child++;
    return child;
}
```

**Boats to save people**: each boat carries at most two people with total weight `≤ limit`. The heaviest person must go in some boat; pair them with the lightest if possible (if the lightest doesn't fit with them, nobody does).

```java
static int numRescueBoats(int[] people, int limit) {
    int[] p = people.clone();
    Arrays.sort(p);
    int boats = 0;
    for (int lo = 0, hi = p.length - 1; lo <= hi; hi--, boats++)
        if (p[lo] + p[hi] <= limit) lo++;          // the lightest rides along
    return boats;
}
```

`findContentChildren([1, 2, 3], [1, 1])` → `1`; `([1, 2], [1, 2, 3])` → `2`. `numRescueBoats([3, 2, 2, 1], 3)` → `3`; `([3, 5, 3, 4], 5)` → `4`. With **more than two** people per boat this greedy is wrong: that's bin packing, which is NP-hard.

### 8.5 Partition labels

Split a string into as many parts as possible so that each letter appears in at most one part. Record each letter's last index; a part can end at `i` once `i` reaches the last occurrence of every letter seen in the part.

```java
static List<Integer> partitionLabels(String s) {
    int[] last = new int[26];
    for (int i = 0; i < s.length(); i++) last[s.charAt(i) - 'a'] = i;
    List<Integer> sizes = new ArrayList<>();
    int start = 0, end = 0;
    for (int i = 0; i < s.length(); i++) {
        end = Math.max(end, last[s.charAt(i) - 'a']);
        if (i == end) { sizes.add(end - start + 1); start = i + 1; }
    }
    return sizes;
}
```

`"ababcbacadefegdehijhklij"` → `[9, 7, 8]`; `"eccbbbbdec"` → `[10]`.

### 8.6 Largest number from concatenation

Arrange non-negative integers to form the largest number. Order `a` before `b` when the string `a + b` is larger than `b + a`.

```java
static String largestNumber(int[] nums) {
    String[] s = new String[nums.length];
    for (int i = 0; i < nums.length; i++) s[i] = String.valueOf(nums[i]);
    Arrays.sort(s, (a, b) -> (b + a).compareTo(a + b));
    if (s[0].equals("0")) return "0";              // all zeros
    return String.join("", s);
}
```

`[10, 2]` → `"210"`; `[3, 30, 34, 5, 9]` → `"9534330"`; `[0, 0]` → `"0"`, not `"00"`. Sorting the strings in plain descending order fails: `"30" > "3"`, but `"330" > "303"`, so `3` must come first. (This comparator is transitive, which is a real theorem, not obvious; it's what makes sorting with it legal.)

### 8.7 Remove k digits for the smallest number

Remove `k` digits from a number string to make the result as small as possible. A digit should go if the digit after it is smaller: a monotonic stack ([[DSA/02 - Linear Data Structures/04 - Stacks|Stacks]]) keeps the digits non-decreasing.

```java
static String removeKdigits(String num, int k) {
    StringBuilder st = new StringBuilder();        // used as a stack
    for (char c : num.toCharArray()) {
        while (k > 0 && st.length() > 0 && st.charAt(st.length() - 1) > c) {
            st.deleteCharAt(st.length() - 1);
            k--;
        }
        st.append(c);
    }
    st.setLength(st.length() - k);                 // still k left: drop from the (largest) end
    int i = 0;
    while (i < st.length() - 1 && st.charAt(i) == '0') i++;   // strip leading zeros, keep one digit
    return st.length() == 0 ? "0" : st.substring(i);
}
```

`("1432219", 3)` → `"1219"`; `("10200", 1)` → `"200"`; `("10", 2)` → `"0"`; `("12345", 2)` → `"123"` (nothing is popped during the scan, so the last two digits go).

### 8.8 Task scheduler: a formula from the greedy picture

Tasks (letters) each take one slot, and two equal letters need at least `n` slots between them. Lay out the most frequent letter first: with count `maxCount`, it creates `maxCount − 1` full frames of length `n + 1`, plus a final partial frame holding every letter tied for the maximum. Other letters fill the idle slots; if they overflow the frames, no idling is needed at all.

```java
static int leastInterval(char[] tasks, int n) {
    int[] cnt = new int[26];
    for (char t : tasks) cnt[t - 'A']++;
    int maxCount = 0, numMax = 0;
    for (int c : cnt) {
        if (c > maxCount) { maxCount = c; numMax = 1; }
        else if (c == maxCount) numMax++;
    }
    return Math.max(tasks.length, (maxCount - 1) * (n + 1) + numMax);
}
```

`AAABBB`, `n = 2` → `8` (`AB_AB_AB`); `n = 0` → `6`; `AAAAAABCDEFG`, `n = 2` → `16`.

### 8.9 More one-liners worth knowing

| Problem | Greedy rule | Example |
|---|---|---|
| Best time to buy and sell stock II (unlimited trades) | add every positive day-to-day difference | `[7, 1, 5, 3, 6, 4]` → `7` |
| Two city scheduling (`2n` people, `n` per city) | sort by `costA − costB`, first half to A | `[[10,20],[30,200],[400,50],[30,20]]` → `110` |
| Queue reconstruction by height | sort by height desc, `k` asc; insert each at index `k` | |
| Lemonade change | for a 20, give `10 + 5` before `5 + 5 + 5` | `[5,5,5,5,10,20,10,10]` → `true` |
| Minimum platforms / meeting rooms | depth of overlap | [[#3.5 Interval partitioning: the fewest rooms|§3.5]] |
| Reorganize string (no equal neighbours) | most frequent remaining letter, except the last used | [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues#8.2 Reorganize a string so no two adjacent letters are equal|Heaps § 8.2]] |

```java
static int maxProfitUnlimited(int[] prices) {
    int profit = 0;
    for (int i = 1; i < prices.length; i++) profit += Math.max(0, prices[i] - prices[i - 1]);
    return profit;
}

static int twoCitySchedCost(int[][] costs) {
    int[][] c = costs.clone();
    Arrays.sort(c, (x, y) -> Integer.compare(x[0] - x[1], y[0] - y[1]));   // most "A-favoured" first
    int total = 0, half = c.length / 2;
    for (int i = 0; i < c.length; i++) total += i < half ? c[i][0] : c[i][1];
    return total;
}

static int[][] reconstructQueue(int[][] people) {  // {height, number of taller-or-equal people in front}
    int[][] p = people.clone();
    Arrays.sort(p, (x, y) -> x[0] != y[0] ? Integer.compare(y[0], x[0]) : Integer.compare(x[1], y[1]));
    List<int[]> q = new ArrayList<>();
    for (int[] x : p) q.add(x[1], x);              // everyone already placed is at least as tall
    return q.toArray(new int[0][]);
}

static boolean lemonadeChange(int[] bills) {
    int fives = 0, tens = 0;
    for (int b : bills) {
        if (b == 5) fives++;
        else if (b == 10) { if (fives == 0) return false; fives--; tens++; }
        else if (tens > 0 && fives > 0) { tens--; fives--; }      // keep fives: they're more useful
        else if (fives >= 3) fives -= 3;
        else return false;
    }
    return true;
}
```

`reconstructQueue([[7,0],[4,4],[7,1],[5,0],[6,1],[5,2]])` → `[[5,0],[7,0],[5,2],[6,1],[4,4],[7,1]]`. In stock II, adding every rise equals buying at each local minimum and selling at the next local maximum; the problem allows selling and buying on the same day, which is what makes the day-by-day sum legal. In lemonade change, giving `5 + 5 + 5` first fails `[5, 5, 5, 5, 10, 20, 10, 10]`: it runs out of fives for the last ten.

### 8.10 Greedy elsewhere in the syllabus

- **Heaps** supply "the best remaining item" for greedy rules: reorganize string, connect sticks, furthest building, IPO ([[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues#8. Greedy Scheduling with Heaps|Heaps § 8]]).
- **Graphs**: Dijkstra (finalise the closest unfinished vertex), Prim and Kruskal (cheapest safe edge) ([[DSA/05 - Graphs/03 - Shortest Path Algorithms|Shortest Path Algorithms]], [[DSA/05 - Graphs/04 - Minimum Spanning Trees|Minimum Spanning Trees]]).
- **Two pointers**: container with most water discards the shorter wall ([[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]]).
- **Binary search on the answer** often uses a greedy feasibility check: "can the packages ship in `D` days with capacity `c`?" fills each day greedily ([[DSA/03 - Sorting and Searching/02 - Binary Search#6.2 Ship packages within D days / split array largest sum (minimise the maximum)|Binary Search § 6.2]]).

---

## 9. When Greedy Fails

| Problem | Tempting greedy | Counterexample | Use instead |
|---|---|---|---|
| 0/1 knapsack | best value/weight first | `[60/10, 100/20, 120/30]`, cap 50: 160 vs 220 | DP |
| Coin change, arbitrary coins | largest coin first | `{1, 3, 4}`, 6: 3 coins vs 2 | DP |
| Weighted interval scheduling | earliest end / highest profit | [[#3.4 Weighted intervals: greedy fails, DP works|§3.4]] | DP + binary search |
| Activity selection | shortest / earliest start | [[#3.1 Activity selection: the most non-overlapping intervals|§3.1]] table | earliest end |
| Jump game II | jump as far as possible | `[2, 3, 1, 1, 4]`: 3 vs 2 | BFS levels |
| Shortest path with negative edges | Dijkstra | `A→B 2, A→C 3, C→B −2` | Bellman-Ford |
| Longest path / TSP | nearest unvisited neighbour | arbitrarily bad | DP over subsets ([[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]]) |
| Maximum sum path in a grid / triangle | best next cell | a small step that leads to a huge value | DP |
| Bin packing, boats with > 2 seats | first fit / heaviest + lightest | NP-hard | search / DP |
| Set cover | most new elements first | only an `ln n` approximation | exact search |
| Max product subarray | extend while it grows | a negative times a negative | DP tracking min and max |

> [!important] The pattern in these failures
> Greedy fails when an early choice **uses up something** (capacity, coins, a slot, the path's freedom) whose value depends on choices not made yet. If the choice can always be "repaired" later by an exchange that loses nothing, greedy is safe.

---

## 10. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Sorting intervals by start for activity selection | too few intervals | sort by **end** |
| `<` vs `<=` on touching intervals | off by one on boundary cases | read whether touching counts as overlap |
| Comparator `a[1] - b[1]` | wrong order near `±2³¹` | `Integer.compare` |
| Greedy for 0/1 knapsack or arbitrary coins | wrong answer on hidden tests | DP |
| Huffman by sorting once | cost too high | heap: merged nodes re-enter the pool |
| Huffman with one symbol | empty code `""` | special-case to `"0"` |
| `jump` looping to `n − 1` inclusive | one extra jump | loop `i < n − 1` |
| Gas station returning `start` without checking `total` | answer when none exists | `total >= 0 ? start : -1` |
| One-pass candy | constraint from the right violated | two passes |
| Largest number `"00"` | not a valid number | return `"0"` when the first is `"0"` |
| Remove k digits: forgetting leftover `k` or leading zeros | `"12345", 2` → `"12345"`; `"0200"` | trim the end; strip zeros; empty → `"0"` |
| Ratio sort by `double` division | precision ties, divide by zero | cross-multiply in `long` |
| Sorting the caller's array in place | caller's data reordered | sort a copy (`clone()`) |
| Trusting a greedy rule because the examples pass | WA on hidden tests | brute-force comparison on small random inputs |

---

## 11. Trick Questions and Special Cases

> [!question]- Activity selection by earliest end and by latest start (scanning right to left): same count?
> Yes. Reversing time turns "ends earliest" into "starts latest", and the problem is symmetric under reversing time. Both are optimal; they may pick different intervals.

> [!question]- `eraseOverlapIntervals([[1, 100], [11, 22], [1, 11], [2, 12]])`?
> `2`. Sorted by end: `[1, 11]`, `[2, 12]`, `[11, 22]`, `[1, 100]`. Keep `[1, 11]`; `[2, 12]` overlaps; `[11, 22]` touches and is kept; `[1, 100]` overlaps. Two kept, two removed.

> [!question]- Do `[1, 2]` and `[2, 3]` need one arrow or two? Should one of them be erased?
> One arrow (an arrow at `x = 2` hits both: balloons are closed intervals). No erasing (in non-overlapping intervals, touching is allowed). Same pair, opposite conventions.

> [!question]- In weighted interval scheduling, why doesn't "highest profit first" work either?
> One high-profit interval can block several that together earn more: `[0, 10]` with profit 10 versus `[0, 5]` and `[5, 10]` with profit 6 each. Highest profit takes 10; the optimum is 12. And earliest end fails the other way (§3.4). No single key works because the trade-off depends on the combination.

> [!question]- Huffman codes for `[2, 2, 1, 1]`: are the code lengths unique?
> No. After merging `1 + 1 = 2`, three trees have frequency 2, and the tie can be broken two ways: lengths `{1, 2, 3, 3}` or `{2, 2, 2, 2}`. Both cost `12`. The **cost** is unique; the tree and the code lengths aren't.

> [!question]- Huffman with a single symbol: how many bits per symbol?
> The tree is one leaf at depth 0, so the formula says 0 bits, but a decoder can't count symbols in an empty stream. Implementations assign the code `"0"` (1 bit per symbol). The heap loop never runs, so `huffmanCost` returns `0`.

> [!question]- Is greedy coin change optimal for `{1, 2, 5, 10, 20, 50}`?
> Yes: the 1-2-5 pattern used by the euro is canonical. But "each coin is at least double the previous" isn't enough in general: `{1, 5, 12}` fails at 15 (`12 + 1 + 1 + 1` is 4 coins, `5 + 5 + 5` is 3). Check, don't assume.

> [!question]- `jump([2, 3, 0, 1, 4])`?
> `2` (`0 → 1 → 4`). The `0` at index 2 doesn't matter because the second level already reaches index 4. `canJump` would also be true.

> [!question]- Gas station: why can the answer be found in one pass even though the route is circular?
> Because of the two facts in §8.2: a failed stretch eliminates all of its starts at once, and `total ≥ 0` guarantees the last candidate succeeds, so the wrap-around part never has to be simulated.

> [!question]- Candy with ratings `[1, 3, 2, 2, 1]`?
> `7`: candies `1, 2, 1, 2, 1`. The two equal ratings don't constrain each other, so the second `2` only has to beat the `1` after it.

> [!question]- `largestNumber([0, 0, 0])` and `largestNumber([0, 1])`?
> `"0"` (not `"000"`), and `"10"`.

> [!question]- `removeKdigits("9", 1)` and `removeKdigits("100", 1)`?
> `"0"` (everything removed), and `"0"` (remove the `1`, leaving `"00"`, which strips to `"0"`).

> [!question]- Task scheduler `AAABBB` with `n = 50`?
> `(3 − 1) · 51 + 2 = 104`. And with tasks `ABCDEFG` (all distinct), `n = 2`: `max(7, 0 · 3 + 7) = 7`, no idling.

> [!question]- Minimum lateness: does shortest-job-first also minimise the maximum lateness?
> No. Jobs `(duration 1, deadline 100)` and `(duration 10, deadline 10)`: shortest first finishes the long job at 11, lateness 1; deadline order finishes it at 10, lateness 0.

> [!question]- Is "pick the locally best move" in a grid path problem greedy-safe?
> Almost never: a cell with a slightly smaller value can lead to a much larger one. Grid path problems are DP ([[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]]).

> [!question]- Stock II with `[1, 2, 3, 4, 5]`: why does summing daily gains (4 transactions) equal one transaction (buy at 1, sell at 5)?
> The daily differences telescope: `(2−1) + (3−2) + (4−3) + (5−4) = 5 − 1`. Same profit, so the "one trade per rise" view is just a way to collect every rising stretch.

---

## 12. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| Activity selection key | earliest **end** | stays ahead |
| `eraseOverlapIntervals([[1,2],[1,2],[1,2]])` | `2` | keep one |
| `findMinArrowShots([[1,2],[2,3],[3,4],[4,5]])` | `2` | touching shares a point |
| Weighted intervals `[1,3,50],[2,4,10],[3,5,40],[3,6,70]` | `120` | DP; greedy gives 90 |
| `videoStitching([[0,1],[1,2]], 5)` | `−1` | gap |
| `totalCompletionTime([3,1,2])` | `10` | shortest first |
| Unit jobs `[[4,20],[1,10],[1,40],[1,30]]` | `60` | min-heap of profits |
| Fractional knapsack 60/10, 100/20, 120/30, cap 50 | `240.0` | 0/1 answer: `220` |
| Huffman cost `5,9,12,13,16,45` | `224` | sum of merges |
| Huffman cost `[x]` (one symbol) | `0` | code `"0"` by convention |
| Greedy coins `{1,3,4}`, 6 | `3` | optimal 2 |
| `jump([2,3,1,1,4])` | `2` | furthest-jump greedy gives 3 |
| Gas `[1,2,3,4,5]`, cost `[3,4,5,1,2]` | `3` | |
| `candy([1,2,87,87,87,2,1])` | `13` | two passes |
| `largestNumber([3,30,34,5,9])` | `"9534330"` | `a+b` vs `b+a` |
| `removeKdigits("10200", 1)` | `"200"` | strip leading zeros |
| `leastInterval(AAABBB, 2)` | `8` | `(3−1)·3 + 2` |

---

## 13. Summary

- Greedy is correct when the locally best choice is always part of **some** optimal solution (greedy-choice property) and the rest is a smaller instance of the same problem (optimal substructure).
- Proofs: **greedy stays ahead** (never behind after `k` steps) and **exchange argument** (swap an optimal solution toward greedy without loss). In practice, test a rule against brute force on small random inputs.
- Intervals: earliest **end** for selection, `n − kept` for removals, end-sorted arrows, depth for rooms, furthest reach for covering. Weighted intervals need DP.
- Scheduling: shortest first minimises total completion time, earliest deadline first minimises maximum lateness, a min-heap of profits or a max-heap of durations handles "commit, then evict".
- Fractional knapsack and Huffman coding are greedy; 0/1 knapsack and arbitrary coin systems aren't.
- Array/string classics: jump game (BFS levels), gas station, candy (two passes), cookies and boats (sorted pairing), partition labels, largest number (`a+b` vs `b+a`), remove k digits (monotonic stack), task scheduler (frame formula).

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/05 - Graphs/09 - Heavy-Light Decomposition|Heavy-Light Decomposition]] · Next: [[DSA/06 - Algorithm Design Paradigms/02 - Divide and Conquer|Divide and Conquer]]
- [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|Heaps and Priority Queues]]: heap-driven greedy scheduling
- [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms|Sorting Algorithms]]: comparators, the first step of most greedy algorithms
- [[DSA/06 - Algorithm Design Paradigms/04 - Dynamic Programming Fundamentals|Dynamic Programming — Fundamentals]]: what to use when greedy fails
- [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]]: 0/1 knapsack and coin change
- [[DSA/05 - Graphs/04 - Minimum Spanning Trees|Minimum Spanning Trees]] and [[DSA/05 - Graphs/03 - Shortest Path Algorithms|Shortest Path Algorithms]]: greedy graph algorithms
- [[DSA/08 - Specialized Topics/01 - Intervals and Sweep Line|Intervals and Sweep Line]]: merging and sweeping intervals
