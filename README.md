# Radio Notebook

An offline desktop engineering notebook by James Lee for amateur-radio experiments. Version 0.1.0 is a working foundation using the same Python/Tkinter architecture as NMEA Workbench.

## What works

- Create, open, edit and save experiment JSON: question, equipment, procedure, observations and conclusion.
- Calculate wavelength, quarter-wave element and total half-wave dipole length, with an adjustable shortening factor.
- Calculate reflected-power percentage from SWR.
- Import CSV SWR sweeps, inspect measurements and plot frequency versus SWR.
- Open a synthetic demo and an editable antenna-comparison experiment template.

## Windows application

Open **Actions → Test and build Windows app**. After a successful run, download **Radio-Notebook-Windows** under Artifacts (GitHub sign-in required). Extract the entire ZIP into a permanent folder, then run **Radio-Notebook.exe**. Keep all included folders together. No Python installation is required for this package.

For a desktop icon, right-click the executable and select **Show more options → Send to → Desktop (create shortcut)**. Alternatively run the included `create_desktop_shortcut.ps1` with PowerShell. The first version uses the standard executable icon; custom artwork can be added later.

The workflow builds on pushes to main and can be run manually. Artifacts are retained for 30 days. An installer and published releases are future improvements.

## Editable source

Install Python 3.11+ with Tcl/Tk, download and extract the repository or clone it, then double-click `launch.cmd` on Windows. No pip packages are required for source mode. On macOS/Linux with Tk installed, run `python3 main.py`.

## Try the foundation

1. In Experiment notebook, click Open JSON and choose `data/templates/antenna_comparison.json`.
2. Customize the setup and save a copy in your own experiment folder.
3. Open Antenna tools and calculate a starting length for a frequency.
4. Open Measurements & plots and load the synthetic demo, or import your own CSV.
5. Write your interpretation in the experiment and save with Ctrl+S.

CSV format:

```csv
frequency_mhz,swr
146.0,1.5
146.5,1.2
147.0,1.4
```

Demo measurements are invented. Lowest sampled SWR is reported; the app does not infer the true resonant frequency. Measurement CSVs are opened separately and not embedded in notes. Notes save explicitly, with a discard prompt for unsaved changes.

## Folder organization

| Folder | Contents |
| --- | --- |
| `src/ui/` | Desktop interface |
| `src/radio/` | Calculations and measurement import |
| `src/notebook/` | Experiment persistence |
| `data/templates/` | Editable experiment templates |
| `assets/images/` | Application diagrams and photos |
| `assets/icons/` | Future application icon |
| `examples/measurements/` | Synthetic sample measurements |
| `docs/` | Guides and development scope |
| `scripts/` | Windows packaging and desktop shortcut |
| `tests/` | Calculation, validation and file checks |

Personal experiment files can live anywhere you choose. Keep them outside this repository unless you intend to publish them; `personal-experiments/` is ignored by Git.

## Development

```bash
python -m unittest discover -s tests -v
python main.py
```

Windows packaging:

```bash
python -m pip install -r requirements-build.txt
python scripts/build_windows.py
```

## Next steps

Link photos and measurement files to experiments; add equipment profiles, comparison plots, dB/feedline calculations, report exports and instrument-specific import formats. The current version does not connect to or control a radio.

Antenna lengths are initial geometric estimates requiring measurement and tuning. Reflected power is not antenna efficiency. No source redistribution license has been selected yet.
