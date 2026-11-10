#!/usr/bin/env python3
"""Лист по Visual Grammar: формы, структуры, отношения, подписи. Собирается через Plate, пишется save()."""
import contextlib
import hashlib
import html
import math
import pathlib
import random

MAIN, ACCENT, PAPER = "main", "accent", "paper"
FONT = "'Helvetica Neue', 'Inter Tight', Arial, sans-serif"
PALETTES = {  # фон, главная краска, акцент
    "mono": ("#ffffff", "#1b1b1b", "#8c8c8c"),
    "brand": ("#fafafa", "#1b2b4c", "#ff1493"),
    "sprague": ("#fcefdf", "#221e1f", "#ec2f28", "#f8cd28", "#1e95bb", "#fbaab3"),  # после акцента идут ещё краски
    "leborg": ("#ffffff", "#2b2a2a", "#fd4439"),
    "cobalt": ("#f5f2ea", "#14213d", "#2f6fed"),
    "moss": ("#f1efe4", "#26332b", "#5a8a3a"),
    "sand": ("#f4ead9", "#3b2a20", "#c2601a"),
    "night": ("#11151c", "#ece7db", "#f2b441"),
}
FORMATS = {
    "page": (1080, 1322),
    "spread": (2160, 1322),
    "square": (1080, 1080),
    "wide": (1600, 900),
    "hero": (1600, 840),
    "og": (1200, 630),
    "story": (1080, 1920),
}
DASHES = {"dash": (1.1, 0.8), "dot": (0.02, 0.62)}


def _rgb(color):
    c = color.lstrip("#")
    c = "".join(ch * 2 for ch in c) if len(c) == 3 else c
    return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))


def _luminance(color):
    channels = [v / 255 for v in _rgb(color)]
    r, g, b = (v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in channels)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    """Контраст двух цветов по WCAG."""
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def mix(a, b, k):
    """Цвет между a и b: k=0 это a, k=1 это b."""
    return "#" + "".join(f"{round(x + (y - x) * k):02x}" for x, y in zip(_rgb(a), _rgb(b)))


def _n(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def _pts(points):
    return " ".join(f"{_n(x)},{_n(y)}" for x, y in points)


def _rot(points, angle, pivot):
    a, (px, py) = math.radians(angle), pivot
    c, s = math.cos(a), math.sin(a)
    return [(px + (x - px) * c - (y - py) * s, py + (x - px) * s + (y - py) * c) for x, y in points]


def _smooth(points, closed=True):
    """Гладкая линия через точки: Катмулл-Ром в кубические кривые."""
    n, out = len(points), [f"M{_n(points[0][0])} {_n(points[0][1])}"]
    at = (lambda i: points[i % n]) if closed else (lambda i: points[min(max(i, 0), n - 1)])
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = (at(i + k) for k in (-1, 0, 1, 2))
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f"C{_n(c1[0])} {_n(c1[1])} {_n(c2[0])} {_n(c2[1])} {_n(p2[0])} {_n(p2[1])}")
    return "".join(out) + ("Z" if closed else "")


def circle(x, y, r):
    """Контур круга строкой пути: для subtract() и clip()."""
    return f"M{_n(x - r)} {_n(y)}a{_n(r)} {_n(r)} 0 1 0 {_n(2 * r)} 0a{_n(r)} {_n(r)} 0 1 0 {_n(-2 * r)} 0Z"


def sector(x, y, r, start, end):
    """Контур сектора: часть круга. Углы в градусах, 0 смотрит вправо, рост идёт по часовой."""
    a, b = math.radians(start), math.radians(end)
    x1, y1, x2, y2 = x + r * math.cos(a), y + r * math.sin(a), x + r * math.cos(b), y + r * math.sin(b)
    return f"M{_n(x)} {_n(y)}L{_n(x1)} {_n(y1)}A{_n(r)} {_n(r)} 0 {int(end - start > 180)} 1 {_n(x2)} {_n(y2)}Z"


def box(cx, cy, w, h):
    return f"M{_n(cx - w / 2)} {_n(cy - h / 2)}h{_n(w)}v{_n(h)}h{_n(-w)}Z"


class Plate:
    def __init__(self, fmt="page", seed="plate", ground=PAPER, palette="mono", tone="screen", font=FONT, loop=None, rtl=False):
        """palette: имя из PALETTES или (фон, главная, акцент). tone: screen даёт тинт растром, flat прозрачностью.

        loop называет сцену живого цикла: страница оживляет лист по этому имени.
        rtl пишет текст справа налево: строка стоит от x влево, раскладку зеркалит сам лист.
        """
        self.w, self.h = FORMATS.get(fmt, fmt)
        self.u = (self.w / 2 if fmt == "spread" else self.w) / 100
        self.margin = (7 if self.u > 11 else 12.5) * self.u
        self.hair = min(0.14 * self.u, 1.6)
        self.step = 0.62 * self.u
        self.optical = (self.w / 2, self.h * 0.46)
        self.rng = random.Random(seed)
        self.ns = "vg" + hashlib.md5(str(seed).encode()).hexdigest()[:6]
        colors = PALETTES.get(palette, palette)
        self.inks, self.spots = dict(zip((PAPER, MAIN, ACCENT), colors)), list(colors[2:])
        self.ground, self.tone, self.font, self.loop = ground, tone, font, loop
        self.fill = self.inks.get(ground, ground)
        self.dark = _luminance(self.fill) < 0.3
        self.rtl = rtl
        self.defs, self.body, self.screens = [], [], {}
        self.uid = 0

    # Краски

    def _c(self, ink):
        """Цвет по роли. Любой другой цвет проходит как есть. На заливке главной краской она меняется на бумагу."""
        if ink == MAIN and self.ground == MAIN:
            ink = PAPER
        return self.inks.get(ink, ink)

    def spot(self, i=0, plain=ACCENT):
        """Краска по очереди для многоцветной палитры. У палитры с одним акцентом вернёт plain."""
        colors = [c for c in self.spots if c != self.fill]
        return colors[i % len(colors)] if len(self.spots) > 1 else plain

    def on_ground(self):
        """Краска текста: та, что контрастнее к заливке."""
        return max((MAIN, PAPER), key=lambda ink: contrast(self.inks[ink], self.fill))

    def _accent(self):
        """Краска термина и линий: акцент, если он виден на заливке, иначе бумага или главная."""
        if self.ground == ACCENT:
            return PAPER
        return ACCENT if contrast(self.inks[ACCENT], self.fill) >= 3 else self.on_ground()

    def _paint(self, ink, tint):
        if ink is None:
            return "none"
        color = self._c(ink)
        if tint >= 100 or self.tone == "flat":
            return color
        key = (color, tint, self.step)
        if key not in self.screens:
            self.screens[key] = f"{self.ns}s{len(self.screens)}"
            t, s = tint / 100, max(round(self.step * 2**0.5 * 2) / 2, 1)
            spots = [(s / 2, s / 2), (0, 0), (s, 0), (0, s), (s, s)]
            if t <= 0.5:
                r = s * math.sqrt(t / (2 * math.pi))
                tile = f'<path fill="{color}" d="{"".join(circle(x, y, r) for x, y in spots)}"/>'
            else:
                r = s * math.sqrt((1 - t) / (2 * math.pi))
                holes = "".join(circle(x, y, r) for x, y in spots)
                tile = f'<path fill-rule="evenodd" fill="{color}" d="M0 0H{_n(s)}V{_n(s)}H0Z{holes}"/>'
            self.defs.append(
                f'<pattern id="{self.screens[key]}" width="{_n(s)}" height="{_n(s)}" '
                f'patternUnits="userSpaceOnUse">{tile}</pattern>'
            )
        return f"url(#{self.screens[key]})"

    def _style(self, ink, tint=100, line=None, dash=None, through=False, alpha=1):
        """Заливка и контур. ink=None даёт контур без заливки. through=True: форма просвечивает на наложении."""
        out = f' fill="{self._paint(ink, tint)}"'
        if alpha < 1:
            out += f' opacity="{alpha:.3f}"'
        if ink and tint < 100 and self.tone == "flat":
            out += f' fill-opacity="{tint / 100:.2f}"'
        if line:
            out += f' stroke="{self._c(line)}" stroke-width="{_n(self.hair)}"'
            if dash:
                out += f' stroke-dasharray="{self._dash(dash)}" stroke-linecap="round"'
        if through:
            out += f' style="mix-blend-mode:{"screen" if self.dark else "multiply"}"'
        return out

    def _dash(self, dash):
        a, b = DASHES[dash]
        return f"{_n(a * self.u)} {_n(b * self.u)}"

    # Формы

    def disc(self, x, y, r, ink=MAIN, tint=100, **kw):
        self.body.append(f'<circle cx="{_n(x)}" cy="{_n(y)}" r="{_n(r)}"{self._style(ink, tint, **kw)}/>')

    def ring(self, x, y, r, hole, ink=MAIN, tint=100, **kw):
        self.path(circle(x, y, r) + circle(x, y, hole), ink, tint, evenodd=True, **kw)

    def rect(self, cx, cy, w, h, ink=MAIN, tint=100, angle=0, rounded=0, **kw):
        turn = f' transform="rotate({_n(angle)} {_n(cx)} {_n(cy)})"' if angle else ""
        corner = f' rx="{_n(rounded)}"' if rounded else ""
        self.body.append(
            f'<rect x="{_n(cx - w / 2)}" y="{_n(cy - h / 2)}" width="{_n(w)}" height="{_n(h)}"'
            f'{corner}{turn}{self._style(ink, tint, **kw)}/>'
        )

    def ellipse(self, cx, cy, rx, ry, ink=MAIN, tint=100, angle=0, **kw):
        turn = f' transform="rotate({_n(angle)} {_n(cx)} {_n(cy)})"' if angle else ""
        self.body.append(
            f'<ellipse cx="{_n(cx)}" cy="{_n(cy)}" rx="{_n(rx)}" ry="{_n(ry)}"{turn}{self._style(ink, tint, **kw)}/>'
        )

    def poly(self, points, ink=MAIN, tint=100, **kw):
        self.body.append(f'<polygon points="{_pts(points)}"{self._style(ink, tint, **kw)}/>')

    def path(self, d, ink=MAIN, tint=100, evenodd=False, **kw):
        rule = ' fill-rule="evenodd"' if evenodd else ""
        self.body.append(f'<path d="{d}"{rule}{self._style(ink, tint, **kw)}/>')

    def subtract(self, keep, cut, ink=MAIN, tint=100, **kw):
        """Вычитание: форма keep без формы cut. Оба контура строками пути."""
        self.uid += 1
        self.defs.append(
            f'<clipPath id="{self.ns}c{self.uid}"><path clip-rule="evenodd" d="M0 0H{self.w}V{self.h}H0Z{cut}"/></clipPath>'
        )
        self.body.append(f'<path d="{keep}" clip-path="url(#{self.ns}c{self.uid})"{self._style(ink, tint, **kw)}/>')

    def blob(self, x, y, r, kind="organic", ink=MAIN, tint=100, seed=None, turn=0, **kw):
        """Контур не из геометрии: organic живой и плавный, random рваный, cloud лепестками.

        seed держит одну форму на всех кадрах ролика, turn поворачивает её.
        """
        rng, n = (self.rng if seed is None else random.Random(seed)), 180
        shift = rng.uniform(0, math.tau)
        waves = {
            "organic": [(2, 0.08), (3, 0.13), (4, 0.05)],
            "random": [(2, 0.06), (3, 0.09), (5, 0.05), (9, 0.035), (14, 0.022)],
        }.get(kind, [])
        phases = [rng.uniform(0, math.tau) for _ in waves]
        points = []
        for i in range(n):
            a = math.tau * i / n
            if kind == "cloud":
                k = 0.8 + 0.3 * abs(math.sin(2.5 * a + shift))
            else:
                k = 1 + sum(amp * math.sin(f * a + ph) for (f, amp), ph in zip(waves, phases))
            a += math.radians(turn)
            points.append((x + r * k * math.cos(a), y + r * k * math.sin(a)))
        self.path(_smooth(points), ink, tint, **kw)

    def contour(self, points, ink=MAIN, tint=100, **kw):
        """Гладкий замкнутый контур через точки."""
        self.path(_smooth(points), ink, tint, **kw)

    def influence(self, a, b, mutual=False, ink=MAIN, tint=100, soft=9, **kw):
        """Круг a=(x, y, r) продавлен кругом b. При mutual граница между ними прямая, как у двух равных сил."""
        (ax, ay, ar), (bx, by, br) = a, b
        if mutual:
            d = math.hypot(bx - ax, by - ay)
            ux, uy = (bx - ax) / d, (by - ay) / d
            big = ar * 40
            bx, by, br = ax + ux * (d / 2 + big), ay + uy * (d / 2 + big), big
        n, radii = 360, []
        for i in range(n):
            ca, sa = math.cos(math.radians(i)), math.sin(math.radians(i))
            fx, fy = ax - bx, ay - by
            bq = fx * ca + fy * sa
            disc = bq * bq - (fx * fx + fy * fy - br * br)
            t = -bq - math.sqrt(disc) if disc > 0 else ar
            radii.append(min(ar, t) if t > 0 else ar)
        raw = list(radii)
        for _ in range(2):
            radii = [sum(radii[(i + k) % n] for k in range(-soft, soft + 1)) / (2 * soft + 1) for i in range(n)]
        points = []
        for i in range(0, n, 3):
            r, a2 = min(radii[i], raw[i]), math.radians(i)
            points.append((ax + r * math.cos(a2), ay + r * math.sin(a2)))
        self.path(_smooth(points), ink, tint, **kw)

    # Объём

    def cube(self, x, y, a, top=(ACCENT, 70), left=(ACCENT, 100), right=(ACCENT, 30), angle=0, **kw):
        """Изометрический куб. Вернёт вершины по часовой от верхней, последней идёт центр: так строится открытый объём."""
        c, h = a * math.cos(math.radians(30)), a / 2
        v = _rot(
            [(x, y - a), (x + c, y - h), (x + c, y + h), (x, y + a), (x - c, y + h), (x - c, y - h), (x, y)],
            angle,
            (x, y),
        )
        self.poly([v[0], v[1], v[6], v[5]], *top, **kw)
        self.poly([v[5], v[6], v[3], v[4]], *left, **kw)
        self.poly([v[6], v[1], v[2], v[3]], *right, **kw)
        return v

    def wirecube(self, x, y, a, ink=MAIN):
        c, h = a * math.cos(math.radians(30)), a / 2
        self.poly(
            [(x, y - a), (x + c, y - h), (x + c, y + h), (x, y + a), (x - c, y + h), (x - c, y - h)],
            None,
            line=ink,
        )
        for ex, ey in ((x, y - a), (x + c, y + h), (x - c, y + h)):
            self.line(x, y, ex, ey, ink, "dash")
        for ex, ey in ((x, y + a), (x + c, y - h), (x - c, y - h)):
            self.line(x, y, ex, ey, ink)

    def plane(self, x, y, w, ink=MAIN, tint=100, **kw):
        """Плоскость в изометрии: ромб шириной 2w."""
        h = w * math.tan(math.radians(30))
        self.poly([(x, y - h), (x + w, y), (x, y + h), (x - w, y)], ink, tint, **kw)

    def pierce(self, x, y, size, r=None, front=0, back=0, cloud=0, body=(ACCENT, 28), cap=(ACCENT, 60), plate=MAIN):
        """Проникновение и выдавливание: пластина с отверстием, цилиндр идёт сквозь неё.

        front и back задают длину цилиндра перед пластиной и за ней, cloud рисует за пластиной бесформенную массу.
        """
        r = r or size * 0.27
        k, skew = 0.74, 0.29
        at = lambda u, v: (x + k * (u - size / 2), y - size / 2 + v - skew * (u - size / 2))
        corners = [at(0, 0), at(size, 0), at(size, size), at(0, size)]
        hole = [
            at(size / 2 + r * math.cos(t), size / 2 + r * math.sin(t))
            for t in (math.tau * i / 72 for i in range(72))
        ]
        axis = (0.92, 0.38)

        if cloud:
            with self.part("cloud"):
                self.blob(x - size * 0.42, y, cloud, "cloud", ACCENT, 28)
        if back:
            self.tube(hole, axis, -back, 0, body, (MAIN, 100))
        thick = self.u * 0.8
        self.poly([(px - thick, py - thick * 0.42) for px, py in corners], PAPER, line=MAIN)
        ring = "M" + "L".join(f"{_n(a)} {_n(b)}" for a, b in corners) + "Z"
        ring += "M" + "L".join(f"{_n(a)} {_n(b)}" for a, b in hole) + "Z"
        self.path(ring, plate, evenodd=True)
        with self.part("hole"):
            self.poly(hole, None, line=MAIN)
        if not (front or back):
            shifted = [(px - thick, py - thick * 0.42) for px, py in hole]
            self.subtract("M" + "L".join(f"{_n(a)} {_n(b)}" for a, b in hole) + "Z",
                          "M" + "L".join(f"{_n(a)} {_n(b)}" for a, b in shifted) + "Z", PAPER)
        if front:
            with self.part("tube"):
                self.tube(hole, axis, 0, front, body, cap)
        return hole, axis

    def tube(self, hole, axis, near, far, body=(ACCENT, 28), cap=(ACCENT, 60)):
        """Цилиндр вдоль оси: контур hole сдвинут на near и far. Торец рисуется на дальнем конце."""
        shift = lambda points, s: [(px + axis[0] * s, py + axis[1] * s) for px, py in points]
        count, nx, ny = len(hole), -axis[1], axis[0]
        dots = [px * nx + py * ny for px, py in hole]
        hi, lo = dots.index(max(dots)), dots.index(min(dots))
        arc = lambda s, e: [hole[(s + i) % count] for i in range((e - s) % count + 1)]
        a, b = arc(hi, lo), arc(lo, hi)
        side = lambda part: sum(px * axis[0] + py * axis[1] for px, py in part) / len(part)
        ahead, behind = (a, b) if side(a) > side(b) else (b, a)
        if far < near:
            ahead, behind = behind, ahead
        shape, end = shift(ahead, far) + shift(behind, near), shift(hole, far)
        self.poly(shape, PAPER)
        self.poly(shape, *body, line=MAIN)
        self.poly(end, PAPER)
        self.poly(end, *cap, line=MAIN)

    # Линии

    def line(self, x1, y1, x2, y2, ink=None, dash=None, weight=1, alpha=1):
        ink = self._c(ink or self._accent())
        pattern = f' stroke-dasharray="{self._dash(dash)}" stroke-linecap="round"' if dash else ""
        pattern += f' opacity="{alpha:.3f}"' if alpha < 1 else ""
        self.body.append(
            f'<line x1="{_n(x1)}" y1="{_n(y1)}" x2="{_n(x2)}" y2="{_n(y2)}" '
            f'stroke="{ink}" stroke-width="{_n(self.hair * weight * (1.5 if dash == "dot" else 1))}"{pattern}/>'
        )

    def rules(self, xs=(), ys=(), ink=None, dash=None):
        """Структурные линии во всю длину листа: выходят за край."""
        for x in xs:
            self.line(x, 0, x, self.h, ink, dash)
        for y in ys:
            self.line(0, y, self.w, y, ink, dash)

    def cross(self, x, y, r, ink=None, dash="dash"):
        """Оси через центр формы, чуть длиннее самой формы."""
        self.line(x - r, y, x + r, y, ink, dash)
        self.line(x, y - r, x, y + r, ink, dash)

    def arrow(self, x1, y1, x2, y2, bend=0, ink=None, dash=None, alpha=1):
        """Стрелка-выноска. bend выгибает её дугой: доля длины, знак задаёт сторону."""
        ink = self._c(ink or self._accent())
        dx, dy = x2 - x1, y2 - y1
        cx, cy = (x1 + x2) / 2 - dy * bend, (y1 + y2) / 2 + dx * bend
        bx, by = self._head(x2, y2, x2 - cx, y2 - cy, ink, alpha)
        pattern = f' stroke-dasharray="{self._dash(dash)}" stroke-linecap="round"' if dash else ""
        pattern += f' opacity="{alpha:.3f}"' if alpha < 1 else ""
        self.body.append(
            f'<path d="M{_n(x1)} {_n(y1)}Q{_n(cx)} {_n(cy)} {_n(bx)} {_n(by)}" fill="none" '
            f'stroke="{ink}" stroke-width="{_n(self.hair)}"{pattern}/>'
        )

    def orbit(self, x, y, r, start=-60, sweep=270, ink=None, dash=None, alpha=1):
        """Дуга со стрелкой вокруг центра: вращение. Углы в градусах, положительный sweep идёт по часовой."""
        ink = self._c(ink or self._accent())
        a, b = math.radians(start), math.radians(start + sweep)
        x1, y1 = x + r * math.cos(a), y + r * math.sin(a)
        x2, y2 = x + r * math.cos(b), y + r * math.sin(b)
        turn = 1 if sweep > 0 else -1
        self._head(x2, y2, -math.sin(b) * turn, math.cos(b) * turn, ink, alpha)
        pattern = f' stroke-dasharray="{self._dash(dash)}" stroke-linecap="round"' if dash else ""
        pattern += f' opacity="{alpha:.3f}"' if alpha < 1 else ""
        self.body.append(
            f'<path d="M{_n(x1)} {_n(y1)}A{_n(r)} {_n(r)} 0 {int(abs(sweep) > 180)} {int(sweep > 0)} {_n(x2)} {_n(y2)}" '
            f'fill="none" stroke="{ink}" stroke-width="{_n(self.hair)}"{pattern}/>'
        )

    def _head(self, x, y, tx, ty, ink, alpha=1):
        """Наконечник в точке (x, y) по направлению (tx, ty). Вернёт основание: туда идёт линия."""
        size = math.hypot(tx, ty) or 1
        tx, ty = tx / size, ty / size
        scale = min(self.u, 10.8)
        head, half = 1.5 * scale, 0.42 * scale
        bx, by = x - tx * head, y - ty * head
        self.poly([(x, y), (bx - ty * half, by + tx * half), (bx + ty * half, by - tx * half)], ink, alpha=alpha)
        return bx, by

    def dot(self, x, y, r=None, ink=None, **kw):
        """Метка на важной точке формы: вершина, центр, начало движения."""
        self.disc(x, y, r or 0.8 * self.u, ink or self._accent(), **kw)

    def band(self, points, width, ink=MAIN):
        """Полоса-масса по гладкой линии через точки: поток, ветка, дорога."""
        self.body.append(
            f'<path d="{_smooth(points, closed=False)}" fill="none" stroke="{self._c(ink)}" stroke-width="{_n(width)}"/>'
        )

    # Поля форм

    def lattice(self, x, y, cols, rows, step, r, ink=MAIN, tint=100, **kw):
        """Формальная структура: одинаковые круги на ровной сетке. Вернёт центры."""
        centers = [(x + c * step, y + i * step) for i in range(rows) for c in range(cols)]
        for cx, cy in centers:
            self.disc(cx, cy, r, ink, tint, **kw)
        return centers

    def scatter(self, x, y, w, h, n, rmin, rmax, ink=MAIN, tint=100, gap=0, inside=None, size=None, **kw):
        """Неформальная структура: круги без рисунка, не касаются друг друга. Вернёт (x, y, r).

        inside(x, y) сужает поле до любой фигуры, size(x, y) задаёт радиус по месту.
        """
        placed = []
        for _ in range(n * 400):
            if len(placed) == n:
                break
            r = self.rng.uniform(rmin, rmax)
            cx, cy = self.rng.uniform(x + r, x + w - r), self.rng.uniform(y + r, y + h - r)
            r = size(cx, cy) if size else r
            if inside and not inside(cx, cy):
                continue
            if all(math.hypot(cx - a, cy - b) > r + c + gap for a, b, c in placed):
                placed.append((cx, cy, r))
        if len(placed) < n:
            raise ValueError(f"в поле {w}×{h} поместилось {len(placed)} кругов из {n}: увеличь поле или уменьши круги")
        for cx, cy, r in placed:
            self.disc(cx, cy, r, ink, tint, **kw)
        return placed

    def diffusion(self, x, y, w, h, step, rmin, rmax, focus=None, ink=MAIN, tint=100, jitter=0.2, **kw):
        """Рассеяние: сетка расшатана, круги растут к точке focus."""
        fx, fy = focus or (x + w / 2, y + h / 2)
        reach = math.hypot(max(fx - x, x + w - fx), max(fy - y, y + h - fy))
        for i in range(int(h / step) + 1):
            for c in range(int(w / step) + 1):
                cx = x + c * step + self.rng.uniform(-jitter, jitter) * step
                cy = y + i * step + self.rng.uniform(-jitter, jitter) * step
                near = max(0, 1 - math.hypot(cx - fx, cy - fy) / reach)
                r = rmin + (rmax - rmin) * near**2.4 * self.rng.uniform(0.8, 1.1)
                self.disc(cx, cy, r, ink, tint, **kw)

    def mass(self, x, y, cols, rows, step, ink=MAIN, tint=100, sizes=(0.5, 0.66, 0.92), **kw):
        """Масса: круги на сетке, размер случайный из трёх, срастаются в одно тело."""
        for i in range(rows):
            for c in range(cols):
                self.disc(x + c * step, y + i * step, step * self.rng.choice(sizes), ink, tint, **kw)

    def fade(self, shape, x, y, w, h, start, end, angle=0, ink=ACCENT, step=None):
        """Растровая растяжка внутри контура shape: тинт идёт от start к end вдоль угла angle."""
        s = step or self.step * 1.5
        self.uid += 1
        color = self._c(ink)
        if self.tone == "flat":
            self.defs.append(
                f'<linearGradient id="{self.ns}g{self.uid}" gradientTransform="rotate({_n(angle)} .5 .5)">'
                f'<stop offset="0" stop-color="{color}" stop-opacity="{start / 100:.2f}"/>'
                f'<stop offset="1" stop-color="{color}" stop-opacity="{end / 100:.2f}"/></linearGradient>'
            )
            self.body.append(f'<path d="{shape}" fill="url(#{self.ns}g{self.uid})"/>')
            return
        self.defs.append(f'<clipPath id="{self.ns}c{self.uid}"><path d="{shape}"/></clipPath>')
        a = math.radians(angle)
        ux, uy = math.cos(a), math.sin(a)
        low = min(ux * px + uy * py for px in (x, x + w) for py in (y, y + h))
        high = max(ux * px + uy * py for px in (x, x + w) for py in (y, y + h))
        dots, row, py = [], 0, y
        while py <= y + h + s:
            px = x + (row % 2) * s / 2 ** 0.5
            while px <= x + w + s:
                k = (ux * px + uy * py - low) / (high - low)
                t = (start + (end - start) * k) / 100
                if t > 0.004:
                    r = s * math.sqrt(t / math.pi) if t < 0.5 else s * (0.399 + (t - 0.5) * 0.62)
                    dots.append(f'<circle cx="{_n(px)}" cy="{_n(py)}" r="{_n(r)}"/>')
                px += s * 2**0.5
            py += s / 2**0.5
            row += 1
        self.body.append(f'<g clip-path="url(#{self.ns}c{self.uid})" fill="{color}">{"".join(dots)}</g>')

    def tree(self, x, y, r, label, branches, spread=(0, 360), reach=None, size=2.1, ink=ACCENT, arrows=False):
        """Карта: круг-корень, волосные лучи, круги детей. branches: подписи или (подпись, [дети]).

        arrows=True показывает, что от корня к детям что-то идёт.
        """
        reach = reach or r * 3.4
        count, (a0, a1) = len(branches), spread
        full = abs(a1 - a0) >= 360
        for i, item in enumerate(branches):
            name, kids = item if isinstance(item, tuple) else (item, [])
            a = a0 + (a1 - a0) * (i + 0.5 if full else i) / (count if full else max(count - 1, 1))
            bx, by = x + reach * math.cos(math.radians(a)), y + reach * math.sin(math.radians(a))
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            if arrows:
                self.arrow(x + r * ca, y + r * sa, bx - (r * 0.36 + 0.6 * self.u) * ca, by - (r * 0.36 + 0.6 * self.u) * sa, ink=ink)
            else:
                self.line(x + r * ca, y + r * sa, bx, by)
            self.disc(bx, by, r * 0.36, ink)
            right = math.cos(math.radians(a)) >= 0
            gap = (r * 0.36 + 1.2 * self.u) * (1 if right else -1)
            self.text(bx + gap, by + 0.36 * size * self.u, name, size, anchor="start" if right else "end")
            if kids:
                self.tree(bx, by, r * 0.36, None, kids, (a - 38, a + 38), reach * 0.62, size * 0.86, ink)
        self.disc(x, y, r, ink)
        if label:
            self.text(x, y + r * 0.13, label, r * 0.36 / self.u, PAPER, 700, "middle")

    # Текст

    def text(self, x, y, s, size=1.8, ink=None, weight=400, anchor="start", angle=0, track=0, alpha=1):
        """Одна строка. size в долях self.u: 1.8 это 1,8% ширины листа."""
        ink = self._c(ink or self.on_ground())
        extra = f' letter-spacing="{_n(track * size * self.u)}"' if track else ""
        turn = f' transform="rotate({_n(angle)} {_n(x)} {_n(y)})"' if angle else ""
        turn += f' opacity="{alpha:.3f}"' if alpha < 1 else ""
        self.body.append(
            f'<text x="{_n(x)}" y="{_n(y)}" font-size="{_n(size * self.u)}" font-weight="{weight}" '
            f'fill="{ink}" text-anchor="{anchor}"{extra}{turn}>{html.escape(s, quote=False)}</text>'
        )

    def lead(self, x, y, term, lines, size=3, ink=None, accent=None, weight=400, leading=1.3):
        """Термин с точкой и определение в подбор: строки разбиты руками. Вернёт y под блоком."""
        ink, accent = self._c(ink or self.on_ground()), self._c(accent or self._accent())
        px = size * self.u
        for i, s in enumerate(lines):
            run = html.escape(s, quote=False)
            if i == 0:
                run = f'<tspan fill="{accent}" font-weight="500">{html.escape(term)}</tspan> {run}'
            self.body.append(
                f'<text x="{_n(x)}" y="{_n(y + i * px * leading)}" font-size="{_n(px)}" '
                f'font-weight="{weight}" fill="{ink}">{run}</text>'
            )
        return y + len(lines) * px * leading

    def statement(self, x, y, term, lines, **kw):
        """Крупное утверждение: открывает раздел или держит лист один."""
        return self.lead(x, y, term, lines, size=4.5, weight=500, leading=1.26, **kw)

    def title(self, x, y, s, ink=None, size=10.5):
        self.text(x, y, s, size, ink or self._accent(), 700, track=-0.012)

    def note(self, x, y, lines, ink=None, size=1.8, leading=1.34):
        """Мелкая подпись или сноска. Вернёт y под ней."""
        for i, s in enumerate(lines):
            self.text(x, y + i * size * self.u * leading, s, size, ink)
        return y + len(lines) * size * self.u * leading

    def runner(self, *parts, side="left", ink=None):
        """Колонтитул капсом: разделы через черту, последний полужирный."""
        y, anchor = 6.6 * self.u, "start" if side == "left" else "end"
        x = self.margin if side == "left" else self.w - self.margin
        ink = self._c(ink or self.on_ground())
        head = " | ".join(p.upper() for p in parts[:-1])
        tail = html.escape(parts[-1].upper())
        self.body.append(
            f'<text x="{_n(x)}" y="{_n(y)}" font-size="{_n(1.34 * self.u)}" fill="{ink}" text-anchor="{anchor}" '
            f'letter-spacing="{_n(0.08 * 1.34 * self.u)}" font-weight="400">{html.escape(head)}'
            f'{" | " if head else ""}<tspan font-weight="700">{tail}</tspan></text>'
        )

    # Сборка

    @contextlib.contextmanager
    def clip(self, shape):
        """Всё внутри обрезается контуром shape: так форма упирается в рамку."""
        self.uid += 1
        self.defs.append(f'<clipPath id="{self.ns}c{self.uid}"><path d="{shape}"/></clipPath>')
        self.body.append(f'<g clip-path="url(#{self.ns}c{self.uid})">')
        yield
        self.body.append("</g>")

    @contextlib.contextmanager
    def at(self, x, y, scale=1, angle=0):
        """Своя система координат: ячейка азбуки, развёрнутая группа. Волосная линия и растр сохраняют размер листа."""
        saved = self.u, self.hair, self.step
        self.u, self.hair, self.step = self.u / scale, self.hair / scale, self.step / scale
        self.body.append(f'<g transform="translate({_n(x)} {_n(y)}) rotate({_n(angle)}) scale({_n(scale)})">')
        yield
        self.body.append("</g>")
        self.u, self.hair, self.step = saved

    @contextlib.contextmanager
    def part(self, name):
        """Подвижная часть: страница находит её по data-part. Без скрипта лист остаётся статичным."""
        self.body.append(f'<g data-part="{name}">')
        yield
        self.body.append("</g>")

    def markup(self, alt=""):
        loop = f' data-loop="{self.loop}"' if self.loop else ""
        loop += ' direction="rtl"' if self.rtl else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" font-family="{self.font}" data-u="{_n(self.u)}"{loop} role="img" aria-labelledby="{self.ns}t" style="isolation:isolate">'
            f'<title id="{self.ns}t">{html.escape(alt)}</title><defs>{"".join(self.defs)}</defs>'
            f'<rect width="{self.w}" height="{self.h}" fill="{self.fill}"/>{"".join(self.body)}</svg>\n'
        )

    def save(self, path, alt=""):
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.markup(alt), encoding="utf-8")
        return path
