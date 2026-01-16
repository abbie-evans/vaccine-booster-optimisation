# Import useful modules
import os
from classes.params import Params
from classes.infectioncount import InfectionCount
from classes.infectionforce import InfectionForce
from classes.timesteps import Timesteps
params = Params.instance()
infectioncount = InfectionCount.instance()
infection_force = InfectionForce()
project_root = os.path.dirname(os.path.dirname(__file__))

# Get initial variables
sim_length = 100  # change this for simulation length
num_people = 100  # change this for variable number of people
n_infec = 60  # change this for initial number of people exposed
R_e = 1.5  # change this for transmissibility of the novel variant
vacc_strat = 1  # change this for vaccine strategy
vacc_amount = 10  # change this for varying number of boosters per day
t_newvacc_avail = 2  # if only making vaccine available after a certain time change this

# Initialise people for the simulation
timesteps = Timesteps(num_people, sim_length, R_e)  # initialise people
timesteps.initialise_people(n_infec)  # give people old immunity and some new infections
timesteps.get_p_exposed(infection_force.lambda_list)  # update suceptibilities/prob exposed
infec_rate_param = timesteps.calculate_new_beta()  # get a new beta based on these initial values

# Loop through timesteps
for t in range(1, sim_length):
    infection_force.all_lambda(infec_rate_param, num_people=num_people)  # update force of infection
    timesteps.administer_booster(vacc_strat, t_newvacc_avail, t, vacc_amount)  # administer the boosters
    timesteps.get_p_exposed(infection_force.lambda_list)  # recalculate susceptibilities/prob exposed
    timesteps.increment_people()  # update people
