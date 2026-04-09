from datetime import date

from flask import Blueprint, redirect, render_template, request, url_for

from app.services.export_service import build_day_sections
from app.services.week_service import (
    get_adjacent_day_dates,
    get_session_by_date,
    get_week_start_for_day,
)

days_bp = Blueprint("days", __name__)

FALLBACK_SESSION_DATE = "2026-04-08"


@days_bp.route("/today")
def today():
    requested_date = date.today().isoformat()
    return _render_day_page(
        page_title="Hoy",
        page_heading="Hoy",
        page_intro="Sesion del dia cargada desde archivos JSON validados.",
        requested_date=requested_date,
        allow_fallback=True,
        show_back_links=False,
    )


@days_bp.route("/day/<session_date>")
def day_detail(session_date: str):
    return _render_day_page(
        page_title="Detalle del dia",
        page_heading="Detalle del dia",
        page_intro="Sesion seleccionada desde la vista semanal.",
        requested_date=session_date,
        allow_fallback=False,
        show_back_links=True,
    )


@days_bp.route("/day")
def day_lookup():
    session_date = request.args.get("session_date", "").strip()
    if not session_date:
        return redirect(url_for("days.today"))
    return redirect(url_for("days.day_detail", session_date=session_date))


def _render_day_page(
    *,
    page_title: str,
    page_heading: str,
    page_intro: str,
    requested_date: str,
    allow_fallback: bool,
    show_back_links: bool,
):
    session = get_session_by_date(requested_date)
    error_message = None
    is_fallback = False
    fallback_session_date = None

    if session is None and allow_fallback:
        session = get_session_by_date(FALLBACK_SESSION_DATE)
        if session is not None:
            is_fallback = True
            fallback_session_date = FALLBACK_SESSION_DATE
        else:
            error_message = (
                f"No se encontro una sesion para hoy ({requested_date}) "
                f"ni el fallback {FALLBACK_SESSION_DATE}."
            )
    elif session is None:
        error_message = f"No se encontro una sesion para {requested_date}."

    previous_day, next_day = get_adjacent_day_dates(requested_date)

    return render_template(
        "pages/day_detail.html",
        page_title=page_title,
        page_heading=page_heading,
        page_intro=page_intro,
        session=session,
        requested_date=requested_date,
        is_fallback=is_fallback,
        fallback_session_date=fallback_session_date,
        error_message=error_message,
        show_back_links=show_back_links,
        previous_day=previous_day,
        next_day=next_day,
        week_start_for_day=get_week_start_for_day(requested_date),
        day_sections=build_day_sections(session),
    )
