from tkinter import Frame, Label, Canvas, PhotoImage, Button, Toplevel
from tkinter import LEFT, NW, X, Y, BOTH, YES


class MainApp:
    def __init__(self, parent, config, communicator, backgrounds, counter_updater):
        self.parent = parent
        self.screen_width = self.parent.winfo_screenwidth()
        self.screen_height = self.parent.winfo_screenheight()
        self.frame = Frame(self.parent)
        self.communicator = communicator
        self.backgrounds = backgrounds

        self.counter_updater = counter_updater
        self.counters = config.counters
        self.counter_app = None
        self.popup_show_time = int(config.show_time) * 1000

        self.max_slots = int(self.screen_height / MessagePopup.HEGHT)
        self.slots = {slot_num: None for slot_num in range(0, self.max_slots)}

        self.host_label = Label(
            self.frame,
            width=40,
            text="mqtt://{}:{}\nTopic: {}".format(
                config.mqtt_connection["host"],
                config.mqtt_connection["port"],
                config.mqtt_connection["topic"],
            ),
        )
        self.host_label.pack()
        self.counter_button = Button(
            self.frame,
            text='show/hide counters',
            width=40,
            command=self.counter_window
        )
        self.counter_button.pack()

        self.close_button = Button(
            self.frame,
            text='Quit',
            width=40,
            command=self.parent.destroy
        )
        self.close_button.pack()
        self.frame.pack()

    def _get_free_slot(self):
        for pos in reversed(range(0, self.max_slots)):
            if self.slots[pos] is None:
                return pos

    def force_update(self):
        self.counter_updater.force_update()

    def check_queue(self):
        if self.communicator.is_message_empty():
            return
        self.new_popup()

        self.parent.after(500, self.check_queue)

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
            label_colors=self.counters
        )
        self.update_counter_window()

    def update_counter_window(self):
        if not self.counter_app:
            return

        counters = self.counter_updater.get_counters()
        for color, value in counters.items():
            self.counter_app.set_counter(color, value)
        self.parent.after(60000, self.update_counter_window)

    def new_popup(self):
        pos = self._get_free_slot()
        if pos is None:
            return
        msg = self.communicator.get_message()
        new_window = Toplevel(self.parent)

        app = MessagePopup(
            parent=new_window,
            position=pos,
            color=msg.color,
            title=msg.title,
            text=msg.text,
            background=self._get_background(msg.color)
        )

        self.slots[pos] = app
        new_window.after(self.popup_show_time, app.quit)
        new_window.after(self.popup_show_time + 500, lambda: self._clear_slot(pos))

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
    LABEL_SIZE = 75
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
        for label_pos in sorted(label_colors.keys()):
            label_color = label_colors[label_pos]
            frame, self.labels[label_color] = self.make_label(
                self,
                self.LABEL_SIZE,
                width=3,
                height=self.LABEL_SIZE,
                foreground="white",
                font=("Roboto", self.LABEL_FONT_SIZE),
                text='0'
            )
            frame.pack(
                padx=self.LABEL_PAD,
                pady=self.LABEL_PAD,
                side=LEFT
            )

        self.show()

    @staticmethod
    def make_label(master, size, *args, **kwargs):
        frame = Frame(master, height=size, width=size)
        frame.pack_propagate(0)
        label = Label(frame, *args, **kwargs)
        label.pack(fill=BOTH, expand=YES)
        return frame, label

    def set_counter(self, color, value):
        if color not in self.labels.keys():
            return
        self.labels[color].config(background=color if value > 0 else "#9E9E9E")
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
