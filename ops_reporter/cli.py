from __future__ import annotations

import argparse
from pathlib import Path

from .core import load_data
from .report import generate_excel_report, generate_html_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Turn production CSV/XLSX data into a management report.")
    parser.add_argument("input", help="Input CSV or XLSX file")
    parser.add_argument("--output-dir", default="output", help="Directory for generated reports")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    frame = load_data(args.input)
    output_dir = Path(args.output_dir)
    excel = generate_excel_report(frame, output_dir / "operations_report.xlsx")
    html = generate_html_summary(frame, output_dir / "operations_report.html")
    print(f"Created {excel}")
    print(f"Created {html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
