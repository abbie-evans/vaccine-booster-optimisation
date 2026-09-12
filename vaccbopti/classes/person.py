# FILE CONTAINING ALL THE RELEVANT INFORMATION AND FUNCTIONS FOR A PERSON IN THE SIMULATION.
# - contains parameters that need to be individually defined per person
# - function: to assign the age group of the person
# - function: calculates the probability a person's status changes from susceptible to exposed
# - function: calculates the relative susceptibility, v(t), of an individual
# - function: initialises people with infected status for the start of the simulation
# - function: decision tree to determine a person's status at each time step
# - function: determines if the person's status, based on probability
# - function: determines the number of days a person is in a status, dependent on the probabiltiy distribution

# Import useful modules
import numpy as np
import itertools
from .params import Params
params = Params.instance()


# Define Person class
class Person:
    """A class representing an individual in the simulation, each with unique ID."""
    id_iter = itertools.count()

    def __init__(self):
        """Initialise the Person object.
        Parameters:
            id (int): a unique ID for each person
            age_group (str): the age group the person belongs to (16 different classes, seen in parameter file)
            age_group_index (int): the index of the age group in the list of age groups
            status (str): person's status relative to the infection
                          susceptible, exposed, symptomatic, asymptomatic, hospitalised, dead
            vacc_status (str): person's vaccination status
                               unvacc, ex_vacc, new_vacc, ineligible
            vacc_status_t_i (str): the person's vaccine status at the time of infection
            susceptibility (float): susceptibility, v(t), of an individual
            prob_exposed (float): probability an individual will become infected
            latent_t_i (int): time left in the latent period once exposed
                              if -1, then the person is not currently in a latent period
            infect_t_i (int): time left in infectious period once infectious (symptomatic or asymptomatic)
                              if -1, then the person is not currently in an infectious period
            hosp_t_i (int): time spent in hospital
                            if -1, then the person is not currently in a hospital
            death_t_i (int): time at death from hospitalisation
                             if -1, then the person is not currently in the 'dead' status
            immunity_time_exvacc (int): time since given last vaccination/infection from previous variant
                                        if -1, then the person has not received a pre-existing vaccine
            immunity_time_newvacc (int): time since last variant-adapted vaccine
                                         if -1, then the person has not received a new vaccine
            immunity_time_infec (int): time since infection with novel variant
                                       if -1, then the person has not been infected
        """
        self.id = next(self.id_iter)
        self.age_group = None
        self.age_group_index = None
        self.status = 'susceptible'
        self.vacc_status = 'unvacc'
        self.vacc_status_t_i = 'unvacc'
        self.susceptibility = 0
        self.susceptibility_H = 0
        self.prob_exposed = 0.01
        self.latent_t_i = -1
        self.infect_t_i = -1
        self.hosp_t_i = -1
        self.death_t_i = -1
        self.immunity_time_exvacc = -1
        self.immunity_time_newvacc = -1
        self.immunity_time_infec = -1

    def set_age_group(self, n):
        """Assign individual a specific age-group.
        Parameters:
            n (int): index for a specific age group from array of age groups
        """
        self.age_group = str(params.age_groups[n])
        self.age_group_index = n

    def calc_susceptibility(self):
        """Calculates the relative susceptibility, v(t), of an individual.
        Returns:
            susceptibility (float): level of susceptibility is determined by their immune status
        """
        if self.immunity_time_exvacc == -1:
            immunity_exvacc = 0
            immunity_exvacc_H = 0
        else:
            immunity_exvacc = params.f_exvacc[self.immunity_time_exvacc]
            immunity_exvacc_H = params.f_exvacc_hosp[self.immunity_time_exvacc]
        if self.immunity_time_newvacc == -1:
            immunity_newvacc = 0
            immunity_newvacc_H = 0
        else:
            immunity_newvacc = params.f_newvacc[self.immunity_time_newvacc]
            immunity_newvacc_H = params.f_newvacc_hosp[self.immunity_time_exvacc]
        if self.immunity_time_infec == -1:
            immunity_infec = 0
            immunity_infec_H = 0
        else:
            immunity_infec = params.f_infec[self.immunity_time_infec]
            immunity_infec_H = params.f_infec_hosp[self.immunity_time_exvacc]
        susceptibility = 1 - max(immunity_exvacc,
                                 immunity_newvacc,
                                 immunity_infec)
        susceptibility_H = 1 - max(immunity_exvacc_H,
                                   immunity_newvacc_H,
                                   immunity_infec_H)
        self.susceptibility = susceptibility
        self.susceptibility_H = susceptibility_H / susceptibility

    def calc_prob_exposed(self, force_infection):
        """Calculates the probability a person's status changes from susceptible to exposed."""
        exp_val = np.exp(-self.susceptibility * force_infection)
        self.prob_exposed = 1 - exp_val

    def pick_distr_prob(self, distribution):
        """Determines the number of days a person is in a status, dependent on the probability distribution.
        Parameters:
            distribution (array): the probability distribution for different days
        Returns:
            days (int): the number of days a person is in a specific status
        """
        choices = list(range(1, len(distribution) + 1))
        days = np.random.choice(choices, p=distribution)
        return days

    def determine_status_change(self, statuses, probability):
        """Determines if the person's status will change, based on probability.
        Parameters:
            statuses (list): a list of the two possible statuses
            probability (float or list): a float of probability or list of probabilities per age group
        """
        if type(probability) is list:
            status = np.random.choice(statuses, size=1, p=[probability[self.age_group_index],
                                                           1 - probability[self.age_group_index]])
        else:
            status = np.random.choice(statuses, size=1, p=[probability, 1 - probability])
        self.status = str(status[0])

    def initialise_infection(self):
        """Initialises people with infected status for the start of the simulation."""
        self.status = 'exposed'
        self.immunity_time_infec = 0  # reset the immunity time counter for infection
        self.latent_t_i = self.pick_distr_prob(params.latent_t)  # gives them a latent time

    def increment_immunity_time(self):
        """Increments the time since immunity for each method."""
        if self.immunity_time_exvacc > -1:
            self.immunity_time_exvacc += 1
        if self.immunity_time_newvacc > -1:
            self.immunity_time_newvacc += 1
        if self.immunity_time_infec > -1:
            self.immunity_time_infec += 1

    def change_status(self, total_infections, infections_each_day):
        """Decision tree to determine a person's status at each time step.
        Parameters:
            total_infections (pd.DataFrame): keep track of how many people in each status for infection force
            infections_each_day (pd.DataFrame): identify who enters each status each day for final outputs"""
        # Check vaccine status and set to add to index
        if self.vacc_status_t_i == 'unvacc' or self.vacc_status_t_i == 'ineligible':
            vacc_status = 'unvaccinated'
        if self.vacc_status_t_i == 'ex_vacc':
            vacc_status = 'ex_vaccine'
        if self.vacc_status_t_i == 'new_vacc':
            vacc_status = 'new_vaccine'
        # If dead - consideration is seperate from the rest of the population
        if self.status == 'dead':
            if self.death_t_i == -1:
                return
            else:
                self.death_t_i -= 1
                if self.death_t_i == -1:  # death time over
                    total_infections.loc[(self.age_group, vacc_status), 'hospitalised'] -= 1  # remove from hospital
                    total_infections.loc[(self.age_group, vacc_status), 'dead'] += 1  # and add to dead at t
                    infections_each_day.loc[(self.age_group, vacc_status), 'dead'] += 1  # and time over, add to dead at t
                    return
        # If infected in any condition, then count down until recovered and back to susceptible population or removed
        if (self.status == 'asymptomatic' or self.status == 'symptomatic' or self.status == 'hospitalised'):
            self.infect_t_i -= 1  # count down infection time
            if self.infect_t_i == -1:  # if infection time is over
                if self.status == 'asymptomatic': # remove from asymptomatic total counts
                    total_infections.loc[(self.age_group, vacc_status), 'asymptomatic'] -= 1
                if self.status == 'symptomatic':  # remove from symptomatic total counts
                    total_infections.loc[(self.age_group, vacc_status), 'symptomatic'] -= 1
                if self.status == 'hospitalised':  # remove from hospitalised total counts
                    total_infections.loc[(self.age_group, vacc_status), 'hospitalised'] -= 1
                self.status = 'susceptible'  # back to susceptible
            return
        # If exposed, count down until latent period is finished and then determine response to infection
        if self.status == 'exposed':
            self.latent_t_i -= 1
            if self.latent_t_i == -1:  # if latent period is finished, determine type of infection
                self.determine_status_change(['symptomatic', 'asymptomatic'],   # (a)symptomatic or not
                                             params.p_v_symp_a)
                self.infect_t_i = self.pick_distr_prob(params.infec_t)  # determine infectious period time
                if self.status == 'asymptomatic':
                    total_infections.loc[(self.age_group, vacc_status), 'asymptomatic'] += 1
                    infections_each_day.loc[(self.age_group, vacc_status), 'asymptomatic'] += 1
                if self.status == 'symptomatic':  # if symptomatic
                    self.determine_status_change(['hospitalised', 'symptomatic'],  # check if hospitalised
                                                 params.p_nv_IH_list[self.age_group_index] * self.susceptibility_H)
                    if self.status != 'hospitalised':  # if not hospitalised
                        total_infections.loc[(self.age_group, vacc_status), 'symptomatic'] += 1  # add to symptomatic
                        infections_each_day.loc[(self.age_group, vacc_status), 'symptomatic'] += 1  # add to symptomatic
                    if self.status == 'hospitalised':  # if hospitalised, calculate how long in hospital
                        self.hosp_t_i = self.pick_distr_prob(params.hosp_t)
                        self.determine_status_change(['dead', 'hospitalised'],  # check if they die
                                                     params.p_nv_HD_list[self.age_group_index])
                        total_infections.loc[(self.age_group, vacc_status), 'hospitalised'] += 1  # add to hospitalised
                        infections_each_day.loc[(self.age_group, vacc_status), 'hospitalised'] += 1  # add to hospitalised
                        if self.status == 'dead':  # if they die, calculate how long it takes
                            self.death_t_i = self.hosp_t_i + self.pick_distr_prob(params.death_t)
            return
        # If a person is susceptible, see if they become exposed
        if self.status == 'susceptible':
            self.determine_status_change(['exposed', 'susceptible'], self.prob_exposed)
            if self.status == 'exposed':  # once exposed, choose time until infected
                self.vacc_status_t_i = self.vacc_status  # set vaccine status for the dataframe
                self.immunity_time_infec = 0  # give immunity time
                self.latent_t_i = self.pick_distr_prob(params.latent_t)
            return
