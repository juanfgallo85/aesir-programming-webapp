from datetime import date

from app.models.block import Block
from app.models.cycle import Cycle
from app.models.week import TrainingWeek
from app.services.data_loader import load_all_sessions, load_blocks, load_cycles, load_weeks
from app.services.week_service import get_current_week


def get_all_blocks() -> list[Block]:
    return sorted(load_blocks(), key=lambda block: block.start_date)


def get_all_cycles() -> list[Cycle]:
    return sorted(load_cycles(), key=lambda cycle: cycle.start_date)


def get_cycle_by_id(cycle_id: str) -> Cycle | None:
    return next((cycle for cycle in get_all_cycles() if cycle.id == cycle_id), None)


def get_current_cycle(target_date: date | None = None) -> Cycle | None:
    reference_date = target_date or date.today()
    cycles = get_all_cycles()

    for cycle in cycles:
        if cycle.start_date <= reference_date <= cycle.end_date:
            return cycle

    return cycles[0] if cycles else None


def get_block_by_id(block_id: str) -> Block | None:
    return next((block for block in get_all_blocks() if block.id == block_id), None)


def get_block_for_week(week: TrainingWeek | None) -> Block | None:
    if week is None:
        return None
    return get_block_by_id(week.block_id)


def get_current_block(target_date: date | None = None) -> tuple[Block | None, list[TrainingWeek], bool]:
    reference_date = target_date or date.today()
    blocks = get_all_blocks()
    current_week, week_is_fallback = get_current_week(reference_date)

    if current_week is not None:
        related_block = get_block_for_week(current_week)
        if related_block is not None:
            return related_block, get_weeks_for_block(related_block.id), week_is_fallback

    for block in blocks:
        if block.start_date <= reference_date <= block.end_date:
            return block, get_weeks_for_block(block.id), False

    if blocks:
        fallback_block = blocks[0]
        return fallback_block, get_weeks_for_block(fallback_block.id), True

    return None, [], False


def get_weeks_for_block(block_id: str) -> list[TrainingWeek]:
    weeks = [week for week in load_weeks() if week.block_id == block_id]
    return sorted(weeks, key=lambda week: week.start_date)


def get_block_position(block_id: str) -> tuple[int | None, int]:
    blocks = get_all_blocks()
    for index, block in enumerate(blocks, start=1):
        if block.id == block_id:
            return index, len(blocks)
    return None, len(blocks)


def get_calendar_overview(target_date: date | None = None) -> dict[str, object]:
    reference_date = target_date or date.today()
    blocks = get_all_blocks()
    current_cycle = get_current_cycle(reference_date)
    current_week, _ = get_current_week(reference_date)
    current_block, _, _ = get_current_block(reference_date)
    session_counts = _build_week_session_counts()

    block_cards = []
    weeks_with_sessions = 0

    for index, block in enumerate(blocks, start=1):
        week_summaries = []
        detailed_weeks_count = 0
        for week in get_weeks_for_block(block.id):
            session_count = session_counts.get(week.start_date.isoformat(), 0)
            has_sessions = session_count > 0
            if has_sessions:
                weeks_with_sessions += 1
                detailed_weeks_count += 1
            week_summaries.append(
                {
                    "week": week,
                    "session_count": session_count,
                    "has_sessions": has_sessions,
                    "is_current": current_week is not None
                    and current_week.start_date == week.start_date,
                }
            )

        block_cards.append(
            {
                "block": block,
                "weeks": week_summaries,
                "position": index,
                "is_current": current_block is not None and current_block.id == block.id,
                "detailed_weeks_count": detailed_weeks_count,
            }
        )

    return {
        "cycle": current_cycle,
        "blocks": block_cards,
        "current_block": current_block,
        "current_week": current_week,
        "total_blocks": len(blocks),
        "total_weeks": sum(len(card["weeks"]) for card in block_cards),
        "weeks_with_sessions": weeks_with_sessions,
    }


def build_block_context(block: Block | None) -> dict[str, object]:
    if block is None:
        return {
            "block": None,
            "block_weeks": [],
            "week_summaries": [],
            "cycle": None,
            "block_position": None,
            "block_total": len(get_all_blocks()),
        }

    session_counts = _build_week_session_counts()
    block_weeks = get_weeks_for_block(block.id)
    week_summaries = []
    for week in block_weeks:
        session_count = session_counts.get(week.start_date.isoformat(), 0)
        week_summaries.append(
            {
                "week": week,
                "session_count": session_count,
                "has_sessions": session_count > 0,
            }
        )

    block_position, block_total = get_block_position(block.id)

    return {
        "block": block,
        "block_weeks": block_weeks,
        "week_summaries": week_summaries,
        "cycle": get_cycle_by_id(block.cycle_id),
        "block_position": block_position,
        "block_total": block_total,
    }


def _build_week_session_counts() -> dict[str, int]:
    sessions = load_all_sessions()
    counts: dict[str, int] = {}

    for week in load_weeks():
        counts[week.start_date.isoformat()] = sum(
            1
            for session in sessions
            if week.start_date <= session.session_date <= week.end_date
        )

    return counts
