import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
from tmdb_wrapper import TMDB_WRAPPER, TMDB_RESULT


# Load environment variables from .env file
load_dotenv()

# read the Telegram bot token from environment variable
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TMDB_API = os.getenv("TMDB_API")
CHANNEL_ID = os.getenv("CHANNEL_ID")
MY_CHAT_ID = os.getenv("MY_CHAT_ID")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is not set.")

if not TMDB_API:
    raise ValueError("TMDB_API environment variable is not set.")

if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID environment variable is not set.")

if not MY_CHAT_ID:
    raise ValueError("MY_CHAT_ID environment variable is not set.")


#create a tmdb wrapper
tmdb = TMDB_WRAPPER(TMDB_API)

# No conversation states needed anymore

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Welcome to the Movie & TV Show Bot! 🎬\n\n"
        "Send me a movie or TV show title to search for it!"
    )

async def search_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the search query from user."""
    query = update.message.text
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Search for movies and TV shows
    results = tmdb.search(query)
    
    if not results:
        await update.message.reply_text(
            "❌ No results found. Try a different search term."
        )
        return
    
    text = f"🎬 *Search Results for:* `{query}`\n"
    text += f"📊 Found {len(results)} result(s)\n\n"
    
    keyboard = []

    for i, movie in enumerate(results, 1):
        # Media type icon
        media_icon = "🎬" if movie.media_type == "movie" else "📺"
        
        # Rating stars
        rating = movie.vote_average
        rating_icon = "⭐"
        
        # Format year
        year = movie.get_year()
        year_text = f"📅 {year}" if year != "Unknown" else "📅 N/A"
        
        # Build result entry
        text += f"*{i}.* {media_icon} *{movie.title}*\n"
        text += f"   └ {year_text} • {rating_icon} {rating}/10 • ID: `{movie.id}`\n"
        text += f"   └ Type: _{movie.media_type.title()}_\n\n"
        button_text = f"{i}. {media_icon} {movie.title[:20]}{'...' if len(movie.title)>20 else ''} ({movie.get_year()})"
        
        callback_data = f"select_{movie.media_type}_{movie.id}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle movie/TV show selection from inline keyboard."""
    query = update.callback_query
    await query.answer()
    
    # Parse callback data
    try:
        _, media_type, item_id = query.data.split('_', 2)
        item_id = int(item_id)
    except (ValueError, IndexError):
        await query.edit_message_text("❌ Invalid selection.")
        return
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Get detailed information
    if media_type == "movie":
        result = tmdb.get_movie(item_id)
    elif media_type == "tv-show":
        result = tmdb.get_tv_show(item_id)
    else:
        await query.edit_message_text("❌ Unknown media type.")
        return
    
    if not result:
        await query.edit_message_text("❌ Could not fetch details for this item.")
        return
    
    # Format the message
    caption = tmdb.print_result(result)
    
    # Get poster URL
    poster_url = result.get_poster_url()
    
    if poster_url:
        try:
            # Send photo with caption
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=poster_url,
                caption=caption,
                parse_mode='Markdown'
            )
            # Delete the search results message
            await query.delete_message()
        except Exception as e:
            # If photo fails, send text message
            await query.edit_message_text(
                f"🖼️ *Poster not available*\n\n{caption}",
                parse_mode='Markdown'
            )
    else:
        # No poster available, send text only
        await query.edit_message_text(
            f"🖼️ *No poster available*\n\n{caption}",
            parse_mode='Markdown'
        )

#create telegram app
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(selection_handler, pattern="^select_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_query_handler))

app.run_polling()


