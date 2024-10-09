from scipy.interpolate import interp1d
import pandas as pd
import numpy as np


def interpolateXY(df:pd.DataFrame, Momentum:float|int) -> float:
    
    x_val = df['mom']
    y_val = df['EI']

    interpolation_function = interp1d(x_val, y_val, kind='linear', fill_value="extrapolate")

    stiffness:np.ndarray = interpolation_function(Momentum)

    return float(stiffness)