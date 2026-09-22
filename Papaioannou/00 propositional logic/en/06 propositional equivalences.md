---
tags:
  - uni/επλ-111/propositional-logic/en
---

## Overview

- An important step in a mathematical argument is replacing a proposition with an equivalent one — a proposition that says the same thing in a more usable shape.
- That is the whole job of this note: what "the same thing" means precisely, and the 2 methods for proving it.
- The same note in Greek: [[06 προτασιακές ισοδυναμίες|προτασιακές ισοδυναμίες]].

## Definitions

> A compound proposition is a tautology if it is always true — $P \lor \lnot P$.
> A compound proposition is a contradiction if it is always false — $P \land \lnot P$.

> 2 propositions $P$ and $Q$ are logically equivalent, written $P \equiv Q$, if the proposition $P \leftrightarrow Q$ is a tautology.

- A proposition that is neither is a contingency — true on some rows and false on others, the ordinary case.
- Notation: a compound proposition that is a tautology is written $\mathbf{T}$, and one that is a contradiction is written $\mathbf{F}$. These are the same 2 symbols as the truth values, used as propositions.
- $\equiv$ is not an operator. $\leftrightarrow$ builds a proposition inside the language; $\equiv$ is a claim made about 2 propositions from outside it.
- $P$ is a tautology exactly when $\lnot P$ is a contradiction, so the 2 notions are 1 notion seen from either side.

| | true on | example |
|---|---|---|
| tautology | every row | $P \lor \lnot P$ |
| contingency | some rows | $P \to Q$ |
| contradiction | no row | $P \land \lnot P$ |

## Method A — truth tables

- Build 1 table with a column for $P$ and a column for $Q$. They are equivalent if the 2 columns agree on every row.
- Mechanical, and it always terminates.
- The drawback: a compound proposition over $N$ propositions needs $2^N$ rows, 1 for each combination of T and F. 10 propositions is 1024 rows, 20 is over a million.

## Method B — logical laws

- Rewrite 1 side step by step using known equivalences until it becomes the other, naming the law used at each step.
- The cost does not grow with the number of propositions, which is why it is the method that scales.

| equivalence | name |
|---|---|
| $P \land \mathbf{T} \equiv P$, $P \lor \mathbf{F} \equiv P$ | identity laws |
| $P \lor \mathbf{T} \equiv \mathbf{T}$, $P \land \mathbf{F} \equiv \mathbf{F}$ | domination laws |
| $P \lor P \equiv P$, $P \land P \equiv P$ | idempotent laws |
| $\lnot(\lnot P) \equiv P$ | double negation |
| $P \lor Q \equiv Q \lor P$, $P \land Q \equiv Q \land P$ | commutative laws |
| $(P \lor Q) \lor R \equiv P \lor (Q \lor R)$, $(P \land Q) \land R \equiv P \land (Q \land R)$ | associative laws |
| $P \lor (Q \land R) \equiv (P \lor Q) \land (P \lor R)$, $P \land (Q \lor R) \equiv (P \land Q) \lor (P \land R)$ | distributive laws |
| $\lnot(P \land Q) \equiv \lnot P \lor \lnot Q$, $\lnot(P \lor Q) \equiv \lnot P \land \lnot Q$ | De Morgan's laws |

- The lecture's table stops there, but 3 more are worth adding. The negation laws and the definition of implication are used inside its own worked proofs; the absorption laws sit alongside them because they fall out of distributivity:

| equivalence | name |
|---|---|
| $P \lor \lnot P \equiv \mathbf{T}$, $P \land \lnot P \equiv \mathbf{F}$ | negation laws |
| $P \lor (P \land Q) \equiv P$, $P \land (P \lor Q) \equiv P$ | absorption laws |
| $P \to Q \equiv \lnot P \lor Q$, $Q \to P \equiv \lnot Q \lor P$ | definition of implication |

- 3 more, proved by truth table, complete the working set:

| equivalence | name |
|---|---|
| $P \to Q \equiv \lnot Q \to \lnot P$ | contrapositive |
| $P \oplus Q \equiv (P \land \lnot Q) \lor (\lnot P \land Q)$ | definition of exclusive or |
| $P \leftrightarrow Q \equiv (P \to Q) \land (Q \to P)$ | definition of the biconditional |

- These are the same laws as in [[00 math/07 discrete mathematics/04 boolean algebra & logic circuits/00 boolean algebra basics|boolean algebra]], under a second set of symbols: $\land$ is $\cdot$, $\lor$ is $+$, $\mathbf{T}$ is 1 and $\mathbf{F}$ is 0.
- Each law comes in a pair, and the 2 halves are duals: swap $\land$ with $\lor$ and $\mathbf{T}$ with $\mathbf{F}$ and 1 half becomes the other. Remembering 1 of each pair is enough.

## $P$, $Q$ and $R$ are slots

- Every law above is a schema, not a claim about 3 particular propositions. Any proposition goes in a slot, atomic or compound.
- The only rule is that substitution is uniform: whatever goes in the $P$ slot goes in every occurrence of $P$, on both sides.
- Nothing requires the propositions to be distinct. $Q = P$ is allowed, $R = P$ is allowed, and so is the literally same proposition in both slots of a binary operator.
- $P \to P$ is the example to hold on to: well formed, and in fact a tautology. Its table has 2 rows, not 4, and gives T on both — with $P$ true both hypothesis and conclusion hold, with $P$ false the implication is vacuously true.
- The table of laws already does this. The idempotent laws are $P \lor P \equiv P$, the same proposition in both slots, and the negation laws are the case $Q = \lnot P$. If distinct propositions were required, neither could be written down.
- The reason is that operators are [[01 logical operators|truth-functional]]: each is a function from truth values to a truth value, and a function does not break when handed the same argument twice, the way $\min(3,3) = 3$ does not.
- The absorption laws are exactly that case: distributivity with $R = P$ gives $P \lor (Q \land P) \equiv (P \lor Q) \land (P \lor P) \equiv (P \lor Q) \land P \equiv P$. So do the worked proofs below, where De Morgan is applied with $\lnot P$ in the $P$ slot and with the whole of $\lnot P \land Q$ in the $Q$ slot.
- Distinctness matters in 1 place only, and that is usually where the confusion starts: $2^N$ counts distinct atomic propositions, so with $Q = P$ the table for $P \to Q$ drops from 4 rows to 2.
- Substitution preserves validity, not contingency. A law with $\equiv$ still holds after any substitution, while a contingent proposition can collapse into a tautology: $P \to Q$ is contingent, $P \to P$ is a tautology. That $P \to P$ says nothing useful is a judgement about usefulness, not correctness.

## Worked proof — a tautology

$(P \land Q) \to (P \lor Q) \equiv \mathbf{T}$

| step | law |
|---|---|
| $(P \land Q) \to (P \lor Q)$ | |
| $\equiv \lnot(P \land Q) \lor (P \lor Q)$ | definition of implication |
| $\equiv (\lnot P \lor \lnot Q) \lor (P \lor Q)$ | De Morgan |
| $\equiv (\lnot P \lor P) \lor (\lnot Q \lor Q)$ | commutativity and associativity |
| $\equiv \mathbf{T} \lor \mathbf{T}$ | negation laws |
| $\equiv \mathbf{T}$ | domination |

## Worked proof — a simplification

$\lnot(P \lor (\lnot P \land Q)) \equiv \lnot P \land \lnot Q$

| step | law |
|---|---|
| $\lnot(P \lor (\lnot P \land Q))$ | |
| $\equiv \lnot P \land \lnot(\lnot P \land Q)$ | De Morgan |
| $\equiv \lnot P \land (\lnot(\lnot P) \lor \lnot Q)$ | De Morgan |
| $\equiv \lnot P \land (P \lor \lnot Q)$ | double negation |
| $\equiv (\lnot P \land P) \lor (\lnot P \land \lnot Q)$ | distributivity |
| $\equiv \mathbf{F} \lor (\lnot P \land \lnot Q)$ | negation laws |
| $\equiv \lnot P \land \lnot Q$ | identity |

## Practice set from the lecture

Prove each pair equivalent by truth table:

- $P \to Q$ and $\lnot Q \to \lnot P$ — the contrapositive of $P \to Q$.
- $P \to Q$ and $\lnot P \lor Q$ — the definition of implication.
- $P \oplus Q$ and $(P \land \lnot Q) \lor (\lnot P \land Q)$ — the definition of exclusive or.
- $\lnot(P \lor Q)$ and $\lnot P \land \lnot Q$ — De Morgan's law.
- $P \lor (Q \land R)$ and $(P \lor Q) \land (P \lor R)$ — distributivity. The slide labels this one associativity, but distributing $\lor$ over $\land$ is a distributive law; the table above has it in the right row.

## Satisfiability

- Worth naming alongside the 2 definitions above, because the course returns to it: a proposition is satisfiable if at least 1 row of its truth table makes it true.
- Tautology means every row, satisfiable means at least 1, contradiction means none.
- $P$ is a tautology if and only if $\lnot P$ is unsatisfiable, which is the propositional core of proof by contradiction.
- See [[00 math/11 mathematical logic & proof/06 propositional logic|propositional logic]] for satisfiability, normal forms and the connection to SAT.
