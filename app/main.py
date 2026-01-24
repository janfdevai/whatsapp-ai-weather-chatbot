from fastapi import BackgroundTasks, FastAPI, Request, Response

from app.chanels.whatsapp import Subscription, process_request, verify_subscription

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello WhatsApp Webhook"}


@app.get("/webhook")
async def verify_webhook(suscription: Subscription):
    """Handshake for Meta to verify your server."""
    verify_subscription(suscription)
    return Response(status_code=403)


@app.post("/webhook")
async def handle_message(request: Request, background_tasks: BackgroundTasks):
    """Receives incoming messages and sends a reply."""
    await process_request(request, background_tasks)
    return {"status": "success"}
