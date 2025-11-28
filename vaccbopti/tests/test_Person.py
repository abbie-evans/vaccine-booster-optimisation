# FILE FOR TESTING THE PERSON CLASS

# Import useful modules
import sys
sys.path.insert(0, "C:/Users/lina4801/OneDrive - Nexus365/Team-Project-Sandpit/vaccine-booster-optimisation")
import numpy as np
import unittest
from unittest import TestCase
from vaccbopti.classes.person import Person
from vaccbopti.classes.params import Params
params = Params.instance()


# Define testing class
class test_person(TestCase):
    """A class to test that the Person class is set up and runs correctly."""

    def setUp(self):
        """Create a test Person object."""
        self.testPerson = Person()

    def test_get_age_group(self):
        """Test that the ages are called correctly and can be reindexed correctly."""
        self.assertEqual(self.testPerson.age_group, None)
        self.testPerson.get_age_group(4)
        self.assertEqual(self.testPerson.age_group, "20-24")
        index = np.where(params.age_groups == self.testPerson.age_group)[0][0]
        self.assertEqual(index, 4)
    
    def test_calc_susceptibility(self):
        """Test that susceptibility calculations are correct."""
        self.assertEqual(self.testPerson.calc_susceptibility(), 1)
        self.testPerson.immunity_time_exvacc = 5
        self.assertAlmostEqual(self.testPerson.calc_susceptibility(), 1 - 0.22898922)
    
    def test_determine_status_change(self):
        self.testPerson.get_age_group(4)
        self.testPerson.determine_status_change(['symptomatic', 'asymptomatic'], 1)
        probs = [0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]
        self.testPerson.determine_status_change(["symptomatic", "asymptomatic"], probs)
        self.assertEqual(self.testPerson.status, 'asymptomatic')


if __name__ == "__main__":
    unittest.main()
