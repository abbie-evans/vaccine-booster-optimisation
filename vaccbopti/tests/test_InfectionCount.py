# possibility for tests:
# does it make the dataframe? can assert if len == 16?
# To be added: does it add no one on day 1?

import unittest
from unittest import TestCase
from vaccbopti.classes.infectioncount import InfectionCount
from vaccbopti.classes.params import Params

class TestInfectionCount(TestCase):
    def setUp(self):
        self.testTable = InfectionCount.instance().count_df
        self.ageNbs = Params.instance().age_groups

    def test_df_len(self):
        len_df = len(self.testTable)
        len_age_groups = len(self.ageNbs)
        self.assertEqual(len_df, len_age_groups)

if __name__ == '__main__':
    unittest.main()