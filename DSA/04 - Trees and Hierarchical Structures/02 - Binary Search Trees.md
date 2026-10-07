# Binary Search Trees

A <span class="hl-blue">binary search tree</span> (BST) is a binary tree that keeps its keys ordered: for every node, all keys in its **left subtree** are smaller and all keys in its **right subtree** are larger. Searching it is binary search on a linked structure: each comparison discards a whole subtree. Unlike a sorted array, a BST also supports insertion and deletion without shifting elements.

Every operation costs `O(h)`, where `h` is the height. That's `O(log n)` when the tree is balanced and `O(n)` when it degenerates into a chain, which is exactly what inserting sorted keys produces. This note covers the BST property (and the validation mistake almost everyone makes), search, insert, and delete, successor and predecessor, order statistics, range queries, building BSTs from sorted data and traversals, the classic BST problems, and why plain BSTs give way to the balanced trees of the next chapter.

## Contents

- [[#1. The BST Property|1. The BST Property]]
- [[#2. Search, Minimum, Maximum|2. Search, Minimum, Maximum]]
- [[#3. Insertion|3. Insertion]]
- [[#4. Deletion|4. Deletion]]
- [[#5. Validating a BST|5. Validating a BST]]
- [[#6. Successor, Predecessor, Floor, Ceiling|6. Successor, Predecessor, Floor, Ceiling]]
- [[#7. Order Statistics|7. Order Statistics]]
- [[#8. Range Operations|8. Range Operations]]
- [[#9. Building BSTs|9. Building BSTs]]
- [[#10. Classic BST Problems|10. Classic BST Problems]]
- [[#11. Height and Performance|11. Height and Performance]]
- [[#12. Common Mistakes|12. Common Mistakes]]
- [[#13. Trick Questions and Special Cases|13. Trick Questions and Special Cases]]
- [[#14. Quick Reference — Non-Obvious Outcomes|14. Quick Reference — Non-Obvious Outcomes]]
- [[#15. Summary|15. Summary]]

---

## 1. The BST Property

> [!note] Definition
> A binary tree is a BST if, for **every** node `n`:
> - every key in `n`'s left subtree is `< n.key`, and
> - every key in `n`'s right subtree is `> n.key`.
>
> Equivalently: the **inorder traversal is strictly increasing**.

The condition is about **whole subtrees**, not just the two children. A tree where every node is greater than its left child and smaller than its right child can still violate it, if a key deep in a left subtree is larger than an ancestor higher up ([[#5. Validating a BST|§5]]).

The equivalence with inorder is the most useful fact about BSTs: anything you'd do with a sorted array (scan in order, find the `k`-th element, look for neighbours, two pointers) has a BST version based on inorder traversal ([[DSA/04 - Trees and Hierarchical Structures/01 - Binary Trees#3. Depth-First Traversals|Binary Trees § 3]]).

All examples below use this tree:

```
          8
        /   \
       3     10
      / \      \
     1   6      14
        / \     /
       4   7   13
```

Inorder: `1 3 4 6 7 8 10 13 14`.

### 1.1 Duplicate keys

The definition above has none. When a BST must hold repeated keys, pick one policy and use it everywhere:

| Policy | How | Notes |
|---|---|---|
| Reject | insert does nothing if the key exists | set semantics; Java's `TreeSet` |
| Count field | each node stores `key` and `count` | cleanest: one node per distinct key; `TreeMap<K, Integer>` in Java |
| Duplicates go left (`≤`) | `key <= n.key` goes left | search must keep going after a match to find all copies; validation becomes `left ≤ node < right` |
| Map to distinct pairs | store `(key, uniqueId)` | how `TreeSet` is made to hold duplicates ([[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]]) |

LeetCode's "validate BST" uses the strict definition: `[2, 2, 2]` is **not** a valid BST.

---

## 2. Search, Minimum, Maximum

```
search(n, key):
    while n ≠ null and n.key ≠ key:
        n = (key < n.key) ? n.left : n.right
    return n                            -- null if absent
```

```java
static TreeNode search(TreeNode n, int key) {
    while (n != null && n.val != key)
        n = key < n.val ? n.left : n.right;
    return n;
}

static TreeNode min(TreeNode n) {                  // n must not be null
    while (n.left != null) n = n.left;
    return n;
}

static TreeNode max(TreeNode n) {
    while (n.right != null) n = n.right;
    return n;
}
```

Each step moves one level down, so search is `O(h)`. The iterative form is preferred: the recursive one is tail-recursive, but Java doesn't eliminate tail calls ([[DSA/01 - Foundations/02 - Recursion#7. Tail Recursion|Recursion § 7]]), so it uses `O(h)` stack for nothing.

The minimum is the **leftmost** node, which isn't necessarily a leaf: it can have a right child. In the example, `min = 1`, `max = 14`, and `max` has a left child (`13`).

---

## 3. Insertion

A new key always becomes a new **leaf**: search for it, and attach it where the search fell off the tree.

```
insert(n, key):                         -- returns the root of the updated subtree
    if n = null: return new node(key)
    if key < n.key: n.left = insert(n.left, key)
    elif key > n.key: n.right = insert(n.right, key)
    -- equal: already present
    return n
```

```java
static TreeNode insert(TreeNode n, int key) {
    if (n == null) return new TreeNode(key);
    if (key < n.val) n.left = insert(n.left, key);
    else if (key > n.val) n.right = insert(n.right, key);
    return n;                                      // equal key: unchanged (set semantics)
}
```

The "return the subtree's new root and reassign it" pattern (`n.left = insert(n.left, key)`) handles the empty-subtree case without special code, and it's the pattern every self-balancing tree builds on: a rotation changes a subtree's root, and the parent's link is updated by the same assignment.

> [!warning] Always use the returned root
> `insert(root, 5);` on an **empty** tree creates a node and throws it away: `root` is still `null`. Write `root = insert(root, 5);`. Java passes the reference by value, so a method can't reassign the caller's variable ([[DSA/02 - Linear Data Structures/03 - Linked Lists|Linked Lists]] has the same issue with `head`).

The iterative version avoids recursion depth on degenerate trees:

```java
static TreeNode insertIterative(TreeNode root, int key) {
    TreeNode node = new TreeNode(key);
    if (root == null) return node;
    TreeNode cur = root;
    while (true) {
        if (key < cur.val) {
            if (cur.left == null) { cur.left = node; break; }
            cur = cur.left;
        } else if (key > cur.val) {
            if (cur.right == null) { cur.right = node; break; }
            cur = cur.right;
        } else break;                              // duplicate
    }
    return root;
}
```

The shape of a BST depends on the **insertion order**, not just the set of keys: inserting `1, 2, 3, 4, 5` produces a chain, while `3, 1, 4, 2, 5` produces a tree of height 2 ([[#11. Height and Performance|§11]]).

---

## 4. Deletion

Find the node, then:

| Case | Action |
|---|---|
| 1. No children (leaf) | remove it: the parent's link becomes `null` |
| 2. One child | replace the node by that child: the whole child subtree moves up one level |
| 3. Two children | replace the node's key by its **inorder successor** (the minimum of its right subtree), then delete the successor from the right subtree; the successor has no left child, so that's case 1 or 2 |

![[BST - Delete Three Cases.excalidraw|800]]

```
delete(n, key):                         -- returns the root of the updated subtree
    if n = null: return null            -- key not found
    if key < n.key: n.left = delete(n.left, key)
    elif key > n.key: n.right = delete(n.right, key)
    else:
        if n.left = null: return n.right            -- cases 1 and 2
        if n.right = null: return n.left
        s = min(n.right)                            -- case 3
        n.key = s.key
        n.right = delete(n.right, s.key)
    return n
```

```java
static TreeNode delete(TreeNode n, int key) {
    if (n == null) return null;
    if (key < n.val) n.left = delete(n.left, key);
    else if (key > n.val) n.right = delete(n.right, key);
    else {
        if (n.left == null) return n.right;        // also covers the leaf case: returns null
        if (n.right == null) return n.left;
        TreeNode s = min(n.right);
        n.val = s.val;                             // copy the successor's key up
        n.right = delete(n.right, s.val);          // and remove the successor below
    }
    return n;
}
```

Why the successor: it's the smallest key larger than `n`, so after it moves into `n`'s place, everything in the left subtree is still smaller and everything left in the right subtree is still larger. The **predecessor** (maximum of the left subtree) works equally well.

> [!info]- Deleting without copying keys (relinking nodes)
> Copying `s.val` into `n` is fine for an `int` tree, but it changes which **node object** holds which key. If something else keeps references to nodes (an iterator, a `Map<Key, Node>`, a node with satellite data that's expensive to copy), relink the successor node into `n`'s position instead:
> ```java
> static TreeNode deleteRelink(TreeNode n, int key) {
>     if (n == null) return null;
>     if (key < n.val) n.left = deleteRelink(n.left, key);
>     else if (key > n.val) n.right = deleteRelink(n.right, key);
>     else {
>         if (n.left == null) return n.right;
>         if (n.right == null) return n.left;
>         TreeNode t = n;
>         n = min(t.right);                          // the successor node itself takes t's place
>         n.right = deleteMin(t.right);              // detach it from t's right subtree first
>         n.left = t.left;
>     }
>     return n;
> }
>
> static TreeNode deleteMin(TreeNode n) {            // removes the leftmost node, returns the new root
>     if (n.left == null) return n.right;
>     n.left = deleteMin(n.left);
>     return n;
> }
> ```
> The order matters: `n.right = deleteMin(t.right)` must run **before** `n.left = t.left`, and both after `n` is reassigned. This is Hibbard deletion as written in Sedgewick's *Algorithms*.

> [!warning] Deleting a key and re-inserting it doesn't restore the tree
> Deleting a node with two children moves its successor up; re-inserting the key puts it at a **leaf**. The set of keys is the same, but the shape (and so the height and every traversal except inorder) can differ.

---

## 5. Validating a BST

![[BST - Local Check Is Not Enough.excalidraw|800]]

> [!warning] Checking each node against its children is not enough
> `left.val < n.val < right.val` at every node accepts `[10, 5, 15, null, null, 6, 20]`: `6 < 15` is fine locally, but `6` is in the **right** subtree of `10`, so it must be greater than 10. Every key must lie within bounds set by **all** of its ancestors.

**Bounds method.** Pass down the open interval the subtree's keys must lie in. Going left tightens the upper bound to the current key; going right tightens the lower bound.

```
valid(n, lo, hi):                       -- every key in n's subtree must be in (lo, hi)
    if n = null: return true
    if n.key ≤ lo or n.key ≥ hi: return false
    return valid(n.left, lo, n.key) and valid(n.right, n.key, hi)
```

```java
static boolean isValidBST(TreeNode root) { return valid(root, null, null); }

static boolean valid(TreeNode n, Integer lo, Integer hi) {   // null = unbounded
    if (n == null) return true;
    if ((lo != null && n.val <= lo) || (hi != null && n.val >= hi)) return false;
    return valid(n.left, lo, n.val) && valid(n.right, n.val, hi);
}
```

> [!warning] `Integer.MIN_VALUE` and `MAX_VALUE` as "infinity"
> Starting with `valid(root, Integer.MIN_VALUE, Integer.MAX_VALUE)` rejects the single-node tree `[2147483647]`, because `n.val >= hi` is true. The sentinels collide with real keys. Use `null` for "no bound" (as above), or `long` bounds `Long.MIN_VALUE`/`Long.MAX_VALUE`, which no `int` can equal.

**Inorder method.** A tree is a BST exactly when its inorder sequence is strictly increasing, so compare each visited key with the previous one:

```java
static boolean isValidBSTInorder(TreeNode root) {
    Deque<TreeNode> st = new ArrayDeque<>();
    TreeNode cur = root, prev = null;              // prev: a node, not an int, so "none yet" is null
    while (cur != null || !st.isEmpty()) {
        while (cur != null) { st.push(cur); cur = cur.left; }
        cur = st.pop();
        if (prev != null && cur.val <= prev.val) return false;   // must strictly increase
        prev = cur;
        cur = cur.right;
    }
    return true;
}
```

Both are `O(n)`. The inorder version stops at the first violation and needs no bounds; the bounds version generalises to other constraints.

> [!info]- With duplicates allowed on one side, inorder isn't enough
> If the policy is "duplicates go left" (`left ≤ node < right`), the inorder sequence of a valid tree is non-decreasing. But the tree `2 → right 2` also has the non-decreasing inorder `2, 2`, and it violates the policy (the duplicate is on the right). With duplicates, the inorder sequence no longer determines which side they're on, so use the bounds method with `≤` on one side and `<` on the other.

---

## 6. Successor, Predecessor, Floor, Ceiling

The **successor** of a key is the next larger key in the tree (the next element of the inorder sequence).

![[BST - Inorder Successor.excalidraw|800]]

With **parent pointers**, from a node `x`:

```
successor(x):
    if x.right ≠ null: return min(x.right)           -- case 1: leftmost node of the right subtree
    while x.parent ≠ null and x = x.parent.right:    -- case 2: climb while coming up from the right
        x = x.parent
    return x.parent                                  -- first ancestor reached from its LEFT side (or null)
```

In the example, the successor of `6` is `7` (case 1) and the successor of `7` is `8` (case 2: climb from `7` to `6` to `3`, all from the right, then `3` is the left child of `8`). The maximum, `14`, has no successor.

**Without parent pointers**, search from the root and remember the last node where the search went **left**: that node is larger than the key, and it's the smallest such node seen.

```java
static TreeNode successor(TreeNode root, int key) {    // smallest key > key, or null
    TreeNode best = null;
    for (TreeNode n = root; n != null; ) {
        if (key < n.val) { best = n; n = n.left; }     // n is a candidate; look for a smaller one
        else n = n.right;                              // n is too small (or equal)
    }
    return best;
}

static TreeNode predecessor(TreeNode root, int key) {  // largest key < key, or null
    TreeNode best = null;
    for (TreeNode n = root; n != null; ) {
        if (key > n.val) { best = n; n = n.right; }
        else n = n.left;
    }
    return best;
}
```

`O(h)`, and `key` doesn't have to be in the tree. The same walk with `≤`/`≥` gives **floor** (largest key `≤ x`) and **ceiling** (smallest key `≥ x`), the tree versions of the lower/upper bound of [[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]]:

```java
static TreeNode floor(TreeNode n, int key) {       // largest key ≤ key, or null
    TreeNode best = null;
    while (n != null) {
        if (n.val == key) return n;
        if (n.val < key) { best = n; n = n.right; }
        else n = n.left;
    }
    return best;
}

static TreeNode ceiling(TreeNode n, int key) {     // smallest key ≥ key, or null
    TreeNode best = null;
    while (n != null) {
        if (n.val == key) return n;
        if (n.val > key) { best = n; n = n.left; }
        else n = n.right;
    }
    return best;
}
```

| Java `TreeSet` / `TreeMap` | Meaning | Example tree, argument `5` |
|---|---|---|
| `lower(x)` / `lowerKey` | largest `< x` | `4` |
| `floor(x)` / `floorKey` | largest `≤ x` | `4` |
| `ceiling(x)` / `ceilingKey` | smallest `≥ x` | `6` |
| `higher(x)` / `higherKey` | smallest `> x` | `6` |

With argument `6`, the four give `4, 6, 6, 7`. All return `null` when nothing qualifies ([[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]] covers the full API).

### 6.1 Closest value

The closest key to a target is the floor or the ceiling; one walk can track both:

```java
static int closestValue(TreeNode n, double target) {    // n not null; ties → the smaller key
    int best = n.val;
    while (n != null) {
        double d = Math.abs(n.val - target), bd = Math.abs(best - target);
        if (d < bd || (d == bd && n.val < best)) best = n.val;
        n = target < n.val ? n.left : n.right;
    }
    return best;
}
```

`[4, 2, 5, 1, 3]`, target `3.714` → `4`; target `3.5` → `3` (a tie, resolved to the smaller key). The `k` closest values come from an inorder traversal with a sliding window of size `k`, or from two stacks walking outward from the target ([[#10.3 Two sum in a BST|§10.3]] uses the same stacks).

---

## 7. Order Statistics

### 7.1 k-th smallest by inorder

The `k`-th smallest key is the `k`-th node of the inorder traversal. The iterative traversal can stop as soon as it gets there:

```java
static int kthSmallest(TreeNode root, int k) {     // 1-based k, 1 ≤ k ≤ n
    Deque<TreeNode> st = new ArrayDeque<>();
    TreeNode cur = root;
    while (true) {
        while (cur != null) { st.push(cur); cur = cur.left; }
        cur = st.pop();
        if (--k == 0) return cur.val;
        cur = cur.right;
    }
}
```

`O(h + k)`. In the example, `kthSmallest(root, 3) = 4`. The `k`-th **largest** is a reverse inorder (right, node, left).

### 7.2 Augmenting nodes with subtree sizes

When `k`-th queries interleave with insertions and deletions, store each subtree's **size** in its root. Then the rank of a node is known at each step, and select runs in `O(h)` without visiting `k` nodes:

```
select(n, k):                           -- k-th smallest, 1-based
    while n ≠ null:
        ls = size(n.left)
        if k ≤ ls: n = n.left
        elif k = ls + 1: return n.key
        else: k = k − ls − 1; n = n.right

rank(n, key):                           -- number of keys < key
    r = 0
    while n ≠ null:
        if key ≤ n.key: n = n.left
        else: r = r + 1 + size(n.left); n = n.right
    return r
```

```java
static class SNode {
    int key, size = 1;                             // size of the subtree rooted here
    SNode left, right;
    SNode(int key) { this.key = key; }
}

static int size(SNode n) { return n == null ? 0 : n.size; }

static SNode insertSized(SNode n, int key) {
    if (n == null) return new SNode(key);
    if (key < n.key) n.left = insertSized(n.left, key);
    else if (key > n.key) n.right = insertSized(n.right, key);
    else return n;                                 // duplicate: no size changes
    n.size = 1 + size(n.left) + size(n.right);     // recompute on the way back up
    return n;
}

static int select(SNode n, int k) {
    while (n != null) {
        int ls = size(n.left);
        if (k <= ls) n = n.left;
        else if (k == ls + 1) return n.key;
        else { k -= ls + 1; n = n.right; }
    }
    throw new IllegalArgumentException("k out of range");
}

static int rank(SNode n, int key) {
    int r = 0;
    while (n != null) {
        if (key <= n.key) n = n.left;
        else { r += 1 + size(n.left); n = n.right; }
    }
    return r;
}
```

Every operation that changes structure (insert, delete, and the rotations of a balanced tree) must recompute the sizes along its path. The count of keys in `[lo, hi]` is `rank(hi + 1) − rank(lo)`. Java's `TreeMap` has no rank or select; when they're needed with updates, use this augmented tree on top of a balanced one (a treap with sizes, [[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]]), or a Fenwick tree over compressed keys ([[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees]]).

---

## 8. Range Operations

### 8.1 Range sum

Sum the keys in `[lo, hi]`, skipping subtrees that lie entirely outside:

```java
static int rangeSumBST(TreeNode n, int lo, int hi) {
    if (n == null) return 0;
    if (n.val < lo) return rangeSumBST(n.right, lo, hi);   // n and its whole left subtree are too small
    if (n.val > hi) return rangeSumBST(n.left, lo, hi);    // n and its whole right subtree are too big
    return n.val + rangeSumBST(n.left, lo, hi) + rangeSumBST(n.right, lo, hi);
}
```

`O(h + m)` for `m` keys in the range, roughly: the walk follows two boundary paths and visits every node in between. In the example, `[4, 10]` → `4 + 6 + 7 + 8 + 10 = 35`. If most keys are in range, it's still `O(n)`; for many range queries with updates, the augmented tree of [[#7.2 Augmenting nodes with subtree sizes|§7.2]] (with subtree sums) or a Fenwick tree answers each in `O(log n)`.

### 8.2 Trim to a range

Remove every key outside `[lo, hi]`, keeping the rest as a valid BST:

```java
static TreeNode trimBST(TreeNode n, int lo, int hi) {
    if (n == null) return null;
    if (n.val < lo) return trimBST(n.right, lo, hi);   // drop n and its left subtree
    if (n.val > hi) return trimBST(n.left, lo, hi);    // drop n and its right subtree
    n.left = trimBST(n.left, lo, hi);
    n.right = trimBST(n.right, lo, hi);
    return n;
}
```

When `n` is too small, its **right** subtree may still contain keys in range, so the answer is the trimmed right subtree, which takes `n`'s place. The root of the result can be a different node from the original root.

---

## 9. Building BSTs

### 9.1 From a sorted array: a balanced BST

Use the middle element as the root, and build the halves recursively:

```
build(a, lo, hi):
    if lo > hi: return null
    mid = (lo + hi) / 2
    node = new node(a[mid])
    node.left = build(a, lo, mid − 1)
    node.right = build(a, mid + 1, hi)
    return node
```

```java
static TreeNode sortedArrayToBST(int[] a) { return buildBalanced(a, 0, a.length - 1); }

static TreeNode buildBalanced(int[] a, int lo, int hi) {
    if (lo > hi) return null;
    int mid = (lo + hi) >>> 1;
    TreeNode n = new TreeNode(a[mid]);
    n.left = buildBalanced(a, lo, mid - 1);
    n.right = buildBalanced(a, mid + 1, hi);
    return n;
}
```

`O(n)`, height `⌊log₂ n⌋`. For an even-length range either middle works, so several balanced answers are correct. The same idea **rebalances** any BST in `O(n)`: inorder it into a list, then rebuild.

> [!example]- From a sorted linked list in O(n)
> Finding the middle of a linked list costs `O(n)` per level (`O(n log n)` total). Instead, build in **inorder**: construct the left subtree from the first `n/2` list nodes, take the next list node as the root, then build the right subtree. The list is consumed front to back, exactly as an inorder traversal visits the finished tree.
> ```java
> class ListNode {
>     int val;
>     ListNode next;
>     ListNode(int val) { this.val = val; }
> }
>
> static TreeNode sortedListToBST(ListNode head) {
>     int n = 0;
>     for (ListNode p = head; p != null; p = p.next) n++;
>     return fromList(new ListNode[]{head}, n);
> }
>
> static TreeNode fromList(ListNode[] cur, int n) {  // builds a BST from the next n list nodes
>     if (n == 0) return null;
>     TreeNode left = fromList(cur, n / 2);
>     TreeNode root = new TreeNode(cur[0].val);       // the list pointer is now at the middle
>     cur[0] = cur[0].next;
>     root.left = left;
>     root.right = fromList(cur, n - n / 2 - 1);
>     return root;
> }
> ```
> `[-10, -3, 0, 5, 9]` → root `0` with `[-10, -3]` on the left and `[5, 9]` on the right.

### 9.2 From a preorder sequence

A BST's inorder is its sorted keys, so its **preorder alone** determines it ([[DSA/04 - Trees and Hierarchical Structures/01 - Binary Trees#9. Building a Tree from Traversals|Binary Trees § 9]]). Sorting to get the inorder costs `O(n log n)`; an upper bound passed down does it in `O(n)`:

```java
static TreeNode bstFromPreorder(int[] pre) {
    return fromPreorder(pre, new int[]{0}, Long.MAX_VALUE);
}

static TreeNode fromPreorder(int[] pre, int[] i, long bound) {   // take keys < bound
    if (i[0] == pre.length || pre[i[0]] > bound) return null;
    TreeNode n = new TreeNode(pre[i[0]++]);
    n.left = fromPreorder(pre, i, n.val);          // the left subtree takes keys < n.val
    n.right = fromPreorder(pre, i, bound);         // the right subtree takes the rest, up to bound
    return n;
}
```

`[8, 5, 1, 7, 10, 12]` → `[8, 5, 10, 1, 7, null, 12]`. Each key is read once. Only an **upper** bound is checked, so the input must be a valid BST preorder: given `[4, 24, 0]`, it puts `0` in `4`'s right subtree and returns a tree that isn't a BST, without any error. Validate first when the input isn't guaranteed:

**Is a sequence a valid BST preorder?** Scan with a decreasing stack, tracking the lower bound: once a key larger than the stack top appears, the walk has moved into a right subtree, and every later key must exceed the popped values.

```java
static boolean verifyPreorder(int[] pre) {
    Deque<Integer> st = new ArrayDeque<>();
    long low = Long.MIN_VALUE;                     // every later key must exceed this
    for (int x : pre) {
        if (x < low) return false;
        while (!st.isEmpty() && st.peek() < x) low = st.pop();   // entering a right subtree
        st.push(x);
    }
    return true;
}
```

`[5, 2, 1, 3, 6]` → `true`; `[5, 2, 6, 1, 3]` → `false` (after `6`, the walk is in `5`'s right subtree, so `1` can't appear). This is the monotonic-stack pattern of [[DSA/02 - Linear Data Structures/04 - Stacks#8. Monotonic Stack|Stacks § 8]].

### 9.3 Counting BSTs: Catalan numbers

The number of structurally different BSTs on the keys `1..n` is the Catalan number `C(n)`: choose a root `r`, then the left subtree is any BST on `1..r−1` and the right subtree any BST on `r+1..n`.

```java
static long numTrees(int n) {
    long[] c = new long[n + 1];
    c[0] = 1;                                      // one empty tree
    for (int m = 1; m <= n; m++)
        for (int root = 1; root <= m; root++)
            c[m] += c[root - 1] * c[m - root];
    return c[n];
}
```

`1, 1, 2, 5, 14, 42, 132, …`; `numTrees(19) = 1 767 263 190`, the largest that fits in an `int`. The closed form is `C(n) = (2n choose n) / (n + 1)` ([[DSA/01 - Foundations/04 - Math for Algorithms|Math for Algorithms]]). Generating all of them (rather than counting) uses the same split recursively and returns `C(n)` trees, which grows like `4ⁿ`.

---

## 10. Classic BST Problems

### 10.1 Lowest common ancestor

In a BST, the LCA of `p` and `q` is the first node, walking down from the root, whose key lies between them (inclusive): above it both keys are on the same side, and at it they split.

```java
static TreeNode lcaBST(TreeNode n, TreeNode p, TreeNode q) {
    while (n != null) {
        if (p.val < n.val && q.val < n.val) n = n.left;
        else if (p.val > n.val && q.val > n.val) n = n.right;
        else return n;                             // split point, or n is p or q
    }
    return null;
}
```

`O(h)` time and `O(1)` space, versus `O(n)` for the general binary-tree LCA ([[DSA/04 - Trees and Hierarchical Structures/01 - Binary Trees#8.5 Lowest common ancestor|Binary Trees § 8.5]]). In the example, `LCA(4, 7) = 6`, `LCA(4, 14) = 8`, `LCA(3, 4) = 3`.

### 10.2 BST iterator

Iterate a BST in sorted order with `next()` and `hasNext()`, using `O(h)` memory instead of `O(n)` for a full inorder list. It's the iterative inorder traversal of [[DSA/04 - Trees and Hierarchical Structures/01 - Binary Trees#4.2 Inorder|Binary Trees § 4.2]], paused between visits:

```java
static class BSTIterator {
    private final Deque<TreeNode> st = new ArrayDeque<>();

    BSTIterator(TreeNode root) { pushLeft(root); }

    private void pushLeft(TreeNode n) {
        for (; n != null; n = n.left) st.push(n);
    }

    boolean hasNext() { return !st.isEmpty(); }

    int next() {
        TreeNode n = st.pop();                     // the smallest key not yet returned
        pushLeft(n.right);
        return n.val;
    }
}
```

A single `next()` can cost `O(h)` (pushing a long left spine), but each node is pushed and popped once over the whole iteration, so it's `O(1)` **amortized** ([[DSA/01 - Foundations/01 - Complexity Analysis|Complexity Analysis]]). Modifying the tree during iteration invalidates the stack. Java's `TreeMap` iterators throw `ConcurrentModificationException` in that case; this one silently misbehaves.

### 10.3 Two sum in a BST

Find two keys summing to `k`. A hash set of seen keys works on any tree (`O(n)` space). The BST-specific version runs the two-pointer technique of [[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]] with two iterators, one ascending and one descending, in `O(h)` space:

```java
static boolean findTarget(TreeNode root, int k) {
    Deque<TreeNode> lo = new ArrayDeque<>(), hi = new ArrayDeque<>();
    for (TreeNode n = root; n != null; n = n.left) lo.push(n);    // lo.peek(): smallest unused key
    for (TreeNode n = root; n != null; n = n.right) hi.push(n);   // hi.peek(): largest unused key
    while (!lo.isEmpty() && !hi.isEmpty() && lo.peek() != hi.peek()) {   // stop when they meet
        long sum = (long) lo.peek().val + hi.peek().val;
        if (sum == k) return true;
        if (sum < k) {
            TreeNode n = lo.pop();
            for (n = n.right; n != null; n = n.left) lo.push(n);
        } else {
            TreeNode n = hi.pop();
            for (n = n.left; n != null; n = n.right) hi.push(n);
        }
    }
    return false;
}
```

The `lo.peek() != hi.peek()` test stops the pointers when they reach the same node, so a key isn't paired with itself: in `[5, 3, 6]` with `k = 10`, `5 + 5` must not count.

### 10.4 Recover a BST with two swapped keys

Two keys of a BST were swapped by mistake; fix the tree without changing its shape. Swapping two elements of a sorted sequence creates **one or two** inversions (adjacent pairs out of order). The first misplaced key is the **larger** element of the first inversion; the second is the **smaller** element of the last inversion.

```java
static void recoverTree(TreeNode root) {
    TreeNode first = null, second = null, prev = null, cur = root;
    Deque<TreeNode> st = new ArrayDeque<>();
    while (cur != null || !st.isEmpty()) {
        while (cur != null) { st.push(cur); cur = cur.left; }
        cur = st.pop();
        if (prev != null && prev.val > cur.val) {  // an inversion
            if (first == null) first = prev;       // first inversion: its larger element
            second = cur;                          // latest inversion: its smaller element
        }
        prev = cur;
        cur = cur.right;
    }
    int t = first.val; first.val = second.val; second.val = t;
}
```

Inorder `1 6 3 4 5 2 7` (2 and 6 swapped) has inversions `6 > 3` and `5 > 2`: `first = 6`, `second = 2`. Inorder `1 3 2 4` (adjacent keys swapped) has only one inversion, `3 > 2`, and both nodes come from it, which is why `second` is set at **every** inversion, not only the second one. Morris traversal makes this `O(1)` space.

### 10.5 Convert a BST to a sorted doubly linked list, in place

Reuse `left` as "previous" and `right` as "next". An inorder traversal visits the nodes in sorted order; link each one to the node visited before it.

```java
static TreeNode treeToDoublyList(TreeNode root) {  // circular; returns the smallest node
    if (root == null) return null;
    TreeNode[] ends = new TreeNode[2];             // [head, tail] of the list built so far
    linkInorder(root, ends);
    ends[0].left = ends[1];                        // close the circle
    ends[1].right = ends[0];
    return ends[0];
}

static void linkInorder(TreeNode n, TreeNode[] ends) {
    if (n == null) return;
    linkInorder(n.left, ends);
    if (ends[1] == null) ends[0] = n;              // first node visited: the head
    else { ends[1].right = n; n.left = ends[1]; }
    ends[1] = n;
    linkInorder(n.right, ends);
}
```

Overwriting `n.left` is safe because the left subtree is already finished when `n` is visited; `n.right` is overwritten only later, when the next node is linked, after `n.right` has already been passed to the recursive call.

### 10.6 Other problems that reduce to inorder

| Problem | Idea |
|---|---|
| Minimum absolute difference between any two keys | only **adjacent** keys in inorder can be closest |
| Mode(s) of a BST with duplicates | equal keys are consecutive in inorder: count runs |
| Convert to a "greater sum tree" (each key += sum of larger keys) | **reverse** inorder with a running sum |
| Merge two BSTs into a sorted list | inorder both, then merge ([[DSA/03 - Sorting and Searching/01 - Sorting Algorithms#3. Merge Sort|merge step]]) |
| Largest BST subtree inside a binary tree | bottom-up: return (isBST, min, max, size) for each subtree |

---

## 11. Height and Performance

| Insertion order of `n` keys | Height | Cost per operation |
|---|---|---|
| Sorted or reverse-sorted | `n − 1` (a chain) | `O(n)` |
| Random (each order equally likely) | `≈ 2.99 log₂ n` expected; average depth `≈ 1.39 log₂ n` | `O(log n)` expected |
| Median first, recursively (§9.1) | `⌊log₂ n⌋` | `O(log n)` |
| Self-balancing tree, any order | `O(log n)` guaranteed | `O(log n)` |

![[BST - Insertion Order Shapes.excalidraw|800]]

Building a BST by inserting `n` sorted keys costs `1 + 2 + … + (n − 1) = Θ(n²)` comparisons, the same as quicksort with the first element as pivot on sorted input. That's not a coincidence: inserting into a BST compares exactly the same pairs of keys as quicksort does when it uses each subarray's first element as the pivot ([[DSA/03 - Sorting and Searching/01 - Sorting Algorithms#4.3 Pivot choice and the worst case|Sorting § 4.3]]).

Real inputs are often sorted or nearly sorted (timestamps, IDs, keys read from a sorted file), so a plain BST is a bad default. In Java, use `TreeMap`/`TreeSet` (red-black trees, `O(log n)` guaranteed); the plain BST is the foundation for understanding them, and for the many interview problems that hand you one ([[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]]).

> [!info]- Deletions make random BSTs worse over time
> The `O(log n)` expected height holds for trees built by random insertions only. Hibbard deletion always replaces a two-child node by its **successor**, which removes nodes from right subtrees more often than from left ones. After many random insert/delete pairs, experiments and analyses show the average depth drifting up toward `Θ(√n)`. Alternating between successor and predecessor (or choosing randomly) reduces the effect; balanced trees eliminate it.

---

## 12. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Validating only against children | invalid trees accepted | pass bounds down, or check inorder |
| `Integer.MIN_VALUE`/`MAX_VALUE` as bounds | `[2147483647]` rejected | `null` or `long` bounds |
| `<=` vs `<` in validation | duplicates accepted or rejected wrongly | match the duplicate policy |
| `insert(root, x);` without assigning | first insertion into an empty tree lost | `root = insert(root, x);` |
| Deleting a two-child node by removing it | subtree lost or BST order broken | replace with successor (or predecessor) |
| Successor deleted from the whole tree instead of the right subtree | the wrong node removed when keys repeat; extra work | `n.right = delete(n.right, s.val)` |
| `min()` assumed to return a leaf | missed right child of the minimum | the leftmost node may have a right child |
| Successor that only looks at the right subtree | `null` for nodes without a right child | climb to the first ancestor reached from the left |
| `kthSmallest` with a full inorder list | `O(n)` time and memory | stop the iterative traversal at `k` |
| Subtree sizes not updated after delete/rotation | wrong `select`/`rank` | recompute on every structural change |
| Two-sum pointers allowed to meet | a key paired with itself | stop when both stacks point at the same node |
| Recover-tree setting `second` only on the second inversion | adjacent swaps not fixed | update `second` at every inversion |
| Plain BST fed sorted data | `O(n)` operations, stack overflow in recursion | balanced tree / `TreeMap` |
| Mutating a key inside the tree | node becomes unreachable by search | delete, change, re-insert |

---

## 13. Trick Questions and Special Cases

> [!question]- Is `[10, 5, 15, null, null, 6, 20]` a valid BST?
> No. Every parent–child pair is ordered correctly (`5 < 10 < 15`, `6 < 15 < 20`), but `6` is in the right subtree of `10` and is smaller than 10. Checking only children says "valid".

> [!question]- Is the single-node tree `[2147483647]` a valid BST?
> Yes, every one-node tree is. Code using `Integer.MAX_VALUE` as the initial upper bound rejects it (`val >= hi`), and code using `Integer.MIN_VALUE` as a lower bound rejects `[-2147483648]`.

> [!question]- Is `[2, 2, 2]` a valid BST? `[1, 1]`?
> Not under the standard (strict) definition, which is LeetCode's: keys must be strictly smaller on the left and strictly larger on the right. Whether duplicates are allowed is a policy decision; the validation must match it.

> [!question]- If a binary tree's inorder traversal is strictly increasing, is it a BST?
> Yes: for distinct keys, "inorder is strictly increasing" and "is a BST" are equivalent. That's why the inorder method of validation is correct.

> [!question]- Do two different BSTs on the same keys have the same inorder traversal? The same preorder?
> Same inorder: always (it's the sorted keys), so inorder alone says nothing about the shape. Same preorder: never, for distinct keys, because a BST's preorder determines it uniquely ([[#9.2 From a preorder sequence|§9.2]]).

> [!question]- Is `[5, 2, 6, 1, 3]` the preorder of some BST?
> No. After `6` (larger than the root `5`), the traversal is in the root's right subtree, so every later key must be greater than 5. `1` breaks that.

> [!question]- What's the successor of the maximum key? The predecessor of the minimum?
> Neither exists: `null`. Successor code that climbs parents must stop at the root; `TreeMap.higherKey(lastKey())` returns `null`.

> [!question]- What's the successor of `7` in the example tree, and why isn't it in `7`'s subtree?
> `8`. `7` has no right child, so its successor is the first ancestor whose **left** subtree contains it: climb `7 → 6 → 3` (each from the right) and then `3` is the left child of `8`.

> [!question]- Which node does deleting `3` from the example move, and where?
> `3` has two children, so its successor `4` (minimum of `3`'s right subtree) replaces it: the key at `3`'s position becomes `4`, and the leaf `4` is removed. Inorder: `1 4 6 7 8 10 13 14`.

> [!question]- Delete `8` (the root) from the example, then insert `8` again. Same tree?
> No. Deletion moves the successor `10` into the root, giving root `10` with left subtree `3…` and right subtree `14 → 13`. Re-inserting `8` puts it as the right child of `7`, a leaf. Same keys, different shape.

> [!question]- How many comparisons to build a BST by inserting `1, 2, …, n` in that order?
> `0 + 1 + … + (n − 1) = n(n − 1)/2`: each new key walks the whole chain. The resulting height is `n − 1`.

> [!question]- In what order should `1..7` be inserted to get a perfect tree?
> Any order where each subtree's median comes before the rest of that subtree, for example `4, 2, 6, 1, 3, 5, 7` (level order of the result) or `4, 2, 1, 3, 6, 5, 7` (its preorder).

> [!question]- How many structurally different BSTs hold the keys `{1, 2, 3}`? `{1, 2, 3, 4}`?
> `5` and `14` (Catalan numbers). Each choice of root splits the remaining keys into fixed left and right sets.

> [!question]- `LCA(p, q)` in a BST when `p` is an ancestor of `q`?
> `p` itself. The walk stops at `p`, since `p`'s key is between `p` and `q` (inclusive). The general binary-tree LCA gives the same answer.

> [!question]- Recover a BST whose inorder is `3 2 1`. Which keys were swapped?
> `3` and `1`. Inversions are `3 > 2` and `2 > 1`: `first` = the larger of the first (`3`), `second` = the smaller of the last (`1`). Swapping them gives `1 2 3`.

> [!question]- Range sum `[4, 10]` on the example: which nodes are never visited?
> Only `1`. At `3` (too small), the code skips `3`'s whole left subtree, which is `1`. But `14` and `13` are both visited although they're out of range: when a node is too **big**, only its right subtree is skipped, because its left subtree may still hold keys in range. Pruning removes the far side of each out-of-range node, not the node's whole neighbourhood. The result is `35`.

---

## 14. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| Inorder of any BST | sorted keys | definition |
| Shape from inorder alone | unknown | all BSTs on a key set share it |
| Shape from preorder alone | unique | inorder = sorted |
| `isValidBST([10,5,15,null,null,6,20])` | `false` | `6` below `10` on the right |
| `isValidBST([2147483647])` | `true` | use `null`/`long` bounds |
| Minimum node | leftmost; may have a right child | |
| Successor of a node with no right child | nearest ancestor reached from the left | |
| Delete a two-child node | copy successor up, delete it below | successor has no left child |
| Delete then re-insert | different shape | key returns as a leaf |
| `floor(5)` / `higher(6)` in the example | `4` / `7` | |
| `kthSmallest(example, 3)` | `4` | inorder `1 3 4 …` |
| `numTrees(3)` / `numTrees(19)` | `5` / `1 767 263 190` | Catalan |
| Insert sorted `1..n` | height `n − 1`, `Θ(n²)` total | chain |
| Random insertion height | `≈ 2.99 log₂ n` expected | |
| LCA in a BST | `O(h)`, no recursion | first key between `p` and `q` |
| BST iterator `next()` | `O(1)` amortized, `O(h)` worst | each node pushed once |
| Swapped adjacent keys | one inversion | set `second` at every inversion |
| `verifyPreorder([5,2,6,1,3])` | `false` | `1 < 5` after entering the right subtree |

---

## 15. Summary

- A BST keeps **every** key of the left subtree smaller and every key of the right subtree larger; equivalently, its inorder traversal is strictly increasing.
- **Search, insert, delete, min, max, floor, ceiling, successor** all walk one root-to-leaf path: `O(h)`. Insert adds a leaf; delete handles 0, 1, or 2 children, the last by swapping in the successor.
- **Validate** with bounds passed down (using `null`/`long`, not `int` extremes) or with an increasing inorder check; checking only children is wrong.
- **Order statistics**: stop an inorder traversal at `k`, or store subtree sizes for `O(h)` select and rank.
- **Ranges** prune whole subtrees: range sum, trim.
- **Build** a balanced BST from sorted data by taking medians; a BST from its preorder in `O(n)` with bounds; count shapes with Catalan numbers.
- Many problems are "do it on the inorder sequence": iterator, two sum, recover swapped nodes, linked-list conversion, minimum difference.
- The height depends on the insertion order: sorted input makes a chain. Real code uses balanced trees (`TreeMap`/`TreeSet`).

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/04 - Trees and Hierarchical Structures/01 - Binary Trees|Binary Trees]] · Next: [[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]]
- [[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]]: the same search on an array; floor/ceiling as lower/upper bound
- [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms|Sorting Algorithms]]: BST insertion and quicksort make the same comparisons
- [[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]]: two sum on a sorted sequence
- [[DSA/02 - Linear Data Structures/04 - Stacks|Stacks]]: the monotonic stack behind preorder verification
- [[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]]: guaranteed `O(log n)` height; `TreeMap`/`TreeSet`
- [[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees]]: rank queries over a fixed key range
