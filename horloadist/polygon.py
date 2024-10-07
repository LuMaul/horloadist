import numpy as np

class Polygon:
    def __init__(self, glob_xy:list[float,float]):
        self._xy = glob_xy

    @property
    def _xy_closed_polygon(self) -> np.ndarray:
        return np.vstack((self._xy, self._xy[0]))
    
    @property
    def _triangle_areas(self) -> np.ndarray:
        xy = self._xy_closed_polygon
        return np.cross(xy[:-1], xy[1:]) / 2
    
    @property
    def area(self) -> np.float64:
        return abs(np.sum(self._triangle_areas))
    
    @property
    def _triangle_centroids(self) -> np.ndarray:
        xy = self._xy_closed_polygon
        return (xy[:-1] + xy[1:]) / 3

    @property
    def centroid(self) -> np.ndarray:
        tri_areas = self._triangle_areas
        tri_centr = self._triangle_centroids
        statical_moments = np.sum(tri_areas[:, np.newaxis] * tri_centr, axis=0)
        centroid = statical_moments / self.area
        return centroid