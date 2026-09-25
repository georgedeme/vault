# Bit Manipulation

<span class="hl-blue">Bit manipulation</span> means working directly on the binary representation of integers with bitwise operators. It gives `O(1)` tricks (power-of-two tests, lowest set bit), compact set representations (a whole subset of up to 64 elements in a single `long`), and the XOR identities behind a whole family of interview problems.

It's also full of traps: two's complement, sign extension, masked shift distances, and Java's operator precedence each produce wrong-but-plausible answers. This note covers both the techniques and the traps. The language-level rules for the operators are in [[Java/Foundations/Operators#9. Bitwise and Shift Operators|Java: Operators § 9]].

## Contents

- [[#1. Binary and Two's Complement|1. Binary and Two's Complement]]
- [[#2. The Operators|2. The Operators]]
- [[#3. Single-Bit Operations|3. Single-Bit Operations]]
- [[#4. Lowest and Highest Set Bit Tricks|4. Lowest and Highest Set Bit Tricks]]
- [[#5. Counting Bits (popcount)|5. Counting Bits (popcount)]]
- [[#6. XOR and Its Properties|6. XOR and Its Properties]]
- [[#7. Bitmasks as Sets|7. Bitmasks as Sets]]
- [[#8. Arithmetic Tricks and Their Limits|8. Arithmetic Tricks and Their Limits]]
- [[#9. Java's Built-in Bit Methods|9. Java's Built-in Bit Methods]]
- [[#10. Common Mistakes|10. Common Mistakes]]
- [[#11. Trick Questions and Special Cases|11. Trick Questions and Special Cases]]
- [[#12. Quick Reference — Non-Obvious Outcomes|12. Quick Reference — Non-Obvious Outcomes]]
- [[#13. Summary|13. Summary]]

---

## 1. Binary and Two's Complement

A non-negative integer in binary: bit `i` has weight `2ⁱ`, with bit 0 (the <span class="hl-blue">least significant bit</span>, LSB) on the right. `13 = 1101₂ = 8 + 4 + 1`.

### 1.1 Two's complement

Java's `byte`, `short`, `int`, and `long` are **signed, two's complement** integers of 8, 16, 32, and 64 bits (`char` is the only unsigned one, 16 bits).

> [!note] Definition
> In <span class="hl-blue">two's complement</span> with `w` bits, the top bit (bit `w−1`, the <span class="hl-blue">sign bit</span>) has weight **`−2^(w−1)`** instead of `+2^(w−1)`. Every other bit keeps its usual positive weight.

| `int` value | Bits (32) | Notes |
|---|---|---|
| `0` | `0000…0000` | |
| `1` | `0000…0001` | |
| `-1` | `1111…1111` | all ones |
| `Integer.MAX_VALUE` = 2³¹−1 | `0111…1111` | |
| `Integer.MIN_VALUE` = −2³¹ | `1000…0000` | only the sign bit |
| `-2` | `1111…1110` | |

> [!important] The two identities everything else relies on
> - **`-x == ~x + 1`**: to negate, flip all bits and add one.
> - **`~x == -x - 1`**: so `~0 == -1`, `~5 == -6`.

> [!warning] The range is asymmetric
> There's one more negative value than positive: `int` goes from −2³¹ to 2³¹−1. So `-Integer.MIN_VALUE == Integer.MIN_VALUE` and `Math.abs(Integer.MIN_VALUE) == Integer.MIN_VALUE` (still negative). Any code that negates an arbitrary `int` has this edge case. Widen to `long` first.

### 1.2 Reading and writing binary in Java

| Task | Code | Result / note |
|---|---|---|
| Binary literal | `0b1101`, `0b1111_0000` | underscores allowed |
| Hex literal | `0xFF`, `0x8000_0000` | `0x8000_0000` is `Integer.MIN_VALUE` |
| To binary string | `Integer.toBinaryString(13)` | `"1101"`, **no leading zeros** |
| Negative to binary | `Integer.toBinaryString(-1)` | 32 ones (treated as unsigned) |
| Zero-padded | `String.format("%8s", Integer.toBinaryString(x)).replace(' ', '0')` | pad to 8 bits (for `x < 256`) |
| Parse binary | `Integer.parseInt("1101", 2)` | `13` |
| Parse 32-bit pattern | `Integer.parseUnsignedInt("1111…1111", 2)` | `-1`. `parseInt` **throws** here (value > `MAX_VALUE`) |

---

## 2. The Operators

| Operator | Name | Rule per bit | Example (`a = 1100₂`, `b = 1010₂`) |
|---|---|---|---|
| `a & b` | AND | 1 if **both** are 1 | `1000` |
| `a \| b` | OR | 1 if **either** is 1 | `1110` |
| `a ^ b` | XOR | 1 if they **differ** | `0110` |
| `~a` | NOT | flip every bit | `…11110011` (= `-13`) |
| `a << k` | left shift | move left `k`, fill with 0 | `a << 1` = `11000` = 24 |
| `a >> k` | arithmetic right shift | move right `k`, fill with **copies of the sign bit** | `-8 >> 1` = `-4` |
| `a >>> k` | logical right shift | move right `k`, fill with **0** | `-1 >>> 28` = `15` |

> [!note] Shifts as arithmetic
> - `x << k` = `x · 2ᵏ` (wrapping on overflow, exactly like `*`).
> - `x >> k` = `⌊x / 2ᵏ⌋`, rounding toward **−∞**.
> - `x / 2ᵏ` in Java rounds toward **zero**. The two differ for negative odd values: `-7 >> 1 == -4`, but `-7 / 2 == -3`.

### 2.1 Java-specific rules that break naive code

> [!warning] Shift distances are taken mod 32 (int) or mod 64 (long)
> Only the low 5 bits of the distance are used for `int` (6 for `long`). So `1 << 32 == 1`, `1 << 33 == 2`, and **`1 << 40 == 256`**, not 2⁴⁰. Also `x >> 32 == x`, not 0. For bits ≥ 31 you need a `long` **literal**: `1L << 40`. Assigning to a `long` doesn't help: `long m = 1 << 40;` is still 256, because the shift is computed in `int` first.

> [!warning] `byte`/`short`/`char` are promoted to `int` first
> ```java
> byte b = (byte) 0xF0;        // -16
> int r = b >>> 4;             // 0x0FFFFFFF = 268435455, not 0x0F
> int ok = (b & 0xFF) >>> 4;   // 0x0F = 15
> ```
> `b` is sign-extended to `0xFFFFFFF0` before the shift. Mask with `& 0xFF` to treat a byte as unsigned. Details in [[Java/Foundations/Operators#9.2 `>>>` on `byte` / `short` Doesn't Do What You'd Expect|Operators § 9.2]].

> [!warning] Precedence: bitwise operators bind *looser* than `==`
> From highest to lowest: `~` → `* / %` → `+ -` → `<< >> >>>` → `< > <= >=` → `== !=` → `&` → `^` → `|` → `&&` → `||`.
> - `x & 1 == 0` parses as `x & (1 == 0)`, which is a **compile error** in Java (`int & boolean`). In C it silently compiles to the wrong thing.
> - `(x & mask) != 0` always needs the parentheses.
> - `a + b << 1` is `(a + b) << 1`, not `a + (b << 1)`.
> - `1 << n - 1` is `1 << (n − 1)`.
>
> **Rule: parenthesise every bitwise sub-expression.**

> [!info]- `&` and `|` on booleans don't short-circuit
> On `boolean` operands, `&` and `|` are logical operators that **always evaluate both sides**. `if (i < n & a[i] > 0)` still evaluates `a[i]` when `i == n` → `ArrayIndexOutOfBoundsException`. Use `&&` / `||` for conditions. `^` on booleans is logical XOR ("exactly one is true"), which is occasionally handy.

---

## 3. Single-Bit Operations

Bits are numbered from 0 at the LSB. `1 << i` is a <span class="hl-blue">mask</span> with only bit `i` set.

| Operation | Pseudocode | Java (`int`) |
|---|---|---|
| Test bit `i` | `(x >> i) AND 1` | `((x >> i) & 1) == 1` or `(x & (1 << i)) != 0` |
| Set bit `i` to 1 | `x OR (1 << i)` | `x \| (1 << i)` |
| Clear bit `i` to 0 | `x AND NOT(1 << i)` | `x & ~(1 << i)` |
| Toggle bit `i` | `x XOR (1 << i)` | `x ^ (1 << i)` |
| Set bit `i` to `v` ∈ {0,1} | clear, then OR in `v << i` | `(x & ~(1 << i)) \| (v << i)` |
| Lowest `k` bits mask | `(1 << k) − 1` | `(1 << k) - 1` (for `k ≤ 31`) |
| Keep only lowest `k` bits | `x AND ((1 << k) − 1)` | `x & ((1 << k) - 1)` |

```java
static boolean testBit(int x, int i)  { return ((x >> i) & 1) == 1; }
static int setBit(int x, int i)       { return x | (1 << i); }
static int clearBit(int x, int i)     { return x & ~(1 << i); }
static int toggleBit(int x, int i)    { return x ^ (1 << i); }
```

> [!warning] Testing bit 31
> `(x & (1 << 31)) > 0` is **always false**: `1 << 31` is `Integer.MIN_VALUE`, so a set bit 31 gives a *negative* result. Compare with `!= 0`, never `> 0`. `((x >> i) & 1) == 1` works for every `i` from 0 to 31.

> [!tip] Low-`k`-bits mask for `k = 32`
> `(1 << 32) - 1` is `0` (the distance wraps to 0, so it's `1 − 1`), not all ones. Use `-1 >>> (32 - k)` for `1 ≤ k ≤ 32`, or special-case `k = 32`.

---

## 4. Lowest and Highest Set Bit Tricks

Subtracting 1 from `x` flips its lowest set bit to 0 and every bit below it to 1. Negating (`~x + 1`) flips all bits above the lowest set bit and keeps that bit itself. The tricks below all follow from these two facts.

| Expression | Effect | `x = 0101 1000` |
|---|---|---|
| `x & (x − 1)` | **clear** the lowest set bit | `0101 0000` |
| `x & −x` | **isolate** the lowest set bit | `0000 1000` |
| `x \| (x − 1)` | set all bits below the lowest set bit | `0101 1111` |
| `x \| (x + 1)` | set the lowest **unset** bit | `0101 1001` |
| `x & (x + 1)` | clear the trailing ones | (no trailing ones) `0101 1000` |
| `~x & (x + 1)` | isolate the lowest **unset** bit | `0000 0001` |

> [!example]- Why `x & (x − 1)` clears the lowest set bit
> ```
> x      = 0101 1000
> x − 1  = 0101 0111     ← the lowest 1 became 0, the zeros below it became 1s
> x & (x−1) = 0101 0000  ← bits above are unchanged; the rest cancel
> ```
> And `x & −x`:
> ```
> x      = 0101 1000
> ~x     = 1010 0111
> −x = ~x + 1 = 1010 1000   ← +1 ripples up to exactly the lowest set bit of x
> x & −x = 0000 1000
> ```

### 4.1 Power-of-two tests

A power of two has **exactly one** set bit, so clearing its lowest set bit leaves 0:

```
isPowerOfTwo(x):
    return x > 0 AND (x AND (x − 1)) == 0
```

```java
static boolean isPowerOfTwo(int x) {
    return x > 0 && (x & (x - 1)) == 0;
}

static boolean isPowerOfFour(int x) {
    // one set bit, and it's in an even position: 0x55555555 = 0101…0101
    return x > 0 && (x & (x - 1)) == 0 && (x & 0x55555555) != 0;
}
```

> [!warning] The `x > 0` is not optional
> Without it, `0` passes (`0 & −1 == 0`), and so does `Integer.MIN_VALUE` (`0x80000000 & 0x7FFFFFFF == 0`): it has one set bit, but it's the sign bit.

### 4.2 Highest set bit, ⌊log₂ x⌋, next power of two

| Want | Java | Notes |
|---|---|---|
| Highest set bit as a value | `Integer.highestOneBit(x)` | `highestOneBit(0) == 0` |
| Its index = `⌊log₂ x⌋` | `31 - Integer.numberOfLeadingZeros(x)` | gives `-1` for `x = 0` |
| Number of bits needed for `x` | `32 - Integer.numberOfLeadingZeros(x)` | `0` for `x = 0` |
| Smallest power of two `≥ x` (`1 ≤ x ≤ 2³⁰`) | `1 << (32 - Integer.numberOfLeadingZeros(x - 1))` | `x = 1` → `1`; `x = 5` → `8`; `x = 8` → `8` |
| Is `x` a power of two | `Integer.bitCount(x) == 1` | also correctly rejects `0`; `MIN_VALUE` has bitCount 1, so add `x > 0` |

> [!tip] Prefer integer `log₂` over `Math.log`
> `(int) (Math.log(x) / Math.log(2))` goes through floating point. It happens to come out right for `int` powers of two, but the pattern isn't safe:
> - the same idea in base 10 gives `(int) (Math.log(1000) / Math.log(10)) == 2`, because the quotient is `2.9999999999999996`;
> - for a `long` above 2⁵³, converting to `double` rounds. For `x = (1L << 60) - 1` it gives `60` instead of `59`.
>
> `31 - Integer.numberOfLeadingZeros(x)` (or `63 - Long.numberOfLeadingZeros(x)`) is exact and a single instruction.

These tricks are the core of [[DSA/Fenwick Trees|Fenwick trees]] (`i & −i`), sparse tables (`⌊log₂⌋` lookups), and iterating over set bits (§7.3).

---

## 5. Counting Bits (popcount)

The <span class="hl-blue">population count</span> (popcount) of `x` is its number of set bits.

### 5.1 Brian Kernighan's algorithm

Clear the lowest set bit until nothing is left. The loop runs once **per set bit**, not once per bit position.

```
popcount(x):
    count = 0
    while x ≠ 0:
        x = x AND (x − 1)
        count = count + 1
    return count
```

```java
static int popcount(int x) {
    int count = 0;
    while (x != 0) {           // != 0, not > 0: negative numbers have bits too
        x &= x - 1;
        count++;
    }
    return count;
}
```

In practice, use **`Integer.bitCount(x)`** / **`Long.bitCount(x)`**. The JIT compiles them to a single `POPCNT` instruction where the CPU supports it.

> [!warning] The naive shift loop hangs on negative input
> ```java
> while (x != 0) { count += x & 1; x >>= 1; }   // infinite loop for x < 0
> ```
> `>>` copies the sign bit in, so `-1 >> 1 == -1` forever. Use `>>>`. The version with `while (x > 0)` is wrong in a different way: it returns 0 for every negative number.

### 5.2 Counting bits for every number 0…n in O(n)

`i >> 1` is smaller than `i` and has the same bits except the last one:

```
bits[0] = 0
for i = 1 to n:
    bits[i] = bits[i >> 1] + (i AND 1)
```

```java
static int[] countBits(int n) {
    int[] bits = new int[n + 1];
    for (int i = 1; i <= n; i++) bits[i] = bits[i >> 1] + (i & 1);
    return bits;
}
```

(Equivalently `bits[i] = bits[i & (i − 1)] + 1`, which removes the lowest set bit instead.)

> [!info]- Parity
> The <span class="hl-blue">parity</span> of `x` is `popcount(x) mod 2` = `Integer.bitCount(x) & 1`. It's also the XOR of all bits, which you can compute by folding: `x ^= x >>> 16; x ^= x >>> 8; x ^= x >>> 4; x ^= x >>> 2; x ^= x >>> 1; return x & 1;`

---

## 6. XOR and Its Properties

> [!important] XOR identities
> | Property | Statement |
> |---|---|
> | Identity | `a ^ 0 = a` |
> | Self-inverse | `a ^ a = 0` |
> | Commutative | `a ^ b = b ^ a` |
> | Associative | `(a ^ b) ^ c = a ^ (b ^ c)` |
> | Cancels | `a ^ b ^ a = b`, so `x = a ^ b ⟺ a = x ^ b` |
> | Complement | `a ^ ~0 = ~a` (`a ^ -1` flips every bit) |
> | Addition without carry | `a + b = (a ^ b) + 2·(a & b)` |
>
> Together: XOR-ing a multiset of values, in any order, leaves exactly the values that appear an **odd** number of times, combined.

### 6.1 Single number: everything appears twice except one

```
single(a):
    x = 0
    for v in a: x = x XOR v
    return x                         -- pairs cancel, the loner survives
```

```java
static int singleNumber(int[] a) {
    int x = 0;
    for (int v : a) x ^= v;
    return x;
}
```

`Θ(n)` time, `Θ(1)` space, which beats a `HashSet`'s `Θ(n)` space.

### 6.2 Two numbers appear once, the rest twice

XOR everything to get `d = p ^ q`. Since `p ≠ q`, `d ≠ 0`, so it has some set bit, and `p` and `q` differ in it. Split all values by that bit: each group contains exactly one of `p`, `q`, and the pairs stay together.

```
twoSingles(a):
    d = XOR of all a
    bit = d AND (−d)                 -- any set bit works; the lowest is easy
    p = 0
    for v in a: if v AND bit ≠ 0: p = p XOR v
    return (p, d XOR p)
```

```java
static int[] twoSingles(int[] a) {
    int d = 0;
    for (int v : a) d ^= v;
    int bit = d & -d;                // fine even if d == Integer.MIN_VALUE
    int p = 0;
    for (int v : a) if ((v & bit) != 0) p ^= v;
    return new int[]{p, d ^ p};
}
```

### 6.3 Every number appears three times except one

XOR doesn't help, because three copies XOR to the value itself. Count each bit position **mod 3**:

```
for each bit b in 0..31:
    cnt = number of values with bit b set
    if cnt mod 3 ≠ 0: set bit b in the answer
```

```java
static int singleAmongTriples(int[] a) {
    int result = 0;
    for (int b = 0; b < 32; b++) {
        int cnt = 0;
        for (int v : a) cnt += (v >>> b) & 1;
        if (cnt % 3 != 0) result |= 1 << b;   // b = 31 correctly rebuilds negative answers
    }
    return result;
}
```

This generalises to "every value appears `k` times except one" by counting mod `k`.

### 6.4 Missing number in 0…n

`n` distinct values from `0…n`, one missing. XOR all indices `0…n` with all values; everything present cancels.

```java
static int missingNumber(int[] a) {       // a has length n, values in 0..n
    int x = a.length;                     // start with n itself
    for (int i = 0; i < a.length; i++) x ^= i ^ a[i];
    return x;
}
```

The sum formula `n(n+1)/2 − Σa` also works, but it can overflow `int` for large `n`. XOR can't overflow.

### 6.5 XOR of 1…n in O(1) and range XOR

`1 ^ 2 ^ … ^ n` repeats with period 4:

| `n mod 4` | `0` | `1` | `2` | `3` |
|---|---|---|---|---|
| `1 ^ … ^ n` | `n` | `1` | `n + 1` | `0` |

```java
static long xorUpTo(long n) {             // XOR of 0..n (0 changes nothing)
    switch ((int) (n & 3)) {
        case 0:  return n;
        case 1:  return 1;
        case 2:  return n + 1;
        default: return 0;
    }
}
// XOR of l..r = xorUpTo(r) ^ xorUpTo(l - 1)
```

The same **prefix-XOR** idea works on arrays: with `px[i] = a[0] ^ … ^ a[i−1]`, the XOR of `a[l..r]` is `px[r+1] ^ px[l]`, just like prefix sums ([[DSA/Prefix Sums and Difference Arrays|Prefix Sums]]).

### 6.6 Swap without a temporary, and why not to

```java
a ^= b;  b ^= a;  a ^= b;    // swaps a and b
```

> [!warning] The aliasing bug
> On array elements, `arr[i] ^= arr[j]; arr[j] ^= arr[i]; arr[i] ^= arr[j];` **zeroes** the element when `i == j`: the first line computes `x ^ x = 0`, and it's the same memory. A temporary variable is just as fast on modern hardware and has no such case. The XOR swap is an interview curiosity, not a technique.

### 6.7 Gray code

In the <span class="hl-blue">Gray code</span> sequence, consecutive values differ in exactly one bit. The `i`-th Gray code is `i ^ (i >> 1)`.

```java
static int gray(int i) { return i ^ (i >> 1); }

static int fromGray(int g) {              // inverse: prefix XOR of the bits from the top
    int b = 0;
    for (; g != 0; g >>>= 1) b ^= g;
    return b;
}
```

For `n = 3`: `000, 001, 011, 010, 110, 111, 101, 100`. The last and first also differ in one bit, so the sequence is cyclic.

> [!info]- Maximum XOR of two numbers
> "Find the maximum `a[i] ^ a[j]`" is solved greedily bit by bit, from the highest bit down, with a binary trie. That's `O(n · 32)`. See [[DSA/Tries|Tries]].

---

## 7. Bitmasks as Sets

With a universe `{0, 1, …, n−1}` for `n ≤ 32` (`int`) or `n ≤ 64` (`long`), a subset is a single integer: bit `i` is set ⟺ element `i` is in the set. Every set operation becomes one instruction.

| Set operation | Bitmask | Java |
|---|---|---|
| Empty set | `0` | `0` |
| Full set `{0..n−1}` | `2ⁿ − 1` | `(1 << n) - 1` |
| `{i}` | `1 << i` | `1 << i` |
| `i ∈ A` | bit `i` of `A` | `((A >> i) & 1) == 1` |
| `A ∪ {i}` / `A \ {i}` | set / clear bit | `A \| (1 << i)` / `A & ~(1 << i)` |
| `A ∪ B` | OR | `A \| B` |
| `A ∩ B` | AND | `A & B` |
| `A \ B` | AND NOT | `A & ~B` |
| Symmetric difference | XOR | `A ^ B` |
| Complement within `{0..n−1}` | XOR with full | `A ^ ((1 << n) - 1)` |
| `A ⊆ B` | `A ∩ B = A` | `(A & B) == A` |
| Size of `A` | popcount | `Integer.bitCount(A)` |
| Smallest element | lowest set bit | `Integer.numberOfTrailingZeros(A)` |

> [!warning] `~A` is not the complement of the set
> `~A` also sets bits `n…31`, which aren't in the universe, so it isn't a valid set. Use `A ^ full` or `~A & full`.

### 7.1 Enumerating all subsets

```
for mask = 0 to 2ⁿ − 1:
    for i = 0 to n − 1:
        if bit i of mask is set: element i is in this subset
```

```java
static List<List<Integer>> allSubsets(int[] a) {
    int n = a.length;                       // n ≤ 30 for this int loop
    List<List<Integer>> res = new ArrayList<>();
    for (int mask = 0; mask < (1 << n); mask++) {
        List<Integer> s = new ArrayList<>();
        for (int i = 0; i < n; i++)
            if (((mask >> i) & 1) == 1) s.add(a[i]);
        res.add(s);
    }
    return res;
}
```

`Θ(n · 2ⁿ)`, the same as the recursive version in [[DSA/Foundations/Recursion#6.3 Generating all subsets (include / exclude)|Recursion § 6.3]], with no recursion depth. The loop orders subsets by their binary value, which is useful because every proper subset of `mask` is **numerically smaller** than `mask`. Bitmask DP relies on exactly this: iterating masks in increasing order means every subset has already been processed.

> [!warning] `n = 31` and `n ≥ 32`
> `1 << 31` is negative, so `mask < (1 << 31)` is false immediately and the loop runs **zero** times. For `n ≥ 32` the shift wraps. Use `long` and `1L << n` past 30. At `2³¹` subsets the enumeration is too slow anyway; the usual limit is `n ≤ 20–25` (see [[DSA/Foundations/Complexity Analysis#12. From Constraints to Target Complexity|Complexity § 12]]).

### 7.2 Enumerating the submasks of a mask

To visit every subset `s ⊆ m`, including `m` and `∅`:

```
s = m
loop:
    process(s)
    if s == 0: break
    s = (s − 1) AND m          -- next smaller submask
```

```java
static void forEachSubmask(int m, java.util.function.IntConsumer process) {
    for (int s = m; ; s = (s - 1) & m) {
        process.accept(s);
        if (s == 0) break;
    }
}
```

`s − 1` clears the lowest set bit of `s` and sets everything below it; `& m` keeps only the bits allowed in `m`. The result is the next submask in decreasing order.

> [!important] Submasks of all masks cost 3ⁿ, not 4ⁿ
> Enumerating the submasks of **every** mask of `n` bits takes `Σ 2^popcount(m) = 3ⁿ` steps in total: each element is independently in `s`, in `m \ s`, or in neither. At `n = 15` that's ~1.4 × 10⁷, which is fine; `4ⁿ` would be ~10⁹. Used in subset-partition DP. See [[DSA/Advanced DP|Advanced DP]].

> [!warning] The loop condition trap
> `for (s = m; s > 0; s = (s - 1) & m)` **skips the empty set**. That's fine if you meant non-empty submasks; otherwise it's a silent off-by-one. With `m = 0` the version above processes `0` exactly once.

### 7.3 Iterating over the set bits only

```java
for (int m = mask; m != 0; m &= m - 1) {
    int i = Integer.numberOfTrailingZeros(m);   // index of the lowest set bit
    // ... element i is in the set
}
```

This costs `popcount(mask)` iterations, not `n`.

### 7.4 Masks with exactly k bits (Gosper's hack) *(advanced)*

Given a mask `x` with `k` bits, this gives the next larger mask with `k` bits:

```java
static int nextSameBitCount(int x) {
    int c = x & -x;                  // lowest set bit
    int r = x + c;                   // ripple: clear the lowest run of 1s, set the bit above it
    return (((r ^ x) >>> 2) / c) | r; // move the remaining 1s back down to the bottom
}
// all k-subsets of n: for (int x = (1 << k) - 1; x < (1 << n); x = nextSameBitCount(x)) ...
```

Needs `k ≥ 1`.

### 7.5 Common mask applications

- **Set of letters in a word**: `mask |= 1 << (c - 'a')`. Two words share no letter ⟺ `(m1 & m2) == 0`.
- **Visited-set in a state**: a BFS state `(node, mask of keys collected)`, or a TSP DP state `(mask of visited cities, last city)`. See [[DSA/Advanced DP|Advanced DP]].
- **Rows of a board** (N-queens): columns and both diagonals as masks, where the free positions are `~(cols | d1 | d2) & full`.
- **Large boolean arrays**: `java.util.BitSet`, or a `long[]` used as a bitset, packs 64 flags per word. That makes some `O(n²)` algorithms 64× faster. Java's `BitSet` has no shift operation, so subset-sum-by-shifting needs a hand-rolled `long[]`.

---

## 8. Arithmetic Tricks and Their Limits

| Trick | Works when | Trap |
|---|---|---|
| `x & 1` is 1 ⟺ `x` is odd | **all** `x` (including negatives) | `x % 2 == 1` is **false** for negative odd `x` (`-3 % 2 == -1`) |
| `x << k` = `x · 2ᵏ` | always (wraps like `*`) | overflow is silent |
| `x >> k` = `x / 2ᵏ` | `x ≥ 0` | for negative `x`, `>>` rounds down, `/` rounds toward 0 |
| `x & (m − 1)` = `x mod m` for `m = 2ᵏ` | always, and it equals `Math.floorMod(x, m)` | for negative `x` it differs from `x % m`: `-1 & 7 == 7`, `-1 % 8 == -1` |
| `(lo + hi) >>> 1` = midpoint | `lo, hi ≥ 0` | the `lo + hi` overflow is undone by the unsigned shift; `(lo + hi) / 2` breaks for large indices |
| `(a & b) + ((a ^ b) >> 1)` = `⌊(a+b)/2⌋` | any `int`s | never overflows |
| `(a ^ b) < 0` ⟺ opposite signs | any `int`s | treats `0` as positive |
| `x >> 31` | any `int` | `-1` if negative, `0` otherwise: a branch-free sign mask |
| `(x ^ (x >> 31)) - (x >> 31)` = `Math.abs(x)` | `x ≠ MIN_VALUE` | same asymmetry as `Math.abs` |
| `c ^ 32` toggles ASCII letter case | `c` is a letter `A–Z`/`a–z` | `'a' ^ 32 == 'A'`; also changes non-letters (`'['` ↔ `'{'`). Result is an `int`, so cast back to `char` |
| `c \| 32` / `c & ~32` | ASCII letters | force lowercase / uppercase |

### 8.1 Reversing bits

```
reverse(x):                          -- 32-bit
    r = 0
    repeat 32 times:
        r = (r << 1) OR (x AND 1)    -- append x's lowest bit to r
        x = x >>> 1
    return r
```

```java
static int reverseBits(int x) {
    int r = 0;
    for (int i = 0; i < 32; i++) {
        r = (r << 1) | (x & 1);
        x >>>= 1;
    }
    return r;                        // same as Integer.reverse(x)
}
```

> [!tip] Unsigned problems in a signed language
> LeetCode-style "treat this as an unsigned 32-bit integer" problems work with Java's `int` unchanged. The bit pattern is identical; only printing and comparison differ. Use `Integer.toUnsignedString`, `Integer.toUnsignedLong(x)` (`x & 0xFFFFFFFFL`), `Integer.compareUnsigned`, `Integer.divideUnsigned`.

### 8.2 Adding without `+`

```java
static int add(int a, int b) {
    while (b != 0) {
        int carry = (a & b) << 1;    // positions that generate a carry
        a = a ^ b;                   // sum without carries
        b = carry;
    }
    return a;
}
```

This terminates for negative numbers too in Java, because the carry is shifted left each round and falls off after at most 32 iterations. (In Python it would loop forever, since integers there are unbounded.)

---

## 9. Java's Built-in Bit Methods

All exist on both `Integer` and `Long`, run in `O(1)`, and most compile to a single CPU instruction.

| Method | Returns | Value at `0` |
|---|---|---|
| `bitCount(x)` | number of set bits | `0` |
| `highestOneBit(x)` | `x` with only its highest set bit kept | `0` |
| `lowestOneBit(x)` | `x & -x` | `0` |
| `numberOfLeadingZeros(x)` | zeros above the highest set bit | `32` (`64` for `Long`) |
| `numberOfTrailingZeros(x)` | zeros below the lowest set bit = index of lowest set bit | `32` (`64`) |
| `reverse(x)` | bits in reverse order | `0` |
| `reverseBytes(x)` | bytes in reverse order (endianness swap) | `0` |
| `rotateLeft(x, k)` / `rotateRight(x, k)` | cyclic shift | `0` |
| `signum(x)` | `-1`, `0`, or `1` | `0` |
| `toBinaryString(x)` / `toHexString(x)` | unsigned representation | `"0"` |

> [!warning] The zero cases
> `numberOfTrailingZeros(0)` returns 32, which is not a valid bit index. Code like `a[Integer.numberOfTrailingZeros(mask)]` throws on an empty mask. Similarly, `31 - numberOfLeadingZeros(0)` is `-1`.

---

## 10. Common Mistakes

| Mistake | What happens | Fix |
|---|---|---|
| `1 << i` with `i ≥ 32` | wraps: `1 << 40 == 256` | `1L << i` |
| `long m = 1 << 40;` | still 256 | the literal must be `1L` |
| `(x & (1 << 31)) > 0` | always false | `!= 0` |
| `x & 1 == 0` | compile error | `(x & 1) == 0` |
| `x % 2 == 1` for oddness | fails on negatives | `(x & 1) == 1` or `x % 2 != 0` |
| `x >> 1` in a popcount loop | infinite loop for `x < 0` | `>>>` |
| `(x & (x-1)) == 0` alone | accepts `0` and `MIN_VALUE` | add `x > 0` |
| `~mask` as set complement | sets bits outside the universe | `mask ^ full` |
| `byte b; b >>> 4` | sign-extended first | `(b & 0xFF) >>> 4` |
| XOR swap on `arr[i]`, `arr[j]` with `i == j` | element becomes 0 | use a temp |
| `mask < (1 << n)` with `n = 31` | loop never runs | `long` and `1L << n` |
| Submask loop with `s > 0` | skips `∅` | process then `if (s == 0) break` |
| `Integer.parseInt(32-bit string, 2)` | `NumberFormatException` | `parseUnsignedInt` |

---

## 11. Trick Questions and Special Cases

> [!question]- What is `1 << 32` in Java? And `1L << 64`?
> `1` and `1L`. The shift distance is masked to its low 5 bits for `int` (low 6 for `long`), so `32 → 0` and `64 → 0`. It's **not** 0, as you might expect from "shifting everything out".

> [!question]- What is `-7 >> 1`, `-7 / 2`, and `-7 >>> 1`?
> `-4`, `-3`, and `2147483644`. `>>` is floor division by 2; `/` truncates toward zero; `>>>` shifts in a zero, turning the number into a huge positive.

> [!question]- Is `0` a power of two by the `(x & (x-1)) == 0` test? Is `Integer.MIN_VALUE`?
> Both pass the bit test, but neither is a (positive) power of two. `0 & -1 == 0`; `MIN_VALUE` has a single set bit, the sign bit. The complete test is `x > 0 && (x & (x - 1)) == 0`.

> [!question]- What is `Integer.MIN_VALUE & -Integer.MIN_VALUE`?
> `Integer.MIN_VALUE`, since `-MIN_VALUE == MIN_VALUE`. The lowest set bit of `MIN_VALUE` is bit 31 itself, so the trick still gives the right *bit pattern*, just a negative value.

> [!question]- Does `x & (m - 1)` compute `x % m` for m a power of two?
> For `x ≥ 0`, yes. For negative `x` it gives the **non-negative** remainder, like `Math.floorMod`: `-3 & 7 == 5`, while `-3 % 8 == -3`. That's often what you actually want (e.g. circular buffer indices), but it isn't `%`.

> [!question]- Two numbers appear once, the rest twice — what if the XOR of the two is `Integer.MIN_VALUE`?
> Nothing breaks. `d & -d == MIN_VALUE` isolates bit 31, and the partition test `(v & bit) != 0` works correctly. (A test written as `(v & bit) > 0` would fail here.)

> [!question]- Why does `x ^ y ^ x` give `y` even with overflow-prone values?
> XOR works bit by bit with no carries, so there's no overflow at all. That's why the XOR form of "missing number" is safer than the sum formula.

> [!question]- What does `(char) ('a' ^ ' ')` give? And `'5' ^ ' '`?
> `'A'`: the space character is 32, the bit that separates ASCII upper and lower case. `'5' ^ ' '` is `21`, a control character. The trick only makes sense on letters.

> [!question]- How many iterations does `for (s = m; s > 0; s = (s-1) & m)` run for `m = 0b1011`?
> 7: all non-empty submasks (`2³ − 1`). The empty set is skipped by the `s > 0` condition.

> [!question]- Is `Integer.bitCount(x) == 1` a correct power-of-two test?
> Not quite: it accepts `Integer.MIN_VALUE`. For positive `x` it's correct, so add `x > 0`.

> [!question]- `x` is an `int`; what's `x >>> 32`? What's `x >>> 31`?
> `x >>> 32 == x` (distance masked to 0). `x >>> 31` is `1` if `x` is negative, `0` otherwise, which is a common way to extract the sign bit.

> [!question]- Can `a + b == (a ^ b) + 2 * (a & b)` overflow when `a + b` doesn't?
> In Java both sides wrap mod 2³² and are always equal, so it holds for every `int`. The identity is exact modular arithmetic, not an approximation.

> [!question]- Is `x << 1` always the same as `x * 2`?
> Yes, including overflow: both wrap identically in two's complement. `x >> 1` vs `x / 2` is where they differ (negative odd numbers).

---

## 12. Quick Reference — Non-Obvious Outcomes

| Expression | Value / meaning |
|---|---|
| `~x` | `-x - 1` |
| `-x` | `~x + 1` |
| `x & (x - 1)` | clear lowest set bit |
| `x & -x` | lowest set bit (as a value) |
| `x \| (x + 1)` | set lowest unset bit |
| `x > 0 && (x & (x-1)) == 0` | power of two |
| `31 - Integer.numberOfLeadingZeros(x)` | `⌊log₂ x⌋` (`-1` for 0) |
| `1 << (32 - nlz(x - 1))` | next power of two `≥ x` |
| `1 << 40` | `256` |
| `1 << 31` | `Integer.MIN_VALUE` |
| `-7 >> 1` / `-7 / 2` | `-4` / `-3` |
| `-1 >>> 28` | `15` |
| `(byte) 0xF0 >>> 4` | `268435455` |
| `-3 & 7` / `-3 % 8` | `5` / `-3` |
| `bits[i] = bits[i>>1] + (i&1)` | popcount of 0..n in `O(n)` |
| XOR `1..n` | `n, 1, n+1, 0` for `n mod 4 = 0,1,2,3` |
| `i ^ (i >> 1)` | `i`-th Gray code |
| `s = (s - 1) & m` | next submask of `m` |
| All submasks of all `n`-bit masks | `3ⁿ` total |
| `Integer.numberOfTrailingZeros(0)` | `32` |
| `Math.abs(Integer.MIN_VALUE)` | `Integer.MIN_VALUE` |

---

## 13. Summary

- Java integers are **two's complement**: `-x == ~x + 1`, the range is asymmetric, and `MIN_VALUE` is its own negation.
- `>>` keeps the sign (floor division by 2ᵏ); `>>>` fills with zeros. Shift distances are **mod 32/64**, so write `1L << i` for high bits.
- **Parenthesise** every bitwise sub-expression: `&`, `^`, `|` bind more loosely than `==`.
- `x & (x−1)` clears and `x & −x` isolates the lowest set bit. These give the power-of-two test (with `x > 0`), Kernighan popcount, and set-bit iteration.
- **XOR** is its own inverse and order-independent, so pairs cancel. That solves single-number, two-singles, missing-number, and range-XOR problems in `O(1)` space.
- A `long` is a **set of up to 64 elements**. Enumerate all subsets with `0…2ⁿ−1`, submasks with `s = (s−1) & m` (total `3ⁿ`), and set bits with `m &= m−1`.
- Prefer `Integer`/`Long` built-ins (`bitCount`, `numberOfTrailingZeros`, `highestOneBit`), and remember their zero cases.

## Related

- [[DSA/Syllabus|Syllabus]]
- Previous: [[DSA/Foundations/Recursion|Recursion]] · Next: [[DSA/Foundations/Math for Algorithms|Math for Algorithms]]
- [[Java/Foundations/Operators#9. Bitwise and Shift Operators|Java: Operators § 9]]: operator semantics, masked shifts, precedence
- [[Java/Foundations/Type Casting#2. Narrowing Between Integer Types — Overflow and Wraparound|Java: Type Casting § 2]]: wraparound and narrowing
- [[DSA/Fenwick Trees|Fenwick Trees]]: built on `i & −i`
- [[DSA/Tries|Tries]]: bitwise trie for maximum XOR
- [[DSA/Advanced DP|Advanced DP]]: bitmask DP and DP over subsets
- [[DSA/Backtracking|Backtracking]]: N-queens with masks
