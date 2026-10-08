# Tries

A <span class="hl-blue">trie</span> (prefix tree, pronounced "try") stores a set of strings as a tree whose edges are labelled with characters. The path from the root to a node spells a **prefix**, and every string with that prefix lives in the node's subtree. Looking up a word of length `L` takes `O(L)` steps, regardless of how many words are stored, and prefix questions ("is there any word starting with `pre`?", "how many?", "list them in order") cost the same.

That makes tries the structure for autocomplete, dictionaries with prefix queries, searching many words at once in a grid, and, with bits instead of letters, maximum-XOR problems. This note covers the structure and its three basic operations, counting and deletion, the classic applications (longest common prefix, replace words, wildcard search, search suggestions, word search II), bitwise tries for XOR queries, the array-based implementation used in contests, and the memory cost that's the trie's main weakness.

## Contents

- [[#1. Structure|1. Structure]]
- [[#2. Insert, Search, StartsWith|2. Insert, Search, StartsWith]]
- [[#3. Counting and Deletion|3. Counting and Deletion]]
- [[#4. Applications|4. Applications]]
- [[#5. Bitwise Tries for XOR|5. Bitwise Tries for XOR]]
- [[#6. Implementation Choices and Memory|6. Implementation Choices and Memory]]
- [[#7. Common Mistakes|7. Common Mistakes]]
- [[#8. Trick Questions and Special Cases|8. Trick Questions and Special Cases]]
- [[#9. Quick Reference — Non-Obvious Outcomes|9. Quick Reference — Non-Obvious Outcomes]]
- [[#10. Summary|10. Summary]]

---

## 1. Structure

> [!note] Definition
> A trie over an alphabet `Σ` is a rooted tree where:
> - each edge is labelled with one character, and the edges leaving a node have **distinct** labels;
> - the root represents the empty string, and each node represents the string spelled by the path to it;
> - each node has an **end-of-word** flag, set if that string was inserted.

![[Tries - Prefix Tree.excalidraw|800]]

The flag is essential, because the set of nodes alone doesn't say which prefixes are words: after inserting only `"tea"`, the nodes for `"t"` and `"te"` exist but aren't words. A word can end at an internal node (`"in"` when `"inn"` is also stored), so "is a leaf" and "is a word" are different things.

| Property | Value |
|---|---|
| Nodes | at most `1 + total length of all words`; fewer when words share prefixes |
| Depth | length of the longest word |
| Children per node | at most `|Σ|` (26 for lowercase letters, 2 for bits) |
| Preorder traversal (children in alphabet order) | the words in **lexicographic** order |

---

## 2. Insert, Search, StartsWith

```
insert(word):
    cur = root
    for c in word:
        if cur has no child c: create it
        cur = cur.child[c]
    cur.end = true

walk(s):                                -- the node for s, or null
    cur = root
    for c in s:
        if cur has no child c: return null
        cur = cur.child[c]
    return cur

search(word)     = walk(word) ≠ null and walk(word).end
startsWith(pre)  = walk(pre) ≠ null
```

```java
class TrieNode {
    TrieNode[] next = new TrieNode[26];            // next[c − 'a'], null if absent
    boolean end;                                   // a word ends here
}

static void insertInto(TrieNode root, String w) {
    TrieNode cur = root;
    for (int k = 0; k < w.length(); k++) {
        int i = w.charAt(k) - 'a';
        if (cur.next[i] == null) cur.next[i] = new TrieNode();
        cur = cur.next[i];
    }
    cur.end = true;
}

static TrieNode walk(TrieNode root, String s) {
    TrieNode cur = root;
    for (int k = 0; k < s.length() && cur != null; k++) cur = cur.next[s.charAt(k) - 'a'];
    return cur;
}

static TrieNode build(String[] words) {
    TrieNode root = new TrieNode();
    for (String w : words) insertInto(root, w);
    return root;
}

static class Trie {
    private final TrieNode root = new TrieNode();

    void insert(String w) { insertInto(root, w); }

    boolean search(String w) {
        TrieNode n = walk(root, w);
        return n != null && n.end;                 // the path exists AND a word ends there
    }

    boolean startsWith(String p) { return walk(root, p) != null; }
}
```

All three are `O(L)` for a string of length `L`. Inserting `"apple"` then asking `search("app")` gives `false` and `startsWith("app")` gives `true`. Inserting `"app"` afterwards creates **no** nodes; it only sets a flag.

![[Tries - End Flag vs Prefix.excalidraw|800]]

> [!warning] The alphabet is part of the contract
> `next[c − 'a']` works only for lowercase `a`–`z`. An uppercase letter gives a negative index (`'A' − 'a' = −32`), a digit or space gives a negative one too, and `'{'` gives 26: all throw `ArrayIndexOutOfBoundsException`. For mixed input, size the array for the real alphabet (128 for ASCII), map characters explicitly, or use a `HashMap<Character, TrieNode>` per node ([[#6. Implementation Choices and Memory|§6]]).

---

## 3. Counting and Deletion

A boolean flag can't count duplicates, and deletion needs to know whether a node is still used by another word. Two counters per node answer both:

- `pass`: how many inserted words go **through** this node (have this prefix);
- `end`: how many inserted words **end** here.

```java
static class CountingTrie {
    private static class Node {
        Node[] next = new Node[26];
        int pass, end;
    }

    private final Node root = new Node();

    void insert(String w) {
        Node cur = root;
        cur.pass++;                                // root.pass = total number of words
        for (int k = 0; k < w.length(); k++) {
            int i = w.charAt(k) - 'a';
            if (cur.next[i] == null) cur.next[i] = new Node();
            cur = cur.next[i];
            cur.pass++;
        }
        cur.end++;
    }

    int countWordsEqualTo(String w) { Node n = find(w); return n == null ? 0 : n.end; }

    int countWordsStartingWith(String p) { Node n = find(p); return n == null ? 0 : n.pass; }

    void erase(String w) {                         // removes one copy, if present
        if (countWordsEqualTo(w) == 0) return;     // otherwise counts on the path go wrong
        Node cur = root;
        cur.pass--;
        for (int k = 0; k < w.length(); k++) {
            int i = w.charAt(k) - 'a';
            if (--cur.next[i].pass == 0) {         // no other word uses this branch
                cur.next[i] = null;                // prune it all at once
                return;
            }
            cur = cur.next[i];
        }
        cur.end--;
    }

    private Node find(String s) {
        Node cur = root;
        for (int k = 0; k < s.length() && cur != null; k++) cur = cur.next[s.charAt(k) - 'a'];
        return cur;
    }
}
```

Insert `"apple"` twice and `"app"` once: `countWordsEqualTo("apple") = 2`, `countWordsStartingWith("app") = 3`. After `erase("apple")` once: `1` and `2`. Erasing `"apple"` once more cuts the branch below `"app"`, but the nodes `a-p-p` stay because `"app"` still passes through them.

> [!warning] Deleting a word must not delete shared prefixes or longer words
> Removing `"app"` from a trie that also holds `"apple"` must only clear the end flag: the nodes are on `"apple"`'s path. Removing `"apple"` must stop pruning at the node for `"app"` (it's a word) and at any node with another child. Without `pass` counts, the recursive version deletes a child only if it has **no children and no end flag** after the recursive call returns. And erasing a word that isn't present must change nothing, which is why the presence check comes first.

---

## 4. Applications

### 4.1 Longest common prefix

Walk down from the root while the current node has **exactly one child** and isn't the end of a word.

```java
static String longestCommonPrefix(String[] words) {
    TrieNode cur = build(words);
    StringBuilder sb = new StringBuilder();
    while (!cur.end) {                             // a word ends here: the prefix can't be longer
        int only = -1, count = 0;
        for (int i = 0; i < 26; i++) if (cur.next[i] != null) { only = i; count++; }
        if (count != 1) break;                     // the words disagree here
        sb.append((char) ('a' + only));
        cur = cur.next[only];
    }
    return sb.toString();
}
```

`["flower", "flow", "flight"]` → `"fl"`; `["ab", "a"]` → `"a"` (the end flag stops it); `["", "abc"]` → `""`. For a single query, comparing the strings directly is simpler ([[DSA/02 - Linear Data Structures/02 - Strings|Strings]]); the trie pays off when the word set changes or many queries follow.

### 4.2 Replace words with their shortest root

Given a dictionary of roots, replace each word of a sentence with the **shortest** root that's a prefix of it.

```java
static String replaceWords(List<String> roots, String sentence) {
    TrieNode trie = build(roots.toArray(new String[0]));
    StringBuilder out = new StringBuilder();
    for (String w : sentence.split(" ")) {
        if (out.length() > 0) out.append(' ');
        TrieNode cur = trie;
        int k = 0;
        while (k < w.length() && !cur.end && cur.next[w.charAt(k) - 'a'] != null) {
            cur = cur.next[w.charAt(k) - 'a'];
            k++;
        }
        out.append(cur.end ? w.substring(0, k) : w);   // stop at the FIRST end flag: shortest root
    }
    return out.toString();
}
```

Roots `["cat", "bat", "rat"]`, sentence `"the cattle was rattled by the battery"` → `"the cat was rat by the bat"`. Checking `!cur.end` **before** moving on is what makes the root the shortest: with roots `["a", "aa"]`, `"aaa"` becomes `"a"`.

### 4.3 Wildcard search

`search` with `'.'` matching any one letter: on a `'.'`, try every child.

```java
static class WordDictionary {
    private final TrieNode root = new TrieNode();

    void addWord(String w) { insertInto(root, w); }

    boolean search(String w) { return match(root, w, 0); }

    private boolean match(TrieNode n, String w, int k) {
        if (k == w.length()) return n.end;
        char c = w.charAt(k);
        if (c == '.') {
            for (TrieNode child : n.next)
                if (child != null && match(child, w, k + 1)) return true;
            return false;
        }
        TrieNode child = n.next[c - 'a'];
        return child != null && match(child, w, k + 1);
    }
}
```

After adding `"bad"`, `"dad"`, `"mad"`: `search("pad")` → `false`, `search(".ad")` → `true`, `search("b..")` → `true`, `search("..")` → `false` (no two-letter word: the end flag matters even with wildcards). Worst case `O(26^d · …)` for `d` dots, but the trie prunes every branch that no stored word follows.

### 4.4 Search suggestions (autocomplete)

After each typed character, return up to three stored words with that prefix, in lexicographic order. A DFS from the prefix's node, visiting children in alphabet order, finds them in sorted order and can stop after three.

```java
static List<List<String>> suggestedProducts(String[] products, String searchWord) {
    TrieNode root = build(products);
    List<List<String>> res = new ArrayList<>();
    TrieNode cur = root;
    StringBuilder prefix = new StringBuilder();
    for (char c : searchWord.toCharArray()) {
        prefix.append(c);
        cur = cur == null ? null : cur.next[c - 'a'];   // once off the trie, stay off
        List<String> found = new ArrayList<>();
        collect(cur, prefix, found, 3);
        res.add(found);
    }
    return res;
}

static void collect(TrieNode n, StringBuilder sb, List<String> out, int limit) {
    if (n == null || out.size() == limit) return;
    if (n.end) out.add(sb.toString());             // a word comes before its extensions
    for (int i = 0; i < 26 && out.size() < limit; i++) {
        if (n.next[i] == null) continue;
        sb.append((char) ('a' + i));
        collect(n.next[i], sb, out, limit);
        sb.deleteCharAt(sb.length() - 1);
    }
}
```

`["mobile", "mouse", "moneypot", "monitor", "mousepad"]`, typing `"mouse"`: `m` → `[mobile, moneypot, monitor]`, …, `mous` → `[mouse, mousepad]`. Recording the word **before** visiting children is what puts `"mouse"` ahead of `"mousepad"`. The `cur == null` guard matters: after a character with no match, every longer prefix also has no match, and indexing into `null` would throw.

> [!tip] Faster autocomplete
> Real autocomplete stores, at every node, the top-`k` completions (by popularity or alphabetically) computed at insertion time. A query is then `O(|prefix|)` with no DFS, at the cost of `k` extra references per node. For a static product list, sorting it and binary searching for the prefix ([[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]]) gives the same answers with no trie at all: the three suggestions are the next three strings from the lower bound, if they start with the prefix.

### 4.5 Word search II: many words in a grid

Find every dictionary word that can be traced in a letter grid through adjacent cells, each cell used at most once per word. Searching each word separately repeats work; instead, run **one** backtracking search ([[DSA/06 - Algorithm Design Paradigms/03 - Backtracking|Backtracking]]) from every cell, walking the trie alongside the path. As soon as the path spells a prefix of no word, the trie has no child, and the branch is abandoned.

```java
static class WNode {
    WNode[] next = new WNode[26];
    String word;                                   // the complete word ending here, or null
}

static List<String> findWords(char[][] board, String[] words) {
    WNode root = new WNode();
    for (String w : words) {
        WNode cur = root;
        for (char c : w.toCharArray()) {
            int i = c - 'a';
            if (cur.next[i] == null) cur.next[i] = new WNode();
            cur = cur.next[i];
        }
        cur.word = w;
    }
    List<String> res = new ArrayList<>();
    for (int r = 0; r < board.length; r++)
        for (int c = 0; c < board[0].length; c++) dfsBoard(board, r, c, root, res);
    return res;
}

static void dfsBoard(char[][] b, int r, int c, WNode parent, List<String> res) {
    if (r < 0 || c < 0 || r >= b.length || c >= b[0].length || b[r][c] == '#') return;
    WNode n = parent.next[b[r][c] - 'a'];
    if (n == null) return;                         // no word continues this way: prune
    if (n.word != null) { res.add(n.word); n.word = null; }   // report each word once
    char ch = b[r][c];
    b[r][c] = '#';                                 // mark the cell as used on this path
    dfsBoard(b, r + 1, c, n, res);
    dfsBoard(b, r - 1, c, n, res);
    dfsBoard(b, r, c + 1, n, res);
    dfsBoard(b, r, c - 1, n, res);
    b[r][c] = ch;                                  // restore it for other paths
}
```

Board `[[o,a,a,n],[e,t,a,e],[i,h,k,r],[i,f,l,v]]`, words `[oath, pea, eat, rain]` → `oath` and `eat`. Three details matter:

- Storing the **whole word** at its end node avoids rebuilding it from the path.
- Clearing `n.word` after reporting stops the same word from being found again through another path (it would otherwise appear twice in the result).
- Continuing the search below a found word is necessary: `"oath"` and `"oaths"` can both be in the dictionary.

> [!info]- Pruning exhausted branches
> Once all words below a node have been found, that whole subtree is dead weight that the DFS keeps entering. Counting the remaining words per node (or removing a leaf node from its parent after its word is reported, and repeating upward while the parent becomes an empty non-word leaf) makes later searches stop earlier. On adversarial inputs (a board of all `'a'`s with words `"aaaa…ab"`) this is the difference between passing and timing out.

### 4.6 Other problems

| Problem | Trie idea |
|---|---|
| Longest word buildable one letter at a time | DFS only through nodes whose end flag is set |
| Word break (can `s` be split into dictionary words?) | DP over positions; from each position, walk the trie to find all words starting there ([[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]]) |
| Concatenated words | the same, requiring at least two pieces |
| Palindrome pairs (advanced) | insert reversed words; match prefixes/suffixes that are palindromes |
| Map sum pairs (sum of values with a prefix) | store a running sum per node; on overwrite, add the difference |
| Stream of characters: does any word end here? | trie of **reversed** words, walked backwards over the recent characters |
| Count distinct substrings | insert every suffix into a trie and count nodes (`O(n²)`); suffix structures do it faster ([[DSA/07 - String Algorithms/04 - Suffix Structures|Suffix Structures]]) |
| Many patterns in one text | Aho–Corasick: a trie with failure links ([[DSA/07 - String Algorithms/01 - String Matching|String Matching]]) |

---

## 5. Bitwise Tries for XOR

Treat each integer as a 31-bit string (for non-negative `int`s), from the highest bit down, and insert it into a trie with two children per node. XOR rewards **differing** bits, and a higher bit outweighs all lower ones together (`2ᵇ > 2ᵇ⁻¹ + … + 1`). So to maximise `x ^ y` over stored `y`, walk down choosing the child **opposite** to `x`'s bit whenever it exists: a greedy choice that's always right, bit by bit.

![[Tries - Max XOR Walk.excalidraw|800]]

### 5.1 Maximum XOR of two numbers

```
for each x in a:
    insert x
    walk: at bit b (from 30 down to 0), prefer the child with bit (x_b XOR 1); if it exists, set bit b of the result
    best = max(best, result)
```

```java
static int findMaximumXOR(int[] a) {               // a[i] ≥ 0
    int[][] next = new int[a.length * 31 + 1][2];  // node 0 is the root; 0 also means "no child"
    int nodes = 1, best = 0;
    for (int x : a) {
        int cur = 0;
        for (int b = 30; b >= 0; b--) {            // insert x
            int bit = (x >> b) & 1;
            if (next[cur][bit] == 0) next[cur][bit] = nodes++;
            cur = next[cur][bit];
        }
        cur = 0;
        int xr = 0;
        for (int b = 30; b >= 0; b--) {            // best partner among the numbers so far
            int bit = (x >> b) & 1;
            if (next[cur][bit ^ 1] != 0) { xr |= 1 << b; cur = next[cur][bit ^ 1]; }   // opposite bit
            else cur = next[cur][bit];
        }
        best = Math.max(best, xr);
    }
    return best;
}
```

`[3, 10, 5, 25, 2, 8]` → `28` (`5 ^ 25`). `O(31 n)` time, versus `O(n²)` for all pairs. Inserting `x` before querying means the walk always finds a complete path (at worst `x` itself, giving 0), so `cur` never falls off the trie; a one-element array returns `0`.

Using `0` as "no child" is safe because node 0 is the root, and the root is never anyone's child. The bit width must cover the largest value: `a[i] < 2³¹` for non-negative `int`s, so bits 30…0. With **negative** numbers, bit 31 (the sign bit) matters too and the meaning of "maximum" depends on whether the result is read as signed; include bit 31 and use `>>>`.

### 5.2 Maximum XOR with an element no larger than `m` (offline queries)

Each query `(x, m)` asks for `max(x ^ y)` over `y ≤ m`. Sort the queries by `m` and the numbers ascending; before answering a query, insert every number `≤ m`. Each query then runs on exactly the right set.

```java
static int[] maximizeXor(int[] nums, int[][] queries) {    // queries[i] = {x, m}
    int[] a = nums.clone();
    Arrays.sort(a);
    Integer[] order = new Integer[queries.length];
    for (int i = 0; i < order.length; i++) order[i] = i;
    Arrays.sort(order, Comparator.comparingInt(i -> queries[i][1]));   // by limit m
    int[][] next = new int[a.length * 31 + 1][2];
    int nodes = 1, j = 0;
    int[] res = new int[queries.length];
    for (int qi : order) {
        int x = queries[qi][0], m = queries[qi][1];
        while (j < a.length && a[j] <= m) {        // insert everything allowed for this query
            int cur = 0;
            for (int b = 30; b >= 0; b--) {
                int bit = (a[j] >> b) & 1;
                if (next[cur][bit] == 0) next[cur][bit] = nodes++;
                cur = next[cur][bit];
            }
            j++;
        }
        if (j == 0) { res[qi] = -1; continue; }    // no number ≤ m: the trie is empty
        int cur = 0, xr = 0;
        for (int b = 30; b >= 0; b--) {
            int bit = (x >> b) & 1;
            if (next[cur][bit ^ 1] != 0) { xr |= 1 << b; cur = next[cur][bit ^ 1]; }
            else cur = next[cur][bit];
        }
        res[qi] = xr;
    }
    return res;
}
```

`nums = [0, 1, 2, 3, 4]`, queries `[[3, 1], [1, 3], [5, 6]]` → `[3, 3, 7]`; `nums = [5, 2, 4, 6, 6, 3]`, `[[12, 4], [8, 1], [6, 3]]` → `[15, -1, 5]`. Answering **offline** (reordering queries, then writing answers back by original index) is a general technique; Mo's algorithm is another instance ([[DSA/04 - Trees and Hierarchical Structures/09 - Sqrt Decomposition|Sqrt Decomposition]]).

> [!example]- Deletions and counting queries (advanced)
> - **Deletions** (a sliding window of numbers, or "remove `y`"): store a counter per node, incremented on insert and decremented on removal, and treat a child with count 0 as absent during the walk.
> - **Count pairs with `x ^ y < k`**: walk `x`'s path alongside `k`'s bits. Where `k` has a 1, every `y` in the child that makes the XOR bit 0 gives a smaller XOR, so add that child's count, then continue into the child that makes the XOR bit 1. Where `k` has a 0, the XOR bit must be 0. `O(31)` per number.
> - **Maximum XOR of a subarray**: prefix XORs `P[i]` turn it into "maximum `P[i] ^ P[j]`" ([[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays#3. Beyond Sums|Prefix Sums § 3]]): insert prefixes one by one (starting with `P[0] = 0`) and query each.

---

## 6. Implementation Choices and Memory

| Children stored as | Child lookup | Memory per node | Use when |
|---|---|---|---|
| `Node[26]` array | `O(1)` | 26 references (~100–200 bytes) | small fixed alphabet; most problems |
| `HashMap<Character, Node>` | `O(1)` expected, slower constant | proportional to actual children, plus map overhead | large or unknown alphabet (Unicode) |
| `TreeMap<Character, Node>` | `O(log σ)` | proportional to children | need ordered iteration over a large alphabet |
| global `int[][] next` + node counter | `O(1)` | `σ` ints per node, no objects | contests: fast allocation, no GC pressure |

The array version is wasteful when nodes are sparse: a million characters of input can mean a million nodes × 26 references, over 100 MB. When memory is the limit, use maps, a global array sized `total length + 1`, or a **compressed trie** (radix tree / Patricia trie), which merges every chain of single-child non-word nodes into one edge labelled with a string; it has at most `2n` nodes for `n` words.

| | `HashSet<String>` | Trie |
|---|---|---|
| Insert / exact lookup | `O(L)` expected (hashing reads the whole string) | `O(L)` worst case |
| "Any word with prefix `p`?" | `O(n · L)` scan, or store all prefixes | `O(|p|)` |
| Count / list words with prefix `p` | scan | `O(|p|)` / `O(|p| + output)` |
| Sorted iteration | sort first | DFS in alphabet order |
| Wildcards, grid search pruning | no | yes |
| Memory | compact | can be large |

For plain membership on a static set, a `HashSet` is simpler and usually faster. Use a trie when **prefixes** matter.

---

## 7. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| `search` returns `walk(w) != null` | prefixes reported as words | also check `end` |
| `startsWith` checks `end` | `startsWith("app")` false with only `"apple"` stored | the node's existence is enough |
| `c − 'a'` on uppercase, digits, spaces | `ArrayIndexOutOfBoundsException` | size for the real alphabet / map characters |
| Boolean end flag for duplicate words | counts wrong; deleting one copy deletes all | integer counts |
| Deleting nodes on a shared path | other words disappear | prune only unused branches (`pass == 0`) |
| Erasing a word that isn't present | counts go negative | check presence first |
| Autocomplete adding the word after its children | `"mousepad"` before `"mouse"` | record the node's word before recursing |
| Not guarding a `null` node after a failed character | `NullPointerException` on longer prefixes | stay `null` once off the trie |
| Word search II without clearing found words | duplicates in the result | set `word = null` after reporting |
| Word search II not restoring the cell | later paths miss valid words | restore after the four calls |
| Stopping word search at the first found word | misses longer words on the same path | keep searching below it |
| XOR trie with too few bits | wrong maximum for large values | cover the highest set bit (30 for non-negative `int`) |
| XOR trie querying an empty trie | walks into "no child" nodes and returns garbage | insert first, or check emptiness |
| Array trie sized by the number of words | index out of bounds | size by total characters + 1 |

---

## 8. Trick Questions and Special Cases

> [!question]- Only `"apple"` is stored. `search("app")`? `startsWith("app")`? `startsWith("apple")`? `startsWith("apples")`?
> `false`, `true`, `true`, `false`. A word is a prefix of itself, so `startsWith` of a stored word is always `true`.

> [!question]- How many new nodes does inserting `"app"` create after `"apple"`?
> Zero. The nodes for `a`, `ap`, `app` already exist; only the end flag on `app` changes.

> [!question]- How many nodes, including the root, for the words `"a"`, `"ab"`, `"abc"`? For `"abc"`, `"abd"`, `"x"`?
> `4` (root, `a`, `ab`, `abc`): each word extends the previous one. `6` (root, `a`, `ab`, `abc`, `abd`, `x`).

> [!question]- What does `startsWith("")` return on an **empty** trie? `search("")`?
> `startsWith("")` is `true`: the empty string's node is the root, which always exists. `search("")` is `false` unless the empty string was inserted (which sets `root.end`).

> [!question]- With a boolean trie, insert `"cat"` twice, then delete it once. Is `"cat"` still there?
> No: the flag can't record two copies, so one delete removes the word entirely. A multiset needs integer counts.

> [!question]- Delete `"apple"` from a trie that holds `"app"` and `"apple"`. Which nodes go?
> Only `l` and `e` (the nodes below `app`). The node `app` ends a word, so pruning stops there; deleting further would also delete `"app"`.

> [!question]- Is every leaf the end of a word? Is every word-end a leaf?
> In a trie built only by insertions, every leaf is a word end (a node is created only on the way to a word's end). But word ends can be internal: `"in"` when `"inn"` is stored. After deletions without pruning, dead leaves can exist too.

> [!question]- In what order does a DFS over a trie (children `a` to `z`) list `"app"`, `"apple"`, `"apply"`, `"apt"`?
> `app, apple, apply, apt`, the lexicographic order, provided each node's own word is emitted **before** its children. Emitting after the children gives `apple, apply, app, apt`.

> [!question]- Replace words with roots `["a", "aa", "aaa"]` in `"aaaa"`?
> `"a"`: the walk stops at the first end flag it reaches. Continuing to the deepest end flag returns the **longest** root, `"aaa"`, which is the wrong answer here.

> [!question]- Wildcard dictionary with `"bad"` only: `search("...")`? `search("..")`? `search("....")`?
> `true`, `false`, `false`. Dots match exactly one character each; the walk must end at a node with the end flag after consuming the whole pattern.

> [!question]- Maximum XOR of `[7]`? Of `[0, 0]`? Of `[8, 10, 2]`?
> `0` (a number XOR itself), `0`, and `10` (`8 ^ 2 = 10`; `8 ^ 10 = 2`, `10 ^ 2 = 8`).

> [!question]- Why is the greedy "take the opposite bit if possible" walk correct for maximum XOR?
> Bit `b` is worth `2ᵇ`, more than all lower bits combined (`2ᵇ − 1`). So making bit `b` of the result 1 beats any choice that makes it 0, no matter what happens below. The trie tells, at each step, whether some stored number with the already-chosen higher bits has the needed bit.

> [!question]- Word search II with words `["a", "aa"]` on the board `[["a", "a"]]`: what's the result?
> Both: `"a"` (found at the first cell, reported once, then cleared) and `"aa"` (the search continues below the node for `"a"`). Stopping at the first word found, or not clearing it, gives `["a"]` or `["a", "a", "aa", …]`.

> [!question]- A `HashSet<String>` lookup and a trie lookup are both `O(L)`. Why isn't hashing `O(1)`?
> Computing a `String`'s hash reads every character (Java caches the hash per `String` object, but a new query string is hashed from scratch), and `equals` compares characters on a hit. Both are linear in the word length; the trie's advantage is prefix queries, not speed of exact lookup.

---

## 9. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `search("app")` with only `"apple"` | `false` | end flag |
| `startsWith("app")` with only `"apple"` | `true` | node exists |
| `startsWith("")` on an empty trie | `true` | root |
| Insert `"app"` after `"apple"` | 0 new nodes | flag only |
| Nodes for `"a"`, `"ab"`, `"abc"` | 4 with the root | shared prefixes |
| Max nodes | `1 + total length` | |
| `'A' − 'a'` | `−32` | index out of bounds |
| LCP of `["ab", "a"]` | `"a"` | stop at end flag |
| Replace words, roots `["a","aa"]`, word `"aaa"` | `"a"` | first end flag |
| `search("..")` with only `"bad"` | `false` | must end at a word |
| `findMaximumXOR([3,10,5,25,2,8])` | `28` | `5 ^ 25` |
| `findMaximumXOR([7])` | `0` | `x ^ x` |
| `maximizeXor` with no number `≤ m` | `−1` | empty trie |
| DFS order with word-before-children | lexicographic | |
| Array trie memory | `σ` references per node | ~100+ MB per million nodes at `σ = 26` |
| Compressed trie nodes | `≤ 2n` | single-child chains merged |

---

## 10. Summary

- A trie stores strings along root-to-node paths; a node per prefix, an **end flag** per word. Insert, search, and prefix checks are `O(L)`, independent of the number of words.
- `search` needs the end flag; `startsWith` only needs the node. Words can end at internal nodes.
- **Counts** (`pass`, `end`) give prefix counts, duplicates, and safe deletion that prunes only unused branches.
- Applications: longest common prefix, shortest-root replacement, wildcard search, autocomplete in lexicographic order, and word search II (one backtracking search pruned by the trie).
- **Bitwise tries** answer maximum-XOR queries greedily from the highest bit; offline sorting handles limits like `y ≤ m`.
- Memory is the cost: choose arrays, maps, a global `int[][]`, or a compressed trie according to the alphabet and the input size. For plain membership, a `HashSet` is enough.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|Heaps and Priority Queues]] · Next: [[DSA/04 - Trees and Hierarchical Structures/06 - Union-Find|Union-Find]]
- [[DSA/02 - Linear Data Structures/02 - Strings|Strings]]: longest common prefix by direct comparison
- [[DSA/01 - Foundations/03 - Bit Manipulation|Bit Manipulation]]: XOR properties behind the bitwise trie
- [[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]]: prefix XOR for subarray XOR problems
- [[DSA/06 - Algorithm Design Paradigms/03 - Backtracking|Backtracking]]: grid word search
- [[DSA/07 - String Algorithms/01 - String Matching|String Matching]]: Aho–Corasick, a trie with failure links
- [[DSA/07 - String Algorithms/04 - Suffix Structures|Suffix Structures]]: suffix tries, trees, and automata
