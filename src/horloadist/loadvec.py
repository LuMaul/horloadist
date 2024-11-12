import numpy as np

from horloadist.polygon import Polygon, Polygons


def z_linspace(z_num_floors:int=5, floor_heigt:float=3.00) -> np.ndarray:
    z_heigt = z_num_floors * floor_heigt
    return np.linspace(start=0.00, stop=z_heigt, num=z_num_floors+1)


def uniform(z_space:np.ndarray, const_force:float=0.00) -> np.ndarray:
    v = np.full_like(z_space, const_force)
    v[0] = 0.0 # no load at z=0.0
    return v


def _weighted_norm(
        z_space:np.ndarray,
        g_force:float=1.00,
        q_force:float=0.00
        ) -> np.ndarray:
    
    tot_weight = (z_space * (g_force + q_force)).sum()
    return z_space * (g_force + q_force) / tot_weight


def _tot_hor_force(z_space:np.ndarray, S:float, g_force:float, q_force:float) -> float:
    return S * len(z_space-1) * (g_force + q_force)


def weighted_norm_g_by_polygon(
        z_space:np.ndarray,
        S:float,
        polygon:Polygon|Polygons,
        thickness:float,
        density:float,
        q_force:float=0
        ) -> np.ndarray:
    
    g_force = polygon.mass(thickness=thickness, density=density)
    h_force = _tot_hor_force(z_space=z_space, S=S, g_force=g_force, q_force=q_force)

    return _weighted_norm(z_space=z_space, g_force=g_force, q_force=q_force) * h_force