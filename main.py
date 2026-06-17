import argparse
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
        choice = input("\nDownload type - Video (v) or Audio (a): ").strip().lower()
        if choice in {"v", "video", "Video"}:
            return "video"
        if choice in {"a", "audio", "Audio"}:
            return "audio"
        print("\nInvalid selection. Enter v/video/Video or a/audio/Audio.")


def prompt_format(download_type: str) -> str:
    formats = VIDEO_FORMATS if download_type == "video" else AUDIO_FORMATS
    while True:
        selected = input(f"\nChoose format ({'/'.join(formats)}): ").strip().lower()
        if selected in formats:
            return selected
        print(f"\nInvalid format. Choose one of: {', '.join(formats)}")


def prompt_output_directory() -> Path:
    while True:
        raw_path = input("\nDownload location (folder path): ").strip().strip('"')
        if not raw_path:
            print("\nLocation cannot be empty.")
            continue

        output_path = Path(os.path.expanduser(raw_path)).resolve()
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            return output_path
        except OSError as exc:
            print(f"\nCannot use this location: {exc}")


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ytdownload",
        description="YouTube Downloader CLI",
    )
    parser.add_argument(
        "url",
        nargs="?",
        default=None,
        help="YouTube URL to download. If omitted, you'll be prompted for it.",
    )
    return parser.parse_args()


def download_youtube_content() -> None:
    print("\nYouTube Downloader CLI")
    args = parse_args()
    pending_url = args.url

    while True:
        if pending_url:
            url = pending_url
            pending_url = None
        else:
            url = prompt_non_empty("\nEnter YouTube URL: ")
        download_type = prompt_download_type()
        selected_format = prompt_format(download_type)
        output_dir = prompt_output_directory()

        ydl_opts = build_ydl_options(download_type, selected_format, output_dir)
        print()

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"\nDownload completed. Saved in: {output_dir}")
        except Exception as exc:
            print(f"\nDownload failed: {exc}")

        while True:
            again = input("\nDownload another file? (yes/no): ").strip().lower()
            if again in {"yes", "y"}:
                break
            if again in {"no", "n"}:
                print("\nExiting.")
                return
            print("\nPlease enter yes or no.")


if __name__ == "__main__":
    download_youtube_content()