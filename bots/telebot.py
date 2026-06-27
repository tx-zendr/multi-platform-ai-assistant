import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from backend.main import Gemini_Bot  # Your updated class with database support
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


TOKEN = os.getenv("Telebot")
gemini_api_key = os.getenv("gemini_api_key")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# /start handler
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Hi, I am NEET Exam Helper Bot 🤖\nUse /help to see what I can do!")

# /help handler
@dp.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer(
        "Hi, I am NEET Exam Helper Bot 🤖\n\n"
        "/help: for help\n"
        "/start: to Start the Bot\n"
        "/clear: to Clear Past Conversation"
    )

# /clear handler (Updated to clear messages for this user session if needed)
@dp.message(Command("clear"))
async def clear_handler(message: types.Message):
    from database.connection import BotDatabase
    db = BotDatabase()
    result_message = db.clear()
    await message.answer(result_message)
# Main message handler for text and media

@dp.message()
async def echo_handler(message: types.Message):
    # Set fallback prompt text if a user uploads file with no text caption
    text_prompt = message.text or message.caption or "Analyze this file"
    image_path = None
    audio_path = None
    pdf_path = None

    # 1. Download files locally to pass to Gemini API File Manager
    if message.photo:
        largest_photo = message.photo[-1]
        file_info = await bot.get_file(largest_photo.file_id)
        destination = f"temp_{largest_photo.file_id}.jpg"
        await bot.download_file(file_info.file_path, destination=destination)
        image_path = destination

    elif message.audio:
        file_info = await bot.get_file(message.audio.file_id)
        destination = f"temp_{message.audio.file_id}.mp3"
        await bot.download_file(file_info.file_path, destination=destination)
        audio_path = destination

    elif message.document and message.document.mime_type == "application/pdf":
        file_info = await bot.get_file(message.document.file_id)
        destination = f"temp_{message.document.file_id}.pdf"
        await bot.download_file(file_info.file_path, destination=destination)
        pdf_path = destination

    # 2. Process query via the unified DB-backed Gemini wrapper
    try:
        bot_instance = Gemini_Bot(
            text=text_prompt, 
            image=image_path, 
            audio=audio_path, 
            pdf=pdf_path
        )
        
        # Generates text content, fetches past DB turns, and commits logs automatically
        response_text = bot_instance.generate(type="NEET Helper Telegram Bot")
        await message.answer(response_text)
        
    except Exception as e:
        await message.answer("Sorry, I ran into an error processing that request.")
        print(f"Error generating response: {e}")
        
    finally:
        # 3. Cleanup local system files immediately 
        for path in [image_path, audio_path, pdf_path]:
            if path and os.path.exists(path):
                os.remove(path)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())