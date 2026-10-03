"""Local desktop notebook. UI is separate from calculations and persistence."""
import json
import sys
from datetime import date
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.radio.calculations import antenna_lengths, reflected_percent
from src.radio.measurements import read_sweep
from src.notebook.storage import FIELDS, load_experiment, save_experiment


class RadioNotebook:
    def __init__(self, root):
        self.root = root
        self.base = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parents[2]
        self.path = None
        self.dirty = False
        self.points = []
        root.title('Radio Notebook | James Lee')
        root.geometry('1080x780')
        root.minsize(850, 650)
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('TFrame', background='#edf2f5')
        style.configure('TLabel', background='#edf2f5', foreground='#152f42', font=('Segoe UI', 10))
        style.configure('TButton', padding=7)
        style.configure('TNotebook.Tab', padding=(20, 10))
        ttk.Label(root, text='RADIO NOTEBOOK', font=('Segoe UI', 22, 'bold')).pack(anchor='w', padx=24, pady=(20, 2))
        ttk.Label(root, text='Ask a question. Measure it. Explain what you learned.').pack(anchor='w', padx=24, pady=(0, 16))
        tabs = ttk.Notebook(root)
        tabs.pack(fill='both', expand=True, padx=20, pady=8)
        frames = []
        for label in ('Experiment notebook', 'Antenna tools', 'Measurements & plots', 'Project guide'):
            frame = ttk.Frame(tabs, padding=16)
            tabs.add(frame, text=label)
            frames.append(frame)
        self.build_notebook(frames[0])
        self.build_tools(frames[1])
        self.build_measurements(frames[2])
        guide = tk.Text(frames[3], wrap='word', font=('Segoe UI', 11), padx=16, pady=16)
        guide.pack(fill='both', expand=True)
        guide.insert('1.0', (self.base / 'docs/PROJECT_GUIDE.txt').read_text(encoding='utf-8'))
        guide.configure(state='disabled')
        self.status = tk.StringVar(value='Ready • Your experiments stay in files you choose.')
        ttk.Label(root, textvariable=self.status).pack(anchor='w', padx=24, pady=10)
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.bind('<Control-s>', lambda event: self.save())
        root.bind('<Control-o>', lambda event: self.open())

    def build_notebook(self, frame):
        bar = ttk.Frame(frame)
        bar.pack(fill='x', pady=(0, 10))
        for title, command in [('New', self.new), ('Open JSON', self.open), ('Save', self.save), ('Save as', lambda: self.save(True))]:
            ttk.Button(bar, text=title, command=command).pack(side='left', padx=(0, 8))
        self.entries = {}
        for field in FIELDS:
            row = ttk.Frame(frame)
            row.pack(fill='both', expand=field not in ('title', 'date'), pady=3)
            ttk.Label(row, text=field.capitalize(), width=15).pack(side='left', anchor='n')
            text = tk.Text(row, height=1 if field in ('title', 'date') else 3, wrap='word', undo=True, font=('Segoe UI', 10))
            text.pack(side='left', fill='both', expand=True)
            text.bind('<<Modified>>', self.modified)
            self.entries[field] = text
        self.fill({'date': date.today().isoformat()})

    def modified(self, event):
        if event.widget.edit_modified():
            self.dirty = True
            event.widget.edit_modified(False)

    def fill(self, values):
        for key, widget in self.entries.items():
            widget.delete('1.0', 'end')
            widget.insert('1.0', values.get(key, ''))
            widget.edit_modified(False)
        self.dirty = False

    def discard(self):
        return not self.dirty or messagebox.askyesno('Unsaved experiment', 'Discard unsaved changes?')

    def new(self):
        if self.discard():
            self.path = None
            self.fill({'date': date.today().isoformat()})
            self.status.set('New experiment')

    def open(self):
        if not self.discard():
            return
        path = filedialog.askopenfilename(filetypes=[('Experiments', '*.json')])
        if path:
            try:
                values = load_experiment(path)
                self.fill(values)
                self.path = path
                self.status.set(f'Opened {path}')
            except (OSError, ValueError) as error:
                messagebox.showerror('Could not open', str(error))

    def save(self, save_as=False):
        path = self.path if not save_as else None
        if not path:
            path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('Experiment', '*.json')])
        if path:
            try:
                save_experiment(path, {key: widget.get('1.0', 'end-1c') for key, widget in self.entries.items()})
                self.path, self.dirty = path, False
                self.status.set(f'Saved {path}')
            except OSError as error:
                messagebox.showerror('Could not save', str(error))

    def close(self):
        if self.discard():
            self.root.destroy()

    def build_tools(self, frame):
        ttk.Label(frame, text='Antenna starting dimensions', font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=8)
        self.frequency, self.factor, self.swr = tk.StringVar(value='146.52'), tk.StringVar(value='0.95'), tk.StringVar(value='1.5')
        for label, variable in [('Frequency (MHz)', self.frequency), ('Length factor (0–1)', self.factor), ('Measured SWR (≥1)', self.swr)]:
            row = ttk.Frame(frame)
            row.pack(anchor='w', pady=8)
            ttk.Label(row, text=label, width=25).pack(side='left')
            ttk.Entry(row, textvariable=variable, width=18).pack(side='left')
        ttk.Button(frame, text='Calculate', command=self.calculate).pack(anchor='w', pady=12)
        self.results = tk.StringVar()
        ttk.Label(frame, textvariable=self.results, font=('Consolas', 13), justify='left').pack(anchor='w', pady=16)
        ttk.Label(frame, text='Length estimates use c/f and your shortening factor.\nHalf-wave is total dipole length; each leg is half that length.\nConstruction, nearby objects and feed arrangement affect tuning.\nReflected power describes mismatch; it does not measure antenna efficiency.', wraplength=730).pack(anchor='w', pady=12)
        self.calculate()

    def calculate(self):
        try:
            wave, quarter, half = antenna_lengths(self.frequency.get(), self.factor.get())
            reflection = reflected_percent(self.swr.get())
            self.results.set(f'Free-space wavelength: {wave:.4f} m\nQuarter-wave element:  {quarter:.4f} m / {quarter * 100:.2f} cm\nHalf-wave dipole total: {half:.4f} m\nEach dipole leg:       {half / 2:.4f} m\nReflected power:      {reflection:.2f}%')
        except ValueError as error:
            messagebox.showerror('Check inputs', str(error))

    def build_measurements(self, frame):
        bar = ttk.Frame(frame)
        bar.pack(fill='x')
        ttk.Button(bar, text='Import SWR CSV', command=self.choose_sweep).pack(side='left', padx=(0, 10))
        ttk.Button(bar, text='Load synthetic demo', command=lambda: self.load_sweep(self.base / 'examples/measurements/demo_swr.csv')).pack(side='left')
        self.summary = tk.StringVar(value='CSV columns: frequency_mhz,swr • Demo values are synthetic.')
        ttk.Label(frame, textvariable=self.summary).pack(anchor='w', pady=12)
        self.canvas = tk.Canvas(frame, background='white', highlightthickness=0, height=320)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind('<Configure>', lambda event: self.draw())
        self.table = ttk.Treeview(frame, columns=('f', 's'), show='headings', height=5)
        self.table.heading('f', text='Frequency (MHz)')
        self.table.heading('s', text='SWR')
        scroll = ttk.Scrollbar(frame, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side='left', fill='x', expand=True, pady=10)
        scroll.pack(side='right', fill='y', pady=10)

    def choose_sweep(self):
        path = filedialog.askopenfilename(filetypes=[('SWR measurements', '*.csv')])
        if path:
            self.load_sweep(path)

    def load_sweep(self, path):
        try:
            points = read_sweep(path)
        except (OSError, ValueError, UnicodeError) as error:
            messagebox.showerror('Could not import', str(error))
            return
        self.points = points
        self.table.delete(*self.table.get_children())
        for f, s in points:
            self.table.insert('', 'end', values=(f'{f:g}', f'{s:g}'))
        f, s = min(points, key=lambda point: point[1])
        self.summary.set(f'{Path(path).name} • {len(points)} points • Lowest sampled SWR {s:g} at {f:g} MHz')
        self.draw()

    def draw(self):
        c = self.canvas
        c.delete('all')
        w, h = max(c.winfo_width(), 300), max(c.winfo_height(), 220)
        if not self.points:
            c.create_text(w/2, h/2, text='Import measurements or load the synthetic demo.', fill='#52677a')
            return
        lo, hi = self.points[0][0], self.points[-1][0]
        if hi == lo:
            lo, hi = lo - 0.5, hi + 0.5
        top = max(2, max(s for _, s in self.points) * 1.1)
        for i in range(5):
            y = h - 45 - i * (h - 75) / 4
            c.create_line(65, y, w-20, y, fill='#e5ebef')
            c.create_text(40, y, text=f'{1 + (top-1)*i/4:.1f}')
        coordinates = []
        for f, s in self.points:
            x = 65 + (f-lo)/(hi-lo)*(w-85)
            y = h-45 - (s-1)/(top-1)*(h-75)
            coordinates.extend((x,y))
        if len(coordinates) >= 4:
            c.create_line(*coordinates, fill='#087f8c', width=2)
        for x,y in zip(coordinates[::2], coordinates[1::2]):
            c.create_oval(x-3,y-3,x+3,y+3,fill='#087f8c',outline='')
        c.create_text(65,h-25,text=f'{lo:g}',anchor='w')
        c.create_text(w-20,h-25,text=f'{hi:g}',anchor='e')
        c.create_text(w/2,h-10,text='Frequency (MHz)')
        c.create_text(30,15,text='SWR')
