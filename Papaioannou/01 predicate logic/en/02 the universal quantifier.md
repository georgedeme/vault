---
tags:
  - uni/επλ-111/predicate-logic/en
---

## Definition

> "$P(x)$ is true for every value of $x$ in the domain", written $\forall x\, P(x)$.

- $\forall$: the universal quantifier.
- Read "for every $x$, $P(x)$" or "for all $x$, $P(x)$".
- [[01 binding variables|Binds]] $x$, so $\forall x\, P(x)$ is a [[00 propositions|proposition]].
- See also [[00 math/11 mathematical logic & proof/03 quantifiers & their negation|quantifiers & their negation]].
- The same note in Greek: [[02 καθολικός ποσοδείκτης|καθολικός ποσοδείκτης]].

## Examples

| $P(x)$ | domain | $\forall x\, P(x)$ | why |
|---|---|---|---|
| $x + 1 > x$ | integers | T | adding $1$ always increases |
| $x > 2$ | integers | F | fails at $x = 2$ |
| $x^2 < 10$ | $1, 2, 3, 4$ | F | fails at $x = 4$ |
| $x^2 < 10$ | $1, 2, 3$ | T | largest square is $9$ |
| $x^2 \ge x$ | integers | T | fails only for $0 < x < 1$, where no integer lies |
| $x^2 \ge x$ | reals | F | fails at $x = \frac{1}{2}$ |

- Same $P(x)$, different [[01 binding variables|domain]], different answer — rows 3–4 and 5–6.
- Domains: [[00 math/00 arithmetic & number systems/00 number systems/01 integers|integers]], [[00 math/00 arithmetic & number systems/00 number systems/04 the real number line & number system hierarchy|reals]].
- For a fixed property $P$ whose truth on existing elements stays unchanged, enlarging the domain adds cases to check: a true $\forall x\,P(x)$ may become false, but a counterexample remains a counterexample.

## Counterexamples

> To show $\forall x\, P(x)$ is false, find 1 value $a$ in the domain with $P(a)$ false. That value is a counterexample.

- 1 is enough.
- Proving $\forall x\, P(x)$ true needs an argument covering every value — checking finitely many individual examples does not cover an infinite domain.
- Why 1 is enough: [[04 negating quantifiers|$\lnot\forall x\, P(x) \equiv \exists x\, \lnot P(x)$]].
- More in [[00 math/11 mathematical logic & proof/04 counterexamples & disproof|counterexamples & disproof]].

## Finite domain

- Domain $a_1, \dots, a_n$: $\forall x\, P(x) \equiv P(a_1) \land \dots \land P(a_n)$, a [[01 logical operators|conjunction]].
- $x^2 < 10$ over $1, 2, 3$: $(1 < 10) \land (4 < 10) \land (9 < 10)$, true.
- Standard first-order logic assumes a non-empty domain. If empty domains are allowed, a universal statement is true there: nothing can fail — [[02 implication|vacuous truth]].
