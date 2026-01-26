from fastapi import BackgroundTasks, Request, Response

from app.agents.team import weather_agent

from .client import (
    mark_message_as_read,
    send_whatsapp_image_message,
    send_whatsapp_text_message,
    upload_media,
)
from .config import VERIFY_TOKEN
from .models import Subscription
from .utils import process_message_type, remove_extra_one


def verify_subscription(subscription: Subscription):
    if subscription.mode == "subscribe" and subscription.token == VERIFY_TOKEN:
        return Response(content=subscription.challenge)


async def process_message_answer(response, from_number):
    answer = response["messages"][-1].content

    # 2. Send the message
    if response.get("image_path"):
        image_uploaded = await upload_media(response.get("image_path"))
        print("IMAGE UPLOADED: ", image_uploaded)
        media_id = image_uploaded.get("id")
        await send_whatsapp_image_message(from_number, answer, media_id)
    else:
        await send_whatsapp_text_message(from_number, answer)


async def run_agent_and_send_reply(message: dict, from_number: str):
    message_id = message.get("id")
    try:
        await mark_message_as_read(message_id)
        message_content = await process_message_type(message)

        response = await weather_agent.ainvoke(
            {
                "messages": [{"role": "user", "content": message_content}],
                "user": {"phone_number": from_number},
            },
            {"configurable": {"thread_id": from_number}},
        )

        await process_message_answer(response, from_number)
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
            message = entry["messages"][0]
            from_number = remove_extra_one(message["from"])
            background_tasks.add_task(run_agent_and_send_reply, message, from_number)
        return {"status": "accepted"}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}
