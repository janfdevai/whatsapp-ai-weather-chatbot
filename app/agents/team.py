from langgraph.checkpoint.memory import InMemorySaver

from app.agents.chatbot_agent.graph import chatbot_agent_builder


def compile_agent(builder, memory):
    """Compile the agent using the provided builder and memory"""
    return builder.compile(checkpointer=memory)


chatbot_agent = compile_agent(chatbot_agent_builder, InMemorySaver())
