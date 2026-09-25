---
tags:
  - linux
---
# 04 - Essential Commands

This is a practical reference for the commands you'll use daily, grouped by task. Each section also lists the gotchas that catch people out. At the end is how to discover commands you don't know yet.

## Anatomy of a Command

```bash
ls   -l -a   --human-readable   /etc
│    │       │                   └── argument (what to act on)
│    │       └── long option (full word, two dashes)
│    └── short options (one letter, one dash; can combine: -la)
└── command
```

- Everything is **case-sensitive**: `ls -r` (reverse order) ≠ `ls -R` (recursive).
- Short options usually combine: `ls -l -a -h` = `ls -lah`.
- `--` means "end of options": `rm -- -weird-name.txt` deletes a file whose name starts with `-`.
- **Paths:** absolute paths start at `/` (`/etc/hosts`); relative paths start from your current directory (`docs/notes.txt`). `.` = current dir, `..` = parent, `~` = your home, `-` (with `cd`) = previous dir.
- **Tab completion:** press `Tab` to complete commands, paths and even options; press it twice to list possibilities. Use it constantly: it's faster and prevents typos.

## Navigation

| Command | What it does |
|---|---|
| `pwd` | Print the current (working) directory |
| `cd dir` | Change directory |
| `cd` / `cd ~` | Go home |
| `cd -` | Go back to the previous directory |
| `cd ..` | Up one level |
| `ls` | List directory contents |
| `ls -l` | Long format: permissions, owner, size, date |
| `ls -a` | Include hidden (dot) files |
| `ls -lh` | Human-readable sizes (K, M, G) |
| `ls -lt` / `ls -lS` | Sort by modification time / size |
| `ls -R` | Recursive |
| `ls -d */` | List only directories |
| `tree -L 2` | Tree view, 2 levels deep (may need installing) |

```bash
cd /var/log        # absolute path
cd ../lib          # relative: sibling directory
cd "My Documents"  # quotes needed because of the space
ls -lah ~/Downloads
```

## Files and Directories

| Command | What it does |
|---|---|
| `touch file` | Create an empty file (or update an existing file's timestamp) |
| `mkdir dir` | Create a directory |
| `mkdir -p a/b/c` | Create nested directories (no error if they exist) |
| `cp src dst` | Copy a file |
| `cp -r dir dst` | Copy a directory recursively |
| `cp -a dir dst` | Archive copy: recursive + keep permissions, owners, timestamps, symlinks |
| `mv src dst` | Move **or rename** |
| `rm file` | Delete a file (**permanently**) |
| `rm -r dir` | Delete a directory and everything in it |
| `rmdir dir` | Delete a directory only if it's **empty** |
| `ln -s target linkname` | Create a symbolic link (shortcut) |
| `file thing` | Detect the real file type (ignores the extension) |
| `stat file` | Detailed metadata: size, permissions, timestamps, inode |

```bash
mkdir -p projects/linux/notes
cp notes.txt notes.bak
cp -r photos/ /media/george/USB/
mv draft.md final.md                 # rename
mv *.jpg ~/Pictures/                 # move many files
ln -s /opt/app/bin/app ~/.local/bin/app
rm -i *.tmp                          # ask before each deletion
```

> [!warning] Files and directories gotchas
> - <span class="hl-red">`rm` has no Recycle Bin.</span> Deleted files are gone. Consider `rm -i`, `rm -I` (asks once for >3 files), or `trash-cli` (`trash-put file`).
> - **`cp` and `mv` overwrite existing files silently.** Use `-i` (ask) or `-n` (never overwrite).
> - **Spaces in names:** `rm my file.txt` deletes two files, `my` and `file.txt`. Quote it: `rm "my file.txt"`, or escape: `rm my\ file.txt`.
> - **Dangerous variables:** `rm -rf "$DIR"/` with an empty `$DIR` becomes `rm -rf /`. GNU `rm` refuses `/` itself (`--preserve-root`), but **not `/*`**. In scripts use `"${DIR:?}"`, which aborts if `DIR` is empty.
> - **A stray space:** `rm -rf / home/george/tmp` (note the space after `/`) targets `/`.
> - **`ln -s` argument order** is the same as `cp`: **target first**, then the link name. Relative targets are resolved relative to the **link's** location, not your current directory.
> - `cp dir dst` without `-r` fails with `omitting directory`.
> - **`*` doesn't match hidden files**, so `cp -r src/* dst/` skips `.gitignore`, `.env` etc. Use `cp -r src/. dst/`.

## Viewing Content

| Command | What it does |
|---|---|
| `cat file` | Print a whole file (best for short files) |
| `less file` | Scroll through a file: `/text` search, `n`/`N` next/previous match, `g`/`G` top/bottom, `q` quit |
| `head file` / `head -n 20 file` | First 10 / 20 lines |
| `tail file` / `tail -n 50 file` | Last 10 / 50 lines |
| `tail -f log` | **Follow** a file as it grows (logs). `Ctrl+C` to stop |
| `tail -F log` | Follow, and keep following if the file is rotated or recreated |
| `wc -l file` | Count lines (`-w` words, `-c` bytes) |
| `diff -u old new` | Show differences between files |
| `cat -A file` | Show hidden characters: tabs `^I`, line ends `$`, Windows CR `^M` |

```bash
less /var/log/syslog
tail -f /var/log/nginx/access.log
head -n 5 data.csv
journalctl -f            # follow the systemd journal instead of text log files
```

> [!warning] Viewing content gotchas
> - **`cat` on a binary file** can garble your terminal. Type `reset` (even blindly) to fix it. Check first with `file thing`.
> - **Don't `cat` huge files**; use `less`, which doesn't load the whole file.
> - **`tail -f` stops following after log rotation** (the old file gets renamed). Use `tail -F`.
> - **`wc -l` counts newline characters**, so a file whose last line has no trailing newline reports one line fewer than you'd expect.
> - Many distros now log only to the systemd **journal**: `/var/log/syslog` may not exist. Use `journalctl`.

## Searching

### Finding files: `find`, `locate`

```bash
find . -name "*.md"                  # by name (case-sensitive), from current dir
find ~ -iname "*report*"             # case-insensitive
find /var/log -type f -size +100M    # files bigger than 100 MB
find . -type d -name node_modules    # directories only
find . -mtime -7                     # modified in the last 7 days
find . -name "*.tmp" -delete         # delete matches (see warning!)
find . -name "*.sh" -exec chmod +x {} +   # run a command on all matches

locate nginx.conf                    # instant search in a prebuilt database (plocate/mlocate)
sudo updatedb                        # refresh that database
```

### Searching inside files: `grep`

| Option | Meaning |
|---|---|
| `grep text file` | Lines containing `text` |
| `-i` | Ignore case |
| `-r` | Recursive through directories |
| `-n` | Show line numbers |
| `-v` | Invert: lines that **don't** match |
| `-l` | Only print file names that match |
| `-c` | Count matching lines |
| `-w` | Whole words only |
| `-E` | Extended regex: `+`, `?`, `()` and alternation work without backslashes |
| `-F` | Fixed string: treat the pattern literally, not as a regex |
| `-o` | Print only the matched part |
| `-A 3` / `-B 3` / `-C 3` | Show 3 lines after / before / around each match |

```bash
grep -rn "TODO" ~/projects
grep -i "error" /var/log/syslog
grep -v "^#" /etc/ssh/sshd_config      # hide comment lines
grep -E "fail(ed|ure)" app.log
```

### Finding commands

```bash
which python3        # path of the executable that would run
type ls              # builtin? alias? function? file? (more complete than which)
type -a python3      # every match on PATH, in order
whereis ls           # binary, source, man page locations
command -v git       # portable "is this installed?" check for scripts
```

> [!warning] Searching gotchas
> - **Quote `find` patterns:** `find . -name *.md` lets the **shell** expand `*.md` first (to files in the current dir), giving wrong results or `paths must precede expression`. Write `find . -name "*.md"`.
> - **`-delete` position matters!** `find . -delete -name "*.tmp"` deletes **everything**, because `find` evaluates left to right and `-delete` runs before the name test. Always put `-delete` last, and run the command without it first to preview.
> - **`grep` patterns are regular expressions**: `grep "1.5"` also matches `125`, since `.` means "any character". Use `grep -F "1.5"` for literal text.
> - **`locate` can't find new files** until the database is updated (usually daily, or manually with `sudo updatedb`).
> - **`which` misses aliases, builtins and functions**: `which cd` finds nothing, but `type cd` says "shell builtin".
> - **`ps aux | grep firefox` also shows the grep process itself.** Use `pgrep -a firefox`.

## Permissions

> [!note] Reading `ls -l`
> ```
> -rwxr-xr--  1  george  devs  4096  Sep 25 10:00  deploy.sh
> │└┬┘└┬┘└┬┘  │    │      │     │         │           └── name
> │ │  │  │   │    │      │     │         └── last modified
> │ │  │  │   │    │      │     └── size (bytes)
> │ │  │  │   │    │      └── group
> │ │  │  │   │    └── owner (user)
> │ │  │  │   └── hard link count
> │ │  │  └── others: r--  (read only)
> │ │  └── group:  r-x  (read + execute)
> │ └── owner:  rwx  (read + write + execute)
> └── type: - file, d directory, l symlink, c/b device, s socket, p pipe
> ```

| | On a **file** | On a **directory** |
|---|---|---|
| `r` (4) | Read the contents | **List** the names inside (`ls`) |
| `w` (2) | Modify the contents | **Create, delete, rename** entries inside |
| `x` (1) | Run it as a program | **Enter / pass through** it (`cd`, access files inside) |

**Octal notation:** add the numbers for each of owner/group/others.

| Octal | Symbolic | Typical use |
|---|---|---|
| `755` | `rwxr-xr-x` | Scripts, programs, directories |
| `644` | `rw-r--r--` | Normal files |
| `700` | `rwx------` | Private directories (`~/.ssh`) |
| `600` | `rw-------` | Private files (SSH keys, secrets) |
| `777` | `rwxrwxrwx` | ⚠️ Almost never correct |

```bash
chmod +x script.sh            # add execute for everyone (subject to umask)
chmod u+x,g-w file            # symbolic: u=user(owner) g=group o=others a=all
chmod 644 notes.txt           # octal
chmod -R u+rwX project/       # capital X: execute only on directories (and already-executable files)
sudo chown george:devs file   # change owner and group
whoami; id                    # who am I, which groups am I in
sudo command                  # run one command as root
sudo -i                       # interactive root shell (use sparingly)
./script.sh                   # run a script in the current directory
```

This is the basic model only; a permissions deep-dive (special bits, ACLs, umask) is planned (see [[00 - Index]]).

> [!warning] Permissions gotchas
> - **`chmod -R 777` is never the fix.** It gives *everyone* write access and hides the real problem (usually the wrong owner: fix with `chown`).
> - **Deleting depends on the directory, not the file.** With `w` on a directory you can delete a file in it even if the file itself is read-only and owned by someone else. The exception is the **sticky bit** (`/tmp` is `drwxrwxrwt`): only the owner can delete their files there.
> - **`./script.sh` vs `script.sh`:** the current directory isn't on `PATH` (for security), so you must write `./`. `Permission denied` means you forgot `chmod +x`; you can also run `bash script.sh` without the execute bit.
> - **`sudo echo "text" > /etc/file` fails** with `Permission denied`. The **redirection `>` is done by your own shell** before `sudo` runs. Use `echo "text" | sudo tee /etc/file` (`tee -a` to append). See [[05 - The Unix Philosophy#Redirection|Redirection]].
> - **`sudo cd /root` fails**: `cd` is a shell builtin (see [[03 - Core Parts of a Distro#Core Utilities and the Shell|Why cd is a builtin]]). Use `sudo -i` or `sudo ls /root`.
> - **Don't run graphical apps with `sudo`**; they may create root-owned files in your home and break things later. Use `sudoedit /etc/file` (or `pkexec`) for editing system files.

## Process Management

A **process** is a running program, identified by a **PID**. Every process has a parent; the tree starts at PID 1, the [[03 - Core Parts of a Distro#Init System|init system]].

| Command | What it does |
|---|---|
| `ps aux` | Snapshot of all processes (BSD-style flags) |
| `ps -ef` | Same, POSIX style (shows parent PID) |
| `pgrep -a name` | Find processes by name, with command lines |
| `top` | Live view sorted by CPU (`q` quit, `M` sort by memory, `k` kill) |
| `htop` / `btop` | Friendlier interactive viewers (may need installing) |
| `kill PID` | Send SIGTERM: ask the process to exit cleanly |
| `kill -9 PID` | Send SIGKILL: force-kill (last resort) |
| `pkill name` / `killall name` | Signal processes by name |
| `command &` | Run in the **background** |
| `jobs` | List this shell's background/stopped jobs |
| `fg %1` / `bg %1` | Bring job 1 to the foreground / resume it in the background |
| `nohup command &` | Keep running after you close the terminal |
| `nice -n 10 command` | Start with lower CPU priority |

**Keyboard control of the foreground process:**

| Key | Signal | Effect |
|---|---|---|
| `Ctrl+C` | SIGINT | Interrupt: usually stops the program |
| `Ctrl+Z` | SIGTSTP | **Pause** (suspend): the program is still there; resume with `fg` or `bg` |
| `Ctrl+D` | — (end of input) | "No more input": exits shells and interactive programs |
| `Ctrl+\` | SIGQUIT | Stronger quit, with a core dump |

**Services** (long-running background daemons) are managed through systemd:

```bash
systemctl status ssh
sudo systemctl restart nginx
journalctl -u nginx --since "10 min ago"
```

More in [[03 - Core Parts of a Distro#Init System|Init System]].

> [!warning] Process gotchas
> - **Reach for `kill -9` last.** SIGKILL gives the program no chance to save data, remove lock files or close connections cleanly. Try plain `kill` (SIGTERM) first and wait a few seconds.
> - **`Ctrl+Z` does not quit.** A suspended process still holds memory, files and ports (then "port already in use" confuses you). Check `jobs`.
> - **Zombie processes (`Z` state) can't be killed**: they're already dead, and their parent hasn't collected their exit status. Kill or fix the **parent**.
> - **Processes in `D` state** (uninterruptible sleep, usually waiting on a disk or NFS) ignore even `kill -9` until the I/O completes.
> - **Closing the terminal sends SIGHUP**, which kills its jobs. Use `nohup`, `disown`, `tmux`/`screen`, or a systemd service for long-running work.
> - **`killall` on other Unixes** (e.g. Solaris) kills *all processes*. On Linux it kills by name; prefer `pkill` in scripts you'll share.

## Package Management

The same tasks across the major [[02 - Distributions Overview#Distro Families|distro families]]:

| Task | Debian / Ubuntu | Fedora / RHEL | Arch | openSUSE |
|---|---|---|---|---|
| Refresh package lists | `sudo apt update` | (automatic) `dnf makecache` | `sudo pacman -Sy` ⚠️ only with `-u` | `sudo zypper refresh` |
| Upgrade everything | `sudo apt update && sudo apt upgrade` | `sudo dnf upgrade` | `sudo pacman -Syu` | `sudo zypper update` (Tumbleweed: `sudo zypper dup`) |
| Install | `sudo apt install pkg` | `sudo dnf install pkg` | `sudo pacman -S pkg` | `sudo zypper install pkg` |
| Remove | `sudo apt remove pkg` | `sudo dnf remove pkg` | `sudo pacman -R pkg` | `sudo zypper remove pkg` |
| Remove + configs / unused deps | `sudo apt purge pkg`, `sudo apt autoremove` | `sudo dnf autoremove` | `sudo pacman -Rns pkg` | `sudo zypper remove -u pkg` |
| Search | `apt search term` | `dnf search term` | `pacman -Ss term` | `zypper search term` |
| Package info | `apt show pkg` | `dnf info pkg` | `pacman -Si pkg` | `zypper info pkg` |
| List installed | `apt list --installed` | `dnf list --installed` | `pacman -Q` | `zypper search -i` |
| Which package owns a file? | `dpkg -S /usr/bin/ls` | `rpm -qf /usr/bin/ls` | `pacman -Qo /usr/bin/ls` | `rpm -qf /usr/bin/ls` |
| Which package *provides* a file (not installed)? | `apt-file search name` | `dnf provides '*/name'` | `pacman -F name` | `zypper search --provides name` |
| Install a local package file | `sudo apt install ./file.deb` | `sudo dnf install ./file.rpm` | `sudo pacman -U file.pkg.tar.zst` | `sudo zypper install ./file.rpm` |

Alpine: `apk update`, `apk upgrade`, `apk add pkg`, `apk del pkg`, `apk search term`.

**Universal formats** (see [[03 - Core Parts of a Distro#Package Manager|Package Manager]] for the comparison):

```bash
flatpak install flathub org.mozilla.firefox
flatpak update
flatpak list

sudo snap install code --classic
snap list
```

> [!warning] Package management gotchas
> - **`apt update` doesn't upgrade anything**; it only refreshes the list of what's available. `apt upgrade` installs the upgrades.
> - **`apt` vs `apt-get`:** `apt` is for humans (progress bars, nicer output); `apt-get` has a stable interface for **scripts**.
> - **`apt install ./file.deb` needs the `./`.** Without it, apt searches the repositories for a package with that name.
> - **Arch partial upgrades:** never `pacman -Sy pkg`. Refreshing without upgrading can install a package built against newer libraries than you have. Use `pacman -Syu pkg`.
> - **Package names differ between families:** `apache2` (Debian) vs `httpd` (Fedora); `build-essential` vs `@development-tools`. Use search.
> - **Another process holds the lock** (`Could not get lock /var/lib/dpkg/lock-frontend`): an automatic update or another terminal is running. Wait for it; **don't delete the lock file**.

## System Information

Not a separate category in most lists, but you'll use these constantly:

```bash
uname -a                  # kernel and architecture
cat /etc/os-release       # distribution and version
hostnamectl               # hostname, OS, kernel, hardware summary
uptime                    # how long running + load averages
free -h                   # RAM and swap usage
df -h                     # free space per mounted filesystem
du -sh folder/            # size of a folder
du -sh -- * | sort -h     # sizes of everything here, smallest → largest
lsblk                     # disks and partitions
lscpu; lspci; lsusb       # CPU, PCI devices (GPU, Wi-Fi), USB devices
ip a                      # network interfaces and IP addresses
ss -tulpn                 # listening ports and which programs own them
```

> [!info]- Trick: `df` says the disk is full, but `du` can't find the files
> A process still has a **deleted** file open, typically a log file removed with `rm` while the service is writing to it. The name is gone (so `du` doesn't count it), but the data stays allocated until the process closes it (so `df` still counts it). Find it with `sudo lsof +L1` (or `sudo lsof | grep deleted`), then restart that process. Truncating a log instead of deleting it (`> file.log` or `truncate -s 0 file.log`) avoids the problem.

## Discovering New Commands

You don't memorise commands; you learn how to look them up fast.

| Tool | Use it for | Example |
|---|---|---|
| `man cmd` | The full official manual | `man ls` |
| `cmd --help` | Quick option summary | `cp --help` |
| `tldr cmd` | Community cheat sheets of common examples | `tldr tar` |
| `apropos keyword` / `man -k keyword` | Search man page **descriptions** when you don't know the command name | `apropos partition` |
| `whatis cmd` | One-line description | `whatis grep` |
| `help builtin` | Docs for **shell builtins** (bash) | `help cd` |
| `type cmd` | What kind of command it is | `type cd` |
| `info cmd` | Longer GNU manuals (coreutils, bash) | `info coreutils` |

**Navigating `man`** (it uses `less`): `/word` search, `n` next match, `g`/`G` top/bottom, `q` quit. Scroll to **EXAMPLES** near the end for usage examples.

**Man page sections:** the same name can exist in several sections.

| Section | Contents | Example |
|---|---|---|
| 1 | User commands | `man 1 passwd` (the command) |
| 2 | System calls | `man 2 open` |
| 3 | C library functions | `man 3 printf` |
| 4 | Device files | `man 4 null` |
| 5 | **File formats and config files** | `man 5 passwd` (the `/etc/passwd` file), `man 5 crontab` |
| 7 | Overviews, conventions | `man 7 signal`, `man 7 regex` |
| 8 | System administration commands | `man 8 mount` |

`man passwd` shows section 1 (the first match). `man -f passwd` lists all sections that have it.

```bash
man -k "copy file"       # same as apropos
tldr find                # install with: apt/dnf/pacman install tldr (or tealdeer)
compgen -c | less        # every command available in this shell
ls /usr/share/doc/pkg    # extra docs shipped with a package
```

> [!tip] Beyond the terminal
> - The **Arch Wiki** (wiki.archlinux.org) is excellent even if you don't use Arch.
> - **explainshell.com** breaks down a pasted command, option by option.
> - Error messages are searchable: paste the exact message in quotes.

> [!warning] Discovery gotchas
> - **`man cd` gives nothing** (or a generic builtins page): `cd` is a bash builtin. Use `help cd`.
> - **Some distros ship without man pages** (minimal containers, Ubuntu minimal images). Install `man-db`, or run `unminimize` on minimal Ubuntu.
> - **`apropos` finds nothing** right after installing packages until its index is rebuilt (`sudo mandb`).
> - **Not every command supports `--help`**, and some BSD-style tools print usage only on errors. Fall back to `man`.
> - **Don't copy-paste commands from the web blindly**, especially `curl … | sudo bash`. Read them first; look up each part.

## Terminal Shortcuts

| Shortcut | Action |
|---|---|
| `Tab` / `Tab Tab` | Complete / list completions |
| `↑` / `↓` | Previous / next command in history |
| `Ctrl+R` | **Reverse-search history** (type part of an old command; `Ctrl+R` again for older) |
| `!!` | The previous command (`sudo !!` = rerun last command with sudo) |
| `!$` or `Alt+.` | Last argument of the previous command |
| `Ctrl+A` / `Ctrl+E` | Jump to start / end of line |
| `Ctrl+W` / `Ctrl+U` / `Ctrl+K` | Delete previous word / to start of line / to end of line |
| `Ctrl+L` | Clear the screen (same as `clear`) |
| `Ctrl+Shift+C` / `Ctrl+Shift+V` | Copy / paste in most terminal emulators |
| `Ctrl+S` / `Ctrl+Q` | Freeze / unfreeze terminal output |

> [!warning] `Ctrl+C` in a terminal is not "copy"
> It sends SIGINT and interrupts the running program. Copy with `Ctrl+Shift+C`. And if your terminal suddenly "stops responding" to typing, you probably pressed `Ctrl+S`; press `Ctrl+Q`.

## Common Mistakes

> [!warning] Common Mistakes
> - Forgetting quotes around names with spaces, or around `find`/`grep` patterns.
> - Using `rm -rf` with variables or wildcards without checking what they expand to. Run `echo rm -rf $DIR/*` first to see the expansion.
> - Expecting `*` to include dotfiles.
> - `sudo` with `>` redirection, or with `cd`.
> - Fixing permission errors with `chmod 777` instead of fixing ownership.
> - `kill -9` as the first resort; `Ctrl+Z` mistaken for quitting.
> - `apt update` without `apt upgrade` (or the reverse, with stale lists).
> - Looking for `man cd`, `which cd`.
> - Mixing up `ls -r` / `ls -R`, and similar case differences.

## Practice

**1.** `ls -lh` shows your `Photos` directory as `4.0K`, but it holds 3 GB of pictures. Is something wrong?

> [!success]- Solution
> No. For a directory, `ls -l` reports the size of the **directory itself** (the list of names it contains, usually one 4 KB block), not the total of its contents. To measure what's inside, use `du -sh Photos/`.

**2.** You run `find . -delete -name "*.log"` in your project folder. What happens?

> [!success]- Solution
> **Everything under `.` is deleted**, not just the `.log` files. `find` evaluates its expression left to right: `-delete` comes first, is applied to every file, and the `-name` test after it doesn't matter. The correct form is `find . -name "*.log" -delete`. Always run without `-delete` first to preview.

**3.** `echo "127.0.0.1 test.local" > /etc/hosts` gives `Permission denied`. So does `sudo echo "127.0.0.1 test.local" > /etc/hosts`. Why, and what's the fix? (Bonus: what's wrong with the original command even as root?)

> [!success]- Solution
> The `>` redirection is performed by **your** (non-root) shell *before* running `sudo echo`, so opening `/etc/hosts` for writing fails. Fix: `echo "127.0.0.1 test.local" | sudo tee -a /etc/hosts`. Here `tee` runs as root and does the writing.
> **Bonus:** `>` **truncates**. Even as root, it would have **replaced the whole `/etc/hosts`** with one line. You want **append** (`>>`, or `tee -a`).

**4.** A user has `rw-` on a file `report.txt`, but the directory containing it is `r-x` for them. Can they (a) edit the file, (b) delete it, (c) rename it?

> [!success]- Solution
> (a) **Yes**: editing changes the file's *contents*, governed by the file's own `w` bit.
> (b) **No** and (c) **No**: deleting and renaming change the *directory's* list of entries, which requires `w` on the **directory**.
> (Careful: some editors "save" by writing a new file and renaming it over the old one. With a non-writable directory that save fails even though the file itself is writable.)

**5.** A program ignores `Ctrl+C`. What do you do, in order?

> [!success]- Solution
> 1. Try `Ctrl+\` (SIGQUIT), or `Ctrl+Z` then `kill %1`.
> 2. From another terminal: `pgrep -a name` → `kill PID` (SIGTERM); wait a few seconds.
> 3. Only then `kill -9 PID` (SIGKILL).
> 4. If even that doesn't work, check its state in `ps`. `D` (waiting on I/O) or `Z` (zombie: deal with the parent) processes won't respond to signals.

**6.** You want to know which command can resize a partition, but you don't know its name. How do you find it without a web search?

> [!success]- Solution
> `apropos partition` (or `man -k partition`) searches the one-line descriptions of all man pages and lists candidates like `fdisk`, `parted`, `resize2fs`, `growpart`. Then `whatis`/`tldr`/`man` the promising one.

**7.** `man passwd` describes the command, but you wanted the format of the `/etc/passwd` file. How do you get it?

> [!success]- Solution
> `man 5 passwd`. Section 5 holds file formats; section 1 (the default first match) holds the command. `man -f passwd` shows which sections exist.

**8.** You deleted a 20 GB log file with `rm`, but `df -h` shows no extra free space. Why?

> [!success]- Solution
> The service writing that log still has the file **open**. The name is gone, but the data remains until the process closes it. Find it with `sudo lsof +L1` and restart the service. Next time, empty an in-use log with `truncate -s 0 file.log` instead of deleting it.

## Related

- [[00 - Index]]
- [[03 - Core Parts of a Distro]]: what these commands belong to (coreutils, shell, package manager, systemd)
- [[05 - The Unix Philosophy]]: combining these commands with pipes and redirection
- [[02 - Distributions Overview#Distro Families|Distro families]]: which package manager you have
