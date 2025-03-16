#!/bin/bash

# ✅ Update package lists and install ffmpeg
apt-get update && apt-get install -y ffmpeg

# ✅ Start Gunicorn (Flask Server)
gunicorn -w 4 -b 0.0.0.0:$PORT app:app