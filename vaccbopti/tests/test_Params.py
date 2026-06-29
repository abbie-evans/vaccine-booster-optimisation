# FILE FOR TESTING THE PARAMS CLASS SO THAT ERRORS RISE WHERE THEY SHOULD

# Import useful modules
import unittest
import numpy as np
from unittest import TestCase
from vaccbopti.classes.params import Params
from unittest import mock


# Define testing class
class TestParams(TestCase):
    """A class to test that the Params class is set up and runs correctly."""

    def setUp(self):
        """Create a test Params object."""
        self.testParams = Params.instance()

    def test_integration_gamma(self):
        """Ensure that the function runs for each k in values (one Lk) for gamma distribution"""
        np.testing.assert_array_equal(round(self.testParams.integration(1, "gamma", [2, 1])[0], 2), 0.1)

    def test_integration_weibull(self):
        """Ensure that the function runs for each k in values (one Lk) for weibull distribution"""
        np.testing.assert_array_equal(round(self.testParams.integration(1, "weibull", [2, 1])[0], 2), 0.61)

    def test_integral_of_density_probability(self):
        """Ensure that the function runs for each k in values (one Lk)"""
        with mock.patch.object(self.testParams,
                               "integration",
                               return_value=(0.1, 0.001)):
            self.testParams.days_samples = [1, 2, 3, 4]
            np.testing.assert_array_equal(
                self.testParams.integral_of_density_probability("gamma", [2, 1]),
                [0.1, 0.1, 0.1]
            )

    def test_integral_probabilities_array(self):
        """Ensure that the probabilities sum to 1"""
        with mock.patch.object(self.testParams,
                               "integral_of_density_probability",
                               return_value=[0.1, 0.2, 0.3, 0.4]):
            np.testing.assert_array_equal(
                self.testParams.integral_probabilities_array("gamma", [2, 1]),
                [0.0, 0.1, 0.2, 0.3, 0.4]
            )

    def test_calc_fx(self):
        """Test that the exp_val and fx calculation is correct."""
        self.testParams.shape_param = 0
        np.testing.assert_array_equal(self.testParams.calc_fx(1, 1), np.linspace(0.5, 0.5, 5000 + 1))

    def test_calc_nx(self):
        """Test that the nx calculation is correct."""
        np.testing.assert_array_equal(self.testParams.calc_nx(0), np.linspace(0, 0, 5000 + 1))

    def test_error_more_than_one_instance(self):
        """Check if RuntimeError is raised when Params contains an object."""
        with self.assertRaises(RuntimeError) as ve:
            Params()  # equivalent to __init__(self)
        self.assertEqual("This class is a singleton!", str(ve.exception))

    def test_error_instance_not_created(self):
        """Check to make sure that it exists when an instance is set up."""
        test_var = self.testParams.infec_asymp
        self.assertEqual(0.255, test_var)


if __name__ == '__main__':
    unittest.main()
