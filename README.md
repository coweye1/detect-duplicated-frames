# Detect Duplicated Frames (OBS Video Error Detector)

A Python script designed to automatically detect frame drops and screen freezes in OBS-recorded rhythm game videos (such as DDR, PIU, and Geometry Dash). 

When recording gameplay alongside a webcam, sometimes the game capture stutters while the webcam remains perfectly smooth at 60fps. This tool automates the quality control process by finding the exact timestamps where the game screen froze, saving you from the tedious task of manually checking a 60fps video frame-by-frame.

## ✨ Features
- **Targeted Analysis**: Analyzes only the game screen area (left 65% of the video) to prevent false positives from webcam movements.
- **GUI File Selection**: Easily select the `.mp4` video you want to analyze using a simple UI dialog.
- **Instant Freeze Detection**: Calculates pixel differences between consecutive frames to accurately pinpoint duplicated frames (stutters).
- **Gimmick & Black Screen Filtering**: Automatically ignores intentional in-game stop gimmicks or post-game black screens (continuous freezes of 4+ frames), focusing only on actual dropped frames.
- **Automated Reporting**: Generates a detailed `_에러리포트.txt` (Error Report) file in the same directory as the original video, logging the exact frame numbers and timestamps of suspected errors.

## 🛠️ Requirements
You need to install the following libraries to run this script:

```bash
pip install opencv-python numpy
