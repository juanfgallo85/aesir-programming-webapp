from datetime import date

from flask import Blueprint, render_template

from app.services.block_service import build_block_context, get_block_by_id, get_current_block

blocks_bp = Blueprint("blocks", __name__)


@blocks_bp.route("/block/current")
def current_block():
    requested_date = date.today().isoformat()
    block, _, is_fallback = get_current_block()
    return _render_block_page(
        block=block,
        requested_label=requested_date,
        is_fallback=is_fallback,
    )


@blocks_bp.route("/block/<block_id>")
def block_detail(block_id: str):
    return _render_block_page(
        block=get_block_by_id(block_id),
        requested_label=block_id,
        is_fallback=False,
    )


def _render_block_page(*, block, requested_label: str, is_fallback: bool):
    context = build_block_context(block)
    error_message = None

    if context["block"] is None:
        error_message = f"No se encontro un bloque disponible para {requested_label}."

    return render_template(
        "pages/block_detail.html",
        requested_label=requested_label,
        is_fallback=is_fallback,
        error_message=error_message,
        **context,
    )
