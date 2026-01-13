# FILE FOR TESTING THE PERSON CLASS

# Import useful modules
import unittest
from unittest import TestCase
from vaccbopti.classes.infectioncount import InfectionCount
from vaccbopti.classes.params import Params
ageNbs = Params.instance().age_groups
testTable = InfectionCount.instance()


# Set up testing class
class TestInfectionCount(TestCase):
    """A class to test that the InfectionCount class is set up and runs correctly."""

    def test_error_more_than_one_instance(self):
        """Check if RuntimeError is raised when TestInfection contains an object."""
        with self.assertRaises(RuntimeError) as ve:
            InfectionCount()  # equivalent to __init__(self)
        self.assertEqual("This class is a singleton!", str(ve.exception))

    def test_error_instance_not_created(self):
        """Check to make sure that it exists when an instance is set up."""
        self.assertIsNotNone(InfectionCount.instance().df_status)
        self.assertIsNotNone(InfectionCount.instance().count_df)

    def test_df_len(self):
        """Ensures the dataframe has the correct length."""
        len_df = len(testTable.count_df)
        len_age_groups = len(ageNbs)
        self.assertEqual(len_df, len_age_groups)

    def test_amend_df(self):
        """Ensures the dataframe is ammended correctly."""
        testTable.count_df.loc[2, 'symptomatic'] = 5
        testTable.count_df.loc[15, 'asymptomatic'] = 17
        self.assertEqual(testTable.count_df.loc[2, 'symptomatic'], 5)
        self.assertEqual(testTable.count_df.loc[15, 'asymptomatic'], 17)


if __name__ == '__main__':
    unittest.main()
