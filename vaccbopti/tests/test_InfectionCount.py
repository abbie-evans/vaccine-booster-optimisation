# FILE FOR TESTING THE PERSON CLASS

# Import useful modules
import unittest
from unittest import TestCase
from vaccbopti.classes.infection_count import InfectionCount
from vaccbopti.classes.params import Params
ageNbs = Params.instance().age_groups


# Set up testing class
class TestInfectionCount(TestCase):
    """A class to test that the InfectionCount class is set up and runs correctly."""

    def setUp(self):
        """Set up the test table for the test class."""
        self.testTable = InfectionCount()

    def test_df_len(self):
        """Ensures the dataframe has the correct length."""
        len_df = len(self.testTable.count_df)
        len_age_groups = len(ageNbs)
        self.assertEqual(len_df, len_age_groups * 3)

    def test_amend_df(self):
        """Ensures the dataframe is ammended correctly."""
        self.testTable.count_df.loc[(ageNbs[2], 'ex_vaccine'), 'symptomatic'] = 5
        self.testTable.count_df.loc[(ageNbs[6], 'new_vaccine'), 'symptomatic'] = 13
        self.testTable.count_df.loc[(ageNbs[15], 'unvaccinated'), 'asymptomatic'] = 17
        self.assertEqual(self.testTable.count_df.loc[(ageNbs[2], 'ex_vaccine'), 'symptomatic'], 5)
        self.assertEqual(self.testTable.count_df.loc[(ageNbs[6], 'new_vaccine'), 'symptomatic'], 13)
        self.assertEqual(self.testTable.count_df.loc[(ageNbs[15], 'unvaccinated'), 'asymptomatic'], 17)


if __name__ == '__main__':
    unittest.main()
