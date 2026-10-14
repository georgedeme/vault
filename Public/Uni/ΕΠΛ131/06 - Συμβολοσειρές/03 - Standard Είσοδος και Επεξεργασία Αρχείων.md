---
publish: true
---
# 03 - Standard Είσοδος και Επεξεργασία Αρχείων

Οι βιβλιοθήκες `StdIn`/`StdOut`, η ανακατεύθυνση αρχείων, και τα πρώτα προγράμματα επεξεργασίας κειμένου: παλινδρομικά, επεκτάσεις αρχείων, μέτρηση γραμμών και λέξεων (διαφάνειες VI-16 … VI-22).

## 1. Standard Είσοδος και Έξοδος (VI-16)

> [!note] Οι δύο βιβλιοθήκες
> - **Standard είσοδος:** παρέχεται η βιβλιοθήκη **`StdIn`**.
> - **Standard έξοδος:** παρέχεται η βιβλιοθήκη **`StdOut`** (**ταυτόσημη** με τη βιβλιοθήκη `System.out`).
> - Όλες οι μέθοδοί τους είναι **στατικές μέθοδοι** (`public static`): καλούνται με το όνομα της κλάσης, `StdIn.readLine()`, **όχι** πάνω σε κάποιο αντικείμενο.

| `public class StdIn` | Τι κάνει |
|---|---|
| `boolean isEmpty()` | `true` αν δεν υπάρχουν άλλες τιμές, αλλιώς `false` |
| `int readInt()` | διαβάζει τιμή τύπου `int` |
| `double readDouble()` | διαβάζει τιμή τύπου `double` |
| `long readLong()` | διαβάζει τιμή τύπου `long` |
| `boolean readBoolean()` | διαβάζει τιμή τύπου `boolean` |
| `char readChar()` | διαβάζει τιμή τύπου `char` |
| `String readString()` | διαβάζει τιμή τύπου `String` (την επόμενη «λέξη») |
| `String readLine()` | διαβάζει **το υπόλοιπο της γραμμής** |
| `String readAll()` | διαβάζει **το υπόλοιπο του κειμένου** |

| `public class StdOut` | Τι κάνει |
|---|---|
| `void print(String s)` | τυπώνει το `s` |
| `void println(String s)` | τυπώνει το `s` και αλλάζει γραμμή |
| `void println()` | αλλάζει γραμμή |
| `void printf(String f, ...)` | μορφοποιημένη εκτύπωση |

> [!warning] ➕ Οι `StdIn`/`StdOut` δεν είναι μέρος της Java
> Είναι από το booksite του βιβλίου (Sedgewick & Wayne). Για να κάνει compile ένα πρόγραμμα που τις χρησιμοποιεί, πρέπει το `StdIn.java`/`StdOut.java` (ή το `stdlib.jar`) να βρίσκεται στον ίδιο φάκελο ή στο classpath· αλλιώς `error: cannot find symbol … StdIn`. Η εναλλακτική της «σκέτης» Java είναι ο `Scanner` ([[01 - Δομή Προγράμματος Java|II – 01]]).

> [!important] Τι ακριβώς διαβάζει κάθε μέθοδος
> - **`readString()`**: προσπερνά κενούς χαρακτήρες (κενά, tab, αλλαγές γραμμής) και επιστρέφει την επόμενη ακολουθία από **μη** κενούς χαρακτήρες. `"x,y"` είναι **μία** λέξη.
> - **`readLine()`**: επιστρέφει ό,τι απομένει **στην τρέχουσα γραμμή**, **χωρίς** το `'\n'`. Κρατά τα κενά στην αρχή (στοίχιση).
> - **`readAll()`**: όλο το υπόλοιπο κείμενο σε ένα `String`, **μαζί** με τις αλλαγές γραμμής.
> - **`isEmpty()`**: `true` όταν **δεν απομένει καμία λέξη**, δηλαδή όταν απομένουν μόνο κενοί χαρακτήρες (ή τίποτα).

> [!warning] Παγίδα: `readInt()` και μετά `readLine()`
> Με είσοδο
> ```
> 5
> hello
> ```
> ```java
> int n = StdIn.readInt();       // 5
> String s = StdIn.readLine();   // ""  (!) – το υπόλοιπο της ΙΔΙΑΣ γραμμής μετά το 5
> String t = StdIn.readLine();   // "hello"
> ```
> Η `readInt` σταματά **μετά** το `5` και αφήνει το `'\n'`. Λύση: ένα «άδειο» `StdIn.readLine();` για να τελειώσει η γραμμή, ή χρήση `readString()` αν ζητάς μία λέξη.

## 2. Ανακατεύθυνση εισόδου/εξόδου

![[Είσοδος-Έξοδος - Ανακατεύθυνση.excalidraw|800]]

| Εντολή | Είσοδος (`StdIn`) | Έξοδος (`StdOut`) |
|---|---|---|
| `java CountLines` | πληκτρολόγιο (τέλος: Ctrl+D ή Ctrl+Z, Enter) | οθόνη |
| `java CountLines < CountLines.java` | το αρχείο | οθόνη |
| `java CountLines < in.txt > out.txt` | `in.txt` | το αρχείο `out.txt` (σβήνει ό,τι είχε) |
| `java A \| java B` | `B`: η έξοδος του `A` | οθόνη |
| `java GeneFind ATG TAG < genome.txt` | το αρχείο | οθόνη · **`args`** = `{"ATG", "TAG"}` |

> [!tip] Ορίσματα γραμμής εντολής ≠ standard είσοδος
> Τα `ATG TAG` πηγαίνουν στον πίνακα `args`. Τα `< genome.txt` τα χειρίζεται το λειτουργικό σύστημα και **δεν** εμφανίζονται στο `args` (`args.length == 2`). Το πρόγραμμα δεν ξέρει αν διαβάζει από αρχείο ή από πληκτρολόγιο.

## 3. Παραδείγματα επεξεργασίας (VI-17, VI-18)

### Είναι το string παλινδρομικό;

**Ψευδοκώδικας**
```
isPalindrome(s):
    N ← μήκος του s
    για i = 0 … N/2 − 1:
        αν s[i] ≠ s[N−1−i]: επίστρεψε ψευδές
    επίστρεψε αληθές
```

```java
public static boolean isPalindrome(String s)
{
   int N = s.length();
   for (int i = 0; i < N/2; i++)
      if (s.charAt(i) != s.charAt(N-1-i))
         return false;
   return true;
}
```

Συγκρίνει το πρώτο με το τελευταίο, το δεύτερο με το προτελευταίο, … **μέχρι τη μέση** (ίδια ιδέα με την [[02 - Βασική Επεξεργασία Πινάκων|αντιστροφή πίνακα, IV – 02]]). Το `!=` εδώ είναι σωστό: συγκρίνει **`char`** (βασικός τύπος), όχι `String`.

| Είσοδος | Αποτέλεσμα | Σχόλιο |
|---|---|---|
| `""` | `true` | `N/2 = 0`: ο βρόχος δεν εκτελείται |
| `"a"` | `true` | ένα γράμμα |
| `"abba"` | `true` | |
| `"radar"` | `true` | περιττό μήκος: το μεσαίο `'d'` δεν συγκρίνεται (δεν χρειάζεται) |
| `"abca"` | `false` | |
| `"Anna"` | **`false`** | `'A' != 'a'`: διάκριση κεφαλαίων. Λύση: `isPalindrome(s.toLowerCase())` |
| `"a b a"` | `true` | τα κενά μετράνε σαν χαρακτήρες |
| `"never odd or even"` | **`false`** | λόγω κενών – θα χρειαζόταν πρώτα `s.replace(" ", "")` |

### Όνομα αρχείου και επέκταση από όρισμα γραμμής εντολής

```java
String s = args[0];
int dot = s.indexOf(".");
String base      = s.substring(0, dot);
String extension = s.substring(dot + 1, s.length());
```

| `args[0]` | `base` | `extension` |
|---|---|---|
| `"notes.txt"` | `"notes"` | `"txt"` |
| `"archive.tar.gz"` | `"archive"` | **`"tar.gz"`** – η `indexOf` βρίσκει την **πρώτη** τελεία |
| `".gitignore"` | **`""`** | `"gitignore"` |
| `"README"` | ✗ `StringIndexOutOfBoundsException` (`dot == -1` → `substring(0, -1)`) | |
| (κανένα όρισμα) | ✗ `ArrayIndexOutOfBoundsException` στο `args[0]` | |

> [!tip] Πιο ανθεκτική εκδοχή
> ```java
> int dot = s.lastIndexOf('.');            // η ΤΕΛΕΥΤΑΙΑ τελεία: "gz"
> if (dot == -1) { base = s; extension = ""; }
> ```
> Το `s.substring(dot + 1, s.length())` είναι ίδιο με το `s.substring(dot + 1)`.

### Γραμμές που περιέχουν ένα string (σαν το `grep`)

```java
String query = args[0];
while (!StdIn.isEmpty())
{
   String s = StdIn.readLine();
   if (s.contains(query)) StdOut.println(s);
}
```

Η `contains` κάνει διάκριση πεζών/κεφαλαίων και ψάχνει **υπο**συμβολοσειρά (`"null"` βρίσκεται μέσα στο `"nullLines"`). Με `query = ""` τυπώνονται **όλες** οι γραμμές.

### Υπερσύνδεσμοι προς εκπαιδευτικά ιδρύματα (VI-18)

```java
while (!StdIn.isEmpty())
{
   String s = StdIn.readString();
   if (s.startsWith("http://") && s.endsWith(".edu"))
      StdOut.println(s);
}
```

Διαβάζει **λέξεις** (`readString`), όχι γραμμές, γιατί ένας σύνδεσμος δεν έχει κενά. Χάνει όμως: `"https://mit.edu"` (`https`), `"http://mit.edu/"` (τελική `/`), `"(http://mit.edu)"` (παρένθεση), `"HTTP://MIT.EDU"` (κεφαλαία).

## 4. Πλήθος γραμμών (VI-19)

```java
public class CountLines {

 public static void main(String[] args){
   int count = 0;
   while (!StdIn.isEmpty()){
     StdIn.readLine(); count++;
   }

   System.out.println("Number of lines = " + count);
 }

}
```
```
$ java CountLines < CountLines.java
Number of lines = 12
```

Το αποτέλεσμα της `readLine()` δεν αποθηκεύεται πουθενά: μας ενδιαφέρει μόνο ότι **καταναλώθηκε** μία γραμμή.

> [!warning] Ποιες γραμμές μετράει πραγματικά (ελέγχθηκε)
> Επειδή η `isEmpty()` κοιτάζει αν απομένει **λέξη**, οι κενές γραμμές στο **τέλος** του αρχείου **δεν** μετριούνται:
>
> | Είσοδος (`\n` = αλλαγή γραμμής) | `count` |
> |---|---|
> | `a\n\nb\n` | `3` – η κενή γραμμή στη **μέση** μετράει |
> | `a\nb\n\n\n` | `2` – οι κενές στο **τέλος** όχι |
> | `a\n   \n` | `1` – ούτε γραμμή με μόνο κενά στο τέλος |
> | `a\nb` (χωρίς τελικό `\n`) | `2` |
> | (κενό αρχείο) | `0` |

## 5. Πλήθος «λέξεων» (VI-20)

```java
public class CountWords {

 public static void main(String[] args){
   int count = 0;
   while (!StdIn.isEmpty()){
     StdIn.readString(); count++;
   }

   System.out.println("Number of words = " + count);
 }

}
```
```
$ java CountWords < CountLines.java
Number of words = 27
```

«Λέξη» (σε εισαγωγικά στη διαφάνεια) = ό,τι επιστρέφει η `readString()`: ακολουθία μη κενών χαρακτήρων. Το `System.out.println("Number` είναι **μία** λέξη, το `{` επίσης.

## 6. Γραμμές και λέξεις μαζί (VI-21, VI-22)

```
$java CountWordsLines < CountLines.java
Number of lines = 12
Number of words = 27
```

Δεν γίνεται να τρέξουμε πρώτα το ένα και μετά το άλλο στην ίδια είσοδο: η είσοδος **καταναλώνεται** καθώς διαβάζεται. Άρα διαβάζουμε **γραμμές** και μετράμε τις λέξεις κάθε γραμμής **χαρακτήρα προς χαρακτήρα**.

**Ψευδοκώδικας**
```
lineCount ← 0, wordCount ← 0
όσο υπάρχει είσοδος:
    s ← επόμενη γραμμή; lineCount++
    beg ← ψευδές                       // «είμαι μέσα σε λέξη;»
    για κάθε χαρακτήρα c του s:
        αν beg και c κενός:            // μόλις τελείωσε μια λέξη
            beg ← ψευδές; wordCount++
        αν όχι beg και c όχι κενός:    // μόλις άρχισε μια λέξη
            beg ← αληθές
    αν beg: wordCount++                // λέξη που τελειώνει στο τέλος της γραμμής
```

```java
public class CountWordsLines {

 public static boolean white_space(char c){
   return c == ' ' || c == '\n' || c == '\t';
 }

 public static void main(String[] args){
   int lineCount = 0, wordCount = 0;
   while (!StdIn.isEmpty()){
     String s = StdIn.readLine(); lineCount++;
     boolean beg = false;
     for (int i = 0; i < s.length(); i++){
       if (beg && white_space(s.charAt(i)))
           { beg = false; wordCount++; }
       if (!beg && !white_space(s.charAt(i)))
           { beg = true; }
     }
     if (beg) wordCount++;
   }

   System.out.println("Number of lines = " + lineCount);
   System.out.println("Number of words = " + wordCount);
 }
}
```

![[Είσοδος-Έξοδος - Μέτρηση Λέξεων.excalidraw|800]]

> [!important] Η ιδέα: μετράμε **τέλη** λέξεων
> Κάθε λέξη έχει ακριβώς ένα τέλος: είτε έναν κενό χαρακτήρα αμέσως μετά, είτε το τέλος της γραμμής. Το `beg` είναι μια **σημαία κατάστασης** (μέσα/έξω από λέξη) και ο αριθμός λέξεων αυξάνεται μόνο στη μετάβαση «μέσα → έξω».

> [!warning] Παγίδες του κώδικα
> - Χωρίς το τελικό `if (beg) wordCount++;` χάνεται η **τελευταία** λέξη κάθε γραμμής που δεν τελειώνει με κενό (δηλαδή σχεδόν όλων).
> - Το `boolean beg = false;` πρέπει να είναι **μέσα** στον `while`: κάθε γραμμή ξεκινά «έξω από λέξη».
> - Ο έλεγχος `c == '\n'` στη `white_space` δεν χρειάζεται ποτέ: η `readLine()` αφαιρεί το `'\n'`. Δεν βλάπτει όμως.
> - Η `white_space` δεν περιλαμβάνει άλλους κενούς χαρακτήρες (π.χ. `'\f'`), ενώ η `readString()` τους περιλαμβάνει, οπότε σε τέτοια αρχεία `CountWords` και `CountWordsLines` μπορεί να διαφωνούν. Στα κανονικά αρχεία δίνουν το ίδιο.

> [!example]- Ίχνος σε ολόκληρη είσοδο
> Είσοδος: `"  Hello,world  "`, `""`, `" a b\tc "` (3 γραμμές).
>
> | Γραμμή | Λέξεις της γραμμής | `lineCount` | `wordCount` |
> |---|---|---|---|
> | `"  Hello,world  "` | `Hello,world` (το κόμμα δεν είναι κενό) | 1 | 1 |
> | `""` | – (ο `for` δεν εκτελείται, `beg` μένει `false`) | 2 | 1 |
> | `" a b\tc "` | `a`, `b`, `c` (το `\t` είναι κενός) | 3 | 4 |
>
> Έξοδος: `Number of lines = 3`, `Number of words = 4` (ελέγχθηκε).

## Συχνά Λάθη

> [!warning] Συχνά Λάθη
> - `StdIn` χωρίς το `StdIn.java` στον φάκελο → `cannot find symbol`.
> - `readInt()` και μετά `readLine()` → κενό string.
> - Σύγχυση `readString()` (λέξη) με `readLine()` (γραμμή).
> - Χρήση της `indexOf` χωρίς έλεγχο για `-1`.
> - Ξεχνάς τη λέξη στο τέλος της γραμμής στη μέτρηση λέξεων.
> - Νομίζεις ότι τα `< file` εμφανίζονται στο `args`.

## Σχετικά

- Προηγούμενο: [[02 - Συμβολοσειρές ως Δείκτες και Σύγκριση]]
- Επόμενο: [[04 - Εύρεση Γονιδίου]]
- `args`, `Scanner`, `printf`: [[01 - Δομή Προγράμματος Java|II – 01 Δομή Προγράμματος]]
- `boolean` σημαίες σε βρόχους: [[06 - Αναζήτηση και break|IV – 06 Αναζήτηση]]
- Γρήγορη επανάληψη: [[Uni/ΕΠΛ131/06 - Συμβολοσειρές/07 - Τυπολόγιο|07 - Τυπολόγιο]] · Εξάσκηση: [[Uni/ΕΠΛ131/06 - Συμβολοσειρές/08 - Ασκήσεις|08 - Ασκήσεις]]
