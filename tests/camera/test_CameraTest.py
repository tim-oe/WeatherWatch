from pathlib import Path
import unittest

import piexif
import pprint

from camera.Camera import Camera
from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig

class CameraTest(unittest.TestCase):

    def test(self):
        ac: AppConfig = AppConfig()
        cc: CameraConfig = ac.camera
        
        c: Camera = Camera()
        
        for f in cc.folder.iterdir():
            f.unlink()

        c.process(cc.luxLimit - 1) 
        
        found: bool = False
        image_path: str
                
        for file in cc.folder.glob(f"*{cc.extension}"):       
            found = True
            image_path = str(Path(file.absolute()).resolve())
    
        self.assertTrue(found)        

        print(f"img {image_path}")
    
        exif_dict = piexif.load(image_path)

        pprint.pprint(exif_dict)

        num, den = exif_dict["Exif"][piexif.ExifIFD.ExposureTime]
        print(f"ExposureTime {num}/{den} {num/den} sec")

        iso = exif_dict["Exif"][piexif.ExifIFD.ISOSpeedRatings]
        print(f"ISOSpeedRatings {iso}")

        self.assertGreater(num, den)
        self.assertGreater(iso, 400)
    
        for f in cc.folder.iterdir():
            f.unlink()

        c.process(cc.luxLimit + 1) 
        
        found: bool = False
        image_path: str
                
        for file in cc.folder.glob(f"*{cc.extension}"):       
            found = True
            image_path = str(Path(file.absolute()).resolve())
    
        self.assertTrue(found)        

        print(f"img {image_path}")
    
        exif_dict = piexif.load(image_path)

        pprint.pprint(exif_dict)

        num, den = exif_dict["Exif"][piexif.ExifIFD.ExposureTime]
        print(f"ExposureTime {num}/{den} {num/den} sec")
    
        iso = exif_dict["Exif"][piexif.ExifIFD.ISOSpeedRatings]
        print(f"ISOSpeedRatings {iso}")
    
        self.assertLess(num, den)
        self.assertLess(iso, 600)

    # def test(self):
    #     ac: AppConfig = AppConfig()
    #     cc: CameraConfig = ac.camera
        
    #     c: Camera = Camera()
        
    #     for f in cc.folder.iterdir():
    #         f.unlink()

    #     c.process(cc.luxLimit + 1) 
        
    #     found: bool = False
    #     image_path: str
                
    #     for file in cc.folder.glob(f"*{cc.extension}"):       
    #         found = True
    #         image_path = str(Path(file.absolute()).resolve())
    
    #     self.assertTrue(found)        

    #     print(f"img {image_path}")
    
    #     exif_dict = piexif.load(image_path)

    #     pprint.pprint(exif_dict)

    #     num, den = exif_dict["Exif"][piexif.ExifIFD.ExposureTime]
    #     print(f"ExposureTime {num}/{den} {num/den} sec")

    #     iso = exif_dict["Exif"][piexif.ExifIFD.ISOSpeedRatings]
    #     print(f"ISOSpeedRatings {iso}")

    #     for f in cc.folder.iterdir():
    #         f.unlink()
