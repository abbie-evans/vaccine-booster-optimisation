# FILE FOR TESTING THE INFECTIONFORCE CLASS

# Import useful modules
import unittest
from unittest import TestCase
from vaccbopti.classes.params import Params
from vaccbopti.classes.infectionforce import InfectionForce
from vaccbopti.classes.infectioncount import InfectionCount
parameters = Params.instance()


# Define testing class
class TestInfectionForce(TestCase):
    """A class to test that the InfectionForce class is set up and runs correctly."""

    def setUp(self):
        """Create a test InfectionForce object."""
        self.testInfectionForce = InfectionForce()
        self.infection_count = InfectionCount()

    def test_correct_init(self):
        """Test that the empty array is correctly setup."""
        for i in self.testInfectionForce.lambda_list:
            self.assertEqual(i, 0)

    def test_calc_z(self):
        """Test that the formula to calculate z correctly by replacing the values by 2."""
        # Define the test values and compute manually
        self.infection_count.count_df = self.infection_count.count_df.replace(0, 2)
        test_I_b = 12
        test_A_b = 6
        test_p = 0.255
        test_M_12 = 3.81832
        test_N_a = 6112
        test_manual = test_M_12 / test_N_a * (test_I_b + test_p * test_A_b)
        # Execute the function in the class InfectionForce
        test_function = self.testInfectionForce.calc_z(1, 2, self.infection_count.count_df)
        self.assertEqual(test_function, test_manual)

    def test_calc_lambda(self):
        """Tests that the calculation for overall lambda is correct."""
        test_function, test_nb = self.testInfectionForce.calc_lambda(1, self.infection_count.count_df)
        self.test_nb = float(1.1)
        loop_times = 16
        self.assertEqual(loop_times, test_nb)  # the function should run over 16 age groups
        self.assertEqual(type(test_function), type(self.test_nb))  # output value should be correct

    def test_set_lambda_list(self):
        """Tests that the function to add all lambda to the list is correct."""
        self.testInfectionForce.set_lambda_list(self.infection_count.count_df)
        self.assertEqual(len(self.testInfectionForce.lambda_list), 16)
        for i in self.testInfectionForce.lambda_list:
            self.assertIsInstance(i, float)


if __name__ == '__main__':
    unittest.main()
