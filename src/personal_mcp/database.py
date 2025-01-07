import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator


class Database:
    def __init__(self, db_path: str = "personal_tracking.db"):
        self.db_path = Path(db_path)
        self.initialize_schema()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection with context management."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    def initialize_schema(self) -> None:
        """Initialize the database schema with foreign key support."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Workouts table - track workout sessions
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS workouts (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    perceived_effort INTEGER CHECK (perceived_effort BETWEEN 1 AND 10),
                    post_workout_feeling TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Exercises table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS exercises (
                    id INTEGER PRIMARY KEY,
                    workout_id INTEGER,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (workout_id) REFERENCES workouts (id) ON DELETE CASCADE
                )
            """
            )

            # Sets table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sets (
                    id INTEGER PRIMARY KEY,
                    exercise_id INTEGER,
                    weight REAL NOT NULL,
                    reps INTEGER NOT NULL,
                    rpe REAL CHECK (rpe BETWEEN 1 AND 10),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (exercise_id) REFERENCES exercises (id) ON DELETE CASCADE
                )
            """
            )

            # Meals table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS meals (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    meal_type TEXT NOT NULL,
                    time TEXT NOT NULL,
                    total_protein REAL,
                    total_calories REAL,
                    hunger_level INTEGER CHECK (hunger_level BETWEEN 1 AND 10),
                    satisfaction_level INTEGER CHECK (satisfaction_level BETWEEN 1 AND 10),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Foods table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS foods (
                    id INTEGER PRIMARY KEY,
                    meal_id INTEGER,
                    name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    protein REAL,
                    calories REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (meal_id) REFERENCES meals (id) ON DELETE CASCADE
                )
            """
            )

            # Journal entries table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    entry_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    mood INTEGER CHECK (mood BETWEEN 1 AND 10),
                    energy INTEGER CHECK (energy BETWEEN 1 AND 10),
                    sleep_quality INTEGER CHECK (sleep_quality BETWEEN 1 AND 10),
                    stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 10),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Tags table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                )
            """
            )

            # Journal entry tags mapping
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS entry_tags (
                    entry_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (entry_id, tag_id),
                    FOREIGN KEY (entry_id) REFERENCES journal_entries (id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
                )
            """
            )

            conn.commit()
