# utils/image_utils.py
# Drawing functions for detection visualization
# Colored boxes, info panels, legend

import cv2
import base64
import numpy as np
import sys
import os
sys.path.insert(
    0, '/home/leopardtech/Desktop/mosaic-edge')
import config

# ─────────────────────────────────────────────
# COLORS (BGR format for OpenCV)
# ─────────────────────────────────────────────
COLOR_CONFIRMED = (0, 255, 0)       # Green
COLOR_UNCERTAIN = (0, 255, 255)     # Yellow
COLOR_MISSED    = (0, 0, 255)       # Red
COLOR_OBJECT    = (255, 100, 0)     # Blue
COLOR_TITLE     = (0, 255, 255)     # Cyan


# ─────────────────────────────────────────────
# ENCODE FRAME TO BASE64
# For sending uncertain images to cloud
# ─────────────────────────────────────────────
def encode_frame(frame):
    resized = cv2.resize(frame, (320, 240))
    _, buffer = cv2.imencode(
        '.jpg', resized,
        [cv2.IMWRITE_JPEG_QUALITY, 70])
    return base64.b64encode(
        buffer).decode('utf-8')


# ─────────────────────────────────────────────
# GET COLOR BY STATUS
# ─────────────────────────────────────────────
def get_status_color(status):
    return {
        'confirmed':              COLOR_CONFIRMED,
        'uncertain':              COLOR_UNCERTAIN,
        'possible_missed_victim': COLOR_MISSED
    }.get(status, (200, 200, 200))


# ─────────────────────────────────────────────
# DRAW PERSON BOUNDING BOX + INFO PANEL
# ─────────────────────────────────────────────
def draw_person_box(frame, idx, person,
                    pose_result, expr_result,
                    score_result):

    x1, y1, x2, y2 = [
        int(v) for v in person['bbox']]
    color  = get_status_color(
        score_result['status'])
    status = score_result['status'].upper()

    # Main bounding box
    cv2.rectangle(
        frame, (x1, y1), (x2, y2), color, 3)

    # Person number tag on box
    tag = f"P{idx + 1}"
    cv2.rectangle(
        frame,
        (x1, y1 - 22),
        (x1 + 28, y1),
        color, -1)
    cv2.putText(
        frame, tag,
        (x1 + 3, y1 - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55, (0, 0, 0), 2)

    # Info panel position
    # Put right of box or left if near edge
    panel_x = x2 + 8
    if panel_x + 220 > frame.shape[1]:
        panel_x = max(0, x1 - 228)

    panel_y = y1
    line_h  = 22

    # Build lines for info panel
    lines = [
        f"STATUS: {status}",
        f"PRIORITY: {score_result['priority']}",
        f"──────────────────",
        f"Score:  {score_result['final_score']}",
        f"YOLO:   {person['confidence']}",
        f"Pose:   {pose_result['pose_score']}",
        f"Expr:   {expr_result['expression_score']}",
        f"──────────────────",
        f"Expr: {expr_result['expression']}",
    ]

    # Add pose indicators
    for ind in pose_result.get('indicators', []):
        lines.append(f"• {ind}")

    panel_h = len(lines) * line_h + 16

    # Semi-transparent black background
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (panel_x, panel_y),
        (panel_x + 220, panel_y + panel_h),
        (0, 0, 0), -1)
    cv2.addWeighted(
        overlay, 0.75,
        frame, 0.25, 0, frame)

    # Panel border matching status color
    cv2.rectangle(
        frame,
        (panel_x, panel_y),
        (panel_x + 220, panel_y + panel_h),
        color, 1)

    # Priority colors
    priority_colors = {
        'CRITICAL': (0, 0, 255),
        'HIGH':     (0, 100, 255),
        'MEDIUM':   (0, 200, 255),
        'LOW':      (200, 200, 200)
    }

    # Draw each line in panel
    font = cv2.FONT_HERSHEY_SIMPLEX
    ty   = panel_y + 18

    for line in lines:
        if line.startswith("STATUS"):
            tc = color
            sc = 0.55
            wt = 2
        elif line.startswith("PRIORITY"):
            tc = priority_colors.get(
                score_result['priority'],
                (255, 255, 255))
            sc = 0.52
            wt = 1
        elif line.startswith("──"):
            tc = (80, 80, 80)
            sc = 0.45
            wt = 1
        elif line.startswith("•"):
            tc = (0, 220, 220)
            sc = 0.48
            wt = 1
        elif line.startswith("Expr:"):
            tc = (200, 200, 0)
            sc = 0.50
            wt = 1
        else:
            tc = (220, 220, 220)
            sc = 0.50
            wt = 1

        cv2.putText(
            frame, line,
            (panel_x + 6, ty),
            font, sc, tc, wt)
        ty += line_h

    return frame


# ─────────────────────────────────────────────
# DRAW OBJECT BOUNDING BOX (blue)
# ─────────────────────────────────────────────
def draw_object_box(frame, obj):
    x1, y1, x2, y2 = [
        int(v) for v in obj['bbox']]

    # Blue box
    cv2.rectangle(
        frame, (x1, y1), (x2, y2),
        COLOR_OBJECT, 2)

    label = f"{obj['class']} {obj['confidence']}"
    (tw, th), _ = cv2.getTextSize(
        label,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48, 1)

    # Label background
    cv2.rectangle(
        frame,
        (x1, y1 - th - 6),
        (x1 + tw + 4, y1),
        COLOR_OBJECT, -1)

    cv2.putText(
        frame, label,
        (x1 + 2, y1 - 4),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48, (255, 255, 255), 1)

    return frame


# ─────────────────────────────────────────────
# DRAW LEGEND (bottom right)
# ─────────────────────────────────────────────
def draw_legend(frame):
    h, w = frame.shape[:2]

    items = [
        (COLOR_CONFIRMED,
         f"CONFIRMED  >= {config.THRESHOLD}"),
        (COLOR_UNCERTAIN,
         f"UNCERTAIN  {config.FLOOR}"
         f" - {config.THRESHOLD}"),
        (COLOR_MISSED,
         f"MISSED     < {config.FLOOR}"),
        (COLOR_OBJECT,
         "OBJECT     non-person"),
    ]

    legend_w = 240
    legend_h = len(items) * 24 + 16
    lx = w - legend_w - 10
    ly = h - legend_h - 10

    # Semi-transparent background
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (lx, ly),
        (lx + legend_w, ly + legend_h),
        (0, 0, 0), -1)
    cv2.addWeighted(
        overlay, 0.75,
        frame, 0.25, 0, frame)

    font = cv2.FONT_HERSHEY_SIMPLEX
    ty   = ly + 18

    for color, label in items:
        # Color square
        cv2.rectangle(
            frame,
            (lx + 6, ty - 12),
            (lx + 22, ty + 4),
            color, -1)
        # Label text
        cv2.putText(
            frame, label,
            (lx + 28, ty),
            font, 0.47,
            (200, 200, 200), 1)
        ty += 24

    return frame


# ─────────────────────────────────────────────
# DRAW SUMMARY PANEL (top left)
# Shows all persons detected in frame
# ─────────────────────────────────────────────
def draw_summary_panel(frame, image_name,
                        person_results, objects):

    lines = [
        "MOSAIC EDGE AI",
        f"Persons: {len(person_results)}",
        f"Objects: {len(objects)}",
        "──────────────────────",
    ]

    for i, pr in enumerate(person_results):
        lines.append(
            f"P{i+1}: {pr['status']} "
            f"{pr['score']} [{pr['priority']}]"
        )

    if objects:
        lines.append("──────────────────────")
        for obj in objects:
            lines.append(
                f"  {obj['class']} "
                f"{obj['confidence']}"
            )

    lines.append("──────────────────────")
    lines.append(f"Threshold: {config.THRESHOLD}")
    lines.append(f"Floor:     {config.FLOOR}")

    panel_w  = 260
    line_h   = 22
    panel_h  = len(lines) * line_h + 16
    panel_x  = 10
    panel_y  = 10

    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (panel_x, panel_y),
        (panel_x + panel_w, panel_y + panel_h),
        (0, 0, 0), -1)
    cv2.addWeighted(
        overlay, 0.80,
        frame, 0.20, 0, frame)

    cv2.rectangle(
        frame,
        (panel_x, panel_y),
        (panel_x + panel_w, panel_y + panel_h),
        COLOR_TITLE, 1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    ty   = panel_y + 18

    for i, line in enumerate(lines):
        if i == 0:
            color = COLOR_TITLE
            scale = 0.65
            weight = 2
        elif line.startswith("──"):
            color = (80, 80, 80)
            scale = 0.45
            weight = 1
        elif 'CONFIRMED' in line:
            color = COLOR_CONFIRMED
            scale = 0.50
            weight = 1
        elif 'UNCERTAIN' in line:
            color = COLOR_UNCERTAIN
            scale = 0.50
            weight = 1
        elif 'MISSED' in line:
            color = COLOR_MISSED
            scale = 0.50
            weight = 1
        else:
            color = (200, 200, 200)
            scale = 0.50
            weight = 1

        cv2.putText(
            frame, line,
            (panel_x + 8, ty),
            font, scale, color, weight)
        ty += line_h

    return frame
