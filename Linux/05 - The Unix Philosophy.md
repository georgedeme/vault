---
tags:
  - linux
---
# 05 - The Unix Philosophy

This note covers the design ideas Linux inherited from Unix: small tools that do one job, connected with pipes, all speaking plain text. It also explains why these ideas make the command line the centre of Linux rather than an optional extra.

## The Core Ideas

> [!important] The classic summary (Doug McIlroy, inventor of Unix pipes)
> *"Write programs that do one thing and do it well. Write programs to work together. Write programs to handle text streams, because that is a universal interface."*

| Principle | What it means in practice |
|---|---|
| **Do one thing well** | `sort` only sorts, `uniq` only removes adjacent duplicates, `wc` only counts. None of them tries to do the others' jobs |
| **Compose small tools** | Complex tasks come from chaining simple tools with [[#Pipes\|pipes]], not from one giant program with every feature |
| **Text is the universal interface** | Tools read and write lines of text, so *any* tool can feed *any* other, even tools written decades apart |
| **Everything is a file** | Devices, kernel info and processes are accessed through the file interface (see [[#Everything Is a File]]) |
| **Silence is golden** | A successful command prints nothing: `cp a b` just returns. Output means information or an error |
| **Configuration as text** | Settings live in human-readable files in `/etc` and `~/.config`, editable with any editor and trackable with Git |
| **Mechanism, not policy** | Provide flexible building blocks and let users decide how to combine them |
| **Prototype early, automate** | Try something interactively, then save the same commands as a script |

## Standard Streams

Every process starts with three open channels, identified by **file descriptor** numbers:

| FD | Name | Default | Used for |
|---|---|---|---|
| `0` | **stdin** (standard input) | Keyboard | Data coming in |
| `1` | **stdout** (standard output) | Terminal | Normal results |
| `2` | **stderr** (standard error) | Terminal | Errors and diagnostics |

stdout and stderr both show up on your screen, but they're **separate streams**. That's what lets you save the results and still see the errors, or throw away the errors and keep the results.

## Pipes

> [!note] Definition
> A **pipe** `|` connects the **stdout** of one command to the **stdin** of the next. The commands run **at the same time**, with data flowing through as it's produced; nothing is written to disk in between.

```bash
ls -l /etc | less                     # page through long output
ps aux | grep nginx                   # filter a process list
history | grep ssh                    # find that ssh command from last week
cat /var/log/auth.log | grep "Failed" | wc -l   # count failed logins
du -sh -- * | sort -h | tail -n 5     # the 5 biggest items in this directory
```

> [!warning] Pipes carry stdout only
> Errors (stderr) **bypass** the pipe and go straight to the screen. `find / -name x | less` still floods the terminal with `Permission denied` lines. Either discard them (`2>/dev/null`) or send them into the pipe too (`2>&1 |`, or `|&` in bash).

> [!info]- Deeper: each pipeline stage runs in its own subshell
> In bash, every part of a pipeline runs in a separate child process. So `echo "hello" | read word; echo "$word"` prints an **empty line**: `read` set `word` inside a subshell that has already exited. Likewise, `cd` inside a pipeline has no effect on your shell. Use redirection or command substitution instead: `read word <<< "hello"` or `word=$(echo hello)`.

## Redirection

Redirection connects a stream to a **file** instead of the terminal or another command.

| Syntax | Meaning |
|---|---|
| `cmd > file` | stdout to file (**overwrite**; creates the file if missing) |
| `cmd >> file` | stdout to file (**append**) |
| `cmd < file` | stdin from file |
| `cmd 2> file` | stderr to file |
| `cmd 2>/dev/null` | Discard errors |
| `cmd > file 2>&1` | stdout **and** stderr to the same file |
| `cmd &> file` | Same thing, bash shorthand |
| `cmd > /dev/null 2>&1` | Discard all output |
| `cmd << EOF … EOF` | **Here-document**: multi-line stdin written inline |
| `cmd <<< "text"` | **Here-string**: one string as stdin (bash) |
| `cmd \| tee file` | Show on screen **and** save to file (`tee -a` appends) |

```bash
ls -l > listing.txt                   # save output
echo "new line" >> notes.txt          # append
sort < names.txt > sorted.txt         # input from one file, output to another
find / -name "*.conf" 2>/dev/null     # hide permission errors
./build.sh > build.log 2>&1           # capture everything for later
make 2>&1 | tee build.log             # watch it live and save it
> app.log                             # empty a file (truncate) without deleting it

cat << EOF > config.ini
[server]
port=8080
EOF
```

> [!warning] Redirection gotchas
> - **`sort file > file` empties the file.** The shell opens and **truncates** `file` for output *before* `sort` runs, so `sort` reads an empty file. Use `sort -o file file`, `sort file | sponge file` (from moreutils), or write to a temp file and `mv` it.
> - **Order matters:** `cmd > file 2>&1` puts both streams in the file. `cmd 2>&1 > file` sends stderr to the **terminal**, because redirections are processed left to right: `2>&1` copies where stdout points *at that moment* (the terminal), and only then is stdout moved to the file.
> - **`>` is performed by your shell, not by the command.** So `sudo cmd > /root/file` fails: your non-root shell opens the file. Use `cmd | sudo tee /root/file`. See [[04 - Essential Commands#Permissions|Permissions gotchas]].
> - **`>` vs `>>`:** one wrong character overwrites a file you meant to append to. `set -o noclobber` makes `>` refuse to overwrite existing files (force with `>|`).

## Composing Tools: The Classic Filters

A **filter** reads stdin, transforms it, and writes stdout. These are the building blocks of most pipelines:

| Tool | Does one thing | Example |
|---|---|---|
| `grep` | Keep lines matching a pattern | `grep -i error` |
| `sort` | Sort lines (`-n` numeric, `-h` human sizes, `-r` reverse, `-k2` by field 2, `-u` unique) | `sort -rn` |
| `uniq` | Collapse **adjacent** duplicates (`-c` count them) | `sort \| uniq -c` |
| `cut` | Extract columns by delimiter | `cut -d: -f1 /etc/passwd` |
| `tr` | Translate or delete characters | `tr 'a-z' 'A-Z'` |
| `wc` | Count lines / words / bytes | `wc -l` |
| `head` / `tail` | First / last lines | `head -n 10` |
| `sed` | Stream editing (substitute, delete lines) | `sed 's/http:/https:/g'` |
| `awk` | Field-based processing, a small language | `awk '{print $1, $3}'` |
| `tee` | Copy the stream to a file and pass it on | `tee out.txt` |
| `xargs` | Turn input lines into **arguments** for a command | `xargs rm` |
| `column -t` | Align output into a table | `mount \| column -t` |

> [!warning] Filter gotchas
> - **`uniq` only removes *adjacent* duplicates.** `a b a` stays `a b a`. Always `sort` first (`sort | uniq`, or `sort -u`).
> - **`sort` is alphabetical by default:** `10` comes before `9`. Use `-n` for numbers and `-h` for sizes like `2K`, `1G`.
> - **`cut -d' '` breaks on multiple spaces** (each space starts a new field). For whitespace-separated columns, use `awk '{print $2}'`.
> - **`sort` order depends on your locale** (`LC_ALL`), and can differ between machines. Scripts that need a stable byte order use `LC_ALL=C sort`.

## Worked Pipelines

> [!example]- Top 5 most common words in a text file
> ```bash
> tr -cs '[:alpha:]' '\n' < book.txt | tr '[:upper:]' '[:lower:]' | sort | uniq -c | sort -rn | head -n 5
> ```
> | Stage | Output |
> |---|---|
> | `tr -cs '[:alpha:]' '\n' < book.txt` | Every run of non-letters becomes a newline, giving one word per line |
> | `tr '[:upper:]' '[:lower:]'` | Lowercase, so "The" and "the" count together |
> | `sort` | Identical words become adjacent (needed by `uniq`) |
> | `uniq -c` | Collapse duplicates, prefixing each with its count: `  42 the` |
> | `sort -rn` | Sort by that count, numerically, largest first |
> | `head -n 5` | Keep the top five |
>
> Six tools, none of which "knows" about word frequency, together solve a task none of them was designed for.

> [!example]- The 10 IP addresses that hit a web server most
> ```bash
> awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head
> ```
> Field 1 of each access-log line is the client IP. Same `sort | uniq -c | sort -rn` counting pattern as above: once you know it, you can reuse it everywhere.

> [!example]- Failed SSH logins by username
> ```bash
> journalctl -u ssh --since today | grep "Failed password" | grep -oE "for (invalid user )?[^ ]+" | awk '{print $NF}' | sort | uniq -c | sort -rn
> ```
> `grep -o` extracts only the "for USER" part; `awk '{print $NF}'` takes its last word (the username). (The unit is `sshd` on Fedora/RHEL/Arch.)

> [!example]- Find and delete all `.tmp` files safely, even with spaces in names
> ```bash
> find . -name "*.tmp" -print0 | xargs -0 rm --
> ```
> `-print0` separates names with a NUL byte instead of a newline, and `xargs -0` splits on NUL, so names with spaces or newlines survive intact. (`find . -name "*.tmp" -delete` is simpler here; the `xargs` pattern generalises to any command.)

## Exit Codes and Chaining

Every command returns an **exit code**: `0` means **success**, anything else means failure. (This is the opposite of most programming languages, where 0 is "false".)

```bash
ls /etc > /dev/null; echo $?     # 0   — $? holds the last exit code
ls /nope; echo $?                # 2   — error

mkdir build && cd build          # && : run the next command only if the previous SUCCEEDED
ping -c1 host || echo "down"     # || : run the next command only if the previous FAILED
make; make install               # ;  : run the next command regardless
sudo apt update && sudo apt upgrade -y
```

> [!warning] Exit-code gotchas
> - **A pipeline's exit code is that of the *last* command.** `false | true` returns 0, so `cat missing.txt | sort > out.txt` "succeeds" (and leaves an empty `out.txt`) even though `cat` failed. In scripts, use `set -o pipefail`.
> - **`grep` returns 1 when nothing matches.** That's normal, but in a script with `set -e` it stops the script.
> - **`a && b || c` is not a real if/else:** `c` also runs when `a` succeeds but `b` fails. Use `if a; then b; else c; fi` when it matters.

## Command Substitution and xargs

Two ways to use one command's output as **arguments** (not stdin) for another:

```bash
echo "Today is $(date +%A)"               # $(…) inserts the output into the command line
kill $(pgrep -f old-server)
cp report.pdf "backup-$(date +%F).pdf"    # backup-2026-09-25.pdf

find . -name "*.log" | xargs gzip          # xargs builds: gzip a.log b.log c.log …
grep -rl "oldName" src/ | xargs sed -i 's/oldName/newName/g'
```

> [!important] stdin vs arguments
> Some commands read **stdin** (`grep`, `sort`, `wc`); others only take **arguments** (`rm`, `cp`, `mkdir`, `echo`). `ls | rm` does nothing useful, because `rm` ignores stdin. That's what `xargs` or `$(…)` is for.

## Everything Is a File

Unix exposes very different things through the same file interface: open, read, write, close. The same tools (`cat`, `echo`, redirection) work on all of them.

```bash
cat /proc/cpuinfo                              # CPU info: generated by the kernel on read
cat /proc/$$/status                            # info about your current shell process
cat /sys/class/power_supply/BAT0/capacity      # battery percentage (on laptops)
echo "test" > /dev/null                        # the "black hole": discards everything
head -c 16 /dev/urandom | base64               # random bytes, e.g. for a password
dd if=/dev/zero of=blank.img bs=1M count=100   # a 100 MB file of zeros
lsblk; ls -l /dev/sda /dev/nvme0n1             # disks are "block device" files
ls -l /dev/tty                                 # your terminal is a "character device" file
mkfifo mypipe                                  # a named pipe: a pipe that lives in the filesystem
```

| Path | What it really is |
|---|---|
| `/dev/sda`, `/dev/nvme0n1` | Whole disks (block devices) |
| `/dev/null` | Discards writes; reads are always empty |
| `/dev/zero` / `/dev/urandom` | Endless zeros / random bytes |
| `/dev/tty`, `/dev/pts/0` | Terminals |
| `/proc/<pid>/` | A running process: command line, memory, open files |
| `/sys/…` | Devices and kernel settings |

See also [[03 - Core Parts of a Distro#Filesystem Hierarchy|Filesystem Hierarchy]].

> [!warning] "Everything is a file" isn't literally true on Linux
> **Network interfaces aren't files**: there's no `/dev/eth0`; you use `ip link` and sockets instead. It's more accurate to say "almost everything is a **file descriptor**". Also, writing to device files can be destructive: `dd … of=/dev/sda` overwrites a whole disk with no confirmation. Double-check `of=` with `lsblk` first.

## Why the Command Line Is Central

1. **Composability:** GUIs offer the features their designers imagined. Pipes let you build features nobody anticipated, as in the word-frequency example above.
2. **Automation:** any sequence you type can be saved as a script, scheduled (systemd timers, cron), and run on 1,000 servers. Clicks can't be.
3. **Remote work:** servers have no desktop ([[03 - Core Parts of a Distro#Display Server|no display server]]). `ssh server` gives you the full command line over a slow connection.
4. **Reproducibility and communication:** a command can be pasted into docs, chat or a note like this one, and it does exactly the same thing for someone else. "Click Settings → … → …" breaks with every UI redesign.
5. **Stability:** `ls`, `grep` and pipes work essentially as they did decades ago. Skills learned once keep paying off.
6. **Transparency:** GUIs on Linux are usually front-ends to the same command-line tools and text config files. Knowing the CLI lets you debug the GUI when it fails.
7. **Low requirements:** works in recovery mode, over serial consoles, in containers, and on tiny devices.

> [!tip] Balance
> The point isn't to avoid GUIs. A graphical file manager or settings app is often faster for one-off tasks. The CLI wins for anything **repeated, remote, bulk, or precise**.

## Limits and Criticisms

The philosophy is a guideline, not a law, and it has real limits:

- **Text parsing is fragile.** Tools meant for humans (`ls`, `ps`) don't have stable output formats. Parsing `ls` output breaks on file names with spaces or newlines; use `find`, globs or `stat` in scripts.
- **Not all data is lines of text.** JSON, YAML and CSV with quoted commas don't fit line-based tools well. Modern tools fill the gap in the same spirit: `jq` (JSON), `yq` (YAML), `xsv`/`miller` (CSV). PowerShell on Windows and Nushell take another route, passing **structured objects** through pipes instead of text.
- **systemd** is often cited as going against the philosophy, because it's one large suite doing many jobs (init, logging, network, DNS…). Supporters answer that it's many small binaries with a shared design, and that integration solved real problems. This remains an ongoing debate in the Linux world.
- **"Worse is better":** Unix won partly by being simple and pragmatic rather than perfect. Some rough edges (like the redirection gotchas above) are the price of that simplicity.

## Common Mistakes

> [!warning] Common Mistakes
> - `sort file > file` (or any read-and-write-same-file redirection), which empties the file.
> - Expecting errors to go through a pipe.
> - `2>&1 > file` in the wrong order.
> - `uniq` without `sort` first.
> - Numeric data sorted without `-n`.
> - Piping into commands that only take arguments (`ls | rm`) instead of using `xargs`.
> - `xargs` with file names containing spaces, without `-print0`/`-0`.
> - Trusting a pipeline's exit status without `pipefail`.
> - Parsing `ls` output in scripts.

## Practice

**1.** Count how many user accounts on the system use `bash` as their login shell. (`/etc/passwd` has one account per line, fields separated by `:`, and the shell is the last field.)

> [!success]- Solution
> ```bash
> cut -d: -f7 /etc/passwd | grep -c "bash$"
> ```
> or `grep -c "/bash$" /etc/passwd`. `cut` extracts field 7 (the shell); `grep -c` counts matching lines. Anchoring with `$` avoids matching things like `/usr/bin/bashful`.

**2.** `cat names.txt | uniq` still shows "Anna" three times. Why?

> [!success]- Solution
> `uniq` only collapses **adjacent** duplicate lines, and the three "Anna" lines aren't next to each other. Use `sort names.txt | uniq`, or just `sort -u names.txt`. (The `cat` is unnecessary too: `uniq names.txt` reads the file directly.)

**3.** What's the difference between these two commands?
```bash
./script.sh > out.txt 2>&1
./script.sh 2>&1 > out.txt
```

> [!success]- Solution
> - **First:** stdout goes to `out.txt`, then stderr is pointed at *where stdout now points* (the file). **Both** end up in `out.txt`.
> - **Second:** stderr is first pointed at where stdout points *at that moment* (the terminal); then stdout alone moves to the file. **Errors appear on screen**, and only normal output is saved.
>
> Redirections are processed left to right, and `2>&1` copies the *current* target; it isn't a permanent link.

**4.** You run `sort -r scores.txt > scores.txt` and the file is now empty. What happened, and how do you do it correctly?

> [!success]- Solution
> The shell sets up `> scores.txt` **before** starting `sort`, and doing so truncates the file to 0 bytes. `sort` then reads an empty file. Correct: `sort -r -o scores.txt scores.txt` (`sort` reads everything before writing its `-o` output), or `sort -r scores.txt > tmp && mv tmp scores.txt`.

**5.** Why doesn't `find . -name "*.bak" | rm` delete anything?

> [!success]- Solution
> `rm` takes file names as **arguments** and never reads **stdin**, so the piped list is ignored (and `rm` complains about a missing operand). Use `find . -name "*.bak" -delete`, `find … -exec rm {} +`, or `find … -print0 | xargs -0 rm`.

**6.** In a script, `cat data.csv | sort > sorted.csv && echo "Done!"` printed "Done!" even though `data.csv` doesn't exist. How?

> [!success]- Solution
> A pipeline's exit status is that of its **last** command. `cat` fails (exit 1), but `sort` happily sorts the empty input and exits 0, so `&&` sees success. You also get an empty `sorted.csv`. A failure in any stage **except the last** is invisible to `&&`. Put `set -o pipefail` at the top of the script so the pipeline fails if any stage fails. (Here, `sort data.csv > sorted.csv` also avoids the problem, because there's no pipeline.)

**7.** Write a one-liner that shows the 3 largest files (not directories) anywhere under your home directory.

> [!success]- Solution
> ```bash
> find ~ -type f -printf '%s %p\n' 2>/dev/null | sort -rn | head -n 3
> ```
> `-printf '%s %p\n'` prints size in bytes and path; `2>/dev/null` hides unreadable-directory errors; `sort -rn` sorts numerically, largest first. (For human-readable sizes: `find ~ -type f -exec du -h {} + 2>/dev/null | sort -rh | head -n 3`.)

## Related

- [[00 - Index]]
- [[04 - Essential Commands]]: the individual tools being composed here
- [[03 - Core Parts of a Distro#Core Utilities and the Shell|Core Utilities and the Shell]]: where these tools and the shell come from
- [[01 - What is Linux#A Short History|A Short History]]: where Unix fits in Linux's history
