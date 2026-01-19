# FILE CONTAINING THE DATAFRAME OF INFECTIOUS PEOPE TO INITIALISE AT THE START OF THE MODEL.

# Important and useful modules
import pandas as pd
import numpy as np


# Define InfectionCount class
class InfectionCount:
    """Holds a dataframe of the number of people that are asymptomatic/symptomatic infected."""

    def __init__(self):
        """Initialise the dataframe.
        Parameters:
            df_status (list): status that need to be included in the dataframe
            count_df (df): the dataframe of counts"""
        self.df_status = ['symptomatic', 'asymptomatic']
        self.count_df = pd.DataFrame(0,
                                     index=np.arange(16),
                                     columns=self.df_status)
