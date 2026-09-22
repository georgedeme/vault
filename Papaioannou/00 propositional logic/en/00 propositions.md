---
tags:
  - uni/επλ-111/propositional-logic/en
---

## Overview

- Lecture 1 of ΕΠΛ 111, Discrete Structures in Computer Science, University of Cyprus, following Rosen 5th edition chapters 1.1 and 1.2.
- Understanding and constructing valid mathematical arguments is a stated goal of the course, and logic is the tool for it.
- The rules of logic give precise meaning to mathematical statements, and are what distinguish a valid argument from an invalid one.
- This folder is the course's presentation of [[00 math/11 mathematical logic & proof/06 propositional logic|propositional logic]], in the course's notation.
- The same notes in Greek: [[00 προτάσεις|προτάσεις]].

## Definition

> A proposition is a declarative statement that is either true (T) or false (F), but not both at the same time.

- The truth value of a proposition is T or F.
- Capital letters stand for propositions: $P$, $Q$, $R$, $S$, … The course uses capitals where Rosen uses $p$, $q$, $r$.
- The branch of logic that deals with propositions is propositional logic, also called the propositional calculus.
- Declarative is doing real work in the definition. A sentence that asserts nothing has no truth value and so is not a proposition.

## Which of these are propositions

- Nicosia is the capital of Cyprus — yes, true.
- Oxford is the capital of England — yes, false. Being false does not stop a statement being a proposition; having no fixed truth value does.
- $1+1=2$ — yes, true.
- $2+2=5$ — yes, false.
- $x+1=2$ — no. Its truth depends on $x$, so it has no single truth value. It is an open sentence, and needs [[00 math/11 mathematical logic & proof/03 quantifiers & their negation|quantifiers]] before it becomes a proposition.
- $x+y=z$ — no, for the same reason.
- Also excluded: questions, commands and opinions, since none of them declare anything that can be true or false.
- The borderline case worth knowing: a statement can be a proposition even when nobody knows its truth value. "There are infinitely many twin primes" is either true or false, so it qualifies; being unproved is not the same as being undetermined.

## Atomic and compound

- An atomic proposition contains no [[01 logical operators|logical operator]]. Everything above is atomic.
- A compound proposition is built out of simpler propositions with logical operators; that construction is the whole subject of this folder.
- Propositional logic never looks inside an atom. "Every prime greater than $2$ is odd" is a single letter here, which is the limitation [[00 math/11 mathematical logic & proof/03 quantifiers & their negation|predicate logic]] exists to lift.

## Where this folder goes

- [[01 logical operators|Logical operators]] and the truth table that defines each one.
- [[02 implication|Implication]] and [[03 the biconditional|the biconditional]], the 2 operators that cause the most trouble.
- [[04 operator precedence|Operator precedence]], so a formula written without parentheses still has 1 reading.
- [[05 translating natural language|Translating natural language]] into formulas.
- [[06 propositional equivalences|Propositional equivalences]], and the 2 methods for proving them.
- [[07 functional completeness|Functional completeness]] — how few operators you actually need.
