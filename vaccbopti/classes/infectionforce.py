# File for force of infection class

from vaccbopti.classes.params import Params
from vaccbopti.classes.infectioncount import InfectionCount
params = Params.instance()


class InfectionForce:

    '''
    This class defines the function to compute the force of infection on
    each susceptible individual in age group a given by the function:
    Lambda_a = infect_rate_param_a * sum over age groups 1-16 (contactmatrix_ab/number of indivs in a)
    * nb of infected individuals in group b + probability of being asymptomatically infected * Asymptomatic in group b

    Variables used in the functions of the class
    - infec_rate_param : infection rate parameter, reflecting susceptibility of indivs in age group a
    - age_groups:age group of indiv
    - contactmatrix: mean daily number of contacts that an indiv in age group b has with an indiv ina ge group a
    - n_indivs_a: number of individuals in age group a
    - count_df: dataframe describing number of asymptomatic and symptomatically infected indivs in age group
    - infec_asymp: [constant] infectiousness of asymptomatic infected indiv, relative to symptomatic infectd individual
    '''
    def __init__(self):
        self.lambda_list = []
        self.count_df = InfectionCount.instance().count_df

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
        p = params.infec_asymp
        A_b = self.count_df.loc[b, 'asymptomatic']
        M_ab = params.contactmatrix[a][b]
        N_a = params.n_indivs_a[a]
        z = M_ab / N_a * (I_b + p * A_b)
        return z

    def calc_lambda(self, a):
        '''
        This function calculates lambda from the obtained value of calc_z().
        '''
        #a loop, for b in range(len(age_groups))
        sum_z = 0
        # for testing purposes
        test_n = 0
        for b in range(len(params.age_groups)):
            sub_z = self.calc_z(a, b=b)
            sum_z = sum_z + sub_z
            test_n += 1
        # need to change to float instead of numpyfloat64
        lambda_a = float(params.infec_rate_param[a] * sum_z)
        return lambda_a, test_n

    def all_lambda(self):
        for a in params.age_groups:
            lambda_a = self.calc_lambda(a)
            self.lambda_list.append(lambda_a)
