from pydantic import BaseModel, ConfigDict, Field


class ScalingOption(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    level: str = Field(min_length=1)
    adjustment: str = Field(min_length=1)
