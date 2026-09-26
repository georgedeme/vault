# 04 - Εντολή switch

Επιλογή ανάμεσα σε πολλές περιπτώσεις με βάση την **τιμή** μιας έκφρασης (διαφάνειες III-17 … III-19).

## 1. Σύνταξη (III-17)

```
switch (έκφραση_ελέγχου) {
    σύνολο_ετικετών_1
        εντολές_1
        break;
    σύνολο_ετικετών_2
        εντολές_2
        break;
    . . .
    σύνολο_ετικετών_n
        εντολές_n
        break;
    default:
        εντολές_d
}
```
Κάθε «ετικέτα» είναι της μορφής `case σταθερά:`· ένα «σύνολο ετικετών» είναι μία ή περισσότερες διαδοχικές ετικέτες.

> [!important] Κανόνες (III-17)
> - Η **έκφραση_ελέγχου** πρέπει να είναι **βαθμωτού τύπου**, π.χ. `char` ή `int`, αλλά **όχι `double`**.
> - Μπορεί να είναι **`String`**, αλλά **όχι `boolean`**.
> - Η εκτέλεση ξεκινά από την ετικέτα που ταιριάζει και **τερματίζεται όταν φτάσουμε σε `break`** (ή στο τέλος του `switch`).
> - Αν καμία ετικέτα δεν ταιριάζει, εκτελείται το `default` (αν υπάρχει· αλλιώς τίποτα).

## 2. Παράδειγμα (III-18)

```java
char choice = args[0].charAt(0);
switch (choice) {
    case 'B': case 'b': System.out.println("B or b"); break;
    case 'W': case 'w': System.out.println("W or w"); break;
    case 'K': case 'k': System.out.println("K or k"); break;
    case 'R': case 'r': System.out.println("R or r"); break;
    default:            System.out.println("Wrong choice");
}
```

| Είσοδος | Έξοδος |
|---|---|
| `k` | `K or k` |
| `W` | `W or w` |
| `x` | `Wrong choice` |

Το `case 'B': case 'b':` είναι **σύνολο ετικετών**: και οι δύο τιμές οδηγούν στις ίδιες εντολές.

## 3. Τι ΔΕΝ επιτρέπεται (III-19)

```java
switch (year % 4 == 0) {                 // ✗ boolean έκφραση ελέγχου
    case false: isLeapYear = false; break;
    case true:  switch (year % 100 == 0) {
        …
```
**Το πιο πάνω δεν επιτρέπεται** – το `year % 4 == 0` είναι `boolean`. Για `true`/`false` υπάρχει το `if`.

> [!note] Επιτρεπτοί τύποι έκφρασης ελέγχου ➕
>
> | Τύπος | Επιτρέπεται; |
> |---|---|
> | `char`, `byte`, `short`, `int` | ✓ |
> | `String` | ✓ (σύγκριση με `equals`· αν η τιμή είναι `null` → `NullPointerException`) |
> | `long` | ✗ |
> | `float`, `double` | ✗ |
> | `boolean` | ✗ |

## 4. Fall-through: τι γίνεται χωρίς `break` ➕

> [!warning] Χωρίς `break`, η εκτέλεση «πέφτει» στην επόμενη περίπτωση
> ```java
> int sw = 2;
> switch (sw) {
>     case 1: System.out.print("one ");
>     case 2: System.out.print("two ");
>     case 3: System.out.print("three ");
>     default: System.out.println("def");
> }
> ```
> Έξοδος: **`two three def`** – ξεκινά από το `case 2` και συνεχίζει μέχρι το τέλος, αγνοώντας τις υπόλοιπες ετικέτες.
> Το fall-through είναι **σκόπιμο** στα σύνολα ετικετών (`case 'B': case 'b':`) και σχεδόν πάντα **λάθος** αλλού.

## 5. Ειδικές περιπτώσεις ➕

| Κώδικας | Αποτέλεσμα |
|---|---|
| `case 1: … case 1:` | ✗ compile: duplicate case label |
| `int y = 3; … case y:` | ✗ compile: constant expression required (η ετικέτα πρέπει να είναι **σταθερά**) |
| `final int y = 3; … case y:` | ✓ (το `final` με σταθερή τιμή μετράει ως σταθερά) |
| `byte b; switch (b) { case 200: … }` | ✗ compile: το 200 δεν χωράει σε `byte` |
| `switch (k) { }` | ✓ (κενό switch – δεν κάνει τίποτα) |
| `default` **στην αρχή**, χωρίς `break` | ✓ – αν εκτελεστεί, **πέφτει** στις επόμενες περιπτώσεις |
| `case 'a' … 'z':` (εύρος) | ✗ – δεν υπάρχουν εύρη· για εύρη χρησιμοποίησε `if` |
| `case x > 5:` | ✗ – οι ετικέτες είναι **τιμές**, όχι συνθήκες |

> [!example]- `default` στην αρχή
> ```java
> int k = 2;
> switch (k) {
>     default: System.out.println("d");
>     case 1:  System.out.println("1");
> }
> ```
> Έξοδος: `d` και μετά `1`. Το `default` επιλέγεται (καμία ετικέτα = 2) και, χωρίς `break`, η εκτέλεση συνεχίζει στο `case 1`. Η **θέση** του `default` δεν επηρεάζει πότε επιλέγεται, μόνο το τι ακολουθεί.

> [!info]- ➕ Νέα σύνταξη με `->` (Java 14+)
> ```java
> switch (k) {
>     case 1 -> System.out.println("one");
>     case 2, 3 -> System.out.println("two or three");
>     default -> System.out.println("other");
> }
> ```
> Με `->` **δεν υπάρχει fall-through** και δεν χρειάζεται `break`. Δεν εμφανίζεται στις διαφάνειες – στις εξετάσεις χρησιμοποίησε την κλασική μορφή εκτός αν σου επιτραπεί ρητά.

## 6. `switch` ή `if`;

| Χρησιμοποίησε `switch` όταν | Χρησιμοποίησε `if` όταν |
|---|---|
| συγκρίνεις **μία** έκφραση με **πολλές σταθερές τιμές** | οι συνθήκες είναι **εύρη** (`income < 47450`) |
| η έκφραση είναι `int`/`char`/`String` | η έκφραση είναι `double`, `long`, `boolean` |
| π.χ. μενού επιλογών, μήνας → ημέρες | συνδυασμοί συνθηκών με `&&`/`\|\|` |

> [!example]- Ημέρες του μήνα με fall-through
> ```java
> int days;
> switch (month) {
>     case 4: case 6: case 9: case 11:
>         days = 30; break;
>     case 2:
>         days = isLeapYear ? 29 : 28; break;
>     default:
>         days = 31;
> }
> ```

## Συχνά Λάθη

> [!warning] Συχνά Λάθη
> - Ξεχασμένο `break` → εκτελούνται και οι επόμενες περιπτώσεις.
> - `switch` σε `double` ή `boolean`.
> - Μεταβλητή (μη `final`) ως ετικέτα `case`.
> - Ξεχασμένο `default` όταν η είσοδος μπορεί να είναι άκυρη.
> - `case "yes":` με `char` επιλογέα (τύποι δεν ταιριάζουν) – `case 'y':`.

## Σχετικά

- Προηγούμενο: [[03 - Φώλιασμα Επιλογών]]
- Επόμενο: [[05 - Εντολή while και Σύνθετοι Τελεστές Ανάθεσης]]
- `break` σε βρόχους: [[Uni/ΕΠΛ131/ΕΠΛ131 IV Πίνακες Μιας Διάστασης/06 - Αναζήτηση και break|IV – 06 Αναζήτηση και break]]
- Γρήγορη επανάληψη: [[09 - Τυπολόγιο]] · Εξάσκηση: [[10 - Ασκήσεις]]
