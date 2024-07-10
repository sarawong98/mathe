import tkinter as tk
import numpy as np
import random

# Konstanten für die Bildschirmgröße und den Roboterarm
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
ARM_LENGTH_1, ARM_LENGTH_2, ARM_LENGTH_3 = 150, 150, 150
BOX_SIZE = 50
GRID_SIZE = 50

# Klasse für den Roboterarm
class RoboticArm:
    def __init__(self, num_joints=2):
        self.num_joints = num_joints
        self.shoulder_angle = 0
        self.elbow_angle = 0
        self.wrist_angle = 0
        self.shoulder_pos = np.array([400, SCREEN_HEIGHT / 2])
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
                                                                  ARM_LENGTH_1 + ARM_LENGTH_2 * np.cos(self.elbow_angle))
        elif self.num_joints == 3:
            # Berechnung der inversen Kinematik für drei Gelenke
            distance = min(distance, ARM_LENGTH_1 + ARM_LENGTH_2 + ARM_LENGTH_3)
            cos_angle2 = (distance**2 - ARM_LENGTH_1**2 - ARM_LENGTH_2**2 - ARM_LENGTH_3**2) / (2 * ARM_LENGTH_1 * distance)
            cos_angle2 = np.clip(cos_angle2, -1, 1)
            angle2 = np.arccos(cos_angle2)
            self.shoulder_angle = np.arctan2(dy, dx) - angle2

            x1 = ARM_LENGTH_1 * np.cos(self.shoulder_angle)
            y1 = ARM_LENGTH_1 * np.sin(self.shoulder_angle)
            x2 = target[0] - self.shoulder_pos[0] - x1
            y2 = target[1] - self.shoulder_pos[1] - y1
            d2 = np.hypot(x2, y2)
            cos_angle3 = (d2**2 - ARM_LENGTH_2**2 - ARM_LENGTH_3**2) / (2 * ARM_LENGTH_2 * ARM_LENGTH_3)
            cos_angle3 = np.clip(cos_angle3, -1, 1)
            self.wrist_angle = np.arccos(cos_angle3)

            cos_elbow_angle = (d2**2 + ARM_LENGTH_2**2 - ARM_LENGTH_3**2) / (2 * d2 * ARM_LENGTH_2)
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
                                                          ARM_LENGTH_2 * np.sin(self.shoulder_angle + self.elbow_angle)])
        elif self.num_joints == 3:
            wrist_pos = elbow_pos + np.array([ARM_LENGTH_2 * np.cos(self.shoulder_angle + self.elbow_angle),
                                              ARM_LENGTH_2 * np.sin(self.shoulder_angle + self.elbow_angle)])
            self.end_effector_pos = wrist_pos + np.array([ARM_LENGTH_3 * np.cos(self.shoulder_angle + self.elbow_angle + self.wrist_angle),
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

        # Erstellung des Rasters und der roten Kästen
        self.create_grid()
        self.create_red_boxes()
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

    def create_red_boxes(self):
        colors = ["red", "green", "blue", "yellow"]
        random.shuffle(colors)
        self.box_colors = {}
        offset_x = 450
        offset_y = SCREEN_HEIGHT / 2 - 150
        for i, color in enumerate(colors):
            box = self.canvas.create_rectangle(offset_x, offset_y + i * (BOX_SIZE + 10), offset_x + BOX_SIZE,
                                               offset_y + BOX_SIZE + i * (BOX_SIZE + 10), fill='white', outline='black',
                                               tags="box")
            self.canvas.tag_bind(box, "<Button-3>", self.on_right_click)
            self.box_colors[box] = color

    def create_grid(self):
        colors = ["red", "green", "blue", "yellow"]
        random.shuffle(colors)
        self.grid_colors = {}
        offset_x = 600
        offset_y = SCREEN_HEIGHT / 2 - 50
        for i in range(2):
            for j in range(2):
                x0, y0 = offset_x + j * (GRID_SIZE + 10), offset_y + i * (GRID_SIZE + 10)
                x1, y1 = offset_x + GRID_SIZE + j * (GRID_SIZE + 10), offset_y + GRID_SIZE + i * (GRID_SIZE + 10)
                color = colors.pop()
                square = self.canvas.create_rectangle(x0, y0, x1, y1, fill='white', outline='black', tags="grid")
                self.grid_colors[square] = color

    def create_legend(self):
        legend_x = 50
        legend_y = 50
        legend_width = 20
        legend_height = 20
        gap = 10
        box_colors = {
            'black': 'Generierte Box',
            'orange': 'Vom Greifarm aufgenommene Box',
            'red': 'Nicht richtig platzierte Box',
            'green': 'Richtig platzierte Box'
        }

        for i, (color, description) in enumerate(box_colors.items()):
            self.canvas.create_rectangle(legend_x, legend_y + i * (legend_height + gap),
                                         legend_x + legend_width, legend_y + legend_height + i * (legend_height + gap),
                                         fill=color)
            self.canvas.create_text(legend_x + legend_width + gap, legend_y + legend_height / 2 + i * (legend_height + gap),
                                    text=description, anchor='w')

    def on_press(self, event):
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

    def on_release(self, event):
        self.dragging = False

    def on_right_click(self, event):
        if self.selected_box:
            box_coords = self.canvas.coords(self.selected_box)
            for square in self.canvas.find_withtag("grid"):
                square_coords = self.canvas.coords(square)
                print(square_coords)
                print(event.x)
                print(event.y)
                if self.is_inside(square_coords, box_coords):
                    self.canvas.itemconfig(self.selected_box, outline="green")
                    self.canvas.coords(self.selected_box, square_coords[0], square_coords[1], square_coords[2],
                                       square_coords[3])
                    break
                else:
                    self.canvas.itemconfig(self.selected_box, outline="red")
            self.selected_box = None
        else:
            items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
            for item in items:
                if item in self.canvas.find_withtag("box"):
                    self.selected_box = item
                    self.canvas.itemconfig(self.selected_box, outline="orange")

    def is_near_end_effector(self, x, y):
        ex, ey = self.robotic_arm.end_effector_pos
        return np.hypot(ex - x, ey - y) < 10

    def draw_robotic_arm(self):
        self.canvas.delete("arm")

        shoulder_pos = self.robotic_arm.shoulder_pos
        elbow_pos = shoulder_pos + np.array([ARM_LENGTH_1 * np.cos(self.robotic_arm.shoulder_angle),
                                             ARM_LENGTH_1 * np.sin(self.robotic_arm.shoulder_angle)])
        if self.robotic_arm.num_joints == 1:
            end_effector_pos = elbow_pos
        elif self.robotic_arm.num_joints == 2:
            end_effector_pos = elbow_pos + np.array(
                [ARM_LENGTH_2 * np.cos(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle),
                 ARM_LENGTH_2 * np.sin(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle)])
        elif self.robotic_arm.num_joints == 3:
            wrist_pos = elbow_pos + np.array(
                [ARM_LENGTH_2 * np.cos(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle),
                 ARM_LENGTH_2 * np.sin(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle)])
            end_effector_pos = wrist_pos + np.array(
                [ARM_LENGTH_3 * np.cos(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle + self.robotic_arm.wrist_angle),
                 ARM_LENGTH_3 * np.sin(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle + self.robotic_arm.wrist_angle)])

        self.canvas.create_line(shoulder_pos[0], shoulder_pos[1], elbow_pos[0], elbow_pos[1], width=5, fill='blue',
                                tags="arm")

        if self.robotic_arm.num_joints >= 2:
            self.canvas.create_line(elbow_pos[0], elbow_pos[1], end_effector_pos[0], end_effector_pos[1], width=5,
                                    fill='blue', tags="arm")

        if self.robotic_arm.num_joints == 3:
            wrist_pos = elbow_pos + np.array(
                [ARM_LENGTH_2 * np.cos(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle),
                 ARM_LENGTH_2 * np.sin(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle)])
            self.canvas.create_line(wrist_pos[0], wrist_pos[1], end_effector_pos[0], end_effector_pos[1], width=5,
                                    fill='blue', tags="arm")

        self.canvas.create_oval(end_effector_pos[0] - 5, end_effector_pos[1] - 5, end_effector_pos[0] + 5,
                                end_effector_pos[1] + 5, fill='blue', tags="arm")

    def check_positions(self):
        correct_positions = 0
        for box in self.canvas.find_withtag("box"):
            box_color = self.box_colors[box]
            box_coords = self.canvas.coords(box)
            for square in self.canvas.find_withtag("grid"):
                square_color = self.grid_colors[square]
                square_coords = self.canvas.coords(square)
                if self.is_inside(square_coords, box_coords) and box_color == square_color:
                    correct_positions += 1
        if correct_positions == 4:
            print("Herzlichen Glückwunsch! Alle Kästen sind korrekt platziert!")
        else:
            print(f"{correct_positions} von 4 Kästen sind korrekt platziert.")

    def is_inside(self, square_coords, box_coords):
        tolerance = 3
        return (square_coords[0] - tolerance <= box_coords[0] and
                square_coords[1] - tolerance <= box_coords[1] and
                square_coords[2] + tolerance >= box_coords[2] and
                square_coords[3] + tolerance >= box_coords[3])

# Hauptfunktion
def main():
    root = tk.Tk()
    root.title("Robotic Arm Simulation")

    gui = GUI(root)

    root.mainloop()

if __name__ == "__main__":
    main()
