#This is the code which is used to run the genetic algorithm for the optimization of the fluidic pinball actuation
# After running this part of the code then the output should used to change icoFoam files and run "Run_simple_pinball.py"
import numpy as np
import random
from deap import creator, base, tools, algorithms
import os
import pandas as pd
import subprocess
import shutil
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import signal
import matplotlib as mpl

# Font settings
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.rcParams['font.family'] = 'Arial'

sim_dir = '/home/meltend/OpenFOAM/meltend-v2312/run/tutorials/incompressible/icoFoam/pimpleFOAM-fluidicpinball'
os.chdir(sim_dir)  
num_cores = 10 # Number of cores to use

# Some parameters for time control and other settings
time_limit = 18 * 60 * 60  # Max time: 18 hours
omega_tolerance = 1e-3
z_len = 0.02  # Simplified z-domain length
start_time = 0.0
end_time = 20.0
time_step = 0.5

start_clock = time.time() #Start the clock
stop_optimization = False

def handle_signal(sig, frame):
    global stop_optimization
    print("\nGot stop signal. Wrapping things up...")
    stop_optimization = True

signal.signal(signal.SIGINT, handle_signal)

def clean_up(): #Clear the old directories from previous runs
    for i in range(num_cores):
        core_dir = os.path.join(sim_dir, f'processor{i}')
        if os.path.exists(core_dir):
            shutil.rmtree(core_dir)

    post_dir = os.path.join(sim_dir, 'postProcessing')
    if os.path.exists(post_dir):
        shutil.rmtree(post_dir)

def update_omega(file_path, new_omegas): #Update the omega values in the file
    with open(file_path, 'r') as f:
        lines = f.readlines()

    cyl_names = ['cylinder_a', 'cylinder_b', 'cylinder_c']
    in_block = False
    current_cylinder = None

    for i, line in enumerate(lines):
        for cyl in cyl_names:
            if cyl in line:
                in_block = True
                current_cylinder = cyl_names.index(cyl)
                break

        if in_block and 'omega' in line:
            indent = len(line) - len(line.lstrip())
            lines[i] = ' ' * indent + f'omega           {new_omegas[current_cylinder]};\n'
            in_block = False

    with open(file_path, 'w') as f:
        f.writelines(lines)

    print(f"Omega values updated in {file_path}: {new_omegas}")

#Read the forces data from a file
def load_forces(file_path):
    df = pd.read_csv(file_path, sep='\s+', comment='#', header=None)
    df.columns = ['Time', 'total_x', 'total_y', 'total_z', 'pressure_x', 'pressure_y', 'pressure_z', 'viscous_x', 'viscous_y', 'viscous_z']
    return df

def load_torque(file_path): #Read torque data from a file
    df = pd.read_csv(file_path, sep='\s+', comment='#', header=None)
    df.columns = ['Time', 'total_x', 'total_y', 'total_z', 'pressure_x', 'pressure_y', 'pressure_z', 'viscous_x', 'viscous_y', 'viscous_z']
    return df

#Calculate the power for actuation based on what torque is
def avg_actuation_power(torque_df, omega):
    torque_z = torque_df['total_z'].values[int(0.3 * len(torque_df)):]
    avg_torque = torque_z.mean()
    return abs(avg_torque * omega)

# Get thee average drag power
def avg_drag_power(df_a, df_b, df_c, velocity):
    avg_drag = df_a['total_x'].iloc[int(0.5 * len(df_a)):].mean() + \
               df_b['total_x'].iloc[int(0.5 * len(df_b)):].mean() + \
               df_c['total_x'].iloc[int(0.5 * len(df_c)):].mean()
    return abs(avg_drag * velocity)

def update_times(start, end):
    control_file = os.path.join(sim_dir, 'system', 'controlDict')
    with open(control_file, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if 'startTime' in line:
            lines[i] = f'startTime {start};\n'
        if 'endTime' in line:
            lines[i] = f'endTime {end};\n'

    with open(control_file, 'w') as f:
        f.writelines(lines)
    print(f"Simulation time updated: start={start}, end={end}")

def get_latest_time():
    times = [float(d) for d in os.listdir(sim_dir) if d.replace('.', '', 1).isdigit()]
    return max(times) if times else start_time

def objective(omega_vals, gen):
    global stop_optimization
    clean_up()

    if time.time() - start_clock > time_limit:
        print("Time limit reached. Stopping...")
        stop_optimization = True
        return 0

    # Update omega values in the file
    U_file = os.path.join(sim_dir, '0', 'U')
    update_omega(U_file, omega_vals)

    latest_time = get_latest_time()
    start = latest_time if latest_time != start_time else start_time
    end = start + time_step
    update_times(start, end)

    # Run Openfoam sim
    subprocess.run(['blockMesh'])
    subprocess.run(['decomposePar'])
    subprocess.run(['mpirun', '-np', str(num_cores), 'icoFoam', '-parallel'])
    subprocess.run(['reconstructPar'])

    #Get the results
    start_str = f'{round(start)}'
    df_a = load_forces(os.path.join(sim_dir, 'postProcessing', 'forces_cylinder_a', start_str, 'force.dat'))
    df_b = load_forces(os.path.join(sim_dir, 'postProcessing', 'forces_cylinder_b', start_str, 'force.dat'))
    df_c = load_forces(os.path.join(sim_dir, 'postProcessing', 'forces_cylinder_c', start_str, 'force.dat'))

    #Calc drag power
    velocity = 1.0
    drag_power = avg_drag_power(df_a, df_b, df_c, velocity)

    #Get torque and actuation power
    torque_a = load_torque(os.path.join(sim_dir, 'postProcessing', 'forces_cylinder_a', start_str, 'moment.dat'))
    torque_b = load_torque(os.path.join(sim_dir, 'postProcessing', 'forces_cylinder_b', start_str, 'moment.dat'))
    torque_c = load_torque(os.path.join(sim_dir, 'postProcessing', 'forces_cylinder_c', start_str, 'moment.dat'))

    actuation_power = avg_actuation_power(torque_a, omega_vals[0]) + \
                      avg_actuation_power(torque_b, omega_vals[1]) + \
                      avg_actuation_power(torque_c, omega_vals[2])

    total_power = (drag_power + actuation_power) / z_len
    return (total_power,)

# DEAP setup
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, -2, 2)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=3)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

#Mutation and mating functions
def mutate(ind, prob):
    for i in range(len(ind)):
        if random.random() < prob:
            ind[i] += random.gauss(0, 1)
            ind[i] = np.clip(ind[i], -2, 2)
    return ind,

def mate(ind1, ind2, alpha=0.5):
    for i in range(len(ind1)):
        if random.random() < 0.5:
            temp = ind1[i]
            ind1[i] = alpha * ind1[i] + (1 - alpha) * ind2[i]
            ind2[i] = alpha * ind2[i] + (1 - alpha) * temp
        ind1[i] = np.clip(ind1[i], -2, 2)
        ind2[i] = np.clip(ind2[i], -2, 2)
    return ind1, ind2

#Register evaluation, crossover, mutation, and selection
toolbox.register("evaluate", objective, gen=0)
toolbox.register("mate", mate)
toolbox.register("mutate", mutate, prob=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

#Run genetic algorithm
def run_ga():
    pop = toolbox.population(n=50)
    hof = tools.HallOfFame(1)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)

    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=30, stats=stats, halloffame=hof, verbose=True)
    return pop, log, hof

# Main function
if __name__ == "__main__":
    pop, log, hof = run_ga()

    print("Best solution:", hof[0])
    print("Best fitness:", hof[0].fitness.values)
