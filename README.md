# Multi-Function-Music-and-Weather-Bot
A simple multifunctional Discord bot that integrates music playback, weather updates, and ChatGPT capabilities. This bot allows you to interact with a variety of features such as playing music from YouTube, fetching real-time weather data, and chatting with OpenAI’s GPT-3.

## Features:
- **Weather Command**: Get current weather details like temperature, humidity, wind speed, and description for any city using `/weather`.
- **Modular Design**: Easily extendable and clean structure.
- **Slash Commands**: Uses Discord's modern slash command system for a better user experience.
- **Environment Variables**: Secure handling of API keys via `.env` file.

## Requirements:
Before getting started, ensure you have the following:
- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **FFmpeg** - Required for music playback functionality. [Download FFmpeg](https://ffmpeg.org/download.html)
- **Discord Developer Token** - [Create a Discord bot](https://discord.com/developers/applications) through the Discord Developer Portal.
- **OpenAI API Key** - [Get your API key from OpenAI](https://platform.openai.com/account/api-keys).
- **OpenWeather API Key** - [Sign up for an API key from OpenWeatherMap](https://openweathermap.org/api).

## PowerShell Dependencies:
Run the following commands to install the required dependencies, but not limited too:
- pip install discord.py
- pip install yt-dlp
- pip install openai
- pip install requests
- pip install python-dotenv

Setup Environment Variables: Create a .env file in the root directory of the project and add the following variables with your respective API keys

Commands: After fully integrating the bot into your system, run the main.py file and it will give you access to the following:
- /hello: Greet the bot with a friendly "hello!"
- /ask: Ask ChatGPT anything and get a response.
- /change nickname: Change your Discord nickname (if permitted).
- /weather <city>: Get real-time weather for any city
Music Commands
- /join: The bot joins your voice channel.
- /leave: The bot leaves your voice channel.
- /play <url>: Play a song from a YouTube URL.
- /skip: Skip the current song.
- /pause: Pause the current song.
- /resume: Resume the song if it's paused.
- /stop: Stop the music and clear the queue.
- /queue: View the current music queue.

Summary: Getting Started

To set up this Discord bot, you should be familiar with the Discord Developer Portal for creating a bot and enabling required intents. You'll also need basic knowledge of environment variables using a .env file to securely store your Discord token, OpenAI key, and OpenWeather API key. This bot uses asynchronous Python (async/await), so understanding async patterns is helpful. Make sure FFmpeg is installed for music playback, and be comfortable using pip to install dependencies. Basic experience with REST APIs and handling JSON is useful for the ChatGPT and weather features. Finally, ensure you’ve signed up for OpenAI and OpenWeather to obtain API keys.

I have provided my code files above! 


