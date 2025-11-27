# File for parameters
import numpy as np
import pandas as pd
import scipy.stats as stats

class Params:
    """Class containing all the general information."""
    def __init__ (self):
        self.age_groups = ['0-4', '5-9', '10-14', '15-19',
                           '20-24', '25-29', '30-34', '35-39',
                           '40-44', '45-49', '50-54', '55-59',
                           '60-64', '65-69', '70-74', '75+']
        self.n_indivs_a = [5758, 6112, 5849, 5413,
                           6011, 6698, 6828, 6691,
                           6424, 6311, 6889, 6696,
                           5769, 5015, 5021, 8515]
        self.p_v_symp_a = [0.068, 0.015, 0.021, 0.026,
                           0.067, 0.098, 0.104, 0.094,
                           0.101, 0.125, 0.193, 0.261,
                           0.293, 0.539, 0.633, 0.678]
        self.contactmatrix = pd.read_csv('UK_Contacts_1.csv')
        self.infec_asymp = 0.255
        self.mean_infec = 9
        self.mean_latent = 5
        self.mean_hosp = 7.75
        self.mean_death = 10
        self.sd_hosp = 5.57
        self.sd_death = 12.1
        self.infec_rate_param = [0.186, 0.108, 0.122, 0.131,
                                 0.185, 0.213, 0.217, 0.210,
                                 0.215, 0.233, 0.272, 0.305,
                                 0.318, 0.397, 0.422, 0.430]
        #contactmatrix = #placeholder
        self.n_indivs_a = [5758, 6112, 5849, 5413,
                           6011, 6698, 6828, 6691,
                           6424, 6311, 6889, 6696,
                           5769, 5015, 5021, 8515]
        self.n_infec_sympt = 0
        self.n_infec_asympt = 0
        self.shape_param = 0.25
        self.n50_ag_infec = 0.091
        self.n50_ag_hd = 0.021
        self.decay_switch = 75
        self.decay_fast = -np.log(2)/35
        self.decay_slow = -np.log(2)/1000
        self.n0_exvacc = 0.22
        self.n0_newvacc = 0.44
        self.n0_infec = 0.66
        self.p_nv_IH = [0.011, 0.011, 0.006, 0.005,
                        0.004, 0.003, 0.004, 0.006,
                        0.008, 0.011, 0.011, 0.01,
                        0.014, 0.016, 0.016, 0.017]
        self.p_nv_HD = [0.001, 0.001, 0.014, 0.008,
                        0.009, 0.019, 0.017, 0.019,
                        0.028, 0.031, 0.047, 0.085,
                        0.146, 0.137, 0.246, 0.445]

    def initial_distribution(self, param):
        """Return a single random sample for the requested param string."""

        # latent period (gamma)
        if param == "latent_t":
            shape_dist = 3.0
            scale_dist = self.mean_latent / shape_dist
            return float(np.random.gamma(shape_dist, scale_dist))

        # infectious period (gamma)
        elif param == "infec_t":
            shape_dist = 3.0
            scale_dist = self.mean_infec / shape_dist
            return float(np.random.gamma(shape_dist, scale_dist))

        # delay between infectiousness and hospitalisation (Weibull)
        elif param == "hosp_t":
            k = 1.4
            lam = 8.4
            return float(np.random.weibull(k) * lam)

        # delay between hospitalisation and death (gamma)
        elif param == "death_t":
            # gamma params from mean and sd:
            # shape = (mean / sd) ** 2
            # scale = (sd ** 2) / mean
            shape_dist = (self.mean_death / self.sd_death) ** 2
            scale_dist = (self.sd_death ** 2) / self.mean_death
            return float(np.random.gamma(shape_dist, scale_dist))

        else:
            raise ValueError(f"Unknown param '{param}'")


if __name__ == "__main__":

    params = Params()
    # Check the output
    print("latent_t sample:", params.initial_distribution("latent_t"))
    print("infec_t sample:", params.initial_distribution("infec_t"))
    print("death_t sample:", params.initial_distribution("death_t"))
    print("hosp_t  sample:", params.initial_distribution("hosp_t"))
    
