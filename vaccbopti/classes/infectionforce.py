# FILE CONTAINING THE CALCULATIONS FOR FORCE OF INFECTION.

# Important and useful modules
from vaccbopti.classes.params import Params
from vaccbopti.classes.infectioncount import InfectionCount
params = Params.instance()
infectioncount = InfectionCount.instance()


# Define InfectionForce class
class InfectionForce:
    """Defines the function to compute the force of infection on each susceptible individual.
    The equation of force of infection, lambda_a, in age group a is given by:
        lambda_a = infect_rate_param_a *
                   sum over b age groups 1-16 { [contactmatrix_ab/n of indiv in a] *
                                                [n of infected indiv in b +
                                                (p(being asymptomatically infected) * asymptomatic indiv in b)] }

    Parameters
    - infec_rate_param : infection rate parameter, reflecting susceptibility of indivs in age group a
    - age_groups:age group of indiv
    - contactmatrix: mean daily number of contacts that an indiv in age group b has with an indiv in age group a
    - n_indivs_a: number of individuals in age group a
    - count_df: dataframe describing number of asymptomatic and symptomatically infected indivs in age group
    - infec_asymp: [constant] infectiousness of asymptomatic infected indiv, relative to symptomatic infectd individual
    """

    def __init__(self):
        """Initialise InfectionForce class.
        Parameters:
            lambda_list (list): the force of infection for each age group 1-16
        """
        self.lambda_list = []

    def calc_z(self, a, b):
        """Accesses the counts of infected people and calculates what we define as z, the sum.
        z = [contactmatrix_ab/n of indiv in a] * [n of infected indiv in b +
                                                  (p(being asymptomatically infected) * asymptomatic indiv in b)]
        Parameters:
            a (int): fixed age group for which lambda will be calculated
            b (int): the other age group to which contact is compared.
        """
        M_ab = params.contactmatrix[a][b]
        N_a = params.n_indivs_a[a]
        I_b = infectioncount.count_df.loc[b, 'symptomatic']
        p = params.infec_asymp
        A_b = infectioncount.count_df.loc[b, 'asymptomatic']
        z = (M_ab / N_a) * (I_b + (p * A_b))
        return z

    def calc_lambda(self, infec_rate_param, a):
        """Calculates lambda for age group a from the obtained value of calc_z().
        lambda_a = infect_rate_param_a * sum over b age groups 1-16 {z}
        Parameters:
            infec_rate_param (list): the infection rate parameter, beta
            a (int): fixed age group for which lambda will be calculated
        """
        sum_z = 0  # holds the sum of z
        test_n = 0  # for testing purposes
        for b in range(len(params.age_groups)):  # loop to sum z
            sub_z = self.calc_z(a, b=b)
            sum_z += sub_z  # sum individual z to overall z
            test_n += 1
        lambda_a = float(infec_rate_param[a] * sum_z)  # must be float instead of npfloat64
        return lambda_a, test_n

    def all_lambda(self, infec_rate_param=params.infec_rate_param):
        """Calculates lambda for each age group a, and holds them in a list."""
        for a in range(len(params.age_groups)):
            lambda_a, test_n = self.calc_lambda(infec_rate_param, a)
            self.lambda_list.append(lambda_a)
