import tkinter as tk
from logic import controller

LOW_MARK = 25    # % level of the low probe
HIGH_MARK = 90   # % level of the high probe
TICK_MS = 200


class App:
    def __init__(self, root):
        self.root = root
        root.title("Water Tank Level Controller")
        root.resizable(False, False)

        self.level = 60.0
        self.q = 0                      # latch memory
        self.enable = tk.IntVar(value=1)
        self.broken = tk.IntVar(value=0)
        self.draining = False

        # ---- tank drawing ----
        self.canvas = tk.Canvas(root, width=200, height=330, bg="white")
        self.canvas.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # ---- control panel ----
        panel = tk.LabelFrame(root, text=" Inputs ", padx=8, pady=8)
        panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        tk.Checkbutton(panel, text="Enable (E)", variable=self.enable).pack(anchor="w")
        tk.Checkbutton(panel, text="Break HIGH sensor (fault test)",
                       variable=self.broken).pack(anchor="w")
        use = tk.Button(panel, text="Hold to USE water", width=22)
        use.pack(pady=6)
        use.bind("<ButtonPress-1>", lambda e: setattr(self, "draining", True))
        use.bind("<ButtonRelease-1>", lambda e: setattr(self, "draining", False))

        # ---- readout ----
        out = tk.LabelFrame(root, text=" Sensors and outputs ", padx=8, pady=8)
        out.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.lbl = tk.Label(out, text="", font=("Consolas", 11), justify="left")
        self.lbl.pack(anchor="w")
        self.leds = {}
        for name, colour in (("PUMP", "green"), ("FULL", "blue"),
                             ("LOW", "orange"), ("FAULT", "red")):
            row = tk.Frame(out)
            row.pack(anchor="w", pady=2)
            c = tk.Canvas(row, width=22, height=22, highlightthickness=0)
            oval = c.create_oval(2, 2, 20, 20, fill="grey")
            c.pack(side="left")
            tk.Label(row, text=name, width=8, anchor="w").pack(side="left")
            self.leds[name] = (c, oval, colour)

        self.tick()

    def read_sensors(self):
        L = 1 if self.level >= LOW_MARK else 0
        H = 1 if (self.level >= HIGH_MARK or self.broken.get()) else 0
        return L, H

    def tick(self):
        L, H = self.read_sensors()
        E = self.enable.get()
        outputs, self.q = controller(L, H, E, self.q)

        # physics of the tank
        if outputs["PUMP"]:
            self.level += 2.0
        if self.draining:
            self.level -= 2.5
        self.level = max(0.0, min(100.0, self.level))

        self.draw(L, H, E, outputs)
        self.root.after(TICK_MS, self.tick)

    def draw(self, L, H, E, outputs):
        c = self.canvas
        c.delete("all")
        top, bottom, left, right = 20, 310, 40, 160
        height = bottom - top
        y = bottom - height * self.level / 100
        c.create_rectangle(left, y, right, bottom, fill="#4aa3df", outline="")
        c.create_rectangle(left, top, right, bottom, width=3)
        for mark, name in ((LOW_MARK, "L"), (HIGH_MARK, "H")):
            ym = bottom - height * mark / 100
            c.create_line(left - 15, ym, right + 15, ym, dash=(4, 3), fill="red")
            c.create_text(right + 25, ym, text=name, font=("Arial", 11, "bold"))
        c.create_text(100, 10, text=f"Level {self.level:.0f}%")

        self.lbl.config(text=f"E={E}  H={H}  L={L}\nPUMP={outputs['PUMP']}  "
                             f"FAULT={outputs['FAULT']}")
        for name, (cv, oval, colour) in self.leds.items():
            cv.itemconfig(oval, fill=colour if outputs[name] else "grey")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
