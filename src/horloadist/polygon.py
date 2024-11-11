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
    Represents a collection of positive and negative polygons, which together 
    define a composite shape with an overall centroid.

    Attributes
    ----------
    _pos_polygon : Polygon
        The primary positive polygon.
    _neg_polygons : list[Polygon]
        A list of negative polygons that represent areas to subtract from 
        the positive polygon, e.g., holes or recesses.

    Methods
    -------
    __init__(pos_polygon: Polygon, neg_polygons: list[Polygon] = [])
        Initializes the Polygons object with a primary positive polygon and 
        optional negative polygons.

    centroid() -> tuple[float, float]
        Calculates the overall centroid of the composite shape, taking into 
        account both positive and negative polygons.

    _stat_moment(polygon: Polygon) -> np.ndarray
        Calculates the statistical moment (area * centroid) for a single 
        polygon. Positive polygons add to the moment, while negative polygons 
        subtract from it.

    Examples
    --------
    >>> pos_polygon = Polygon([[0, 0], [1, 0], [1, 1], [0, 1]])
    >>> neg_polygons = [Polygon([[0.5, 0.5], [0.75, 0.5], [0.75, 0.75], [0.5, 0.75]])]
    >>> polygons = Polygons(pos_polygon, neg_polygons)
    >>> print(polygons.centroid)
    (0.5, 0.5)
    """
    def __init__(
            self,
            pos_polygon:Polygon,
            neg_polygons:list[Polygon]=[]
            ):

        self._pos_polygon = pos_polygon
        self._neg_polygons = neg_polygons

    @property
    def area(self) -> float:
        tot_poly_area = 0.00
        tot_poly_area += self._pos_polygon.area
        for neg_polygon in self._neg_polygons:
            tot_poly_area -= neg_polygon.area
        return float(tot_poly_area)


    @property
    def centroid(self) -> tuple[float, float]:
        """
        Computes the centroid of the composite shape formed by the positive 
        polygon and the negative polygons. The centroid is calculated based on 
        the statical moments of all polygons.

        Returns
        -------
        tuple[float, float]
            The (x, y) coordinates of the composite centroid.
        """
        tot_stat_moment = np.array([0.00, 0.00])
        tot_poly_area = 0.00

        tot_stat_moment += self._stat_moment(self._pos_polygon)
        tot_poly_area += self._pos_polygon.area
        
        for neg_polygon in self._neg_polygons:
            tot_stat_moment -= self._stat_moment(neg_polygon)
            tot_poly_area -= neg_polygon.area

        x, y = 1/tot_poly_area * tot_stat_moment

        return x, y
    
    def _stat_moment(self, polygon:Polygon) -> np.ndarray:
        return polygon.area * np.array(polygon.centroid)