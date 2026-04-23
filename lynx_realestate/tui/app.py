"""Textual UI for Lynx Real Estate Analysis."""

from __future__ import annotations

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll

from lynx_investor_core.pager import PagingAppMixin, tui_paging_bindings
from lynx_investor_core.urlsafe import safe_webbrowser_open
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Collapsible,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
    TabbedContent,
    TabPane,
)

from rich.console import Group
from rich.table import Table as RichTable

from lynx_realestate.models import (
    AnalysisReport,
    CompanyStage,
    CompanyTier,
    Relevance,
)


# ======================================================================
# About modal
# ======================================================================

class AboutModal(ModalScreen):
    BINDINGS = [Binding("escape", "dismiss_modal", "Close")]

    def compose(self) -> ComposeResult:
        from lynx_realestate import get_about_text
        about = get_about_text()
        with Vertical(id="about-dialog"):
            yield Label(
                f"[bold blue]{about['name']}[/]",
                id="about-title",
            )
            yield VerticalScroll(
                Static(
                    f"[bold green]{about['logo']}[/]\n"
                    f"[bold blue]{about['name']} v{about['version']}[/]\n"
                    f"[dim]Part of {about['suite']} v{about['suite_version']}[/]\n"
                    f"[dim]Released {about['year']}[/]\n\n"
                    f"[bold]Developed by:[/] {about['author']}\n"
                    f"[bold]Contact:[/]      {about['email']}\n"
                    f"[bold]License:[/]      {about['license']}\n\n"
                    f"{about['description']}\n\n"
                    f"[bold cyan]BSD 3-Clause License[/]\n"
                    f"[dim]{about['license_text']}[/]",
                    id="about-content",
                ),
                id="about-scroll",
            )
            yield Label(
                "[dim]Press Escape to close[/]",
                id="about-hint",
            )

    def action_dismiss_modal(self) -> None:
        self.dismiss()


# ======================================================================
# Explain modal
# ======================================================================

class ExplainModal(ModalScreen):
    """Versatile explain dialog for metrics, sections, and conclusion items."""
    BINDINGS = [Binding("escape", "dismiss_modal", "Close")]

    def __init__(self, key: str, kind: str = "metric", **kwargs) -> None:
        """*kind* can be ``metric``, ``section``, or ``conclusion``."""
        super().__init__(**kwargs)
        self._key = key
        self._kind = kind

    def compose(self) -> ComposeResult:
        from lynx_realestate.metrics.explanations import (
            get_conclusion_explanation,
            get_explanation,
            get_section_explanation,
        )

        title = ""
        content = ""

        if self._kind == "metric":
            exp = get_explanation(self._key)
            if exp:
                title = exp.full_name
                content = (
                    f"[bold]{exp.full_name}[/]\n\n"
                    f"{exp.description}\n\n"
                    f"[bold cyan]Why it matters:[/]\n{exp.why_used}\n\n"
                    f"[bold cyan]Formula:[/]\n[bold]{exp.formula}[/]\n\n"
                    f"[dim]Category: {exp.category}[/]"
                )
            else:
                title = self._key
                content = f"No explanation available for '{self._key}'."

        elif self._kind == "section":
            sec = get_section_explanation(self._key)
            if sec:
                title = sec["title"]
                content = f"[bold]{sec['title']}[/]\n\n{sec['description']}"
            else:
                title = self._key.title()
                content = f"No section explanation available for '{self._key}'."

        elif self._kind == "conclusion":
            ce = get_conclusion_explanation(self._key)
            if ce:
                title = ce["title"]
                content = f"[bold]{ce['title']}[/]\n\n{ce['description']}"
            else:
                title = "Conclusion"
                content = "No conclusion explanation available."

        with Vertical(id="explain-dialog"):
            yield Label(f"[bold]{title}[/]", id="explain-title")
            yield VerticalScroll(Static(content, id="explain-content"), id="explain-scroll")
            yield Label("[dim]Press Escape to close[/]", id="explain-hint")

    def action_dismiss_modal(self) -> None:
        self.dismiss()


# ======================================================================
# Metric list modal (for browsing explanations)
# ======================================================================

class MetricListModal(ModalScreen[str]):
    """Modal for browsing all metric explanations.

    If *focus_key* is provided, the cursor starts on that metric row.
    """
    BINDINGS = [Binding("escape", "dismiss_modal", "Close")]

    def __init__(self, focus_key: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self._focus_key = focus_key

    def compose(self) -> ComposeResult:
        from lynx_realestate.metrics.explanations import list_metrics
        with Vertical(id="metric-list-dialog"):
            yield Label("[bold]Select a metric to explain[/]", id="metric-list-title")
            t = DataTable(zebra_stripes=True, cursor_type="row", id="metric-list-table")
            t.add_column("Key", width=24)
            t.add_column("Name", width=None)
            t.add_column("Category", width=16)
            for m in list_metrics():
                t.add_row(m.key, m.full_name, m.category, key=m.key)
            yield t
            yield Label("[dim]Press Enter to explain, Escape to close[/]", id="metric-list-hint")

    def on_mount(self) -> None:
        """Move cursor to the focused metric if one was specified."""
        if not self._focus_key:
            return
        try:
            t = self.query_one("#metric-list-table", DataTable)
            from lynx_realestate.metrics.explanations import list_metrics
            metrics = list_metrics()
            for idx, m in enumerate(metrics):
                if m.key == self._focus_key:
                    t.move_cursor(row=idx)
                    return
        except Exception:
            pass

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        from lynx_realestate.metrics.explanations import list_metrics
        metrics = list_metrics()
        idx = event.cursor_row
        if 0 <= idx < len(metrics):
            self.dismiss(metrics[idx].key)

    def action_dismiss_modal(self) -> None:
        self.dismiss("")


# ======================================================================
# Export format modal
# ======================================================================

class ExportModal(ModalScreen[str]):
    BINDINGS = [Binding("escape", "dismiss_modal", "Cancel")]

    def compose(self) -> ComposeResult:
        with Vertical(id="export-dialog"):
            yield Label("[bold]Export Report[/]", id="export-title")
            with Horizontal(id="export-buttons"):
                yield Button("TXT", id="export-txt", variant="primary")
                yield Button("HTML", id="export-html", variant="primary")
                yield Button("PDF", id="export-pdf", variant="primary")
            yield Label("[dim]Select format, or Escape to cancel[/]", id="export-hint")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        fmt = event.button.id.replace("export-", "")
        self.dismiss(fmt)

    def action_dismiss_modal(self) -> None:
        self.dismiss("")


# ======================================================================
# Search modal
# ======================================================================

class SearchModal(ModalScreen[str]):
    BINDINGS = [Binding("escape", "dismiss_modal", "Cancel")]

    def compose(self) -> ComposeResult:
        with Vertical(id="search-dialog"):
            yield Label("Enter Ticker or ISIN", id="search-label")
            yield Input(
                placeholder="e.g. SPG, O, PLD, EQIX, WELL",
                id="search-input",
            )
            yield Label(
                "[dim]Press Enter to analyze, Escape to cancel[/]",
                id="search-hint",
            )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = (event.value or "").strip()
        if len(value) > 100:
            value = value[:100]
        self.dismiss(value)

    def action_dismiss_modal(self) -> None:
        self.dismiss("")


# ======================================================================
# News browser dialog
# ======================================================================

class NewsBrowserDialog(ModalScreen):
    """Dialog shown after opening a news article in the browser."""
    BINDINGS = [Binding("escape", "dismiss_modal", "Close")]

    def compose(self) -> ComposeResult:
        with Vertical(id="news-dialog"):
            yield Label(
                "[bold]News article opened in your default browser.[/]",
                id="news-dialog-label",
            )
            with Horizontal(id="news-dialog-buttons"):
                yield Button("OK", id="news-ok-btn", variant="primary")
                yield Button("Do not show again", id="news-suppress-btn", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "news-suppress-btn":
            self.dismiss("suppress")
        else:
            self.dismiss("ok")

    def action_dismiss_modal(self) -> None:
        self.dismiss("ok")


# ======================================================================
# Download result dialog
# ======================================================================

class DownloadResultDialog(ModalScreen):
    """Dialog showing filing download result."""
    BINDINGS = [Binding("escape", "dismiss_modal", "Close")]

    def __init__(self, message: str, success: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        self._message = message
        self._success = success

    def compose(self) -> ComposeResult:
        style = "bold green" if self._success else "bold red"
        with Vertical(id="download-dialog"):
            yield Label(
                f"[{style}]{self._message}[/]",
                id="download-dialog-label",
            )
            yield Button("OK", id="download-ok-btn", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

    def action_dismiss_modal(self) -> None:
        self.dismiss()


# ======================================================================
# Report view -- uses compose() so Textual properly initialises widgets
# ======================================================================

class ReportView(VerticalScroll):
    """Widget that renders analysis report sections progressively.

    Sections are mounted one-by-one via ``add_stage()`` so the user sees
    data as soon as it arrives, rather than waiting for the full pipeline.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._report: AnalysisReport | None = None
        self._hint_removed: bool = False

    def compose(self) -> ComposeResult:
        # Starts empty -- sections are mounted dynamically.
        yield Static(
            "[dim]Fetching data...[/]",
            id="loading-hint",
        )

    def add_stage(self, stage: str, report: AnalysisReport) -> None:
        """Mount the widgets for a given analysis stage."""
        self._report = report

        # Remove the loading hint once (first real content).
        if not self._hint_removed:
            self._hint_removed = True
            try:
                self.query_one("#loading-hint", Static).remove()
            except Exception:
                pass

        if stage == "profile":
            self._mount_profile(report)
        elif stage == "financials":
            self._mount_section(
                "Financials", _build_financials(report),
            )
        elif stage == "valuation":
            self._mount_section("Valuation", _build_valuation(report))
        elif stage == "profitability":
            self._mount_section("Profitability", _build_profitability(report))
        elif stage == "solvency":
            self._mount_section(
                "Solvency & Financial Health", _build_solvency(report),
            )
        elif stage == "growth":
            self._mount_section("Growth", _build_growth(report))
        elif stage == "share_structure":
            self._mount_section("Share Structure", _build_share_structure(report))
        elif stage == "real_estate_quality":
            self._mount_section("Real Estate Quality", _build_real_estate_quality(report))
        elif stage == "intrinsic_value":
            self._mount_section("Intrinsic Value", _build_iv(report))
        elif stage == "market_intelligence":
            self._mount_section("Market Intelligence", _build_market_intelligence(report))
        elif stage == "filings":
            self._mount_filings(report)
        elif stage == "news":
            self._mount_news(report)
        elif stage == "conclusion":
            self._mount_section("Conclusion", _build_conclusion(report))
        elif stage == "complete":
            # If no sections were mounted yet (cached report), render all.
            if not list(self.query(Collapsible)):
                self.render_full(report)

    # -- Internal mount helpers --

    def _mount_profile(self, r: AnalysisReport) -> None:
        p = r.profile
        desc = _s(p.description) if p.description else "[dim]No description available.[/]"
        if len(desc) > 800:
            desc = desc[:800] + "..."

        profile_section = Collapsible(
            title="Company Profile", collapsed=False, id="sec-profile",
        )
        self.mount(profile_section)

        split = Horizontal(id="profile-split")
        profile_section.mount(split)
        split.mount(_build_profile_table(r))
        split.mount(Static(desc, id="profile-desc"))

        # Sector and industry insights (after profile)
        self._mount_sector_industry(r)

    def _mount_sector_industry(self, r: AnalysisReport) -> None:
        """Mount sector and industry insight collapsibles."""
        from lynx_realestate.metrics.sector_insights import get_sector_insight, get_industry_insight

        p = r.profile
        sector_info = get_sector_insight(p.sector)
        industry_info = get_industry_insight(p.industry)

        if sector_info:
            t = _build_insight_table(sector_info)
            c = Collapsible(title=f"Sector: {sector_info.sector}", collapsed=True)
            self.mount(c)
            c.mount(t)

        if industry_info:
            t = _build_insight_table(industry_info)
            c = Collapsible(title=f"Industry: {industry_info.industry}", collapsed=True)
            self.mount(c)
            c.mount(t)

    def _mount_section(self, title: str, widget, section_id: str = "") -> None:
        kwargs = {"title": title, "collapsed": True}
        if section_id:
            kwargs["id"] = section_id
        c = Collapsible(**kwargs)
        self.mount(c)
        c.mount(widget)

    def _mount_filings(self, r: AnalysisReport) -> None:
        c = Collapsible(title="Filings", collapsed=True, id="sec-filings")
        self.mount(c)
        c.mount(_build_filings(r))
        c.mount(Static(
            "[dim]Select a row and press [bold]Enter[/bold] to download filing[/]",
        ))

    def _mount_news(self, r: AnalysisReport) -> None:
        c = Collapsible(title="News", collapsed=True, id="sec-news")
        self.mount(c)
        c.mount(_build_news(r))
        c.mount(Static(
            "[dim]Select a row and press [bold]Enter[/bold] to open in browser[/]",
        ))

    def render_full(self, report: AnalysisReport) -> None:
        """Convenience: mount all sections at once (for cached reports)."""
        stages = [
            "profile", "financials", "valuation", "profitability",
            "solvency", "growth", "share_structure", "real_estate_quality",
            "intrinsic_value", "market_intelligence", "filings", "news", "conclusion",
        ]
        for stage in stages:
            self.add_stage(stage, report)


# ======================================================================
# Main application
# ======================================================================

class LynxRealEstateApp(PagingAppMixin, App):
    TITLE = "Lynx Real Estate Analysis"
    SUB_TITLE = "Real Estate Sector Analysis"
    CSS = """
    #search-dialog {
        width: 60;
        height: auto;
        max-height: 12;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        margin: 4 8;
    }
    #search-label {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    #search-hint {
        text-align: center;
        margin-top: 1;
    }
    #search-input {
        margin: 0 2;
    }
    #status-area {
        text-align: center;
        margin: 4;
        height: auto;
    }
    ReportView {
        height: 1fr;
    }
    #profile-split {
        height: auto;
    }
    #profile-split DataTable {
        width: 1fr;
        height: auto;
        max-height: 16;
    }
    #profile-desc {
        width: 1fr;
        padding: 1 2;
        height: auto;
    }
    Collapsible {
        margin: 0 0 1 0;
    }
    #about-dialog {
        width: 76;
        height: auto;
        max-height: 46;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        margin: 1 2;
    }
    #about-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    #about-scroll {
        height: auto;
        max-height: 34;
        margin: 0 1;
    }
    #about-content {
        width: 1fr;
        margin: 0 1;
    }
    #about-hint {
        text-align: center;
        margin-top: 1;
    }
    #news-dialog, #download-dialog {
        width: 60;
        height: auto;
        max-height: 10;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        margin: 6 10;
        align-horizontal: center;
    }
    #news-dialog-label, #download-dialog-label {
        text-align: center;
        margin-bottom: 1;
    }
    #news-dialog-buttons {
        align-horizontal: center;
        height: auto;
    }
    #news-dialog-buttons Button {
        margin: 0 1;
    }
    #download-ok-btn {
        margin: 0 1;
    }
    #explain-dialog {
        width: 100;
        height: auto;
        max-height: 40;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        margin: 1 2;
    }
    #explain-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    #explain-scroll {
        height: auto;
        max-height: 30;
        margin: 0 1;
    }
    #explain-content {
        width: 1fr;
        margin: 0 1;
    }
    #explain-hint {
        text-align: center;
        margin-top: 1;
    }
    #metric-list-dialog {
        width: 100;
        height: 38;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        margin: 2 4;
    }
    #metric-list-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    #metric-list-hint {
        text-align: center;
        margin-top: 1;
    }
    #export-dialog {
        width: 50;
        height: auto;
        max-height: 10;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        margin: 6 10;
    }
    #export-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    #export-buttons {
        align-horizontal: center;
        height: auto;
    }
    #export-buttons Button {
        margin: 0 1;
    }
    #export-hint {
        text-align: center;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("a", "analyze", "Analyze"),
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("t", "cycle_theme", "Theme"),
        Binding("f1", "about", "About"),
        Binding("e", "explain_context", "Explain"),
        Binding("E", "explain_all", "Metrics List", key_display="shift+e"),
        Binding("i", "info_metric", "Metric Info"),
        Binding("x", "export", "Export"),
        Binding("tab", "focus_next", "Tab:Next"),
        Binding("shift+tab", "focus_previous", "S-Tab:Prev"),
        Binding("enter", "select", "Enter:Open", show=True),
        Binding("space", "toggle_node", "Space:Toggle", show=True),
        Binding("up", "scroll_up", "Up", show=False),
        Binding("down", "scroll_down", "Down", show=False),
        *tui_paging_bindings(),
        Binding("escape", "app.focus('status-area')", "Esc:Back"),
        Binding("ctrl+l", "_ee_lynx", show=False),
        Binding("ctrl+f", "_ee_fortune", show=False),
        Binding("ctrl+m", "_ee_matrix", show=False),
    ]

    report: AnalysisReport | None = None
    _last_identifier: str = ""
    _suppress_news_dialog: bool = False
    _theme_index: int = 0
    _report_view: ReportView | None = None

    def on_mount(self) -> None:
        from lynx_realestate.tui.themes import register_all_themes, THEME_NAMES
        try:
            register_all_themes(self)
            self.theme = THEME_NAMES[0]  # realestate-dark
        except Exception:
            pass  # Fall back to Textual's default theme

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "[bold blue]  lynx-realestate  [/]\n\n"
            "[bold]Real Estate Sector Analysis Tool[/]\n"
            "[dim]Press [bold]A[/bold] to analyze a stock, "
            "[bold]Q[/bold] to quit[/]\n\n"
            "[dim]Navigation: click section headers to expand/collapse  "
            "[bold]\u2191\u2193[/bold] scroll  "
            "[bold]Escape[/bold] go back[/]",
            id="status-area",
        )
        yield Footer()

    def action_about(self) -> None:
        self.push_screen(AboutModal())

    def action_export(self) -> None:
        if not self.report:
            self._set_status("[yellow]No analysis loaded. Press A to analyze first.[/]")
            return
        self.push_screen(ExportModal(), self._on_export_result)

    def _on_export_result(self, fmt: str) -> None:
        if not fmt or not self.report:
            return
        self._do_export(fmt)

    @work(thread=True)
    def _do_export(self, fmt: str) -> None:
        from lynx_realestate.export import ExportFormat, export_report
        try:
            path = export_report(self.report, ExportFormat(fmt))
            self.call_from_thread(
                self.push_screen,
                DownloadResultDialog(f"Report exported to:\n{path}", success=True),
            )
        except Exception as e:
            self.call_from_thread(
                self.push_screen,
                DownloadResultDialog(f"Export failed: {e}", success=False),
            )

    def action_explain_all(self) -> None:
        """Browse all metric explanations (Shift+E)."""
        self.push_screen(MetricListModal(focus_key=""), self._on_explain_result)

    def _on_explain_result(self, key: str) -> None:
        if key:
            self.push_screen(ExplainModal(key, kind="metric"))

    def action_explain_context(self) -> None:
        """Context-aware explain (e): explains the focused metric, section, or conclusion item."""
        focused = self.focused

        # If on a DataTable, try to explain the selected metric row
        if isinstance(focused, DataTable):
            try:
                row_key = focused.coordinate_to_cell_key(focused.cursor_coordinate).row_key
                key_str = str(row_key.value) if row_key.value else ""
                if key_str:
                    self.push_screen(ExplainModal(key_str, kind="metric"))
                    return
            except Exception:
                pass

            # Check if the DataTable is inside a conclusion section
            section = self._find_parent_section(focused)
            if section == "conclusion":
                # Try to explain the specific conclusion category
                try:
                    row_idx = focused.cursor_coordinate.row
                    row_data = focused.get_row_at(row_idx)
                    cell_text = str(row_data[0]) if row_data else ""
                    # Category rows like "Valuation (65)"
                    for cat in ("valuation", "profitability", "solvency", "growth", "real_estate_quality"):
                        if cat in cell_text.lower():
                            self.push_screen(ExplainModal(cat, kind="conclusion"))
                            return
                    # Verdict / Summary / Strength / Risk / Tier Note
                    self.push_screen(ExplainModal("overall", kind="conclusion"))
                    return
                except Exception:
                    self.push_screen(ExplainModal("overall", kind="conclusion"))
                    return

            # If the DataTable row has no metric key, explain the parent section
            if section:
                self.push_screen(ExplainModal(section, kind="section"))
                return

        # If on a Collapsible or any widget, try to explain the parent section
        if focused is not None:
            section = self._find_parent_section(focused)
            if section:
                if section == "conclusion":
                    self.push_screen(ExplainModal("overall", kind="conclusion"))
                else:
                    self.push_screen(ExplainModal(section, kind="section"))
                return

        self.notify("Nothing to explain here. Select a metric or section.", timeout=3)

    def _find_parent_section(self, widget) -> str:
        """Walk up the widget tree to find which analysis section a widget belongs to."""
        _SECTION_MAP = {
            "sec-profile": "profile",
            "sec-filings": "filings",
            "sec-news": "news",
        }
        _TITLE_MAP = {
            "company profile": "profile",
            "valuation": "valuation",
            "profitability": "profitability",
            "solvency": "solvency",
            "growth": "growth",
            "share structure": "share_structure",
            "real estate quality": "real_estate_quality",
            "intrinsic value": "intrinsic_value",
            "market intelligence": "market_intelligence",
            "financials": "financials",
            "filings": "filings",
            "news": "news",
            "conclusion": "conclusion",
            "screening": "conclusion",
        }
        for ancestor in widget.ancestors_with_self:
            if isinstance(ancestor, Collapsible):
                # Check by ID first
                if ancestor.id and ancestor.id in _SECTION_MAP:
                    return _SECTION_MAP[ancestor.id]
                # Check by title
                title = str(getattr(ancestor, "title", "")).lower()
                for key, section in _TITLE_MAP.items():
                    if key in title:
                        return section
        return ""

    def action_info_metric(self) -> None:
        """Browse all metric explanations (I key).

        If the cursor is on a DataTable metric row, the list opens
        with that metric pre-selected.  Otherwise it starts at the top.
        """
        focus_key = ""
        focused = self.focused
        if isinstance(focused, DataTable):
            try:
                row_key = focused.coordinate_to_cell_key(focused.cursor_coordinate).row_key
                key_str = str(row_key.value) if row_key.value else ""
                if key_str:
                    focus_key = key_str
            except Exception:
                pass
        self.push_screen(MetricListModal(focus_key=focus_key), self._on_explain_result)

    def action_analyze(self) -> None:
        self.push_screen(SearchModal(), self._on_search_result)

    def action_cycle_theme(self) -> None:
        from lynx_realestate.tui.themes import THEME_NAMES
        self._theme_index = (self._theme_index + 1) % len(THEME_NAMES)
        self.theme = THEME_NAMES[self._theme_index]
        self.notify(f"Theme: {self.theme}", timeout=2)

    def action__ee_lynx(self) -> None:
        from lynx_realestate.easter import LYNX_ASCII, WOLF_ASCII, BULL_ASCII
        import random
        art = random.choice([LYNX_ASCII, WOLF_ASCII, BULL_ASCII])
        self.notify(art.strip(), timeout=5)

    def action__ee_fortune(self) -> None:
        from lynx_realestate.easter import FORTUNE_QUOTES
        import random
        quote = random.choice(FORTUNE_QUOTES)
        self.notify(f"\u2728 {quote}", timeout=8)

    def action__ee_matrix(self) -> None:
        from lynx_realestate.tui.themes import THEME_NAMES
        import random
        for i in range(14):
            self._theme_index = (self._theme_index + 1) % len(THEME_NAMES)
            self.theme = THEME_NAMES[self._theme_index]
            self.set_timer(0.2 * i, lambda idx=self._theme_index: None)
        self.notify("\U0001f9e0 You found the Matrix!", timeout=3)

    def action_refresh(self) -> None:
        if self._last_identifier:
            self._start_analysis(self._last_identifier, force_refresh=True)

    def _on_search_result(self, identifier: str) -> None:
        if identifier:
            self._start_analysis(identifier)

    def _start_analysis(self, identifier: str, force_refresh: bool = False) -> None:
        self._last_identifier = identifier
        # Prepare an empty ReportView that will receive sections progressively
        self._remove_reports()
        try:
            self.query_one("#status-area", Static).display = False
        except Exception:
            pass
        self._report_view = ReportView()
        self.mount(self._report_view, before=self.query_one(Footer))
        self._do_analysis(identifier, force_refresh)

    @work(thread=True, exclusive=True)
    def _do_analysis(self, identifier: str, force_refresh: bool = False) -> None:
        from lynx_realestate.core.analyzer import run_progressive_analysis
        from lynx_realestate.core.storage import is_testing

        def on_progress(stage: str, report) -> None:
            """Forward each stage to the main thread for rendering."""
            self.report = report
            self.call_from_thread(self._render_stage, stage, report)

        try:
            refresh = force_refresh or is_testing()
            report = run_progressive_analysis(
                identifier,
                download_reports=True,
                download_news=True,
                refresh=refresh,
                on_progress=on_progress,
            )
            self.report = report
        except Exception as e:
            from lynx_realestate.core.analyzer import SectorMismatchError
            if isinstance(e, SectorMismatchError):
                self.call_from_thread(
                    self._set_status,
                    f"[bold blink red]!! SECTOR MISMATCH — ANALYSIS BLOCKED !![/]\n\n"
                    f"[bold red]{e}[/]\n\n"
                    f"[bold blink red]This tool is specialized ONLY for the Real Estate sector:[/]\n"
                    f"[red]REITs | Real Estate Operating Companies | Property Management[/]\n\n"
                    f"[dim]Press A to analyze a different stock[/]",
                )
            else:
                msg = str(e) if str(e) else type(e).__name__
                self.call_from_thread(
                    self._set_status,
                    f"[bold red]Error:[/] {msg}\n\n"
                    "[dim]Press A to try again[/]",
                )

    def _set_status(self, message: str) -> None:
        self._remove_reports()
        try:
            sa = self.query_one("#status-area", Static)
            sa.update(message)
            sa.display = True
        except Exception:
            pass

    def _remove_reports(self) -> None:
        self._report_view = None
        try:
            for w in list(self.query(ReportView)):
                w.remove()
        except Exception:
            pass

    def _render_stage(self, stage: str, report: AnalysisReport) -> None:
        """Mount a single section into the live ReportView."""
        try:
            view = self._report_view
            if view is None:
                return
            view.add_stage(stage, report)
        except Exception as e:
            # Don't destroy the report view on a single-section error.
            self.notify(
                f"Render error ({stage}): {type(e).__name__}: {e}",
                severity="error",
                timeout=8,
            )

    # --- DataTable row selection handlers ---

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle Enter on a selected row in Filings or News tables."""
        if not self.report:
            return

        # Determine which section the table is in by checking parent Collapsible
        table = event.data_table
        section_id = ""
        for ancestor in table.ancestors_with_self:
            if isinstance(ancestor, Collapsible) and ancestor.id:
                section_id = ancestor.id
                break

        row_idx = event.cursor_row

        if section_id == "sec-filings":
            self._download_filing(row_idx)
        elif section_id == "sec-news":
            self._open_news(row_idx)

    def _download_filing(self, row_idx: int) -> None:
        if not self.report or not self.report.filings:
            return
        filings = self.report.filings[:20]
        if row_idx < 0 or row_idx >= len(filings):
            return
        filing = filings[row_idx]
        self._do_download_filing(filing)

    @work(thread=True)
    def _do_download_filing(self, filing) -> None:
        from lynx_realestate.core.reports import download_filing
        report = self.report
        if not report:
            return
        try:
            path = download_filing(report.profile.ticker, filing)
            if path:
                self.call_from_thread(
                    self.push_screen,
                    DownloadResultDialog(
                        f"Filing {filing.form_type} ({filing.filing_date}) downloaded.\n"
                        f"Saved to: {path}",
                        success=True,
                    ),
                )
            else:
                self.call_from_thread(
                    self.push_screen,
                    DownloadResultDialog(
                        f"Failed to download {filing.form_type} ({filing.filing_date}).",
                        success=False,
                    ),
                )
        except Exception as e:
            self.call_from_thread(
                self.push_screen,
                DownloadResultDialog(f"Download error: {e}", success=False),
            )

    def _open_news(self, row_idx: int) -> None:
        if not self.report or not self.report.news:
            return
        articles = self.report.news[:20]
        if row_idx < 0 or row_idx >= len(articles):
            return
        article = articles[row_idx]
        if not article.url:
            return

        if safe_webbrowser_open(article.url):
            if not self._suppress_news_dialog:
                self.push_screen(
                    NewsBrowserDialog(),
                    self._on_news_dialog_result,
                )

    def _on_news_dialog_result(self, result: str) -> None:
        if result == "suppress":
            self._suppress_news_dialog = True


# ======================================================================
# Table builders
# ======================================================================

def _build_profile_table(r: AnalysisReport) -> DataTable:
    """Build the company profile key-value table (left side of split)."""
    p = r.profile
    t = DataTable(zebra_stripes=True, show_cursor=False)
    t.add_column("Field", width=22)
    t.add_column("Value", width=None)
    _r2(t, "Company", _s(p.name))
    _r2(t, "Ticker", _s(p.ticker))
    if p.isin:
        _r2(t, "ISIN", p.isin)
    _r2(t, "Tier", _safe_tier(p.tier))
    _r2(t, "Stage", _safe_stage(p.stage))
    _r2(t, "Property Type", _s(p.primary_property_type.value if hasattr(p.primary_property_type, "value") else p.primary_property_type))
    _r2(t, "Jurisdiction", _s(p.jurisdiction_tier.value if hasattr(p.jurisdiction_tier, "value") else p.jurisdiction_tier))
    _r2(t, "Jurisdiction Country", _s(p.jurisdiction_country))
    _r2(t, "Sector", _s(p.sector))
    _r2(t, "Industry", _s(p.industry))
    _r2(t, "Country", _s(p.country))
    _r2(t, "Exchange", _s(p.exchange))
    _r2(t, "Market Cap", _money(p.market_cap))
    _r2(t, "Employees", f"{p.employees:,}" if p.employees else "N/A")
    if p.website:
        _r2(t, "Website", p.website)
    return t


def _build_valuation(r: AnalysisReport) -> DataTable:
    v = r.valuation
    stage = _get_stage(r)
    tier = _get_tier(r)
    t = DataTable(zebra_stripes=True, cursor_type="row")
    t.add_column("Metric", width=26)
    t.add_column("Value", width=16)
    t.add_column("Assessment", width=None)
    t.add_column("?", width=3)
    if v is None:
        return t

    def rel(key: str) -> Relevance:
        return _get_rel(key, tier, "valuation", stage)

    _rm_rel(t, "P/E (Trailing)", _num(v.pe_trailing), _ape(v.pe_trailing), "pe_trailing", rel("pe_trailing"))
    _rm_rel(t, "P/E (Forward)", _num(v.pe_forward), _ape(v.pe_forward), "pe_forward", rel("pe_forward"))
    _rm_rel(t, "P/B Ratio", _num(v.pb_ratio), _thr(v.pb_ratio, [(1, "Below Book"), (1.5, "Cheap"), (3, "Fair")], "Premium"), "pb_ratio", rel("pb_ratio"))
    _rm_rel(t, "P/S Ratio", _num(v.ps_ratio), "", "ps_ratio", rel("ps_ratio"))
    _rm_rel(t, "P/FCF", _num(v.p_fcf), _thr(v.p_fcf, [(10, "Cheap"), (20, "Fair")], "Expensive"), "p_fcf", rel("p_fcf"))
    _rm_rel(t, "EV/EBITDA", _num(v.ev_ebitda), _thr(v.ev_ebitda, [(8, "Cheap"), (12, "Fair"), (18, "Expensive")], "Very Expensive"), "ev_ebitda", rel("ev_ebitda"))
    _rm_rel(t, "EV/Revenue", _num(v.ev_revenue), _thr(v.ev_revenue, [(1, "Very cheap"), (3, "Cheap"), (5, "Fair"), (8, "Expensive")], "Very expensive"), "ev_revenue", rel("ev_revenue"))
    _rm_rel(t, "PEG Ratio", _num(v.peg_ratio), _thr(v.peg_ratio, [(1, "Undervalued"), (2, "Fair")], "Overvalued"), "peg_ratio", rel("peg_ratio"))
    _rm_rel(t, "Earnings Yield", _pct(v.earnings_yield), _yield_assess(v.earnings_yield), "earnings_yield", rel("earnings_yield"))
    _rm_rel(t, "Dividend Yield", _pct(v.dividend_yield), _div_assess(v.dividend_yield), "dividend_yield", rel("dividend_yield"))
    _rm_rel(t, "P/Tangible Book", _num(v.price_to_tangible_book), _thr(v.price_to_tangible_book, [(0.67, "Deep Value"), (1, "Below Book"), (1.5, "Near Book")], "Premium"), "price_to_tangible_book", rel("price_to_tangible_book"))
    _rm_rel(t, "P/NCAV (Net-Net)", _num(v.price_to_ncav), _thr(v.price_to_ncav, [(0.67, "Classic Net-Net"), (1, "Below NCAV"), (1.5, "Near NCAV")], "Above NCAV"), "price_to_ncav", rel("price_to_ncav"))
    _rm_rel(t, "Cash/Market Cap", _pct(v.cash_to_market_cap), _thr(v.cash_to_market_cap, [(0.1, "Low"), (0.3, "Moderate"), (0.5, "Strong")], "Very strong"), "cash_to_market_cap", rel("cash_to_market_cap"))
    _rm_rel(t, "Enterprise Value", _money(v.enterprise_value), "", "", Relevance.RELEVANT)
    _rm_rel(t, "Market Cap", _money(v.market_cap), "", "", Relevance.RELEVANT)
    return t


def _build_profitability(r: AnalysisReport) -> DataTable | Static:
    p = r.profitability
    stage = _get_stage(r)
    tier = _get_tier(r)

    def rel(key: str) -> Relevance:
        return _get_rel(key, tier, "profitability", stage)

    _keys = ["roe", "roa", "roic", "gross_margin", "operating_margin", "net_margin", "fcf_margin", "ebitda_margin"]
    if p is None or all(rel(k) == Relevance.IRRELEVANT for k in _keys):
        stage_name = _safe_stage(stage)
        return Static(
            f"[dim]Profitability metrics are not applicable for {stage_name} stage companies. "
            f"Pre-revenue real-estate companies have no meaningful margins or returns on capital to evaluate.[/]"
        )

    t = DataTable(zebra_stripes=True, cursor_type="row")
    t.add_column("Metric", width=26)
    t.add_column("Value", width=16)
    t.add_column("Assessment", width=None)
    t.add_column("?", width=3)

    _rm_rel(t, "ROE", _pct(p.roe), _thr(p.roe, [(0, "Negative"), (0.10, "Below Avg"), (0.15, "Good"), (0.20, "Excellent")], "Outstanding"), "roe", rel("roe"))
    _rm_rel(t, "ROA", _pct(p.roa), _thr(p.roa, [(0, "Negative"), (0.05, "Low"), (0.10, "Good")], "Excellent"), "roa", rel("roa"))
    _rm_rel(t, "ROIC", _pct(p.roic), _thr(p.roic, [(0, "Negative"), (0.07, "Below WACC"), (0.10, "Good"), (0.15, "Wide Moat")], "Exceptional"), "roic", rel("roic"))
    _rm_rel(t, "Gross Margin", _pct(p.gross_margin), "", "gross_margin", rel("gross_margin"))
    _rm_rel(t, "Operating Margin", _pct(p.operating_margin), _margin_assess(p.operating_margin, 0.25, 0.15, 0.05), "operating_margin", rel("operating_margin"))
    _rm_rel(t, "Net Margin", _pct(p.net_margin), _margin_assess(p.net_margin, 0.20, 0.10, 0.05), "net_margin", rel("net_margin"))
    _rm_rel(t, "FCF Margin", _pct(p.fcf_margin), _margin_assess(p.fcf_margin, 0.20, 0.10, 0.05), "fcf_margin", rel("fcf_margin"))
    _rm_rel(t, "EBITDA Margin", _pct(p.ebitda_margin), _margin_assess(p.ebitda_margin, 0.30, 0.15, 0.05), "ebitda_margin", rel("ebitda_margin"))
    return t


def _build_solvency(r: AnalysisReport) -> DataTable:
    s = r.solvency
    stage = _get_stage(r)
    tier = _get_tier(r)
    t = DataTable(zebra_stripes=True, cursor_type="row")
    t.add_column("Metric", width=26)
    t.add_column("Value", width=16)
    t.add_column("Assessment", width=None)
    t.add_column("?", width=3)
    if s is None:
        return t

    def rel(key: str) -> Relevance:
        return _get_rel(key, tier, "solvency", stage)

    _rm_rel(t, "Debt/Equity", _num(s.debt_to_equity), _thr(s.debt_to_equity, [(0.3, "Very Conservative"), (0.5, "Conservative"), (1.0, "Moderate"), (2.0, "High")], "Very High"), "debt_to_equity", rel("debt_to_equity"))
    _rm_rel(t, "Debt/EBITDA", _num(s.debt_to_ebitda), _thr(s.debt_to_ebitda, [(1, "Very Low"), (2, "Manageable"), (3, "Moderate")], "Heavy"), "debt_to_ebitda", rel("debt_to_ebitda"))
    _rm_rel(t, "Current Ratio", _num(s.current_ratio), _thr(s.current_ratio, [(1.0, "Liquidity Risk"), (1.5, "Adequate"), (2.0, "Good")], "Strong"), "current_ratio", rel("current_ratio"))
    _rm_rel(t, "Quick Ratio", _num(s.quick_ratio), "", "quick_ratio", rel("quick_ratio"))
    _rm_rel(t, "Interest Coverage", _num(s.interest_coverage, 1), _thr(s.interest_coverage, [(1, "Cannot cover"), (2, "Tight"), (4, "Adequate"), (8, "Strong")], "Very strong"), "interest_coverage", rel("interest_coverage"))
    _rm_rel(t, "Altman Z-Score", _num(s.altman_z_score), _thr(s.altman_z_score, [(1.81, "Distress"), (2.99, "Grey Zone")], "Safe"), "altman_z_score", rel("altman_z_score"))
    _rm_rel(t, "Cash Burn Rate (/yr)", _money(s.cash_burn_rate), _burn(s.cash_burn_rate), "cash_burn_rate", rel("cash_burn_rate"))
    _rm_rel(t, "Cash Runway", f"{s.cash_runway_years:.1f} yrs" if s.cash_runway_years is not None else "N/A", "", "cash_runway_years", rel("cash_runway_years"))
    _rm_rel(t, "Burn % of Market Cap", _pct(s.burn_as_pct_of_market_cap), _thr(s.burn_as_pct_of_market_cap, [(0.05, "Low"), (0.10, "Moderate"), (0.20, "Concerning")], "Critical"), "burn_as_pct_of_market_cap", rel("burn_as_pct_of_market_cap"))
    _rm_rel(t, "Working Capital", _money(s.working_capital), "", "working_capital", rel("working_capital"))
    _rm_rel(t, "Cash Per Share", f"${s.cash_per_share:.2f}" if s.cash_per_share is not None else "N/A", "", "cash_per_share", rel("cash_per_share"))
    _rm_rel(t, "NCAV Per Share", f"${s.ncav_per_share:.4f}" if s.ncav_per_share is not None else "N/A", "", "ncav_per_share", rel("ncav_per_share"))
    _rm_rel(t, "Total Debt", _money(s.total_debt), "", "", Relevance.RELEVANT)
    _rm_rel(t, "Total Cash", _money(s.total_cash), "", "", Relevance.RELEVANT)
    _rm_rel(t, "Net Debt", _money(s.net_debt), "", "", Relevance.RELEVANT)
    return t


def _build_growth(r: AnalysisReport) -> DataTable:
    g = r.growth
    stage = _get_stage(r)
    tier = _get_tier(r)
    t = DataTable(zebra_stripes=True, cursor_type="row")
    t.add_column("Metric", width=26)
    t.add_column("Value", width=16)
    t.add_column("Assessment", width=None)
    t.add_column("?", width=3)
    if g is None:
        return t

    def rel(key: str) -> Relevance:
        return _get_rel(key, tier, "growth", stage)

    _rm_rel(t, "Revenue Growth (YoY)", _pct(g.revenue_growth_yoy), _growth_assess(g.revenue_growth_yoy), "revenue_growth_yoy", rel("revenue_growth_yoy"))
    _rm_rel(t, "Revenue CAGR (3Y)", _pct(g.revenue_cagr_3y), _cagr_assess(g.revenue_cagr_3y), "revenue_cagr_3y", rel("revenue_cagr_3y"))
    _rm_rel(t, "Revenue CAGR (5Y)", _pct(g.revenue_cagr_5y), _cagr_assess(g.revenue_cagr_5y), "revenue_cagr_5y", rel("revenue_cagr_5y"))
    _rm_rel(t, "Earnings Growth (YoY)", _pct(g.earnings_growth_yoy), _growth_assess(g.earnings_growth_yoy), "earnings_growth_yoy", rel("earnings_growth_yoy"))
    _rm_rel(t, "Earnings CAGR (3Y)", _pct(g.earnings_cagr_3y), _cagr_assess(g.earnings_cagr_3y), "earnings_cagr_3y", rel("earnings_cagr_3y"))
    _rm_rel(t, "Earnings CAGR (5Y)", _pct(g.earnings_cagr_5y), _cagr_assess(g.earnings_cagr_5y), "earnings_cagr_5y", rel("earnings_cagr_5y"))
    _rm_rel(t, "FCF Growth (YoY)", _pct(g.fcf_growth_yoy), _growth_assess(g.fcf_growth_yoy), "fcf_growth_yoy", rel("fcf_growth_yoy"))
    _rm_rel(t, "Book Value Growth (YoY)", _pct(g.book_value_growth_yoy), _growth_assess(g.book_value_growth_yoy), "book_value_growth_yoy", rel("book_value_growth_yoy"))
    _rm_rel(t, "Share Dilution (YoY)", _pct(g.shares_growth_yoy), _dilution_assess(g.shares_growth_yoy), "shares_growth_yoy", rel("shares_growth_yoy"))
    _rm_rel(t, "Share Dilution CAGR (3Y)", _pct(g.shares_growth_3y_cagr), _cagr_assess(g.shares_growth_3y_cagr), "shares_growth_3y_cagr", rel("shares_growth_3y_cagr"))
    _rm_rel(t, "Dilution Ratio", _num(g.dilution_ratio), _thr(g.dilution_ratio, [(1.0, "No Dilution"), (1.1, "Minimal"), (1.3, "Moderate")], "Significant"), "dilution_ratio", rel("dilution_ratio") if g.dilution_ratio is not None else Relevance.CONTEXTUAL)
    return t


def _build_share_structure(r: AnalysisReport) -> Static:
    """Build a Rich Table for share structure with multi-line cell wrapping."""
    ss = r.share_structure
    stage = _get_stage(r)
    tier = _get_tier(r)
    t = RichTable(show_lines=True, border_style="yellow", expand=True)
    t.add_column("Indicator", style="bold", width=24, no_wrap=True)
    t.add_column("Details", ratio=1, overflow="fold")
    if ss is None:
        return _rich_table_widget(t)

    def rel(key: str) -> Relevance:
        return _get_rel(key, tier, "share_structure", stage)

    def _row(label, value, relevance):
        if relevance == Relevance.IRRELEVANT:
            return
        if relevance == Relevance.CRITICAL:
            prefix = "[bold cyan]*[/] "
        elif relevance == Relevance.IMPORTANT:
            prefix = "[#ff8800]>[/] "
        else:
            prefix = "  "
        val = f"[dim]{value}[/]" if relevance == Relevance.CONTEXTUAL else value
        t.add_row(f"{prefix}{label}", val)

    _row("Shares Outstanding", f"{ss.shares_outstanding:,.0f}" if ss.shares_outstanding else "N/A", rel("shares_outstanding"))
    _row("Fully Diluted Shares", f"{ss.fully_diluted_shares:,.0f}" if ss.fully_diluted_shares else "N/A", rel("fully_diluted_shares"))
    _row("Float", f"{ss.float_shares:,.0f}" if ss.float_shares else "N/A", Relevance.RELEVANT)
    _row("Insider Ownership", _pct(ss.insider_ownership_pct), rel("insider_ownership_pct"))
    _row("Institutional Ownership", _pct(ss.institutional_ownership_pct), rel("institutional_ownership_pct"))
    _row("Assessment", _s(ss.share_structure_assessment), rel("share_structure_assessment"))
    return _rich_table_widget(t)


def _build_real_estate_quality(r: AnalysisReport) -> Static:
    """Build a Rich Table for real estate quality with multi-line cell wrapping."""
    m = r.real_estate_quality
    stage = _get_stage(r)
    tier = _get_tier(r)
    t = RichTable(show_lines=True, border_style="yellow", expand=True)
    t.add_column("Indicator", style="bold", width=24, no_wrap=True)
    t.add_column("Assessment", ratio=1, overflow="fold")
    if m is None:
        return _rich_table_widget(t)

    def rel(key: str) -> Relevance:
        return _get_rel(key, tier, "real_estate_quality", stage)

    def _row(label, value, relevance):
        if relevance == Relevance.IRRELEVANT:
            return
        if relevance == Relevance.CRITICAL:
            prefix = "[bold cyan]*[/] "
        elif relevance == Relevance.IMPORTANT:
            prefix = "[#ff8800]>[/] "
        else:
            prefix = "  "
        val = f"[dim]{value}[/]" if relevance == Relevance.CONTEXTUAL else value
        t.add_row(f"{prefix}{label}", val)

    _row("Quality Score", f"{m.quality_score:.1f}/100" if m.quality_score is not None else "N/A", rel("quality_score"))
    _row("Competitive Position", _s(m.competitive_position), Relevance.RELEVANT)
    _row("Insider Alignment", _s(m.insider_alignment), rel("insider_alignment"))
    _row("Financial Position", _s(m.financial_position), rel("financial_position"))
    _row("Dilution Risk", _s(m.dilution_risk), rel("dilution_risk"))
    _row("Asset Backing", _s(m.asset_backing), rel("asset_backing"))
    _row("Revenue Status", _s(m.revenue_predictability), rel("revenue_predictability"))
    _row("Share Structure", _s(m.share_structure_assessment), Relevance.RELEVANT)
    _row("Management Quality", _s(m.management_quality), Relevance.RELEVANT)
    roic_vals = [v for v in m.roic_history if v is not None]
    if roic_vals:
        t.add_row("[dim]ROIC Trend[/]", " -> ".join(_pctplain(x) for x in reversed(roic_vals)))
    gm_vals = [v for v in m.gross_margin_history if v is not None]
    if gm_vals:
        t.add_row("[dim]GM Trend[/]", " -> ".join(_pctplain(x) for x in reversed(gm_vals)))
    return _rich_table_widget(t)


def _build_insight_table(info) -> Static:
    """Build a Rich Table for a SectorInsight or IndustryInsight.

    Uses Rich Table (not Textual DataTable) because Rich Tables support
    multi-line cells with automatic text wrapping while keeping proper
    table borders and alignment.
    """
    t = RichTable(show_lines=True, border_style="cyan", expand=True)
    t.add_column("Aspect", style="bold cyan", width=20, no_wrap=True)
    t.add_column("Details", ratio=1, overflow="fold")
    t.add_row("Overview", info.overview)
    t.add_row("Critical Metrics", ", ".join(info.critical_metrics))
    t.add_row("Key Risks", ", ".join(info.key_risks))
    t.add_row("What to Watch", ", ".join(info.what_to_watch))
    t.add_row("Typical Valuation", info.typical_valuation)
    return _rich_table_widget(t)


def _build_iv(r: AnalysisReport) -> Static:
    """Build a Rich Table for intrinsic value with multi-line cell wrapping."""
    iv = r.intrinsic_value
    t = RichTable(show_lines=True, border_style="green", expand=True)
    t.add_column("Method", style="bold", width=30, no_wrap=True)
    t.add_column("Value", justify="right", width=16, no_wrap=True)
    t.add_column("Margin of Safety", ratio=1, overflow="fold")
    if iv is None:
        return _rich_table_widget(t)
    primary = _s(iv.primary_method)
    secondary = _s(iv.secondary_method)

    def tag(n):
        if n in primary:
            return "[bold green](primary)[/] "
        if n in secondary:
            return "[cyan](secondary)[/] "
        return "[dim](reference)[/] "

    t.add_row("Current Price", f"${iv.current_price:.2f}" if iv.current_price else "N/A", "")
    t.add_row(f"{tag('DCF')}DCF (10Y)", f"${iv.dcf_value:.2f}" if iv.dcf_value else "N/A", _mos(iv.margin_of_safety_dcf))
    t.add_row(f"{tag('Graham')}Graham Number", f"${iv.graham_number:.2f}" if iv.graham_number else "N/A", _mos(iv.margin_of_safety_graham))
    t.add_row(f"{tag('NCAV')}NCAV (Net-Net)", f"${iv.ncav_value:.4f}" if iv.ncav_value is not None else "N/A", _mos(iv.margin_of_safety_ncav))
    t.add_row(f"{tag('Asset')}Tangible Book", f"${iv.asset_based_value:.4f}" if iv.asset_based_value else "N/A", _mos(iv.margin_of_safety_asset))
    if iv.nav_per_share is not None:
        t.add_row(f"{tag('NAV')}NAV/Share", f"${iv.nav_per_share:.4f}", _mos(iv.margin_of_safety_nav))
    if iv.lynch_fair_value:
        t.add_row("[dim](reference)[/] Lynch Fair Value", f"${iv.lynch_fair_value:.2f}", "")
    t.add_row("Primary Method", primary, "")
    t.add_row("Secondary Method", secondary, "")
    return _rich_table_widget(t)


def _build_market_intelligence(r: AnalysisReport) -> Static:
    """Build Rich Tables for market intelligence section."""
    mi = r.market_intelligence
    if mi is None:
        return Static("[dim]No market intelligence data available.[/]")

    from rich.table import Table as RichTable
    from rich.panel import Panel as RichPanel
    from rich.console import Group

    parts = []

    # Rate Commodity & Sector Context Sector Context
    if mi.benchmark_rate_name or mi.sector_etf_name:
        t = RichTable(show_lines=True, border_style="cyan", expand=True, title="Rate Commodity & Sector Context Sector Context")
        t.add_column("Indicator", style="bold", width=22, no_wrap=True)
        t.add_column("Value", width=14, no_wrap=True)
        t.add_column("Context", ratio=1, overflow="fold")
        if mi.benchmark_rate_name and mi.benchmark_rate_value:
            t.add_row("Property Type", mi.benchmark_rate_name, f"${mi.benchmark_rate_value:,.2f}")
            if mi.rate_52w_high and mi.rate_52w_low:
                t.add_row("52W Range", f"${mi.rate_52w_low:,.2f} - ${mi.rate_52w_high:,.2f}", "")
        if mi.sector_etf_name:
            perf = f"{mi.sector_etf_3m_perf*100:+.1f}% (3m)" if mi.sector_etf_3m_perf is not None else ""
            t.add_row("Sector ETF", f"{mi.sector_etf_name}", f"${mi.sector_etf_price:,.2f}  {perf}" if mi.sector_etf_price else "")
        if mi.peer_etf_name:
            perf = f"{mi.peer_etf_3m_perf*100:+.1f}% (3m)" if mi.peer_etf_3m_perf is not None else ""
            t.add_row("Peer ETF", f"{mi.peer_etf_name}", f"${mi.peer_etf_price:,.2f}  {perf}" if mi.peer_etf_price else "")
        parts.append(t)

    # Analyst Consensus
    if mi.analyst_count and mi.analyst_count > 0:
        t = RichTable(show_lines=True, border_style="blue", expand=True, title="Analyst Consensus")
        t.add_column("Indicator", style="bold", width=22, no_wrap=True)
        t.add_column("Value", width=14, no_wrap=True)
        t.add_column("Assessment", ratio=1, overflow="fold")
        rec = (mi.recommendation or "N/A").replace("_", " ").title()
        t.add_row("Recommendation", rec, "")
        t.add_row("Analyst Count", str(mi.analyst_count), "")
        if mi.target_mean:
            t.add_row("Target Mean", f"${mi.target_mean:.2f}", f"Upside: {mi.target_upside_pct*100:.0f}%" if mi.target_upside_pct else "")
        if mi.target_high:
            t.add_row("Target High", f"${mi.target_high:.2f}", "")
        if mi.target_low:
            t.add_row("Target Low", f"${mi.target_low:.2f}", "")
        parts.append(t)

    # Short Interest
    if mi.shares_short:
        t = RichTable(show_lines=True, border_style="red", expand=True, title="Short Interest")
        t.add_column("Indicator", style="bold", width=22, no_wrap=True)
        t.add_column("Value", width=14, no_wrap=True)
        t.add_column("Assessment", ratio=1, overflow="fold")
        t.add_row("Shares Short", f"{mi.shares_short:,.0f}", "")
        if mi.short_pct_of_float:
            t.add_row("Short % of Float", f"{mi.short_pct_of_float:.1f}%", mi.short_squeeze_risk or "")
        if mi.short_ratio_days:
            t.add_row("Days to Cover", f"{mi.short_ratio_days:.1f}", "")
        parts.append(t)

    # Price Technicals
    t = RichTable(show_lines=True, border_style="magenta", expand=True, title="Price Technicals")
    t.add_column("Indicator", style="bold", width=22, no_wrap=True)
    t.add_column("Value", width=14, no_wrap=True)
    t.add_column("Assessment", ratio=1, overflow="fold")
    has_tech = False
    if mi.price_52w_high:
        t.add_row("52-Week High", f"${mi.price_52w_high:.2f}", f"{mi.pct_from_52w_high*100:.1f}% from high" if mi.pct_from_52w_high else "")
        has_tech = True
    if mi.price_52w_low:
        t.add_row("52-Week Low", f"${mi.price_52w_low:.2f}", f"+{mi.pct_from_52w_low*100:.1f}% from low" if mi.pct_from_52w_low else "")
        has_tech = True
    if mi.sma_50:
        above = "Above" if mi.above_sma_50 else "Below"
        t.add_row("50-Day SMA", f"${mi.sma_50:.2f}", above)
        has_tech = True
    if mi.sma_200:
        above = "Above" if mi.above_sma_200 else "Below"
        t.add_row("200-Day SMA", f"${mi.sma_200:.2f}", above)
        has_tech = True
    if mi.golden_cross is not None:
        signal = "Golden Cross (bullish)" if mi.golden_cross else "Death Cross (bearish)"
        t.add_row("MA Cross", "", signal)
        has_tech = True
    if mi.beta:
        beta_note = "High volatility" if mi.beta > 2 else "Above average" if mi.beta > 1.5 else "Moderate" if mi.beta > 1 else "Low"
        t.add_row("Beta", f"{mi.beta:.2f}", beta_note)
        has_tech = True
    if has_tech:
        parts.append(t)

    # Insider Activity
    if mi.insider_transactions:
        t = RichTable(show_lines=True, border_style="yellow", expand=True, title="Insider Transactions")
        t.add_column("Date", width=12, no_wrap=True)
        t.add_column("Insider", width=22, overflow="fold")
        t.add_column("Shares", justify="right", width=12, no_wrap=True)
        for tx in mi.insider_transactions[:6]:
            t.add_row(tx.date[:10] if tx.date else "", tx.insider, f"{tx.shares:,.0f}" if tx.shares else "N/A")
        if mi.insider_buy_signal:
            t.add_row("", f"[bold]Signal: {mi.insider_buy_signal}[/]", "")
        parts.append(t)

    # Top Holders
    if mi.top_holders:
        holder_text = f"[bold]Institutional Holders[/] ({mi.institutions_count or '?'} total, {mi.institutions_pct*100:.1f}% held)\n" if mi.institutions_pct else "[bold]Institutional Holders[/]\n"
        holder_text += "\n".join(f"  {h}" for h in mi.top_holders[:5])
        parts.append(holder_text)

    # Risk Warnings
    if mi.risk_warnings:
        warn_text = "[bold red]Risk Warnings[/]\n" + "\n".join(f"  [red]\u26a0[/] {w}" for w in mi.risk_warnings)
        parts.append(warn_text)

    # Disclaimers
    if mi.disclaimers:
        disc_text = "[dim]" + "\n".join(f"  {d}" for d in mi.disclaimers) + "[/]"
        parts.append(disc_text)

    # Combine all parts
    combined_parts = []
    for p in parts:
        if isinstance(p, str):
            combined_parts.append(p)
        else:
            # Rich Table - render it
            combined_parts.append(p)

    return _rich_table_widget(Group(*combined_parts))


def _build_conclusion(r: AnalysisReport) -> Static:
    """Build a Rich Table for the conclusion with multi-line text wrapping."""
    from lynx_realestate.core.conclusion import generate_conclusion
    c = generate_conclusion(r)
    t = RichTable(show_lines=True, border_style="cyan", expand=True)
    t.add_column("Item", style="bold", width=24, no_wrap=True)
    t.add_column("Details", ratio=1, overflow="fold")
    t.add_row("Verdict", f"[bold]{c.verdict}[/] ({c.overall_score:.0f}/100)")
    t.add_row("Summary", c.summary)
    for cat in ("valuation", "profitability", "solvency", "growth", "real_estate_quality"):
        score = c.category_scores.get(cat, 0)
        summary = c.category_summaries.get(cat, "")
        sc = "green" if score >= 60 else "yellow" if score >= 40 else "red"
        t.add_row(f"{cat.replace('_', ' ').title()}", f"[{sc}]{score:.0f}/100[/]  {summary}")
    for i, s in enumerate(c.strengths, 1):
        t.add_row(f"[green]Strength {i}[/]", s)
    for i, risk in enumerate(c.risks, 1):
        t.add_row(f"[red]Risk {i}[/]", risk)
    if c.tier_note:
        t.add_row("[dim]Tier Note[/]", f"[dim]{c.tier_note}[/]")
    if c.stage_note:
        t.add_row("[dim]Stage Note[/]", f"[dim]{c.stage_note}[/]")
    # Screening checklist
    if c.screening_checklist:
        _labels = {
            "cash_runway_18m": "Cash Runway >18 months", "low_dilution": "Low Dilution (<5%/yr)",
            "insider_ownership": "Insider Ownership >10%", "tight_share_structure": "Tight Share Structure (<200M)",
            "no_excessive_debt": "No Excessive Debt", "positive_working_capital": "Positive Working Capital",
            "management_track_record": "Management Track Record", "tier_1_2_jurisdiction": "Tier 1/2 Jurisdiction",
            "cash_backing": "Cash Backing >30%", "has_revenue": "Has Revenue (Producers)",
        }
        t.add_row("", "")
        for key, val in c.screening_checklist.items():
            label = _labels.get(key, key.replace("_", " ").title())
            if val is True:
                t.add_row(f"  {label}", "[bold green]PASS[/]")
            elif val is False:
                t.add_row(f"  {label}", "[bold red]FAIL[/]")
            else:
                t.add_row(f"  {label}", "[dim]N/A[/]")
    return _rich_table_widget(t)


def _build_screening(checklist: dict) -> Static:
    """Build a Rich Table for the 10-point screening checklist."""
    t = RichTable(border_style="cyan", expand=True)
    t.add_column("Criterion", style="bold", width=32, no_wrap=True)
    t.add_column("Result", justify="center", width=8, no_wrap=True)
    _labels = {
        "cash_runway_18m": "Cash Runway >18 months",
        "low_dilution": "Low Dilution (<5%/yr)",
        "insider_ownership": "Insider Ownership >10%",
        "tight_share_structure": "Tight Share Structure (<200M)",
        "no_excessive_debt": "No Excessive Debt",
        "positive_working_capital": "Positive Working Capital",
        "management_track_record": "Management Track Record",
        "tier_1_2_jurisdiction": "Tier 1/2 Jurisdiction",
        "cash_backing": "Cash Backing >30%",
        "has_revenue": "Has Revenue (Producers)",
    }
    for key, val in checklist.items():
        label = _labels.get(key, key.replace("_", " ").title())
        if val is True:
            t.add_row(label, "[bold green]PASS[/]")
        elif val is False:
            t.add_row(label, "[bold red]FAIL[/]")
        else:
            t.add_row(label, "[dim]N/A[/]")
    return _rich_table_widget(t)


def _build_financials(r: AnalysisReport) -> DataTable:
    t = DataTable(zebra_stripes=True)
    t.add_column("Period", width=6)
    t.add_column("Revenue", width=12)
    t.add_column("Gross Profit", width=12)
    t.add_column("Op Income", width=12)
    t.add_column("Net Income", width=12)
    t.add_column("FCF", width=12)
    t.add_column("Equity", width=12)
    t.add_column("Debt", width=12)
    for st in (r.financials or [])[:5]:
        t.add_row(_s(st.period), _money(st.revenue), _money(st.gross_profit),
                  _money(st.operating_income), _money(st.net_income),
                  _money(st.free_cash_flow), _money(st.total_equity), _money(st.total_debt))
    return t


def _build_filings(r: AnalysisReport) -> DataTable:
    t = DataTable(zebra_stripes=True, cursor_type="row")
    t.add_column("#", width=4)
    t.add_column("Type", width=10)
    t.add_column("Filed", width=12)
    t.add_column("Period", width=12)
    t.add_column("Saved", width=6)
    for i, f in enumerate((r.filings or [])[:20], 1):
        t.add_row(str(i), _s(f.form_type), _s(f.filing_date), _s(f.period), "Yes" if f.local_path else "No")
    return t


def _build_news(r: AnalysisReport) -> DataTable:
    t = DataTable(zebra_stripes=True, cursor_type="row")
    t.add_column("#", width=4)
    t.add_column("Title", width=None)  # auto-size to content
    t.add_column("Source", width=20)
    t.add_column("Date", width=26)
    for i, n in enumerate((r.news or [])[:20], 1):
        t.add_row(str(i), n.title or "", _s(n.source), _s(n.published))
    return t


# ======================================================================
# Relevance-aware row helpers
# ======================================================================

def _rm_rel(t: DataTable, label: str, value: str, assessment: str,
            key: str, rel: Relevance) -> None:
    """Add a metric row with relevance styling."""
    if rel == Relevance.IRRELEVANT:
        return  # Skip irrelevant metrics entirely
    prefix = ""
    if rel == Relevance.CRITICAL:
        prefix = "* "
        label = f"{prefix}{label}"
    elif rel == Relevance.IMPORTANT:
        prefix = "> "
        label = f"{prefix}{label}"
    elif rel == Relevance.CONTEXTUAL:
        label = f"  {label}"
        value = f"[dim]{value}[/]" if not value.startswith("[") else value
        assessment = f"[dim]{assessment}[/]" if assessment and not assessment.startswith("[") else assessment
    else:
        label = f"  {label}"
    t.add_row(str(label), str(value), str(assessment), "\u2139" if key else "", key=key if key else None)


def _r2_rel(t: DataTable, label: str, value: str, rel: Relevance) -> None:
    """Add a 2-column row with relevance styling."""
    if rel == Relevance.IRRELEVANT:
        return
    if rel == Relevance.CRITICAL:
        label = f"* {label}"
    elif rel == Relevance.CONTEXTUAL:
        value = f"[dim]{value}[/]" if not str(value).startswith("[") else str(value)
    t.add_row(str(label), str(value))


def _get_rel(key: str, tier: CompanyTier, category: str, stage: CompanyStage) -> Relevance:
    """Convenience wrapper for the relevance lookup."""
    from lynx_realestate.metrics.relevance import get_relevance
    return get_relevance(key, tier, category=category, stage=stage)


# ======================================================================
# Safe formatters
# ======================================================================

def _r3(t: DataTable, c1: str, c2: str, c3: str) -> None:
    t.add_row(str(c1), str(c2), str(c3))


def _rm(t: DataTable, c1: str, c2: str, c3: str, key: str = "") -> None:
    """Add a metric row with an info marker if a key is available."""
    t.add_row(str(c1), str(c2), str(c3), "\u2139" if key else "", key=key if key else None)


def _r2(t: DataTable, c1: str, c2: str) -> None:
    t.add_row(str(c1), str(c2))


def _rich_table_widget(table: RichTable) -> Static:
    """Wrap a Rich Table in a Textual Static widget.

    Textual's Static widget natively accepts Rich renderable objects.
    The table is passed directly — Textual handles rendering through
    its own pipeline, avoiding ANSI escape code conflicts that cause
    color bleeding and visual artifacts when scrolling.
    """
    return Static(table)


def _s(val) -> str:
    return str(val) if val is not None else "N/A"


def _num(val, digits: int = 2) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
        if v != v:
            return "N/A"  # NaN check
        return f"{v:,.{digits}f}"
    except Exception:
        return "N/A"


def _pct(val) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
        if v != v:
            return "N/A"  # NaN check
        return f"{v * 100:.2f}%"
    except Exception:
        return "N/A"


def _pctplain(val) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
        if v != v:
            return "N/A"  # NaN check
        return f"{v * 100:.1f}%"
    except Exception:
        return "N/A"


def _money(val) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
        if v != v:
            return "N/A"  # NaN check
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


def _yield_assess(val) -> str:
    if val is None:
        return ""
    try:
        v = float(val)
        if v > 0.10:
            return "Excellent"
        if v > 0.07:
            return "Good"
        if v > 0.05:
            return "Fair"
        if v > 0:
            return "Low"
        return "Negative"
    except Exception:
        return ""


def _div_assess(val) -> str:
    if val is None:
        return ""
    try:
        v = float(val)
        if v <= 0:
            return "No dividend"
        if v > 0.06:
            return "Very high"
        if v > 0.04:
            return "High"
        if v > 0.02:
            return "Moderate"
        return "Low"
    except Exception:
        return ""


def _margin_assess(val, exc: float, good: float, fair: float) -> str:
    if val is None:
        return ""
    try:
        v = float(val)
        if v < 0:
            return "Negative"
        if v > exc:
            return "Excellent"
        if v > good:
            return "Good"
        if v > fair:
            return "Moderate"
        return "Thin"
    except Exception:
        return ""


def _growth_assess(val) -> str:
    if val is None:
        return ""
    try:
        v = float(val)
        if v > 0.25:
            return "Very strong"
        if v > 0.10:
            return "Good"
        if v > 0:
            return "Positive"
        if v > -0.10:
            return "Slight decline"
        return "Declining"
    except Exception:
        return ""


def _cagr_assess(val) -> str:
    if val is None:
        return ""
    try:
        v = float(val)
        if v > 0.15:
            return "Excellent"
        if v > 0.08:
            return "Good"
        if v > 0:
            return "Positive"
        return "Declining"
    except Exception:
        return ""


def _dilution_assess(val) -> str:
    if val is None:
        return ""
    try:
        v = float(val)
        if v < -0.02:
            return "Buybacks"
        if v < 0.01:
            return "Minimal"
        if v < 0.05:
            return "Modest (<5%)"
        if v < 0.10:
            return "Significant"
        return "Heavy dilution"
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


def _safe_stage(stage) -> str:
    if isinstance(stage, CompanyStage):
        return stage.value
    return str(stage) if stage else "N/A"


def _get_stage(r: AnalysisReport) -> CompanyStage:
    try:
        stage = r.profile.stage
        if isinstance(stage, CompanyStage):
            return stage
    except Exception:
        pass
    return CompanyStage.PRE_DEVELOPMENT


# ======================================================================
# Entry point
# ======================================================================

def run_tui() -> None:
    app = LynxRealEstateApp()
    app.run()
