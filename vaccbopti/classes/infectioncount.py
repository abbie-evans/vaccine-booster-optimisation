# FILE CONTAINING THE DATAFRAME OF INDIVIDUALS TO INITIALISE AT THE START OF THE MODEL.

# Important and useful modules
import pandas as pd
import itertools
from .params import Params
params = Params.instance()


# Define InfectionCount class
class InfectionCount:
    """Holds a dataframe of the number of people that are asymptomatic/symptomatic infected."""

    def __init__(self):
        """Initialise the dataframe.
        
        Parameters
        ----------
        df_status : list
            Statuses that need to be included in the dataframe
        count_df : pd.DataFrame
            The dataframe of counts
        """
        self.vaccinated = ['unvaccinated', 'ex_vaccine', 'new_vaccine']
        self.df_status = ['symptomatic', 'asymptomatic', 'hospitalised', 'dead']
        self.index = list(itertools.product(*[params.age_groups, self.vaccinated]))
        self.index = pd.MultiIndex.from_tuples(self.index, names=["ages", "vacc_status"])
        self.count_df = pd.DataFrame(0, index=self.index, columns=self.df_status)
