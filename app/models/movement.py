from pydantic import BaseModel, ConfigDict, Field


class Movement(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    slug: str = Field(min_length=1)
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    dominant_pattern: str = Field(min_length=1)
    technical_level: str | None = None
    description: str | None = None
    equipment: list[str] = Field(default_factory=list)
    basic_cues: list[str] = Field(default_factory=list)
    common_errors: list[str] = Field(default_factory=list)
    scaling_notes: list[str] = Field(default_factory=list)
