---
tags:
  - uni/επλ-111/predicate-logic/en
---

## Overview

- Negation flips the quantifier and moves inside it.
- $\lnot\forall x\, P(x) \equiv \exists x\, \lnot P(x)$
- $\lnot\exists x\, P(x) \equiv \forall x\, \lnot P(x)$
- The quantifier form of [[06 propositional equivalences|De Morgan's laws]].
- See also [[00 math/11 mathematical logic & proof/03 quantifiers & their negation|quantifiers & their negation]].
- The same note in Greek: [[04 άρνηση ποσοδεικτών|άρνηση ποσοδεικτών]].

## Negating $\forall$

$P(x)$: $x$ has taken Discrete Structures. Domain: the students of the class.

| formula | reading |
|---|---|
| $\forall x\, P(x)$ | every student has taken Discrete Structures |
| $\lnot\forall x\, P(x)$ | it is not the case that every student has taken Discrete Structures |
| $\exists x\, \lnot P(x)$ | some student has not taken Discrete Structures |

- Rows 2 and 3 say the same thing.
- Not "no one has taken it" — that is $\forall x\, \lnot P(x)$, far stronger.
- Refuting "everyone": 1 [[02 the universal quantifier|counterexample]].

## Negating $\exists$

Same $P(x)$ and domain.

| formula | reading |
|---|---|
| $\exists x\, P(x)$ | some student has taken Discrete Structures |
| $\lnot\exists x\, P(x)$ | it is not the case that some student has taken Discrete Structures |
| $\forall x\, \lnot P(x)$ | every student has not taken Discrete Structures |

- Rows 2 and 3 say the same thing.
- "Every student has not taken it" means no student has — not "not every student has".
- Refuting "someone": rule out everyone, the [[03 the existential quantifier|hard direction]].

## Why De Morgan

- Finite domain: $\forall$ is a [[01 logical operators|conjunction]], $\exists$ a [[01 logical operators|disjunction]].
- $\lnot\forall x\, P(x) \equiv \lnot(P(a_1) \land \dots \land P(a_n)) \equiv \lnot P(a_1) \lor \dots \lor \lnot P(a_n) \equiv \exists x\, \lnot P(x)$.
- $\lnot\exists x\, P(x) \equiv \lnot(P(a_1) \lor \dots \lor P(a_n)) \equiv \lnot P(a_1) \land \dots \land \lnot P(a_n) \equiv \forall x\, \lnot P(x)$.
- Holds on infinite domains too, as a law of predicate logic.

## Using the rule

- Push $\lnot$ inward 1 quantifier at a time, flipping each — the same for [[06 nested quantifiers|nested quantifiers]].
- Then finish with the [[06 propositional equivalences|propositional laws]].
- $\lnot\forall x\, (P(x) \to Q(x)) \equiv \exists x\, \lnot(P(x) \to Q(x)) \equiv \exists x\, (P(x) \land \lnot Q(x))$, by the [[02 implication|negated implication]].
- "Not every $P$ is a $Q$" = "some $P$ is not a $Q$".
