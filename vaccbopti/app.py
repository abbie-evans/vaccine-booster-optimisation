# Import useful modules
import os
import re
import pandas as pd
from run_simulation import Simulation
from shinywidgets import render_plotly
from shiny import reactive
from shiny.express import expressify, input, render, ui
from shiny.types import FileInfo
from make_plots import get_yll, load_status_data, aggregate_status, format_combined_sd, plot_track_status_plotly, plot_age_dynamics_plotly, plot_strategy_comparison_plotly, get_strategy_totals
import plotly.express as px
from faicons import icon_svg as icon


# File paths
project_root = os.path.dirname(os.path.dirname(__file__))
strategy_dir = f'{project_root}/outputs'
files = [f for f in os.listdir(strategy_dir) if f.endswith('.csv')]
examples = [f for f in files if 'mean' in f]
examples = [f.split('_mean')[0] for f in examples]

# Create a dictionary of each of the mean outputs of runs (example and subsequent)
sim_runs_means = {}
for f in examples:
    sim_runs_means.update({f: pd.read_csv(f'{strategy_dir}/{f}_mean.csv')})

# Create a dictionary of each of the std ouputs of runs (example and subsequent)
sim_runs_stds = {}
for f in examples:
    if os.path.isfile(f'{strategy_dir}/{f}_std.csv'):
        sim_runs_stds.update({f: pd.read_csv(f'{strategy_dir}/{f}_std.csv')})

# Create a reactive value to update simulation choice
run_names = reactive.value(list(sim_runs_means.keys()))
@expressify
def choose_simulation_run(id):
    global sim_runs_means
    ui.input_select(id, "Select simulation", dict(zip(sim_runs_means.keys(), sim_runs_means.keys())))
    @reactive.effect  # dynamically changes the list for each of the runs or uploads
    def _():
        ui.update_select(id, choices=dict(zip(run_names(), run_names())))
@expressify
def choose_multiple_simulations(id):
    global sim_runs_means
    ui.input_selectize(id, "Select simulations", dict(zip(sim_runs_means.keys(), sim_runs_means.keys())), multiple=True, selected=sim_runs_means.keys())
    @reactive.effect  # dynamically changes the list for each of the runs or uploads
    def _():
        ui.update_selectize(id, choices=dict(zip(run_names(), run_names())), selected=run_names())

# Load data
def load_data(label):
    global sim_runs_means, sim_runs_stds
    df_sum = sim_runs_means[label]
    df_sd = sim_runs_stds[label]
    return df_sum, df_sd

# Plot layouts
VIVID = px.colors.qualitative.Vivid  # colour scheme
LEGEND_CAPTION = "S = symptomatic · AS = asymptomatic · H = hospitalised · D = dead"


# --- THE GUI OF THE PAGE ---
ui.page_opts(title="Optimising Vaccine Booster Implementation", fillable=True)


# --- SIDEBAR TO HAVE ALL THE USER INPUTS ---
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
                ui.input_numeric("sim_length", "Simulation Timesteps", 365, min=5, step=1)
                "The number of timesteps (days) each simulation will run for."
            # Number of people
            with ui.tooltip(id="num_people_tooltip", placement="right"):
                ui.input_numeric("num_people", "Number of People", 100000, min=10, step=1)
                "The number of people to have in the simulation."
            # Number of Infected
            with ui.tooltip(id="n_infec_tooltip", placement="right"):
                ui.input_numeric("n_infec", "Initially Infected People", 100, min=0, max=100, step=1)
                "The number of people who start the simulation exposed to the new variant."
            @reactive.effect  # dynamically changes the max limit to be limited by total number of people
            def _():
                n_infec = input.n_infec()
                if (input.num_people() is not None) & (n_infec is not None):
                    if n_infec > input.num_people():
                        n_infec = input.num_people()
                    ui.update_numeric("n_infec", value=n_infec, max=input.num_people())
            # Percentage of people that will not recieve the vaccine
            with ui.tooltip(id="n_ineligible_tooltip", placement="right"):
                ui.input_numeric("n_ineligible", "% of Population Ineligable for Vaccine", 0.2, min=0, max=1, step=0.01)
                "The percentage of people that will not be vaccinated, due to being immunocompromised or vaccine-hesitant."
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
                ui.input_numeric("vacc_amount", "Number of Boosters Admistered Per Day", 2000, min=1)
                "The number of booster vaccines to administer per day."
            @reactive.effect  # dynamically changes the max limit to be limited by total number of people
            def _():
                vacc_amount = input.vacc_amount()
                if (input.num_people() is not None) & (vacc_amount is not None):
                    if vacc_amount > input.num_people():
                        vacc_amount = input.num_people()
                    ui.update_numeric("vacc_amount", value=vacc_amount, max=input.num_people())
            # New Vaccine Availability
            with ui.tooltip(id="t_newvacc_avail_tooltip", placement="right"):
                ui.input_numeric("t_newvacc_avail", "New Vaccine Availability", 40, min=1)
                "Which day the new booster vaccine (for the new variant) is available to be administered. Only a vaccine for an old variant (which is less effective) is available before this."
            @reactive.effect  # dynamically changes the max limit to be limited by total number of days
            def _():
                t_newvacc_avail = input.t_newvacc_avail()
                if (input.sim_length() is not None) & (t_newvacc_avail is not None):
                    if t_newvacc_avail > input.sim_length():
                        t_newvacc_avail = input.sim_length()
                    ui.update_numeric("t_newvacc_avail", value=t_newvacc_avail, max=input.sim_length())
            # R_e
            with ui.tooltip(id="R_e_tooltip", placement="right"):
                ui.input_numeric("R_e", "Transmissability of New Variant", 1.5, min=0.1, step=0.01)
                "The transmissability, R_e, of the novel varient."
            # Run simulation Button
            ui.input_action_button("run", "Run simulation")
            @render.text
            @reactive.event(input.run)
            def run_simulation():
                sim = calc_simulation()  # run simulation 
                sim_runs_means.update({f"run_{len([c for c in run_names() if 'run' in c]) + 1}": sim.statusDF_mean})  # add mean dataframe to list of runs
                sim_runs_stds.update({f"run_{len([c for c in run_names() if 'run' in c]) + 1}": sim.statusDF_std})  # add std dataframe to list of runs
                ui.update_navs("main_tabs", selected="Outputs")  # switch to outputs tab!
                run_names.set(list(sim_runs_means.keys()))
                return f"Saved run {len([c for c in run_names() if 'run' in c])} of the session! :)"  # list number of runs only to confirm it worked

        # Load other csvs
        with ui.accordion_panel('Load inputs'):
            ui.input_file("csv_upload", "Upload a mean and std .csv from previous runs!", multiple=True)  
            # Save uploaded csv to file
            @render.text
            def add_uploaded_to_dict():
                files = parsed_file()
                if files is not None:
                    sim_runs_means.update(files[0])  # add means dataframe to list of runs
                    sim_runs_stds.update(files[1])  # add stds dataframe to list of runs
                    run_names.set(list(sim_runs_means.keys()))
                    return f'Added {len(files[0])} mean data file(s) and {len(files[1])} stds data file(s) for analysis! Now {len(run_names())} simulations to analyse.'


# --- MAIN OUTPUTS PANEL
with ui.navset_card_pill(id="main_tabs"):

    # Introduction text to model
    with ui.nav_panel("Introduction"):
        # Overview
        ui.markdown("""
            # Overview
            As observed during the COVID-19 pandemic, the emergence of new variants during infectious disease outbreaks has the potential to have devastating consequences, particularly if existing vaccines then offer reduced protection. When a variant of concern emerges, a crucial question for public health policy makers is whether to administer booster doses of the current vaccine (which was designed with an earlier variant in mind) or wait until an updated vaccine becomes available before deploying booster doses. Relatedly, pharmaceutical companies and vaccine manufacturers must decide whether it is worthwhile to update existing vaccines.
            <br><br>
            This app allows you to run a **stochastic, individual-based outbreak simulation** model that can be used to project numbers of cases and deaths during an outbreak of a novel variant of SARS-CoV-2 under different vaccination strategies. This can be used to investigate scenarios in which it is beneficial to wait to update a variant-specific vaccine before undertaking booster vaccination and when it is instead preferable to use an existing vaccine (without a development delay). Our model allows you to compare the outputs of **6 different booster administration strategies**.
            <br><br>
            You can run your own simulation and look at the outputs, upload previous .csv files you have created to look at, or look at and compare the outputs of our example runs!""")
        # More details
        with ui.accordion(id='model_info', open=['Model Overview', 'Booster Administration Strategies']):
            with ui.accordion_panel('Model Overview'):
                ui.markdown("""This is a stochastic individual-based model, the simulation is repeated as the number of runs set by the user over the number of timesteps, which represents days in the simulation. The mean and standard deviation of these simulations are presented in the outputs. Each simulation represents the dynamics over a given period such that one wave of the outbreak occurs. 
                            <br><br>
                            The model uses a set population of individuals with a global age distribution (based on UK values). This age distribution is separated into groups of every 5 years (0-4 years old, 5-9 years old, etc), in addition to 75+ years old. Each individual's immune status is tracked, which is conferred by infection and/or a booster vaccination - which is either a vaccine for an old varient, or a new vaccine designed specifically for the new variant. We assume each individual in the population has previously been vaccinated against and/or infected by a previous SARS-CoV-2 variant at least once over a two-year period before the start of the simulation, giving them some level of immunity.
                            <br><br>
                            At the simulation start, a random number of individuals (less than the total population) will be infected with the novel variant, allowing the intialisation of the spread.
                            <br><br>
                            Each day, a set number of people will receive the booster vaccine, with a maximum vaccine uptake level (set by the percentage of the population ineligible for the vaccine). The booster administration strategy, and when an updated version of the booster is available will affect the outcome of the model.""")
            with ui.accordion_panel('Booster Administration Strategies'):
                ui.markdown("""
                            <u>No Booster Administration</u><br>
                            No new or old boosters are administered to population.
                            <br><br>
                            <u>Strategy 1</u><br>
                            Old vaccine is administered to everyone starting with the oldest age group and proceeding in descending (oldest to youngest) order. No new (updated) vaccine is administrated.
                            <br><br>
                            <u>Strategy 2</u><br>
                            Once available new (updated) vaccine is administered to everyone starting with oldest age group and proceeding in descending (oldest to youngest) order. No old vaccine is administered.
                            <br><br>
                            <u>Strategy 3</u><br>
                            Before the updated vaccine becomes available, the original vaccine is administered to the oldest eligible age groups proceeding in descending age order (oldest to youngest). Once the updated vaccine becomes available, vaccination switches to the updated vaccine, which is administered to individuals aged _49 years and younger_, again in descending age order. After all eligible individuals in the younger age groups have received the updated vaccine, vaccination resumes in the older age groups that have not yet been vaccinated, using the old vaccine.
                            <br><br>
                            <u>Strategy 4</u><br>
                            Before the updated vaccine becomes available, the original vaccine is administered to the youngest eligible age groups proceeding in ascending age order (youngest to oldest). Once the updated vaccine becomes available, vaccination switches to the updated vaccine, which is administered to individuals aged _50 years and above_, again in ascending age order. After all eligible individuals in the older age groups have received the updated vaccine, vaccination resumes in the youngest age groups that have not yet been vaccinated, using the old vaccine.
                            <br><br>
                            <u>Strategy 5</u><br>
                            The old vaccine is administered randomly to anyone eligible in the population
                            <br><br>
                            <u>Strategy 6</u><br>
                            Once the new vaccine is available the updated vaccine is administered randomly to anyone eligible in the population.
                            """)

    # Output panels
    with ui.nav_panel("Outputs"):

        # Nested panel for individual graph titles
        with ui.navset_tab(id="outputs_tabs"):

            # Within Simulation Overview
            with ui.nav_panel("Simulation Overview"):
                # Choice
                with ui.card():
                    choose_simulation_run('strategy')
                with ui.layout_columns(col_widths=[8, 4]):
                    # Graph
                    with ui.card():
                        ui.card_header("Status over time")
                        @render_plotly
                        def status_plot():
                            df_agg, df_sd_agg = agg_data()
                            return plot_track_status_plotly(df_agg, df_sd_agg)
                        ui.markdown(f"*{LEGEND_CAPTION}*")
                    # Status overview
                    with ui.layout_columns(col_widths=[12, 12]):
                        with ui.value_box(showcase=icon("skull"), theme="red"):
                            "Total deaths"
                            @render.text
                            def total_deaths_text():
                                agg = all_strategy_agg()
                                totals = get_strategy_totals(agg, input.strategy())
                                return f"{totals['total_deaths']:,.0f}"
                        with ui.value_box(showcase=icon("hospital"), theme="orange"):
                            "Total hospitalisations"
                            @render.text
                            def total_hosp_text():
                                agg = all_strategy_agg()
                                totals = get_strategy_totals(agg, input.strategy())
                                return f"{totals['total_hospitalised']:,.0f}"
                        with ui.value_box(showcase=icon("hourglass-half"), theme="blue"):
                            " Total years of life lost"
                            @render.text
                            def total_yll_text():
                                agg = all_strategy_agg_by_age()
                                df_agg = agg[input.strategy()]
                                yll = get_yll(df_agg)
                                return f"{yll:,.0f}"

            # Comparing across age
            with ui.nav_panel("Simulation Age Dynamics"):
                with ui.card():
                    choose_simulation_run('strategy_age')
                with ui.card():
                    ui.card_header("Dynamics within age groups")
                    ui.input_select("age_status", "Select status", choices=['S', 'AS', 'H', 'D'])
                    @render_plotly
                    def age_plot():
                        df_agg = age_agg_data()
                        return plot_age_dynamics_plotly(df_agg, input.age_status())
                    ui.markdown(f"*{LEGEND_CAPTION}*")

            # Comparing different Simulations
            with ui.nav_panel("Comparing Different Simulations"):
                with ui.card():
                    ui.card_header("Comparing different simulations")
                    ui.input_select("strategy_status", "Select status", choices=['S', 'AS', 'H', 'D'])
                    choose_multiple_simulations("strategies_to_compare")
                    @render_plotly
                    def strategy_plot():
                        agg = all_strategy_agg()
                        selected = list(input.strategies_to_compare())
                        return plot_strategy_comparison_plotly(agg, input.strategy_status(), strategies_to_plot=selected)


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
        #sim.save_csv()
    return sim

# Upload csv
@reactive.calc
def parsed_file():
    files: list[FileInfo] | None = input.csv_upload()
    if files is not None:
        means = {}
        stds = {}
        for file in files:
            if 'mean' in file['name']:
                name = file['name'].split('_mean')[0]
                means.update({name: pd.read_csv(file["datapath"])})
            elif 'std' in file['name']:
                name = file['name'].split('_std')[0]
                stds.update({name: pd.read_csv(file["datapath"])})
        return means, stds

# Aggregate data based on vaccine status
@reactive.calc
def agg_data():
    label = input.strategy()
    df_sum, df_sd = load_data(label)
    df_agg = aggregate_status(df_sum, group_cols=['t', 'vacc_status'])
    df_sd_agg = format_combined_sd(df_sd)
    return df_agg, df_sd_agg

# Aggregate data based on age groups
@reactive.calc
def age_agg_data():
    label = input.strategy_age()
    df_sum, _ = load_data(label)
    return aggregate_status(df_sum, group_cols=['t', 'ages'])

# Compare all strategy data
@reactive.calc
def all_strategy_agg():
    result = {}
    for label in run_names():
        df_sum, _ = load_data(label)
        result[label] = aggregate_status(df_sum, group_cols=['t'])
    return result

## Compare strategies by age
@reactive.calc
def all_strategy_agg_by_age():
    result = {}
    for label in run_names():
        df_sum, _ = load_data(label)
        result[label] = aggregate_status(df_sum, group_cols=['t', 'ages'])
    return result
