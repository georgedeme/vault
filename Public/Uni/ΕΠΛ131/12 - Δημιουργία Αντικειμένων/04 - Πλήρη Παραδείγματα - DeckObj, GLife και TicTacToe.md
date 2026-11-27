---
publish: true
---
# 04 - Πλήρη Παραδείγματα - DeckObj, GLife και TicTacToe

Τρία ολοκληρωμένα αντικειμενοστραφή παραδείγματα από τις διαφάνειες (XII-3 … XII-17) που δείχνουν στην πράξη πώς συνδυάζονται τα ιδιωτικά πεδία, οι κατασκευαστές, οι βοηθητικές `private` μέθοδοι, η `toString()`, η `equals()` και το `this`.

## 1. Αντικείμενο `DeckObj` — Τράπουλα (XII-4 … XII-6)

Η `DeckObj` αναπαριστά μια τράπουλα 52 φύλλων με **ένα μόνο ιδιωτικό πεδίο** (`private String[] deck;`):

```java
public class DeckObj { // Αντικείμενο Τράπουλα
    private String[] deck; // μόνο ένα πεδίο

    public DeckObj() { // βασικός κατασκευαστής
        String[] suit = { "Clubs", "Diamonds", "Hearts", "Spades" };
        String[] rank = { "2", "3", "4", "5", "6", "7", "8", "9",
                          "10", "Jack", "Queen", "King", "Ace" };
        int SUITS = suit.length;
        int RANKS = rank.length;
        int N = SUITS * RANKS;

        deck = new String[N];
        for (int i = 0; i < RANKS; i++)
            for (int j = 0; j < SUITS; j++)
                deck[SUITS * i + j] = rank[i] + " of " + suit[j];
    }

    public DeckObj(DeckObj d) { // αντιγραφέας-κατασκευαστής (copy constructor)
        deck = new String[d.deck.length];
        for (int i = 0; i < deck.length; i++)
            deck[i] = d.deck[i];
    }

    public boolean equals(DeckObj d) {
        for (int i = 0; i < deck.length; i++)
            if (!deck[i].equals(d.deck[i])) return false;
        return true;
    }

    public void shuffle() {
        int N = deck.length;
        for (int i = 0; i < N; i++) {
            int r = i + (int) (Math.random() * (N - i));
            String t = deck[r];
            deck[r] = deck[i];
            deck[i] = t;
        }
    }

    public String toString() {
        String ds = "";
        for (String s : deck)
            ds += ("\n" + s);
        return ds;
    }
}
```

### Τι αξίζει να προσέξεις στη `DeckObj`

| Σημείο | Γιατί έχει σημασία |
|---|---|
| **Copy constructor** `DeckObj(DeckObj d)` | Φτιάχνει **νέο** πίνακα `new String[d.deck.length]` και αντιγράφει κάθε στοιχείο. Αν έγραφε `deck = d.deck;`, οι δύο τράπουλες θα μοιράζονταν τον **ίδιο** πίνακα (aliasing) και το `d1.shuffle()` θα ανακάτευε και τη `d2`! Επειδή τα `String` είναι αμετάβλητα (immutable), η αντιγραφή `deck[i] = d.deck[i]` είναι απολύτως ασφαλής. |
| **`d.deck`** (ιδιωτικό πεδίο) | Επιτρέπεται μέσα στη `DeckObj(DeckObj d)` και τη `equals(DeckObj d)` γιατί το `private` ισχύει ανά **κλάση** ([[02 - Static, Ενθυλάκωση και this#5. Πρόσβαση σε private πεδία άλλου αντικειμένου (XII-39)|02 §5]]). |
| **`shuffle()`** | Κλασικός αλγόριθμος ανακατέματος (Fisher–Yates / Knuth): για κάθε `i` επιλέγει τυχαία θέση `r` στο `[i, N-1]` και αντιμεταθέτει `deck[i]` ↔ `deck[r]`. |
| **`toString()`** | Χρησιμοποιεί βρόχο `for-each` (`for (String s : deck)`) και επιστρέφει μία συμβολοσειρά με όλα τα φύλλα (ένα ανά γραμμή). |

> [!warning] ➕ Παγίδες στη `DeckObj.equals(DeckObj d)`
> 1. Αν κληθεί `d1.equals(null)`, η πρόσβαση `d.deck[i]` θα ρίξει **`NullPointerException`** (σε πλήρη κώδικα ελέγχουμε πρώτα `if (d == null) return false;`).
> 2. Επειδή η παράμετρος είναι τύπου **`DeckObj`** και όχι **`Object`**, η μέθοδος αυτή κάνει **overload** (όχι override) της `Object.equals(Object)`. Για κλήση `d1.equals(d2)` (με `DeckObj d1, d2`) δουλεύει όπως αναμένεται, αλλά αν το `d2` έχει στατικό τύπο `Object`, θα κληθεί η προεπιλεγμένη `Object.equals` (που συγκρίνει διευθύνσεις με `==`).

## 2. Αντικείμενο `GLife` — Παιχνίδι της Ζωής (XII-7 … XII-10)

Υλοποίηση του *Conway's Game of Life* σε πλέγμα `size × size`. Έχει **δύο ιδιωτικά πεδία** (έναν 2D `boolean[][]` για την κατάσταση των κελιών και έναν 2D `int[][]` για το πλήθος ζωντανών γειτόνων) και **δύο `private` βοηθητικές μεθόδους**:

```java
public class GLife {
    private boolean[][] cells;
    private int[][] liveN;

    public GLife(int size, double p) {
        cells = new boolean[size][size];
        liveN = new int[size][size];
        for (int i = 0; i < size; i++)
            for (int j = 0; j < size; j++)
                if (Math.random() < p) cells[i][j] = true;
    }

    public String toString() {
        String s = "";
        for (int i = 0; i < cells.length; i++) {
            s = s + "\n";
            for (int j = 0; j < cells.length; j++)
                if (cells[i][j]) s = s + "O";
                else s = s + " ";
        }
        s = s + "\n";
        return s;
    }

    private void computeLiveNeighbors() {
        for (int i = 0; i < liveN.length; i++)
            for (int j = 0; j < liveN.length; j++)
                liveN[i][j] = live_neighbors(i, j);
    }

    private int live_neighbors(int x, int y) {
        int N = cells.length;
        int count = 0;
        if (cells[x][y]) count--;              // αφαιρεί το ίδιο το κελί (θα ξαναμετρηθεί στο 3×3)
        for (int i = x - 1; i <= x + 1; i++)
            for (int j = y - 1; j <= y + 1; j++)
                if (i >= 0 && i < N && j >= 0 && j < N && cells[i][j])
                    count++;
        return count;
    }

    public void evolve() {
        computeLiveNeighbors();
        boolean[][] ncells = new boolean[cells.length][cells.length];
        for (int i = 0; i < cells.length; i++)
            for (int j = 0; j < cells.length; j++) {
                if (cells[i][j] && (liveN[i][j] < 2 || liveN[i][j] > 3))
                    ncells[i][j] = false;
                else if (!cells[i][j] && liveN[i][j] == 3)
                    ncells[i][j] = true;
                else
                    ncells[i][j] = cells[i][j];
            }
        cells = ncells;                        // αντικατάσταση αναφοράς (παλιός πίνακας → GC)
    }
}
```

### Τι αξίζει να προσέξεις στη `GLife`

- **Ενθυλάκωση βοηθητικών μεθόδων**: Οι `computeLiveNeighbors()` και `live_neighbors(x, y)` είναι **`private`** — ο πελάτης βλέπει μόνο `GLife(size, p)`, `evolve()` και `toString()`.
- **Short-circuit στην `live_neighbors`**: Ο έλεγχος `i >= 0 && i < N && j >= 0 && j < N && cells[i][j]` πρέπει να έχει τα όρια **πριν** από το `cells[i][j]`, αλλιώς στα ακριανά κελιά πετάει `ArrayIndexOutOfBoundsException`!
- **Το κόλπο `if (cells[x][y]) count--;`**: Επειδή ο διπλός βρόχος διατρέχει και το ίδιο το `(x, y)`, αν το `(x, y)` είναι ζωντανό θα μετρηθεί `+1`· το `count--` στην αρχή το αντισταθμίζει καθαρά.
- **Γιατί `ncells` στην `evolve()` και μετά `cells = ncells;`**: Όλα τα κελιά πρέπει να εξελιχθούν **ταυτόχρονα** με βάση την ίδια γενιά. Στο τέλος `cells = ncells;` απλώς αλλάζει την αναφορά του πεδίου `cells` στον νέο πίνακα (και ο παλιός συλλέγεται από τον Garbage Collector).

> [!warning] ⚠️ Σημείωση (XII-8)
> Στο κάτω μέρος της διαφάνειας XII-8 υπάρχει ένα **επιπλέον `}`** μετά τη `toString()`, το οποίο θα έκλεινε πρόωρα την κλάση `GLife` (οι υπόλοιπες μέθοδοι της κλάσης συνεχίζονται στις XII-9 και XII-10).

## 3. Αντικείμενο `TicTacToe` — Τρίλιζα (XII-11 … XII-17)

Ένα πλήρες διαδραστικό παιχνίδι Τρίλιζας μεγέθους `size × size` (προεπιλογή `3 × 3`), όπου η `public` διεπαφή αποτελείται **μόνο** από τους 2 κατασκευαστές, τη `game()`, τη `toString()` και τη `main` — όλη η υπόλοιπη λογική είναι κρυμμένη σε 11 `private` βοηθητικές μεθόδους!

| Κατηγορία | Μέλη της `TicTacToe` |
|---|---|
| **`private` πεδία (6)** | `char[][] grid`, `char player`, `boolean hasWinner = false`, `boolean isFull = false`, `char winner`, `boolean hasStarted = false` |
| **`public` κατασκευαστές (2)** | `TicTacToe()` (καλεί **`this(3);`**) · `TicTacToe(int size)` (γεμίζει με `'E'` και διαλέγει τυχαία `'O'` ή `'X'`) |
| **`public` μέθοδοι (2)** | `game()` (κύριος βρόχος `do ... while(!hasWinner && !isFull)`) · `toString()` (σχεδιάζει το πλέγμα με `hLine`, `dLine`, `mLine`) |
| **`private` βοηθητικές (11)** | `turnPlayer()`, `play()`, `checkWin()`, `hLine()`, `dLine()`, `mLine(int)`, `same_elem(char[])`, `copy_col(char[], int)`, `copy_diag1(char[])`, `copy_diag2(char[])` |
| **`public static main`** | `TicTacToe ttt = new TicTacToe(); ttt.game();` (XII-17) |

> [!example]- Πλήρης κώδικας και κρίσιμα σημεία της `TicTacToe` (XII-12 … XII-17)
> ```java
> // XII-12: Αλυσίδωση κατασκευαστών με this(3)
> public TicTacToe() {
>     this(3);
> }
>
> // XII-13: Χρήση του this μέσα σε System.out.println (καλεί αυτόματα toString())
> public void game() {
>     do {
>         play();
>         turnPlayer();
>         checkWin();
>     } while (!hasWinner && !isFull);
>     if (hasWinner)
>         System.out.println(this + "\nWell done Player " + winner + "! You have won the game.\n\n");
>     else if (isFull)
>         System.out.println(this + "\nThis is a draw! Noone wins.\n\n");
> }
> ```
>
> Στη `checkWin()` (XII-15) ελέγχονται διαδοχικά (με `if (!hasWinner)` για αποφυγή περιττής δουλειάς):
> 1. όλες οι **γραμμές** (`for (char[] row : grid)`),
> 2. όλες οι **στήλες** (με `copy_col(col, i)`),
> 3. η **κύρια διαγώνιος** (`grid[i][i]`, με `copy_diag1`),
> 4. η **δευτερεύουσα διαγώνιος** (`grid[i][grid.length - 1 - i]`, με `copy_diag2`).
>
> Για κάθε μία ελέγχεται `same_elem(...) && ...[0] != 'E'` (ώστε να μη θεωρηθεί νίκη μια κενή γραμμή από `'E'`!).

> [!warning] ⚠️ Σημειώσεις για τη `TicTacToe` (XII-13, XII-14)
> - **XII-13**: στη `turnPlayer()` η γραμμή `if (player == 'O’)` έχει τυπογραφικό δεξί απόστροφο `’` αντί για απλό `'`.
> - **XII-14**: στη `play()` η γραμμή `else System.out.println(this + "\n\nNext to play is " + Player);` γράφει **`Player`** με κεφαλαίο `P` αντί για **`player`** → **σφάλμα μεταγλώττισης** (`cannot find symbol: variable Player`), επειδή η Java είναι case-sensitive!

## Συχνά Λάθη

> [!warning] Συχνά Λάθη
> - Στον copy constructor της `DeckObj`: `deck = d.deck;` αντί για δημιουργία νέου πίνακα → aliasing!
> - Στην `evolve()` της `GLife`: ενημέρωση του `cells[i][j]` επιτόπου χωρίς νέο πίνακα `ncells` → οι επόμενοι γείτονες θα διάβαζαν τη νέα γενιά αντί για την παλιά.
> - Στην `checkWin()` της `TicTacToe`: ξέχασμα του `row[0] != 'E'` → από τον πρώτο γύρο όποια γραμμή είναι όλη `'E'` θα φαινόταν «νικητήρια».
> - Λάθος σειρά όρων στο short-circuit: `cells[i][j] && i >= 0` πετάει `ArrayIndexOutOfBoundsException`!

## Σχετικά

- Προηγούμενο: [[03 - Αναφορές, Ψευδώνυμα και Πέρασμα δια Τιμής]]
- Επόμενο: [[05 - Αμετάβλητα Αντικείμενα - Charge και Οπτικοποίηση Δυναμικού]]
- Ευρετήριο ενότητας: [[Uni/ΕΠΛ131/12 - Δημιουργία Αντικειμένων/00 - Ευρετήριο|00 - Ευρετήριο]]
