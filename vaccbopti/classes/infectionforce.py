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
                   sum over b age groups 1-16 { [contact_matrix_ab/n of indiv in a] *
                                                [n of infected indiv in b +
                                                (p(being asymptomatically infected) * asymptomatic indiv in b)] }

    Parameters
    - infec_rate_params : infection rate parameter, reflecting susceptibility of individuals in age group a
    - age_groups: age group of individuals
    - contact_matrix: mean daily number of contacts that an individual in age group b has with individuals in age group a
    - prop_indivs_a: proportion of individuals in age group a
    - num_people: total number of people in the simulation
    - count_df: dataframe describing number of asymptomatic and symptomatically infected individuals in age group
    - infec_asymp: [constant] infectiousness of asymptomatic infected individuals, relative to symptomatic infected
                    individuals
    """

    def __init__(self):
        """Initialise InfectionForce class.
        Parameters:
            lambda_list (list): the force of infection for each age group 1-16
        """
        self.lambda_list = np.zeros(16)

    def calc_z(self, a, b, infection_count, num_people=100000):
        """Accesses the counts of infected people and calculates what we define as z.
        Defined as: transmission to age group a from b, based on the proportion of interactions people in age group a
        have with age group b (from the contact matrix) and the number of people who are currently infected in each.
        z = [contact_matrix_ab/n of indiv in a] * [n of infected indiv in b +
                                                  (p(being asymptomatically infected) * asymptomatic indiv in b)]
        Parameters:
            a (int): fixed age group for which lambda will be calculated
            b (int): the other age group to which contact is compared
            infection_count (df): the pandas dataframe to read the counts of (a)symptomatic people
            num_people (int): the total number of people in the simulation
        Returns:
            z (float): the calculated z value, strength of transmission from age group b to a
        """
        infection_count = infection_count.groupby('ages').sum()
        M_ab = params.contact_matrix[a][b]
        N_a = int(round(params.prop_indivs_a[a] * num_people))
        I_b = float(infection_count.loc[params.age_groups[b], ['symptomatic', 'hospitalised']].sum())
        p = params.infec_asymp
        A_b = float(infection_count.loc[params.age_groups[b], 'asymptomatic'])
        z = (M_ab / N_a) * (I_b + (p * A_b))
        return z

    def calc_lambda(self, a, infection_count, infec_rate_params=params.infec_rate_params, num_people=100000):
        """Calculates transmission for age group a across all age groups (from the each value of calc_z()),
        weighted by the infection rate parameter for age group a.
        lambda_a = infect_rate_param_a * sum over b age groups 1-16 {z}
        Parameters:
            a (int): fixed age group for which lambda will be calculated
            infec_rate_params (list): the infection rate parameter, beta
            num_people (int): the total number of people in the simulation
        Returns:
            lambda_a: the overall transmission to age group a
        """
        sum_z = 0  # holds the sum of z
        for b in range(len(params.age_groups)):  # loop to sum z
            sub_z = self.calc_z(a, b, infection_count, num_people=num_people)
            sum_z += sub_z  # sum individual z to overall z
        lambda_a = float(infec_rate_params[a] * sum_z)  # must be float instead of npfloat64
        return lambda_a

    def set_lambda_list(self, infection_count, infec_rate_params=params.infec_rate_params, num_people=100000):
        """Calculates lambda for each age group a, and holds them in a list."""
        for a in range(len(params.age_groups)):
            lambda_a = self.calc_lambda(a, infection_count, infec_rate_params, num_people)
            self.lambda_list[a] = lambda_a
