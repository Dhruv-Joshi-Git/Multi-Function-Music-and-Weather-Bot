import os
import requests
from discord import app_commands, Interaction
from dotenv import load_dotenv

load_dotenv()  # Loads your .env file into environment variables

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def add_weather_command(bot):
    @bot.tree.command(name="weather", description="Get weather info for a city.")
    @app_commands.describe(city="The city you want weather info for")
    async def weather(interaction: Interaction, city: str):
        await interaction.response.defer()
        
        # Construct the API URL with the city and API key
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        
        try:
            # Send the API request
            res = requests.get(url)
            
            # Check the status code of the response
            if res.status_code != 200:
                await interaction.followup.send(f" Error: {res.status_code}. Unable to fetch weather data.")
                return
            
            # Parse the response JSON
            data = res.json()

            # Check if the city was found
            if data.get("cod") != 200:
                await interaction.followup.send(f" City not found: {city}")
                return

            # Extract relevant information from the response
            name = data["name"]
            weather = data["weather"][0]["description"].capitalize()
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]

            # Create the message with weather info
            msg = (
                f"**🌤️ Weather in {name}**\n"
                f"📝 {weather}\n"
                f"🌡️ {temp}°C\n"
                f"💧 Humidity: {humidity}%\n"
                f"🌬️ Wind: {wind} m/s"
            )
            await interaction.followup.send(msg)

        except requests.exceptions.RequestException as e:
            # Handle any exceptions that occur with the request
            await interaction.followup.send(f" Error retrieving weather: {e}")
