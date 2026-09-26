# 01 - Δομή Προγράμματος Java

➕ Συμπληρωματική σημείωση: ο «σκελετός» που εμφανίζεται σε **κάθε** παράδειγμα των διαφανειών, χωρίς να εξηγείται εκεί (η Ενότητα I δεν υπάρχει στο υλικό).

## 1. Ο σκελετός

```java
public class IntOps {                          // όνομα κλάσης = όνομα αρχείου (IntOps.java)
    public static void main(String[] args) {   // εδώ ξεκινά η εκτέλεση
        int a = Integer.parseInt(args[0]);     // κάθε εντολή τελειώνει με ;
        System.out.println(a);
    }
}
```

> [!note] Κανόνες
> - Ένα αρχείο `X.java` περιέχει την `public class X` – **ίδιο όνομα, ίδια κεφαλαία/μικρά**.
> - Η εκτέλεση ξεκινά πάντα από την `public static void main(String[] args)`.
> - Η Java είναι **case-sensitive**: `System` ≠ `system`, `Main` ≠ `main`.
> - Τα `{ }` ορίζουν **μπλοκ** (σώμα κλάσης, μεθόδου, βρόχου…). Το `;` τερματίζει **εντολή**, όχι μπλοκ.

## 2. Μεταγλώττιση και εκτέλεση

| Βήμα | Εντολή | Αποτέλεσμα |
|---|---|---|
| Μεταγλώττιση | `javac IntOps.java` | Δημιουργεί `IntOps.class` (bytecode) ή βγάζει **compile errors** |
| Εκτέλεση | `java IntOps 1234 99` | Η JVM τρέχει τη `main`· τα `1234`, `99` γίνονται `args[0]`, `args[1]` |

> [!warning] Συχνά λάθη εκτέλεσης
> - `java IntOps.class` ✗ → γράφεις **το όνομα της κλάσης**, όχι του αρχείου.
> - Άλλαξες τον κώδικα αλλά δεν ξανάτρεξες `javac` → τρέχει η **παλιά** έκδοση.
> - **Ελληνικά σε Windows:** αν το αρχείο έχει ελληνικά (σε σχόλια, strings ή ονόματα μεταβλητών), το `javac` στα Windows μπορεί να βγάλει `unmappable character for encoding windows-1252`. Λύση: `javac -encoding UTF-8 IntOps.java`.

## 3. Ορίσματα γραμμής εντολής (command-line arguments)

> [!note] `String[] args`
> Ό,τι γράψεις μετά το όνομα της κλάσης μπαίνει στον πίνακα `args` **ως `String`**, χωρισμένο με κενά.
> Για αριθμούς χρειάζεται μετατροπή: `Integer.parseInt(args[0])`, `Double.parseDouble(args[1])`.

| Εκτέλεση | Τι γίνεται |
|---|---|
| `java Quadratic -3.0 2.0` | ✓ `args[0] = "-3.0"`, `args[1] = "2.0"` |
| `java Quadratic 1.0 hello` | ✗ `java.lang.NumberFormatException: hello` (runtime) |
| `java Quadratic 1.0` | ✗ `java.lang.ArrayIndexOutOfBoundsException` – δεν υπάρχει `args[1]` |
| `java IntOps 5.0 2` | ✗ `NumberFormatException` – το `parseInt` **δεν** δέχεται δεκαδικό |
| `java Hello "New York"` | Τα εισαγωγικά κάνουν το `New York` **ένα** όρισμα |

Για ένα χαρακτήρα: `char c = args[0].charAt(0);` (χρησιμοποιείται στο `switch` και στο `PrintChars` της Ενότητας III).

## 4. Έξοδος

| Μέθοδος | Τι κάνει |
|---|---|
| `System.out.println(x)` | Τυπώνει `x` **και** αλλάζει γραμμή |
| `System.out.println()` | Μόνο αλλαγή γραμμής (κενή γραμμή) |
| `System.out.print(x)` | Τυπώνει `x` **χωρίς** αλλαγή γραμμής |
| `System.out.printf(fmt, …)` | Μορφοποιημένη έξοδος (δεν αλλάζει γραμμή μόνη της) |

### `printf` – οι προσδιοριστές που χρειάζεσαι

| Προσδιοριστής | Τύπος | Παράδειγμα | Έξοδος |
|---|---|---|---|
| `%d` | ακέραιος | `printf("%d", 42)` | `42` |
| `%5d` | ακέραιος σε πλάτος 5 (δεξιά στοίχιση) | `printf("%5d", 42)` | `   42` |
| `%-5d` | πλάτος 5, αριστερή στοίχιση | `printf("%-5d\|", 42)` | `42   \|` |
| `%f` / `%.2f` | πραγματικός (2 δεκαδικά) | `printf("%.2f", 3.14159)` | `3.14` |
| `%c` | χαρακτήρας | `printf("%c", 'x')` | `x` |
| `%s` | String | `printf("%s", "hi")` | `hi` |
| `%n` ή `\n` | αλλαγή γραμμής | | |

> [!warning] Παγίδες `printf`
> - `printf("%d", 3.5)` → **runtime** `IllegalFormatConversionException` (το `%d` θέλει ακέραιο).
> - `printf("%.2f", 3)` → ίδιο πρόβλημα (το `3` είναι `int`). Γράψε `3.0`.

Στη διαφάνεια III-56: `System.out.printf("\t%c%4d", c, (int)c);` = tab, χαρακτήρας, κωδικός σε πλάτος 4.

## 5. Είσοδος από το πληκτρολόγιο

```java
import java.util.Scanner;                 // πριν από την class

Scanner in = new Scanner(System.in);
int A = in.nextInt();                     // διαβάζει int
double d = in.nextDouble();               // διαβάζει double
String w = in.next();                     // μία λέξη
String line = in.nextLine();              // ολόκληρη γραμμή
```

> [!warning] Η παγίδα `nextInt()` + `nextLine()`
> Μετά από `nextInt()` το `Enter` μένει στην είσοδο· το επόμενο `nextLine()` επιστρέφει αμέσως **κενό** `""`. Λύση: ένα επιπλέον `in.nextLine();` για να «φάει» το υπόλοιπο της γραμμής.

> [!info]- `StdIn` / `StdOut` των διαφανειών
> Οι διαφάνειες III-61, IV-49 χρησιμοποιούν `StdIn.readDouble()` και `StdOut.println(...)`. Αυτές **δεν** είναι μέρος της Java· είναι βιβλιοθήκες του βιβλίου (booksite, `stdlib.jar`) που πρέπει να υπάρχουν στο classpath. Το `StdOut.println` συμπεριφέρεται όπως το `System.out.println`, το `StdIn.readDouble()` όπως το `Scanner.nextDouble()`.

## 6. Σχόλια

```java
// σχόλιο μίας γραμμής
/* σχόλιο
   πολλών γραμμών */
/** σχόλιο τεκμηρίωσης (Javadoc) */
```

Στη διαφάνεια III-16: `if (x == 0); /* do nothing */ else y = 1/x;` – το σχόλιο δεν αλλάζει τίποτα, η κενή εντολή είναι το `;`.

## 7. Ονόματα (identifiers)

> [!note] Κανόνες
> - Γράμματα, ψηφία, `_`, `$` · **δεν** ξεκινούν με ψηφίο · όχι δεσμευμένες λέξεις (`int`, `class`, `for`, `true`…).
> - ✓ `count`, `x_big`, `START_CHAR`, `$tmp` · ✗ `2x`, `my-var`, `class`, `is prime`

| Σύμβαση | Χρήση | Παράδειγμα |
|---|---|---|
| `camelCase` | μεταβλητές, μέθοδοι | `isLeapYear`, `perLine` |
| `PascalCase` | κλάσεις | `LeapYear`, `PrintChars` |
| `UPPER_CASE` | σταθερές | `START_CHAR`, `SUITS` |

## 8. Είδη σφαλμάτων

| Είδος | Πότε | Παράδειγμα |
|---|---|---|
| **Μεταγλώττισης** (compile-time) | Το `javac` αρνείται | `int x = 5.0;` · λείπει `;` · `int` αντί `boolean` σε `if` |
| **Εκτέλεσης** (runtime / exception) | Το πρόγραμμα «σκάει» ενώ τρέχει | `1 / 0` → `ArithmeticException` · `args[1]` χωρίς όρισμα |
| **Λογικό** (logic error) | Τρέχει αλλά δίνει λάθος αποτέλεσμα | `(a + b) / 2` με `int` αντί για `double` μέσο όρο |

> [!tip] Στις εξετάσεις
> Όταν σε ρωτούν «τι τυπώνει;», πρώτα ρώτα «**κάνει compile;**». Πολλές ερωτήσεις-παγίδες έχουν απάντηση «σφάλμα μεταγλώττισης».

## Συχνά Λάθη

> [!warning] Συχνά Λάθη
> - `public class Main` σε αρχείο `IntOps.java` → compile error.
> - `System.out.printLn` / `printnl` → compile error (typo – υπάρχει και στις διαφάνειες III-31, III-46!).
> - Ξεχνάς το `import java.util.Scanner;`.
> - Χρησιμοποιείς `args[0]` σαν αριθμό χωρίς `parseInt`: `args[0] + 1` με `args[0] = "5"` δίνει `"51"`.

## Σχετικά

- Επόμενο: [[02 - Τύποι Δεδομένων, Μεταβλητές και Ανάθεση]]
- Μετατροπή `String` → αριθμού: [[08 - Μετατροπή Τύπων]]
- Γρήγορη επανάληψη: [[10 - Τυπολόγιο]] · Εξάσκηση: [[11 - Ασκήσεις]]
- Ευρετήριο: [[Uni/ΕΠΛ131/ΕΠΛ131 II Βασικοί Τύποι Δεδομένων/00 - Ευρετήριο|00 - Ευρετήριο]]
