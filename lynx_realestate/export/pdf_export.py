"""PDF export (requires weasyprint)."""
from __future__ import annotations
from pathlib import Path
from lynx_realestate.models import AnalysisReport

def export_pdf(report: AnalysisReport, output_path: Path) -> Path:
    try: import weasyprint
    except ImportError: raise RuntimeError("PDF export requires weasyprint: pip install weasyprint")
    from lynx_realestate.export.html_export import export_html
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f: html_path = Path(f.name)
    export_html(report, html_path)
    weasyprint.HTML(string=html_path.read_text(encoding="utf-8")).write_pdf(str(output_path))
    html_path.unlink(missing_ok=True); return output_path
