# Two Pointers

The <span class="hl-blue">two-pointer technique</span> walks two indices through a sequence (or through two sequences) so that each pointer only ever moves in **one direction**. Together they visit `O(n)` positions, so problems that look like they need all `O(n²)` pairs are solved in linear time.

The technique works when a comparison at the current positions proves that a whole group of pairs can be skipped: in a sorted array, if `a[i] + a[j]` is too small, then `a[i]` paired with anything left of `j` is too small too. This note covers the families: pointers moving toward each other (pair sums, containers, palindromes), the `k`-sum problems built on them, read/write pointers for in-place rewriting, fast/slow pointers on arrays, merging and intersecting two sorted sequences, and three-way partitioning. Two pointers that delimit a **contiguous range** form a sliding window, covered in [[DSA/03 - Sorting and Searching/04 - Sliding Window|Sliding Window]].

## Contents

- [[#1. The Idea|1. The Idea]]
- [[#2. Opposite Ends|2. Opposite Ends]]
- [[#3. k-Sum Problems|3. k-Sum Problems]]
- [[#4. Same Direction — Read and Write Pointers|4. Same Direction — Read and Write Pointers]]
- [[#5. Fast and Slow Pointers on Arrays|5. Fast and Slow Pointers on Arrays]]
- [[#6. Two Sequences|6. Two Sequences]]
- [[#7. Partitioning|7. Partitioning]]
- [[#8. Choosing an Approach|8. Choosing an Approach]]
- [[#9. Common Mistakes|9. Common Mistakes]]
- [[#10. Trick Questions and Special Cases|10. Trick Questions and Special Cases]]
- [[#11. Quick Reference — Non-Obvious Outcomes|11. Quick Reference — Non-Obvious Outcomes]]
- [[#12. Summary|12. Summary]]

---

## 1. The Idea

| Family | Pointers | Typical problems |
|---|---|---|
| **Opposite ends** | `i = 0`, `j = n − 1`, moving inward | pair sum in a sorted array, container with most water, palindrome check, reversing |
| **Same direction (read/write)** | `r` reads every element, `w` marks where the next kept element goes | remove duplicates, remove an element, move zeroes, compress |
| **Fast and slow** | one moves 1 step, the other 2 | cycle detection, find the duplicate number, middle of a list |
| **Two sequences** | one pointer per sequence | merge sorted arrays, intersection, interval intersections |
| **Partitioning** | 2 or 3 region boundaries | Dutch national flag, quicksort partition, parity partition |
| **Window** | `left` and `right` bounding a subarray | [[DSA/03 - Sorting and Searching/04 - Sliding Window|Sliding Window]] |

> [!important] Why it's O(n) and not O(n²)
> Each pointer moves in only one direction and never backs up, so together they make at most `2n` moves. The nested-looking `while` loops are an amortized argument, the same as in [[DSA/01 - Foundations/01 - Complexity Analysis#4.6 Two pointers — a nested loop that isn't quadratic|Complexity Analysis § 4.6]].
>
> **Correctness** is the hard part. A two-pointer algorithm skips pairs without looking at them, so for each move you need an argument why every skipped pair can't be the answer. If you can't state that argument, the algorithm is probably wrong.

---

## 2. Opposite Ends

### 2.1 Two sum in a sorted array

Find two elements of a sorted array that add up to `target`.

```
twoSumSorted(a, target):
    i = 0; j = n − 1
    while i < j:
        s = a[i] + a[j]
        if s == target: return (i, j)
        if s < target: i += 1        -- a[i] + (anything ≤ a[j]) < target: a[i] is useless
        else: j −= 1                 -- a[j] + (anything ≥ a[i]) > target: a[j] is useless
    return none
```

```java
static int[] twoSumSorted(int[] a, int target) {
    int i = 0, j = a.length - 1;
    while (i < j) {
        long sum = (long) a[i] + a[j];          // long: two ints near 2³¹ overflow
        if (sum == target) return new int[]{i, j};
        if (sum < target) i++;
        else j--;
    }
    return new int[]{-1, -1};
}
```

> [!important] The elimination argument
> Picture all pairs `(i, j)` with `i < j` as the upper triangle of an `n × n` grid. If `a[i] + a[j] < target`, then `a[i] + a[k] ≤ a[i] + a[j] < target` for every `k < j`, and the pairs `(i, k)` with `k > j` were already eliminated. So the whole **row** `i` is eliminated, and `i++` loses nothing. Symmetrically, a too-large sum eliminates the whole **column** `j`. Every step removes one row or one column, so after at most `n − 1` steps either the answer is found or nothing is left.

![[Two Pointers - Sorted Two Sum Elimination.excalidraw|800]]

This needs the array **sorted**. For an unsorted array returning original indices, a hash map is `O(n)` ([[DSA/02 - Linear Data Structures/06 - Hash Tables#9.1 Two sum (unsorted, return indices)|Hash Tables § 9.1]]); sorting first costs `O(n log n)` and loses the original indices unless you sort `(value, index)` pairs.

### 2.2 Counting pairs

**Count pairs with sum `< target`**: when `a[i] + a[j] < target`, `a[i]` pairs successfully with **every** element in `a[i+1..j]`, so add `j − i` at once and move `i`.

```java
static long countPairsLess(int[] a, int target) {     // a sorted
    long count = 0;
    int i = 0, j = a.length - 1;
    while (i < j) {
        if (a[i] + a[j] < target) { count += j - i; i++; }
        else j--;
    }
    return count;
}
```

Counting pairs with sum **exactly** `target` is harder with duplicates: when `a[i] + a[j] == target`, every copy of `a[i]` pairs with every copy of `a[j]`, so count the run lengths and multiply (or, if `a[i] == a[j]`, add `C(len, 2)` and stop). Often simpler: `count(< target + 1) − count(< target)`.

> [!example]- Valid triangle number: count triples that can form a triangle
> After sorting, `a[i] ≤ a[j] ≤ a[k]` form a triangle iff `a[i] + a[j] > a[k]` (the other two inequalities hold automatically). Fix the largest side `k` and count pairs in `a[0..k)` with sum `> a[k]`, the mirror image of the counting above.
> ```java
> static int triangleNumber(int[] nums) {
>     int[] a = nums.clone();
>     Arrays.sort(a);
>     int count = 0;
>     for (int k = a.length - 1; k >= 2; k--) {
>         int i = 0, j = k - 1;
>         while (i < j) {
>             if (a[i] + a[j] > a[k]) { count += j - i; j--; }   // a[i..j−1] all work with a[j]
>             else i++;
>         }
>     }
>     return count;
> }
> ```
> `[2, 2, 3, 4]` → `3`. Zeros never form a triangle: `[0, 0, 0]` → `0`, because `0 + 0 > 0` is false. `O(n²)` instead of `O(n³)`.

### 2.3 Container with most water

Given heights `h`, choose two lines that, with the x-axis, hold the most water: maximise `min(h[i], h[j]) × (j − i)`.

```java
static int maxArea(int[] h) {
    int i = 0, j = h.length - 1, best = 0;
    while (i < j) {
        best = Math.max(best, Math.min(h[i], h[j]) * (j - i));
        if (h[i] < h[j]) i++;        // move the SHORTER line
        else j--;
    }
    return best;
}
```

![[Two Pointers - Container With Most Water.excalidraw|800]]

> [!important] Why moving the shorter line is safe
> Say `h[i] < h[j]`. Any other container using line `i` is `(i, k)` with `i < k < j`: it's narrower, and its height is still at most `h[i]`. So none of them can beat the area just recorded, and line `i` can be discarded. Moving the **taller** line instead discards containers that could be larger. When `h[i] == h[j]`, moving either is safe: any container using one of them, inside the range, is narrower and no taller.

`[1, 8, 6, 2, 5, 4, 8, 3, 7]` → `49` (lines at indices 1 and 8: height 7, width 7).

### 2.4 Trapping rain water

The water above bar `i` is `min(maxLeft(i), maxRight(i)) − h[i]`. The prefix-max/suffix-max arrays compute this in `O(n)` space ([[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums]]); the stack version fills valleys layer by layer ([[DSA/02 - Linear Data Structures/04 - Stacks#9.3 Trapping rain water (stack version)|Stacks § 9.3]]). Two pointers need `O(1)` space:

```java
static int trap(int[] h) {
    int i = 0, j = h.length - 1, leftMax = 0, rightMax = 0, water = 0;
    while (i < j) {
        if (h[i] < h[j]) {                       // the right side has a wall taller than h[i]
            leftMax = Math.max(leftMax, h[i]);
            water += leftMax - h[i];             // bounded by leftMax
            i++;
        } else {
            rightMax = Math.max(rightMax, h[j]);
            water += rightMax - h[j];
            j--;
        }
    }
    return water;
}
```

Why it's correct: the pointer that moves is always at the **lower** of the two current bars. So every bar processed on the left was lower than some bar still on the right, and `leftMax ≤ maxRight(i)`. That means `min(maxLeft(i), maxRight(i)) = leftMax`, which is all the left side needs to know. `[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]` → `6`.

### 2.5 Merging from both ends: squares of a sorted array

`[-4, -1, 0, 3, 10]` → `[0, 1, 9, 16, 100]`. The squares are largest at the two **ends** (big negatives and big positives), so fill the result from the back, taking the larger of the two end squares.

```java
static int[] sortedSquares(int[] a) {
    int n = a.length;
    int[] res = new int[n];
    int i = 0, j = n - 1;
    for (int k = n - 1; k >= 0; k--) {
        if (Math.abs(a[i]) > Math.abs(a[j])) { res[k] = a[i] * a[i]; i++; }
        else { res[k] = a[j] * a[j]; j--; }
    }
    return res;
}
```

Filling from the front would need the **smallest** absolute value first, which is somewhere in the middle. `O(n)` instead of square-then-sort `O(n log n)`.

### 2.6 Greedy pairing: boats to save people

Each boat holds at most two people and `limit` weight. Sort; try to pair the **heaviest** remaining person with the **lightest**. If even the lightest doesn't fit with them, the heaviest goes alone.

```java
static int numRescueBoats(int[] people, int limit) {
    int[] p = people.clone();
    Arrays.sort(p);
    int i = 0, j = p.length - 1, boats = 0;
    while (i <= j) {                         // <=: a single person left still needs a boat
        if (p[i] + p[j] <= limit) i++;       // lightest rides along
        j--;                                 // heaviest always leaves
        boats++;
    }
    return boats;
}
```

`[3, 2, 2, 1], limit 3` → `3`. Pairing the heaviest with the lightest is optimal by an exchange argument: if the heaviest can share with anyone, it can share with the lightest, and swapping partners never makes another pair infeasible ([[DSA/06 - Algorithm Design Paradigms/01 - Greedy Algorithms|Greedy Algorithms]]).

### 2.7 Reversing and palindromes

Swap or compare `a[i]` and `a[j]`, then move both inward:

```java
static boolean isPalindrome(String s) {
    int i = 0, j = s.length() - 1;
    while (i < j) if (s.charAt(i++) != s.charAt(j--)) return false;
    return true;
}
```

The variants (skip non-alphanumerics, ignore case, allow one deletion) are in [[DSA/02 - Linear Data Structures/02 - Strings#7. Palindrome Basics|Strings § 7]]; reversing a range and rotation by three reversals are in [[DSA/02 - Linear Data Structures/01 - Arrays#6.1 Three reversals|Arrays § 6.1]].

---

## 3. k-Sum Problems

### 3.1 3Sum

Find all **unique** triples with sum `0`. Sort, fix the first element `a[k]`, then run two-sum on `a[k+1..n)` for `−a[k]`.

```
threeSum(a):
    sort a
    for k = 0 to n − 3:
        if k > 0 and a[k] == a[k − 1]: continue          -- same first element: same triples
        i = k + 1; j = n − 1
        while i < j:
            s = a[k] + a[i] + a[j]
            if s < 0: i += 1
            elif s > 0: j −= 1
            else:
                record (a[k], a[i], a[j])
                i += 1; j −= 1
                skip i past equal values; skip j past equal values
```

```java
static List<List<Integer>> threeSum(int[] nums) {
    int[] a = nums.clone();
    Arrays.sort(a);
    List<List<Integer>> res = new ArrayList<>();
    int n = a.length;
    for (int k = 0; k < n - 2; k++) {
        if (a[k] > 0) break;                              // three positives can't sum to 0
        if (k > 0 && a[k] == a[k - 1]) continue;
        int i = k + 1, j = n - 1;
        while (i < j) {
            int sum = a[k] + a[i] + a[j];
            if (sum < 0) i++;
            else if (sum > 0) j--;
            else {
                res.add(List.of(a[k], a[i], a[j]));
                i++; j--;
                while (i < j && a[i] == a[i - 1]) i++;    // skip duplicate second elements
                while (i < j && a[j] == a[j + 1]) j--;
            }
        }
    }
    return res;
}
```

`O(n²)` time, `O(1)` extra besides sorting and the output. `[-1, 0, 1, 2, -1, -4]` → `[[-1, -1, 2], [-1, 0, 1]]`; `[0, 0, 0, 0]` → `[[0, 0, 0]]`.

> [!warning] Deduplication
> - Skip the first element with `a[k] == a[k − 1]` (compare to the **previous**, so the first occurrence is still used). Comparing to `a[k + 1]` skips the first copy instead and loses triples like `[-1, -1, 2]` that need two copies.
> - After a match, skip duplicates of `a[i]` and `a[j]` **inside** the two-sum loop. Skipping them before checking misses triples that use the duplicate.
> - Collecting the triples into a `HashSet<List<Integer>>` also works, but hides a sloppy loop and costs extra memory.

### 3.2 3Sum closest

Track the sum closest to `target`; move pointers as in 3Sum. No deduplication needed, since only the value is returned.

```java
static int threeSumClosest(int[] nums, int target) {
    int[] a = nums.clone();
    Arrays.sort(a);
    int best = a[0] + a[1] + a[2];
    for (int k = 0; k < a.length - 2; k++) {
        int i = k + 1, j = a.length - 1;
        while (i < j) {
            int sum = a[k] + a[i] + a[j];
            if (Math.abs(sum - target) < Math.abs(best - target)) best = sum;
            if (sum < target) i++;
            else if (sum > target) j--;
            else return sum;                             // can't get closer than exact
        }
    }
    return best;
}
```

### 3.3 4Sum and k-Sum

Add one more outer loop per extra element: `kSum` is `O(n^(k−1))`. For 4Sum, both outer loops skip duplicates, the second one relative to its own starting position.

```java
static List<List<Integer>> fourSum(int[] nums, int target) {
    int[] a = nums.clone();
    Arrays.sort(a);
    List<List<Integer>> res = new ArrayList<>();
    int n = a.length;
    for (int p = 0; p < n - 3; p++) {
        if (p > 0 && a[p] == a[p - 1]) continue;
        for (int q = p + 1; q < n - 2; q++) {
            if (q > p + 1 && a[q] == a[q - 1]) continue;  // q > p + 1, NOT q > 0
            int i = q + 1, j = n - 1;
            while (i < j) {
                long sum = (long) a[p] + a[q] + a[i] + a[j];
                if (sum < target) i++;
                else if (sum > target) j--;
                else {
                    res.add(List.of(a[p], a[q], a[i], a[j]));
                    i++; j--;
                    while (i < j && a[i] == a[i - 1]) i++;
                    while (i < j && a[j] == a[j + 1]) j--;
                }
            }
        }
    }
    return res;
}
```

> [!warning] 4Sum overflows `int`
> `[10⁹, 10⁹, 10⁹, 10⁹]` with target `−294967296`: the `int` sum `4·10⁹` wraps to exactly `−294967296`, so an `int` version reports a quadruple that doesn't exist. Cast to `long` **before** the first addition: `(long) a[p] + a[q] + …`. Writing `(long) (a[p] + a[q] + a[i] + a[j])` casts after the overflow has already happened.

> [!warning] `q > 0` instead of `q > p + 1`
> The inner duplicate check must only skip **repeated choices for the second element**. With `q > 0`, the first valid `q = p + 1` is skipped whenever `a[p + 1] == a[p]`, losing quadruples like `[2, 2, 2, 2]`.

**4Sum count across four arrays** ("how many `(i, j, k, l)` with `A[i] + B[j] + C[k] + D[l] == 0`") is a hash map problem, not two pointers: count all `A + B` sums in a map, then look up `−(C + D)`. `O(n²)` ([[DSA/06 - Algorithm Design Paradigms/07 - Meet in the Middle|Meet in the Middle]]).

---

## 4. Same Direction — Read and Write Pointers

`r` scans every element; `w` is the length of the output built so far in the same array. Kept elements are copied to `a[w++]`. Because `w ≤ r` always, writing never overwrites an element that hasn't been read.

### 4.1 Remove duplicates from a sorted array, keeping at most `k` copies

```
removeDuplicates(a, k):
    w = 0
    for x in a:
        if w < k or a[w − k] ≠ x:            -- fewer than k copies of x in the output so far
            a[w] = x; w += 1
    return w                                 -- new length; a[0..w) is the result
```

```java
static int removeDuplicates(int[] a, int k) {
    int w = 0;
    for (int x : a)
        if (w < k || a[w - k] != x) a[w++] = x;
    return w;
}
```

![[Two Pointers - Read Write Pointers.excalidraw|800]]

With `k = 1`, this is the classic "remove duplicates" (`a[w − 1] ≠ x`). Comparing with the **output** (`a[w − k]`), not the input (`a[r − k]`), is what makes it correct: the input at `r − k` may already have been overwritten. `[0, 0, 1, 1, 1, 1, 2, 3, 3]` with `k = 2` → length `7`, `[0, 0, 1, 1, 2, 3, 3]`.

### 4.2 Remove an element, move zeroes

Two versions of "remove every `val`", depending on whether order matters:

```java
// order preserved: copy kept elements forward (Arrays § 5.3)
int w = 0;
for (int r = 0; r < a.length; r++) if (a[r] != val) a[w++] = a[r];

// order not preserved: overwrite a removed element with the LAST element
static int removeElement(int[] a, int val) {
    int i = 0, n = a.length;
    while (i < n) {
        if (a[i] == val) a[i] = a[--n];      // don't advance i: the moved element is unchecked
        else i++;
    }
    return n;
}
```

The second version writes only once per **removed** element, which is better when removals are rare.

**Move zeroes** to the end keeping the order of the others: the swap version moves each non-zero to `a[w]` and the zero that was there to `a[r]` in one pass.

```java
static void moveZeroes(int[] a) {
    int w = 0;
    for (int r = 0; r < a.length; r++)
        if (a[r] != 0) swap(a, w++, r);
}
```

### 4.3 Backspace string compare in O(1) space

`"ab#c"` and `"ad#c"` both type `"ac"`. A stack solves it in `O(n)` space ([[DSA/02 - Linear Data Structures/04 - Stacks#7.1 Cancel adjacent pairs|Stacks § 7.1]]). Scanning from the **right** avoids it: a `#` means "skip the next real character to the left".

```java
static boolean backspaceCompare(String s, String t) {
    int i = s.length() - 1, j = t.length() - 1;
    while (true) {
        i = nextKept(s, i);
        j = nextKept(t, j);
        if (i < 0 || j < 0) return i < 0 && j < 0;      // both exhausted together?
        if (s.charAt(i) != t.charAt(j)) return false;
        i--; j--;
    }
}

static int nextKept(String s, int i) {       // index of the next surviving char at or left of i
    int skip = 0;
    while (i >= 0) {
        if (s.charAt(i) == '#') { skip++; i--; }
        else if (skip > 0) { skip--; i--; }
        else break;
    }
    return i;
}
```

Edge cases: `"ab##"` vs `"c#d#"` → both empty, `true`; `"a##c"` vs `"#a#c"` → both `"c"`, `true` (backspace on an empty string does nothing).

---

## 5. Fast and Slow Pointers on Arrays

An array whose values are valid indices defines a function `i → a[i]`, and following it from any start eventually enters a cycle: a **linked list in disguise**. Floyd's cycle detection from [[DSA/02 - Linear Data Structures/03 - Linked Lists|Linked Lists]] applies directly.

### 5.1 Find the duplicate number

`n + 1` numbers in `1..n`, exactly one value repeated (possibly many times). Find it in `O(n)` time and `O(1)` space **without modifying** the array.

Start at index 0 (no value points to 0, since values are `≥ 1`, so 0 is outside the cycle). The duplicate value `d` has two (or more) indices pointing to it, so `d` is the **entrance** of the cycle.

```java
static int findDuplicate(int[] a) {
    int slow = 0, fast = 0;
    do { slow = a[slow]; fast = a[a[fast]]; } while (slow != fast);   // meet inside the cycle
    slow = 0;
    while (slow != fast) { slow = a[slow]; fast = a[fast]; }          // meet at the entrance
    return slow;
}
```

`[1, 3, 4, 2, 2]` → `2`; `[3, 1, 3, 4, 2]` → `3`. The constraints are what rule out the easy answers: sorting or marking signs ([[DSA/02 - Linear Data Structures/01 - Arrays#7.2 Sign marking|Arrays § 7.2]]) modifies the array, a set uses `O(n)` space, and the sum formula fails when the duplicate appears more than twice. A binary search on the value (count elements `≤ mid`; pigeonhole) is an `O(n log n)` alternative that also meets the constraints.

### 5.2 Happy number and other implicit sequences

Any process `x → f(x)` on a finite set eventually cycles. "Is `n` a happy number?" (repeatedly replace by the sum of squares of digits; happy if it reaches 1) is "does the sequence reach the fixed point 1, or a different cycle?". Fast/slow detects the cycle in `O(1)` space; a `HashSet` of seen values is the `O(cycle length)` space alternative.

---

## 6. Two Sequences

One pointer per sorted sequence; at each step, advance the pointer at the **smaller** value.

### 6.1 Merge two sorted arrays in place (into the first)

`a` has length `m + n` with `m` real elements followed by `n` free slots; merge `b` into it.

```java
static void mergeInto(int[] a, int m, int[] b, int n) {
    int i = m - 1, j = n - 1, k = m + n - 1;
    while (j >= 0) {                                // when b is used up, a's rest is already in place
        if (i >= 0 && a[i] > b[j]) a[k--] = a[i--];
        else a[k--] = b[j--];
    }
}
```

Fill from the **back**: the largest remaining element goes to the last free slot. Merging from the front would overwrite `a`'s unread elements. The loop condition is `j >= 0`, not `i >= 0 && j >= 0`: if `a` runs out first, the rest of `b` still has to be copied; if `b` runs out first, nothing remains to do.

### 6.2 Intersection of two sorted arrays

```java
static List<Integer> intersectSorted(int[] a, int[] b) {     // with multiplicity
    List<Integer> res = new ArrayList<>();
    int i = 0, j = 0;
    while (i < a.length && j < b.length) {
        if (a[i] < b[j]) i++;
        else if (a[i] > b[j]) j++;
        else { res.add(a[i]); i++; j++; }
    }
    return res;
}
```

`[1, 2, 2, 3, 5]` and `[2, 2, 2, 5, 7]` → `[2, 2, 5]`. For distinct values only, skip duplicates after a match. When one array is much shorter (`m ≪ n`), binary-searching each of its elements in the longer one is `O(m log n)`, better than `O(m + n)`.

### 6.3 Interval list intersections

Two lists of disjoint, sorted closed intervals. The intersection of `A[i]` and `B[j]` is `[max(starts), min(ends)]` if non-empty. Then discard the interval that **ends first**: it can't intersect anything further in the other list.

```java
static int[][] intervalIntersection(int[][] A, int[][] B) {
    List<int[]> res = new ArrayList<>();
    int i = 0, j = 0;
    while (i < A.length && j < B.length) {
        int lo = Math.max(A[i][0], B[j][0]);
        int hi = Math.min(A[i][1], B[j][1]);
        if (lo <= hi) res.add(new int[]{lo, hi});    // <=: closed intervals touching at a point
        if (A[i][1] < B[j][1]) i++;
        else j++;
    }
    return res.toArray(new int[0][]);
}
```

`A = [[0,2],[5,10],[13,23],[24,25]]`, `B = [[1,5],[8,12],[15,24],[25,26]]` → `[[1,2],[5,5],[8,10],[15,23],[24,24],[25,25]]`. The single-point intersections `[5,5]`, `[24,24]`, `[25,25]` are easy to lose with `<`.

### 6.4 Smallest difference between two arrays

Sort both; the closest pair must be "adjacent" in the merged order, so walk both like a merge and check `|a[i] − b[j]|` at every step.

```java
static long smallestDifference(int[] x, int[] y) {
    int[] a = x.clone(), b = y.clone();
    Arrays.sort(a); Arrays.sort(b);
    long best = Long.MAX_VALUE;
    int i = 0, j = 0;
    while (i < a.length && j < b.length) {
        best = Math.min(best, Math.abs((long) a[i] - b[j]));   // long: the difference can overflow
        if (a[i] < b[j]) i++;          // only a larger a[i] can get closer to b[j]
        else j++;
    }
    return best;
}
```

`[1, 3, 15, 11, 2]` and `[23, 127, 235, 19, 8]` → `3` (`11` and `8`).

### 6.5 Subsequence check and pairs with a given difference

- **Is `s` a subsequence of `t`?** Advance through `t`, and advance in `s` on each match ([[DSA/02 - Linear Data Structures/02 - Strings|Strings § 8.6]]).
- **Count unique pairs with difference `k`** in an array: sort, then for each distinct `a[i]` move a second pointer `j` forward (never back) until `a[j] − a[i] ≥ k`.

```java
static int findPairs(int[] nums, int k) {           // unique pairs (x, x + k), k ≥ 0
    int[] a = nums.clone();
    Arrays.sort(a);
    int count = 0, j = 0;
    for (int i = 0; i < a.length; i++) {
        if (i > 0 && a[i] == a[i - 1]) continue;    // each value of x once
        j = Math.max(j, i + 1);                     // j > i: an element can't pair with itself
        while (j < a.length && (long) a[j] - a[i] < k) j++;
        if (j < a.length && (long) a[j] - a[i] == k) count++;
    }
    return count;
}
```

`[3, 1, 4, 1, 5], k = 2` → `2` (`(1, 3)` and `(3, 5)`). `k = 0` counts values that occur at least twice: `[1, 3, 1, 5, 4]` → `1`. The `j > i` rule is what makes `k = 0` work; without it, every element pairs with itself.

---

## 7. Partitioning

### 7.1 Dutch national flag (three-way partition)

Sort an array of `0`s, `1`s, and `2`s in one pass. Maintain four regions:

```
a[0..lo)    = 0
a[lo..mid)  = 1
a[mid..hi]  = unknown
a(hi..n)    = 2
```

```
sortColors(a):
    lo = 0; mid = 0; hi = n − 1
    while mid ≤ hi:
        if a[mid] == 0: swap(a[lo], a[mid]); lo += 1; mid += 1
        elif a[mid] == 2: swap(a[mid], a[hi]); hi −= 1       -- don't advance mid
        else: mid += 1
```

```java
static void sortColors(int[] a) {
    int lo = 0, mid = 0, hi = a.length - 1;
    while (mid <= hi) {
        if (a[mid] == 0) swap(a, lo++, mid++);
        else if (a[mid] == 2) swap(a, mid, hi--);
        else mid++;
    }
}
```

![[Two Pointers - Dutch National Flag.excalidraw|800]]

> [!warning] The two asymmetries
> - After swapping with `hi`, **don't** advance `mid`: the element that came from `a[hi]` hasn't been examined yet.
> - After swapping with `lo`, **do** advance `mid`: the element that came from `a[lo]` was already examined (it's a `1`, or it's the same element when `lo == mid`).
> - The loop condition is `mid <= hi`: `a[hi]` itself is still unknown.

Counting sort (count the 0s, 1s, 2s, then overwrite) is also `O(n)` but takes two passes; the flag algorithm works on any three-way split by a pivot, which is how three-way quicksort handles duplicates ([[DSA/03 - Sorting and Searching/01 - Sorting Algorithms#4.4 Equal keys and three-way partitioning|Sorting Algorithms § 4.4]]).

### 7.2 Two-way partition (Hoare style)

Move evens before odds: `i` searches from the left for an odd, `j` from the right for an even, and they swap.

```java
static void partitionByParity(int[] a) {
    int i = 0, j = a.length - 1;
    while (i < j) {
        if (a[i] % 2 == 0) i++;                  // already on the correct side
        else if (a[j] % 2 != 0) j--;             // != 0, not == 1: negatives give −1
        else swap(a, i++, j--);
    }
}
```

`a[j] % 2 == 1` would be false for negative odd numbers (`−3 % 2 == −1` in Java), so they'd be treated as even. The same shape partitions around any predicate: negatives before positives, vowels before consonants, values `< pivot` before `≥ pivot`. Like quicksort's partition, it is **not stable**; the read/write version of [[#4.2 Remove an element, move zeroes|§4.2]] is stable but only moves one class.

---

## 8. Choosing an Approach

| Problem shape | Two pointers | Alternative |
|---|---|---|
| Pair with sum `= t`, **sorted** | `O(n)`, `O(1)` space | binary search per element: `O(n log n)` |
| Pair with sum `= t`, unsorted, need indices | sort `(value, index)`: `O(n log n)` | **hash map: `O(n)`** |
| Count pairs with sum `< t` | sort + two pointers: `O(n log n)` | hash map can't do `<` |
| All unique triples (3Sum) | `O(n²)` | hash set per `k`: `O(n²)` with more memory and harder dedup |
| Subarray sum `= k` with negatives | doesn't work | prefix sums + hash map |
| Longest subarray satisfying a monotone condition | sliding window (two pointers) | |
| Merge / intersect sorted sequences | `O(m + n)` | binary search if one is tiny |

> [!tip] Signals for two pointers
> The input is sorted (or sorting is allowed and indices don't matter); the question is about **pairs**, triples, or a partition; or the answer must be built **in place** with `O(1)` extra space. If the problem mentions a contiguous subarray with a condition that only gets "more violated" as it grows, it's a sliding window.

---

## 9. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Two pointers on an unsorted array | misses pairs, wrong counts | sort first (or use a hash map) |
| `while (i <= j)` in pair problems | element paired with itself | `i < j` (but `<=` in boats: a lone person needs a boat) |
| `int` sum of two/four large values | overflow, phantom matches | `long` before adding |
| `(long) (a + b)` | cast after the overflow | `(long) a + b` |
| 3Sum dedup with `a[k] == a[k + 1]` | loses triples with repeated values | compare with `a[k − 1]` |
| 4Sum inner dedup with `q > 0` | loses `[2, 2, 2, 2]`-style answers | `q > p + 1` |
| Moving the taller line in container | misses the optimum | move the shorter one |
| Advancing `mid` after swapping with `hi` | unexamined element skipped | only advance after `lo` swaps or a `1` |
| Merging into `a` from the front | overwrites unread elements | merge from the back |
| Merge loop `while (i >= 0 && j >= 0)` with nothing after it | leftover `b` elements lost | loop on `j >= 0` |
| Read/write dedup comparing with `a[r − k]` | compares with overwritten data | compare with the output `a[w − k]` |
| `x % 2 == 1` to test odd | negative odd numbers treated as even | `x % 2 != 0` |
| Interval intersection with `lo < hi` | single-point intersections lost | `lo <= hi` for closed intervals |
| Pairs with difference `k = 0` without `j > i` | every element pairs with itself | start `j` at `i + 1` |

---

## 10. Trick Questions and Special Cases

> [!question]- Two sum on a sorted array: why can the pointer at the smaller end be discarded when the sum is too small?
> Because every other partner it could have is at most `a[j]` (the partners to the right of `j` have already been ruled out), so its sum with any of them is at most `a[i] + a[j]`, still too small. One comparison eliminates `a[i]`'s entire row of pairs; that's why `n − 1` steps suffice for `n(n−1)/2` pairs.

> [!question]- `countPairsLess([-1, 1, 2, 3, 1], 2)` without sorting first?
> It returns `4`; the true count is `3` (`−1` with `1`, `2`, and the other `1`). Two pointers silently give wrong answers on unsorted input; there's no exception. Sort first: `[-1, 1, 1, 2, 3]` gives `3`.

> [!question]- Container with most water `[1, 1]`? `[1, 2, 1]`?
> `1` and `2`. In `[1, 2, 1]` the best container uses the two outer lines of height 1 (width 2, area 2), not the tall middle line; the area depends on the **shorter** line and the width, not on the tallest line.

> [!question]- `fourSum([1000000000, 1000000000, 1000000000, 1000000000], -294967296)`?
> `[]`. The `int` sum `4·10⁹` overflows to exactly `−294967296`, so an `int` implementation returns `[[10⁹, 10⁹, 10⁹, 10⁹]]`. This is a real LeetCode test case.

> [!question]- `threeSum([0, 0, 0, 0])`?
> `[[0, 0, 0]]`, one triple. Without deduplication of the first element and of the inner pointers, the same triple is reported several times.

> [!question]- Boats to save people: `[3, 5, 3, 4]`, limit `5`?
> `4`: no two people fit together (`3 + 3 = 6 > 5`), so everyone rides alone. The loop condition `i <= j` matters: with `i < j`, the last person (when `i == j`) never gets a boat.

> [!question]- Remove duplicates in place from `[1, 1, 2]`: what's in the array afterwards?
> `[1, 2, 2]` with returned length `2`. Only `a[0..w)` is meaningful; the tail keeps whatever was there. Problems that check "the first `k` elements" accept any tail, and code that prints the whole array looks wrong.

> [!question]- Find the duplicate in `[2, 2, 2, 2, 2]` (n = 4)?
> `2`. The repeated value can appear many times, which breaks the "sum of `1..n`" and XOR tricks (they assume exactly two copies). Floyd's cycle detection doesn't care: index 0 leads to `2`, and `2 → 2` is a self-loop, which is the cycle's entrance.

> [!question]- Why does `findDuplicate` start at index 0 and not at `a[0]`?
> Index 0 is guaranteed to be outside the cycle (no value is 0, so nothing points to it). Starting outside makes the "meet again at the entrance" step land on the duplicate. Starting the second phase from `a[0]` instead of `0` shifts the walk by one step and returns the wrong value.

> [!question]- Sort colors `[2, 0, 1]`: trace the flag algorithm.
> `mid = 0`: `a[0] = 2` → swap with `hi = 2` → `[1, 0, 2]`, `hi = 1`, `mid` stays 0. `a[0] = 1` → `mid = 1`. `a[1] = 0` → swap with `lo = 0` → `[0, 1, 2]`, `lo = 1`, `mid = 2`. `mid > hi`: done. Advancing `mid` after the first swap would have left the `1` unexamined at index 0, giving `[1, 0, 2]`.

> [!question]- Backspace compare `"a##c"` vs `"#a#c"`?
> `true`: both type `"c"`. A `#` on an empty buffer does nothing. A right-to-left scan handles this naturally; a left-to-right scan that decrements a length counter must clamp it at zero.

> [!question]- Merge `a = [0]` (`m = 0`) with `b = [1]` (`n = 1`)?
> `a` becomes `[1]`. With `m = 0`, `i` starts at `−1`, so the `a[i]` comparison must be guarded by `i >= 0`, and the loop must run on `j >= 0` alone. Code that loops while both are non-negative copies nothing.

> [!question]- Is 3Sum faster with a hash set than with two pointers?
> No, both are `O(n²)`. The hash version has larger constants, needs extra memory, and makes deduplication harder. Two pointers after sorting is the standard. (3Sum is believed to need about `n²` time in general; this is the "3SUM-hard" conjecture.)

---

## 11. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| Two pointers, total moves | `≤ n` | each pointer moves one way |
| Pair sum on unsorted input | silently wrong | needs sorted order |
| Count pairs with sum `< t`, per step | add `j − i` | all of `a[i+1..j]` work |
| `maxArea([1, 8, 6, 2, 5, 4, 8, 3, 7])` | `49` | |
| `trap([0,1,0,2,1,0,1,3,2,1,2,1])` | `6` | |
| `sortedSquares([-4, -1, 0, 3, 10])` | `[0, 1, 9, 16, 100]` | fill from the back |
| `threeSum([0, 0, 0, 0])` | `[[0, 0, 0]]` | dedup |
| `fourSum([10⁹ ×4], −294967296)` | `[]` | `long` sum |
| k-Sum with two pointers | `O(n^(k−1))` | |
| `removeDuplicates([0,0,1,1,1,1,2,3,3], 2)` | `7` | compare with `a[w − 2]` |
| `findDuplicate([2, 2, 2, 2, 2])` | `2` | Floyd from index 0 |
| `findPairs([1, 3, 1, 5, 4], 0)` | `1` | `j > i` |
| `−3 % 2` in Java | `−1` | sign follows the dividend |
| Interval intersections that touch | `[5, 5]` | closed intervals: `<=` |
| `numRescueBoats([3, 5, 3, 4], 5)` | `4` | nobody can share |
| `triangleNumber([0, 0, 0])` | `0` | `0 + 0 > 0` is false |

---

## 12. Summary

- Two pointers replace a scan over all `O(n²)` pairs with `O(n)` moves, because each comparison eliminates a whole row or column of pairs. State that elimination argument for every move.
- **Opposite ends** on sorted data: pair sums, counting pairs (`+= j − i`), container with most water (move the shorter line), trapping rain water (process the lower side), squares of a sorted array (fill from the back), greedy pairing.
- **k-Sum**: sort, fix `k − 2` elements, two-pointer the rest: `O(n^(k−1))`. Deduplicate against the previous element; use `long` for 4Sum.
- **Read/write pointers** rewrite arrays in place; compare against the output (`a[w − k]`), not the input.
- **Fast/slow** pointers find cycles in index-valued arrays (find the duplicate number).
- **Two sequences**: advance the smaller side; merge in place from the back; discard the interval that ends first.
- **Partitioning**: Dutch national flag with `lo`, `mid`, `hi`; don't advance `mid` after a swap with `hi`.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]] · Next: [[DSA/03 - Sorting and Searching/04 - Sliding Window|Sliding Window]]
- [[DSA/02 - Linear Data Structures/01 - Arrays|Arrays]]: write-pointer removal, reversal, rotation
- [[DSA/02 - Linear Data Structures/03 - Linked Lists|Linked Lists]]: fast/slow pointers, Floyd's algorithm
- [[DSA/02 - Linear Data Structures/06 - Hash Tables|Hash Tables]]: two sum on unsorted input
- [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms|Sorting Algorithms]]: merging, partitioning, three-way quicksort
- [[DSA/03 - Sorting and Searching/04 - Sliding Window|Sliding Window]]: two pointers that delimit a subarray
- [[DSA/08 - Specialized Topics/01 - Intervals and Sweep Line|Intervals and Sweep Line]]: merging and intersecting intervals
