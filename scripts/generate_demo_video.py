from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "demo"
FRAMES_DIR = DEMO_DIR / "frames"
VIDEO_PATH = DEMO_DIR / "civicpulse_demo.mp4"
WIDTH = 1280
HEIGHT = 720


SLIDES = [
    {
        "title": "CivicPulse",
        "subtitle": "Algorithmic Fairness Auditing for Public Resource Allocation",
        "bullets": [
            "Scenario: housing-assistance applicants are prioritized by a scoring model",
            "Goal: detect whether district-level groups are treated differently",
            "Audience: city analysts, NGOs, and policy reviewers",
        ],
        "metric": "Model-agnostic audit",
    },
    {
        "title": "Fairness Warning",
        "subtitle": "The audit finds a large district-level approval gap",
        "bullets": [
            "North selection rate: 100.0%",
            "South selection rate: 33.3%",
            "Disparate impact ratio: 0.33",
        ],
        "metric": "0.33 DI",
    },
    {
        "title": "Metrics From Scratch",
        "subtitle": "CivicPulse computes standard fairness metrics directly in Python",
        "bullets": [
            "Disparate impact ratio",
            "Demographic parity difference",
            "Equal opportunity difference",
            "Equalized odds difference",
        ],
        "metric": "Custom fairness core",
    },
    {
        "title": "Explainability",
        "subtitle": "SHAP and LIME convert black-box scoring into inspectable evidence",
        "bullets": [
            "SHAP ranks the most influential features",
            "LIME explains a representative applicant decision",
            "Plain-English summaries help non-technical stakeholders",
        ],
        "metric": "SHAP + LIME",
    },
    {
        "title": "Mitigation Simulator",
        "subtitle": "Policy teams can compare fairness and accuracy trade-offs",
        "bullets": [
            "Baseline threshold: parity gap 66.7%",
            "Group threshold adjustment: parity gap 0.0%",
            "Reweighting proxy: parity gap 50.0%",
        ],
        "metric": "Before / after",
    },
    {
        "title": "Deep ML Benchmark",
        "subtitle": "Compare standard models with adversarial debiasing",
        "bullets": [
            "Logistic regression: transparent baseline",
            "XGBoost: strong tabular baseline",
            "PyTorch adversarial network: fairness-aware deep learning",
        ],
        "metric": "PyTorch adversarial debiasing",
    },
    {
        "title": "Stakeholder Workflow",
        "subtitle": "Export, publish, and brief decision-makers",
        "bullets": [
            "Download Power BI-ready CSVs",
            "Persist audit runs to Supabase",
            "Publish a Kaggle fairness-audit notebook",
        ],
        "metric": "Audit-ready evidence",
    },
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, max_width: int, text_font: ImageFont.ImageFont) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textbbox((0, 0), trial, font=text_font)[2] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_slide(slide: dict[str, object], index: int) -> Path:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#f8fafc")
    draw = ImageDraw.Draw(image)

    teal = "#155e75"
    clay = "#b45309"
    ink = "#122024"
    slate = "#475569"
    border = "#cbd5e1"

    draw.rectangle((0, 0, WIDTH, 86), fill="#ffffff")
    draw.rounded_rectangle((38, 22, 92, 76), radius=8, fill=teal)
    draw.text((54, 32), "CP", fill="white", font=font(18, True))
    draw.text((112, 22), "CivicPulse", fill=ink, font=font(28, True))
    draw.text((112, 56), "Fairness audit demo", fill=slate, font=font(16))

    draw.text((60, 138), str(slide["title"]), fill=ink, font=font(54, True))
    draw.text((64, 210), str(slide["subtitle"]), fill=slate, font=font(25))

    y = 304
    bullet_font = font(25)
    for bullet in slide["bullets"]:  # type: ignore[index]
        draw.ellipse((70, y + 10, 82, y + 22), fill=clay)
        for line in wrap(draw, str(bullet), 700, bullet_font):
            draw.text((104, y), line, fill=ink, font=bullet_font)
            y += 38
        y += 18

    draw.rounded_rectangle((860, 210, 1200, 520), radius=8, fill="#ffffff", outline=border, width=2)
    draw.text((896, 250), "Key signal", fill=slate, font=font(18, True))
    metric_lines = wrap(draw, str(slide["metric"]), 260, font(34, True))
    metric_y = 318
    for line in metric_lines:
        draw.text((896, metric_y), line, fill=teal, font=font(34, True))
        metric_y += 48

    progress_width = int((index + 1) / len(SLIDES) * 1080)
    draw.rounded_rectangle((100, 646, 1180, 658), radius=6, fill="#e2e8f0")
    draw.rounded_rectangle((100, 646, 100 + progress_width, 658), radius=6, fill=teal)
    draw.text((100, 672), f"{index + 1}/{len(SLIDES)}", fill=slate, font=font(16, True))

    frame_path = FRAMES_DIR / f"slide_{index + 1:02d}.png"
    image.save(frame_path)
    return frame_path


def main() -> None:
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    for old_frame in FRAMES_DIR.glob("slide_*.png"):
        old_frame.unlink()

    for index, slide in enumerate(SLIDES):
        draw_slide(slide, index)

    command = [
        "ffmpeg",
        "-y",
        "-framerate",
        "1/3",
        "-i",
        str(FRAMES_DIR / "slide_%02d.png"),
        "-vf",
        "format=yuv420p,fps=30",
        "-c:v",
        "libx264",
        "-movflags",
        "+faststart",
        str(VIDEO_PATH),
    ]
    subprocess.run(command, check=True)
    print(f"Wrote {VIDEO_PATH}")


if __name__ == "__main__":
    main()
