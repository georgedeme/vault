---
tags:
  - uni/επλ-111/propositional-logic/en
---

## Overview

- Logical operators build new compound propositions out of simpler ones that are already available.
- The course uses 6: negation, conjunction, disjunction, exclusive or, [[02 implication|implication]] and [[03 the biconditional|the biconditional]].
- Negation is unary — it builds a new proposition from 1 existing proposition. The other 5 are binary and take 2.
- Every one of them is truth-functional: the truth value of the whole is fixed by the truth values of its parts, which is exactly what makes a truth table a complete check rather than a sample.
- The same note in Greek: [[01 λογικοί τελεστές|λογικοί τελεστές]].

## Truth tables

> A truth table shows the relation between the truth values of propositions.

- It is the tool for computing the truth value of a compound proposition from the values of the simpler propositions inside it.
- A compound proposition over $N$ distinct propositions needs $2^N$ rows, 1 for each combination of T and F.
- Conventional row order counts down from all-T, with the leftmost column changing slowest.
- See [[00 math/11 mathematical logic & proof/01 truth tables & logical equivalence|truth tables & logical equivalence]] for the same tables in the math module.

## All 6 operators at once

| $P$ | $Q$ | $\lnot P$ | $P \land Q$ | $P \lor Q$ | $P \oplus Q$ | $P \to Q$ | $P \leftrightarrow Q$ |
|---|---|---|---|---|---|---|---|
| T | T | F | T | T | F | T | T |
| T | F | F | F | T | T | F | F |
| F | T | T | F | T | T | T | F |
| F | F | T | F | F | F | T | T |

- Worth memorizing as a block. Each column below is the same table one operator at a time, with the wording and the examples.
- Read across the $P \land Q$ column: 1 T. Across $P \lor Q$: 1 F. Across $P \to Q$: 1 F, in the second row.

## Negation

> Let $P$ be a proposition. The statement "it is not the case that $P$" is also a proposition, called the negation of $P$ and written $\lnot P$.

| $P$ | $\lnot P$ |
|---|---|
| T | F |
| F | T |

- $P$: today is Friday. The negation of $P$ is "it is not the case that today is Friday", more simply "today is not Friday".
- The clumsy "it is not the case that" form is the safe one. Moving the "not" into the sentence is a simplification, and it goes wrong the moment the sentence contains a quantifier.

## Conjunction

> Let $P$ and $Q$ be propositions. The statement "$P$ and $Q$" is also a proposition, called the conjunction of $P$ and $Q$ and written $P \land Q$.

| $P$ | $Q$ | $P \land Q$ |
|---|---|---|
| T | T | T |
| T | F | F |
| F | T | F |
| F | F | F |

- True only when both propositions are true.
- $P$: today is Friday. $Q$: it is raining today. $P \land Q$: today is Friday and it is raining.
- So $P \land Q$ is true on rainy Fridays, and false on any day that is not a Friday and on Fridays with no rain.

## Disjunction

> Let $P$ and $Q$ be propositions. The statement "$P$ or $Q$" is also a proposition, called the disjunction of $P$ and $Q$ and written $P \lor Q$.

| $P$ | $Q$ | $P \lor Q$ |
|---|---|---|
| T | T | T |
| T | F | T |
| F | T | T |
| F | F | F |

- True when at least 1 of the propositions is true. This is the inclusive or, not the everyday either-or.
- With the same $P$ and $Q$: $P \lor Q$ is "today is Friday or it is raining", true on any day that is a Friday or has rain, rainy Fridays included.

## Exclusive or

> Let $P$ and $Q$ be propositions. The statement "either $P$ or $Q$" is also a proposition, called the exclusive or of $P$ and $Q$ and written $P \oplus Q$.

| $P$ | $Q$ | $P \oplus Q$ |
|---|---|---|
| T | T | F |
| T | F | T |
| F | T | T |
| F | F | F |

- True when exactly 1 of the propositions is true — the one case $\lor$ does not exclude is the one $\oplus$ rules out.
- $P \oplus Q$ is "today is either Friday or raining", true on dry Fridays and on any non-Friday with rain.
- It is the same operator as XOR in [[00 math/07 discrete mathematics/04 boolean algebra & logic circuits/00 boolean algebra basics|boolean algebra]], and $P \oplus Q \equiv \lnot(P \leftrightarrow Q)$.
- $\oplus$ is associative and commutative, so a chain $P_1 \oplus P_2 \oplus \dots \oplus P_n$ is unambiguous and is true exactly when an odd number of its parts are true. That parity reading is why XOR is the operator behind checksums and one-time pads.

## The other 2

- [[02 implication|Implication]], $P \to Q$, and [[03 the biconditional|the biconditional]], $P \leftrightarrow Q$, get their own notes because their truth tables do not match the ordinary reading of the English sentence.
- Once an expression mixes operators, [[04 operator precedence|operator precedence]] decides how it is read.
