# MediaInfo Bot

A Telegram bot for retrieving detailed information about movies and TV shows from [The Movie Database (TMDB)](https://www.themoviedb.org/) API. The bot provides comprehensive media information including ratings, overviews, release dates, and poster images, with optional functionality to share findings to your personal Telegram channel.

## Features

- 🎬 **Movie & TV Show Search**: Search for movies and TV shows by title with interactive results
- 📊 **Detailed Information**: Get comprehensive details including ratings, genres, release dates, overviews, and status
- 🖼️ **Poster Images**: View high-quality poster images for each media item
- 📱 **Inline Queries**: Use inline mode for quick searches directly in any chat
- 📢 **Channel Integration**: Send media information to your personal channel (authorized users only)
- 🎯 **Interactive Selection**: Choose from search results using custom keyboard buttons
- 📝 **Custom Notes**: Add extra notes when sending to channel
- 🔄 **Smart Search**: Automatically detects movies vs TV shows and provides appropriate details

## How to Use

### Basic Search
Simply send the bot a movie or TV show title, and it will return a list of results. Use the interactive keyboard to select the specific item you want detailed information about.

#### Example Workflow
1. Send: `Inception`
2. Bot shows search results with buttons
3. Click: `1. 🎬 Inception (2010)`
4. Bot shows detailed info with poster
5. (If authorized) Click `📤 Send` to share to your channel

### Commands Available

- `/start` - Display welcome message and instructions
- **Text Search**: Send any movie or TV show title (no command needed)
- **Inline mode**: Use `@your_bot_username <media_name>` in any chat for quick searches

### Special Features (Authorized Users Only)
- 📤 **Send to Channel**: Send the current result to your configured channel
- 📝 **Edit Extra Notes**: Add custom notes before sending to channel

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

   **Note**: All four environment variables are required for the bot to run properly. The `CHANNEL_ID` and `MY_CHAT_ID` are used for the channel integration feature.

### Installation Options

#### Option 1: Using Docker (Recommended)

1. **Build and run with Docker Compose**:
   ```bash
   docker compose up -d
   ```

   To rebuild after changes:
   ```bash
   docker compose build
   docker compose up -d
   ```


#### Option 2: Using Poetry

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
