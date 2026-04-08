from google.adk.tools import AgentTool
from pydantic import BaseModel, Field
from typing import Optional
import httpx
import logging

logger = logging.getLogger(__name__)

class WeatherInput(BaseModel):
    user_id: str = Field(description="The internal user ID to lookup default location if missing")
    location: Optional[str] = Field(None, description="The location mentioned in the user prompt, e.g. 'Paris', 'New York', 'London'. If not mentioned, set to None.")

class WeatherTool(AgentTool):
    """
    AgentTool representing the Weather Service.
    Wraps the Open-Meteo API. If location is not provided, queries AlloyDB (via MCP Toolbox hypothetically)
    for the user's default location fallback.
    """
    
    @property
    def name(self) -> str:
        return "weather_service"

    @property
    def description(self) -> str:
        return "Fetches current weather for a specified location. If location is missing, it will lookup user profile defaults."

    @property
    def schema(self) -> type[BaseModel]:
        return WeatherInput

    async def execute(self, inputs: WeatherInput) -> str:
        location = inputs.location
        if not location:
            # Fallback to database logic
            logger.info(f"No location provided. Defaulting to Profile location for user: {inputs.user_id}")
            # Here we would normally hit the AlloyDB tools via `mcp_manager`
            # For the MVP logic stub, let's assume we retrieved "Seattle" from DB
            location = "Seattle"
        
        try:
            # We mock the geocoding step for MVP efficiency and directly hit Open-Meteo with hardcoded coordinates
            # if we wanted a real dynamic response, we'd do a Geocoding API lookup first.
            lat, lon = 47.6062, -122.3321  # Default Seattle coordinates
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
            weather = data.get("current_weather", {})
            return f"Weather for '{location}': {weather.get('temperature')}°C, Wind: {weather.get('windspeed')} km/h"
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return f"Could not fetch weather data for {location}."
