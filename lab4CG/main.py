"""
Лабораторная работа №4. Алгоритмы отсечения отрезка.

Реализованы:
  1) Алгоритм Цируса — Бека      (отсечение отрезка выпуклым многоугольником)
  2) Алгоритм Сазерленда — Коэна (отсечение отрезка прямоугольником)
  3) Алгоритм средней точки      (отсечение отрезка прямоугольником)

Входные данные читаются из текстовых файлов. Отрисовка — на tkinter.Canvas.
Начало координат — в центре окна программы, ось Y направлена вверх.
"""

import os
import tkinter as tk
from tkinter import messagebox


# =====================================================================
#  Векторная алгебра
# =====================================================================
def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def mult(a, t):
    return (a[0] * t, a[1] * t)


# =====================================================================
#  Чтение входных данных и генерация демо-файлов
# =====================================================================
def read_points_from_txt(path):
    """Читает файл, в каждой строке — пара чисел 'x y' (или 'x,y').
    Пустые строки и строки, начинающиеся с '#', игнорируются."""
    points = []
    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            line = line.replace(',', ' ')
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                x = float(parts[0])
                y = float(parts[1])
            except ValueError:
                continue
            points.append((x, y))
    return points


def read_cyrus_beck_input(path):
    """Все точки, кроме двух последних — вершины многоугольника;
    последние две — концы отрезка."""
    pts = read_points_from_txt(path)
    if len(pts) < 4:
        raise ValueError("Нужно минимум 4 точки (3 вершины + 2 конца отрезка).")
    polygon = pts[:-2]
    line = pts[-2:]
    return polygon, line


def read_rect_input(path):
    """Первые 4 точки — вершины прямоугольника; следующие две — отрезок."""
    pts = read_points_from_txt(path)
    if len(pts) < 6:
        raise ValueError("Нужно 6 точек (4 вершины прямоугольника + 2 конца отрезка).")
    rect = pts[:4]
    line = pts[4:6]
    return rect, line


def ensure_input_files():
    cb_path = 'cyrus_beck_input.txt'
    sc_path = 'sutherland_cohen_input.txt'

    if not os.path.exists(cb_path):
        with open(cb_path, 'w', encoding='utf-8') as f:
            f.write("# Многоугольник-отсекатель (вершины, CCW)\n")
            for p in [(3, 0), (2, 2), (0, 3), (-2, 2),
                      (-3, 0), (-2, -2), (0, -3), (2, -2)]:
                f.write(f"{p[0]} {p[1]}\n")
            f.write("# Отрезок: две последние точки\n")
            f.write("-5 -0.5\n")
            f.write("5 0.5\n")

    if not os.path.exists(sc_path):
        with open(sc_path, 'w', encoding='utf-8') as f:
            f.write("# Прямоугольник-отсекатель (4 вершины)\n")
            for p in [(-3, -2), (3, -2), (3, 2), (-3, 2)]:
                f.write(f"{p[0]} {p[1]}\n")
            f.write("# Отрезок: две последние точки\n")
            f.write("-5 -3\n")
            f.write("5 3\n")


# =====================================================================
#  Алгоритм Цируса — Бека
# =====================================================================
def polygon_area(polygon):
    area = 0.0
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return area / 2.0


def get_edges(polygon):
    """Список рёбер вида (точка_на_ребре, внутренняя_нормаль)."""
    edges = []
    n = len(polygon)
    ccw = polygon_area(polygon) > 0
    for i in range(n):
        a = polygon[i]
        b = polygon[(i + 1) % n]
        v = (b[0] - a[0], b[1] - a[1])
        norm = (-v[1], v[0]) if ccw else (v[1], -v[0])
        edges.append((a, norm))
    return edges


def cyrus_beck(line, edges, eps=1e-9):
    p0, p1 = line[0], line[1]
    d = (p1[0] - p0[0], p1[1] - p0[1])

    t_in, t_out = 0.0, 1.0
    cand_in, cand_out = [], []

    for idx, (pe, nrm) in enumerate(edges):
        num = dot(nrm, sub(p0, pe))
        den = dot(nrm, d)
        if abs(den) < eps:
            if num < -eps:                 # отрезок снаружи этой стороны
                return None, None, False, [], []
        else:
            t = -num / den
            pt = add(p0, mult(d, t))
            if den > 0:                    # входим в полуплоскость
                cand_in.append((t, pt, idx))
                t_in = max(t_in, t)
            else:                          # выходим из полуплоскости
                cand_out.append((t, pt, idx))
                t_out = min(t_out, t)

    if t_in <= t_out + eps:
        return (add(p0, mult(d, t_in)),
                add(p0, mult(d, t_out)),
                True, cand_in, cand_out)
    return None, None, False, cand_in, cand_out


# =====================================================================
#  Алгоритм Сазерленда — Коэна
# =====================================================================
INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8


def compute_code(x, y, xmin, xmax, ymin, ymax):
    code = INSIDE
    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT
    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP
    return code


def sutherland_cohen(x0, y0, x1, y1, xmin, xmax, ymin, ymax):
    while True:
        c0 = compute_code(x0, y0, xmin, xmax, ymin, ymax)
        c1 = compute_code(x1, y1, xmin, xmax, ymin, ymax)

        if c0 == 0 and c1 == 0:
            return (x0, y0), (x1, y1), True
        if (c0 & c1) != 0:
            return None, None, False

        c_out = c0 if c0 != 0 else c1

        if abs(x0 - x1) < 1e-9:
            x = x0
            if c_out & TOP:
                y = ymax
            elif c_out & BOTTOM:
                y = ymin
            else:
                return None, None, False
        else:
            k = (y1 - y0) / (x1 - x0)
            if c_out & TOP:
                x = x0 + (ymax - y0) / k
                y = ymax
            elif c_out & BOTTOM:
                x = x0 + (ymin - y0) / k
                y = ymin
            elif c_out & RIGHT:
                y = y0 + k * (xmax - x0)
                x = xmax
            elif c_out & LEFT:
                y = y0 + k * (xmin - x0)
                x = xmin

        if c_out == c0:
            x0, y0 = x, y
        else:
            x1, y1 = x, y


# =====================================================================
#  Алгоритм средней точки
# =====================================================================
def midpoint_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax,
                  midpoints, eps=1e-6):
    c1 = compute_code(x1, y1, xmin, xmax, ymin, ymax)
    c2 = compute_code(x2, y2, xmin, xmax, ymin, ymax)

    if c1 == 0 and c2 == 0:
        return x1, y1, x2, y2, True
    if (c1 & c2) != 0:
        return None, None, None, None, False
    if abs(x2 - x1) < eps and abs(y2 - y1) < eps:
        if c1 == 0:
            return x1, y1, x1, y1, True
        return None, None, None, None, False

    xm = (x1 + x2) / 2.0
    ym = (y1 + y2) / 2.0
    midpoints.append((xm, ym))

    left = midpoint_clip(x1, y1, xm, ym, xmin, ymin, xmax, ymax,
                         midpoints, eps)
    right = midpoint_clip(xm, ym, x2, y2, xmin, ymin, xmax, ymax,
                          midpoints, eps)

    if left[4] and right[4]:
        return left[0], left[1], right[2], right[3], True
    if left[4]:
        return left
    if right[4]:
        return right
    return None, None, None, None, False


# =====================================================================
#  Приложение на tkinter
# =====================================================================
class ClipApp:
    SCALE = 50          # пикселей на одну единицу
    W, H = 900, 650     # размеры холста

    def __init__(self, root):
        self.root = root
        root.title("Лабораторная работа №4 — Алгоритмы отсечения отрезка")
        root.configure(bg='#f5f5f5')
        root.resizable(False, False)

        top = tk.Frame(root, bg='#f5f5f5')
        top.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)
        tk.Label(top, text="Алгоритм:", font=('Arial', 11, 'bold'),
                 bg='#f5f5f5').pack(side=tk.LEFT, padx=(0, 8))

        for label, cmd in (
            ("Цирус — Бек", self.run_cyrus_beck),
            ("Сазерленд — Коэн", self.run_sutherland_cohen),
            ("Средней точки", self.run_midpoint),
        ):
            tk.Button(top, text=label, command=cmd, width=16,
                      font=('Arial', 10)).pack(side=tk.LEFT, padx=3)

        self.canvas = tk.Canvas(root, width=self.W, height=self.H,
                                bg='white', highlightthickness=1,
                                highlightbackground='#999')
        self.canvas.pack(padx=8, pady=4)

        self.status = tk.Label(root, text="Выберите алгоритм.",
                               anchor='w', bg='#f5f5f5',
                               font=('Arial', 10), wraplength=self.W - 20,
                               justify='left')
        self.status.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=(0, 6))

        self.draw_axes()

    # ------- преобразования координат -------
    def to_screen(self, x, y):
        return self.W / 2 + x * self.SCALE, self.H / 2 - y * self.SCALE

    # ------- статическая сетка и оси -------
    def draw_axes(self):
        xu = int(self.W / (2 * self.SCALE))
        yu = int(self.H / (2 * self.SCALE))
        for i in range(-xu, xu + 1):
            sx, _ = self.to_screen(i, 0)
            self.canvas.create_line(sx, 0, sx, self.H, fill='#eef2f7')
        for j in range(-yu, yu + 1):
            _, sy = self.to_screen(0, j)
            self.canvas.create_line(0, sy, self.W, sy, fill='#eef2f7')

        cx, cy = self.to_screen(0, 0)
        self.canvas.create_line(0, cy, self.W, cy, fill='#888')
        self.canvas.create_line(cx, self.H, cx, 0, fill='#888')
        self.canvas.create_line(self.W - 20, cy, self.W - 4, cy,
                                fill='#444', arrow=tk.LAST, width=1.5)
        self.canvas.create_line(cx, 20, cx, 4,
                                fill='#444', arrow=tk.LAST, width=1.5)
        self.canvas.create_text(self.W - 12, cy - 12, text='x', fill='#333')
        self.canvas.create_text(cx + 12, 12, text='y', fill='#333')
        self.canvas.create_text(cx - 10, cy + 12, text='O', fill='#333')

    def clear(self):
        self.canvas.delete('all')
        self.draw_axes()

    # ------- примитивы -------
    def draw_polygon(self, polygon, fill='#cfe8ff', outline='#1f4e79'):
        pts = []
        for x, y in polygon:
            sx, sy = self.to_screen(x, y)
            pts.extend([sx, sy])
        self.canvas.create_polygon(pts, fill=fill, outline=outline, width=2)

    def draw_segment(self, p1, p2, color='#666', width=2, dash=None):
        x1, y1 = self.to_screen(p1[0], p1[1])
        x2, y2 = self.to_screen(p2[0], p2[1])
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width,
                                dash=dash, capstyle=tk.ROUND)

    def draw_point(self, p, color='red', r=5):
        sx, sy = self.to_screen(p[0], p[1])
        self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r,
                                fill=color, outline='black', width=1)

    def draw_legend(self, items):
        x0 = 15
        y0 = self.H - 15
        for i, (color, label) in enumerate(reversed(items)):
            y = y0 - i * 20
            self.canvas.create_rectangle(x0, y - 7, x0 + 12, y + 5,
                                         fill=color, outline='black')
            self.canvas.create_text(x0 + 18, y - 1, text=label,
                                    anchor='w', font=('Arial', 9))

    # ------- запуск алгоритмов -------
    def run_cyrus_beck(self):
        try:
            polygon, line = read_cyrus_beck_input('cyrus_beck_input.txt')
        except Exception as e:
            messagebox.showerror("Ошибка",
                                 f"Не удалось прочитать файл:\n{e}")
            return

        self.clear()
        self.draw_polygon(polygon)

        p0, p1 = line[0], line[1]
        self.draw_segment(p0, p1, color='#888', width=1, dash=(5, 3))

        edges = get_edges(polygon)
        p_in, p_out, visible, cand_in, cand_out = cyrus_beck(line, edges)

        for _, pt, _ in cand_in:
            self.draw_point(pt, color='#2ca02c', r=5)
        for _, pt, _ in cand_out:
            self.draw_point(pt, color='#ff7f0e', r=5)

        if visible:
            self.draw_segment(p_in, p_out, color='#d62728', width=3)
            self.draw_point(p_in, color='#d62728', r=6)
            self.draw_point(p_out, color='#d62728', r=6)
            self.status.config(
                text=(f"Цирус — Бек: видимый отрезок "
                      f"({p_in[0]:.2f}, {p_in[1]:.2f}) → "
                      f"({p_out[0]:.2f}, {p_out[1]:.2f});  "
                      f"кандидатов на вход {len(cand_in)}, "
                      f"на выход {len(cand_out)}."))
        else:
            self.status.config(
                text=(f"Цирус — Бек: отрезок полностью невидим;  "
                      f"кандидатов на вход {len(cand_in)}, "
                      f"на выход {len(cand_out)}."))

        self.draw_legend([
            ('#888888', 'Исходный отрезок'),
            ('#2ca02c', 'Кандидат на вход'),
            ('#ff7f0e', 'Кандидат на выход'),
            ('#d62728', 'Видимый отрезок'),
        ])

    def run_sutherland_cohen(self):
        try:
            rect, line = read_rect_input('sutherland_cohen_input.txt')
        except Exception as e:
            messagebox.showerror("Ошибка",
                                 f"Не удалось прочитать файл:\n{e}")
            return

        self.clear()
        self.draw_polygon(rect)

        (x0, y0), (x1, y1) = line
        self.draw_segment((x0, y0), (x1, y1),
                          color='#888', width=1, dash=(5, 3))

        xs = [p[0] for p in rect]
        ys = [p[1] for p in rect]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)

        p1, p2, visible = sutherland_cohen(x0, y0, x1, y1,
                                           xmin, xmax, ymin, ymax)

        if visible:
            self.draw_segment(p1, p2, color='#d62728', width=3)
            self.draw_point(p1, color='#d62728', r=6)
            self.draw_point(p2, color='#d62728', r=6)
            self.status.config(
                text=(f"Сазерленд — Коэн: видимый отрезок "
                      f"({p1[0]:.2f}, {p1[1]:.2f}) → "
                      f"({p2[0]:.2f}, {p2[1]:.2f})."))
        else:
            self.status.config(text="Сазерленд — Коэн: отрезок полностью невидим.")

        self.draw_legend([
            ('#888888', 'Исходный отрезок'),
            ('#d62728', 'Видимый отрезок'),
        ])

    def run_midpoint(self):
        try:
            rect, line = read_rect_input('sutherland_cohen_input.txt')
        except Exception as e:
            messagebox.showerror("Ошибка",
                                 f"Не удалось прочитать файл:\n{e}")
            return

        self.clear()
        self.draw_polygon(rect)

        (x0, y0), (x1, y1) = line
        self.draw_segment((x0, y0), (x1, y1),
                          color='#888', width=1, dash=(5, 3))

        xs = [p[0] for p in rect]
        ys = [p[1] for p in rect]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)

        midpoints = []
        res = midpoint_clip(x0, y0, x1, y1, xmin, ymin, xmax, ymax,
                            midpoints)

        for mx, my in midpoints:
            sx, sy = self.to_screen(mx, my)
            self.canvas.create_oval(sx - 4, sy - 4, sx + 4, sy + 4,
                                    fill='#2ca02c', outline='')

        if res[4]:
            p1 = (res[0], res[1])
            p2 = (res[2], res[3])
            self.draw_segment(p1, p2, color='#d62728', width=3)
            self.draw_point(p1, color='#d62728', r=6)
            self.draw_point(p2, color='#d62728', r=6)
            self.status.config(
                text=(f"Средней точки: видимый отрезок "
                      f"({p1[0]:.2f}, {p1[1]:.2f}) → "
                      f"({p2[0]:.2f}, {p2[1]:.2f});  "
                      f"средних точек {len(midpoints)}."))
        else:
            self.status.config(
                text=(f"Средней точки: отрезок полностью невидим;  "
                      f"средних точек {len(midpoints)}."))

        self.draw_legend([
            ('#888888', 'Исходный отрезок'),
            ('#2ca02c', 'Средние точки'),
            ('#d62728', 'Видимый отрезок'),
        ])


def main():
    ensure_input_files()
    root = tk.Tk()
    ClipApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()