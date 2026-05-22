import tkinter as tk
from tkinter import messagebox
import math


class ConvexHullVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Выпуклая оболочка")

        self.canvas = tk.Canvas(root, width=1000, height=700, bg='white')
        self.canvas.pack(pady=10)

        self.points = []
        self.gen = None
        self.divider_counter = 0

        self.create_controls()

        self.canvas.bind('<Button-1>', self.add_point)
        self.canvas.bind('<Button-3>', self.clear_canvas)

    def create_controls(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Button(frame, text="Построить", command=self.start_convex_hull,
                  bg='lightgreen', font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=5)

        self.btn_next = tk.Button(frame, text="Следующий шаг", command=self.next_step,
                                  bg='yellow', state=tk.DISABLED, font=('Arial', 11, 'bold'))
        self.btn_next.pack(side=tk.LEFT, padx=5)

        tk.Button(frame, text="Очистить", command=self.clear_all, bg='lightcoral').pack(side=tk.LEFT, padx=5)

    def add_point(self, event):
        x, y = event.x, event.y
        for px, py in self.points:
            if math.hypot(px - x, py - y) < 10: return

        self.points.append((x, y))
        self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill='blue', outline='black', tags="point")
        self.canvas.create_text(x + 8, y - 8, text=str(len(self.points)), font=('Arial', 8), fill='black', tags="point")

    def clear_canvas(self, event=None):
        self.canvas.delete("all")
        self.points = []
        self.btn_next.config(state=tk.DISABLED)
        self.gen = None

    def clear_all(self):
        self.clear_canvas()

    def start_convex_hull(self):
        if len(self.points) < 3:
            messagebox.showwarning("Ошибка", "Нужно минимум 3 точки")
            return

        self.canvas.delete("all")
        for i, (x, y) in enumerate(self.points):
            self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill='blue', outline='black', tags="point")
            self.canvas.create_text(x + 8, y - 8, text=str(i + 1), font=('Arial', 8), fill='black', tags="point")

        sorted_points = sorted(self.points)

        self.gen = self.divide_and_conquer_gen(sorted_points)
        self.btn_next.config(state=tk.NORMAL)
        self.divider_counter = 0

        try:
            next(self.gen)
        except StopIteration:
            self.btn_next.config(state=tk.DISABLED)

    def next_step(self):
        try:
            next(self.gen)
        except StopIteration:
            self.btn_next.config(state=tk.DISABLED)

    def cross_product(self, O, A, B):
        return (A[0] - O[0]) * (B[1] - O[1]) - (A[1] - O[1]) * (B[0] - O[0])

    def get_ccw_hull(self, points):
        if len(points) <= 2: return sorted(points)
        points = sorted(points)
        lower = []
        for p in points:
            while len(lower) >= 2 and self.cross_product(lower[-2], lower[-1], p) > 0:
                lower.pop()
            lower.append(p)
        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and self.cross_product(upper[-2], upper[-1], p) > 0:
                upper.pop()
            upper.append(p)
        return lower[:-1] + upper[:-1]

    def find_upper_tangent(self, lh, rh):
        i = max(range(len(lh)), key=lambda x: lh[x][0])
        j = min(range(len(rh)), key=lambda x: rh[x][0])
        n, m = len(lh), len(rh)
        while True:
            changed = False
            while True:
                ni = (i + 1) % n
                if self.cross_product(rh[j], lh[i], lh[ni]) > 0:
                    i, changed = ni, True
                else:
                    break
            while True:
                pj = (j - 1) % m
                if self.cross_product(lh[i], rh[j], rh[pj]) < 0:
                    j, changed = pj, True
                else:
                    break
            if not changed: break
        return i, j

    def find_lower_tangent(self, lh, rh):
        i = max(range(len(lh)), key=lambda x: lh[x][0])
        j = min(range(len(rh)), key=lambda x: rh[x][0])
        n, m = len(lh), len(rh)
        while True:
            changed = False
            while True:
                pi = (i - 1) % n
                if self.cross_product(rh[j], lh[i], lh[pi]) < 0:
                    i, changed = pi, True
                else:
                    break
            while True:
                nj = (j + 1) % m
                if self.cross_product(lh[i], rh[j], rh[nj]) > 0:
                    j, changed = nj, True
                else:
                    break
            if not changed: break
        return i, j

    def draw_hull(self, hull, color, width):
        if len(hull) < 2: return []
        c = []
        for p in hull: c.extend(p)
        c.extend(hull[0])
        item_id = self.canvas.create_line(*c, fill=color, width=width)
        return [item_id]

    def divide_and_conquer_gen(self, points):
        if len(points) <= 3:
            hull = self.get_ccw_hull(points)
            ids = self.draw_hull(hull, 'blue', 2)
            yield
            return hull, ids

        mid = len(points) // 2
        lp, rp = points[:mid], points[mid:]

        mx = (lp[-1][0] + rp[0][0]) // 2
        div_id = self.canvas.create_line(mx, 0, mx, 700, dash=(5, 5), fill='gray')
        yield

        lh, lh_ids = yield from self.divide_and_conquer_gen(lp)

        rh, rh_ids = yield from self.divide_and_conquer_gen(rp)

        iu, ju = self.find_upper_tangent(lh, rh)
        il, jl = self.find_lower_tangent(lh, rh)

        bridge_ids = [
            self.canvas.create_line(*lh[iu], *rh[ju], fill='red', width=3),
            self.canvas.create_line(*lh[il], *rh[jl], fill='orange', width=3)
        ]
        yield

        merged = []
        curr = iu
        while True:
            merged.append(lh[curr])
            if curr == il: break
            curr = (curr + 1) % len(lh)
        curr = jl
        while True:
            merged.append(rh[curr])
            if curr == ju: break
            curr = (curr + 1) % len(rh)

        merged_ids = self.draw_hull(merged, 'darkgreen', 3)

        for id in lh_ids: self.canvas.delete(id)
        for id in rh_ids: self.canvas.delete(id)
        for id in bridge_ids: self.canvas.delete(id)
        self.canvas.delete(div_id)

        yield

        return merged, merged_ids


def main():
    root = tk.Tk()
    app = ConvexHullVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()