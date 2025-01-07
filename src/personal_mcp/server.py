from mcp.server.fastmcp import FastMCP

from .database import Database
from .prompts import register_prompts
from .resources import register_resources
from .tools import register_journal_tools, register_nutrition_tools, register_workout_tools


class PersonalMCP:
    def __init__(
        self, name: str = "Personal Assistant", db_path: str = "personal_tracking.db"
    ) -> None:
        self.mcp = FastMCP(name)
        self.db = Database(db_path)
        self.setup_tools()
        self.setup_resources()
        self.setup_prompts()

    def setup_tools(self) -> None:
        register_workout_tools(self.mcp, self.db)
        register_nutrition_tools(self.mcp, self.db)
        register_journal_tools(self.mcp, self.db)

    def setup_resources(self) -> None:
        register_resources(self.mcp, self.db)

    def setup_prompts(self) -> None:
        register_prompts(self.mcp)

    def run(self) -> None:
        """Run the MCP server."""
        self.mcp.run()
