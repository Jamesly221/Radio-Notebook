"""SI-unit calculations; antenna lengths are starting estimates."""
import math


def positive(value):
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError('Enter a finite number greater than zero.')
    return value


def antenna_lengths(frequency_mhz, factor=0.95):
    f = positive(frequency_mhz)
    k = positive(factor)
    if k > 1:
        raise ValueError('Length factor must be between 0 and 1.')
    wavelength = 299.792458 / f
    return wavelength, wavelength * k / 4, wavelength * k / 2


def reflected_percent(swr):
    swr = positive(swr)
    if swr < 1:
        raise ValueError('SWR must be at least 1.')
    return 100 * ((swr - 1) / (swr + 1)) ** 2
