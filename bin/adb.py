# -*- coding: utf-8 -*- 
# @Time : 2020/10/15 9:38 
# @Author : 詹生松 
# @File : adb.py
import time
import uiautomator2 as u2
import warnings
import adbutils
from logzero import logger


class SignDevice(u2.Device):

    def __start_atx_agent(self):
        warnings.warn("start atx-agent ...", RuntimeWarning)
        ad = self._adb_device
        ad.shell([self._atx_agent_path, "server", "--stop"])
        ad.shell([self._atx_agent_path, "server", "--nouia", "-d"])
        deadline = time.time() + 3
        while time.time() < deadline:
            if self.agent_alive:
                return
        raise RuntimeError("atx-agent recover failed")

    def __wait_for_device(self, serial: str, timeout=60.0):
        """
        wait for device came online
        """
        deadline = time.time() + timeout
        first = True
        while time.time() < deadline:
            device = None
            for d in adbutils.adb.device_list():
                if d.serial == serial:
                    device = d
                    break
            if device:
                if not first:
                    logger.info("device(%s) came online", serial)
                return device
            if first:
                first = False
            else:
                logger.info("wait for device(%s), left(%.1fs)", serial, deadline - time.time())
            time.sleep(2.0)
        return None

    def _init_atx_agent(self, start_uiautomator=False, sign=False):
        """
        Install atx-agent and app-uiautomator apks, only usb connected device is ok
        """
        if self._connect_method != "usb":
            raise u2.ConnectError("http connection is down")

        assert self._connect_method == "usb"
        assert self._serial

        self._adb_device = self.__wait_for_device(self._serial)
        if not self._adb_device:
            raise RuntimeError("USB device %s is offline" % self._serial)

        ad = self._adb_device
        lport = ad.forward_port(7912)
        self._port = lport

        if self.agent_alive and self.alive:
            return

        if not sign:
            initer = u2.Initer(ad)
            if not initer.check_install():
                initer.install()  # same as run cli: uiautomator2 init

        if not self.agent_alive:
            self.__start_atx_agent()

        if start_uiautomator:
            if not self.alive:
                self.reset_uiautomator("atx-agent restarted")

    def init_atx_agent(self, start_uiautomator=False, sign=False):
        self._init_atx_agent(start_uiautomator=start_uiautomator, sign=sign)


def sign_connect_usb(serial=None, healthcheck=False, init=False, sign=False):
    """
    Args:
        serial (str): android device serial
        sign (bool): android device can`t install sign app.
    Returns:
        Device

    Raises:
        u2.ConnectError
    """
    adb = adbutils.AdbClient()
    if not serial:
        device = adb.device()
        serial = device.serial
    d = SignDevice()
    d._connect_method = "usb"
    d._serial = serial
    d.init_atx_agent(sign=sign)
    if healthcheck:
        warnings.warn("healthcheck param is deprecated", DeprecationWarning)
    if init:
        warnings.warn("init param is deprecated", DeprecationWarning)
    return d


class USBAdb:
    sign = False
    package = ""

    def __init__(self, sn):
        self.sn = sn
        self.usb = None
        self._connect(sign=self.sign)
        self._handler()
        self._stop()

    def change_sn(self, sn):
        self.sn = sn
        self._connect(sign=True)

    def _connect(self, sign=False):
        if self.usb is None:
            self.usb = sign_connect_usb(self.sn, sign=sign)
        if not self.usb.agent_alive and not self.usb.alive:
            self.usb = sign_connect_usb(self.sn, sign=sign)
        return self.usb

    @property
    def app_current(self):
        return self.usb.app_current()

    @property
    def dump_hierarchy(self):
        return self.usb.dump_hierarchy()

    def click_elem(self, conf: dict, timeout=10, callback=None, **kwargs):
        if self.elem_find(**conf).exists(timeout):
            self.elem_find(**conf).click()
            if callable(callback):
                return callback(**kwargs)
        return False

    def elem_find(self, **kwargs):
        return self.usb(**kwargs)

    def click_xy(self, x, y):
        self.usb.click(x, y)

    def _handler(self):
        self.app_start()
        self.handler()

    def app_start(self):
        self.usb.app_start(self.package, stop=True, wait=True)

    def handler(self):
        pass

    @staticmethod
    def bounds_position(elem_info: dict):
        bottom = elem_info.get("bounds", {}).get("bottom", -1)
        left = elem_info.get("bounds", {}).get("left", -1)
        right = elem_info.get("bounds", {}).get("right", -1)
        top = elem_info.get("bounds", {}).get("top", -1)
        return bottom, left, right, top

    @classmethod
    def sleep(cls, t: float):
        time.sleep(t)

    @classmethod
    def timestamps(cls):
        return time.time()

    def _stop(self):
        self.usb.app_stop(self.package)


if __name__ == "__main__":
    pass
