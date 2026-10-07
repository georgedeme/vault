# Prefix Sums and Difference Arrays

A <span class="hl-blue">prefix sum</span> array stores the running totals `P[i] = a[0] + … + a[i−1]`. After one `O(n)` pass, the sum of **any** subarray is a single subtraction, `P[r + 1] − P[l]`. A <span class="hl-blue">difference array</span> is the inverse: it stores `D[i] = a[i] − a[i−1]`, so adding a value to a whole **range** of `a` changes only two entries of `D`, and one prefix-sum pass rebuilds `a` afterwards.

Together they answer "many range queries, no updates" and "many range updates, then read everything" in `O(1)` each. Combined with a hash map, prefix sums also count and measure subarrays with a given sum, including with negative numbers, which is where sliding windows fail. This note covers 1D and 2D prefix sums, the other operations that work the same way (XOR, counts, parity masks), prefix sums with hashing and with binary search, difference arrays in 1D and 2D, and when to move on to Fenwick and segment trees.

## Contents

- [[#1. The Idea|1. The Idea]]
- [[#2. 1D Prefix Sums|2. 1D Prefix Sums]]
- [[#3. Beyond Sums|3. Beyond Sums]]
- [[#4. 2D Prefix Sums|4. 2D Prefix Sums]]
- [[#5. Prefix Sums with Hash Maps|5. Prefix Sums with Hash Maps]]
- [[#6. Prefix Sums with Binary Search|6. Prefix Sums with Binary Search]]
- [[#7. Difference Arrays|7. Difference Arrays]]
- [[#8. Static vs. Dynamic Data|8. Static vs. Dynamic Data]]
- [[#9. Common Mistakes|9. Common Mistakes]]
- [[#10. Trick Questions and Special Cases|10. Trick Questions and Special Cases]]
- [[#11. Quick Reference — Non-Obvious Outcomes|11. Quick Reference — Non-Obvious Outcomes]]
- [[#12. Summary|12. Summary]]

---

## 1. The Idea

> [!note] Definition
> For an array `a` of length `n`, the prefix sum array `P` has length **`n + 1`**:
> - `P[0] = 0` (the sum of the empty prefix),
> - `P[i + 1] = P[i] + a[i]`, so `P[i]` is the sum of the first `i` elements, `a[0..i)`.
>
> Then the sum of the subarray `a[l..r]` (inclusive) is
>
> **`sum(l, r) = P[r + 1] − P[l]`**
>
> or, with half-open ranges, `sum of a[l..r) = P[r] − P[l]`.

![[Prefix Sums - Range Sum as Difference.excalidraw|800]]

`P[i]` sits **between** elements: it's the total of everything to the left of the boundary before index `i`. A subarray is the stretch between two boundaries, so its sum is the difference of the two totals. Thinking of `P` as boundary values avoids nearly every off-by-one.

> [!tip] Why `P[0] = 0` and length `n + 1`
> With the extra leading zero, `sum(0, r) = P[r + 1] − P[0]` needs no special case. The alternative, `P[i] = a[0] + … + a[i]` with length `n`, makes every query starting at index 0 a special case (`l == 0 ? P[r] : P[r] − P[l − 1]`), a classic source of bugs. In hash-map problems, the same zero is the `count.put(0, 1)` that lets subarrays start at index 0.

| Task | Without prefix sums | With prefix sums |
|---|---|---|
| One range sum | `O(n)` | `O(n)` to build, then `O(1)` |
| `q` range sums | `O(nq)` | `O(n + q)` |
| All `O(n²)` subarray sums | `O(n³)` | `O(n²)` |
| Count subarrays with sum `= k` | `O(n²)` | `O(n)` with a hash map |

---

## 2. 1D Prefix Sums

### 2.1 Build and query

```
build(a):
    P = array of n + 1 zeros
    for i = 0 to n − 1: P[i + 1] = P[i] + a[i]

sum(l, r):                          -- inclusive
    return P[r + 1] − P[l]
```

```java
static long[] prefix(int[] a) {
    long[] p = new long[a.length + 1];           // long: n × max|a[i]| can exceed int
    for (int i = 0; i < a.length; i++) p[i + 1] = p[i] + a[i];
    return p;
}

static long rangeSum(long[] p, int l, int r) {   // a[l..r], inclusive
    return p[r + 1] - p[l];
}
```

> [!warning] Use `long` for the prefix array
> `n = 10⁵` elements of up to `10⁹` sum to `10¹⁴`. Even if every range answer fits in `int`, the **prefix** values may not: and an overflowed `P[r + 1] − P[l]` is not reliably "fixed" by the subtraction once you compare, divide, or use it as a map key. Declare `P` as `long[]`.

`Arrays.stream(a).sum()` is fine for one total, but doesn't give prefixes. `Arrays.parallelPrefix(p, Long::sum)` computes prefix sums in place (inclusive, without the leading zero).

### 2.2 Using the total: pivot index

The **pivot index** is where the sum of elements to the left equals the sum to the right. With the total `T`, the right sum is `T − left − a[i]`, so no array is needed at all.

```java
static int pivotIndex(int[] a) {
    long total = 0, left = 0;
    for (int x : a) total += x;
    for (int i = 0; i < a.length; i++) {
        if (left == total - left - a[i]) return i;    // left sum excludes a[i]
        left += a[i];
    }
    return -1;
}
```

`[1, 7, 3, 6, 5, 6]` → `3`; `[2, 1, −1]` → `0` (the left sum of index 0 is the empty sum, 0, and the right sum is `1 + (−1) = 0`); `[1, 2, 3]` → `−1`. Many "split the array into two parts" problems use the same running-left/total-minus-left pair.

### 2.3 Prefix minimum and maximum

A running minimum of prefix sums turns "best subarray" questions into "best pair of boundaries":

- **Maximum subarray sum** = `max over j` of `P[j] − min(P[0..j−1])`, which is Kadane's algorithm in disguise ([[DSA/02 - Linear Data Structures/01 - Arrays#8.1 Maximum subarray sum (Kadane's algorithm)|Arrays § 8.1]]).
- **Best time to buy and sell a stock** (one transaction) = `max over days` of `price − min(price so far)`:

```java
static int maxProfit(int[] prices) {
    int minSoFar = Integer.MAX_VALUE, best = 0;
    for (int p : prices) {
        minSoFar = Math.min(minSoFar, p);
        best = Math.max(best, p - minSoFar);      // sell today, bought at the cheapest day before
    }
    return best;
}
```

- **Minimum start value** so that a running total `start + a[0] + … + a[i]` never drops below 1: `1 − min(0, min prefix)`.

```java
static int minStartValue(int[] a) {
    int sum = 0, minPrefix = 0;                   // 0: the empty prefix also counts
    for (int x : a) { sum += x; minPrefix = Math.min(minPrefix, sum); }
    return 1 - minPrefix;
}
```

`[-3, 2, -3, 4, 2]` → `5`; `[1, 2]` → `1` (the start must be positive even if no prefix is negative).

### 2.4 Prefix and suffix arrays

When the answer at `i` combines "something about everything left of `i`" with "something about everything right of `i`", precompute both directions:

- **Trapping rain water**: water at `i` = `min(maxLeft[i], maxRight[i]) − h[i]`.

```java
static int trapPrefix(int[] h) {
    int n = h.length;
    if (n == 0) return 0;
    int[] maxL = new int[n], maxR = new int[n];
    maxL[0] = h[0];
    for (int i = 1; i < n; i++) maxL[i] = Math.max(maxL[i - 1], h[i]);   // includes h[i] itself
    maxR[n - 1] = h[n - 1];
    for (int i = n - 2; i >= 0; i--) maxR[i] = Math.max(maxR[i + 1], h[i]);
    int water = 0;
    for (int i = 0; i < n; i++) water += Math.min(maxL[i], maxR[i]) - h[i];
    return water;
}
```

Including `h[i]` in both maxima makes the formula never negative. The two-pointer version needs `O(1)` space ([[DSA/03 - Sorting and Searching/03 - Two Pointers#2.4 Trapping rain water|Two Pointers § 2.4]]).

- **Product of array except self**: prefix products × suffix products ([[DSA/02 - Linear Data Structures/01 - Arrays#8.3 Product of array except self (prefix × suffix)|Arrays § 8.3]]).
- **Maximum sum of two non-overlapping subarrays**: best subarray ending at or before `i` (prefix) plus best starting after `i` (suffix).

### 2.5 Contribution counting: the sum of all subarray sums

Element `a[i]` belongs to every subarray that starts in `[0, i]` and ends in `[i, n − 1]`: `(i + 1)(n − i)` subarrays.

```java
static long sumOfAllSubarraySums(int[] a) {
    long n = a.length, total = 0;
    for (int i = 0; i < n; i++) total += (long) a[i] * (i + 1) * (n - i);
    return total;
}
```

`[1, 2, 3]` → `20` (`1 + 2 + 3 + 3 + 5 + 6`). This "count how many times each element contributes" idea also drives the monotonic-stack sum of subarray minimums ([[DSA/02 - Linear Data Structures/04 - Stacks#9.4 Sum of subarray minimums (contribution technique)|Stacks § 9.4]]). The prefix-sum view: the sum of all `P[r + 1] − P[l]` over `l ≤ r`, computable with a prefix sum **of** prefix sums.

---

## 3. Beyond Sums

The trick works for any operation where a range's value can be recovered from two prefixes, which needs an **inverse** operation.

| Operation | Prefix | Range `[l, r]` | Notes |
|---|---|---|---|
| Sum | `P[i+1] = P[i] + a[i]` | `P[r+1] − P[l]` | |
| XOR | `X[i+1] = X[i] ^ a[i]` | `X[r+1] ^ X[l]` | XOR is its own inverse ([[DSA/01 - Foundations/03 - Bit Manipulation|Bit Manipulation]]) |
| Count of a property | `C[i+1] = C[i] + (a[i] has it ? 1 : 0)` | `C[r+1] − C[l]` | "how many vowels / primes / 1s in the range" |
| Count per letter | `cnt[c][i+1]` for 26 letters | per-letter difference | `O(26n)` memory |
| Parity of each letter | bitmask `M[i+1] = M[i] ^ (1 << c)` | `M[r+1] ^ M[l]` | 26 bits fit in an `int` |
| Product | `Q[i+1] = Q[i] · a[i]` | `Q[r+1] / Q[l]` | **breaks on zeros**; mod a prime, divide with a modular inverse ([[DSA/01 - Foundations/04 - Math for Algorithms|Math for Algorithms]]) |
| Min / max | — | **not invertible** | use a sparse table (`O(1)` query) or a segment tree |

> [!example]- Palindrome queries with a parity mask
> "Can `s[l..r]` be rearranged into a palindrome after changing at most `k` letters?" Only the **parity** of each letter's count matters: a letter with an odd count needs a partner. With `M[i]` = the XOR of `1 << letter` over the first `i` characters, the odd letters in the range are the set bits of `M[r+1] ^ M[l]`, and `odd / 2` changes fix them.
> ```java
> static boolean[] canMakePaliQueries(String s, int[][] queries) {
>     int n = s.length();
>     int[] mask = new int[n + 1];
>     for (int i = 0; i < n; i++) mask[i + 1] = mask[i] ^ (1 << (s.charAt(i) - 'a'));
>     boolean[] res = new boolean[queries.length];
>     for (int q = 0; q < queries.length; q++) {
>         int l = queries[q][0], r = queries[q][1], k = queries[q][2];
>         int odd = Integer.bitCount(mask[r + 1] ^ mask[l]);
>         res[q] = odd / 2 <= k;                     // one odd letter may stay in the middle
>     }
>     return res;
> }
> ```
> `"abcda"`, queries `[3,3,0]` → `true` (one letter), `[1,2,0]` → `false` (`"bc"`), `[0,3,1]` → `false` (`"abcd"`: 4 odd letters need 2 changes), `[0,3,2]` → `true`, `[0,4,1]` → `true` (`"abcda"`: `b, c, d` odd, one change). `O(n + q)` instead of `O(26)` per query with 26 count arrays.

> [!warning] Prefix products and zeros
> One zero makes every later prefix product 0, and `Q[r+1] / Q[l]` divides by zero for any `l` past it. Handle zeros separately (record the position of the last zero; a range containing one has product 0), or split the array at zeros. Also, products overflow fast: use `long` with a modulus, or logarithms when only comparisons are needed.

---

## 4. 2D Prefix Sums

`P[r][c]` = the sum of the rectangle of rows `0..r−1` and columns `0..c−1` (again one extra row and column of zeros). Build by **inclusion–exclusion**: the cell, plus the rectangle above, plus the rectangle to the left, minus their overlap, which was added twice.

```
build:  P[r+1][c+1] = m[r][c] + P[r][c+1] + P[r+1][c] − P[r][c]

query (r1, c1) to (r2, c2), inclusive:
        P[r2+1][c2+1] − P[r1][c2+1] − P[r2+1][c1] + P[r1][c1]
```

```java
static class Matrix2D {
    private final long[][] p;

    Matrix2D(int[][] m) {
        int R = m.length, C = m[0].length;
        p = new long[R + 1][C + 1];
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++)
                p[r + 1][c + 1] = m[r][c] + p[r][c + 1] + p[r + 1][c] - p[r][c];
    }

    long sumRegion(int r1, int c1, int r2, int c2) {
        return p[r2 + 1][c2 + 1] - p[r1][c2 + 1] - p[r2 + 1][c1] + p[r1][c1];
    }
}
```

![[Prefix Sums - 2D Inclusion-Exclusion.excalidraw|800]]

`O(R·C)` to build, `O(1)` per query. The query subtracts the strip above and the strip to the left, then adds back the top-left corner, which both strips removed.

> [!tip] Sum of a fixed-size `k × k` block around every cell
> "Matrix block sum" (`answer[r][c]` = sum of `m` within distance `k`) is one 2D query per cell with clamped corners: `r1 = max(0, r − k)`, `r2 = min(R − 1, r + k)`, and the same for columns. Clamping is the whole difficulty; the prefix array handles the rest.

> [!example]- Count submatrices with sum = target, `O(R²·C)`
> Fix the top and bottom rows. The sums of each column between them form a 1D array; count its subarrays with sum `target` using the hash-map method of [[#5.1 Count subarrays with sum = k|§5.1]].
> ```java
> static int numSubmatrixSumTarget(int[][] m, int target) {
>     int R = m.length, C = m[0].length, res = 0;
>     for (int top = 0; top < R; top++) {
>         int[] col = new int[C];                         // column sums of rows top..bottom
>         for (int bottom = top; bottom < R; bottom++) {
>             for (int c = 0; c < C; c++) col[c] += m[bottom][c];
>             Map<Integer, Integer> count = new HashMap<>();
>             count.put(0, 1);
>             int sum = 0;
>             for (int c = 0; c < C; c++) {
>                 sum += col[c];
>                 res += count.getOrDefault(sum - target, 0);
>                 count.merge(sum, 1, Integer::sum);
>             }
>         }
>     }
>     return res;
> }
> ```
> Choose the smaller dimension for the outer pair (transpose if `R > C`). The same "fix two rows, run a 1D algorithm on column sums" pattern finds the maximum-sum submatrix with Kadane in `O(R²·C)`.

---

## 5. Prefix Sums with Hash Maps

A subarray `a[i..j]` has sum `P[j+1] − P[i]`. So "is there a subarray ending at `j` with property X?" becomes "is there an **earlier prefix** `P[i]` with a matching value?", a hash-map lookup. This works with **negative numbers**, unlike a sliding window.

![[Prefix Sums - Subarray Sum with Hash Map.excalidraw|800]]

| Question | Map key | Map value | Look up |
|---|---|---|---|
| Count subarrays with sum `= k` | prefix sum | how many times seen | `sum − k` |
| Longest subarray with sum `= k` | prefix sum | **first** index seen | `sum − k` |
| Count subarrays with sum divisible by `k` | `floorMod(sum, k)` | count | same remainder |
| Is there a subarray of length `≥ 2` with sum a multiple of `k`? | `sum % k` | first index | same remainder, distance `≥ 2` |
| Longest subarray with equal 0s and 1s | prefix of `±1` | first index | same value |
| Count subarrays with XOR `= k` | prefix XOR | count | `x ^ k` |
| Longest substring with even count of each vowel | parity bitmask | first index | same mask |

> [!important] The seed entry
> Before the loop, put the **empty prefix** in the map: count `0 → 1`, or first index `0 → −1`. It stands for `P[0] = 0`, the boundary before index 0, and lets a subarray that starts at index 0 be found. Forgetting it is the most common bug in this whole family.

### 5.1 Count subarrays with sum = k

The counting version is in [[DSA/02 - Linear Data Structures/06 - Hash Tables#9.3 Subarray sum equals k|Hash Tables § 9.3]]: for each prefix, add `count[sum − k]`, then record `sum`. Look up **before** inserting, or `k = 0` counts the empty subarray at every position.

### 5.2 Longest subarray with sum = k

Store the **first** index where each prefix value appears; a later occurrence gives a longer subarray.

```java
static int maxSubArrayLen(int[] a, int k) {
    Map<Long, Integer> first = new HashMap<>();
    first.put(0L, -1);                            // empty prefix ends "at index −1"
    long sum = 0;
    int best = 0;
    for (int i = 0; i < a.length; i++) {
        sum += a[i];
        Integer j = first.get(sum - k);
        if (j != null) best = Math.max(best, i - j);   // a[j+1..i] has sum k
        first.putIfAbsent(sum, i);                // keep the EARLIEST index
    }
    return best;
}
```

`[1, −1, 5, −2, 3], k = 3` → `4`. With `put` instead of `putIfAbsent`, later indices overwrite earlier ones, and the subarrays found get **shorter**. For the **shortest** such subarray, do the opposite: overwrite, to keep the latest index.

> [!warning] `Map<Long, Integer>` and `get(sum - k)`
> If `sum` is a `long` and `k` an `int`, `sum − k` is a `long`, autoboxed to `Long`: correct. But with an `int` sum and a `Map<Long, …>`, `first.get(sum - k)` boxes an **`Integer`**, which never equals any `Long` key, and the lookup silently always fails. Keep the key type and the expression type identical.

### 5.3 Subarrays divisible by k

Two prefixes with the same remainder mod `k` bound a subarray whose sum is a multiple of `k`.

```java
static int subarraysDivByK(int[] a, int k) {
    int[] count = new int[k];                     // remainders 0..k−1: an array beats a map
    count[0] = 1;
    int sum = 0, res = 0;
    for (int x : a) {
        sum = Math.floorMod(sum + x, k);          // floorMod: never negative
        res += count[sum];
        count[sum]++;
    }
    return res;
}
```

`[4, 5, 0, −2, −3, 1], k = 5` → `7`. Java's `%` keeps the sign of the dividend: `−7 % 5 == −2`, while `Math.floorMod(−7, 5) == 3`. With `%`, prefixes `−2` and `3` (which are congruent mod 5) land in different buckets, or the index `−2` crashes the array version ([[DSA/01 - Foundations/04 - Math for Algorithms|Math for Algorithms]]).

**Continuous subarray sum** ("is there a subarray of length **at least 2** whose sum is a multiple of `k`?") stores the first index of each remainder and checks the distance:

```java
static boolean checkSubarraySum(int[] a, int k) {      // a[i] ≥ 0
    Map<Integer, Integer> first = new HashMap<>();
    first.put(0, -1);
    int sum = 0;
    for (int i = 0; i < a.length; i++) {
        sum = (sum + a[i]) % k;
        Integer j = first.putIfAbsent(sum, i);         // returns the existing index, if any
        if (j != null && i - j >= 2) return true;
    }
    return false;
}
```

`[23, 2, 4, 6, 7], k = 6` → `true` (`[2, 4]`); `[5, 0, 0, 0], k = 3` → `true` (`[0, 0]`, sum 0 is a multiple of every `k`); `[0], k = 1` → `false` (too short).

### 5.4 Equal numbers of 0s and 1s

Map `0 → −1`, `1 → +1`; a subarray with equal counts has sum 0, i.e. two equal prefixes.

```java
static int findMaxLength(int[] a) {
    Map<Integer, Integer> first = new HashMap<>();
    first.put(0, -1);
    int sum = 0, best = 0;
    for (int i = 0; i < a.length; i++) {
        sum += a[i] == 1 ? 1 : -1;
        Integer j = first.putIfAbsent(sum, i);
        if (j != null) best = Math.max(best, i - j);
    }
    return best;
}
```

`[0, 1, 0]` → `2`. The prefix ranges over `[−n, n]`, so an `int[2n + 1]` array offset by `n` can replace the map.

### 5.5 XOR and parity masks

**Count subarrays with XOR `= k`**: the XOR of `a[i..j]` is `X[j+1] ^ X[i]`, and `X[j+1] ^ X[i] = k` iff `X[i] = X[j+1] ^ k`.

```java
static long countXorK(int[] a, int k) {
    Map<Integer, Integer> count = new HashMap<>();
    count.put(0, 1);
    int x = 0;
    long res = 0;
    for (int v : a) {
        x ^= v;
        res += count.getOrDefault(x ^ k, 0);
        count.merge(x, 1, Integer::sum);
    }
    return res;
}
```

**Longest substring where every vowel appears an even number of times**: the state is a 5-bit parity mask, so the "map" is an `int[32]` of first indices.

```java
static int findTheLongestSubstring(String s) {
    int[] first = new int[32];
    Arrays.fill(first, -2);                       // −2 = "not seen"; −1 is a real index (empty prefix)
    first[0] = -1;
    int mask = 0, best = 0;
    for (int i = 0; i < s.length(); i++) {
        int bit = "aeiou".indexOf(s.charAt(i));
        if (bit >= 0) mask ^= 1 << bit;
        if (first[mask] == -2) first[mask] = i;
        else best = Math.max(best, i - first[mask]);
    }
    return best;
}
```

`"eleetminicoworoep"` → `13`. The sentinel for "not seen" can't be `−1`, because `−1` is the legitimate index of the empty prefix.

---

## 6. Prefix Sums with Binary Search

With **non-negative** elements, prefix sums are non-decreasing, so they can be binary searched ([[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]]).

**Weighted random pick**: index `i` with probability `w[i] / Σw`. Lay the weights end to end on a line: index `i` owns the interval `[P[i], P[i+1])`. Draw `r` uniformly from `[0, Σw)` and find the first prefix total `> r`.

```java
static class WeightedPicker {
    private final long[] p;                       // p[i] = w[0] + … + w[i] (inclusive here)
    private final Random rnd = new Random();

    WeightedPicker(int[] w) {
        p = new long[w.length];
        long s = 0;
        for (int i = 0; i < w.length; i++) { s += w[i]; p[i] = s; }
    }

    int pick() {
        long r = (long) (rnd.nextDouble() * p[p.length - 1]);   // r in [0, total)
        int lo = 0, hi = p.length - 1;
        while (lo < hi) {                          // first i with p[i] > r
            int mid = (lo + hi) >>> 1;
            if (p[mid] > r) hi = mid;
            else lo = mid + 1;
        }
        return lo;
    }
}
```

With `w = [1, 3, 2]`, `r = 0` → index 0; `r = 1, 2, 3` → index 1; `r = 4, 5` → index 2: probabilities `1/6, 3/6, 2/6`. Using `p[mid] >= r` instead of `> r` shifts every boundary by one and gives index 0 probability `2/6`.

Other uses: "how many elements (from the start) can be bought with budget `B`?" is `upperBound(P, B) − 1`; "shortest subarray starting at `i` with sum `≥ s`" (non-negative values) is a binary search for `P[i] + s`.

---

## 7. Difference Arrays

### 7.1 Range updates in O(1)

The difference array `D[i] = a[i] − a[i−1]` (with `a[−1] = 0`) is the inverse of prefix summing: the prefix sums of `D` give back `a`. Adding `v` to every element of `a[l..r]` changes only two differences: `a[l]` rises relative to `a[l−1]`, and `a[r+1]` falls back relative to `a[r]`.

```
rangeAdd(D, l, r, v):
    D[l] += v
    D[r + 1] −= v                 -- D has length n + 1, so r + 1 = n is safe

rebuild(D):
    run = 0
    for i = 0 to n − 1: run += D[i]; a[i] = run
```

```java
static long[] rangeAdd(int n, int[][] updates) {      // each update: {l, r, v}, inclusive
    long[] diff = new long[n + 1];
    for (int[] u : updates) {
        diff[u[0]] += u[2];
        diff[u[1] + 1] -= u[2];
    }
    long[] a = new long[n];
    long run = 0;
    for (int i = 0; i < n; i++) { run += diff[i]; a[i] = run; }
    return a;
}
```

![[Prefix Sums - Difference Array Range Update.excalidraw|800]]

`n = 5`, updates `+2 on [1, 3]`, `+3 on [2, 4]`, `−2 on [0, 2]` → `[-2, 0, 3, 5, 3]`. `O(n + q)` instead of `O(nq)`. The catch: you can only read `a` after rebuilding. Interleaved updates and queries need a Fenwick or segment tree ([[#8. Static vs. Dynamic Data|§8]]).

To start from an existing array instead of zeros, initialise `D[i] = a[i] − a[i − 1]`, or keep the updates in a separate difference array and add the rebuilt result to `a`.

### 7.2 Applications

**Corporate flight bookings** (1-indexed, inclusive ranges of flights):

```java
static int[] corpFlightBookings(int[][] bookings, int n) {   // {first, last, seats}, 1-indexed
    int[] diff = new int[n + 1];
    for (int[] b : bookings) {
        diff[b[0] - 1] += b[2];                  // convert to 0-indexed start
        diff[b[1]] -= b[2];                      // (last − 1) + 1 = last
    }
    int[] res = new int[n];
    int run = 0;
    for (int i = 0; i < n; i++) { run += diff[i]; res[i] = run; }
    return res;
}
```

`[[1,2,10],[2,3,20],[2,5,25]], n = 5` → `[10, 55, 45, 25, 25]`.

**Car pooling**: passengers board at `from` and leave at `to` (the seat is free again **at** `to`), so the range is half-open `[from, to)`, and the decrement goes at `to`, not `to + 1`.

```java
static boolean carPooling(int[][] trips, int capacity) {    // {passengers, from, to}
    int maxLoc = 0;
    for (int[] t : trips) maxLoc = Math.max(maxLoc, t[2]);
    int[] diff = new int[maxLoc + 1];
    for (int[] t : trips) {
        diff[t[1]] += t[0];
        diff[t[2]] -= t[0];                      // they leave AT to: half-open interval
    }
    int load = 0;
    for (int d : diff) {
        load += d;
        if (load > capacity) return false;
    }
    return true;
}
```

`[[2,1,5],[3,3,7]], capacity 4` → `false` (5 people between 3 and 5); `[[2,1,5],[3,5,7]], capacity 3` → `true` (the first group leaves at 5 as the second boards).

> [!tip] Large coordinates: sort the events instead
> When positions go up to `10⁹`, an array of that size is impossible. Store only the `2q` change points: a `TreeMap<Integer, Integer>` of `position → delta` (`merge(l, v)`, `merge(r + 1, −v)`), then walk its keys in order with a running sum. Or sort an array of `(position, delta)` events. This is the **sweep line** ([[DSA/08 - Specialized Topics/01 - Intervals and Sweep Line|Intervals and Sweep Line]]), and "minimum number of meeting rooms" is exactly "maximum running sum". With coordinate compression the array version works again.

### 7.3 2D difference arrays

Add `v` to every cell of a rectangle with four corner updates; a 2D prefix sum rebuilds the matrix.

```java
static long[][] rectAdd(int R, int C, int[][] updates) {   // {r1, c1, r2, c2, v}, inclusive
    long[][] d = new long[R + 1][C + 1];
    for (int[] u : updates) {
        int r1 = u[0], c1 = u[1], r2 = u[2], c2 = u[3], v = u[4];
        d[r1][c1] += v;
        d[r1][c2 + 1] -= v;
        d[r2 + 1][c1] -= v;
        d[r2 + 1][c2 + 1] += v;                  // added back: subtracted twice
    }
    long[][] a = new long[R][C];
    for (int r = 0; r < R; r++)
        for (int c = 0; c < C; c++) {
            long up = r > 0 ? a[r - 1][c] : 0, left = c > 0 ? a[r][c - 1] : 0;
            long diag = r > 0 && c > 0 ? a[r - 1][c - 1] : 0;
            a[r][c] = d[r][c] + up + left - diag;   // 2D prefix sum of d
        }
    return a;
}
```

Typical use: "stamping" problems (can these rectangles cover all empty cells?), counting how many rectangles cover each cell, and image-processing style box filters.

### 7.4 Higher order: adding arithmetic progressions (advanced)

To add `1, 2, 3, …, len` to `a[l..r]`, use a **second-order** difference array: prefix-summing twice turns a few point updates into a linear ramp.

```java
static long[] addProgressions(int n, int[][] updates) {   // each {l, r}: add 1, 2, …, r−l+1
    long[] d2 = new long[n + 2];
    for (int[] u : updates) {
        int l = u[0], r = u[1];
        long len = r - l + 1;
        d2[l] += 1;                              // the slope starts at l
        d2[r + 1] -= len + 1;                    // stop the ramp and cancel its height len
        d2[r + 2] += len;                        // restore the slope to 0
    }
    long[] res = new long[n];
    long d1 = 0, v = 0;
    for (int i = 0; i < n; i++) {
        d1 += d2[i];                             // first prefix sum: the slope
        v += d1;                                 // second prefix sum: the value
        res[i] = v;
    }
    return res;
}
```

`n = 6`, update `[1, 4]` → `[0, 1, 2, 3, 4, 0]`. In general, adding a polynomial of degree `d` over a range takes a difference array of order `d + 1`.

---

## 8. Static vs. Dynamic Data

| Workload | Structure | Update | Query |
|---|---|---|---|
| Many range-sum queries, no updates | prefix sums | — (rebuild `O(n)`) | `O(1)` |
| Many range updates, then read everything once | difference array | `O(1)` | `O(n)` rebuild, then `O(1)` |
| Point updates mixed with range-sum queries | Fenwick tree | `O(log n)` | `O(log n)` |
| Range updates mixed with point queries | Fenwick tree **over the difference array** | `O(log n)` | `O(log n)` |
| Range updates mixed with range queries, or min/max | segment tree (with lazy propagation) | `O(log n)` | `O(log n)` |
| Range min/max, no updates | sparse table | — | `O(1)` |

Updating one element of `a` changes **every** later prefix sum, `O(n)` per update. That's the boundary of this technique; the trees in [[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees]] and [[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees|Segment Trees]] store partial sums so that both operations are logarithmic.

---

## 9. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| `P` of length `n` with `P[i] = a[0..i]` | special case or crash for `l = 0` | length `n + 1`, `P[0] = 0` |
| `P[r] − P[l]` for an inclusive range | last element missing | `P[r + 1] − P[l]` |
| `int` prefix array | overflow on large inputs | `long[]` |
| Forgetting `count.put(0, 1)` / `first.put(0, −1)` | subarrays starting at index 0 missed | seed the empty prefix |
| Inserting the current prefix before looking up (`k = 0`) | empty subarrays counted | look up first |
| `put` instead of `putIfAbsent` for longest | answers too short | keep the first index |
| `sum % k` with negative numbers | wrong buckets, negative array index | `Math.floorMod` |
| `Map<Long, …>.get(intExpression)` | lookups always miss | same key type |
| Prefix products with zeros | division by zero | track zeros separately |
| Prefix min/max used for arbitrary ranges | wrong answer | only for prefixes; use a sparse table |
| 2D query with wrong signs or corners | off by a strip | `− top − left + corner` |
| Difference array of length `n` | `ArrayIndexOutOfBounds` at `r + 1 = n` | length `n + 1` |
| Decrement at `to + 1` for half-open intervals | load counted one step too long | decrement at `to` |
| Reading `a` before rebuilding | stale values | rebuild after all updates |
| Difference array with `10⁹` positions | out of memory | sorted events / `TreeMap` |
| Prefix sums with frequent point updates | `O(n)` per update | Fenwick tree |
| "not seen" sentinel `−1` in a first-index array | empty prefix and unseen states collide | use `−2` or fill with `Integer.MIN_VALUE` |

---

## 10. Trick Questions and Special Cases

> [!question]- With `P[0] = 0`, what's the sum of `a[2..5]` (inclusive)? And of the empty range?
> `P[6] − P[2]`. The empty range `[l, l)` has sum `P[l] − P[l] = 0`, which the formula gives for free. That's why `P` is indexed by boundaries, not elements.

> [!question]- Pivot index of `[2, 1, −1]`?
> `0`. The left sum of index 0 is the empty sum, 0, and the right sum is `1 + (−1) = 0`. Code that only checks indices `1..n−2`, or that assumes a pivot needs elements on both sides, misses it.

> [!question]- Subarray sum equals `k = 0` in `[0, 0, 0]`: how many?
> `6`: every subarray (`3 + 2 + 1`). With the lookup done **after** inserting the current prefix, each position also matches itself, adding the empty subarray, and the result is `9`.

> [!question]- Subarrays divisible by 5 in `[−1, 5]`: what goes wrong with `%`?
> The prefixes are `0, −1, 4`. The answer is `1` (`[5]`, from the prefixes `−1` and `4`, which are congruent mod 5). With `%`, the remainders are `0, −1, 4`: `−1` and `4` land in different buckets, a map-based version returns `0`, and an array-based version throws on index `−1`. With `Math.floorMod`, they're `0, 4, 4`, and the match is found.

> [!question]- Is there a subarray of length ≥ 2 with sum a multiple of `k` in `[5, 0, 0, 0]`, `k = 3`?
> Yes: `[0, 0]`, sum 0, which is a multiple of every `k`. And in `[0]`? No: only length 1. Seeding the map with `0 → −1` (not `0 → 0`) is what makes a valid subarray starting at index 0 have the right length.

> [!question]- Longest subarray with sum `k = 3` in `[1, −1, 5, −2, 3]`?
> `4` (`[1, −1, 5, −2]`). A sliding window can't find it (negative numbers), and the prefix map must keep the **first** index of each prefix value, or it finds `[3]` (length 1) instead.

> [!question]- Range-update `+1` on `[0, n−1]` with a difference array of length `n`?
> `diff[n] −= 1` throws `ArrayIndexOutOfBoundsException`. The difference array needs length `n + 1` (the last slot is never read back), or a guard `if (r + 1 < n)`.

> [!question]- Car pooling `[[2, 1, 5], [3, 5, 7]]`, capacity 3: possible?
> Yes. The first group leaves **at** 5 and the second boards at 5, so at most 3 people are aboard at any time. Treating the trip as inclusive (`decrement at to + 1`) counts 5 people at location 5 and wrongly answers `false`.

> [!question]- Why can't prefix sums answer range-minimum queries?
> `min` has no inverse: knowing `min(a[0..r])` and `min(a[0..l−1])` doesn't determine `min(a[l..r])` (if the prefix minimum is before `l`, it says nothing about the range). Prefix minima work only for ranges that start at 0. General range minima need a sparse table or a segment tree.

> [!question]- `Map<Long, Integer> first` with `int sum`: why does `first.get(sum - k)` never find anything?
> `sum − k` is an `int`, autoboxed to an `Integer`. `Integer.valueOf(3).equals(Long.valueOf(3))` is `false`, so no `Long` key ever matches. The code compiles (`get` takes an `Object`) and silently returns `null`. Use the same type for the key and the lookup expression.

> [!question]- Weighted random pick with weights `[1, 3, 2]`: which `r` values map to index 1?
> `r ∈ {1, 2, 3}`, with `r` drawn from `[0, 6)` and "first prefix `> r`" on `p = [1, 4, 6]`. Using `>=` would map `r = 1` to index 0, giving index 0 probability `2/6` instead of `1/6`. Off-by-one errors here produce no crash, just a subtly wrong distribution.

> [!question]- Sum of all subarray sums of `[1, 2, 3]`?
> `20`. Element `a[i]` appears in `(i + 1)(n − i)` subarrays: `1·3·1 + 2·2·2 + 3·1·3 = 3 + 8 + 9`. No need to enumerate the 6 subarrays.

> [!question]- After updating one element, can the prefix sums be fixed in O(1)?
> No: every `P[j]` with `j > i` changes, `O(n)` work. If updates and queries interleave, use a Fenwick tree (`O(log n)` for both).

---

## 11. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `P` length | `n + 1` | boundary values, `P[0] = 0` |
| Sum of `a[l..r]` inclusive | `P[r + 1] − P[l]` | |
| `pivotIndex([2, 1, −1])` | `0` | empty left sum |
| `minStartValue([1, 2])` | `1` | start must be positive anyway |
| Subarrays with sum 0 in `[0, 0, 0]` | `6` | look up before inserting |
| `−7 % 5` / `Math.floorMod(−7, 5)` | `−2` / `3` | sign of the dividend |
| `subarraysDivByK([4,5,0,−2,−3,1], 5)` | `7` | |
| `maxSubArrayLen([1,−1,5,−2,3], 3)` | `4` | first index |
| `checkSubarraySum([5,0,0,0], 3)` | `true` | `0` is a multiple of `k` |
| `checkSubarraySum([0], 1)` | `false` | length `≥ 2` |
| `findMaxLength([0, 1, 0])` | `2` | `0 → −1` |
| Prefix XOR of `a[l..r]` | `X[r+1] ^ X[l]` | XOR is self-inverse |
| Range min from prefix minima | impossible | `min` isn't invertible |
| Difference array length | `n + 1` | `D[r + 1]` with `r = n − 1` |
| Car pooling decrement | at `to` | half-open trip |
| `corpFlightBookings(..., 5)` example | `[10, 55, 45, 25, 25]` | |
| 2D query | `P[r2+1][c2+1] − P[r1][c2+1] − P[r2+1][c1] + P[r1][c1]` | inclusion–exclusion |
| 2D range add | 4 corner updates | |
| Sum of all subarray sums `[1,2,3]` | `20` | `(i + 1)(n − i)` contributions |
| Prefix sums after a point update | `O(n)` to fix | use a Fenwick tree |

---

## 12. Summary

- `P[0] = 0`, `P[i + 1] = P[i] + a[i]`; the sum of `a[l..r]` is `P[r + 1] − P[l]`. Think of `P` as values at the boundaries between elements, and store it as `long`.
- The same works for any invertible operation: XOR, counts, parity bitmasks, and products (careful with zeros). Min and max are not invertible.
- **2D** prefix sums use inclusion–exclusion to answer rectangle sums in `O(1)`.
- **Prefix sums + hash maps** turn subarray questions into "find an earlier prefix": counts (`sum − k`), longest (first index), divisibility (`floorMod`), balance (`±1`), XOR, parity masks. Seed the empty prefix; this works with negative numbers.
- With non-negative values, prefix sums are sorted and can be **binary searched** (weighted random pick).
- **Difference arrays** make range updates `O(1)`: `D[l] += v`, `D[r + 1] −= v`, then one prefix-sum pass. They extend to 2D (four corners), half-open intervals, sorted events for huge coordinates, and higher orders for progressions.
- Interleaved updates and queries are beyond this technique: Fenwick and segment trees.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/03 - Sorting and Searching/04 - Sliding Window|Sliding Window]] · Next: [[DSA/04 - Trees and Hierarchical Structures/01 - Binary Trees|Binary Trees]]
- [[DSA/01 - Foundations/03 - Bit Manipulation|Bit Manipulation]]: prefix XOR and bitmask states
- [[DSA/02 - Linear Data Structures/01 - Arrays|Arrays]]: Kadane, product except self
- [[DSA/02 - Linear Data Structures/06 - Hash Tables|Hash Tables]]: subarray sum equals k
- [[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]]: shortest subarray with sum ≥ k using prefix sums and a deque
- [[DSA/03 - Sorting and Searching/04 - Sliding Window|Sliding Window]]: the alternative when all values are non-negative
- [[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees]] and [[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees|Segment Trees]]: prefix sums with updates
- [[DSA/08 - Specialized Topics/01 - Intervals and Sweep Line|Intervals and Sweep Line]]: difference arrays over sorted events
