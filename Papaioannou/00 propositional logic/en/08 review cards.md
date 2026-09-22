---
tags:
  - uni/επλ-111/propositional-logic/en
---

## Overview

- Spaced repetition cards for the propositional logic lecture.
- 1 card per line, prompt and answer separated by an arrow.
- The deck name comes from this note's folder.
- The same note in Greek: [[08 κάρτες επανάληψης|κάρτες επανάληψης]].

## Propositions and operators

A proposition --> a declarative statement that is either true or false, but not both
Why $x + 1 = 2$ is not a proposition --> its truth depends on $x$, so it has no single truth value
Atomic vs compound proposition --> atomic contains no logical operator; compound is built from simpler ones with operators
Truth-functional --> the truth value of the whole is fixed by the truth values of its parts
Rows in a truth table over $N$ propositions --> $2^N$
The 6 operators of the course --> negation, conjunction, disjunction, exclusive or, implication, biconditional
Which operator is unary --> negation; the other 5 are binary
When $P \land Q$ is true --> only when both are true
When $P \lor Q$ is true --> when at least 1 is true, inclusive
When $P \oplus Q$ is true --> when exactly 1 is true
$P \oplus Q$ in terms of the biconditional --> $\lnot(P \leftrightarrow Q)$
$P \oplus Q$ using only $\lnot$, $\land$, $\lor$ --> $(P \land \lnot Q) \lor (\lnot P \land Q)$
When a chain $P_1 \oplus \dots \oplus P_n$ is true --> when an odd number of its parts are true

## Implication

When $P \to Q$ is false --> only when the hypothesis is true and the conclusion is false
Vacuous truth --> a false hypothesis makes the implication true whatever the conclusion
The 4 readings of $P \to Q$ --> $P$ implies $Q$; if $P$ then $Q$; $P$ is sufficient for $Q$; $P$ only if $Q$
In $P \to Q$, which part is necessary --> $Q$; $P$ is the sufficient one
Converse of $P \to Q$ --> $Q \to P$
Inverse of $P \to Q$ --> $\lnot P \to \lnot Q$
Contrapositive of $P \to Q$ --> $\lnot Q \to \lnot P$
Which of the 3 is equivalent to $P \to Q$ --> only the contrapositive
Affirming the consequent --> concluding $P$ from $P \to Q$ and $Q$; invalid, it is the converse error
$P \to Q$ without the arrow --> $\lnot P \lor Q$
Negation of $P \to Q$ --> $P \land \lnot Q$, a conjunction

## The biconditional

When $P \leftrightarrow Q$ is true --> when $P$ and $Q$ have the same truth value
$P \leftrightarrow Q$ as 2 implications --> $(P \to Q) \land (Q \to P)$
The 4 readings of $P \leftrightarrow Q$ --> $P$ iff $Q$; $P$ if and only if $Q$; $P$ is necessary and sufficient for $Q$; if $P$ then $Q$ and conversely
Difference between $\leftrightarrow$ and $\equiv$ --> $\leftrightarrow$ is an operator inside the language; $\equiv$ claims from outside that $P \leftrightarrow Q$ is a tautology

## Precedence

Precedence order, tightest first --> $\lnot$, $\land$, $\lor$, $\oplus$, $\to$, $\leftrightarrow$
How the course reads $P \to Q \to R$ --> $(P \to Q) \to R$, left to right
How most texts read $P \to Q \to R$ --> $P \to (Q \to R)$, right-associative
Which operators are associative --> $\land$, $\lor$, $\oplus$, $\leftrightarrow$; only $\to$ is sensitive to grouping

## Translating

$P$ unless $Q$ --> $\lnot Q \to P$
Neither $P$ nor $Q$ --> $\lnot P \land \lnot Q$
Not both $P$ and $Q$ --> $\lnot(P \land Q)$
$P$ if $Q$ --> $Q \to P$
$P$ only if $Q$ --> $P \to Q$
How "but" translates --> exactly like "and"; the contrast is not truth-functional

## Equivalences

Tautology --> a compound proposition that is always true
Contradiction --> a compound proposition that is always false
Contingency --> true on some rows and false on others
Satisfiable --> at least 1 row of the truth table makes it true
$P \equiv Q$ --> $P \leftrightarrow Q$ is a tautology
The 2 methods for proving an equivalence --> truth tables, or rewriting with logical laws
Drawback of the truth-table method --> $2^N$ rows, so it is unusable past a few dozen propositions
De Morgan's laws --> $\lnot(P \land Q) \equiv \lnot P \lor \lnot Q$ and $\lnot(P \lor Q) \equiv \lnot P \land \lnot Q$
Identity laws --> $P \land \mathbf{T} \equiv P$ and $P \lor \mathbf{F} \equiv P$
Domination laws --> $P \lor \mathbf{T} \equiv \mathbf{T}$ and $P \land \mathbf{F} \equiv \mathbf{F}$
Negation laws --> $P \lor \lnot P \equiv \mathbf{T}$ and $P \land \lnot P \equiv \mathbf{F}$
Absorption laws --> $P \lor (P \land Q) \equiv P$ and $P \land (P \lor Q) \equiv P$
Distributive laws --> $P \lor (Q \land R) \equiv (P \lor Q) \land (P \lor R)$ and its dual
Duality of the laws --> swap $\land$ with $\lor$ and $\mathbf{T}$ with $\mathbf{F}$ and 1 half of each pair becomes the other
What $P$, $Q$, $R$ are inside a law --> slots for any proposition, atomic or compound; they may coincide, as long as substitution is uniform
The absorption laws as a special case --> distributivity with $R = P$
Is $P \to P$ valid --> yes, and it is a tautology; 2 rows in the table, T on both
What distinctness actually affects --> only the row count $2^N$; with $Q = P$ the table for $P \to Q$ drops from 4 rows to 2
What substitution preserves --> validity, not contingency; $P \to Q$ is contingent, $P \to P$ is a tautology

## Functional completeness

Functionally complete --> every compound proposition is equivalent to one using only operators from the collection
Why $\{\lnot, \land, \lor\}$ is complete --> a formula can be read off any truth table as a disjunction of 1 conjunction per true row
The shape that construction produces --> disjunctive normal form, the same as sum-of-products in boolean algebra
Why $\{\lnot, \land\}$ is complete --> $P \lor Q \equiv \lnot(\lnot P \land \lnot Q)$ by De Morgan and double negation
Why $\{\land, \lor\}$ is not complete --> both return T on all-T input, so $\lnot P$ is unreachable
The 2 binary operators complete on their own --> NAND and NOR
