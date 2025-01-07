import sqlite3
from datetime import datetime

import pytest
from personal_mcp.database import Database


def test_database_initialization(temp_db_path):
    """Test database initialization creates all required tables."""
    db = Database(temp_db_path)

    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Check all tables exist
        tables = [
            "workouts",
            "exercises",
            "sets",
            "meals",
            "foods",
            "journal_entries",
            "tags",
            "entry_tags",
        ]

        for table in tables:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            assert cursor.fetchone() is not None, f"Table {table} was not created"


def test_foreign_key_constraints(db):
    """Test foreign key constraints are enforced."""
    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Try to insert exercise without valid workout_id
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                "INSERT INTO exercises (workout_id, name) VALUES (999, 'Invalid Exercise')"
            )


def test_data_types_and_constraints(db):
    """Test data type constraints and validations."""
    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Test perceived_effort range constraint
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                """
                INSERT INTO workouts (date, perceived_effort)
                VALUES (?, ?)
                """,
                (datetime.now().strftime("%Y-%m-%d"), 11),  # Invalid effort level
            )

        # Test RPE range constraint
        workout_id = cursor.execute(
            "INSERT INTO workouts (date) VALUES (?)", (datetime.now().strftime("%Y-%m-%d"),)
        ).lastrowid

        exercise_id = cursor.execute(
            "INSERT INTO exercises (workout_id, name) VALUES (?, ?)", (workout_id, "Test Exercise")
        ).lastrowid

        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                """
                INSERT INTO sets (exercise_id, weight, reps, rpe)
                VALUES (?, ?, ?, ?)
                """,
                (exercise_id, 100, 10, 11),  # Invalid RPE
            )


def test_cascading_deletes(db):
    """Test cascading deletes work properly."""
    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Create test data
        cursor.execute(
            "INSERT INTO workouts (date) VALUES (?)", (datetime.now().strftime("%Y-%m-%d"),)
        )
        workout_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO exercises (workout_id, name) VALUES (?, ?)", (workout_id, "Test Exercise")
        )
        exercise_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO sets (exercise_id, weight, reps)
            VALUES (?, ?, ?)
            """,
            (exercise_id, 100, 10),
        )

        # Delete workout and verify cascading deletes
        cursor.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))

        cursor.execute("SELECT COUNT(*) FROM exercises WHERE workout_id = ?", (workout_id,))
        assert cursor.fetchone()[0] == 0, "Exercise not deleted after workout deletion"

        cursor.execute("SELECT COUNT(*) FROM sets WHERE exercise_id = ?", (exercise_id,))
        assert cursor.fetchone()[0] == 0, "Set not deleted after exercise deletion"


def test_journal_tags(db):
    """Test journal entry tags functionality."""
    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Create journal entry
        cursor.execute(
            """
            INSERT INTO journal_entries (date, entry_type, content)
            VALUES (?, ?, ?)
            """,
            (datetime.now().strftime("%Y-%m-%d"), "daily", "Test entry"),
        )
        entry_id = cursor.lastrowid

        # Create tags
        tags = ["test", "example"]
        tag_ids = []
        for tag in tags:
            cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag,))
            tag_ids.append(cursor.lastrowid)

        # Link tags to entry
        for tag_id in tag_ids:
            cursor.execute(
                "INSERT INTO entry_tags (entry_id, tag_id) VALUES (?, ?)", (entry_id, tag_id)
            )

        # Verify tags are linked
        cursor.execute(
            """
            SELECT t.name
            FROM tags t
            JOIN entry_tags et ON t.id = et.tag_id
            WHERE et.entry_id = ?
            """,
            (entry_id,),
        )
        retrieved_tags = [row[0] for row in cursor.fetchall()]
        assert set(retrieved_tags) == set(tags), "Tags not properly linked to entry"


def test_meal_tracking(db):
    """Test meal and food tracking functionality."""
    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Create meal
        cursor.execute(
            """
            INSERT INTO meals (date, meal_type, time, hunger_level, satisfaction_level)
            VALUES (?, ?, ?, ?, ?)
            """,
            (datetime.now().strftime("%Y-%m-%d"), "lunch", "12:00", 7, 8),
        )
        meal_id = cursor.lastrowid

        # Add foods to meal
        foods = [("Chicken", 200, "g", 46, 330), ("Rice", 100, "g", 7, 111)]

        for food in foods:
            cursor.execute(
                """
                INSERT INTO foods (meal_id, name, amount, unit, protein, calories)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (meal_id, *food),
            )

        # Verify meal totals
        cursor.execute(
            """
            SELECT SUM(protein), SUM(calories)
            FROM foods
            WHERE meal_id = ?
            """,
            (meal_id,),
        )
        total_protein, total_calories = cursor.fetchone()
        assert total_protein == 53, "Incorrect total protein calculation"
        assert total_calories == 441, "Incorrect total calories calculation"
