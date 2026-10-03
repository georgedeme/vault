# Strings

A <span class="hl-blue">string</span> is a sequence of characters. Algorithmically it's an array of characters, and most array techniques carry over directly: indices, two pointers, frequency counting, sliding windows. What makes strings their own topic in Java is the representation: `String` is **immutable**, characters are 16-bit integers, and the library is full of methods whose cost and edge-case behaviour aren't obvious from their names.

This note covers the cost model of `String` and `StringBuilder`, character arithmetic, frequency counting, anagram and palindrome basics, the common manipulation patterns (reversal, compression, parsing, big-number arithmetic), and the `split`/`compareTo`/Unicode traps. The language basics (literals, the pool, the method list) are in [[Java/03 - Program Structure/02 - Strings|Java: Strings]]. Pattern matching (KMP, Z, Rabin–Karp) and palindrome algorithms (Manacher) have their own chapters in Part VII.

## Contents

- [[#1. Terminology|1. Terminology]]
- [[#2. The Cost Model of String|2. The Cost Model of String]]
- [[#3. StringBuilder and char Arrays|3. StringBuilder and char Arrays]]
- [[#4. Characters Are Integers|4. Characters Are Integers]]
- [[#5. Character Frequency Counting|5. Character Frequency Counting]]
- [[#6. Anagrams and Character Mappings|6. Anagrams and Character Mappings]]
- [[#7. Palindrome Basics|7. Palindrome Basics]]
- [[#8. Common Manipulation Patterns|8. Common Manipulation Patterns]]
- [[#9. Parsing and Number Conversion|9. Parsing and Number Conversion]]
- [[#10. Comparison, Splitting, and Unicode Traps|10. Comparison, Splitting, and Unicode Traps]]
- [[#11. Common Mistakes|11. Common Mistakes]]
- [[#12. Trick Questions and Special Cases|12. Trick Questions and Special Cases]]
- [[#13. Quick Reference — Non-Obvious Outcomes|13. Quick Reference — Non-Obvious Outcomes]]
- [[#14. Summary|14. Summary]]

---

## 1. Terminology

> [!note] Definitions
> For a string `s` of length `n`:
> - A <span class="hl-blue">substring</span> is a **contiguous** block `s[i..j]`. There are `n(n+1)/2` non-empty substrings (counting position, not distinct content).
> - A <span class="hl-blue">subsequence</span> keeps characters in order but may skip some: `"ace"` is a subsequence of `"abcde"`. There are `2ⁿ` subsequences (including the empty one).
> - A <span class="hl-blue">prefix</span> is `s[0..j]`, a <span class="hl-blue">suffix</span> is `s[i..n−1]`. There are `n + 1` of each, counting the empty one.
> - Two strings are <span class="hl-blue">anagrams</span> if one is a rearrangement of the other (same character counts).
> - A <span class="hl-blue">palindrome</span> reads the same forwards and backwards.

> [!warning] "Substring" vs. "subsequence" in problem statements
> They lead to completely different algorithms. Longest common **substring** is a contiguous-match DP (or suffix structures); longest common **subsequence** is the classic LCS DP. Read the statement twice. Problems about arrays use **subarray** (contiguous) vs. **subsequence** in the same way.

---

## 2. The Cost Model of String

A Java `String` wraps a private array of characters (since Java 9, a `byte[]` holding either Latin-1 bytes or UTF-16 pairs, "compact strings") plus a cached hash. The contents can never change, so every "modifying" method builds a new string.

| Operation | Cost | Notes |
|---|---|---|
| `length()`, `charAt(i)` | `O(1)` | |
| `substring(i, j)` | `O(j − i)` | a **copy** (since Java 7u6; earlier versions shared the array in `O(1)`) |
| `s + t`, `concat` | `O(len(s) + len(t))` | new string |
| `equals`, `compareTo` | `O(min(len(s), len(t)))` | `equals` returns early on different lengths |
| `hashCode()` | `O(n)` first call, then `O(1)` | cached in the object |
| `indexOf`, `contains`, `replace` | `O(n·m)` worst case | naive matching; KMP/Z give `O(n + m)` ([[DSA/07 - String Algorithms/01 - String Matching|String Matching]]) |
| `toCharArray()`, `toLowerCase()`, `trim()`, `strip()` | `O(n)` | new array / string |
| `split(regex)` | `O(n)` plus regex overhead | single-character non-metacharacter delimiters take a fast path |
| `String.valueOf(char[])`, `new String(char[])` | `O(n)` | copies the array |
| `s.repeat(k)` | `O(n·k)` | Java 11+ |

> [!important] Concatenation in a loop is quadratic
> ```java
> String s = "";
> for (int i = 0; i < n; i++) s += c;    // copies the whole string every iteration
> ```
> Iteration `i` copies `i` characters, so the total is `1 + 2 + … + n = Θ(n²)`. For `n = 10⁵` that's about 5 × 10⁹ character copies: a certain TLE. The compiler optimizes `+` **within one expression** (into a `StringBuilder` or an `invokedynamic` concat), but it can't carry a buffer across loop iterations. Use a `StringBuilder`.

> [!tip] Strings as hash keys cost O(length)
> Every `HashMap<String, …>` lookup computes or compares the key in `O(L)` (the hash is cached per `String` object, but `equals` on a hit still scans). For `n` keys of length `L`, budget `O(n·L)`, not `O(n)`. When `L` is large and keys are substrings of one big string, use polynomial hashes instead ([[DSA/07 - String Algorithms/02 - String Hashing|String Hashing]]).

---

## 3. StringBuilder and char Arrays

### 3.1 StringBuilder costs

`StringBuilder` is a dynamic array of characters ([[DSA/02 - Linear Data Structures/01 - Arrays#3. Dynamic Arrays and Amortized Resizing|Arrays § 3]]): initial capacity 16, growth to `2 × old + 2`.

| Operation | Cost |
|---|---|
| `append(x)` | `O(1)` amortized (plus the length of `x`) |
| `charAt(i)`, `setCharAt(i, c)` | `O(1)` |
| `deleteCharAt(length() − 1)`, `setLength(len − 1)` | `O(1)` |
| `insert(0, x)`, `deleteCharAt(0)` | `O(n)`: shifts everything |
| `insert(i, x)`, `delete(i, j)` | `O(n − i)` |
| `reverse()` | `O(n)` |
| `toString()` | `O(n)`: copies into a new `String` |

> [!warning] Building a result back-to-front
> `sb.insert(0, c)` in a loop is `Θ(n²)`, exactly the problem `StringBuilder` was supposed to solve. Append in reverse order and call `reverse()` once at the end ([[#8.5 Adding numbers given as strings|§8.5]]).

> [!warning] `StringBuilder` does not override `equals`
> `sb1.equals(sb2)` is reference equality, so two builders with the same content are "not equal", and `StringBuilder` is useless as a `HashMap` key or `HashSet` element (its hash is identity-based and its content is mutable anyway). Compare with `sb1.toString().equals(sb2.toString())`, `sb1.compareTo(sb2) == 0` (Java 11+), or `str.contentEquals(sb)`.

> [!tip] `StringBuilder` as a backtracking buffer
> Append before recursing and `setLength(len)` after, to undo. `setLength` only moves the size, so it's `O(1)`. The same "choose, recurse, un-choose" pattern as in [[DSA/01 - Foundations/02 - Recursion#6.3 Generating all subsets (include / exclude)|Recursion § 6.3]].
> ```java
> int len = sb.length();
> sb.append(c);
> dfs(...);
> sb.setLength(len);      // undo
> ```

### 3.2 When to drop to `char[]`

For in-place algorithms (reverse, swap characters, sort the characters, two-pointer rewrites), convert once and work on the array:

```java
char[] cs = s.toCharArray();   // O(n) copy
// ... modify cs in place ...
String result = new String(cs); // O(n) copy back (String.valueOf(cs) is the same)
```

> [!warning] `cs.toString()` is not the string
> `char[]` inherits `Object.toString()`, so `cs.toString()` returns something like `"[C@1b6d3586"`. Use `new String(cs)` or `String.valueOf(cs)`. The same applies to `"" + cs`. (`System.out.println(cs)` is the one exception: `println` has a `char[]` overload and prints the characters.)

> [!info]- `StringBuffer`
> `StringBuffer` is the synchronized, thread-safe version from Java 1.0. Every method takes a lock, which costs time and buys nothing in single-threaded code. Use `StringBuilder`.

---

## 4. Characters Are Integers

`char` is an **unsigned 16-bit integer** (a UTF-16 code unit, `0` to `65535`). Arithmetic on `char`s promotes them to `int`.

### 4.1 Values worth knowing

| Character | Code | | Character | Code |
|---|---|---|---|---|
| `'\0'` | 0 | | `'A'` | 65 |
| `' '` (space) | 32 | | `'Z'` | 90 |
| `'0'` | 48 | | `'a'` | 97 |
| `'9'` | 57 | | `'z'` | 122 |

Upper and lower case differ by exactly **32**, which is a single bit (bit 5). Uppercase letters sort **before** lowercase ones.

![[Strings - Character Codes.excalidraw|800]]

### 4.2 The standard conversions

| Goal | Code | Notes |
|---|---|---|
| letter → index `0..25` | `c - 'a'` | `int` result |
| index → letter | `(char) ('a' + i)` | cast needed: `'a' + i` is an `int` |
| digit char → value | `c - '0'` | |
| value → digit char | `(char) ('0' + d)` | |
| is ASCII digit | `c >= '0' && c <= '9'` | prefer this over `Character.isDigit`, see below |
| is lowercase letter | `c >= 'a' && c <= 'z'` | |
| to lowercase (ASCII letter) | `(char) (c \| 32)` | or `Character.toLowerCase(c)` |
| to uppercase (ASCII letter) | `(char) (c & ~32)` | |
| toggle case (ASCII letter) | `(char) (c ^ 32)` | |

The bit forms are explained in [[DSA/01 - Foundations/03 - Bit Manipulation|Bit Manipulation]]; they only make sense for letters (`'1' ^ 32` is `'\u0011'`).

> [!warning] `char` arithmetic surprises
> ```java
> System.out.println('a' + 'b');        // 195     (int addition)
> System.out.println("" + 'a' + 'b');   // ab      (string concatenation, left to right)
> System.out.println('a' + 1);          // 98
> System.out.println((char) ('a' + 1)); // b
> StringBuilder sb = new StringBuilder();
> sb.append('a' + 1);                   // appends "98": append(int) is chosen
> char c = 'a';
> c += 1;                               // OK: compound assignment casts implicitly
> c = c + 1;                            // compile error: int can't go into char without a cast
> ```

> [!warning] `Character.isDigit` and `Character.getNumericValue` are Unicode-aware
> - `Character.isDigit('٣')` (Arabic-Indic three) is `true`, and `'٣' - '0'` is 1,587. If the input could contain non-ASCII text, `c >= '0' && c <= '9'` is the safe test for "is a decimal digit I can convert with `c - '0'`".
> - `Character.getNumericValue('a')` returns **10** (and `'z'` gives 35), because letters are digits in base 36. It does not return `-1` for letters.
> - `Character.isLetter` and `isLetterOrDigit` accept letters from every script (`'é'`, `'ж'`, `'中'`).

---

## 5. Character Frequency Counting

Counting how many times each character appears is the first step of most anagram, palindrome, and window problems.

| Alphabet | Structure | Index |
|---|---|---|
| lowercase letters only | `int[26]` | `c - 'a'` |
| ASCII (letters, digits, punctuation) | `int[128]` | `c` |
| any `char` | `int[65536]` (256 KB) or `HashMap<Character, Integer>` | `c` |
| full Unicode (code points) | `HashMap<Integer, Integer>` | `s.codePointAt(i)` |

```
counts(s):
    cnt = array of 26 zeros
    for each character c in s:
        cnt[c − 'a'] += 1
    return cnt
```

```java
static int[] counts(String s) {
    int[] cnt = new int[26];
    for (int i = 0; i < s.length(); i++) cnt[s.charAt(i) - 'a']++;
    return cnt;
}
```

A fixed-size array is `O(1)` space (`O(σ)` for an alphabet of size `σ`), avoids boxing, and is several times faster than a map. Comparing two count arrays is `O(σ)` with `Arrays.equals(c1, c2)`.

### 5.1 One array, increment and decrement

To compare two strings' character multisets, count `s` up and `t` down in a single array. Every entry is zero exactly when the multisets match. This halves the memory and gives "how many more of `c` does `s` have than `t`" directly, which is the state that [[DSA/03 - Sorting and Searching/04 - Sliding Window|Sliding Window]] problems (find all anagrams, minimum window substring) maintain incrementally.

### 5.2 First unique character

```java
static int firstUniqChar(String s) {
    int[] cnt = new int[26];
    for (int i = 0; i < s.length(); i++) cnt[s.charAt(i) - 'a']++;
    for (int i = 0; i < s.length(); i++)
        if (cnt[s.charAt(i) - 'a'] == 1) return i;   // second pass in STRING order
    return -1;
}
```

> [!warning] Scan the string, not the count array, in the second pass
> Scanning `cnt` for the first entry equal to 1 finds the **alphabetically** first unique letter, not the first one in the string. For `"zaba"` the answer is `'z'` at index 0, but scanning the count array would report `'b'`.

---

## 6. Anagrams and Character Mappings

### 6.1 Anagram check

| Approach | Time | Space |
|---|---|---|
| Sort both, compare | `O(n log n)` | `O(n)` (the `char[]` copies) |
| Count characters | `O(n + σ)` | `O(σ)` |

```java
static boolean isAnagram(String s, String t) {
    if (s.length() != t.length()) return false;    // also makes the single loop safe
    int[] cnt = new int[26];
    for (int i = 0; i < s.length(); i++) {
        cnt[s.charAt(i) - 'a']++;
        cnt[t.charAt(i) - 'a']--;
    }
    for (int c : cnt) if (c != 0) return false;
    return true;
}
```

### 6.2 Grouping anagrams

Every word in a group must map to the **same key**, and words in different groups to different keys.

```
groupAnagrams(words):
    groups = empty map from key to list
    for w in words:
        key = canonical form of w         -- sorted letters, or a count signature
        groups[key].append(w)
    return all lists in groups
```

```java
static List<List<String>> groupAnagrams(String[] words) {
    Map<String, List<String>> groups = new HashMap<>();
    for (String w : words) {
        char[] cs = w.toCharArray();
        Arrays.sort(cs);
        String key = new String(cs);                 // NOT cs.toString()
        groups.computeIfAbsent(key, k -> new ArrayList<>()).add(w);
    }
    return new ArrayList<>(groups.values());
}
```

Sorted key: `O(n · L log L)` for `n` words of length `L`. A count-signature key is `O(n · (L + 26))`:

```java
static String countKey(String w) {
    int[] cnt = new int[26];
    for (int i = 0; i < w.length(); i++) cnt[w.charAt(i) - 'a']++;
    StringBuilder sb = new StringBuilder();
    for (int c : cnt) sb.append(c).append('#');      // separator is essential
    return sb.toString();
}
```

> [!warning] Signatures need separators
> Concatenating the counts without a separator makes different multisets collide: counts `(1, 11)` and `(11, 1)` both become `"111"`. With `'#'` they are `"1#11#"` and `"11#1#"`. Using an `int[]` as the key doesn't work at all: arrays use identity `equals`/`hashCode`. `Arrays.toString(cnt)` or `List<Integer>` keys work ([[DSA/02 - Linear Data Structures/06 - Hash Tables|Hash Tables]]).

### 6.3 Isomorphic strings and word patterns — the mapping must be a bijection

`s` and `t` are <span class="hl-blue">isomorphic</span> if the characters of `s` can be consistently replaced to get `t`, with no two characters of `s` mapping to the same character of `t`. `"egg"/"add"` yes; `"foo"/"bar"` no (`o` would map to both `a` and `r`); `"badc"/"baba"` no (`b→b` and `d→b`).

```java
static boolean isIsomorphic(String s, String t) {      // ASCII input
    if (s.length() != t.length()) return false;
    int[] sToT = new int[128], tToS = new int[128];   // 0 = unmapped; store char + 1
    for (int i = 0; i < s.length(); i++) {
        char a = s.charAt(i), b = t.charAt(i);
        if (sToT[a] == 0 && tToS[b] == 0) {
            sToT[a] = b + 1;
            tToS[b] = a + 1;
        } else if (sToT[a] != b + 1 || tToS[b] != a + 1) {
            return false;
        }
    }
    return true;
}
```

![[Strings - Isomorphic Mapping.excalidraw|800]]

> [!warning] One map is not enough
> Checking only `s → t` consistency accepts `"badc"/"baba"`: `b→b, a→a, d→b, c→a` is a consistent function but not one-to-one. You need the map in **both** directions (or a map plus a "used" set for the targets). "Word pattern" (`"abba"` vs. `"dog cat cat dog"`) is the same problem with words instead of characters.

> [!info]- Why store `char + 1`
> The arrays start full of zeros, and `'\0'` is a legitimate character, so `0` can't mean both "unmapped" and "maps to `'\0'`". Shifting by one reserves `0` as the sentinel. The same issue appears in memoization ([[DSA/01 - Foundations/02 - Recursion#10. From Recursion to Memoization|Recursion § 10]]). Alternatively, fill the arrays with `-1`.

---

## 7. Palindrome Basics

### 7.1 Two-pointer check

```
isPalindrome(s):
    lo = 0; hi = len(s) − 1
    while lo < hi:
        if s[lo] ≠ s[hi]: return false
        lo += 1; hi −= 1
    return true
```

`O(n)` time, `O(1)` space. Don't build `new StringBuilder(s).reverse().toString()` and compare: it's also `O(n)`, but it allocates two extra strings and can't be adapted to the variants below.

### 7.2 Ignoring non-alphanumerics and case

```java
static boolean isPalindromeAlnum(String s) {
    int lo = 0, hi = s.length() - 1;
    while (lo < hi) {
        char a = s.charAt(lo), b = s.charAt(hi);
        if (!Character.isLetterOrDigit(a)) { lo++; continue; }
        if (!Character.isLetterOrDigit(b)) { hi--; continue; }
        if (Character.toLowerCase(a) != Character.toLowerCase(b)) return false;
        lo++;
        hi--;
    }
    return true;
}
```

Edge cases: `""` and `" "` and `".,"` are all palindromes (nothing left to compare). `"0P"` is **not**: `'0'` and `'P'` are both alphanumeric and differ, and lowercasing doesn't make a digit equal a letter.

### 7.3 Palindrome after deleting at most one character

At the first mismatch, one of the two characters must go. Try **both**.

```java
static boolean validPalindromeOneDeletion(String s) {
    int lo = 0, hi = s.length() - 1;
    while (lo < hi) {
        if (s.charAt(lo) != s.charAt(hi))
            return isPalRange(s, lo + 1, hi) || isPalRange(s, lo, hi - 1);
        lo++;
        hi--;
    }
    return true;
}

static boolean isPalRange(String s, int lo, int hi) {
    while (lo < hi) if (s.charAt(lo++) != s.charAt(hi--)) return false;
    return true;
}
```

`O(n)`: the outer scan plus at most two range checks. Skipping only one side fails on `"cbbcc"`: the first mismatch is `b` (index 1) vs. `c` (index 3); deleting the left one leaves `"bc"` in the middle, but deleting the right one leaves `"bb"`, which works.

![[Strings - Palindrome With One Deletion.excalidraw|800]]

### 7.4 Questions about rearrangements

| Question | Answer from the counts |
|---|---|
| Can the letters be rearranged into a palindrome? | at most **one** character has an odd count |
| Longest palindrome buildable from these letters? | `Σ (cnt / 2) × 2`, plus 1 if any count is odd |
| Minimum characters to add so a rearrangement is a palindrome | `max(0, #odd − 1)` |

The odd-count test is a parity question, so it can also be done with a bitmask: flip bit `c − 'a'` per character, then the answer is "mask has at most one bit set", `(mask & (mask − 1)) == 0` ([[DSA/01 - Foundations/03 - Bit Manipulation#4.1 Power-of-two tests|Bit Manipulation § 4.1]]). Prefix parity masks extend this to "count substrings that can be rearranged into a palindrome".

Longest palindromic substring (expand around center, Manacher) and palindromic DP are covered in [[DSA/07 - String Algorithms/03 - Palindromes|Palindromes]].

---

## 8. Common Manipulation Patterns

### 8.1 Reverse a string

```java
static String reverse(String s) {
    char[] cs = s.toCharArray();
    for (int lo = 0, hi = cs.length - 1; lo < hi; lo++, hi--) {
        char t = cs[lo]; cs[lo] = cs[hi]; cs[hi] = t;
    }
    return new String(cs);
}
```

Or `new StringBuilder(s).reverse().toString()`, which also keeps surrogate pairs (emoji) intact ([[#10.4 Unicode — length() is not the number of characters|§10.4]]). Recursion with `substring` is `Θ(n²)` ([[DSA/01 - Foundations/02 - Recursion#5.1 Helper functions with extra parameters|Recursion § 5.1]]).

### 8.2 Reverse the words

`"  the sky  is blue "` → `"blue is sky the"`: one space between words, none at the ends.

```java
static String reverseWords(String s) {
    String[] words = s.trim().split("\\s+");
    StringBuilder sb = new StringBuilder();
    for (int i = words.length - 1; i >= 0; i--) {
        sb.append(words[i]);
        if (i > 0) sb.append(' ');
    }
    return sb.toString();
}
```

> [!info]- In place on a `char[]` (O(1) extra space)
> Reverse the whole array, then reverse each word. Then compact the spaces with a write pointer ([[DSA/02 - Linear Data Structures/01 - Arrays#5.3 Remove elements in place (write pointer)|Arrays § 5.3]]): copy a word, then write one space only if another word follows. This is the same double-reversal idea as array rotation ([[DSA/02 - Linear Data Structures/01 - Arrays#6.1 Three reversals|Arrays § 6.1]]).

### 8.3 Run-length encoding: the group loop

`"aaabccdddd"` → `"a3b1c2d4"`. Process **maximal runs** with an inner loop, rather than comparing each character with the previous one:

```
encode(s):
    i = 0
    while i < n:
        j = i
        while j < n and s[j] == s[i]: j += 1     -- s[i..j−1] is one run
        output s[i], (j − i)
        i = j
```

```java
static String runLengthEncode(String s) {
    StringBuilder sb = new StringBuilder();
    int i = 0, n = s.length();
    while (i < n) {
        int j = i;
        while (j < n && s.charAt(j) == s.charAt(i)) j++;
        sb.append(s.charAt(i)).append(j - i);
        i = j;
    }
    return sb.toString();
}
```

> [!tip] Why the group loop
> The "compare with the previous character" version must flush the last run **after** the loop, and forgetting that is the most common bug. The group loop has no special last case. It also gives the run boundaries `[i, j)` directly, which many problems need (count binary substrings, longest run, decode a compressed string).

> [!warning] Decoding with multi-digit counts
> `"a12b3"` means 12 `a`s, not `a`, `1`, `2`. When decoding, read **all** consecutive digits into a number (`num = num * 10 + (c − '0')`). If the original text can contain digits itself, run-length encoding is ambiguous unless counts are delimited. Nested encodings like `"3[a2[c]]"` need a stack ([[DSA/02 - Linear Data Structures/04 - Stacks|Stacks]]).

### 8.4 Longest common prefix

```java
static String longestCommonPrefix(String[] strs) {
    if (strs.length == 0) return "";
    for (int i = 0; i < strs[0].length(); i++) {
        char c = strs[0].charAt(i);
        for (int k = 1; k < strs.length; k++)
            if (i == strs[k].length() || strs[k].charAt(i) != c)
                return strs[0].substring(0, i);
    }
    return strs[0];
}
```

Vertical scanning: `O(total length)` worst case, and it stops at the first column that disagrees. Alternative: sort the array, and the LCP of the **first and last** strings is the LCP of all of them (`O(n L log n)` though, because of the sort). For many queries, use a [[DSA/04 - Trees and Hierarchical Structures/05 - Tries|Trie]].

### 8.5 Adding numbers given as strings

Numbers too long for `long` arrive as strings. Add digit by digit from the **right**, carrying.

```java
static String addStrings(String a, String b) {
    StringBuilder sb = new StringBuilder();
    int i = a.length() - 1, j = b.length() - 1, carry = 0;
    while (i >= 0 || j >= 0 || carry > 0) {        // carry > 0: don't lose the final carry
        int sum = carry;
        if (i >= 0) sum += a.charAt(i--) - '0';
        if (j >= 0) sum += b.charAt(j--) - '0';
        sb.append((char) ('0' + sum % 10));
        carry = sum / 10;
    }
    return sb.reverse().toString();                  // built least-significant first
}
```

Binary addition is the same with base 2. **Multiplication** of two `n`-digit strings: `res[i + j + 1] += d1[i] × d2[j]` into an `int[n + m]`, then propagate carries right to left and strip leading zeros. Result length is at most `n + m`. For contest-sized numbers, `java.math.BigInteger` is the practical tool (its multiplication switches to Karatsuba/Toom-Cook for large inputs).

### 8.6 Is `s` a subsequence of `t`?

```java
static boolean isSubsequence(String s, String t) {
    int i = 0;
    for (int j = 0; j < t.length() && i < s.length(); j++)
        if (s.charAt(i) == t.charAt(j)) i++;     // greedy: match as early as possible
    return i == s.length();
}
```

`O(|t|)`. Greedy earliest matching is optimal, because matching `s[i]` later can never help the rest of `s`. For **many** queries `s₁, s₂, …` against one long `t`, precompute, for each position and character, the next occurrence (`next[pos][c]`, `O(26·|t|)`), or keep per-character lists of positions and binary search them.

---

## 9. Parsing and Number Conversion

| Call | Result | Notes |
|---|---|---|
| `Integer.parseInt("42")` | `42` | |
| `Integer.parseInt("+42")` | `42` | leading `+` allowed since Java 7 |
| `Integer.parseInt(" 42")` | `NumberFormatException` | no whitespace allowed; `trim()` first |
| `Integer.parseInt("")` | `NumberFormatException` | |
| `Integer.parseInt("2147483648")` | `NumberFormatException` | overflow is an error, not a wrap |
| `Integer.parseInt("101", 2)` | `5` | any radix `2..36` |
| `Integer.parseInt("ff", 16)` | `255` | |
| `Long.parseLong(...)` | | for values beyond `int` |
| `Integer.toString(255, 16)` | `"ff"` | |
| `Integer.toBinaryString(-1)` | `"11111111111111111111111111111111"` | two's complement, no sign |
| `Integer.toString(-5, 2)` | `"-101"` | signed |
| `String.valueOf(3.0)` | `"3.0"` | |

### 9.1 Writing `atoi` by hand: overflow before it happens

The usual specification: skip leading spaces, read an optional sign, read digits until a non-digit, and clamp to the `int` range on overflow.

```
atoi(s):
    skip spaces; read optional '+' or '−' into sign
    result = 0
    while next char is a digit d:
        if result > (MAX − d) / 10: return sign = + ? MAX : MIN    -- result·10 + d would exceed MAX
        result = result × 10 + d
    return sign × result
```

```java
static int myAtoi(String s) {
    int i = 0, n = s.length();
    while (i < n && s.charAt(i) == ' ') i++;
    int sign = 1;
    if (i < n && (s.charAt(i) == '+' || s.charAt(i) == '-')) {
        if (s.charAt(i) == '-') sign = -1;
        i++;
    }
    int result = 0;
    while (i < n && s.charAt(i) >= '0' && s.charAt(i) <= '9') {
        int d = s.charAt(i) - '0';
        if (result > (Integer.MAX_VALUE - d) / 10)       // check BEFORE multiplying
            return sign == 1 ? Integer.MAX_VALUE : Integer.MIN_VALUE;
        result = result * 10 + d;
        i++;
    }
    return sign * result;
}
```

> [!important] Why this handles `-2147483648`
> The magnitude `2147483648` doesn't fit in an `int`, so the check fires on the last digit, and the function returns `Integer.MIN_VALUE`, which happens to be exactly right. Checking **after** the multiplication doesn't work, because by then the value has already wrapped around. Accumulating in a `long` also works, but only if you check after every digit: a 30-digit input overflows `long` too.

### 9.2 Digits of a number

```java
int n = 9071, sum = 0;
while (n > 0) { sum += n % 10; n /= 10; }       // digits from least significant
```

Fails for `n = 0` if you need "one digit, 0" (the loop doesn't run), and for negative `n` (`%` keeps the sign). `String.valueOf(n)` and iterating characters is simpler when performance doesn't matter. Base conversion and digit sums are in [[DSA/01 - Foundations/04 - Math for Algorithms#11.3 Digits and bases|Math for Algorithms § 11.3]].

---

## 10. Comparison, Splitting, and Unicode Traps

### 10.1 `==` vs. `equals`

`==` compares references. It sometimes "works" because string literals and compile-time constant expressions are interned in the pool ([[Java/03 - Program Structure/02 - Strings#2. Creating Strings — Literals vs. `new`|Java: Strings § 2]]), which hides the bug until the strings come from input or are built at run time. Always use `equals`.

```java
String a = "ab";
String b = "a" + "b";          // constant expression, folded at compile time → pooled
System.out.println(a == b);    // true
String x = "a";
System.out.println(a == x + "b");        // false: built at run time
final String y = "a";
System.out.println(a == y + "b");        // true: y is a constant variable, so this is folded too
```

### 10.2 `compareTo` is lexicographic by UTF-16 code

`s.compareTo(t)` returns the difference of the **first differing characters**, or the **difference in lengths** if one string is a prefix of the other.

| Expression | Result | Reason |
|---|---|---|
| `"apple".compareTo("apply")` | `-20` | `'e' − 'y'` |
| `"apple".compareTo("app")` | `2` | prefix: `5 − 3` |
| `"Apple".compareTo("apple")` | `-32` | `'A' − 'a'`: uppercase sorts first |
| `"10".compareTo("9")` | `-8` | `'1' < '9'`: `"10"` sorts **before** `"9"` |
| `"a".compareToIgnoreCase("B")` | negative | compares case-folded characters |

> [!warning] Sorting numbers stored as strings
> Lexicographic order puts `"10"` before `"9"` and `"100"` before `"20"`. To compare non-negative integers as strings (without leading zeros), compare **lengths first**, then lexicographically: `a.length() != b.length() ? a.length() - b.length() : a.compareTo(b)`.

> [!info]- The "largest number" comparator
> Arrange numbers to form the largest concatenation (`[3, 30, 34, 5, 9]` → `"9534330"`). Neither numeric nor lexicographic order works: `"3"` vs. `"30"` should give `"330"`, not `"303"`. Sort with the comparator `(a, b) -> (b + a).compareTo(a + b)`. Edge case: all zeros give `"000"`, which must be returned as `"0"`. Custom comparators are covered in [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms|Sorting Algorithms]].

### 10.3 `split` takes a regular expression

| Expression | Result | Why |
|---|---|---|
| `"a,b,,".split(",")` | `["a", "b"]` | **trailing** empty strings are removed |
| `"a,b,,".split(",", -1)` | `["a", "b", "", ""]` | a negative limit keeps them |
| `",a".split(",")` | `["", "a"]` | a **leading** empty string is kept |
| `"".split(",")` | `[""]` (length 1) | no match → the whole string |
| `"a.b".split(".")` | `[]` (length **0**) | `.` matches every character; all pieces are empty and trailing |
| `"a.b".split("\\.")` | `["a", "b"]` | escape metacharacters |
| `"a\|b".split("\|")` | `["a", "\|", "b"]` | `\|` alone matches the empty string, so it splits between every character |
| `" a  b".split(" ")` | `["", "a", "", "b"]` | every single space is a delimiter |
| `" a  b".trim().split("\\s+")` | `["a", "b"]` | the usual "split into words" |
| `"   ".trim().split("\\s+")` | `[""]` (length 1) | empty string, see row 4 |

Regex metacharacters that need escaping: `. | $ ^ * + ? ( ) [ ] { } \`. `Pattern.quote(delim)` escapes any literal delimiter. `replaceAll` and `replaceFirst` also take a regex (`"a.b".replaceAll(".", "x")` is `"xxx"`); `replace` takes a literal and still replaces **all** occurrences.

### 10.4 Unicode — length() is not the number of characters

`String` stores UTF-16 **code units**. Characters outside the Basic Multilingual Plane (most emoji, some CJK) take **two** units, a <span class="hl-blue">surrogate pair</span>.

```java
String s = "a😀";
s.length();                       // 3, not 2
s.codePointCount(0, s.length());  // 2
s.charAt(1);                      // '\uD83D', half of the emoji
```

- Reversing a `char[]` swaps the two halves of a pair and corrupts it. `StringBuilder.reverse()` treats surrogate pairs as single characters and keeps them intact.
- Iterate code points with `s.codePoints()` or `s.codePointAt(i)` plus `Character.charCount(cp)` when the input can contain such characters.
- Competitive-programming and interview inputs are almost always ASCII, and saying so is a reasonable assumption to state out loud.

> [!warning] Case conversion depends on the locale
> `"TITLE".toLowerCase()` on a JVM running in a Turkish locale gives `"tıtle"` (dotless ı), which breaks equality checks against `"title"`. Use `toLowerCase(Locale.ROOT)` for anything that isn't displayed to a user. Case conversion can also change the length: `"ß".toUpperCase()` is `"SS"`.

### 10.5 hashCode collisions are easy to construct

`String.hashCode()` is `s[0]·31ⁿ⁻¹ + s[1]·31ⁿ⁻² + … + s[n−1]` in `int` arithmetic. `"Aa"` and `"BB"` both hash to `2112`, and since a concatenation of colliding blocks also collides, `"AaAa"`, `"AaBB"`, `"BBAa"`, `"BBBB"` all share one hash. That's `2ᵏ` colliding strings of length `2k`, the basis of hash-flooding attacks ([[DSA/02 - Linear Data Structures/06 - Hash Tables|Hash Tables]]). Equal hashes never mean equal strings.

---

## 11. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| `s1 == s2` | works on literals, fails on input | `s1.equals(s2)` |
| `s.toUpperCase();` without assignment | nothing changes | `s = s.toUpperCase();` |
| `s += c` in a loop | `Θ(n²)`, TLE | `StringBuilder` |
| `sb.insert(0, c)` in a loop | `Θ(n²)` | append, then `reverse()` once |
| `sb1.equals(sb2)` | `false` for equal content | compare `toString()`s or use `compareTo` |
| `cs.toString()` on a `char[]` | `"[C@…"` | `new String(cs)` |
| `sb.append('a' + 1)` | appends `"98"` | `(char) ('a' + 1)` |
| `split(".")`, `split("\|")` | empty array / every character split | `split("\\.")`, `split("\\|")` |
| `split(" ")` on irregular spacing | empty tokens | `trim().split("\\s+")` |
| Count signature without separators | false anagram matches | append `'#'` after each count |
| Isomorphism checked one way only | accepts `"badc"/"baba"` | check both directions |
| First unique char: scanning the count array | alphabetically first, not first in string | scan the string |
| `Character.isDigit` then `c − '0'` | garbage on non-ASCII digits | `c >= '0' && c <= '9'` |
| `parseInt` on untrimmed input | `NumberFormatException` | `trim()` first |
| Overflow check after `result * 10 + d` | wrapped value passes the check | check before multiplying |
| Losing the final carry in string addition | `"99" + "1" = "00"` | loop while `carry > 0` too |
| Lexicographic sort of numeric strings | `"10" < "9"` | compare lengths first |
| Forgetting the last run in RLE | last group missing | group loop |
| `n(n+1)/2` substrings in an `int` | overflow for `n ≥ 65,536` | `long` |

---

## 12. Trick Questions and Special Cases

> [!question]- Is `s.substring(i, j)` O(1)?
> No. Since Java 7 update 6 it copies the characters, so it's `O(j − i)`. A loop that takes `substring`s of every prefix or suffix is `Θ(n²)` time **and** allocation. Older articles describing `O(1)` substrings (shared backing array) are about Java 6.

> [!question]- What does `"a.b.c".split(".").length` return?
> `0`. `.` is a regex matching any character, so every character is a delimiter, all the pieces between them are empty strings, and trailing empty strings are removed, leaving nothing.

> [!question]- What does `"".split(",").length` return? And `",".split(",").length`?
> `1` and `0`. When the delimiter doesn't occur, the result is the original string (`""`) as the single element. For `","`, there are two empty pieces, both trailing, so both are removed.

> [!question]- What does `System.out.println('a' + 'b' + "c")` print?
> `195c`. Evaluation is left to right: `'a' + 'b'` is `int` addition (`97 + 98 = 195`), then `195 + "c"` is concatenation. `"c" + 'a' + 'b'` prints `cab`.

> [!question]- Is `"Aa".hashCode() == "BB".hashCode()`?
> Yes, both are `2112`: `65·31 + 97 = 66·31 + 66`. Equal hash codes say nothing about equality, which is why `HashMap` always confirms with `equals`.

> [!question]- Are `"abc"` and `"abd"` anagrams if you only compare sums of character codes?
> The sums differ here, but a sum (or XOR) of codes is **not** a valid anagram test: `"ad"` and `"bc"` have the same sum (`97 + 100 = 98 + 99`) and aren't anagrams. Multisets need per-character counts (or a sort).

> [!question]- Does `isAnagram` need the length check?
> In the single-loop version, yes: the loop indexes both strings with the same `i`, so unequal lengths cause an exception or skip characters. The length check is also a free early exit.

> [!question]- Valid palindrome: is `"0P"` a palindrome after removing non-alphanumerics and ignoring case?
> No. Both characters are alphanumeric, and `'0'` is not equal to `'p'`. This is a LeetCode test case that catches solutions that lowercase and then compare with something like `Character.isLetter` only, or that treat digits as ignorable.

> [!question]- Is `"race a car"` a palindrome after cleaning?
> No: it becomes `"raceacar"`, whose reverse is `"racaecar"`. `"A man, a plan, a canal: Panama"` is the classic one that is.

> [!question]- Valid palindrome with one deletion: why isn't it enough to skip the left character on mismatch?
> Because sometimes only the right one works. In `"cbbcc"`, the first mismatch is index 1 (`b`) vs. index 3 (`c`). Skipping the left leaves `"bc"` (not a palindrome), but skipping the right leaves `"bb"`. Both choices must be tried, and because only one mismatch is allowed, each choice is a plain palindrome check, so it stays `O(n)`.

> [!question]- How many substrings does a string of length 10⁵ have? Can you list them?
> `n(n+1)/2 ≈ 5 × 10⁹` (which overflows `int`). Listing them is impossible within a time limit, and generating them with `substring` would also copy `Θ(n³)` characters in total. Problems that seem to ask about "all substrings" want a counting argument, a sliding window, hashing, or a suffix structure.

> [!question]- `String s = null; s += "a";` — what is `s`?
> `"nulla"`. String concatenation converts a `null` reference to the text `"null"`. `sb.append((String) null)` also appends `"null"`. But `s.length()` on the original `null` throws `NullPointerException`.

> [!question]- Which is `true`: `"ab" == "a" + "b"`, or `"ab" == x + "b"` with `String x = "a"`?
> The first. `"a" + "b"` is a compile-time constant expression, folded to `"ab"` and pooled. `x + "b"` is computed at run time into a new object. If `x` is declared `final String x = "a";`, it becomes a constant variable and the second comparison is also `true`. None of this should ever matter, because content comparison uses `equals`.

> [!question]- Is `new StringBuilder(s).reverse()` the same as reversing `s.toCharArray()`?
> For ASCII, yes. For text with surrogate pairs (emoji like `"😀"`), no: the `char[]` reversal swaps the two halves of each pair and produces invalid UTF-16, while `StringBuilder.reverse()` keeps each pair together.

> [!question]- Largest number from `[0, 0]`?
> `"0"`, not `"00"`. After sorting with the concatenation comparator, if the first string is `"0"`, every string is `"0"`, so return `"0"`.

> [!question]- Compare version numbers `"1.01"` and `"1.001"`. Equal?
> Yes, if revisions are compared as **integers** (`01` = `001` = `1`). Split on `"\\."` (not `"."`), parse each part, and treat missing parts as `0`, so `"1.0"` equals `"1"` and `"1.0.0.0"`. Comparing the strings directly gets all of these wrong.

---

## 13. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `s += c` over `n` iterations | `Θ(n²)` | copies the whole string each time |
| `substring(i, j)` | `O(j − i)` | copy since Java 7u6 |
| `sb.insert(0, x)` | `O(n)` | shifts the buffer |
| `sb.setLength(len)` | `O(1)` | undo for backtracking |
| `sb1.equals(sb2)` | reference comparison | not overridden |
| `char[].toString()` | `"[C@…"` | `Object.toString` |
| `'a' + 'b'` | `195` | `int` arithmetic |
| `'a' + 'b' + "c"` | `"195c"` | left-to-right |
| `sb.append('a' + 1)` | `"98"` | `append(int)` |
| `c = c + 1` (`char c`) | compile error | `int` → `char` needs a cast |
| `(char) (c ^ 32)` | toggles letter case | upper/lower differ by bit 5 |
| `Character.getNumericValue('a')` | `10` | base-36 digit |
| `Character.isDigit('٣')` | `true` | Unicode digit |
| `"Aa".hashCode() == "BB".hashCode()` | `true` (2112) | easy collisions |
| `"apple".compareTo("app")` | `2` | length difference |
| `"Apple".compareTo("apple")` | `-32` | uppercase sorts first |
| `"10".compareTo("9")` | negative | lexicographic |
| `"a.b".split(".")` | length 0 | regex `.`; trailing empties dropped |
| `"".split(",")` | `[""]` | no match → original |
| `"a\|b".split("\|")` | `["a","\|","b"]` | empty-string regex |
| `"a,,".split(",")` | `["a"]` | trailing empties removed |
| `"a,,".split(",", -1)` | `["a","",""]` | negative limit keeps them |
| `Integer.parseInt(" 1")` | `NumberFormatException` | no trimming |
| `Integer.parseInt("+1")` | `1` | allowed since Java 7 |
| `"a😀".length()` | `3` | surrogate pair |
| `"ß".toUpperCase()` | `"SS"` | length changes |
| `null + "a"` | `"nulla"` | `null` → `"null"` |
| `n(n+1)/2` substrings, `n = 10⁵` | ≈ 5 × 10⁹ | overflows `int` |

---

## 14. Summary

- A string is a character array with an immutable wrapper. `charAt`/`length` are `O(1)`; `substring`, concatenation, `toCharArray`, and `equals` are `O(n)`.
- Never build a string with `+=` in a loop. Use `StringBuilder` (append-only, then `reverse()` if needed), or a `char[]` for in-place work.
- `char` is a 16-bit integer: `c − 'a'`, `c − '0'`, `(char) ('a' + i)`, and case differs by 32. Watch `int` promotion in `+` and in `append`.
- **Frequency arrays** (`int[26]`, `int[128]`) solve anagram, unique-character, and palindrome-rearrangement questions in `O(n)`. Grouping needs a canonical key with separators.
- **Mappings** (isomorphic strings, word patterns) must be checked in both directions.
- **Palindromes**: two pointers; on a mismatch with one deletion allowed, try both sides. Rearrangement questions reduce to "how many odd counts".
- Use the **group loop** for runs, build digit-by-digit arithmetic from the right with a final carry, and check `atoi` overflow **before** multiplying.
- `split` and `replaceAll` take regexes, `compareTo` is by code unit (uppercase first, `"10" < "9"`), `length()` counts UTF-16 units, and hash codes collide easily.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/02 - Linear Data Structures/01 - Arrays|Arrays]] · Next: [[DSA/02 - Linear Data Structures/03 - Linked Lists|Linked Lists]]
- [[Java/03 - Program Structure/02 - Strings|Java: Strings]]: the `String` class, the pool, `StringBuilder`, formatting
- [[DSA/03 - Sorting and Searching/04 - Sliding Window|Sliding Window]]: anagram windows, longest substring without repeats, minimum window
- [[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]]: palindrome checks and in-place rewrites
- [[DSA/07 - String Algorithms/01 - String Matching|String Matching]] · [[DSA/07 - String Algorithms/02 - String Hashing|String Hashing]] · [[DSA/07 - String Algorithms/03 - Palindromes|Palindromes]]: the Part VII algorithms
- [[DSA/04 - Trees and Hierarchical Structures/05 - Tries|Tries]]: prefix queries over many strings
- [[DSA/02 - Linear Data Structures/06 - Hash Tables|Hash Tables]]: strings as keys, hash collisions
