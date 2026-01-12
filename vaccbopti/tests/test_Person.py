# FILE FOR TESTING THE PERSON CLASS

# Import useful modules
import sys
sys.path.insert(0, "C:/Users/lina4801/OneDrive - Nexus365/Team-Project-Sandpit/vaccine-booster-optimisation")
import numpy as np
import unittest
from unittest import TestCase
from vaccbopti.classes.person import Person
from vaccbopti.classes.params import Params
from vaccbopti.classes.infectioncount import InfectionCount
params = Params.instance()
infectioncount = InfectionCount.instance()


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
        """Test that the status change with probabilities are correct."""
        self.testPerson.get_age_group(4)
        self.testPerson.determine_status_change(['symptomatic', 'asymptomatic'], 1)
        self.assertEqual(self.testPerson.status, 'symptomatic')
        probs = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        self.testPerson.determine_status_change(['symptomatic', 'asymptomatic'], probs)
        self.assertEqual(self.testPerson.status, 'asymptomatic')

    def test_pick_distr_prob(self):
        """Test that a number is correctly picked from a probability distribution."""
        self.testPerson.latent_t_i = self.testPerson.pick_distr_prob(params.latent_t)
        self.assertIsNot(self.testPerson.latent_t_i, 1)
        self.testPerson.latent_t_i = -1
    
    def test_change_status_asymptomatic(self):
        """Test that the status change decision tree works correctly on the asymptomatic branch."""
        self.testPerson.get_age_group(4)
        # Checking the switch from susceptible to exposed and ensure that latent time is added.
        self.testPerson.status = 'susceptible'
        self.testPerson.prob_exposed = 0
        self.testPerson.change_status()
        self.assertEqual(self.testPerson.status, 'susceptible')
        self.testPerson.prob_exposed = 1
        self.testPerson.change_status()
        self.assertEqual(self.testPerson.status, 'exposed')
        self.assertIsNot(self.testPerson.latent_t_i, -1)
        self.testPerson.latent_t_i = 0
        # Checking the switch from exposed to asymptomatic.
        params.p_v_symp_a = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.testPerson.change_status()
        self.assertEqual(self.testPerson.latent_t_i, -1)
        self.assertEqual(self.testPerson.status, 'asymptomatic')
        self.assertNotEqual(self.testPerson.infect_t_i, -1)
        self.assertEqual(infectioncount.count_df.loc[4, 'asymptomatic'], 1)
        self.testPerson.infect_t_i = 1
        # Checking the switch back from asymptomatic to susceptible.
        self.testPerson.change_status()
        self.assertEqual(self.testPerson.infect_t_i, 0)
        self.assertEqual(self.testPerson.status, 'asymptomatic')
        self.testPerson.change_status()
        self.assertEqual(self.testPerson.infect_t_i, -1)
        self.assertEqual(infectioncount.count_df.loc[4, 'asymptomatic'], 0)
        self.assertEqual(self.testPerson.status, 'susceptible')

    def test_change_status_symptomatic(self):
        """Test that the status change decision tree works correctly on the symptomatic branch."""
        """self.testPerson.get_age_group(4)
        # Checking the switch from exposed to symptomatic (not hospitalised or dead).
        self.testPerson.status = 'exposed'
        self.testPerson.latent_t_i = 0
        #params.p_v_symp_a = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        params.p_v_symp_a = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.testPerson.change_status()
        #print(self.testPerson.status)
        #self.assertEqual(self.testPerson.latent_t_i, -1)
        #self.assertNotEqual(self.testPerson.infect_t_i, -1)
        #self.assertEqual(self.testPerson.status, 'symptomatic')
        #self.assertEqual(infectioncount.count_df.loc[4, 'symptomatic'], 1)
        #self.testPerson.infect_t_i = 1"""


if __name__ == "__main__":
    unittest.main()