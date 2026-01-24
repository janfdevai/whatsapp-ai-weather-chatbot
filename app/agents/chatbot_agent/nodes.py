from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from app.agents.chatbot_agent.state import MessagesState
from app.agents.chatbot_agent.tools import tools

model = init_chat_model("openai:gpt-5-nano", temperature=0)
model_with_tools = model.bind_tools(tools)


def llm_call(state: MessagesState):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            model_with_tools.invoke(
                [SystemMessage(content="You are a helpful assistant.")]
                + state["messages"]
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


tool_node = ToolNode(tools)
