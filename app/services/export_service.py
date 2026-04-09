from app.models.session import SessionDay
from app.models.week import TrainingWeek
from app.services.block_service import get_block_for_week
from app.services.week_service import (
    get_session_by_date,
    get_sessions_for_week,
    get_week_by_start_date,
    get_week_detail_status,
)


def build_day_sections(session: SessionDay | None) -> list[dict[str, object]]:
    if session is None:
        return []

    section_titles = [
        ("joint_prep", "Movilidad / activacion articular"),
        ("warm_up", "Warm-up"),
        ("skill", "Skill / tecnica"),
        ("strength", "Strength"),
        ("wod", "WOD principal"),
        ("accessory", "Accessory"),
        ("cooldown", "Cooldown"),
        ("competitor_extra", "Extra competidor"),
    ]

    grouped_parts: dict[str, list[object]] = {}
    for part in session.session_parts:
        grouped_parts.setdefault(part.normalized_type, []).append(part)

    return [
        {"key": key, "title": title, "parts": grouped_parts.get(key, [])}
        for key, title in section_titles
        if grouped_parts.get(key)
    ]


def get_day_export_context(session_date: str) -> dict[str, object]:
    session = get_session_by_date(session_date)
    return {
        "session": session,
        "requested_date": session_date,
        "error_message": None if session is not None else f"No se encontro una sesion para {session_date}.",
        "day_sections": build_day_sections(session),
    }


def get_week_export_context(week_start: str) -> dict[str, object]:
    week = get_week_by_start_date(week_start)
    sessions = get_sessions_for_week(week) if week is not None else []
    related_block = get_block_for_week(week)
    week_status = get_week_detail_status(week, sessions)

    return {
        "week": week,
        "sessions": sessions,
        "related_block": related_block,
        "week_status": week_status,
        "requested_week_start": week_start,
        "error_message": None if week is not None else f"No se encontro una semana para {week_start}.",
    }
