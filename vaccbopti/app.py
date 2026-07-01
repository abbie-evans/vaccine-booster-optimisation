# Import useful modules
import os
from shiny import reactive
from shiny.express import input, render, ui
from run_simulation import Simulation
project_root = os.path.dirname(os.path.dirname(__file__))

# Create a list of each of the outputs of subsequent runs
sim_runs_means = []
sim_runs_stds = []


# --- THE GUI OF THE PAGE --

# Title
ui.page_opts(title="Vaccine Booster Optimisation Simulations", fillable=True)

# Sidebar to hold all the user inputs
with ui.sidebar(position="left"):

    # Dark Mode
    ui.input_dark_mode(mode="light")

    # Allow you to either run a simulation or load previous data
    with ui.accordion(id='inputs', open='Run Simulation'):
        # Simulation inputs
        with ui.accordion_panel('Run Simulation'):
            # Number of runs
            with ui.tooltip(id="number_runs_tooltip", placement="right"):
                ui.input_numeric("number_runs", "Number of Runs", 10, min=1, step=1)
                "The number of times you want to run a simulation."
            # Simulation Length
            with ui.tooltip(id="sim_length_tooltip", placement="right"):
                ui.input_numeric("sim_length", "Simulation Timesteps", 100, min=5, step=1)
                "The number of timesteps (days) each simulation will run for."
            # Number of people
            with ui.tooltip(id="num_people_tooltip", placement="right"):
                ui.input_numeric("num_people", "Number of People", 100, min=10, step=1)
                "The number of people to have in the simulation."
            # Percentage of people that will not recieve the vaccine
            with ui.tooltip(id="n_ineligible_tooltip", placement="right"):
                ui.input_numeric("n_ineligible", "% of Population Ineligable for Vaccine", 0.2, min=0, max=1, step=0.01)
                "The percentage of people that will not be vaccinated, due to being immunocompromised or vaccine-hesitant."
            # Number of Infected
            with ui.tooltip(id="n_infec_tooltip", placement="right"):
                ui.input_numeric("n_infec", "Initially Infected People", 40, min=0, max=100, step=1)
                "The number of people who start the simulation exposed to the new variant."
            @reactive.effect  # dynamically changes the max limit to be limited by total number of people
            def _():
                n_infec = input.n_infec()
                if (input.num_people() is not None) & (n_infec is not None):
                    if n_infec > input.num_people():
                        n_infec = input.num_people()
                    ui.update_numeric("n_infec", value=n_infec, max=input.num_people())
            # R_e
            with ui.tooltip(id="R_e_tooltip", placement="right"):
                ui.input_numeric("R_e", "Transmissability of New Variant", 1.5, min=0.1, step=0.01)
                "The transmissability, R_e, of the novel varient."
            # Vaccine Strategy
            with ui.tooltip(id="vacc_strat_tooltip", placement="right"):
                ui.input_selectize("vacc_strat", "Vaccine Administration Strategy",
                                {0: "No Booster",
                                1: "Strategy 1",
                                2: "Strategy 2",
                                3: "Strategy 3",
                                4: "Strategy 4",
                                5: "Strategy 5",
                                6: "Strategy 6"})
                "Which booster vaccine administration strategy to use - see the introduction for more details."
            # Number of Vaccines to Give Out
            with ui.tooltip(id="vacc_amount_tooltip", placement="right"):
                ui.input_numeric("vacc_amount", "Number of Boosters Admistered Per Day", 10, min=1)
                "The number of booster vaccines to administer per day."
            # New Vaccine Availability
            with ui.tooltip(id="t_newvacc_avail_tooltip", placement="right"):
                ui.input_numeric("t_newvacc_avail", "New Vaccine Availability", 10, min=1)
                "Which day the new booster vaccine (for the new variant) is available to be administered. Only a vaccine for an old variant (which is less effective) is available before this."
            # Run simulation Button
            ui.input_action_button("run", "Run simulation")  

        # Load other csvs
        with ui.accordion_panel('Load inputs'):
            'Load csv'

# Main outputs panels
with ui.navset_card_pill(id="main_tabs"):
    with ui.nav_panel("Introduction"):
        "Panel A content for testing"
    with ui.nav_panel("Outputs"):
        "Panel B content"


# --- FUNCTIONS TO RUN THE GUI ---

# Run simulation code
@reactive.calc
def calc_simulation():
    sim = Simulation(number_runs=input.number_runs(),
                        sim_length=input.sim_length(),
                        num_people=input.num_people(),
                        n_infec=input.n_infec(),
                        n_ineligible=input.n_ineligible(),
                        R_e=input.R_e(),
                        vacc_strat=input.vacc_strat(),
                        vacc_amount=input.vacc_amount(),
                        t_newvacc_avail=input.t_newvacc_avail())
    with ui.Progress(min=0, max=input.number_runs()*input.sim_length()) as p:
        sim.run(progress=p)
        sim.save_csv()
    return sim

# When button is pressed
@render.text
@reactive.event(input.run)
def run_simulation():
    sim = calc_simulation()  # run simulation
    sim_runs_means.append(sim.statusDF_mean)  # add mean dataframe to list of runs
    sim_runs_stds.append(sim.statusDF_std)  # add std dataframe to list of runs
    ui.update_navset("main_tabs", selected="Outputs")  # switch to outputs tab!
    return f"Saved run {len(sim_runs_means)} of the session! :)"  # visible output so know it's worked
