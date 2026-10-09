"""
Test script for the turn logger module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Log.turn_logger import (
    TurnRecord, format_turn, begin_turn, end_turn,
    add_tool_call, add_tool_message, add_usage, set_agent_output,
    get_current_turn
)

def test_format_turn_basic():
    """Test formatting a basic turn with no tools."""
    record = TurnRecord(
        count=1,
        user_input="Hello, world!",
        started_at=0.0,
        agent_output="Hello! How can I help you today?",
        input_tokens=10,
        output_tokens=15,
        total_tokens=25,
        duration_s=1.5,
        model_name="test-model"
    )
    
    formatted = format_turn(record)
    print("=== Test: Basic Turn ===")
    print(formatted)
    print()
    
    assert "UserInputCount : 1" in formatted
    assert "UserInput      : Hello, world!" in formatted
    assert "Tool Calls     : none" in formatted
    assert "ToolMessage    : none" in formatted
    assert "AgentOutput    : Hello! How can I help you today?" in formatted
    assert "Input Tokens       : 10" in formatted
    assert "Output Tokens      : 15" in formatted
    assert "Total Tokens       : 25" in formatted
    assert "Tokens / Second    : 10.00" in formatted  # 15 / 1.5
    assert "Total Duration     : 1.50s" in formatted
    assert "Model Name         : test-model" in formatted
    print("✓ Basic turn test passed\n")


def test_format_turn_with_tools():
    """Test formatting a turn with tool calls and messages."""
    record = TurnRecord(
        count=2,
        user_input="What's the weather like?",
        started_at=0.0,
        tool_calls=[
            {"name": "get_weather", "args": {"location": "New York"}}
        ],
        tool_messages=[
            {"name": "get_weather", "result": "Sunny, 72°F"}
        ],
        agent_output="It's sunny and 72°F in New York.",
        input_tokens=50,
        output_tokens=30,
        total_tokens=80,
        duration_s=2.0,
        model_name="test-model"
    )
    
    formatted = format_turn(record)
    print("=== Test: Turn with Tools ===")
    print(formatted)
    print()
    
    assert "UserInputCount : 2" in formatted
    assert "Tool Calls     : get_weather({\"location\": \"New York\"})" in formatted
    assert "ToolMessage    : get_weather -> Sunny, 72°F" in formatted
    print("✓ Turn with tools test passed\n")


def test_format_turn_missing_tokens():
    """Test formatting with missing token data (n/a)."""
    record = TurnRecord(
        count=3,
        user_input="Test missing tokens",
        started_at=0.0,
        agent_output="Response without token data",
        input_tokens=None,
        output_tokens=None,
        total_tokens=None,
        duration_s=None,
        model_name=""
    )
    
    formatted = format_turn(record)
    print("=== Test: Missing Token Data ===")
    print(formatted)
    print()
    
    assert "Input Tokens       : n/a" in formatted
    assert "Output Tokens      : n/a" in formatted
    assert "Total Tokens       : n/a" in formatted
    assert "Tokens / Second    : 0.00" in formatted
    assert "Total Duration     : 0.00s" in formatted
    assert "Model Name         : n/a" in formatted
    print("✓ Missing token data test passed\n")


def test_format_turn_long_tool_result():
    """Test truncation of long tool results."""
    long_result = "x" * 3000
    record = TurnRecord(
        count=4,
        user_input="Test long result",
        started_at=0.0,
        tool_messages=[
            {"name": "big_tool", "result": long_result}
        ],
        agent_output="Done",
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
        duration_s=1.0,
        model_name="test-model"
    )
    
    formatted = format_turn(record)
    print("=== Test: Long Tool Result Truncation ===")
    print(formatted)
    print()
    
    assert "[truncated" in formatted
    assert "1000 chars" in formatted  # 3000 - 2000 = 1000 truncated
    print("✓ Long tool result truncation test passed\n")


def test_format_turn_with_error():
    """Test formatting a turn with an error."""
    record = TurnRecord(
        count=5,
        user_input="Test error",
        started_at=0.0,
        agent_output="Partial response",
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
        duration_s=1.0,
        model_name="test-model",
        error="Connection timeout"
    )
    
    formatted = format_turn(record)
    print("=== Test: Turn with Error ===")
    print(formatted)
    print()
    
    assert "Error            : Connection timeout" in formatted
    print("✓ Turn with error test passed\n")


def test_integration():
    """Test the full integration flow."""
    print("=== Test: Integration Flow ===")
    
    # Begin turn
    turn = begin_turn(1, "Test integration")
    assert turn.count == 1
    assert turn.user_input == "Test integration"
    
    # Add tool call
    add_tool_call("test_tool", {"param": "value"})
    
    # Add tool message
    add_tool_message("test_tool", "Tool result")
    
    # Add usage
    add_usage(100, 50, 150, 2.5, "test-model")
    
    # Set agent output
    set_agent_output("Integration test complete")
    
    # End turn and get formatted output
    formatted = end_turn()
    
    print(formatted)
    print()
    
    assert "UserInputCount : 1" in formatted
    assert "Tool Calls     : test_tool({\"param\": \"value\"})" in formatted
    assert "ToolMessage    : test_tool -> Tool result" in formatted
    assert "AgentOutput    : Integration test complete" in formatted
    assert "Input Tokens       : 100" in formatted
    assert "Output Tokens      : 50" in formatted
    assert "Total Tokens       : 150" in formatted
    assert "Model Name         : test-model" in formatted
    
    # Verify turn is cleared
    assert get_current_turn() is None
    print("✓ Integration flow test passed\n")


def test_accumulate_usage():
    """Test that usage accumulates across multiple calls."""
    print("=== Test: Accumulate Usage ===")
    
    turn = begin_turn(1, "Test accumulate")
    
    # First LLM call
    add_usage(100, 50, 150, 1.0, "model-1")
    
    # Second LLM call in same turn
    add_usage(200, 75, 275, 1.5, "model-1")
    
    set_agent_output("Done")
    formatted = end_turn()
    
    print(formatted)
    print()
    
    assert "Input Tokens       : 300" in formatted  # 100 + 200
    assert "Output Tokens      : 125" in formatted  # 50 + 75
    assert "Total Tokens       : 425" in formatted  # 150 + 275
    assert "Total Duration     : 2.50s" in formatted  # 1.0 + 1.5
    print("✓ Accumulate usage test passed\n")


if __name__ == "__main__":
    test_format_turn_basic()
    test_format_turn_with_tools()
    test_format_turn_missing_tokens()
    test_format_turn_long_tool_result()
    test_format_turn_with_error()
    test_integration()
    test_accumulate_usage()
    
    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)