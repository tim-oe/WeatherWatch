import time
import unittest

from entity.AQISensor import AQISensor
from repository.AQISensorRepository import AQISensorRepository
from svc.AQISvc import AQISvc

class AQISvcTest(unittest.TestCase):
    def setup_method(self, test_method):
        self.svc: AQISvc = AQISvc()
        self.repo: AQISensorRepository = AQISensorRepository()

        self.repo.exec('truncate ' + AQISensor.__tablename__)

    def teardown_classsvc(self):
        AQISensorRepository().exec('truncate ' + AQISensor.__tablename__)
    
    def test(self):
        
        for x in range(5):
            self.svc.process()
            time.sleep(.5)
            
        act = self.repo.findLatest()
        self.assertIsNotNone(act)        
        
    # def test(self):
    #     svc: AQISvc = AQISvc()
        
    #     svc.cleanup()
