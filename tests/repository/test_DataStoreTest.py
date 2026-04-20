import unittest

import pytest

from repository.DataStore import DataStore


@pytest.mark.db
class DataStoreTest(unittest.TestCase):

    def test(self):
        ds: DataStore = DataStore()
        ds.get_table_def("outdoor_sensor")