import matplotlib.pyplot as plt
import pandas as pd

# include a dropdown/selection with the lines they want to include in the plot
def load_status_data(sum_path='output/statusDF.csv'):
    df_sum = pd.read_csv(sum_path)
    #df_sd = pd.read_csv(sd_path)
    return df_sum, df_sd

STATUS_COLS = ['symptomatic', 'asymptomatic', 'hospitalised', 'dead']
RENAME = {'symptomatic': 'S', 'asymptomatic': 'AS', 'hospitalised': 'H', 'dead': 'D'}

def aggregate_status(df_sum, group_cols):
    """group_cols: list of columns to keep, e.g. ['t', 'vacc_status']
    or ['t', 'vacc_status', 'ages'] for the age-resolved version later."""
    return (
        df_sum.groupby(list(group_cols))[STATUS_COLS]
        .sum()
        .rename(columns=RENAME)
    )

def plot_track_status(df_agg, lines_to_plot=None, ax=None):
    df_plot = df_agg.unstack('vacc_status')

    if ax is None:
        fig, ax = plt.subplots(figsize=(10,6))
    else:
        fig = ax.figure
    
    all_statuses = ['S', 'AS', 'H', 'D']
    all_vacc = df_plot.columns.get_level_values('vacc_status').unique()

    if lines_to_plot is None:
        lines_to_plot = [(status, vacc) for status in all_statuses for vacc in all_vacc]
    
    for status, vacc in lines_to_plot:
        if (status, vacc) in df_plot.columns:
            ax.plot(df_plot.index, df_plot[(status, vacc)], label=f'{status} ({vacc})')
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Count')
    ax.legend()
    return fig
    



    
