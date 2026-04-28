import tkinter as tk
import winsound

WORK_MINUTES  = 25
BREAK_MINUTES = 5
CANVAS_SIZE   = 300
ARC_PADDING   = 30

BG_COLOR    = "#1a1a2e"
ARC_EMPTY   = "#2a2a3e"
ARC_WORK    = "#e94560"
ARC_BREAK   = "#06d6a0"
TEXT_COLOR  = "#ffffff"
BTN_START   = "#e94560"
BTN_STOP    = "#444466"
BTN_RESET   = "#2a2a3e"

is_running    = False
is_break      = False
sessions_done = 0
time_left     = WORK_MINUTES * 60
total_time    = WORK_MINUTES * 60
after_id      = None


def start_stop():
    global is_running
    if is_running:
        pause_timer()
    else:
        run_timer()


def run_timer():
    global is_running
    is_running = True
    btn_start.config(text="Pause", bg=BTN_STOP)
    tick()


def pause_timer():
    global is_running, after_id
    is_running = False
    btn_start.config(text="Resume", bg=BTN_START)
    if after_id:
        root.after_cancel(after_id)


def reset_timer():
    global is_running, is_break, time_left, total_time, after_id
    if after_id:
        root.after_cancel(after_id)
    is_running = False
    is_break   = False
    time_left  = WORK_MINUTES * 60
    total_time = WORK_MINUTES * 60
    btn_start.config(text="Start", bg=BTN_START, fg="white")
    label_mode.config(text="Focus Time", fg=TEXT_COLOR)
    update_display()


def tick():
    global time_left, after_id
    if time_left > 0:
        time_left -= 1
        update_display()
        after_id = root.after(1000, tick)
    else:
        session_complete()


def session_complete():
    global is_break, sessions_done, time_left, total_time, is_running
    is_running = False

    if not is_break:
        sessions_done += 1
        label_sessions.config(text="o  " * sessions_done)
        play_sound()
        show_completion_message()
        is_break   = True
        time_left  = BREAK_MINUTES * 60
        total_time = BREAK_MINUTES * 60
        btn_start.config(text="Start Break", bg=BTN_START, fg="white")
        label_mode.config(text="Break Time", fg=BTN_STOP)
    else:
        is_break   = False
        time_left  = WORK_MINUTES * 60
        total_time = WORK_MINUTES * 60
        btn_start.config(text="Start", bg=BTN_START, fg="white")
        label_mode.config(text="Focus Time", fg=TEXT_COLOR)

    update_display()


def update_display():
    mins = time_left // 60
    secs = time_left % 60
    label_time.config(text=f"{mins:02d}:{secs:02d}")
    draw_arc()


def draw_arc():
    canvas.delete("arc")

    x0 = ARC_PADDING
    y0 = ARC_PADDING
    x1 = CANVAS_SIZE - ARC_PADDING
    y1 = CANVAS_SIZE - ARC_PADDING

    canvas.create_arc(x0, y0, x1, y1,
                      start=90, extent=359.9,
                      style=tk.ARC, outline=ARC_EMPTY,
                      width=12, tags="arc")

    fraction = time_left / total_time if total_time > 0 else 0
    extent   = fraction * 359.9
    color    = ARC_BREAK if is_break else ARC_WORK

    if extent > 0:
        canvas.create_arc(x0, y0, x1, y1,
                          start=90, extent=extent,
                          style=tk.ARC, outline=color,
                          width=12, tags="arc")


def play_sound():
    for _ in range(3):
        winsound.Beep(880, 200)


MESSAGES = [
    "Session complete! You earned this break.",
    "Another one down. Keep it up!",
    "Focus unlocked. Nice work!",
    "You are on a roll. Rest up!",
    "Big brain hours. Take a breather!",
]


def show_completion_message():
    msg_index = (sessions_done - 1) % len(MESSAGES)
    message   = MESSAGES[msg_index]

    popup = tk.Toplevel(root)
    popup.title("Done!")
    popup.configure(bg=BG_COLOR)
    popup.geometry("320x150")
    popup.resizable(False, False)

    popup.update_idletasks()
    px = root.winfo_x() + (root.winfo_width()  // 2) - 160
    py = root.winfo_y() + (root.winfo_height() // 2) - 75
    popup.geometry(f"+{px}+{py}")

    tk.Label(popup, text=message,
             font=("Helvetica", 12, "bold"),
             bg=BG_COLOR, fg=TEXT_COLOR,
             wraplength=280, justify="center").pack(pady=28)

    tk.Button(popup, text="Let's go",
              font=("Helvetica", 11),
              bg=BTN_START, fg="white",
              relief="flat", padx=16, pady=6,
              command=popup.destroy).pack()

    popup.after(4000, popup.destroy)


root = tk.Tk()
root.title("Pomodoro Timer")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

canvas = tk.Canvas(root, width=CANVAS_SIZE, height=CANVAS_SIZE,
                   bg=BG_COLOR, highlightthickness=0)
canvas.pack(pady=(30, 0))

label_time = tk.Label(root, text="25:00",
                      font=("Helvetica", 48, "bold"),
                      bg=BG_COLOR, fg=TEXT_COLOR)
canvas.create_window(CANVAS_SIZE // 2, CANVAS_SIZE // 2,
                     window=label_time)

label_mode = tk.Label(root, text="Focus Time",
                      font=("Helvetica", 12),
                      bg=BG_COLOR, fg=TEXT_COLOR)
label_mode.pack()

label_sessions = tk.Label(root, text="",
                           font=("Helvetica", 14),
                           bg=BG_COLOR, fg=ARC_WORK)
label_sessions.pack(pady=(4, 0))

btn_frame = tk.Frame(root, bg=BG_COLOR)
btn_frame.pack(pady=20)

btn_start = tk.Button(btn_frame, text="Start",
                      font=("Helvetica", 12, "bold"),
                      bg=BTN_START, fg="white",
                      relief="flat", padx=22, pady=9,
                      command=start_stop)
btn_start.grid(row=0, column=0, padx=8)

btn_reset = tk.Button(btn_frame, text="Reset",
                      font=("Helvetica", 12),
                      bg=BTN_RESET, fg=TEXT_COLOR,
                      relief="flat", padx=22, pady=9,
                      command=reset_timer)
btn_reset.grid(row=0, column=1, padx=8)

draw_arc()

root.mainloop()
