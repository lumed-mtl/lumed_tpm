import pyvisa as visa


class powermeter:

    def __init__(self):
        self.rm = visa.ResourceManager()
        self.connected = False
        self.idn = None  # identity, i.e. device model
        self._wavelength = None
        self._auto_power_range = None
        self._power_range = None
        self._power = None
        self._power_units = None
        self._min_power_range = None
        self._max_power_range = None
        self.min_wavelength = None
        self.max_wavelength = None

