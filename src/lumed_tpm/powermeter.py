import pyvisa as visa


class Powermeter:

    def __init__(self):
        self.rm = visa.ResourceManager("@py")
        self.connected = False
        self.idn = None  # identity, i.e. device model
        self.measuring = None
        self._wavelength = None
        self._power = None
        self._power_units = None
        self._averaging_rate = None

    def list_devices(self):
        """
        Scan all connected devices to computer

        Returns
        -------
        dict_connected_devices, dict
            Dictionary of all found devices. Format: {idn1:address1, idn2:address2, ...}
        """
        self.connected_devices = {}
        self.rm = visa.ResourceManager("@py")
        for addr in self.rm.list_resources():
            try:
                with self.rm.open_resource(addr) as instr:
                    idn = instr.query("*IDN?").rstrip("\n")
                    self.connected_devices[idn] = addr
            except visa.VisaIOError:
                pass
        return self.connected_devices

    def connect_device(self, selected_idn):
        """
        Connects the selected device in the gui

        Returns
        -------
        (bool, str), list
            bool: True if device successfully connected, False otherwise. str: idn if connected, error message otherwise.
        """
        self.list_devices()
        if self.connected == False:
            if selected_idn in self.connected_devices:
                try:
                    selected_addr = self.connected_devices[selected_idn]
                    self.instr = self.rm.open_resource(selected_addr)
                    self.idn = selected_idn
                    self.__initialize_properties()
                    return True, self.idn
                except visa.VisaIOError:
                    return False, "Error connecting device."
            else:
                raise ValueError(
                    "The selected device is not a valid device. Verify the device is properly connected."
                )
        else:
            raise ValueError("A device is already connected.")

    def disconnect_device(self):
        """
        Disconnects the currently connected device

        Returns
        -------
        (bool, str), list
            bool: True if device successfully disconnected, False otherwise. str: success message if disconnected, error message otherwise.
        """
        if self.connected == True:
            try:
                self.instr.close()
                self.connected = False
                return True, "Successfully disconnected device."
            except Exception as e:
                return False, e
        else:
            raise ValueError("No device connected.")

    def __initialize_properties(self):
        self.connected = True
        self.measuring = False
        self.wavelength
        self.averaging_rate = 1
        self.power_units = "W"

    @property
    def power(self):
        if self.connected:
            if self._power_units == None:
                self._power_units = "W"  # sets the default units to Watts
            self.instr.write("power:dc:unit " + self._power_units.upper())
            self._power = float(self.instr.query("measure:power?"))
            return self._power, self._power_units
        else:
            self._power, self._power_units = None, None
            raise RuntimeError("No device connected.")

    @property
    def power_units(self):
        if self.connected:
            return self._power_units
        else:
            self._power, self._power_units = None, None
            raise RuntimeError("No device connected.")

    @power_units.setter
    def power_units(self, units):
        if self.connected:
            self._power_units = units
            self.instr.write("power:dc:unit " + self._power_units.upper())
            return self._power_units
        else:
            self._power, self._power_units = None, None
            raise RuntimeError("No device connected.")

    @property
    def wavelength(self):
        if self.connected:
            self._wavelength = self.instr.query("SENS:CORR:WAV?")
            return self._wavelength
        else:
            raise RuntimeError("No device connected.")

    @property
    def averaging_rate(self):
        if self.connected:
            return self._averaging_rate
        else:
            raise RuntimeError("No device connected.")

    @averaging_rate.setter
    def averaging_rate(self, N):
        if self.connected:
            try:
                rate = int(N)
                if rate <= 0:
                    self._averaging_rate = 1
                else:
                    self._averaging_rate = rate
            except:
                self._averaging_rate = 1
            self.instr.write(f"AVER:COUNT {self._averaging_rate}")
            return self._averaging_rate
        else:
            raise RuntimeError("No device connected.")
