"""Tkinter graphical user interface for Lynx Real Estate Analysis."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional

from lynx_realestate.metrics.relevance import get_relevance
from lynx_realestate.models import AnalysisReport, CompanyStage, CompanyTier, Relevance
from lynx_investor_core.gui_themes import ThemeCycler, apply_theme
from lynx_investor_core.urlsafe import safe_webbrowser_open

# ---------------------------------------------------------------------------
# Colour palette (Catppuccin Mocha)
# ---------------------------------------------------------------------------
BG = "#1e1e2e"
BG_SURFACE = "#232336"
BG_CARD = "#2a2a3d"
BG_INPUT = "#313147"
BG_HOVER = "#3b3b54"
FG = "#cdd6f4"
FG_DIM = "#6c7086"
FG_SUBTLE = "#585b70"
ACCENT = "#89b4fa"
ACCENT_DIM = "#5a7ec2"
LAVENDER = "#b4befe"
BORDER = "#45475a"
BORDER_LIGHT = "#585b70"
BTN_BG = "#89b4fa"
BTN_FG = "#1e1e2e"
BTN_ACTIVE = "#74c7ec"
BTN_SECONDARY_BG = "#45475a"
BTN_SECONDARY_FG = "#cdd6f4"
BTN_DANGER_BG = "#f38ba8"
GREEN = "#a6e3a1"
GREEN_DIM = "#5a8a5a"
RED = "#f38ba8"
RED_DIM = "#8a4a5a"
YELLOW = "#f9e2af"
ORANGE = "#fab387"
TEAL = "#94e2d5"
MAUVE = "#cba6f7"
PINK = "#f5c2e7"
SKY = "#89dceb"
PEACH = "#fab387"

# Unicode glyphs
DIAMOND = "\u25c6"
CHECK = "\u2714"
CROSS = "\u2718"
WARN_ICON = "\u26a0"
ARROW_DOWN = "\u25bc"
ARROW_RIGHT = "\u25b6"
BULLET = "\u2022"
STAR = "\u2605"
CIRCLE = "\u25cf"
CHART = "\u2587"

# Section icons
ICON_PROFILE = "\U0001f3e2"    # office building
ICON_VALUATION = "\U0001f4b0"  # money bag
ICON_PROFIT = "\U0001f4c8"     # chart increasing
ICON_SOLVENCY = "\U0001f3e6"   # bank
ICON_GROWTH = "\U0001f680"     # rocket
ICON_ENERGY = "\u26a1"         # lightning bolt
ICON_SHARES = "\U0001f4ca"     # bar chart
ICON_VALUE = "\U0001f4a1"      # light bulb
ICON_FINANCE = "\U0001f4ca"    # bar chart
ICON_FILING = "\U0001f4c4"     # page facing up
ICON_NEWS = "\U0001f4f0"       # newspaper
ICON_SCREENING = "\U0001f4cb"  # clipboard

# Fonts -- use platform-appropriate defaults.
# Tkinter does NOT support comma-separated fallback lists; each tuple
# must contain a single family name.  We pick a good cross-platform
# default and Tk handles missing fonts gracefully (falls back to its
# built-in default).
import platform as _plat
if _plat.system() == "Windows":
    _FAMILY = "Segoe UI"
    _MONO = "Consolas"
elif _plat.system() == "Darwin":
    _FAMILY = "Helvetica"
    _MONO = "Menlo"
else:
    _FAMILY = "Noto Sans"
    _MONO = "Noto Sans Mono"

FONT = (_FAMILY, 11)
FONT_BOLD = (_FAMILY, 11, "bold")
FONT_SMALL = (_FAMILY, 10)
FONT_SMALL_BOLD = (_FAMILY, 10, "bold")
FONT_TITLE = (_FAMILY, 22, "bold")
FONT_SUBTITLE = (_FAMILY, 12)
FONT_SECTION = (_FAMILY, 13, "bold")
FONT_MONO = (_MONO, 10)
FONT_SPLASH_TITLE = (_FAMILY, 36, "bold")
FONT_SPLASH_SUB = (_FAMILY, 14)
FONT_SPLASH_VER = (_FAMILY, 11)
FONT_TIER = (_FAMILY, 12, "bold")
FONT_STAGE = (_FAMILY, 11, "bold")
FONT_BTN = (_FAMILY, 10, "bold")

# Tier colour mapping
TIER_COLORS = {
    CompanyTier.MEGA:  ("#a6e3a1", "#1a3a1a"),  # green badge
    CompanyTier.LARGE: ("#94e2d5", "#1a3535"),   # teal badge
    CompanyTier.MID:   ("#89b4fa", "#1a2a45"),   # blue badge
    CompanyTier.SMALL: ("#f9e2af", "#3a351a"),   # yellow badge
    CompanyTier.MICRO: ("#fab387", "#3a2a1a"),   # orange badge
    CompanyTier.NANO:  ("#f38ba8", "#3a1a25"),   # red badge
}

# Stage colour mapping
STAGE_COLORS = {
    CompanyStage.STABILIZED:  ("#a6e3a1", "#1a3a1a"),
    CompanyStage.NET_LEASE:   ("#94e2d5", "#1a3535"),
    CompanyStage.LEASE_UP: ("#89b4fa", "#1a2a45"),
    CompanyStage.DEVELOPMENT:  ("#f9e2af", "#3a351a"),
    CompanyStage.PRE_DEVELOPMENT: ("#fab387", "#3a2a1a"),
}


# ---------------------------------------------------------------------------
# Splash screen
# ---------------------------------------------------------------------------

class SplashScreen:
    """Animated splash screen shown at startup."""

    def __init__(self, root: tk.Tk, on_done: callable) -> None:
        self.root = root
        self.on_done = on_done
        self.frame = tk.Frame(root, bg=BG)
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.frame.lift()

        # Center content
        center = tk.Frame(self.frame, bg=BG)
        center.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        # Logo diamond pattern
        logo_text = f"{DIAMOND}  {DIAMOND}  {DIAMOND}"
        self.logo = tk.Label(
            center, text=logo_text, font=(_FAMILY, 28),
            bg=BG, fg=ACCENT,
        )
        self.logo.pack(pady=(0, 12))

        # Title
        self.title = tk.Label(
            center, text="LYNX", font=FONT_SPLASH_TITLE,
            bg=BG, fg=FG,
        )
        self.title.pack(pady=(0, 2))

        # Subtitle
        self.subtitle = tk.Label(
            center, text="Real Estate Analysis", font=FONT_SPLASH_SUB,
            bg=BG, fg=ACCENT,
        )
        self.subtitle.pack(pady=(0, 20))

        # Tagline
        self.tagline = tk.Label(
            center, text="Real Estate Sector Analysis", font=FONT_SMALL,
            bg=BG, fg=FG_DIM,
        )
        self.tagline.pack(pady=(0, 30))

        # Version
        from lynx_realestate import __version__, __year__, __author__, SUITE_LABEL
        self.version = tk.Label(
            center, text=f"v{__version__}  {BULLET}  {__year__}  {BULLET}  {__author__}",
            font=FONT_SPLASH_VER, bg=BG, fg=FG_SUBTLE,
        )
        self.version.pack(pady=(0, 4))

        self.suite_label = tk.Label(
            center, text=SUITE_LABEL,
            font=FONT_SPLASH_VER, bg=BG, fg=FG_SUBTLE,
        )
        self.suite_label.pack(pady=(0, 40))

        # Loading bar
        self.bar_frame = tk.Frame(center, bg=BORDER, height=3, width=260)
        self.bar_frame.pack(pady=(0, 8))
        self.bar_frame.pack_propagate(False)
        self.bar_fill = tk.Frame(self.bar_frame, bg=ACCENT, height=3, width=0)
        self.bar_fill.place(x=0, y=0, relheight=1)

        self.loading_label = tk.Label(
            center, text="Loading...", font=FONT_SMALL,
            bg=BG, fg=FG_DIM,
        )
        self.loading_label.pack()

        self._progress = 0
        self._animate()

    def _animate(self) -> None:
        self._progress += 8
        if self._progress > 100:
            self._progress = 100
        bar_width = int(260 * self._progress / 100)
        self.bar_fill.place(x=0, y=0, relheight=1, width=bar_width)

        if self._progress >= 100:
            self.root.after(200, self._fade_out)
        else:
            self.root.after(40, self._animate)

    def _fade_out(self) -> None:
        self.frame.destroy()
        self.on_done()


# ---------------------------------------------------------------------------
# Collapsible section
# ---------------------------------------------------------------------------

class CollapsibleCard:
    """A card with a clickable header that expands/collapses the content."""

    def __init__(self, parent: tk.Frame, title: str, icon: str = "",
                 accent: str = ACCENT, expanded: bool = True,
                 info_command=None) -> None:
        self.expanded = expanded
        self.accent = accent

        self.outer = tk.Frame(parent, bg=BG)
        self.outer.pack(fill=tk.X, padx=16, pady=(10, 0))

        # Header bar -- clickable
        self.header = tk.Frame(self.outer, bg=BG_CARD, cursor="hand2")
        self.header.pack(fill=tk.X)

        # Expand/collapse indicator
        arrow = ARROW_DOWN if expanded else ARROW_RIGHT
        self.arrow_label = tk.Label(
            self.header, text=arrow, font=FONT_SMALL,
            bg=BG_CARD, fg=FG_DIM, padx=8,
        )
        self.arrow_label.pack(side=tk.LEFT)

        # Icon
        if icon:
            tk.Label(
                self.header, text=icon, font=(_FAMILY, 13),
                bg=BG_CARD, fg=accent, padx=(0,),
            ).pack(side=tk.LEFT)

        # Title
        tk.Label(
            self.header, text=f"  {title}", font=FONT_SECTION,
            bg=BG_CARD, fg=accent, anchor=tk.W,
        ).pack(side=tk.LEFT, fill=tk.X)

        # Section info button (right side of header)
        self._info_btn = None
        if info_command:
            self._info_btn = tk.Button(
                self.header, text=" info ", font=(_FAMILY, 9, "bold"),
                bg=BORDER, fg=ACCENT, activebackground=BG_HOVER,
                activeforeground=FG, relief=tk.FLAT, padx=4, pady=0,
                cursor="hand2", command=info_command,
            )
            self._info_btn.pack(side=tk.RIGHT, padx=(0, 8))

        # Content area
        self.content = tk.Frame(
            self.outer, bg=BG_CARD,
            highlightbackground=BORDER, highlightthickness=1,
        )
        if expanded:
            self.content.pack(fill=tk.X, pady=(0, 0))

        # Bind click on entire header -- but skip the info button so its
        # command fires without also toggling the section.
        for widget in (self.header, self.arrow_label):
            widget.bind("<Button-1>", self._toggle)
        for child in self.header.winfo_children():
            if child is not self._info_btn:
                child.bind("<Button-1>", self._toggle)

    def _toggle(self, event=None) -> None:
        self.expanded = not self.expanded
        if self.expanded:
            self.content.pack(fill=tk.X, pady=(0, 0))
            self.arrow_label.configure(text=ARROW_DOWN)
        else:
            self.content.pack_forget()
            self.arrow_label.configure(text=ARROW_RIGHT)

    @property
    def frame(self) -> tk.Frame:
        return self.content


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class LynxRealEstateGUI:
    """Tkinter GUI application for Lynx Real Estate Analysis."""

    def __init__(self, cli_args) -> None:
        self.cli_args = cli_args
        self._current_report: AnalysisReport | None = None
        self._sections: list[CollapsibleCard] = []
        self._suppress_news_dialog: bool = False

        self.root = tk.Tk()
        self.root.title("Lynx Real Estate Analysis")
        self.root.configure(bg=BG)
        self.root.geometry("1150x900")
        self.root.minsize(960, 640)

        # Configure ttk scrollbar style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar",
                        background=BORDER, troughcolor=BG,
                        arrowcolor=FG_DIM, borderwidth=0)

        # Show splash, then build UI
        self._splash = SplashScreen(self.root, self._after_splash)

    def _after_splash(self) -> None:
        self._build_toolbar()
        self._build_result_area()
        self._show_welcome()

        # Suite-wide theme cycling (Ctrl+T / Ctrl+Shift+T)
        from lynx_realestate.tui.themes import HOUSE_THEMES as _HOUSE_THEMES
        from lynx_investor_core.gui_themes import register_gui_themes
        register_gui_themes(*_HOUSE_THEMES)
        self._theme_cycler = ThemeCycler(self.root, start="realestate-dark")
        self._theme_cycler.apply_current()
        self.root.bind_all("<Control-t>", lambda _: self._theme_cycler.next())
        self.root.bind_all("<Control-T>", lambda _: self._theme_cycler.previous())

        # Pre-fill and auto-analyze if ticker given
        identifier = getattr(self.cli_args, "identifier", None)
        if identifier:
            self.entry_ticker.insert(0, identifier)
            self.root.after(100, self._on_analyze)

    # ---- Toolbar ---------------------------------------------------------

    def _build_toolbar(self) -> None:
        toolbar = tk.Frame(self.root, bg=BG_SURFACE, pady=8, padx=16)
        toolbar.pack(fill=tk.X)

        # Left side: branding with logo
        brand = tk.Frame(toolbar, bg=BG_SURFACE)
        brand.pack(side=tk.LEFT, padx=(0, 20))

        # Toolbar logo
        self._toolbar_logo = None
        logo_path = Path(__file__).resolve().parent.parent.parent / "img" / "logo_sm_quarter_green.png"
        if logo_path.exists():
            try:
                self._toolbar_logo = tk.PhotoImage(file=str(logo_path))
                tk.Label(
                    brand, image=self._toolbar_logo, bg=BG_SURFACE,
                ).pack(side=tk.LEFT, padx=(0, 6))
            except tk.TclError:
                pass

        tk.Label(
            brand, text="Lynx Real Estate", font=(_FAMILY, 14, "bold"),
            bg=BG_SURFACE, fg=ACCENT,
        ).pack(side=tk.LEFT)

        # Separator
        sep = tk.Frame(toolbar, bg=BORDER, width=1, height=30)
        sep.pack(side=tk.LEFT, padx=(0, 16), fill=tk.Y)

        # Ticker input
        tk.Label(
            toolbar, text="Ticker:", font=FONT_SMALL_BOLD,
            bg=BG_SURFACE, fg=FG_DIM,
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.entry_ticker = tk.Entry(
            toolbar, font=FONT, width=16, bg=BG_INPUT, fg=FG,
            insertbackground=FG, relief=tk.FLAT, highlightthickness=2,
            highlightcolor=ACCENT, highlightbackground=BORDER,
        )
        self.entry_ticker.pack(side=tk.LEFT, padx=(0, 10), ipady=3)

        # Analyze button
        self.btn_analyze = tk.Button(
            toolbar, text=f"  {STAR} Analyze  ", font=FONT_BTN,
            bg=BTN_BG, fg=BTN_FG,
            activebackground=BTN_ACTIVE, activeforeground=BTN_FG,
            relief=tk.FLAT, padx=14, pady=4, cursor="hand2",
            command=self._on_analyze,
        )
        self.btn_analyze.pack(side=tk.LEFT, padx=(0, 6))

        # Clear button
        self.btn_clear = tk.Button(
            toolbar, text="  Clear  ", font=FONT_BTN,
            bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
            activebackground=BG_HOVER, activeforeground=FG,
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
            command=self._on_clear,
        )
        self.btn_clear.pack(side=tk.LEFT, padx=(0, 12))

        # Options row (checkboxes)
        opts = tk.Frame(toolbar, bg=BG_SURFACE)
        opts.pack(side=tk.LEFT, padx=(0, 8))

        self.var_refresh = tk.BooleanVar(
            value=getattr(self.cli_args, "refresh", False))
        self.var_no_reports = tk.BooleanVar(
            value=getattr(self.cli_args, "no_reports", False))
        self.var_no_news = tk.BooleanVar(
            value=getattr(self.cli_args, "no_news", False))

        for text, var in [("Refresh", self.var_refresh),
                          ("Skip filings", self.var_no_reports),
                          ("Skip news", self.var_no_news)]:
            cb = tk.Checkbutton(
                opts, text=text, variable=var,
                font=FONT_SMALL, bg=BG_SURFACE, fg=FG_DIM,
                selectcolor=BG_INPUT, activebackground=BG_SURFACE,
                activeforeground=FG, highlightthickness=0,
            )
            cb.pack(side=tk.LEFT, padx=(0, 6))

        # Export button (left group, after checkboxes)
        self.btn_export = tk.Button(
            toolbar, text="  Export  ", font=FONT_BTN,
            bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
            activebackground=BG_HOVER, activeforeground=FG,
            relief=tk.FLAT, padx=6, pady=3, cursor="hand2",
            command=self._on_export,
        )
        self.btn_export.pack(side=tk.LEFT, padx=(0, 6))

        # Keybindings button
        self.btn_keys = tk.Button(
            toolbar, text="  Keybindings  ", font=FONT_BTN,
            bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
            activebackground=BG_HOVER, activeforeground=FG,
            relief=tk.FLAT, padx=6, pady=3, cursor="hand2",
            command=self._show_controls,
        )
        self.btn_keys.pack(side=tk.LEFT, padx=(0, 6))

        # Themes button (pops a family-grouped menu)
        self._themes_btn = tk.Button(
            toolbar, text=" Themes \u25bc ", font=FONT_BTN,
            bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
            activebackground=BG_HOVER, activeforeground=FG,
            relief=tk.FLAT, padx=6, pady=3, cursor="hand2",
            command=self._show_themes_menu,
        )
        self._themes_btn.pack(side=tk.LEFT, padx=(0, 6))

        # Status bar -- shows progress during analysis
        self.status_var = tk.StringVar(value="")
        self.status_label = tk.Label(
            toolbar, textvariable=self.status_var, font=FONT_SMALL,
            bg=BG_SURFACE, fg=FG_DIM, anchor=tk.W,
        )
        self.status_label.pack(side=tk.LEFT, padx=(8, 0))

        # -- Right side buttons (packed right-to-left) --

        # Quit (rightmost)
        self.btn_quit = tk.Button(
            toolbar, text="  Quit  ", font=FONT_BTN,
            bg=BTN_DANGER_BG, fg=BTN_FG,
            activebackground="#e06080", activeforeground=BTN_FG,
            relief=tk.FLAT, padx=8, pady=3, cursor="hand2",
            command=self.root.destroy,
        )
        self.btn_quit.pack(side=tk.RIGHT, padx=(4, 0))

        # About (before Quit)
        self.btn_about = tk.Button(
            toolbar, text="  About  ", font=FONT_BTN,
            bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
            activebackground=BG_HOVER, activeforeground=FG,
            relief=tk.FLAT, padx=6, pady=3, cursor="hand2",
            command=self._on_about,
        )
        self.btn_about.pack(side=tk.RIGHT, padx=(4, 0))

        # Expand all / Collapse all (before About)
        self.btn_expand = tk.Button(
            toolbar, text=" Expand All ", font=FONT_BTN,
            bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
            activebackground=BG_HOVER, activeforeground=FG,
            relief=tk.FLAT, padx=6, pady=3, cursor="hand2",
            command=lambda: self._toggle_all(True),
        )
        self.btn_expand.pack(side=tk.RIGHT, padx=(2, 0))

        self.btn_collapse = tk.Button(
            toolbar, text=" Collapse All ", font=FONT_BTN,
            bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
            activebackground=BG_HOVER, activeforeground=FG,
            relief=tk.FLAT, padx=6, pady=3, cursor="hand2",
            command=lambda: self._toggle_all(False),
        )
        self.btn_collapse.pack(side=tk.RIGHT, padx=(2, 0))

        # Bind Enter key
        self.entry_ticker.bind("<Return>", lambda _: self._on_analyze())
        # Bind Escape to clear
        self.root.bind("<Escape>", lambda _: self._on_clear())
        # Ctrl+P: show keyboard shortcuts / controls
        self.root.bind("<Control-p>", lambda _: self._show_controls())
        # Hidden keybindings (F-keys bypass Entry widget interception)
        self.root.bind("<F9>", lambda _: self._ee_shake())
        self.root.bind("<F10>", lambda _: self._ee_rainbow())
        self.root.bind("<F11>", lambda _: self._ee_fortune())

    # ---- Scrollable result area ------------------------------------------

    def _build_result_area(self) -> None:
        container = tk.Frame(self.root, bg=BG)
        container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            container, orient=tk.VERTICAL, command=self.canvas.yview,
        )
        self.scroll_frame = tk.Frame(self.canvas, bg=BG)

        self.scroll_frame.bind(
            "<Configure>",
            lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor=tk.NW,
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width),
        )

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Mouse wheel scrolling (Linux + Windows + macOS)
        import platform
        def _on_mousewheel(e):
            if platform.system() == "Darwin":
                scroll_amount = -e.delta
            else:
                scroll_amount = -1 * (e.delta // 120)
            self.canvas.yview_scroll(scroll_amount, "units")
        self.canvas.bind_all(
            "<MouseWheel>",
            _on_mousewheel,
        )
        self.canvas.bind_all(
            "<Button-4>",
            lambda _: self.canvas.yview_scroll(-3, "units"),
        )
        self.canvas.bind_all(
            "<Button-5>",
            lambda _: self.canvas.yview_scroll(3, "units"),
        )
        # PageUp / PageDown (Ctrl+Home/End) — shared across every suite app.
        from lynx_investor_core.pager import bind_tk_paging
        bind_tk_paging(self.root, self.canvas)

    # ---- Welcome screen --------------------------------------------------

    def _show_welcome(self) -> None:
        """Show an empty-state welcome message."""
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        self._sections.clear()

        center = tk.Frame(self.scroll_frame, bg=BG)
        center.pack(expand=True, fill=tk.BOTH, pady=80)

        tk.Label(
            center, text=DIAMOND, font=(_FAMILY, 48),
            bg=BG, fg=ACCENT_DIM,
        ).pack(pady=(0, 16))

        tk.Label(
            center, text="Enter a ticker symbol and press Analyze",
            font=FONT_SUBTITLE, bg=BG, fg=FG_DIM,
        ).pack(pady=(0, 8))

        tk.Label(
            center, text="e.g. OCO.V, DML.TO, UUUU, FUU.V, or an ISIN",
            font=FONT_SMALL, bg=BG, fg=FG_SUBTLE,
        ).pack(pady=(0, 24))

        # Keyboard hints
        hints = tk.Frame(center, bg=BG)
        hints.pack()
        for key, action in [("Enter", "Analyze"), ("Escape", "Clear"),
                            ("Scroll", "Navigate results")]:
            row = tk.Frame(hints, bg=BG)
            row.pack(anchor=tk.W, pady=1)
            tk.Label(
                row, text=f"  {key}  ", font=FONT_SMALL_BOLD,
                bg=BORDER, fg=FG, padx=4,
            ).pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(
                row, text=action, font=FONT_SMALL,
                bg=BG, fg=FG_DIM,
            ).pack(side=tk.LEFT)

    # ---- Actions ---------------------------------------------------------

    def _on_analyze(self) -> None:
        ticker = self.entry_ticker.get().strip()
        if not ticker:
            self.status_var.set(f"{WARN_ICON}  Enter a ticker or ISIN")
            return

        self.btn_analyze.configure(state=tk.DISABLED)
        self.btn_clear.configure(state=tk.DISABLED)
        self.status_var.set(f"Analysing {ticker}...")

        # Read tkinter variables on the main thread for thread safety.
        refresh = self.var_refresh.get()
        no_reports = self.var_no_reports.get()
        no_news = self.var_no_news.get()

        # Clear the scroll area NOW on the main thread, before the
        # analysis thread starts.  This prevents a race where progress
        # callbacks fire before _prepare_progressive runs.
        self._prepare_progressive()

        thread = threading.Thread(
            target=self._run_analysis, args=(ticker, refresh, no_reports, no_news), daemon=True,
        )
        thread.start()

    def _on_clear(self) -> None:
        self.entry_ticker.delete(0, tk.END)
        self._current_report = None
        self.status_var.set("")
        self._show_welcome()
        self.entry_ticker.focus_set()

    def _on_export(self) -> None:
        if not self._current_report:
            self.status_var.set(f"{WARN_ICON}  Analyze a stock first")
            return

        from tkinter import filedialog
        fmt = tk.StringVar(value="html")
        win = tk.Toplevel(self.root)
        win.title("Export Report")
        win.configure(bg=BG)
        win.geometry("360x200")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="Export Format", font=FONT_BOLD, bg=BG, fg=ACCENT).pack(pady=(16, 8))
        for text, val in [("TXT (Plain Text)", "txt"), ("HTML", "html"), ("PDF (requires weasyprint)", "pdf")]:
            tk.Radiobutton(
                win, text=text, variable=fmt, value=val,
                font=FONT, bg=BG, fg=FG, selectcolor=BG_INPUT,
                activebackground=BG, activeforeground=FG,
            ).pack(anchor=tk.W, padx=40)

        def _do_export():
            report = self._current_report
            chosen = fmt.get()  # Capture value BEFORE destroying the window
            win.destroy()

            if not report:
                self.status_var.set(f"{WARN_ICON}  No report to export")
                return

            self.status_var.set(f"Exporting as {chosen.upper()}...")

            def _run():
                from lynx_realestate.export import ExportFormat, export_report
                try:
                    path = export_report(report, ExportFormat(chosen))
                    self.root.after(0, lambda p=str(path): self._show_export_success(p))
                except Exception as e:
                    self.root.after(0, lambda msg=str(e): self._show_export_error(msg))

            thread = threading.Thread(target=_run, daemon=True)
            thread.start()

        tk.Button(
            win, text="  Export  ", font=FONT_BTN,
            bg=BTN_BG, fg=BTN_FG, activebackground=BTN_ACTIVE,
            relief=tk.FLAT, padx=14, pady=4, cursor="hand2",
            command=_do_export,
        ).pack(pady=(12, 0))
        win.bind("<Escape>", lambda _: win.destroy())

    def _show_export_success(self, file_path: str) -> None:
        """Show a styled export success dialog with a clickable file link."""
        import subprocess
        import platform

        win = tk.Toplevel(self.root)
        win.title("Export Complete")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        # Success icon and title
        tk.Label(
            win, text=CHECK, font=(_FAMILY, 32),
            bg=BG, fg=GREEN,
        ).pack(pady=(20, 4))

        tk.Label(
            win, text="Report exported successfully", font=(_FAMILY, 13, "bold"),
            bg=BG, fg=FG,
        ).pack(pady=(0, 12))

        # File path card
        path_card = tk.Frame(win, bg=BG_CARD, padx=16, pady=10)
        path_card.pack(fill=tk.X, padx=24, pady=(0, 4))

        tk.Label(
            path_card, text="Saved to:", font=FONT_SMALL_BOLD,
            bg=BG_CARD, fg=FG_DIM, anchor=tk.W,
        ).pack(fill=tk.X)

        # Clickable file path
        path_label = tk.Label(
            path_card, text=file_path, font=FONT_MONO,
            bg=BG_CARD, fg=ACCENT, anchor=tk.W, cursor="hand2",
            wraplength=500, justify=tk.LEFT,
        )
        path_label.pack(fill=tk.X, pady=(2, 0))

        def _open_file():
            try:
                sys = platform.system()
                if sys == "Darwin":
                    subprocess.Popen(["open", file_path])
                elif sys == "Windows":
                    subprocess.Popen(["start", "", file_path], shell=True)
                else:
                    subprocess.Popen(["xdg-open", file_path])
            except Exception:
                pass

        def _open_folder():
            try:
                folder = str(Path(file_path).parent)
                sys = platform.system()
                if sys == "Darwin":
                    subprocess.Popen(["open", folder])
                elif sys == "Windows":
                    subprocess.Popen(["explorer", folder])
                else:
                    subprocess.Popen(["xdg-open", folder])
            except Exception:
                pass

        path_label.bind("<Button-1>", lambda _: _open_file())

        # Hover effect on the path label
        path_label.bind("<Enter>", lambda _: path_label.configure(fg=BTN_ACTIVE))
        path_label.bind("<Leave>", lambda _: path_label.configure(fg=ACCENT))

        # Hint
        tk.Label(
            win, text="Click the path to open the file",
            font=FONT_SMALL, bg=BG, fg=FG_SUBTLE,
        ).pack(pady=(2, 8))

        # Buttons row
        btn_row = tk.Frame(win, bg=BG)
        btn_row.pack(pady=(0, 16))

        tk.Button(
            btn_row, text="  Open File  ", font=FONT_BTN,
            bg=BTN_BG, fg=BTN_FG, activebackground=BTN_ACTIVE,
            relief=tk.FLAT, padx=12, pady=4, cursor="hand2",
            command=_open_file,
        ).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(
            btn_row, text="  Open Folder  ", font=FONT_BTN,
            bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
            activebackground=BG_HOVER, activeforeground=FG,
            relief=tk.FLAT, padx=12, pady=4, cursor="hand2",
            command=_open_folder,
        ).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(
            btn_row, text="  Close  ", font=FONT_BTN,
            bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
            activebackground=BG_HOVER, activeforeground=FG,
            relief=tk.FLAT, padx=12, pady=4, cursor="hand2",
            command=win.destroy,
        ).pack(side=tk.LEFT)

        win.bind("<Escape>", lambda _: win.destroy())

        # Center on screen
        win.update_idletasks()
        w, h = win.winfo_reqwidth(), win.winfo_reqheight()
        sx = (win.winfo_screenwidth() - w) // 2
        sy = (win.winfo_screenheight() - h) // 2
        win.geometry(f"{w}x{h}+{sx}+{sy}")

    def _show_export_error(self, msg: str) -> None:
        """Show a styled export error dialog."""
        win = tk.Toplevel(self.root)
        win.title("Export Failed")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        tk.Label(
            win, text=CROSS, font=(_FAMILY, 32),
            bg=BG, fg=RED,
        ).pack(pady=(20, 4))

        tk.Label(
            win, text="Export failed", font=(_FAMILY, 13, "bold"),
            bg=BG, fg=RED,
        ).pack(pady=(0, 12))

        error_card = tk.Frame(win, bg=BG_CARD, padx=16, pady=10)
        error_card.pack(fill=tk.X, padx=24, pady=(0, 12))

        tk.Label(
            error_card, text=msg, font=FONT,
            bg=BG_CARD, fg=FG, wraplength=450, justify=tk.LEFT,
        ).pack(fill=tk.X)

        btn_frame = tk.Frame(win, bg=BG)
        btn_frame.pack(pady=(0, 16))
        tk.Button(
            btn_frame, text="  Close  ", font=FONT_BTN,
            bg=BTN_BG, fg=BTN_FG, activebackground=BTN_ACTIVE,
            relief=tk.FLAT, padx=14, pady=4, cursor="hand2",
            command=win.destroy,
        ).pack(anchor=tk.CENTER)

        win.bind("<Escape>", lambda _: win.destroy())

        win.update_idletasks()
        w, h = win.winfo_reqwidth(), win.winfo_reqheight()
        sx = (win.winfo_screenwidth() - w) // 2
        sy = (win.winfo_screenheight() - h) // 2
        win.geometry(f"{w}x{h}+{sx}+{sy}")

    def _show_themes_menu(self) -> None:
        """Pop up a themes menu grouped by family."""
        from lynx_investor_core.gui_themes import list_themes_by_family
        menu = tk.Menu(self.root, tearoff=0)
        current = getattr(self._theme_cycler, "current_name", "")
        sector_family = ["realestate-dark", "realestate-light"]
        families = {"Sector": sector_family, **list_themes_by_family()}
        for family, names in families.items():
            sub = tk.Menu(menu, tearoff=0)
            for theme_name in names:
                label = ("\u25cf " if theme_name == current else "   ") + theme_name
                sub.add_command(
                    label=label,
                    command=lambda n=theme_name: self._select_theme(n),
                )
            menu.add_cascade(label=family, menu=sub)
        x = self._themes_btn.winfo_rootx()
        y = self._themes_btn.winfo_rooty() + self._themes_btn.winfo_height()
        menu.tk_popup(x, y)

    def _select_theme(self, theme_name: str) -> None:
        """Apply *theme_name*, falling back to sector house themes."""
        from lynx_investor_core.gui_themes import apply_theme, theme_by_name
        theme = theme_by_name(theme_name)
        if theme is None:
            return  # silently ignore unknown
        try:
            self._theme_cycler.set(theme_name)
        except ValueError:
            # House theme is not in the Suite cycler — apply directly.
            pass
        apply_theme(self.root, theme=theme)

    def _show_controls(self) -> None:
        """Show keyboard shortcuts and controls dialog (Ctrl+P)."""
        shortcuts = [
            ("Enter", "Analyze ticker"),
            ("Escape", "Clear / Reset"),
            ("Ctrl+P", "Show this controls dialog"),
            ("Ctrl+T", "Cycle theme"),
            ("Scroll", "Navigate results"),
            ("Click section header", "Expand / Collapse section"),
            ("Click ?", "Explain section or metric"),
        ]
        sections = []
        for key, action in shortcuts:
            sections.append((key, action))
        self._show_info_popup(
            "Keyboard Shortcuts & Controls",
            "lynx-realestate -- Graphical Interface",
            sections,
        )

    def _on_about(self) -> None:
        from lynx_realestate import get_about_text
        about = get_about_text()

        win = tk.Toplevel(self.root)
        win.title("About lynx-realestate")
        win.configure(bg=BG)
        win.configure(width=620, height=700)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        # Logo
        logo_path = Path(__file__).resolve().parent.parent.parent / "img" / "logo_sm_green.png"
        if logo_path.exists():
            try:
                win._about_logo = tk.PhotoImage(file=str(logo_path))
                tk.Label(
                    win, image=win._about_logo, bg=BG,
                ).pack(pady=(16, 8))
            except tk.TclError:
                pass

        # Title
        tk.Label(
            win, text=about['name'],
            font=(_FAMILY, 18, "bold"), bg=BG, fg=ACCENT,
        ).pack(pady=(4, 4))

        tk.Label(
            win, text=f"Version {about['version']}",
            font=FONT_SMALL, bg=BG, fg=FG_DIM,
        ).pack(pady=(0, 2))

        tk.Label(
            win, text=f"Part of {about['suite']} v{about['suite_version']}",
            font=FONT_SMALL, bg=BG, fg=ACCENT_DIM,
        ).pack(pady=(0, 2))

        tk.Label(
            win, text=f"Released {about['year']}",
            font=FONT_SMALL, bg=BG, fg=FG_DIM,
        ).pack(pady=(0, 16))

        # Author info
        info_frame = tk.Frame(win, bg=BG_CARD, padx=20, pady=12)
        info_frame.pack(fill=tk.X, padx=24, pady=(0, 12))

        for label, value in [
            ("Developed by", about["author"]),
            ("Contact", about["email"]),
            ("License", about["license"]),
        ]:
            row = tk.Frame(info_frame, bg=BG_CARD)
            row.pack(fill=tk.X, pady=2)
            tk.Label(
                row, text=f"{label}:", font=FONT_BOLD,
                bg=BG_CARD, fg=ACCENT, width=14, anchor=tk.E,
            ).pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(
                row, text=value, font=FONT,
                bg=BG_CARD, fg=FG, anchor=tk.W,
            ).pack(side=tk.LEFT)

        # Description
        tk.Label(
            win, text=about["description"], font=FONT_SMALL,
            bg=BG, fg=FG_DIM, wraplength=560, justify=tk.CENTER,
        ).pack(padx=24, pady=(0, 12))

        # License text in scrollable frame
        license_frame = tk.Frame(win, bg=BG_CARD)
        license_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 12))

        tk.Label(
            license_frame, text="BSD 3-Clause License",
            font=FONT_SMALL_BOLD, bg=BG_CARD, fg=ACCENT,
        ).pack(pady=(8, 4))

        license_inner = tk.Frame(license_frame, bg=BG_CARD)
        license_inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        license_scroll = ttk.Scrollbar(license_inner, orient=tk.VERTICAL)
        license_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        license_text = tk.Text(
            license_inner, font=FONT_SMALL, bg=BG_CARD, fg=FG_DIM,
            wrap=tk.WORD, relief=tk.FLAT, height=14,
            highlightthickness=0, padx=12, pady=4,
            yscrollcommand=license_scroll.set,
        )
        license_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        license_scroll.configure(command=license_text.yview)
        license_text.insert("1.0", about["license_text"])
        license_text.configure(state=tk.DISABLED)

        # Close button (centered)
        close_frame = tk.Frame(win, bg=BG)
        close_frame.pack(fill=tk.X, pady=(8, 16))
        tk.Button(
            close_frame, text="  Close  ", font=(_FAMILY, 11, "bold"),
            bg=BTN_BG, fg=BTN_FG,
            activebackground=BTN_ACTIVE, activeforeground=BTN_FG,
            relief=tk.FLAT, padx=20, pady=6, cursor="hand2",
            command=win.destroy,
        ).pack(anchor=tk.CENTER)

        win.bind("<Escape>", lambda _: win.destroy())

        # Center on screen after all widgets are packed
        win.update_idletasks()
        w = win.winfo_reqwidth()
        h = win.winfo_reqheight()
        sx = (win.winfo_screenwidth() - w) // 2
        sy = (win.winfo_screenheight() - h) // 2
        win.geometry(f"{w}x{h}+{sx}+{sy}")

    def _toggle_all(self, expand: bool) -> None:
        for card in self._sections:
            if expand and not card.expanded:
                card._toggle()
            elif not expand and card.expanded:
                card._toggle()

    # ---- Hidden features -------------------------------------------------

    def _ee_shake(self) -> None:
        from lynx_realestate.easter import tk_fireworks
        tk_fireworks(self.root)

    def _ee_rainbow(self) -> None:
        from lynx_realestate.easter import tk_rainbow_title
        tk_rainbow_title(self.root)

    def _ee_fortune(self) -> None:
        from lynx_realestate.easter import FORTUNE_QUOTES
        import random
        quote = random.choice(FORTUNE_QUOTES)
        messagebox.showinfo("\u2728 Fortune Cookie \u2728", quote)

    # ---- Analysis -------------------------------------------------------

    def _run_analysis(self, identifier: str, refresh: bool, no_reports: bool, no_news: bool) -> None:
        try:
            from lynx_realestate.core.analyzer import run_progressive_analysis
            from lynx_realestate.core.storage import is_testing

            refresh = refresh or is_testing()

            def on_progress(stage: str, report: AnalysisReport) -> None:
                """Dispatch each stage to the UI thread."""
                try:
                    self.root.after(0, self._render_stage, stage, report)
                except tk.TclError:
                    pass  # Root destroyed

            report = run_progressive_analysis(
                identifier=identifier,
                download_reports=not no_reports,
                download_news=not no_news,
                max_filings=getattr(self.cli_args, "max_filings", 10),
                verbose=getattr(self.cli_args, "verbose", False),
                refresh=refresh,
                on_progress=on_progress,
            )

            self._current_report = report
            try:
                self.root.after(0, self._finalize_report, report)
            except tk.TclError:
                pass

        except Exception as e:
            from lynx_realestate.core.analyzer import SectorMismatchError
            if isinstance(e, SectorMismatchError):
                try:
                    self.root.after(0, self._show_sector_mismatch, str(e))
                except tk.TclError:
                    pass
            else:
                msg = str(e) or type(e).__name__
                try:
                    self.root.after(0, self._show_analysis_error, msg)
                except tk.TclError:
                    pass

    def _prepare_progressive(self) -> None:
        """Clear the scroll area and prepare for progressive section mounting."""
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        self._sections.clear()
        self.status_var.set("Fetching data...")

    def _render_stage(self, stage: str, report: AnalysisReport) -> None:
        """Render a single analysis stage into the scroll area."""
        self._current_report = report
        try:
            if stage == "profile":
                self._render_tier_banner(report)
                self._render_profile(report)
                self._render_sector_industry(report)
                p = report.profile
                self.status_var.set(
                    f"Analyzing {_s(p.name)} ({_s(p.ticker)})..."
                )
            elif stage == "financials":
                self._render_financials(report)
            elif stage == "valuation":
                self._render_valuation(report)
            elif stage == "profitability":
                self._render_profitability(report)
            elif stage == "solvency":
                self._render_solvency(report)
            elif stage == "growth":
                self._render_growth(report)
            elif stage == "share_structure":
                self._render_share_structure(report)
            elif stage == "real_estate_quality":
                self._render_real_estate_quality(report)
            elif stage == "intrinsic_value":
                self._render_intrinsic_value(report)
            elif stage == "market_intelligence":
                self._render_market_intelligence(report)
            elif stage == "filings":
                self._render_filings(report)
            elif stage == "news":
                self._render_news(report)
            elif stage == "conclusion":
                self._render_conclusion(report)
            elif stage == "complete":
                # If no sections rendered yet (cached report loaded with
                # only the "complete" stage), render everything now.
                if not self._sections:
                    self._render_all_sections(report)
                # Otherwise: all sections were already rendered
                # progressively — nothing to do.

            # Update scroll region after each section
            self.scroll_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception:
            pass  # Silently ignore render errors for individual sections

    def _render_all_sections(self, report: AnalysisReport) -> None:
        """Render all sections at once (used for cached reports only)."""
        self._render_tier_banner(report)
        self._render_profile(report)
        self._render_sector_industry(report)
        self._render_valuation(report)
        self._render_profitability(report)
        self._render_solvency(report)
        self._render_growth(report)
        self._render_share_structure(report)
        self._render_real_estate_quality(report)
        self._render_intrinsic_value(report)
        self._render_market_intelligence(report)
        self._render_financials(report)
        self._render_filings(report)
        self._render_news(report)
        self._render_conclusion(report)

    def _finalize_report(self, report: AnalysisReport) -> None:
        """Called after the full analysis completes."""
        self.status_var.set(f"{CHECK}  Analysis complete")
        self.btn_analyze.configure(state=tk.NORMAL)
        self.btn_clear.configure(state=tk.NORMAL)
        # Bottom padding
        tk.Frame(self.scroll_frame, bg=BG, height=24).pack(fill=tk.X)
        self.scroll_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _show_analysis_error(self, msg: str) -> None:
        self.status_var.set(f"{WARN_ICON}  Error")
        self.btn_analyze.configure(state=tk.NORMAL)
        self.btn_clear.configure(state=tk.NORMAL)
        messagebox.showerror("Analysis Error", msg)

    def _show_sector_mismatch(self, msg: str) -> None:
        """Show a prominent red sector mismatch warning dialog."""
        self.status_var.set(f"{CROSS}  SECTOR MISMATCH")
        self.btn_analyze.configure(state=tk.NORMAL)
        self.btn_clear.configure(state=tk.NORMAL)

        win = tk.Toplevel(self.root)
        win.title("SECTOR MISMATCH — ANALYSIS BLOCKED")
        win.configure(bg="#3a0a0a")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        # Red warning icon
        tk.Label(
            win, text=f"{WARN_ICON} {CROSS} {WARN_ICON}", font=(_FAMILY, 36),
            bg="#3a0a0a", fg="#ff4444",
        ).pack(pady=(20, 8))

        # Title
        tk.Label(
            win, text="WRONG SECTOR", font=(_FAMILY, 20, "bold"),
            bg="#3a0a0a", fg="#ff4444",
        ).pack(pady=(0, 8))

        tk.Label(
            win, text="ANALYSIS BLOCKED", font=(_FAMILY, 14, "bold"),
            bg="#3a0a0a", fg="#ff6666",
        ).pack(pady=(0, 16))

        # Message
        msg_frame = tk.Frame(win, bg="#2a0808", padx=20, pady=14)
        msg_frame.pack(fill=tk.X, padx=24, pady=(0, 12))
        tk.Label(
            msg_frame, text=msg, font=FONT,
            bg="#2a0808", fg="#ffaaaa", wraplength=520, justify=tk.LEFT,
        ).pack(fill=tk.X)

        # Specialization note
        tk.Label(
            win,
            text=(
                "This tool is specialized ONLY for:\n"
                "Real Estate  |  REITs  |  Property Management\n"
                "Operating Companies  |  Real Estate Services"
            ),
            font=(_FAMILY, 11, "bold"),
            bg="#3a0a0a", fg="#ff8888", justify=tk.CENTER,
        ).pack(padx=24, pady=(0, 16))

        # Close button
        tk.Button(
            win, text="  Close  ", font=(_FAMILY, 11, "bold"),
            bg="#ff4444", fg="#ffffff",
            activebackground="#cc3333", activeforeground="#ffffff",
            relief=tk.FLAT, padx=20, pady=6, cursor="hand2",
            command=win.destroy,
        ).pack(pady=(0, 20))

        win.bind("<Escape>", lambda _: win.destroy())

        # Center on screen
        win.update_idletasks()
        w, h = win.winfo_reqwidth(), win.winfo_reqheight()
        sx = (win.winfo_screenwidth() - w) // 2
        sy = (win.winfo_screenheight() - h) // 2
        win.geometry(f"{w}x{h}+{sx}+{sy}")

    # ---- Tier banner -----------------------------------------------------

    def _render_tier_banner(self, r: AnalysisReport) -> None:
        p = r.profile
        tier = p.tier
        fg_col, bg_col = TIER_COLORS.get(tier, (ACCENT, BG_CARD))

        banner = tk.Frame(self.scroll_frame, bg=bg_col, pady=12, padx=20)
        banner.pack(fill=tk.X, padx=16, pady=(12, 0))

        # Company name row
        name_row = tk.Frame(banner, bg=bg_col)
        name_row.pack(fill=tk.X)

        tk.Label(
            name_row, text=_s(p.name), font=(_FAMILY, 18, "bold"),
            bg=bg_col, fg=FG, anchor=tk.W,
        ).pack(side=tk.LEFT)

        tk.Label(
            name_row, text=f"  ({_s(p.ticker)})", font=(_FAMILY, 14),
            bg=bg_col, fg=FG_DIM, anchor=tk.W,
        ).pack(side=tk.LEFT)

        if p.isin:
            tk.Label(
                name_row, text=f"  ISIN: {p.isin}", font=FONT_SMALL,
                bg=bg_col, fg=FG_SUBTLE, anchor=tk.W,
            ).pack(side=tk.LEFT, padx=(12, 0))

        # Info row
        info_row = tk.Frame(banner, bg=bg_col)
        info_row.pack(fill=tk.X, pady=(6, 0))

        # Tier badge
        badge_frame = tk.Frame(info_row, bg=fg_col, padx=8, pady=2)
        badge_frame.pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(
            badge_frame, text=_safe_tier(tier), font=FONT_TIER,
            bg=fg_col, fg=BG,
        ).pack()

        # Stage badge
        stage = p.stage
        stage_fg, stage_bg = STAGE_COLORS.get(stage, (ACCENT, BG_CARD))
        stage_badge = tk.Frame(info_row, bg=stage_fg, padx=8, pady=2)
        stage_badge.pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(
            stage_badge, text=stage.value if isinstance(stage, CompanyStage) else str(stage),
            font=FONT_STAGE, bg=stage_fg, fg=BG,
        ).pack()

        # Commodity badge
        property_type = p.primary_property_type
        if property_type:
            property_type_text = property_type.value if hasattr(property_type, 'value') else str(property_type)
            comm_badge = tk.Frame(info_row, bg=YELLOW, padx=6, pady=2)
            comm_badge.pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(
                comm_badge, text=property_type_text, font=FONT_SMALL_BOLD,
                bg=YELLOW, fg=BG,
            ).pack()

        # Jurisdiction badge
        jurisdiction = p.jurisdiction_tier
        if jurisdiction and hasattr(jurisdiction, 'value'):
            jur_text = jurisdiction.value
            jur_color = GREEN if "Tier 1" in jur_text else (YELLOW if "Tier 2" in jur_text else RED)
            jur_badge = tk.Frame(info_row, bg=jur_color, padx=6, pady=2)
            jur_badge.pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(
                jur_badge, text=jur_text, font=FONT_SMALL_BOLD,
                bg=jur_color, fg=BG,
            ).pack()

        # Quick stats
        parts = []
        if p.sector:
            parts.append(p.sector)
        if p.industry:
            parts.append(p.industry)
        if p.country:
            parts.append(p.country)
        if p.market_cap:
            parts.append(f"MCap: {_money(p.market_cap)}")

        if parts:
            tk.Label(
                info_row, text=f"  {BULLET}  ".join(parts), font=FONT_SMALL,
                bg=bg_col, fg=FG_DIM, anchor=tk.W,
            ).pack(side=tk.LEFT, padx=(8, 0))

    # ---- Profile ---------------------------------------------------------

    def _render_profile(self, r: AnalysisReport) -> None:
        p = r.profile
        card = CollapsibleCard(
            self.scroll_frame, "Company Profile",
            icon=ICON_PROFILE, accent=ACCENT, expanded=True,
            info_command=lambda: self._show_section_info("profile"),
        )
        self._sections.append(card)
        frame = card.frame

        # Split layout: metrics left (1/3), description right (2/3)
        split = tk.Frame(frame, bg=BG_CARD)
        split.pack(fill=tk.X)
        split.columnconfigure(0, weight=1)
        split.columnconfigure(1, weight=2)

        # Left side: key-value metrics (1/3)
        left = tk.Frame(split, bg=BG_CARD)
        left.grid(row=0, column=0, sticky="nsew")

        # Stage display
        stage_text = p.stage.value if isinstance(p.stage, CompanyStage) else str(p.stage)
        # Commodity display
        property_type_text = p.primary_property_type.value if hasattr(p.primary_property_type, 'value') else str(p.primary_property_type)
        # Jurisdiction display
        jurisdiction_text = p.jurisdiction_tier.value if hasattr(p.jurisdiction_tier, 'value') else str(p.jurisdiction_tier)
        jurisdiction_country_text = _s(p.jurisdiction_country) if hasattr(p, 'jurisdiction_country') and p.jurisdiction_country else ""
        if jurisdiction_country_text and jurisdiction_country_text != "N/A":
            jurisdiction_text = f"{jurisdiction_text} ({jurisdiction_country_text})"

        # (label, value, optional fg override)
        rows: list[tuple[str, str, str]] = [
            ("Company", _s(p.name), FG),
            ("Ticker", _s(p.ticker), FG),
            ("ISIN", _s(p.isin), FG),
            ("Tier", _safe_tier(p.tier), FG),
            ("Stage", stage_text, FG),
            ("Property Type", property_type_text, YELLOW),
            ("Jurisdiction", jurisdiction_text, FG),
            ("Sector", _s(p.sector), FG),
            ("Industry", _s(p.industry), FG),
            ("Country", _s(p.country), FG),
            ("Exchange", _s(p.exchange), FG),
            ("Currency", _s(p.currency), YELLOW),
            ("Market Cap", _money(p.market_cap), FG),
            ("Employees", f"{p.employees:,}" if p.employees else "N/A", FG),
        ]
        if p.website:
            rows.append(("Website", p.website, FG))

        for i, (label, value, fg_color) in enumerate(rows):
            bg = BG_INPUT if i % 2 == 0 else BG_CARD
            row = tk.Frame(left, bg=bg)
            row.pack(fill=tk.X)
            tk.Label(
                row, text=label, font=FONT_BOLD, bg=bg, fg=ACCENT,
                width=14, anchor=tk.E, pady=3,
            ).pack(side=tk.LEFT, padx=(12, 6))
            tk.Label(
                row, text=value, font=FONT, bg=bg, fg=fg_color,
                anchor=tk.W, pady=3,
            ).pack(side=tk.LEFT, padx=(6, 12))

        # Right side: business description (2/3)
        right = tk.Frame(split, bg=BG_CARD, padx=12, pady=8)
        right.grid(row=0, column=1, sticky="nsew")

        # Vertical separator
        tk.Frame(right, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

        desc_area = tk.Frame(right, bg=BG_CARD)
        desc_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            desc_area, text="Business Description", font=FONT_SMALL_BOLD,
            bg=BG_CARD, fg=ACCENT_DIM, anchor=tk.W,
        ).pack(fill=tk.X, pady=(0, 6))

        desc = p.description or "No description available."
        tk.Label(
            desc_area, text=desc, font=FONT,
            bg=BG_CARD, fg=FG_DIM, wraplength=600,
            justify=tk.LEFT, anchor=tk.NW,
        ).pack(fill=tk.BOTH, expand=True)

    # ---- Sector & Industry Insights ----------------------------------------

    def _render_sector_industry(self, r: AnalysisReport) -> None:
        from lynx_realestate.metrics.sector_insights import get_sector_insight, get_industry_insight

        p = r.profile
        items = []
        if p.sector:
            si = get_sector_insight(p.sector)
            if si:
                items.append((f"Sector: {si.sector}", si))
        if p.industry:
            ii = get_industry_insight(p.industry)
            if ii:
                items.append((f"Industry: {ii.industry}", ii))

        for label, info in items:
            card = CollapsibleCard(
                self.scroll_frame, label,
                icon="\U0001f4d6", accent=LAVENDER, expanded=False,
            )
            self._sections.append(card)
            frame = card.frame
            rows = [
                ("Overview", info.overview),
                ("Critical Metrics", ", ".join(info.critical_metrics)),
                ("Key Risks", ", ".join(info.key_risks)),
                ("What to Watch", ", ".join(info.what_to_watch)),
                ("Typical Valuation", info.typical_valuation),
            ]
            for i, (lbl, value) in enumerate(rows):
                bg = BG_INPUT if i % 2 == 0 else BG_CARD
                row_frame = tk.Frame(frame, bg=bg)
                row_frame.pack(fill=tk.X)
                tk.Label(
                    row_frame, text=lbl, font=FONT_BOLD, bg=bg, fg=ACCENT,
                    width=22, anchor=tk.E, pady=3,
                ).pack(side=tk.LEFT, padx=(12, 6))
                tk.Label(
                    row_frame, text=value, font=FONT, bg=bg, fg=FG,
                    anchor=tk.W, pady=3, wraplength=700, justify=tk.LEFT,
                ).pack(side=tk.LEFT, padx=(6, 12))

    # ---- Valuation -------------------------------------------------------

    def _render_valuation(self, r: AnalysisReport) -> None:
        v = r.valuation
        if v is None:
            return
        card = CollapsibleCard(
            self.scroll_frame, "Valuation",
            icon=ICON_VALUATION, accent=YELLOW, expanded=False,
            info_command=lambda: self._show_section_info("valuation"),
        )
        self._sections.append(card)
        frame = card.frame

        stage = r.profile.stage
        tier = _get_tier(r)
        rel = lambda key: get_relevance(key, tier, "valuation", stage)

        rows = [
            ("P/E (Trailing)", _num(v.pe_trailing), _ape(v.pe_trailing), "pe_trailing"),
            ("P/E (Forward)", _num(v.pe_forward), _ape(v.pe_forward), "pe_forward"),
            ("P/B Ratio", _num(v.pb_ratio), _thr(v.pb_ratio, [(1, "Below Book"), (1.5, "Cheap"), (3, "Fair")], "Premium"), "pb_ratio"),
            ("P/S Ratio", _num(v.ps_ratio), "", "ps_ratio"),
            ("P/FCF", _num(v.p_fcf), _thr(v.p_fcf, [(10, "Cheap"), (20, "Fair")], "Expensive"), "p_fcf"),
            ("EV/EBITDA", _num(v.ev_ebitda), _thr(v.ev_ebitda, [(8, "Cheap"), (12, "Fair"), (18, "Expensive")], "Very Expensive"), "ev_ebitda"),
            ("EV/Revenue", _num(v.ev_revenue), _thr(v.ev_revenue, [(1, "Very cheap"), (3, "Cheap"), (5, "Fair"), (8, "Expensive")], "Very expensive"), "ev_revenue"),
            ("PEG Ratio", _num(v.peg_ratio), _thr(v.peg_ratio, [(1, "Undervalued"), (2, "Fair")], "Overvalued"), "peg_ratio"),
            ("Earnings Yield", _pct(v.earnings_yield), _thr(v.earnings_yield, [(0, "Negative"), (0.05, "Low"), (0.07, "Fair"), (0.10, "Good")], "Excellent"), "earnings_yield"),
            ("Dividend Yield", _pct(v.dividend_yield), _thr(v.dividend_yield, [(0, "No dividend"), (0.02, "Low"), (0.04, "Moderate"), (0.06, "High")], "Very high"), "dividend_yield"),
            ("P/Tangible Book", _num(v.price_to_tangible_book), _thr(v.price_to_tangible_book, [(0.67, "Deep Value"), (1, "Below Book"), (1.5, "Near Book")], "Premium"), "price_to_tangible_book"),
            ("P/NCAV (Net-Net)", _num(v.price_to_ncav), _thr(v.price_to_ncav, [(0.67, "Classic Net-Net"), (1, "Below NCAV"), (1.5, "Near NCAV")], "Above NCAV"), "price_to_ncav"),
            ("Cash/Market Cap", _pct(v.cash_to_market_cap), _thr(v.cash_to_market_cap, [(0.10, "Low"), (0.30, "Moderate"), (0.50, "Strong")], "Very Strong Cash Backing"), ""),
            ("Enterprise Value", _money(v.enterprise_value), "", ""),
            ("Market Cap", _money(v.market_cap), "", ""),
        ]
        for i, (label, value, assessment, key) in enumerate(rows):
            self._add_metric_row_rel(frame, i, label, value, assessment,
                                     metric_key=key, relevance=rel(key) if key else Relevance.RELEVANT)

    # ---- Profitability ---------------------------------------------------

    def _render_profitability(self, r: AnalysisReport) -> None:
        p = r.profitability
        if p is None:
            return

        stage = r.profile.stage
        tier = _get_tier(r)
        rel = lambda key: get_relevance(key, tier, "profitability", stage)

        rows = [
            ("ROE", _pct(p.roe), _thr(p.roe, [(0, "Negative"), (0.10, "Below Avg"), (0.15, "Good"), (0.20, "Excellent")], "Outstanding"), "roe"),
            ("ROA", _pct(p.roa), _thr(p.roa, [(0, "Negative"), (0.05, "Low"), (0.10, "Good")], "Excellent"), "roa"),
            ("ROIC", _pct(p.roic), _thr(p.roic, [(0, "Negative"), (0.07, "Below WACC"), (0.10, "Good"), (0.15, "Wide Moat")], "Exceptional"), "roic"),
            ("Gross Margin", _pct(p.gross_margin), _thr(p.gross_margin, [(0, "Negative"), (0.20, "Thin"), (0.40, "Good"), (0.60, "Strong")], "Very strong"), "gross_margin"),
            ("Operating Margin", _pct(p.operating_margin), _thr(p.operating_margin, [(0, "Loss"), (0.05, "Thin"), (0.15, "Good"), (0.25, "Excellent")], "Outstanding"), "operating_margin"),
            ("Net Margin", _pct(p.net_margin), _thr(p.net_margin, [(0, "Loss"), (0.05, "Thin"), (0.10, "Good"), (0.20, "Excellent")], "Outstanding"), "net_margin"),
            ("FCF Margin", _pct(p.fcf_margin), _thr(p.fcf_margin, [(0, "Negative"), (0.05, "Weak"), (0.10, "Good"), (0.20, "Strong")], "Excellent"), "fcf_margin"),
            ("EBITDA Margin", _pct(p.ebitda_margin), _thr(p.ebitda_margin, [(0, "Negative"), (0.05, "Thin"), (0.15, "Good"), (0.30, "Excellent")], "Outstanding"), "ebitda_margin"),
        ]

        all_irrelevant = all(rel(key) == Relevance.IRRELEVANT for _, _, _, key in rows)

        card = CollapsibleCard(
            self.scroll_frame, "Profitability",
            icon=ICON_PROFIT, accent=GREEN, expanded=False,
            info_command=lambda: self._show_section_info("profitability"),
        )
        self._sections.append(card)
        frame = card.frame

        if all_irrelevant:
            stage_name = _s(r.profile.stage.value) if hasattr(r.profile.stage, "value") else _s(r.profile.stage)
            note = tk.Label(
                frame,
                text=(f"Profitability metrics are not applicable for {stage_name} stage companies. "
                      f"Pre-revenue real-estate companies have no meaningful margins or returns on capital to evaluate."),
                font=FONT_SMALL, bg=BG_CARD, fg=FG_DIM,
                wraplength=700, justify=tk.LEFT, anchor=tk.W,
                padx=16, pady=12,
            )
            note.pack(fill=tk.X)
        else:
            for i, (label, value, assessment, key) in enumerate(rows):
                self._add_metric_row_rel(frame, i, label, value, assessment,
                                         metric_key=key, relevance=rel(key))

    # ---- Solvency --------------------------------------------------------

    def _render_solvency(self, r: AnalysisReport) -> None:
        s = r.solvency
        if s is None:
            return
        card = CollapsibleCard(
            self.scroll_frame, "Solvency & Financial Health",
            icon=ICON_SOLVENCY, accent=RED, expanded=False,
            info_command=lambda: self._show_section_info("solvency"),
        )
        self._sections.append(card)
        frame = card.frame

        stage = r.profile.stage
        tier = _get_tier(r)
        rel = lambda key: get_relevance(key, tier, "solvency", stage)

        def _burn_pct_assessment(val):
            if val is None:
                return ""
            try:
                v = float(val)
                if v <= 0:
                    return "Cash flow positive"
                if v < 0.04:
                    return "Low burn"
                if v < 0.08:
                    return "Moderate burn"
                return "High burn rate"
            except Exception:
                return ""

        rows = [
            ("Debt/Equity", _num(s.debt_to_equity), _thr(s.debt_to_equity, [(0.3, "Very Conservative"), (0.5, "Conservative"), (1.0, "Moderate"), (2.0, "High")], "Very High"), "debt_to_equity"),
            ("Debt/EBITDA", _num(s.debt_to_ebitda), _thr(s.debt_to_ebitda, [(1, "Very Low"), (2, "Manageable"), (3, "Moderate")], "Heavy"), "debt_to_ebitda"),
            ("Current Ratio", _num(s.current_ratio), _thr(s.current_ratio, [(1.0, "Liquidity Risk"), (1.5, "Adequate"), (2.0, "Good")], "Strong"), "current_ratio"),
            ("Quick Ratio", _num(s.quick_ratio), "", "quick_ratio"),
            ("Interest Coverage", _num(s.interest_coverage, 1), _thr(s.interest_coverage, [(1, "Cannot cover"), (2, "Tight"), (4, "Adequate"), (8, "Strong")], "Very strong"), "interest_coverage"),
            ("Altman Z-Score", _num(s.altman_z_score), _thr(s.altman_z_score, [(1.81, "Distress"), (2.99, "Grey Zone")], "Safe"), "altman_z_score"),
            ("Cash Burn Rate (/yr)", _money(s.cash_burn_rate), _burn(s.cash_burn_rate), "cash_burn_rate"),
            ("Burn % of MCap (/yr)", _pct(s.burn_as_pct_of_market_cap), _burn_pct_assessment(s.burn_as_pct_of_market_cap), "burn_as_pct_of_market_cap"),
            ("Cash Runway", f"{s.cash_runway_years:.1f} yrs" if s.cash_runway_years is not None else "N/A", "", "cash_runway_years"),
            ("Working Capital", _money(s.working_capital), "", "working_capital"),
            ("Cash Per Share", f"${s.cash_per_share:.2f}" if s.cash_per_share is not None else "N/A", "", "cash_per_share"),
            ("NCAV Per Share", f"${s.ncav_per_share:.4f}" if s.ncav_per_share is not None else "N/A", "", "ncav_per_share"),
            ("Total Debt", _money(s.total_debt), "", "total_debt"),
            ("Total Cash", _money(s.total_cash), "", "total_cash"),
            ("Net Debt", _money(s.net_debt), "", "net_debt"),
        ]
        for i, (label, value, assessment, key) in enumerate(rows):
            self._add_metric_row_rel(frame, i, label, value, assessment,
                                     metric_key=key, relevance=rel(key) if key else Relevance.RELEVANT)

    # ---- Growth ----------------------------------------------------------

    def _render_growth(self, r: AnalysisReport) -> None:
        g = r.growth
        if g is None:
            return
        card = CollapsibleCard(
            self.scroll_frame, "Growth",
            icon=ICON_GROWTH, accent=MAUVE, expanded=False,
            info_command=lambda: self._show_section_info("growth"),
        )
        self._sections.append(card)
        frame = card.frame

        stage = r.profile.stage
        tier = _get_tier(r)
        rel = lambda key: get_relevance(key, tier, "growth", stage)

        def _ga(val):
            return _thr(val, [(0, "Declining"), (0.10, "Positive"), (0.25, "Good")], "Very strong") if val is not None else ""
        def _ca(val):
            return _thr(val, [(0, "Declining"), (0.08, "Positive"), (0.15, "Good")], "Excellent") if val is not None else ""
        def _da(val):
            if val is None: return ""
            try:
                v = float(val)
                if v < -0.02: return "Buybacks"
                if v < 0.01: return "Minimal"
                if v < 0.05: return "Modest"
                if v < 0.10: return "Significant"
                return "Heavy dilution"
            except Exception: return ""

        def _dr(val):
            """Dilution ratio assessment."""
            if val is None: return ""
            try:
                v = float(val)
                if v < 1.05: return "Minimal overhang"
                if v < 1.15: return "Moderate overhang"
                if v < 1.30: return "Significant overhang"
                return "Heavy warrant/option overhang"
            except Exception: return ""

        rows = [
            ("Revenue Growth (YoY)", _pct(g.revenue_growth_yoy), _ga(g.revenue_growth_yoy), "revenue_growth_yoy"),
            ("Revenue CAGR (3Y)", _pct(g.revenue_cagr_3y), _ca(g.revenue_cagr_3y), "revenue_cagr_3y"),
            ("Revenue CAGR (5Y)", _pct(g.revenue_cagr_5y), _ca(g.revenue_cagr_5y), "revenue_cagr_5y"),
            ("Earnings Growth (YoY)", _pct(g.earnings_growth_yoy), _ga(g.earnings_growth_yoy), "earnings_growth_yoy"),
            ("Earnings CAGR (3Y)", _pct(g.earnings_cagr_3y), _ca(g.earnings_cagr_3y), "earnings_cagr_3y"),
            ("Earnings CAGR (5Y)", _pct(g.earnings_cagr_5y), _ca(g.earnings_cagr_5y), "earnings_cagr_5y"),
            ("FCF Growth (YoY)", _pct(g.fcf_growth_yoy), _ga(g.fcf_growth_yoy), "fcf_growth_yoy"),
            ("Book Value Growth (YoY)", _pct(g.book_value_growth_yoy), _ga(g.book_value_growth_yoy), "book_value_growth_yoy"),
            ("Share Dilution (YoY)", _pct(g.shares_growth_yoy), _da(g.shares_growth_yoy), "shares_growth_yoy"),
            ("Dilution CAGR (3Y)", _pct(g.shares_growth_3y_cagr), _da(g.shares_growth_3y_cagr), "shares_growth_3y_cagr"),
            ("Dilution Ratio", _num(g.dilution_ratio), _dr(g.dilution_ratio), ""),
        ]
        for i, (label, value, assessment, key) in enumerate(rows):
            self._add_metric_row_rel(frame, i, label, value, assessment,
                                     metric_key=key, relevance=rel(key) if key else Relevance.RELEVANT)

    # ---- Share Structure -------------------------------------------------

    def _render_share_structure(self, r: AnalysisReport) -> None:
        ss = r.share_structure
        if ss is None:
            return
        card = CollapsibleCard(
            self.scroll_frame, "Share Structure",
            icon=ICON_SHARES, accent=SKY, expanded=False,
            info_command=lambda: self._show_section_info("share_structure"),
        )
        self._sections.append(card)
        frame = card.frame

        stage = r.profile.stage
        tier = _get_tier(r)
        rel = lambda key: get_relevance(key, tier, "share_structure", stage)

        def _shares_fmt(val):
            if val is None:
                return "N/A"
            try:
                v = float(val)
                if v >= 1e9:
                    return f"{v / 1e9:,.2f}B"
                if v >= 1e6:
                    return f"{v / 1e6:,.2f}M"
                return f"{v:,.0f}"
            except Exception:
                return "N/A"

        def _struct_assessment(val):
            if val is None:
                return ""
            t = str(val).lower()
            if "tight" in t:
                return "Tight structure"
            if "moderate" in t:
                return "Moderate"
            if "bloated" in t:
                return "Bloated"
            return str(val)

        rows = [
            ("Shares Outstanding", _shares_fmt(ss.shares_outstanding), "", "shares_outstanding"),
            ("Fully Diluted", _shares_fmt(ss.fully_diluted_shares), "", "fully_diluted_shares"),
            ("Warrants Outstanding", _shares_fmt(ss.warrants_outstanding), "", "warrants_outstanding"),
            ("Options Outstanding", _shares_fmt(ss.options_outstanding), "", "options_outstanding"),
            ("Insider Ownership", _pct(ss.insider_ownership_pct), _thr(ss.insider_ownership_pct, [(0.05, "Low"), (0.10, "Moderate"), (0.20, "Good")], "Strong insider alignment"), "insider_ownership_pct"),
            ("Institutional Ownership", _pct(ss.institutional_ownership_pct), "", "institutional_ownership_pct"),
            ("Float", _shares_fmt(ss.float_shares), "", "float_shares"),
            ("Warrant Overhang", _s(ss.warrant_overhang_risk) if ss.warrant_overhang_risk else "N/A", "", "warrant_overhang_risk"),
            ("Assessment", _s(ss.share_structure_assessment), _struct_assessment(ss.share_structure_assessment), "share_structure_assessment"),
        ]
        for i, (label, value, assessment, key) in enumerate(rows):
            self._add_metric_row_rel(frame, i, label, value, assessment,
                                     metric_key=key, relevance=rel(key) if key else Relevance.RELEVANT)

    # ---- Real Estate Quality ---------------------------------------------

    def _render_real_estate_quality(self, r: AnalysisReport) -> None:
        m = r.real_estate_quality
        if m is None:
            return
        card = CollapsibleCard(
            self.scroll_frame, "Real Estate Quality Indicators",
            icon=ICON_ENERGY, accent=YELLOW, expanded=False,
            info_command=lambda: self._show_section_info("real_estate_quality"),
        )
        self._sections.append(card)
        frame = card.frame

        stage = r.profile.stage
        tier = _get_tier(r)
        rel = lambda key: get_relevance(key, tier, "real_estate_quality", stage)

        # Quality score bar
        if m.quality_score is not None:
            self._render_score_bar(frame, m.quality_score, label="Quality Score")

        rows: list[tuple[str, str, str]] = [
            ("Competitive Position", _s(m.competitive_position), "competitive_position"),
            ("Insider Alignment", _s(m.insider_alignment), "insider_alignment"),
            ("Financial Position", _s(m.financial_position), "financial_position"),
            ("Dilution Risk", _s(m.dilution_risk), "dilution_risk"),
            ("Asset Backing", _s(m.asset_backing), "asset_backing"),
            ("Revenue Status", _s(m.revenue_predictability), "revenue_predictability"),
            ("Share Structure", _s(m.share_structure_assessment), "share_structure_assessment"),
            ("Management Quality", _s(m.management_quality), "management_quality"),
            ("Management Track Record", _s(m.management_track_record), "management_track_record"),
            ("Jurisdiction", _s(m.jurisdiction_assessment), "jurisdiction_assessment"),
            ("Reserve Quality", _s(m.reserve_quality), "reserve_quality"),
            ("Reserve Life", _s(m.reserve_life_assessment), "reserve_life_assessment"),
            ("Production Scale", _s(m.production_scale_assessment), "production_scale_assessment"),
            ("Catalyst Density", _s(m.catalyst_density), "catalyst_density"),
            ("Strategic Backing", _s(m.strategic_backing), "strategic_backing"),
            ("Niche Position", _s(m.niche_position), "niche_position"),
        ]

        for i, (label, value, key) in enumerate(rows):
            self._add_row_rel(frame, i, label, value, relevance=rel(key))

        # Near-term catalysts
        if m.near_term_catalysts:
            sep = tk.Frame(frame, bg=BORDER, height=1)
            sep.pack(fill=tk.X, padx=12, pady=6)
            tk.Label(
                frame, text="  Near-Term Catalysts:", font=FONT_SMALL_BOLD,
                bg=BG_CARD, fg=ACCENT, anchor=tk.W, padx=16,
            ).pack(fill=tk.X)
            for cat in m.near_term_catalysts:
                tk.Label(
                    frame, text=f"    {BULLET}  {cat}",
                    font=FONT_SMALL, bg=BG_CARD, fg=FG_DIM,
                    anchor=tk.W, padx=16, pady=1,
                ).pack(fill=tk.X)

        # ROIC history trend
        if m.roic_history:
            sep = tk.Frame(frame, bg=BORDER, height=1)
            sep.pack(fill=tk.X, padx=12, pady=6)
            trend = " \u2192 ".join(_pctplain(x) for x in reversed(m.roic_history))
            tk.Label(
                frame, text=f"  ROIC Trend:  {trend}",
                font=FONT_MONO, bg=BG_CARD, fg=FG_DIM,
                anchor=tk.W, padx=16, pady=2,
            ).pack(fill=tk.X)

        # Gross margin history trend
        if m.gross_margin_history:
            trend = " \u2192 ".join(_pctplain(x) for x in reversed(m.gross_margin_history))
            tk.Label(
                frame, text=f"  GM Trend:    {trend}",
                font=FONT_MONO, bg=BG_CARD, fg=FG_DIM,
                anchor=tk.W, padx=16, pady=2,
            ).pack(fill=tk.X)

    def _render_score_bar(self, parent: tk.Frame, score: float,
                          label: str = "Quality Score") -> None:
        """Render a visual score bar."""
        bar_row = tk.Frame(parent, bg=BG_CARD, pady=8, padx=16)
        bar_row.pack(fill=tk.X)

        tk.Label(
            bar_row, text=label, font=FONT_BOLD,
            bg=BG_CARD, fg=ACCENT, anchor=tk.E, width=22,
        ).pack(side=tk.LEFT, padx=(0, 8))

        # Score bar container
        bar_outer = tk.Frame(bar_row, bg=BORDER, height=18, width=200)
        bar_outer.pack(side=tk.LEFT, padx=(0, 8))
        bar_outer.pack_propagate(False)

        # Determine color
        if score >= 70:
            bar_color = GREEN
        elif score >= 45:
            bar_color = YELLOW
        elif score >= 20:
            bar_color = ORANGE
        else:
            bar_color = RED

        fill_width = max(1, int(200 * score / 100))
        bar_fill = tk.Frame(bar_outer, bg=bar_color, height=18)
        bar_fill.place(x=0, y=0, relheight=1, width=fill_width)

        tk.Label(
            bar_row, text=f"{score:.1f}/100", font=FONT_BOLD,
            bg=BG_CARD, fg=bar_color,
        ).pack(side=tk.LEFT)

    # ---- Intrinsic Value -------------------------------------------------

    def _render_intrinsic_value(self, r: AnalysisReport) -> None:
        iv = r.intrinsic_value
        if iv is None:
            return
        card = CollapsibleCard(
            self.scroll_frame, "Intrinsic Value",
            icon=ICON_VALUE, accent=TEAL, expanded=False,
            info_command=lambda: self._show_section_info("intrinsic_value"),
        )
        self._sections.append(card)
        frame = card.frame

        primary = _s(iv.primary_method)
        secondary = _s(iv.secondary_method)

        def tag(n: str) -> str:
            if n in primary:
                return "(primary) "
            if n in secondary:
                return "(secondary) "
            return ""

        rows = [
            ("Current Price", f"${iv.current_price:.2f}" if iv.current_price else "N/A", ""),
            (f"{tag('DCF')}DCF (10Y)", f"${iv.dcf_value:.2f}" if iv.dcf_value else "N/A", _mos(iv.margin_of_safety_dcf)),
            (f"{tag('Graham')}Graham Number", f"${iv.graham_number:.2f}" if iv.graham_number else "N/A", _mos(iv.margin_of_safety_graham)),
            (f"{tag('NCAV')}NCAV (Net-Net)", f"${iv.ncav_value:.4f}" if iv.ncav_value is not None else "N/A", _mos(iv.margin_of_safety_ncav)),
            (f"{tag('Asset')}Tangible Book", f"${iv.asset_based_value:.4f}" if iv.asset_based_value else "N/A", _mos(iv.margin_of_safety_asset)),
        ]
        if iv.nav_per_share is not None:
            rows.append(("NAV/Share", f"${iv.nav_per_share:.4f}", _mos(iv.margin_of_safety_nav)))
        if iv.lynch_fair_value:
            rows.append(("Lynch Fair Value", f"${iv.lynch_fair_value:.2f}", ""))

        for i, (label, value, assessment) in enumerate(rows):
            self._add_metric_row(frame, i, label, value, assessment)

    # ---- Market Intelligence ------------------------------------------------

    def _render_market_intelligence(self, r: AnalysisReport) -> None:
        """Render market intelligence: analysts, short interest, technicals, insiders, risks, disclaimers."""
        mi = r.market_intelligence
        if mi is None:
            return

        card = CollapsibleCard(
            self.scroll_frame, "Market Intelligence",
            icon="\U0001f4ca", accent=SKY, expanded=False,
            info_command=lambda: self._show_section_info("market_intelligence"),
        )
        self._sections.append(card)
        frame = card.frame

        idx = 0

        # Rate Commodity & Sector Context Sector Context
        if mi.benchmark_rate_name or mi.sector_etf_name:
            tk.Label(frame, text="  Rate Commodity & Sector Context Sector Context", font=FONT_SECTION,
                     bg=BG_CARD, fg=ACCENT, anchor=tk.W).pack(fill=tk.X, padx=12, pady=(4, 2))
            if mi.benchmark_rate_name and mi.benchmark_rate_value:
                self._add_row(frame, idx, "Property Type", f"{mi.benchmark_rate_name} — ${mi.benchmark_rate_value:,.2f}"); idx += 1
                if mi.rate_52w_high and mi.rate_52w_low:
                    self._add_row(frame, idx, "52W Range", f"${mi.rate_52w_low:,.2f} — ${mi.rate_52w_high:,.2f}"); idx += 1
            if mi.sector_etf_name and mi.sector_etf_price:
                perf = f"  ({mi.sector_etf_3m_perf*100:+.1f}% 3m)" if mi.sector_etf_3m_perf is not None else ""
                self._add_row(frame, idx, "Sector ETF", f"{mi.sector_etf_name} — ${mi.sector_etf_price:,.2f}{perf}"); idx += 1
            if mi.peer_etf_name and mi.peer_etf_price:
                perf = f"  ({mi.peer_etf_3m_perf*100:+.1f}% 3m)" if mi.peer_etf_3m_perf is not None else ""
                self._add_row(frame, idx, "Peer ETF", f"{mi.peer_etf_name} — ${mi.peer_etf_price:,.2f}{perf}"); idx += 1
            sep = tk.Frame(frame, bg=BORDER, height=1); sep.pack(fill=tk.X, padx=12, pady=4)

        # Analyst consensus
        if mi.analyst_count and mi.analyst_count > 0:
            rec = (mi.recommendation or "N/A").replace("_", " ").title()
            self._add_row(frame, idx, "Recommendation", rec); idx += 1
            self._add_row(frame, idx, "Analyst Count", str(mi.analyst_count)); idx += 1
            if mi.target_mean:
                upside = f"  (upside: {mi.target_upside_pct*100:.0f}%)" if mi.target_upside_pct else ""
                self._add_row(frame, idx, "Target Mean", f"${mi.target_mean:.2f}{upside}"); idx += 1
            if mi.target_high:
                self._add_row(frame, idx, "Target High / Low", f"${mi.target_high:.2f} / ${mi.target_low:.2f}" if mi.target_low else f"${mi.target_high:.2f}"); idx += 1

        # Short interest
        if mi.shares_short:
            sep = tk.Frame(frame, bg=BORDER, height=1); sep.pack(fill=tk.X, padx=12, pady=4)
            self._add_row(frame, idx, "Shares Short", f"{mi.shares_short:,.0f}"); idx += 1
            if mi.short_pct_of_float:
                self._add_row(frame, idx, "Short % of Float", f"{mi.short_pct_of_float:.1f}%"); idx += 1
            if mi.short_ratio_days:
                self._add_row(frame, idx, "Days to Cover", f"{mi.short_ratio_days:.1f}"); idx += 1
            if mi.short_squeeze_risk:
                self._add_row(frame, idx, "Squeeze Risk", mi.short_squeeze_risk); idx += 1

        # Price technicals
        if mi.price_52w_high or mi.sma_50 or mi.beta:
            sep = tk.Frame(frame, bg=BORDER, height=1); sep.pack(fill=tk.X, padx=12, pady=4)
            if mi.price_52w_high and mi.price_52w_low:
                self._add_row(frame, idx, "52-Week Range", f"${mi.price_52w_low:.2f} - ${mi.price_52w_high:.2f}"); idx += 1
            if mi.price_52w_range_position is not None:
                pos = mi.price_52w_range_position * 100
                self._add_row(frame, idx, "52W Range Position", f"{pos:.0f}%"); idx += 1
            if mi.sma_50:
                above = "Above" if mi.above_sma_50 else "Below"
                self._add_row(frame, idx, "50-Day SMA", f"${mi.sma_50:.2f} ({above})"); idx += 1
            if mi.sma_200:
                above = "Above" if mi.above_sma_200 else "Below"
                self._add_row(frame, idx, "200-Day SMA", f"${mi.sma_200:.2f} ({above})"); idx += 1
            if mi.golden_cross is not None:
                signal = "Golden Cross (bullish)" if mi.golden_cross else "Death Cross (bearish)"
                color = GREEN if mi.golden_cross else RED
                bg_row = BG_INPUT if idx % 2 == 0 else BG_CARD
                row = tk.Frame(frame, bg=bg_row); row.pack(fill=tk.X)
                tk.Label(row, text="  MA Cross Signal", font=FONT_BOLD, bg=bg_row, fg=ACCENT, width=26, anchor=tk.E, pady=3).pack(side=tk.LEFT, padx=(12, 6))
                tk.Label(row, text=signal, font=FONT, bg=bg_row, fg=color, anchor=tk.W, pady=3).pack(side=tk.LEFT, padx=(6, 12))
                idx += 1
            if mi.beta:
                self._add_row(frame, idx, "Beta", f"{mi.beta:.2f}"); idx += 1

        # Insider activity
        if mi.insider_transactions:
            sep = tk.Frame(frame, bg=BORDER, height=1); sep.pack(fill=tk.X, padx=12, pady=4)
            tk.Label(frame, text="  Recent Insider Transactions", font=FONT_SECTION, bg=BG_CARD, fg=ACCENT, anchor=tk.W).pack(fill=tk.X, padx=12, pady=(4, 2))
            for tx in mi.insider_transactions[:5]:
                bg_row = BG_INPUT if idx % 2 == 0 else BG_CARD
                row = tk.Frame(frame, bg=bg_row); row.pack(fill=tk.X)
                date_str = tx.date[:10] if tx.date else ""
                shares_str = f"{tx.shares:,.0f}" if tx.shares else "N/A"
                tk.Label(row, text=f"  {date_str}", font=FONT_SMALL, bg=bg_row, fg=FG_DIM, width=12, anchor=tk.W).pack(side=tk.LEFT, padx=(12, 4))
                tk.Label(row, text=tx.insider, font=FONT_SMALL, bg=bg_row, fg=FG, anchor=tk.W).pack(side=tk.LEFT, padx=(4, 4))
                tk.Label(row, text=shares_str, font=FONT_SMALL, bg=bg_row, fg=FG, anchor=tk.E, width=12).pack(side=tk.RIGHT, padx=(4, 12))
                idx += 1
            if mi.insider_buy_signal:
                signal_color = GREEN if "buying" in mi.insider_buy_signal.lower() else RED if "selling" in mi.insider_buy_signal.lower() else YELLOW
                tk.Label(frame, text=f"  Signal: {mi.insider_buy_signal}", font=FONT_SMALL_BOLD, bg=BG_CARD, fg=signal_color, anchor=tk.W).pack(fill=tk.X, padx=16, pady=2)

        # Top holders
        if mi.top_holders:
            sep = tk.Frame(frame, bg=BORDER, height=1); sep.pack(fill=tk.X, padx=12, pady=4)
            count_str = f" ({mi.institutions_count} institutions)" if mi.institutions_count else ""
            tk.Label(frame, text=f"  Top Institutional Holders{count_str}", font=FONT_SMALL_BOLD, bg=BG_CARD, fg=ACCENT, anchor=tk.W).pack(fill=tk.X, padx=12, pady=(4, 2))
            for h in mi.top_holders[:5]:
                tk.Label(frame, text=f"    {h}", font=FONT_SMALL, bg=BG_CARD, fg=FG_DIM, anchor=tk.W).pack(fill=tk.X, padx=12)

        # Risk warnings
        if mi.risk_warnings:
            sep = tk.Frame(frame, bg=BORDER, height=1); sep.pack(fill=tk.X, padx=12, pady=4)
            warn_frame = tk.Frame(frame, bg=BG_CARD, padx=16, pady=6); warn_frame.pack(fill=tk.X)
            tk.Label(warn_frame, text=f"{WARN_ICON}  Risk Warnings", font=FONT_SMALL_BOLD, bg=BG_CARD, fg=RED, anchor=tk.W).pack(fill=tk.X, pady=(0, 4))
            for w in mi.risk_warnings:
                tk.Label(warn_frame, text=f"  {WARN_ICON} {w}", font=FONT_SMALL, bg=BG_CARD, fg=RED, anchor=tk.W, wraplength=800, justify=tk.LEFT).pack(fill=tk.X)

        # Disclaimers
        if mi.disclaimers:
            sep = tk.Frame(frame, bg=BORDER, height=1); sep.pack(fill=tk.X, padx=12, pady=4)
            disc_frame = tk.Frame(frame, bg=BG_CARD, padx=16, pady=6); disc_frame.pack(fill=tk.X)
            for d in mi.disclaimers:
                tk.Label(disc_frame, text=d, font=FONT_SMALL, bg=BG_CARD, fg=FG_SUBTLE, anchor=tk.W, wraplength=800, justify=tk.LEFT).pack(fill=tk.X, pady=1)

    # ---- Financials ------------------------------------------------------

    def _render_financials(self, r: AnalysisReport) -> None:
        if not r.financials:
            return
        card = CollapsibleCard(
            self.scroll_frame, f"Financial Statements ({len(r.financials[:5])}Y)",
            icon=ICON_FINANCE, accent=SKY, expanded=False,
            info_command=lambda: self._show_section_info("financials"),
        )
        self._sections.append(card)
        frame = card.frame

        cols = ["Period", "Revenue", "Gross Profit", "Op Income",
                "Net Income", "FCF", "Equity", "Debt"]
        hdr = tk.Frame(frame, bg=BG_SURFACE)
        hdr.pack(fill=tk.X)
        for col in cols:
            tk.Label(
                hdr, text=col, font=FONT_SMALL_BOLD, bg=BG_SURFACE, fg=ACCENT,
                width=14, anchor=tk.CENTER, pady=4,
            ).pack(side=tk.LEFT, padx=1)

        for i, st in enumerate(r.financials[:5]):
            bg = BG_INPUT if i % 2 == 0 else BG_CARD
            row = tk.Frame(frame, bg=bg)
            row.pack(fill=tk.X)
            # (value_text, raw_number) -- raw used for red/green coloring
            cells = [
                (_s(st.period), None),
                (_money(st.revenue), st.revenue),
                (_money(st.gross_profit), st.gross_profit),
                (_money(st.operating_income), st.operating_income),
                (_money(st.net_income), st.net_income),
                (_money(st.free_cash_flow), st.free_cash_flow),
                (_money(st.total_equity), st.total_equity),
                (_money(st.total_debt), None),  # debt is not P&L
            ]
            for val_text, raw in cells:
                fg_color = FG
                if raw is not None:
                    try:
                        v = float(raw)
                        if v > 0:
                            fg_color = GREEN
                        elif v < 0:
                            fg_color = RED
                    except (TypeError, ValueError):
                        pass
                tk.Label(
                    row, text=val_text, font=FONT_SMALL, bg=bg, fg=fg_color,
                    width=14, anchor=tk.CENTER, pady=3,
                ).pack(side=tk.LEFT, padx=1)

    # ---- Filings ---------------------------------------------------------

    def _render_filings(self, r: AnalysisReport) -> None:
        if not r.filings:
            return
        card = CollapsibleCard(
            self.scroll_frame, f"SEC Filings ({len(r.filings)})",
            icon=ICON_FILING, accent=PEACH, expanded=False,
            info_command=lambda: self._show_section_info("filings"),
        )
        self._sections.append(card)
        frame = card.frame

        cols = ["Type", "Filed", "Period", "Saved", ""]
        hdr = tk.Frame(frame, bg=BG_SURFACE)
        hdr.pack(fill=tk.X)
        widths = [14, 18, 18, 10, 12]
        for col, w in zip(cols, widths):
            tk.Label(
                hdr, text=col, font=FONT_SMALL_BOLD, bg=BG_SURFACE, fg=ACCENT,
                width=w, anchor=tk.CENTER, pady=4,
            ).pack(side=tk.LEFT, padx=1)

        for i, f in enumerate(r.filings[:20]):
            bg = BG_INPUT if i % 2 == 0 else BG_CARD
            row = tk.Frame(frame, bg=bg)
            row.pack(fill=tk.X)
            vals = [
                (_s(f.form_type), 14),
                (_s(f.filing_date), 18),
                (_s(f.period), 18),
                (f"{CHECK} Yes" if f.local_path else "No", 10),
            ]
            for val, w in vals:
                fg_color = GREEN if val.startswith(CHECK) else FG
                tk.Label(
                    row, text=val, font=FONT_SMALL, bg=bg, fg=fg_color,
                    width=w, anchor=tk.CENTER, pady=3,
                ).pack(side=tk.LEFT, padx=1)
            # Download button
            filing = f
            btn = tk.Button(
                row, text="Download", font=FONT_SMALL,
                bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
                activebackground=BG_HOVER, activeforeground=FG,
                relief=tk.FLAT, padx=4, pady=1, cursor="hand2",
                command=lambda fl=filing: self._download_filing_gui(fl),
            )
            btn.pack(side=tk.LEFT, padx=4)

    # ---- News ------------------------------------------------------------

    def _render_news(self, r: AnalysisReport) -> None:
        if not r.news:
            return
        card = CollapsibleCard(
            self.scroll_frame, f"News ({len(r.news)})",
            icon=ICON_NEWS, accent=PINK, expanded=False,
            info_command=lambda: self._show_section_info("news"),
        )
        self._sections.append(card)
        frame = card.frame

        for i, n in enumerate(r.news[:20]):
            bg = BG_INPUT if i % 2 == 0 else BG_CARD
            row = tk.Frame(frame, bg=bg, pady=3)
            row.pack(fill=tk.X)

            title = (n.title or "")[:80] + ("..." if len(n.title or "") > 80 else "")
            meta = f"{_s(n.source)}  {BULLET}  {_s(n.published)}"

            tk.Label(
                row, text=f" {i + 1}.", font=FONT_SMALL_BOLD, bg=bg, fg=FG_DIM,
                anchor=tk.E, width=4,
            ).pack(side=tk.LEFT, padx=(8, 4))
            tk.Label(
                row, text=title, font=FONT, bg=bg, fg=FG,
                anchor=tk.W,
            ).pack(side=tk.LEFT, padx=(0, 8))

            # Open in browser button
            if n.url:
                article = n
                btn = tk.Button(
                    row, text="Open", font=FONT_SMALL,
                    bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
                    activebackground=BG_HOVER, activeforeground=FG,
                    relief=tk.FLAT, padx=4, pady=1, cursor="hand2",
                    command=lambda art=article: self._open_news_gui(art),
                )
                btn.pack(side=tk.RIGHT, padx=(4, 12))

            tk.Label(
                row, text=meta, font=FONT_SMALL, bg=bg, fg=FG_SUBTLE,
                anchor=tk.E,
            ).pack(side=tk.RIGHT, padx=(0, 4))

    # ---- Screening -------------------------------------------------------

    def _render_screening(self, r: AnalysisReport) -> None:
        """Render the real estate screening checklist."""
        from lynx_realestate.core.conclusion import generate_conclusion
        c = generate_conclusion(r)
        checklist = c.screening_checklist
        if not checklist:
            return

        card = CollapsibleCard(
            self.scroll_frame, "Real Estate Screening Checklist",
            icon=ICON_SCREENING, accent=TEAL, expanded=False,
            info_command=lambda: self._show_section_info("screening"),
        )
        self._sections.append(card)
        frame = card.frame

        # Labels for each check
        check_labels = {
            "cash_runway_18m": "Cash runway > 18 months",
            "low_dilution": "Low dilution (< 5% YoY)",
            "insider_ownership": "Insider ownership > 10%",
            "tight_share_structure": "Tight share structure (< 200M FD)",
            "no_excessive_debt": "No excessive debt",
            "positive_working_capital": "Positive working capital",
            "management_track_record": "Management track record",
            "tier_1_2_jurisdiction": "Tier 1/2 jurisdiction",
            "cash_backing": "Cash backing > 30% of market cap",
            "has_revenue": "Generating revenue",
        }

        pass_count = 0
        fail_count = 0
        na_count = 0

        for i, (key, result) in enumerate(checklist.items()):
            bg = BG_INPUT if i % 2 == 0 else BG_CARD
            row = tk.Frame(frame, bg=bg)
            row.pack(fill=tk.X)

            label_text = check_labels.get(key, key.replace("_", " ").title())

            if result is True:
                status_text = f"{CHECK} PASS"
                status_color = GREEN
                pass_count += 1
            elif result is False:
                status_text = f"{CROSS} FAIL"
                status_color = RED
                fail_count += 1
            else:
                status_text = f"{BULLET} N/A"
                status_color = FG_DIM
                na_count += 1

            tk.Label(
                row, text=label_text, font=FONT_BOLD, bg=bg, fg=ACCENT,
                width=36, anchor=tk.E, pady=3,
            ).pack(side=tk.LEFT, padx=(12, 6))
            tk.Label(
                row, text=status_text, font=FONT_BOLD, bg=bg, fg=status_color,
                width=10, anchor=tk.W, pady=3,
            ).pack(side=tk.LEFT, padx=(6, 12))

        # Summary row
        sep = tk.Frame(frame, bg=BORDER, height=1)
        sep.pack(fill=tk.X, padx=12, pady=6)
        summary_row = tk.Frame(frame, bg=BG_CARD, pady=4)
        summary_row.pack(fill=tk.X)
        summary_text = (
            f"  Screening: {pass_count} passed, {fail_count} failed, {na_count} N/A  "
            f"({pass_count}/{pass_count + fail_count} applicable checks passed)"
        )
        overall_color = GREEN if fail_count == 0 else (YELLOW if fail_count <= 2 else RED)
        tk.Label(
            summary_row, text=summary_text, font=FONT_BOLD,
            bg=BG_CARD, fg=overall_color, anchor=tk.W, padx=16,
        ).pack(fill=tk.X)

    # ---- Conclusion -----------------------------------------------------

    def _render_conclusion(self, r: AnalysisReport) -> None:
        from lynx_realestate.core.conclusion import generate_conclusion
        c = generate_conclusion(r)

        # Verdict colour
        verdict_colors = {
            "Strong Buy": GREEN, "Buy": GREEN_DIM,
            "Hold": YELLOW, "Caution": ORANGE, "Avoid": RED,
        }
        vc = verdict_colors.get(c.verdict, FG)

        card = CollapsibleCard(
            self.scroll_frame, "Assessment Conclusion",
            icon="\U0001f4dd", accent=vc, expanded=False,
            info_command=lambda: self._show_conclusion_info("overall"),
        )
        self._sections.append(card)
        frame = card.frame

        # Verdict + score bar
        verdict_frame = tk.Frame(frame, bg=BG_CARD, pady=8, padx=16)
        verdict_frame.pack(fill=tk.X)
        tk.Label(
            verdict_frame, text=f"{c.verdict}  ({c.overall_score:.0f}/100)",
            font=(_FAMILY, 14, "bold"), bg=BG_CARD, fg=vc,
        ).pack(anchor=tk.W)
        tk.Label(
            verdict_frame, text=c.summary, font=FONT_SMALL,
            bg=BG_CARD, fg=FG_DIM, wraplength=900, justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(4, 0))

        # Category scores (using real_estate_quality instead of moat)
        sep = tk.Frame(frame, bg=BORDER, height=1)
        sep.pack(fill=tk.X, padx=12, pady=6)
        for i, cat in enumerate(("valuation", "profitability", "solvency", "growth", "real_estate_quality")):
            score = c.category_scores.get(cat, 0)
            summary = c.category_summaries.get(cat, "")
            display_name = cat.replace("_", " ").title()
            self._add_metric_row(frame, i, display_name, f"{score:.0f}/100", summary)

        # Screening checklist summary in conclusion
        if c.screening_checklist:
            sep_screen = tk.Frame(frame, bg=BORDER, height=1)
            sep_screen.pack(fill=tk.X, padx=12, pady=6)

            check_labels = {
                "cash_runway_18m": "Cash runway > 18m",
                "low_dilution": "Low dilution",
                "insider_ownership": "Insider > 10%",
                "tight_share_structure": "Tight shares",
                "no_excessive_debt": "Low debt",
                "positive_working_capital": "+Working capital",
                "management_track_record": "Mgmt track record",
                "tier_1_2_jurisdiction": "Tier 1/2 jurisdiction",
                "cash_backing": "Cash backing > 30%",
                "has_revenue": "Has revenue",
            }

            screening_frame = tk.Frame(frame, bg=BG_CARD, padx=16, pady=4)
            screening_frame.pack(fill=tk.X)
            tk.Label(
                screening_frame, text="Screening Checklist:", font=FONT_SMALL_BOLD,
                bg=BG_CARD, fg=ACCENT, anchor=tk.W,
            ).pack(fill=tk.X, pady=(0, 4))

            checklist_text_parts = []
            for key, result in c.screening_checklist.items():
                label = check_labels.get(key, key)
                if result is True:
                    checklist_text_parts.append(f"{CHECK} {label}")
                elif result is False:
                    checklist_text_parts.append(f"{CROSS} {label}")
                else:
                    checklist_text_parts.append(f"{BULLET} {label}")

            checklist_display = "    ".join(checklist_text_parts)
            tk.Label(
                screening_frame, text=checklist_display, font=FONT_SMALL,
                bg=BG_CARD, fg=FG_DIM, anchor=tk.W, wraplength=900,
                justify=tk.LEFT,
            ).pack(fill=tk.X)

        # Strengths & risks
        if c.strengths or c.risks:
            sep2 = tk.Frame(frame, bg=BORDER, height=1)
            sep2.pack(fill=tk.X, padx=12, pady=6)
            idx = 0
            for s in c.strengths:
                bg = BG_INPUT if idx % 2 == 0 else BG_CARD
                row = tk.Frame(frame, bg=bg)
                row.pack(fill=tk.X)
                tk.Label(
                    row, text=f"{CHECK} Strength", font=FONT_BOLD, bg=bg, fg=GREEN,
                    width=22, anchor=tk.E, pady=3,
                ).pack(side=tk.LEFT, padx=(12, 6))
                tk.Label(
                    row, text=s, font=FONT, bg=bg, fg=FG,
                    anchor=tk.W, pady=3,
                ).pack(side=tk.LEFT, padx=(6, 12))
                idx += 1
            for risk in c.risks:
                bg = BG_INPUT if idx % 2 == 0 else BG_CARD
                row = tk.Frame(frame, bg=bg)
                row.pack(fill=tk.X)
                tk.Label(
                    row, text=f"{WARN_ICON} Risk", font=FONT_BOLD, bg=bg, fg=RED,
                    width=22, anchor=tk.E, pady=3,
                ).pack(side=tk.LEFT, padx=(12, 6))
                tk.Label(
                    row, text=risk, font=FONT, bg=bg, fg=FG,
                    anchor=tk.W, pady=3,
                ).pack(side=tk.LEFT, padx=(6, 12))
                idx += 1

        # Tier note
        if c.tier_note:
            tk.Label(
                frame, text=c.tier_note, font=FONT_SMALL,
                bg=BG_CARD, fg=FG_SUBTLE, wraplength=900,
                justify=tk.LEFT, anchor=tk.NW, padx=16, pady=6,
            ).pack(fill=tk.X)

        # Stage note
        if c.stage_note:
            tk.Label(
                frame, text=c.stage_note, font=FONT_SMALL,
                bg=BG_CARD, fg=FG_SUBTLE, wraplength=900,
                justify=tk.LEFT, anchor=tk.NW, padx=16, pady=(0, 6),
            ).pack(fill=tk.X)

    # ---- Filing download / News open --------------------------------------

    def _download_filing_gui(self, filing) -> None:
        report = self._current_report
        if not report:
            return

        def _do():
            from lynx_realestate.core.reports import download_filing
            try:
                path = download_filing(report.profile.ticker, filing)
                if path:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Download Complete",
                        f"Filing {filing.form_type} ({filing.filing_date}) downloaded.\n\n"
                        f"Saved to:\n{path}",
                    ))
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Download Failed",
                        f"Could not download {filing.form_type} ({filing.filing_date}).",
                    ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Download Error", str(e),
                ))

        thread = threading.Thread(target=_do, daemon=True)
        thread.start()

    def _open_news_gui(self, article) -> None:
        if not article.url:
            return
        if not safe_webbrowser_open(article.url):
            messagebox.showerror("Unsafe URL", "Refused: unsafe URL")
            return

        if not self._suppress_news_dialog:
            result = messagebox.askyesno(
                "News Opened",
                "News article has been opened in your default browser.\n\n"
                "Click 'Yes' to continue showing this message,\n"
                "or 'No' to suppress it for the rest of this session.",
            )
            if not result:
                self._suppress_news_dialog = True

    # ---- Row helpers -----------------------------------------------------

    def _add_row(self, frame: tk.Frame, idx: int, label: str, value: str) -> None:
        """Add a simple label-value row."""
        bg = BG_INPUT if idx % 2 == 0 else BG_CARD
        r = tk.Frame(frame, bg=bg)
        r.pack(fill=tk.X)
        tk.Label(
            r, text=label, font=FONT_BOLD, bg=bg, fg=ACCENT,
            width=26, anchor=tk.E, pady=3,
        ).pack(side=tk.LEFT, padx=(12, 6))
        tk.Label(
            r, text=value, font=FONT, bg=bg, fg=FG,
            anchor=tk.W, pady=3, wraplength=700, justify=tk.LEFT,
        ).pack(side=tk.LEFT, padx=(6, 12), fill=tk.X, expand=True)

    def _add_metric_row(self, frame: tk.Frame, idx: int,
                        label: str, value: str, assessment: str,
                        metric_key: str = "") -> None:
        """Add a metric row with label, value, assessment badge, and info button."""
        bg = BG_INPUT if idx % 2 == 0 else BG_CARD
        r = tk.Frame(frame, bg=bg)
        r.pack(fill=tk.X)
        tk.Label(
            r, text=label, font=FONT_BOLD, bg=bg, fg=ACCENT,
            width=22, anchor=tk.E, pady=3,
        ).pack(side=tk.LEFT, padx=(12, 6))
        tk.Label(
            r, text=value, font=FONT, bg=bg, fg=FG,
            width=16, anchor=tk.E, pady=3,
        ).pack(side=tk.LEFT, padx=(6, 8))
        if assessment:
            fg_color = _assessment_color(assessment)
            tk.Label(
                r, text=f" {assessment} ", font=FONT_SMALL,
                bg=bg, fg=fg_color, anchor=tk.W, pady=3,
                wraplength=400, justify=tk.LEFT,
            ).pack(side=tk.LEFT, padx=(4, 8), fill=tk.X, expand=True)
        # Metric explanation button (smaller "?" for individual metrics)
        if metric_key:
            btn = tk.Button(
                r, text=" ? ", font=(_FAMILY, 9, "bold"),
                bg=BORDER, fg=ACCENT, activebackground=BG_HOVER,
                activeforeground=FG, relief=tk.FLAT, padx=2, pady=0,
                cursor="hand2",
                command=lambda k=metric_key: self._show_metric_info(k),
            )
            btn.pack(side=tk.RIGHT, padx=(0, 8))

    def _add_metric_row_rel(self, frame, idx, label, value, assessment, metric_key="", relevance=Relevance.RELEVANT):
        """Add a metric row with relevance-based styling."""
        if relevance == Relevance.IRRELEVANT:
            return  # Skip entirely
        bg = BG_INPUT if idx % 2 == 0 else BG_CARD
        row = tk.Frame(frame, bg=bg)
        row.pack(fill=tk.X)

        # Label with relevance prefix
        if relevance == Relevance.CRITICAL:
            prefix = f"{STAR} "
            label_fg = ACCENT
            label_font = FONT_BOLD
        elif relevance == Relevance.IMPORTANT:
            prefix = "> "
            label_fg = "#ff8800"
            label_font = FONT_BOLD
        elif relevance == Relevance.CONTEXTUAL:
            prefix = "  "
            label_fg = FG_SUBTLE
            label_font = FONT_SMALL
        else:
            prefix = "  "
            label_fg = ACCENT
            label_font = FONT_BOLD

        tk.Label(row, text=f"{prefix}{label}", font=label_font, bg=bg, fg=label_fg,
                 width=24, anchor=tk.E, pady=3).pack(side=tk.LEFT, padx=(12, 6))

        val_fg = FG_DIM if relevance == Relevance.CONTEXTUAL else FG
        tk.Label(row, text=value, font=FONT if relevance != Relevance.CONTEXTUAL else FONT_SMALL,
                 bg=bg, fg=val_fg, width=18, anchor=tk.W, pady=3).pack(side=tk.LEFT, padx=(6, 4))

        if assessment:
            assess_fg = _assessment_color(assessment) if relevance != Relevance.CONTEXTUAL else FG_SUBTLE
            tk.Label(row, text=assessment, font=FONT_SMALL, bg=bg, fg=assess_fg,
                     anchor=tk.W, pady=3, wraplength=400, justify=tk.LEFT,
                     ).pack(side=tk.LEFT, padx=(4, 4), fill=tk.X, expand=True)

        if metric_key:
            btn = tk.Button(row, text=" ? ", font=(_FAMILY, 9, "bold"),
                           bg=BORDER, fg=ACCENT, activebackground=BG_HOVER,
                           activeforeground=FG, relief=tk.FLAT,
                           padx=2, pady=0, cursor="hand2",
                           command=lambda k=metric_key: self._show_metric_info(k))
            btn.pack(side=tk.RIGHT, padx=(0, 8))

    def _add_row_rel(self, frame, idx, label, value, relevance=Relevance.RELEVANT):
        """Add a simple label-value row with relevance-based styling."""
        if relevance == Relevance.IRRELEVANT:
            return
        bg = BG_INPUT if idx % 2 == 0 else BG_CARD
        row = tk.Frame(frame, bg=bg)
        row.pack(fill=tk.X)
        if relevance == Relevance.CRITICAL:
            prefix = f"{STAR} "
            fg = ACCENT
            label_font = FONT_BOLD
        elif relevance == Relevance.IMPORTANT:
            prefix = "> "
            fg = "#ff8800"
            label_font = FONT_BOLD
        elif relevance == Relevance.CONTEXTUAL:
            prefix = "  "
            fg = FG_SUBTLE
            label_font = FONT_SMALL
        else:
            prefix = "  "
            fg = ACCENT
            label_font = FONT_BOLD
        tk.Label(row, text=f"{prefix}{label}", font=label_font,
                 bg=bg, fg=fg, width=24, anchor=tk.E, pady=3).pack(side=tk.LEFT, padx=(12, 6))
        val_fg = FG_DIM if relevance == Relevance.CONTEXTUAL else FG
        tk.Label(row, text=value, font=FONT if relevance != Relevance.CONTEXTUAL else FONT_SMALL,
                 bg=bg, fg=val_fg, anchor=tk.W, pady=3,
                 wraplength=600, justify=tk.LEFT,
                 ).pack(side=tk.LEFT, padx=(6, 12), fill=tk.X, expand=True)

    # ---- Explanation popups ------------------------------------------------

    def _show_info_popup(self, title: str, subtitle: str, sections: list) -> None:
        """Generic info popup with title, subtitle, and content sections."""
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        tk.Label(
            win, text=title, font=(_FAMILY, 14, "bold"),
            bg=BG, fg=ACCENT, wraplength=560,
        ).pack(padx=24, pady=(16, 4))

        if subtitle:
            tk.Label(
                win, text=subtitle, font=FONT_SMALL,
                bg=BG, fg=FG_SUBTLE,
            ).pack(padx=24, pady=(0, 12))

        card = tk.Frame(win, bg=BG_CARD, padx=16, pady=12)
        card.pack(fill=tk.X, padx=20, pady=(0, 8))

        for i, (heading, text) in enumerate(sections):
            if i > 0:
                tk.Frame(card, bg=BORDER, height=1).pack(fill=tk.X, pady=8)
            tk.Label(
                card, text=heading, font=FONT_SMALL_BOLD,
                bg=BG_CARD, fg=ACCENT, anchor=tk.W,
            ).pack(fill=tk.X)
            tk.Label(
                card, text=text, font=FONT, bg=BG_CARD, fg=FG,
                wraplength=520, justify=tk.LEFT, anchor=tk.NW,
            ).pack(fill=tk.X, pady=(2, 0))

        btn_frame = tk.Frame(win, bg=BG)
        btn_frame.pack(fill=tk.X, pady=(8, 16))
        tk.Button(
            btn_frame, text="  Close  ", font=FONT_BTN,
            bg=BTN_BG, fg=BTN_FG, activebackground=BTN_ACTIVE,
            relief=tk.FLAT, padx=14, pady=4, cursor="hand2",
            command=win.destroy,
        ).pack(anchor=tk.CENTER)

        win.bind("<Escape>", lambda _: win.destroy())
        win.update_idletasks()
        w, h = win.winfo_reqwidth(), win.winfo_reqheight()
        sx = (win.winfo_screenwidth() - w) // 2
        sy = (win.winfo_screenheight() - h) // 2
        win.geometry(f"{w}x{h}+{sx}+{sy}")

    def _show_metric_info(self, key: str) -> None:
        from lynx_realestate.metrics.explanations import get_explanation
        exp = get_explanation(key)
        if not exp:
            return
        self._show_info_popup(
            exp.full_name,
            f"Category: {exp.category.title()}",
            [
                ("What it measures", exp.description),
                ("Formula", exp.formula),
                ("Why it matters", exp.why_used),
            ],
        )

    def _show_section_info(self, section_key: str) -> None:
        from lynx_realestate.metrics.explanations import get_section_explanation
        sec = get_section_explanation(section_key)
        if not sec:
            return
        self._show_info_popup(
            sec["title"],
            "",
            [("Description", sec["description"])],
        )

    def _show_conclusion_info(self, category: str = "overall") -> None:
        from lynx_realestate.metrics.explanations import get_conclusion_explanation
        ce = get_conclusion_explanation(category)
        if not ce:
            return
        self._show_info_popup(
            ce["title"],
            "Conclusion Methodology",
            [("How it works", ce["description"])],
        )

    # ---- Run -------------------------------------------------------------

    def run(self) -> None:
        if hasattr(self, "entry_ticker"):
            self.entry_ticker.focus_set()
        # Bottom-right language toggle (US/ES/IT/DE/FR/FA).
        try:
            from lynx_investor_core.lang_widget import mount_tk_language_button
            mount_tk_language_button(self.root)
        except Exception:
            pass
        self.root.mainloop()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _s(val) -> str:
    return str(val) if val is not None else "N/A"


def _num(val, digits: int = 2) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
        if v != v: return "N/A"  # NaN check
        return f"{v:,.{digits}f}"
    except Exception:
        return "N/A"


def _pct(val) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
        if v != v: return "N/A"  # NaN check
        return f"{v * 100:.2f}%"
    except Exception:
        return "N/A"


def _pctplain(val) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
        if v != v: return "N/A"  # NaN check
        return f"{v * 100:.1f}%"
    except Exception:
        return "N/A"


def _money(val) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
        if v != v: return "N/A"  # NaN check
        if abs(v) >= 1e12:
            return f"${v / 1e12:,.2f}T"
        if abs(v) >= 1e9:
            return f"${v / 1e9:,.2f}B"
        if abs(v) >= 1e6:
            return f"${v / 1e6:,.2f}M"
        return f"${v:,.0f}"
    except Exception:
        return "N/A"


def _mos(val) -> str:
    if val is None:
        return "N/A"
    try:
        p = float(val) * 100
        if p > 25:
            return f"{p:.1f}% (Undervalued)"
        if p > 0:
            return f"{p:.1f}% (Slight Undervalue)"
        return f"{p:.1f}% (Overvalued)"
    except Exception:
        return "N/A"


def _burn(val) -> str:
    if val is None:
        return ""
    try:
        v = float(val)
        if v == 0:
            return "Not burning cash"
        if v < 0:
            return "Burning cash"
        return "Cash flow positive"
    except Exception:
        return ""


def _ape(val) -> str:
    if val is None:
        return ""
    try:
        v = float(val)
        if v < 0:
            return "Negative earnings"
        if v < 10:
            return "Very cheap"
        if v < 15:
            return "Value range"
        if v < 20:
            return "Fair"
        if v < 30:
            return "Expensive"
        return "Very expensive"
    except Exception:
        return ""


def _thr(val, thresholds, over_label) -> str:
    if val is None:
        return ""
    try:
        v = float(val)
        for threshold, label in thresholds:
            if v < threshold:
                return label
        return over_label
    except Exception:
        return ""


def _safe_tier(tier) -> str:
    if isinstance(tier, CompanyTier):
        return tier.value
    return str(tier) if tier else "N/A"


def _get_tier(r: AnalysisReport) -> CompanyTier:
    try:
        tier = r.profile.tier
        if isinstance(tier, CompanyTier):
            return tier
    except Exception:
        pass
    return CompanyTier.NANO


def _assessment_color(text: str) -> str:
    """Pick a colour for assessment text based on sentiment."""
    t = text.lower()

    # Check neutral first -- these override broader substring matches.
    neutral = ("slight undervalue", "below avg", "below wacc",
               "near book", "near ncav", "grey zone",
               "fair", "moderate", "manageable", "adequate",
               "modest", "moderate overhang", "moderate burn")
    for word in neutral:
        if word in t:
            return YELLOW

    # Positive -- ordered longest-first to avoid substring collisions.
    positive = ("not burning cash", "cash flow positive",
                "very conservative", "classic net-net",
                "below book", "below ncav", "deep value",
                "wide moat", "value range", "very low", "very cheap",
                "undervalue", "cheap", "good", "excellent", "outstanding",
                "exceptional", "strong", "safe", "conservative", "low",
                "tight", "minimal", "buybacks", "minimal overhang",
                "pass", "low burn")
    for word in positive:
        if word in t:
            return GREEN

    # Negative -- checked last.
    negative = ("very expensive", "very high", "burning cash",
                "liquidity risk", "above ncav", "negative",
                "expensive", "overvalued", "distress",
                "heavy", "high", "premium", "bloated",
                "significant", "heavy dilution", "fail",
                "heavy warrant", "significant overhang", "high burn")
    for word in negative:
        if word in t:
            return RED

    return FG_DIM


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_gui(args) -> None:
    """Launch the tkinter GUI."""
    app = LynxRealEstateGUI(cli_args=args)
    app.run()
