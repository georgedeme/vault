---
publish: true
---
# 03 - Tic-Tac-Toe, Διάσπαση και Σύνθεση

Το ταμπλό της τρίλιζας (tic-tac-toe) ως `char[3][3]`: είναι γεμάτο; είναι άδειο; **υπάρχει νικητής;** Το τελευταίο λύνεται με τη στρατηγική της **διάσπασης και σύνθεσης**: σχεδιασμός από πάνω προς τα κάτω, υλοποίηση από κάτω προς τα πάνω (διαφάνειες IX-12 … IX-14, IX-21 … IX-28).

Σύμβαση: `'X'` και `'O'` οι δύο παίκτες, **`'E'`** (Empty) για κενό τετράγωνο.

## 1. Είναι το ταμπλό τελείως γεμάτο; (IX-12, IX-13)

| Όχι | | | | Ναι | | |
|---|---|---|---|---|---|---|
| X | O | E | | X | O | O |
| E | O | E | | O | O | X |
| X | E | E | | X | X | O |

```java
public class Tables{

  public static boolean filled (char[][] ttt){
    for (char[] cs : ttt){   // for each row
      for (char c : cs){     // for each element of the row
        if (c == 'E') return false;
      }
    }
    return true;
  }

  public static void main(String[] args){
    char[][] ttt1 = {{'X', 'O', 'E'}, {'E','O','E'},
                     {'X','E','E'}};
    char[][] ttt2 = {{'X', 'O', 'O'}, {'O','O','X'},
                     {'X','X','O'}};
    System.out.println(filled(ttt1));
    System.out.println(filled(ttt2));
  }
}
```

```
$ java Tables
false
true
```

## 2. Είναι τελείως κενό; (IX-14)

```java
public static boolean empty (char[][] ttt){
  for (char[] cs : ttt){   // for each row of ttt
    for (char c : cs){     // for each element of the row
      if (c != 'E') return false;
    }
  }
  return true;
}
```

> [!important] Το μοτίβο «για όλα» (∀)
> Και οι δύο είναι **καθολικοί** έλεγχοι: «όλα τα στοιχεία είναι ≠ `'E'`» / «όλα είναι `'E'`». Μόλις βρεθεί **ένα αντιπαράδειγμα** → `return false` αμέσως (η `return` βγαίνει και από τους δύο βρόχους). `return true` μόνο **μετά** τους βρόχους, όταν έχουν ελεγχθεί όλα. Οι δύο μέθοδοι διαφέρουν μόνο στον τελεστή (`==` / `!=`).

> [!warning] ➕ Παγίδες (ελέγχθηκαν)
> - `return true` **μέσα** στον βρόχο (π.χ. `else return true;`) θα αποφάσιζε από το **πρώτο** στοιχείο μόνο.
> - `filled` και `empty` **δεν** είναι αντίθετα: ένα ταμπλό στη μέση του παιχνιδιού δεν είναι ούτε γεμάτο ούτε κενό. `!filled(t)` σημαίνει «υπάρχει τουλάχιστον ένα `'E'`».
> - `empty(new char[3][3])` → **`false`**: η προεπιλεγμένη τιμή του `char` είναι `'\u0000'`, όχι `'E'`. Ένα νέο ταμπλό πρέπει να γεμίσει ρητά με `'E'`.

## 3. Πρόβλημα: υπάρχει νικητής; (IX-21)

> [!note] Πρόβλημα
> Να οριστεί η συνάρτηση **`win`** η οποία λαμβάνει ως παράμετρο δεδομένο πίνακα που αντιπροσωπεύει τη διάταξη των επιλογών των δύο παικτών στο παιγνίδι tic-tac-toe, και επιστρέφει `true` εάν η διάταξη αποτελεί νίκη για κάποιον από τους παίκτες. Διαφορετικά επιστρέφει `false`. Σε περίπτωση νίκης, εκτυπώνει ποιος νίκησε και πώς.

**Να εφαρμόσουμε τη στρατηγική της «διάσπασης και σύνθεσης».** Διάσπαση του προβλήματος σε υπο-προβλήματα:
- Είναι τα περιεχόμενα δεδομένης **σειράς** τα ίδια;
- Είναι τα περιεχόμενα δεδομένης **στήλης** τα ίδια;
- Είναι όλα τα στοιχεία της μίας ή της άλλης **διαγωνίου** τα ίδια;

(και φυσικά να μην είναι `'E'`).

## 4. Σχεδιασμός από πάνω προς τα κάτω (IX-22 … IX-24)

```java
public static boolean win (char [][] ttt_b){
  return rWin(ttt_b) || cWin(ttt_b) || dWin(ttt_b);
}
```

**Προσδιορισμός πιο βασικών υπο-προβλημάτων (IX-23):**
- Είναι όλα τα στοιχεία δεδομένου **μονοδιάστατου** πίνακα τα ίδια; → `same_elem`
- Αντιγραφή δεδομένης **στήλης** δισδιάστατου πίνακα σε μονοδιάστατο πίνακα → `copy_col`
- Αντιγραφή δεδομένης **διαγωνίου** δισδιάστατου πίνακα σε μονοδιάστατο πίνακα → `copy_diag1`, `copy_diag2`

> [!important] Γιατί χρειάζονται οι αντιγραφές (IX-23)
> **Σημείωση:** Μόνο τα στοιχεία της **εξωτερικής** διάστασης μπορεί να αναφερθούν ως ολότητες, σε σχέση με πολυδιάστατους πίνακες. Επομένως σχετικά με δισδιάστατους πίνακες, μπορεί να γίνει άμεση αναφορά στις **σειρές** του πίνακα, ως ολότητες (δηλαδή ως μονοδιάστατους πίνακες), αλλά **όχι στις στήλες ή τις διαγώνιους** του.
>
> Άρα: η σειρά `ttt[i]` δίνεται **κατευθείαν** στη `same_elem`· μια στήλη ή διαγώνιος πρέπει πρώτα να **αντιγραφεί** σε βοηθητικό πίνακα `char[3]`.

![[Tic-Tac-Toe - Διάσπαση.png|800]]

| Επίπεδο | Συναρτήσεις | Ορατότητα |
|---|---|---|
| κορυφή | `win` | **`public`** – η μόνη |
| μεσαίο | `rWin`, `cWin`, `dWin` | `private` |
| βάση | `same_elem`, `copy_col`, `copy_diag1`, `copy_diag2` | `private` |

«Μόνο η `win` είναι `public`. Οι υπόλοιπες, που αποτελούν τις βοηθητικές από τις οποίες συντίθεται, είναι `private`.» **Σχεδιασμός/διάσπαση από τα πάνω προς τα κάτω** (IX-22) · **υλοποίηση/σύνθεση από κάτω προς τα πάνω** (IX-24).

## 5. Υλοποίηση (IX-25 … IX-28)

**Βασικές συναρτήσεις (IX-25):**
```java
public class TicTacToe {

  // Are all elements of table the same?
  private static boolean same_elem (char[] table) {
    for (int i = 1; i < table.length; i++)
       if (table[i] != table[0]) return false;
    return true; }

  // Copy column col of table into array col_table
  private static void copy_col(char[][] table, char[] col_table,
                               int col){
    for (int i = 0; i < table[0].length; i++)
       col_table[i] = table[i][col];
  }

  // Copy diagonal of table
  private static void copy_diag1(char[][] table, char[] diag){
     for (int i =0; i < diag.length; i++)
        diag[i] = table[i][i];
  }

  // Copy anti-diagonal of table
  private static void copy_diag2(char[][] table, char[] diag){
     for (int i =0; i < diag.length; i++)
        diag[i] = table[i][2-i];
  }
  // class definition continues …
```

**Σειρά και στήλη (IX-26):**
```java
  // Is there a row win?
  private static boolean rWin (char[][] ttt){
    for (int i = 0; i < ttt.length; i++)
       if (ttt[i][0] != 'E' && same_elem(ttt[i])){
          System.out.println("Player " + ttt[i][0] + " wins on row " + (i+1));
          return true;
       }
    return false;
  }

  // Is there a colum win?
  private static boolean cWin (char[][] ttt){
    for (int i = 0; i < ttt.length; i++){
       char[] aux = new char[3];
       copy_col(ttt, aux, i);
       if (aux[0] != 'E' && same_elem(aux)){
          System.out.println("Player " + aux[0] + " wins on colum " + (i+1));
          return true;
       }
    }
    return false;
  }
  // class definition continues . . .
```

**Διαγώνιοι και η κύρια συνάρτηση (IX-27):**
```java
  // Is there a diagonal win?
  private static boolean dWin(char[][] ttt){
     char[]aux = new char[3];
     copy_diag1(ttt, aux);
     if (aux[0] != 'E' && same_elem(aux)){
        System.out.println("Player " + aux[0] + " wins on diagonal");
        return true;
     }
     copy_diag2(ttt, aux);
     if (aux[0] != 'E' && same_elem(aux)){
        System.out.println("Player " + aux[0] + " wins on antidiagonal");
        return true;
     }
     return false;
  }

  // The principal function win
  public static boolean win (char [][] ttt_b){
     return rWin(ttt_b) || cWin(ttt_b) || dWin(ttt_b);
  }
  // class definition continues . . .
```

**`main` για δοκιμή (IX-28):**
```java
  // completion of class definition by including main for
  // testing purposes

  public static void main(String[] args){
     char[][] board = new char[3][3];
     for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++){
           board[i][j]=args[0].charAt(i*3+j);}

     if (win(board)) System.out.println("Thus there is a winner!!");
     else System.out.println("Nobody wins!");
  }
}
```

Το όρισμα είναι 9 χαρακτήρες, **σειρά-σειρά**: ο χαρακτήρας `i*3+j` πάει στη θέση `[i][j]`.

| Εντολή | Ταμπλό | Έξοδος (ελέγχθηκε) |
|---|---|---|
| `java TicTacToe EEXEEOEEE` | `EEX / EEO / EEE` | `Nobody wins!` |
| `java TicTacToe XEEXEEXEE` | `XEE / XEE / XEE` | `Player X wins on colum 1` · `Thus there is a winner!!` |
| `java TicTacToe EEOEOEOEE` | `EEO / EOE / OEE` | `Player O wins on antidiagonal` · `Thus there is a winner!!` |

![[Tic-Tac-Toe - Γραμμές Νίκης.png|800]]

> [!warning] ⚠️ Σημείωση για τη IX-28
> Η έξοδος της διαφάνειας δεν είναι αυτή που τυπώνει ο κώδικας:
> - γράφει `wins on col 1` – ο κώδικας τυπώνει **`wins on colum 1`** (έτσι είναι γραμμένο το string στη IX-26)·
> - γράφει `wins on antiDiagonal` – ο κώδικας τυπώνει **`antidiagonal`**·
> - γράφει `Thus there is a winner!` – ο κώδικας τυπώνει **`winner!!`** (δύο θαυμαστικά).
>
> Επίσης η IX-27 έχει υπόλειμμα από άλλη διαφάνεια (`ΕΠΛ131 – Ενότητα X`, `X-27`) στο κάτω μέρος.

> [!example]- ➕ Περισσότερες περιπτώσεις και οριακές συμπεριφορές (ελέγχθηκαν)
> - `XXXOOOEEE` → `Player X wins on row 1` – το `O` έχει επίσης γραμμή (σειρά 2), αλλά το `||` κάνει **short-circuit**: η `rWin` βρίσκει πρώτα τη σειρά 1 και επιστρέφει. Δεν ελέγχεται ποτέ αν η διάταξη είναι «νόμιμη».
> - `XOXOXOXOX` → `Player X wins on diagonal` – υπάρχει **και** αντιδιαγώνιος του X, αλλά η `dWin` επιστρέφει με την πρώτη.
> - `EXEEXEEXE` → `Player X wins on colum 2` – το `(i+1)` μετατρέπει δείκτη 1 σε «στήλη 2».
> - Όρισμα με λιγότερους από 9 χαρακτήρες (`XXX`) → `StringIndexOutOfBoundsException` στην `charAt`. Χωρίς όρισμα → `ArrayIndexOutOfBoundsException` στο `args[0]`.
> - Πεζά (`xxxeeeeee`) → `Player x wins on row 1`: η σύγκριση με `'E'` είναι case-sensitive, το `'e'` θεωρείται παίκτης!

> [!tip] ➕ Γενίκευση σε N × N
> - Η `copy_diag2` έχει **σκληροκωδικοποιημένο** `2-i`· για N × N γίνεται `table[i][table.length-1-i]`.
> - Οι `cWin`, `dWin` φτιάχνουν `new char[3]`· γενικά `new char[ttt.length]`.
> - Η `copy_col` χρησιμοποιεί `table[0].length` ως πλήθος **σειρών** – σωστό μόνο επειδή ο πίνακας είναι τετραγωνικός. Σωστά: `table.length` (μία τιμή για κάθε σειρά).
> - Η `same_elem` και η `rWin` είναι ήδη γενικές.

## Συχνά Λάθη

> [!warning] Συχνά Λάθη
> - Ξεχασμένος έλεγχος `!= 'E'`: μια σειρά `EEE` είναι «όλα ίδια» αλλά δεν είναι νίκη.
> - Προσπάθεια να δοθεί στήλη στη `same_elem` χωρίς αντιγραφή (δεν υπάρχει έκφραση για στήλη).
> - `return true` μέσα στον βρόχο στις `filled`/`empty`.
> - Πίστη ότι η `win` τυπώνει όλες τις γραμμές νίκης: σταματά στην πρώτη (short-circuit).
> - Σύγχυση `charAt(i*3+j)` με `charAt(j*3+i)` (το δεύτερο γεμίζει στήλη-στήλη, δηλαδή τον ανάστροφο).
> - Αντιγραφή της εξόδου της διαφάνειας (`col`, `antiDiagonal`, `!`) σε ερώτηση «τι τυπώνει».

## Σχετικά

- Προηγούμενο: [[02 - Πράξεις Πινάκων και Διάσπαση ανά Διάσταση]] · Επόμενο: [[04 - Αυτο-αποφεύγων Περίπατος]]
- Διάσπαση και σύνθεση, `private` βοηθητικές: [[05 - Υπερφόρτωση Συναρτήσεων|VIII – 05]] · [[06 - Βιβλιοθήκες DrawGraph και SortLib|VIII – 06]]
- Αρθρωτότητα (πυραμίδες): [[05 - Διακριτά Σχήματα και Αρθρωτότητα|VI – 05]] · Short-circuit: [[01 - Συνθήκες και Λογικές Εκφράσεις|III – 01]]
- Γρήγορη επανάληψη: [[Uni/ΕΠΛ131/09 - Πίνακες Πολλών Διαστάσεων/06 - Τυπολόγιο|06 - Τυπολόγιο]] · Εξάσκηση: [[Uni/ΕΠΛ131/09 - Πίνακες Πολλών Διαστάσεων/07 - Ασκήσεις|07 - Ασκήσεις]]
