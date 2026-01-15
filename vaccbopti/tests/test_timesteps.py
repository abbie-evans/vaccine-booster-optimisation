# FILE FOR TESTING THE PERSON CLASS

# Import useful modules
import sys
sys.path.append("C:/Users/lina4801/OneDrive - Nexus365/Team-Project-Sandpit/vaccine-booster-optimisation")
import numpy as np
import unittest
from unittest import TestCase
from vaccbopti.classes.params import Params
from vaccbopti.classes.person import Person
from vaccbopti.classes.timesteps import Timesteps
params = Params.instance()


# Define testing class
class test_timesteps(TestCase):
    """A class to test that the Timesteps class is set up and runs correctly."""

    def setUp(self):
        """Create a test Timesteps object.
        Parameters:
            sim_length (int): length of the test simulation
            num_people (int): number of people in the test simulation
            n_infec (int): number of infected people to start with
            n_indiv (list): number of people in each age group"""
        self.sim_length = 100
        self.num_people = 100
        self.n_infec = 10
        self.n_indiv = [3, 5, 5, 5,  # number in each age group N(a) - NORMALLY FROM PARAMS
                        5, 5, 8, 10,
                        7, 8, 9, 12,
                        5, 6, 5, 2]
        self.testTimesteps = Timesteps(self.num_people, self.n_indiv, self.sim_length)

    def test_defaults(self):
        """Ensure that the timesteps class is set up with correct defaults."""
        self.assertEqual(self.testTimesteps.R_e, 1.5)
        self.assertEqual(len(self.testTimesteps.indices), self.num_people)
        self.assertEqual(len(self.testTimesteps.People), self.num_people)
        self.assertIsInstance(self.testTimesteps.People[0], Person)
        self.assertEqual(len(self.testTimesteps.IDs), self.num_people)
        self.assertEqual(len(self.testTimesteps.n_age_groups), len(self.n_indiv) + 1)

    def test_initialise_people(self):
        """Ensure people are correctly given all information necessary after initialisation."""
        self.testTimesteps.initialise_people(self.n_infec)
        # Check age group loop works correctly
        self.assertEqual(self.testTimesteps.People[0].age_group, params.age_groups[0])  # row 1
        self.assertEqual(self.testTimesteps.People[3].age_group, params.age_groups[1])
        self.assertEqual(self.testTimesteps.People[8].age_group, params.age_groups[2])
        self.assertEqual(self.testTimesteps.People[13].age_group, params.age_groups[3])
        self.assertEqual(self.testTimesteps.People[18].age_group, params.age_groups[4])  # row 2
        self.assertEqual(self.testTimesteps.People[23].age_group, params.age_groups[5])
        self.assertEqual(self.testTimesteps.People[28].age_group, params.age_groups[6])
        self.assertEqual(self.testTimesteps.People[36].age_group, params.age_groups[7])
        self.assertEqual(self.testTimesteps.People[46].age_group, params.age_groups[8])  # row 3
        self.assertEqual(self.testTimesteps.People[53].age_group, params.age_groups[9])
        self.assertEqual(self.testTimesteps.People[61].age_group, params.age_groups[10])
        self.assertEqual(self.testTimesteps.People[70].age_group, params.age_groups[11])
        self.assertEqual(self.testTimesteps.People[82].age_group, params.age_groups[12])  # row 4
        self.assertEqual(self.testTimesteps.People[87].age_group, params.age_groups[13])
        self.assertEqual(self.testTimesteps.People[93].age_group, params.age_groups[14])
        self.assertEqual(self.testTimesteps.People[98].age_group, params.age_groups[15])


if __name__ == "__main__":
    unittest.main()
