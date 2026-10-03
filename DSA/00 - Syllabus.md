# Data Structures and Algorithms — Syllabus

This note is the index for the `DSA/` folder. Each chapter below is (or will become) its own note, ordered roughly in the sequence it should be studied.

**Scope:** this syllabus aims to cover every algorithm and data structure that appears in competitive programming and interview problem sets (LeetCode, Codeforces, and similar). Chapter descriptions name the specific algorithms covered, so this page can be scanned to check whether a given technique has a home. Topics that are contest-specific or rarely needed below the highest difficulty tiers are marked *(advanced)*.

**Format:** per vault convention, each chapter states an algorithm in pseudocode first, then gives a working Java implementation.

Checkboxes track progress: checked means the note exists and is written; unchecked means the chapter is planned but not yet created. Clicking an unchecked link in Obsidian will create the note.

---

## Part I — Foundations

- [x] [[01 - Complexity Analysis|Complexity Analysis]] — Big-O, Big-Θ, Big-Ω, amortized analysis, space complexity, recurrence relations, complexity of common operations
- [x] [[02 - Recursion|Recursion]] — base cases, the call stack, recursion trees, tail recursion, converting recursion to iteration, stack overflow limits
- [x] [[03 - Bit Manipulation|Bit Manipulation]] — bitwise operators, common tricks (clear/set/toggle, lowest set bit, power-of-two checks), bitmasks, `popcount`, XOR properties
- [x] [[Math for Algorithms|Math for Algorithms]] — GCD/LCM and Euclid's algorithm, modular arithmetic, fast (binary) exponentiation, modular inverse, Sieve of Eratosthenes, prime factorization, combinatorics (nCr, Pascal's triangle), Euler's totient, CRT *(advanced)*

---

## Part II — Linear Data Structures

- [x] [[Arrays|Arrays]] — static vs. dynamic arrays, amortized resizing, in-place operations, rotation, 2D arrays
- [x] [[Strings|Strings]] — immutability, `StringBuilder`, character frequency counting, anagram/palindrome basics, common string manipulation patterns
- [x] [[Linked Lists|Linked Lists]] — singly, doubly, and circular lists; reversal; fast/slow pointers (cycle detection, middle node); merging
- [x] [[Stacks|Stacks]] — LIFO operations, expression evaluation, parentheses matching, monotonic stack (next greater/smaller element, largest rectangle in histogram)
- [x] [[Queues and Deques|Queues and Deques]] — FIFO operations, circular buffers, monotonic deque (sliding window maximum)
- [x] [[Hash Tables|Hash Tables]] — hash functions, collision resolution (chaining, open addressing), load factor, `HashMap`/`HashSet` in Java, hashing custom objects, anti-hash tests *(advanced)*

---

## Part III — Sorting and Searching

- [ ] [[DSA/Sorting Algorithms|Sorting Algorithms]] — bubble, selection, insertion, merge, quick, heap sort; counting, radix, bucket sort; stability; Java's `Arrays.sort`/`Collections.sort` and custom comparators
- [ ] [[DSA/Binary Search|Binary Search]] — classic search, lower/upper bound, boundary variants, binary search on the answer, search in rotated/2D arrays, ternary search *(advanced)*
- [ ] [[DSA/Two Pointers|Two Pointers]] — opposite-end and same-direction pointers, pair/triplet sums, partitioning, in-place deduplication
- [ ] [[DSA/Sliding Window|Sliding Window]] — fixed and variable-size windows, longest/shortest subarray patterns, window with constraints
- [ ] [[DSA/Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]] — 1D/2D prefix sums, range sum queries, difference arrays for range updates, subarray-sum-equals-k with hashing

---

## Part IV — Trees and Hierarchical Structures

- [ ] [[DSA/Binary Trees|Binary Trees]] — terminology, recursive and iterative traversals (preorder, inorder, postorder, level-order), depth/height, diameter, tree construction from traversals, serialization
- [ ] [[DSA/Binary Search Trees|Binary Search Trees]] — insert/search/delete, validation, successor/predecessor, k-th smallest, BST to sorted structures
- [ ] [[DSA/Balanced Trees|Balanced Trees]] — rotations, AVL trees, red-black trees, treaps; Java's `TreeMap`/`TreeSet` as the practical substitute *(advanced)*
- [ ] [[DSA/Heaps and Priority Queues|Heaps and Priority Queues]] — binary heap structure, heapify, insert/extract, `PriorityQueue` in Java, top-k problems, two-heap median, heap sort connection
- [ ] [[DSA/Tries|Tries]] — prefix tree insert/search, prefix matching, autocomplete, bitwise trie for maximum XOR
- [ ] [[DSA/Union-Find|Union-Find (Disjoint Set Union)]] — union by rank/size, path compression, connected components, cycle detection, DSU on edges; rollback/persistent DSU *(advanced)*
- [ ] [[DSA/Segment Trees|Segment Trees]] — range queries and point updates, lazy propagation for range updates, iterative implementation, merge-sort tree *(advanced)*
- [ ] [[DSA/Fenwick Trees|Fenwick Trees (Binary Indexed Trees)]] — point update/prefix query, range update variants, 2D BIT, counting inversions *(advanced)*
- [ ] [[DSA/Sqrt Decomposition|Sqrt Decomposition and Mo's Algorithm]] — block decomposition for range queries, offline query reordering *(advanced)*

---

## Part V — Graphs

- [ ] [[DSA/Graph Representations and Traversals|Graph Representations and Traversals]] — adjacency list vs. matrix vs. edge list, directed/undirected/weighted graphs, BFS, DFS, connected components, grid graphs, flood fill, multi-source BFS
- [ ] [[DSA/Topological Sorting|Topological Sorting]] — Kahn's algorithm, DFS-based ordering, cycle detection in directed graphs, course-schedule patterns, longest path in a DAG
- [ ] [[DSA/Shortest Path Algorithms|Shortest Path Algorithms]] — BFS for unweighted graphs, 0-1 BFS, Dijkstra (with priority queue), Bellman-Ford and negative cycles, Floyd-Warshall, SPFA, path reconstruction
- [ ] [[DSA/Minimum Spanning Trees|Minimum Spanning Trees]] — Kruskal (with DSU), Prim (with priority queue), properties of MSTs, second-best MST *(advanced)*
- [ ] [[DSA/Graph Connectivity|Graph Connectivity]] — strongly connected components (Tarjan, Kosaraju), bridges and articulation points, biconnected components, condensation graphs *(advanced)*
- [ ] [[DSA/Bipartite Graphs and Matching|Bipartite Graphs and Matching]] — 2-coloring / bipartiteness checking, maximum bipartite matching (Kuhn's), König's theorem *(advanced)*
- [ ] [[DSA/Lowest Common Ancestor|Lowest Common Ancestor]] — binary lifting, Euler tour with sparse table, distance queries on trees *(advanced)*
- [ ] [[DSA/Network Flow|Network Flow]] — Ford-Fulkerson, Edmonds-Karp, Dinic's algorithm, max-flow min-cut theorem, flow modelling patterns *(advanced)*
- [ ] [[DSA/Heavy-Light Decomposition|Heavy-Light Decomposition]] — path queries on trees, combining with segment trees *(advanced)*

---

## Part VI — Algorithm Design Paradigms

- [ ] [[DSA/Greedy Algorithms|Greedy Algorithms]] — greedy-choice property, exchange arguments, interval scheduling, activity selection, Huffman coding, when greedy fails
- [ ] [[DSA/Divide and Conquer|Divide and Conquer]] — the master theorem, merge-sort-style recursion, quickselect, closest pair of points, counting inversions
- [ ] [[DSA/Backtracking|Backtracking]] — permutations, combinations, subsets, N-queens, sudoku solver, word search, pruning strategies, constraint propagation
- [ ] [[DSA/Dynamic Programming Fundamentals|Dynamic Programming — Fundamentals]] — optimal substructure and overlapping subproblems, memoization vs. tabulation, state design, transition derivation, space optimization
- [ ] [[DSA/Classic DP Problems|Classic DP Problems]] — 0/1 and unbounded knapsack, coin change, longest increasing subsequence (O(n log n) variant included), longest common subsequence, edit distance, matrix chain multiplication, partition problems, grid path DP
- [ ] [[DSA/Advanced DP|Advanced DP]] — bitmask DP, tree DP, interval DP, digit DP, DP on subsets, convex hull trick and divide-and-conquer DP optimizations *(advanced)*
- [ ] [[DSA/Meet in the Middle|Meet in the Middle]] — splitting exponential search spaces, subset-sum applications *(advanced)*

---

## Part VII — String Algorithms

- [ ] [[DSA/String Matching|String Matching]] — naive matching, KMP and the failure function, Z-algorithm, Rabin-Karp rolling hash, Aho-Corasick for multiple patterns *(advanced)*
- [ ] [[DSA/String Hashing|String Hashing]] — polynomial hashing, prefix hashes for O(1) substring comparison, double hashing and collision avoidance
- [ ] [[DSA/Palindromes|Palindromes]] — expand-around-center, palindromic DP, Manacher's algorithm, palindromic substring counting
- [ ] [[DSA/Suffix Structures|Suffix Structures]] — suffix arrays, LCP arrays (Kasai's), suffix automaton, suffix trees *(advanced)*

---

## Part VIII — Specialized Topics

- [ ] [[DSA/Intervals and Sweep Line|Intervals and Sweep Line]] — merging/inserting intervals, event-based sweeping, meeting rooms, skyline problem, coordinate compression
- [ ] [[DSA/Computational Geometry|Computational Geometry]] — points and vectors, cross/dot products, orientation tests, line and segment intersection, convex hull (Graham scan, Andrew's monotone chain), polygon area, closest pair *(advanced)*
- [ ] [[DSA/Game Theory|Game Theory]] — impartial games, Nim, Grundy numbers and the Sprague-Grundy theorem, minimax with alpha-beta pruning *(advanced)*
- [ ] [[DSA/Matrix Exponentiation|Matrix Exponentiation]] — representing linear recurrences as matrices, fast exponentiation of matrices, Fibonacci in O(log n) *(advanced)*
- [ ] [[DSA/Randomized Algorithms|Randomized Algorithms]] — randomized quickselect, reservoir sampling, shuffling (Fisher-Yates), probabilistic guarantees *(advanced)*

---

## Part IX — Practice

- [ ] [[DSA/Problem-Solving Patterns|Problem-Solving Patterns]] — catalogue mapping common problem signatures to the technique that solves them, and how to recognise which applies
- [ ] [[DSA/Competitive Programming Toolkit|Competitive Programming Toolkit]] — fast I/O in Java, integer overflow and `long` discipline, time/memory limits, template setup, common contest pitfalls

---

## Notes

- Order within each part is the intended reading order; Parts I–VI are broadly sequential, while Parts VII–IX can be taken as needed.
- Topics marked *(advanced)* are contest-oriented and can be safely deferred until the surrounding fundamentals are solid.
- This syllabus will be updated as chapters are added, split, or reordered.
