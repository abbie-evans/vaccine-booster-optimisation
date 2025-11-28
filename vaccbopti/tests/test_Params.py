# test file for ensuring error raised are as expected

import unittest
from unittest import TestCase
from vaccbopti.classes.params import Params

# check if the RuntimeError is raised when the Params._instance contains an object


class TestParams(TestCase):

    def test_error_more_than_one_instance(self):
        with self.assertRaises(RuntimeError) as ve:
            Params()  # equivalent to __init__(self)
        self.assertEqual("This class is a singleton!", str(ve.exception))

    def test_error_instance_not_created(self):
        test_var = Params.instance().infec_asymp
        self.assertEqual(0.255, test_var)


if __name__ == '__main__':
    unittest.main()
