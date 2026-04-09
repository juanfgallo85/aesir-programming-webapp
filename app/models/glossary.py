from pydantic import BaseModel, ConfigDict, Field


class GlossaryTerm(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    term: str = Field(min_length=1)
    category: str | None = None
    definition: str = Field(min_length=1)
