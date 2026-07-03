# Demo

This folder contains the demo scenario and generated walkthrough video for CivicPulse.

- `SCENARIO.md`: narrative, demo flow, and voiceover script.
- `civicpulse_demo.mp4`: short visual walkthrough.

## Regenerate the Video

```bash
python scripts/generate_demo_video.py
```

The script creates slide images under `demo/frames/` and renders `demo/civicpulse_demo.mp4` with FFmpeg.
