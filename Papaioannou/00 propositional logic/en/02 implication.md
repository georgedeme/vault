---
tags:
  - uni/επλ-111/propositional-logic/en
---

## Definition

> Let $P$ and $Q$ be propositions. The statement "$P$ implies $Q$" is also a proposition, called the implication and written $P \to Q$. $P$ is the hypothesis and $Q$ is the conclusion.

| $P$ | $Q$ | $P \to Q$ |
|---|---|---|
| T | T | T |
| T | F | F |
| F | T | T |
| F | F | T |

- False in exactly 1 case: hypothesis true and conclusion false. Every other row is true.
- Also called the conditional; see [[00 math/11 mathematical logic & proof/00 conditional statements, converse & contrapositive|conditional statements, converse & contrapositive]].
- The same note in Greek: [[02 συνεπαγωγή|συνεπαγωγή]].

## Why that table

- Read $P \to Q$ as a promise. The promise is broken only when the hypothesis happens and the conclusion does not.
- The lecture's example: "if you score 100% on the final exam, then you get a final grade of 10".
- You feel cheated in exactly 1 scenario — you scored 100% and did not get a 10. That is the row with hypothesis true and conclusion false.
- Score less than 100% and the promise said nothing about your grade, so nothing can break it, whatever grade you end up with. Both of those rows are true.

## Vacuous truth

- When the hypothesis is false the implication is true regardless of the conclusion. This is called vacuous truth, and it is the source of most confusion about $\to$.
- $P$: today is Friday. $Q$: $2+3=5$. $R$: $2+3=6$.
- $P \to Q$ is true by definition, since the conclusion is true on every row.
- $P \to R$ is true every day except Friday. On Friday the hypothesis holds and the conclusion is false, so the implication fails.
- There is no requirement that $P$ and $Q$ have anything to do with each other. $\to$ is a truth function, not a claim about causation.
- This is why "every element of the empty set is blue" is true. There is no element to make the hypothesis hold, so nothing can falsify it.

## The 4 ways to say it

All of these are $P \to Q$:

- $P$ implies $Q$
- If $P$, then $Q$
- $P$ is sufficient for $Q$
- $P$ only if $Q$ — that is, $P$ cannot be true when $Q$ is not true

- "$P$ only if $Q$" is the one that trips people up, because the English word order puts $Q$ second while the condition it states is a necessary one. Check it against the table rather than against intuition: the only forbidden combination is $P$ true with $Q$ false, which is exactly what "$P$ cannot be true when $Q$ is not" says.
- Equivalently, $Q$ is necessary for $P$. Sufficient points forward along the arrow, necessary points backward: in $P \to Q$, $P$ is sufficient and $Q$ is necessary.
- Contrast with [[03 the biconditional|$P$ if and only if $Q$]], which claims both directions and is strictly stronger.

## Converse, inverse, contrapositive

| name | formula |
|---|---|
| implication | $P \to Q$ |
| converse | $Q \to P$ |
| inverse | $\lnot P \to \lnot Q$ |
| contrapositive | $\lnot Q \to \lnot P$ |

| $P$ | $Q$ | $P \to Q$ | $Q \to P$ | $\lnot P \to \lnot Q$ | $\lnot Q \to \lnot P$ |
|---|---|---|---|---|---|
| T | T | T | T | T | T |
| T | F | F | T | T | F |
| F | T | T | F | F | T |
| F | F | T | T | T | T |

- Only the contrapositive column matches the original, so $P \to Q \equiv \lnot Q \to \lnot P$ and nothing else here does.
- The converse and the inverse match each other, which is no accident: each is the other's contrapositive.
- Treating a true implication as if its converse followed is the single most common error in the course, and it has a name — affirming the consequent.

## Rewriting the arrow away

- $P \to Q \equiv \lnot P \lor Q$ is the definition of implication, used constantly in [[06 propositional equivalences|equivalence proofs]].
- Reading it back out: either the hypothesis fails, or the conclusion holds. That is the whole content of the arrow.
- Negating an implication therefore gives $\lnot(P \to Q) \equiv P \land \lnot Q$ — a conjunction, not another implication. The negation of "if it rains I stay in" is "it rains and I do not stay in".
