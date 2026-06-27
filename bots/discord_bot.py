import os
import logging
import asyncio
import discord
from dotenv import load_dotenv

from backend.main import Gemini_Bot


# ----------------------------
# Load Environment Variables
# ----------------------------
load_dotenv()

DISCORD_TOKEN = os.getenv("Discord")

if not DISCORD_TOKEN:
    raise ValueError("Discord token not found in .env")


# ----------------------------
# Logging
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ----------------------------
# Discord Intents
# ----------------------------
intents = discord.Intents.default()
intents.message_content = True


# ----------------------------
# Discord Client
# ----------------------------
class MyClient(discord.Client):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create Gemini only once
        self.gemini = Gemini_Bot()

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    async def on_message(self, message):

        # Ignore all bots
        if message.author.bot:
            return

        # Ignore empty messages
        if not message.content and not message.attachments:
            return

        # Example command
        if message.content.startswith("$hello"):
            await message.channel.send("Hello!")
            return

        text = message.content.strip()

        image = None
        audio = None
        pdf = None

        try:
            # Read attachments
            for attachment in message.attachments:

                content_type = attachment.content_type or ""

                file_bytes = await attachment.read()

                if content_type.startswith("image/"):
                    image = file_bytes

                elif content_type.startswith("audio/"):
                    audio = file_bytes

                elif content_type == "application/pdf":
                    pdf = file_bytes

            # Generate AI response

            response = await asyncio.to_thread(self.gemini.generate,text=text,
                image=image,
                audio=audio,
                pdf=pdf,
                platform_user_id=str(message.author.id),username=message.author.name
            )

            await message.channel.send(response)

        except Exception as e:
            logger.exception("Error while processing message")

            await message.channel.send(
                "⚠️ Sorry, something went wrong."
            )


# ----------------------------
# Run Bot
# ----------------------------
client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)