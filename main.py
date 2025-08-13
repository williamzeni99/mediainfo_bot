import imdb
import os
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, InlineQueryHandler
from dotenv import load_dotenv
import logging
import uuid

logger = logging.getLogger("logger")

# Load environment variables from .env file
load_dotenv()

# read the Telegram bot token from environment variable
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is not set.")


app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome to the IMDb Bot! Use @mediajellyinfoer_bot <media_name> to get inline suggestions.")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query
    if not query:
        return
    
    # Create IMDb instance
    ia = imdb.IMDb()
    
    try:
        # Search for movies/shows
        search_results = ia.search_movie(query, results=1)
        results = []
        
        for movie in search_results:
            # Get basic movie info
            title = movie.get('canonical title', 'Unknown Title')
            year = movie.get('year', 'Unknown Year')
            kind = movie.get('kind', 'Unknown')
            cover = movie.get('full-size cover url', "Unknown" )
            
            # print(movie.asXML())
            # Create result item
            result = InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"{title} ({year})",
                description=f"{kind.title()}",
                input_message_content=InputTextMessageContent(
                    message_text=f"🎬 *{title}* ({year})\n"
                                f"Type: {kind.title()}\n"
                                f"IMDb ID: {movie.movieID}\n"
                                f"cover: {cover}",
                    # parse_mode='Markdown'
                )
            )
            results.append(result)
        
        await update.inline_query.answer(results, cache_time=300)
        
    except Exception as e:
        logger.error(f"Error in inline query: {e}")
        # Return empty results on error
        await update.inline_query.answer([])

app.add_handler(CommandHandler("start", start))
app.add_handler(InlineQueryHandler(callback=inline_query))



app.run_polling()


