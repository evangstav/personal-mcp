from typing import List, Dict


def register_prompts(mcp):
    """Register prompts for the MCP server."""

    @mcp.prompt()
    def analyze_workout_load(workout_history: str) -> List[Dict]:
        """Analyze workout load and suggest adjustments."""
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"""Please analyze my workout history and suggest adjustments based on:
                1. Shoulder rehabilitation status (post-surgery September 2024)
                2. Recent performance and recovery patterns
                3. Energy levels and mood from journal entries
                
                History: {workout_history}
                
                Focus on:
                - Safe shoulder progression
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
                    "text": f"""Analyze meal logs ({start_date} to {end_date}):
                
                Log: {nutrition_log}
                
                Targets:
                - Daily protein: 160g (2g/kg at 80kg)
                - Pre/post workout nutrition
                - Supplement timing (creatine, vitamins, omega-3)
                - Hunger and satisfaction patterns""",
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
                    "text": f"""Analyze journal entries:
                {entries}
                
                1. Mood/energy patterns
                2. Sleep and recovery trends
                3. Workout and nutrition impacts
                4. Stress management
                5. Progress on rehabilitation
                6. Areas for improvement""",
                },
            }
        ]
