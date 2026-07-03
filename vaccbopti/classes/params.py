# FILE CONTAINING ALL THE RELEVANT INFORMATION TO INITIALISE AT THE START OF THE MODEL.

# Important and useful modules
import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import scipy.integrate as integrate
from scipy.stats import weibull_min


# Define Params class
class Params:

    class __Params:
        """Inner singleton class containing all the general information."""

        def __init__(self):
            """Initialises all of the parameters to be accessed by other functions and model."""
            self.project_root = os.path.dirname(os.path.dirname(__file__))
            self.contactmatrix = pd.read_csv(f'{self.project_root}/classes/UK_Contacts.csv', header=None)
            self.age_groups = ['0-4', '5-9', '10-14', '15-19',  # age groups set up
                               '20-24', '25-29', '30-34', '35-39',
                               '40-44', '45-49', '50-54', '55-59',
                               '60-64', '65-69', '70-74', '75+']
            self.old_groups = self.age_groups[7:]
            self.young_groups = self.age_groups[:7]
            self.prop_indivs_a = [0.05758, 0.06112, 0.05849, 0.05413,  # prop of indiv in agegroups
                                  0.06011, 0.06698, 0.06828, 0.06691,
                                  0.06424, 0.06311, 0.06889, 0.06696,
                                  0.05769, 0.05015, 0.05021, 0.08515]
            self.p_v_symp_a = [0.068, 0.015, 0.021, 0.026,  # probability of developing symptoms d(a)
                               0.067, 0.098, 0.104, 0.094,
                               0.101, 0.125, 0.193, 0.261,
                               0.293, 0.539, 0.633, 0.678]
            self.infec_rate_param = [0.186, 0.108, 0.122, 0.131,  # infection rate beta(a)
                                     0.185, 0.213, 0.217, 0.210,
                                     0.215, 0.233, 0.272, 0.305,
                                     0.318, 0.397, 0.422, 0.430]
            self.infec_asymp = 0.255  # infectiousness of an asymptomatic relative to symptomatic
            self.shape_param = 2.5  # shape parameter linking immunity to infection level
            self.n50_ag_infec = 0.091  # 50% immunity level against infection n50_1
            self.n50_ag_hd = 0.021  # 50% immunity level against hospitalistion/death n50_2
            self.decay_switch = 75  # switch slow and fast decays (days)
            self.decay_fast = -np.log(2) / 35  # fast antibody decay
            self.decay_slow = -np.log(2) / 1000  # slow antibody decay
            self.n0_exvacc = 0.22  # max immune recognition following existing vaccination
            self.n0_newvacc = 0.44  # max immune recognition following new vaccination
            self.n0_infec = 0.66  # max immunie recognition following infection
            self.mean_latent = 5  # mean latent period (days)
            self.mean_infec = 9  # mean infectious period (days)
            self.p_nv_IH = [0.011, 0.011, 0.006, 0.005,  # probability they are hospitalised
                            0.004, 0.003, 0.004, 0.006,
                            0.008, 0.011, 0.011, 0.01,
                            0.014, 0.016, 0.016, 0.017]
            self.mean_hosp = 7.75  # mean hospitalisation time (days)
            self.sd_hosp = 5.57  # s.d. of hospitalisation time (days)
            self.p_nv_HD = [0.001, 0.001, 0.014, 0.008,  # probability of death
                            0.009, 0.019, 0.017, 0.019,
                            0.028, 0.031, 0.047, 0.085,
                            0.146, 0.137, 0.246, 0.445]
            self.mean_death = 10  # mean death time (days)
            self.sd_death = 12.1  # s.d. of death time (days)
            self.days_samples = np.array(range(1, 1001))  # number of samples for days of periods

            """Shape and scale parameters for gamma and weibull distribution for periods."""
            self.shape = 3.0
            self.scale_latent_t = self.mean_latent / self.shape
            self.scale_infec_t = self.mean_infec / self.shape
            self.shape_death_t = (self.mean_death / self.sd_death) ** 2
            self.scale_death_t = (self.sd_death**2) / self.mean_death
            self.k = 1.4
            self.lam = 8.4

            """Producing arrays from which the latent, infectious, hospitalisation, and time to deaths are sampled."""
            self.latent_t = self.integral_probabilities_array("gamma",
                                                              [self.shape, self.scale_latent_t])
            self.infec_t = self.integral_probabilities_array("gamma",
                                                             [self.shape, self.scale_infec_t])
            self.hosp_t = self.integral_probabilities_array("weibull",
                                                            [self.k, self.lam])
            self.death_t = self.integral_probabilities_array("gamma",
                                                             [self.shape_death_t, self.scale_death_t])

            """Tau curves to access under each condition"""
            self.f_exvacc = self.calc_fx(self.n0_exvacc, self.n50_ag_infec)
            self.f_newvacc = self.calc_fx(self.n0_newvacc, self.n50_ag_infec)
            self.f_infec = self.calc_fx(self.n0_infec, self.n50_ag_infec)
            self.f_exvacc_hosp = self.calc_fx(self.n0_exvacc, self.n50_ag_hd)
            self.f_newvacc_hosp = self.calc_fx(self.n0_newvacc, self.n50_ag_hd)
            self.f_infec_hosp = self.calc_fx(self.n0_infec, self.n50_ag_hd)

        def integration(self, k, dist, parameters):
            "Define the integration function"
            integrand_gamma = lambda u: (1 - abs(u - k)) * stats.gamma.pdf(u, parameters[0], parameters[1])
            integrand_weibull = lambda u: (1 - abs(u - k)) * weibull_min.pdf(u, parameters[0], scale=parameters[1])
            if dist == "gamma":
                return integrate.quad(integrand_gamma, k - 1, k + 1)
            else:
                return integrate.quad(integrand_weibull, k - 1, k + 1)

        def integral_of_density_probability(self, dist, parameters):
            """Run for each k in values (one Lk)"""
            prob = []
            for k in self.days_samples[1:]:
                result = self.integration(k, dist, parameters)
                prob.append(result[0])
            return prob

        def integral_probabilities_array(self, dist, parameters):
            """Ensure that the probabilities sum to 1"""
            lk1 = 1 - sum(self.integral_of_density_probability(dist, parameters))
            # final array for the probabilities of each Lk
            lk = [lk1] + self.integral_of_density_probability(dist, parameters)
            return lk

        def calc_fx(self, n0_x, n50_m):
            """Method to calculate the tau_x curves.
            Parameters:
                n0_x (float): which method is conferring resistance
                n50_m (float): deciding on immunity level conferred by infection or hospitalisation
            Returns:
                f_x: tau_x curves to be indexed
            """
            exp_val = (- self.shape_param
                       * np.log10(self.calc_nx(n0_x))
                       - np.log10(n50_m))  # susceptibility M=1 or hospitalisation M=2
            f_x = 1 / (1 + np.exp(exp_val))
            return f_x

        def calc_nx(self, n0_x):
            """Calculating n_x, the immunity levels modelled using a biphasic exponential decay function.
            Parameters:
                n0_x (float): which method is conferring resistance
                                - vaccination with existing vaccine
                                - vaccination with variant adapted vaccine
                                - infection with new strain
            Returns:
                n_x: immunity levels as the exponential decay
            """
            tau_x = np.linspace(0, 5000, 5000 + 1)
            num_exp1 = self.decay_fast * tau_x + self.decay_slow * self.decay_switch
            num_exp2 = self.decay_slow * tau_x + self.decay_fast * self.decay_switch
            numerator = np.exp(num_exp1) + np.exp(num_exp2)
            dem_exp1 = np.exp(self.decay_fast * self.decay_switch)
            dem_exp2 = np.exp(self.decay_slow * self.decay_switch)
            denominator = dem_exp1 + dem_exp2
            n_x = n0_x * (numerator / denominator)
            return n_x

    _instance = None

    def __init__(self):
        """Virtual private constructor to enforce singleton pattern."""
        raise RuntimeError("This class is a singleton!")

    @staticmethod
    def instance():
        """Creates a singleton instance of __Parameters under _instance to access variables.
        Returns:
            __Params._instance: an instance of the __Parameters class to access all variables
        """
        if not Params._instance:
            Params._instance = Params.__Params()
        return Params._instance
