=============================
Vaccine Booster Optimisation
=============================

As observed during the COVID-19 pandemic, the emergence of new variants during infectious disease outbreaks has the potential to have devastating consequences, particularly if existing vaccines then offer reduced protection. When a variant of concern emerges, a crucial question for public health policy makers is whether to administer booster doses of the current vaccine (which was designed with an earlier variant in mind) or wait until an updated vaccine becomes available before deploying booster doses. Relatedly, pharmaceutical companies and vaccine manufacturers must decide whether it is worthwhile to update existing vaccines.

This repository holds the code to a **stochastic, individual-based outbreak simulation model** that can be used to project numbers of cases and deaths during an outbreak of a novel variant of SARS-CoV-2 under different vaccination strategies. This can be used to investigate scenarios in which it is beneficial to wait to update a variant-adapted vaccine before undertaking booster vaccination and when it is instead preferable to use an existing vaccine (without a development delay).
 
Local Installation
-------------------
1. Download all the files in this repository to your local machine.
2. Open in the terminal the folder ``vaccine-booster-optimisation`` and ensure you have your Python virtual environment running
3. Run ``pip install .``
4. Run ``python vaccbopti/app.py``

Background
--------------
This is a stochastic individual-based model, the simulation is repeated `100` times, and the mean of these simulations is presented. Each simulation represents the dynamics over a given period such that one wave of the outbreak occurs. The model uses a set population of individuals (default is `100 000` individuals) with a global age distribution (based on UK values). This age distribution is separated into groups of every 5 years (0-4 years old, 5-9 years old, etc), in addition to 75+ years old. Each individual's immune status is tracked, which is conferred by infection and/or a booster vaccination. We assume each individual in the population has previously been vaccinated against and/or infected by a previous SARS-CoV-2 variant at least once over a two-year period before the start of the simulation, giving them some level of immunity. 

The user has an option of 7 different booster administration strategies. If a booster vaccine is administered to the population, we assume a set amount per day is given out (default is `2000` such that the entire population is vaccinated within 40 days), with a maximum vaccine uptake level of `80%`.

* Strategy 0: Doesn't apply booster vaccines
* Strategy 1: Vaccinates everyone using an existing vaccine (not updated for the novel variant), starting at the oldest age group and descending.
* Strategy 2: Vaccinates everyone starting at the oldest age group and descending, once the updated variant-adapted vaccine becomes available.
* Strategy 3: Starts vaccinating with the existing vaccine from the oldest age groups (from 75+ down), until the new variant-adapted vaccine becomes available. Then, the new variant-adapted vaccine is administered in the middle groups (from 49 down). When all the updated vaccines have been administered, vaccination with the existing vaccine is continued in the older age groups.
* Strategy 4: Starts vaccinating with the existing vaccine from the youngest age groups (0+ up). Switches to vaccinating from the middle age groups up (50+ and up) until all have been vaccinated with the updated variant-adapted vaccine. It then switches back to vaccinating the remaining individuals in the young age groups with the existing vaccine.
* Strategy 5: The existing vaccine is administered randomly to individuals within the population.
* Strategy 6: The updated variant-adapted vaccine is administered randomly to individuals within the population when it becomes available.

We consider the effect of the vaccine booster administration strategy on the number of deaths and the years of life lost (YLL) due to premature mortality, given the level of protection of the variant-adapted vaccine against infection and hospitalisation, for a period of one year following variant emergence.

Running a simulation
--------------------
You can use our user interface to configure the parameters and run a simulation.
