# Class to store data output
import pandas as pd
from vaccbopti.classes.params import Params
params = Params.instance()

class Output:
    def __init__(self):
        self.tracked_status = ['symptomatic', 'hospitalised', 'dead']
        self.vacc_states = ['vacc', 'unvacc']
        self.statusDF = None
    
    def setdf(self):
        #pull column names
        columns = ['t']
        for age_group in params.age_groups:
            for status in self.tracked_status:
                for vacc_state in self.vacc_states:
                    columns.append(f'{age_group}_{status}_{vacc_state}')
        self.statusDF = pd.DataFrame(columns=columns)
    
    def initialise_df(self):
        self.setdf()
    
    def append_daily_nbs(self, t, People=People):
        row = {'t': t}
        for age_group in params.age_groups:
            for status in self.tracked_status:
                for vacc_state in self.vacc_states:
                    count = sum(1 for p in People 
                            if p.age_group == age_group 
                            and p.status == status 
                            and p.vacc_status == vacc_state)
                    row[f'{age_group}_{status}_{vacc_state}'] = count
        # append to df        
        self.statusDF = pd.concat([self.statusDF, pd.DataFrame([row])], ignore_index=True)