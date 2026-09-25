# Math for Algorithms

This note covers the number theory and combinatorics that algorithm problems keep coming back to: **GCD/LCM**, **modular arithmetic**, **fast exponentiation**, **modular inverses**, **primes and factorization**, **Euler's totient**, **binomial coefficients**, and the **Chinese Remainder Theorem**. Every one of them has a Java-specific failure mode, usually overflow or the sign of `%`, so those get as much attention as the math.

The companion topics are [[DSA/Foundations/Bit Manipulation|Bit Manipulation]] (fast exponentiation walks the bits of the exponent) and [[DSA/Matrix Exponentiation|Matrix Exponentiation]] (the same algorithm on matrices).

## Contents

- [[#1. Integer Arithmetic in Java — The Ground Rules|1. Integer Arithmetic in Java — The Ground Rules]]
- [[#2. GCD, LCM, and Euclid's Algorithm|2. GCD, LCM, and Euclid's Algorithm]]
- [[#3. Modular Arithmetic|3. Modular Arithmetic]]
- [[#4. Fast (Binary) Exponentiation|4. Fast (Binary) Exponentiation]]
- [[#5. Modular Inverse|5. Modular Inverse]]
- [[#6. Primes and the Sieve of Eratosthenes|6. Primes and the Sieve of Eratosthenes]]
- [[#7. Prime Factorization and Divisors|7. Prime Factorization and Divisors]]
- [[#8. Euler's Totient Function|8. Euler's Totient Function]]
- [[#9. Combinatorics|9. Combinatorics]]
- [[#10. Chinese Remainder Theorem (advanced)|10. Chinese Remainder Theorem (advanced)]]
- [[#11. Useful Formulas and Utilities|11. Useful Formulas and Utilities]]
- [[#12. Common Mistakes|12. Common Mistakes]]
- [[#13. Trick Questions and Special Cases|13. Trick Questions and Special Cases]]
- [[#14. Quick Reference — Non-Obvious Outcomes|14. Quick Reference — Non-Obvious Outcomes]]
- [[#15. Summary|15. Summary]]

---

## 1. Integer Arithmetic in Java — The Ground Rules

### 1.1 Ranges and overflow

| Type | Range | Roughly |
|---|---|---|
| `int` | −2³¹ … 2³¹ − 1 | ±2.1 × 10⁹ |
| `long` | −2⁶³ … 2⁶³ − 1 | ±9.2 × 10¹⁸ |

Overflow is **silent**: the result wraps around modulo 2³² or 2⁶⁴ with no exception (details in [[Java/Foundations/Operators#4. Integer Overflow|Operators § 4]]).

> [!warning] Cast *before* multiplying
> ```java
> int a = 100_000, b = 100_000;
> long wrong = a * b;           // 1410065408: multiplied in int, THEN widened
> long wrong2 = (long) (a * b); // same thing, the cast comes too late
> long right = (long) a * b;    // 10000000000
> ```
> The type of `a * b` is decided by the operands, not by the variable it's assigned to. <span class="hl-yellow">If a product of two values up to 10⁵ or more is possible, at least one operand must be `long` before the `*`.</span>

Limits worth knowing: `12!` is the largest factorial that fits in `int`, `20!` the largest in `long`. `C(66, 33)` fits in `long`; `C(67, 33)` doesn't. `fib(46)` / `fib(92)` are the last Fibonacci numbers that fit in `int` / `long`.

`Math.addExact`, `Math.multiplyExact`, and `Math.toIntExact` throw `ArithmeticException` on overflow instead of wrapping. They're useful for debugging, or for detecting "the answer exceeds the limit". For truly big values use `BigInteger`, at a large constant-factor cost.

### 1.2 Division and remainder

| Expression | Value | Rule |
|---|---|---|
| `7 / 2` | `3` | truncates toward zero |
| `-7 / 2` | `-3` | toward zero, **not** `-4` |
| `-7 % 3` | `-1` | the sign of `%` follows the **dividend** |
| `7 % -3` | `1` | |
| `Math.floorDiv(-7, 2)` | `-4` | rounds toward −∞ |
| `Math.floorMod(-7, 3)` | `2` | always in `[0, m)` for `m > 0` |
| `Integer.MIN_VALUE / -1` | `Integer.MIN_VALUE` | the one division that overflows (no exception) |

> [!important] Ceiling division
> For `a ≥ 0`, `b > 0`: **`⌈a / b⌉ = (a + b − 1) / b`**. The `a + b − 1` can overflow when `a` is near the maximum; `a / b + (a % b != 0 ? 1 : 0)` can't. For negative operands use `-Math.floorDiv(-a, b)` (Java 18+ has `Math.ceilDiv`).

### 1.3 Floating point is not a shortcut

- `Math.pow` returns a `double`, and a `double` has only 53 bits of precision. `(long) Math.pow(3, 35)` is `50031545098999704`, but `3³⁵ = 50031545098999707`. **Never use `Math.pow` for exact integer powers.** Use a loop or fast exponentiation (§4).
- `Math.sqrt(n)` on a `long` near 10¹⁸ can be off by one: `(long) Math.sqrt(999_999_999_999_999_999L)` is `1_000_000_000`, whose square exceeds `n`. Correct it with a fix-up loop (§11.2).
- `(int) Math.log10(n) + 1` for the digit count gives **19** for `999_999_999_999_999_999L` (18 digits), because the conversion to `double` rounds `n` up to 10¹⁸. It also fails for `n = 0`. Use `Long.toString(n).length()` or a loop.

---

## 2. GCD, LCM, and Euclid's Algorithm

> [!note] Definitions
> - <span class="hl-blue">`gcd(a, b)`</span>: the largest integer dividing both `a` and `b`. By convention `gcd(a, 0) = |a|` and `gcd(0, 0) = 0`.
> - <span class="hl-blue">`lcm(a, b)`</span>: the smallest positive integer divisible by both. `lcm(a, 0) = 0`.
> - `a` and `b` are <span class="hl-blue">coprime</span> if `gcd(a, b) = 1`.

### 2.1 Euclid's algorithm

Any common divisor of `a` and `b` also divides `a − q·b` for any `q`, in particular `a mod b`. So **`gcd(a, b) = gcd(b, a mod b)`**, and the numbers shrink quickly.

```
gcd(a, b):
    if b == 0: return a
    return gcd(b, a mod b)
```

```java
static long gcd(long a, long b) {
    a = Math.abs(a); b = Math.abs(b);        // make the result non-negative
    while (b != 0) {
        long t = a % b;
        a = b;
        b = t;
    }
    return a;
}

static long lcm(long a, long b) {
    if (a == 0 || b == 0) return 0;
    return Math.abs(a / gcd(a, b) * b);      // divide FIRST to delay overflow
}
```

> [!example]- Trace: `gcd(252, 105)`
> | `a` | `b` | `a mod b` |
> |---|---|---|
> | 252 | 105 | 42 |
> | 105 | 42 | 21 |
> | 42 | 21 | 0 |
> | 21 | 0 | — |
>
> Result: `21`. Check: `252 = 12·21`, `105 = 5·21`, and `gcd(12, 5) = 1`.

**Complexity: `O(log min(a, b))`.** After two steps, the larger argument has at least halved. The worst case is two consecutive Fibonacci numbers (Lamé's theorem): the number of steps is at most about 5 × the number of decimal digits of the smaller number.

> [!warning] Negatives and `Math.abs`
> Java's `%` keeps the dividend's sign, so the plain loop can return a **negative** gcd: `gcd(4, -6)` comes out as `-2`. Take absolute values first, or use `BigInteger.gcd` (always non-negative). `Math.abs(Long.MIN_VALUE)` is still negative, so that single input stays broken.

> [!tip] `lcm` overflow
> `a * b / gcd(a, b)` computes `a * b` first, which can overflow even when the lcm fits. `a / gcd(a, b) * b` is exact (the division has no remainder) and only overflows if the lcm itself does. The lcm of a whole array grows fast: the lcm of `1…43` already exceeds `long`.

Useful properties:
- `gcd(a, b) · lcm(a, b) = |a · b|`
- `gcd(a, b) = gcd(a − b, b)`: the subtraction form, the basis of "gcd of differences" tricks
- `gcd(a₁, …, aₙ)` = fold `gcd` over the array. It can only decrease, and it's `O(n + log max)` total, because each decrease at least halves it.
- `gcd(F(m), F(n)) = F(gcd(m, n))` for Fibonacci numbers

### 2.2 Extended Euclid and Bézout's identity

> [!important] Bézout's identity
> For any integers `a, b`, there exist integers `x, y` with **`a·x + b·y = gcd(a, b)`**. The extended Euclidean algorithm finds them.

Unwinding the recursion: if `b·x₁ + (a mod b)·y₁ = g` and `a mod b = a − ⌊a/b⌋·b`, then `a·y₁ + b·(x₁ − ⌊a/b⌋·y₁) = g`.

```
extgcd(a, b):                         -- returns (g, x, y) with a·x + b·y = g
    if b == 0: return (a, 1, 0)
    (g, x1, y1) = extgcd(b, a mod b)
    return (g, y1, x1 − (a div b)·y1)
```

```java
static long[] extGcd(long a, long b) {        // {g, x, y}, for a, b ≥ 0
    if (b == 0) return new long[]{a, 1, 0};
    long[] r = extGcd(b, a % b);
    return new long[]{r[0], r[2], r[1] - (a / b) * r[2]};
}
```

The recursion depth is `O(log)`, so it's safe. `|x| ≤ b` and `|y| ≤ a`, so the coefficients never overflow if `a` and `b` fit.

> [!note] Linear Diophantine equations
> `a·x + b·y = c` has integer solutions **iff `gcd(a, b)` divides `c`**. If `(x₀, y₀)` solves `a·x + b·y = g`, then `x = x₀·(c/g)`, `y = y₀·(c/g)` is one solution, and all solutions are `x + k·(b/g)`, `y − k·(a/g)` for integer `k`.

---

## 3. Modular Arithmetic

> [!note] Definition
> `a ≡ b (mod m)` means `m` divides `a − b`: `a` and `b` leave the same remainder when divided by `m`. Working "mod `m`" means keeping only that remainder, always a value in `[0, m)`.

Problems say "output the answer modulo 10⁹ + 7" because the true answer is astronomically large. You're expected to reduce **at every step**, never at the end.

### 3.1 The rules

| Operation | Rule | Java (values already in `[0, M)`) |
|---|---|---|
| Addition | `(a + b) mod m = ((a mod m) + (b mod m)) mod m` | `(a + b) % M` |
| Subtraction | same, but the result may be negative | `((a - b) % M + M) % M` |
| Multiplication | `(a·b) mod m = ((a mod m)·(b mod m)) mod m` | `a * b % M` (with `long`) |
| Exponentiation | reduce the base, not the exponent (see §8.2) | `modPow(a, e, M)` |
| Division | **no rule**. Multiply by the modular inverse (§5) | `a * inv(b) % M` |

> [!warning] Division does not distribute over mod
> `(a / b) mod m ≠ (a mod m) / (b mod m)`. Example: `(12 / 4) mod 7 = 3`, but `(12 mod 7) / (4 mod 7) = 5 / 4`, which isn't even an integer. Once values have been reduced mod `m`, **ordinary division is meaningless**. Divide by multiplying by the inverse.

> [!warning] Comparisons are meaningless after reduction
> `max(a mod M, b mod M)` is not `max(a, b) mod M`: `10⁹ + 8` reduces to `1`. If a problem needs the *largest* answer and also wants it modulo `M`, compare the true values (or their logarithms, or use a different representation) and reduce only the winner.

### 3.2 Choosing the modulus and avoiding overflow

- `1_000_000_007` and `998_244_353` are both **prime** and fit in `int`. Their sum fits in `int`, but the product of two residues (~10¹⁸) needs `long`. It fits, because `(10⁹)² < 9.2 × 10¹⁸`.
- `998244353 = 119 · 2²³ + 1` is the standard modulus for the number-theoretic transform (NTT).
- **Declare the modulus as an integer.** `final int MOD = 1e9 + 7;` is a compile error: `1e9` is a `double` literal. Write `1_000_000_007`.
- If `M` is larger than ~3 × 10⁹ (e.g. `M ≈ 10¹⁸`), `a * b` overflows `long` even with both operands reduced. Use the `mulMod` below or `BigInteger`.

```java
static final long MOD = 1_000_000_007L;

static long add(long a, long b) { return (a + b) % MOD; }
static long sub(long a, long b) { return ((a - b) % MOD + MOD) % MOD; }
static long mul(long a, long b) { return a % MOD * (b % MOD) % MOD; }
static long norm(long x)        { x %= MOD; return x < 0 ? x + MOD : x; }
```

> [!info]- `mulMod` for a 64-bit modulus
> Russian-peasant multiplication: the same halving/doubling as fast exponentiation, but with `+` in place of `×`. It needs `2m < 2⁶³`, i.e. `m < 2⁶²`.
> ```java
> static long mulMod(long a, long b, long m) {   // a, b in [0, m), m < 2^62
>     long r = 0;
>     while (b > 0) {
>         if ((b & 1) == 1) { r += a; if (r >= m) r -= m; }
>         a += a; if (a >= m) a -= m;
>         b >>= 1;
>     }
>     return r;
> }
> ```
> `O(log b)` per multiplication. Alternatively `BigInteger.valueOf(a).multiply(BigInteger.valueOf(b)).mod(BigInteger.valueOf(m)).longValue()`, or `Math.multiplyHigh` for a faster 128-bit approach.

### 3.3 A huge number given as a string

For "compute `N mod m`" where `N` has 10⁵ digits, go digit by digit. This is Horner's rule, applying the multiplication and addition rules at each step:

```java
static long modOfString(String s, long m) {
    long r = 0;
    for (int i = 0; i < s.length(); i++) r = (r * 10 + (s.charAt(i) - '0')) % m;
    return r;
}
```

The same idea makes divisibility-by-`k` checks on a streaming number `O(1)` per digit.

---

## 4. Fast (Binary) Exponentiation

Computing `aᵉ` by repeated multiplication takes `e − 1` steps, which is hopeless for `e = 10¹⁸`. Instead, square the base and follow the **binary digits of `e`**:

`a¹³ = a^(1101₂) = a⁸ · a⁴ · a¹`, and `a¹, a², a⁴, a⁸` come from repeated squaring.

```
modpow(a, e, m):                  -- e ≥ 0
    result = 1 mod m
    a = a mod m
    while e > 0:
        if e is odd: result = result × a mod m
        a = a × a mod m
        e = e div 2
    return result
```

```java
static long modPow(long a, long e, long m) {   // m ≤ ~3.03e9 so products fit in long
    long result = 1 % m;                       // handles m = 1 correctly (answer 0)
    a %= m;
    if (a < 0) a += m;
    while (e > 0) {
        if ((e & 1) == 1) result = result * a % m;
        a = a * a % m;
        e >>= 1;
    }
    return result;
}
```

`O(log e)` multiplications: about 60 for `e ≈ 10¹⁸`. The recursive form (`half = pow(a, e/2)`, then square) is in [[DSA/Foundations/Recursion#6.1 Fast power (halving)|Recursion § 6.1]].

> [!example]- Trace: `3¹³ mod 1000`
> | `e` (binary) | odd? | `result` | `a` (after squaring) |
> |---|---|---|---|
> | `1101` | yes | `1·3 = 3` | `9` |
> | `110` | no | `3` | `81` |
> | `11` | yes | `3·81 = 243` | `6561 mod 1000 = 561` |
> | `1` | yes | `243·561 = 136323 → 323` | … |
>
> `3¹³ = 1594323`, and `1594323 mod 1000 = 323`. ✓

> [!warning] Edge cases
> - **`e = 0`**: returns `1 % m`, which is `0` when `m = 1`. Starting with `result = 1` gives the wrong answer `1` for `m = 1`.
> - **`0⁰`**: this code returns 1 (mod `m`), the usual convention in combinatorics.
> - **Negative base**: normalise with `a %= m; if (a < 0) a += m;`, or the result can come out negative.
> - **Negative exponent**: not meaningful unless you mean the inverse, `a⁻ᵉ = (a⁻¹)ᵉ` (§5).
> - `BigInteger.modPow` works for any sizes and also accepts a negative exponent (computing the inverse), but it's slower.

The same loop works for anything with an associative multiplication: matrices ([[DSA/Matrix Exponentiation|Matrix Exponentiation]]), permutations (apply a permutation `k` times), and `mulMod` itself.

---

## 5. Modular Inverse

> [!note] Definition
> The <span class="hl-blue">modular inverse</span> of `a` modulo `m` is an `x` with **`a·x ≡ 1 (mod m)`**, written `a⁻¹`. It exists **iff `gcd(a, m) = 1`**. Division `b / a` mod `m` is defined as `b · a⁻¹` mod `m`.

### 5.1 Fermat's little theorem (prime modulus)

> [!important] Fermat's little theorem
> If `p` is prime and `p ∤ a`, then `a^(p−1) ≡ 1 (mod p)`. So **`a⁻¹ ≡ a^(p−2) (mod p)`**.

```java
static long inverse(long a, long p) {        // p prime, a not divisible by p
    return modPow(a, p - 2, p);
}
```

`O(log p)`. This is the standard choice when the modulus is `10⁹ + 7` or `998244353`.

### 5.2 Extended Euclid (any modulus)

From `a·x + m·y = 1`, reducing mod `m` gives `a·x ≡ 1`. So `x` is the inverse:

```java
static long inverseGeneral(long a, long m) {  // returns -1 if no inverse exists
    long[] r = extGcd(((a % m) + m) % m, m);
    if (r[0] != 1) return -1;
    return ((r[1] % m) + m) % m;              // x can be negative; normalise
}
```

This works when `m` isn't prime (as long as `gcd(a, m) = 1`), and it's typically a little faster than `modPow`.

### 5.3 Inverses of 1…n in O(n)

For a prime `p` and `i < p`: write `p = q·i + r` with `q = ⌊p/i⌋`, `r = p mod i`. Then `0 ≡ q·i + r`, so `i⁻¹ ≡ −q · r⁻¹ (mod p)`, and `r < i` has already been computed.

```
inv[1] = 1
for i = 2 to n:
    inv[i] = −(p div i) × inv[p mod i]  mod p
```

```java
static long[] inversesUpTo(int n, long p) {   // n < p, p prime
    long[] inv = new long[n + 1];
    inv[1] = 1;
    for (int i = 2; i <= n; i++)
        inv[i] = (p - (p / i) * inv[(int) (p % i)] % p) % p;
    return inv;
}
```

> [!warning] When the inverse doesn't exist
> - `a ≡ 0 (mod p)` has no inverse. `modPow(0, p−2, p)` returns `0` **silently**, and every "division" by it then gives 0. In combinatorics this happens exactly when `n ≥ p` in `n!`: that's why factorial-based `C(n, k) mod p` requires `n < p` (§9.3).
> - Fermat needs a **prime** modulus. `10⁹ + 6` is not prime, and `a^(m−2) mod m` for composite `m` generally isn't an inverse.
> - For composite `m`, the inverse of `a` exists only if `gcd(a, m) = 1`. Mod 10, `2` has no inverse.

---

## 6. Primes and the Sieve of Eratosthenes

> [!note] Definition
> An integer `p > 1` is <span class="hl-blue">prime</span> if its only positive divisors are `1` and `p`. `1` is **not** prime, and `2` is the only even prime. Every integer `n > 1` has a unique factorization into primes (the fundamental theorem of arithmetic).

### 6.1 Trial division — O(√n)

If `n = a·b` with `a ≤ b`, then `a ≤ √n`. So `n` is composite iff it has a divisor in `[2, √n]`.

```
isPrime(n):
    if n < 2: return false
    for d = 2 while d·d ≤ n:
        if n mod d == 0: return false
    return true
```

```java
static boolean isPrime(long n) {
    if (n < 2) return false;
    if (n < 4) return true;                    // 2, 3
    if (n % 2 == 0 || n % 3 == 0) return false;
    for (long d = 5; d * d <= n; d += 6)       // every prime > 3 is 6k ± 1
        if (n % d == 0 || n % (d + 2) == 0) return false;
    return true;
}
```

> [!tip] `d * d <= n`, not `d <= Math.sqrt(n)`
> The integer condition avoids floating-point error and a `sqrt` call per iteration. Keep `d` a `long`: with `int d` and `n` near `Integer.MAX_VALUE`, `d * d` overflows to a negative number and the loop never stops.

`O(√n)` is fine for one number up to ~10¹⁴. For many queries, sieve. For single 64-bit numbers, use Miller–Rabin (below).

### 6.2 Sieve of Eratosthenes — all primes up to n

Cross out every multiple of each prime. Anything left uncrossed is prime.

```
sieve(n):
    composite[0..n] = false
    for i = 2 while i·i ≤ n:
        if not composite[i]:
            for j = i·i to n step i:        -- smaller multiples were crossed by smaller primes
                composite[j] = true
    primes = all i in [2, n] with not composite[i]
```

```java
static boolean[] sieve(int n) {               // isPrime[i] for 0..n
    boolean[] isPrime = new boolean[n + 1];
    if (n >= 2) Arrays.fill(isPrime, 2, n + 1, true);
    for (int i = 2; (long) i * i <= n; i++) {
        if (!isPrime[i]) continue;
        for (int j = i * i; j <= n; j += i) isPrime[j] = false;
    }
    return isPrime;
}
```

**Complexity: `O(n log log n)` time, `O(n)` memory.** The inner loop runs `n/p` times for each prime `p ≤ √n`, and the sum of `1/p` over primes grows like `log log n`. In practice it's linear: `n = 10⁷` runs in well under a second. Memory is the real limit: `boolean[10⁸]` is 100 MB.

> [!info]- Why start the inner loop at `i·i`?
> Any composite `j = i·k` with `k < i` has a prime factor smaller than `i`, so it was already crossed out when that smaller prime was processed. Starting at `2·i` would still be correct, just slower. This is also why the outer loop can stop at `√n`: every composite `≤ n` has a prime factor `≤ √n`.

> [!info]- Prime counts to sanity-check against
> `π(n)` (the number of primes `≤ n`) is about `n / ln n`:
> | `n` | `10²` | `10³` | `10⁴` | `10⁵` | `10⁶` | `10⁷` | `10⁹` |
> |---|---|---|---|---|---|---|---|
> | `π(n)` | 25 | 168 | 1229 | 9592 | 78498 | 664579 | 50847534 |
>
> The gap between consecutive primes below 10⁹ is never more than 282, which is why "find the next prime after `x`" by testing `x+1, x+2, …` is fast.

### 6.3 Smallest-prime-factor sieve (linear sieve)

Storing each number's **smallest prime factor** (`spf`) lets you factorize any `x ≤ n` in `O(log x)` by repeatedly dividing by `spf[x]`. The linear sieve fills `spf` in `O(n)` by crossing out each composite exactly once, from its smallest prime factor.

```
spf[0..n] = 0; primes = []
for i = 2 to n:
    if spf[i] == 0: spf[i] = i; primes.append(i)       -- i is prime
    for p in primes:
        if p > spf[i] or i·p > n: break
        spf[i·p] = p                                    -- p is the smallest prime of i·p
```

```java
static int[] smallestPrimeFactors(int n) {
    int[] spf = new int[n + 1];
    List<Integer> primes = new ArrayList<>();
    for (int i = 2; i <= n; i++) {
        if (spf[i] == 0) { spf[i] = i; primes.add(i); }
        for (int p : primes) {
            if (p > spf[i] || (long) i * p > n) break;
            spf[i * p] = p;
        }
    }
    return spf;
}

static List<Integer> factorizeWithSpf(int x, int[] spf) {   // x ≥ 2
    List<Integer> factors = new ArrayList<>();
    while (x > 1) {
        factors.add(spf[x]);
        x /= spf[x];
    }
    return factors;                                         // with repetition, ascending
}
```

<span class="hl-yellow">Many factorization queries on values ≤ 10⁷ → SPF sieve. One value up to 10¹² → trial division. One value up to 10¹⁸ → Pollard's rho (advanced).</span>

> [!info]- Segmented sieve *(advanced)*
> For primes in a window `[L, R]` with `R` up to ~10¹² but `R − L ≤ 10⁶`: sieve the primes up to `√R` normally, then for each such prime `p`, cross out its multiples inside the window, starting at `max(p², ⌈L/p⌉·p)`. Memory is `O(√R + (R − L))`. Watch out for `L = 1` (1 isn't prime).

> [!info]- Miller–Rabin *(advanced)*
> A probabilistic primality test in `O(k log³ n)`. For 64-bit `n`, testing the bases `{2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}` is **deterministic** (no error). It needs a 64-bit `mulMod` (§3.2). In Java, `BigInteger.valueOf(n).isProbablePrime(30)` is a correct, if slower, stand-in.

---

## 7. Prime Factorization and Divisors

### 7.1 Trial-division factorization — O(√n)

```
factorize(n):                     -- n ≥ 2
    factors = []
    for p = 2 while p·p ≤ n:
        while n mod p == 0:
            factors.append(p); n = n / p
    if n > 1: factors.append(n)    -- what's left is a prime > √(original n)
    return factors
```

```java
static List<Long> factorize(long n) {
    List<Long> factors = new ArrayList<>();
    for (long p = 2; p * p <= n; p++) {
        while (n % p == 0) {
            factors.add(p);
            n /= p;
        }
    }
    if (n > 1) factors.add(n);
    return factors;
}
```

> [!warning] Don't forget the leftover factor
> After the loop, `n > 1` means the remainder is a prime larger than `√n`. At most one such factor can exist. Forgetting it is the classic bug: `factorize(14)` would return only `[2]`, dropping the `7`.

The loop condition `p·p ≤ n` uses the **shrinking** `n`, so a number with small factors finishes quickly. The worst case, `O(√n)`, is when `n` is prime or a product of two large primes.

### 7.2 Divisor count and divisor sum

If `n = p₁^e₁ · p₂^e₂ · … · pₖ^eₖ`:

| Quantity | Formula | `n = 12 = 2²·3` |
|---|---|---|
| Number of divisors `d(n)` | `(e₁+1)(e₂+1)…(eₖ+1)` | `3·2 = 6` → {1,2,3,4,6,12} |
| Sum of divisors `σ(n)` | `Π (pᵢ^(eᵢ+1) − 1) / (pᵢ − 1)` | `7·4 = 28` |

> [!info]- How many divisors can a number have?
> Far fewer than people guess, which is what makes "iterate over all divisors" feasible:
> | `n` up to | max `d(n)` |
> |---|---|
> | 10³ | 32 |
> | 10⁶ | 240 |
> | 10⁹ | 1344 |
> | 10¹⁸ | 103680 |
>
> A common rough bound is `d(n) ≈ n^(1/3)` for the ranges seen in problems.

### 7.3 Listing all divisors — O(√n)

Divisors come in pairs `(d, n/d)` with `d ≤ √n`:

```java
static List<Long> divisors(long n) {          // n ≥ 1, unsorted
    List<Long> ds = new ArrayList<>();
    for (long d = 1; d * d <= n; d++) {
        if (n % d == 0) {
            ds.add(d);
            if (d != n / d) ds.add(n / d);     // perfect squares: don't add √n twice
        }
    }
    return ds;
}
```

> [!tip] Divisors of every number up to n — harmonic sieve
> `for d in 1..n: for multiple m = d, 2d, 3d, … ≤ n: add d to divisors[m]` costs `Σ n/d = O(n log n)` (see [[DSA/Foundations/Complexity Analysis#4.5 Harmonic sums — the sieve pattern|Complexity § 4.5]]). Much better than `n` separate `O(√n)` loops.

---

## 8. Euler's Totient Function

> [!note] Definition
> <span class="hl-blue">`φ(n)`</span> is the number of integers in `[1, n]` that are coprime to `n`. `φ(1) = 1`, and `φ(p) = p − 1` for a prime `p`.

> [!important] Product formula
> **`φ(n) = n · Π (1 − 1/p)`** over the distinct primes `p` dividing `n`.
> Consequences: `φ(pᵏ) = pᵏ − pᵏ⁻¹`; `φ` is multiplicative (`φ(ab) = φ(a)φ(b)` when `gcd(a, b) = 1`); and `Σ_{d | n} φ(d) = n`.

### 8.1 Computing φ

For a single `n`, factorize and apply the formula as `result -= result / p`, which keeps everything in integers:

```
phi(n):
    result = n
    for p = 2 while p·p ≤ n:
        if n mod p == 0:
            while n mod p == 0: n = n / p
            result = result − result / p
    if n > 1: result = result − result / n     -- leftover prime factor
    return result
```

```java
static long phi(long n) {
    long result = n;
    for (long p = 2; p * p <= n; p++) {
        if (n % p == 0) {
            while (n % p == 0) n /= p;
            result -= result / p;
        }
    }
    if (n > 1) result -= result / n;
    return result;
}

static int[] phiUpTo(int n) {                 // all totients in O(n log log n)
    int[] phi = new int[n + 1];
    for (int i = 0; i <= n; i++) phi[i] = i;
    for (int i = 2; i <= n; i++) {
        if (phi[i] != i) continue;            // i is not prime (already reduced)
        for (int j = i; j <= n; j += i) phi[j] -= phi[j] / i;
    }
    return phi;
}
```

### 8.2 Euler's theorem and reducing huge exponents

> [!important] Euler's theorem
> If `gcd(a, m) = 1`, then **`a^φ(m) ≡ 1 (mod m)`**. Fermat's little theorem is the special case `m = p`.

Consequences:
- **Exponent reduction**: if `gcd(a, m) = 1`, then `aᵉ ≡ a^(e mod φ(m)) (mod m)`. For prime `p`: reduce the exponent **mod `p − 1`, not mod `p`**.
- **Inverse for any modulus**: `a⁻¹ ≡ a^(φ(m) − 1) (mod m)`.
- **When `gcd(a, m) ≠ 1`**: the generalised form `aᵉ ≡ a^((e mod φ(m)) + φ(m)) (mod m)` holds for all `e ≥ log₂ m`. It's needed for power towers such as `a^(b^c) mod m`.

> [!example]- `2^(10¹⁸) mod (10⁹ + 7)`
> `p = 10⁹ + 7` is prime and `gcd(2, p) = 1`. Reduce the exponent mod `p − 1 = 10⁹ + 6`, then call `modPow(2, 10¹⁸ mod (10⁹ + 6), p)`. `modPow` handles `e = 10¹⁸` directly as well (~60 steps). The reduction is essential only when the exponent itself is too big to store, e.g. `2^(3^(10⁵))`, or an exponent given as a string (reduce it digit by digit mod `p − 1`, §3.3).

---

## 9. Combinatorics

### 9.1 Counting basics

| Question | Count |
|---|---|
| Ordered arrangements of all `n` distinct items | `n!` |
| Ordered selections of `k` from `n` (permutations) | `P(n, k) = n! / (n − k)!` |
| Unordered selections of `k` from `n` (combinations) | `C(n, k) = n! / (k! (n − k)!)` |
| Sequences of length `k` over `n` symbols (repetition allowed) | `nᵏ` |
| Arrangements of a multiset (`n` items, counts `c₁…cₘ`) | `n! / (c₁! c₂! … cₘ!)` |
| Subsets of an `n`-set | `2ⁿ` |
| Multisets of size `k` from `n` types (**stars and bars**) | `C(n + k − 1, k)` |
| Ways to write `n` as an ordered sum of `k` **non-negative** ints | `C(n + k − 1, k − 1)` |
| … of `k` **positive** ints | `C(n − 1, k − 1)` |

> [!important] Binomial identities
> - `C(n, 0) = C(n, n) = 1`; `C(n, k) = 0` if `k < 0` or `k > n`
> - Symmetry: `C(n, k) = C(n, n − k)`
> - **Pascal's rule**: `C(n, k) = C(n − 1, k − 1) + C(n − 1, k)` (element `n` is either chosen or not)
> - Row sum: `Σₖ C(n, k) = 2ⁿ`
> - Hockey stick: `Σ_{i=r}^{n} C(i, r) = C(n + 1, r + 1)`
> - Vandermonde: `Σₖ C(m, k)·C(n, r − k) = C(m + n, r)`
> - Binomial theorem: `(x + y)ⁿ = Σₖ C(n, k) xᵏ yⁿ⁻ᵏ`

### 9.2 Pascal's triangle — O(n²) table

```
C[0..n][0..n] = 0
for i = 0 to n:
    C[i][0] = 1
    for j = 1 to i:
        C[i][j] = C[i−1][j−1] + C[i−1][j]
```

```java
static long[][] pascal(int n, long mod) {     // mod = Long.MAX_VALUE for exact values (n ≤ 66)
    long[][] C = new long[n + 1][n + 1];
    for (int i = 0; i <= n; i++) {
        C[i][0] = 1;
        for (int j = 1; j <= i; j++) C[i][j] = (C[i - 1][j - 1] + C[i - 1][j]) % mod;
    }
    return C;
}
```

It uses only addition, so it works with **any modulus**, prime or not, and without a modulus it gives exact values up to `n = 66`. `O(n²)` memory limits it to `n ≈ 5000`.

### 9.3 Factorials and inverse factorials — O(n) precompute, O(1) per query

The standard method for many `C(n, k) mod p` queries with prime `p > n`:

```
fact[0] = 1
for i = 1 to N: fact[i] = fact[i−1] × i mod p
invFact[N] = modpow(fact[N], p − 2, p)
for i = N down to 1: invFact[i−1] = invFact[i] × i mod p      -- 1/(i−1)! = i / i!
C(n, k) = 0 if k < 0 or k > n, else fact[n] × invFact[k] × invFact[n−k] mod p
```

```java
static final int MAXN = 1_000_000;
static long[] fact = new long[MAXN + 1], invFact = new long[MAXN + 1];

static void initFactorials(long p) {
    fact[0] = 1;
    for (int i = 1; i <= MAXN; i++) fact[i] = fact[i - 1] * i % p;
    invFact[MAXN] = modPow(fact[MAXN], p - 2, p);
    for (int i = MAXN; i > 0; i--) invFact[i - 1] = invFact[i] * i % p;
}

static long nCr(int n, int k, long p) {
    if (k < 0 || k > n) return 0;
    return fact[n] * invFact[k] % p * invFact[n - k] % p;   // reduce between the two products
}
```

Only **one** `modPow` call: the backward loop gets every other inverse factorial for free.

> [!warning] Conditions for the factorial method
> - The modulus must be **prime** (for the inverse), and **`n < p`**. Otherwise `n!` contains the factor `p`, so `fact[n] ≡ 0` and every result comes out 0. For `n ≥ p`, use Lucas' theorem (below).
> - `fact[n] * invFact[k] * invFact[n-k] % p` without the middle `% p` overflows: a product of three values near 10⁹ is 10²⁷.
> - Return 0 for `k < 0` or `k > n` explicitly. Problems love to call `C(n, k)` with `k` out of range, and the array access would throw or give garbage.

### 9.4 One exact value — multiplicative formula

```java
static long nCrExact(int n, int k) {          // exact while the result fits in long
    if (k < 0 || k > n) return 0;
    k = Math.min(k, n - k);                   // fewer steps
    long r = 1;
    for (int i = 1; i <= k; i++) r = r * (n - k + i) / i;   // exact at every step
    return r;
}
```

After step `i`, `r = C(n − k + i, i)`, an integer, so the division is always exact. But **the order matters**: `r * (n−k+i)` must be computed before dividing, and that intermediate can overflow even when the final answer fits. It's safe for every `k` only up to `n = 61`. At `n = 62, k = 28` the intermediate product overflows, even though `C(62, 28)` itself fits. Beyond that, cancel with `gcd` before multiplying, or use `BigInteger`.

> [!info]- Lucas' theorem *(advanced)*
> For a prime `p`, write `n` and `k` in base `p`: `n = (nₘ … n₀)ₚ`, `k = (kₘ … k₀)ₚ`. Then
> `C(n, k) ≡ Π C(nᵢ, kᵢ) (mod p)`, where each small `C(nᵢ, kᵢ)` has `nᵢ < p` and uses the factorial table.
> Consequence: `C(n, k)` is odd ⟺ `(k & n) == k` (the case `p = 2`: every bit of `k` must be set in `n`).

### 9.5 Other sequences that show up constantly

> [!note] Catalan numbers
> `Cₙ = C(2n, n) / (n + 1) = C(2n, n) − C(2n, n + 1)`: **1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862**, …
> They count balanced parenthesis strings with `n` pairs, full binary trees with `n + 1` leaves, BSTs on `n` keys, triangulations of an `(n+2)`-gon, monotone lattice paths that don't cross the diagonal, and valid push/pop sequences. Recurrence: `C₀ = 1`, `Cₙ₊₁ = Σᵢ Cᵢ·Cₙ₋ᵢ`.

> [!note] Derangements
> Permutations with no fixed point: `D(n) = (n − 1)(D(n−1) + D(n−2))`, `D(0) = 1`, `D(1) = 0`: **1, 0, 1, 2, 9, 44, 265**, … and `D(n)/n! → 1/e`.

> [!note] Inclusion–exclusion
> `|A ∪ B ∪ C| = |A| + |B| + |C| − |A∩B| − |A∩C| − |B∩C| + |A∩B∩C|`. In general, add intersections of odd size and subtract those of even size.
> **Example**: integers in `[1, n]` divisible by 2, 3, or 5 = `n/2 + n/3 + n/5 − n/6 − n/10 − n/15 + n/30` (integer division). With `k` conditions there are `2ᵏ` terms, enumerated with a bitmask ([[DSA/Foundations/Bit Manipulation#7.1 Enumerating all subsets|Bit Manipulation § 7.1]]). Note that the intersections use the **lcm** of the divisors, not the product, when they aren't coprime.

> [!note] Pigeonhole principle
> Putting `n + 1` items into `n` boxes forces some box to hold two. It's a proof tool that often turns into an algorithm: among any `n + 1` integers, two have the same remainder mod `n`. Among `n` prefix sums (mod `n`), plus the empty prefix, two are equal, so some non-empty subarray has a sum divisible by `n`.

---

## 10. Chinese Remainder Theorem (advanced)

> [!important] Chinese Remainder Theorem
> If `m₁, …, mₖ` are **pairwise coprime**, the system `x ≡ aᵢ (mod mᵢ)` has a **unique** solution modulo `M = m₁·m₂·…·mₖ`.
> For **non-coprime** moduli, `x ≡ a₁ (mod m₁)`, `x ≡ a₂ (mod m₂)` is solvable **iff `a₁ ≡ a₂ (mod gcd(m₁, m₂))`**, and then the solution is unique modulo `lcm(m₁, m₂)`.

Merge two congruences at a time. From `x = a₁ + m₁·t`, we need `m₁·t ≡ a₂ − a₁ (mod m₂)`. Divide by `g = gcd(m₁, m₂)` and multiply by the inverse of `m₁/g` modulo `m₂/g`:

```
crt(a1, m1, a2, m2):
    (g, p, q) = extgcd(m1, m2)                 -- m1·p + m2·q = g
    if (a2 − a1) mod g ≠ 0: return NO SOLUTION
    t = ((a2 − a1) / g) × p  mod (m2 / g)
    return (a1 + m1·t  mod lcm,  lcm)          -- lcm = m1 / g × m2
```

```java
// Returns {x, lcm} with x ≡ a1 (mod m1), x ≡ a2 (mod m2), or null if none exists.
// Assumes 0 ≤ a1 < m1, 0 ≤ a2 < m2, and that m2/g is small enough for the
// product below to fit in a long (e.g. moduli up to ~1e9).
static long[] crt(long a1, long m1, long a2, long m2) {
    long[] e = extGcd(m1, m2);
    long g = e[0], p = e[1];
    if ((a2 - a1) % g != 0) return null;
    long mod = m2 / g;
    long t = ((a2 - a1) / g % mod) * (p % mod) % mod;
    if (t < 0) t += mod;
    long lcm = m1 / g * m2;
    return new long[]{a1 + m1 * t, lcm};      // m1·t < lcm, so this is already in [0, lcm)
}
```

For `k` congruences, fold: merge the first two into one, then merge that with the third, and so on.

> [!example]- `x ≡ 2 (mod 3)`, `x ≡ 3 (mod 5)`, `x ≡ 2 (mod 7)`
> Merge the first two: `x ≡ 8 (mod 15)`. Merge with the third: `x ≡ 23 (mod 105)`. Check: `23 = 7·3 + 2 = 4·5 + 3 = 3·7 + 2`. ✓ (This is Sunzi's original problem.)

Uses: combining answers computed modulo several small primes (e.g. `C(n, k) mod` a composite `m`), and reasoning about periodic events ("when do these cycles align?"). The overflow constraint is real: once the combined modulus passes ~10⁹, the `t` computation needs `mulMod` or `BigInteger`.

---

## 11. Useful Formulas and Utilities

### 11.1 Sums

| Sum | Closed form | Overflow note |
|---|---|---|
| `1 + 2 + … + n` | `n(n+1)/2` | `n = 10⁹` → ~5 × 10¹⁷, needs `long` |
| `1² + … + n²` | `n(n+1)(2n+1)/6` | the product overflows `long` well before the result does |
| `1³ + … + n³` | `(n(n+1)/2)²` | |
| `1 + r + … + rⁿ⁻¹` | `(rⁿ − 1)/(r − 1)` | mod p: multiply by `(r−1)⁻¹`; if `r ≡ 1`, the sum is `n` |
| `1/1 + 1/2 + … + 1/n` | `≈ ln n + 0.577` | the harmonic series behind `O(n log n)` sieves |

> [!warning] Formulas with division, under a modulus
> `n(n+1)/2 mod M`: you can't divide the reduced product by 2 (§3.1). Either divide **before** reducing (one of `n`, `n+1` is even, so halve that one), or multiply by `inv(2) = (M + 1) / 2`.

### 11.2 Exact integer square root

```java
static long isqrt(long n) {                   // largest r with r*r <= n, n >= 0
    long r = (long) Math.sqrt((double) n);
    while (r > 0 && r > n / r) r--;           // r*r > n, tested without multiplying
    while (r + 1 <= n / (r + 1)) r++;         // (r+1)^2 <= n, likewise
    return r;
}
static boolean isPerfectSquare(long n) { if (n < 0) return false; long r = isqrt(n); return r * r == n; }
```

`Math.sqrt` gets you within 1; the two loops fix it. The checks are written with **division** because the obvious `(r + 1) * (r + 1) <= n` overflows near `Long.MAX_VALUE` (`3037000500²` > 2⁶³ − 1). The wrapped product is negative, so the loop would keep incrementing.

### 11.3 Digits and bases

- Digit sum / reversal: loop `n % 10`, `n /= 10`. For negatives, `%` gives negative digits, so take `Math.abs` first (mind `Long.MIN_VALUE`).
- Base conversion: `Long.toString(n, base)` and `Long.parseLong(s, base)` for `2 ≤ base ≤ 36`.
- Number of digits of `n!` without computing it: `⌊Σ log₁₀ i⌋ + 1`. Trailing zeros of `n!`: `⌊n/5⌋ + ⌊n/25⌋ + ⌊n/125⌋ + …` (Legendre's formula for `p = 5`).

---

## 12. Common Mistakes

| Mistake | Effect | Fix |
|---|---|---|
| `long x = a * b;` with `int`s | overflow before widening | `(long) a * b` |
| `(a - b) % M` | can be negative | `((a - b) % M + M) % M` |
| Reducing only at the end | overflow mid-computation | reduce after every `+` and `*` |
| `fact[n] * inv[k] * inv[n-k] % M` | overflow (10²⁷) | `% M` after each multiplication |
| Dividing reduced values | wrong answer | multiply by the inverse |
| Fermat inverse with a non-prime modulus | wrong answer | extended Euclid |
| Reducing the exponent mod `p` | wrong answer | reduce mod `p − 1` (and only if `gcd(a, p) = 1`) |
| `final int MOD = 1e9 + 7;` | compile error | `1_000_000_007` |
| `Math.pow` for integer powers | precision loss above 2⁵³ | loop or `modPow` |
| `result = 1` in `modPow` with `m = 1` | returns `1` instead of `0` | `result = 1 % m` |
| Forgetting the leftover prime in factorization | missing factor | `if (n > 1) add(n)` |
| `for (int d = 2; d * d <= n; d++)` with large `n` | `d * d` overflows | `long d` |
| Sieve inner loop from `i * i` in `int` for `n` near `2³¹` | overflow | loop bound check in `long` |
| `C(n, k)` with `k > n` or `k < 0` | exception or garbage | return 0 |
| Factorial method with `n ≥ p` | all results 0 | Lucas' theorem |
| `gcd` with negative inputs | negative gcd | `Math.abs` first |
| `a * b / gcd(a, b)` | overflow | `a / gcd(a, b) * b` |
| Treating `1` as prime | wrong counts | `n < 2 → false` |

---

## 13. Trick Questions and Special Cases

> [!question]- What is `gcd(0, 0)`? `gcd(0, 5)`? `lcm(0, 5)`?
> `0`, `5`, and `0`, by convention. Every integer divides 0, so `gcd(0, n) = |n|`. `gcd(0, 0) = 0` keeps the identities working. Euclid's loop returns these values automatically. Beware code that divides by the gcd, since `lcm(0, 0)` would divide by zero without a guard.

> [!question]- Is 1 prime? Is 2?
> `1` is **not** prime; with it, unique factorization would fail (`6 = 2·3 = 1·2·3`). `2` is prime, and the only even one. Many "count primes" bugs are really about 0 and 1 being left as `true` in the sieve array.

> [!question]- `modPow(a, 0, 1)` — what should it return?
> `0`. Everything mod 1 is 0, including `a⁰ = 1`. Code that initialises `result = 1` returns `1`. That's why `result = 1 % m`.

> [!question]- Can you compute `(a / b) mod M` as `(a mod M) / (b mod M)`?
> No. After reduction, the quotient may not even be an integer, and when it is, it's usually wrong. Use `a · b⁻¹ mod M`, which requires `gcd(b, M) = 1`.

> [!question]- To compute `a^e mod p` with `e` astronomically large, reduce `e` mod what?
> Mod **`p − 1`** (by Fermat), not mod `p`, and only if `p ∤ a`. If `p | a`, the answer is 0 for any `e ≥ 1`, but `e mod (p−1)` could be 0, giving `a⁰ = 1`. That's wrong, so handle it separately.

> [!question]- Why is `n ≥ p` fatal for `C(n, k) mod p` via factorials?
> `n!` then contains the factor `p`, so `fact[n] ≡ 0` and has no inverse. The true `C(n, k) mod p` may be non-zero (e.g. `C(p+1, 1) = p + 1 ≡ 1`). Lucas' theorem handles this case correctly.

> [!question]- What is `(-7) % 3` in Java? And `Math.floorMod(-7, 3)`?
> `-1` and `2`. `%` keeps the sign of the dividend; `floorMod` always returns a value in `[0, m)`. Many "mod" formulas in textbooks assume the second behaviour.

> [!question]- Is the Sieve of Eratosthenes O(n log n) or O(n log log n)?
> `O(n log log n)`. The inner loop only runs for **primes** `p`, and `Σ 1/p` over primes up to `n` is `~ln ln n`. Running it for every `i` (not just primes) would give the harmonic sum `O(n log n)`.

> [!question]- Is trial division up to √n polynomial-time?
> No. It's `O(√N)` in the **value** `N`, which is exponential in the input size (`log N` bits). See [[DSA/Foundations/Complexity Analysis#1.1 What counts as "input size"?|Complexity § 1.1]]. It's still perfectly practical up to ~10¹⁴.

> [!question]- `x ≡ 1 (mod 4)` and `x ≡ 2 (mod 6)` — is there a solution?
> No. `gcd(4, 6) = 2`, and `1 ≢ 2 (mod 2)`: the first makes `x` odd, the second makes it even. CRT's uniqueness and existence need coprime moduli, or the compatibility check.

> [!question]- What is `φ(1)`? And is `φ(n)` even?
> `φ(1) = 1` (the number 1 is coprime to itself). `φ(n)` is even for every `n ≥ 3`, because coprime residues pair up as `k ↔ n − k`.

> [!question]- A number `n ≤ 10¹²` — how long does factorizing it take?
> At most ~10⁶ iterations (`√10¹²`). It's the prime (or product-of-two-large-primes) case that takes that long; numbers with small factors finish much faster.

> [!question]- Why does `(long) Math.sqrt(n)` need correcting?
> A `double` has 53 bits of precision. Near 10¹⁸, `n` isn't exactly representable, and the rounded square root can be off by one in either direction. `(long) Math.sqrt(10¹⁸ − 1)` is `10⁹`, whose square exceeds `n`.

> [!question]- Does `C(n, k)` via the multiplicative formula depend on the order of `*` and `/`?
> Yes. `r = r * (n−k+i) / i` is always exact. `r = r / i * (n−k+i)` isn't, because `r` needn't be divisible by `i` at that point, and integer division truncates.

> [!question]- The sum `1 + 2 + … + n` for `n = 10⁵` in `int` — safe?
> `n(n+1)/2 ≈ 5 × 10⁹` exceeds `Integer.MAX_VALUE` (~2.1 × 10⁹). And computing `n * (n + 1)` in `int` overflows already at `n ≈ 46341`. Use `long`.

> [!question]- How many times can `gcd` decrease when folded over an array?
> At most `log₂(max)` times, since each strict decrease at least halves it (the new gcd divides the old one). So folding `gcd` over `n` numbers is `O(n + log max)`, not `O(n log max)`.

---

## 14. Quick Reference — Non-Obvious Outcomes

| Fact | Value |
|---|---|
| `gcd` complexity | `O(log min(a, b))` |
| `lcm` without overflow | `a / gcd(a,b) * b` |
| `ax + by = c` solvable | iff `gcd(a, b) \| c` |
| `(a − b) mod M` | `((a − b) % M + M) % M` |
| Max modulus for `a * b % m` in `long` | ~3.03 × 10⁹ |
| `modPow` | `O(log e)`; start from `1 % m` |
| Inverse mod prime `p` | `a^(p−2)` |
| Inverse exists | iff `gcd(a, m) = 1` |
| Inverses `1..n` | `inv[i] = −(p/i)·inv[p % i]` |
| Exponent reduction mod prime `p` | mod `p − 1` |
| Sieve | `O(n log log n)` |
| SPF sieve factorization | `O(log x)` per query |
| Trial division | `O(√n)`; remember the leftover `n > 1` |
| Max divisors `≤ 10⁹` | 1344 |
| `π(10⁶)` | 78498 |
| `φ(n)` | `n · Π(1 − 1/p)` |
| `C(n, k) mod p`, `n < p` | `fact[n]·invFact[k]·invFact[n−k]` |
| Largest exact `C(n, n/2)` in `long` | `n = 66` |
| Largest factorial in `int` / `long` | `12!` / `20!` |
| Stars and bars (`k` non-neg summing to `n`) | `C(n + k − 1, k − 1)` |
| Catalan | 1, 1, 2, 5, 14, 42, 132, … |
| `C(n, k)` odd | iff `(k & n) == k` |
| `(long) Math.pow(3, 35)` | off by 3 |
| `-7 % 3` / `floorMod(-7, 3)` | `-1` / `2` |

---

## 15. Summary

- **Overflow** is the main enemy. Cast to `long` before multiplying, reduce mod `M` after every operation, and know which products fit (`M ≈ 10⁹` is safe in `long`; `M ≈ 10¹⁸` isn't).
- Java's `%` follows the dividend's sign. Normalise with `+ M` or use `Math.floorMod`.
- **Euclid** computes `gcd` in `O(log)`; the extended version gives Bézout coefficients, inverses for any modulus, and CRT.
- **Fast exponentiation** follows the bits of the exponent: `O(log e)`. It works for any associative multiplication.
- Modular **division is multiplication by the inverse**, which exists iff `gcd(a, m) = 1`. For prime `p`, `a⁻¹ = a^(p−2)`.
- **Sieve** for many primes (`O(n log log n)`), **SPF sieve** for many factorizations, **trial division** (`O(√n)`) for one number, and don't forget the leftover prime factor.
- **`φ(n) = n·Π(1 − 1/p)`**. Euler's theorem lets you reduce exponents mod `φ(m)` (mod `p − 1` for a prime).
- **`C(n, k) mod p`**: precompute factorials and inverse factorials (`n < p`), use Pascal's triangle for small `n` or composite moduli, and Lucas for `n ≥ p`.
- **CRT** merges congruences pairwise, and needs a compatibility check when the moduli aren't coprime.

## Related

- [[DSA/Syllabus|Syllabus]]
- Previous: [[DSA/Foundations/Bit Manipulation|Bit Manipulation]] · Next: [[DSA/Arrays|Arrays]] (Part II)
- [[DSA/Foundations/Complexity Analysis#1.1 What counts as "input size"?|Complexity Analysis § 1.1]]: pseudo-polynomial complexity of number algorithms
- [[DSA/Foundations/Recursion#6.1 Fast power (halving)|Recursion § 6.1]]: recursive fast power
- [[Java/Foundations/Operators#3. Division and Remainder — The Special Cases|Java: Operators § 3–4]]: `/`, `%`, and overflow
- [[DSA/Matrix Exponentiation|Matrix Exponentiation]]: fast exponentiation on matrices
- [[DSA/String Hashing|String Hashing]]: polynomial hashing mod a prime
- [[DSA/Classic DP Problems|Classic DP Problems]]: counting problems modulo `10⁹ + 7`
