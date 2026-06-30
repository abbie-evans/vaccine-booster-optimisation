# Import useful modules
import os
import itertools
import numpy as np
import pandas as pd
from vaccbopti.classes import Params
from vaccbopti.classes import InfectionCount
from vaccbopti.classes import InfectionForce
from vaccbopti.classes import Timesteps
params = Params.instance()
infectioncount = InfectionCount().count_df
infection_force = InfectionForce()
project_root = os.path.dirname(os.path.dirname(__file__))


# Get initial variables
number_runs = 2  # change this for the number of runs you want to average over
sim_length = 50  # change this for simulation length
num_people = 100  # change this for variable number of people
n_infec = 60  # change this for initial number of people exposed
R_e = 1.5  # change this for transmissibility of the novel variant
vacc_strat = 3  # change this for vaccine strategy
vacc_amount = 10  # change this for varying number of boosters per day
t_newvacc_avail = 2  # if only making vaccine available after a certain time change this

# Create overall output dataframes
timepoints = list(range(0, sim_length))
vaccine = ['unvaccinated', 'old_vaccine', 'new_vaccine']
df_status = ['symptomatic', 'asymptomatic', 'hospitalised', 'dead']
index = list(itertools.product(*[timepoints, params.age_groups, vaccine]))
index = pd.MultiIndex.from_tuples(index, names=["t", "ages", "vacc_status"])
statusDF_sum = pd.DataFrame(0, index=index, columns=df_status)
statusDF_sum_squares = pd.DataFrame(0, index=index, columns=df_status)

# Start loop for each run
for r in range(number_runs):

    # Initialise people for the simulation
    timesteps = Timesteps(num_people, sim_length, R_e)  # initialise people
    timesteps.initialise_people(n_infec)  # give people old immunity and some new infections
    timesteps.get_p_exposed(infection_force.lambda_list)  # update suceptibilities/prob exposed
    infec_rate_param = timesteps.calculate_new_beta()  # get a new beta based on these initial values

    # Loop through timesteps
    for t in range(1, sim_length):
        infection_force.all_lambda(infectioncount, infec_rate_param, num_people=num_people)  # update force of infection
        timesteps.administer_booster(vacc_strat, t_newvacc_avail, t, vacc_amount)  # administer the boosters
        timesteps.get_p_exposed(infection_force.lambda_list)  # recalculate susceptibilities/prob exposed
        timesteps.increment_people(infectioncount)  # update people
        timesteps.append_daily_nbs_outputdf(t, infectioncount)  # updates overall dataframe

    # Update overall dataframes
    statusDF_sum = statusDF_sum.add(timesteps.statusDF)  # summing values from each run (will divide to get average)
    statusDF_sum_squares = statusDF_sum_squares.add(timesteps.statusDF ** 2)  # sum of squares to find the variance/std

# Get the mean and std from sum values and save to output
statusDF_std = (statusDF_sum_squares / number_runs) - (statusDF_sum / number_runs) ** 2  # get std over
statusDF_std = np.sqrt(statusDF_std)
statusDF_mean = statusDF_sum / number_runs  # get mean over runs

statusDF_mean.to_csv(f'{project_root}/outputs/output_mean_strategy_{vacc_strat}.csv')  # save mean data
statusDF_std.to_csv(f'{project_root}/outputs/output_std_strategy_{vacc_strat}.csv')  # save std data
