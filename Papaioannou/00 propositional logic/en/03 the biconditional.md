---
tags:
  - uni/επλ-111/propositional-logic/en
---

## Definition

> Let $P$ and $Q$ be propositions. The statement "$P$ if and only if $Q$" is also a proposition, called the biconditional and written $P \leftrightarrow Q$.

| $P$ | $Q$ | $P \leftrightarrow Q$ |
|---|---|---|
| T | T | T |
| T | F | F |
| F | T | F |
| F | F | T |

- True when $P$ and $Q$ have the same truth value, false when they differ.
- It is the negation of [[01 logical operators|exclusive or]]: $P \leftrightarrow Q \equiv \lnot(P \oplus Q)$.
- The same note in Greek: [[03 συνεπαγωγή διπλής κατεύθυνσης|συνεπαγωγή διπλής κατεύθυνσης]].

## Example

- $P$: he can board the plane. $Q$: he has bought a ticket.
- $P \leftrightarrow Q$: he can board the plane if and only if he has bought a ticket.
- Both directions are claimed at once. A ticket guarantees boarding, and no ticket guarantees no boarding. Compare with [[02 implication|$P \to Q$]] alone, which would leave open the case of boarding without a ticket.

## The 4 ways to say it

All of these are $P \leftrightarrow Q$:

- $P$ if and only if $Q$
- $P$ iff $Q$ — the contracted form, used in writing
- $P$ is necessary and sufficient for $Q$
- If $P$ then $Q$, and conversely

- The third spells out the structure: [[02 implication|necessary and sufficient]] together is exactly an implication in each direction.

## In terms of the other operators

- $P \leftrightarrow Q \equiv (P \to Q) \land (Q \to P)$ — an implication in each direction, which is where the name comes from.
- $P \leftrightarrow Q \equiv (\lnot P \lor Q) \land (P \lor \lnot Q)$, after applying the definition of implication to each half. This is the form used in [[07 functional completeness|functional completeness]].
- $P \leftrightarrow Q \equiv (P \land Q) \lor (\lnot P \land \lnot Q)$ — the 2 rows where the table is true, written out directly.
- Every mathematical definition is a biconditional, which is why proving one means proving 2 implications. That is the practical reason this operator matters more than its truth table suggests.

## Not the same as $\equiv$

- $P \leftrightarrow Q$ is a proposition built inside the language, with its own truth table; it can be true on some rows and false on others.
- $P \equiv Q$ is a claim made about 2 propositions from outside the language: it says $P \leftrightarrow Q$ is a tautology, true on every row.
- So $\leftrightarrow$ is an operator and $\equiv$ is not. Writing $\equiv$ inside a formula is a category error, the same way $\models$ is not a connective.
- See [[06 propositional equivalences|propositional equivalences]].
