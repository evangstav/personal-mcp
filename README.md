# Personal MCP Server

[![smithery badge](https://smithery.ai/badge/personal-mcp)](https://smithery.ai/server/personal-mcp)

A Model Context Protocol server for personal health and well-being tracking. This server provides tools and resources for tracking workouts, nutrition, and daily journal entries, with AI-assisted analysis through Claude integration.

## Features

### Workout Tracking
- Log exercises, sets, and reps
- Track perceived effort and post-workout feelings
- Calculate safe training weights with rehabilitation considerations
- Historical workout analysis
- Shoulder rehabilitation support
- RPE-based load management

### Nutrition Management
- Log meals and individual food items
- Track protein and calorie intake
- Monitor hunger and satisfaction levels
- Daily nutrition targets and progress
- Pre/post workout nutrition tracking
- Meal timing analysis

### Journal System
- Daily entries with mood and energy tracking
- Sleep quality and stress level monitoring
- Tag-based organization
- Trend analysis and insights
- Correlation analysis between workouts, nutrition, and well-being
- Pattern recognition in mood and energy levels

## Installation

### Installing via Smithery

To install Personal Health Tracker for Claude Desktop automatically via [Smithery](https://smithery.ai/server/personal-mcp):

```bash
npx -y @smithery/cli install personal-mcp --client claude
```

### Prerequisites
- Python 3.10 or higher
- pip or uv package manager

### Using pip
```bash
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/yourusername/personal-mcp.git
cd personal-mcp
uv pip install -e ".[dev]"
```

## Usage

### Basic Server
Run the server with default settings:
```bash
personal-mcp run
```

### Development Mode
Run with hot reloading for development:
```bash
personal-mcp dev
```

### MCP Inspector
Debug with the MCP Inspector:
```bash
personal-mcp inspect
```

### Claude Desktop Integration
Install to Claude Desktop:
```bash
personal-mcp install --claude-desktop
```

### Configuration Options
```bash
personal-mcp --help
```

Available options:
- `--name`: Set server name (default: "Personal Assistant")
- `--db-path`: Specify database location
- `--dev`: Enable development mode
- `--inspect`: Run with MCP Inspector
- `-v, --verbose`: Enable verbose logging

## MCP Tools

### Workout Tools
```python
# Log a workout
workout = {
    "date": "2024-01-07",
    "exercises": [
        {
            "name": "Bench Press",
            "sets": [
                {"weight": 135, "reps": 10, "rpe": 7}
            ]
        }
    ],
    "perceived_effort": 8
}

# Calculate training weights
params = {
    "exercise": "Bench Press",
    "base_weight": 200,
    "days_since_surgery": 90,
    "recent_pain_level": 2,
    "recent_rpe": 7
}
```

### Nutrition Tools
```python
# Log a meal
meal = {
    "meal_type": "lunch",
    "foods": [
        {
            "name": "Chicken Breast",
            "amount": 200,
            "unit": "g",
            "protein": 46,
            "calories": 330
        }
    ],
    "hunger_level": 7,
    "satisfaction_level": 8
}

# Check nutrition targets
targets = await mcp.call_tool("check_nutrition_targets", {"date": "2024-01-07"})
```

### Journal Tools
```python
# Create a journal entry
entry = {
    "entry_type": "daily",
    "content": "Great workout today...",
    "mood": 8,
    "energy": 7,
    "sleep_quality": 8,
    "stress_level": 3,
    "tags": ["workout", "recovery"]
}

# Analyze entries
analysis = await mcp.call_tool("analyze_journal_entries", {
    "start_date": "2024-01-01",
    "end_date": "2024-01-07"
})
```

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=personal_mcp

# Run specific test file
pytest tests/test_database.py
```

### Code Quality
```bash
# Format code
black src/personal_mcp

# Lint code
ruff check src/personal_mcp

# Type checking
mypy src/personal_mcp
```

## Project Structure
```
personal-mcp/
├── src/
│   └── personal_mcp/
│       ├── tools/
│       │   ├── workout.py
│       │   ├── nutrition.py
│       │   └── journal.py
│       ├── database.py
│       ├── models.py
│       ├── resources.py
│       ├── prompts.py
│       └── server.py
├── tests/
│   ├── test_database.py
│   ├── test_server.py
│   └── test_cli.py
├── pyproject.toml
└── mcp.json
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
