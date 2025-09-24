🚆 Wagon Coach Counting & Full-Coverage Report

This project processes side-view train videos to automatically:

✅ Split the train video into smaller segments, one per coach (or engine).
✅ Count the number of coaches in the train.
✅ Extract representative frames for each coach to ensure full coverage from nose to tail.
✅ Generate a structured PDF report summarizing the coach count and embedding selected images for easy inspection.

📌 Project Overview

Imagine a CCTV camera installed at a railway station that records an entire train passing by.
This project builds a video processing pipeline that:

Detects vertical "valleys" (gaps between coaches) using image profiles.

Splits the video into per-coach video clips.

Extracts frames periodically (e.g., every 30 frames) to get minimal but complete coverage.

Organizes output into folders like:

Processed_Video/
 ├── 12309_1/
 │   ├── 12309_1.mp4
 │   ├── 12309_1_1.jpg
 │   └── 12309_1_2.jpg
 ├── 12309_2/
 │   └── ...


Generates a report in PDF format with:

Total coach count

Summary table (coach name + frame count)

Image thumbnails for each coach (ensuring full coverage)

🖼 Example Output

Summary Page (Auto-Generated PDF)

Total coaches detected

Table listing each coach and number of frames captured

Coach Pages

A set of images (2 per row) showing coverage for that coach

Works for engines and wagons

📂 Project Structure
.
├── full_coverage_report.py     # Main script (splits + generates report)
├── Raw_video/
│   └── DHN-wagon/train_sideview.mp4   # Input video (example)
├── Processed_Video/            # Auto-generated output (coach-wise)
├── Final Report---Assignment Submission/
│   └── Coverage_Report.pdf      # Auto-generated final PDF report
└── README.md

🛠 Tech Stack

Python 3.x

OpenCV – Video reading, splitting, frame extraction

NumPy – Profile computation and valley detection

ReportLab – PDF report generation

Pillow – Image handling

⚙️ Installation

Clone the repository:

git clone https://github.com/Pukhrajgarasiya78/wagon-coach-report.git
cd wagon-coach-report


Install dependencies:

pip install opencv-python numpy reportlab pillow

▶️ Usage

Run the main script directly:

python full_coverage_report.py


This will:

Process Raw_video/DHN-wagon/train_sideview.mp4

Create coach-wise folders inside Processed_Video/

Generate a PDF report inside Final Report---Assignment Submission/

📊 Sample Report

Page 1: Summary table with coach count

Subsequent Pages: Thumbnails of each coach (first 6 frames only)

Ensures color consistency and full coverage per coach

🚀 Features

🔎 Automatic coach detection – no manual splitting

🎞 Minimal frame extraction – saves space but ensures coverage

🗂 Organized folder structure – per-coach media neatly grouped

📄 Professional PDF output – ready for analysis or submission

📌 Future Enhancements

CLI arguments: --video, --train_number for flexibility

Detect open/closed doors using object detection (YOLO/Faster R-CNN)

Add engine/wagon classification (separate engines from coaches)

Export report to HTML format for interactive viewing

📜 License

This project is licensed under the MIT License – free to use, modify, and distribute.
