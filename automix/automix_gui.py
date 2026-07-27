#!/usr/bin/env python3
"""
AutoMix GUI — standalone desktop app.

Visual identity: a mastering-rack front panel (see DESIGN.md).

IMPORTANT: this is built with --windowed (no console) for the packaged
.exe, which means an unhandled exception before mainloop() would
normally just make the app flash and vanish with zero explanation. main()
below guards against exactly that: any startup failure gets written to
automix_error.log next to the executable AND shown in a message box.
"""
import os
import sys
import traceback
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ---------------------------------------------------------------- tokens --

BG = "#17181B"
PANEL = "#1D1F23"
HAIRLINE = "#33353A"
TEXT_PRIMARY = "#ECEAE4"
TEXT_MUTED = "#8B8D93"
AMBER = "#E8A33D"
AMBER_DIM = "#6B5327"
TEAL = "#3ED6C0"
RED = "#E5484D"

FONT_DISPLAY = ("Segoe UI Semibold", 20)
FONT_LABEL = ("Consolas", 9)
FONT_BODY = ("Segoe UI", 10)
FONT_BUTTON = ("Segoe UI Semibold", 12)


def _app_base_dir():
    """Folder the .exe (or script) lives in — works both frozen (PyInstaller
    onefile, where __file__ resolves inside the temp extraction dir) and as
    a plain script."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _assets_dir():
    """Where bundled data (icon) actually lives at runtime. PyInstaller
    onefile extracts --add-data into sys._MEIPASS, not next to the exe."""
    if getattr(sys, "_MEIPASS", None):
        return os.path.join(sys._MEIPASS, "assets")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


ASSETS_DIR = _assets_dir()


class LEDMeter(tk.Canvas):
    """Segmented level-meter: header decoration at idle, busy indicator
    while processing. Replaces a stock progress bar."""

    SEGMENTS = 24

    def __init__(self, parent, width=480, height=14, **kwargs):
        super().__init__(parent, width=width, height=height, bg=PANEL,
                          highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.running = False
        self._phase = 0
        self._draw(active_count=0)

    def _seg_color(self, index, lit_upto):
        if index > lit_upto:
            return HAIRLINE
        frac = index / self.SEGMENTS
        if frac > 0.85:
            return RED
        if frac > 0.6:
            return TEAL
        return AMBER

    def _draw(self, active_count):
        self.delete("all")
        gap = 3
        seg_w = (self.width - gap * (self.SEGMENTS - 1)) / self.SEGMENTS
        for i in range(self.SEGMENTS):
            x0 = i * (seg_w + gap)
            x1 = x0 + seg_w
            color = self._seg_color(i, active_count)
            self.create_rectangle(x0, 1, x1, self.height - 1, fill=color, outline="")

    def start(self):
        self.running = True
        self._animate()

    def stop(self):
        self.running = False
        self._draw(active_count=-1)

    def _animate(self):
        if not self.running:
            return
        import math
        self._phase += 1
        sweep = int((math.sin(self._phase / 8) + 1) / 2 * self.SEGMENTS)
        self._draw(active_count=sweep)
        self.after(45, self._animate)


class AutoMixApp:
    def __init__(self, root):
        self.root = root
        root.title("AutoMix")
        root.configure(bg=BG)
        root.geometry("620x520")
        root.resizable(False, False)
        self._set_icon()

        self.stems_folder = tk.StringVar()
        self.output_path = tk.StringVar()
        self.genre = tk.StringVar(value="modern_pop")
        self.status = tk.StringVar(value="Select a stems folder to begin.")

        # Import here, not at module load, so a bad dependency (e.g. a
        # pedalboard DLL problem) surfaces as a clear dialog from main()
        # instead of killing the process before the window even appears.
        from presets import GENRE_PRESETS
        self.GENRE_PRESETS = GENRE_PRESETS

        self._build_header()
        self._build_body()
        self._build_footer()

    def _set_icon(self):
        ico_path = os.path.join(ASSETS_DIR, "automix.ico")
        try:
            if sys.platform.startswith("win") and os.path.exists(ico_path):
                self.root.iconbitmap(ico_path)
            else:
                png_path = os.path.join(ASSETS_DIR, "icon.png")
                if os.path.exists(png_path):
                    img = tk.PhotoImage(file=png_path)
                    self.root.iconphoto(True, img)
                    self._icon_ref = img
        except Exception:
            pass  # icon is cosmetic; never block app start over it

    def _hairline(self, parent):
        tk.Frame(parent, bg=HAIRLINE, height=1).pack(fill="x")

    def _hairline_padded(self, parent):
        tk.Frame(parent, bg=HAIRLINE, height=1).pack(fill="x", padx=28, pady=(14, 0))

    def _section_label(self, parent, text):
        tk.Label(parent, text=text, font=FONT_LABEL, fg=TEXT_MUTED, bg=BG,
                  anchor="w").pack(fill="x", padx=28, pady=(18, 6))

    def _build_header(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x")

        top = tk.Frame(header, bg=BG)
        top.pack(fill="x", padx=28, pady=(24, 4))
        tk.Label(top, text="AUTOMIX", font=FONT_DISPLAY, fg=TEXT_PRIMARY, bg=BG).pack(side="left")
        tk.Label(top, text="  STEM \u2192 MASTER", font=FONT_LABEL, fg=AMBER, bg=BG).pack(
            side="left", pady=(8, 0))

        meter_row = tk.Frame(header, bg=BG)
        meter_row.pack(fill="x", padx=28, pady=(6, 18))
        self.header_meter = LEDMeter(meter_row, width=564, height=8)
        self.header_meter.pack(fill="x")
        self.header_meter._draw(active_count=self.header_meter.SEGMENTS)

        self._hairline(self.root)

    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)

        self._section_label(body, "INPUT — STEMS FOLDER")
        row = tk.Frame(body, bg=BG)
        row.pack(fill="x", padx=28)
        entry = tk.Entry(row, textvariable=self.stems_folder, font=FONT_BODY,
                          bg=PANEL, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                          relief="flat", state="readonly", readonlybackground=PANEL)
        entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))
        self._rack_button(row, "BROWSE", self.pick_folder, width=10).pack(side="left")

        self._hairline_padded(body)

        self._section_label(body, "GENRE PRESET")
        row2 = tk.Frame(body, bg=BG)
        row2.pack(fill="x", padx=28)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Automix.TCombobox", fieldbackground=PANEL, background=PANEL,
                         foreground=TEXT_PRIMARY, arrowcolor=AMBER, bordercolor=HAIRLINE,
                         lightcolor=PANEL, darkcolor=PANEL)
        combo = ttk.Combobox(row2, textvariable=self.genre, state="readonly",
                              style="Automix.TCombobox", font=FONT_BODY,
                              values=list(self.GENRE_PRESETS.keys()))
        combo.pack(fill="x", ipady=4)

        self._hairline_padded(body)

        self._section_label(body, "OUTPUT FILE")
        row3 = tk.Frame(body, bg=BG)
        row3.pack(fill="x", padx=28)
        out_entry = tk.Entry(row3, textvariable=self.output_path, font=FONT_BODY,
                              bg=PANEL, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                              relief="flat", state="readonly", readonlybackground=PANEL)
        out_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))
        self._rack_button(row3, "CHOOSE", self.pick_output, width=10).pack(side="left")

        self._hairline_padded(body)

        transport = tk.Frame(body, bg=BG)
        transport.pack(fill="x", padx=28, pady=(20, 8))
        self.process_btn = tk.Button(
            transport, text="\u25b6  PROCESS", font=FONT_BUTTON, bg=AMBER, fg=BG,
            activebackground=TEAL, activeforeground=BG, relief="flat", bd=0,
            command=self.process, cursor="hand2", pady=10,
        )
        self.process_btn.pack(fill="x")

        self.meter = LEDMeter(body, width=564, height=14)
        self.meter.pack(padx=28, pady=(12, 4))

    def _build_footer(self):
        self._hairline(self.root)
        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=28, pady=14)
        tk.Label(footer, textvariable=self.status, font=FONT_LABEL, fg=TEXT_MUTED,
                  bg=BG, wraplength=560, justify="left", anchor="w").pack(fill="x")

    def _rack_button(self, parent, text, command, width=None):
        return tk.Button(parent, text=text, font=FONT_LABEL, bg=PANEL, fg=TEXT_PRIMARY,
                          activebackground=HAIRLINE, activeforeground=TEXT_PRIMARY,
                          relief="flat", bd=1, highlightbackground=HAIRLINE,
                          highlightthickness=1, command=command, cursor="hand2",
                          width=width, pady=6)

    def pick_folder(self):
        folder = filedialog.askdirectory(title="Select folder containing stem WAVs")
        if folder:
            self.stems_folder.set(folder)
            if not self.output_path.get():
                self.output_path.set(os.path.join(folder, "mixed_master.wav"))

    def pick_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".wav",
                                             filetypes=[("WAV audio", "*.wav")])
        if path:
            self.output_path.set(path)

    def log(self, msg):
        self.status.set(msg)
        self.root.update_idletasks()

    def process(self):
        folder = self.stems_folder.get()
        output = self.output_path.get()
        if not folder:
            messagebox.showwarning("AutoMix", "Choose a stems folder first.")
            return
        if not output:
            output = os.path.join(folder, "mixed_master.wav")
            self.output_path.set(output)

        self.process_btn.config(state="disabled", bg=AMBER_DIM)
        self.meter.start()
        thread = threading.Thread(target=self._run_engine, args=(folder, output), daemon=True)
        thread.start()

    def _run_engine(self, folder, output):
        try:
            from engine import AutoMixEngine
            preset = self.GENRE_PRESETS[self.genre.get()]
            engine = AutoMixEngine(preset, verbose=True)
            engine.log = lambda msg: self.root.after(0, self.log, msg)
            engine.run(folder, output)
            self.root.after(0, self._on_success, output)
        except Exception:
            err = traceback.format_exc()
            self._write_error_log(err)
            self.root.after(0, self._on_error, err)

    def _write_error_log(self, text):
        try:
            log_path = os.path.join(_app_base_dir(), "automix_error.log")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            pass

    def _on_success(self, output):
        self.meter.stop()
        self.process_btn.config(state="normal", bg=AMBER)
        self.status.set(f"Done. Saved to {output}")
        messagebox.showinfo("AutoMix", f"Mix complete.\n\nSaved to:\n{output}")

    def _on_error(self, error_msg):
        self.meter.stop()
        self.process_btn.config(state="normal", bg=AMBER)
        short = error_msg.strip().splitlines()[-1] if error_msg.strip() else "Unknown error"
        self.status.set(f"Error: {short}")
        messagebox.showerror(
            "AutoMix",
            f"Something went wrong:\n\n{short}\n\n"
            f"Full details were saved to automix_error.log next to the app."
        )


def main():
    try:
        root = tk.Tk()
        AutoMixApp(root)
        root.mainloop()
    except Exception:
        # Built with --windowed => no console. Without this, a startup
        # failure (e.g. a missing DLL for pedalboard/numpy/scipy) would
        # just make the app flash and disappear with no explanation.
        err = traceback.format_exc()
        try:
            log_path = os.path.join(_app_base_dir(), "automix_error.log")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(err)
        except Exception:
            log_path = None
        try:
            fallback = tk.Tk()
            fallback.withdraw()
            messagebox.showerror(
                "AutoMix failed to start",
                "AutoMix hit an error before its window could open:\n\n"
                + err.strip().splitlines()[-1]
                + (f"\n\nFull details saved to:\n{log_path}" if log_path else "")
                + "\n\nIf this mentions a missing DLL, installing the "
                  "Microsoft Visual C++ Redistributable (x64) usually fixes it."
            )
        except Exception:
            print(err, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
