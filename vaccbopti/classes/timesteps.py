# FILE FOR TIMESTEPS CLASS

# Import other modules
import numpy as np
import random
import itertools
import pandas as pd
from .person import Person
from .params import Params
from .booster_admin import BoosterAdmin
params = Params.instance()
boosters = BoosterAdmin()


# Define Timesteps class
class Timesteps:
    """A class representing the steps in the simulation."""

    def __init__(self, num_people, sim_length=365, R_e=1.5):
        """Initialise the Timesteps object.
        Inputs:
            num_people (int): the total number of people involved in the simulation
            sim_length (int): the total length of time in the simulation
            R_e (float): effective reproduction number/transmissibility of the novel variant
        Parameters:
            indices (list): all the indices for all people
            People (array): all the people in the simulation
            IDs (array): all the IDs of each of the people
            rho_age_groups (list): the indices for the ranges of people in each age group
            statusDF (pd.DataFrame): will contain the values of each of the statuses for each group at each timepoint
        """
        self.sim_length = sim_length
        self.R_e = R_e
        self.num_people = num_people
        self.indices = list(np.linspace(0, num_people - 1, num_people))
        self.People = np.array([Person() for p in range(num_people)])
        self.IDs = np.array([p.id for p in self.People])
        rho_age_groups = np.array(params.prop_indivs_a) * num_people
        rho_age_groups = [int(round(n)) for n in rho_age_groups[0:-1]]
        rho_age_groups = np.cumsum([0] + rho_age_groups)
        self.rho_age_groups = np.append(rho_age_groups, num_people)
        # Create output dataframes
        timepoints = list(range(0, self.sim_length))
        vaccine = ['unvaccinated', 'vaccinated']
        df_status = ['symptomatic', 'asymptomatic', 'hospitalised', 'dead']
        index = list(itertools.product(*[timepoints, params.age_groups, vaccine]))
        index = pd.MultiIndex.from_tuples(index, names=["t", "ages", "vacc_status"])
        self.statusDF = pd.DataFrame(0, index=index, columns=df_status)

    def initialise_people(self, n_infec):
        """Ensure people have all information necessary after initialisation:
           - assigned age groups,
           - have been infected/vaccinated with a previous variant at some point
           - random subset are infected
           - random subset are ineligible for vaccination
           - updates their susceptibility based on these infection times
        Parameters:
            rho_age_groups (list): number of people in each age group
            n_infec (int): number of people to be randomly infected
            """
        # Assign age groups
        for n in range(len(self.rho_age_groups) - 1):
            for p in range(self.rho_age_groups[n], self.rho_age_groups[n + 1]):
                self.People[p].get_age_group(n)
                self.People[p].immunity_time_exvacc = np.random.choice(365 * 2 + 1)
        # Ineligible for booster group
        inelig_group = random.sample(self.indices, int(round(0.2 * self.num_people)))
        for p in inelig_group:
            self.People[int(p)].vacc_status = 'ineligible'
        # Randomly infected group
        infect_group = random.sample(self.indices, n_infec)
        for p in infect_group:
            self.People[int(p)].initialise_infection()

    def get_p_exposed(self, force_infection):
        """Gets the probability that a person is exposed.
        Parameters:
            force_infection (float): the force of infection calcuated"""
        for n in range(len(self.rho_age_groups) - 1):
            for p in range(self.rho_age_groups[n], self.rho_age_groups[n + 1]):
                self.People[p].calc_susceptibility()
                self.People[p].calc_prob_exposed(force_infection[n])

    def calculate_average_susceptibility(self):
        """Calculate the average of the susceptibility for each person."""
        susceptibility_sum = 0
        for p in self.People:
            susceptibility_sum += p.susceptibility
        average_susceptibility = susceptibility_sum / self.num_people
        return average_susceptibility

    def calculate_new_beta(self):
        """Calcuates a new beta, the infection rate parameter based on R_e (changes based on sim time)."""
        R_a_b = np.zeros(params.contactmatrix.shape)
        for a in range(len(params.contactmatrix)):
            for b in range(len(params.contactmatrix)):
                R_a_b[a][b] = ((params.p_v_symp_a[a] + params.infec_asymp * (1 - params.p_v_symp_a[a]))
                               * (1 / params.mean_infec * self.calculate_average_susceptibility()
                               * params.infec_rate_param[a] * params.contactmatrix[a][b]))
        calc_R_e = np.linalg.eigvals(R_a_b)
        calc_R_e = float(np.array([n.real for n in calc_R_e if n.imag == 0]).max())
        if calc_R_e == 0:
            calc_R_e = 1e-12  # to avoid a divide by 0 error
        new_beta_factor = self.R_e / calc_R_e
        new_beta = new_beta_factor * np.array(params.infec_rate_param)
        return new_beta.tolist()

    def administer_booster(self, vacc_strat, t_newvacc_avail, t, vacc_amount=2000):
        """Administers the booster based on the strategy inputted by the user.
        - strategy 0: doesn't apply booster vaccines
        - strategy 1: vaccinates everyone starting at the oldest age group and descending,
                      not taking into account the availability of the updated vaccine
        - strategy 2: vaccinates everyone starting at the oldest age group and descending,
                      when the updated vaccine becomes available
        - strategy 3: starts vaccinating with the old vaccine from the oldest age groups (from 75+ down),
                      until the new vaccine becomes available. Then, the new vaccine starting at the middle
                      groups is prioritised (from 49 down). When all the updated vaccines have been administered,
                      the old vaccination is continued in the older age groups.
        - strategy 4: starts vaccinating with the old vaccine to the youngest age groups (0+ up), and switches to
                      vaccinating from the middle age groups up (50+ and up) until all have been vaccinated with the
                      updated vaccine. It then switches back to vaccinating the remaining individuals in the young
                      age groups with the old vaccine.
        - strategy 5: the old vaccine is administered randomnly to anyone within the population
        - strategy 6: updated vaccine administered randomnly to anyone within population when it becomes available
        Parameteters:
            vacc_strat (int): which number vaccine strategy we're using"""
        if vacc_strat == 0:
            return
        if vacc_strat == 1:
            boosters.vacc_strat_1(self.People, vacc_amount)
        if vacc_strat == 2:
            boosters.vacc_strat_2(self.People, vacc_amount, t, t_newvacc_avail)
        if vacc_strat == 3:
            boosters.vacc_strat_3(self.People, vacc_amount, t, t_newvacc_avail)
        if vacc_strat == 4:
            boosters.vacc_strat_4(self.People, vacc_amount, t, t_newvacc_avail)
        if vacc_strat == 5:
            boosters.vacc_strat_5(self.People, vacc_amount)
        if vacc_strat == 6:
            boosters.vacc_strat_6(self.People, vacc_amount, t, t_newvacc_avail)

    def increment_people(self, infectioncount):
        """Increases immunity times by 1 and changes status.
        Parameters:
            infectioncount (pd.DataFrame): the dataframe containing the day's data"""
        for p in self.People:
            p.change_status(infectioncount)
            p.increment_immunity_time()

    def append_daily_nbs_outputdf(self, t, infectioncount):
        """Adds the daily data to the overall dataframe.
        Parameters:
            t (int): the timestep of the simulation
            infectioncount (pd.DataFrame): the dataframe containing the day's data"""
        if (self.statusDF.loc[t].index == infectioncount.index).all():
            self.statusDF.loc[t] = infectioncount.to_numpy()
        else:
            raise IndexError("The index of overall table and daily table don't match - values will not line up.")
