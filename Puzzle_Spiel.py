import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import random
import os
from scipy.optimize import least_squares

# Konstanten für die Bildschirmgröße und den Roboterarm
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
ARM_LENGTH_1, ARM_LENGTH_2, ARM_LENGTH_3 = 150, 150, 150
BOX_SIZE = 50
GRID_SIZE = 50

# Klasse für den Roboterarm
class RoboticArm:
    # initialisiert den Roboter Arm mit Startwerten
    def __init__(self, num_joints=2):

        #Anzahl der Gelenke
        self.num_joints = num_joints

        #Winkel vom Roboterarm
        self.shoulder_angle = 0
        self.elbow_angle = 0
        self.wrist_angle = 0

        #Positionen vom Roboterarm
        self.shoulder_pos = np.array([400, SCREEN_HEIGHT / 2]) #ist ja fest woher der Roboterarm startet
        self.elbow_pos = 0
        self.wrist_pos = 0

        #Hilfsvariabeln für 3 Gelenke
        self.initial_guess = [0, 0, 0]
        self.result = [0, 0, 0]

        #Abstand zu Zielposition
        self.dx = 0
        self.dy = 0

        #armlängen
        self.arm_lengths = [ARM_LENGTH_1, ARM_LENGTH_2, ARM_LENGTH_3]

        #Endeffektor berechnen
        self.update_end_effector()

    # Setter für Anzahl der Gelenke
    def set_num_joints(self, num_joints):
        self.num_joints = num_joints
        self.update_end_effector()

    # Setter für Länge der Armteile
    def set_arm_length(self, index, length):
        self.arm_lengths[index] = length
        self.update_end_effector()

    # berechnet Winkel für alle Roboterarme
    def move_to(self, target):
        #berechnet distanz von der Schulterposition zur Zielposition
        self.dx, self.dy = target[0] - self.shoulder_pos[0], target[1] - self.shoulder_pos[1]
        distance = np.hypot(self.dx, self.dy) # x**2 + y**2 = distance**2

        # Fall: 1 Gelenk
        if self.num_joints == 1:

            # distance kann nur so groß sein wie armlänge
            distance = min(distance, self.arm_lengths[0])

            # braucht ja nur einen Winkel:
            self.shoulder_angle = np.arctan2(self.dy, self.dx) # winkel = tan**-1(x/y)


        # Fall: 2 Gelenke
        elif self.num_joints == 2:

            # distance kann nur so groß sein wie armlängen zsm
            distance = min(distance, self.arm_lengths[0] + self.arm_lengths[1])

            #Kosinussatz c**2 = a**2 + b**2 - 2ab*cos(winkel)
            cos_angle2 = (distance ** 2 - self.arm_lengths[0] ** 2 - self.arm_lengths[1] ** 2) / (2 * self.arm_lengths[0] * self.arm_lengths[1])
            cos_angle2 = np.clip(cos_angle2, -1, 1)
            self.elbow_angle = np.arccos(cos_angle2)

            #berechnen schulterwinkel
            self.shoulder_angle = np.arctan2(self.dy, self.dx) - np.arctan2(self.arm_lengths[1] * np.sin(self.elbow_angle),
                                                                            self.arm_lengths[0] + self.arm_lengths[1] * np.cos(self.elbow_angle))

        # Fall: 3 Gelenke

        #Variante 1
        #        elif self.num_joints == 3:
        #            # Begrenzung der maximalen Reichweite des Arms
        #            if distance > sum(self.arm_lengths):
        #                distance = sum(self.arm_lengths)
        #                target = self.shoulder_pos + distance * np.array([self.dx, self.dy]) / distance
        #
        #            # Berechnung der Winkel für die einzelnen Segmente
        #            cos_angle2 = (distance**2 - self.arm_lengths[0]**2 - self.arm_lengths[1]**2) / (2 * self.arm_lengths[0] * self.arm_lengths[1])
        #            cos_angle2 = np.clip(cos_angle2, -1.0, 1.0)
        #            self.elbow_angle = np.arccos(cos_angle2)
        #
        #            k1 = self.arm_lengths[0] + self.arm_lengths[1] * cos_angle2
        #            k2 = self.arm_lengths[1] * np.sin(self.elbow_angle)
        #            self.shoulder_angle = np.arctan2(self.dy, self.dx) - np.arctan2(k2, k1)
        #
        #            # Berechnung des Handgelenkwinkels
        #            wrist_target = target - np.array([self.arm_lengths[2] * np.cos(self.shoulder_angle + self.elbow_angle), self.arm_lengths[2] * np.sin(self.shoulder_angle + self.elbow_angle)])
        #            wrist_dx, wrist_dy = wrist_target[0] - self.shoulder_pos[0], wrist_target[1] - self.shoulder_pos[1]
        #            wrist_angle1 = np.arctan2(wrist_dy, wrist_dx)
        #            self.wrist_angle = self.shoulder_angle + self.elbow_angle - wrist_angle1

        #Variante 2
        elif self.num_joints == 3:

            self.initial_guess = [self.shoulder_angle, self.elbow_angle, self.wrist_angle]

            self.result = least_squares(self.equations, self.initial_guess)

            self.shoulder_angle, self.elbow_angle, self.wrist_angle = self.result.x



        self.update_end_effector()

    def equations(self, angles):
        alpha, beta, gamma = angles
        # Kumulierte Winkel
        total_alpha = alpha
        total_beta = alpha + beta
        total_gamma = alpha + beta + gamma
        return [
            self.arm_lengths[0] * np.cos(total_alpha) + self.arm_lengths[1] * np.cos(total_beta) + self.arm_lengths[2] * np.cos(total_gamma) - self.dx,
            self.arm_lengths[0] * np.sin(total_alpha) + self.arm_lengths[1] * np.sin(total_beta) + self.arm_lengths[2] * np.sin(total_gamma) - self.dy
        ]

    # Position des Endeffektors
    def update_end_effector(self):
        if self.num_joints == 1:
            self.elbow_pos = self.shoulder_pos + np.array([self.arm_lengths[0] * np.cos(self.shoulder_angle),
                                                           self.arm_lengths[0] * np.sin(self.shoulder_angle)])
            self.end_effector_pos = self.elbow_pos
        elif self.num_joints == 2:
            self.elbow_pos = self.shoulder_pos + np.array([self.arm_lengths[0] * np.cos(self.shoulder_angle),
                                                           self.arm_lengths[0] * np.sin(self.shoulder_angle)])
            self.end_effector_pos = self.elbow_pos + np.array([self.arm_lengths[1] * np.cos(self.shoulder_angle + self.elbow_angle),
                                                               self.arm_lengths[1] * np.sin(self.shoulder_angle + self.elbow_angle)])
        elif self.num_joints == 3:
            self.elbow_pos = self.shoulder_pos + np.array([self.arm_lengths[0] * np.cos(self.shoulder_angle),
                                                           self.arm_lengths[0] * np.sin(self.shoulder_angle)])
            self.wrist_pos = self.elbow_pos + np.array([self.arm_lengths[1] * np.cos(self.shoulder_angle + self.elbow_angle),
                                                        self.arm_lengths[1] * np.sin(self.shoulder_angle + self.elbow_angle)])
            self.end_effector_pos = self.wrist_pos + np.array([self.arm_lengths[2] * np.cos(self.shoulder_angle + self.elbow_angle + self.wrist_angle),
                                                               self.arm_lengths[2] * np.sin(self.shoulder_angle + self.elbow_angle + self.wrist_angle)])

# Klasse für die GUI
class GUI:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg='white')
        self.canvas.pack()

        # initialisiert den Roboterarm
        self.robotic_arm = RoboticArm()
        self.draw_robotic_arm()

        # initialisiert dei Werte für Drag and Drop
        self.selected_piece = None
        self.dragging = False

        # Eventlistener für die Maus
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)

        # erstellen der Puzzleteile
        self.create_grid()
        self.create_puzzle_pieces()
        self.create_legend()

        # erstellen des Menüs
        self.create_config_panel()

        # Button zum Überprüfen der Puzzleteile
        self.check_button = tk.Button(master, text="Check Positions", command=self.check_positions)
        self.check_button.pack()

    # Panel für das Menü
    def create_config_panel(self):
        config_frame = tk.Frame(self.master, bd=2, relief=tk.RIDGE)
        config_frame.place(x=SCREEN_WIDTH - 250, y=10, width=220, height=320)

        tk.Label(config_frame, text="Konfiguration").pack(pady=10)
        tk.Label(config_frame, text="Anzahl der Gelenke:").pack()

        self.num_joints_var = tk.IntVar(value=2)
        joints_option_menu = tk.OptionMenu(config_frame, self.num_joints_var, 1, 2, 3, command=self.update_num_joints)
        joints_option_menu.pack(pady=5)

        tk.Label(config_frame, text="Armlänge 1:").pack()
        self.arm_length1_slider = tk.Scale(config_frame, from_=50, to_=300, orient=tk.HORIZONTAL, command=self.update_arm_length1)
        self.arm_length1_slider.set(ARM_LENGTH_1)
        self.arm_length1_slider.pack()

        self.arm_length2_label = tk.Label(config_frame, text="Armlänge 2:")
        self.arm_length2_label.pack()
        self.arm_length2_slider = tk.Scale(config_frame, from_=50, to_=300, orient=tk.HORIZONTAL, command=self.update_arm_length2)
        self.arm_length2_slider.set(ARM_LENGTH_2)
        self.arm_length2_slider.pack()

        self.arm_length3_label = tk.Label(config_frame, text="Armlänge 3:")
        self.arm_length3_label.pack()
        self.arm_length3_slider = tk.Scale(config_frame, from_=50, to_=300, orient=tk.HORIZONTAL, command=self.update_arm_length3)
        self.arm_length3_slider.set(ARM_LENGTH_3)
        self.arm_length3_slider.pack()

    # updatet Anzahl der Gelenke
    def update_num_joints(self, value):
        value = int(value)
        if value >= 2:
            self.arm_length2_label.pack()
            self.arm_length2_slider.pack()
        else:
            self.arm_length2_label.pack_forget()
            self.arm_length2_slider.pack_forget()
        if value == 3:
            self.arm_length3_label.pack()
            self.arm_length3_slider.pack()
        else:
            self.arm_length3_label.pack_forget()
            self.arm_length3_slider.pack_forget()

        self.robotic_arm.set_num_joints(int(value))
        self.draw_robotic_arm()

    # aktualisiert den Roboterarm nach ändern des ersten Arms
    def update_arm_length1(self, value):
        self.robotic_arm.set_arm_length(0, int(value))
        self.draw_robotic_arm()

    # aktualisiert den Roboterarm nach ändern des zweiten Arms
    def update_arm_length2(self, value):
        self.robotic_arm.set_arm_length(1, int(value))
        self.draw_robotic_arm()

    # aktualisiert den Roboterarm nach ändern des dritten Arms
    def update_arm_length3(self, value):
        self.robotic_arm.set_arm_length(2, int(value))
        self.draw_robotic_arm()

    # erstellt die Puzzleteile
    def create_puzzle_pieces(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "math-puzzles-image.jpg")
        self.puzzle_image = Image.open(image_path)
        self.puzzle_image = self.puzzle_image.resize((2 * GRID_SIZE, 2 * GRID_SIZE), Image.Resampling.LANCZOS)
        self.puzzle_pieces = []
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)] # 2x2 Grid
        random.shuffle(positions) # zufällige Anordnung der Teile
        for i in range(2):
            for j in range(2):
                box_image = self.puzzle_image.crop((j * GRID_SIZE, i * GRID_SIZE, (j + 1) * GRID_SIZE, (i + 1) * GRID_SIZE))
                box_image = ImageTk.PhotoImage(box_image)
                pos = positions.pop()
                piece = self.canvas.create_image(450 + pos[0] * (BOX_SIZE + 10), SCREEN_HEIGHT / 2 - 100 + pos[1] * (BOX_SIZE + 10), image=box_image, tags="puzzle_piece")
                self.canvas.tag_bind(piece, "<Button-3>", self.on_right_click)
                self.puzzle_pieces.append((piece, (i, j), box_image))
                self.canvas.tag_raise(piece)

    # erstellt Grid für das Puzzle
    def create_grid(self):
        offset_x = 600
        offset_y = SCREEN_HEIGHT / 2 - 100
        self.grid_positions = {}
        for i in range(2):
            for j in range(2):
                x0, y0 = offset_x + j * GRID_SIZE, offset_y + i * GRID_SIZE
                x1, y1 = offset_x + GRID_SIZE + j * GRID_SIZE, offset_y + GRID_SIZE + i * GRID_SIZE
                square = self.canvas.create_rectangle(x0, y0, x1, y1, fill='white', outline='black', tags="grid")
                self.grid_positions[square] = (i, j)

    # Legende oben links
    def create_legend(self):
        legend_items = ["Mit der linken Maustaste den Greifarm an die gewünschte Position verschieben",
                        "Zum Aufnehmen eines Puzzleteils Rechtsklick verwenden"]
        for index, text in enumerate(legend_items):
            self.canvas.create_text(50, 30 + index * 20, text=text, anchor='w')

    # Endeffektor auswählen
    def on_press(self, event):
        if self.is_near_end_effector(event.x, event.y):
            self.dragging = True

    # Arm bewegen
    def on_drag(self, event):
        if self.dragging:
            target = np.array([event.x, event.y])
            self.robotic_arm.move_to(target)
            self.draw_robotic_arm()
            if self.selected_piece:
                piece, pos, box_image = self.selected_piece
                ex, ey = self.robotic_arm.end_effector_pos
                self.canvas.coords(piece, ex, ey)

    # Arm loslassen
    def on_release(self, event):
        self.dragging = False

    # Puzzleteil wenn möglich aufheben
    def on_right_click(self, event):
        if self.selected_piece:
            piece, pos, box_image = self.selected_piece
            piece_coords = self.canvas.coords(piece)
            for square in self.canvas.find_withtag("grid"):
                square_coords = self.canvas.coords(square)
                if self.is_inside(square_coords, piece_coords):
                    self.canvas.coords(piece, square_coords[0] + (BOX_SIZE / 2), square_coords[1] + (BOX_SIZE / 2))
                    break
            self.selected_piece = None
        else:
            items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
            for item in items:
                if item in [piece for piece, pos, box_image in self.puzzle_pieces]:
                    self.selected_piece = [(piece, pos, box_image) for piece, pos, box_image in self.puzzle_pieces if piece == item][0]
                    piece, pos, box_image = self.selected_piece
                    ex, ey = self.robotic_arm.end_effector_pos
                    self.canvas.coords(piece, ex, ey)

    # definiert Feld in dem der Endeffektor ausgewählt weredn kann
    def is_near_end_effector(self, x, y):
        ex, ey = self.robotic_arm.end_effector_pos
        return np.hypot(ex - x, ey - y) < 10

    # Arm zeichnen
    def draw_robotic_arm(self):
        self.canvas.delete("arm")
        self.shoulder_pos = self.robotic_arm.shoulder_pos
        self.elbow_pos = self.shoulder_pos + np.array([self.robotic_arm.arm_lengths[0] * np.cos(self.robotic_arm.shoulder_angle),
                                                       self.robotic_arm.arm_lengths[0] * np.sin(self.robotic_arm.shoulder_angle)])
        if self.robotic_arm.num_joints == 1:
            self.end_effector_pos = self.elbow_pos
        elif self.robotic_arm.num_joints == 2:
            self.end_effector_pos = self.elbow_pos + np.array([self.robotic_arm.arm_lengths[1] * np.cos(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle),
                                                               self.robotic_arm.arm_lengths[1] * np.sin(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle)])
        elif self.robotic_arm.num_joints == 3:
            # Zeichnet den Roboterarm auf der Leinwand

            self.wrist_pos = self.elbow_pos + np.array([self.robotic_arm.arm_lengths[1] * np.cos(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle),
                                                        self.robotic_arm.arm_lengths[1] * np.sin(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle)])
            self.end_effector_pos = self.wrist_pos + np.array([self.robotic_arm.arm_lengths[2] * np.cos(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle + self.robotic_arm.wrist_angle),
                                                               self.robotic_arm.arm_lengths[2] * np.sin(self.robotic_arm.shoulder_angle + self.robotic_arm.elbow_angle + self.robotic_arm.wrist_angle)])

        # Zeichnen des ersten Arms
        self.canvas.create_line(self.robotic_arm.shoulder_pos[0], self.robotic_arm.shoulder_pos[1], self.robotic_arm.elbow_pos[0], self.robotic_arm.elbow_pos[1], width=5, fill='blue', tags="arm")
        if self.robotic_arm.num_joints == 2:
            self.canvas.create_line(self.robotic_arm.elbow_pos[0], self.robotic_arm.elbow_pos[1], self.robotic_arm.end_effector_pos[0], self.robotic_arm.end_effector_pos[1], width=5, fill='blue', tags="arm")
        if self.robotic_arm.num_joints == 3:
            # Zeichnen des zweiten Arms
            self.canvas.create_line(self.robotic_arm.elbow_pos[0], self.robotic_arm.elbow_pos[1], self.robotic_arm.wrist_pos[0], self.robotic_arm.wrist_pos[1], width=5, fill='blue', tags="arm")
            # Zeichnen des dritten Arms
            self.canvas.create_line(self.robotic_arm.wrist_pos[0], self.robotic_arm.wrist_pos[1], self.robotic_arm.end_effector_pos[0], self.robotic_arm.end_effector_pos[1], width=5, fill='blue', tags="arm")

        self.canvas.create_oval(self.robotic_arm.end_effector_pos[0] - 5, self.robotic_arm.end_effector_pos[1] - 5, self.robotic_arm.end_effector_pos[0] + 5, self.robotic_arm.end_effector_pos[1] + 5, fill='blue', tags="arm")

    # überprüft ob die Puzzleteile richtig liegen
    def check_positions(self):
        correct_positions = 0
        for piece, pos, box_image in self.puzzle_pieces:
            piece_coords = self.canvas.coords(piece)
            for square in self.canvas.find_withtag("grid"):
                grid_pos = self.grid_positions[square]
                square_coords = self.canvas.coords(square)
                if self.is_inside(square_coords, piece_coords) and pos == grid_pos:
                    correct_positions += 1
        if correct_positions == 4:
            print("Herzlichen Glückwunsch! Alle Puzzleteile sind korrekt platziert!")
        else:
            print(f"{correct_positions} von 4 Puzzleteilen sind korrekt platziert.")

    # guckt ob das Puzzleteil im Grid liegt
    def is_inside(self, square_coords, piece_coords):
        tolerance = 3
        piece_x0 = piece_coords[0] - BOX_SIZE / 2
        piece_y0 = piece_coords[1] - BOX_SIZE / 2
        piece_x1 = piece_coords[0] + BOX_SIZE / 2
        piece_y1 = piece_coords[1] + BOX_SIZE / 2
        return (square_coords[0] - tolerance <= piece_x0 and
                square_coords[1] - tolerance <= piece_y0 and
                square_coords[2] + tolerance >= piece_x1 and
                square_coords[3] + tolerance >= piece_y1)

# Hauptfunktion
def main():
    root = tk.Tk()
    root.title("Robotic Arm Simulation")
    gui = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
