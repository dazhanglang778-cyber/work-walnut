from __future__ import annotations

# Copyright (C) 2026 dazhanglang
# SPDX-License-Identifier: GPL-3.0-only

import ctypes
import json
import math
import random
import re
import sys
import time
import tkinter as tk
from datetime import date
from pathlib import Path

if sys.platform == "win32":
    from ctypes import wintypes

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageTk


APP_DIR = Path(__file__).resolve().parent
ASSET_DIR = APP_DIR / "assets"
CONFIG_PATH = APP_DIR / "config.json"
TRANSPARENT_KEY = "#ff00ff"

STATE_FILES = [
    "wallnut-healthy.png",
    "wallnut-tired.png",
    "wallnut-injured.png",
    "tallnut-ninja.png",
    "tallnut-critical.png",
    "wallnut-crazy.png",
    "wallnut-redhot.png",
]
STATE_LABELS = ["正常", "轻伤", "受伤", "海盗", "重伤", "疯狂", "红温"]
GREEN_MESSAGE_FILES = [
    "green-message-zombie.png",
    "green-message-player.png",
]


class WallnutPet:
    def __init__(self) -> None:
        self.config = self.load_config()
        self.root = tk.Tk()
        self.root.title("工作坚果")
        self.windowing_system = str(
            self.root.tk.call("tk", "windowingsystem")
        ).lower()
        self.transparent_bg = (
            "systemTransparent"
            if self.windowing_system == "aqua"
            else TRANSPARENT_KEY
        )
        self.configure_transparent_window(self.root)

        self.window_size = int(self.config["window_size"])
        self.pet_size = int(self.config["pet_size"])
        self.canvas = tk.Canvas(
            self.root,
            width=self.window_size,
            height=self.window_size,
            bg=self.transparent_bg,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()
        self.image_item = self.canvas.create_image(
            self.window_size // 2,
            self.window_size // 2,
            anchor="center",
        )

        self.base_images = [self.load_pet_image(ASSET_DIR / name) for name in STATE_FILES]
        self.green_message_images = [
            self.load_green_message_image(ASSET_DIR / name)
            for name in GREEN_MESSAGE_FILES
        ]
        self.current_state = 0
        self.current_photo: ImageTk.PhotoImage | None = None
        self.roll_frame_cache: dict[tuple[int, int], list[ImageTk.PhotoImage]] = {}
        self.bubble_window: tk.Toplevel | None = None
        self.bubble_canvas: tk.Canvas | None = None
        self.bubble_item: int | None = None
        self.bubble_photo: ImageTk.PhotoImage | None = None
        self.bubble_text = ""
        self.bubble_tail_up = False
        self.bubble_size = (174, 82)
        self.green_message_window: tk.Toplevel | None = None
        self.green_message_canvas: tk.Canvas | None = None
        self.green_message_photo: ImageTk.PhotoImage | None = None
        self.green_message_size = (0, 0)
        self.green_message_shown = False
        self.animating = False
        self.canvas_offset_x = 0.0
        self.canvas_offset_y = 0.0
        self.wobble_enabled = True
        self.session_started = time.monotonic()
        self.session_date = date.today()
        self.active_elapsed_seconds = 0.0
        self.last_fatigue_check = time.monotonic()
        self.manual_state_until = 0.0

        self.press_screen = (0, 0)
        self.press_window = (0, 0)
        self.dragged = False
        self.pending_click: str | None = None
        self.right_click_job: str | None = None
        self.wobble_job: str | None = None

        self.menu = self.build_menu()
        self.position_near_bottom_right()
        self.show_pose()
        self.bind_events()
        self.schedule_wobble()
        self.root.after(500, self.preload_current_roll_frames)
        self.root.after(10_000, self.update_fatigue)

    def load_config(self) -> dict:
        defaults = {
            "window_size": 200,
            "pet_size": 96,
            "drag_threshold_pixels": 18,
            "wobble_interval_seconds": [6, 14],
            "roll_distance": 140,
            "launch_speed": [900, 1250],
            "launch_drag": 0.992,
            "launch_restitution": 0.82,
            "launch_max_seconds": 8,
            "launch_stop_speed": 78,
            "fatigue_minutes": [0, 45, 90, 135, 180, 225, 270],
            "green_message_minutes": 315,
            "auto_fatigue": True,
            "mac_safe_margins": [8, 28, 8, 80],
        }
        try:
            user_config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            defaults.update(user_config)
        except (OSError, ValueError, TypeError):
            pass
        return defaults

    def configure_transparent_window(self, window: tk.Misc) -> None:
        """Apply the native transparent-window mode on Windows or macOS."""
        window.overrideredirect(True)
        window.attributes("-topmost", True)
        window.configure(bg=self.transparent_bg)
        if self.windowing_system == "aqua":
            window.wm_attributes("-transparent", True)
        elif self.windowing_system == "win32":
            window.wm_attributes("-transparentcolor", TRANSPARENT_KEY)

    def load_pet_image(self, path: Path) -> Image.Image:
        image = Image.open(path).convert("RGBA")
        bbox = image.getchannel("A").getbbox()
        if bbox:
            image = image.crop(bbox)
        # Size Tall-nuts by eye scale: pirate eyes align with the normal
        # Wall-nut at 144 px, while critical reaches the same visual eye size
        # at 132 px. Every state keeps its native aspect ratio.
        state_sizes = {
            "tallnut-ninja.png": 138,
            "tallnut-critical.png": 138,
            "wallnut-crazy.png": 112,
        }
        target_size = state_sizes.get(path.name, self.pet_size)
        image.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        return self.harden_alpha(image)

    def load_green_message_image(self, path: Path) -> Image.Image:
        image = Image.open(path).convert("RGBA")
        bbox = image.getchannel("A").getbbox()
        if bbox:
            image = image.crop(bbox)
        # Both source compositions have the same master width but different
        # aspect ratios. A low height cap made the taller variant only 192 px
        # wide, so it looked noticeably smaller. Keep both at the larger
        # variant's 230 px width and preserve their native proportions.
        image.thumbnail((230, 260), Image.Resampling.LANCZOS)
        return self.harden_alpha(image)

    @staticmethod
    def harden_alpha(image: Image.Image) -> Image.Image:
        """Prevent Tk color-key halos after every resize or rotation."""
        image = image.copy()
        clean_alpha = image.getchannel("A").point(lambda value: 255 if value >= 72 else 0)
        image.putalpha(clean_alpha)
        return image

    def position_near_bottom_right(self) -> None:
        self.root.update_idletasks()
        left, top, right, bottom = self.desktop_work_area()
        x = max(left, right - self.window_size - 48)
        y = max(top, bottom - self.window_size - 24)
        self.root.geometry(f"{self.window_size}x{self.window_size}+{x}+{y}")

    def build_menu(self) -> tk.Menu:
        menu = tk.Menu(self.root, tearoff=False)
        for index, label in enumerate(STATE_LABELS):
            menu.add_command(
                label=f"切换到：{label}",
                command=lambda state=index: self.set_state(state, manual=True),
            )
        menu.add_separator()
        menu.add_command(label="恢复精神", command=self.reset_fatigue)
        menu.add_command(label="暂停随机晃动", command=self.toggle_wobble)
        self.wobble_menu_index = menu.index("end")
        menu.add_separator()
        menu.add_command(label="退出桌宠", command=self.root.destroy)
        return menu

    def bind_events(self) -> None:
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Double-Button-3>", self.on_right_double_click)
        if self.windowing_system == "aqua":
            # A Mac mouse/trackpad may report the secondary click as button 2,
            # or as Control-click, depending on the device and user settings.
            self.canvas.bind("<Button-2>", self.on_right_click)
            self.canvas.bind("<Double-Button-2>", self.on_right_double_click)
            self.canvas.bind("<Control-Button-1>", self.on_right_click)
            self.canvas.bind(
                "<Control-Double-Button-1>",
                self.on_right_double_click,
            )

    def on_right_click(self, event: tk.Event) -> None:
        if self.right_click_job is not None:
            self.root.after_cancel(self.right_click_job)
        self.right_click_job = self.root.after(
            260,
            self.show_menu_at,
            event.x_root,
            event.y_root,
        )

    def show_menu_at(self, x_root: int, y_root: int) -> None:
        self.right_click_job = None
        try:
            self.menu.tk_popup(x_root, y_root)
        finally:
            self.menu.grab_release()

    def on_right_double_click(self, _event: tk.Event) -> str:
        if self.right_click_job is not None:
            self.root.after_cancel(self.right_click_job)
            self.right_click_job = None
        self.launch_when_ready()
        return "break"

    def launch_when_ready(self) -> None:
        if self.animating:
            self.root.after(80, self.launch_when_ready)
            return
        self.play_launch()

    def on_press(self, event: tk.Event) -> None:
        if self.animating:
            self.dragged = True
            return
        if self.pending_click is not None:
            self.root.after_cancel(self.pending_click)
            self.pending_click = None
        self.press_screen = (event.x_root, event.y_root)
        self.press_window = (
            self.root.winfo_x() + self.canvas_offset_x,
            self.root.winfo_y() + self.canvas_offset_y,
        )
        self.dragged = False

    def on_drag(self, event: tk.Event) -> None:
        dx = event.x_root - self.press_screen[0]
        dy = event.y_root - self.press_screen[1]
        drag_threshold = float(self.config.get("drag_threshold_pixels", 18))
        if math.hypot(dx, dy) > drag_threshold:
            self.dragged = True
        if self.dragged and not self.animating:
            x = self.press_window[0] + dx
            y = self.press_window[1] + dy
            self.move_window_clamped(x, y)

    def on_release(self, _event: tk.Event) -> None:
        if not self.dragged and not self.animating:
            self.pending_click = self.root.after(230, self.play_bounce)
        self.dragged = False

    def on_double_click(self, _event: tk.Event) -> None:
        if self.pending_click is not None:
            self.root.after_cancel(self.pending_click)
            self.pending_click = None
        if not self.dragged and not self.animating:
            self.play_roll()

    def move_window_clamped(self, x: float, y: float, angle: float = 0.0) -> None:
        """Clamp the visible sprite, not its larger transparent window."""
        min_x, max_x, min_y, max_y = self.launch_bounds(angle)
        x = min(max(x, min_x), max_x)
        y = min(max(y, min_y), max_y)
        self.move_window_for_launch(x, y)

    def pose_half_extents(self, angle: float) -> tuple[float, float]:
        """Approximate the visible rotated sprite bounds inside the window."""
        image = self.base_images[self.current_state]
        radians = math.radians(angle)
        cosine = abs(math.cos(radians))
        sine = abs(math.sin(radians))
        half_width = (image.width * cosine + image.height * sine) / 2
        half_height = (image.width * sine + image.height * cosine) / 2
        return half_width, half_height

    def desktop_work_area(self) -> tuple[int, int, int, int]:
        """Return the usable desktop area for the current window system."""
        if self.windowing_system == "win32":
            rect = wintypes.RECT()
            try:
                success = ctypes.windll.user32.SystemParametersInfoW(
                    0x0030,  # SPI_GETWORKAREA
                    0,
                    ctypes.byref(rect),
                    0,
                )
                if success:
                    return rect.left, rect.top, rect.right, rect.bottom
            except (AttributeError, OSError):
                pass

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        if self.windowing_system == "aqua":
            # Tk does not expose the macOS Dock/menu-bar work area directly.
            # Keep conservative, user-adjustable margins until the first
            # signed Mac release can use native AppKit screen information.
            margins = self.config.get("mac_safe_margins", [8, 28, 8, 80])
            try:
                left, top, right, bottom = (max(0, int(x)) for x in margins)
                return left, top, screen_w - right, screen_h - bottom
            except (TypeError, ValueError):
                pass
        return 0, 0, screen_w, screen_h

    def launch_bounds(self, angle: float) -> tuple[float, float, float, float]:
        half_width, half_height = self.pose_half_extents(angle)
        center = self.window_size / 2
        left, top, right, bottom = self.desktop_work_area()
        return (
            left + half_width - center,
            right - half_width - center,
            top + half_height - center,
            bottom - half_height - center,
        )

    def move_window_for_launch(self, x: float, y: float) -> None:
        """Offset the sprite inside its window so its artwork can touch a wall."""
        max_window_x = max(0, self.root.winfo_screenwidth() - self.window_size)
        max_window_y = max(0, self.root.winfo_screenheight() - self.window_size)
        window_x = min(max(0, round(x)), max_window_x)
        window_y = min(max(0, round(y)), max_window_y)
        self.canvas_offset_x = x - window_x
        self.canvas_offset_y = y - window_y
        self.root.geometry(f"+{window_x}+{window_y}")
        # Dragging does not render a fresh animation frame, so apply the
        # within-window offset immediately. Otherwise the artwork stays
        # centered until the next wobble/pose refresh and appears unable to
        # reach the wall for several seconds.
        self.canvas.coords(
            self.image_item,
            self.window_size // 2 + self.canvas_offset_x,
            self.window_size // 2 + self.canvas_offset_y,
        )
        self.pet_physical_x = x
        self.pet_physical_y = y
        self.update_bubble_position()
        self.update_green_message_position()

    def set_state(self, state: int, manual: bool = False) -> None:
        physical_x = self.root.winfo_x() + self.canvas_offset_x
        physical_y = self.root.winfo_y() + self.canvas_offset_y
        self.current_state = min(max(0, state), len(self.base_images) - 1)
        if manual:
            # A manual choice starts a fresh 45-minute interval for that
            # state. In particular, choosing normal must not resume an old
            # elapsed session and jump straight to a late state.
            thresholds = self.config["fatigue_minutes"]
            threshold = float(thresholds[self.current_state])
            self.session_started = time.monotonic() - threshold * 60
            self.active_elapsed_seconds = threshold * 60
            self.last_fatigue_check = time.monotonic()
            self.session_date = date.today()
            self.manual_state_until = 0.0
            self.green_message_shown = False
            self.dismiss_green_message()
        self.move_window_clamped(physical_x, physical_y)
        self.show_pose()
        self.root.after(100, self.preload_current_roll_frames)
        self.show_state_bubble()

    def format_work_duration(self) -> str:
        minutes = max(0, int(round(self.active_elapsed_seconds / 60)))
        hours, remaining = divmod(minutes, 60)
        if hours and remaining:
            return f"{hours}小时{remaining}分钟"
        if hours:
            return f"{hours}小时"
        return f"{minutes}分钟"

    def choose_bubble_text(self) -> str:
        messages = [
            "可以站起来\n走动一下。",
            "记得喝水。",
            "再不休息，僵尸会吃掉你的脑子。",
            "再干也不会加工资。",
            "你好像掉头发了。",
            "是不是有点想家了。",
            "看看窗外，我为你准备了风景。",
            "慢就是快。",
            "要不要去洗把脸。",
            "你需要吃个小零食。",
            "你的脸色不太好。",
            "我在桌上发现几根你的头发。",
            "僵尸都下班了。",
            "记得给脑子浇水。",
            "听说出去透气的人都捡到了钱。",
            "Watch out！\n其实也没什么...",
            "你不必像坚果\n那样坚硬。",
            "人类不需要像\n坚果那样逞强...",
            "世上没有不可能。\n除了坚果过敏...",
            "你的表情吓到我了。",
            "都会结束的。",
            "你辛苦了。",
            "我会给你一些脑子。",
        ]
        if self.active_elapsed_seconds >= 60:
            duration = self.format_work_duration()
            # For mixed hour/minute durations, keep the hour on the first line
            # and the complete minute value on the second line.
            if "小时" in duration and "分钟" in duration:
                duration = duration.replace("小时", "小时\n", 1)
            messages.append(f"你已经工作{duration}了。")
        return random.choice(messages)

    @staticmethod
    def bubble_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        font_dir = Path("C:/Windows/Fonts")
        candidates = [
            Path("/System/Library/Fonts/PingFang.ttc"),
            Path("/System/Library/Fonts/STHeiti Light.ttc"),
            Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
            font_dir / "SIMYOU.TTF",
            font_dir / "msyhbd.ttc",
            font_dir / "msyh.ttc",
            font_dir / "simhei.ttf",
        ]
        for path in candidates:
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue
        return ImageFont.load_default()

    @staticmethod
    def wrap_bubble_text(
        text: str,
        draw: ImageDraw.ImageDraw,
        font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
        max_width: int,
        stroke_width: int = 0,
    ) -> list[str]:
        lines: list[str] = []
        # Explicit newlines are semantic breaks. Numeric durations are treated
        # as indivisible tokens so values such as "45分钟" never split between
        # the number and its unit.
        for paragraph in text.split("\n"):
            current = ""
            tokens = re.findall(r"\d+(?:小时|分钟)|.", paragraph)
            for token in tokens:
                candidate = current + token
                bbox = draw.textbbox(
                    (0, 0),
                    candidate,
                    font=font,
                    stroke_width=stroke_width,
                )
                if current and bbox[2] - bbox[0] > max_width:
                    lines.append(current)
                    current = token
                else:
                    current = candidate
            if current:
                lines.append(current)
        return lines[:3]

    def render_bubble_image(self, text: str, tail_up: bool) -> Image.Image:
        # Draw one continuous high-resolution silhouette, then derive its
        # outline from that silhouette. This prevents a visible seam where the
        # rounded body meets the pointer and gives the pointer a softly curved
        # tip instead of a rigid triangular joint.
        scale = 4
        width, height = self.bubble_size
        width *= scale
        height *= scale
        tail_height = 24 * scale
        margin = 5 * scale
        border = 3 * scale
        radius = 22 * scale
        # Compact F pointer: narrow at the root, short, and almost vertical.
        # Its two sides remain gently curved so it does not look assembled
        # from a rigid triangle.
        tail_base_x = int(width * 0.33)
        tail_tip_x = tail_base_x + 2 * scale
        dark_brown = (58, 29, 12, 255)
        warm_white = (255, 251, 239, 255)
        silhouette = Image.new("L", (width, height), 0)
        shape_draw = ImageDraw.Draw(silhouette)

        if tail_up:
            body_top = tail_height
            body_bottom = height - margin
            tip_y = margin + 2 * scale
            body_edge = body_top
            direction_y = -1
        else:
            body_top = margin
            body_bottom = height - tail_height
            tip_y = height - margin - 2 * scale
            body_edge = body_bottom
            direction_y = 1

        def cubic_curve(
            p0: tuple[float, float],
            p1: tuple[float, float],
            p2: tuple[float, float],
            p3: tuple[float, float],
            steps: int = 20,
        ) -> list[tuple[float, float]]:
            points: list[tuple[float, float]] = []
            for index in range(steps + 1):
                t = index / steps
                inverse = 1.0 - t
                x = (
                    inverse**3 * p0[0]
                    + 3 * inverse**2 * t * p1[0]
                    + 3 * inverse * t**2 * p2[0]
                    + t**3 * p3[0]
                )
                y = (
                    inverse**3 * p0[1]
                    + 3 * inverse**2 * t * p1[1]
                    + 3 * inverse * t**2 * p2[1]
                    + t**3 * p3[1]
                )
                points.append((x, y))
            return points

        left_root = (
            tail_base_x - 5 * scale,
            body_edge - direction_y * 2 * scale,
        )
        right_root = (
            tail_base_x + 7 * scale,
            body_edge - direction_y * 2 * scale,
        )
        tip = (tail_tip_x, tip_y)
        left_curve = cubic_curve(
            left_root,
            (tail_base_x - 3 * scale, body_edge + direction_y * 5 * scale),
            (tail_tip_x - 3 * scale, tip_y - direction_y * 4 * scale),
            tip,
        )
        right_curve = cubic_curve(
            tip,
            (tail_tip_x + 1 * scale, tip_y - direction_y * 4 * scale),
            (tail_base_x + 5 * scale, body_edge + direction_y * 5 * scale),
            right_root,
        )
        tail = left_curve + right_curve[1:]

        shape_draw.rounded_rectangle(
            (margin, body_top, width - margin, body_bottom),
            radius=radius,
            fill=255,
        )
        shape_draw.polygon(tail, fill=255)
        tip_radius = 1.25 * scale
        shape_draw.ellipse(
            (
                tail_tip_x - tip_radius,
                tip_y - tip_radius,
                tail_tip_x + tip_radius,
                tip_y + tip_radius,
            ),
            fill=255,
        )
        silhouette = silhouette.filter(
            ImageFilter.GaussianBlur(radius=1.15 * scale)
        ).point(lambda value: 255 if value >= 128 else 0)
        # A square max-filter flattens the last row of pixels at a narrow tip.
        # A radial blur threshold grows the outline evenly in every direction,
        # leaving a complete dark curve around the pointed end.
        outline = silhouette.filter(
            ImageFilter.GaussianBlur(radius=border * 0.58)
        ).point(lambda value: 255 if value >= 18 else 0)

        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        image.paste(dark_brown, (0, 0, width, height), outline)
        image.paste(warm_white, (0, 0, width, height), silhouette)
        draw = ImageDraw.Draw(image)

        stroke_width = max(1, round(0.7 * scale))
        max_text_width = width - 24 * scale
        spacing = 2 * scale
        if "\n" in text:
            # A manual line break is intentional layout, not a long one-line
            # sentence. Allow all requested lines before judging font size.
            target_lines = min(3, text.count("\n") + 1)
        else:
            target_lines = 1 if len(text) <= 12 else 2
        compact_text = text.replace("\n", "")
        # This manually balanced two-line sentence has enough room for the
        # same visual size as the shorter reminders. Do not let its total
        # character count unnecessarily push it into a smaller font.
        is_soft_reminder = compact_text == "你不必像坚果那样坚硬。"
        if is_soft_reminder:
            # The first line has seven glyphs. Give it the full safe interior
            # width so it can use the normal reminder font size.
            max_text_width = width - 14 * scale
        maximum_font_size = 20 if is_soft_reminder else 18
        font = self.bubble_font(13 * scale)
        lines = [text]
        for font_size in range(maximum_font_size, 10, -1):
            candidate_font = self.bubble_font(font_size * scale)
            candidate_lines = self.wrap_bubble_text(
                text,
                draw,
                candidate_font,
                max_text_width,
                stroke_width=stroke_width,
            )
            candidate_boxes = [
                draw.textbbox(
                    (0, 0),
                    line,
                    font=candidate_font,
                    stroke_width=stroke_width,
                )
                for line in candidate_lines
            ]
            candidate_height = sum(box[3] - box[1] for box in candidate_boxes)
            candidate_height += spacing * max(0, len(candidate_lines) - 1)
            available_height = body_bottom - body_top - border * 2
            if len(candidate_lines) <= target_lines and candidate_height <= available_height:
                font = candidate_font
                lines = candidate_lines
                break
        boxes = [
            draw.textbbox(
                (0, 0),
                line,
                font=font,
                stroke_width=stroke_width,
            )
            for line in lines
        ]
        line_heights = [box[3] - box[1] for box in boxes]
        total_height = sum(line_heights) + spacing * max(0, len(lines) - 1)
        text_area_top = body_top + border
        text_area_bottom = body_bottom - border
        y = text_area_top + (text_area_bottom - text_area_top - total_height) / 2
        for line, box, line_height in zip(lines, boxes, line_heights):
            line_width = box[2] - box[0]
            draw.text(
                ((width - line_width) / 2, y - box[1]),
                line,
                font=font,
                fill=dark_brown,
                stroke_width=stroke_width,
                stroke_fill=dark_brown,
            )
            y += line_height + spacing

        rendered = image.resize(self.bubble_size, Image.Resampling.LANCZOS)
        return self.harden_alpha(rendered)

    def show_state_bubble(self) -> None:
        self.dismiss_bubble()
        self.bubble_text = self.choose_bubble_text()
        self.bubble_window = tk.Toplevel(self.root)
        self.configure_transparent_window(self.bubble_window)
        width, height = self.bubble_size
        self.bubble_canvas = tk.Canvas(
            self.bubble_window,
            width=width,
            height=height,
            bg=self.transparent_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.bubble_canvas.pack()
        self.bubble_item = self.bubble_canvas.create_image(0, 0, anchor="nw")
        self.bubble_canvas.bind("<Button-1>", self.dismiss_bubble)
        self.update_bubble_position(force_render=True)

    def update_bubble_position(self, force_render: bool = False) -> None:
        if self.bubble_window is None or not self.bubble_window.winfo_exists():
            return
        width, height = self.bubble_size
        pet_x = getattr(
            self,
            "pet_physical_x",
            self.root.winfo_x() + self.canvas_offset_x,
        )
        pet_y = getattr(
            self,
            "pet_physical_y",
            self.root.winfo_y() + self.canvas_offset_y,
        )
        half_width, half_height = self.pose_half_extents(0.0)
        center = self.window_size / 2
        pet_center_x = pet_x + center
        pet_top = pet_y + center - half_height
        pet_bottom = pet_y + center + half_height
        left, top, right, bottom = self.desktop_work_area()
        tail_up = pet_top - height < top
        x = pet_center_x - width / 2
        x = min(max(x, left), max(left, right - width))
        if tail_up:
            y = min(pet_bottom - 3, bottom - height)
        else:
            y = max(top, pet_top - height + 3)
        if force_render or tail_up != self.bubble_tail_up:
            self.bubble_tail_up = tail_up
            self.bubble_photo = ImageTk.PhotoImage(
                self.render_bubble_image(self.bubble_text, tail_up)
            )
            if self.bubble_canvas is not None and self.bubble_item is not None:
                self.bubble_canvas.itemconfigure(
                    self.bubble_item,
                    image=self.bubble_photo,
                )
        self.bubble_window.geometry(f"{width}x{height}+{round(x)}+{round(y)}")

    def dismiss_bubble(self, _event: tk.Event | None = None) -> str:
        if self.bubble_window is not None:
            try:
                self.bubble_window.destroy()
            except tk.TclError:
                pass
        self.bubble_window = None
        self.bubble_canvas = None
        self.bubble_item = None
        self.bubble_photo = None
        return "break"

    def show_green_message(self) -> None:
        self.dismiss_bubble()
        self.dismiss_green_message()
        image = random.choice(self.green_message_images)
        width, height = image.size
        self.green_message_size = (width, height)
        self.green_message_window = tk.Toplevel(self.root)
        self.configure_transparent_window(self.green_message_window)
        self.green_message_canvas = tk.Canvas(
            self.green_message_window,
            width=width,
            height=height,
            bg=self.transparent_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.green_message_canvas.pack()
        self.green_message_photo = ImageTk.PhotoImage(image)
        self.green_message_canvas.create_image(
            width // 2,
            height // 2,
            image=self.green_message_photo,
            anchor="center",
        )
        self.green_message_canvas.bind("<Button-1>", self.complete_green_message)
        self.update_green_message_position()

    def update_green_message_position(self) -> None:
        if (
            self.green_message_window is None
            or not self.green_message_window.winfo_exists()
        ):
            return
        width, height = self.green_message_size
        pet_x = getattr(
            self,
            "pet_physical_x",
            self.root.winfo_x() + self.canvas_offset_x,
        )
        pet_y = getattr(
            self,
            "pet_physical_y",
            self.root.winfo_y() + self.canvas_offset_y,
        )
        center = self.window_size / 2
        pet_center_x = pet_x + center
        pet_center_y = pet_y + center
        # The end-of-cycle message is a face-covering overlay, not a speech
        # bubble. Keep its center exactly aligned with the pet even at a wall.
        x = round(pet_center_x - width / 2)
        y = round(pet_center_y - height / 2)
        x_geometry = f"+{x}" if x >= 0 else str(x)
        y_geometry = f"+{y}" if y >= 0 else str(y)
        self.green_message_window.geometry(
            f"{width}x{height}{x_geometry}{y_geometry}"
        )

    def complete_green_message(self, _event: tk.Event | None = None) -> str:
        """Dismiss the end card and begin a fresh normal work cycle."""
        self.dismiss_green_message()
        self.reset_fatigue()
        return "break"

    def dismiss_green_message(self, _event: tk.Event | None = None) -> str:
        if self.green_message_window is not None:
            try:
                self.green_message_window.destroy()
            except tk.TclError:
                pass
        self.green_message_window = None
        self.green_message_canvas = None
        self.green_message_photo = None
        self.green_message_size = (0, 0)
        return "break"

    def reset_fatigue(self) -> None:
        self.session_started = time.monotonic()
        self.session_date = date.today()
        self.active_elapsed_seconds = 0.0
        self.last_fatigue_check = self.session_started
        self.manual_state_until = 0.0
        self.green_message_shown = False
        self.dismiss_green_message()
        self.set_state(0)

    def toggle_wobble(self) -> None:
        self.wobble_enabled = not self.wobble_enabled
        label = "暂停随机晃动" if self.wobble_enabled else "继续随机晃动"
        self.menu.entryconfigure(self.wobble_menu_index, label=label)

    def update_fatigue(self) -> None:
        if self.config.get("auto_fatigue", True):
            now = time.monotonic()
            today = date.today()
            if today != self.session_date:
                # Every calendar day starts a new work cycle at normal.
                self.session_date = today
                self.session_started = now
                self.active_elapsed_seconds = 0.0
                self.last_fatigue_check = now
                self.manual_state_until = 0.0
                self.green_message_shown = False
                self.dismiss_green_message()
                if self.current_state != 0:
                    self.set_state(0)
            else:
                # The callback normally runs every 30 seconds. Cap a delayed
                # callback so Windows sleep/hibernate or a prolonged system
                # stall cannot count as hours of active computer time.
                delta = max(0.0, now - self.last_fatigue_check)
                self.active_elapsed_seconds += min(delta, 90.0)
                self.last_fatigue_check = now
            if now >= self.manual_state_until:
                elapsed_minutes = self.active_elapsed_seconds / 60
                thresholds = self.config["fatigue_minutes"]
                target = 0
                for index, threshold in enumerate(thresholds):
                    if elapsed_minutes >= threshold:
                        target = index
                if target != self.current_state:
                    self.set_state(target)
                green_message_minutes = float(
                    self.config.get("green_message_minutes", 315)
                )
                if (
                    elapsed_minutes >= green_message_minutes
                    and not self.green_message_shown
                ):
                    self.green_message_shown = True
                    self.show_green_message()
        self.root.after(30_000, self.update_fatigue)

    def show_pose(
        self,
        angle: float = 0.0,
        scale_x: float = 1.0,
        scale_y: float = 1.0,
        offset_y: int = 0,
    ) -> None:
        posed = self.render_pose_image(angle, scale_x, scale_y)
        self.current_photo = ImageTk.PhotoImage(posed)
        self.canvas.itemconfigure(self.image_item, image=self.current_photo)
        self.canvas.coords(
            self.image_item,
            self.window_size // 2 + self.canvas_offset_x,
            self.window_size // 2 + self.canvas_offset_y + offset_y,
        )

    def render_pose_image(
        self,
        angle: float = 0.0,
        scale_x: float = 1.0,
        scale_y: float = 1.0,
    ) -> Image.Image:
        """Render one pose as a Pillow image for display or frame caching."""
        image = self.base_images[self.current_state]
        width = max(1, round(image.width * scale_x))
        height = max(1, round(image.height * scale_y))
        posed = image.resize((width, height), Image.Resampling.LANCZOS)
        if angle:
            posed = posed.rotate(
                angle,
                resample=Image.Resampling.BICUBIC,
                expand=True,
                fillcolor=(0, 0, 0, 0),
            )
        # Transformations create fresh semi-transparent pixels. Clean them on
        # every animation frame before Tk composites against the color key.
        return self.harden_alpha(posed)

    def build_roll_frames(self, direction: int) -> list[ImageTk.PhotoImage]:
        key = (self.current_state, direction)
        cached = self.roll_frame_cache.get(key)
        if cached is not None:
            return cached
        frames: list[ImageTk.PhotoImage] = []
        steps = 34
        for index in range(steps + 1):
            progress = index / steps
            eased = 0.5 - 0.5 * math.cos(math.pi * progress)
            angle = direction * -720 * eased
            frames.append(ImageTk.PhotoImage(self.render_pose_image(angle)))
        self.roll_frame_cache[key] = frames
        return frames

    def preload_current_roll_frames(self) -> None:
        """Prepare roll artwork while idle so playback does no image rotation."""
        if self.animating:
            self.root.after(500, self.preload_current_roll_frames)
            return
        self.build_roll_frames(1)
        self.build_roll_frames(-1)

    def animate_poses(self, poses: list[tuple], frame_ms: int, done=None) -> None:
        if self.animating:
            return
        self.animating = True

        def frame(index: int) -> None:
            if index >= len(poses):
                self.show_pose()
                self.animating = False
                if done:
                    done()
                return
            self.show_pose(*poses[index])
            self.root.after(frame_ms, frame, index + 1)

        frame(0)

    def play_bounce(self) -> None:
        self.pending_click = None
        poses = [
            (0, 1.00, 1.00, 0),
            (0, 1.06, 0.92, 8),
            (0, 0.96, 1.07, -7),
            (0, 1.02, 0.98, 2),
            (0, 1.00, 1.00, 0),
        ]
        self.animate_poses(poses, 55)

    def schedule_wobble(self) -> None:
        if self.wobble_job is not None:
            return
        low, high = self.config["wobble_interval_seconds"]
        delay = random.uniform(float(low), float(high))
        self.wobble_job = self.root.after(round(delay * 1000), self.try_wobble)

    def try_wobble(self) -> None:
        self.wobble_job = None
        if self.wobble_enabled and not self.animating and not self.dragged:
            poses = [
                (0.0, 1, 1, 0),
                (-0.8, 1, 1, -1),
                (1.2, 1, 1, -3),
                (-1.4, 1, 1, -2),
                (0.8, 1, 1, -1),
                (0.0, 1, 1, 0),
            ]
            self.animate_poses(poses, 70, self.schedule_wobble)
        else:
            self.schedule_wobble()

    def play_roll(self) -> None:
        if self.animating:
            return
        self.animating = True
        steps = 34
        start_x = self.root.winfo_x() + self.canvas_offset_x
        start_y = self.root.winfo_y() + self.canvas_offset_y
        left, top, right, bottom = self.desktop_work_area()
        distance = int(self.config["roll_distance"])
        direction = 1 if start_x + self.window_size / 2 < (left + right) / 2 else -1
        roll_frames = self.build_roll_frames(direction)

        center = self.window_size / 2
        half_width_0, half_height_0 = self.pose_half_extents(0.0)
        min_x_0 = left + half_width_0 - center
        max_x_0 = right - half_width_0 - center
        min_y_0 = top + half_height_0 - center
        max_y_0 = bottom - half_height_0 - center
        edge_tolerance = 3.0
        touches_left = start_x <= min_x_0 + edge_tolerance
        touches_right = start_x >= max_x_0 - edge_tolerance
        touches_top = start_y <= min_y_0 + edge_tolerance
        touches_bottom = start_y >= max_y_0 - edge_tolerance
        available = max_x_0 - start_x if direction > 0 else start_x - min_x_0
        distance = min(distance, max(0, available))

        def frame(index: int) -> None:
            if index > steps:
                self.show_pose()
                self.animating = False
                self.schedule_wobble()
                return
            progress = index / steps
            eased = 0.5 - 0.5 * math.cos(math.pi * progress)
            angle = direction * -720 * eased
            half_width, half_height = self.pose_half_extents(angle)
            min_x = left + half_width - center
            max_x = right - half_width - center
            min_y = top + half_height - center
            max_y = bottom - half_height - center

            x = start_x + direction * distance * eased
            if touches_left or touches_right:
                # At a vertical screen edge, keep the horizontal center on a
                # continuous path. Tracking the changing width of a non-round
                # rotated sprite makes its center oscillate twice per turn and
                # produces severe sideways judder.
                pass
            else:
                x = min(max(x, min_x), max_x)

            if touches_bottom or touches_top:
                # At a horizontal screen edge, lock the vertical center.
                # Following the outline of a non-round sprite necessarily
                # makes its center bob as it turns, which looks like judder.
                y = start_y
            else:
                hop = abs(math.sin(math.pi * progress)) * 9
                y = min(max(start_y - hop, min_y), max_y)
            self.move_window_for_launch(x, y)
            self.current_photo = roll_frames[index]
            self.canvas.itemconfigure(self.image_item, image=self.current_photo)
            self.canvas.coords(
                self.image_item,
                self.window_size // 2 + self.canvas_offset_x,
                self.window_size // 2 + self.canvas_offset_y,
            )
            self.root.after(18, frame, index + 1)

        frame(0)

    def play_launch(self) -> None:
        """Launch the pet as a damped top-down ball inside the screen."""
        if self.animating:
            return
        self.animating = True

        x = float(self.root.winfo_x()) + self.canvas_offset_x
        y = float(self.root.winfo_y()) + self.canvas_offset_y

        low_speed, high_speed = self.config["launch_speed"]
        speed = random.uniform(float(low_speed), float(high_speed))
        # Always start along a screen diagonal. A small random deviation keeps
        # launches lively without ever looking horizontal or vertical.
        direction = random.choice(
            [math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4]
        )
        direction += math.radians(random.uniform(-7, 7))

        vx = math.cos(direction) * speed
        vy = math.sin(direction) * speed
        spin_direction = 1 if vx >= 0 else -1
        rotation = 0.0
        restitution = float(self.config["launch_restitution"])
        drag_per_frame = float(self.config["launch_drag"])
        max_seconds = float(self.config["launch_max_seconds"])
        started = time.monotonic()
        previous = started

        def frame() -> None:
            nonlocal x, y, vx, vy, rotation, previous, spin_direction
            now = time.monotonic()
            dt = min(0.04, max(0.001, now - previous))
            previous = now

            x += vx * dt
            y += vy * dt
            collided = False

            min_x, max_x, min_y, max_y = self.launch_bounds(rotation)

            if x <= min_x:
                x = min_x
                vx = abs(vx) * restitution
                collided = True
            elif x >= max_x:
                x = max_x
                vx = -abs(vx) * restitution
                collided = True

            if y <= min_y:
                y = min_y
                vy = abs(vy) * restitution
                collided = True
            elif y >= max_y:
                y = max_y
                vy = -abs(vy) * restitution
                collided = True

            if collided:
                # Small energy variation keeps repeated paths from feeling mechanical.
                vx *= random.uniform(0.97, 1.01)
                vy *= random.uniform(0.97, 1.01)
                spin_direction = 1 if vx >= 0 else -1

            drag = drag_per_frame ** (dt * 60)
            vx *= drag
            vy *= drag

            remaining_speed = math.hypot(vx, vy)
            travel = remaining_speed * dt
            radius = max(1.0, self.pet_size * 0.46)
            # Angular speed follows translational speed, so the spin decelerates
            # continuously instead of freezing at a tilted angle near the end.
            rotation += spin_direction * math.degrees(travel / radius)

            self.move_window_for_launch(x, y)
            self.show_pose(angle=rotation)

            elapsed = now - started
            stop_speed = float(self.config.get("launch_stop_speed", 78))
            if (elapsed >= 1.8 and remaining_speed < stop_speed) or elapsed >= max_seconds:
                min_x, max_x, min_y, max_y = self.launch_bounds(0.0)
                x = min(max(x, min_x), max_x)
                y = min(max(y, min_y), max_y)
                self.move_window_for_launch(x, y)
                self.show_pose()
                self.animating = False
                self.schedule_wobble()
                return

            self.root.after(16, frame)

        frame()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    pet = WallnutPet()
    if "--launch-smoke-test" in sys.argv:
        pet.set_state(4)
        pet.root.after(200, pet.play_launch)
        pet.root.after(8_500, pet.root.destroy)
    elif "--right-double-smoke-test" in sys.argv:
        pet.set_state(4)

        class FakePointerEvent:
            x_root = pet.root.winfo_x() + pet.window_size // 2
            y_root = pet.root.winfo_y() + pet.window_size // 2

        event = FakePointerEvent()
        pet.root.after(200, pet.on_right_click, event)
        pet.root.after(320, pet.on_right_double_click, event)
        pet.root.after(8_500, pet.root.destroy)
    elif "--animation-smoke-test" in sys.argv:
        pet.root.after(200, pet.play_roll)
        pet.root.after(1_800, pet.root.destroy)
    elif "--bubble-smoke-test" in sys.argv:
        pet.root.after(200, pet.set_state, 1)
        pet.root.after(2_500, pet.root.destroy)
    elif "--smoke-test" in sys.argv:
        pet.root.after(1_500, pet.root.destroy)
    pet.run()
