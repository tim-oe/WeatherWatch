import json
from pathlib import Path
import unittest
import piexif
import pprint

from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from gps.DMSCoordinate import Ordinal
from svc.CameraSvc import CameraSvc
from tests.repository.test_OutdoorSensorRepositoryTest import OutdoorSensorRepositoryTest
from entity.OutdoorSensor import OutdoorSensor
from repository.OutdoorSensorRepository import OutdoorSensorRepository

class SensorSvcTest(unittest.TestCase):

    def setup_method(self, test_method):
        self.svc: CameraSvc = CameraSvc()
        self.cc: CameraConfig = AppConfig().camera
        self.outdoorRepo: OutdoorSensorRepository = OutdoorSensorRepository()

        self.outdoorRepo.exec('truncate ' + OutdoorSensor.__tablename__)

    def teardown_class(self):
        OutdoorSensorRepository().exec('truncate ' + OutdoorSensor.__tablename__)
        
    def test(self):
        self.outdoorRepo.exec('truncate ' + OutdoorSensor.__tablename__)
        
        ent: OutdoorSensor = OutdoorSensorRepositoryTest.getSample()
        
        ent.light_lux = 100.00
        
        self.outdoorRepo.insert(ent)
        
        for f in self.cc.folder.iterdir():
            f.unlink()

        self.svc.process()
        
        found: bool = False
        image_path: str
                
        for file in self.cc.folder.glob(f"*{self.cc.extension}"):       
            found = True
            image_path = str(Path(file.absolute()).resolve())
    
        self.assertTrue(found)        
    
        exif_dict = piexif.load(image_path)

        pprint.pprint(exif_dict)
        
        # lux
        self.assertTrue(piexif.ExifIFD.UserComment in exif_dict["Exif"])
        user_data = json.loads(exif_dict["Exif"][piexif.ExifIFD.UserComment].decode())
        pprint.pprint(user_data)
        self.assertIn("lux", user_data)
        self.assertTrue(piexif.ImageIFD.ImageDescription in exif_dict["0th"])
        image_description = exif_dict["0th"][piexif.ImageIFD.ImageDescription].decode("utf-8")
        self.assertTrue(image_description.startswith("WeatherWatch lux="))
        self.assertTrue(piexif.ImageIFD.XPComment in exif_dict["0th"])
        xp_comment_raw = exif_dict["0th"][piexif.ImageIFD.XPComment]
        if isinstance(xp_comment_raw, tuple):
            xp_comment_raw = bytes(xp_comment_raw)
        xp_comment = xp_comment_raw.decode("utf-16le").rstrip("\x00")
        self.assertEqual(image_description, xp_comment)

        # camera
        self.assertTrue(piexif.ExifIFD.LightSource in exif_dict["Exif"])
        self.assertTrue(piexif.ExifIFD.LensMake in exif_dict["Exif"])
        self.assertTrue(piexif.ExifIFD.LensModel in exif_dict["Exif"])
        # weather
        self.assertTrue(piexif.ExifIFD.Temperature in exif_dict["Exif"])
        self.assertTrue(piexif.ExifIFD.Humidity in exif_dict["Exif"])
        self.assertTrue(piexif.ExifIFD.Pressure in exif_dict["Exif"])

        # GPS
        num, den = exif_dict['GPS'][piexif.GPSIFD.GPSAltitude]
        self.assertGreater(num, den)

        self.assertTrue(piexif.GPSIFD.GPSLatitude in exif_dict["GPS"])
        self.assertTrue(piexif.GPSIFD.GPSLongitude in exif_dict["GPS"])

        self.assertEqual(Ordinal.NORTH.value, exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef].decode())
        self.assertEqual(Ordinal.WEST.value, exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef].decode())

        my_file = Path(self.cc.current_file)
        self.assertTrue(my_file.is_file())
        