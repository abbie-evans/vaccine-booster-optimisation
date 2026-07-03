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
            status (str): person's status relative to the infection
                          susceptible, exposed, symptomatic, asymptomatic, hospitalised, dead
            vacc_status (str): person's vaccination status
                               unvacc, old_vacc, new_vacc, ineligible
            vacc_status_t_i (str): the person's vaccine status at the time of infection
            susceptibility (float): susceptibility, v(t), of an individual
            prob_exposed (float): probability an individual will become infected
            latent_t_i (int): time left in the latent period once exposed
            infect_t_i (int): time left in infectious period once infectious (symptomatic or asymptomatic)
            hosp_t_i (int): time spent in hospital
            death_t_i (int): time at death from hospitalisation
            immunity_time_exvacc (int): time since given last vaccination/sickness from previous strain
            immunity_time_newvacc (int): time since given since strain-adapted vaccine
            immunity_time_infec (int): time since infection with novel strain
        """
        self.id = next(self.id_iter)
        self.age_group = None
        self.status = 'susceptible'
        self.vacc_status = 'unvacc'
        self.vacc_status_t_i = 'unvacc'
        self.susceptibility = 0
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
        self.age_group = str(params.age_groups[n])

    def calc_susceptibility(self):
        """Calculates the relative susceptibility, v(t), of an individual.
        Returns:
            susceptibility (float): level of susceptibility is determined by their immune status
        """
        if self.immunity_time_exvacc < 0:
            immunity_exvacc = 0
        else:
            immunity_exvacc = params.f_exvacc[self.immunity_time_exvacc]
        if self.immunity_time_newvacc < 0:
            immunity_newvacc = 0
        else:
            immunity_newvacc = params.f_newvacc[self.immunity_time_newvacc]
        if self.immunity_time_infec < 0:
            immunity_infec = 0
        else:
            immunity_infec = params.f_infec[self.immunity_time_infec]
        susceptibility = 1 - max(immunity_exvacc,
                                 immunity_newvacc,
                                 immunity_infec)
        self.susceptibility = susceptibility

    def calc_prob_exposed(self, force_infection):
        """Calculates the probability a person's status changes from susceptible to exposed."""
        exp_val = np.exp(-self.susceptibility * force_infection)
        self.prob_exposed = 1 - exp_val

    def pick_distr_prob(self, distribution):
        """Determines the number of days a person is in a status, dependent on the probabiltiy distribution.
        Params:
            distribution (array): the probability distribution for different days
        Returns:
            days (int): the number of days a person is in a specific status
        """
        choices = list(range(1, len(distribution) + 1))
        days = np.random.choice(choices, p=distribution)
        return days

    def determine_status_change(self, statuses, probability):
        """Determines if the person's status, based on probability.
        Params:
            statuses (list): a list of the two possible statuses
            probability (float or list): a float of probability or list of probabilities per age group
        """
        if type(probability) is list:
            index = np.where(np.array(params.age_groups) == self.age_group)[0][0]
            status = np.random.choice(statuses, size=1, p=[probability[index], 1 - probability[index]])
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

    def change_status(self, infectioncount):
        """Decision tree to determine a person's status at each time step."""
        # Check vaccine status and set to add to index
        if self.vacc_status_t_i == 'unvacc' or self.vacc_status_t_i == 'ineligible':
            vaccine = 'unvaccinated'
        if self.vacc_status_t_i == 'old_vacc':
            vaccine = 'old_vaccine'
        if self.vacc_status_t_i == 'new_vacc':
            vaccine = 'new_vaccine'
        # If dead - consideration is seperate from the rest of the popluation
        if self.status == 'dead':
            if self.death_t_i == -1:
                return
            else:
                self.death_t_i -= 1
                if self.death_t_i == -1:  # death time over
                    infectioncount.loc[(self.age_group, vaccine), 'dead'] += 1  # ...and time over, add to dead for t
                    return
        # If infected in any condition, then count down until recovered and back to susceptible population or removed
        if (self.status == 'symptomatic' or self.status == 'asymptomatic' or self.status == 'hospitalised'):
            self.infect_t_i -= 1  # count down infection time
            if self.infect_t_i == -1:  # if infection time is over
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
                    infectioncount.loc[(self.age_group, vaccine), 'asymptomatic'] += 1
                if self.status == 'symptomatic':  # if symptomatic
                    self.determine_status_change(['hospitalised', 'symptomatic'],  # check if hospitalised
                                                 params.p_nv_IH)
                    if self.status != 'hospitalised':  # if not hospitalised
                        infectioncount.loc[(self.age_group, vaccine), 'symptomatic'] += 1  # set symptomatic count
                    if self.status == 'hospitalised':  # if hospitalised, calculate how long in hospital
                        self.hosp_t_i = self.pick_distr_prob(params.hosp_t)
                        self.determine_status_change(['dead', 'hospitalised'],  # check if they die
                                                     params.p_nv_HD)
                        infectioncount.loc[(self.age_group, vaccine), 'hospitalised'] += 1  # add to hospitalised count
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
