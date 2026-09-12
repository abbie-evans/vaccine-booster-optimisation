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
        
        Parameters
        ----------
        num_people : int
            The total number of people involved in the simulation
        sim_length : int
            The total length of time in the simulation
        R_e : float
            Effective reproduction number/transmissibility of the novel variant
        """
        self.sim_length = sim_length
        self.R_e = R_e
        self.num_people = num_people
        self.indices = list(np.linspace(0, num_people - 1, num_people))
        self.people = np.array([Person() for p in range(num_people)])
        self.IDs = np.array([p.id for p in self.people])
        rho_age_groups = np.array(params.prop_indivs_a) * num_people
        rho_age_groups = [int(round(n)) for n in rho_age_groups[0:-1]]
        rho_age_groups = np.cumsum([0] + rho_age_groups)
        self.rho_age_groups = np.append(rho_age_groups, num_people)
        # Create output dataframes
        timepoints = list(range(0, self.sim_length))
        vaccine = ['unvaccinated', 'ex_vaccine', 'new_vaccine']
        df_status = ['symptomatic', 'asymptomatic', 'hospitalised', 'dead']
        index = list(itertools.product(*[timepoints, params.age_groups, vaccine]))
        index = pd.MultiIndex.from_tuples(index, names=["t", "ages", "vacc_status"])
        self.statusDF = pd.DataFrame(0, index=index, columns=df_status)

    def initialise_people(self, n_infec, prop_ineligible=0.2):
        """Ensure people have all information necessary after initialisation.

        This includes:
        - Assigning age groups.
        - Determining when people have previously been infected or
          vaccinated with a previous variant.
        - Infecting a random subset of people.
        - Making a random subset of people ineligible for vaccination.
        - Updating susceptibility based on previous infection times.
        
        Parameters
        ----------
        n_infec : int
            Number of people to be randomly infected
        prop_ineligible : float
            Proportion of overall population that will not receive the vaccine
            """
        # Assign age groups
        for n in range(len(self.rho_age_groups) - 1):
            for p in range(self.rho_age_groups[n], self.rho_age_groups[n + 1]):
                self.people[p].set_age_group(n)
                self.people[p].immunity_time_exvacc = np.random.choice(365 * 2 + 1)
        # Ineligible for booster group
        inelig_group = random.sample(self.indices, int(round(prop_ineligible * self.num_people)))
        for p in inelig_group:
            self.people[int(p)].vacc_status = 'ineligible'
        # Randomly infected group
        infect_group = random.sample(self.indices, n_infec)
        for p in infect_group:
            self.people[int(p)].initialise_infection()

    def set_p_exposed(self, force_infection):
        """Gets the probability that a person is exposed.
        
        Parameters
        ----------
        force_infection : float
            The force of infection calcuated"""
        for n in range(len(self.rho_age_groups) - 1):
            for p in range(self.rho_age_groups[n], self.rho_age_groups[n + 1]):
                self.people[p].calc_susceptibility()
                self.people[p].calc_prob_exposed(force_infection[n])

    def calculate_average_susceptibility(self, a):
        """Calculate the average susceptibility of the population in age group a.
        
        Parameters
        ----------
        a : int
            The index of the age group to calculate susceptibility for."""
        susceptibility_sum = 0
        susceptibility_pop = [p for p in self.people if p.age_group_index == a]
        for p in susceptibility_pop:
            susceptibility_sum += p.susceptibility
        average_susceptibility = susceptibility_sum / self.num_people
        return average_susceptibility

    def calculate_new_beta(self):
        """Calculates a new beta, the infection rate parameter based on R_e (changes based on sim time)."""
        R_a_b = np.zeros(params.contact_matrix.shape)
        for a in range(len(params.contact_matrix)):
            for b in range(len(params.contact_matrix)):
                R_a_b[a][b] = ((params.p_v_symp_a[b] + params.infec_asymp * (1 - params.p_v_symp_a[b]))
                               * (params.mean_infec * self.calculate_average_susceptibility(a)
                               * params.infec_rate_params[a] * params.contact_matrix[a][b]))
        eigenvalues = np.linalg.eigvals(R_a_b)
        calc_R_e = np.real(max(eigenvalues))
        if calc_R_e == 0:
            calc_R_e = 1e-12  # to avoid a divide by 0 error
        new_beta_factor = self.R_e / calc_R_e
        new_beta = new_beta_factor * np.array(params.infec_rate_params)
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
        - strategy 5: the old vaccine is administered randomly to anyone within the population
        - strategy 6: updated vaccine administered randomly to anyone within the population when it becomes available
        
        Parameters
        ----------
        vacc_strat : int
            Which numbered vaccine strategy is being used"""
        if vacc_strat == 0:
            return
        if vacc_strat == 1:
            boosters.vacc_strat_1(self.people, vacc_amount)
        if vacc_strat == 2:
            boosters.vacc_strat_2(self.people, vacc_amount, t, t_newvacc_avail)
        if vacc_strat == 3:
            boosters.vacc_strat_3(self.people, vacc_amount, t, t_newvacc_avail)
        if vacc_strat == 4:
            boosters.vacc_strat_4(self.people, vacc_amount, t, t_newvacc_avail)
        if vacc_strat == 5:
            boosters.vacc_strat_5(self.people, vacc_amount)
        if vacc_strat == 6:
            boosters.vacc_strat_6(self.people, vacc_amount, t, t_newvacc_avail)

    def update_people(self, total_infections, infections_each_day):
        """Increases immunity times by 1 and changes status.
        
        Parameters
        ----------
        total_infections : pd.DataFrame
            Keep track of how many people in each status for infection force
        infections_each_day : pd.DataFrame
            Identify who enters each status each day for final outputs"""
        for p in self.people:
            p.change_status(total_infections, infections_each_day)
            p.increment_immunity_time()

    def append_daily_nbs_outputdf(self, t, infections_each_day):
        """Adds the daily data to the overall dataframe.
        
        Parameters
        ----------
        t : int
            The timestep of the simulation
        infections_each_day : pd.DataFrame
            The dataframe containing the day's data"""
        if (self.statusDF.loc[t].index == infections_each_day.index).all():
            self.statusDF.loc[t] = infections_each_day.to_numpy()
        else:
            raise IndexError("The index of overall table and daily table don't match - values will not line up.")
