# FILE CONTAINING ALL THE RELEVANT INFORMATION AND FUNCTIONS FOR A PERSON IN THE SIMULATION.


# Import useful modules
import numpy as np
from params import Params
from infectionforce import InfectionForce

# Define Person class
class Person:
    """A class representing an individual in the simulation."""

    def __init__(self):
        """Initialise the Person object.
        Parameters:
            age_group (str): the age group the person belongs to (16 different classes, seen in parameter file)
            status (str): person's status relative to the infection
                          susceptible, exposed, symptomatic, asymptomatic, hospitalised, dead
            prob_infected (float): probability an individual will become infected
            latent_t_i (int): time left in the latent period once exposed
            infect_t_i (int): time left in infectious period once infectious (symptomatic or asymptomatic)
            hosp_t_i (int): time spent in hospital
            death_t_i (int): time at death from hospitalisation
            immunity_time_exvacc (int): time since given last vaccination/sickness from previous strain
            immunity_time_newvacc (int): time since given since strain-adapted vaccine
            immunity_time_infec (int): time since infection with novel strain
        """
        self.age_group = None
        self.status = 'susceptible'
        self.prob_exposed = 0.01
        self.latent_t_i = -1
        self.infect_t_i = -1
        self.hosp_t_i = -1
        self.death_t_i = -1
        self.immunity_time_exvacc = -1
        self.immunity_time_newvacc = -1
        self.immunity_time_infec = -1

    def get_age_group(self, n):
        """Assign individual a specific age-group.
        Params:
            n (int): index for a specific age group from array of age groups
        """
        self.age_group = str(Params.instance().age_groups[n])

    def calc_prob_exposed(self):
        """Calculates the probability a person's status changes from susceptible to exposed."""
        exp_val = np.exp(-self.calc_susceptibility() * InfectionForce.instance().infection_force)
        self.prob_exposed = 1 - exp_val

    def calc_susceptibility(self):
        """Calculates the relative susceptibility, v(t), of an individual.
        Returns:
            susceptibility (float): level of susceptibility is determined by their immune status
        """
        if self.immunity_time_exvacc < 0:
            immunity_exvacc = 0
        else:
            immunity_exvacc = Params.instance().f_exvacc[self.immunity_time_exvacc]
        if self.immunity_time_newvacc < 0:
            immunity_newvacc = 0
        else:
            immunity_newvacc = Params.instance().f_newvacc[self.immunity_time_newvacc]
        if self.immunity_time_infec < 0:
            immunity_infec = 0
        else:
            immunity_infec = Params.instance().f_infec[self.immunity_time_infec]
        susceptibility = 1 - max(immunity_exvacc,
                                 immunity_newvacc,
                                 immunity_infec)
        return susceptibility

    def change_status(self):
        """Decision tree to determine a person's status at each time step."""
        # If infected in any condition, then count down until recovered and back to susceptible population
        if self.status == 'symptomatic' or self.status == 'asymptomatic' or self.status == 'hospitalised':
            self.infect_t_i -= 1
            if self.infect_t_i == -1:
                self.status = 'susceptible'
        # If exposed, count down until latent period is finished and then determine response to infection
        if self.status == 'exposed':
            self.latent_t_i -= 1
            if self.latent_t_i == -1:  # if latent period is finished, determine type of infection
                self.determine_status_change(["symptomatic", "asymptomatic"],   # (a)symptomatic or not
                                             Params.instance().p_v_symp_a)
                self.infect_t_i = self.pick_distr_prob(self,  # determine infectious period time
                                                       Params.instance().infec_period)                   
                if self.status == 'symptomatic':  # if symptomatic
                    self.determine_status_change(['symptomatic', 'hospitalised'],  # check if hospitalised
                                                 Params.instance().p_nv_IH)
                    if self.status == 'hospitalised':  # if hospitalised, calculate how long in hospital
                        self.hosp_t_i = self.pick_distr_prob(Params.instance().hosp_time)
                        self.determine_status_change(['hospitalised', 'dead'],  # check if they die
                                                     Params.instance().p_nv_HD)
                        if self.status == 'dead':  # if they die, calculate how long it takes
                            self.death_t_i = self.hosp_t_i + self.pick_distr_prob(Params.instance().death_period)
        # If a person is susceptible, see if they become exposed
        if self.status == 'susceptible':
            self.determine_status_change(['susceptible', 'exposed'], self.prob_exposed)
            if self.status == 'exposed':  # once exposed, choose time until infected
                self.latent_t_i = self.pick_distr_prob(Params.instance().latent_time)

    def determine_status_change(self, statuses, probability):
        """Determines if the person's status, based on probability.
        Params:
            statuses (list): a list of the two possible statuses
            probability (float or list): a float of probability or list of probabilities per age group
        """
        if type(probability) is list:
            index = np.where(Params.instance().age_groups == self.age_group)[0][0]
            status = np.random.choice(statuses, size=1, p=[probability[index], 1 - probability[index]])
        else:
            status = np.random.choice(statuses, size=1, p=[probability, 1 - probability])
        self.status = str(status[0])

    def pick_distr_prob(self, distribution):
        """Determines the number of days a person is in a status, dependent on the probabiltiy distribution.
        Params:
            distribution (array): the probability distribution for different days
        Returns:
            days (int): the number of days a person is in a specific status
        """
        days = np.random.choice(distribution)
        return int(days)
