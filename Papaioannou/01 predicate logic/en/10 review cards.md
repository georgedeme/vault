---
tags:
  - uni/επλ-111/predicate-logic/en
---

## Overview

- Spaced repetition cards for the predicate logic lecture.
- 1 card per line, prompt and answer separated by an arrow.
- The deck name comes from this note's folder.
- The same note in Greek: [[010 uni/01 ΕΠΛ 111/01 predicate logic/gr/10 κάρτες επανάληψης|κάρτες επανάληψης]].

## Predicates and binding

Why $x > 3$ is not a proposition --> its truth value depends on the value of $x$
The 2 parts of "$x$ is greater than $3$" --> the variable $x$, the subject, and the predicate "is greater than $3$", a property of it
Another name for $P(x)$ --> propositional function
Arity of a predicate --> the number of arguments it takes
Domain, or universe of discourse --> the set of values the variables may take
Two ways to obtain a proposition from an open formula --> substitute values for its free variables, or bind them with quantifiers; the methods can be combined
Free variable occurrence --> an occurrence outside the scope of a quantifier for that variable; assigning a value to evaluate it does not bind it
When a predicate statement is a proposition --> when it has no free variables
Truth value of $P(4) \oplus R(1,2,3)$ with $P(x)$: $x > 3$, $R(x,y,z)$: $x + y = z$ --> F, both sides are true

## The 2 quantifiers

$\forall x\, P(x)$ --> $P(x)$ is true for every value of $x$ in the domain
$\exists x\, P(x)$ --> $P(x)$ is true for at least 1 value of $x$ in the domain
Counterexample --> a value $a$ with $P(a)$ false, which proves $\forall x\, P(x)$ false
Witness --> a value $a$ with $P(a)$ true, which proves $\exists x\, P(x)$ true
$\forall x\, (x^2 \ge x)$ over the integers vs the reals --> true over the integers, false over the reals at $x = \frac{1}{2}$
$\forall x\, (x^2 < 10)$ over $1,2,3$ vs $1,2,3,4$ --> true, then false because of $x = 4$
$\forall x\, P(x)$ over a finite domain $a_1, \dots, a_n$ --> $P(a_1) \land \dots \land P(a_n)$
$\exists x\, P(x)$ over a finite domain $a_1, \dots, a_n$ --> $P(a_1) \lor \dots \lor P(a_n)$
Which 2 cases need only 1 value to settle --> $\forall$ false and $\exists$ true
Effect of enlarging the domain for a fixed property unchanged on existing elements --> $\forall$ can only get harder to satisfy, $\exists$ only easier

## Negation

$\lnot\forall x\, P(x)$ --> $\exists x\, \lnot P(x)$
$\lnot\exists x\, P(x)$ --> $\forall x\, \lnot P(x)$
Why the negation rules are De Morgan's laws --> over a finite domain $\forall$ is a conjunction and $\exists$ a disjunction
$\lnot\forall x\, (P(x) \to Q(x))$ --> $\exists x\, (P(x) \land \lnot Q(x))$
$\lnot\forall x\, \exists y\, P(x,y)$ --> $\exists x\, \forall y\, \lnot P(x,y)$
$\lnot\exists x\, \forall y\, P(x,y)$ --> $\forall x\, \exists y\, \lnot P(x,y)$
What negation does to a chain of quantifiers --> flips every quantifier, keeps their order, and puts $\lnot$ on the predicate

## Translating

"Every $P$ is a $Q$" --> $\forall x\, (P(x) \to Q(x))$
"Some $P$ is a $Q$" --> $\exists x\, (P(x) \land Q(x))$
What is wrong with $\exists x\, (P(x) \to Q(x))$ for "some $P$ is a $Q$" --> any $x$ that is not a $P$ makes it vacuously true
What is wrong with $\forall x\, (P(x) \land Q(x))$ for "every $P$ is a $Q$" --> it claims everything in the domain is a $P$
"All students have visited France or Greece", domain all people --> $\forall x\, (S(x) \to (F(x) \lor G(x)))$
Same sentence, domain all students --> $\forall x\, (F(x) \lor G(x))$
Why "exactly 1" needs equality --> "no other" has to say $z \ne y$
The 2 halves of "exactly 1" --> at least 1, and no more than 1
$\exists!$ --> the uniqueness quantifier, "there is exactly 1"
Why $\lnot(x = y)$ in "there are 2 students who…" --> without it $x$ and $y$ could be the same student
$A \to \exists y\, B(y)$ vs $\exists y\, (A \to B(y))$ --> equivalent when $y$ does not occur in $A$ and the domain is non-empty

## Nesting and order

Scope of a quantifier --> the part of the statement it applies to
Nested quantifiers --> quantifiers inside the scope of other quantifiers
$\forall x\, \exists y\, P(x,y)$ over $1,2,3$ without quantifiers --> $(P(1,1) \lor P(1,2) \lor P(1,3)) \land (P(2,1) \lor P(2,2) \lor P(2,3)) \land (P(3,1) \lor P(3,2) \lor P(3,3))$
Which quantifiers commute --> adjacent quantifiers of the same kind, with their shared scope unchanged
$\forall x\, \exists y\, (x + y = 0)$ vs $\exists y\, \forall x\, (x + y = 0)$ over the integers --> true, false
Why order matters in $\forall x\, \exists y$ --> $y$ is chosen after $x$ and may depend on it
Which of $\forall x\, \exists y$ and $\exists y\, \forall x$ is stronger --> $\exists y\, \forall x$; it implies the other, not conversely

"Every $A$ relates to some $B$" --> $\forall x\, (A(x) \to \exists y\, (B(y) \land R(x,y)))$
"There is a $B$ to which every $A$ relates" --> $\exists y\, (B(y) \land \forall x\, (A(x) \to R(x,y)))$
Which question distinguishes $\forall x\,\exists y$ from $\exists y\,\forall x$ --> whether $y$ may change when $x$ changes
Escaping through a non-member in $\exists y\,(B(y)\to C(y))$ --> a $y$ outside $B$ makes the implication vacuously true
Overclaiming in $\forall x\,(A(x)\land C(x))$ --> it requires every domain element to be an $A$
Why $B(y)$ stays outside in $\exists y\,(B(y)\land\forall x\,(A(x)\to R(x,y)))$ --> it must hold for the witness even if there are no $A$s
"Some $A$ fails to relate to at least one $B$" --> $\exists x\, (A(x) \land \exists y\, (B(y) \land \lnot R(x,y)))$
"Some $A$ relates to no $B$" --> $\exists x\, (A(x) \land \forall y\, (B(y) \to \lnot R(x,y)))$
How to represent a known, named object $a$ --> use the constant $a$, not a free variable or a new quantifier
"Some $A$ relates to all the other $A$s" --> $\exists x\, (A(x) \land \forall y\, ((A(y) \land \lnot(x = y)) \to R(x,y)))$

## Translation checks

Steps before writing the final formula --> fix the domain; expand the sentence in words; name the objects; make quantifiers and connectives explicit; replace predicates with symbols; read it back
Does $\exists x$ itself restrict $x$ to students --> no; over all people, $S(x)\land\dots$ requires the witness to be a student
Why $\forall x\,(S(x)\to H(x))$ exempts non-students --> when $S(x)$ is false, the implication is true regardless of $H(x)$
When can the category restriction be omitted --> when the stated domain already consists of that category; this concerns domain elements, not everyone outside it
Must $\forall$ always use $\to$ and $\exists$ always use $\land$ --> no; these patterns express category restrictions, not a general syntax rule
Does choosing all teachers as the single domain restrict only $x$ in a formula with $x,y$ --> no; it also restricts $y$, so students outside that domain disappear
Does "all the others" imply no relation to oneself --> no; excluding oneself from the requirement leaves the self-relation unspecified
What turns at least three collaborators into exactly three --> require all three witnesses to be pairwise different and require every collaborator to equal one of them

## Databases

Who proposed predicate logic as a query language, and when --> Edgar F. Codd, 1970
What a table is in predicate logic --> a predicate, with each row a true instance
Closed-world assumption --> any instance not listed in the database is false
How a query returns values rather than yes or no --> leave those variables free; they become the result's columns
How 2 tables are joined in a formula --> by sharing a variable between predicates in a conjunction
What first-order logic over the edge relation cannot express uniformly --> reachability in arbitrary finite networks with no common bound on their size
What a fixed bound on route length permits --> a finite disjunction of formulas for each permitted length; counting chain variables alone is not a proof of general inexpressibility
