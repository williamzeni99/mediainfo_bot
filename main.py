import os
from telegram import InputVenueMessageContent, Update, InlineQueryResultDocument, InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultCachedPhoto, InputMessageContent, MessageEntity
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
    await update.message.reply_text("Welcome to the Media Info! Use @mediajellyinfoer_bot <media_name> to get inline suggestions. Click on one cover to get the results.")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query
    if not query:
        return
    
    try:
        movies = tmdb.search(query)[:10]
        results = []
        for movie in movies:
            # Get basic movie info
            title = movie.get_formatted_title()

            if movie.poster_path is None:
                print(f"No poster available for {title}, skipping photo result.")
                continue

            # Create photo result with poster
            result = InlineQueryResultPhoto(
                id=str(uuid.uuid4()),
                photo_url=movie.get_poster_url(),
                thumbnail_url=movie.get_thumbnail_url(),
                title=title,
                description=f"📅 {movie.release_date}",
                caption= tmdb.print_result(movie),
                parse_mode='Markdown'
            )
            results.append(result)
        
        await update.inline_query.answer(results)
        
    except Exception as e:
        # Return empty results on error
        print(f"Error during inline query: {e}")
        await update.inline_query.answer([])

async def getimage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.message.text.split(maxsplit=1)
    if len(query) < 2:
        await update.message.reply_text("Please provide a movie or TV show name.")
        return
    
    title = query[1]
    try:
        movies = tmdb.search(title)
        if not movies:
            await update.message.reply_text("No results found.")
            return
        
        # Use the first result for simplicity
        movie = movies[0]
        
        if movie.poster_path is None:
            await update.message.reply_text("No poster available for this media.")
            return
        
        poster = movie.download_poster()
        if poster is None:
            await update.message.reply_text("Failed to download poster.")
            return
        await update.message.reply_photo(photo=poster, caption=movie.get_formatted_title())
    
    except Exception as e:
        await update.message.reply_text(f"Error fetching image: {e}")

app.add_handler(CommandHandler("start", start))
app.add_handler(InlineQueryHandler(callback=inline_query))
app.add_handler(CommandHandler("img", getimage))  # Reuse start handler for help command



app.run_polling()


