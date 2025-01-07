from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, conint


class JournalEntry(BaseModel):
    content: str
    entry_type: str
    mood: Optional[conint(ge=1, le=10)] = None
    energy: Optional[conint(ge=1, le=10)] = None
    sleep_quality: Optional[conint(ge=1, le=10)] = None
    stress_level: Optional[conint(ge=1, le=10)] = None
    tags: Optional[List[str]] = None
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    class Config:
        arbitrary_types_allowed = True


class Set(BaseModel):
    weight: float
    reps: int
    rpe: Optional[conint(ge=1, le=10)] = None
    notes: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


class Exercise(BaseModel):
    name: str
    sets: List[Set]

    class Config:
        arbitrary_types_allowed = True


class Workout(BaseModel):
    date: str
    exercises: List[Exercise]
    perceived_effort: Optional[conint(ge=1, le=10)] = None
    post_workout_feeling: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


class Food(BaseModel):
    name: str
    amount: float
    unit: str
    protein: Optional[float] = None
    calories: Optional[float] = None

    class Config:
        arbitrary_types_allowed = True


class Meal(BaseModel):
    meal_type: str
    foods: List[Food]
    time: str
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    hunger_level: Optional[conint(ge=1, le=10)] = None
    satisfaction_level: Optional[conint(ge=1, le=10)] = None
    notes: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
