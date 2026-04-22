"""Export package for real estate analysis reports."""

from __future__ import annotations
from enum import Enum
from pathlib import Path
from typing import Optional
from lynx_realestate.models import AnalysisReport

class ExportFormat(str, Enum):
    TXT = "txt"; HTML = "html"; PDF = "pdf"

def export_report(report: AnalysisReport, fmt, output_path: Optional[Path] = None) -> Path:
    """Export an analysis report. *fmt* can be an ExportFormat enum or a string ('txt', 'html', 'pdf')."""
    from lynx_realestate.core.storage import get_company_dir
    from datetime import datetime

    # Accept both ExportFormat enum and plain string
    if isinstance(fmt, str):
        fmt = ExportFormat(fmt)

    ext = fmt.value
    if output_path is None:
        output_path = get_company_dir(report.profile.ticker) / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == ExportFormat.TXT:
        from lynx_realestate.export.txt_export import export_txt; return export_txt(report, output_path)
    elif fmt == ExportFormat.HTML:
        from lynx_realestate.export.html_export import export_html; return export_html(report, output_path)
    elif fmt == ExportFormat.PDF:
        from lynx_realestate.export.pdf_export import export_pdf; return export_pdf(report, output_path)
    raise ValueError(f"Unknown format: {fmt}")
