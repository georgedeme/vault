---
tags:
  - uni/επλ-111/predicate-logic/en
---

## Overview

- Obtain a [[00 propositions|proposition]] by replacing every free variable with a specific value, using [[02 the universal quantifier|quantifiers]], or combining the two.
- The lecture groups these under "binding"; formally, substitution and quantifier binding are different operations.
- The 2 can be mixed in 1 statement.
- The same note in Greek: [[01 δέσμευση μεταβλητών|δέσμευση μεταβλητών]].

## Domain

- Domain, or universe of discourse: the [[00 math/07 discrete mathematics/00 set theory/00 sets & set operations|set]] of values the variables can take.
- Part of the statement's meaning — same [[00 predicates|predicate]], different domain, possibly a different truth value.
- Always stated alongside the formula: "domain: all [[00 math/00 arithmetic & number systems/00 number systems/01 integers|integers]]".

## Free and bound

- A variable occurrence is bound when it lies in the scope of a quantifier for that variable; otherwise it is free.
- A closed formula has no free variable occurrences and expresses a proposition under a fixed interpretation.
- Replacing $x$ by $4$ changes $P(x)$ into $P(4)$; that occurrence of $x$ disappears.
- Merely assigning $x=4$ to evaluate $P(x)$ does not change the written formula or make its free occurrence bound.
- In $(\forall x\, P(x)) \to Q(x)$, the first occurrence is bound and the occurrence in $Q(x)$ is free. Use $\forall x\, (P(x)\to Q(x))$ to cover both.
- See [Stanford's definition of free and bound occurrences](https://logical.stanford.edu/intrologic/sections/section_07.html?section=8).
- In [[09 predicate logic and databases|database queries]], the free variables are what the query returns.

## Assigning a value

Domain: all [[00 math/00 arithmetic & number systems/00 number systems/01 integers|integers]].

| predicate | instance | truth value |
|---|---|---|
| $P(x)$: $x > 3$ | $P(4)$: $4 > 3$ | T |
| | $P(2)$: $2 > 3$ | F |
| $Q(x,y)$: $x = y + 3$ | $Q(3,0)$: $3 = 0 + 3$ | T |
| | $Q(1,2)$: $1 = 2 + 3$ | F |
| $R(x,y,z)$: $x + y = z$ | $R(1,2,3)$: $1 + 2 = 3$ | T |
| | $R(0,0,1)$: $0 + 0 = 1$ | F |

- Arguments fill by position: $Q(3,0)$ means $x = 3$, $y = 0$.

## Combining with operators

- Fully substituted instances are ordinary propositions, so the [[01 logical operators|logical operators]] apply unchanged.
- $P(4) \lor P(2)$: $\mathbf{T} \lor \mathbf{F}$, true.
- $P(4) \oplus R(1,2,3)$: $\mathbf{T} \oplus \mathbf{T}$, false.
- $R(0,0,1) \to R(1,2,3)$: $\mathbf{F} \to \mathbf{T}$, true.

## Using quantifiers

- Binds a variable without picking a value — says how many values work.
- $\forall x\, P(x)$: every value — [[02 the universal quantifier|the universal quantifier]].
- $\exists x\, P(x)$: at least 1 value — [[03 the existential quantifier|the existential quantifier]].

## Mixing both

$P(x,y)$: $x \ge y$, domain: the [[00 math/00 arithmetic & number systems/00 number systems/00 natural & whole numbers|natural numbers]] $0, 1, 2, 3, 4, \dots$

| statement | reading | truth value |
|---|---|---|
| $\forall x\, P(x,0)$ | every $x$ is at least $0$ | T |
| $\forall y\, P(0,y)$ | $0$ is at least every $y$ | F |
| $\exists y\, P(0,y)$ | $0$ is at least some $y$ | T |

- Each line: 1 variable fixed by a value, 1 quantified — a proposition.
- $\forall y\, P(0,y)$ fails at $y = 1$, a [[02 the universal quantifier|counterexample]].
- $\exists y\, P(0,y)$ holds at $y = 0$, a [[03 the existential quantifier|witness]].
