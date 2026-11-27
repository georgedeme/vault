---
publish: true
---
# 05 - Αμετάβλητα Αντικείμενα - Charge και Οπτικοποίηση Δυναμικού

Σχεδίαση ενός καθαρού, <span class="hl-blue">αμετάβλητου (immutable)</span> τύπου δεδομένων (`Charge`) από το API μέχρι την υλοποίηση και τον πελάτη (`Potential`), και πώς το χρησιμοποιούμε με πίνακα αντικειμένων και `Picture` (διαφάνειες XII-41 … XII-49).

## 1. Προδιαγραφή & API του `Charge` (XII-42, XII-43)

- **Στόχος**: Τύπος δεδομένων που αναπαριστά ένα σημειακό ηλεκτρικό φορτίο $q$ στη θέση $(r_x, r_y)$.
- **Σύνολο τιμών**: Τρεις πραγματικοί αριθμοί (`double`): `rx`, `ry`, `q`.
- **Ηλεκτρικό δυναμικό** στο σημείο $(x, y)$:
  $$V = k \frac{q}{r}, \qquad r = \sqrt{(r_x - x)^2 + (r_y - y)^2}, \qquad k = 8.99 \times 10^9\ \text{N}\cdot\text{m}^2/\text{C}^2$$

| API της `public class Charge` (XII-43) | Περιγραφή |
|---|---|
| `Charge(double x0, double y0, double q0)` | Δημιουργεί φορτίο $q_0$ στη θέση $(x_0, y_0)$ |
| `double potentialAt(double x, double y)` | Επιστρέφει το ηλεκτρικό δυναμικό $V$ στο $(x, y)$ λόγω του φορτίου |
| `String toString()` | Επιστρέφει τη συμβολοσειρά αναπαράστασης (π.χ. `"21.3 at (0.51, 0.63)"`) |

## 2. Αμετάβλητα (Immutable) αντικείμενα & Υλοποίηση `Charge` (XII-44, XII-46)

> [!note] Τι σημαίνει αμετάβλητο (immutable) αντικείμενο;
> Ένα αντικείμενο είναι <span class="hl-blue">αμετάβλητο (immutable)</span> αν η κατάστασή του **δεν μπορεί να αλλάξει** μετά τη δημιουργία του (όπως το `String` και το `Color`).
> Στη Java αυτό επιτυγχάνεται όταν:
> 1. Όλα τα πρωτογενή πεδία είναι **`private final`** (αρχικοποιούνται μία φορά στον κατασκευαστή και δεν μπορούν να ξανα-ανατεθούν).
> 2. Δεν υπάρχουν μέθοδοι που τροποποιούν την κατάσταση (mutators / setters) και η κλάση δεν περιέχει αναφορές σε εξωτερικά μεταβλητά αντικείμενα (ή τα αντιγράφει αμυντικά).

Η σωστή υλοποίηση της `Charge` (όπως δίνεται στο διάγραμμα ανατομίας της **XII-46**):

```java
public class Charge {
    private final double rx, ry;        // instance variables (private final → immutable!)
    private final double q;

    public Charge(double x0, double y0, double q0) {    // constructor
        rx = x0;
        ry = y0;
        q  = q0;
    }

    public double potentialAt(double x, double y) {     // instance method
        double k  = 8.99e9;
        double dx = x - rx;
        double dy = y - ry;
        return k * q / Math.sqrt(dx * dx + dy * dy);
    }

    public String toString() {                          // instance method
        return q + " at (" + rx + ", " + ry + ")";
    }

    public static void main(String[] args) {            // test client
        double x = Double.parseDouble(args[0]);
        double y = Double.parseDouble(args[1]);
        Charge c1 = new Charge(.51, .63, 21.3);
        Charge c2 = new Charge(.13, .94, 81.9);
        double v1 = c1.potentialAt(x, y);
        double v2 = c2.potentialAt(x, y);
        StdOut.println(c1);                             // καλεί αυτόματα c1.toString()
        StdOut.println(c2);                             // καλεί αυτόματα c2.toString()
        StdOut.println(v1 + v2);
    }
}
```

> [!tip] Αυτόματη κλήση της `toString()` (XII-45)
> Όταν περνάς ένα αντικείμενο στην `System.out.println(c1)` ή `StdOut.println(c1)`, ή όταν το συνενώνεις με `String` (`"" + c1`), η Java καλεί **αυτόματα** την `c1.toString()`.
> - Εκτέλεση: `% java Charge .50 .50` →
>   ```text
>   21.3 at (0.51, 0.63)
>   81.9 at (0.13, 0.94)
>   2.74936907085912e12
>   ```
> - ➕ **Τι συμβαίνει αν ΔΕΝ ορίσεις `toString()` στην κλάση σου;** Τότε καλείται η προεπιλεγμένη `Object.toString()`, η οποία τυπώνει κάτι σαν `Charge@15db9742` (όνομα κλάσης + `@` + δεκαεξαδικό hash code), **όχι** τα πεδία!

> [!warning] ⚠️ Σημειώσεις για τη διαφάνεια XII-44 (πολλαπλά σφάλματα!)
> Η διαφάνεια **XII-44** περιέχει μια πρόχειρη εκδοχή της `Charge` με **έξι** λάθη που διορθώνονται στη **XII-46**:
> 1. Στο υποσέλιδο κάτω αριστερά γράφει `ΕΠΛ131 – Ενότητα VII` αντί για `XII`.
> 2. Η σταθερά γράφεται `k = 8.9e9;` αντί για `8.99e9` (όπως στις XII-42 και XII-46).
> 3. Η μέθοδος γράφεται `pottentialAt` (με δύο `t`) αντί για `potentialAt` (όπως στο API XII-43 και στον client XII-45).
> 4. Στη `Euclidean`: `Math.sqrt((x-rx)* (x-rx)+ ((y-ry)* (y-ry);` — λείπουν δύο δεξιές παρενθέσεις `))` → σφάλμα μεταγλώττισης.
> 5. Στη `toString()`: γράφει `System.println(q + “ at ” + ...);` — τριπλό σφάλμα: (α) `System.out.println` όχι `System.println`, (β) η `toString()` πρέπει να **επιστρέφει** `String` με `return`, όχι να τυπώνει, και (γ) χρησιμοποιεί τυπογραφικά εισαγωγικά `“ ”`.
> 6. Το σημείωμα δεξιά γράφει: *«all non-reference instance variables are **static**»* — εννοεί **`final`**, όχι `static`! (Αν τα `rx, ry, q` ήταν `static`, όλα τα φορτία θα μοιράζονταν την ίδια θέση και το ίδιο φορτίο.)

## 3. Οπτικοποίηση του δυναμικού — `Potential` (XII-47 … XII-49)

Διαβάζει $N$ φορτία από αρχείο (`% java Potential < charges.txt`) σε έναν πίνακα `Charge[]` και υπολογίζει το συνολικό δυναμικό $V = \sum_i k q_i / r_i$ σε κάθε pixel μιας εικόνας `512 × 512`:

```java
// Βήμα 1: Ανάγνωση σε συστοιχία από αντικείμενα (XII-48)
int N = StdIn.readInt();
Charge[] a = new Charge[N];                 // δέσμευση μνήμης για τη συστοιχία
for (int i = 0; i < N; i++) {
    double x0 = StdIn.readDouble();
    double y0 = StdIn.readDouble();
    double q0 = StdIn.readDouble();
    a[i] = new Charge(x0, y0, q0);          // δέσμευση μνήμης για κάθε ξεχωριστό Charge
}

// Βήμα 2: Οπτικοποίηση σε Picture (XII-49)
int SIZE = 512;
Picture pic = new Picture(SIZE, SIZE);
for (int row = 0; row < SIZE; row++) {
    for (int col = 0; col < SIZE; col++) {
        double V = 0.0;
        for (int i = 0; i < N; i++) {
            double x = 1.0 * row / SIZE;
            double y = 1.0 * col / SIZE;
            V += a[i].potentialAt(x, y);    // αρχή επαλληλίας
        }
        Color color = getColor(V);          // χρώμα ως συνάρτηση του V
        pic.set(row, SIZE - 1 - col, color); // (0, 0) είναι πάνω αριστερά!
    }
}
pic.show();
```

> [!tip] Γιατί `SIZE - 1 - col` στην `pic.set(...)` (XII-49);
> Στην κλάση `Picture`, το pixel `(0, 0)` βρίσκεται **πάνω αριστερά** (ο άξονας $y$ αυξάνεται προς τα κάτω), ενώ στο καρτεσιανό μοναδιαίο τετράγωνο $[0, 1] \times [0, 1]$ το `(0, 0)` είναι **κάτω αριστερά**. Η αντιστροφή `SIZE - 1 - col` φέρνει την εικόνα στον σωστό προσανατολισμό.
> Επίσης πρόσεξε το `1.0 * row / SIZE`: χωρίς το `1.0 *`, η ακέραια διαίρεση `row / SIZE` θα έδινε πάντα `0`!

## Συχνά Λάθη

> [!warning] Συχνά Λάθη
> - Σύγχυση **`final`** με **`static`** για immutability: το `final` εμποδίζει την αλλαγή της τιμής ενός πεδίου μετά την αρχικοποίηση· το `static` το κάνει κοινό για όλα τα αντικείμενα!
> - Να γράφεις `System.out.println(...)` μέσα στη `toString()` αντί για `return ...;`: η `toString()` **επιστρέφει** `String`, δεν τυπώνει.
> - Να περιμένεις ότι `println(obj)` θα τυπώσει τα πεδία χωρίς να έχεις ορίσει `toString()` → τυπώνει `ClassName@hex`.
> - Να γράφεις `row / SIZE` αντί `1.0 * row / SIZE` → ακέραια διαίρεση, δίνει `0`.

## Σχετικά

- Προηγούμενο: [[04 - Πλήρη Παραδείγματα - DeckObj, GLife και TicTacToe]]
- Επόμενο: [[Uni/ΕΠΛ131/12 - Δημιουργία Αντικειμένων/06 - Τυπολόγιο|06 - Τυπολόγιο]]
- Ευρετήριο ενότητας: [[Uni/ΕΠΛ131/12 - Δημιουργία Αντικειμένων/00 - Ευρετήριο|00 - Ευρετήριο]]
