# Instagram Saved Posts Downloader

A Python tool to download all your saved Instagram posts (photos, videos, reels, carousels) from your account with metadata preservation.

## Features

-  **Collection Selection** - Choose specific collections or download all saved posts
-  **All Media Types** - Supports photos, videos, reels, and carousel albums
-  **Metadata Export** - Saves captions, hashtags, audio info, and timestamps as JSON
-  **Smart Tracking** - Automatically skips previously downloaded content
-  **Organized Storage** - Files sorted by media type (photos/videos/albums)
-  **ZIP Backups** - Creates compressed archives of your downloads
-  **Progress Tracking** - Real-time progress bars and statistics

## Requirements

- Python 3.11 - 3.13 (recommended: 3.13)
- Instagram account
- Active Instagram session

## Installation

1. **Clone or download this repository:**
```bash
git clone https://github.com/tg769/instagram-saved-collection-download.git
cd instagram-saved-collection-download
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Getting Your Session ID

1. Open Instagram in your web browser and log in
2. Press `F12` to open Developer Tools
3. Go to the **Application** tab (Chrome/Edge) or **Storage** tab (Firefox)
4. Navigate to **Cookies** → `https://www.instagram.com`
5. Find the cookie named `sessionid`
6. Copy the entire value

⚠️ **Security Warning**: Your session ID gives full access to your account. Never share it with anyone.

## Usage

### Command Line (CLI)

```bash
python app.py
```

**What happens:**
1. Paste your Instagram `sessionid` when prompted
2. Choose a collection or select "0" for all saved posts
3. Optionally specify how many posts to download
4. Watch the download progress
5. Get a ZIP backup when complete

**Example:**
```
📂 Your Instagram Collections:
  0. All Saved Posts (download everything)
  1. music (45 posts)
  2. gym (32 posts)
  3. travel (18 posts)

📌 Select collection number (0 for all): 2
📊 Selected: gym
How many posts to download? (Enter for all, or a number): 10
```

### Graphical Interface (GUI)

```bash
python run_gui.py
```

The GUI provides:
- Simple session ID input field
- Collection selection dropdown
- Download progress display
- Live activity logs

## Project Structure

```
instagram-saved-collection-download/
├── app.py                    # Main CLI application
├── run_gui.py                # GUI launcher
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── downloader/
│   ├── __init__.py
│   ├── client.py            # Instagram authentication
│   ├── fetch.py             # Fetch saved posts & collections
│   ├── download.py          # Download media files
│   ├── metadata.py          # Extract and save metadata
│   ├── utils.py             # Utilities and tracking
│   └── zipper.py            # ZIP backup creation
├── gui/
│   ├── __init__.py
│   └── gui.py               # Tkinter GUI interface
├── data/
│   └── downloaded.json      # Download tracking (auto-created)
└── downloads/
    ├── photos/              # Downloaded photos
    ├── videos/              # Downloaded videos/reels
    ├── albums/              # Downloaded carousel albums
    └── metadata/            # JSON metadata files
```

## Metadata Format

Each downloaded post includes a JSON file with:

```json
{
  "pk": "1234567890",
  "media_type": 2,
  "caption": "Post caption text",
  "username": "author_username",
  "taken_at": "2025-11-21T12:00:00",
  "product_type": "clips",
  "audio": "Audio Track Name",
  "hashtags": ["travel", "photography"],
  "downloaded_at": "2025-11-21T14:30:00"
}
```

## Features in Detail

### Collection Support
- Browse all your Instagram collections
- Download specific collections (music, gym, recipes, etc.)
- Or download all saved posts at once

### Incremental Downloads
- Tracks what's already downloaded in `data/downloaded.json`
- Re-running the tool only downloads new posts
- Saves time and bandwidth

### Smart Organization
- Photos → `downloads/photos/`
- Videos/Reels → `downloads/videos/`
- Carousels → `downloads/albums/`
- Metadata → `downloads/metadata/`

### ZIP Backups
- Automatically creates `instagram_saved_backup.zip`
- Contains all downloads and metadata
- Easy archival and sharing

## Troubleshooting

**"Login failed"**
- Your session ID may have expired
- Get a fresh session ID from your browser
- Make sure you copied the entire value

**"No collections found"**
- You may not have created any collections
- The tool will fetch all saved posts instead

**Some downloads failed**
- Private account posts may be inaccessible
- Deleted posts will show as failed
- Check `instagram_downloader.log` for details

**Python version issues**
- Use Python 3.11 to 3.13 (not 3.14+)
- Run with: `py -3.13 app.py` on Windows

## Privacy & Ethics

-  Downloads only content **you** have saved
-  Uses **your own** session cookie
-  All data stays on **your machine**
-  No passwords required or stored
-  Respects rate limits automatically

This tool is for **personal archival** purposes only. Use responsibly and in accordance with Instagram's Terms of Service.

## License

MIT License - See LICENSE file for details.

## Author

Created by [tg769](https://github.com/tg769)

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/tg769/instagram-saved-collection-download/issues).

## Support 

If you find this tool helpful, please ⭐ star the repository!

For bugs or questions, open an issue on GitHub.
