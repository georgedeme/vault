---
tags:
  - uni/επλ-111/propositional-logic/en
---

## Overview

- Sentences in natural language are often ambiguous. Translating them into logical propositions removes the ambiguity.
- Once translated, rules of inference can be applied to draw valid conclusions.
- Some reasonable assumptions may be needed, based on the intended meaning of the sentence rather than its literal words.
- The same note in Greek: [[05 μετάφραση προτάσεων φυσικής γλώσσας|μετάφραση προτάσεων φυσικής γλώσσας]].

## Method

- Break the sentence into its component propositions, and name each one $P$, $Q$, $R$, …
- Look for the [[01 logical operators|logical operators]] connecting them, including the ones hiding in words like "unless", "only", "cannot" and "neither".
- Assemble the formula, adding parentheses where [[04 operator precedence|precedence]] would give the wrong reading.
- Each component should be an atomic proposition with no operator left inside it, and should be phrased positively, so that any negation shows up explicitly as $\lnot$.

## Words that carry an operator

| English | formula |
|---|---|
| $P$ and $Q$; $P$ but $Q$; both | $P \land Q$ |
| $P$ or $Q$ | $P \lor Q$ |
| either $P$ or $Q$ but not both | $P \oplus Q$ |
| if $P$ then $Q$; $P$ only if $Q$; $P$ is sufficient for $Q$ | $P \to Q$ |
| $P$ if $Q$; $P$ is necessary for $Q$ | $Q \to P$ |
| $P$ if and only if $Q$; exactly when | $P \leftrightarrow Q$ |
| $P$ unless $Q$ | $\lnot Q \to P$ |
| neither $P$ nor $Q$ | $\lnot P \land \lnot Q$ |
| not both $P$ and $Q$ | $\lnot(P \land Q)$ |

- "but" and "and" translate identically. The contrast it carries is not truth-functional, so logic throws it away.
- "$P$ if $Q$" and "$P$ only if $Q$" point the arrow in opposite directions. This pair causes more mistakes than anything else in the table.
- "neither nor" and "not both" are the 2 [[06 propositional equivalences|De Morgan]] shapes, and mixing them up flips the answer.

## Example 1

> If I go to the mountain or to the sea, then I will not go shopping

- $P$: I will go to the mountain.
- $Q$: I will go to the sea.
- $R$: I will go shopping.
- "If $P$ or $Q$ then not $R$" gives $(P \lor Q) \to \lnot R$.
- The parentheses are redundant under the [[04 operator precedence|precedence table]], since $\lor$ binds tighter than $\to$, and are worth writing anyway.

## Example 2

> You cannot ride the rollercoaster if you are under 1.30 unless you are over 16

- $P$: you can ride the rollercoaster.
- $Q$: you are under 1.30.
- $R$: you are over 16.
- Reading it as "$Q$ and not $R$ if and only if not $P$": $(Q \land \lnot R) \leftrightarrow \lnot P$.
- Reading it as "not $Q$ or $R$ if and only if $P$": $(\lnot Q \lor R) \leftrightarrow P$.
- "Unless" is the trap. It introduces an exception to the condition stated before it, which is why $R$ arrives negated on one side or disjoined on the other.
- The biconditional rather than an implication is one of the reasonable assumptions above — the sentence is taken to state the full rule for riding, not just one way to be turned away.

## Checking 2 translations agree

Both readings are the same proposition, which a truth table settles:

| $P$ | $Q$ | $R$ | $(Q \land \lnot R) \leftrightarrow \lnot P$ | $(\lnot Q \lor R) \leftrightarrow P$ |
|---|---|---|---|---|
| T | T | T | T | T |
| T | T | F | F | F |
| T | F | T | T | T |
| T | F | F | T | T |
| F | T | T | F | F |
| F | T | F | T | T |
| F | F | T | F | F |
| F | F | F | F | F |

- The 2 columns agree on all 8 rows, so the formulas are [[06 propositional equivalences|logically equivalent]].
- Note that neither is a tautology. Equivalence means the columns match, not that they are all T.
- The 2 are related by contraposition inside the biconditional: $Q \land \lnot R$ and $\lnot Q \lor R$ are negations of each other by De Morgan, and negating both sides of a biconditional leaves it unchanged.
