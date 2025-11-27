import pandas as pd
import numpy as np


class InfectionCount:
    '''
    This class holds a dataframe with the number of people
    that are asymptomatic and symptomatic infected
    '''
    class __InfectionCount:
    #create a dictionary which holds the statuses and the corresponding age groups (index of 16)

        df_status = ['symptomatic',
                     'asymptomatic']
        count_df = pd.DataFrame(0,
                                index=np.arange(16),
                                columns=df_status)

    _instance = __InfectionCount

    def __init__(self):
        """Virutal private constructor to enforce singleton pattern."""
        if InfectionCount._instance is not None:
            raise RuntimeError("This class is a singleton!")

    @staticmethod
    def instance():
        """Creates singleton instance of __Parameters under
        _instance if one doesn't already exist.

        Returns
        -------
        __Parameters
            An instance of the __Parameters class

        """
        if not InfectionCount._instance:
            raise RuntimeError("Config file hasn't been set")
        return InfectionCount._instance
