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
R_{ab} = ( d^{(a)} + p(1-d^{(a)}) ) ( \frac{1}{\gamma}\overline{v}(t)\beta^{(a)}M_{ab} )
```

### Transmitting the Variant to Individuals

The probability that an individual is infected by the new variant is given by:
```math
P(i_\text{infected}) = 1 - \exp^{-v_i(t)\Delta^{(a)}}
```

The force of infection $\Delta$ in an age group, $a$, $\Delta^{(a)}$ is given by:
```math
\Delta^{(a)} = \beta^{(a)} \sum_{b=1}^{16} \frac{M_{ab}}{N_{(a)}} (I^{(b)} + pA^{(b)})
```