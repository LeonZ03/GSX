"""Local pixel audit for photos 57/58/59/60/61/65.

The output contains only image dimensions, wheel ROI coordinates, arc samples and
fit diagnostics. Source pixels are never written. No formal calibration is read
back into or overwritten, and no body pixels are used in the solver.
"""
from pathlib import Path
import sys, json, math
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "reconstruction_v2"
sys.path.insert(0, str(ROOT / ".tools/calibration"))
import numpy as np
import cv2
from scipy.optimize import least_squares
from fit_cameras import solve

OUT = V2 / "qa/stage_b_evidence/stage_b_holdout_corrected.json"
IDS = [57, 58, 59, 60, 61, 65]


def photo(n):
    return next(ROOT.glob(f"IMG/*_{n}_97.jpg"))


def components(rgb):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([55, 255, 255]))
    _n, lab, stats, cents = cv2.connectedComponentsWithStats(mask)
    out = []
    for st, ce in zip(stats[1:], cents[1:]):
        x, y, w, h, area = map(int, st)
        if area >= 80:
            out.append({"bbox": [x, y, w, h], "area": area,
                        "center": [round(float(ce[0]), 2), round(float(ce[1]), 2)]})
    return sorted(out, key=lambda x: x["area"], reverse=True)


def arc_for(rgb, box):
    x, y, w, h = box
    hsv = cv2.cvtColor(rgb[y:y+h, x:x+w], cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([55, 255, 255]))
    yy, xx = np.where(mask > 0)
    if len(xx) < 30:
        return {"points": [], "ellipse": None, "coverage_deg": 0.0}
    pts = np.column_stack([xx+x, yy+y]).astype(np.float32)
    ellipse = cv2.fitEllipse(pts) if len(pts) >= 5 else None
    cen = np.array(ellipse[0]) if ellipse else np.median(pts, axis=0)
    ang = np.arctan2(pts[:, 1]-cen[1], pts[:, 0]-cen[0])
    samples = []
    occupied = []
    for t in np.arange(-math.pi, math.pi, math.radians(5)):
        d = np.arctan2(np.sin(ang-t), np.cos(ang-t))
        sel = pts[np.abs(d) < math.radians(2.5)]
        if len(sel) >= 3:
            samples.append(np.median(sel, axis=0).round(2).tolist())
            occupied.append(t)
    coverage = len(occupied) * 5.0
    return {"points": samples, "ellipse": ellipse, "coverage_deg": round(coverage, 1), "pixel_count": int(len(pts))}


def main():
    report = {"privacy": "pixel coordinates/statistics only; no source pixels or plate data", "formal_calibration_modified": False, "body_fit_used": False, "views": {}}
    for n in IDS:
        p = photo(n); rgb = np.array(Image.open(p).convert("RGB")); h, w = rgb.shape[:2]
        comps = components(rgb)
        row = {"image_size": [w, h], "fluorescent_components": comps[:20], "wheel_rois": {}, "fit": None}
        # 61 has two large lower wheel components; these are explicit pixel ROIs.
        if n == 61:
            boxes = json.loads((OUT.parent / "roi_config.local.json").read_text())[str(n)]
            for k, b in boxes.items():
                row["wheel_rois"][k] = {"bbox": b, **arc_for(rgb, b)}
            ann = {"image_id": 61, "image_size": [w, h], "role": "holdout_candidate", "side": "right", "steering_model":"raked_axis_25_6_trail104",
                   "wheels": {k: {"rim_points": v["points"], "center": None} for k, v in row["wheel_rois"].items()}}
            if all(len(x["rim_points"]) >= 5 for x in ann["wheels"].values()):
                try:
                    row["fit"] = solve(ann)
                    row["fit"]["status"] = "diagnostic_only_unverified_arc_segmentation"
                except Exception as e:
                    row["fit"] = {"status": "no_physical_solution", "error": str(e)}
            else:
                row["fit"] = {"status": "insufficient_arc_samples", "reason": "one or both wheel ROIs have fewer than five angular bins"}
        else:
            # Do not guess axle centres or assign components as wheels for other views.
            row["fit"] = {"status": "not_attempted", "reason": "No manually reviewed two-wheel ROI; connected components alone cannot identify axle arcs."}
        report["views"][str(n)] = row
    report["conclusion"] = "61 has two candidate lower-image fluorescent ROIs and a wheel-only diagnostic fit, but the segmentation/ROI assignment is not manually accepted and therefore is not a scorable independent camera. Other views require manual ROI review before a fit; no independent pair is promoted."
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "views": len(IDS), "61_fit": report["views"]["61"]["fit"] and report["views"]["61"]["fit"].get("status")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
