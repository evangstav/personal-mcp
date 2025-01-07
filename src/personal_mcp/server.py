from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional
import pandas as pd
from .database import Database
from .tools import register_workout_tools, register_nutrition_tools, register_journal_tools
from .resources import register_resources
from .prompts import register_prompts


class PersonalMCP:
    def __init__(self, name: str = "Personal Assistant", db_path: str = "personal_tracking.db"):
        self.mcp = FastMCP(name)
        self.db = Database(db_path)
        self.setup_tools()
        self.setup_resources()
        self.setup_prompts()

    def setup_tools(self):
        register_workout_tools(self.mcp, self.db)
        register_nutrition_tools(self.mcp, self.db)
        register_journal_tools(self.mcp, self.db)

    def setup_resources(self):
        @self.mcp.resource("health://workout-history/{start_date}/{end_date}")
        def get_workout_history(start_date: str, end_date: str) -> str:
            """Get workout history within a date range."""
            with self.db.get_connection() as conn:
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

        @self.mcp.resource("health://nutrition/{start_date}/{end_date}")
        def get_nutrition_log(start_date: str, end_date: str) -> str:
            """Get nutrition log within a date range."""
            with self.db.get_connection() as conn:
                query = """
                    SELECT m.*, f.name as food_name, 
                           f.amount, f.unit, f.protein, f.calories
                    FROM meals m
                    JOIN foods f ON m.id = f.meal_id
                    WHERE m.date BETWEEN ? AND ?
                """
                df = pd.read_sql_query(query, conn, params=(start_date, end_date))
                return df.to_json(orient="records")

        @self.mcp.resource("journal://entries/{start_date}/{end_date}")
        def get_journal_entries(start_date: str, end_date: str) -> str:
            """Get journal entries within a date range."""
            with self.db.get_connection() as conn:
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

    def setup_prompts(self):
        @self.mcp.prompt()
        def analyze_workout_load(workout_history: str) -> List[Dict]:
            """Analyze workout load and suggest adjustments."""
            return [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"""Please analyze my recent workout history and suggest adjustments based on:
                    1. Shoulder rehabilitation status
                    2. Recent performance
                    3. Recovery patterns
                    4. Energy levels and mood from journal entries
                    
                    Workout History:
                    {workout_history}
                    
                    Particularly focus on:
                    - Safe progression for shoulder exercises
                    - Maintaining leg strength (squats, deadlifts)
                    - Overall volume management
                    - Correlation between workout intensity and recovery metrics""",
                    },
                }
            ]

        @self.mcp.prompt()
        def nutrition_recommendations(
            nutrition_log: str, start_date: str, end_date: str
        ) -> List[Dict]:
            """Get personalized nutrition recommendations."""
            return [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"""Based on my meal logs for period {start_date} to {end_date}, please provide:
                    
                    Nutrition Log:
                    {nutrition_log}
                    
                    1. Protein intake optimization
                    2. Meal timing suggestions
                    3. Pre/post workout nutrition
                    4. Supplement timing (creatine, vitamins, omega-3)
                    5. Patterns between nutrition and energy/mood
                    6. Hunger and satisfaction patterns""",
                    },
                }
            ]

        @self.mcp.prompt()
        def journal_insights(entries: str) -> List[Dict]:
            """Generate insights from journal entries."""
            return [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"""Please analyze my journal entries and provide insights on:
                    
                    Entries:
                    {entries}
                    
                    1. Patterns in mood and energy levels
                    2. Sleep quality trends and correlations
                    3. Stress management effectiveness
                    4. Relationship between workouts and well-being
                    5. Impact of nutrition on daily metrics
                    6. Progress towards goals mentioned in entries
                    7. Suggestions for improvement based on patterns""",
                    },
                }
            ]

    def run(self):
        """Run the MCP server."""
        self.mcp.run()
