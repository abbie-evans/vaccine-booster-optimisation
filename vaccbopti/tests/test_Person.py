# FILE FOR TESTING THE PERSON CLASS

# Import useful modules
from vaccbopti.classes.params import Params
from vaccbopti.classes.person import Person
import unittest
from unittest import TestCase
params = Params.instance()


# Define testing class
class test_person(TestCase):
    """A class to test that the Person class is set up and runs correctly."""

    def setUp(self):
        """Create a test Person object."""
        self.testPerson = Person()
    
    def test_get_age_group(self):
        self.assertEqual(self.testPerson.age_group, None)
        self.testPerson.get_age_group(0)
        self.assertEqual(self.testPerson.age_group, '0-4')

if __name__ == "__main__":
    unittest.main()
