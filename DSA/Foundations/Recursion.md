# Recursion

<span class="hl-blue">Recursion</span> is solving a problem by reducing it to **smaller instances of the same problem**, until the instance is small enough to answer directly. A recursive function calls itself on those smaller inputs and combines their answers.

Nearly every later chapter depends on it. Tree and graph traversals, divide and conquer, backtracking, and dynamic programming are all recursion with a particular shape. This note covers the mechanics (base cases, the call stack), how to analyze recursion (recursion trees), and the practical limits you hit in Java (no tail-call elimination, `StackOverflowError`, converting to iteration).

## Contents

- [[#1. Anatomy of a Recursive Function|1. Anatomy of a Recursive Function]]
- [[#2. The Call Stack|2. The Call Stack]]
- [[#3. Kinds of Recursion|3. Kinds of Recursion]]
- [[#4. Recursion Trees — Counting Calls and Depth|4. Recursion Trees — Counting Calls and Depth]]
- [[#5. Designing a Recursive Solution|5. Designing a Recursive Solution]]
- [[#6. Classic Examples|6. Classic Examples]]
- [[#7. Tail Recursion|7. Tail Recursion]]
- [[#8. Converting Recursion to Iteration|8. Converting Recursion to Iteration]]
- [[#9. Stack Overflow Limits in Java|9. Stack Overflow Limits in Java]]
- [[#10. From Recursion to Memoization|10. From Recursion to Memoization]]
- [[#11. Common Mistakes|11. Common Mistakes]]
- [[#12. Trick Questions and Special Cases|12. Trick Questions and Special Cases]]
- [[#13. Quick Reference — Non-Obvious Outcomes|13. Quick Reference — Non-Obvious Outcomes]]
- [[#14. Summary|14. Summary]]

---

## 1. Anatomy of a Recursive Function

> [!note] Definition
> A recursive function has two kinds of branch:
> 1. <span class="hl-blue">Base case(s)</span>: inputs answered **directly**, without a recursive call.
> 2. <span class="hl-blue">Recursive case(s)</span>: inputs answered by calling the function on **strictly smaller** inputs and combining the results.

> [!important] The three requirements for correctness
> 1. **Every input eventually reaches a base case.** Each call must make *progress*: the input gets smaller by some measure (a number decreases, an array range shrinks, a tree node moves toward the leaves).
> 2. **The base cases are correct.**
> 3. **The combine step is correct, assuming the recursive calls are correct.**
>
> This is proof by induction: base cases are the base step, and requirement 3 is the inductive step.

### 1.1 The "recursive leap of faith"

When writing the recursive case, **do not trace the recursion in your head**. Assume the call on the smaller input already returns the right answer, and ask only: *given that answer, how do I build the answer for the current input?* Tracing is for debugging, not design. Point 3 above is exactly this assumption, and induction is what makes it safe.

### 1.2 Example: factorial

```
factorial(n):
    if n ≤ 1:                      -- base case
        return 1
    return n × factorial(n − 1)    -- recursive case: smaller input, then combine
```

```java
static long factorial(int n) {
    if (n <= 1) return 1;              // base case (also guards n = 0 and negatives)
    return n * factorial(n - 1);       // recursive case
}
```

> [!tip] Guard with `<=`, not `==`
> A base case `if (n == 0)` gives infinite recursion (and then `StackOverflowError`) on a negative input, and on inputs that skip over 0 (e.g. recursing on `n − 2` from an odd `n`). Write `n <= 0` or `n <= 1` unless there's a reason not to.

---

## 2. The Call Stack

Each call to a method creates a <span class="hl-blue">stack frame</span> holding its parameters, local variables, and the **return address** (where to resume in the caller). Frames are pushed on call and popped on return, so the most recent call always finishes first (LIFO). The Java-level mechanics are in [[Java/Program Structure/Methods#6.2 The Call Stack|Methods § 6.2]].

A recursive call is not special: it's an ordinary call that happens to target the same method. Every active call has **its own frame and its own copy of `n`**.

### 2.1 Trace: `factorial(4)`

| Step | Event | Stack (bottom → top) | Value produced |
|---|---|---|---|
| 1 | call `factorial(4)` | `f(4)` | — |
| 2 | call `factorial(3)` | `f(4) f(3)` | — |
| 3 | call `factorial(2)` | `f(4) f(3) f(2)` | — |
| 4 | call `factorial(1)` | `f(4) f(3) f(2) f(1)` | — |
| 5 | base case returns | `f(4) f(3) f(2)` | `1` |
| 6 | `2 × 1` returns | `f(4) f(3)` | `2` |
| 7 | `3 × 2` returns | `f(4)` | `6` |
| 8 | `4 × 6` returns | (empty) | `24` |

The recursion has two phases: <span class="hl-blue">winding</span> (steps 1–4, pushing frames on the way down) and <span class="hl-blue">unwinding</span> (steps 5–8, returning and combining on the way back up). The multiplications all happen during unwinding. That's why this version is *not* tail-recursive ([[#7. Tail Recursion|§7]]).

### 2.2 Work before vs. after the call decides the order

```java
static void down(int n) {       // prints 3 2 1
    if (n == 0) return;
    System.out.print(n + " ");  // before the call → runs while winding
    down(n - 1);
}

static void up(int n) {         // prints 1 2 3
    if (n == 0) return;
    up(n - 1);
    System.out.print(n + " ");  // after the call → runs while unwinding
}

static void both(int n) {       // prints 3 2 1 1 2 3
    if (n == 0) return;
    System.out.print(n + " ");
    both(n - 1);
    System.out.print(n + " ");
}
```

<span class="hl-yellow">Code before the recursive call runs top-down; code after it runs bottom-up, in reverse order.</span> This is the whole difference between preorder and postorder tree traversal, and it's also how recursion reverses things (print a linked list backwards, reverse a string).

### 2.3 Space cost = maximum depth, not number of calls

Only the frames on the **current path** from the first call exist at once. A call's frame is gone before its sibling call starts. So:

- **Time** ∝ total number of calls × work per call.
- **Space** ∝ maximum depth × frame size.

Naive Fibonacci makes `Θ(φⁿ)` calls but uses only `Θ(n)` stack space, because the deepest path is `fib(n) → fib(n−1) → … → fib(1)`.

---

## 3. Kinds of Recursion

| Kind | Shape | Example | Calls | Depth |
|---|---|---|---|---|
| **Linear** | one recursive call per invocation | factorial, sum of list | `n` | `n` |
| **Binary / tree** | two or more calls per invocation | Fibonacci, tree traversal, merge sort | often exponential, or `n` for trees | `n` or `log n` |
| **Tail** | the recursive call is the *last* action; its result is returned unchanged | `gcd(b, a % b)` | as linear | as linear (in Java) |
| **Head** | the recursive call comes *first*, work happens after | `up(n)` above | as linear | as linear |
| **Mutual (indirect)** | `A` calls `B`, `B` calls `A` | `isEven`/`isOdd`, recursive-descent parsers | — | — |
| **Nested** | an argument of the recursive call is itself a recursive call | Ackermann, McCarthy 91 | can be enormous | — |

```java
// Mutual recursion: each function makes progress on behalf of the other
static boolean isEven(int n) { return n == 0 || isOdd(n - 1); }
static boolean isOdd(int n)  { return n != 0 && isEven(n - 1); }
```

> [!info]- Nested recursion — the McCarthy 91 function
> ```
> M(n):
>     if n > 100: return n − 10
>     return M(M(n + 11))
> ```
> It returns `91` for **every** `n ≤ 101`, and `n − 10` above that. Nothing about the definition suggests that, which is the point. Nested recursion is hard to reason about, and termination is not obvious. The Ackermann function `A(m, n)` is nested too. It always terminates, but `A(4, 2)` already has 19,729 decimal digits, and it can't be written with bounded `for` loops alone (it is not *primitive recursive*).

---

## 4. Recursion Trees — Counting Calls and Depth

A <span class="hl-blue">recursion tree</span> draws each call as a node, with its recursive calls as children. Two numbers come straight off it:

- **Total time** = sum of the non-recursive work over all nodes.
- **Stack space** = height of the tree (longest root-to-leaf path).

### 4.1 Naive Fibonacci

```
fib(n):
    if n ≤ 1: return n
    return fib(n − 1) + fib(n − 2)
```

```
                    fib(4)
                 /          \
            fib(3)            fib(2)
           /      \          /      \
       fib(2)    fib(1)   fib(1)   fib(0)
      /      \
  fib(1)   fib(0)
```

9 calls for `n = 4`. `fib(2)` is computed twice, `fib(1)` three times: the same subproblems are solved over and over (<span class="hl-blue">overlapping subproblems</span>). The number of calls satisfies `C(n) = C(n−1) + C(n−2) + 1`, which solves to exactly **`C(n) = 2·F(n+1) − 1`**. That's `Θ(φⁿ)` with `φ ≈ 1.618`, and `fib(50)` takes about 4 × 10¹⁰ calls.

| Quantity | Naive Fibonacci |
|---|---|
| Calls | `2·F(n+1) − 1 = Θ(φⁿ)` |
| Time | `Θ(φⁿ)`, usually quoted as `O(2ⁿ)` (a valid but loose upper bound) |
| Stack depth | `n` |
| Space | `Θ(n)` |

### 4.2 Reading the shape

| Branching `b`, depth `d`, work per call `O(1)` | Calls |
|---|---|
| `b = 1` (linear) | `d` |
| `b = 2`, input shrinks by 1 (`T(n−1)` twice) | `2ᵈ = 2ⁿ` |
| `b = 2`, input halves (`T(n/2)` twice) | `2^(log₂ n) = n` |
| `b = 1`, input halves (binary search) | `log₂ n` |

The general tool for recurrences like `T(n) = a·T(n/b) + f(n)` is the Master Theorem. See [[DSA/Foundations/Complexity Analysis#6. Recurrence Relations|Complexity Analysis § 6–7]].

---

## 5. Designing a Recursive Solution

1. **State the function's contract precisely.** What does `solve(args)` return, in words? Most broken recursions come from a vague contract. For example, "`height(node)` = number of **edges** on the longest downward path" and "number of **nodes**" give different base cases.
2. **Choose what shrinks.** Common options: `n → n−1`, a range `[lo, hi]` → half of it, a node → its children, an index `i → i+1` through an array.
3. **Write the base case(s)** for the smallest inputs. Check that *every* chain of shrinking hits one.
4. **Write the recursive case** using the leap of faith ([[#1.1 The "recursive leap of faith"|§1.1]]).
5. **Check the cost**: count the calls, check the depth, and see whether subproblems repeat (if they do, memoize, [[#10. From Recursion to Memoization|§10]]).

### 5.1 Helper functions with extra parameters

The public signature often doesn't carry enough state. The standard fix is a private helper with extra parameters: an index, a range, an accumulator, or the partial answer built so far.

```java
// Public API: isPalindrome(s). Helper: works on the index range [lo, hi].
static boolean isPalindrome(String s) {
    return isPal(s, 0, s.length() - 1);
}

private static boolean isPal(String s, int lo, int hi) {
    if (lo >= hi) return true;                           // 0 or 1 characters left
    if (s.charAt(lo) != s.charAt(hi)) return false;
    return isPal(s, lo + 1, hi - 1);
}
```

> [!warning] Pass indices, not substrings
> `isPal(s.substring(1, s.length() - 1))` looks cleaner, but every `substring` copies the string (since Java 7). That makes the recursion `Θ(n²)` time and `Θ(n²)` total allocation instead of `Θ(n)`. The same goes for `Arrays.copyOfRange` or `list.subList(...)` copies passed down. Pass the original plus bounds.

---

## 6. Classic Examples

### 6.1 Fast power (halving)

```
power(x, n):                 -- n ≥ 0
    if n == 0: return 1
    half = power(x, n / 2)   -- compute ONCE
    if n is even: return half × half
    else:         return half × half × x
```

```java
static double myPow(double x, int n) {
    long N = n;                      // widen FIRST: -Integer.MIN_VALUE overflows int
    if (N < 0) { x = 1 / x; N = -N; }
    return pow(x, N);
}

private static double pow(double x, long n) {
    if (n == 0) return 1.0;
    double half = pow(x, n / 2);
    return (n % 2 == 0) ? half * half : half * half * x;
}
```

`T(n) = T(n/2) + O(1)` → `Θ(log n)` time and `Θ(log n)` stack. The modular version used in number theory is in [[DSA/Foundations/Math for Algorithms#4. Fast (Binary) Exponentiation|Math for Algorithms § 4]].

> [!warning] Two classic bugs in this one function
> - `return pow(x, n/2) * pow(x, n/2);` makes **two** calls: `T(n) = 2T(n/2) + O(1) = Θ(n)`. All the benefit of halving is gone. Store the result in `half`.
> - `n = Integer.MIN_VALUE`: `-n` is still `Integer.MIN_VALUE` (negative), so `if (n < 0) return 1 / pow(x, -n)` recurses forever. Widen to `long` before negating.

### 6.2 Towers of Hanoi

Move `n` disks from peg `from` to peg `to` using `via`, never placing a larger disk on a smaller one.

```
hanoi(n, from, to, via):
    if n == 0: return
    hanoi(n − 1, from, via, to)     -- clear the n−1 smaller disks out of the way
    move disk n: from → to
    hanoi(n − 1, via, to, from)     -- put them back on top of disk n
```

```java
static void hanoi(int n, char from, char to, char via, List<String> moves) {
    if (n == 0) return;
    hanoi(n - 1, from, via, to, moves);
    moves.add("disk " + n + ": " + from + " -> " + to);
    hanoi(n - 1, via, to, from, moves);
}
```

`T(n) = 2T(n−1) + 1` → exactly **`2ⁿ − 1` moves**, which is also the proven minimum. Depth is only `n`.

### 6.3 Generating all subsets (include / exclude)

```
subsets(a, i, current, result):
    if i == len(a):
        result.add(copy of current)
        return
    subsets(a, i + 1, current, result)          -- exclude a[i]
    current.push(a[i])
    subsets(a, i + 1, current, result)          -- include a[i]
    current.pop()                               -- undo: restore state for the caller
```

```java
static List<List<Integer>> subsets(int[] a) {
    List<List<Integer>> result = new ArrayList<>();
    build(a, 0, new ArrayList<>(), result);
    return result;
}

private static void build(int[] a, int i, List<Integer> current, List<List<Integer>> result) {
    if (i == a.length) {
        result.add(new ArrayList<>(current));   // COPY: current keeps changing
        return;
    }
    build(a, i + 1, current, result);
    current.add(a[i]);
    build(a, i + 1, current, result);
    current.remove(current.size() - 1);         // undo
}
```

`2ⁿ` leaves, each copying up to `n` elements → `Θ(n · 2ⁿ)` time, depth `n`. This "choose, recurse, un-choose" shape is the core of [[DSA/Backtracking|Backtracking]]. The same subsets can be generated without recursion using bitmasks, see [[DSA/Foundations/Bit Manipulation#7. Bitmasks as Sets|Bit Manipulation § 7]].

> [!warning] `result.add(current)` without copying
> This adds a **reference** to the one shared list. When the recursion finishes, the undo steps have emptied it, so `result` holds `2ⁿ` references to the same empty list. Always add `new ArrayList<>(current)`.

### 6.4 Recursion over data structures

Recursive data structures (linked lists, trees) have recursive algorithms built in: "a list is empty, or a node followed by a list"; "a tree is empty, or a node with two subtrees".

```java
// Height in nodes: empty tree = 0
static int height(TreeNode node) {
    if (node == null) return 0;
    return 1 + Math.max(height(node.left), height(node.right));
}
```

Depth equals the tree's height: `O(log n)` if balanced, but **`O(n)` for a degenerate (path-shaped) tree**. That's often enough to overflow the stack at `n = 10⁵`. See [[DSA/Binary Trees|Binary Trees]] and [[DSA/Linked Lists|Linked Lists]].

---

## 7. Tail Recursion

> [!note] Definition
> A call is a <span class="hl-blue">tail call</span> if it's the **last thing** the function does: its result is returned directly, with no pending work. A function whose recursive calls are all tail calls is <span class="hl-blue">tail-recursive</span>.

```java
// NOT tail-recursive: the multiplication happens AFTER the call returns
static long fact(int n) {
    if (n <= 1) return 1;
    return n * fact(n - 1);
}

// Tail-recursive: the pending work is carried forward in an accumulator
static long factTail(int n, long acc) {       // call as factTail(n, 1)
    if (n <= 1) return acc;
    return factTail(n - 1, n * acc);
}
```

When a call is in tail position, the caller's frame is no longer needed. A compiler can **reuse** it, turning the recursion into a jump, and stack use becomes `O(1)`. This is <span class="hl-blue">tail-call optimization (TCO)</span>.

> [!warning] Java does NOT perform tail-call optimization
> Neither `javac` nor the HotSpot JIT eliminates tail calls (among other reasons, the JVM's security model and stack traces rely on frames existing). `factTail(100_000, 1)` throws `StackOverflowError` just like `fact`. In Java, a tail-recursive method is **just as deep** as a non-tail-recursive one. Its advantage is that it converts to a loop mechanically ([[#8.1 Tail recursion → a loop (mechanical)|§8.1]]). Scala (`@tailrec`), Kotlin (`tailrec`), and Scheme do eliminate tail calls; C/C++ compilers usually do at `-O2` but don't guarantee it.

> [!info]- The accumulator transformation
> To make a linear recursion tail-recursive, find the pending operation (`n × _`), add a parameter that accumulates it, and apply it *before* the call instead of after. This only works directly when the combine operation is associative (like `×`, `+`, `max`). A recursion with two calls (like Fibonacci) can't be made tail-recursive this way without extra state. For Fibonacci you carry *two* accumulators: `fibTail(n, a, b) = fibTail(n−1, b, a+b)`, which is the iterative algorithm in disguise.

---

## 8. Converting Recursion to Iteration

<span class="hl-yellow">Every recursion can be turned into iteration.</span> The call stack is just a stack, and you can manage one yourself. You'd do this in Java when the depth might exceed the stack limit ([[#9. Stack Overflow Limits in Java|§9]]).

### 8.1 Tail recursion → a loop (mechanical)

The recursive call "restarts the function with new arguments", so reassign the parameters and loop.

```
gcd(a, b):                         gcd(a, b):
    if b == 0: return a      ⇒         while b ≠ 0:
    return gcd(b, a mod b)                 (a, b) = (b, a mod b)
                                       return a
```

```java
static long gcdIter(long a, long b) {
    while (b != 0) {
        long t = a % b;
        a = b;
        b = t;
    }
    return a;
}
```

### 8.2 General recursion → an explicit stack

A frame is *(parameters, locals, where to resume)*. Put that state in an object, push it on an `ArrayDeque`, and loop until the stack is empty.

> [!important] Push in reverse order
> A stack pops the **last** thing pushed first. If the recursive version does `A; B; C`, push `C`, then `B`, then `A`.

**Hanoi with an explicit stack.** Each frame is either "solve `hanoi(n, from, to, via)`" or "perform this one move":

```
push Solve(n, from, to, via)
while stack not empty:
    f = pop
    if f is Move: output the move; continue
    if f.n == 0: continue
    push Solve(f.n − 1, f.via, f.to, f.from)   -- runs third
    push Move(f.n, f.from, f.to)               -- runs second
    push Solve(f.n − 1, f.from, f.via, f.to)   -- runs first
```

```java
static void hanoiIter(int n, char from, char to, char via, List<String> moves) {
    Deque<int[]> stack = new ArrayDeque<>();
    stack.push(new int[]{n, from, to, via, 0});      // last field: 0 = solve, 1 = move
    while (!stack.isEmpty()) {
        int[] f = stack.pop();
        if (f[4] == 1) {
            moves.add("disk " + f[0] + ": " + (char) f[1] + " -> " + (char) f[2]);
            continue;
        }
        if (f[0] == 0) continue;
        stack.push(new int[]{f[0] - 1, f[3], f[2], f[1], 0});  // hanoi(n-1, via, to, from)
        stack.push(new int[]{f[0], f[1], f[2], f[3], 1});      // move disk n
        stack.push(new int[]{f[0] - 1, f[1], f[3], f[2], 0});  // hanoi(n-1, from, via, to)
    }
}
```

It produces the same move sequence as the recursive version.

### 8.3 Post-processing without recursion: reverse preorder

A very common case: a recursive DFS on a tree computes something **after** visiting the children (subtree sizes, subtree sums, tree DP). The easiest iterative version doesn't simulate frames at all:

1. Do an iterative DFS and record the **order** in which nodes are first visited, plus each node's parent.
2. Process the nodes in **reverse** of that order. Every node's children appear after it in the visiting order, so they're processed before it.

```
order = []; parent[root] = −1
push root
while stack not empty:
    u = pop; order.append(u)
    for v in adj[u]:
        if v ≠ parent[u]: parent[v] = u; push v
for u in reverse(order):
    size[u] += 1                              -- u itself; children already added theirs
    if parent[u] ≠ −1: size[parent[u]] += size[u]
```

```java
// Subtree sizes of a tree given as an adjacency list, no recursion (safe for n = 10^6)
static int[] subtreeSizes(List<Integer>[] adj, int root) {
    int n = adj.length;
    int[] parent = new int[n], order = new int[n], size = new int[n];
    int cnt = 0;
    Deque<Integer> stack = new ArrayDeque<>();
    parent[root] = -1;
    stack.push(root);
    while (!stack.isEmpty()) {
        int u = stack.pop();
        order[cnt++] = u;
        for (int v : adj[u]) {
            if (v != parent[u]) {
                parent[v] = u;
                stack.push(v);
            }
        }
    }
    for (int i = cnt - 1; i >= 0; i--) {
        int u = order[i];
        size[u] += 1;
        if (parent[u] != -1) size[parent[u]] += size[u];
    }
    return size;
}
```

> [!info]- When you need a true "resume point"
> If the combine step needs to run *between* children (inorder traversal), or on a general graph where the tree trick doesn't apply, store a **stage** (or a child-iterator index) in each frame. Peek the top frame; if it still has children left, advance its index and push the next child; otherwise pop it and do its post-work. This is how iterative inorder/postorder traversal and iterative Tarjan's SCC are written. See [[DSA/Binary Trees|Binary Trees]] and [[DSA/Graph Connectivity|Graph Connectivity]].

> [!warning] An iterative DFS is not automatically the same traversal
> Pushing all neighbours and marking them visited **at push time** gives an order that isn't a real DFS order. It's fine for reachability and connected components, but wrong for anything that relies on DFS structure (discovery/finish times, low-link values, topological order by finish time). Mark visited **when popped**, or use the stage-based frame. See [[DSA/Graph Representations and Traversals|Graph Representations and Traversals]].

---

## 9. Stack Overflow Limits in Java

Each thread has a fixed-size stack, typically **512 KB–1 MB** on 64-bit JVMs (1 MB by default on common desktop/server platforms). When it fills up, the JVM throws `java.lang.StackOverflowError`.

| Frame content | Rough max depth with a 1 MB stack |
|---|---|
| a couple of `int` parameters | ~10,000–50,000 |
| many parameters / locals | a few thousand |

These numbers vary with JIT state, platform, and frame size, and they're **not** something to rely on. The practical rule:

<span class="hl-yellow">Depth ≤ ~10⁴ is safe. Depth ~10⁵ is a coin flip. Depth ≥ 10⁶ will overflow.</span> Recursion depth equals `n` for a linear recursion, a path-shaped tree, a linked list, or a DFS on a long chain or a large grid (a 1000×1000 flood fill can go 10⁶ deep).

### 9.1 Fixes, in order of preference

1. **Reduce the depth.** Recurse on the smaller half and loop on the larger one (quicksort, [[#12. Trick Questions and Special Cases|§12]]); use a balanced structure.
2. **Convert to iteration** ([[#8. Converting Recursion to Iteration|§8]]).
3. **Run the recursion in a thread with a bigger stack.** This is the standard competitive-programming trick:

```java
public static void main(String[] args) throws InterruptedException {
    Thread t = new Thread(null, () -> solve(), "solver", 1L << 28);  // 256 MB stack
    t.start();
    t.join();
}
```

The stack-size argument is only a *hint* (the Javadoc allows a JVM to ignore it), but it's honoured on the usual judges (Codeforces, AtCoder). The stack memory counts toward the memory limit. The `-Xss` JVM flag does the same thing for all threads, but you can't pass flags to an online judge.

> [!warning] Don't catch `StackOverflowError`
> It's an `Error`, not an `Exception`. Catching it to "detect deep input" leaves the program in an unreliable state (the overflow can hit inside library code, class initialisation, or a `finally` block). Fix the depth instead.

---

## 10. From Recursion to Memoization

When the recursion tree has **repeated subproblems** (§4.1), cache each answer the first time you compute it. This is <span class="hl-blue">memoization</span>, and it's top-down dynamic programming.

```
memo = table initialised to "unknown"
fib(n):
    if n ≤ 1: return n
    if memo[n] known: return memo[n]
    memo[n] = fib(n − 1) + fib(n − 2)
    return memo[n]
```

```java
static long[] memo;

static long fibMemo(int n) {
    if (n <= 1) return n;
    if (memo[n] != -1) return memo[n];        // -1 = "not computed" (0 is a valid answer for n = 0)
    return memo[n] = fibMemo(n - 1) + fibMemo(n - 2);
}
// setup: memo = new long[n + 1]; Arrays.fill(memo, -1);
```

Time drops from `Θ(φⁿ)` to `Θ(n)` (number of distinct states × work per state), stack depth stays `n`. The full treatment (state design, tabulation, space optimisation) is in [[DSA/Dynamic Programming Fundamentals|Dynamic Programming — Fundamentals]].

> [!warning] Memoization pitfalls
> - **The sentinel must not be a valid answer.** Using `0` as "not computed" makes every state whose true answer is 0 get recomputed, which can quietly bring back exponential time.
> - **A shared memo across test cases** gives wrong answers if the memoized function depends on per-test input. Reset it (or allocate it) per test.
> - **Overflow:** `fib(92)` is the last Fibonacci number that fits in a `long`. `fib(47)` already overflows `int`.
> - Memoization doesn't reduce **depth**: `fibMemo(100_000)` still overflows the stack. Tabulate bottom-up instead.

---

## 11. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Missing or unreachable base case | `StackOverflowError` | Every chain of calls must hit a base case. Use `n <= 0`, not `n == 0`. |
| No progress (`f(n)` calls `f(n)`) | `StackOverflowError` | Each call must shrink the input |
| `f(n--)` instead of `f(n - 1)` | infinite recursion | `n--` passes the **old** value |
| Forgetting to `return` the recursive result | wrong answer / compile error | `return f(n - 1);`, not `f(n - 1);` |
| Calling the same subproblem twice instead of storing it | exponential time | `half = f(n/2); return half * half;` |
| Adding a shared mutable list to the result | all results identical/empty | add a copy |
| Forgetting to undo state after the call | later branches see stale state | choose → recurse → un-choose |
| Passing `substring` / copies down | hidden `Θ(n²)` | pass indices |
| Static/global state not reset between test cases | wrong answers on test 2+ | reset in `solve()` |
| Assuming tail recursion saves stack in Java | `StackOverflowError` | convert to a loop |
| Deep recursion on `n ≥ 10⁵` | `StackOverflowError` | iterate, or use a big-stack thread |

---

## 12. Trick Questions and Special Cases

> [!question]- What is the space complexity of naive recursive Fibonacci?
> `Θ(n)`, not `Θ(2ⁿ)`. Only one root-to-leaf path of frames exists at a time, and the longest path has length `n`. Time is exponential, space is linear.

> [!question]- Is naive Fibonacci Θ(2ⁿ)?
> No. It's `Θ(φⁿ)` with `φ ≈ 1.618`; the exact call count is `2·F(n+1) − 1`. `O(2ⁿ)` is a correct upper bound but not tight. `Θ(2ⁿ)` is false, because `φⁿ/2ⁿ → 0`.

> [!question]- `return f(n-1) + f(n-1);` vs. `int x = f(n-1); return x + x;`
> Same value, very different cost. The first makes two calls: `T(n) = 2T(n−1) + 1 = Θ(2ⁿ)`. The second makes one: `Θ(n)`. The same applies to fast power with `pow(x, n/2) * pow(x, n/2)`, which gives `Θ(n)` instead of `Θ(log n)`.

> [!question]- What does this print for n = 3?
> ```java
> static void g(int n) {
>     if (n <= 0) return;
>     g(n - 1);
>     System.out.print(n + " ");
>     g(n - 1);
> }
> ```
> `1 2 1 3 1 2 1`. It's an inorder walk of a complete binary recursion tree: `2ⁿ − 1` numbers printed (the "ruler sequence"), the same shape as the Hanoi move order.

> [!question]- Why does `return f(n--);` never terminate?
> Post-decrement evaluates to the **old** value of `n`, so `f` is called with the same `n` forever (the decrement happens to this frame's local copy, which is never used again). `f(--n)` would pass `n − 1` but also changes the local `n`, which breaks any code after the call that uses `n`. Write `f(n - 1)`.

> [!question]- Does making a function tail-recursive prevent StackOverflowError in Java?
> No. The JVM doesn't eliminate tail calls, so a tail-recursive method uses one frame per call, just like any other. The benefit in Java is that tail recursion converts to a `while` loop mechanically.

> [!question]- Is `return n * fact(n - 1);` a tail call?
> No. The multiplication happens *after* `fact(n − 1)` returns, so the frame must stay alive to finish it. A tail call's result is returned **unchanged**: `return fact(n − 1, n * acc);`.

> [!question]- Recursive vs. iterative binary search: same complexity?
> Same time `Θ(log n)`, different space: recursive uses `Θ(log n)` stack, iterative uses `Θ(1)`. The recursive one is tail-recursive, so it converts directly into the loop.

> [!question]- Quicksort's worst-case recursion depth is n. Can you bound it to O(log n) without changing the pivot rule?
> Yes. After partitioning, **recurse into the smaller part and loop on the larger part** (the tail call becomes a loop). Each recursive call handles at most half the current range, so depth is `≤ log₂ n` even when time degrades to `Θ(n²)`.

> [!question]- `myPow(2.0, Integer.MIN_VALUE)` — why might it overflow the stack?
> A typical `if (n < 0) return 1 / pow(x, -n);` computes `-Integer.MIN_VALUE`, which overflows back to `Integer.MIN_VALUE`, so `n` is still negative and the call repeats forever. Convert to `long` before negating.

> [!question]- Can every recursive algorithm be written iteratively? And vice versa?
> Yes to both. A recursion can always be simulated with an explicit stack ([[#8.2 General recursion → an explicit stack|§8.2]]), and any loop can be rewritten as tail recursion. What differs is convenience and, in Java, the stack limit. Some recursions (like Ackermann) can't be written with bounded `for` loops alone, but they can with a `while` loop and an explicit stack.

> [!question]- Does the order of the two recursive calls in `fib(n-1) + fib(n-2)` affect complexity?
> Not without memoization, since both orders compute the same tree. With memoization, `fib(n-1)` first is better: it fills in `fib(n-2)`, so the second call becomes an `O(1)` lookup. Calling `fib(n-2)` first still gives `O(n)` total, but with more real recursion. Either way, the depth is `n`.

> [!question]- A recursive DFS on a 1000 × 1000 grid — what can go wrong?
> The recursion depth can reach the number of cells, 10⁶ (for example, a snake-shaped open region). That will overflow the default stack. Use an explicit stack, BFS, or a big-stack thread.

> [!question]- What does `isEven(-1)` do with the mutual recursion in §3?
> It never reaches `n == 0` (it goes `-1, -2, -3, …`) and ends in `StackOverflowError`. Mutual recursion needs the same "every input reaches a base case" check as direct recursion, and it's easier to miss because the progress is split across two functions.

> [!question]- Memoized recursion on n = 10⁶ states — is it safe?
> The time is fine, but the depth can be `10⁶`, since the first call chain goes straight down to the base case before anything is cached. Either tabulate bottom-up, or warm the memo from small `n` upward so each call only recurses one level deep.

> [!question]- Recursion with two branches that halve the input — how many calls?
> `T(n) = 2T(n/2) + O(1)` gives `Θ(n)` calls, not `Θ(log n)`. Only a **single** halving branch (binary search) gives `log n`. Depth is `log n` in both cases.

---

## 13. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| Naive `fib(n)` calls | `2·F(n+1) − 1` | `C(n) = C(n−1) + C(n−2) + 1` |
| Naive `fib(n)` space | `Θ(n)` | only one path of frames is live |
| `f(n-1) + f(n-1)` | `Θ(2ⁿ)` | two calls, not one |
| `x = f(n-1); x + x` | `Θ(n)` | one call |
| `pow(x,n/2) * pow(x,n/2)` | `Θ(n)` | two halving calls |
| `half = pow(x,n/2); half*half` | `Θ(log n)` | one halving call |
| Hanoi, `n` disks | `2ⁿ − 1` moves, depth `n` | `T(n) = 2T(n−1) + 1` |
| Subsets via include/exclude | `Θ(n·2ⁿ)` time, depth `n` | `2ⁿ` leaves, copy each |
| `return n * f(n-1)` | not a tail call | multiplication pending |
| Tail recursion in Java | still `Θ(depth)` stack | no TCO on the JVM |
| `f(n--)` | infinite recursion | passes old value |
| Base case `n == 0`, input `-1` | `StackOverflowError` | never hits 0 |
| `substring` passed down | `Θ(n²)` | each call copies |
| `result.add(current)` | all entries the same list | reference, not copy |
| Quicksort, smaller side first | depth `≤ log₂ n` | larger side becomes a loop |
| Default Java stack | ~10⁴–10⁵ frames | platform and frame-size dependent |
| `new Thread(null, r, "", 1L<<28)` | 256 MB stack | standard CP workaround |

---

## 14. Summary

- A recursive function needs **base cases**, **progress** toward them on every input, and a **combine** step that's correct assuming the smaller calls are. That's induction.
- Each call has its **own frame**. Work before the call runs top-down (winding); work after it runs bottom-up in reverse (unwinding).
- **Time ∝ number of calls; space ∝ maximum depth.** Draw the recursion tree to get both.
- Repeated subproblems in the tree are the signal to **memoize**, which is top-down DP.
- **Tail recursion** leaves no pending work, but **Java doesn't optimize it**. Its value in Java is that it converts mechanically to a loop.
- Any recursion converts to iteration with an **explicit stack** (push in reverse order). For tree DP, "reverse preorder" avoids frame simulation entirely.
- Java's stack handles roughly **10⁴** frames safely. For deeper recursion, iterate, reduce depth, or run in a thread with a large stack.

## Related

- [[DSA/Syllabus|Syllabus]]
- Previous: [[DSA/Foundations/Complexity Analysis|Complexity Analysis]] · Next: [[DSA/Foundations/Bit Manipulation|Bit Manipulation]]
- [[DSA/Foundations/Complexity Analysis#6. Recurrence Relations|Complexity Analysis § 6–7]]: solving recurrences, the Master Theorem
- [[Java/Program Structure/Methods#9. Recursion|Java: Methods § 9]]: recursion from the language side; [[Java/Program Structure/Methods#6.2 The Call Stack|§ 6.2]] on the call stack
- [[DSA/Backtracking|Backtracking]]: choose, recurse, un-choose
- [[DSA/Divide and Conquer|Divide and Conquer]]: merge sort, quickselect
- [[DSA/Dynamic Programming Fundamentals|Dynamic Programming — Fundamentals]]: memoization and tabulation
- [[DSA/Binary Trees|Binary Trees]]: recursive and iterative traversals
