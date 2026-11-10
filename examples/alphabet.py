#!/usr/bin/env python3
"""Азбука: четыре листа, по фигуре на термин. Заодно рецепт каждого термина. Запуск: alphabet.py папка [палитра]."""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from vg import MAIN, PALETTES, PAPER, Plate, box, circle, mix


def grid(p, xs, ys, dash=None):
    for x in xs:
        p.line(x, ys[0], x, ys[-1], MAIN, dash)
    for y in ys:
        p.line(xs[0], y, xs[-1], y, MAIN, dash)


def point(p):
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        p.line(50 + 8 * dx, 38 + 8 * dy, 50 + 26 * dx, 38 + 26 * dy)


def surface(p):
    for i in range(9):
        p.line(14, 26 + 3 * i, 66, 8 + 3 * i)
        p.line(14, 26 + 3 * i, 66, 44 + 3 * i)
    p.plane(50, 38, 34, MAIN, 30)


def dimensions(p):
    p.wirecube(50, 38, 27, MAIN)
    for a in range(0, 360, 60):
        p.dot(50 + 27 * math.sin(math.radians(a)), 38 - 27 * math.cos(math.radians(a)), 2.4)


def informal(p):
    grid_points = [[(16 + 22 * c + (7 * math.sin(3 * c + 2 * r)), 8 + 20 * r + 5 * math.cos(2 * c + 3 * r)) for c in range(4)] for r in range(4)]
    for row in grid_points:
        for a, b in zip(row, row[1:]):
            p.line(*a, *b)
    for column in zip(*grid_points):
        for a, b in zip(column, column[1:]):
            p.line(*a, *b)


def similar(p):
    rows = [[(16 + 22 * c + 1.8 * math.sin(5 * c + r), 8 + 20 * r + 1.8 * math.cos(4 * c + r)) for c in range(4)] for r in range(4)]
    for row in rows:
        for a, b in zip(row, row[1:]):
            p.line(*a, *b)
    for column in zip(*rows):
        for a, b in zip(column, column[1:]):
            p.line(*a, *b)


def skeleton(p):
    p.line(10, 4, 90, 72, MAIN, "dash")
    p.line(90, 4, 10, 72, MAIN, "dash")
    for r in (6, 12, 18):
        p.disc(50, 38, r, None, line=MAIN, dash="dot")
    for x, y in ((10, 4), (90, 4), (10, 72), (90, 72)):
        p.disc(x, y, 8, None, line=MAIN, dash="dot")


def spiral(p):
    points = [(50 + 1.0 * t * math.cos(t / 3.2), 38 + 1.0 * t * math.sin(t / 3.2)) for t in range(0, 34)]
    for a, b in zip(points, points[1:]):
        p.line(*a, *b)


def basic(p):
    grid(p, (14, 38, 62, 86), (2, 26, 50, 74))
    for i in range(9):
        p.text(18 + 24 * (i % 3), 14 + 24 * (i // 3), str(i + 1), 1.45, MAIN)


def tone(p):
    for x, k in ((22, 0), (50, 0.35), (78, 0.7)):
        p.disc(x, 38, 12, mix(p.inks[MAIN], "#000000", k))


def active(p):
    for i, x in enumerate((26, 50, 74)):
        for j, y in enumerate((14, 38, 62)):
            shift = j * 5
            p.subtract(circle(x, y + shift, 9), box(x, y + 12 + 12, 24, 12), MAIN)
    grid(p, (14, 38, 62, 86), (2, 26, 50, 74))


def texture(p):
    for x, step in ((22, 6), (50, 4), (78, 2.8)):
        with p.clip(circle(x, 38, 12)):
            for k in range(-5, 6):
                p.line(x - 12, 38 + k * step, x + 12, 38 + k * step, MAIN, weight=3)
                p.line(x + k * step, 26, x + k * step, 50, MAIN, weight=3)


def sphere(p):
    p.fade(circle(50, 38, 26), 24, 12, 52, 52, 100, 0)
    p.disc(50, 38, 26, None, line=MAIN)
    p.ellipse(50, 38, 26, 8, None, line=MAIN)
    p.ellipse(50, 38, 10, 26, None, line=MAIN)
    p.dot(24, 38, 2.6)


def mirror(p):
    p.line(50, 8, 50, 70, MAIN, "dash")
    half = "M{x} 22a16 16 0 0 {s} 0 32Z"
    p.path(half.format(x=44, s=0), MAIN)
    p.path(half.format(x=56, s=1), MAIN, 45)


def rotation(p):
    p.disc(50, 38, 28, None, line=MAIN, dash="dot")
    p.dot(50, 38, 2.4)
    p.rect(30, 18, 11, 15, MAIN, angle=-45)
    p.arrow(38, 14, 74, 22, 0.28)


def spin(p):
    p.disc(50, 38, 10, MAIN)
    p.orbit(50, 38, 19)


def repeat_form(p):
    for x, y, w, h, a, t in ((26, 18, 16, 22, 12, 100), (68, 16, 9, 6, -14, 100), (24, 56, 22, 16, 40, 45), (68, 54, 18, 26, -36, 100)):
        p.rect(x, y, w, h, MAIN, t, angle=a)


def repeat_tone(p):
    p.disc(28, 22, 13, MAIN, 45)
    p.rect(70, 22, 22, 22, MAIN, 45, angle=20)
    p.ellipse(28, 56, 16, 9, MAIN, 45, angle=-25)
    p.poly([(70, 44), (84, 68), (56, 68)], MAIN, 45)


def repeat_direction(p):
    for x, y, r in ((26, 22, 13), (70, 18, 9), (28, 58, 9), (70, 54, 15)):
        p.ellipse(x, y, r, r * 0.42, MAIN, angle=-30)


def scale(p):
    p.disc(58, 30, 30, MAIN, 30)
    p.disc(34, 52, 9, MAIN)
    p.arrow(34, 52, 76, 12)


def move(p):
    p.disc(30, 38, 13, MAIN, 30)
    p.disc(62, 38, 13, MAIN)
    p.arrow(34, 38, 60, 38, ink=PAPER)


def path_(p):
    p.disc(24, 58, 8, MAIN, 40)
    p.arrow(28, 52, 70, 18, 0.25, dash="dash")
    p.disc(78, 14, 7, MAIN)


def superordinate(p):
    p.line(10, 60, 90, 16, MAIN, "dash")
    p.rect(30, 49, 14, 19, MAIN, angle=-28)
    p.rect(66, 29, 14, 19, MAIN, angle=-28)
    p.rect(32, 44, 13, 17, MAIN, 45, angle=30, through=True)
    p.rect(70, 26, 13, 17, MAIN, 45, angle=62, through=True)


def displacement(p):
    p.ellipse(50, 38, 26, 15, MAIN, angle=-30)


def angle(p):
    p.ellipse(53, 43.5, 13, 26, MAIN, 40, angle=30)
    p.line(40, 66, 40, 6)
    p.line(40, 66, 69, 16)
    p.arrow(40, 30, 58, 35, -0.12)
    p.dot(40, 66, 2.2)


def attract(p):
    p.disc(38, 38, 12, MAIN)
    p.disc(63, 38, 12, MAIN)


def symmetry(p):
    p.line(50, 6, 50, 72)
    for y in (26, 50):
        p.disc(36, y, 10, MAIN)
        p.disc(64, y, 10, MAIN, 45)


def balance(p):
    p.line(10, 60, 90, 60)
    p.dot(46, 60, 2)
    p.disc(30, 44, 16, MAIN)
    p.disc(84, 54, 6, MAIN)


def group(p):
    p.line(20, 38, 80, 38)
    for x in (20, 50, 80):
        p.disc(x, 38, 11, MAIN)


def coarse(p):
    with p.clip(box(50, 38, 88, 76)):
        for c in range(4):
            for r in range(4):
                p.disc(14 + 24 * c, 2 + 24 * r, 10, MAIN)


def diffuse(p):
    p.diffusion(10, 4, 80, 68, 8, 1.2, 4.2, ink=MAIN)


def direction(p):
    with p.at(50, 38, 1, -18):
        grid(p, (-36, -18, 0, 18, 36), (-30, -10, 10, 30))
        for x, y in ((-27, -20), (-9, -20), (9, 0), (27, 0), (-9, 20), (9, 20)):
            p.disc(x, y, 8, MAIN)


def position(p):
    p.lattice(60, 46, 3, 3, 12, 6, MAIN)
    p.rules(())
    for x in (60, 72, 84):
        p.line(x, 0, x, 76)
    for y in (46, 58, 70):
        p.line(8, y, 92, y)


def weight(p):
    with p.clip(box(50, 38, 92, 76)):
        p.mass(4, 62, 9, 3, 11.5, MAIN)


def dominance(p):
    p.scatter(6, 4, 66, 68, 13, 5, 13, MAIN)
    p.disc(88, 12, 3, MAIN)


def neutral(p):
    p.lattice(22, 12, 3, 3, 26, 11, MAIN, 30)


def depth(p):
    p.disc(40, 38, 22, MAIN, 70)
    p.disc(64, 38, 18, MAIN, 30, through=True)


def parallel(p):
    p.rect(50, 26, 60, 15, MAIN)
    p.rect(50, 50, 60, 15, MAIN)


def tilt(p):
    p.rect(50, 38, 56, 13, MAIN, angle=-45)


def negative(p):
    p.rect(50, 21, 100, 42, MAIN)
    p.disc(50, 21, 12, PAPER)
    p.disc(50, 58, 12, MAIN)


def transparent(p):
    p.rect(50, 21, 100, 42, MAIN, 45)
    p.disc(34, 42, 15, MAIN, 30)
    p.disc(66, 42, 15, MAIN)


def tangent(p):
    p.disc(38, 38, 12, MAIN)
    p.disc(62, 38, 12, MAIN)


def overlap(p):
    p.disc(50, 26, 15, MAIN, 70)
    p.disc(50, 44, 15, MAIN, 40, through=True)


def compound(p):
    p.path(circle(50, 26, 15) + circle(50, 46, 15), MAIN)


def subtract(p):
    p.subtract(circle(50, 44, 18), circle(50, 22, 18), MAIN)
    p.disc(50, 22, 18, None, line=MAIN, dash="dash")


def pierced(p):
    p.pierce(46, 36, 54, front=30, plate=MAIN, body=(MAIN, 20), cap=(MAIN, 50))


def extruded(p):
    p.pierce(58, 38, 50, cloud=25, plate=MAIN)


def influenced(p):
    p.influence((42, 30, 22), (64, 50, 18), ink=MAIN, tint=60)
    p.disc(64, 50, 18, MAIN)


def modify(p):
    p.rect(50, 38, 40, 40, MAIN, rounded=9)
    p.rect(50, 38, 40, 40, None, line=MAIN, dash="dot")


def variation(p):
    for i, (x, k) in enumerate(((17, 1), (39, 1.25), (64, 1.55))):
        p.ellipse(x, 22, 9 * k, 9, MAIN, 45, angle=-12 * i)
        p.ellipse(x, 52, 9 * k, 9, MAIN, angle=-22 * i)


SHEETS = [
    ("Абстрактное", 4, [
        (point, "Точка"),
        (lambda p: p.line(50, 2, 50, 74), "Линия"),
        (surface, "Плоскость"),
        (lambda p: p.wirecube(50, 38, 30, MAIN), "Объём"),
        (dimensions, "Измерения"),
        (lambda p: (p.rect(50, 38, 76, 76, None, line=MAIN), p.line(12, 0, 88, 76), p.line(88, 0, 12, 76)), "Формат"),
        (lambda p: grid(p, (14, 38, 62, 86), (2, 26, 50, 74)), "Формальная\nструктура"),
        (lambda p: grid(p, (10, 13, 18, 26, 38, 54, 74, 92), (2, 26, 50, 74)), "Градация"),
        (lambda p: [p.disc(50, 38, r, None, line=MAIN) for r in (5, 11, 18, 26, 35)], "Концентрическое\nизлучение"),
        (lambda p: [p.line(50 - 36 * math.cos(a * math.pi / 6), 38 - 36 * math.sin(a * math.pi / 6), 50 + 36 * math.cos(a * math.pi / 6), 38 + 36 * math.sin(a * math.pi / 6)) for a in range(6)], "Центробежное\nизлучение"),
        (informal, "Неформальная\nструктура"),
        (similar, "Распределение\nна глаз"),
        (lambda p: grid(p, (14, 38, 62, 86), (2, 26, 50, 74), "dash"), "Невидимая\nструктура"),
        (skeleton, "Структурный\nскелет"),
        (spiral, "Спираль"),
        (basic, "Базовая\nструктура"),
    ]),
    ("Конкретное", 3, [
        (lambda p: p.blob(50, 38, 24, "organic", MAIN), "Форма"),
        (lambda p: (p.disc(48, 42, 30, MAIN), p.disc(86, 10, 3, MAIN)), "Размер"),
        (lambda p: p.disc(50, 38, 15, MAIN), "Цвет"),
        (tone, "Тон"),
        (lambda p: [p.disc(x, 38, 12, MAIN, t) for x, t in ((22, 100), (50, 65), (78, 35))], "Насыщенность"),
        (sphere, "Цветовая сфера"),
        (lambda p: grid(p, (14, 38, 62, 86), (2, 26, 50, 74)), "Видимая\nструктура"),
        (active, "Активная\nструктура"),
        (texture, "Фактура"),
    ]),
    ("Действия", 4, [
        (lambda p: [p.disc(x, y, 11, MAIN, t) for x, y, t in ((36, 24, 100), (64, 24, 100), (36, 52, 40), (64, 52, 40))], "Повтор"),
        (repeat_form, "Повтор формы"),
        (repeat_tone, "Повтор цвета"),
        (repeat_direction, "Повтор\nнаправления"),
        (lambda p: [p.disc(x, 38, 7, MAIN) for x in (14, 32, 50, 68, 86)], "Частота"),
        (lambda p: [p.disc(x, 38, 7, MAIN) for x in (10, 25, 46, 61, 82, 97)], "Ритм"),
        (mirror, "Отражение"),
        (rotation, "Вращение"),
        (spin, "Вращение\nвокруг оси"),
        (scale, "Масштаб"),
        (move, "Движение"),
        (path_, "Траектория"),
        (lambda p: p.arrow(24, 60, 76, 14), "Направление"),
        (superordinate, "Главное\nи подчинённое"),
        (displacement, "Смещение"),
        (angle, "Угол смещения"),
    ]),
    ("Отношения", 5, [
        (attract, "Притяжение"),
        (symmetry, "Симметрия"),
        (balance, "Равновесие"),
        (group, "Группа"),
        (coarse, "Крупное"),
        (diffuse, "Рассеяние"),
        (direction, "Направление\nструктуры"),
        (position, "Положение"),
        (weight, "Вес"),
        (dominance, "Доминирование"),
        (neutral, "Нейтральность"),
        (depth, "Фон"),
        (parallel, "Параллель"),
        (tilt, "Угол"),
        (negative, "Негатив"),
        (transparent, "Прозрачное"),
        (tangent, "Касание"),
        (overlap, "Наложение"),
        (compound, "Соединение"),
        (subtract, "Вычитание"),
        (pierced, "Проникновение"),
        (extruded, "Выдавливание"),
        (influenced, "Влияние"),
        (modify, "Модификация"),
        (variation, "Вариация"),
    ]),
]


def build(out, palette="cobalt"):
    paper, main, accent = PALETTES[palette]
    number = 0
    for title, cols, cells in SHEETS:
        rows = math.ceil(len(cells) / cols)
        p = Plate("page", title, palette=(paper, accent, accent))
        left, cell = 8 * p.u, (p.w - 16 * p.u) / cols
        top = 19 * p.u
        p.h = int(top + cell * rows + 8 * p.u)
        p.title(left, 13.5 * p.u, title)
        for i, (draw, label) in enumerate(cells):
            number += 1
            x, y = left + cell * (i % cols), top + cell * (i // cols)
            p.rect(x + cell / 2, y + cell / 2, cell, cell, None, line=MAIN)
            with p.at(x, y, cell / 100):
                with p.clip(box(50, 50, 100, 100)):
                    draw(p)
                lines = label.split("\n")
                for k, s in enumerate(lines):
                    base = 96 - (len(lines) - 1 - k) * 8
                    p.text(4 + 2.7 * p.u, base, s, 1.45, main)
                p.text(4, 96 - (len(lines) - 1) * 8, str(number), 1.45, MAIN)
        p.save(pathlib.Path(out) / f"alphabet-{number:02d}.svg", f"Азбука: {title}")


if __name__ == "__main__":
    build(*(sys.argv[1:] or ["."]))
