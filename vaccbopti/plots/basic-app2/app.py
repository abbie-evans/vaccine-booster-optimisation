from shiny import render, ui
from shiny.express import input
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from shiny import render, ui, reactive
from shiny.express import input
from shinywidgets import render_plotly
import glob, re, os
from shiny.express import render, ui
from faicons import icon_svg as icon

## setup
import plotly.express as px

VIVID = px.colors.qualitative.Vivid

#to rename them
STATUS_COLS = ['symptomatic', 'asymptomatic', 'hospitalised', 'dead']
RENAME = {'symptomatic': 'S', 'asymptomatic': 'AS', 'hospitalised': 'H', 'dead': 'D'}

#to pool vacc status
VACC_MAP = {
    'unvaccinated': 'unvaccinated',
    'old_vaccine': 'vaccinated',
    'new_vaccine': 'vaccinated'}

def load_status_data(sum_path, sd_path=None):
    df_sum = pd.read_csv(sum_path)
    df_sd = pd.read_csv(sd_path) if sd_path else None
    return df_sum, df_sd


def aggregate_status(df_sum, group_cols, pool_vacc=True):
    """
    group_cols: list of columns to keep, e.g. ['t', 'vacc_status']
    pool_vacc: if True, collapses old_vaccine/new_vaccine into 'vaccinated'
    """
    df = df_sum.copy()

    if pool_vacc and 'vacc_status' in df.columns:
        df['vacc_status'] = df['vacc_status'].map(VACC_MAP)

    return (
        df.groupby(list(group_cols))[STATUS_COLS]
        .sum()
        .rename(columns=RENAME)
    )

def aggregate_status_sd(df_sd, group_cols, pool_vacc=True):
    """
    Same grouping as aggregate_status, but correctly pools SD by
    converting to variance, summing, then converting back: sqrt(sum(sd^2))
    """
    df = df_sd.copy()

    if pool_vacc and 'vacc_status' in df.columns:
        df['vacc_status'] = df['vacc_status'].map(VACC_MAP)

    var_df = df.copy()
    var_df[STATUS_COLS] = df[STATUS_COLS] ** 2

    return (
        var_df.groupby(list(group_cols))[STATUS_COLS]
        .sum()
        .pow(0.5)
        .rename(columns=RENAME)
    )

def plot_track_status_plotly(df_agg, df_sd_agg=None, lines_to_plot=None):
    df_plot = df_agg.unstack('vacc_status')
    df_sd_plot = df_sd_agg.unstack('vacc_status') if df_sd_agg is not None else None

    all_statuses = ['S', 'AS', 'H', 'D']
    all_vacc = df_plot.columns.get_level_values('vacc_status').unique()

    if lines_to_plot is None:
        lines_to_plot = [(status, vacc) for status in all_statuses for vacc in all_vacc]

    fig = go.Figure()
    colors = {'S': VIVID[0], 'AS': VIVID[1], 'H': VIVID[2], 'D': VIVID[3]}

    for status, vacc in lines_to_plot:
        if (status, vacc) not in df_plot.columns:
            continue

        x = df_plot.index
        y = df_plot[(status, vacc)]
        color = colors.get(status, 'gray')
        group = f"{status}"  # group by status, so vacc/unvacc nest under one legend header

        # SD shaded band, drawn first so the line sits on top
        if df_sd_plot is not None and (status, vacc) in df_sd_plot.columns:
            sd = df_sd_plot[(status, vacc)]
            fig.add_trace(go.Scatter(
                x=list(x) + list(x[::-1]),
                y=list(y + sd) + list((y - sd)[::-1]),
                fill='toself',
                fillcolor=color,
                opacity=0.15,
                line=dict(width=0),
                legendgroup=group,
                showlegend=False,
                hoverinfo='skip',
            ))

        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines',
            name=f'{status} ({vacc})',
            legendgroup=group,
            legendgrouptitle_text=status,
            line=dict(color=color, dash='dash' if vacc == 'unvaccinated' else 'solid'),
        ))

    fig.update_layout(
        title='Status over time',
        xaxis_title='Time',
        yaxis_title='Count',
        legend=dict(groupclick='togglegroup'),
    )
    return fig

# PLOT 2: looking at different age groups
# input: which strategy + drop-down menu of which var (AS,S,H,D)
# clickable legend of age groups
def plot_age_dynamics_plotly(df_agg, status, ages_to_plot=None):
    """
    df_agg: output of aggregate_status with group_cols=['t', 'ages']
    status: one of 'S', 'AS', 'H', 'D'
    ages_to_plot: list of age-group labels to include; None = all
    """
    df_plot = df_agg[status].unstack('ages')

    all_ages = list(df_plot.columns)
    if ages_to_plot is None:
        ages_to_plot = all_ages

    fig = go.Figure()

    for age in ages_to_plot:
        if age in df_plot.columns:
            fig.add_trace(go.Scatter(
                x=df_plot.index,
                y=df_plot[age],
                mode='lines',
                name=age,
                legendgroup=age,
            ))

    fig.update_layout(
        title=f'{status} by age group',
        xaxis_title='Time',
        yaxis_title=status,
        legend=dict(title='Age group', groupclick='togglegroup'),
    )
    return fig

# PLOT 3: comparing different strategies
# pooled across vacc/unvacc
# input: select which strategies
# clickable legend: subheader (strat 1; AS,S,D,H, strat2: ...)
def plot_strategy_comparison_plotly(strategy_agg, status, strategies_to_plot=None):
    """
    strategy_agg: dict {strategy_label: df_agg}, df_agg indexed by t with columns S/AS/H/D
    status: one of 'S', 'AS', 'H', 'D'
    strategies_to_plot: list of strategy labels to include; None = all
    """
    labels = strategies_to_plot if strategies_to_plot is not None else list(strategy_agg.keys())

    fig = go.Figure()
    colors = VIVID

    for i, label in enumerate(labels):
        if label not in strategy_agg:
            continue
        df = strategy_agg[label]
        color = colors[i % len(colors)]

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[status],
            mode='lines',
            name=f'Strategy {label}',
            legendgroup=f'strategy_{label}',
            legendgrouptitle_text=f'Strategy {label}',
            line=dict(color=color),
        ))

    fig.update_layout(
        title=f'{status} across strategies',
        xaxis_title='Time',
        yaxis_title=status,
        legend=dict(title='Strategy', groupclick='togglegroup'),
    )
    return fig

# VIS 4: numbers across strategies
# select a strategy, then display the total deaths and hospitalisations for that strategy
# input: which strategy
def get_strategy_totals(strategy_agg, label):
    """
    strategy_agg: dict {strategy_label: df_agg}, df_agg indexed by t with columns S/AS/H/D
    label: which strategy to summarise
    Returns dict with total deaths and hospitalisations across the whole trial
    """
    df = strategy_agg[label]
    return {
        'total_deaths': df['D'].sum(),
        'total_hospitalised': df['H'].sum(),
    }



## plot plotl

# discover available strategy files
# need to update this path to general location
strategy_dir = '/home/bentevissel/vaccine-booster-optimisation/outputs'
mean_files = sorted(glob.glob(f'{strategy_dir}/output_mean_strategy_*.csv'))
strategy_labels = [re.search(r'strategy_(.+)\.csv', f).group(1) for f in mean_files]

## a bit roundabout but explain legend
LEGEND_CAPTION = " · ".join(f"{short} = {full}" for full, short in RENAME.items())

## reactive plots
@reactive.calc
def agg_data():
    label = input.strategy()
    sum_path = f'{strategy_dir}/output_mean_strategy_{label}.csv'
    sd_path = f'{strategy_dir}/output_std_strategy_{label}.csv'
    df_sum, df_sd = load_status_data(sum_path, sd_path)
    df_agg = aggregate_status(df_sum, group_cols=['t', 'vacc_status'])
    df_sd_agg = aggregate_status_sd(df_sd, group_cols=['t', 'vacc_status'])
    return df_agg, df_sd_agg


@reactive.calc
def age_agg_data():
    label = input.strategy()
    sum_path = f'{strategy_dir}/output_mean_strategy_{label}.csv'
    df_sum, _ = load_status_data(sum_path)
    return aggregate_status(df_sum, group_cols=['t', 'ages'])

@reactive.calc
def all_strategy_agg():
    result = {}
    for label in strategy_labels:
        sum_path = f'{strategy_dir}/output_mean_strategy_{label}.csv'
        df_sum, _ = load_status_data(sum_path)
        result[label] = aggregate_status(df_sum, group_cols=['t'])
    return result

## lay out 
with ui.panel_conditional("input.main_tabs != 'Strategy comparison'"):
    with ui.card():
        ui.input_select("strategy", "Select strategy", choices=strategy_labels)

## WIP TABBED
with ui.navset_card_tab(id="main_tabs"):
    with ui.nav_panel("Within-strategy dynamics"):
        with ui.layout_columns(col_widths=[8, 4]):
            with ui.card():
                ui.card_header("Status over time")

                @render_plotly
                def status_plot():
                    df_agg, df_sd_agg = agg_data()
                    return plot_track_status_plotly(df_agg, df_sd_agg)

                ui.markdown(f"*{LEGEND_CAPTION}*")

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

    with ui.nav_panel("Age dynamics"):
        with ui.card():
            ui.card_header("Dynamics within age groups")
            ui.input_select("age_status", "Select variable", choices=['S', 'AS', 'H', 'D'])

            @render_plotly
            def age_plot():
                df_agg = age_agg_data()
                return plot_age_dynamics_plotly(df_agg, input.age_status())

            ui.markdown(f"*{LEGEND_CAPTION}*")

    with ui.nav_panel("Strategy comparison"):
        with ui.card():
            ui.card_header("Comparing strategies")
            ui.input_select("strategy_status", "Select variable", choices=['S', 'AS', 'H', 'D'])
            ui.input_selectize(
                "strategies_to_compare", "Select strategies",
                choices=strategy_labels, multiple=True,
                selected=strategy_labels
            )

            @render_plotly
            def strategy_plot():
                agg = all_strategy_agg()
                selected = list(input.strategies_to_compare())
                return plot_strategy_comparison_plotly(agg, input.strategy_status(), strategies_to_plot=selected)