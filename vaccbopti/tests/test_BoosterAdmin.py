# FILE FOR TESTING THE BOOSTERADMIN CLASS

# Import useful modules
import numpy as np
import unittest
from unittest import TestCase
from vaccbopti.classes.person import Person
from vaccbopti.classes.params import Params
from vaccbopti.classes.booster_admin import BoosterAdmin
params = Params.instance()
admin = BoosterAdmin()


# Define testing class
class testBoosterAdmin(TestCase):
    """A class to test that the BoosteAdmin class is set up and runs correctly."""

    def setUp(self):
        """Create a dummy population with mixed statuses"""
        self.statuses = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'hospitalised', 'dead']
        self.vacc_statuses = ['unvacc', 'ineligible']
        self.People = [Person() for p in range(200)]
        for person in self.People:
            person.age_group = str(np.random.choice(params.age_groups))
            person.status = str(np.random.choice(self.statuses))
            person.vacc_status = str(np.random.choice(self.vacc_statuses))
        self.vacc_amount = 40

    def test_update_suceptibility(self):
        """Tests that the susceptibility update function works correctly."""
        # Check old vaccine
        person = self.People[0]
        admin.update_susceptibility('old_vacc', person)
        self.assertEqual(person.immunity_time_exvacc, 0)
        self.assertEqual(person.immunity_time_newvacc, -1)
        self.assertEqual(person.vacc_status, 'vacc')
        person = self.People[1]
        admin.update_susceptibility('new_vacc', person)
        self.assertEqual(person.immunity_time_exvacc, -1)
        self.assertEqual(person.immunity_time_newvacc, 0)
        self.assertEqual(person.vacc_status, 'vacc')

    def test_vaccine_administration(self):
        """Test that after vaccine administration, no eligible self.People remain unvaccinated."""
        # Run vaccine administration
        admin.vaccine_administration(self.People, 200, vaccine_choice='old_vacc',
                                     direction='descend', age_targets='everyone')
        # Check that eligible unvaccinated People no longer exist in Population
        # (Eligible = not symptomatic, hospitalised, or dead)
        remaining_unvacc = [p for p in self.People
                            if p.status not in ['symptomatic', 'hospitalised', 'dead']
                            and p.vacc_status == 'unvacc']
        self.assertEqual(len(remaining_unvacc), 0)

    def test_vacc_strat_1(self):
        """Test that vaccine strategy 1 works correctly."""
        # Count number of vaccinated People
        count_original = sum(1 for p in self.People
                             if p.status not in ['symptomatic', 'hospitalised', 'dead']
                             and p.vacc_status == 'unvacc')
        admin.vacc_strat_1(self.People, self.vacc_amount)
        count_post = sum(1 for p in self.People
                         if p.vacc_status == 'vacc')
        self.assertNotEqual(count_original, count_post)

    def test_vacc_strat_2(self):
        """Test that vaccine strategy 2 works correctly."""
        # Count number of vaccinated People
        count_original = sum(1 for p in self.People
                             if p.status not in ['symptomatic', 'hospitalised', 'dead']
                             and p.vacc_status == 'unvacc')
        for a in range(20):
            admin.vacc_strat_2(self.People, self.vacc_amount, t=a, t_newvacc_avail=15)
        count_postVS = sum(1 for p in self.People
                           if p.vacc_status == 'vacc')
        self.assertEqual(count_original, count_postVS)

    def test_vacc_strat_3(self):
        """Test that vaccine strategy 3 on single population:
           - old vaccine to mid-old before availability
           - new vaccine to mid-young after
        """
        t_newvacc_avail = 10
        # Run strategy 3 before vaccine availability (t < t_newvacc_avail)
        admin.vacc_strat_3(self.People, self.vacc_amount, t=5, t_newvacc_avail=t_newvacc_avail)
        # Store who was vaccinated before availability
        vaccinated_before = [p for p in self.People if p.vacc_status == 'vacc']
        # Verify vaccinated People before availability are from mid-old age groups
        for person in vaccinated_before:
            self.assertIn(person.age_group, params.old_groups)
        # Run strategy 3 after vaccine availability (t > t_newvacc_avail) on population
        admin.vacc_strat_3(self.People, self.vacc_amount, t=15, t_newvacc_avail=t_newvacc_avail)
        # Get People vaccinated after availability (those now vaccinated but not in vaccinated_before)
        vaccinated_after = [p for p in self.People if p.vacc_status == 'vacc' and p not in vaccinated_before]
        # Verify new vaccinated self.People after availability are from mid-young age groups
        for person in vaccinated_after:
            self.assertIn(person.age_group, params.young_groups)

    def test_vacc_strat_4(self):
        """Test that vaccine strategy 4 works correctly."""
        t_newvacc_avail = 10
        # Run strategy 4 before vaccine availability (t < t_newvacc_avail)
        admin.vacc_strat_4(self.People, self.vacc_amount, t=5, t_newvacc_avail=t_newvacc_avail)
        # Store who was vaccinated before availability
        vaccinated_before = [p for p in self.People if p.vacc_status == 'vacc']
        # Verify vaccinated People before availability are from yound-mid age groups
        for person in vaccinated_before:
            self.assertIn(person.age_group, params.young_groups)
        # Run strategy 4 after vaccine availability (t > t_newvacc_avail) on population
        admin.vacc_strat_3(self.People, self.vacc_amount, t=15, t_newvacc_avail=t_newvacc_avail)
        # Get People vaccinated after availability (those now vaccinated but not in vaccinated_before)
        vaccinated_after = [p for p in self.People if p.vacc_status == 'vacc' and p not in vaccinated_before]
        # Verify new vaccinated self.People after availability are from mid-young age groups
        for person in vaccinated_after:
            self.assertIn(person.age_group, params.old_groups)

    def test_vacc_strat_5(self):
        """Test that vaccine strategy 5 works correctly."""
        # Count number of vaccinated People
        count_original = sum(1 for p in self.People
                             if p.status not in ['symptomatic', 'hospitalised', 'dead']
                             and p.vacc_status == 'unvacc')
        admin.vacc_strat_5(self.People, self.vacc_amount)
        count_postVS = sum(1 for p in self.People
                           if p.vacc_status == 'vacc')
        self.assertNotEqual(count_original, count_postVS)

    def test_vacc_strat_6(self):
        """Test that vaccine strategy 6 works correctly."""
        # Count number of vaccinated People
        count_original = sum(1 for p in self.People
                             if p.status not in ['symptomatic', 'hospitalised', 'dead']
                             and p.vacc_status == 'unvacc')
        for a in range(20):
            admin.vacc_strat_6(self.People, self.vacc_amount, t=a, t_newvacc_avail=15)
        count_postVS = sum(1 for p in self.People
                           if p.vacc_status == 'vacc')
        self.assertEqual(count_original, count_postVS)


if __name__ == "__main__":
    unittest.main()
