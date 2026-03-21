# YouTube Downloader CLI

Private, personal-use command-line app for downloading YouTube video or audio.

## Current Features

- CLI-only flow (no web UI/server)
- Interactive prompts for:
  - URL
  - Download type (`video` or `audio`)
  - Output format
  - Download location
- Output folder is created automatically if it does not exist
- After each download, asks whether to continue with another download (`yes/no`)

## Supported Formats

- Video: `mp4`, `mkv`, `webm`
- Audio: `mp3`, `m4a`, `opus`

## Requirements

- Python 3.8+
- FFmpeg available in PATH
- Python dependency from `requirements.txt` (`yt-dlp`)

### FFmpeg Setup (Windows)

1. Download FFmpeg from https://ffmpeg.org/download.html
2. Add FFmpeg to PATH
3. Verify:
   ```powershell
   ffmpeg -version
   ```

## Project Structure

```
YouTubeDownloader/
├── main.py               # Main and only CLI entrypoint
├── requirements.txt      # Python dependencies
└── README.md
```

## Installation

1. Open terminal in the project folder:
   ```powershell
   cd d:\Projects\YouTubeDownloader
   ```
2. Create virtual environment:
   ```powershell
   python -m venv venv
   ```
3. Activate virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage

Run the CLI:

```powershell
python main.py
```

Prompt order:

1. Enter YouTube URL
2. Choose download type (Video/Audio)
3. Choose format (based on type)
4. Enter download location (folder path)
5. Choose whether to continue with another download (yes/no)

## Troubleshooting

### FFmpeg not found

- Confirm FFmpeg is installed and in PATH
- Run `ffmpeg -version`

### Download fails

- Video may be private, deleted, region-restricted, or age-restricted
- Update yt-dlp:
  ```powershell
  pip install --upgrade yt-dlp
  ```

### Dependency/import errors

- Activate the virtual environment
- Reinstall dependencies:
  ```powershell
  pip install -r requirements.txt
  ```

## License

For personal use only. Respect YouTube Terms of Service.
