from datetime import date

from flask import Blueprint, render_template

from app.services.block_service import (
    get_block_for_week,
    get_calendar_overview,
    get_weeks_for_block,
)
from app.services.week_service import (
    get_sessions_for_week,
    get_week_by_start_date,
    get_week_detail_status,
    get_week_navigation,
    get_current_week,
)

weeks_bp = Blueprint("weeks", __name__)


@weeks_bp.route("/calendar")
def calendar():
    return render_template("pages/calendar.html", **get_calendar_overview())


@weeks_bp.route("/week/current")
def current_week():
    requested_date = date.today().isoformat()
    week, is_fallback = get_current_week()
    requested_week_start = week.start_date.isoformat() if week else requested_date
    return _render_week_page(
        requested_week_start=requested_week_start,
        requested_date=requested_date,
        is_fallback=is_fallback,
    )


@weeks_bp.route("/week/<week_start>")
def week_detail(week_start: str):
    return _render_week_page(
        requested_week_start=week_start,
        requested_date=week_start,
        is_fallback=False,
    )


def _render_week_page(
    *,
    requested_week_start: str,
    requested_date: str,
    is_fallback: bool,
):
    week = get_week_by_start_date(requested_week_start)
    sessions = get_sessions_for_week(week) if week is not None else []
    error_message = None
    if week is None:
        error_message = f"No se encontro una semana para {requested_week_start}."

    previous_week_start, next_week_start = get_week_navigation(requested_week_start)
    related_block = get_block_for_week(week)
    block_weeks = get_weeks_for_block(related_block.id) if related_block is not None else []
    week_status = get_week_detail_status(week, sessions)

    return render_template(
        "pages/week_detail.html",
        week=week,
        sessions=sessions,
        requested_date=requested_date,
        requested_week_start=requested_week_start,
        is_fallback=is_fallback,
        error_message=error_message,
        previous_week_start=previous_week_start,
        next_week_start=next_week_start,
        related_block=related_block,
        block_weeks=block_weeks,
        week_status=week_status,
    )
