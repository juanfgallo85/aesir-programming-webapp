from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.services.data_loader import (  # noqa: E402
    load_all_sessions,
    load_athlete_profiles,
    load_block_rules_config,
    load_blocks,
    load_cycles,
    load_day_families_config,
    load_glossary,
    load_gym_profile,
    load_movements,
    load_session_by_date,
    load_session_templates_config,
    load_weeks,
)


def main():
    gym_profile = load_gym_profile()
    athlete_profiles = load_athlete_profiles()
    movements = load_movements()
    glossary = load_glossary()
    cycles = load_cycles()
    blocks = load_blocks()
    weeks = load_weeks()
    day_families = load_day_families_config()
    block_rules = load_block_rules_config()
    session_templates = load_session_templates_config()
    sessions = load_all_sessions()
    session = load_session_by_date("2026-04-08")
    explicit_detailed_weeks = sum(1 for week in weeks if week.session_dates)
    weeks_with_loaded_sessions = sum(
        1
        for week in weeks
        if any(week.start_date <= item.session_date <= week.end_date for item in sessions)
    )
    draft_sessions = sum(1 for item in sessions if item.status == "draft")
    reviewed_sessions = sum(1 for item in sessions if item.status == "reviewed")
    final_sessions = sum(1 for item in sessions if item.status == "final")
    locked_sessions = sum(1 for item in sessions if item.status == "locked")

    print(f"OK gym profile: {gym_profile.name}")
    print(f"OK athlete profiles: {len(athlete_profiles)}")
    print(f"OK movements: {len(movements)}")
    print(f"OK glossary terms: {len(glossary)}")
    print(f"OK cycles: {len(cycles)}")
    print(f"OK blocks: {len(blocks)}")
    print(f"OK weeks: {len(weeks)}")
    print(f"OK explicit detailed weeks: {explicit_detailed_weeks}")
    print(f"OK weeks with loaded sessions: {weeks_with_loaded_sessions}")
    print(f"OK day families: {len(day_families)}")
    print(f"OK block rules: {len(block_rules.get('block_rules', {}))}")
    print(f"OK session templates: {len(session_templates)} sections")
    print(f"OK all sessions: {len(sessions)}")
    print(f"OK session states: draft={draft_sessions}, reviewed={reviewed_sessions}, final={final_sessions}, locked={locked_sessions}")
    print(f"OK session by date: {session.session_date} -> {session.title}")


if __name__ == "__main__":
    main()
