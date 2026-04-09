from datetime import date, timedelta

from app.models.session import SessionDay
from app.models.week import TrainingWeek
from app.services.data_loader import load_all_sessions, load_session_by_date, load_weeks


def get_all_weeks() -> list[TrainingWeek]:
    return sorted(load_weeks(), key=lambda week: week.start_date)


def get_week_for_date(target_date: date) -> TrainingWeek | None:
    for week in get_all_weeks():
        if week.start_date <= target_date <= week.end_date:
            return week
    return None


def get_current_week(target_date: date | None = None) -> tuple[TrainingWeek | None, bool]:
    reference_date = target_date or date.today()
    weeks = get_all_weeks()

    current_week = get_week_for_date(reference_date)
    if current_week is not None:
        return current_week, False

    if weeks:
        return weeks[0], True

    return None, False


def get_week_by_start_date(week_start: str | date) -> TrainingWeek | None:
    try:
        parsed_date = _parse_date(week_start)
    except ValueError:
        return None

    for week in get_all_weeks():
        if week.start_date == parsed_date:
            return week
    return None


def get_week_by_start(week_start: str | date) -> TrainingWeek | None:
    return get_week_by_start_date(week_start)


def get_previous_week(week_start: str | date) -> TrainingWeek | None:
    try:
        parsed_date = _parse_date(week_start)
    except ValueError:
        return None
    return get_week_by_start_date(parsed_date - timedelta(days=7))


def get_next_week(week_start: str | date) -> TrainingWeek | None:
    try:
        parsed_date = _parse_date(week_start)
    except ValueError:
        return None
    return get_week_by_start_date(parsed_date + timedelta(days=7))


def get_session_by_date(session_date: str | date) -> SessionDay | None:
    try:
        return load_session_by_date(session_date)
    except (FileNotFoundError, ValueError):
        return None


def get_week_session_dates(week: TrainingWeek) -> list[date]:
    if week.session_dates:
        return sorted(week.session_dates)

    # Default planning pattern for weeks that only exist at calendar level.
    return [week.start_date + timedelta(days=offset) for offset in range(6)]


def get_sessions_for_week_range(start_date: date, end_date: date) -> list[SessionDay]:
    sessions = [
        session
        for session in load_all_sessions()
        if start_date <= session.session_date <= end_date
    ]
    return sorted(sessions, key=lambda session: session.session_date)


def get_sessions_for_week(week: TrainingWeek) -> list[SessionDay]:
    sessions_by_date: dict[date, SessionDay] = {}

    for session_date in get_week_session_dates(week):
        session = get_session_by_date(session_date)
        if session is not None:
            sessions_by_date[session.session_date] = session

    for session in get_sessions_for_week_range(week.start_date, week.end_date):
        sessions_by_date.setdefault(session.session_date, session)

    return [sessions_by_date[session_date] for session_date in sorted(sessions_by_date)]


def get_week_detail_status(
    week: TrainingWeek | None,
    sessions: list[SessionDay] | None = None,
) -> dict[str, object]:
    if week is None:
        return {
            "label": "not_found",
            "message": "Semana no encontrada.",
            "expected_sessions": 0,
            "loaded_sessions": 0,
            "is_complete": False,
        }

    loaded_sessions = len(sessions) if sessions is not None else len(get_sessions_for_week(week))
    expected_sessions = len(get_week_session_dates(week))

    if loaded_sessions == 0 and expected_sessions == 0:
        return {
            "label": "pending",
            "message": "Semana disponible, detalle de sesiones pendiente.",
            "expected_sessions": expected_sessions,
            "loaded_sessions": loaded_sessions,
            "is_complete": False,
        }

    if expected_sessions and loaded_sessions < expected_sessions:
        return {
            "label": "partial",
            "message": f"Semana parcial: {loaded_sessions} de {expected_sessions} sesiones cargadas.",
            "expected_sessions": expected_sessions,
            "loaded_sessions": loaded_sessions,
            "is_complete": False,
        }

    return {
        "label": "complete",
        "message": f"Semana completa: {loaded_sessions} sesiones cargadas.",
        "expected_sessions": expected_sessions,
        "loaded_sessions": loaded_sessions,
        "is_complete": loaded_sessions > 0,
    }


def get_sessions_for_current_week(
    target_date: date | None = None,
) -> tuple[TrainingWeek | None, list[SessionDay], bool]:
    week, is_fallback = get_current_week(target_date)

    if week is None:
        return None, [], is_fallback

    return week, get_sessions_for_week(week), is_fallback


def get_week_navigation(week_start: str | date) -> tuple[str, str]:
    try:
        parsed_date = _parse_date(week_start)
    except ValueError:
        parsed_date = date.today()
    previous_week = get_previous_week(parsed_date)
    next_week = get_next_week(parsed_date)
    previous_week_start = (
        previous_week.start_date.isoformat()
        if previous_week is not None
        else (parsed_date - timedelta(days=7)).isoformat()
    )
    next_week_start = (
        next_week.start_date.isoformat()
        if next_week is not None
        else (parsed_date + timedelta(days=7)).isoformat()
    )
    return previous_week_start, next_week_start


def get_week_start_for_day(target_date: str | date) -> str:
    try:
        parsed_date = _parse_date(target_date)
    except ValueError:
        parsed_date = date.today()
    week = get_week_for_date(parsed_date)
    if week is not None:
        return week.start_date.isoformat()

    current_week, _ = get_current_week()
    if current_week is not None:
        return current_week.start_date.isoformat()

    monday = parsed_date - timedelta(days=parsed_date.weekday())
    return monday.isoformat()


def get_adjacent_day_dates(target_date: str | date) -> tuple[str, str]:
    try:
        parsed_date = _parse_date(target_date)
    except ValueError:
        parsed_date = date.today()
    previous_day = (parsed_date - timedelta(days=1)).isoformat()
    next_day = (parsed_date + timedelta(days=1)).isoformat()
    return previous_day, next_day


def _parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)
