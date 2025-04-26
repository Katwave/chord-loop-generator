import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES

class MidiOrganizerApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("MIDI File Organizer")
        self.geometry("600x550")  # Increased height for new field
        self.configure(bg="#0d1117")
        
        # Initialize variables
        self.dropped_files = []
        self.keywords = ["kick", "hi-hat", "open-hat", "snare", "percussion", "clap"]
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_styles()
        
        # Create GUI elements
        self.create_widgets()
        
    def _configure_styles(self):
        # Colors
        self.bg_color = "#0d1117"
        self.frame_color = "#161b22"
        self.accent_color = "#238636"
        self.text_color = "#c9d1d9"
        self.border_color = "#30363d"
        
        # Configure styles
        self.style.configure('.', background=self.bg_color, foreground=self.text_color)
        
        # Entry style
        self.style.configure('TEntry',
                            fieldbackground=self.frame_color,
                            foreground=self.text_color,
                            borderwidth=0,
                            insertcolor=self.text_color,
                            padding=8)
        self.style.map('TEntry',
                     fieldbackground=[('active', self.frame_color)],
                     foreground=[('active', self.text_color)])
        
        # Button style
        self.style.configure('TButton',
                           background=self.accent_color,
                           foreground="#ffffff",
                           borderwidth=0,
                           padding=10,
                           font=('Arial', 10, 'bold'))
        self.style.map('TButton',
                      background=[('active', '#2ea043'), ('pressed', '#238636')])
        
        # Frame style
        self.style.configure('Glass.TFrame',
                           background=self.frame_color,
                           borderwidth=2,
                           relief='solid',
                           bordercolor=self.border_color)
        
        # Label style
        self.style.configure('Glass.TLabel',
                           background=self.frame_color,
                           foreground=self.text_color,
                           font=('Arial', 10),
                           padding=10,
                           anchor='center')
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Genre input
        genre_frame = ttk.Frame(main_frame, style='Glass.TFrame', padding=10)
        genre_frame.pack(fill='x', pady=5)
        ttk.Label(genre_frame, text="Genre:").pack(side='left', padx=5)
        self.genre_entry = ttk.Entry(genre_frame)
        self.genre_entry.pack(side='right', expand=True, fill='x', padx=5)
        
        # Style input
        style_frame = ttk.Frame(main_frame, style='Glass.TFrame', padding=10)
        style_frame.pack(fill='x', pady=5)
        ttk.Label(style_frame, text="Style:").pack(side='left', padx=5)
        self.style_entry = ttk.Entry(style_frame)
        self.style_entry.pack(side='right', expand=True, fill='x', padx=5)
        
        # Song Name input
        song_frame = ttk.Frame(main_frame, style='Glass.TFrame', padding=10)
        song_frame.pack(fill='x', pady=5)
        ttk.Label(song_frame, text="Song Name:").pack(side='left', padx=5)
        self.song_entry = ttk.Entry(song_frame)
        self.song_entry.pack(side='right', expand=True, fill='x', padx=5)
        
        # Drag and drop area
        drop_container = ttk.Frame(main_frame, style='Glass.TFrame')
        drop_container.pack(fill='both', expand=True, pady=10)
        
        self.drop_label = ttk.Label(drop_container,
                                  style='Glass.TLabel',
                                  text="Drag and drop MIDI files here")
        self.drop_label.pack(expand=True, fill='both', padx=2, pady=2)
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Save button
        self.save_btn = ttk.Button(main_frame, text="Save Files", style='TButton')
        self.save_btn.pack(fill='x', pady=10)
        self.save_btn.configure(command=self.save_files)
        
    # Keep all existing logic methods unchanged below
    def handle_drop(self, event):
        self.dropped_files = self.tk.splitlist(event.data)
        valid_files = [f for f in self.dropped_files if f.lower().endswith('.mid')]
        
        if len(valid_files) != len(self.dropped_files):
            messagebox.showwarning("Invalid Files", "Some files were not MIDI files and were ignored")
        
        self.dropped_files = valid_files
        self.drop_label.config(text=f"{len(self.dropped_files)} files ready for processing")
        
    def categorize_file(self, filename):
        filename_lower = os.path.basename(filename).lower()
        for keyword in self.keywords:
            if keyword in filename_lower:
                return keyword
        return None
    
    def save_files(self):
        genre = self.genre_entry.get().strip()
        style = self.style_entry.get().strip()
        song_name = self.song_entry.get().strip()
        
        if not genre or not style or not song_name:
            messagebox.showerror("Error", "Please fill all fields: Genre, Style, and Song Name")
            return
            
        if not self.dropped_files:
            messagebox.showwarning("Warning", "No files to process")
            return
            
        for file_path in self.dropped_files:
            category = self.categorize_file(file_path)
            if not category:
                continue
                
            # Create destination path
            dest_dir = os.path.join(
                "assets", "midi", 
                genre, style, 
                f"{category}s"  # Pluralize category
            )
            
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
                
            # Create new filename
            new_filename = f"{song_name}.mid"
            dest_path = os.path.join(dest_dir, new_filename)
            
            # Copy file with new name
            try:
                shutil.copy(file_path, dest_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy file: {str(e)}")
                return
            
        messagebox.showinfo("Success", f"{len(self.dropped_files)} files organized successfully!")
        self.dropped_files = []
        self.drop_label.config(text="Drag and drop MIDI files here")

if __name__ == "__main__":
    app = MidiOrganizerApp()
    app.mainloop()