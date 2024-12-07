import unittest

from repository.DataStore import DataStore

class DataStoreTest(unittest.TestCase):

    def test(self):
        ds: DataStore = DataStore()
        ds.get_schema_def()