# Vaccine Booster Optimisation

As observed during the COVID-19 pandemic, the emergence of new variants during infectious disease outbreaks has the potential to have devastating consequences, particularly if existing vaccines then offer reduced protection. When a variant of concern emerges, a crucial question for public health policy makers is whether to administer booster doses of the current vaccine (which was designed with an earlier variant in mind) or wait until an updated vaccine becomes available before deploying booster doses. Relatedly, pharmaceutical companies and vaccine manufacturers must decide whether it is worthwhile to update
existing vaccines.

This repository holds the code to a **stochastic, individual-based outbreak simulation model** that can be used to project numbers of cases and deaths during an outbreaks of a novel variant of SARS-CoV-2 under different vaccination strategies. This can be used to investigate scenarios in which it is beneficial to wait to update a variant-specific vaccine before undertaking booster vaccination and when it is instead preferable to use an existing vaccine (without a development delay).


## To Setup and Run the Model

1. Download all the files in this repository.
2. Use `setup.py`.

## Background
 
 The model uses a set population of individuals (default is `100 000` individuals) with a global age distribution (based on UK values). This age distribution is separated into groups of every 5 years (0-4 years old, 5-9 years old, etc), in addition to 75+ years old. Each individual's immune status is tracked, which is conferred by infection and/or a booster vaccination. We assume each individual in the population has previously been vaccinated against and/or infected by a previous SARS-CoV-2 varient at least once over a two-year period before the start of the simulation. Additionally, we assume `2000` booster doses per day are administered, such that the entire population is vaccinated within 40 days, with a maximum vaccine uptake level of `80%`.

 As this is a stochastic individual-based model, the simulation is repeated `100` times, and the mean of these simulations is presented. Each simulation represents the dynamics over a given period such that one wave of the outbreak occurs.

 We consider the effect on the number of deaths and the years of life lost (YLL) due to premature mortality, given the level of protection of the variant-adapted vaccine against infection and hospitalisation, for a period of one year following variant emergence.
 

 ### Modelling the Infectiousness of the Variant

 At the start of the model, `100` random indiviuals are infected with the novel variant. 

The variant has an effective reproduction number $R_e$, or the transmissibility of the novel variant at the beginning of each simulation, accounting for the immunity and susceptibility of the host population at the time, $\beta$. The simulation period is then adapted given a value of $R_e$, such that for `t = 1 year`, $R_e=1.5$, and for `t = 185 days`, $R_e=3$.

$R_e$ is calculated by finding the largest eigenvalue from the next-generation matrix with entries $R_{ab}$.
```math
R_{ab} = \left( d^{(a)} + p(1-d^{(a)}) \right) \left( \frac{1}{\gamma}\overline{v}(t)\beta^{(a)}M_{ab} \right)
```
where:
- $d^{(a)}$ is the probability that a vaccinated infected indivudal in age group $a$ develops symptoms
- $p$ is the infectiousness of an asymptomatic infected individual, relative to a symptomatic infected individual
- $1/\gamma$ is the mean infectious period
- $\overline{v}(t)$ is the average susceptibility of the whole population to the new variant at the start of the simulation
- $\beta^{(a)}$ is the infection rate parameter, reflecting the susceptibility of individuals in age group $a$
- $M_{ab}$ is the mean daily number of contacts that an individual in age group $b$ has with an individual age group $a$


### Modelling the Transmission of the Variant

The probability that an individual is infected by the new variant is dependent on the force of infection and relative susceptibility, given by:
```math
P(i_\text{infected}) = 1 - \exp^{-v_i(t)\Delta^{(a)}}
```

The force of infection $\Delta$ in an age group, $a$, $\Delta^{(a)}$ is given by:
```math
\Delta^{(a)} = \beta^{(a)} \sum_{b=1}^{16} \frac{M_{ab}}{N_{(a)}} \left(I^{(b)} + pA^{(b)} \right)
```
where
- $\beta^{(a)}$, $M_{ab}$, and $p$ are defined as above
- $N_{(a)}$ is the number of individuals in age group $a$
- $I^{(b)}$ and $A^{(b)}$ are the numbers of individuals in group $b$ that are infectious symptomatic and asymptomatic, relatively

A 'susceptible' individual refers to individuals who are partially susceptibile, where the level of susceptibility is determined by their immune status. The relative susceptibility of an individual is given by:
```math
v_i(t) = 1 - \text{max} \left[ f_1(\tau_1(t)), f_2(\tau_2(t)), f_3(\tau_3(t)) \right]
```
where each function $f_x(\tau_x(t))$ is a possible source of immunity for each individual, and $\tau_x(t)$ is the time since receiving this source of immunity, and where $x={1,2,3}$, represents vaccination with an existing vaccine, vaccination with a variant-adapted vaccine, and infection with the novel variant, respectively. 

A logistic relationship is assumed between the immunity level and the protection against infection with the novel variant and hospitalisation, where:
```math
f_x(\tau_x(t)) = \frac{1}{ 1 + \exp[ -k (\log_{10}(n_x) - \log_{10}(n_{50_m}) ) ]}
```
and
- $k$ is the shape parameter
- $n_{50_m}$ is the immunity level at which 50% protection is conferred, where $m={1,2}$ and represents infection and hospitalisation/death, respectively

The immunity levels, $n_x$, from each source of immunity are tracked individually and are modelled using a biphasic exponentaion decay function, to model the waning immunity seen in individuals given previous infection and vaccination:
```math
n_x(t) = n^0_x \frac{ \exp(\pi_1\tau_x(t) + \pi_2t_s) + \exp(\pi_2\tau_x(t) + \pi_1t_s) }{ \exp(\pi_1t_s) + \exp(\pi_2t_s) }
```
where
- $t_s$ is the period of switching between the fast and slow decays (days)
- $\pi_1$ and $\pi_2$ rates for the initial period of fast or slow antibody decay, respectively (1/day)
- $n^0_x$ is the initial immunity level
  - $n^0_{v_1}$ is max immune recognition following vaccination with an existing vaccine
  - $n^0_{v_2}$ is max immune recognition following vaccination with an variant-adapted vaccine, which varies with vaccine efficacy, VE
  - $\text{VE} = \frac{n^0_{v_2}}{n^0_{v_1}}$
  - $n^0_{i}$ is max immune recognition following infection


### Modelling Patient Behaviour Once Exposed

Once an individual is exposed:
- the latent period, or the time between when a person is infected and when they become infectious, $t^*_L$ is drawn from a gamma distribution
  - $L_k = \int_{k-1}^{k+1} (1 - |u-k|)g(u) du$
  - with $k$ days following exposure, chosen such that $k=1$ gives a valid distribution for $L_1$
  - the mean latent period is given as $1/\alpha$ 
- after the latent period is finished, a sample is taken to determine whether the patient is either symptomatic or asymptomatic infectious
  - given as age-dependent probability $d^{(a)}$

If a patient is symptomatic infectious:
- their infectious period is given by a gamma distribution $L_k = \int_{k-1}^{k+1} (1 - |u-k|)g(u) du$
  - the mean infectious period is given by $1/\gamma$
- a sample is taken to determine if they are hospitalised, $P_{IH}(t)$
  - a time is sampled $t^*_H$ from a Weibull distribution which determines the time they were hospitalised
- a further sample is then taken to determine if they die as a result $P_{HD}(t)$
-  a time is sampled $t^*_D$ from a gamma distribution which determines the time they died after hospitalisation

Individuals who remain asymptomatic throughout infection and those who have an infectious period will only recover and transition to being susceptible after their infectious period. Individuals who die are removed from the population after time of death.


### Summary of Parameters
| Parameter | Definition | Value |
| --------- | ---------- | ----- |
| $d^{(a)}$ | probability that a vaccinated infected individual in age group $a$ develops symptoms | [0.068, 0.015, 0.021, 0.026, 0.067, 0.098, 0.104, 0.094, 0.101, 0.125, 0.193, 0.261, 0.293, 0.539, 0.633, 0.678] | 
| $p$ | infectiousness of an asymptomatic infected individual, relative to a symptomatic infected individual | 0.255 | 
| $1/\gamma$ | mean infectious period (days) | 9 | 
| $\overline{v}(t)$ | average susceptibility of the whole population to the new variant at the start of the simulation | calculated at the start of the simulation | 
| $\beta^{(a)}$ | infection rate parameter, reflecting the susceptibility of individuals in age group $a$ (per day) | [0.186, 0.108, 0.122, 0.131, 0.185, 0.213,  0.217, 0.210, 0.215, 0.233, 0.272, 0.305, 0.318, 0.397, 0.422, 0.430] |
| $M_{ab}$ | mean daily number of contacts that an individual in age group $b$ has with an individual age group $a$ | contact matrix for UK |
| $N_{(a)}$ | the number of individuals in age group $a$ | [5758, 6112, 5849, 5413, 6011, 6698, 6828, 6691, 6424, 6311, 6889, 6696, 5769, 5015, 5021, 8515] |
| $I^{(b)}$ | numbers of individuals in group $b$ that are infectious symptomatic | cacluated at the start of the simulation |
| $A^{(b)}$ | numbers of individuals in group $b$ that are infectious asymptomatic | calculated at the start of the simulation |
| $k$ | shape parameter linking immunity level and protection against infection/hospitality | 0.25 |
| $n_{50_1}$ | immunity level at which 50% protection is conferred against infection | 0.091 |
| $n_{50_2}$ | immunity level at which 50% protection is conferred against hospitalisation and death | 0.021 |
| $t_s$ | period of switching between the fast and slow decays (days) | 75 |
| $\pi_1$ | rates for the initial period of fast antibody decay (1/day) | $-\frac{log(2)}{35}$ |
| $\pi_2$ | rates for the initial period of slow antibody decay (1/day) | $-\frac{log(2)}{1000}$ |
| $n^0_{v_1}$ | max immune recognition following vaccination with an existing vaccine | 0.22 |
| $n^0_{v_2}$ | max immune recognition following vaccination with an variant-adapted vaccine | 0.44 |
| $n^0_{i}$ | max immune recognition following infection | 0.66 |
| $1/\alpha$ | the mean latent period (days) | 5 |
| $P_{IH}(t)$ | probability that an unvaccinated symptomatic infected individual in age group $a$ is hospitalised | [0.011, 0.011, 0.006, 0.005, 0.004, 0.003, 0.004, 0.006, 0.008, 0.011, 0.011, 0.01, 0.014, 0.016, 0.016, 0.017] |
| $P_{HD}(t)$ | probability that an unvaccinated hospitalised individual in age group $a$ dies | [0.001, 0.001, 0.014, 0.008, 0.009, 0.019, 0.017, 0.019, 0.028, 0.031, 0.047, 0.085, 0.146, 0.137, 0.246, 0.445] | 