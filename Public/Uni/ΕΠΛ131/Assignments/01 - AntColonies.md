---
publish: true
---
# 01 - AntColonies (Ant, Cell, CellGrid)

Πλήρης υλοποίηση σε Java των αντικειμένων **`Cell`**, **`CellGrid`** και **`Ant`** για την άσκηση προσομοίωσης αποικιών μυρμηγκιών (`AntColonies.java`) του **ΕΠΛ 131**.

> [!note] Τι δίνεται ήδη στο περίγραμμα
> Τα πεδία, οι κατασκευαστές και η `draw()` της `CellGrid` δίνονται ήδη στα αρχεία-περιγράμματα. Οι κώδικες παρακάτω περιλαμβάνουν **όλες** τις απαιτούμενες μεθόδους της διεπαφής (API) — συμπεριλαμβανομένων των **`toString()`** και των τριών κλάσεων.

---

## 1. `Cell.java`

Κάθε κελί διατηρεί δυναμικά τους πίνακες `antIds` (ταυτότητες μυρμηγκιών πάνω στο κελί) και `times` (χρονικά σημεία κάθε μονάδας μυρωδιάς), χωρίς χρήση `ArrayList` — με χειροκίνητη αύξηση/μείωση πίνακα (όπως στη `TabLib` της [[Uni/ΕΠΛ131/06 - Συμβολοσειρές/06 - Πίνακες Συμβολοσειρών|Ενότητας VI]]).

```java
public class Cell {
    private boolean hasNest; // κατά πόσο έχει πάνω του φωλιά
    private int foodAmount;  // πόσους σπόρους έχει επί του παρόντος
    private int scentAmount; // πλήθος μονάδων μυρωδιάς που δεν έχουν εξατμιστεί
    private int[] times;     // χρονικά σημεία κατά τα οποία χρίστηκε
    private int[] antIds;    // ταυτότητες των μυρμηγκιών στο σημείο αυτό

    public Cell() {
        hasNest = false;
        foodAmount = 0;
        scentAmount = 0;
        times = null;
        antIds = null;
    }

    public boolean hasFood() {
        return foodAmount > 0;
    }

    public void getFood() {
        if (foodAmount > 0) {
            foodAmount--;
        }
    }

    public void putFood() {
        foodAmount++;
    }

    public void putFood(int food) {
        if (food > 0) {
            foodAmount += food;
        }
    }

    public boolean hasAnts() {
        return antIds != null && antIds.length > 0;
    }

    public void putNest() {
        hasNest = true;
    }

    public boolean withNest() {
        return hasNest;
    }

    public int getScent() {
        return scentAmount;
    }

    public void addAnt(int antID) {
        if (antIds == null) {
            antIds = new int[1];
            antIds[0] = antID;
        } else {
            int[] newArr = new int[antIds.length + 1];
            for (int i = 0; i < antIds.length; i++) {
                newArr[i] = antIds[i];
            }
            newArr[antIds.length] = antID;
            antIds = newArr;
        }
    }

    public void removeAnt(int antID) {
        if (antIds == null) return;
        int idx = -1;
        for (int i = 0; i < antIds.length; i++) {
            if (antIds[i] == antID) {
                idx = i;
                break;
            }
        }
        if (idx == -1) return;

        if (antIds.length == 1) {
            antIds = null;
        } else {
            int[] newArr = new int[antIds.length - 1];
            int k = 0;
            for (int i = 0; i < antIds.length; i++) {
                if (i != idx) {
                    newArr[k++] = antIds[i];
                }
            }
            antIds = newArr;
        }
    }

    public void addScent(int time) {
        scentAmount++;
        if (times == null) {
            times = new int[1];
            times[0] = time;
        } else {
            int[] newTimes = new int[times.length + 1];
            for (int i = 0; i < times.length; i++) {
                newTimes[i] = times[i];
            }
            newTimes[times.length] = time;
            times = newTimes;
        }
    }

    public void updateScent(int curTime, int elapsed) {
        if (times == null) return;

        int keep = 0;
        for (int i = 0; i < times.length; i++) {
            if (curTime - times[i] <= elapsed) {
                keep++;
            }
        }

        if (keep == 0) {
            times = null;
            scentAmount = 0;
        } else {
            int[] newTimes = new int[keep];
            int k = 0;
            for (int i = 0; i < times.length; i++) {
                if (curTime - times[i] <= elapsed) {
                    newTimes[k++] = times[i];
                }
            }
            times = newTimes;
            scentAmount = keep;
        }
    }

    public String toString() {
        String s = hasNest ? "Cell that has a nest.\n" : "Cell that does not have a nest.\n";
        if (foodAmount == 0) {
            s += "- There are no seeds.\n";
        } else if (hasNest) {
            s += "- The nest has " + foodAmount + " stored seeds.\n";
        } else {
            s += "- The cell has " + foodAmount + " seeds for collection.\n";
        }
        if (!hasNest && scentAmount > 0) {
            s += "- Currently it is annotated with " + scentAmount + " units of scent.\n";
        }
        int nAnts = (antIds == null) ? 0 : antIds.length;
        s += "- At present there are " + nAnts + " ants on it.\n";
        return s;
    }
}
```

---

## 2. `CellGrid.java`

Το καρτεσιανό πεδίο $N \times N$ διαχειρίζεται τον δισδιάστατο πίνακα `Cell[][] grid`.

```java
public class CellGrid {
    private int size;    // το μέγεθός του
    private Cell[][] grid; // τα σημεία που το απαρτίζουν

    public CellGrid(int N) {
        size = N;
        grid = new Cell[N][N];
        for (int i = 0; i < N; i++)
            for (int j = 0; j < N; j++)
                grid[i][j] = new Cell();
    }

    public int getSize() {
        return size;
    }

    public Cell getCell(int x, int y) {
        if (x < 0 || x >= size || y < 0 || y >= size) {
            return null;
        }
        return grid[x][y];
    }

    public void putNest(int x, int y, int[] antIds) {
        grid[x][y].putNest();
        if (antIds != null) {
            for (int i = 0; i < antIds.length; i++) {
                grid[x][y].addAnt(antIds[i]);
            }
        }
    }

    public void putFood(int x, int y, int food) {
        grid[x][y].putFood(food);
    }

    public void updateScent(int time, int elapsed) {
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                grid[i][j].updateScent(time, elapsed);
            }
        }
    }

    public boolean allSeedsCollected() {
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                if (!grid[i][j].withNest() && grid[i][j].hasFood()) {
                    return false;
                }
            }
        }
        return true;
    }

    public String toString() {
        String s = "A " + size + "x" + size + " Terain as follows:\n";
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                Cell c = grid[i][j];
                if (c.withNest() || c.hasFood() || c.getScent() > 0 || c.hasAnts()) {
                    s += "Cell(" + i + "," + j + "):\n" + c.toString();
                }
            }
        }
        s += "All other cells are empty.\n";
        return s;
    }

    // Η draw() δίνεται ήδη στο περίγραμμα του μαθήματος (χρησιμοποιεί StdDraw).
}
```

---

## 3. `Ant.java`

Κύρια σημεία της συμπεριφοράς της `move(int time)`:
- **`searchFood(int time)`**:
  1. Βρίσκει τα έγκυρα ορθογώνια γειτονικά κελιά (πάνω, κάτω, αριστερά, δεξιά), **εξαιρώντας** το `(previousX, previousY)` ώστε να αποφεύγονται κύκλοι μπρος–πίσω.
  2. Αν κάποιο/α από αυτά έχουν μυρωδιά (`getScent() > 0`), διαλέγει τυχαία ανάμεσα σε εκείνα με τη **μέγιστη** μυρωδιά· αλλιώς διαλέγει τυχαία από όλα τα έγκυρα γειτονικά.
  3. Ενημερώνει τα κελιά (`removeAnt` από το παλιό, `addAnt` στο νέο) και τις συντεταγμένες (`previousX`, `previousY`, `pos`).
  4. Αν το νέο κελί **δεν** έχει φωλιά (`!nextCell.withNest()`) και έχει σπόρους (`nextCell.hasFood()`), παίρνει 1 σπόρο (`getFood()`) και θέτει `carriesFood = true`.
- **`goBackNest(int time)`**:
  1. Αν το μυρμήγκι βρίσκεται **ήδη** στη φωλιά του (`isAtNest()`), αποθέτει τον σπόρο (`putFood()`), θέτει `carriesFood = false` και μηδενίζει την προηγούμενη θέση (`previousX = -1; previousY = -1;`) ώστε στο επόμενο βήμα να μπορεί να κινηθεί προς οποιαδήποτε κατεύθυνση.
  2. Αλλιώς, χρίζει το **τρέχον** κελί με 1 μονάδα μυρωδιάς (`addScent(time)`), διαλέγει τυχαία ένα από τα (1 ή 2) βήματα συντομότερης διαδρομής προς τη φωλιά `nestPos`, και μετακινείται εκεί.

```java
public class Ant {
    private CellGrid terain;     // το πεδίο στο οποίο βρίσκεται και μπορεί να μετακινηθεί
    private int id;              // η ταυτότητά του
    private int[] pos;           // οι συντεταγμένες της τρέχουσας θέσης του
    private int previousX;       // η συντεταγμένη X της αμέσως προηγούμενης θέσης του
    private int previousY;       // η συντεταγμένη Y της αμέσως προηγούμενης θέσης του
    private int[] nestPos;       // οι συντεταγμένες της φωλιάς του
    private boolean carriesFood;   // κατά πόσο μεταφέρει ένα σπόρο
    private boolean justFoundFood; // αν μόλις βρήκε τροφή στο τρέχον βήμα (για toString)
    private String color;          // το χρώμα του

    public Ant(CellGrid grid, int Id, String col, int[] NestPos) {
        terain = grid;
        id = Id;
        color = new String(col);
        pos = new int[2];
        nestPos = new int[2];
        nestPos[0] = NestPos[0];
        nestPos[1] = NestPos[1];
        pos[0] = nestPos[0];
        pos[1] = nestPos[1]; // αρχικά είναι στη φωλιά του
        previousX = -1;
        previousY = -1;      // αρχικές εικονικές τιμές
        carriesFood = false;
        justFoundFood = false;
    }

    public boolean isAtNest() {
        return pos[0] == nestPos[0] && pos[1] == nestPos[1];
    }

    public boolean wasAt(int x, int y) {
        return previousX == x && previousY == y;
    }

    public boolean isAt(int x, int y) {
        return pos[0] == x && pos[1] == y;
    }

    public int getId() {
        return id;
    }

    public int[] getPos() {
        return new int[] { pos[0], pos[1] };
    }

    public int[] getNestPos() {
        return new int[] { nestPos[0], nestPos[1] };
    }

    public boolean carries_food() {
        return carriesFood;
    }

    public void move(int time) {
        if (!carriesFood) searchFood(time);
        else goBackNest(time);
    }

    private void searchFood(int time) {
        int[][] dirs = { { -1, 0 }, { 1, 0 }, { 0, -1 }, { 0, 1 } };
        int n = terain.getSize();
        int[][] valid = new int[4][2];
        int count = 0;

        // Συλλογή έγκυρων γειτονικών κελιών, εξαιρώντας το αμέσως προηγούμενο
        for (int i = 0; i < 4; i++) {
            int nx = pos[0] + dirs[i][0];
            int ny = pos[1] + dirs[i][1];
            if (nx >= 0 && nx < n && ny >= 0 && ny < n && !wasAt(nx, ny)) {
                valid[count][0] = nx;
                valid[count][1] = ny;
                count++;
            }
        }

        // Εφεδρική περίπτωση αν το μόνο έγκυρο γειτονικό είναι το προηγούμενο
        if (count == 0) {
            for (int i = 0; i < 4; i++) {
                int nx = pos[0] + dirs[i][0];
                int ny = pos[1] + dirs[i][1];
                if (nx >= 0 && nx < n && ny >= 0 && ny < n) {
                    valid[count][0] = nx;
                    valid[count][1] = ny;
                    count++;
                }
            }
        }
        if (count == 0) return;

        // Προτεραιότητα στη μέγιστη μυρωδιά
        int maxScent = 0;
        for (int i = 0; i < count; i++) {
            int sc = terain.getCell(valid[i][0], valid[i][1]).getScent();
            if (sc > maxScent) {
                maxScent = sc;
            }
        }

        int[][] best = new int[4][2];
        int bestCount = 0;
        if (maxScent > 0) {
            for (int i = 0; i < count; i++) {
                int sc = terain.getCell(valid[i][0], valid[i][1]).getScent();
                if (sc == maxScent) {
                    best[bestCount][0] = valid[i][0];
                    best[bestCount][1] = valid[i][1];
                    bestCount++;
                }
            }
        } else {
            best = valid;
            bestCount = count;
        }

        int pick = (int) (Math.random() * bestCount);
        int nextX = best[pick][0];
        int nextY = best[pick][1];

        // Μετακίνηση και ενημέρωση κελιών
        terain.getCell(pos[0], pos[1]).removeAnt(id);
        previousX = pos[0];
        previousY = pos[1];
        pos[0] = nextX;
        pos[1] = nextY;
        Cell nextCell = terain.getCell(pos[0], pos[1]);
        nextCell.addAnt(id);

        // Παίρνει σπόρο ΜΟΝΟ αν το κελί έχει τροφή και ΔΕΝ είναι φωλιά
        if (!nextCell.withNest() && nextCell.hasFood()) {
            nextCell.getFood();
            carriesFood = true;
            justFoundFood = true;
        }
    }

    private void goBackNest(int time) {
        justFoundFood = false;

        // Αν έφτασε ήδη στη φωλιά του, αφήνει τον σπόρο
        if (isAtNest()) {
            terain.getCell(pos[0], pos[1]).putFood();
            carriesFood = false;
            previousX = -1;
            previousY = -1;
            return;
        }

        // Χρίζει το τρέχον κελί με 1 μονάδα μυρωδιάς πριν απομακρυνθεί
        terain.getCell(pos[0], pos[1]).addScent(time);

        // Επιλογή ενός από τα βήματα συντομότερης διαδρομής προς nestPos
        int[][] candidates = new int[2][2];
        int count = 0;
        if (pos[0] < nestPos[0]) {
            candidates[count][0] = pos[0] + 1;
            candidates[count][1] = pos[1];
            count++;
        } else if (pos[0] > nestPos[0]) {
            candidates[count][0] = pos[0] - 1;
            candidates[count][1] = pos[1];
            count++;
        }
        if (pos[1] < nestPos[1]) {
            candidates[count][0] = pos[0];
            candidates[count][1] = pos[1] + 1;
            count++;
        } else if (pos[1] > nestPos[1]) {
            candidates[count][0] = pos[0];
            candidates[count][1] = pos[1] - 1;
            count++;
        }

        int pick = (int) (Math.random() * count);
        int nextX = candidates[pick][0];
        int nextY = candidates[pick][1];

        // Μετακίνηση και ενημέρωση κελιών
        terain.getCell(pos[0], pos[1]).removeAnt(id);
        previousX = pos[0];
        previousY = pos[1];
        pos[0] = nextX;
        pos[1] = nextY;
        terain.getCell(pos[0], pos[1]).addAnt(id);
    }

    public String toString() {
        String prefix = color + " Ant-" + id + " at (" + pos[0] + "," + pos[1] + "). ";
        if (isAtNest() && !carriesFood) {
            return prefix + "It is at its nest and does not hold any food.";
        } else if (isAtNest() && carriesFood) {
            return prefix + "It has returned to its nest and has food to deliver.";
        } else if (!carriesFood) {
            return prefix + "It is out looking for food.";
        } else if (justFoundFood) {
            return prefix + "It has found food!";
        } else {
            return prefix + "It is going back to its nest with food.";
        }
    }
}
```

---

## Συχνά Λάθη

> [!warning] Προσοχή στην υλοποίηση
> - **Σπόροι σε φωλιά:** Το μυρμήγκι μπορεί να περάσει από οποιαδήποτε φωλιά κατά την αναζήτηση, αλλά **ποτέ** δεν παίρνει σπόρο από φωλιά — απαραίτητος ο έλεγχος `!nextCell.withNest() && nextCell.hasFood()`.
> - **Ενθυλάκωση πινάκων (`getPos`, `getNestPos`):** Επιστρέφουμε αντίγραφο (`new int[] { ... }`) και όχι απευθείας αναφορά στο `private` πεδίο `pos` / `nestPos`, για αποφυγή aliasing.
> - **Εξάτμιση μυρωδιάς (`updateScent`):** Εξατμίζεται όταν `curTime - times[i] > elapsed` (γνήσια μεγαλύτερο του `elapsed`), και ο `scentAmount` πρέπει να μένει συγχρονισμένος με το `times.length`.
> - **Χρίσμα μυρωδιάς:** Το χρίσμα γίνεται πάνω στο κελί **από το οποίο φεύγει** το μυρμήγκι επιστρέφοντας (συμπεριλαμβανομένης της πηγής τροφής, **όχι** της φωλιάς).
> - **Απελευθέρωση σπόρου στη φωλιά:** Όταν το μυρμήγκι αφήνει τον σπόρο στη φωλιά, επαναφέρουμε `previousX = -1; previousY = -1;` ώστε να μπορεί να ξαναβγεί προς την κατεύθυνση από όπου ήρθε (ακολουθώντας τη μυρωδιά πίσω στην πηγή τροφής!).

## Σχετικά

- [[Uni/ΕΠΛ131/11 - Χρήση Αντικειμένων/00 - Ευρετήριο|Ενότητα XI – Χρήση Αντικειμένων]]
- [[Uni/ΕΠΛ131/12 - Δημιουργία Αντικειμένων/00 - Ευρετήριο|Ενότητα XII – Δημιουργία Αντικειμένων]]
- [[Uni/ΕΠΛ131/ΕΠΛ131 Διάγραμμα Ύλης|ΕΠΛ131 Διάγραμμα Ύλης]]
