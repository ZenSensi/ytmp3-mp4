import os
import uuid
import threading
import time
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)  # Allow all cross-origin requests from the frontend

TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_downloads")
os.makedirs(TEMP_DIR, exist_ok=True)


def delete_file_later(path, delay=90):
    """Delete a file after a delay to allow download to complete."""
    def _delete():
        time.sleep(delay)
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"[Cleanup] Failed to remove {path}: {e}")
    t = threading.Thread(target=_delete, daemon=True)
    t.start()


@app.get("/")
def index():
    return jsonify({"message": "YTMP4 Backend API is running."})


@app.get("/api/download")
def download_video():
    url = request.args.get("url", "").strip()
    fmt = request.args.get("format", "mp4").strip().lower()

    if not url:
        return jsonify({"error": "No URL provided."}), 400

    if fmt not in ("mp3", "mp4"):
        return jsonify({"error": "Invalid format. Choose 'mp3' or 'mp4'."}), 400

    unique_id = str(uuid.uuid4())
    out_template = os.path.join(TEMP_DIR, f"{unique_id}_%(title)s.%(ext)s")

    ydl_opts = {
        "outtmpl": out_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    if fmt == "mp3":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        # MP4 up to 1080p, forcing mp4 container
        ydl_opts.update({
            "format": "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[ext=mp4]/best",
            "merge_output_format": "mp4",
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            raw_path = ydl.prepare_filename(info)

        # Determine actual file path (extension might change for mp3)
        if fmt == "mp3":
            actual_path = os.path.splitext(raw_path)[0] + ".mp3"
        else:
            # mp4 or mkv (if ffmpeg merges to mkv as fallback)
            if not os.path.exists(raw_path):
                # Try .mp4
                base = os.path.splitext(raw_path)[0]
                for ext in [".mp4", ".mkv", ".webm"]:
                    candidate = base + ext
                    if os.path.exists(candidate):
                        actual_path = candidate
                        break
                else:
                    actual_path = raw_path  # Will fail below if not found
            else:
                actual_path = raw_path

        if not os.path.exists(actual_path):
            return jsonify({"error": "File could not be created. Check if ffmpeg is installed."}), 500

        # Sanitize title for filename
        title = info.get("title", "video")
        safe_title = "".join(c for c in title if c.isalnum() or c in " _-").strip() or "video"
        download_name = f"{safe_title}.{fmt}"

        # Schedule deletion after download
        delete_file_later(actual_path)

        return send_file(
            actual_path,
            as_attachment=True,
            download_name=download_name,
            mimetype="application/octet-stream"
        )

    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        if "Video unavailable" in msg or "Private video" in msg:
            return jsonify({"error": "Video is unavailable or private."}), 404
        if "age" in msg.lower():
            return jsonify({"error": "Video is age-restricted and cannot be downloaded."}), 403
        return jsonify({"error": "Could not download video. It may be restricted."}), 400
    except Exception as e:
        print(f"[Server Error] {e}")
        return jsonify({"error": "An internal server error occurred."}), 500


if __name__ == "__main__":
    print("Starting YTMP4 backend server at http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)
