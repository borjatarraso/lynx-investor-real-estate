"""Command-line interface for lynx-realestate."""

from __future__ import annotations

import argparse
import sys

from lynx_realestate import __author__, __author_email__, __license__, __version__, __year__, SUITE_LABEL


def _ticker_completer(prefix, **kw):
    """Dynamic completer that returns cached tickers for this agent's mode."""
    try:
        from lynx_investor_core.storage import list_cached_tickers
        items = list_cached_tickers() or []
        return [t["ticker"] for t in items if t["ticker"].startswith(prefix.upper())]
    except Exception:
        return []


def build_parser():
    parser = argparse.ArgumentParser(
        prog="lynx-realestate",
        description="Lynx Real Estate Analysis — REIT and real-estate operating company fundamental analysis tool.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  lynx-realestate -p SPG                            US mall REIT\n"
            "  lynx-realestate -p O                              Triple-net lease REIT\n"
            "  lynx-realestate -p PLD                            Industrial/logistics REIT\n"
            "  lynx-realestate -p EQIX --refresh                 Force fresh data\n"
            '  lynx-realestate -p "Simon Property Group"         Search by name\n'
            "  lynx-realestate -p -i                             Interactive mode\n"
            "  lynx-realestate -t SPG                            Testing mode\n"
        ),
    )
    run_mode = parser.add_mutually_exclusive_group(required=True)
    run_mode.add_argument("-p", "--production-mode", action="store_const", const="production", dest="run_mode",
                          help="Production mode: use data/ for persistent cache")
    run_mode.add_argument("-t", "--testing-mode", action="store_const", const="testing", dest="run_mode",
                          help="Testing mode: use data_test/ (isolated, always fresh)")
    ident_arg = parser.add_argument("identifier", nargs="?", help="Ticker symbol, ISIN, or company name")
    ident_arg.completer = _ticker_completer
    ui_mode = parser.add_mutually_exclusive_group()
    ui_mode.add_argument("-i", "--interactive-mode", action="store_true", dest="interactive")
    ui_mode.add_argument("-tui", "--textual-ui", action="store_true", dest="tui")
    ui_mode.add_argument("-s", "--search", action="store_true")
    ui_mode.add_argument("-x", "--gui", action="store_true", help="Launch the graphical user interface (Tkinter)")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--drop-cache", metavar="TICKER", nargs="?", const="__prompt__")
    parser.add_argument("--list-cache", action="store_true")
    parser.add_argument("--no-reports", action="store_true", help="Skip fetching SEC/SEDAR filings")
    parser.add_argument("--no-news", action="store_true", help="Skip fetching news articles")

    def _positive_int(value: str) -> int:
        n = int(value)
        if n <= 0:
            raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
        return n

    parser.add_argument("--max-filings", type=_positive_int, default=10, metavar="N",
                        help="Maximum filings to download (default: 10)")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--export", choices=["txt", "html", "pdf"], metavar="FORMAT")
    parser.add_argument("--output", metavar="PATH")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}  |  {SUITE_LABEL}  ({__year__}) by {__author__}")
    parser.add_argument("--about", action="store_true")
    parser.add_argument("--explain", metavar="METRIC", nargs="?", const="__list__")
    parser.add_argument("--explain-section", metavar="SECTION", nargs="?", const="__list__")
    parser.add_argument("--explain-conclusion", metavar="CATEGORY", nargs="?", const="overall")
    return parser


def run_cli():
    parser = build_parser()

    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass  # argcomplete optional at runtime

    # Hidden features
    if "--b2m" in sys.argv:
        from rich.console import Console
        from lynx_realestate.easter import rich_rocket, rich_fortune
        c = Console()
        rich_rocket(c)
        rich_fortune(c)
        return

    if "--about" in sys.argv:
        from rich.console import Console; from rich.panel import Panel; from lynx_realestate import get_about_text
        about = get_about_text(); c = Console(stderr=True)
        c.print(f"[bold green]{about['logo']}[/]")
        c.print(Panel(f"[bold blue]{about['name']} v{about['version']}[/]\n[dim]Part of {about['suite']} v{about['suite_version']}[/]\n\n"
                      f"[bold]By:[/] {about['author']}\n[bold]License:[/] {about['license']}\n\n[dim]{about['description']}[/]",
                      title="[bold]About[/]", border_style="blue"))
        return

    if "--explain-section" in sys.argv:
        from rich.console import Console; from rich.panel import Panel; from rich.table import Table
        from lynx_realestate.metrics.explanations import get_section_explanation, SECTION_EXPLANATIONS
        c = Console(stderr=True); idx = sys.argv.index("--explain-section")
        section = sys.argv[idx + 1] if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("-") else None
        if not section:
            t = Table(title="Analysis Sections", border_style="cyan")
            t.add_column("Key", style="bold cyan", min_width=18); t.add_column("Title", min_width=30)
            for key, sec in SECTION_EXPLANATIONS.items():
                t.add_row(key, sec["title"])
            c.print(t)
        else:
            sec = get_section_explanation(section.lower().replace("-", "_"))
            if sec:
                c.print(Panel(f"[bold]{sec['title']}[/]\n\n{sec['description']}", title=f"[bold]{sec['title']}[/]", border_style="cyan"))
            else:
                c.print(f"[red]Unknown section '{section}'.[/]")
        return

    if "--explain-conclusion" in sys.argv:
        from rich.console import Console; from rich.panel import Panel
        from lynx_realestate.metrics.explanations import get_conclusion_explanation, CONCLUSION_METHODOLOGY
        c = Console(stderr=True); idx = sys.argv.index("--explain-conclusion")
        cat = sys.argv[idx + 1] if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("-") else "overall"
        ce = get_conclusion_explanation(cat)
        if ce:
            c.print(Panel(f"[bold]{ce['title']}[/]\n\n{ce['description']}", title=f"[bold]{ce['title']}[/]", border_style="cyan"))
        else:
            c.print(f"[red]Unknown category '{cat}'.[/]")
        return

    if "--explain" in sys.argv:
        from rich.console import Console; from rich.panel import Panel; from rich.table import Table
        from lynx_realestate.metrics.explanations import get_explanation, list_metrics
        c = Console(stderr=True); idx = sys.argv.index("--explain")
        metric = sys.argv[idx+1] if idx+1 < len(sys.argv) and not sys.argv[idx+1].startswith("-") else None
        if not metric:
            t = Table(title="Available Metrics", border_style="cyan")
            t.add_column("Key", style="bold cyan"); t.add_column("Name"); t.add_column("Category")
            for m in list_metrics(): t.add_row(m.key, m.full_name, m.category)
            c.print(t)
        else:
            exp = get_explanation(metric.lower().replace("-", "_"))
            if exp:
                c.print(Panel(f"[bold]{exp.full_name}[/]\n\n{exp.description}\n\n[bold cyan]Why:[/]\n{exp.why_used}\n\n[bold cyan]Formula:[/]\n{exp.formula}",
                              title=f"[bold]{exp.key}[/]", border_style="cyan"))
            else:
                c.print(f"[red]Unknown metric '{metric}'.[/]")
        return

    args = parser.parse_args()
    from rich.console import Console; errc = Console(stderr=True)
    from lynx_realestate.core.storage import set_mode, is_testing
    set_mode(args.run_mode)
    mode_label = "[bold green]PRODUCTION[/]" if args.run_mode == "production" else "[bold yellow]TESTING[/]"
    errc.print(f"Mode: {mode_label}")

    if args.list_cache:
        _cmd_list_cache(errc); return
    if args.drop_cache is not None:
        target = args.drop_cache if args.drop_cache != "__prompt__" else (args.identifier or "")
        if not target: errc.print("[bold red]Error:[/] Specify a ticker or ALL."); sys.exit(1)
        _cmd_drop_cache(errc, target); return
    if args.interactive:
        from lynx_realestate.interactive import run_interactive; run_interactive(); return
    if args.tui:
        from lynx_realestate.tui.app import run_tui; run_tui(); return
    if args.gui:
        from lynx_realestate.gui.app import run_gui; run_gui(args); return
    if args.search:
        if not args.identifier: errc.print("[bold red]Error:[/] Provide a search query."); sys.exit(1)
        from lynx_realestate.core.ticker import search_companies, display_search_results
        results = search_companies(args.identifier, max_results=15)
        if results: display_search_results(results)
        else: errc.print(f"[yellow]No results for '{args.identifier}'.[/]")
        return
    if not args.identifier: parser.print_help(); sys.exit(1)

    refresh = args.refresh or is_testing()
    from lynx_realestate.core.analyzer import run_progressive_analysis
    from lynx_realestate.display import display_report_stage
    try:
        report = run_progressive_analysis(identifier=args.identifier, download_reports=not args.no_reports,
            download_news=not args.no_news, max_filings=args.max_filings, verbose=args.verbose,
            refresh=refresh, on_progress=display_report_stage)
        if args.export:
            from pathlib import Path; from lynx_realestate.export import ExportFormat, export_report
            fmt = ExportFormat(args.export); out = Path(args.output) if args.output else None
            try: path = export_report(report, fmt, out); errc.print(f"[bold green]Exported to:[/] {path}")
            except RuntimeError as e: errc.print(f"[bold red]Export failed:[/] {e}")
    except ValueError as e: errc.print(f"[bold red]Error:[/] {e}"); sys.exit(1)
    except (ConnectionError, TimeoutError, OSError) as e: errc.print(f"[bold red]Network error:[/] {e}"); sys.exit(1)
    except KeyboardInterrupt: print("\nAborted."); sys.exit(130)
    except Exception as e:
        from lynx_realestate.core.analyzer import SectorMismatchError
        if isinstance(e, SectorMismatchError):
            from rich.panel import Panel
            errc.print()
            errc.print(Panel(
                f"[bold blink red]SECTOR MISMATCH — ANALYSIS BLOCKED[/]\n\n"
                f"[bold red]{e}[/]\n\n"
                f"[bold blink red]This tool is specialized ONLY for Real Estate / REIT companies.[/]\n"
                f"[bold red]Companies outside the real estate sector cannot be analyzed here.[/]",
                title="[bold blink red]!! WRONG SECTOR !![/]",
                border_style="bold red",
                padding=(1, 3),
            ))
            errc.print()
            sys.exit(1)
        errc.print(f"[bold red]Unexpected error:[/] {type(e).__name__}: {e}"); sys.exit(1)


def _cmd_list_cache(con):
    from rich.table import Table; from lynx_realestate.core.storage import list_cached_tickers, get_mode
    tickers = list_cached_tickers()
    if not tickers: con.print(f"[yellow]No cached data ({get_mode()}).[/]"); return
    t = Table(title=f"Cached Data ({get_mode()})", border_style="cyan")
    t.add_column("Ticker", style="bold cyan"); t.add_column("Company"); t.add_column("Stage"); t.add_column("Age", justify="right"); t.add_column("Size", justify="right")
    for info in tickers:
        age = info.get("age_hours"); age_str = f"{age:.1f}h" if age and age < 24 else f"{age/24:.1f}d" if age else "?"
        t.add_row(info["ticker"], info.get("name", ""), info.get("stage", ""), age_str, f"{info.get('size_mb', 0):.1f}MB")
    con.print(t)


def _cmd_drop_cache(con, target):
    from lynx_realestate.core.storage import drop_cache_all, drop_cache_ticker, get_mode
    label = f"({get_mode()})"
    if target.upper() == "ALL":
        count = drop_cache_all(); con.print(f"[bold green]Removed all cached data {label} ({count} tickers).[/]")
    else:
        if drop_cache_ticker(target): con.print(f"[bold green]Removed cached data for {target.upper()} {label}.[/]")
        else: con.print(f"[yellow]No cached data found for '{target.upper()}' {label}.[/]")
