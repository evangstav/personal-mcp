from typing import Dict, List

from mcp.server.fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Register MCP prompts."""

    @mcp.prompt()
    def analyze_workout_load(workout_history: str) -> List[Dict]:
        """Analyze workout load and suggest adjustments."""
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"""Please analyze my workout history and suggest adjustments based on:
                    1. Shoulder rehabilitation status
                    2. Recent performance
                    3. Recovery patterns
                    4. Energy levels and mood from journal entries

                    Workout History:
                    {workout_history}

                    Particularly focus on:
                    - Safe progression for shoulder exercises
                    - Maintaining leg strength
                    - Volume management
                    - Recovery metrics""",
                },
            }
        ]

    @mcp.prompt()
    def nutrition_recommendations(nutrition_log: str, start_date: str, end_date: str) -> List[Dict]:
        """Get personalized nutrition recommendations."""
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (  # Use parentheses for line continuation
                        f"""Based on my meal logs for period {start_date} to {end_date}, please provide:

                        Nutrition Log:
                        {nutrition_log}

                        1. Protein intake optimization
                        2. Meal timing suggestions
                        3. Pre/post workout nutrition
                        4. Supplement timing (creatine, vitamins, omega-3)
                        5. Patterns between nutrition and energy/mood
                        6. Hunger and satisfaction patterns"""
                    ),
                },
            }
        ]

    @mcp.prompt()
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
