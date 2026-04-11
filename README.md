# ytmp3-mp4

A web-based YouTube downloader that lets you save videos as **MP3** (audio) or **MP4** (video) directly from your browser. Built with a Python/Flask backend and a clean frontend UI, with a one-click Windows startup script.

🔗 **Live Demo:** [ytmp3-mp4.vercel.app](https://ytmp3-mp4.vercel.app)

---

## Features

- Download YouTube videos as **MP3** or **MP4**
- Simple, clean browser-based UI
- Fast downloads powered by `yt-dlp`
- One-click server startup on Windows (`start_server.bat`)
- CORS-enabled Flask API — frontend and backend can run separately

---

## Tech Stack

| Layer    | Tech                          |
|----------|-------------------------------|
| Backend  | Python, Flask, yt-dlp         |
| Frontend | HTML, CSS, JavaScript         |
| CORS     | flask-cors                    |
| Deploy   | Vercel (frontend)             |

---

## Project Structure

```
ytmp3-mp4/
├── backend/          # Flask API server
├── frontend/         # Web UI (HTML/CSS/JS)
├── UI/               # Additional UI assets
├── requirements.txt  # Python dependencies
├── start_server.bat  # Windows startup script
└── test_download.py  # Download test script
```

---

## Getting Started

### Prerequisites

- Python 3.x
- `pip`
- `ffmpeg` (required by yt-dlp for audio conversion — [download here](https://ffmpeg.org/download.html))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ZenSensi/ytmp3-mp4.git
   cd ytmp3-mp4
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server**

   On Windows, just double-click `start_server.bat`, or run manually:
   ```bash
   cd backend
   python app.py
   ```

4. **Open the frontend**

   Open `frontend/index.html` in your browser, or serve it with any static file server.

---

## Usage

1. Paste a YouTube video URL into the input field.
2. Choose your desired format — **MP3** or **MP4**.
3. Click **Download** and wait for the file to be ready.

---

## Dependencies

```
flask
yt-dlp
flask-cors
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## Notes

- Make sure `ffmpeg` is installed and available in your system PATH for MP3 conversion to work.
- The backend runs locally — the Vercel deployment hosts the frontend only.
- For large videos, download times will vary based on your internet speed.

---

## License

This project is open source. Feel free to fork, modify, and build on it.
