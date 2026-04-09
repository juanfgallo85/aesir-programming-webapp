from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Cycle(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    focus: str = Field(min_length=1)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self
