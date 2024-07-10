import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np
import random
import os

# Konstanten für die Bildschirmgröße und den Roboterarm
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
ARM_LENGTH_1, ARM_LENGTH_2, ARM_LENGTH_3 = 150, 150, 150
BOX_SIZE = 100  # Geändert für das Puzzle
GRID_SIZE = 100  # Geändert für das Puzzle


# Klasse für den Roboterarm
class RoboticArm:
    def __init__(self, num_joints=2):
        self.num_joints = num_joints
        self.shoulder_angle = 0
        self.elbow_angle = 0
        self.wrist_angle = 0
        self.shoulder_pos = np.array([400, SCREEN_HEIGHT / 2])
        self.holding_piece = None
        self.update_end_effector()

    def set_num_joints(self, num_joints):
        self.num_joints = num_joints
        self.update_end_effector()

    def move_to(self, target):
        dx, dy = target[0] - self.shoulder_pos[0], target[1] - self.shoulder_pos[1]
        distance = np.hypot(dx, dy)

        if self.num_joints == 1:
            self.shoulder_angle = np.arctan2(dy, dx)
            distance = min(distance, ARM_LENGTH_1)
        elif self.num_joints == 2:
            distance = min(distance, ARM_LENGTH_1 + ARM_LENGTH_2)
            cos_angle2 = (distance ** 2 - ARM_LENGTH_1 ** 2 - ARM_LENGTH_2 ** 2) / (2 * ARM_LENGTH_1 * ARM_LENGTH_2)
            cos_angle2 = np.clip(cos_angle2, -1, 1)
            self.elbow_angle = np.arccos(cos_angle2)
            self.shoulder_angle = np.arctan2(dy, dx) - np.arctan2(ARM_LENGTH_2 * np.sin(self.elbow_angle),
                                                                  ARM_LENGTH_1 + ARM_LENGTH_2 * np.cos(
                                                                      self.elbow_angle))
        elif self.num_joints == 3:
            # Berechnung der inversen Kinematik für drei Gelenke
            distance = min(distance, ARM_LENGTH_1 + ARM_LENGTH_2 + ARM_LENGTH_3)
            cos_angle2 = (distance ** 2 - ARM_LENGTH_1 ** 2 - ARM_LENGTH_2 ** 2 - ARM_LENGTH_3 ** 2) / (
                        2 * ARM_LENGTH_1 * distance)
            cos_angle2 = np.clip(cos_angle2, -1, 1)
            angle2 = np.arccos(cos_angle2)
            self.shoulder_angle = np.arctan2(dy, dx) - angle2

            x1 = ARM_LENGTH_1 * np.cos(self.shoulder_angle)
            y1 = ARM_LENGTH_1 * np.sin(self.shoulder_angle)
            x2 = target[0] - self.shoulder_pos[0] - x1
            y2 = target[1] - self.shoulder_pos[1] - y1
            d2 = np.hypot(x2, y2)
            cos_angle3 = (d2 ** 2 - ARM_LENGTH_2 ** 2 - ARM_LENGTH_3 ** 2) / (2 * ARM_LENGTH_2 * ARM_LENGTH_3)
            cos_angle3 = np.clip(cos_angle3, -1, 1)
            self.wrist_angle = np.arccos(cos_angle3)

            cos_elbow_angle = (d2 ** 2 + ARM_LENGTH_2 ** 2 - ARM_LENGTH_3 ** 2) / (2 * d2 * ARM_LENGTH_2)
            cos_elbow_angle = np.clip(cos_elbow_angle, -1, 1)
            self.elbow_angle = np.arccos(cos_elbow_angle) - np.arctan2(y2, x2)

        self.update_end_effector()

    def update_end_effector(self):
        elbow_pos = self.shoulder_pos + np.array(
            [ARM_LENGTH_1 * np.cos(self.shoulder_angle), ARM_LENGTH_1 * np.sin(self.shoulder_angle)])
        if self.num_joints == 1:
            self.end_effector_pos = elbow_pos
        elif self.num_joints == 2:
            self.end_effector_pos = elbow_pos + np.array([ARM_LENGTH_2 * np.cos(self.shoulder_angle + self.elbow_angle),
                                                          ARM_LENGTH_2 * np.sin(
                                                              self.shoulder_angle + self.elbow_angle)])
        elif self.num_joints == 3:
            wrist_pos = elbow_pos + np.array([ARM_LENGTH_2 * np.cos(self.shoulder_angle + self.elbow_angle),
                                              ARM_LENGTH_2 * np.sin(self.shoulder_angle + self.elbow_angle)])
            self.end_effector_pos = wrist_pos + np.array(
                [ARM_LENGTH_3 * np.cos(self.shoulder_angle + self.elbow_angle + self.wrist_angle),
                 ARM_LENGTH_3 * np.sin(self.shoulder_angle + self.elbow_angle + self.wrist_angle)])


# Klasse für die GUI
class GUI:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg='white')
        self.canvas.pack()

        # Initialisierung des Roboterarms
        self.robotic_arm = RoboticArm()
        self.draw_robotic_arm()

        # Initialisierung von Variablen für das Drag-and-Drop
        self.selected_box = None
        self.dragging = False

        # Event-Listener für Mausereignisse
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)

        # Erstellung des Rasters und der Puzzleteile
        self.create_grid()
        self.create_puzzle_pieces()
        self.create_legend()

        # Konfigurationsbereich oben rechts
        self.create_config_panel()

        # Button zur Überprüfung der Positionen
        self.check_button = tk.Button(master, text="Überprüfen", command=self.check_positions)
        self.check_button.pack()

    def create_config_panel(self):
        config_frame = tk.Frame(self.master, bd=2, relief=tk.RIDGE)
        config_frame.place(x=SCREEN_WIDTH - 250, y=10, width=240, height=180)

        tk.Label(config_frame, text="Konfiguration").pack(pady=10)
        tk.Label(config_frame, text="Anzahl der Gelenke:").pack()

        self.num_joints_var = tk.IntVar(value=2)
        joints_option_menu = tk.OptionMenu(config_frame, self.num_joints_var, 1, 2, 3, command=self.update_num_joints)
        joints_option_menu.pack(pady=5)

    def update_num_joints(self, value):
        self.robotic_arm.set_num_joints(int(value))
        self.draw_robotic_arm()

    def create_puzzle_pieces(self):
        # Verwendung eines relativen Pfads zum Laden des Bildes
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "math-puzzles-image.jpg")
        self.puzzle_image = Image.open(image_path)
        self.puzzle_image = self.puzzle_image.resize((2 * GRID_SIZE, 2 * GRID_SIZE), Image.Resampling.LANCZOS)
        self.puzzle_pieces = []
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        random.shuffle(positions)

        for i in range(2):
            for j in range(2):
                box_image = self.puzzle_image.crop((j * GRID_SIZE, i * GRID_SIZE, (j + 1) * GRID_SIZE, (i + 1) * GRID_SIZE))
                box_image = ImageTk.PhotoImage(box_image)
                pos = positions.pop()
                piece = self.canvas.create_image(450 + pos[1] * (BOX_SIZE + 10),
                                                 SCREEN_HEIGHT / 2 - 100 + pos[0] * (BOX_SIZE + 10), image=box_image,
                                                 tags="puzzle_piece")
                self.canvas.tag_bind(piece, "<Button-3>", self.on_right_click)
                self.puzzle_pieces.append((piece, (i, j), box_image))

    def create_grid(self):
        offset_x = 600
        offset_y = SCREEN_HEIGHT / 2 - 100
        self.grid_positions = {}
        for i in range(2):
            for j in range(2):
                x0, y0 = offset_x + j * (GRID_SIZE + 10), offset_y + i * (GRID_SIZE + 10)
                x1, y1 = offset_x + GRID_SIZE + j * (GRID_SIZE + 10), offset_y + GRID_SIZE + i * (GRID_SIZE + 10)
                square = self.canvas.create_rectangle(x0, y0, x1, y1, fill='white', outline='black', tags="grid")
                self.grid_positions[square] = (i, j)

    def create_legend(self):
        legend_items = ["Mit der linken Maustaste den Greifarm an die gewünschte Position verschieben", "Zum Aufnehmen eines Puzzleteils Rechtsklick verwenden"]
        for index, text in enumerate(legend_items):
            self.canvas.create_text(50, 30 + index * 20, text=text, anchor='w')

    def on_press(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        tags = self.canvas.gettags(item)
        if "puzzle_piece" in tags:
            self.selected_box = item
            self.dragging = True

        if self.is_near_end_effector(event.x, event.y):
            self.dragging = True

    def on_drag(self, event):
        if self.dragging:
            target = np.array([event.x, event.y])
            self.robotic_arm.move_to(target)
            self.draw_robotic_arm()

            if self.selected_box:
                ex, ey = self.robotic_arm.end_effector_pos
                self.canvas.coords(self.selected_box, ex - BOX_SIZE / 2, ey - BOX_SIZE / 2, ex + BOX_SIZE / 2,
                                   ey + BOX_SIZE / 2)

        """
        if self.dragging and self.selected_box:
            self.canvas.coords(self.selected_box, event.x, event.y)
        """

    def on_release(self, event):
        if self.dragging:
            self.dragging = False
            self.selected_box = None

    def on_release(self, event):
        self.dragging = False

    def on_right_click(self, event):
        target = (event.x, event.y)
        if self.robotic_arm.holding_piece is None:
            item = self.canvas.find_closest(target[0], target[1])
            tags = self.canvas.gettags(item)
            if "puzzle_piece" in tags:
                self.robotic_arm.holding_piece = item
                self.canvas.itemconfig(item, state='hidden')
                self.robotic_arm.move_to(target)
        else:
            self.canvas.itemconfig(self.robotic_arm.holding_piece, state='normal')
            self.canvas.coords(self.robotic_arm.holding_piece, target[0], target[1])
            self.robotic_arm.holding_piece = None
            self.robotic_arm.move_to(target)
        self.draw_robotic_arm()

    def check_positions(self):
        correct_positions = {(0, 0): (600, 200), (0, 1): (710, 200), (1, 0): (600, 310), (1, 1): (710, 310)}
        all_correct = True
        for piece, correct_pos, _ in self.puzzle_pieces:
            current_pos = self.canvas.coords(piece)
            correct_grid_pos = correct_positions[correct_pos]
            if abs(current_pos[0] - correct_grid_pos[0]) > 10 or abs(current_pos[1] - correct_grid_pos[1]) > 10:
                all_correct = False
                break

        if all_correct:
            messagebox.showinfo("Erfolg", "Alle Puzzleteile sind korrekt positioniert!")
        else:
            messagebox.showwarning("Fehler", "Ein oder mehrere Puzzleteile sind falsch positioniert.")

    def is_near_end_effector(self, x, y):
        ex, ey = self.robotic_arm.end_effector_pos
        return np.hypot(ex - x, ey - y) < 10

    def draw_robotic_arm(self):
        self.canvas.delete("arm")
        shoulder_pos = self.robotic_arm.shoulder_pos
        elbow_pos = shoulder_pos + np.array([ARM_LENGTH_1 * np.cos(self.robotic_arm.shoulder_angle),
                                             ARM_LENGTH_1 * np.sin(self.robotic_arm.shoulder_angle)])
        self.canvas.create_line(shoulder_pos[0], shoulder_pos[1], elbow_pos[0], elbow_pos[1], fill="blue", width=3,
                                tags="arm")

        if self.robotic_arm.num_joints >= 2:
            end_effector_pos = elbow_pos + np.array(
                [ARM_LENGTH_2 * np.cos(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle),
                 ARM_LENGTH_2 * np.sin(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle)])
            self.canvas.create_line(elbow_pos[0], elbow_pos[1], end_effector_pos[0], end_effector_pos[1], fill="green",
                                    width=3, tags="arm")

            if self.robotic_arm.num_joints == 3:
                wrist_pos = end_effector_pos + np.array([ARM_LENGTH_3 * np.cos(
                    self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle + self.robotic_arm.wrist_angle),
                                                         ARM_LENGTH_3 * np.sin(
                                                             self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle + self.robotic_arm.wrist_angle)])
                self.canvas.create_line(end_effector_pos[0], end_effector_pos[1], wrist_pos[0], wrist_pos[1],
                                        fill="red", width=3, tags="arm")


# Hauptprogramm
if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()
