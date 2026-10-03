# Linked Lists

A <span class="hl-blue">linked list</span> is a sequence of **nodes**, each holding a value and a reference to the next node. Unlike an array, the nodes can be anywhere in memory, so there's no `O(1)` access by index. In exchange, inserting or removing a node is `O(1)` **once you have a reference to the right place**: you just redirect a pointer or two.

Linked lists are less common in production Java than arrays (`ArrayList` and `ArrayDeque` usually win), but they are everywhere in interviews. They're also the building block of hash-table chaining, LRU caches, adjacency lists, and the free lists inside allocators. Almost every linked-list problem comes down to a few techniques: a **dummy head**, **pointer reversal**, and **fast/slow pointers**. This note covers each of them, with the edge cases that break them.

## Contents

- [[#1. Nodes and Terminology|1. Nodes and Terminology]]
- [[#2. Variants|2. Variants]]
- [[#3. Basic Operations|3. Basic Operations]]
- [[#4. The Dummy (Sentinel) Node|4. The Dummy (Sentinel) Node]]
- [[#5. Doubly Linked Lists and the LRU Cache|5. Doubly Linked Lists and the LRU Cache]]
- [[#6. Reversal|6. Reversal]]
- [[#7. Fast and Slow Pointers|7. Fast and Slow Pointers]]
- [[#8. Merging and Combining Lists|8. Merging and Combining Lists]]
- [[#9. Rearrangement Patterns|9. Rearrangement Patterns]]
- [[#10. Circular Lists and the Josephus Problem|10. Circular Lists and the Josephus Problem]]
- [[#11. Java's LinkedList|11. Java's LinkedList]]
- [[#12. Common Mistakes|12. Common Mistakes]]
- [[#13. Trick Questions and Special Cases|13. Trick Questions and Special Cases]]
- [[#14. Quick Reference — Non-Obvious Outcomes|14. Quick Reference — Non-Obvious Outcomes]]
- [[#15. Summary|15. Summary]]

---

## 1. Nodes and Terminology

```java
// The node class used by LeetCode and throughout this note
class ListNode {
    int val;
    ListNode next;
    ListNode() {}
    ListNode(int val) { this.val = val; }
    ListNode(int val, ListNode next) { this.val = val; this.next = next; }
}
```

```
head
 │
 ▼
[3|•]──►[7|•]──►[1|•]──►[9|/]
                          ▲
                         tail        (/ = null: end of list)
```

> [!note] Definitions
> - The <span class="hl-blue">head</span> is the first node; the list is identified by a reference to it. An **empty list** is `head == null`.
> - The <span class="hl-blue">tail</span> is the last node; its `next` is `null` (in a non-circular list).
> - A list is a **recursive** structure: either empty, or a node followed by a list. This is why many list algorithms have a short recursive form ([[DSA/01 - Foundations/02 - Recursion#6.4 Recursion over data structures|Recursion § 6.4]]).

### 1.1 Arrays vs. linked lists

| Operation | Array / `ArrayList` | Singly linked list | Doubly linked list |
|---|---|---|---|
| Access `i`-th element | `O(1)` | `O(i)` | `O(min(i, n − i))` |
| Insert / delete at front | `O(n)` | `O(1)` | `O(1)` |
| Insert / delete at back | `O(1)` amortized | `O(1)` insert with a tail pointer; delete `O(n)` | `O(1)` |
| Insert / delete **given a node** | — | insert after it `O(1)`; delete it needs the **previous** node | `O(1)` |
| Search by value | `O(n)` (`O(log n)` if sorted) | `O(n)`, even if sorted | `O(n)` |
| Extra memory per element | none | one reference | two references |
| Cache behaviour | excellent (contiguous) | poor (nodes scattered) | poor |

> [!warning] "Linked-list insertion is O(1)" has a condition attached
> Only if you already hold a reference to the position. Inserting at index `i` means walking `i` nodes first, so "insert in the middle" is `O(n)` for linked lists **too**. In practice, an `ArrayList` insert in the middle (one `System.arraycopy`) often beats a `LinkedList` insert at the same index (a pointer-chasing walk), despite the identical big-O.

---

## 2. Variants

| Variant | Structure | Typical use |
|---|---|---|
| **Singly linked** | `next` only | stacks, hash-table chains, most interview problems |
| **Doubly linked** | `prev` and `next` | deques, LRU caches, `java.util.LinkedList`; `O(1)` removal given the node |
| **Circular** | the tail's `next` points back to the head | round-robin scheduling, Josephus, circular buffers of nodes |
| **With sentinels** | dummy node(s) at the ends that hold no data | removes `null` special cases ([[#4. The Dummy (Sentinel) Node|§4]]) |

> [!info]- Two variants you'll hear about but rarely write
> - **XOR linked list.** Each node stores `prev XOR next` in a single field, so a doubly linked list costs one pointer per node. Traversal needs the previous address to recover the next one. It's impossible in Java (you can't XOR references, and the GC moves objects) and rarely worth it elsewhere.
> - **Skip list.** A sorted linked list with extra "express lane" levels. Each node is promoted to the next level with probability ½, so search, insert, and delete are `O(log n)` **expected**. It's a randomized alternative to balanced trees; Java's `ConcurrentSkipListMap`/`ConcurrentSkipListSet` are built on it. See [[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]] for the deterministic alternatives.

---

## 3. Basic Operations

### 3.1 Traverse, length, search

```
length(head):
    count = 0; cur = head
    while cur ≠ null:
        count += 1
        cur = cur.next
    return count
```

```java
static int length(ListNode head) {
    int count = 0;
    for (ListNode cur = head; cur != null; cur = cur.next) count++;
    return count;
}

static ListNode find(ListNode head, int target) {
    for (ListNode cur = head; cur != null; cur = cur.next)
        if (cur.val == target) return cur;
    return null;
}
```

> [!important] Never move `head` itself
> Walk with a separate `cur` variable. Writing `while (head != null) head = head.next;` inside a method only changes the local copy, which is harmless, but in code that keeps using `head` afterwards (or in a field), the start of the list is lost.

### 3.2 Insert

```java
static ListNode insertAtHead(ListNode head, int val) {
    return new ListNode(val, head);           // works for an empty list too
}

static void insertAfter(ListNode node, int val) {
    node.next = new ListNode(val, node.next); // order matters: read node.next before overwriting it
}
```

To append in `O(1)`, keep a `tail` reference alongside `head` and update it on every append. Without one, appending is `O(n)` and building a list of `n` elements by appending is `O(n²)`.

### 3.3 Delete

A singly linked node can't unlink itself: you need the node **before** it.

```
deleteValue(head, target):              -- delete the first node with val = target
    if head == null: return null
    if head.val == target: return head.next      -- the head is a special case...
    prev = head
    while prev.next ≠ null and prev.next.val ≠ target:
        prev = prev.next
    if prev.next ≠ null:
        prev.next = prev.next.next
    return head
```

The head special case disappears with a dummy node ([[#4. The Dummy (Sentinel) Node|§4]]).

> [!info]- Deleting a node when you're given only that node
> Without the previous node, you can't unlink it. The standard trick **copies the next node's value into this one and unlinks the next node instead**:
> ```java
> static void deleteNode(ListNode node) {     // node is not the tail
>     node.val = node.next.val;
>     node.next = node.next.next;
> }
> ```
> Limits: it **can't delete the tail** (there's no next node to copy from), and it changes node identity. Any outside reference to the original next node now points to a node that's no longer in the list, and the reference to `node` now holds a different value. It's a puzzle answer, not a general technique.

---

## 4. The Dummy (Sentinel) Node

Most linked-list bugs are special cases at the head: deleting the head, inserting before it, or building a result list that starts empty. A <span class="hl-blue">dummy node</span> placed in front of the real head turns all of them into the general case, because every real node now has a predecessor.

```
deleteAll(head, target):                -- delete every node with val = target
    dummy = new node; dummy.next = head
    prev = dummy
    while prev.next ≠ null:
        if prev.next.val == target:
            prev.next = prev.next.next   -- don't advance: the new prev.next needs checking too
        else:
            prev = prev.next
    return dummy.next                    -- the head may have changed
```

```java
static ListNode removeElements(ListNode head, int target) {
    ListNode dummy = new ListNode(0, head);
    ListNode prev = dummy;
    while (prev.next != null) {
        if (prev.next.val == target) prev.next = prev.next.next;
        else prev = prev.next;
    }
    return dummy.next;
}
```

> [!tip] When to reach for a dummy
> - The head might be removed or replaced (deletions, reversal of a prefix, partitioning).
> - You're **building** a new list node by node (merging, adding numbers, filtering): `tail = dummy`, then `tail.next = newNode; tail = tail.next;`, and return `dummy.next`.
>
> Return `dummy.next`, **not** `head`. The original `head` may no longer be the first node, or may not be in the list at all.

---

## 5. Doubly Linked Lists and the LRU Cache

With a `prev` pointer, a node can unlink itself in `O(1)`. Two sentinels, one at each end, mean `prev` and `next` are never `null` for a real node, so insertion and removal have no special cases at all.

```
head ⇄ [A] ⇄ [B] ⇄ [C] ⇄ tail          (head and tail are sentinels; empty list: head ⇄ tail)
```

```
insertAfter(p, x):              remove(x):
    x.prev = p                      x.prev.next = x.next
    x.next = p.next                 x.next.prev = x.prev
    p.next.prev = x
    p.next = x
```

```java
class DoublyLinkedList {
    static class Node {
        int key, val;
        Node prev, next;
        Node(int key, int val) { this.key = key; this.val = val; }
    }

    private final Node head = new Node(0, 0), tail = new Node(0, 0);   // sentinels
    private int size = 0;

    DoublyLinkedList() {
        head.next = tail;
        tail.prev = head;
    }

    void addFirst(Node x) { insertAfter(head, x); }
    void addLast(Node x)  { insertAfter(tail.prev, x); }

    void insertAfter(Node p, Node x) {
        x.prev = p;
        x.next = p.next;
        p.next.prev = x;          // must come BEFORE p.next = x
        p.next = x;
        size++;
    }

    void remove(Node x) {
        x.prev.next = x.next;
        x.next.prev = x.prev;
        x.prev = x.next = null;   // optional: helps catch use-after-remove bugs
        size--;
    }

    Node removeLast() {           // null if empty
        if (size == 0) return null;
        Node x = tail.prev;
        remove(x);
        return x;
    }

    int size() { return size; }
}
```

![[Linked Lists - Doubly Linked Insert.excalidraw|800]]

> [!warning] The order of the four pointer writes in `insertAfter`
> If you write `p.next = x` before `p.next.prev = x`, then `p.next` already **is** `x`, so the second write sets `x.prev = x`, and the old successor still points back to `p`. The rule: set the new node's own two pointers first (they don't disturb anything), then update the neighbour that you reach **through** `p.next` before overwriting `p.next`.

### 5.1 LRU cache — hash map + doubly linked list

A <span class="hl-blue">least-recently-used (LRU) cache</span> of capacity `c` supports `get(key)` and `put(key, value)` in `O(1)`. When it's full, `put` evicts the key that was used least recently.

- A **hash map** finds a key's node in `O(1)`.
- A **doubly linked list** keeps nodes in recency order: most recent at the front, least recent at the back. Moving a node to the front is `remove` + `addFirst`, both `O(1)` because the node knows its neighbours.

```
get(key):
    if key not in map: return −1
    node = map[key]; move node to front
    return node.val

put(key, value):
    if key in map:
        update map[key].val; move it to front; return
    if size == capacity:
        lru = remove last node; delete lru.key from map     -- the node must store its key
    node = new node(key, value); add to front; map[key] = node
```

```java
class LRUCache {
    private final int capacity;
    private final Map<Integer, DoublyLinkedList.Node> map = new HashMap<>();
    private final DoublyLinkedList list = new DoublyLinkedList();   // front = most recent

    LRUCache(int capacity) { this.capacity = capacity; }

    public int get(int key) {
        DoublyLinkedList.Node x = map.get(key);
        if (x == null) return -1;
        list.remove(x);
        list.addFirst(x);
        return x.val;
    }

    public void put(int key, int value) {
        if (capacity <= 0) return;
        DoublyLinkedList.Node x = map.get(key);
        if (x != null) {                      // update counts as a "use"
            x.val = value;
            list.remove(x);
            list.addFirst(x);
            return;
        }
        if (map.size() == capacity) {
            DoublyLinkedList.Node lru = list.removeLast();
            map.remove(lru.key);              // this is why nodes store their key
        }
        x = new DoublyLinkedList.Node(key, value);
        list.addFirst(x);
        map.put(key, x);
    }
}
```

> [!warning] LRU details that fail hidden tests
> - **The node must store its key.** Eviction finds the node through the list, then must remove the right entry from the map.
> - **`put` on an existing key** updates the value *and* makes it most recent, without evicting anything (the size doesn't change).
> - **Evict before inserting**, and only when the key is new. Evicting on every `put` at capacity throws out an entry when updating an existing key.
> - `get` of a missing key must **not** change the recency order.

Java's built-in shortcut is a `LinkedHashMap` in access order with `removeEldestEntry` overridden; see [[DSA/02 - Linear Data Structures/06 - Hash Tables|Hash Tables]].

---

## 6. Reversal

### 6.1 Iterative reversal

Walk the list and turn each `next` pointer around. Three references: `prev` (already reversed part), `cur` (being processed), and `next` (saved before `cur.next` is overwritten).

```
reverse(head):
    prev = null; cur = head
    while cur ≠ null:
        next = cur.next        -- save, or the rest of the list is lost
        cur.next = prev        -- turn the pointer around
        prev = cur
        cur = next
    return prev                -- the old tail is the new head
```

```java
static ListNode reverse(ListNode head) {
    ListNode prev = null, cur = head;
    while (cur != null) {
        ListNode next = cur.next;
        cur.next = prev;
        prev = cur;
        cur = next;
    }
    return prev;
}
```

```
before:  null   1 → 2 → 3 → null
         prev  cur
step 1:  null ← 1    2 → 3 → null
                prev cur
step 2:  null ← 1 ← 2    3 → null
                    prev cur
step 3:  null ← 1 ← 2 ← 3    null
                        prev  cur      → return prev (3)
```

![[Linked Lists - Iterative Reversal.excalidraw|800]]

`O(n)` time, `O(1)` space. Empty and single-node lists work without special cases.

### 6.2 Recursive reversal

```java
static ListNode reverseRec(ListNode head) {
    if (head == null || head.next == null) return head;   // 0 or 1 nodes
    ListNode newHead = reverseRec(head.next);             // reverse the rest
    head.next.next = head;      // the old second node now points back to head
    head.next = null;           // head becomes the tail
    return newHead;
}
```

> [!warning] Recursive reversal uses O(n) stack
> One frame per node. A list of 10⁵ nodes can throw `StackOverflowError` in Java ([[DSA/01 - Foundations/02 - Recursion#9. Stack Overflow Limits in Java|Recursion § 9]]). Interviewers sometimes ask for the recursive version specifically; be ready to state its space cost. Forgetting `head.next = null` leaves a two-node cycle between the first two nodes.

### 6.3 Reverse a sublist (positions `left..right`, 1-indexed)

Walk to the node **before** position `left`. Then, `right − left` times, take the node right after the reversed block's tail and move it to the front of the block.

```java
static ListNode reverseBetween(ListNode head, int left, int right) {
    ListNode dummy = new ListNode(0, head);          // left may be 1
    ListNode before = dummy;
    for (int i = 1; i < left; i++) before = before.next;
    ListNode cur = before.next;                       // stays the block's tail throughout
    for (int i = 0; i < right - left; i++) {
        ListNode move = cur.next;
        cur.next = move.next;
        move.next = before.next;
        before.next = move;
    }
    return dummy.next;
}
```

> [!example]- Trace: `1 → 2 → 3 → 4 → 5`, `left = 2`, `right = 4`
> `before = 1`, `cur = 2`.
> - Move `3` to the front of the block: `1 → 3 → 2 → 4 → 5`.
> - Move `4` to the front of the block: `1 → 4 → 3 → 2 → 5`. ✓
>
> `cur` (node 2) never moves; it just keeps getting pushed back as nodes jump over it.

### 6.4 Reverse in groups of `k`

Reverse each consecutive block of `k` nodes; a final block shorter than `k` stays as it is.

```java
static ListNode reverseKGroup(ListNode head, int k) {
    ListNode dummy = new ListNode(0, head);
    ListNode groupPrev = dummy;
    while (true) {
        ListNode kth = groupPrev;                          // find the k-th node ahead
        for (int i = 0; i < k && kth != null; i++) kth = kth.next;
        if (kth == null) break;                            // fewer than k left
        ListNode groupNext = kth.next;
        ListNode prev = groupNext, cur = groupPrev.next;   // reverse; the block's tail links to groupNext
        while (cur != groupNext) {
            ListNode next = cur.next;
            cur.next = prev;
            prev = cur;
            cur = next;
        }
        ListNode oldFirst = groupPrev.next;                // now the block's last node
        groupPrev.next = kth;
        groupPrev = oldFirst;
    }
    return dummy.next;
}
```

`O(n)` time, `O(1)` space. Starting `prev` at `groupNext` instead of `null` reconnects the reversed block to the rest of the list for free. With `k = 2` this is "swap nodes in pairs".

> [!warning] Check that a full group exists **before** reversing
> Reversing first and then discovering the group was short means undoing it. Count ahead `k` nodes first. Also note `k = 1` must return the list unchanged, which this code does (each "reversal" is a single node).

---

## 7. Fast and Slow Pointers

Two pointers walk the list at different speeds, usually 1 and 2 nodes per step (the <span class="hl-blue">tortoise and hare</span>). In one pass they find the middle, detect cycles, and find cycle entrances.

### 7.1 Middle node — which middle?

```java
// Even length → SECOND middle:  1 2 [3] 4      odd → the middle: 1 2 [3] 4 5
static ListNode middleSecond(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
    }
    return slow;
}

// Even length → FIRST middle:   1 [2] 3 4      odd → the middle: 1 2 [3] 4 5
static ListNode middleFirst(ListNode head) {       // head != null
    ListNode slow = head, fast = head.next;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
    }
    return slow;
}
```

> [!important] Which one you need
> - **"Return the middle node"** problems usually want the **second** middle for even lengths.
> - **Splitting a list in half** (merge sort, palindrome check, reorder) needs the **first** middle, so you can cut with `right = mid.next; mid.next = null;`. With the second middle, a 2-node list splits into "2 nodes" and "empty", and a recursive merge sort recurses on the same 2 nodes forever.

### 7.2 Cycle detection (Floyd's algorithm)

If there's a cycle, the fast pointer enters it and eventually laps the slow one: once both are inside, the gap between them shrinks by exactly 1 each step, so it must hit 0. If there's no cycle, `fast` reaches `null`.

```
hasCycle(head):
    slow = fast = head
    while fast ≠ null and fast.next ≠ null:
        slow = slow.next
        fast = fast.next.next
        if slow == fast: return true        -- compare AFTER moving
    return false
```

```java
static boolean hasCycle(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow == fast) return true;      // reference comparison: same node
    }
    return false;
}
```

`O(n)` time, `O(1)` space. The alternative, a `HashSet<ListNode>` of visited nodes, is `O(n)` space.

### 7.3 Where does the cycle start?

After the meeting, put one pointer back at the head and move **both** one step at a time. They meet at the cycle's first node.

```java
static ListNode detectCycle(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow == fast) {
            ListNode p = head;
            while (p != slow) {
                p = p.next;
                slow = slow.next;
            }
            return p;
        }
    }
    return null;
}
```

![[Linked Lists - Floyd Cycle Detection.excalidraw|800]]

> [!info]- Why the second phase lands on the cycle start
> Let `a` = distance from the head to the cycle start, `c` = cycle length, and `b` = distance from the cycle start to the meeting point (along the cycle). When they meet, slow has walked `a + b` and fast has walked `2(a + b)`. Fast's extra distance is a whole number of laps: `2(a + b) − (a + b) = kc`, so `a + b = kc` and
> ```
> a = kc − b = (k − 1)·c + (c − b)
> ```
> `c − b` is the distance from the meeting point forward to the cycle start. So a pointer starting at the head and a pointer starting at the meeting point, both moving 1 step at a time, arrive at the cycle start together after `a` steps (the second one goes around `k − 1` extra full laps). Also, slow is caught before it completes a single lap, which is why the first phase is `O(n)`.

**Cycle length:** from the meeting point, walk one pointer around until it returns, counting steps.

### 7.4 Floyd on arrays: find the duplicate number

An array of `n + 1` integers with values in `1..n` contains at least one duplicate. Treat it as a function `i → nums[i]`: following it from index 0 is a walk through a linked list, and a duplicate value means two indices point to the same next index, which is a cycle entrance. Index 0 is never a target (values are ≥ 1), so it's a valid "head".

```java
static int findDuplicate(int[] nums) {          // O(n) time, O(1) space, array not modified
    int slow = 0, fast = 0;
    do {
        slow = nums[slow];
        fast = nums[nums[fast]];
    } while (slow != fast);
    slow = 0;
    while (slow != fast) {
        slow = nums[slow];
        fast = nums[fast];
    }
    return slow;
}
```

The same "implicit linked list" view solves **happy number** (iterate the digit-square sum; a cycle that doesn't contain 1 means unhappy) and any "iterate `x → f(x)` on a finite set" question. Every such sequence eventually enters a cycle, the "ρ shape" that also underlies Pollard's rho factorization.

### 7.5 `n`-th node from the end

Move `fast` `n` steps ahead, then move both until `fast` is at the last node. `slow` is then **before** the target, which is what deletion needs.

```java
static ListNode removeNthFromEnd(ListNode head, int n) {   // 1 ≤ n ≤ length
    ListNode dummy = new ListNode(0, head);                 // n = length removes the head
    ListNode fast = dummy, slow = dummy;
    for (int i = 0; i < n; i++) fast = fast.next;
    while (fast.next != null) {
        fast = fast.next;
        slow = slow.next;
    }
    slow.next = slow.next.next;
    return dummy.next;
}
```

---

## 8. Merging and Combining Lists

### 8.1 Merge two sorted lists

```java
static ListNode merge(ListNode a, ListNode b) {
    ListNode dummy = new ListNode(0), tail = dummy;
    while (a != null && b != null) {
        if (a.val <= b.val) { tail.next = a; a = a.next; }   // <= keeps equal elements in order (stable)
        else                { tail.next = b; b = b.next; }
        tail = tail.next;
    }
    tail.next = (a != null) ? a : b;                         // attach the leftover in O(1)
    return dummy.next;
}
```

`O(n + m)` time, `O(1)` extra space: it **relinks** the existing nodes rather than creating new ones.

### 8.2 Merge `k` sorted lists

| Method | Time (N total nodes) | Space |
|---|---|---|
| Merge one at a time into a running result | `O(N·k)` | `O(1)` |
| Min-heap of the `k` current heads | `O(N log k)` | `O(k)` |
| Pairwise (divide and conquer) | `O(N log k)` | `O(1)` iterative / `O(log k)` recursive |

```java
static ListNode mergeKLists(ListNode[] lists) {
    PriorityQueue<ListNode> pq = new PriorityQueue<>(Comparator.comparingInt(node -> node.val));
    for (ListNode head : lists) if (head != null) pq.offer(head);   // skip empty lists
    ListNode dummy = new ListNode(0), tail = dummy;
    while (!pq.isEmpty()) {
        ListNode node = pq.poll();
        tail.next = node;
        tail = node;
        if (node.next != null) pq.offer(node.next);
    }
    return dummy.next;
}
```

> [!warning] Two heap pitfalls
> - **`null` heads:** `PriorityQueue` rejects `null`, and a comparator dereferencing `null.val` throws. Skip empty lists.
> - **`(x, y) -> x.val - y.val`** overflows for values near `±2³¹` and then orders incorrectly. Use `Comparator.comparingInt` or `Integer.compare`. Heaps are covered in [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|Heaps and Priority Queues]].

### 8.3 Intersection of two lists

Two singly linked lists may merge into a shared tail (a "Y" shape). Find the first shared **node**. Let each pointer walk its own list and then switch to the other list's head: both travel `lenA + lenB` steps and meet at the intersection, or both reach `null` together if there's none.

```java
static ListNode getIntersectionNode(ListNode a, ListNode b) {
    ListNode p = a, q = b;
    while (p != q) {
        p = (p == null) ? b : p.next;    // switch AFTER stepping onto null
        q = (q == null) ? a : q.next;
    }
    return p;                            // the shared node, or null
}
```

![[Linked Lists - Intersection by Switching Heads.excalidraw|800]]

> [!warning] Two ways to get this wrong
> - **Comparing values instead of nodes.** In `A = 4 → 1 → 8 → 4 → 5` and `B = 5 → 6 → 1 → 8 → 4 → 5`, the shared node is the `8`. The two `1`s have the same value but are different nodes. Use `==` on node references.
> - **Switching lists without passing through `null`** (`p = (p.next == null) ? b : p.next`). With no intersection, `p` and `q` are never both `null` at the same moment, so the loop runs forever.

### 8.4 Add two numbers stored as lists

Digits in **reverse** order (least significant first), so addition proceeds naturally from the head:

```java
static ListNode addTwoNumbers(ListNode a, ListNode b) {
    ListNode dummy = new ListNode(0), tail = dummy;
    int carry = 0;
    while (a != null || b != null || carry != 0) {     // carry != 0: 5 + 5 = 10 needs a new node
        int sum = carry;
        if (a != null) { sum += a.val; a = a.next; }
        if (b != null) { sum += b.val; b = b.next; }
        tail.next = new ListNode(sum % 10);
        tail = tail.next;
        carry = sum / 10;
    }
    return dummy.next;
}
```

Converting each list to a `long`, adding, and converting back fails as soon as the numbers have more than 18 digits. If the digits are stored most-significant first, reverse both lists first, or push the digits onto two stacks ([[DSA/02 - Linear Data Structures/04 - Stacks|Stacks]]) and pop to add from the least significant end.

---

## 9. Rearrangement Patterns

### 9.1 Palindrome list in O(1) space

Find the first middle, reverse the second half, compare the two halves, and reverse the second half back to restore the input.

```java
static boolean isPalindrome(ListNode head) {
    if (head == null || head.next == null) return true;
    ListNode mid = middleFirst(head);
    ListNode second = reverse(mid.next);
    boolean ok = true;
    for (ListNode p = head, q = second; q != null; p = p.next, q = q.next) {
        if (p.val != q.val) { ok = false; break; }
    }
    mid.next = reverse(second);        // restore the original list
    return ok;
}
```

For odd lengths, the middle node belongs to the first half and is never compared, which is correct. Copying the values into an array and checking it with two pointers is simpler, but uses `O(n)` space.

### 9.2 Reorder list: `L0 → Ln → L1 → Ln−1 → …`

Same three steps: split at the first middle, reverse the second half, then interleave the two halves.

```java
static void reorderList(ListNode head) {
    if (head == null || head.next == null) return;
    ListNode mid = middleFirst(head);
    ListNode second = reverse(mid.next);
    mid.next = null;                         // cut, or the result contains a cycle
    ListNode first = head;
    while (second != null) {
        ListNode n1 = first.next, n2 = second.next;
        first.next = second;
        second.next = n1;
        first = n1;
        second = n2;
    }
}
```

### 9.3 Remove duplicates from a sorted list

```java
// Keep one copy of each value: 1 1 2 3 3 → 1 2 3
static ListNode deleteDuplicates(ListNode head) {
    ListNode cur = head;
    while (cur != null && cur.next != null) {
        if (cur.next.val == cur.val) cur.next = cur.next.next;   // don't advance: there may be a third copy
        else cur = cur.next;
    }
    return head;
}

// Remove EVERY value that appears more than once: 1 2 3 3 4 4 5 → 1 2 5
static ListNode deleteAllDuplicates(ListNode head) {
    ListNode dummy = new ListNode(0, head), prev = dummy;   // the head itself may be removed
    while (prev.next != null) {
        ListNode cur = prev.next;
        if (cur.next != null && cur.next.val == cur.val) {
            int v = cur.val;
            while (cur != null && cur.val == v) cur = cur.next;   // skip the whole run
            prev.next = cur;
        } else {
            prev = cur;
        }
    }
    return dummy.next;
}
```

### 9.4 Partition around `x` (stable)

All nodes `< x` before all nodes `≥ x`, each group in its original order. Build two lists with two dummies, then join them.

```java
static ListNode partition(ListNode head, int x) {
    ListNode lessDummy = new ListNode(0), geDummy = new ListNode(0);
    ListNode less = lessDummy, ge = geDummy;
    for (ListNode cur = head; cur != null; cur = cur.next) {
        if (cur.val < x) { less.next = cur; less = cur; }
        else             { ge.next = cur;   ge = cur; }
    }
    ge.next = null;                  // ESSENTIAL: the last ≥ node may still point into the "less" list
    less.next = geDummy.next;
    return lessDummy.next;
}
```

> [!warning] Terminate every list you build out of reused nodes
> The last node appended to `ge` keeps whatever `next` it had in the original list, possibly a node now in the `less` list. Without `ge.next = null`, the result contains a **cycle**, and printing it loops forever. The same applies to odd/even splitting and to any "split into several lists" problem.

### 9.5 Rotate right by `k`

`k` can be much larger than the length (up to `2 × 10⁹` in the usual problem), so reduce it modulo the length, then make the list circular and break it in the right place.

```java
static ListNode rotateRight(ListNode head, int k) {
    if (head == null || head.next == null) return head;
    int n = 1;
    ListNode tail = head;
    while (tail.next != null) { tail = tail.next; n++; }
    k %= n;
    if (k == 0) return head;
    ListNode newTail = head;
    for (int i = 0; i < n - k - 1; i++) newTail = newTail.next;
    ListNode newHead = newTail.next;
    newTail.next = null;
    tail.next = head;
    return newHead;
}
```

### 9.6 Sort a list: merge sort

Merge sort suits linked lists: splitting is a middle-find, merging is relinking with `O(1)` extra space, and no random access is needed. Quicksort and heap sort rely on random access and do poorly here.

```java
static ListNode sortList(ListNode head) {
    if (head == null || head.next == null) return head;
    ListNode mid = middleFirst(head);       // FIRST middle, or 2-node lists never split
    ListNode right = mid.next;
    mid.next = null;
    return merge(sortList(head), sortList(right));
}
```

`O(n log n)` time, `O(log n)` stack. A bottom-up version (merge runs of size 1, 2, 4, … iteratively) gets `O(1)` extra space. The algorithm itself is covered in [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms|Sorting Algorithms]].

### 9.7 Copy a list with random pointers

Each node has a `next` and a `random` pointer (to any node or `null`). Make a deep copy.

```
copy(head):
    map = {}                                   -- original node → its copy
    for each node x: map[x] = new node(x.val)
    for each node x:
        map[x].next   = map[x.next]            -- map[null] = null
        map[x].random = map[x.random]
    return map[head]
```

```java
static Node copyRandomList(Node head) {
    Map<Node, Node> copy = new HashMap<>();
    for (Node x = head; x != null; x = x.next) copy.put(x, new Node(x.val));
    for (Node x = head; x != null; x = x.next) {
        copy.get(x).next = copy.get(x.next);       // HashMap.get(null) returns null here
        copy.get(x).random = copy.get(x.random);
    }
    return copy.get(head);
}
```

> [!info]- O(1) extra space: interleave the copies
> 1. Insert each copy right after its original: `A → A' → B → B' → …`.
> 2. Set `x.next.random = (x.random == null) ? null : x.random.next`. The copy of any node is the node right after it.
> 3. Separate the two lists, restoring the original `next` pointers.
> ```java
> static Node copyRandomListInterleave(Node head) {
>     if (head == null) return null;
>     for (Node p = head; p != null; p = p.next.next) {
>         Node c = new Node(p.val);
>         c.next = p.next;
>         p.next = c;
>     }
>     for (Node p = head; p != null; p = p.next.next)
>         p.next.random = (p.random == null) ? null : p.random.next;
>     Node copyHead = head.next;
>     for (Node p = head; p != null; p = p.next) {
>         Node c = p.next;
>         p.next = c.next;
>         c.next = (c.next == null) ? null : c.next.next;
>     }
>     return copyHead;
> }
> ```
> The map version relies on the node class **not** overriding `equals`/`hashCode`, so that nodes are compared by identity. If two nodes with the same value were "equal", the map would merge them.

---

## 10. Circular Lists and the Josephus Problem

In a circular list there's no `null` to stop at. Traverse with a `do`/`while` that stops on returning to the start, and handle the empty list separately:

```java
static int sizeCircular(ListNode start) {
    if (start == null) return 0;
    int count = 0;
    ListNode cur = start;
    do {
        count++;
        cur = cur.next;
    } while (cur != start);
    return count;
}
```

A plain `while (cur != start)` loop never runs, because `cur` starts equal to `start`. A `while (cur != null)` loop never ends.

> [!tip] Keep a pointer to the tail, not the head
> In a circular singly linked list, `tail.next` is the head. Holding `tail` gives `O(1)` access to both ends: insert at the front with `x.next = tail.next; tail.next = x`, and at the back with the same two lines plus `tail = x`.

### 10.1 Josephus problem

`n` people stand in a circle; counting from person 0, every `k`-th person is eliminated until one remains. Who survives?

| Method | Time |
|---|---|
| Simulate with a circular linked list | `O(n·k)` |
| Simulate with a queue (rotate `k − 1`, remove one) | `O(n·k)` |
| Recurrence | `O(n)` |

The recurrence: after the first elimination, the remaining `n − 1` people form a smaller instance whose numbering starts `k` places later. So, with 0-indexed positions,

```
J(1) = 0
J(n) = (J(n − 1) + k) mod n
```

```java
static int josephus(int n, int k) {            // 0-indexed position of the survivor
    int pos = 0;
    for (int m = 2; m <= n; m++) pos = (pos + k) % m;
    return pos;
}
```

> [!info]- The k = 2 closed form
> Write `n = 2ᵐ + L` with `0 ≤ L < 2ᵐ`. The survivor (1-indexed) is `2L + 1`. In binary, that's a left rotation of `n`'s bits: move the leading 1 to the end. For `n = 41 = 101001₂`, the survivor is `010011₂ = 19`.

---

## 11. Java's LinkedList

`java.util.LinkedList` is a doubly linked list that implements both `List` and `Deque`.

| Operation | Cost |
|---|---|
| `addFirst`, `addLast`, `removeFirst`, `removeLast`, `peekFirst`, `peekLast` | `O(1)` |
| `get(i)`, `set(i, x)`, `add(i, x)`, `remove(i)` | `O(min(i, n − i))`: walks from the nearer end |
| `contains`, `indexOf`, `remove(Object)` | `O(n)` |
| `ListIterator.add`, `ListIterator.remove`, `ListIterator.set` | `O(1)` at the cursor |
| Memory per element | node object (~24 bytes) + boxed value (~16 bytes) |

> [!warning] Indexed loops over a `LinkedList` are quadratic
> ```java
> for (int i = 0; i < list.size(); i++) sum += list.get(i);   // Θ(n²) for LinkedList
> for (int x : list) sum += x;                                 // Θ(n)
> ```
> `get(i)` walks from an end each time. Iterate with for-each or an iterator, and to insert or remove during a walk, use a `ListIterator` (the only way to get the `O(1)` middle insert that linked lists are supposed to offer).

> [!tip] Which class to use
> - As a **stack, queue, or deque**: `ArrayDeque`. Faster (contiguous, no node allocation) and lower memory. See [[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]].
> - As a **list**: `ArrayList`.
> - `LinkedList` is worth it only for frequent insertion/removal **through an iterator** in the middle of a long list, or when you need `null` elements in a queue (`ArrayDeque` rejects `null`). And with `null` elements, `poll()` returning `null` becomes ambiguous.
> - For interview problems, write your own `ListNode`: the problems are about pointer manipulation, which `LinkedList` hides.

---

## 12. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Not saving `cur.next` before overwriting it | rest of the list lost | `next = cur.next` first |
| Returning `head` after the head changed | wrong or partial list | dummy node; return `dummy.next` |
| `fast.next.next` without checking `fast.next` | `NullPointerException` | `while (fast != null && fast.next != null)` |
| Checking `slow == fast` before the first move | "cycle" in every list | move, then compare |
| Second middle used to split | infinite recursion on 2 nodes | first middle (`fast = head.next`) |
| Not cutting the halves (`mid.next = null`) | cycles / wrong merges | cut before recursing or interleaving |
| Reused last node not terminated | cycle in the output | `tail.next = null` |
| Advancing after deleting `cur.next` | consecutive targets survive | advance only when nothing was deleted |
| Comparing node values instead of identity | wrong intersection / cycle answers | `==` on nodes |
| Recursive list algorithm on `n = 10⁵` | `StackOverflowError` | iterative version |
| `insertAfter` pointer writes in the wrong order | `x.prev = x`, broken back links | update `p.next.prev` before `p.next` |
| LRU node without its key | can't remove the evicted entry from the map | store the key in the node |
| `rotateRight` without `k %= n` | TLE for huge `k` | reduce modulo length |
| Merging `k` lists one by one | `O(N·k)` | heap or pairwise |
| `for (i…) list.get(i)` on `LinkedList` | `Θ(n²)` | for-each / iterator |
| `while (cur != start)` on a circular list | loop body never runs | `do`/`while` |

---

## 13. Trick Questions and Special Cases

> [!question]- Is inserting into the middle of a linked list O(1)?
> Only if you already have a reference to the node you're inserting after. Finding position `i` takes `O(i)`. "Insert at index `i`" is `O(n)` for linked lists just like for arrays, and usually slower in practice because of pointer chasing.

> [!question]- Can you binary search a sorted linked list in O(log n)?
> No. Binary search needs `O(1)` access to the middle, and finding the middle of a linked range takes time linear in its length. The total is `n/2 + n/4 + … = O(n)` steps of walking, no better than a linear scan. Skip lists add express lanes to get `O(log n)` expected.

> [!question]- Floyd uses speeds 1 and 2. Would 1 and 3 also detect every cycle?
> Not reliably. Inside the cycle, the gap between the pointers changes by the **difference** in speeds each step. With speeds 1 and 2 it changes by 1, so it must pass through 0. With speeds 1 and 3 it changes by 2: if the cycle length is even and the gap is odd when both are inside, the gap is never 0 and the pointers jump over each other forever. The cycle-start derivation also relies on fast moving exactly twice as fast.

> [!question]- In Floyd's algorithm, can slow go around the cycle several times before they meet?
> No. When slow enters the cycle, fast is already inside and at most `c − 1` steps "behind" it (measured in the direction of travel). It closes the gap by 1 per step, so they meet within `c − 1` steps, before slow finishes one lap. That's why the whole algorithm is `O(n)`.

> [!question]- Is finding the middle with fast/slow pointers faster than counting the length and walking n/2?
> Not really. Fast/slow visits about `n` nodes with the fast pointer and `n/2` with the slow one, which is the same `~1.5n` node visits as two passes. The advantage is that it's one pass (useful for streams, or when the length isn't known), not that it's asymptotically or practically faster.

> [!question]- Detecting a cycle with a `HashSet<ListNode>`: when does it give wrong answers?
> When the node class overrides `equals`/`hashCode` by value. Then two different nodes with equal values count as "already seen", and an acyclic list like `1 → 2 → 1` is reported as cyclic. The standard `ListNode` doesn't override them, so it uses identity, which is what you want. `IdentityHashMap`-based sets make this explicit.

> [!question]- Intersection of `[4,1,8,4,5]` and `[5,6,1,8,4,5]` — is it at the node with value 1?
> No. The lists share nodes starting at `8`. The `1`s are separate nodes with equal values. Intersection means the **same node object**, so compare references, never values.

> [!question]- The list-switching intersection trick — does it terminate when the lists don't intersect?
> Yes, as long as each pointer steps **onto** `null` before switching. Both pointers walk `lenA + lenB` nodes and then both are `null` at the same moment, so `p == q` ends the loop with `null`. If a pointer jumps from the last node straight to the other head, the two never become `null` together, and the loop is infinite.

> [!question]- Delete a node given only a reference to it — possible for every node?
> Not for the tail. The trick copies the next node's value and unlinks the next node, so it needs a next node. It also isn't a true deletion of *that* object: external references to the original next node now point to a node outside the list.

> [!question]- Remove the n-th node from the end where n equals the list length?
> That's the head. Without a dummy node, `slow` would have to stop *before* the head, which doesn't exist, and the usual code throws `NullPointerException` or removes the wrong node. With the dummy, `slow` stops at the dummy and `dummy.next = head.next` works like any other case.

> [!question]- Does recursive reversal of a 10⁶-node list work in Java?
> No, it throws `StackOverflowError`: one frame per node, and Java doesn't eliminate tail calls (and this recursion isn't a tail call anyway). Use the iterative 3-pointer version, which is `O(1)` space.

> [!question]- Reverse a list of one node, or an empty list?
> Both return the input unchanged with the standard code: for `null`, the loop never runs and `prev = null` is returned; for one node, one iteration sets its `next` to `null` (already `null`) and returns it. Good reversal code needs no special cases.

> [!question]- Merge `k` sorted lists by merging them one after another — what's the complexity?
> `O(N·k)`, where `N` is the total number of nodes. The running result grows, and every merge re-walks it. With `k` lists of `n` nodes each, that's `n·(2 + 3 + … + k) ≈ n·k²/2 = N·k/2`. Pairwise merging or a heap gives `O(N log k)`.

> [!question]- Why does partitioning a list sometimes print forever?
> The last node of the "≥ x" list still has its old `next`, which may point into the "< x" list, so after joining the two lists the result has a cycle. Set `ge.next = null` before joining.

> [!question]- What happens in Java to nodes you unlink? Do you need to free them?
> Nothing explicit: once no reference reaches them, the garbage collector reclaims them, even if they form a cycle among themselves. (In C/C++ forgetting to free them is a leak.) But a node that's unlinked from the list and still referenced by something else, such as a map, stays alive. That's why the LRU cache must remove the evicted key from its map.

> [!question]- Josephus with n = 7, k = 3 (0-indexed)?
> `3`. Running the recurrence: `J(1)=0, J(2)=(0+3)%2=1, J(3)=(1+3)%3=1, J(4)=(1+3)%4=0, J(5)=(0+3)%5=3, J(6)=(3+3)%6=0, J(7)=(0+3)%7=3`. In 1-indexed terms, person 4 survives. Simulation order of elimination: 2, 5, 1, 6, 4, 0 (0-indexed).

---

## 14. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| Insert at index `i` | `O(i)` | walking dominates |
| Binary search on a list | `O(n)` | no random access |
| `while (fast != null && fast.next != null)`, both start at head | **second** middle (even `n`) | |
| Same loop with `fast = head.next` | **first** middle | use for splitting |
| Floyd: compare before moving | always "cycle" | both start at head |
| Floyd with speeds 1 and 3 | can miss a cycle | gap changes by 2 |
| After meeting, restart one at head | they meet at the cycle start | `a = (k−1)c + (c−b)` |
| Find duplicate in `n+1` values `1..n` | Floyd on `i → nums[i]` | `O(1)` space, array unchanged |
| Intersection: switch via `null` | terminates with `null` if disjoint | both walk `lenA + lenB` |
| Delete given only the node | can't delete the tail | copies the next node |
| Recursive reversal | `O(n)` stack | one frame per node |
| Merge `k` lists sequentially | `O(N·k)` | re-walks the result |
| Merge `k` lists with a heap | `O(N log k)` | |
| Partition without `ge.next = null` | cycle | stale `next` |
| `LinkedList.get(i)` in a loop | `Θ(n²)` | walks each time |
| `LinkedList` vs `ArrayDeque` for a queue | `ArrayDeque` faster | contiguous, no node objects |
| Josephus | `J(n) = (J(n−1) + k) mod n` | `O(n)` |
| Josephus `k = 2` | rotate `n`'s bits left by one | `2L + 1` |

---

## 15. Summary

- A linked list trades `O(1)` indexing for `O(1)` insertion/removal **at a known node**. Finding the node is still `O(n)`, and the poor cache behaviour makes it slower than an array in most real workloads.
- **Dummy head**: removes head special cases; return `dummy.next`. Doubly linked lists with **two sentinels** have no special cases at all.
- **Reversal**: save `next`, point back, advance. Know the iterative, recursive (`O(n)` stack), sublist, and `k`-group versions.
- **Fast/slow pointers**: middle (choose first or second middle deliberately), Floyd's cycle detection and cycle start, `n`-th from the end, and the implicit-list trick on arrays.
- **Combining**: merge with a dummy tail; `k` lists with a heap; intersection by switching heads through `null`; add numbers digit by digit with a final carry.
- Lists built from reused nodes must be **terminated** (`tail.next = null`), and nodes are compared by **identity**, not value.
- **LRU cache** = hash map + doubly linked list, with the key stored in each node.
- In real Java, prefer `ArrayDeque`/`ArrayList` over `LinkedList`, and never index into a `LinkedList` in a loop.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/02 - Linear Data Structures/02 - Strings|Strings]] · Next: [[DSA/02 - Linear Data Structures/04 - Stacks|Stacks]]
- [[DSA/01 - Foundations/02 - Recursion#6.4 Recursion over data structures|Recursion § 6.4]]: recursion on recursive structures, and its depth cost
- [[DSA/02 - Linear Data Structures/06 - Hash Tables|Hash Tables]]: chaining uses linked lists; `LinkedHashMap` as an LRU cache
- [[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]]: linked vs. array-backed queues
- [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|Heaps and Priority Queues]]: merging `k` sorted lists
- [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms|Sorting Algorithms]]: merge sort
- [[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]]: the array versions of fast/slow and gap pointers
