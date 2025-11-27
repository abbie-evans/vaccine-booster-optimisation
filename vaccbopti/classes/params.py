# File for parameters
import math
import numpy as np
import mpmath as mp


class params:
    """Class containing all the general information."""

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
    infec_rate_param = [0.186, 0.108, 0.122, 0.131,
                        0.185, 0.213, 0.217, 0.210,
                        0.215, 0.233, 0.272, 0.305,
                        0.318, 0.397, 0.422, 0.430]
    #contactmatrix =  # placeholder
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
    decay_fast = -math.log(2) / 35
    decay_slow = -math.log(2) / 1000
    n0_exvacc = 0.22
    n0_newvacc = 0.44
    n0_infec = 0.66
    mean_latent = 5
    p_nv_IH = [0.011, 0.011, 0.006, 0.005,
               0.004, 0.003, 0.004, 0.006,
               0.008, 0.011, 0.011, 0.01,
               0.014, 0.016, 0.016, 0.017]
    p_nv_HD = [0.001, 0.001, 0.014, 0.008,
               0.009, 0.019, 0.017, 0.019,
               0.028, 0.031, 0.047, 0.085,
               0.146, 0.137, 0.246, 0.445]

    # initiate distribution for different parameters
    def initial_distribution(param):
        if param == "latent_t":
            shape_dist = 3
            scale_dist = mean_latent / shape_dist
            sample_latent_t = np.random.gamma(shape_dist, scale_dist)

            return sample_latent_t

        elif param == "infec_t":
            shape_dist = 3
            scale_dist = mean_infec / shape_dist
            sample_infec_t = np.random.gamma(shape_dist, scale_dist)

            return sample_infec_t

        elif param == "hosp_t":
            def weibull_from_mean_sd(mean, sd):
                R = sd / mean

                # equation to solve for root that gives the shape k
                def equation(k):
                    return mp.sqrt(mp.gamma(1 + 2 / k) / mp.gamma(1 + 1 / k) ** 2 - 1) - R

                # solve for k (shape)
                k = mp.findroot(equation, 1.5)  # 1.5 is a reasonable initial guess

                # scale
                lam = mean / mp.gamma(1 + 1 / k)

                return float(k), float(lam)

            k, lam = weibull_from_mean_sd(mean, sd)

        #elif param == "death_t":
            #shape_dist: (mean_t_D: float / sd_t_D: float) ^ 2(float)
            #scale_dist: (sd_t_D ^ 2: float / mean_t_D: float)(float)
            sample_infec_t = np.random.gamma(shape_dist, scale_dist)
            #return sample_death_t

            weibull_from_mean_sd()

            + shape_t_H, scale_t_H: weibull_from_mean_sd(mean_t_H, sd_t_H)(float)
            + shape_t_D: (mean_t_D: float / sd_t_D: float) ^ 2(float)
            + scale_t_D: (sd_t_D ^ 2: float / mean_t_D: float)(float)
            + dist_t_H: Weibull(shape_t_H: float, scale_t_H: float)
            + dist_t_D: Gamma(shape_t_D: float, scale_t_D: float)
            + dist_t_L: Gamma(shape(int=3), scale: mean / (int =3))
            + dist_t_I: Gamma(shape(int=3), scale: mean / (int =3))

            + latent_t: array
            + infec_t: array
            + hosp_t: array
            + death_t: array
