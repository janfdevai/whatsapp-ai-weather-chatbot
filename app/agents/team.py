from langgraph.checkpoint.memory import InMemorySaver

from app.agents.weather_agent.graph import weather_agent_builder


def compile_agent(builder, memory):
    """Compile the agent using the provided builder and memory"""
    return builder.compile(checkpointer=memory)


weather_agent = compile_agent(weather_agent_builder, InMemorySaver())
