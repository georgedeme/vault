# Backtracking

<span class="hl-blue">Backtracking</span> builds candidate solutions one choice at a time and abandons a partial candidate (**backtracks**) as soon as it can't be completed into a valid solution. It's a depth-first search over an implicit tree of choices, the <span class="hl-blue">state-space tree</span>, where each node is a partial solution and each edge is one choice. It's the standard tool for "generate all …" problems (subsets, permutations, combinations, partitions) and for constraint puzzles (N-queens, sudoku), where the answer is exponential in size or the search space has no structure that DP could exploit.

This note covers the choose / explore / unchoose template, the three core enumerations (subsets, permutations, combinations) with and without duplicates, string-building problems, grid searches, N-queens and sudoku (with bitmasks), pruning strategies, the size of each search space, and the Java mistakes that break backtracking code silently. The include/exclude subsets recursion in [[DSA/01 - Foundations/02 - Recursion#6.3 Generating all subsets (include / exclude)|Recursion § 6.3]] is the starting point.

## Contents

- [[#1. The Template|1. The Template]]
- [[#2. Subsets|2. Subsets]]
- [[#3. Permutations|3. Permutations]]
- [[#4. Combinations|4. Combinations]]
- [[#5. Building Strings|5. Building Strings]]
- [[#6. Grid Search|6. Grid Search]]
- [[#7. N-Queens|7. N-Queens]]
- [[#8. Sudoku Solver|8. Sudoku Solver]]
- [[#9. Pruning Strategies|9. Pruning Strategies]]
- [[#10. How Big Is the Search?|10. How Big Is the Search?]]
- [[#11. Common Mistakes|11. Common Mistakes]]
- [[#12. Trick Questions and Special Cases|12. Trick Questions and Special Cases]]
- [[#13. Quick Reference — Non-Obvious Outcomes|13. Quick Reference — Non-Obvious Outcomes]]
- [[#14. Summary|14. Summary]]

---

## 1. The Template

```
backtrack(state):
    if state is a complete solution:
        record a COPY of it
        return
    for each choice c available in state:
        if c can't lead to a valid solution: continue     -- prune
        apply c to state                                   -- choose
        backtrack(state)                                   -- explore
        undo c                                             -- unchoose
```

> [!important] The undo step is the whole point
> One mutable `state` (a list, a `StringBuilder`, a board) is shared by the entire search. After a recursive call returns, the state must be **exactly** what it was before the choice, so that the next choice in the loop starts from the right place. Every "apply" needs a matching "undo" on every path out of the call, including early returns.

Three questions define any backtracking solution:

1. **What is the state?** The partial answer plus whatever makes the checks fast (`used[]`, column/diagonal flags, the remaining sum).
2. **What are the choices at each step?** Which element comes next, whether to take an element, which digit goes in a cell.
3. **When is a branch dead?** The earlier a dead branch is recognised, the smaller the tree ([[#9. Pruning Strategies|§9]]).

There are two ways to lay out the choices, and most problems fit one of them:

| Layout | Each level decides | Leaves | Typical use |
|---|---|---|---|
| **Include / exclude** | whether element `i` is in | `2ⁿ`, all at depth `n` | subsets, target-sum assignments |
| **Pick the next item** (loop from `start`) | which element comes next | every node can be an answer | subsets, combinations, permutations |

---

## 2. Subsets

### 2.1 The loop form

Each node of the tree is a subset; its children extend it with an element **after** the last one chosen (the `start` index prevents producing `{1, 2}` and `{2, 1}` separately).

```java
static List<List<Integer>> subsetsByStart(int[] a) {
    List<List<Integer>> res = new ArrayList<>();
    subsetsFrom(a, 0, new ArrayList<>(), res);
    return res;
}

static void subsetsFrom(int[] a, int start, List<Integer> path, List<List<Integer>> res) {
    res.add(new ArrayList<>(path));                // every node is a subset: record it
    for (int i = start; i < a.length; i++) {
        path.add(a[i]);                            // choose
        subsetsFrom(a, i + 1, path, res);          // explore: only later elements
        path.remove(path.size() - 1);              // unchoose
    }
}
```

`[1, 2, 3]` → `[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]`: 8 subsets, in this order. Without recursion, the subsets are the bitmasks `0 … 2ⁿ − 1` ([[DSA/01 - Foundations/03 - Bit Manipulation#7.1 Enumerating all subsets|Bit Manipulation § 7.1]]).

### 2.2 Subsets with duplicates

For `[1, 2, 2]`, choosing "the first 2" or "the second 2" as the next element gives the same subsets. **Sort**, then at each level skip an element equal to the one tried just before it **at the same level**:

```java
static List<List<Integer>> subsetsWithDup(int[] nums) {
    int[] a = nums.clone();
    Arrays.sort(a);                                // equal values must be adjacent
    List<List<Integer>> res = new ArrayList<>();
    subsetsDup(a, 0, new ArrayList<>(), res);
    return res;
}

static void subsetsDup(int[] a, int start, List<Integer> path, List<List<Integer>> res) {
    res.add(new ArrayList<>(path));
    for (int i = start; i < a.length; i++) {
        if (i > start && a[i] == a[i - 1]) continue;   // this value was already tried at this level
        path.add(a[i]);
        subsetsDup(a, i + 1, path, res);
        path.remove(path.size() - 1);
    }
}
```

![[Backtracking - Skipping Duplicates.excalidraw|800]]

`[1, 2, 2]` → `[], [1], [1,2], [1,2,2], [2], [2,2]`: 6, not 8. The condition is `i > start`, not `i > 0`: at `i == start` the element is the **first** choice at this level, so taking a second `2` right after a first `2` (deeper in the same branch) is allowed, and that's how `[2, 2]` is produced.

> [!warning] Deduplicating with a `Set<List<Integer>>` instead
> It works, but it still explores every duplicate branch (exponentially many for inputs like `[2, 2, 2, …]`) and then pays to hash each result. The skip rule never generates them in the first place.

---

## 3. Permutations

### 3.1 With a `used[]` array

Every position can hold any element not used yet. The tree has `n` choices at the top, `n − 1` below, …, so `n!` leaves.

```
permute(path):
    if |path| = n: record a copy; return
    for i = 0 .. n−1:
        if used[i]: continue
        used[i] = true; path.add(a[i])
        permute(path)
        path.removeLast(); used[i] = false
```

```java
static List<List<Integer>> permute(int[] a) {
    List<List<Integer>> res = new ArrayList<>();
    permuteRec(a, new boolean[a.length], new ArrayList<>(), res);
    return res;
}

static void permuteRec(int[] a, boolean[] used, List<Integer> path, List<List<Integer>> res) {
    if (path.size() == a.length) { res.add(new ArrayList<>(path)); return; }
    for (int i = 0; i < a.length; i++) {
        if (used[i]) continue;
        used[i] = true; path.add(a[i]);            // choose
        permuteRec(a, used, path, res);            // explore
        path.remove(path.size() - 1); used[i] = false;   // unchoose, in reverse order
    }
}
```

![[Backtracking - Permutations Tree.excalidraw|800]]

### 3.2 By swapping in place

Fix position `k` by swapping each candidate into it, recurse on `k + 1`, and swap back. No `used[]` and no `path`: the array itself is the state.

```java
static List<List<Integer>> permuteBySwap(int[] nums) {
    List<List<Integer>> res = new ArrayList<>();
    permuteSwap(nums.clone(), 0, res);
    return res;
}

static void permuteSwap(int[] a, int k, List<List<Integer>> res) {
    if (k == a.length) {
        List<Integer> p = new ArrayList<>();
        for (int x : a) p.add(x);
        res.add(p);
        return;
    }
    for (int i = k; i < a.length; i++) {
        swapInts(a, k, i);                         // a[i] goes to position k
        permuteSwap(a, k + 1, res);
        swapInts(a, k, i);                         // swap back
    }
}

static void swapInts(int[] a, int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }
```

`[1, 2, 3]` → `[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,2,1], [3,1,2]`. The last two are **not** in lexicographic order: swapping `3` to the front leaves `[3, 2, 1]`, not `[3, 1, 2]`. Use the `used[]` version (on sorted input) when the order matters.

### 3.3 Permutations with duplicates

Sort, and among equal values, only ever use them **left to right**: skip `a[i]` if it equals `a[i − 1]` and `a[i − 1]` isn't currently in the path.

```java
static List<List<Integer>> permuteUnique(int[] nums) {
    int[] a = nums.clone();
    Arrays.sort(a);
    List<List<Integer>> res = new ArrayList<>();
    permuteUniqueRec(a, new boolean[a.length], new ArrayList<>(), res);
    return res;
}

static void permuteUniqueRec(int[] a, boolean[] used, List<Integer> path, List<List<Integer>> res) {
    if (path.size() == a.length) { res.add(new ArrayList<>(path)); return; }
    for (int i = 0; i < a.length; i++) {
        if (used[i]) continue;
        if (i > 0 && a[i] == a[i - 1] && !used[i - 1]) continue;   // equal copies in order only
        used[i] = true; path.add(a[i]);
        permuteUniqueRec(a, used, path, res);
        path.remove(path.size() - 1); used[i] = false;
    }
}
```

`[1, 1, 2]` → `[1,1,2], [1,2,1], [2,1,1]`. The number of distinct permutations is `n! / (c₁! · c₂! · …)` for value counts `cᵢ`.

> [!info]- Why `!used[i − 1]`, and why `used[i − 1]` also works
> If `a[i − 1]` is equal and **not** in the path, then placing `a[i]` here would be the same as placing `a[i − 1]` here, which the loop already tried (or will skip for the same reason). So the rule forces equal copies to appear in index order, and each distinct permutation is generated exactly once.
> The opposite rule, skip when `used[i − 1]` **is** true, forces equal copies to appear in **reverse** index order, which also generates each distinct permutation once. It prunes later in the tree, though (many partial paths die only when the last copies can't be placed), so `!used[i − 1]` is faster.

### 3.4 Without recursion: next permutation and the k-th permutation

**Next permutation** (the next one in lexicographic order) works with duplicates and needs no recursion: find the rightmost `i` with `a[i] < a[i + 1]`; swap `a[i]` with the rightmost element larger than it; reverse the suffix after `i`.

```java
static boolean nextPermutation(int[] a) {         // false (and a reset to ascending) if a was the last
    int i = a.length - 2;
    while (i >= 0 && a[i] >= a[i + 1]) i--;        // the suffix after i is non-increasing
    if (i >= 0) {
        int j = a.length - 1;
        while (a[j] <= a[i]) j--;                  // rightmost element larger than a[i]
        swapInts(a, i, j);
    }
    for (int l = i + 1, r = a.length - 1; l < r; l++, r--) swapInts(a, l, r);
    return i >= 0;
}
```

`[1, 2, 3]` → `[1, 3, 2]`; `[1, 1, 5]` → `[1, 5, 1]`; `[3, 2, 1]` → `[1, 2, 3]` and `false`. Calling it repeatedly from the sorted array enumerates all distinct permutations in order, `O(n)` per step.

**The k-th permutation of `1..n`** (1-based `k`) needs no enumeration at all: there are `(n − 1)!` permutations starting with each first digit, so the first digit is the `⌊(k − 1) / (n − 1)!⌋`-th remaining digit, and so on.

```java
static String getPermutation(int n, int k) {
    List<Integer> digits = new ArrayList<>();
    int[] fact = new int[n + 1];
    fact[0] = 1;
    for (int i = 1; i <= n; i++) { fact[i] = fact[i - 1] * i; digits.add(i); }
    k--;                                           // to 0-based
    StringBuilder sb = new StringBuilder();
    for (int i = n; i >= 1; i--) {
        int idx = k / fact[i - 1];
        sb.append(digits.remove(idx));             // remove(int index), not remove(Object)
        k %= fact[i - 1];
    }
    return sb.toString();
}
```

`(3, 3)` → `"213"`; `(4, 9)` → `"2314"`. `idx` is an `int`, so `digits.remove(idx)` removes by **index**; with an `Integer` it would remove the first element **equal** to it, a different and wrong operation.

---

## 4. Combinations

### 4.1 Choose `k` of `1..n`

```java
static List<List<Integer>> combine(int n, int k) {
    List<List<Integer>> res = new ArrayList<>();
    combineRec(n, k, 1, new ArrayList<>(), res);
    return res;
}

static void combineRec(int n, int k, int start, List<Integer> path, List<List<Integer>> res) {
    if (path.size() == k) { res.add(new ArrayList<>(path)); return; }
    for (int i = start; i <= n - (k - path.size()) + 1; i++) {   // leave enough numbers for the rest
        path.add(i);
        combineRec(n, k, i + 1, path, res);
        path.remove(path.size() - 1);
    }
}
```

`combine(4, 2)` → `[1,2], [1,3], [1,4], [2,3], [2,4], [3,4]`. The loop bound is a pruning rule: if `k − |path|` more numbers are needed, starting later than `n − (k − |path|) + 1` can't succeed. Without it the output is the same but the tree is much larger when `k` is close to `n`.

### 4.2 The combination-sum family

| Problem | Reuse an element? | Duplicates in input? | Recurse with | Skip rule |
|---|---|---|---|---|
| Combination sum | yes | no | `i` | none |
| Combination sum II | no | yes | `i + 1` | `i > start && a[i] == a[i−1]` |
| Combination sum III (`k` numbers from 1–9) | no | no | `i + 1` | none; also stop at size `k` |
| Subsets / subsets II | no | no / yes | `i + 1` | none / as above |

```java
static List<List<Integer>> combinationSum(int[] candidates, int target) {   // reuse allowed
    int[] a = candidates.clone();
    Arrays.sort(a);
    List<List<Integer>> res = new ArrayList<>();
    combSum(a, 0, target, new ArrayList<>(), res);
    return res;
}

static void combSum(int[] a, int start, int remain, List<Integer> path, List<List<Integer>> res) {
    if (remain == 0) { res.add(new ArrayList<>(path)); return; }
    for (int i = start; i < a.length; i++) {
        if (a[i] > remain) break;                  // sorted: every later candidate is too big too
        path.add(a[i]);
        combSum(a, i, remain - a[i], path, res);   // i, not i + 1: a[i] may be used again
        path.remove(path.size() - 1);
    }
}

static List<List<Integer>> combinationSum2(int[] candidates, int target) {  // each used once, input has duplicates
    int[] a = candidates.clone();
    Arrays.sort(a);
    List<List<Integer>> res = new ArrayList<>();
    combSum2(a, 0, target, new ArrayList<>(), res);
    return res;
}

static void combSum2(int[] a, int start, int remain, List<Integer> path, List<List<Integer>> res) {
    if (remain == 0) { res.add(new ArrayList<>(path)); return; }
    for (int i = start; i < a.length; i++) {
        if (a[i] > remain) break;
        if (i > start && a[i] == a[i - 1]) continue;
        path.add(a[i]);
        combSum2(a, i + 1, remain - a[i], path, res);
        path.remove(path.size() - 1);
    }
}

static List<List<Integer>> combinationSum3(int k, int n) {   // k distinct numbers from 1..9 summing to n
    List<List<Integer>> res = new ArrayList<>();
    combSum3(k, 1, n, new ArrayList<>(), res);
    return res;
}

static void combSum3(int k, int start, int remain, List<Integer> path, List<List<Integer>> res) {
    if (path.size() == k) { if (remain == 0) res.add(new ArrayList<>(path)); return; }
    for (int i = start; i <= 9 && i <= remain; i++) {
        path.add(i);
        combSum3(k, i + 1, remain - i, path, res);
        path.remove(path.size() - 1);
    }
}
```

`combinationSum([2, 3, 6, 7], 7)` → `[[2,2,3], [7]]`; `([2, 3, 5], 8)` → `[[2,2,2,2], [2,3,3], [3,5]]`; `([2], 1)` → `[]`. `combinationSum2([10, 1, 2, 7, 6, 1, 5], 8)` → `[[1,1,6], [1,2,5], [1,7], [2,6]]`. `combinationSum3(3, 9)` → `[[1,2,6], [1,3,5], [2,3,4]]`; `(4, 1)` → `[]`.

> [!tip] Counting instead of listing
> If the question asks **how many** combinations sum to the target, don't backtrack: the count can be astronomically large while the DP is `O(n · target)` (coin change II, [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]]). Backtracking is for when every solution must be **output**.

---

## 5. Building Strings

Strings are built in a `StringBuilder` and undone with `setLength(length − 1)`. Building with `s + c` and passing the new string down also works (no undo needed, each call has its own string) but allocates a string per node.

### 5.1 Generate parentheses

All balanced strings of `n` pairs. Add `(` while fewer than `n` are open; add `)` only while it closes something. Every leaf is then valid, so no final check is needed.

```java
static List<String> generateParenthesis(int n) {
    List<String> res = new ArrayList<>();
    genPar(n, 0, 0, new StringBuilder(), res);
    return res;
}

static void genPar(int n, int open, int close, StringBuilder sb, List<String> res) {
    if (sb.length() == 2 * n) { res.add(sb.toString()); return; }
    if (open < n) {
        sb.append('(');
        genPar(n, open + 1, close, sb, res);
        sb.setLength(sb.length() - 1);
    }
    if (close < open) {
        sb.append(')');
        genPar(n, open, close + 1, sb, res);
        sb.setLength(sb.length() - 1);
    }
}
```

`n = 3` → `((())), (()()), (())(), ()(()), ()()()`: the Catalan number `C₃ = 5`. Generating all `2²ⁿ` strings and filtering valid ones is the brute force this replaces.

### 5.2 Letter combinations of a phone number

```java
static final String[] KEYS = {"", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"};

static List<String> letterCombinations(String digits) {
    List<String> res = new ArrayList<>();
    if (digits.isEmpty()) return res;              // [] by definition, not [""]
    letters(digits, 0, new StringBuilder(), res);
    return res;
}

static void letters(String d, int i, StringBuilder sb, List<String> res) {
    if (i == d.length()) { res.add(sb.toString()); return; }
    for (char c : KEYS[d.charAt(i) - '0'].toCharArray()) {
        sb.append(c);
        letters(d, i + 1, sb, res);
        sb.setLength(sb.length() - 1);
    }
}
```

`"23"` → `ad, ae, af, bd, be, bf, cd, ce, cf`; `""` → `[]`. The recursion would naturally return `[""]` for an empty input (one empty combination), which is why the empty case is special-cased.

### 5.3 Palindrome partitioning

Split a string into pieces that are all palindromes; list every way. Choose the end of the first piece, check it's a palindrome, recurse on the rest. Precomputing `pal[i][j]` makes each check `O(1)`.

```java
static List<List<String>> partition(String s) {
    int n = s.length();
    boolean[][] pal = new boolean[n][n];           // pal[i][j]: s[i..j] is a palindrome
    for (int i = n - 1; i >= 0; i--)
        for (int j = i; j < n; j++)
            pal[i][j] = s.charAt(i) == s.charAt(j) && (j - i < 2 || pal[i + 1][j - 1]);
    List<List<String>> res = new ArrayList<>();
    partitionRec(s, 0, pal, new ArrayList<>(), res);
    return res;
}

static void partitionRec(String s, int start, boolean[][] pal, List<String> path, List<List<String>> res) {
    if (start == s.length()) { res.add(new ArrayList<>(path)); return; }
    for (int end = start; end < s.length(); end++) {
        if (!pal[start][end]) continue;            // prune: the first piece must be a palindrome
        path.add(s.substring(start, end + 1));
        partitionRec(s, end + 1, pal, path, res);
        path.remove(path.size() - 1);
    }
}
```

`"aab"` → `[[a, a, b], [aa, b]]`; `"aaa"` → 4 partitions (every one of the `2ⁿ⁻¹` cut sets works). The **minimum** number of cuts is a DP problem, not a backtracking one ([[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]]).

### 5.4 Restore IP addresses

Split a digit string into four parts, each `0–255` without leading zeros.

```java
static List<String> restoreIpAddresses(String s) {
    List<String> res = new ArrayList<>();
    ipRec(s, 0, new ArrayList<>(), res);
    return res;
}

static void ipRec(String s, int pos, List<String> parts, List<String> res) {
    int left = 4 - parts.size();                   // parts still to place
    if (left == 0) {
        if (pos == s.length()) res.add(String.join(".", parts));
        return;
    }
    int rem = s.length() - pos;
    if (rem < left || rem > 3 * left) return;      // too few or too many digits remain
    for (int len = 1; len <= 3 && pos + len <= s.length(); len++) {
        String part = s.substring(pos, pos + len);
        if (len > 1 && part.charAt(0) == '0') break;   // "0" is fine, "01" isn't
        if (Integer.parseInt(part) > 255) break;
        parts.add(part);
        ipRec(s, pos + len, parts, res);
        parts.remove(parts.size() - 1);
    }
}
```

`"25525511135"` → `["255.255.11.135", "255.255.111.35"]`; `"0000"` → `["0.0.0.0"]`; `"101023"` → 5 addresses; `"010010"` → `["0.10.0.10", "0.100.1.0"]`. The length check prunes almost every branch: a string of 13+ digits returns immediately.

---

## 6. Grid Search

### 6.1 Word search

Does a word appear in a grid as a path of adjacent cells, each used at most once? DFS from every cell; mark the current path's cells so it can't loop back onto itself, and **unmark** on the way out so other paths may use them.

```java
static boolean exist(char[][] board, String word) {
    for (int r = 0; r < board.length; r++)
        for (int c = 0; c < board[0].length; c++)
            if (wsDfs(board, word, 0, r, c)) return true;
    return false;
}

static boolean wsDfs(char[][] b, String w, int k, int r, int c) {
    if (k == w.length()) return true;
    if (r < 0 || c < 0 || r >= b.length || c >= b[0].length || b[r][c] != w.charAt(k)) return false;
    char saved = b[r][c];
    b[r][c] = '#';                                 // on the current path: can't be reused
    boolean found = wsDfs(b, w, k + 1, r + 1, c) || wsDfs(b, w, k + 1, r - 1, c)
                 || wsDfs(b, w, k + 1, r, c + 1) || wsDfs(b, w, k + 1, r, c - 1);
    b[r][c] = saved;                               // restore, even when found
    return found;
}
```

Board `ABCE / SFCS / ADEE`: `"ABCCED"` → `true`, `"SEE"` → `true`, `"ABCB"` → `false` (it would need the `B` twice). Worst case `O(R·C·3ᴸ)` for a word of length `L` (after the first step, at most 3 directions are new). Two cheap prunings help a lot: return `false` if the board doesn't contain enough of some letter, and search for the reversed word if its first letter is more common in the board than its last.

> [!warning] A global `visited` set that's never cleared
> Marking cells visited "for the whole search" (as in a flood fill) is wrong here: a cell that was a dead end on one path can be exactly what another path needs. Path-based marking with restore is what makes this backtracking rather than plain DFS.

**Many words at once** (word search II): searching each word separately repeats work; walk the grid once while descending a trie of all the words ([[DSA/04 - Trees and Hierarchical Structures/05 - Tries#4.5 Word search II: many words in a grid|Tries § 4.5]]).

### 6.2 Paths that visit every cell exactly once

**Unique paths III**: count the walks from the start (`1`) to the end (`2`) that pass over every empty cell (`0`) exactly once, avoiding obstacles (`-1`).

```java
static int uniquePathsIII(int[][] grid) {
    int[][] g = new int[grid.length][];
    for (int i = 0; i < grid.length; i++) g[i] = grid[i].clone();
    int toVisit = 0, sr = 0, sc = 0;
    for (int r = 0; r < g.length; r++)
        for (int c = 0; c < g[0].length; c++) {
            if (g[r][c] != -1) toVisit++;          // start, end and every empty cell
            if (g[r][c] == 1) { sr = r; sc = c; }
        }
    return pathsFrom(g, sr, sc, toVisit);
}

static int pathsFrom(int[][] g, int r, int c, int left) {   // left: cells still to visit, including (r, c)
    if (r < 0 || c < 0 || r >= g.length || c >= g[0].length || g[r][c] == -1) return 0;
    if (g[r][c] == 2) return left == 1 ? 1 : 0;    // at the end: was everything else covered?
    int saved = g[r][c];
    g[r][c] = -1;                                  // treat the path as an obstacle
    int total = pathsFrom(g, r + 1, c, left - 1) + pathsFrom(g, r - 1, c, left - 1)
              + pathsFrom(g, r, c + 1, left - 1) + pathsFrom(g, r, c - 1, left - 1);
    g[r][c] = saved;
    return total;
}
```

`[[1,0,0,0],[0,0,0,0],[0,0,2,-1]]` → `2`; `[[1,0,0,0],[0,0,0,0],[0,0,0,2]]` → `4`; `[[0,1],[2,0]]` → `0`. Grids are limited to about 20 cells: the count of Hamiltonian paths explodes, and for larger inputs the problem is solved with a bitmask DP over visited cells ([[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]]).

---

## 7. N-Queens

Place `n` queens on an `n × n` board so that no two attack each other. One queen per row, so the choice at row `r` is the column. A cell `(r, c)` is attacked if its column is taken, or its **diagonal** (`r − c` constant) or **anti-diagonal** (`r + c` constant) is.

![[Backtracking - N-Queens Diagonals.excalidraw|800]]

```
place(r):
    if r = n: record the board; return
    for c = 0 .. n−1:
        if col[c] or diag[r − c] or anti[r + c]: continue
        mark col[c], diag[r − c], anti[r + c]; queen[r] = c
        place(r + 1)
        unmark them
```

```java
static List<List<String>> solveNQueens(int n) {
    List<List<String>> res = new ArrayList<>();
    placeQueens(0, n, new int[n], new boolean[n], new boolean[2 * n - 1], new boolean[2 * n - 1], res);
    return res;
}

static void placeQueens(int r, int n, int[] queenCol, boolean[] col, boolean[] diag, boolean[] anti,
                        List<List<String>> res) {
    if (r == n) { res.add(renderBoard(queenCol)); return; }
    for (int c = 0; c < n; c++) {
        int d = r - c + n - 1, a = r + c;          // r − c ranges over −(n−1)..n−1: shift to 0..2n−2
        if (col[c] || diag[d] || anti[a]) continue;
        queenCol[r] = c;
        col[c] = diag[d] = anti[a] = true;
        placeQueens(r + 1, n, queenCol, col, diag, anti, res);
        col[c] = diag[d] = anti[a] = false;
    }
}

static List<String> renderBoard(int[] queenCol) {
    List<String> rows = new ArrayList<>();
    for (int c : queenCol) {
        char[] row = new char[queenCol.length];
        Arrays.fill(row, '.');
        row[c] = 'Q';
        rows.add(new String(row));
    }
    return rows;
}
```

`n = 4` → `[".Q..", "...Q", "Q...", "..Q."]` and `["..Q.", "Q...", "...Q", ".Q.."]`.

**Counting only**, the three flag arrays become three bitmasks. Shifting the diagonal masks by one bit per row moves each attack to the column it hits in the next row.

```java
static int totalNQueens(int n) {                  // n ≤ 15 or so (masks stay inside an int)
    return countQueens(n, 0, 0, 0, 0);
}

static int countQueens(int n, int row, int cols, int diag, int anti) {
    if (row == n) return 1;
    int count = 0;
    int free = ~(cols | diag | anti) & ((1 << n) - 1);   // columns not attacked in this row
    while (free != 0) {
        int bit = free & -free;                    // lowest free column
        free -= bit;
        count += countQueens(n, row + 1, cols | bit, (diag | bit) << 1, (anti | bit) >>> 1);
    }
    return count;
}
```

| `n` | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Solutions | 1 | 0 | 0 | 2 | 10 | 4 | 40 | 92 | 352 | 724 |

---

## 8. Sudoku Solver

Fill a 9×9 grid so that every row, column and 3×3 box contains `1–9` once. Keep, for each row, column and box, a 9-bit mask of the digits already used; the candidates for a cell are the bits in none of its three masks. Two refinements make the search fast:

- **Most constrained cell first** (<span class="hl-blue">MRV</span>, minimum remaining values): fill the empty cell with the fewest candidates. A cell with one candidate is forced; a cell with zero proves the branch is dead **before** going deeper.
- Bit operations for the candidate sets: `Integer.bitCount` counts them, `x & -x` picks one.

```java
static boolean solveSudoku(char[][] b) {
    int[] row = new int[9], col = new int[9], box = new int[9];
    List<int[]> empty = new ArrayList<>();
    for (int r = 0; r < 9; r++)
        for (int c = 0; c < 9; c++) {
            if (b[r][c] == '.') { empty.add(new int[]{r, c}); continue; }
            int bit = 1 << (b[r][c] - '1');
            row[r] |= bit; col[c] |= bit; box[r / 3 * 3 + c / 3] |= bit;
        }
    return sudokuRec(b, empty, row, col, box);
}

static boolean sudokuRec(char[][] b, List<int[]> empty, int[] row, int[] col, int[] box) {
    int best = -1, bestCount = 10;
    for (int i = 0; i < empty.size(); i++) {       // MRV: the empty cell with the fewest candidates
        int r = empty.get(i)[0], c = empty.get(i)[1];
        if (b[r][c] != '.') continue;
        int cnt = Integer.bitCount(~(row[r] | col[c] | box[r / 3 * 3 + c / 3]) & 0x1FF);
        if (cnt == 0) return false;                // some cell has no digit left: dead branch
        if (cnt < bestCount) { bestCount = cnt; best = i; }
    }
    if (best == -1) return true;                   // no empty cells: solved
    int r = empty.get(best)[0], c = empty.get(best)[1], bx = r / 3 * 3 + c / 3;
    int cand = ~(row[r] | col[c] | box[bx]) & 0x1FF;
    while (cand != 0) {
        int bit = cand & -cand;
        cand -= bit;
        b[r][c] = (char) ('1' + Integer.numberOfTrailingZeros(bit));
        row[r] |= bit; col[c] |= bit; box[bx] |= bit;
        if (sudokuRec(b, empty, row, col, box)) return true;   // keep the filled board
        row[r] ^= bit; col[c] ^= bit; box[bx] ^= bit;
        b[r][c] = '.';
    }
    return false;
}
```

On a solved board the function returns `true` **without** undoing, which is how the solution is left in `b`. Filling cells in plain row-major order also works for ordinary puzzles, but on hard ones MRV cuts the search by orders of magnitude, because forced cells are filled first and contradictions surface immediately. That's <span class="hl-blue">constraint propagation</span> in its simplest form; full solvers also propagate "this digit has only one possible place in this row".

---

## 9. Pruning Strategies

| Strategy | Idea | Example |
|---|---|---|
| **Feasibility** | stop when the partial state already breaks a constraint | queen attacked, part > 255, `remain < 0` |
| **Bounds** | stop when even the best completion can't succeed or beat the best found (<span class="hl-blue">branch and bound</span>) | not enough numbers left (`combine`), not enough digits left (IP) |
| **Sorted input + `break`** | once a candidate is too big, every later one is too | combination sum |
| **Duplicate skipping** | equal choices at the same level give equal subtrees | subsets II, permutations II |
| **Symmetry breaking** | interchangeable choices are tried once | identical buckets, mirror boards |
| **Ordering** | try the most constrained or most likely choice first | MRV in sudoku, largest items first |
| **Precomputation** | make each check `O(1)` | palindrome table, bitmask candidates |
| **Memoizing failures** | a state that failed once fails again | word break, partition with a bitmask state |

**Example combining several**: can the array be split into `k` subsets with equal sums (matchsticks to square is `k = 4`)?

```java
static boolean canPartitionKSubsets(int[] nums, int k) {
    int sum = 0;
    for (int x : nums) sum += x;
    if (sum % k != 0) return false;                // feasibility before any search
    int target = sum / k;
    Integer[] a = new Integer[nums.length];
    for (int i = 0; i < nums.length; i++) a[i] = nums[i];
    Arrays.sort(a, Collections.reverseOrder());    // big items first: failures surface early
    if (a[0] > target) return false;
    return fillBuckets(a, 0, new int[k], target);
}

static boolean fillBuckets(Integer[] a, int i, int[] bucket, int target) {
    if (i == a.length) return true;                // nothing exceeded target, total = k·target: all equal
    for (int b = 0; b < bucket.length; b++) {
        if (bucket[b] + a[i] > target) continue;
        if (b > 0 && bucket[b] == bucket[b - 1]) continue;   // same sum as the previous bucket: same subtree
        bucket[b] += a[i];
        if (fillBuckets(a, i + 1, bucket, target)) return true;
        bucket[b] -= a[i];
    }
    return false;
}
```

`([4, 3, 2, 3, 5, 2, 1], 4)` → `true` (`5`, `1+4`, `2+3`, `2+3`); `([1, 2, 3, 4], 3)` → `false` (sum 10 isn't divisible by 3). The bucket-symmetry rule covers the important special case: all empty buckets are interchangeable, so the first item is only ever tried in bucket 0. Without it, the same assignment is explored `k!` times.

---

## 10. How Big Is the Search?

The size of the output bounds the work from below, so knowing these numbers tells you whether backtracking can work at all.

| Search | Number of leaves / results | Practical limit |
|---|---|---|
| Subsets | `2ⁿ` | `n ≤ 20` |
| Permutations | `n!` (`10! = 3,628,800`) | `n ≤ 10` (`11! ≈ 4·10⁷`) |
| Combinations | `C(n, k)` (max at `k = n/2`: `C(20, 10) = 184,756`) | |
| Balanced parentheses | Catalan `Cₙ ≈ 4ⁿ / (n^1.5 √π)` (`C₁₀ = 16,796`) | `n ≤ 12` or so |
| Phone letters | up to `4ⁿ` | short inputs |
| Palindrome partitions | up to `2ⁿ⁻¹` | `n ≤ 16` |
| N-queens | 92 for `n = 8`, 14,200 for `n = 12` | `n ≤ 12`–`15` with bitmasks |

Each recorded result also costs its own length to copy, so "all subsets" is `Θ(n·2ⁿ)` and "all permutations" is `Θ(n·n!)`. The recursion depth is only the length of one candidate, so stack overflow is rarely the problem here; running time is.

> [!tip] Backtracking or DP?
> If the problem asks for **all** solutions, backtracking (the output is the bottleneck anyway). If it asks for **the number** of solutions, **the best** one, or **whether one exists**, look for overlapping states first: identical "remaining problem" states reached by different paths mean DP or memoized search ([[DSA/06 - Algorithm Design Paradigms/04 - Dynamic Programming Fundamentals|Dynamic Programming — Fundamentals]]). If the inputs are tiny (`n ≤ 20`) and the state is a set, a bitmask DP is often both simpler and faster ([[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]]).

---

## 11. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| `res.add(path)` | every result is the same (usually empty) list | `res.add(new ArrayList<>(path))` |
| Missing undo on one branch | later results contain stale elements | every apply has an undo; restore before returning |
| Returning early before restoring the board | grid permanently marked | assign the result, restore, then return |
| `path.remove(x)` with an `Integer` value on a `List<Integer>` | removes the first element **equal** to `x` | `path.remove(path.size() - 1)` |
| Skip rule `i > 0` instead of `i > start` | `[2, 2]` missing from subsets II | `i > start` |
| Skip rule on unsorted input | duplicates remain | sort first |
| Combination sum recursing with `i + 1` | reuse not allowed: answers missing | `i` when reuse is allowed |
| Permutations with a start index | only combinations produced | loop from 0 with `used[]` |
| `break` instead of `continue` on unsorted candidates | answers missing | sort first, or `continue` |
| Diagonal index `r − c` used directly | `ArrayIndexOutOfBoundsException` | `r − c + n − 1` |
| Global `visited` in word search | false negatives | mark on the path, unmark on return |
| `letterCombinations("")` returning `[""]` | wrong expected output | special-case empty input |
| IP parts like `"01"` or `"256"` | invalid addresses | leading-zero and range checks |
| Static result lists not reset between calls | answers from earlier inputs leak | create the list inside the public method |

---

## 12. Trick Questions and Special Cases

> [!question]- How many subsets does `[]` have? How many permutations?
> One of each: the empty subset and the empty permutation. `subsetsByStart([])` returns `[[]]`. (`letterCombinations("")` is the odd one out: the problem defines it as `[]`.)

> [!question]- Subsets II on `[2, 1, 2]` without sorting first?
> Duplicates. The two 2s aren't adjacent, so `a[i] == a[i − 1]` never fires, and the output is `[], [2], [2,1], [2,1,2], [2,2], [1], [1,2], [2]`: the subset `{2}` appears twice, and so does `{1, 2}` (as `[2, 1]` and `[1, 2]`). Sorting is part of the algorithm.

> [!question]- In permutations II, both `!used[i − 1]` and `used[i − 1]` give the right answer. Which is faster?
> `!used[i − 1]`. It forces equal copies to be placed in index order and cuts duplicate branches near the root; the other version cuts them deep in the tree. Same output, many more nodes visited.

> [!question]- Why is the swap-based permutation order not lexicographic, even on sorted input?
> Swapping `a[k]` with a later `a[i]` moves the old `a[k]` to position `i`, disturbing the sorted order of the suffix. For `[1, 2, 3]`, the branch that puts `3` first leaves `[3, 2, 1]`, so `[3, 2, 1]` is generated before `[3, 1, 2]`.

> [!question]- `combinationSum([2, 3, 6, 7], 7)`: why isn't `[3, 2, 2]` in the output alongside `[2, 2, 3]`?
> The `start` index makes each combination appear in non-decreasing order only. Counting **ordered** sequences (`[2, 2, 3]`, `[2, 3, 2]`, `[3, 2, 2]` all different) is a different problem (combination sum IV), solved by DP.

> [!question]- What happens if the candidates in combination sum include 0?
> Infinite recursion: choosing 0 doesn't reduce `remain`, and reuse is allowed. The problem guarantees positive candidates; with zeros the number of combinations is infinite anyway.

> [!question]- `totalNQueens(6)` is smaller than `totalNQueens(5)`. Is that a bug?
> No: 10 for `n = 5`, 4 for `n = 6`. The sequence isn't monotonic at small `n`. `n = 2` and `n = 3` have no solutions at all.

> [!question]- Word search `"ABA"` on the board `[["A", "B"]]`?
> `false`. The path `A → B → A` would reuse the first cell; there's only one `A`. The `'#'` marker is what prevents it.

> [!question]- `restoreIpAddresses("010010")`?
> `["0.10.0.10", "0.100.1.0"]`. Every `0` that starts a part must be the whole part, which rules out `"01.0.0.10"`-style splits.

> [!question]- `getPermutation(4, 9)`?
> `"2314"`. With `k − 1 = 8`: `8 / 3! = 1` → second digit of `[1,2,3,4]` = `2`; `8 % 6 = 2`, `2 / 2! = 1` → second of `[1,3,4]` = `3`; `2 % 2 = 0` → first of `[1,4]` = `1`; then `4`.

> [!question]- `nextPermutation([1, 3, 2])` and `nextPermutation([2, 2, 1])`?
> `[2, 1, 3]` (the pivot is `1` at index 0, swapped with `2`, then the suffix `[3, 1]` reversed to `[1, 3]`); and `[1, 2, 2]` with `false`, because `[2, 2, 1]` is the last permutation of those values.

> [!question]- Does generate-parentheses need to check validity at the leaves?
> No. The two rules (`open < n` to add `(`, `close < open` to add `)`) keep every prefix valid, so every complete string is balanced. That's pruning so strong that no dead branch is ever entered.

> [!question]- `canPartitionKSubsets([2, 2, 2, 2, 3, 4, 5], 4)`?
> `false`. The sum is 20 (divisible by 4, target 5) and no number exceeds 5, so both quick checks pass. But the bucket holding the `4` needs exactly a `1` more, and there is no `1`. Divisibility and "largest ≤ target" are necessary, not sufficient; the search is what decides.

---

## 13. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `subsetsByStart([1,2,3])` order | `[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]` | every node recorded |
| `subsetsWithDup([1,2,2])` | 6 subsets | skip `i > start` duplicates |
| `permuteUnique([1,1,2])` | 3 | `3! / 2!` |
| Swap permutations of `[1,2,3]` | ends `[3,2,1], [3,1,2]` | not lexicographic |
| `nextPermutation([3,2,1])` | `[1,2,3]`, `false` | wraps around |
| `getPermutation(3, 3)` | `"213"` | factorial number system |
| `combine(4, 2)` | 6 | `C(4, 2)` |
| `combinationSum([2,3,5], 8)` | `[[2,2,2,2],[2,3,3],[3,5]]` | recurse with `i` |
| `combinationSum2([10,1,2,7,6,1,5], 8)` | `[[1,1,6],[1,2,5],[1,7],[2,6]]` | |
| `generateParenthesis(3)` | 5 strings | Catalan |
| `letterCombinations("")` | `[]` | by definition |
| `partition("aaa")` | 4 | `2ⁿ⁻¹` |
| `restoreIpAddresses("0000")` | `["0.0.0.0"]` | |
| `exist(ABCE/SFCS/ADEE, "ABCB")` | `false` | no cell reuse |
| `uniquePathsIII([[0,1],[2,0]])` | `0` | can't cover all cells |
| N-queens `n = 4, 6, 8` | `2, 4, 92` | not monotonic |
| `canPartitionKSubsets([4,3,2,3,5,2,1], 4)` | `true` | |

---

## 14. Summary

- Backtracking is DFS over a tree of partial solutions: **choose, explore, unchoose**, with one shared mutable state that must be restored exactly.
- **Subsets**: loop from `start`, record every node. **Combinations**: the same with a size or sum condition. **Permutations**: loop from 0 with `used[]`, or swap in place.
- **Duplicates**: sort, then skip `a[i] == a[i − 1]` at the same level (`i > start`), or for permutations when `a[i − 1]` isn't in use.
- Reuse allowed → recurse with `i`; not allowed → `i + 1`. Sorted candidates allow `break`.
- Strings: `StringBuilder` with `setLength` undo; constraints in the choice rules (parentheses, IP parts, palindromes) keep the tree small.
- Grids: mark the path, unmark on return. N-queens: column and diagonal flags (`r − c`, `r + c`), or bitmasks. Sudoku: bitmask candidates and most-constrained-cell-first.
- Prune by feasibility, bounds, ordering, symmetry and duplicate skipping; the output size (`2ⁿ`, `n!`, Catalan) sets the limit on `n`.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/06 - Algorithm Design Paradigms/02 - Divide and Conquer|Divide and Conquer]] · Next: [[DSA/06 - Algorithm Design Paradigms/04 - Dynamic Programming Fundamentals|Dynamic Programming — Fundamentals]]
- [[DSA/01 - Foundations/02 - Recursion|Recursion]]: include/exclude subsets, the call stack
- [[DSA/01 - Foundations/03 - Bit Manipulation|Bit Manipulation]]: subsets as bitmasks, `x & -x`
- [[DSA/04 - Trees and Hierarchical Structures/05 - Tries|Tries]]: word search II
- [[DSA/05 - Graphs/01 - Graph Representations and Traversals|Graph Representations and Traversals]]: DFS on explicit graphs
- [[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]]: bitmask DP when backtracking is too slow
- [[DSA/06 - Algorithm Design Paradigms/07 - Meet in the Middle|Meet in the Middle]]: halving an exponential search
- [[DSA/08 - Specialized Topics/03 - Game Theory|Game Theory]]: minimax search with alpha-beta pruning
