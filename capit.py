import os
import sys
import threading
import tempfile
import subprocess
import shutil
import importlib.util
import webbrowser
import ctypes
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
        self.geometry("1000x800") 
        self.set_window_icon()
        
        self.video_path = ctk.StringVar()
        self.task_choice = ctk.StringVar(value="translate")
        self.model_choice = ctk.StringVar(value="base")
        self.stop_event = threading.Event()

        # Whisper Model Sizes (Approx MB) for the real-time progress bar
        self.model_sizes = {
            "tiny": 75, "base": 145, "small": 470, "medium": 1450, "large": 3050
        }

        self.accent_blue = "#3b8ed0"
        self.accent_red = "#e74c3c"
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()
        self.check_system_health()
        self.update_model_status_view()

    def set_window_icon(self):
        try:
            icon_path = resource_path(os.path.join("images", "translate.ico"))
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except: pass

    def get_model_path(self, model_name):
        return os.path.join(os.path.expanduser("~"), ".cache", "whisper", f"{model_name}.pt")

    def update_model_status_view(self, *args):
        model_name = self.model_choice.get()
        path = self.get_model_path(model_name)
        if os.path.exists(path):
            self.model_stat_lbl.configure(text=f"● {model_name.capitalize()}: Ready (Offline)", text_color="#2ecc71")
        else:
            self.model_stat_lbl.configure(text=f"● {model_name.capitalize()}: Not Downloaded", text_color="#f39c12")

    def check_delete_visibility(self, *args):
        model_name = self.delete_model_choice.get()
        if os.path.exists(self.get_model_path(model_name)):
            self.delete_btn.pack(side="left", padx=5)
        else:
            self.delete_btn.pack_forget()

    def delete_model(self):
        model_name = self.delete_model_choice.get()
        path = self.get_model_path(model_name)
        if messagebox.askyesno("Confirm", f"Delete {model_name} model from disk?"):
            try:
                os.remove(path)
                self.update_model_status_view()
                self.check_delete_visibility()
            except Exception as e:
                messagebox.showerror("Error", str(e))

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
        ctk.CTkLabel(self.home_frame, text="Transcribe or translate your media files into .SRT subtitles using AI.", text_color=("gray30", "gray70"), font=ctk.CTkFont(size=13)).pack(padx=40, anchor="w", pady=(0, 20))

        f_card = ctk.CTkFrame(self.home_frame, corner_radius=25, border_width=1)
        f_card.pack(padx=40, pady=10, fill="x")
        ctk.CTkLabel(f_card, text="Source Video", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=25, pady=(20, 0))
        entry_row = ctk.CTkFrame(f_card, fg_color="transparent")
        entry_row.pack(fill="x", padx=15, pady=20)
        self.file_entry = ctk.CTkEntry(entry_row, textvariable=self.video_path, placeholder_text="Select a video file...", height=45, corner_radius=22, border_color=self.accent_blue)
        self.file_entry.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(entry_row, text="Browse", width=110, height=45, corner_radius=22, fg_color=self.accent_blue, text_color="white", command=self.select_file).pack(side="right", padx=5)

        s_card = ctk.CTkFrame(self.home_frame, corner_radius=25, border_width=1)
        s_card.pack(padx=40, pady=20, fill="x")
        grid = ctk.CTkFrame(s_card, fg_color="transparent")
        grid.pack(padx=25, pady=25, fill="x")
        
        m_col = ctk.CTkFrame(grid, fg_color="transparent")
        m_col.pack(side="left", expand=True)
        ctk.CTkLabel(m_col, text="Model Size", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.model_menu = ctk.CTkOptionMenu(m_col, values=["tiny", "base", "small", "medium", "large"], variable=self.model_choice, height=40, corner_radius=20, fg_color=self.accent_blue, command=self.update_model_status_view)
        self.model_menu.pack()
        self.model_stat_lbl = ctk.CTkLabel(m_col, text="Checking Status...", font=ctk.CTkFont(size=11))
        self.model_stat_lbl.pack(pady=5)

        a_col = ctk.CTkFrame(grid, fg_color="transparent")
        a_col.pack(side="left", expand=True)
        ctk.CTkLabel(a_col, text="Action", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        radio_row = ctk.CTkFrame(a_col, fg_color="transparent")
        radio_row.pack()
        ctk.CTkRadioButton(radio_row, text="Translate", variable=self.task_choice, value="translate").pack(side="left", padx=10)
        ctk.CTkRadioButton(radio_row, text="Transcribe", variable=self.task_choice, value="transcribe").pack(side="left", padx=10)

        self.p_bar = ctk.CTkProgressBar(self.home_frame, height=12, corner_radius=6, progress_color=self.accent_blue)
        self.p_bar.set(0)
        self.p_bar.pack(padx=60, pady=(40, 5), fill="x")
        self.status_lbl = ctk.CTkLabel(self.home_frame, text="System Idle", font=ctk.CTkFont(size=13))
        self.status_lbl.pack(pady=(0, 20))

        btn_row = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        btn_row.pack(pady=10)
        self.start_btn = ctk.CTkButton(btn_row, text="START", width=220, height=56, corner_radius=28, fg_color=self.accent_blue, text_color=("black", "white"), font=ctk.CTkFont(size=15, weight="bold"), command=self.begin_work)
        self.stop_btn = ctk.CTkButton(btn_row, text="STOP", width=160, height=56, corner_radius=28, fg_color="transparent", border_width=2, border_color=self.accent_red, text_color=("black", "white"), state="disabled", command=self.kill_work)
        self.start_btn.pack(side="left", padx=12)
        self.stop_btn.pack(side="left", padx=12)

    def build_settings(self):
        header = ctk.CTkLabel(self.settings_frame, text="Settings", font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(pady=(40, 20), padx=40, anchor="w")
        scroll_frame = ctk.CTkScrollableFrame(self.settings_frame, fg_color="transparent")
        scroll_frame.pack(padx=40, fill="both", expand=True)

        s_card = ctk.CTkFrame(scroll_frame, corner_radius=25, border_width=1)
        s_card.pack(pady=10, fill="x")
        ctk.CTkLabel(s_card, text="UI Theme", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=30, pady=(25, 5))
        self.theme_toggle = ctk.CTkSegmentedButton(s_card, values=["Light", "Dark"], command=lambda m: ctk.set_appearance_mode(m), height=45, corner_radius=22)
        self.theme_toggle.set("Dark")
        self.theme_toggle.pack(padx=30, pady=(0, 25), anchor="w")

        m_card = ctk.CTkFrame(scroll_frame, corner_radius=25, border_width=1)
        m_card.pack(pady=10, fill="x")
        ctk.CTkLabel(m_card, text="Model Management", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=30, pady=(25, 5))
        del_row = ctk.CTkFrame(m_card, fg_color="transparent")
        del_row.pack(fill="x", padx=30, pady=(0, 25))
        self.delete_model_choice = ctk.StringVar(value="tiny")
        ctk.CTkOptionMenu(del_row, values=["tiny", "base", "small", "medium", "large"], variable=self.delete_model_choice, height=40, corner_radius=20, command=self.check_delete_visibility).pack(side="left", padx=(0, 10))
        self.delete_btn = ctk.CTkButton(del_row, text="Delete Model", height=40, corner_radius=20, fg_color="transparent", border_width=1, border_color=self.accent_red, text_color=self.accent_red, command=self.delete_model)
        self.check_delete_visibility()

        ctk.CTkLabel(s_card, text="Requirements Status", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=30, pady=(10, 5))
        self.dep_container = ctk.CTkFrame(s_card, fg_color="transparent")
        self.dep_container.pack(fill="x", padx=30, pady=(0, 30))
        for engine, attr in [("FFmpeg Engine:", "ff"), ("Whisper AI:", "wh"), ("Python Core:", "py")]:
            row = ctk.CTkFrame(self.dep_container, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=engine, width=120, anchor="w").pack(side="left")
            stat_lbl = ctk.CTkLabel(row, text="Checking...", font=ctk.CTkFont(weight="bold"))
            stat_lbl.pack(side="left", padx=10)
            setattr(self, f"{attr}_stat_lbl", stat_lbl)

        btn_row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        btn_row.pack(pady=30, fill="x")
        self.repair_btn = ctk.CTkButton(btn_row, text="Install", height=45, corner_radius=22, fg_color=self.accent_blue, text_color=("black", "white"), command=lambda: self.manage_deps("install"))
        self.repair_btn.pack(side="left", padx=5)
        self.uninst_btn = ctk.CTkButton(btn_row, text="Uninstall", height=45, corner_radius=22, fg_color="transparent", border_width=1, border_color=self.accent_red, text_color=self.accent_red, command=lambda: self.manage_deps("uninstall"))
        self.uninst_btn.pack(side="left", padx=5)

    def build_credits(self):
        header = ctk.CTkLabel(self.credits_frame, text="Credits & Developer Info", font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(pady=(40, 20), padx=40, anchor="w")
        c_card = ctk.CTkFrame(self.credits_frame, corner_radius=25, border_width=1)
        c_card.pack(padx=40, pady=10, fill="both", expand=True)
        ctk.CTkLabel(c_card, text="Developed By", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.accent_blue).pack(pady=(30, 5))
        ctk.CTkLabel(c_card, text="Chaitanya Kumar Sathivada", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)
        ctk.CTkButton(c_card, text="View GitHub Profile", fg_color="transparent", border_width=1, command=lambda: webbrowser.open("https://github.com/ChaitanyaKumarS2403")).pack(pady=20)
        ctk.CTkLabel(c_card, text=f"Version: {self.version}", font=ctk.CTkFont(size=12)).pack(side="bottom", pady=(5, 5))
        self.copyright_lbl = ctk.CTkLabel(c_card, text="© Copy rights @ Chaitanya Kumar Sathivada", font=ctk.CTkFont(size=12))
        self.copyright_lbl.pack(side="bottom", pady=(5, 10))

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

    def check_system_health(self):
        ff_ok = shutil.which("ffmpeg") is not None
        wh_ok = importlib.util.find_spec("whisper") is not None
        py_ok = sys.version_info >= (3, 8)
        self.ff_stat_lbl.configure(text="Active" if ff_ok else "Missing", text_color="green" if ff_ok else self.accent_red)
        self.wh_stat_lbl.configure(text="Active" if wh_ok else "Missing", text_color="green" if wh_ok else self.accent_red)
        self.py_stat_lbl.configure(text="Active" if py_ok else "Missing", text_color="green" if py_ok else self.accent_red)
        status = "🟢 Engine Ready" if (ff_ok and wh_ok) else "🔴 Engine Missing"
        self.health_dot.configure(text=status, text_color="green" if (ff_ok and wh_ok) else self.accent_red)
        self.after(3000, self.check_system_health)

    def manage_deps(self, mode):
        def task():
            self.repair_btn.configure(state="disabled")
            self.uninst_btn.configure(state="disabled")
            try:
                if mode == "install":
                    if sys.platform == "win32":
                        subprocess.run(["powershell", "-Command", "winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements"], check=False)
                    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=False)
                    subprocess.run([sys.executable, "-m", "pip", "install", "openai-whisper", "ffmpeg-python"], check=False)
                else:
                    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "openai-whisper", "ffmpeg-python"], check=False)
                    if sys.platform == "win32":
                        subprocess.run(["powershell", "-Command", "winget uninstall --id Gyan.FFmpeg"], check=False)
                messagebox.showinfo("Success", "Process finished. CapIT will now restart.")
                self.restart_app()
            except:
                self.repair_btn.configure(state="normal")
                self.uninst_btn.configure(state="normal")
        threading.Thread(target=task).start()

    def restart_app(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Videos", "*.mp4 *.mkv *.avi *.mov")])
        if path: self.video_path.set(path)

    def monitor_download(self, file_path, target_mb):
        while not os.path.exists(file_path) and not self.stop_event.is_set():
            self.after(500)
            if not threading.main_thread().is_alive(): return

        while os.path.exists(file_path) and not self.stop_event.is_set():
            current_size = os.path.getsize(file_path) / (1024 * 1024)
            progress = min(current_size / target_mb, 1.0)
            self.p_bar.set(0.1 + (progress * 0.55)) 
            self.status_lbl.configure(text=f"Downloading Model: {int(progress*100)}%")
            if progress >= 0.99: break
            self.after(1000)

    def reset_ui(self):
        """Clears the file entry, resets progress bar, and status labels."""
        self.video_path.set("")
        self.p_bar.set(0)
        self.status_lbl.configure(text="System Idle")
        self.update_model_status_view()
        self.check_delete_visibility()

    def begin_work(self):
        if not self.video_path.get(): return
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        threading.Thread(target=self.process_engine, daemon=True).start()

    def kill_work(self): self.stop_event.set()

    def process_engine(self):
        try:
            import whisper
            import ffmpeg
            temp_path = os.path.join(tempfile.gettempdir(), "capit_audio.wav")
            
            self.status_lbl.configure(text="Extracting Audio...")
            self.p_bar.set(0.05)
            ffmpeg.input(self.video_path.get()).output(temp_path, acodec="pcm_s16le", ac=1, ar="16000").overwrite_output().run(quiet=True)
            
            m_name = self.model_choice.get()
            m_path = self.get_model_path(m_name)
            
            if not os.path.exists(m_path):
                monitor = threading.Thread(target=self.monitor_download, args=(m_path, self.model_sizes[m_name]), daemon=True)
                monitor.start()

            model = whisper.load_model(m_name)
            
            self.status_lbl.configure(text="AI Processing (Transcribing)...")
            self.p_bar.set(0.7)
            result = model.transcribe(temp_path, task=self.task_choice.get())
            
            self.p_bar.set(0.9)
            out_file = os.path.splitext(self.video_path.get())[0] + ".srt"
            with open(out_file, "w", encoding="utf-8") as f:
                for i, seg in enumerate(result["segments"], 1):
                    f.write(f"{i}\n{whisper.utils.format_timestamp(seg['start'])} --> {whisper.utils.format_timestamp(seg['end'])}\n{seg['text'].strip()}\n\n")
            
            self.p_bar.set(1.0)
            self.status_lbl.configure(text="Complete!")
            messagebox.showinfo("Done", "Captions Created Successfully.")
            # Trigger full UI reset
            self.after(100, self.reset_ui)

        except Exception as e:
            self.status_lbl.configure(text="Error occurred.")
            messagebox.showerror("Error", str(e))
            self.p_bar.set(0) # Reset on error too
        finally:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")

if __name__ == "__main__":
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('chaitanyakumar.capit.app.1000')
    app = CapIT()
    app.mainloop()