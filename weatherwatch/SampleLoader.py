#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
#
#
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
from conf.DatabaseConfig import DatabaseConfig
from pyutil import filereplace
from repository.AQISensorRepository import AQISensorRepository
from repository.IndoorSensorRepository import IndoorSensorRepository
from repository.OutdoorSensorRepository import OutdoorSensorRepository


def createSql(table_name: str, d: date, repo):
    for x in range(1, 5):
        stamp = d.strftime("%Y-%m-%d")
        src = f"tests/data/db/{x}_{table_name}.sql"
        tgt = f"{stamp}_{table_name}.sql"

        print(tgt)

        outFile: Path = Path(tempfile.gettempdir() / Path(tgt))

        shutil.copy(Path(src), outFile)
        filereplace(outFile.resolve(), "__YYYY_MM_DD__", stamp)
        repo.execFile(outFile.resolve())
        outFile.unlink()

        d = d + timedelta(days=1)


# actual start point
if __name__ == "__main__":
    pass
    dbConfig: DatabaseConfig = AppConfig().database
    if dbConfig.production:
        raise Exception("DO NOT RUN ON PROD!!!!")

    indoorRepo: IndoorSensorRepository = IndoorSensorRepository()
    indoorRepo.exec(f"truncate {indoorRepo.entity.__table__}")

    outdoorRepo: OutdoorSensorRepository = OutdoorSensorRepository()
    outdoorRepo.exec(f"truncate {outdoorRepo.entity.__table__}")

    aqiRepo: AQISensorRepository = AQISensorRepository()
    aqiRepo.exec(f"truncate {aqiRepo.entity.__table__}")

    createSql("outdoor_sensor", date.today() - timedelta(days=7), outdoorRepo)
    createSql("outdoor_sensor", date.today() - timedelta(days=3), outdoorRepo)

    createSql("indoor_sensor", date.today() - timedelta(days=7), indoorRepo)
    createSql("indoor_sensor", date.today() - timedelta(days=3), indoorRepo)

    createSql("aqi_sensor", date.today() - timedelta(days=7), aqiRepo)
    createSql("aqi_sensor", date.today() - timedelta(days=3), aqiRepo)

    outdoorRepo.execFile("tests/data/db/finalize.sql")
