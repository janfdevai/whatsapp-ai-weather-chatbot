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


async def send_whatsapp_text_message(to_number: str, text: str):
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text},
    }

    await client.post(url, json=payload, headers=headers)


async def send_whatsapp_image_message(to_number: str, answer, image_path: str):
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "image",
        "image": {
            "link": "https://static.vecteezy.com/vite/assets/photo-masthead-375-BoK_p8LG.webp",
            "caption": answer,
        },
    }

    await client.post(url, json=payload, headers=headers)


async def process_message_type(message) -> str:
    if "text" in message:
        return message["text"]["body"]
    elif "location" in message:
        return str(message["location"])

    return "message not precessed"


async def run_agent_and_send_reply(message, from_number):
    """
    All slow operations happen here, safely away from the Meta Webhook timeout.
    """
    message_id = message.get("id")
    try:
        # Do these inside the background task to save time in the main thread
        await mark_message_as_read(message_id)
        message_content = await process_message_type(message)

        # 1. Wait for the slow LLM
        response = await chatbot_agent.ainvoke(
            {
                "messages": [{"role": "user", "content": message_content}],
                "user": {"phone_number": from_number},
            },
            {"configurable": {"thread_id": from_number}},
        )

        print("MODEL RESPONSE: ", response)

        answer = response["messages"][-1].content

        # 2. Send the message
        if response.get("image_path"):
            await send_whatsapp_image_message(
                from_number, "This should be a Image", response.get("image_path")
            )
        else:
            await send_whatsapp_text_message(from_number, answer)
    except Exception as e:
        print(f"Error in background task: {e}")
        await send_whatsapp_text_message(
            from_number, "Agent is not available right now. Please try again later."
        )


async def process_request(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()

    try:
        entry = data["entry"][0]["changes"][0]["value"]
        if "messages" in entry:
            print("ENTRY", entry)

            message = entry["messages"][0]

            from_number = remove_extra_one(message["from"])

            # IMMEDIATELY hand off to background task
            background_tasks.add_task(run_agent_and_send_reply, message, from_number)

        # ALWAYS return 200 OK immediately
        return {"status": "accepted"}

    except Exception as e:
        print(f"Error: {e}")
        await send_whatsapp_text_message(
            from_number, "Agent is not available right now. Please try again later."
        )

        # Still return 200 so Meta stops retrying the "bad" payload
        return {"status": "error", "message": str(e)}
