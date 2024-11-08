class Load:
    """Initialize the object with x and y magnitudes.
    
    Parameters
    ----------
    x_magnitude : float, optional
        The magnitude in the x-direction. Default is 0.
    y_magnitude : float, optional
        The magnitude in the y-direction. Default is 0.
    """
    def __init__(
            self,
            x_magnitude:float=0.0,
            y_magnitude:float=0.0,
            ) -> None:
        
        self._x_magnitude = x_magnitude
        self._y_magnitude = y_magnitude