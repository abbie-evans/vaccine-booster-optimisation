# FILE FOR TESTING THE SIMULATION CLASS WHEN A RUN HAPPENS

# Import useful modules
import unittest
from unittest import TestCase
import numpy as np
from vaccbopti.classes import Params
from vaccbopti import run_simulation
params = Params.instance()


# Define testing class
class test_run_simulation(TestCase):
    """A class to test that the Timesteps class is set up and runs correctly."""

    def setUp(self):
        """Create a test Timesteps object."""
        self.number_runs = 2
        self.sim_length = 5
        self.num_people = 32
        self.n_infec = 5
        self.prop_ineligible = 0.2
        self.R_e = 1.5
        self.vacc_amount = 10
        self.t_newvacc_avail = 2

    def test_setup(self):
        """Ensure that Simulation class is set up with correct defaults."""
        testRunSim = run_simulation.Simulation(number_runs=self.number_runs, sim_length=self.sim_length,
                                               num_people=self.num_people, n_infec=self.n_infec,
                                               prop_ineligible=self.prop_ineligible, R_e=self.R_e, vacc_strat=0,
                                               vacc_amount=self.vacc_amount, t_newvacc_avail=self.t_newvacc_avail)
        self.assertEqual(testRunSim.number_runs, self.number_runs)
        self.assertEqual(testRunSim.sim_length, self.sim_length)
        self.assertEqual(testRunSim.num_people, self.num_people)
        self.assertEqual(testRunSim.n_infec, self.n_infec)
        self.assertEqual(testRunSim.prop_ineligible, self.prop_ineligible)
        self.assertEqual(testRunSim.R_e, self.R_e)
        self.assertEqual(testRunSim.vacc_amount, self.vacc_amount)
        self.assertEqual(testRunSim.t_newvacc_avail, self.t_newvacc_avail)
        self.assertEqual(testRunSim.vacc_strat, 0)
        self.assertEqual(len(testRunSim.timepoints), self.sim_length)
        self.assertEqual(len(testRunSim.statusDF_sum),
                         self.sim_length * len(params.age_groups) * len(testRunSim.vaccine))
        self.assertEqual(len(testRunSim.statusDF_sum.columns), len(testRunSim.df_status))
        self.assertEqual(len(testRunSim.statusDF_sum_squares),
                         self.sim_length * len(params.age_groups) * len(testRunSim.vaccine))
        self.assertEqual(len(testRunSim.statusDF_sum_squares.columns), len(testRunSim.df_status))

    def test_run(self):
        """Test that the simulation run works correctly."""
        testRunSim = run_simulation.Simulation(number_runs=self.number_runs, sim_length=self.sim_length,
                                               num_people=self.num_people, n_infec=self.n_infec,
                                               prop_ineligible=self.prop_ineligible, R_e=self.R_e, vacc_strat=0,
                                               vacc_amount=self.vacc_amount, t_newvacc_avail=self.t_newvacc_avail)
        testRunSim.run()
        # Check mean output
        statusDF_mean = testRunSim.statusDF_sum / self.number_runs
        self.assertTrue(testRunSim.statusDF_mean.equals(statusDF_mean))
        # Get std output
        statusDF_std = ((testRunSim.statusDF_sum_squares / self.number_runs)
                        - (testRunSim.statusDF_sum / self.number_runs) ** 2)
        statusDF_std = np.sqrt(statusDF_std)
        vacc_map = {'unvaccinated': 'unvaccinated', 'ex_vaccine': 'vaccinated', 'new_vaccine': 'vaccinated'}
        std_combined = statusDF_std.reset_index()
        std_combined['vacc_status'] = std_combined['vacc_status'].map(vacc_map)
        std_combined = std_combined.set_index(['t', 'ages', 'vacc_status'])
        # Now convert from SD into variance for pooling
        var_combined = std_combined ** 2
        statusDF_std = (var_combined.groupby(['t', 'vacc_status']).sum().pow(0.5))
        self.assertTrue(testRunSim.statusDF_std.equals(statusDF_std))


if __name__ == "__main__":
    unittest.main()
