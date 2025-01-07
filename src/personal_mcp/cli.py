import click
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

from .server import PersonalMCP

console = Console()

def setup_logging(verbose: bool = False):
    """Configure rich logging for the CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )

def get_config_dir() -> Path:
    """Get the configuration directory, creating it if needed."""
    if sys.platform == "darwin":
        config_dir = Path.home() / "Library" / "Application Support" / "personal-mcp"
    elif sys.platform == "win32":
        config_dir = Path(os.getenv("APPDATA")) / "personal-mcp"
    else:
        config_dir = Path.home() / ".config" / "personal-mcp"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def load_config() -> dict:
    """Load configuration from config file."""
    config_file = get_config_dir() / "config.json"
    if config_file.exists():
        return json.loads(config_file.read_text())
    return {}

def save_config(config: dict):
    """Save configuration to config file."""
    config_file = get_config_dir() / "config.json"
    config_file.write_text(json.dumps(config, indent=2))

@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose: bool):
    """Personal MCP Server - Health and Well-being Tracking"""
    setup_logging(verbose)

@cli.command()
@click.option("--name", default="Personal Assistant", help="Server name")
@click.option("--db-path", help="Database path")
def run(name: str, db_path: Optional[str]):
    """Run the MCP server."""
    try:
        server = PersonalMCP(name=name, db_path=db_path)
        server.run()
    except Exception as e:
        console.print(f"[red]Error starting server:[/red] {str(e)}")
        sys.exit(1)

@cli.command()
@click.option("--name", default="Personal Assistant", help="Server name")
@click.option("--db-path", help="Database path")
def dev(name: str, db_path: Optional[str]):
    """Run the server in development mode."""
    try:
        server = PersonalMCP(name=name, db_path=db_path)
        try:
            from mcp.server.development import run_development_server
            run_development_server(server.mcp)
        except ImportError:
            console.print("[yellow]Development server not available. Running in normal mode.[/yellow]")
            server.run()
    except Exception as e:
        console.print(f"[red]Error starting development server:[/red] {str(e)}")
        sys.exit(1)

@cli.command()
@click.option("--name", default="Personal Assistant", help="Server name")
@click.option("--db-path", help="Database path")
def inspect(name: str, db_path: Optional[str]):
    """Run the server with MCP Inspector."""
    try:
        server = PersonalMCP(name=name, db_path=db_path)
        try:
            from mcp.server.inspector import run_inspector
            run_inspector(server.mcp)
        except ImportError:
            console.print("[yellow]Inspector not available. Running in normal mode.[/yellow]")
            server.run()
    except Exception as e:
        console.print(f"[red]Error starting inspector:[/red] {str(e)}")
        sys.exit(1)

@cli.command()
@click.option("--claude-desktop", is_flag=True, help="Install to Claude Desktop")
@click.option("--name", default="Personal Assistant", help="Server name")
def install(claude_desktop: bool, name: str):
    """Install the server configuration."""
    try:
        if claude_desktop:
            config_file = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        else:
            config_file = Path.home() / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline" / "settings" / "cline_mcp_settings.json"

        if not config_file.exists():
            console.print(f"[yellow]Configuration file not found:[/yellow] {config_file}")
            return

        config = json.loads(config_file.read_text())
        server_config = {
            "command": "personal-mcp",
            "args": ["--name", name],
            "env": {},
            "disabled": False
        }

        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        config["mcpServers"]["personal-mcp"] = server_config
        config_file.write_text(json.dumps(config, indent=2))
        
        console.print(f"[green]Successfully installed server configuration to:[/green] {config_file}")
    
    except Exception as e:
        console.print(f"[red]Error installing server configuration:[/red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    cli()