# Binary Trees

A <span class="hl-blue">binary tree</span> is a set of nodes where each node holds a value and has at most two children, a **left** and a **right** child, and every node except the root has exactly one parent. It's the first non-linear structure in this syllabus, and most tree problems come down to one question: **what should a recursive call on a subtree return?** Once that's clear, the answer for a node combines the answers for its two subtrees.

This note covers the vocabulary (and its two incompatible height conventions), how trees are stored, the four traversals in recursive and iterative form (including Morris traversal in `O(1)` space), level-order patterns, height/balance/diameter/path-sum problems, comparing and transforming trees, rebuilding a tree from its traversals, serialization, and treating a tree as a graph. Search trees, heaps, and the other specialised trees build on all of this.

## Contents

- [[#1. Terminology|1. Terminology]]
- [[#2. Representing Trees in Java|2. Representing Trees in Java]]
- [[#3. Depth-First Traversals|3. Depth-First Traversals]]
- [[#4. Iterative Traversals|4. Iterative Traversals]]
- [[#5. Level-Order Traversal|5. Level-Order Traversal]]
- [[#6. Depth, Height, and Balance|6. Depth, Height, and Balance]]
- [[#7. Diameter and Path Problems|7. Diameter and Path Problems]]
- [[#8. Comparing and Transforming Trees|8. Comparing and Transforming Trees]]
- [[#9. Building a Tree from Traversals|9. Building a Tree from Traversals]]
- [[#10. Serialization|10. Serialization]]
- [[#11. Trees as Graphs|11. Trees as Graphs]]
- [[#12. Common Mistakes|12. Common Mistakes]]
- [[#13. Trick Questions and Special Cases|13. Trick Questions and Special Cases]]
- [[#14. Quick Reference — Non-Obvious Outcomes|14. Quick Reference — Non-Obvious Outcomes]]
- [[#15. Summary|15. Summary]]

---

## 1. Terminology

> [!note] Definitions
> - **Root**: the only node without a parent. **Leaf**: a node with no children. **Internal node**: a node with at least one child.
> - **Edge**: a parent–child link. A tree with `n` nodes has exactly **`n − 1` edges**.
> - **Ancestor / descendant**: `u` is an ancestor of `v` if `u` is on the path from the root to `v`. In most definitions (and in LCA problems) a node is its **own** ancestor and descendant.
> - **Subtree of `v`**: `v` together with **all** of its descendants.
> - **Depth** of a node: the number of edges from the root to it. The root has depth 0. **Level** usually means depth (some texts start levels at 1).
> - **Height** of a node: the number of edges on the longest downward path from it to a leaf. A leaf has height 0. The **height of a tree** is the height of its root.
> - **Size**: the number of nodes.

> [!warning] Two height conventions
> Textbooks count **edges**: a single node has height 0 and the empty tree has height `−1`. LeetCode's "maximum depth" counts **nodes**: a single node has depth 1 and the empty tree 0. Both are common, and mixing them gives off-by-one answers, especially in diameter (edges) and balance checks (either works, as long as both subtrees use the same one). This note counts **nodes** in code (`height(null) = 0`) unless it says otherwise, and says "edges" explicitly when a problem asks for them.

### 1.1 Shapes

| Shape | Definition | Example property |
|---|---|---|
| **Full** (proper, strict) | every node has 0 or 2 children | leaves = internal nodes + 1 |
| **Complete** | every level full except possibly the last, which is filled **from the left** | fits in an array with no gaps; height `⌊log₂ n⌋` |
| **Perfect** | all internal nodes have 2 children and all leaves have the same depth | `2^(h+1) − 1` nodes, `2^h` leaves (height `h` in edges) |
| **Height-balanced** | at every node, the subtree heights differ by at most 1 | height `O(log n)` |
| **Degenerate** (skewed) | every internal node has exactly one child | a linked list: height `n − 1` |

![[Binary Trees - Tree Shapes.excalidraw|800]]

A perfect tree is both full and complete, but neither of the other two implies anything: a full tree can have its leaves at very different depths, and a complete tree can have a node with only a left child.

### 1.2 Counting facts

| Fact | Value | Why |
|---|---|---|
| Edges | `n − 1` | every node but the root has one parent edge |
| `null` child pointers | `n + 1` | `2n` pointer slots, `n − 1` are used |
| Leaves vs. two-child nodes | `n₀ = n₂ + 1` | in **any** binary tree |
| Max nodes at depth `d` | `2^d` | each level at most doubles |
| Height of `n` nodes | between `⌈log₂(n + 1)⌉ − 1` and `n − 1` (edges) | perfect vs. degenerate |
| Distinct shapes with `n` nodes | Catalan number `C(n)`: 1, 1, 2, 5, 14, 42, … | choose the left subtree's size `k`, then `C(k)·C(n − 1 − k)` |

The `n₀ = n₂ + 1` fact follows from counting edges two ways: `n − 1 = n₁ + 2n₂` and `n = n₀ + n₁ + n₂`. One-child nodes cancel out, so they never change the number of leaves.

---

## 2. Representing Trees in Java

### 2.1 Linked nodes

The standard representation, and the one used by LeetCode:

```java
class TreeNode {
    int val;
    TreeNode left, right;

    TreeNode(int val) { this.val = val; }
    TreeNode(int val, TreeNode left, TreeNode right) {
        this.val = val; this.left = left; this.right = right;
    }
}
```

A missing child is `null`. Add a `parent` field only when a problem needs upward moves (successor queries, distance-`k` problems); it doubles the work of every structural change, since both directions must stay consistent.

### 2.2 Arrays for complete trees

A **complete** tree can be stored in an array in level order, with no pointers at all:

| Indexing | Children of `i` | Parent of `i` |
|---|---|---|
| 0-based | `2i + 1`, `2i + 2` | `(i − 1) / 2` |
| 1-based | `2i`, `2i + 1` | `i / 2` |

This is how heaps ([[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|Heaps and Priority Queues]]) and segment trees ([[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees|Segment Trees]]) are stored. For other shapes it wastes space: a degenerate tree of height `h` needs `2^(h+1) − 1` slots for `h + 1` nodes.

### 2.3 LeetCode's level-order format

Problems write trees as level-order arrays with `null` for missing children, such as `[1, 2, 3, 4, 5, null, 6, null, null, 7]`. Unlike the heap layout, **children of `null` are not listed**, so a node's index can't be computed from its parent's. The builder needs a queue:

```
fromLevelOrder(a):
    if a is empty or a[0] is null: return null
    root = node(a[0]); queue = [root]; i = 1
    while i < length(a):
        cur = queue.pop()
        if a[i] ≠ null: cur.left = node(a[i]); queue.push(cur.left)
        i = i + 1
        if i < length(a) and a[i] ≠ null: cur.right = node(a[i]); queue.push(cur.right)
        i = i + 1
    return root
```

```java
static TreeNode fromLevelOrder(Integer[] a) {
    if (a.length == 0 || a[0] == null) return null;
    TreeNode root = new TreeNode(a[0]);
    Deque<TreeNode> q = new ArrayDeque<>();
    q.add(root);
    int i = 1;
    while (i < a.length) {
        TreeNode cur = q.poll();
        if (a[i] != null) { cur.left = new TreeNode(a[i]); q.add(cur.left); }
        i++;
        if (i < a.length && a[i] != null) { cur.right = new TreeNode(a[i]); q.add(cur.right); }
        i++;
    }
    return root;
}
```

The array must be `Integer[]` (not `int[]`) to hold `null`s. The running example in this note is `[1, 2, 3, 4, 5, null, 6, null, null, 7]`:

```
        1
      /   \
     2     3
    / \     \
   4   5     6
      /
     7
```

> [!example]- Why `[1, null, 2, 3]` is not the heap layout
> In the heap layout, index 3 would be the left child of index 1, the `null`. In LeetCode's format, the children of a `null` are skipped, so `3` is the **left child of `2`**: the tree is `1 → right 2 → left 3`. Reading such an array with `2i + 1`/`2i + 2` arithmetic gives the wrong tree, or an index out of range.

---

## 3. Depth-First Traversals

A traversal visits every node once. The three depth-first orders differ only in **when** a node is visited relative to its two subtrees:

```
dfs(node):
    if node = null: return
    visit(node)              -- preorder:  node, left, right
    dfs(node.left)
    visit(node)              -- inorder:   left, node, right
    dfs(node.right)
    visit(node)              -- postorder: left, right, node
```

```java
static void preorder(TreeNode n, List<Integer> out) {
    if (n == null) return;
    out.add(n.val);
    preorder(n.left, out);
    preorder(n.right, out);
}

static void inorder(TreeNode n, List<Integer> out) {
    if (n == null) return;
    inorder(n.left, out);
    out.add(n.val);
    inorder(n.right, out);
}

static void postorder(TreeNode n, List<Integer> out) {
    if (n == null) return;
    postorder(n.left, out);
    postorder(n.right, out);
    out.add(n.val);
}
```

On the running example:

| Order | Sequence | Typical use |
|---|---|---|
| Preorder | `1 2 4 5 7 3 6` | copying and serializing a tree; passing information **down** (depth, path so far) |
| Inorder | `4 2 7 5 1 3 6` | a BST's keys in **sorted** order ([[DSA/04 - Trees and Hierarchical Structures/02 - Binary Search Trees|Binary Search Trees]]) |
| Postorder | `4 7 5 2 6 3 1` | anything that needs the children's results first: height, size, deleting a tree, evaluating an expression |
| Level order | `1 · 2 3 · 4 5 6 · 7` | anything by level or by distance from the root ([[#5. Level-Order Traversal|§5]]) |

![[Binary Trees - Traversal Orders.excalidraw|800]]

All four take `O(n)` time. The recursive versions use `O(h)` stack space: `O(log n)` for a balanced tree, `O(n)` for a degenerate one.

> [!tip] Reading the orders off a drawing
> Walk around the outline of the tree counter-clockwise, starting left of the root. Each node is passed three times: on its **left** side (preorder), **underneath** (inorder), and on its **right** side (postorder). Listing nodes at the moment you pass the chosen side gives that order.

For an **expression tree** (operators at internal nodes, operands at leaves), preorder gives prefix notation, postorder gives postfix notation, and inorder gives infix **without the parentheses**, which is ambiguous: `(1 + 2) * 3` and `1 + (2 * 3)` have the same inorder sequence. See [[DSA/02 - Linear Data Structures/04 - Stacks#6.1 Three notations|Stacks § 6.1]].

### 3.1 Two styles of tree recursion

| Style | Information flows | Implemented as | Examples |
|---|---|---|---|
| **Top-down** | from parent to children, as **parameters** | preorder | depth of each node, root-to-leaf sums, "good nodes" (no larger ancestor) |
| **Bottom-up** | from children to parent, as **return values** | postorder | height, size, balance, diameter, max path sum |

A function that needs both receives the parent's information as a parameter and returns the subtree's summary. When the answer isn't the same thing the recursion returns (diameter returns a height but reports a path length), keep the answer in a separate variable, such as a one-element array or a field ([[#7.1 Diameter|§7.1]]).

> [!example]- Top-down: count "good" nodes
> A node is good if no node on the path from the root to it has a larger value. The maximum so far travels down as a parameter:
> ```java
> static int goodNodes(TreeNode n, int maxSoFar) {
>     if (n == null) return 0;
>     int good = n.val >= maxSoFar ? 1 : 0;
>     int m = Math.max(maxSoFar, n.val);
>     return good + goodNodes(n.left, m) + goodNodes(n.right, m);
> }
> ```
> Start with `goodNodes(root, Integer.MIN_VALUE)` (or `root.val`): the root is always good. `[3, 1, 4, 3, null, 1, 5]` → `4`.

---

## 4. Iterative Traversals

Recursion depth equals the tree's height, so a degenerate tree with `10⁵` nodes overflows Java's default stack ([[DSA/01 - Foundations/02 - Recursion#9. Stack Overflow Limits in Java|Recursion § 9]]). The iterative versions replace the call stack with an explicit one.

### 4.1 Preorder

```
preorderIterative(root):
    stack = [root]                      -- if root ≠ null
    while stack not empty:
        n = stack.pop(); visit(n)
        push n.right, then n.left       -- skip nulls; left is pushed last, so popped first
```

```java
static List<Integer> preorderIterative(TreeNode root) {
    List<Integer> out = new ArrayList<>();
    if (root == null) return out;
    Deque<TreeNode> st = new ArrayDeque<>();
    st.push(root);
    while (!st.isEmpty()) {
        TreeNode n = st.pop();
        out.add(n.val);
        if (n.right != null) st.push(n.right);     // right first: the stack reverses the order
        if (n.left != null) st.push(n.left);
    }
    return out;
}
```

> [!warning] `ArrayDeque` rejects `null`
> `st.push(null)` throws `NullPointerException`, so the `!= null` checks are required, not just an optimisation. (`LinkedList` accepts `null`, which only moves the bug: a later `n.val` throws instead.)

### 4.2 Inorder

Go left as far as possible, pushing every node on the way. Pop one, visit it, then do the same for its right subtree.

```
inorderIterative(root):
    cur = root; stack = []
    while cur ≠ null or stack not empty:
        while cur ≠ null: stack.push(cur); cur = cur.left
        cur = stack.pop(); visit(cur)
        cur = cur.right
```

```java
static List<Integer> inorderIterative(TreeNode root) {
    List<Integer> out = new ArrayList<>();
    Deque<TreeNode> st = new ArrayDeque<>();
    TreeNode cur = root;
    while (cur != null || !st.isEmpty()) {
        while (cur != null) { st.push(cur); cur = cur.left; }   // slide down the left spine
        cur = st.pop();
        out.add(cur.val);
        cur = cur.right;
    }
    return out;
}
```

The stack always holds the nodes whose left subtree is in progress and that haven't been visited yet. This same loop, paused between steps, is the **BST iterator** ([[DSA/04 - Trees and Hierarchical Structures/02 - Binary Search Trees|Binary Search Trees]]).

### 4.3 Postorder

**Shortcut**: preorder with the children swapped (node, right, left) produces exactly the **reverse** of postorder.

```java
static List<Integer> postorderByReversal(TreeNode root) {
    LinkedList<Integer> out = new LinkedList<>();
    if (root == null) return out;
    Deque<TreeNode> st = new ArrayDeque<>();
    st.push(root);
    while (!st.isEmpty()) {
        TreeNode n = st.pop();
        out.addFirst(n.val);                       // prepend: builds the reversed sequence
        if (n.left != null) st.push(n.left);
        if (n.right != null) st.push(n.right);
    }
    return out;
}
```

This gives the right **output**, but nodes are still **processed** parent-first. It can't compute anything that needs the children's results (height, subtree sums) on the fly. For that, use a true postorder with one stack and a pointer to the last visited node:

```
postorderIterative(root):
    cur = root; last = null; stack = []
    while cur ≠ null or stack not empty:
        while cur ≠ null: stack.push(cur); cur = cur.left
        top = stack.peek()
        if top.right ≠ null and top.right ≠ last:  cur = top.right    -- right subtree not done
        else: visit(top); last = stack.pop()
```

```java
static List<Integer> postorderIterative(TreeNode root) {
    List<Integer> out = new ArrayList<>();
    Deque<TreeNode> st = new ArrayDeque<>();
    TreeNode cur = root, last = null;              // last: the most recently visited node
    while (cur != null || !st.isEmpty()) {
        while (cur != null) { st.push(cur); cur = cur.left; }
        TreeNode top = st.peek();
        if (top.right != null && top.right != last) cur = top.right;   // go do the right subtree
        else { out.add(top.val); last = st.pop(); }                    // both subtrees done
    }
    return out;
}
```

The `top.right != last` test is what tells "coming up from the left" apart from "coming up from the right". Without it, the loop descends into the right subtree forever.

### 4.4 Morris traversal: inorder in O(1) space (advanced)

Morris traversal avoids the stack by temporarily **threading** the tree: before descending into a node's left subtree, it points the right pointer of that subtree's rightmost node (the inorder predecessor) back at the node, so it can find its way back up.

```
morrisInorder(root):
    cur = root
    while cur ≠ null:
        if cur.left = null: visit(cur); cur = cur.right
        else:
            pred = rightmost node of cur.left (stop if pred.right = cur)
            if pred.right = null: pred.right = cur; cur = cur.left           -- first time: add thread
            else:                 pred.right = null; visit(cur); cur = cur.right   -- second time: remove it
```

```java
static List<Integer> morrisInorder(TreeNode root) {
    List<Integer> out = new ArrayList<>();
    TreeNode cur = root;
    while (cur != null) {
        if (cur.left == null) {
            out.add(cur.val);
            cur = cur.right;                       // may follow a thread back up
        } else {
            TreeNode pred = cur.left;
            while (pred.right != null && pred.right != cur) pred = pred.right;
            if (pred.right == null) { pred.right = cur; cur = cur.left; }
            else { pred.right = null; out.add(cur.val); cur = cur.right; }
        }
    }
    return out;
}
```

`O(n)` time (each edge is walked a constant number of times) and `O(1)` extra space. The tree is modified during the traversal and restored by the end, so it's unsafe if another thread reads the tree meanwhile, or if the loop can exit early (an early `return` leaves threads behind, and the tree then contains a cycle). Moving `out.add` into the "add thread" branch gives Morris **preorder**.

---

## 5. Level-Order Traversal

Breadth-first search with a queue visits nodes in order of depth. To process one level at a time, record the queue's size at the start of each level:

```
levelOrder(root):
    queue = [root]                      -- if root ≠ null
    while queue not empty:
        size = queue.size()             -- the nodes of exactly one level
        repeat size times:
            n = queue.pop(); visit(n)
            push n.left, n.right        -- skip nulls
        -- end of a level
```

```java
static List<List<Integer>> levelOrder(TreeNode root) {
    List<List<Integer>> levels = new ArrayList<>();
    if (root == null) return levels;
    Deque<TreeNode> q = new ArrayDeque<>();
    q.add(root);
    while (!q.isEmpty()) {
        int size = q.size();                       // snapshot before the loop adds children
        List<Integer> level = new ArrayList<>(size);
        for (int i = 0; i < size; i++) {
            TreeNode n = q.poll();
            level.add(n.val);
            if (n.left != null) q.add(n.left);
            if (n.right != null) q.add(n.right);
        }
        levels.add(level);
    }
    return levels;
}
```

`O(n)` time; the queue holds at most one level plus part of the next, `O(w)` for maximum width `w`, which is up to `n/2` in a perfect tree. DFS uses `O(h)`; for a wide, shallow tree DFS needs less memory, and for a deep, narrow one BFS does.

> [!warning] `i < q.size()` in the loop condition
> The queue grows while the level is processed, so `for (int i = 0; i < q.size(); i++)` keeps going into the next level, and the levels run together. Store the size in a variable first.

### 5.1 Variations

| Problem | Change to the template |
|---|---|
| Bottom-up level order | reverse the list of levels at the end |
| Zigzag order | reverse every second level (or `addFirst` into a `LinkedList`) |
| Right side view | keep the **last** node of each level |
| Level averages / sums | sum each level in a `long` (values near `Integer.MAX_VALUE` overflow) |
| Minimum depth | return at the **first leaf** found: BFS beats DFS here |
| Connect next pointers on each level | link each node to the next one polled in the same level |
| Largest value per level | max over each level |

The right side view also has a DFS form: visit the **right** child first, and record a node when its depth equals the number of values recorded so far (it's the first node seen at that depth).

```java
static void rightView(TreeNode n, int depth, List<Integer> out) {
    if (n == null) return;
    if (depth == out.size()) out.add(n.val);       // first node reached at this depth
    rightView(n.right, depth + 1, out);            // right first
    rightView(n.left, depth + 1, out);
}
```

The running example gives `[1, 3, 6, 7]`: node `7` is a left descendant, but it's the only node at depth 3, so it's visible from the right. Code that only follows right pointers returns `[1, 3, 6]`.

### 5.2 Maximum width (with gaps)

"Width" here counts the positions between the leftmost and rightmost nodes of a level, **including** missing ones. Give nodes heap-style positions (`2p + 1`, `2p + 2`) and measure `last − first + 1` per level.

```java
static int widthOfBinaryTree(TreeNode root) {
    if (root == null) return 0;
    Deque<TreeNode> q = new ArrayDeque<>();
    Deque<Long> pos = new ArrayDeque<>();
    q.add(root); pos.add(0L);
    int best = 0;
    while (!q.isEmpty()) {
        int size = q.size();
        long first = pos.peek(), p = 0;
        for (int i = 0; i < size; i++) {
            TreeNode n = q.poll();
            p = pos.poll() - first;                // re-base each level so positions stay small
            if (n.left != null) { q.add(n.left); pos.add(2 * p + 1); }
            if (n.right != null) { q.add(n.right); pos.add(2 * p + 2); }
        }
        best = Math.max(best, (int) p + 1);        // p is now the last position, first is 0
    }
    return best;
}
```

Without re-basing, positions double on every level, and a tree only 64 levels deep (a zigzag path, say) overflows even a `long`. Re-basing keeps every position below twice the level's width.

---

## 6. Depth, Height, and Balance

### 6.1 Maximum and minimum depth

```java
static int maxDepth(TreeNode n) {                  // in nodes: empty tree = 0
    if (n == null) return 0;
    return 1 + Math.max(maxDepth(n.left), maxDepth(n.right));
}

static int minDepth(TreeNode n) {                  // nodes on the shortest root-to-LEAF path
    if (n == null) return 0;
    if (n.left == null) return 1 + minDepth(n.right);     // a missing child is not a leaf
    if (n.right == null) return 1 + minDepth(n.left);
    return 1 + Math.min(minDepth(n.left), minDepth(n.right));
}
```

> [!warning] Minimum depth is not the mirror of maximum depth
> `1 + min(minDepth(left), minDepth(right))` returns `1` for the tree `1 → left 2`, because the missing right child has depth 0. But the root isn't a leaf; the only root-to-leaf path has 2 nodes. A `null` child must be ignored, not counted as a path of length 0. The max-depth version doesn't have this problem, because `max` never picks the 0.

### 6.2 Checking balance in O(n)

The obvious version compares `height(left)` and `height(right)` at every node, recomputing heights from scratch: `O(n log n)` for balanced trees and `O(n²)` for degenerate ones. Instead, compute height bottom-up and return a sentinel as soon as any subtree is unbalanced:

```
checkHeight(n):                         -- height, or −1 if the subtree is unbalanced
    if n = null: return 0
    l = checkHeight(n.left);  if l = −1: return −1
    r = checkHeight(n.right); if r = −1: return −1
    if |l − r| > 1: return −1
    return 1 + max(l, r)
```

```java
static boolean isBalanced(TreeNode root) { return checkHeight(root) != -1; }

static int checkHeight(TreeNode n) {
    if (n == null) return 0;
    int l = checkHeight(n.left);
    if (l == -1) return -1;                        // stop early: the answer is already known
    int r = checkHeight(n.right);
    if (r == -1) return -1;
    if (Math.abs(l - r) > 1) return -1;
    return 1 + Math.max(l, r);
}
```

> [!warning] Balanced at the root is not enough
> The condition must hold at **every** node. A root whose two subtrees both have height 3 passes the root check even if each subtree is a three-node chain hanging off a single path. Checking only `|height(root.left) − height(root.right)| ≤ 1` accepts such trees.

### 6.3 Counting the nodes of a complete tree in O(log² n)

In a complete tree, if the leftmost and rightmost paths have the same length `h`, the tree is perfect and has `2^h − 1` nodes. Otherwise, recurse: one of the two subtrees is always perfect, so only one recursion goes deep.

```java
static int countNodes(TreeNode root) {
    if (root == null) return 0;
    int lh = 0, rh = 0;
    for (TreeNode n = root; n != null; n = n.left) lh++;
    for (TreeNode n = root; n != null; n = n.right) rh++;
    if (lh == rh) return (1 << lh) - 1;            // perfect: 2^h − 1 nodes
    return 1 + countNodes(root.left) + countNodes(root.right);
}
```

`O(log n)` levels of recursion that each walk `O(log n)` steps: `O(log² n)` instead of `O(n)`. This relies on the tree being complete; on any other tree the shortcut gives wrong counts.

---

## 7. Diameter and Path Problems

### 7.1 Diameter

The <span class="hl-blue">diameter</span> is the number of **edges** on the longest path between any two nodes. Every path has a highest node where it bends; the longest path bending at `n` goes down the deepest branch on each side, with `height(left) + height(right)` edges (heights in nodes). The recursion returns a height, while the answer is a path length, so the best value goes in a separate variable:

```
height(n):                              -- in nodes; also updates best
    if n = null: return 0
    l = height(n.left); r = height(n.right)
    best = max(best, l + r)             -- longest path that bends at n, in edges
    return 1 + max(l, r)
```

```java
static int diameterOfBinaryTree(TreeNode root) {
    int[] best = {0};
    heightForDiameter(root, best);
    return best[0];
}

static int heightForDiameter(TreeNode n, int[] best) {
    if (n == null) return 0;
    int l = heightForDiameter(n.left, best), r = heightForDiameter(n.right, best);
    best[0] = Math.max(best[0], l + r);
    return 1 + Math.max(l, r);
}
```

![[Binary Trees - Diameter Not Through Root.excalidraw|800]]

> [!warning] The diameter doesn't have to pass through the root
> `height(root.left) + height(root.right)` is only the longest path **through the root**. If one subtree of the root is a single leaf and the other contains a large bushy subtree, the longest path lies entirely inside that subtree. The bend point must range over **every** node, which is why `best` is updated at each one.

### 7.2 Maximum path sum

Same shape as the diameter, with values instead of edge counts. The path may start and end anywhere and needn't include the root; values can be negative.

```java
static int maxPathSum(TreeNode root) {
    int[] best = {Integer.MIN_VALUE};              // not 0: every value may be negative
    maxGain(root, best);
    return best[0];
}

static int maxGain(TreeNode n, int[] best) {       // best downward path starting at n
    if (n == null) return 0;
    int l = Math.max(0, maxGain(n.left, best));    // a negative branch is better left out
    int r = Math.max(0, maxGain(n.right, best));
    best[0] = Math.max(best[0], n.val + l + r);    // path bending at n: may use both branches
    return n.val + Math.max(l, r);                 // a path going up can use only one
}
```

`[-10, 9, 20, null, null, 15, 7]` → `42` (`15 + 20 + 7`); `[-3]` → `−3`. Starting `best` at 0 returns 0 for an all-negative tree, which corresponds to the empty path, not allowed here. The value **returned** upward must use at most one branch: a path that continues to the parent can't fork.

### 7.3 Root-to-leaf path sums

```java
static boolean hasPathSum(TreeNode n, int target) {
    if (n == null) return false;
    if (n.left == null && n.right == null) return target == n.val;   // the path must END at a leaf
    return hasPathSum(n.left, target - n.val) || hasPathSum(n.right, target - n.val);
}
```

The leaf check is what makes the problem correct: a version that returns `target == 0` on reaching `null` accepts paths that end at a node with one child, such as the root of `[1, 2]` with target 1 (the root is not a leaf, so the answer is `false`).

To list all such paths, build the path in one shared list and undo each step on the way back (backtracking, [[DSA/06 - Algorithm Design Paradigms/03 - Backtracking|Backtracking]]):

```java
static List<List<Integer>> pathSum(TreeNode root, int target) {
    List<List<Integer>> res = new ArrayList<>();
    collectPaths(root, target, new ArrayList<>(), res);
    return res;
}

static void collectPaths(TreeNode n, int remaining, List<Integer> path, List<List<Integer>> res) {
    if (n == null) return;
    path.add(n.val);
    if (n.left == null && n.right == null && remaining == n.val)
        res.add(new ArrayList<>(path));            // a COPY: path keeps changing afterwards
    else {
        collectPaths(n.left, remaining - n.val, path, res);
        collectPaths(n.right, remaining - n.val, path, res);
    }
    path.remove(path.size() - 1);                  // undo, by INDEX
}
```

> [!warning] `path.remove(n.val)` calls the wrong overload
> `List<Integer>` has `remove(int index)` and `remove(Object o)`. With an `int` argument, Java picks `remove(int index)`: `path.remove(n.val)` removes the element **at position** `n.val`, or throws if that position doesn't exist. Remove by index (`path.size() − 1`), which is also `O(1)`.

### 7.4 Downward paths anywhere: prefix sums on a tree

"Count the downward paths (not necessarily starting at the root or ending at a leaf) whose sum is `target`" is the array problem "subarrays with sum `k`" ([[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays#5. Prefix Sums with Hash Maps|Prefix Sums § 5]]), applied to each root-to-node path. The hash map holds the prefix sums of the **current path** only, so each entry is removed again when the recursion leaves its node.

```java
static int pathSumAnyStart(TreeNode root, int target) {
    Map<Long, Integer> seen = new HashMap<>();
    seen.put(0L, 1);                               // the empty prefix
    return countPaths(root, 0L, target, seen);
}

static int countPaths(TreeNode n, long sum, int target, Map<Long, Integer> seen) {
    if (n == null) return 0;
    sum += n.val;
    int res = seen.getOrDefault(sum - target, 0);  // paths ending at n
    seen.merge(sum, 1, Integer::sum);
    res += countPaths(n.left, sum, target, seen) + countPaths(n.right, sum, target, seen);
    seen.merge(sum, -1, Integer::sum);             // leaving n: its prefix is off the path now
    return res;
}
```

`[10, 5, -3, 3, 2, null, 11, 3, -2, null, 1]`, target 8 → `3`. `O(n)` instead of `O(n · h)` for "start a path at every node". Without the removal step, a prefix from one branch would match a node in a **sibling** branch, counting "paths" that go up and down again. The `long` matters: LeetCode includes a test whose path sums overflow `int`.

---

## 8. Comparing and Transforming Trees

### 8.1 Same tree, symmetric tree

```java
static boolean isSameTree(TreeNode a, TreeNode b) {
    if (a == null || b == null) return a == b;     // both null → true; one null → false
    return a.val == b.val && isSameTree(a.left, b.left) && isSameTree(a.right, b.right);
}

static boolean isSymmetric(TreeNode root) {
    return root == null || isMirror(root.left, root.right);
}

static boolean isMirror(TreeNode a, TreeNode b) {
    if (a == null || b == null) return a == b;
    return a.val == b.val && isMirror(a.left, b.right) && isMirror(a.right, b.left);  // outer and inner pairs
}
```

A tree is symmetric if its left subtree mirrors its right subtree, which compares **outer** with outer and **inner** with inner. Checking that each node's two children are equal isn't the same thing: `[1, 2, 2, 3, 4, 4, 3]` is symmetric, but node `2`'s children `3` and `4` differ.

### 8.2 Invert (mirror) a tree

```java
static TreeNode invertTree(TreeNode n) {
    if (n == null) return null;
    TreeNode oldLeft = n.left;
    n.left = invertTree(n.right);
    n.right = invertTree(oldLeft);                 // NOT invertTree(n.left): n.left was just overwritten
    return n;
}
```

### 8.3 Subtree of another tree

`sub` is a subtree of `root` if some node of `root`, **with all its descendants**, is identical to `sub`.

```java
static boolean isSubtree(TreeNode root, TreeNode sub) {
    if (root == null) return sub == null;
    return isSameTree(root, sub) || isSubtree(root.left, sub) || isSubtree(root.right, sub);
}
```

`O(m · n)` in the worst case. `root = [3, 4, 5, 1, 2, null, null, null, null, 0]`, `sub = [4, 1, 2]` → `false`: the `4` in `root` has the extra descendant `0`.

> [!info]- Linear time: serialize and search
> Serialize both trees in preorder **with null markers and delimiters** ([[#10. Serialization|§10]]) and check whether one string contains the other, using KMP for `O(m + n)` ([[DSA/07 - String Algorithms/01 - String Matching|String Matching]]). Both details are required:
> - Without null markers, different shapes give the same string (`[4, 1]` and `[4, null, 1]` both serialize to `4,1`).
> - Without a delimiter **before** each value, `"2,#,#"` is found inside `"12,#,#"`. Write `,12,#,#` and search for `,2,#,#`.

### 8.4 Merge two trees

Overlapping nodes add up; where only one tree has a node, use it.

```java
static TreeNode mergeTrees(TreeNode a, TreeNode b) {
    if (a == null) return b;                       // reuses b's subtree as-is (shares nodes)
    if (b == null) return a;
    a.val += b.val;
    a.left = mergeTrees(a.left, b.left);
    a.right = mergeTrees(a.right, b.right);
    return a;
}
```

This version modifies `a` and shares subtrees of `b` with the result: changing the result later also changes `b`. Build new nodes throughout if the inputs must stay independent.

### 8.5 Lowest common ancestor

The LCA of `p` and `q` is the deepest node that has both as descendants (a node counts as its own descendant).

```java
static TreeNode lowestCommonAncestor(TreeNode n, TreeNode p, TreeNode q) {
    if (n == null || n == p || n == q) return n;
    TreeNode l = lowestCommonAncestor(n.left, p, q);
    TreeNode r = lowestCommonAncestor(n.right, p, q);
    if (l != null && r != null) return n;          // one found on each side: n is where they split
    return l != null ? l : r;                      // both on one side (or neither)
}
```

Each call returns `p`, `q`, their LCA, or `null`. Two consequences:
- If `p` is an ancestor of `q`, the search stops at `p` and never looks for `q`. That's correct, because `p` is then the LCA.
- The code **assumes both nodes are in the tree**. If `q` is missing, it returns `p` instead of `null`. When existence isn't guaranteed, count how many of the two were actually found.

For a BST there's a simpler `O(h)` walk ([[DSA/04 - Trees and Hierarchical Structures/02 - Binary Search Trees|Binary Search Trees]]); for many LCA queries on one tree, binary lifting answers each in `O(log n)` ([[DSA/05 - Graphs/07 - Lowest Common Ancestor|Lowest Common Ancestor]]).

### 8.6 Flatten to a linked list in preorder

Rearrange the tree so each node's `right` pointer leads to the next node in preorder and every `left` is `null`, in place.

```java
static void flatten(TreeNode root) {
    for (TreeNode cur = root; cur != null; cur = cur.right) {
        if (cur.left != null) {
            TreeNode tail = cur.left;
            while (tail.right != null) tail = tail.right;   // last node of the left part, in preorder
            tail.right = cur.right;                         // left part, then the old right part
            cur.right = cur.left;
            cur.left = null;                                // otherwise the result isn't a list
        }
    }
}
```

`O(n)` time overall (each node is passed by a `tail` walk at most once), `O(1)` space. The running example becomes `1 → 2 → 4 → 5 → 7 → 3 → 6`.

---

## 9. Building a Tree from Traversals

One traversal isn't enough to determine a tree: `[1, 2]` is the preorder of both "2 is the left child" and "2 is the right child". **Inorder plus preorder** (or plus postorder) is enough when values are **distinct**:

- Preorder's first value is the root.
- That value's position in the inorder sequence splits it: everything before it is the left subtree, everything after is the right subtree.
- Preorder lists the whole left subtree right after the root, then the right subtree, so recursing **left first** consumes the preorder values in order.

```
build(lo, hi):                          -- builds the subtree whose inorder range is in[lo..hi]
    if lo > hi: return null
    val = pre[next]; next = next + 1
    m = position of val in the inorder array
    node = new node(val)
    node.left = build(lo, m − 1)
    node.right = build(m + 1, hi)
    return node
```

```java
static TreeNode buildTree(int[] pre, int[] in) {
    Map<Integer, Integer> pos = new HashMap<>();
    for (int i = 0; i < in.length; i++) pos.put(in[i], i);   // O(1) lookups; values distinct
    return buildPreIn(pre, new int[]{0}, 0, in.length - 1, pos);
}

static TreeNode buildPreIn(int[] pre, int[] next, int lo, int hi, Map<Integer, Integer> pos) {
    if (lo > hi) return null;
    int val = pre[next[0]++];
    int m = pos.get(val);
    TreeNode n = new TreeNode(val);
    n.left = buildPreIn(pre, next, lo, m - 1, pos);    // left first: matches preorder
    n.right = buildPreIn(pre, next, m + 1, hi, pos);
    return n;
}
```

![[Binary Trees - Build from Preorder and Inorder.excalidraw|800]]

`O(n)` with the position map; searching the inorder array for each root instead costs `O(n²)` on a degenerate tree. The `int[] next` is a shared counter: a plain `int` parameter would be copied into each call, and the right subtree would restart reading preorder from the wrong place.

**Inorder plus postorder**: read the postorder **backwards** (root, right, left), so build the **right** subtree first.

```java
static TreeNode buildFromPostIn(int[] in, int[] post) {
    Map<Integer, Integer> pos = new HashMap<>();
    for (int i = 0; i < in.length; i++) pos.put(in[i], i);
    return buildPostIn(post, new int[]{post.length - 1}, 0, in.length - 1, pos);
}

static TreeNode buildPostIn(int[] post, int[] next, int lo, int hi, Map<Integer, Integer> pos) {
    if (lo > hi) return null;
    int val = post[next[0]--];
    int m = pos.get(val);
    TreeNode n = new TreeNode(val);
    n.right = buildPostIn(post, next, m + 1, hi, pos);   // RIGHT first
    n.left = buildPostIn(post, next, lo, m - 1, pos);
    return n;
}
```

| Traversals given | Unique tree? |
|---|---|
| Inorder + preorder | yes (distinct values) |
| Inorder + postorder | yes (distinct values) |
| Inorder + level order | yes (distinct values) |
| Preorder + postorder | **no**: a node with one child could have it on either side. Unique only for **full** trees |
| Preorder alone, of a BST | yes: the inorder is the sorted order ([[DSA/04 - Trees and Hierarchical Structures/02 - Binary Search Trees|Binary Search Trees]]) |
| Preorder with null markers | yes: that's serialization ([[#10. Serialization|§10]]) |
| Any pair, with repeated values | not in general: `pre = [1, 1]`, `in = [1, 1]` fits two trees |

> [!example]- Preorder + postorder for a full tree
> In a full tree, the node after the root in preorder is the left child, `L`. In postorder, the left subtree ends at `L`, which gives the left subtree's size.
> ```java
> static TreeNode buildPrePost(int[] pre, int[] post) {
>     Map<Integer, Integer> postPos = new HashMap<>();
>     for (int i = 0; i < post.length; i++) postPos.put(post[i], i);
>     return buildPP(pre, 0, pre.length - 1, 0, postPos);
> }
>
> static TreeNode buildPP(int[] pre, int a, int b, int c, Map<Integer, Integer> postPos) {
>     // pre[a..b] is a subtree whose postorder starts at index c
>     if (a > b) return null;
>     TreeNode n = new TreeNode(pre[a]);
>     if (a == b) return n;
>     int leftRoot = pre[a + 1];
>     int leftSize = postPos.get(leftRoot) - c + 1;   // the left subtree ends at its root in postorder
>     n.left = buildPP(pre, a + 1, a + leftSize, c, postPos);
>     n.right = buildPP(pre, a + leftSize + 1, b, c + leftSize, postPos);
>     return n;
> }
> ```
> `pre = [1, 2, 4, 5, 3, 6, 7]`, `post = [4, 5, 2, 6, 7, 3, 1]` → the perfect tree `[1, 2, 3, 4, 5, 6, 7]`. For a non-full tree this returns **one** of the valid trees (it always makes a lone child the left child).

---

## 10. Serialization

To store a tree as a string and rebuild it exactly, write the preorder sequence **with a marker for every `null`**. The markers fix the shape, so one traversal is enough.

```
serialize(n):
    if n = null: write "#"; return
    write n.val; serialize(n.left); serialize(n.right)

deserialize(tokens):
    t = next token
    if t = "#": return null
    n = node(t); n.left = deserialize(tokens); n.right = deserialize(tokens)
    return n
```

```java
static String serialize(TreeNode root) {
    StringBuilder sb = new StringBuilder();
    serialize(root, sb);
    return sb.toString();
}

static void serialize(TreeNode n, StringBuilder sb) {
    if (n == null) { sb.append("#,"); return; }
    sb.append(n.val).append(',');                  // delimiter: values have several digits or a sign
    serialize(n.left, sb);
    serialize(n.right, sb);
}

static TreeNode deserialize(String data) {
    Deque<String> tokens = new ArrayDeque<>(Arrays.asList(data.split(",")));
    return deserialize(tokens);
}

static TreeNode deserialize(Deque<String> tokens) {
    String t = tokens.poll();
    if (t.equals("#")) return null;
    TreeNode n = new TreeNode(Integer.parseInt(t));
    n.left = deserialize(tokens);
    n.right = deserialize(tokens);
    return n;
}
```

The running example serializes to `1,2,4,#,#,5,7,#,#,#,3,#,6,#,#,`. A tree of `n` nodes produces `n` values and `n + 1` markers (the `n + 1` null pointers of [[#1.2 Counting facts|§1.2]]). `split(",")` drops the trailing empty string, so the final comma is harmless; the empty tree is `"#,"`.

Level-order serialization (LeetCode's own format, [[#2.3 LeetCode's level-order format|§2.3]]) works too, and is easier to read for wide trees. Both are `O(n)`.

> [!tip] Compact variants
> For a **BST**, the preorder without markers is enough, because the inorder (sorted order) is implied. For a tree with a known shape (complete trees), the level-order values without markers are enough.

---

## 11. Trees as Graphs

A `TreeNode` only points down. Problems that move **upward or sideways**, such as "all nodes at distance `k` from a target" or "time for an infection starting at a node to spread to the whole tree", treat the tree as an undirected graph: record each node's parent, then run BFS from the start node ([[DSA/05 - Graphs/01 - Graph Representations and Traversals|Graph Representations and Traversals]]).

```java
static List<Integer> distanceK(TreeNode root, TreeNode target, int k) {
    Map<TreeNode, TreeNode> parent = new HashMap<>();
    Deque<TreeNode> st = new ArrayDeque<>();
    st.push(root);
    while (!st.isEmpty()) {                        // record parents (any traversal order works)
        TreeNode n = st.pop();
        if (n.left != null) { parent.put(n.left, n); st.push(n.left); }
        if (n.right != null) { parent.put(n.right, n); st.push(n.right); }
    }
    Set<TreeNode> seen = new HashSet<>();
    Deque<TreeNode> q = new ArrayDeque<>();
    q.add(target); seen.add(target);
    for (int d = 0; d < k && !q.isEmpty(); d++) {
        for (int size = q.size(); size > 0; size--) {
            TreeNode n = q.poll();
            for (TreeNode m : new TreeNode[]{n.left, n.right, parent.get(n)})
                if (m != null && seen.add(m)) q.add(m);    // seen: never walk back the way you came
        }
    }
    List<Integer> res = new ArrayList<>();
    for (TreeNode n : q) res.add(n.val);
    return res;
}
```

On the running example, distance 1 from node `5` gives `[7, 2]` and distance 2 gives `[4, 1]`, both reached through the parent `2`. The `seen` set matters: with parent links, the graph has edges in both directions, so BFS would otherwise bounce between a node and its parent.

The maps are keyed by `TreeNode` **identity** (`TreeNode` doesn't override `equals`/`hashCode`), so duplicate values are fine. A map keyed by `val` breaks as soon as two nodes share a value.

---

## 12. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Mixing the node and edge height conventions | off-by-one diameter or height | fix one convention per function; diameter counts edges |
| `minDepth` as `1 + min(left, right)` | `1` for a root with one child | ignore `null` children |
| Checking balance only at the root | unbalanced trees accepted | check at every node, bottom-up |
| Recomputing heights at every node | `O(n²)` on degenerate trees | return height and balance together |
| Diameter as `height(left) + height(right)` at the root only | misses paths in one subtree | update a best value at every node |
| `best = 0` in max path sum | `0` for an all-negative tree | start at `Integer.MIN_VALUE` |
| Path sum "ends" at `null` | paths ending at a one-child node accepted | test for a leaf |
| Adding `path` itself (not a copy) to the results | every result list ends up empty | `new ArrayList<>(path)` |
| `path.remove(n.val)` | wrong element removed, or exception | `path.remove(path.size() − 1)` |
| Prefix-sum map not cleaned up on return | paths across sibling branches counted | `merge(sum, −1)` after the children |
| `i < q.size()` as the level loop condition | levels merge | snapshot `size` first |
| Pushing `null` into an `ArrayDeque` | `NullPointerException` | check children before pushing |
| `invertTree`: overwrite `left`, then use it | right subtree becomes a copy of the left | save the old left first |
| Plain `int` index while building from traversals | wrong tree | shared counter (`int[]` or a field) |
| Building from postorder+inorder left subtree first | wrong tree | right first when reading postorder backwards |
| Serializing without null markers or delimiters | shapes or values can't be recovered | `#` markers and `,` after every token |
| Recursion on a `10⁵`-node degenerate tree | `StackOverflowError` | iterative traversal, or a bigger thread stack |
| LCA when a node may be absent | returns the other node instead of `null` | count both nodes found |
| Heap-style indices on LeetCode arrays | wrong tree | queue-based builder |

---

## 13. Trick Questions and Special Cases

> [!question]- A tree has 10 leaves and 4 nodes with exactly one child. How many nodes does it have?
> `23`. With `n₀ = n₂ + 1`, there are `9` two-child nodes, so `10 + 4 + 9 = 23`. The one-child nodes don't affect the leaf count at all.

> [!question]- What's the height of the empty tree? Of a single node?
> In edges: `−1` and `0`. In nodes (LeetCode's "maximum depth"): `0` and `1`. Neither is wrong; the bug is mixing them, such as computing a diameter from node-heights and then subtracting one more.

> [!question]- Is every complete tree full? Every full tree complete?
> Neither. `[1, 2, 3, 4]` is complete (last level filled from the left) but not full (node `2` has one child). A root whose right child has two leaf children, while its left child is a leaf, is full but not complete (the last level isn't filled from the left).

> [!question]- Preorder `[1, 2]`, postorder `[2, 1]`: which tree?
> Either `1 → left 2` or `1 → right 2`. Preorder and postorder can't tell which side a single child is on. With inorder `[2, 1]` it's the left child; with `[1, 2]`, the right child.

> [!question]- Right side view of the running example?
> `[1, 3, 6, 7]`. Node `7` is in the **left** subtree, but nothing else is at depth 3, so it's visible from the right. Following only right pointers gives `[1, 3, 6]`.

> [!question]- Minimum depth of `[1, 2]` (root with only a left child)?
> `2`. The root isn't a leaf, so the only root-to-leaf path is `1 → 2`. The naive `1 + min(…)` returns `1`.

> [!question]- Maximum path sum of `[-3]`? Of `[2, -1]`?
> `−3` (the path must contain at least one node). `2` for the second: the best path is the root alone, and the `max(0, gain)` clamp correctly drops the `−1` branch.

> [!question]- Diameter of a tree with a single node? With two nodes?
> `0` and `1`: the diameter counts **edges**. Reporting the number of nodes on the path gives `1` and `2`.

> [!question]- Does `hasPathSum(null, 0)` return true?
> No. There's no root-to-leaf path in an empty tree, so no path sums to 0. A version that returns `target == 0` at `null` says `true`.

> [!question]- Sum of left leaves of `[3, 9, 20, null, null, 15, 7]`?
> `24` (`9 + 15`). A "left leaf" must be both a left child and a leaf: `7` is a leaf but a right child, and `20` is neither. A single-node tree has sum 0: the root is a leaf, but not a left child. Summing all **left children** instead (leaf or not) is the usual misreading.

> [!question]- Is `[1, 2, 2, null, 3, null, 3]` symmetric?
> No. The values match level by level (`2, 2` then `3, 3`), but both `3`s are **right** children. The mirror of the left `2`'s right child would be the right `2`'s **left** child. Comparing levels as lists, ignoring nulls, wrongly says yes.

> [!question]- Is `[4, 1, 2]` a subtree of `[3, 4, 5, 1, 2, null, null, null, null, 0]`?
> No. The `4` in the big tree has the extra descendant `0`, and a subtree must include **all** descendants. A "contains a matching top part" check says yes.

> [!question]- Serialized string `"2,#,#,"` is found inside `"12,#,#,"`. Does that make tree `2` a subtree of tree `12`?
> No: it's a false match from string search. Put a delimiter before every value too (`",2,#,#"` vs `",12,#,#"`), so a match can only start at a token boundary.

> [!question]- Which traversal deletes a tree safely when deallocation is manual (C/C++)?
> Postorder: a node is freed only after both subtrees. Freeing in preorder loses the pointers to the children. (Java's garbage collector makes `root = null` enough.)

> [!question]- What does the LCA function return for `p = 5`, `q = 7` in the running example?
> Node `5`: it's an ancestor of `7`, and a node is its own ancestor. The function stops at `5` without searching below it, which is fine because the answer is already known.

> [!question]- The `width` of `[1, 3, 2, 5, null, null, 9, 6, null, 7]`?
> `7`, on the last level: `6` is at position 0 and `7` at position 6, and the 5 positions between them count even though they're empty. Counting only the nodes present gives `2`.

> [!question]- Morris traversal: what happens if the loop `return`s as soon as it finds the target?
> The tree is left with threads in it: some `right` pointers point back up to an ancestor, so the tree now contains cycles. Any later traversal loops forever. Morris traversal must run to completion, or the threads must be removed.

---

## 14. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| Edges in a tree of `n` nodes | `n − 1` | one parent edge per non-root |
| `null` children | `n + 1` | `2n − (n − 1)` |
| Leaves in terms of two-child nodes | `n₂ + 1` | one-child nodes don't matter |
| Nodes of a perfect tree of height `h` (edges) | `2^(h+1) − 1` | |
| Shapes with 3 nodes | `5` | Catalan |
| Preorder / inorder / postorder of the example | `1 2 4 5 7 3 6` / `4 2 7 5 1 3 6` / `4 7 5 2 6 3 1` | |
| Postorder from swapped preorder | reversed | node, right, left → left, right, node |
| Right side view of the example | `[1, 3, 6, 7]` | the left-subtree `7` is visible |
| `minDepth([1, 2])` | `2` | the root isn't a leaf |
| `maxPathSum([-3])` | `−3` | best starts at `MIN_VALUE` |
| Diameter of a single node | `0` | edges |
| `hasPathSum([1, 2], 1)` | `false` | the root isn't a leaf |
| `path.remove(n.val)` on `List<Integer>` | removes by index | overload resolution |
| Pre + post order | not unique | one-child side is unknown |
| Serialized size | `n` values + `n + 1` markers | |
| BFS queue memory | `O(width)` | up to `n/2` |
| DFS stack memory | `O(height)` | up to `n` |
| Morris traversal space | `O(1)` | threads in null pointers |
| Count nodes of a complete tree | `O(log² n)` | one side is always perfect |

---

## 15. Summary

- A binary tree has `n − 1` edges and `n + 1` null pointers. Know which **height convention** a problem uses (edges vs. nodes) and stick to it.
- **Full**, **complete**, **perfect**, **balanced**, and **degenerate** are different shapes; only complete trees fit in an array without gaps.
- **Traversals**: preorder (copy, serialize, pass information down), inorder (BST order), postorder (combine children's results), level order (anything by depth). Iterative versions use a stack (DFS) or a queue (BFS); Morris traversal uses `O(1)` space by threading.
- Most problems are **bottom-up recursion**: decide what a subtree call returns, combine at the node, and keep the global answer separately when it differs (diameter, max path sum).
- **Path problems**: root-to-leaf paths must check for a leaf; downward paths anywhere use prefix sums with an undo step; listing paths needs copies and removal by index.
- **Inorder + preorder/postorder** rebuild a tree with distinct values; preorder + postorder doesn't. **Preorder with null markers** serializes a tree on its own.
- For upward or sideways movement, add parent links and treat the tree as a graph.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]] · Next: [[DSA/04 - Trees and Hierarchical Structures/02 - Binary Search Trees|Binary Search Trees]]
- [[DSA/01 - Foundations/02 - Recursion|Recursion]]: the call stack, converting recursion to iteration, stack limits
- [[DSA/02 - Linear Data Structures/04 - Stacks|Stacks]] and [[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]]: the structures behind DFS and BFS
- [[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]]: the array version of downward path sums
- [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|Heaps and Priority Queues]]: complete trees stored in arrays
- [[DSA/05 - Graphs/01 - Graph Representations and Traversals|Graph Representations and Traversals]]: BFS and DFS on general graphs
- [[DSA/05 - Graphs/07 - Lowest Common Ancestor|Lowest Common Ancestor]]: many LCA queries on one tree
- [[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]]: tree DP (house robber III, tree diameter in general trees)
