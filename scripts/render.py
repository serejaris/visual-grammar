#!/usr/bin/env python3
"""Проверяет читаемость листов. Рядом с SVG кладёт PNG, .proof.png (копии 375 px в цвете и в сером) и .blind.png (без подписей)."""
import argparse
import itertools
import json
import os
import pathlib
import re
import shutil
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from vg import contrast

MIN_CONTRAST = 3
MEASURE = """<script>
const under = b => {
  const fills = new Set();
  for (let i = 0; i < 16; i++) for (const k of [0.3, 0.7]) {
    const hit = document.elementsFromPoint(b.left + b.width * (i + 0.5) / 16, b.top + b.height * k)
      .find(el => el instanceof SVGGeometryElement && (el.getAttribute('fill') || 'none') !== 'none');
    if (hit && !hit.hasAttribute('fill-opacity')) fills.add(hit.getAttribute('fill'));
  }
  return [...fills];
};
const strokes = [...document.querySelectorAll('svg line, svg path, svg polygon, svg circle, svg ellipse, svg rect')]
  .filter(el => el.getAttribute('stroke') && !el.closest('defs') && (el.getAttribute('fill') || 'none') === 'none');
const crossed = b => strokes.some(el => {
  const m = el.getScreenCTM(), length = el.getTotalLength(), n = Math.min(800, Math.ceil(length / 3));
  for (let i = 0; i <= n; i++) {
    const q = el.getPointAtLength(length * i / n);
    const x = m.a * q.x + m.c * q.y + m.e, y = m.b * q.x + m.d * q.y + m.f;
    if (x > b.left && x < b.right && y > b.top + b.height * 0.2 && y < b.bottom - b.height * 0.2) return true;
  }
  return false;
});
const els = [...document.querySelectorAll('svg text')];
const data = els.map(e => {
  const b = e.getBoundingClientRect(), m = e.getScreenCTM();
  return {s: e.textContent, x: b.left, y: b.top, w: b.width, h: b.height,
          size: parseFloat(getComputedStyle(e).fontSize) * Math.hypot(m.a, m.b),
          inks: [e, ...e.querySelectorAll('tspan')].map(t => t.getAttribute('fill')).filter(Boolean),
          under: under(b), crossed: crossed(b)};
});
const pre = document.createElement('pre'); pre.id = 'vg'; pre.textContent = JSON.stringify(data);
document.body.append(pre);
</script>"""


def chrome():
    for path in (
        os.environ.get("CHROME"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
    ):
        if path and os.path.exists(path):
            return path
    sys.exit("Chrome не найден: укажи путь в переменной CHROME")


def browser(profile, *args):
    """Запуск Chrome. Он изредка виснет на старте профиля, поэтому короткий срок и две попытки."""
    command = [chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={profile}", *args]
    for attempt in (1, 2):
        try:
            return subprocess.run(command, capture_output=True, text=True, timeout=45)
        except subprocess.TimeoutExpired:
            if attempt == 2:
                sys.exit("Chrome не ответил за две попытки")


def is_hex(color):
    return bool(re.fullmatch(r"#[0-9a-fA-F]{3}|#[0-9a-fA-F]{6}", color))


def text_defects(items, w, h, u):
    found, edge, smallest = [], 3 * u, 1.3 * u
    for t in items:
        label = t["s"][:40]
        if t["size"] < smallest - 0.01:
            found.append(f"мелкий текст {t['size']:.1f} px, нужно от {smallest:.1f}: {label}")
        if t["x"] < edge or t["y"] < edge or t["x"] + t["w"] > w - edge or t["y"] + t["h"] > h - edge:
            found.append(f"текст ближе {edge:.0f} px к краю листа: {label}")
        if t["crossed"]:
            found.append(f"волосная линия идёт через подпись: {label}")
        pairs = [(a, b) for a in t["inks"] for b in t["under"] if is_hex(a) and is_hex(b)]
        worst = min((contrast(a, b) for a, b in pairs), default=MIN_CONTRAST)
        if worst < MIN_CONTRAST:
            found.append(f"подпись теряется на фоне: контраст {worst:.1f}, нужно от {MIN_CONTRAST}: {label}")
    for a, b in itertools.combinations(items, 2):
        inset_a, inset_b = a["h"] * 0.16, b["h"] * 0.16
        apart = (
            a["x"] + a["w"] <= b["x"]
            or b["x"] + b["w"] <= a["x"]
            or a["y"] + a["h"] - inset_a <= b["y"] + inset_b
            or b["y"] + b["h"] - inset_b <= a["y"] + inset_a
        )
        if not apart:
            found.append(f"подписи наехали: {a['s'][:30]} / {b['s'][:30]}")
    return found


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24])


def proof_sheet(png, w, h, tmp):
    """Две копии шириной 375 px, в цвете и в сером: так лист выглядит в ленте и без цвета."""
    source, height = png.resolve().as_uri(), round(375 * h / w)
    page = pathlib.Path(tmp, "proof.html")
    page.write_text(
        '<!doctype html><body style="margin:0;background:#777;display:flex;gap:16px">'
        f'<img style="width:375px" src="{source}"><img style="width:375px;filter:grayscale(1)" src="{source}"></body>',
        encoding="utf-8",
    )
    browser(
        f"{tmp}/p", f"--window-size=766,{height}", "--force-device-scale-factor=2", "--allow-file-access-from-files",
        f"--screenshot={png.with_suffix('.proof.png').resolve()}", page.as_uri(),
    )


def render(path, scale):
    svg = path.read_text(encoding="utf-8")
    w, h = (int(re.search(rf'{k}="(\d+)"', svg).group(1)) for k in ("width", "height"))
    u = float(re.search(r'data-u="([\d.]+)"', svg).group(1))
    out = path.with_suffix(".png")
    with tempfile.TemporaryDirectory(prefix="vg-") as tmp:
        page = pathlib.Path(tmp, "plate.html")
        frame = f'<!doctype html><html lang="ru"><body style="margin:0">{svg}</body></html>'
        page.write_text(frame.replace("</body>", MEASURE + "</body>"), encoding="utf-8")
        dump = browser(f"{tmp}/p", f"--window-size={w},{h}", "--dump-dom", page.as_uri())
        found = re.search(r'<pre id="vg">(.*?)</pre>', dump.stdout, re.S)
        if not found:
            sys.exit(f"Chrome не вернул замеры: {dump.stderr[-400:]}")
        items = json.loads(found.group(1).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">"))
        defects = text_defects(items, w, h, u)
        page.write_text(frame, encoding="utf-8")
        browser(
            f"{tmp}/p", f"--window-size={w},{h}", f"--force-device-scale-factor={scale}",
            f"--screenshot={out.resolve()}", page.as_uri(),
        )
        proof_sheet(out, w, h, tmp)
        page.write_text(frame.replace("</body>", "<style>svg text{display:none}</style></body>"), encoding="utf-8")
        browser(f"{tmp}/p", f"--window-size={w},{h}", f"--screenshot={path.with_suffix('.blind.png').resolve()}", page.as_uri())
    if png_size(out) != (w * scale, h * scale):
        defects.append(f"снимок {png_size(out)} вместо {w * scale}×{h * scale}")
    for line in defects:
        print(f"✗ {line}")
    print(f"{'✗' if defects else '✓'} {out} · дефектов: {len(defects)}")
    return len(defects)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=pathlib.Path, nargs="+")
    parser.add_argument("--scale", type=int, default=2)
    args = parser.parse_args()
    sys.exit(1 if sum(render(path, args.scale) for path in args.svg) else 0)


if __name__ == "__main__":
    main()
