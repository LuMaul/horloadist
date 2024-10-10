import numpy as np


class Polygon:
    """
    A class to represent a polygon and compute its geometric properties such as
    area and centroid.

    Parameters
    ----------
    glob_xy : list of tuple of float
        A list of 2D points (x, y coordinates) that define the vertices of
        the polygon.
    
    Attributes
    ----------
    _xy : list of tuple of float
        List of x and y coordinates representing the vertices of the polygon.
    _xy_closed_polygon : np.ndarray
        A closed polygon by appending the first point to the end.
    _triangle_areas : np.ndarray
        Areas of the triangles formed between consecutive polygon vertices.
    _triangle_centroids : np.ndarray
        Centroids of the triangles formed between consecutive polygon vertices.
    area : np.float64
        The total area of the polygon.
    centroid : np.ndarray
        The centroid (geometric center) of the polygon.
    """
    def __init__(self, glob_xy:list[list[float|int]]):
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