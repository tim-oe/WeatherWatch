import time
import unittest

from entity.AQISensor import AQISensor
from repository.AQISensorRepository import AQISensorRepository
from svc.AQISvc import AQISvc

class AQISvcTest(unittest.TestCase):
    # def test(self):
    #     svc: AQISvc = AQISvc()
    #     repo: AQISensorRepository = AQISensorRepository()

    #     repo.exec('truncate ' + AQISensor.__tablename__)
        
    #     for x in range(5):
    #         svc.process()
    #         time.sleep(1)
            
    #     act = repo.findLatest()
    #     self.assertIsNotNone(act)        
        
    def test(self):
        svc: AQISvc = AQISvc()
        
        svc.cleanup()
