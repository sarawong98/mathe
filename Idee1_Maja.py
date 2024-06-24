import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Konstanten für den Roboterarm
ARM_LENGTH_1 = 150
ARM_LENGTH_2 = 150
BOX_SIZE = 50
GRID_SIZE = 50

# Klasse für den Roboterarm
class RoboticArm:
    def __init__(self):
        self.shoulder_angle = np.pi / 4  # Initialer Winkel
        self.elbow_angle = np.pi / 4     # Initialer Winkel
        self.shoulder_pos = np.array([0, 0, 0])
        self.end_effector_pos = np.array([ARM_LENGTH_1 + ARM_LENGTH_2, 0, 0])
        self.update_end_effector()

    def move_to(self, target):
        dx, dy = target[0] - self.shoulder_pos[0], target[1] - self.shoulder_pos[1]
        distance = np.sqrt(dx**2 + dy**2)

        if distance > ARM_LENGTH_1 + ARM_LENGTH_2:
            distance = ARM_LENGTH_1 + ARM_LENGTH_2

        cos_angle2 = (distance**2 - ARM_LENGTH_1**2 - ARM_LENGTH_2**2) / (2 * ARM_LENGTH_1 * ARM_LENGTH_2)
        cos_angle2 = np.clip(cos_angle2, -1, 1)

        angle2 = np.arccos(cos_angle2)
        angle1 = np.arctan2(dy, dx) - np.arctan2(ARM_LENGTH_2 * np.sin(angle2), ARM_LENGTH_1 + ARM_LENGTH_2 * np.cos(angle2))

        self.shoulder_angle = angle1
        self.elbow_angle = angle2
        self.update_end_effector()

    def update_end_effector(self):
        elbow_pos = self.shoulder_pos + np.array([ARM_LENGTH_1 * np.cos(self.shoulder_angle), ARM_LENGTH_1 * np.sin(self.shoulder_angle), 0])
        self.end_effector_pos = elbow_pos + np.array([ARM_LENGTH_2 * np.cos(self.shoulder_angle + self.elbow_angle), ARM_LENGTH_2 * np.sin(self.shoulder_angle + self.elbow_angle), 0])

    def get_joint_positions(self):
        elbow_pos = self.shoulder_pos + np.array([ARM_LENGTH_1 * np.cos(self.shoulder_angle), ARM_LENGTH_1 * np.sin(self.shoulder_angle), 0])
        return self.shoulder_pos, elbow_pos, self.end_effector_pos

# Initialisiere Roboterarm
robotic_arm = RoboticArm()

# Puzzleteile und Gitter
puzzle_pieces = [
    np.array([450, 0, 150]),
    np.array([450, 0, 250]),
    np.array([450, 0, 350]),
    np.array([450, 0, 450])
]

grid_positions = [
    np.array([600, 0, 250]),
    np.array([650, 0, 250]),
    np.array([600, 0, 300]),
    np.array([650, 0, 300])
]

selected_piece = None

# Erstelle die 3D-Grafik
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-300, 700])
ax.set_ylim([-300, 300])
ax.set_zlim([0, 600])
ax.view_init(elev=20., azim=30)

dragging = False

def on_press(event):
    global dragging, selected_piece
    if event.inaxes != ax:
        return

    if event.button == 1:  # Linke Maustaste
        ex, ey, ez = robotic_arm.end_effector_pos
        if np.linalg.norm(np.array([event.xdata, event.ydata, 0]) - np.array([ex, ey, ez])) < 20:
            dragging = True

        for piece in puzzle_pieces:
            if np.linalg.norm(np.array([event.xdata, event.ydata, 0]) - np.array([piece[0], piece[1], piece[2]])) < 20:
                selected_piece = piece
                break

def on_release(event):
    global dragging, selected_piece
    dragging = False
    selected_piece = None

def on_motion(event):
    global dragging, selected_piece
    if dragging and event.inaxes == ax:
        target = np.array([event.xdata, event.ydata, 0])
        robotic_arm.move_to(target)
        update_plot()
    elif selected_piece is not None and event.inaxes == ax:
        selected_piece[0] = event.xdata
        selected_piece[1] = event.ydata
        selected_piece[2] = event.ydata  # Für 3D-Betrachtung
        update_plot()

def disable_default_mouse_interactions():
    fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)
    ax.get_proj = lambda: np.dot(Axes3D.get_proj(ax), np.diag([1, 1, 1, 1]))

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
disable_default_mouse_interactions()

def update_plot():
    ax.clear()
    ax.set_xlim([-300, 700])
    ax.set_ylim([-300, 300])
    ax.set_zlim([0, 600])

    shoulder_pos, elbow_pos, end_effector_pos = robotic_arm.get_joint_positions()
    
    # Zeichne den Roboterarm
    ax.plot([shoulder_pos[0], elbow_pos[0]], [shoulder_pos[1], elbow_pos[1]], [shoulder_pos[2], elbow_pos[2]], 'b-')
    ax.plot([elbow_pos[0], end_effector_pos[0]], [elbow_pos[1], end_effector_pos[1]], [elbow_pos[2], end_effector_pos[2]], 'r-')
    
    # Zeichne die Gelenkpunkte
    ax.scatter(shoulder_pos[0], shoulder_pos[1], shoulder_pos[2], color='blue', s=100)
    ax.scatter(elbow_pos[0], elbow_pos[1], elbow_pos[2], color='green', s=100)
    ax.scatter(end_effector_pos[0], end_effector_pos[1], end_effector_pos[2], color='red', s=100)
    
    # Zeichne die Puzzleteile
    for piece in puzzle_pieces:
        ax.scatter(piece[0], piece[1], piece[2], color='red', s=BOX_SIZE)
    
    # Zeichne das Gitter
    for grid_pos in grid_positions:
        ax.scatter(grid_pos[0], grid_pos[1], grid_pos[2], color='black', s=GRID_SIZE)

    plt.draw()

# Initiale Zeichnung
update_plot()

plt.show()
