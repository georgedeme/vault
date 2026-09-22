---
tags:
  - uni/επλ-111/predicate-logic/en
---

## Definition

> "$P(x)$ is true for some value of $x$ in the domain", written $\exists x\, P(x)$.

- $\exists$: the existential quantifier.
- Read "for some $x$, $P(x)$" or "there exists $x$ such that $P(x)$".
- "Some" means at least 1 — not exactly 1.
- The same note in Greek: [[03 υπαρξιακός ποσοδείκτης|υπαρξιακός ποσοδείκτης]].

## Examples

| $P(x)$ | domain | $\exists x\, P(x)$ | why |
|---|---|---|---|
| $x + 1 > x$ | integers | T | $x = 0$ works |
| $x = x + 1$ | integers | F | reduces to $0 = 1$ for every $x$ |
| $x^2 < 10$ | $1, 2, 3, 4$ | T | $x = 1$ works |
| $x^2 < 10$ | $4, 5, 6$ | F | smallest square is $16$ |
| $x^2 \ge x$ | integers | T | $x = 0$ works |
| $x^2 \ge x$ | reals | T | $x = 2$ works |

- Rows 3–4: the [[01 binding variables|domain]] decides again.
- For a fixed property $P$ whose truth on existing elements stays unchanged, enlarging the domain adds possible witnesses: a false $\exists x\,P(x)$ may become true, but an existing witness still works.
- Row 6 against the [[02 the universal quantifier|$\forall$ table]]: $x^2 \ge x$ over the reals is false under $\forall$, true under $\exists$.

## Witnesses

> To show $\exists x\, P(x)$ is true, find 1 value $a$ in the domain with $P(a)$ true. That value is a witness.

- 1 is enough.
- Proving $\exists x\, P(x)$ false means proving [[04 negating quantifiers|$\forall x\, \lnot P(x)$]] — exhaust the cases on a finite domain, or give a general argument (as in row 2).
- A [[02 the universal quantifier|counterexample]] to $\forall x\, P(x)$ is a witness for $\exists x\, \lnot P(x)$.

## Finite domain

- Domain $a_1, \dots, a_n$: $\exists x\, P(x) \equiv P(a_1) \lor \dots \lor P(a_n)$, a [[01 logical operators|disjunction]].
- $\forall$ is to $\land$ as $\exists$ is to $\lor$ — why the [[04 negating quantifiers|negation rules]] are [[06 propositional equivalences|De Morgan's laws]].
- Standard first-order logic assumes a non-empty domain. If empty domains are allowed, an existential statement is false there: no witness exists.

## True and false

- $\forall x\, P(x)$ true: $P(a)$ true for every $a$. False: some $a$ with $P(a)$ false.
- $\exists x\, P(x)$ true: some $a$ with $P(a)$ true. False: $P(a)$ false for every $a$.
- Easy cases, 1 value settles them: $\forall$ false, $\exists$ true.
- Hard cases, they need an argument over the whole domain: $\forall$ true, $\exists$ false.
