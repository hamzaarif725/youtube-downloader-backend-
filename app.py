from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import yt_dlp

app = Flask(__name__)
CORS(app)

# Directory to store downloads
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/get_video_info', methods=['POST'])
def get_video_info():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "No URL provided"}), 400

        url = data["url"]
        
        # Extract video info using yt-dlp
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return jsonify({
            "title": info["title"],
            "thumbnail": info["thumbnail"],
            "description": info.get("description", "No description available"),
            "video_id": info["id"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        if not data or 'video_id' not in data:
            return jsonify({"error": "No video ID provided"}), 400

        video_id = data["video_id"]
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        final_output = os.path.join(DOWNLOAD_FOLDER, f"{video_id}.mp4")

        # ✅ Check if the video is already downloaded
        if os.path.exists(final_output):
            return jsonify({"message": "Video is already downloaded", "file_path": final_output}), 200

        # Download options: H.264 video + AAC audio
        video_opts = {
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, f"{video_id}.%(ext)s"),
            "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
        }

        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([youtube_url])

        # Ensure the file exists before sending
        if not os.path.exists(final_output):
            return jsonify({"error": "Merged file not found"}), 500

        # Send the merged MP4 file to frontend
        return send_file(final_output, as_attachment=True, mimetype="video/mp4")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
