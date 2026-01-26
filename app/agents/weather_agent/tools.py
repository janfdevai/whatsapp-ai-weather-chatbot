import os

import httpx
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command

from app import PROJECT_ROOT
from app.agents.weather_agent.utils import generate_weather_image

OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")


@tool
async def get_weather_by_city(city: str, runtime: ToolRuntime) -> Command | str:
    """Fetch weather data for a given city."""
    # Example: Access context if you want to use a default city or units
    # user_phone = runtime.context.user_phone_number

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": OPEN_WEATHER_API_KEY,
            "units": "metric",  # Standardize units
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            description = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            generate_weather_image(city, description)

            return Command(
                update={
                    "image_path": f"{PROJECT_ROOT}/public/weather_image.png",
                    "messages": [
                        ToolMessage(
                            f"The current weather in {city} is {description} with a temperature of {temp}°C.",
                            tool_call_id=runtime.tool_call_id,
                        )
                    ],
                }
            )

    except Exception as e:
        return f"Error fetching weather data: {e}"


@tool
async def get_weather_by_location(
    latitude: str, longitude: str, address: str = None, name: str = None
):
    """Fetch weather data for a given latitud and longitude."""
    # Example: Access context if you want to use a default city or units
    # user_phone = runtime.context.user_phone_number

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": OPEN_WEATHER_API_KEY,
            "units": "metric",  # Standardize units
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            description = data["weather"][0]["description"]
            temp = data["main"]["temp"]

            if address and name:
                return f"The current weather for {name} in the address {address}, is {description} with a temperature of {temp}°C."

            return f"The current weather of your current location, is {description} with a temperature of {temp}°C."

    except Exception as e:
        return f"Error fetching weather data: {e}"


@tool
def get_user_phone_number(runtime: ToolRuntime) -> str:
    """Get the user's phone number."""

    return runtime.state.get("user", {}).get("phone_number", "unknown")


@tool
def get_user_name(runtime: ToolRuntime) -> str:
    """Get the name of the user"""
    return runtime.state.get("user", {}).get("name", "unknown")


@tool
def update_user_name(user_name: str, runtime: ToolRuntime) -> Command:
    """Update the name of the user in the state once they've revealed it."""
    return Command(
        update={
            "user": {"name": user_name},
            "messages": [
                ToolMessage(
                    "Successfully updated user name",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


tools = [
    get_user_phone_number,
    get_user_name,
    update_user_name,
    get_weather_by_city,
    get_weather_by_location,
]
