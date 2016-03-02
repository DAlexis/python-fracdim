import numpy as np

class KochSnowflake:
    def __init__(self):
        self.points = None
        self.pointsCount = 0

    def construct(self, depth):
        self.pointsCount = 3 * 4**(depth-1)
        self.points = np.ndarray(shape=(self.pointsCount, 2))
        self.depth = depth
        return self.points

    def __recursiveAddLine(self, currentDepth, p1, p2):
        pass