from argparse import ArgumentParser
from datetime import date, timedelta
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.services.generation_service import generate_sessions_for_range, parse_yes_no  # noqa: E402


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Refresh upcoming draft sessions without touching protected content.",
    )
    parser.add_argument("--start-date", default=date.today().isoformat())
    parser.add_argument("--weeks-ahead", type=int, default=6)
    parser.add_argument("--overwrite-draft", default="yes")
    parser.add_argument("--dry-run", default="no")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    start_date = date.fromisoformat(args.start_date)
    end_date = start_date + timedelta(days=max(args.weeks_ahead, 1) * 7 - 1)
    overwrite_draft = parse_yes_no(args.overwrite_draft)
    dry_run = parse_yes_no(args.dry_run)

    summary = generate_sessions_for_range(
        start_date=start_date,
        end_date=end_date,
        overwrite_draft=overwrite_draft,
        dry_run=dry_run,
        generated_by="refresh_future_weeks.py",
        refresh_mode=True,
    )

    print("Refresh future weeks summary")
    print(f"- range: {summary['start_date']} -> {summary['end_date']}")
    print(f"- weeks scanned: {summary['weeks_scanned']}")
    print(f"- dates considered: {summary['dates_considered']}")
    print(f"- created: {summary['created']}")
    print(f"- regenerated drafts: {summary['regenerated']}")
    print(f"- skipped protected: {summary['skipped_protected']}")
    print(f"- skipped draft: {summary['skipped_draft']}")
    print(f"- dry run: {summary['dry_run']}")


if __name__ == "__main__":
    main()
