from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai import OpenAI
import base64
import os

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Handle incoming photos
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Confirm receipt
        await update.message.reply_text("✅ Screenshot received, analyzing...")

        # Get the highest resolution photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        path = await file.download_to_drive()

        # Convert image to base64
        with open(path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()

        # Ask OpenAI to analyze chart
        prompt_text = (
            "Analyze this stock chart and tell me BUY, SELL, or HOLD with explanation."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                    ]
                }
            ]
        )

        # Send OpenAI response
        await update.message.reply_text(response.choices[0].message.content)

    except Exception as e:
        # Catch errors and send to Telegram
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

# Create Telegram app
app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

# Add handler for photos
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# Run webhook for Render
app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 10000)),
    webhook_url=os.getenv("RENDER_URL")
)
