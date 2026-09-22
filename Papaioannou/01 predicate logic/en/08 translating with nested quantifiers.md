---
tags:
  - uni/επλ-111/predicate-logic/en
---

## Overview

- [[05 translating with quantifiers|Translating with quantifiers]], now with [[06 nested quantifiers|nested quantifiers]].
- Same method. New: track which variable each quantifier introduces and where its [[06 nested quantifiers|scope]] ends.
- The same note in Greek: [[08 μετάφραση με φωλιασμένους ποσοδείκτες|μετάφραση με φωλιασμένους ποσοδείκτες]].

## Equality

- $x = y$: a built-in [[00 predicates|predicate]], true when $x$ and $y$ are the same element of the [[01 binding variables|domain]].
- $\lnot(x = y)$, also written $x\ne y$ or $\lnot{=}(x,y)$: different elements. Different variable names alone do not require different values.
- Needed for counting — "2", "exactly 1", "all the others".

## Example 1, mothers

> Every person who is a woman and a parent is someone's mother

Domain: all people.

- $P(x)$: $x$ is a woman. $Q(x)$: $x$ is a parent. $R(x,y)$: $x$ is the mother of $y$.
- For every $x$, if $x$ is a woman and $x$ is a parent, then there is a $y$ such that $x$ is the mother of $y$.

$$\forall x\, ((P(x) \land Q(x)) \to \exists y\, R(x,y))$$

- Restricted $\forall$, so [[05 translating with quantifiers|$\to$]].
- Equivalent, with $\exists y$ moved to the front:

$$\forall x\, \exists y\, ((P(x) \land Q(x)) \to R(x,y))$$

- Why: $y$ does not appear in the hypothesis $A$, and $A \to \exists y\, B(y) \equiv \exists y\, (A \to B(y))$.
- Requires a non-empty domain.

## Example 2, exactly 1 friend

> Everyone has exactly 1 friend

Domain: all people. $P(x,y)$: $x$ is a friend of $y$.

- Counting friends other than oneself: for every $x$, choose a different person $y$ who is a friend; every person $z$ different from both $x$ and $y$ must not be a friend of $x$.

$$\forall x\, \exists y\, (\lnot(x = y) \land P(x,y) \land \forall z\, (\lnot(x = z) \land \lnot(y = z) \to \lnot P(x,z)))$$

- "Exactly 1" = at least 1 + no more than 1.
- At least 1: the [[03 the existential quantifier|witness]] $y$.
- No more than 1 other friend: $\forall z\,((z\ne x\land z\ne y)\to\lnot P(x,z))$, nested inside $\exists y$ so it can refer to $y$.
- The formula excludes oneself from the count; it does not require $P(x,x)$ to be false.
- If self-friendship must be false as well, use the stricter formula below. It agrees with the first formula when $\forall x\,\lnot P(x,x)$ is already assumed.

$$\forall x\,\exists y\,(x\ne y\land P(x,y)\land\forall z\,(P(x,z)\to z=y))$$

- Here every friend must equal $y$; since $y\ne x$, this also rules out $P(x,x)$.
- Shorthand: $\exists!$, the uniqueness quantifier — "there is exactly 1".

## Example 3, 2 students

> There are 2 students who between them have emailed or phoned every other student

Domain: all students. $P(x,y)$: $x$ has emailed $y$. $Q(x,y)$: $x$ has phoned $y$.

- There are $x$, $y$ such that $x$ and $y$ are different, and for every $z$, if $z$ is neither $x$ nor $y$, then $x$ or $y$ has emailed or phoned $z$.

$$\exists x\, \exists y\, (\lnot(x = y) \land \forall z\, (\lnot((x = z) \lor (y = z)) \to (P(x,z) \lor P(y,z) \lor Q(x,z) \lor Q(y,z))))$$

- $\lnot(x = y)$: 2 different students.
- $\lnot((x = z) \lor (y = z))$: "every other" excludes $x$ and $y$.
- "Between them": a 4-way [[01 logical operators|disjunction]] — 1 contact per $z$ is enough.

## Example 4, sum of 2 positive integers

> The sum of 2 positive integers is a positive integer

Domain: all [[00 math/00 arithmetic & number systems/00 number systems/01 integers|integers]].

- For every $x$ and $y$, if $x$ is positive and $y$ is positive, then there is a $z$ such that $z$ is positive and $x + y = z$.

$$\forall x\, \forall y\, ((x > 0) \land (y > 0) \to \exists z\, (z > 0 \land x + y = z))$$

- Domain is all integers, so positivity must be stated.
- $\forall$ with $\to$ for the inputs, $\exists$ with $\land$ for the output.
- No $\lnot(x = y)$: $1 + 1$ counts.

## Worked translation with two categories

Domain: all people. $S(x)$: $x$ is a student. $T(x)$: $x$ is a teacher. $R(x,y)$: $x$ has taught $y$.

### Every teacher has taught some student

1. For every teacher, there is at least one student whom that teacher has taught.
2. For every person, if that person is a teacher, then there exists a person who is a student and whom the teacher has taught.
3. For every $x$, if $x$ is a teacher, then there exists $y$ such that $y$ is a student and $x$ has taught $y$.
4. For every $x$, if $T(x)$, then there exists $y$ such that $S(y)$ and $R(x,y)$.

$$\forall x\,(T(x)\to\exists y\,(S(y)\land R(x,y)))$$

- There is no requirement that $x\ne y$: add it only if the sentence says "another" or the intended model requires it.
- Changing the whole domain to teachers would also restrict $y$ to teachers. It would lose students outside that domain; do not remove category predicates by changing the meaning of the problem.

### One teacher has taught all the other teachers

1. There exists a teacher who has taught every teacher different from that teacher.
2. There exists a person $x$ who is a teacher and, for every person $y$, if $y$ is a teacher different from $x$, then $x$ has taught $y$.
3. There exists $x$ such that $T(x)$ and, for every $y$, if $T(y)$ and $x\ne y$, then $R(x,y)$.

$$\exists x\,(T(x)\land\forall y\,((T(y)\land x\ne y)\to R(x,y)))$$

- Compare $\forall x\,(T(x)\to\exists y\,(T(y)\land x\ne y\land R(y,x)))$: every teacher has been taught by some other teacher. That teacher may differ for each $x$.
- A cycle of three teachers, each teaching only the next, satisfies the second claim but not the first. Renaming variables is harmless; reversing quantifier order or relation arguments can change meaning.

## Exactly three

Domain: all people. $h$ names Christodoulos. $C(h,x)$: Christodoulos has collaborated with $x$.

1. There are three people with whom Christodoulos has collaborated.
2. They are pairwise different: $x\ne y$, $x\ne z$, $y\ne z$.
3. Every collaborator $w$ is one of those three: if $C(h,w)$, then $w=x$ or $w=y$ or $w=z$.

$$
\exists x\,\exists y\,\exists z\,\bigl(
x\ne y\land x\ne z\land y\ne z
\land C(h,x)\land C(h,y)\land C(h,z)
\land\forall w\,(C(h,w)\to(w=x\lor w=y\lor w=z))
\bigr)
$$

- The distinct witnesses give "at least three"; the final universal clause rules out a fourth.
- "At most three" alone would not require three witnesses. "Exactly three" requires both existence and the upper bound.

## Choosing order and connectives

Let $A(x)$ mean that $x$ belongs to the first category, $B(y)$ that $y$ belongs to the second, and $R(x,y)$ that $x$ relates to $y$. The relation need not be symmetric.

### $\forall x\,\exists y$ or $\exists y\,\forall x$

- "Every $A$ relates to some $B$":

$$\forall x\,(A(x)\to\exists y\,(B(y)\land R(x,y)))$$

- The witness $y$ is chosen after $x$ is given, so it may differ for each $x$.
- "There is a $B$ to which every $A$ relates":

$$\exists y\,(B(y)\land\forall x\,(A(x)\to R(x,y)))$$

- The same witness $y$ must work for every $x$. This is a stronger requirement.
- Key question: "May $y$ change when $x$ changes?" If yes, $\forall x\,\exists y$. If not, $\exists y\,\forall x$.
- Adjacent quantifiers of the same kind commute; mixed kinds generally do not — [[07 quantifier order|quantifier order]].

### $\to$ or $\land$

- Restricting a universally quantified variable: $\forall x\,(A(x)\to\dots)$. Only the $A$s must meet the requirement; other objects satisfy the implication by [[02 implication|vacuous truth]].
- Multiple restrictions on the same universal object go together in the hypothesis: $\forall x\,((A(x)\land C(x))\to\dots)$.
- Restricting an existential witness: $\exists y\,(B(y)\land\dots)$. The witness must actually be a $B$ and satisfy the remaining requirement.
- Reminder: restricted $\forall$ with $\to$, restricted $\exists$ with $\land$ — see [[05 translating with quantifiers|the domain rule and its limits]].

### Common mistakes

#### Escaping through a non-member

$$\forall x\,\exists y\,((A(x)\land B(y))\to R(x,y))$$

- Too weak: $\exists y$ can choose a $y$ that is not a $B$. The hypothesis becomes false and the implication true without requiring $R(x,y)$.
- Correction: conjoin the existential witness's membership with its requirement:

$$\forall x\,(A(x)\to\exists y\,(B(y)\land R(x,y)))$$

#### Requiring everyone to belong

$$\forall x\,\exists y\,(A(x)\land B(y)\land R(x,y))$$

- Too strong: the conjunction requires every domain element $x$ to be an $A$.
- $A(x)$ should restrict which $x$s must meet the requirement, not describe the whole domain. Put it in an implication's hypothesis.

#### Hiding witness membership inside a universal implication

$$\exists y\,\forall x\,(A(x)\to(B(y)\land R(x,y)))$$

- If there are no $A$s, every implication is vacuously true and $B(y)$ is never required.
- If the sentence requires an actual $B$, keep $B(y)$ outside $\forall x$:

$$\exists y\,(B(y)\land\forall x\,(A(x)\to R(x,y)))$$

### "Someone" and "no one"

- "Some $A$ fails to relate to at least one $B$":

$$\exists x\,(A(x)\land\exists y\,(B(y)\land\lnot R(x,y)))$$

- One $B$ to which it does not relate is enough.
- "Some $A$ relates to no $B$":

$$\exists x\,(A(x)\land\forall y\,(B(y)\to\lnot R(x,y)))$$

- Equivalently: $\exists x\,(A(x)\land\lnot\exists y\,(B(y)\land R(x,y)))$.
- These differ: "not with someone" can mean one failure, whereas "with no one" means failure for all. Resolve ambiguous wording before choosing.

### Named or existentially quantified objects

- For a known object named $a$, use the constant $a$ without a quantifier: $B(a)\land\dots$.
- "Some $B$ exists" means $\exists y\,(B(y)\land\dots)$.
- "Every $B$" means $\forall y\,(B(y)\to\dots)$.
- "A particular object" does not justify a free variable. Use a defined constant or a quantifier.

### "All the others"

$$\exists x\,(A(x)\land\forall y\,((A(y)\land\lnot(x=y))\to R(x,y)))$$

- $\exists x$: there is a particular $A$ that performs the action.
- $\forall y$: consider all potential recipients.
- $A(y)\land\lnot(x=y)$ restricts the requirement to the other members of the same category.
- This imposes no requirement on $R(x,x)$; it neither asserts nor denies it.

## Check with counterexamples

- For $\forall x$, try an $x$ outside $A$. The translation should usually exempt it, not require it to become an $A$.
- For $\exists y$, try to satisfy the formula by choosing a $y$ outside $B$. If that works, you probably used $\to$ instead of $\land$.
- Imagine there are no $A$s. If the sentence still requires a $B$ to exist, $B(y)$ must stay outside the implication under $\forall x$.
- Ask whether one shared witness is required or a different one may be used per object; this decides [[07 quantifier order|the order]].
- Check that no variable was left [[01 binding variables|free]].

## Checklist

- Every variable bound?
- $\forall$ restrictions with $\to$, $\exists$ restrictions with $\land$?
- Each $\exists$ after the variables its witness depends on — [[07 quantifier order|order]]?
- Counting words backed by equality?
