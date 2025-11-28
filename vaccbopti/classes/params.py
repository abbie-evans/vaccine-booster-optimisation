# FILE CONTAINING ALL THE RELEVANT INFORMATION TO INITIALISE AT THE START OF THE MODEL.

# Important and useful modules
import numpy as np
import pandas as pd
import os


# Define Params class
class Params:

    class __Params:
        """Inner singleton class containing all the general information."""

        def __init__(self):
            """Initialises all of the parameters to be accessed by other functions and model."""
            self.project_root = os.path.dirname(os.path.dirname(__file__))
            self.contactmatrix = pd.read_csv(f'{self.project_root}/classes/UK_Contacts.csv', header=None)
            self.age_groups = np.array(['0-4', '5-9', '10-14', '15-19',  # age groups set up
                                        '20-24', '25-29', '30-34', '35-39',
                                        '40-44', '45-49', '50-54', '55-59',
                                        '60-64', '65-69', '70-74', '75+'])
            self.n_indivs_a = [5758, 6112, 5849, 5413,  # number in each age group N(a)
                               6011, 6698, 6828, 6691,
                               6424, 6311, 6889, 6696,
                               5769, 5015, 5021, 8515]
            self.p_v_symp_a = [0.068, 0.015, 0.021, 0.026,  # probability of developing symptoms d(a)
                               0.067, 0.098, 0.104, 0.094,
                               0.101, 0.125, 0.193, 0.261,
                               0.293, 0.539, 0.633, 0.678]
            self.infec_rate_param = [0.186, 0.108, 0.122, 0.131,  # infection rate beta(a)
                                     0.185, 0.213, 0.217, 0.210,
                                     0.215, 0.233, 0.272, 0.305,
                                     0.318, 0.397, 0.422, 0.430]
            self.infec_asymp = 0.255  # infectiousness of an asymptomatic relative to symptomatic
            self.shape_param = 0.25  # shape parameter linking immunity to infection level
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

            # latent period (gamma)
            self.shape_dist = 3.0
            self.scale_dist_latent_t = self.mean_latent / self.shape_dist
            self.latent_t = float(np.random.gamma(self.shape_dist, self.scale_dist_latent_t))

            # infectious period (gamma)
            self.scale_dist_infec_t = self.mean_infec / self.shape_dist
            self.infec_t = float(np.random.gamma(self.shape_dist, self.scale_dist_infec_t))

            # delay between infectiousness and hospitalisation (Weibull)
            self.k = 1.4
            self.lam = 8.4
            self.hosp_t = float(np.random.weibull(self.k) * self.lam)

            # delay between hospitalisation and death (gamma)
            self.shape_dist_death_t = (self.mean_death / self.sd_death) ** 2
            self.scale_dist_death_t = (self.sd_death**2) / self.mean_death
            self.death_t = float(np.random.gamma(self.shape_dist_death_t, self.scale_dist_death_t))

            # tau curves to access under each condition
            self.f_exvacc = self.calc_fx(self.n0_exvacc, self.n50_ag_infec)
            self.f_newvacc = self.calc_fx(self.n0_newvacc, self.n50_ag_infec)
            self.f_infec = self.calc_fx(self.n0_infec, self.n50_ag_infec)

        def calc_fx(self, n0_x, n50_m):
            """Method to calculate the tau_x curves.
            Parameters:
                n0_x (float): which method is conffering resistance
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
                n0_x (float): which method is conffering resistance
                                - vaccination with existing vaccine
                                - vaccination with variant adapted vaccine
                                - infection with new strain
            Returns:
                n_x: immunity levels as the exponential decay
            """
            tau_x = np.linspace(0, 365 * 2, 365 * 2 + 1)
            num_exp1 = self.decay_fast * tau_x + self.decay_slow * self.decay_switch
            num_exp2 = self.decay_slow * tau_x + self.decay_fast * self.decay_switch
            numerator = np.exp(num_exp1) + np.exp(num_exp2)
            dem_exp1 = np.exp(self.decay_fast * self.decay_switch)
            dem_exp2 = np.exp(self.decay_slow * self.decay_switch)
            denominator = dem_exp1 + dem_exp2
            n_x = n0_x * (numerator / denominator)
            return n_x

    _instance = __Params

    def __init__(self):
        """Virtual private constructor to enforce singleton pattern."""
        raise RuntimeError("This class is a singleton!")

    @staticmethod
    def instance():
        """Creates singleton instance of __Parameters under _instance to access variables.
        Returns:
            __Params._instance(): an instance of the __Parameters class to access all variables
        """
        if not Params._instance():
            raise RuntimeError("Error in configs.")
        return Params._instance()
