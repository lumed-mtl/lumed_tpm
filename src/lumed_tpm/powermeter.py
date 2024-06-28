import pyvisa as visa


class Powermeter:

    def __init__(self):
        self.rm = visa.ResourceManager('@py')
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
        self.connected_devices = {}
        self.rm = visa.ResourceManager()
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
        if selected_idn in self.connected_devices:
            try:
                selected_addr = self.connected_devices[selected_idn]
                self.instr = self.rm.open_resource(selected_addr)
                self.idn = selected_idn
                self.connected = True
                return True, self.idn
            except visa.VisaIOError:
                return False, "Error connecting device."
        else:
            raise ValueError(
                "The selected device is not valid device. Verify the device is properly connected."
            )

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


if __name__ == "__main__":
    # rm = visa.ResourceManager('@py')
    # resources = rm.list_resources()
    # print(resources)


    newObj = Powermeter()
    newObj.connect_device("Thorlabs,PM100USB,1910986,1.7.0")
    
    newObj.disconnect_device()

    # with rm.open_resource(resources[0]) as instr:
    # print(instr.query('*IDN?'))
    # print (instr.query("MEAS:POW?"))
    # print(instr.query("SYST:SENS:IDN?"))

    # instr.write("MEAS:POW?")
    # print(instr.read())
