import tkinter

import User
from Provider import Provider


class Presenter:
    @staticmethod
    def display(providers):
        root = tkinter.Tk()

        my_canvas = tkinter.Canvas(root, bg="white", height=720, width=1280)
        my_canvas.pack()

        def create_circle(x, y, r, canvas_name):
            x0 = x - r
            y0 = y - r
            x1 = x + r
            y1 = y + r
            return canvas_name.create_oval(x0/2, y0/2, x1/2, y1/2)

        for p in providers:
            p: Provider
            create_circle(p.fog_server.x+250, p.fog_server.y+250, p.fog_server.radius, my_canvas)
            for u in p.users:
                u: User
                create_circle(u.x+200, u.y+200, 2, my_canvas)

        root.mainloop()
