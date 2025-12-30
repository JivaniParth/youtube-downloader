# YouTube Downloader Web App

A private, personal-use web application for downloading YouTube videos and audio files. Built with FastAPI backend and vanilla HTML/CSS/JS frontend.

## Features

- Download YouTube videos in MP4, MKV, or WebM formats
- Extract audio as MP3, M4A, or OPUS
- Simple, minimal dark-themed UI
- Mobile-friendly responsive design
- Automatic file cleanup after download
- Real-time loading states and error handling

## Prerequisites

Before running this application, ensure you have:

- **Python 3.8+** installed
- **FFmpeg** installed and available in PATH
- **yt-dlp** installed (or will be installed via requirements.txt)

### Installing FFmpeg

#### Windows:
1. Download from: https://ffmpeg.org/download.html
2. Extract and add to PATH
3. Verify: `ffmpeg -version`

## Project Structure

```
YouTubeDownloader/
├── main.py                 # FastAPI backend server
├── static/
│   └── index.html         # Frontend UI
├── downloads/             # Temporary download storage (auto-created)
├── requirements.txt       # Python dependencies
├── yt_downloader.py       # Original CLI script (can be kept for reference)
└── README.md             # This file
```

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd d:\\Projects\\YouTubeDownloader
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Windows (CMD):
     ```cmd
     .\venv\Scripts\activate.bat
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the FastAPI server**:
   ```bash
   python main.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

3. **Use the application**:
   - Paste a YouTube URL
   - Select Video or Audio
   - Choose format (MP4/MKV/WebM for video, MP3/M4A/OPUS for audio)
   - Click Download
   - File will download to your browser's download folder

## Running on a Private VPS

1. **Set up your VPS** with Python 3.8+ and FFmpeg

2. **Transfer files** to your VPS:
   ```bash
   scp -r YouTubeDownloader/ user@your-vps-ip:/path/to/directory
   ```

3. **SSH into your VPS**:
   ```bash
   ssh user@your-vps-ip
   ```

4. **Follow installation steps** above

5. **Run with a process manager** (recommended for production):
   
   Using `screen`:
   ```bash
   screen -S youtube-downloader
   python main.py
   # Press Ctrl+A, then D to detach
   ```

   Or using `systemd` (create a service file):
   ```ini
   [Unit]
   Description=YouTube Downloader Web App
   After=network.target

   [Service]
   User=your-username
   WorkingDirectory=/path/to/YouTubeDownloader
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/python main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

6. **Access via VPS IP**:
   ```
   http://your-vps-ip:8000
   ```

   **Security Note**: Since this is for personal use, consider:
   - Using a VPN to access your VPS
   - Setting up firewall rules to limit access
   - Using SSH tunneling: `ssh -L 8000:localhost:8000 user@your-vps-ip`

## Configuration

### Change Port

Edit [main.py](main.py#L157) at the bottom:
```python
uvicorn.run(app, host="0.0.0.0", port=YOUR_PORT)
```

### Change Download Directory

Edit [main.py](main.py#L24):
```python
DOWNLOADS_DIR = Path("your/custom/path")
```

### Adjust File Cleanup Delay

Edit [main.py](main.py#L133):
```python
asyncio.create_task(delete_file_after_delay(downloaded_file, delay=10))  # 10 seconds
```

## Troubleshooting

### "FFmpeg not found"
- Ensure FFmpeg is installed and in your PATH
- Test: `ffmpeg -version`

### "Download error: Video unavailable"
- Video may be private, deleted, or region-locked
- Update yt-dlp: `pip install --upgrade yt-dlp`

### "Module not found" errors
- Activate your virtual environment
- Reinstall requirements: `pip install -r requirements.txt`

### Port already in use
- Change the port in [main.py](main.py#L157)
- Or kill the process using port 8000

### Files not downloading
- Check browser's download settings
- Ensure pop-ups are not blocked
- Check browser console for JavaScript errors (F12)

## Technical Details

### Backend (FastAPI)
- **Endpoint**: `POST /download`
- **Accepts**: JSON with `url`, `download_type`, `format`
- **Returns**: File as streaming response
- **Cleanup**: Files deleted after 5 seconds using async tasks

### Frontend
- Pure HTML/CSS/JavaScript (no frameworks)
- Dark theme with gradient backgrounds
- Responsive design (mobile-friendly)
- Real-time error handling and user feedback

### Security Considerations
- **Private use only** - no authentication implemented
- Files are temporary and auto-deleted
- Unique IDs prevent filename conflicts
- No database or persistent storage
- CORS enabled for local development

## Limitations

- No download queue (one at a time)
- No download progress tracking
- No playlist support
- Files temporarily stored on disk
- No user authentication
- Single concurrent user recommended

## License

For personal use only. Respect YouTube's Terms of Service.

## Original CLI Script

The original CLI script ([yt_downloader.py](yt_downloader.py)) is still available in the project directory for reference or standalone use.
