---
publish: true
---
# 06 - Βιβλιοθήκες DrawGraph και SortLib

Δύο δικές μας **βιβλιοθήκες** επαναχρησιμοποιήσιμων συναρτήσεων: η `DrawGraph` σχεδιάζει γραφικές παραστάσεις (με **overloading** της `plot`), η `SortLib` ταξινομεί πίνακες (insertion sort, bubble sort) και μετρά τον χρόνο τους (διαφάνειες VIII-37 … VIII-62).

## 1. Η βιβλιοθήκη DrawGraph (VIII-37 … VIII-39)

**Πρόβλημα:** σχεδίαση συνεχών γραφικών παραστάσεων (plotting continuous graphs). Ο πίνακας `ys` κρατά τις τιμές `y` στα σημεία `x = 0, 1, …, ys.length-1`· ενώνοντας διαδοχικά σημεία με ευθύγραμμα τμήματα παίρνουμε την καμπύλη.

- Θα αξιοποιηθεί η βιβλιοθήκη **`StdDraw`** (κλάση του βιβλίου, [[05 - Γραφικά με StdDraw|VII – 05]]).
- Θα γίνει χρήση της έννοιας του **function overloading** – υπερφόρτωση συναρτήσεων ([[05 - Υπερφόρτωση Συναρτήσεων|05]]).

| `public class DrawGraph` | |
|---|---|
| `void plot(double[] ys)` | plots one graph |
| `void plot(double[] ys1, double[] ys2)` | plots two graphs – `ys1` and `ys2` are parallel arrays |

## 2. Βοηθητικές `private` συναρτήσεις (VIII-38)

```java
import java.awt.Color; // Uses colors - Color is an object

public class DrawGraph {

  // returns the maximum element of table ys
  private static double max (double[] ys){
   double M = Double.NEGATIVE_INFINITY;
   for (int i = 0; i < ys.length; i++) {
     if (M < ys[i]) M = ys[i];
   }
   return M;
  }

  // returns the minimum element of table ys
  private static double min (double[] ys){
   double M = Double.POSITIVE_INFINITY;
   for (int i = 0; i < ys.length; i++) {
     if (M > ys[i]) M = ys[i];
   }
   return M;
  }
  // Class definition continues . . .
```

> [!important] Γιατί `private`
> Οι `max` και `min` είναι **βοηθητικές**: τις χρειάζεται η `plot` για να βρει την κλίμακα του άξονα `y`. Δεν ανήκουν στη διεπαφή της βιβλιοθήκης (δεν εμφανίζονται στο API), άρα κρύβονται. Ο χρήστης βλέπει μόνο τις δύο `plot` – [[03 - Σχεδιασμός Μονάδων|απόκρυψη υλοποίησης]]. Αν αύριο αλλάξουν, κανένας client δεν επηρεάζεται.

## 3. Οι δύο εκδοχές της `plot` (VIII-40 … VIII-43)

```java
  public static void plot (double[] ys){
     double MIN = min(ys);
     double MAX = max(ys);
     StdDraw.setXscale(0,ys.length-1);
     StdDraw.setYscale(MIN,MAX);
     StdDraw.setPenRadius(0.004);
     StdDraw.setPenColor(StdDraw.BLACK);
     StdDraw.clear(StdDraw.WHITE);

     for (int i = 0; i < ys.length-1; i++){
        StdDraw.line(i, ys[i], i+1, ys[i+1]);
     }
  }
```

```java
  public static void plot (double[] ys1, double[] ys2){
     double MIN = min(ys1);
     if (MIN > min(ys2)) MIN = min(ys2);
     double MAX = max(ys1);
     if (MAX < max(ys2)) MAX = max(ys2);

     StdDraw.setXscale(0,ys1.length-1);
     StdDraw.setYscale(MIN,MAX);
     StdDraw.clear(StdDraw.WHITE);
     StdDraw.setPenRadius(0.004);

     for (int i = 0; i < ys1.length-1; i++){
        StdDraw.setPenColor(StdDraw.RED);
        StdDraw.line(i, ys1[i], i+1, ys1[i+1]);
        StdDraw.setPenColor(StdDraw.GREEN);
        StdDraw.line(i, ys2[i], i+1, ys2[i+1]);
     }
  }
```

> [!note] Πώς διαβάζεται
> - Η κλίμακα `y` καλύπτει **και τους δύο** πίνακες: `MIN` = το μικρότερο από τα δύο ελάχιστα, `MAX` = το μεγαλύτερο από τα δύο μέγιστα.
> - Το βρόχο έχει `ys1.length-1` επαναλήψεις: `n` σημεία → `n-1` τμήματα. Το `i+1` φτάνει έως `ys1.length-1`, άρα μένει μέσα στα όρια.
> - Σε κάθε επανάληψη σχεδιάζεται ένα κόκκινο τμήμα του `ys1` και ένα πράσινο του `ys2` – οι δύο καμπύλες «μεγαλώνουν» **ταυτόχρονα**.

**Ερώτηση (VIII-42):** πώς διαφέρει ο παρακάτω κώδικας από την προηγούμενη εκδοχή;

```java
  public static void plot (double[] ys1, double[] ys2){
     . . . . . . . . . . . . . . . .
     for (int i = 0; i < ys1.length-1; i++){
        StdDraw.setPenColor(StdDraw.RED);
        StdDraw.line(i, ys1[i], i+1, ys1[i+1]);
     }
     for (int i = 0; i < ys2.length-1; i++){
        StdDraw.setPenColor(StdDraw.GREEN);
        StdDraw.line(i, ys2[i], i+1, ys2[i+1]);
     }
  }
```

> [!success]- Απάντηση (VIII-43)
> - Πρώτα σχεδιάζεται **εξ ολοκλήρου** η κόκκινη γραφική παράσταση και **μετά** η πράσινη – στον προηγούμενο κώδικα οι δύο παραστάσεις σχεδιάζονται ταυτόχρονα.
> - Επιπρόσθετα, τώρα οι πίνακες `ys1` και `ys2` **δεν χρειάζεται να έχουν το ίδιο πλήθος** στοιχείων. Σε περίπτωση διαφορετικού πλήθους, ο μικρότερος πίνακας θεωρείται παράλληλος του αρχικού τμήματος του μεγαλύτερου.

> [!warning] ➕ Τι θα γινόταν με διαφορετικά μήκη
> - **Πρώτη** εκδοχή, `ys2` **μικρότερος** από `ys1`: ο κοινός βρόχος φτάνει σε `ys2[i+1]` πέρα από τα όρια → `ArrayIndexOutOfBoundsException`. Γι' αυτό απαιτεί παράλληλους πίνακες.
> - **Δεύτερη** εκδοχή, `ys2` **μεγαλύτερος** από `ys1`: δεν σκάει, αλλά ο άξονας `x` έχει οριστεί με `setXscale(0, ys1.length-1)`, άρα το επιπλέον κομμάτι του `ys2` σχεδιάζεται **έξω** από το παράθυρο (δεν φαίνεται). Η «παράλληλη» ερμηνεία της απάντησης ισχύει πλήρως μόνο όταν ο `ys1` είναι ο μεγαλύτερος.
> - Αν όλες οι τιμές είναι **ίσες** (`MIN == MAX`) ή ο πίνακας έχει **ένα** στοιχείο (`setXscale(0, 0)`), η κλίμακα είναι μηδενικού πλάτους· η σημερινή έκδοση της `StdDraw` πετά `IllegalArgumentException` («the min and max are the same»).

## 4. Η `main` για δοκιμή (VIII-44 … VIII-47)

```java
  // The class definition is completed with function main
  // for purely testing purposes

  public static void main (String[] args){
     int N = Integer.parseInt(args[0]);
     double[] ys = new double[N+1];
     double[] zs = new double[N+1];
     for (int x = 0; x < N; x++){
        ys[x] = Math.sin(4*Math.PI*x/N) +
                Math.sin(20*Math.PI*x/N);
        zs[x] = Math.sin(2*Math.PI*x/N) +
                Math.sin(10*Math.PI*x/N);
     }
     plot(zs); StdDraw.show(500);
     plot(ys); StdDraw.show(500);
     plot(ys, zs); StdDraw.show(500);
  }
}
```

```
$ java DrawGraph 200
```

Τρεις εικόνες: η `zs` (VIII-45: 1 + 5 περίοδοι), η `ys` (VIII-46: 2 + 10 περίοδοι), και οι δύο μαζί σε κόκκινο/πράσινο (VIII-47).

> [!tip] ➕ Λεπτομέρειες της `main`
> - Οι πίνακες έχουν `N+1` θέσεις αλλά ο βρόχος γεμίζει μόνο `0 … N-1`· η θέση `N` μένει `0.0` (προεπιλογή). Εδώ είναι **σωστό κατά τύχη**: στο `x = N` και οι δύο συναρτήσεις ισούνται με `sin(k·π) = 0`. Με `x <= N` ο κώδικας θα ήταν σωστός για οποιαδήποτε συνάρτηση.
> - `4*Math.PI*x/N`: ο πολλαπλασιασμός με `Math.PI` γίνεται **πρώτα**, άρα η διαίρεση `/N` είναι πραγματική. Με `4*x/N*Math.PI` θα γινόταν ακέραια διαίρεση ([[07 - Αποτίμηση Εκφράσεων|II – 07]]).
> - `StdDraw.show(500)` είναι η παλιά έκδοση της `StdDraw` (σήμερα `show()` + `pause(500)`, όπως σημειώθηκε στη [[05 - Γραφικά με StdDraw|VII – 05]]).
> - Η `plot` καλείται χωρίς πρόθεμα κλάσης επειδή η `main` είναι στην ίδια κλάση. Από άλλο πρόγραμμα: `DrawGraph.plot(ys);`.

## 5. Η βιβλιοθήκη SortLib (VIII-48 … VIII-51)

Αρχικά θα περιλαμβάνει συναρτήσεις για την ταξινόμηση πινάκων με ακεραίους, βάσει γνωστών μεθόδων:
- **Bubble sort** – ταξινόμηση φυσαλίδας
- **Insertion sort** – ταξινόμηση εισαγωγής

Για σκοπούς δοκιμής θα αξιοποιηθούν βοηθητικές συναρτήσεις καθώς και η βιβλιοθήκη `DrawGraph`: παρουσίαση χρόνου εκτέλεσης για διάφορα μεγέθη πινάκων – **complexity estimates**.

| `public class SortLib` | |
|---|---|
| `void insertionSort(int[] table)` | applies insertion sort |
| `void bubbleSort(int[] table)` | applies bubble sort |

### Βοηθητική: είναι ταξινομημένος;

```java
public class SortLib {

 // Ancillary function for testing purposes - Is table sorted?
 private static boolean sorted (int[] table){
   for (int i = 0; i < table.length-1; i++)
     if (table[i] > table[i+1]) return false;
   return true;
 }
```

Πρώτο «χαλασμένο» ζεύγος γειτόνων → `false`. Αν δεν βρεθεί κανένα → `true`. Κενός πίνακας ή πίνακας ενός στοιχείου → `true` (ο βρόχος δεν εκτελείται).

### Insertion sort

**Ψευδοκώδικας**
```
insertionSort(table):
    για i = 1 … n-1:                     // table[0..i-1] είναι ήδη ταξινομημένο
        j = i
        όσο j > 0 και table[j] < table[j-1]:
            αντιμετάθεσε table[j], table[j-1]   // «βύθισε» το νέο στοιχείο προς τα αριστερά
            j = j - 1
```

```java
 // INSERTION SORT - Complexity: O(n2)
 public static void insertionSort (int[] table){
   for (int i = 1; i < table.length; i++){
     boolean stop = false;
     for (int j = i; !stop && j > 0; j--){
       if (table[j] < table[j-1]){
          int temp = table[j-1];
          table[j-1] = table[j];
          table[j] = temp;
       }
       else stop = true;
     }
   }
 }
```

Η σημαία `stop` υλοποιεί το «όσο … και `table[j] < table[j-1]`»: μόλις το νέο στοιχείο βρει θέση (δεν είναι μικρότερο από τον αριστερό γείτονα), σταματά – τα αριστερά του είναι ήδη ταξινομημένα.

### Bubble sort

**Ψευδοκώδικας**
```
bubbleSort(table):
    index = n
    επανάλαβε:
        sorted = true; index = index - 1
        για i = 0 … index-1:
            αν table[i] > table[i+1]: αντιμετάθεσε, sorted = false
    μέχρι index == 0 ή sorted              // το μεγαλύτερο «ανέβηκε» στη θέση index
```

```java
 // BUBBLE SORT - Complexity: O(n2)
 public static void bubbleSort(int[] table){
   boolean sorted = true;
   int index = table.length;
   do {
      sorted = true; index--;
      for (int i = 0; i < index; i++){
         if (table[i] > table[i+1]){
            sorted = false;
            int temp = table[i];
            table[i] = table[i+1];
            table[i+1] = temp;
         }
      }
   } while(index > 0 && !sorted);
 }

 public static void main(String[] args){. . . . .}
}
```

> [!example]- Ίχνος και των δύο με `{5, 2, 4, 6, 1, 3}` (ελέγχθηκε)
>
> **Insertion sort** – μετά από κάθε τιμή του `i`:
>
> | `i` | Πίνακας | Τι έγινε |
> |---|---|---|
> | 1 | `2 5 4 6 1 3` | το `2` πέρασε αριστερά του `5` |
> | 2 | `2 4 5 6 1 3` | το `4` σταμάτησε μετά το `2` |
> | 3 | `2 4 5 6 1 3` | το `6` ήταν ήδη στη θέση του (`stop` αμέσως) |
> | 4 | `1 2 4 5 6 3` | το `1` πήγε μέχρι την αρχή |
> | 5 | `1 2 3 4 5 6` | το `3` σταμάτησε μετά το `2` |
>
> **Bubble sort** – μετά από κάθε πέρασμα του `do`:
>
> | Πέρασμα | `index` | Πίνακας | `sorted` |
> |---|---|---|---|
> | 1 | 5 | `2 4 5 1 3 6` | `false` – το `6` στην τελική θέση |
> | 2 | 4 | `2 4 1 3 5 6` | `false` |
> | 3 | 3 | `2 1 3 4 5 6` | `false` |
> | 4 | 2 | `1 2 3 4 5 6` | `false` (έγινε αντιμετάθεση) |
> | 5 | 1 | `1 2 3 4 5 6` | `true` → τέλος |
>
> Ο bubble sort χρειάζεται ένα **επιπλέον** πέρασμα χωρίς αλλαγές για να «μάθει» ότι τελείωσε.

![[Συναρτήσεις - Insertion και Bubble Sort.png|800]]

> [!tip] ➕ Ακραίες περιπτώσεις (ελέγχθηκαν)
> - Κενός πίνακας: η `bubbleSort` κάνει `index = -1`, ο `for` δεν εκτελείται, η συνθήκη `index > 0` είναι ψευδής → τέλος. Η `insertionSort` δεν μπαίνει στον βρόχο. Κανένα σφάλμα.
> - Ήδη ταξινομημένος πίνακας: insertion sort κάνει μόνο `n-1` συγκρίσεις (κάθε νέο στοιχείο σταματά αμέσως)· bubble sort ένα πέρασμα `n-1` συγκρίσεων. Αυτή είναι η **καλύτερη** περίπτωση – γραμμική.
> - Αντίστροφα ταξινομημένος: η **χειρότερη** – περίπου `n²/2` συγκρίσεις και αντιμεταθέσεις και στους δύο.
> - Και οι δύο είναι `void`: ταξινομούν **επί τόπου** τον πίνακα του καλούντα ([[04 - Πίνακες ως Παράμετροι Συναρτήσεων|04]]).
> - Με 2000 τυχαίους πίνακες (μήκη 0 … 29, με διπλότυπα και αρνητικούς) η `sorted` επιβεβαίωσε και τις δύο.

## 6. Μέτρηση χρόνου και πολυπλοκότητα (VIII-52 … VIII-59)

**Συμπληρώστε τη `main` για τη δοκιμή της `SortLib` (VIII-52):**
- Κάνετε χρήση της ιδιωτικής, βοηθητικής συνάρτησης `sorted` για να βεβαιωθείτε ότι οι `insertionSort` και `bubbleSort` είναι ορθές. (Σε μεταγενέστερο στάδιο θα ζητηθεί να προσθέσετε και άλλες μεθόδους ταξινόμησης: selection sort, merge sort, quick sort.)
- Αξιοποιείστε τη μέθοδο **`System.nanoTime()`** για να μετρήσετε το χρόνο εκτέλεσης:
  ```java
  long start = System.nanoTime();
  insertionSort(table);
  long elapsedTime = System.nanoTime() - start;
                   // measures time in nano seconds
  ```
- Για κάθε συνάρτηση ταξινόμησης: δημιουργήστε πίνακες με τυχαίο τρόπο (π.χ. στοιχεία από 0 έως 100) και διαφορετικά πλήθη (π.χ. 100, 200, …, 1000)· για κάθε πλήθος επαναλάβετε αρκετές φορές (π.χ. 50) και υπολογίστε τον **μέσο** χρόνο· παρουσιάστε τα αποτελέσματα αριθμητικά και ως γραφικές παραστάσεις.

> [!example]- Ενδεικτική υλοποίηση της `main` (➕, ελέγχθηκε η λογική χωρίς γραφικά)
> ```java
> public static void main(String[] args){
>    int REPS = 50;
>    double[] tBubble = new double[10], tInsert = new double[10];
>    System.out.println("Size\tBubble Sort\tInsertion Sort");
>    for (int k = 0; k < 10; k++){
>       int n = 100 * (k + 1);
>       long sumB = 0, sumI = 0;
>       for (int r = 0; r < REPS; r++){
>          int[] a = new int[n], b = new int[n];
>          for (int i = 0; i < n; i++) a[i] = b[i] = (int)(Math.random() * 101);
>          long start = System.nanoTime(); bubbleSort(a);    sumB += System.nanoTime() - start;
>          start = System.nanoTime();      insertionSort(b); sumI += System.nanoTime() - start;
>          if (!sorted(a) || !sorted(b)) System.out.println("ERROR");
>       }
>       tBubble[k] = (double) sumB / REPS;  tInsert[k] = (double) sumI / REPS;
>       System.out.println(n + "\t" + tBubble[k] + "\t" + tInsert[k]);
>    }
>    DrawGraph.plot(tBubble, tInsert);     // κόκκινο: bubble, πράσινο: insertion
> }
> ```
> - Οι `a` και `b` έχουν **ίδιο** περιεχόμενο αλλά είναι **διαφορετικοί** πίνακες (όχι `b = a`), ώστε ο δεύτερος αλγόριθμος να μην πάρει ήδη ταξινομημένο πίνακα.
> - `(double) sumB / REPS`: χωρίς το cast η διαίρεση `long / int` είναι ακέραια.

| Size | Bubble Sort (ns) | Insertion Sort (ns) | | Size | Merge Sort (ns) | Quick Sort (ns) |
|---|---|---|---|---|---|---|
| 100 | 60806.7 | 55677.54 | | 100 | 12118.84 | 9355.34 |
| 500 | 198793.42 | 98489.1 | | 500 | 28591.1 | 27571.04 |
| 1000 | 1493227.1 | 364276.86 | | 1000 | 58949.88 | 55255.62 |

(απόσπασμα από τις VIII-53 και VIII-57· η VIII-55 συγκρίνει bubble με merge sort: `897496.1` έναντι `58596.84` στο 1000)

> [!important] Τι δείχνουν οι γραφικές παραστάσεις (VIII-54, VIII-56, VIII-58, VIII-59)
> - **Bubble, insertion, selection sort – O(n²)**: διπλασιασμός του `n` → περίπου **τετραπλασιασμός** του χρόνου. Η καμπύλη «σηκώνεται» απότομα.
> - **Merge sort, quick sort – O(n log n)**: σχεδόν ευθεία γραμμή, πολύ χαμηλότερα.
> - Και οι δύο O(n²) έχουν την ίδια τάξη, αλλά ο insertion sort είναι πρακτικά ταχύτερος (σταματά νωρίς με τη σημαία `stop`, κάνει λιγότερες αντιμεταθέσεις στον μέσο όρο).

> [!warning] ➕ Γιατί οι πρώτες μετρήσεις είναι «παράξενες»
> Στη VIII-53 ο bubble sort στο `200` (47959.0) είναι **ταχύτερος** από το `100` (60806.7), και στη VIII-57 το `100` του merge sort είναι αργό σε σχέση με τα επόμενα. Δεν είναι λάθος του αλγορίθμου: στις πρώτες εκτελέσεις η JVM ακόμη «ζεσταίνεται» (φορτώνει κλάσεις, μεταγλωττίζει τον κώδικα σε κώδικα μηχανής – JIT). Για αξιόπιστες μετρήσεις: μερικές «προθερμαντικές» εκτελέσεις πριν τη μέτρηση, και μέσος όρος πολλών επαναλήψεων (γι' αυτό τα 50).

## 7. Client – Server: η αρθρωτή εικόνα (VIII-60 … VIII-62)

| Client (χρησιμοποιεί) | → | Server (παρέχει) |
|---|---|---|
| `Newton`, `SortLib` | → | `DrawGraph` |
| `DrawGraph` | → | `StdDraw`, `Color` |
| `StdDraw` | → | `Color` |

Κάθε κλάση είναι **client** των βιβλιοθηκών που χρησιμοποιεί και **server** για όσες τη χρησιμοποιούν. Η `DrawGraph` είναι server για τη `SortLib` (σχεδιάζει τους χρόνους) και client της `StdDraw`. Ο καθένας ξέρει μόνο τη **διεπαφή** (`public`) του από κάτω.

![[Συναρτήσεις - Client Server.png|800]]

> [!note] Σύνοψη της Ενότητας VIII (VIII-61, VIII-62)
> - Η έννοια της συνάρτησης είναι σημαντικότατη για τον δομημένο προγραμματισμό: **αφαιρετικότητα** προγράμματος, **αρθρωτές** λύσεις.
> - Εξετάσθηκαν **στατικές** συναρτήσεις/μέθοδοι.
> - Διεπαφή – signature: διαχωρισμός ανάμεσα στο «τι» και το «πώς» · παράμετροι – `return`.
> - Κλήσεις – ορίσματα – binding: **πέρασμα δια τιμής** · τιμές που είναι διευθύνσεις (πίνακες, αντικείμενα).
> - Ροή ελέγχου · εμβέλεια ονομασιών · function overloading · βιβλιοθήκες με επαναχρησιμοποιήσιμες συναρτήσεις (`public` – `private`).
> - Θα επανέλθουμε στις συναρτήσεις: **αναδρομικές** συναρτήσεις ([[Uni/ΕΠΛ131/10 - Αναδρομή/00 - Ευρετήριο|Ενότητα X]]) και μέθοδοι αναφοράς για αντικείμενα.
>
> Στο βιβλίο: Ενότητες **2.1** και **2.2** (VIII-63).

## Συχνά Λάθη

> [!warning] Συχνά Λάθη
> - Βοηθητικές συναρτήσεις ως `public`: «φουσκώνουν» το API και δεσμεύουν τη βιβλιοθήκη να τις κρατά για πάντα.
> - Βρόχος `i < ys.length` (αντί για `ys.length-1`) όταν χρησιμοποιείς `ys[i+1]` → εκτός ορίων.
> - Κοινός βρόχος για δύο πίνακες διαφορετικού μήκους.
> - Μέτρηση χρόνου με **ήδη ταξινομημένο** πίνακα (π.χ. ταξινόμηση του ίδιου πίνακα και από τους δύο αλγόριθμους): ο δεύτερος δείχνει ψεύτικα καλό χρόνο.
> - Ακέραια διαίρεση στον μέσο όρο χρόνων.
> - Σύγχυση του bubble sort με την insertion: ο bubble «σπρώχνει» το **μεγαλύτερο** προς το τέλος σε κάθε πέρασμα· η insertion «βυθίζει» το **νέο** στοιχείο στο ταξινομημένο αριστερό κομμάτι.

## Σχετικά

- Προηγούμενο: [[05 - Υπερφόρτωση Συναρτήσεων]]
- `StdDraw`: [[05 - Γραφικά με StdDraw|VII – 05]] · Αρχές (απόκρυψη, σύζευξη, επαναχρησιμοποίηση): [[03 - Σχεδιασμός Μονάδων|V – 03]] · [[04 - Demeter, Βελτιστοποίηση, Επαναχρησιμοποίηση και Αλλαγή|V – 04]]
- Γραμμική και δυαδική αναζήτηση (log₂N): [[06 - Αναζήτηση και break|IV – 06]]
- Γρήγορη επανάληψη: [[Uni/ΕΠΛ131/08 - Συναρτήσεις/07 - Τυπολόγιο|07 - Τυπολόγιο]] · Εξάσκηση: [[Uni/ΕΠΛ131/08 - Συναρτήσεις/08 - Ασκήσεις|08 - Ασκήσεις]]
