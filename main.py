from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os
import uuid
import asyncio
from pathlib import Path
from typing import Dict

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure downloads directory exists
DOWNLOADS_DIR = Path("downloads")
DOWNLOADS_DIR.mkdir(exist_ok=True)

# Store download progress and cancellation flags
download_progress: Dict[str, dict] = {}
cancel_flags: Dict[str, bool] = {}


class DownloadRequest(BaseModel):
    url: str
    download_type: str  # 'audio' or 'video'
    format: str  # 'mp3', 'mp4', 'm4a', etc.


class StartDownloadRequest(BaseModel):
    url: str
    download_type: str  # 'audio' or 'video'
    format: str  # 'mp3', 'mp4', 'm4a', etc.


@app.get("/")
async def root():
    """Serve the frontend HTML page"""
    return FileResponse("static/index.html")


@app.post("/start-download")
async def start_download(request: StartDownloadRequest):
    """Start a download and return a download ID for tracking progress"""
    if not request.url or not request.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    download_id = str(uuid.uuid4())[:12]
    
    # Initialize progress tracking
    download_progress[download_id] = {
        "status": "starting",
        "progress": 0,
        "speed": "",
        "eta": "",
        "filename": "",
        "error": None
    }
    cancel_flags[download_id] = False
    
    # Start download in background
    asyncio.create_task(process_download(download_id, request))
    
    return {"download_id": download_id}


@app.get("/progress/{download_id}")
async def get_progress(download_id: str):
    """Get the current progress of a download"""
    if download_id not in download_progress:
        raise HTTPException(status_code=404, detail="Download ID not found")
    
    return download_progress[download_id]


@app.post("/cancel/{download_id}")
async def cancel_download(download_id: str):
    """Cancel an ongoing download"""
    if download_id not in cancel_flags:
        raise HTTPException(status_code=404, detail="Download ID not found")
    
    cancel_flags[download_id] = True
    download_progress[download_id]["status"] = "cancelled"
    
    return {"message": "Download cancelled"}


@app.get("/download/{download_id}")
async def download_file(download_id: str):
    """Download the completed file"""
    if download_id not in download_progress:
        raise HTTPException(status_code=404, detail="Download ID not found")
    
    progress = download_progress[download_id]
    
    if progress["status"] != "completed":
        raise HTTPException(status_code=400, detail="Download not completed yet")
    
    file_path = progress.get("file_path")
    if not file_path or not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="Downloaded file not found")
    
    response = FileResponse(
        path=file_path,
        filename=progress["filename"],
        media_type='application/octet-stream'
    )
    
    # Schedule cleanup
    asyncio.create_task(cleanup_download(download_id, Path(file_path)))
    
    return response


async def process_download(download_id: str, request: StartDownloadRequest):
    """Process the download in the background with progress tracking"""
    unique_id = str(uuid.uuid4())[:8]
    downloaded_file = None
    
    def progress_hook(d):
        """Hook to track download progress"""
        if cancel_flags.get(download_id, False):
            raise Exception("Download cancelled by user")
        
        if d['status'] == 'downloading':
            progress_data = download_progress[download_id]
            progress_data["status"] = "downloading"
            
            # Calculate percentage
            if d.get('total_bytes'):
                percent = (d.get('downloaded_bytes', 0) / d['total_bytes']) * 100
                progress_data["progress"] = round(percent, 1)
            elif d.get('total_bytes_estimate'):
                percent = (d.get('downloaded_bytes', 0) / d['total_bytes_estimate']) * 100
                progress_data["progress"] = round(percent, 1)
            
            # Speed and ETA
            if d.get('speed'):
                speed_mb = d['speed'] / 1024 / 1024
                progress_data["speed"] = f"{speed_mb:.2f} MB/s"
            
            if d.get('eta'):
                progress_data["eta"] = f"{d['eta']}s"
        
        elif d['status'] == 'finished':
            download_progress[download_id]["status"] = "processing"
            download_progress[download_id]["progress"] = 100
    
    # Configure yt-dlp options
    ydl_opts = {
        'progress_hooks': [progress_hook],
        'quiet': False,
        'no_warnings': True,
    }
    
    if request.download_type == "audio":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': str(DOWNLOADS_DIR / f'{unique_id}_%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': request.format,
                'preferredquality': '192',
            }],
        })
    elif request.download_type == "video":
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': str(DOWNLOADS_DIR / f'{unique_id}_%(title)s.%(ext)s'),
        })
        if request.format in ['mp4', 'mkv', 'webm']:
            ydl_opts['merge_output_format'] = request.format
    
    try:
        # Download the content
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=True)
            
            if cancel_flags.get(download_id, False):
                raise Exception("Download cancelled by user")
            
            # Find the downloaded file
            base_filename = f'{unique_id}_{info["title"]}'
            possible_extensions = [request.format, 'mp4', 'mkv', 'webm', 'mp3', 'm4a', 'opus']
            
            for ext in possible_extensions:
                potential_file = DOWNLOADS_DIR / f'{base_filename}.{ext}'
                if potential_file.exists():
                    downloaded_file = potential_file
                    break
            
            if not downloaded_file:
                for file in DOWNLOADS_DIR.glob(f'{unique_id}_*'):
                    downloaded_file = file
                    break
        
        if not downloaded_file or not downloaded_file.exists():
            raise Exception("Download completed but file not found")
        
        # Update progress to completed
        download_progress[download_id].update({
            "status": "completed",
            "progress": 100,
            "filename": downloaded_file.name.replace(f'{unique_id}_', ''),
            "file_path": str(downloaded_file)
        })
        
    except Exception as e:
        # Handle errors
        download_progress[download_id].update({
            "status": "error",
            "error": str(e)
        })
        
        # Clean up partial downloads
        if downloaded_file and downloaded_file.exists():
            downloaded_file.unlink()
        
        # Clean up any files with the unique_id
        for file in DOWNLOADS_DIR.glob(f'{unique_id}_*'):
            try:
                file.unlink()
            except:
                pass


async def cleanup_download(download_id: str, file_path: Path, delay: int = 10):
    """Clean up download data and file after a delay"""
    await asyncio.sleep(delay)
    
    try:
        if file_path.exists():
            file_path.unlink()
            print(f"Deleted: {file_path.name}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
    
    # Remove from tracking dictionaries
    download_progress.pop(download_id, None)
    cancel_flags.pop(download_id, None)


@app.on_event("startup")
async def startup_event():
    """Clean up any leftover files on startup"""
    for file in DOWNLOADS_DIR.glob("*"):
        try:
            file.unlink()
        except Exception as e:
            print(f"Error cleaning up {file}: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)