import io

from apscheduler.schedulers.background import BackgroundScheduler

from conf.AppConfig import AppConfig
from conf.SchedulerConfig import SchedulerConfig
from svc.SensorSvc import SensorSvc
from util.Singleton import Singleton

__all__ = ["SchedulerSvc"]


class SchedulerSvc(Singleton):
    SENSOR_JOB = "sensor"

    """
    SchedulerSvc service
    sets up automated tasks
    https://apscheduler.readthedocs.io/en/3.x/index.html
    """

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self._schedulerConfig: SchedulerConfig = AppConfig().scheduler
        self._scheduler = BackgroundScheduler()
        self._sensorSvc = SensorSvc()

        self._scheduler.add_job(
            self._sensorSvc.process,
            "interval",
            minutes=int(self._schedulerConfig.sensorInterval),
            max_instances=1,
            coalesce=True,
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
