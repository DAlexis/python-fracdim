import numpy as np
import math

class KochSnowflake:
    def __init__(self):
        self.__points = None
        self.__depth = 0
        self.__pointsCount = 0
        self.__currentPointsCount = 0

    def __appendPoint(self, point):
        self.__points[self.__currentPointsCount, :] = point
        self.__currentPointsCount += 1

    def construct(self, depth):
        self.__currentPointsCount = 0
        self.__pointsCount = 3 * 4**(depth-1) + 1
        self.__points = np.ndarray(shape=(self.__pointsCount, 2))
        self.__depth = depth
        p1 = np.asarray([0, 0])
        p2 = np.asarray([1, 0])
        p3 = np.asarray([0.5, math.sqrt(3) / 2])
        self.__appendPoint(p1)
        self.__recursiveAddLine(1, p1, p2)
        self.__appendPoint(p2)
        self.__recursiveAddLine(1, p2, p3)
        self.__appendPoint(p3)
        self.__recursiveAddLine(1, p3, p1)
        self.__appendPoint(p1)
        return self.__points

    def __recursiveAddLine(self, currentDepth, p1, p2):
        if currentDepth == self.__depth:
            return

        pl = p1 * 2.0/3.0 + p2 * 1.0/3.0
        pr = p1 * 1.0/3.0 + p2 * 2.0/3.0
        pc = p1 * 0.5 + p2 * 0.5

        vs = (p2-p1) / 3
        vslen = math.sqrt(vs[0]*vs[0] + vs[1]*vs[1])
        v = np.ndarray(shape=[2])
        v[0] = vs[1] * math.sqrt(3) / 2
        v[1] = -vs[0] * math.sqrt(3) / 2
        pc += v
        self.__recursiveAddLine(currentDepth+1, p1, pl)
        self.__appendPoint(pl)
        self.__recursiveAddLine(currentDepth+1, pl, pc)
        self.__appendPoint(pc)
        self.__recursiveAddLine(currentDepth+1, pc, pr)
        self.__appendPoint(pr)
        self.__recursiveAddLine(currentDepth+1, pr, p2)


