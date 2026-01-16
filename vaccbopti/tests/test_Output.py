# test file for output.py
from unittest import TestCase
import numpy as np
from vaccbopti.classes.output import Output
from vaccbopti.classes.params import Params
from vaccbopti.classes.person import Person

params = Params.instance()

class test_Output(TestCase):
    def setUp(self):
        self.testoutput = Output()
        statuses = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'hospitalised', 'dead']
        vacc_statuses = ['unvacc', 'ineligible']
        self.People = [Person() for p in range(500)]
        for person in self.People:
            person.age_group = str(np.random.choice(params.age_groups))
            person.status = str(np.random.choice(statuses))
            person.vacc_status = str(np.random.choice(vacc_statuses))
       
    def test_setdf(self):
        self.testoutput.setdf()
        length_col = len(self.testoutput.statusDF.columns)
        # we require 129 columns because 16 age groups, 4 statuses and 2 vacc-statuses + time
        required_cols = 129
        self.assertEqual(length_col, required_cols)




# row number is the same as days
# group number is the correct name
# check that the sum is the right sum