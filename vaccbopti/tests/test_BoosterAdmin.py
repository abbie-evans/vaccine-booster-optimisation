# FILE FOR TESTING THE BOOSTERADMIN CLASS

# Import useful modules
import unittest
from unittest import TestCase
from vaccbopti.classes.person import Person
from vaccbopti.classes.params import Params
from vaccbopti.classes.booster_admin import BoosterAdmin
params = Params.instance()


# Define testing class
class testBoosterAdmin(TestCase):
    """A class to test that the BoosterAdmin class is set up and runs correctly."""

    def setUp(self):
        """Create a dummy population with mixed statuses"""
        self.people = [Person() for p in range(80)]
        example_ages = params.age_groups * 5
        i = 0
        for person in self.people:
            person.age_group = example_ages[i]
            person.status = 'susceptible'
            person.vacc_status = 'unvacc'
            i += 1
        self.vacc_amount = 40
        self.admin = BoosterAdmin()

    def test_update_suceptibility(self):
        """Tests that the susceptibility update function works correctly."""
        # Check old vaccine
        person = self.people[0]
        self.admin.update_susceptibility('ex_vacc', person)
        self.assertEqual(person.immunity_time_exvacc, 0)
        self.assertEqual(person.immunity_time_newvacc, -1)
        self.assertEqual(person.vacc_status, 'ex_vacc')
        person = self.people[1]
        self.admin.update_susceptibility('new_vacc', person)
        self.assertEqual(person.immunity_time_exvacc, -1)
        self.assertEqual(person.immunity_time_newvacc, 0)
        self.assertEqual(person.vacc_status, 'new_vacc')

    def test_vaccine_administration(self):
        """Test that after vaccine administration, no eligible self.people remain unvaccinated."""
        # Run vaccine administration
        self.admin.vaccine_administration(self.people, 80, vaccine_choice='ex_vacc',
                                          direction='descend', age_targets='everyone')
        # Check that eligible unvaccinated people no longer exist in Population
        # (Eligible = not symptomatic, hospitalised, or dead)
        remaining_unvacc = [p for p in self.people
                            if p.status not in ['symptomatic', 'hospitalised', 'dead']
                            and p.vacc_status == 'unvacc']
        self.assertEqual(len(remaining_unvacc), 0)

    def test_vacc_strat_1(self):
        """Test that vaccine strategy 1 works correctly."""
        # Count number of vaccinated people
        count_original = sum(1 for p in self.people
                             if p.vacc_status == 'unvacc')
        self.admin.vacc_strat_1(self.people, self.vacc_amount)
        count_post = sum(1 for p in self.people
                         if p.vacc_status == 'unvacc')
        self.assertNotEqual(count_original, count_post)

    def test_vacc_strat_2(self):
        """Test that vaccine strategy 2 works correctly."""
        # Count number of vaccinated people
        count_original = sum(1 for p in self.people
                             if p.vacc_status == 'unvacc')
        for a in range(5):
            self.admin.vacc_strat_2(self.people, self.vacc_amount, t=a, t_newvacc_avail=3)
            count_postVS = sum(1 for p in self.people if p.vacc_status == 'unvacc')
            if a < 3:  # check vaccination doesn't happen before it's available
                self.assertEqual(count_original, count_postVS)
            if a > 3:  # check vaccination does't happen after it's available
                self.assertNotEqual(count_original, count_postVS)

    def test_vacc_strat_3(self):
        """Test that vaccine strategy 3 on single population:
           - old vaccine to mid-old before availability
           - new vaccine to mid-young after
           - then old vaccine again once all of mid-young had been vaccinated
        """
        t_newvacc_avail = 10
        # Run strategy 3 before vaccine availability (t < t_newvacc_avail)
        self.admin.vacc_strat_3(self.people, self.vacc_amount, t=5, t_newvacc_avail=t_newvacc_avail)
        # Store who was vaccinated before availability
        vaccinated_before = [p for p in self.people if p.vacc_status == 'ex_vacc']
        # Verify vaccinated people before availability are from mid-old age groups
        for person in vaccinated_before:
            self.assertIn(person.age_group, params.old_groups)
        # Check that there are still eligible people for the new vaccine
        new_eligible = [p for p in self.people if p.vacc_status == 'unvacc' and p.age_group in params.young_groups]
        self.assertGreater(len(new_eligible), 0)
        # Run strategy 3 after vaccine availability (t > t_newvacc_avail) on population
        self.admin.vacc_strat_3(self.people, 80, t=15, t_newvacc_avail=t_newvacc_avail)
        # Check that all eligible people have been vaccinated
        new_eligible = [p for p in self.people if p.vacc_status == 'unvacc' and p.age_group in params.young_groups]
        self.assertEqual(len(new_eligible), 0)
        # Get people vaccinated after availability (those now vaccinated but not in vaccinated_before)
        vaccinated_after = [p for p in self.people if p.vacc_status == 'new_vacc' and p not in vaccinated_before]
        # Verify new vaccinated self.people after availability are from mid-young age groups
        for person in vaccinated_after:
            self.assertIn(person.age_group, params.young_groups)
        # Check strategy 3 after all of the young has been vaccinated
        self.admin.vacc_strat_3(self.people, self.vacc_amount, t=20, t_newvacc_avail=t_newvacc_avail)
        vaccinated_complete = [p for p in self.people if p.vacc_status == 'new_vacc'
                               and p not in vaccinated_before
                               and p not in vaccinated_after]
        for person in vaccinated_complete:
            self.assertIn(person.age_group, params.old_groups)

    def test_vacc_strat_4(self):
        """Test that vaccine strategy 4 works correctly."""
        t_newvacc_avail = 10
        # Run strategy 4 before vaccine availability (t < t_newvacc_avail)
        self.admin.vacc_strat_4(self.people, self.vacc_amount, t=5, t_newvacc_avail=t_newvacc_avail)
        # Store who was vaccinated before availability
        vaccinated_before = [p for p in self.people if p.vacc_status == 'ex_vacc']
        # Verify vaccinated people before availability are from yound-mid age groups
        for person in vaccinated_before:
            self.assertIn(person.age_group, params.young_groups)
        # Check that there are still eligible people for the new vaccine
        new_eligible = [p for p in self.people if p.vacc_status == 'unvacc' and p.age_group in params.old_groups]
        self.assertGreater(len(new_eligible), 0)
        # Run strategy 4 after vaccine availability (t > t_newvacc_avail) on population
        self.admin.vacc_strat_4(self.people, 80, t=15, t_newvacc_avail=t_newvacc_avail)
        # Check that all eligible people have been vaccinated
        new_eligible = [p for p in self.people if p.vacc_status == 'unvacc' and p.age_group in params.old_groups]
        self.assertEqual(len(new_eligible), 0)
        # Get people vaccinated after availability (those now vaccinated but not in vaccinated_before)
        vaccinated_after = [p for p in self.people if p.vacc_status == 'new_vacc' and p not in vaccinated_before]
        # Verify new vaccinated self.people after availability are from mid-young age groups
        for person in vaccinated_after:
            self.assertIn(person.age_group, params.old_groups)
        # Check strategy 4 after all of the young has been vaccinated
        self.admin.vacc_strat_4(self.people, self.vacc_amount, t=20, t_newvacc_avail=t_newvacc_avail)
        vaccinated_complete = [p for p in self.people if p.vacc_status == 'new_vacc'
                               and p not in vaccinated_before
                               and p not in vaccinated_after]
        for person in vaccinated_complete:
            self.assertIn(person.age_group, params.young_groups)

    def test_vacc_strat_5(self):
        """Test that vaccine strategy 5 works correctly."""
        # Count number of vaccinated people
        count_original = sum(1 for p in self.people
                             if p.status not in ['symptomatic', 'hospitalised', 'dead']
                             and p.vacc_status == 'unvacc')
        self.admin.vacc_strat_5(self.people, self.vacc_amount)
        count_postVS = sum(1 for p in self.people if p.vacc_status == 'unvacc')
        self.assertNotEqual(count_original, count_postVS)

    def test_vacc_strat_6(self):
        """Test that vaccine strategy 6 works correctly."""
        # Count number of vaccinated people
        count_original = sum(1 for p in self.people
                             if p.status not in ['symptomatic', 'hospitalised', 'dead']
                             and p.vacc_status == 'unvacc')
        for a in range(20):
            self.admin.vacc_strat_6(self.people, self.vacc_amount, t=a, t_newvacc_avail=15)
        count_postVS = sum(1 for p in self.people if p.vacc_status == 'unvacc')
        self.assertNotEqual(count_original, count_postVS)


if __name__ == "__main__":
    unittest.main()
