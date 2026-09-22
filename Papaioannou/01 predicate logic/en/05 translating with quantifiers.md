---
tags:
  - uni/επλ-111/predicate-logic/en
---

## Overview

- Natural language is often ambiguous. A formula is not.
- Once translated, [[00 math/11 mathematical logic & proof/02 direct & indirect proof|valid conclusions]] can be drawn by rule.
- Reasonable assumptions about the intended meaning are allowed.
- Builds on [[05 translating natural language|translating natural language]] from lecture 1.
- The same note in Greek: [[05 μετάφραση με ποσοδείκτες|μετάφραση με ποσοδείκτες]].

## Method

- Fix the [[01 binding variables|domain]] first — it decides the shape of the formula.
- Rewrite the sentence step by step in ordinary language until every "for every", "there exists", "if … then", "and", and "not" is explicit.
- With a broad domain, expand "every student" into "every person, if that person is a student …"; expand "some student" into "there exists a person who is a student and …".
- Name the objects $x,y,\dots$ and repeat them instead of ambiguous pronouns; preserve who acts on whom.
- Split the remaining claims into [[00 predicates|predicates]], then replace words with [[01 logical operators|symbols]]. Do not skip directly from the original sentence to the final formula.
- Put the entire intended [[06 nested quantifiers|scope]] inside each quantifier's parentheses.
- Read the formula back into words and compare its meaning with the original; state any interpretation needed for ambiguous wording.

## Quantifier words

- all, every, each, any: $\forall$.
- some, there is, at least 1: $\exists$.
- no, none, nobody: $\lnot\exists$, or $\forall \dots \lnot$ by [[04 negating quantifiers|negation]].
- not all, not every: $\lnot\forall$, or $\exists \dots \lnot$.

## "All", domain all students

> All students have visited France or Greece

- Rephrased: every student has visited France or Greece.
- $P(x)$: $x$ has visited France. $Q(x)$: $x$ has visited Greece.
- $\forall x\, (P(x) \lor Q(x))$.
- The domain is exactly the students — no "is a student" predicate needed.

## "All", domain all people

> All students have visited France or Greece

- Rephrased: for every $x$, if $x$ is a student, then $x$ has visited France or $x$ has visited Greece.
- $P(x)$: $x$ is a student. $Q(x)$: $x$ has visited France. $R(x)$: $x$ has visited Greece.
- $\forall x\, (P(x) \to (Q(x) \lor R(x)))$.
- Wider domain, so "is a student" becomes the hypothesis of an [[02 implication|implication]].
- Non-students make the hypothesis false — [[02 implication|vacuously true]], and correctly so.

## "Some", domain all students

> Some student has visited France or Greece

- Rephrased: there is a student who has visited France or Greece.
- $P(x)$: $x$ has visited France. $Q(x)$: $x$ has visited Greece.
- $\exists x\, (P(x) \lor Q(x))$.

## "Some", domain all people

> Some student has visited France or Greece

- Rephrased: there is an $x$ such that $x$ is a student and at least one of the following holds: $x$ has visited France, or $x$ has visited Greece.
- $P(x)$: $x$ is a student. $Q(x)$: $x$ has visited France. $R(x)$: $x$ has visited Greece.
- $\exists x\, (P(x) \land (Q(x) \lor R(x)))$.
- Here the restriction is a [[01 logical operators|conjunction]]: the [[03 the existential quantifier|witness]] must be a student and have traveled.

## The pattern

- Restricting a universal claim to a category: "every $P$ is a $Q$" is $\forall x\, (P(x) \to Q(x))$.
- Requiring an existential witness to belong to a category: "some $P$ is a $Q$" is $\exists x\, (P(x) \land Q(x))$.
- For these translations, $\forall x\, (P(x) \land Q(x))$ is too strong: it also claims everything in the domain is a $P$.
- For these translations, $\exists x\, (P(x) \to Q(x))$ is too weak: any non-$P$ makes it true, even if there are no $P$s.
- The quantifier itself does not narrow the domain. In $\exists x\,(P(x)\land Q(x))$, $P(x)$ is what requires the witness to belong to the category.
- If the domain already consists exactly of the $P$s, write $\forall x\,Q(x)$ or $\exists x\,Q(x)$. Membership is then guaranteed for domain elements, not for everyone outside the domain.
- These are patterns for category restrictions, not rules that forbid $\land$ under $\forall$ or $\to$ under $\exists$.
- For example, over all students, "every student studies and works" is $\forall x\,(S(x)\land W(x))$, where $S$ means studies and $W$ means works.

## Worked translation, step by step

Domain: all people. $T(x)$: $x$ is a teacher. $H(x)$: $x$ has a computer.

### Every teacher has a computer

1. Every teacher has a computer.
2. For every person, if that person is a teacher, then that person has a computer.
3. For every $x$, if $x$ is a teacher, then $x$ has a computer.
4. For every $x$, if $T(x)$, then $H(x)$.

$$\forall x\,(T(x)\to H(x))$$

- A non-teacher imposes no requirement on $H(x)$, because the implication is true when $T(x)$ is false.
- If the domain is all teachers instead, the same claim is $\forall x\,H(x)$.

### Some teacher has a computer

1. At least one teacher has a computer.
2. There exists a person who is a teacher and has a computer.
3. There exists $x$ such that $x$ is a teacher and $x$ has a computer.
4. There exists $x$ such that $T(x)$ and $H(x)$.

$$\exists x\,(T(x)\land H(x))$$

- A non-teacher cannot be a witness, because the conjunction requires $T(x)$ to be true.
- If the domain is all teachers instead, the same claim is $\exists x\,H(x)$.
- With two different categories in one relation, keep both restrictions where needed — [[08 translating with nested quantifiers|nested translation]].
