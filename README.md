# MediaInfo Bot

A Telegram bot for retrieving detailed information about movies and TV shows from [The Movie Database (TMDB)](https://www.themoviedb.org/) API. The bot provides comprehensive media information including ratings, overviews, release dates, and poster images, with optional functionality to share findings to your personal Telegram channel.

## Features

- 🎬 **Movie & TV Show Search**: Search for movies and TV shows by title
- 📊 **Detailed Information**: Get comprehensive details including ratings, genres, release dates, and overviews
- 🖼️ **Poster Images**: View high-quality poster images for each media item
- 📱 **Inline Queries**: Use inline mode for quick searches directly in any chat
- 📢 **Channel Integration**: Optionally send media information to your personal channel
- 🔍 **ID-based Lookups**: Search by specific TMDB IDs for precise results

## Commands

- `/start` - Display welcome message and available commands
- `/search <title>` - Search for movies or TV shows (extensive search)
- `/getmovie <id>` - Get movie details by TMDB ID
- `/gettv <id>` - Get TV show details by TMDB ID
- `/send <movie/tv-show> <id> [extra_notes]` - Send media information to your channel
- **Inline mode**: Use `@your_bot_username <media_name>` in any chat for quick searches

## Installation & Configuration

### Prerequisites

1. **TMDB API Key**: Register at [TMDB](https://www.themoviedb.org/) and obtain an API key from your account settings
2. **Telegram Bot Token**: Create a bot via [@BotFather](https://t.me/botfather) on Telegram
3. **Chat IDs**: You'll optionally need your personal chat ID and your channel ID

### Getting Required IDs

#### Finding Your Chat ID
1. Start a chat with [@userinfobot](https://t.me/userinfobot)
2. Send any message to get your chat ID

#### Finding Your Channel ID (Optional)
1. Add [@userinfobot](https://t.me/userinfobot) to your channel as an admin
2. Send a message in the channel to get the channel ID
3. Remove the bot from the channel after getting the ID

### Configuration

1. **Environment Setup**: Copy the example environment file and configure it:
   ```bash
   cp env-example .env
   ```

2. **Edit the `.env` file** with your credentials:
   ```env
   TELEGRAM_TOKEN=your_bot_token_here
   TMDB_API=your_tmdb_api_key_here
   CHANNEL_ID=your_channel_id_here
   MY_CHAT_ID=your_personal_chat_id_here
   ```

### Installation Options

#### Option 1: Using Poetry 

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Configure virtualenvs inside project** (optional):
   ```bash
   poetry config virtualenvs.in-project true
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Run the bot**:
   ```bash
   poetry run python main.py
   ```

#### Option 2: Using Docker

1. **Build with Docker Compose**:
   ```bash
   docker compose build
   ```

2. **Run with Docker Compose**:
   ```bash
   docker compose up -d
   ```

## Usage Examples

### Basic Search
```
/search The Matrix
```

### Get Specific Movie
```
/getmovie 603
```

### Get TV Show
```
/gettv 1399
```

### Send to Channel (with optional notes)
```
/send movie 603 Great sci-fi classic!
```

### Inline Query
Type in any chat: `@your_bot_username Inception`

## Requirements

- Python 3.11+
- Valid TMDB API key
- Telegram Bot Token
- Internet connection

## Dependencies

- `python-telegram-bot` - Telegram Bot API wrapper
- `python-dotenv` - Environment variable management
- `tmdbsimple` - TMDB API wrapper

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

If you encounter any issues or have questions, please open an issue on the repository.

---

**Note**: Make sure to keep your API keys and tokens secure. Never commit them to version control.
