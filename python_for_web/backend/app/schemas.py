from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Name = Annotated[str, Field(min_length=1, max_length=100)]
Skill = Annotated[str, Field(min_length=1, max_length=60)]


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class AnalysisRequest(InputModel):
    text: str = Field(min_length=1, max_length=50_000)

    @field_validator("text", mode="before")
    @classmethod
    def preserve_text(cls, value):
        # Counts include the original whitespace, while whitespace-only is invalid.
        if isinstance(value, str) and not value.strip():
            raise ValueError("Enter some text to analyze")
        return value

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)


class WordFrequency(BaseModel):
    word: str
    count: int


class AnalysisResult(BaseModel):
    character_count: int
    word_count: int
    unique_word_count: int
    frequent_words: list[WordFrequency]


class StudentFields(InputModel):
    name: Name
    country: Name
    city: Name
    date_of_birth: date
    skills: list[Skill] = Field(default_factory=list, max_length=30)
    bio: str = Field(default="", max_length=2_000)

    @field_validator("date_of_birth")
    @classmethod
    def not_future(cls, value):
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return value

    @field_validator("skills")
    @classmethod
    def unique_skills(cls, values):
        return list(dict.fromkeys(values))


class StudentCreate(StudentFields):
    pass


class StudentUpdate(InputModel):
    name: Name | None = None
    country: Name | None = None
    city: Name | None = None
    date_of_birth: date | None = None
    skills: list[Skill] | None = Field(default=None, max_length=30)
    bio: str | None = Field(default=None, max_length=2_000)

    @model_validator(mode="after")
    def validate_patch(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")
        if any(getattr(self, key) is None for key in self.model_fields_set):
            raise ValueError("Student fields cannot be null")
        if self.date_of_birth and self.date_of_birth > date.today():
            raise ValueError("Date of birth cannot be in the future")
        if self.skills is not None:
            self.skills = list(dict.fromkeys(self.skills))
        return self


class StudentRead(StudentFields):
    id: str
    created_at: datetime
    updated_at: datetime


class StudentPage(BaseModel):
    items: list[StudentRead]
    total: int
    offset: int
    limit: int
