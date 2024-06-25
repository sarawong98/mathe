import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

def Endeffektor_ausrechnen(length, winkel):
    rad = np.radians(winkel)  # Winkel in Radianten umwandeln
    xOderYLength = length * np.cos(rad)
    zlength = length * np.sin(rad)
    return xOderYLength, zlength


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Greifarm")
        
        # Erstellen der 3D Grafik
        self.fig, self.ax = plt.subplots(subplot_kw={'projection': '3d'})

        #hauptarm
        self.line, = self.ax.plot([0, 0], [0, 0], [10, 0], 'r-')
        
        # Ende des Hauptarms
        tip_x = 0
        tip_y = 0
        tip_z = 0

        # Länge und Richtung der ersten Reihe zusätzlichen Striche
        xOderYLength1, zlength1 = Endeffektor_ausrechnen(2, 315)
        self.line1, = self.ax.plot([tip_x, tip_x + xOderYLength1], [tip_y, tip_y], [tip_z, tip_z + zlength1], 'm-')  # Nach rechts
        self.line2, = self.ax.plot([tip_x, tip_x - xOderYLength1], [tip_y, tip_y], [tip_z, tip_z + zlength1], 'm-')  # Nach links
        self.line3, = self.ax.plot([tip_x, tip_x], [tip_y, tip_y - xOderYLength1], [tip_z, tip_z + zlength1], 'm-')  # Nach vor
        self.line4, = self.ax.plot([tip_x, tip_x], [tip_y, tip_y + xOderYLength1], [tip_z, tip_z + zlength1], 'm-')  # Nach zurueck

        # Länge und Richtung der zweiten Reihe zusätzlichen Striche
        xOderYLength2, zlength2 = Endeffektor_ausrechnen(2, 270)
        self.line11, = self.ax.plot([tip_x + xOderYLength1, tip_x + xOderYLength1 + xOderYLength2], [tip_y, tip_y], [tip_z + zlength1, tip_z + zlength1 + zlength2], 'b-')  # der rechte nach unten
        self.line21, = self.ax.plot([tip_x - xOderYLength1, tip_x - xOderYLength1 - xOderYLength2], [tip_y, tip_y], [tip_z + zlength1, tip_z + zlength1 + zlength2], 'b-')  # der linke nach unten
        self.line31, = self.ax.plot([tip_x, tip_x], [tip_y - xOderYLength1, tip_y - xOderYLength1 - xOderYLength2], [tip_z + zlength1, tip_z + zlength1 + zlength2], 'b-')  # der vorne nach unten
        self.line41, = self.ax.plot([tip_x, tip_x], [tip_y + xOderYLength1, tip_y + xOderYLength1 + xOderYLength2], [tip_z + zlength1, tip_z + zlength1 + zlength2], 'b-')  # der zurueck nach unten

        # Länge und Richtung der dritten Reihe zusätzlichen Striche
        xOderYLength3, zlength3 = Endeffektor_ausrechnen(1, 270)
        self.line12, = self.ax.plot([tip_x + xOderYLength1 + xOderYLength2, tip_x + xOderYLength1 + xOderYLength2 + xOderYLength3], [tip_y, tip_y], [tip_z + zlength1 + zlength2, tip_z + zlength1 + zlength2 + zlength3], 'g-')  # der rechte nach unten
        self.line22, = self.ax.plot([tip_x - xOderYLength1 - xOderYLength2, tip_x - xOderYLength1 - xOderYLength2 - xOderYLength3], [tip_y, tip_y], [tip_z + zlength1 + zlength2, tip_z + zlength1 + zlength2 + zlength3], 'g-')  # der linke nach unten
        self.line32, = self.ax.plot([tip_x, tip_x], [tip_y - xOderYLength1 - xOderYLength2, tip_y - xOderYLength1 - xOderYLength2 - xOderYLength3], [tip_z + zlength1 + zlength2, tip_z + zlength1 + zlength2 + zlength3], 'g-')  # der vorne nach unten
        self.line42, = self.ax.plot([tip_x, tip_x], [tip_y + xOderYLength1 + xOderYLength2, tip_y + xOderYLength1 + xOderYLength2 + xOderYLength3], [tip_z + zlength1 + zlength2, tip_z + zlength1 + zlength2 + zlength3], 'g-')  # der zurueck nach unten

        # Kugeln auf dem Boden
        kugel_positionen_x = [-5, 5, -5, 5]
        kugel_positionen_y = [-5, 5, 5, -5]
        kugel_positionen_z = [-10, -10, -10, -10]
        self.kugeln = self.ax.scatter(kugel_positionen_x, kugel_positionen_y, kugel_positionen_z, s=600, c='blue', depthshade=True)

        # Buttons zum Bewegen des Strichs in der X- und Z-Richtung und deren Layout
        haupt_frame = tk.Frame(root)
        haupt_frame.pack(side=tk.BOTTOM, pady=20)

        linker_frame = tk.Frame(haupt_frame)
        linker_frame.pack(side=tk.LEFT, padx=10)

        btn_zuruek = tk.Button(linker_frame, text="Zurück", command=lambda: self.move_line(0, 1))
        btn_zuruek.pack(side=tk.TOP)

        mittel_frame = tk.Frame(linker_frame)
        mittel_frame.pack(side=tk.TOP)
        
        btn_links = tk.Button(mittel_frame, text="Links", command=lambda: self.move_line(-1, 0))
        btn_links.pack(side=tk.LEFT)
        btn_rechts = tk.Button(mittel_frame, text="Rechts", command=lambda: self.move_line(1, 0))
        btn_rechts.pack(side=tk.LEFT)

        btn_vor = tk.Button(linker_frame, text="Vor", command=lambda: self.move_line(0, -1))
        btn_vor.pack(side=tk.TOP)

        rechter_frame = tk.Frame(haupt_frame)
        rechter_frame.pack(side=tk.RIGHT)

        btn_greifen = tk.Button(rechter_frame, text="Greifen", command=self.extra_action)
        btn_greifen.pack(side=tk.LEFT)

        # Einbinden der Grafik in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        # Achseneinstellungen
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.ax.set_zlim(-10, 10)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

    """
    def check_collision(line):
        x, y, z = line._verts3d
        end_x, end_y, end_z = x[1], y[1], z[1]  # Endpunkt des Greifers
        for kx, ky, kz in zip(self.kugeln._offsets3d[0], self.kugeln._offsets3d[1], self.kugeln._offsets3d[2]):
            dist = np.sqrt((end_x - kx) ** 2 + (end_y - ky) ** 2 + (end_z - kz) ** 2)
            if dist <= 1.0:  # Angenommener Radius + Toleranz
                print("Kollision erkannt!")
                # Hier könnten Sie weitere Aktionen hinzufügen, z.B. das Entfernen der Kugel oder das Ändern ihrer Farbe
    """
    def GreifarmOeffnen(self, a):
        winkelaenderung = 270 - (a * 15)
        xOderYLength, zlength = Endeffektor_ausrechnen(1, winkelaenderung)

        x1, y1, z1 = self.line12._verts3d
        new_x1 = np.clip(x1 + xOderYLength, -10, 10)
        new_z1 = np.clip(z1 + zlength, -10, 10)
        self.line12.set_data([x1[0], new_x1[1]], [y1[0], y1[0]])
        self.line12.set_3d_properties([z1[0], new_z1[1]])

        x2, y2, z2 = self.line22._verts3d
        new_x2 = np.clip(x2 - xOderYLength, -10, 10)
        new_z2 = np.clip(z2 + zlength, -10, 10)
        self.line22.set_data([x2[0], new_x2[1]], [y2[0], y2[0]])
        self.line22.set_3d_properties([z2[0], new_z2[1]])

        x3, y3, z3 = self.line32._verts3d
        new_y3 = np.clip(y3 - xOderYLength, -10, 10)
        new_z3 = np.clip(z3 + zlength, -10, 10)
        self.line32.set_data([x3[0], x3[0]], [y3[0], new_y3[1]])
        self.line32.set_3d_properties([z3[0], new_z3[1]])

        x4, y4, z4 = self.line42._verts3d
        new_y4 = np.clip(y4 + xOderYLength, -10, 10)
        new_z4 = np.clip(z4 + zlength, -10, 10)
        self.line42.set_data([x4[0], x4[0]], [y4[0], new_y4[1]])
        self.line42.set_3d_properties([z4[0], new_z4[1]])
        

        
        
        
        

    def check_collision(self, x, y, z):
        for kx, ky, kz in zip(self.kugeln._offsets3d[0], self.kugeln._offsets3d[1], self.kugeln._offsets3d[2]):
            dist = np.sqrt((x - kx) ** 2 + (y - ky) ** 2 + (z - kz) ** 2)
            if dist <= 1.0:  # Angenommener Radius + Toleranz
                return True
        return False

    def move_line(self, dx, dy):
        # Aktuelle Position der Hauptlinie abrufen und aktualisieren
        x, y, z = self.line._verts3d
        new_x = np.clip(x + dx, -10, 10)  # Begrenzung auf Achsenbereich
        new_y = np.clip(y + dy, -10, 10)
        self.line.set_data(new_x, new_y)  # aktualisiert die X- und Y-Koordinaten der Linie
        self.line.set_3d_properties(z)  # aktualisiert die Z-Koordinaten der Linie

        # Bewege auch die zusätzlichen Linien
        for line in [self.line1, self.line2, self.line3, self.line4, self.line11, self.line21, self.line31, self.line41, self.line12, self.line22, self.line32, self.line42]: #damit der alle Linien aktualisiert
            x, y, z = line._verts3d
            line.set_data([x[0] + dx, x[1] + dx], [y[0] + dy, y[1] + dy])
            line.set_3d_properties([z[0], z[1]])
        self.canvas.draw()

    def move_line_up_and_down(self, dz):
        # Bewegung der Linien
        x, y, z = self.line._verts3d
        new_z = np.clip(z + dz, -10, 10)
        self.line.set_data([x[0], x[0]], [y[0], y[0]])
        self.line.set_3d_properties([z[0], new_z[1]])
        for line in [self.line1, self.line2, self.line3, self.line4, self.line11, self.line21, self.line31, self.line41, self.line12, self.line22, self.line32, self.line42]:
            x, y, z = line._verts3d
            line.set_data([x[0], x[1]], [y[0], y[1]])
            line.set_3d_properties([z[0] + dz, z[1] + dz])
        self.canvas.draw()

    

    def extra_action(self):
        # Bewegung des Greifarms 5 Schritte nach unten und wieder nach oben
        for _ in range(5):
            self.move_line_up_and_down(-1)
            self.root.update()
            self.root.after(100)  # Wartezeit zwischen den Schritten

        for a in range(3):
            self.GreifarmOeffnen(a)
            self.canvas.draw()
            self.root.update()
            self.root.after(100)

        for _ in range(5):
            self.move_line_up_and_down(1)
            self.root.update()
            self.root.after(100)  # Wartezeit zwischen den Schritten
            
        # Logik für den extra Button
        print("Extra Aktion ausgeführt")

        #self.check_collision(line)


# Hauptfenster erstellen
root = tk.Tk()
app = App(root)
root.mainloop()

"""
        #arme zusammen gehen und kugel greifen
                    # Arme zusammenführen
        collision_detected = False
        for _ in range(5):
            self.arme_zusammengreifen(1)
            self.root.update()
            self.root.after(100)  # Wartezeit zwischen den Schritten



            
def arme_zusammengreifen(self, schritt):
            self.line1.set_data([tip_x, tip_x], [tip_y, tip_y])
            self.line1.set_3d_properties([tip_z, tip_z])


            self.line2.set_data([tip_x, tip_x], [tip_y, tip_y])
            self.line2.set_3d_properties([tip_z, tip_z])

            self.line3.set_data([tip_x, tip_x], [tip_y, tip_y])
            self.line3.set_3d_properties([tip_z, tip_z])

            self.line4.set_data([tip_x, tip_x], [tip_y, tip_y])
            self.line4.set_3d_properties([tip_z, tip_z])
            
            self.canvas.draw()










            
            # Prüfen auf Kollision
            collision_detected = (
                self.check_collision(self.tip_x, self.tip_y, self.tip_z) or
                self.check_collision(self.tip_x, self.tip_y, self.tip_z) or
                self.check_collision(self.tip_x, self.tip_y, self.tip_z) or
                self.check_collision(self.tip_x, self.tip_y, self.tip_z)
            )
            if collision_detected:
                print("Kollision erkannt!")
                break

        if not collision_detected:
            # Arme wieder öffnen
            self.line1.set_data([self.tip_x, self.tip_x + self.length], [self.tip_y, self.tip_y])
            self.line2.set_data([self.tip_x, self.tip_x - self.length], [self.tip_y, self.tip_y])
            self.line3.set_data([self.tip_x, self.tip_x], [self.tip_y, self.tip_y - self.length])
            self.line4.set_data([self.tip_x, self.tip_x], [self.tip_y, self.tip_y + self.length])
            self.line1.set_3d_properties([self.tip_z, self.tip_z + self.winkel1])
            self.line2.set_3d_properties([self.tip_z, self.tip_z + self.winkel1])
            self.line3.set_3d_properties([self.tip_z, self.tip_z + self.winkel1])
            self.line4.set_3d_properties([self.tip_z, self.tip_z + self.winkel1])
            self.canvas.draw()
"""
