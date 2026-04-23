import tkinter as tk

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MIN_COORD = -20
MAX_COORD = 20
RANGE_SIZE = MAX_COORD - MIN_COORD

CELL_SIZE = min(WINDOW_WIDTH // RANGE_SIZE, WINDOW_HEIGHT // RANGE_SIZE)
CENTER_X = WINDOW_WIDTH // 2
CENTER_Y = WINDOW_HEIGHT // 2

COLORS = {
    "bg": "white",
    "grid": "lightgray",
    "bresenham": "blue",
    "standard": "red"
}

def draw_grid(canvas):
    left = CENTER_X + MIN_COORD * CELL_SIZE
    right = CENTER_X + MAX_COORD * CELL_SIZE
    top = CENTER_Y - MAX_COORD * CELL_SIZE
    bottom = CENTER_Y - MIN_COORD * CELL_SIZE

    for x in range(MIN_COORD, MAX_COORD + 1):
        px = CENTER_X + x * CELL_SIZE
        if left <= px <= right:
            canvas.create_line(px, top, px, bottom, fill=COLORS["grid"])

    for y in range(MIN_COORD, MAX_COORD + 1):
        py = CENTER_Y - y * CELL_SIZE
        if top <= py <= bottom:
            canvas.create_line(left, py, right, py, fill=COLORS["grid"])

def plot_pixel(canvas, x, y, color):
    px = CENTER_X + x * CELL_SIZE
    py = CENTER_Y - y * CELL_SIZE
    r = 3
    if (px - r < 0) or (px + r > WINDOW_WIDTH) or (py - r < 0) or (py + r > WINDOW_HEIGHT):
        return
    canvas.create_oval(px - r, py - r, px + r, py + r, fill=color, outline=color)


def bresenham_line(x1, y1, x2, y2, plot_func):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    x, y = x1, y1
    if dx >= dy:
        d = 2 * dy - dx
        while True:
            plot_func(x, y)
            if x == x2 and y == y2:
                break
            if d >= 0:
                y += sy
                d -= 2 * dx
            x += sx
            d += 2 * dy
    else:
        d = 2 * dx - dy
        while True:
            plot_func(x, y)
            if x == x2 and y == y2:
                break
            if d >= 0:
                x += sx
                d -= 2 * dy
            y += sy
            d += 2 * dx

def bresenham_circle(xc, yc, r, plot_func):
    x = 0
    y = r
    d = 1 - r
    while x <= y:
        plot_func(xc + x, yc + y)
        plot_func(xc - x, yc + y)
        plot_func(xc + x, yc - y)
        plot_func(xc - x, yc - y)
        plot_func(xc + y, yc + x)
        plot_func(xc - y, yc + x)
        plot_func(xc + y, yc - x)
        plot_func(xc - y, yc - x)
        if d < 0:
            d += 2 * x + 3
        else:
            y -= 1
            d += 2 * (x - y) + 5
        x += 1

def clear_canvas(canvas):
    canvas.delete("all")
    draw_grid(canvas)

def draw_line(canvas, x1, y1, x2, y2):
    clear_canvas(canvas)
    bresenham_line(x1, y1, x2, y2,
                   lambda x, y: plot_pixel(canvas, x, y, COLORS["bresenham"]))
    start_x = CENTER_X + x1 * CELL_SIZE
    start_y = CENTER_Y - y1 * CELL_SIZE
    end_x = CENTER_X + x2 * CELL_SIZE
    end_y = CENTER_Y - y2 * CELL_SIZE
    canvas.create_line(start_x, start_y, end_x, end_y,
                       fill=COLORS["standard"], width=2)

def draw_circle(canvas, cx, cy, r):
    clear_canvas(canvas)
    bresenham_circle(cx, cy, r,
                     lambda x, y: plot_pixel(canvas, x, y, COLORS["bresenham"]))
    center_x = CENTER_X + cx * CELL_SIZE
    center_y = CENTER_Y - cy * CELL_SIZE
    radius_pixel = r * CELL_SIZE
    canvas.create_oval(center_x - radius_pixel, center_y - radius_pixel,
                       center_x + radius_pixel, center_y + radius_pixel,
                       outline=COLORS["standard"], width=2, fill="")

def input_int(prompt):
    while True:
        try:
            val = int(input(prompt))
            return val
        except ValueError:
            print("Ошибка: введите целое число")

def get_line_params():
    x1 = input_int("x1: ")
    y1 = input_int("y1: ")
    x2 = input_int("x2: ")
    y2 = input_int("y2: ")
    return x1, y1, x2, y2

def get_circle_params():
    cx = input_int("Центр x: ")
    cy = input_int("Центр y: ")
    r = input_int("Радиус: ")
    if r < 1:
        print("Радиус должен быть >= 1, установлено значение 1")
        r = 1
    return cx, cy, r

def main():
    print("1 - Отрезок")
    print("2 - Окружность")
    choice = input("Выберите фигуру (1 или 2): ").strip()
    if choice == "1":
        x1, y1, x2, y2 = get_line_params()
        root = tk.Tk()
        root.title("Алгоритм Брезенхема - Отрезок")
        canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
                           bg=COLORS["bg"])
        canvas.pack()
        draw_line(canvas, x1, y1, x2, y2)
        root.mainloop()
    elif choice == "2":
        cx, cy, r = get_circle_params()
        root = tk.Tk()
        root.title("Алгоритм Брезенхема - Окружность")
        canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
                           bg=COLORS["bg"])
        canvas.pack()
        draw_circle(canvas, cx, cy, r)
        root.mainloop()
    else:
        print("Неверный выбор. Запустите программу заново.")

if __name__ == "__main__":
    main()
