import pandas as pd
import numpy as np

class InfectionCount:
    '''
    This class holds a dataframe with the number of people
    that are asymptomatic and symptomatic infected
    '''
    #create a dictionary which holds the statuses and the corresponding age groups (index of 16)

    def __init__(self):
        df_status = ['symptomatic','asymptomatic']
        self.count_df = pd.DataFrame(0, index=np.arange(16),columns=df_status)        
