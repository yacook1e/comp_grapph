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
            angle = math.radians(i * 36 + 90)
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

        self.btn_frame = tk.Frame(root, bg=PANEL_BG, width=220)
        self.btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        self.btn_frame.pack_propagate(False)

        self.shape = CompoundShape()
        self.snowflake_template = create_snowflake_template(15)
        self.snowflakes = []
        for _ in range(40):
            self.snowflakes.append([
                random.uniform(-CENTER_X + 50, CENTER_X - 50),
                random.uniform(-CENTER_Y + 50, CENTER_Y - 50),
                random.uniform(-0.5, 0.5),
                random.uniform(-3.0, -1.0),
                random.uniform(0, 360),
                random.uniform(-2, 2),
                random.uniform(0.7, 1.3)
            ])

        self.mode = "shapes"
        self.animation_id = None

        self.create_buttons()
        self.draw_axes()
        self.redraw_shape()
        self.animate()

    def draw_axes(self):
        self.canvas.delete("axes")
        
        self.canvas.create_line(CENTER_X, 0, CENTER_X, HEIGHT, fill="#555566", tags="axes", width=2)
        self.canvas.create_line(0, CENTER_Y, WIDTH, CENTER_Y, fill="#555566", tags="axes", width=2)

        
        self.canvas.create_line(CENTER_X, 5, CENTER_X-5, 15, fill="#555566", tags="axes")
        self.canvas.create_line(CENTER_X, 5, CENTER_X+5, 15, fill="#555566", tags="axes")
        self.canvas.create_line(WIDTH-5, CENTER_Y, WIDTH-15, CENTER_Y-5, fill="#555566", tags="axes")
        self.canvas.create_line(WIDTH-5, CENTER_Y, WIDTH-15, CENTER_Y+5, fill="#555566", tags="axes")

        
        self.canvas.create_text(WIDTH-20, CENTER_Y-10, text="X", fill="#888899", font=("Arial", 12, "bold"), tags="axes")
        self.canvas.create_text(CENTER_X+10, 15, text="Y", fill="#888899", font=("Arial", 12, "bold"), tags="axes")

        
        step = 50
        for x in range(step, WIDTH, step):
            if x == CENTER_X:
                continue
            world_x = x - CENTER_X
            self.canvas.create_line(x, CENTER_Y-3, x, CENTER_Y+3, fill="#555566", tags="axes")
            self.canvas.create_text(x, CENTER_Y+12, text=str(world_x), fill="#777788", font=("Arial", 8), tags="axes")
        for y in range(step, HEIGHT, step):
            if y == CENTER_Y:
                continue
            world_y = CENTER_Y - y
            self.canvas.create_line(CENTER_X-3, y, CENTER_X+3, y, fill="#555566", tags="axes")
            self.canvas.create_text(CENTER_X-10, y, text=str(world_y), fill="#777788", font=("Arial", 8), tags="axes")

        self.canvas.create_text(CENTER_X-10, CENTER_Y+12, text="0", fill="#888899", font=("Arial", 9), tags="axes")

    def create_buttons(self):
        btn_pad = 3

        
        tk.Label(self.btn_frame, text="Сдвиг (пиксели)", bg=PANEL_BG, fg=TEXT_COLOR, font=("Arial", 9, "bold")).pack(fill=tk.X, pady=(8,0))
        frame_shift = tk.Frame(self.btn_frame, bg=PANEL_BG)
        frame_shift.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(frame_shift, text="dx:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT)
        self.shift_x_entry = tk.Entry(frame_shift, width=6, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.shift_x_entry.pack(side=tk.LEFT, padx=2)
        self.shift_x_entry.insert(0, "10")
        tk.Label(frame_shift, text="dy:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=(5,0))
        self.shift_y_entry = tk.Entry(frame_shift, width=6, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.shift_y_entry.pack(side=tk.LEFT, padx=2)
        self.shift_y_entry.insert(0, "10")
        btn_shift = tk.Button(self.btn_frame, text="Применить сдвиг", bg=BUTTON_BG, fg=TEXT_COLOR, command=self.apply_shift)
        btn_shift.pack(fill=tk.X, padx=5, pady=2)

        
        tk.Label(self.btn_frame, text="Масштабирование", bg=PANEL_BG, fg=TEXT_COLOR, font=("Arial", 9, "bold")).pack(fill=tk.X, pady=(8,0))
        frame_scale = tk.Frame(self.btn_frame, bg=PANEL_BG)
        frame_scale.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(frame_scale, text="sx:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT)
        self.scale_x_entry = tk.Entry(frame_scale, width=6, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.scale_x_entry.pack(side=tk.LEFT, padx=2)
        self.scale_x_entry.insert(0, "1.1")
        tk.Label(frame_scale, text="sy:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=(5,0))
        self.scale_y_entry = tk.Entry(frame_scale, width=6, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.scale_y_entry.pack(side=tk.LEFT, padx=2)
        self.scale_y_entry.insert(0, "1.1")
        btn_scale = tk.Button(self.btn_frame, text="Применить масштаб", bg=BUTTON_BG, fg=TEXT_COLOR, command=self.apply_scale)
        btn_scale.pack(fill=tk.X, padx=5, pady=2)

        
        tk.Label(self.btn_frame, text="Поворот (градусы)", bg=PANEL_BG, fg=TEXT_COLOR, font=("Arial", 9, "bold")).pack(fill=tk.X, pady=(8,0))
        frame_rot = tk.Frame(self.btn_frame, bg=PANEL_BG)
        frame_rot.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(frame_rot, text="угол:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT)
        self.rot_angle_entry = tk.Entry(frame_rot, width=6, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.rot_angle_entry.pack(side=tk.LEFT, padx=2)
        self.rot_angle_entry.insert(0, "15")
        btn_rot = tk.Button(self.btn_frame, text="Повернуть вокруг O", bg=BUTTON_BG, fg=TEXT_COLOR, command=self.apply_rotation)
        btn_rot.pack(fill=tk.X, padx=5, pady=2)

        
        tk.Label(self.btn_frame, text="Поворот вокруг точки", bg=PANEL_BG, fg=TEXT_COLOR, font=("Arial", 9, "bold")).pack(fill=tk.X, pady=(8,0))
        frame_point = tk.Frame(self.btn_frame, bg=PANEL_BG)
        frame_point.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(frame_point, text="cx:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT)
        self.rot_cx_entry = tk.Entry(frame_point, width=5, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.rot_cx_entry.pack(side=tk.LEFT, padx=2)
        self.rot_cx_entry.insert(0, "0")
        tk.Label(frame_point, text="cy:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=(5,0))
        self.rot_cy_entry = tk.Entry(frame_point, width=5, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.rot_cy_entry.pack(side=tk.LEFT, padx=2)
        self.rot_cy_entry.insert(0, "0")
        tk.Label(frame_point, text="угол:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=(5,0))
        self.rot_point_angle_entry = tk.Entry(frame_point, width=5, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.rot_point_angle_entry.pack(side=tk.LEFT, padx=2)
        self.rot_point_angle_entry.insert(0, "30")
        btn_rot_point = tk.Button(self.btn_frame, text="Применить поворот", bg=BUTTON_BG, fg=TEXT_COLOR, command=self.apply_rotation_around_point)
        btn_rot_point.pack(fill=tk.X, padx=5, pady=2)

        
        tk.Frame(self.btn_frame, height=2, bg="#444455").pack(fill=tk.X, pady=8)
        reset_btn = tk.Button(self.btn_frame, text="Сбросить фигуру", bg=BUTTON_BG, fg=TEXT_COLOR, command=self.reset_shape)
        reset_btn.pack(fill=tk.X, padx=5, pady=2)

        self.mode_btn = tk.Button(self.btn_frame, text="Снежинки", bg=BUTTON_BG, fg=TEXT_COLOR, command=self.toggle_mode)
        self.mode_btn.pack(fill=tk.X, padx=5, pady=2)

    def apply_shift(self):
        try:
            dx = float(self.shift_x_entry.get())
            dy = float(self.shift_y_entry.get())
        except ValueError:
            return
        if self.mode == "shapes":
            self.shape.transform(Matrix3x3.translation(dx, dy))
            self.redraw_shape()

    def apply_scale(self):
        try:
            sx = float(self.scale_x_entry.get())
            sy = float(self.scale_y_entry.get())
        except ValueError:
            return
        if self.mode == "shapes":
            self.shape.transform(Matrix3x3.scaling(sx, sy))
            self.redraw_shape()

    def apply_rotation(self):
        try:
            angle = float(self.rot_angle_entry.get())
        except ValueError:
            return
        if self.mode == "shapes":
            self.shape.transform(Matrix3x3.rotation(angle))
            self.redraw_shape()

    def apply_rotation_around_point(self):
        try:
            cx = float(self.rot_cx_entry.get())
            cy = float(self.rot_cy_entry.get())
            angle = float(self.rot_point_angle_entry.get())
        except ValueError:
            return
        if self.mode == "shapes":
            matrix = Matrix3x3.rotation_around(angle, cx, cy)
            self.shape.transform(matrix)
            self.redraw_shape()

    def reset_shape(self):
        if self.mode == "shapes":
            self.shape.reset()
            self.redraw_shape()

    def redraw_shape(self):
        self.canvas.delete("shape")
        self.shape.draw(self.canvas)

    def toggle_mode(self):
        if self.mode == "shapes":
            self.mode = "snow"
            self.mode_btn.config(text="Фигуры")
            self.canvas.delete("shape")
        else:
            self.mode = "shapes"
            self.mode_btn.config(text="Снежинки")
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
            angle = math.radians(i * 36 + 90)
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

        self.btn_frame = tk.Frame(root, bg=PANEL_BG, width=220)
        self.btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        self.btn_frame.pack_propagate(False)

        self.shape = CompoundShape()
        self.snowflake_template = create_snowflake_template(15)
        self.snowflakes = []
        for _ in range(40):
            self.snowflakes.append([
                random.uniform(-CENTER_X + 50, CENTER_X - 50),
                random.uniform(-CENTER_Y + 50, CENTER_Y - 50),
                random.uniform(-0.5, 0.5),
                random.uniform(-3.0, -1.0),
                random.uniform(0, 360),
                random.uniform(-2, 2),
                random.uniform(0.7, 1.3)
            ])

        self.mode = "shapes"
        self.animation_id = None

        self.create_buttons()
        self.draw_axes()
        self.redraw_shape()
        self.animate()

    def draw_axes(self):
        self.canvas.delete("axes")
        
        self.canvas.create_line(CENTER_X, 0, CENTER_X, HEIGHT, fill="#555566", tags="axes", width=2)
        self.canvas.create_line(0, CENTER_Y, WIDTH, CENTER_Y, fill="#555566", tags="axes", width=2)

        
        self.canvas.create_line(CENTER_X, 5, CENTER_X-5, 15, fill="#555566", tags="axes")
        self.canvas.create_line(CENTER_X, 5, CENTER_X+5, 15, fill="#555566", tags="axes")
        self.canvas.create_line(WIDTH-5, CENTER_Y, WIDTH-15, CENTER_Y-5, fill="#555566", tags="axes")
        self.canvas.create_line(WIDTH-5, CENTER_Y, WIDTH-15, CENTER_Y+5, fill="#555566", tags="axes")

        
        self.canvas.create_text(WIDTH-20, CENTER_Y-10, text="X", fill="#888899", font=("Arial", 12, "bold"), tags="axes")
        self.canvas.create_text(CENTER_X+10, 15, text="Y", fill="#888899", font=("Arial", 12, "bold"), tags="axes")

        
        step = 50
        for x in range(step, WIDTH, step):
            if x == CENTER_X:
                continue
            world_x = x - CENTER_X
            self.canvas.create_line(x, CENTER_Y-3, x, CENTER_Y+3, fill="#555566", tags="axes")
            self.canvas.create_text(x, CENTER_Y+12, text=str(world_x), fill="#777788", font=("Arial", 8), tags="axes")
        for y in range(step, HEIGHT, step):
            if y == CENTER_Y:
                continue
            world_y = CENTER_Y - y
            self.canvas.create_line(CENTER_X-3, y, CENTER_X+3, y, fill="#555566", tags="axes")
            self.canvas.create_text(CENTER_X-10, y, text=str(world_y), fill="#777788", font=("Arial", 8), tags="axes")

        self.canvas.create_text(CENTER_X-10, CENTER_Y+12, text="0", fill="#888899", font=("Arial", 9), tags="axes")

    def create_buttons(self):
        btn_pad = 3

        # --- Сдвиг ---
        tk.Label(self.btn_frame, text="Сдвиг (пиксели)", bg=PANEL_BG, fg=TEXT_COLOR, font=("Arial", 9, "bold")).pack(fill=tk.X, pady=(8,0))
        frame_shift = tk.Frame(self.btn_frame, bg=PANEL_BG)
        frame_shift.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(frame_shift, text="dx:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT)
        self.shift_x_entry = tk.Entry(frame_shift, width=6, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.shift_x_entry.pack(side=tk.LEFT, padx=2)
        self.shift_x_entry.insert(0, "10")
        tk.Label(frame_shift, text="dy:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=(5,0))
        self.shift_y_entry = tk.Entry(frame_shift, width=6, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.shift_y_entry.pack(side=tk.LEFT, padx=2)
        self.shift_y_entry.insert(0, "10")
        btn_shift = tk.Button(self.btn_frame, text="Применить сдвиг", bg=BUTTON_BG, fg=TEXT_COLOR, command=self.apply_shift)
        btn_shift.pack(fill=tk.X, padx=5, pady=2)

        # --- Масштабирование ---
        tk.Label(self.btn_frame, text="Масштабирование", bg=PANEL_BG, fg=TEXT_COLOR, font=("Arial", 9, "bold")).pack(fill=tk.X, pady=(8,0))
        frame_scale = tk.Frame(self.btn_frame, bg=PANEL_BG)
        frame_scale.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(frame_scale, text="sx:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT)
        self.scale_x_entry = tk.Entry(frame_scale, width=6, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.scale_x_entry.pack(side=tk.LEFT, padx=2)
        self.scale_x_entry.insert(0, "1.1")
        tk.Label(frame_scale, text="sy:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=(5,0))
        self.scale_y_entry = tk.Entry(frame_scale, width=6, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.scale_y_entry.pack(side=tk.LEFT, padx=2)
        self.scale_y_entry.insert(0, "1.1")
        btn_scale = tk.Button(self.btn_frame, text="Применить масштаб", bg=BUTTON_BG, fg=TEXT_COLOR, command=self.apply_scale)
        btn_scale.pack(fill=tk.X, padx=5, pady=2)

        # --- Поворот вокруг начала координат ---
        tk.Label(self.btn_frame, text="Поворот (градусы)", bg=PANEL_BG, fg=TEXT_COLOR, font=("Arial", 9, "bold")).pack(fill=tk.X, pady=(8,0))
        frame_rot = tk.Frame(self.btn_frame, bg=PANEL_BG)
        frame_rot.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(frame_rot, text="угол:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT)
        self.rot_angle_entry = tk.Entry(frame_rot, width=6, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.rot_angle_entry.pack(side=tk.LEFT, padx=2)
        self.rot_angle_entry.insert(0, "15")
        btn_rot = tk.Button(self.btn_frame, text="Повернуть вокруг O", bg=BUTTON_BG, fg=TEXT_COLOR, command=self.apply_rotation)
        btn_rot.pack(fill=tk.X, padx=5, pady=2)

        # --- Поворот вокруг точки ---
        tk.Label(self.btn_frame, text="Поворот вокруг точки", bg=PANEL_BG, fg=TEXT_COLOR, font=("Arial", 9, "bold")).pack(fill=tk.X, pady=(8,0))
        frame_point = tk.Frame(self.btn_frame, bg=PANEL_BG)
        frame_point.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(frame_point, text="cx:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT)
        self.rot_cx_entry = tk.Entry(frame_point, width=5, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.rot_cx_entry.pack(side=tk.LEFT, padx=2)
        self.rot_cx_entry.insert(0, "0")
        tk.Label(frame_point, text="cy:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=(5,0))
        self.rot_cy_entry = tk.Entry(frame_point, width=5, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.rot_cy_entry.pack(side=tk.LEFT, padx=2)
        self.rot_cy_entry.insert(0, "0")
        tk.Label(frame_point, text="угол:", bg=PANEL_BG, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=(5,0))
        self.rot_point_angle_entry = tk.Entry(frame_point, width=5, bg=BUTTON_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.rot_point_angle_entry.pack(side=tk.LEFT, padx=2)
        self.rot_point_angle_entry.insert(0, "30")
        btn_rot_point = tk.Button(self.btn_frame, text="Применить поворот", bg=BUTTON_BG, fg=TEXT_COLOR, command=self.apply_rotation_around_point)
        btn_rot_point.pack(fill=tk.X, padx=5, pady=2)

        # --- Отражения ---
        tk.Label(self.btn_frame, text="Отражения", bg=PANEL_BG, fg=TEXT_COLOR, font=("Arial", 9, "bold")).pack(fill=tk.X, pady=(8,0))
        btn_reflect_x = tk.Button(self.btn_frame, text="Относительно OX", bg=BUTTON_BG, fg=TEXT_COLOR,
                                  command=lambda: self.apply_reflection(Matrix3x3.reflection_x()))
        btn_reflect_x.pack(fill=tk.X, padx=5, pady=2)
        btn_reflect_y = tk.Button(self.btn_frame, text="Относительно OY", bg=BUTTON_BG, fg=TEXT_COLOR,
                                  command=lambda: self.apply_reflection(Matrix3x3.reflection_y()))
        btn_reflect_y.pack(fill=tk.X, padx=5, pady=2)
        btn_reflect_yx = tk.Button(self.btn_frame, text="Относительно Y=X", bg=BUTTON_BG, fg=TEXT_COLOR,
                                   command=lambda: self.apply_reflection(Matrix3x3.reflection_yx()))
        btn_reflect_yx.pack(fill=tk.X, padx=5, pady=2)

        # --- Кнопки управления ---
        tk.Frame(self.btn_frame, height=2, bg="#444455").pack(fill=tk.X, pady=8)
        reset_btn = tk.Button(self.btn_frame, text="Сбросить фигуру", bg=BUTTON_BG, fg=TEXT_COLOR, command=self.reset_shape)
        reset_btn.pack(fill=tk.X, padx=5, pady=2)

        self.mode_btn = tk.Button(self.btn_frame, text="Снежинки", bg=BUTTON_BG, fg=TEXT_COLOR, command=self.toggle_mode)
        self.mode_btn.pack(fill=tk.X, padx=5, pady=2)

    def apply_reflection(self, matrix):
        if self.mode == "shapes":
            self.shape.transform(matrix)
            self.redraw_shape()

    def apply_shift(self):
        try:
            dx = float(self.shift_x_entry.get())
            dy = float(self.shift_y_entry.get())
        except ValueError:
            return
        if self.mode == "shapes":
            self.shape.transform(Matrix3x3.translation(dx, dy))
            self.redraw_shape()

    def apply_scale(self):
        try:
            sx = float(self.scale_x_entry.get())
            sy = float(self.scale_y_entry.get())
        except ValueError:
            return
        if self.mode == "shapes":
            self.shape.transform(Matrix3x3.scaling(sx, sy))
            self.redraw_shape()

    def apply_rotation(self):
        try:
            angle = float(self.rot_angle_entry.get())
        except ValueError:
            return
        if self.mode == "shapes":
            self.shape.transform(Matrix3x3.rotation(angle))
            self.redraw_shape()

    def apply_rotation_around_point(self):
        try:
            cx = float(self.rot_cx_entry.get())
            cy = float(self.rot_cy_entry.get())
            angle = float(self.rot_point_angle_entry.get())
        except ValueError:
            return
        if self.mode == "shapes":
            matrix = Matrix3x3.rotation_around(angle, cx, cy)
            self.shape.transform(matrix)
            self.redraw_shape()

    def reset_shape(self):
        if self.mode == "shapes":
            self.shape.reset()
            self.redraw_shape()

    def redraw_shape(self):
        self.canvas.delete("shape")
        self.shape.draw(self.canvas)

    def toggle_mode(self):
        if self.mode == "shapes":
            self.mode = "snow"
            self.mode_btn.config(text="Фигуры")
            self.canvas.delete("shape")
        else:
            self.mode = "shapes"
            self.mode_btn.config(text="Снежинки")
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
