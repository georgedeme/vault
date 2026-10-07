# Balanced Trees

A plain BST costs `O(h)` per operation, and `h` can reach `n − 1` (sorted input makes a chain, [[DSA/04 - Trees and Hierarchical Structures/02 - Binary Search Trees#11. Height and Performance|BST § 11]]). A <span class="hl-blue">self-balancing</span> BST restores a height of `O(log n)` after every insertion and deletion, using **rotations**: local rearrangements that change the shape but keep the inorder (sorted) order. The various balanced trees differ only in which shapes they allow and when they rotate.

In practice, you'll rarely implement one: Java's `TreeMap` and `TreeSet` are red-black trees, and knowing their API (floor, ceiling, views, polling) solves most "sorted, dynamic set" problems. This note covers rotations, AVL trees and red-black trees (how they rebalance, and an implementation of each), treaps (the easiest balanced tree to write, with split and merge, and the implicit treap for sequences), other balanced structures you'll hear about, and the `TreeMap`/`TreeSet` API with its traps.

## Contents

- [[#1. Why Balance|1. Why Balance]]
- [[#2. Rotations|2. Rotations]]
- [[#3. AVL Trees|3. AVL Trees]]
- [[#4. Red-Black Trees|4. Red-Black Trees]]
- [[#5. Treaps|5. Treaps]]
- [[#6. Other Balanced Structures|6. Other Balanced Structures]]
- [[#7. TreeMap and TreeSet in Java|7. TreeMap and TreeSet in Java]]
- [[#8. Problems Solved with Ordered Sets|8. Problems Solved with Ordered Sets]]
- [[#9. Common Mistakes|9. Common Mistakes]]
- [[#10. Trick Questions and Special Cases|10. Trick Questions and Special Cases]]
- [[#11. Quick Reference — Non-Obvious Outcomes|11. Quick Reference — Non-Obvious Outcomes]]
- [[#12. Summary|12. Summary]]

---

## 1. Why Balance

| Structure | Search | Insert | Delete | Sorted iteration | Floor / ceiling |
|---|---|---|---|---|---|
| Sorted array | `O(log n)` | `O(n)` | `O(n)` | `O(n)` | `O(log n)` |
| Hash table | `O(1)` expected | `O(1)` expected | `O(1)` expected | sort first: `O(n log n)` | `O(n)` |
| Plain BST | `O(h)`, up to `O(n)` | `O(h)` | `O(h)` | `O(n)` | `O(h)` |
| **Balanced BST** | `O(log n)` | `O(log n)` | `O(log n)` | `O(n)` | `O(log n)` |

A balanced BST is the structure for data that changes **and** is queried by order: the largest key below `x`, the next event after time `t`, everything between `a` and `b`, the current minimum and maximum.

"Balanced" never means perfect: keeping a tree perfectly balanced after every insertion can require rebuilding most of it. Each scheme accepts a constant-factor slack that can be restored cheaply:

| Scheme | Invariant | Height bound |
|---|---|---|
| AVL | at every node, the subtree heights differ by at most 1 | `< 1.44 log₂(n + 2)` |
| Red-black | colouring rules: no red node has a red child; equal black count on every path | `≤ 2 log₂(n + 1)` |
| Treap | heap order on random priorities | `O(log n)` **expected** |
| Splay | none: recently accessed keys move to the root | `O(log n)` **amortized** per operation |

---

## 2. Rotations

A rotation turns a parent–child edge around: the child moves up, the parent moves down, and the one subtree that was "between" them changes sides.

```
        y                               x
       / \      rotateRight(y)         / \
      x   C     ───────────────▶      A   y
     / \        ◀───────────────         / \
    A   B        rotateLeft(x)          B   C
```

Inorder before and after: `A x B y C`. Every key in `B` is between `x` and `y`, so it can hang off either one. The rotation changes three links and nothing else: `O(1)`.

![[Balanced Trees - Rotations.excalidraw|800]]

```
rotateRight(y):                         -- returns the new subtree root
    x = y.left
    y.left = x.right                    -- B moves from x to y
    x.right = y
    return x
```

```java
static TreeNode rotateRight(TreeNode y) {
    TreeNode x = y.left;
    y.left = x.right;
    x.right = y;
    return x;
}

static TreeNode rotateLeft(TreeNode x) {
    TreeNode y = x.right;
    x.right = y.left;
    y.left = x;
    return y;
}
```

What changes: the subtree `A` moves one level up, `C` one level down, and `B` stays at the same depth. So a right rotation shortens the left side and lengthens the right side, which is exactly what's needed when the left side is too tall.

> [!warning] The parent's link must be updated too
> `rotateRight(y)` returns `x`, which now sits where `y` was. Whoever pointed at `y` (its parent, or the `root` variable) must be redirected: `node.left = rotateRight(node.left)` or `root = rotateRight(root)`. Calling `rotateRight(y);` and ignoring the result leaves the parent pointing at `y`, which is now **below** `x`, and `x` together with subtree `A` is lost. With parent pointers, `x.parent`, `y.parent`, and `B.parent` must all be fixed as well.

A rotation that's applied to a node and then to its parent (in opposite directions) is a **double rotation**. It handles the "zig-zag" shape where a single rotation would just move the imbalance to the other side ([[#3.2 The four imbalance cases|§3.2]]).

---

## 3. AVL Trees

An <span class="hl-blue">AVL tree</span> (Adelson-Velsky and Landis, 1962, the first self-balancing BST) stores each node's height and keeps the **balance factor** `height(left) − height(right)` in `{−1, 0, +1}` at every node.

### 3.1 Why the height is logarithmic

Let `N(h)` be the fewest nodes an AVL tree of height `h` (in edges) can have. The sparsest such tree has a root, one subtree of height `h − 1`, and the other of height `h − 2`, both themselves sparsest:

`N(h) = N(h − 1) + N(h − 2) + 1`, with `N(0) = 1`, `N(1) = 2`.

So `N(h) = F(h + 3) − 1` (Fibonacci numbers): `1, 2, 4, 7, 12, 20, 33, …`. Fibonacci numbers grow like `φʰ` with `φ ≈ 1.618`, so `h < 1.44 log₂(n + 2)`. An AVL tree is at most 44% taller than a perfect tree, and the height bound is the reason AVL lookups are slightly faster than red-black lookups.

### 3.2 The four imbalance cases

After inserting or deleting below a node, its balance factor can reach `±2`. Name the case by the path from the unbalanced node `z` toward its taller side:

| Case | Shape | Fix |
|---|---|---|
| **LL** | `z` is left-heavy, and its left child is left-heavy (or balanced) | `rotateRight(z)` |
| **RR** | mirror of LL | `rotateLeft(z)` |
| **LR** | `z` is left-heavy, but its left child is **right**-heavy (a zig-zag) | `rotateLeft(z.left)`, then `rotateRight(z)` |
| **RL** | mirror of LR | `rotateRight(z.right)`, then `rotateLeft(z)` |

![[Balanced Trees - AVL Four Cases.excalidraw|800]]

In the LR case, a single right rotation of `z` would move the middle subtree across and leave the tree right-heavy by 2. The first rotation turns the zig-zag into a straight line (an LL case), which the second fixes.

```
rebalance(n):
    update n.height
    if balance(n) > 1:                              -- left side too tall
        if balance(n.left) < 0: n.left = rotateLeft(n.left)      -- LR → LL
        return rotateRight(n)
    if balance(n) < −1:                             -- right side too tall
        if balance(n.right) > 0: n.right = rotateRight(n.right)  -- RL → RR
        return rotateLeft(n)
    return n
```

### 3.3 Implementation

Insertion and deletion are the plain BST versions, with `rebalance` applied to every node on the way back up the recursion.

```java
static class AVLNode {
    int key, height = 1;                           // height in nodes: a leaf has 1
    AVLNode left, right;
    AVLNode(int key) { this.key = key; }
}

static int h(AVLNode n) { return n == null ? 0 : n.height; }
static void update(AVLNode n) { n.height = 1 + Math.max(h(n.left), h(n.right)); }
static int balance(AVLNode n) { return h(n.left) - h(n.right); }

static AVLNode avlRotateRight(AVLNode y) {
    AVLNode x = y.left;
    y.left = x.right;
    x.right = y;
    update(y);                                     // y is now x's child: update it FIRST
    update(x);
    return x;
}

static AVLNode avlRotateLeft(AVLNode x) {
    AVLNode y = x.right;
    x.right = y.left;
    y.left = x;
    update(x);
    update(y);
    return y;
}

static AVLNode rebalance(AVLNode n) {
    update(n);
    int b = balance(n);
    if (b > 1) {
        if (balance(n.left) < 0) n.left = avlRotateLeft(n.left);     // LR
        return avlRotateRight(n);                                    // LL
    }
    if (b < -1) {
        if (balance(n.right) > 0) n.right = avlRotateRight(n.right); // RL
        return avlRotateLeft(n);                                     // RR
    }
    return n;
}

static AVLNode avlInsert(AVLNode n, int key) {
    if (n == null) return new AVLNode(key);
    if (key < n.key) n.left = avlInsert(n.left, key);
    else if (key > n.key) n.right = avlInsert(n.right, key);
    else return n;                                 // duplicate: nothing changed
    return rebalance(n);
}

static AVLNode avlDelete(AVLNode n, int key) {
    if (n == null) return null;
    if (key < n.key) n.left = avlDelete(n.left, key);
    else if (key > n.key) n.right = avlDelete(n.right, key);
    else {
        if (n.left == null) return n.right;
        if (n.right == null) return n.left;
        AVLNode s = n.right;
        while (s.left != null) s = s.left;         // successor
        n.key = s.key;
        n.right = avlDelete(n.right, s.key);
    }
    return rebalance(n);
}
```

Inserting `1, 2, …, 7` in sorted order, the input that makes a plain BST a chain, produces the perfect tree `[4, 2, 6, 1, 3, 5, 7]`.

> [!warning] `< 0`, not `<= 0`, when choosing a double rotation
> After a **deletion**, the taller child can be perfectly balanced (balance 0). That case needs a **single** rotation. Testing `balance(n.left) <= 0` would do a double rotation there, which leaves the tree unbalanced. (After an insertion the child's balance is never 0, so insert-only code with either test passes its tests and still breaks on deletes.)

> [!info]- How many rotations does each operation need?
> - **Insertion**: at most one rebalancing (a single or a double rotation). After it, the rotated subtree has the **same height as before the insertion**, so no ancestor's balance changes, and the recursion could stop early.
> - **Deletion**: a rotation can shrink the subtree's height by one, which can unbalance the parent, so rebalancing can cascade all the way to the root: up to `O(log n)` rotations.
>
> Both are `O(log n)` in total, because the recursion walks one root-to-leaf path either way.

---

## 4. Red-Black Trees

A <span class="hl-blue">red-black tree</span> colours every node red or black and maintains:

> [!note] The red-black properties
> 1. Every node is red or black.
> 2. The root is black.
> 3. Every `null` leaf (NIL) counts as black.
> 4. A red node has no red child (no two reds in a row).
> 5. For every node, all paths from it down to NIL leaves contain the **same number of black nodes** (its black-height).

Properties 4 and 5 together bound the height: the shortest root-to-leaf path can be all black, and the longest alternates black and red, so it's at most **twice** as long. Formally, a subtree with black-height `bh` has at least `2^bh − 1` nodes, giving `h ≤ 2 log₂(n + 1)`.

The balance is looser than AVL's (height up to `2 log₂ n` instead of `1.44 log₂ n`), but updates need fewer rotations: at most 2 per insertion and 3 per deletion, plus `O(log n)` recolourings. That's why most libraries use red-black trees: Java's `TreeMap`/`TreeSet` and `HashMap`'s overfull buckets, C++'s `std::map`, the Linux kernel scheduler.

### 4.1 Insertion

Insert as in a plain BST and colour the new node **red** (that keeps property 5). The only property that can break is 4, when the new node's parent is also red. The fix-up looks at the **uncle** (the parent's sibling):

```
insertFixup(z):                         -- z is red
    while z.parent is red:
        p = z.parent; g = p.parent; u = the other child of g
        if u is red:                    -- case 1: recolour, move the problem up two levels
            p.colour = black; u.colour = black; g.colour = red
            z = g
        else:                           -- uncle black
            if z, p, g form a zig-zag:  -- case 2: rotate at p to make a straight line
                z = p; rotate z away from z's side (left if z is p's right child)
                p = z.parent
            p.colour = black; g.colour = red                 -- case 3: straight line
            rotate g toward the other side (right if p is g's left child)
    root.colour = black
```

![[Balanced Trees - Red-Black Insert Cases.excalidraw|800]]

Case 1 only recolours and repeats higher up; cases 2 and 3 end the loop after at most two rotations. Deletion is longer (a removed black node leaves a "double black" deficit that's pushed up or resolved with up to three rotations); it's in CLRS chapter 13 and rarely asked for in interviews.

### 4.2 Left-leaning red-black trees

The full red-black insertion with parent pointers runs to about a hundred lines. Sedgewick's **left-leaning red-black tree** (LLRB) adds one restriction, red links lean left, and insertion shrinks to three local fixes applied on the way up the recursion:

```java
static final boolean RED = true, BLACK = false;

static class RBNode {
    int key;
    RBNode left, right;
    boolean color = RED;                           // new nodes are red
    RBNode(int key) { this.key = key; }
}

static boolean isRed(RBNode n) { return n != null && n.color == RED; }   // null is black

static RBNode rbRotateLeft(RBNode h) {
    RBNode x = h.right;
    h.right = x.left;
    x.left = h;
    x.color = h.color;                             // x takes h's place and h's colour
    h.color = RED;                                 // the link between them stays red
    return x;
}

static RBNode rbRotateRight(RBNode h) {
    RBNode x = h.left;
    h.left = x.right;
    x.right = h;
    x.color = h.color;
    h.color = RED;
    return x;
}

static void flipColors(RBNode h) {                 // both children red → push the red up
    h.color = RED;
    h.left.color = BLACK;
    h.right.color = BLACK;
}

static RBNode rbInsert(RBNode root, int key) {
    root = rbPut(root, key);
    root.color = BLACK;                            // property 2
    return root;
}

static RBNode rbPut(RBNode h, int key) {
    if (h == null) return new RBNode(key);
    if (key < h.key) h.left = rbPut(h.left, key);
    else if (key > h.key) h.right = rbPut(h.right, key);
    if (isRed(h.right) && !isRed(h.left)) h = rbRotateLeft(h);      // right-leaning red → lean left
    if (isRed(h.left) && isRed(h.left.left)) h = rbRotateRight(h);  // two reds in a row
    if (isRed(h.left) && isRed(h.right)) flipColors(h);             // split a temporary 4-node
    return h;
}
```

The three `if`s must run in that order, at every node on the path back up.

> [!info]- Red-black trees are 2-3-4 trees in disguise
> A **2-3-4 tree** keeps every leaf at the same depth by letting nodes hold 1, 2, or 3 keys. Glue each red node to its black parent and you get exactly such a node: a black node with one red child is a 2-key node, with two red children a 3-key node. Property 5 (equal black counts) is the 2-3-4 tree's "all leaves at the same depth"; property 4 says you can't glue more than one level.
>
> In this view, case 1 of the insertion (recolouring) is **splitting** a full 4-node and pushing its middle key up, and rotations just choose which of a multi-key node's keys is drawn on top. An LLRB corresponds to a 2-3 tree (no 4-nodes survive between operations: `flipColors` splits them immediately). This correspondence is the easiest way to remember why red-black trees work, and it leads directly to B-trees ([[#6. Other Balanced Structures|§6]]).

### 4.3 AVL vs. red-black

| | AVL | Red-black |
|---|---|---|
| Height | `< 1.44 log₂ n` | `≤ 2 log₂ n` |
| Lookups | slightly faster (shorter paths) | slightly slower |
| Rotations per insert / delete | `≤ 2` / up to `O(log n)` | `≤ 2` / `≤ 3` |
| Extra data per node | height (or a 2-bit balance factor) | one colour bit |
| Better for | lookup-heavy workloads | update-heavy workloads; Java `TreeMap`, C++ `std::map`, Linux |

Every AVL tree can be coloured as a valid red-black tree, but not every red-black tree is an AVL tree.

---

## 5. Treaps

A <span class="hl-blue">treap</span> ("tree + heap") gives each node a **random priority** and keeps two orders at once: a BST by key, and a heap by priority (every parent's priority is larger than its children's). For distinct keys and priorities, exactly one tree satisfies both, and it's the BST you'd get by inserting the keys in **decreasing priority order**. With random priorities, that's a random insertion order, so the expected height is `O(log n)` regardless of the order the keys actually arrive in.

Treaps are popular in competitive programming because everything is built from two short operations:

- **split(t, k)**: divide `t` into two treaps, keys `< k` and keys `≥ k`.
- **merge(a, b)**: join two treaps where every key of `a` is smaller than every key of `b`. The root is whichever of the two roots has the higher priority.

```
split(t, k):                            -- returns (L, R): keys < k, keys ≥ k
    if t = null: return (null, null)
    if t.key < k:
        (l, r) = split(t.right, k)      -- t and its left subtree belong to L
        t.right = l
        return (t, r)
    else:
        (l, r) = split(t.left, k)
        t.left = r
        return (l, t)

merge(a, b):                            -- all keys of a < all keys of b
    if a = null: return b
    if b = null: return a
    if a.prio > b.prio: a.right = merge(a.right, b); return a
    else:               b.left = merge(a, b.left);  return b
```

![[Balanced Trees - Treap Split and Merge.excalidraw|800]]

Insert is `split` at the key, then `merge(merge(L, node), R)`; erase splits out the key's range and merges the rest. Storing subtree sizes adds `k`-th element and rank queries, which `TreeMap` doesn't have.

```java
static final Random RNG = new Random();

static class TNode {
    int key, prio, size = 1;
    TNode left, right;
    TNode(int key) { this.key = key; this.prio = RNG.nextInt(); }
}

static int sz(TNode t) { return t == null ? 0 : t.size; }
static void pull(TNode t) { t.size = 1 + sz(t.left) + sz(t.right); }

static TNode[] split(TNode t, int key) {           // [keys < key, keys ≥ key]
    if (t == null) return new TNode[]{null, null};
    if (t.key < key) {
        TNode[] r = split(t.right, key);
        t.right = r[0];
        pull(t);
        return new TNode[]{t, r[1]};
    } else {
        TNode[] l = split(t.left, key);
        t.left = l[1];
        pull(t);
        return new TNode[]{l[0], t};
    }
}

static TNode merge(TNode a, TNode b) {             // every key in a < every key in b
    if (a == null) return b;
    if (b == null) return a;
    if (a.prio > b.prio) { a.right = merge(a.right, b); pull(a); return a; }
    else { b.left = merge(a, b.left); pull(b); return b; }
}

static boolean treapContains(TNode t, int key) {
    while (t != null && t.key != key) t = key < t.key ? t.left : t.right;
    return t != null;
}

static TNode treapInsert(TNode root, int key) {    // set semantics
    if (treapContains(root, key)) return root;
    TNode[] p = split(root, key);
    return merge(merge(p[0], new TNode(key)), p[1]);
}

static TNode treapErase(TNode root, int key) {
    TNode[] a = split(root, key);                  // a[1]: keys ≥ key
    TNode[] b = split(a[1], key + 1);              // b[0]: just key (if present)
    return merge(a[0], b[1]);
}

static int treapKth(TNode t, int k) {              // k-th smallest, 1-based
    while (true) {
        int ls = sz(t.left);
        if (k <= ls) t = t.left;
        else if (k == ls + 1) return t.key;
        else { k -= ls + 1; t = t.right; }
    }
}

static int treapRank(TNode t, int key) {           // number of keys < key
    int r = 0;
    while (t != null) {
        if (key <= t.key) t = t.left;
        else { r += sz(t.left) + 1; t = t.right; }
    }
    return r;
}
```

All operations take `O(log n)` expected time. Two details: `treapErase` uses `key + 1`, which overflows for `Integer.MAX_VALUE` (split on `long`, or erase by walking to the node and replacing it with `merge(node.left, node.right)`); and the priorities must be **random**, since priorities that correlate with keys (say, increasing) turn the treap back into a chain.

> [!example]- Implicit treap: a sequence with O(log n) reverse, insert, and delete anywhere (advanced)
> Drop the keys. A node's **position** in the sequence is its inorder index, computed from subtree sizes, so `split(t, k)` splits off the first `k` elements. Lazy flags work as in segment trees ([[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees|Segment Trees]]): to reverse a range, split it out, flip a `rev` flag on its root, and merge back; the flag is pushed down (children swapped) whenever a node is visited.
> ```java
> static class INode {
>     int val, prio = RNG.nextInt(), size = 1;
>     boolean rev;                                   // "this subtree's order is reversed"
>     INode left, right;
>     INode(int val) { this.val = val; }
> }
>
> static int isz(INode t) { return t == null ? 0 : t.size; }
> static void ipull(INode t) { t.size = 1 + isz(t.left) + isz(t.right); }
>
> static void push(INode t) {                        // apply a pending reversal one level down
>     if (t != null && t.rev) {
>         INode tmp = t.left; t.left = t.right; t.right = tmp;
>         if (t.left != null) t.left.rev ^= true;
>         if (t.right != null) t.right.rev ^= true;
>         t.rev = false;
>     }
> }
>
> static INode[] isplit(INode t, int k) {            // [first k elements, the rest]
>     if (t == null) return new INode[]{null, null};
>     push(t);
>     if (isz(t.left) < k) {
>         INode[] r = isplit(t.right, k - isz(t.left) - 1);
>         t.right = r[0]; ipull(t);
>         return new INode[]{t, r[1]};
>     } else {
>         INode[] l = isplit(t.left, k);
>         t.left = l[1]; ipull(t);
>         return new INode[]{l[0], t};
>     }
> }
>
> static INode imerge(INode a, INode b) {
>     if (a == null) return b;
>     if (b == null) return a;
>     if (a.prio > b.prio) { push(a); a.right = imerge(a.right, b); ipull(a); return a; }
>     else { push(b); b.left = imerge(a, b.left); ipull(b); return b; }
> }
>
> static INode reverse(INode t, int l, int r) {      // reverse positions l..r, 0-based inclusive
>     INode[] a = isplit(t, l);
>     INode[] b = isplit(a[1], r - l + 1);
>     if (b[0] != null) b[0].rev ^= true;
>     return imerge(a[0], imerge(b[0], b[1]));
> }
>
> static void toList(INode t, List<Integer> out) {
>     if (t == null) return;
>     push(t);
>     toList(t.left, out); out.add(t.val); toList(t.right, out);
> }
> ```
> Building `[1..6]` by merging single nodes and reversing positions `1..4` gives `[1, 5, 4, 3, 2, 6]`. Inserting at position `i` is `isplit(t, i)` plus two merges; adding range-sum or range-min fields in `ipull` turns it into a sequence with range queries **and** arbitrary insertions, which an array-based segment tree can't do.

---

## 6. Other Balanced Structures

| Structure | Idea | Guarantee | Where it's used |
|---|---|---|---|
| **Splay tree** | every access rotates the accessed node to the root | `O(log n)` amortized; one operation can be `O(n)` | caches (recent keys are near the root); link-cut trees |
| **B-tree / B+ tree** | nodes hold up to `2t − 1` keys and `2t` children; all leaves at the same depth | height `log_t n` | databases and file systems: one node = one disk page, so few disk reads |
| **Skip list** | sorted linked list with random "express lanes" | `O(log n)` expected | Java's `ConcurrentSkipListMap`/`Set` (easier to make lock-free than a tree); Redis sorted sets |
| **Scapegoat tree** | no per-node balance data; when a node gets too deep, rebuild a subtree perfectly | `O(log n)` amortized | when nodes must stay small |
| **AA tree** | red-black tree where red links can only be right children | same as red-black | simpler code |
| **Weight-balanced tree** | balance by subtree sizes instead of heights | `O(log n)` | functional languages (Haskell `Data.Map`) |

> [!tip] When a skip list instead of `TreeMap`
> `TreeMap` isn't thread-safe; wrapping it in `Collections.synchronizedSortedMap` serialises every access. `ConcurrentSkipListMap` has the same `NavigableMap` API (floor, ceiling, views) and supports concurrent readers and writers. Single-threaded, `TreeMap` is usually faster.

---

## 7. TreeMap and TreeSet in Java

`TreeMap<K, V>` is a red-black tree of key–value entries; `TreeSet<E>` is a `TreeMap` with dummy values. Keys are ordered by their natural order (`Comparable`) or by a `Comparator` given to the constructor.

### 7.1 API

| Operation (`TreeMap` / `TreeSet`) | Returns | Cost |
|---|---|---|
| `put`, `get`, `remove`, `containsKey` / `add`, `remove`, `contains` | | `O(log n)` |
| `firstKey()`, `lastKey()` / `first()`, `last()` | the key; **throws** `NoSuchElementException` if empty | `O(log n)` |
| `firstEntry()`, `lastEntry()` | the entry, or `null` if empty | `O(log n)` |
| `pollFirstEntry()`, `pollLastEntry()` / `pollFirst()`, `pollLast()` | removes and returns it, or `null` if empty | `O(log n)` |
| `floorKey(x)`, `ceilingKey(x)`, `lowerKey(x)`, `higherKey(x)` / `floor`, `ceiling`, `lower`, `higher` | `≤ x`, `≥ x`, `< x`, `> x`, or `null` | `O(log n)` |
| `floorEntry(x)`, … | the entry, or `null` | `O(log n)` |
| `headMap(x)` / `headSet(x)` | **view** of keys `< x` (exclusive by default) | `O(log n)` to create |
| `tailMap(x)` / `tailSet(x)` | **view** of keys `≥ x` (inclusive by default) | `O(log n)` to create |
| `subMap(a, b)` / `subSet(a, b)` | **view** of keys in `[a, b)` | `O(log n)` to create |
| `headMap(x, true)`, `subMap(a, false, b, true)`, … | the same, with explicit inclusivity | |
| `descendingMap()`, `descendingKeySet()` / `descendingSet()`, `descendingIterator()` | reverse-order views | `O(1)` |
| iteration over `keySet()`, `values()`, `entrySet()` | ascending key order | `O(n)` total |
| `size()` of a view | | **`O(k)`**: it counts |

The views are **live**: changes to the map show up in the view and vice versa. Adding a key outside a view's range through the view throws `IllegalArgumentException`.

```java
TreeMap<Integer, String> m = new TreeMap<>(Map.of(10, "a", 20, "b", 30, "c"));
m.floorKey(25);                 // 20
m.ceilingKey(25);               // 30
m.higherKey(30);                // null
m.headMap(20);                  // {10=a}           (20 excluded)
m.tailMap(20);                  // {20=b, 30=c}     (20 included)
m.subMap(10, 30);               // {10=a, 20=b}
m.descendingMap();              // {30=c, 20=b, 10=a}
m.pollFirstEntry();             // 10=a, and removes it
```

### 7.2 Patterns

**Counting multiset.** Java has no `TreeMultiset`; use `TreeMap<value, count>`:

```java
static void addOne(TreeMap<Integer, Integer> ms, int x) {
    ms.merge(x, 1, Integer::sum);
}

static void removeOne(TreeMap<Integer, Integer> ms, int x) {
    ms.computeIfPresent(x, (k, c) -> c == 1 ? null : c - 1);   // returning null removes the key
}
```

Then `firstKey()`/`lastKey()` are the current min and max, and `floorKey`/`ceilingKey` find neighbours, all with duplicates counted correctly.

**Duplicates in a `TreeSet`.** Store indices and compare by value, then by index, so equal values stay distinct elements: `new TreeSet<Integer>((i, j) -> a[i] != a[j] ? Integer.compare(a[i], a[j]) : Integer.compare(i, j))`. This is how sliding-window problems keep a sorted window of possibly equal values.

**Interval maps.** `TreeMap<start, end>` with `floorEntry(x)` finds the interval that could contain `x`. Booking, merging, and "which interval covers `x`" problems follow ([[#8.2 My Calendar: non-overlapping bookings|§8.2]], [[DSA/08 - Specialized Topics/01 - Intervals and Sweep Line|Intervals and Sweep Line]]).

### 7.3 Traps

> [!warning] The comparator defines equality
> `TreeSet` and `TreeMap` never call `equals`: two elements are the **same** if `compare` returns 0. A comparator on part of the data silently drops elements:
> ```java
> TreeSet<int[]> s = new TreeSet<>((a, b) -> Integer.compare(a[0], b[0]));
> s.add(new int[]{1, 5});
> s.add(new int[]{1, 9});        // compare → 0: treated as a duplicate, NOT added
> s.size();                      // 1
>
> TreeSet<String> t = new TreeSet<>(Comparator.comparingInt(String::length));
> t.add("ab");
> t.contains("xy");              // true: same length
> ```
> Break ties on every field (`thenComparingInt(a -> a[1])`), or on an index or id. The Javadoc calls this "consistent with equals".

> [!warning] `null` results and unboxing
> `int f = map.floorKey(x);` compiles, and throws `NullPointerException` when no key `≤ x` exists, because `floorKey` returns `Integer`. Assign to `Integer` and check for `null`. Likewise `firstKey()` **throws** on an empty map, while `firstEntry()` and `pollFirst()` return `null`.

Other traps:
- **No rank.** There's no `O(log n)` way to ask "how many keys are less than `x`" or "what's the `k`-th key": `headSet(x).size()` walks the elements, `O(k)`. Use a treap with sizes ([[#5. Treaps|§5]]) or a Fenwick tree over compressed values ([[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees]]).
- **Mutating a key** that's in the tree breaks the ordering, as with `HashMap` keys ([[DSA/02 - Linear Data Structures/06 - Hash Tables#8. Hashing Custom Objects|Hash Tables § 8]]): remove it, change it, re-insert.
- **`null` keys** throw `NullPointerException` with natural ordering (`HashMap` allows one `null` key).
- **Modifying while iterating** throws `ConcurrentModificationException`; use `iterator.remove()`, or `pollFirst()` in a loop.
- **Overflowing comparators** like `(a, b) -> a - b` give a wrong order for large values of opposite sign; use `Integer.compare` ([[DSA/03 - Sorting and Searching/01 - Sorting Algorithms#10.2 Comparator traps|Sorting § 10.2]]).
- **`remove(Object)` on a `TreeMap<Long, …>`** with an `int` argument boxes to `Integer`, which throws `ClassCastException` as soon as it's compared with a `Long` key (unlike `HashMap`, which just doesn't find it). On an empty map nothing is compared, so the bug hides until the map has entries.

---

## 8. Problems Solved with Ordered Sets

### 8.1 Nearby almost-duplicate

"Are there indices `i ≠ j` with `|i − j| ≤ k` and `|a[i] − a[j]| ≤ t`?" Keep the last `k` values in a sorted set; for each new value `x`, the closest candidates are the ceiling of `x − t` and nothing else matters.

```java
static boolean containsNearbyAlmostDuplicate(int[] a, int k, int t) {
    TreeSet<Long> window = new TreeSet<>();        // long: a[i] − t can overflow int
    for (int i = 0; i < a.length; i++) {
        Long c = window.ceiling((long) a[i] - t);  // smallest value ≥ a[i] − t
        if (c != null && c <= (long) a[i] + t) return true;
        window.add((long) a[i]);
        if (i >= k) window.remove((long) a[i - k]);    // slide: keep only the last k values
    }
    return false;
}
```

`O(n log k)`. `[1, 2, 3, 1]`, `k = 3`, `t = 0` → `true`; `[1, 5, 9, 1, 5, 9]`, `k = 2`, `t = 3` → `false`. The window holds distinct values only, which is safe: a duplicate inside the window would already have returned `true`. A bucket-based hash solution does it in `O(n)`.

### 8.2 My Calendar: non-overlapping bookings

Accept a booking `[start, end)` only if it overlaps no existing one. The only candidates for overlap are the booking that starts at or before `start` and the one that starts after it.

```java
static class MyCalendar {
    private final TreeMap<Integer, Integer> booked = new TreeMap<>();   // start → end

    boolean book(int start, int end) {
        Map.Entry<Integer, Integer> prev = booked.floorEntry(start);
        if (prev != null && prev.getValue() > start) return false;     // prev runs past start
        Integer next = booked.ceilingKey(start);
        if (next != null && next < end) return false;                  // next begins before end
        booked.put(start, end);
        return true;
    }
}
```

`book(10, 20)` → `true`, `book(15, 25)` → `false`, `book(20, 30)` → `true` (half-open: `[10, 20)` and `[20, 30)` only touch). `O(log n)` per booking, versus `O(n)` for scanning a list.

### 8.3 Longest subarray with max − min ≤ limit

A sliding window ([[DSA/03 - Sorting and Searching/04 - Sliding Window|Sliding Window]]) whose validity depends on the window's minimum and maximum. A counting `TreeMap` gives both in `O(log n)`:

```java
static int longestSubarray(int[] a, int limit) {
    TreeMap<Integer, Integer> win = new TreeMap<>();   // value → count
    int best = 0;
    for (int l = 0, r = 0; r < a.length; r++) {
        win.merge(a[r], 1, Integer::sum);
        while (win.lastKey() - win.firstKey() > limit) {
            win.computeIfPresent(a[l], (key, c) -> c == 1 ? null : c - 1);
            l++;
        }
        best = Math.max(best, r - l + 1);
    }
    return best;
}
```

`[8, 2, 4, 7]`, limit 4 → `2`; `[10, 1, 2, 4, 7, 2]`, limit 5 → `4`. Two monotonic deques make it `O(n)` ([[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]]), but the `TreeMap` version also handles "remove an arbitrary element" and "find the median", which deques can't.

### 8.4 Where an ordered set is the right tool

| Signal in the problem | Use |
|---|---|
| "closest value to `x`" in a set that changes | `floor` + `ceiling` |
| current min **and** max under insertions and deletions | `TreeMap` multiset (a heap gives only one end, and can't delete arbitrary elements) |
| intervals: which one contains `x`, merging on insert | `TreeMap<start, end>` + `floorEntry` |
| events in time order, with cancellations | `TreeMap<time, …>` + `pollFirstEntry` |
| sorted iteration plus updates | `TreeMap` |
| "how many elements are less than `x`" with updates | **not** `TreeSet`: Fenwick tree or treap |
| only the min (or only the max), no arbitrary deletions | a heap is simpler and faster ([[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|Heaps and Priority Queues]]) |

---

## 9. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Ignoring a rotation's return value | subtree lost, tree corrupted | `node.left = rotateRight(node.left)` / `root = …` |
| Updating heights in the wrong order after a rotation | wrong heights, later imbalances missed | update the node that moved down first |
| Single rotation for a zig-zag (LR/RL) | still unbalanced | double rotation |
| `balance(child) <= 0` for the double-rotation test | wrong fix after deletions | `< 0` (and `> 0` on the mirror side) |
| Forgetting to rebalance on the way up after delete | AVL invariant broken | `rebalance` every node on the path |
| New red-black node coloured black | black-heights unequal | new nodes are red |
| Root left red | property 2 broken (harmless but violates invariants checked by tests) | colour the root black at the end |
| Treap priorities not random | `O(n)` height on sorted input | `Random` priorities |
| `treapErase` with `key + 1` at `Integer.MAX_VALUE` | overflow: wrong range removed | split on `long`, or erase by node |
| Partial comparator in `TreeSet` | "duplicates" silently dropped | tie-break on every field or an id |
| `int x = map.floorKey(k)` | `NullPointerException` | `Integer`, check `null` |
| `firstKey()` on an empty map | `NoSuchElementException` | `firstEntry()` / `isEmpty()` check |
| `headSet(x).size()` as a rank query | `O(n)` per query | Fenwick tree / treap with sizes |
| `TreeSet` used as a multiset | duplicates lost | `TreeMap<value, count>` or index tie-breaks |
| `merge(x, -1, Integer::sum)` to decrement | zero counts left behind; `firstKey` returns a value with count 0 | `computeIfPresent(…, c == 1 ? null : c − 1)` |

---

## 10. Trick Questions and Special Cases

> [!question]- Does a rotation change the inorder traversal?
> No. That's the point: `A x B y C` before and after. It changes depths (one side gets shorter, the other longer) and the preorder/postorder, never the sorted order.

> [!question]- Insert `1, 2, …, 7` in order into an AVL tree. What's the result?
> The perfect tree `[4, 2, 6, 1, 3, 5, 7]`, height 2. Sorted input, the worst case for a plain BST, is handled with a few RR rotations.

> [!question]- Can an AVL tree with 7 nodes have height 3 (edges)?
> Yes: the minimum number of nodes for height 3 is `N(3) = 7`. So an AVL tree with 7 nodes may be perfect (height 2) or a sparse Fibonacci-shaped tree of height 3. AVL doesn't mean "as short as possible".

> [!question]- Is every complete binary tree a valid AVL tree? Every AVL tree a complete tree?
> Complete → AVL: yes (in a complete tree, the subtree heights at any node differ by at most 1). AVL → complete: no; a Fibonacci-shaped AVL tree has leaves at several depths and gaps on the last level.

> [!question]- Can a red-black tree have no red nodes at all?
> Yes, but then property 5 forces every root-to-leaf path to have the same length: the tree is perfect, with `2ᵏ − 1` nodes. Most sizes need some red nodes.

> [!question]- In a red-black tree, how much longer can the longest root-to-leaf path be than the shortest?
> At most twice as long. Both have the same number of black nodes, and red nodes can't be adjacent, so the longest path alternates black and red.

> [!question]- Is every red-black tree an AVL tree?
> No. A red-black tree can have a node whose subtrees differ in height by more than 1 (one side all black, the other alternating red and black, with equal black counts). Every AVL tree, though, can be coloured to satisfy the red-black properties.

> [!question]- Why are new red-black nodes red rather than black?
> A new black node would add one black node to the paths through it and break property 5 everywhere above it, which is hard to fix. A red node keeps black-heights intact and can only break property 4 (red parent), a local problem the fix-up handles.

> [!question]- AVL deletion: the unbalanced node is left-heavy by 2, and its left child has balance 0. Single or double rotation?
> Single (`rotateRight`). A double rotation would leave the tree unbalanced the other way. This case can't happen after an insertion, so insert-only tests don't catch the `<= 0` bug.

> [!question]- What's in `new TreeSet<>(Comparator.comparingInt(String::length))` after adding `"ab"`, `"cd"`, `"efg"`?
> `["ab", "efg"]`: `"cd"` compares equal to `"ab"` (same length) and is treated as already present. `contains("xy")` then returns `true`.

> [!question]- `TreeMap<Integer, Integer> m` is empty. What do `m.firstKey()`, `m.firstEntry()`, and `m.pollFirstEntry()` do?
> `firstKey()` throws `NoSuchElementException`; the other two return `null`. The `…Key()`/`first()`/`last()` methods throw, the `…Entry()` and `poll…()` methods return `null`.

> [!question]- How do you find how many elements of a `TreeSet` are less than `x`?
> `headSet(x).size()` gives the right answer in `O(k)` time, because a view's `size()` iterates. There's no `O(log n)` rank in the JDK; use a Fenwick tree over compressed values, or an order-statistic tree such as a treap with subtree sizes.

> [!question]- A treap's priorities are assigned as `prio = key`. What happens on inserting `1..n` in order?
> Each new key has the highest priority so far, so it becomes the root, with all earlier keys in its left subtree: a chain of height `n − 1`. The randomness of the priorities is what makes treaps balanced, not the split/merge code.

> [!question]- `My Calendar`: are `[10, 20)` and `[20, 30)` a conflict?
> No: half-open intervals that only touch don't overlap. The test is `prev.end > start` (strict). Using `>=` rejects back-to-back bookings.

> [!question]- Why does `remove(5)` throw on a non-empty `TreeMap<Long, …>` but not on a `HashMap<Long, …>`?
> `5` boxes to an `Integer`. `HashMap` compares with `equals`, which returns `false` for `Integer` vs `Long`, so nothing is removed and nothing is thrown. `TreeMap` compares the argument with the keys using `compareTo`, and comparing an `Integer` with a `Long` throws `ClassCastException`. On an **empty** `TreeMap` there's no key to compare with, so it returns `null` without throwing: the bug appears only once the map has entries.

---

## 11. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| Rotation | `O(1)`, inorder unchanged | three links change |
| AVL height bound | `< 1.44 log₂(n + 2)` | Fibonacci-sized sparsest trees |
| Min nodes of AVL height `0, 1, 2, 3, 4` | `1, 2, 4, 7, 12` | `N(h) = F(h + 3) − 1` |
| Red-black height bound | `≤ 2 log₂(n + 1)` | equal black counts, no red–red |
| Rotations per insertion (AVL / RB) | `≤ 2` / `≤ 2` | |
| Rotations per deletion (AVL / RB) | `O(log n)` / `≤ 3` | |
| AVL insert of `1..7` | `[4, 2, 6, 1, 3, 5, 7]` | |
| Treap shape | BST of keys inserted by decreasing priority | unique for distinct priorities |
| Treap height | `O(log n)` expected | random priorities |
| `TreeSet` with a length comparator: `"ab"`, `"cd"` | size 1 | compare = 0 means equal |
| `int x = map.floorKey(k)` with no floor | `NullPointerException` | unboxing `null` |
| `firstKey()` on empty | throws | `firstEntry()` returns `null` |
| `headMap(x)` / `tailMap(x)` | `< x` / `≥ x` | default inclusivity |
| `headSet(x).size()` | `O(k)` | views count by iterating |
| `TreeMap` thread safety | none | `ConcurrentSkipListMap` |
| `treeMapOfLong.remove(5)` (non-empty) | `ClassCastException` | `Integer` compared with `Long` |
| `MyCalendar`: `[10,20)` then `[20,30)` | both accepted | half-open |

---

## 12. Summary

- Balanced BSTs keep the height `O(log n)` under insertions and deletions; **rotations** fix the shape in `O(1)` without changing the sorted order.
- **AVL**: heights differ by at most 1 at every node; four cases (LL, RR, LR, RL), the zig-zag ones needing a double rotation. Height `< 1.44 log₂ n`; fast lookups.
- **Red-black**: colouring rules bound the height by `2 log₂ n`; insertion recolours (red uncle) or rotates (black uncle); at most 2–3 rotations per update. It's what `TreeMap` uses. LLRB trees make the code short; 2-3-4 trees explain why it works.
- **Treaps**: BST by key, heap by random priority; split and merge give insert, erase, `k`-th, and rank. Implicit treaps handle sequences with reversals and arbitrary insertions.
- Other options: splay trees (amortized, adaptive), B-trees (disks), skip lists (concurrency).
- **`TreeMap`/`TreeSet`**: floor/ceiling/lower/higher, first/last/poll, and live head/tail/sub views. The comparator defines equality; `…Key()` methods return `null` and `first()`/`last()` throw; there's no rank.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/04 - Trees and Hierarchical Structures/02 - Binary Search Trees|Binary Search Trees]] · Next: [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|Heaps and Priority Queues]]
- [[DSA/02 - Linear Data Structures/06 - Hash Tables|Hash Tables]]: the unordered alternative; `HashMap` buckets become red-black trees
- [[DSA/02 - Linear Data Structures/03 - Linked Lists|Linked Lists]]: skip lists
- [[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]]: floor and ceiling on static sorted arrays
- [[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees|Segment Trees]]: lazy propagation, the same idea as the implicit treap's reverse flag
- [[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees]]: rank queries that `TreeSet` can't answer
- [[DSA/08 - Specialized Topics/01 - Intervals and Sweep Line|Intervals and Sweep Line]]: `TreeMap`-based interval problems
