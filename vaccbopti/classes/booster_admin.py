# File for booster administration class

# user input:
# - efficiency of vaccine
# - used strategy
# - amount of people vaccinated each day

#define the actual strategies
#using calc_susceptibility
# strategy determines how many people we pick from each agegroup
# sub_group of people who are eligible
# 1000 people are offered vacc each day
# 


from vaccbopti.classes.person import Person
from vaccbopti.classes.params import Params
# from vaccbopti.classes.timesteps import People
import random as rd
import numpy as np

params = Params.instance()



class BoosterAdmin:
    def __init__(self):
        self.vacc_list = []
        self.vacc_indices = []

    def update_susceptibility(self, vaccine_choice, person):
        ''' 
        An individual's status is changed to 'vacc' (vaccinated), and their immunity_time
        is set to 0 (if given the old vaccine, immunity_time_exvacc, if new vaccine, immunity_time_newvacc).
        This implies they will not be included in the list of people eligible for vaccination.
        vaccine_choice: 'old_vacc' (existing vaccine) or 'new_vacc' (updated vaccine when it becomes available).
        '''
        # access calc_suceptibility
        if vaccine_choice == 'old_vacc':
            person.immunity_time_exvacc = 0
            person.vacc_status = 'vacc'
        elif vaccine_choice == 'new_vacc':
            person.immunity_time_newvacc = 0
            person.vacc_status = 'vacc'
    
    #need to change 'person.' to the correct word 
    # we now have a unique ID for each person in People
    def vaccine_administration(self, People, vaccine_choice, direction, age_targets, vacc_amount=1000):
        ''' 
        In this function, a list is created of all eligible individuals to be vaccinated (those who are
        symptomatic, hospitalised, dead, vaccinated, or not 'eligible for vaccination' (person.vacc_status='unvacc')). 
        Uneligible refers to the 20% of the population that would not be vaccinated for various reasons.
        The list is randomised and resorted according to the vaccination strategy (param 'direction'):
        - descending: re-organise the list into descending age groups (from old to young)
        - ascending: re-organise the list into ascending age groups (young to old)
        - random: no re-organising.
        A sub-population of the list can be selected (param 'age_targets'):
        - mid-old: age groups 50-75+
        - mid-young: age groups 0-49
        - everyone: all age groups
        The to-be-vaccinated individuals are randomly selected, from 1000 per day to the remaining
        amount of individuals in the list available.
        Finally, the vacc_status is changed using the update_susceptibility function.
        '''
        self.vacc_list = [p for p in People 
                          if p.status not in ['symptomatic', 'hospitalised', 'dead'] 
                          and p.vacc_status == 'unvacc']
        #shuffle the list
        rd.shuffle(self.vacc_list)

        # then resort it into age groups but with the people shuffled
        # descend goes from old to young people
        if direction == 'descend':
            self.vacc_list.sort(key=lambda p: params.age_groups.index(p.age_group), reverse=True)
        # ascend goes from young to old people
        elif direction == 'ascend':
            self.vacc_list.sort(key=lambda p: params.age_groups.index(p.age_group))
        # in case we don't want to sort by age
        elif direction == 'random':
            self.vacc_list = self.vacc_list

        # decide if you want to use all, 50+ (old groups), or 49- (young groups)
        if age_targets == 'everyone':
            self.vacc_list = self.vacc_list
        elif age_targets == 'mid-young':
            self.vacc_list = [p for p in self.vacc_list
                 if p.age_group in params.young_groups]
        elif age_targets == 'mid-old':
            self.vacc_list = [p for p in self.vacc_list
                 if p.age_group in params.old_groups]

        # select either 1000 or the length of the remaining unvaccinated people
        limit = min(vacc_amount, len(self.vacc_list))
        self.vacc_indices = [self.vacc_list[i].id for i in range(limit)]
        
        # 'give vaccine' and update status
        for p in People:
            if p.id in self.vacc_indices:
                # change old_vacc -> vaccine_choice
                self.update_susceptibility(vaccine_choice, p)
    
    def vacc_strat_1(self, People):
        '''
        This vaccine strategy vaccinates everyone starting at the oldest age group and descending,
        not taking into account the availability of the updated vaccine.

        '''
        self.vaccine_administration(People, vaccine_choice='old_vacc',direction='descend',age_targets='everyone')

    def vacc_strat_2(self, People, t, t_newvacc_avail):
        '''
        This vaccine strategy vaccinates everyone starting at the oldest age group and descending,
        when the updated vaccine becomes available.
        '''
        if t > t_newvacc_avail:
            self.vaccine_administration(People, vaccine_choice='new_vacc', direction='descend',age_targets='everyone')
    
    def vacc_strat_3 (self, People, t, t_newvacc_avail):
        '''
        The third strategy starts vaccinating with the old vaccine from the oldest age groups and descending 
        (from 75+ down), until the new vaccine becomes available. At this point, the new vaccine starting at 
        the middle age groups is prioritised in a descending way (from 49 down). When all the updated vaccines
        have been administered, the old vaccination is continued in the older age groups.

        t : time (in days)
        t_newvacc_avail : time when updated vaccine becomes available
        '''
        if t < t_newvacc_avail:
            self.vaccine_administration(People, vaccine_choice='old_vacc',direction='descend',age_targets='mid-old')
        elif t > t_newvacc_avail:
            self.vaccine_administration(People, vaccine_choice='new_vacc', direction='descend',age_targets='mid-young')
        elif len(self.vacc_list) == 0:
            self.vaccine_administration(People, vaccine_choice='old_vacc',direction='descend',age_targets='mid-old')
    
    def vacc_strat_4(self, People, t, t_newvacc_avail):
        '''
        The fourth strategy starts vaccinating with the old vaccine to the youngest age groups ascending (0+ up),
        and switches to vaccinating from the middle age groups up (50+ and up) until all have been vaccinated with the 
        updated vaccine. It then switches back to vaccinating the remaining individuals in the young age groups with the 
        old vaccine.
        
        t : time (in days)
        t_newvacc_avail : time when updated vaccine becomes available

        '''
        if t < t_newvacc_avail:
            self.vaccine_administration(People, vaccine_choice='old_vacc',direction='ascend',age_targets='mid-young')
        elif t > t_newvacc_avail:
            self.vaccine_administration(People, vaccine_choice='new_vacc', direction='ascend', age_targets='mid-old')
        elif len(self.vacc_list) == 0:
            self.vaccine_administration(People, vaccine_choice='old_vacc', direction='ascend', age_targets='mid-young')
    
    def vacc_strat_5(self, People):
        ''' 
        The old vaccine is administered randomnly to anyone within the population.
        '''
        self.vaccine_administration(People, vaccine_choice='old_vacc',direction='random',age_targets='everyone')
    
    def vacc_strat_6(self, People,t, t_newvacc_avail):
        ''' 
        The updated vaccine is administered randomnly to anyone within the population when it becomes available.

        t : time (in days)
        t_newvacc_avail : time when updated vaccine becomes available

        '''
        if t > t_newvacc_avail:
            self.vaccine_administration(People, vaccine_choice='new_vacc',direction='random',age_targets='everyone')

