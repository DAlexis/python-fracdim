import numpy as np
import math

def rowToPoints(row, dimension):
    rowLen = len(row)
    pointsCount = rowLen-dimension+1
    if pointsCount < 1:
        return 0

    a = np.ndarray(shape=(pointsCount, dimension))

    for i in range(0, pointsCount):
        for j in range(0, dimension):
            a[i,j] = row[i+j]
    return a

def getPointOnLine(lineBegin, lineEnd, axis, axisValue, targetPoint):
    """
    Get point on line by one given coordinate
    :param lineBegin: first fixed point on line
    :param lineEnd: second fixed point
    :param axis: known coordinate axis index
    :param axisValue: known coordinate
    :param targetPoint: function output
    :return:
    """
    dim = lineBegin.shape[0]
    targetPoint[axis] = axisValue
    progress = (axisValue - lineBegin[axis]) / (lineEnd[axis] - lineBegin[axis])
    for i in range(0, dim):
        if i == axis:
            continue
        targetPoint[i] = (1-progress) * lineBegin[i] + progress * lineEnd[i]

class MultiCell:
    """
        Rectangular cell in multi-dimensional space
    """
    def __init__(self, dim, p1=None, p2=None):
        self.userFlag = False
        self.__dim = 1
        self.__minCorner = None
        self.__maxCorner = None

        if p1 is not None and p1.shape != (dim,):
           raise Exception("Invalid pmin shape")

        if p1 is not None and p2.shape != (dim,):
           raise Exception("Invalid pmax shape")

        self.__dim = dim
        self.__minCorner = np.ndarray(shape=(dim))
        self.__maxCorner = np.ndarray(shape=(dim))

        if (p1 is not None) and (p2 is not None):
            for i in range(0, dim):
                if p1[i] > p2[i]:
                    self.__maxCorner[i] = p1[i]
                    self.__minCorner[i] = p2[i]
                else:
                    self.__maxCorner[i] = p2[i]
                    self.__minCorner[i] = p1[i]
        else:
            if p1 is not None:
                self.__minCorner = p1

            if p2 is not None:
                self.__maxCorner = p2

    def set(self, pmin=None, pmax=None):
        if pmin is not None:
            self.__minCorner = pmin

        if pmax is not None:
            self.__maxCorner = pmax

    def getMin(self):
        return self.__minCorner

    def getMax(self):
        return self.__maxCorner

    def checkPoint(self, p):
        lenP = len(p)
        if lenP > len(self.__minCorner):
            raise Exception("Invalid point dimension")

        for i in range(0, lenP):
            if p[i] < self.__minCorner[i] or p[i] > self.__maxCorner[i]:
                return False

        return True

    def dim(self):
        return self.__dim


class MultiGrid:
    __globalCell = None
    __cells = None
    __cellsPerAxis = 0

    def getCell(self, indices):
        index = 0
        for i in reversed(indices):
            index = index * self.__cellsPerAxis + i
        return self.__cells[index]

    def build(self, globalCell, cellsCountPerAxis):
        self.__globalCell = globalCell
        self.__cellsPerAxis = cellsCountPerAxis
        __cells = []

    def __recursiveAddCells(self, currentDim, offset):
        for i in range(0, self.__cellsPerAxis):
            pass #todo implement from here when this class is needed


class BlocksCounter(object):
    """This class calculates count of blocks that concrete dataset included to."""

    def __markVisited(self, indices):
        index = 0
        for i in reversed(indices):
            index = index * self.__cellsPerAxis + i
        self.__cellHasPoint[index] = 1

    def __getPointIndexes(self, point, indices):
        for i in range(0, self.__globalCell.dim()):
            tmp = (point[i] - self.__globalCell.getMin()[i]) / (self.__globalCell.getMax()[i] - self.__globalCell.getMin()[i])
            index = int(tmp * (self.__cellsPerAxis))
            # For right boundary values than formally does not imcluded to system
            # because cells are alike [0, 1), [1, 2), ... , [9, 10) <-- this border
            # should not be open
            if index == self.__cellsPerAxis:
                index = self.__cellsPerAxis-1

            indices[i] = index

    def __indexToLowerBoundaryCoordinate(self, axis, index):
        return self.__globalCell.getMin()[axis] + \
               (self.__globalCell.getMax()[axis] - self.__globalCell.getMin()[axis]) * \
               (index / self.__cellsPerAxis)

    def __getCellSize(self, axis):
        return (self.__globalCell.getMax()[axis] - self.__globalCell.getMin()[axis]) / self.__cellsPerAxis

    def __init__(self, globalCell=None, cellsPerAxis=1, mode="points"):
        """
        Constructor that configure BlocksCounter
        :param globalCell: MultiCell object describes area of blocks counting
        :param cellsPerAxis: Axis division method
        :param mode: "points" means than only points inclusions will be accounted,
                     "lines" means than lines connecting points will be accounted too. NOT IMPLEMENTED
        :return: constructed object
        """
        if mode != "points" and mode != "lines":
            raise Exception("Invalid mode for BlocksCounter")

        self.__globalCell = None
        self.__offsets = []
        self.__cellsPerAxis = 0
        self.__cellHasPoint = None
        self.__mode = mode
        self.__dim = 0

        if globalCell is not None:
            self.setSize(globalCell)
            self.setCellsPerAxis(cellsPerAxis)

    def setSize(self, cell):
        self.__globalCell = cell
        self.__dim = cell.dim()

    def setCellsPerAxis(self, cellsPerAxis):
        self.__cellsPerAxis = cellsPerAxis
        self.__offsets.append(1)
        for i in range(0, self.__globalCell.dim()-1):
            self.__offsets.append(self.__offsets[i]*cellsPerAxis)

        self.__cellHasPoint = np.ndarray(self.__offsets[-1]*self.__cellsPerAxis)
        self.__cellHasPoint[:] = 0

    def calculate(self, points):
        if self.__mode == "points":
            return self.__calculatePoints(points)
        else:
            return self.__calculateLines(points)

    def __calculateLines(self, points):
        self.__cellHasPoint[:] = 0
        if points.shape[0] == 1:
            return 1

        beginIndexes = np.ndarray(self.__globalCell.dim(), dtype=int)
        endIndexes = np.ndarray(self.__globalCell.dim(), dtype=int)
        indexes = np.ndarray(self.__globalCell.dim(), dtype=int)

        middlePoint = np.ndarray(self.__globalCell.dim())

        self.__getPointIndexes(points[0, :], beginIndexes)
        for pointIndex in range(1, points.shape[0]):
            self.__getPointIndexes(points[pointIndex, :], endIndexes)
            self.__markVisited(endIndexes)
            self.__markVisited(beginIndexes)
            # Iterating by all dimensions to find all crossings of line with grid
            for d in range(0, self.__dim):
                # Now iterating by cells crossing along this dimension
                begin = min(beginIndexes[d], endIndexes[d]) + 1
                end = max(beginIndexes[d], endIndexes[d])

                for i in range(begin, end+1):
                    # We have crossing with i's cell lowest border on axis d
                    getPointOnLine(lineBegin=points[pointIndex-1, :],
                                   lineEnd=points[pointIndex, :],
                                   axis=d,
                                   axisValue=self.__indexToLowerBoundaryCoordinate(axis=d, index=i),
                                   targetPoint=middlePoint)
                    # a little move of border point inside cell
                    middlePoint[d] -= self.__getCellSize(d) * 0.1;
                    self.__getPointIndexes(middlePoint, indexes)
                    self.__markVisited(indexes)

            beginIndexes = endIndexes.copy()

        result = 0
        for m in self.__cellHasPoint:
            if m != 0:
                result += 1

        return result


    def __calculatePoints(self, points):
        self.__cellHasPoint[:] = 0

        indexes = np.ndarray(self.__globalCell.dim(), dtype=int)
        for i in range(0, points.shape[0]):
            self.__getPointIndexes(points[i, :], indexes)
            self.__markVisited(indexes)

        result = 0

        for m in self.__cellHasPoint:
            if m != 0:
                result += 1

        return result
