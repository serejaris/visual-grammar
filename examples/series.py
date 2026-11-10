#!/usr/bin/env python3
"""Как работает скилл: восемь листов, по листу на шаг, и два запасных варианта карты смысла. Через всю серию идёт пример из SKILL.md: субагент решает часть задачи отдельно. Запуск: series.py папка [имена]."""
import contextlib
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from alphabet import SHEETS as ABC
from vg import ACCENT, MAIN, PAPER, Plate, box, circle, sector

PALETTE = "brand"
TOTAL = 8
LEAD = 170  # подпись стоит на одной высоте всю серию, её отсутствие на последнем листе заметно
LABEL = 2.7

# Пример серии: вся задача, отданная часть, отдельный контекст, результат
DISC = (190, 1030, 400)
SLICE = (-62, -22)
FRAME = (650, 440, 340)


def sheet(n, slug, **kw):
    p = Plate("page", slug, palette=PALETTE, **kw)
    p.runner("Visual Grammar", "Как работает скилл", f"{n} из {TOTAL}")
    return p


def thought(path):
    """Доминирование: сплошное поле мелких точек, внутри него поляна с одним отношением: большой круг действует на малый."""
    p = sheet(1, "thought")
    y, big, small = 790, (344, 196), (886, 58)

    def field(x, y0):
        if y0 < 330:
            return False
        t = max(0, min(1, (x - big[0]) / (small[0] - big[0])))
        reach = 262 - 96 * t
        band = math.hypot(x - big[0] - t * (small[0] - big[0]), y0 - y) - reach
        return band > 0 and p.rng.random() < min(1, 0.12 + band / 120)

    p.scatter(0, 0, p.w, p.h, 620, 3.5, 11, MAIN, gap=9, inside=field)
    p.disc(big[0], y, big[1], MAIN)
    p.disc(small[0], y, small[1], MAIN)
    p.poly([(big[0] + big[1] - 8, y - 24), (small[0] - small[1] - 10, y), (big[0] + big[1] - 8, y + 24)], ACCENT)
    p.text(big[0], y + 14, "кто", 3.4, PAPER, 500, "middle")
    p.text(small[0], y + 104, "на что", LABEL, anchor="middle")
    p.text((big[0] + big[1] + small[0] - small[1]) / 2 - 24, y - 44, "как", LABEL, anchor="middle")
    p.lead(p.margin, LEAD, "Мысль.", ["Одна фраза: кто действует,", "на что и как. Пример: субагент решает", "часть задачи отдельно."])
    p.save(path, "Сплошное поле мелких точек, на поляне в нём большой круг острой стрелкой направлен на малый")


def figure(p, stage="color"):
    """Лист-пример: от круга отделён сектор, сектор лежит в своей рамке, обратно идёт точка.

    stage: wire масса только у главной формы, mono одна краска, color акцент на отданной части.
    """
    x, y, r = DISC
    start, end = SLICE
    left, top, side = FRAME
    whole, gap = circle(x, y, r), sector(x, y, r + 2, start, end)
    part = sector(left + 28, top + side - 34, r * 0.74, start, end)
    cx, cy = left + side / 2, top + side / 2
    p.subtract(whole, gap, MAIN)
    p.path(sector(x, y, r, start, end), None, line=MAIN, dash="dash")
    if stage == "wire":
        p.rect(cx, cy, side, side, None, line=MAIN, dash="dash")
        p.path(part, None, line=MAIN, dash="dash")
        p.disc(436, 844, 15, None, line=MAIN, dash="dash")
        return
    p.rect(cx, cy, side, side, None, line=MAIN)
    p.path(part, ACCENT if stage == "color" else MAIN, 100 if stage == "color" else 42)
    p.arrow(486, 680, 636, 580, 0.2, MAIN, "dash")
    p.arrow(760, 796, 454, 826, -0.34, MAIN)
    p.dot(436, 824, 15, MAIN)


def map_sorter(path):
    """Негатив и позитив: вещи стоят отверстиями в плите, над каждым висит его форма. Лишней форме входить некуда."""
    p = sheet(2, "map-sorter")
    top, base, drop = 716, 650, 480
    disc, frame, part, dot = (90, 196), (414, 216), (548, 296), (900, 30)
    p.rect(540, (top + p.h + 40) / 2, p.w + 40, p.h - top + 40, MAIN)

    def row(dy, ink, hollow):
        p.disc(disc[0], base - disc[1] + dy, disc[1], ink)
        x, y, side = frame[0], base - frame[1] / 2 + dy, frame[1]
        p.path(box(x, y, side, side) + (box(x, y, side - 56, side - 56) if hollow else ""), ink, evenodd=True)
        p.path(sector(part[0], base + dy, part[1], *SLICE), ink)
        p.disc(dot[0], base - dot[1] + dy, dot[1], ink)

    row(drop, PAPER, False)
    row(0, ACCENT, True)
    p.poly([(948, base), (1068, base), (1008, base - 104)], None, line=MAIN, dash="dash")
    for x, y1, y2 in ((190, 634, 756), (frame[0], base + 12, base + drop - frame[1] - 10), (680, 610, 872), (dot[0], base + 12, base + drop - 2 * dot[1] - 10)):
        p.arrow(x, y1, x, y2, 0, ACCENT, "dash")
    for x, word in ((140, "вся задача"), (frame[0], "отдельный контекст"), (690, "отданная часть"), (dot[0], "результат")):
        p.text(x, 1196, word, LABEL, PAPER, anchor="middle")
    p.lead(p.margin, LEAD, "Карта смысла.", ["Каждая вещь мысли получает", "свою форму. Форма без вещи снимается."])
    p.save(path, "Над тёмной плитой висят четыре фигуры, под каждой в плите отверстие её формы. Пятая штриховая фигура стоит над сплошной плитой")


def map_legend(path):
    """Формальная структура: карта как условные обозначения: строка, слово слева, стрелка, форма справа."""
    p = sheet(2, "map-legend")
    rows = ((300, 330), (630, 230), (860, 200), (1060, 110), (1170, 160))
    p.rules(ys=[y for y, _ in rows], ink=MAIN)
    x = 806
    words = ("вся задача", "отданная часть", "отдельный контекст", "результат")
    for (y, h), word in zip(rows, words):
        p.text(p.margin, y + h / 2 + 11, word, 3)
        p.dot(500, y + h / 2, 9, ACCENT)
        p.arrow(500, y + h / 2, x - 120, y + h / 2, 0, ACCENT)
    p.disc(x + 70, 465, 150, MAIN)
    p.path(sector(x - 100, 845, 230, *SLICE), MAIN)
    p.rect(x, 960, 150, 150, None, line=MAIN)
    p.disc(x, 1115, 20, MAIN)
    p.poly([(x - 56, 1296), (x + 56, 1296), (x, 1200)], None, line=MAIN, dash="dash")
    p.lead(p.margin, LEAD, "Карта смысла.", ["Каждая вещь мысли получает", "свою форму. Форма без вещи снимается."])
    p.save(path, "Таблица условных обозначений: в четырёх строках стрелка идёт к форме, в пятой штриховой форме не соответствует ничего")


def map_mirror(path):
    """Отражение: слева вещи без формы, справа те же вещи в геометрии. Ось держит пары."""
    p = sheet(2, "map-mirror")
    axis = 540
    p.line(axis, 300, axis, p.h, MAIN, "dash")
    p.blob(axis - 400, 1110, 214, "organic", MAIN, seed="вся задача")
    p.blob(axis - 250, 420, 108, "organic", MAIN, seed="контекст")
    p.blob(axis - 250, 690, 104, "organic", MAIN, seed="часть")
    p.blob(axis - 96, 866, 26, "organic", MAIN, seed="результат")
    p.disc(axis + 400, 1110, 214, MAIN)
    p.rect(axis + 250, 420, 190, 190, None, line=MAIN)
    p.path(sector(axis + 166, 790, 230, *SLICE), MAIN)
    p.disc(axis + 96, 866, 26, MAIN)
    p.poly([(590, 1262), (700, 1262), (645, 1166)], None, line=MAIN, dash="dash")
    for y, a, b in ((420, -128, 142), (690, -128, 150), (866, -64, 64), (1110, -150, 150)):
        p.arrow(axis + a, y, axis + b, y, 0, ACCENT)
    p.text(axis - 250, 410, "отдельный", LABEL, PAPER, anchor="middle")
    p.text(axis - 250, 444, "контекст", LABEL, PAPER, anchor="middle")
    p.text(axis - 250, 680, "отданная", LABEL, PAPER, anchor="middle")
    p.text(axis - 250, 714, "часть", LABEL, PAPER, anchor="middle")
    p.text(axis - 96, 934, "результат", LABEL, anchor="middle")
    p.text(70, 1120, "вся задача", LABEL, PAPER)
    p.lead(p.margin, LEAD, "Карта смысла.", ["Каждая вещь мысли получает", "свою форму. Форма без вещи снимается."])
    p.save(path, "Вдоль штриховой оси пары: слева бесформенные пятна, справа того же размера круг, сектор, рамка и точка, стрелки идут через ось")


def term(path):
    """Масштаб: из ровной сетки 66 фигур вышла одна и выросла в главную форму листа, ещё одна отмечена рядом."""
    p = sheet(3, "term")
    figures = [draw for _, _, cells in ABC for draw, _ in cells]
    cols, w, top, step = 11, (p.w - 2 * p.margin) / 11, 316, 64
    main, spare = p.inks[MAIN], p.inks[ACCENT]
    at = lambda i: (p.margin + w * (i % cols), top + step * (i // cols))
    p.inks[ACCENT] = main
    p.text = lambda *a, **k: None  # у фигуры 16 в ячейках цифры, в мелкой сетке они мусор
    for i, draw in enumerate(figures):
        x, y = at(i)
        if i == 60:
            continue
        hit = i == 35
        if hit:
            p.inks[MAIN] = p.inks[ACCENT] = spare
        with p.at(x, y, w / 100):
            with p.clip(box(50, 38, 100, 76)):
                draw(p)
        p.inks[MAIN], p.inks[ACCENT] = main, main
    p.inks[ACCENT] = spare
    del p.text
    x, y = at(60)
    p.rect(x + w / 2, y + 28, w, 56, None, line=MAIN, dash="dash")
    cx, cy, r = 720, 1130, 330
    p.subtract(circle(cx, cy, r), sector(cx, cy, r + 2, *SLICE), MAIN)
    p.path(sector(cx, cy, r, *SLICE), None, line=MAIN, dash="dash")
    p.arrow(x + w / 2, y + 62, cx - 20, cy - r - 12, 0.04, ACCENT, "dash")
    p.text(p.margin, 770, "61 Вычитание: главный", LABEL)
    p.text(p.margin, 812, "36 Движение: вспомогательный", LABEL, ACCENT)
    p.lead(p.margin, LEAD, "Термин.", ["Из словаря в 66 терминов", "отношение получает один главный", "и до двух вспомогательных."])
    p.save(path, "Ровная сетка мелких фигур, одной не хватает, штриховая стрелка ведёт от пустой ячейки к большому кругу с вырезанным сектором внизу")


def layout(path):
    """Положение: на листе только четыре решения. Масса главной формы, край выделен там, где режет её, место подписи, пустота."""
    p = sheet(4, "layout")
    x, y, r = DISC
    p.subtract(circle(x, y, r), sector(x, y, r + 2, *SLICE), MAIN)
    p.path(sector(x, y, r, *SLICE), None, line=MAIN, dash="dash")
    cut, wide, t = 678, 463, 16
    p.rect(t / 2, (cut + p.h) / 2, t, p.h - cut, ACCENT)
    p.rect(wide / 2, p.h - t / 2, wide, t, ACCENT)
    p.rect(540, 204, 846, 164, None, line=MAIN, dash="dash")
    p.text(110, 1190, "главная форма", LABEL, PAPER)
    p.text(536, 1270, "край режет форму", LABEL)
    p.text(790, 760, "пустота", LABEL, anchor="middle")
    p.text(945, 330, "подпись", LABEL, anchor="end")
    p.lead(p.margin, LEAD, "Раскладка.", ["До кода решено,", "какая форма главная, где её режет край,", "где пустота и где подпись."])
    p.save(path, "Большой круг срезан левым и нижним краями, край выделен там, где режет его. Наверху штриховое место подписи, вся правая часть листа пуста")


def ink(path):
    """Размер и тон: тот же лист в одной краске. Различие держат контур, размер и светлота."""
    p = sheet(5, "ink")
    figure(p, "mono")
    p.text(650, 420, "контур", LABEL, MAIN)
    p.text(304, 896, "размер", LABEL, MAIN)
    p.text(668, 490, "светлота", LABEL, MAIN)
    p.lead(p.margin, LEAD, "Монохром.", ["Без цвета отношение держат", "контур, размер и светлота."], accent=MAIN)
    p.save(path, "Тот же лист без цвета: плотный круг без сектора, контурная рамка, в ней сектор светлее, малая точка возвращается")


def colour(path):
    """Цвет: геометрия прошлого листа не изменилась, акцент встал на одну форму."""
    p = sheet(6, "colour")
    figure(p, "color")
    p.lead(p.margin, LEAD, "Цвет.", ["Ставится последним", "и выделяет главное в мысли."])
    p.save(path, "Тот же лист: единственная цветная форма это сектор в рамке")


def proof(path):
    """Масштаб и тон: две копии листа шириной 375 px, в цвете и в сером."""
    @contextlib.contextmanager
    def grey(q):
        saved = dict(q.inks)
        for key, color in saved.items():
            c = color.lstrip("#")
            r, g, b = (int(c[i : i + 2], 16) for i in (0, 2, 4))
            v = round(0.2126 * r + 0.7152 * g + 0.0722 * b)
            q.inks[key] = f"#{v:02x}{v:02x}{v:02x}"
        yield
        q.inks.update(saved)

    p = sheet(7, "proof")
    k, w, h = 375 / 1080, 375, 459
    top = p.h - h
    gap = 30

    def copy(left):
        with p.at(left, top, k):
            with p.clip(box(540, 661, 1080, 1322)):
                p.rect(540, 661, 1080, 1322, PAPER)
                figure(p, "color")
                for y, width in ((162, 640), (204, 500)):
                    p.rect(135 + width / 2, y, width, 22, MAIN)
        p.rect(left + w / 2, top + h / 2, w, h, None, line=MAIN)

    p.arrow(p.w, 0, w + 6, top - 7, 0, ACCENT)
    for s_ in (0.76, 0.56):
        p.line(0, p.h * (1 - s_), p.w * s_, p.h * (1 - s_), MAIN, "dash")
        p.line(p.w * s_, p.h * (1 - s_), p.w * s_, p.h, MAIN, "dash")
        p.dot(p.w * s_, p.h * (1 - s_), 7, ACCENT)
    copy(0)
    with grey(p):
        copy(w + gap)
    p.dot(p.w, 0, 12, ACCENT)
    p.text(w + gap + 36, top - 18, "в сером", LABEL)
    p.text(40, top - 18, "в цвете", LABEL)
    p.lead(p.margin, LEAD, "Проверка.", ["Отношение читается", "при ширине 375 px и в сером."])
    p.save(path, "Две малые копии листа стоят внизу, одна в цвете, другая в сером, диагональ идёт от угла копии к углу всего листа")


def blind(path):
    """Отсутствие: на месте подписи пустые строки. Формы говорят сами, подпись стала пересказом субагента."""
    p = sheet(8, "blind")
    figure(p, "color")
    for y, width in ((170, 640), (212, 520), (254, 580)):
        p.rect(p.margin + width / 2, y - 11, width, 30, None, line=ACCENT, dash="dash")
    p.lead(620, 910, "Слепое чтение.", ["Субагент", "без контекста", "видит лист без подписи", 'и пересказывает: "кусок', "переносится из круга", "в рамку и указывает", 'обратно на место выреза".', "Пересказ совпал с картой."], size=2.8)
    p.save(path, "Тот же лист: на месте подписи пустые штриховые строки")


SHEETS = (thought, map_sorter, term, layout, ink, colour, proof, blind)
VARIANTS = (map_legend, map_mirror)


if __name__ == "__main__":
    folder = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    names = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] else None
    for number, build in enumerate(SHEETS, 1):
        if not names or build.__name__ in names:
            build(folder / f"{number:02d}-{build.__name__}.svg")
    for number, build in enumerate(VARIANTS, 1):
        if not names or build.__name__ in names:
            build(folder / f"v{number}-{build.__name__}.svg")
