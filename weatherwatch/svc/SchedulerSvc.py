import io

from apscheduler.schedulers.background import BackgroundScheduler
from conf.AppConfig import AppConfig
from conf.SchedulerConfig import SchedulerConfig
from py_singleton import singleton
from svc.PIMetricsSvc import PIMetricsSvc
from svc.SensorSvc import SensorSvc

__all__ = ["SchedulerSvc"]


@singleton
class SchedulerSvc:
    SENSOR_JOB = "sensor"
    PI_METRICS_JOB = "pi_metrics"

    """
    SchedulerSvc service
    sets up automated tasks
    https://apscheduler.readthedocs.io/en/3.x/index.html
    """

    def __init__(self):

        self._schedulerConfig: SchedulerConfig = AppConfig().scheduler
        self._scheduler = BackgroundScheduler()
        self._sensorSvc = SensorSvc()
        self._metricsSvc = PIMetricsSvc()

        self._scheduler.add_job(
            self._sensorSvc.process,
            "interval",
            minutes=self._schedulerConfig.sensorInterval,
            max_instances=1,
            coalesce=True,
            name=SchedulerSvc.SENSOR_JOB,
            id=SchedulerSvc.SENSOR_JOB,
        )

        self._scheduler.add_job(
            self._metricsSvc.process,
            "interval",
            minutes=10,
            max_instances=1,
            coalesce=True,
            name=SchedulerSvc.PI_METRICS_JOB,
            id=SchedulerSvc.PI_METRICS_JOB,
        )

    # override
    def __str__(self):
        out = io.StringIO()
        self._scheduler.print_jobs(out=out)

        return out.getvalue()

    def start(self):
        self._scheduler.start()

    def pause(self):
        self._scheduler.pause()

    def shutdown(self):
        self._scheduler.shutdown()
