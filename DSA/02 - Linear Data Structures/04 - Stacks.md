# Stacks

A <span class="hl-blue">stack</span> is a collection where the **last element added is the first one removed** (LIFO, last in, first out). You can only touch the top: push onto it, pop from it, peek at it. All three are `O(1)`.

That restriction is exactly what makes stacks useful. A stack remembers "things that are still open": unmatched brackets, unfinished function calls, operators waiting for their right operand, or elements still waiting for a larger element to appear. This note covers the implementations and Java's API traps, then the problem families: bracket matching, min-stack, expression parsing and evaluation, stack-based string processing, and the **monotonic stack**, which solves next-greater-element and largest-rectangle problems in `O(n)`.

## Contents

- [[#1. The Stack ADT|1. The Stack ADT]]
- [[#2. Implementations|2. Implementations]]
- [[#3. Stacks in Java|3. Stacks in Java]]
- [[#4. Parentheses Matching|4. Parentheses Matching]]
- [[#5. Min Stack|5. Min Stack]]
- [[#6. Expression Evaluation|6. Expression Evaluation]]
- [[#7. Stack-Based String Processing|7. Stack-Based String Processing]]
- [[#8. Monotonic Stack|8. Monotonic Stack]]
- [[#9. Monotonic Stack Applications|9. Monotonic Stack Applications]]
- [[#10. Common Mistakes|10. Common Mistakes]]
- [[#11. Trick Questions and Special Cases|11. Trick Questions and Special Cases]]
- [[#12. Quick Reference — Non-Obvious Outcomes|12. Quick Reference — Non-Obvious Outcomes]]
- [[#13. Summary|13. Summary]]

---

## 1. The Stack ADT

> [!note] Definition
> A <span class="hl-blue">stack</span> supports:
> - `push(x)`: put `x` on top.
> - `pop()`: remove and return the top element.
> - `peek()` (or `top()`): return the top element without removing it.
> - `isEmpty()`, `size()`.
>
> All are `O(1)` (push is `O(1)` amortized for an array-backed stack that resizes).

```
push 1, push 2, push 3        pop → 3         push 4
                                                   ┌───┐
    ┌───┐                                          │ 4 │ ← top
    │ 3 │ ← top                                    ├───┤
    ├───┤                     ┌───┐                │ 2 │
    │ 2 │                     │ 2 │ ← top          ├───┤
    ├───┤                     ├───┤                │ 1 │
    │ 1 │                     │ 1 │                └───┘
    └───┘                     └───┘
```

### 1.1 When a stack is the right tool

| Signal in the problem | Why a stack |
|---|---|
| Nested structure: brackets, tags, `3[a2[c]]` | the most recently opened thing must close first |
| "Undo", "back", "previous state" | revert the most recent change first |
| Evaluate or parse an expression | operators wait for their operands |
| "Next/previous greater/smaller element" | monotonic stack ([[#8. Monotonic Stack|§8]]) |
| Simulating recursion / iterative DFS | the call stack is a stack ([[DSA/01 - Foundations/02 - Recursion#8. Converting Recursion to Iteration|Recursion § 8]]) |
| Process in reverse, or cancel adjacent pairs | `"abbaca" → "ca"`, asteroid collisions |

---

## 2. Implementations

### 2.1 Array-backed

The top is the end of a dynamic array: push appends, pop removes the last element. No shifting ever happens.

```
push(x):  if size == capacity: grow;  data[size] = x;  size += 1
pop():    if size == 0: error;  size −= 1;  return data[size]
peek():   if size == 0: error;  return data[size − 1]
```

```java
class IntStack {
    private int[] data = new int[16];
    private int size = 0;

    void push(int x) {
        if (size == data.length) data = Arrays.copyOf(data, 2 * size);
        data[size++] = x;
    }

    int pop() {
        if (size == 0) throw new NoSuchElementException("stack is empty");
        return data[--size];
    }

    int peek() {
        if (size == 0) throw new NoSuchElementException("stack is empty");
        return data[size - 1];
    }

    boolean isEmpty() { return size == 0; }
    int size() { return size; }
}
```

In competitive programming the stack is often just `int[] st = new int[n]; int top = 0;` with `st[top++] = x` and `st[--top]`. There's no boxing, and when each element is pushed at most once, the size is bounded by `n`.

### 2.2 Linked

The top is the head of a singly linked list: push inserts a new head, pop removes the head. Every operation is worst-case `O(1)` (no resizing), at the cost of one node object per element.

```java
class LinkedStack<T> {
    private static class Node<T> {
        T val; Node<T> next;
        Node(T val, Node<T> next) { this.val = val; this.next = next; }
    }
    private Node<T> head;
    private int size;

    void push(T x) { head = new Node<>(x, head); size++; }

    T pop() {
        if (head == null) throw new NoSuchElementException();
        T x = head.val;
        head = head.next;
        size--;
        return x;
    }

    T peek() {
        if (head == null) throw new NoSuchElementException();
        return head.val;
    }

    boolean isEmpty() { return head == null; }
}
```

| | Array-backed | Linked |
|---|---|---|
| push | `O(1)` amortized, `O(n)` on resize | `O(1)` worst case |
| Memory per element | 4 bytes for `int[]` (plus slack) | a node object (~16–24 bytes) plus the value |
| Cache behaviour | contiguous | scattered |
| In practice | faster | used when worst-case `O(1)` matters, or for persistence (shared tails) |

> [!info]- Persistent stacks
> A linked stack is naturally **persistent**: `push` creates a new head pointing at the old one, and the old head still describes the old stack. Many versions can share one tail, each costing `O(1)` extra. This is how immutable lists in functional languages work, and why "undo to any earlier version" is cheap with linked stacks.

---

## 3. Stacks in Java

| Operation | `ArrayDeque<E>` (use this) | `Stack<E>` (legacy) |
|---|---|---|
| push | `push(x)` = `addFirst(x)` | `push(x)` |
| pop | `pop()`: throws `NoSuchElementException` if empty | `pop()`: throws `EmptyStackException` |
| peek | `peek()`: returns **`null`** if empty | `peek()`: throws `EmptyStackException` |
| Iteration order | **top → bottom** | **bottom → top** |
| `null` elements | rejected (`NullPointerException`) | allowed |
| Synchronized | no | yes (every method) |

```java
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1); stack.push(2); stack.push(3);
System.out.println(stack);              // [3, 2, 1]   top first

Stack<Integer> old = new Stack<>();
old.push(1); old.push(2); old.push(3);
System.out.println(old);                // [1, 2, 3]   bottom first
```

> [!warning] Why not `java.util.Stack`
> `Stack` extends `Vector`: every method is synchronized (slow for no benefit), and it inherits list methods such as `get(i)`, `add(i, x)`, and `remove(i)` that break the stack abstraction. The Javadoc itself recommends `Deque`. Declare the variable as `Deque<Integer>`, create an `ArrayDeque`, and use only `push`, `pop`, `peek`, and `isEmpty`.

> [!warning] `ArrayDeque.peek()` on an empty stack returns `null`
> `int top = stack.peek();` then throws a `NullPointerException` from **unboxing**, not a helpful "stack is empty" error. Always check `isEmpty()` first. And note that `peek()` and `pop()` behave differently on an empty `ArrayDeque`: `peek()` returns `null`, `pop()` throws.

> [!warning] Don't mix `push` with `offer`/`add` on one `Deque`
> `push` adds at the **front**; `offer` and `add` add at the **back**. `poll` and `pop` both remove from the front. A deque used with `push` and `poll` behaves as a stack; with `offer` and `poll`, as a queue. Mixing them in one algorithm silently produces a different order.

> [!warning] `==` on boxed values from two stacks
> `stack.peek() == minStack.peek()` compares two `Integer` **references**. It happens to be `true` for values in `−128..127` (the `Integer` cache) and `false` for larger equal values. Unbox one side (`int x = stack.peek();`) or use `.equals`. This bug passes small tests and fails large ones.

---

## 4. Parentheses Matching

### 4.1 One bracket type: a counter is enough

For a string of only `(` and `)`, track the number of currently open brackets. It must never go negative, and must end at zero.

```java
static boolean isBalanced(String s) {
    int open = 0;
    for (int i = 0; i < s.length(); i++) {
        if (s.charAt(i) == '(') open++;
        else if (--open < 0) return false;    // a ')' with nothing to close
    }
    return open == 0;
}
```

### 4.2 Several bracket types: a stack is required

`"([)]"` has balanced counts for each type but is invalid: `)` arrives while `[` is the most recent open bracket. The stack remembers *which* bracket is open most recently.

```
isValid(s):
    stack = empty
    for c in s:
        if c is an opening bracket: push the matching closing bracket
        else if stack is empty or pop() ≠ c: return false
    return stack is empty                       -- leftover openers are unmatched
```

```java
static boolean isValid(String s) {
    if (s.length() % 2 == 1) return false;     // free early exit
    Deque<Character> stack = new ArrayDeque<>();
    for (int i = 0; i < s.length(); i++) {
        char c = s.charAt(i);
        if (c == '(') stack.push(')');
        else if (c == '[') stack.push(']');
        else if (c == '{') stack.push('}');
        else if (stack.isEmpty() || stack.pop() != c) return false;
    }
    return stack.isEmpty();
}
```

Pushing the **expected closing bracket** turns the check into a single comparison.

![[Stacks - Bracket Matching.excalidraw|800]]

> [!warning] Three ways to fail
> | Input | Failure | Caught by |
> |---|---|---|
> | `")("` | close with nothing open | `stack.isEmpty()` check before `pop` |
> | `"(]"` | wrong closer | `pop() != c` |
> | `"(("` | unclosed openers | `return stack.isEmpty()` (not `return true`) |

### 4.3 Longest valid parentheses substring

Keep **indices** on the stack. The bottom element is the index just before the current valid run (start with `−1`). An unmatched `)` becomes the new base.

```java
static int longestValidParentheses(String s) {
    Deque<Integer> stack = new ArrayDeque<>();
    stack.push(-1);                                  // base: "the run starts after index −1"
    int best = 0;
    for (int i = 0; i < s.length(); i++) {
        if (s.charAt(i) == '(') {
            stack.push(i);
        } else {
            stack.pop();                             // match with an open '(' or pop the base
            if (stack.isEmpty()) stack.push(i);      // unmatched ')': new base
            else best = Math.max(best, i - stack.peek());
        }
    }
    return best;
}
```

For `")()())"`, the answer is `4`. `O(n)` time. An `O(1)`-space alternative scans left-to-right counting `open`/`close` (reset when `close > open`, record when equal), then right-to-left with the roles swapped; the second scan catches cases like `"(()"` that the first misses.

### 4.4 Minimum removals to make it valid

```java
static String minRemoveToMakeValid(String s) {
    char[] cs = s.toCharArray();
    Deque<Integer> open = new ArrayDeque<>();       // indices of unmatched '('
    for (int i = 0; i < cs.length; i++) {
        if (cs[i] == '(') open.push(i);
        else if (cs[i] == ')') {
            if (open.isEmpty()) cs[i] = '*';        // unmatched ')': mark for removal
            else open.pop();
        }
    }
    while (!open.isEmpty()) cs[open.pop()] = '*';  // unmatched '(' left over
    StringBuilder sb = new StringBuilder();
    for (char c : cs) if (c != '*') sb.append(c);
    return sb.toString();
}
```

(Using `'*'` as a marker assumes it can't occur in the input; a `boolean[]` is the safe version.) If only the **count** is needed (minimum additions to make it valid), no stack is needed: count unmatched `)` as you go, and add the final number of open `(`.

---

## 5. Min Stack

Support `push`, `pop`, `top`, and `getMin` all in `O(1)`.

The minimum can't be maintained in a single variable: after popping the current minimum, you'd need the previous one. So store, alongside each element, **the minimum of the stack at the time it was pushed**.

```
push(x):  push (x, min(x, current min))
pop():    pop
getMin(): the second component of the top pair
```

```java
class MinStack {
    private final Deque<int[]> stack = new ArrayDeque<>();   // {value, min so far}

    public void push(int x) {
        int min = stack.isEmpty() ? x : Math.min(x, stack.peek()[1]);
        stack.push(new int[]{x, min});
    }
    public void pop()    { stack.pop(); }
    public int top()     { return stack.peek()[0]; }
    public int getMin()  { return stack.peek()[1]; }
}
```

> [!info]- Two stacks: store each minimum only when it changes
> ```java
> class MinStack2 {
>     private final Deque<Integer> stack = new ArrayDeque<>();
>     private final Deque<Integer> mins = new ArrayDeque<>();
>
>     public void push(int x) {
>         stack.push(x);
>         if (mins.isEmpty() || x <= mins.peek()) mins.push(x);   // <=, NOT <
>     }
>     public void pop() {
>         int x = stack.pop();                    // unbox: compare as int
>         if (x == mins.peek()) mins.pop();
>     }
>     public int top()    { return stack.peek(); }
>     public int getMin() { return mins.peek(); }
> }
> ```
> - **`<=` handles duplicates.** Push `2, 2`, pop once: the minimum should still be `2`. With `<`, the second `2` isn't recorded in `mins`, so the first pop removes the only `2` from `mins` and the minimum becomes wrong.
> - **Unbox before comparing.** `if (stack.pop() == mins.peek())` compares two `Integer` references and fails for values outside `−128..127`.
>
> A third version stores a single `long` per element, encoding `2x − min` whenever `x` becomes the new minimum, for `O(1)` extra space. It needs `long` arithmetic to avoid overflow, and it's mostly an interview curiosity.

The same "store the aggregate alongside each element" idea gives a max-stack, a stack with `O(1)` `getGcd`, and, combined with the two-stack queue, a **queue with `O(1)` min** ([[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]]).

---

## 6. Expression Evaluation

### 6.1 Three notations

| Notation | `(1 + 2) × 3` written as | Needs parentheses? | Evaluated with |
|---|---|---|---|
| **Infix** | `(1 + 2) * 3` | yes | precedence rules, or convert first |
| **Postfix** (Reverse Polish, RPN) | `1 2 + 3 *` | **no** | one operand stack, left to right |
| **Prefix** (Polish) | `* + 1 2 3` | **no** | one operand stack, **right to left** |

Postfix and prefix are unambiguous without parentheses or precedence rules, which is why compilers and calculators convert to them.

### 6.2 Evaluating postfix

```
evalRPN(tokens):
    stack = empty
    for t in tokens:
        if t is a number: push t
        else:
            b = pop(); a = pop()         -- b was pushed LAST: it's the RIGHT operand
            push(a t b)
    return pop()
```

```java
static int evalRPN(String[] tokens) {
    Deque<Integer> st = new ArrayDeque<>();
    for (String t : tokens) {
        switch (t) {
            case "+" -> st.push(st.pop() + st.pop());
            case "*" -> st.push(st.pop() * st.pop());
            case "-" -> { int b = st.pop(), a = st.pop(); st.push(a - b); }
            case "/" -> { int b = st.pop(), a = st.pop(); st.push(a / b); }
            default  -> st.push(Integer.parseInt(t));   // also handles "-3"
        }
    }
    return st.pop();
}
```

> [!warning] Operand order for `-` and `/`
> The first `pop()` returns the **right** operand. `["4", "13", "5", "/", "+"]` is `4 + 13 / 5 = 6`; reversing the operands computes `5 / 13 = 0` and gives `4`. `+` and `*` are commutative, so the bug only shows on `-` and `/`.

> [!warning] Don't detect operators with `t.charAt(0) == '-'`
> `"-3"` is a negative number, not an operator. Compare the whole token (`t.equals("-")`), or check `t.length() == 1` first. Also note that Java's `/` truncates toward zero (`-7 / 2 == -3`), which is what most RPN problems specify.

**Prefix** is evaluated the same way scanning **right to left**, and then the first `pop()` is the **left** operand.

### 6.3 Infix to postfix: the shunting-yard algorithm

Numbers go straight to the output. Operators wait on a stack until an operator of lower precedence (or a closing parenthesis) shows they're complete.

```
toPostfix(tokens):
    output = []; ops = empty stack
    for t in tokens:
        if t is a number:  output.append(t)
        elif t == '(':     ops.push(t)
        elif t == ')':
            while ops.peek() ≠ '(':  output.append(ops.pop())
            ops.pop()                                       -- discard '('
        else:                                               -- operator
            while ops not empty and ops.peek() ≠ '(' and
                  (prec(ops.peek()) > prec(t) or
                   (prec(ops.peek()) == prec(t) and t is left-associative)):
                output.append(ops.pop())
            ops.push(t)
    while ops not empty: output.append(ops.pop())
    return output
```

```java
static List<String> toPostfix(String expr) {
    List<String> out = new ArrayList<>();
    Deque<Character> ops = new ArrayDeque<>();
    int i = 0, n = expr.length();
    while (i < n) {
        char c = expr.charAt(i);
        if (c == ' ') { i++; continue; }
        if (c >= '0' && c <= '9') {                    // read a multi-digit number
            int j = i;
            while (j < n && expr.charAt(j) >= '0' && expr.charAt(j) <= '9') j++;
            out.add(expr.substring(i, j));
            i = j;
            continue;
        }
        if (c == '(') {
            ops.push(c);
        } else if (c == ')') {
            while (ops.peek() != '(') out.add(String.valueOf(ops.pop()));
            ops.pop();
        } else {
            while (!ops.isEmpty() && ops.peek() != '(' &&
                   (prec(ops.peek()) > prec(c) || (prec(ops.peek()) == prec(c) && c != '^')))
                out.add(String.valueOf(ops.pop()));
            ops.push(c);
        }
        i++;
    }
    while (!ops.isEmpty()) out.add(String.valueOf(ops.pop()));
    return out;
}

static int prec(char op) {
    return switch (op) {
        case '+', '-' -> 1;
        case '*', '/' -> 2;
        case '^' -> 3;
        default -> 0;
    };
}
```

> [!important] Associativity decides ties
> - **Left-associative** (`+ − * /`): `8 − 3 − 2 = (8 − 3) − 2 = 3`. On equal precedence, pop the operator already on the stack first: postfix `8 3 − 2 −`.
> - **Right-associative** (`^`): `2 ^ 3 ^ 2 = 2 ^ (3 ^ 2) = 512`. On equal precedence, **don't** pop: postfix `2 3 2 ^ ^`.
>
> Popping on equal precedence for `^` gives `(2³)² = 64`.

> [!example]- Trace: `3 + 4 * 2 / (1 - 5)`
> | Token | Action | Output | Ops (bottom → top) |
> |---|---|---|---|
> | `3` | output | `3` | |
> | `+` | push | `3` | `+` |
> | `4` | output | `3 4` | `+` |
> | `*` | `prec(+) < prec(*)`: push | `3 4` | `+ *` |
> | `2` | output | `3 4 2` | `+ *` |
> | `/` | equal precedence, left-assoc: pop `*`; then `prec(+) < prec(/)`: push | `3 4 2 *` | `+ /` |
> | `(` | push | `3 4 2 *` | `+ / (` |
> | `1` | output | `3 4 2 * 1` | `+ / (` |
> | `-` | top is `(`: push | `3 4 2 * 1` | `+ / ( -` |
> | `5` | output | `3 4 2 * 1 5` | `+ / ( -` |
> | `)` | pop until `(` | `3 4 2 * 1 5 -` | `+ /` |
> | end | pop all | `3 4 2 * 1 5 - / +` | |
>
> Evaluating: `4 * 2 = 8`, `1 − 5 = −4`, `8 / −4 = −2`, `3 + −2 = 1`.

### 6.4 Direct evaluation: `+`, `−`, and parentheses, with unary minus

When the only operators are `+` and `−`, everything is a signed sum. Keep a running `result` and the `sign` of the next number. At `(`, save `(result, sign)` on the stack and start fresh; at `)`, combine.

```java
static int calculate(String s) {
    Deque<Integer> stack = new ArrayDeque<>();
    int result = 0, sign = 1, num = 0;
    for (int i = 0; i < s.length(); i++) {
        char c = s.charAt(i);
        if (c >= '0' && c <= '9') {
            num = num * 10 + (c - '0');
        } else if (c == '+' || c == '-') {
            result += sign * num;
            num = 0;
            sign = (c == '+') ? 1 : -1;
        } else if (c == '(') {
            stack.push(result);
            stack.push(sign);                 // the sign in front of this '('
            result = 0;
            sign = 1;
        } else if (c == ')') {
            result += sign * num;
            num = 0;
            int savedSign = stack.pop();
            int savedResult = stack.pop();
            result = savedResult + savedSign * result;
        }                                     // spaces are skipped
    }
    return result + sign * num;               // flush the last number
}
```

Unary minus works without special handling: in `"-(2+3)"`, the leading `-` just adds `0` and sets `sign = −1`; in `"1-(-2)"`, the inner `-` does the same inside the parentheses. Result `3`.

### 6.5 Direct evaluation: `+ − * /` without parentheses

`*` and `/` bind tighter, so they must be applied to the **previous term** immediately, while `+` and `−` are deferred. Push terms onto a stack (negated for `−`), fold `*` and `/` into the top term, and sum the stack at the end.

```java
static int calculate2(String s) {
    Deque<Integer> stack = new ArrayDeque<>();
    int num = 0;
    char op = '+';                                    // the operator BEFORE the current number
    for (int i = 0; i < s.length(); i++) {
        char c = s.charAt(i);
        boolean digit = c >= '0' && c <= '9';
        if (digit) num = num * 10 + (c - '0');
        if ((!digit && c != ' ') || i == s.length() - 1) {
            switch (op) {
                case '+' -> stack.push(num);
                case '-' -> stack.push(-num);
                case '*' -> stack.push(stack.pop() * num);
                case '/' -> stack.push(stack.pop() / num);
            }
            op = c;
            num = 0;
        }
    }
    int sum = 0;
    for (int x : stack) sum += x;
    return sum;
}
```

> [!tip] The general case
> For the full grammar (all four operators, parentheses, unary minus), either run shunting-yard and evaluate the postfix, or use the **two-stack** method (one operand stack, one operator stack, applying operators as shunting-yard would pop them), or write a small recursive-descent parser (`expr → term ((+|−) term)*`, `term → factor ((*|/) factor)*`, `factor → number | (expr) | −factor`). Recursive descent is the easiest to extend and to get right.

---

## 7. Stack-Based String Processing

### 7.1 Cancel adjacent pairs

Remove adjacent equal characters repeatedly (`"abbaca"` → `"ca"`). A `StringBuilder` works as the stack:

```java
static String removeDuplicates(String s) {
    StringBuilder st = new StringBuilder();
    for (char c : s.toCharArray()) {
        int n = st.length();
        if (n > 0 && st.charAt(n - 1) == c) st.deleteCharAt(n - 1);   // O(1) at the end
        else st.append(c);
    }
    return st.toString();
}
```

The stack handles cascades (`"abba"`: removing `bb` makes the two `a`s adjacent) automatically. Rescanning the string after each removal is `O(n²)`. **Backspace comparison** (`"ab#c"` = `"ac"`) is the same idea: `#` pops. It can also be done in `O(1)` space by scanning both strings from the right, counting pending backspaces ([[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]]).

### 7.2 Decode a nested string: `3[a2[c]]` → `accaccacc`

At `[`, save the current partial string and the repeat count, and start a new string. At `]`, repeat the inner string and append it to the saved outer one.

```java
static String decodeString(String s) {
    Deque<Integer> counts = new ArrayDeque<>();
    Deque<StringBuilder> outers = new ArrayDeque<>();
    StringBuilder cur = new StringBuilder();
    int k = 0;
    for (char c : s.toCharArray()) {
        if (c >= '0' && c <= '9') {
            k = k * 10 + (c - '0');                 // counts can have several digits
        } else if (c == '[') {
            counts.push(k);
            outers.push(cur);
            cur = new StringBuilder();
            k = 0;
        } else if (c == ']') {
            StringBuilder outer = outers.pop();
            outer.append(cur.toString().repeat(counts.pop()));
            cur = outer;
        } else {
            cur.append(c);
        }
    }
    return cur.toString();
}
```

### 7.3 Simplify a Unix path

```java
static String simplifyPath(String path) {
    Deque<String> st = new ArrayDeque<>();
    for (String part : path.split("/")) {
        if (part.isEmpty() || part.equals(".")) continue;   // "//" and "/./"
        if (part.equals("..")) {
            if (!st.isEmpty()) st.pop();                     // ".." at the root stays at the root
        } else {
            st.push(part);                                   // "..." is a normal name
        }
    }
    StringBuilder sb = new StringBuilder();
    while (!st.isEmpty()) sb.append('/').append(st.pollLast());   // bottom of the stack first
    return sb.length() == 0 ? "/" : sb.toString();
}
```

### 7.4 Asteroid collision

Positive values move right, negative values move left, equal sizes destroy each other. Only a **right-moving** asteroid on the stack followed by a **left-moving** new one can collide.

```java
static int[] asteroidCollision(int[] asteroids) {
    Deque<Integer> st = new ArrayDeque<>();
    for (int x : asteroids) {
        boolean alive = true;
        while (alive && x < 0 && !st.isEmpty() && st.peek() > 0) {
            int top = st.peek();
            if (top < -x) st.pop();                      // top explodes; x keeps going
            else if (top == -x) { st.pop(); alive = false; }
            else alive = false;                          // x explodes
        }
        if (alive) st.push(x);
    }
    int[] res = new int[st.size()];
    for (int i = res.length - 1; i >= 0; i--) res[i] = st.pop();
    return res;
}
```

`[-2, 2]` doesn't collide (they move apart); `[2, -2]` leaves nothing; `[10, 2, -5]` leaves `[10]`.

### 7.5 Validate push/pop sequences

Given the order elements were pushed and a claimed order of pops, can it happen? Simulate: push in order, and after each push, pop while the top equals the next expected pop.

```java
static boolean validateStackSequences(int[] pushed, int[] popped) {
    Deque<Integer> st = new ArrayDeque<>();
    int j = 0;
    for (int x : pushed) {
        st.push(x);
        while (!st.isEmpty() && st.peek() == popped[j]) {   // Integer vs int: unboxes, safe
            st.pop();
            j++;
        }
    }
    return st.isEmpty();
}
```

Popping greedily is always safe: if the top equals the next required output, it can never be output later (anything pushed afterwards would sit on top of it).

---

## 8. Monotonic Stack

A <span class="hl-blue">monotonic stack</span> keeps its elements in sorted order from bottom to top. Before pushing a new element, pop everything that would break the order. Each popped element has just met the element that "beats" it, and that's the answer to a *next greater/smaller* query.

### 8.1 Next greater element

For each `a[i]`, find the first element to its right that is **strictly greater** (or `−1`).

```
nextGreater(a):
    res = array of −1
    stack = empty                              -- indices whose answer is still unknown
    for i = 0 to n − 1:
        while stack not empty and a[stack.top] < a[i]:
            res[stack.pop()] = a[i]            -- a[i] is the first greater element for it
        stack.push(i)
    return res
```

```java
static int[] nextGreater(int[] a) {
    int n = a.length;
    int[] res = new int[n];
    Arrays.fill(res, -1);
    int[] st = new int[n];
    int top = 0;
    for (int i = 0; i < n; i++) {
        while (top > 0 && a[st[top - 1]] < a[i]) res[st[--top]] = a[i];
        st[top++] = i;
    }
    return res;
}
```

![[Stacks - Monotonic Stack Next Greater.excalidraw|800]]

> [!example]- Trace: `a = [2, 1, 2, 4, 3]`
> | `i` | `a[i]` | Popped (index → answer) | Stack after (values) |
> |---|---|---|---|
> | 0 | 2 | — | `[2]` |
> | 1 | 1 | — | `[2, 1]` |
> | 2 | 2 | `1 → 2` | `[2, 2]` (the first 2 is not `< 2`, so it stays) |
> | 3 | 4 | `2 → 4`, `0 → 4` | `[4]` |
> | 4 | 3 | — | `[4, 3]` |
>
> Result: `[4, 2, 4, -1, -1]`. The stack's values are non-increasing from bottom to top at every step.

> [!important] Why it's O(n), not O(n²)
> Each index is pushed once and popped at most once, so all the `while` iterations together run at most `n` times. This is the aggregate argument from [[DSA/01 - Foundations/01 - Complexity Analysis#8.4 Where amortized bounds appear|Complexity Analysis § 8.4]]: a single step can pop many elements, but the total over the whole scan is linear.

### 8.2 The four variants from one scan

Scanning left to right, the pop condition decides two things at once: the answer for each **popped** element (its *next* element), and the answer for the **current** element (whatever remains on top is its *previous* element).

| Pop while `a[top] … a[i]` | Popped elements get their next… | After popping, the top is `i`'s previous… | Stack order (bottom → top) |
|---|---|---|---|
| `<` | **greater** (strict) | greater **or equal** | non-increasing |
| `<=` | greater **or equal** | **greater** (strict) | strictly decreasing |
| `>` | **smaller** (strict) | smaller **or equal** | non-decreasing |
| `>=` | smaller **or equal** | **smaller** (strict) | strictly increasing |

Mnemonic: to find **greater** elements, keep a **decreasing** stack (a greater element pops the smaller ones), and vice versa. Scanning right to left swaps "next" and "previous".

> [!warning] Store indices, not values
> Distances (daily temperatures), widths (histograms), and "which element" answers all need positions. You can always read the value back with `a[index]`, but not the other way round.

### 8.3 Circular arrays

The next greater element may wrap around. Scan `2n` positions with `i % n`, pushing only during the first pass:

```java
static int[] nextGreaterCircular(int[] a) {
    int n = a.length;
    int[] res = new int[n];
    Arrays.fill(res, -1);
    Deque<Integer> st = new ArrayDeque<>();
    for (int i = 0; i < 2 * n; i++) {
        int x = a[i % n];
        while (!st.isEmpty() && a[st.peek()] < x) res[st.pop()] = x;
        if (i < n) st.push(i);
    }
    return res;
}
```

The maximum element (and any element equal to it) correctly gets `−1`: nothing ever pops it.

---

## 9. Monotonic Stack Applications

### 9.1 Daily temperatures and stock span

- **Daily temperatures:** days until a warmer day = `i − idx` when `idx` is popped by `i` (next strictly greater).
- **Stock span:** number of consecutive days up to today with price `≤` today's = `i − (previous strictly greater index)`. Pop while `price[top] <= price[i]`; the remaining top is the previous strictly greater ([[#8.2 The four variants from one scan|§8.2]], row 2). In the online version, store `(price, span)` pairs and add up the spans you pop.

### 9.2 Largest rectangle in a histogram

The largest rectangle that uses bar `i` at full height extends left to just after the **previous smaller** bar and right to just before the **next smaller** bar. One increasing stack finds both: when bar `j` is popped by bar `i`, `i` is its next smaller, and the new top is its previous smaller.

```
largestRectangle(h):
    stack = empty; best = 0
    for i = 0 to n:                          -- i = n is a sentinel bar of height 0
        cur = (i == n) ? 0 : h[i]
        while stack not empty and h[stack.top] ≥ cur:
            height = h[stack.pop()]
            left = stack empty ? −1 : stack.top
            best = max(best, height × (i − left − 1))
        stack.push(i)
    return best
```

```java
static long largestRectangleArea(int[] h) {
    int n = h.length;
    long best = 0;
    int[] st = new int[n + 1];
    int top = 0;
    for (int i = 0; i <= n; i++) {
        int cur = (i == n) ? 0 : h[i];
        while (top > 0 && h[st[top - 1]] >= cur) {
            int height = h[st[--top]];
            int left = (top == 0) ? -1 : st[top - 1];       // previous smaller
            best = Math.max(best, (long) height * (i - left - 1));
        }
        st[top++] = i;
    }
    return best;
}
```

![[Stacks - Largest Rectangle in Histogram.excalidraw|800]]

> [!warning] The details that break histogram solutions
> - **The sentinel.** Without the final height-0 bar, bars still on the stack at the end are never measured; `[1, 2, 3]` returns `0` instead of `4`.
> - **Empty stack → left boundary is `−1`.** The popped bar was the smallest so far, so it extends all the way to index 0, and the width is `i`, not `i − 1`.
> - **Equal heights.** With `>=`, an equal bar pops the earlier one, which then computes a width that's too short. That's harmless, because the **last** bar of the equal run is measured later with the full width. Either `>` or `>=` is correct, as long as the width formula uses the new top.
> - **Overflow.** `height × width` can reach `10⁹ × 10⁵`; use `long` unless the constraints rule it out.

**Maximal rectangle of 1s in a binary matrix:** for each row, let `heights[c]` be the number of consecutive `1`s ending at that row in column `c` (reset to `0` on a `0`). Run the histogram algorithm on every row. `O(R·C)`.

### 9.3 Trapping rain water (stack version)

Water fills "valleys" layer by layer. When a bar taller than the stack top arrives, the top is a valley bottom bounded by the new bar on the right and the next stack element on the left.

```java
static int trap(int[] h) {
    Deque<Integer> st = new ArrayDeque<>();      // indices, heights non-increasing
    int water = 0;
    for (int i = 0; i < h.length; i++) {
        while (!st.isEmpty() && h[st.peek()] < h[i]) {
            int bottom = h[st.pop()];
            if (st.isEmpty()) break;                         // no left wall: water spills
            int left = st.peek();
            int width = i - left - 1;
            int depth = Math.min(h[left], h[i]) - bottom;
            water += width * depth;
        }
        st.push(i);
    }
    return water;
}
```

The `O(1)`-space version uses two pointers moving inward from both ends ([[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]]); the prefix-max/suffix-max version computes `min(maxLeft[i], maxRight[i]) − h[i]` per column ([[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums]]).

### 9.4 Sum of subarray minimums (contribution technique)

Instead of enumerating `n²` subarrays, count for each `a[i]` how many subarrays have it as their minimum: `left[i] × right[i]`, where `left[i]` is the number of possible start positions and `right[i]` the number of possible end positions.

```java
static int sumSubarrayMins(int[] a) {
    final long MOD = 1_000_000_007L;
    int n = a.length;
    int[] left = new int[n], right = new int[n];
    Deque<Integer> st = new ArrayDeque<>();
    for (int i = 0; i < n; i++) {                      // previous STRICTLY smaller
        while (!st.isEmpty() && a[st.peek()] >= a[i]) st.pop();
        left[i] = st.isEmpty() ? i + 1 : i - st.peek();
        st.push(i);
    }
    st.clear();
    for (int i = n - 1; i >= 0; i--) {                 // next smaller OR EQUAL
        while (!st.isEmpty() && a[st.peek()] > a[i]) st.pop();
        right[i] = st.isEmpty() ? n - i : st.peek() - i;
        st.push(i);
    }
    long sum = 0;
    for (int i = 0; i < n; i++) sum = (sum + (long) a[i] * left[i] % MOD * right[i]) % MOD;
    return (int) sum;
}
```

> [!important] Strict on one side, non-strict on the other
> With equal values, a subarray like `[2, 2]` has two candidate minima. If both sides use strict comparisons, both 2s claim it (counted twice); if both are non-strict, neither does. Making one side strict and the other non-strict assigns every subarray to exactly one minimum (here, the leftmost one). For `[3, 1, 2, 4]` the answer is `17`. The same technique gives the sum of subarray maximums, and their difference is the "sum of subarray ranges".

### 9.5 Remove `k` digits to make the smallest number

Greedy: a digit followed by a smaller digit should be removed, so keep the digits in a **non-decreasing** stack.

```java
static String removeKdigits(String num, int k) {
    StringBuilder st = new StringBuilder();             // a stack of digits
    for (char c : num.toCharArray()) {
        while (k > 0 && st.length() > 0 && st.charAt(st.length() - 1) > c) {
            st.deleteCharAt(st.length() - 1);
            k--;
        }
        st.append(c);
    }
    st.setLength(st.length() - k);                      // removals left over: drop from the end
    int i = 0;
    while (i < st.length() - 1 && st.charAt(i) == '0') i++;   // strip leading zeros, keep one digit
    String res = st.substring(i);
    return res.isEmpty() ? "0" : res;
}
```

Edge cases this handles: `"12345", k = 2` (already increasing, remove from the end → `"123"`); `"10200", k = 1` → `"200"` (leading zero stripped); `"10", k = 2` → `"0"` (not `""`). **Remove duplicate letters** (smallest subsequence containing each letter once) uses the same increasing stack, popping a letter only if it occurs again later and isn't already in the stack.

---

## 10. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| `pop()`/`peek()` without checking `isEmpty()` | `NoSuchElementException` / NPE from unboxing `null` | check first |
| Returning `true` at the end of bracket matching | `"(("` accepted | `return stack.isEmpty()` |
| Counter instead of a stack for several bracket types | `"([)]"` accepted | stack |
| `java.util.Stack` | slow; bottom-to-top iteration and printing | `ArrayDeque` |
| Mixing `push` and `offer` on one deque | wrong order | pick stack or queue methods |
| `stack.peek() == other.peek()` on `Integer`s | fails above 127 | unbox or `equals` |
| Min-stack with `<` instead of `<=` | wrong min after popping a duplicate | `<=` |
| `a op b` from `pop(), pop()` in the wrong order | wrong `-` and `/` results | first pop is the right operand |
| Treating `"-3"` as an operator | crash or wrong answer | compare whole tokens |
| Popping on equal precedence for `^` | `2^3^2 = 64` | `^` is right-associative |
| Single-digit number parsing | `12` read as `1`, `2` | accumulate `num = num*10 + d` |
| Forgetting to flush the last number | last term missing | handle it after the loop |
| Storing values in a monotonic stack | can't compute distances or widths | store indices |
| Histogram without a sentinel | remaining bars never measured | extra height-0 bar at `i = n` |
| Both sides strict (or both non-strict) in contribution counting | duplicates over/under-counted | strict on one side only |
| `removeKdigits` returning `""` or `"0200"` | wrong format | strip leading zeros, empty → `"0"` |

---

## 11. Trick Questions and Special Cases

> [!question]- Why isn't a counter enough for `"([)]"`?
> Each type is balanced separately (one `(`, one `)`, one `[`, one `]`), and no prefix has more closers than openers. But the `)` closes while `[` is the most recently opened bracket, so nesting is violated. Only a stack, which records the **order** of opening, catches it.

> [!question]- `Deque<Integer> d = new ArrayDeque<>(); d.push(1); d.push(2); d.push(3);` — what does `System.out.println(d)` print? And for `java.util.Stack`?
> `[3, 2, 1]` for `ArrayDeque` (it iterates from the front, where `push` adds) and `[1, 2, 3]` for `Stack` (it's a `Vector`, iterated from index 0, the bottom). Converting with `new ArrayList<>(stack)` or iterating with for-each also follows these orders, which matters when building output from a stack.

> [!question]- `int x = stack.peek();` on an empty `ArrayDeque` — which exception?
> `NullPointerException`. `peek()` returns `null` for an empty deque (it doesn't throw), and unboxing `null` to `int` throws. `pop()` on the same empty deque throws `NoSuchElementException`. `java.util.Stack.peek()` would throw `EmptyStackException`.

> [!question]- Pushing 1, 2, 3 in that order (with pops interleaved anywhere), which pop order is impossible?
> `3, 1, 2`. To pop 3 first, both 1 and 2 must be on the stack, with 2 above 1, so 2 must come out before 1. All other 5 orders are possible. In general, the number of achievable orders for `n` elements is the Catalan number `Cₙ` (5 for `n = 3`), and the impossible ones are exactly those containing the pattern "high, low, middle" in that relative order.

> [!question]- Is the monotonic stack algorithm O(n²) because of the nested `while`?
> No, `O(n)`. Every index is pushed exactly once and popped at most once, so the inner loop runs at most `n` times in total across the whole scan.

> [!question]- Next greater element in `[1, 1, 1]`?
> `[-1, -1, -1]`, with a strict pop condition (`<`). Equal elements are not "greater", so they don't pop each other. If the condition were `<=`, each `1` would report the next `1` as its "next greater", which answers a different question (next greater **or equal**).

> [!question]- Next greater element in a circular array `[5, 4, 3, 2, 1]`?
> `[-1, 5, 5, 5, 5]`. The second pass over the array lets `5` pop all the remaining indices. The maximum has no greater element anywhere, so it stays `-1`.

> [!question]- Largest rectangle in `[2, 1, 5, 6, 2, 3]`?
> `10`: bars `5` and `6` give a 5 × 2 rectangle. The tallest bar alone gives only `6`, height `2` spans four bars (`5, 6, 2, 3`) for `8`, and height `1` spans all six for `6`. The answer is not always at the tallest bar or at the widest span, which is why every bar must be considered as the limiting height. (And `[1, 2, 3]` without a sentinel gives `0` instead of `4`.)

> [!question]- `evalRPN(["4", "13", "5", "/", "+"])`?
> `6`: `13 / 5 = 2` (integer division), then `4 + 2`. Popping the operands in the wrong order computes `5 / 13 = 0` and returns `4`.

> [!question]- What is `2 ^ 3 ^ 2`?
> `512`, because `^` is right-associative: `2 ^ (3 ^ 2) = 2⁹`. A shunting-yard that treats every operator as left-associative computes `(2³)² = 64`. (In Java code, `^` is XOR, not power: `2 ^ 3 ^ 2` is `3`. Expression-parsing problems define `^` themselves.)

> [!question]- Basic calculator: what are `"- (3 + 4)"` and `"1 - (-2)"`?
> `-7` and `3`. The sign-stack method treats a leading or post-parenthesis `-` as "add 0, then negate what follows", so unary minus needs no special case. Many hand-rolled parsers crash on the leading `-` because they expect a number before every operator.

> [!question]- Min stack: push 0, push 1, push 0, then pop. What's `getMin()`?
> `0`. With the two-stack version, the `<=` comparison recorded **both** zeros in the min stack, so popping one leaves the other. With `<`, only the first `0` would be recorded; popping the second `0` would then pop the min stack's only `0`, and `getMin()` would return a wrong value (or throw).

> [!question]- Remove adjacent duplicates from `"azxxzy"`?
> `"ay"`. Removing `xx` makes the two `z`s adjacent, and they go too. The stack handles the cascade in one pass; a single left-to-right scan that only compares neighbours in the original string returns `"azzy"`.

> [!question]- Sum of subarray minimums of `[2, 2]`?
> `6`: subarrays `[2]`, `[2]`, `[2, 2]`, each with minimum 2. Counting with strict comparisons on both sides gives `8` (the `[2, 2]` subarray is counted by both elements); non-strict on both sides gives `4` (counted by neither).

---

## 12. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `ArrayDeque` after `push(1..3)`, printed | `[3, 2, 1]` | iterates from the top |
| `Stack` after `push(1..3)`, printed | `[1, 2, 3]` | `Vector` order |
| `ArrayDeque.peek()` when empty | `null` | `pop()` throws instead |
| `int x = deque.peek()` when empty | `NullPointerException` | unboxing `null` |
| `ArrayDeque.push(null)` | `NullPointerException` | `null` not allowed |
| `peek() == peek()` on `Integer`s ≥ 128 | can be `false` | reference comparison |
| `"([)]"` with per-type counters | wrongly valid | needs a stack |
| Monotonic stack scan | `O(n)` | each index pushed and popped once |
| Pop while `a[top] < a[i]` | popped: next greater; top: previous greater-or-equal | |
| Pop while `a[top] <= a[i]` | popped: next greater-or-equal; top: previous greater | |
| Histogram with no sentinel, `[1, 2, 3]` | `0` | bars never popped |
| `2 ^ 3 ^ 2` in an expression parser | `512` | right-associative |
| `2 ^ 3 ^ 2` in Java | `3` | XOR |
| RPN `13 5 /` | `2` | first pop is the right operand |
| `-7 / 2` in Java | `-3` | truncation toward zero |
| Impossible pop order for pushes 1, 2, 3 | `3, 1, 2` | 2 is above 1 |
| Achievable pop orders for `n` pushes | Catalan `Cₙ` | |
| Sum of subarray mins `[3, 1, 2, 4]` | `17` | contribution technique |
| `removeKdigits("10", 2)` | `"0"` | empty → `"0"` |

---

## 13. Summary

- A stack is LIFO with `O(1)` push, pop, and peek. Use an array (`ArrayDeque`, or `int[]` + `top`) in practice; a linked stack gives worst-case `O(1)` and cheap persistence.
- In Java, use `Deque<T> st = new ArrayDeque<>()` with `push`/`pop`/`peek`. `peek()` returns `null` when empty, `java.util.Stack` iterates bottom-up, and `Integer` comparisons need unboxing.
- **Bracket matching**: push the expected closer; fail on an empty stack or a mismatch; succeed only if the stack ends empty. Indices on the stack give lengths and positions.
- **Min stack**: store the running minimum with each element (or a second stack updated with `<=`).
- **Expressions**: postfix evaluates with one stack (mind operand order); shunting-yard converts infix using precedence and associativity; `+`/`−` with parentheses needs only a sign stack.
- **Monotonic stack**: keep indices in sorted order; popped elements learn their *next* greater/smaller, and the current element learns its *previous* one. `O(n)` total. Histogram, rain water, stock span, subarray-minimum sums, and greedy digit removal are all applications.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/02 - Linear Data Structures/03 - Linked Lists|Linked Lists]] · Next: [[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]]
- [[DSA/01 - Foundations/02 - Recursion#8. Converting Recursion to Iteration|Recursion § 8]]: replacing the call stack with an explicit one
- [[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]]: queue from two stacks; the monotonic deque
- [[DSA/04 - Trees and Hierarchical Structures/01 - Binary Trees|Binary Trees]]: iterative traversals with a stack
- [[DSA/05 - Graphs/01 - Graph Representations and Traversals|Graph Representations and Traversals]]: iterative DFS
- [[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]]: `O(1)`-space alternatives for rain water and backspace comparison
- [[DSA/01 - Foundations/01 - Complexity Analysis#8. Amortized Analysis|Complexity Analysis § 8]]: why the monotonic stack is linear
