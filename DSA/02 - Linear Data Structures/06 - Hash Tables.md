# Hash Tables

A <span class="hl-blue">hash table</span> stores keys (or key–value pairs) in an array, using a **hash function** to turn each key into an array index. Insert, lookup, and delete all take `O(1)` **expected** time, which makes it the most-used data structure in practical programming. "Have I seen this before?", "how many times?", and "where was it?" are all hash-table questions.

The `O(1)` comes with conditions: a good hash function, a bounded load factor, keys whose `equals` and `hashCode` agree, and inputs that aren't chosen to attack the hash. This note covers how hash tables work (hash functions, chaining, open addressing, resizing), how Java's `HashMap` implements them, how to hash your own objects correctly, the classic problems, and what goes wrong when the conditions fail, up to deliberately constructed anti-hash tests.

## Contents

- [[#1. From Direct Addressing to Hashing|1. From Direct Addressing to Hashing]]
- [[#2. Hash Functions|2. Hash Functions]]
- [[#3. Collision Resolution — Separate Chaining|3. Collision Resolution — Separate Chaining]]
- [[#4. Collision Resolution — Open Addressing|4. Collision Resolution — Open Addressing]]
- [[#5. Load Factor and Resizing|5. Load Factor and Resizing]]
- [[#6. Implementing a Hash Map|6. Implementing a Hash Map]]
- [[#7. HashMap and HashSet in Java|7. HashMap and HashSet in Java]]
- [[#8. Hashing Custom Objects|8. Hashing Custom Objects]]
- [[#9. Classic Hashing Problems|9. Classic Hashing Problems]]
- [[#10. Performance and Anti-Hash Tests (advanced)|10. Performance and Anti-Hash Tests (advanced)]]
- [[#11. Common Mistakes|11. Common Mistakes]]
- [[#12. Trick Questions and Special Cases|12. Trick Questions and Special Cases]]
- [[#13. Quick Reference — Non-Obvious Outcomes|13. Quick Reference — Non-Obvious Outcomes]]
- [[#14. Summary|14. Summary]]

---

## 1. From Direct Addressing to Hashing

If keys are small non-negative integers (`0 ≤ k < U`), store the value for key `k` in `table[k]`. This <span class="hl-blue">direct-address table</span> has worst-case `O(1)` operations and no collisions. It's the frequency array from [[DSA/02 - Linear Data Structures/01 - Arrays#8.4 Frequency arrays instead of maps|Arrays § 8.4]]. It stops working when the key universe is huge (all `long`s, all strings) but only `n ≪ U` keys are actually used.

**Hashing** keeps an array of `m ≈ n` slots (<span class="hl-blue">buckets</span>) and maps each key to one with a hash function `h : keys → {0, …, m − 1}`. Since there are more possible keys than buckets, different keys can map to the same bucket: a <span class="hl-blue">collision</span>. Collisions are unavoidable (pigeonhole principle), so every hash table needs a **collision resolution** strategy.

> [!note] Definitions
> - <span class="hl-blue">Hash function</span> `h(k)`: maps a key to a bucket index. Must be **deterministic** (same key → same index, always).
> - <span class="hl-blue">Load factor</span> `α = n / m`: entries per bucket on average.
> - <span class="hl-blue">Collision</span>: `h(k₁) = h(k₂)` with `k₁ ≠ k₂`.

### 1.1 Hash table vs. the alternatives

| | Hash table | Balanced BST (`TreeMap`) | Sorted array | Direct addressing |
|---|---|---|---|---|
| Insert / delete | `O(1)` expected | `O(log n)` | `O(n)` | `O(1)` |
| Lookup | `O(1)` expected | `O(log n)` | `O(log n)` | `O(1)` |
| Worst case | `O(n)` (Java 8+: `O(log n)` for comparable keys) | `O(log n)` | — | `O(1)` |
| Ordered iteration, min/max, floor/ceiling, range queries | ✗ | ✓ | ✓ | by scanning `U` slots |
| Memory | moderate (empty buckets, entry objects) | high (node per entry) | minimal | `O(U)` |
| Key requirement | `equals` + `hashCode` | `Comparable` or a `Comparator` | comparable | small integer range |

> [!tip] Choosing
> Need order (smallest key ≥ x, iterate sorted, range counts)? → `TreeMap`. Keys are small integers? → an array. Otherwise → `HashMap`. Balanced trees are covered in [[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]].

---

## 2. Hash Functions

A good hash function spreads the keys that actually occur **evenly** across the buckets, and is fast to compute.

### 2.1 Integers

| Method | Formula | Notes |
|---|---|---|
| Division | `h(k) = k mod m` | choose `m` prime and not near a power of 2; with `m = 2ᵖ` it keeps only the low `p` bits |
| Multiplication (Fibonacci hashing) | `h(k) = (k · A mod 2ʷ) >> (w − p)` for `m = 2ᵖ` | `A = 2⁶⁴/φ = 0x9E3779B97F4A7C15`; takes the **top** bits of the product, which depend on all the input bits |
| Bit mixing then masking | `h = mix(k); h & (m − 1)` | what Java's `HashMap` does (§7.1) |

> [!warning] Low bits only
> With `m` a power of two, `k mod m` (or `k & (m − 1)`) ignores every bit above the lowest `p`. If the keys are all multiples of 64 (aligned addresses, scaled coordinates), they use only 1/64 of the buckets. That's why power-of-two tables always **mix** the high bits down first.

### 2.2 Strings and sequences: polynomial hashing

```
h(s) = s[0]·Bⁿ⁻¹ + s[1]·Bⁿ⁻² + … + s[n−1]       computed by Horner's rule:
h = 0
for c in s: h = h·B + c
```

Java uses `B = 31` with `int` overflow as the modulus (`String.hashCode`, `List.hashCode`). Multiplying by 31 is cheap (`(h << 5) − h`), and an odd multiplier loses no information mod 2³². Every character influences the hash, and the order of characters matters (`"ab"` and `"ba"` differ), unlike a plain sum or XOR. For substring comparisons in `O(1)`, prefix hashes with a large prime modulus are used instead ([[DSA/07 - String Algorithms/02 - String Hashing|String Hashing]]).

### 2.3 Combining fields

For an object with several fields, combine their hashes the same way: `h = 31·h + hash(field)` for each field. That's what `Objects.hash(a, b, c)`, `Arrays.hashCode`, `List.hashCode`, and (in practice) records do.

> [!warning] Weak combinations
> - `hash(x) + hash(y)` and `hash(x) ^ hash(y)` are **symmetric**: `(1, 2)` and `(2, 1)` collide. XOR also sends every `(x, x)` to `0`.
> - `31·x + y` for small coordinates collides systematically: `(0, 31)` and `(1, 0)` both give 31. Fine for typical inputs, but exploitable.

> [!info]- Universal hashing — where the "expected O(1)" guarantee comes from
> No fixed hash function is good for **every** input: an adversary who knows `h` can choose `n` keys that all collide. <span class="hl-blue">Universal hashing</span> picks `h` at random from a family when the table is created, so no input is bad for most choices. A family is universal if for any two distinct keys, `Pr[h(k₁) = h(k₂)] ≤ 1/m`. The classic Carter–Wegman family is
> ```
> h_{a,b}(k) = ((a·k + b) mod p) mod m        p prime > every key, a ∈ [1, p), b ∈ [0, p) random
> ```
> With a universal family and chaining, the expected cost of any operation is `O(1 + α)` **for every input**, where the expectation is over the random choice of `h` (not over the input). Java's `HashMap` does **not** randomize its hash, which is why anti-hash tests exist (§10).

---

## 3. Collision Resolution — Separate Chaining

Each bucket holds a **list** of the entries that hash to it. Insert adds to the bucket's list; lookup scans only that list.

```
buckets (m = 8)
 0: ─
 1: [k=17 → "q"] → [k=9 → "x"] → [k=1 → "a"]
 2: ─
 3: [k=11 → "c"]
 4: ─
 5: [k=5 → "e"] → [k=13 → "m"]
 6: ─
 7: ─                                  h(k) = k mod 8
```

![[Hash Tables - Separate Chaining.excalidraw|800]]

```
get(key):
    for entry in bucket[h(key)]:
        if entry.key equals key: return entry.value
    return not found

put(key, value):
    for entry in bucket[h(key)]:
        if entry.key equals key: entry.value = value; return    -- update, don't duplicate
    add (key, value) to bucket[h(key)]
    n += 1
    if n / m > maxLoad: resize                                  -- §5
```

**Cost:** computing `h` plus scanning one chain. Under the assumption that keys hash uniformly and independently ("simple uniform hashing"), the expected chain length is `α`, so

| Operation | Expected cost |
|---|---|
| Unsuccessful search | `Θ(1 + α)` |
| Successful search | `Θ(1 + α/2)` |
| Insert (after checking for the key) | `Θ(1 + α)` |

Keeping `α ≤` a constant (by resizing) makes all of them `O(1)` expected. The worst case, when every key lands in one bucket, is `Θ(n)` per operation.

> [!tip] Chaining tolerates high load
> A chained table still works with `α > 1` (just more slowly). Deletion is simply removal from a list. This simplicity is why Java's `HashMap` uses chaining.

---

## 4. Collision Resolution — Open Addressing

All entries live **in the array itself**, one per slot. On a collision, follow a <span class="hl-blue">probe sequence</span> `h(k, 0), h(k, 1), h(k, 2), …` until an empty slot (insert) or the key (lookup) is found. An empty slot during lookup means "not present". The load factor must stay **below 1**, in practice ≤ 0.5–0.7.

| Probing | `h(k, i)` | Problem |
|---|---|---|
| **Linear** | `(h(k) + i) mod m` | <span class="hl-blue">primary clustering</span>: occupied runs grow and merge, and long runs attract more keys |
| **Quadratic** | `(h(k) + c₁i + c₂i²) mod m` | secondary clustering (keys with the same `h(k)` share a sequence); may fail to find a free slot unless `m` is prime and `α ≤ ½`, or `m` is a power of 2 with triangular steps `i(i+1)/2` |
| **Double hashing** | `(h₁(k) + i·h₂(k)) mod m` | `h₂(k)` must be non-zero and coprime to `m`; closest to ideal |

### 4.1 Expected probes

For linear probing (Knuth's analysis), with load factor `α`:

| `α` | Successful search `≈ ½(1 + 1/(1−α))` | Unsuccessful search `≈ ½(1 + 1/(1−α)²)` |
|---|---|---|
| 0.5 | 1.5 | 2.5 |
| 0.75 | 2.5 | 8.5 |
| 0.9 | 5.5 | 50.5 |

Performance collapses as `α → 1`. Despite clustering, linear probing is often the **fastest** in practice at moderate load, because consecutive probes hit the same cache line. That makes it the usual choice for high-performance primitive-keyed maps.

### 4.2 Deletion: why you can't just empty the slot

Suppose `A`, `B`, `C` all hash to slot 3 and were inserted in that order into slots 3, 4, 5. Deleting `B` by emptying slot 4 breaks lookups for `C`: the probe for `C` starts at 3, finds `A`, moves to 4, finds **empty**, and concludes `C` isn't there.

![[Hash Tables - Linear Probing Deletion.excalidraw|800]]

Two fixes:

1. **Tombstones.** Mark the slot "deleted". Lookups skip over tombstones; inserts may reuse them. Tombstones count toward the load for lookups, so many deletions slow everything down until the next rehash cleans them out.
2. **Backward-shift deletion** (linear probing only). After emptying the slot, scan forward through the run, and move back any entry whose home slot is at or before the hole (cyclically). No tombstones needed.

> [!info]- Other open-addressing schemes
> - **Robin Hood hashing:** during insertion, an entry that is far from its home slot takes the place of one that's closer to its own, and the displaced entry continues probing. This evens out probe lengths and shrinks the worst case.
> - **Cuckoo hashing:** two tables and two hash functions; each key lives in one of exactly two possible slots, so lookup is **worst-case `O(1)`** (two probes). Insertion kicks out an occupant to its alternative slot, possibly cascading, and rehashes on a cycle.
> - **Swiss tables** (Abseil, Rust's `HashMap`) store a byte of hash metadata per slot and compare 16 slots at once with SIMD instructions.

---

## 5. Load Factor and Resizing

As entries are added, `α = n/m` grows and operations slow down. When `α` passes a threshold, allocate a bigger array (typically `2m`) and **rehash** every entry into it. Each entry's bucket depends on `m`, so entries can't simply be copied over.

- One resize costs `Θ(n)`, but with doubling the total over `n` insertions is `O(n)`, so insertion is `O(1)` **amortized** (the same argument as for dynamic arrays: [[DSA/01 - Foundations/01 - Complexity Analysis#8.1 Aggregate method — dynamic arrays|Complexity Analysis § 8.1]]).
- Typical thresholds: `0.75` for chaining (Java's default), `0.5`–`0.7` for open addressing.
- Shrinking on deletion is optional; Java's `HashMap` never shrinks.

![[Hash Tables - Resize Split.excalidraw|800]]

> [!info]- Why doubling makes Java's rehash cheap
> With `m` a power of two and index `= hash & (m − 1)`, doubling `m` adds one more bit to the mask. Each entry either stays at index `i` or moves to `i + m_old`, depending on that one bit of its hash. Java's `resize()` splits each chain into a "low" and a "high" list in one pass, preserving their relative order.

---

## 6. Implementing a Hash Map

### 6.1 Separate chaining, generic keys

```java
import java.util.Objects;

class ChainedHashMap<K, V> {
    private static class Entry<K, V> {
        final K key;
        V val;
        Entry<K, V> next;
        Entry(K key, V val, Entry<K, V> next) { this.key = key; this.val = val; this.next = next; }
    }

    private Entry<K, V>[] table;
    private int size;

    @SuppressWarnings("unchecked")
    ChainedHashMap() { table = (Entry<K, V>[]) new Entry[16]; }   // no generic array creation

    private static int index(Object key, int capacity) {
        int h = Objects.hashCode(key);    // null → 0
        h ^= (h >>> 16);                  // fold the high bits into the low bits
        return h & (capacity - 1);        // capacity is a power of two; result is never negative
    }

    public V get(K key) {
        for (Entry<K, V> e = table[index(key, table.length)]; e != null; e = e.next)
            if (Objects.equals(e.key, key)) return e.val;
        return null;
    }

    public V put(K key, V val) {
        int i = index(key, table.length);
        for (Entry<K, V> e = table[i]; e != null; e = e.next) {
            if (Objects.equals(e.key, key)) {        // existing key: update
                V old = e.val;
                e.val = val;
                return old;
            }
        }
        table[i] = new Entry<>(key, val, table[i]);  // new key: prepend to the chain
        if (++size > table.length * 3 / 4) resize();
        return null;
    }

    public V remove(K key) {
        int i = index(key, table.length);
        Entry<K, V> prev = null;
        for (Entry<K, V> e = table[i]; e != null; prev = e, e = e.next) {
            if (Objects.equals(e.key, key)) {
                if (prev == null) table[i] = e.next;
                else prev.next = e.next;
                size--;
                return e.val;
            }
        }
        return null;
    }

    public int size() { return size; }

    @SuppressWarnings("unchecked")
    private void resize() {
        Entry<K, V>[] old = table;
        table = (Entry<K, V>[]) new Entry[2 * old.length];
        for (Entry<K, V> head : old) {
            Entry<K, V> e = head;
            while (e != null) {
                Entry<K, V> next = e.next;
                int i = index(e.key, table.length);  // recompute with the NEW capacity
                e.next = table[i];
                table[i] = e;
                e = next;
            }
        }
    }
}
```

> [!warning] `Math.abs(hashCode()) % m` can be negative
> `Math.abs(Integer.MIN_VALUE)` is `Integer.MIN_VALUE` (there's no positive counterpart in two's complement), so the bucket index is negative and the array access throws. It's not a theoretical case: `"polygenelubricants".hashCode()` is exactly `Integer.MIN_VALUE`. Use `h & (m − 1)` for power-of-two sizes, `Math.floorMod(h, m)`, or `(h & 0x7fffffff) % m`.

### 6.2 Open addressing for primitive keys (the contest workhorse)

When keys are `int`/`long` and performance matters, a linear-probing table on primitive arrays avoids all boxing. This version has a fixed capacity (at least twice the maximum number of entries) and no deletion, which covers most competitive-programming needs.

```
put(k, v):                                   get(k):
    i = slot(k)                                  i = slot(k)
    while used[i] and keys[i] ≠ k:               while used[i]:
        i = (i + 1) mod capacity                     if keys[i] == k: return vals[i]
    used[i] = true; keys[i] = k; vals[i] = v         i = (i + 1) mod capacity
                                                 return not found
```

```java
class LongIntMap {
    private final long[] keys;
    private final int[] vals;
    private final boolean[] used;
    private final int shift, mask;

    LongIntMap(int maxEntries) {      // capacity = smallest power of two ≥ 2·maxEntries
        int bits = 32 - Integer.numberOfLeadingZeros(Math.max(2, 2 * maxEntries) - 1);
        keys = new long[1 << bits];
        vals = new int[1 << bits];
        used = new boolean[1 << bits];
        shift = 64 - bits;
        mask = (1 << bits) - 1;
    }

    private int slot(long k) {        // Fibonacci hashing: the TOP bits of k·(2^64/φ)
        return (int) ((k * 0x9E3779B97F4A7C15L) >>> shift);
    }

    void put(long k, int v) {
        int i = slot(k);
        while (used[i] && keys[i] != k) i = (i + 1) & mask;   // linear probing with wrap-around
        used[i] = true;
        keys[i] = k;
        vals[i] = v;
    }

    int getOrDefault(long k, int def) {
        for (int i = slot(k); used[i]; i = (i + 1) & mask)
            if (keys[i] == k) return vals[i];
        return def;
    }
}
```

> [!warning] Never fill an open-addressing table
> If every slot is used, a lookup for a missing key never meets an empty slot and loops forever. Size the table so the load stays well below 1 (here at most ½), or add resizing.

---

## 7. HashMap and HashSet in Java

### 7.1 How `HashMap` works

| Detail | Value |
|---|---|
| Structure | array of buckets, separate chaining |
| Default capacity / load factor | 16 / 0.75 (resize at 12 entries); the array is allocated on the first `put` |
| Capacity | always a power of two; doubles on resize |
| Bucket index | `(h ^ (h >>> 16)) & (capacity − 1)` where `h = key.hashCode()` |
| `null` key | allowed (one), stored in bucket 0 |
| Long chains | a bucket with ≥ 8 entries becomes a **red-black tree** (if capacity ≥ 64; otherwise the table is resized instead), and turns back into a list at ≤ 6 |
| Worst case per operation | `O(log n)` for `Comparable` keys in a treeified bucket; can still be `O(n)` for keys that aren't mutually comparable |
| Shrinking | never |
| `HashSet<E>` | a `HashMap<E, Object>` with a dummy value |

The `h ^ (h >>> 16)` step folds the high half of the hash into the low half, because the mask only looks at the low bits. Without it, keys that differ only in their high bits (`Float` values, or `Integer`s that are multiples of a large power of two) would all collide.

### 7.2 Costs and idioms

| Task | Code | Notes |
|---|---|---|
| Count occurrences | `cnt.merge(x, 1, Integer::sum)` | or `cnt.put(x, cnt.getOrDefault(x, 0) + 1)` |
| Decrement, remove at zero | `cnt.computeIfPresent(x, (k, v) -> v == 1 ? null : v - 1)` | returning `null` **removes** the entry |
| Group into lists | `groups.computeIfAbsent(key, k -> new ArrayList<>()).add(v)` | creates the list only when missing |
| Insert only if absent | `map.putIfAbsent(k, v)` | returns the existing value, or `null` |
| Check and insert in one call | `if (!set.add(x)) { /* duplicate */ }` | `add` returns `false` if already present |
| Look up with a default | `map.getOrDefault(k, 0)` | does **not** insert |
| Iterate keys and values | `for (Map.Entry<K, V> e : map.entrySet())` | `keySet()` + `get()` hashes every key twice |
| Remove while iterating | `map.entrySet().removeIf(e -> e.getValue() == 0)` | or an explicit `Iterator` with `it.remove()` |
| Distinguish "absent" from "maps to `null`" | `map.containsKey(k)` | `get` returns `null` for both |

> [!warning] Iteration order is unspecified
> `HashMap` and `HashSet` iterate in bucket order. It can change when the table resizes, differs between JDK versions, and for `Map.of`/`Set.of` it's deliberately **randomized per JVM run**. Small non-negative `Integer` keys often *appear* sorted (their hash is their value), which hides the bug until a key exceeds the capacity or is negative.
> - Need insertion order? `LinkedHashMap` / `LinkedHashSet`.
> - Need sorted order? `TreeMap` / `TreeSet`.

> [!warning] Modifying a map while iterating it
> `for (K k : map.keySet()) if (…) map.remove(k);` throws `ConcurrentModificationException` (fail-fast, best effort). Use `removeIf` on the view, or an iterator's `remove()`. `put` of an **existing** key during iteration doesn't change the structure and is allowed; `put` of a new key isn't.

### 7.3 `LinkedHashMap`: insertion order, access order, and LRU

`LinkedHashMap` threads a doubly linked list through the entries. By default it iterates in insertion order. Constructed with `accessOrder = true`, every `get`/`put` moves the entry to the end, and overriding `removeEldestEntry` turns it into an LRU cache in a few lines:

```java
class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;

    LRUCache(int capacity) {
        super(16, 0.75f, true);              // true = access order (least recent first)
        this.capacity = capacity;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity;            // called after each put
    }
}
```

The from-scratch version (hash map + doubly linked list) is in [[DSA/02 - Linear Data Structures/03 - Linked Lists#5.1 LRU cache — hash map + doubly linked list|Linked Lists § 5.1]].

> [!warning] In access-order mode, `get` is a structural modification
> Calling `get` while iterating an access-ordered `LinkedHashMap` reorders the list and throws `ConcurrentModificationException`.

### 7.4 Other maps and sets

| Class | Use |
|---|---|
| `TreeMap` / `TreeSet` | sorted keys; `floorKey`, `ceilingKey`, `headMap`, `firstKey`, all `O(log n)` |
| `EnumMap` / `EnumSet` | enum keys: an array (or bit vector) indexed by ordinal; faster than hashing |
| `IdentityHashMap` | compares keys with `==` and hashes with `System.identityHashCode` |
| `ConcurrentHashMap` | thread-safe; **rejects `null`** keys and values |
| `BitSet` / `boolean[]` | sets of small non-negative integers |
| `Map.of`, `Set.of`, `Map.copyOf` | immutable; reject `null`; `Set.of(1, 1)` throws `IllegalArgumentException` (duplicate element) |

---

## 8. Hashing Custom Objects

### 8.1 The `equals`/`hashCode` contract

> [!important] The contract
> 1. If `a.equals(b)`, then `a.hashCode() == b.hashCode()`. **(Required.)**
> 2. The converse is not required: unequal objects may share a hash (that's a collision).
> 3. Both must stay the same while the object is a key in a hash-based collection.
>
> `HashMap` finds the bucket with `hashCode`, then confirms with `equals`. Break rule 1 and equal keys go to different buckets, so `contains` misses them and duplicates appear.

| Mistake | Effect |
|---|---|
| Override `equals` but not `hashCode` | equal objects have different (identity) hashes: `set.contains(new Point(1, 2))` is `false` after adding an equal point; the set holds "duplicates" |
| Override `hashCode` but not `equals` | equal-looking objects land in the same bucket but `equals` (identity) says different: same symptoms |
| `public boolean equals(Point other)` | an **overload**, not an override. Collections call `equals(Object)`, which is still identity. Use `@Override` and the `Object` parameter so the compiler catches it |
| `hashCode` uses a field that `equals` ignores | equal objects can hash differently, violating rule 1 |
| Mutable field in `hashCode`, mutated after insertion | the entry is "lost": it sits in the bucket for its old hash |

```java
// Correct by hand
final class Point {
    final int x, y;
    Point(int x, int y) { this.x = x; this.y = y; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Point p)) return false;
        return x == p.x && y == p.y;
    }

    @Override
    public int hashCode() { return 31 * x + y; }     // or Objects.hash(x, y), which boxes
}

// Correct automatically (Java 16+): records generate equals, hashCode, and toString from the components
record P(int x, int y) {}
```

More on `equals`/`hashCode` from the language side is in [[Java/04 - Object-Oriented Programming/01 - Classes and Objects#10.3 Printing and Comparing Objects|Java: Classes and Objects § 10.3]].

### 8.2 Mutable keys

```java
List<Integer> key = new ArrayList<>(List.of(1, 2));
Set<List<Integer>> set = new HashSet<>();
set.add(key);
key.add(3);                        // the key's hashCode changes
set.contains(key);                 // false: looks in the bucket for [1, 2, 3]'s hash
set.contains(List.of(1, 2));       // false: right bucket, but equals([1,2,3]) fails
set.size();                        // 1: the entry is still there, unreachable
```

![[Hash Tables - Mutable Key.excalidraw|800]]

Use immutable keys: `String`, boxed primitives, records with immutable components, `List.copyOf(...)`.

### 8.3 Arrays are bad keys; pairs need encoding

Arrays inherit `equals` and `hashCode` from `Object` (identity), so `set.contains(new int[]{1, 2})` is `false` even if an array with the same contents was added. Options for multi-part keys:

| Key | Code | Trade-off |
|---|---|---|
| Record | `record Pair(int a, int b) {}` | clean and correct; one object per key |
| List | `List.of(a, b)` | correct; boxing; slower |
| String | `a + "," + b` | correct (the separator is essential: `1,23` vs `12,3`); slow |
| Packed `long` | `((long) a << 32) \| (b & 0xFFFFFFFFL)` | fast, no extra objects; see the warnings below |
| Packed `long`, bounded values | `(long) a * M + b` with `M > max b` | fast; needs `0 ≤ b < M` |
| Array contents | `Arrays.toString(arr)`, or a wrapper using `Arrays.equals`/`Arrays.hashCode` | for variable-length keys such as count signatures |

> [!warning] Packing pairs into a `long`
> - **Mask the low part.** `((long) a << 32) | b` with a negative `b` sign-extends `b` to 64 bits, whose upper 32 bits are all ones, overwriting `a`. Use `b & 0xFFFFFFFFL`.
> - **`Long.hashCode` is `(int) (v ^ (v >>> 32))`.** For a packed pair that's `a ^ b`: `(a, b)` and `(b, a)` collide, and **every** `(x, x)` hashes to 0. Coordinates along a diagonal all land in one bucket. Java 8+ treeifies the bucket, so it's `O(log n)` instead of `O(n)` per operation, but still much slower than expected. Mixing the packed value first (§10.2) avoids it.

---

## 9. Classic Hashing Problems

### 9.1 Two sum (unsorted, return indices)

```
twoSum(a, target):
    seen = empty map                        -- value → index
    for i = 0 to n − 1:
        if (target − a[i]) in seen: return (seen[target − a[i]], i)
        seen[a[i]] = i                      -- insert AFTER checking
```

```java
static int[] twoSum(int[] a, int target) {
    Map<Integer, Integer> seen = new HashMap<>();
    for (int i = 0; i < a.length; i++) {
        Integer j = seen.get(target - a[i]);
        if (j != null) return new int[]{j, i};
        seen.put(a[i], i);
    }
    return new int[0];
}
```

`O(n)` expected. Checking **before** inserting prevents pairing an element with itself (`[3, 2, 4]`, target `6`, must not return `[0, 0]`), and handles duplicates (`[3, 3]`, target `6`, returns `[0, 1]`). On a **sorted** array the two-pointer method needs no extra space ([[DSA/03 - Sorting and Searching/03 - Two Pointers|Two Pointers]]).

### 9.2 Longest consecutive sequence in O(n)

Put everything in a set. Only start counting from an `x` that **begins** a run (`x − 1` not in the set), and walk upward.

```java
static int longestConsecutive(int[] a) {
    Set<Integer> set = new HashSet<>();
    for (int x : a) set.add(x);
    int best = 0;
    for (int x : set) {                         // iterate the SET, not the array
        if (set.contains(x - 1)) continue;      // not the start of a run
        int len = 1;
        while (set.contains(x + len)) len++;
        best = Math.max(best, len);
    }
    return best;
}
```

Each element is visited by at most one inner walk (the one starting at its run's beginning), so the total is `O(n)`. Sorting gives `O(n log n)`.

> [!warning] Iterate the set, not the array
> If the array contains the start of a long run many times (`[1, 1, 1, …, 1, 2, 3, …, k]`), iterating the array starts the same `O(k)` walk once per duplicate: `O(n·k)`, quadratic in the worst case. This is a known LeetCode TLE.

### 9.3 Subarray sum equals k

Count subarrays with sum exactly `k`, with negative numbers allowed (so a sliding window doesn't work). With prefix sums `P`, a subarray `(i, j]` has sum `P[j] − P[i]`, so count earlier prefixes equal to `P[j] − k`:

```java
static int subarraySum(int[] a, int k) {
    Map<Integer, Integer> count = new HashMap<>();
    count.put(0, 1);                                 // the empty prefix: subarrays starting at index 0
    int sum = 0, res = 0;
    for (int x : a) {
        sum += x;
        res += count.getOrDefault(sum - k, 0);       // look up BEFORE adding the current prefix
        count.merge(sum, 1, Integer::sum);
    }
    return res;
}
```

Forgetting `count.put(0, 1)` misses every subarray that starts at index 0. The variants (longest subarray with sum `k`: store the **first** index of each prefix; subarrays divisible by `k`: key on `Math.floorMod(sum, k)`) are in [[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]].

### 9.4 More patterns

| Problem | Hash structure | Key idea |
|---|---|---|
| Contains duplicate within distance `k` | set of the last `k` elements | sliding window: add `a[i]`, remove `a[i−k]` |
| Group anagrams | `Map<String, List<String>>` | canonical key ([[DSA/02 - Linear Data Structures/02 - Strings#6.2 Grouping anagrams|Strings § 6.2]]) |
| Isomorphic strings / word pattern | two maps | bijection ([[DSA/02 - Linear Data Structures/02 - Strings#6.3 Isomorphic strings and word patterns — the mapping must be a bijection|Strings § 6.3]]) |
| 4Sum II (`a[i] + b[j] + c[k] + d[l] = 0`) | map of all `a[i] + b[j]` sums → count | meet in the middle: `O(n²)` instead of `O(n⁴)` |
| Valid Sudoku | sets per row, column, and box | box index `(r / 3) * 3 + c / 3` |
| First non-repeating element in a stream | counts + `LinkedHashMap` or queue | order plus counts |
| Copy a graph / random-pointer list | `Map<Node, Node>` | original → copy ([[DSA/02 - Linear Data Structures/03 - Linked Lists#9.7 Copy a list with random pointers|Linked Lists § 9.7]]) |
| Count pairs with difference `k` | set or count map | for each `x`, look up `x + k`; `k = 0` needs counts ≥ 2 |
| Detect a cycle in an iterated function | set of seen values | or Floyd for `O(1)` space |

---

## 10. Performance and Anti-Hash Tests (advanced)

### 10.1 The constant factors

`HashMap<Integer, Integer>` is `O(1)` but expensive per operation: boxing allocates `Integer` objects (outside the cache range `−128..127`), every entry is a separate `Node` object (~32 bytes), and lookups chase pointers. Compared to an `int[]` indexed by key, expect something like **10–50× slower and 5–10× more memory**.

| If keys are… | Use |
|---|---|
| in a small range `[0, U)`, `U ≤ ~10⁷` | `int[]` / `boolean[]` / `BitSet` |
| arbitrary, but all known in advance | sort + compress to `0..n−1` ([[DSA/08 - Specialized Topics/01 - Intervals and Sweep Line|coordinate compression]]), then arrays |
| arbitrary, online | `HashMap`, or a primitive open-addressing map (§6.2) |

> [!warning] `==` on `Integer` values from a map
> ```java
> Map<Character, Integer> m1 = …, m2 = …;
> if (m1.get(a) == m2.get(b)) …          // compares Integer REFERENCES
> ```
> Works while the values are in `−128..127` (cached `Integer` objects), then fails for equal larger values. A classic LeetCode bug in "word pattern"-style solutions that store indices: it passes until a test has more than 128 elements. Use `.equals`, `Objects.equals`, or unbox to `int` first.

### 10.2 Anti-hash tests

Java's `HashMap` hash is **fixed and public**. For `Integer` keys, `hashCode()` is the value itself, so after the `h ^ (h >>> 16)` spreading, an adversary who knows the table capacity can choose many keys that agree on the low bits, and they all land in one bucket. On Codeforces, such inputs are added through "hacks" specifically to time out solutions that rely on `HashMap`.

| Language / structure | Under attack |
|---|---|
| C++ `unordered_map` | `O(n)` per operation: the classic hacking target |
| Java `HashMap`, `Comparable` keys | the bucket treeifies: `O(log n)` per operation, plus a large constant |
| Java `HashMap`, non-comparable colliding keys | can degrade to `O(n)` |
| Strings in any `31`-polynomial table | `"Aa"`/`"BB"`-style collisions in `2ᵏ` combinations ([[DSA/02 - Linear Data Structures/02 - Strings#10.5 hashCode collisions are easy to construct|Strings § 10.5]]) |

**Defences**, from simplest:

1. **Avoid hashing**: sort, compress, and use arrays; or use a `TreeMap` (`O(log n)`, no worst case to exploit).
2. **Randomize**: transform each key with a strong mixing function and a **random seed chosen at run time**, then hash the result. `splitmix64` is a bijection on 64-bit values, so distinct keys stay distinct and the transformed value can itself be the key:

```java
static final long SEED = System.nanoTime();     // differs on every run: the adversary can't predict it

static long splitmix64(long x) {
    x += 0x9E3779B97F4A7C15L;
    x = (x ^ (x >>> 30)) * 0xBF58476D1CE4E5B9L;
    x = (x ^ (x >>> 27)) * 0x94D049BB133111EBL;
    return x ^ (x >>> 31);
}

// Map<Long, Integer> m; use m.merge(splitmix64(key ^ SEED), 1, Integer::sum) instead of the raw key
```

3. **Use a primitive open-addressing map** with a randomized multiplier.

> [!info]- Bloom filters — a probabilistic set
> A <span class="hl-blue">Bloom filter</span> is a bit array of size `m` plus `k` hash functions. `add(x)` sets the `k` bits `hᵢ(x)`; `mightContain(x)` checks that all `k` bits are set. It can return **false positives** (all bits happen to be set by other elements) but **never false negatives**, and it can't delete. With `n` elements, the false-positive rate is about `(1 − e^(−kn/m))ᵏ`, minimized at `k = (m/n) ln 2`. About 10 bits per element gives ~1% false positives, whatever the size of the elements. It's used as a cheap pre-check before an expensive lookup (databases, caches, web crawlers).

---

## 11. Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| `equals` overridden without `hashCode` | duplicates in sets, failed lookups | override both, or use a record |
| `equals(Point p)` instead of `equals(Object o)` | collections ignore it | `@Override` with `Object` |
| Mutating a key after insertion | entry unreachable | immutable keys |
| `int[]` as a key | lookups always miss | record, `List`, string, or packed `long` |
| `Math.abs(h) % m` | negative index for `MIN_VALUE` | `h & (m−1)` / `floorMod` |
| Open-addressing delete by emptying the slot | later keys "disappear" | tombstones or backward shift |
| Resizing by copying the bucket array | entries in wrong buckets | rehash every entry |
| Relying on `HashMap` iteration order | works locally, fails elsewhere | `LinkedHashMap` / `TreeMap` |
| `map.get(k) == null` meaning "absent" | wrong when a value is `null` | `containsKey` |
| `m1.get(a) == m2.get(b)` on `Integer`s | fails above 127 | `.equals` |
| Removing in a for-each over `keySet()` | `ConcurrentModificationException` | `removeIf` / iterator |
| Two sum: inserting before checking | element paired with itself | check, then insert |
| Prefix-sum map without `{0: 1}` | misses subarrays starting at 0 | seed the map |
| Longest consecutive: iterating the array | `O(n²)` with duplicates | iterate the set |
| `(a << 32) \| b` with negative `b` | corrupted key | mask `b & 0xFFFFFFFFL` |
| `HashMap<Integer, …>` with keys in `[0, 10⁶)` | slow, memory-heavy | `int[]` |
| `new HashMap<>(n)` expecting no resize | one resize anyway | `HashMap.newHashMap(n)` (Java 19+) or `(int) (n / 0.75f) + 1` |

---

## 12. Trick Questions and Special Cases

> [!question]- Is `HashMap.get` O(1)?
> `O(1)` **expected** (average) with a decent hash function, and amortized for `put` because of resizing. The worst case is `O(n)` per operation before Java 8 and, since Java 8, `O(log n)` when the colliding keys are `Comparable` (the bucket becomes a red-black tree). With adversarial keys and a known hash, the expected-time assumption simply doesn't hold.

> [!question]- Two keys have the same `hashCode`. Are they equal?
> Not necessarily. `"Aa"` and `"BB"` both hash to 2112, `Long` values `(1L << 32) | 1` and `0L` both hash to `0`. Equal hashes are necessary for equality, never sufficient, which is why `HashMap` always confirms with `equals`.

> [!question]- Two objects are `equals`. Must their hash codes be equal?
> Yes. That's the one hard requirement of the contract. If it's violated, `HashMap`/`HashSet` behave incorrectly (missed lookups, duplicate entries), not just slowly.

> [!question]- Can `hashCode()` return the same constant for every object?
> It's **legal** (equal objects trivially have equal hashes) and every hash collection still works **correctly**, but every key lands in one bucket: `O(n)` per operation before Java 8, `O(log n)` after treeification if the keys are `Comparable`, and potentially still `O(n)` if they aren't.

> [!question]- `Set<int[]> s = new HashSet<>(); s.add(new int[]{1, 2}); s.contains(new int[]{1, 2})` — result?
> `false`. Arrays use identity `equals` and `hashCode`. The two arrays have the same contents but are different objects. Use `List.of(1, 2)`, a record, or an encoded key.

> [!question]- `new HashMap<>(100)`, then 100 puts. How many resizes?
> One. The constructor rounds the capacity up to 128, and the threshold is `128 × 0.75 = 96`, so the 97th insertion triggers a resize to 256. The argument is the initial **capacity**, not the expected number of entries. Java 19 added `HashMap.newHashMap(int numMappings)`, which sizes the table so that `numMappings` entries fit without resizing.

> [!question]- Why does `HashMap` iteration over keys `{3, 1, 2}` print them sorted?
> Coincidence of the implementation: `Integer.hashCode()` is the value, so small non-negative keys go to bucket `key` and the buckets are iterated in index order. Add `17` to a capacity-16 map and it lands in bucket 1, between `1` and `2`; negative keys land at high indices. Never rely on it.

> [!question]- What's the bucket index of `"polygenelubricants"` with `Math.abs(s.hashCode()) % 16`?
> The hash is `Integer.MIN_VALUE`, `Math.abs` of which is still `Integer.MIN_VALUE` (negative), and `MIN_VALUE % 16` is `0`. So it happens to be `0` here, but with a modulus that isn't a power of two (say `% 10`, giving `−8`) the index is negative and the array access throws. The bug depends on the table size, which makes it hard to reproduce.

> [!question]- Linear probing: delete key B from the cluster [A, B, C] (all with the same home slot) by setting its slot to empty. What happens to `get(C)`?
> It returns "not found". The probe sequence for `C` starts at the home slot, sees `A`, moves on, hits the empty slot where `B` was, and stops. Open addressing needs tombstones or backward-shift deletion.

> [!question]- Longest consecutive sequence: is the nested `while` loop O(n²)?
> No, `O(n)`, as long as the outer loop skips every `x` with `x − 1` in the set and iterates the **set** (not the array with duplicates). Each element is then walked over by exactly one inner loop, the one starting at its run's first element.

> [!question]- Two sum on `[3, 3]` with target 6 — does a map from value to index lose one of the 3s?
> Not if you check before inserting: at `i = 1`, the map holds `{3: 0}`, `target − 3 = 3` is found, and `[0, 1]` is returned. Inserting first would overwrite the index (`{3: 1}`) and return `[1, 1]`.

> [!question]- Subarray sum equals k with `a = [1, 1, 1]`, `k = 2`?
> `2` (`[1, 1]` twice). Without the initial `{0: 1}` entry, the subarray starting at index 0 (prefix sum 2 minus the empty prefix 0) is missed and the answer comes out as `1`.

> [!question]- Is a `HashSet<Integer>` faster than a `boolean[]` for keys in `[0, 10⁶)`?
> No, the array is much faster: a direct index, no hashing, no boxing, and 1 MB of memory versus tens of MB for a million `Integer` objects and entry nodes. Hash sets are for keys that **don't** fit a small range.

> [!question]- Does `HashMap` allow `null` keys and values? Does `ConcurrentHashMap`? `Map.of`?
> `HashMap`: one `null` key and any number of `null` values. `ConcurrentHashMap`: neither (a `null` would make `get` ambiguous between "absent" and "maps to `null`" in concurrent code where `containsKey` + `get` isn't atomic). `Map.of`/`Set.of`: neither, plus they reject duplicate keys at creation time.

> [!question]- `map.merge(k, -1, Integer::sum)` brings a count to 0. Is the key removed?
> No, the entry stays with value `0`, and `map.size()` / `containsKey` still count it. `merge` removes the entry only when the remapping function returns `null`. Sliding-window code that uses `map.size()` as "number of distinct elements in the window" must remove zero-count keys explicitly: `computeIfPresent(k, (key, v) -> v == 1 ? null : v - 1)`.

---

## 13. Quick Reference — Non-Obvious Outcomes

| Code / claim | Result | Why |
|---|---|---|
| `HashMap` lookup | `O(1)` expected; `O(log n)` worst (Java 8+, comparable keys) | treeified buckets |
| `HashMap` default | capacity 16, load 0.75, resize at 12 | |
| `new HashMap<>(100)` + 100 puts | 1 resize | threshold 96 |
| Treeify | bucket ≥ 8 and capacity ≥ 64 | untreeify at ≤ 6 |
| Bucket index | `(h ^ h>>>16) & (cap−1)` | mixes high bits into low |
| `"Aa".hashCode() == "BB".hashCode()` | `true` | 2112 |
| `"polygenelubricants".hashCode()` | `Integer.MIN_VALUE` | `Math.abs` stays negative |
| `Long.hashCode(v)` | `(int)(v ^ v>>>32)` | packed `(x, x)` pairs → 0 |
| `Integer.hashCode(v)` | `v` | small keys look sorted |
| `Boolean.hashCode(true/false)` | `1231` / `1237` | |
| `int[]` as key | identity | contents ignored |
| `equals` without `hashCode` | broken sets | contract violated |
| Mutated key | entry lost | wrong bucket |
| `Integer == Integer` from a map, values ≥ 128 | can be `false` | `Integer` cache only covers −128..127 |
| `merge` to 0 | entry kept | only `null` removes |
| `getOrDefault` | doesn't insert | `computeIfAbsent` does |
| `Set.of(1, 1)` | `IllegalArgumentException` | duplicates rejected |
| `Map.of(...)` iteration | randomized per run | salted |
| Linear probing at α = 0.9 | ≈ 50 probes per miss | `½(1 + 1/(1−α)²)` |
| Open addressing, delete by emptying | breaks lookups | tombstones |
| Universal hashing | `O(1 + α)` expected for every input | random `h` |

---

## 14. Summary

- A hash table maps keys to buckets with a hash function and resolves collisions by **chaining** (lists per bucket; Java's choice) or **open addressing** (probe the array; fast and cache-friendly at low load, but deletion needs tombstones).
- With load factor `α` kept bounded by **resizing** (rehash every entry into a doubled table), operations are `O(1)` expected and insertion is `O(1)` amortized. The worst case is `O(n)`, or `O(log n)` in Java 8+ for comparable keys.
- Good hashes use **all** bits of the key: mix before masking a power-of-two table, use polynomial hashing for sequences, and avoid symmetric combinations like XOR and `+`.
- Java's `HashMap`: capacity a power of two, load 0.75, spreading `h ^ (h >>> 16)`, treeified buckets, unspecified iteration order. Learn the idioms (`merge`, `computeIfAbsent`, `computeIfPresent`, `removeIf`) and the traps (`null`, `Integer ==`, modification during iteration).
- Custom keys: `equals` and `hashCode` must agree, keys must not change while stored, and arrays are identity-keyed. Records do it right automatically; packed `long`s are fast but need masking and mixing.
- Classic uses: two sum, longest consecutive run, prefix-sum counting, grouping by canonical keys, bijection checks, and meet-in-the-middle sums.
- When the keys are small integers, an array beats a hash map by an order of magnitude. When inputs are adversarial, randomize the hash or avoid hashing.

## Related

- [[DSA/00 - Syllabus|Syllabus]]
- Previous: [[DSA/02 - Linear Data Structures/05 - Queues and Deques|Queues and Deques]] · Next: [[DSA/03 - Sorting and Searching/01 - Sorting Algorithms|Sorting Algorithms]]
- [[DSA/01 - Foundations/01 - Complexity Analysis#8. Amortized Analysis|Complexity Analysis § 8]]: amortized resizing; § 11.2 on Java collection costs
- [[DSA/02 - Linear Data Structures/03 - Linked Lists#5.1 LRU cache — hash map + doubly linked list|Linked Lists § 5.1]]: LRU cache from scratch
- [[DSA/02 - Linear Data Structures/02 - Strings|Strings]]: string hashing basics, anagram keys
- [[DSA/07 - String Algorithms/02 - String Hashing|String Hashing]]: polynomial rolling hashes for substrings
- [[DSA/03 - Sorting and Searching/05 - Prefix Sums and Difference Arrays|Prefix Sums and Difference Arrays]]: prefix sums with hash maps
- [[DSA/04 - Trees and Hierarchical Structures/03 - Balanced Trees|Balanced Trees]]: `TreeMap`/`TreeSet` when order matters
- [[Java/05 - Working with Data and Errors/02 - Generics|Java: Generics]]: boxing traps, generic arrays
