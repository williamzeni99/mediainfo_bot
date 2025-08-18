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
    text="Welcome to the Media Info! Use @mediajellyinfoer_bot <media_name> to get inline suggestions. Click on one cover to get the results."
    text += "\n\nYou can also use the following commands:\n"
    text += "/search <title> - Search for movies or TV shows IDS (more extensive)\n"
    text += "/getmovie <id> - Get movie details by ID\n"
    text += "/gettv <id> - Get TV show details by ID\n"
    await update.message.reply_text(text)

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query.split("///")
    extra_notes = query[1].strip() if len(query) > 1 else ""
    query = query[0].strip() if query else ""
    # extra_notes = ""
    print(f"Received inline query: {query}, extra notes: {extra_notes}")
    if not query:
        return
    
    try:
        movies = tmdb.search(query)[:10]
        results = []
        for movie in movies:
            # Get basic movie info
            title = movie.get_formatted_title()

            print(f"Processing movie: {title}")

            if movie.poster_path is None:
                print(f"No poster available for {title}, skipping photo result.")
                continue


            caption = tmdb.print_result(movie)
            if extra_notes:
                caption += f"\n\n⚠️ Note extra: {extra_notes}"


            # Create photo result with poster
            result = InlineQueryResultPhoto(
                id=str(uuid.uuid4()),
                photo_url=movie.get_poster_url(),
                thumbnail_url=movie.get_thumbnail_url(),
                title=title,
                description=f"📅 {movie.release_date}",
                caption= caption,
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


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        
        text="Results for your search:\n\n"
        text+= "TITLE - MEDIA TYPE: ID\n"
        text+= "-------------------------\n"
        for movie in movies:
            text += f"{movie.get_formatted_title()} - {movie.media_type}: {movie.id}\n"

        await update.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Error fetching results: {e}")
        return

async def getmovie_byid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.message.text.split("//", maxsplit=1)
    exta_notes = query[1].strip() if len(query) > 1 else ""
    query = query[0].strip()
    query = query.split(maxsplit=1)
    if len(query) < 2:
        await update.message.reply_text("Please provide a movie ID.")
        return
    
    try:
        movie_id = int(query[1])
        movie = tmdb.get_movie(movie_id)
        
        if not movie:
            await update.message.reply_text("No results found for this ID.")
            return
        
        if movie.poster_path is None:
            await update.message.reply_text("No poster available for this media.")
            return
        
        poster = movie.download_poster()
        if poster is None:
            await update.message.reply_text("Failed to download poster.")
            return
        
        caption = tmdb.print_result(movie)
        if exta_notes:
            caption += f"\n\n⚠️ Note extra: {exta_notes}"

        await update.message.reply_photo(photo=poster, caption=caption, parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"Error fetching image: {e}")

async def gettv_byid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.message.text.split("//",maxsplit=1)
    exta_notes = query[1].strip() if len(query) > 1 else ""
    query = query[0].strip()
    query = query.split(maxsplit=1)
    if len(query) < 2:
        await update.message.reply_text("Please provide a TV show ID.")
        return
    
    try:
        tv_id = int(query[1])
        tv_show = tmdb.get_tv_show(tv_id)
        
        if not tv_show:
            await update.message.reply_text("No results found for this ID.")
            return
        
        if tv_show.poster_path is None:
            await update.message.reply_text("No poster available for this media.")
            return
        
        poster = tv_show.download_poster()
        if poster is None:
            await update.message.reply_text("Failed to download poster.")
            return
        
        caption = tmdb.print_result(tv_show)
        if exta_notes:
            caption += f"\n\n⚠️ Note extra: {exta_notes}"

        await update.message.reply_photo(photo=poster, caption=caption, parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"Error fetching image: {e}")

app.add_handler(CommandHandler("start", start))
app.add_handler(InlineQueryHandler(callback=inline_query))
app.add_handler(CommandHandler("img", getimage))  # Reuse start handler for help command
#app.remove_handler(InlineQueryHandler(callback=inline_query))
app.add_handler(CommandHandler("getmovie", getmovie_byid))  # New command to get movie by ID
app.add_handler(CommandHandler("gettv", gettv_byid))  # New command to get TV show by ID
app.add_handler(CommandHandler("search", search))  # New command to search for movies or TV shows
app.run_polling()


