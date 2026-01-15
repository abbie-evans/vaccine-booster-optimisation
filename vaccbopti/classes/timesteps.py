# FILE FOR TIMESTEPS CLASS

# Import other modules
from vaccbopti.classes.person import Person
from vaccbopti.classes import Params
import numpy as np
import random
params = Params.instance()


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

    def initialise_people(self, n_infec):
        """Ensure people have all information necessary after initialisation:
           - assigned age groups,
           - have been infected/vaccinated with a previous variant at some point
           - random subset are infected
           - updates their susceptibility based on these infection times
        Parameters:
            rho_age_groups (list): number of people in each age group
            n_infec (int): number of people to be randomly infected
            """
        for n in range(len(self.rho_age_groups) - 1):
            for p in range(self.rho_age_groups[n], self.rho_age_groups[n + 1]):
                self.People[p].get_age_group(n)
                self.People[p].immunity_time_exvacc = np.random.choice(365 * 2 + 1)
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

    def increment_people(self):
        """Increases immunity times by 1 and changes status."""
        for p in self.People:
            p.change_status()
            p.increment_immunity_time()
