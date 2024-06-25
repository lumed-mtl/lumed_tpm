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

    def list_devices(self):
        """
        Scan all connected devices to computer

        Returns
        -------
        dict_connected_devices, dict
            Dictionary of all found devices. Format: {idn1:address1, idn2:address2, ...}
        """
        self.dict_connected_devices = {}
        self.rm = visa.ResourceManager()
        for addr in self.rm.list_resources():
            try:
                with self.rm.open_resource(addr) as instr:
                    idn = instr.query("*IDN?").rstrip("\n")
                    self.dict_connected_devices[idn] = addr
            except visa.VisaIOError:
                pass
        # self.dict_connected_devices = {'Thorlabs,PM100USB,1910986,1.7.0':'USB0::4883::32882::1910986::0::INSTR'}
        return self.dict_connected_devices

