---
tags:
  - linux
---
# 03 - Core Parts of a Distro

A distribution is a stack of independent projects assembled into one OS. This note goes through each layer from the hardware up: what it does, what the common choices are, and how to inspect it on your own system.

## The Stack at a Glance

```
┌──────────────────────────────────────────────────────────────┐
│  Applications         Firefox, VS Code, LibreOffice, …       │
├──────────────────────────────────────────────────────────────┤
│  Desktop Environment  GNOME, KDE Plasma, Xfce … (or a WM)    │
├──────────────────────────────────────────────────────────────┤
│  Display Server       Wayland compositor / X11 (Xorg)        │
├──────────────────────────────────────────────────────────────┤
│  Shell + core utils   bash/zsh, ls, cp, grep, …              │
│  Package manager      apt, dnf, pacman, …                    │
├──────────────────────────────────────────────────────────────┤
│  Init system          systemd (PID 1) → starts all services  │
├──────────────────────────────────────────────────────────────┤
│  System libraries     glibc (or musl), libstdc++, OpenSSL …  │
╞══════════════════════ system calls ══════════════════════════╡  ← user space above
│  Kernel               Linux: processes, memory, drivers, FS  │  ← kernel space below
├──────────────────────────────────────────────────────────────┤
│  Bootloader           GRUB / systemd-boot (runs only at boot)│
├──────────────────────────────────────────────────────────────┤
│  Firmware             UEFI / BIOS                            │
├──────────────────────────────────────────────────────────────┤
│  Hardware             CPU, RAM, disk, GPU, network           │
└──────────────────────────────────────────────────────────────┘
```

All of this is laid out on disk according to the [[#Filesystem Hierarchy]].

> [!note] Kernel space vs. user space
> - **Kernel space**: code running with full hardware privileges. Only the kernel (and its modules/drivers) runs here. A bug here can crash the whole machine.
> - **User space**: everything else: your shell, the desktop, every app, even `root`'s programs. These can't touch hardware directly; they ask the kernel through **system calls** (`open`, `read`, `write`, `fork`, …), usually via the C library.
>
> Being `root` is a **user-space** privilege level. It's still user space, just with permission to ask the kernel for more.

## Kernel

> [!note] Definition
> The **kernel** is the core of the OS, the one program that talks to hardware. Linux is a **monolithic kernel with loadable modules**: drivers, filesystems and networking all run inside the kernel, but many of them can be loaded and unloaded at runtime as **modules**.

What it's responsible for:
- **Process scheduling**: deciding which program runs on which CPU core, and when.
- **Memory management**: virtual memory, swapping, isolating processes from each other.
- **Device drivers**: disks, GPUs, USB, Wi-Fi, …
- **Filesystems**: ext4, btrfs, xfs, FAT, NTFS, …
- **Networking**: the TCP/IP stack and firewall (netfilter/nftables).
- **Security and isolation**: permissions, namespaces and cgroups (the basis of containers).

```bash
uname -r                       # running kernel version
uname -a                       # kernel + architecture + hostname
ls /boot                       # vmlinuz-* (kernel image) and initramfs/initrd files
lsmod                          # currently loaded modules
modinfo e1000e                 # info about a module
sudo modprobe <module>         # load a module (with its dependencies)
sudo dmesg -w                  # kernel message log, live (or: journalctl -k)
```

> [!info]- What is the initramfs?
> To mount your root filesystem, the kernel may need drivers (for NVMe, LVM, encryption, RAID…) that live **on** that filesystem, which is a chicken-and-egg problem. The **initramfs** is a small temporary root filesystem loaded into RAM by the bootloader alongside the kernel. It contains just enough tools and modules to unlock and mount the real root, then hands over to the real init. Rebuild it with `update-initramfs -u` (Debian/Ubuntu), `dracut -f` (Fedora/RHEL) or `mkinitcpio -P` (Arch).

> [!warning] Kernel gotchas
> - **A kernel update doesn't take effect until you reboot.** After updating, `uname -r` still shows the old version. (Enterprise distros offer *livepatching* for critical fixes.)
> - **Distros keep older kernels installed** as fallbacks. If a new kernel breaks something, pick the previous one from the boot menu.
> - On some distros (notably Arch), updating the kernel **deletes the module files of the running kernel**. Plugging in a USB device that needs a not-yet-loaded module then fails until you reboot.

## Bootloader

> [!note] Definition
> The **bootloader** is the small program the firmware starts. It loads the kernel and initramfs into memory, passes them **kernel parameters**, and starts the kernel. It usually shows a boot menu for choosing between kernels or operating systems.

**The boot hand-off:** firmware (UEFI or legacy BIOS) → **bootloader** → kernel + initramfs → [[#Init System|init]].

| Bootloader | Notes |
|---|---|
| **GRUB 2** | The default on most distros. Handles BIOS and UEFI, dual boot, encrypted `/boot`, complex setups |
| **systemd-boot** | Simple UEFI-only boot manager; reads entries from the EFI partition (Pop!_OS, Arch, some Fedora setups) |
| **rEFInd** | Graphical UEFI boot manager that auto-detects OSes |
| **Limine** | Modern, lightweight; used by some Arch-based distros (e.g. CachyOS) |

With **UEFI**, bootloaders live as `.efi` files on the **EFI System Partition (ESP)**, a small FAT32 partition usually mounted at `/boot/efi` or `/efi`. With **Secure Boot**, distros boot a Microsoft-signed **shim** first, which then verifies GRUB and the kernel.

**Changing GRUB settings the right way:**

```bash
sudo nano /etc/default/grub           # edit settings (e.g. GRUB_TIMEOUT=3, kernel params)

# then regenerate the real config:
sudo update-grub                                  # Debian / Ubuntu
sudo grub2-mkconfig -o /boot/grub2/grub.cfg       # Fedora / RHEL
sudo grub-mkconfig -o /boot/grub/grub.cfg         # Arch

# Fedora/RHEL: change kernel arguments for all kernels
sudo grubby --update-kernel=ALL --args="quiet splash"
```

> [!warning] Bootloader gotchas
> - **Never edit `grub.cfg` directly.** It's generated and gets overwritten at the next kernel update. Edit `/etc/default/grub` (or files in `/etc/grub.d/`) and regenerate.
> - **One-off kernel parameters:** at the GRUB menu, press `e` on an entry, append a parameter to the `linux` line (e.g. `nomodeset` for a broken graphics driver), and press `Ctrl+X` to boot. This doesn't change anything permanently.
> - **Dual boot:** a Windows update or reinstall can overwrite the boot order and hide GRUB. Fix the order in the UEFI setup or with `efibootmgr`. Also disable Windows **Fast Startup**: it leaves NTFS partitions in a hibernated state that Linux mounts read-only.
> - **Hidden menu:** Ubuntu hides the GRUB menu on single-OS systems. Hold `Shift` (BIOS) or tap `Esc` (UEFI) during boot to show it.

## Init System

> [!note] Definition
> The **init system** is the first user-space process the kernel starts. It always has **process ID 1** (PID 1). It brings up the rest of the system (mounts filesystems, starts services, handles login), acts as the ancestor of all processes, and handles shutdown. If PID 1 dies, the kernel panics.

**systemd** is the init system on almost every major distro (Debian, Ubuntu, Fedora, RHEL, Arch, openSUSE). It's also a whole suite: logging (`journald`), login sessions (`logind`), networking (`networkd`), DNS (`resolved`), timers (a cron replacement) and more.

systemd manages **units**, which are described in unit files:

| Unit type | Purpose | Example |
|---|---|---|
| `.service` | A daemon or one-shot task | `sshd.service`, `nginx.service` |
| `.timer` | Scheduled activation (cron replacement) | `fstrim.timer` |
| `.socket` | Start a service when a connection arrives | `cups.socket` |
| `.mount` | A mounted filesystem | `home.mount` |
| `.target` | A group of units / system state (like old runlevels) | `multi-user.target`, `graphical.target` |

```bash
systemctl status sshd                 # is it running? recent log lines
sudo systemctl start nginx            # start now (this boot only)
sudo systemctl enable nginx           # start automatically at every boot
sudo systemctl enable --now nginx     # both at once
sudo systemctl restart nginx          # stop + start
sudo systemctl reload nginx           # re-read config without stopping (if supported)
sudo systemctl disable --now nginx    # stop and don't start at boot
systemctl list-units --type=service   # running services
systemctl --failed                    # what broke?
systemctl get-default                 # graphical.target or multi-user.target

journalctl -u nginx -f                # follow a service's logs
journalctl -b -p err                  # errors from the current boot
journalctl -b -1                      # logs from the previous boot (after a crash)

ps -p 1 -o comm=                      # which init is PID 1 on this system?
```

**Where unit files live:**
- `/usr/lib/systemd/system/`: installed by packages. **Don't edit these**; updates overwrite them.
- `/etc/systemd/system/`: admin overrides; these win. Use `sudo systemctl edit nginx` to create a drop-in override safely.
- After editing unit files manually: `sudo systemctl daemon-reload`.

**Alternatives to systemd:** OpenRC (Alpine, Gentoo), runit (Void), s6, SysVinit (Devuan, a Debian fork without systemd). They do the same job with a smaller scope.

> [!warning] Init gotchas
> - **`start` ≠ `enable`.** `start` runs the service now; `enable` makes it start at boot. Doing only one of them is the #1 "it worked until I rebooted" bug.
> - **`systemctl` inside Docker containers usually fails.** Containers normally run just one process as PID 1, not systemd.
> - **`mask`** is stronger than `disable`: a masked unit can't be started at all, even manually or as a dependency. `unmask` to undo.

## System Libraries

> [!note] Definition
> **Shared libraries** are code used by many programs, loaded at run time instead of being copied into each binary. The most important is the **C standard library** (libc), which implements basic functions (`printf`, `malloc`, `fopen`) and wraps kernel **system calls**. Nearly every program on the system depends on it, directly or indirectly.

| Library | Used by | Notes |
|---|---|---|
| **glibc** (GNU C Library) | Almost all distros | Feature-rich, highly compatible |
| **musl** | Alpine, Void (optional) | Small, simple, strict; common in containers |
| **Bionic** | Android | Google's libc |

Other core libraries: `libstdc++` (C++ runtime), OpenSSL/GnuTLS (crypto/TLS), `zlib`, `libsystemd`. Libraries live in `/usr/lib` (and `/usr/lib64` on Red Hat systems).

```bash
ldd /usr/bin/ls         # which shared libraries a binary needs
ldd --version           # glibc version
file /usr/bin/ls        # "dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2"
```

> [!warning] Library gotchas
> - **`version 'GLIBC_2.38' not found`**: a binary built on a **newer** distro won't run on an **older** glibc. The reverse usually works. That's why portable software is often built on old distros.
> - **Never remove or manually replace glibc.** Almost every command, including `ls`, `sudo` and the package manager itself, stops working instantly.
> - **glibc binaries don't run on musl** (e.g. in Alpine containers), and the error message misleadingly says the file is "not found". See [[02 - Distributions Overview#Practice|Distributions → Practice Q3]].
> - **Statically linked binaries** (common with Go and Rust) include their libraries and don't depend on the system libc, which is why they're easy to copy between distros.

## Core Utilities and the Shell

### Core utilities

The small commands that make the system usable, each doing one job (see [[05 - The Unix Philosophy]]):

| Package | Provides |
|---|---|
| **GNU coreutils** | `ls`, `cp`, `mv`, `rm`, `cat`, `mkdir`, `chmod`, `sort`, `head`, `wc`, … |
| **util-linux** | `mount`, `lsblk`, `fdisk`, `kill`, `su`, `dmesg` |
| **findutils, grep, sed, gawk** | `find`/`xargs`, text searching, stream editing, text processing |
| **procps-ng** | `ps`, `top`, `free`, `kill`, `pgrep` |
| **BusyBox** | One small binary implementing simplified versions of all of the above (Alpine, embedded, initramfs) |
| **uutils coreutils** | A Rust rewrite of coreutils; Ubuntu began shipping it by default in 25.10 |

The everyday commands themselves are covered in [[04 - Essential Commands]].

### The shell

> [!note] Definition
> The **shell** is the program that reads the commands you type, expands things like `*` and `$HOME`, starts programs, and connects them with [[05 - The Unix Philosophy#Pipes|pipes]] and [[05 - The Unix Philosophy#Redirection|redirection]]. It's also a programming language (shell scripts).

| Shell | Notes |
|---|---|
| **bash** | The default interactive shell on most distros; what most tutorials assume |
| **zsh** | Bash-like with better completion and plugins (Oh My Zsh); default on macOS and Kali |
| **fish** | Friendly, great out-of-the-box suggestions, but **not POSIX-compatible** (bash syntax often doesn't work) |
| **dash** | Minimal, fast POSIX shell. `/bin/sh` on Debian/Ubuntu |

> [!important] Terminal ≠ shell ≠ console
> - **Terminal emulator**: the *window* (GNOME Terminal, Konsole, kitty, Alacritty, Ghostty, Windows Terminal). It draws text and sends keystrokes.
> - **Shell**: the *program running inside* that window (bash, zsh), which interprets your commands.
> - **Console / TTY**: the text-only virtual terminals provided by the kernel (`Ctrl+Alt+F3` … `F6`), usable even when the desktop is broken.

```bash
echo $SHELL          # your *login* shell (from /etc/passwd), not necessarily the one running now
ps -p $$             # the shell actually running right now
cat /etc/shells      # installed shells
chsh -s /usr/bin/zsh # change your login shell (log out and back in)
type cd              # "cd is a shell builtin"
type ls              # "ls is aliased to `ls --color=auto'" or "/usr/bin/ls"
```

> [!info]- Why must `cd` be a shell builtin and not a separate program?
> Every external command runs as a **child process** of the shell. A child can change **its own** working directory, but never its parent's. If `cd` were a program, it would change directory inside itself, exit, and your shell would stay where it was. So `cd`, `export`, `source`/`.`, `alias` and `exit` are built into the shell. The same reason explains why `sudo cd /root` fails: `sudo` can only run external programs, and there's no `/usr/bin/cd` that could affect your shell.

> [!warning] `#!/bin/sh` is not bash
> On Debian/Ubuntu, `/bin/sh` is **dash**. A script with `#!/bin/sh` that uses bash-only features (`[[ ]]`, arrays, `source`, `{1..5}`) fails with confusing errors, even though the same lines work in your terminal. Use `#!/bin/bash` if you use bash features.

## Package Manager

> [!note] Definition
> A **package manager** installs, updates and removes software as **packages**: archives with the program's files plus metadata (version, dependencies, install scripts). It downloads them from the distro's **repositories**, checks their **cryptographic signatures**, resolves **dependencies**, and keeps a database of which file belongs to which package.

Two levels:

| Family | Low level (single package files, no dependency resolution) | High level (repos + dependencies) |
|---|---|---|
| Debian/Ubuntu | `dpkg` | `apt` |
| Fedora/RHEL | `rpm` | `dnf` |
| Arch | (`pacman` does both) | `pacman`; AUR helpers like `yay`/`paru` |
| openSUSE | `rpm` | `zypper` |
| Alpine | (`apk` does both) | `apk` |

Repository definitions live in `/etc/apt/sources.list.d/`, `/etc/yum.repos.d/` or `/etc/pacman.conf`. The command cheat sheet per family is in [[04 - Essential Commands#Package Management|Essential Commands → Package Management]].

### Universal package formats

These work across distros and ship apps together with their dependencies:

| Format | Backed by | Sandboxed | Updates | Best for |
|---|---|---|---|---|
| **Flatpak** | Community (Flathub) | ✓ (portals, permissions) | `flatpak update` | Desktop apps on any distro; the de facto standard |
| **Snap** | Canonical | ✓ (AppArmor) | Automatic | Ubuntu desktop and server apps, IoT |
| **AppImage** | Community | ✗ | Manual (download new file) | Portable single-file apps: `chmod +x App.AppImage && ./App.AppImage` |

> [!warning] Package manager gotchas
> - **Don't `sudo pip install` (or `sudo npm install -g`) into system directories.** It can overwrite files the package manager owns. Modern distros block it with `error: externally-managed-environment`. Use a virtual environment (`python -m venv`), `pipx`, or the distro package (`python3-requests`).
> - **Mixing formats duplicates apps.** Firefox from apt, Snap *and* Flatpak means three separate profiles and update paths.
> - **`apt update` ≠ `apt upgrade`.** `update` only refreshes the package **list**; `upgrade` actually installs newer versions.
> - **Third-party repos** (PPAs, COPR, AUR) aren't vetted by your distro. They're convenient, but each one is code you're choosing to trust with root.

## Display Server

> [!note] Definition
> The **display server** sits between graphical apps and the hardware (via the kernel's graphics drivers). It draws windows on screen and routes keyboard/mouse input to the right app. Servers usually have **no display server at all**: they're managed over SSH in text.

| | **X11 (Xorg)** | **Wayland** |
|---|---|---|
| Age | 1984 / X11 since 1987 | Since 2008; default on major desktops since the early 2020s |
| Architecture | Separate X server + window manager + compositor | The **compositor is the display server**: one program (Mutter, KWin, Sway, Hyprland) |
| Security | Any app can read other apps' windows and keystrokes | Apps are isolated from each other |
| Modern features | Bolted on (tearing, mixed-DPI monitors are hard) | Built in: per-monitor scaling, tear-free, HDR, VRR |
| Network transparency | Built in (`ssh -X`) | Not built in (use RDP/VNC, `waypipe`) |
| Status | Maintenance mode; GNOME and KDE are dropping their X11 sessions | Current default everywhere |

**XWayland** runs old X11-only apps inside a Wayland session, transparently.

```bash
echo $XDG_SESSION_TYPE     # wayland, x11, or tty
```

> [!warning] Display server gotchas
> - **Old X11 tools don't work on Wayland**: `xdotool` (automation), `xclip`/`xsel` (clipboard; use `wl-copy`/`wl-paste`), global hotkey tools, some screen recorders. This is by design, because of the security model.
> - **Screen sharing on Wayland** goes through **PipeWire + xdg-desktop-portal**. If Zoom, Discord or OBS shows a black screen, the portal package for your desktop is usually missing.
> - **NVIDIA + Wayland** was troublesome for years. It works well with recent proprietary drivers (explicit sync), but older drivers and distros may still struggle.

## Desktop Environment and Window Manager

> [!note] Definitions
> - **Window manager (WM):** controls the placement, size, focus and decorations of windows. Nothing more.
> - **Desktop environment (DE):** a complete, integrated user interface: a WM/compositor **plus** panel/taskbar, app launcher, file manager, settings app, notifications, network/sound/Bluetooth applets and default apps.
> - **Display manager:** the graphical **login screen** (GDM, SDDM, LightDM) that starts your chosen session. Despite the name, it isn't the display server.

### Desktop environments

| DE | Toolkit | Feel | Resource use |
|---|---|---|---|
| **GNOME** | GTK | Minimal, workflow-driven (Activities overview); extensions for customisation | Medium–high |
| **KDE Plasma** | Qt | Traditional layout, extremely configurable | Medium (lighter than its reputation) |
| **Xfce** | GTK | Classic, stable, modest | Low |
| **Cinnamon** | GTK | Windows-like (Linux Mint) | Medium |
| **MATE** | GTK | Continuation of classic GNOME 2 | Low |
| **LXQt** | Qt | Very lightweight | Very low |
| **COSMIC** | Rust (iced) | Modern, built-in tiling (System76 / Pop!_OS) | Low–medium |
| **Budgie** | GTK | Simple, elegant | Medium |

### Window managers (without a full DE)

| Type | How windows are arranged | Examples |
|---|---|---|
| **Tiling** | Automatically, side by side without overlap; keyboard-driven | i3 (X11), **Sway** (Wayland i3), **Hyprland** (Wayland, animations), bspwm, dwm, niri (scrolling) |
| **Stacking / floating** | Freely overlapping, like classic desktops | Openbox, Fluxbox, IceWM |

A bare WM means assembling your own bar (waybar, polybar), launcher (rofi, wofi), notifications and so on. It's lightweight and highly personal, but it's more work.

> [!tip] You can install several
> Multiple DEs/WMs can be installed side by side; pick one per session at the login screen (usually a gear icon). **GTK apps run fine under KDE, and Qt apps under GNOME**; they may just look slightly out of place.

## Filesystem Hierarchy

Linux has **one directory tree** starting at `/` (root). There are no drive letters: other disks, partitions and USB sticks are **mounted** into a directory in that tree. The standard layout is the **Filesystem Hierarchy Standard (FHS)**.

| Directory | Contains | Example |
|---|---|---|
| `/` | The root of everything | — |
| `/home` | Users' personal directories | `/home/george` (= `~`) |
| `/root` | Home directory of the **root user** (not `/`!) | `/root/.bashrc` |
| `/etc` | System-wide **configuration** (text files) | `/etc/fstab`, `/etc/hostname`, `/etc/ssh/sshd_config` |
| `/usr` | Installed software, read-only in normal operation | `/usr/bin/python3`, `/usr/lib`, `/usr/share/doc` |
| `/usr/local` | Software **you** install manually for all users (the package manager stays out) | `/usr/local/bin/myscript` |
| `/opt` | Self-contained third-party apps | `/opt/google/chrome` |
| `/bin`, `/sbin`, `/lib` | Essential binaries / admin binaries / libraries. On modern distros, **symlinks into `/usr`** | `/bin → /usr/bin` |
| `/var` | **Variable** data that changes while running | `/var/log` (logs), `/var/cache`, `/var/lib` (databases, Docker), `/var/spool` |
| `/tmp` | Temporary files, often **cleared on reboot** (frequently in RAM, as tmpfs) | — |
| `/var/tmp` | Temporary files that should **survive** reboots | — |
| `/boot` | Kernel, initramfs, bootloader files | `/boot/vmlinuz-6.12…` |
| `/boot/efi` | The EFI System Partition (UEFI systems) | `/boot/efi/EFI/ubuntu/shimx64.efi` |
| `/dev` | **Device files**: hardware as files | `/dev/sda`, `/dev/nvme0n1p2`, `/dev/null` |
| `/proc` | **Virtual**: live kernel and process info (not on disk) | `/proc/cpuinfo`, `/proc/meminfo`, `/proc/1234/` |
| `/sys` | **Virtual**: devices and kernel settings | `/sys/class/power_supply/BAT0/capacity` |
| `/run` | Runtime data since boot (tmpfs) | PID files, sockets, `/run/user/1000` |
| `/mnt` | Temporary manual mount point | `sudo mount /dev/sdb1 /mnt` |
| `/media` | Automatic mount point for removable media | `/media/george/USB_STICK` |
| `/srv` | Data served by this system (rarely used) | `/srv/www` |
| `/lost+found` | Recovered file fragments after a filesystem check (ext4) | — |

In your home directory, settings live in **hidden dotfiles/dot-directories**: `~/.bashrc`, `~/.ssh/`, and per the XDG standard `~/.config/` (settings), `~/.local/share/` (data) and `~/.cache/`.

```bash
man hier               # the official description of the hierarchy on your system
ls -la ~               # show hidden dotfiles in your home
df -hT                 # mounted filesystems, their types and free space
lsblk -f               # disks → partitions → filesystems → mount points
findmnt                # the mount tree
cat /proc/meminfo      # read kernel info as if it were a file
```

> [!info]- Where the odd names come from
> - **`/etc`** originally meant "et cetera": everything that didn't fit elsewhere. It became the config directory; the backronym "Editable Text Configuration" is sometimes used.
> - **`/usr`** originally held **user** home directories on early Unix. When `/` ran out of disk space, system binaries spilled into `/usr/bin`, which is where the `/bin` vs. `/usr/bin` split came from. The "Unix System Resources" meaning is a later backronym. Modern distros have **merged** them again ("usrmerge"), so `/bin` is just a symlink to `/usr/bin`.

> [!warning] Filesystem gotchas
> - **"Filesystem" means two things.** The *hierarchy* (the directory layout above) vs. the *filesystem type* (ext4, btrfs, xfs, FAT32, NTFS), i.e. how data is stored on one partition. Context tells you which.
> - **`/root` is not `/`.** "The root directory" is `/`; `/root` is the root *user's* home.
> - **Don't put your own files in `/usr/bin`.** That's the package manager's territory and your file can be overwritten or cause conflicts. Use `/usr/local/bin` (all users) or `~/.local/bin` (just you).
> - **`/tmp` is not a safe place to keep work.** It's often cleared at every boot (and on many distros it's RAM-backed, so it's limited in size).
> - **Changes in `/proc` and `/sys` aren't saved** to disk, and editing them requires care. Some writes change kernel behaviour **immediately** (e.g. `/proc/sys/...`). For persistent kernel settings, use `/etc/sysctl.d/`.
> - **NixOS doesn't follow the FHS.** Software lives in `/nix/store/<hash>-name/`, so random precompiled binaries downloaded from the web often don't run there without extra tooling.

## Putting It Together: The Boot Sequence

1. **Firmware** (UEFI/BIOS) initialises hardware and finds a boot entry.
2. The **[[#Bootloader|bootloader]]** (GRUB) shows the menu and loads the kernel + initramfs with parameters.
3. The **[[#Kernel|kernel]]** starts, detects hardware, loads drivers, uses the initramfs to mount the real root filesystem.
4. The kernel starts **PID 1**, the **[[#Init System|init system]]** (systemd).
5. systemd mounts filesystems from `/etc/fstab`, starts services in parallel, and reaches its target.
6. Text login (**getty** on a TTY) or graphical login (**display manager**: GDM/SDDM).
7. After login: your **[[#Core Utilities and the Shell|shell]]**, or a **[[#Display Server|display server]]** + **[[#Desktop Environment and Window Manager|desktop environment]]** session.

```bash
systemd-analyze            # how long the boot took (firmware, loader, kernel, userspace)
systemd-analyze blame      # which services were slowest
```

## Common Mistakes

> [!warning] Common Mistakes
> - Editing generated files (`grub.cfg`) or package-owned files (`/usr/lib/systemd/system/*.service`) instead of their override locations.
> - `systemctl start` without `enable` (or the reverse), then being surprised after a reboot.
> - Expecting a kernel update to apply without rebooting.
> - Confusing the terminal, the shell and the console.
> - Using `echo $SHELL` to find the current shell (it shows the *login* shell).
> - Writing `#!/bin/sh` and then using bash features.
> - Installing Python packages system-wide with `sudo pip`.
> - Storing important files in `/tmp`.
> - Treating Wayland-incompatible X11 tools as "broken" instead of looking for the Wayland equivalent.

## Practice

**1.** You changed the GRUB timeout by editing `/boot/grub/grub.cfg`. It worked, but after the next kernel update the timeout was back to the old value. Why, and what's the right way?

> [!success]- Solution
> `grub.cfg` is **generated**: every kernel update regenerates it from `/etc/default/grub` and `/etc/grub.d/`, overwriting manual edits. Set `GRUB_TIMEOUT=` in `/etc/default/grub`, then run `sudo update-grub` (Debian/Ubuntu) or the `grub2-mkconfig`/`grub-mkconfig` equivalent.

**2.** You ran `sudo systemctl start nginx` and the site works. After a reboot it's down. What did you forget?

> [!success]- Solution
> `start` only starts it for the current boot. You also need `sudo systemctl enable nginx` (or `enable --now` to do both at once). Check with `systemctl is-enabled nginx`.

**3.** You wrote a script `backup` that all users should be able to run by name. Where should it go?

> [!success]- Solution
> `/usr/local/bin/backup` (and `sudo chmod +x` it). `/usr/local/bin` is on everyone's `PATH` and is reserved for locally installed software, so the package manager never touches it. If only *you* need it: `~/.local/bin/`. Avoid `/usr/bin`.

**4.** `echo $SHELL` prints `/bin/bash`, but you're sure you're in zsh. Who's right?

> [!success]- Solution
> Probably you. `$SHELL` holds your **login shell** (from `/etc/passwd`) and isn't updated when you start another shell by typing `zsh`. Check the actual running shell with `ps -p $$` (or `echo $0`).

**5.** Which layers of the stack are typically **missing** on a cloud web server?

> [!success]- Solution
> The **display server**, **desktop environment/window manager** and **display manager**. Servers are managed over SSH in a shell. Kernel, bootloader, init, libraries, core utilities, shell and package manager are all still there.

**6.** After `sudo apt upgrade`, `uname -r` still shows the old kernel version. Did the upgrade fail?

> [!success]- Solution
> No. The new kernel is installed in `/boot`, but the **running** kernel stays in memory until you **reboot**. `ls /boot` shows the new `vmlinuz-*` file. On Debian/Ubuntu, `/var/run/reboot-required` exists when a reboot is pending.

**7.** Is `/proc/cpuinfo` a file on your disk? How big is it?

> [!success]- Solution
> Not on disk. `/proc` is a **virtual filesystem** generated by the kernel on the fly. `ls -l /proc/cpuinfo` reports a size of **0**, yet `cat` prints many lines, because the content is produced when read. See [[05 - The Unix Philosophy#Everything Is a File|Everything Is a File]].

## Related

- [[00 - Index]]
- [[01 - What is Linux]]: kernel vs. distribution
- [[02 - Distributions Overview]]: how distros choose between these components
- [[04 - Essential Commands]]: using the core utilities, package managers and systemd day to day
- [[05 - The Unix Philosophy]]: why the core utilities are small and composable
