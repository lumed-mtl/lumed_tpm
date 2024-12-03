import logging
from threading import Lock

import numpy as np
import pyvisa

logger = logging.getLogger()


class Powermeter:

    def __init__(self):
        self._ressource_manager = pyvisa.ResourceManager("@py")
        self._instrument: pyvisa.resources.serial.SerialInstrument | None = None
        self.isconnected: bool = False
        self._model: str = ""
        self._serial_number: str = ""
        self._firmware_version: str = ""
        self._mutex: Lock = Lock()

    # Basic methods

    def _safe_scpi_query(self, message: str) -> str:
        with self._mutex:
            try:
                answer = self._instrument.query(message).strip()
            except Exception as e:
                logger.error(e)

        return answer

    def _safe_scpi_write(self, message: str) -> None:
        with self._mutex:
            try:
                _ = self._instrument.write(message)
            except Exception as e:
                logger.error(e)

    def find_thorlabs_pm(self) -> dict:
        ressources = self._ressource_manager.list_resources("?*USB?*")
        ressources = [r for r in ressources if "INSTR" in r]
        available_powermeters = {}
        for ressource in ressources:
            try:
                with self._ressource_manager.open_resource(ressource) as instr:
                    instr.timeout = 200
                    idn = instr.query("*IDN?").strip()
                    if "thorlab" in idn.lower() and "pm" in idn.lower():
                        available_powermeters[ressource] = idn
            except Exception as e:
                logger.debug(e)
        return available_powermeters

    def connect(self, ressource: str) -> None:
        try:
            self._instrument = self._ressource_manager.open_resource(ressource)
            self._instrument.timeout = 200
            self.isconnected = True
            self._model, self._serial_number, self._firmware_version = self.get_id()
        except Exception as e:
            logger.error(e)
            self.isconnected = False

    def auto_connect(self):
        try:
            available_powermeters = self.find_thorlabs_pm()
            logger.debug("found powermeters %s", available_powermeters)
            device = list(self.find_thorlabs_pm())[0]
            logger.debug("attempting connection to %s", device)
            self.connect(device)
        except Exception as e:
            logger.error(e)

    def disconnect(self):
        if not self.isconnected:
            return

        try:
            self._instrument.close()
            self.isconnected = False
        except Exception as e:
            logger.error(e)

    # Getters

    def get_id(self) -> list[str, str, str]:
        try:
            answer = self._safe_scpi_query("*IDN?")
            _, model, serial_number, firmware = answer.split(",")
        except Exception as e:
            logger.error(e)
            model = ""
            serial_number = ""
            firmware = ""

        return model, serial_number, firmware

    def get_average_count(self) -> int:
        try:
            answer = self._safe_scpi_query("sense:average:count?")
            count = int(answer)
        except Exception as e:
            logger.error(e)
            count = np.nan

        return count

    def get_correction_wavelength(self) -> int:
        try:
            answer = self._safe_scpi_query("sense:correction:wavelength?")
            wavelength = int(float(answer))
        except Exception as e:
            logger.error(e)
            wavelength = np.nan

        return wavelength

    def get_correction_wavelength_min(self) -> int:
        try:
            answer = self._safe_scpi_query("sense:correction:wavelength? minimum")
            wavelength = int(float(answer))
        except Exception as e:
            logger.error(e)
            wavelength = np.nan

        return wavelength

    def get_correction_wavelength_max(self) -> int:
        try:
            answer = self._safe_scpi_query("sense:correction:wavelength? maximum")
            wavelength = int(float(answer))
        except Exception as e:
            logger.error(e)
            wavelength = np.nan

        return wavelength

    def get_auto_range(self) -> bool:
        try:
            answer = self._safe_scpi_query("power:dc:range:auto?")
            isauto = bool(int(answer))
        except Exception as e:
            logger.error(e)
            isauto = False

        return isauto

    def get_range(self) -> float:
        try:
            answer = self._safe_scpi_query("power:dc:range?")
            current_range = float(answer)
        except Exception as e:
            logger.error(e)
            current_range = np.nan

        return current_range

    def get_power_unit(self) -> str:
        try:
            unit = self._safe_scpi_query("power:dc:unit?")
        except Exception as e:
            logger.error(e)
            unit = ""

        return unit

    def get_power(self) -> float:
        try:
            answer = self._safe_scpi_query("measure:power?")
            power = float(answer)
        except Exception as e:
            logger.error(e)
            power = np.nan

        return power

    # Setters

    def set_average_count(self, count: int = 1) -> None:
        try:
            self._safe_scpi_write(f"sense:average:count {count}")
        except Exception as e:
            logger.error(e)

    def set_correction_wavelength(self, wavelength: int = 635) -> None:
        try:
            answer = self._safe_scpi_write(f"sense:correction:wavelength {wavelength}")
        except Exception as e:
            logger.error(e)

    def set_auto_range(self, auto_range: bool = False) -> None:
        try:
            auto_range = "ON" if auto_range else "OFF"
            self._safe_scpi_write(f"power:dc:range:auto {auto_range}")
        except Exception as e:
            logger.error(e)

    def set_range(self, upper: float) -> None:
        try:
            self._safe_scpi_write(f"power:dc:range {upper}")
        except Exception as e:
            logger.error(e)

    def set_power_unit(self, unit: str = "W") -> str:
        try:
            self._safe_scpi_write(f"power:dc:unit {unit}")
        except Exception as e:
            logger.error(e)

        return unit


if __name__ == "__main__":
    pm_ = Powermeter()

    devices_ = pm_.find_thorlabs_pm()
    device = list(devices_)[0]
    print(device)
    pm_.connect(device)

    print("connected:", pm_.isconnected)
    print("model:", pm_._model, "serial:", pm_._serial_number)

    pm_.set_correction_wavelength(785)
    print("correction wavelength:", pm_.get_correction_wavelength())

    pm_.set_auto_range(True)
    print("auto range:", pm_.get_auto_range())

    pm_.set_range(50e-3)
    print("current range:", pm_.get_range())
    print("auto range:", pm_.get_auto_range())

    pm_.set_power_unit("W")
    print("current power unit:", pm_.get_power_unit())

    print("Power : ", pm_.get_power(), pm_.get_power_unit())

    print("Min cor wl : ", pm_.get_correction_wavelength_min())
    print("Max cor wl : ", pm_.get_correction_wavelength_max())

    pm_.disconnect()
    print("connected:", pm_.isconnected)
