"""
HoneyGuard Cybersecurity Dark Theme & Styles
Palette based on modern Security Operations Center (SOC) dark aesthetics.
"""

import tkinter as tk
from tkinter import ttk

# SOC Dark Color Palette
BG_DARK = "#0d1117"        # Deep background
BG_PANEL = "#161b22"       # Card / Panel background
BG_SURFACE = "#21262d"     # Border / Input / Table header
TEXT_PRIMARY = "#f0f6fc"   # Bright white text
TEXT_MUTED = "#8b949e"     # Gray secondary text
ACCENT_BLUE = "#58a6ff"    # Primary action blue
ACCENT_GREEN = "#3fb950"   # Normal / Intact / Success
ACCENT_YELLOW = "#d29922"  # Warning / Medium risk
ACCENT_RED = "#f85149"     # Critical / High risk alert
ACCENT_PURPLE = "#bc8cff"  # Forensics / Special

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SUBTITLE = ("Segoe UI", 12, "bold")
FONT_HEADING = ("Segoe UI", 10, "bold")
FONT_BODY = ("Segoe UI", 9)
FONT_MONO = ("Consolas", 9)


def apply_soc_dark_theme(root: tk.Tk):
    """Apply SOC dark styling to root window and ttk widgets."""
    root.configure(bg=BG_DARK)

    style = ttk.Style(root)
    # Use clam as base engine for full color customization
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Global Frame
    style.configure("TFrame", background=BG_DARK)
    style.configure("Panel.TFrame", background=BG_PANEL)
    style.configure("Surface.TFrame", background=BG_SURFACE)

    # Labels
    style.configure("TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=FONT_BODY)
    style.configure("Panel.TLabel", background=BG_PANEL, foreground=TEXT_PRIMARY, font=FONT_BODY)
    style.configure("Title.TLabel", background=BG_PANEL, foreground=TEXT_PRIMARY, font=FONT_TITLE)
    style.configure("Subtitle.TLabel", background=BG_PANEL, foreground=ACCENT_BLUE, font=FONT_SUBTITLE)
    style.configure("Muted.TLabel", background=BG_PANEL, foreground=TEXT_MUTED, font=FONT_BODY)

    # Buttons
    style.configure(
        "TButton",
        background=BG_SURFACE,
        foreground=TEXT_PRIMARY,
        font=FONT_HEADING,
        borderwidth=1,
        focuscolor="none",
        padding=6
    )
    style.map(
        "TButton",
        background=[("active", ACCENT_BLUE), ("pressed", "#1f6feb")],
        foreground=[("active", "#ffffff")]
    )

    style.configure(
        "Primary.TButton",
        background="#1f6feb",
        foreground="#ffffff",
        font=FONT_HEADING,
        padding=6
    )
    style.map(
        "Primary.TButton",
        background=[("active", ACCENT_BLUE), ("pressed", "#1158c7")]
    )

    style.configure(
        "Danger.TButton",
        background="#b62324",
        foreground="#ffffff",
        font=FONT_HEADING,
        padding=6
    )
    style.map(
        "Danger.TButton",
        background=[("active", ACCENT_RED), ("pressed", "#8e1515")]
    )

    style.configure(
        "Success.TButton",
        background="#238636",
        foreground="#ffffff",
        font=FONT_HEADING,
        padding=6
    )
    style.map(
        "Success.TButton",
        background=[("active", ACCENT_GREEN), ("pressed", "#196c2e")]
    )

    # Entry
    style.configure(
        "TEntry",
        fieldbackground=BG_SURFACE,
        foreground=TEXT_PRIMARY,
        insertcolor=TEXT_PRIMARY,
        borderwidth=1
    )

    # Treeview (Data Tables)
    style.configure(
        "Treeview",
        background=BG_PANEL,
        foreground=TEXT_PRIMARY,
        fieldbackground=BG_PANEL,
        font=FONT_BODY,
        rowheight=26,
        borderwidth=0
    )
    style.configure(
        "Treeview.Heading",
        background=BG_SURFACE,
        foreground=TEXT_PRIMARY,
        font=FONT_HEADING,
        padding=5,
        relief="flat"
    )
    style.map(
        "Treeview",
        background=[("selected", "#1f6feb")],
        foreground=[("selected", "#ffffff")]
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#30363d")]
    )
