import os
import uuid
import threading
import time
from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp

# Point Flask's static/template folder to the frontend directory
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_downloads")
os.makedirs(TEMP_DIR, exist_ok=True)

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)


def delete_file_later(path, delay=120):
    """Delete a temp file after a delay so the download can complete."""

    def _delete():
        time.sleep(delay)
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"[Cleanup] Removed: {path}")
        except Exception as e:
            print(f"[Cleanup Error] {e}")

    threading.Thread(target=_delete, daemon=True).start()


# ─── Serve the frontend ────────────────────────────────────────────────────────


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# ─── Download / Convert API ────────────────────────────────────────────────────


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
        "quiet": False,  # Enable logs for debugging
        "no_warnings": False,
    }

    if fmt == "mp3":
        # Best audio quality → converted to MP3 192kbps via ffmpeg
        ydl_opts.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
        )
    else:
        # Best video quality (up to 4K/2160p) + best audio → merged into mp4
        # YouTube serves 4K as separate video+audio streams, ffmpeg merges them
        ydl_opts.update(
            {
                "format": (
                    "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                    "bestvideo+bestaudio/"
                    "best[ext=mp4]/"
                    "best"
                ),
                "merge_output_format": "mp4",
            }
        )

    try:
        print(f"[Download] Starting: url={url!r}, format={fmt!r}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            raw_path = ydl.prepare_filename(info)

        print(f"[Download] Raw path from yt-dlp: {raw_path}")

        # Determine the actual file path (extension can differ for mp3)
        if fmt == "mp3":
            actual_path = os.path.splitext(raw_path)[0] + ".mp3"
        else:
            if os.path.exists(raw_path):
                actual_path = raw_path
            else:
                base = os.path.splitext(raw_path)[0]
                actual_path = raw_path  # fallback
                for ext in [".mp4", ".mkv", ".webm", ".m4v"]:
                    candidate = base + ext
                    if os.path.exists(candidate):
                        actual_path = candidate
                        break

        print(f"[Download] Actual file path: {actual_path}")

        if not os.path.exists(actual_path):
            print(f"[Error] File not found: {actual_path}")
            # List what's in TEMP_DIR to diagnose
            files = os.listdir(TEMP_DIR)
            matching = [f for f in files if f.startswith(unique_id)]
            print(f"[Debug] Matching temp files: {matching}")
            return jsonify({"error": "File conversion failed. Please try again."}), 500

        # Sanitize title for a safe download filename
        title = info.get("title", "video")
        safe_title = (
            "".join(c for c in title if c.isalnum() or c in " _-").strip() or "video"
        )
        download_name = f"{safe_title}.{fmt}"

        print(f"[Download] Serving file: {actual_path} as {download_name!r}")
        delete_file_later(actual_path)

        return send_file(
            actual_path,
            as_attachment=True,
            download_name=download_name,
            mimetype="application/octet-stream",
        )

    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        print(f"[yt-dlp DownloadError] {msg}")
        if "Video unavailable" in msg or "Private video" in msg:
            return jsonify({"error": "❌ Video is unavailable or private."}), 404
        if "age" in msg.lower():
            return jsonify({"error": "❌ Video is age-restricted."}), 403
        if "Sign in" in msg or "login" in msg.lower():
            return jsonify(
                {"error": "❌ This video requires sign-in and cannot be downloaded."}
            ), 403
        return jsonify({"error": f"❌ Could not download: {msg[:200]}"}), 400
    except Exception as e:
        print(f"[Server Error] {type(e).__name__}: {e}")
        return jsonify({"error": f"❌ Internal server error: {str(e)[:200]}"}), 500


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("=" * 55)
    print(f"  YTMP4 Server running at:  http://localhost:{port}")
    print("  Open the above URL in your browser to use the app.")
    print("=" * 55)
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
