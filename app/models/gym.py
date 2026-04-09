from pydantic import BaseModel, ConfigDict, Field


class GymProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1)
    city: str = Field(min_length=1)
    state: str = Field(min_length=1)
    country: str = Field(min_length=1)
    discipline: str = Field(min_length=1)
    class_duration_minutes: int = Field(ge=1, le=180)
    focus: str = Field(min_length=1)
    open_gym_enabled: bool
    same_class_all_day: bool
    session_levels: list[str] = Field(min_length=1)


class AthleteProfileType(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    code: str = Field(min_length=1)
    label: str = Field(min_length=1)
    description: str = Field(min_length=1)
