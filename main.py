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


class DownloadRequest(BaseModel):
    url: str
    download_type: str  # 'audio' or 'video'
    format: str  # 'mp3', 'mp4', 'm4a', etc.


@app.get("/")
async def root():
    """Serve the frontend HTML page"""
    return FileResponse("static/index.html")


@app.post("/download")
async def download_video(request: DownloadRequest):
    """
    Download YouTube content and return the file.
    Automatically deletes the file after sending.
    """
    if not request.url or not request.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    # Generate unique filename to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    
    # Configure yt-dlp options based on user choice
    ydl_opts = {}
    
    if request.download_type == "audio":
        # Audio download configuration
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(DOWNLOADS_DIR / f'{unique_id}_%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': request.format,
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
    elif request.download_type == "video":
        # Video download configuration
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': str(DOWNLOADS_DIR / f'{unique_id}_%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        # If specific video format requested, add merge format
        if request.format in ['mp4', 'mkv', 'webm']:
            ydl_opts['merge_output_format'] = request.format
    else:
        raise HTTPException(status_code=400, detail="Invalid download type. Use 'audio' or 'video'")
    
    downloaded_file = None
    
    try:
        # Download the content
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=True)
            
            # Find the downloaded file
            # yt-dlp might change the extension after post-processing
            base_filename = f'{unique_id}_{info["title"]}'
            
            # Look for the file with various possible extensions
            possible_extensions = [request.format, 'mp4', 'mkv', 'webm', 'mp3', 'm4a', 'opus']
            for ext in possible_extensions:
                potential_file = DOWNLOADS_DIR / f'{base_filename}.{ext}'
                if potential_file.exists():
                    downloaded_file = potential_file
                    break
            
            # If still not found, search directory for files with unique_id
            if not downloaded_file:
                for file in DOWNLOADS_DIR.glob(f'{unique_id}_*'):
                    downloaded_file = file
                    break
        
        if not downloaded_file or not downloaded_file.exists():
            raise HTTPException(status_code=500, detail="Download completed but file not found")
        
        # Return file and schedule deletion after response
        response = FileResponse(
            path=str(downloaded_file),
            filename=downloaded_file.name.replace(f'{unique_id}_', ''),
            media_type='application/octet-stream'
        )
        
        # Schedule file deletion after response is sent
        asyncio.create_task(delete_file_after_delay(downloaded_file))
        
        return response
        
    except yt_dlp.utils.DownloadError as e:
        # Clean up any partial downloads
        if downloaded_file and downloaded_file.exists():
            downloaded_file.unlink()
        raise HTTPException(status_code=400, detail=f"Download error: {str(e)}")
    
    except Exception as e:
        # Clean up any partial downloads
        if downloaded_file and downloaded_file.exists():
            downloaded_file.unlink()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


async def delete_file_after_delay(file_path: Path, delay: int = 5):
    """Delete file after a delay to ensure response is sent"""
    await asyncio.sleep(delay)
    try:
        if file_path.exists():
            file_path.unlink()
            print(f"Deleted: {file_path.name}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")


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
