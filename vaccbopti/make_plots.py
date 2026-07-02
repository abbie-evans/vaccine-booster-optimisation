import pandas as pd
import plotly.graph_objects as go
import os
import plotly.express as px
from natsort import natsorted

VIVID = px.colors.qualitative.Vivid

project_root = os.path.dirname(os.path.dirname(__file__))

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


def format_combined_sd(df_sd):
    """
    load df from std.csv
    set index to time and vaccstatus, and rename columns
    """
    df = df_sd.set_index(['t', 'vacc_status'])
    return df.rename(columns=RENAME)


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
        hovermode="x",
        xaxis_title='Time',
        yaxis_title='Count',
        legend=dict(groupclick='togglegroup'),
    )
    return fig


def plot_age_dynamics_plotly(df_agg, status, ages_to_plot=None):
    """
    df_agg: output of aggregate_status with group_cols=['t', 'ages']
    status: one of 'S', 'AS', 'H', 'D'
    ages_to_plot: list of age-group labels to include; None = all
    """
    df_plot = df_agg[status].unstack('ages')

    all_ages = natsorted(df_plot.columns)
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
        hovermode="x",
        yaxis_title=status,
        legend=dict(title='Age group', groupclick='togglegroup'),
    )
    return fig


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
        hovermode="x",
        yaxis_title=status,
        legend=dict(title='Strategy', groupclick='togglegroup'),
    )
    return fig


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


def get_yll(df_agg):
    '''
    df_agg: output of aggregate_status wit age groups
    yll: accessed from life_expectancy.csv, a local constants file
    '''
    yll_csv = pd.read_csv(f'{project_root}/vaccbopti/life_expectancy.csv')
    death_by_age = df_agg['D'].groupby('ages').sum()
    yll_nb = yll_csv.set_index('age_group').loc[death_by_age.index, 'YLL'].values * death_by_age.values
    return yll_nb.sum()
