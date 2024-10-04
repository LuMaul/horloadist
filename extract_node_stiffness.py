from scipy.interpolate import interp1d
import pandas as pd
import numpy as np
import os


NODE_FILES = {
    7:pd.read_csv(os.path.join('stiffness_data','7 mchi csa N-41.4 kN.csv')),
    8:pd.read_csv(os.path.join('stiffness_data','8 mchi csa N-30.3 kN.csv')),
    9:pd.read_csv(os.path.join('stiffness_data','9 mchi csa N-92.1 kN.csv')),
    10:pd.read_csv(os.path.join('stiffness_data','10 mchi csa N-49.9 kN.csv')),
    11:pd.read_csv(os.path.join('stiffness_data','11 mchi csa N-96.9 kN.csv')),
}

def extractNodeStiffness(NodeNr:int, Momentum:float) -> float:

    df = NODE_FILES[NodeNr]

    x_val = df['mom']
    y_val = df['EI']

    interpolation_function = interp1d(x_val, y_val, kind='linear', fill_value="extrapolate")

    stiffness:np.ndarray = interpolation_function(Momentum)

    return float(stiffness)