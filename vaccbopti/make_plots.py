# Import important modules
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from natsort import natsorted

# Global variables to manage settings for plots
VIVID = px.colors.qualitative.Vivid
project_root = os.path.dirname(os.path.dirname(__file__))

# Rename and map variables for user interface
STATUS_COLS = ['symptomatic', 'asymptomatic', 'hospitalised', 'dead']
RENAME = {'symptomatic': 'I', 'asymptomatic': 'A', 'hospitalised': 'H', 'dead': 'D'}
VACC_MAP = {'unvaccinated': 'unvaccinated',
            'ex_vaccine': 'vaccinated',
            'old_vaccine': 'vaccinated',
            'new_vaccine': 'vaccinated'}


def aggregate_status(df_sum, group_cols, pool_vacc=True, VACC_MAP=VACC_MAP):
    """
    Aggregate new and existing vaccination statuses together to mark all as 'vaccinated' and rename infected statuses.
    Parameters:
        group_cols: list of columns to keep, e.g. ['t', 'vacc_status']
        pool_vacc: if True, collapses ex_vaccine/new_vaccine into 'vaccinated'
    """
    df = df_sum.copy().reset_index()
    if pool_vacc and 'vacc_status' in df.columns:
        df['vacc_status'] = df['vacc_status'].map(VACC_MAP)
    return (df.groupby(list(group_cols))[STATUS_COLS].sum().rename(columns=RENAME))


def format_combined_sd(df_sd):
    """
    Format the aggregated standard deviation dateframe and rename infected statuses.
    Parameters:
        df_sd: the standard devation dataframe to format
    """
    df = df_sd.reset_index().set_index(['t', 'vacc_status'])
    return df.rename(columns=RENAME)


def plot_track_status_plotly(df_agg, df_sd_agg=None, lines_to_plot=None):
    """Makes the plot that tracks how many individuals enter each infected status per timepoint,
    separated by vaccinated and unvaccinated.
    Parameters:
        df_agg: the aggregated dataframe (merging age groups) with all the plotting values
        df_sd_agg: the aggregated dataframe (merging age groups) with the standard deviation
        lines_to_plot: list of status to plot, None = all"""
    # Format dataframes and list statuses to use
    df_plot = df_agg.unstack('vacc_status')
    df_sd_plot = df_sd_agg.unstack('vacc_status') if df_sd_agg is not None else None
    all_statuses = ['I', 'A', 'H', 'D']
    all_vacc = df_plot.columns.get_level_values('vacc_status').unique()
    # Default will plot everything
    if lines_to_plot is None:
        lines_to_plot = [(status, vacc) for status in all_statuses for vacc in all_vacc]
    # Render figure
    fig = go.Figure()
    colors = {'I': VIVID[0], 'A': VIVID[1], 'H': VIVID[2], 'D': VIVID[3]}
    # Add a line to show when the new vaccine is available
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
            fig.add_trace(go.Scatter(x=list(x) + list(x[::-1]),
                                     y=list(y + sd) + list((y - sd)[::-1]),
                                     fill='toself',
                                     fillcolor=color,
                                     opacity=0.15,
                                     line=dict(width=0),
                                     legendgroup=group,
                                     showlegend=False,
                                     hoverinfo='skip'))

        fig.add_trace(go.Scatter(x=x, y=y,
                                 mode='lines',
                                 name=f'{status} ({vacc})',
                                 legendgroup=group,
                                 legendgrouptitle_text=status,
                                 line=dict(color=color, dash='dash' if vacc == 'unvaccinated' else 'solid')))
    fig.update_layout(title='Status over time',
                      hovermode="x",
                      xaxis_title='Time',
                      yaxis_title='Count',
                      legend=dict(groupclick='togglegroup'))
    return fig


def plot_age_dynamics_plotly(df_agg, status, ages_to_plot=None):
    """Makes the plot that tracks how many individuals are in an infected status per timepoint by age-group.
    Parameters:
        df_agg: the aggregated dataframe (merging vaccination statuses) with all the plotting values
        status: which status to plot, of 'I', 'A', 'H', 'D'
        ages_to_plot: list of age-group labels to include; None = all
    """
    # Format dataframes and list ages to use
    df_plot = df_agg[status].unstack('ages')
    all_ages = natsorted(df_plot.columns)
    if ages_to_plot is None:
        ages_to_plot = all_ages
    # Render figure
    fig = go.Figure()
    for age in ages_to_plot:
        if age in df_plot.columns:
            fig.add_trace(go.Scatter(x=df_plot.index,
                                     y=df_plot[age],
                                     mode='lines',
                                     name=age,
                                     legendgroup=age))
    fig.update_layout(title=f'{status} by age group',
                      xaxis_title='Time',
                      hovermode="x",
                      yaxis_title=status,
                      legend=dict(title='Age group', groupclick='togglegroup'))
    return fig


def plot_strategy_comparison_plotly(strategy_agg, status, strategies_to_plot=None):
    """Makes the plot that tracks how many individuals are in an infected status per timepoint for each simulation.
    Parameters:
        df_agg: the aggregated dataframe (merging age groups and vaccination statuses) with all the plotting values
        status: which status to plot, of 'I', 'A', 'H', 'D'
        strategies_to_plot: list of strategy labels to include; None = all
    """
    # List strategies to use
    labels = strategies_to_plot if strategies_to_plot is not None else list(strategy_agg.keys())
    # Render figure
    fig = go.Figure()
    colors = VIVID
    for i, label in enumerate(labels):
        if label not in strategy_agg:
            continue
        df = strategy_agg[label]
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatter(x=df.index,
                                 y=df[status],
                                 mode='lines',
                                 name=f'Strategy {label}',
                                 legendgroup=f'strategy_{label}',
                                 legendgrouptitle_text=f'Strategy {label}',
                                 line=dict(color=color)))
    fig.update_layout(title=f'{status} across strategies',
                      xaxis_title='Time',
                      hovermode="x",
                      yaxis_title=status,
                      legend=dict(title='Strategy', groupclick='togglegroup'))
    return fig


def get_strategy_totals(strategy_agg, label):
    """Get the overall deaths and hospitalisations for a given strategy
    Parameters:
        df_agg: the aggregated dataframe (merging age groups and vaccination statuses) with all the plotting values
        label: which strategy to summarise
    Returns:
        dict with total deaths and hospitalisations across the whole trial
    """
    df = strategy_agg[label]
    return {'total_deaths': df['D'].sum(), 'total_hospitalised': df['H'].sum()}


def get_yll(df_agg):
    """Calculates the total number of years of life lost (YLL) for each strategy.
    Total YLL is given as the number of deaths for an age group multiplied by the years lost by dying at that age,
    (expected average lifespan - actual age of death).
    Parameters:
        df_agg: the aggregated dataframe (vaccination statuses) with all the plotting values
        yll: accessed from life_expectancy.csv, a local constants file
    """
    yll_csv = pd.read_csv(f'{project_root}/vaccbopti/life_expectancy.csv')
    death_by_age = df_agg['D'].groupby('ages').sum()
    yll_nb = yll_csv.set_index('age_group').loc[death_by_age.index, 'YLL'].values * death_by_age.values
    return yll_nb.sum()
