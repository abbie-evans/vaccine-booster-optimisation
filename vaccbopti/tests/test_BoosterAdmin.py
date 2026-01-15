# test file for the class BoosterAdmin()
import unittest
from unittest import TestCase

from vaccbopti.classes.person import Person
from vaccbopti.classes.params import Params
# from vaccbopti.classes.timesteps import People
from vaccbopti.classes.booster_admin import BoosterAdmin
import random as rd
import numpy as np

params = Params.instance()

class testBoosterAdmin(TestCase):
 
    def test_vaccine_administration(self):
        """Test that after vaccine administration, no eligible people remain unvaccinated"""
        #create dummy population with mixed statuses
        statuses = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'hospitalised', 'dead']
        vacc_statuses = ['unvacc', 'ineligible']
        People = [Person() for p in range(200)]
        for person in People:
            person.age_group = str(np.random.choice(params.age_groups))
            person.status = str(np.random.choice(statuses))
            person.vacc_status = str(np.random.choice(vacc_statuses))
        
        # Run vaccine administration
        test1 = BoosterAdmin()
        test1.vaccine_administration(People, vaccine_choice='old_vacc', 
                                     direction='descend', age_targets='everyone')
        
        # Check that eligible unvaccinated people no longer exist in Population
        # (Eligible = not symptomatic, hospitalised, or dead)
        remaining_unvacc = [p for p in People 
                           if p.status not in ['symptomatic', 'hospitalised', 'dead'] 
                           and p.vacc_status == 'unvacc']
        
        self.assertEqual(len(remaining_unvacc), 0)
        
    def test_vacc_strat_1(self):
        # create a dummy People set
        statuses = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'hospitalised', 'dead']
        vacc_statuses = ['unvacc', 'ineligible']
        People = [Person() for p in range(200)]
        for person in People:
            person.age_group = str(np.random.choice(params.age_groups))
            person.status = str(np.random.choice(statuses))
            person.vacc_status = str(np.random.choice(vacc_statuses))
        
        #count number of vacc people
        count_original = sum(1 for p in People 
                    if p.status not in ['symptomatic', 'hospitalised', 'dead'] 
                    and p.vacc_status == 'unvacc')
        test_VS1 = BoosterAdmin().vacc_strat_1(People)
        count_postVS1 = sum(1 for p in People 
                    if p.vacc_status == 'vacc')
        self.assertEqual(count_original, count_postVS1)

    def test_vacc_strat_3(self):
        """Test strategy 3 on single population: old vaccine to mid-old before availability, new vaccine to mid-young after"""
        statuses = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'hospitalised', 'dead']
        vacc_statuses = ['unvacc', 'ineligible']
        t_newvacc_avail = 10
        
        #dummy set
        People = [Person() for p in range(200)]
        for person in People:
            person.age_group = str(np.random.choice(params.age_groups))
            person.status = str(np.random.choice(statuses))
            person.vacc_status = str(np.random.choice(vacc_statuses))
        
        # Run strategy 3 before vaccine availability (t < t_newvacc_avail)
        admin = BoosterAdmin()
        admin.vacc_strat_3(People, t=5, t_newvacc_avail=t_newvacc_avail)
        
        # Store who was vaccinated before availability
        vaccinated_before = [p for p in People if p.vacc_status == 'vacc']
        
        # Verify vaccinated people before availability are from mid-old age groups
        mid_old_groups = params.old_groups
        for person in vaccinated_before:
            self.assertIn(person.age_group, mid_old_groups,
                         msg=f"Before availability (t=5): vaccinated person age_group '{person.age_group}' should be in mid-old groups {mid_old_groups}")
        
        # Run strategy 3 AFTER vaccine availability (t > t_newvacc_avail) on SAME population
        admin2 = BoosterAdmin()
        admin2.vacc_strat_3(People, t=15, t_newvacc_avail=t_newvacc_avail)
        
        # Get people vaccinated after availability (those now vaccinated but not in vaccinated_before)
        vaccinated_after = [p for p in People if p.vacc_status == 'vacc' and p not in vaccinated_before]
        
        # Verify new vaccinated people after availability are from mid-young age groups
        mid_young_groups = params.young_groups
        for person in vaccinated_after:
            self.assertIn(person.age_group, mid_young_groups,
                         msg=f"After availability (t=15): newly vaccinated person age_group '{person.age_group}' should be in mid-young groups {mid_young_groups}")
        
    def test_vacc_strat_5(self):
        # create a dummy People set
        statuses = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'hospitalised', 'dead']
        vacc_statuses = ['unvacc', 'ineligible']
        People = [Person() for p in range(200)]
        for person in People:
            person.age_group = str(np.random.choice(params.age_groups))
            person.status = str(np.random.choice(statuses))
            person.vacc_status = str(np.random.choice(vacc_statuses))
        
        #count number of vacc people
        count_original5 = sum(1 for p in People 
                    if p.status not in ['symptomatic', 'hospitalised', 'dead'] 
                    and p.vacc_status == 'unvacc')
        test_VS5 = BoosterAdmin().vacc_strat_5(People)
        count_postVS5 = sum(1 for p in People 
                    if p.vacc_status == 'vacc')
        self.assertEqual(count_original5, count_postVS5)

    def test_vacc_strat_6(self):
        # create a dummy People set
        statuses = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'hospitalised', 'dead']
        vacc_statuses = ['unvacc', 'ineligible']
        People = [Person() for p in range(200)]
        for person in People:
            person.age_group = str(np.random.choice(params.age_groups))
            person.status = str(np.random.choice(statuses))
            person.vacc_status = str(np.random.choice(vacc_statuses))
        
        #count number of vacc people
        count_original6 = sum(1 for p in People 
                    if p.status not in ['symptomatic', 'hospitalised', 'dead'] 
                    and p.vacc_status == 'unvacc')
        for a in range(20):
            test_VS6 = BoosterAdmin().vacc_strat_6(People, t=a, t_newvacc_avail=15)

        count_postVS6 = sum(1 for p in People 
                    if p.vacc_status == 'vacc')
        self.assertEqual(count_original6, count_postVS6)

# #run test vaccination

