# FILE FOR TIMESTEPS CLASS

# Import other modules
from vaccbopti.classes.person import Person
from vaccbopti.classes import Params
#from vaccbopti.classes.infectionforce import InfectionForce
import numpy as np
params = Params.instance()


# Define Timesteps class
class Timesteps:
    """A class representing the steps in the simulation."""

    def __init__(self, num_people, n_age_groups, sim_length=365, R_e=1.5):
        """Initialise the Timesteps object.
        Inputs:
            num_people (int): the total number of people involved in the simulation
            n_age_groups (list): the number of people in each age group
            sim_length (int): the total length of time in the simulation
            R_e (float): effective reproduction number/transmissibility of the novel variant
        Parameters:
            indices (array): all the indices for all people
            People (array): all the people in the simulation
            IDs (array): all the IDs of each of the people
            n_age_groups (list): the indices for the ranges of people in each age group
        """
        self.sim_length = sim_length
        self.R_e = R_e
        self.num_people = num_people
        self.indices = np.linspace(0, num_people - 1, num_people)
        self.People = np.array([Person() for p in range(num_people)])
        self.IDs = np.array([p.id for p in self.People])
        self.n_age_groups = np.cumsum([0] + n_age_groups)

    def initialise_people(self, n_infec):
        """Ensure people have all information necessary after initialisation:
           - assigned age groups,
           - have been infected/vaccinated with a previous variant at some point
           - random subset are infected
        Parameters:
            n_age_groups (list): number of people in each age group
            n_infec (int): number of people to be randomly infected
            new_beta: the new infection rate given the desired R_e value
            """
        for n in range(len(self.n_age_groups) - 1):
            for p in range(self.n_age_groups[n], self.n_age_groups[n + 1]):
                self.People[p].age_group = str(params.age_groups[n])
                self.People[p].immunity_time_exvacc = np.random.choice(365 * 2 + 1)
        infect_group = np.random.choice(self.indices, n_infec)
        for p in infect_group:
            self.People[int(p)].initialise_infection()

        for a in range(len(params.contactmatrix)):
            for b in range(len(params.contactmatrix)):
                calc_R_ab = ((params.p_v_symp_a[a] + params.infec_asymp * (1 - params.p_v_symp_a[a]))
                             * (1 / params.mean_infec * self.calculate_average_susceptibility()
                             * params.infec_rate_param[a] * params.contactmatrix[a, b]))

        old_R_e = np.linalg.eigvals(calc_R_ab).max()
        new_beta_factor = self.R_e / old_R_e

        new_beta = new_beta_factor * params.infec_rate_param
        return new_beta

    def get_p_exposed(self, force_infection):
        """Gets the probability that a person is exposed.
        Parameters:
            force_infection (float): the force of infection calcuated"""
        for n in range(len(self.n_age_groups) - 1):
            for p in range(self.n_age_groups[n], self.n_age_groups[n + 1]):
                self.People[p].calc_susceptibility()
                self.People[p].calc_prob_exposed(force_infection[n])

    def increment_people(self):
        """Increases immunity times by 1 and changes status."""
        for p in self.People:
            p.increment_immunity_time()
            p.change_status()

    def calculate_average_susceptibility(self):
        """Calculate the average of the susceptibility.

        First, take the attribute susceptibility calculated in get_p_exposed.

        Then sum the values and divide by the number of people for getting the average susceptibility.
        """
        susceptibility_sum = 0
        for p in self.People:
            susceptibility_sum += p.susceptibility
        average_susceptibility = susceptibility_sum / self.num_people
        return average_susceptibility

    # CHECK MAIN.PY TO SEE THE LOOP THERE - THAT's EQUIVALENT TO THIS LOOP
    def simulate_vaccination(self):
        for t in len(self.sim_length):
            return
