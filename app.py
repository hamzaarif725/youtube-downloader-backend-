from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import shutil  # ✅ Used to check if ffmpeg is installed

app = Flask(__name__)
CORS(app)  # ✅ Enables frontend-backend communication

# ✅ Check if ffmpeg is installed
if shutil.which("ffmpeg"):
    print("✅ ffmpeg is installed and available!")
else:
    print("⚠ WARNING: ffmpeg not found! The downloaded format may not be the best available.")

# ✅ Create downloads folder if not exists
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route("/")
def home():
    return "🚀 Flask backend is running with ffmpeg check!"

# 📌 Route to get video info from YouTube
@app.route("/get_video_info", methods=["POST"])
def get_video_info():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        video_data = {
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "description": info.get("description"),
            "video_id": info.get("id"),
        }
        return jsonify(video_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📌 Route to download the video
@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    video_id = data.get("video_id")

    if not video_id:
        return jsonify({"error": "No video ID provided"}), 400

    file_path = os.path.join(DOWNLOAD_FOLDER, f"{video_id}.mp4")

    # ✅ Check if video is already downloaded
    if os.path.exists(file_path):
        return jsonify({"message": "Video is already downloaded"}), 200

    try:
        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": file_path,
            "merge_output_format": "mp4",
            "quiet": False,  # ✅ Show logs for debugging
            "ffmpeg_location": "/usr/bin/ffmpeg"  # ✅ Force yt-dlp to use ffmpeg
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")  # ✅ Log the error
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
