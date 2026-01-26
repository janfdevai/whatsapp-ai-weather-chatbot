from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import tools_condition

from app.agents.weather_agent.nodes import llm_call, tool_node
from app.agents.weather_agent.state import MessagesState

# Build workflow
weather_agent_builder = StateGraph(MessagesState)

# Add nodes
weather_agent_builder.add_node("llm_call", llm_call)
weather_agent_builder.add_node("tools", tool_node)

# Add edges to connect nodes
weather_agent_builder.add_edge(START, "llm_call")
weather_agent_builder.add_conditional_edges("llm_call", tools_condition, ["tools", END])
weather_agent_builder.add_edge("tools", "llm_call")
