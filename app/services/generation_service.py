import json
from copy import deepcopy
from datetime import date, datetime, timedelta
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import Any

from app.models.block import Block
from app.models.session import SessionDay
from app.models.week import TrainingWeek
from app.services.data_loader import (
    SESSIONS_DIR,
    load_block_rules_config,
    load_blocks,
    load_day_families_config,
    load_json_file,
    load_session_templates_config,
    load_weeks,
)
from app.services.week_service import get_week_session_dates


def parse_yes_no(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"yes", "y", "true", "1"}:
        return True
    if normalized in {"no", "n", "false", "0"}:
        return False
    raise ValueError("Expected yes or no")


@lru_cache(maxsize=1)
def load_generation_catalog() -> dict[str, Any]:
    return {
        "day_families": load_day_families_config(),
        "block_rules": load_block_rules_config(),
        "session_templates": load_session_templates_config(),
    }


def generate_sessions_for_range(
    *,
    start_date: date,
    end_date: date,
    overwrite_draft: bool,
    dry_run: bool,
    generated_by: str,
    refresh_mode: bool = False,
) -> dict[str, Any]:
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")

    blocks_by_id = {block.id: block for block in load_blocks()}
    weeks = [
        week
        for week in sorted(load_weeks(), key=lambda item: item.start_date)
        if week_overlaps_range(week, start_date, end_date)
    ]

    summary = {
        "weeks_scanned": len(weeks),
        "dates_considered": 0,
        "created": 0,
        "regenerated": 0,
        "skipped_protected": 0,
        "skipped_draft": 0,
        "dry_run": dry_run,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }

    for week in weeks:
        block = blocks_by_id.get(week.block_id)
        if block is None:
            raise ValueError(f"Block not found for week {week.id}: {week.block_id}")

        for session_date in get_week_session_dates(week):
            if not (start_date <= session_date <= end_date):
                continue

            summary["dates_considered"] += 1
            session_path = session_file_path(session_date)
            existing_session = load_existing_session(session_path)

            if existing_session is not None and existing_session.is_protected_status:
                summary["skipped_protected"] += 1
                continue

            if existing_session is not None and existing_session.status == "draft" and not overwrite_draft:
                summary["skipped_draft"] += 1
                continue

            payload = build_generated_session_payload(
                week=week,
                block=block,
                session_date=session_date,
                generated_by=generated_by,
                refresh_mode=refresh_mode,
            )

            action_key = "regenerated" if existing_session is not None else "created"
            summary[action_key] += 1

            if dry_run:
                continue

            write_session_payload(session_path, payload)

    return summary


def week_overlaps_range(week: TrainingWeek, start_date: date, end_date: date) -> bool:
    return not (week.end_date < start_date or week.start_date > end_date)


def session_file_path(session_date: date) -> Path:
    return SESSIONS_DIR / f"{session_date.isoformat()}.json"


def load_existing_session(path: Path) -> SessionDay | None:
    if not path.exists():
        return None
    payload = load_json_file(path)
    return SessionDay.model_validate(payload)


def write_session_payload(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
        file.write("\n")


def build_generated_session_payload(
    *,
    week: TrainingWeek,
    block: Block,
    session_date: date,
    generated_by: str,
    refresh_mode: bool,
) -> dict[str, Any]:
    catalog = load_generation_catalog()
    family_id, family_config, block_rule = resolve_day_family(
        catalog=catalog,
        week=week,
        block=block,
        session_date=session_date,
    )

    generated_at = datetime.now().replace(microsecond=0).isoformat()
    context = {
        "block_title": block.title,
        "block_objective": block_rule.get("goal_line") or block.objective,
        "week_focus": week.weekly_focus,
        "family_label": family_config["label"],
        "session_date": session_date.isoformat(),
    }

    session_parts = build_session_parts(
        catalog=catalog,
        family_id=family_id,
        family_config=family_config,
        block=block,
        block_rule=block_rule,
        week=week,
        session_date=session_date,
        context=context,
    )

    wod_part = next(
        (part for part in session_parts if part["part_type"] == "wod"),
        session_parts[-1],
    )

    payload = {
        "session_date": session_date.isoformat(),
        "status": "draft",
        "generated_by": generated_by,
        "generated_at": generated_at,
        "review_notes": (
            "Auto-generated draft refreshed. Revisar cargas, flujo, logistica y clima antes de aprobar."
            if refresh_mode
            else "Auto-generated draft. Revisar cargas, flujo, logistica y clima antes de aprobar."
        ),
        "is_auto_generated": True,
        "title": build_session_title(
            family_config=family_config,
            session_date=session_date,
            block=block,
            wod_part=wod_part,
        ),
        "goal": choose_text(
            family_config.get("goal_templates", []),
            context,
            "goal",
            family_id,
            session_date.isoformat(),
        )
        or f"{block.objective} Sesion de {family_config['label'].lower()} alineada con el foco semanal.",
        "coach_summary": choose_text(
            family_config.get("coach_summary_options", []),
            context,
            "coach_summary",
            family_id,
            session_date.isoformat(),
        )
        or "Draft autogenerado. Revisar cargas, logistica y criterio tecnico antes de aprobar.",
        "public_summary": choose_text(
            family_config.get("public_summary_options", []),
            context,
            "public_summary",
            family_id,
            session_date.isoformat(),
        )
        or f"Sesion de {family_config['label'].lower()} con una pieza principal clara y escalable.",
        "family_type": family_config["family_type"],
        "dominant_stimulus": choose_value(
            family_config.get("dominant_stimulus_options", []),
            "stimulus",
            family_id,
            session_date.isoformat(),
        ),
        "dominant_pattern": choose_value(
            family_config.get("dominant_pattern_options", []),
            "pattern",
            family_id,
            session_date.isoformat(),
        ),
        "technical_level": build_technical_level(family_config, week),
        "fatigue_level": build_fatigue_level(family_config, week),
        "operational_color": build_operational_color(family_config, week),
        "equipment_alert": choose_text(
            family_config.get("equipment_alert_options", []),
            context,
            "equipment_alert",
            family_id,
            session_date.isoformat(),
        )
        or family_config["equipment_alert"],
        "session_parts": session_parts,
        "scaling_options": build_scaling_options(
            catalog=catalog,
            family_id=family_id,
            family_config=family_config,
            block_rule=block_rule,
            context=context,
        ),
        "coach_notes": build_coach_notes(
            catalog=catalog,
            family_id=family_id,
            family_config=family_config,
            block_rule=block_rule,
            context=context,
            session_date=session_date,
        ),
    }

    validated = SessionDay.model_validate(payload)
    return validated.model_dump(mode="json")


def resolve_day_family(
    *,
    catalog: dict[str, Any],
    week: TrainingWeek,
    block: Block,
    session_date: date,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    block_rules = catalog["block_rules"]
    day_families = catalog["day_families"]
    rule = block_rules.get("block_rules", {}).get(block.id, {})
    rotation = rule.get("rotation") or block_rules.get("default_rotation", [])
    if not rotation:
        raise ValueError("No default_rotation configured for generator")

    weekday_index = max(0, min(session_date.weekday(), 5))
    family_id = rotation[weekday_index % len(rotation)]
    family_config = day_families[family_id]
    return family_id, family_config, rule


def build_session_parts(
    *,
    catalog: dict[str, Any],
    family_id: str,
    family_config: dict[str, Any],
    block: Block,
    block_rule: dict[str, Any],
    week: TrainingWeek,
    session_date: date,
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    session_parts: list[dict[str, Any]] = []
    templates = catalog["session_templates"]

    for part_type in family_config.get("part_sequence", []):
        if part_type == "competitor_extra" and not should_include_competitor_extra(
            family_id=family_id,
            week=week,
            block=block,
            session_date=session_date,
        ):
            continue

        template_id = select_template_id(
            family_id=family_id,
            family_config=family_config,
            block_rule=block_rule,
            part_type=part_type,
            session_date=session_date,
        )
        if template_id is None:
            continue

        template_group = templates.get(part_type, {})
        template = template_group.get(template_id)
        if template is None:
            raise ValueError(f"Missing template {part_type}:{template_id}")

        rendered = render_tokens(deepcopy(template), context)
        rendered["part_type"] = part_type
        session_parts.append(rendered)

    if not session_parts:
        raise ValueError(f"Could not build session parts for {family_id} on {session_date}")

    return session_parts


def select_template_id(
    *,
    family_id: str,
    family_config: dict[str, Any],
    block_rule: dict[str, Any],
    part_type: str,
    session_date: date,
) -> str | None:
    pool_key = f"{part_type}_pool"
    family_override = block_rule.get("family_overrides", {}).get(family_id, {})
    pool = family_override.get(pool_key, family_config.get(pool_key, []))
    if not pool:
        return None
    return choose_value(pool, family_id, part_type, session_date.isoformat())


def build_scaling_options(
    *,
    catalog: dict[str, Any],
    family_id: str,
    family_config: dict[str, Any],
    block_rule: dict[str, Any],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    family_override = block_rule.get("family_overrides", {}).get(family_id, {})
    profile_id = family_override.get("scaling_profile", family_config.get("scaling_profile", "standard"))
    profiles = catalog["session_templates"].get("scaling_profiles", {})
    profile = profiles.get(profile_id) or profiles.get("standard", [])
    return render_tokens(deepcopy(profile), context)


def build_coach_notes(
    *,
    catalog: dict[str, Any],
    family_id: str,
    family_config: dict[str, Any],
    block_rule: dict[str, Any],
    context: dict[str, Any],
    session_date: date,
) -> list[dict[str, Any]]:
    family_override = block_rule.get("family_overrides", {}).get(family_id, {})
    note_ids = family_override.get("coach_note_pool", family_config.get("coach_note_pool", []))
    note_templates = catalog["session_templates"].get("coach_notes", {})

    if not note_ids:
        return [{"title": "Review", "content": "Draft autogenerado. Revisar logistica y escalados antes de aprobar."}]

    selected_ids = choose_many(note_ids, 2, family_id, session_date.isoformat(), "coach_notes")
    notes = [render_tokens(deepcopy(note_templates[note_id]), context) for note_id in selected_ids]

    block_note = block_rule.get("block_note")
    if block_note:
        notes.append(
            {
                "title": "Bloque",
                "content": render_tokens(block_note, context),
            }
        )

    return notes


def should_include_competitor_extra(
    *,
    family_id: str,
    week: TrainingWeek,
    block: Block,
    session_date: date,
) -> bool:
    if week.deload_flag:
        return False

    if block.block_type in {"performance", "skill", "power"} and session_date.weekday() >= 3:
        return True

    return family_id in {"mixed_modal_builder", "oly_technique_day"} and week.test_week_flag


def build_session_title(
    *,
    family_config: dict[str, Any],
    session_date: date,
    block: Block,
    wod_part: dict[str, Any],
) -> str:
    stems = family_config.get("session_title_stems", [family_config["label"]])
    stem = choose_value(stems, block.id, session_date.isoformat(), "title")
    if wod_part.get("title"):
        return f"{stem}: {wod_part['title']}"
    return f"{stem} | {block.title}"


def build_technical_level(family_config: dict[str, Any], week: TrainingWeek) -> str:
    if week.deload_flag:
        return family_config.get("deload_technical_level", family_config["technical_level"])
    return family_config["technical_level"]


def build_fatigue_level(family_config: dict[str, Any], week: TrainingWeek) -> str:
    if week.deload_flag:
        return family_config.get("deload_fatigue_level", "low-moderate")
    if week.test_week_flag:
        return family_config.get("test_week_fatigue_level", family_config["fatigue_level"])
    return family_config["fatigue_level"]


def build_operational_color(family_config: dict[str, Any], week: TrainingWeek) -> str:
    if week.deload_flag:
        return "green"
    if week.test_week_flag:
        return family_config.get("test_week_operational_color", "amber")
    return family_config["operational_color"]


def choose_many(values: list[str], amount: int, *seed_parts: str) -> list[str]:
    ordered_values = list(values)
    selected: list[str] = []
    for offset in range(min(amount, len(ordered_values))):
        candidate = choose_value(ordered_values, *seed_parts, str(offset))
        if candidate not in selected:
            selected.append(candidate)
        else:
            for value in ordered_values:
                if value not in selected:
                    selected.append(value)
                    break
    return selected


def choose_text(values: list[str], context: dict[str, Any], *seed_parts: str) -> str:
    choice = choose_value(values, *seed_parts)
    return render_tokens(choice, context) if choice else ""


def choose_value(values: list[Any], *seed_parts: str) -> Any:
    if not values:
        return None
    index = stable_index(len(values), *seed_parts)
    return values[index]


def stable_index(length: int, *seed_parts: str) -> int:
    seed = "|".join(seed_parts)
    digest = sha256(seed.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % length


def render_tokens(value: Any, context: dict[str, Any]) -> Any:
    if isinstance(value, str):
        rendered = value
        for key, replacement in context.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(replacement))
        return rendered
    if isinstance(value, list):
        return [render_tokens(item, context) for item in value]
    if isinstance(value, dict):
        return {key: render_tokens(item, context) for key, item in value.items()}
    return value
