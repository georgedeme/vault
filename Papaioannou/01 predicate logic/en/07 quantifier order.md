---
tags:
  - uni/επλ-111/predicate-logic/en
---

## Overview

- Adjacent quantifiers of the same kind can be interchanged without changing their shared scope.
- Mixed kinds: order can change the meaning.
- The same note in Greek: [[07 σειρά ποσοδεικτών|σειρά ποσοδεικτών]].

## Same kind commutes

- $\forall x\, \forall y\, P(x,y) \equiv \forall y\, \forall x\, P(x,y)$ — "for every pair".
- $\exists x\, \exists y\, P(x,y) \equiv \exists y\, \exists x\, P(x,y)$ — "for some pair".
- Finite domain: the same [[06 nested quantifiers|expansion]] with the terms reordered, and [[01 logical operators|$\land$, $\lor$]] are commutative.

## Mixed kinds do not

- $\forall x\, \exists y\, P(x,y) \equiv \exists y\, \forall x\, P(x,y)$? No.

Domain: the [[00 math/00 arithmetic & number systems/00 number systems/01 integers|integers]].

| statement | truth value | why |
|---|---|---|
| $\forall x\, \exists y\, (x + y = 0)$ | T | for each $x$, take $y = -x$ |
| $\exists y\, \forall x\, (x + y = 0)$ | F | $x = 1$ needs $y = -1$, $x = 2$ needs $y = -2$ |

| statement | truth value | why |
|---|---|---|
| $\forall x\, \forall y\, \exists z\, (x + y = z)$ | T | for each $x$, $y$, take $z = x + y$ |
| $\exists z\, \forall x\, \forall y\, (x + y = z)$ | F | $1 + 1 \ne 1 + 2$, so no single $z$ works |

- Same predicate, domain and quantifiers — only the order changed.

## Why order matters

- $\forall x\, \exists y$: $y$ is chosen after $x$, so it may depend on $x$. 1 [[03 the existential quantifier|witness]] per $x$.
- $\exists y\, \forall x$: $y$ is chosen first, so 1 witness must work for every $x$.
- $\exists y\, \forall x$ is the stronger claim: $\exists y\, \forall x\, P(x,y) \to \forall x\, \exists y\, P(x,y)$.
- The converse fails — both tables above.

## Everyday language

- Domain: people. $M(y,x)$ means "$y$ is the mother of $x$".
- "Everyone has a mother": $\forall x\, \exists y\, M(y,x)$, true under the ordinary biological interpretation.
- "Someone is everyone's mother": $\exists y\, \forall x\, M(y,x)$, false.
- Natural language hides the order; [[08 translating with nested quantifiers|translation]] makes it explicit.
