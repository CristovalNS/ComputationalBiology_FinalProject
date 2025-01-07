import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageSequence
import os


class AnimatedGIFLabel(tk.Label):
    """
    A Tkinter Label that plays an animated GIF using Pillow, with pause/resume/refresh support.
    """

    def __init__(self, master, gif_path, delay=100, **kwargs):
        super().__init__(master, **kwargs)

        self.gif_path = gif_path
        self.delay = delay
        self.frames = []
        self.current_frame = 0
        self.is_paused = False  # track whether the animation is paused
        self.after_id = None  # store the ID of the scheduled .after call

        # Load all frames from the GIF using Pillow
        pil_image = Image.open(gif_path)
        for frame in ImageSequence.Iterator(pil_image):
            frame_rgb = frame.convert("RGBA")
            tk_frame = ImageTk.PhotoImage(frame_rgb)
            self.frames.append(tk_frame)

        if not self.frames:
            raise RuntimeError(f"No frames found in the GIF: {gif_path}")

        # Display the first frame
        self.config(image=self.frames[0])

        # Start the animation
        self._schedule_next_frame()

    def _schedule_next_frame(self):
        """Schedule the animation of the next frame, unless we're paused."""
        if not self.is_paused:
            self.after_id = self.after(self.delay, self._animate)

    def _animate(self):
        """Move to the next frame, then schedule the subsequent one."""
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.config(image=self.frames[self.current_frame])
        self._schedule_next_frame()

    def pause(self):
        """Stop advancing frames."""
        if not self.is_paused:
            self.is_paused = True
            if self.after_id is not None:
                self.after_cancel(self.after_id)
                self.after_id = None

    def resume(self):
        """Resume advancing frames."""
        if self.is_paused:
            self.is_paused = False
            self._schedule_next_frame()

    def refresh(self):
        """
        Restart the animation from frame 0.
        If paused, unpause it.
        """
        self.pause()  # cancel any pending after calls
        self.current_frame = 0  # go back to the beginning
        self.config(image=self.frames[0])
        self.is_paused = False  # unpause
        self._schedule_next_frame()


def do_fullscreen_layout():
    """Positions all rectangles and frames for the user's full screen size."""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    gap_x = 20
    gap_y = 20
    param_width = screen_width // 3
    box_width = (screen_width - param_width - gap_x * 3) // 2
    box_height = (screen_height - gap_y * 3) // 2

    # --- Place the Canvas rectangles ---
    canvas.coords(box1, gap_x, gap_y, gap_x + box_width, gap_y + box_height)
    canvas.coords(
        box2,
        gap_x * 2 + box_width, gap_y,
        gap_x * 2 + 2 * box_width, gap_y + box_height
    )
    canvas.coords(
        box3,
        gap_x, gap_y * 2 + box_height,
               gap_x + box_width, gap_y * 2 + 2 * box_height
    )
    canvas.coords(
        box4,
        gap_x * 2 + box_width, gap_y * 2 + box_height,
        gap_x * 2 + 2 * box_width, gap_y * 2 + 2 * box_height
    )

    # --- Position & size the frames to match each rectangle ---
    canvas.coords("box1_frame", gap_x, gap_y)
    canvas.itemconfig("box1_frame", width=box_width, height=box_height)

    canvas.coords("box2_frame", gap_x * 2 + box_width, gap_y)
    canvas.itemconfig("box2_frame", width=box_width, height=box_height)

    canvas.coords("box3_frame", gap_x, gap_y * 2 + box_height)
    canvas.itemconfig("box3_frame", width=box_width, height=box_height)

    canvas.coords("box4_frame", gap_x * 2 + box_width, gap_y * 2 + box_height)
    canvas.itemconfig("box4_frame", width=box_width, height=box_height)

    # --- Parameters section on the right ---
    rect_left = gap_x * 3 + 2 * box_width
    rect_right = rect_left + param_width
    rect_top = gap_y
    rect_bottom = screen_height - gap_y

    canvas.coords(parameters_section, rect_left, rect_top, rect_right, rect_bottom)
    canvas.coords("parameters_frame", rect_left, rect_top)
    canvas.itemconfig(
        "parameters_frame",
        width=(rect_right - rect_left),
        height=(rect_bottom - rect_top)
    )


# Keep track of each box’s GIF path and label so we can refresh/pause them collectively
box_gif_paths = {1: None, 2: None, 3: None, 4: None}
box_gif_labels = {1: None, 2: None, 3: None, 4: None}


def show_parameters_for_box(box_num):
    """
    Displays an "Open File" button, plus "Refresh All", "Pause All", and "Resume All"
    in the parameters frame. Clicking "Open File" picks a GIF for that box.
    'Refresh All' restarts all loaded GIFs across all boxes.
    'Pause' and 'Resume' affect all loaded GIFs collectively.
    """
    for widget in parameters_frame.winfo_children():
        widget.destroy()

    box_label = tk.Label(
        parameters_frame,
        text=f"You selected Box {box_num}",
        font=("Arial", 14), fg="green"
    )
    box_label.pack(pady=10)

    def on_open_file():
        file_path = filedialog.askopenfilename(
            title="Select a GIF file",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        if file_path:
            load_and_display_gif(box_num, file_path)

    open_file_btn = tk.Button(
        parameters_frame,
        text="Open a .gif file",
        font=("Arial", 12),
        bg="lightblue",
        command=on_open_file
    )
    open_file_btn.pack(pady=5)

    def on_refresh_all():
        for label_obj in box_gif_labels.values():
            if label_obj is not None:
                label_obj.refresh()

    refresh_btn = tk.Button(
        parameters_frame,
        text="Refresh ALL GIFs",
        font=("Arial", 12),
        bg="lightgreen",
        command=on_refresh_all
    )
    refresh_btn.pack(pady=5)

    def on_pause_all():
        for label_obj in box_gif_labels.values():
            if label_obj is not None:
                label_obj.pause()

    pause_all_btn = tk.Button(
        parameters_frame,
        text="Pause ALL GIFs",
        font=("Arial", 12),
        bg="pink",
        command=on_pause_all
    )
    pause_all_btn.pack(pady=5)

    def on_resume_all():
        for label_obj in box_gif_labels.values():
            if label_obj is not None:
                label_obj.resume()

    resume_all_btn = tk.Button(
        parameters_frame,
        text="Resume ALL GIFs",
        font=("Arial", 12),
        bg="cyan",
        command=on_resume_all
    )
    resume_all_btn.pack(pady=5)

    def on_pause():
        label_obj = box_gif_labels[box_num]
        if label_obj is not None:
            label_obj.pause()

    pause_btn = tk.Button(
        parameters_frame,
        text="Pause This GIF",
        font=("Arial", 12),
        bg="lightcoral",
        command=on_pause
    )
    pause_btn.pack(pady=5)

    def on_resume():
        label_obj = box_gif_labels[box_num]
        if label_obj is not None:
            label_obj.resume()

    resume_btn = tk.Button(
        parameters_frame,
        text="Resume This GIF",
        font=("Arial", 12),
        bg="lightcyan",
        command=on_resume
    )
    resume_btn.pack(pady=5)


def load_and_display_gif(box_num, gif_path):
    """
    Actually load the .gif file and place it in the chosen box's frame.
    Store references so we can refresh/pause/resume later.
    """
    print(f"[Console] Box {box_num} is loading: {gif_path}")

    # Save path in our dictionary
    box_gif_paths[box_num] = gif_path

    # Clear the chosen box so we can place the new GIF
    if box_num == 1:
        for w in box1_frame.winfo_children():
            w.destroy()
        gif_label = AnimatedGIFLabel(box1_frame, gif_path, delay=100, bg="white")
        gif_label.pack(fill="both", expand=True)
        gif_label.bind("<Button-1>", lambda e: show_parameters_for_box(1))
        box_gif_labels[1] = gif_label

    elif box_num == 2:
        for w in box2_frame.winfo_children():
            w.destroy()
        gif_label = AnimatedGIFLabel(box2_frame, gif_path, delay=100, bg="white")
        gif_label.pack(fill="both", expand=True)
        gif_label.bind("<Button-1>", lambda e: show_parameters_for_box(2))
        box_gif_labels[2] = gif_label

    elif box_num == 3:
        for w in box3_frame.winfo_children():
            w.destroy()
        gif_label = AnimatedGIFLabel(box3_frame, gif_path, delay=100, bg="white")
        gif_label.pack(fill="both", expand=True)
        gif_label.bind("<Button-1>", lambda e: show_parameters_for_box(3))
        box_gif_labels[3] = gif_label

    elif box_num == 4:
        for w in box4_frame.winfo_children():
            w.destroy()
        gif_label = AnimatedGIFLabel(box4_frame, gif_path, delay=100, bg="white")
        gif_label.pack(fill="both", expand=True)
        gif_label.bind("<Button-1>", lambda e: show_parameters_for_box(4))
        box_gif_labels[4] = gif_label


def on_box1_click(event):
    show_parameters_for_box(box_num=1)


def on_box2_click(event):
    show_parameters_for_box(box_num=2)


def on_box3_click(event):
    show_parameters_for_box(box_num=3)


def on_box4_click(event):
    show_parameters_for_box(box_num=4)


# --------------------- MAIN APPLICATION SETUP ---------------------
root = tk.Tk()
root.title("Fullscreen GIF Loader (Refresh All)")

# Fullscreen
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

canvas = tk.Canvas(root, bg="lightgrey")
canvas.pack(fill=tk.BOTH, expand=True)

# Create the 4 boxes as rectangles
box1 = canvas.create_rectangle(0, 0, 0, 0, fill="white", outline="red", tags="box1")
box2 = canvas.create_rectangle(0, 0, 0, 0, fill="white", outline="red", tags="box2")
box3 = canvas.create_rectangle(0, 0, 0, 0, fill="white", outline="red", tags="box3")
box4 = canvas.create_rectangle(0, 0, 0, 0, fill="white", outline="red", tags="box4")

# Rectangle for parameters
parameters_section = canvas.create_rectangle(
    0, 0, 0, 0, fill="white", outline="red", tags="parameters_section"
)

# Frames on top of each box
box1_frame = tk.Frame(canvas, bg="white")
box2_frame = tk.Frame(canvas, bg="white")
box3_frame = tk.Frame(canvas, bg="white")
box4_frame = tk.Frame(canvas, bg="white")

parameters_frame = tk.Frame(canvas, bg="white")

canvas.create_window(0, 0, anchor="nw", window=box1_frame, tags="box1_frame")
canvas.create_window(0, 0, anchor="nw", window=box2_frame, tags="box2_frame")
canvas.create_window(0, 0, anchor="nw", window=box3_frame, tags="box3_frame")
canvas.create_window(0, 0, anchor="nw", window=box4_frame, tags="box4_frame")
canvas.create_window(0, 0, anchor="nw", window=parameters_frame, tags="parameters_frame")

# Bind a click on each box's Frame
box1_frame.bind("<Button-1>", on_box1_click)
box2_frame.bind("<Button-1>", on_box2_click)
box3_frame.bind("<Button-1>", on_box3_click)
box4_frame.bind("<Button-1>", on_box4_click)


def on_initial_draw(_):
    root.unbind("<Map>")
    root.update_idletasks()
    do_fullscreen_layout()


root.bind("<Map>", on_initial_draw)
root.mainloop()
