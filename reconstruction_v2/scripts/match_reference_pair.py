"""Real SIFT correspondence extraction for the 62/63 reference photographs.

The script deliberately reports only detector-derived correspondences.  It uses
the annotated privacy/luggage exclusions, a conservative vehicle ROI, mutual
ratio matching, and a robust fundamental-matrix fit.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.tools' / 'calibration'))
import cv2
import numpy as np


PYRAMID = {
    62: (150, 600, 1279, 1350),
    63: (60, 600, 1260, 1570),
}


def load_annotation(n: int) -> dict:
    return json.loads((ROOT / "reconstruction_v2" / "annotations" / f"photo_{n}.json").read_text(encoding="utf-8"))


def mask_for(n: int, shape: tuple[int, int]) -> np.ndarray:
    h, w = shape
    mask = np.zeros((h, w), np.uint8)
    x0, y0, x1, y1 = PYRAMID[n]
    mask[max(0, y0):min(h, y1 + 1), max(0, x0):min(w, x1 + 1)] = 255
    ann = load_annotation(n)
    for item in ann.get("exclude_polygons", []):
        poly = np.asarray(item["polygon"], np.int32)
        cv2.fillPoly(mask, [poly], 0)
    # 62 has an explicit privacy strip even if a caller changes the ROI.
    if n == 62:
        mask[: min(1050, h), : min(150, w)] = 0
    return mask


def image_path(n: int) -> Path:
    candidates = sorted((ROOT / "IMG").glob(f"*_{n}_97.jpg"))
    if len(candidates) != 1:
        raise FileNotFoundError(f"expected one IMG/*_{n}_97.jpg, got {candidates}")
    return candidates[0]


def region(n: int, x: float, y: float) -> str:
    x0, y0, x1, y1 = PYRAMID[n]
    if x < x0 + (x1 - x0) / 3:
        col = "rear"
    elif x < x0 + 2 * (x1 - x0) / 3:
        col = "mid"
    else:
        col = "front"
    if y < y0 + (y1 - y0) / 2:
        row = "upper"
    else:
        row = "lower"
    return f"{row}_{col}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(ROOT / "reconstruction_v2" / "calibration" / "feature_matches_62_63.json"))
    ap.add_argument("--image", default=str(ROOT / "reconstruction_v2" / "renders" / "matches_62_63.jpg"))
    ap.add_argument("--max-matches", type=int, default=300)
    args = ap.parse_args()

    p62, p63 = image_path(62), image_path(63)
    im62 = cv2.imdecode(np.fromfile(str(p62), dtype=np.uint8), cv2.IMREAD_COLOR)
    im63 = cv2.imdecode(np.fromfile(str(p63), dtype=np.uint8), cv2.IMREAD_COLOR)
    if im62 is None or im63 is None:
        raise RuntimeError("failed to read input photographs")
    gray62, gray63 = cv2.cvtColor(im62, cv2.COLOR_BGR2GRAY), cv2.cvtColor(im63, cv2.COLOR_BGR2GRAY)
    m62, m63 = mask_for(62, gray62.shape), mask_for(63, gray63.shape)
    sift = cv2.SIFT_create(nfeatures=8000, contrastThreshold=0.025, edgeThreshold=10)
    k62, d62 = sift.detectAndCompute(gray62, m62)
    k63, d63 = sift.detectAndCompute(gray63, m63)
    if d62 is None or d63 is None:
        raise RuntimeError("SIFT found no descriptors in one ROI")
    matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    fwd = matcher.knnMatch(d62, d63, k=2)
    rev = matcher.knnMatch(d63, d62, k=2)
    ratio = 0.78
    best_fwd = {m.queryIdx: m for m, n in fwd if m.distance < ratio * n.distance}
    best_rev = {m.queryIdx: m for m, n in rev if m.distance < ratio * n.distance}
    mutual = [m for qi, m in best_fwd.items() if m.trainIdx in best_rev and best_rev[m.trainIdx].trainIdx == qi]
    mutual.sort(key=lambda m: m.distance)
    pts62 = np.float32([k62[m.queryIdx].pt for m in mutual])
    pts63 = np.float32([k63[m.trainIdx].pt for m in mutual])
    F = None
    inlier_mask = np.zeros(len(mutual), np.uint8)
    method_name = "none"
    if len(mutual) >= 8:
        method = getattr(cv2, "USAC_MAGSAC", cv2.RANSAC)
        method_name = "USAC_MAGSAC" if method != cv2.RANSAC else "RANSAC"
        F, inlier_mask = cv2.findFundamentalMat(pts62, pts63, method, 1.5, 0.999, 10000)
        if F is None or F.shape != (3, 3):
            F, inlier_mask = cv2.findFundamentalMat(pts62, pts63, cv2.RANSAC, 1.5, 0.999, 10000)
            method_name = "RANSAC" if F is not None else "none"
    inlier_mask = np.asarray(inlier_mask).reshape(-1).astype(bool) if len(mutual) else np.zeros(0, bool)
    if F is None:
        F = np.zeros((3, 3), dtype=float)
    F = np.asarray(F, dtype=float)
    # Sampson distance, in squared pixels, for the accepted correspondences.
    good = [i for i, ok in enumerate(inlier_mask) if ok]
    x1 = np.c_[pts62[good], np.ones(len(good))] if good else np.empty((0, 3))
    x2 = np.c_[pts63[good], np.ones(len(good))] if good else np.empty((0, 3))
    sampson = []
    if good:
        Fx1 = (F @ x1.T).T
        Ftx2 = (F.T @ x2.T).T
        x2Fx1 = np.sum(x2 * Fx1, axis=1)
        sampson = ((x2Fx1 * x2Fx1) / (Fx1[:, 0] ** 2 + Fx1[:, 1] ** 2 + Ftx2[:, 0] ** 2 + Ftx2[:, 1] ** 2 + 1e-12)).tolist()
    matches = []
    for j, i in enumerate(good):
        m = mutual[i]
        a, b = k62[m.queryIdx].pt, k63[m.trainIdx].pt
        matches.append({"point": [round(a[0], 3), round(a[1], 3), round(b[0], 3), round(b[1], 3)],
                        "descriptor_distance": round(float(m.distance), 5),
                        "sampson_residual_px2": round(float(sampson[j]), 6),
                        "region_62": region(62, *a), "region_63": region(63, *b)})
    # Keep the most spatially useful subset: low descriptor distance, then grid spread.
    if len(matches) > args.max_matches:
        matches = sorted(matches, key=lambda z: (z["sampson_residual_px2"], z["descriptor_distance"]))[:args.max_matches]
    coverage = {}
    for z in matches:
        coverage[z["region_62"]] = coverage.get(z["region_62"], 0) + 1
    out = {"schema": "gsx-reference-feature-matches-v1", "image_ids": [62, 63],
           "images": {"62": str(p62.relative_to(ROOT)).replace("\\", "/"), "63": str(p63.relative_to(ROOT)).replace("\\", "/")},
           "image_size": [int(im62.shape[1]), int(im62.shape[0])], "roi_xyxy": {"62": PYRAMID[62], "63": PYRAMID[63]},
           "detector": {"name": "SIFT", "keypoints": {"62": len(k62), "63": len(k63)}, "ratio_threshold": ratio,
                        "mutual_ratio_candidates": len(mutual), "fundamental_method": method_name, "inliers_before_cap": len(good)},
           "fundamental_matrix": F.tolist(), "matches": matches, "coverage_region_62": coverage,
           "notes": "All points are detector-derived; no synthetic rim/circle points. Exclusion polygons and privacy mask applied."}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # Side-by-side local QA image. Privacy and exclusions remain black; no source pixels are exported outside ROI.
    left, right = im62.copy(), im63.copy()
    left[m62 == 0] = (0, 0, 0)
    right[m63 == 0] = (0, 0, 0)
    canvas = np.hstack([left, right])
    for z in matches:
        x1, y1, x2, y2 = z["point"]
        p1, p2 = (int(round(x1)), int(round(y1))), (int(round(x2)) + im62.shape[1], int(round(y2)))
        cv2.circle(canvas, p1, 3, (0, 255, 255), -1)
        cv2.circle(canvas, p2, 3, (0, 255, 255), -1)
        cv2.line(canvas, p1, p2, (255, 180, 0), 1, cv2.LINE_AA)
    cv2.putText(canvas, f"62/63 SIFT mutual+{method_name} inliers: {len(matches)}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
    Path(args.image).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(args.image, canvas, [cv2.IMWRITE_JPEG_QUALITY, 92])


if __name__ == "__main__":
    main()





