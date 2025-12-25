import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import subprocess
import threading
import sys
import os

class M4BConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("M4B Converter GUI")
        self.root.geometry("800x600")

        # Variables
        self.files = []
        self.output_dir = tk.StringVar()
        self.custom_name = tk.StringVar(value="%(title)s")
        self.no_mp4v2 = tk.BooleanVar(value=True)
        self.skip_encoding = tk.BooleanVar(value=False)
        self.debug = tk.BooleanVar(value=False)
        self.pipe_wav = tk.BooleanVar(value=False)

        # UI Layout
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # File Selection
        file_frame = ttk.LabelFrame(main_frame, text="Input Files", padding="5")
        file_frame.pack(fill=tk.X, pady=5)
        
        self.file_listbox = tk.Listbox(file_frame, height=5)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y)
        ttk.Button(btn_frame, text="Add Files...", command=self.add_files).pack(pady=2)
        ttk.Button(btn_frame, text="Clear", command=self.clear_files).pack(pady=2)

        # Output Directory
        out_frame = ttk.Frame(main_frame)
        out_frame.pack(fill=tk.X, pady=5)
        ttk.Label(out_frame, text="Output Directory:").pack(side=tk.LEFT)
        ttk.Entry(out_frame, textvariable=self.output_dir).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(out_frame, text="Browse...", command=self.browse_output).pack(side=tk.LEFT)

        # Options
        opt_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        opt_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(opt_frame, text="Use ffmpeg for metadata (--no-mp4v2)", variable=self.no_mp4v2).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(opt_frame, text="Skip encoding (--skip-encoding)", variable=self.skip_encoding).grid(row=0, column=1, sticky=tk.W)
        ttk.Checkbutton(opt_frame, text="Debug mode (--debug)", variable=self.debug).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(opt_frame, text="Pipe WAV (--pipe-wav)", variable=self.pipe_wav).grid(row=1, column=1, sticky=tk.W)

        ttk.Label(opt_frame, text="Custom Chapter Name:").grid(row=2, column=0, sticky=tk.W, pady=(5,0))
        ttk.Entry(opt_frame, textvariable=self.custom_name).grid(row=2, column=1, sticky=tk.EW, pady=(5,0))
        
        opt_frame.columnconfigure(1, weight=1)

        # Run Button
        self.run_btn = ttk.Button(main_frame, text="Start Conversion", command=self.start_conversion)
        self.run_btn.pack(pady=10)

        # Log Output
        log_frame = ttk.LabelFrame(main_frame, text="Log Output", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled', height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def add_files(self):
        filenames = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.m4b *.mp3 *.mp4"), ("All Files", "*.*")])
        for f in filenames:
            self.files.append(f)
            self.file_listbox.insert(tk.END, os.path.basename(f))

    def clear_files(self):
        self.files = []
        self.file_listbox.delete(0, tk.END)

    def browse_output(self):
        d = filedialog.askdirectory()
        if d:
            self.output_dir.set(d)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def start_conversion(self):
        if not self.files:
            self.log("No input files selected.\n")
            return
        
        self.run_btn.config(state='disabled')
        thread = threading.Thread(target=self.run_process)
        thread.start()

    def run_process(self):
        cmd = [sys.executable, "m4b.py", "--assume-yes"]
        
        if self.output_dir.get():
            cmd.extend(["--output-dir", self.output_dir.get()])
        
        if self.custom_name.get():
            cmd.extend(["--custom-name", self.custom_name.get()])

        if self.no_mp4v2.get():
            cmd.append("--no-mp4v2")
        
        if self.skip_encoding.get():
            cmd.append("--skip-encoding")
            
        if self.debug.get():
            cmd.append("--debug")

        if self.pipe_wav.get():
            cmd.append("--pipe-wav")

        cmd.extend(self.files)

        self.log("Running command: " + " ".join(cmd) + "\n\n")
        
        try:
            # Determine startupinfo to hide window on Windows, irrelevant on macOS
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                startupinfo=startupinfo,
                text=True, # Python 3.7+
                bufsize=1,
                universal_newlines=True
            )

            for line in process.stdout:
                self.log(line)

            process.wait()
            self.log("\nProcess finished with exit code: %d\n" % process.returncode)
            
        except Exception as e:
            self.log("\nError starting process: %s\n" % str(e))
        finally:
            self.root.after(0, lambda: self.run_btn.config(state='normal'))

if __name__ == "__main__":
    root = tk.Tk()
    app = M4BConverterApp(root)
    root.mainloop()
