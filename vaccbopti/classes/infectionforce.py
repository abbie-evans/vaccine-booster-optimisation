# File for force of infection class

from person import Person
from params import Params
from infectioncount import InfectionCount

class InfectionForce:
    '''


    '''
    def __init__(self):
        self.lambda_list = []
        self.infect_rate_param = Params.instance().infect_rate_param
        self.age_groups = Params.instance().age_groups
        self.contactmatrix = Params.instance().contactmatrix
        self.n_indivs_a = Params.instance().n_indivs_a
        self.count_df = InfectionCount.count_df
        # this is a good structure bc it makes sure it's always up to date
        self.infect_asymp = Params.instance().infect_asymp

    def calc_z(self, a, b):
        '''
        This function accesses the counts of infected people
        and calculates what we define as z, the part of the lambda
        function to be summed ultimately.
        INPUT a = fixed age group for which lambda will be calculated (integer)
        b = other age group to which contact is compared 
        '''
        # first just calculate (I(b) + p*A(b))
        # input: age group a (fixed as we are calculating lambda for group a)
        # and age group b (will loop over)
        I_b = self.count_df['symptomatic'][b]
        p = self.infect_asymp
        A_b = self.count_df['asymptomatic'][b]
        M_ab = self.contactmatrix[a][b]
        N_a = self.n_indivs_a[a]
        z = M_ab/N_a * (I_b + p*A_b)
        return z
    
    def calc_lambda(self, a):
        '''
        This function calculates lambda from the obtained value of calc_z().
        '''
        #a loop, for b in range(len(age_groups))
        sum_z = 0
        for b in range(len(self.age_groups)):
            sub_z = self.calc_z(a,b=b)
            sum_z = sum_z + sub_z
        lambda_a = self.infect_rate_param * sum_z
        return lambda_a
    
    def all_lambda(self):
        for a in self.age_groups:
            lambda_a = self.calc_lambda(a)
            self.lambda_list.append(lambda_a)
        



