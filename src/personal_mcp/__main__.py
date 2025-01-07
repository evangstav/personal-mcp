from .cli import cli

def main():
    """Main entry point for the Personal MCP server."""
    cli(auto_envvar_prefix="PERSONAL_MCP")

if __name__ == "__main__":
    main()
