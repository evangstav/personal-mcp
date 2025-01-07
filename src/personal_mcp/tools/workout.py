import json
from typing import Optional

from ..models import Workout


def register_workout_tools(mcp, db):
    """Register workout-related tools."""

    @mcp.tool(description="Log a workout session with exercises")
    def log_workout(workout: Workout) -> str:
        """Log a workout session with exercises and subjective feedback."""
        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Create workout entry
            cursor.execute(
                """
                INSERT INTO workouts (date, perceived_effort, post_workout_feeling, notes)
                VALUES (?, ?, ?, ?)
            """,
                (
                    workout.date,
                    workout.perceived_effort,
                    workout.post_workout_feeling,
                    workout.notes,
                ),
            )
            workout_id = cursor.lastrowid

            # Add exercises and sets
            for exercise in workout.exercises:
                cursor.execute(
                    """
                    INSERT INTO exercises (workout_id, name)
                    VALUES (?, ?)
                """,
                    (workout_id, exercise.name),
                )
                exercise_id = cursor.lastrowid

                for set_data in exercise.sets:
                    cursor.execute(
                        """
                        INSERT INTO sets (exercise_id, weight, reps, rpe, notes)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            exercise_id,
                            set_data.weight,
                            set_data.reps,
                            set_data.rpe,
                            set_data.notes,
                        ),
                    )

            conn.commit()
            return f"Logged workout for {workout.date} with {len(workout.exercises)} exercises"

    @mcp.tool(description="Calculate safe training weights based on recovery")
    def calculate_training_weights(
        exercise: str,
        base_weight: float,
        days_since_surgery: Optional[int] = None,
        recent_pain_level: Optional[int] = None,
        recent_rpe: Optional[float] = None,
    ) -> str:
        """Calculate safe training weights taking into account shoulder recovery."""
        base_reduction = 0.4  # 40% reduction post-surgery
        recovery_factor = min((days_since_surgery or 0) / 180, 1) if days_since_surgery else 1
        pain_reduction = (recent_pain_level or 0) * 0.05 if recent_pain_level else 0

        rpe_adjustment = 0
        if recent_rpe:
            if recent_rpe > 8:  # Too hard
                rpe_adjustment = -0.05
            elif recent_rpe < 6:  # Too easy
                rpe_adjustment = 0.05

        recommended_weight = base_weight * (1 - base_reduction) * (0.6 + 0.4 * recovery_factor)
        recommended_weight *= 1 - pain_reduction
        recommended_weight *= 1 + rpe_adjustment

        result = {
            "recommended_weight": round(recommended_weight, 1),
            "recommended_reps": "12-15 for rehabilitation phase",
            "notes": "Focus on form and controlled movement",
        }

        return json.dumps(result)
