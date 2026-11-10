#!/usr/bin/env python3
"""Идеальный цикл: кадр считается как функция фазы t от 0 до 1, поэтому конец совпадает с началом по построению."""
import math
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from vg import Plate

PAGE = """<!doctype html>
<html lang="ru"><head><meta charset="UTF-8"><style>
html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:{ground}}}
#root{{position:relative;width:{w}px;height:{h}px}}
#stage svg{{display:block;width:{w}px;height:{h}px}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{seconds}" data-width="{w}" data-height="{h}">
<div id="stage"></div></div>
<script src="assets/frames.js"></script>
<script>
const stage = document.getElementById("stage");
function renderAt(t) {{ stage.innerHTML = FRAMES[Math.min(FRAMES.length - 1, Math.round(t * {fps}))]; }}
window.addEventListener("hf-seek", e => renderAt(e.detail.time));
renderAt(0);
</script></body></html>
"""


def clamp(x, low=0.0, high=1.0):
    return max(low, min(high, x))


def ease(x):
    """Плавный разгон и остановка."""
    x = clamp(x)
    return x * x * x * (x * (6 * x - 15) + 10)


def snap(x):
    """Толчок: быстрый ход с лёгким перелётом и возвратом."""
    x = clamp(x)
    return 1 - (1 - x) ** 3 * math.cos(x * math.pi * 1.5)


def span(t, a, b, curve=ease):
    """Ход от 0 до 1, пока фаза идёт от a до b."""
    return curve((t - a) / (b - a))


def lerp(a, b, k):
    return a + (b - a) * k


def turn(t, offset=0):
    """Фаза со сдвигом: для элементов конвейера, у каждого свой offset."""
    return (t + offset) % 1


def curve(start, end, bend, k):
    """Точка на дуге p.arrow(start, end, bend) при доле пути k."""
    (x1, y1), (x2, y2) = start, end
    dx, dy = x2 - x1, y2 - y1
    cx, cy = (x1 + x2) / 2 - dy * bend, (y1 + y2) / 2 + dx * bend
    a, b, c = (1 - k) ** 2, 2 * k * (1 - k), k * k
    return a * x1 + b * cx + c * x2, a * y1 + b * cy + c * y2


class Loop:
    """Ролик: make() даёт чистый лист, draw(p, t) рисует кадр."""

    def __init__(self, name, make, draw, seconds=6, fps=30, alt=""):
        self.name, self.make, self.draw, self.seconds, self.fps, self.alt = name, make, draw, seconds, fps, alt

    def frame(self, t):
        p = self.make()
        self.draw(p, t)
        return p.markup(self.alt)

    def frames(self):
        if self.frame(0) != self.frame(1):
            raise ValueError(f"{self.name}: кадр t=1 расходится с t=0, цикл не замкнут")
        count = round(self.seconds * self.fps)
        return [self.frame(i / count) for i in range(count)]

    def sheet(self, folder, phases, blind=False):
        """SVG отдельных фаз: смотреть глазами до рендера. blind убирает подписи для слепого чтения."""
        folder = pathlib.Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        paths = []
        for t in phases:
            svg = self.frame(t)
            svg = re.sub(r"<text.*?</text>", "", svg) if blind else svg
            path = folder / f"{self.name}-{round(t * 1000):04d}.svg"
            path.write_text(svg, encoding="utf-8")
            paths.append(path)
        return paths

    def project(self, folder, scale=2):
        """Проект HyperFrames: кадры лежат массивом, страница показывает нужный по событию hf-seek."""
        folder = pathlib.Path(folder)
        (folder / "assets").mkdir(parents=True, exist_ok=True)
        frames, probe = self.frames(), self.make()
        strings = ",".join("`" + svg.replace("\\", "\\\\").replace("`", "\\`") + "`" for svg in frames)
        (folder / "assets" / "frames.js").write_text(f"const FRAMES=[{strings}];\n", encoding="utf-8")
        (folder / "index.html").write_text(
            PAGE.format(w=probe.w * scale, h=probe.h * scale, ground=probe.fill, seconds=self.seconds, fps=self.fps),
            encoding="utf-8",
        )
        return folder

    def render(self, folder, out, quality="delivery", scale=2):
        """Рендер в MP4 без звука. scale=2 даёт вдвое больше точек, чем у листа: текст на кадре остаётся чётким."""
        folder, out = self.project(folder, scale), pathlib.Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        raw = out.with_suffix(".raw.mp4")
        subprocess.run(
            ["npx", "hyperframes", "render", "--quality", quality, "--fps", str(self.fps), "--output", str(raw.resolve())],
            cwd=folder, check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-map", "0:v:0", "-c", "copy", "-an",
             "-movflags", "+faststart", str(out)],
            check=True,
        )
        raw.unlink()
        return out


def seam(video):
    """Сравнивает стык с обычным шагом кадра. Вернёт (стык, обычный шаг): стык не должен быть заметнее шага."""
    video = pathlib.Path(video)
    folder = video.parent / f".{video.stem}-seam"
    folder.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-fps_mode", "passthrough", str(folder / "%04d.png")], check=True)
    frames = sorted(folder.glob("*.png"))

    def distance(a, b):
        done = subprocess.run(["magick", "compare", "-metric", "RMSE", str(a), str(b), "null:"], capture_output=True, text=True)
        return float(re.search(r"\(([\d.e-]+)\)", done.stderr).group(1))

    join = distance(frames[-1], frames[0])
    steps = [distance(frames[i], frames[i + 1]) for i in range(0, len(frames) - 1, max(1, len(frames) // 40))]
    for path in frames:
        path.unlink()
    folder.rmdir()
    return join, max(steps)
