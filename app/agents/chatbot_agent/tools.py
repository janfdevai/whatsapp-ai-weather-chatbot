from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command


@tool
def get_user_phone_number(runtime: ToolRuntime) -> str:
    """Get the user's phone number."""

    return runtime.state.get("user", {}).get("phone_number", "unknown")


@tool
def get_user_name(runtime: ToolRuntime) -> str:
    """Get the name of the user"""
    return runtime.state.get("user", {}).get("name", "unknown")


@tool
def update_user_name(user_name: str, runtime: ToolRuntime) -> Command:
    """Update the name of the user in the state once they've revealed it."""
    return Command(
        update={
            "user": {"name": user_name},
            "messages": [
                ToolMessage(
                    "Successfully updated user name",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


tools = [get_user_phone_number, get_user_name, update_user_name]
