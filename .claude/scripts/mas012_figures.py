"""Generate the SVG figures for Public/Uni/ΜΑΣ012.

Run:  python mas012_figures.py            (all figures)
      python mas012_figures.py c2-04      (only names starting with the prefix)

Output: <chapter>/99 - Σχήματα/<name>.svg, embedded in the notes as ![[<name>.svg]].
Palette: slots 1-4 of the validated dataviz reference palette (light mode),
on a white surface so the figures read the same in light and dark site themes.
"""
import os
import sys

import matplotlib as mpl

mpl.use("svg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

BASE = r"C:\Users\demet\Documents\Obsidian Vault\Public\Uni\ΜΑΣ012"
CHAPTERS = {
    "c1": "01 - Εισαγωγή",
    "c2": "02 - Συναρτήσεις",
    "c3": "03 - Όρια και Συνέχεια",
    "c4": "04 - Παράγωγος",
}
FIG_DIR = "99 - Σχήματα"

# palette ---------------------------------------------------------------
C1, C2, C3, C4 = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e9e8e3"
PI = np.pi

mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "mathtext.fontset": "cm",
    "font.size": 10,
    "axes.edgecolor": INK2,
    "axes.labelcolor": INK,
    "axes.titlesize": 10.5,
    "axes.titlecolor": INK,
    "axes.titlepad": 10,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "text.color": INK,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "svg.fonttype": "path",
    "svg.hashsalt": "mas012",
    "lines.linewidth": 2,
    "lines.solid_capstyle": "round",
    "legend.frameon": False,
    "legend.fontsize": 9,
    "legend.handlelength": 1.8,
})

REGISTRY = []


def figure(name):
    def deco(fn):
        REGISTRY.append((name, fn))
        return fn
    return deco


def save(fig, name):
    folder = os.path.join(BASE, CHAPTERS[name[:2]], FIG_DIR)
    os.makedirs(folder, exist_ok=True)
    fig.savefig(os.path.join(folder, name + ".svg"), format="svg",
                bbox_inches="tight", pad_inches=0.1, metadata={"Date": None})
    preview = os.environ.get("MAS012_PREVIEW")
    if preview:  # PNG copies for visual review only
        os.makedirs(preview, exist_ok=True)
        fig.savefig(os.path.join(preview, name + ".png"), dpi=110, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


# helpers ---------------------------------------------------------------
def maxes(ax, xlim, ylim, xticks=(), yticks=(), xtl=None, ytl=None,
          equal=False, grid=True, xlabel="$x$", ylabel="$y$"):
    """Math-style axes crossing at the origin (or at the lower-left edge)."""
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    if equal:
        ax.set_aspect("equal")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    x0 = 0 if xlim[0] <= 0 <= xlim[1] else xlim[0]
    y0 = 0 if ylim[0] <= 0 <= ylim[1] else ylim[0]
    ax.spines["left"].set_position(("data", x0))
    ax.spines["bottom"].set_position(("data", y0))
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(0.9)
        ax.spines[s].set_zorder(1.5)
    ax.plot(1, y0, ">", color=INK2, ms=4.5, transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(x0, 1, "^", color=INK2, ms=4.5, transform=ax.get_xaxis_transform(), clip_on=False)
    if xlabel:
        ax.text(1.012, y0, xlabel, transform=ax.get_yaxis_transform(), ha="left", va="center")
    if ylabel:
        ax.annotate(ylabel, xy=(x0, 1), xycoords=ax.get_xaxis_transform(), xytext=(6, -2),
                    textcoords="offset points", ha="left", va="top")
    ax.set_xticks(list(xticks))
    ax.set_yticks(list(yticks))
    if xtl is not None:
        ax.set_xticklabels(xtl)
    if ytl is not None:
        ax.set_yticklabels(ytl)
    ax.tick_params(length=3, width=0.8, pad=2)
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_bbox(dict(facecolor="white", edgecolor="none", pad=0.6, alpha=0.85))
    if grid:
        for v in xticks:
            ax.axvline(v, color=GRID, lw=0.7, zorder=0)
        for v in yticks:
            ax.axhline(v, color=GRID, lw=0.7, zorder=0)
    return ax


def curve(ax, x, y, color=C1, label=None, jump=None, **kw):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    if jump is not None:
        bad = np.abs(np.deftrightarrow(y)) > jump
        y = y.copy()
        y[1:][bad] = np.nan
    kw.setdefault("lw", 2)
    return ax.plot(x, y, color=color, label=label, **kw)


def dot(ax, x, y, open_=False, color=C1, ms=6.5, z=6, label=None):
    ax.plot([x], [y], "o", ms=ms, mfc="white" if open_ else color, mec=color,
            mew=1.7, zorder=z, clip_on=False, label=label)


def vline(ax, x, color=MUTED, ls=(0, (4, 3)), lw=1.1, **kw):
    ax.axvline(x, color=color, ls=ls, lw=lw, zorder=1, **kw)


def hline(ax, y, color=MUTED, ls=(0, (4, 3)), lw=1.1, **kw):
    ax.axhline(y, color=color, ls=ls, lw=lw, zorder=1, **kw)


def seg(ax, p, q, color=MUTED, ls=(0, (2, 2)), lw=1.1, **kw):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=color, ls=ls, lw=lw, **kw)


def note(ax, xy, text, xytext, ha="left", va="center", fs=9, color=INK2):
    ax.annotate(text, xy=xy, xytext=xytext, ha=ha, va=va, fontsize=fs, color=color,
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.9,
                                shrinkA=2, shrinkB=4, mutation_scale=8))


def label(ax, x, y, text, ha="left", va="center", fs=9.5, color=INK, **kw):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs, color=color, **kw)


def pi_ticks(lo, hi, step=0.5):
    """Ticks at multiples of step*pi with nice labels."""
    names = {0: "0"}
    out_v, out_l = [], []
    k = int(np.ceil(lo / (step * PI) - 1e-9))
    while k * step * PI <= hi + 1e-9:
        v = k * step
        from fractions import Fraction
        f = Fraction(v).limit_denominator(4)
        if f == 0:
            s = names[0]
        else:
            n, d = f.numerator, f.denominator
            sign = "-" if n < 0 else ""
            n = abs(n)
            num = r"\pi" if n == 1 else rf"{n}\pi"
            s = rf"${sign}{num}$" if d == 1 else rf"${sign}\frac{{{num}}}{{{d}}}$"
        out_v.append(v * PI)
        out_l.append(s)
        k += 1
    return out_v, out_l


def numberline(ax, y, x0, x1, color=MUTED):
    ax.plot([x0, x1], [y, y], color=color, lw=0.9, zorder=1)
    ax.plot([x1], [y], ">", color=color, ms=4, zorder=1)


def interval(ax, y, a, b, a_open, b_open, color, lw=4.5, a_inf=False, b_inf=False):
    ax.plot([a, b], [y, y], color=color, lw=lw, solid_capstyle="butt", zorder=3)
    if a_inf:
        ax.plot([a], [y], "<", color=color, ms=7, zorder=3)
    else:
        dot(ax, a, y, a_open, color)
    if b_inf:
        ax.plot([b], [y], ">", color=color, ms=7, zorder=3)
    else:
        dot(ax, b, y, b_open, color)


def right_angle(ax, p, u, v, s, color=INK2):
    p, u, v = map(np.asarray, (p, u, v))
    u = u / np.linalg.norm(u) * s
    v = v / np.linalg.norm(v) * s
    pts = np.array([p + u, p + u + v, p + v])
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=1)


def arc(ax, r, t0, t1, center=(0, 0), color=INK2, lw=1.2, arrow=True):
    t = np.linspace(t0, t1, 60)
    ax.plot(center[0] + r * np.cos(t), center[1] + r * np.sin(t), color=color, lw=lw)
    if arrow:
        ax.annotate("", xy=(center[0] + r * np.cos(t1), center[1] + r * np.sin(t1)),
                    xytext=(center[0] + r * np.cos(t[-4]), center[1] + r * np.sin(t[-4])),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=8))


def X(a, b, n=1200):
    return np.linspace(a, b, n)


# =======================================================================
# Chapter 1 — Εισαγωγή
# =======================================================================
@figure("c1-01-intervals")
def _():
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    rows = [
        ("$[1, 4]$", [(1, 4, False, False)], C1),
        ("$(2, 5)$", [(2, 5, True, True)], C2),
        (r"$[1,4] \cup (2,5) = [1, 5)$", [(1, 5, False, True)], C3),
        (r"$[1,4] \cap (2,5) = (2, 4]$", [(2, 4, True, False)], C4),
        (r"$(0,2) \cup (2,5) \neq (0,5)$", [(0, 2, True, True), (2, 5, True, True)], C1),
    ]
    ax.set_xlim(-0.7, 5.8)
    ax.set_ylim(-0.9, 4.5)
    ax.axis("off")
    for k in range(6):
        ax.plot([k, k], [-0.3, 4.3], color=GRID, lw=0.8, zorder=0)
        label(ax, k, -0.6, str(k), ha="center", color=INK2, fs=9)
    for i, (lab, segs, c) in enumerate(rows):
        y = 4 - i
        numberline(ax, y, -0.6, 5.6)
        label(ax, -0.8, y, lab, ha="right")
        for a, b, ao, bo in segs:
            interval(ax, y, a, b, ao, bo, c)
    save(fig, "c1-01-intervals")


@figure("c1-01-sign-chart")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.5))
    x = X(-3, 3)
    ax = axs[0]
    maxes(ax, (-3.1, 3.1), (-6.5, 6.5), xticks=[-2, 0, 2], yticks=[-4, 4])
    y = x**3 - 4 * x
    ax.fill_between(x, y, 0, where=y <= 0, color=C2, alpha=0.13, lw=0)
    curve(ax, x, y, C1, label="$y = x^3 - 4x$")
    interval(ax, 0, -3.05, -2, False, False, C2, a_inf=True)
    interval(ax, 0, 0, 2, False, False, C2)
    ax.plot([], [], color=C2, lw=4.5, label=r"λύση: $y \leq 0$")
    ax.legend(loc="upper left")
    ax.set_title(r"$x^3 \leq 4x \Leftrightarrow x \in (-\infty, -2] \cup [0, 2]$", fontsize=10)

    ax = axs[1]
    maxes(ax, (-3.1, 3.1), (-6.5, 8.5), xticks=[-2, 1], yticks=[-4, 4])
    y = (x - 1) ** 2 * (x + 2)
    ax.fill_between(x, y, 0, where=y <= 0, color=C2, alpha=0.13, lw=0)
    curve(ax, x, y, C1, label="$y = (x-1)^2(x+2)$")
    interval(ax, 0, -3.05, -2, False, True, C2, a_inf=True)
    dot(ax, 1, 0, False, INK2, ms=5.5)
    note(ax, (1, 0.1), "διπλή ρίζα: η καμπύλη\nαγγίζει, δεν αλλάζει πρόσημο", (0.15, -4.6), ha="left")
    ax.legend(loc="upper left")
    ax.set_title(r"$(x-1)^2(x+2) < 0 \Leftrightarrow x \in (-\infty, -2)$", fontsize=10)
    fig.tight_layout(w_pad=3)
    save(fig, "c1-01-sign-chart")


@figure("c1-02-neighborhood")
def _():
    fig, ax = plt.subplots(figsize=(6.2, 1.9))
    ax.set_xlim(-2.8, 2.6)
    ax.set_ylim(-0.75, 1.75)
    ax.axis("off")
    for y, lab, hole in [(1.2, r"$|x - a| < \delta$", False), (0, r"$0 < |x - a| < \delta$", True)]:
        numberline(ax, y, -2.1, 2.3)
        interval(ax, y, -1, 1, True, True, C1)
        if hole:
            dot(ax, 0, y, True, C1)
        else:
            dot(ax, 0, y, False, INK2, ms=4.5)
        label(ax, -2.25, y, lab, ha="right")
    for xv, t in [(-1, r"$a-\delta$"), (0, "$a$"), (1, r"$a+\delta$")]:
        label(ax, xv, -0.45, t, ha="center", color=INK2)
    ax.annotate("", xy=(1, 1.55), xytext=(0, 1.55),
                arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.9, mutation_scale=8))
    label(ax, 0.5, 1.66, r"$\delta$", ha="center", va="bottom", color=INK2)
    save(fig, "c1-02-neighborhood")


@figure("c1-02-sum-abs")
def _():
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    x = X(-4.6, 3.6)
    maxes(ax, (-4.7, 3.8), (-0.2, 8), xticks=[-3, -2, 1, 2], yticks=[2, 3, 5])
    curve(ax, x, np.abs(x - 1) + np.abs(x + 2), C1, label=r"$y = |x-1| + |x+2|$")
    ax.plot([-4.7, 3.8], [5, 5], color=C2, lw=1.4, ls=(0, (5, 3)), label="$y = 5$: δύο λύσεις")
    ax.plot([-4.7, 3.8], [3, 3], color=C3, lw=1.4, ls=(0, (5, 3)), label=r"$y = 3$: όλο το $[-2, 1]$")
    ax.plot([-2, 1], [3, 3], color=C3, lw=4.5, solid_capstyle="butt", zorder=4)
    ax.plot([-4.7, 3.8], [2, 2], color=C4, lw=1.4, ls=(0, (1.5, 2.5)), label="$y = 2$: καμία λύση")
    dot(ax, -3, 5, False, C2)
    dot(ax, 2, 5, False, C2)
    ax.legend(loc="upper center", ncol=2, fontsize=8.5, bbox_to_anchor=(0.5, -0.1))
    save(fig, "c1-02-sum-abs")


@figure("c1-03-polar")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(8.4, 4.0))
    ax = axs[0]
    maxes(ax, (-2.6, 2.7), (-2.4, 2.6), xticks=[-2, -1, 1, 2], yticks=[-2, -1, 1, 2], equal=True)
    t = PI / 3
    P = (2 * np.cos(t), 2 * np.sin(t))
    Q = (-P[0], -P[1])
    ax.plot([0, 2.7], [0, 0], color=INK, lw=2.2, zorder=2)
    seg(ax, Q, (2.6 * np.cos(t), 2.6 * np.sin(t)), MUTED, lw=1)
    ax.plot([0, P[0]], [0, P[1]], color=C1, lw=2.2)
    ax.plot([0, Q[0]], [0, Q[1]], color=C2, lw=2.2, ls=(0, (4, 2.5)))
    arc(ax, 0.55, 0, t)
    label(ax, 0.62, 0.32, r"$\theta = \frac{\pi}{3}$", fs=10)
    dot(ax, *P, color=C1)
    dot(ax, *Q, color=C2)
    label(ax, P[0] + 0.12, P[1], r"$(2, \frac{\pi}{3})$")
    label(ax, Q[0] - 0.12, Q[1] - 0.05, r"$(-2, \frac{\pi}{3})$", ha="right")
    label(ax, 0.68, 1.2, "$r = 2$", ha="right", color=INK2, fs=9)
    label(ax, 1.4, -0.28, "πολικός άξονας", fs=8.5, color=INK2)
    ax.set_title(r"αρνητικό $r$: αντίθετη κατεύθυνση", fontsize=10)

    ax = axs[1]
    maxes(ax, (-1.8, 1.8), (-1.7, 1.8), xticks=[-1, 1], yticks=[-1, 1], equal=True)
    seg(ax, (0, 0), (1, 1), C2, ls=(0, (4, 2.5)), lw=1.8)
    dot(ax, 1, 1, True, C2)
    label(ax, 1.05, 1.22, r"$\tan^{-1}(1) = \frac{\pi}{4}$" + "\nδίνει αυτό (λάθος)", ha="center", fs=8.5, color=INK2)
    ax.plot([0, -1], [0, -1], color=C1, lw=2.2)
    dot(ax, -1, -1, False, C1)
    arc(ax, 0.42, 0, 5 * PI / 4, color=C1)
    label(ax, -0.05, 0.55, r"$\theta = \frac{5\pi}{4}$", ha="right", fs=10)
    label(ax, -1.08, -1.2, "$(-1, -1)$", ha="right")
    ax.set_title("παγίδα τεταρτημορίου: ίδιο $y/x$", fontsize=10)
    fig.tight_layout(w_pad=3)
    save(fig, "c1-03-polar")


@figure("c1-03-polar-circles")
def _():
    fig, ax = plt.subplots(figsize=(4.6, 4.6))
    maxes(ax, (-2.7, 4.8), (-2.7, 4.8), xticks=[-2, 2, 4], yticks=[-2, 2, 4], equal=True)
    t = X(0, 2 * PI, 400)
    ax.plot(2 * np.cos(t), 2 * np.sin(t), color=C1, label="$r = 2$")
    r = 4 * np.cos(t)
    ax.plot(r * np.cos(t), r * np.sin(t), color=C2, ls=(0, (5, 2.5)), label=r"$r = 4\cos\theta$")
    r = 4 * np.sin(t)
    ax.plot(r * np.cos(t), r * np.sin(t), color=C3, ls=(0, (1.5, 2)), label=r"$r = 4\sin\theta$")
    dot(ax, 2, 0, False, C2, ms=4)
    dot(ax, 0, 2, False, C3, ms=4)
    ax.legend(loc="upper right", fontsize=8.5)
    save(fig, "c1-03-polar-circles")


@figure("c1-04-slopes")
def _():
    fig, axs = plt.subplots(1, 4, figsize=(9.6, 2.6))
    x = X(-2, 2, 50)
    titles = ["$m > 0$: ανεβαίνει", "$m < 0$: κατεβαίνει", "$m = 0$: οριζόντια", "κατακόρυφη: χωρίς κλίση"]
    for ax, ttl, k in zip(axs, titles, range(4)):
        maxes(ax, (-2, 2), (-2, 2), equal=True, grid=False)
        ax.set_title(ttl, fontsize=9.5)
        if k == 0:
            curve(ax, x, 0.7 * x + 0.3, C1)
            ax.plot([-0.8, 1.0], [0.7 * -0.8 + 0.3] * 2, color=C2, lw=1.2)
            ax.plot([1.0, 1.0], [0.7 * -0.8 + 0.3, 0.7 + 0.3], color=C2, lw=1.2)
            label(ax, 0.1, -0.52, r"$\Delta x$", ha="center", va="top", fs=9)
            label(ax, 1.08, 0.2, r"$\Delta y$", fs=9)
        elif k == 1:
            curve(ax, x, -0.8 * x + 0.2, C1)
        elif k == 2:
            curve(ax, x, 0 * x + 1, C1)
        else:
            ax.plot([1, 1], [-2, 2], color=C1)
    fig.tight_layout(w_pad=1.5)
    save(fig, "c1-04-slopes")


@figure("c1-04-circle-tangent")
def _():
    fig, ax = plt.subplots(figsize=(4.8, 4.6))
    maxes(ax, (-6, 9.3), (-6, 8.3), xticks=[-5, 3, 5], yticks=[-5, 4, 5], equal=True)
    t = X(0, 2 * PI, 300)
    ax.plot(5 * np.cos(t), 5 * np.sin(t), color=C1, label=r"$x^2 + y^2 = 25$")
    x = X(-1, 9, 10)
    ax.plot(x, (25 - 3 * x) / 4, color=C2, label=r"εφαπτομένη $3x + 4y = 25$")
    ax.plot([0, 3], [0, 4], color=INK2, lw=1.4, label=r"ακτίνα, κλίση $\frac{4}{3}$")
    right_angle(ax, (3, 4), (-3, -4), (4, -3), 0.55)
    dot(ax, 3, 4, False, INK)
    label(ax, 3.2, 4.35, "$(3, 4)$")
    ax.legend(loc="upper right", fontsize=8.5)
    save(fig, "c1-04-circle-tangent")


@figure("c1-04-parabola-focus")
def _():
    fig, ax = plt.subplots(figsize=(5.4, 3.9))
    maxes(ax, (-5, 5.2), (-2, 6), xticks=[-4, -2, 2, 4], yticks=[-1, 1, 2, 4], equal=True)
    x = X(-4.8, 4.8)
    ax.plot(x, x**2 / 4, color=C1, label=r"$x^2 = 4py$ ($p = 1$)")
    ax.plot([-5, 5.2], [-1, -1], color=C3, label=r"διευθετούσα $y = -p$")
    P = (3, 2.25)
    dot(ax, 0, 1, False, C2, label=r"εστία $F(0, p)$")
    seg(ax, P, (0, 1), C2, ls=(0, (4, 2)), lw=1.4)
    seg(ax, P, (3, -1), C3, ls=(0, (4, 2)), lw=1.4)
    dot(ax, *P, False, INK, ms=5.5)
    dot(ax, 3, -1, False, C3, ms=4.5)
    label(ax, 3.2, 2.35, "$P$")
    label(ax, 1.35, 1.95, "$PF$", ha="center", fs=9, color=INK2)
    label(ax, 3.12, 0.55, "$PD$", fs=9, color=INK2)
    label(ax, 3.2, -1.35, "$D$", fs=9, color=INK2)
    ax.legend(loc="upper center", fontsize=8.5)
    save(fig, "c1-04-parabola-focus")


@figure("c1-04-line-parabola")
def _():
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    maxes(ax, (-2.5, 3.3), (-2, 7), xticks=[-1, 1, 2], yticks=[1, 4])
    x = X(-2.4, 3.2)
    curve(ax, x, x**2, C1, label="$y = x^2$")
    curve(ax, x, x + 2, C2, ls=(0, (5, 2.5)), label="$y = x + 2$: τέμνει σε 2 σημεία")
    curve(ax, x, 2 * x - 1, C3, ls=(0, (1.5, 2)), label="$y = 2x - 1$: εφάπτεται (διπλή ρίζα)")
    dot(ax, -1, 1, False, C2)
    dot(ax, 2, 4, False, C2)
    dot(ax, 1, 1, False, C3)
    ax.legend(loc="upper left", fontsize=8.5)
    save(fig, "c1-04-line-parabola")


# =======================================================================
# Chapter 2 — Συναρτήσεις
# =======================================================================
@figure("c2-01-vertical-line-test")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.3))
    t = X(0, 2 * PI, 300)
    for k, ax in enumerate(axs):
        maxes(ax, (-1.6, 1.6), (-1.5, 1.5), xticks=[-1, 1], yticks=[-1, 1], equal=True)
        ax.axvline(0.5, color=C2, lw=1.4, ls=(0, (5, 2.5)))
        if k == 0:
            ax.plot(np.cos(t), np.sin(t), color=C1)
            dot(ax, 0.5, np.sqrt(0.75), False, C2)
            dot(ax, 0.5, -np.sqrt(0.75), False, C2)
            ax.set_title("$x^2 + y^2 = 1$: 2 σημεία ⇒ όχι συνάρτηση", fontsize=9.5)
        else:
            x = X(-1, 1)
            ax.plot(x, np.sqrt(1 - x**2), color=C1)
            dot(ax, 0.5, np.sqrt(0.75), False, C2)
            ax.set_title(r"$y = \sqrt{1 - x^2}$: 1 σημείο ⇒ συνάρτηση", fontsize=9.5)
    fig.tight_layout(w_pad=2)
    save(fig, "c2-01-vertical-line-test")


@figure("c2-01-hole")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0))
    x = X(-1.2, 4)
    for k, ax in enumerate(axs):
        maxes(ax, (-1.3, 4.2), (-0.5, 6.6), xticks=[2], yticks=[4])
        curve(ax, x, x + 2, C1)
        seg(ax, (2, 0), (2, 4))
        seg(ax, (0, 4), (2, 4))
        if k == 0:
            dot(ax, 2, 4, True, C1)
            ax.set_title(r"$f(x) = \frac{x^2 - 4}{x - 2}$: τρύπα στο $(2, 4)$", fontsize=10)
        else:
            dot(ax, 2, 4, False, C1)
            ax.set_title(r"$g(x) = x + 2$: ορίζεται παντού", fontsize=10)
    fig.tight_layout(w_pad=2)
    save(fig, "c2-01-hole")


@figure("c2-01-abs-piecewise")
def _():
    fig, ax = plt.subplots(figsize=(5.4, 2.8))
    maxes(ax, (-0.3, 8.3), (-3, 3), xticks=[3, 4, 5], yticks=[-2, 2])
    x = X(-0.3, 8.2)
    curve(ax, x, np.abs(x - 5) - np.abs(x - 3), C1, label=r"$f(x) = |x - 5| - |x - 3|$")
    for p in [(3, 2), (5, -2), (4, 0)]:
        dot(ax, *p, False, C1, ms=5)
    ax.legend(loc="upper right")
    save(fig, "c2-01-abs-piecewise")


@figure("c2-01-sign-fn")
def _():
    fig, ax = plt.subplots(figsize=(5.0, 2.6))
    maxes(ax, (-1.2, 5.2), (-1.7, 1.7), xticks=[2], yticks=[-1, 1])
    ax.plot([-1.2, 2], [-1, -1], color=C1)
    ax.plot([2, 5.2], [1, 1], color=C1, label=r"$f(x) = \frac{|x - 2|}{x - 2}$")
    dot(ax, 2, -1, True, C1)
    dot(ax, 2, 1, True, C1)
    note(ax, (2, 0.02), "το $f(2)$ δεν ορίζεται:\nκανένα σημείο εδώ", (2.6, -0.75))
    ax.legend(loc="upper left", bbox_to_anchor=(0.2, 1.0))
    save(fig, "c2-01-sign-fn")


@figure("c2-01-floor")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(8.6, 3.2))
    ax = axs[0]
    maxes(ax, (-2.6, 3.3), (-3.3, 2.6), xticks=[-2, -1, 1, 2, 3], yticks=[-3, -2, 1, 2], equal=True)
    for k in range(-3, 3):
        a, b = max(k, -2.6), k + 1
        ax.plot([a, b], [k, k], color=C1)
        if k >= -2:
            dot(ax, k, k, False, C1, ms=5.5)
        dot(ax, b, k, True, C1, ms=5.5)
    dot(ax, -0.4, -1, False, C2, ms=5)
    note(ax, (-0.4, -1.05), "$[-0.4] = -1$", (-1.6, -2.4), ha="center")
    ax.set_title("$y = [x]$: σκαλοπάτια", fontsize=10)

    ax = axs[1]
    maxes(ax, (-2.6, 3.3), (-0.6, 1.5), xticks=[-2, -1, 1, 2, 3], yticks=[1])
    for k in range(-3, 3):
        a, b = max(k, -2.6), k + 1
        ax.plot([a, b], [a - k, 1], color=C1)
        if k >= -2:
            dot(ax, k, 0, False, C1, ms=5.5)
        dot(ax, b, 1, True, C1, ms=5.5)
    hline(ax, 1)
    ax.set_title("$y = x - [x]$: περιοδική, περίοδος 1", fontsize=10)
    fig.tight_layout(w_pad=3)
    save(fig, "c2-01-floor")


@figure("c2-01-even-odd")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.3))
    x = X(-2.1, 2.1)
    ax = axs[0]
    maxes(ax, (-2.3, 2.3), (-0.6, 4.6), xticks=[-1.5, 1.5], yticks=[], xtl=["$-a$", "$a$"])
    curve(ax, x, x**2, C1, label="$y = x^2$")
    seg(ax, (-1.5, 2.25), (1.5, 2.25), C2, lw=1.4, ls=(0, (4, 2)))
    dot(ax, 1.5, 2.25, False, C2)
    dot(ax, -1.5, 2.25, False, C2)
    label(ax, 0.12, 2.55, "$f(-a) = f(a)$", fs=9)
    ax.set_title("άρτια: συμμετρία ως προς τον άξονα $y$", fontsize=10)
    ax.legend(loc="upper left")
    ax = axs[1]
    maxes(ax, (-2.3, 2.3), (-3.2, 3.2), xticks=[-1.3, 1.3], yticks=[], xtl=["$-a$", "$a$"])
    curve(ax, x, x**3 - x, C1, label="$y = x^3 - x$")
    a = 1.3
    seg(ax, (-a, -(a**3 - a)), (a, a**3 - a), C2, lw=1.4, ls=(0, (4, 2)))
    dot(ax, a, a**3 - a, False, C2)
    dot(ax, -a, -(a**3 - a), False, C2)
    label(ax, 0.2, -1.6, "$f(-a) = -f(a)$", fs=9)
    ax.set_title("περιττή: συμμετρία ως προς την αρχή", fontsize=10)
    ax.legend(loc="upper left")
    fig.tight_layout(w_pad=3)
    save(fig, "c2-01-even-odd")


@figure("c2-01-powers")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.4))
    x = X(-1.7, 1.7)
    styles = [dict(color=C1), dict(color=C2, ls=(0, (5, 2.5))), dict(color=C3, ls=(0, (1.5, 2)))]
    ax = axs[0]
    maxes(ax, (-1.7, 1.7), (-0.4, 2.8), xticks=[-1, 1], yticks=[1])
    for n, st in zip([2, 4, 6], styles):
        curve(ax, x, x**n, label=f"$x^{n}$", **st)
    dot(ax, 1, 1, False, INK, ms=4.5)
    dot(ax, -1, 1, False, INK, ms=4.5)
    ax.set_title("άρτιο $n$: σχήμα «U»", fontsize=10)
    ax.legend(loc="upper center", ncol=3)
    ax = axs[1]
    maxes(ax, (-1.7, 1.7), (-2.8, 2.8), xticks=[-1, 1], yticks=[-1, 1])
    for n, st in zip([1, 3, 5], styles):
        curve(ax, x, x**n, label=f"$x^{n}$" if n > 1 else "$x$", **st)
    dot(ax, 1, 1, False, INK, ms=4.5)
    dot(ax, -1, -1, False, INK, ms=4.5)
    ax.set_title("περιττό $n$: σχήμα «S»", fontsize=10)
    ax.legend(loc="upper left")
    fig.tight_layout(w_pad=3)
    save(fig, "c2-01-powers")


@figure("c2-01-periodic")
def _():
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    xt, xl = pi_ticks(0, 3 * PI, 0.5)
    maxes(ax, (-0.2, 3 * PI + 0.3), (-1.25, 1.55), xticks=xt[1:], xtl=xl[1:], yticks=[-1, 1])
    x = X(-0.2, 3 * PI + 0.2)
    curve(ax, x, np.sin(x), MUTED, lw=1.4, ls=(0, (4, 2.5)), label=r"$\sin x$ (περίοδος $2\pi$)")
    curve(ax, x, np.abs(np.sin(x)), C1, label=r"$|\sin x|$ (περίοδος $\pi$)")
    curve(ax, x, np.sin(x) ** 2, C2, ls=(0, (5, 2.5)), label=r"$\sin^2 x$ (περίοδος $\pi$)")
    ax.annotate("", xy=(2 * PI, 1.3), xytext=(PI, 1.3),
                arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.9, mutation_scale=8))
    label(ax, 1.5 * PI, 1.38, r"$T = \pi$", ha="center", va="bottom", fs=9, color=INK2)
    ax.legend(loc="lower left", ncol=3, fontsize=8.5, bbox_to_anchor=(0, -0.02))
    save(fig, "c2-01-periodic")


@figure("c2-02-transformations")
def _():
    fig, axs = plt.subplots(2, 2, figsize=(8.6, 6.4))
    base = dict(color=MUTED, lw=1.5, ls=(0, (4, 2.5)))
    ax = axs[0, 0]
    maxes(ax, (-3, 4.2), (-0.8, 6), xticks=[2], yticks=[1])
    x = X(-3, 4.2)
    curve(ax, x, x**2, label="$f(x) = x^2$", **base)
    curve(ax, x, (x - 2) ** 2, C1, label="$f(x - 2)$: δεξιά κατά 2")
    curve(ax, x, x**2 + 1, C2, label="$f(x) + 1$: πάνω κατά 1")
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title("μετατοπίσεις", fontsize=10)

    ax = axs[0, 1]
    maxes(ax, (-4.5, 4.5), (-2.5, 2.8), xticks=[-4, 4], yticks=[-2, 2])
    x = X(0, 4.5)
    curve(ax, x, np.sqrt(x), label=r"$f(x) = \sqrt{x}$", **base)
    curve(ax, x, -np.sqrt(x), C1, label=r"$-f(x)$: ως προς τον άξονα $x$")
    curve(ax, -x, np.sqrt(x), C2, label=r"$f(-x)$: ως προς τον άξονα $y$")
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title("ανακλάσεις", fontsize=10)

    ax = axs[1, 0]
    xt, xl = pi_ticks(0, 2 * PI, 0.5)
    maxes(ax, (0, 2 * PI + 0.2), (-2.4, 3.0), xticks=xt[1:], xtl=xl[1:], yticks=[-2, -1, 1, 2])
    x = X(0, 2 * PI + 0.1)
    curve(ax, x, np.sin(x), label=r"$f(x) = \sin x$", **base)
    curve(ax, x, 2 * np.sin(x), C1, label=r"$2f(x)$: κατακόρυφο τέντωμα")
    curve(ax, x, np.sin(2 * x), C2, label=r"$f(2x)$: οριζόντια συμπίεση")
    ax.legend(loc="upper right", fontsize=8.5, ncol=1)
    ax.set_title("τέντωμα και συμπίεση", fontsize=10)

    ax = axs[1, 1]
    maxes(ax, (-3.6, 2.6), (-4, 5), xticks=[-1], yticks=[2])
    x = X(-3.6, 2.6)
    curve(ax, x, x**2, label="$x^2$", **base)
    curve(ax, x, 2 - (x + 1) ** 2, C1, label="$2 - (x + 1)^2$")
    dot(ax, -1, 2, False, C1)
    label(ax, -0.85, 2.45, "κορυφή $(-1, 2)$", fs=9)
    ax.legend(loc="lower right", fontsize=8.5)
    ax.set_title("συνδυασμός (Παράδειγμα 4)", fontsize=10)
    fig.tight_layout(h_pad=2.5, w_pad=3)
    save(fig, "c2-02-transformations")


@figure("c2-02-abs")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.3))
    x = X(-4.2, 4.6)
    f = x**2 - 2 * x - 3
    base = dict(color=MUTED, lw=1.5, ls=(0, (4, 2.5)))
    ax = axs[0]
    maxes(ax, (-4.2, 4.6), (-4.6, 6.5), xticks=[-1, 1, 3], yticks=[-4, 4])
    curve(ax, x, f, label="$f(x) = x^2 - 2x - 3$", **base)
    curve(ax, x, np.abs(f), C1, label="$|f(x)|$")
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title("$|f(x)|$: ό,τι είναι κάτω από τον $x$ ανεβαίνει", fontsize=10)
    ax = axs[1]
    maxes(ax, (-4.2, 4.6), (-4.6, 6.5), xticks=[-3, -1, 1, 3], yticks=[-4, 4])
    curve(ax, x, f, label="$f(x)$", **base)
    curve(ax, x, np.abs(x) ** 2 - 2 * np.abs(x) - 3, C1, label="$f(|x|)$")
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title("$f(|x|)$: το δεξί μισό καθρεφτίζεται αριστερά", fontsize=10)
    fig.tight_layout(w_pad=3)
    save(fig, "c2-02-abs")


@figure("c2-03-hline-test")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.1))
    x = X(-2.6, 2.6)
    ax = axs[0]
    maxes(ax, (-2.7, 2.7), (-1, 6.5), xticks=[-2, 2], yticks=[4])
    curve(ax, x, x**2, C1)
    hline(ax, 4, C2, lw=1.4, ls=(0, (5, 2.5)))
    dot(ax, -2, 4, False, C2)
    dot(ax, 2, 4, False, C2)
    ax.set_title("$x^2$: 2 σημεία ⇒ όχι 1-1", fontsize=10)
    ax = axs[1]
    maxes(ax, (-2.2, 2.2), (-6, 6), xticks=[-1, 1], yticks=[3])
    x = X(-2.2, 2.2)
    curve(ax, x, x**3, C1)
    hline(ax, 3, C2, lw=1.4, ls=(0, (5, 2.5)))
    dot(ax, 3 ** (1 / 3), 3, False, C2)
    ax.set_title("$x^3$: πάντα 1 σημείο ⇒ 1-1", fontsize=10)
    fig.tight_layout(w_pad=2)
    save(fig, "c2-03-hline-test")


@figure("c2-03-reflection")
def _():
    fig, ax = plt.subplots(figsize=(5.0, 4.7))
    maxes(ax, (-3, 7.6), (-1.2, 7.6), xticks=[2, 4, 6], yticks=[2, 4, 6], equal=True)
    ax.plot([-1.2, 7.4], [-1.2, 7.4], color=INK2, lw=1, ls=(0, (1.5, 2)), label="$y = x$")
    x = X(2 / 3, 7.4)
    curve(ax, x, np.sqrt(3 * x - 2), C1, label=r"$f(x) = \sqrt{3x - 2}$")
    x = X(0, np.sqrt(3 * 7.4 - 2))
    curve(ax, x, (x**2 + 2) / 3, C2, label=r"$f^{-1}(x) = \frac{x^2 + 2}{3},\ x \geq 0$")
    x = X(-3, 0)
    curve(ax, x, (x**2 + 2) / 3, MUTED, lw=1.4, ls=(0, (4, 2.5)), label="όχι μέρος της $f^{-1}$")
    dot(ax, 2 / 3, 0, False, C1, ms=5)
    dot(ax, 0, 2 / 3, False, C2, ms=5)
    dot(ax, 6, 4, False, C1, ms=5)
    dot(ax, 4, 6, False, C2, ms=5)
    seg(ax, (6, 4), (4, 6), INK2)
    label(ax, 6.15, 3.75, "$(6, 4)$", fs=9)
    label(ax, 3.85, 6.25, "$(4, 6)$", ha="right", fs=9)
    ax.legend(loc="upper left", fontsize=8.5, bbox_to_anchor=(-0.02, 1.0))
    save(fig, "c2-03-reflection")


@figure("c2-03-restrict")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.9))
    for k, ax in enumerate(axs):
        maxes(ax, (-2.6, 4.4), (-2.6, 4.4), xticks=[-2, 2, 4], yticks=[-2, 2, 4], equal=True)
        ax.plot([-2.6, 4.2], [-2.6, 4.2], color=INK2, lw=1, ls=(0, (1.5, 2)))
        xa = X(-2.1, 2.1)
        curve(ax, xa, xa**2, MUTED, lw=1.3, ls=(0, (4, 2.5)))
        xs = X(0, 2.1) if k == 0 else X(-2.1, 0)
        curve(ax, xs, xs**2, C1, label="$x^2$, $x \\geq 0$" if k == 0 else "$x^2$, $x \\leq 0$")
        xr = X(0, 4.4)
        if k == 0:
            curve(ax, xr, np.sqrt(xr), C2, label=r"$f^{-1}(x) = \sqrt{x}$")
            ax.set_title(r"περιορισμός στο $[0, \infty)$", fontsize=10)
        else:
            curve(ax, xr, -np.sqrt(xr), C2, label=r"$f^{-1}(x) = -\sqrt{x}$")
            ax.set_title(r"περιορισμός στο $(-\infty, 0]$", fontsize=10)
        ax.legend(loc="lower right", fontsize=8.5)
    fig.tight_layout(w_pad=3)
    save(fig, "c2-03-restrict")


@figure("c2-04-unit-circle")
def _():
    fig, ax = plt.subplots(figsize=(5.0, 4.9))
    maxes(ax, (-1.55, 1.95), (-1.5, 1.75), xticks=[-1, 1], yticks=[-1, 1], equal=True)
    t = X(0, 2 * PI, 300)
    ax.plot(np.cos(t), np.sin(t), color=INK2, lw=1.3)
    th = 0.85
    c, s, tn = np.cos(th), np.sin(th), np.tan(th)
    ax.plot([1, 1], [-1.5, 1.75], color=MUTED, lw=1, ls=(0, (4, 2.5)))
    seg(ax, (0, 0), (1, tn), MUTED, lw=1)
    ax.plot([0, c], [0, s], color=INK, lw=1.6)
    ax.plot([0, c], [0, 0], color=C1, lw=3, solid_capstyle="butt", label=r"$\cos\theta$")
    ax.plot([c, c], [0, s], color=C2, lw=3, solid_capstyle="butt", label=r"$\sin\theta$")
    ax.plot([1, 1], [0, tn], color=C3, lw=3, solid_capstyle="butt", label=r"$\tan\theta$")
    arc(ax, 0.3, 0, th)
    label(ax, 0.33, 0.13, r"$\theta$", fs=10)
    dot(ax, c, s, False, INK, ms=5.5)
    label(ax, c - 0.06, s + 0.12, r"$P(\cos\theta, \sin\theta)$", ha="center", fs=9)
    dot(ax, 1, tn, False, C3, ms=5)
    label(ax, 1.06, tn + 0.08, "$T$", fs=9)
    for (xq, yq, txt) in [(0.95, 1.55, "Ι: όλες +"), (-0.95, 1.55, r"ΙΙ: $\sin$ +"),
                          (-0.95, -1.35, r"ΙΙΙ: $\tan$ +"), (0.95, -1.35, r"IV: $\cos$ +")]:
        label(ax, xq, yq, txt, ha="center", fs=8.5, color=INK2)
    ax.legend(loc="center left", fontsize=8.5, bbox_to_anchor=(0.0, 0.33))
    save(fig, "c2-04-unit-circle")


@figure("c2-04-graphs")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(10.2, 3.2), gridspec_kw={"width_ratios": [1.45, 1]})
    ax = axs[0]
    xt, xl = pi_ticks(-2 * PI, 2 * PI, 0.5)
    maxes(ax, (-2 * PI - 0.2, 2 * PI + 0.3), (-1.4, 1.6), xticks=xt, xtl=xl, yticks=[-1, 1])
    ax.tick_params(axis="x", labelsize=7.5)
    x = X(-2 * PI - 0.2, 2 * PI + 0.2)
    curve(ax, x, np.sin(x), C1, label=r"$\sin x$")
    curve(ax, x, np.cos(x), C2, ls=(0, (5, 2.5)), label=r"$\cos x$")
    ax.legend(loc="upper right", ncol=2, bbox_to_anchor=(1.0, 1.08))
    ax.set_title(r"$\sin$, $\cos$: περίοδος $2\pi$, τιμές στο $[-1, 1]$", fontsize=10, loc="left")
    ax = axs[1]
    xt, xl = pi_ticks(-1.5 * PI, 1.5 * PI, 0.5)
    maxes(ax, (-1.5 * PI - 0.1, 1.5 * PI + 0.2), (-4.2, 4.2), xticks=xt, xtl=xl, yticks=[-1, 1])
    ax.tick_params(axis="x", labelsize=7.5)
    for a in (-1.5, -0.5, 0.5, 1.5):
        vline(ax, a * PI)
    for k in (-2, -1, 0, 1):
        x = X(k * PI - PI / 2 + 0.02, k * PI + PI / 2 - 0.02, 400)
        x = x[(x > -1.5 * PI) & (x < 1.5 * PI)]
        curve(ax, x, np.tan(x), C1, label=r"$\tan x$" if k == 0 else None)
    ax.legend(loc="upper left")
    ax.set_title(r"$\tan$: περίοδος $\pi$, ασύμπτωτες $x = \frac{\pi}{2} + k\pi$", fontsize=10, loc="left")
    fig.tight_layout(w_pad=2.5)
    save(fig, "c2-04-graphs")


@figure("c2-04-inverse-trig")
def _():
    fig, axs = plt.subplots(1, 3, figsize=(10.4, 3.9))
    idl = dict(color=INK2, lw=1, ls=(0, (1.5, 2)))
    ax = axs[0]
    maxes(ax, (-1.9, 1.9), (-1.9, 1.9), xticks=[-1, 1], yticks=[-PI / 2, PI / 2],
          ytl=[r"$-\frac{\pi}{2}$", r"$\frac{\pi}{2}$"], equal=True)
    ax.plot([-1.9, 1.9], [-1.9, 1.9], **idl)
    x = X(-PI / 2, PI / 2)
    curve(ax, x, np.sin(x), C2, lw=1.6, ls=(0, (4, 2)), label=r"$\sin x$, $|x| \leq \frac{\pi}{2}$")
    x = X(-1, 1)
    curve(ax, x, np.arcsin(x), C1, label=r"$\sin^{-1}x$")
    dot(ax, -1, -PI / 2, False, C1, ms=4.5)
    dot(ax, 1, PI / 2, False, C1, ms=4.5)
    ax.legend(loc="upper left", fontsize=8.5)

    ax = axs[1]
    maxes(ax, (-1.6, 3.5), (-1.6, 3.5), xticks=[-1, 1, PI], xtl=["$-1$", "$1$", r"$\pi$"],
          yticks=[PI / 2, PI], ytl=[r"$\frac{\pi}{2}$", r"$\pi$"], equal=True)
    ax.plot([-1.6, 3.4], [-1.6, 3.4], **idl)
    x = X(0, PI)
    curve(ax, x, np.cos(x), C2, lw=1.6, ls=(0, (4, 2)), label=r"$\cos x$, $0 \leq x \leq \pi$")
    x = X(-1, 1)
    curve(ax, x, np.arccos(x), C1, label=r"$\cos^{-1}x$")
    dot(ax, -1, PI, False, C1, ms=4.5)
    dot(ax, 1, 0, False, C1, ms=4.5)
    ax.legend(loc="upper right", fontsize=8.5)

    ax = axs[2]
    maxes(ax, (-4.2, 4.2), (-4.2, 4.2), xticks=[-2, 2], yticks=[-PI / 2, PI / 2],
          ytl=[r"$-\frac{\pi}{2}$", r"$\frac{\pi}{2}$"], equal=True)
    ax.plot([-4.2, 4.2], [-4.2, 4.2], **idl)
    hline(ax, PI / 2)
    hline(ax, -PI / 2)
    x = X(-1.33, 1.33)
    curve(ax, x, np.tan(x), C2, lw=1.6, ls=(0, (4, 2)), label=r"$\tan x$, $|x| < \frac{\pi}{2}$")
    x = X(-4.2, 4.2)
    curve(ax, x, np.arctan(x), C1, label=r"$\tan^{-1}x$")
    ax.legend(loc="upper left", fontsize=8.5)
    fig.tight_layout(w_pad=2)
    save(fig, "c2-04-inverse-trig")


@figure("c2-04-arcsin-sin")
def _():
    fig, ax = plt.subplots(figsize=(7.4, 3.0))
    xt, xl = pi_ticks(-2 * PI, 2 * PI, 0.5)
    maxes(ax, (-2 * PI - 0.2, 2 * PI + 0.3), (-2.3, 2.3), xticks=xt, xtl=xl,
          yticks=[-PI / 2, PI / 2], ytl=[r"$-\frac{\pi}{2}$", r"$\frac{\pi}{2}$"])
    ax.tick_params(axis="x", labelsize=7.5)
    ax.axvspan(-PI / 2, PI / 2, color=C3, alpha=0.1, lw=0)
    x = X(-2 * PI - 0.2, 2 * PI + 0.2, 2000)
    curve(ax, x, x, C2, lw=1.4, ls=(0, (5, 2.5)), label="$y = x$")
    curve(ax, x, np.arcsin(np.sin(x)), C1, label=r"$y = \sin^{-1}(\sin x)$")
    dot(ax, 5 * PI / 6, PI / 6, False, C1, ms=5)
    note(ax, (5 * PI / 6, PI / 6), r"$\sin^{-1}(\sin\frac{5\pi}{6}) = \frac{\pi}{6}$", (3.6, 1.75), fs=8.5)
    label(ax, 0, -2.05, r"ίσες μόνο στο $[-\frac{\pi}{2}, \frac{\pi}{2}]$", ha="center", fs=8.5, color=INK2)
    ax.legend(loc="upper left", fontsize=8.5)
    save(fig, "c2-04-arcsin-sin")


@figure("c2-05-exp")
def _():
    fig, ax = plt.subplots(figsize=(5.4, 3.5))
    maxes(ax, (-3, 3), (-0.4, 6.2), xticks=[-2, -1, 1, 2], yticks=[1, 2, 4])
    x = X(-3, 3)
    curve(ax, x, 2**x, C1, label="$2^x$")
    curve(ax, x, np.exp(x), C2, ls=(0, (5, 2.5)), label="$e^x$")
    curve(ax, x, 0.5**x, C3, ls=(0, (1.5, 2)), label=r"$(\frac{1}{2})^x$")
    dot(ax, 0, 1, False, INK, ms=5)
    label(ax, 0.12, 0.72, "$(0, 1)$", fs=9)
    label(ax, 2.95, 0.25, "ασύμπτωτη $y = 0$", ha="right", fs=8.5, color=INK2)
    ax.legend(loc="upper center")
    save(fig, "c2-05-exp")


@figure("c2-05-exp-ln")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(8.6, 4.0))
    ax = axs[0]
    maxes(ax, (-3, 4.6), (-3, 4.6), xticks=[1, 2, 3], yticks=[1, 2, 3], equal=True)
    ax.plot([-3, 4.5], [-3, 4.5], color=INK2, lw=1, ls=(0, (1.5, 2)), label="$y = x$")
    x = X(-3, 1.5)
    curve(ax, x, np.exp(x), C1, label="$e^x$")
    x = X(0.04, 4.6)
    curve(ax, x, np.log(x), C2, ls=(0, (5, 2.5)), label=r"$\ln x$")
    dot(ax, 0, 1, False, C1, ms=5)
    dot(ax, 1, 0, False, C2, ms=5)
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title("αντίστροφες: συμμετρικές ως προς $y = x$", fontsize=10)
    ax = axs[1]
    maxes(ax, (-3, 3), (-0.4, 6.2), xticks=[-1, 1], yticks=[1])
    x = X(-3, 3)
    curve(ax, x, np.exp(x), C1, label="$e^x$")
    curve(ax, x, np.exp(-x), C2, ls=(0, (5, 2.5)), label="$e^{-x}$")
    dot(ax, 0, 1, False, INK, ms=5)
    ax.legend(loc="upper center", ncol=2)
    ax.set_title("$e^x$, $e^{-x}$: συμμετρικές ως προς τον άξονα $y$", fontsize=10)
    fig.tight_layout(w_pad=3)
    save(fig, "c2-05-exp-ln")


@figure("c2-06-hyperbolic")
def _():
    fig, axs = plt.subplots(1, 3, figsize=(10.4, 3.4))
    half = dict(lw=1.3, ls=(0, (4, 2)))
    x = X(-2.6, 2.6)
    ax = axs[0]
    maxes(ax, (-2.7, 2.7), (-0.5, 5.5), xticks=[-2, 2], yticks=[1])
    curve(ax, x, np.cosh(x), C1, label=r"$\cosh x$")
    curve(ax, x, np.exp(x) / 2, C2, label=r"$\frac{1}{2}e^x$", **half)
    curve(ax, x, np.exp(-x) / 2, C3, label=r"$\frac{1}{2}e^{-x}$", **half)
    dot(ax, 0, 1, False, C1, ms=5)
    ax.legend(loc="upper center", ncol=3, fontsize=8.5)
    ax.set_title(r"$\cosh x = \frac{1}{2}e^x + \frac{1}{2}e^{-x}$", fontsize=10)
    ax = axs[1]
    maxes(ax, (-2.7, 2.7), (-4.5, 4.5), xticks=[-2, 2], yticks=[-2, 2])
    curve(ax, x, np.sinh(x), C1, label=r"$\sinh x$")
    curve(ax, x, np.exp(x) / 2, C2, label=r"$\frac{1}{2}e^x$", **half)
    curve(ax, x, -np.exp(-x) / 2, C3, label=r"$-\frac{1}{2}e^{-x}$", **half)
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title(r"$\sinh x = \frac{1}{2}e^x - \frac{1}{2}e^{-x}$", fontsize=10)
    ax = axs[2]
    maxes(ax, (-4, 4), (-1.6, 1.6), xticks=[-2, 2], yticks=[-1, 1])
    hline(ax, 1)
    hline(ax, -1)
    curve(ax, X(-4, 4), np.tanh(X(-4, 4)), C1, label=r"$\tanh x$")
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title(r"$\tanh x$: ασύμπτωτες $y = \pm 1$", fontsize=10)
    fig.tight_layout(w_pad=2)
    save(fig, "c2-06-hyperbolic")


@figure("c2-06-hyperbola")
def _():
    fig, ax = plt.subplots(figsize=(5.0, 4.0))
    maxes(ax, (-1.6, 4.0), (-2.7, 2.7), xticks=[1, 2, 3], yticks=[-2, -1, 1, 2], equal=True)
    for sgn in (1, -1):
        ax.plot([-1.6, 2.7], [sgn * -1.6, sgn * 2.7], color=MUTED, lw=1, ls=(0, (4, 2.5)))
    t = X(0, 2 * PI, 300)
    ax.plot(np.cos(t), np.sin(t), color=C2, ls=(0, (5, 2.5)), label=r"$x^2 + y^2 = 1$: $(\cos t, \sin t)$")
    u = X(-1.85, 1.85)
    ax.plot(np.cosh(u), np.sinh(u), color=C1, label=r"$x^2 - y^2 = 1$: $(\cosh t, \sinh t)$")
    t0 = 0.9
    dot(ax, np.cos(t0), np.sin(t0), False, C2, ms=5)
    dot(ax, np.cosh(t0), np.sinh(t0), False, C1, ms=5)
    label(ax, np.cosh(t0) + 0.15, np.sinh(t0) - 0.12, r"$(\cosh t, \sinh t)$", fs=9)
    label(ax, 3.9, 2.45, "$y = x$", ha="right", fs=8.5, color=INK2)
    ax.legend(loc="lower right", fontsize=8.5, bbox_to_anchor=(1.03, -0.03))
    save(fig, "c2-06-hyperbola")


# =======================================================================
# Chapter 3 — Όρια και Συνέχεια
# =======================================================================
@figure("c3-01-limit-not-value")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.0))
    ax = axs[0]
    maxes(ax, (-1.2, 3.2), (-0.4, 4.4), xticks=[1], yticks=[2])
    x = X(-1.2, 3.1)
    curve(ax, x, x + 1, C1)
    seg(ax, (1, 0), (1, 2))
    seg(ax, (0, 2), (1, 2))
    dot(ax, 1, 2, True, C1)
    ax.set_title(r"$\frac{x^2 - 1}{x - 1}$: $f(1)$ δεν ορίζεται, $\lim_{x \to 1} = 2$", fontsize=10)
    ax = axs[1]
    maxes(ax, (-0.6, 3.0), (-0.4, 7.5), xticks=[2], yticks=[1, 4])
    x = X(-0.6, 2.7)
    curve(ax, x, x**2, C1)
    seg(ax, (2, 0), (2, 4))
    seg(ax, (0, 4), (2, 4))
    dot(ax, 2, 4, True, C1)
    dot(ax, 2, 1, False, C2)
    label(ax, 2.15, 1.0, "$f(2) = 1$", fs=9)
    ax.set_title(r"$f(2) = 1$, αλλά $\lim_{x \to 2} f(x) = 4$", fontsize=10)
    fig.tight_layout(w_pad=3)
    save(fig, "c3-01-limit-not-value")


@figure("c3-01-one-sided")
def _():
    fig, ax = plt.subplots(figsize=(5.4, 3.1))
    maxes(ax, (-0.6, 4.6), (-1.7, 3.0), xticks=[2], yticks=[1, 1.5, 2], ytl=["1", "1.5", "2"])
    ax.plot([-0.6, 2], [-0.6, 2], color=C1)
    ax.plot([2, 4.6], [1, -1.6], color=C1)
    dot(ax, 2, 2, True, C1)
    dot(ax, 2, 1, True, C1)
    dot(ax, 2, 1.5, False, C2)
    note(ax, (1.95, 2.02), r"$\lim_{x \to 2^-} f = 2$", (0.3, 2.65), ha="left")
    note(ax, (2.05, 0.97), r"$\lim_{x \to 2^+} f = 1$", (3.0, 1.9), ha="left")
    label(ax, 2.18, 1.5, "$f(2) = 1.5$", fs=9)
    save(fig, "c3-01-one-sided")


@figure("c3-01-infinite")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.1))
    for k, ax in enumerate(axs):
        lo = 0 if k == 0 else -8
        maxes(ax, (-3, 3), (lo - 0.5, 8.5), xticks=[-2, -1, 1, 2], yticks=[4] if k == 0 else [-4, 4])
        for s in (-1, 1):
            x = s * X(0.05, 3)
            y = 1 / x**2 if k == 0 else 1 / x
            curve(ax, x, np.clip(y, -9, 9), C1)
    axs[0].set_title(r"$\frac{1}{x^2}$: $+\infty$ και από τις δύο πλευρές", fontsize=10)
    axs[1].set_title(r"$\frac{1}{x}$: $-\infty$ αριστερά, $+\infty$ δεξιά", fontsize=10)
    fig.tight_layout(w_pad=3)
    save(fig, "c3-01-infinite")


@figure("c3-01-oscillation")
def _():
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    maxes(ax, (-0.02, 1.25), (-1.35, 1.6), xticks=[0.2, 0.5, 1], yticks=[-1, 1])
    t = np.concatenate([X(1 / 1.25, 40, 40000)])
    x = 1 / t
    ax.plot(x, np.sin(PI * t), color=C1, lw=1.1, label=r"$\sin\frac{\pi}{x}$")
    ks = np.arange(1, 9)
    ax.plot(1 / ks, 0 * ks, "o", ms=6, mfc=C2, mec=C2, zorder=6,
            label=r"$x = 1, \frac{1}{2}, \frac{1}{3}, \dots$: πάντα $0$")
    xs = 2 / (4 * np.arange(0, 6) + 1)
    ax.plot(xs, 0 * xs + 1, "o", ms=6, mfc="white", mec=C3, mew=1.8, zorder=6,
            label=r"$x = \frac{2}{4k + 1}$: πάντα $1$")
    ax.legend(loc="upper right", fontsize=8.5, bbox_to_anchor=(1.0, 1.1), ncol=1)
    save(fig, "c3-01-oscillation")


@figure("c3-02-hole-vs-asymptote")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.1))
    ax = axs[0]
    maxes(ax, (-1.2, 4.2), (-0.5, 6.6), xticks=[2], yticks=[4])
    x = X(-1.2, 4.1)
    curve(ax, x, x + 2, C1)
    dot(ax, 2, 4, True, C1)
    ax.set_title(r"$\frac{x^2 - 4}{x - 2}$: ο παράγοντας φεύγει ⇒ τρύπα", fontsize=10)
    ax = axs[1]
    maxes(ax, (-2, 4), (-5, 5), xticks=[1], yticks=[-2, 2])
    vline(ax, 1)
    for a, b in [(-2, 0.97), (1.03, 4)]:
        x = X(a, b)
        curve(ax, x, 1 / (x - 1), C1)
    ax.set_title(r"$\frac{x - 1}{(x - 1)^2}$: μένει κάτω ⇒ ασύμπτωτη", fontsize=10)
    fig.tight_layout(w_pad=3)
    save(fig, "c3-02-hole-vs-asymptote")


@figure("c3-02-k-over-zero")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(7.8, 3.2))
    ax = axs[0]
    maxes(ax, (-2, 8), (-10, 12), xticks=[3], yticks=[1])
    vline(ax, 3)
    for a, b in [(-2, 2.7), (3.3, 8)]:
        x = X(a, b)
        curve(ax, x, (x + 1) / (x - 3), C1)
    label(ax, 2.8, -8.5, r"$-\infty$", ha="right", fs=10)
    label(ax, 3.2, 10.5, r"$+\infty$", fs=10)
    ax.set_title(r"$\frac{x + 1}{x - 3}$: πλευρικά $\mp\infty$", fontsize=10)
    ax = axs[1]
    maxes(ax, (-2, 6), (-16, 3), xticks=[2, 5], yticks=[-10])
    vline(ax, 2)
    for a, b in [(-2, 1.55), (2.45, 6)]:
        x = X(a, b)
        curve(ax, x, (x - 5) / (x - 2) ** 2, C1)
    label(ax, 2.15, -14.5, r"$-\infty$ και από τις δύο", fs=9)
    ax.set_title(r"$\frac{x - 5}{(x - 2)^2}$: $\lim_{x \to 2} = -\infty$", fontsize=10)
    fig.tight_layout(w_pad=3)
    save(fig, "c3-02-k-over-zero")


@figure("c3-03-sinx-over-x")
def _():
    fig, ax = plt.subplots(figsize=(7.4, 2.8))
    xt, xl = pi_ticks(-6 * PI, 6 * PI, 2)
    maxes(ax, (-6 * PI - 0.5, 6 * PI + 0.8), (-0.4, 1.2), xticks=xt, xtl=xl, yticks=[1])
    x = X(-6 * PI, 6 * PI, 3000)
    x = x[np.abs(x) > 1e-3]
    env = dict(lw=1, ls=(0, (4, 2.5)))
    xp = X(1.1, 6 * PI)
    ax.plot(xp, 1 / xp, color=MUTED, label=r"$\pm\frac{1}{x}$", **env)
    ax.plot(xp, -1 / xp, color=MUTED, **env)
    ax.plot(-xp, 1 / xp, color=MUTED, **env)
    ax.plot(-xp, -1 / xp, color=MUTED, **env)
    curve(ax, x, np.sin(x) / x, C1, label=r"$\frac{\sin x}{x}$")
    dot(ax, 0, 1, True, C1, ms=5)
    ax.legend(loc="upper right", fontsize=9)
    save(fig, "c3-03-sinx-over-x")


@figure("c3-03-two-asymptotes")
def _():
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    maxes(ax, (-14, 14), (-2.6, 2.6), xticks=[-10, 2, 10], yticks=[-1 / 3, 1 / 3],
          ytl=[r"$-\frac{1}{3}$", r"$\frac{1}{3}$"])
    hline(ax, 1 / 3, C2)
    hline(ax, -1 / 3, C3)
    vline(ax, 2)
    for a, b in [(-14, 1.6), (2.4, 14)]:
        x = X(a, b, 2000)
        curve(ax, x, np.sqrt(x**2 + 2) / (3 * x - 6), C1,
              label=r"$\frac{\sqrt{x^2 + 2}}{3x - 6}$" if a < 0 else None)
    label(ax, 13.8, 0.55, r"$y = \frac{1}{3}$ για $x \to +\infty$", ha="right", fs=9)
    label(ax, -13.8, -0.6, r"$y = -\frac{1}{3}$ για $x \to -\infty$", ha="left", fs=9)
    ax.legend(loc="upper left", fontsize=9.5)
    save(fig, "c3-03-two-asymptotes")


@figure("c3-03-oblique")
def _():
    fig, ax = plt.subplots(figsize=(4.8, 4.0))
    maxes(ax, (-5, 5), (-6.5, 6.5), xticks=[-4, -2, 2, 4], yticks=[-4, -2, 2, 4])
    x = X(-5, 5)
    ax.plot(x, x, color=C2, lw=1.4, ls=(0, (5, 2.5)), label="πλάγια ασύμπτωτη $y = x$")
    for a, b in [(-5, -0.16), (0.16, 5)]:
        x = X(a, b)
        curve(ax, x, (x**2 + 1) / x, C1, label=r"$\frac{x^2 + 1}{x} = x + \frac{1}{x}$" if a < 0 else None)
    ax.legend(loc="upper left", fontsize=8.5)
    save(fig, "c3-03-oblique")


@figure("c3-04-epsilon-delta")
def _():
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    a, L, eps = 2, 5, 2
    lo, hi = np.sqrt(L - eps - 1), np.sqrt(L + eps - 1)  # sqrt2, sqrt6
    d = min(a - lo, hi - a)
    xt = [lo, a - d, a, a + d]
    maxes(ax, (0.5, 3.05), (1.0, 10.2), xticks=xt,
          xtl=[r"$\sqrt{2}$", r"$a - \delta$", "$a = 2$", r"$a + \delta$"],
          yticks=[L - eps, L, L + eps],
          ytl=[r"$L - \varepsilon$", "$L = 5$", r"$L + \varepsilon$"], grid=False)
    ax.axhspan(L - eps, L + eps, color=C2, alpha=0.12, lw=0, label=r"ζώνη $|f(x) - L| < \varepsilon$")
    ax.axvspan(a - d, a + d, color=C1, alpha=0.14, lw=0, label=r"$|x - a| < \delta$")
    for yv in (L - eps, L + eps):
        hline(ax, yv, C2, lw=1)
    for xv in (a - d, a + d):
        vline(ax, xv, C1, lw=1)
    x = X(0.6, 3.0)
    curve(ax, x, x**2 + 1, INK, lw=2, label="$f(x) = x^2 + 1$")
    seg(ax, (lo, 1.0), (lo, L - eps), INK2)
    dot(ax, lo, L - eps, False, INK2, ms=4)
    dot(ax, hi, L + eps, False, INK2, ms=4)
    dot(ax, a, L, True, INK, ms=5.5)
    ax.annotate("", xy=(a - d, 9.2), xytext=(a, 9.2),
                arrowprops=dict(arrowstyle="<->", color=C1, lw=1, mutation_scale=8))
    ax.annotate("", xy=(a + d, 9.2), xytext=(a, 9.2),
                arrowprops=dict(arrowstyle="<->", color=C1, lw=1, mutation_scale=8))
    label(ax, a - d / 2, 9.35, r"$\delta$", ha="center", va="bottom", fs=10)
    label(ax, a + d / 2, 9.35, r"$\delta$", ha="center", va="bottom", fs=10)
    note(ax, (lo + 0.02, 1.6), "αριστερά χωράει\nπερισσότερο, αλλά το $\\delta$\nτο ορίζει η στενή πλευρά",
         (0.62, 7.6), ha="left", fs=8.5)
    ax.legend(loc="upper left", fontsize=8.5, bbox_to_anchor=(0.0, 0.62))
    save(fig, "c3-04-epsilon-delta")


@figure("c3-05-discontinuities")
def _():
    fig, axs = plt.subplots(1, 4, figsize=(10.6, 2.8))
    ax = axs[0]
    maxes(ax, (-0.5, 4), (-0.5, 6.5), xticks=[2], yticks=[4], grid=False)
    x = X(-0.5, 4)
    curve(ax, x, x + 2, C1)
    dot(ax, 2, 4, True, C1)
    ax.set_title("άρση ασυνέχειας\n(διορθώσιμη)", fontsize=9.5)
    ax = axs[1]
    maxes(ax, (-2, 2), (-1.6, 1.6), xticks=[], yticks=[-1, 1], grid=False)
    ax.plot([-2, 0], [-1, -1], color=C1)
    ax.plot([0, 2], [1, 1], color=C1)
    dot(ax, 0, -1, True, C1)
    dot(ax, 0, 1, True, C1)
    ax.set_title("άλμα\n(πεπερασμένο πήδημα)", fontsize=9.5)
    ax = axs[2]
    maxes(ax, (-2, 2), (-6, 6), xticks=[], yticks=[], grid=False)
    for s in (-1, 1):
        x = s * X(0.17, 2)
        curve(ax, x, 1 / x, C1)
    ax.set_title("άπειρη\n(δευτέρου είδους)", fontsize=9.5)
    ax = axs[3]
    maxes(ax, (-0.6, 0.6), (-1.4, 1.4), xticks=[], yticks=[-1, 1], grid=False)
    t = X(1 / 0.6, 60, 30000)
    ax.plot(1 / t, np.sin(t), color=C1, lw=0.8)
    ax.plot(-1 / t, -np.sin(t), color=C1, lw=0.8)
    ax.set_title("ταλάντωση\n(δευτέρου είδους)", fontsize=9.5)
    fig.tight_layout(w_pad=1.5)
    save(fig, "c3-05-discontinuities")


@figure("c3-05-ivt")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(8.6, 3.3))
    ax = axs[0]
    maxes(ax, (0.75, 2.2), (-2, 6), xticks=[1, 1.25, 1.5, 2], xtl=["1", "1.25", "1.5", "2"], yticks=[-1, 5])
    x = X(0.75, 2.15)
    curve(ax, x, x**3 - x - 1, C1, label="$f(x) = x^3 - x - 1$")
    dot(ax, 1, -1, False, C1)
    dot(ax, 2, 5, False, C1)
    seg(ax, (1, 0), (1, -1))
    seg(ax, (2, 0), (2, 5))
    r = 1.324718
    dot(ax, r, 0, False, C2, label=r"ρίζα $\approx 1.3247$")
    for m in (1.5, 1.25):
        dot(ax, m, m**3 - m - 1, True, C3, ms=5)
    ax.plot([], [], "o", mfc="white", mec=C3, mew=1.7, label="βήματα διχοτόμησης")
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title("$f(1) < 0 < f(2)$ ⇒ ρίζα στο $(1, 2)$", fontsize=10)
    ax = axs[1]
    maxes(ax, (-1.3, 1.3), (-5, 5), xticks=[-1, 1], yticks=[-1, 1])
    for s in (-1, 1):
        x = s * X(0.2, 1)
        curve(ax, x, 1 / x, C1)
    dot(ax, -1, -1, False, C1)
    dot(ax, 1, 1, False, C1)
    ax.set_title(r"$\frac{1}{x}$ στο $[-1, 1]$: όχι συνεχής ⇒ καμία ρίζα", fontsize=10)
    fig.tight_layout(w_pad=3)
    save(fig, "c3-05-ivt")


@figure("c3-06-squeeze")
def _():
    fig, ax = plt.subplots(figsize=(6.0, 3.3))
    maxes(ax, (-0.42, 0.42), (-0.18, 0.18), xticks=[-0.4, -0.2, 0.2, 0.4], yticks=[-0.1, 0.1])
    x = X(-0.41, 0.41, 400)
    curve(ax, x, x**2, C2, lw=1.4, ls=(0, (5, 2.5)), label="$x^2$")
    curve(ax, x, -(x**2), C3, lw=1.4, ls=(0, (1.5, 2)), label="$-x^2$")
    t = X(1 / 0.41, 400, 60000)
    xs = np.concatenate([-1 / t[::-1], 1 / t])
    ax.plot(xs, xs**2 * np.sin(1 / xs), color=C1, lw=1.0, label=r"$x^2\sin\frac{1}{x}$")
    ax.legend(loc="upper center", ncol=3, fontsize=9)
    save(fig, "c3-06-squeeze")


@figure("c3-06-sin-proof")
def _():
    fig, ax = plt.subplots(figsize=(5.2, 3.9))
    ax.set_aspect("equal")
    ax.axis("off")
    x0 = 0.75
    c, s, tn = np.cos(x0), np.sin(x0), np.tan(x0)
    ax.fill([0, 1, 1], [0, 0, tn], color=C3, alpha=0.18, lw=0, label=r"τρίγωνο $OAT$: $\frac{\tan x}{2}$")
    tt = X(0, x0, 80)
    ax.fill(np.r_[0, np.cos(tt)], np.r_[0, np.sin(tt)], color=C2, alpha=0.25, lw=0,
            label=r"τομέας $OAP$: $\frac{x}{2}$")
    ax.fill([0, 1, c], [0, 0, s], color=C1, alpha=0.35, lw=0, label=r"τρίγωνο $OAP$: $\frac{\sin x}{2}$")
    t = X(-0.05, PI / 2 + 0.05, 200)
    ax.plot(np.cos(t), np.sin(t), color=INK2, lw=1.2)
    ax.plot([0, 1.25], [0, 0], color=INK2, lw=1)
    ax.plot([0, 1.08], [0, 1.08 * tn], color=INK2, lw=1)
    ax.plot([1, 1], [0, tn], color=INK2, lw=1)
    ax.plot([c, c], [0, s], color=INK2, lw=1, ls=(0, (3, 2)))
    ax.plot([1, c], [0, s], color=INK2, lw=1)
    arc(ax, 0.2, 0, x0, arrow=False)
    label(ax, 0.23, 0.08, "$x$", fs=10)
    for (px, py, t_, ha) in [(0, 0, "$O$", "right"), (1, 0, "$A$", "left"), (c, s, "$P$", "right"),
                             (1, tn, "$T$", "left")]:
        dot(ax, px, py, False, INK, ms=4)
        label(ax, px + (0.04 if ha == "left" else -0.04), py + 0.04, t_, ha=ha, va="bottom")
    label(ax, c - 0.03, s / 2, r"$\sin x$", ha="right", fs=9, color=INK2)
    label(ax, 1.04, tn / 2, r"$\tan x$", fs=9, color=INK2)
    ax.set_xlim(-0.12, 1.75)
    ax.set_ylim(-0.08, 1.12)
    ax.legend(loc="upper right", fontsize=8.5, bbox_to_anchor=(1.05, 1.0))
    save(fig, "c3-06-sin-proof")


@figure("c3-06-e-limit")
def _():
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    maxes(ax, (-30, 30), (0, 4.6), xticks=[-20, -10, 10, 20], yticks=[1, np.e], ytl=["1", "$e$"])
    hline(ax, np.e, C3)
    hline(ax, 1, MUTED, ls=(0, (1.5, 2.5)))
    x = X(0.05, 30, 2000)
    curve(ax, x, (1 + 1 / x) ** x, C1, label=r"$x \to +\infty$: ανεβαίνει προς το $e$")
    x = X(-30, -1.27, 2000)
    curve(ax, x, (1 + 1 / x) ** x, C2, ls=(0, (5, 2.5)), label=r"$x \to -\infty$: κατεβαίνει προς το $e$")
    label(ax, 29.5, 0.75, "όχι 1, παρόλο που η βάση → 1", ha="right", fs=8.5, color=INK2)
    ax.legend(loc="upper center", fontsize=8.5, ncol=1, bbox_to_anchor=(0.5, 1.06))
    ax.set_title(r"$\left(1 + \frac{1}{x}\right)^x$", fontsize=10, loc="left")
    save(fig, "c3-06-e-limit")


@figure("c3-06-growth")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(8.6, 3.2))
    ax = axs[0]
    maxes(ax, (0, 6.2), (0, 260), xticks=[2, 4, 6], yticks=[100, 200])
    x = X(0, 6.1)
    curve(ax, x, x**3, C2, ls=(0, (5, 2.5)), label="$x^3$")
    curve(ax, x, np.exp(x), C1, label="$e^x$")
    dot(ax, 4.5364, 4.5364**3, False, INK, ms=5)
    note(ax, (4.5364, 93.4), r"$x \approx 4.54$: η $e^x$ περνά μπροστά", (0.3, 170), fs=8.5)
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title(r"$x^n \ll e^x$: τελικά κερδίζει η $e^x$", fontsize=10)
    ax = axs[1]
    maxes(ax, (0, 40), (-2.5, 7), xticks=[10, 20, 30], yticks=[2, 4, 6])
    x = X(0.03, 40, 2000)
    curve(ax, x, np.sqrt(x), C2, ls=(0, (5, 2.5)), label=r"$\sqrt{x}$")
    curve(ax, x, np.log(x), C1, label=r"$\ln x$")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title(r"$\ln x \ll x^n$: ακόμη και $\ln x < \sqrt{x}$", fontsize=10)
    fig.tight_layout(w_pad=3)
    save(fig, "c3-06-growth")


# =======================================================================
# Chapter 4 — Παράγωγος
# =======================================================================
@figure("c4-01-secants")
def _():
    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    maxes(ax, (-0.6, 3.4), (-1.5, 9.8), xticks=[1, 1.4, 2, 3], xtl=["1", "1.4", "2", "3"], yticks=[1])
    x = X(-0.6, 3.3)
    curve(ax, x, x**2, C1, label="$y = x^2$")
    shades = ["#c9c8c2", "#a6a59f", "#77766f"]
    for q, col in zip([3, 2, 1.4], shades):
        m = q + 1
        ax.plot(x, 1 + m * (x - 1), color=col, lw=1.3)
        dot(ax, q, q**2, True, col, ms=5)
    ax.plot([], [], color=shades[1], lw=1.3, label=r"τέμνουσες $PQ$ καθώς $Q \to P$")
    curve(ax, x, 2 * x - 1, C2, lw=2.2, label="εφαπτομένη $y = 2x - 1$")
    dot(ax, 1, 1, False, INK)
    label(ax, 0.92, 1.45, "$P$", ha="right")
    label(ax, 3.06, 8.6, "$Q$", fs=9, color=INK2)
    ax.legend(loc="upper left", fontsize=8.5)
    save(fig, "c4-01-secants")


@figure("c4-01-tangent-traps")
def _():
    fig, axs = plt.subplots(1, 3, figsize=(10.4, 3.3))
    ax = axs[0]
    maxes(ax, (-2.6, 2.1), (-10, 6), xticks=[-2, 1], yticks=[-8, 1])
    x = X(-2.6, 2.05)
    curve(ax, x, x**3, C1, label="$y = x^3$")
    curve(ax, x, 3 * x - 2, C2, lw=1.5, ls=(0, (5, 2.5)), label="εφ. στο $(1, 1)$")
    dot(ax, 1, 1, False, C2, ms=5)
    dot(ax, -2, -8, True, C2, ms=5)
    note(ax, (-2, -8), "ξανατέμνει\nστο $(-2, -8)$", (-1.7, -3.2), fs=8.5)
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title("τέμνει την καμπύλη και αλλού", fontsize=10)
    ax = axs[1]
    maxes(ax, (-2.2, 2.2), (-1.8, 1.8), xticks=[-1, 1], yticks=[-1, 1])
    x = X(-2.2, 2.2, 2000)
    curve(ax, x, np.cbrt(x), C1, label=r"$y = \sqrt[3]{x}$")
    ax.plot([0, 0], [-1.8, 1.8], color=C2, lw=2.2, label="εφαπτομένη $x = 0$", zorder=4)
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title("κατακόρυφη εφαπτομένη", fontsize=10)
    ax = axs[2]
    maxes(ax, (-2, 2), (-0.8, 2.2), xticks=[-1, 1], yticks=[1])
    x = X(-2, 2)
    curve(ax, x, np.abs(x), C1, label="$y = |x|$")
    dot(ax, 0, 0, False, C2, ms=5)
    note(ax, (0.03, 0.05), "γωνία: καμία\nεφαπτομένη", (0.55, 1.75), fs=8.5)
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title("δεν υπάρχει εφαπτομένη", fontsize=10)
    fig.tight_layout(w_pad=2)
    save(fig, "c4-01-tangent-traps")


@figure("c4-02-nondeftrightarrow")
def _():
    fig, axs = plt.subplots(1, 4, figsize=(10.6, 2.9))
    specs = [
        ("γωνία: $|x|$", lambda x: np.abs(x), (-1.6, 1.8)),
        ("ακίδα: $x^{2/3}$", lambda x: np.cbrt(x**2), (-0.5, 1.8)),
        (r"κατακόρυφη εφ.: $\sqrt[3]{x}$", np.cbrt, (-1.6, 1.6)),
    ]
    for ax, (ttl, f, yl) in zip(axs, specs):
        maxes(ax, (-1.6, 1.6), yl, xticks=[], yticks=[], grid=False)
        x = X(-1.6, 1.6, 3000)
        curve(ax, x, f(x), C1)
        dot(ax, 0, 0, False, C2, ms=5)
        ax.set_title(ttl, fontsize=9.5)
    ax = axs[3]
    maxes(ax, (-1.6, 2.4), (-1.8, 2.4), xticks=[-1, 1, 2], yticks=[], grid=False)
    for k in range(-2, 3):
        a, b = max(k, -1.6), min(k + 1, 2.4)
        ax.plot([a, b], [k, k], color=C1)
        if k >= -1:
            dot(ax, k, k, False, C1, ms=4.5)
        if k + 1 <= 2.4:
            dot(ax, k + 1, k, True, C1, ms=4.5)
    ax.set_title("ασυνέχεια: $[x]$", fontsize=9.5)
    fig.tight_layout(w_pad=1.5)
    save(fig, "c4-02-nondeftrightarrow")


@figure("c4-02-piecewise")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.3))
    ax = axs[0]
    maxes(ax, (-1.6, 2.6), (-1, 4.4), xticks=[1], yticks=[1])
    x = X(-1.6, 1)
    curve(ax, x, x**2, C1, label=r"$x^2$, $x \leq 1$")
    x = X(1, 2.6)
    curve(ax, x, 2 * x - 1, C2, label=r"$2x - 1$, $x > 1$")
    dot(ax, 1, 1, False, INK, ms=5)
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title("συνεχής + ίσες πλευρικές ⇒ παραγωγίσιμη", fontsize=10)
    ax = axs[1]
    maxes(ax, (-0.6, 2.4), (0, 6), xticks=[1], yticks=[3])
    x = X(-0.6, 1)
    curve(ax, x, x**2 + 2, C1, label=r"$x^2 + 2$, $x \leq 1$")
    x = X(1, 2.4)
    curve(ax, x, x + 2, C2, label=r"$x + 2$, $x > 1$")
    curve(ax, X(1, 2.0), 2 * X(1, 2.0) + 1, C1, lw=1.2, ls=(0, (4, 2)))
    label(ax, 2.02, 5.0, "κλίση 2", fs=8.5, color=INK2)
    label(ax, 2.38, 3.95, "κλίση 1", ha="right", fs=8.5, color=INK2)
    dot(ax, 1, 3, False, INK, ms=5)
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title("συνεχής, αλλά γωνία ⇒ όχι παραγωγίσιμη", fontsize=10)
    fig.tight_layout(w_pad=3)
    save(fig, "c4-02-piecewise")


@figure("c4-02-xsin")
def _():
    fig, axs = plt.subplots(1, 2, figsize=(8.6, 3.0))
    t = X(1 / 0.34, 300, 60000)
    xs = np.concatenate([-1 / t[::-1], 1 / t])
    env = dict(lw=1.2, ls=(0, (4, 2.5)), color=MUTED)
    ax = axs[0]
    maxes(ax, (-0.35, 0.35), (-0.36, 0.36), xticks=[-0.2, 0.2], yticks=[-0.2, 0.2])
    x = X(-0.34, 0.34)
    ax.plot(x, np.abs(x), **env, label=r"$\pm|x|$")
    ax.plot(x, -np.abs(x), **env)
    ax.plot(xs, xs * np.sin(1 / xs), color=C1, lw=0.9, label=r"$x\sin\frac{1}{x}$")
    ax.legend(loc="upper center", ncol=2, fontsize=8.5)
    ax.set_title("συνεχής, όχι παραγωγίσιμη στο 0", fontsize=10)
    ax = axs[1]
    maxes(ax, (-0.35, 0.35), (-0.12, 0.12), xticks=[-0.2, 0.2], yticks=[-0.1, 0.1])
    ax.plot(x, x**2, **env, label=r"$\pm x^2$")
    ax.plot(x, -(x**2), **env)
    ax.plot(xs, xs**2 * np.sin(1 / xs), color=C1, lw=0.9, label=r"$x^2\sin\frac{1}{x}$")
    ax.legend(loc="upper center", ncol=2, fontsize=8.5)
    ax.set_title("παραγωγίσιμη στο 0, $f'(0) = 0$", fontsize=10)
    fig.tight_layout(w_pad=3)
    save(fig, "c4-02-xsin")


@figure("c4-03-sin-derivative")
def _():
    fig, axs = plt.subplots(2, 1, figsize=(7.2, 4.6), sharex=False)
    xt, xl = pi_ticks(0, 2 * PI, 0.5)
    pts = [0, PI / 2, PI, 3 * PI / 2, 2 * PI]
    ax = axs[0]
    maxes(ax, (-0.3, 2 * PI + 0.4), (-1.5, 1.5), xticks=xt[1:], xtl=xl[1:], yticks=[-1, 1])
    x = X(-0.3, 2 * PI + 0.3)
    curve(ax, x, np.sin(x), C1, label=r"$f(x) = \sin x$")
    for p in pts:
        m = np.cos(p)
        h = 0.45
        ax.plot([p - h, p + h], [np.sin(p) - m * h, np.sin(p) + m * h], color=C2, lw=1.6)
        dot(ax, p, np.sin(p), False, C2, ms=4.5)
    ax.plot([], [], color=C2, lw=1.6, label="εφαπτομένες: κλίσεις $1, 0, -1, 0, 1$")
    ax.legend(loc="lower left", fontsize=8.5)
    ax = axs[1]
    maxes(ax, (-0.3, 2 * PI + 0.4), (-1.5, 1.5), xticks=xt[1:], xtl=xl[1:], yticks=[-1, 1])
    curve(ax, x, np.cos(x), C2, label=r"$f'(x) = \cos x$")
    for p in pts:
        dot(ax, p, np.cos(p), False, C2, ms=4.5)
    ax.legend(loc="lower left", fontsize=8.5)
    for p in pts:
        for a in axs:
            a.axvline(p, color=GRID, lw=1.0, zorder=0)
    fig.tight_layout(h_pad=1.5)
    save(fig, "c4-03-sin-derivative")


@figure("c4-05-circle-implicit")
def _():
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    maxes(ax, (-7, 10), (-7.5, 7.5), xticks=[-5, 3, 5], yticks=[-5, -4, 4, 5], equal=True)
    t = X(0, 2 * PI, 300)
    ax.plot(5 * np.cos(t), 5 * np.sin(t), color=C1, label=r"$x^2 + y^2 = 25$")
    x = X(-0.5, 9)
    ax.plot(x, 4 - 0.75 * (x - 3), color=C2, lw=1.6, label=r"στο $(3, 4)$: $y' = -\frac{3}{4}$")
    ax.plot(x, -4 + 0.75 * (x - 3), color=C3, lw=1.6, ls=(0, (5, 2.5)), label=r"στο $(3, -4)$: $y' = \frac{3}{4}$")
    dot(ax, 3, 4, False, C2, ms=5)
    dot(ax, 3, -4, False, C3, ms=5)
    for p, horiz in [((0, 5), True), ((0, -5), True), ((5, 0), False), ((-5, 0), False)]:
        if horiz:
            ax.plot([p[0] - 1.6, p[0] + 1.6], [p[1], p[1]], color=C4, lw=1.4)
        else:
            ax.plot([p[0], p[0]], [p[1] - 1.6, p[1] + 1.6], color=C4, lw=1.4)
        dot(ax, *p, False, C4, ms=4.5)
    ax.plot([], [], color=C4, lw=1.4, label="οριζόντιες / κατακόρυφες εφ.")
    ax.legend(loc="upper right", fontsize=8, bbox_to_anchor=(1.04, 1.04))
    save(fig, "c4-05-circle-implicit")


@figure("c4-05-folium")
def _():
    fig, ax = plt.subplots(figsize=(4.8, 4.6))
    maxes(ax, (-3, 3.2), (-3, 3.2), xticks=[-2, 1.5, 3], xtl=["$-2$", r"$\frac{3}{2}$", "$3$"],
          yticks=[-2, 1.5, 3], ytl=["$-2$", r"$\frac{3}{2}$", "$3$"], equal=True)
    g = np.linspace(-3.2, 3.4, 900)
    Xg, Yg = np.meshgrid(g, g)
    ax.contour(Xg, Yg, Xg**3 + Yg**3 - 3 * Xg * Yg, levels=[0], colors=[C1], linewidths=2)
    ax.plot([], [], color=C1, label=r"$x^3 + y^3 = 3xy$")
    x = X(-1, 3.2)
    ax.plot(x, 3 - x, color=C2, lw=1.6, label=r"εφ. στο $(\frac{3}{2}, \frac{3}{2})$: $y' = -1$")
    x = X(-3, 2)
    ax.plot(x, -1 - x, color=MUTED, lw=1.1, ls=(0, (4, 2.5)), label="ασύμπτωτη $x + y + 1 = 0$")
    dot(ax, 1.5, 1.5, False, C2, ms=5)
    ax.legend(loc="lower left", fontsize=8, bbox_to_anchor=(-0.02, -0.02))
    save(fig, "c4-05-folium")


@figure("c4-06-inverse-slopes")
def _():
    fig, ax = plt.subplots(figsize=(5.0, 4.8))
    maxes(ax, (-3, 5.4), (-3, 5.4), xticks=[1, 3], yticks=[1, 3], equal=True)
    ax.plot([-3, 5.3], [-3, 5.3], color=INK2, lw=1, ls=(0, (1.5, 2)), label="$y = x$")
    t = X(-1.65, 1.5)
    f = t**3 + t + 1
    curve(ax, t, f, C1, label="$f(x) = x^3 + x + 1$")
    curve(ax, f, t, C2, ls=(0, (5, 2.5)), label="$f^{-1}$")
    h = 0.45
    ax.plot([1 - h, 1 + h], [3 - 4 * h, 3 + 4 * h], color=C1, lw=1.3, zorder=3)
    ax.plot([3 - 4 * h, 3 + 4 * h], [1 - h, 1 + h], color=C2, lw=1.3, zorder=3)
    dot(ax, 1, 3, False, C1, ms=5)
    dot(ax, 3, 1, False, C2, ms=5)
    label(ax, 1.25, 3.0, "κλίση $f'(1) = 4$", fs=8.5)
    label(ax, 3.1, 0.45, r"κλίση $(f^{-1})'(3) = \frac{1}{4}$", fs=8.5, ha="center", va="top")
    ax.legend(loc="upper left", fontsize=8.5)
    save(fig, "c4-06-inverse-slopes")


# =======================================================================
if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else ""
    for name, fn in REGISTRY:
        if name.startswith(prefix):
            fn()
            print("ok", name)
