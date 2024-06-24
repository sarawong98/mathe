import tkinter as tk
import numpy as np

# Konstanten für die Bildschirmgröße und den Roboterarm
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
ARM_LENGTH_1, ARM_LENGTH_2 = 150, 150
BOX_SIZE = 50
GRID_SIZE = 50

# Klasse für den Roboterarm
class RoboticArm:
    def __init__(self):
        self.shoulder_angle = 0
        self.elbow_angle = 0
        self.shoulder_pos = np.array([400, SCREEN_HEIGHT/2])
        self.end_effector_pos = self.shoulder_pos + np.array([ARM_LENGTH_1 + ARM_LENGTH_2, 0])

    def move_to(self, target):
        # Inverse Kinematik zur Berechnung der Gelenkwinkel
        dx, dy = target[0] - self.shoulder_pos[0], target[1] - self.shoulder_pos[1]
        distance = np.hypot(dx, dy)

        if distance > ARM_LENGTH_1 + ARM_LENGTH_2:
            distance = ARM_LENGTH_1 + ARM_LENGTH_2

        cos_angle2 = (distance**2 - ARM_LENGTH_1**2 - ARM_LENGTH_2**2) / (2 * ARM_LENGTH_1 * ARM_LENGTH_2)
        if cos_angle2 < -1:
            cos_angle2 = -1
        elif cos_angle2 > 1:
            cos_angle2 = 1

        angle2 = np.arccos(cos_angle2)
        angle1 = np.arctan2(dy, dx) - np.arctan2(ARM_LENGTH_2 * np.sin(angle2), ARM_LENGTH_1 + ARM_LENGTH_2 * np.cos(angle2))

        self.shoulder_angle = angle1
        self.elbow_angle = angle2
        self.update_end_effector()

    def update_end_effector(self):
        elbow_pos = self.shoulder_pos + np.array([ARM_LENGTH_1 * np.cos(self.shoulder_angle), ARM_LENGTH_1 * np.sin(self.shoulder_angle)])
        self.end_effector_pos = elbow_pos + np.array([ARM_LENGTH_2 * np.cos(self.shoulder_angle + self.elbow_angle), ARM_LENGTH_2 * np.sin(self.shoulder_angle + self.elbow_angle)])

# Klasse für die GUI
class GUI:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg='white')
        self.canvas.pack()

        self.robotic_arm = RoboticArm()
        self.draw_robotic_arm()

        self.selected_box = None  # Variable zur Speicherung des ausgewählten Kastens
        self.dragging = False

        # Event-Listener für Drag-and-Drop
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)

        self.create_grid()
        self.create_red_boxes()

    def create_red_boxes(self):
        offset_x = 450
        offset_y = SCREEN_HEIGHT / 2 - 150
        for i in range(4):
            box = self.canvas.create_rectangle(offset_x, offset_y + i * (BOX_SIZE + 10), offset_x + BOX_SIZE, offset_y + BOX_SIZE + i * (BOX_SIZE + 10), fill='red', outline='white', tags="box")
            self.canvas.tag_bind(box, "<Button-3>", self.on_right_click)

    def create_grid(self):
        offset_x = 600
        offset_y = SCREEN_HEIGHT / 2 - 50
        for i in range(2):
            for j in range(2):
                x0, y0 = offset_x + j * (GRID_SIZE + 10), offset_y + i * (GRID_SIZE + 10)
                x1, y1 = offset_x + GRID_SIZE + j * (GRID_SIZE + 10), offset_y + GRID_SIZE + i * (GRID_SIZE + 10)
                self.canvas.create_rectangle(x0, y0, x1, y1, fill='white', outline='black')

    def on_press(self, event):
        if self.is_near_end_effector(event.x, event.y):
            self.dragging = True


    def on_drag(self, event):
        if self.dragging:
            target = np.array([event.x, event.y])
            self.robotic_arm.move_to(target)
            self.draw_robotic_arm()

            # Bewegung des ausgewählten Kastens
            if self.selected_box:
                ex, ey = self.robotic_arm.end_effector_pos
                self.canvas.coords(self.selected_box, ex - BOX_SIZE / 2, ey - BOX_SIZE / 2, ex + BOX_SIZE / 2, ey + BOX_SIZE / 2)

    def on_release(self, event):
        self.dragging = False

    def on_right_click(self, event):
        if self.selected_box:
            self.canvas.itemconfig(self.selected_box, outline="")
            self.selected_box = None
        else:
            items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
            for item in items:
                if item in self.canvas.find_withtag("box"):
                    self.selected_box = item
                    self.canvas.itemconfig(self.selected_box, outline="black")
                    

    def is_near_end_effector(self, x, y):
        ex, ey = self.robotic_arm.end_effector_pos
        return np.hypot(ex - x, ey - y) < 10

    def draw_robotic_arm(self):
        self.canvas.delete("arm")
        
        shoulder_pos = self.robotic_arm.shoulder_pos
        elbow_pos = shoulder_pos + np.array([ARM_LENGTH_1 * np.cos(self.robotic_arm.shoulder_angle), ARM_LENGTH_1 * np.sin(self.robotic_arm.shoulder_angle)])
        end_effector_pos = elbow_pos + np.array([ARM_LENGTH_2 * np.cos(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle), ARM_LENGTH_2 * np.sin(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle)])

        # Zeichnen des ersten Arms
        self.canvas.create_line(shoulder_pos[0], shoulder_pos[1], elbow_pos[0], elbow_pos[1], width=5, fill='blue', tags="arm")

        # Zeichnen des zweiten Arms
        self.canvas.create_line(elbow_pos[0], elbow_pos[1], end_effector_pos[0], end_effector_pos[1], width=5, fill='blue', tags="arm")

        # Zeichnen des Endeffektors
        self.canvas.create_oval(end_effector_pos[0] - 5, end_effector_pos[1] - 5, end_effector_pos[0] + 5, end_effector_pos[1] + 5, fill='blue', tags="arm")


# Hauptfunktion
def main():
    root = tk.Tk()
    root.title("Robotic Arm Simulation")

    gui = GUI(root)

    root.mainloop()

if __name__ == "__main__":
    main()
