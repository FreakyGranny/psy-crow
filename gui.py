from tkinter import Frame, Label, Canvas, PhotoImage, Button, Toplevel
from tkinter import LEFT, NW, X, Y


class MainApp:
    def __init__(self, parent, config, storage, backgrounds):
        self.parent = parent
        self.screen_width = self.parent.winfo_screenwidth()
        self.screen_height = self.parent.winfo_screenheight()
        self.frame = Frame(self.parent)
        self.storage = storage
        self.backgrounds = backgrounds
        self.counters = {key.upper(): 0 for key in config.counters}
        self.counter_app = None
        self.popup_show_time = int(config.show_time) * 1000

        max_slots = int(self.screen_height / MessagePopup.HEGHT)
        self.slots = {slot_num: None for slot_num in reversed(range(0, max_slots))}

        self.host_label = Label(
            self.frame,
            width=25,
            text="mqtt://{}:{}\nTopic: {}".format(
                config.mqtt_connection["host"],
                config.mqtt_connection["port"],
                config.mqtt_connection["topic"],
            ),
        )
        self.host_label.pack()
        if self.counters:
            self.counter_button = Button(
                self.frame,
                text='show/hide counters',
                width=25,
                command=self.counter_window
            )
            self.counter_button.pack()

        self.close_button = Button(
            self.frame,
            text='Quit',
            width=25,
            command=self.parent.destroy
        )
        self.close_button.pack()
        self.frame.pack()

    def _get_free_slot(self):
        for pos, slot in self.slots.items():
            if slot is None:
                return pos

    def incoming_popup(self):
        for slot in self.slots.values():
            if slot is None:
                self.new_popup()
                return

        self.parent.after(500, self.incoming_popup)

    def _get_background(self, color):
        if color in self.backgrounds.keys():
            return self.backgrounds[color]

    def counter_window(self):
        if self.counter_app:
            self.counter_app.quit()
            self.counter_app = None
            return

        self.counter_app = CounterWindow(
            parent=Toplevel(self.parent),
            screen_width=self.screen_width,
            label_colors=self.counters.keys()
        )
        self.update_counter_window()

    def update_counter_window(self):
        if not self.counter_app:
            return

        for color, value in self.counters.items():
            self.counter_app.set_counter(color, value)

    def new_popup(self):
        pos = self._get_free_slot()
        msg = self.storage.get_nowait()
        newWindow = Toplevel(self.parent)

        app = MessagePopup(
            parent=newWindow,
            position=pos,
            color=msg.color,
            title=msg.title,
            text=msg.text,
            background=self._get_background(msg.color)
        )

        self.slots[pos] = app
        newWindow.after(self.popup_show_time, app.quit)
        newWindow.after(self.popup_show_time + 500, lambda: self._clear_slot(pos))

        if msg.color in self.counters.keys():
            self.counters[msg.color] += 1

        if msg.resolve_color in self.counters.keys():
            if self.counters[msg.resolve_color] > 0:
                self.counters[msg.resolve_color] -= 1

        self.update_counter_window()

    def _clear_slot(self, pos):
        self.slots[pos] = None


class Popup(Frame):
    def __init__(self, parent, geometry):
        Frame.__init__(self, parent)
        self.parent = parent
        self.is_fading_in = False
        self.is_fading_out = False
        self.parent.geometry('0x0+0+0')
        self.parent.overrideredirect(True)
        self.parent.wait_visibility(self.parent)
        self.parent.attributes("-alpha", 0.0)
        self.parent.geometry(geometry)

    def quit(self):
        if self.is_fading_in:
            return
        self.is_fading_out = True
        alpha = self.parent.attributes("-alpha")
        if alpha > 0:
            alpha -= .2
            self.parent.attributes("-alpha", alpha)
            self.after(100, self.quit)
        else:
            self.parent.destroy()

    def show(self):
        self.parent.deiconify()
        if self.is_fading_out:
            return
        self.is_fading_in = True
        alpha = self.parent.attributes("-alpha")
        if alpha < 1:
            alpha += .2
            self.parent.attributes("-alpha", alpha)
            self.after(100, self.show)
        self.is_fading_in = False


class CounterWindow(Popup):
    LABEL_SIZE = 88
    LABEL_PAD = 1
    LABEL_FONT_SIZE = 30

    def __init__(self, parent, screen_width, label_colors):
        window_width = len(label_colors) * (self.LABEL_SIZE + self.LABEL_PAD * 2)
        window_geometry = "{}x{}+{}+{}".format(
            window_width,
            self.LABEL_SIZE + self.LABEL_PAD * 2,
            screen_width - window_width,
            0
        )
        Popup.__init__(self, parent, window_geometry)
        self.pack()
        self.config(bg="#1f1f1f")
        self.labels = {}
        for label_color in label_colors:
            self.labels[label_color] = Label(
                self,
                background=label_color,
                width=3,
                height=self.LABEL_SIZE,
                foreground="white",
                font=("Roboto", self.LABEL_FONT_SIZE),
                text='0'
            )
            self.labels[label_color].pack(
                padx=self.LABEL_PAD,
                pady=self.LABEL_PAD,
                side=LEFT
            )
        self.show()

    def set_counter(self, color, value):
        if color not in self.labels.keys():
            return

        self.labels[color].config(text=str(value))


class MessagePopup(Popup):
    WIDTH = 732
    HEGHT = 305
    HORIZONTAL_OFFSET = 55
    VERTICAL_OFFSET = 40
    TITLE_FONT_SIZE = 26
    TEXT_FONT_SIZE = 20

    def __init__(self, parent, position, color, title, text, background=None):
        geometry = '{}x{}+{}+{}'.format(
            self.WIDTH,
            self.HEGHT,
            self.HORIZONTAL_OFFSET,
            self.VERTICAL_OFFSET + position *(self.HEGHT + self.VERTICAL_OFFSET)
        )
        Popup.__init__(self, parent, geometry)
        self.pack()

        canvas = Canvas(
            self,
            background=color,
            width=self.WIDTH,
            height=self.HEGHT,
            bd=0,
            highlightthickness=0
        )
        canvas.pack(fill=Y, padx=0, ipady=0, side=LEFT)
        canvas.create_line(0, 80, self.WIDTH, 80, fill="white", width=2)
        if background:
            self.background_image = PhotoImage(file=background)
            canvas.create_image(0, 0, image=self.background_image, anchor=NW)
        canvas.create_text(30, 20, text=title,
                           anchor=NW,
                           fill="white",
                           font=("Roboto", self.TITLE_FONT_SIZE),
                           )
        canvas.create_text(30, 120, text=text,
                           anchor=NW,
                           fill="white",
                           font=("Roboto", self.TEXT_FONT_SIZE),
                           width=450
                           )
        self.show()
