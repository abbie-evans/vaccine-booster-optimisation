# FILE FOR TESTING THE PARAMS CLASS SO THAT ERRORS RISE WHERE THEY SHOULD

# Import useful modules
import unittest
from unittest import TestCase
from vaccbopti.classes.params import Params


# Define testing class
class TestParams(TestCase):
    """A class to test that the Person class is set up and runs correctly."""

    def test_error_more_than_one_instance(self):
        """Check if RuntimeError is raised when Params contains an object."""
        with self.assertRaises(RuntimeError) as ve:
            Params()  # equivalent to __init__(self)
        self.assertEqual("This class is a singleton!", str(ve.exception))

    def test_error_instance_not_created(self):
        """Check to make sure that it exists when an instance is set up."""
        test_var = Params.instance().infec_asymp
        self.assertEqual(0.255, test_var)


if __name__ == '__main__':
    unittest.main()
