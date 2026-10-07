# Data Structures and Algorithms — Syllabus

This note is the index for the `DSA/` folder. Each chapter below is (or will become) its own note, ordered roughly in the sequence it should be studied.

**Scope:** this syllabus aims to cover every algorithm and data structure that appears in competitive programming and interview problem sets (LeetCode, Codeforces, and similar). Chapter descriptions name the specific algorithms covered, so this page can be scanned to check whether a given technique has a home. Topics that are contest-specific or rarely needed below the highest difficulty tiers are marked *(advanced)*.

**Format:** per vault convention, each chapter states an algorithm in pseudocode first, then gives a working Java implementation.

Checkboxes track progress: checked means the note exists and is written; unchecked means the chapter is planned but not yet created. Clicking an unchecked link in Obsidian will create the note.

---

## Part I — Foundations

- [x] [[DSA/01 - Foundations/01 - Complexity Analysis|Complexity Analysis]] — Big-O, Big-Θ, Big-Ω, amortized analysis, space complexity, recurrence relations, complexity of common operations
- [x] [[DSA/01 - Foundations/02 - Recursion|Recursion]] — base cases, the call stack, recursion trees, tail recursion, converting recursion to iteration, stack overflow limits
- [x] [[DSA/01 - Foundations/03 - Bit Manipulation|Bit Manipulation]] — bitwise operators, common tricks (clear/set/toggle, lowest set bit, power-of-two checks), bitmasks, `popcount`, XOR properties
- [x] [[DSA/01 - Foundations/04 - Math for Algorithms|Math for Algorithms]] — GCD/LCM and Euclid's algorithm, modular arithmetic, fast (binary) exponentiation, modular inverse, Sieve of Eratosthenes, prime factorization, combinatorics (nCr, Pascal's triangle), Euler's totient, CRT *(advanced)*

---

## Part II — Linear Data Structures

- [x] [[DSA/02 - Linear Data Structures/01 - Arrays|Arrays]] — static vs. dynamic arrays, amortized resizing, in-place operations, rotation, 2D arrays
- [x] [[DSA/02 - Linear Data Structures/02 - Strings|Strings]] — immutability, `StringBuilder`, character frequency counting, anagram/palindrome basics, common string manipulation patterns
- [x] [[DSA/02 - Linear Data Structures/03 - Linked Lists|Linked Lists]] — singly, doubly, and circular lists; reversal; fast/slow pointers (cycle detection, middle node); merging
- [x] [[DSA/02 - Linear Data Structures/04 - Stacks|Stacks]] — LIFO operations, expression evaluation, parentheses matching, monotonic stack (next greater/smaller element, largest rectangle in histogram)
- [x] [[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]] — FIFO operations, circular buffers, monotonic deque (sliding window maximum)
- [x] [[DSA/02 - Linear Data Structures/06 - Hash Tables|Hash Tables]] — hash functions, collision resolution (chaining, open addressing), load factor, `HashMap`/`HashSet` in Java, hashing custom objects, anti-hash tests *(advanced)*

---

## Part III — Sorting and Searching

- [x] [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms|Sorting Algorithms]] — bubble, selection, insertion, merge, quick, heap sort; counting, radix, bucket sort; stability; Java's `Arrays.sort`/`Collections.sort` and custom comparators
- [x] [[DSA/03 - Sorting and Searching/02 - Binary Search|Binary Search]] — classic search, lower/upper bound, boundary variants, binary search on the answer, search in rotated/2D arrays, ternary search *(advanced)*
- [x] [[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]] — opposite-end and same-direction pointers, pair/triplet sums, partitioning, in-place deduplication
- [x] [[DSA/03 - Sorting and Searching/04 - Sliding Window|Sliding Window]] — fixed and variable-size windows, longest/shortest subarray patterns, window with constraints
- [x] [[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]] — 1D/2D prefix sums, range sum queries, difference arrays for range updates, subarray-sum-equals-k with hashing

---

## Part IV — Trees and Hierarchical Structures

- [ ] [[DSA/04 - Trees and Hierarchical Structures/01 - Binary Trees|Binary Trees]] — terminology, recursive and iterative traversals (preorder, inorder, postorder, level-order), depth/height, diameter, tree construction from traversals, serialization
- [ ] [[DSA/04 - Trees and Hierarchical Structures/02 - Binary Search Trees|Binary Search Trees]] — insert/search/delete, validation, successor/predecessor, k-th smallest, BST to sorted structures
- [ ] [[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]] — rotations, AVL trees, red-black trees, treaps; Java's `TreeMap`/`TreeSet` as the practical substitute *(advanced)*
- [ ] [[DSA/04 - Trees and Hierarchical Structures/04 - Heaps and Priority Queues|Heaps and Priority Queues]] — binary heap structure, heapify, insert/extract, `PriorityQueue` in Java, top-k problems, two-heap median, heap sort connection
- [ ] [[DSA/04 - Trees and Hierarchical Structures/05 - Tries|Tries]] — prefix tree insert/search, prefix matching, autocomplete, bitwise trie for maximum XOR
- [ ] [[DSA/04 - Trees and Hierarchical Structures/06 - Union-Find|Union-Find (Disjoint Set Union)]] — union by rank/size, path compression, connected components, cycle detection, DSU on edges; rollback/persistent DSU *(advanced)*
- [ ] [[DSA/04 - Trees and Hierarchical Structures/07 - Segment Trees|Segment Trees]] — range queries and point updates, lazy propagation for range updates, iterative implementation, merge-sort tree *(advanced)*
- [ ] [[DSA/04 - Trees and Hierarchical Structures/08 - Fenwick Trees|Fenwick Trees (Binary Indexed Trees)]] — point update/prefix query, range update variants, 2D BIT, counting inversions *(advanced)*
- [ ] [[DSA/04 - Trees and Hierarchical Structures/09 - Sqrt Decomposition|Sqrt Decomposition and Mo's Algorithm]] — block decomposition for range queries, offline query reordering *(advanced)*

---

## Part V — Graphs

- [ ] [[DSA/05 - Graphs/01 - Graph Representations and Traversals|Graph Representations and Traversals]] — adjacency list vs. matrix vs. edge list, directed/undirected/weighted graphs, BFS, DFS, connected components, grid graphs, flood fill, multi-source BFS
- [ ] [[DSA/05 - Graphs/02 - Topological Sorting|Topological Sorting]] — Kahn's algorithm, DFS-based ordering, cycle detection in directed graphs, course-schedule patterns, longest path in a DAG
- [ ] [[DSA/05 - Graphs/03 - Shortest Path Algorithms|Shortest Path Algorithms]] — BFS for unweighted graphs, 0-1 BFS, Dijkstra (with priority queue), Bellman-Ford and negative cycles, Floyd-Warshall, SPFA, path reconstruction
- [ ] [[DSA/05 - Graphs/04 - Minimum Spanning Trees|Minimum Spanning Trees]] — Kruskal (with DSU), Prim (with priority queue), properties of MSTs, second-best MST *(advanced)*
- [ ] [[DSA/05 - Graphs/05 - Graph Connectivity|Graph Connectivity]] — strongly connected components (Tarjan, Kosaraju), bridges and articulation points, biconnected components, condensation graphs *(advanced)*
- [ ] [[DSA/05 - Graphs/06 - Bipartite Graphs and Matching|Bipartite Graphs and Matching]] — 2-coloring / bipartiteness checking, maximum bipartite matching (Kuhn's), König's theorem *(advanced)*
- [ ] [[DSA/05 - Graphs/07 - Lowest Common Ancestor|Lowest Common Ancestor]] — binary lifting, Euler tour with sparse table, distance queries on trees *(advanced)*
- [ ] [[DSA/05 - Graphs/08 - Network Flow|Network Flow]] — Ford-Fulkerson, Edmonds-Karp, Dinic's algorithm, max-flow min-cut theorem, flow modelling patterns *(advanced)*
- [ ] [[DSA/05 - Graphs/09 - Heavy-Light Decomposition|Heavy-Light Decomposition]] — path queries on trees, combining with segment trees *(advanced)*

---

## Part VI — Algorithm Design Paradigms

- [ ] [[DSA/06 - Algorithm Design Paradigms/01 - Greedy Algorithms|Greedy Algorithms]] — greedy-choice property, exchange arguments, interval scheduling, activity selection, Huffman coding, when greedy fails
- [ ] [[DSA/06 - Algorithm Design Paradigms/02 - Divide and Conquer|Divide and Conquer]] — the master theorem, merge-sort-style recursion, quickselect, closest pair of points, counting inversions
- [ ] [[DSA/06 - Algorithm Design Paradigms/03 - Backtracking|Backtracking]] — permutations, combinations, subsets, N-queens, sudoku solver, word search, pruning strategies, constraint propagation
- [ ] [[DSA/06 - Algorithm Design Paradigms/04 - Dynamic Programming Fundamentals|Dynamic Programming — Fundamentals]] — optimal substructure and overlapping subproblems, memoization vs. tabulation, state design, transition derivation, space optimization
- [ ] [[DSA/06 - Algorithm Design Paradigms/05 - Classic DP Problems|Classic DP Problems]] — 0/1 and unbounded knapsack, coin change, longest increasing subsequence (O(n log n) variant included), longest common subsequence, edit distance, matrix chain multiplication, partition problems, grid path DP
- [ ] [[DSA/06 - Algorithm Design Paradigms/06 - Advanced DP|Advanced DP]] — bitmask DP, tree DP, interval DP, digit DP, DP on subsets, convex hull trick and divide-and-conquer DP optimizations *(advanced)*
- [ ] [[DSA/06 - Algorithm Design Paradigms/07 - Meet in the Middle|Meet in the Middle]] — splitting exponential search spaces, subset-sum applications *(advanced)*

---

## Part VII — String Algorithms

- [ ] [[DSA/07 - String Algorithms/01 - String Matching|String Matching]] — naive matching, KMP and the failure function, Z-algorithm, Rabin-Karp rolling hash, Aho-Corasick for multiple patterns *(advanced)*
- [ ] [[DSA/07 - String Algorithms/02 - String Hashing|String Hashing]] — polynomial hashing, prefix hashes for O(1) substring comparison, double hashing and collision avoidance
- [ ] [[DSA/07 - String Algorithms/03 - Palindromes|Palindromes]] — expand-around-center, palindromic DP, Manacher's algorithm, palindromic substring counting
- [ ] [[DSA/07 - String Algorithms/04 - Suffix Structures|Suffix Structures]] — suffix arrays, LCP arrays (Kasai's), suffix automaton, suffix trees *(advanced)*

---

## Part VIII — Specialized Topics

- [ ] [[DSA/08 - Specialized Topics/01 - Intervals and Sweep Line|Intervals and Sweep Line]] — merging/inserting intervals, event-based sweeping, meeting rooms, skyline problem, coordinate compression
- [ ] [[DSA/08 - Specialized Topics/02 - Computational Geometry|Computational Geometry]] — points and vectors, cross/dot products, orientation tests, line and segment intersection, convex hull (Graham scan, Andrew's monotone chain), polygon area, closest pair *(advanced)*
- [ ] [[DSA/08 - Specialized Topics/03 - Game Theory|Game Theory]] — impartial games, Nim, Grundy numbers and the Sprague-Grundy theorem, minimax with alpha-beta pruning *(advanced)*
- [ ] [[DSA/08 - Specialized Topics/04 - Matrix Exponentiation|Matrix Exponentiation]] — representing linear recurrences as matrices, fast exponentiation of matrices, Fibonacci in O(log n) *(advanced)*
- [ ] [[DSA/08 - Specialized Topics/05 - Randomized Algorithms|Randomized Algorithms]] — randomized quickselect, reservoir sampling, shuffling (Fisher-Yates), probabilistic guarantees *(advanced)*

---

## Part IX — Practice

- [ ] [[DSA/09 - Practice/01 - Problem-Solving Patterns|Problem-Solving Patterns]] — catalogue mapping common problem signatures to the technique that solves them, and how to recognise which applies
- [ ] [[DSA/09 - Practice/02 - Competitive Programming Toolkit|Competitive Programming Toolkit]] — fast I/O in Java, integer overflow and `long` discipline, time/memory limits, template setup, common contest pitfalls

---

## Notes

- Order within each part is the intended reading order; Parts I–VI are broadly sequential, while Parts VII–IX can be taken as needed.
- Topics marked *(advanced)* are contest-oriented and can be safely deferred until the surrounding fundamentals are solid.
- This syllabus will be updated as chapters are added, split, or reordered.
- Each part is a folder (`DSA/NN - Part Name/`) holding numbered chapter notes and a `99 - Drawings` folder for its Excalidraw diagrams. The links to planned chapters already point to their final numbered paths.
