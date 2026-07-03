# FILE FOR BOOSTER ADMINISTRATION CLASS

# Import useful modules
from .params import Params
import random
params = Params.instance()


# Define BoosterAdmin class
class BoosterAdmin:
    """A class representing how we'll administer vaccines to the popluation."""

    def __init__(self):
        """Initialise the BoosterAdmin class.
        Params:
            vacc_list (list): a lit of the people to be vaccinated"""
        self.vacc_list = []

    def update_susceptibility(self, vaccine_choice, person):
        """Vaccinates an individual (vacc_status to 'vacc' - old or new) and updates their immunity time (set to 0).
        This implies they will not be included in the list of people eligible for vaccination.
        Parameters:
            vaccine_choice: 'old_vacc' (existing vaccine) or 'new_vacc' (updated vaccine when it becomes available)
                            this will affect which immunity time variable is updated
        """
        if vaccine_choice == 'old_vacc':
            person.immunity_time_exvacc = 0
            person.vacc_status = 'old_vacc'
        elif vaccine_choice == 'new_vacc':
            person.immunity_time_newvacc = 0
            person.vacc_status = 'new_vacc'

    def vaccine_administration(self, People, vacc_amount, vaccine_choice, direction, age_targets):
        """Administers a vaccine to the population.
        - a list is created of all eligible individuals to be vaccinated
            - those who are not symptomatic, hospitalised, dead, vaccinated,
            - and they are 'eligible for vaccination' (person.vacc_status='unvacc')
            - ineligible refers to the 20% of the population that would not be vaccinated for various reasons
        - the list is randomised and resorted according to the vaccination strategy (param 'direction'):
            - descending: re-organise the list into descending age groups (from old to young)
            - ascending: re-organise the list into ascending age groups (young to old)
            - random: no re-organising
        - a sub-population of the list can be selected (param 'age_targets'):
            - mid-old: age groups 50-75+
            - mid-young: age groups 0-49
            - everyone: all age groups
        - the eligible to-be-vaccinated individuals are randomly selected, from 1000 per day to the remaining
          amount of individuals in the list available
        - finally, the vacc_status is changed using the update_susceptibility function.
        """
        # Step one - randomised list of eligible individuals
        self.vacc_list = [p for p in People
                          if p.status not in ['symptomatic', 'hospitalised', 'dead']
                          and p.vacc_status == 'unvacc']
        random.shuffle(self.vacc_list)  # shuffle the list
        # Step 2 - resort into age groups but still with the people shuffled
        if direction == 'descend':  # descend goes from old to young people
            self.vacc_list.sort(key=lambda p: params.age_groups.index(p.age_group), reverse=True)
        elif direction == 'ascend':  # ascend goes from young to old people
            self.vacc_list.sort(key=lambda p: params.age_groups.index(p.age_group))
        elif direction == 'random':  # in case we don't want to sort by age
            self.vacc_list = self.vacc_list
        # Step 3 - decide targets, eg. use all, 50+ (old groups), or 0-49 (young groups)
        if age_targets == 'everyone':
            self.vacc_list = self.vacc_list
        elif age_targets == 'mid-young':
            self.vacc_list = [p for p in self.vacc_list
                              if p.age_group in params.young_groups]
        elif age_targets == 'mid-old':
            self.vacc_list = [p for p in self.vacc_list
                              if p.age_group in params.old_groups]
        # Step 4 - select n_people of either total vaccine amount or the remaining unvacc
        limit = min(vacc_amount, len(self.vacc_list))
        self.vacc_indices = [self.vacc_list[i].id for i in range(limit)]
        # Step 5 - 'give vaccine' and update status
        for p in People:
            if p.id in self.vacc_indices:
                self.update_susceptibility(vaccine_choice, p)

    def vacc_strat_1(self, People, vacc_amount):
        """This vaccine strategy vaccinates everyone starting at the oldest age group and descending,
        not taking into account the availability of the updated vaccine.
        """
        self.vaccine_administration(People, vacc_amount,
                                    vaccine_choice='old_vacc', direction='descend', age_targets='everyone')

    def vacc_strat_2(self, People, vacc_amount, t, t_newvacc_avail):
        """This vaccine strategy vaccinates everyone starting at the oldest age group and descending,
        when the updated vaccine becomes available.
        """
        if t >= t_newvacc_avail:
            self.vaccine_administration(People, vacc_amount,
                                        vaccine_choice='new_vacc', direction='descend', age_targets='everyone')

    def vacc_strat_3(self, People, vacc_amount, t, t_newvacc_avail):
        """The third strategy starts vaccinating with the old vaccine from the oldest age groups and descending
        (from 75+ down), until the new vaccine becomes available. At this point, the new vaccine starting at
        the middle age groups is prioritised in a descending way (from 49 down). When all the updated vaccines
        have been administered, the old vaccination is continued in the older age groups.
        Parameters:
            t : time (in days)
            t_newvacc_avail : time when updated vaccine becomes available
        """
        if t < t_newvacc_avail:
            self.vaccine_administration(People, vacc_amount,
                                        vaccine_choice='old_vacc', direction='descend', age_targets='mid-old')
        elif t >= t_newvacc_avail:
            new_eligible = [p for p in People if p.status not in ['symptomatic', 'hospitalised', 'dead']
                            and p.vacc_status == 'unvacc'
                            and p.age_group in params.young_groups]
            if len(new_eligible) != 0:
                self.vaccine_administration(People, vacc_amount,
                                            vaccine_choice='new_vacc', direction='descend', age_targets='mid-young')
            elif len(new_eligible) == 0:
                self.vaccine_administration(People, vacc_amount,
                                            vaccine_choice='old_vacc', direction='descend', age_targets='mid-old')

    def vacc_strat_4(self, People, vacc_amount, t, t_newvacc_avail):
        """The fourth strategy starts vaccinating with the old vaccine to the youngest age groups ascending (0+ up),
        and switches to vaccinating from the middle age groups up (50+ and up) until all have been vaccinated with the
        updated vaccine. It then switches back to vaccinating the remaining individuals in the young age groups with the
        old vaccine.
        Parameters:
            t : time (in days)
            t_newvacc_avail : time when updated vaccine becomes available
        """
        if t < t_newvacc_avail:
            self.vaccine_administration(People, vacc_amount,
                                        vaccine_choice='old_vacc', direction='ascend', age_targets='mid-young')
        elif t >= t_newvacc_avail:
            new_eligible = [p for p in People if p.status not in ['symptomatic', 'hospitalised', 'dead']
                            and p.vacc_status == 'unvacc'
                            and p.age_group in params.old_groups]
            if len(new_eligible) != 0:
                self.vaccine_administration(People, vacc_amount,
                                            vaccine_choice='new_vacc', direction='ascend', age_targets='mid-old')
            elif len(new_eligible) == 0:
                self.vaccine_administration(People, vacc_amount,
                                            vaccine_choice='old_vacc', direction='ascend', age_targets='mid-young')

    def vacc_strat_5(self, People, vacc_amount):
        """The old vaccine is administered randomnly to anyone within the population."""
        self.vaccine_administration(People, vacc_amount,
                                    vaccine_choice='old_vacc', direction='random', age_targets='everyone')

    def vacc_strat_6(self, People, vacc_amount, t, t_newvacc_avail):
        """The updated vaccine is administered randomnly to anyone within the population when it becomes available.
        Parameters:
            t : time (in days)
            t_newvacc_avail : time when updated vaccine becomes available
        """
        if t >= t_newvacc_avail:
            self.vaccine_administration(People, vacc_amount,
                                        vaccine_choice='new_vacc', direction='random', age_targets='everyone')

