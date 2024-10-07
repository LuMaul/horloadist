

class SupportNode:
    def __init__(self, nr:int, glob_x:float, glob_y:float, glob_EIy:float, glob_EIx:float):
        self._nr = nr
        self._glob_x = glob_x
        self._glob_y = glob_y
        self._glob_EIy = glob_EIy
        self._glob_EIx = glob_EIx

        self._Rx = None
        self._Ry = None