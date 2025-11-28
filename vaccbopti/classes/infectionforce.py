# File for force of infection class

from vaccbopti.classes.params import Params
from vaccbopti.classes.infectioncount import InfectionCount


class InfectionForce:

    '''
    This class defines the function to compute the force of infection on
    each susceptible individual in age group a given by the function:
    Lambda_a = infect_rate_param_a * sum over age groups 1-16 (contactmatrix_ab/number of indivs in a)
    * nb of infected individuals in group b + probability of being asymptomatically infected * Asymptomatic in group b

    '''
    def __init__(self):
        params = Params.instance()
        self.lambda_list = []
        self.infec_rate_param = params.infec_rate_param
        self.age_groups = params.age_groups
        self.contactmatrix = params.contactmatrix
        self.n_indivs_a = params.n_indivs_a
        self.count_df = InfectionCount.instance().count_df
        # this is a good structure bc it makes sure it's always up to date
        self.infec_asymp = params.infec_asymp

    def calc_z(self, a, b):
        '''
        This function accesses the counts of infected people
        and calculates what we define as z, the part of the lambda
        function to be summed ultimately.
        INPUT a = fixed age group for which lambda will be calculated (integer)
        b = other age group to which contact is compared.
        '''
        # first just calculate (I(b) + p*A(b))
        # input: age group a (fixed as we are calculating lambda for group a)
        # and age group b (will loop over)
        I_b = self.count_df.loc[b, 'symptomatic']
        p = self.infec_asymp
        A_b = self.count_df.loc[b, 'asymptomatic']
        M_ab = self.contactmatrix[a][b]
        N_a = self.n_indivs_a[a]
        z = M_ab / N_a * (I_b + p * A_b)
        return z

    def calc_lambda(self, a):
        '''
        This function calculates lambda from the obtained value of calc_z().
        '''
        #a loop, for b in range(len(age_groups))
        sum_z = 0
        for b in range(len(self.age_groups)):
            sub_z = self.calc_z(a, b=b)
            sum_z = sum_z + sub_z
        lambda_a = self.infec_rate_param * sum_z
        return lambda_a

    def all_lambda(self):
        for a in self.age_groups:
            lambda_a = self.calc_lambda(a)
            self.lambda_list.append(lambda_a)
