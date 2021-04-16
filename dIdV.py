import pandas as pd


import matplotlib.pyplot as plt
import numpy as np
from matplotlib import  cm

#User Parameters

file = "015_NTJJ01_dVdImap(Bz)_I109_V34_ac10nA(27.7777Hz)_nodc_acpre500_0.18T_-0.18T_st2mT.dat"
mag_noise = 0.0002 # Noise in magnetic field
number_of_plots = 10
b_precision_legend = 3

resistance = 10

current_min = -0.025
current_max = 0.025

dI_dV_min = 0
dI_dV_max = 3000

fig_a_name = "fig A.png"
fig_a_xlabel = "Magnetic Field (mT)"
fig_a_ylabel = r"I ($\mu$A)"

fig_b_name = "fig B.png"
fig_b_xlabel = "Current (mA)"
fig_b_ylabel = r"dV/dI ($\Omega$)"

# Excluding all the lines where header exist
exclude = [i for i, line in enumerate(open(file)) if line.startswith('M')] 

data = pd.read_csv(file, sep="\t", skiprows= exclude[1:])

data["Source Voltage (V)"] = data["Source Voltage (V)"]/resistance
data = data[(data["Source Voltage (V)"] < current_max) & (data["Source Voltage (V)"] > current_min)]

data = data[(data["Differential Resistance dV/dI (ohm)"] < dI_dV_max) & (data["Differential Resistance dV/dI (ohm)"] > dI_dV_min)]

def get_next_data_frame(dataframe, start, noise, axis=0 ):
    return dataframe[(dataframe[axis] < dataframe[axis][start] + noise) & (dataframe[axis] > dataframe[axis][start] - noise)]

def get_dataframes_by_column(data, noise, axis):
    dataframes = []
    size = 0
    while(True):
        df = get_next_data_frame(data, size, noise, axis)
        dataframes.append(df)
        size += df[axis].size
        if (size >= data[axis].size or (data[axis][size] < data[axis].values[-1] + noise) and (data[axis][size] > data[axis].values[-1] - noise)):
            return dataframes

#Saving Files
dataframes = get_dataframes_by_column(data, mag_noise, "Magnetic Field (T)")

for i, df in enumerate(dataframes):
    df.to_csv(f"{file}_{i}", sep="\t")

fig, ax = plt.subplots()

divisor = len(dataframes) // number_of_plots
b_array = []
di_dv_array = []
for i, df in enumerate(dataframes):
    B = df["Magnetic Field (T)"].values[0]
    b_array.append(B)

    if ( i == len(dataframes) - 1):
        i_array = data["Source Voltage (V)"]
    di_dv_array.append(data["Differential Resistance dV/dI (ohm)"])
    
    if (i% divisor == 0):
        ax.plot(df["Source Voltage (V)"], df["Differential Resistance dV/dI (ohm)"], label = f"B = {B:.{b_precision_legend}f}")
ax.set_xlabel(fig_b_xlabel)
ax.set_ylabel(fig_b_ylabel)

legend = ax.legend(loc='center right', bbox_to_anchor=(1.3, 0.5) )
fig.savefig(fig_b_name, dpi = 300, bbox_extra_artists=(legend,),
            bbox_inches='tight')
fig.show()

fig, ax = plt.subplots()
cs = ax.contourf(b_array, i_array, np.transpose(di_dv_array), cmap=cm.PuBu_r)
cbar = fig.colorbar(cs)
ax.set_xlabel(fig_a_xlabel)
ax.set_ylabel(fig_a_ylabel)
fig.tight_layout()
fig.savefig(fig_a_name, dpi = 300)


plt.show()