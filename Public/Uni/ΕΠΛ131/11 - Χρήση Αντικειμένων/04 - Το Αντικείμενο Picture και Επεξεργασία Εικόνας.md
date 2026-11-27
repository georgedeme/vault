---
publish: true
---
# 04 - Το Αντικείμενο Picture και Επεξεργασία Εικόνας

Ο αφηρημένος τύπος **`Picture`** (raster γραφικά), η **τροποποιησιμότητα (mutability)** σε αντίθεση με την `Color`, και τρία πλήρη φίλτρα επεξεργασίας εικόνας: **`Grayscale`**, **`Scale`** και **`ColorSeparation`** (διαφάνειες XI-52 … XI-66).

## 1. Το Αντικείμενο `Picture` (XI-29, XI-30, XI-52)

Η `Picture` είναι κλάση της βιβλιοθήκης του βιβλίου του μαθήματος (Sedgewick & Wayne) και αναπαριστά **raster γραφικά**: ένα δισδιάστατο πλέγμα από εικονοστοιχεία (**pixels**), όπου κάθε pixel είναι ένα αντικείμενο **`Color`** (XI-30, XI-52).

> *«Η εσωτερική αναπαράσταση των pictures και colors δεν μας αφορά!!» (XI-29) — μπορούμε όμως να τη φανταζόμαστε σαν έναν 2D πίνακα από αναφορές σε αντικείμενα `Color` (XI-30).*

### API της `Picture` (XI-52, XI-53)

| Μέθοδος | Κατηγορία | Περιγραφή |
|---|---|---|
| `Picture(String filename)` | Κατασκευαστής | Φορτώνει εικόνα από υπάρχον αρχείο (π.χ. `.jpg`, `.png`) |
| `Picture(int w, int h)` | Κατασκευαστής | Δημιουργεί κενή (μαύρη) εικόνα πλάτους `w` και ύψους `h` |
| `int width()` | Ανακτητής | Επιστρέφει το πλάτος της εικόνας (αριθμός στηλών) |
| `int height()` | Ανακτητής | Επιστρέφει το ύψος της εικόνας (αριθμός γραμμών) |
| `Color get(int i, int j)` | Ανακτητής | Επιστρέφει το `Color` του pixel `(i, j)` |
| `void set(int i, int j, Color c)` | **Μεταλλάκτης** | Θέτει το χρώμα του pixel `(i, j)` σε `c` |
| `void show()` | Μέθοδος αναφοράς | Εμφανίζει την εικόνα σε παράθυρο |
| `void save(String filename)` | Μέθοδος αναφοράς | Αποθηκεύει την εικόνα σε αρχείο |

> [!warning] ⚠️ Σημείωση (XI-52 & XI-58) — Σειρά συντεταγμένων `(i, j)` στη `Picture`
> - Το pixel **`(0, 0)`** βρίσκεται **πάνω αριστερά** (όχι κάτω αριστερά όπως στη `StdDraw`!).
> - Στα διαγράμματα των XI-52 και XI-58 ο δείκτης `i` σημειώνεται κάθετα και ο `j` οριζόντια (και η XI-58 γράφει «δείκτη γραμμής σε $w_s/w_t$», «δείκτη στήλης σε $h_s/h_t$»).
> - **Στον πραγματικό κώδικα** (`Grayscale` XI-54, `Scale` XI-59, `ColorSeparation` XI-63) και στην κλάση `Picture`, ισχύει το **αντίστροφο**:
>   - το **1ο όρισμα `i`** είναι η **στήλη (`0 .. width() - 1`, οριζόντια)**,
>   - το **2ο όρισμα `j`** είναι η **γραμμή (`0 .. height() - 1`, κάθετα)**.
> - Δηλαδή **`pic.get(col, row)`** και **`pic.set(col, row, c)`**! Αν τα αντιστρέψεις σε μη τετράγωνη εικόνα (π.χ. `400×200`), θα πάρεις `IndexOutOfBoundsException`.

## 2. Τροποποιησιμότητα (Mutability) της `Picture` (XI-53)

> [!important] `Picture` (mutable) έναντι `Color` & `String` (immutable)
> - Επειδή η `Picture` περιλαμβάνει τον **μεταλλάκτη `set(i, j, c)`**, η εσωτερική κατάστασή της είναι **τροποποιήσιμη (mutable)**.
> - Κατ' επέκταση, αν υπάρχουν **πολλαπλές αναφορές** στην ίδια εικόνα (`Picture p2 = p1;`), αλλάζοντας ένα pixel μέσω της `p2.set(…)`, **επηρεάζεται και η `p1`**!
> - Αντίθετα, οι `Color` και `String` δεν έχουν μεταλλάκτες — είναι **αμετάβλητες (immutable)**.

| Κλάση | Μεταλλάκτες | Είδος | Αν `b = a;` και καλέσω μέθοδο στην `b`… |
|---|---|---|---|
| `String`, `Color` | Κανένας | **Αμετάβλητη (immutable)** | Η `a` **δεν** μπορεί να αλλάξει ποτέ (`darker()`, `substring()` φτιάχνουν νέο αντικείμενο) |
| `DeckObj`, `GLife`, `TicTacToe`, `Picture` | `shuffle()`, `evolve()`, `Game()`, `set()` | **Τροποποιήσιμη (mutable)** | Η `a` **αλλάζει** μαζί με τη `b` (ίδιο αντικείμενο στη μνήμη) |

## 3. Φίλτρο 1: `Grayscale` (XI-54 … XI-57)

Μετατρέπει μια έγχρωμη εικόνα σε μαυρόασπρη (αποχρώσεις του γκρι) χρησιμοποιώντας τη `Luminance.toGray(color)`:

```java
import java.awt.Color;

public class Grayscale {
   public static void main(String[] args) {
      Picture pic = new Picture(args[0]);
      for (int i = 0; i < pic.width(); i++) {
         for (int j = 0; j < pic.height(); j++) {
            Color color = pic.get(i, j);
            Color gray  = Luminance.toGray(color);
            pic.set(i, j, gray);
         }
      }
      pic.show();
   }
}
```

- Η `Grayscale` τροποποιεί την `pic` **επί τόπου (in-place)** στη μνήμη, αντικαθιστώντας κάθε pixel `(i, j)` με την απόχρωση του γκρι.
- **Προσοχή (XI-55):** <span class="hl-yellow">Το αρχείο στον δίσκο (`mandrill.jpg`) ΔΕΝ αλλάζει!</span> Αλλάζει μόνο αν αποθηκεύσουμε ρητά την εικόνα με `pic.save(args[0])` (ή σε νέο όνομα αρχείου).

## 4. Φίλτρο 2: Κλιμάκωση `Scale` (XI-58 … XI-61)

**Στόχος:** συρρίκνωση (downscaling) ή μεγέθυνση (upscaling) μιας πηγαίας εικόνας $w_s \times h_s$ σε νέα εικόνα στόχο $w_t \times h_t$.

**Ομοιόμορφη στρατηγική (XI-58):** για κάθε pixel `(ti, tj)` της εικόνας στόχου, βρίσκουμε το αντίστοιχο pixel `(si, sj)` στην πηγαία εικόνα:
$$s_i = \left\lfloor \frac{t_i \cdot w_s}{w_t} \right\rfloor, \qquad s_j = \left\lfloor \frac{t_j \cdot h_s}{h_t} \right\rfloor$$

```java
import java.awt.Color;

public class Scale {
   public static void main(String args[]) {
      String filename = args[0];
      int w = Integer.parseInt(args[1]);
      int h = Integer.parseInt(args[2]);
      Picture source = new Picture(filename);
      Picture target = new Picture(w, h);
      for (int ti = 0; ti < w; ti++) {
         for (int tj = 0; tj < h; tj++) {
            int si = ti * source.width()  / w;
            int sj = tj * source.height() / h;
            Color color = source.get(si, sj);
            target.set(ti, tj, color);
         }
      }
      source.show();
      target.show();
   }
}
```

![[Αντικείμενα - Picture, Mutability και Scale.png|800]]

> [!warning] ➕ Δύο κρίσιμες λεπτομέρειες στο `Scale`
> 1. **Σειρά πράξεων στην ακέραια διαίρεση**: πρέπει να γράψουμε **`ti * source.width() / w`** (πρώτα πολλαπλασιασμός, μετά διαίρεση). Αν γράψουμε `(ti / w) * source.width()`, επειδή `0 ≤ ti < w`, η ακέραια διαίρεση `ti / w` δίνει **πάντα `0`** — όλη η `target` θα γεμίσει με το χρώμα του pixel `(0, 0)`!
> 2. **Κοινές αναφορές `Color` (aliasing) στο upscaling/downscaling**: η `target.set(ti, tj, color)` δεν δημιουργεί νέα αντικείμενα `Color`· βάζει στην `target` **αναφορά στο ίδιο αντικείμενο `Color`** που βρίσκεται στη `source` (και στο upscaling, πολλά γειτονικά pixels της `target` δείχνουν στο ίδιο `Color`!). Αυτό είναι **απόλυτα ασφαλές** ακριβώς επειδή η `Color` είναι **αμετάβλητη** (XI-33)!

## 5. Φίλτρο 3: Διαχωρισμός Χρωμάτων `ColorSeparation` & Άλλα Φίλτρα (XI-62 … XI-64)

Εκτός από `Grayscale` και `Scale`, με το ίδιο μοτίβο (`get`/`set`) υλοποιούνται φίλτρα όπως **RGB διαχωρισμός χρώματος**, **swirl**, **wave**, **glass**, και **Sobel εντοπισμός ακμής** (XI-62).

Η `ColorSeparation` (XI-63) διαχωρίζει μια εικόνα στα τρία βασικά κανάλια **R**, **G**, **B**, δημιουργώντας τρεις νέες εικόνες ίδιων διαστάσεων:

```java
import java.awt.Color;

public class ColorSeparation {
   public static void main(String args[]) {
      Picture pic = new Picture(args[0]);
      int width  = pic.width();
      int height = pic.height();

      Picture R = new Picture(width, height);
      Picture G = new Picture(width, height);
      Picture B = new Picture(width, height);

      for (int i = 0; i < width; i++) {
         for (int j = 0; j < height; j++) {
            Color c = pic.get(i, j);
            int r = c.getRed();
            int g = c.getGreen();
            int b = c.getBlue();
            R.set(i, j, new Color(r, 0, 0));
            G.set(i, j, new Color(0, g, 0));
            B.set(i, j, new Color(0, 0, b));
         }
      }
      R.show();
      G.show();
      B.show();
   }
}
```

Εδώ η `pic` παραμένει **ανέπαφη** (δεν καλείται `pic.set`), ενώ δημιουργούνται 3 νέα αντικείμενα `Picture` και 3 νέα αντικείμενα `Color` ανά pixel.

## Συχνά Λάθη

- **Αντιστροφή `width()` και `height()` στους βρόχους**: `for (int i = 0; i < pic.height(); i++)` με `pic.get(i, j)` → `IndexOutOfBoundsException` σε μη τετράγωνη εικόνα. Θυμήσου: `get(col, row)` → `i < width()`, `j < height()`.
- **Να νομίζεις ότι `pic.set(…)` αλλάζει το αρχείο `.jpg`**: αλλάζει μόνο το αντικείμενο στη μνήμη· το αρχείο στον δίσκο αλλάζει **μόνο** με `pic.save(…)`.
- **Ακέραια διαίρεση `(ti / w) * source.width()` στο `Scale`**: δίνει πάντα `0`! Πάντα πρώτα πολλαπλασιασμός: `ti * source.width() / w`.
- **Να ξεχάσεις ότι η `Picture` είναι mutable**: αν γράψεις `Picture copy = source;` και κάνεις grayscale στο `copy`, χάλασες και το `source`! Για ανεξάρτητο αντίγραφο πρέπει να φτιάξεις `new Picture(w, h)` και να αντιγράψεις τα pixels.

## Σχετικά

- Ευρετήριο: [[Uni/ΕΠΛ131/11 - Χρήση Αντικειμένων/00 - Ευρετήριο|00 - Ευρετήριο]]
- Προηγούμενη σημείωση: [[03 - Το Αντικείμενο Color και η Κλάση Luminance]]
- Τυπολόγιο: [[Uni/ΕΠΛ131/11 - Χρήση Αντικειμένων/05 - Τυπολόγιο|05 - Τυπολόγιο]] · Ασκήσεις: [[Uni/ΕΠΛ131/11 - Χρήση Αντικειμένων/06 - Ασκήσεις|06 - Ασκήσεις]]
- Επόμενη ενότητα (πώς υλοποιούμε εμείς αντικείμενα): [[Uni/ΕΠΛ131/12 - Δημιουργία Αντικειμένων/00 - Ευρετήριο|Ενότητα XII – Δημιουργία Αντικειμένων]]
