import json
from datetime import datetime
import pytest
from personal_mcp.models import Workout, Meal, JournalEntry
from mcp.server.fastmcp.exceptions import ToolError, ResourceError

@pytest.mark.asyncio
async def test_workout_tools(server, sample_workout):
    """Test workout-related MCP tools."""
    # Test log_workout tool
    workout = Workout(**sample_workout)
    result = await server.mcp.call_tool("log_workout", {"workout": workout.model_dump()})
    assert isinstance(result, list)
    assert "Logged workout" in result[0].text
    
    # Test calculate_training_weights tool
    params = {
        "exercise": "Bench Press",
        "base_weight": 200,
        "days_since_surgery": 90,
        "recent_pain_level": 2,
        "recent_rpe": 7
    }
    result = await server.mcp.call_tool("calculate_training_weights", params)
    weights = json.loads(result[0].text)
    assert "recommended_weight" in weights
    assert "recommended_reps" in weights
    assert weights["recommended_weight"] > 0

@pytest.mark.asyncio
async def test_nutrition_tools(server, sample_meal):
    """Test nutrition-related MCP tools."""
    # Test log_meal tool
    meal = Meal(**sample_meal)
    result = await server.mcp.call_tool("log_meal", {"meal": meal.model_dump()})
    assert isinstance(result, list)
    assert "Logged" in result[0].text
    assert "protein" in result[0].text
    
    # Test check_nutrition_targets tool
    today = datetime.now().strftime("%Y-%m-%d")
    result = await server.mcp.call_tool("check_nutrition_targets", {"date": today})
    targets = json.loads(result[0].text)
    assert "protein" in targets
    assert "calories" in targets
    assert "metrics" in targets

@pytest.mark.asyncio
async def test_journal_tools(server, sample_journal_entry):
    """Test journal-related MCP tools."""
    # Test add_journal_entry tool
    entry = JournalEntry(**sample_journal_entry)
    result = await server.mcp.call_tool("log_journal_entry", {"entry": entry.model_dump()})
    assert isinstance(result, list)
    assert "Added" in result[0].text
    
    # Test analyze_journal_entries tool
    today = datetime.now().strftime("%Y-%m-%d")
    params = {
        "start_date": today,
        "end_date": today
    }
    result = await server.mcp.call_tool("analyze_journal_entries", params)
    analysis = json.loads(result[0].text)
    assert "entry_count" in analysis
    assert "average_metrics" in analysis
    assert "trends" in analysis

@pytest.mark.asyncio
async def test_workout_history_resource(server, sample_workout):
    """Test workout history resource."""
    # Add sample workout with today's date
    workout = Workout(**sample_workout)
    workout.date = datetime.now().strftime("%Y-%m-%d")
    await server.mcp.call_tool("log_workout", {"workout": workout.model_dump()})
    
    # Test resource
    today = datetime.now().strftime("%Y-%m-%d")
    result = await server.mcp.read_resource(f"health://workout-history/{today}/{today}")
    result_text = result[0].text if isinstance(result, list) else result
    history = json.loads(result_text)
    assert len(history) > 0
    assert "exercise_name" in history[0]
    assert "weight" in history[0]

@pytest.mark.asyncio
async def test_nutrition_resource(server, sample_meal):
    """Test nutrition resource."""
    # Add sample meal with today's date
    meal = Meal(**sample_meal)
    meal.date = datetime.now().strftime("%Y-%m-%d")
    await server.mcp.call_tool("log_meal", {"meal": meal.model_dump()})
    
    # Test resource
    today = datetime.now().strftime("%Y-%m-%d")
    result = await server.mcp.read_resource(f"health://nutrition/{today}/{today}")
    result_text = result[0].text if isinstance(result, list) else result
    nutrition = json.loads(result_text)
    assert len(nutrition) > 0
    assert "food_name" in nutrition[0]
    assert "protein" in nutrition[0]
    assert "calories" in nutrition[0]

@pytest.mark.asyncio
async def test_journal_resource(server, sample_journal_entry):
    """Test journal entries resource."""
    # Add sample entry with today's date
    entry = JournalEntry(**sample_journal_entry)
    entry.date = datetime.now().strftime("%Y-%m-%d")
    await server.mcp.call_tool("log_journal_entry", {"entry": entry.model_dump()})
    
    # Test resource
    today = datetime.now().strftime("%Y-%m-%d")
    result = await server.mcp.read_resource(f"journal://entries/{today}/{today}")
    result_text = result[0].text if isinstance(result, list) else result
    entries = json.loads(result_text)
    assert len(entries) > 0
    assert "content" in entries[0]
    assert "tags" in entries[0]

@pytest.mark.asyncio
async def test_prompts(server):
    """Test MCP prompts."""
    prompts = await server.mcp.list_prompts()
    prompt_names = {p.name for p in prompts}
    assert "analyze_workout_load" in prompt_names
    assert "nutrition_recommendations" in prompt_names
    assert "journal_insights" in prompt_names
    
    # Test workout analysis prompt
    result = await server.mcp.get_prompt("analyze_workout_load", {"workout_history": "[]"})
    assert len(result.messages) > 0
    assert "analyze my recent workout history" in result.messages[0].content.text.lower()
    
    # Test nutrition recommendations prompt
    result = await server.mcp.get_prompt(
        "nutrition_recommendations",
        {"nutrition_log": "[]", "start_date": "2024-01-01", "end_date": "2024-01-07"}
    )
    assert len(result.messages) > 0
    assert "based on my meal logs" in result.messages[0].content.text.lower()
    
    # Test journal insights prompt
    result = await server.mcp.get_prompt("journal_insights", {"entries": "[]"})
    assert len(result.messages) > 0
    assert "analyze my journal entries" in result.messages[0].content.text.lower()

@pytest.mark.asyncio
async def test_error_handling(server):
    """Test error handling in MCP tools and resources."""
    # Test invalid workout data
    with pytest.raises(Exception):
        await server.mcp.call_tool("log_workout", {"workout": {}})
    
    # Test non-existent tool
    with pytest.raises(ToolError):
        await server.mcp.call_tool("non_existent_tool", {})
    
    # Test non-existent prompt
    with pytest.raises(Exception):
        await server.mcp.get_prompt("non_existent_prompt", {})
    
    # Test invalid resource URI
    with pytest.raises(Exception):
        await server.mcp.read_resource("invalid://resource/uri")
