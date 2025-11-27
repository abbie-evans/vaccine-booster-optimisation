# File for parameters

class params:
    """Class containing all the general information."""
    
    age_groups = ['0-4', '5-9', '10-14', '15-19', 
                  '20-24', '25-29', '30-34', '35-39', 
                  '40-44', '45-49', '50-54', '55-59', 
                  '60-64', '65-69', '70-74', '75+']
    n_indivs_a = [5758, 6112, 5849, 5413, 
                  6011, 6698, 6828, 6691, 
                  6424, 6311, 6889, 6696, 
                  5769, 5015, 5021, 8515]
    
    @classmethod
    def access_age_groups(cls):
        """Method to access the age groups in this class, to then assign one of the age groups to a person."""
        return cls.age_groups