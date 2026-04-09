from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TrainingWeek(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(min_length=1)
    cycle_id: str = Field(min_length=1)
    block_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    weekly_focus: str = Field(min_length=1)
    deload_flag: bool = False
    test_week_flag: bool = False
    start_date: date
    end_date: date
    session_dates: list[date] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self
