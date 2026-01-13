# Import useful modules
import os
from vaccbopti.classes.params import Params
from vaccbopti.classes.infectioncount import InfectionCount
from vaccbopti.classes.infectionforce import InfectionForce
from vaccbopti.classes.timesteps import Timesteps
params = Params.instance()
infectioncount = InfectionCount.instance()
project_root = os.path.dirname(os.path.dirname(__file__))

# Get initial varialbes
sim_length = 100
num_people = 100
n_infec = 5
n_indiv = [3, 5, 5, 5,  # number in each age group N(a) - NORMALLY FROM PARAMS
           5, 5, 8, 10,
           7, 8, 9, 12,
           5, 6, 5, 2]

##### INTIALISE PEOPLE
timesteps = Timesteps(num_people, n_indiv)
timesteps.initialise_people(n_infec)
print(timesteps.People[1].immunity_time_exvacc)

##### LOOP
for t in range(0, sim_length):
    #### Calculate starting infectiousness/susceptibility etc
    infection_force = InfectionForce()
    infection_force.all_lambda()
    ### DEPENDING ON T ADMINISTER SOME VACCINES USING BOOSTER STRATEGY
    timesteps.get_p_exposed(infection_force.lambda_list)
    timesteps.increment_people()