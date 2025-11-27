# File for person class

class Person:
    def __init__(self):
        self.age_group = None
        self.status = 'susceptible' #susceptible, exposed, infectious symptomatic, infectious asymptomatic, hospitalised, dead
    def get_age_group(self, n):
        self.age_group = params.access_age_groups()[n]
    def calc_susceptibility():
        susceptibility = 1 - max(calc_fx(), calc_fx(), calc_fx())
        return susceptibility
    def calc_fx()
        
        return f_x