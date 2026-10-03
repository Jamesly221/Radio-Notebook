import tempfile
import unittest
from pathlib import Path
from src.radio.calculations import antenna_lengths, reflected_percent
from src.radio.measurements import read_sweep
from src.notebook.storage import load_experiment, save_experiment


class CoreTests(unittest.TestCase):
    def test_physics(self):
        wave, quarter, half = antenna_lengths(150, 1)
        self.assertAlmostEqual(wave, 1.9986163867)
        self.assertAlmostEqual(half, 2 * quarter)
        self.assertEqual(reflected_percent(1), 0)
        self.assertAlmostEqual(reflected_percent(3), 25)
        for bad in (0, -1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                antenna_lengths(bad)
        with self.assertRaises(ValueError):
            reflected_percent(0.9)

    def test_files(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'experiment.json'
            save_experiment(path, {'title': 'FT-5DR antenna test', 'observations': 'Δ repeatability'})
            self.assertEqual(load_experiment(path)['observations'], 'Δ repeatability')
            save_experiment(path, {'title': 'Revised'})
            self.assertEqual(load_experiment(path)['title'], 'Revised')
            path.write_text('{"schema_version": 2}')
            with self.assertRaises(ValueError):
                load_experiment(path)

    def test_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'sweep.csv'
            path.write_text('frequency_mhz,swr\n147,2\n146,1.2\n')
            self.assertEqual(read_sweep(path), [(146, 1.2), (147, 2)])
            for content in ('frequency,swr\n146,1\n', 'frequency_mhz,swr\n146,0.5\n', 'frequency_mhz,swr\n146,nan\n', 'frequency_mhz,swr\n'):
                path.write_text(content)
                with self.assertRaises(ValueError):
                    read_sweep(path)
