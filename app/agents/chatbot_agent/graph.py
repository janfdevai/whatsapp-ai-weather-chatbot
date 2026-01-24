from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import tools_condition

from app.agents.chatbot_agent.nodes import llm_call, tool_node
from app.agents.chatbot_agent.state import MessagesState

# Build workflow
chatbot_agent_builder = StateGraph(MessagesState)

# Add nodes
chatbot_agent_builder.add_node("llm_call", llm_call)
chatbot_agent_builder.add_node("tools", tool_node)

# Add edges to connect nodes
chatbot_agent_builder.add_edge(START, "llm_call")
chatbot_agent_builder.add_conditional_edges("llm_call", tools_condition, ["tools", END])
chatbot_agent_builder.add_edge("tools", "llm_call")
