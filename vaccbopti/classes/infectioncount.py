# FILE CONTAINING THE DATAFRAME OF INFECTIOUS PEOPE TO INITIALISE AT THE START OF THE MODEL.

# Important and useful modules
import pandas as pd
import numpy as np


# Define InfectionCount class
class InfectionCount:
    """Holds a dataframe of the number of people that are asymptomatic/symptomatic infected."""

    class __InfectionCount:
        """Inner singleton class containing the dataframe."""
        df_status = ['symptomatic',
                     'asymptomatic']
        count_df = pd.DataFrame(0,
                                index=np.arange(16),
                                columns=df_status)

    _instance = None

    def __init__(self):
        """Virtual private constructor to enforce singleton pattern."""
        if InfectionCount._instance is not None:
            raise RuntimeError("This class is a singleton!")

    @staticmethod
    def instance():
        """Creates singleton instance of __InfectionCount under _instance to access variables.
        Returns:
            __InfectionCount._instance: an instance of __InfectionCount to access the df
        """
        if not InfectionCount._instance:
            InfectionCount._instance = InfectionCount.__InfectionCount()
        return InfectionCount._instance
