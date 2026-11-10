#!/usr/bin/env python3
"""Двадцать листов на темы чата вайбкодеров и проектов: у каждого свой главный термин. Запуск: topics.py папка [имена] [палитра]."""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from vg import ACCENT, MAIN, PAPER, Plate, circle, mix

PALETTE = "brand"


def trace(points, closed=False):
    """Ломаная строкой пути."""
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in points) + ("Z" if closed else "")


def limits(path):
    """Ритм: круг лимита тает от шага к шагу и разом возвращается, сбросы идут через равные промежутки."""
    p = Plate("wide", "limits", palette=PALETTE)
    y, x, gap, cycle = 590, -70, 16, (112, 88, 66, 46, 28, 14, 5)
    radii, spots = cycle * 3, []
    for i, r in enumerate(radii):
        spots.append(x)
        x += r + gap + radii[(i + 1) % len(radii)]
    size = len(cycle)
    for i, (x, r) in enumerate(zip(spots, radii)):
        if i % size == 0:
            p.line(x, 340, x, p.h)
            if 0 < x < p.w / 2:
                p.text(x + 16, 836, "сброс", 2.2)
        p.disc(x, y, r, p.spot(i // size) if i % size == 0 else MAIN)
    for start in range(0, len(radii) - size, size):
        last, reset = start + size - 1, start + size
        p.line(spots[start], y - radii[start] - 10, spots[last], y - 14, MAIN)
        p.arrow(spots[last], y - 14, spots[reset] - 18, y - radii[reset] - 12, -0.34, ink=ACCENT)
    p.lead(p.margin, 150, "Сброс.", ["Лимит расходуется", "всю неделю и возвращается", "разом. Поэтому перед", "сбросом его сжигают."])
    p.save(path, "Ряд кругов тает до точки и разом возвращается к полному размеру, повтор идёт через равные промежутки")


def environment(path):
    """Формат: одна и та же форма входит в свой мягкий контур и не входит в жёсткую рамку."""
    p = Plate("square", "environment", palette=PALETTE)
    y, r, left, right, w, h, t = 640, 180, 280, 770, 250, 290, 11
    p.blob(left, y, r, "organic", MAIN, seed="environment")
    p.blob(left, y, r * 1.13, "organic", None, line=MAIN, dash="dash", seed="environment")
    p.blob(right, y, r, "organic", MAIN, seed="environment")
    p.rect(right, y - h / 2, w + t, t, ACCENT)
    p.rect(right, y + h / 2, w + t, t, ACCENT)
    p.rect(right - w / 2, y, t, h, ACCENT)
    p.rect(right + w / 2, y, t, h, ACCENT)
    p.text(left, 912, "ручная среда", 2.6, anchor="middle")
    p.text(right, 912, "автоматизация", 2.6, anchor="middle")
    p.lead(p.margin, 150, "Окружение.", ["Агент подстраивается под окружение,", "где его растили. В автоматизации оно другое."])
    p.save(path, "Одна и та же форма дважды: слева она точно входит в свой контур, справа вылезает за края жёсткой рамки")


def race(path):
    """Параллель: три полосы идут на равном расстоянии, две обрываются, одна уходит за край листа."""
    p = Plate("wide", "race", ACCENT, PALETTE)
    start, stretch = 270, 1420

    def lane(shift, end):
        points = []
        for i in range(70):
            x = start + (end - start) * i / 69
            k = (x - start) / stretch * math.tau * 0.6
            y, slope = 660 - 110 * (1 - math.cos(k)), -110 * math.sin(k) * math.tau * 0.6 / stretch
            size = math.hypot(1, slope)
            points.append((x - shift * slope / size, y + shift / size))
        return points

    p.line(start, 0, start, p.h, PAPER)
    runs = ((-104, 1760, "DeepSeek", "рабочий вариант"), (0, 930, "GLM", "упёрся в сборку"), (104, 620, "MiMo", "ничего рабочего"))
    for shift, end, name, result in runs:
        points = lane(shift, end)
        p.band(points, 62, MAIN)
        x, y = min(points, key=lambda q: abs(q[0] - start))
        p.text(start - 18, y + 13, name, 2.4, PAPER, 500, "end")
        if end < p.w:
            ex, ey = points[-1]
            p.dot(ex, ey, 31, PAPER)
            p.text(ex + 50, ey + 13, result, 2.4, MAIN)
        else:
            ex, ey = points[39]
            p.text(ex, ey + 84, result, 2.4, MAIN)
    p.lead(start + 26, 120, "Забег.", ["Одну задачу дали трём бесплатным", "агентам на два дня. Справился один."], ink=MAIN, accent=PAPER)
    p.save(path, "Три параллельные полосы стартуют от одной линии: две обрываются, третья уходит за край листа")


def fomo(path):
    """Траектория: точка всё время меняет цель и останавливается, не дойдя ни до одного круга."""
    p = Plate("page", "fomo", MAIN, PALETTE)
    models = ((860, 980, 190), (170, 640, 130), (900, 470, 170), (540, 1236, 66), (640, 790, 46))
    for i, (x, y, r) in enumerate(models):
        p.disc(x, y, r, p.spot(i, MAIN))
    x, y = 96, 1230
    p.disc(x, y, 11, None, line=ACCENT)
    for tx, ty, r in models:
        size = math.hypot(tx - x, ty - y)
        nx, ny = tx - (tx - x) / size * (r + 70), ty - (ty - y) / size * (r + 70)
        p.arrow(x, y, nx, ny, ink=ACCENT)
        x, y = nx, ny
    p.dot(x, y, 12)
    p.lead(p.margin, 150, "Фомо.", ["Новая модель выходит раньше, чем", "успевают освоить прошлую. Ни одну", "не осваивают до конца."])
    p.save(path, "Точка идёт ломаной линией от круга к кругу и каждый раз сворачивает, не дойдя до него")


def ban(path):
    """Активная структура: одна прямая режет круг из двадцати четырёх колец, половина съехала вдоль линии."""
    p = Plate("page", "ban", MAIN, PALETTE)
    x, y, r, a, shift, gap, far = 540, 880, 590, math.radians(-24), 108, 16, 3000
    ux, uy = math.cos(a), math.sin(a)
    start, end = (x - ux * far, y - uy * far), (x + ux * far, y + uy * far)

    def half(side, gap=0):
        ox, oy, nx, ny = -uy * gap, ux * gap, -uy * side * far, ux * side * far
        a, b = (start[0] + ox, start[1] + oy), (end[0] + ox, end[1] + oy)
        return trace([a, b, (b[0] + nx, b[1] + ny), (a[0] + nx, a[1] + ny)], True)

    def rings(cx, cy):
        p.disc(cx, cy, r, MAIN)
        for k in range(1, 24):
            p.disc(cx, cy, r * k / 24, None, line=p.inks[MAIN])

    with p.clip(half(-1)):
        rings(x, y)
    with p.clip(half(1, gap)):
        rings(x + ux * shift - uy * gap, y + uy * shift + ux * gap)
    p.line(*start, *end, ACCENT, weight=2)
    p.lead(p.margin, 130, "Бан.", ["Два года работы в аккаунте,", "одна проверка документа."])
    p.save(path, "Круг из тонких колец разрезан одной прямой линией, нижняя половина съехала вдоль разреза")


def sprint(path):
    """Угол смещения: план идёт прямо в цель, шаги уходят от него на малый угол и проходят мимо."""
    p = Plate("wide", "sprint", palette=PALETTE)
    x, y, tilt, goal, count = 190, 730, math.tan(math.radians(11)), 1230, 8
    top = lambda at: y - (at - x) * tilt
    p.rect((x + goal) / 2, y, goal - x, 6, MAIN)
    p.disc(goal, y, 66, MAIN)
    for i in range(1, count + 3):
        at = x + (goal - x) * i / count
        if i <= count:
            p.line(at, y - (66 if i == count else 0), at, top(at), MAIN, "dash")
        p.disc(at, top(at), 20, ACCENT)
    p.orbit(x, y, 340, 0, -11, ACCENT)
    p.dot(x, y, 15, MAIN)
    p.text(goal, y + 12, "цель", 2.2, PAPER, 500, "middle")
    p.text(x + 110, y + 56, "малый угол", 2.2)
    p.note(goal + 22, top(goal) + 70, ["большое", "расстояние"], size=2.2)
    p.lead(p.margin, 150, "Сверка.", ["Без неё агент немного уходит от плана,", "и к концу спринта отклонение большое."])
    p.save(path, "Прямая идёт в цель, цепочка точек из той же начальной точки уходит от неё на малый угол и проходит мимо цели")


def review(path):
    """Спираль: код в центре, каждый виток приносит новые замечания, и спираль не замыкается."""
    p = Plate("square", "review", MAIN, PALETTE)
    x, y, end = 700, 790, math.radians(45) + 3 * math.tau
    radius = lambda t: 640 * math.exp(0.1135 * (t - end))
    at = lambda t: (x + radius(t) * math.cos(t), y + radius(t) * math.sin(t))
    p.path(trace([at(i * 0.02) for i in range(int(end / 0.02) + 1)]), None, line=MAIN)
    t, count = 0.5, 0
    while t < end:
        p.dot(*at(t), 4 + radius(t) * 0.04, p.spot(count))
        t, count = t + 120 / radius(t), count + 1
    p.disc(x, y, 62, MAIN)
    p.text(x, y + 10, "код", 2.6, p.inks[MAIN], 500, "middle")
    p.lead(p.margin, 130, "Ревью.", ["Модель всегда найдёт что сказать,", "даже про свой код."])
    p.save(path, "Спираль раскручивается от круга в центре, на витках всё больше точек, линия уходит за край")


def mentors(path):
    """Вес: каждый ряд вдвое больше прошлого и держит верхний, деньги поднимаются к одной точке."""
    p = Plate("page", "mentors", palette=PALETTE)
    rows = (390, 540, 670, 790, 900, 1000, 1092, 1176, 1256)
    sizes = (54, 44, 35, 27, 20, 14, 9.5, 6.4, 4.2)
    place = lambda level, j: 540 + (j - (2**level - 1) / 2) * 1280 / 2**level
    for level in range(1, len(rows)):
        for j in range(2**level):
            p.line(place(level, j), rows[level], place(level - 1, j // 2), rows[level - 1], MAIN)
    for level in range(1, len(rows)):
        for j in range(2**level):
            p.disc(place(level, j), rows[level], sizes[level], MAIN)
    j = 2 ** (len(rows) - 1) // 2 - 37
    for level in range(len(rows) - 1, 0, -1):
        x1, y1, x2, y2 = place(level, j), rows[level], place(level - 1, j // 2), rows[level - 1]
        size = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / size, (y2 - y1) / size
        p.arrow(x1, y1, x2 - ux * (sizes[level - 1] + 3), y2 - uy * (sizes[level - 1] + 3), ink=ACCENT)
        p.disc(x1, y1, sizes[level], ACCENT)
        j //= 2
    p.disc(540, rows[0], sizes[0], ACCENT)
    p.lead(p.margin, 130, "Наставники наставников.", ["Покупают", "обязательную подписку, чтобы продавать", "дальше. Платит тот, кто стоит ниже."])
    p.save(path, "Дерево: одна точка наверху, каждый ряд вдвое больше прошлого, внизу плотная масса, стрелки идут вверх")


def metadata(path):
    """Невидимая структура: документ выглядит чистым, под линзой виден ровный рисунок, которого глаз не видел."""
    p = Plate("page", "metadata", MAIN, PALETTE)
    dark = p.inks[MAIN]
    p.rect(540, 860, 780, 1060, MAIN)
    for row in range(19):
        p.line(204, 440 + row * 46, 204 + p.rng.uniform(420, 672), 440 + row * 46, dark)
    lens = (650, 806, 252)
    with p.clip(circle(*lens)):
        p.rect(lens[0], lens[1], 520, 520, dark)
        p.lattice(lens[0] - 252, lens[1] - 252, 11, 11, 50.4, 9, ACCENT)
    p.disc(*lens, None, line=ACCENT)
    p.rect(lens[0] + 262, lens[1] + 262, 240, 34, dark, angle=45)
    p.lead(p.margin, 130, "Метаданные.", ["Файл выглядит чистым, но хранит след", "программы, которая его собрала."])
    p.save(path, "Лист с ровными строками, под круглой лупой на нём виден правильный рисунок точек")


def launch(path):
    """Объём: продукт заперт внутри куба, поле людей вокруг его не касается."""
    p = Plate("square", "launch", palette=PALETTE)
    x, y, a = 540, 660, 236
    edge, half = (a + 42) * math.cos(math.radians(30)), a + 42

    def crowd(cx, cy):
        dx, dy = abs(cx - x), abs(cy - y)
        reach = max(dx / edge, (dy + dx * math.tan(math.radians(30))) / half)
        return reach > 1 and not (cy < 270 and cx < 960) and p.rng.random() < 1 / (1 + (5 * (reach - 1)) ** 2)

    for i, (cx, cy, r) in enumerate(p.scatter(0, 0, p.w, p.h, 260, 5, 9, None, gap=11, inside=crowd)):
        p.disc(cx, cy, r, p.spot(i))
    p.disc(x, y, 96, MAIN)
    p.wirecube(x, y, a)
    p.lead(p.margin, 130, "Выпуск.", ["Пока продукт не вышел,", "его некому оценить."])
    p.save(path, "Круг внутри прозрачного куба, вокруг куба поле мелких точек, ни одна его не касается")


def portrait(path):
    """Структурный скелет: отвес и линии черт выходят за край, на них собраны голова и длинная борода."""
    p = Plate("page", "portrait", palette=PALETTE)
    x, y, a, b = 540, 640, 226, 306
    egg = [(x + a * math.cos(t) * (1 - 0.17 * math.sin(t)), y + b * math.sin(t)) for t in (math.tau * i / 72 for i in range(72))]
    shape = trace(egg, True)
    brow, eye, nose, mouth = y - 44, y + 4, y + 118, y + 186
    p.line(0, 1168, 300, 1042)
    p.line(p.w, 1168, 780, 1042)
    beard = [(x - 196, y + 96), (x - 174, y + 330), (x - 116, y + 520), (x - 40, y + 690), (x + 30, y + 690), (x + 112, y + 520), (x + 172, y + 330), (x + 196, y + 96), (x + 120, y + 150), (x, y + 136), (x - 120, y + 150)]
    p.contour(egg, PAPER, line=MAIN)
    p.contour(beard, MAIN)
    with p.clip(shape):
        p.rect(x + 160, y, 320, 680, MAIN, 40)
    p.ellipse(x, mouth, 62, 16, PAPER)
    p.rect(x - 100, brow, 112, 11, MAIN)
    p.rect(x + 100, brow, 112, 11, MAIN)
    p.ellipse(x - 100, eye, 34, 11, MAIN)
    p.ellipse(x + 100, eye, 34, 11, MAIN)
    p.poly([(x + 6, eye + 16), (x + 46, nose), (x - 6, nose + 4)], MAIN)
    p.line(x, 270, x, p.h, dash="dash")
    p.rules(ys=[brow, eye, nose, mouth])
    p.line(0, y - b, p.w, y - b)
    p.dot(x, y - b, 11)
    p.lead(p.margin, 130, "Построение.", ["Портрет начинают с пропорций.", "Черты ставят на них последними."])
    p.save(path, "Голова из овала с длинной бородой, тонкие линии отвеса и черт лица проходят через весь лист")


def lead(path):
    """Главное и подчинённое: большой круг идёт по прямой, вокруг неё петля за петлёй крутятся малые циклы."""
    p = Plate("wide", "lead", palette=PALETTE)
    x0, y0, a, b, tilt = -160, 730, 34, 118, math.radians(-7)
    c, s = math.cos(tilt), math.sin(tilt)
    at = lambda u, v: (x0 + u * c - v * s, y0 + u * s + v * c)
    points = [at(a * t - b * math.sin(t), -b * math.cos(t)) for t in (i * 0.05 for i in range(1300))]
    p.path(trace(points), None, line=MAIN)
    p.line(*at(0, 0), *at(1900, 0), ACCENT, weight=2)
    cx, cy = at(1190, 0)
    p.disc(cx, cy, 172, MAIN)
    p.orbit(cx, cy, 116, -150, 270, PAPER)
    p.lead(p.margin, 150, "Лид.", ["Агент ведёт проект целиком: пишет план,", "нанимает исполнителей, принимает работу."])
    p.save(path, "Большой круг идёт по прямой, вокруг неё тонкая линия делает петлю за петлёй")


def funnel(path):
    """Формальная структура: ровная сетка людей, пустые места показывают, сколько не дошло, обрыв отмечен линией."""
    p = Plate("page", "funnel", palette=PALETTE)
    counts = (15, 14, 13, 12, 5, 4, 3, 2, 1)
    cols, step, r, left, top, drop = 15, 76, 27, 330, 340, 64
    for row, n in enumerate(counts):
        y = top + row * step + (drop if row > 3 else 0)
        first = (cols - n) // 2
        for c in range(cols):
            x = left + (c - 4) * step
            if first <= c < first + n:
                p.disc(x, y, r, ACCENT if row == len(counts) - 1 else MAIN)
            else:
                p.disc(x, y, r, None, line=MAIN, dash="dash")
    edge = top + 3 * step + r + 62
    p.rules(ys=[edge])
    p.text(p.margin, edge - 12, "самый резкий шаг", 2.6)
    p.lead(p.margin, 130, "Воронка.", ["С каждым шагом бота людей меньше,", "и на одном шаге уходит больше всего."])
    p.save(path, "Ровная сетка кругов сверху вниз пустеет, резкий обрыв отмечен линией, внизу остаётся одна точка")


def identity(path):
    """Смещение: запись индекса и карточка разъехались, зазор между ними выделен."""
    p = Plate("square", "identity", palette=PALETTE)
    a, b, r = (440, 660), (580, 590), 300
    p.subtract(circle(*a, r), circle(*b, r), ACCENT)
    with p.clip(circle(*b, r)):
        p.disc(*a, r, MAIN)
    p.disc(*b, r, None, line=MAIN, dash="dash")
    p.text(150, 1032, "индекс: проверен", 2.6)
    p.text(690, 268, "карточки нет", 2.6)
    p.lead(p.margin, 130, "Расхождение.", ['Индекс пишет "проверен",', "а карточки человека нет."])
    p.save(path, "Плотный круг и штриховой контур той же величины разъехались, зазор между ними выделен цветом")


def component(path):
    """Центробежное излучение: один компонент расходится лучами на все страницы и стоит на каждой."""
    p = Plate("page", "component", palette=PALETTE)
    sx, sy, sw, sh = 540, 430, 320, 150
    cols, rows, w, h, gapx, gapy, top = 7, 5, 118, 158, 24, 30, 720
    left = (p.w - cols * w - (cols - 1) * gapx) / 2
    pages = [(left + c * (w + gapx), top + r * (h + gapy)) for r in range(rows) for c in range(cols)]
    for x, y in pages:
        p.line(sx, sy + sh / 2, x + w / 2, y + 34, MAIN)
    for x, y in pages:
        p.rect(x + w / 2, y + h / 2, w, h, PAPER, line=MAIN)
        p.rect(x + w / 2, y + 34, w * 0.6, 28, ACCENT)
    p.rect(sx, sy, sw, sh, ACCENT)
    p.text(sx, sy + 14, "компонент", 3.2, PAPER, 500, "middle")
    p.lead(p.margin, 130, "Компонент.", ["Живёт в одном месте, сборка сама ставит его", "на страницы. Одна правка меняет всю книгу."])
    p.save(path, "Один прямоугольник сверху, лучи расходятся к сетке страниц, на каждой стоит его малая копия")


def proxy(path):
    """Касание: два больших круга сходятся в одной точке, через неё идёт всё между ними."""
    p = Plate("wide", "proxy", ACCENT, PALETTE)
    y, r, touch = 690, 440, 800
    p.disc(touch - r, y, r, MAIN)
    p.disc(touch + r, y, r, MAIN)
    p.line(0, y, p.w, y, PAPER, "dash")
    p.dot(touch, y, 15, PAPER)
    p.line(touch, y - 36, touch, 254, PAPER)
    p.text(touch + 16, 278, "прокси", 2.4, PAPER, 500)
    p.text(touch - r, y - 26, "харнесы", 3, PAPER, anchor="middle")
    p.text(touch + r, y - 26, "модели", 3, PAPER, anchor="middle")
    p.lead(p.margin, 96, "Прокси.", ["Claude Code, Codex и OpenCode выходят", "к моделям через один прокси."], ink=PAPER, accent=PAPER)
    p.save(path, "Два огромных круга касаются в одной точке, она отмечена")


def cutover(path):
    """Движение: бот ушёл со старой базы на новую, на старой остался штриховой след."""
    p = Plate("square", "cutover", palette=PALETTE)
    old, new, bot = (250, 520, 176), (770, 790, 272), 58
    p.disc(*old, None, line=MAIN, dash="dash")
    p.disc(*new, MAIN)
    p.disc(old[0], old[1], bot, None, line=MAIN, dash="dash")
    p.disc(new[0], new[1], bot, PAPER)
    p.arrow(old[0] + bot + 8, old[1] - 12, new[0] - bot - 8, new[1] - 10, -0.26, ink=ACCENT)
    p.text(old[0], old[1] + 122, "старая база", 2.4, anchor="middle")
    p.text(new[0], new[1] + 9, "бот", 2.4, MAIN, 500, "middle")
    p.text(new[0], new[1] + 146, "новая база", 2.8, PAPER, anchor="middle")
    p.lead(p.margin, 130, "Переезд.", ["Бота переводят на новую базу за одно", "окно простоя: 5–10 минут."])
    p.save(path, "Малый круг ушёл из пустого штрихового круга в большой плотный, на старом месте остался его контур")


def glass(path):
    """Прозрачное: взгляд проходит сквозь плоскость до кнопки, рука упирается в неё."""
    p = Plate("wide", "glass", MAIN, PALETTE, tone="flat")
    agent = (230, 590, 112)
    pane = [(720, 262), (820, 200), (820, 830), (720, 892)]
    win = (1250, 540, 520, 430)
    left, top = win[0] - win[2] / 2, win[1] - win[3] / 2
    p.rect(*win, None, line=MAIN)
    p.rect(win[0], top + 26, win[2], 52, MAIN)
    button = (left + 340, top + 270)
    p.rect(*button, 190, 74, ACCENT)
    p.arrow(agent[0] + 104, agent[1] - 40, button[0] - 100, button[1], ink=MAIN, dash="dash")
    p.poly(pane, MAIN, 18, line=MAIN)
    p.arrow(agent[0] + 106, agent[1] + 36, 720, 652, ink=ACCENT)
    p.disc(*agent, MAIN)
    p.text(392, 500, "видит", 2.2)
    p.text(392, 712, "нажать не может", 2.2)
    p.lead(p.margin, 110, "Просмотр.", ["Computer use даёт агенту", "в браузере только просмотр."])
    p.save(path, "Круг смотрит сквозь прозрачную плоскость на кнопку в окне, вторая стрелка упирается в плоскость")


def house(path):
    """Базовая структура: дом собран из одного кубика, последний идёт на пустое место."""
    p = Plate("page", "house", palette=PALETTE)
    a, x0, y0 = 70, 540, 820
    c = a * math.cos(math.radians(30))
    at = lambda i, j, k: (x0 + (i - j) * c, y0 + (i + j) * a / 2 - k * a)
    faces = lambda top, left, right: dict(top=(top, 100), left=(left, 100), right=(right, 100), line=p.inks[PAPER])
    wall = faces(mix(p.inks[ACCENT], p.inks[PAPER], 0.55), p.inks[ACCENT], mix(p.inks[ACCENT], p.inks[MAIN], 0.5))
    if len(p.spots) > 1:
        wall = faces(p.spots[1], p.spots[0], p.spots[2])
    door = faces(mix(p.inks[MAIN], p.inks[PAPER], 0.3), p.inks[MAIN], p.inks[MAIN])
    blocks = [(i, j, k) for k in range(3) for i in range(4) for j in range(4)]
    blocks += [(i, j, 3) for i in range(1, 3) for j in range(4)]
    missing = (2, 3, 3)
    for i, j, k in sorted(blocks, key=lambda b: (b[0] + b[1] + b[2], b[2])):
        if (i, j, k) != missing:
            p.cube(*at(i, j, k), a, **(door if (i, j, k) in ((1, 3, 0), (1, 3, 1)) else wall))
    x, y = at(*missing)
    p.wirecube(x, y, a)
    p.cube(x, y - 330, a, **door)
    p.arrow(x, y - 330 + a + 14, x, y - a - 12, ink=MAIN, dash="dash")
    p.lead(p.margin, 130, "Дом роботов.", ["Детская игра: Валли, Ева, М-О и Капитан", "строят домики."])
    p.save(path, "Изометрический дом из одинаковых кубиков, один кубик опускается на пустое место в крыше")


def leak(path):
    """Проникновение: секрет прошёл узкую щель в плите, за ней расходится веером копий."""
    p = Plate("page", "leak", palette=PALETTE)
    x, slab = 540, 600
    p.rect(x, slab / 2, p.w + 40, slab, MAIN)
    p.rect(x, 384, 230, 70, None, line=PAPER)
    p.text(x, 394, "настройки", 2.6, PAPER, anchor="middle")
    p.line(x, 419, x, slab - 30, PAPER, "dash")
    p.disc(x, slab, 26, ACCENT)
    p.scatter(
        0, slab + 24, p.w, p.h - slab + 60, 120, 6, 15, ACCENT, gap=9,
        inside=lambda cx, cy: abs(cx - x) < (cy - slab) * 0.74 + 8,
        size=lambda cx, cy: 5 + (cy - slab) * 0.018,
    )
    p.lead(p.margin, 130, "Утечка.", ["Пароль попал в git через файл настроек", "агента и остался в чужом форке."], ink=PAPER, accent=ACCENT)
    p.save(path, "Точка проходит узкую щель в сплошной плите, под плитой расходится веер таких же точек")


SHEETS = (
    limits, environment, race, fomo, ban, sprint, review, mentors, metadata, launch,
    portrait, lead, funnel, identity, component, proxy, cutover, glass, house, leak,
)

if __name__ == "__main__":
    folder = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    names = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] else None
    PALETTE = sys.argv[3] if len(sys.argv) > 3 else PALETTE
    for number, build in enumerate(SHEETS, 1):
        if not names or build.__name__ in names:
            build(folder / f"{number:02d}-{build.__name__}.svg")
