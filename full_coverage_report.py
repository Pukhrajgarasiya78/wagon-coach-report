# full_coverage_report.py
# Combined: video splitting + PDF report generation
# Requirements: opencv-python, numpy, reportlab, pillow

import cv2
import numpy as np
import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

# =========================
#  VIDEO SPLITTING SECTION
# =========================

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def compute_profile(frame_gray):
    edges = cv2.Canny(frame_gray, 50, 150)
    profile = edges.sum(axis=0).astype(np.float32)
    kernel = 51
    profile = cv2.GaussianBlur(profile, (kernel|1, 1), 0)
    return profile

def find_valleys(profiles, min_distance=80, threshold_ratio=0.35):
    avg = np.mean(profiles, axis=0)
    avg_norm = (avg - avg.min()) / (avg.max() - avg.min() + 1e-9)
    valleys = []
    for i, v in enumerate(avg_norm):
        if v < threshold_ratio:
            valleys.append(i)
    if not valleys:
        return []
    groups, cur = [], [valleys[0]]
    for x in valleys[1:]:
        if x - cur[-1] <= min_distance//2:
            cur.append(x)
        else:
            groups.append(cur)
            cur = [x]
    groups.append(cur)
    centers = [int(np.mean(g)) for g in groups]
    return centers

def split_video_on_columns(video_path, out_dir, train_number="12309", sample_every_n_frames=30):
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Video: {video_path}, frames={total_frames}, fps={fps}, size={width}x{height}")

    profiles = []
    sample_idxs = list(range(0, total_frames, max(1, sample_every_n_frames)))
    for fi in sample_idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ok, frame = cap.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        profiles.append(compute_profile(gray))
    if not profiles:
        raise RuntimeError("No profiles computed — check video read.")

    centers = find_valleys(profiles, min_distance=int(0.02*width), threshold_ratio=0.20)
    print("Valley centers (x) =>", centers)

    split_x = [0] + centers + [width]
    split_intervals = [(split_x[i], split_x[i+1]) for i in range(len(split_x)-1)]
    merged = []
    for a,b in split_intervals:
        if merged and b - a < 0.1*width:
            prev_a, prev_b = merged.pop()
            merged.append((prev_a, b))
        else:
            merged.append((a,b))

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    frame_idx = 0
    writers = {}
    coach_idx = 1
    for seg in merged:
        folder = Path(out_dir) / f"{train_number}_{coach_idx}"
        ensure_dir(folder)
        out_path = folder / f"{train_number}_{coach_idx}.mp4"
        w, h = int(seg[1] - seg[0]), height
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writers[coach_idx] = {
            "writer": cv2.VideoWriter(str(out_path), fourcc, fps, (w,h)),
            "seg": seg,
            "folder": folder,
            "frame_counter": 0
        }
        coach_idx += 1

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        for idx, meta in writers.items():
            xa, xb = meta["seg"]
            crop = frame[:, int(xa):int(xb)]
            meta["writer"].write(crop)
            if frame_idx % 30 == 0:
                img_name = meta["folder"] / f"{train_number}_{idx}_{meta['frame_counter']+1}.jpg"
                cv2.imwrite(str(img_name), crop)
                meta['frame_counter'] += 1
        frame_idx += 1

    for meta in writers.values():
        meta["writer"].release()
    cap.release()
    print(f"Done. Created {len(writers)} coach folders")

# =========================
#  REPORT GENERATION SECTION
# =========================

BASE_INPUT = "Processed_Video"
REPORT_FOLDER = "Final Report---Assignment Submission"
REPORT_FILE = "Coverage_Report.pdf"

def collect_coach_data():
    base = Path(BASE_INPUT)
    if not base.exists():
        raise FileNotFoundError(f"Input folder '{BASE_INPUT}' not found.")
    coaches = []
    for folder in sorted(base.glob("*")):
        if folder.is_dir():
            imgs = sorted(folder.glob("*.jpg"))
            coaches.append({"name": folder.name, "images": imgs})
    return coaches

def generate_report(coaches):
    os.makedirs(REPORT_FOLDER, exist_ok=True)
    output_path = os.path.join(REPORT_FOLDER, REPORT_FILE)
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>Train Wagon Coverage Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(f"<b>Total Coaches Detected:</b> {len(coaches)}", styles["Normal"]))
    elements.append(Spacer(1, 0.1*inch))
    engine_guess = "Yes" if "engine" in coaches[0]["name"].lower() or len(coaches)==2 else "Unknown"
    elements.append(Paragraph(f"<b>Engine Present:</b> {engine_guess}", styles["Normal"]))
    elements.append(Spacer(1, 0.2*inch))

    data = [["Coach", "Frame Count"]]
    for coach in coaches:
        data.append([coach["name"], str(len(coach["images"]))])
    table = Table(data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))
    elements.append(table)
    elements.append(PageBreak())

    for coach in coaches:
        elements.append(Paragraph(f"<b>Coach: {coach['name']}</b>", styles["Heading2"]))
        elements.append(Spacer(1, 0.1*inch))
        thumbs = coach["images"][:6]
        if not thumbs:
            elements.append(Paragraph("No images found.", styles["Normal"]))
            elements.append(PageBreak())
            continue
        row = []
        img_rows = []
        for idx, img in enumerate(thumbs, start=1):
            row.append(Image(str(img), width=2.5*inch, height=1.5*inch))
            if idx % 2 == 0:
                img_rows.append(row)
                row = []
        if row:
            img_rows.append(row)
        for r in img_rows:
            elements.append(Table([r], hAlign='CENTER'))
            elements.append(Spacer(1, 0.2*inch))
        elements.append(PageBreak())

    doc.build(elements)
    print(f"[INFO] Report generated at: {output_path}")

# =========================
#  MAIN ENTRY POINT
# =========================

if __name__ == "__main__":
    DEFAULT_INPUT = r"Raw_video\DHN-wagon\train_sideview.mp4"
    DEFAULT_OUT = "Processed_Video"
    DEFAULT_TRAIN = "12309"

    print(f"[INFO] Using input video: {DEFAULT_INPUT}")
    print(f"[INFO] Output folder: {DEFAULT_OUT}")
    print(f"[INFO] Train number: {DEFAULT_TRAIN}")

    split_video_on_columns(DEFAULT_INPUT, DEFAULT_OUT, train_number=DEFAULT_TRAIN)

    coaches = collect_coach_data()
    generate_report(coaches)
