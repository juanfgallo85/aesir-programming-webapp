from app.models.glossary import GlossaryTerm
from app.models.movement import Movement
from app.services.data_loader import load_glossary, load_movements


def get_library_index(
    *,
    query: str = "",
    category: str = "",
    pattern: str = "",
) -> tuple[list[Movement], list[str], list[str]]:
    movements = sorted(load_movements(), key=lambda movement: movement.name)
    categories = sorted({movement.category for movement in movements})
    patterns = sorted({movement.dominant_pattern for movement in movements})

    query_text = query.strip().lower()
    category_text = category.strip().lower()
    pattern_text = pattern.strip().lower()

    filtered_movements = []
    for movement in movements:
        searchable_text = " ".join(
            [
                movement.name,
                movement.slug,
                movement.category,
                movement.dominant_pattern,
                movement.description or "",
                " ".join(movement.basic_cues),
                " ".join(movement.common_errors),
                " ".join(movement.scaling_notes),
            ]
        ).lower()

        if query_text and query_text not in searchable_text:
            continue

        if category_text and movement.category.lower() != category_text:
            continue

        if pattern_text and movement.dominant_pattern.lower() != pattern_text:
            continue

        filtered_movements.append(movement)

    return filtered_movements, categories, patterns


def get_movement_by_slug(slug: str) -> Movement | None:
    slug_text = slug.strip().lower()
    for movement in load_movements():
        if movement.slug.lower() == slug_text:
            return movement
    return None


def get_glossary_terms() -> list[GlossaryTerm]:
    return sorted(load_glossary(), key=lambda term: term.term.lower())
