# seir_sim.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Parameters (same as your R code) ---
initS = 100
initI = 10
beta = 0.5
gamma = 1/5    # E -> I rate per timestep
tau = 1/10     # I -> R rate per timestep
alpha = 1      # R -> S rate per timestep (1 means always return)
no_of_timesteps = 100

# --- Initialize population vector ---
# 0 = S, 1 = E, 2 = I, 3 = R
pop = np.concatenate([np.zeros(initS, dtype=int), np.ones(initI, dtype=int)])

# --- Prepare results table ---
sim_table = pd.DataFrame(index=range(no_of_timesteps),
                         columns=['Day', 'S', 'E', 'I', 'R'],
                         dtype=float)

# --- Simulation loop ---
n = len(pop)
for t in range(no_of_timesteps):
    day = t + 1
    # record counts
    sim_table.loc[t, 'Day'] = day
    sim_table.loc[t, 'S'] = np.sum(pop == 0)
    sim_table.loc[t, 'E'] = np.sum(pop == 1)
    sim_table.loc[t, 'I'] = np.sum(pop == 2)
    sim_table.loc[t, 'R'] = np.sum(pop == 3)

    # force of infection
    lam = beta * np.sum(pop == 2) / n

    # one uniform random draw per individual per event (same structure as R)
    rand_lambda = np.random.rand(n)
    rand_gamma = np.random.rand(n)
    rand_tau = np.random.rand(n)
    rand_alpha = np.random.rand(n)

    # iterate individuals (keeps same per-individual event order as your R code)
    for i in range(n):
        if pop[i] == 0:
            # S -> E (infection)
            if rand_lambda[i] < lam:
                pop[i] = 1
        if pop[i] == 1:
            # E -> I (latency ends)
            if rand_gamma[i] < gamma:
                pop[i] = 2
        if pop[i] == 2:
            # I -> R (recovery)
            if rand_tau[i] < tau:
                pop[i] = 3
        if pop[i] == 3:
            # R -> S (loss of immunity)
            if rand_alpha[i] < alpha:
                pop[i] = 0

# show results
print(sim_table)

# --- Plotting (similar to your R plot) ---
plt.figure(figsize=(8,5))
plt.plot(sim_table['Day'], sim_table['S'], label='S', color='black')
plt.plot(sim_table['Day'], sim_table['I'], label='I', color='red')
plt.plot(sim_table['Day'], sim_table['R'], label='R', color='blue')
plt.ylim(0, n)
plt.xlabel('Weeks')
plt.ylabel('# People')
plt.legend(loc='upper right')
plt.title('SEIR-like simulation')
plt.grid(False)
plt.tight_layout()
plt.show()

