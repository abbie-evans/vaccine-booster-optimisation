# FILE FOR TESTING THE PERSON CLASS

# Import useful modules
import numpy as np
import unittest
from unittest import TestCase
from unittest.mock import patch
import vaccbopti.classes.person as person
from vaccbopti.classes.person import Person
from vaccbopti.classes.params import Params
from vaccbopti.classes.infectioncount import InfectionCount
params = Params.instance()


# Define testing class
class test_person(TestCase):
    """A class to test that the Person class is set up and runs correctly."""

    def setUp(self):
        """Create a test Person object."""
        self.testPerson = Person()

    def test_defaults(self):
        """Ensure that a person is set up with correct defaults."""
        self.assertEqual(self.testPerson.age_group, None)
        self.assertEqual(self.testPerson.status, 'susceptible')
        self.assertEqual(self.testPerson.latent_t_i, -1)

    def test_IDs(self):
        """Ensures that when people are initiated, each ID is unique."""
        People = [Person() for p in range(20)]
        ids = [P.id for P in People]
        unique = np.unique(ids)
        self.assertTrue(set(ids) == set(unique))
        anotherPerson = Person()
        self.assertNotIn(anotherPerson.id, ids)

    def test_get_age_group(self):
        """Test that the ages are called correctly and can be reindexed correctly."""
        self.testPerson.get_age_group(4)
        self.assertEqual(self.testPerson.age_group, "20-24")
        index = np.where(np.array(params.age_groups) == self.testPerson.age_group)[0][0]
        self.assertEqual(index, 4)

    def test_calc_susceptibility(self):
        """Test that susceptibility calculations are correct."""
        self.testPerson.calc_susceptibility()
        self.assertEqual(self.testPerson.susceptibility, 1)
        self.testPerson.immunity_time_exvacc = 5
        self.testPerson.calc_susceptibility()
        self.assertAlmostEqual(self.testPerson.susceptibility, 1 - 0.22898922)
        self.testPerson.immunity_time_newvacc = 3
        self.testPerson.calc_susceptibility()
        self.assertAlmostEqual(self.testPerson.susceptibility, 1 - 0.24318079419781505)

    def test_calc_prob_exposed(self):
        """Ensure that the calculation occurs correctly."""
        self.testPerson.immunity_time_exvacc = 5
        self.testPerson.calc_susceptibility()
        self.testPerson.calc_prob_exposed(1)
        self.assertAlmostEqual(self.testPerson.prob_exposed, 0.5374546996)

    def test_pick_distr_prob(self):
        """Test that a number is correctly picked from a probability distribution."""
        self.testPerson.latent_t_i = self.testPerson.pick_distr_prob(params.latent_t)
        self.assertIsNot(self.testPerson.latent_t_i, 1)
        self.testPerson.latent_t_i = -1

    def test_determine_status_change(self):
        """Test that the status change with probabilities are correct."""
        self.testPerson.get_age_group(4)
        self.testPerson.determine_status_change(['symptomatic', 'asymptomatic'], 1)
        self.assertEqual(self.testPerson.status, 'symptomatic')
        probs = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        self.testPerson.determine_status_change(['symptomatic', 'asymptomatic'], probs)
        self.assertEqual(self.testPerson.status, 'asymptomatic')

    def test_initialise_infec(self):
        """Ensure that initialising random people as infected works correctly."""
        self.testPerson.immunity_time_infec = 5
        self.testPerson.initialise_infection()
        self.assertEqual(self.testPerson.status, 'exposed')
        self.assertNotEqual(self.testPerson.latent_t_i, -1)
        self.assertEqual(self.testPerson.immunity_time_infec, 0)

    def test_increment_immunity_time(self):
        """Ensures that immunity is incremented correctly."""
        self.testPerson.increment_immunity_time()
        self.assertEqual(self.testPerson.immunity_time_exvacc, -1)
        self.assertEqual(self.testPerson.immunity_time_newvacc, -1)
        self.assertEqual(self.testPerson.immunity_time_infec, -1)
        self.testPerson.immunity_time_exvacc = 0
        self.testPerson.immunity_time_newvacc = 5
        self.testPerson.immunity_time_infec = 10
        self.testPerson.increment_immunity_time()
        self.assertEqual(self.testPerson.immunity_time_exvacc, 1)
        self.assertEqual(self.testPerson.immunity_time_newvacc, 6)
        self.assertEqual(self.testPerson.immunity_time_infec, 11)

    @patch.object(person.params, 'p_v_symp_a', new=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    def test_change_status_asymptomatic(self):
        """Test that the status change decision tree works correctly on the asymptomatic branch."""
        infectioncount = InfectionCount().count_df
        self.testPerson.get_age_group(4)
        # Checking the switch from susceptible to exposed and ensure that latent time is added.
        self.testPerson.status = 'susceptible'
        self.testPerson.vacc_status = 'new_vacc'
        self.testPerson.prob_exposed = 0
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.status, 'susceptible')
        self.testPerson.prob_exposed = 1
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.status, 'exposed')
        self.assertIsNot(self.testPerson.latent_t_i, -1)
        self.testPerson.latent_t_i = 0
        # Checking the switch from exposed to asymptomatic.
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.latent_t_i, -1)
        self.assertEqual(self.testPerson.status, 'asymptomatic')
        self.assertNotEqual(self.testPerson.infect_t_i, -1)
        self.assertEqual(infectioncount.loc[(self.testPerson.age_group,
                                             'new_vaccine'), 'asymptomatic'], 1)
        self.testPerson.infect_t_i = 1
        # Checking the switch back from asymptomatic to susceptible.
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.infect_t_i, 0)
        self.assertEqual(self.testPerson.status, 'asymptomatic')
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.infect_t_i, -1)
        self.assertEqual(infectioncount.loc[(self.testPerson.age_group,
                                             'new_vaccine'), 'asymptomatic'], 0)
        self.assertEqual(self.testPerson.status, 'susceptible')

    @patch.object(person.params, 'p_v_symp_a', new=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    @patch.object(person.params, 'p_nv_HD', new=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    def test_change_status_symptomatic_fine(self):
        """Test that the status change decision tree works correctly on the symptomatic/unhospitalised branch."""
        self.testPerson.get_age_group(4)
        infectioncount = InfectionCount().count_df
        # Checking the switch from exposed to symptomatic (not hospitalised or dead).
        self.testPerson.vacc_status = 'old_vacc'
        self.testPerson.vacc_status_t_i = 'old_vacc'
        self.testPerson.status = 'exposed'
        self.testPerson.latent_t_i = 0
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.latent_t_i, -1)
        self.assertEqual(self.testPerson.status, 'symptomatic')
        self.assertNotEqual(self.testPerson.infect_t_i, -1)
        self.assertEqual(infectioncount.loc[(self.testPerson.age_group,
                                             'old_vaccine'), 'symptomatic'], 1)
        self.testPerson.infect_t_i = 1
        # Checking the switch back from symptomatic to susceptible.
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.infect_t_i, 0)
        self.assertEqual(self.testPerson.status, 'symptomatic')
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.infect_t_i, -1)
        self.assertEqual(infectioncount.loc[(self.testPerson.age_group,
                                             'old_vaccine'), 'symptomatic'], 0)
        self.assertEqual(self.testPerson.status, 'susceptible')

    @patch.object(person.params, 'p_v_symp_a', new=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    @patch.object(person.params, 'p_nv_IH', new=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    @patch.object(person.params, 'p_nv_HD', new=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    def test_change_status_symptomatic_hospitalised(self):
        """Test that the status change decision tree works correctly on the symptomatic/hospitalised branch."""
        self.testPerson.get_age_group(4)
        infectioncount = InfectionCount().count_df
        # Checking the switch from exposed to symptomatic/hospitalised (not dead).
        self.testPerson.status = 'exposed'
        self.testPerson.latent_t_i = 0
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.latent_t_i, -1)
        self.assertEqual(self.testPerson.status, 'hospitalised')
        self.assertNotEqual(self.testPerson.infect_t_i, -1)
        self.assertNotEqual(self.testPerson.hosp_t_i, -1)
        self.assertEqual(infectioncount.loc[(self.testPerson.age_group,
                                             'unvaccinated'), 'hospitalised'], 1)
        self.testPerson.infect_t_i = 1
        # Checking the switch back from hospitalised to susceptible.
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.infect_t_i, 0)
        self.assertEqual(self.testPerson.status, 'hospitalised')
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.infect_t_i, -1)
        self.assertEqual(infectioncount.loc[(self.testPerson.age_group,
                                             'unvaccinated'), 'hospitalised'], 0)
        self.assertEqual(self.testPerson.status, 'susceptible')

    @patch.object(person.params, 'p_v_symp_a', new=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    @patch.object(person.params, 'p_nv_IH', new=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    @patch.object(person.params, 'p_nv_HD', new=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    def test_change_status_symptomatic_dead(self):
        """Test that the status change decision tree works correctly on the symptomatic/dead branch."""
        self.testPerson.get_age_group(4)
        infectioncount = InfectionCount().count_df
        # Checking the switch from exposed to symptomatic/dead.
        self.testPerson.status = 'exposed'
        self.testPerson.latent_t_i = 0
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.latent_t_i, -1)
        self.assertEqual(self.testPerson.status, 'dead')
        self.assertNotEqual(self.testPerson.infect_t_i, -1)
        self.assertNotEqual(self.testPerson.hosp_t_i, -1)
        self.assertNotEqual(self.testPerson.death_t_i, -1)
        self.assertEqual(infectioncount.loc[(self.testPerson.age_group,
                                             'unvaccinated'), 'hospitalised'], 1)
        self.testPerson.death_t_i = 1
        # Checking the person stays dead after the dead period is over.
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.death_t_i, 0)
        self.assertEqual(self.testPerson.status, 'dead')
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.death_t_i, -1)
        self.assertEqual(infectioncount.loc[(self.testPerson.age_group,
                                             'unvaccinated'), 'hospitalised'], 0)
        self.assertEqual(infectioncount.loc[(self.testPerson.age_group,
                                             'unvaccinated'), 'dead'], 1)
        self.assertEqual(self.testPerson.status, 'dead')
        self.testPerson.change_status(infectioncount)
        self.assertEqual(self.testPerson.status, 'dead')


if __name__ == "__main__":
    unittest.main()
