import operator

from langchain.messages import AnyMessage
from typing_extensions import Annotated, TypedDict

from app.agents.chatbot_agent.utils import merge_user


class UserState(TypedDict):
    name: str
    phone_number: str


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user: Annotated[UserState, merge_user]
    llm_calls: int
