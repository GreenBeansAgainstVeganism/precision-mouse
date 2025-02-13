from pynput import mouse, keyboard
from tkinter import *
from tkinter import ttk, font, messagebox
import ctypes

# necessary for avoiding scaling issues on hi-res displays
PROCESS_PER_MONITOR_DPI_AWARE = 2
ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

# controllers
mousectrl = mouse.Controller()
root = Tk()
root.title("Precision Mouse")
root.geometry("640x560")

# state
INFOTEXTRELATIVE = \
        "Press [SHIFT]+V to move cursor\n" + \
        "by a precise offset in pixels.\n\n" + \
        "Press [SHIFT]+C, move cursor,\n" + \
        "then press it again to store offset"
INFOTEXTABSOLUTE = \
        "Press [SHIFT]+V to move cursor\n" + \
        "to a precise position on screen in pixels.\n\n" + \
        "Press [SHIFT]+C to set offset to cursor's\n" + \
        "current position"
isrelative = BooleanVar(value=True)
xoffset = IntVar(value=85)
yoffset = IntVar()
infotext = StringVar(value=INFOTEXTRELATIVE)



# ui

def on_changerelative():
    global storedoffset
    if isrelative.get():
        infotext.set(INFOTEXTRELATIVE)
    else:
        infotext.set(INFOTEXTABSOLUTE)
        storedoffset = None
        [m.config(foreground="#000") for m in highlights]

class SpinboxValidator:
    def __init__(self, spinbox, min_val, max_val):
        self.spinbox = spinbox
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, new_value):
        if new_value == "":
            self.spinbox.set(0)
            return False

        try:
            value = int(new_value)
            if self.min_val <= value <= self.max_val:
                return True

            if value > self.max_val:
                self.spinbox.set(self.max_val)
            else:
                self.spinbox.set(self.min_val)

            return False

        except ValueError:
            return False

swidth = root.winfo_screenwidth()
sheight = root.winfo_screenheight()

frm = ttk.Frame(root, padding=10)

frm.pack(expand=True,fill='both')

pos = "cursor position: {0:>4}, {1:>4}".format(*mousectrl.position)
label = ttk.Label(
    frm,
    text=pos,
    font=font.Font(font=("Courier",10)),
    relief="sunken",
    background="#222",
    foreground="#df4",
    padding=10)
label.pack()

ttk.Checkbutton(
    frm,
    text="relative mode",
    variable=isrelative,
    command=on_changerelative).pack()

frm1 = ttk.Frame(frm)
frm1.pack()
label_xoffset = ttk.Label(frm1, text="x offset:")
label_xoffset.pack(side=LEFT,padx=(0,10))
spinbox1 = ttk.Spinbox(
    frm1,
    from_=-swidth,
    to=swidth,
    textvariable=xoffset,
    validate='key')
spinbox1.pack(side=RIGHT)
validate1 = SpinboxValidator(spinbox1,-swidth,swidth)
spinbox1.config(validatecommand=(root.register(validate1.validate),'%P'))

frm2 = ttk.Frame(frm)
frm2.pack()
label_yoffset = ttk.Label(frm2, text="y offset:")
label_yoffset.pack(side=LEFT,padx=(0,10))
spinbox2 = ttk.Spinbox(
    frm2,
    from_=-sheight,
    to=sheight,
    textvariable=yoffset,
    validate="key")
spinbox2.pack(side=RIGHT)
validate2 = SpinboxValidator(spinbox2,-sheight,sheight)
spinbox2.config(validatecommand=(root.register(validate2.validate),'%P'))

ttk.Label(frm,textvariable=infotext,justify=CENTER).pack()
frm3 = ttk.Frame(frm)
frm3.pack(side=BOTTOM)
infobox = messagebox.Message(
    parent=root.winfo_toplevel(),
    type=messagebox.OK,
    title="Additional Controls",
    message=
        "Arrow Keys: nudge cursor\n" +
        "[SHIFT] + Arrow Keys: 10x nudge\n" +
        "[CTRL] + [SHIFT] + Arrow Keys: 100x nudge\n" +
        "[SHIFT]+X: click with keyboard")
ttk.Button(
    frm3,
    text="Additional Controls",
    command=infobox.show).pack(side=LEFT,padx=10,ipadx=10)
ttk.Button(frm3, text="Close", command=root.destroy).pack(side=RIGHT)

for child in frm.winfo_children():
    child.pack_configure(pady=5)

# input listeners

def on_move(x, y):
    label['text'] = "cursor position: {0:>4}, {1:>4}".format(x,y)
    if storedoffset is not None:
        (x1, y1) = storedoffset
        xoffset.set(x-x1)
        yoffset.set(y-y1)

def reposition_cursor():
    if isrelative.get():
        mousectrl.move(xoffset.get(),yoffset.get())
    else:
        mousectrl.position = (xoffset.get(),yoffset.get())


storedoffset = None
highlights = [label_xoffset,label_yoffset,spinbox1,spinbox2]
def set_offset():
    global storedoffset
    if isrelative.get():
        if storedoffset is None:
            storedoffset = mousectrl.position
            [m.config(foreground="#f00") for m in highlights]
            xoffset.set(0)
            yoffset.set(0)
        else:
            (x1, y1) = storedoffset
            (x2, y2) = mousectrl.position
            xoffset.set(x2-x1)
            yoffset.set(y2-y1)
            storedoffset = None
            [m.config(foreground="#000") for m in highlights]
    else:
        (x, y) = mousectrl.position
        xoffset.set(x)
        yoffset.set(y)

mouselistener = mouse.Listener(
    on_move=on_move)
mouselistener.start()

hotkeylistener = keyboard.GlobalHotKeys({
    '<shift>+v': reposition_cursor,
    '<shift>+c': set_offset,
    '<shift>+x': lambda: mousectrl.click(mouse.Button.left),
    '<up>': lambda: mousectrl.move(0,-1),
    '<down>': lambda: mousectrl.move(0,1),
    '<left>': lambda: mousectrl.move(-1,0),
    '<right>': lambda: mousectrl.move(1,0),
    '<shift>+<up>': lambda: mousectrl.move(0,-9),
    '<shift>+<down>': lambda: mousectrl.move(0,9),
    '<shift>+<left>': lambda: mousectrl.move(-9,0),
    '<shift>+<right>': lambda: mousectrl.move(9,0),
    '<ctrl>+<shift>+<up>': lambda: mousectrl.move(0,-90),
    '<ctrl>+<shift>+<down>': lambda: mousectrl.move(0,90),
    '<ctrl>+<shift>+<left>': lambda: mousectrl.move(-90,0),
    '<ctrl>+<shift>+<right>': lambda: mousectrl.move(90,0)})
hotkeylistener.start()

root.mainloop()

mouselistener.stop()
hotkeylistener.stop()
