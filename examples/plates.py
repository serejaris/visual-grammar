#!/usr/bin/env python3
"""Образцы листов: один термин на лист, у каждого формата своя раскладка. Запуск: plates.py папка [палитра]."""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from vg import ACCENT, MAIN, PAPER, Plate, circle, sector


def context(out, palette):
    """Формат и вес: масса растёт вниз, давит на задачу и выдавливает её за край листа."""
    p = Plate("page", "context", palette=palette)
    pitch, task = 118, (863, 1322, 92)
    p.mass(-22, 8, 11, 6, pitch)
    p.rules(ys=[8 + pitch * r for r in range(0, 6)])
    for c in range(1, 10):
        x = -22 + pitch * c
        p.line(x, 0, x, 730)
        reach = task[1] - (task[2] ** 2 - (x - task[0]) ** 2) ** 0.5 - 8 if abs(x - task[0]) < task[2] else 950
        p.arrow(x, 730, x, reach)
    p.disc(*task, ACCENT)
    p.text(748, 1276, "задача", 1.9, anchor="end")
    p.lead(p.margin, 1030, "Контекст.", ["Агент видит только то, что", "поместилось в окно контекста.", "История растёт и вытесняет задачу."])
    p.save(out / "context.svg", "Масса кругов занимает верх листа, стрелки идут от неё вниз и давят на круг, выдавленный за нижний край")


def subagent(out, palette):
    """Вычитание и движение: от целого отделена часть, она работает в своей рамке, обратно приходит меньше, чем ушло."""
    p = Plate("page", "subagent", ACCENT, palette)
    p.runner("Агенты", "Субагенты")
    x, y, r, start, end = 190, 1010, 400, -62, -22
    p.subtract(circle(x, y, r), sector(x, y, r + 2, start, end), MAIN)
    p.path(sector(x, y, r, start, end), None, line=PAPER, dash="dash")
    left, top, side = 650, 420, 340
    p.rect(left + side / 2, top + side / 2, side, side, None, line=PAPER)
    p.path(sector(left + 28, top + side - 34, r * 0.74, start, end), PAPER)
    p.arrow(486, 660, 636, 560, 0.2, PAPER, "dash")
    p.arrow(760, 776, 454, 806, -0.34, PAPER)
    p.dot(436, 804, 15, PAPER)
    p.lead(p.margin, 170, "Субагент.", ["Решает свою часть задачи", "в отдельном контексте и возвращает", "только результат."])
    p.text(left, top - 20, "отдельный контекст", 1.9)
    p.text(640, 938, "результат", 1.9)
    p.text(64, 1240, "вся задача", 1.9, PAPER)
    p.save(out / "subagent.svg", "От большого круга отделён сектор и лежит в отдельной рамке, обратно к пустому месту идёт маленькая точка")


def skill(out, palette):
    """Выдавливание: бесформенная масса проходит через отверстие и получает его профиль."""
    p = Plate("page", "skill", palette=palette)
    p.runner("Агенты", "Скиллы")
    p.pierce(620, 590, 600, r=150, front=330, cloud=430, cap=(ACCENT, 70))
    p.arrow(66, 214, 214, 330, -0.1, MAIN)
    p.text(66, 196, "Промпт", 1.9)
    p.text(884, 960, "Результат", 1.9)
    p.lead(p.margin, 1120, "Скилл.", ["Задаёт один процесс для разных", "промптов. Ход работы предсказуем."])
    p.save(out / "skill.svg", "Бесформенная масса давит на пластину и выходит из отверстия ровным цилиндром")


def review(out, palette):
    """Влияние: круг отошёл и оставил вмятину, штриховой контур показывает форму до правки."""
    p = Plate("wide", "review", palette=palette)
    author, pressed = (1130, 350, 420), (1420, 770, 300)
    p.influence(author, pressed)
    p.disc(1474, 848, 300, ACCENT)
    with p.clip(circle(*pressed)):
        p.disc(*author, None, line=MAIN, dash="dash")
    p.arrow(1304, 600, 1262, 540, ink=MAIN)
    p.text(880, 320, "Автор", 2.4, PAPER)
    p.text(1310, 830, "Критик", 2.4, PAPER)
    p.lead(p.margin, 170, "Ревью.", ["Второй агент", "проверяет работу,", "и она меняется там,", "где он нашёл дефект."])
    p.save(out / "review.svg", "В большой форме вмятина от круга рядом, штриховой контур показывает, какой форма была до этого")


def variation(out, palette):
    """Вариация: из одной точки выходят запуски, они совпадают в ядре и расходятся по краям."""
    p = Plate("wide", "variation", palette=palette, tone="flat")
    x, y, source = 1124, 470, (330, 660)
    runs = ((430, 300, -14, -18, 8, 148), (396, 326, 10, 16, -12, 164), (446, 284, -28, 6, 16, 180), (408, 316, 4, -8, -18, 196), (428, 296, 20, 20, 8, 212))
    for rx, ry, angle, dx, dy, t in runs:
        p.ellipse(x + dx, y + dy, rx, ry, MAIN, 34, angle=angle, through=True, line=MAIN)
        a, u = math.radians(angle), math.radians(t)
        ex = x + dx + rx * math.cos(u) * math.cos(a) - ry * math.sin(u) * math.sin(a)
        ey = y + dy + rx * math.cos(u) * math.sin(a) + ry * math.sin(u) * math.cos(a)
        p.arrow(*source, ex - 5, ey, ink=ACCENT)
    p.dot(*source, 16)
    p.text(source[0] - 32, source[1] + 10, "промпт", 1.3, anchor="end")
    p.text(x, y + 12, "одно решение", 2.4, PAPER, anchor="middle")
    p.lead(p.margin, 170, "Вариация.", ["Один промпт при", "каждом запуске даёт", "одно и то же решение.", "Детали разные."])
    p.save(out / "variation.svg", "Из одной точки расходятся пять стрелок к пяти наложенным овалам: ядро плотное, края расходятся")


def org(out, palette):
    """Излучение: всё расходится от одного центра, размер круга показывает уровень."""
    p = Plate("page", "org", palette=palette)
    p.runner("Агенты", "Компания")
    p.tree(
        540, 760, 112, "Компания",
        ["Финансы", "Право", "Безопасность", "Контент", "Медиа", "Дизайн", "Ресёрч", "Продажи"],
        reach=340, size=2.3, arrows=True,
    )
    p.lead(p.margin, 170, "Компания.", ["Хранит правила для всех отделов.", "У каждого отдела своя папка и своё дело."])
    p.save(out / "org.svg", "Большой круг в центре, тонкие лучи ведут к восьми кругам поменьше с названиями отделов")


def cover(out, palette):
    """Обложка: поле форм на сплошном цвете, вариация идёт через сетку."""
    p = Plate("square", "cover", ACCENT, palette)
    for c in range(6):
        for r in range(4):
            k = (c + r) / 8
            p.ellipse(120 + 190 * c, 500 + 186 * r, 66 + 44 * k, 66 - 18 * k, MAIN, angle=-52 * k)
    p.title(90, 190, "Азбука", p.on_ground(), 12.5)
    p.title(90, 318, "агента", PAPER, 12.5)
    p.save(out / "cover.svg", "Обложка с названием Азбука агента на сплошной заливке: сетка кругов постепенно вытягивается в наклонные эллипсы")


def balance(out, palette):
    """Равновесие на развороте: мелкие формы на длинном плече держат одну большую."""
    p = Plate("spread", "balance", palette=palette)
    gutter, beam = p.w / 2, 1016
    p.line(gutter, 0, gutter, p.h, ACCENT)
    p.rules(ys=[beam])
    p.disc(gutter + 400, beam - 330, 330, MAIN)
    p.scatter(40, 640, 760, beam - 640, 7, 40, 74, ACCENT, gap=22)
    p.dot(gutter, beam, 16)
    p.lead(p.margin, 190, "Равновесие.", ["Семь мелких форм держат одну", "большую. Чем дальше форма от", "оси, тем больше её вес."])
    p.save(out / "balance.svg", "Разворот: слева семь мелких кругов, справа один большой")


if __name__ == "__main__":
    folder = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    for build in (context, subagent, skill, review, variation, org, cover, balance):
        build(folder, sys.argv[2] if len(sys.argv) > 2 else "mono")
