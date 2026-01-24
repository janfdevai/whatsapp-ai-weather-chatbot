import os

import httpx
from fastapi import BackgroundTasks, Query, Request, Response
from pydantic import BaseModel

from app.agents.team import chatbot_agent

timeout_config = httpx.Timeout(60.0, connect=10.0)
client = httpx.AsyncClient(timeout=timeout_config)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION")

url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
headers = {
    "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}


class Subscription(BaseModel):
    mode: str = (Query(None, alias="hub.mode"),)
    token: str = (Query(None, alias="hub.verify_token"),)
    challenge: str = (Query(None, alias="hub.challenge"),)


def verify_subscription(subscription: Subscription):
    if subscription.mode == "subscribe" and subscription.token == VERIFY_TOKEN:
        return Response(content=subscription.challenge)


def remove_extra_one(from_number: int) -> int:
    if "1" not in from_number[:2]:
        return from_number[:2] + from_number[3:]
    return from_number


async def mark_message_as_read(message_id: str):
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
        "typing_indicator": {"type": "text"},
    }
    await client.post(url, json=payload, headers=headers)


async def send_whatsapp_message(to_number: str, text: str):
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text},
    }

    await client.post(url, json=payload, headers=headers)


async def run_agent_and_send_reply(text_body, from_number, message_id):
    """
    All slow operations happen here, safely away from the Meta Webhook timeout.
    """
    try:
        # Do these inside the background task to save time in the main thread
        await mark_message_as_read(message_id)

        # 1. Wait for the slow LLM
        response = await chatbot_agent.ainvoke(
            {
                "messages": [{"role": "user", "content": text_body}],
                "user": {"phone_number": from_number},
            },
            {"configurable": {"thread_id": from_number}},
        )
        answer = response["messages"][-1].content

        # 2. Send the message
        await send_whatsapp_message(from_number, answer)
    except Exception as e:
        print(f"Error in background task: {e}")
        await send_whatsapp_message(
            from_number, "Agent is not available right now. Please try again later."
        )


async def process_request(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()

    try:
        entry = data["entry"][0]["changes"][0]["value"]
        if "messages" in entry:
            print("ENTRY", entry)

            message = entry["messages"][0]
            message_id = message.get("id")
            from_number = remove_extra_one(message["from"])
            text_body = message["text"]["body"]

            # IMMEDIATELY hand off to background task
            background_tasks.add_task(
                run_agent_and_send_reply, text_body, from_number, message_id
            )

        # ALWAYS return 200 OK immediately
        return {"status": "accepted"}

    except Exception as e:
        print(f"Error: {e}")
        await send_whatsapp_message(
            from_number, "Agent is not available right now. Please try again later."
        )

        # Still return 200 so Meta stops retrying the "bad" payload
        return {"status": "error", "message": str(e)}
