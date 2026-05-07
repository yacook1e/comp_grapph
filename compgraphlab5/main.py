import tkinter as tk

# --- Конфигурация ---
WIDTH, HEIGHT = 600, 400
PIXEL_SIZE = 6  # Уменьшил пиксель для большей гладкости
COLOR_BG = "white"
COLOR_FILLED = "#4A90E2"
COLOR_PARTITION = "green"
COLOR_EDGE = "black"

# Координаты вершин многоугольника
POLYGON = [
    (100, 100),
    (250, 50),
    (350, 150),
    (450, 100),
    (500, 250),
    (300, 350),
    (150, 250)
]

# Координата перегородки (x)
PARTITION_X = 300


class XOR2App:
    def __init__(self, root):
        self.root = root
        self.root.title("Алгоритм XOR-2 с перегородкой (Final)")
        self.root.geometry(f"{WIDTH}x{HEIGHT + 100}")

        self.rows = HEIGHT // PIXEL_SIZE
        self.cols = WIDTH // PIXEL_SIZE
        self.grid = [[False for _ in range(self.cols)] for _ in range(self.rows)]

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=COLOR_BG)
        self.canvas.pack(pady=10)

        frame = tk.Frame(root)
        frame.pack(fill="x")

        self.btn_step = tk.Button(frame, text="Следующее ребро", command=self.next_step)
        self.btn_step.pack(side="left", padx=20)

        self.btn_auto = tk.Button(frame, text="Авто", command=self.auto_play)
        self.btn_auto.pack(side="left", padx=5)

        self.btn_reset = tk.Button(frame, text="Сброс", command=self.reset)
        self.btn_reset.pack(side="left", padx=5)

        self.label = tk.Label(frame, text="Готово")
        self.label.pack(side="right", padx=20)

        self.after_id = None
        self.current_edge_idx = 0
        self.edges = []

        for i in range(len(POLYGON)):
            p1 = POLYGON[i]
            p2 = POLYGON[(i + 1) % len(POLYGON)]
            self.edges.append((p1, p2))

        self.draw_partition_line()
        self.draw_polygon_outline()

    def reset(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.canvas.delete("all")
        self.grid = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_edge_idx = 0
        self.draw_partition_line()
        self.draw_polygon_outline()
        self.label.config(text="Сброс выполнен")

    def auto_play(self):
        self.next_step()
        if self.current_edge_idx < len(self.edges):
            self.after_id = self.root.after(100, self.auto_play)

    def flip_pixel(self, x, y):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.grid[y][x] = not self.grid[y][x]
            color = COLOR_FILLED if self.grid[y][x] else COLOR_BG

            self.canvas.create_rectangle(
                x * PIXEL_SIZE, y * PIXEL_SIZE,
                (x + 1) * PIXEL_SIZE, (y + 1) * PIXEL_SIZE,
                fill=color, outline=color
            )
            # Важно: поднимаем контур наверх, чтобы он не перекрывался пикселями
            self.canvas.tag_raise("outline")

    def draw_partition_line(self):
        x = PARTITION_X
        self.canvas.create_line(x, 0, x, HEIGHT, fill=COLOR_PARTITION, dash=(4, 4))
        self.canvas.create_text(x + 15, 15, text="Перегородка", fill=COLOR_PARTITION, anchor="nw")

    def draw_polygon_outline(self):
        points = [coord for vertex in POLYGON for coord in vertex]
        # Рисуем контур жирнее (width=2), чтобы было видно
        self.canvas.create_polygon(points, outline=COLOR_EDGE, width=2, fill="", tags="outline")

    def next_step(self):
        if self.current_edge_idx >= len(self.edges):
            self.label.config(text="Готово!")
            return

        p1, p2 = self.edges[self.current_edge_idx]
        x1, y1 = p1
        x2, y2 = p2

        if y1 == y2:
            self.current_edge_idx += 1
            self.label.config(text=f"Пропуск горизонтального ребра")
            return

        if y1 < y2:
            y_start, y_end = y1, y2
        else:
            y_start, y_end = y2, y1

        y_start_grid = int(y_start / PIXEL_SIZE)
        y_end_grid = int(y_end / PIXEL_SIZE)

        dx = x2 - x1
        dy = y2 - y1

        for y_pixel in range(y_start_grid, y_end_grid):
            real_y = (y_pixel + 0.5) * PIXEL_SIZE

            if dy != 0:
                intersect_x = x1 + dx * (real_y - y1) / dy
            else:
                intersect_x = x1

                # Используем round для более точного попадания в центр пикселя
            x_pixel = int(round(intersect_x / PIXEL_SIZE))

            partition_pixel = int(PARTITION_X / PIXEL_SIZE)

            start_x = min(x_pixel, partition_pixel)
            end_x = max(x_pixel, partition_pixel)

            for x_fill in range(start_x, end_x):
                self.flip_pixel(x_fill, y_pixel)

        self.current_edge_idx += 1
        self.label.config(text=f"Обработано ребро {self.current_edge_idx}/{len(self.edges)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = XOR2App(root)
    root.mainloop()