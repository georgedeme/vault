---
tags:
  - uni/επλ-111/propositional-logic/en
---

## Overview

- Are all 6 [[01 logical operators|logical operators]] actually needed? No — 3 of them are already definable from the other 3.
- $P \oplus Q \equiv (P \land \lnot Q) \lor (\lnot P \land Q)$
- $P \to Q \equiv \lnot P \lor Q$
- $P \leftrightarrow Q \equiv (\lnot P \lor Q) \land (P \lor \lnot Q)$
- Each of these is an [[06 propositional equivalences|equivalence]] provable by truth table, so $\oplus$, $\to$ and $\leftrightarrow$ are conveniences rather than necessities.
- The same note in Greek: [[07 συναρτησιακή πληρότητα|συναρτησιακή πληρότητα]].

## Definition

> A collection of logical operators $\Sigma$ is functionally complete when every compound proposition is equivalent to some compound proposition that uses only operators from $\Sigma$.

- The question is about expressive power, not about convenience. A complete set can say everything, however awkwardly.
- Equivalently: every truth table over $n$ inputs — and there are $2^{2^n}$ of them — must be writable using only $\Sigma$.

## Is $\{\lnot, \land, \lor\}$ complete

Yes, and the proof is a construction that reads a formula straight off any truth table.

| $P$ | $Q$ | $R$ | $S$ | |
|---|---|---|---|---|
| T | T | T | T | $P \land Q \land R$ |
| T | T | F | F | |
| T | F | T | T | $P \land \lnot Q \land R$ |
| T | F | F | F | |
| F | T | T | F | |
| F | T | F | F | |
| F | F | T | T | $\lnot P \land \lnot Q \land R$ |
| F | F | F | F | |

- Take each row where the target column is T, and write the conjunction of the propositions in that row, negated wherever the row has F. That conjunction is true on that row and false on every other.
- Join those conjunctions with $\lor$. The result is true on exactly the rows the table marks T.
- $S \equiv (P \land Q \land R) \lor (P \land \lnot Q \land R) \lor (\lnot P \land \lnot Q \land R)$
- The construction works for any table at all, which is the proof. Its output is [[00 math/11 mathematical logic & proof/06 propositional logic|disjunctive normal form]], the same shape as sum-of-products in [[00 math/07 discrete mathematics/04 boolean algebra & logic circuits/00 boolean algebra basics|boolean algebra]].
- The 1 table it cannot handle directly is the all-F column, which has no true rows to collect; that one is written $\mathbf{F}$, or $P \land \lnot P$.
- The formula it produces is rarely the smallest one. Every true row here has $R$ true, and among the rows with $R$ true the only false one is $P$ false with $Q$ true, so $S \equiv R \land (P \lor \lnot Q)$ — 3 literals instead of 9. [[00 math/07 discrete mathematics/04 boolean algebra & logic circuits/02 Karnaugh maps|Karnaugh maps]] do this minimization systematically.

## Is $\{\lnot, \land\}$ complete

- Yes. From De Morgan and double negation, $P \lor Q \equiv \lnot(\lnot P \land \lnot Q)$.
- So every $\lor$ in the construction above can be rewritten away, leaving only $\lnot$ and $\land$.

## Is $\{\lnot, \lor\}$ complete

- Yes, by the mirror argument: $P \land Q \equiv \lnot(\lnot P \lor \lnot Q)$.
- $\{\lnot, \to\}$ is complete too, since $P \lor Q \equiv \lnot P \to Q$.

## The limit

- $\{\land, \lor\}$ is not complete. Both operators return T when every input is T, so any formula built from them alone is true on the all-T row, and $\lnot P$ is not. No amount of nesting escapes that.
- The argument generalizes: a property preserved by every operator in $\Sigma$, and not held by some target formula, proves $\Sigma$ incomplete.
- Going the other way, NAND on its own is complete, and so is NOR — $\lnot P \equiv P \uparrow P$ and $P \land Q \equiv (P \uparrow Q) \uparrow (P \uparrow Q)$, where $\uparrow$ is NAND. That is why a chip can be built from [[00 math/07 discrete mathematics/04 boolean algebra & logic circuits/01 logic gates & circuits|1 repeated gate type]].
- NAND and NOR are the only 2 binary operators that are complete on their own.
