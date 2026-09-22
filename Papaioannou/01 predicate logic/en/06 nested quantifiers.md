---
tags:
  - uni/επλ-111/predicate-logic/en
---

## Definition

> The scope of a quantifier is the part of the statement it applies to. Nested quantifiers appear inside the scope of other quantifiers.

- $\forall x\, \exists y\, (x + y = 0)$, domain: the [[00 math/00 arithmetic & number systems/00 number systems/04 the real number line & number system hierarchy|real numbers]]. True — for each $x$, take $y = -x$.
- The inner $y$ may depend on the outer $x$ — why [[07 quantifier order|order]] matters.
- Parentheses mark scope: in $\forall x\, (P(x) \lor \exists y\, Q(x,y))$, $\exists y$ covers only $Q(x,y)$.
- The same note in Greek: [[06 φωλιασμένοι ποσοδείκτες|φωλιασμένοι ποσοδείκτες]].

## As nested loops

- On a finite domain, quantifiers can be evaluated as [[01 cs/00 programming fundamentals/05 loops/04 nested loops|nested loops]] over the [[01 binding variables|domain]], in the order written.
- $\forall$ fails on the first false case. $\exists$ succeeds on the first true case.
- $\forall x\, \exists y$: for each $x$, search for a $y$ — the search restarts for every $x$.

```python
all(any(P(x, y) for y in domain) for x in domain)   # ∀x ∃y P(x,y)
```

- The Python expression assumes a defined predicate `P` and a finite, reusable collection `domain`, such as a list. It illustrates evaluation, not a general algorithm for infinite domains.

## Without quantifiers

$\forall x\, \exists y\, P(x,y)$, domain: $1, 2, 3$.

- Expanding [[02 the universal quantifier|$\forall$]] first: $\exists y\, P(1,y) \land \exists y\, P(2,y) \land \exists y\, P(3,y)$.
- Expanding [[03 the existential quantifier|$\exists$]] first: $\forall x\, (P(x,1) \lor P(x,2) \lor P(x,3))$.
- Both end at:

$$(P(1,1) \lor P(1,2) \lor P(1,3)) \land (P(2,1) \lor P(2,2) \lor P(2,3)) \land (P(3,1) \lor P(3,2) \lor P(3,3))$$

- 1 [[01 logical operators|disjunction]] per $x$, joined by conjunction — each can be satisfied by a different $y$.

## Reading nested statements

Domain: the [[00 math/00 arithmetic & number systems/00 number systems/04 the real number line & number system hierarchy|real numbers]]. Laws from [[00 math/01 algebra/00 foundations/02 properties of real numbers|properties of real numbers]].

- $\forall x\, \exists y\, (x + y = 0)$: every real number has an additive inverse.
- $\forall x\, \forall y\, (x + y = y + x)$: the commutative law for addition.
- $\forall x\, \forall y\, \forall z\, (x + (y + z) = (x + y) + z)$: the associative law for addition.
- $\forall x\, \forall y\, ((x > 0) \land (y < 0) \to xy < 0)$: a positive times a negative is negative.
- Algebraic laws are $\forall$ statements — 1 [[02 the universal quantifier|counterexample]] refutes one.

## Example, a computer or a classmate with one

$$\forall x\, (P(x) \lor \exists y\, (P(y) \land Q(x,y)))$$

- $P(x)$: $x$ has a computer. $Q(x,y)$: $x$ and $y$ are classmates. Domain: all students.
- Every student has a computer, or has a classmate who has a computer.
- $\exists y$ covers only the right disjunct — a separate $y$ per student.
- Inner part: [[05 translating with quantifiers|$\exists$ with $\land$]].

## Example, friends who are not friends

$$\exists x\, \forall y\, \forall z\, ((P(x,y) \land P(x,z) \land \lnot Q(y,z)) \to \lnot P(y,z))$$

- $P(x,y)$: $x$ and $y$ are friends. $Q(x,y)$: $x$ and $y$ are the same person. Domain: all students.
- Some student has no friends who are friends with each other.
- $\lnot Q(y,z)$: $y$ and $z$ must be 2 different friends.
- [[05 translating with quantifiers|$\forall$ with $\to$]]: $y$, $z$ range over everyone, the hypothesis keeps only friends of $x$.

- This does not require the chosen student to have friends. Zero or one friend also satisfies it, because there is no pair of different friends that violates the requirement.

## Negating nested quantifiers

- The [[04 negating quantifiers|negation rules]], 1 quantifier at a time:

$$\lnot\forall x\, \forall y\, P(x,y) \equiv \exists x\, \lnot\forall y\, P(x,y) \equiv \exists x\, \exists y\, \lnot P(x,y)$$
$$\lnot\forall x\, \exists y\, P(x,y) \equiv \exists x\, \lnot\exists y\, P(x,y) \equiv \exists x\, \forall y\, \lnot P(x,y)$$
$$\lnot\exists x\, \forall y\, P(x,y) \equiv \forall x\, \lnot\forall y\, P(x,y) \equiv \forall x\, \exists y\, \lnot P(x,y)$$
$$\lnot\exists x\, \exists y\, P(x,y) \equiv \forall x\, \lnot\exists y\, P(x,y) \equiv \forall x\, \forall y\, \lnot P(x,y)$$

- Every quantifier flips, the order stays, $\lnot$ lands on the predicate.
- "Not every real has an additive inverse": $\exists x\, \forall y\, (x + y \ne 0)$.
