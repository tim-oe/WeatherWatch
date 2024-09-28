import io

from apscheduler.schedulers.background import BackgroundScheduler

from conf.AppConfig import AppConfig
from conf.SchedulerConfig import SchedulerConfig
from svc.SensorSvc import SensorSvc

__all__ = ["SchedulerSvc"]


class SchedulerSvc(object):
    SENSOR_JOB = "sensor"

    """
    SchedulerSvc service
    sets up automated tasks
    https://apscheduler.readthedocs.io/en/3.x/index.html
    """

    # override for singleton
    # https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(SchedulerSvc, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self._schedulerConfig: SchedulerConfig = AppConfig().scheduler
        self._scheduler = BackgroundScheduler()
        self._sensorSvc = SensorSvc()

        self._scheduler.add_job(
            self._sensorSvc.process,
            "interval",
            minutes=self._schedulerConfig.sensorInterval,
            max_instances=1,
            name=SchedulerSvc.SENSOR_JOB,
            id=SchedulerSvc.SENSOR_JOB,
        )

    # override
    def __str__(self):
        out = io.StringIO()
        self._scheduler.print_jobs(out=out)

        return out.getvalue()

    def start(self):
        self._scheduler.start()

    def stop(self):
        self._scheduler.stop()

    def pause(self):
        self._scheduler.pause()

    def shutdown(self):
        self._scheduler.shutdown()
