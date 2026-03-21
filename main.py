import yt_dlp
import os
from pathlib import Path
VIDEO_FORMATS = ("mp4", "mkv", "webm")
AUDIO_FORMATS = ("mp3", "m4a", "opus")


def prompt_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Value cannot be empty. Please try again.")


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


def build_ydl_options(download_type: str, selected_format: str, output_dir: Path) -> dict:
    options = {
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
                "player_skip": ["webpage", "configs"],
            }
        },
    }

    if download_type == "audio":
        options.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": selected_format,
                        "preferredquality": "192",
                    }
                ],
            }
        )
    else:
        options.update(
            {
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": selected_format,
            }
        )

    return options


def download_youtube_content() -> None:
    print("\nYouTube Downloader CLI")

    while True:
        url = prompt_non_empty("Enter YouTube URL: ")
        download_type = prompt_download_type()
        selected_format = prompt_format(download_type)
        output_dir = prompt_output_directory()

        ydl_opts = build_ydl_options(download_type, selected_format, output_dir)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"Download completed. Saved in: {output_dir}")
        except Exception as exc:
            print(f"Download failed: {exc}")

        while True:
            again = input("Download another file? (yes/no): ").strip().lower()
            if again in {"yes", "y"}:
                break
            if again in {"no", "n"}:
                print("Exiting.")
                return
            print("Please enter yes or no.")


if __name__ == "__main__":
    download_youtube_content()