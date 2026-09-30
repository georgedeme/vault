# Complexity Analysis

<span class="hl-blue">Complexity analysis</span> is the study of how an algorithm's resource usage — time and memory — grows as its input grows. It deliberately ignores machine speed, language, and constant factors, and asks a single question: **what happens as the input gets large?**

This is the foundation for every other chapter in this syllabus. Choosing between a hash map and a sorted array, between recursion and an explicit stack, or between `O(n²)` brute force and `O(n log n)` sorting is always a complexity argument.

## Contents

- [[#1. The Model — What Exactly Are We Counting?|1. The Model — What Exactly Are We Counting?]]
- [[#2. Asymptotic Notation|2. Asymptotic Notation]]
- [[#3. The Growth Hierarchy|3. The Growth Hierarchy]]
- [[#4. Analyzing Iterative Code|4. Analyzing Iterative Code]]
- [[#5. Best, Average, and Worst Case|5. Best, Average, and Worst Case]]
- [[#6. Recurrence Relations|6. Recurrence Relations]]
- [[#7. The Master Theorem|7. The Master Theorem]]
- [[#8. Amortized Analysis|8. Amortized Analysis]]
- [[#9. Space Complexity|9. Space Complexity]]
- [[#10. Multi-Variable and Output-Sensitive Complexity|10. Multi-Variable and Output-Sensitive Complexity]]
- [[#11. Complexity of Common Operations|11. Complexity of Common Operations]]
- [[#12. From Constraints to Target Complexity|12. From Constraints to Target Complexity]]
- [[#13. Trick Questions and Special Cases|13. Trick Questions and Special Cases]]
- [[#14. Quick Reference — Non-Obvious Outcomes|14. Quick Reference — Non-Obvious Outcomes]]
- [[#15. Summary|15. Summary]]

---

## 1. The Model — What Exactly Are We Counting?

Analysis is done against an idealized machine, the **RAM (Random Access Machine) model**:

- Each *primitive operation* — arithmetic, comparison, assignment, array indexing, following a reference — costs **1 unit of time**.
- Memory access is **uniform cost**: reading `a[0]` costs the same as reading `a[1_000_000]`.
- Integers are assumed to fit in a machine word.

We then count primitive operations as a function of the **input size `n`**, and describe that function's growth rate.

> [!warning] All three of those assumptions are lies
> They are useful lies, but they do fail:
> - **Cache effects** make sequential access far faster than random access in practice. An `O(n log n)` merge sort with good locality can beat a cache-hostile `O(n)` algorithm at realistic sizes.
> - **Big-integer arithmetic is not `O(1)`.** If values grow past 64 bits (factorials, Fibonacci without modulo, `BigInteger` work), multiplication itself costs a function of the number of digits.
> - **Comparisons are not always `O(1)`.** Comparing two strings of length `L` costs `O(L)`, so sorting `n` strings is `O(n·L·log n)`, not `O(n log n)`.

### 1.1 What counts as "input size"?

`n` is whatever the problem's size is measured in, and getting this wrong is a common source of incorrect analyses.

| Input | Usual `n` | Common mistake |
|---|---|---|
| Array / list | number of elements | — |
| String | number of characters | — |
| Graph | **two** variables: `V` vertices, `E` edges | collapsing them into a single `n` |
| Matrix `r × c` | `r·c` cells | calling an `r × c` scan `O(n²)` when `n = r·c` |
| A number `N` (e.g. "is `N` prime?") | **number of bits**, `log N` | calling trial division "polynomial" |

> [!warning] Pseudo-polynomial complexity
> For an algorithm whose input is a *numeric value* `N`, complexity written in terms of `N` is called <span class="hl-blue">pseudo-polynomial</span>, because the true input size is `log N` bits. The 0/1 knapsack DP runs in `O(n·W)` — polynomial in the capacity `W`, but exponential in the number of bits used to write `W`. This is exactly why knapsack is NP-hard yet has a "polynomial" DP.

---

## 2. Asymptotic Notation

The three notations below describe **bounds on a function**, not properties of an algorithm. Keeping that distinction clear resolves most confusion in this topic.

### 2.1 Big-O — upper bound

`f(n) = O(g(n))` if there exist constants `c > 0` and `n₀ ≥ 0` such that:

```
0 ≤ f(n) ≤ c · g(n)   for all n ≥ n₀
```

Read as: *`f` grows no faster than `g`, ignoring constants and small inputs.*

### 2.2 Big-Ω — lower bound

`f(n) = Ω(g(n))` if there exist `c > 0`, `n₀ ≥ 0` such that:

```
0 ≤ c · g(n) ≤ f(n)   for all n ≥ n₀
```

Read as: *`f` grows at least as fast as `g`.*

### 2.3 Big-Θ — tight bound

`f(n) = Θ(g(n))` if `f(n) = O(g(n))` **and** `f(n) = Ω(g(n))`. Equivalently, there are constants `c₁, c₂ > 0` with:

```
0 ≤ c₁ · g(n) ≤ f(n) ≤ c₂ · g(n)   for all n ≥ n₀
```

This is the notation that actually says "this *is* the growth rate."

![[Complexity - Theta Sandwich.excalidraw|800]]

### 2.4 Little-o and little-ω — strict bounds

- `f(n) = o(g(n))`: `f` grows **strictly slower** — the bound holds for *every* `c > 0`, not merely for some `c`. Equivalently `lim f(n)/g(n) = 0`.
- `f(n) = ω(g(n))`: `f` grows **strictly faster**; `lim f(n)/g(n) = ∞`.

So `2n² = O(n²)` and `2n² = Θ(n²)` are both true, but `2n² = o(n²)` is **false** — while `2n² = o(n³)` is true.

> [!tip] An analogy that is almost right
> `O` ≈ `≤`, `Ω` ≈ `≥`, `Θ` ≈ `=`, `o` ≈ `<`, `ω` ≈ `>`.
> It breaks down because these are not total orders: functions such as `n^(1+sin n)` are comparable to `n` under none of them.

> [!warning] The `=` in `f(n) = O(g(n))` is not equality
> `O(g(n))` is a *set* of functions; the `=` is historical abuse of notation for `∈`. It does not work symmetrically — `n = O(n²)` is true, `O(n²) = n` is meaningless — and you may never "cancel" across it. `n = O(n²)` and `n² = O(n²)` together do **not** give `n = n²`.

### 2.5 Why "worst case" and "Big-O" are not synonyms

This is the single most common conceptual error in the topic.

- **Best / average / worst case** selects *which input* you analyze.
- **O / Ω / Θ** describes *how you bound* the resulting function.

The two axes are independent, so all combinations are legitimate: the **best** case of insertion sort is `Θ(n)`; the **worst** case of any comparison sort is `Ω(n log n)`. Saying "insertion sort is `O(n²)`" is true but incomplete; saying "Big-O means worst case" is simply wrong.

> [!example]- Statements that are technically true but useless
> - Binary search is `O(n!)` — true; the upper bound is valid, just absurdly loose.
> - Every algorithm is `Ω(1)`.
>
> When an interviewer asks for "the complexity," they want the **tight** (Θ) bound, even though convention writes it with `O`.

---

## 3. The Growth Hierarchy

Ordered from slowest-growing (best) to fastest-growing (worst):

```
O(1) < O(α(n)) < O(log log n) < O(log n) < O(√n) < O(n) < O(n log n)
     < O(n√n) < O(n²) < O(n³) < O(n^k) < O(2ⁿ) < O(n!) < O(nⁿ)
```

![[Complexity - Growth Rates.excalidraw|800]]

| Class | Name | Typical source |
|---|---|---|
| `O(1)` | constant | array index, hash lookup, arithmetic |
| `O(α(n))` | inverse Ackermann | union-find with path compression + union by rank |
| `O(log n)` | logarithmic | binary search, balanced-tree ops, heap push/pop |
| `O(√n)` | root | trial-division primality, sqrt decomposition |
| `O(n)` | linear | single pass, two pointers, counting |
| `O(n log n)` | linearithmic | merge/heap sort, most divide and conquer |
| `O(n²)` | quadratic | all pairs, simple 2D DP |
| `O(n³)` | cubic | Floyd–Warshall, naive matrix multiplication |
| `O(2ⁿ)` | exponential | all subsets, unmemoized branching recursion |
| `O(n!)` | factorial | all permutations, brute-force TSP |

### 3.1 Simplification rules

1. **Drop constant factors.** `Θ(3n)` → `Θ(n)`.
2. **Keep only the dominant term.** `Θ(n² + n log n + 500)` → `Θ(n²)`.
3. **Log bases are constants.** `log₂ n = log₁₀ n / log₁₀ 2`, so `O(log₂ n) = O(log₁₀ n) = O(ln n)`. Write `O(log n)` with no base.
4. **Sequential code adds; nested code multiplies.** `O(a) + O(b) = O(max(a, b))`; a loop of `a` iterations doing `O(b)` work each is `O(a·b)`.

> [!warning] Exponents are *not* like log bases
> `O(2ⁿ)` and `O(3ⁿ)` are **not** the same class: `3ⁿ / 2ⁿ = 1.5ⁿ → ∞`. Changing the base of a logarithm is a constant factor; changing the base of an exponent is not. Likewise `O(2ⁿ) ≠ O(2^(2n))`, since `2^(2n) = 4ⁿ`.

> [!info]- Comparisons that trip people up
> - `O(log n)` vs `O(√n)` — the logarithm is smaller for all large `n`.
> - `O(n log n)` vs `O(n^1.1)` — **`n^1.1` is asymptotically larger**, even though `n log n` is bigger for every `n` you would ever actually run. Asymptotics describe the limit, not your test case.
> - `O(2ⁿ)` vs `O(n!)` — factorial is worse; `n!` eventually beats `cⁿ` for any constant `c`.
> - `O(n!)` vs `O(nⁿ)` — `nⁿ` is worse, since `n! < nⁿ`.
> - `O(log(n!)) = O(n log n)` by Stirling's approximation — this is where the comparison-sort lower bound comes from.
> - `O(√n) = O(n^0.5)` — a polynomial, not something exotic.

---

## 4. Analyzing Iterative Code

The method: **state the loop structure in pseudocode → count how many times the innermost statement executes → simplify.**

### 4.1 Independent nested loops multiply

```
for i = 0 to n-1:
    for j = 0 to m-1:
        constant work
```

`Θ(n·m)` — which is `Θ(n²)` only when `m = n`. Writing `O(n²)` for an `r × c` grid scan is wrong unless `r ≈ c`.

### 4.2 Dependent bounds — still quadratic

```
for i = 0 to n-1:
    for j = i+1 to n-1:
        constant work
```

The body runs `(n−1) + (n−2) + … + 1 = n(n−1)/2` times. Halving is a constant factor, so this is still `Θ(n²)`.

### 4.3 Multiplicative progress gives a logarithm

```
i = 1
while i < n:
    constant work
    i = i * 2
```

`i` takes the values `1, 2, 4, 8, …`, so the loop runs `⌊log₂ n⌋ + 1` times → `Θ(log n)`.

<span class="hl-yellow">Rule of thumb: multiplying or dividing the loop variable by a constant each step ⇒ logarithmic; adding or subtracting a constant ⇒ linear.</span>

### 4.4 A logarithm inside a linear loop

```
for i = 0 to n-1:
    binary_search(array, i)      # O(log n)
```

`Θ(n log n)`.

### 4.5 Harmonic sums — the sieve pattern

```
for i = 1 to n:
    for j = i to n step i:
        constant work
```

The inner loop runs `n/i` times, so the total is `n/1 + n/2 + n/3 + … + n/n = n·Hₙ ≈ n ln n` → **`Θ(n log n)`**, not `Θ(n²)`. This is the same analysis behind the Sieve of Eratosthenes, which is `O(n log log n)` because it only iterates over primes.

### 4.6 Two pointers — a nested loop that isn't quadratic

```
left = 0
for right = 0 to n-1:
    while condition_violated:
        left = left + 1
```

The `while` *looks* nested, but `left` only ever increases and never exceeds `n`. The **total** inner work across the entire run is `O(n)`, so the whole thing is `Θ(n)`.

> [!tip] Analyze total work, not maximum nesting depth
> Counting loop nesting is a heuristic, not a method — sliding windows, two pointers, monotonic stacks, and union-find all defeat it. Ask instead: *over the whole execution, how many times can this statement run in total?*

### 4.7 Java — recognising the pattern in real code

```java
// Θ(n²) time, Θ(1) auxiliary space — every pair considered once
boolean hasPairWithSum(int[] a, int target) {
    for (int i = 0; i < a.length; i++)
        for (int j = i + 1; j < a.length; j++)
            if (a[i] + a[j] == target) return true;
    return false;
}

// Θ(n) expected time, Θ(n) auxiliary space — hashing trades space for time
boolean hasPairWithSumFast(int[] a, int target) {
    Set<Integer> seen = new HashSet<>();
    for (int x : a) {
        if (seen.contains(target - x)) return true;
        seen.add(x);
    }
    return false;
}
```

The second version is a textbook time–space trade-off, and a reminder that a complexity claim should always say *which* resource it describes.

---

## 5. Best, Average, and Worst Case

| Case | Meaning | Example: linear search |
|---|---|---|
| Best | the most favourable input of size `n` | target is first → `Θ(1)` |
| Worst | the least favourable input of size `n` | target absent → `Θ(n)` |
| Average | expectation over an assumed input distribution | uniform position → `Θ(n)` |

**Average case requires a stated distribution.** "Average" with no distribution is not a defined quantity; the usual convention is uniformly random input, which is frequently unrealistic.

### 5.1 Expected vs. average — not the same thing

- **Average case**: the randomness is in the *input*. An adversary who knows the algorithm can choose a bad input.
- **Expected case**: the randomness is in the *algorithm* (random pivots, random hash seed). The guarantee holds **for every input**, because the adversary cannot predict the coin flips.

This is why randomized quicksort is preferred over "quicksort on data that looks random": its `O(n log n)` expected time cannot be defeated by a crafted input, whereas fixed-pivot quicksort degrades to `Θ(n²)` on already-sorted arrays.

> [!warning] Java-specific consequence
> `Arrays.sort(int[])` uses dual-pivot quicksort, whose worst case is `O(n²)`, and anti-quicksort tests exploiting it are common on Codeforces. `Arrays.sort(Integer[])` and `Collections.sort` use TimSort, which is `O(n log n)` worst case. The standard defence for primitives is to shuffle first, or to box into `Integer[]`. See [[DSA/Sorting Algorithms|Sorting Algorithms]].

---

## 6. Recurrence Relations

Recursive algorithms are analyzed by writing `T(n)` — the cost on input size `n` — in terms of itself, then solving.

### 6.1 Recursion tree method

```
T(n) = 2·T(n/2) + n,    T(1) = 1
```

| Level | Subproblems | Size each | Work at level |
|---|---|---|---|
| 0 | 1 | `n` | `n` |
| 1 | 2 | `n/2` | `n` |
| 2 | 4 | `n/4` | `n` |
| … | … | … | `n` |
| `log₂ n` | `n` | 1 | `n` |

Depth is `log₂ n` and each level costs `n`, so `T(n) = Θ(n log n)` — merge sort.

![[Complexity - Merge Sort Recursion Tree.excalidraw|800]]

### 6.2 Substitution (guess and verify by induction)

Guess `T(n) ≤ c·n log n`, substitute into the recurrence, and confirm the inequality holds for suitable `c` and `n₀`. Rigorous, but it requires a correct guess — usually obtained from a recursion tree first.

### 6.3 Recurrences worth memorising

| Recurrence | Solution | Algorithm |
|---|---|---|
| `T(n) = T(n−1) + O(1)` | `Θ(n)` | linear recursion, naive factorial |
| `T(n) = T(n−1) + O(n)` | `Θ(n²)` | quicksort worst case, selection sort |
| `T(n) = 2T(n−1) + O(1)` | `Θ(2ⁿ)` | Towers of Hanoi, subset enumeration |
| `T(n) = T(n/2) + O(1)` | `Θ(log n)` | binary search |
| `T(n) = T(n/2) + O(n)` | `Θ(n)` | quickselect (expected) |
| `T(n) = 2T(n/2) + O(1)` | `Θ(n)` | tree traversal, tree height |
| `T(n) = 2T(n/2) + O(n)` | `Θ(n log n)` | merge sort |
| `T(n) = 2T(n/2) + O(n log n)` | `Θ(n log² n)` | CDQ divide and conquer |
| `T(n) = 8T(n/2) + O(n²)` | `Θ(n³)` | naive matrix multiplication |
| `T(n) = 7T(n/2) + O(n²)` | `Θ(n^2.81)` | Strassen's algorithm |

> [!warning] `2T(n/2) + O(n)` vs `T(n/2) + O(n)`
> These differ by one recursive call — and by a whole log factor: `Θ(n log n)` vs `Θ(n)`. The second is a *geometric* series `n + n/2 + n/4 + … ≤ 2n`, which is exactly why quickselect finds the k-th element faster than sorting finds all of them.

---

## 7. The Master Theorem

For recurrences of the form

```
T(n) = a·T(n/b) + f(n),     a ≥ 1,  b > 1
```

compare `f(n)` against the "leaf work" `n^(log_b a)`:

| Case | Condition | Result |
|---|---|---|
| 1 | `f(n) = O(n^(log_b a − ε))` for some `ε > 0` | `T(n) = Θ(n^(log_b a))` — leaves dominate |
| 2 | `f(n) = Θ(n^(log_b a) · logᵏ n)`, `k ≥ 0` | `T(n) = Θ(n^(log_b a) · log^(k+1) n)` |
| 3 | `f(n) = Ω(n^(log_b a + ε))` **and** `a·f(n/b) ≤ c·f(n)` for some `c < 1` | `T(n) = Θ(f(n))` — root dominates |

![[Complexity - Master Theorem Cases.excalidraw|800]]

> [!example]- Worked applications
> - **Merge sort** — `a=2, b=2, f(n)=n`. `n^(log₂ 2) = n`, and `f(n) = Θ(n)` → Case 2 with `k=0` → `Θ(n log n)`.
> - **Binary search** — `a=1, b=2, f(n)=1`. `n^(log₂ 1) = n⁰ = 1` → Case 2 with `k=0` → `Θ(log n)`.
> - **Strassen** — `a=7, b=2, f(n)=n²`. `n^(log₂ 7) ≈ n^2.807` dominates `n²` → Case 1 → `Θ(n^2.807)`.
> - **Binary tree traversal** — `a=2, b=2, f(n)=1`. `n^(log₂ 2) = n` dominates `1` → Case 1 → `Θ(n)`.

> [!warning] When the Master Theorem does not apply
> - **Unequal splits**: `T(n) = T(n/3) + T(2n/3) + n` is not of the required form. Use a recursion tree — the answer is `Θ(n log n)`. (Akra–Bazzi generalizes to this case.)
> - **Subtractive recurrences**: `T(n) = T(n−1) + n` would need `b = 1`, which is disallowed.
> - **The "gap"**: `T(n) = 2T(n/2) + n/log n`. Here `f(n)` is smaller than `n` but not *polynomially* smaller, so no case applies. (The true answer is `Θ(n log log n)`.)
> - **Case 3's regularity condition** genuinely matters and must be checked, not assumed.

---

## 8. Amortized Analysis

<span class="hl-blue">Amortized complexity</span> is the average cost per operation over a **worst-case sequence** of operations. It is a guarantee, not a probabilistic statement — the distinction from "average case" matters.

### 8.1 Aggregate method — dynamic arrays

A dynamic array (`ArrayList`, C++ `vector`) doubles its capacity when full. A single `add` that triggers a resize costs `Θ(n)` — but resizes are rare. Starting from capacity 1, the total copying work over `n` appends is:

```
1 + 2 + 4 + 8 + … + n  <  2n      (geometric series)
```

Total `O(n)` over `n` operations ⇒ **`O(1)` amortized** per `add`, with `O(n)` worst case for any individual one.

![[Complexity - Amortized Doubling.excalidraw|800]]

> [!warning] The growth factor must be multiplicative
> If the array grew by a *constant* `+c` instead of doubling, the resize work would be `c + 2c + 3c + … ≈ n²/(2c)` → **`O(n)` amortized per operation**, quadratic overall. A growth factor greater than 1 is precisely what makes the series geometric.

> [!info]- Why shrinking uses a different threshold
> If a dynamic array shrank as soon as it fell to half full, alternating `add`/`remove` at the boundary would resize on *every* operation — "thrashing", `Θ(n)` per operation. The standard fix is to shrink only at one-quarter occupancy, leaving slack so that `Ω(n)` operations must occur between consecutive resizes.

### 8.2 Accounting (banker's) method

Charge each operation a fixed "price" above its real cost and store the surplus as credit on specific elements; expensive operations then spend saved credit. If the credit balance never goes negative, the charged price is a valid amortized bound. For dynamic arrays, charging 3 units per `add` — 1 to insert, 2 saved to pay for that element's eventual copy — covers all resizes.

### 8.3 Potential method

Define a potential function `Φ` on the structure's state. The amortized cost of operation `i` is `ĉᵢ = cᵢ + Φ(Dᵢ) − Φ(Dᵢ₋₁)`. Cheap operations build potential; expensive ones release it. This is the general technique behind splay trees and Fibonacci heaps.

### 8.4 Where amortized bounds appear

| Structure / algorithm | Amortized | Single-operation worst case |
|---|---|---|
| `ArrayList.add` (append) | `O(1)` | `O(n)` on resize |
| `HashMap.put` / `get` | `O(1)` | `O(n)` pre-Java 8; `O(log n)` from Java 8 (treeified bins) |
| Union-find (rank + path compression) | `O(α(n))` ≈ `O(1)` | `O(log n)` |
| Monotonic stack sweep | `O(1)` per element | `O(n)` for one step |
| Fibonacci heap `extract-min` | `O(log n)` | `O(n)` |

> [!warning] Amortized ≠ average ≠ expected
> - **Amortized** — worst-case sequence, guaranteed total. No assumptions at all.
> - **Average** — assumes a distribution over inputs.
> - **Expected** — randomness lives inside the algorithm.
>
> Amortized bounds are also unsafe for **real-time** requirements, since a single operation can still block for `Θ(n)`; and they break if the structure is **repeatedly copied or rolled back**, because each copy restarts the accounting.

---

## 9. Space Complexity

**Total space** = input space + auxiliary space. In practice, "space complexity" usually means <span class="hl-blue">auxiliary space</span>: memory used beyond the input itself.

### 9.1 The recursion call stack counts

```java
// Time O(n), auxiliary space O(n) — n stack frames
int sum(int[] a, int i) {
    if (i == a.length) return 0;
    return a[i] + sum(a, i + 1);
}

// Time O(n), auxiliary space O(1)
int sumIter(int[] a) {
    int s = 0;
    for (int x : a) s += x;
    return s;
}
```

Forgetting the call stack is the most common space-complexity error. **Recursion depth is memory.**

| Algorithm | Auxiliary space | Why |
|---|---|---|
| Merge sort (arrays) | `O(n)` | merge buffer |
| Quicksort | `O(log n)` average, `O(n)` worst | call stack depth only |
| Heap sort | `O(1)` | fully in-place |
| DFS on a graph | `O(V)` | stack + visited set |
| BFS on a graph | `O(V)` | the queue can hold an entire level |
| Recursion on a balanced BST | `O(log n)` | height |
| Recursion on a skewed BST | `O(n)` | height degenerates to `n` |

> [!tip] Java does not eliminate tail calls
> Even a tail-recursive method consumes one frame per call on the JVM, so deep recursion throws `StackOverflowError` at roughly 10⁴–10⁵ frames. A recursive solution over `n = 10⁶` must be converted to iteration with an explicit stack. See [[DSA/Foundations/Recursion|Recursion]].

### 9.2 "In-place" is a claim about auxiliary space

An algorithm is **in-place** if it uses `O(1)` auxiliary space. Note two wrinkles: quicksort is routinely called in-place despite its `O(log n)` stack, and Java's `String` immutability makes genuinely in-place string reversal impossible without dropping to `char[]` or `StringBuilder`.

---

## 10. Multi-Variable and Output-Sensitive Complexity

### 10.1 Graphs need two variables

BFS/DFS is `O(V + E)` — **not** `O(n)`, and not `O(V²)` in general.

- Sparse graph (`E ≈ V`): `O(V + E) = O(V)`.
- Dense graph (`E ≈ V²`): `O(V + E) = O(V²)`.

Dijkstra with a binary heap is `O((V + E) log V)`, usually written `O(E log V)` because `E ≥ V − 1` in a connected graph. Collapsing `V` and `E` into a single `n` hides exactly the distinction that decides between adjacency lists and adjacency matrices.

### 10.2 Output-sensitive complexity

When the *output* itself can be huge, the bound must include it. Enumerating every subset that sums to a target is `O(n · 2ⁿ)` because there can be exponentially many answers — no algorithm can beat the time needed merely to print them. Likewise "report all pairs within distance d" is `Ω(k)` for `k` reported pairs.

### 10.3 Complexity with memoization

A memoized recursion runs in:

```
O(number of distinct states × work per state)
```

**Not** `O(branching^depth)` — that is the *unmemoized* bound. Fibonacci with memoization is `O(n)` states × `O(1)` work = `O(n)`, down from `O(2ⁿ)`. This single formula is the whole of DP analysis; see [[DSA/Dynamic Programming Fundamentals|Dynamic Programming — Fundamentals]].

---

## 11. Complexity of Common Operations

### 11.1 Core structures

| Operation | Array | Dynamic array | Linked list | Hash table | Balanced BST | Binary heap |
|---|---|---|---|---|---|---|
| Access by index | `O(1)` | `O(1)` | `O(n)` | — | — | — |
| Search by value | `O(n)` | `O(n)` | `O(n)` | `O(1)` avg | `O(log n)` | `O(n)` |
| Insert at end | — | `O(1)` amort. | `O(1)` | `O(1)` avg | `O(log n)` | `O(log n)` |
| Insert at front | — | `O(n)` | `O(1)` | — | — | — |
| Delete by value | — | `O(n)` | `O(n)` incl. find | `O(1)` avg | `O(log n)` | `O(n)` |
| Find min / max | `O(n)` | `O(n)` | `O(n)` | `O(n)` | `O(log n)` | `O(1)` peek |
| Ordered iteration | `O(n log n)` | `O(n log n)` | `O(n log n)` | `O(n log n)` | `O(n)` | `O(n log n)` |

### 11.2 Java collections

| Class | Backing structure | Key costs |
|---|---|---|
| `ArrayList` | dynamic array | `get`/`set` `O(1)`; `add` `O(1)` amortized; `add(0,x)` / `remove(0)` `O(n)`; `contains` `O(n)` |
| `LinkedList` | doubly linked list | `addFirst`/`addLast`/`removeFirst`/`removeLast` `O(1)`; `get(i)` `O(n)` |
| `ArrayDeque` | circular buffer | both ends `O(1)` amortized; preferred over `Stack` and `LinkedList` |
| `HashMap` / `HashSet` | buckets, treeified when large | `O(1)` average; `O(log n)` worst per bucket since Java 8 |
| `LinkedHashMap` | hash + linked order | `O(1)` average, preserves insertion order |
| `TreeMap` / `TreeSet` | red-black tree | `get`/`put`/`remove`/`floor`/`ceiling`/`first`/`last` all `O(log n)` |
| `PriorityQueue` | binary heap | `offer`/`poll` `O(log n)`; `peek` `O(1)`; **`contains` / `remove(Object)` `O(n)`** |
| `StringBuilder` | dynamic `char[]` | `append` `O(1)` amortized; `toString` `O(n)` |

> [!warning] Traps hiding in the standard library
> - `list.contains(x)` inside a loop over `n` elements is `O(n²)` — use a `HashSet`.
> - `ArrayList.remove(0)` in a loop is `O(n²)` — use an `ArrayDeque`.
> - `PriorityQueue.remove(someObject)` is `O(n)`, not `O(log n)`: the heap has no index, so it scans. Lazy deletion is the standard workaround.
> - `String.substring` has been `O(n)` (a real copy) since Java 7; before that it shared the backing array in `O(1)`. Repeated substring calls in a loop are `O(n²)`.
> - A poor `hashCode()` (say, one returning a constant) degrades every `HashMap` operation toward `O(log n)` — and to `O(n)` if the keys are not `Comparable`.
> - Boxing matters: `HashMap<Integer,Integer>` is dramatically slower than an `int[]` when keys are bounded, even though both are "`O(1)`".

---

## 12. From Constraints to Target Complexity

Competitive-programming problems state `n`; the constraint tells you which complexity class is intended. Assuming roughly **10⁸ simple operations per second** in Java:

| `n` up to | Feasible complexity | Typical technique |
|---|---|---|
| 10–12 | `O(n!)` | permutations, brute force |
| 20–25 | `O(2ⁿ)`, `O(2ⁿ·n)` | subset enumeration, bitmask DP, meet in the middle |
| 100 | `O(n³)`, `O(n⁴)` | Floyd–Warshall, interval DP |
| 1,000–5,000 | `O(n²)` | 2D DP, all-pairs loops |
| 10⁵–10⁶ | `O(n log n)` | sorting, heaps, segment trees, binary search on the answer |
| 10⁶–10⁷ | `O(n)` | two pointers, prefix sums, counting |
| 10⁹–10¹⁸ | `O(log n)` or `O(1)` | binary exponentiation, closed-form math, matrix exponentiation |

<span class="hl-yellow">Reading the constraint first and deriving the target complexity from it is usually faster than inventing an algorithm and hoping it fits.</span>

> [!warning] Constant factors decide real submissions
> Two `O(n log n)` solutions are not interchangeable. A recursive segment tree with object allocation can be 5–10× slower than a Fenwick tree doing the same job. In Java specifically, `Scanner` is roughly an order of magnitude slower than `BufferedReader`, and boxing costs both time and memory. See [[DSA/Competitive Programming Toolkit|Competitive Programming Toolkit]].

---

## 13. Trick Questions and Special Cases

> [!question]- Is `O(2n)` faster than `O(n)`?
> They are the **same class** — constants are dropped. In wall-clock terms a particular `2n` implementation may well be twice as slow, but asymptotically the two statements are identical. `O(n/2)`, `O(3n + 7)`, and `O(n)` are all `Θ(n)`.

> [!question]- What is the complexity of a loop that runs 1,000,000 times regardless of input?
> `O(1)`. Complexity measures growth *as a function of `n`*. A fixed bound independent of the input is constant, however large it is.

> [!question]- Is `O(log n)` the same as `O(log n²)`?
> Yes: `log n² = 2 log n = O(log n)`. But `O(log² n)` — meaning `(log n)²` — is strictly larger. Where the exponent sits changes the answer.

> [!question]- Two sequential loops, each `O(n)` — is that `O(n²)`?
> No. `O(n) + O(n) = O(2n) = O(n)`. Sequential code **adds**; only nesting multiplies.

> [!question]- What is the complexity of building a heap from n elements?
> `O(n)`, not `O(n log n)`. Inserting one at a time is `O(n log n)`, but bottom-up `heapify` is `O(n)`, because most nodes sit near the leaves and sift down only a short distance — `Σ (n/2^(h+1))·h` converges to `O(n)`.

> [!question]- Is string concatenation in a loop `O(n)`?
> No — `O(n²)`. Java's `String` is immutable, so every `s += c` copies the whole accumulated string. `StringBuilder.append` is `O(1)` amortized, making the loop `O(n)`. See [[DSA/Strings|Strings]].

> [!question]- Why isn't trial division up to `√N` a polynomial-time primality test?
> `O(√N)` is polynomial in the *value* `N` but exponential in the input **size** `log N`: a 64-bit number is 64 bits of input but up to `2³²` divisors to try. This is the pseudo-polynomial distinction from §1.1.

> [!question]- Does adding memoization always reduce complexity?
> Only when subproblems actually overlap. Memoizing a recursion whose calls are all distinct — merge sort's halves, for instance — adds space and constant overhead while leaving time complexity unchanged.

> [!question]- Is hashing always `O(1)`?
> It is `O(1)` **expected**, assuming a good hash function. Adversarial keys that deliberately collide push Java 7's `HashMap` to `O(n)` per operation; Java 8+ treeifies large buckets, capping it at `O(log n)`. Anti-hash tests on Codeforces exploit exactly this, and the usual defence is a randomized hash seed.

> [!question]- Is `O(n log n)` always better than `O(n²)`?
> Asymptotically yes; for small `n`, no. Insertion sort beats merge sort below roughly 30–50 elements, which is why production sorts (TimSort, introsort) switch to insertion sort for small runs. Asymptotic superiority is a statement about large `n` only.

> [!question]- The inner loop runs fewer than n times — does that change the class?
> Only if it changes it *asymptotically*. `for (j = i+1; j < n; j++)` runs `n(n−1)/2` times in total: still `Θ(n²)`. But `for (j = 1; j < n; j *= 2)` runs `log n` times, which genuinely changes the class.

> [!question]- What is the complexity of `Collections.sort` on n strings of length L?
> `O(n·L·log n)`. Each comparison costs `O(L)`, not `O(1)`. The same caveat applies to sorting tuples, arrays, or any type whose comparison is not constant-time.

> [!question]- If a function is `O(n²)`, can it also be `O(n³)`?
> Yes — Big-O is an upper bound, and any valid upper bound can be loosened. It cannot also be `Θ(n³)`, however, because `Θ` is tight.

> [!question]- Does an early `return` improve the complexity?
> It improves the **best case**, not the worst case. Linear search with an early exit is `Θ(1)` best and `Θ(n)` worst — and worst case is what an unqualified complexity claim describes.

> [!question]- Recursion that makes 2 calls and halves the input — `O(log n)` or `O(n)`?
> `O(n)`. `T(n) = 2T(n/2) + O(1) = Θ(n)`. Only **one** recursive branch, as in binary search, yields `O(log n)`; two branches end up visiting every element.

> [!question]- What is the complexity of nested loops over an `r × c` matrix?
> `Θ(r·c)`. If `n` is defined as the *total number of cells*, that is `Θ(n)` — linear in the input size, not quadratic. The label depends entirely on what `n` was defined to be.

---

## 14. Quick Reference — Non-Obvious Outcomes

| Code / claim | Complexity | Why |
|---|---|---|
| `for (i = 1; i < n; i *= 2)` | `Θ(log n)` | multiplicative progress |
| `for (i=0;i<n;i++) for (j=i;j<n;j++)` | `Θ(n²)` | `n(n−1)/2` is still quadratic |
| `for (i=1;i<=n;i++) for (j=i;j<=n;j+=i)` | `Θ(n log n)` | harmonic series |
| `s += c` in a loop (`String`) | `Θ(n²)` | immutable copy each iteration |
| `sb.append(c)` in a loop | `Θ(n)` | `O(1)` amortized |
| `list.remove(0)` in a loop | `Θ(n²)` | shifts all elements |
| `list.contains(x)` in a loop | `Θ(n²)` | linear scan per call |
| `pq.remove(obj)` | `Θ(n)` | heap has no index; scans |
| Build heap via `heapify` | `Θ(n)` | not `n log n` |
| Build heap via `n` inserts | `Θ(n log n)` | — |
| BFS / DFS | `Θ(V + E)` | two variables, not one |
| Dijkstra (binary heap) | `Θ(E log V)` | — |
| Sorting `n` strings of length `L` | `Θ(n·L·log n)` | comparisons are not `O(1)` |
| Union-find, both optimizations | `Θ(α(n))` | effectively constant |
| Memoized recursion | states × work per state | not branching^depth |
| Trial-division primality | `Θ(√N)` | pseudo-polynomial in input bits |
| `T(n) = 2T(n/2) + O(n)` | `Θ(n log n)` | merge sort |
| `T(n) = T(n/2) + O(n)` | `Θ(n)` | geometric series, quickselect |
| `n log n` vs `n^1.1` | `n^1.1` is larger | true only in the limit |
| `O(log₂ n)` vs `O(log₁₀ n)` | identical | base is a constant factor |
| `O(2ⁿ)` vs `O(4ⁿ)` | different classes | exponent base is *not* a constant factor |

---

## 15. Summary

- Complexity describes **growth**, not runtime. Constants and low-order terms are discarded deliberately — that is both the method's power and its main blind spot.
- **O / Ω / Θ** bound a function from above, below, and tightly; **best / average / worst** select which input is analyzed. The two axes are independent, and conflating them ("Big-O means worst case") is the most common error in the topic.
- Analyze **total work over the whole execution**, not nesting depth — two pointers, sliding windows, and monotonic stacks all look quadratic and are not.
- **Recurrences** capture recursive cost: solve with a recursion tree, then confirm via the Master Theorem where it applies, remembering the cases where it does not (unequal splits, subtractive recurrences, the polynomial gap).
- **Amortized** bounds are worst-case guarantees over a sequence, distinct from average and expected. Geometric growth is what makes dynamic-array appends `O(1)` amortized.
- **Space includes the call stack.** Recursion depth is memory, and the JVM does not eliminate tail calls.
- Complexity may need **more than one variable** (`V` and `E`), and for numeric inputs the real input size is `log N` bits — the source of pseudo-polynomial bounds.
- In practice, **read the constraint first**, derive the target class from it, then pick an implementation whose constant factor also fits.
