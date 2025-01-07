from datetime import datetime

import pytest
from personal_mcp.models import Exercise, Food, JournalEntry, Meal, Set, Workout
from pydantic import ValidationError


def test_set_validation():
    valid_set = Set(weight=60.0, reps=8, rpe=7)
    assert valid_set.weight == 60.0
    assert valid_set.reps == 8
    assert valid_set.rpe == 7

    with pytest.raises(ValidationError):
        Set(weight=60.0, reps=8, rpe=11)  # RPE > 10


def test_exercise_validation():
    valid_exercise = Exercise(name="Squat", sets=[Set(weight=60.0, reps=8, rpe=7)])
    assert valid_exercise.name == "Squat"
    assert len(valid_exercise.sets) == 1


def test_workout_validation():
    valid_workout = Workout(
        date=datetime.now().strftime("%Y-%m-%d"),
        exercises=[Exercise(name="Squat", sets=[Set(weight=60.0, reps=8, rpe=7)])],
        perceived_effort=7,
    )
    assert len(valid_workout.exercises) == 1

    with pytest.raises(ValidationError):
        Workout(
            date=datetime.now().strftime("%Y-%m-%d"),
            exercises=[],  # Empty exercises list
            perceived_effort=11,  # Invalid effort level
        )


def test_food_validation():
    valid_food = Food(name="Chicken Breast", amount=100.0, unit="g", protein=30.0, calories=165.0)
    assert valid_food.name == "Chicken Breast"
    assert valid_food.amount == 100.0


def test_meal_validation():
    valid_meal = Meal(
        meal_type="lunch",
        foods=[Food(name="Chicken Breast", amount=100.0, unit="g", protein=30.0, calories=165.0)],
        time="12:00",
        hunger_level=7,
        satisfaction_level=8,
    )
    assert valid_meal.meal_type == "lunch"
    assert len(valid_meal.foods) == 1

    with pytest.raises(ValidationError):
        Meal(
            meal_type="lunch",
            foods=[],  # Empty foods list
            time="12:00",
            hunger_level=11,  # Invalid level
        )


def test_journal_entry_validation():
    valid_entry = JournalEntry(
        content="Test entry",
        entry_type="daily",
        mood=8,
        energy=7,
        sleep_quality=8,
        stress_level=3,
        tags=["test", "mood"],
    )
    assert valid_entry.content == "Test entry"
    assert len(valid_entry.tags) == 2

    with pytest.raises(ValidationError):
        JournalEntry(content="Test entry", entry_type="daily", mood=11)  # Invalid mood level
