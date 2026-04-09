from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.note import CoachNote
from app.models.scaling import ScalingOption

SessionPartType = Literal[
    "joint_prep",
    "warm_up",
    "skill",
    "strength",
    "wod",
    "accessory",
    "cooldown",
    "competitor_extra",
    "brief",
    "warmup",
    "metcon",
]
SessionStatus = Literal["draft", "reviewed", "final", "locked"]


class SessionPartMovement(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1)
    reps: int | None = Field(default=None, ge=0)
    sets: int | None = Field(default=None, ge=0)
    calories: int | None = Field(default=None, ge=0)
    distance_meters: int | None = Field(default=None, ge=0)
    percentage_of_pr: str | None = None
    suggested_load_male: str | None = None
    suggested_load_female: str | None = None
    suggested_load_general: str | None = None
    machine_calories_male: int | None = Field(default=None, ge=0)
    machine_calories_female: int | None = Field(default=None, ge=0)
    running_distance_meters: int | None = Field(default=None, ge=0)
    weather_alternative: str | None = None
    notes: str | None = None


class SessionPart(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1)
    part_type: SessionPartType
    duration_minutes: int = Field(ge=1, le=60)
    description: str = Field(min_length=1)
    format: str | None = None
    scheme: str | None = None
    score_type: str | None = None
    movements: list[SessionPartMovement] = Field(default_factory=list)
    notes: str | None = None

    @property
    def normalized_type(self) -> str:
        aliases = {
            "brief": "joint_prep",
            "warmup": "warm_up",
            "metcon": "wod",
        }
        return aliases.get(self.part_type, self.part_type)

    @property
    def display_label(self) -> str:
        labels = {
            "joint_prep": "Movilidad / activacion articular",
            "warm_up": "Warm-up",
            "skill": "Skill",
            "strength": "Strength",
            "wod": "WOD principal",
            "accessory": "Accessory",
            "cooldown": "Cooldown",
            "competitor_extra": "Extra competidor",
        }
        return labels.get(self.normalized_type, self.normalized_type.replace("_", " ").title())

    @property
    def is_primary_wod(self) -> bool:
        return self.normalized_type == "wod"


class SessionDay(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    session_date: date
    status: SessionStatus = "reviewed"
    generated_by: str | None = None
    generated_at: datetime | None = None
    review_notes: str | None = None
    is_auto_generated: bool = False
    title: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    coach_summary: str = Field(min_length=1)
    public_summary: str = Field(min_length=1)
    family_type: str = Field(min_length=1)
    dominant_stimulus: str = Field(min_length=1)
    dominant_pattern: str = Field(min_length=1)
    technical_level: str = Field(min_length=1)
    fatigue_level: str = Field(min_length=1)
    operational_color: str = Field(min_length=1)
    equipment_alert: str = Field(min_length=1)
    session_parts: list[SessionPart] = Field(min_length=1)
    scaling_options: list[ScalingOption] = Field(min_length=1)
    coach_notes: list[CoachNote] = Field(min_length=1)

    @property
    def status_label(self) -> str:
        labels = {
            "draft": "Draft",
            "reviewed": "Reviewed",
            "final": "Final",
            "locked": "Locked",
        }
        return labels.get(self.status, self.status.title())

    @property
    def is_protected_status(self) -> bool:
        return self.status in {"reviewed", "final", "locked"}
