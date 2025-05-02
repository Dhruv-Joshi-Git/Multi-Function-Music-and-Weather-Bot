# Import the required libraries 
import discord # Discord API lib
from discord.ext import commands # Import bot commands
from discord import app_commands # Import slash comands
import yt_dlp                    # Import youtube audio
from openai import OpenAI        # Gives access to OpenAI client
import os                        # Access API keys
from dotenv import load_dotenv   # Import from .env fle
from weather import add_weather_command # Weather command function

# Load .env
load_dotenv()  # Loads variables like DISCORD_TOKEN and OPENAI_API_KEY
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Instantiate OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.guilds = True
intents.presences = True

# Create class for commands
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.music_queue = {}  # {guild.id: [(title, url)]}

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced.")

    async def on_ready(self):
        print(f'Logged on as {self.user} (ID: {self.user.id})')

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Hello message
        if message.content.startswith('hello'):
            await message.channel.send(f'Hi there! {message.author}')

        # ChatGPT message command
        elif message.content.startswith("!ask"):
            prompt = message.content[5:].strip()

            if not prompt:
                await message.channel.send("Please provide a prompt after !ask.")
                return

            await message.channel.send("Thinking...")

            try:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                reply = response.choices[0].message.content
                await message.channel.send(reply)
            except Exception as e:
                await message.channel.send(f"❌ Error: {e}")

    async def on_message_edit(self, before, after):
        if before.author != self.user:
            await before.channel.send(f'Message edited:\n**Before:** {before.content}\n**After:** {after.content}')

    async def on_message_delete(self, message):
        if message.author != self.user:
            await message.channel.send(f'Message deleted from {message.author}: {message.content}')

    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.text_channels, name="general")
        if channel:
            await channel.send(f'👋 Welcome to the server, {member.mention}!')

    async def on_member_remove(self, member):
        channel = discord.utils.get(member.guild.text_channels, name="general")
        if channel:
            await channel.send(f'👋 {member} has left the server.')

    async def on_member_update(self, before, after):
        channel = discord.utils.get(after.guild.text_channels, name="general")
        if before.nick != after.nick:
            await channel.send(f'{before.name} changed nickname to {after.nick}')
        elif before.roles != after.roles:
            await channel.send(f'{before.name} updated their roles.')

    async def on_guild_join(self, guild):
        print(f'✅ Joined a new guild: {guild.name}')

    async def on_guild_remove(self, guild):
        print(f'❌ Removed from guild: {guild.name}')

    async def on_reaction_add(self, reaction, user):
        if user != self.user:
            await reaction.message.channel.send(f'{user} reacted with {reaction.emoji}')

    async def on_reaction_remove(self, reaction, user):
        if user != self.user:
            await reaction.message.channel.send(f'{user} removed their {reaction.emoji} reaction')

    async def play_next_song(self, interaction):
        guild_id = interaction.guild.id
        if guild_id not in self.music_queue or not self.music_queue[guild_id]:
            vc = interaction.guild.voice_client
            if vc:
                await vc.disconnect()
            return

        next_song = self.music_queue[guild_id].pop(0)
        title, audio_url = next_song

        vc = interaction.guild.voice_client
        if vc:
            source = discord.FFmpegPCMAudio(audio_url)
            vc.play(source, after=lambda e: self.loop.create_task(self.play_next_song(interaction)))
# Assigning bot MyBot class  
bot = MyBot()


# Slash Commands

# Greeting
@bot.tree.command(name="hello", description="Say hello to the bot!")
async def hello_command(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hi there, {interaction.user.mention}! 👋")

# Add the weather command from your external module (weather.py)
add_weather_command(bot)

@bot.tree.command(name="change_nick", description="Change your nickname.")
@app_commands.describe(nickname="The new nickname you want to set")
async def change_nick(interaction: discord.Interaction, nickname: str):
    member = interaction.guild.get_member(interaction.user.id)
    bot_member = interaction.guild.me
    bot_top_role = bot_member.top_role
    user_top_role = member.top_role

    if not bot_member.guild_permissions.manage_nicknames:
        await interaction.response.send_message(" I don't have permission to manage nicknames.", ephemeral=True)
        return
    if user_top_role >= bot_top_role:
        await interaction.response.send_message(" I can't change your nickname due to role hierarchy.", ephemeral=True)
        return

    try:
        await member.edit(nick=nickname)
        await interaction.response.send_message(f" Your nickname was changed to **{nickname}**!")
    except discord.Forbidden:
        await interaction.response.send_message(" I can't change your nickname due to permission issues (Forbidden).", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f" Something went wrong: {e}", ephemeral=True)

@bot.tree.command(name="ask", description="Ask ChatGPT anything!")
@app_commands.describe(prompt="Your question or message for ChatGPT")
async def ask(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content
        await interaction.followup.send(reply)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")


# Voice / Music Commands

@bot.tree.command(name="join", description="Bot joins the voice channel.")
async def join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message(" You are not connected to a voice channel.", ephemeral=True)
        return
    channel = interaction.user.voice.channel
    await channel.connect()
    await interaction.response.send_message(f" Joined {channel.name}!")

@bot.tree.command(name="leave", description="Bot leaves the voice channel.")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message(" Disconnected from the voice channel.")
    else:
        await interaction.response.send_message(" I'm not connected to a voice channel.", ephemeral=True)

@bot.tree.command(name="play", description="Play a song from YouTube URL.")
@app_commands.describe(url="YouTube video URL")
async def play(interaction: discord.Interaction, url: str):
    await interaction.response.defer()

    if not interaction.user.voice:
        await interaction.followup.send(" You are not connected to a voice channel.", ephemeral=True)
        return

    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info.get('title', 'Unknown Title')
    except Exception as e:
        await interaction.followup.send(f" Error extracting audio: {e}")
        return

    guild_id = interaction.guild.id
    if guild_id not in bot.music_queue:
        bot.music_queue[guild_id] = []

    bot.music_queue[guild_id].append((title, audio_url))

    vc = interaction.guild.voice_client
    if not vc.is_playing():
        await bot.play_next_song(interaction)
        await interaction.followup.send(f" Now playing: **{title}**")
    else:
        await interaction.followup.send(f" Added to queue: **{title}**")

@bot.tree.command(name="queue", description="Show the current music queue.")
async def show_queue(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    if guild_id not in bot.music_queue or not bot.music_queue[guild_id]:
        await interaction.response.send_message(" The queue is currently empty.")
        return

    description = "\n".join([f"{idx+1}. {title}" for idx, (title, _) in enumerate(bot.music_queue[guild_id])])
    await interaction.response.send_message(f" **Current Queue:**\n{description}")

@bot.tree.command(name="skip", description="Skip the current song.")
async def skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_playing():
        await interaction.response.send_message("Nothing is playing.", ephemeral=True)
        return

    vc.stop()
    await interaction.response.send_message("Skipped the song!")

@bot.tree.command(name="pause", description="Pause the current song.")
async def pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_playing():
        await interaction.response.send_message("Nothing is playing to pause.", ephemeral=True)
        return
    vc.pause()
    await interaction.response.send_message("Paused the song!")

@bot.tree.command(name="resume", description="Resume the paused song.")
async def resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_paused():
        await interaction.response.send_message("Nothing is paused to resume.", ephemeral=True)
        return
    vc.resume()
    await interaction.response.send_message("Resumed the song!")

@bot.tree.command(name="stop", description="Stop playing music and clear the queue.")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    guild_id = interaction.guild.id

    if not vc or not vc.is_connected():
        await interaction.response.send_message("I'm not connected to a voice channel.", ephemeral=True)
        return

    # Stop playing if necessary
    if vc.is_playing() or vc.is_paused():
        vc.stop()

    # Clear the queue
    if guild_id in bot.music_queue:
        bot.music_queue[guild_id] = []

    # Respond before disconnecting to avoid bot logic error loop
    await interaction.response.send_message("Stopped the music, cleared the queue, and disconnecting...")

    # disconnect
    await vc.disconnect()

# Run the bot

if __name__ == "__main__":
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("❌ Invalid token. Please check your bot token.")
    except discord.HTTPException as http_err:
        print(f"❌ HTTP error occurred: {http_err}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
