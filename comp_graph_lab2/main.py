import tkinter as tk
import math
import random

WIDTH = 800
HEIGHT = 600
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

BG_COLOR = "#1e1e2f"
STAR_COLOR = "#ffaa66"
HEX_COLOR = "#66aaff"
SNOW_COLOR = "#aaddff"
BUTTON_BG = "#3a3a4a"
BUTTON_ACTIVE = "#5a5a6a"
TEXT_COLOR = "#ffffff"
PANEL_BG = "#2a2a3a"

class Matrix3x3:
    def __init__(self, data=None):
        # единичная по умолчанию
        if data is None:
            self.data = [[1, 0, 0],
                         [0, 1, 0],
                         [0, 0, 1]]
        else:
            self.data = [row[:] for row in data]

    def __mul__(self, other):
        result = [[0, 0, 0] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    result[i][j] += self.data[i][k] * other.data[k][j]
        return Matrix3x3(result)

    def transform_point(self, point):
        x, y, w = point
        x_new = self.data[0][0]*x + self.data[0][1]*y + self.data[0][2]*w
        y_new = self.data[1][0]*x + self.data[1][1]*y + self.data[1][2]*w
        return [x_new, y_new, w]

    @staticmethod
    def translation(dx, dy):
        return Matrix3x3([[1, 0, dx],
                          [0, 1, dy],
                          [0, 0, 1]])

    @staticmethod
    def scaling(sx, sy):
        return Matrix3x3([[sx, 0, 0],
                          [0, sy, 0],
                          [0, 0, 1]])

    @staticmethod
    def rotation(angle_deg):
        rad = math.radians(angle_deg)
        c, s = math.cos(rad), math.sin(rad)
        return Matrix3x3([[c, -s, 0],
                          [s,  c, 0],
                          [0,  0, 1]])

    @staticmethod
    def reflection_x():
        return Matrix3x3([[1, 0, 0],
                          [0, -1, 0],
                          [0, 0, 1]])

    @staticmethod
    def reflection_y():
        return Matrix3x3([[-1, 0, 0],
                          [0, 1, 0],
                          [0, 0, 1]])

    @staticmethod
    def reflection_yx():
        return Matrix3x3([[0, 1, 0],
                          [1, 0, 0],
                          [0, 0, 1]])

    @staticmethod
    def rotation_around(angle_deg, cx, cy):
        t1 = Matrix3x3.translation(-cx, -cy)
        r = Matrix3x3.rotation(angle_deg)
        t2 = Matrix3x3.translation(cx, cy)
        return t2 * r * t1

class CompoundShape:
    def __init__(self):
        outer_r = 80
        inner_r = 35
        self.star_verts = []
        for i in range(10):
            angle = math.radians(i * 36 + 90)  #+90 градусов для вертикальной ориентации
            r = outer_r if i % 2 == 0 else inner_r
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            self.star_verts.append([x, y])

        hex_r = inner_r * 1.056
        self.hex_verts = []
        for i in range(6):
            angle = math.radians(i * 60)
            x = hex_r * math.cos(angle)
            y = hex_r * math.sin(angle)
            self.hex_verts.append([x, y])

        self.orig_star = [list(v) for v in self.star_verts]
        self.orig_hex = [list(v) for v in self.hex_verts]

    def transform(self, matrix):
        new_star = []
        for v in self.star_verts:
            p = matrix.transform_point([v[0], v[1], 1])
            new_star.append([p[0], p[1]])
        self.star_verts = new_star

        new_hex = []
        for v in self.hex_verts:
            p = matrix.transform_point([v[0], v[1], 1])
            new_hex.append([p[0], p[1]])
        self.hex_verts = new_hex

    def reset(self):
        self.star_verts = [list(v) for v in self.orig_star]
        self.hex_verts = [list(v) for v in self.orig_hex]

    def draw(self, canvas):
        if len(self.star_verts) >= 3:
            points = []
            for v in self.star_verts:
                x = CENTER_X + v[0]
                y = CENTER_Y - v[1]
                points.append((x, y))
            canvas.create_polygon(points, outline=STAR_COLOR, fill="", width=2, tags="shape")

        if len(self.hex_verts) >= 3:
            points = []
            for v in self.hex_verts:
                x = CENTER_X + v[0]
                y = CENTER_Y - v[1]
                points.append((x, y))
            canvas.create_polygon(points, outline=HEX_COLOR, fill="", width=2, tags="shape")

def create_snowflake_template(radius=15):
    vertices = []
    for i in range(12):
        angle = math.radians(i * 30)
        r = radius if i % 2 == 0 else radius * 0.5
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        vertices.append([x, y])
    return vertices

class LabApp:
    def __init__(self, root):
        self.root = root
        root.title("лабораторная работа 2 - вариант 5")
        root.geometry(f"{WIDTH}x{HEIGHT}")
        root.configure(bg=BG_COLOR)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.btn_frame = tk.Frame(root, bg=PANEL_BG, width=140)
        self.btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        self.btn_frame.pack_propagate(False)

        self.shape = CompoundShape()

        self.snowflake_template = create_snowflake_template(15)
        self.snowflakes = []
        for _ in range(40):
            self.snowflakes.append([
                random.uniform(-CENTER_X + 50, CENTER_X - 50),   # x
                random.uniform(-CENTER_Y + 50, CENTER_Y - 50),   # y
                random.uniform(-0.5, 0.5),                       # vx
                random.uniform(-3.0, -1.0),                      # vy
                random.uniform(0, 360),              # угол
                random.uniform(-2, 2),              # угловая скорость
                random.uniform(0.7, 1.3)      # масштаб
            ])

        self.mode = "shapes"
        self.animation_id = None
        self.pending_rotate_point = False
        self.rotate_angle = 15

        self.create_buttons()
        self.draw_axes()
        self.redraw_shape()
        self.animate()
    def draw_axes(self):
        self.canvas.delete("axes")
        self.canvas.create_line(CENTER_X, 0, CENTER_X, HEIGHT, fill="#444444", tags="axes")
        self.canvas.create_line(0, CENTER_Y, WIDTH, CENTER_Y, fill="#444444", tags="axes")

    def create_buttons(self):
        btn_pad = 3
        buttons_data = [
            ("Move OX+", lambda: self.transform_shape(Matrix3x3.translation(10, 0))),
            ("Move OX-", lambda: self.transform_shape(Matrix3x3.translation(-10, 0))),
            ("Move OY+", lambda: self.transform_shape(Matrix3x3.translation(0, 10))),
            ("Move OY-", lambda: self.transform_shape(Matrix3x3.translation(0, -10))),
            ("Refl OX", lambda: self.transform_shape(Matrix3x3.reflection_x())),
            ("Refl OY", lambda: self.transform_shape(Matrix3x3.reflection_y())),
            ("Refl Y=X", lambda: self.transform_shape(Matrix3x3.reflection_yx())),
            ("X+", lambda: self.transform_shape(Matrix3x3.scaling(1.1, 1.0))),
            ("X-", lambda: self.transform_shape(Matrix3x3.scaling(0.9, 1.0))),
            ("Y+", lambda: self.transform_shape(Matrix3x3.scaling(1.0, 1.1))),
            ("Y-", lambda: self.transform_shape(Matrix3x3.scaling(1.0, 0.9))),
            ("Rot around O", lambda: self.transform_shape(Matrix3x3.rotation(15))),
        ]
        for text, cmd in buttons_data:
            btn = tk.Button(self.btn_frame, text=text, bg=BUTTON_BG, fg=TEXT_COLOR,
                            activebackground=BUTTON_ACTIVE, command=cmd)
            btn.pack(fill=tk.X, pady=btn_pad, padx=5)

        # поворот вокруг точки
        self.rotate_point_btn = tk.Button(self.btn_frame, text="Rot around point", bg=BUTTON_BG, fg=TEXT_COLOR,
                                          activebackground=BUTTON_ACTIVE, command=self.activate_rotate_point)
        self.rotate_point_btn.pack(fill=tk.X, pady=btn_pad, padx=5)

        reset_btn = tk.Button(self.btn_frame, text="Reset", bg=BUTTON_BG, fg=TEXT_COLOR,
                              activebackground=BUTTON_ACTIVE, command=self.reset_shape)
        reset_btn.pack(fill=tk.X, pady=btn_pad, padx=5)

        self.mode_btn = tk.Button(self.btn_frame, text="Snowflakes", bg=BUTTON_BG, fg=TEXT_COLOR,
                                  activebackground=BUTTON_ACTIVE, command=self.toggle_mode)
        self.mode_btn.pack(fill=tk.X, pady=btn_pad, padx=5)

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def transform_shape(self, matrix):
        if self.mode == "shapes":
            self.shape.transform(matrix)
            self.redraw_shape()

    def reset_shape(self):
        self.shape.reset()
        self.redraw_shape()

    def activate_rotate_point(self):
        if self.mode == "shapes":
            self.pending_rotate_point = True
            self.canvas.config(cursor="crosshair")

    def on_canvas_click(self, event):
        if self.pending_rotate_point:
            world_x = event.x - CENTER_X
            world_y = CENTER_Y - event.y
            matrix = Matrix3x3.rotation_around(self.rotate_angle, world_x, world_y)
            self.shape.transform(matrix)
            self.pending_rotate_point = False
            self.canvas.config(cursor="")
            self.redraw_shape()

    def redraw_shape(self):
        self.canvas.delete("shape")
        self.shape.draw(self.canvas)

    def toggle_mode(self):
        if self.mode == "shapes":
            self.mode = "snow"
            self.mode_btn.config(text="Shapes")
            self.canvas.delete("shape")
        else:
            self.mode = "shapes"
            self.mode_btn.config(text="Snowflakes")
            self.canvas.delete("snowflake")
            self.redraw_shape()

    def animate(self):
        if self.mode == "snow":
            self.update_snowflakes()
            self.draw_snowflakes()
        self.animation_id = self.root.after(30, self.animate)

    def update_snowflakes(self):
        dt = 0.03
        for sf in self.snowflakes:
            sf[0] += sf[2] * dt
            sf[1] += sf[3] * dt
            sf[4] += sf[5] * dt

            if sf[1] < -CENTER_Y - 50:
                sf[0] = random.uniform(-CENTER_X + 50, CENTER_X - 50)
                sf[1] = CENTER_Y - 50
                sf[2] = random.uniform(-0.5, 0.5)
                sf[3] = random.uniform(-3.0, -1.0)
                sf[4] = random.uniform(0, 360)
                sf[5] = random.uniform(-2, 2)
                sf[6] = random.uniform(0.7, 1.3)

    def draw_snowflakes(self):
        self.canvas.delete("snowflake")
        for sf in self.snowflakes:
            # матрица масштаб, поворот, перенос
            m_scale = Matrix3x3.scaling(sf[6], sf[6])
            m_rot = Matrix3x3.rotation(sf[4])
            m_trans = Matrix3x3.translation(sf[0], sf[1])
            matrix = m_trans * m_rot * m_scale

            points = []
            for v in self.snowflake_template:
                p = matrix.transform_point([v[0], v[1], 1])
                x = CENTER_X + p[0]
                y = CENTER_Y - p[1]
                points.append((x, y))
            if len(points) > 2:
                self.canvas.create_polygon(points, outline=SNOW_COLOR, fill="", width=1, tags="snowflake")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = LabApp(root)
    app.run()