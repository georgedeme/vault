# Loops in Java

Loops repeat a block of code while a condition holds, or once per element of a sequence. Java provides four forms — the counter-style `for`, the collection-style enhanced `for`, `while`, and `do-while` — plus `break` and `continue` to alter a loop's flow from inside its body. Choosing the right form, and understanding exactly when the condition is checked relative to the body, avoids a number of off-by-one and infinite-loop bugs.

## Contents

- [[#1. The while Loop|1. The while Loop]]
- [[#2. The do-while Loop|2. The do-while Loop]]
- [[#3. The for Loop|3. The for Loop]]
- [[#4. The Enhanced for Loop (for-each)|4. The Enhanced for Loop (for-each)]]
- [[#5. break|5. break]]
- [[#6. continue|6. continue]]
- [[#7. Labeled break and continue|7. Labeled break and continue]]
- [[#8. Nested Loops and Loop Variable Scope|8. Nested Loops and Loop Variable Scope]]
- [[#9. Infinite Loops — Intentional and Accidental|9. Infinite Loops — Intentional and Accidental]]
- [[#10. Common Pitfalls|10. Common Pitfalls]]
- [[#11. Summary|11. Summary]]

---

## 1. The `while` Loop

Checks the condition **before** each iteration, including the first. If the condition is `false` to begin with, the body never runs at all.

```java
int i = 0;
while (i < 5) {
    System.out.println(i);
    i++;
}
// prints 0 1 2 3 4
```

```java
int i = 10;
while (i < 5) {
    System.out.println(i);   // never runs — condition is false on entry
}
```

As with `if`, the condition must be a `boolean` expression — an `int` cannot be used directly as a loop condition in Java.

---

## 2. The `do-while` Loop

Checks the condition **after** each iteration, so the body always runs at least once, even if the condition is `false` from the start.

```java
int i = 10;
do {
    System.out.println(i);   // runs once, prints 10
    i++;
} while (i < 5);
```

This makes `do-while` a good fit for situations that are naturally "do this, then decide whether to repeat" — a classic example is reading user input, where you need at least one prompt before there's anything to check:

```java
Scanner scanner = new Scanner(System.in);
String input;
do {
    System.out.print("Enter a command (or 'quit'): ");
    input = scanner.nextLine();
} while (!input.equals("quit"));
```

> [!warning] Don't forget the trailing semicolon
> `do-while` is the only loop form that ends with a `;` after the `while (...)` clause. Omitting it is a compile error; including it on the other loop forms is also a compile error (it would create an empty-body loop — see [[#10. Common Pitfalls|Common Pitfalls]]).

---

## 3. The `for` Loop

Bundles initialization, condition, and update into one header — most useful when the number of iterations is known or driven by a counter.

```java
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}
```

The header has three clauses, each optional, separated by `;`:

```java
for (initialization; condition; update) {
    // body
}
```

1. **Initialization** runs once, before the loop starts.
2. **Condition** is checked before each iteration (including the first) — same timing as `while`.
3. **Update** runs after each iteration's body, before the condition is checked again.

Multiple variables can be initialized and updated in a single header, separated by commas:

```java
for (int i = 0, j = 10; i < j; i++, j--) {
    System.out.println(i + " " + j);
}
```

All three clauses are optional. Omitting all of them produces an infinite loop (see [[#9. Infinite Loops — Intentional and Accidental|section 9]]):

```java
for (;;) {
    // runs forever unless a break (or return/exception) exits it
}
```

A variable declared in the initialization clause is scoped to the loop — it does not exist outside the `for` block:

```java
for (int i = 0; i < 5; i++) { }
// System.out.println(i);   // compile error: i cannot be resolved
```

---

## 4. The Enhanced `for` Loop (for-each)

Iterates directly over the elements of an array or anything implementing `Iterable` (`List`, `Set`, etc.), without an explicit index or `Iterator`.

```java
int[] numbers = {10, 20, 30};
for (int n : numbers) {
    System.out.println(n);
}

List<String> names = List.of("Alice", "Bob", "Carol");
for (String name : names) {
    System.out.println(name);
}
```

Read the syntax as "for each `n` in `numbers`." Internally, this desugars to an `Iterator` (for `Iterable` types) or an index-based loop (for arrays) — but neither is visible or accessible from the enhanced `for` syntax itself.

> [!warning] The loop variable is a copy, not a reference to the slot
> For primitives and for object references alike, the for-each variable holds a **copy** of each element as it's visited. Reassigning it inside the loop body does not modify the original array or collection:
> ```java
> int[] numbers = {1, 2, 3};
> for (int n : numbers) {
>     n = n * 10;   // only changes the local copy
> }
> System.out.println(numbers[0]);   // still 1, unchanged
> ```
> To mutate elements in place, use an index-based `for` loop instead.

Enhanced `for` also cannot access an index, iterate backward, or skip by a step other than one — any of those requirements calls for a traditional `for` loop instead.

---

## 5. `break`

Immediately exits the nearest enclosing loop (or `switch`), skipping any remaining iterations.

```java
for (int i = 0; i < 10; i++) {
    if (i == 5) {
        break;
    }
    System.out.println(i);
}
// prints 0 1 2 3 4, then exits the loop entirely when i == 5
```

`break` is also the standard way to give an otherwise-infinite loop a real exit condition — see [[#9. Infinite Loops — Intentional and Accidental|section 9]].

---

## 6. `continue`

Skips the rest of the **current** iteration's body and jumps straight to the next one — for a `for` loop, that means the update clause still runs before the condition is re-checked; for `while`/`do-while`, control jumps straight to the condition check.

```java
for (int i = 0; i < 10; i++) {
    if (i % 2 != 0) {
        continue;   // skip printing odd numbers
    }
    System.out.println(i);
}
// prints 0 2 4 6 8
```

> [!info] `continue` does not stop the loop
> Unlike `break`, `continue` doesn't exit the loop — it only skips the remainder of the current pass. The loop's own condition still governs whether another iteration happens.

---

## 7. Labeled `break` and `continue`

By default, `break` and `continue` act on the **nearest enclosing** loop only. A label lets either statement target an outer loop directly, which is useful when a decision made in an inner loop needs to affect an outer one.

```java
outer:
for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
        if (j == 1) {
            continue outer;   // skips to the next i, not just the next j
        }
        System.out.println(i + "," + j);
    }
}
```

```
0,0
1,0
2,0
```

Without the label, `continue` (or `break`) would only affect the inner `j` loop:

```java
for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
        if (j == 1) {
            break;   // exits only the inner loop; i keeps incrementing normally
        }
        System.out.println(i + "," + j);
    }
}
```

```
0,0
1,0
2,0
```

> [!tip] Both examples above print the same output
> They arrive at it differently: `continue outer` skips straight to the next `i` from inside the inner loop, while the unlabeled `break` exits the inner loop and lets the outer loop's own natural iteration continue. The distinction matters more once there's code *after* the inner loop, inside the outer loop's body — the unlabeled `break` would still run that code, while `continue outer` would skip it.

A label is any identifier followed by `:`, placed immediately before the loop it names. Labeled `break` also works on nested `for`, `while`, and `do-while` loops — not just doubly-nested `for` as shown here.

---

## 8. Nested Loops and Loop Variable Scope

Loop variables are scoped to their own loop, so the same variable name can be reused at each nesting level without conflict:

```java
for (int i = 0; i < 3; i++) {
    for (int i2 = 0; i2 < 2; i2++) {   // must use a different name than the outer i in the same scope chain
        System.out.println(i + ":" + i2);
    }
}
```

Note that Java does not allow shadowing a loop variable with the *same* name in a directly nested scope — `for (int i = 0; ...) { for (int i = 0; ...) }` is a compile error, unlike some languages that permit shadowing. Each level needs a distinct variable name.

---

## 9. Infinite Loops — Intentional and Accidental

A loop with no exit condition, or one whose condition never becomes `false`, runs forever. This is sometimes intentional — for example, a server's main request-handling loop — and always requires an explicit exit path via `break`, `return`, or an exception:

```java
while (true) {
    String command = readNextCommand();
    if (command.equals("quit")) {
        break;
    }
    process(command);
}
```

More often, an infinite loop is accidental — the loop variable is never updated, or is updated in a way that never satisfies the exit condition:

```java
int i = 0;
while (i < 5) {
    System.out.println(i);
    // forgot i++ — this loop never terminates
}
```

---

## 10. Common Pitfalls

- **A stray semicolon creates an empty-body loop.** This is one of the most common loop bugs, because it compiles cleanly and produces no error — the loop just does nothing useful, or spins forever:

```java
for (int i = 0; i < 5; i++); {
    System.out.println(i);   // NOT part of the loop — runs once, after the (empty) loop finishes
}
```

> [!info]- Why does this compile without errors?
> The `;` immediately after `(...)` is itself a complete (empty) statement — that's the loop's entire body. The `{ ... }` block that follows is just an ordinary block that runs once, after the loop has already finished all five iterations doing nothing. This also means `i` is out of scope inside that block, since it was declared in the now-finished `for` header — so the code above wouldn't even compile as written; a version using a variable declared before the loop would run once and silently skip the intended five prints.

- **Off-by-one errors from `<` vs. `<=`.** `for (int i = 0; i <= array.length; i++)` runs one iteration too many and throws `ArrayIndexOutOfBoundsException` on the last pass; the correct bound for a zero-indexed array is `i < array.length`.
- **Modifying a collection while iterating it with enhanced `for`.** Adding or removing elements from a `List` during a for-each loop over it throws `ConcurrentModificationException` at runtime — use an explicit `Iterator`'s own `remove()` method, or build a separate collection of changes to apply after the loop.
- **Expecting the for-each variable to mutate the source.** Covered in [[#4. The Enhanced for Loop (for-each)|section 4]] — reassigning the loop variable only changes the local copy, never the underlying array or collection element.
- **Forgetting that `continue` doesn't skip the `for` loop's update clause.** In a `for` loop, `continue` still runs the update expression (e.g. `i++`) before re-checking the condition — it does not restart the header from the initialization.

---

## 11. Summary

- `while` checks its condition before each pass, so the body may run zero times; `do-while` checks after, so the body always runs at least once.
- `for` bundles initialization, condition, and update into one header, each clause optional — `for (;;)` is a common intentional infinite loop.
- Enhanced `for` iterates elements of an array or `Iterable` directly, but only exposes a **copy** of each element and cannot index, step, or go backward.
- `break` exits the nearest enclosing loop entirely; `continue` skips only the rest of the current iteration. A label (`outer: for (...)`) lets either target an outer loop from inside a nested one.
- A stray `;` right after a loop header silently creates an empty-body loop — one of the easiest loop bugs to introduce and the hardest to spot by eye.
- Any loop needs a real path to `false` (or a `break`/`return`/exception) — forgetting to update the condition variable is the most common cause of an accidental infinite loop.
