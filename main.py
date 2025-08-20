import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
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

# Store the current search result for the authorized user
current_search_result = None

# No conversation states needed anymore

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    # Clear any saved results
    global current_search_result

    if update.effective_chat.id != int(MY_CHAT_ID):
        current_search_result = None
    
    await update.message.reply_text(
        "Welcome to the Movie & TV Show Bot! 🎬\n\n"
        "Send me a movie or TV show title to search for it!",
        reply_markup=ReplyKeyboardRemove()
    )

async def search_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the search query from user."""
    query = update.message.text
    
    # Check if this is an abort command
    if query == "❌ Abort Search":
        # Clear stored results and saved search result
        context.user_data.clear()
        global current_search_result

        if update.effective_chat.id != int(MY_CHAT_ID):
            current_search_result = None
        
        await update.message.reply_text(
            "Search aborted. Send me a movie or TV show title to search for it!",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Check if this is a send command (authorized user only)
    if query == "📤 Send" and str(update.effective_chat.id) == MY_CHAT_ID:
        await handle_send_to_channel(update, context)
        return
    
    # Check if this is a clear command (authorized user only)
    if query == "🗑️ Clear" and str(update.effective_chat.id) == MY_CHAT_ID:
        await handle_clear_result(update, context)
        return
    
    # Check if this is a selection from results
    if query and query[0].isdigit() and '.' in query and 'search_results' in context.user_data:
        await handle_selection(update, context, query)
        return
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Search for movies and TV shows
    results = tmdb.search(query)
    
    if not results:
        await update.message.reply_text(
            "❌ No results found. Try a different search term.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Store results in context for later use
    context.user_data['search_results'] = results
    
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
        
        # Create keyboard button
        button_text = f"{i}. {media_icon} {movie.title[:25]}{'...' if len(movie.title)>25 else ''}"
        keyboard.append([KeyboardButton(button_text)])

    # Add abort button
    keyboard.append([KeyboardButton("❌ Abort Search")])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, selection_text: str):
    """Handle selection from keyboard buttons."""
    # Extract the number from the selection
    try:
        selection_num = int(selection_text.split('.')[0]) - 1
        results = context.user_data.get('search_results', [])
        
        if selection_num < 0 or selection_num >= len(results):
            await update.message.reply_text(
                "❌ Invalid selection.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        selected_item = results[selection_num]
        
    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ Invalid selection.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Get detailed information
    if selected_item.media_type == "movie":
        result = tmdb.get_movie(selected_item.id)
    elif selected_item.media_type == "tv-show":
        result = tmdb.get_tv_show(selected_item.id)
    else:
        await update.message.reply_text(
            "❌ Unknown media type.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    if not result:
        await update.message.reply_text(
            "❌ Could not fetch details for this item.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Clear the keyboard and stored results
    context.user_data.clear()
    
    # Format the message
    caption = tmdb.print_result(result)
    
    # Get poster URL
    poster_url = result.get_poster_url()
    
    # Check if this is the authorized user and save the result
    is_authorized_user = str(update.effective_chat.id) == MY_CHAT_ID
    if is_authorized_user:
        global current_search_result
        current_search_result = {
            'caption': caption,
            'poster_url': poster_url
        }
    
    # Create keyboard for authorized user
    keyboard = None
    if is_authorized_user and current_search_result:
        keyboard = ReplyKeyboardMarkup([
            [KeyboardButton("📤 Send"), KeyboardButton("🗑️ Clear")]
        ], one_time_keyboard=True, resize_keyboard=True)
    else:
        keyboard = ReplyKeyboardRemove()
    
    if poster_url:
        try:
            # Send photo with caption
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=poster_url,
                caption=caption,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        except Exception as e:
            # If photo fails, send text message
            await update.message.reply_text(
                f"🖼️ *Poster not available*\n\n{caption}",
                parse_mode='Markdown',
                reply_markup=keyboard
            )
    else:
        # No poster available, send text only
        await update.message.reply_text(
            f"🖼️ *No poster available*\n\n{caption}",
            parse_mode='Markdown',
            reply_markup=keyboard
        )

async def handle_send_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the saved search result to the channel."""
    global current_search_result
    
    if not current_search_result:
        await update.message.reply_text(
            "❌ No search result saved to send.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    try:
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=MY_CHAT_ID, action="typing")
        
        if current_search_result['poster_url']:
            # Send photo with caption to channel
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=current_search_result['poster_url'],
                caption=current_search_result['caption'],
                parse_mode='Markdown'
            )
        else:
            # Send text only to channel
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=f"🖼️ *No poster available*\n\n{current_search_result['caption']}",
                parse_mode='Markdown'
            )
        
        await update.message.reply_text(
            "✅ Successfully sent to channel!",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Clear the saved result after sending
        current_search_result = None
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Failed to send to channel: {str(e)}",
            reply_markup=ReplyKeyboardRemove()
        )

async def handle_clear_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear the saved search result."""
    global current_search_result
    current_search_result = None
    
    await update.message.reply_text(
        "🗑️ Saved result cleared. Send me a movie or TV show title to search for it!",
        reply_markup=ReplyKeyboardRemove()
    )

#create telegram app
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_query_handler))

app.run_polling()


