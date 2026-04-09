from flask import Blueprint, render_template

from app.services.export_service import get_day_export_context, get_week_export_context

exports_bp = Blueprint("exports", __name__)


@exports_bp.route("/export/day/<session_date>")
def export_day(session_date: str):
    return render_template(
        "pages/export_day.html",
        hide_nav=True,
        export_mode=True,
        **get_day_export_context(session_date),
    )


@exports_bp.route("/export/week/<week_start>")
def export_week(week_start: str):
    return render_template(
        "pages/export_week.html",
        hide_nav=True,
        export_mode=True,
        **get_week_export_context(week_start),
    )
