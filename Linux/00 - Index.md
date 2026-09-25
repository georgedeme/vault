---
tags:
  - linux
---
# 00 - Index

This is the index for the `Linux/` knowledge base. Each chapter below is (or will become) its own note, in roughly the order it should be studied. It isn't meant to be exhaustive: chapters get added as new topics come up.

Checkboxes track progress: checked means the note exists and is written; unchecked means the chapter is planned. Clicking an unchecked link in Obsidian creates the note.

## Part I — Foundations

- [x] [[01 - What is Linux]] — kernel vs. distribution, open source and licences, how Linux differs from Windows/macOS
- [x] [[02 - Distributions Overview]] — what distinguishes distros, families, distros by purpose, how to choose
- [x] [[03 - Core Parts of a Distro]] — the full stack: kernel, bootloader, init, libraries, shell, package manager, display server, desktop, filesystem hierarchy
- [x] [[04 - Essential Commands]] — navigation, files, viewing, searching, permissions, processes, packages, discovering commands
- [x] [[05 - The Unix Philosophy]] — small composable tools, streams, pipes, redirection, why the CLI is central

## Part II — Working With the System

- [ ] [[Linux/06 - Users, Groups and Permissions|06 - Users, Groups and Permissions]] — permissions deep-dive: users/groups, `umask`, setuid/setgid/sticky bits, ACLs, `sudoers`
- [ ] [[Linux/07 - Processes and Signals|07 - Processes and Signals]] — process life cycle, states, signals, priorities, job control
- [ ] [[Linux/08 - Services and systemd|08 - Services and systemd]] — writing unit files, timers, targets, the journal
- [ ] [[Linux/09 - Disks, Filesystems and Mounting|09 - Disks, Filesystems and Mounting]] — partitions, ext4/btrfs/xfs, `fstab`, LVM, swap
- [ ] [[Linux/10 - Package Management in Depth|10 - Package Management in Depth]] — repositories, signing keys, pinning, building from source, Flatpak/Snap internals

## Part III — The Shell and Scripting

- [ ] [[Linux/11 - Shell Environment and Customisation|11 - Shell Environment and Customisation]] — variables, `PATH`, `.bashrc`/`.zshrc`, aliases, quoting and expansion
- [ ] [[Linux/12 - Text Processing|12 - Text Processing]] — regular expressions, `grep`, `sed`, `awk`, `jq`
- [ ] [[Linux/13 - Shell Scripting|13 - Shell Scripting]] — conditionals, loops, functions, arguments, `set -euo pipefail`

## Part IV — Networking

- [ ] [[Linux/14 - Networking Basics|14 - Networking Basics]] — IP, DNS, `ip`, `ss`, `ping`, `curl`
- [ ] [[Linux/15 - SSH and Remote Access|15 - SSH and Remote Access]] — keys, config, tunnels, `scp`/`rsync`
- [ ] [[Linux/16 - Firewalls|16 - Firewalls]] — nftables, `ufw`, `firewalld`

## Part V — Advanced

- [ ] [[Linux/17 - The Boot Process in Depth|17 - The Boot Process in Depth]] — UEFI, Secure Boot, initramfs, recovery
- [ ] [[Linux/18 - The Kernel in Depth|18 - The Kernel in Depth]] — modules, `sysctl`, compiling a kernel
- [ ] [[Linux/19 - Containers|19 - Containers]] — namespaces, cgroups, Docker/Podman
- [ ] [[Linux/20 - Security and Hardening|20 - Security and Hardening]] — updates, SELinux/AppArmor, auditing

## Review

- [ ] [[Linux/Cheat Sheet|Cheat Sheet]] — the most-used commands and rules on one page
- [ ] [[Linux/Exercises|Exercises]] — mixed practice across chapters (each chapter already has its own **Practice** section)

## Key Concepts

Each concept is explained in one place; other notes link there.

| Concept | Where it's explained |
|---|---|
| Kernel | [[03 - Core Parts of a Distro#Kernel\|Core Parts → Kernel]] |
| Distribution | [[01 - What is Linux#Kernel vs. Distribution\|What is Linux → Kernel vs. Distribution]] |
| Distro families (Debian, Red Hat, Arch, SUSE) | [[02 - Distributions Overview#Distro Families\|Distributions → Distro Families]] |
| Release models (fixed, LTS, rolling, atomic) | [[02 - Distributions Overview#Release models\|Distributions → Release models]] |
| Open source and licences (GPL, MIT…) | [[01 - What is Linux#Open Source Basics\|What is Linux → Open Source Basics]] |
| Bootloader (GRUB) | [[03 - Core Parts of a Distro#Bootloader\|Core Parts → Bootloader]] |
| Init system (systemd, PID 1) | [[03 - Core Parts of a Distro#Init System\|Core Parts → Init System]] |
| C library (glibc, musl) | [[03 - Core Parts of a Distro#System Libraries\|Core Parts → System Libraries]] |
| Shell, terminal, console | [[03 - Core Parts of a Distro#Core Utilities and the Shell\|Core Parts → Core Utilities and the Shell]] |
| Package manager, Flatpak/Snap/AppImage | [[03 - Core Parts of a Distro#Package Manager\|Core Parts → Package Manager]] |
| X11 vs. Wayland | [[03 - Core Parts of a Distro#Display Server\|Core Parts → Display Server]] |
| Desktop environment vs. window manager | [[03 - Core Parts of a Distro#Desktop Environment and Window Manager\|Core Parts → Desktop Environment]] |
| Filesystem hierarchy (`/etc`, `/usr`, `/var`…) | [[03 - Core Parts of a Distro#Filesystem Hierarchy\|Core Parts → Filesystem Hierarchy]] |
| Permissions (`rwx`, `chmod`, `sudo`) | [[04 - Essential Commands#Permissions\|Essential Commands → Permissions]] |
| Processes and signals | [[04 - Essential Commands#Process Management\|Essential Commands → Process Management]] |
| Man pages and finding commands | [[04 - Essential Commands#Discovering New Commands\|Essential Commands → Discovering New Commands]] |
| stdin / stdout / stderr | [[05 - The Unix Philosophy#Standard Streams\|Unix Philosophy → Standard Streams]] |
| Pipes | [[05 - The Unix Philosophy#Pipes\|Unix Philosophy → Pipes]] |
| Redirection | [[05 - The Unix Philosophy#Redirection\|Unix Philosophy → Redirection]] |
| Exit codes, `&&`, `\|\|` | [[05 - The Unix Philosophy#Exit Codes and Chaining\|Unix Philosophy → Exit Codes and Chaining]] |
| Everything is a file | [[05 - The Unix Philosophy#Everything Is a File\|Unix Philosophy → Everything Is a File]] |

> [!tip] Adding a chapter
> 1. Create the note from its unchecked link above (or add a new line in the right part and number it).
> 2. Follow the chapter structure: short intro line → sections → **Common Mistakes** → **Practice** (solutions in `> [!success]- Solution`) → **Related**. Tag it `#linux`.
> 3. When a concept gets its own chapter (e.g. permissions), point the **Key Concepts** row to it, and link the new chapter from the section that currently explains the concept.
> 4. Tick the checkbox.

## Notes

- Order within each part is the intended reading order; parts are meant to be read in sequence.
- Planned chapters (Parts II–V) are suggestions. Rename, reorder or drop them as your learning goes; renaming a note through Obsidian updates the links.
