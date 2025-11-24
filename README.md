# Vaccine Booster Optimisation

As observed during the COVID-19 pandemic, the emergence of new variants during infectious disease outbreaks has the potential to have devastating consequences, particularly if existing vaccines then offer reduced protection. When a variant of concern emerges, a crucial question for public health policy makers is whether to administer booster doses of the current vaccine (which was designed with an earlier variant in mind) or wait until an updated vaccine becomes available before deploying booster doses. Relatedly, pharmaceutical companies and vaccine manufacturers must decide whether it is worthwhile to update
existing vaccines.

This repository holds the code to a **stochastic, individual-based outbreak simulation model** that can be used to project numbers of cases and deaths during an outbreaks of a novel variant of SARS-CoV-2 under different vaccination strategies. This can be used to investigate scenarios in which it is beneficial to wait to update a variant-specific vaccine before undertaking booster vaccination and when it is instead preferable to use an existing vaccine (without a development delay).


## To Setup and Run the Model



## Background
 
 The model uses a set population of individuals (default is `100 000` individuals) with a global age distribution (based on UK values). This age distribution is separated into groups of every 5 years (0-4 years old, 5-9 years old, etc), in addition to 75+ years old. Each individual's immune status is tracked, which is conferred by infection and/or a booster vaccination. We assume each individual in the population has previously been vaccinated against and/or infected by a previous SARS-CoV-2 varient at least once over a two-year period before the start of the simulation. Additionally, we assume `2000` booster doses per day are administered, such that the entire population is vaccinated within 40 days, with a maximum vaccine uptake level of 80%.
 

 ### Infectiousness of the Variant

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

### Transmitting the Variant to Individuals

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

The immunity levels, $n_x$, from each source of immunity are tracked individually and are modelled using a biphasic exponentaion decay function:
```math
n_x(t) = n^0_x frac{ \exp(\pi_1\tau_x(t) + \pi_2t_s) + \exp(\pi_2\tau_x(t) + \pi_1t_s) }{ \exp(\pi_1\t_s) + \exp(\pi_2\t_s) }
```
where
- $t_s$ is the period of switching between the fast and slow decays (days)
- $\pi_1$ and $\pi_2$ rates for the initial period of fast or slow antibody decay, respectively (1/day)
- $n^0_x$ is the initial immunity level
  - $n^0_{v_1}$ is max immune recognition following vaccination with an existing vaccine
  - $n^0_{v_2}$ is max immune recognition following vaccination with an variant-adapted vaccine, which varies with vaccine efficacy ($\text{VE} = \frac{n^0_{v_2}}{n^0_{v_1}}$)
  - $n^0_{i}$ is max immune recognition following infection