#!/usr/bin/env python3
"""Объяснялки в идеальном цикле: лист из plates.py оживает по той же карте смысла. Запуск: loops.py папка [имя] [палитра]."""
import math
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from motion import Loop, curve, ease, lerp, seam, snap, span, turn
from vg import ACCENT, MAIN, PAPER, Plate, circle, mix, sector

LEAD, LABEL = 4, 2.8  # на кадре текст крупнее, чем на листе: ролик смотрят с телефона


def subagent(palette):
    """Часть уходит в свою рамку, там сжимается в результат, результат возвращается и занимает место."""
    x, y, r, start, end = 190, 1010, 400, -62, -22
    left, top, side = 650, 420, 340
    tip, away = (x, y), (left + 28, top + side - 34)
    leave = ((486, 660), (636, 560), 0.2)
    back = ((770, 780), (436, 804), -0.34)
    mid = math.radians((start + end) / 2)

    def draw(p, t):
        p.lead(p.margin, 170, "Субагент.", ["Решает свою часть задачи", "в отдельном контексте и возвращает", "только результат."], LEAD, weight=500)
        p.rect(left + side / 2, top + side / 2, side, side, None, line=PAPER)
        p.text(left, top - 20, "отдельный контекст", LABEL)
        out, work, ret, fill = span(t, 0.07, 0.25), span(t, 0.27, 0.52), span(t, 0.54, 0.72), span(t, 0.74, 0.88)
        p_main, p_paper = p.inks[MAIN], p.inks[PAPER]
        if out > 0 and fill < 1:
            p.subtract(circle(x, y, r), sector(x, y, r + 2, start, end), MAIN)
        else:
            p.disc(x, y, r)
        p.text(64, 1240, "вся задача", LABEL, PAPER)
        if 0 < out and fill < 1:
            alpha = span(t, 0.07, 0.12) * (1 - span(t, 0.84, 0.88))
            p.path(sector(x, y, r, start, end), None, line=PAPER, dash="dash", alpha=alpha)
        if out > 0 and ret == 0 and work < 1:
            scale = lerp(1, 0.74, out) * lerp(1, 0.14, work)
            center_gap = 0.62 * r * lerp(1, 0.74, out)
            tx, ty = lerp(tip[0], away[0], out), lerp(tip[1], away[1], out)
            cx, cy = tx + center_gap * math.cos(mid), ty + center_gap * math.sin(mid)
            spin = 540 * work
            rr = r * scale
            a = mid + math.radians(spin)
            sx, sy = cx - 0.62 * rr * math.cos(a), cy - 0.62 * rr * math.sin(a)
            p.path(sector(sx, sy, rr, start + spin, end + spin), mix(p_main, p_paper, span(out, 0.55, 0.95)))
        if 0.02 < out < 1:
            p.arrow(*leave[0], *leave[1], leave[2], PAPER, "dash", alpha=math.sin(out * math.pi))
        if 0 < work < 1:
            gap = 0.62 * r * 0.74
            cx, cy = away[0] + gap * math.cos(mid), away[1] + gap * math.sin(mid)
            p.orbit(cx, cy, 124, -90 + 360 * work, 300, PAPER, alpha=math.sin(work * math.pi))
        if work >= 1 and fill < 1:
            if ret > 0:
                p.arrow(*back[0], *back[1], back[2], PAPER, alpha=math.sin(min(ret * 1.05, 1) * math.pi * 0.5) * (1 - fill))
                p.text(640, 948, "результат", LABEL, alpha=min(1, ret * 3) * (1 - fill))
        if 0 < fill < 1:
            with p.clip(circle(back[1][0], back[1][1], 560 * fill)):
                p.path(sector(x, y, r, start - 0.6, end + 0.6), MAIN)
        if work >= 1 and fill < 1:
            gap = 0.62 * r * 0.74
            home = (away[0] + gap * math.cos(mid), away[1] + gap * math.sin(mid))
            dx, dy = curve(home, back[1], -0.46, ret)
            p.dot(dx, dy, 15 * (1 - span(fill, 0.55, 1)), PAPER)

    return Loop(
        "subagent", lambda: Plate("page", "subagent", ACCENT, palette), draw, 8,
        alt="Сектор уходит из круга в отдельную рамку, сжимается в точку, точка возвращается и заполняет пустое место",
    )


LATIN = "'Helvetica Neue', 'Inter Tight', Arial, sans-serif"
CONTEXT = {  # термин, строки лида, подпись задачи, шрифт
    "ru": ("Контекст.", ["Агент видит только", "то, что поместилось в окно", "контекста. История растёт", "и вытесняет задачу."], "задача", LATIN),
    "en": ("Context.", ["An agent sees only", "what fits in the context", "window. History grows", "and pushes the task out."], "task", LATIN),
    "zh": ("上下文。", ["智能体只能看到", "上下文窗口里放得下的内容。", "历史记录不断增长，", "把任务挤了出去。"], "任务", "'PingFang SC', 'Helvetica Neue', sans-serif"),
    "es": ("Contexto.", ["Un agente solo ve", "lo que cabe en la ventana", "de contexto. El historial", "crece y desplaza la tarea."], "tarea", LATIN),
    "hi": ("कॉन्टेक्स्ट।", ["एजेंट सिर्फ़ वही देखता है", "जो कॉन्टेक्स्ट विंडो में", "समा जाए। हिस्ट्री बढ़ती है", "और काम को बाहर धकेल देती है।"], "काम", "'Kohinoor Devanagari', 'Devanagari Sangam MN', sans-serif"),
    "ar": ("السياق.", ["لا يرى الوكيل إلا", "ما تتسع له نافذة السياق.", "يتضخم سجل المحادثة", "ويزيح المهمة خارجها."], "المهمة", "'SF Arabic', 'Geeza Pro', sans-serif"),
    "pt": ("Contexto.", ["Um agente só vê", "o que cabe na janela", "de contexto. O histórico", "cresce e expulsa a tarefa."], "tarefa", LATIN),
    "ja": ("コンテキスト。", ["エージェントが", "見られるのは、コンテキスト", "ウィンドウに収まる分だけ。", "履歴が増え、タスクを押し出す。"], "タスク", "'Hiragino Sans', 'Hiragino Kaku Gothic ProN', sans-serif"),
    "fr": ("Contexte.", ["Un agent ne voit que", "ce qui tient dans la fenêtre", "de contexte. L’historique", "grandit et évince la tâche."], "tâche", LATIN),
}


def context(palette, lang="ru"):
    """Масса толчками растёт вниз, давит на задачу и выталкивает её за край, сжатие возвращает всё на место. Арабская версия зеркальная: текст справа, задача слева."""
    term, lines, label, font = CONTEXT[lang]
    rtl = lang == "ar"
    pitch, x0, y0, r_task, rest = 118, -22, 8, 92, 1130
    table = random.Random("context")
    sizes = {(row, col): table.choice((0.5, 0.66, 0.92)) for row in range(-7, 4) for col in range(11)}

    def draw(p, t):
        pushes = sum(span(t, a, a + 0.1, snap) for a in (0.08, 0.2, 0.32, 0.44))
        shift = pitch * pushes * (1 - span(t, 0.66, 0.9))
        edge = y0 + pitch * 2 + shift
        for (row, col), k in sizes.items():
            p.disc(x0 + col * pitch, y0 + row * pitch + shift, pitch * k)
        for row in range(-7, 3):
            p.line(0, y0 + row * pitch + shift, p.w, y0 + row * pitch + shift)
        task_x = 217 if rtl else 863
        reach = edge + 506
        task_y = max(rest, reach + r_task)
        for col in range(1, 10):
            x = x0 + pitch * col
            p.line(x, 0, x, edge)
            if abs(x - task_x) < r_task:
                tip = task_y - (r_task**2 - (x - task_x) ** 2) ** 0.5 - 8
                p.arrow(x, edge, x, min(tip, reach))
            else:
                p.arrow(x, edge, x, edge + 230)
        p.disc(task_x, task_y, r_task, ACCENT)
        p.text(task_x, task_y + 10, label, LABEL, PAPER, 500, "middle")
        p.lead(p.w - p.margin if rtl else p.margin, 1010, term, lines, LEAD * (0.94 if lang == "ja" else 1))

    return Loop(
        "context" if lang == "ru" else f"context-{lang}", lambda: Plate("page", "context", palette=palette, font=font, rtl=rtl), draw, 8,
        alt="Масса кругов толчками опускается и выдавливает маленький круг за нижний край, потом сжимается обратно",
    )


def skill(palette):
    """Разные массы идут в одно отверстие, с другой стороны выходят одинаковые цилиндры. Конвейер без начала и конца."""
    x, y, size, hole_r, length = 620, 590, 600, 150, 170
    masses = ((11, "cloud", 200), (12, "organic", 185), (13, "random", 170))
    near, far = -1200, 1000

    def draw(p, t):
        ax, ay = 0.92, 0.38
        for i, (seed, kind, radius) in enumerate(masses):
            s = lerp(near, far, turn(t, i / 3))
            if s < 0:
                r = lerp(hole_r * 0.82, radius, ease(-s / 340))
                p.blob(x + ax * s, y + ay * s, r, kind, p.spot(i), 28, seed=seed, turn=s * 0.08, line=MAIN)
        hole, axis = p.pierce(x, y, size, r=hole_r, cap=(ACCENT, 70))
        for i in range(3):
            s = lerp(near, far, turn(t, i / 3))
            if s > 2:
                p.tube(hole, axis, max(0, s - length), s, (p.spot(i), 28), (p.spot(i), 70))
        p.text(66, 196, "разные промпты", LABEL)
        p.text(790, 1040, "один процесс", LABEL)
        p.lead(p.margin, 1130, "Скилл.", ["Задаёт один процесс для разных", "промптов. Ход работы предсказуем."], LEAD)

    return Loop(
        "skill", lambda: Plate("page", "skill", palette=palette), draw, 6,
        alt="Разные бесформенные массы проходят через отверстие в пластине и выходят одинаковыми цилиндрами",
    )


def variation(palette):
    """Запуски один за другим ложатся на одно ядро: решение совпадает, края расходятся."""
    x, y, source = 540, 730, (540, 1216)
    runs = ((372, 262, -14, -16, 8, 62), (344, 284, 10, 14, -10, 78), (388, 248, -28, 6, 14, 92), (354, 276, 4, -8, -14, 106), (372, 258, 20, 18, 8, 122))

    def draw(p, t):
        leave = 1 - span(t, 0.84, 0.95)
        for i, (rx, ry, angle, dx, dy, u) in enumerate(runs):
            start = 0.05 + i * 0.13
            go, show = span(t, start, start + 0.07), span(t, start + 0.06, start + 0.13)
            a, q = math.radians(angle), math.radians(u)
            ex = x + dx + rx * math.cos(q) * math.cos(a) - ry * math.sin(q) * math.sin(a)
            ey = y + dy + rx * math.cos(q) * math.sin(a) + ry * math.sin(q) * math.cos(a)
            if show > 0 and leave > 0:
                scale = lerp(0.93, 1, show)
                p.ellipse(x + dx, y + dy, rx * scale, ry * scale, p.spot(i), 42, angle=angle, through=True, line=MAIN, alpha=show * leave)
            if go > 0 and leave > 0:
                p.arrow(*source, lerp(source[0], ex, go), lerp(source[1], ey, go), ink=ACCENT, alpha=leave)
        label = span(t, 0.34, 0.42) * leave
        if label > 0:
            p.text(x, y + 12, "одно решение", 3.2, PAPER, anchor="middle", alpha=label)
        p.dot(*source, 16, ACCENT)
        p.text(source[0] + 32, source[1] + 10, "промпт", LABEL)
        p.lead(p.margin, 170, "Вариация.", ["Один промпт при каждом", "запуске даёт одно и то же", "решение. Детали разные."], LEAD)

    return Loop(
        "variation", lambda: Plate("page", "variation", palette=palette, tone="flat"), draw, 8,
        alt="Из точки по очереди выходят стрелки, с каждой на листе появляется ещё один овал: ядро плотное, края расходятся",
    )


def review(palette):
    """Критик обходит работу, давит в трёх местах, работа меняется там, где он давил."""
    cx, cy, radius, r_critic, depth, sigma = 540, 866, 300, 92, 84, 25
    stops = (-40, 80, 200)

    def press(t, j):
        """Глубина вмятины j: растёт при нажатии, держится, расправляется, когда критик ушёл дальше."""
        local = turn(t, -j / 3)
        return span(local, 0.14, 0.19) * (1 - span(local, 0.72, 0.94))

    def draw(p, t):
        whole = t * 3
        j = int(whole) % 3
        local = whole - int(whole)
        angle = lerp(stops[j] - 120, stops[j], span(local, 0, 0.3))
        push = span(local, 0.42, 0.56) * (1 - span(local, 0.74, 0.92))
        reach = lerp(radius + r_critic + 40, radius - depth + r_critic, push)
        p.disc(cx, cy, radius - 1.6, None, line=ACCENT, dash="dash")
        points = []
        for degree in range(0, 360, 3):
            r = radius
            for k, stop in enumerate(stops):
                delta = (degree - stop + 180) % 360 - 180
                r -= depth * press(t, k) * math.exp(-((delta / sigma) ** 2))
            a = math.radians(degree)
            points.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        p.contour(points)
        a = math.radians(angle)
        px, py = cx + reach * math.cos(a), cy + reach * math.sin(a)
        p.disc(px, py, r_critic, ACCENT)
        p.text(px, py + 10, "критик", LABEL, PAPER, anchor="middle")
        p.text(cx, cy + 12, "работа", 3.2, PAPER, anchor="middle")
        p.lead(p.margin, 170, "Ревью.", ["Второй агент проверяет", "работу. Она меняется там,", "где он нашёл дефект."], LEAD)

    return Loop(
        "review", lambda: Plate("page", "review", palette=palette), draw, 9,
        alt="Малый круг обходит большой и давит на него в трёх местах, на большом круге появляются и расправляются вмятины",
    )


def org(palette):
    """Правила расходятся из центра: импульс бежит по лучу, отдел принимает его."""
    cx, cy, r_root, r_node, reach = 540, 770, 112, 40, 316
    names = ("Финансы", "Право", "Безопасность", "Контент", "Медиа", "Дизайн", "Ресёрч", "Продажи")

    def draw(p, t):
        for i, name in enumerate(names):
            a = math.radians(22.5 + 45 * i)
            ca, sa = math.cos(a), math.sin(a)
            bx, by = cx + reach * ca, cy + reach * sa
            p.line(cx + r_root * ca, cy + r_root * sa, bx, by)
            local = turn(t, -i / 8)
            run = span(local, 0, 0.2)
            swell = math.sin(span(local, 0.17, 0.36) * math.pi)
            if 0 < run < 1:
                d = lerp(r_root, reach - r_node, run)
                p.dot(cx + d * ca, cy + d * sa, 12, p.spot(i))
            p.disc(bx, by, r_node * (1 + 0.3 * swell), p.spot(i))
            right = ca >= 0
            gap = (r_node * 1.3 + 14) * (1 if right else -1)
            p.text(bx + gap, by + 10, name, LABEL, anchor="start" if right else "end")
        p.disc(cx, cy, r_root, ACCENT)
        p.text(cx, cy + 15, "Компания", 4, PAPER, 700, "middle")
        p.lead(p.margin, 170, "Компания.", ["Хранит правила для всех", "отделов. У каждого отдела", "своя папка и своё дело."], LEAD)

    return Loop(
        "org", lambda: Plate("page", "org", palette=palette), draw, 6,
        alt="Из центрального круга по лучам по очереди бегут точки, каждый отдел принимает свою",
    )


LOOPS = {"subagent": subagent, "context": context, "skill": skill, "variation": variation, "review": review, "org": org}
LOCALES = {f"context-{lang}": lambda palette, lang=lang: context(palette, lang) for lang in CONTEXT if lang != "ru"}


if __name__ == "__main__":
    folder = pathlib.Path(sys.argv[1])
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else list(LOOPS)
    palette = sys.argv[3] if len(sys.argv) > 3 else "brand"
    for name in names:
        loop = (LOOPS | LOCALES)[name](palette)
        out = loop.render(folder / "project" / name, folder / f"{name}.mp4")
        join, step = seam(out)
        print(f"{'✓' if join <= step else '✗'} {name}: стык {join:.5f}, обычный шаг {step:.5f}, {out}")
