import io

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from py_singleton import singleton

from camera.Camera import Camera
from conf.AppConfig import AppConfig
from conf.SchedulerConfig import SchedulerConfig
from repository.DataStore import DataStore
from svc.PIMetricsSvc import PIMetricsSvc
from svc.SensorSvc import SensorSvc

__all__ = ["SchedulerSvc"]


def sensor():
    """
    schedule entry point for sensor task
    """
    sensorSvc = SensorSvc()
    sensorSvc.process()

def camera():
    """
    schedule entry point for camera task
    """
    camera = Camera()
    camera.snap()

def pimetrics():
    """
    schedule entry point for pimetrics task
    """
    metricsSvc = PIMetricsSvc()
    metricsSvc.process()
    
@singleton
class SchedulerSvc:
    SENSOR_JOB = "sensor"
    CAMERA_JOB = "camera"
    PI_METRICS_JOB = "pi_metrics"

    """
    SchedulerSvc service
    sets up automated tasks
    https://apscheduler.readthedocs.io/en/3.x/index.html
    """

    def __init__(self):

        self._schedulerConfig: SchedulerConfig = AppConfig().scheduler

        # in order to use this the task functions need to be static
        jobstores = {
            'default': SQLAlchemyJobStore(url=AppConfig().database.url)
        }

        self._scheduler = BackgroundScheduler(jobstores=jobstores)

        # self._scheduler = BackgroundScheduler()
        
        self._sensorSvc = SensorSvc()
        self._metricsSvc = PIMetricsSvc()
        self._camera = Camera()

        self._scheduler.add_job(
            sensor,
            "interval",
            minutes=self._schedulerConfig.sensorInterval,
            max_instances=1,
            coalesce=True,
            name=SchedulerSvc.SENSOR_JOB,
            id=SchedulerSvc.SENSOR_JOB,
        )

        self._scheduler.add_job(
            pimetrics,
            "cron",
            minute=f"2-59/{self._schedulerConfig.piMetricsInterval}",
            max_instances=1,
            coalesce=True,
            name=SchedulerSvc.PI_METRICS_JOB,
            id=SchedulerSvc.PI_METRICS_JOB,
        )

        if self._camera.enable is True:
            self._scheduler.add_job(
                camera,
                "cron",
                minute=f"3-59/{self._schedulerConfig.cameraInterval}",
                max_instances=1,
                coalesce=True,
                name=SchedulerSvc.CAMERA_JOB,
                id=SchedulerSvc.CAMERA_JOB,
            )

    # override
    def __del__(self):
        self._scheduler.shutdown()

    # override
    def __str__(self):
        out = io.StringIO()
        self._scheduler.print_jobs(out=out)

        return out.getvalue()

    def start(self):
        self._scheduler.start()

    def pause(self):
        self._scheduler.pause()
