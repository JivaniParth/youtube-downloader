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
├── ytdownload.bat         # Launcher so the app can be run as `ytdownload` from anywhere
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

## Run from anywhere as `ytdownload`

After the venv is set up (see Installation above), you can call this tool as `ytdownload` from any folder, in any terminal, without typing `python main.py` or its full path.

1. `ytdownload.bat` (included in this folder) already points at `venv\Scripts\python.exe` and `main.py` using its own location, so it works as-is as long as it stays in this project folder alongside `main.py` and `venv\`.
2. Add this project folder to your **user PATH** once, so Windows can find `ytdownload.bat` from anywhere:
   - PowerShell (run once, then close and reopen your terminal):
     ```powershell
     [Environment]::SetEnvironmentVariable("Path", $env:Path + ";D:\Projects\YouTubeDownloader", "User")
     ```
   - Or via the GUI: Search "Environment Variables" → Edit the user `Path` variable → New → paste the project folder path (e.g. `D:\Projects\YouTubeDownloader`) → OK.
3. Open a **new** terminal window (PATH changes only apply to new sessions) and run:
   ```powershell
   ytdownload https://youtu.be/GnjPoRXYxaM
   ```
   You'll then be prompted for download type, format, and location, same as before. You can also just run `ytdownload` with no URL and you'll be prompted for everything, including the URL.

## Usage

Run the CLI directly with Python:

```powershell
python main.py
```

Or, once set up as described above, from any folder:

```powershell
ytdownload [url]
```

The URL is optional — pass it as an argument to skip that prompt, or omit it and you'll be asked for it.

Prompt order:

1. (URL — skipped if passed as an argument)
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