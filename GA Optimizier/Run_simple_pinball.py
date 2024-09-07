# This code just runs some basic simulations and plots drag and Cp for either normal or optimal conditions.
import os
import pandas as pd
import numpy as np
import subprocess
import shutil
import matplotlib.pyplot as plt

z_length = 0.02  # Shortened variable name for simplicity

# Function to load the forces data from a file
def load_forces(file_path):
    df = pd.read_csv(file_path, delim_whitespace=True, comment='#', header=None)
    df.columns = ['Time', 'force_x', 'force_y', 'force_z', 'pressure_x', 'pressure_y', 'pressure_z', 'viscous_x', 'viscous_y', 'viscous_z']
    return df

cylinder_file_path = '/home/meltend/OpenFOAM/meltend-v2312/run/tutorials/incompressible/icoFoam/Simple-fluidicpinball'
os.chdir(cylinder_file_path)  # Move to the working directory
num_cores = 10

# Clean up old directories from previous runs
def clean_old_runs():
    post_proc_dir = os.path.join(cylinder_file_path, 'postProcessing')
    if os.path.exists(post_proc_dir):
        shutil.rmtree(post_proc_dir)

    for i in range(num_cores):
        core_dir = os.path.join(cylinder_file_path, f'processor{i}')
        if os.path.exists(core_dir):
            shutil.rmtree(core_dir)
def get_force_file_paths():
    post_processing_dir = os.path.join(cylinder_file_path, 'postProcessing')
    cylinder_a_file_path = os.path.join(post_processing_dir, 'forces_cylinder_a', '0', 'force.dat')
    cylinder_b_file_path = os.path.join(post_processing_dir, 'forces_cylinder_b', '0', 'force.dat')
    cylinder_c_file_path = os.path.join(post_processing_dir, 'forces_cylinder_c', '0', 'force.dat')
    return cylinder_a_file_path, cylinder_b_file_path, cylinder_c_file_path

def get_moment_file_paths():
    post_processing_dir = os.path.join(cylinder_file_path, 'postProcessing')
    cylinder_a_file_path = os.path.join(cylinder_file_path, 'postProcessing', 'forces_cylinder_a', '0', 'moment.dat')
    cylinder_b_file_path = os.path.join(cylinder_file_path, 'postProcessing', 'forces_cylinder_b', '0', 'moment.dat')
    cylinder_c_file_path = os.path.join(cylinder_file_path, 'postProcessing', 'forces_cylinder_c', '0', 'moment.dat')
    return cylinder_a_file_path,cylinder_b_file_path,cylinder_c_file_path
#
# Function to run the simulation
def run_sim():
    subprocess.run(['blockMesh'])
    subprocess.run(['snappyHexMesh', '-overwrite'])
    subprocess.run(['decomposePar'])
    subprocess.run(['mpirun', '-np', str(num_cores), 'icoFoam', '-parallel'])
    subprocess.run(['reconstructPar'])

# Read pressure values from a file
def load_pressure_data(file_path):
    pressure_vals = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.strip().isdigit():
            num_points = int(line.strip())
            break

    for j in range(i + 2, i + 2 + num_points):
        pressure_vals.append(float(lines[j].strip()))

    return np.array(pressure_vals)

# Calculate pressure coefficient
def calc_cp(pressure, p_ref, density, velocity):
    return (pressure - p_ref) / (0.5 * density * velocity**2)

# Plot pressure coefficient over time
def plot_cp_vs_time(cp_vals, times):
    plt.figure()
    plt.plot(times, cp_vals, marker='o', linestyle='-', color='b', label='Cp vs Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Cp')
    plt.title('Cp Over Time')
    plt.legend()
    plt.show()

# Extract Cp values for different time steps
def get_cp_from_times(project_dir, density, velocity, p_ref):
    time_dirs = sorted([d for d in os.listdir(project_dir) if os.path.isdir(os.path.join(project_dir, d)) and d.replace('.', '', 1).isdigit()], key=float)
    
    cp_vals = []
    time_vals = []

    for time_dir in time_dirs:
        pressure_file = os.path.join(project_dir, time_dir, 'p')
        if os.path.exists(pressure_file):
            pressure_data = load_pressure_data(pressure_file)
            cp = calc_cp(pressure_data.mean(), p_ref, density, velocity)
            cp_vals.append(cp)
            time_vals.append(float(time_dir))

    if cp_vals and time_vals:
        pd.DataFrame({'Time': time_vals, 'Cp': cp_vals}).to_csv('cp_vs_time.csv', index=False)
        plot_cp_vs_time(cp_vals, time_vals)

# Calculate average drag
def avg_drag(df_a, df_b, df_c):
    skip_percent = 0.6
    skip_idx = int(skip_percent * len(df_a))

    drag_a = df_a['force_x'].iloc[skip_idx:].mean()
    drag_b = df_b['force_x'].iloc[skip_idx:].mean()
    drag_c = df_c['force_x'].iloc[skip_idx:].mean()

    return (drag_a + drag_b + drag_c) / z_length

# Load torque data from file
def load_torque(file_path):
    df = pd.read_csv(file_path, delim_whitespace=True, comment='#', header=None)
    df.columns = ['Time', 'torque_x', 'torque_y', 'torque_z']
    return df

# Calculate average power from torque
def avg_power_from_torque(torque_df, omega):
    torque_z = torque_df['torque_z'].values[int(0.05 * len(torque_df)):]
    avg_torque = torque_z.mean()
    return abs((avg_torque * omega) / z_length)

# Plot drag over time
def plot_drag(df_a, df_b, df_c, avg_drag, actuation_power):
    total_drag = (df_a['force_x'].iloc[3:] + df_b['force_x'].iloc[3:] + df_c['force_x'].iloc[3:]) / z_length
    time_vals = df_a['Time'].iloc[3:]

    plt.figure()
    plt.plot(time_vals, total_drag, label='Total Drag')
    plt.axhline(y=avg_drag, color='r', linestyle='--', label='Avg Drag')
    plt.axhline(y=actuation_power, color='b', linestyle=':', label='Actuation Power')
    plt.xlabel('Time')
    plt.ylabel('Drag')
    plt.title('Drag Over Time')
    plt.legend()
    plt.show()

# Main workflow
clean_old_runs()
run_sim()

file_a, file_b, file_c = get_force_file_paths()
df_a = load_forces(file_a)
df_b = load_forces(file_b)
df_c = load_forces(file_c)

torque_a, torque_b, torque_c = get_moment_file_paths()
torque_df_a = load_torque(torque_a)
torque_df_b = load_torque(torque_b)
torque_df_c = load_torque(torque_c)

# Unforced case
omega_a, omega_b, omega_c = 0, 0, 0

avg_power_a = avg_power_from_torque(torque_df_a, omega_a)
avg_power_b = avg_power_from_torque(torque_df_b, omega_b)
avg_power_c = avg_power_from_torque(torque_df_c, omega_c)

total_actuation_power = avg_power_a + avg_power_b + avg_power_c

avg_drag_total = avg_drag(df_a, df_b, df_c)
net_drag = avg_drag_total + total_actuation_power

plot_drag(df_a, df_b, df_c, avg_drag_total, total_actuation_power)

# Extract and plot Cp
get_cp_from_times(cylinder_file_path, 1.0, 1.0, 0.0)
