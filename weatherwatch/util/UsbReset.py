import time
from pathlib import Path
from typing import List

from util.Logger import logger

__all__ = ["UsbReset"]


@logger
class UsbReset:
    """
    re-enumerate a usb device via the sysfs 'authorized' flag (0 -> 1)

    this is the equivalent of a physical unplug/replug: the host controller
    drops and re-enumerates the device, which clears a wedged RTL-SDR dongle
    that has fallen off the bus or been left in a bad state by librtlsdr.

    requires root to write /sys/bus/usb/devices/*/authorized (the weatherwatch
    service runs as root).
    """

    USB_DEVICES = "/sys/bus/usb/devices"

    VENDOR_FILE = "idVendor"
    PRODUCT_FILE = "idProduct"
    AUTHORIZED_FILE = "authorized"

    def find_device(self, vendor_id: str, product_ids: List[str]) -> Path:
        """
        locate the sysfs path of a usb device by vendor / product id
        :param self: this
        :param vendor_id: usb idVendor (e.g. "0bda")
        :param product_ids: acceptable idProduct values (e.g. ["2838", "2832"])
        :return: the sysfs device path, or None when no match is found
        """
        for dev in Path(UsbReset.USB_DEVICES).glob("*"):
            vid = dev / UsbReset.VENDOR_FILE
            pid = dev / UsbReset.PRODUCT_FILE
            authorized = dev / UsbReset.AUTHORIZED_FILE

            # interface nodes (e.g. 1-1:1.0) have no idVendor; skip them
            if not (vid.is_file() and pid.is_file() and authorized.is_file()):
                continue

            if vid.read_text().strip() == vendor_id and pid.read_text().strip() in product_ids:
                return dev

        return None

    def present(self, vendor_id: str, product_ids: List[str]) -> bool:
        """
        check whether a usb device matching vendor / product id is present
        :param self: this
        :param vendor_id: usb idVendor
        :param product_ids: acceptable idProduct values
        :return: True when the device is found on the usb bus
        """
        return self.find_device(vendor_id, product_ids) is not None

    def reset(self, vendor_id: str, product_ids: List[str], settle_sec: int = 5, wait_sec: int = 20) -> bool:
        """
        re-enumerate the matching usb device
        :param self: this
        :param vendor_id: usb idVendor
        :param product_ids: acceptable idProduct values
        :param settle_sec: seconds to hold the device de-authorized before re-authorizing
        :param wait_sec: seconds to wait for the device to re-authorize after reset
        :return: True when the device was reset and came back authorized
        """
        dev = self.find_device(vendor_id, product_ids)
        if dev is None:
            self.logger.error("usb device %s:%s not found - cannot reset", vendor_id, product_ids)
            return False

        authorized = dev / UsbReset.AUTHORIZED_FILE
        self.logger.warning("resetting usb device at %s (%s:%s)", dev, vendor_id, product_ids)

        try:
            authorized.write_text("0")
            time.sleep(settle_sec)
            authorized.write_text("1")
        except OSError:
            self.logger.exception("failed to write %s - is the service running as root?", authorized)
            return False

        for i in range(wait_sec):
            if authorized.is_file() and authorized.read_text().strip() == "1":
                self.logger.info("usb device %s re-authorized after reset (%ss)", dev, i)
                return True
            time.sleep(1)

        self.logger.error("usb device %s:%s did not re-authorize after reset", vendor_id, product_ids)
        return False
