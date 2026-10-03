# Queues and Deques

A <span class="hl-blue">queue</span> removes elements in the order they arrived (FIFO, first in, first out): add at the back, remove from the front. A <span class="hl-blue">deque</span> ("deck", double-ended queue) allows adding and removing at **both** ends, so it can act as a stack, a queue, or something in between.

Queues model anything processed in arrival order: BFS frontiers, task schedulers, buffers between a producer and a consumer, and sliding time windows. The deque's main algorithmic use is the **monotonic deque**, which maintains the maximum or minimum of a sliding window in `O(1)` amortized time and speeds up a family of DP recurrences from `O(nk)` to `O(n)`. This note covers the implementations (especially the circular buffer), Java's API, queues built from stacks and vice versa, and the monotonic deque with its applications.

## Contents

- [[#1. The Queue and Deque ADTs|1. The Queue and Deque ADTs]]
- [[#2. Implementations|2. Implementations]]
- [[#3. The Circular Buffer|3. The Circular Buffer]]
- [[#4. Queues and Deques in Java|4. Queues and Deques in Java]]
- [[#5. Queues from Stacks, Stacks from Queues|5. Queues from Stacks, Stacks from Queues]]
- [[#6. Queue Applications|6. Queue Applications]]
- [[#7. Monotonic Deque — Sliding Window Maximum|7. Monotonic Deque — Sliding Window Maximum]]
- [[#8. Monotonic Deque Applications|8. Monotonic Deque Applications]]
- [[#9. Common Mistakes|9. Common Mistakes]]
- [[#10. Trick Questions and Special Cases|10. Trick Questions and Special Cases]]
- [[#11. Quick Reference — Non-Obvious Outcomes|11. Quick Reference — Non-Obvious Outcomes]]
- [[#12. Summary|12. Summary]]

---

## 1. The Queue and Deque ADTs

> [!note] Definitions
> A <span class="hl-blue">queue</span> supports `enqueue(x)` (add at the back), `dequeue()` (remove from the front), `peek()` (look at the front), and `isEmpty()`, all `O(1)`.
>
> A <span class="hl-blue">deque</span> supports `addFirst`, `addLast`, `removeFirst`, `removeLast`, `peekFirst`, and `peekLast`, all `O(1)`.

```
            dequeue ◄── [ 1 | 2 | 3 | 4 ] ◄── enqueue
                         front      back

    addFirst / removeFirst ◄──► [ 1 | 2 | 3 | 4 ] ◄──► addLast / removeLast
```

| Structure | Insert | Remove | Order |
|---|---|---|---|
| Stack | top | top | LIFO |
| Queue | back | front | FIFO |
| Deque | either end | either end | caller decides |
| Priority queue | anywhere | the smallest (or largest) | by priority, **not** arrival ([[DSA/Heaps and Priority Queues|Heaps and Priority Queues]]) |

---

## 2. Implementations

| Implementation | enqueue | dequeue | Notes |
|---|---|---|---|
| Linked list with head **and tail** | `O(1)` | `O(1)` | enqueue at the tail, dequeue at the head |
| Linked list with head only | `O(n)` | `O(1)` | must walk to the end to enqueue |
| Array, dequeue by shifting | `O(1)` amortized | **`O(n)`** | `ArrayList.remove(0)` is this |
| Array, advance a `front` index | `O(1)` | `O(1)` | slots before `front` are wasted forever |
| **Circular buffer** | `O(1)` amortized | `O(1)` | reuses freed slots by wrapping around (§3) |

> [!warning] `ArrayList` as a queue
> `list.add(x)` / `list.remove(0)` looks like a queue but every dequeue shifts the remaining elements: `n` dequeues cost `Θ(n²)`. BFS on a graph of 10⁵ nodes written this way can TLE on its own. Use `ArrayDeque`.

> [!tip] The contest queue: an array and two indices
> When the total number of enqueues is bounded by `N` (BFS enqueues each vertex at most once), `int[] q = new int[N]; int head = 0, tail = 0;` with `q[tail++] = x` and `q[head++]` is the fastest queue there is. Nothing is reused, so there's no wrap-around to manage. `head == tail` means empty.

The linked version:

```java
class LinkedQueue<T> {
    private static class Node<T> {
        T val; Node<T> next;
        Node(T val) { this.val = val; }
    }
    private Node<T> head, tail;     // dequeue at head, enqueue at tail
    private int size;

    void offer(T x) {
        Node<T> node = new Node<>(x);
        if (tail == null) head = tail = node;     // was empty
        else { tail.next = node; tail = node; }
        size++;
    }

    T poll() {
        if (head == null) throw new NoSuchElementException();
        T x = head.val;
        head = head.next;
        if (head == null) tail = null;            // became empty: reset tail too
        size--;
        return x;
    }

    boolean isEmpty() { return head == null; }
}
```

> [!warning] Reset `tail` when the queue becomes empty
> Without `if (head == null) tail = null;`, `tail` still points at the removed node. The next `offer` then appends to that orphan (`tail.next = node`) instead of setting `head`, so `head` stays `null` and the element is lost.

---

## 3. The Circular Buffer

A <span class="hl-blue">circular buffer</span> (ring buffer) stores the queue in an array, treating the last slot as adjacent to the first. Keep the index of the front (`head`) and the number of elements (`size`). The back is computed:

```
front element:  data[head]
back slot:      (head + size) mod capacity      -- where the next element goes
i-th element:   data[(head + i) mod capacity]
```

```
capacity 8, head = 6, size = 4:

index:   0   1   2   3   4   5   6   7
       [ c | d |   |   |   |   | a | b ]
                 ▲               ▲
          next back slot       head        queue order: a b c d
```

### 3.1 Fixed capacity (design circular queue)

```java
class CircularQueue {
    private final int[] data;
    private int head = 0, size = 0;

    CircularQueue(int capacity) { data = new int[capacity]; }

    boolean offer(int x) {
        if (size == data.length) return false;              // full
        data[(head + size) % data.length] = x;
        size++;
        return true;
    }

    int poll() {
        if (size == 0) throw new NoSuchElementException();
        int x = data[head];
        head = (head + 1) % data.length;
        size--;
        return x;
    }

    int front() {
        if (size == 0) throw new NoSuchElementException();
        return data[head];
    }

    int rear() {
        if (size == 0) throw new NoSuchElementException();
        return data[(head + size - 1) % data.length];
    }

    boolean isEmpty() { return size == 0; }
    boolean isFull()  { return size == data.length; }
}
```

> [!important] Full vs. empty: `head == tail` is ambiguous
> The other common representation keeps `head` and `tail` indices instead of `size`. Then an empty queue and a full queue both have `head == tail`. The two standard fixes:
> 1. **Keep a `size` (or `count`) field**, as above. All `capacity` slots are usable.
> 2. **Leave one slot empty**: "full" means `(tail + 1) % capacity == head`. Only `capacity − 1` slots are usable, so allocate one extra.
>
> Mixing the two (a `head`/`tail` design that also tries to use every slot, without a counter) is a classic bug.

### 3.2 A growable deque

Adding at the front moves `head` backward, which needs a **non-negative** modulo:

```java
class IntDeque {
    private int[] data = new int[8];
    private int head = 0, size = 0;

    void addFirst(int x) {
        if (size == data.length) grow();
        head = (head - 1 + data.length) % data.length;   // NOT (head - 1) % length: that's −1 at head = 0
        data[head] = x;
        size++;
    }

    void addLast(int x) {
        if (size == data.length) grow();
        data[(head + size) % data.length] = x;
        size++;
    }

    int pollFirst() {
        if (size == 0) throw new NoSuchElementException();
        int x = data[head];
        head = (head + 1) % data.length;
        size--;
        return x;
    }

    int pollLast() {
        if (size == 0) throw new NoSuchElementException();
        size--;
        return data[(head + size) % data.length];
    }

    int get(int i) {                                     // O(1) random access, which ArrayDeque lacks
        if (i < 0 || i >= size) throw new IndexOutOfBoundsException();
        return data[(head + i) % data.length];
    }

    int size() { return size; }

    private void grow() {
        int[] bigger = new int[2 * data.length];
        for (int i = 0; i < size; i++) bigger[i] = data[(head + i) % data.length];  // unroll the wrap
        data = bigger;
        head = 0;
    }
}
```

> [!warning] Resizing a circular buffer is not `Arrays.copyOf`
> If the contents wrap around (`head` near the end, the back near the start), copying the array as-is into a bigger one leaves a gap in the middle, and the modulo arithmetic with the **new** capacity reads the wrong slots. Copy the elements **in queue order** starting from `head`, then reset `head = 0`.

> [!tip] Power-of-two capacities
> If the capacity is a power of two, `i % capacity` can be replaced by `i & (capacity − 1)`, which is faster and also works for `i = −1` (`-1 & (cap − 1) = cap − 1`). Older versions of `ArrayDeque` did exactly this ([[03 - Bit Manipulation|Bit Manipulation]]).

---

## 4. Queues and Deques in Java

### 4.1 The `Queue` interface: two families of methods

| Operation | Throws an exception on failure | Returns a special value |
|---|---|---|
| Insert at back | `add(x)`: `IllegalStateException` if a bounded queue is full | `offer(x)`: returns `false` |
| Remove from front | `remove()`: `NoSuchElementException` | `poll()`: returns **`null`** |
| Examine front | `element()`: `NoSuchElementException` | `peek()`: returns **`null`** |

### 4.2 `Deque` methods

| | Front | Back |
|---|---|---|
| Insert | `addFirst`, `offerFirst`, `push` | `addLast`, `offerLast`, `add`, `offer` |
| Remove | `removeFirst`, `pollFirst`, `remove()`, `poll()`, `pop` | `removeLast`, `pollLast` |
| Examine | `getFirst`, `peekFirst`, `element()`, `peek()` | `getLast`, `peekLast` |

So a `Deque` used with `offer`/`poll` is a queue (back in, front out), and with `push`/`pop` it's a stack (front in, front out). For a deque used as a deque, prefer the explicit `…First`/`…Last` names: they make the intent obvious.

### 4.3 Which class

| Class | Structure | Notes |
|---|---|---|
| **`ArrayDeque`** | circular array | the default for queues, stacks, and deques; rejects `null`; no `get(i)` |
| `LinkedList` | doubly linked list | allows `null` (which makes `poll()`'s `null` ambiguous); more memory, slower |
| `PriorityQueue` | binary heap | implements `Queue` but is **not FIFO** |
| `ArrayBlockingQueue`, `LinkedBlockingQueue` | | thread-safe producer/consumer queues with blocking `put`/`take` |

> [!warning] `PriorityQueue` is a `Queue` but not a FIFO queue
> `Queue<Integer> q = new PriorityQueue<>();` compiles and `poll()` returns the **smallest** element, not the oldest. Its iterator and `toString()` show the internal heap array order, which is neither insertion order nor sorted order. Declaring a variable as `Queue<…>` doesn't tell a reader which behaviour they get.

> [!info]- Iterating and the `descendingIterator`
> `ArrayDeque` iterates from front to back. `descendingIterator()` goes back to front. Modifying the deque during iteration (other than through the iterator) throws `ConcurrentModificationException`. There's no `get(i)`: if you need random access into a deque-like structure, write the circular buffer from §3.2 or use two indices into an array.

---

## 5. Queues from Stacks, Stacks from Queues

### 5.1 Queue from two stacks: O(1) amortized

Push incoming elements onto `in`. To dequeue, pop from `out`; if `out` is empty, first move **everything** from `in` to `out`, which reverses their order so the oldest element ends up on top.

```
offer(x):  in.push(x)
poll():    if out is empty: while in not empty: out.push(in.pop())
           return out.pop()
```

```java
class TwoStackQueue<T> {
    private final Deque<T> in = new ArrayDeque<>(), out = new ArrayDeque<>();

    void offer(T x) { in.push(x); }

    T poll() { shift(); return out.pop(); }      // throws if the queue is empty
    T peek() { shift(); return out.peek(); }     // null if the queue is empty

    boolean isEmpty() { return in.isEmpty() && out.isEmpty(); }
    int size() { return in.size() + out.size(); }

    private void shift() {
        if (out.isEmpty())                       // ONLY when out is empty
            while (!in.isEmpty()) out.push(in.pop());
    }
}
```

**Amortized `O(1)`:** each element is pushed onto `in` once, moved to `out` once, and popped from `out` once. That's at most 4 stack operations per element over its whole lifetime, even though a single `poll` that triggers a transfer costs `Θ(n)`.

> [!warning] Transfer only when `out` is empty
> If you move `in` to `out` while `out` still holds elements, the newer elements land **on top of** older ones, and the next `poll` returns a newer element first. FIFO order is broken.

> [!tip] Why this matters beyond interviews
> Combine it with the min-stack ([[Stacks#5. Min Stack|Stacks § 5]]): if each stack tracks its own minimum, the queue's minimum is `min(in.min, out.min)`. That gives a **queue with `O(1)` min**, which works for any associative operation (`gcd`, `max`, bitwise AND/OR), even ones with no inverse, where a monotonic deque doesn't apply. This "two-stack trick" is a standard way to maintain an aggregate over a sliding window.

### 5.2 Stack from queues

With one queue: to push `x`, enqueue it and then rotate the queue `size − 1` times (dequeue and re-enqueue), so `x` reaches the front. Push is `O(n)`, pop and top are `O(1)`.

```java
class QueueStack {
    private final Deque<Integer> q = new ArrayDeque<>();

    void push(int x) {
        q.offer(x);
        for (int i = 0; i < q.size() - 1; i++) q.offer(q.poll());   // size() is fixed during the loop
    }
    int pop()  { return q.poll(); }
    int top()  { return q.peek(); }
    boolean isEmpty() { return q.isEmpty(); }
}
```

Unlike the queue-from-stacks direction, there's no amortized trick here: some operation must be `Θ(n)` per call in the worst case.

---

## 6. Queue Applications

### 6.1 BFS and level-by-level processing

BFS visits nodes in order of distance from the start because the queue releases them in the order they were discovered. The full treatment is in [[DSA/Graph Representations and Traversals|Graph Representations and Traversals]]; the queue mechanics that matter:

```java
Deque<Integer> q = new ArrayDeque<>();
q.offer(start);
visited[start] = true;                     // mark when ENQUEUED, not when dequeued
int level = 0;
while (!q.isEmpty()) {
    int sz = q.size();                     // snapshot: exactly the nodes of this level
    for (int k = 0; k < sz; k++) {
        int u = q.poll();
        // ... process u at distance `level` ...
        for (int v : adj[u]) {
            if (!visited[v]) {
                visited[v] = true;
                q.offer(v);
            }
        }
    }
    level++;
}
```

> [!warning] Two BFS queue bugs
> - **`for (int k = 0; k < q.size(); k++)`** re-reads the size every iteration while children are being added, so levels mix together. Take the snapshot first.
> - **Marking visited when dequeued** lets the same node be enqueued many times (once per neighbour that sees it before it's processed). The answers may still be right, but the queue can grow to `O(E)` entries, and on dense graphs or grids that's a TLE or MLE.

### 6.2 Sliding time windows

"How many requests in the last 3000 ms?" Keep the timestamps in a queue; drop old ones from the front.

```java
class RecentCounter {
    private final Deque<Integer> q = new ArrayDeque<>();

    int ping(int t) {                       // t is strictly increasing
        q.offer(t);
        while (q.peekFirst() < t - 3000) q.pollFirst();
        return q.size();
    }
}
```

Amortized `O(1)` per call: each timestamp is added once and removed once. A **moving average** over the last `k` values is the same with a running sum: add the new value, and when the queue exceeds `k`, subtract the value you poll.

### 6.3 Round-robin simulation

Rotating a queue (`q.offer(q.poll())`) models taking turns: CPU scheduling with time slices, "hot potato", or the [[Linked Lists#10.1 Josephus problem|Josephus problem]] (rotate `k − 1` times, then remove one: `O(n·k)` total). **Task scheduling with cooldowns** combines a max-heap (pick the most frequent remaining task) with a queue (tasks cooling down, each with the time it becomes available again).

---

## 7. Monotonic Deque — Sliding Window Maximum

Given an array and a window size `k`, output the maximum of every window `a[i−k+1..i]`.

| Approach | Time |
|---|---|
| Scan each window | `O(n·k)` |
| Max-heap with lazy deletion of expired indices | `O(n log n)` |
| `TreeMap` of counts | `O(n log k)` |
| **Monotonic deque** | **`O(n)`** |

### 7.1 The idea

Keep a deque of **indices** whose values are **decreasing** from front to back. The front is always the maximum of the current window.

- When `a[i]` arrives, any element at the back that is `≤ a[i]` can **never** be a window maximum again: `a[i]` is at least as big and will stay in the window longer. Pop those from the back.
- When the front index falls out of the window (`≤ i − k`), pop it from the front.

```
maxSlidingWindow(a, k):
    dq = empty deque of indices              -- a[dq] decreasing from front to back
    for i = 0 to n − 1:
        if dq.front == i − k: dq.popFront()                  -- expired
        while dq not empty and a[dq.back] ≤ a[i]: dq.popBack()   -- dominated
        dq.pushBack(i)
        if i ≥ k − 1: output a[dq.front]
```

```java
static int[] maxSlidingWindow(int[] a, int k) {
    int n = a.length;
    int[] res = new int[n - k + 1];
    Deque<Integer> dq = new ArrayDeque<>();
    for (int i = 0; i < n; i++) {
        if (!dq.isEmpty() && dq.peekFirst() <= i - k) dq.pollFirst();
        while (!dq.isEmpty() && a[dq.peekLast()] <= a[i]) dq.pollLast();
        dq.offerLast(i);
        if (i >= k - 1) res[i - k + 1] = a[dq.peekFirst()];
    }
    return res;
}
```

> [!example]- Trace: `a = [1, 3, -1, -3, 5, 3, 6, 7]`, `k = 3`
> | `i` | `a[i]` | Expired | Popped from back | Deque (values) | Output |
> |---|---|---|---|---|---|
> | 0 | 1 | | | `[1]` | |
> | 1 | 3 | | 1 | `[3]` | |
> | 2 | −1 | | | `[3, −1]` | **3** |
> | 3 | −3 | | | `[3, −1, −3]` | **3** |
> | 4 | 5 | index 1 (3) | −3, −1 | `[5]` | **5** |
> | 5 | 3 | | | `[5, 3]` | **5** |
> | 6 | 6 | | 3, 5 | `[6]` | **6** |
> | 7 | 7 | | 6 | `[7]` | **7** |
>
> Output: `[3, 3, 5, 5, 6, 7]`.

> [!important] Why it's O(n)
> Each index enters the deque once and leaves at most once (from the front or from the back). All the `while` iterations together are bounded by `n`. The same aggregate argument as the monotonic stack ([[Stacks#8. Monotonic Stack|Stacks § 8]]); in fact, the monotonic deque *is* a monotonic stack with one extra operation: expiring from the bottom.

> [!tip] Variants
> - **Sliding window minimum:** keep values **increasing**; pop from the back while `a[back] ≥ a[i]`.
> - Storing **indices** is what makes expiry possible. If you store values, you can't tell whether the front has left the window.
> - Popping with `<` instead of `<=` keeps equal values in the deque. It's still correct (expiry is by index), just slightly more work.

---

## 8. Monotonic Deque Applications

### 8.1 Longest subarray where max − min ≤ limit

A variable-size [[DSA/Sliding Window|sliding window]] that needs the window's maximum **and** minimum. Keep one decreasing deque (max) and one increasing deque (min); shrink from the left while the window is invalid.

```java
static int longestSubarray(int[] a, int limit) {
    Deque<Integer> maxQ = new ArrayDeque<>(), minQ = new ArrayDeque<>();
    int left = 0, best = 0;
    for (int right = 0; right < a.length; right++) {
        while (!maxQ.isEmpty() && a[maxQ.peekLast()] < a[right]) maxQ.pollLast();
        maxQ.offerLast(right);
        while (!minQ.isEmpty() && a[minQ.peekLast()] > a[right]) minQ.pollLast();
        minQ.offerLast(right);
        while ((long) a[maxQ.peekFirst()] - a[minQ.peekFirst()] > limit) {   // long: avoids overflow
            left++;
            if (maxQ.peekFirst() < left) maxQ.pollFirst();
            if (minQ.peekFirst() < left) minQ.pollFirst();
        }
        best = Math.max(best, right - left + 1);
    }
    return best;
}
```

### 8.2 Shortest subarray with sum ≥ K, with negative numbers

With only positive numbers, a plain sliding window works: extending the window always increases the sum. **Negative numbers break that**, because shrinking can increase the sum. Work with prefix sums instead: a subarray `(i, j]` has sum `P[j] − P[i]`, and we want the smallest `j − i` with `P[j] − P[i] ≥ K`.

Keep candidate start indices `i` in a deque with **increasing** `P[i]`:

- **Front:** if `P[j] − P[front] ≥ K`, record `j − front` and pop it. No later `j` can give a shorter subarray from this start.
- **Back:** if `P[back] ≥ P[j]`, pop it. `j` is a better start than `back`: it's later (shorter subarrays) and has a smaller-or-equal prefix (larger sums).

```java
static int shortestSubarray(int[] a, int k) {
    int n = a.length;
    long[] pre = new long[n + 1];                         // long: sums can exceed int
    for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];
    Deque<Integer> dq = new ArrayDeque<>();
    int best = n + 1;
    for (int j = 0; j <= n; j++) {
        while (!dq.isEmpty() && pre[j] - pre[dq.peekFirst()] >= k)
            best = Math.min(best, j - dq.pollFirst());
        while (!dq.isEmpty() && pre[dq.peekLast()] >= pre[j])
            dq.pollLast();
        dq.offerLast(j);
    }
    return best <= n ? best : -1;
}
```

`O(n)`. Prefix sums are covered in [[DSA/Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]].

### 8.3 DP with a sliding-window maximum

Many DP recurrences take the best of the previous `k` states:

```
dp[i] = a[i] + max(dp[i−k], …, dp[i−1])
```

Done naively that's `O(n·k)`. A monotonic deque over `dp` makes each `max` `O(1)` amortized, so the whole DP is `O(n)`. **Constrained subsequence sum** (choose a non-empty subsequence where consecutive chosen indices are at most `k` apart, maximize the sum) is the standard example:

```java
static int constrainedSubsetSum(int[] a, int k) {
    int n = a.length;
    int[] dp = new int[n];                     // best sum of a valid subsequence ending at i
    Deque<Integer> dq = new ArrayDeque<>();    // indices, dp decreasing from front to back
    int best = Integer.MIN_VALUE;
    for (int i = 0; i < n; i++) {
        if (!dq.isEmpty() && dq.peekFirst() < i - k) dq.pollFirst();
        int prev = dq.isEmpty() ? 0 : Math.max(0, dp[dq.peekFirst()]);   // or start fresh at i
        dp[i] = a[i] + prev;
        while (!dq.isEmpty() && dp[dq.peekLast()] <= dp[i]) dq.pollLast();
        dq.offerLast(i);
        best = Math.max(best, dp[i]);
    }
    return best;
}
```

"Jump game VI" (`dp[i] = a[i] + max(dp[i−k..i−1])`, must start at 0 and end at `n − 1`) is the same without the `max(0, …)`. More DP speed-ups of this kind are in [[DSA/Advanced DP|Advanced DP]].

### 8.4 A queue with O(1) max

Keep a normal queue for the elements and a monotonic deque of **values** for the maximum:

```java
class MaxQueue {
    private final Deque<Integer> q = new ArrayDeque<>(), maxDq = new ArrayDeque<>();

    void offer(int x) {
        q.offerLast(x);
        while (!maxDq.isEmpty() && maxDq.peekLast() < x) maxDq.pollLast();   // < keeps duplicates
        maxDq.offerLast(x);
    }

    int poll() {
        int x = q.pollFirst();
        if (x == maxDq.peekFirst()) maxDq.pollFirst();      // int vs Integer: unboxes
        return x;
    }

    int max() { return maxDq.peekFirst(); }
}
```

> [!warning] Storing values: the pop condition must be strict
> With values instead of indices, duplicates must stay. If `offer` popped with `<=`, then after offering `5, 5` the deque would hold one `5`; polling the first `5` would remove it, and `max()` would be wrong while the second `5` is still in the queue.

---

## 9. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| `ArrayList.remove(0)` as dequeue | `Θ(n²)` total | `ArrayDeque` |
| Linked queue: not resetting `tail` on empty | next element lost | `if (head == null) tail = null` |
| `head == tail` meaning both empty and full | full queue looks empty | keep `size`, or waste one slot |
| `(head − 1) % cap` | index `−1` at `head = 0` | `(head − 1 + cap) % cap` |
| `Arrays.copyOf` to grow a wrapped buffer | elements out of order | copy in queue order from `head` |
| Two-stack queue transferring when `out` isn't empty | FIFO order broken | transfer only into an empty `out` |
| `poll()` result unboxed without a check | NPE on empty queue | check `isEmpty()` |
| `PriorityQueue` used as a FIFO queue | wrong order | `ArrayDeque` |
| `k < q.size()` as the BFS level loop bound | levels mixed | snapshot the size |
| Marking BFS visited on dequeue | queue blows up | mark on enqueue |
| Monotonic deque storing values | can't expire elements | store indices |
| Max-queue storing values, popping with `<=` | wrong max after polling a duplicate | `<` |
| Sliding window on arrays with negatives | wrong answer | prefix sums + monotonic deque |
| `int` prefix sums | overflow | `long` |

---

## 10. Trick Questions and Special Cases

> [!question]- Queue from two stacks: what's the worst case for a single `poll`, and why is it still called O(1)?
> A single `poll` can cost `Θ(n)` when `out` is empty and `in` holds `n` elements. But each element is transferred at most once in its lifetime, so any sequence of `m` operations costs `O(m)` in total: `O(1)` **amortized**. It's not `O(1)` worst case, so it's a poor choice when every individual operation must be fast (real-time systems).

> [!question]- Can you implement a stack with queues in O(1) amortized per operation?
> Not with the standard constructions: they make either `push` or `pop` cost `Θ(n)` on **every** call (rotating the queue), so there's no amortization to be had. The asymmetry with the two-stack queue comes from the fact that moving elements between stacks reverses them, which turns LIFO into FIFO in one transfer, while moving elements between queues preserves their order and gains nothing.

> [!question]- A circular buffer with capacity 5 uses `head` and `tail` indices and no size counter. How many elements can it hold?
> 4. One slot must stay empty so that "full" (`(tail + 1) % 5 == head`) and "empty" (`head == tail`) look different. With a separate `size` field, all 5 are usable.

> [!question]- `Queue<Integer> q = new PriorityQueue<>(); q.offer(3); q.offer(1); q.offer(2);` — what does `q.poll()` return? What does `System.out.println(q)` show first?
> `poll()` returns `1`, the smallest, not `3`, the oldest. Printing shows the heap's internal array, which isn't guaranteed to be sorted. For three elements it happens to be `[1, 3, 2]`, but in general neither the iteration order nor `toString` is sorted.

> [!question]- Does `ArrayDeque` have a `get(int index)` method?
> No. It's a circular array internally, but the API doesn't expose indexing. To read the `i`-th element you'd iterate. If you need indexing, use your own ring buffer ([[#3.2 A growable deque|§3.2]]), or an `ArrayList` if you don't need fast removal at the front.

> [!question]- `LinkedList<Integer> q` with `q.offer(null)` — what does `q.poll()` return, and how do you tell it apart from an empty queue?
> It returns `null`, exactly as it would for an empty queue. You can't tell the two apart from `poll()` alone; check `isEmpty()` first. This ambiguity is why `ArrayDeque` (and most of the newer queue classes) reject `null` elements outright.

> [!question]- Sliding window maximum with k = 1? With k = n?
> With `k = 1`, every window has one element, so the output is the array itself. With `k = n`, there's a single window, and the output is one value, the overall maximum. Both work with the standard code; `n − k + 1` is the output length in every case.

> [!question]- Why can't the sliding-window technique find the shortest subarray with sum ≥ K when the array has negative numbers?
> Two-pointer sliding windows rely on monotonicity: extending the window should never decrease the sum, and shrinking should never increase it. A negative number breaks both. For `[2, -1, 2]` with `K = 3`, the only valid subarray is the whole array. Prefix sums with a monotonic deque restore a usable structure: increasing prefix values as candidate starts.

> [!question]- In the sliding window maximum, why is it safe to discard a smaller element that's still inside the window?
> Because the new, larger element arrived **later**, it stays in every future window that the smaller one is in, and it's at least as large. So the smaller element can never again be the maximum of any window. That "dominated forever" argument is the whole justification for the monotonic deque.

> [!question]- BFS with `visited` marked when dequeued — wrong answers or just slow?
> For shortest distances in an unweighted graph, still correct: the first time a node is dequeued is still at its minimum distance, as long as later duplicate dequeues are skipped. But a node can be enqueued once per incoming edge, so the queue can hold `Θ(E)` entries instead of `Θ(V)`. On a dense graph that's quadratic memory. Marking at enqueue time is both correct and efficient.

> [!question]- `for (int i = 0; i < q.size() - 1; i++) q.offer(q.poll());` — does this rotate correctly when pushing in the queue-based stack?
> Yes. Each iteration removes one element and adds one, so `q.size()` doesn't change during the loop, and the loop runs exactly `size − 1` times. The same loop shape **does** break in BFS level processing, where the loop body adds more elements than it removes.

> [!question]- Max queue: offer 5, offer 5, poll, max()?
> `5`. With values stored and a strict pop condition (`<`), the deque holds both 5s; polling removes one. If the deque popped with `<=`, it would hold one 5, polling would remove it, and `max()` would fail on a non-empty queue.

---

## 11. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `ArrayList.remove(0)` as dequeue | `O(n)` per call | shifts |
| Two-stack queue `poll` | `O(1)` amortized, `Θ(n)` worst | each element moves once |
| Queue-based stack `push` | `Θ(n)` | rotation |
| `head == tail` with no size field | empty **or** full | waste one slot or count |
| Capacity `c`, one slot wasted | holds `c − 1` | |
| `(0 − 1) % 8` in Java | `-1` | use `+ cap` or `& (cap − 1)` |
| `-1 & 7` | `7` | power-of-two mask wraps correctly |
| `queue.poll()` when empty | `null` | `remove()` throws |
| `queue.add(x)` on a full bounded queue | `IllegalStateException` | `offer` returns `false` |
| `PriorityQueue.poll()` | smallest, not oldest | not FIFO |
| `ArrayDeque.offer(null)` | `NullPointerException` | `null` rejected |
| `deque.push(x)` then `deque.poll()` | returns `x` | both at the front |
| Sliding window max | `O(n)` | each index in/out once |
| Monotonic deque for max | decreasing front → back | front is the max |
| Shortest subarray ≥ K with negatives | prefix sums + increasing deque | window isn't monotone |
| `dp[i] = a[i] + max(dp[i−k..i−1])` | `O(n)` with a deque | sliding window max over `dp` |

---

## 12. Summary

- A queue is FIFO; a deque allows both ends. All core operations are `O(1)`.
- Implement with a linked list (head + tail) or, better, a **circular buffer**: front at `head`, back at `(head + size) mod capacity`. Distinguish full from empty with a `size` field, wrap backwards with `+ capacity`, and resize by copying in queue order.
- In Java, use `ArrayDeque` for queues, stacks, and deques. `poll`/`peek` return `null` when empty, `PriorityQueue` is not FIFO, and `ArrayList.remove(0)` is not a queue.
- **Two stacks make a queue** with `O(1)` amortized operations (transfer only when `out` is empty), and with per-stack aggregates they give a queue with `O(1)` min/max/gcd.
- BFS: snapshot the size per level, mark visited on enqueue.
- The **monotonic deque** stores indices with monotone values; expire from the front, discard dominated elements from the back. It gives sliding window max/min in `O(n)`, handles windows needing both max and min, finds shortest subarrays with negative numbers via prefix sums, and turns "max over the last `k` DP states" from `O(nk)` into `O(n)`.

## Related

- [[DSA/00 - Syllabus|00 - Syllabus]]
- Previous: [[Stacks|Stacks]] · Next: [[Hash Tables|Hash Tables]]
- [[Stacks#8. Monotonic Stack|Stacks § 8]]: the monotonic stack
- [[DSA/Sliding Window|Sliding Window]]: variable-size windows
- [[DSA/Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]]
- [[DSA/Graph Representations and Traversals|Graph Representations and Traversals]]: BFS, multi-source BFS
- [[DSA/Shortest Path Algorithms|Shortest Path Algorithms]]: 0-1 BFS with a deque
- [[DSA/Heaps and Priority Queues|Heaps and Priority Queues]]: priority-ordered queues
- [[DSA/Advanced DP|Advanced DP]]: DP optimizations
