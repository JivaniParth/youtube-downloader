import yt_dlp
import os

def download_youtube_content():
    while True:
        print("\n--- YouTube Downloader ---")
        url = input("Enter the YouTube URL: ").strip()
        
        if not url:
            print("Error: URL cannot be empty.")
            continue

        # Ask the user for their preference
        choice = input("Do you want to save Video (v) or Audio (a)? ").lower().strip()
        
        # Define options for yt-dlp based on user choice
        ydl_opts = {}

        if choice == 'a' or choice == 'audio':
            print("Configuring for Audio (MP3)...")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': '%(title)s.%(ext)s',  # Save file as "VideoTitle.mp3"
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            
        elif choice == 'v' or choice == 'video':
            print("Configuring for Video (Highest Quality)...")
            ydl_opts = {
                # 'bestvideo+bestaudio' downloads the best separate streams and merges them 
                # (requires FFmpeg). If unavailable, falls back to 'best' single file.
                'format': 'bestvideo+bestaudio/best', 
                'outtmpl': '%(title)s.%(ext)s',
            }
            
        else:
            print("Invalid selection. Please enter 'v' or 'a'.")
            continue

        # Attempt the download
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n✅ Download completed successfully!")
            
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")

        # Ask to continue or exit
        again = input("\nDo you want to download another? (y/n): ").lower().strip()
        if again != 'y':
            print("Exiting...")
            break

if __name__ == "__main__":
    download_youtube_content()