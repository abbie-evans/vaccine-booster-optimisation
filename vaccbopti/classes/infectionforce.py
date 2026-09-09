# FILE CONTAINING THE CALCULATIONS FOR FORCE OF INFECTION.

# Important and useful modules
import numpy as np
from .params import Params
params = Params.instance()


# Define InfectionForce class
class InfectionForce:
    """Defines the function to compute the force of infection on each susceptible individual.
    The equation of force of infection, lambda_a, in age group a is given by:
        lambda_a = infect_rate_param_a *
                   sum over b age groups 1-16 { [contactmatrix_ab/n of indiv in a] *
                                                [n of infected indiv in b +
                                                (p(being asymptomatically infected) * asymptomatic indiv in b)] }

    Parameters
    - infec_rate_param : infection rate parameter, reflecting susceptibility of individuals in age group a
    - age_groups: age group of individuals
    - contactmatrix: mean daily number of contacts that an individual in age group b has with individuals in age group a
    - prop_indivs_a: proportion of individuals in age group a
    - num_people: total number of people in the simulation
    - count_df: dataframe describing number of asymptomatic and symptomatically infected individuals in age group
    - infec_asymp: [constant] infectiousness of asymptomatic infected individuals, relative to symptomatic infected individuals
    """

    def __init__(self):
        """Initialise InfectionForce class.
        Parameters:
            lambda_list (list): the force of infection for each age group 1-16
        """
        self.lambda_list = np.zeros(16)

    def calc_z(self, a, b, infectioncount, num_people=100000):
        """Accesses the counts of infected people and calculates what we define as z, the sum.
        z = [contactmatrix_ab/n of indiv in a] * [n of infected indiv in b +
                                                  (p(being asymptomatically infected) * asymptomatic indiv in b)]
        Parameters:
            a (int): fixed age group for which lambda will be calculated
            b (int): the other age group to which contact is compared
            infectioncount (df): the pandas dataframe to read the counts of (a)symptomatic people
            num_people (int): the total number of people in the simulation
        """
        infectioncount = infectioncount.groupby('ages').sum()
        M_ab = params.contactmatrix[a][b]
        N_a = int(round(params.prop_indivs_a[a] * num_people))
        I_b = float(infectioncount.loc[params.age_groups[b], ['symptomatic', 'hospitalised']].sum())
        p = params.infec_asymp
        A_b = float(infectioncount.loc[params.age_groups[b], 'asymptomatic'])
        z = (M_ab / N_a) * (I_b + (p * A_b))
        return z

    def calc_lambda(self, a, infectioncount, infec_rate_param=params.infec_rate_param, num_people=100000):
        """Calculates lambda for age group a from the obtained value of calc_z().
        lambda_a = infect_rate_param_a * sum over b age groups 1-16 {z}
        Parameters:
            a (int): fixed age group for which lambda will be calculated
            infec_rate_param (list): the infection rate parameter, beta
            num_people (int): the total number of people in the simulation
        """
        sum_z = 0  # holds the sum of z
        test_n = 0  # for testing purposes
        for b in range(len(params.age_groups)):  # loop to sum z
            sub_z = self.calc_z(a, b, infectioncount, num_people=num_people)
            sum_z += sub_z  # sum individual z to overall z
            test_n += 1
        lambda_a = float(infec_rate_param[a] * sum_z)  # must be float instead of npfloat64
        return lambda_a, test_n

    def all_lambda(self, infectioncount, infec_rate_param=params.infec_rate_param, num_people=100000):
        """Calculates lambda for each age group a, and holds them in a list."""
        for a in range(len(params.age_groups)):
            lambda_a, test_n = self.calc_lambda(a, infectioncount, infec_rate_param, num_people)
            self.lambda_list[a] = lambda_a
