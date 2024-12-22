#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
used to load sample data for testing and development
DO NOT RUN ON PRODUCTION
DESTRUCTIVE OPERATIONS!!!!
"""
import shutil
import tempfile
from datetime import date, timedelta
from pathlib import Path

from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from conf.DatabaseConfig import DatabaseConfig
from conf.TimelapseConfig import TimelapseConfig
from pyutil import filereplace
from repository.AQISensorRepository import AQISensorRepository
from repository.IndoorSensorRepository import IndoorSensorRepository
from repository.OutdoorSensorRepository import OutdoorSensorRepository


def create_sql(table_name: str, d: date, repo):
    """
    create the sql file
    :param table_name: the table name
    :param date: the sample data date
    :param repo: the db repo
    """

    for x in range(1, 5):
        stamp = d.strftime("%Y-%m-%d")
        src = f"tests/data/db/{x}_{table_name}.sql"
        tgt = f"{stamp}_{table_name}.sql"

        print(tgt)

        out_file: Path = Path(tempfile.gettempdir() / Path(tgt))

        shutil.copy(Path(src), out_file)
        filereplace(out_file.resolve(), "__YYYY_MM_DD__", stamp)
        repo.exec_file(out_file.resolve())
        out_file.unlink()

        d = d + timedelta(days=1)


def init_files():
    """
    init image ahd timelape files
    """
    camera_config: CameraConfig = AppConfig().camera
    pic_dir: Path = camera_config.folder
    pic_dir.mkdir(parents=True, exist_ok=True)

    img_file: Path = Path("tests/data/img/current.jpg")
    shutil.copy(img_file, pic_dir)

    timelapse_config: TimelapseConfig = AppConfig().timelapse
    vid_dir: Path = timelapse_config.folder
    vid_dir.mkdir(parents=True, exist_ok=True)
    vid_file: Path = Path("tests/data/vids/2024-11-12.mp4")

    d = date.today() - timedelta(days=1)
    stamp = d.strftime("%Y-%m-%d")

    tgt_file = vid_dir / f"{stamp}{timelapse_config.extension}"
    shutil.copy(vid_file, tgt_file)


# actual start point
if __name__ == "__main__":
    db_config: DatabaseConfig = AppConfig().database
    if db_config.production:
        raise Exception("DO NOT RUN ON PROD!!!!")

    indoor_repo: IndoorSensorRepository = IndoorSensorRepository()
    indoor_repo.exec(f"truncate {indoor_repo.entity.__table__}")

    outdoor_repo: OutdoorSensorRepository = OutdoorSensorRepository()
    outdoor_repo.exec(f"truncate {outdoor_repo.entity.__table__}")

    aqi_repo: AQISensorRepository = AQISensorRepository()
    aqi_repo.exec(f"truncate {aqi_repo.entity.__table__}")

    create_sql("outdoor_sensor", date.today() - timedelta(days=7), outdoor_repo)
    create_sql("outdoor_sensor", date.today() - timedelta(days=3), outdoor_repo)

    create_sql("indoor_sensor", date.today() - timedelta(days=7), indoor_repo)
    create_sql("indoor_sensor", date.today() - timedelta(days=3), indoor_repo)

    create_sql("aqi_sensor", date.today() - timedelta(days=7), aqi_repo)
    create_sql("aqi_sensor", date.today() - timedelta(days=3), aqi_repo)

    outdoor_repo.exec_file("tests/data/db/finalize.sql")

    init_files()
