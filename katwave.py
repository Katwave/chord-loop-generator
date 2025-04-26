import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from PIL import ImageTk, Image
import pygame
import sys
import ctypes

# Import your generation modules
from gen_chords import generate_chord_progression
from gen_loop import generate_drum_loop

# Load data
with open("json-data/drum_patterns.json") as f:
    drum_data = json.load(f)

from chord_templates import chord_progressions

class NeonStyle:
    colors = {
        "background": "#160207",
        "main": "#d41b43",
        "disabled": "#4a0a1a",
        "text": "#ffffff",
        "button_bg": "#2d0712",
        "shadow": "#0a000d"
    }

bg = NeonStyle.colors["background"]

class MusicGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # # For custom title bar (with min,max close)
        # # Remove native title bar
        # self.overrideredirect(True)
        # # Reapply override and ensure taskbar icon when mapped
        # self.bind("<Map>", lambda e: (self.overrideredirect(True), self._force_taskbar_icon()))

        pygame.mixer.init()

        self.app_name = "Katwave"
        self.title(self.app_name)
        self.geometry("900x750")
        self.configure(bg=bg)
        self.last_save_path = os.path.expanduser("~")
        self.track_length = 0
        self.is_playing = False

        # Load logo & icons
        png_logo_path = "assets/images/logo.png"
        ico_logo_path = "assets/images/logo.ico"
        self.logo_img = ImageTk.PhotoImage(Image.open(png_logo_path).resize((40, 40)))
        self.play_icon = ImageTk.PhotoImage(Image.open("assets/images/play.png").resize((24,24)))
        self.pause_icon = ImageTk.PhotoImage(Image.open("assets/images/pause.png").resize((24,24)))

        # # For custom title bar (with min,max close)
        # # Build custom title bar
        # self._create_title_bar()
        # # Ensure window shows on taskbar even with overrideredirect
        # self.after(10, self._force_taskbar_icon)

        try:
            self.iconphoto(False, self.logo_img)

            # Set taskbar icon (must be .ico file for Windows)
            # self.iconbitmap(ico_logo_path)
        except Exception:
            pass

        if sys.platform == "win32":
            # Set app icon for taskbar (Windows)
            myappid = 'katwave.music.generator'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            self.iconbitmap('assets/images/logo.ico')

        # Styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._create_styles()

        # Variables
        self.current_mode = tk.StringVar(value="chords")
        self.genre_var = tk.StringVar()
        self.style_var = tk.StringVar()
        self.mood_var = tk.StringVar()
        self.inspired_var = tk.StringVar()

        # Layout frames
        self.header_frame = ttk.Frame(self, style='Neon.TFrame')
        self.header_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        self.body_frame = ttk.Frame(self, style='Neon.TFrame')
        self.body_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=40)
        self.footer_frame = ttk.Frame(self, style='Neon.TFrame')
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=40)

        # Build UI
        # self.create_header()
        self.create_body()
        self.create_footer()
        self.update_dropdowns()

    def _create_title_bar(self):
        title_bar = ttk.Frame(self, style='Neon.TFrame')
        title_bar.pack(side=tk.TOP, fill=tk.X)
        lbl_logo = ttk.Label(title_bar, image=self.logo_img, background=bg)
        lbl_logo.pack(side=tk.LEFT, padx=5)
        lbl_title = ttk.Label(title_bar, text=self.app_name,
                              font=('Arial', 12, 'bold'), foreground=NeonStyle.colors['main'], background=bg)
        lbl_title.pack(side=tk.LEFT)
        spacer = ttk.Frame(title_bar, style='Neon.TFrame')
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)
        btn_min = tk.Button(title_bar, text='—', command=self.minimize_window,
                            bg=bg, fg=NeonStyle.colors['text'], bd=0)
        btn_min.pack(side=tk.RIGHT, padx=5)
        btn_close = tk.Button(title_bar, text='✕', command=self.destroy,
                              bg=bg, fg=NeonStyle.colors['text'], bd=0)
        btn_close.pack(side=tk.RIGHT)
        def start_move(event):
            self._x = event.x
            self._y = event.y
        def on_move(event):
            x = event.x_root - self._x
            y = event.y_root - self._y
            self.geometry(f"900x750+{x}+{y}")
        title_bar.bind('<ButtonPress-1>', start_move)
        title_bar.bind('<B1-Motion>', on_move)

    def _force_taskbar_icon(self):
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            exStyle = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            exStyle = exStyle & ~0x00000080 | 0x00040000
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, exStyle)
            ctypes.windll.user32.ShowWindow(hwnd, 5)
        except Exception:
            pass

    def minimize_window(self):
        # Disable override so iconify works
        self.overrideredirect(False)
        self.iconify()

    def _create_styles(self):
        main = NeonStyle.colors["main"]
        text = NeonStyle.colors["text"]
        disabled = NeonStyle.colors["disabled"]
        shadow = NeonStyle.colors["shadow"]

        # Frame background
        self.style.configure('Neon.TFrame', background=bg)

        # Combobox style
        self.style.configure('Neon.TCombobox', fieldbackground=bg, background=bg, foreground=text,
                           selectbackground=bg, selectforeground=text, insertcolor=text,
                           bordercolor=main, lightcolor=main, darkcolor=main,
                           arrowsize=15, font=('Arial', 12, 'bold'))
        self.style.map('Neon.TCombobox', fieldbackground=[('readonly', bg)], background=[('readonly', bg)])

        # Entry style
        self.style.configure('Neon.TEntry', fieldbackground=bg, foreground=text,
                             insertcolor=text, bordercolor=main, lightcolor=main,
                             darkcolor=main, font=('Arial', 12))

        # Progress bar style: thinner, colored thumb and trough
        self.style.configure('Neon.Horizontal.TScale', troughcolor=disabled, background=main,
                             sliderlength=12, thickness=6)

    def create_header(self):
        ttk.Label(self.header_frame, image=self.logo_img, background=bg).pack(side=tk.LEFT, padx=10)
        ttk.Label(self.header_frame, text=self.app_name,
                  font=('Arial', 24, 'bold'), foreground=NeonStyle.colors['main'], background=bg).pack(side=tk.LEFT)

    def create_body(self):
        toggles = ttk.Frame(self.body_frame, style='Neon.TFrame')
        toggles.pack(pady=10)
        self.chords_btn = tk.Button(toggles, text="Chords", command=lambda: self.set_mode('chords'),
                                   bg=bg, fg=NeonStyle.colors['text'], bd=0)
        self.chords_btn.pack(side=tk.LEFT, padx=5)
        self.drums_btn = tk.Button(toggles, text="Drum Loop", command=lambda: self.set_mode('drums'),
                                   bg=bg, fg=NeonStyle.colors['text'], bd=0)
        self.drums_btn.pack(side=tk.LEFT, padx=5)

        self.form_container = ttk.Frame(self.body_frame, style='Neon.TFrame')
        self.form_container.pack(fill=tk.BOTH, expand=True, pady=10)
        self.chords_form = self.create_chords_form()
        self.drums_form = self.create_drums_form()
        self.set_mode('chords')

    def create_footer(self):
        # CREATE button
        btn_bg = NeonStyle.colors['main']
        cb_frame = tk.Frame(self.footer_frame, bg=NeonStyle.colors['shadow'])
        cb_frame.pack(side=tk.LEFT, padx=(0,20))
        self.create_btn = tk.Button(cb_frame, text="CREATE", command=self.handle_create,
                                    bg=btn_bg, fg=NeonStyle.colors['text'], bd=0,
                                    font=('Arial', 14, 'bold'), padx=20, pady=10)
        self.create_btn.pack(padx=2, pady=2)

        # Playback controls (image-only buttons)
        pb_frame = tk.Frame(self.footer_frame, bg=bg)
        pb_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.play_btn = tk.Button(pb_frame, image=self.play_icon, command=self.play_audio, bd=0, bg=bg)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        self.pause_btn = tk.Button(pb_frame, image=self.pause_icon, command=self.pause_audio, bd=0, bg=bg)
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        # Styled, thinner progress bar
        self.progress = ttk.Scale(pb_frame, style='Neon.Horizontal.TScale', from_=0, to=1, orient=tk.HORIZONTAL)
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.progress.bind('<ButtonRelease-1>', self.on_seek)

    def create_chords_form(self):
        frm = ttk.Frame(self.form_container, style='Neon.TFrame')
        frm.pack(fill=tk.X)
        ttk.Label(frm, text="Genre:", font=('Arial', 12, 'bold'),
                  foreground=NeonStyle.colors['main'], background=bg).pack(anchor=tk.W)
        self.genre_combo = ttk.Combobox(frm, textvariable=self.genre_var, style='Neon.TCombobox', state='readonly')
        self.genre_combo.pack(fill=tk.X, pady=5, ipady=5)
        self.genre_combo.bind('<Button-1>', lambda e: self.genre_combo.event_generate('<Down>'))
        self.genre_var.trace_add('write', self.clear_style)

        ttk.Label(frm, text="Mood:", font=('Arial', 12, 'bold'),
                  foreground=NeonStyle.colors['main'], background=bg).pack(anchor=tk.W)
        self.mood_combo = ttk.Combobox(frm, textvariable=self.mood_var, style='Neon.TCombobox', state='disabled')
        self.mood_combo.pack(fill=tk.X, pady=5, ipady=5)
        self.mood_combo.bind('<Button-1>', lambda e: self.mood_combo.event_generate('<Down>'))

        self.genre_var.trace_add('write', self.update_moods)
        self.mood_var.trace_add('write', self.update_create_btn)
        return frm

    def create_drums_form(self):
        frm = ttk.Frame(self.form_container, style='Neon.TFrame')
        frm.pack(fill=tk.X)
        ttk.Label(frm, text="Genre:", font=('Arial', 12, 'bold'),
                  foreground=NeonStyle.colors['main'], background=bg).pack(anchor=tk.W)
        self.drums_genre_combo = ttk.Combobox(frm, textvariable=self.genre_var, style='Neon.TCombobox', state='readonly')
        self.drums_genre_combo.pack(fill=tk.X, pady=5, ipady=5)
        self.drums_genre_combo.bind('<Button-1>', lambda e: self.drums_genre_combo.event_generate('<Down>'))
        self.genre_var.trace_add('write', self.clear_style)

        ttk.Label(frm, text="Style:", font=('Arial', 12, 'bold'),
                  foreground=NeonStyle.colors['main'], background=bg).pack(anchor=tk.W)
        self.style_combo = ttk.Combobox(frm, textvariable=self.style_var, style='Neon.TCombobox', state='disabled')
        self.style_combo.pack(fill=tk.X, pady=5, ipady=5)
        self.style_combo.bind('<Button-1>', lambda e: self.style_combo.event_generate('<Down>'))

        ttk.Label(frm, text="Inspiration (optional):", font=('Arial', 12, 'bold'),
                  foreground=NeonStyle.colors['main'], background=bg).pack(anchor=tk.W)
        self.inspired_entry = ttk.Entry(frm, textvariable=self.inspired_var, style='Neon.TEntry')
        self.inspired_entry.pack(fill=tk.X, pady=5, ipady=5)
        self.inspired_var.set("Enter artist name...")

        self.genre_var.trace_add('write', self.update_styles)
        self.style_var.trace_add('write', self.update_create_btn)
        return frm

    def clear_style(self, *args):
        self.style_var.set("")
        self.mood_var.set("")
        self.update_styles()
        self.update_moods()

    def handle_create(self):
        try:
            types = [('MIDI files', '*.mid')] if self.current_mode.get()=='chords' else [('WAV files','*.wav')]
            path = filedialog.asksaveasfilename(initialdir=self.last_save_path, filetypes=types, defaultextension=types[0][1])
            if not path: return
            self.last_save_path = os.path.dirname(path)
            if self.current_mode.get()=='chords':
                generate_chord_progression(genre=self.genre_var.get(), mood=self.mood_var.get(), output_path=path)
            else:
                generate_drum_loop(genre=self.genre_var.get(), style=self.style_var.get(), inspired_by=self.inspired_var.get(), output_path=path)
            messagebox.showinfo("Success", f"File generated successfully!\n{path}")
            pygame.mixer.music.load(path)
            self.track_length = pygame.mixer.Sound(path).get_length()
            self.progress.config(to=self.track_length)
            self.play_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate file:\n{e}")

    def play_audio(self):
        if self.track_length == 0:
            messagebox.showwarning("Music not loaded", "music not loaded")
            return
        if not self.is_playing:
            pygame.mixer.music.play(loops=0, start=self.progress.get())
            self.is_playing = True
            self.after(200, self.update_progress)

    def pause_audio(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False

    def update_progress(self):
        if self.is_playing:
            pos_ms = pygame.mixer.music.get_pos()
            if pos_ms >= 0:
                self.progress.set(pos_ms/1000.0)
            self.after(200, self.update_progress)

    def on_seek(self,event):
        if self.is_playing:
            pygame.mixer.music.play(loops=0,start=self.progress.get())

    def set_mode(self,mode):
        self.current_mode.set(mode)
        if mode=='chords':
            self.chords_btn.config(bg=NeonStyle.colors['button_bg'], highlightthickness=2, highlightbackground=NeonStyle.colors['main'])
            self.drums_btn.config(bg=bg, highlightthickness=0)
            self.drums_form.pack_forget()
            self.chords_form.pack(fill=tk.X,pady=5)
        else:
            self.drums_btn.config(bg=NeonStyle.colors['button_bg'], highlightthickness=2, highlightbackground=NeonStyle.colors['main'])
            self.chords_btn.config(bg=bg, highlightthickness=0)
            self.chords_form.pack_forget()
            self.drums_form.pack(fill=tk.X,pady=5)
        self.update_dropdowns()

    def update_dropdowns(self):
        if self.current_mode.get()=='chords':
            self.genre_var.set("")
            self.genre_combo['values']=list(chord_progressions.keys())
        else:
            self.genre_var.set("")
            self.drums_genre_combo['values']=list(drum_data.keys())

    def update_moods(self,*args):
        g=self.genre_var.get()
        if g in chord_progressions:
            self.mood_combo.config(state='readonly')
            self.mood_combo['values']=list(chord_progressions[g].keys())
        else:
            self.mood_combo.config(state='disabled')
            self.mood_var.set('')
        if hasattr(self, 'create_btn'):
            self.update_create_btn()

    def update_styles(self,*args):
        g=self.genre_var.get()
        if g in drum_data:
            self.style_combo.config(state='readonly')
            self.style_combo['values']=list(drum_data[g].keys())
        else:
            self.style_combo.config(state='disabled')
            self.style_var.set('')
        if hasattr(self, 'create_btn'):
            self.update_create_btn()

    def update_create_btn(self,*args):
        if not hasattr(self, 'create_btn'):
            return
        valid=(self.genre_var.get() and ((self.current_mode.get()=='chords' and self.mood_var.get()) or
               (self.current_mode.get()=='drums' and self.style_var.get())))
        self.create_btn.config(state=tk.NORMAL if valid else tk.DISABLED)

if __name__=="__main__":
    app=MusicGeneratorApp()
    app.mainloop()
