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


# Define class to run simulation that can then interact with the app

class Simulation:
    """The class that will be used to run a simulation."""

    def __init__(self, number_runs=2, sim_length=100, num_people=100, n_infec=60, n_ineligible=0.2,
                 R_e=1.5, vacc_strat=0, vacc_amount=10, t_newvacc_avail=5):
        """Initialise the simulation with the user inputs.
        User inputs:
            number_runs (int): the number of runs you want to average over
            sim_length (int): the timesteps (days) the simulation runs
            num_people (int): number of people in the simulation
            n_infec = 60 (int): initial number of people exposed to new variant
            n_ineligible (float): percent of population that won't receive vaccine
            R_e (float): transmissibility of the novel variant
            vacc_strat (int): vaccination strategy used
            vacc_amount (int): change this for varying number of boosters administered per day
            t_newvacc_avail (int): if making the new vaccine available after a certain time
        """
        # Save user inputs as variables
        self.number_runs = number_runs
        self.sim_length = sim_length
        self.num_people = num_people
        self.n_infec = n_infec
        self.n_ineligible = n_ineligible
        self.R_e = R_e
        self.vacc_strat = vacc_strat
        self.vacc_amount = vacc_amount
        self.t_newvacc_avail = t_newvacc_avail
        # Create overall output dataframes
        self.timepoints = list(range(0, self.sim_length))
        self.vaccine = ['unvaccinated', 'old_vaccine', 'new_vaccine']
        self.df_status = ['symptomatic', 'asymptomatic', 'hospitalised', 'dead']
        index = list(itertools.product(*[self.timepoints, params.age_groups, self.vaccine]))
        index = pd.MultiIndex.from_tuples(index, names=["t", "ages", "vacc_status"])
        self.statusDF_sum = pd.DataFrame(0, index=index, columns=self.df_status)
        self.statusDF_sum_squares = pd.DataFrame(0, index=index, columns=self.df_status)

    def run(self, progress=None):
        """Runs the simulation! :)
        Parameters:
            progress (optional): a shiny.ui.Progress object which will be used to send progress updates"""
        # Initialise set up
        if (progress is not None):
            progress.set(0,
                         message="Initialising simulation...",
                         detail="Setting up people, updating susceptibilities...")
        # Start loop for each run
        for r in range(self.number_runs):
            # Initialise people for the simulation
            timesteps = Timesteps(self.num_people, self.sim_length, self.R_e)  # initialise people
            timesteps.initialise_people(self.n_infec, n_ineligible=self.n_ineligible)  # set immunity and infections
            timesteps.get_p_exposed(infection_force.lambda_list)  # update suceptibilities/prob exposed
            infec_rate_param = timesteps.calculate_new_beta()  # get a new beta based on these initial values
            # Loop through timesteps
            for t in range(1, self.sim_length):
                infection_force.all_lambda(infectioncount, infec_rate_param, num_people=self.num_people)  # F_infec
                timesteps.administer_booster(self.vacc_strat, self.t_newvacc_avail, t, self.vacc_amount)  # boosters
                timesteps.get_p_exposed(infection_force.lambda_list)  # recalculate susceptibilities/prob exposed
                timesteps.increment_people(infectioncount)  # update people
                timesteps.append_daily_nbs_outputdf(t, infectioncount)  # updates overall dataframe
                # Shiny progress update
                if (progress is not None) and (t % 2 == 0 or t == 1):
                    progress.set((r + 1) * t,
                                 message=f"Performing step {(r + 1) * t}/{self.number_runs*self.sim_length}",
                                 detail=f"Run: {r + 1}/{self.number_runs}; Timestep: {t}/{self.sim_length}")
            # Update overall dataframes
            self.statusDF_sum = self.statusDF_sum.add(timesteps.statusDF)  # summing each run (divide to get average)
            self.statusDF_sum_squares = self.statusDF_sum_squares.add(timesteps.statusDF ** 2)  # sum squares for std
        # Get the mean and std from sum values and save to output
        self.statusDF_std = ((self.statusDF_sum_squares / self.number_runs)
                             - (self.statusDF_sum / self.number_runs) ** 2)
        self.statusDF_std = np.sqrt(self.statusDF_std)
        self.statusDF_mean = self.statusDF_sum / self.number_runs  # get mean over runs
 
    def save_csv(self):
        """Saves the csvs"""
        self.statusDF_mean.to_csv(f'{project_root}/outputs/model_example_strategy_{self.vacc_strat}_mean.csv')  # save mean
        self.statusDF_std.to_csv(f'{project_root}/outputs/model_example_strategy_{self.vacc_strat}_std.csv')  # save std
