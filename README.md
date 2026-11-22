# YouTube Downloader (MP3 / MP4)

A small desktop app with a Tkinter interface for downloading YouTube videos and playlists as **MP3 audio** or **high-quality MP4 video**. It uses [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) in the background.

## Features

- Single video or whole playlist link
- MP3 (audio) or MP4 (best video + audio) output
- Choose the save folder
- List view with per-item status, downloads run in a background thread so the window does not freeze

## Requirements

- Python 3.9+
- `yt-dlp`
- **FFmpeg** — needed to merge video/audio and convert to MP3.
  On Windows, download a build from <https://www.gyan.dev/ffmpeg/builds/> and put `ffmpeg.exe` in the same folder as `main.py` (or add it to `PATH`).

## Run

```bash
pip install yt-dlp
python main.py
```

## Note

Only download content you have the right to download. Respect YouTube's Terms of Service and copyright.

## License

MIT — see [LICENSE](LICENSE).
