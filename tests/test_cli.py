import json
import logging
import os
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from personal_mcp.cli import cli


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_config_dir(tmp_path):
    """Create a temporary config directory."""
    return tmp_path / "config"


def test_cli_help(cli_runner):
    """Test CLI help command."""
    result = cli_runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Personal MCP Server" in result.output
    assert "run" in result.output
    assert "dev" in result.output
    assert "inspect" in result.output
    assert "install" in result.output


@patch("personal_mcp.cli.PersonalMCP")
def test_cli_run(mock_personal_mcp, cli_runner, temp_db_path):
    """Test CLI run command."""
    mock_server = MagicMock()
    mock_personal_mcp.return_value = mock_server

    result = cli_runner.invoke(cli, ["run", "--name", "Test Server", "--db-path", temp_db_path])

    assert result.exit_code == 0
    mock_personal_mcp.assert_called_once_with(name="Test Server", db_path=temp_db_path)
    mock_server.run.assert_called_once()


@patch("personal_mcp.cli.PersonalMCP")
def test_cli_dev_fallback(mock_personal_mcp, cli_runner, temp_db_path):
    """Test CLI dev command falls back to normal mode when development server is unavailable."""
    mock_server = MagicMock()
    mock_personal_mcp.return_value = mock_server

    result = cli_runner.invoke(cli, ["dev", "--name", "Test Server", "--db-path", temp_db_path])

    assert result.exit_code == 0
    assert "Development server not available" in result.output
    mock_server.run.assert_called_once()


@patch("personal_mcp.cli.PersonalMCP")
def test_cli_inspect_fallback(mock_personal_mcp, cli_runner, temp_db_path):
    """Test CLI inspect command falls back to normal mode when inspector is unavailable."""
    mock_server = MagicMock()
    mock_personal_mcp.return_value = mock_server

    result = cli_runner.invoke(cli, ["inspect", "--name", "Test Server", "--db-path", temp_db_path])

    assert result.exit_code == 0
    assert "Inspector not available" in result.output
    mock_server.run.assert_called_once()


def test_cli_install(cli_runner, tmp_path):
    """Test CLI install command."""
    # Create mock config files
    config_dir = tmp_path / "Library" / "Application Support" / "Claude"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "claude_desktop_config.json"

    mock_config = {"mcpServers": {}}
    config_file.write_text(json.dumps(mock_config))

    with patch.dict(os.environ, {"HOME": str(tmp_path)}):
        result = cli_runner.invoke(cli, ["install", "--claude-desktop", "--name", "Test Server"])

    assert result.exit_code == 0
    assert "Successfully installed" in result.output

    # Verify configuration was updated
    config = json.loads(config_file.read_text())
    assert "personal-mcp" in config["mcpServers"]
    assert config["mcpServers"]["personal-mcp"]["command"] == "personal-mcp"
    assert "--name" in config["mcpServers"]["personal-mcp"]["args"]
    assert "Test Server" in config["mcpServers"]["personal-mcp"]["args"]


@patch("personal_mcp.cli.PersonalMCP")
def test_cli_verbose_logging(mock_personal_mcp, cli_runner, temp_db_path):
    """Test verbose logging option."""
    mock_server = MagicMock()
    mock_personal_mcp.return_value = mock_server

    with patch("personal_mcp.cli.logging.basicConfig") as mock_basic_config:
        result = cli_runner.invoke(
            cli, ["--verbose", "run", "--name", "Test Server", "--db-path", temp_db_path]
        )

        assert result.exit_code == 0
        assert mock_basic_config.call_args.kwargs["level"] == logging.DEBUG


@patch("personal_mcp.cli.PersonalMCP")
def test_cli_config_handling(mock_personal_mcp, cli_runner, mock_config_dir):
    """Test configuration file handling."""
    mock_server = MagicMock()
    mock_personal_mcp.return_value = mock_server

    mock_config_dir.mkdir(parents=True)
    config_file = mock_config_dir / "config.json"

    # Test with non-existent config
    with patch("personal_mcp.cli.get_config_dir", return_value=mock_config_dir):
        result = cli_runner.invoke(cli, ["run", "--name", "Test Server"])
        assert result.exit_code == 0
        mock_server.run.assert_called_once()

    # Test with existing config
    config = {"default_name": "Custom Server", "default_db_path": "custom.db"}
    config_file.write_text(json.dumps(config))

    with patch("personal_mcp.cli.get_config_dir", return_value=mock_config_dir):
        result = cli_runner.invoke(cli, ["run"])
        assert result.exit_code == 0
        assert mock_server.run.call_count == 2


def test_cli_error_handling(cli_runner):
    """Test CLI error handling."""
    # Test with invalid command
    result = cli_runner.invoke(cli, ["invalid-command"])
    assert result.exit_code != 0
    assert "Error" in result.output or "No such command" in result.output
