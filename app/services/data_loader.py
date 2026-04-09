import json
from datetime import date
from pathlib import Path
from typing import Any, TypeVar

from pydantic import ValidationError

from app.models.block import Block
from app.models.cycle import Cycle
from app.models.glossary import GlossaryTerm
from app.models.gym import AthleteProfileType, GymProfile
from app.models.movement import Movement
from app.models.session import SessionDay
from app.models.week import TrainingWeek

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
SESSIONS_DIR = DATA_DIR / "programming" / "sessions"
GENERATOR_DIR = DATA_DIR / "programming" / "generator"

ModelT = TypeVar("ModelT")


def load_json_file(path: str | Path) -> Any:
    resolved_path = _resolve_path(path)

    if not resolved_path.exists():
        raise FileNotFoundError(f"JSON file not found: {resolved_path}")

    try:
        with resolved_path.open("r", encoding="utf-8-sig") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in {resolved_path} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def load_gym_profile() -> GymProfile:
    path = DATA_DIR / "gym" / "gym_profile.json"
    return _validate_item(load_json_file(path), GymProfile, path)


def load_athlete_profiles() -> list[AthleteProfileType]:
    path = DATA_DIR / "gym" / "athlete_profiles.json"
    return _validate_list(load_json_file(path), AthleteProfileType, path)


def load_movements() -> list[Movement]:
    path = DATA_DIR / "library" / "movements.json"
    return _validate_list(load_json_file(path), Movement, path)


def load_glossary() -> list[GlossaryTerm]:
    path = DATA_DIR / "library" / "glossary.json"
    return _validate_list(load_json_file(path), GlossaryTerm, path)


def load_cycles() -> list[Cycle]:
    path = DATA_DIR / "programming" / "cycles.json"
    return _validate_list(load_json_file(path), Cycle, path)


def load_blocks() -> list[Block]:
    path = DATA_DIR / "programming" / "blocks.json"
    return _validate_list(load_json_file(path), Block, path)


def load_weeks() -> list[TrainingWeek]:
    path = DATA_DIR / "programming" / "weeks.json"
    return _validate_list(load_json_file(path), TrainingWeek, path)


def load_day_families_config() -> dict[str, Any]:
    path = GENERATOR_DIR / "day_families.json"
    return _validate_mapping(load_json_file(path), path)


def load_block_rules_config() -> dict[str, Any]:
    path = GENERATOR_DIR / "block_rules.json"
    return _validate_mapping(load_json_file(path), path)


def load_session_templates_config() -> dict[str, Any]:
    path = GENERATOR_DIR / "session_templates.json"
    return _validate_mapping(load_json_file(path), path)


def load_session_by_date(session_date: str | date) -> SessionDay:
    parsed_date = _parse_session_date(session_date)
    path = SESSIONS_DIR / f"{parsed_date.isoformat()}.json"
    return _validate_item(load_json_file(path), SessionDay, path)


def load_all_sessions() -> list[SessionDay]:
    if not SESSIONS_DIR.exists():
        raise FileNotFoundError(f"Sessions directory not found: {SESSIONS_DIR}")

    sessions: list[SessionDay] = []
    for path in sorted(SESSIONS_DIR.glob("*.json")):
        sessions.append(_validate_item(load_json_file(path), SessionDay, path))
    return sessions


def validate_core_data() -> dict[str, Any]:
    return {
        "gym_profile": load_gym_profile(),
        "athlete_profiles": load_athlete_profiles(),
        "movements": load_movements(),
        "glossary": load_glossary(),
        "cycles": load_cycles(),
        "blocks": load_blocks(),
        "weeks": load_weeks(),
        "day_families": load_day_families_config(),
        "block_rules": load_block_rules_config(),
        "session_templates": load_session_templates_config(),
        "sessions": load_all_sessions(),
    }


def _resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return BASE_DIR / candidate


def _parse_session_date(session_date: str | date) -> date:
    if isinstance(session_date, date):
        return session_date

    if isinstance(session_date, str):
        try:
            return date.fromisoformat(session_date)
        except ValueError as exc:
            raise ValueError("session_date must use YYYY-MM-DD format") from exc

    raise TypeError("session_date must be a date object or a YYYY-MM-DD string")


def _validate_item(payload: Any, model_class: type[ModelT], source: Path) -> ModelT:
    try:
        return model_class.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(
            f"Validation failed for {source} with model {model_class.__name__}: "
            f"{_format_validation_error(exc)}"
        ) from exc


def _validate_list(payload: Any, model_class: type[ModelT], source: Path) -> list[ModelT]:
    if not isinstance(payload, list):
        raise ValueError(f"Expected a list in {source}, got {type(payload).__name__}")

    validated_items: list[ModelT] = []
    for index, item in enumerate(payload, start=1):
        try:
            validated_items.append(model_class.model_validate(item))
        except ValidationError as exc:
            raise ValueError(
                f"Validation failed for {source} at item {index} with model {model_class.__name__}: "
                f"{_format_validation_error(exc)}"
            ) from exc
    return validated_items


def _validate_mapping(payload: Any, source: Path) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError(f"Expected an object in {source}, got {type(payload).__name__}")
    return payload


def _format_validation_error(error: ValidationError) -> str:
    issues = []
    for item in error.errors(include_url=False):
        location = ".".join(str(part) for part in item["loc"]) or "root"
        issues.append(f"{location}: {item['msg']}")
    return "; ".join(issues)
