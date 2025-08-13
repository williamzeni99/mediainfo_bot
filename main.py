import os
from telegram import Update, InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, InlineQueryHandler
from dotenv import load_dotenv
import uuid
from tmdb_wrapper import TMDB_WRAPPER, TMDB_RESULT


# Load environment variables from .env file
load_dotenv()

# read the Telegram bot token from environment variable
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TMDB_API = os.getenv("TMDB_API")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is not set.")

if not TMDB_API:
    raise ValueError("TMDB_API environment variable is not set.")


#create a tmdb wrapper
tmdb = TMDB_WRAPPER(TMDB_API)

#create telegram app
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome to the IMDb Bot! Use @mediajellyinfoer_bot <media_name> to get inline suggestions.")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query
    if not query:
        return
    
    try:
        
        movies = tmdb.search(query)
        results = []
        for movie in movies:
            # Get basic movie info
            title = movie.get_formatted_title()

            
            poster_url = movie.get_poster_url()
            

            #TODO: Why is not showing the photo?

            # if poster_url:
            #     # Use InlineQueryResultPhoto for results with images
            result = InlineQueryResultPhoto(
                id=str(uuid.uuid4()),
                photo_url=poster_url,
                # thumbnail_url=f"https://image.tmdb.org/t/p/w185{movie.poster_path}",  # Smaller thumbnail,  # Smaller thumbnail
                title=title,
                description=f"{movie.title} - 📅 {movie.release_date}",
                caption=tmdb.print_result(movie),
                parse_mode='Markdown'
            )
            # else:
            #     # Fallback to article if no poster available
            # result = InlineQueryResultArticle(
            #     id=str(uuid.uuid4()),
            #     title=title,
            #     description=f"{movie.title} - 📅 {movie.release_date}",
            #     input_message_content=InputTextMessageContent(
            #         message_text=tmdb.print_result(movie),
            #         parse_mode='Markdown'
            #     )
            # )
            results.append(result)
        
        await update.inline_query.answer(results, cache_time=0)
        
    except Exception as e:
        # Return empty results on error
        await update.inline_query.answer([])

app.add_handler(CommandHandler("start", start))
app.add_handler(InlineQueryHandler(callback=inline_query))



app.run_polling()


