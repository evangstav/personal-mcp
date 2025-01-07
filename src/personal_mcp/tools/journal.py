import json
from typing import List, Optional

import pandas as pd

from ..models import JournalEntry


def register_journal_tools(mcp, db):
    """Register journal-related tools."""

    @mcp.tool(description="Log a journal entry")
    def log_journal_entry(entry: JournalEntry) -> str:
        """Add a journal entry with metadata."""
        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Create journal entry
            cursor.execute(
                """
                INSERT INTO journal_entries
                (date, entry_type, content, mood, energy, sleep_quality, stress_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    entry.date,
                    entry.entry_type,
                    entry.content,
                    entry.mood,
                    entry.energy,
                    entry.sleep_quality,
                    entry.stress_level,
                ),
            )
            entry_id = cursor.lastrowid

            # Handle tags
            if entry.tags:
                for tag in entry.tags:
                    # Insert or get tag
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO tags (name) VALUES (?)
                    """,
                        (tag,),
                    )
                    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
                    tag_id = cursor.fetchone()[0]

                    # Link tag to entry
                    cursor.execute(
                        """
                        INSERT INTO entry_tags (entry_id, tag_id)
                        VALUES (?, ?)
                    """,
                        (entry_id, tag_id),
                    )

            conn.commit()
            return f"Added {entry.entry_type} journal entry for {entry.date}"

    @mcp.tool(description="Analyze journal entries")
    def analyze_journal_entries(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        entry_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Analyze journal entries and extract insights."""
        with db.get_connection() as conn:
            query = """
                SELECT j.*, GROUP_CONCAT(t.name) as tags
                FROM journal_entries j
                LEFT JOIN entry_tags et ON j.id = et.entry_id
                LEFT JOIN tags t ON et.tag_id = t.id
                WHERE 1=1
            """
            params = []

            if start_date:
                query += " AND j.date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND j.date <= ?"
                params.append(end_date)
            if entry_type:
                query += " AND j.entry_type = ?"
                params.append(entry_type)

            query += " GROUP BY j.id"

            df = pd.read_sql_query(query, conn, params=params)

            if df.empty:
                return json.dumps({"message": "No entries found for the specified criteria"})

            # Filter by tags if specified
            if tags:
                df = df[df["tags"].apply(lambda x: x and any(tag in x.split(",") for tag in tags))]

            metrics = {
                "entry_count": len(df),
                "average_metrics": {
                    "mood": round(df["mood"].mean(), 2),
                    "energy": round(df["energy"].mean(), 2),
                    "sleep_quality": round(df["sleep_quality"].mean(), 2),
                    "stress_level": round(df["stress_level"].mean(), 2),
                },
                "trends": {
                    "mood_trend": "improving" if df["mood"].is_monotonic_increasing else "varying",
                    "energy_trend": (
                        "improving" if df["energy"].is_monotonic_increasing else "varying"
                    ),
                },
                "common_tags": (
                    df["tags"].value_counts().head(5).to_dict() if not df["tags"].empty else {}
                ),
            }

            return json.dumps(metrics)
