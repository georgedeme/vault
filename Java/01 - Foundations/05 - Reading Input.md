# Reading Input in Java

A program reads keyboard input through <span class="hl-blue">`System.in`</span>, a stream of raw bytes. To turn those bytes into words, lines, and numbers, you wrap the stream in a reader. This chapter covers `Scanner` (convenient, parses numbers for you) and `BufferedReader` (faster, reads whole lines). It explains the difference between **token-based** and **line-based** reading, which causes the most common input bug, and shows how to turn text into numbers with `Integer.parseInt` / `Double.parseDouble`. It also covers validating input with retry loops, reading until the input ends, the locale trap in `nextDouble`, and why a program should use exactly one `Scanner` on `System.in` and never close it.

Command-line arguments, the other way to pass values to a program, are covered in [[Java/01 - Foundations/01 - Introduction to Java#5.3 Command-Line Arguments|Introduction to Java § 5.3]]. The validation loops use `while` and `do-while` from [[Java/02 - Control Flow/02 - Loops|Loops]], and a few examples use `try`/`catch`, which is explained fully in [[Java/05 - Working with Data and Errors/01 - Exception Handling|Exception Handling]]. Reading from **files** is in [[Java/07 - Input and Output/01 - File I-O|File I/O]].

## Contents

- [[#1. Where Keyboard Input Comes From|1. Where Keyboard Input Comes From]]
- [[#2. `Scanner` Basics|2. `Scanner` Basics]]
- [[#3. Token-Based vs. Line-Based Reading|3. Token-Based vs. Line-Based Reading]]
- [[#4. Parsing Strings into Numbers|4. Parsing Strings into Numbers]]
- [[#5. Validating Input|5. Validating Input]]
- [[#6. Comparing Input Strings|6. Comparing Input Strings]]
- [[#7. Reading Until the End of Input|7. Reading Until the End of Input]]
- [[#8. Locale and Decimal Numbers|8. Locale and Decimal Numbers]]
- [[#9. `BufferedReader`|9. `BufferedReader`]]
- [[#10. One `Scanner` for the Whole Program|10. One `Scanner` for the Whole Program]]
- [[#11. Common Pitfalls|11. Common Pitfalls]]
- [[#12. Quick Reference — Non-Obvious Outcomes|12. Quick Reference — Non-Obvious Outcomes]]
- [[#13. Practice — Trick Questions|13. Practice — Trick Questions]]
- [[#14. Summary|14. Summary]]

---

## 1. Where Keyboard Input Comes From

> [!note] Definitions
> - **Standard input** (`System.in`) is the stream a program reads from. By default it's connected to the keyboard. It is an `InputStream`, so it delivers **bytes**, not text or numbers.
> - A **reader** wraps `System.in` and turns the bytes into something usable. `Scanner` splits the text into tokens and parses numbers. `BufferedReader` returns whole lines.
> - **End of input (EOF)** is the point where the stream has no more data and never will. With a file, it's the end of the file. With the keyboard, the user signals it with a special key (see [[#7.1 What End of Input Means|§ 7.1]]).

Three facts explain most of the surprises in this chapter:

1. **The program receives nothing until the user presses Enter.** The terminal collects the line (so the user can correct typos with Backspace) and then delivers it all at once, **including the line separator** (`\n`, or `\r\n` on Windows). That separator stays in the input until something reads past it. This causes the trap in [[#3.2 The `nextInt` Then `nextLine` Trap|§ 3.2]].
2. **Reading blocks.** A call like `nextInt()` waits, for as long as it takes, until there is enough input to answer. A program that "hangs" is usually waiting for input.
3. **The program can't tell where the input comes from.** The same code reads from the keyboard, from a file (`java App < input.txt`), or from another program (`echo 5 | java App`). Automated graders use redirection, so code that only works when typing by hand is broken code.

---

## 2. `Scanner` Basics

### 2.1 Creating a `Scanner`

```java
import java.util.Scanner;                       // Scanner lives in java.util

public class Greeting {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);    // one Scanner, wrapping standard input
        System.out.print("Your name: ");
        String name = sc.nextLine();            // a whole line: "Ada Lovelace"
        System.out.print("Your age: ");
        int age = sc.nextInt();                 // a number: 36
        System.out.println("Hello " + name + ", next year you'll be " + (age + 1) + ".");
    }
}
```

```
Your name: Ada Lovelace
Your age: 36
Hello Ada Lovelace, next year you'll be 37.
```

- Without `import java.util.Scanner;` (or `import java.util.*;`), the code fails with *cannot find symbol: class Scanner*.
- Create the `Scanner` **once** and reuse it. Don't create one per read, and don't close it (see [[#10. One `Scanner` for the Whole Program|§ 10]]).
- `System.out.print` (no `ln`) keeps the cursor on the prompt line, so the user types next to the prompt.

### 2.2 Tokens and the Reading Methods

> [!note] Definitions
> - A **token** is a run of characters between **delimiters**. By default, the delimiter is any amount of whitespace: spaces, tabs, **and line breaks**.
> - **Token-based** methods (`next`, `nextInt`, `nextDouble`, …) skip any leading whitespace, read one token, and stop right after it.
> - The **line-based** method `nextLine` reads everything up to the end of the current line.

| Method | Reads | Returns | Bad input | No more input |
|---|---|---|---|---|
| `next()` | the next token | `String` | — | `NoSuchElementException` |
| `nextInt()` | the next token, as an `int` | `int` | `InputMismatchException` | `NoSuchElementException` |
| `nextLong()`, `nextShort()`, `nextByte()` | the same, other integer types | the primitive | `InputMismatchException` | `NoSuchElementException` |
| `nextDouble()`, `nextFloat()` | the next token, as a decimal | the primitive | `InputMismatchException` | `NoSuchElementException` |
| `nextBoolean()` | the next token, `true` or `false` | `boolean` | `InputMismatchException` | `NoSuchElementException` |
| `nextLine()` | the rest of the current line | `String`, without the line separator | — | `NoSuchElementException: No line found` |
| `hasNext()`, `hasNextInt()`, `hasNextDouble()`, `hasNextLine()`, … | **looks ahead** only | `boolean` | `false` | `false` |

<span class="hl-yellow">The `hasNextX` methods never consume anything.</span> Calling `hasNextInt()` ten times in a row gives the same answer ten times. Only the `next…` methods move forward.

Because line breaks count as whitespace, token-based reads don't care how the values are spread over lines:

```java
// input:  3⏎⏎    4      5⏎          (or "3 4 5" on one line: same result)
int a = sc.nextInt();   // 3
int b = sc.nextInt();   // 4: the blank line and the spaces are skipped
int c = sc.nextInt();   // 5
```

> [!warning] Common mistake: there is no `nextChar()`
> `sc.nextChar()` doesn't exist (*cannot find symbol*). Read a token and take its first character: `char c = sc.next().charAt(0);`. See [[#4.4 Reading a Single Character|§ 4.4]].

### 2.3 What Each `nextX` Accepts

The token must be a **complete** value of the requested type. Results in an English locale (for other locales see [[#8. Locale and Decimal Numbers|§ 8]]):

| Call | Input | Result | Why |
|---|---|---|---|
| `nextInt()` | `+5` / `-5` / `007` | `5` / `-5` / `7` | a sign and leading zeros are fine |
| `nextInt()` | `1,000` | `1000` | the locale's grouping separator is accepted |
| `nextInt()` | `5.0` | `InputMismatchException` | not an integer |
| `nextInt()` | `1_000` / `0x1F` | `InputMismatchException` | source-code syntax isn't input syntax |
| `nextInt()` | `99999999999` | `InputMismatchException` | out of `int` range. It's rejected, **not** wrapped around. Use `nextLong()`. |
| `nextInt(16)` | `ff` | `255` | an overload takes a radix (`nextInt(2)` reads binary) |
| `nextDouble()` | `5` | `5.0` | integers are valid decimals |
| `nextDouble()` | `.5` / `5.` / `1e3` | `0.5` / `5.0` / `1000.0` | |
| `nextDouble()` | `NaN` / `Infinity` | `NaN` / `Infinity` | |
| `nextDouble()` | `3.5f` | `InputMismatchException` | no type suffixes (unlike `parseDouble`, [[#4.2 What `parseInt` and `parseDouble` Accept|§ 4.2]]) |
| `nextBoolean()` | `true` / `TRUE` / `True` | `true` | case-insensitive |
| `nextBoolean()` | `yes` / `1` | `InputMismatchException` | only `true`/`false` |
| `next()` | `Grace Hopper` | `"Grace"` | one token: it stops at the space |

---

## 3. Token-Based vs. Line-Based Reading

### 3.1 How `nextLine` Works

`nextLine()` returns everything from the current position **up to the end of the line**, without the line separator, and then moves past the separator. So:

- If the current position is **right before** a line separator, it returns `""` immediately.
- A blank line gives `""`.
- The last line of the input is returned even if it has no line separator after it.
- Spaces are kept: a line `  hi  ` comes back as `"  hi  "`. Call `strip()` if you don't want them.

Windows' `\r\n` is handled for you: neither `\r` nor `\n` appears in the result.

### 3.2 The `nextInt` Then `nextLine` Trap

<span class="hl-yellow">The most common input bug in Java.</span>

```java
System.out.print("Age: ");
int age = sc.nextInt();
System.out.print("Name: ");
String name = sc.nextLine();
System.out.println(name + " is " + age);
```

```
Age: 25
Name:  is 25                    ← the program didn't wait for the name
```

The user typed `25⏎`. `nextInt()` reads `25` and **stops right before the `⏎`**, because token methods never read the separator after a token. `nextLine()` then finds a line separator straight away and returns the empty rest of that line, `""`. The name the user wanted to type hasn't even been asked for yet.

| Step | Input still unread | Returns |
|---|---|---|
| start | `25⏎Maria Papadopoulou⏎` | |
| `nextInt()` | `⏎Maria Papadopoulou⏎` | `25` |
| `nextLine()` | `Maria Papadopoulou⏎` | `""` (the rest of line 1) |
| another `nextLine()` | *(nothing)* | `"Maria Papadopoulou"` |

**Fixes:**

1. **Discard the rest of the line** after the number:
   ```java
   int age = sc.nextInt();
   sc.nextLine();                       // throw away the "⏎" left by nextInt
   String name = sc.nextLine();
   ```
2. **Read everything as lines** and parse the numbers yourself. This is the more robust option, because a leftover separator never exists:
   ```java
   int age = Integer.parseInt(sc.nextLine().strip());
   String name = sc.nextLine();
   ```

The trap only happens in one direction. `nextLine()` followed by `nextInt()` is fine. So is `nextInt()` followed by `next()`, because `next()` skips leading whitespace, including the leftover `⏎`.

> [!warning] Trick: the rest of the line isn't always empty
> The discard fix throws away **whatever** else is on the line, not only the `⏎`:
> - Input `42 Ada⏎`: after `nextInt()`, `nextLine()` returns `" Ada"` (with a leading space). The discarding `nextLine()` would silently throw away `Ada`.
> - Input `42   ⏎` (trailing spaces): `nextLine()` returns `"   "`, not `""`.

### 3.3 Mixing `next` and `nextLine`

```java
// input:  Maria Papadopoulou⏎
String first = sc.next();       // "Maria"
String rest  = sc.nextLine();   // " Papadopoulou": note the leading space
```

- `next()` reads **one word**, so it can't read a full name, an address, or a sentence. Use `nextLine()` for those.
- `nextLine()` after `next()` starts right after the token, so it includes the space that followed it.

> [!example]- Worked example: reading a count, then values, then a line of text
> ```java
> import java.util.Scanner;
>
> public class Grades {
>     public static void main(String[] args) {
>         Scanner sc = new Scanner(System.in);
>         System.out.print("How many grades? ");
>         int n = sc.nextInt();
>         double[] grades = new double[n];           // length known only at runtime
>         for (int i = 0; i < n; i++) {
>             System.out.print("Grade " + (i + 1) + ": ");
>             grades[i] = sc.nextDouble();
>         }
>         sc.nextLine();                             // discard the rest of the last number's line
>         System.out.print("Comment: ");
>         String comment = sc.nextLine();
>
>         double sum = 0;
>         for (double g : grades) sum += g;
>         System.out.printf("Average %.2f (%s)%n", sum / n, comment);
>     }
> }
> ```
> Input `3⏎7.5 8⏎9⏎Good work overall⏎` prints `Average 8.17 (Good work overall)`.
> - The numbers can be typed on one line or several: `7.5 8` on one line works, because tokens skip line breaks.
> - Without `sc.nextLine()` after the loop, `comment` would be `""`.
> - With a Greek locale, `7.5` would fail. See [[#8. Locale and Decimal Numbers|§ 8]].

---

## 4. Parsing Strings into Numbers

A number often arrives as a `String`: from `nextLine()`, from `BufferedReader.readLine()`, from `args`, or from a text field. A `String` can't be **cast** to a number (`(int) "5"` doesn't compile; see [[Java/01 - Foundations/04 - Type Casting#8. What Casting Cannot Do|Type Casting § 8]]). It has to be **parsed**.

```java
String s = "12";
System.out.println(s + 1);                     // 121: string concatenation
System.out.println(Integer.parseInt(s) + 1);   // 13
```

### 4.1 The `parseX` Methods

| Method | Returns | Example |
|---|---|---|
| `Integer.parseInt(s)` | `int` | `Integer.parseInt("42")` → `42` |
| `Long.parseLong(s)` | `long` | `Long.parseLong("9000000000")` → `9000000000L` |
| `Double.parseDouble(s)` | `double` | `Double.parseDouble("3.5")` → `3.5` |
| `Float.parseFloat(s)`, `Short.parseShort(s)`, `Byte.parseByte(s)` | the primitive | `Byte.parseByte("200")` → `NumberFormatException` (out of range) |
| `Boolean.parseBoolean(s)` | `boolean` | `true` only for `"true"` in any case; **everything else is `false`** |
| `Integer.parseInt(s, radix)` | `int` | `parseInt("1F", 16)` → `31`, `parseInt("-ff", 16)` → `-255`, `parseInt("101", 2)` → `5` |
| `Integer.decode(s)` | `Integer` | reads prefixes: `decode("0x1F")` → `31`, `decode("010")` → `8` (**octal**) |

When the text isn't a valid number, the numeric parsers throw <span class="hl-blue">`NumberFormatException`</span>. It is an **unchecked** exception, so the compiler won't remind you to handle it. Handling it is shown in [[#5.4 Line-Based Validation (Recommended)|§ 5.4]].

### 4.2 What `parseInt` and `parseDouble` Accept

<span class="hl-yellow">`parseInt` is strict about whitespace, and `parseDouble` isn't.</span> The two methods differ in several ways that look arbitrary:

| Input | `Integer.parseInt` | `Double.parseDouble` |
|---|---|---|
| `"42"` | `42` | `42.0` |
| `" 42"`, `"42 "`, `"42\n"` | ❌ `NumberFormatException` | ✅ `42.0`: surrounding whitespace is trimmed |
| `"+42"` / `"-0"` | `42` / `0` | `42.0` / `-0.0` |
| `"4.0"` | ❌ not an integer | `4.0` |
| `""` | ❌ | ❌ (`empty String`) |
| `null` | ❌ **`NumberFormatException`** | ❌ **`NullPointerException`** |
| `"1_000"`, `"1,000"` | ❌ | ❌ |
| `"0x1F"` | ❌ (use radix 16 or `decode`) | ❌ (`"0x1p3"` → `8.0`: hex floating-point syntax is accepted) |
| `"2147483648"` | ❌ out of `int` range | `2.147483648E9` |
| `"-2147483648"` | `-2147483648` (`Integer.MIN_VALUE`) | |
| `"3.5f"`, `"3.5d"` | ❌ | ✅ `3.5`: Java literal suffixes are accepted |
| `"5L"` (with `parseLong`) | ❌: `L` is **not** accepted | |
| `"1e3"` / `"1e400"` | ❌ | `1000.0` / `Infinity` (no exception on overflow) |
| `"NaN"` / `"Infinity"` / `"infinity"` | ❌ | `NaN` / `Infinity` / ❌ (case-sensitive) |
| `"3,5"` | ❌ | ❌: `parseDouble` **always** uses `.` and ignores the locale |

> [!tip] Always `strip()` before `parseInt`
> Users type stray spaces, and lines read with `nextLine`/`readLine` keep them. `Integer.parseInt(line.strip())` avoids a whole class of `NumberFormatException`s. (`trim()` works too. `strip()` also removes Unicode whitespace; see [[Java/03 - Program Structure/02 - Strings#3. Common String Methods|Strings § 3]].)

### 4.3 `parseX` vs. `valueOf`

| Method | Returns | Note |
|---|---|---|
| `Integer.parseInt("42")` | `int` (primitive) | use this for arithmetic |
| `Integer.valueOf("42")` | `Integer` (object) | same parsing rules and exceptions, then boxing |

`Integer.valueOf` returns cached objects for `-128 … 127`, so `Integer.valueOf("127") == Integer.valueOf("127")` is `true` but `Integer.valueOf("128") == Integer.valueOf("128")` is `false`. Compare with `equals`, or parse to `int`. See [[Java/01 - Foundations/04 - Type Casting#9. Autoboxing and Unboxing (Related, Not True Casting)|Type Casting § 9]].

### 4.4 Reading a Single Character

```java
char c = sc.next().charAt(0);        // first character of the next token
char d = sc.nextLine().charAt(0);    // first character of the line: throws StringIndexOutOfBoundsException on an empty line
```

Turning a digit character into its number value:

| Expression | Result | Why |
|---|---|---|
| `'7' - '0'` | `7` | digit codes are consecutive: `55 - 48` |
| `(int) '7'` | `55` | the character **code**, not the digit |
| `Character.getNumericValue('7')` | `7` | |
| `Character.getNumericValue('a')` | `10` | ⚠️ letters count as digits (as in base 36), so this doesn't validate a digit. Check `Character.isDigit(c)` first. |

---

## 5. Validating Input

User input is wrong all the time: letters where a number belongs, `4.5` where a whole number belongs, `200` for an age. Validation has two layers:

- **Format**: is it a number at all? (`hasNextInt`, or catch `NumberFormatException`.)
- **Range**: is the number allowed? (an ordinary `if`.)

A validation loop repeats until both layers pass.

### 5.1 Checking First with `hasNextInt`

```java
System.out.print("Age: ");
while (!sc.hasNextInt()) {
    System.out.print("Not a whole number: " + sc.next() + ". Age: ");   // sc.next() DISCARDS the bad token
}
int age = sc.nextInt();
```

```
Age: abc 4.5
Not a whole number: abc. Age: Not a whole number: 4.5. Age: twenty 21
Not a whole number: twenty. Age:
```

(`age` ends up `21`.)

- `hasNextInt()` only **looks**. Without the `sc.next()` inside the loop, the bad token would never be removed, and the loop would run forever.
- The loop works **per token**, not per line: `abc 4.5` is two bad tokens, so the user gets two error messages for one line.
- At end of input, `hasNextInt()` returns `false` and then `sc.next()` throws `NoSuchElementException`. Programs that may receive EOF should check `hasNext()` first.

### 5.2 Adding a Range Check

```java
int grade;
while (true) {
    System.out.print("Grade (0-10): ");
    if (sc.hasNextInt()) {
        grade = sc.nextInt();
        if (grade >= 0 && grade <= 10) {
            break;                                   // both checks passed
        }
        System.out.println("Out of range.");
    } else {
        System.out.println("Not a whole number: " + sc.next());
    }
}
```

> [!warning] Trick: every `nextInt()` call reads a new number
> ```java
> if (sc.nextInt() >= 0 && sc.nextInt() <= 10) { … }    // reads TWO numbers
> ```
> With input `5 20` this checks `5 >= 0` and then `20 <= 10`. Read the value **once** into a variable, then test the variable.

### 5.3 Retrying with `try` and `catch`

A `try` block runs code that might throw an exception. If it throws, control jumps to a matching `catch` block instead of crashing the program. The full rules are in [[Java/05 - Working with Data and Errors/01 - Exception Handling|Exception Handling]].

<span class="hl-red">This loop never ends</span> when the user types something that isn't a number:

```java
import java.util.InputMismatchException;   // also in java.util

int n;
while (true) {
    try {
        n = sc.nextInt();
        break;
    } catch (InputMismatchException e) {
        System.out.println("Not a number, try again");    // printed forever
    }
}
```

When `nextInt()` throws `InputMismatchException`, it **does not consume the bad token**. The next attempt sees the same `abc`, fails the same way, and the loop runs forever without waiting for new input. The fix is to consume the token in the `catch`:

```java
    } catch (InputMismatchException e) {
        System.out.println("Not a whole number: " + sc.next());   // sc.next() removes it
    }
```

### 5.4 Line-Based Validation (Recommended)

<span class="hl-yellow">Reading a whole line and then parsing it avoids every trap in §§ 3.2 and 5.1–5.3.</span> No separator is left behind, the user gets one message per line, and `42 abc` is rejected as a whole instead of half-accepted.

```java
static int readInt(Scanner sc, String prompt, int min, int max) {
    while (true) {
        System.out.print(prompt);
        String line = sc.nextLine().strip();
        try {
            int value = Integer.parseInt(line);
            if (value >= min && value <= max) {
                return value;
            }
            System.out.println("Please enter a number from " + min + " to " + max + ".");
        } catch (NumberFormatException e) {
            System.out.println("\"" + line + "\" is not a whole number.");
        }
    }
}

int age = readInt(sc, "Age: ", 0, 120);
```

```
Age:  200
Please enter a number from 0 to 120.
Age: abc
"abc" is not a whole number.
Age:
"" is not a whole number.
Age:  35
```

- An empty line (just Enter) is handled: `parseInt("")` throws, and the loop asks again.
- `sc.nextLine()` throws `NoSuchElementException` at end of input. If the input may end (for example, when input is redirected from a file), check `sc.hasNextLine()` first and decide what the program should do.
- The same pattern works for any format: `Double.parseDouble`, a `yes`/`no` check, a date, and so on.

---

## 6. Comparing Input Strings

Input strings are created at runtime, so they are never the same **object** as a literal. `==` compares objects, so it's the wrong test (see [[Java/03 - Program Structure/02 - Strings#2. Creating Strings — Literals vs. `new`|Strings § 2]]):

```java
String answer = sc.next();                // user types: yes
System.out.println(answer == "yes");      // false, always
System.out.println(answer.equals("yes")); // true
```

| Goal | Code |
|---|---|
| exact match | `answer.equals("yes")` |
| ignore case (`Yes`, `YES`) | `answer.equalsIgnoreCase("yes")` |
| ignore surrounding spaces | `answer.strip().equalsIgnoreCase("yes")` |
| safe when `answer` may be `null` (e.g. `readLine()` at EOF) | `"yes".equals(answer)` |
| several options | `switch (answer) { case "yes": … }` (compares with `equals`, but a `null` `answer` throws `NullPointerException`) |

Comparing a single `char` with `==` is fine, because `char` is a primitive: `sc.next().charAt(0) == 'y'`.

---

## 7. Reading Until the End of Input

### 7.1 What End of Input Means

| Source | How the input ends |
|---|---|
| keyboard, Linux / macOS | **Ctrl+D** at the start of a line |
| keyboard, Windows (cmd, PowerShell) | **Ctrl+Z**, then Enter, on a line of its own |
| IDE console | varies (IntelliJ: Ctrl+D). Some consoles have no EOF key, so test with a file instead. |
| a file: `java SumAll < numbers.txt` (cmd, bash) | the end of the file |
| a pipe: `echo 1 2 3 \| java SumAll` | when the other program finishes |

> [!warning] PowerShell has no `<` redirection
> In PowerShell, `java SumAll < numbers.txt` is an error (*the '<' operator is reserved for future use*). Pipe the file in instead: `Get-Content numbers.txt | java SumAll`.

Once the input has ended:
- every `hasNextX()` returns `false`,
- every `nextX()` and `nextLine()` throws `NoSuchElementException`,
- `BufferedReader.readLine()` returns `null` (see [[#9. `BufferedReader`|§ 9]]).

### 7.2 Loops That Read Until the End

```java
Scanner sc = new Scanner(System.in);
long sum = 0;
int count = 0;
while (sc.hasNextInt()) {
    sum += sc.nextInt();
    count++;
}
System.out.println(count + " numbers, sum = " + sum);
```

| Input | Output | Why |
|---|---|---|
| `1 2 3⏎4⏎5 6⏎` then EOF | `6 numbers, sum = 21` | line breaks don't matter |
| `1 2 x 3` | `2 numbers, sum = 3` | ⚠️ the loop stops at the **first** non-integer, and `3` is never read |
| nothing | `0 numbers, sum = 0` | |

> [!warning] Trick: pressing Enter doesn't end the loop
> At the keyboard, the loop above **doesn't** stop after the user presses Enter. Enter is only whitespace, so `hasNextInt()` waits for more. The program looks frozen. It stops only at EOF (Ctrl+D / Ctrl+Z) or at a token that isn't an integer.

To skip bad tokens instead of stopping at them:

```java
while (sc.hasNext()) {
    if (sc.hasNextInt()) {
        sum += sc.nextInt();
    } else {
        sc.next();                 // skip "x"
    }
}
// "1 2 x 3" → sum = 6
```

Line by line:

```java
while (sc.hasNextLine()) {
    String line = sc.nextLine();
    // process one line
}
```

### 7.3 Sentinel Values

A **sentinel** is a special input that means "stop". It suits interactive programs where the user wouldn't know about Ctrl+D:

```java
int n;
long sum = 0;
while ((n = sc.nextInt()) != 0) {     // 0 means "stop"
    sum += n;
}
// input "5 7 0 9" → sum = 12, and 9 is never read
```

- The sentinel must be a value that can never be real data. `0` is a bad sentinel for temperatures, and `-1` is a bad one for bank balances.
- Other common sentinels: a word (`quit`; see the `do-while` example in [[Java/02 - Control Flow/02 - Loops#2. The `do-while` Loop|Loops § 2]]) or an empty line: `while (!(line = sc.nextLine()).isEmpty())`.

---

## 8. Locale and Decimal Numbers

<span class="hl-yellow">`Scanner` reads numbers using the computer's regional settings (its **locale**).</span> In Greek (as in many European languages) the decimal separator is `,` and the thousands separator is `.`. On a computer set to Greek (`el_GR`), `nextDouble()` behaves like this:

| Input | Greek locale (`el_GR`) | English locale (`en_US`) |
|---|---|---|
| `3.5` | ❌ `InputMismatchException` | `3.5` |
| `3,5` | `3.5` | ❌ `InputMismatchException` |
| `3.500` | ⚠️ `3500.0`: the `.` is read as a thousands separator | `3.5` |
| `5` | `5.0` | `5.0` |
| `nextInt()` on `1.000` | `1000` | ❌ |
| `nextInt()` on `1,000` | ❌ | `1000` |

So the same program, with the same input, works on one computer and crashes on another. Worse, `3.500` is quietly read as `3500.0`.

**Fix:** set the locale explicitly when creating the `Scanner`:

```java
import java.util.Locale;
import java.util.Scanner;

Scanner sc = new Scanner(System.in).useLocale(Locale.US);   // always "." for decimals
```

(`Locale.ROOT` works too.) To see which locale a `Scanner` uses, print `sc.locale()`. To test a program under the Greek locale on any computer, run it with `java -Duser.language=el -Duser.country=GR App`.

What depends on the locale and what doesn't:

| Operation | Locale-dependent? |
|---|---|
| `sc.nextDouble()`, `sc.nextInt()`, `sc.hasNextDouble()` | **yes** |
| `Double.parseDouble(s)`, `Integer.parseInt(s)` | no: always `.`, no grouping |
| `System.out.printf("%.2f", 3.5)`, `String.format` | **yes**: prints `3,50` in Greek. Use `printf(Locale.US, …)` (see [[Java/03 - Program Structure/02 - Strings#6. Formatted Output — `printf` and `String.format`|Strings § 6]]) |
| `System.out.println(3.5)`, `"" + 3.5`, `String.valueOf(3.5)` | no: always `3.5` |

> [!tip] Line-based reading sidesteps the locale
> `Double.parseDouble(sc.nextLine().strip())` always expects `3.5`, whatever the computer's settings. This is another reason to prefer the pattern in [[#5.4 Line-Based Validation (Recommended)|§ 5.4]]. If users should be able to type `3,5`, decide that on purpose (for example `s.replace(',', '.')`) instead of leaving it to the locale.

---

## 9. `BufferedReader`

`BufferedReader` reads **whole lines** and nothing else. It doesn't parse numbers or split tokens. In exchange it is much faster than `Scanner` and has no locale behaviour.

### 9.1 Reading Lines and Parsing Them

```java
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Sum {
    public static void main(String[] args) throws IOException {
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(in.readLine().strip());      // first line: a number
        String line;
        while ((line = in.readLine()) != null) {             // until end of input
            System.out.println("[" + line + "]");
        }
    }
}
```

- **The layers**: `System.in` delivers bytes, `InputStreamReader` decodes them into characters, and `BufferedReader` groups the characters into lines.
- `readLine()` returns the line **without** its separator, or **`null` at end of input**. It doesn't throw at EOF. Calling it again after EOF keeps returning `null`.
- `readLine()` declares **`IOException`**, which is a *checked* exception. The compiler forces you to deal with it, either with `throws IOException` on the method (as above) or with `try`/`catch`. Without either:
  ```
  error: unreported exception IOException; must be caught or declared to be thrown
  ```
- At EOF, `in.readLine().strip()` throws `NullPointerException`, because you can't call a method on `null`.

> [!warning] Trick: two `readLine()` calls per iteration
> ```java
> while (in.readLine() != null) {             // reads line 1 and throws it away
>     System.out.println(in.readLine());      // reads line 2
> }
> ```
> Every call reads a **new** line. With input `a⏎b⏎c⏎`, this prints `b` and then `null`. Store the line once: `while ((line = in.readLine()) != null)`.

### 9.2 Splitting a Line into Tokens

With `BufferedReader`, you split lines into numbers yourself:

```java
String[] parts = line.strip().split("\\s+");      // "\\s+" = one or more whitespace characters
int[] nums = new int[parts.length];
for (int i = 0; i < parts.length; i++) {
    nums[i] = Integer.parseInt(parts[i]);
}
```

| Code | Result | Why |
|---|---|---|
| `" 1 2".split("\\s+")` | `["", "1", "2"]` | ⚠️ leading whitespace produces an empty first element, so `parseInt("")` throws |
| `" 1 2".strip().split("\\s+")` | `["1", "2"]` | strip first |
| `"1 2 ".split("\\s+")` | `["1", "2"]` | trailing empty strings are removed |
| `"1  2".split(" ")` | `["1", "", "2"]` | split on **one** space: double spaces give empty tokens |
| `"".split("\\s+")` | `[""]` (length **1**, not 0) | an empty line is one empty token |

`java.util.StringTokenizer` is an older alternative that never produces empty tokens and is a little faster than `split`:

```java
StringTokenizer st = new StringTokenizer(line);       // "  10 20   30 " → 10, 20, 30
while (st.hasMoreTokens()) {
    sum += Integer.parseInt(st.nextToken());
}
```

### 9.3 `Scanner` vs. `BufferedReader`

| | `Scanner` | `BufferedReader` |
|---|---|---|
| Package | `java.util` | `java.io` |
| Reads | tokens, numbers, lines | lines only |
| Parsing | built in (`nextInt`, …) | manual (`parseInt`, `split`) |
| End of input | `hasNextX()` false, `nextX()` throws `NoSuchElementException` | `readLine()` returns `null` |
| Exceptions | unchecked (`InputMismatchException`, `NoSuchElementException`) | checked `IOException` must be handled |
| Locale | `nextDouble`/`nextInt` depend on it | none (`parseDouble` always uses `.`) |
| Speed | slow (regular-expression based) | fast. Summing 1,000,000 integers: about 280 ms vs. about 55 ms with `StringTokenizer` (JDK 17, measured for this note) |
| Best for | interactive programs, coursework, small inputs | large inputs (online judges, competitive programming), line-oriented data |

Don't use both on `System.in` in one program. Each one buffers input ahead, so one steals input from the other (see [[#10.2 Two `Scanner`s Steal Each Other's Input|§ 10.2]]).

### 9.4 Other Ways to Read

- **`Scanner` on a `String`**: `new Scanner("3 4 5")` reads from the text instead of the keyboard. This is handy for trying out code and in tests.
- **`Scanner` / `BufferedReader` on a file**: see [[Java/07 - Input and Output/01 - File I-O|File I/O]].
- **`System.console()`** gives `readLine(prompt)` and `readPassword()` (which doesn't echo the typed characters and returns a `char[]`). In Java 17 it returns **`null`** when input is redirected and in many IDE consoles, so always check for `null`. Newer versions (Java 22+) changed when it's `null`.
- **`System.in.read()`** reads a single **byte** as an `int`, or `-1` at EOF. Typing `a⏎` in the Windows console gives `97`, `13`, `10`: the `\r\n` is there too. This is rarely what you want.

> [!tip] Greek letters from the keyboard
> Non-ASCII input (for example Greek) typed in the Windows console can come out garbled when the console's code page and Java's charset don't match. The fix depends on the setup (e.g. `chcp 65001` in cmd). Charsets are covered properly in [[Java/07 - Input and Output/01 - File I-O|File I/O]].

---

## 10. One `Scanner` for the Whole Program

### 10.1 Don't Close a `Scanner` on `System.in`

`sc.close()` closes the stream underneath the `Scanner`. For `new Scanner(System.in)` that stream is **`System.in` itself**, and a closed `System.in` can't be reopened:

```java
static int readAge() {
    Scanner sc = new Scanner(System.in);
    int age = sc.nextInt();
    sc.close();                  // closes System.in for the rest of the program
    return age;
}

readAge();                       // works
readAge();                       // NoSuchElementException: the new Scanner reads a closed stream
System.in.read();                // IOException: Stream closed
```

`try (Scanner sc = new Scanner(System.in)) { … }` closes it too, at the end of the block. So do not put a `System.in` `Scanner` in try-with-resources unless the block is the whole program.

IDEs often warn *"Resource leak: 'sc' is never closed"*. For a `Scanner` on `System.in`, it's safe to ignore the warning, or to close the `Scanner` once as the very last statement of `main`. Scanners on **files** should be closed (see [[Java/07 - Input and Output/01 - File I-O|File I/O]]).

### 10.2 Two `Scanner`s Steal Each Other's Input

```java
static int readInt() {
    return new Scanner(System.in).nextInt();     // a new Scanner on every call
}

int x = readInt();
int y = readInt();
```

With the input piped in (`printf '3\n4\n' | java App`), the second call throws `NoSuchElementException`, **even though nothing was closed**. A `Scanner` doesn't read one character at a time. It reads a **block** of input (up to about 1,000 characters) into its own private buffer. The first `Scanner` swallowed both `3` and `4`, used the `3`, and was thrown away with the `4` still in its buffer. The second `Scanner` finds `System.in` empty.

> [!warning] Trick: it seems to work at the keyboard
> When a person types one number per line, the terminal delivers only one line at a time, so each `Scanner` happens to get its own line and the bug stays hidden. It shows up when the user types `3 4` on one line, and every time the input is redirected, which is how automated graders run programs.

### 10.3 Sharing One `Scanner`

Create the `Scanner` once, and give every method access to it. There are two common ways:

```java
public class App {
    private static final Scanner IN = new Scanner(System.in);   // (1) one static field

    static int readInt(String prompt) {
        System.out.print(prompt);
        return IN.nextInt();
    }

    static String readName(Scanner sc) {                          // (2) pass it as a parameter
        return sc.nextLine();
    }

    public static void main(String[] args) {
        int x = readInt("x: ");
        int y = readInt("y: ");
        System.out.println(x + y);           // input "3 4" → 7
    }
}
```

`static` fields are covered in [[Java/04 - Object-Oriented Programming/01 - Classes and Objects|Classes and Objects]].

---

## 11. Common Pitfalls

- **`nextInt()` (or `nextDouble()`, `next()`) followed by `nextLine()`** returns `""`, the leftover end of the number's line. Discard it with an extra `nextLine()`, or read everything with `nextLine()` and parse.
- **Using `next()` for a name or sentence.** It reads one word only.
- **Retrying `nextInt()` in a `try`/`catch` without consuming the bad token.** `InputMismatchException` leaves the token in place, so the loop spins forever. Call `sc.next()` in the `catch`.
- **A `hasNextInt()` loop that never calls `next()` on bad input**: the same infinite loop.
- **Calling `nextInt()` twice in one condition** (`sc.nextInt() > 0 && sc.nextInt() < 10`) reads two numbers.
- **`nextDouble()` on a Greek-locale computer** rejects `3.5` and reads `3.500` as `3500.0`. Use `useLocale(Locale.US)`.
- **`Integer.parseInt` with spaces around the number** (`" 42"`, `"42 "`) throws `NumberFormatException`. Call `strip()` first. (`Double.parseDouble` trims by itself, which hides the inconsistency.)
- **`Integer.parseInt("4.0")`** throws. A whole number with a decimal point is not an `int`.
- **Expecting `Boolean.parseBoolean("yes")` to fail.** It returns `false` for anything except `true`, and never throws.
- **Closing a `Scanner` on `System.in`**, directly or with try-with-resources. Every later read fails.
- **Creating a new `Scanner(System.in)` in each method.** Input disappears into the old `Scanner`'s buffer. Share one `Scanner`.
- **Comparing input with `==`.** It's always `false`. Use `equals` / `equalsIgnoreCase`.
- **`readLine()` without handling `IOException`** is a compile error. `readLine()` returning `null` at EOF causes `NullPointerException` if you call a method on it.
- **Calling `readLine()` twice per loop iteration** skips every other line.
- **`line.split("\\s+")` on a line with leading spaces** produces an empty first token, and `parseInt("")` throws. Call `strip()` first.
- **A `while (sc.hasNextInt())` loop at the keyboard** doesn't end on Enter. It ends on EOF (Ctrl+D / Ctrl+Z) or on a non-number.
- **`(int) '7'` to get the digit** gives `55`. Use `'7' - '0'`.

---

## 12. Quick Reference — Non-Obvious Outcomes

| Code | Result | Why |
|---|---|---|
| `nextInt()` then `nextLine()`, input `25⏎Ada⏎` | `nextLine()` → `""` | the `⏎` after `25` is still unread |
| `nextInt()` then `nextLine()`, input `42 Ada⏎` | `" Ada"` | the rest of the line, with its leading space |
| `next()` then `nextLine()`, input `Maria Papadopoulou⏎` | `"Maria"`, `" Papadopoulou"` | `next()` reads one word |
| `nextLine()` then `nextInt()` | works | the trap goes one way only |
| `nextInt()` × 3, input `3⏎⏎  4  5` | `3`, `4`, `5` | line breaks are whitespace |
| `sc.nextChar()` | compile error | no such method: use `next().charAt(0)` |
| `int n = sc.nextLine();` | compile error | `String` can't be converted to `int` |
| `nextInt()` on `5.0` | `InputMismatchException` | not an integer |
| `nextInt()` on `99999999999` | `InputMismatchException` | out of range, not wrapped |
| `nextInt()` on `1,000` (English locale) | `1000` | grouping separator accepted |
| `nextDouble()` on `3.5` (Greek locale) | `InputMismatchException` | decimal separator is `,` |
| `nextDouble()` on `3.500` (Greek locale) | `3500.0` | `.` is the thousands separator |
| `nextDouble()` on `3.5f` | `InputMismatchException` | no suffixes in input |
| `nextBoolean()` on `TRUE` | `true` | case-insensitive |
| `nextInt()` throws, then `nextInt()` again | throws again, forever | the bad token is not consumed |
| `hasNextInt()` twice on `abc` | `false`, `false` | looking doesn't consume |
| `nextLine()` / `nextInt()` at EOF | `NoSuchElementException` | no more input |
| `readLine()` at EOF | `null` | no exception |
| `Integer.parseInt(" 42")` | `NumberFormatException` | no trimming |
| `Double.parseDouble(" 4.2 ")` | `4.2` | trims whitespace |
| `Integer.parseInt("4.0")` | `NumberFormatException` | not an integer |
| `Integer.parseInt("+42")` | `42` | a leading `+` is allowed |
| `Integer.parseInt("")` | `NumberFormatException` | empty |
| `Integer.parseInt(null)` | `NumberFormatException` | but … |
| `Double.parseDouble(null)` | `NullPointerException` | … inconsistent with `parseInt` |
| `Integer.parseInt("2147483648")` | `NumberFormatException` | out of `int` range |
| `Double.parseDouble("3.5f")` | `3.5` | Java suffixes accepted |
| `Long.parseLong("5L")` | `NumberFormatException` | the `L` suffix is not |
| `Double.parseDouble("1e400")` | `Infinity` | no overflow exception |
| `Double.parseDouble("3,5")` | `NumberFormatException` | always `.`, whatever the locale |
| `Integer.decode("010")` | `8` | leading `0` = octal |
| `Boolean.parseBoolean("yes")` | `false` | never throws |
| `"12" + 1` | `"121"` | concatenation, not addition |
| `(int) '7'` / `'7' - '0'` | `55` / `7` | code vs. digit value |
| `Character.getNumericValue('a')` | `10` | letters count as digits |
| `sc.next() == "yes"` | `false` | different objects |
| `" 1 2".split("\\s+")` | `["", "1", "2"]` | leading empty token |
| `"".split("\\s+").length` | `1` | one empty token |
| `while (in.readLine() != null) print(in.readLine())` | every other line, then `null` | two reads per iteration |
| `sc.close()` on `System.in`, then a new `Scanner(System.in)` | `NoSuchElementException` | `System.in` is closed for good |
| two `Scanner(System.in)`, piped input | the second finds nothing | the first buffered it all |
| `readLine()` without `throws IOException` | compile error | checked exception |
| `printf("%.2f", 3.5)` (Greek locale) | `3,50` | `printf` is locale-dependent |

---

## 13. Practice — Trick Questions

**Q1.** The user types `25⏎` and then wants to type `Maria Papadopoulou⏎`. What is printed, and how would you fix it?

```java
System.out.print("Age: ");
int age = sc.nextInt();
System.out.print("Name: ");
String name = sc.nextLine();
System.out.println(name + " is " + age);
```

> [!success]- Answer
> ```
> Age: 25
> Name:  is 25
> ```
> The program doesn't wait for the name. `nextInt()` stops before the `⏎`, so `nextLine()` returns the empty rest of that line. Fix: add `sc.nextLine();` after `nextInt()`, or read the age as `Integer.parseInt(sc.nextLine().strip())`.

**Q2.** Input: `42 Ada⏎Bob⏎`. What do `n`, `rest`, and `next` hold?

```java
int n = sc.nextInt();
String rest = sc.nextLine();
String next = sc.nextLine();
```

> [!success]- Answer
> | Variable | Value | Why |
> |---|---|---|
> | `n` | `42` | first token |
> | `rest` | `" Ada"` | the rest of line 1, **including** the space |
> | `next` | `"Bob"` | line 2 |
>
> So the "add a `nextLine()` to discard" fix would throw away `Ada`.

**Q3.** The user types `abc⏎`. What happens? Fix it.

```java
int n;
while (true) {
    try {
        n = sc.nextInt();
        break;
    } catch (InputMismatchException e) {
        System.out.println("Try again");
    }
}
```

> [!success]- Answer
> `Try again` is printed forever, and the program never waits for new input. `nextInt()` throws **without consuming** `abc`, so every retry sees the same token. Fix: consume it in the `catch`, with `sc.next();` (discards the token) or `sc.nextLine();` (discards the whole line). Better still, read lines and parse them as in [[#5.4 Line-Based Validation (Recommended)|§ 5.4]].

**Q4.** On a computer with a Greek locale, what does `sc.nextDouble()` return for each input? What about in an English locale?

`3.5` · `3,5` · `3.500` · `7`

> [!success]- Answer
> | Input | Greek (`el_GR`) | English (`en_US`) |
> |---|---|---|
> | `3.5` | `InputMismatchException` | `3.5` |
> | `3,5` | `3.5` | `InputMismatchException` |
> | `3.500` | `3500.0` (`.` groups thousands) | `3.5` |
> | `7` | `7.0` | `7.0` |
>
> The `3.500` case is the dangerous one: no error, just a wrong value. Use `new Scanner(System.in).useLocale(Locale.US)`, or read the line and use `Double.parseDouble`, which always expects `.`.

**Q5.** Which of these throw, and which exception?

```java
Integer.parseInt(" 42")        // (1)
Integer.parseInt("+42")        // (2)
Integer.parseInt("4.0")        // (3)
Double.parseDouble(" 4.0 ")    // (4)
Double.parseDouble("4")        // (5)
Integer.parseInt(null)         // (6)
Double.parseDouble(null)       // (7)
Boolean.parseBoolean("yes")    // (8)
Integer.parseInt("2147483648") // (9)
Double.parseDouble("3.5f")     // (10)
```

> [!success]- Answer
> | # | Result |
> |---|---|
> | (1) | `NumberFormatException`: `parseInt` doesn't trim |
> | (2) | `42` |
> | (3) | `NumberFormatException`: not an integer |
> | (4) | `4.0`: `parseDouble` trims |
> | (5) | `4.0` |
> | (6) | `NumberFormatException` |
> | (7) | `NullPointerException` (not `NumberFormatException`) |
> | (8) | `false`: no exception, ever |
> | (9) | `NumberFormatException`: one more than `Integer.MAX_VALUE` |
> | (10) | `3.5`: the `f` suffix is accepted |

**Q6.** Two versions of a helper. The program calls `readInt()` twice and is run with `printf '3\n4\n' | java App`. What happens in each version?

```java
// Version A
static int readInt() {
    Scanner sc = new Scanner(System.in);
    int v = sc.nextInt();
    sc.close();
    return v;
}

// Version B
static int readInt() {
    return new Scanner(System.in).nextInt();
}
```

> [!success]- Answer
> **Both** throw `NoSuchElementException` on the second call, for different reasons:
> - **A**: `close()` closed `System.in` itself, so the second `Scanner` reads from a closed stream.
> - **B**: nothing is closed, but the first `Scanner` read `3⏎4⏎` into its buffer in one go. The `4` was lost with it, and the second `Scanner` finds the stream empty.
>
> Typing one number per line at the keyboard makes **B** seem to work, because each line arrives separately. Fix both by using a single shared `Scanner` that is never closed ([[#10.3 Sharing One `Scanner`|§ 10.3]]).

**Q7.** The user enters `5 20`. What does this print, and what was intended?

```java
if (sc.nextInt() >= 0 && sc.nextInt() <= 10) {
    System.out.println("valid");
} else {
    System.out.println("invalid");
}
```

> [!success]- Answer
> `invalid`. The condition reads **two** numbers: `5 >= 0` is `true`, then `20 <= 10` is `false`. The intent was to range-check one number. Read it once: `int g = sc.nextInt(); if (g >= 0 && g <= 10) …`. If the user had typed only `5` and pressed Enter, the program would sit waiting for a second number.

**Q8.** What is printed for input `1 2 x 3`? And what happens if a person runs the program, types `1 2 3`, and presses Enter?

```java
long sum = 0;
while (sc.hasNextInt()) {
    sum += sc.nextInt();
}
System.out.println(sum);
```

> [!success]- Answer
> - `1 2 x 3` → `3`. The loop stops at `x`, the first token that isn't an integer, so the `3` after it is never read.
> - Typing `1 2 3⏎` prints **nothing yet**. Enter is just whitespace, and `hasNextInt()` waits for the next token. The loop ends only on EOF (Ctrl+D on Linux/macOS, Ctrl+Z then Enter on Windows), after which it prints `6`.

**Q9.** The user types `yes`. Why is `Cancelled` printed?

```java
String answer = sc.next();
if (answer == "yes") {
    System.out.println("Confirmed");
} else {
    System.out.println("Cancelled");
}
```

> [!success]- Answer
> `==` compares **objects**. The string read from the input is a new object, never the pooled literal `"yes"`, so the comparison is always `false`. Use `answer.equals("yes")`, or `answer.equalsIgnoreCase("yes")` to also accept `YES`/`Yes`.

**Q10.** Input: `a⏎b⏎c⏎`. What is printed?

```java
BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
while (in.readLine() != null) {
    System.out.println(in.readLine());
}
```

> [!success]- Answer
> ```
> b
> null
> ```
> Each `readLine()` reads a new line. Iteration 1: the condition reads `a`, the body prints `b`. Iteration 2: the condition reads `c`, the body reads EOF and prints `null`. Iteration 3: the condition gets `null` and the loop ends. Fix: `String line; while ((line = in.readLine()) != null) System.out.println(line);`.

**Q11.** A line of input is `  10 20 30`, with two leading spaces. What goes wrong, and what are two fixes?

```java
String[] parts = in.readLine().split("\\s+");
int sum = 0;
for (String p : parts) {
    sum += Integer.parseInt(p);
}
```

> [!success]- Answer
> `split("\\s+")` on a string that **starts** with whitespace gives an empty first element: `["", "10", "20", "30"]`. Then `Integer.parseInt("")` throws `NumberFormatException`. Fixes: `in.readLine().strip().split("\\s+")`, or use `new StringTokenizer(line)`, which never produces empty tokens. (A completely empty line is still a problem after `strip()`: `"".split("\\s+")` is `[""]`, with length 1.)

**Q12.** Which of these compile?

```java
char c = sc.nextChar();                                            // (1)
int n = sc.nextLine();                                             // (2)
int m = Integer.parseInt(sc.nextLine());                           // (3)
String s = new BufferedReader(new InputStreamReader(System.in)).readLine();   // (4) inside a main without "throws"
int k = (int) sc.next();                                           // (5)
```

> [!success]- Answer
> | # | Compiles? | Why |
> |---|---|---|
> | (1) | ❌ | `Scanner` has no `nextChar()` |
> | (2) | ❌ | `String` can't be converted to `int` |
> | (3) | ✅ | (it may still throw `NumberFormatException` at runtime) |
> | (4) | ❌ | unreported checked `IOException` |
> | (5) | ❌ | a `String` can't be cast to `int`; parse it instead |

---

## 14. Summary

- `System.in` delivers **bytes**. Wrap it in a `Scanner` (tokens and numbers) or a `BufferedReader` (lines). Keyboard input arrives a line at a time, **including the line separator**, and reads block until input is available.
- **Token methods** (`next`, `nextInt`, `nextDouble`, …) skip whitespace, including line breaks, and stop right after the token. **`nextLine()`** returns the rest of the current line. So `nextInt()` followed by `nextLine()` returns `""`. Discard the leftover line, or read everything with `nextLine()` and parse it.
- `hasNextX()` only looks ahead. `nextX()` on bad input throws `InputMismatchException` **and leaves the token in place**, so any retry loop must consume it with `next()`.
- **Parse** strings with `Integer.parseInt` / `Double.parseDouble`. Failures throw the unchecked `NumberFormatException`. `parseInt` doesn't trim spaces, but `parseDouble` does. `parseInt(null)` and `parseDouble(null)` throw different exceptions, and `parseBoolean` never throws.
- The most robust validation pattern is: read a line, `strip()` it, parse it in a `try`/`catch`, check the range, and repeat until it's valid.
- `nextDouble()`/`nextInt()` follow the computer's **locale**. On a Greek computer `3.5` fails and `3.500` becomes `3500.0`. Use `useLocale(Locale.US)`, or `parseDouble`, which always expects `.`.
- At **end of input**, `hasNextX()` is `false`, `nextX()`/`nextLine()` throw `NoSuchElementException`, and `readLine()` returns `null`. The user signals EOF with Ctrl+D (Linux/macOS) or Ctrl+Z then Enter (Windows).
- `BufferedReader` is several times faster but reads only lines, requires handling the checked `IOException`, and leaves splitting and parsing to you. Watch out for `split` producing empty tokens.
- Use **one** `Scanner` on `System.in` for the whole program, and **never close it**. Closing it closes `System.in` for good, and a second `Scanner` loses input that the first one had already buffered.
- Compare input strings with `equals`/`equalsIgnoreCase`, never `==`.

## Related

- [[Java/00 - Syllabus|Syllabus]]
- Previous: [[Java/01 - Foundations/04 - Type Casting|Type Casting]] · Next: [[Java/02 - Control Flow/01 - Conditional Statements|Conditional Statements]]
- [[Java/01 - Foundations/01 - Introduction to Java#5.3 Command-Line Arguments|Introduction to Java § 5.3]]: command-line arguments, the other way to give a program input
- [[Java/01 - Foundations/04 - Type Casting#8. What Casting Cannot Do|Type Casting § 8]]: why a `String` must be parsed, not cast
- [[Java/01 - Foundations/04 - Type Casting#9. Autoboxing and Unboxing (Related, Not True Casting)|Type Casting § 9]]: `Integer.valueOf` and `==` on wrappers
- [[Java/03 - Program Structure/02 - Strings|Strings]]: `equals`, `strip`, `split`, and locale-dependent `printf`
- [[Java/02 - Control Flow/02 - Loops|Loops]]: the `while` and `do-while` loops used for validation
- [[Java/02 - Control Flow/03 - Arrays#3.1 With `new` and a Length|Arrays § 3.1]]: creating an array whose length is read from input
- [[Java/05 - Working with Data and Errors/01 - Exception Handling|Exception Handling]]: `try`/`catch`, checked vs. unchecked exceptions (`IOException` vs. `NumberFormatException`)
- [[Java/07 - Input and Output/01 - File I-O|File I/O]]: `Scanner` and `BufferedReader` on files, charsets, closing resources
