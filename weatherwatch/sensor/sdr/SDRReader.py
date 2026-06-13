import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from queue import Empty, Queue
from subprocess import PIPE, Popen
from typing import List

from conf.AppConfig import AppConfig
from conf.SensorConfig import SensorConfig
from entity.SDRMetricts import SDRMetrics
from py_singleton import singleton
from python_event_bus import EventBus
from repository.SDRMetricsRepository import SDRMetricsRepository
from sensor.sdr.BaseData import BaseData
from sensor.sdr.IndoorData import IndoorData
from sensor.sdr.OutdoorData import OutdoorData
from util.Converter import Converter
from util.Emailer import Emailer
from util.Logger import logger
from util.UsbReset import UsbReset

__all__ = ["SDRReader"]


@logger
class SensorEvent:
    """
    class to allow for async event
    """

    def __init__(self, evt: str, data: BaseData):
        """
        ctor
        :param self: this
        :param evt: event name
        :param data: event data
        """
        self._data = data
        self._evt = evt

    def fire(self):
        """
        fire event
        :param self: this
        """
        self.logger.debug("fire %s", self._evt)
        emailer = Emailer()
        try:
            EventBus.call(self._evt, self._data)
        except Exception as e:
            self.logger.exception("event processing error %s data\n%s", self._evt, self._data)
            emailer.send_error_notification(
                e,
                subject_prefix="sdr event Error",
            )


@logger
@singleton
class SDRReader:
    # pylint: disable=line-too-long
    """
    RTL-SDR sensor reader
    lib: https://github.com/merbanan/rtl_433
    dev receiver: https://www.nooelec.com/store/sdr/sdr-receivers/nesdr-smart-sdr.html?srsltid=AfmBOoqsEaIcHnJ1mghLBbE5q-Gf0NjyJYp46zaCQwDXRngPQauzruzT
    nano receiver: https://www.nooelec.com/store/nesdr-nano-three.html?srsltid=AfmBOoqo75MWaw153HkAv74eAI2DQ20mXLbyGMAAxUaYlXcehXMSOOzr
    linux install: https://www.nooelec.com/store/downloads/dl/file/id/72/product/0/nesdr_installation_manual_for_ubuntu.pdf
    indoor: /usr/local/bin/rtl_433 -M level -F json -R 20
    outdoor: /usr/local/bin/rtl_433 -M level -F json -R 153
    """  # noqa
    # pylint: enable=line-too-long

    ON_POSIX = "posix" in sys.builtin_module_names
    DEVICE_FLAG = "-R"

    RESET_KEY = "reset"

    # TODO externalize
    CMD_BASE = [
        "/usr/local/bin/rtl_433",
        "-q",
        "-M",
        "level",
        "-F",
        "json",
        "-f",
        "433920000",
        "-s",
        "1024000",
    ]

    def __init__(self):
        """
        ctor
        :param self: this
        """

        self._app_config: AppConfig = AppConfig()

        self._emailer = Emailer()

        reader_conf = self._app_config.conf[AppConfig.SDR_KEY][AppConfig.READER_KEY]
        self._timeout = reader_conf["timeout"]

        # usb re-enumeration recovery for a wedged RTL-SDR dongle (optional config)
        self._reset_conf: dict = reader_conf.get(SDRReader.RESET_KEY, {})
        self._usb_reset = UsbReset()

        # sensor read pool predefined thread
        self._read_pool = ThreadPoolExecutor(max_workers=1)

        self._sensors: dict = {}
        self._cmd = SDRReader.CMD_BASE.copy()
        for s in self._app_config.sensors:
            self._cmd.append(SDRReader.DEVICE_FLAG)
            self._cmd.append(str(s.device))
            self._sensors[s.key] = s

        self.logger.debug("sensors: %s", (str(self._sensors)))

        self._ignores: dict = self._app_config.ignores

        self.logger.debug("ignores: %s", (str(self._ignores)))

        # sensor data thread to fire event async
        self._data_pool = ThreadPoolExecutor(max_workers=len(self._sensors))

        self._reads = []

        self._sdr_metrics_repo = SDRMetricsRepository()

        # startup diagnostic: confirm the SDR dongle is on the usb bus
        self.detect_device()

    # override
    def __del__(self):
        self._read_pool.shutdown()
        self._data_pool.shutdown()

    def detect_device(self):
        """
        startup diagnostic: detect the configured SDR usb dongle on the bus

        logs the sysfs path when found; logs an error and emails a notification
        when the configured dongle is missing so a dead dongle is visible at
        boot rather than only after the first failed read cycle
        :param self: this
        """
        vendor_id = self._reset_conf.get("vendor_id")
        product_ids = self._reset_conf.get("product_ids", [])

        if not vendor_id or not product_ids:
            self.logger.warning("SDR usb device not configured - skipping startup dongle detection")
            return

        dev = self._usb_reset.find_device(vendor_id, product_ids)
        if dev is None:
            self.logger.error("SDR usb dongle %s:%s NOT detected at startup", vendor_id, product_ids)
            self._emailer.send_error_notification(
                Exception(f"SDR usb dongle {vendor_id}:{product_ids} not detected at startup"),
                subject_prefix="SDR Dongle Missing",
            )
        else:
            self.logger.info("SDR usb dongle detected at startup: %s (%s:%s)", dev, vendor_id, product_ids)

    @property
    def reads(self) -> List[BaseData]:
        """
        reads string property getter
        :param self: this
        :return: the reads
        """
        return self._reads

    def push_record(self, out, queue):
        """
        push sensor data (will be json) to queue
        :param src: the source name (not used)
        :param out: the output buffer to read data from
        :param queue: the queue to push data to
        """
        try:
            for line in out:
                try:
                    json.loads(line)
                    queue.put(line.strip())
                except ValueError:
                    self.logger.debug(line)
        except Exception:
            self.logger.exception("line processing error")
        finally:
            out.close()

    def process_record(self, line: str, sensors: dict, reads: List[BaseData], processed: List[str]):
        """
        process sensor data
        :param self: this
        :param line: the line to processes
        :param sensors: the set of sensors
        :param read: the set of existing reads
        :param processed: the set of keys already processed
        """
        self.logger.debug("sensor json: %s", line)
        j = json.loads(line)

        key = BaseData.key(j)
        self.logger.debug("incoming key: %s", key)

        if key in self._ignores:
            self.logger.debug("ignoring: %s", key)
        else:
            if key in sensors:
                sensor: SensorConfig = sensors[key]
                r: BaseData = None
                evt = None
                match sensor.data_class:
                    case IndoorData.__name__:
                        r = json.loads(line, object_hook=IndoorData.json_decoder)
                        evt = IndoorData.__name__
                    case OutdoorData.__name__:
                        r = json.loads(line, object_hook=OutdoorData.json_decoder)
                        evt = OutdoorData.__name__
                    case _:
                        self.logger.error("unkown impl for sensor: %s", sensor)

                if r is not None:
                    r.raw = json.loads(line)
                    r.config = sensor
                    reads.append(r)
                    # EventBus.call(evt, r)
                    se: SensorEvent = SensorEvent(evt, r)
                    self._data_pool.submit(se.fire)

                del sensors[key]
                processed.append(key)
            else:
                if key not in processed:
                    self.logger.warning("skipping: %s\n%s", key, line)

    def read(self):
        """
        read sensor data
        this will block until all sensors are read or until timeout

        when fewer than the configured min_reads sensors are read the SDR is
        considered wedged: the usb dongle is re-enumerated and the read retried
        up to max_retries times before giving up for this cycle
        :param self: this
        """
        reset_enabled = bool(self._reset_conf.get("enable", False))
        min_reads = int(self._reset_conf.get("min_reads", 1))
        max_retries = int(self._reset_conf.get("max_retries", 0))

        attempt = 0
        reads, sensors = self.read_once()

        while reset_enabled and len(reads) < min_reads and attempt < max_retries:
            attempt += 1
            self.logger.warning(
                "read %s sensor(s) (< %s) - re-enumerating SDR usb device (attempt %s/%s)",
                len(reads),
                min_reads,
                attempt,
                max_retries,
            )
            self.reset_sdr()
            reads, sensors = self.read_once()

        self._reads = reads

        for k, v in sensors.items():
            self.logger.warning("no data for %s=%s", k, v)
            if v.name == "outdoor":
                try:
                    raise Exception(f"no data for {k}={v}")
                except Exception as e:
                    self._emailer.send_error_notification(
                        e,
                        subject_prefix="SDR Sensor unread",
                    )

    def read_once(self):
        """
        perform a single sensor read pass
        this will block until all sensors are read or until timeout
        :param self: this
        :return: tuple of (reads, unread sensor config dict)
        """
        self.logger.debug("starting cmd: %s", self._cmd)
        sensors = self._sensors.copy()
        processed = []
        reads = []

        with Popen(
            self._cmd,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
            bufsize=1,
            close_fds=SDRReader.ON_POSIX,
        ) as p:

            q = Queue()

            # read sdr output
            self._read_pool.submit(self.push_record, p.stdout, q)

            start_monotonic = time.monotonic()
            start_time = datetime.now()
            duration = 0
            try:
                while len(reads) < len(self._sensors) and duration < self._timeout:
                    try:
                        data = q.get(timeout=10)
                    except Empty:
                        pass
                    else:  # got line
                        self.process_record(data, sensors, reads, processed)

                    sys.stdout.flush()
                    duration = Converter.duration_seconds(start_monotonic)

                    self.logger.debug("duration: %s reads %s", duration, len(reads))
                self.log_metrics(start_time, datetime.now(), duration, len(reads))
            except Exception as e:
                self._emailer.send_error_notification(
                    e,
                    subject_prefix="SDR Read Error",
                )
            finally:
                self.logger.info("stopping reader %s sec, reads %s", duration, len(reads))
                p.terminate()

        return reads, sensors

    def reset_sdr(self):
        """
        re-enumerate the SDR usb dongle to recover a wedged device
        :param self: this
        """
        try:
            ok = self._usb_reset.reset(
                self._reset_conf.get("vendor_id"),
                self._reset_conf.get("product_ids", []),
                settle_sec=int(self._reset_conf.get("settle_sec", 5)),
                wait_sec=int(self._reset_conf.get("wait_sec", 20)),
            )
            if not ok:
                self._emailer.send_error_notification(
                    Exception(
                        f"SDR usb reset failed for {self._reset_conf.get('vendor_id')}:"
                        f"{self._reset_conf.get('product_ids')}"
                    ),
                    subject_prefix="SDR USB Reset",
                )
        except Exception as e:
            self._emailer.send_error_notification(
                e,
                subject_prefix="SDR USB Reset",
            )

    def log_metrics(self, start_time: datetime, end_time: datetime, duration: int, sensor_cnt: int):
        """
        log metric data
        :param self: this
        :param start_time: processing start time
        :param end_time: processing end time
        :param sensor_cnt: the number of sensors
        """
        try:
            m: SDRMetrics = SDRMetrics()
            m.start_time = start_time
            m.end_time = end_time
            m.duration_sec = duration
            m.sensor_cnt = sensor_cnt

            self._sdr_metrics_repo.insert(m)
        except Exception:
            self.logger.exception("sensor read failed")
