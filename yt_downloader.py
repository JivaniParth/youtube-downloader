import yt_dlp
import os
from pathlib import Path


VIDEO_FORMATS = ("mp4", "mkv", "webm")
AUDIO_FORMATS = ("mp3", "m4a", "opus")


def prompt_download_type() -> str:
    while True:
        choice = input("Download type - Video (v) or Audio (a): ").strip().lower()
        if choice in {"v", "video"}:
            return "video"
        if choice in {"a", "audio"}:
            return "audio"
        print("Invalid selection. Enter v/video or a/audio.")


def prompt_format(download_type: str) -> str:
    formats = VIDEO_FORMATS if download_type == "video" else AUDIO_FORMATS
    while True:
        selected = input(f"Choose format ({'/'.join(formats)}): ").strip().lower()
        if selected in formats:
            return selected
        print(f"Invalid format. Choose one of: {', '.join(formats)}")


def prompt_output_directory() -> Path:
    while True:
        raw_path = input("Download location (folder path): ").strip().strip('"')
        if not raw_path:
            print("Location cannot be empty.")
            continue

        output_path = Path(os.path.expanduser(raw_path)).resolve()
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            return output_path
        except OSError as exc:
            print(f"Cannot use this location: {exc}")

def download_youtube_content():
    while True:
        print("\n--- YouTube Downloader ---")
        url = input("Enter the YouTube URL: ").strip()
        
        if not url:
            print("Error: URL cannot be empty.")
            continue

        download_type = prompt_download_type()
        selected_format = prompt_format(download_type)
        output_dir = prompt_output_directory()

        if download_type == "audio":
            print(f"Configuring for Audio ({selected_format.upper()})...")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': selected_format,
                    'preferredquality': '192',
                }],
            }
        else:
            print(f"Configuring for Video ({selected_format.upper()})...")
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best', 
                'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
                'merge_output_format': selected_format,
            }

        # Attempt the download
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n✅ Download completed successfully!")
            print(f"Saved in: {output_dir}")
            
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")

        # Ask to continue or exit
        again = input("\nDo you want to download another? (y/n): ").lower().strip()
        if again != 'y':
            print("Exiting...")
            break

if __name__ == "__main__":
    download_youtube_content()