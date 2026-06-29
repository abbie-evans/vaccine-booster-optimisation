# FILE FOR TESTING THE PERSON CLASS

# Import useful modules
import unittest
from unittest import TestCase
from vaccbopti.classes.params import Params
from vaccbopti.classes.person import Person
from vaccbopti.classes.infectionforce import InfectionForce
from vaccbopti.classes.infectioncount import InfectionCount
from vaccbopti.classes.timesteps import Timesteps
params = Params.instance()
infection_force = InfectionForce()
infectioncount = InfectionCount().count_df
infection_force.all_lambda(infectioncount)


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
        self.sim_length = 5
        self.num_people = 100
        self.n_infec = 10
        self.testTimesteps = Timesteps(self.num_people, self.sim_length)

    def test_defaults(self):
        """Ensure that the timesteps class is set up with correct defaults."""
        self.assertEqual(self.testTimesteps.R_e, 1.5)
        self.assertEqual(len(self.testTimesteps.indices), self.num_people)
        self.assertEqual(len(self.testTimesteps.People), self.num_people)
        self.assertIsInstance(self.testTimesteps.People[0], Person)
        self.assertEqual(len(self.testTimesteps.IDs), self.num_people)
        self.assertEqual(len(self.testTimesteps.rho_age_groups), len(params.prop_indivs_a) + 1)

    def test_initialise_people(self):
        """Ensure people are correctly given all information necessary after initialisation."""
        self.testTimesteps.initialise_people(self.n_infec)
        # Check age group loop works correctly
        self.assertEqual(self.testTimesteps.People[0].age_group, params.age_groups[0])  # row 1
        self.assertEqual(self.testTimesteps.People[6].age_group, params.age_groups[1])
        self.assertEqual(self.testTimesteps.People[12].age_group, params.age_groups[2])
        self.assertEqual(self.testTimesteps.People[18].age_group, params.age_groups[3])
        self.assertEqual(self.testTimesteps.People[23].age_group, params.age_groups[4])  # row 2
        self.assertEqual(self.testTimesteps.People[29].age_group, params.age_groups[5])
        self.assertEqual(self.testTimesteps.People[36].age_group, params.age_groups[6])
        self.assertEqual(self.testTimesteps.People[43].age_group, params.age_groups[7])
        self.assertEqual(self.testTimesteps.People[50].age_group, params.age_groups[8])  # row 3
        self.assertEqual(self.testTimesteps.People[56].age_group, params.age_groups[9])
        self.assertEqual(self.testTimesteps.People[62].age_group, params.age_groups[10])
        self.assertEqual(self.testTimesteps.People[69].age_group, params.age_groups[11])
        self.assertEqual(self.testTimesteps.People[76].age_group, params.age_groups[12])  # row 4
        self.assertEqual(self.testTimesteps.People[82].age_group, params.age_groups[13])
        self.assertEqual(self.testTimesteps.People[87].age_group, params.age_groups[14])
        self.assertEqual(self.testTimesteps.People[92].age_group, params.age_groups[15])
        # Ensures 20% of people are ineligble for the booster vaccine
        vacc_status = [p.vacc_status for p in self.testTimesteps.People if p.vacc_status == 'ineligible']
        self.assertEqual(len(vacc_status), int(round(self.num_people * 0.2)))
        # Ensures everyone has been given a random previous infection/vaccine time
        for p in self.testTimesteps.People:
            self.assertIsNot(p.immunity_time_exvacc, -1)
        # Ensures the correct number of people have been randomly infected
        exposed = [p.status for p in self.testTimesteps.People if p.status == 'exposed']
        self.assertEqual(len(exposed), self.n_infec)

    def test_get_p_exposed(self):
        """Tests that people are accurately given susceptibilities and p(exposure) once initialised."""
        self.testTimesteps.initialise_people(self.n_infec)
        self.testTimesteps.get_p_exposed(infection_force.lambda_list)
        # Ensures every person now has an updated susceptibility and probability of exposure
        for p in self.testTimesteps.People:
            self.assertIsNot(p.susceptibility, 0)
            self.assertIsNot(p.prob_exposed, 0)

    def test_calculate_average_susceptibility(self):
        """Tests average susceptibility calculation occurs and gives a value."""
        self.testTimesteps.initialise_people(self.n_infec)
        self.testTimesteps.get_p_exposed(infection_force.lambda_list)
        self.assertIsNotNone(self.testTimesteps.calculate_average_susceptibility())
        self.assertIsNot(self.testTimesteps.calculate_average_susceptibility(), 0)

    def test_calculate_new_beta(self):
        """Tests that a new beta is outputted once people have updated susceptibility."""
        self.testTimesteps.initialise_people(self.n_infec)
        self.testTimesteps.get_p_exposed(infection_force.lambda_list)
        beta = self.testTimesteps.calculate_new_beta()
        self.assertIs(len(beta), len(params.infec_rate_param))
        for b in beta:
            self.assertIsNotNone(b)

    def test_administer_booster_s0(self):
        """Tests the booster administration with strategy 0 occurs correctly."""
        old_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        old_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        self.testTimesteps.administer_booster(0, 1, 1, 10)
        new_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        new_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        self.assertListEqual(old_it_exvacc, new_it_exvacc)
        self.assertListEqual(old_it_newvacc, new_it_newvacc)

    def test_administer_booster_s1(self):
        """Tests the booster administration with strategy 1 occurs correctly."""
        self.testTimesteps.initialise_people(self.n_infec)
        old_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        old_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        self.testTimesteps.administer_booster(1, 1, 1, 10)
        new_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        new_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        self.assertNotEqual(old_it_exvacc, new_it_exvacc)
        self.assertListEqual(old_it_newvacc, new_it_newvacc)

    def test_administer_booster_2(self):
        """Tests the booster administration with strategy 2 occurs correctly."""
        self.testTimesteps.initialise_people(self.n_infec)
        old_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        old_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        # Check before the new booster comes out that nothing is happening in the loop
        self.testTimesteps.administer_booster(2, 2, 1, 10)
        new_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        self.assertListEqual(old_it_newvacc, new_it_newvacc)
        # Check after the new bosoter coems out that boosters occur
        self.testTimesteps.administer_booster(2, 2, 5, 10)
        new_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        new_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        self.assertListEqual(old_it_exvacc, new_it_exvacc)
        self.assertNotEqual(old_it_newvacc, new_it_newvacc)

    def test_administer_booster_3(self):
        """Tests the booster administration with strategy 3 occurs correctly."""
        self.testTimesteps.initialise_people(self.n_infec)
        old_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        old_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        # Check before the new booster comes out that old booster is added
        self.testTimesteps.administer_booster(3, 2, 1, 10)
        new_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        new_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        self.assertNotEqual(old_it_exvacc, new_it_exvacc)
        self.assertListEqual(old_it_newvacc, new_it_newvacc)
        # Check after booster available that it is changing
        self.testTimesteps.administer_booster(3, 2, 5, 10)
        new_new_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        new_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        self.assertListEqual(new_it_exvacc, new_new_it_exvacc)
        self.assertNotEqual(old_it_newvacc, new_it_newvacc)

    def test_administer_booster_4(self):
        """Tests the booster administration with strategy 4 occurs correctly."""
        self.testTimesteps.initialise_people(self.n_infec)
        old_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        old_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        # Check before the new booster comes out that old booster is added
        self.testTimesteps.administer_booster(4, 2, 1, 10)
        new_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        new_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        self.assertNotEqual(old_it_exvacc, new_it_exvacc)
        self.assertListEqual(old_it_newvacc, new_it_newvacc)
        # Check after booster available that it is changing
        self.testTimesteps.administer_booster(4, 2, 5, 10)
        new_new_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        new_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        self.assertListEqual(new_it_exvacc, new_new_it_exvacc)
        self.assertNotEqual(old_it_newvacc, new_it_newvacc)

    def test_administer_booster_5(self):
        """Tests the booster administration with strategy 5 occurs correctly."""
        old_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        old_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        self.testTimesteps.administer_booster(5, 2, 1, 10)
        new_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        new_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        self.assertNotEqual(old_it_exvacc, new_it_exvacc)
        self.assertListEqual(old_it_newvacc, new_it_newvacc)

    def test_administer_booster_6(self):
        """Tests the booster administration with strategy 6 occurs correctly."""
        old_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        old_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        # Check before the new booster comes out that old booster is added
        self.testTimesteps.administer_booster(6, 2, 1, 10)
        new_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        new_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        self.assertListEqual(old_it_exvacc, new_it_exvacc)
        self.assertListEqual(old_it_newvacc, new_it_newvacc)
        # Check after booster available that it is changing
        self.testTimesteps.administer_booster(6, 2, 5, 10)
        new_new_it_exvacc = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        new_it_newvacc = [p.immunity_time_newvacc for p in self.testTimesteps.People]
        self.assertListEqual(new_it_exvacc, new_new_it_exvacc)
        self.assertNotEqual(old_it_newvacc, new_it_newvacc)

    def test_increment_people(self):
        """Tests that the increments occur correctly."""
        self.testTimesteps.initialise_people(self.n_infec)
        exvacc_times_old = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        self.testTimesteps.increment_people(infectioncount)
        exvacc_times_new = [p.immunity_time_exvacc for p in self.testTimesteps.People]
        for i in range(len(exvacc_times_new)):
            self.assertEqual(exvacc_times_old[i] + 1, exvacc_times_new[i])

    def test_append_daily_nbs_outputdf(self):
        """Test that append_daily_nbs_outputdf correctly adds rows for each timestep."""
        # Initialize people and set up the output dataframe
        self.testTimesteps.initialise_people(self.n_infec)
        for t in range(self.sim_length):
            self.testTimesteps.append_daily_nbs_outputdf(t, infectioncount)
        # Check that the dataframe has the correct number of rows (one per timestep)
        num_rows = self.testTimesteps.statusDF.shape[0]
        self.assertEqual(num_rows, self.sim_length * len(params.age_groups) * 3)


if __name__ == "__main__":
    unittest.main()
