from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai import OpenAI
import base64
import os

# Initialize OpenAI client using environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to handle incoming photos
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Reply immediately to confirm receipt
        await update.message.reply_text("✅ Screenshot received, analyzing...")

        # Get the highest-resolution photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        path = await file.download_to_drive()

        # Convert image to base64
        with open(path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()

        # Ask OpenAI to analyze the chart
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this stock chart and tell me BUY, SELL, or HOLD with explanation."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }]
        )

        # Send OpenAI reply to Telegram
