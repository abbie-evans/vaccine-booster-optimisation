#the tests to write:
# does calc_z calculate correctly?
#does calc_lambda add 16 values?


import unittest
from unittest import TestCase
from vaccbopti.classes.infectionforce import InfectionForce
from vaccbopti.classes.params import Params


class TestInfectionForce(TestCase):

    def setUp(self):
        self.testInfectionForce = InfectionForce()
        self.parameters = Params.instance()

    def test_correct_params(self):
        '''
        Test that the parameters are initiated correctly from Params
        '''
        self.assertEqual(self.testInfectionForce.infec_rate_param, self.parameters.infec_rate_param)
        self.assertEqual(self.testInfectionForce.contactmatrix[1][2], self.parameters.contactmatrix[1][2])
        self.assertEqual(self.testInfectionForce.n_indivs_a, self.parameters.n_indivs_a)
        self.assertEqual(self.testInfectionForce.infec_asymp, 0.255)

    def test_calc_z(self):
        '''
        Test that the formula to calculate z calculates z correctly
        by replacing the values by 2 and resetting them afterwards.
        '''
        
        self.testInfectionForce.count_df = self.testInfectionForce.count_df.replace(0, 2) #add values
        print(self.testInfectionForce.count_df)

        # define the test values and compute manually
        test_I_b = 2
        test_A_b = 2
        test_p = 0.255
        test_M_12 = 3.81832
        test_N_a = 6112
        test_manual = test_M_12 / test_N_a * (test_I_b + test_p * test_A_b)
        # execute the function in the class InfectionForce
        test_function = self.testInfectionForce.calc_z(1, 2)
        self.assertEqual(test_function, test_manual)
        # set df back to all zeros
        self.testInfectionForce.count_df = self.testInfectionForce.count_df.replace(2, 0)
        # if the function replaces one value correctly, it should replace all of them
        self.assertEqual(list(self.testInfectionForce.count_df.iloc[1, :]), [0, 0])

    # def test_calc_lambda_a(self):


if __name__ == '__main__':
    unittest.main()
