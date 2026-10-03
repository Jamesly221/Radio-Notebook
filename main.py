import sys
import tkinter as tk
from src.ui.app import RadioNotebook


def main():
    root = tk.Tk()
    app = RadioNotebook(root)
    if '--smoke-test' in sys.argv:
        app.calculate()
        app.load_sweep(app.base / 'examples/measurements/demo_swr.csv')
        root.update()
        assert len(app.points) == 7
        assert 'Quarter' in app.results.get()
        root.destroy()
    else:
        root.mainloop()


if __name__ == '__main__':
    main()
