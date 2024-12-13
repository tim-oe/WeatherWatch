
import unittest

from backup.BackupRange import BackupRange


class BackupRangeTest(unittest.TestCase):

    def test(self):
        
        last_week: BackupRange = BackupRange.prev_week()
        print(f"week: [{last_week}]")
        self.assertLess(last_week.from_date, last_week.to_date)
        
        # weekday() returns 0 for Monday, 6 for Sunday
        self.assertEqual(0, last_week.from_date.weekday())
        self.assertEqual(6, last_week.to_date.weekday())
        
        last_month: BackupRange = BackupRange.prev_month()
        print(f"month: [{last_month}]")
        self.assertLess(last_month.from_date, last_month.to_date)
        self.assertEqual(1, last_month.from_date.day)
        
