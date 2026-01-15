# Import useful modules
import os
from vaccbopti.classes.params import Params
from vaccbopti.classes.infectioncount import InfectionCount
from vaccbopti.classes.infectionforce import InfectionForce
from vaccbopti.classes.timesteps import Timesteps
params = Params.instance()
infectioncount = InfectionCount.instance()
infection_force = InfectionForce()
project_root = os.path.dirname(os.path.dirname(__file__))

# Get initial variables
sim_length = 100
num_people = 100
n_infec = 5
n_indiv = [3, 5, 5, 5,  # number in each age group N(a) - NORMALLY FROM PARAMS
           5, 5, 8, 10,
           7, 8, 9, 12,
           5, 6, 5, 2]
R_e = 1.5

# Initialise people for the simulation
timesteps = Timesteps(num_people, n_indiv, sim_length, R_e)  # initialise people
timesteps.initialise_people(n_infec)  # give people old immunity and some new infections 
# VACCINE BOOSTER STRATEGY
timesteps.get_p_exposed(infection_force.lambda_list)  # update suceptibilities/prob exposed
infec_rate_param = timesteps.calculate_new_beta()  # get a new beta based on these initial values

# Loop through timesteps
for t in range(1, sim_length):
    infection_force.all_lambda(infec_rate_param)
    timesteps.get_p_exposed(infection_force.lambda_list)
    timesteps.increment_people()
