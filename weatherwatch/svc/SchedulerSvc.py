import io

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from conf.AppConfig import AppConfig
from conf.SchedulerConfig import SchedulerConfig
from py_singleton import singleton
from svc.AQISvc import AQISvc
from svc.BackupSvc import BackupSvc
from svc.CameraSvc import CameraSvc
from svc.PIMetricsSvc import PIMetricsSvc
from svc.SensorSvc import SensorSvc
from svc.TimelapseSvc import TimelapseSvc
from svc.WUSvc import WUSvc

__all__ = ["SchedulerSvc"]


def sensor():
    """
    schedule entry point for sensor task
    """
    svc = SensorSvc()
    svc.process()


def wu():
    """
    schedule entry point for sensor task
    """
    svc = WUSvc()
    svc.process()


def aqi():
    """
    schedule entry point for aqi task
    """
    svc = AQISvc()
    svc.process()


def camera():
    """
    schedule entry point for camera task
    """
    svc = CameraSvc()
    svc.process()


def file_backup():
    """
    schedule entry point for file backup task
    """
    svc = BackupSvc()
    svc.camera()


def db_backup():
    """
    schedule entry point for file backup task
    """
    svc = BackupSvc()
    svc.db()


def timelapse():
    """
    schedule entry point for timelapse task
    """
    svc = TimelapseSvc()
    svc.process()


def pimetrics():
    """
    schedule entry point for pimetrics task
    """
    svc = PIMetricsSvc()
    svc.process()


@singleton
class SchedulerSvc:
    """
    SchedulerSvc service
    sets up automated tasks
    https://apscheduler.readthedocs.io/en/3.x/index.html
    """

    AQI_JOB = "aqi"
    CAMERA_JOB = "camera"
    DB_BACKUP_JOB = "db_backup"
    FILE_BACKUP_JOB = "file_backup"
    PI_METRICS_JOB = "pi_metrics"
    SENSOR_JOB = "sensor"
    TIMELAPSE_JOB = "timelapse"
    WU_JOB = "weather_underground"

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._app_config = AppConfig()
        self._scheduler_config: SchedulerConfig = self._app_config.scheduler

        # in order to use this the task functions need to be static
        jobstores = {"default": SQLAlchemyJobStore(url=AppConfig().database.url)}

        job_defaults = {"coalesce": True, "max_instances": 1, "replace_existing": True, "misfire_grace_time": 60}

        self._scheduler = BackgroundScheduler(jobstores=jobstores, job_defaults=job_defaults)

        self._scheduler.add_job(
            sensor,
            "interval",
            minutes=self._scheduler_config.sensor_interval,
            name=SchedulerSvc.SENSOR_JOB,
            id=SchedulerSvc.SENSOR_JOB,
            coalesce=True,
            max_instances=1,
            replace_existing=True,
            misfire_grace_time=60,
        )

        self._scheduler.add_job(
            pimetrics,
            "cron",
            minute=f"2-59/{self._scheduler_config.pi_metrics_interval}",
            name=SchedulerSvc.PI_METRICS_JOB,
            id=SchedulerSvc.PI_METRICS_JOB,
            coalesce=True,
            max_instances=1,
            replace_existing=True,
            misfire_grace_time=60,
        )

        if self._app_config.camera.enable is True:
            self._scheduler.add_job(
                camera,
                "cron",
                minute=f"3-59/{self._scheduler_config.camera_interval}",
                name=SchedulerSvc.CAMERA_JOB,
                id=SchedulerSvc.CAMERA_JOB,
                coalesce=True,
                max_instances=1,
                replace_existing=True,
                misfire_grace_time=60,
            )

        if self._app_config.timelapse.enable is True:
            self._scheduler.add_job(
                timelapse,
                "cron",
                hour=self._scheduler_config.timelapse_hour,
                minute="6",
                name=SchedulerSvc.TIMELAPSE_JOB,
                id=SchedulerSvc.TIMELAPSE_JOB,
                coalesce=True,
                max_instances=1,
                replace_existing=True,
                misfire_grace_time=60,
            )

        if self._app_config.backup.file_enable is True:
            self._scheduler.add_job(
                file_backup,
                "cron",
                hour=self._scheduler_config.file_back_hour,
                minute="7",
                name=SchedulerSvc.FILE_BACKUP_JOB,
                id=SchedulerSvc.FILE_BACKUP_JOB,
                coalesce=True,
                max_instances=1,
                replace_existing=True,
                misfire_grace_time=60,
            )

        if self._app_config.backup.db_enable is True:
            self._scheduler.add_job(
                db_backup,
                "cron",
                hour=self._scheduler_config.db_back_hour,
                minute="7",
                name=SchedulerSvc.DB_BACKUP_JOB,
                id=SchedulerSvc.DB_BACKUP_JOB,
                coalesce=True,
                max_instances=1,
                replace_existing=True,
                misfire_grace_time=60,
            )

        if self._app_config.aqi.enable is True:
            self._scheduler.add_job(
                aqi,
                "cron",
                minute=f"4-59/{self._scheduler_config.camera_interval}",
                name=SchedulerSvc.AQI_JOB,
                id=SchedulerSvc.AQI_JOB,
                coalesce=True,
                max_instances=1,
                replace_existing=True,
                misfire_grace_time=60,
            )

        if self._app_config.wu.enable is True:
            self._scheduler.add_job(
                wu,
                "interval",
                minutes=self._scheduler_config.wu_interval,
                name=SchedulerSvc.WU_JOB,
                id=SchedulerSvc.WU_JOB,
                coalesce=True,
                max_instances=1,
                replace_existing=True,
                misfire_grace_time=60,
            )

    def __str__(self):
        """
        override
        :param self: this
        """
        out = io.StringIO()
        self._scheduler.print_jobs(out=out)

        return out.getvalue()

    def __del__(self):
        """
        override
        :param self: this
        """
        self._scheduler.shutdown()

    def start(self):
        """
        start application scheduler
        :param self: this
        """
        self._scheduler.start()

    def pause(self):
        """
        pause application scheduler
        :param self: this
        """
        self._scheduler.pause()
