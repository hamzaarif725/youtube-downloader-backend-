#!/bin/bash

# ✅ Install ffmpeg using Nix (compatible with Railway)
nix-env -iA nixpkgs.ffmpeg

# ✅ Start the Flask server using Gunicorn
gunicorn -w 4 -b 0.0.0.0:$PORT app:app
