---
tags:
  - uni/επλ-111/predicate-logic/en
---

## Overview

- In a [[01 cs/03 databases/00 relational databases|relational database]], a table represents a [[00 predicates|predicate]], a row a true instance, and a query a formula.
- Historical context: in 1970, Edgar F. Codd introduced the relational model and connected database querying with predicate logic.
- The same note in Greek: [[09 κατηγορική λογική και βάσεις δεδομένων|κατηγορική λογική και βάσεις δεδομένων]].

## Tables as predicates

Flight:

| origin | destination | airline |
|---|---|---|
| VIE | LHR | BA |
| LHR | EDI | BA |
| LGW | GLA | U2 |
| LCA | VIE | OS |

Airport:

| code | city |
|---|---|
| VIE | Vienna |
| LGW | London |
| LHR | London |
| LCA | Larnaca |
| GLA | Glasgow |
| EDI | Edinburgh |

- $\text{Flight}(x,y,z)$: the flight from airport $x$ to airport $y$ is operated by airline $z$.
- $\text{Airport}(x,y)$: airport $x$ is in city $y$.
- [[01 binding variables|Domain]]: every value in the database.
- Row: a true instance, e.g. $\text{Flight}(\text{VIE}, \text{LHR}, \text{BA})$.
- Missing row: false, e.g. $\text{Flight}(\text{LHR}, \text{VIE}, \text{OS})$, $\text{Airport}(\text{LCA}, \text{Vienna})$ — the [[01 cs/03 databases/03 the closed-world assumption|closed-world assumption]].

## Yes-or-no queries

> Is there a flight from Vienna to London?

$$\exists x\, \exists y\, \exists z\, (\text{Flight}(x,y,z) \land \text{Airport}(x, \text{Vienna}) \land \text{Airport}(y, \text{London}))$$

- Every variable [[01 binding variables|bound]]: a proposition, and its truth value is the answer.
- True — [[03 the existential quantifier|witnesses]] $x = \text{VIE}$, $y = \text{LHR}$, $z = \text{BA}$.
- The shared $x$ links $\text{Flight}$ to $\text{Airport}$ — a [[01 cs/03 databases/02 joins|join]].

## Queries that return values

> Which airlines have a flight from Vienna to London?

$$\exists x\, \exists y\, (\text{Flight}(x,y,z) \land \text{Airport}(x, \text{Vienna}) \land \text{Airport}(y, \text{London}))$$

- $z$ has no quantifier: it is [[01 binding variables|free]].
- The free variable determines the values returned: $z = \text{BA}$.
- Free variables = the result's columns — the `SELECT` list in [[01 cs/03 databases/01 SQL|SQL]].

## Routes with stops

> Is there a route from Vienna to Edinburgh?

- 1 stop: 2 flights, the first's destination is the second's origin.

$$\exists x\, \exists y\, \exists z\, \exists w\, \exists v\, (\text{Airport}(x, \text{Vienna}) \land \text{Airport}(y, \text{Edinburgh}) \land \text{Flight}(x,z,w) \land \text{Flight}(z,y,v))$$

- Yes: VIE → LHR → EDI, stopover $z = \text{LHR}$.
- For a separate Larnaca-to-Edinburgh query, replace `Vienna` with `Larnaca` in the formula. With exactly two flights the answer is no: LCA only flies to VIE, which has no direct flight to EDI.
- 2 stops: 1 more flight, new variables $z_1$, $w_1$.

$$\exists x\, \exists y\, \exists z\, \exists w\, \exists v\, \exists z_1\, \exists w_1\, (\text{Airport}(x, \text{Vienna}) \land \text{Airport}(y, \text{Edinburgh}) \land \text{Flight}(x,z,w) \land \text{Flight}(z,z_1,w_1) \land \text{Flight}(z_1,y,v))$$

- As written, this asks for three flights from Vienna; it is false in the displayed table.
- Replacing `Vienna` with `Larnaca` makes it true: LCA → VIE → LHR → EDI.
- Two flights and three flights are exact lengths. To ask for at most three flights, use a disjunction of the one-, two-, and three-flight formulas.
- Without inequalities between airports, these formulas allow repeated airports; they describe walks rather than requiring simple paths.

### Reading the changing route diagrams

- Slides 45–49 successively add intermediate vertices to the illustrated Vienna–Edinburgh route; the two-flight formula stops matching when a third flight is needed, and the three-flight formula stops matching when a fourth is needed.
- The printed tables remain unchanged while the diagrams change. Treat the altered diagrams as separate hypothetical graphs, not as additional rows of the displayed database.
- Airport identity matters: LHR and LGW are both in London, but are different airports. Sharing a city does not establish a connecting flight or an airport transfer.

## The limit

> Is there a route with any number of stops?

- There is no single first-order formula over the flight/edge relation that expresses reachability uniformly for arbitrary finite networks of unbounded size.
- For a fixed upper bound on route length, combine the corresponding finite-length formulas with disjunction — [[00 math/07 discrete mathematics/02 graph theory/02 paths, cycles & connectivity|paths and connectivity]].
- For a known network with at most $n$ airports, distinct reachable endpoints have a simple path of at most $n-1$ flights; that bound can be expanded into a formula. The limitation concerns one formula for every network size.
- Counting the variables in a written chain motivates the limitation, but is not a proof that no other first-order formula works. See [Gaifman and Vardi on finite-graph connectivity](https://www.cs.rice.edu/~vardi/papers/beatcs85.pdf).
- Needs [[01 cs/00 programming fundamentals/06 functions/05 recursion|recursion]] — SQL's `WITH RECURSIVE`, or [[00 breadth-first search (BFS)|breadth-first search]].
