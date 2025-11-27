# File for parameters
# Initiate distribution of parameters
import numpy as np
import pandas as pd
import os


class Params:

    class __Params:
        """Class containing all the general information."""
        file_root = os.path.dirname(os.path.dirname(__file__))
        contactmatrix = pd.read_csv(f'{file_root}/classes/UK_Contacts_1.csv', header=None)
        age_groups = ['0-4', '5-9', '10-14', '15-19',
                      '20-24', '25-29', '30-34', '35-39',
                      '40-44', '45-49', '50-54', '55-59',
                      '60-64', '65-69', '70-74', '75+']
        n_indivs_a = [5758, 6112, 5849, 5413,
                      6011, 6698, 6828, 6691,
                      6424, 6311, 6889, 6696,
                      5769, 5015, 5021, 8515]
        p_v_symp_a = [0.068, 0.015, 0.021, 0.026,
                      0.067, 0.098, 0.104, 0.094,
                      0.101, 0.125, 0.193, 0.261,
                      0.293, 0.539, 0.633, 0.678]
        infec_asymp = 0.255
        mean_infec = 9
        mean_latent = 5
        mean_hosp = 7.75
        mean_death = 10
        sd_hosp = 5.57
        sd_death = 12.1
        infec_rate_param = [0.186, 0.108, 0.122, 0.131,
                            0.185, 0.213, 0.217, 0.210,
                            0.215, 0.233, 0.272, 0.305,
                            0.318, 0.397, 0.422, 0.430]
        #contactmatrix = #placeholder
        n_indivs_a = [5758, 6112, 5849, 5413,
                      6011, 6698, 6828, 6691,
                      6424, 6311, 6889, 6696,
                      5769, 5015, 5021, 8515]
        n_infec_sympt = 0
        n_infec_asympt = 0
        shape_param = 0.25
        n50_ag_infec = 0.091
        n50_ag_hd = 0.021
        decay_switch = 75
        decay_fast = -np.log(2) / 35
        decay_slow = -np.log(2) / 1000
        n0_exvacc = 0.22
        n0_newvacc = 0.44
        n0_infec = 0.66
        p_nv_IH = [0.011, 0.011, 0.006, 0.005,
                   0.004, 0.003, 0.004, 0.006,
                   0.008, 0.011, 0.011, 0.01,
                   0.014, 0.016, 0.016, 0.017]
        p_nv_HD = [0.001, 0.001, 0.014, 0.008,
                   0.009, 0.019, 0.017, 0.019,
                   0.028, 0.031, 0.047, 0.085,
                   0.146, 0.137, 0.246, 0.445]

        # latent period (gamma)
        shape_dist = 3.0
        scale_dist_latent_t = mean_latent / shape_dist
        latent_t = float(np.random.gamma(shape_dist, scale_dist_latent_t))

        # infectious period (gamma)
        scale_dist_infec_t = mean_infec / shape_dist
        infec_t = float(np.random.gamma(shape_dist, scale_dist_infec_t))

        # delay between infectiousness and hospitalisation (Weibull)
        k = 1.4
        lam = 8.4
        hosp_t = float(np.random.weibull(k) * lam)

        # delay between hospitalisation and death (gamma)
        shape_dist_death_t = (mean_death / sd_death) ** 2
        scale_dist_death_t = (sd_death ** 2) / mean_death
        death_t = float(np.random.gamma(shape_dist_death_t, scale_dist_death_t))

    _instance = __Params

    def __init__(self):
        """Virutal private constructor to enforce singleton pattern."""
        if Params._instance is not None:
            raise RuntimeError("This class is a singleton!")

    @staticmethod
    def instance():
        """Creates singleton instance of __Parameters under
        _instance if one doesn't already exist.

        Returns
        -------
        __Parameters
            An instance of the __Parameters class

        """
        if not Params._instance:
            raise RuntimeError("Config file hasn't been set")
        return Params._instance
