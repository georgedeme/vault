---
publish: true
---
# 02 - Static, Ενθυλάκωση και this

Η διαφορά ανάμεσα σε <span class="hl-blue">`static` (κλάσης)</span> και <span class="hl-blue">non-static (`instance`)</span> πεδία και μεθόδους, η αρχή της <span class="hl-blue">ενθυλάκωσης (encapsulation)</span> με `public` / `private`, και η αυτο-αναφορά `this` (διαφάνειες XII-29 … XII-40).

## 1. Static πεδία vs Instance πεδία (XII-29 … XII-31)

| | `static` πεδίο (**class field / variable**) | Non-static πεδίο (**instance field / variable**) |
|---|---|---|
| **Σε ποιον ανήκει** | Στην **κλάση** — μοιράζεται ανάμεσα σε **ΌΛΑ** τα αντικείμενα | Σε κάθε **ξεχωριστό (individual)** αντικείμενο |
| **Πού αποθηκεύεται** | Με τον κώδικα της κλάσης (ένα μόνο αντίγραφο) | Μέσα στη μνήμη κάθε αντικειμένου που φτιάχνεται με `new` |
| **Αρχικοποίηση** | Στη δήλωση (ή σε `static` μέθοδο) — **όχι** σε κατασκευαστή | Στον κατασκευαστή (ή στη δήλωση) |
| **Πρόσβαση από άλλη κλάση** | `ClassName.fieldName` (dot notation, αν είναι `public`) | `objName.fieldName` (σπάνια, αφού τα πεδία είναι `private`) |

### `static final` σταθερές (XII-29, XII-30)

Ένα `static` πεδίο συχνά συνδυάζεται με `final` για να ορίσει μια **σταθερά** κοινή σε όλα τα αντικείμενα:

```java
public class RollingDie {
    private static final double slowDown    = 0.97;
    private static final double speedFactor = 0.04;
    ...
}
```

Όταν μια `static` σταθερά είναι **`public`**, λειτουργεί ως παγκόσμια σταθερά και αναφέρεται από άλλες κλάσεις με `ClassName.constName`:

```java
double area = Math.PI * r * r;
setBackground(Color.blue);
c.add(btn, BorderLayout.NORTH);
System.out.println(area);          // το out είναι public static πεδίο της System!
```

### Κλάσεις μόνο με `static` μέλη (XII-31)

Αν μια κλάση έχει **ΜΟΝΟ `static`** πεδία και **κανένα** non-static (instance) πεδίο, δεν υπάρχει λόγος να δημιουργούμε αντικείμενα αυτής της κλάσης (όλα θα ήταν πανομοιότυπα). Παραδείγματα είναι οι `Math` και `System`, οι οποίες **δεν έχουν `public` κατασκευαστές** (έχουν `private` κατασκευαστή), οπότε `new Math()` είναι σφάλμα μεταγλώττισης.

> [!warning] ⚠️ Σημείωση (XII-31)
> Στη διαφάνεια XII-31 υπάρχει απλώς τυπογραφική επανάληψη («δεν έχει κανένα ΚΑΝΕΝΑ non-static πεδίο»).

## 2. Static μέθοδοι vs Instance μέθοδοι (XII-32 … XII-35)

| | `static` μέθοδος (XII-32) | Instance (non-static) μέθοδος (XII-33) |
|---|---|---|
| **Κλήση** | `ClassName.statMethod(...)` | `objName.instMethod(...)` |
| **Παράδειγμα** | `Math.random()`, `Math.sqrt(x)`, `System.exit(0)` | `c1.potentialAt(x, y)`, `b1.move()` |
| **Πρόσβαση σε `static` πεδία/μεθόδους** | **ΝΑΙ** | **ΝΑΙ** |
| **Πρόσβαση σε non-static πεδία/μεθόδους** | **ΟΧΙ** (σφάλμα μεταγλώττισης!) | **ΝΑΙ** (σε ΟΛΑ τα πεδία & ΟΛΕΣ τις μεθόδους) |
| **Χρήση του `this`** | **ΟΧΙ** (δεν υπάρχει αντικείμενο!) | **ΝΑΙ** (`this` = το αντικείμενο που κάλεσε τη μέθοδο) |

> [!warning] ⚠️ Σημείωση (XII-32)
> Η διαφάνεια XII-32 γράφει `System.exit();` χωρίς όρισμα. Στη Java η `System.exit(int status)` απαιτεί ακέραιο κωδικό εξόδου (π.χ. `System.exit(0);` για κανονικό τερματισμό).

![[Αντικείμενα - Static vs Instance και Πρόσβαση.png|800]]

### Το παράδειγμα `MyClass` (XII-34)

```java
public class MyClass {
    public static final int statConst = 10;  // static σταθερά
    private static int statVar;              // static πεδίο
    private int instVar;                     // instance πεδίο

    public static int statMethod(...) {
        statVar = statConst;                 // ✓ OK (static → static)
        statMethod2(...);                    // ✓ OK (static → static)

        instVar = ...;                       // ✗ Error! (static → instance)
        instMethod(...);                     // ✗ Error! (static → instance)
    }

    public int instMethod(...) {
        statVar = statConst;                 // ✓ OK
        instVar = statConst;                 // ✓ OK
        instVar = statMethod(...);           // ✓ OK
        statVar = instMethod2(...);          // ✓ OK
    }
}
```

> [!warning] ⚠️ Σημείωση (XII-34)
> Στη διαφάνεια XII-34 ο κώδικας είναι ενδεικτικός σκελετός: δηλώνει `public static final int statConst;` χωρίς αρχική τιμή (στην πράξη ένα `static final` πεδίο πρέπει να αρχικοποιηθεί στη δήλωση ή σε `static { ... }` block) και οι μέθοδοι επιστροφής `int` δεν έχουν `return`.

## 3. Η παγίδα της `main` (XII-35)

<span class="hl-yellow">Η `main` είναι `static`!</span> Άρα **ΔΕΝ** μπορεί να έχει απευθείας πρόσβαση σε non-static πεδία ή να καλεί non-static μεθόδους της ίδιας κλάσης:

```java
public class Hello {
    private String message = "Hello, World";

    public static void main(String[] args) {
        System.out.println(message);    // ✗ Error: non-static variable message
                                        //   cannot be referenced from a static context
    }
}
```

> [!tip] ➕ Πώς διορθώνεται (2 τρόποι)
> 1. Κάνεις το πεδίο `static`: `private static String message = "Hello, World";` (αν ανήκει στην κλάση).
> 2. Δημιουργείς πρώτα **αντικείμενο** μέσα στη `main` και αναφέρεσαι μέσω αυτού:
>    ```java
>    Hello h = new Hello();
>    System.out.println(h.message);     // ✓ OK (μέσα στην ίδια κλάση επιτρέπεται και το private!)
>    ```
>    Αυτό ακριβώς κάνει η `TicTacToe.main` στη XII-17: `TicTacToe ttt = new TicTacToe(); ttt.game();`.

## 4. Ενθυλάκωση (Encapsulation) και `public` vs `private` (XII-36 … XII-38)

> [!note] Ορισμός (XII-36)
> Η απόκρυψη (**hiding**) των λεπτομερειών της υλοποίησης (**implementation details**) μιας κλάσης ονομάζεται <span class="hl-blue">ενθυλάκωση (encapsulation)</span>.

- Επιτυγχάνεται κάνοντας **ΟΛΑ τα πεδία** και τις **βοηθητικές μεθόδους** (που χρειάζονται μόνο εντός της κλάσης) **`private`**.
- Οι **`public` κατασκευαστές και μέθοδοι** συνιστούν τη **διεπαφή (interface)** της κλάσης προς τις άλλες κλάσεις που τη χρησιμοποιούν (**πελάτες / clients**).
- Οι `static` σταθερές (`static final`) ενίοτε ορίζονται `public`.
- **Γιατί βοηθά στη συντήρηση;** Μπορείς να αλλάξεις την εσωτερική υλοποίηση (π.χ. πώς αποθηκεύονται τα δεδομένα) χωρίς να «σπάσει» ο κώδικας κανενός πελάτη, εφόσον η `public` διεπαφή μένει ίδια.

> [!warning] ⚠️ Σημείωση (XII-38)
> Στο πρότυπο της διαφάνειας XII-38 αναφέρονται ενδεικτικά `public <sometype> myMethod(...)` και `private <sometype> myMethod(...)`. Θυμήσου ότι δύο μέθοδοι στην ίδια κλάση **δεν** μπορούν να έχουν το ίδιο όνομα και την ίδια λίστα παραμέτρων, ακόμα κι αν η μία είναι `public` και η άλλη `private`.

## 5. Πρόσβαση σε `private` πεδία άλλου αντικειμένου (XII-39)

> [!important] Κρίσιμος κανόνας Java (XII-39)
> <span class="hl-yellow">Το `private` ισχύει σε επίπεδο **κλάσης**, όχι σε επίπεδο μεμονωμένου αντικειμένου!</span>
> Οποιοδήποτε αντικείμενο (μέθοδος/κατασκευαστής) της **ίδιας κλάσης** μπορεί να διαβάσει **και να τροποποιήσει** τα `private` πεδία ενός άλλου αντικειμένου της ίδιας κλάσης.

```java
public class Fraction {
    private int num, denom;
    ...
    public Fraction multiply(Fraction other) {
        int newNum = num * other.num;       // ✓ ΕΠΙΤΡΕΠΕΤΑΙ! Παρόλο που το num είναι private!
        int newDen = denom * other.denom;
        return new Fraction(newNum, newDen);
    }
}
```

Το ίδιο βλέπουμε και:
- στον copy constructor `DeckObj(DeckObj d)` → `d.deck.length`, `d.deck[i]` (XII-5),
- στη `DeckObj.equals(DeckObj d)` → `d.deck[i]` (XII-6),
- στη `Ball.collisionMove(Ball[] bs, int n)` → `bs[i].rx`, `bs[i].ry` (XII-68).

## 6. Η αυτο-αναφορά `this` (XII-40)

> [!note] Ορισμός (XII-40)
> Το <span class="hl-blue">`this`</span> είναι μια προκαθορισμένη μεταβλητή αναφοράς διαθέσιμη μέσα σε κάθε **μέθοδο αναφοράς (instance method)** και κάθε **κατασκευαστή**, η οποία δείχνει στο **ίδιο το αντικείμενο** πάνω στο οποίο κλήθηκε η μέθοδος.

```java
public Fraction multiply(Fraction other) {
    int newNum = this.num * other.num;      // ισοδύναμο με num * other.num
    ...
}
```

### Οι 3 βασικές χρήσεις του `this`

| Χρήση | Παράδειγμα | Πού εμφανίζεται |
|---|---|---|
| **1. Διάκριση πεδίου από παράμετρο (shadowing)** ➕ | `public Point(int x, int y) { this.x = x; this.y = y; }` | Όταν η παράμετρος έχει το ίδιο όνομα με το πεδίο (`x = x;` χωρίς `this` δεν αλλάζει το πεδίο!) |
| **2. Κλήση άλλου κατασκευαστή** | `public TicTacToe() { this(3); }` · `this(n, 1);` | XII-12, XII-26 (πάντα 1η εντολή) |
| **3. Πέρασμα του εαυτού μας ως όρισμα** | `System.out.println(this + "\nFirst to play...");` | XII-13, XII-14 (καλεί αυτόματα την `this.toString()`) |

> [!warning] ➕ `this` μέσα σε `static` μέθοδο
> Η χρήση `this` μέσα σε `static` μέθοδο (όπως η `main`) δίνει **σφάλμα μεταγλώττισης** (`non-static variable this cannot be referenced from a static context`).

## Συχνά Λάθη

> [!warning] Συχνά Λάθη
> - Κλήση non-static μεθόδου ή πεδίου απευθείας από τη `main` χωρίς να έχει δημιουργηθεί αντικείμενο με `new`.
> - Να νομίζεις ότι `other.num` απαγορεύεται επειδή το `num` είναι `private`: μέσα στην κλάση `Fraction` **επιτρέπεται**! Απαγορεύεται μόνο έξω από την κλάση `Fraction`.
> - **Shadowing bug**: `public Point(int x) { x = x; }` αναθέτει την παράμετρο στον εαυτό της και αφήνει το πεδίο `this.x` στην τιμή `0`!
> - Αλλαγή ενός `static` πεδίου από ένα αντικείμενο (`a.count++`): αλλάζει για **όλα** τα αντικείμενα της κλάσης, όχι μόνο για το `a`.
> - Προσπάθεια `new Math()` ή `new System()` (οι κατασκευαστές τους είναι `private`).

## Σχετικά

- Προηγούμενο: [[01 - Δομή Κλάσης, Κατασκευαστές και Μέθοδοι]]
- Επόμενο: [[03 - Αναφορές, Ψευδώνυμα και Πέρασμα δια Τιμής]]
- Ευρετήριο ενότητας: [[Uni/ΕΠΛ131/12 - Δημιουργία Αντικειμένων/00 - Ευρετήριο|00 - Ευρετήριο]]
