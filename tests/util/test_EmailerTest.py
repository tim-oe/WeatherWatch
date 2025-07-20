import traceback
import unittest

from util.Emailer import Emailer

class EmailerTest(unittest.TestCase):
    def test(self):        
        emailer = Emailer()
        try:
            # some code that might raise an exception
            1 / 0
        except Exception as e:        
            #emailer.send_error_notification(e, subject_prefix="unit test")
            pass
