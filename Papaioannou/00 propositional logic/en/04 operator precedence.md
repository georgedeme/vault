---
tags:
  - uni/επλ-111/propositional-logic/en
---

## Overview

- Compound propositions are built from simpler ones using the [[01 logical operators|logical operators]], and once more than 1 operator appears the expression needs a single agreed reading.
- Ambiguity is not permitted in logic, or in mathematics generally.
- Parentheses always settle the order in which operators apply. Precedence rules exist only so that readable expressions do not need parentheses everywhere.
- The same note in Greek: [[04 προτεραιότητα τελεστών|προτεραιότητα τελεστών]].

## Why it matters

- What does $\lnot P \land Q$ mean? There are 2 candidate readings, and they are different propositions:

| $P$ | $Q$ | $(\lnot P) \land Q$ | $\lnot (P \land Q)$ |
|---|---|---|---|
| T | T | F | F |
| T | F | F | T |
| F | T | T | T |
| F | F | F | T |

- The 2 columns disagree on 2 of the 4 rows, so the reading has to be fixed by a rule rather than left to the reader.

## The precedence table

| operator | precedence |
|---|---|
| $\lnot$ negation | 1 |
| $\land$ conjunction | 2 |
| $\lor$ disjunction | 3 |
| $\oplus$ exclusive or | 4 |
| $\to$ implication | 5 |
| $\leftrightarrow$ biconditional | 6 |

- 1 binds tightest. $\lnot$ applies to as little as possible, $\leftrightarrow$ to as much as possible.
- The order is worth remembering by what it mirrors: $\lnot$ behaves like a minus sign, $\land$ like multiplication, $\lor$ like addition, and $\to$ like a relation sign such as $=$, which is why it comes near the end.

![[precedence of logical operators (Excalidraw).excalidraw]]

## Worked readings

- $\lnot P \land Q$ is $(\lnot P) \land Q$.
- $P \lor Q \land \lnot R$ is $P \lor (Q \land (\lnot R))$.
- $P \lor Q \to R$ is $(P \lor Q) \to R$.
- $P \to Q \to R$ is $(P \to Q) \to R$ — the course reads a chain of equal-precedence operators left to right.

## The one to parenthesize anyway

- Most logic texts, and the [[00 math/11 mathematical logic & proof/06 propositional logic|math module note]], take $\to$ to be right-associative, so that $P \to Q \to R$ means $P \to (Q \to R)$.
- These are not the same proposition. With $P$ false and $R$ false, $(P \to Q) \to R$ is false and $P \to (Q \to R)$ is true.
- Use the course convention in ΕΠΛ 111, and write the parentheses in anything of your own rather than relying on either.
- $\land$, $\lor$, $\oplus$ and $\leftrightarrow$ are all associative, so chains of those read the same whichever way they are grouped. $\to$ is the only one where it matters.
