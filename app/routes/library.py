from flask import Blueprint, render_template, request

from app.services.library_service import (
    get_glossary_terms,
    get_library_index,
    get_movement_by_slug,
)

library_bp = Blueprint("library", __name__)


@library_bp.route("/library")
def library_index():
    query = request.args.get("q", "")
    category = request.args.get("category", "")
    pattern = request.args.get("pattern", "")
    movements, categories, patterns = get_library_index(
        query=query,
        category=category,
        pattern=pattern,
    )

    return render_template(
        "pages/library_index.html",
        movements=movements,
        categories=categories,
        patterns=patterns,
        query=query,
        selected_category=category,
        selected_pattern=pattern,
    )


@library_bp.route("/library/movement/<slug>")
def movement_detail(slug: str):
    movement = get_movement_by_slug(slug)
    error_message = None

    if movement is None:
        error_message = f"No se encontro un movimiento con slug '{slug}'."

    return render_template(
        "pages/movement_detail.html",
        movement=movement,
        error_message=error_message,
    )


@library_bp.route("/glossary")
def glossary_index():
    terms = get_glossary_terms()
    return render_template("pages/glossary_index.html", terms=terms)
