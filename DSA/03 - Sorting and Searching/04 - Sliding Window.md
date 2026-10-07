# Sliding Window

A <span class="hl-blue">sliding window</span> is a contiguous range `a[left..right]` that moves across an array or string. Instead of recomputing a property of every subarray from scratch (`O(n²)` subarrays, often `O(n)` each), you maintain it **incrementally**: add the element entering on the right, remove the one leaving on the left. Each element enters once and leaves at most once, so the whole scan is `O(n)`.

There are two kinds: **fixed-size** windows (every subarray of length `k`) and **variable-size** windows, which grow on the right and shrink on the left to find the longest or shortest subarray satisfying a condition, or to count such subarrays. Variable windows only work when the condition is **monotone** in the window, which is exactly what fails with negative numbers. This note covers both kinds, the counting tricks (`exactly k = atMost(k) − atMost(k − 1)`), complement windows, and how to recognise when a window can't work.

## Contents

- [[#1. The Idea|1. The Idea]]
- [[#2. Fixed-Size Windows|2. Fixed-Size Windows]]
- [[#3. Variable Windows — Longest Valid|3. Variable Windows — Longest Valid]]
- [[#4. Variable Windows — Shortest Valid|4. Variable Windows — Shortest Valid]]
- [[#5. Counting Subarrays|5. Counting Subarrays]]
- [[#6. The Non-Shrinking Window|6. The Non-Shrinking Window]]
- [[#7. Complement Windows|7. Complement Windows]]
- [[#8. When a Sliding Window Fails|8. When a Sliding Window Fails]]
- [[#9. Common Mistakes|9. Common Mistakes]]
- [[#10. Trick Questions and Special Cases|10. Trick Questions and Special Cases]]
- [[#11. Quick Reference — Non-Obvious Outcomes|11. Quick Reference — Non-Obvious Outcomes]]
- [[#12. Summary|12. Summary]]

---

## 1. The Idea

> [!note] Window state
> The window `a[left..right]` keeps a summary that can be updated in `O(1)` (or `O(log n)`) when one element enters or leaves:
> - a **sum** (add on enter, subtract on leave);
> - a **frequency table** (`int[26]`, `int[128]`, or a `HashMap`) plus a counter derived from it ("number of distinct values", "number of characters still missing");
> - a **monotonic deque** for the window's max or min ([[DSA/02 - Linear Data Structures/05 - Queues and Deques#7. Monotonic Deque — Sliding Window Maximum|Queues and Deques § 7]]);
> - a sorted structure (`TreeMap`, two heaps) for the median or order statistics.
>
> Anything that can't be "un-added" cheaply (max with only a running variable, product with zeros) needs one of the richer structures.

> [!important] When a variable window works
> Shrinking from the left must never be wasted work. That's true when validity is **monotone**:
> - **For "longest valid":** if a window is valid, every window **inside** it is valid too. Then once `[left, right]` is invalid, every window `[left, right']` with `right' > right` is also invalid, so `left` can move right for good.
> - **For "shortest valid":** if a window is valid, every window **containing** it is valid too. Then once `[left, right]` is valid, extending it further right can't give a shorter answer for this `left`, so `left` can move.
>
> "Sum ≤ k with non-negative numbers", "at most k distinct", "no repeated character" are monotone. "Sum == k with negative numbers" is not ([[#8. When a Sliding Window Fails|§8]]).

| Signal in the problem | Window type |
|---|---|
| "every subarray / substring of length `k`" | fixed |
| "longest subarray / substring such that …" | variable, shrink while **invalid** |
| "shortest / minimum-length subarray such that …" | variable, shrink while **valid** |
| "number of subarrays such that …" | variable, count per right end |
| contiguous, and the condition is monotone | variable works |
| subsequence (not contiguous), or the condition isn't monotone | not a sliding window: DP, prefix sums + hashing, … |

---

## 2. Fixed-Size Windows

### 2.1 Maximum sum of a window of size `k`

```
maxSumK(a, k):
    sum = a[0] + … + a[k − 1]; best = sum
    for i = k to n − 1:
        sum += a[i] − a[i − k]               -- a[i] enters, a[i − k] leaves
        best = max(best, sum)
    return best
```

```java
static long maxSumK(int[] a, int k) {
    long sum = 0;
    for (int i = 0; i < k; i++) sum += a[i];
    long best = sum;                          // NOT 0: all windows may be negative
    for (int i = k; i < a.length; i++) {
        sum += a[i] - a[i - k];
        best = Math.max(best, sum);
    }
    return best;
}
```

`O(n)` instead of `O(nk)`. Initialising `best = 0` returns `0` for `[-5, -2, -3], k = 2` instead of `−7`. The same skeleton gives maximum average (divide at the end), the number of windows with average `≥ t` (compare `sum ≥ t·k`, no division), and fixed windows over strings ("maximum number of vowels in a substring of length `k`").

### 2.2 Find all anagrams of `p` in `s`

Slide a window of length `|p|` over `s`. Keep `diff[c] = count in p − count in window`, and the number of letters whose `diff` is non-zero. The window is an anagram exactly when that number is 0, so each step costs `O(1)` instead of comparing two 26-element arrays.

```java
static List<Integer> findAnagrams(String s, String p) {
    List<Integer> res = new ArrayList<>();
    int k = p.length();
    if (k > s.length()) return res;
    int[] diff = new int[26];
    for (int i = 0; i < k; i++) { diff[p.charAt(i) - 'a']++; diff[s.charAt(i) - 'a']--; }
    int nonZero = 0;
    for (int d : diff) if (d != 0) nonZero++;
    if (nonZero == 0) res.add(0);
    for (int i = k; i < s.length(); i++) {
        nonZero += change(diff, s.charAt(i) - 'a', -1);       // enters the window
        nonZero += change(diff, s.charAt(i - k) - 'a', +1);   // leaves the window
        if (nonZero == 0) res.add(i - k + 1);
    }
    return res;
}

static int change(int[] diff, int c, int delta) {             // returns the change in nonZero
    int before = diff[c] != 0 ? 1 : 0;
    diff[c] += delta;
    int after = diff[c] != 0 ? 1 : 0;
    return after - before;
}
```

`"cbaebabacd"`, `"abc"` → `[0, 6]`; `"abab"`, `"ab"` → `[0, 1, 2]` (overlapping matches count). "Permutation in string" is the same check, returning on the first match. The single `diff` array that counts one string up and the other down is from [[DSA/02 - Linear Data Structures/02 - Strings#5.1 One array, increment and decrement|Strings § 5.1]].

> [!tip] Comparing the whole table each step is fine too
> `Arrays.equals(countP, countWindow)` on two `int[26]` arrays is `O(26)` per step, so `O(26n)` overall: perfectly acceptable for lowercase letters. The `nonZero` counter matters when the alphabet is large (Unicode, or arbitrary integers in a `HashMap`).

### 2.3 Windows with a set or map

**Contains duplicate within distance `k`**: is there `i ≠ j` with `a[i] == a[j]` and `|i − j| ≤ k`? Keep the last `k` elements in a set.

```java
static boolean containsNearbyDuplicate(int[] a, int k) {
    Set<Integer> window = new HashSet<>();
    for (int i = 0; i < a.length; i++) {
        if (!window.add(a[i])) return true;        // a[i] already among the previous k
        if (i >= k) window.remove(a[i - k]);       // keep only a[i−k+1..i]
    }
    return false;
}
```

**Maximum sum of a length-`k` subarray with all distinct elements**: maintain the sum and a count map; the window qualifies when the map has `k` keys.

```java
static long maxSumDistinctK(int[] a, int k) {
    Map<Integer, Integer> count = new HashMap<>();
    long sum = 0, best = 0;                        // 0 = "no qualifying window"
    for (int i = 0; i < a.length; i++) {
        sum += a[i];
        count.merge(a[i], 1, Integer::sum);
        if (i >= k) {
            sum -= a[i - k];
            if (count.merge(a[i - k], -1, Integer::sum) == 0) count.remove(a[i - k]);   // drop zero counts!
        }
        if (i >= k - 1 && count.size() == k) best = Math.max(best, sum);
    }
    return best;
}
```

> [!warning] Remove keys whose count drops to zero
> `map.size()` counts keys, not keys with a positive count. Forgetting `count.remove(x)` when a count reaches 0 makes "number of distinct values" only ever grow. The `merge(x, -1, Integer::sum) == 0` idiom decrements and tests in one call (and `merge` itself removes the key if the function returns `null`, but not `0`).

### 2.4 Window maximum, minimum, and median

- **Maximum/minimum of every window**: monotonic deque, `O(n)` ([[DSA/02 - Linear Data Structures/05 - Queues and Deques#7. Monotonic Deque — Sliding Window Maximum|Queues and Deques § 7]]). A running `max` variable doesn't work, because when the maximum leaves the window you don't know the next one.
- **Median of every window**: two balanced halves with deletion, `O(n log k)`.

> [!example]- Sliding window median with two `TreeSet`s
> Store **indices** (so equal values are distinct elements), ordered by value then index. `low` holds the smaller half, `high` the larger; `low` may have one extra element.
> ```java
> static double[] medianSlidingWindow(int[] a, int k) {
>     Comparator<Integer> cmp = (i, j) -> a[i] != a[j] ? Integer.compare(a[i], a[j]) : Integer.compare(i, j);
>     TreeSet<Integer> low = new TreeSet<>(cmp), high = new TreeSet<>(cmp);
>     double[] res = new double[a.length - k + 1];
>     for (int i = 0; i < a.length; i++) {
>         if (i >= k) { if (!low.remove(i - k)) high.remove(i - k); }   // index leaving the window
>         low.add(i);
>         high.add(low.pollLast());                  // move low's largest to high
>         if (high.size() > low.size()) low.add(high.pollFirst());     // rebalance
>         if (i >= k - 1)
>             res[i - k + 1] = k % 2 == 1 ? a[low.last()]
>                                         : ((double) a[low.last()] + a[high.first()]) / 2;
>     }
>     return res;
> }
> ```
> `[1, 3, -1, -3, 5, 3, 6, 7], k = 3` → `[1, -1, -1, 3, 5, 6]`. The `(double)` cast before adding matters: `[2147483647, 2147483647], k = 2` overflows in `int` and gives `-1.0` instead of `2.147483647E9`. A `PriorityQueue` version needs "lazy deletion" (remember what to remove, discard it when it reaches the top), because `PriorityQueue.remove(Object)` is `O(k)`. Heaps are covered in [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|Heaps and Priority Queues]].

---

## 3. Variable Windows — Longest Valid

```
longestValid(a):
    left = 0; best = 0
    for right = 0 to n − 1:
        add a[right] to the window
        while the window is invalid:           -- shrink until valid again
            remove a[left]; left += 1
        best = max(best, right − left + 1)      -- the window is valid here
    return best
```

The answer is recorded **after** shrinking, when the window is guaranteed valid.

### 3.1 Longest substring without repeating characters

```java
static int lengthOfLongestSubstring(String s) {
    int[] count = new int[128];                  // ASCII; use a HashMap for general Unicode
    int left = 0, best = 0;
    for (int right = 0; right < s.length(); right++) {
        char c = s.charAt(right);
        count[c]++;
        while (count[c] > 1) count[s.charAt(left++)]--;   // only c can be repeated
        best = Math.max(best, right - left + 1);
    }
    return best;
}
```

![[Sliding Window - Expand and Shrink.excalidraw|800]]

`"abcabcbb"` → `3`, `"bbbbb"` → `1`, `"pwwkew"` → `3` (`"wke"`; `"pwke"` is a subsequence, not a substring), `""` → `0`, `" "` → `1` (a space is a character).

**Jump version**: store the last index of each character, and jump `left` past the previous occurrence directly.

```java
static int lengthOfLongestSubstringJump(String s) {
    int[] last = new int[128];
    Arrays.fill(last, -1);
    int left = 0, best = 0;
    for (int right = 0; right < s.length(); right++) {
        char c = s.charAt(right);
        left = Math.max(left, last[c] + 1);      // max: never move left BACKWARDS
        last[c] = right;
        best = Math.max(best, right - left + 1);
    }
    return best;
}
```

> [!warning] The `abba` bug
> Without `Math.max`, `left = last[c] + 1` can move `left` backwards. On `"abba"`: at the second `b`, `left` jumps to 2; at the final `a`, `last['a'] = 0`, so `left` would go back to 1, and the window `"bba"` (length 3) is counted although it contains two `b`s. The correct answer is `2`. The previous occurrence only matters if it's **inside** the current window.

### 3.2 At most `k` distinct values (fruit into baskets)

```java
static int longestAtMostKDistinct(int[] a, int k) {
    Map<Integer, Integer> count = new HashMap<>();
    int left = 0, best = 0;
    for (int right = 0; right < a.length; right++) {
        count.merge(a[right], 1, Integer::sum);
        while (count.size() > k) {
            int x = a[left++];
            if (count.merge(x, -1, Integer::sum) == 0) count.remove(x);
        }
        best = Math.max(best, right - left + 1);
    }
    return best;
}
```

"Fruit into baskets" is `k = 2`: `[1, 2, 3, 2, 2]` → `4` (`[2, 3, 2, 2]`).

### 3.3 Max consecutive ones with at most `k` flips

"Longest subarray of 1s after flipping at most `k` zeros" is "longest window with at most `k` zeros". The flips never have to be performed.

```java
static int longestOnes(int[] a, int k) {
    int left = 0, zeros = 0, best = 0;
    for (int right = 0; right < a.length; right++) {
        if (a[right] == 0) zeros++;
        while (zeros > k) if (a[left++] == 0) zeros--;
        best = Math.max(best, right - left + 1);
    }
    return best;
}
```

`[1,1,1,0,0,0,1,1,1,1,0], k = 2` → `6`. "Longest subarray of 1s after deleting **exactly one** element" is the `k = 1` window, minus 1 (the deleted element), and an all-ones array must still delete one: `[1, 1, 1]` → `2`.

### 3.4 Longest repeating character replacement

Replace at most `k` characters so that the window is all one letter. A window is valid when `length − (count of its most frequent letter) ≤ k`.

```java
static int characterReplacement(String s, int k) {
    int[] count = new int[26];
    int left = 0, maxFreq = 0, best = 0;
    for (int right = 0; right < s.length(); right++) {
        maxFreq = Math.max(maxFreq, ++count[s.charAt(right) - 'A']);
        while (right - left + 1 - maxFreq > k) count[s.charAt(left++) - 'A']--;
        best = Math.max(best, right - left + 1);
    }
    return best;
}
```

`"AABABBA", k = 1` → `4`.

> [!important] Why `maxFreq` is never decreased
> When an element leaves, the true maximum frequency in the window may drop, but `maxFreq` isn't updated. That makes the validity test too lenient for some windows, so why is the answer still right? Because the answer can only **improve** when a window has a larger `maxFreq` than any seen before: `best ≤ maxFreq + k` always. A stale, too-large `maxFreq` can keep a window from shrinking, but it never lets the window grow beyond `(largest frequency ever achieved) + k`, which is a valid length that was actually achieved. Recomputing the true maximum (scan 26 counts) is also correct and still `O(26n)`, if the shortcut feels too clever.

---

## 4. Variable Windows — Shortest Valid

```
shortestValid(a):
    left = 0; best = ∞
    for right = 0 to n − 1:
        add a[right]
        while the window is valid:              -- shrink while it stays valid
            best = min(best, right − left + 1)  -- record BEFORE removing
            remove a[left]; left += 1
    return best (or "none" if still ∞)
```

### 4.1 Minimum-size subarray with sum ≥ target (positive numbers)

```java
static int minSubArrayLen(int target, int[] a) {
    int left = 0, best = Integer.MAX_VALUE;
    long sum = 0;
    for (int right = 0; right < a.length; right++) {
        sum += a[right];
        while (sum >= target) {
            best = Math.min(best, right - left + 1);
            sum -= a[left++];
        }
    }
    return best == Integer.MAX_VALUE ? 0 : best;   // the problem's "no such subarray" value
}
```

`target = 7, [2, 3, 1, 2, 4, 3]` → `2` (`[4, 3]`); `target = 11, [1, 1, 1, 1]` → `0`. This relies on **positive** elements: removing an element always decreases the sum. With negatives, see [[#8. When a Sliding Window Fails|§8]]. An `O(n log n)` alternative binary-searches the prefix sums (which are increasing) for each start.

### 4.2 Minimum window substring

The shortest substring of `s` containing every character of `t` (with multiplicity). Track `need[c]` (how many more `c`s the window needs; negative means surplus) and `missing` (the total still needed).

```
minWindow(s, t):
    need[c] = count of c in t; missing = |t|
    left = 0
    for right = 0 to |s| − 1:
        c = s[right]
        if need[c] > 0: missing −= 1           -- c was actually needed
        need[c] −= 1                           -- surplus goes negative
        while missing == 0:                    -- window contains all of t
            record [left, right] if shorter
            d = s[left]; need[d] += 1
            if need[d] > 0: missing += 1       -- removed a needed copy, not a surplus one
            left += 1
```

```java
static String minWindow(String s, String t) {
    int[] need = new int[128];
    for (char c : t.toCharArray()) need[c]++;
    int missing = t.length();
    int left = 0, bestLen = Integer.MAX_VALUE, bestStart = 0;
    for (int right = 0; right < s.length(); right++) {
        if (need[s.charAt(right)]-- > 0) missing--;
        while (missing == 0) {
            if (right - left + 1 < bestLen) { bestLen = right - left + 1; bestStart = left; }
            if (++need[s.charAt(left++)] > 0) missing++;
        }
    }
    return bestLen == Integer.MAX_VALUE ? "" : s.substring(bestStart, bestStart + bestLen);
}
```

![[Sliding Window - Minimum Window Substring.excalidraw|800]]

`"ADOBECODEBANC"`, `"ABC"` → `"BANC"`; `"a"`, `"aa"` → `""` (`t` needs two `a`s); `"aa"`, `"aa"` → `"aa"`. Characters not in `t` get negative `need` values and never affect `missing`.

> [!warning] Store the start and length, not the substring
> Calling `s.substring(left, right + 1)` every time a shorter window is found copies characters each time, which can make the algorithm `O(n²)` in the worst case. Record `bestStart` and `bestLen`, and build the string once at the end.

---

## 5. Counting Subarrays

### 5.1 "At most": count `right − left + 1` per right end

If validity is monotone (sub-windows of valid windows are valid), then for a fixed `right`, the valid windows ending at `right` are exactly those starting at `left, left + 1, …, right`: that's `right − left + 1` subarrays.

**Subarrays with product `< k`** (positive integers):

```java
static int numSubarrayProductLessThanK(int[] a, int k) {
    if (k <= 1) return 0;                     // no product of positive ints is < 1; also stops left > right
    long prod = 1;
    int left = 0, count = 0;
    for (int right = 0; right < a.length; right++) {
        prod *= a[right];
        while (prod >= k) prod /= a[left++];
        count += right - left + 1;            // all windows ending at right that start ≥ left
    }
    return count;
}
```

`[10, 5, 2, 6], k = 100` → `8`. Without the `k <= 1` guard, with `k = 0` the `while` loop divides past `right` (when `left > right`, `prod` is `1`, still `≥ 0`) and runs off the end of the array.

### 5.2 "Exactly k" = atMost(k) − atMost(k − 1)

"Exactly `k` distinct values" isn't monotone in the useful way: a window with exactly `k` distinct can be extended or shrunk into one with fewer **or** more. But "at most `k`" is monotone, and every subarray with exactly `k` distinct is counted by `atMost(k)` and not by `atMost(k − 1)`.

```java
static int subarraysWithKDistinct(int[] a, int k) {
    return atMostKDistinct(a, k) - atMostKDistinct(a, k - 1);
}

static int atMostKDistinct(int[] a, int k) {                // values ≥ 0
    int max = 0;
    for (int x : a) max = Math.max(max, x);
    int[] count = new int[max + 1];
    int left = 0, distinct = 0, res = 0;
    for (int right = 0; right < a.length; right++) {
        if (count[a[right]]++ == 0) distinct++;
        while (distinct > k) if (--count[a[left++]] == 0) distinct--;
        res += right - left + 1;
    }
    return res;
}
```

![[Sliding Window - Exactly K from At Most.excalidraw|800]]

`[1, 2, 1, 2, 3], k = 2` → `7` (`atMost(2) = 12`, `atMost(1) = 5`). The same subtraction counts **binary subarrays with sum = goal** and **subarrays with exactly `k` odd numbers** (map each element to `a[i] % 2` and count sums):

```java
static int numSubarraysWithSum(int[] a, int goal) {          // a contains only 0s and 1s
    return atMostSum(a, goal) - atMostSum(a, goal - 1);
}

static int atMostSum(int[] a, int goal) {
    if (goal < 0) return 0;                  // atMost(−1) is 0; without this the loop breaks
    int left = 0, sum = 0, res = 0;
    for (int right = 0; right < a.length; right++) {
        sum += a[right];
        while (sum > goal) sum -= a[left++];
        res += right - left + 1;
    }
    return res;
}
```

`[1, 0, 1, 0, 1], goal = 2` → `4`; `[0, 0, 0, 0, 0], goal = 0` → `15` (every subarray). With `goal = 0`, `atMostSum(a, −1)` must return 0: inside the loop, `sum > −1` is always true and `left` would run past `right`. The prefix-sum + hash map method ([[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums]]) also works here, and it's the only one of the two that still works with negative numbers.

### 5.3 "At least": add `left` per right end

If validity is monotone the **other** way (super-windows of valid windows are valid), shrink while the window is valid. After the loop, the windows `[0..right], [1..right], …, [left − 1..right]` are all valid: `left` subarrays end at `right`.

**Substrings containing at least one of each `a`, `b`, `c`**:

```java
static int numberOfSubstrings(String s) {
    int[] count = new int[3];
    int left = 0, res = 0;
    for (int right = 0; right < s.length(); right++) {
        count[s.charAt(right) - 'a']++;
        while (count[0] > 0 && count[1] > 0 && count[2] > 0) count[s.charAt(left++) - 'a']--;
        res += left;                           // starts 0..left−1 all give valid windows
    }
    return res;
}
```

`"abcabc"` → `10`, `"aaacb"` → `3`. Equivalently, `atLeast(k) = total − atMost(k − 1)`, where `total = n(n+1)/2`.

---

## 6. The Non-Shrinking Window

When only the **maximum length** is needed, the window never has to get smaller: once a valid window of length `L` is found, there's no point looking at shorter ones. Replace the `while` with an `if`, so the window slides (both ends move by one) when invalid and grows when valid.

```java
static int longestOnesNoShrink(int[] a, int k) {
    int left = 0, zeros = 0;
    for (int right = 0; right < a.length; right++) {
        if (a[right] == 0) zeros++;
        if (zeros > k) {                       // slide: drop exactly one element
            if (a[left] == 0) zeros--;
            left++;
        }
    }
    return a.length - left;                    // the window's final size is the answer
}
```

The window may be **invalid** at the end, but its size equals the best valid size seen, because it only grew at moments when it was valid. This is also why the stale `maxFreq` in [[#3.4 Longest repeating character replacement|§3.4]] works. The trade-off: shorter code and fewer operations, but the window's contents no longer describe a valid answer, so you can't read the answer's position from it.

---

## 7. Complement Windows

When a problem removes elements **from both ends**, what remains is a contiguous middle. Turn "best choice of ends" into "best middle window".

**Maximum points from taking `k` cards from either end**: the cards left behind are a window of length `n − k`; maximise the taken sum = minimise that window's sum.

```java
static int maxScore(int[] cards, int k) {
    int n = cards.length, w = n - k;
    long total = 0, sum = 0;
    for (int c : cards) total += c;
    for (int i = 0; i < w; i++) sum += cards[i];
    long minWindow = sum;
    for (int i = w; i < n; i++) {
        sum += cards[i] - cards[i - w];
        minWindow = Math.min(minWindow, sum);
    }
    return (int) (total - minWindow);
}
```

`[1, 2, 3, 4, 5, 6, 1], k = 3` → `12`; with `k = n`, the window is empty and the answer is the total.

**Minimum operations to reduce `x` to zero** (remove from either end, subtracting the removed value): the remaining middle must sum to `total − x`, and we want it as **long** as possible.

```java
static int minOperations(int[] a, int x) {        // a[i] ≥ 1
    long target = -x;
    for (int v : a) target += v;                   // the middle must sum to total − x
    if (target < 0) return -1;                     // even removing everything isn't enough
    int left = 0, best = -1;
    long sum = 0;
    for (int right = 0; right < a.length; right++) {
        sum += a[right];
        while (sum > target) sum -= a[left++];
        if (sum == target) best = Math.max(best, right - left + 1);
    }
    return best < 0 ? -1 : a.length - best;
}
```

`[1, 1, 4, 2, 3], x = 5` → `2`; `[5, 6, 7, 8, 9], x = 4` → `−1`; `[3, 2, 20, 1, 1, 3], x = 10` → `5`. When `target = 0`, the empty window (`best = 0`) is the answer: remove everything. The `while (sum > target)` guard lets `left` reach `right + 1`, giving an empty window, which is exactly what `target = 0` needs.

---

## 8. When a Sliding Window Fails

![[Sliding Window - Negative Numbers Break It.excalidraw|800]]

> [!warning] Negative numbers break sum windows
> With negatives, adding an element can **decrease** the sum and removing one can **increase** it. "The sum is too big, so shrink from the left" is no longer justified: removing a negative element makes it bigger. Example: shortest subarray with sum `≥ 3` in `[2, −1, 2, 1]`. At `right = 2` the window `[2, −1, 2]` has sum 3: length 3 is recorded, then the leading `2` is dropped, leaving `[−1, 2]` with sum 1. At `right = 3`, `[−1, 2, 1]` sums to 2, below 3, so the window never shrinks past the `−1`, and `[2, 1]` (sum 3, length 2) is never examined. The window returns 3; the answer is 2.

What to use instead:

| Problem with negatives allowed | Technique |
|---|---|
| Count subarrays with sum `= k` | prefix sums + hash map of prefix counts ([[DSA/02 - Linear Data Structures/06 - Hash Tables#9.3 Subarray sum equals k|Hash Tables § 9.3]]) |
| Longest subarray with sum `= k` | prefix sums + map of **first** index of each prefix ([[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums]]) |
| Shortest subarray with sum `≥ k` | prefix sums + monotonic deque ([[DSA/02 - Linear Data Structures/05 - Queues and Deques#8.2 Shortest subarray with sum ≥ K, with negative numbers|Queues and Deques § 8.2]]) |
| Maximum subarray sum (any length) | Kadane's algorithm ([[DSA/02 - Linear Data Structures/01 - Arrays#8.1 Maximum subarray sum (Kadane's algorithm)|Arrays § 8.1]]) |
| Longest subarray with sum `≤ k` | prefix sums + binary search over prefix maxima, `O(n log n)` |

Other conditions that aren't monotone: "exactly `k`" (use the at-most subtraction), "the window's sum is divisible by `k`" (prefix sums mod `k`), "the number of distinct values equals the window length minus something"… Before writing a window, check: if `[l, r]` is valid, is `[l + 1, r]` valid (for longest) or `[l, r + 1]` valid (for shortest)? If neither holds, look elsewhere.

Products with **zeros** are another trap: a zero makes the product 0 and dividing it back out is impossible. Split the array at zeros, or track the count of zeros in the window separately.

---

## 9. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| `best = 0` for the maximum window sum | `0` when all windows are negative | start from the first window |
| Recording the answer before shrinking (longest) | an invalid window is counted | update after the `while` |
| Recording after shrinking (shortest) | the valid window is gone | update inside the `while`, before removing |
| `left = last[c] + 1` without `max` | `"abba"` → `3` | `left = max(left, last[c] + 1)` |
| Map count reaches 0 but the key stays | distinct count only grows | remove zero-count keys |
| Sum window with negative numbers | misses answers | prefix sums + hash map or deque |
| Product window with `k ≤ 1` | infinite loop or index out of bounds | return 0 early |
| `atMost(goal − 1)` with `goal = 0` | `left` runs past `right` | `atMost(−1) = 0` |
| Using "exactly k" directly as the window condition | wrong counts | `atMost(k) − atMost(k − 1)` |
| `substring` for every candidate window | `O(n²)` | store start and length |
| `int` sum of a window of large values | overflow | `long` |
| `(a + b) / 2` for the median of two `int`s | overflow | `((double) a + b) / 2` |
| `int[26]` with uppercase or other characters | `ArrayIndexOutOfBoundsException` | size the table for the actual alphabet |
| Counting with `right − left + 1` for an "at least" condition | counts the wrong side | add `left` instead |

---

## 10. Trick Questions and Special Cases

> [!question]- Longest substring without repeating characters in `"pwwkew"`: `"pwke"`, length 4?
> No, `3`. `"pwke"` isn't contiguous (it skips the second `w`), so it's a subsequence, not a substring. The longest substring is `"wke"` (or `"kew"`).

> [!question]- Jump version without `max` on `"abba"`?
> Returns `3` instead of `2`. At the final `a`, the last `a` was at index 0, which is already **outside** the window (`left = 2`). Setting `left = 1` moves the window backwards and includes both `b`s.

> [!question]- Why is the nested `while` loop still O(n)?
> `left` only increases and never exceeds `right + 1 ≤ n`. Over the whole run, the inner loop executes at most `n` times in total, however the iterations are distributed among values of `right`. The same amortized argument as for the monotonic stack.

> [!question]- Longest repeating character replacement: is it a bug that `maxFreq` is never decreased?
> No. The answer only increases when some window reaches a new highest letter frequency `f`, and then `f + k` is achievable. A stale `maxFreq` can stop the window from shrinking (it slides instead), but it can't make `best` exceed the largest `f + k` that was actually achieved. Decreasing it properly is also correct, just more work.

> [!question]- Count subarrays of `[1, 2, 1, 2, 3]` with exactly 2 distinct values.
> `7`: `[1,2]`, `[2,1]`, `[1,2]`, `[2,3]`, `[1,2,1]`, `[2,1,2]`, `[1,2,1,2]`. Computed as `atMost(2) − atMost(1) = 12 − 5`. A single window with "exactly 2" as its condition misses subarrays like `[2, 1]` in the middle, because the window doesn't know when to shrink.

> [!question]- Binary subarrays with sum 0 in `[0, 0, 0, 0, 0]`?
> `15`: all `5·6/2` subarrays. `atMost(0) = 15`, `atMost(−1) = 0`. Without the `goal < 0` guard, `atMost(−1)` loops `left` past `right` and either crashes or returns garbage.

> [!question]- Minimum window substring for `s = "a"`, `t = "aa"`?
> `""`. `t` needs two `a`s and `s` has one. Checking only whether each character of `t` **appears** in the window (a set instead of counts) wrongly returns `"a"`.

> [!question]- Shortest subarray with sum `≥ 3` in `[2, -1, 2, 1]` with the standard window?
> It returns `3` (`[2, −1, 2]`), but the answer is `2` (`[2, 1]`). With negatives, removing an element can increase the sum, so the window's shrink rule isn't justified. Use prefix sums with a monotonic deque.

> [!question]- Number of subarrays with product `< 0`?
> Not a sliding window: the sign flips with each negative factor, so validity isn't monotone. Count prefix parities instead: a subarray has a negative product when the number of negatives in it is odd (and it contains no zero), i.e. its two prefix parities differ.

> [!question]- Maximum points from cards `[9, 7, 7, 9, 7, 7, 9]` with `k = 7`?
> `55`, the total. The complement window has length `n − k = 0` and sum 0. Code that assumes `w ≥ 1` (initialising the minimum with `cards[0]`) breaks on this case.

> [!question]- Can a sliding window find the longest subarray with sum exactly `k` in `[1, −1, 5, −2, 3]`, `k = 3`?
> No: negative numbers. The answer is `4` (`[1, −1, 5, −2]`), found with prefix sums and a map from each prefix sum to its **first** index.

> [!question]- Sliding window median of `[2147483647, 2147483647]`, `k = 2`?
> `2147483647.0`. Averaging the two middle values as `(a + b) / 2.0` with `int` addition overflows to `−2` first and gives `−1.0`. Cast one operand to `double` (or `long`) before adding.

> [!question]- Fixed window over `"aaaa"` looking for anagrams of `"aa"`: how many?
> `3` (start indices 0, 1, 2). Matches overlap. Jumping the window forward by `k` after each match (as in some "find all occurrences" loops) would report only 2.

---

## 11. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| Variable window, total inner-loop iterations | `≤ n` | `left` only moves right |
| `lengthOfLongestSubstring("pwwkew")` | `3` | substring, not subsequence |
| `lengthOfLongestSubstring(" ")` | `1` | space is a character |
| Jump version on `"abba"` without `max` | `3` (wrong) | `left` moves back |
| `characterReplacement("AABABBA", 1)` | `4` | |
| `minWindow("a", "aa")` | `""` | counts, not presence |
| `minSubArrayLen(11, [1,1,1,1])` | `0` | none exists |
| `numSubarrayProductLessThanK([10,5,2,6], 100)` | `8` | `right − left + 1` per step |
| Exactly `k` | `atMost(k) − atMost(k − 1)` | |
| `numSubarraysWithSum([0,0,0,0,0], 0)` | `15` | needs `atMost(−1) = 0` |
| At least: subarrays ending at `right` | `left` | shrink while valid |
| `numberOfSubstrings("abcabc")` | `10` | |
| `maxSumK([-5, -2, -3], 2)` | `−7` | don't start from 0 |
| Sum window with negatives | unreliable | use prefix sums |
| Non-shrinking window, final `n − left` | the max length | window only grows when valid |
| Cards from both ends | complement window of `n − k` | |
| Median of `[MAX, MAX]` with `int` addition | `−1.0` | overflow |

---

## 12. Summary

- A sliding window maintains a summary of `a[left..right]` incrementally; each element enters and leaves once, so the scan is `O(n)`.
- **Fixed** windows: add `a[i]`, remove `a[i − k]`. Use counters (`nonZero`, distinct count) to make comparisons `O(1)`, a deque for max/min, two ordered halves for the median.
- **Longest valid**: expand, shrink while invalid, record after shrinking. **Shortest valid**: expand, record and shrink while valid.
- Validity must be **monotone**. Non-negative sums, "at most `k` distinct", and "no repeats" are; sums with negatives and "exactly `k`" are not.
- **Counting**: `right − left + 1` per step for at-most conditions; `left` per step for at-least conditions; `exactly(k) = atMost(k) − atMost(k − 1)`.
- If only the maximum length matters, the window never needs to shrink. If elements are removed from both ends, search the complement window in the middle.
- When the window doesn't fit (negatives, divisibility, parity), switch to prefix sums with hashing, a monotonic deque, or binary search.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]] · Next: [[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]]
- [[DSA/02 - Linear Data Structures/02 - Strings|Strings]]: frequency counting with one array
- [[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]]: sliding window maximum, windows with max − min limits
- [[DSA/02 - Linear Data Structures/06 - Hash Tables|Hash Tables]]: frequency maps and subarray sums
- [[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]]: the tool for negative numbers
- [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|Heaps and Priority Queues]]: sliding window median
