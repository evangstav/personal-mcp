from datetime import datetime

import pandas as pd
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ResourceError

from .database import Database


def validate_date_format(date_str: str) -> bool:
    """Validate date string format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def register_resources(mcp: FastMCP, db: Database) -> None:
    """Register MCP resources."""

    @mcp.resource("health://workout-history/{start_date}/{end_date}")
    def get_workout_history(start_date: str, end_date: str) -> str:
        """Get workout history within a date range."""
        if not validate_date_format(start_date) or not validate_date_format(end_date):
            raise ResourceError("Invalid date format. Expected YYYY-MM-DD")

        with db.get_connection() as conn:
            query = """
                SELECT w.*, e.name as exercise_name,
                       s.weight, s.reps, s.rpe, s.notes as set_notes
                FROM workouts w
                JOIN exercises e ON w.id = e.workout_id
                JOIN sets s ON e.id = s.exercise_id
                WHERE w.date BETWEEN ? AND ?
            """
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
            return df.to_json(orient="records")

    @mcp.resource("health://nutrition/{start_date}/{end_date}")
    def get_nutrition_log(start_date: str, end_date: str) -> str:
        """Get nutrition log within a date range."""
        if not validate_date_format(start_date) or not validate_date_format(end_date):
            raise ResourceError("Invalid date format. Expected YYYY-MM-DD")

        with db.get_connection() as conn:
            query = """
                SELECT m.*, f.name as food_name,
                       f.amount, f.unit, f.protein, f.calories
                FROM meals m
                JOIN foods f ON m.id = f.meal_id
                WHERE m.date BETWEEN ? AND ?
            """
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
            return df.to_json(orient="records")

    @mcp.resource("journal://entries/{start_date}/{end_date}")
    def get_journal_entries(start_date: str, end_date: str) -> str:
        """Get journal entries within a date range."""
        if not validate_date_format(start_date) or not validate_date_format(end_date):
            raise ResourceError("Invalid date format. Expected YYYY-MM-DD")

        with db.get_connection() as conn:
            query = """
                SELECT j.*, GROUP_CONCAT(t.name) as tags
                FROM journal_entries j
                LEFT JOIN entry_tags et ON j.id = et.entry_id
                LEFT JOIN tags t ON et.tag_id = t.id
                WHERE j.date BETWEEN ? AND ?
                GROUP BY j.id
            """
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
            return df.to_json(orient="records")
