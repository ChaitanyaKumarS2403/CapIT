import os
import sys
import threading
import tempfile
import subprocess
import shutil
import importlib.util
import webbrowser
import customtkinter as ctk
from PIL import Image
from tkinter import filedialog, messagebox

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CapIT(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.version = "v1.0.0.0"
        self.title("CapIT")
        self.geometry("1050x850") 
        self.set_window_icon()
        
        self.video_path = ctk.StringVar()
        self.task_choice = ctk.StringVar(value="translate")
        self.model_choice = ctk.StringVar(value="none") 
        self.is_downloading = False

        self.model_sizes = {"tiny": 75, "base": 145, "small": 470, "medium": 1450, "large": 3000}
        self.model_priority = ["large", "medium", "small", "base", "tiny"]

        self.accent_blue = "#3b8ed0"
        self.accent_red = "#e74c3c"
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()
        self.check_system_health()
        self.auto_select_best_model()

    def set_window_icon(self):
        try:
            icon_path = resource_path(os.path.join("images", "translate.ico"))
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except: pass

    def get_model_path(self, model_name):
        base_dir = os.path.join(os.path.expanduser("~"), ".cache", "whisper")
        variations = [f"{model_name}.pt"]
        if model_name == "large":
            variations.extend(["large-v3.pt", "large-v2.pt", "large-v1.pt"])
        for v in variations:
            full_path = os.path.join(base_dir, v)
            if os.path.exists(full_path):
                return full_path
        return os.path.join(base_dir, f"{model_name}.pt")

    def auto_select_best_model(self):
        selected = "none"
        for m in self.model_priority:
            if os.path.exists(self.get_model_path(m)):
                selected = m
                break
        self.update_active_model(selected)

    def update_active_model(self, m_name):
        self.model_choice.set(m_name)
        if hasattr(self, 'active_model_pill'):
            display_text = m_name.upper() if m_name != "none" else "NONE (Check Settings)"
            self.active_model_pill.configure(text=display_text, fg_color=self.accent_blue if m_name != "none" else self.accent_red)

    def change_appearance_mode(self, mode):
        ctk.set_appearance_mode(mode)
        if mode == "light":
            self.light_mode_btn.configure(fg_color=self.accent_blue, text_color="white", border_width=0)
            self.dark_mode_btn.configure(fg_color="transparent", text_color=("gray10", "gray90"), border_width=1)
        else:
            self.dark_mode_btn.configure(fg_color=self.accent_blue, text_color="white", border_width=0)
            self.light_mode_btn.configure(fg_color="transparent", text_color=("gray10", "gray90"), border_width=1)

    def setup_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1) 
        
        try:
            logo_path = resource_path(os.path.join("images", "translate.png"))
            logo_img = ctk.CTkImage(Image.open(logo_path), size=(35, 35))
            self.logo_label = ctk.CTkLabel(self.sidebar, text=" CapIT", image=logo_img, compound="left", font=ctk.CTkFont(size=26, weight="bold"))
        except:
            self.logo_label = ctk.CTkLabel(self.sidebar, text="CapIT", font=ctk.CTkFont(size=26, weight="bold"))
        self.logo_label.pack(pady=(50, 40))

        self.home_btn = ctk.CTkButton(self.sidebar, text="Home", height=45, corner_radius=22, command=lambda: self.show_frame("home"))
        self.home_btn.pack(padx=25, pady=10, fill="x")
        self.settings_btn = ctk.CTkButton(self.sidebar, text="Settings", height=45, corner_radius=22, command=lambda: self.show_frame("settings"))
        self.settings_btn.pack(padx=25, pady=10, fill="x")
        self.credits_btn = ctk.CTkButton(self.sidebar, text="Credits", height=45, corner_radius=22, command=lambda: self.show_frame("credits"))
        self.credits_btn.pack(padx=25, pady=10, fill="x")

        self.health_card = ctk.CTkFrame(self.sidebar, height=80, corner_radius=20, fg_color=("gray85", "gray14"))
        self.health_card.pack(side="bottom", padx=20, pady=40, fill="x")
        self.health_dot = ctk.CTkLabel(self.health_card, text="● System Status", font=ctk.CTkFont(size=11))
        self.health_dot.pack(pady=15)

        self.home_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.credits_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.build_home()
        self.build_settings()
        self.build_credits()
        self.show_frame("home")

    def build_home(self):
        ctk.CTkLabel(self.home_frame, text="CapIT: AI-Powered Captioning Tool", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(40, 5), padx=40, anchor="w")
        ctk.CTkLabel(self.home_frame, text="Transcribe or translate media files into .SRT subtitles.", text_color=("gray30", "gray70"), font=ctk.CTkFont(size=13)).pack(padx=40, anchor="w", pady=(0, 20))

        pill_row = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        pill_row.pack(padx=40, anchor="w", pady=(0, 10))
        ctk.CTkLabel(pill_row, text="Active Model:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        self.active_model_pill = ctk.CTkLabel(pill_row, text="LOADING...", corner_radius=12, fg_color=self.accent_blue, text_color="white", font=ctk.CTkFont(size=11, weight="bold"), padx=10, pady=2)
        self.active_model_pill.pack(side="left", padx=10)

        f_card = ctk.CTkFrame(self.home_frame, corner_radius=25, border_width=1)
        f_card.pack(padx=40, pady=10, fill="x")
        ctk.CTkLabel(f_card, text="Source Video", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=25, pady=(20, 0))
        entry_row = ctk.CTkFrame(f_card, fg_color="transparent")
        entry_row.pack(fill="x", padx=15, pady=20)
        self.file_entry = ctk.CTkEntry(entry_row, textvariable=self.video_path, placeholder_text="Select a video file...", height=45, corner_radius=22, border_color=self.accent_blue)
        self.file_entry.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(entry_row, text="Browse", width=110, height=45, corner_radius=22, fg_color=self.accent_blue, command=self.select_file).pack(side="right", padx=5)

        s_card = ctk.CTkFrame(self.home_frame, corner_radius=25, border_width=1)
        s_card.pack(padx=40, pady=20, fill="x")
        ctk.CTkLabel(s_card, text="Task Action", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 0))
        radio_row = ctk.CTkFrame(s_card, fg_color="transparent")
        radio_row.pack(pady=20)
        ctk.CTkRadioButton(radio_row, text="Translate", variable=self.task_choice, value="translate").pack(side="left", padx=20)
        ctk.CTkRadioButton(radio_row, text="Transcribe", variable=self.task_choice, value="transcribe").pack(side="left", padx=20)

        self.p_bar = ctk.CTkProgressBar(self.home_frame, height=12, corner_radius=6, progress_color=self.accent_blue)
        self.p_bar.set(0)
        self.p_bar.pack(padx=60, pady=(40, 5), fill="x")
        self.status_lbl = ctk.CTkLabel(self.home_frame, text="System Idle", font=ctk.CTkFont(size=13))
        self.status_lbl.pack(pady=(0, 20))

        self.start_btn = ctk.CTkButton(self.home_frame, text="START", width=220, height=56, corner_radius=28, fg_color=self.accent_blue, font=ctk.CTkFont(size=15, weight="bold"), command=self.begin_work)
        self.start_btn.pack(pady=10)

    def build_settings(self):
        header = ctk.CTkLabel(self.settings_frame, text="Settings", font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(pady=(40, 20), padx=40, anchor="w")
        
        scroll = ctk.CTkScrollableFrame(self.settings_frame, fg_color="transparent")
        scroll.pack(padx=40, fill="both", expand=True)

        t_card = ctk.CTkFrame(scroll, corner_radius=25, border_width=1)
        t_card.pack(pady=10, fill="x")
        ctk.CTkLabel(t_card, text="Appearance Mode", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=30, pady=(20, 10))
        theme_btn_row = ctk.CTkFrame(t_card, fg_color="transparent")
        theme_btn_row.pack(fill="x", padx=30, pady=(0, 25))
        self.light_mode_btn = ctk.CTkButton(theme_btn_row, text="Light Mode", width=130, height=38, corner_radius=19, command=lambda: self.change_appearance_mode("light"))
        self.light_mode_btn.pack(side="left", padx=(0, 10))
        self.dark_mode_btn = ctk.CTkButton(theme_btn_row, text="Dark Mode", width=130, height=38, corner_radius=19, command=lambda: self.change_appearance_mode("dark"))
        self.dark_mode_btn.pack(side="left")

        self.change_appearance_mode(ctk.get_appearance_mode().lower())

        m_card = ctk.CTkFrame(scroll, corner_radius=25, border_width=1)
        m_card.pack(pady=10, fill="x")
        ctk.CTkLabel(m_card, text="Model Management", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=30, pady=(20, 10))
        self.set_model_status_lbl = ctk.CTkLabel(m_card, text="Ready", font=ctk.CTkFont(size=12))
        self.set_model_status_lbl.pack(padx=30, anchor="w")
        self.set_model_pbar = ctk.CTkProgressBar(m_card, height=8, corner_radius=4, progress_color=self.accent_blue)
        self.set_model_pbar.set(0)
        self.set_model_pbar.pack(fill="x", padx=30, pady=(5, 15))
        self.model_box = ctk.CTkFrame(m_card, fg_color="transparent")
        self.model_box.pack(fill="x", padx=20, pady=(0, 20))
        self.refresh_settings_models()

        d_card = ctk.CTkFrame(scroll, corner_radius=25, border_width=1)
        d_card.pack(pady=10, fill="x")
        ctk.CTkLabel(d_card, text="System Engines", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=30, pady=15)
        self.dep_container = ctk.CTkFrame(d_card, fg_color="transparent")
        self.dep_container.pack(fill="x", padx=30, pady=(0, 20))
        for engine, attr in [("FFmpeg (Winget):", "ff"), ("Whisper AI (Pip):", "wh"), ("Python Core:", "py")]:
            row = ctk.CTkFrame(self.dep_container, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=engine, width=150, anchor="w").pack(side="left")
            stat_lbl = ctk.CTkLabel(row, text="Checking...", font=ctk.CTkFont(weight="bold"))
            stat_lbl.pack(side="left", padx=10)
            setattr(self, f"{attr}_stat_lbl", stat_lbl)

        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(pady=30, fill="x")
        self.repair_btn = ctk.CTkButton(btn_row, text="Install Engines", height=45, corner_radius=22, fg_color=self.accent_blue, command=lambda: self.manage_deps("install"))
        self.repair_btn.pack(side="left", padx=5)
        self.uninst_btn = ctk.CTkButton(btn_row, text="Uninstall Engines", height=45, corner_radius=22, fg_color="transparent", border_width=1, border_color=self.accent_red, text_color=self.accent_red, command=lambda: self.manage_deps("uninstall"))
        self.uninst_btn.pack(side="left", padx=5)

    def download_model(self, name):
        def monitor_file(target_path, total_size_mb):
            parent_dir = os.path.dirname(target_path)
            while self.is_downloading:
                try:
                    curr_size_mb = 0
                    files = [os.path.join(parent_dir, f) for f in os.listdir(parent_dir) if f.endswith('.tmp') or f.startswith(name)]
                    if files:
                        curr_size_mb = max(os.path.getsize(f) for f in files) / (1024 * 1024)
                    
                    p = min(curr_size_mb / total_size_mb, 0.98)
                    self.after(0, lambda v=p, cm=curr_size_mb, tm=total_size_mb: [
                        self.set_model_pbar.set(v), 
                        self.set_model_status_lbl.configure(text=f"Downloading {name.upper()}: ({int(cm)}MB / {int(tm)}MB)")
                    ])
                except: pass
                threading.Event().wait(0.5)

        def run():
            try:
                import whisper
                self.is_downloading = True
                threading.Thread(target=monitor_file, args=(self.get_model_path(name), self.model_sizes[name]), daemon=True).start()
                whisper.load_model(name)
                self.after(0, lambda: [self.set_model_pbar.set(1.0), self.update_active_model(name), self.refresh_settings_models()])
                messagebox.showinfo("Success", f"{name.capitalize()} model ready.")
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Model Download Failed: {str(e)}"))
            finally:
                self.is_downloading = False
                self.after(1000, lambda: [self.set_model_pbar.set(0), self.set_model_status_lbl.configure(text="Ready")])
        
        threading.Thread(target=run, daemon=True).start()

    def refresh_settings_models(self):
        for widget in self.model_box.winfo_children(): widget.destroy()
        for m in self.model_priority:
            path = self.get_model_path(m)
            exists = os.path.exists(path)
            row = ctk.CTkFrame(self.model_box, fg_color=("gray85", "gray20") if self.model_choice.get() == m else "transparent", corner_radius=12)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=m.upper(), width=100, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15, pady=8)
            ctk.CTkLabel(row, text="Downloaded" if exists else "Not Installed", text_color="#2ecc71" if exists else "orange", width=150, anchor="w").pack(side="left")
            btn_c = ctk.CTkFrame(row, fg_color="transparent")
            btn_c.pack(side="right", padx=10)
            if not exists:
                ctk.CTkButton(btn_c, text="Install", width=80, height=28, command=lambda n=m: self.download_model(n)).pack(side="left")
            else:
                if self.model_choice.get() != m:
                    ctk.CTkButton(btn_c, text="Activate", width=80, height=28, fg_color=self.accent_blue, command=lambda n=m: [self.update_active_model(n), self.refresh_settings_models()]).pack(side="left", padx=2)
                ctk.CTkButton(btn_c, text="Delete", width=80, height=28, fg_color="transparent", border_width=1, border_color=self.accent_red, text_color=self.accent_red, command=lambda n=m: self.delete_model(n)).pack(side="left", padx=2)

    def manage_deps(self, mode):
        def task():
            self.after(0, lambda: [self.repair_btn.configure(state="disabled"), self.uninst_btn.configure(state="disabled")])
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = subprocess.SW_HIDE
            try:
                if mode == "install":
                    # Install Python Core via Winget
                    subprocess.run("winget install -e --id Python.Python.3 --accept-source-agreements --accept-package-agreements", 
                                 shell=True, startupinfo=info, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # Install FFmpeg via Winget
                    subprocess.run("winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements", 
                                 shell=True, startupinfo=info, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # Install Python Dependencies via Pip
                    subprocess.run(f'"{sys.executable}" -m pip install openai-whisper ffmpeg-python', 
                                 shell=True, startupinfo=info, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    # Uninstall FFmpeg
                    subprocess.run("winget uninstall -e --id Gyan.FFmpeg", shell=True, startupinfo=info, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # Uninstall Python dependencies (Python Core remains)
                    subprocess.run(f'"{sys.executable}" -m pip uninstall -y openai-whisper ffmpeg-python', 
                                 shell=True, startupinfo=info, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Immediate UI Refresh
                self.check_system_health()
                self.after(0, lambda: messagebox.showinfo("Success", f"Engines {mode}ed successfully."))
            except Exception as e: 
                self.after(0, lambda: messagebox.showerror("Error", f"Subprocess Error: {str(e)}"))
            finally: 
                self.after(0, lambda: [self.repair_btn.configure(state="normal"), self.uninst_btn.configure(state="normal")])
        threading.Thread(target=task, daemon=True).start()

    def check_system_health(self):
        ff_ok = shutil.which("ffmpeg") is not None
        wh_ok = importlib.util.find_spec("whisper") is not None
        
        self.after(0, lambda: [
            self.ff_stat_lbl.configure(text="Active" if ff_ok else "Missing", text_color="green" if ff_ok else self.accent_red),
            self.wh_stat_lbl.configure(text="Active" if wh_ok else "Missing", text_color="green" if wh_ok else self.accent_red),
            self.py_stat_lbl.configure(text="Active", text_color="green"),
            self.health_dot.configure(text="🟢 Engine Ready" if (ff_ok and wh_ok) else "🔴 Engine Missing", 
                                     text_color="green" if (ff_ok and wh_ok) else self.accent_red)
        ])
        
        if not hasattr(self, "_health_loop_active"):
            self._health_loop_active = True
            self._run_health_loop()

    def _run_health_loop(self):
        ff_ok = shutil.which("ffmpeg") is not None
        wh_ok = importlib.util.find_spec("whisper") is not None
        self.after(0, lambda: [
            self.ff_stat_lbl.configure(text="Active" if ff_ok else "Missing", text_color="green" if ff_ok else self.accent_red),
            self.wh_stat_lbl.configure(text="Active" if wh_ok else "Missing", text_color="green" if wh_ok else self.accent_red),
            self.health_dot.configure(text="🟢 Engine Ready" if (ff_ok and wh_ok) else "🔴 Engine Missing", 
                                     text_color="green" if (ff_ok and wh_ok) else self.accent_red)
        ])
        self.after(3000, self._run_health_loop)

    def delete_model(self, name):
        if messagebox.askyesno("Confirm", f"Delete {name} model?"):
            try: 
                os.remove(self.get_model_path(name))
                self.auto_select_best_model()
                self.refresh_settings_models()
            except Exception as e: messagebox.showerror("Error", str(e))

    def begin_work(self):
        if self.model_choice.get() == "none" or not self.video_path.get():
            messagebox.showwarning("Warning", "Configuration incomplete.")
            return
        self.start_btn.configure(state="disabled")
        threading.Thread(target=self.process_engine, daemon=True).start()

    def process_engine(self):
        temp_path = os.path.join(tempfile.gettempdir(), "capit_audio.wav")
        try:
            import whisper, ffmpeg
            from whisper.utils import format_timestamp
            self.after(0, lambda: [self.status_lbl.configure(text="Extracting Audio..."), self.p_bar.set(0.10)])
            ffmpeg.input(self.video_path.get()).output(temp_path, acodec="pcm_s16le", ac=1, ar="16000").overwrite_output().run(quiet=True)
            self.after(0, lambda: [self.status_lbl.configure(text="Loading AI Model..."), self.p_bar.set(0.25)])
            model = whisper.load_model(self.model_choice.get())
            self.after(0, lambda: self.status_lbl.configure(text="AI Processing..."))
            probe = ffmpeg.probe(self.video_path.get())
            total_duration = float(probe['format']['duration'])
            result = model.transcribe(temp_path, task=self.task_choice.get())
            out_file = os.path.splitext(self.video_path.get())[0] + ".srt"
            with open(out_file, "w", encoding="utf-8") as f:
                for i, seg in enumerate(result["segments"], 1):
                    progress = 0.3 + (0.7 * (seg['end'] / total_duration))
                    self.after(0, lambda v=progress: self.p_bar.set(v))
                    f.write(f"{i}\n{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}\n{seg['text'].strip()}\n\n")
            self.after(0, lambda: [self.p_bar.set(1.0), self.status_lbl.configure(text="Complete!")])
            messagebox.showinfo("Done", f"Captions saved to: {out_file}")
        except Exception as e: 
            self.after(0, lambda: messagebox.showerror("Error", f"Processing Failed: {str(e)}"))
        finally: 
            if os.path.exists(temp_path): os.remove(temp_path)
            self.after(1000, lambda: [self.p_bar.set(0), self.status_lbl.configure(text="System Idle"), self.start_btn.configure(state="normal")])

    def show_frame(self, name):
        frames = {"home": self.home_frame, "settings": self.settings_frame, "credits": self.credits_frame}
        buttons = {"home": self.home_btn, "settings": self.settings_btn, "credits": self.credits_btn}
        for f_name, frame in frames.items():
            if f_name == name:
                frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
                buttons[f_name].configure(fg_color=self.accent_blue, text_color="white")
            else:
                frame.grid_forget()
                buttons[f_name].configure(fg_color="transparent", text_color=("gray10", "gray90"))

    def build_credits(self):
        header = ctk.CTkLabel(self.credits_frame, text="Credits & Developer Info", font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(pady=(40, 20), padx=40, anchor="w")
        c_card = ctk.CTkFrame(self.credits_frame, corner_radius=25, border_width=1)
        c_card.pack(padx=40, pady=10, fill="both", expand=True)
        ctk.CTkLabel(c_card, text="Developed By", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.accent_blue).pack(pady=(30, 5))
        ctk.CTkLabel(c_card, text="Chaitanya Kumar Sathivada", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)
        ctk.CTkButton(c_card, text="View GitHub Profile", fg_color="transparent", border_width=1, command=lambda: webbrowser.open("https://github.com/ChaitanyaKumarS2403")).pack(pady=20)
        ctk.CTkLabel(c_card, text=f"Version: {self.version}", font=ctk.CTkFont(size=12)).pack(side="bottom", pady=(5, 5))
        ctk.CTkLabel(c_card, text="© Copyrights @ Chaitanya Kumar Sathivada", font=ctk.CTkFont(size=12)).pack(side="bottom", pady=(5, 10))

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Videos", "*.mp4 *.mkv *.avi *.mov")])
        if path: self.video_path.set(path)

if __name__ == "__main__":
    app = CapIT()
    app.mainloop()