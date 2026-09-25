---
tags:
  - linux
---
# 01 - What is Linux

This note covers what "Linux" actually means, where it came from, how open source works, and why using Linux feels different from Windows or macOS.

## Kernel vs. Distribution

The word "Linux" is used for two different things, and a lot of confusion comes from mixing them up.

> [!note] Definition: Linux (strictly speaking)
> **Linux** is a **kernel**: the core program that manages hardware, memory, processes and devices. Other programs ask it for things like "open this file" or "send this packet". On its own the kernel has no shell, no desktop, no installer and no apps. See [[03 - Core Parts of a Distro#Kernel|Kernel]].

> [!note] Definition: Distribution (distro)
> A **distribution** is a complete, installable operating system built around the Linux kernel. It adds a [[03 - Core Parts of a Distro#Bootloader|bootloader]], an [[03 - Core Parts of a Distro#Init System|init system]], [[03 - Core Parts of a Distro#System Libraries|system libraries]], a [[03 - Core Parts of a Distro#Core Utilities and the Shell|shell and core tools]], a [[03 - Core Parts of a Distro#Package Manager|package manager]] and usually a [[03 - Core Parts of a Distro#Desktop Environment and Window Manager|desktop environment]]. Ubuntu, Fedora, Debian and Arch are distributions. See [[02 - Distributions Overview]].

**Analogy:** the kernel is the engine and the distribution is the car. Many different cars use the same engine, but they don't have the same seats, dashboard or maintenance schedule.

| Layer | Who makes it | Examples |
|---|---|---|
| Kernel | Linux kernel project (Linus Torvalds and thousands of contributors) | `linux` 6.x |
| Core userland | GNU project and others | `bash`, `ls`, `cp`, `grep`, glibc |
| System services | Various projects | systemd, NetworkManager, PipeWire |
| Desktop | Desktop projects | GNOME, KDE Plasma, Xfce |
| Packaging, defaults, installer, support | **The distribution** | apt + Ubuntu repos, dnf + Fedora repos |

You can check both halves on any system:

```bash
uname -r              # kernel version, e.g. 6.12.10-200.fc41.x86_64
cat /etc/os-release   # distribution name and version, e.g. Fedora Linux 41
```

> [!important] Kernel version ≠ distro version
> "Ubuntu 24.04" is a **distribution** version (released April 2024). The kernel inside it has its own version number (6.8, 6.11, …). Nobody runs "Linux 24.04".

### The "GNU/Linux" naming debate

The GNU project (started 1983 by Richard Stallman) wrote much of the userland that early distros used: the compiler (GCC), the C library (glibc), the shell (bash) and the core utilities. The Free Software Foundation argues that the whole OS should be called **GNU/Linux**. Most people just say "Linux". Both are common; you'll see "GNU/Linux" in Debian's documentation.

### Edge cases: is it Linux?

| System | Linux kernel? | Typical GNU userland? | Verdict |
|---|---|---|---|
| Ubuntu, Fedora, Arch | ✓ | ✓ | A regular Linux distribution |
| **Alpine Linux** | ✓ | ✗ (uses musl + BusyBox) | Linux, but almost no GNU. That's why "GNU/Linux" doesn't cover everything |
| **Android** | ✓ (modified) | ✗ (Bionic libc, own userland) | Runs the Linux kernel, but isn't a "Linux distro" in the usual sense. Normal Linux apps don't run on it |
| **ChromeOS** | ✓ | Partly | Linux-based (built with Gentoo's tooling). Runs regular Linux apps in a container |
| **WSL 2** (Windows) | ✓ (real kernel in a lightweight VM) | ✓ | Real Linux running inside Windows |
| **WSL 1** | ✗ (translated Linux syscalls into Windows calls) | ✓ | Linux programs without a Linux kernel |
| **macOS** | ✗ (XNU kernel: Mach + BSD) | ✗ (BSD tools) | **Not Linux.** It's a certified UNIX, a cousin rather than a relative |
| **FreeBSD / OpenBSD** | ✗ (own kernels) | ✗ | Separate Unix-like operating systems |
| **SteamOS** (Steam Deck) | ✓ | ✓ | An Arch-based Linux distribution |

## A Short History

| Year | Event |
|---|---|
| 1969 | **Unix** is created at Bell Labs (Ken Thompson, Dennis Ritchie). It's the ancestor of the ideas in [[05 - The Unix Philosophy]] |
| 1983 | Richard Stallman announces the **GNU** project, a free Unix-like OS |
| 1987 | Andrew Tanenbaum releases **Minix**, a small teaching Unix |
| 1991 | Linus Torvalds, a Finnish student, announces a hobby kernel: *"just a hobby, won't be big and professional like gnu"* |
| 1992 | Linux is relicensed under the **GPLv2**. GNU tools + Linux kernel = a complete free OS |
| 1993 | Slackware and Debian, among the oldest distributions still maintained |
| 2004 | Ubuntu launches and makes desktop Linux much more approachable |
| 2005 | Linus writes **Git** to manage kernel development |
| 2008 | Android ships, putting the Linux kernel on billions of phones |

> [!info]- Why does Linux look like Unix if it contains no Unix code?
> Linux is **Unix-like**: it was written from scratch to behave like Unix, following the **POSIX** standard (a specification of how Unix-like systems should behave: system calls, shell, core utilities). It contains no original AT&T Unix code. That's why shell skills carry over between Linux, macOS and the BSDs, while the internals are completely different.

## Open Source Basics

> [!note] Definition: Open source / free software
> Software whose **source code** is available and whose licence lets you use, study, modify and redistribute it. The FSF frames this as the **four freedoms**:
> 0. Run the program for any purpose.
> 1. Study and change how it works (requires source access).
> 2. Redistribute copies.
> 3. Distribute your modified versions.

"Free" means **free as in freedom** (libre), not necessarily **free as in beer** (gratis). You can legally sell free software.

### Licences you'll meet

| Licence | Type | What it requires | Used by |
|---|---|---|---|
| **GPL** (v2, v3) | Copyleft | If you **distribute** modified binaries, you must provide the source under the same licence | Linux kernel (GPLv2 only), bash, GCC |
| **LGPL** | Weak copyleft | Changes to the library must be shared; programs that just *link* to it can stay closed | glibc |
| **MIT / BSD** | Permissive | Keep the copyright notice; otherwise do what you want, including closing the source | Xorg, FreeBSD, many libraries |
| **Apache 2.0** | Permissive + patent grant | Like MIT, plus explicit patent terms | Kubernetes, Android userland |

> [!important] Copyleft is triggered by distribution, not by use
> You can modify GPL software privately forever and share nothing. The obligation to share source applies once you **give binaries to someone else**, and it's owed to the people you gave them to.

### How the kernel is developed

- Changes are sent as patches to mailing lists (LKML), reviewed by **subsystem maintainers**, and merged upward to Linus.
- A new mainline kernel comes out roughly every **9–10 weeks**: a 2-week merge window, then weekly `-rc` release candidates.
- Some versions are marked **longterm (LTS)** and receive fixes for years. Distros usually build on these.
- Most kernel code today is written by paid engineers at companies such as Intel, Google, Red Hat, AMD, Meta and Microsoft.

> [!warning] Two opposite myths about open source
> - *"Anyone can change the code."* Anyone can **fork** it, but changes to the official project go through review.
> - *"Open source is automatically secure because many people look at it."* Not guaranteed. In 2024 a backdoor was deliberately planted in the `xz` compression library (CVE-2024-3094) by a trusted maintainer. It was caught by chance, just before it reached stable distros. Open code makes discovery **possible**; it doesn't make it certain.

## How Linux Differs from Windows and macOS

### At a glance

| Aspect | Linux | Windows | macOS |
|---|---|---|---|
| Kernel | Linux (monolithic, modular) | NT | XNU |
| Source | Open | Closed | Mostly closed (Darwin core is open) |
| Who controls it | Nobody single-handedly: many distros and projects | Microsoft | Apple |
| Installing software | [[03 - Core Parts of a Distro#Package Manager\|Package manager]] from signed repositories | Download installers, Microsoft Store, winget | App Store, DMG downloads, Homebrew |
| Updates | One command updates the **OS and all apps**; you choose when | Windows Update (OS only); often forced | Software Update |
| Configuration | Mostly **plain-text files** in `/etc` and `~/.config` | Registry + GUI | plist files + GUI |
| Filesystem layout | One tree from `/`, drives **mounted** into it ([[03 - Core Parts of a Distro#Filesystem Hierarchy\|FHS]]) | Drive letters `C:\`, `D:\` | One tree from `/` |
| Path separator | `/` | `\` | `/` |
| File names | **Case-sensitive** (`Notes.txt` ≠ `notes.txt`) | Case-insensitive | Case-insensitive by default |
| What makes a file executable | The **execute permission bit** | The extension (`.exe`, `.bat`) | Permission bit / app bundle |
| Hidden files | Name starts with `.` | A file attribute | Name starts with `.` |
| Line endings | `LF` (`\n`) | `CRLF` (`\r\n`) | `LF` |
| Admin model | Normal user + `sudo` when needed | UAC prompts | Normal user + `sudo` / password prompt |
| Role of the terminal | Central, first-class tool | Optional (PowerShell) | Optional (zsh) |

### The mindset shifts

1. **Choice everywhere.** There is no single "Linux look". The desktop, the file manager, even the init system can be swapped. That's powerful, but the same task may be done differently on two distros.
2. **Software comes from repositories.** Instead of googling "download X", you run `sudo apt install x` and the distro gives you a signed, tested package. Downloading random installers from websites is the exception. See [[04 - Essential Commands#Package Management|Package Management]].
3. **Text is the interface.** Configuration lives in readable text files, and tools talk to each other through text streams. This is the heart of [[05 - The Unix Philosophy]].
4. **You aren't root by default.** Your daily account can't break the system; you borrow admin rights with `sudo` for single commands. See [[04 - Essential Commands#Permissions|Permissions]].
5. **The command line is normal.** GUIs exist and are good, but the terminal is often the fastest, most precise and most documented way to do something.
6. **Transparency.** You can read the source, the logs (`journalctl`) and the config. When something breaks, the information needed to fix it is usually there.

> [!info]- Why can Linux replace a file that's in use, when Windows refuses?
> On Linux a file name is just a pointer to the actual data (an *inode*). Deleting or replacing the name doesn't touch a program that already has the file open: it keeps using the old data until it closes it. That's why package managers can update running programs without a reboot, and why only a **kernel** update truly needs one. The downside is that deleting a huge log file that's still open doesn't free the disk space until the process holding it closes it.

> [!warning] "It's all Unix, so my macOS terminal skills transfer 1:1"
> Mostly, but not completely. macOS ships **BSD** versions of tools, Linux ships **GNU** versions, and flags differ. Classic example: in-place editing is `sed -i 's/a/b/' file` on Linux but `sed -i '' 's/a/b/' file` on macOS.

### Honest trade-offs

- **Commercial software:** Adobe Creative Cloud and Microsoft Office have no native Linux versions (web versions or alternatives only).
- **Gaming:** Proton (Steam) runs most Windows games well, but some online games whose anti-cheat blocks Linux don't work.
- **Hardware:** most hardware works out of the box. Very new laptops, some Wi-Fi chips, fingerprint readers and NVIDIA GPUs (proprietary driver) can need extra steps.

## Where Linux Runs

- **Servers and cloud:** the large majority of web servers and cloud instances.
- **Supercomputers:** every system on the TOP500 list has run Linux since 2017.
- **Phones:** Android, via the Linux kernel.
- **Embedded:** routers, smart TVs, cars, NAS boxes, smart devices.
- **Containers:** Docker and Kubernetes rely on Linux kernel features (namespaces, cgroups). Docker on Windows or macOS quietly runs a Linux VM.
- **Desktops:** a few percent of the market, growing thanks to gaming (Steam Deck) and developers.

## Common Mistakes

> [!warning] Common Mistakes
> - **"I downloaded Linux."** You downloaded a **distribution**. The kernel is one part of it.
> - **"Linux = Ubuntu."** Ubuntu is one distro among hundreds. Instructions for Ubuntu don't always work on Fedora or Arch (different [[03 - Core Parts of a Distro#Package Manager|package managers]], paths, defaults).
> - **Confusing kernel and distro versions.** `uname -r` shows the kernel; `/etc/os-release` shows the distro.
> - **Ignoring case sensitivity.** `cd Documents` works; `cd documents` fails. `Photo.JPG` and `photo.jpg` can both exist in the same folder.
> - **Scripts written on Windows.** They carry `CRLF` line endings and fail with `/bin/bash^M: bad interpreter`. Fix with `dos2unix script.sh` or `sed -i 's/\r$//' script.sh`.
> - **Thinking open source means no cost or no company.** Red Hat sells RHEL subscriptions; Canonical sells Ubuntu Pro.

## Practice

**1.** A friend says: *"I'm running Linux 24.04."* What's imprecise about that?

> [!success]- Solution
> 24.04 is the **Ubuntu** version (year.month of release). "Linux" strictly means the kernel, which has its own numbering (e.g. 6.8). The accurate phrasing is "Ubuntu 24.04, kernel 6.8". Check with `cat /etc/os-release` and `uname -r`.

**2.** Is Android Linux? Is macOS?

> [!success]- Solution
> - **Android:** it runs the Linux **kernel**, but not the GNU userland or glibc. It isn't a Linux *distribution* in the usual sense, and desktop Linux programs don't run on it.
> - **macOS:** no. It uses the XNU kernel and is a certified **UNIX**. It feels similar in the terminal because both follow POSIX and share the Unix heritage.

**3.** A router manufacturer modifies the Linux kernel, adds its own closed-source web-interface app, and sells the routers. What must it publish?

> [!success]- Solution
> Because the kernel is **GPLv2**, the manufacturer must provide the **source code of its modified kernel** to people who receive the router (the binary). The **separate** user-space web-interface app is a different program that only talks to the kernel through system calls, so it can stay closed-source. The GPL does not "infect" programs just because they run on Linux.

**4.** On a Linux laptop, can `Notes.txt` and `notes.txt` coexist in the same folder? What if the folder is on a FAT32 USB stick?

> [!success]- Solution
> On a normal Linux filesystem (ext4, btrfs, xfs): **yes**, they're two different files. On a **FAT32/exFAT** USB stick: **no**. Case sensitivity is a property of the **filesystem**, not of the OS, and FAT is case-insensitive even when mounted on Linux. Copying both files to the stick makes one overwrite the other (or triggers an error).

**5.** RHEL costs money. Is it still open source?

> [!success]- Solution
> **Yes.** The subscription pays for support, certified updates and tooling, not for the right to use the code. The GPL requires Red Hat to give the source to those who receive the binaries (its customers). Since 2023, Red Hat publishes the development code as **CentOS Stream** and gives the exact RHEL sources to customers only. That decision is what forced rebuilds like Rocky Linux and AlmaLinux to change how they work (see [[02 - Distributions Overview#Enterprise|Enterprise distros]]).

**6.** Your Windows-edited script fails with `bash: ./deploy.sh: /bin/bash^M: bad interpreter: No such file or directory`, although `/bin/bash` clearly exists. Why?

> [!success]- Solution
> The file has Windows `CRLF` line endings, so the first line is really `#!/bin/bash\r`. The system looks for an interpreter literally named `bash\r` (shown as `^M`). Convert with `dos2unix deploy.sh`. You can reveal the hidden characters with `cat -A deploy.sh`, where lines end in `^M$`.

## Related

- [[00 - Index]]
- [[02 - Distributions Overview]]: the major distributions and how they differ
- [[03 - Core Parts of a Distro]]: every layer on top of the kernel
- [[05 - The Unix Philosophy]]: the design ideas Linux inherited from Unix
