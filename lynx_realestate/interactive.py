"""Interactive prompt-based mode for lynx-realestate."""

from __future__ import annotations

try:
    import readline as _readline
except ImportError:
    pass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from lynx_investor_core.pager import console_pager, paged_print
from lynx_realestate.core.analyzer import run_progressive_analysis
from lynx_realestate.core.news import download_article
from lynx_realestate.core.reports import download_filing
from lynx_realestate.display import display_full_report, display_report_stage
from lynx_realestate.models import AnalysisReport

console = Console()

BANNER = "\n[bold blue]  L Y N X   Real Estate Analysis[/]\n[dim]    Real Estate Sector Analysis[/]\n"

MENU = """
[bold cyan]Analysis:[/]
  [bold]analyze[/] <TICKER|ISIN|NAME>   Analyze (uses cache)
  [bold]refresh[/] <TICKER|ISIN|NAME>   Force fresh data
  [bold]search[/] <query>               Search for a company

[bold cyan]View data:[/]
  [bold]metrics[/]                      Show last analysis
  [bold]filings[/]                      List filings
  [bold]download-filing[/] <N>          Download filing #N
  [bold]news[/]                         Show news
  [bold]download-news[/] <N>            Download article #N
  [bold]summary[/]                      Quality + shares + market intel
  [bold]open-news[/] <N>                Open news article #N in browser
  [bold]export[/] <txt|html|pdf>        Export report

[bold cyan]Cache:[/]
  [bold]cache[/]                        List cached tickers
  [bold]drop-cache[/] <TICKER|all>      Remove cached data

[bold cyan]Learn:[/]
  [bold]explain[/] <metric>             Explain a metric
  [bold]explain-all[/]                  List all metrics
  [bold]explain-section[/] <section>    Explain an analysis section
  [bold]explain-conclusion[/] [category]   Explain conclusion methodology

[bold cyan]Other:[/]
  [bold]about[/] / [bold]help[/] / [bold]quit[/]
"""


def run_interactive():
    from lynx_realestate import get_logo_ascii
    from lynx_realestate.core.storage import get_mode, is_testing
    logo = get_logo_ascii()
    console.print(f"[bold green]{logo}[/]")
    console.print(BANNER)
    mode_panel = "[bold yellow]TESTING MODE[/]\nData in data_test/" if is_testing() else "[bold green]PRODUCTION MODE[/]\nData in data/"
    console.print(Panel(mode_panel, border_style="yellow" if is_testing() else "green"))
    console.print(Panel(MENU, border_style="cyan", title="[bold]Interactive Mode[/]"))

    current_report: AnalysisReport | None = None

    while True:
        prompt_color = "yellow" if is_testing() else "cyan"
        try:
            console.print(f"\n[bold {prompt_color}]lynx-realestate[/] ", end="")
            raw = input().strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/]"); break
        if not raw: continue

        parts = raw.split(maxsplit=1)
        cmd, arg = parts[0].lower(), (parts[1].strip() if len(parts) > 1 else "")

        if cmd in ("quit", "exit", "q"):
            console.print("[dim]Goodbye![/]"); break
        elif cmd == "help":
            console.print(MENU)
        elif cmd == "about":
            from lynx_realestate import get_about_text; from rich.panel import Panel as P
            a = get_about_text()
            console.print(P(f"[bold blue]{a['name']} v{a['version']}[/]\n[dim]Part of {a['suite']} v{a['suite_version']}[/]\n\n[bold]By:[/] {a['author']}\n\n[dim]{a['description']}[/]",
                            title="[bold]About[/]", border_style="blue"))
        elif cmd == "explain":
            from lynx_realestate.metrics.explanations import get_explanation
            if not arg: console.print("[yellow]Usage: explain <metric_key>[/]"); continue
            exp = get_explanation(arg.lower().replace("-", "_"))
            if exp:
                console.print(Panel(f"[bold]{exp.full_name}[/]\n\n{exp.description}\n\n[bold cyan]Why:[/]\n{exp.why_used}\n\n[bold cyan]Formula:[/]\n{exp.formula}",
                                    title=f"[bold]{exp.key}[/]", border_style="cyan"))
            else: console.print(f"[red]Unknown metric '{arg}'.[/]")
        elif cmd == "explain-all":
            from lynx_realestate.metrics.explanations import list_metrics
            t = Table(title="Available Metrics", border_style="cyan")
            t.add_column("Key", style="bold cyan"); t.add_column("Name"); t.add_column("Category")
            for m in list_metrics(): t.add_row(m.key, m.full_name, m.category)
            paged_print(console, t)
        elif cmd == "search":
            if not arg:
                try: arg = Prompt.ask("[bold]Search query[/]")
                except (EOFError, KeyboardInterrupt): continue
            from lynx_realestate.core.ticker import search_companies, display_search_results
            results = search_companies(arg, max_results=10)
            if results: display_search_results(results)
            else: console.print(f"[yellow]No results for '{arg}'.[/]")
        elif cmd in ("analyze", "refresh"):
            force = cmd == "refresh" or is_testing()
            if not arg:
                try: arg = Prompt.ask("[bold]Enter ticker or company name[/]")
                except (EOFError, KeyboardInterrupt): continue
            if not arg: continue
            try:
                current_report = run_progressive_analysis(identifier=arg, refresh=force, on_progress=display_report_stage)
            except ValueError as e: console.print(f"[bold red]Error:[/] {e}")
            except (ConnectionError, TimeoutError, OSError) as e: console.print(f"[bold red]Network error:[/] {e}")
            except KeyboardInterrupt: console.print("[dim]Cancelled.[/]")
            except Exception as e:
                from lynx_realestate.core.analyzer import SectorMismatchError
                if isinstance(e, SectorMismatchError):
                    console.print()
                    console.print(Panel(
                        f"[bold blink red]SECTOR MISMATCH — ANALYSIS BLOCKED[/]\n\n"
                        f"[bold red]{e}[/]\n\n"
                        f"[bold blink red]This tool is specialized ONLY for the Real Estate sector.[/]",
                        title="[bold blink red]!! WRONG SECTOR !![/]",
                        border_style="bold red", padding=(1, 3),
                    ))
                    console.print()
                else:
                    console.print(f"[bold red]Error:[/] {type(e).__name__}: {e}")
        elif cmd == "metrics":
            if current_report:
                with console_pager(console):
                    display_full_report(current_report)
            else: console.print("[yellow]No analysis loaded.[/]")
        elif cmd == "summary":
            if current_report:
                from lynx_realestate.display import _display_energy_quality, _display_share_structure, _display_intrinsic_value, _display_market_intelligence
                _display_energy_quality(current_report); _display_share_structure(current_report)
                _display_intrinsic_value(current_report); _display_market_intelligence(current_report)
            else: console.print("[yellow]No analysis loaded.[/]")
        elif cmd == "filings":
            if current_report and current_report.filings:
                from lynx_realestate.display import _display_filings; _display_filings(current_report)
            else: console.print("[yellow]No filings available.[/]")
        elif cmd == "news":
            if current_report and current_report.news:
                from lynx_realestate.display import _display_news; _display_news(current_report)
            else: console.print("[yellow]No news available.[/]")
        elif cmd == "download-filing":
            if not current_report or not current_report.filings: console.print("[yellow]No filings.[/]"); continue
            try:
                idx = int(arg) - 1 if arg else IntPrompt.ask("Filing number") - 1
                if 0 <= idx < len(current_report.filings):
                    f = current_report.filings[idx]; path = download_filing(current_report.profile.ticker, f)
                    console.print(f"[green]Saved to:[/] {path}" if path else "[red]Download failed.[/]")
            except (ValueError, TypeError, EOFError, KeyboardInterrupt): pass
        elif cmd == "download-news":
            if not current_report or not current_report.news: console.print("[yellow]No news.[/]"); continue
            try:
                idx = int(arg) - 1 if arg else IntPrompt.ask("Article number") - 1
                if 0 <= idx < len(current_report.news):
                    path = download_article(current_report.profile.ticker, current_report.news[idx])
                    console.print(f"[green]Saved to:[/] {path}" if path else "[red]Download failed.[/]")
            except (ValueError, TypeError, EOFError, KeyboardInterrupt): pass
        elif cmd == "export":
            if not current_report: console.print("[yellow]No analysis loaded.[/]"); continue
            fmt = arg.lower() if arg else ""
            if fmt not in ("txt", "html", "pdf"): console.print("[yellow]Usage: export <txt|html|pdf>[/]"); continue
            try:
                from lynx_realestate.export import ExportFormat, export_report
                path = export_report(current_report, ExportFormat(fmt)); console.print(f"[bold green]Exported to:[/] {path}")
            except Exception as e: console.print(f"[bold red]Error:[/] {e}")
        elif cmd == "cache":
            from lynx_realestate.core.storage import list_cached_tickers, get_mode
            tickers = list_cached_tickers()
            if not tickers: console.print(f"[yellow]No cached data ({get_mode()}).[/]"); continue
            t = Table(title=f"Cached Data ({get_mode()})", border_style="cyan")
            t.add_column("Ticker", style="bold cyan"); t.add_column("Company"); t.add_column("Stage"); t.add_column("Age")
            for info in tickers:
                age = info.get("age_hours"); age_str = f"{age:.1f}h" if age and age < 24 else f"{age/24:.1f}d" if age else "?"
                t.add_row(info["ticker"], info.get("name", ""), info.get("stage", ""), age_str)
            console.print(t)
        elif cmd == "drop-cache":
            if not arg:
                try: arg = Prompt.ask("[bold]Ticker to drop (or 'all')[/]")
                except (EOFError, KeyboardInterrupt): continue
            from lynx_realestate.core.storage import drop_cache_all, drop_cache_ticker, get_mode
            if arg.lower() == "all":
                count = drop_cache_all(); console.print(f"[bold green]Removed all ({count} tickers).[/]")
            elif drop_cache_ticker(arg): console.print(f"[bold green]Removed {arg.upper()}.[/]")
            else: console.print(f"[yellow]No data for '{arg.upper()}'.[/]")
        elif cmd == "explain-section":
            from lynx_realestate.metrics.explanations import get_section_explanation, SECTION_EXPLANATIONS
            if not arg:
                console.print("[bold]Available sections:[/]")
                for key, sec in SECTION_EXPLANATIONS.items():
                    console.print(f"  [bold cyan]{key:20s}[/] {sec['title']}")
            else:
                sec = get_section_explanation(arg.lower().replace(" ", "_").replace("-", "_"))
                if sec:
                    console.print(Panel(f"[bold]{sec['title']}[/]\n\n{sec['description']}", title=f"[bold]{sec['title']}[/]", border_style="cyan"))
                else:
                    console.print(f"[red]Unknown section '{arg}'.[/]")
        elif cmd == "explain-conclusion":
            from lynx_realestate.metrics.explanations import get_conclusion_explanation, CONCLUSION_METHODOLOGY
            key = arg.lower().replace(" ", "_").replace("-", "_") if arg else "overall"
            ce = get_conclusion_explanation(key)
            if ce:
                console.print(Panel(f"[bold]{ce['title']}[/]\n\n{ce['description']}", title=f"[bold]{ce['title']}[/]", border_style="cyan"))
            else:
                console.print("[bold]Available categories:[/]")
                for k, v in CONCLUSION_METHODOLOGY.items():
                    console.print(f"  [bold cyan]{k:20s}[/] {v['title']}")
        elif cmd == "open-news":
            if not current_report or not current_report.news: console.print("[yellow]No news.[/]"); continue
            try:
                idx = int(arg) - 1 if arg else IntPrompt.ask("Article number") - 1
                if 0 <= idx < len(current_report.news):
                    art = current_report.news[idx]
                    if art.url:
                        from lynx_investor_core.urlsafe import safe_webbrowser_open; _ok = safe_webbrowser_open(art.url)
                        console.print(f"[green]Opened in browser:[/] {art.title[:60]}")
                    else:
                        console.print("[red]No URL available.[/]")
            except (ValueError, TypeError, EOFError, KeyboardInterrupt): pass
        elif cmd == "matrix":
            from lynx_realestate.easter import rich_matrix; rich_matrix(console)
        elif cmd == "fortune":
            from lynx_realestate.easter import rich_fortune; rich_fortune(console)
        elif cmd == "rocket":
            from lynx_realestate.easter import rich_rocket; rich_rocket(console)
        elif cmd == "lynx":
            from lynx_realestate.easter import rich_lynx; rich_lynx(console)
        else:
            console.print(f"[dim]Unknown command '{cmd}'. Trying as ticker...[/]")
            try:
                current_report = run_progressive_analysis(identifier=raw, refresh=is_testing(), on_progress=display_report_stage)
            except Exception as e:
                from lynx_realestate.core.analyzer import SectorMismatchError
                if isinstance(e, SectorMismatchError):
                    console.print(Panel(
                        f"[bold blink red]SECTOR MISMATCH[/]\n\n[bold red]{e}[/]",
                        title="[bold blink red]!! WRONG SECTOR !![/]",
                        border_style="bold red", padding=(1, 2),
                    ))
                else:
                    console.print(f"[red]{e}[/]\n[dim]Type 'help' for commands.[/]")
