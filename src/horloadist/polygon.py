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
    

class Polygons:
    """
    Represents a collection of positive and negative polygons.

    Attributes
    ----------
    _pos_polygons : list[Polygon]
        List of positive polygons.
    _neg_polygons : list[Polygon]
        List of negative polygons. E.g. a shell recess.

    Methods
    -------
    centroid() -> tuple[float, float]
        Calculates the overall centroid of the positive and negative polygons.

    _stat_moment(polygon: Polygon) -> np.ndarray
        Calculates the statistical moment (area * centroid) for a single polygon.

    Examples
    --------
    >>> pos_polygons = [Polygon([[0, 0], [1, 0], [1, 1], [0, 1]]),
                    Polygon([[2, 0], [3, 0], [3, 2], [2, 2]])]
    >>> neg_polygons = [Polygon([[1, 1], [2, 1], [2, 2], [1, 2]])]
    >>> polygons = Polygons(pos_polygons, neg_polygons)
    >>> print(polygons.centroid)
    (1.0, 1.0)
    """
    def __init__(
            self,
            pos_polygons:list[Polygon],
            neg_polygons:list[Polygon]=[]
            ):

        self._pos_polygons = pos_polygons
        self._neg_polygons = neg_polygons


    @property
    def centroid(self) -> tuple[float, float]:

        tot_stat_moment = np.array([0.00, 0.00])
        tot_poly_area = 0.00
        for pos_polygon in self._pos_polygons:
            tot_stat_moment += self._stat_moment(pos_polygon)
            tot_poly_area += pos_polygon.area
        
        for neg_polygon in self._neg_polygons:
            tot_stat_moment -= self._stat_moment(neg_polygon)
            tot_poly_area -= neg_polygon.area

        x, y = 1/tot_poly_area * tot_stat_moment

        return x, y
    
    def _stat_moment(self, polygon:Polygon) -> np.ndarray:
        return polygon.area * np.array(polygon.centroid)