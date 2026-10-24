---
publish: true
---
# 04 - Αρχεία με In και Out

Αντί για ένα κανάλι εισόδου και ένα εξόδου που ορίζει το λειτουργικό σύστημα, το πρόγραμμα ανοίγει **μόνο του** όσα αρχεία θέλει, ως **αντικείμενα** των κλάσεων `In` και `Out` (διαφάνειες VII-52 … VII-74).

## 1. Ρητή αναφορά σε αρχεία (VII-52)

> [!note] Τι αλλάζει
> - Η ρητή αναφορά σε αρχεία συνεπάγεται την αξιοποίηση **αφηρημένων τύπων** για αρχεία εισόδου και αρχεία εξόδου:
>   - Επομένως συγκεκριμένα αρχεία είναι περιπτώσεις **αντικειμένων**.
>   - Ως αφηρημένη έννοια, ένα αρχείο είναι απλά μια **ακολουθία χαρακτήρων**. Όμως οι **μέθοδοι αναφοράς** επιτρέπουν την επεξεργασία ενός αρχείου σε υψηλότερο επίπεδο από αυτό των ατομικών χαρακτήρων (αριθμοί, λέξεις, γραμμές).
> - Σε αντίθεση με την ανακατεύθυνση, τώρα μπορούμε να έχουμε **ταυτόχρονα πολλαπλά αρχεία** εισόδου ή/και εξόδου: κανάλια εισόδου (**input stream**) και κανάλια εξόδου (**output stream**).

| | Ανακατεύθυνση (`<`, `>`) | Ρητή αναφορά (`In`, `Out`) |
|---|---|---|
| Ποιος ανοίγει το αρχείο | το λειτουργικό σύστημα | το πρόγραμμα |
| Πλήθος αρχείων | ένα εισόδου, ένα εξόδου | **όσα θέλουμε**, ταυτόχρονα |
| Όνομα αρχείου | στη γραμμή εντολής, μετά το `<` | συνήθως **όρισμα** (`args[i]`), ή σταθερά στον κώδικα |
| Μέθοδοι | **στατικές** (`StdIn.readInt()`) | **αναφοράς** (`f.readInt()`) |
| Αλλάζει ο κώδικας; | όχι | ναι |

## 2. Οι κλάσεις αντικειμένων `In` και `Out` (VII-53 … VII-55)

> [!note] Ορισμοί
> - Η κλάση **`In`** αντιπροσωπεύει **αρχεία εισόδου**· η κλάση **`Out`** αρχεία **εξόδου**.
> - Η `In` περιλαμβάνει **ταυτόσημες** μεθόδους με την `StdIn`, και παρομοίως η `Out` με τις `System.out` και `StdOut`.
> - Όμως οι δικές τους μέθοδοι είναι **μέθοδοι αναφοράς** και **όχι στατικές** μέθοδοι όπως στην περίπτωση των `StdIn`, `System.out` και `StdOut`.
> - Και βεβαίως οι `In` και `Out` περιλαμβάνουν τους ομώνυμους **κατασκευαστές** τους.

| Κλάση `In` | |
|---|---|
| `In(String name)` | create input stream from name (κατασκευαστής) |
| `boolean isEmpty()` | `true` if no more values, `false` otherwise |
| `int readInt()` · `double readDouble()` · `long readLong()` · `boolean readBoolean()` · `char readChar()` · `String readString()` | read a value of type … |
| `String readLine()` | read the rest of the line |
| `String readAll()` | read the rest of the text |
| `void close()` | ➕ κλείνει το αρχείο |

| Κλάση `Out` | |
|---|---|
| `Out(String name)` | create output stream from name (κατασκευαστής) |
| `void print(String s)` · `void println(String s)` · `void println()` · `void printf(String f, ...)` | όπως στη `System.out` |
| `void close()` | ➕ κλείνει το αρχείο |

> [!important] Στατική μέθοδος vs μέθοδος αναφοράς
> ```java
> int a = StdIn.readInt();          // στατική: όνομα ΚΛΑΣΗΣ – μία μόνο standard είσοδος
> In f = new In("data.txt");        // κατασκευαστής: νέο αντικείμενο-αρχείο
> int b = f.readInt();              // αναφοράς: όνομα ΑΝΤΙΚΕΙΜΕΝΟΥ – ποιο αρχείο;
> ```
> Αφού μπορούν να υπάρχουν πολλά αρχεία, κάθε κλήση πρέπει να λέει **από ποιο** διαβάζει. Το `In.readInt()` δεν κάνει compile (`non-static method … cannot be referenced from a static context`) – ίδιο λάθος με το `String.length()` ([[01 - Το String ως Αφηρημένος Τύπος Δεδομένων|VI – 01]]).

> [!warning] ➕ Οι `In`/`Out` δεν είναι μέρος της Java
> Όπως οι `StdIn`/`StdOut` και η `StdDraw`, είναι από το booksite του βιβλίου (`In.java`, `Out.java` ή `stdlib.jar` στον φάκελο/classpath). Η «σκέτη» Java έχει `Scanner(new File(name))` και `PrintWriter(name)`, που θέλουν διαχείριση εξαιρέσεων (`FileNotFoundException`).

## 3. Μέτρηση χαρακτήρων και η παγίδα της isEmpty (VII-56)

Η VII-56 δείχνει το ίδιο πρόγραμμα με `In`/`Out` και με `StdIn`/`System.out`:

```java
In ifile = new In("input.txt");
Out ofile = new Out("result.txt");

int count = 0;

while(!ifile.isEmpty()){
  char c = ifile.readChar();
  count++;
}

ofile.print(count);
ifile.close();
ofile.close();
```

```java
int count = 0;

while(!StdIn.isEmpty()){
  char c = StdIn.readChar();
  count++;
}

System.out.print(count);
```

Η μόνη διαφορά: `ifile.` αντί για `StdIn.`, `ofile.` αντί για `System.out.`, και οι κατασκευαστές/`close`. Το πρώτο έχει τα ονόματα των αρχείων **μέσα** στον κώδικα· το δεύτερο τρέχει ως `java CountChars < input.txt > result.txt`.

> [!warning] ⚠️ Σημείωση για τη VII-56
> Ο κώδικας της διαφάνειας έχει τυπογραφικά εισαγωγικά (`“input.txt”`), που δεν κάνουν compile· στη Java μόνο `"`.

![[Αρχεία - isEmpty και Κενοί Χαρακτήρες.png|800]]

> [!warning] Το πρόγραμμα **δεν** μετρά όλους τους χαρακτήρες (ελέγχθηκε)
> Η `isEmpty()` ρωτά «υπάρχει άλλη **λέξη**;». Μόλις απομένουν μόνο κενοί χαρακτήρες (κενά, tab, `\n`), επιστρέφει `true` – ακόμη κι αν υπάρχουν χαρακτήρες να διαβαστούν με `readChar()`.
>
> | Αρχείο | Χαρακτήρες | `count` |
> |---|---|---|
> | `"ab\n"` | 3 | **2** – η τελική αλλαγή γραμμής δεν μετράει |
> | `"xy"` | 2 | 2 |
> | `"␣␣a␣b␣␣\n\n"` | 9 | **5** – μετράνε τα κενά πριν το `b`, όχι μετά |
>
> Σχεδόν κάθε αρχείο κειμένου τελειώνει με `\n`, άρα το αποτέλεσμα είναι συνήθως **ένα λιγότερο** από το πραγματικό μέγεθος. Για όλους τους χαρακτήρες: `count = ifile.readAll().length();`. Το `char c` δεν χρησιμοποιείται – μας ενδιαφέρει μόνο ότι **καταναλώνεται** ένας χαρακτήρας.

## 4. Κατασκευαστές `In()` και `In(String)` (VII-57)

> [!note] Πληροφορίες για `In()`
> - **`In()`**: χωρίς παραμέτρους επιστρέφει αναφορά στην **προκαθορισμένη είσοδο** (standard input).
> - **`In(String)`**: ανοίγει το αρχείο με το όνομα της παραμέτρου.
>   - Παράδειγμα: προσπάθησε να ανοίξεις μια **ιστοσελίδα**.
>   - Πετάει σφάλμα/εξαίρεση (**exception**) αν δεν υπάρχει.

```java
String name = "https://introcs.cs.princeton.edu/java/home/";
In inf = new In(name);

System.out.println(name);

while(!inf.isEmpty())
    System.out.println(inf.readLine());
```

Τυπώνει τη διεύθυνση και μετά τον **κώδικα HTML** της σελίδας, γραμμή-γραμμή. Για το πρόγραμμα, μια ιστοσελίδα είναι κι αυτή μια ακολουθία χαρακτήρων.

> [!tip] Τι εξαίρεση και πότε
> `new In("δεν_υπάρχει.txt")` → `IllegalArgumentException` («could not open …») **τη στιγμή της κατασκευής**, όχι στην πρώτη ανάγνωση. Με `new In()` το πρόγραμμα συμπεριφέρεται όπως με `StdIn` – χρήσιμο αν μια μέθοδος δέχεται ένα `In` και θέλουμε να της δώσουμε άλλοτε αρχείο, άλλοτε πληκτρολόγιο.

## 5. Μέσος όρος – Version 5: αρχείο από τη γραμμή εντολής (VII-59, VII-60)

```java
// Computing the average of a list of numbers
// Version 5: Reading input from file named
// on the command line

public class Average {

 public static void main(String[] args) {
  double sum = 0.0;
  int cnt = 0;
  In i_file = new In(args[0]);
  while (!i_file.isEmpty()){
     sum += i_file.readDouble();
     cnt++;
  }
  double average = sum/cnt;
  System.out.println("\nAverage is " + average);
 }

}
```

```
$ java Average Data.txt          ← όχι  < Data.txt
Average is 84.6
```

| Version | Πηγή δεδομένων | Εκτέλεση | Ποιος ανοίγει το `Data.txt` |
|---|---|---|---|
| 1 | ορίσματα | `java Average 45 67 2 109 200` | – |
| 2 | πληκτρολόγιο (`StdIn`) με prompts | `java Average` | – |
| 3 | `StdIn` με ανακατεύθυνση | `java Average < Data.txt` | το λειτουργικό σύστημα |
| (4) | `StdIn` από σωλήνα | `java RandomSeq … \| java Average` | – |
| 5 | `In` | `java Average Data.txt` | το πρόγραμμα |

> [!warning] «Μοιάζει ίδιο αλλά δεν είναι»
> - `java Average Data.txt` με τη **Version 3** → η `StdIn` περιμένει πληκτρολόγιο (το `Data.txt` αγνοείται, κάθεται στο `args`).
> - `java Average < Data.txt` με τη **Version 5** → `args` κενός → `ArrayIndexOutOfBoundsException` στο `args[0]`.

## 6. Συνένωση αρχείων: `Append` (VII-61 … VII-65)

```java
// Appends the contents of a set of input files
// named on the command line.
// Files are sequentially processed.

public class Append {

 public static void main(String[] args) {

  for (String name : args){
    In file = new In(name);
    String s = file.readAll();
    System.out.print(s);
    file.close(); // not necessary but good practice
  }

 }

}
```

```
$ java Append input1.txt input2.txt > result.txt
$ cat result.txt
One two three
four five
six
eight nine
ten
1 2 3
4 5 6 8
9
```

> [!important] Τι να προσέξεις
> - **Ένα** αντικείμενο `In` τη φορά, στη **σειρά** των ορισμάτων (sequentially processed). Η μεταβλητή `file` ξαναχρησιμοποιείται για κάθε αρχείο.
> - Η έξοδος πάει στη **standard έξοδο** – στο `result.txt` με **ανακατεύθυνση**. Συνδυάζονται και τα δύο: αρχεία εισόδου με `In`, έξοδος με `>`.
> - `print`, όχι `println`: η `readAll()` κρατά τις αλλαγές γραμμής του αρχείου.
> - Το `close()` «δεν είναι απαραίτητο» εδώ (το πρόγραμμα τελειώνει σύντομα και τα κλείνει όλα), αλλά είναι **καλή πρακτική**: κάθε ανοιχτό αρχείο δεσμεύει πόρους.

> [!warning] Αρχείο χωρίς τελική αλλαγή γραμμής (VII-65)
> Το `file2.txt` της διαφάνειας (φτιαγμένο από την `RandomFiles`, §7) τελειώνει σε `"… 38 39 "` **χωρίς** `\n` (έχει 15 αριθμούς και αλλαγή γραμμής γίνεται μόνο κάθε 10). Η `Append` δεν προσθέτει τίποτα ανάμεσα στα αρχεία, άρα η πρώτη γραμμή του `file3.txt` **κολλάει** στην τελευταία του `file2.txt`:
> ```
> 40 31 36 38 39 8 10 10 8 9 9 6 7 8 10
> ```
> Χωρίς το τελικό κενό θα έβγαινε `…38 398 10…` (ελέγχθηκε) – δύο αριθμοί ενωμένοι σε έναν.

> [!tip] Το `*` το επεκτείνει το shell (VII-65)
> `java Append file*.txt > result.txt` δίνει το ίδιο με `java Append file1.txt file2.txt file3.txt`: το shell αντικαθιστά το `file*.txt` με τα ονόματα που ταιριάζουν, **σε αλφαβητική σειρά**, πριν ξεκινήσει η Java. Άρα `args.length == 3`. Παγίδα: με 10+ αρχεία η σειρά είναι `file1, file10, file11, file2, …` (σύγκριση χαρακτήρων, όχι αριθμών).

## 7. Δημιουργία πολλών αρχείων: `RandomFiles` (VII-66 … VII-68)

```java
// Creates M separate files containing random numbers
// as for RandomSeq

public class RandomFiles {

 public static void main(String[] args) {
  int M = Integer.parseInt(args[0]);
  String seed = args[1];
  int N = Integer.parseInt(args[2]);
  int base = Integer.parseInt(args[3]);
  int limit = Integer.parseInt(args[4]);
  for (int f = 1; f <= M; f++){
    String name = seed + f + ".txt";
    Out output = new Out(name);
    for (int i = 1; i <= N; i++){
      output.print(base + (int)(Math.random()*(limit-base+1))
                     + "  ");
      if (i % 10 == 0) output.println();
    }
    output.close();
  }
 }
}
```

```
$ java RandomFiles 5 nums 10 1 100
$ ls nums*
nums1.txt  nums2.txt  nums3.txt  nums4.txt  nums5.txt
$ java Append nums* > result.txt
$ cat result.txt
80  34  13  31  1  96  56  79  33  12
68  24  37  7  55  8  90  88  31  96
…
```

> [!important] Σημεία
> - Το **όνομα** κάθε αρχείου φτιάχνεται με συνένωση: `seed + f + ".txt"` → `"nums" + 1 + ".txt"` = `"nums1.txt"` (`<seed><n>.txt`). Το `seed` είναι `String` (δεν χρειάζεται `parse`).
> - `new Out(name)` **μέσα** στον βρόχο: ένα νέο αρχείο/αντικείμενο ανά επανάληψη, κλείνει πριν ανοίξει το επόμενο.
> - Ίδια λογική με την `RandomSeq`, απλώς `output.print` αντί για `System.out.print`.
> - Με `N = 10`, κάθε αρχείο έχει μία γραμμή **με** τελικό `\n` (`10 % 10 == 0`). Με `N = 15` το αρχείο τελειώνει σε κενό χωρίς `\n` (το `file2.txt` του §6).
> - 5 ορίσματα: αν λείπει κάποιο → `ArrayIndexOutOfBoundsException`. Η σειρά τους έχει σημασία: `M seed N base limit`.

> [!warning] `new Out(name)` σβήνει
> Αν το `nums1.txt` υπάρχει ήδη, το περιεχόμενό του **χάνεται** τη στιγμή της κατασκευής (όπως το `>`). Το ξανατρέξιμο της `RandomFiles` αντικαθιστά τα αρχεία, δεν προσθέτει.

## 8. Συγχώνευση γραμμών: `Merge` (VII-69 … VII-71)

**Ψευδοκώδικας**
```
άνοιξε file1, file2 για ανάγνωση και file3 για εγγραφή
όσο και τα δύο έχουν περιεχόμενο:
    γράψε την επόμενη γραμμή του file1 στο file3
    γράψε την επόμενη γραμμή του file2 στο file3
αν το file1 έχει ακόμη περιεχόμενο: γράψε όλο το υπόλοιπό του
αν το file2 έχει ακόμη περιεχόμενο: γράψε όλο το υπόλοιπό του
κλείσε και τα τρία
```

```java
// Merges the contents of two input files into an
// output file

public class Merge {

 public static void main (String[] args){
    In file1 = new In(args[0]);
    In file2 = new In(args[1]);
    Out file3 = new Out(args[2]);
    while (!file1.isEmpty() && !file2.isEmpty()){
      file3.println(file1.readLine());
      file3.println(file2.readLine());
    }
    if (!file1.isEmpty())
       file3.print(file1.readAll());
    if (!file2.isEmpty())
       file3.print(file2.readAll());
    file1.close();
    file2.close();
    file3.close();
 }
}
```

```
$ java Merge input1.txt input2.txt out.txt
$ cat out.txt
One two three
1 2 3
four five
4 5 6 8
six
9
eight nine
ten
```

![[Αρχεία - Merge.png|800]]

> [!important] Γιατί δουλεύει
> - Ο βρόχος συνεχίζει όσο έχουν περιεχόμενο **και τα δύο** (`&&`): σταματά μόλις τελειώσει **ένα**.
> - Μετά τον βρόχο, **το πολύ ένα** από τα δύο `if` εκτελείται: το αρχείο που έμεινε. Αν τελείωσαν μαζί, κανένα.
> - `println(readLine())`: η `readLine()` **αφαιρεί** το `\n`, άρα το ξαναβάζουμε. `print(readAll())`: η `readAll()` το **κρατά**.
> - Τρία ορίσματα = τρία αρχεία: **τα ονόματα** έρχονται από τη γραμμή εντολής, τα **περιεχόμενα** από τα αρχεία. Κανένα `<` ή `>`.

> [!example]- Περιπτώσεις-παγίδες (ελέγχθηκαν)
> - **Ανάποδα ορίσματα** (`java Merge input2.txt input1.txt out.txt`): πρώτα `1 2 3`, μετά `One two three`, …, και στο τέλος `eight nine`, `ten` από το (μακρύτερο) `input1.txt`. Η σειρά αλλάζει, το περιεχόμενο όχι.
> - **Κενή γραμμή στη μέση** του `file1` (`"a\n\nb\n"`): η `isEmpty()` είναι `false` (ακολουθεί το `b`), η `readLine()` επιστρέφει `""`, και γράφεται κενή γραμμή κανονικά.
> - **Κενές γραμμές στο τέλος** ενός αρχείου: **χάνονται** – όταν απομένουν μόνο `\n`, η `isEmpty()` λέει `true`.
> - **Ίδιο αρχείο για είσοδο και έξοδο** (`java Merge a.txt b.txt a.txt`): το `new Out("a.txt")` το **σβήνει** πριν διαβαστεί → το `file1` είναι κενό από την αρχή, και το `out` έχει μόνο το `b.txt`.
> - **Ανύπαρκτο αρχείο εισόδου** → `IllegalArgumentException` στο `new In(…)`.

## 9. Προσθήκη σε υπάρχον αρχείο: `Concatenate` (VII-72, VII-73)

**Ψευδοκώδικας**
```
διάβασε ΟΛΟ το args[0] σε s και κλείσ' το
άνοιξε το args[0] για εγγραφή (σβήνεται) και γράψε ξανά το s
για κάθε επόμενο όρισμα i = 1, 2, …:
    διάβασε όλο το args[i] και γράψ' το στο args[0]
κλείσε το args[0]
```

```java
// Concatenates a set of input files and appends
// them at the end of an (existing) output file

public class Concatenate {

 public static void main(String[] args) {
  In t_file = new In(args[0]);
  String s = t_file.readAll();
  t_file.close();
  Out o_file = new Out(args[0]);
  o_file.print(s);
  for (int i = 1; i < args.length; i++){
    In i_file = new In(args[i]);
    s = i_file.readAll();
    o_file.print(s);
    i_file.close();
  }
  o_file.close();
 }
}
```

```
$ java Concatenate out.txt file*txt
$ cat out.txt
One two three
1 2 3
…
ten
1 19 16 14 3 2 18 19 20 1
38 34 39 36 32 39 40 38 31 36
40 31 36 38 39 8 10 10 8 9 9 6 7 8 10
6 8 7 8 9 9 10 10 7 6
```

![[Αρχεία - Σειρά In και Out.png|800]]

> [!important] Γιατί πρώτα `readAll` και μετά `new Out`
> Η `Out` **δεν** έχει λειτουργία «προσθήκης στο τέλος»: ο κατασκευαστής **ξαναδημιουργεί** το αρχείο από την αρχή. Άρα για να «προσθέσουμε», διαβάζουμε πρώτα όλο το παλιό περιεχόμενο στη μνήμη (`s`), μετά ανοίγουμε για εγγραφή και γράφουμε **ξανά** το παλιό και μετά τα νέα. Αν αλλάξει η σειρά, το παλιό περιεχόμενο χάνεται. Το `args[0]` είναι ταυτόχρονα **είσοδος** και **έξοδος** – το μόνο πρόγραμμα της ενότητας που το κάνει.

> [!warning] Περιπτώσεις-παγίδες (ελέγχθηκαν)
> - Το `args[0]` πρέπει να **υπάρχει** ήδη («existing» στο σχόλιο): αλλιώς `IllegalArgumentException` στο `new In(args[0])`, πριν γραφτεί οτιδήποτε.
> - `java Concatenate d.txt d.txt` → το `d.txt` **διπλασιάζεται**: όταν το `i = 1` το ξαναδιαβάζει, το αρχείο έχει ήδη γραμμένο το `s` (η `print` της `Out` κάνει flush αμέσως). Με `d.txt d.txt d.txt` → 4 αντίγραφα.
> - Το `t_file.close()` πριν το `new Out` είναι **ουσιαστικό**, όχι απλή καλή πρακτική: δεν διαβάζουμε και γράφουμε το ίδιο αρχείο ταυτόχρονα.
> - Με ένα μόνο όρισμα, το αρχείο ξαναγράφεται ίδιο (ο `for` δεν εκτελείται).
> - Όλο το αρχείο περνά από τη μνήμη (`String s`): για τεράστια αρχεία, πρακτικός περιορισμός.

## 10. Επισημάνσεις για αρχεία κειμένου (VII-74)

> [!note] Τι είναι ένα αρχείο κειμένου
> - Το λειτουργικό σύστημα (Unix/Linux) **δεν υποστηρίζει** οποιαδήποτε δομή: κάθε αρχείο κειμένου είναι απλά μια **ακολουθία χαρακτήρων** η οποία τερματίζεται από τον ειδικό χαρακτήρα **EOF**.
> - Η δομή ενός τέτοιου αρχείου είναι καθαρά **«ιδεατή»** και ερμηνεύεται μέσω των κατάλληλων εντολών εισόδου (για την εισαγωγή στοιχείων από αρχείο κειμένου) ή εξόδου (για τη δημιουργία αρχείου κειμένου).
> - Σε κάθε περίπτωση η επεξεργασία είναι **σειριακή**.
> - Τα αρχεία αποθηκεύονται σε **δευτερεύουσα μνήμη**· για τη σχετική επεξεργασία τα περιεχόμενά τους πρέπει να εισαχθούν σε **πρωτεύουσα** μνήμη.

> [!tip] Τι σημαίνουν στην πράξη
> - **«Ιδεατή» δομή**: οι «γραμμές» είναι απλώς χαρακτήρες `\n` μέσα στην ακολουθία· οι «αριθμοί» είναι ψηφία ανάμεσα σε κενά. Το ίδιο αρχείο `"45 67\n2\n"` είναι 3 αριθμοί για τη `readDouble()`, 2 γραμμές για τη `readLine()`, 8 χαρακτήρες για τη `readAll().length()`.
> - **Σειριακή** επεξεργασία: διαβάζεις από την αρχή προς το τέλος, κάθε ανάγνωση **καταναλώνει**. Δεν γυρνάς πίσω – για δεύτερο πέρασμα ανοίγεις νέο `In` (ή κρατάς τα δεδομένα σε πίνακα/`String`).
> - **EOF** (End Of File): στο πληκτρολόγιο το «στέλνουμε» με `Ctrl-D` / `Ctrl-Z, Enter`. Δεν είναι χαρακτήρας που διαβάζεται· η `isEmpty()` απλώς επιστρέφει `true`.
> - Αρχεία εισόδου στη **δευτερεύουσα** μνήμη (δίσκος), μεταβλητές του προγράμματος στην **πρωτεύουσα** (RAM): γι' αυτό η `Concatenate` φέρνει πρώτα όλο το αρχείο σε ένα `String`.

## Συχνά Λάθη

> [!warning] Συχνά Λάθη
> - `In.readInt()` / `Out.println(…)` χωρίς αντικείμενο → compile error (μέθοδοι αναφοράς).
> - `new Out(x)` πριν διαβαστεί το `x` → το περιεχόμενο χάνεται.
> - `java Average < Data.txt` σε πρόγραμμα με `new In(args[0])` (και αντίστροφα).
> - `println(file.readAll())` → επιπλέον κενή γραμμή στο τέλος.
> - Νομίζεις ότι η `isEmpty()` + `readChar()` μετρά όλους τους χαρακτήρες.
> - Ξεχνάς ότι κενές γραμμές στο τέλος ενός αρχείου «δεν υπάρχουν» για την `isEmpty()`.
> - Ξεχνάς το `close()` σε `Out` σε μεγαλύτερα προγράμματα → δεδομένα που δεν γράφτηκαν ακόμη στον δίσκο (με τις κλάσεις του βιβλίου η `print` κάνει flush, με `PrintWriter` της Java όχι).
> - Αρχεία χωρίς τελικό `\n` → η `Append` κολλά γραμμές μεταξύ αρχείων.

## Σχετικά

- Προηγούμενο: [[03 - Ανακατεύθυνση και Σωλήνωση]] · Επόμενο: [[05 - Γραφικά με StdDraw]]
- Μέθοδοι αναφοράς, κατασκευαστές, αντικείμενα: [[01 - Το String ως Αφηρημένος Τύπος Δεδομένων|VI – 01]]
- `readLine`/`readString`/`readAll`, `CountLines`: [[03 - Standard Είσοδος και Επεξεργασία Αρχείων|VI – 03]]
- Γρήγορη επανάληψη: [[Uni/ΕΠΛ131/07 - Είσοδος και Έξοδος/06 - Τυπολόγιο|06 - Τυπολόγιο]] · Εξάσκηση: [[Uni/ΕΠΛ131/07 - Είσοδος και Έξοδος/07 - Ασκήσεις|07 - Ασκήσεις]]
