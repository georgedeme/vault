---
tags:
  - uni/επλ-111/predicate-logic/en
---

## Overview

- Lecture 2 of ΕΠΛ 111, Discrete Structures in Computer Science, University of Cyprus — Rosen 5th edition, chapters 1.3 and 1.4.
- Extends [[00 propositions|propositional logic]] to statements with [[01 binding variables|variables]].
- 2 new tools: predicates, and [[02 the universal quantifier|quantifiers]].
- The course's version of [[00 math/11 mathematical logic & proof/03 quantifiers & their negation|quantifiers & their negation]].
- The same notes in Greek: [[00 κατηγορήματα|κατηγορήματα]].

## The gap in propositional logic

- $x > 3$, $x = y + 3$, $x + y = z$ — everywhere in mathematical arguments.
- Not [[00 propositions|propositions]]: the truth value depends on the values of the variables.
- Propositional logic cannot look inside them. Each would be 1 opaque letter.

## Definition

> The statement "$x$ is greater than $3$" has 2 parts: the variable $x$, the subject of the statement, and the predicate "is greater than $3$", a property the subject can have.

- Written $P(x)$: $x > 3$.
- $P(x)$ is a propositional [[00 math/01 algebra/05 functions/00 what is a function|function]]: plug in a value, get a proposition.
- Obtain a proposition by [[01 binding variables|substituting a value or quantifying]] the free variable.
- Substitution gives an instance for each domain value; there are infinitely many such instances only when the domain is infinite.

## Several variables

- $Q(x,y)$: $x = y + 3$.
- $R(x,y,z)$: $x + y = z$.
- $P(x_1, \dots, x_k)$: a statement involving $x_1, \dots, x_k$.
- Arity: the number of arguments. $P(x)$ is unary, $Q(x,y)$ binary.
- Argument order matters: $Q(3,0)$ is true, $Q(0,3)$ is false.
- A predicate of arity 2 or more is a [[00 math/07 discrete mathematics/01 relations & functions/00 relations & their properties|relation]] — which is why [[09 predicate logic and databases|database tables]] are predicates.

## Contents

- [[01 binding variables|Binding variables]] — the domain, free and bound variables.
- [[02 the universal quantifier|The universal quantifier]] and [[03 the existential quantifier|the existential quantifier]].
- [[04 negating quantifiers|Negating quantifiers]].
- [[05 translating with quantifiers|Translating with quantifiers]].
- [[06 nested quantifiers|Nested quantifiers]] and [[07 quantifier order|quantifier order]].
- [[08 translating with nested quantifiers|Translating with nested quantifiers]].
- [[09 predicate logic and databases|Predicate logic and databases]].
- [[010 uni/01 ΕΠΛ 111/01 predicate logic/en/10 review cards|Review cards]].
